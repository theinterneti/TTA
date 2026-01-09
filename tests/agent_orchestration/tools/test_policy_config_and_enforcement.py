# Logseq: [[TTA.dev/Tests/Agent_orchestration/Tools/Test_policy_config_and_enforcement]]
import asyncio

import pytest
from tta_ai.orchestration.tools.coordinator import ToolCoordinator
from tta_ai.orchestration.tools.invocation_service import ToolInvocationService
from tta_ai.orchestration.tools.models import ToolPolicy, ToolSpec
from tta_ai.orchestration.tools.policy_config import ToolPolicyConfig
from tta_ai.orchestration.tools.redis_tool_registry import RedisToolRegistry


async def async_identity(v):
    await asyncio.sleep(0)
    return v


def sync_identity(v):
    return v


@pytest.mark.redis
@pytest.mark.asyncio
async def test_kg_enabled_tools_policy_network(redis_client, monkeypatch):
    reg = RedisToolRegistry(redis_client, key_prefix="testao_policy_kg")

    # Tool with KG read -> safety flag 'network'
    spec = ToolSpec(
        name="kg.read", version="1.0.0", description="KG read", safety_flags=["network"]
    )  # KG flag
    await reg.register_tool(spec)

    # Disallow network -> should block
    cfg = ToolPolicyConfig(
        allow_network_tools=False,
        callable_allowlist=[
            "tests.agent_orchestration.tools.test_policy_config_and_enforcement.async_identity",
            "test_policy_config_and_enforcement.async_identity",
        ],
    )
    policy = ToolPolicy(config=cfg)
    coord = ToolCoordinator(registry=reg, policy=policy)
    svc = ToolInvocationService(registry=reg, coordinator=coord, policy=policy)
    with pytest.raises(Exception):
        await svc.invoke_tool_by_spec(spec, async_identity, v=1)

    # Allow network -> should pass
    cfg2 = ToolPolicyConfig(
        allow_network_tools=True, callable_allowlist=cfg.callable_allowlist
    )
    policy2 = ToolPolicy(config=cfg2)
    coord2 = ToolCoordinator(registry=reg, policy=policy2)
    svc2 = ToolInvocationService(registry=reg, coordinator=coord2, policy=policy2)
    res = await svc2.invoke_tool_by_spec(spec, async_identity, v=2)
    assert res == 2


@pytest.mark.redis
@pytest.mark.asyncio
async def test_policy_enforcement_matrix(redis_client):
    reg = RedisToolRegistry(redis_client, key_prefix="testao_policy_matrix")

    cases = [
        ({"allow_network_tools": False}, ["network"], True),
        ({"allow_network_tools": True}, ["network"], False),
        ({"allow_filesystem_tools": False}, ["filesystem"], True),
        ({"allow_filesystem_tools": True}, ["filesystem"], False),
        ({"allow_process_tools": False}, ["process"], True),
        ({"allow_process_tools": True}, ["process"], False),
        (
            {"allow_network_tools": False, "allow_filesystem_tools": False},
            ["network", "filesystem"],
            True,
        ),
    ]

    for cfg_kwargs, flags, expect_block in cases:
        spec = ToolSpec(
            name=f"t.{'-'.join(flags)}",
            version="1.0.0",
            description="combo",
            safety_flags=flags,
        )
        await reg.register_tool(spec)
        cfg = ToolPolicyConfig(
            callable_allowlist=[
                "tests.agent_orchestration.tools.test_policy_config_and_enforcement.sync_identity",
                "test_policy_config_and_enforcement.sync_identity",
            ],
            **cfg_kwargs,
        )
        policy = ToolPolicy(config=cfg)
        coord = ToolCoordinator(registry=reg, policy=policy)
        svc = ToolInvocationService(registry=reg, coordinator=coord, policy=policy)
        if expect_block:
            with pytest.raises(Exception):
                await svc.invoke_tool_by_spec(spec, sync_identity, v="ok")
        else:
            res = await svc.invoke_tool_by_spec(spec, sync_identity, v="ok")
            assert res == "ok"
