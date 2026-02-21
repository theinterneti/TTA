# Logseq: [[TTA.dev/Agent_orchestration/Workflow_transaction]]
from __future__ import annotations

import contextlib
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Savepoint:
    name: str
    created_at: float


@dataclass
class CleanupItem:
    kind: str  # "redis_key" | "tmp_file" | "custom"
    value: str
    done: bool = False


@dataclass
class TxState:
    run_id: str
    savepoints: list[Savepoint] = field(default_factory=list)
    cleanup: dict[str, list[CleanupItem]] = field(default_factory=dict)  # name -> items


class WorkflowTransaction:
    """
    Transaction-like helper for workflows with savepoints and rollback.

    Redis keys (pfx=ao):
      - {pfx}:wf:tx:{run_id} -> JSON TxState
    """

    def __init__(self, redis, key_prefix: str = "ao") -> None:
        self._redis = redis
        self._pfx = key_prefix.rstrip(":")

    def _key(self, run_id: str) -> str:
        return f"{self._pfx}:wf:tx:{run_id}"

    # ---- Public API ----
    async def create_savepoint(self, run_id: str, name: str, created_at: float) -> None:
        tx = await self._load(run_id) or TxState(run_id=run_id)
        # idempotent: do not duplicate
        if not any(sp.name == name for sp in tx.savepoints):
            tx.savepoints.append(Savepoint(name=name, created_at=created_at))
        await self._persist(tx)

    async def add_cleanup(
        self, run_id: str, savepoint: str, *, kind: str, value: str
    ) -> None:
        tx = await self._load(run_id) or TxState(run_id=run_id)
        items = tx.cleanup.setdefault(savepoint, [])
        # idempotent: avoid duplicate (kind,value)
        if not any((c.kind == kind and c.value == value) for c in items):
            items.append(CleanupItem(kind=kind, value=value))
        await self._persist(tx)

    async def rollback_to(self, run_id: str, savepoint: str) -> dict[str, Any]:
        tx = await self._load(run_id)
        if not tx:
            return {"ok": False, "error": "no_transaction"}
        if not any(sp.name == savepoint for sp in tx.savepoints):
            return {"ok": False, "error": "savepoint_not_found"}
        # Execute cleanup items for the savepoint and all prior savepoints (inclusive)
        executed = 0
        errors: list[str] = []
        # Determine affected savepoints (<= requested index)
        sps = [sp.name for sp in tx.savepoints]
        try:
            idx = sps.index(savepoint)
        except ValueError:
            return {"ok": False, "error": "savepoint_not_found"}
        affected = sps[: idx + 1]
        for sp in affected:
            for item in tx.cleanup.get(sp, []):
                if item.done:
                    continue
                try:
                    await self._cleanup_item(item)
                    item.done = True
                    executed += 1
                except Exception as e:
                    errors.append(f"{sp}:{item.kind}:{item.value}:{e}")
        # Trim state to only the target savepoint (as the current state)
        tx.savepoints = [sp for sp in tx.savepoints if sp.name == savepoint]
        await self._persist(tx)
        return {"ok": True, "executed": executed, "errors": errors}

    # ---- Helpers ----
    async def _cleanup_item(self, item: CleanupItem) -> None:
        if item.kind == "redis_key":
            with contextlib.suppress(Exception):
                await self._redis.delete(item.value)
        elif item.kind == "tmp_file":
            with contextlib.suppress(FileNotFoundError):
                os.unlink(item.value)
        except_list = {"custom"}
        if item.kind in except_list:
            # Custom cleanup types should be handled by callers; we mark done
            return

    async def _persist(self, tx: TxState) -> None:
        await self._redis.set(self._key(tx.run_id), json.dumps(self._dump(tx)))

    async def _load(self, run_id: str) -> TxState | None:
        raw = await self._redis.get(self._key(run_id))
        if not raw:
            return None
        try:
            return self._from_dump(
                json.loads(raw if isinstance(raw, str) else raw.decode())
            )
        except Exception:
            return None

    # ---- ser/de ----
    def _dump(self, tx: TxState) -> dict[str, Any]:
        return {
            "run_id": tx.run_id,
            "savepoints": [
                {"name": s.name, "created_at": s.created_at} for s in tx.savepoints
            ],
            "cleanup": {
                sp: [{"kind": c.kind, "value": c.value, "done": c.done} for c in items]
                for sp, items in tx.cleanup.items()
            },
        }

    def _from_dump(self, d: dict[str, Any]) -> TxState:
        tx = TxState(run_id=d.get("run_id"))
        for s in d.get("savepoints", []) or []:
            tx.savepoints.append(
                Savepoint(
                    name=s.get("name"), created_at=float(s.get("created_at") or 0)
                )
            )
        for sp, items in (d.get("cleanup") or {}).items():
            tx.cleanup[sp] = [
                CleanupItem(
                    kind=i.get("kind"),
                    value=i.get("value"),
                    done=bool(i.get("done", False)),
                )
                for i in items or []
            ]
        return tx
