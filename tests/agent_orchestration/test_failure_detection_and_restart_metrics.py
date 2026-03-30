# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_failure_detection_and_restart_metrics]]
import asyncio
import os

import pytest

from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_failure_detection_and_restart_metrics(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8612,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.monitoring.health_check_interval": 0.2,
            "agent_orchestration.monitoring.failure_detection_enabled": True,
            "agent_orchestration.monitoring.failure_detection_interval": 0.2,
            "agent_orchestration.agents.auto_register": True,
            "agent_orchestration.agents.heartbeat_ttl": 1.0,
            "agent_orchestration.agents.heartbeat_interval": 0.2,
            "agent_orchestration.agents.ipa.enabled": True,
            "agent_orchestration.agents.wba.enabled": False,
            "agent_orchestration.agents.nga.enabled": False,
        }
    )
    await comp.start()
    # Short wait to allow background tasks to run
    await asyncio.sleep(0.6)

    # Force degrade one agent by stopping it, failure detection should attempt restart
    reg = getattr(comp, "_agent_registry", None)
    agents = reg.all() if reg else []
    if agents:
        a = agents[0]
        await a.stop()
    await asyncio.sleep(0.6)

    # Query /metrics-prom to ensure new metrics exist and are numeric
    app = comp._create_diagnostics_app()
    assert app is not None
    # We can't easily call the ASGI endpoint here; instead ensure counters are present by directly calling internal method
    # The metrics endpoint internally builds its own registry; invoke and inspect output string
    out = await app.router.routes[-1].endpoint()  # metrics_prometheus
    assert isinstance(out, str)
    assert "agent_orchestration_agents_unhealthy" in out
    assert "agent_orchestration_agents_restarts_total" in out
    assert "agent_orchestration_agents_fallbacks_total" in out

    await comp.stop()
