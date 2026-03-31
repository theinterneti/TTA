"""Unit tests targeting src/agent_orchestration/workflow_monitor.py directly.

The existing test_workflow_monitor_and_metrics.py is marked @pytest.mark.redis
and hits a real Redis instance, leaving 0% coverage for the unit gate.
This file uses mock Redis so it runs without an actual Redis connection.
"""

from __future__ import annotations

import json
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agent_orchestration.workflow_monitor import RunRecord, RunStep, WorkflowMonitor

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_redis() -> MagicMock:
    redis = MagicMock()
    redis.set = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.rpush = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    redis.hincrby = AsyncMock(return_value=1)
    redis.hgetall = AsyncMock(return_value={})
    redis.lrange = AsyncMock(return_value=[])
    return redis


def _monitor(redis=None) -> WorkflowMonitor:
    return WorkflowMonitor(redis or _mock_redis(), key_prefix="test")


def _run_record(run_id: str = "r1", status: str = "running") -> RunRecord:
    return RunRecord(
        run_id=run_id, workflow="wf", status=status, started_at=time.time()
    )


# ---------------------------------------------------------------------------
# Key helpers
# ---------------------------------------------------------------------------


def test_run_key_format():
    m = _monitor()
    assert m._run_key("abc") == "test:wf:runs:abc"


def test_audit_key_format():
    m = _monitor()
    assert m._audit_key("abc") == "test:wf:rollback:audit:abc"


def test_metrics_key_format():
    m = _monitor()
    assert m._metrics_key() == "test:wf:metrics"


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------


def test_dump_and_from_dump_round_trip():
    m = _monitor()
    rr = _run_record()
    rr.steps.append(RunStep(name="step1", started_at=time.time()))
    dumped = m._dump(rr)
    restored = m._from_dump(dumped)
    assert restored.run_id == rr.run_id
    assert restored.workflow == rr.workflow
    assert restored.status == rr.status
    assert len(restored.steps) == 1
    assert restored.steps[0].name == "step1"


def test_from_dump_handles_missing_fields():
    m = _monitor()
    minimal = {"run_id": "x"}
    rr = m._from_dump(minimal)
    assert rr.run_id == "x"
    assert rr.status == "running"
    assert rr.steps == []


def test_dump_includes_step_warned_flag():
    m = _monitor()
    rr = _run_record()
    step = RunStep(name="s", started_at=time.time(), warned=True)
    rr.steps.append(step)
    dumped = m._dump(rr)
    assert dumped["steps"][0]["warned"] is True


# ---------------------------------------------------------------------------
# start_run
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_start_run_calls_redis_set():
    redis = _mock_redis()
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.start_run("r1", workflow="my-wf")
    redis.set.assert_called_once()
    key, payload = redis.set.call_args.args
    assert key == "test:wf:runs:r1"
    data = json.loads(payload)
    assert data["workflow"] == "my-wf"
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_start_run_with_custom_timeouts():
    redis = _mock_redis()
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.start_run("r2", total_timeout_s=120.0, step_timeout_s=30.0)
    key, payload = redis.set.call_args.args
    data = json.loads(payload)
    assert data["total_timeout_s"] == 120.0
    assert data["step_timeout_s"] == 30.0


# ---------------------------------------------------------------------------
# start_step / end_step
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_start_step_appends_step():
    rr = _run_record()
    redis = _mock_redis()
    redis.get = AsyncMock(return_value=json.dumps(_WorkflowMonitor_dump(rr)))
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.start_step("r1", "step_a")
    _, payload = redis.set.call_args.args
    data = json.loads(payload)
    assert len(data["steps"]) == 1
    assert data["steps"][0]["name"] == "step_a"


@pytest.mark.asyncio
async def test_end_step_sets_ended_at():
    rr = _run_record()
    rr.steps.append(RunStep(name="s1", started_at=time.time()))
    redis = _mock_redis()
    redis.get = AsyncMock(return_value=json.dumps(_WorkflowMonitor_dump(rr)))
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.end_step("r1")
    _, payload = redis.set.call_args.args
    data = json.loads(payload)
    assert data["steps"][0]["ended_at"] is not None


@pytest.mark.asyncio
async def test_end_step_with_error_sets_failed_status():
    rr = _run_record()
    rr.steps.append(RunStep(name="s1", started_at=time.time()))
    redis = _mock_redis()
    redis.get = AsyncMock(return_value=json.dumps(_WorkflowMonitor_dump(rr)))
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.end_step("r1", error="boom")
    _, payload = redis.set.call_args.args
    data = json.loads(payload)
    assert data["status"] == "failed"


@pytest.mark.asyncio
async def test_start_step_noop_on_missing_run():
    redis = _mock_redis()
    redis.get = AsyncMock(return_value=None)
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.start_step("missing", "step_a")  # must not raise
    redis.set.assert_not_called()


# ---------------------------------------------------------------------------
# complete_run / fail_run
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_complete_run_sets_completed_status():
    rr = _run_record()
    redis = _mock_redis()
    redis.get = AsyncMock(return_value=json.dumps(_WorkflowMonitor_dump(rr)))
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.complete_run("r1")
    _, payload = redis.set.call_args.args
    data = json.loads(payload)
    assert data["status"] == "completed"
    assert data["ended_at"] is not None


@pytest.mark.asyncio
async def test_fail_run_sets_failed_status():
    rr = _run_record()
    redis = _mock_redis()
    redis.get = AsyncMock(return_value=json.dumps(_WorkflowMonitor_dump(rr)))
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.fail_run("r1", "test failure")
    _, payload = redis.set.call_args.args
    data = json.loads(payload)
    assert data["status"] == "failed"


@pytest.mark.asyncio
async def test_fail_run_closes_open_step():
    rr = _run_record()
    rr.steps.append(RunStep(name="s", started_at=time.time()))  # step still open
    redis = _mock_redis()
    redis.get = AsyncMock(return_value=json.dumps(_WorkflowMonitor_dump(rr)))
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.fail_run("r1", "forced failure")
    _, payload = redis.set.call_args.args
    data = json.loads(payload)
    assert data["steps"][0]["error"] == "forced failure"


# ---------------------------------------------------------------------------
# get_run
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_run_returns_none_on_miss():
    redis = _mock_redis()
    redis.get = AsyncMock(return_value=None)
    m = WorkflowMonitor(redis, key_prefix="test")
    assert await m.get_run("missing") is None


@pytest.mark.asyncio
async def test_get_run_returns_dict():
    rr = _run_record()
    redis = _mock_redis()
    redis.get = AsyncMock(return_value=json.dumps(_WorkflowMonitor_dump(rr)))
    m = WorkflowMonitor(redis, key_prefix="test")
    result = await m.get_run("r1")
    assert isinstance(result, dict)
    assert result["run_id"] == "r1"


# ---------------------------------------------------------------------------
# Rollback audit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_record_rollback_audit_calls_rpush():
    redis = _mock_redis()
    m = WorkflowMonitor(redis, key_prefix="test")
    await m.record_rollback_audit("r1", {"event": "rollback"})
    redis.rpush.assert_called_once()
    redis.expire.assert_called_once()


@pytest.mark.asyncio
async def test_get_rollback_history_empty_returns_empty_list():
    redis = _mock_redis()
    redis.lrange = AsyncMock(return_value=[])
    m = WorkflowMonitor(redis, key_prefix="test")
    result = await m.get_rollback_history("r1")
    assert result == []


@pytest.mark.asyncio
async def test_get_rollback_history_deserialises_entries():
    entry = {"event": "rollback", "ts": 12345}
    redis = _mock_redis()
    redis.lrange = AsyncMock(return_value=[json.dumps(entry)])
    m = WorkflowMonitor(redis, key_prefix="test")
    result = await m.get_rollback_history("r1")
    assert result == [entry]


@pytest.mark.asyncio
async def test_get_rollback_history_handles_redis_error():
    redis = _mock_redis()
    redis.lrange = AsyncMock(side_effect=RuntimeError("redis down"))
    m = WorkflowMonitor(redis, key_prefix="test")
    result = await m.get_rollback_history("r1")
    assert result == []


# ---------------------------------------------------------------------------
# metrics_snapshot
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_metrics_snapshot_returns_empty_on_error():
    redis = _mock_redis()
    redis.hgetall = AsyncMock(side_effect=RuntimeError("redis down"))
    m = WorkflowMonitor(redis, key_prefix="test")
    assert await m.metrics_snapshot() == {}


@pytest.mark.asyncio
async def test_metrics_snapshot_converts_values_to_int():
    redis = _mock_redis()
    redis.hgetall = AsyncMock(return_value={b"workflow_failures_total": b"5"})
    m = WorkflowMonitor(redis, key_prefix="test")
    snapshot = await m.metrics_snapshot()
    assert snapshot["workflow_failures_total"] == 5


# ---------------------------------------------------------------------------
# check_timeouts_once
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_timeouts_once_skips_non_running_runs():
    rr = _run_record(status="completed")
    redis = _mock_redis()

    async def _scan(*args, **kwargs):
        yield b"test:wf:runs:r1"

    redis.scan_iter = _scan
    redis.get = AsyncMock(return_value=json.dumps(_WorkflowMonitor_dump(rr)))
    m = WorkflowMonitor(redis, key_prefix="test")
    transitioned = await m.check_timeouts_once()
    assert transitioned == 0


@pytest.mark.asyncio
async def test_check_timeouts_once_transitions_timed_out_run():
    rr = _run_record(status="running")
    # Set started_at far in the past so total timeout fires
    rr.started_at = time.time() - 10000
    rr.total_timeout_s = 1.0

    redis = _mock_redis()

    async def _scan(*args, **kwargs):
        yield b"test:wf:runs:r1"

    redis.scan_iter = _scan
    redis.get = AsyncMock(return_value=json.dumps(_WorkflowMonitor_dump(rr)))
    m = WorkflowMonitor(redis, key_prefix="test")
    transitioned = await m.check_timeouts_once()
    assert transitioned == 1


@pytest.mark.asyncio
async def test_check_timeouts_once_handles_parse_error_gracefully():
    redis = _mock_redis()

    async def _scan(*args, **kwargs):
        yield b"test:wf:runs:bad"

    redis.scan_iter = _scan
    redis.get = AsyncMock(return_value=b"not valid json{{{")
    m = WorkflowMonitor(redis, key_prefix="test")
    transitioned = await m.check_timeouts_once()
    assert transitioned == 0


# ---------------------------------------------------------------------------
# start/stop background checks
# ---------------------------------------------------------------------------


def test_stop_background_checks_no_task_does_not_raise():
    m = _monitor()
    m.stop_background_checks()  # must not raise


# ---------------------------------------------------------------------------
# Helpers for tests above
# ---------------------------------------------------------------------------


def _WorkflowMonitor_dump(rr: RunRecord) -> dict:
    """Helper that uses WorkflowMonitor._dump without instantiating with redis."""
    m = WorkflowMonitor.__new__(WorkflowMonitor)
    m._pfx = "test"
    m._def_total = 300.0
    m._def_step = 60.0
    return m._dump(rr)
