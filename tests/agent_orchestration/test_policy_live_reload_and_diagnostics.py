# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_policy_live_reload_and_diagnostics]]
import json
import os
import tempfile
import time

import pytest
from starlette.testclient import TestClient
from tta_ai.orchestration.tools.policy_config import redact_policy_config_dict

from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_policy_snapshot_and_redaction(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8620,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.tools": {
                "redis_key_prefix": "ao",
                "cache_ttl_s": 0.5,
                "cache_max_items": 16,
                "allowed_callables": [],
                "max_schema_depth": 5,
            },
        }
    )
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    # Snapshot should include policy and schema
    resp = client.get("/policy")
    assert resp.status_code == 200
    snap = resp.json()
    assert "policy" in snap and "schema" in snap
    assert "max_schema_depth" in snap["schema"]

    # Redaction utility should redact sensitive-looking keys
    sample = {"api_key": "secret", "password": "p", "token": "t", "normal": 123}
    red = redact_policy_config_dict(sample)
    assert red["api_key"] == "***REDACTED***"
    assert red["password"] == "***REDACTED***"
    assert red["token"] == "***REDACTED***"
    assert red["normal"] == 123


@pytest.mark.redis
@pytest.mark.asyncio
async def test_manual_reload_and_status(redis_client, monkeypatch):
    # Create a temp policy file
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "allow_network_tools": False,
                "allow_filesystem_tools": False,
                "callable_allowlist": [],
                "default_timeout_ms": 111,
            },
            f,
        )
    monkeypatch.setenv("TTA_TOOL_POLICY_CONFIG", path)

    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8621,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.diagnostics.admin_api_key": "adminkey",
            "agent_orchestration.tools": {"redis_key_prefix": "ao"},
        }
    )
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    # Status should reflect file source
    st = client.get("/policy/status").json()
    assert st.get("source") == path

    # Change file and trigger manual reload
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "allow_network_tools": True,
                "allow_filesystem_tools": True,
                "callable_allowlist": ["x.y.z"],
                "default_timeout_ms": 222,
            },
            f,
        )
    os.utime(path, None)

    r = client.post("/policy/reload", headers={"X-AO-DIAG-KEY": "adminkey"}).json()
    assert r.get("ok") is True

    snap = client.get("/policy").json()
    pol = snap.get("policy", {})
    # Verify the updated fields took effect
    assert pol.get("allow_network_tools") is True
    assert pol.get("default_timeout_ms") == 222


@pytest.mark.redis
@pytest.mark.asyncio
async def test_live_reload_applies_and_rollback(redis_client, monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "allow_network_tools": False,
                "allow_filesystem_tools": False,
                "callable_allowlist": [],
            },
            f,
        )
    monkeypatch.setenv("TTA_TOOL_POLICY_CONFIG", path)

    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8622,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.diagnostics.policy_live_reload_enabled": True,
            "agent_orchestration.diagnostics.policy_live_reload_interval_s": 0.2,
            "agent_orchestration.tools": {"redis_key_prefix": "ao"},
        }
    )
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    # Update to a valid config and wait for watcher
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "allow_network_tools": True,
                "allow_filesystem_tools": False,
                "callable_allowlist": [],
            },
            f,
        )
    os.utime(path, None)
    time.sleep(0.6)  # allow 3x interval

    snap = client.get("/policy").json()
    assert snap["policy"].get("allow_network_tools") is True

    # Now write an invalid config (bad type) and ensure rollback (no change to True)
    with open(path, "w", encoding="utf-8") as f:
        f.write('{"allow_network_tools": "notabool"}')
    os.utime(path, None)
    time.sleep(0.6)

    snap2 = client.get("/policy").json()
    # still True (unchanged)
    assert snap2["policy"].get("allow_network_tools") is True
    # audit should include an error entry
    audit = snap2.get("reload_audit", [])
    assert any((not e.get("ok") and e.get("source") == path) for e in audit)
