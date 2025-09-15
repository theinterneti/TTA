import pytest

from src.agent_orchestration.tools.coordinator import ToolCoordinator
from src.agent_orchestration.tools.models import ToolParameter, ToolPolicy, ToolSpec
from src.agent_orchestration.tools.redis_tool_registry import RedisToolRegistry


@pytest.mark.redis
@pytest.mark.asyncio
async def test_tool_coordinator_create_or_get(redis_client):
    reg = RedisToolRegistry(redis_client, key_prefix="testao_tools2")
    coord = ToolCoordinator(registry=reg, policy=ToolPolicy(allow_network_tools=False))

    async def factory():
        return ToolSpec(
            name="kg.query",
            version="1.0.1",
            description="Query KG",
            parameters=[ToolParameter(name="q", schema={"type": "string"})],
            returns_schema={"type": "object"},
            safety_flags=[],
        )

    spec = await coord.create_or_get("sig-kg-query-v101", factory)
    assert spec is not None and spec.name == "kg.query"

    # second call should not create duplicate
    spec2 = await coord.create_or_get("sig-kg-query-v101", factory)
    assert spec2.version == spec.version
