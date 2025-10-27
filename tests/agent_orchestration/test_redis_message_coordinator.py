import asyncio
import json
import uuid

import pytest

from tta_ai.orchestration import (
    AgentId,
    AgentMessage,
    AgentType,
    MessagePriority,
    MessageType,
)
from tta_ai.orchestration.coordinators import RedisMessageCoordinator


@pytest.mark.redis
@pytest.mark.asyncio
async def test_send_message_enqueues(redis_client):
    coord = RedisMessageCoordinator(redis_client, key_prefix="testao")
    sender = AgentId(type=AgentType.IPA)
    recipient = AgentId(type=AgentType.WBA, instance="i1")
    msg = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=sender,
        recipient=recipient,
        message_type=MessageType.REQUEST,
        payload={"hello": "world"},
        priority=MessagePriority.NORMAL,
    )
    res = await coord.send_message(sender, recipient, msg)
    assert res.delivered is True

    # Inspect Redis queue
    key = f"testao:queue:{recipient.type.value}:{recipient.instance}"
    item = await redis_client.lpop(key)
    assert item is not None
    parsed = json.loads(item)
    assert parsed["message"]["message_id"] == msg.message_id
    assert parsed["message"]["payload"] == msg.payload


@pytest.mark.redis
@pytest.mark.asyncio
async def test_broadcast_message(redis_client):
    coord = RedisMessageCoordinator(redis_client, key_prefix="testao")
    sender = AgentId(type=AgentType.IPA)
    recipients: list[AgentId] = [
        AgentId(type=AgentType.WBA, instance="a"),
        AgentId(type=AgentType.NGA, instance="b"),
    ]
    msg = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=sender,
        recipient=recipients[0],
        message_type=MessageType.EVENT,
        payload={"foo": 1},
    )
    results = await coord.broadcast_message(sender, msg, recipients)
    assert len(results) == 2
    assert all(r.delivered for r in results)

    # Verify one message per recipient
    for r in recipients:
        key = f"testao:queue:{r.type.value}:{r.instance}"
        val = await redis_client.lpop(key)
        assert val is not None


@pytest.mark.redis
@pytest.mark.asyncio
async def test_subscribe_records_types(redis_client):
    coord = RedisMessageCoordinator(redis_client, key_prefix="testao")
    agent = AgentId(type=AgentType.NGA, instance="sub1")
    sub = coord.subscribe_to_messages(agent, [MessageType.REQUEST, MessageType.EVENT])
    assert sub.agent_id == agent
    # allow background task to run
    await asyncio.sleep(0.05)
    key = f"testao:subs:{agent.type.value}:{agent.instance}"
    members = await redis_client.smembers(key)
    assert {m.decode() for m in members} >= {"request", "event"}
