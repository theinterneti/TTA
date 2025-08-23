import asyncio
import pytest

from src.agent_orchestration.tools.models import ToolSpec
from src.agent_orchestration.tools.redis_tool_registry import RedisToolRegistry
from src.agent_orchestration.tools.coordinator import ToolCoordinator
from src.agent_orchestration.tools.policy_config import ToolPolicyConfig
from src.agent_orchestration.tools.models import ToolPolicy


async def noop():
    await asyncio.sleep(0)
    return "ok"


@pytest.mark.redis
@pytest.mark.asyncio
async def test_registry_idempotency_and_concurrency(redis_client):
    reg = RedisToolRegistry(redis_client, key_prefix="testao_idem")

    async def factory():
        return ToolSpec(name="same.tool", version="1.0.0", description="x")

    policy = ToolPolicy(config=ToolPolicyConfig(callable_allowlist=[
        "tests.agent_orchestration.tools.test_registry_idempotency.noop",
        "test_registry_idempotency.noop",
    ]))

    coord = ToolCoordinator(registry=reg, policy=policy)

    # concurrent create_or_get calls should not duplicate tool in registry
    res = await asyncio.gather(
        coord.create_or_get("sig-same-tool-100", factory),
        coord.create_or_get("sig-same-tool-100", factory),
    )
    assert res[0].signature_hash() == res[1].signature_hash()

    # ensure registry returns a single entry
    existing = await reg.get_tool("same.tool", "1.0.0")
    assert existing is not None

    # concurrent invocations via invocation service
    from src.agent_orchestration.tools.invocation_service import ToolInvocationService
    svc = ToolInvocationService(registry=reg, coordinator=coord, policy=policy)
    out = await asyncio.gather(
        svc.invoke_tool_by_spec(existing, noop),
        svc.invoke_tool_by_spec(existing, noop),
    )
    assert out == ["ok", "ok"]

