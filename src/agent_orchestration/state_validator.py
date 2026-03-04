# Logseq: [[TTA.dev/Agent_orchestration/State_validator]]
from __future__ import annotations

import contextlib
import json
import logging
import time
from typing import Any

from .models import AgentType

logger = logging.getLogger(__name__)

_AGENT_TYPES = (AgentType.IPA, AgentType.WBA, AgentType.NGA)
_DEFAULT_PRIORITY = 5


def _decode(value: bytes | bytearray | str) -> str:
    """Decode a Redis value to str."""
    return value.decode() if isinstance(value, (bytes, bytearray)) else value


def _extract_priority(payload: bytes | bytearray | str) -> int:
    """Extract message priority from a JSON payload, defaulting to NORMAL."""
    try:
        data = json.loads(_decode(payload))
        return int(data.get("priority", _DEFAULT_PRIORITY))
    except Exception:
        return _DEFAULT_PRIORITY


class StateValidator:
    """
    Performs workflow state integrity checks and best-effort repairs using Redis.

    Validation rules implemented:
    - Reclaim expired reservations (stale locks) back to ready queues
    - Remove orphaned reservation entries without payloads
    - Optionally clear orphaned processes/keys (best-effort, Redis-only for now)

    Metrics: increments 'state_validation_errors' in {pfx}:wf:metrics for any detected inconsistency.
    """

    def __init__(self, redis, key_prefix: str = "ao") -> None:
        self._redis = redis
        self._pfx = key_prefix.rstrip(":")

    async def validate_and_repair(self) -> dict[str, Any]:
        """Run all repair passes and return aggregate results."""
        repaired = 0
        errors = 0

        repaired += await self._coordinator_recovery_pass()

        try:
            r, e = await self._targeted_scan_pass()
            repaired += r
            errors += e

            repaired += await self._brute_force_pass()
        except Exception:
            logger.warning(
                "StateValidator.validate_and_repair error during scan passes",
                exc_info=True,
            )

        if repaired == 0:
            repaired += await self._raw_bytes_pass()

        return {"repaired": repaired, "errors": errors}

    # ---- Recovery passes ----

    async def _coordinator_recovery_pass(self) -> int:
        """Use RedisMessageCoordinator for robust token recovery."""
        try:
            from .coordinators import RedisMessageCoordinator

            coord = RedisMessageCoordinator(self._redis, key_prefix=self._pfx)
            recovered = await coord.recover_pending(None)
            return int(recovered or 0)
        except Exception:
            logger.debug("Coordinator recovery pass skipped", exc_info=True)
            return 0

    async def _targeted_scan_pass(self) -> tuple[int, int]:
        """Scan each agent type for expired reservations and requeue them."""
        repaired = 0
        errors = 0
        now_us = int(time.time() * 1_000_000)
        passes = (now_us, None)

        for at in _AGENT_TYPES:
            instances = await self._discover_instances(at)
            for inst in instances:
                repaired += await self._recover_instance_via_coordinator(at, inst)
                r, e = await self._requeue_expired_tokens(at, inst, passes)
                repaired += r
                errors += e

        return repaired, errors

    async def _brute_force_pass(self) -> int:
        """Brute-force scan reserved hashes regardless of earlier results."""
        repaired = 0
        try:
            now_us = int(time.time() * 1_000_000)
            for at in _AGENT_TYPES:
                klist = await self._redis.keys(f"{self._pfx}:reserved:{at.value}:*")
                for kk in klist or []:
                    k = _decode(kk)
                    inst = k.split(":")[-1]
                    repaired += await self._repair_hash_tokens(at, inst, k, now_us)
        except Exception:
            logger.debug("Brute-force pass error", exc_info=True)
        return repaired

    async def _raw_bytes_pass(self) -> int:
        """Last-chance repair using raw bytes to avoid encoding mismatches."""
        repaired = 0
        try:
            now_us = int(time.time() * 1_000_000)
            klist = await self._redis.keys(f"{self._pfx}:reserved_deadlines:*")
            for kk in klist or []:
                dkey = _decode(kk)
                parts = dkey.split(":")
                if len(parts) < 4:
                    continue
                at_val, inst = parts[-2], parts[-1]
                try:
                    at = AgentType(at_val)
                except ValueError:
                    logger.debug(
                        "Skipping deadline key %s: invalid agent type '%s'",
                        dkey,
                        at_val,
                    )
                    continue
                repaired += await self._repair_deadline_tokens(at, inst, dkey, now_us)
        except Exception:
            logger.debug("Raw bytes pass error", exc_info=True)
        return repaired

    # ---- Instance discovery ----

    async def _discover_instances(self, at: AgentType) -> set[str]:
        """Build the set of instances from deadline zsets and reserved hashes."""
        instances: set[str] = set()
        async for key in self._redis.scan_iter(
            match=f"{self._pfx}:reserved_deadlines:{at.value}:*"
        ):
            instances.add(_decode(key).split(":")[-1])
        async for key in self._redis.scan_iter(
            match=f"{self._pfx}:reserved:{at.value}:*"
        ):
            instances.add(_decode(key).split(":")[-1])
        # Also union with KEYS results (robustness in tests/small envs)
        try:
            for pattern in (
                f"{self._pfx}:reserved_deadlines:{at.value}:*",
                f"{self._pfx}:reserved:{at.value}:*",
            ):
                for kk in await self._redis.keys(pattern) or []:
                    instances.add(_decode(kk).split(":")[-1])
        except Exception:
            logger.debug("KEYS fallback failed for %s", at.value, exc_info=True)
        return instances

    # ---- Per-instance repair helpers ----

    async def _recover_instance_via_coordinator(self, at: AgentType, inst: str) -> int:
        """Ask the coordinator to perform recovery for a specific instance."""
        try:
            from .coordinators import RedisMessageCoordinator
            from .models import AgentId

            coord = RedisMessageCoordinator(self._redis, key_prefix=self._pfx)
            return int(await coord.recover_pending(AgentId(type=at, instance=inst)))
        except Exception:
            logger.debug(
                "Coordinator recovery failed for %s:%s", at.value, inst, exc_info=True
            )
            return 0

    async def _requeue_expired_tokens(
        self,
        at: AgentType,
        inst: str,
        passes: tuple[int, None],
    ) -> tuple[int, int]:
        """Requeue expired tokens for an agent instance across two time passes."""
        repaired = 0
        errors = 0
        dkey = f"{self._pfx}:reserved_deadlines:{at.value}:{inst}"

        for cutoff in passes:
            cut = cutoff if cutoff is not None else int(time.time() * 1_000_000)
            tokens = await self._collect_expired_tokens(at, inst, dkey, cut)
            if not tokens:
                continue
            for tok in tokens:
                try:
                    repaired += await self._requeue_single_token(
                        at, inst, dkey, tok, cut
                    )
                except Exception:
                    logger.debug(
                        "Failed to requeue token %s for %s:%s",
                        tok,
                        at.value,
                        inst,
                        exc_info=True,
                    )
                    errors += 1
                    await self._incr_metric("state_validation_errors", 1)

        return repaired, errors

    async def _collect_expired_tokens(
        self, at: AgentType, inst: str, dkey: str, cutoff: int
    ) -> set[str]:
        """Collect expired tokens from deadline zset and reserved hash."""
        tokens: set[str] = set()
        zr_tokens = await self._redis.zrangebyscore(dkey, min=-1, max=cutoff)
        for tb in zr_tokens or []:
            tokens.add(_decode(tb))
        try:
            htokens = await self._redis.hkeys(self._res_hash(at, inst))
            for ht in htokens or []:
                htok = _decode(ht)
                try:
                    dscore = await self._redis.zscore(dkey, htok)
                except Exception:
                    dscore = None
                if dscore is None or float(dscore) <= float(cutoff):
                    tokens.add(htok)
        except Exception:
            logger.debug(
                "Hash token scan failed for %s:%s", at.value, inst, exc_info=True
            )
        return tokens

    async def _requeue_single_token(
        self,
        at: AgentType,
        inst: str,
        dkey: str,
        tok: str,
        timestamp: int,
    ) -> int:
        """Requeue a single expired token. Returns 1 on success, 0 otherwise."""
        payload = await self._redis.hget(self._res_hash(at, inst), tok)
        if not payload:
            await self._redis.zrem(dkey, tok)
            return 1
        await self._reschedule_payload(at, inst, payload, timestamp)
        await self._redis.hdel(self._res_hash(at, inst), tok)
        await self._redis.zrem(dkey, tok)
        return 1

    async def _reschedule_payload(
        self,
        at: AgentType,
        inst: str,
        payload: bytes | bytearray | str,
        timestamp: int,
    ) -> None:
        """Reschedule a payload to the appropriate queue, or DLQ on failure."""
        try:
            prio = _extract_priority(payload)
            await self._redis.zadd(
                self._sched_key(at, inst, prio), {payload: timestamp}
            )
            await self._redis.rpush(self._queue_key(at, inst), payload)
        except Exception:
            logger.debug("Rescheduling to DLQ for %s:%s", at.value, inst, exc_info=True)
            await self._redis.rpush(self._dlq_key(at, inst), payload)

    # ---- Brute-force / raw-bytes helpers ----

    async def _repair_hash_tokens(
        self, at: AgentType, inst: str, hash_key: str, now_us: int
    ) -> int:
        """Repair all expired tokens in a reserved hash."""
        repaired = 0
        dkey = f"{self._pfx}:reserved_deadlines:{at.value}:{inst}"
        hkeys = await self._redis.hkeys(hash_key)
        for ht in hkeys or []:
            tok = _decode(ht)
            try:
                dscore = await self._redis.zscore(dkey, tok)
            except Exception:
                dscore = None
            if dscore is not None and float(dscore) > float(now_us):
                continue
            payload = await self._redis.hget(hash_key, tok)
            if payload:
                await self._reschedule_payload(at, inst, payload, now_us)
            await self._redis.hdel(hash_key, tok)
            await self._redis.zrem(dkey, tok)
            repaired += 1
        return repaired

    async def _repair_deadline_tokens(
        self, at: AgentType, inst: str, dkey: str, now_us: int
    ) -> int:
        """Repair tokens from a deadline zset using raw bytes."""
        repaired = 0
        tokens = await self._redis.zrangebyscore(dkey, min=-1, max=now_us)
        if not tokens:
            return 0
        for tb in tokens:
            payload = await self._redis.hget(
                f"{self._pfx}:reserved:{at.value}:{inst}", tb
            )
            if payload:
                await self._reschedule_payload(at, inst, payload, now_us)
            await self._redis.hdel(f"{self._pfx}:reserved:{at.value}:{inst}", tb)
            await self._redis.zrem(dkey, tb)
            repaired += 1
        return repaired

    # ---- Key helpers ----

    def _res_hash(self, at: AgentType, inst: str) -> str:
        return f"{self._pfx}:reserved:{at.value}:{inst}"

    def _sched_key(self, at: AgentType, inst: str, prio: int) -> str:
        return f"{self._pfx}:sched:{at.value}:{inst}:prio:{prio}"

    def _queue_key(self, at: AgentType, inst: str) -> str:
        return f"{self._pfx}:queue:{at.value}:{inst}"

    def _dlq_key(self, at: AgentType, inst: str) -> str:
        return f"{self._pfx}:dlq:{at.value}:{inst}"

    async def _incr_metric(self, name: str, inc: int) -> None:
        with contextlib.suppress(Exception):
            await self._redis.hincrby(f"{self._pfx}:wf:metrics", name, int(inc))
