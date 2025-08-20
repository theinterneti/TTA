import asyncio
import os
import uuid

import pytest

from src.components.agent_orchestration_component import AgentOrchestrationComponent


class DummyConfig(dict):
    def get(self, key, default=None):
        return super().get(key, default)


@pytest.mark.redis
@pytest.mark.asyncio
async def test_poll_queue_metrics_once(redis_client):
    # Provide a redis url into component config
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent({"player_experience.api.redis_url": url, "agent_orchestration.port": 8599})

    # Start component (this will create coordinator using the provided URL)
    assert comp._start_impl() is True

    # Enqueue a message to create keys and then run single polling cycle
    from src.agent_orchestration.coordinators import RedisMessageCoordinator
    coord = comp._message_coordinator
    assert isinstance(coord, RedisMessageCoordinator)

    from src.agent_orchestration import AgentId, AgentType, AgentMessage, MessageType
    aid = AgentId(type=AgentType.IPA, instance="testpoll")
    msg = AgentMessage(message_id=uuid.uuid4().hex, sender=aid, recipient=aid, message_type=MessageType.EVENT)
    assert (await coord.send_message(aid, aid, msg)).delivered

    # Run one polling cycle
    await comp._poll_queue_metrics_once()

    snap = coord.metrics.snapshot()
    # At least some gauges should be present
    assert any(k.startswith("ipa:testpoll|") or k.startswith("ipa:testpoll") for k in [f"{k0}|{k1}" for (k0,k1) in coord.metrics.gauges.queue_lengths.keys()])

    # Stop component
    assert comp._stop_impl() is True

