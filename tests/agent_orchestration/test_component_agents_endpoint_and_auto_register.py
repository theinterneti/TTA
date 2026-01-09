# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_component_agents_endpoint_and_auto_register]]
import os

import pytest

from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_agents_endpoint_and_auto_register(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8610,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.agents.auto_register": True,
            "agent_orchestration.agents.heartbeat_ttl": 2.0,
            "agent_orchestration.agents.heartbeat_interval": 0.5,
            "agent_orchestration.agents.ipa.enabled": True,
            "agent_orchestration.agents.ipa.instance": "worker-1",
            "agent_orchestration.agents.wba.enabled": True,
            "agent_orchestration.agents.nga.enabled": True,
        }
    )
    assert comp._start_impl() is True

    # Build ASGI app directly
    app = comp._create_diagnostics_app()
    assert app is not None

    from starlette.testclient import TestClient

    client = TestClient(app)

    res = client.get("/agents")
    assert res.status_code == 200
    body = res.json()
    assert "local" in body and "redis_index" in body
    # Derived metrics should be present (performance keys may be zero but exist)
    # Note: performance is attached when any Agent.process_with_timeout has run; it's ok if absent.
    # Ensure heartbeat age is present for redis_index entries
    if body["redis_index"]:
        assert "last_heartbeat_age" in body["redis_index"][0]

    # Shutdown should deregister keys
    assert comp._stop_impl() is True
    # After stop, agent key should be deleted or expire shortly; we check direct key for ipa instance
    import asyncio

    await asyncio.sleep(0.1)
    key = "ao:agents:input_processor:worker-1"
    assert (await redis_client.get(key)) in (None,)
