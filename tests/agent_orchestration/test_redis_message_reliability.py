import asyncio
import uuid

import pytest

from src.agent_orchestration import (
    AgentId,
    AgentMessage,
    AgentType,
    FailureType,
    MessagePriority,
    MessageType,
)
from src.agent_orchestration.coordinators import RedisMessageCoordinator


@pytest.mark.redis
@pytest.mark.asyncio
async def test_priority_ordering_and_fifo(redis_client):
    coord = RedisMessageCoordinator(redis_client, key_prefix="testao")
    sender = AgentId(type=AgentType.IPA)
    recipient = AgentId(type=AgentType.WBA, instance="prio")

    # Enqueue: LOW then HIGH then two NORMAL
    msgs = [
        AgentMessage(
            message_id=uuid.uuid4().hex,
            sender=sender,
            recipient=recipient,
            message_type=MessageType.EVENT,
            payload={"i": 1},
            priority=MessagePriority.LOW,
        ),
        AgentMessage(
            message_id=uuid.uuid4().hex,
            sender=sender,
            recipient=recipient,
            message_type=MessageType.EVENT,
            payload={"i": 2},
            priority=MessagePriority.HIGH,
        ),
        AgentMessage(
            message_id=uuid.uuid4().hex,
            sender=sender,
            recipient=recipient,
            message_type=MessageType.EVENT,
            payload={"i": 3},
            priority=MessagePriority.NORMAL,
        ),
        AgentMessage(
            message_id=uuid.uuid4().hex,
            sender=sender,
            recipient=recipient,
            message_type=MessageType.EVENT,
            payload={"i": 4},
            priority=MessagePriority.NORMAL,
        ),
    ]
    for m in msgs:
        r = await coord.send_message(sender, recipient, m)
        assert r.delivered is True

    # Receive first: HIGH
    rm = await coord.receive(recipient, visibility_timeout=1)
    assert rm is not None
    assert rm.queue_message.message.payload["i"] == 2
    await coord.ack(recipient, rm.token)

    # Next two should be NORMAL in FIFO order (3 then 4)
    rm = await coord.receive(recipient, visibility_timeout=1)
    assert rm.queue_message.message.payload["i"] == 3
    await coord.ack(recipient, rm.token)

    rm = await coord.receive(recipient, visibility_timeout=1)
    assert rm.queue_message.message.payload["i"] == 4
    await coord.ack(recipient, rm.token)

    # Finally, LOW
    rm = await coord.receive(recipient, visibility_timeout=1)
    assert rm.queue_message.message.payload["i"] == 1
    await coord.ack(recipient, rm.token)


@pytest.mark.redis
@pytest.mark.asyncio
async def test_retry_exponential_backoff_and_limits(redis_client):
    coord = RedisMessageCoordinator(redis_client, key_prefix="testao")
    await coord.configure(
        retry_attempts=2, backoff_base=0.05, backoff_factor=2.0, backoff_max=1.0
    )

    sender = AgentId(type=AgentType.IPA)
    recipient = AgentId(type=AgentType.NGA, instance="retry")
    m = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=sender,
        recipient=recipient,
        message_type=MessageType.REQUEST,
        payload={"n": 1},
    )
    assert (await coord.send_message(sender, recipient, m)).delivered

    # Receive and NACK (transient)
    rm1 = await coord.receive(recipient, visibility_timeout=0.1)
    assert rm1 is not None
    await coord.nack(recipient, rm1.token, failure=FailureType.TRANSIENT, error="first")

    # Immediately try to receive again; should be None due to backoff delay
    rm_none = await coord.receive(recipient, visibility_timeout=0.1)
    assert rm_none is None

    # Wait for ~base backoff (0.05s) and attempt again
    await asyncio.sleep(0.08)
    rm2 = await coord.receive(recipient, visibility_timeout=0.1)
    assert rm2 is not None

    # Second NACK should schedule with ~0.1s delay and then go to DLQ after exceeding attempts
    await coord.nack(
        recipient, rm2.token, failure=FailureType.TRANSIENT, error="second"
    )
    # Too soon
    assert (await coord.receive(recipient, visibility_timeout=0.1)) is None
    await asyncio.sleep(0.12)

    # Receive third time, NACK to exceed attempts -> should go to DLQ (no re-schedule)
    rm3 = await coord.receive(recipient, visibility_timeout=0.1)
    assert rm3 is not None
    await coord.nack(recipient, rm3.token, failure=FailureType.TRANSIENT, error="third")

    # No more messages available
    assert (await coord.receive(recipient, visibility_timeout=0.1)) is None

    # Check DLQ has the message
    dlq_key = f"testao:dlq:{recipient.type.value}:{recipient.instance or 'default'}"
    dlq_len = await redis_client.llen(dlq_key)
    assert dlq_len >= 1


@pytest.mark.redis
@pytest.mark.asyncio
async def test_visibility_timeout_and_recovery(redis_client):
    coord = RedisMessageCoordinator(redis_client, key_prefix="testao")
    sender = AgentId(type=AgentType.IPA)
    recipient = AgentId(type=AgentType.WBA, instance="recover")

    m = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=sender,
        recipient=recipient,
        message_type=MessageType.EVENT,
    )
    assert (await coord.send_message(sender, recipient, m)).delivered

    rm = await coord.receive(recipient, visibility_timeout=0.05)
    assert rm is not None
    # Do not ack; wait until visibility timeout expires
    await asyncio.sleep(0.06)
    recovered = await coord.recover_pending(recipient)
    assert recovered >= 1

    # Now should be able to receive again
    rm2 = await coord.receive(recipient, visibility_timeout=0.1)
    assert rm2 is not None
    await coord.ack(recipient, rm2.token)


@pytest.mark.redis
@pytest.mark.asyncio
async def test_queue_overflow_graceful(redis_client):
    coord = RedisMessageCoordinator(redis_client, key_prefix="testao")
    await coord.configure(queue_size=1)
    sender = AgentId(type=AgentType.IPA)
    recipient = AgentId(type=AgentType.NGA, instance="overflow")

    m1 = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=sender,
        recipient=recipient,
        message_type=MessageType.REQUEST,
    )
    m2 = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=sender,
        recipient=recipient,
        message_type=MessageType.REQUEST,
    )

    res1 = await coord.send_message(sender, recipient, m1)
    assert res1.delivered is True

    res2 = await coord.send_message(sender, recipient, m2)
    assert res2.delivered is False
    assert res2.error == "queue full"
