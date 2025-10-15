from __future__ import annotations

import contextlib
import json
import logging
import time
from typing import Any

from .models import AgentType

logger = logging.getLogger(__name__)


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
        repaired = 0
        errors = 0
        # First try a coordinator-driven recovery for robust token handling
        with contextlib.suppress(Exception):
            from .coordinators import RedisMessageCoordinator

            coord = RedisMessageCoordinator(self._redis, key_prefix=self._pfx)
            recovered = await coord.recover_pending(None)
            repaired += int(recovered or 0)
        # Then perform targeted scans to handle orphans and any remaining edge cases
        now_us = int(time.time() * 1_000_000)
        passes = (now_us, None)
        try:
            for at in (AgentType.IPA, AgentType.WBA, AgentType.NGA):
                # Build instances set from both deadlines zsets and reserved hashes to avoid SCAN timing gaps
                instances: set[str] = set()
                async for key in self._redis.scan_iter(
                    match=f"{self._pfx}:reserved_deadlines:{at.value}:*"
                ):
                    k = key.decode() if isinstance(key, (bytes, bytearray)) else key
                    instances.add(k.split(":")[-1])
                async for key in self._redis.scan_iter(
                    match=f"{self._pfx}:reserved:{at.value}:*"
                ):
                    k = key.decode() if isinstance(key, (bytes, bytearray)) else key
                    instances.add(k.split(":")[-1])
                # Also union with KEYS results (robustness in tests/small envs)
                with contextlib.suppress(Exception):
                    klist = await self._redis.keys(
                        f"{self._pfx}:reserved_deadlines:{at.value}:*"
                    )
                    for kk in klist or []:
                        k = kk.decode() if isinstance(kk, (bytes, bytearray)) else kk
                        instances.add(k.split(":")[-1])
                    klist2 = await self._redis.keys(
                        f"{self._pfx}:reserved:{at.value}:*"
                    )
                    for kk in klist2 or []:
                        k = kk.decode() if isinstance(kk, (bytes, bytearray)) else kk
                        instances.add(k.split(":")[-1])
                # Process each discovered instance
                for inst in instances:
                    dkey = f"{self._pfx}:reserved_deadlines:{at.value}:{inst}"
                    # First, ask the coordinator to perform recovery for this specific instance (robust and atomic)
                    with contextlib.suppress(Exception):
                        from .coordinators import RedisMessageCoordinator
                        from .models import AgentId

                        coord = RedisMessageCoordinator(
                            self._redis, key_prefix=self._pfx
                        )
                        repaired += int(
                            await coord.recover_pending(AgentId(type=at, instance=inst))
                        )
                    # Run up to two passes to be robust to immediate writes
                    for _, cutoff in enumerate(passes):
                        cut = (
                            cutoff
                            if cutoff is not None
                            else int(time.time() * 1_000_000)
                        )
                        zr_tokens = await self._redis.zrangebyscore(
                            dkey, min=-1, max=cut
                        )
                        # Also consider tokens from reserved hash with missing or past deadlines (robust against timing)
                        extra_tokens: list = []
                        with contextlib.suppress(Exception):
                            htokens = await self._redis.hkeys(self._res_hash(at, inst))
                            for ht in htokens or []:
                                htok = (
                                    ht.decode()
                                    if isinstance(ht, (bytes, bytearray))
                                    else ht
                                )
                                try:
                                    dscore = await self._redis.zscore(dkey, htok)
                                except Exception:
                                    dscore = None
                                if dscore is None or float(dscore) <= float(cut):
                                    extra_tokens.append(htok)
                        # Merge and de-duplicate tokens
                        tokens_set = set()
                        for tb in zr_tokens or []:
                            tokens_set.add(
                                tb.decode()
                                if isinstance(tb, (bytes, bytearray))
                                else tb
                            )
                        for et in extra_tokens:
                            tokens_set.add(et)
                        if not tokens_set:
                            continue
                        for tok in tokens_set:
                            try:
                                payload = await self._redis.hget(
                                    self._res_hash(at, inst), tok
                                )
                                if not payload:
                                    # Token expired but payload already reclaimed elsewhere; clean up deadline and count as repaired
                                    await self._redis.zrem(dkey, tok)
                                    repaired += 1
                                    continue
                                # Requeue to sched
                                try:
                                    pdata = (
                                        payload
                                        if isinstance(payload, str)
                                        else payload.decode()
                                    )
                                    data = json.loads(pdata)
                                    prio = int(data.get("priority", 5))
                                    await self._redis.zadd(
                                        self._sched_key(at, inst, prio), {payload: cut}
                                    )
                                    await self._redis.rpush(
                                        self._queue_key(at, inst), payload
                                    )
                                except Exception:
                                    await self._redis.rpush(
                                        self._dlq_key(at, inst), payload
                                    )
                                # Cleanup reservation
                                await self._redis.hdel(self._res_hash(at, inst), tok)
                                await self._redis.zrem(dkey, tok)
                                repaired += 1
                            except Exception:
                                errors += 1
                                await self._incr_metric("state_validation_errors", 1)
            # Final fallback: brute-force over reserved hashes regardless of earlier results
            with contextlib.suppress(Exception):
                now2 = int(time.time() * 1_000_000)
                for at in (AgentType.IPA, AgentType.WBA, AgentType.NGA):
                    klist = await self._redis.keys(f"{self._pfx}:reserved:{at.value}:*")
                    for kk in klist or []:
                        k = kk.decode() if isinstance(kk, (bytes, bytearray)) else kk
                        inst = k.split(":")[-1]
                        hkeys = await self._redis.hkeys(k)
                        for ht in hkeys or []:
                            tok = (
                                ht.decode()
                                if isinstance(ht, (bytes, bytearray))
                                else ht
                            )
                            try:
                                dscore = await self._redis.zscore(
                                    f"{self._pfx}:reserved_deadlines:{at.value}:{inst}",
                                    tok,
                                )
                            except Exception:
                                dscore = None
                            if dscore is None or float(dscore) <= float(now2):
                                payload = await self._redis.hget(k, tok)
                                if payload:
                                    try:
                                        pdata = (
                                            payload
                                            if isinstance(payload, str)
                                            else payload.decode()
                                        )
                                        qmsg = json.loads(pdata)
                                        prio = int(qmsg.get("priority", 5))
                                        await self._redis.zadd(
                                            self._sched_key(at, inst, prio),
                                            {payload: now2},
                                        )
                                        await self._redis.rpush(
                                            self._queue_key(at, inst), payload
                                        )
                                    except Exception:
                                        await self._redis.rpush(
                                            self._dlq_key(at, inst), payload
                                        )
                                await self._redis.hdel(k, tok)
                                await self._redis.zrem(
                                    f"{self._pfx}:reserved_deadlines:{at.value}:{inst}",
                                    tok,
                                )
                                repaired += 1
        except Exception:
            logger.debug("StateValidator.validate_and_repair error", exc_info=True)
        # Last-chance repair using raw bytes to avoid encoding mismatches
        with contextlib.suppress(Exception):
            if repaired == 0:
                now3 = int(time.time() * 1_000_000)
                klist = await self._redis.keys(f"{self._pfx}:reserved_deadlines:*")
                for kk in klist or []:
                    dkey = kk.decode() if isinstance(kk, (bytes, bytearray)) else kk
                    parts = dkey.split(":")
                    if len(parts) < 4:
                        continue
                    at_val = parts[-2]
                    inst = parts[-1]
                    # Resolve AgentType from value string
                    try:
                        at = AgentType(at_val)
                    except Exception as e:
                        logger.debug(
                            f"Skipping deadline key {dkey}: invalid agent type '{at_val}' - {type(e).__name__}"
                        )
                        continue
                    tokens = await self._redis.zrangebyscore(dkey, min=-1, max=now3)
                    if not tokens:
                        continue
                    for tb in tokens:
                        tok_field = tb  # keep original bytes if bytes
                        payload = await self._redis.hget(
                            f"{self._pfx}:reserved:{at.value}:{inst}", tok_field
                        )
                        if payload:
                            # Reschedule using original payload bytes
                            try:
                                # Derive priority without decoding by attempting JSON load; fallback to NORMAL
                                prio = 5
                                try:
                                    pd = (
                                        payload
                                        if isinstance(payload, str)
                                        else payload.decode()
                                    )
                                    jd = json.loads(pd)
                                    prio = int(jd.get("priority", 5))
                                except Exception:
                                    prio = 5
                                await self._redis.zadd(
                                    f"{self._pfx}:sched:{at.value}:{inst}:prio:{prio}",
                                    {payload: now3},
                                )
                            except Exception:
                                await self._redis.rpush(
                                    f"{self._pfx}:dlq:{at.value}:{inst}", payload
                                )
                        await self._redis.hdel(
                            f"{self._pfx}:reserved:{at.value}:{inst}", tok_field
                        )
                        await self._redis.zrem(dkey, tok_field)
                        repaired += 1
        return {"repaired": repaired, "errors": errors}

    # ---- Helpers ----
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
