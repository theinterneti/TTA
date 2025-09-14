"""
Enhanced Therapeutic Monitoring Service

Production-ready therapeutic monitoring service for clinical-grade metrics collection,
analytics, and evidence-based outcome measurements. Integrates with all 9 therapeutic
systems to provide comprehensive clinical insights.
"""

import asyncio
import logging
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC time with timezone awareness."""
    return datetime.now(timezone.utc)


class MetricType(Enum):
    """Types of therapeutic metrics."""

    ENGAGEMENT = "engagement"
    PROGRESS = "progress"
    SAFETY = "safety"
    THERAPEUTIC_VALUE = "therapeutic_value"
    INTERVENTION_EFFECTIVENESS = "intervention_effectiveness"
    EMOTIONAL_REGULATION = "emotional_regulation"
    COPING_SKILLS = "coping_skills"
    THERAPEUTIC_ALLIANCE = "therapeutic_alliance"
    BEHAVIORAL_CHANGE = "behavioral_change"
    CRISIS_RISK = "crisis_risk"


class AnalyticsTimeframe(Enum):
    """Analytics timeframes for reporting."""

    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class OutcomeMeasure(Enum):
    """Evidence-based outcome measures."""

    PHQ9 = "phq9"  # Depression
    GAD7 = "gad7"  # Anxiety
    DASS21 = "dass21"  # Depression, Anxiety, Stress
    WEMWBS = "wemwbs"  # Mental Wellbeing
    THERAPEUTIC_ALLIANCE = "therapeutic_alliance"
    FUNCTIONAL_IMPROVEMENT = "functional_improvement"
    QUALITY_OF_LIFE = "quality_of_life"
    TREATMENT_ADHERENCE = "treatment_adherence"


@dataclass
class MetricDataPoint:
    """Individual metric data point."""

    timestamp: datetime
    value: float
    metric_type: MetricType
    user_id: str
    session_id: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClinicalOutcome:
    """Clinical outcome measurement."""

    outcome_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    measure_type: OutcomeMeasure = OutcomeMeasure.THERAPEUTIC_ALLIANCE
    baseline_score: float | None = None
    current_score: float = 0.0
    target_score: float | None = None
    measurement_date: datetime = field(default_factory=utc_now)
    clinician_notes: str = ""
    validated: bool = False
    improvement_percentage: float | None = None


@dataclass
class AnalyticsReport:
    """Clinical analytics report."""

    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.WEEKLY
    generated_at: datetime = field(default_factory=utc_now)
    metrics_summary: dict[str, Any] = field(default_factory=dict)
    outcome_measures: list[ClinicalOutcome] = field(default_factory=list)
    trends: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    protective_factors: list[str] = field(default_factory=list)


class TherapeuticMonitoringService:
    """
    Enhanced therapeutic monitoring service for clinical-grade metrics collection,
    analytics, and evidence-based outcome measurements.

    Features:
    - Real-time metrics aggregation from all therapeutic systems
    - Clinical analytics and trend analysis
    - Evidence-based outcome measurements
    - Automated report generation
    - Risk factor identification
    - Treatment effectiveness tracking
    """

    def __init__(self) -> None:
        """Initialize the enhanced therapeutic monitoring service."""
        # Metrics storage
        self.metrics_data: dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.outcome_measures: dict[str, list[ClinicalOutcome]] = defaultdict(list)
        self.analytics_reports: dict[str, list[AnalyticsReport]] = defaultdict(list)

        # Aggregated metrics cache
        self.metrics_cache: dict[str, dict[str, Any]] = {}
        self.cache_expiry: dict[str, datetime] = {}
        self.cache_duration = timedelta(minutes=5)

        # Configuration
        self.metrics_retention_days = 90
        self.analytics_update_interval = 300  # 5 minutes
        self.outcome_measurement_frequency = timedelta(weeks=2)

        # Background tasks
        self._analytics_task: asyncio.Task | None = None
        self._cleanup_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

        # Performance metrics
        self.service_metrics = {
            "metrics_collected": 0,
            "analytics_reports_generated": 0,
            "outcome_measures_recorded": 0,
            "trend_analyses_performed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        logger.info("Enhanced TherapeuticMonitoringService initialized")

    async def initialize(self) -> None:
        """Initialize the enhanced therapeutic monitoring service."""
        try:
            logger.info("Initializing Enhanced TherapeuticMonitoringService")

            # Start background tasks
            self._analytics_task = asyncio.create_task(self._analytics_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

            logger.info("Enhanced TherapeuticMonitoringService initialization complete")

        except Exception as e:
            logger.error(f"Error initializing TherapeuticMonitoringService: {e}")
            raise

    async def collect_metric(
        self,
        user_id: str,
        session_id: str,
        metric_type: MetricType,
        value: float,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Collect a therapeutic metric data point."""
        try:
            data_point = MetricDataPoint(
                timestamp=utc_now(),
                value=value,
                metric_type=metric_type,
                user_id=user_id,
                session_id=session_id,
                context=context or {},
            )

            # Store metric
            metric_key = f"{user_id}:{metric_type.value}"
            self.metrics_data[metric_key].append(data_point)

            # Invalidate cache for this user
            self._invalidate_cache(user_id)

            self.service_metrics["metrics_collected"] += 1
            logger.debug(
                f"Collected metric: {metric_type.value} = {value} for user {user_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error collecting metric: {e}")
            return False

    async def record_outcome_measure(
        self,
        user_id: str,
        measure_type: OutcomeMeasure,
        current_score: float,
        baseline_score: float | None = None,
        target_score: float | None = None,
        clinician_notes: str = "",
    ) -> str:
        """Record a clinical outcome measurement."""
        try:
            # Calculate improvement percentage if baseline exists
            improvement_percentage = None
            if baseline_score is not None and baseline_score != 0:
                improvement_percentage = (
                    (current_score - baseline_score) / baseline_score
                ) * 100

            outcome = ClinicalOutcome(
                user_id=user_id,
                measure_type=measure_type,
                baseline_score=baseline_score,
                current_score=current_score,
                target_score=target_score,
                clinician_notes=clinician_notes,
                improvement_percentage=improvement_percentage,
            )

            self.outcome_measures[user_id].append(outcome)
            self.service_metrics["outcome_measures_recorded"] += 1

            logger.info(
                f"Recorded outcome measure: {measure_type.value} = {current_score} for user {user_id}"
            )
            return outcome.outcome_id

        except Exception as e:
            logger.error(f"Error recording outcome measure: {e}")
            return ""

    async def generate_analytics_report(
        self,
        user_id: str,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.WEEKLY,
    ) -> AnalyticsReport | None:
        """Generate comprehensive analytics report for user."""
        try:
            # Check cache first
            cache_key = f"{user_id}:{timeframe.value}"
            if self._is_cache_valid(cache_key):
                self.service_metrics["cache_hits"] += 1
                return self.metrics_cache[cache_key].get("report")

            self.service_metrics["cache_misses"] += 1

            # Calculate timeframe boundaries
            end_time = utc_now()
            start_time = self._get_timeframe_start(end_time, timeframe)

            # Collect metrics for timeframe
            metrics_summary = await self._calculate_metrics_summary(
                user_id, start_time, end_time
            )
            trends = await self._analyze_trends(user_id, start_time, end_time)
            recommendations = await self._generate_recommendations(
                user_id, metrics_summary, trends
            )
            risk_factors, protective_factors = (
                await self._identify_risk_protective_factors(user_id, metrics_summary)
            )

            # Get recent outcome measures
            recent_outcomes = [
                outcome
                for outcome in self.outcome_measures.get(user_id, [])
                if outcome.measurement_date >= start_time
            ]

            report = AnalyticsReport(
                user_id=user_id,
                timeframe=timeframe,
                metrics_summary=metrics_summary,
                outcome_measures=recent_outcomes,
                trends=trends,
                recommendations=recommendations,
                risk_factors=risk_factors,
                protective_factors=protective_factors,
            )

            # Cache report
            self.metrics_cache[cache_key] = {"report": report}
            self.cache_expiry[cache_key] = utc_now() + self.cache_duration

            # Store report
            self.analytics_reports[user_id].append(report)
            self.service_metrics["analytics_reports_generated"] += 1

            logger.info(
                f"Generated analytics report for user {user_id} ({timeframe.value})"
            )
            return report

        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return None

    async def get_real_time_metrics(
        self, user_id: str, metric_types: list[MetricType] | None = None
    ) -> dict[str, Any]:
        """Get real-time metrics for user."""
        try:
            if metric_types is None:
                metric_types = list(MetricType)

            real_time_metrics = {}

            for metric_type in metric_types:
                metric_key = f"{user_id}:{metric_type.value}"
                data_points = list(self.metrics_data.get(metric_key, []))

                if data_points:
                    # Get most recent data point
                    latest = data_points[-1]
                    real_time_metrics[metric_type.value] = {
                        "current_value": latest.value,
                        "timestamp": latest.timestamp.isoformat(),
                        "context": latest.context,
                    }

                    # Calculate recent trend (last 10 data points)
                    if len(data_points) >= 2:
                        recent_values = [dp.value for dp in data_points[-10:]]
                        trend = self._calculate_trend(recent_values)
                        real_time_metrics[metric_type.value]["trend"] = trend

            return real_time_metrics

        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {}

    async def get_outcome_progress(
        self, user_id: str, measure_type: OutcomeMeasure | None = None
    ) -> dict[str, Any]:
        """Get outcome measurement progress for user."""
        try:
            outcomes = self.outcome_measures.get(user_id, [])

            if measure_type:
                outcomes = [o for o in outcomes if o.measure_type == measure_type]

            if not outcomes:
                return {}

            # Sort by measurement date
            outcomes.sort(key=lambda x: x.measurement_date)

            progress_data = {
                "total_measurements": len(outcomes),
                "first_measurement": outcomes[0].measurement_date.isoformat(),
                "latest_measurement": outcomes[-1].measurement_date.isoformat(),
                "measures": {},
            }

            # Group by measure type
            by_measure = defaultdict(list)
            for outcome in outcomes:
                by_measure[outcome.measure_type.value].append(outcome)

            for measure, measure_outcomes in by_measure.items():
                if len(measure_outcomes) >= 2:
                    baseline = measure_outcomes[0].current_score
                    current = measure_outcomes[-1].current_score
                    improvement = (
                        ((current - baseline) / baseline * 100) if baseline != 0 else 0
                    )

                    progress_data["measures"][measure] = {
                        "baseline_score": baseline,
                        "current_score": current,
                        "improvement_percentage": improvement,
                        "measurements_count": len(measure_outcomes),
                        "trend": self._calculate_trend(
                            [o.current_score for o in measure_outcomes]
                        ),
                    }

            return progress_data

        except Exception as e:
            logger.error(f"Error getting outcome progress: {e}")
            return {}

    # Helper Methods

    def _invalidate_cache(self, user_id: str) -> None:
        """Invalidate cache entries for user."""
        keys_to_remove = [
            key for key in self.metrics_cache.keys() if key.startswith(f"{user_id}:")
        ]
        for key in keys_to_remove:
            self.metrics_cache.pop(key, None)
            self.cache_expiry.pop(key, None)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is valid."""
        if cache_key not in self.metrics_cache:
            return False
        if cache_key not in self.cache_expiry:
            return False
        return utc_now() < self.cache_expiry[cache_key]

    def _get_timeframe_start(
        self, end_time: datetime, timeframe: AnalyticsTimeframe
    ) -> datetime:
        """Get start time for analytics timeframe."""
        if timeframe == AnalyticsTimeframe.REAL_TIME:
            return end_time - timedelta(minutes=5)
        elif timeframe == AnalyticsTimeframe.HOURLY:
            return end_time - timedelta(hours=1)
        elif timeframe == AnalyticsTimeframe.DAILY:
            return end_time - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            return end_time - timedelta(weeks=1)
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            return end_time - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.QUARTERLY:
            return end_time - timedelta(days=90)
        else:
            return end_time - timedelta(weeks=1)

    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "stable"

        # Simple linear regression slope
        n = len(values)
        x_values = list(range(n))

        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        # Adjust thresholds based on data range for better sensitivity
        data_range = max(values) - min(values)
        threshold = max(0.01, data_range * 0.1 / n)  # Dynamic threshold

        if slope > threshold:
            return "improving"
        elif slope < -threshold:
            return "declining"
        else:
            return "stable"

    async def _calculate_metrics_summary(
        self, user_id: str, start_time: datetime, end_time: datetime
    ) -> dict[str, Any]:
        """Calculate metrics summary for timeframe."""
        summary = {}

        for metric_type in MetricType:
            metric_key = f"{user_id}:{metric_type.value}"
            data_points = [
                dp
                for dp in self.metrics_data.get(metric_key, [])
                if start_time <= dp.timestamp <= end_time
            ]

            if data_points:
                values = [dp.value for dp in data_points]
                summary[metric_type.value] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
                    "trend": self._calculate_trend(values),
                    "latest_value": values[-1],
                }

        return summary

    async def _analyze_trends(
        self, user_id: str, start_time: datetime, end_time: datetime
    ) -> dict[str, Any]:
        """Analyze trends in metrics."""
        trends = {}

        # Analyze each metric type
        for metric_type in MetricType:
            metric_key = f"{user_id}:{metric_type.value}"
            data_points = [
                dp
                for dp in self.metrics_data.get(metric_key, [])
                if start_time <= dp.timestamp <= end_time
            ]

            if len(data_points) >= 3:
                values = [dp.value for dp in data_points]
                trend_direction = self._calculate_trend(values)

                # Calculate rate of change
                if len(values) >= 2:
                    rate_of_change = (values[-1] - values[0]) / len(values)
                else:
                    rate_of_change = 0.0

                trends[metric_type.value] = {
                    "direction": trend_direction,
                    "rate_of_change": rate_of_change,
                    "volatility": statistics.stdev(values) if len(values) > 1 else 0.0,
                }

        self.service_metrics["trend_analyses_performed"] += 1
        return trends

    async def _generate_recommendations(
        self, user_id: str, metrics_summary: dict[str, Any], trends: dict[str, Any]
    ) -> list[str]:
        """Generate clinical recommendations based on metrics and trends."""
        recommendations = []

        # Safety-related recommendations
        if "safety" in metrics_summary:
            safety_data = metrics_summary["safety"]
            if safety_data["latest_value"] < 0.7:
                recommendations.append(
                    "Consider increasing safety monitoring frequency"
                )
            if trends.get("safety", {}).get("direction") == "declining":
                recommendations.append("Implement additional safety interventions")

        # Engagement recommendations
        if "engagement" in metrics_summary:
            engagement_data = metrics_summary["engagement"]
            if engagement_data["latest_value"] < 0.5:
                recommendations.append("Explore strategies to improve user engagement")
            if trends.get("engagement", {}).get("direction") == "declining":
                recommendations.append("Review and adjust therapeutic approach")

        # Progress recommendations
        if "progress" in metrics_summary:
            progress_data = metrics_summary["progress"]
            if progress_data["latest_value"] < 0.3:
                recommendations.append(
                    "Consider adjusting therapeutic goals or methods"
                )
            if trends.get("progress", {}).get("direction") == "stable":
                recommendations.append(
                    "Introduce new therapeutic challenges or techniques"
                )

        # Crisis risk recommendations
        if "crisis_risk" in metrics_summary:
            crisis_data = metrics_summary["crisis_risk"]
            if crisis_data["latest_value"] > 0.7:
                recommendations.append("Immediate clinical review recommended")
                recommendations.append("Consider crisis intervention protocols")

        return recommendations

    async def _identify_risk_protective_factors(
        self, user_id: str, metrics_summary: dict[str, Any]
    ) -> tuple[list[str], list[str]]:
        """Identify risk and protective factors from metrics."""
        risk_factors = []
        protective_factors = []

        # Analyze metrics for risk factors
        if (
            "safety" in metrics_summary
            and metrics_summary["safety"]["latest_value"] < 0.6
        ):
            risk_factors.append("Low safety scores")

        if (
            "engagement" in metrics_summary
            and metrics_summary["engagement"]["latest_value"] < 0.4
        ):
            risk_factors.append("Poor engagement levels")

        if (
            "crisis_risk" in metrics_summary
            and metrics_summary["crisis_risk"]["latest_value"] > 0.6
        ):
            risk_factors.append("Elevated crisis risk")

        # Analyze metrics for protective factors
        if (
            "therapeutic_alliance" in metrics_summary
            and metrics_summary["therapeutic_alliance"]["latest_value"] > 0.7
        ):
            protective_factors.append("Strong therapeutic alliance")

        if (
            "coping_skills" in metrics_summary
            and metrics_summary["coping_skills"]["latest_value"] > 0.6
        ):
            protective_factors.append("Good coping skills utilization")

        if (
            "progress" in metrics_summary
            and metrics_summary["progress"]["latest_value"] > 0.6
        ):
            protective_factors.append("Consistent therapeutic progress")

        return risk_factors, protective_factors

    # Background Tasks

    async def _analytics_loop(self) -> None:
        """Background loop for periodic analytics updates."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Generate analytics reports for users with recent activity
                    active_users = set()
                    cutoff_time = utc_now() - timedelta(hours=24)

                    # Find users with recent metrics
                    for metric_key, data_points in self.metrics_data.items():
                        user_id = metric_key.split(":")[0]
                        recent_points = [
                            dp for dp in data_points if dp.timestamp > cutoff_time
                        ]
                        if recent_points:
                            active_users.add(user_id)

                    # Generate reports for active users
                    for user_id in active_users:
                        await self.generate_analytics_report(
                            user_id, AnalyticsTimeframe.DAILY
                        )

                    # Wait for next analytics cycle
                    await asyncio.sleep(self.analytics_update_interval)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in analytics loop: {e}")
                    await asyncio.sleep(self.analytics_update_interval)

        except asyncio.CancelledError:
            logger.info("Analytics loop cancelled")

    async def _cleanup_loop(self) -> None:
        """Background loop for cleaning up old data."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    cutoff_time = utc_now() - timedelta(
                        days=self.metrics_retention_days
                    )

                    # Clean up old metrics data
                    for data_points in self.metrics_data.values():
                        # Remove old data points
                        while data_points and data_points[0].timestamp < cutoff_time:
                            data_points.popleft()

                    # Clean up old analytics reports
                    for user_id, reports in self.analytics_reports.items():
                        self.analytics_reports[user_id] = [
                            report
                            for report in reports
                            if report.generated_at > cutoff_time
                        ]

                    # Clean up expired cache entries
                    current_time = utc_now()
                    expired_keys = [
                        key
                        for key, expiry in self.cache_expiry.items()
                        if current_time > expiry
                    ]
                    for key in expired_keys:
                        self.metrics_cache.pop(key, None)
                        self.cache_expiry.pop(key, None)

                    # Wait 24 hours before next cleanup
                    await asyncio.sleep(86400)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in cleanup loop: {e}")
                    await asyncio.sleep(86400)

        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")

    async def health_check(self) -> dict[str, Any]:
        """Perform health check."""
        try:
            return {
                "status": "healthy",
                "service": "therapeutic_monitoring",
                "metrics": {
                    **self.service_metrics,
                    "active_users": len(
                        {key.split(":")[0] for key in self.metrics_data.keys()}
                    ),
                    "total_metrics_stored": sum(
                        len(data) for data in self.metrics_data.values()
                    ),
                    "cache_size": len(self.metrics_cache),
                    "analytics_reports_stored": sum(
                        len(reports) for reports in self.analytics_reports.values()
                    ),
                },
                "background_tasks": {
                    "analytics_task_running": self._analytics_task
                    and not self._analytics_task.done(),
                    "cleanup_task_running": self._cleanup_task
                    and not self._cleanup_task.done(),
                },
            }
        except Exception as e:
            logger.error(f"Error in therapeutic monitoring health check: {e}")
            return {
                "status": "unhealthy",
                "service": "therapeutic_monitoring",
                "error": str(e),
            }

    async def shutdown(self) -> None:
        """Shutdown the therapeutic monitoring service."""
        try:
            logger.info("Shutting down TherapeuticMonitoringService")

            # Signal shutdown
            self._shutdown_event.set()

            # Cancel background tasks
            if self._analytics_task and not self._analytics_task.done():
                self._analytics_task.cancel()
                try:
                    await self._analytics_task
                except asyncio.CancelledError:
                    pass

            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            logger.info("TherapeuticMonitoringService shutdown complete")

        except Exception as e:
            logger.error(f"Error during therapeutic monitoring shutdown: {e}")
            raise

    def get_service_metrics(self) -> dict[str, Any]:
        """Get service performance metrics."""
        return {
            **self.service_metrics,
            "active_users": len(
                {key.split(":")[0] for key in self.metrics_data.keys()}
            ),
            "total_metrics_stored": sum(
                len(data) for data in self.metrics_data.values()
            ),
            "cache_size": len(self.metrics_cache),
            "cache_hit_rate": (
                self.service_metrics["cache_hits"]
                / (
                    self.service_metrics["cache_hits"]
                    + self.service_metrics["cache_misses"]
                )
                if (
                    self.service_metrics["cache_hits"]
                    + self.service_metrics["cache_misses"]
                )
                > 0
                else 0.0
            ),
        }
