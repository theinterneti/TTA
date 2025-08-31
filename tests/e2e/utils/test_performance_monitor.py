"""
Performance Monitoring Utilities for E2E Testing

This module provides comprehensive performance monitoring and analysis
tools for end-to-end testing of the TTA therapeutic platform.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric data."""

    name: str
    value: float
    unit: str
    timestamp: float
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """Complete performance snapshot at a point in time."""

    timestamp: float
    cpu_usage: float
    memory_usage: float
    memory_available: float
    active_connections: int
    response_time: float
    error_count: int
    context: dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Comprehensive performance monitoring for E2E tests."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize performance monitor."""
        self.config = config or {}
        self.metrics: list[PerformanceMetric] = []
        self.snapshots: list[PerformanceSnapshot] = []
        self.start_time = None
        self.monitoring_active = False
        self.monitoring_task = None

        # Performance thresholds
        self.thresholds = {
            "api_response_time_ms": self.config.get("api_response_threshold", 200),
            "database_query_time_ms": self.config.get("db_query_threshold", 100),
            "memory_usage_mb": self.config.get("memory_threshold", 512),
            "cpu_usage_percent": self.config.get("cpu_threshold", 80),
            "error_rate_percent": self.config.get("error_rate_threshold", 5),
            "concurrent_users": self.config.get("max_concurrent_users", 100),
        }

    async def start_monitoring(self, interval_seconds: float = 1.0):
        """Start continuous performance monitoring."""
        if self.monitoring_active:
            logger.warning("Performance monitoring already active")
            return

        self.monitoring_active = True
        self.start_time = time.time()

        # Start monitoring task
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )

        logger.info(f"Performance monitoring started with {interval_seconds}s interval")

    async def stop_monitoring(self):
        """Stop performance monitoring."""
        if not self.monitoring_active:
            return

        self.monitoring_active = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Performance monitoring stopped")

    async def _monitoring_loop(self, interval_seconds: float):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Capture performance snapshot
                snapshot = await self._capture_snapshot()
                self.snapshots.append(snapshot)

                # Check thresholds and log warnings
                await self._check_thresholds(snapshot)

                await asyncio.sleep(interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)

    async def _capture_snapshot(self) -> PerformanceSnapshot:
        """Capture current performance snapshot."""
        # System metrics
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        # Mock application-specific metrics (would be real in production)
        active_connections = len(asyncio.all_tasks())  # Simplified
        response_time = 0.0  # Would measure actual response times
        error_count = 0  # Would track actual errors

        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory.used / (1024 * 1024),  # MB
            memory_available=memory.available / (1024 * 1024),  # MB
            active_connections=active_connections,
            response_time=response_time,
            error_count=error_count,
            context={
                "monitoring_duration": (
                    time.time() - self.start_time if self.start_time else 0
                )
            },
        )

        return snapshot

    async def _check_thresholds(self, snapshot: PerformanceSnapshot):
        """Check performance thresholds and log warnings."""
        warnings = []

        if snapshot.cpu_usage > self.thresholds["cpu_usage_percent"]:
            warnings.append(f"High CPU usage: {snapshot.cpu_usage:.1f}%")

        if snapshot.memory_usage > self.thresholds["memory_usage_mb"]:
            warnings.append(f"High memory usage: {snapshot.memory_usage:.1f}MB")

        if snapshot.response_time > self.thresholds["api_response_time_ms"] / 1000:
            warnings.append(
                f"Slow response time: {snapshot.response_time * 1000:.1f}ms"
            )

        if warnings:
            logger.warning(f"Performance threshold violations: {'; '.join(warnings)}")

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str,
        context: dict[str, Any] | None = None,
    ):
        """Record a custom performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            context=context or {},
        )
        self.metrics.append(metric)

    def record_api_response_time(
        self, endpoint: str, response_time_ms: float, status_code: int = 200
    ):
        """Record API response time metric."""
        self.record_metric(
            name="api_response_time",
            value=response_time_ms,
            unit="ms",
            context={
                "endpoint": endpoint,
                "status_code": status_code,
                "threshold_met": response_time_ms
                <= self.thresholds["api_response_time_ms"],
            },
        )

    def record_database_query_time(
        self, query_type: str, query_time_ms: float, success: bool = True
    ):
        """Record database query time metric."""
        self.record_metric(
            name="database_query_time",
            value=query_time_ms,
            unit="ms",
            context={
                "query_type": query_type,
                "success": success,
                "threshold_met": query_time_ms
                <= self.thresholds["database_query_time_ms"],
            },
        )

    def record_therapeutic_outcome(
        self, user_id: str, outcome_score: float, session_duration_s: float
    ):
        """Record therapeutic outcome metric."""
        self.record_metric(
            name="therapeutic_outcome",
            value=outcome_score,
            unit="score",
            context={
                "user_id": user_id,
                "session_duration_s": session_duration_s,
                "outcome_quality": (
                    "excellent"
                    if outcome_score > 0.8
                    else "good"
                    if outcome_score > 0.6
                    else "needs_improvement"
                ),
            },
        )

    def record_crisis_intervention_time(
        self, user_id: str, intervention_time_s: float, crisis_level: str
    ):
        """Record crisis intervention response time."""
        self.record_metric(
            name="crisis_intervention_time",
            value=intervention_time_s,
            unit="seconds",
            context={
                "user_id": user_id,
                "crisis_level": crisis_level,
                "response_acceptable": intervention_time_s
                <= 5.0,  # 5 second threshold for crisis response
            },
        )

    def get_performance_summary(self) -> dict[str, Any]:
        """Generate comprehensive performance summary."""
        if not self.snapshots:
            return {"error": "No performance data available"}

        # Calculate summary statistics
        cpu_values = [s.cpu_usage for s in self.snapshots]
        memory_values = [s.memory_usage for s in self.snapshots]
        response_times = [
            m.value for m in self.metrics if m.name == "api_response_time"
        ]
        db_query_times = [
            m.value for m in self.metrics if m.name == "database_query_time"
        ]

        summary = {
            "monitoring_duration_s": (
                time.time() - self.start_time if self.start_time else 0
            ),
            "snapshots_captured": len(self.snapshots),
            "metrics_recorded": len(self.metrics),
            "system_performance": {
                "cpu_usage": {
                    "avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    "max": max(cpu_values) if cpu_values else 0,
                    "threshold_violations": sum(
                        1
                        for v in cpu_values
                        if v > self.thresholds["cpu_usage_percent"]
                    ),
                },
                "memory_usage_mb": {
                    "avg": (
                        sum(memory_values) / len(memory_values) if memory_values else 0
                    ),
                    "max": max(memory_values) if memory_values else 0,
                    "threshold_violations": sum(
                        1
                        for v in memory_values
                        if v > self.thresholds["memory_usage_mb"]
                    ),
                },
            },
            "application_performance": {
                "api_response_times_ms": {
                    "count": len(response_times),
                    "avg": (
                        sum(response_times) / len(response_times)
                        if response_times
                        else 0
                    ),
                    "max": max(response_times) if response_times else 0,
                    "threshold_violations": sum(
                        1
                        for t in response_times
                        if t > self.thresholds["api_response_time_ms"]
                    ),
                },
                "database_query_times_ms": {
                    "count": len(db_query_times),
                    "avg": (
                        sum(db_query_times) / len(db_query_times)
                        if db_query_times
                        else 0
                    ),
                    "max": max(db_query_times) if db_query_times else 0,
                    "threshold_violations": sum(
                        1
                        for t in db_query_times
                        if t > self.thresholds["database_query_time_ms"]
                    ),
                },
            },
            "therapeutic_metrics": self._get_therapeutic_metrics_summary(),
            "threshold_compliance": self._calculate_threshold_compliance(),
        }

        return summary

    def _get_therapeutic_metrics_summary(self) -> dict[str, Any]:
        """Get summary of therapeutic-specific metrics."""
        therapeutic_outcomes = [
            m for m in self.metrics if m.name == "therapeutic_outcome"
        ]
        crisis_interventions = [
            m for m in self.metrics if m.name == "crisis_intervention_time"
        ]

        return {
            "therapeutic_outcomes": {
                "count": len(therapeutic_outcomes),
                "avg_score": (
                    sum(m.value for m in therapeutic_outcomes)
                    / len(therapeutic_outcomes)
                    if therapeutic_outcomes
                    else 0
                ),
                "excellent_outcomes": sum(
                    1 for m in therapeutic_outcomes if m.value > 0.8
                ),
                "good_outcomes": sum(
                    1 for m in therapeutic_outcomes if 0.6 < m.value <= 0.8
                ),
            },
            "crisis_interventions": {
                "count": len(crisis_interventions),
                "avg_response_time_s": (
                    sum(m.value for m in crisis_interventions)
                    / len(crisis_interventions)
                    if crisis_interventions
                    else 0
                ),
                "fast_responses": sum(
                    1 for m in crisis_interventions if m.value <= 5.0
                ),
                "critical_interventions": sum(
                    1
                    for m in crisis_interventions
                    if m.context.get("crisis_level") == "CRITICAL"
                ),
            },
        }

    def _calculate_threshold_compliance(self) -> dict[str, float]:
        """Calculate compliance rates for all thresholds."""
        compliance = {}

        # API response time compliance
        api_metrics = [m for m in self.metrics if m.name == "api_response_time"]
        if api_metrics:
            compliant = sum(
                1 for m in api_metrics if m.context.get("threshold_met", False)
            )
            compliance["api_response_time"] = compliant / len(api_metrics)

        # Database query time compliance
        db_metrics = [m for m in self.metrics if m.name == "database_query_time"]
        if db_metrics:
            compliant = sum(
                1 for m in db_metrics if m.context.get("threshold_met", False)
            )
            compliance["database_query_time"] = compliant / len(db_metrics)

        # Crisis intervention compliance
        crisis_metrics = [
            m for m in self.metrics if m.name == "crisis_intervention_time"
        ]
        if crisis_metrics:
            compliant = sum(
                1 for m in crisis_metrics if m.context.get("response_acceptable", False)
            )
            compliance["crisis_intervention_time"] = compliant / len(crisis_metrics)

        return compliance

    async def save_performance_report(self, filepath: str):
        """Save comprehensive performance report to file."""
        report = {
            "performance_summary": self.get_performance_summary(),
            "detailed_metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp,
                    "context": m.context,
                }
                for m in self.metrics
            ],
            "snapshots": [
                {
                    "timestamp": s.timestamp,
                    "cpu_usage": s.cpu_usage,
                    "memory_usage": s.memory_usage,
                    "memory_available": s.memory_available,
                    "active_connections": s.active_connections,
                    "response_time": s.response_time,
                    "error_count": s.error_count,
                    "context": s.context,
                }
                for s in self.snapshots
            ],
            "thresholds": self.thresholds,
            "test_metadata": {
                "start_time": self.start_time,
                "end_time": time.time(),
                "duration_s": time.time() - self.start_time if self.start_time else 0,
            },
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Performance report saved to {filepath}")


class LoadTestScenario:
    """Load testing scenario configuration and execution."""

    def __init__(
        self, name: str, concurrent_users: int, duration_s: float, ramp_up_s: float = 0
    ):
        """Initialize load test scenario."""
        self.name = name
        self.concurrent_users = concurrent_users
        self.duration_s = duration_s
        self.ramp_up_s = ramp_up_s
        self.results = []

    async def execute(self, test_function, *args, **kwargs) -> dict[str, Any]:
        """Execute load test scenario."""
        logger.info(f"Starting load test scenario: {self.name}")
        logger.info(
            f"Concurrent users: {self.concurrent_users}, Duration: {self.duration_s}s"
        )

        start_time = time.time()
        tasks = []

        # Create tasks with ramp-up
        for i in range(self.concurrent_users):
            if self.ramp_up_s > 0:
                delay = (i / self.concurrent_users) * self.ramp_up_s
                await asyncio.sleep(delay)

            task = asyncio.create_task(test_function(*args, **kwargs))
            tasks.append(task)

        # Wait for all tasks to complete or timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.duration_s + self.ramp_up_s + 30,  # Extra buffer
            )
        except asyncio.TimeoutError:
            logger.warning(f"Load test {self.name} timed out")
            results = ["timeout"] * len(tasks)

        end_time = time.time()

        # Analyze results
        successful = sum(
            1 for r in results if not isinstance(r, Exception) and r != "timeout"
        )
        failed = len(results) - successful

        scenario_results = {
            "scenario_name": self.name,
            "concurrent_users": self.concurrent_users,
            "duration_s": end_time - start_time,
            "successful_requests": successful,
            "failed_requests": failed,
            "success_rate": successful / len(results) if results else 0,
            "requests_per_second": len(results) / (end_time - start_time),
            "errors": [str(r) for r in results if isinstance(r, Exception)],
        }

        self.results.append(scenario_results)
        logger.info(
            f"Load test {self.name} completed: {successful}/{len(results)} successful"
        )

        return scenario_results
