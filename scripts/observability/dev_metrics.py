"""
Development Metrics Collection Framework

Tracks execution metrics for development operations (tests, builds, quality checks)
with automatic persistence and summary generation.

Usage:
    from observability.dev_metrics import track_execution, DevMetricsCollector

    @track_execution("pytest_unit_tests", metadata={"suite": "unit"})
    def run_unit_tests():
        # Your test execution code
        pass
"""

import functools
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec('P')
T = TypeVar('T')


@dataclass
class ExecutionMetric:
    """Metric for a single execution."""
    name: str
    started_at: datetime
    ended_at: datetime | None = None
    duration_ms: float | None = None
    status: str = "running"  # running, success, failed
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with ISO format timestamps."""
        return {
            "name": self.name,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "metadata": self.metadata,
            "error": self.error
        }


class DevMetricsCollector:
    """Collects development metrics."""

    def __init__(self, metrics_dir: str = ".metrics"):
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)
        self.current_metrics: dict[str, ExecutionMetric] = {}

    def start_execution(self, name: str, metadata: dict | None = None) -> str:
        """Start tracking an execution."""
        import uuid

        exec_id = str(uuid.uuid4())
        metric = ExecutionMetric(
            name=name,
            started_at=datetime.utcnow(),
            metadata=metadata or {}
        )

        self.current_metrics[exec_id] = metric
        logger.info(f"Started tracking: {name} (id={exec_id})")
        return exec_id

    def end_execution(
        self,
        exec_id: str,
        status: str = "success",
        error: str | None = None
    ) -> None:
        """End tracking an execution."""
        metric = self.current_metrics.get(exec_id)
        if not metric:
            logger.warning(f"No metric found for execution id: {exec_id}")
            return

        metric.ended_at = datetime.utcnow()
        metric.duration_ms = (
            (metric.ended_at - metric.started_at).total_seconds() * 1000
        )
        metric.status = status
        metric.error = error

        logger.info(
            f"Completed tracking: {metric.name} "
            f"(status={status}, duration={metric.duration_ms:.0f}ms)"
        )

        # Save metric
        self._save_metric(metric)

        # Remove from current
        del self.current_metrics[exec_id]

    def _save_metric(self, metric: ExecutionMetric) -> None:
        """Save metric to file."""
        date_str = metric.started_at.strftime("%Y-%m-%d")
        metrics_file = self.metrics_dir / f"{date_str}.jsonl"

        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metric.to_dict()) + '\n')

    def get_metrics_summary(self, days: int = 7) -> dict[str, Any]:
        """Get summary of metrics for the last N days."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        metrics = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            metrics_file = self.metrics_dir / f"{date_str}.jsonl"

            if metrics_file.exists():
                with open(metrics_file) as f:
                    for line in f:
                        try:
                            metrics.append(json.loads(line))
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse metric line: {line}")

            current_date += timedelta(days=1)

        # Aggregate metrics
        by_name = {}
        for m in metrics:
            name = m["name"]
            if name not in by_name:
                by_name[name] = []
            by_name[name].append(m)

        summary = {}
        for name, name_metrics in by_name.items():
            durations = [m["duration_ms"] for m in name_metrics if m.get("duration_ms")]
            successes = sum(1 for m in name_metrics if m["status"] == "success")
            failures = sum(1 for m in name_metrics if m["status"] == "failed")

            summary[name] = {
                "total_executions": len(name_metrics),
                "successes": successes,
                "failures": failures,
                "success_rate": successes / len(name_metrics) if name_metrics else 0,
                "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
            }

        return summary

    def get_recent_metrics(self, name: str | None = None, limit: int = 10) -> list[dict]:
        """Get recent metrics, optionally filtered by name."""
        all_metrics = []

        # Read last 7 days of metrics
        for days_ago in range(7):
            date = datetime.utcnow() - timedelta(days=days_ago)
            date_str = date.strftime("%Y-%m-%d")
            metrics_file = self.metrics_dir / f"{date_str}.jsonl"

            if metrics_file.exists():
                with open(metrics_file) as f:
                    for line in f:
                        try:
                            metric = json.loads(line)
                            if name is None or metric["name"] == name:
                                all_metrics.append(metric)
                        except json.JSONDecodeError:
                            continue

        # Sort by started_at descending
        all_metrics.sort(key=lambda m: m["started_at"], reverse=True)

        return all_metrics[:limit]

    def clear_old_metrics(self, days_to_keep: int = 30) -> int:
        """Clear metrics older than specified days. Returns number of files deleted."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        deleted = 0

        for metrics_file in self.metrics_dir.glob("*.jsonl"):
            try:
                # Parse date from filename (YYYY-MM-DD.jsonl)
                date_str = metrics_file.stem
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff_date:
                    metrics_file.unlink()
                    deleted += 1
                    logger.info(f"Deleted old metrics file: {metrics_file}")
            except (ValueError, OSError) as e:
                logger.warning(f"Failed to process metrics file {metrics_file}: {e}")

        return deleted


# Global collector instance
_collector = DevMetricsCollector()


def track_execution(name: str, metadata: dict | None = None):
    """
    Decorator to track function execution with metrics.

    Usage:
        @track_execution("pytest_unit_tests", metadata={"suite": "unit"})
        def run_unit_tests():
            # Your code here
            pass

    Args:
        name: Name of the operation being tracked
        metadata: Optional metadata to attach to the metric
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            exec_id = _collector.start_execution(name, metadata)
            try:
                result = func(*args, **kwargs)
                _collector.end_execution(exec_id, status="success")
                return result
            except Exception as e:
                _collector.end_execution(exec_id, status="failed", error=str(e))
                raise
        return wrapper
    return decorator


def get_collector() -> DevMetricsCollector:
    """Get the global metrics collector instance."""
    return _collector


if __name__ == "__main__":
    # Example usage
    @track_execution("example_operation", metadata={"type": "demo"})
    def example_operation():
        """Example operation for testing."""
        import time
        time.sleep(0.1)
        return "success"

    # Run example
    print("Running example operation...")
    result = example_operation()
    print(f"Result: {result}")

    # Get summary
    summary = _collector.get_metrics_summary(days=1)
    print("\nMetrics Summary:")
    for name, metrics in summary.items():
        print(f"\n{name}:")
        print(f"  Executions: {metrics['total_executions']}")
        print(f"  Success Rate: {metrics['success_rate']:.1%}")
        print(f"  Avg Duration: {metrics['avg_duration_ms']:.0f}ms")
