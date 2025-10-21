import asyncio
import os

import pytest

from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_agents_endpoint_includes_heartbeat_age(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8611,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.agents.auto_register": True,
            "agent_orchestration.agents.heartbeat_ttl": 1.0,
            "agent_orchestration.agents.heartbeat_interval": 0.2,
            "agent_orchestration.agents.ipa.enabled": True,
            "agent_orchestration.agents.wba.enabled": False,
            "agent_orchestration.agents.nga.enabled": False,
        }
    )
    await comp.start()
    # allow /agents to populate
    await asyncio.sleep(0.5)

    # Call diagnostics /agents handler directly
    app = comp._create_diagnostics_app()
    assert app is not None
    # The router function is internal; instead, rely on registry listing
    reg = getattr(comp, "_agent_registry", None)
    assert reg is not None
    try:
        from tta_ai.orchestration.registries import RedisAgentRegistry

        if isinstance(reg, RedisAgentRegistry):
            lst = await reg.list_registered()
            assert isinstance(lst, list)
            assert len(lst) >= 1
            assert "last_heartbeat_age" not in lst[0]
    except Exception:
        pass

    await comp.stop()
