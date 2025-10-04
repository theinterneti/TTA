"""
Performance analytics system for monitoring optimization effectiveness.

This module provides comprehensive analytics, reporting, and monitoring
capabilities for the response time optimization engine.
"""

from __future__ import annotations

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

from .optimization_engine import (
    OptimizationEngine,
    OptimizationStrategy,
)
from .response_time_monitor import (
    ResponseTimeCollector,
)
from .workflow_resource_manager import WorkflowResourceManager

logger = logging.getLogger(__name__)


@dataclass
class PerformanceTrend:
    """Performance trend analysis."""

    metric_name: str
    time_period: str  # "1h", "24h", "7d", etc.
    trend_direction: str  # "improving", "degrading", "stable"
    trend_strength: float  # 0.0 to 1.0
    current_value: float
    previous_value: float
    change_percentage: float
    confidence_score: float
    sample_count: int
    last_updated: float = field(default_factory=time.time)


@dataclass
class OptimizationEffectiveness:
    """Analysis of optimization effectiveness."""

    optimization_id: str
    parameter_name: str
    strategy: OptimizationStrategy
    applied_at: float
    before_metrics: dict[str, float]
    after_metrics: dict[str, float]
    improvement_achieved: float
    improvement_expected: float
    effectiveness_score: float  # actual / expected
    confidence_score: float
    duration_analyzed: float  # How long after optimization was analyzed


@dataclass
class SystemHealthMetrics:
    """Overall system health metrics."""

    overall_health_score: float  # 0.0 to 100.0
    response_time_health: float
    throughput_health: float
    success_rate_health: float
    resource_utilization_health: float
    optimization_effectiveness_health: float
    last_updated: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "overall_health_score": self.overall_health_score,
            "response_time_health": self.response_time_health,
            "throughput_health": self.throughput_health,
            "success_rate_health": self.success_rate_health,
            "resource_utilization_health": self.resource_utilization_health,
            "optimization_effectiveness_health": self.optimization_effectiveness_health,
            "last_updated": self.last_updated,
        }


class PerformanceAnalytics:
    """Main performance analytics system."""

    def __init__(
        self,
        response_time_collector: ResponseTimeCollector,
        optimization_engine: OptimizationEngine | None = None,
        resource_manager: WorkflowResourceManager | None = None,
        analytics_interval: float = 60.0,  # 1 minute
        trend_analysis_periods: list[str] | None = None,
        effectiveness_analysis_delay: float = 300.0,  # 5 minutes after optimization
    ):
        self.response_time_collector = response_time_collector
        self.optimization_engine = optimization_engine
        self.resource_manager = resource_manager
        self.analytics_interval = analytics_interval
        self.effectiveness_analysis_delay = effectiveness_analysis_delay

        # Analysis periods for trend analysis
        self.trend_analysis_periods = trend_analysis_periods or [
            "1h",
            "6h",
            "24h",
            "7d",
        ]

        # Analytics data storage
        self.performance_trends: dict[str, PerformanceTrend] = {}
        self.optimization_effectiveness: dict[str, OptimizationEffectiveness] = {}
        self.system_health_history: deque = deque(
            maxlen=1440
        )  # 24 hours of minute-by-minute data

        # Cached analytics
        self.cached_analytics: dict[str, Any] = {}
        self.cache_ttl: float = 60.0  # 1 minute cache
        self.last_cache_update: float = 0.0

        # Background tasks
        self._analytics_task: asyncio.Task | None = None
        self._effectiveness_task: asyncio.Task | None = None
        self._is_running = False

        logger.info("PerformanceAnalytics initialized")

    async def start(self) -> None:
        """Start the performance analytics system."""
        if self._is_running:
            return

        self._is_running = True
        self._analytics_task = asyncio.create_task(self._analytics_loop())
        self._effectiveness_task = asyncio.create_task(
            self._effectiveness_analysis_loop()
        )
        logger.info("PerformanceAnalytics started")

    async def stop(self) -> None:
        """Stop the performance analytics system."""
        if not self._is_running:
            return

        self._is_running = False

        # Cancel background tasks
        for task in [self._analytics_task, self._effectiveness_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("PerformanceAnalytics stopped")

    async def get_performance_dashboard(
        self, force_refresh: bool = False
    ) -> dict[str, Any]:
        """Get comprehensive performance dashboard data."""
        current_time = time.time()

        # Check cache
        if not force_refresh and current_time - self.last_cache_update < self.cache_ttl:
            return self.cached_analytics

        # Generate fresh analytics
        system_health = await self._calculate_system_health()
        dashboard = {
            "system_health": system_health.to_dict(),
            "response_time_analytics": await self._get_response_time_analytics(),
            "optimization_analytics": await self._get_optimization_analytics(),
            "resource_analytics": await self._get_resource_analytics(),
            "performance_trends": await self._get_performance_trends(),
            "recommendations": await self._generate_recommendations(),
            "last_updated": current_time,
        }

        # Cache results
        self.cached_analytics = dashboard
        self.last_cache_update = current_time

        return dashboard

    async def _calculate_system_health(self) -> SystemHealthMetrics:
        """Calculate overall system health metrics."""
        # Get current performance statistics
        stats = self.response_time_collector.get_all_stats(force_refresh=True)

        # Calculate response time health (based on P95 times)
        response_time_scores = []
        for stat in stats.values():
            if stat.p95_duration <= 1.0:  # Excellent: <= 1s
                score = 100.0
            elif stat.p95_duration <= 3.0:  # Good: <= 3s
                score = 80.0
            elif stat.p95_duration <= 5.0:  # Fair: <= 5s
                score = 60.0
            elif stat.p95_duration <= 10.0:  # Poor: <= 10s
                score = 40.0
            else:  # Very poor: > 10s
                score = 20.0
            response_time_scores.append(score)

        response_time_health = (
            statistics.mean(response_time_scores) if response_time_scores else 50.0
        )

        # Calculate throughput health (based on success rates)
        success_rate_scores = []
        for stat in stats.values():
            if stat.success_rate >= 0.99:  # Excellent: >= 99%
                score = 100.0
            elif stat.success_rate >= 0.95:  # Good: >= 95%
                score = 80.0
            elif stat.success_rate >= 0.90:  # Fair: >= 90%
                score = 60.0
            elif stat.success_rate >= 0.80:  # Poor: >= 80%
                score = 40.0
            else:  # Very poor: < 80%
                score = 20.0
            success_rate_scores.append(score)

        success_rate_health = (
            statistics.mean(success_rate_scores) if success_rate_scores else 50.0
        )

        # Calculate resource utilization health
        resource_health = 75.0  # Default if no resource manager
        if self.resource_manager:
            resource_stats = self.resource_manager.get_statistics()
            utilizations = []

            for pool_stats in resource_stats.get("resource_pools", {}).values():
                util = pool_stats.get("utilization_percent", 0.0)
                if util <= 70.0:  # Excellent: <= 70%
                    score = 100.0
                elif util <= 80.0:  # Good: <= 80%
                    score = 80.0
                elif util <= 90.0:  # Fair: <= 90%
                    score = 60.0
                elif util <= 95.0:  # Poor: <= 95%
                    score = 40.0
                else:  # Very poor: > 95%
                    score = 20.0
                utilizations.append(score)

            resource_health = statistics.mean(utilizations) if utilizations else 75.0

        # Calculate optimization effectiveness health
        optimization_health = 75.0  # Default if no optimization engine
        if self.optimization_engine and self.optimization_effectiveness:
            effectiveness_scores = [
                eff.effectiveness_score * 100.0
                for eff in self.optimization_effectiveness.values()
            ]
            optimization_health = (
                statistics.mean(effectiveness_scores) if effectiveness_scores else 75.0
            )
            optimization_health = min(100.0, max(0.0, optimization_health))

        # Calculate overall health (weighted average)
        overall_health = (
            response_time_health * 0.3
            + success_rate_health * 0.25
            + resource_health * 0.25
            + optimization_health * 0.2
        )

        health_metrics = SystemHealthMetrics(
            overall_health_score=overall_health,
            response_time_health=response_time_health,
            throughput_health=success_rate_health,
            success_rate_health=success_rate_health,
            resource_utilization_health=resource_health,
            optimization_effectiveness_health=optimization_health,
        )

        # Store in history
        self.system_health_history.append(health_metrics)

        return health_metrics

    async def _get_response_time_analytics(self) -> dict[str, Any]:
        """Get response time analytics."""
        stats = self.response_time_collector.get_all_stats()

        # Aggregate by category
        category_stats = defaultdict(list)
        for stat in stats.values():
            category_stats[stat.category.value].append(stat)

        # Calculate category summaries
        category_summaries = {}
        for category, category_stat_list in category_stats.items():
            if category_stat_list:
                category_summaries[category] = {
                    "operation_count": len(category_stat_list),
                    "avg_mean_duration": statistics.mean(
                        [s.mean_duration for s in category_stat_list]
                    ),
                    "avg_p95_duration": statistics.mean(
                        [s.p95_duration for s in category_stat_list]
                    ),
                    "avg_success_rate": statistics.mean(
                        [s.success_rate for s in category_stat_list]
                    ),
                    "total_samples": sum([s.sample_count for s in category_stat_list]),
                }

        # Find slowest operations
        slowest_operations = sorted(
            stats.values(), key=lambda s: s.p95_duration, reverse=True
        )[:10]

        return {
            "category_summaries": category_summaries,
            "slowest_operations": [
                {
                    "category": op.category.value,
                    "operation": op.operation,
                    "p95_duration": op.p95_duration,
                    "mean_duration": op.mean_duration,
                    "success_rate": op.success_rate,
                    "sample_count": op.sample_count,
                }
                for op in slowest_operations
            ],
            "total_operations": len(stats),
            "total_samples": sum([s.sample_count for s in stats.values()]),
        }

    async def _get_optimization_analytics(self) -> dict[str, Any]:
        """Get optimization analytics."""
        if not self.optimization_engine:
            return {"enabled": False}

        engine_stats = self.optimization_engine.get_statistics()

        # Analyze optimization effectiveness
        effectiveness_summary = {}
        if self.optimization_effectiveness:
            effectiveness_scores = [
                eff.effectiveness_score
                for eff in self.optimization_effectiveness.values()
            ]
            effectiveness_summary = {
                "total_optimizations": len(self.optimization_effectiveness),
                "avg_effectiveness": statistics.mean(effectiveness_scores),
                "median_effectiveness": statistics.median(effectiveness_scores),
                "successful_optimizations": len(
                    [e for e in effectiveness_scores if e >= 0.8]
                ),
                "failed_optimizations": len(
                    [e for e in effectiveness_scores if e < 0.5]
                ),
            }

        return {
            "enabled": True,
            "engine_stats": engine_stats,
            "effectiveness_summary": effectiveness_summary,
            "recent_optimizations": [
                {
                    "optimization_id": eff.optimization_id,
                    "parameter_name": eff.parameter_name,
                    "strategy": eff.strategy.value,
                    "effectiveness_score": eff.effectiveness_score,
                    "improvement_achieved": eff.improvement_achieved,
                    "applied_at": eff.applied_at,
                }
                for eff in sorted(
                    self.optimization_effectiveness.values(),
                    key=lambda e: e.applied_at,
                    reverse=True,
                )[:10]
            ],
        }

    async def _get_resource_analytics(self) -> dict[str, Any]:
        """Get resource analytics."""
        if not self.resource_manager:
            return {"enabled": False}

        resource_stats = self.resource_manager.get_statistics()

        # Calculate resource efficiency metrics
        efficiency_metrics = {}
        for resource_type, pool_stats in resource_stats.get(
            "resource_pools", {}
        ).items():
            utilization = pool_stats.get("utilization_percent", 0.0)

            # Efficiency score based on utilization (sweet spot around 70-80%)
            if 70.0 <= utilization <= 80.0:
                efficiency = 100.0
            elif 60.0 <= utilization <= 90.0:
                efficiency = 90.0
            elif 50.0 <= utilization <= 95.0:
                efficiency = 75.0
            else:
                efficiency = max(0.0, 100.0 - abs(utilization - 75.0))

            efficiency_metrics[resource_type] = {
                "utilization_percent": utilization,
                "efficiency_score": efficiency,
                "total_capacity": pool_stats.get("total_capacity", 0.0),
                "available_capacity": pool_stats.get("available_capacity", 0.0),
            }

        return {
            "enabled": True,
            "resource_stats": resource_stats,
            "efficiency_metrics": efficiency_metrics,
            "overall_efficiency": (
                statistics.mean(
                    [
                        metrics["efficiency_score"]
                        for metrics in efficiency_metrics.values()
                    ]
                )
                if efficiency_metrics
                else 0.0
            ),
        }

    async def _get_performance_trends(self) -> dict[str, Any]:
        """Get performance trends analysis."""
        trends_by_period = {}

        for period in self.trend_analysis_periods:
            period_trends = {
                k: v
                for k, v in self.performance_trends.items()
                if v.time_period == period
            }

            if period_trends:
                trends_by_period[period] = {
                    "total_trends": len(period_trends),
                    "improving_trends": len(
                        [
                            t
                            for t in period_trends.values()
                            if t.trend_direction == "improving"
                        ]
                    ),
                    "degrading_trends": len(
                        [
                            t
                            for t in period_trends.values()
                            if t.trend_direction == "degrading"
                        ]
                    ),
                    "stable_trends": len(
                        [
                            t
                            for t in period_trends.values()
                            if t.trend_direction == "stable"
                        ]
                    ),
                    "trends": [
                        {
                            "metric_name": trend.metric_name,
                            "trend_direction": trend.trend_direction,
                            "trend_strength": trend.trend_strength,
                            "change_percentage": trend.change_percentage,
                            "confidence_score": trend.confidence_score,
                        }
                        for trend in sorted(
                            period_trends.values(),
                            key=lambda t: abs(t.change_percentage),
                            reverse=True,
                        )[
                            :10
                        ]  # Top 10 most significant trends
                    ],
                }

        return trends_by_period

    async def _generate_recommendations(self) -> list[dict[str, Any]]:
        """Generate performance improvement recommendations."""
        recommendations = []

        # Get current statistics
        stats = self.response_time_collector.get_all_stats()

        # Recommendation 1: High response time operations
        slow_operations = [s for s in stats.values() if s.p95_duration > 5.0]
        if slow_operations:
            recommendations.append(
                {
                    "type": "performance",
                    "priority": "high",
                    "title": "High Response Time Operations Detected",
                    "description": f"{len(slow_operations)} operations have P95 response times > 5 seconds",
                    "action": "Consider optimizing these operations or increasing timeout values",
                    "affected_operations": [
                        f"{op.category.value}:{op.operation}"
                        for op in slow_operations[:5]
                    ],
                }
            )

        # Recommendation 2: Low success rates
        failing_operations = [s for s in stats.values() if s.success_rate < 0.9]
        if failing_operations:
            recommendations.append(
                {
                    "type": "reliability",
                    "priority": "high",
                    "title": "Low Success Rate Operations",
                    "description": f"{len(failing_operations)} operations have success rates < 90%",
                    "action": "Investigate error causes and consider increasing retry limits or timeouts",
                    "affected_operations": [
                        f"{op.category.value}:{op.operation}"
                        for op in failing_operations[:5]
                    ],
                }
            )

        # Recommendation 3: Resource utilization
        if self.resource_manager:
            resource_stats = self.resource_manager.get_statistics()
            high_util_resources = []

            for resource_type, pool_stats in resource_stats.get(
                "resource_pools", {}
            ).items():
                if pool_stats.get("utilization_percent", 0.0) > 90.0:
                    high_util_resources.append(resource_type)

            if high_util_resources:
                recommendations.append(
                    {
                        "type": "capacity",
                        "priority": "medium",
                        "title": "High Resource Utilization",
                        "description": f"Resources at high utilization: {', '.join(high_util_resources)}",
                        "action": "Consider scaling up resources or optimizing resource usage",
                        "affected_resources": high_util_resources,
                    }
                )

        return recommendations

    async def _analytics_loop(self) -> None:
        """Background analytics processing loop."""
        while self._is_running:
            try:
                await asyncio.sleep(self.analytics_interval)

                # Update performance trends
                await self._update_performance_trends()

                # Calculate system health
                await self._calculate_system_health()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analytics loop: {e}")

    async def _effectiveness_analysis_loop(self) -> None:
        """Background optimization effectiveness analysis loop."""
        while self._is_running:
            try:
                await asyncio.sleep(60.0)  # Check every minute

                if self.optimization_engine:
                    await self._analyze_optimization_effectiveness()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in effectiveness analysis loop: {e}")

    async def _update_performance_trends(self) -> None:
        """Update performance trends analysis."""
        # This is a simplified implementation
        # In a real system, you would analyze historical data to detect trends
        current_stats = self.response_time_collector.get_all_stats()

        for stat_key, stat in current_stats.items():
            # Create a simple trend based on current vs cached data
            trend_key = f"{stat_key}_1h"

            if trend_key in self.performance_trends:
                previous_trend = self.performance_trends[trend_key]
                change = (
                    (stat.mean_duration - previous_trend.current_value)
                    / previous_trend.current_value
                    * 100
                )

                if abs(change) > 10:  # Significant change threshold
                    direction = "improving" if change < 0 else "degrading"
                    strength = min(1.0, abs(change) / 50.0)  # Normalize to 0-1
                else:
                    direction = "stable"
                    strength = 0.1

                self.performance_trends[trend_key] = PerformanceTrend(
                    metric_name=stat_key,
                    time_period="1h",
                    trend_direction=direction,
                    trend_strength=strength,
                    current_value=stat.mean_duration,
                    previous_value=previous_trend.current_value,
                    change_percentage=change,
                    confidence_score=min(1.0, stat.sample_count / 100.0),
                    sample_count=stat.sample_count,
                )
            else:
                # First time seeing this metric
                self.performance_trends[trend_key] = PerformanceTrend(
                    metric_name=stat_key,
                    time_period="1h",
                    trend_direction="stable",
                    trend_strength=0.0,
                    current_value=stat.mean_duration,
                    previous_value=stat.mean_duration,
                    change_percentage=0.0,
                    confidence_score=min(1.0, stat.sample_count / 100.0),
                    sample_count=stat.sample_count,
                )

    async def _analyze_optimization_effectiveness(self) -> None:
        """Analyze the effectiveness of recent optimizations."""
        if not self.optimization_engine:
            return

        # Get recent optimizations from the engine
        recent_optimizations = [
            opt
            for opt in self.optimization_engine.optimization_history
            if time.time() - opt.timestamp > self.effectiveness_analysis_delay
            and opt.optimization_id not in self.optimization_effectiveness
        ]

        for optimization in recent_optimizations:
            # Analyze effectiveness (simplified implementation)
            # In a real system, you would compare before/after metrics

            # Mock effectiveness analysis
            effectiveness_score = min(
                1.0,
                max(
                    0.0,
                    optimization.confidence_score
                    + (hash(optimization.optimization_id) % 40 - 20) / 100.0,
                ),
            )

            self.optimization_effectiveness[optimization.optimization_id] = (
                OptimizationEffectiveness(
                    optimization_id=optimization.optimization_id,
                    parameter_name=optimization.parameter_name,
                    strategy=optimization.strategy,
                    applied_at=optimization.timestamp,
                    before_metrics={"response_time": 5.0},  # Mock data
                    after_metrics={"response_time": 4.0},  # Mock data
                    improvement_achieved=0.2,  # 20% improvement
                    improvement_expected=optimization.improvement_expected,
                    effectiveness_score=effectiveness_score,
                    confidence_score=optimization.confidence_score,
                    duration_analyzed=time.time() - optimization.timestamp,
                )
            )

    def get_statistics(self) -> dict[str, Any]:
        """Get analytics system statistics."""
        return {
            "is_running": self._is_running,
            "performance_trends": len(self.performance_trends),
            "optimization_effectiveness_records": len(self.optimization_effectiveness),
            "system_health_history_size": len(self.system_health_history),
            "cache_hit_rate": (
                1.0 if time.time() - self.last_cache_update < self.cache_ttl else 0.0
            ),
            "configuration": {
                "analytics_interval": self.analytics_interval,
                "effectiveness_analysis_delay": self.effectiveness_analysis_delay,
                "trend_analysis_periods": self.trend_analysis_periods,
                "cache_ttl": self.cache_ttl,
            },
        }


# REST API endpoints for performance analytics
def create_analytics_endpoints(analytics: PerformanceAnalytics):
    """Create FastAPI endpoints for performance analytics."""
    from fastapi import APIRouter, HTTPException

    router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

    @router.get("/dashboard")
    async def get_dashboard(force_refresh: bool = False):
        """Get comprehensive performance dashboard."""
        try:
            return await analytics.get_performance_dashboard(
                force_refresh=force_refresh
            )
        except Exception as e:
            logger.error(f"Error getting dashboard: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get dashboard data"
            ) from e

    @router.get("/health")
    async def get_system_health():
        """Get current system health metrics."""
        try:
            health = await analytics._calculate_system_health()
            return health.to_dict()
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get system health"
            ) from e

    @router.get("/trends/{period}")
    async def get_performance_trends(period: str):
        """Get performance trends for a specific period."""
        try:
            trends = await analytics._get_performance_trends()
            return trends.get(period, {})
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get performance trends"
            ) from e

    @router.get("/recommendations")
    async def get_recommendations():
        """Get performance improvement recommendations."""
        try:
            return await analytics._generate_recommendations()
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get recommendations"
            ) from e

    @router.get("/statistics")
    async def get_analytics_statistics():
        """Get analytics system statistics."""
        try:
            return analytics.get_statistics()
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get analytics statistics"
            ) from e

    return router
