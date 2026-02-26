# Logseq: [[TTA.dev/Agent_orchestration/Workflow_monitor]]
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RunStep:
    name: str
    started_at: float
    ended_at: float | None = None
    error: str | None = None
    warned: bool = False


@dataclass
class RunRecord:
    run_id: str
    workflow: str | None = None
    status: str = "running"  # running|completed|failed|timed_out
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None
    steps: list[RunStep] = field(default_factory=list)
    total_timeout_s: float = 300.0
    step_timeout_s: float = 60.0


class WorkflowMonitor:
    """
    Tracks workflow execution state in Redis, performs timeout detection and resource
    early warnings, and maintains an audit trail for rollbacks.

    Redis keys (prefix pfx=ao by default):
      - {pfx}:wf:runs:{run_id} -> JSON record
      - {pfx}:wf:rollback:audit:{run_id} -> list of JSON entries (audit trail)
      - {pfx}:wf:metrics -> hash of counters
    """

    def __init__(
        self,
        redis,
        key_prefix: str = "ao",
        *,
        default_total_timeout_s: float = 300.0,
        default_step_timeout_s: float = 60.0,
        audit_retention_days: int = 30,
    ) -> None:
        self._redis = redis
        self._pfx = key_prefix.rstrip(":")
        self._def_total = float(default_total_timeout_s)
        self._def_step = float(default_step_timeout_s)
        self._audit_ttl_s = int(max(1, audit_retention_days) * 86400)
        self._bg_task: asyncio.Task | None = None

    # ---- Redis key helpers ----
    def _run_key(self, run_id: str) -> str:
        return f"{self._pfx}:wf:runs:{run_id}"

    def _audit_key(self, run_id: str) -> str:
        return f"{self._pfx}:wf:rollback:audit:{run_id}"

    def _metrics_key(self) -> str:
        return f"{self._pfx}:wf:metrics"

    # ---- Public API ----
    async def start_run(
        self,
        run_id: str,
        *,
        workflow: str | None = None,
        total_timeout_s: float | None = None,
        step_timeout_s: float | None = None,
    ) -> None:
        now = time.time()
        rr = RunRecord(
            run_id=run_id,
            workflow=workflow,
            started_at=now,
            total_timeout_s=float(total_timeout_s or self._def_total),
            step_timeout_s=float(step_timeout_s or self._def_step),
        )
        await self._redis.set(self._run_key(run_id), json.dumps(self._dump(rr)))

    async def start_step(self, run_id: str, step_name: str) -> None:
        rr = await self._load(run_id)
        if not rr:
            return
        rr.steps.append(RunStep(name=step_name, started_at=time.time()))
        await self._persist(rr)

    async def end_step(self, run_id: str, *, error: str | None = None) -> None:
        rr = await self._load(run_id)
        if not rr:
            return
        if rr.steps:
            rr.steps[-1].ended_at = time.time()
            rr.steps[-1].error = error
        if error:
            rr.status = "failed"
            rr.ended_at = time.time()
            await self._incr_metric("workflow_failures_total", 1)
        await self._persist(rr)

    async def complete_run(self, run_id: str) -> None:
        rr = await self._load(run_id)
        if not rr:
            return
        rr.status = "completed"
        rr.ended_at = time.time()
        await self._persist(rr)

    async def fail_run(self, run_id: str, reason: str) -> None:
        rr = await self._load(run_id)
        if not rr:
            return
        rr.status = "failed"
        rr.ended_at = time.time()
        if rr.steps and rr.steps[-1].ended_at is None:
            rr.steps[-1].error = reason
            rr.steps[-1].ended_at = rr.ended_at
        await self._persist(rr)
        await self._incr_metric("workflow_failures_total", 1)

    async def get_run(self, run_id: str) -> dict[str, Any] | None:
        rr = await self._load(run_id)
        return self._dump(rr) if rr else None

    async def record_rollback_audit(self, run_id: str, entry: dict[str, Any]) -> None:
        try:
            await self._redis.rpush(self._audit_key(run_id), json.dumps(entry))
            await self._redis.expire(self._audit_key(run_id), self._audit_ttl_s)
            await self._incr_metric("rollback_operations_total", 1)
        except Exception:
            logger.debug("Failed to record rollback audit", exc_info=True)

    async def get_rollback_history(self, run_id: str) -> list[dict[str, Any]]:
        try:
            raw = await self._redis.lrange(self._audit_key(run_id), 0, -1)
            out: list[dict[str, Any]] = []
            for b in raw or []:
                with contextlib.suppress(Exception):
                    out.append(json.loads(b if isinstance(b, str) else b.decode()))
            return out
        except Exception:
            return []

    # ---- Timeout detection ----
    async def check_timeouts_once(self) -> int:
        """Scan all runs and apply early warnings and timeouts.
        Returns number of runs transitioned to timed_out.
        """
        transitioned = 0
        try:
            async for key in self._redis.scan_iter(match=f"{self._pfx}:wf:runs:*"):
                k = key.decode() if isinstance(key, (bytes, bytearray)) else key
                data = await self._redis.get(k)
                if not data:
                    continue
                try:
                    rr = self._from_dump(
                        json.loads(data if isinstance(data, str) else data.decode())
                    )
                except Exception as e:
                    logger.debug(
                        f"Skipping workflow record {k}: failed to parse JSON - {type(e).__name__}: {e}"
                    )
                    continue
                if rr.status not in ("running",):
                    continue
                now = time.time()
                # Early warning for total timeout
                if (now - rr.started_at) >= 0.75 * rr.total_timeout_s:
                    await self._maybe_warn(rr, "total")
                # Step early warning and timeout
                if rr.steps:
                    s = rr.steps[-1]
                    if s.ended_at is None:
                        elapsed = now - s.started_at
                        if elapsed >= 0.75 * rr.step_timeout_s and not s.warned:
                            s.warned = True
                            await self._audit(
                                rr.run_id,
                                {
                                    "ts": now,
                                    "event": "early_warning",
                                    "type": "step",
                                    "name": s.name,
                                    "elapsed": elapsed,
                                },
                            )
                            await self._persist(rr)
                        if elapsed >= rr.step_timeout_s:
                            rr.status = "timed_out"
                            rr.ended_at = now
                            s.error = "step_timeout"
                            s.ended_at = now
                            transitioned += 1
                            await self._persist(rr)
                            await self._incr_metric("workflow_failures_total", 1)
                            continue
                # Total timeout
                if (now - rr.started_at) >= rr.total_timeout_s:
                    rr.status = "timed_out"
                    rr.ended_at = now
                    transitioned += 1
                    await self._persist(rr)
                    await self._incr_metric("workflow_failures_total", 1)
        except Exception:
            logger.debug("check_timeouts_once error", exc_info=True)
        return transitioned

    def start_background_checks(self, interval_s: float = 1.0) -> None:
        with contextlib.suppress(Exception):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._bg_task = loop.create_task(self._bg_loop(interval_s))  # type: ignore[attr-defined]

    def stop_background_checks(self) -> None:
        t = self._bg_task
        if t:
            with contextlib.suppress(Exception):
                t.cancel()
            self._bg_task = None

    # ---- Helpers ----
    async def _maybe_warn(self, rr: RunRecord, kind: str) -> None:
        with contextlib.suppress(Exception):
            await self._audit(
                rr.run_id, {"ts": time.time(), "event": "early_warning", "type": kind}
            )

    async def _audit(self, run_id: str, entry: dict[str, Any]) -> None:
        await self.record_rollback_audit(run_id, entry)

    async def _persist(self, rr: RunRecord) -> None:
        await self._redis.set(self._run_key(rr.run_id), json.dumps(self._dump(rr)))

    async def _load(self, run_id: str) -> RunRecord | None:
        raw = await self._redis.get(self._run_key(run_id))
        if not raw:
            return None
        try:
            return self._from_dump(
                json.loads(raw if isinstance(raw, str) else raw.decode())
            )
        except Exception:
            return None

    async def _incr_metric(self, name: str, inc: int) -> None:
        with contextlib.suppress(Exception):
            await self._redis.hincrby(self._metrics_key(), name, int(inc))

    async def metrics_snapshot(self) -> dict[str, int]:
        try:
            data = await self._redis.hgetall(self._metrics_key())
            out: dict[str, int] = {}
            for k, v in (data or {}).items():
                key = k if isinstance(k, str) else k.decode()
                try:
                    out[key] = int(v if isinstance(v, str) else v.decode())
                except Exception:
                    out[key] = 0
            return out
        except Exception:
            return {}

    # ---- serialization helpers ----
    def _dump(self, rr: RunRecord) -> dict[str, Any]:
        return {
            "run_id": rr.run_id,
            "workflow": rr.workflow,
            "status": rr.status,
            "started_at": rr.started_at,
            "ended_at": rr.ended_at,
            "total_timeout_s": rr.total_timeout_s,
            "step_timeout_s": rr.step_timeout_s,
            "steps": [
                {
                    "name": s.name,
                    "started_at": s.started_at,
                    "ended_at": s.ended_at,
                    "error": s.error,
                    "warned": s.warned,
                }
                for s in rr.steps
            ],
        }

    def _from_dump(self, d: dict[str, Any]) -> RunRecord:
        rr = RunRecord(
            run_id=d.get("run_id") or "",
            workflow=d.get("workflow"),
            status=d.get("status", "running"),
            started_at=float(d.get("started_at") or time.time()),
            ended_at=d.get("ended_at"),
            total_timeout_s=float(d.get("total_timeout_s") or self._def_total),
            step_timeout_s=float(d.get("step_timeout_s") or self._def_step),
        )
        for s in d.get("steps", []) or []:
            rr.steps.append(
                RunStep(
                    name=s.get("name"),
                    started_at=float(s.get("started_at") or time.time()),
                    ended_at=s.get("ended_at"),
                    error=s.get("error"),
                    warned=bool(s.get("warned", False)),
                )
            )
        return rr
