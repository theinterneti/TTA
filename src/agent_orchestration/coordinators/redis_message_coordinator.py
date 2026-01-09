"""

# Logseq: [[TTA.dev/Agent_orchestration/Coordinators/Redis_message_coordinator]]
Redis-backed implementation of the MessageCoordinator with reliability (Task 4.1 + 4.2).

Capabilities:
- send_message: enqueue to a recipient-specific Redis list (legacy/audit) and ready scheduler (zset)
- broadcast_message: looped send to multiple recipients
- subscribe_to_messages: record subscriptions in Redis for observability (set)
- receive/ack/nack: reservation semantics with visibility timeouts and exponential backoff retries
- recover_pending: reclaim expired reservations back to ready queues

Keys (per agent instance):
- {pfx}:queue:{type}:{inst}                 - legacy/audit list of enqueued payloads
- {pfx}:sched:{type}:{inst}:prio:{lvl}      - zset of ready/delayed items (score=available_at_us)
- {pfx}:reserved:{type}:{inst}              - hash of token -> payload JSON
- {pfx}:reserved_deadlines:{type}:{inst}    - zset of token -> deadline_us
- {pfx}:dlq:{type}:{inst}                   - dead-letter queue list
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
import uuid
from datetime import UTC, datetime

from redis.asyncio import Redis

from ..interfaces import MessageCoordinator
from ..messaging import (
    FailureType,
    MessageResult,
    MessageSubscription,
    QueueMessage,
    ReceivedMessage,
)
from ..models import AgentId, AgentMessage, AgentType, MessageType

logger = logging.getLogger(__name__)


def _now_us() -> int:
    return int(time.time() * 1_000_000)


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()


class RedisMessageCoordinator(MessageCoordinator):
    def __init__(self, redis: Redis, key_prefix: str = "ao") -> None:
        # Optional router attached by component for intelligent routing
        self._agent_router = None

        self._redis = redis
        self._pfx = key_prefix.rstrip(":")
        # Defaults; configurable via configure()
        self._queue_size = 10000
        self._retry_attempts = 3
        # Metrics
        from ..metrics import MessageMetrics

        self.metrics = MessageMetrics()
        self._backoff_base = 1.0
        self._backoff_factor = 2.0
        self._backoff_max = 30.0

    # ---- Key helpers ----
    def _queue_key(self, agent_id: AgentId) -> str:
        inst = agent_id.instance or "default"
        return f"{self._pfx}:queue:{agent_id.type.value}:{inst}"

    def _subs_key(self, agent_id: AgentId) -> str:
        inst = agent_id.instance or "default"
        return f"{self._pfx}:subs:{agent_id.type.value}:{inst}"

    def _sched_key(self, agent_id: AgentId, prio_level: int) -> str:
        inst = agent_id.instance or "default"
        return f"{self._pfx}:sched:{agent_id.type.value}:{inst}:prio:{prio_level}"

    def _reserved_hash(self, agent_id: AgentId) -> str:
        inst = agent_id.instance or "default"
        return f"{self._pfx}:reserved:{agent_id.type.value}:{inst}"

    def _reserved_deadlines(self, agent_id: AgentId) -> str:
        inst = agent_id.instance or "default"
        return f"{self._pfx}:reserved_deadlines:{agent_id.type.value}:{inst}"

    def _dlq_key(self, agent_id: AgentId) -> str:
        inst = agent_id.instance or "default"
        return f"{self._pfx}:dlq:{agent_id.type.value}:{inst}"

    # ---- Public API ----
    async def send_message(
        self, sender: AgentId, recipient: AgentId, message: AgentMessage
    ) -> MessageResult:
        try:
            # Queue backpressure (graceful overflow handling)
            qlen = await self._redis.llen(self._queue_key(recipient))
            if qlen is not None and qlen >= self._queue_size:
                return MessageResult(
                    message_id=message.message_id, delivered=False, error="queue full"
                )

            # Ensure timestamp exists and is ISO-8601
            if not message.timestamp:
                message.timestamp = _iso_now()

            qmsg = QueueMessage(
                message=message,
                priority=message.priority,
                enqueued_at=_iso_now(),
                delivery_attempts=0,
            )
            payload = json.dumps(qmsg.model_dump())
            # Legacy/audit list
            await self._redis.rpush(self._queue_key(recipient), payload)
            # Schedule into priority zset (available now)
            score = _now_us()
            await self._redis.zadd(
                self._sched_key(recipient, int(message.priority)), {payload: score}
            )
            # Metrics: mark successful delivery
            with contextlib.suppress(Exception):
                self.metrics.inc_delivered_ok(1)
            return MessageResult(message_id=message.message_id, delivered=True)
        except Exception as e:
            with contextlib.suppress(Exception):
                self.metrics.inc_delivered_error(1)
            return MessageResult(
                message_id=message.message_id, delivered=False, error=str(e)
            )

    async def broadcast_message(
        self, sender: AgentId, message: AgentMessage, recipients: list[AgentId]
    ) -> list[MessageResult]:
        results: list[MessageResult] = []
        for r in recipients:
            res = await self.send_message(sender=sender, recipient=r, message=message)
            results.append(res)
        return results

    def subscribe_to_messages(
        self, agent_id: AgentId, message_types: list[MessageType]
    ) -> MessageSubscription:
        # Fire-and-forget recording; unit tests can assert stored values
        sub_id = f"sub_{uuid.uuid4().hex[:12]}"

        async def _store():
            with contextlib.suppress(Exception):
                if message_types:
                    await self._redis.sadd(
                        self._subs_key(agent_id), *[mt.value for mt in message_types]
                    )

        with contextlib.suppress(Exception):
            asyncio.get_running_loop().create_task(_store())
        return MessageSubscription(
            subscription_id=sub_id, agent_id=agent_id, message_types=message_types
        )

    async def receive(
        self, agent_id: AgentId, visibility_timeout: int = 5
    ) -> ReceivedMessage | None:
        """Reserve the next message by priority (HIGH->NORMAL->LOW) and FIFO within each."""
        now = _now_us()
        for prio in (9, 5, 1):
            skey = self._sched_key(agent_id, prio)
            # Find one due item (score <= now)
            members = await self._redis.zrangebyscore(
                skey, min=-1, max=now, start=0, num=1
            )
            if not members:
                continue
            member = members[0]
            # Remove it from sched set
            await self._redis.zrem(skey, member)
            payload = (
                member.decode() if isinstance(member, (bytes, bytearray)) else member
            )
            # Create reservation
            token = f"res_{uuid.uuid4().hex[:16]}"
            deadline = now + int(visibility_timeout * 1_000_000)
            # Store reservation
            await self._redis.hset(self._reserved_hash(agent_id), token, payload)
            await self._redis.zadd(
                self._reserved_deadlines(agent_id), {token: deadline}
            )
            # Return wrapper
            qmsg_dict = json.loads(payload)
            return ReceivedMessage(
                token=token,
                queue_message=QueueMessage(**qmsg_dict),
                visibility_deadline=datetime.fromtimestamp(
                    deadline / 1_000_000, tz=UTC
                ).isoformat(),
            )
        return None

    async def ack(self, agent_id: AgentId, token: str) -> bool:
        # Remove reservation and underlying audit list entry
        payload = await self._redis.hget(self._reserved_hash(agent_id), token)
        await self._redis.hdel(self._reserved_hash(agent_id), token)
        await self._redis.zrem(self._reserved_deadlines(agent_id), token)
        if payload:
            # Remove one occurrence from audit list
            with contextlib.suppress(Exception):
                await self._redis.lrem(self._queue_key(agent_id), 1, payload)
            return True
        return False

    async def nack(
        self,
        agent_id: AgentId,
        token: str,
        failure: FailureType = FailureType.TRANSIENT,
        error: str | None = None,
    ) -> bool:
        payload = await self._redis.hget(self._reserved_hash(agent_id), token)
        await self._redis.hdel(self._reserved_hash(agent_id), token)
        await self._redis.zrem(self._reserved_deadlines(agent_id), token)
        if not payload:
            return False
        try:
            data = json.loads(payload)
            qm = QueueMessage(**data)
            # Update attempts and error
            qm.delivery_attempts = int(qm.delivery_attempts or 0) + 1
            qm.last_error = error
            updated = json.dumps(qm.model_dump())
            # Also ensure audit list has a canonical payload form for LREM cleanup later
            await self._redis.lrem(self._queue_key(agent_id), 1, payload)
            await self._redis.rpush(self._queue_key(agent_id), updated)

            # DLQ on permanent failure or when attempts exceed allowed retries
            if (
                failure == FailureType.PERMANENT
                or qm.delivery_attempts > self._retry_attempts
            ):
                await self._redis.rpush(self._dlq_key(agent_id), updated)
                with contextlib.suppress(Exception):
                    self.metrics.inc_permanent(1)
                # Alert/notify: administrator visibility for persistent failures
                with contextlib.suppress(Exception):
                    logger.error(
                        "DLQ enqueue for %s:%s message_id=%s attempts=%s error=%s",
                        agent_id.type.value,
                        agent_id.instance or "default",
                        qm.message.message_id,
                        qm.delivery_attempts,
                        error,
                    )
                # Also remove the latest audit copy to avoid duplication
                await self._redis.lrem(self._queue_key(agent_id), 1, updated)
                return True

            # Schedule retry with exponential backoff
            delay = min(
                self._backoff_base
                * (self._backoff_factor ** (qm.delivery_attempts - 1)),
                self._backoff_max,
            )
            score = _now_us() + int(delay * 1_000_000)
            await self._redis.zadd(
                self._sched_key(agent_id, int(qm.priority)), {updated: score}
            )
            with contextlib.suppress(Exception):
                self.metrics.inc_retries_scheduled(1, last_backoff_seconds=delay)
                self.metrics.inc_nacks(1)
            return True
        except Exception:
            # If we cannot parse, dead-letter to avoid poison-pill loops
            await self._redis.rpush(self._dlq_key(agent_id), payload)
            return False

    async def recover_pending(self, agent_id: AgentId | None = None) -> int:
        """Reclaim expired reservations back to ready queues.
        If agent_id is None, perform a best-effort scan across known agent instances.
        Returns number of messages recovered. Logs per-agent counts for observability.
        """
        recovered_total = 0
        per_agent_counts: dict[str, int] = {}
        agent_ids: list[AgentId]
        if agent_id is None:
            # Discover known agent queues by pattern (best-effort, cheap approach)
            seen: set[str] = set()
            agent_ids = []
            for at in (AgentType.IPA, AgentType.WBA, AgentType.NGA):
                # Prefer deadlines keys
                for pattern in (
                    f"{self._pfx}:reserved_deadlines:{at.value}:*",
                    f"{self._pfx}:reserved:{at.value}:*",
                ):
                    async for key in self._redis.scan_iter(match=pattern):
                        parts = (
                            key.decode() if isinstance(key, (bytes, bytearray)) else key
                        )
                        inst = parts.split(":")[-1]
                        sig = f"{at.value}:{inst}"
                        if sig in seen:
                            continue
                        seen.add(sig)
                        agent_ids.append(AgentId(type=at, instance=inst))
        else:
            agent_ids = [agent_id]

        now = _now_us()
        for aid in agent_ids:
            recovered_for_agent = 0
            dkey = self._reserved_deadlines(aid)
            tokens = await self._redis.zrangebyscore(dkey, min=-1, max=now)
            for t in tokens:
                token = t.decode() if isinstance(t, (bytes, bytearray)) else t
                payload = await self._redis.hget(self._reserved_hash(aid), token)
                if payload:
                    try:
                        pdata = (
                            payload if isinstance(payload, str) else payload.decode()
                        )
                        data = json.loads(pdata)
                        qm = QueueMessage(**data)
                        score = _now_us()
                        # Re-schedule using the original payload to preserve audit list matching
                        await self._redis.zadd(
                            self._sched_key(aid, int(qm.priority)), {payload: score}
                        )
                        recovered_total += 1
                        recovered_for_agent += 1
                    except Exception:
                        await self._redis.rpush(self._dlq_key(aid), payload)
                await self._redis.hdel(self._reserved_hash(aid), token)
                await self._redis.zrem(self._reserved_deadlines(aid), token)
            if recovered_for_agent:
                agent_key = f"{aid.type.name.lower()}:{aid.instance or 'default'}"
                per_agent_counts[agent_key] = recovered_for_agent

        if per_agent_counts:
            for agent_key, count in per_agent_counts.items():
                with contextlib.suppress(Exception):
                    logger.info("Recovered %s messages for agent %s", count, agent_key)
        return recovered_total

    async def configure(
        self,
        *,
        queue_size: int | None = None,
        retry_attempts: int | None = None,
        backoff_base: float | None = None,
        backoff_factor: float | None = None,
        backoff_max: float | None = None,
    ) -> None:
        if queue_size is not None:
            self._queue_size = queue_size
        if retry_attempts is not None:
            self._retry_attempts = retry_attempts
        if backoff_base is not None:
            self._backoff_base = backoff_base
        if backoff_factor is not None:
            self._backoff_factor = backoff_factor
        if backoff_max is not None:
            self._backoff_max = backoff_max
