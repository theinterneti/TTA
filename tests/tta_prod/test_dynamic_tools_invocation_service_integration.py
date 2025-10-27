import pytest

from tta_ai.orchestration.tools.metrics import get_tool_metrics
from tta.prod.src.tools.dynamic_tools import DynamicTool


@pytest.mark.redis
def test_dynamic_tool_exec_routes_through_service_and_collects_metrics(redis_client):
    code = """
async def mytool_action(x: int, y: int):
    return x + y
"""
    tool = DynamicTool(
        name="mytool",
        description="add",
        function_code=code,
        parameters=[],
        kg_read=False,
        kg_write=False,
    )

    res = tool.execute(x=2, y=3)
    assert res == 5

    snap = get_tool_metrics().snapshot()
    assert any(k.startswith("mytool:") for k in snap)
    succ = snap.get("mytool:1.0.0", {})
    if succ:
        assert succ.get("successes", 0) >= 1


@pytest.mark.redis
def test_dynamic_tool_policy_enforcement_blocks_unallowed_callable(
    redis_client, monkeypatch
):
    code = """
async def blocked_action():
    return 1
"""
    tool = DynamicTool(
        name="blocked",
        description="blocked",
        function_code=code,
        parameters=[],
        kg_read=False,
        kg_write=False,
    )

    # Disallow any callable by allowlist (doesn't include our dynamic function)
    monkeypatch.setenv("TTA_ALLOWED_CALLABLES", "never.this.callable")

    with pytest.raises(Exception):
        # Since BaseTool.execute is sync and action is async, policy enforcement should happen
        tool.execute()


@pytest.mark.redis
@pytest.mark.asyncio
async def test_backward_compatibility_direct_call_fallback(redis_client):
    # Running in an event loop should trigger fallback path (direct call)
    code = """
async def fc_action():
    return 42
"""
    tool = DynamicTool(
        name="fc",
        description="fc",
        function_code=code,
        parameters=[],
    )

    res = tool.execute()
    assert res == 42
