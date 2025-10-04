import asyncio
import os

import pytest
from starlette.testclient import TestClient

from src.agent_orchestration.tools.metrics import get_tool_metrics
from src.agent_orchestration.tools.models import ToolSpec
from src.components.agent_orchestration_component import AgentOrchestrationComponent


async def add(a: int, b: int) -> int:
    await asyncio.sleep(0)
    return a + b


def fail() -> None:
    raise RuntimeError("nope")


@pytest.mark.redis
@pytest.mark.asyncio
async def test_callable_registry_and_execute(redis_client):
    # Setup component with diagnostics and tool execution enabled
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8612,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.diagnostics.allow_tool_execution": True,
            "agent_orchestration.tools": {
                "redis_key_prefix": "ao",
                "cache_ttl_s": 0.5,
                "cache_max_items": 32,
                "allowed_callables": [
                    "tests.agent_orchestration.test_callable_registry_and_execute_endpoint.add",
                    "tests.agent_orchestration.test_callable_registry_and_execute_endpoint.fail",
                    "test_callable_registry_and_execute_endpoint.add",
                    "test_callable_registry_and_execute_endpoint.fail",
                ],
            },
        }
    )
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    # Register tool, and register callable in registry via component field
    reg = comp._tool_registry
    spec = ToolSpec(name="math.add", version="2.0.0", description="Add")
    await reg.register_tool(spec)
    # callable registry is present on component
    creg = comp._callable_registry
    creg.register_callable("math.add", "2.0.0", add)

    # Execute via endpoint
    resp = client.post(
        "/tools/execute",
        json={
            "tool_name": "math.add",
            "version": "2.0.0",
            "arguments": {"a": 2, "b": 4},
        },
    )
    assert resp.status_code == 200
    js = resp.json()
    assert js.get("ok") is True and js.get("result") == 6

    # Failure path
    spec2 = ToolSpec(name="bad", version="1.0.0", description="fail")
    await reg.register_tool(spec2)
    creg.register_callable("bad", "1.0.0", fail)
    resp2 = client.post(
        "/tools/execute", json={"tool_name": "bad", "version": "1.0.0", "arguments": {}}
    )
    assert resp2.status_code == 200
    js2 = resp2.json()
    assert js2.get("ok") is False and "nope" in js2.get("error", "")

    # Metrics captured
    snap = get_tool_metrics().snapshot()
    assert "math.add:2.0.0" in snap and snap["math.add:2.0.0"]["successes"] >= 1
    assert "bad:1.0.0" in snap and snap["bad:1.0.0"]["failures"] >= 1
