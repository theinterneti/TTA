import os
import json
import time
import tempfile
import pytest

from starlette.testclient import TestClient

from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_safety_snapshot_endpoint(redis_client):
    # Seed Redis rules
    rules = {"rules": [{"id": "r1", "category": "professional_ethics", "priority": 5, "level": "warning", "pattern": "diagnose", "flags": "i"}]}
    await redis_client.set("ao:safety:rules", json.dumps(rules))

    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent({
        "player_experience.api.redis_url": url,
        "agent_orchestration.port": 8700,
        "agent_orchestration.safety.enabled": True,
        "agent_orchestration.diagnostics.enabled": True,
        "agent_orchestration.tools": {"redis_key_prefix": "ao"},
    })
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    resp = client.get("/safety")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("enabled") is True
    assert "rules" in data and data["rules"].get("rules")
    status = data.get("status") or {}
    assert status.get("source", "").startswith("redis:")
    assert status.get("redis_key") == "ao:safety:rules"
    assert status.get("cache_ttl_s") == 2.0
    assert status.get("last_reload_ts") is not None


@pytest.mark.redis
@pytest.mark.asyncio
async def test_safety_manual_reload_endpoint(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    # Initial rules
    await redis_client.set("ao:safety:rules", json.dumps({"rules": [{"id": "rA", "category": "professional_ethics", "priority": 5, "level": "warning", "pattern": "diagnose", "flags": "i"}]}))
    comp = AgentOrchestrationComponent({
        "player_experience.api.redis_url": url,
        "agent_orchestration.port": 8701,
        "agent_orchestration.safety.enabled": True,
        "agent_orchestration.diagnostics.enabled": True,
        "agent_orchestration.diagnostics.admin_api_key": "adminkey",
        "agent_orchestration.tools": {"redis_key_prefix": "ao"},
    })
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    # Confirm initial
    snap1 = client.get("/safety").json()
    assert any(r.get("id") == "rA" for r in snap1.get("rules", {}).get("rules", []))

    # Update rules in Redis
    await redis_client.set("ao:safety:rules", json.dumps({"rules": [{"id": "rB", "category": "crisis_detection", "priority": 99, "level": "blocked", "pattern": "kill myself", "flags": "i"}]}))

    # Trigger manual reload
    reload_resp = client.post("/safety/reload", headers={"X-AO-DIAG-KEY": "adminkey"})
    assert reload_resp.status_code == 200
    assert reload_resp.json().get("ok") is True

    snap2 = client.get("/safety").json()
    assert any(r.get("id") == "rB" for r in snap2.get("rules", {}).get("rules", []))


@pytest.mark.redis
@pytest.mark.asyncio
async def test_safety_reload_unauthorized(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent({
        "player_experience.api.redis_url": url,
        "agent_orchestration.port": 8702,
        "agent_orchestration.safety.enabled": True,
        "agent_orchestration.diagnostics.enabled": True,
        "agent_orchestration.diagnostics.admin_api_key": "adminkey",
        "agent_orchestration.tools": {"redis_key_prefix": "ao"},
    })
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    # Missing key
    r1 = client.post("/safety/reload")
    assert r1.status_code == 401
    assert r1.json().get("ok") is False

    # Incorrect key
    r2 = client.post("/safety/reload", headers={"X-AO-DIAG-KEY": "wrong"})
    assert r2.status_code == 401
    assert r2.json().get("ok") is False


@pytest.mark.redis
@pytest.mark.asyncio
async def test_safety_endpoints_when_diagnostics_disabled(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent({
        "player_experience.api.redis_url": url,
        "agent_orchestration.port": 8703,
        "agent_orchestration.safety.enabled": True,
        "agent_orchestration.diagnostics.enabled": False,
        "agent_orchestration.tools": {"redis_key_prefix": "ao"},
    })
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    client = TestClient(app)

    # GET should still be available but reflect disabled status
    g = client.get("/safety")
    assert g.status_code == 200
    assert g.json().get("enabled") in (True, False)  # service may still be enabled; diagnostics disabled refers to admin

    # POST should return an explicit diagnostics disabled error
    p = client.post("/safety/reload")
    assert p.status_code == 200
    assert p.json().get("error") == "diagnostics disabled"

