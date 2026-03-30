# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_workflow_monitor_and_metrics]]
import os

import pytest

from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_workflow_monitor_metrics_and_diagnostics(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8625,
            "agent_orchestration.diagnostics.enabled": True,
            # Enable error handling/monitoring
            "agent_orchestration.error_handling.enabled": True,
            "agent_orchestration.workflow": {
                "timeouts": {"total_seconds": 0.5, "per_step_seconds": 0.2},
                "audit_retention_days": 1,
                "timeout_check_interval_s": 0.05,
                "state_validation_interval_s": 0.05,
            },
            "agent_orchestration.tools": {"redis_key_prefix": "ao"},
        }
    )
    assert comp._start_impl() is True
    app = comp._create_diagnostics_app()
    from starlette.testclient import TestClient

    client = TestClient(app)

    # Simulate a run by interacting with the monitor directly
    from tta_ai.orchestration.workflow_monitor import WorkflowMonitor

    mon = getattr(comp, "_workflow_monitor", None)
    assert isinstance(mon, WorkflowMonitor)

    run_id = "testrun1"
    await mon.start_run(run_id, workflow="w1", total_timeout_s=0.3, step_timeout_s=0.1)
    await mon.start_step(run_id, "stepA")

    # Give time to trigger early warning and timeout
    await asyncio_sleep(0.45)
    # One more scan just in case
    await mon.check_timeouts_once()

    # Metrics endpoint should include workflow section
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert "workflow" in body
    wf = body["workflow"]
    # workflow_failures_total should be >=1 due to timeout
    assert int(wf.get("workflow_failures_total", 0)) >= 1


async def asyncio_sleep(t):
    import asyncio

    await asyncio.sleep(t)
