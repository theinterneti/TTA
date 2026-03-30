# Logseq: [[TTA.dev/Agent_orchestration/Router]]
from __future__ import annotations

import contextlib
import json
import time
from typing import Any

from .models import AgentId, AgentType


class AgentRouter:
    """Centralized agent router that selects healthy instances per AgentType.

    Enhanced selection policy:
    - Prefer running and non-degraded instances from AgentRegistry
    - Weighted scoring among candidates using:
      * queue length (30%, lower is better)
      * heartbeat age (40%, lower is better; recency threshold default 30s)
      * success rate (30%, higher is better)
    - Falls back gracefully if Redis/metrics are unavailable
    """

    def __init__(
        self,
        registry: Any,
        redis_client: Any | None = None,
        tool_policy: Any | None = None,
        *,
        heartbeat_fresh_s: float = 30.0,
        w_queue: float = 0.30,
        w_heartbeat: float = 0.40,
        w_success: float = 0.30,
    ) -> None:
        self._registry = registry
        self._redis = redis_client
        self._tool_policy = tool_policy
        self._hb_fresh = float(heartbeat_fresh_s)
        # Normalize weights sum to 1.0 defensively
        total = float(w_queue + w_heartbeat + w_success) or 1.0
        self._wq = float(w_queue) / total
        self._wh = float(w_heartbeat) / total
        self._ws = float(w_success) / total

    async def _measure_queue_length(self, agent) -> int:
        if not self._redis:
            return 0
        try:
            key = f"ao:queue:{agent.agent_id.type.value}:{agent.agent_id.instance or 'default'}"
            qlen = await self._redis.llen(key)
            return int(qlen or 0)
        except Exception:
            return 0

    async def _measure_heartbeat_age(self, agent) -> float:
        if not self._redis:
            return float("inf")
        try:
            key = f"ao:agents:{agent.agent_id.type.value}:{agent.agent_id.instance or 'default'}"
            val = await self._redis.get(key)
            if not val:
                return float("inf")
            data = json.loads(val if isinstance(val, str) else val.decode())
            last = float(data.get("last_heartbeat", 0.0))
            if last <= 0.0:
                return float("inf")
            return max(0.0, time.time() - last)
        except Exception:
            return float("inf")

    def _measure_success_rate(self, agent) -> float:
        try:
            # prefer sliding window if available
            if hasattr(agent._metrics, "window_success_rate"):
                sr = float(agent._metrics.window_success_rate())
                return max(0.0, min(1.0, sr))
            req = int(getattr(agent._metrics, "requests", 0))
            err = int(getattr(agent._metrics, "errors", 0))
            if req <= 0:
                return 1.0
            succ = max(0, req - err)
            return max(0.0, min(1.0, succ / float(req)))
        except Exception:
            return 1.0

    @staticmethod
    def _normalize(values: list[float]) -> list[float]:
        # Min-max normalize to [0,1]; if all equal, return zeros
        if not values:
            return []
        vmin = min(values)
        vmax = max(values)
        if vmax == vmin:
            return [0.0 for _ in values]
        return [(v - vmin) / (vmax - vmin) for v in values]

    async def _score_candidates(
        self, candidates: list[Any]
    ) -> tuple[list[dict[str, Any]], Any | None]:
        # Gather raw metrics
        queues: list[float] = []
        hb_ages: list[float] = []
        succs: list[float] = []
        raw: list[dict[str, Any]] = []
        for a in candidates:
            q = await self._measure_queue_length(a)
            h = await self._measure_heartbeat_age(a)
            s = self._measure_success_rate(a)
            queues.append(float(q))
            hb_ages.append(float(h))
            succs.append(float(s))
            raw.append(
                {
                    "agent": a,
                    "instance": a.agent_id.instance or "default",
                    "queue_length": int(q),
                    "heartbeat_age_s": float(h),
                    "success_rate": float(s),
                }
            )
        # Normalize: lower is better for q and h; higher is better for s
        nq = self._normalize(queues)
        nh = [
            min(1.0, (h / self._hb_fresh) if self._hb_fresh > 0 else 1.0)
            for h in hb_ages
        ]
        ns = succs  # already in [0,1]
        # Compute weighted score: lower is better (penalize low success)
        for i, entry in enumerate(raw):
            penalty_success = 1.0 - ns[i]
            score = (
                (self._wq * nq[i]) + (self._wh * nh[i]) + (self._ws * penalty_success)
            )
            entry["score"] = float(score)
        # Choose best (min score)
        best = None
        if raw:
            best = min(raw, key=lambda d: d.get("score", 1e9)).get("agent")
        return raw, best

    async def resolve_healthy_instance(
        self, agent_type: AgentType, exclude_degraded: bool = True
    ) -> AgentId | None:
        candidates = []
        try:
            for a in self._registry.all():
                with contextlib.suppress(Exception):
                    if (
                        a.agent_id.type == agent_type
                        and a._running
                        and (not exclude_degraded or not a._degraded)
                    ):
                        candidates.append(a)
        except Exception:
            return None
        if not candidates:
            return None
        scored, best_agent = await self._score_candidates(candidates)
        if best_agent is not None:
            return AgentId(
                type=best_agent.agent_id.type, instance=best_agent.agent_id.instance
            )
        # Fallback: first candidate
        a0 = candidates[0]
        return AgentId(type=a0.agent_id.type, instance=a0.agent_id.instance)

    async def resolve_target(
        self, recipient: AgentId, exclude_degraded: bool = True
    ) -> AgentId:
        """Return an AgentId with instance resolved to a healthy one when possible.
        Honors explicit instance when healthy; otherwise picks another healthy instance of the same type.
        """
        with contextlib.suppress(Exception):
            if recipient.instance:
                for a in self._registry.all():
                    if (
                        a.agent_id.type == recipient.type
                        and a.agent_id.instance == recipient.instance
                    ):
                        if a._running and (not exclude_degraded or not a._degraded):
                            return recipient
                        break
        resolved = await self.resolve_healthy_instance(
            recipient.type, exclude_degraded=exclude_degraded
        )
        return resolved or recipient

    async def preview(
        self,
        agent_type: AgentType,
        exclude_degraded: bool = True,
        show_all_candidates: bool = False,
    ) -> dict[str, Any]:
        """Compute routing preview with scores, metrics, and exclusions for transparency."""
        out: dict[str, Any] = {
            "agent_type": agent_type.value,
            "weights": {"queue": self._wq, "heartbeat": self._wh, "success": self._ws},
            "heartbeat_fresh_s": self._hb_fresh,
            # Explicitly include configured_* keys for ops-facing consumers
            "configured_weights": {
                "queue": self._wq,
                "heartbeat": self._wh,
                "success": self._ws,
            },
            "configured_heartbeat_fresh_seconds": self._hb_fresh,
            "candidates": [],
            "selected": None,
            "reason": "",
            "excluded": [],
            "summary": {
                "total_agents": 0,
                "healthy_candidates": 0,
                "excluded_count": 0,
                "exclusion_reasons": {},
            },
        }
        all_agents: list[Any] = []
        try:
            all_agents = list(self._registry.all())
        except Exception:
            all_agents = []
        out["summary"]["total_agents"] = len(all_agents)
        candidates: list[Any] = []
        # Build exclusions
        for a in all_agents:
            reason = None
            try:
                if a.agent_id.type != agent_type:
                    reason = "wrong_type"
                elif not a._running:
                    reason = "not_running"
                elif a._degraded and exclude_degraded:
                    reason = "degraded"
            except Exception:
                reason = "unhealthy"
            if reason:
                out["excluded"].append(
                    {
                        "instance": getattr(a.agent_id, "instance", None) or "default",
                        "reason": reason,
                    }
                )
                out["summary"]["exclusion_reasons"][reason] = (
                    out["summary"]["exclusion_reasons"].get(reason, 0) + 1
                )
                if show_all_candidates and a.agent_id.type == agent_type:
                    # Include excluded candidate in candidates with marking
                    with contextlib.suppress(Exception):
                        q = await self._measure_queue_length(a)
                        h = await self._measure_heartbeat_age(a)
                        s = self._measure_success_rate(a)
                        out["candidates"].append(
                            {
                                "instance": a.agent_id.instance or "default",
                                "queue_length": int(q),
                                "heartbeat_age_s": float(h),
                                "success_rate": float(s),
                                "score": None,
                                "excluded": True,
                                "exclusion_reason": reason,
                            }
                        )
            else:
                candidates.append(a)
        out["summary"]["excluded_count"] = len(out["excluded"])
        if not candidates:
            out["reason"] = "no healthy candidates found"
            return out
        scored, best = await self._score_candidates(candidates)
        # shape output
        scored_sorted = sorted(scored, key=lambda d: d.get("score", 1e9))
        if show_all_candidates:
            # Keep previously appended excluded entries; append healthy scored entries
            for d in scored_sorted:
                out["candidates"].append(
                    {
                        "instance": d["instance"],
                        "queue_length": d["queue_length"],
                        "heartbeat_age_s": d["heartbeat_age_s"],
                        "success_rate": d["success_rate"],
                        "score": d["score"],
                        "excluded": False,
                    }
                )
            out["summary"]["healthy_candidates"] = len(scored_sorted)
        else:
            # Only healthy candidates
            out["candidates"] = [
                {
                    "instance": d["instance"],
                    "queue_length": d["queue_length"],
                    "heartbeat_age_s": d["heartbeat_age_s"],
                    "success_rate": d["success_rate"],
                    "score": d["score"],
                    "excluded": False,
                }
                for d in scored_sorted
            ]
            out["summary"]["healthy_candidates"] = len(scored_sorted)
        if best is not None:
            out["selected"] = best.agent_id.instance or "default"
            out["reason"] = "selected minimal weighted score"
        else:
            out["reason"] = "fallback to first candidate"
        return out
