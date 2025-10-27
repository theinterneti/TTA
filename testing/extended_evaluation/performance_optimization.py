"""
Performance Optimization and Caching Framework for TTA Quality Evaluation

Provides intelligent caching, database optimization, response time monitoring,
and performance benchmarking tools for extended session testing.
"""

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import psutil
import yaml

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring and optimization."""

    timestamp: datetime

    # Response time metrics
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    max_response_time: float = 0.0

    # System resource metrics
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0

    # Database performance
    db_query_count: int = 0
    avg_db_query_time: float = 0.0
    db_connection_pool_usage: float = 0.0

    # Cache performance
    cache_hit_rate: float = 0.0
    cache_miss_rate: float = 0.0
    cache_size_mb: float = 0.0

    # API performance
    api_requests_per_minute: float = 0.0
    api_error_rate: float = 0.0
    api_timeout_rate: float = 0.0

    # Session performance
    concurrent_sessions: int = 0
    avg_session_duration: float = 0.0
    session_completion_rate: float = 0.0


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: int | None = None
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl_seconds is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds

    def update_access(self):
        """Update access metadata."""
        self.last_accessed = datetime.now()
        self.access_count += 1


class IntelligentCache:
    """
    Intelligent caching system with LRU eviction, TTL support,
    and performance monitoring.
    """

    def __init__(self, max_size_mb: int = 512, default_ttl_seconds: int = 3600):
        """Initialize intelligent cache."""
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl_seconds = default_ttl_seconds

        # Cache storage
        self.cache: dict[str, CacheEntry] = {}
        self.access_order = deque()  # For LRU eviction

        # Performance tracking
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.current_size_bytes = 0

        logger.info(f"IntelligentCache initialized with {max_size_mb}MB capacity")

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if key in self.cache:
            entry = self.cache[key]

            # Check expiration
            if entry.is_expired():
                await self._remove_entry(key)
                self.misses += 1
                return None

            # Update access and move to end of LRU queue
            entry.update_access()
            self.access_order.remove(key)
            self.access_order.append(key)

            self.hits += 1
            return entry.value

        self.misses += 1
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """Set value in cache."""
        # Calculate size (simplified)
        size_bytes = len(str(value).encode("utf-8"))

        # Check if we need to evict entries
        while (
            self.current_size_bytes + size_bytes > self.max_size_bytes
            and self.access_order
        ):
            await self._evict_lru()

        # If still too large, don't cache
        if size_bytes > self.max_size_bytes:
            logger.warning(f"Cache entry too large: {size_bytes} bytes")
            return False

        # Remove existing entry if present
        if key in self.cache:
            await self._remove_entry(key)

        # Create new entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            ttl_seconds=ttl_seconds or self.default_ttl_seconds,
            size_bytes=size_bytes,
        )

        # Add to cache
        self.cache[key] = entry
        self.access_order.append(key)
        self.current_size_bytes += size_bytes

        return True

    async def _evict_lru(self):
        """Evict least recently used entry."""
        if not self.access_order:
            return

        lru_key = self.access_order.popleft()
        await self._remove_entry(lru_key)
        self.evictions += 1

    async def _remove_entry(self, key: str):
        """Remove entry from cache."""
        if key in self.cache:
            entry = self.cache[key]
            self.current_size_bytes -= entry.size_bytes
            del self.cache[key]

            if key in self.access_order:
                self.access_order.remove(key)

    def get_stats(self) -> dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0

        return {
            "hit_rate": hit_rate,
            "miss_rate": 1.0 - hit_rate,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "entries": len(self.cache),
            "size_mb": self.current_size_bytes / (1024 * 1024),
            "utilization": self.current_size_bytes / self.max_size_bytes,
        }

    async def cleanup_expired(self):
        """Clean up expired entries."""
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]

        for key in expired_keys:
            await self._remove_entry(key)

        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


class DatabaseOptimizer:
    """Database query optimization and connection pooling."""

    def __init__(self, config: dict[str, Any]):
        """Initialize database optimizer."""
        self.config = config
        self.query_stats = defaultdict(list)
        self.connection_pool_stats = {
            "active_connections": 0,
            "idle_connections": 0,
            "total_connections": 0,
        }

        # Query optimization settings
        self.batch_size = config.get("batch_size", 100)
        self.query_timeout = config.get("query_timeout", 30)
        self.enable_query_caching = config.get("enable_query_caching", True)

        logger.info("DatabaseOptimizer initialized")

    async def execute_optimized_query(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        cache_key: str | None = None,
        cache_ttl: int = 300,
    ) -> Any:
        """Execute database query with optimization."""
        start_time = time.time()

        # Check cache first if enabled
        if cache_key and self.enable_query_caching:
            # Would check cache here
            pass

        try:
            # Execute query (simplified - would use actual database connection)
            result = await self._execute_query(query, params)

            # Cache result if specified
            if cache_key and self.enable_query_caching:
                # Would cache result here
                pass

            # Record performance metrics
            execution_time = time.time() - start_time
            self.query_stats[query].append(execution_time)

            return result

        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise

    async def _execute_query(self, query: str, params: dict[str, Any] | None) -> Any:
        """Execute actual database query."""
        # Simplified implementation - would use actual database driver
        await asyncio.sleep(0.01)  # Simulate query execution
        return {"result": "mock_data"}

    async def batch_execute(
        self, queries: list[tuple[str, dict[str, Any]]]
    ) -> list[Any]:
        """Execute multiple queries in batch for efficiency."""
        results = []

        # Group queries by type for optimization
        query_groups = defaultdict(list)
        for i, (query, params) in enumerate(queries):
            query_groups[query].append((i, params))

        # Execute each group
        for query, param_list in query_groups.items():
            # Batch execute similar queries
            batch_results = await self._batch_execute_similar(query, param_list)
            results.extend(batch_results)

        return results

    async def _batch_execute_similar(
        self, query: str, param_list: list[tuple[int, dict[str, Any]]]
    ) -> list[Any]:
        """Execute batch of similar queries."""
        # Simplified implementation
        results = []
        for index, params in param_list:
            result = await self._execute_query(query, params)
            results.append((index, result))

        return results

    def get_performance_stats(self) -> dict[str, Any]:
        """Get database performance statistics."""
        stats = {
            "query_count": sum(len(times) for times in self.query_stats.values()),
            "avg_query_time": 0.0,
            "slow_queries": 0,
            "connection_pool": self.connection_pool_stats,
        }

        # Calculate average query time
        all_times = [time for times in self.query_stats.values() for time in times]
        if all_times:
            stats["avg_query_time"] = statistics.mean(all_times)
            stats["slow_queries"] = len([t for t in all_times if t > 1.0])  # > 1 second

        return stats


class ResponseTimeMonitor:
    """Monitor and alert on response time performance."""

    def __init__(self, config: dict[str, Any]):
        """Initialize response time monitor."""
        self.config = config
        self.response_times = deque(maxlen=1000)  # Keep last 1000 response times
        self.alerts_sent = []

        # Alert thresholds
        self.warning_threshold = config.get("warning_threshold", 5.0)  # seconds
        self.critical_threshold = config.get("critical_threshold", 10.0)  # seconds
        self.alert_cooldown = config.get("alert_cooldown", 300)  # seconds

        logger.info("ResponseTimeMonitor initialized")

    async def record_response_time(self, response_time: float, context: dict[str, Any]):
        """Record response time measurement."""
        self.response_times.append(
            {"time": response_time, "timestamp": datetime.now(), "context": context}
        )

        # Check for alerts
        await self._check_alerts(response_time, context)

    async def _check_alerts(self, response_time: float, context: dict[str, Any]):
        """Check if alerts should be sent."""
        alert_level = None

        if response_time > self.critical_threshold:
            alert_level = "critical"
        elif response_time > self.warning_threshold:
            alert_level = "warning"

        if alert_level:
            # Check cooldown
            last_alert = self._get_last_alert(alert_level)
            if (
                not last_alert
                or (datetime.now() - last_alert).total_seconds() > self.alert_cooldown
            ):
                await self._send_alert(alert_level, response_time, context)

    def _get_last_alert(self, alert_level: str) -> datetime | None:
        """Get timestamp of last alert of given level."""
        for alert in reversed(self.alerts_sent):
            if alert["level"] == alert_level:
                return alert["timestamp"]
        return None

    async def _send_alert(
        self, level: str, response_time: float, context: dict[str, Any]
    ):
        """Send performance alert."""
        alert = {
            "level": level,
            "timestamp": datetime.now(),
            "response_time": response_time,
            "context": context,
            "message": f"{level.upper()}: Response time {response_time:.2f}s exceeds threshold",
        }

        self.alerts_sent.append(alert)
        logger.warning(f"Performance alert: {alert['message']}")

        # In real implementation, would send to monitoring system

    def get_performance_summary(self) -> dict[str, Any]:
        """Get response time performance summary."""
        if not self.response_times:
            return {"no_data": True}

        times = [entry["time"] for entry in self.response_times]

        return {
            "count": len(times),
            "avg": statistics.mean(times),
            "median": statistics.median(times),
            "p95": self._percentile(times, 95),
            "p99": self._percentile(times, 99),
            "max": max(times),
            "min": min(times),
            "alerts_sent": len(self.alerts_sent),
        }

    def _percentile(self, data: list[float], percentile: int) -> float:
        """Calculate percentile of data."""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


class PerformanceOptimizationFramework:
    """
    Comprehensive performance optimization framework for TTA extended sessions.

    Provides intelligent caching, database optimization, monitoring, and
    performance benchmarking capabilities.
    """

    def __init__(self, config_path: str | None = None):
        """Initialize performance optimization framework."""
        self.config_path = (
            config_path or "testing/configs/performance_optimization_config.yaml"
        )
        self.config = self._load_config()

        # Initialize components
        self.cache = IntelligentCache(
            max_size_mb=self.config.get("cache", {}).get("max_size_mb", 512),
            default_ttl_seconds=self.config.get("cache", {}).get("default_ttl", 3600),
        )

        self.db_optimizer = DatabaseOptimizer(self.config.get("database", {}))
        self.response_monitor = ResponseTimeMonitor(self.config.get("monitoring", {}))

        # Performance tracking
        self.performance_history: list[PerformanceMetrics] = []
        self.optimization_recommendations: list[str] = []

        # Background tasks
        self.cleanup_task = None
        self.monitoring_task = None

        logger.info("PerformanceOptimizationFramework initialized")

    def _load_config(self) -> dict[str, Any]:
        """Load performance optimization configuration."""
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded performance config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default performance configuration."""
        return {
            "cache": {"max_size_mb": 512, "default_ttl": 3600, "cleanup_interval": 300},
            "database": {
                "batch_size": 100,
                "query_timeout": 30,
                "enable_query_caching": True,
            },
            "monitoring": {
                "warning_threshold": 5.0,
                "critical_threshold": 10.0,
                "alert_cooldown": 300,
            },
        }

    async def start_optimization(self):
        """Start performance optimization background tasks."""
        # Start cache cleanup task
        self.cleanup_task = asyncio.create_task(self._cache_cleanup_loop())

        # Start performance monitoring task
        self.monitoring_task = asyncio.create_task(self._performance_monitoring_loop())

        logger.info("Performance optimization started")

    async def stop_optimization(self):
        """Stop performance optimization background tasks."""
        if self.cleanup_task:
            self.cleanup_task.cancel()

        if self.monitoring_task:
            self.monitoring_task.cancel()

        logger.info("Performance optimization stopped")

    async def _cache_cleanup_loop(self):
        """Background task for cache cleanup."""
        cleanup_interval = self.config.get("cache", {}).get("cleanup_interval", 300)

        while True:
            try:
                await asyncio.sleep(cleanup_interval)
                await self.cache.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")

    async def _performance_monitoring_loop(self):
        """Background task for performance monitoring."""
        monitoring_interval = 60  # Monitor every minute

        while True:
            try:
                await asyncio.sleep(monitoring_interval)
                await self._collect_performance_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")

    async def _collect_performance_metrics(self):
        """Collect current performance metrics."""
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()

        # Cache metrics
        cache_stats = self.cache.get_stats()

        # Database metrics
        db_stats = self.db_optimizer.get_performance_stats()

        # Response time metrics
        response_stats = self.response_monitor.get_performance_summary()

        # Create performance metrics
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_usage_percent=cpu_percent,
            memory_usage_percent=memory.percent,
            memory_usage_mb=memory.used / (1024 * 1024),
            cache_hit_rate=cache_stats.get("hit_rate", 0.0),
            cache_miss_rate=cache_stats.get("miss_rate", 0.0),
            cache_size_mb=cache_stats.get("size_mb", 0.0),
            avg_db_query_time=db_stats.get("avg_query_time", 0.0),
            db_query_count=db_stats.get("query_count", 0),
            avg_response_time=response_stats.get("avg", 0.0)
            if "avg" in response_stats
            else 0.0,
            p95_response_time=response_stats.get("p95", 0.0)
            if "p95" in response_stats
            else 0.0,
            p99_response_time=response_stats.get("p99", 0.0)
            if "p99" in response_stats
            else 0.0,
        )

        self.performance_history.append(metrics)

        # Keep only last 24 hours of metrics
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.performance_history = [
            m for m in self.performance_history if m.timestamp > cutoff_time
        ]

        # Generate optimization recommendations
        await self._generate_optimization_recommendations(metrics)

    async def _generate_optimization_recommendations(self, metrics: PerformanceMetrics):
        """Generate optimization recommendations based on metrics."""
        recommendations = []

        # Cache recommendations
        if metrics.cache_hit_rate < 0.8:
            recommendations.append(
                "Consider increasing cache size or TTL to improve hit rate"
            )

        if metrics.cache_size_mb > 400:  # Near capacity
            recommendations.append(
                "Cache approaching capacity - consider increasing size"
            )

        # Memory recommendations
        if metrics.memory_usage_percent > 80:
            recommendations.append(
                "High memory usage detected - consider memory optimization"
            )

        # Response time recommendations
        if metrics.avg_response_time > 3.0:
            recommendations.append(
                "High average response time - investigate bottlenecks"
            )

        # Database recommendations
        if metrics.avg_db_query_time > 0.5:
            recommendations.append(
                "Slow database queries detected - consider query optimization"
            )

        # Update recommendations (keep only recent ones)
        self.optimization_recommendations.extend(recommendations)
        self.optimization_recommendations = self.optimization_recommendations[
            -10:
        ]  # Keep last 10

    async def get_performance_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.performance_history:
            return {"error": "No performance data available"}

        recent_metrics = self.performance_history[-1]

        # Calculate trends
        if len(self.performance_history) >= 2:
            previous_metrics = self.performance_history[-2]
            trends = {
                "response_time_trend": recent_metrics.avg_response_time
                - previous_metrics.avg_response_time,
                "memory_trend": recent_metrics.memory_usage_percent
                - previous_metrics.memory_usage_percent,
                "cache_hit_rate_trend": recent_metrics.cache_hit_rate
                - previous_metrics.cache_hit_rate,
            }
        else:
            trends = {}

        return {
            "timestamp": recent_metrics.timestamp.isoformat(),
            "current_metrics": {
                "avg_response_time": recent_metrics.avg_response_time,
                "p95_response_time": recent_metrics.p95_response_time,
                "memory_usage_percent": recent_metrics.memory_usage_percent,
                "cpu_usage_percent": recent_metrics.cpu_usage_percent,
                "cache_hit_rate": recent_metrics.cache_hit_rate,
                "cache_size_mb": recent_metrics.cache_size_mb,
            },
            "trends": trends,
            "recommendations": self.optimization_recommendations,
            "cache_stats": self.cache.get_stats(),
            "database_stats": self.db_optimizer.get_performance_stats(),
            "response_time_stats": self.response_monitor.get_performance_summary(),
        }
