"""
Redis-backed implementation of the MessageCoordinator (Task 4.1).

This minimal implementation provides:
- send_message: enqueue to a recipient-specific Redis list
- broadcast_message: looped send to multiple recipients
- subscribe_to_messages: record subscriptions in Redis for observability (set)

Notes:
- Retrieval/consumption is intentionally out-of-scope for Task 4.1
- Keys are namespaced via key_prefix (default "ao")
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import List

from redis.asyncio import Redis

from ..interfaces import MessageCoordinator
from ..models import AgentId, AgentMessage, MessageType
from ..messaging import MessageResult, MessageSubscription, QueueMessage


class RedisMessageCoordinator(MessageCoordinator):
    def __init__(self, redis: Redis, key_prefix: str = "ao") -> None:
        self._redis = redis
        self._pfx = key_prefix.rstrip(":")

    def _queue_key(self, agent_id: AgentId) -> str:
        inst = agent_id.instance or "default"
        return f"{self._pfx}:queue:{agent_id.type.value}:{inst}"

    def _subs_key(self, agent_id: AgentId) -> str:
        inst = agent_id.instance or "default"
        return f"{self._pfx}:subs:{agent_id.type.value}:{inst}"

    async def send_message(self, sender: AgentId, recipient: AgentId, message: AgentMessage) -> MessageResult:
        try:
            # Ensure timestamp exists and is ISO-8601
            if not message.timestamp:
                message.timestamp = datetime.now(timezone.utc).isoformat()

            qmsg = QueueMessage(message=message)
            payload = json.dumps(qmsg.model_dump())
            await self._redis.rpush(self._queue_key(recipient), payload)
            return MessageResult(message_id=message.message_id, delivered=True)
        except Exception as e:
            return MessageResult(message_id=message.message_id, delivered=False, error=str(e))

    async def broadcast_message(self, sender: AgentId, message: AgentMessage, recipients: List[AgentId]) -> List[MessageResult]:
        results: List[MessageResult] = []
        for r in recipients:
            res = await self.send_message(sender=sender, recipient=r, message=message)
            results.append(res)
        return results

    def subscribe_to_messages(self, agent_id: AgentId, message_types: List[MessageType]) -> MessageSubscription:
        # Fire-and-forget recording; unit tests can assert stored values
        sub_id = f"sub_{uuid.uuid4().hex[:12]}"
        # Store subscription types in a Redis set
        # We do not await here because interface is sync; schedule best-effort task
        async def _store():
            try:
                if message_types:
                    await self._redis.sadd(self._subs_key(agent_id), *[mt.value for mt in message_types])
            except Exception:
                # Non-fatal for subscription bookkeeping in this minimal version
                pass
        # Ensure background task is scheduled in an event loop if available
        try:
            import asyncio
            asyncio.get_running_loop().create_task(_store())
        except Exception:
            # If no loop, ignore persistence; subscription object still returned
            pass

        return MessageSubscription(subscription_id=sub_id, agent_id=agent_id, message_types=message_types)

