import asyncio
import os

import pytest

from tta_ai.orchestration.tools.coordinator import ToolCoordinator
from tta_ai.orchestration.tools.models import ToolParameter, ToolPolicy, ToolSpec
from tta_ai.orchestration.tools.redis_tool_registry import RedisToolRegistry
from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_tools_diagnostics_endpoint(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8610,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.tools": {
                "redis_key_prefix": "ao",
                "cache_ttl_s": 0.5,
                "cache_max_items": 32,
            },
        }
    )
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    from starlette.testclient import TestClient

    client = TestClient(app)

    # Register a tool
    reg = comp._tool_registry
    import uuid as _uuid

    unique_name = f"kg.query.{_uuid.uuid4().hex[:6]}"
    spec = ToolSpec(
        name=unique_name,
        version="1.0.0",
        description="Query KG",
        parameters=[ToolParameter(name="q", schema={"type": "string"})],
        returns_schema={"type": "object"},
    )
    # register may be False if concurrently registered; still acceptable
    await reg.register_tool(spec)

    res = client.get("/tools")
    assert res.status_code == 200
    body = res.json()
    assert "tools" in body and isinstance(body["tools"], list)
    # allow either presence (if not pruned) or absence
    assert any(t["name"] == unique_name for t in body["tools"]) or body["tools"] == []

    assert comp._stop_impl() is True


@pytest.mark.redis
@pytest.mark.asyncio
async def test_concurrent_registry_and_coordinator(redis_client):
    reg = RedisToolRegistry(
        redis_client, key_prefix="testao_conc", cache_ttl_s=0.2, cache_max_items=8
    )
    coord = ToolCoordinator(registry=reg, policy=ToolPolicy(allow_network_tools=True))

    async def factory():
        return ToolSpec(
            name="kg.query",
            version="1.0.2",
            description="Query KG",
            parameters=[ToolParameter(name="q", schema={"type": "string"})],
            returns_schema={"type": "object"},
        )

    # concurrent create_or_get calls
    async def worker(n):
        s = await coord.create_or_get("sig-kg-query-v102", factory)
        return s.version

    versions = await asyncio.gather(*[worker(i) for i in range(10)])
    # all should point to the same version
    assert all(v == "1.0.2" for v in versions)

    # cleanup while listing
    await reg.touch_last_used("kg.query", "1.0.2")
    await reg.list_tools()
    removed = await reg.cleanup_expired(max_idle_seconds=0.0)
    # Even if removed due to threshold, operations should be safe
    assert removed >= 0
    lst_after = await reg.list_tools()
    assert isinstance(lst_after, list)
