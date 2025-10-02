"""
Performance Monitoring Service

This module provides real-time performance tracking and metrics collection
for AI models in the TTA platform.
"""

import asyncio
import json
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any

from ..interfaces import IPerformanceMonitor
from ..models import ModelUsageStats, PerformanceMetrics

logger = logging.getLogger(__name__)


class PerformanceMonitor(IPerformanceMonitor):
    """Performance monitoring service for AI models."""

    def __init__(self, redis_client=None, neo4j_driver=None):
        self.redis_client = redis_client
        self.neo4j_driver = neo4j_driver

        # In-memory storage for metrics (fallback if Redis unavailable)
        self._metrics_cache: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._aggregated_stats: dict[str, dict[str, Any]] = {}

        # Configuration
        self.max_metrics_per_model = 1000
        self.aggregation_interval_minutes = 5
        self.retention_days = 30

        # Background tasks
        self._aggregation_task = None
        self._cleanup_task = None
        self._running = False

    async def start(self):
        """Start the performance monitor."""
        self._running = True

        # Start background tasks
        self._aggregation_task = asyncio.create_task(self._aggregation_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("Performance monitor started")

    async def stop(self):
        """Stop the performance monitor."""
        self._running = False

        # Cancel background tasks
        if self._aggregation_task:
            self._aggregation_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

        logger.info("Performance monitor stopped")

    async def record_metrics(self, model_id: str, metrics: dict[str, Any]) -> None:
        """Record performance metrics for a model."""
        try:
            # Create metrics object
            timestamp = datetime.now()

            performance_metrics = PerformanceMetrics(
                model_id=model_id,
                timestamp=timestamp,
                response_time_ms=metrics.get("response_time_ms", 0),
                tokens_per_second=metrics.get("tokens_per_second", 0),
                total_tokens=metrics.get("total_tokens", 0),
                quality_score=metrics.get("quality_score"),
                therapeutic_safety_score=metrics.get("therapeutic_safety_score"),
                memory_usage_mb=metrics.get("memory_usage_mb"),
                gpu_memory_usage_mb=metrics.get("gpu_memory_usage_mb"),
                cpu_usage_percent=metrics.get("cpu_usage_percent"),
                error_count=metrics.get("error_count", 0),
                success_rate=metrics.get("success_rate", 1.0),
                task_type=metrics.get("task_type"),
                context_length_used=metrics.get("context_length_used"),
                metadata=metrics.get("metadata", {}),
            )

            # Store in Redis if available
            if self.redis_client:
                await self._store_metrics_redis(performance_metrics)

            # Store in Neo4j if available
            if self.neo4j_driver:
                await self._store_metrics_neo4j(performance_metrics)

            # Always store in memory cache as fallback
            self._metrics_cache[model_id].append(performance_metrics)

            logger.debug(f"Recorded metrics for model {model_id}")

        except Exception as e:
            logger.error(f"Failed to record metrics for {model_id}: {e}")

    async def get_model_performance(
        self, model_id: str, timeframe_hours: int = 24
    ) -> dict[str, Any]:
        """Get performance metrics for a model over a timeframe."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)

            # Try to get from Redis first
            if self.redis_client:
                metrics = await self._get_metrics_redis(model_id, cutoff_time)
            else:
                # Fallback to memory cache
                all_metrics = list(self._metrics_cache.get(model_id, []))
                metrics = [m for m in all_metrics if m.timestamp > cutoff_time]

            if not metrics:
                return {
                    "model_id": model_id,
                    "timeframe_hours": timeframe_hours,
                    "metrics_count": 0,
                    "message": "No metrics available for the specified timeframe",
                }

            # Calculate aggregated statistics
            stats = self._calculate_aggregated_stats(metrics)
            stats.update(
                {
                    "model_id": model_id,
                    "timeframe_hours": timeframe_hours,
                    "metrics_count": len(metrics),
                    "period_start": min(m.timestamp for m in metrics).isoformat(),
                    "period_end": max(m.timestamp for m in metrics).isoformat(),
                }
            )

            return stats

        except Exception as e:
            logger.error(f"Failed to get performance metrics for {model_id}: {e}")
            return {"error": str(e)}

    async def get_system_performance(self) -> dict[str, Any]:
        """Get overall system performance metrics."""
        try:
            # Get metrics for all models
            all_model_ids = list(self._metrics_cache.keys())

            if self.redis_client:
                # Get all model IDs from Redis
                redis_keys = await self.redis_client.keys("metrics:*")
                redis_model_ids = [key.decode().split(":")[1] for key in redis_keys]
                all_model_ids.extend(redis_model_ids)

            all_model_ids = list(set(all_model_ids))  # Remove duplicates

            system_stats = {
                "total_models": len(all_model_ids),
                "active_models": 0,
                "total_requests": 0,
                "average_response_time_ms": 0,
                "average_quality_score": 0,
                "overall_success_rate": 0,
                "models": {},
            }

            total_response_time = 0
            total_quality_scores = []
            total_success_rates = []
            request_count = 0

            # Aggregate stats from all models
            for model_id in all_model_ids:
                model_stats = await self.get_model_performance(model_id, 1)  # Last hour

                if model_stats.get("metrics_count", 0) > 0:
                    system_stats["active_models"] += 1

                    model_requests = model_stats.get("total_requests", 0)
                    system_stats["total_requests"] += model_requests
                    request_count += model_requests

                    if model_stats.get("average_response_time_ms"):
                        total_response_time += (
                            model_stats["average_response_time_ms"] * model_requests
                        )

                    if model_stats.get("average_quality_score"):
                        total_quality_scores.extend(
                            [model_stats["average_quality_score"]] * model_requests
                        )

                    if model_stats.get("success_rate"):
                        total_success_rates.extend(
                            [model_stats["success_rate"]] * model_requests
                        )

                    system_stats["models"][model_id] = {
                        "requests": model_requests,
                        "avg_response_time_ms": model_stats.get(
                            "average_response_time_ms"
                        ),
                        "success_rate": model_stats.get("success_rate"),
                    }

            # Calculate system averages
            if request_count > 0:
                system_stats["average_response_time_ms"] = (
                    total_response_time / request_count
                )

            if total_quality_scores:
                system_stats["average_quality_score"] = sum(total_quality_scores) / len(
                    total_quality_scores
                )

            if total_success_rates:
                system_stats["overall_success_rate"] = sum(total_success_rates) / len(
                    total_success_rates
                )

            system_stats["timestamp"] = datetime.now().isoformat()

            return system_stats

        except Exception as e:
            logger.error(f"Failed to get system performance: {e}")
            return {"error": str(e)}

    def _calculate_aggregated_stats(
        self, metrics: list[PerformanceMetrics]
    ) -> dict[str, Any]:
        """Calculate aggregated statistics from metrics."""
        if not metrics:
            return {}

        # Response time statistics
        response_times = [m.response_time_ms for m in metrics if m.response_time_ms > 0]

        # Token statistics
        total_tokens = sum(m.total_tokens for m in metrics)
        tokens_per_second = [
            m.tokens_per_second for m in metrics if m.tokens_per_second > 0
        ]

        # Quality scores
        quality_scores = [
            m.quality_score for m in metrics if m.quality_score is not None
        ]
        safety_scores = [
            m.therapeutic_safety_score
            for m in metrics
            if m.therapeutic_safety_score is not None
        ]

        # Success rates
        success_rates = [m.success_rate for m in metrics if m.success_rate is not None]
        error_counts = [m.error_count for m in metrics]

        # Resource usage
        memory_usage = [
            m.memory_usage_mb for m in metrics if m.memory_usage_mb is not None
        ]
        gpu_memory_usage = [
            m.gpu_memory_usage_mb for m in metrics if m.gpu_memory_usage_mb is not None
        ]
        cpu_usage = [
            m.cpu_usage_percent for m in metrics if m.cpu_usage_percent is not None
        ]

        stats = {
            "total_requests": len(metrics),
            "total_tokens": total_tokens,
            "total_errors": sum(error_counts),
        }

        # Response time stats
        if response_times:
            stats.update(
                {
                    "average_response_time_ms": sum(response_times)
                    / len(response_times),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                    "p95_response_time_ms": self._percentile(response_times, 95),
                    "p99_response_time_ms": self._percentile(response_times, 99),
                }
            )

        # Token throughput stats
        if tokens_per_second:
            stats.update(
                {
                    "average_tokens_per_second": sum(tokens_per_second)
                    / len(tokens_per_second),
                    "max_tokens_per_second": max(tokens_per_second),
                }
            )

        # Quality stats
        if quality_scores:
            stats.update(
                {
                    "average_quality_score": sum(quality_scores) / len(quality_scores),
                    "min_quality_score": min(quality_scores),
                    "max_quality_score": max(quality_scores),
                }
            )

        if safety_scores:
            stats.update(
                {
                    "average_safety_score": sum(safety_scores) / len(safety_scores),
                    "min_safety_score": min(safety_scores),
                    "max_safety_score": max(safety_scores),
                }
            )

        # Success rate stats
        if success_rates:
            stats["success_rate"] = sum(success_rates) / len(success_rates)

        # Resource usage stats
        if memory_usage:
            stats.update(
                {
                    "average_memory_usage_mb": sum(memory_usage) / len(memory_usage),
                    "peak_memory_usage_mb": max(memory_usage),
                }
            )

        if gpu_memory_usage:
            stats.update(
                {
                    "average_gpu_memory_usage_mb": sum(gpu_memory_usage)
                    / len(gpu_memory_usage),
                    "peak_gpu_memory_usage_mb": max(gpu_memory_usage),
                }
            )

        if cpu_usage:
            stats.update(
                {
                    "average_cpu_usage_percent": sum(cpu_usage) / len(cpu_usage),
                    "peak_cpu_usage_percent": max(cpu_usage),
                }
            )

        return stats

    def _percentile(self, data: list[float], percentile: int) -> float:
        """Calculate percentile of a list of numbers."""
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]

    async def _store_metrics_redis(self, metrics: PerformanceMetrics):
        """Store metrics in Redis."""
        try:
            key = f"metrics:{metrics.model_id}"
            value = {
                "timestamp": metrics.timestamp.isoformat(),
                "response_time_ms": metrics.response_time_ms,
                "tokens_per_second": metrics.tokens_per_second,
                "total_tokens": metrics.total_tokens,
                "quality_score": metrics.quality_score,
                "therapeutic_safety_score": metrics.therapeutic_safety_score,
                "success_rate": metrics.success_rate,
                "error_count": metrics.error_count,
                "metadata": metrics.metadata,
            }

            # Store as a list with expiration
            await self.redis_client.lpush(key, json.dumps(value))
            await self.redis_client.ltrim(key, 0, self.max_metrics_per_model - 1)
            await self.redis_client.expire(key, self.retention_days * 24 * 3600)

        except Exception as e:
            logger.error(f"Failed to store metrics in Redis: {e}")

    async def _store_metrics_neo4j(self, metrics: PerformanceMetrics):
        """Store metrics in Neo4j."""
        try:
            async with self.neo4j_driver.session() as session:
                query = """
                MERGE (m:Model {id: $model_id})
                CREATE (m)-[:HAS_METRIC]->(metric:PerformanceMetric {
                    timestamp: datetime($timestamp),
                    response_time_ms: $response_time_ms,
                    tokens_per_second: $tokens_per_second,
                    total_tokens: $total_tokens,
                    quality_score: $quality_score,
                    therapeutic_safety_score: $therapeutic_safety_score,
                    success_rate: $success_rate,
                    error_count: $error_count
                })
                """

                await session.run(
                    query,
                    {
                        "model_id": metrics.model_id,
                        "timestamp": metrics.timestamp.isoformat(),
                        "response_time_ms": metrics.response_time_ms,
                        "tokens_per_second": metrics.tokens_per_second,
                        "total_tokens": metrics.total_tokens,
                        "quality_score": metrics.quality_score,
                        "therapeutic_safety_score": metrics.therapeutic_safety_score,
                        "success_rate": metrics.success_rate,
                        "error_count": metrics.error_count,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store metrics in Neo4j: {e}")

    async def _get_metrics_redis(
        self, model_id: str, cutoff_time: datetime
    ) -> list[PerformanceMetrics]:
        """Get metrics from Redis."""
        try:
            key = f"metrics:{model_id}"
            raw_metrics = await self.redis_client.lrange(key, 0, -1)

            metrics = []
            for raw_metric in raw_metrics:
                data = json.loads(raw_metric.decode())
                timestamp = datetime.fromisoformat(data["timestamp"])

                if timestamp > cutoff_time:
                    metric = PerformanceMetrics(
                        model_id=model_id,
                        timestamp=timestamp,
                        response_time_ms=data.get("response_time_ms", 0),
                        tokens_per_second=data.get("tokens_per_second", 0),
                        total_tokens=data.get("total_tokens", 0),
                        quality_score=data.get("quality_score"),
                        therapeutic_safety_score=data.get("therapeutic_safety_score"),
                        success_rate=data.get("success_rate", 1.0),
                        error_count=data.get("error_count", 0),
                        metadata=data.get("metadata", {}),
                    )
                    metrics.append(metric)

            return metrics

        except Exception as e:
            logger.error(f"Failed to get metrics from Redis: {e}")
            return []

    async def _aggregation_loop(self):
        """Background task for aggregating metrics."""
        while self._running:
            try:
                await asyncio.sleep(self.aggregation_interval_minutes * 60)
                await self._aggregate_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in aggregation loop: {e}")

    async def _cleanup_loop(self):
        """Background task for cleaning up old metrics."""
        while self._running:
            try:
                await asyncio.sleep(24 * 3600)  # Run daily
                await self._cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _aggregate_metrics(self):
        """Aggregate metrics for better performance."""
        # This would implement metric aggregation logic
        # For now, just log that aggregation is running
        logger.debug("Running metric aggregation")

    async def _cleanup_old_metrics(self):
        """Clean up old metrics beyond retention period."""
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)

        # Clean up memory cache
        for model_id in list(self._metrics_cache.keys()):
            metrics = self._metrics_cache[model_id]
            # Remove old metrics
            while metrics and metrics[0].timestamp < cutoff_time:
                metrics.popleft()

        logger.debug(f"Cleaned up metrics older than {cutoff_time}")

    async def get_model_usage_stats(
        self, model_id: str, period_hours: int = 24
    ) -> ModelUsageStats:
        """Get usage statistics for a model."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=period_hours)

        performance_data = await self.get_model_performance(model_id, period_hours)

        return ModelUsageStats(
            model_id=model_id,
            period_start=start_time,
            period_end=end_time,
            total_requests=performance_data.get("total_requests", 0),
            successful_requests=performance_data.get("total_requests", 0)
            - performance_data.get("total_errors", 0),
            failed_requests=performance_data.get("total_errors", 0),
            total_tokens_generated=performance_data.get("total_tokens", 0),
            average_tokens_per_request=performance_data.get("total_tokens", 0)
            / max(performance_data.get("total_requests", 1), 1),
            average_response_time_ms=performance_data.get(
                "average_response_time_ms", 0
            ),
            p95_response_time_ms=performance_data.get("p95_response_time_ms", 0),
            average_quality_score=performance_data.get("average_quality_score"),
            peak_memory_usage_mb=performance_data.get("peak_memory_usage_mb"),
            average_cpu_usage_percent=performance_data.get("average_cpu_usage_percent"),
        )
