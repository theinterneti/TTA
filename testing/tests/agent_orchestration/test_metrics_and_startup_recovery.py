import asyncio
import uuid

import pytest

from src.agent_orchestration import (
    AgentId,
    AgentMessage,
    AgentType,
    MessageType,
)
from src.agent_orchestration.coordinators import RedisMessageCoordinator


@pytest.mark.redis
@pytest.mark.asyncio
async def test_metrics_counters_and_gauges(redis_client):
    coord = RedisMessageCoordinator(redis_client, key_prefix="testao")
    # Speed up backoff for test
    await coord.configure(backoff_base=0.05, backoff_factor=2.0, backoff_max=1.0)

    sender = AgentId(type=AgentType.IPA)
    recipient = AgentId(type=AgentType.WBA, instance="metrics")

    # Send one message successfully
    m1 = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=sender,
        recipient=recipient,
        message_type=MessageType.EVENT,
    )
    assert (await coord.send_message(sender, recipient, m1)).delivered

    # Verify delivered_ok incremented
    snap = coord.metrics.snapshot()
    assert snap["delivery"]["delivered_ok"] >= 1

    # Force a nack path to increment retry metrics
    rm = await coord.receive(recipient, visibility_timeout=0.05)
    assert rm is not None
    await coord.nack(recipient, rm.token, error="transient")

    # Wait for retry to reappear and ack it
    await asyncio.sleep(0.08)
    rm2 = await coord.receive(recipient, visibility_timeout=0.05)
    assert rm2 is not None
    await coord.ack(recipient, rm2.token)

    snap2 = coord.metrics.snapshot()
    assert snap2["retry"]["total_nacks"] >= 1
    assert snap2["retry"]["total_retries_scheduled"] >= 1
    assert snap2["retry"]["last_backoff_seconds"] > 0.0


@pytest.mark.redis
@pytest.mark.asyncio
async def test_auto_recovery_on_startup_simulation(redis_client):
    coord = RedisMessageCoordinator(redis_client, key_prefix="testao")
    sender = AgentId(type=AgentType.IPA)
    recipient = AgentId(type=AgentType.NGA, instance="autorecover")

    m = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=sender,
        recipient=recipient,
        message_type=MessageType.REQUEST,
    )
    assert (await coord.send_message(sender, recipient, m)).delivered

    # Reserve but do not ack
    r = await coord.receive(recipient, visibility_timeout=0.05)
    assert r is not None

    # Simulate restart: call recover_pending(None) to scan globally
    await asyncio.sleep(0.06)
    recovered = await coord.recover_pending(None)
    assert recovered >= 1

    # Now message should be available again
    r2 = await coord.receive(recipient, visibility_timeout=0.05)
    assert r2 is not None
    await coord.ack(recipient, r2.token)
