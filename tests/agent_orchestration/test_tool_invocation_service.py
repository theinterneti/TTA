import asyncio

import pytest
from tta_ai.orchestration.tools.coordinator import ToolCoordinator
from tta_ai.orchestration.tools.invocation_service import ToolInvocationService
from tta_ai.orchestration.tools.metrics import get_tool_metrics
from tta_ai.orchestration.tools.models import ToolParameter, ToolPolicy, ToolSpec
from tta_ai.orchestration.tools.redis_tool_registry import RedisToolRegistry


async def async_ok(a, b):
    await asyncio.sleep(0)
    return a + b


def sync_fail():
    raise RuntimeError("boom")


@pytest.mark.redis
@pytest.mark.asyncio
async def test_tool_invocation_service_records_metrics_and_policy(redis_client):
    reg = RedisToolRegistry(
        redis_client, key_prefix="testao_inv", cache_ttl_s=0.2, cache_max_items=8
    )
    policy = ToolPolicy(
        allow_network_tools=True,
        allowed_callables=[
            "tests.agent_orchestration.test_tool_invocation_service.async_ok",
            "tests.agent_orchestration.test_tool_invocation_service.sync_fail",
            "test_tool_invocation_service.async_ok",
            "test_tool_invocation_service.sync_fail",
        ],
    )
    coord = ToolCoordinator(registry=reg, policy=policy)

    svc = ToolInvocationService(registry=reg, coordinator=coord, policy=policy)

    # Register tool and invoke async function
    spec = ToolSpec(
        name="math.add",
        version="1.0.0",
        description="Add numbers",
        parameters=[
            ToolParameter(name="a", schema={"type": "number"}),
            ToolParameter(name="b", schema={"type": "number"}),
        ],
        returns_schema={"type": "number"},
    )
    await reg.register_tool(spec)

    # Since we didn't pass a resolver, use invoke_tool_by_spec
    result = await svc.invoke_tool_by_spec(spec, async_ok, a=2, b=3)
    assert result == 5

    # Now test failure path and metrics still recorded
    spec2 = ToolSpec(name="do.fail", version="1.0.0", description="Failing tool")
    await reg.register_tool(spec2)
    with pytest.raises(RuntimeError):
        await svc.invoke_tool_by_spec(spec2, sync_fail)

    snap = get_tool_metrics().snapshot()
    assert "math.add:1.0.0" in snap
    assert snap["math.add:1.0.0"]["successes"] >= 1
    assert "do.fail:1.0.0" in snap
    assert snap["do.fail:1.0.0"]["failures"] >= 1


@pytest.mark.redis
@pytest.mark.asyncio
async def test_tool_invocation_service_register_and_invoke(redis_client):
    reg = RedisToolRegistry(redis_client, key_prefix="testao_inv2")
    policy = ToolPolicy(
        allow_network_tools=True,
        allowed_callables=[
            "tests.agent_orchestration.test_tool_invocation_service.async_ok",
            "test_tool_invocation_service.async_ok",
        ],
    )  # noqa: E501
    coord = ToolCoordinator(registry=reg, policy=policy)
    svc = ToolInvocationService(registry=reg, coordinator=coord, policy=policy)

    async def factory():
        return ToolSpec(name="adder", version="1.0.1", description="adder")

    res = await svc.register_and_invoke(factory, "sig-adder-101", async_ok, a=1, b=2)
    assert res == 3
