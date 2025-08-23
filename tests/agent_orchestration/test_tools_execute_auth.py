import os
import asyncio
import pytest
from starlette.testclient import TestClient

from src.components.agent_orchestration_component import AgentOrchestrationComponent
from src.agent_orchestration.tools.models import ToolSpec


async def add(a: int, b: int) -> int:
    await asyncio.sleep(0)
    return a + b


@pytest.mark.redis
@pytest.mark.asyncio
async def test_tools_execute_auth_unauthorized(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent({
        "player_experience.api.redis_url": url,
        "agent_orchestration.port": 8613,
        "agent_orchestration.diagnostics.enabled": True,
        "agent_orchestration.diagnostics.allow_tool_execution": True,
        "agent_orchestration.diagnostics.tool_exec_api_key": "secret",
        "agent_orchestration.tools": {
            "allowed_callables": [
                "tests.agent_orchestration.test_tools_execute_auth.add",
                "test_tools_execute_auth.add",
            ]
        }
    })
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    # register tool and callable
    reg = comp._tool_registry
    spec = ToolSpec(name="math.add", version="1.0.0", description="Add")
    await reg.register_tool(spec)
    comp._callable_registry.register_callable("math.add", "1.0.0", add)

    # no header should be unauthorized
    r1 = client.post("/tools/execute", json={"tool_name": "math.add", "version": "1.0.0", "arguments": {"a": 1, "b": 2}})
    assert r1.status_code == 401

    # wrong header should be unauthorized
    r2 = client.post("/tools/execute", headers={"X-AO-DIAG-KEY": "nope"}, json={"tool_name": "math.add", "version": "1.0.0", "arguments": {"a": 1, "b": 2}})
    assert r2.status_code == 401


@pytest.mark.redis
@pytest.mark.asyncio
async def test_tools_execute_auth_authorized_and_allowed_tools(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent({
        "player_experience.api.redis_url": url,
        "agent_orchestration.port": 8614,
        "agent_orchestration.diagnostics.enabled": True,
        "agent_orchestration.diagnostics.allow_tool_execution": True,
        "agent_orchestration.diagnostics.tool_exec_api_key": "secret",
        "agent_orchestration.diagnostics.allowed_tools": ["math.add:*"] ,
        "agent_orchestration.tools": {
            "allowed_callables": [
                "tests.agent_orchestration.test_tools_execute_auth.add",
                "test_tools_execute_auth.add",
            ]
        }
    })
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    reg = comp._tool_registry
    spec = ToolSpec(name="math.add", version="2.0.0", description="Add")
    await reg.register_tool(spec)
    comp._callable_registry.register_callable("math.add", "2.0.0", add)

    # wrong tool should be blocked by allowed_tools
    bad = client.post("/tools/execute", headers={"X-AO-DIAG-KEY": "secret"}, json={"tool_name": "other", "version": "1.0.0", "arguments": {}})
    assert bad.status_code == 200 and bad.json().get("ok") is False

    # correct tool and key
    ok = client.post("/tools/execute", headers={"X-AO-DIAG-KEY": "secret"}, json={"tool_name": "math.add", "version": "2.0.0", "arguments": {"a": 3, "b": 4}})
    assert ok.status_code == 200
    js = ok.json()
    assert js.get("ok") is True and js.get("result") == 7

