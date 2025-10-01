import asyncio
import time

import pytest

from src.agent_orchestration.tools.coordinator import ToolCoordinator
from src.agent_orchestration.tools.invocation_service import ToolInvocationService
from src.agent_orchestration.tools.metrics import get_tool_metrics
from src.agent_orchestration.tools.models import ToolPolicy, ToolSpec
from src.agent_orchestration.tools.policy_config import ToolPolicyConfig
from src.agent_orchestration.tools.redis_tool_registry import RedisToolRegistry


async def slow_async(ms):
    await asyncio.sleep(ms / 1000.0)
    return "done"


def slow_sync(ms):
    time.sleep(ms / 1000.0)
    return "done"


def boom():
    raise RuntimeError("boom")


@pytest.mark.redis
@pytest.mark.asyncio
async def test_async_timeout_and_metrics(redis_client):
    reg = RedisToolRegistry(redis_client, key_prefix="testao_timeout_async")
    spec = ToolSpec(name="t.async", version="1.0.0", description="async")
    await reg.register_tool(spec)

    cfg = ToolPolicyConfig(
        default_timeout_ms=50,
        callable_allowlist=[
            "tests.agent_orchestration.tools.test_timeouts_and_metrics.slow_async",
            "test_timeouts_and_metrics.slow_async",
        ],
    )
    policy = ToolPolicy(config=cfg)
    svc = ToolInvocationService(
        registry=reg,
        coordinator=ToolCoordinator(registry=reg, policy=policy),
        policy=policy,
    )

    with pytest.raises(TimeoutError):
        await svc.invoke_tool_by_spec(spec, slow_async, ms=200)

    snap = get_tool_metrics().snapshot()
    assert snap.get("t.async:1.0.0", {}).get("failures", 0) >= 1


@pytest.mark.redis
@pytest.mark.asyncio
async def test_sync_timeout_and_metrics(redis_client):
    reg = RedisToolRegistry(redis_client, key_prefix="testao_timeout_sync")
    spec = ToolSpec(name="t.sync", version="1.0.0", description="sync")
    await reg.register_tool(spec)

    cfg = ToolPolicyConfig(
        default_timeout_ms=50,
        callable_allowlist=[
            "tests.agent_orchestration.tools.test_timeouts_and_metrics.slow_sync",
            "test_timeouts_and_metrics.slow_sync",
        ],
    )
    policy = ToolPolicy(config=cfg)
    svc = ToolInvocationService(
        registry=reg,
        coordinator=ToolCoordinator(registry=reg, policy=policy),
        policy=policy,
    )

    with pytest.raises(TimeoutError):
        await svc.invoke_tool_by_spec(spec, slow_sync, ms=200)

    snap = get_tool_metrics().snapshot()
    assert snap.get("t.sync:1.0.0", {}).get("failures", 0) >= 1


@pytest.mark.redis
@pytest.mark.asyncio
async def test_exception_records_failure_metric(redis_client):
    reg = RedisToolRegistry(redis_client, key_prefix="testao_metrics_fail")
    spec = ToolSpec(name="t.fail", version="1.0.0", description="fail")
    await reg.register_tool(spec)

    cfg = ToolPolicyConfig(
        callable_allowlist=[
            "tests.agent_orchestration.tools.test_timeouts_and_metrics.boom",
            "test_timeouts_and_metrics.boom",
        ]
    )
    policy = ToolPolicy(config=cfg)
    svc = ToolInvocationService(
        registry=reg,
        coordinator=ToolCoordinator(registry=reg, policy=policy),
        policy=policy,
    )

    with pytest.raises(RuntimeError):
        await svc.invoke_tool_by_spec(spec, boom)

    snap = get_tool_metrics().snapshot()
    assert snap.get("t.fail:1.0.0", {}).get("failures", 0) >= 1
