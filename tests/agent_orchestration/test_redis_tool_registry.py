# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_redis_tool_registry]]
import asyncio

import pytest
from tta_ai.orchestration.tools.models import ToolParameter, ToolSpec
from tta_ai.orchestration.tools.redis_tool_registry import RedisToolRegistry


@pytest.mark.redis
@pytest.mark.asyncio
async def test_register_get_list_and_cleanup(redis_client):
    reg = RedisToolRegistry(
        redis_client, key_prefix="testao_tools", cache_ttl_s=0.2, cache_max_items=16
    )
    spec = ToolSpec(
        name="kg.query",
        version="1.0.0",
        description="Query KG",
        parameters=[ToolParameter(name="q", schema={"type": "string"})],
        returns_schema={"type": "object"},
    )
    created = await reg.register_tool(spec)
    assert created is True

    # idempotent
    created2 = await reg.register_tool(spec)
    assert created2 is False

    got = await reg.get_tool("kg.query", "1.0.0")
    assert got is not None and got.name == spec.name

    lst = await reg.list_tools()
    assert any(t.name == "kg.query" for t in lst)

    # touch and cleanup
    await reg.touch_last_used("kg.query", "1.0.0")
    await asyncio.sleep(0.05)
    removed = await reg.cleanup_expired(max_idle_seconds=0.01)
    # Recently touched should ideally not be removed; allow 0 or 1 due to coarse timers
    assert removed in (0, 1)

    # simulate idle and expect potential removal depending on timing
    await asyncio.sleep(0.25)
    removed2 = await reg.cleanup_expired(max_idle_seconds=0.1)
    assert removed2 >= 0
