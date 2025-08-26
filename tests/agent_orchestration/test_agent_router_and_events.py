import asyncio
import os
import pytest

from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_agent_router_resolves_and_events_endpoint(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent({
        "player_experience.api.redis_url": url,
        "agent_orchestration.port": 8613,
        "agent_orchestration.diagnostics.enabled": True,
        "agent_orchestration.monitoring.health_check_interval": 0.2,
        "agent_orchestration.monitoring.failure_detection_enabled": True,
        "agent_orchestration.monitoring.failure_detection_interval": 0.2,
        "agent_orchestration.agents.auto_register": True,
        "agent_orchestration.agents.heartbeat_ttl": 1.0,
        "agent_orchestration.agents.heartbeat_interval": 0.2,
        "agent_orchestration.agents.ipa.enabled": True,
        "agent_orchestration.agents.wba.enabled": True,
        "agent_orchestration.agents.nga.enabled": False,
    })
    await comp.start()
    await asyncio.sleep(0.5)

    # Trigger a fallback by stopping one agent and waiting for detection
    reg = getattr(comp, "_agent_registry", None)
    agents = reg.all() if reg else []
    if agents:
        a = agents[0]
        await a.stop()
    await asyncio.sleep(0.6)

    # Check that /events returns something structured
    app = comp._create_diagnostics_app()
    data = await app.router.routes[-1].endpoint()  # /events endpoint
    assert isinstance(data, dict) and "events" in data

    await comp.stop()

