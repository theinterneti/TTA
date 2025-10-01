"""
Comprehensive metrics collection system for performance monitoring.

This module provides classes and utilities for collecting, aggregating, and
analyzing various performance metrics across the Player Experience Interface.
"""

import json
import statistics
import threading
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    """Types of metrics that can be collected."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class MetricSeverity(str, Enum):
    """Severity levels for metric alerts."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """Individual metric data point."""

    timestamp: datetime
    value: int | float
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance-related metrics."""

    request_count: int = 0
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0  # requests per second
    concurrent_users: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request_count": self.request_count,
            "average_response_time": self.average_response_time,
            "p95_response_time": self.p95_response_time,
            "p99_response_time": self.p99_response_time,
            "error_rate": self.error_rate,
            "throughput": self.throughput,
            "concurrent_users": self.concurrent_users,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "active_connections": self.active_connections,
        }


@dataclass
class DatabaseMetrics:
    """Database performance metrics."""

    query_count: int = 0
    average_query_time: float = 0.0
    slow_query_count: int = 0
    connection_pool_size: int = 0
    active_connections: int = 0
    failed_queries: int = 0
    cache_hit_rate: float = 0.0
    index_usage_rate: float = 0.0
    deadlock_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "query_count": self.query_count,
            "average_query_time": self.average_query_time,
            "slow_query_count": self.slow_query_count,
            "connection_pool_size": self.connection_pool_size,
            "active_connections": self.active_connections,
            "failed_queries": self.failed_queries,
            "cache_hit_rate": self.cache_hit_rate,
            "index_usage_rate": self.index_usage_rate,
            "deadlock_count": self.deadlock_count,
        }


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    hit_count: int = 0
    miss_count: int = 0
    hit_rate: float = 0.0
    eviction_count: int = 0
    memory_usage_mb: float = 0.0
    key_count: int = 0
    average_get_time: float = 0.0
    average_set_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": self.hit_rate,
            "eviction_count": self.eviction_count,
            "memory_usage_mb": self.memory_usage_mb,
            "key_count": self.key_count,
            "average_get_time": self.average_get_time,
            "average_set_time": self.average_set_time,
        }


@dataclass
class ErrorMetrics:
    """Error tracking metrics."""

    total_errors: int = 0
    error_rate: float = 0.0
    errors_by_type: dict[str, int] = field(default_factory=dict)
    errors_by_endpoint: dict[str, int] = field(default_factory=dict)
    critical_errors: int = 0
    recovery_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_errors": self.total_errors,
            "error_rate": self.error_rate,
            "errors_by_type": self.errors_by_type,
            "errors_by_endpoint": self.errors_by_endpoint,
            "critical_errors": self.critical_errors,
            "recovery_time": self.recovery_time,
        }


@dataclass
class UserEngagementMetrics:
    """User engagement and therapeutic effectiveness metrics."""

    active_users: int = 0
    session_duration_avg: float = 0.0
    therapeutic_interactions: int = 0
    completion_rate: float = 0.0
    user_satisfaction_score: float = 0.0
    crisis_interventions: int = 0
    successful_interventions: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "active_users": self.active_users,
            "session_duration_avg": self.session_duration_avg,
            "therapeutic_interactions": self.therapeutic_interactions,
            "completion_rate": self.completion_rate,
            "user_satisfaction_score": self.user_satisfaction_score,
            "crisis_interventions": self.crisis_interventions,
            "successful_interventions": self.successful_interventions,
        }


class MetricsCollector:
    """Central metrics collection and aggregation system."""

    def __init__(self, max_history_size: int = 10000, aggregation_interval: int = 60):
        """
        Initialize metrics collector.

        Args:
            max_history_size: Maximum number of metric points to keep in memory
            aggregation_interval: Interval in seconds for metric aggregation
        """
        self.max_history_size = max_history_size
        self.aggregation_interval = aggregation_interval

        # Metric storage
        self.metrics: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_history_size)
        )
        self.counters: dict[str, int] = defaultdict(int)
        self.gauges: dict[str, float] = defaultdict(float)
        self.timers: dict[str, list[float]] = defaultdict(list)

        # Thread safety
        self.lock = threading.RLock()

        # Background aggregation
        self.aggregation_thread = None
        self.stop_aggregation = threading.Event()

        # Metric callbacks
        self.metric_callbacks: dict[str, list[Callable]] = defaultdict(list)

        # Start background aggregation
        self.start_aggregation()

    def start_aggregation(self):
        """Start background metric aggregation."""
        if self.aggregation_thread is None or not self.aggregation_thread.is_alive():
            self.stop_aggregation.clear()
            self.aggregation_thread = threading.Thread(
                target=self._aggregation_loop, daemon=True
            )
            self.aggregation_thread.start()

    def stop(self):
        """Stop the metrics collector."""
        self.stop_aggregation.set()
        if self.aggregation_thread and self.aggregation_thread.is_alive():
            self.aggregation_thread.join(timeout=5)

    def _aggregation_loop(self):
        """Background loop for metric aggregation."""
        while not self.stop_aggregation.wait(self.aggregation_interval):
            try:
                self._aggregate_metrics()
            except Exception as e:
                print(f"Error in metrics aggregation: {e}")

    def _aggregate_metrics(self):
        """Aggregate metrics and trigger callbacks."""
        with self.lock:
            # Aggregate timers
            for metric_name, times in self.timers.items():
                if times:
                    avg_time = statistics.mean(times)
                    p95_time = (
                        statistics.quantiles(times, n=20)[18]
                        if len(times) >= 20
                        else max(times)
                    )
                    p99_time = (
                        statistics.quantiles(times, n=100)[98]
                        if len(times) >= 100
                        else max(times)
                    )

                    self.record_gauge(f"{metric_name}_avg", avg_time)
                    self.record_gauge(f"{metric_name}_p95", p95_time)
                    self.record_gauge(f"{metric_name}_p99", p99_time)

                    # Clear timer data after aggregation
                    times.clear()

            # Trigger callbacks
            for metric_name, callbacks in self.metric_callbacks.items():
                for callback in callbacks:
                    try:
                        callback(metric_name, self.get_metric_value(metric_name))
                    except Exception as e:
                        print(f"Error in metric callback for {metric_name}: {e}")

    def record_counter(
        self, name: str, value: int = 1, tags: dict[str, str] | None = None
    ):
        """Record a counter metric."""
        with self.lock:
            self.counters[name] += value
            self._record_metric_point(name, value, MetricType.COUNTER, tags)

    def record_gauge(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ):
        """Record a gauge metric."""
        with self.lock:
            self.gauges[name] = value
            self._record_metric_point(name, value, MetricType.GAUGE, tags)

    def record_timer(
        self, name: str, duration: float, tags: dict[str, str] | None = None
    ):
        """Record a timer metric."""
        with self.lock:
            self.timers[name].append(duration)
            self._record_metric_point(name, duration, MetricType.TIMER, tags)

    def record_histogram(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ):
        """Record a histogram metric."""
        with self.lock:
            self._record_metric_point(name, value, MetricType.HISTOGRAM, tags)

    def _record_metric_point(
        self,
        name: str,
        value: int | float,
        metric_type: MetricType,
        tags: dict[str, str] | None = None,
    ):
        """Record a metric point with metadata."""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            tags=tags or {},
            metadata={"type": metric_type.value},
        )
        self.metrics[name].append(point)

    def get_metric_value(self, name: str) -> int | float | None:
        """Get current value of a metric."""
        with self.lock:
            if name in self.counters:
                return self.counters[name]
            elif name in self.gauges:
                return self.gauges[name]
            elif name in self.metrics and self.metrics[name]:
                return self.metrics[name][-1].value
            return None

    def get_metric_history(
        self, name: str, duration: timedelta | None = None
    ) -> list[MetricPoint]:
        """Get metric history for a given duration."""
        with self.lock:
            if name not in self.metrics:
                return []

            points = list(self.metrics[name])

            if duration:
                cutoff_time = datetime.utcnow() - duration
                points = [p for p in points if p.timestamp >= cutoff_time]

            return points

    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get aggregated performance metrics."""
        with self.lock:
            return PerformanceMetrics(
                request_count=self.counters.get("requests_total", 0),
                average_response_time=self.gauges.get("response_time_avg", 0.0),
                p95_response_time=self.gauges.get("response_time_p95", 0.0),
                p99_response_time=self.gauges.get("response_time_p99", 0.0),
                error_rate=self.gauges.get("error_rate", 0.0),
                throughput=self.gauges.get("throughput", 0.0),
                concurrent_users=self.gauges.get("concurrent_users", 0),
                memory_usage_mb=self.gauges.get("memory_usage_mb", 0.0),
                cpu_usage_percent=self.gauges.get("cpu_usage_percent", 0.0),
                active_connections=self.gauges.get("active_connections", 0),
            )

    def get_database_metrics(self) -> DatabaseMetrics:
        """Get aggregated database metrics."""
        with self.lock:
            return DatabaseMetrics(
                query_count=self.counters.get("db_queries_total", 0),
                average_query_time=self.gauges.get("db_query_time_avg", 0.0),
                slow_query_count=self.counters.get("db_slow_queries", 0),
                connection_pool_size=self.gauges.get("db_pool_size", 0),
                active_connections=self.gauges.get("db_active_connections", 0),
                failed_queries=self.counters.get("db_failed_queries", 0),
                cache_hit_rate=self.gauges.get("db_cache_hit_rate", 0.0),
                index_usage_rate=self.gauges.get("db_index_usage_rate", 0.0),
                deadlock_count=self.counters.get("db_deadlocks", 0),
            )

    def get_cache_metrics(self) -> CacheMetrics:
        """Get aggregated cache metrics."""
        with self.lock:
            hit_count = self.counters.get("cache_hits", 0)
            miss_count = self.counters.get("cache_misses", 0)
            total_requests = hit_count + miss_count
            hit_rate = (hit_count / total_requests * 100) if total_requests > 0 else 0.0

            return CacheMetrics(
                hit_count=hit_count,
                miss_count=miss_count,
                hit_rate=hit_rate,
                eviction_count=self.counters.get("cache_evictions", 0),
                memory_usage_mb=self.gauges.get("cache_memory_mb", 0.0),
                key_count=self.gauges.get("cache_key_count", 0),
                average_get_time=self.gauges.get("cache_get_time_avg", 0.0),
                average_set_time=self.gauges.get("cache_set_time_avg", 0.0),
            )

    def get_error_metrics(self) -> ErrorMetrics:
        """Get aggregated error metrics."""
        with self.lock:
            total_requests = self.counters.get("requests_total", 0)
            total_errors = self.counters.get("errors_total", 0)
            error_rate = (
                (total_errors / total_requests * 100) if total_requests > 0 else 0.0
            )

            return ErrorMetrics(
                total_errors=total_errors,
                error_rate=error_rate,
                errors_by_type=dict(self.counters.get("errors_by_type", {})),
                errors_by_endpoint=dict(self.counters.get("errors_by_endpoint", {})),
                critical_errors=self.counters.get("critical_errors", 0),
                recovery_time=self.gauges.get("recovery_time", 0.0),
            )

    def get_user_engagement_metrics(self) -> UserEngagementMetrics:
        """Get user engagement metrics."""
        with self.lock:
            return UserEngagementMetrics(
                active_users=self.gauges.get("active_users", 0),
                session_duration_avg=self.gauges.get("session_duration_avg", 0.0),
                therapeutic_interactions=self.counters.get(
                    "therapeutic_interactions", 0
                ),
                completion_rate=self.gauges.get("completion_rate", 0.0),
                user_satisfaction_score=self.gauges.get("user_satisfaction", 0.0),
                crisis_interventions=self.counters.get("crisis_interventions", 0),
                successful_interventions=self.counters.get(
                    "successful_interventions", 0
                ),
            )

    def add_metric_callback(
        self, metric_name: str, callback: Callable[[str, Any], None]
    ):
        """Add a callback for metric changes."""
        self.metric_callbacks[metric_name].append(callback)

    def remove_metric_callback(
        self, metric_name: str, callback: Callable[[str, Any], None]
    ):
        """Remove a metric callback."""
        if metric_name in self.metric_callbacks:
            try:
                self.metric_callbacks[metric_name].remove(callback)
            except ValueError:
                pass

    def export_metrics(self, format_type: str = "json") -> str:
        """Export all metrics in specified format."""
        with self.lock:
            metrics_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "performance": self.get_performance_metrics().to_dict(),
                "database": self.get_database_metrics().to_dict(),
                "cache": self.get_cache_metrics().to_dict(),
                "errors": self.get_error_metrics().to_dict(),
                "user_engagement": self.get_user_engagement_metrics().to_dict(),
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
            }

            if format_type.lower() == "json":
                return json.dumps(metrics_data, indent=2, default=str)
            else:
                return str(metrics_data)

    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.timers.clear()


# Global metrics collector instance
_global_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


def record_request_metric(
    endpoint: str, method: str, status_code: int, duration: float
):
    """Convenience function to record request metrics."""
    collector = get_metrics_collector()

    # Record basic metrics
    collector.record_counter("requests_total")
    collector.record_timer("response_time", duration)

    # Record by endpoint
    collector.record_counter(f"requests_by_endpoint_{endpoint}")
    collector.record_timer(f"response_time_{endpoint}", duration)

    # Record by method
    collector.record_counter(f"requests_by_method_{method}")

    # Record errors
    if status_code >= 400:
        collector.record_counter("errors_total")
        collector.record_counter(f"errors_by_status_{status_code}")

        if status_code >= 500:
            collector.record_counter("critical_errors")


def record_database_query_metric(query_type: str, duration: float, success: bool):
    """Convenience function to record database query metrics."""
    collector = get_metrics_collector()

    collector.record_counter("db_queries_total")
    collector.record_timer("db_query_time", duration)
    collector.record_timer(f"db_query_time_{query_type}", duration)

    if not success:
        collector.record_counter("db_failed_queries")
        collector.record_counter(f"db_failed_queries_{query_type}")

    # Track slow queries (> 1 second)
    if duration > 1.0:
        collector.record_counter("db_slow_queries")


def record_cache_metric(operation: str, hit: bool, duration: float):
    """Convenience function to record cache metrics."""
    collector = get_metrics_collector()

    if hit:
        collector.record_counter("cache_hits")
    else:
        collector.record_counter("cache_misses")

    collector.record_timer(f"cache_{operation}_time", duration)


def record_therapeutic_interaction(
    interaction_type: str, success: bool, user_satisfaction: float | None = None
):
    """Convenience function to record therapeutic interaction metrics."""
    collector = get_metrics_collector()

    collector.record_counter("therapeutic_interactions")
    collector.record_counter(f"therapeutic_interactions_{interaction_type}")

    if success:
        collector.record_counter("successful_interventions")

    if user_satisfaction is not None:
        collector.record_gauge("user_satisfaction", user_satisfaction)
