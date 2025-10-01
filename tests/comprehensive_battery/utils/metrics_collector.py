"""
Test Metrics Collector

Collects and analyzes metrics during comprehensive testing including:
- Performance metrics (response times, throughput)
- Resource usage metrics (CPU, memory, disk)
- Error rates and failure patterns
- System stability indicators
- Test execution statistics
"""

import asyncio
import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric."""

    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemSnapshot:
    """System resource snapshot."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_connections: int
    active_processes: int
    load_average: list[float] = field(default_factory=list)


class TestMetricsCollector:
    """
    Collects and analyzes metrics during comprehensive testing.

    Provides real-time monitoring of system performance, resource usage,
    and test execution statistics for comprehensive analysis.
    """

    def __init__(self):
        self.metrics: list[PerformanceMetric] = []
        self.system_snapshots: list[SystemSnapshot] = []
        self.error_counts: dict[str, int] = defaultdict(int)
        self.test_timings: dict[str, list[float]] = defaultdict(list)

        self.collection_start_time: datetime | None = None
        self.collection_end_time: datetime | None = None
        self.is_collecting = False

        # Monitoring task
        self.monitoring_task: asyncio.Task | None = None

    async def start_collection(self, collection_interval: float = 1.0):
        """Start metrics collection."""
        if self.is_collecting:
            return

        self.collection_start_time = datetime.utcnow()
        self.is_collecting = True

        # Start background monitoring
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(collection_interval)
        )

        logger.info("Test metrics collection started")

    async def stop_collection(self):
        """Stop metrics collection."""
        if not self.is_collecting:
            return

        self.is_collecting = False
        self.collection_end_time = datetime.utcnow()

        # Stop monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Test metrics collection stopped")

    def record_performance_metric(
        self,
        name: str,
        value: float,
        unit: str = "ms",
        category: str = "performance",
        metadata: dict[str, Any] | None = None,
    ):
        """Record a performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow(),
            category=category,
            metadata=metadata or {},
        )
        self.metrics.append(metric)

    def record_test_timing(self, test_name: str, duration_seconds: float):
        """Record test execution timing."""
        self.test_timings[test_name].append(duration_seconds)
        self.record_performance_metric(
            name=f"test_duration_{test_name}",
            value=duration_seconds * 1000,  # Convert to milliseconds
            unit="ms",
            category="test_timing",
        )

    def record_error(self, error_type: str, error_message: str = ""):
        """Record an error occurrence."""
        self.error_counts[error_type] += 1
        self.record_performance_metric(
            name=f"error_{error_type}",
            value=1,
            unit="count",
            category="error",
            metadata={"error_message": error_message},
        )

    async def capture_system_snapshot(self) -> SystemSnapshot:
        """Capture current system resource snapshot."""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Get disk usage
            disk = psutil.disk_usage("/")
            disk_usage_percent = (disk.used / disk.total) * 100

            # Get network connections
            network_connections = len(psutil.net_connections())

            # Get process count
            active_processes = len(psutil.pids())

            # Get load average (Unix systems)
            load_average = []
            try:
                load_average = list(psutil.getloadavg())
            except AttributeError:
                # Windows doesn't have load average
                pass

            snapshot = SystemSnapshot(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                network_connections=network_connections,
                active_processes=active_processes,
                load_average=load_average,
            )

            self.system_snapshots.append(snapshot)
            return snapshot

        except Exception as e:
            logger.error(f"Failed to capture system snapshot: {e}")
            return SystemSnapshot(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_connections=0,
                active_processes=0,
            )

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance metrics summary."""
        if not self.metrics:
            return {"error": "No metrics collected"}

        # Group metrics by category
        metrics_by_category = defaultdict(list)
        for metric in self.metrics:
            metrics_by_category[metric.category].append(metric)

        summary = {}

        for category, category_metrics in metrics_by_category.items():
            values = [m.value for m in category_metrics]

            if values:
                summary[category] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
                }

        return summary

    def get_system_resource_summary(self) -> dict[str, Any]:
        """Get system resource usage summary."""
        if not self.system_snapshots:
            return {"error": "No system snapshots collected"}

        cpu_values = [s.cpu_percent for s in self.system_snapshots]
        memory_values = [s.memory_percent for s in self.system_snapshots]
        disk_values = [s.disk_usage_percent for s in self.system_snapshots]

        return {
            "cpu_usage": {
                "min": min(cpu_values),
                "max": max(cpu_values),
                "mean": statistics.mean(cpu_values),
                "median": statistics.median(cpu_values),
            },
            "memory_usage": {
                "min": min(memory_values),
                "max": max(memory_values),
                "mean": statistics.mean(memory_values),
                "median": statistics.median(memory_values),
            },
            "disk_usage": {
                "min": min(disk_values),
                "max": max(disk_values),
                "mean": statistics.mean(disk_values),
                "median": statistics.median(disk_values),
            },
            "collection_duration": (
                (self.collection_end_time - self.collection_start_time).total_seconds()
                if self.collection_end_time and self.collection_start_time
                else 0
            ),
        }

    def get_error_summary(self) -> dict[str, Any]:
        """Get error occurrence summary."""
        total_errors = sum(self.error_counts.values())

        return {
            "total_errors": total_errors,
            "error_types": dict(self.error_counts),
            "error_rate": total_errors / len(self.metrics) if self.metrics else 0,
        }

    def get_test_timing_summary(self) -> dict[str, Any]:
        """Get test execution timing summary."""
        timing_summary = {}

        for test_name, timings in self.test_timings.items():
            if timings:
                timing_summary[test_name] = {
                    "executions": len(timings),
                    "min_duration": min(timings),
                    "max_duration": max(timings),
                    "mean_duration": statistics.mean(timings),
                    "median_duration": statistics.median(timings),
                    "total_duration": sum(timings),
                }

        return timing_summary

    def get_comprehensive_report(self) -> dict[str, Any]:
        """Get comprehensive metrics report."""
        return {
            "collection_period": {
                "start_time": (
                    self.collection_start_time.isoformat()
                    if self.collection_start_time
                    else None
                ),
                "end_time": (
                    self.collection_end_time.isoformat()
                    if self.collection_end_time
                    else None
                ),
                "duration_seconds": (
                    (
                        self.collection_end_time - self.collection_start_time
                    ).total_seconds()
                    if self.collection_end_time and self.collection_start_time
                    else 0
                ),
            },
            "performance_summary": self.get_performance_summary(),
            "system_resource_summary": self.get_system_resource_summary(),
            "error_summary": self.get_error_summary(),
            "test_timing_summary": self.get_test_timing_summary(),
            "metrics_count": len(self.metrics),
            "snapshots_count": len(self.system_snapshots),
        }

    def export_raw_data(self) -> dict[str, Any]:
        """Export raw collected data."""
        return {
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp.isoformat(),
                    "category": m.category,
                    "metadata": m.metadata,
                }
                for m in self.metrics
            ],
            "system_snapshots": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "cpu_percent": s.cpu_percent,
                    "memory_percent": s.memory_percent,
                    "disk_usage_percent": s.disk_usage_percent,
                    "network_connections": s.network_connections,
                    "active_processes": s.active_processes,
                    "load_average": s.load_average,
                }
                for s in self.system_snapshots
            ],
            "error_counts": dict(self.error_counts),
            "test_timings": dict(self.test_timings),
        }

    async def _monitoring_loop(self, interval: float):
        """Background monitoring loop."""
        while self.is_collecting:
            try:
                # Capture system snapshot
                await self.capture_system_snapshot()

                # Wait for next interval
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)

    def reset(self):
        """Reset all collected metrics."""
        self.metrics.clear()
        self.system_snapshots.clear()
        self.error_counts.clear()
        self.test_timings.clear()
        self.collection_start_time = None
        self.collection_end_time = None
        self.is_collecting = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            self.monitoring_task = None
