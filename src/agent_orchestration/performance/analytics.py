"""
Performance analytics and bottleneck identification algorithms.

This module provides advanced analytics for identifying performance bottlenecks,
predicting performance issues, and generating optimization recommendations.
"""
from __future__ import annotations

import asyncio
import logging
import time
import statistics
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

from .response_time_monitor import ResponseTimeMonitor, ResponseTimeMetric, OperationType, PerformanceLevel

logger = logging.getLogger(__name__)


class BottleneckType(str, Enum):
    """Types of performance bottlenecks."""
    AGENT_OVERLOAD = "agent_overload"
    WORKFLOW_CONGESTION = "workflow_congestion"
    DATABASE_LATENCY = "database_latency"
    NETWORK_DELAY = "network_delay"
    RESOURCE_CONTENTION = "resource_contention"
    INEFFICIENT_ALGORITHM = "inefficient_algorithm"
    MEMORY_PRESSURE = "memory_pressure"
    CONCURRENT_LIMIT = "concurrent_limit"


class TrendDirection(str, Enum):
    """Performance trend directions."""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    VOLATILE = "volatile"


@dataclass
class BottleneckIdentification:
    """Identified performance bottleneck."""
    bottleneck_type: BottleneckType
    severity: float  # 0.0 to 1.0
    affected_operations: List[OperationType]
    description: str
    evidence: Dict[str, Any]
    recommendations: List[str]
    estimated_impact: float  # Estimated performance improvement if resolved
    confidence: float  # 0.0 to 1.0


@dataclass
class PerformanceTrend:
    """Performance trend analysis."""
    operation_type: OperationType
    trend_direction: TrendDirection
    trend_strength: float  # 0.0 to 1.0
    current_performance: float
    predicted_performance: float
    time_horizon_minutes: int
    confidence: float


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation."""
    recommendation_id: str
    title: str
    description: str
    priority: int  # 1 (highest) to 5 (lowest)
    estimated_improvement: float  # Expected performance improvement
    implementation_effort: str  # "low", "medium", "high"
    affected_components: List[str]
    prerequisites: List[str]
    risks: List[str]


class PerformanceAnalytics:
    """Advanced performance analytics and bottleneck identification."""
    
    def __init__(
        self,
        response_time_monitor: ResponseTimeMonitor,
        analysis_window_minutes: int = 30,
        trend_analysis_points: int = 10
    ):
        self.response_time_monitor = response_time_monitor
        self.analysis_window_minutes = analysis_window_minutes
        self.trend_analysis_points = trend_analysis_points
        
        # Analytics state
        self.bottleneck_history: deque[BottleneckIdentification] = deque(maxlen=100)
        self.trend_history: Dict[OperationType, deque[float]] = defaultdict(
            lambda: deque(maxlen=trend_analysis_points)
        )
        self.last_analysis_time: float = 0.0
        
        # Performance baselines
        self.performance_baselines: Dict[OperationType, float] = {}
        self.baseline_calculation_window: int = 1440  # 24 hours in minutes
        
        logger.info("PerformanceAnalytics initialized")
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """Perform comprehensive performance analysis."""
        current_time = time.time()
        
        # Get recent performance statistics
        statistics = self.response_time_monitor.get_statistics(
            time_window_minutes=self.analysis_window_minutes
        )
        
        if not statistics:
            return {
                "bottlenecks": [],
                "trends": [],
                "recommendations": [],
                "overall_health": "no_data"
            }
        
        # Identify bottlenecks
        bottlenecks = await self._identify_bottlenecks(statistics)
        
        # Analyze trends
        trends = await self._analyze_trends(statistics)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(bottlenecks, trends, statistics)
        
        # Calculate overall health score
        overall_health = self._calculate_health_score(statistics, bottlenecks)
        
        self.last_analysis_time = current_time
        
        return {
            "bottlenecks": [self._bottleneck_to_dict(b) for b in bottlenecks],
            "trends": [self._trend_to_dict(t) for t in trends],
            "recommendations": [self._recommendation_to_dict(r) for r in recommendations],
            "overall_health": overall_health,
            "analysis_timestamp": current_time,
            "analysis_window_minutes": self.analysis_window_minutes
        }
    
    async def _identify_bottlenecks(
        self,
        statistics: Dict[OperationType, Any]
    ) -> List[BottleneckIdentification]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        for op_type, stats in statistics.items():
            # Check for various bottleneck patterns
            bottlenecks.extend(await self._check_agent_overload(op_type, stats))
            bottlenecks.extend(await self._check_workflow_congestion(op_type, stats))
            bottlenecks.extend(await self._check_database_latency(op_type, stats))
            bottlenecks.extend(await self._check_resource_contention(op_type, stats))
        
        # Sort by severity
        bottlenecks.sort(key=lambda b: b.severity, reverse=True)
        
        # Store in history
        for bottleneck in bottlenecks[:5]:  # Keep top 5
            self.bottleneck_history.append(bottleneck)
        
        return bottlenecks
    
    async def _check_agent_overload(
        self,
        operation_type: OperationType,
        stats: Any
    ) -> List[BottleneckIdentification]:
        """Check for agent overload bottlenecks."""
        bottlenecks = []
        
        # High average response time with low success rate indicates overload
        if (stats.average_duration > 3.0 and 
            stats.success_rate < 0.9 and 
            stats.total_operations > 10):
            
            severity = min(1.0, (stats.average_duration - 2.0) / 3.0)
            
            bottleneck = BottleneckIdentification(
                bottleneck_type=BottleneckType.AGENT_OVERLOAD,
                severity=severity,
                affected_operations=[operation_type],
                description=f"Agent overload detected for {operation_type.value} operations",
                evidence={
                    "average_duration": stats.average_duration,
                    "success_rate": stats.success_rate,
                    "total_operations": stats.total_operations,
                    "p95_duration": stats.p95_duration
                },
                recommendations=[
                    "Increase agent instance count",
                    "Implement request queuing and throttling",
                    "Optimize agent processing algorithms",
                    "Add circuit breaker patterns"
                ],
                estimated_impact=0.4,  # 40% improvement expected
                confidence=0.8
            )
            
            bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    async def _check_workflow_congestion(
        self,
        operation_type: OperationType,
        stats: Any
    ) -> List[BottleneckIdentification]:
        """Check for workflow congestion bottlenecks."""
        bottlenecks = []
        
        # High P95 with acceptable average suggests congestion
        if (operation_type == OperationType.WORKFLOW_EXECUTION and
            stats.p95_duration > 4.0 and 
            stats.average_duration < 2.0):
            
            severity = min(1.0, (stats.p95_duration - 2.0) / 8.0)
            
            bottleneck = BottleneckIdentification(
                bottleneck_type=BottleneckType.WORKFLOW_CONGESTION,
                severity=severity,
                affected_operations=[operation_type],
                description="Workflow congestion causing high tail latencies",
                evidence={
                    "p95_duration": stats.p95_duration,
                    "average_duration": stats.average_duration,
                    "p99_duration": stats.p99_duration,
                    "performance_distribution": stats.performance_distribution
                },
                recommendations=[
                    "Implement workflow prioritization",
                    "Add concurrent workflow limits",
                    "Optimize workflow scheduling",
                    "Implement workflow batching"
                ],
                estimated_impact=0.3,
                confidence=0.7
            )
            
            bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    async def _check_database_latency(
        self,
        operation_type: OperationType,
        stats: Any
    ) -> List[BottleneckIdentification]:
        """Check for database latency bottlenecks."""
        bottlenecks = []
        
        # Database operations with consistently high latency
        if (operation_type == OperationType.DATABASE_OPERATION and
            stats.median_duration > 1.0 and
            stats.min_duration > 0.5):
            
            severity = min(1.0, stats.median_duration / 5.0)
            
            bottleneck = BottleneckIdentification(
                bottleneck_type=BottleneckType.DATABASE_LATENCY,
                severity=severity,
                affected_operations=[operation_type],
                description="Database operations showing consistently high latency",
                evidence={
                    "median_duration": stats.median_duration,
                    "min_duration": stats.min_duration,
                    "max_duration": stats.max_duration,
                    "total_operations": stats.total_operations
                },
                recommendations=[
                    "Optimize database queries",
                    "Add database connection pooling",
                    "Implement query caching",
                    "Consider database indexing improvements"
                ],
                estimated_impact=0.5,
                confidence=0.9
            )
            
            bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    async def _check_resource_contention(
        self,
        operation_type: OperationType,
        stats: Any
    ) -> List[BottleneckIdentification]:
        """Check for resource contention bottlenecks."""
        bottlenecks = []
        
        # High variance in response times suggests contention
        if stats.total_operations > 5:
            variance_indicator = (stats.max_duration - stats.min_duration) / stats.average_duration
            
            if variance_indicator > 3.0 and stats.average_duration > 1.0:
                severity = min(1.0, variance_indicator / 10.0)
                
                bottleneck = BottleneckIdentification(
                    bottleneck_type=BottleneckType.RESOURCE_CONTENTION,
                    severity=severity,
                    affected_operations=[operation_type],
                    description=f"High variance in {operation_type.value} response times indicates resource contention",
                    evidence={
                        "variance_indicator": variance_indicator,
                        "min_duration": stats.min_duration,
                        "max_duration": stats.max_duration,
                        "average_duration": stats.average_duration
                    },
                    recommendations=[
                        "Implement resource pooling",
                        "Add resource usage monitoring",
                        "Optimize resource allocation algorithms",
                        "Consider horizontal scaling"
                    ],
                    estimated_impact=0.25,
                    confidence=0.6
                )
                
                bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    async def _analyze_trends(
        self,
        statistics: Dict[OperationType, Any]
    ) -> List[PerformanceTrend]:
        """Analyze performance trends."""
        trends = []
        
        for op_type, stats in statistics.items():
            # Update trend history
            self.trend_history[op_type].append(stats.average_duration)
            
            if len(self.trend_history[op_type]) >= 3:
                trend = self._calculate_trend(op_type, list(self.trend_history[op_type]))
                if trend:
                    trends.append(trend)
        
        return trends
    
    def _calculate_trend(
        self,
        operation_type: OperationType,
        data_points: List[float]
    ) -> Optional[PerformanceTrend]:
        """Calculate trend for a series of data points."""
        if len(data_points) < 3:
            return None
        
        # Simple linear regression for trend
        n = len(data_points)
        x_values = list(range(n))
        
        # Calculate slope
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(data_points)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, data_points))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Determine trend direction and strength
        if abs(slope) < 0.01:  # Minimal change
            trend_direction = TrendDirection.STABLE
            trend_strength = 0.0
        elif slope > 0:
            trend_direction = TrendDirection.DEGRADING
            trend_strength = min(1.0, abs(slope) * 10)
        else:
            trend_direction = TrendDirection.IMPROVING
            trend_strength = min(1.0, abs(slope) * 10)
        
        # Check for volatility
        if statistics.stdev(data_points) > y_mean * 0.5:
            trend_direction = TrendDirection.VOLATILE
            trend_strength = statistics.stdev(data_points) / y_mean
        
        # Predict future performance
        predicted_performance = data_points[-1] + slope * 5  # 5 time periods ahead
        
        return PerformanceTrend(
            operation_type=operation_type,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            current_performance=data_points[-1],
            predicted_performance=max(0, predicted_performance),
            time_horizon_minutes=5 * self.analysis_window_minutes // len(data_points),
            confidence=min(1.0, len(data_points) / self.trend_analysis_points)
        )
    
    async def _generate_recommendations(
        self,
        bottlenecks: List[BottleneckIdentification],
        trends: List[PerformanceTrend],
        statistics: Dict[OperationType, Any]
    ) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # High-priority recommendations based on bottlenecks
        for bottleneck in bottlenecks[:3]:  # Top 3 bottlenecks
            if bottleneck.severity > 0.7:
                rec = OptimizationRecommendation(
                    recommendation_id=f"bottleneck_{bottleneck.bottleneck_type.value}",
                    title=f"Address {bottleneck.bottleneck_type.value.replace('_', ' ').title()}",
                    description=bottleneck.description,
                    priority=1,
                    estimated_improvement=bottleneck.estimated_impact,
                    implementation_effort="medium",
                    affected_components=[op.value for op in bottleneck.affected_operations],
                    prerequisites=[],
                    risks=["Temporary performance impact during implementation"]
                )
                recommendations.append(rec)
        
        # Trend-based recommendations
        degrading_trends = [t for t in trends if t.trend_direction == TrendDirection.DEGRADING]
        if degrading_trends:
            rec = OptimizationRecommendation(
                recommendation_id="trend_degradation",
                title="Address Performance Degradation Trends",
                description="Multiple operations showing degrading performance trends",
                priority=2,
                estimated_improvement=0.2,
                implementation_effort="low",
                affected_components=[t.operation_type.value for t in degrading_trends],
                prerequisites=["Performance monitoring dashboard"],
                risks=["May require ongoing monitoring"]
            )
            recommendations.append(rec)
        
        # General optimization recommendations
        overall_p95 = statistics.mean([s.p95_duration for s in statistics.values()])
        if overall_p95 > 2.0:
            rec = OptimizationRecommendation(
                recommendation_id="general_optimization",
                title="Implement General Performance Optimizations",
                description="Overall system performance below SLA targets",
                priority=3,
                estimated_improvement=0.3,
                implementation_effort="high",
                affected_components=["all"],
                prerequisites=["Performance baseline establishment"],
                risks=["System-wide changes may introduce instability"]
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _calculate_health_score(
        self,
        statistics: Dict[OperationType, Any],
        bottlenecks: List[BottleneckIdentification]
    ) -> str:
        """Calculate overall system health score."""
        if not statistics:
            return "no_data"
        
        # Calculate SLA compliance rate
        sla_compliant = sum(1 for s in statistics.values() if s.meets_sla)
        sla_rate = sla_compliant / len(statistics)
        
        # Factor in bottleneck severity
        max_bottleneck_severity = max([b.severity for b in bottlenecks], default=0.0)
        
        # Calculate composite health score
        health_score = sla_rate * (1 - max_bottleneck_severity * 0.5)
        
        if health_score >= 0.9:
            return "excellent"
        elif health_score >= 0.7:
            return "good"
        elif health_score >= 0.5:
            return "fair"
        elif health_score >= 0.3:
            return "poor"
        else:
            return "critical"
    
    def _bottleneck_to_dict(self, bottleneck: BottleneckIdentification) -> Dict[str, Any]:
        """Convert bottleneck to dictionary."""
        return {
            "type": bottleneck.bottleneck_type.value,
            "severity": bottleneck.severity,
            "affected_operations": [op.value for op in bottleneck.affected_operations],
            "description": bottleneck.description,
            "evidence": bottleneck.evidence,
            "recommendations": bottleneck.recommendations,
            "estimated_impact": bottleneck.estimated_impact,
            "confidence": bottleneck.confidence
        }
    
    def _trend_to_dict(self, trend: PerformanceTrend) -> Dict[str, Any]:
        """Convert trend to dictionary."""
        return {
            "operation_type": trend.operation_type.value,
            "trend_direction": trend.trend_direction.value,
            "trend_strength": trend.trend_strength,
            "current_performance": trend.current_performance,
            "predicted_performance": trend.predicted_performance,
            "time_horizon_minutes": trend.time_horizon_minutes,
            "confidence": trend.confidence
        }
    
    def _recommendation_to_dict(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "id": recommendation.recommendation_id,
            "title": recommendation.title,
            "description": recommendation.description,
            "priority": recommendation.priority,
            "estimated_improvement": recommendation.estimated_improvement,
            "implementation_effort": recommendation.implementation_effort,
            "affected_components": recommendation.affected_components,
            "prerequisites": recommendation.prerequisites,
            "risks": recommendation.risks
        }
