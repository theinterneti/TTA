# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_tools_summary_and_prometheus]]
import os

import pytest
from tta_ai.orchestration.tools.metrics import get_tool_metrics

from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_tools_summary_and_prom_export(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8611,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.tools": {
                "redis_key_prefix": "ao",
                "cache_ttl_s": 0.5,
                "cache_max_items": 32,
                "max_prometheus_tools": 5,
            },
        }
    )
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    from starlette.testclient import TestClient

    client = TestClient(app)

    # seed tool metrics without invoking real tools
    tm = get_tool_metrics()
    tm.record_success("kg.query", "1.0.0", 12.0)
    tm.record_failure("kg.query", "1.0.0", 30.0)
    tm.record_success("fs.read", "1.0.0", 5.0)

    # summary endpoint
    res = client.get(
        "/tools/summary?limit=10&status=&name_prefix=&sort_by=last_used_at&order=desc"
    )
    assert res.status_code == 200
    js = res.json()
    assert "items" in js and isinstance(js["items"], list)
    assert "counts" in js and "active" in js["counts"]

    # prometheus endpoint should include our tool counters/histograms
    resp = client.get("/metrics-prom")
    assert resp.status_code == 200
    body = resp.text
    assert "agent_orchestration_tool_invocations_total" in body
    assert "agent_orchestration_tool_success_total" in body
    assert "agent_orchestration_tool_failure_total" in body
    assert "agent_orchestration_tool_duration_seconds_bucket" in body

    assert comp._stop_impl() is True
