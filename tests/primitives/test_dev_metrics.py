"""
Tests for Development Metrics Framework

Tests cover:
- Execution tracking start/end
- Metrics persistence to JSONL files
- Metrics summary generation
- track_execution decorator
- Dashboard generation (basic validation)
"""

import json

# Import from scripts/observability/
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "scripts" / "observability")
)

from dev_metrics import (
    DevMetricsCollector,
    ExecutionMetric,
    track_execution,
)


class TestExecutionMetric:
    """Test ExecutionMetric dataclass."""

    def test_create_metric(self):
        """Test creating an execution metric."""
        started_at = datetime.utcnow()
        metric = ExecutionMetric(
            name="test_operation", started_at=started_at, metadata={"key": "value"}
        )

        assert metric.name == "test_operation"
        assert metric.started_at == started_at
        assert metric.status == "running"
        assert metric.metadata == {"key": "value"}

    def test_metric_to_dict(self):
        """Test converting metric to dictionary."""
        started_at = datetime.utcnow()
        ended_at = started_at + timedelta(seconds=1)

        metric = ExecutionMetric(
            name="test_operation",
            started_at=started_at,
            ended_at=ended_at,
            duration_ms=1000.0,
            status="success",
            metadata={"key": "value"},
        )

        data = metric.to_dict()

        assert data["name"] == "test_operation"
        assert data["status"] == "success"
        assert data["duration_ms"] == 1000.0
        assert data["metadata"] == {"key": "value"}


class TestDevMetricsCollector:
    """Test DevMetricsCollector class."""

    def test_create_collector(self):
        """Test creating a metrics collector."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            assert collector.metrics_dir == Path(tmpdir)
            assert len(collector.current_metrics) == 0

    def test_start_execution(self):
        """Test starting execution tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            exec_id = collector.start_execution(
                "test_operation", metadata={"key": "value"}
            )

            assert exec_id in collector.current_metrics
            metric = collector.current_metrics[exec_id]
            assert metric.name == "test_operation"
            assert metric.status == "running"
            assert metric.metadata == {"key": "value"}

    def test_end_execution_success(self):
        """Test ending execution tracking with success."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            exec_id = collector.start_execution("test_operation")
            time.sleep(0.01)  # Small delay to ensure duration > 0
            collector.end_execution(exec_id, status="success")

            # Metric should be removed from current_metrics
            assert exec_id not in collector.current_metrics

            # Metric should be saved to file
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            metrics_file = Path(tmpdir) / f"{date_str}.jsonl"
            assert metrics_file.exists()

            # Verify metric content
            with open(metrics_file) as f:
                line = f.readline()
                data = json.loads(line)

            assert data["name"] == "test_operation"
            assert data["status"] == "success"
            assert data["duration_ms"] > 0

    def test_end_execution_failure(self):
        """Test ending execution tracking with failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            exec_id = collector.start_execution("test_operation")
            collector.end_execution(exec_id, status="failed", error="Test error")

            # Verify metric content
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            metrics_file = Path(tmpdir) / f"{date_str}.jsonl"

            with open(metrics_file) as f:
                line = f.readline()
                data = json.loads(line)

            assert data["status"] == "failed"
            assert data["error"] == "Test error"

    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            # Add some metrics
            for i in range(5):
                exec_id = collector.start_execution("test_operation")
                time.sleep(0.01)
                status = "success" if i < 4 else "failed"
                collector.end_execution(exec_id, status=status)

            summary = collector.get_metrics_summary(days=1)

            assert "test_operation" in summary
            metrics = summary["test_operation"]
            assert metrics["total_executions"] == 5
            assert metrics["successes"] == 4
            assert metrics["failures"] == 1
            assert metrics["success_rate"] == 0.8
            assert metrics["avg_duration_ms"] > 0

    def test_get_recent_metrics(self):
        """Test getting recent metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            # Add some metrics
            for i in range(3):
                exec_id = collector.start_execution(f"operation_{i}")
                collector.end_execution(exec_id, status="success")

            recent = collector.get_recent_metrics(limit=2)

            assert len(recent) == 2
            # Should be in reverse chronological order
            assert recent[0]["name"] == "operation_2"
            assert recent[1]["name"] == "operation_1"

    def test_get_recent_metrics_filtered(self):
        """Test getting recent metrics filtered by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            # Add metrics with different names
            exec_id1 = collector.start_execution("operation_a")
            collector.end_execution(exec_id1, status="success")

            exec_id2 = collector.start_execution("operation_b")
            collector.end_execution(exec_id2, status="success")

            exec_id3 = collector.start_execution("operation_a")
            collector.end_execution(exec_id3, status="success")

            recent = collector.get_recent_metrics(name="operation_a", limit=10)

            assert len(recent) == 2
            assert all(m["name"] == "operation_a" for m in recent)

    def test_clear_old_metrics(self):
        """Test clearing old metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            # Create old metrics file
            old_date = datetime.utcnow() - timedelta(days=40)
            old_file = Path(tmpdir) / f"{old_date.strftime('%Y-%m-%d')}.jsonl"
            old_file.write_text('{"name": "old_metric"}\n')

            # Create recent metrics file
            recent_date = datetime.utcnow()
            recent_file = Path(tmpdir) / f"{recent_date.strftime('%Y-%m-%d')}.jsonl"
            recent_file.write_text('{"name": "recent_metric"}\n')

            # Clear old metrics (keep last 30 days)
            deleted = collector.clear_old_metrics(days_to_keep=30)

            assert deleted == 1
            assert not old_file.exists()
            assert recent_file.exists()


class TestTrackExecutionDecorator:
    """Test track_execution decorator."""

    def test_track_execution_success(self):
        """Test tracking successful execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            # Replace global collector
            import dev_metrics

            original_collector = dev_metrics._collector
            dev_metrics._collector = collector

            try:

                @track_execution("test_operation", metadata={"type": "test"})
                def successful_function():
                    return "success"

                result = successful_function()

                assert result == "success"

                # Verify metric was saved
                summary = collector.get_metrics_summary(days=1)
                assert "test_operation" in summary
                assert summary["test_operation"]["successes"] == 1
            finally:
                dev_metrics._collector = original_collector

    def test_track_execution_failure(self):
        """Test tracking failed execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            # Replace global collector
            import dev_metrics

            original_collector = dev_metrics._collector
            dev_metrics._collector = collector

            try:

                @track_execution("test_operation")
                def failing_function():
                    raise ValueError("Test error")

                with pytest.raises(ValueError):
                    failing_function()

                # Verify metric was saved with failure
                summary = collector.get_metrics_summary(days=1)
                assert "test_operation" in summary
                assert summary["test_operation"]["failures"] == 1
            finally:
                dev_metrics._collector = original_collector

    def test_track_execution_with_metadata(self):
        """Test tracking execution with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            # Replace global collector
            import dev_metrics

            original_collector = dev_metrics._collector
            dev_metrics._collector = collector

            try:

                @track_execution("test_operation", metadata={"key": "value"})
                def function_with_metadata():
                    return "success"

                function_with_metadata()

                # Verify metadata was saved
                recent = collector.get_recent_metrics(name="test_operation", limit=1)
                assert len(recent) == 1
                assert recent[0]["metadata"] == {"key": "value"}
            finally:
                dev_metrics._collector = original_collector


class TestDashboardGeneration:
    """Test dashboard generation (basic validation)."""

    def test_generate_dashboard_with_metrics(self):
        """Test generating dashboard with metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = DevMetricsCollector(metrics_dir=tmpdir)

            # Add some metrics
            exec_id = collector.start_execution("test_operation")
            collector.end_execution(exec_id, status="success")

            # Generate dashboard
            from dashboard import generate_dashboard

            output_file = Path(tmpdir) / "dashboard.html"
            generate_dashboard(output_file=str(output_file), days=1, metrics_dir=tmpdir)

            # Verify dashboard file exists
            assert output_file.exists()

            # Verify dashboard contains expected content
            content = output_file.read_text()
            assert "TTA Development Metrics Dashboard" in content
            assert "test_operation" in content

    def test_generate_empty_dashboard(self):
        """Test generating dashboard with no metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from dashboard import generate_dashboard

            output_file = Path(tmpdir) / "dashboard.html"
            generate_dashboard(output_file=str(output_file), days=1, metrics_dir=tmpdir)

            # Verify dashboard file exists
            assert output_file.exists()

            # Verify dashboard indicates no metrics
            content = output_file.read_text()
            assert (
                "No metrics" in content
                or "TTA Development Metrics Dashboard" in content
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
