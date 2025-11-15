"""
Comprehensive response time monitoring system.

This module provides detailed response time tracking across all agent operations
with real-time metrics collection, analysis, and optimization recommendations.
"""

from __future__ import annotations

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class OperationType(str, Enum):
    """Types of operations to monitor."""

    AGENT_PROCESSING = "agent_processing"
    WORKFLOW_EXECUTION = "workflow_execution"
    MESSAGE_COORDINATION = "message_coordination"
    DATABASE_OPERATION = "database_operation"
    EXTERNAL_API_CALL = "external_api_call"
    CACHE_OPERATION = "cache_operation"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"


class PerformanceLevel(str, Enum):
    """Performance level classifications."""

    EXCELLENT = "excellent"  # < 0.5s
    GOOD = "good"  # 0.5s - 1.0s
    ACCEPTABLE = "acceptable"  # 1.0s - 2.0s
    SLOW = "slow"  # 2.0s - 5.0s
    CRITICAL = "critical"  # > 5.0s


@dataclass
class ResponseTimeMetric:
    """Individual response time measurement."""

    operation_id: str
    operation_type: OperationType
    start_time: float
    end_time: float
    duration: float
    agent_id: str | None = None
    workflow_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def performance_level(self) -> PerformanceLevel:
        """Classify performance level based on duration."""
        if self.duration < 0.5:
            return PerformanceLevel.EXCELLENT
        if self.duration < 1.0:
            return PerformanceLevel.GOOD
        if self.duration < 2.0:
            return PerformanceLevel.ACCEPTABLE
        if self.duration < 5.0:
            return PerformanceLevel.SLOW
        return PerformanceLevel.CRITICAL


@dataclass
class PerformanceStatistics:
    """Aggregated performance statistics."""

    operation_type: OperationType
    total_operations: int
    average_duration: float
    median_duration: float
    p95_duration: float
    p99_duration: float
    min_duration: float
    max_duration: float
    success_rate: float
    performance_distribution: dict[PerformanceLevel, int]

    @property
    def meets_sla(self) -> bool:
        """Check if performance meets 2-second SLA."""
        return self.p95_duration < 2.0


class ResponseTimeMonitor:
    """Comprehensive response time monitoring system."""

    def __init__(
        self,
        max_metrics_history: int = 10000,
        statistics_window_minutes: int = 60,
        enable_real_time_analysis: bool = True,
    ):
        self.max_metrics_history = max_metrics_history
        self.statistics_window_minutes = statistics_window_minutes
        self.enable_real_time_analysis = enable_real_time_analysis

        # Metrics storage
        self.metrics_history: deque[ResponseTimeMetric] = deque(maxlen=max_metrics_history)
        self.active_operations: dict[str, dict[str, Any]] = {}

        # Statistics cache
        self.statistics_cache: dict[OperationType, PerformanceStatistics] = {}
        self.last_statistics_update: float = 0.0
        self.statistics_cache_ttl: float = 30.0  # 30 seconds

        # Performance thresholds
        self.performance_thresholds = {
            PerformanceLevel.EXCELLENT: 0.5,
            PerformanceLevel.GOOD: 1.0,
            PerformanceLevel.ACCEPTABLE: 2.0,
            PerformanceLevel.SLOW: 5.0,
        }

        # Alert callbacks
        self.alert_callbacks: list[Callable] = []

        # Background tasks
        self.cleanup_task: asyncio.Task | None = None
        self.analysis_task: asyncio.Task | None = None
        self.is_running = False

        logger.info("ResponseTimeMonitor initialized")

    async def start(self) -> None:
        """Start the response time monitor."""
        if self.is_running:
            return

        self.is_running = True

        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        if self.enable_real_time_analysis:
            self.analysis_task = asyncio.create_task(self._analysis_loop())

        logger.info("ResponseTimeMonitor started")

    async def stop(self) -> None:
        """Stop the response time monitor."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel background tasks
        for task in [self.cleanup_task, self.analysis_task]:
            if task:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

        logger.info("ResponseTimeMonitor stopped")

    @asynccontextmanager
    async def track_operation(
        self,
        operation_type: OperationType,
        agent_id: str | None = None,
        workflow_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Context manager for tracking operation response time."""
        operation_id = f"{operation_type.value}_{int(time.time() * 1000000)}"
        start_time = time.time()

        # Store active operation
        self.active_operations[operation_id] = {
            "operation_type": operation_type,
            "start_time": start_time,
            "agent_id": agent_id,
            "workflow_id": workflow_id,
            "user_id": user_id,
            "metadata": metadata or {},
        }

        try:
            yield operation_id

            # Record successful completion
            end_time = time.time()
            duration = end_time - start_time

            metric = ResponseTimeMetric(
                operation_id=operation_id,
                operation_type=operation_type,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                agent_id=agent_id,
                workflow_id=workflow_id,
                user_id=user_id,
                metadata=metadata or {},
            )

            await self._record_metric(metric)

        except Exception as e:
            # Record failed operation
            end_time = time.time()
            duration = end_time - start_time

            failed_metadata = (metadata or {}).copy()
            failed_metadata.update({"error": str(e), "success": False})

            metric = ResponseTimeMetric(
                operation_id=operation_id,
                operation_type=operation_type,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                agent_id=agent_id,
                workflow_id=workflow_id,
                user_id=user_id,
                metadata=failed_metadata,
            )

            await self._record_metric(metric)
            raise

        finally:
            # Cleanup active operation
            self.active_operations.pop(operation_id, None)

    async def _record_metric(self, metric: ResponseTimeMetric) -> None:
        """Record a response time metric."""
        self.metrics_history.append(metric)

        # Check for performance alerts
        if metric.performance_level in [
            PerformanceLevel.SLOW,
            PerformanceLevel.CRITICAL,
        ]:
            await self._trigger_performance_alert(metric)

        # Invalidate statistics cache if needed
        if metric.operation_type in self.statistics_cache:
            del self.statistics_cache[metric.operation_type]

    async def _trigger_performance_alert(self, metric: ResponseTimeMetric) -> None:
        """Trigger performance alert for slow operations."""
        alert_data = {
            "type": "performance_alert",
            "operation_id": metric.operation_id,
            "operation_type": metric.operation_type.value,
            "duration": metric.duration,
            "performance_level": metric.performance_level.value,
            "agent_id": metric.agent_id,
            "workflow_id": metric.workflow_id,
            "timestamp": metric.end_time,
        }

        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    def get_statistics(
        self,
        operation_type: OperationType | None = None,
        time_window_minutes: int | None = None,
    ) -> dict[OperationType, PerformanceStatistics]:
        """Get performance statistics for operation types."""
        current_time = time.time()
        time_window = time_window_minutes or self.statistics_window_minutes
        cutoff_time = current_time - (time_window * 60)

        # Filter metrics by time window
        recent_metrics = [
            metric for metric in self.metrics_history if metric.end_time >= cutoff_time
        ]

        if operation_type:
            recent_metrics = [
                metric for metric in recent_metrics if metric.operation_type == operation_type
            ]

        # Group metrics by operation type
        metrics_by_type = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_type[metric.operation_type].append(metric)

        # Calculate statistics for each operation type
        statistics = {}
        for op_type, metrics in metrics_by_type.items():
            if metrics:
                statistics[op_type] = self._calculate_statistics(op_type, metrics)

        return statistics

    def _calculate_statistics(
        self, operation_type: OperationType, metrics: list[ResponseTimeMetric]
    ) -> PerformanceStatistics:
        """Calculate performance statistics for a set of metrics."""
        durations = [metric.duration for metric in metrics]
        successful_operations = [metric for metric in metrics if not metric.metadata.get("error")]

        # Performance level distribution
        performance_distribution = defaultdict(int)
        for metric in metrics:
            performance_distribution[metric.performance_level] += 1

        return PerformanceStatistics(
            operation_type=operation_type,
            total_operations=len(metrics),
            average_duration=statistics.mean(durations),
            median_duration=statistics.median(durations),
            p95_duration=self._percentile(durations, 95),
            p99_duration=self._percentile(durations, 99),
            min_duration=min(durations),
            max_duration=max(durations),
            success_rate=len(successful_operations) / len(metrics) if metrics else 0.0,
            performance_distribution=dict(performance_distribution),
        )

    def _percentile(self, data: list[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = (percentile / 100.0) * (len(sorted_data) - 1)

        if index.is_integer():
            return sorted_data[int(index)]
        lower_index = int(index)
        upper_index = lower_index + 1
        weight = index - lower_index

        if upper_index >= len(sorted_data):
            return sorted_data[lower_index]

        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight

    async def _cleanup_loop(self) -> None:
        """Background task to clean up old metrics."""
        while self.is_running:
            try:
                current_time = time.time()

                # Clean up old active operations (stuck operations)
                stuck_operations = [
                    op_id
                    for op_id, op_data in self.active_operations.items()
                    if current_time - op_data["start_time"] > 300  # 5 minutes
                ]

                for op_id in stuck_operations:
                    logger.warning(f"Cleaning up stuck operation: {op_id}")
                    self.active_operations.pop(op_id, None)

                await asyncio.sleep(60)  # Clean up every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)

    async def _analysis_loop(self) -> None:
        """Background task for real-time performance analysis."""
        while self.is_running:
            try:
                # Perform real-time analysis every 30 seconds
                await self._perform_real_time_analysis()
                await asyncio.sleep(30)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(30)

    async def _perform_real_time_analysis(self) -> None:
        """Perform real-time performance analysis."""
        statistics = self.get_statistics(time_window_minutes=5)  # Last 5 minutes

        for op_type, stats in statistics.items():
            # Check SLA violations
            if not stats.meets_sla:
                await self._trigger_sla_violation_alert(op_type, stats)

            # Check for performance degradation
            if stats.average_duration > self.performance_thresholds[PerformanceLevel.ACCEPTABLE]:
                await self._trigger_degradation_alert(op_type, stats)

    async def _trigger_sla_violation_alert(
        self, operation_type: OperationType, statistics: PerformanceStatistics
    ) -> None:
        """Trigger SLA violation alert."""
        alert_data = {
            "type": "sla_violation",
            "operation_type": operation_type.value,
            "p95_duration": statistics.p95_duration,
            "sla_threshold": 2.0,
            "total_operations": statistics.total_operations,
            "timestamp": time.time(),
        }

        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error(f"SLA violation alert callback failed: {e}")

    async def _trigger_degradation_alert(
        self, operation_type: OperationType, statistics: PerformanceStatistics
    ) -> None:
        """Trigger performance degradation alert."""
        alert_data = {
            "type": "performance_degradation",
            "operation_type": operation_type.value,
            "average_duration": statistics.average_duration,
            "acceptable_threshold": self.performance_thresholds[PerformanceLevel.ACCEPTABLE],
            "total_operations": statistics.total_operations,
            "timestamp": time.time(),
        }

        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error(f"Degradation alert callback failed: {e}")

    def add_alert_callback(self, callback: Callable) -> None:
        """Add alert callback function."""
        self.alert_callbacks.append(callback)

    def get_active_operations(self) -> dict[str, dict[str, Any]]:
        """Get currently active operations."""
        return self.active_operations.copy()

    def get_performance_summary(self) -> dict[str, Any]:
        """Get overall performance summary."""
        statistics = self.get_statistics()

        if not statistics:
            return {
                "total_operations": 0,
                "overall_performance": "no_data",
                "sla_compliance": 0.0,
                "active_operations": len(self.active_operations),
            }

        # Calculate overall metrics
        total_operations = sum(stats.total_operations for stats in statistics.values())
        sla_compliant_types = sum(1 for stats in statistics.values() if stats.meets_sla)
        sla_compliance = sla_compliant_types / len(statistics) if statistics else 0.0

        # Determine overall performance level
        avg_p95 = statistics.mean([stats.p95_duration for stats in statistics.values()])
        if avg_p95 < 0.5:
            overall_performance = PerformanceLevel.EXCELLENT
        elif avg_p95 < 1.0:
            overall_performance = PerformanceLevel.GOOD
        elif avg_p95 < 2.0:
            overall_performance = PerformanceLevel.ACCEPTABLE
        elif avg_p95 < 5.0:
            overall_performance = PerformanceLevel.SLOW
        else:
            overall_performance = PerformanceLevel.CRITICAL

        return {
            "total_operations": total_operations,
            "overall_performance": overall_performance.value,
            "sla_compliance": sla_compliance,
            "active_operations": len(self.active_operations),
            "operation_types": len(statistics),
            "statistics_by_type": {
                op_type.value: {
                    "total_operations": stats.total_operations,
                    "average_duration": stats.average_duration,
                    "p95_duration": stats.p95_duration,
                    "meets_sla": stats.meets_sla,
                    "success_rate": stats.success_rate,
                }
                for op_type, stats in statistics.items()
            },
        }


# Global response time monitor instance
_response_time_monitor: ResponseTimeMonitor | None = None


def get_response_time_monitor() -> ResponseTimeMonitor:
    """Get the global response time monitor."""
    global _response_time_monitor
    if _response_time_monitor is None:
        _response_time_monitor = ResponseTimeMonitor()
    return _response_time_monitor
