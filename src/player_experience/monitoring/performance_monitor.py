"""

# Logseq: [[TTA.dev/Player_experience/Monitoring/Performance_monitor]]
Performance monitoring system with real-time tracking and optimization.

This module provides comprehensive performance monitoring including request tracking,
database query optimization, cache monitoring, and automated performance alerts.
"""

import asyncio
import functools
import gc
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import psutil

from .logging_config import get_logger
from .metrics_collector import MetricsCollector, get_metrics_collector

logger = get_logger(__name__)


@dataclass
class RequestContext:
    """Context information for a request being tracked."""

    request_id: str
    endpoint: str
    method: str
    start_time: float
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryContext:
    """Context information for a database query being tracked."""

    query_id: str
    query_type: str
    query_text: str | None
    start_time: float
    connection_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheOperation:
    """Context information for a cache operation being tracked."""

    operation_id: str
    operation_type: str  # get, set, delete, etc.
    key: str
    start_time: float
    hit: bool | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class PerformanceThresholds:
    """Performance thresholds for alerting."""

    def __init__(self):
        # Response time thresholds (seconds)
        self.response_time_warning = 1.0
        self.response_time_critical = 3.0

        # Database query thresholds (seconds)
        self.query_time_warning = 0.5
        self.query_time_critical = 2.0

        # Error rate thresholds (percentage)
        self.error_rate_warning = 5.0
        self.error_rate_critical = 10.0

        # Memory usage thresholds (percentage)
        self.memory_usage_warning = 80.0
        self.memory_usage_critical = 95.0

        # CPU usage thresholds (percentage)
        self.cpu_usage_warning = 80.0
        self.cpu_usage_critical = 95.0

        # Cache hit rate thresholds (percentage)
        self.cache_hit_rate_warning = 70.0
        self.cache_hit_rate_critical = 50.0


class RequestTracker:
    """Tracks individual request performance."""

    def __init__(self, metrics_collector: MetricsCollector | None = None):
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.active_requests: dict[str, RequestContext] = {}
        self.lock = threading.RLock()

    @contextmanager
    def track_request(
        self,
        request_id: str,
        endpoint: str,
        method: str,
        user_id: str | None = None,
        **metadata,
    ):
        """Context manager to track a request."""
        context = RequestContext(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            start_time=time.time(),
            user_id=user_id,
            metadata=metadata,
        )

        with self.lock:
            self.active_requests[request_id] = context

        try:
            yield context
        finally:
            self._finish_request(context)

    def _finish_request(self, context: RequestContext):
        """Finish tracking a request and record metrics."""
        duration = time.time() - context.start_time

        # Remove from active requests
        with self.lock:
            self.active_requests.pop(context.request_id, None)

        # Record metrics
        self.metrics_collector.record_timer("response_time", duration)
        self.metrics_collector.record_timer(
            f"response_time_{context.endpoint}", duration
        )
        self.metrics_collector.record_counter("requests_total")
        self.metrics_collector.record_counter(f"requests_{context.method}")

        # Update concurrent users if user_id provided
        if context.user_id:
            self._update_concurrent_users()

        logger.debug(f"Request {context.request_id} completed in {duration:.3f}s")

    def _update_concurrent_users(self):
        """Update concurrent users metric."""
        with self.lock:
            unique_users = len(
                {ctx.user_id for ctx in self.active_requests.values() if ctx.user_id}
            )
            self.metrics_collector.record_gauge("concurrent_users", unique_users)

    def get_active_requests(self) -> list[RequestContext]:
        """Get list of currently active requests."""
        with self.lock:
            return list(self.active_requests.values())

    def get_slow_requests(self, threshold: float = 2.0) -> list[RequestContext]:
        """Get requests that are taking longer than threshold."""
        current_time = time.time()
        with self.lock:
            return [
                ctx
                for ctx in self.active_requests.values()
                if current_time - ctx.start_time > threshold
            ]


class DatabaseQueryTracker:
    """Tracks database query performance and optimization opportunities."""

    def __init__(self, metrics_collector: MetricsCollector | None = None):
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.active_queries: dict[str, QueryContext] = {}
        self.query_patterns: dict[str, list[float]] = defaultdict(list)
        self.slow_queries: deque = deque(maxlen=100)
        self.lock = threading.RLock()

    @contextmanager
    def track_query(
        self,
        query_id: str,
        query_type: str,
        query_text: str | None = None,
        connection_id: str | None = None,
        **metadata,
    ):
        """Context manager to track a database query."""
        context = QueryContext(
            query_id=query_id,
            query_type=query_type,
            query_text=query_text,
            start_time=time.time(),
            connection_id=connection_id,
            metadata=metadata,
        )

        with self.lock:
            self.active_queries[query_id] = context

        success = True
        try:
            yield context
        except Exception as e:
            success = False
            logger.error(f"Query {query_id} failed: {e}")
            raise
        finally:
            self._finish_query(context, success)

    def _finish_query(self, context: QueryContext, success: bool):
        """Finish tracking a query and record metrics."""
        duration = time.time() - context.start_time

        # Remove from active queries
        with self.lock:
            self.active_queries.pop(context.query_id, None)

        # Record metrics
        self.metrics_collector.record_timer("db_query_time", duration)
        self.metrics_collector.record_timer(
            f"db_query_time_{context.query_type}", duration
        )
        self.metrics_collector.record_counter("db_queries_total")
        self.metrics_collector.record_counter(f"db_queries_{context.query_type}")

        if not success:
            self.metrics_collector.record_counter("db_failed_queries")

        # Track query patterns for optimization
        with self.lock:
            self.query_patterns[context.query_type].append(duration)

            # Keep only recent measurements
            if len(self.query_patterns[context.query_type]) > 1000:
                self.query_patterns[context.query_type] = self.query_patterns[
                    context.query_type
                ][-500:]

        # Track slow queries
        if duration > 1.0:  # Queries taking more than 1 second
            self.metrics_collector.record_counter("db_slow_queries")
            with self.lock:
                self.slow_queries.append(
                    {
                        "query_id": context.query_id,
                        "query_type": context.query_type,
                        "query_text": context.query_text,
                        "duration": duration,
                        "timestamp": datetime.utcnow(),
                        "metadata": context.metadata,
                    }
                )

        logger.debug(
            f"Query {context.query_id} ({context.query_type}) completed in {duration:.3f}s"
        )

    def get_query_optimization_suggestions(self) -> list[dict[str, Any]]:
        """Get suggestions for query optimization."""
        suggestions = []

        with self.lock:
            for query_type, durations in self.query_patterns.items():
                if len(durations) < 10:  # Need sufficient data
                    continue

                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)

                if avg_duration > 0.5:  # Average query time > 500ms
                    suggestions.append(
                        {
                            "query_type": query_type,
                            "issue": "slow_average_time",
                            "avg_duration": avg_duration,
                            "max_duration": max_duration,
                            "suggestion": "Consider adding indexes or optimizing query structure",
                            "priority": "high" if avg_duration > 2.0 else "medium",
                        }
                    )

                if max_duration > 5.0:  # Max query time > 5 seconds
                    suggestions.append(
                        {
                            "query_type": query_type,
                            "issue": "extremely_slow_queries",
                            "max_duration": max_duration,
                            "suggestion": "Investigate and optimize worst-case scenarios",
                            "priority": "critical",
                        }
                    )

        return suggestions

    def get_slow_queries(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent slow queries."""
        with self.lock:
            return list(self.slow_queries)[-limit:]


class CacheTracker:
    """Tracks cache performance and optimization opportunities."""

    def __init__(self, metrics_collector: MetricsCollector | None = None):
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.active_operations: dict[str, CacheOperation] = {}
        self.cache_patterns: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"hits": 0, "misses": 0, "total_time": 0.0, "operations": 0}
        )
        self.lock = threading.RLock()

    @contextmanager
    def track_cache_operation(
        self, operation_id: str, operation_type: str, key: str, **metadata
    ):
        """Context manager to track a cache operation."""
        operation = CacheOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            key=key,
            start_time=time.time(),
            metadata=metadata,
        )

        with self.lock:
            self.active_operations[operation_id] = operation

        try:
            yield operation
        finally:
            self._finish_cache_operation(operation)

    def _finish_cache_operation(self, operation: CacheOperation):
        """Finish tracking a cache operation and record metrics."""
        duration = time.time() - operation.start_time

        # Remove from active operations
        with self.lock:
            self.active_operations.pop(operation.operation_id, None)

        # Record metrics
        self.metrics_collector.record_timer(
            f"cache_{operation.operation_type}_time", duration
        )

        if operation.operation_type == "get":
            if operation.hit:
                self.metrics_collector.record_counter("cache_hits")
            else:
                self.metrics_collector.record_counter("cache_misses")

        # Track cache patterns
        cache_key_pattern = self._extract_key_pattern(operation.key)
        with self.lock:
            pattern_stats = self.cache_patterns[cache_key_pattern]
            pattern_stats["operations"] += 1
            pattern_stats["total_time"] += duration

            if operation.operation_type == "get":
                if operation.hit:
                    pattern_stats["hits"] += 1
                else:
                    pattern_stats["misses"] += 1

        logger.debug(
            f"Cache {operation.operation_type} for {operation.key} completed in {duration:.3f}s"
        )

    def _extract_key_pattern(self, key: str) -> str:
        """Extract pattern from cache key for analysis."""
        # Simple pattern extraction - replace IDs with placeholders
        import re

        # Replace UUIDs
        pattern = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "{uuid}",
            key,
        )

        # Replace numeric IDs
        return re.sub(r"\d+", "{id}", pattern)

    def get_cache_optimization_suggestions(self) -> list[dict[str, Any]]:
        """Get suggestions for cache optimization."""
        suggestions = []

        with self.lock:
            for pattern, stats in self.cache_patterns.items():
                total_requests = stats["hits"] + stats["misses"]
                if total_requests < 10:  # Need sufficient data
                    continue

                hit_rate = (stats["hits"] / total_requests) * 100
                avg_time = stats["total_time"] / stats["operations"]

                if hit_rate < 70:  # Hit rate below 70%
                    suggestions.append(
                        {
                            "pattern": pattern,
                            "issue": "low_hit_rate",
                            "hit_rate": hit_rate,
                            "total_requests": total_requests,
                            "suggestion": "Consider increasing cache TTL or pre-warming cache",
                            "priority": "high" if hit_rate < 50 else "medium",
                        }
                    )

                if avg_time > 0.1:  # Average cache operation > 100ms
                    suggestions.append(
                        {
                            "pattern": pattern,
                            "issue": "slow_cache_operations",
                            "avg_time": avg_time,
                            "suggestion": "Investigate cache backend performance",
                            "priority": "medium",
                        }
                    )

        return suggestions


class SystemResourceMonitor:
    """Monitors system resources (CPU, memory, etc.)."""

    def __init__(self, metrics_collector: MetricsCollector | None = None):
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 30  # seconds

    def start_monitoring(self):
        """Start system resource monitoring."""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True
            )
            self.monitor_thread.start()
            logger.info("System resource monitoring started")

    def stop_monitoring(self):
        """Stop system resource monitoring."""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        logger.info("System resource monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(self.monitor_interval)

    def _collect_system_metrics(self):
        """Collect system resource metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics_collector.record_gauge("cpu_usage_percent", cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        self.metrics_collector.record_gauge(
            "memory_usage_mb", memory.used / 1024 / 1024
        )
        self.metrics_collector.record_gauge("memory_usage_percent", memory.percent)

        # Disk usage
        disk = psutil.disk_usage("/")
        self.metrics_collector.record_gauge("disk_usage_percent", disk.percent)

        # Network I/O
        network = psutil.net_io_counters()
        self.metrics_collector.record_gauge("network_bytes_sent", network.bytes_sent)
        self.metrics_collector.record_gauge("network_bytes_recv", network.bytes_recv)

        # Process-specific metrics
        process = psutil.Process()
        self.metrics_collector.record_gauge(
            "process_memory_mb", process.memory_info().rss / 1024 / 1024
        )
        self.metrics_collector.record_gauge(
            "process_cpu_percent", process.cpu_percent()
        )
        self.metrics_collector.record_gauge("process_threads", process.num_threads())

        # Garbage collection stats
        gc_stats = gc.get_stats()
        if gc_stats:
            self.metrics_collector.record_gauge(
                "gc_collections", sum(stat["collections"] for stat in gc_stats)
            )
            self.metrics_collector.record_gauge(
                "gc_collected", sum(stat["collected"] for stat in gc_stats)
            )


class PerformanceMonitor:
    """Main performance monitoring coordinator."""

    def __init__(self, metrics_collector: MetricsCollector | None = None):
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.thresholds = PerformanceThresholds()

        # Component trackers
        self.request_tracker = RequestTracker(self.metrics_collector)
        self.db_tracker = DatabaseQueryTracker(self.metrics_collector)
        self.cache_tracker = CacheTracker(self.metrics_collector)
        self.system_monitor = SystemResourceMonitor(self.metrics_collector)

        # Alert callbacks
        self.alert_callbacks: list[Callable[[str, str, dict[str, Any]], None]] = []

        # Start system monitoring
        self.system_monitor.start_monitoring()

        # Set up metric callbacks for alerting
        self._setup_alerting()

    def _setup_alerting(self):
        """Set up alerting based on performance thresholds."""

        def check_response_time(metric_name: str, value: Any):
            if metric_name == "response_time_avg" and isinstance(value, (int, float)):
                if value > self.thresholds.response_time_critical:
                    self._trigger_alert(
                        "critical",
                        "High response time",
                        {
                            "metric": metric_name,
                            "value": value,
                            "threshold": self.thresholds.response_time_critical,
                        },
                    )
                elif value > self.thresholds.response_time_warning:
                    self._trigger_alert(
                        "warning",
                        "Elevated response time",
                        {
                            "metric": metric_name,
                            "value": value,
                            "threshold": self.thresholds.response_time_warning,
                        },
                    )

        def check_error_rate(metric_name: str, value: Any):
            if metric_name == "error_rate" and isinstance(value, (int, float)):
                if value > self.thresholds.error_rate_critical:
                    self._trigger_alert(
                        "critical",
                        "High error rate",
                        {
                            "metric": metric_name,
                            "value": value,
                            "threshold": self.thresholds.error_rate_critical,
                        },
                    )
                elif value > self.thresholds.error_rate_warning:
                    self._trigger_alert(
                        "warning",
                        "Elevated error rate",
                        {
                            "metric": metric_name,
                            "value": value,
                            "threshold": self.thresholds.error_rate_warning,
                        },
                    )

        def check_memory_usage(metric_name: str, value: Any):
            if metric_name == "memory_usage_percent" and isinstance(
                value, (int, float)
            ):
                if value > self.thresholds.memory_usage_critical:
                    self._trigger_alert(
                        "critical",
                        "High memory usage",
                        {
                            "metric": metric_name,
                            "value": value,
                            "threshold": self.thresholds.memory_usage_critical,
                        },
                    )
                elif value > self.thresholds.memory_usage_warning:
                    self._trigger_alert(
                        "warning",
                        "Elevated memory usage",
                        {
                            "metric": metric_name,
                            "value": value,
                            "threshold": self.thresholds.memory_usage_warning,
                        },
                    )

        # Register callbacks
        self.metrics_collector.add_metric_callback(
            "response_time_avg", check_response_time
        )
        self.metrics_collector.add_metric_callback("error_rate", check_error_rate)
        self.metrics_collector.add_metric_callback(
            "memory_usage_percent", check_memory_usage
        )

    def _trigger_alert(self, severity: str, message: str, details: dict[str, Any]):
        """Trigger an alert."""
        logger.warning(f"Performance alert ({severity}): {message} - {details}")

        for callback in self.alert_callbacks:
            try:
                callback(severity, message, details)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def add_alert_callback(self, callback: Callable[[str, str, dict[str, Any]], None]):
        """Add an alert callback."""
        self.alert_callbacks.append(callback)

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "performance": self.metrics_collector.get_performance_metrics().to_dict(),
            "database": self.metrics_collector.get_database_metrics().to_dict(),
            "cache": self.metrics_collector.get_cache_metrics().to_dict(),
            "errors": self.metrics_collector.get_error_metrics().to_dict(),
            "user_engagement": self.metrics_collector.get_user_engagement_metrics().to_dict(),
            "active_requests": len(self.request_tracker.get_active_requests()),
            "slow_requests": len(self.request_tracker.get_slow_requests()),
            "optimization_suggestions": {
                "database": self.db_tracker.get_query_optimization_suggestions(),
                "cache": self.cache_tracker.get_cache_optimization_suggestions(),
            },
        }

    def stop(self):
        """Stop all monitoring."""
        self.system_monitor.stop_monitoring()
        self.metrics_collector.stop()


# Decorators for automatic performance tracking


def track_performance(endpoint: str | None = None, track_args: bool = False):
    """Decorator to automatically track function performance."""

    def decorator(func):
        nonlocal endpoint
        if endpoint is None:
            endpoint = f"{func.__module__}.{func.__name__}"

        # Store as local variable for type narrowing
        endpoint_str: str = endpoint

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                request_id = f"{endpoint_str}_{int(time.time() * 1000000)}"
                monitor = get_performance_monitor()

                metadata = {}
                if track_args:
                    metadata["args_count"] = len(args)
                    metadata["kwargs_count"] = len(kwargs)

                with monitor.request_tracker.track_request(
                    request_id, endpoint_str, "FUNCTION", **metadata
                ):
                    return await func(*args, **kwargs)

            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            request_id = f"{endpoint_str}_{int(time.time() * 1000000)}"
            monitor = get_performance_monitor()

            metadata = {}
            if track_args:
                metadata["args_count"] = len(args)
                metadata["kwargs_count"] = len(kwargs)

            with monitor.request_tracker.track_request(
                request_id, endpoint_str, "FUNCTION", **metadata
            ):
                return func(*args, **kwargs)

        return sync_wrapper

    return decorator


def track_database_query(query_type: str | None = None):
    """Decorator to automatically track database query performance."""

    def decorator(func):
        nonlocal query_type
        if query_type is None:
            query_type = str(func.__name__)

        # Store as local variable for type narrowing
        query_type_str: str = query_type

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                query_id = f"{query_type_str}_{int(time.time() * 1000000)}"
                monitor = get_performance_monitor()

                with monitor.db_tracker.track_query(query_id, query_type_str):
                    return await func(*args, **kwargs)

            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            query_id = f"{query_type_str}_{int(time.time() * 1000000)}"
            monitor = get_performance_monitor()

            with monitor.db_tracker.track_query(query_id, query_type_str):
                return func(*args, **kwargs)

        return sync_wrapper

    return decorator


# Global performance monitor instance
_global_monitor: PerformanceMonitor | None = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor
