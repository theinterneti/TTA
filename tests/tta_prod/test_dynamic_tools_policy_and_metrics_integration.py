# Logseq: [[TTA.dev/Tests/Tta_prod/Test_dynamic_tools_policy_and_metrics_integration]]
import pytest
from tta_ai.orchestration.tools.metrics import get_tool_metrics

from tta.prod.src.tools.dynamic_tools import DynamicTool


@pytest.mark.redis
def test_dynamic_tool_network_policy_blocks_kg(redis_client, monkeypatch):
    # Disallow network tools via env-config fallback path
    monkeypatch.setenv("TTA_ALLOW_NETWORK_TOOLS", "false")

    code = """
async def net_action():
    return 7
"""
    tool = DynamicTool(
        name="net",
        description="kg read",
        function_code=code,
        parameters=[],
        kg_read=True,
        kg_write=False,
    )

    with pytest.raises(Exception):
        tool.execute()


@pytest.mark.redis
def test_dynamic_tool_timeout_records_failure(redis_client, monkeypatch):
    # Configure a very small timeout
    monkeypatch.setenv("TTA_TOOL_TIMEOUT_MS", "50")

    code = """
import asyncio
async def slow_action():
    await asyncio.sleep(0.2)
    return 1
"""
    tool = DynamicTool(
        name="slow",
        description="sleep",
        function_code=code,
        parameters=[],
        kg_read=False,
        kg_write=False,
    )

    with pytest.raises(TimeoutError):
        tool.execute()

    snap = get_tool_metrics().snapshot()
    assert snap.get("slow:1.0.0", {}).get("failures", 0) >= 1
