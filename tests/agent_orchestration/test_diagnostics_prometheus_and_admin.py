# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_diagnostics_prometheus_and_admin]]
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
async def test_diagnostics_gated_and_prometheus(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    # Gate diagnostics off
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8601,
            "agent_orchestration.diagnostics.enabled": False,
        }
    )
    assert comp._start_impl() is True
    # No server start expected; stop immediately
    assert comp._stop_impl() is True

    # Gate diagnostics on and build app directly to test endpoints
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8602,
            "agent_orchestration.diagnostics.enabled": True,
        }
    )
    assert comp._start_impl() is True

    # Use internal app creation to avoid running server in test
    app = comp._create_diagnostics_app()
    assert app is not None

    # Acquire coord and generate some metrics
    coord = comp._message_coordinator
    from tta_ai.orchestration import AgentId, AgentMessage, AgentType, MessageType

    aid = AgentId(type=AgentType.IPA, instance="promtest")
    m = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=aid,
        recipient=aid,
        message_type=MessageType.EVENT,
    )
    assert (await coord.send_message(aid, aid, m)).delivered

    # Build ASGI app client
    from starlette.testclient import TestClient

    client = TestClient(app)
    # /health
    res = client.get("/health")
    assert res.status_code == 200
    # /metrics (json snapshot)
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "delivery" in res.json()
    # /metrics-prom (prometheus text)
    res = client.get("/metrics-prom")
    assert res.status_code == 200
    body = res.text
    assert "agent_orchestration_messages_delivered_total" in body

    # stop component
    assert comp._stop_impl() is True


@pytest.mark.redis
@pytest.mark.asyncio
async def test_admin_recover_script(redis_client):
    # Simulate admin recover via function
    # Build URL based on the redis_client fixture to ensure we hit the same instance
    kwargs = redis_client.connection_pool.connection_kwargs
    host = kwargs.get("host", "localhost")
    port = kwargs.get("port", 6379)
    db = kwargs.get("db", 0)
    url = f"redis://{host}:{port}/{db}"
    from tta_ai.orchestration import AgentId, AgentMessage, AgentType, MessageType
    from tta_ai.orchestration.admin.recover import run_recovery

    # Create a reservation to be recovered
    from tta_ai.orchestration.coordinators import RedisMessageCoordinator

    coord = RedisMessageCoordinator(redis_client, key_prefix="ao")
    aid = AgentId(type=AgentType.IPA, instance="adminrecov")
    m = AgentMessage(
        message_id=uuid.uuid4().hex,
        sender=aid,
        recipient=aid,
        message_type=MessageType.EVENT,
    )
    assert (await coord.send_message(aid, aid, m)).delivered
    rm = await coord.receive(aid, visibility_timeout=0.05)
    assert rm is not None
    await asyncio.sleep(0.06)

    per_agent = await run_recovery(url, key_prefix="ao")
    # Should have recovered at least for our agent
    assert any(k.startswith("ipa:adminrecov") for k in per_agent)
