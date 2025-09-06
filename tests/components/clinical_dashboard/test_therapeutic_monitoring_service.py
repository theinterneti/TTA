"""
Tests for Enhanced Therapeutic Monitoring Service

This module tests the clinical-grade metrics collection, analytics, and
evidence-based outcome measurements functionality.
"""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio

from src.components.clinical_dashboard.therapeutic_monitoring_service import (
    AnalyticsTimeframe,
    MetricDataPoint,
    MetricType,
    OutcomeMeasure,
    TherapeuticMonitoringService,
)


def utc_now() -> datetime:
    """Get current UTC time with timezone awareness."""
    return datetime.now(timezone.utc)


class TestTherapeuticMonitoringService:
    """Test Enhanced Therapeutic Monitoring Service functionality."""

    @pytest_asyncio.fixture
    async def monitoring_service(self):
        """Create monitoring service instance."""
        service = TherapeuticMonitoringService()
        await service.initialize()
        yield service
        await service.shutdown()

    @pytest.mark.asyncio
    async def test_service_initialization(self, monitoring_service):
        """Test service initialization."""
        # Verify service is initialized
        health = await monitoring_service.health_check()
        assert health["status"] == "healthy"
        assert health["service"] == "therapeutic_monitoring"

        # Verify background tasks are running
        assert health["background_tasks"]["analytics_task_running"] is True
        assert health["background_tasks"]["cleanup_task_running"] is True

        # Verify initial metrics
        metrics = monitoring_service.get_service_metrics()
        assert metrics["metrics_collected"] == 0
        assert metrics["analytics_reports_generated"] == 0
        assert metrics["outcome_measures_recorded"] == 0

    @pytest.mark.asyncio
    async def test_metric_collection(self, monitoring_service):
        """Test therapeutic metric collection."""
        user_id = "test_user_123"
        session_id = "session_456"

        # Collect various metrics
        metrics_to_collect = [
            (MetricType.ENGAGEMENT, 0.85),
            (MetricType.PROGRESS, 0.72),
            (MetricType.SAFETY, 0.95),
            (MetricType.THERAPEUTIC_VALUE, 0.68),
            (MetricType.EMOTIONAL_REGULATION, 0.74),
        ]

        for metric_type, value in metrics_to_collect:
            success = await monitoring_service.collect_metric(
                user_id=user_id,
                session_id=session_id,
                metric_type=metric_type,
                value=value,
                context={"test": True},
            )
            assert success is True

        # Verify metrics were collected
        service_metrics = monitoring_service.get_service_metrics()
        assert service_metrics["metrics_collected"] == len(metrics_to_collect)
        assert service_metrics["active_users"] == 1

        # Verify real-time metrics retrieval
        real_time_metrics = await monitoring_service.get_real_time_metrics(user_id)
        assert len(real_time_metrics) == len(metrics_to_collect)

        for metric_type, expected_value in metrics_to_collect:
            metric_data = real_time_metrics[metric_type.value]
            assert metric_data["current_value"] == expected_value
            assert "timestamp" in metric_data
            assert metric_data["context"]["test"] is True

    @pytest.mark.asyncio
    async def test_outcome_measurement_recording(self, monitoring_service):
        """Test clinical outcome measurement recording."""
        user_id = "test_user_outcome"

        # Record baseline outcome
        baseline_outcome_id = await monitoring_service.record_outcome_measure(
            user_id=user_id,
            measure_type=OutcomeMeasure.PHQ9,
            current_score=15.0,  # Baseline depression score
            baseline_score=15.0,
            target_score=8.0,
            clinician_notes="Initial assessment - moderate depression",
        )

        assert baseline_outcome_id != ""

        # Record follow-up outcome
        followup_outcome_id = await monitoring_service.record_outcome_measure(
            user_id=user_id,
            measure_type=OutcomeMeasure.PHQ9,
            current_score=10.0,  # Improved score
            baseline_score=15.0,
            target_score=8.0,
            clinician_notes="4-week follow-up - showing improvement",
        )

        assert followup_outcome_id != ""
        assert followup_outcome_id != baseline_outcome_id

        # Verify outcome measures were recorded
        service_metrics = monitoring_service.get_service_metrics()
        assert service_metrics["outcome_measures_recorded"] == 2

        # Verify outcome progress tracking
        progress = await monitoring_service.get_outcome_progress(
            user_id, OutcomeMeasure.PHQ9
        )
        assert progress["total_measurements"] == 2
        assert progress["measures"]["phq9"]["baseline_score"] == 15.0
        assert progress["measures"]["phq9"]["current_score"] == 10.0
        assert (
            progress["measures"]["phq9"]["improvement_percentage"] == -33.33333333333333
        )  # Negative because lower PHQ9 is better

    @pytest.mark.asyncio
    async def test_analytics_report_generation(self, monitoring_service):
        """Test comprehensive analytics report generation."""
        user_id = "test_user_analytics"
        session_id = "session_analytics"

        # Collect metrics over time to create trends
        base_time = utc_now() - timedelta(hours=2)

        for i in range(10):
            timestamp_offset = timedelta(minutes=i * 10)

            # Simulate improving engagement over time
            engagement_value = 0.5 + (i * 0.05)  # 0.5 to 0.95

            # Manually create data point with specific timestamp
            data_point = MetricDataPoint(
                timestamp=base_time + timestamp_offset,
                value=engagement_value,
                metric_type=MetricType.ENGAGEMENT,
                user_id=user_id,
                session_id=session_id,
                context={"sequence": i},
            )

            metric_key = f"{user_id}:{MetricType.ENGAGEMENT.value}"
            monitoring_service.metrics_data[metric_key].append(data_point)

        # Generate analytics report
        report = await monitoring_service.generate_analytics_report(
            user_id=user_id, timeframe=AnalyticsTimeframe.DAILY
        )

        assert report is not None
        assert report.user_id == user_id
        assert report.timeframe == AnalyticsTimeframe.DAILY

        # Verify metrics summary
        assert "engagement" in report.metrics_summary
        engagement_summary = report.metrics_summary["engagement"]
        assert engagement_summary["count"] == 10
        assert engagement_summary["trend"] == "improving"
        assert engagement_summary["latest_value"] == 0.95

        # Verify trends analysis
        assert "engagement" in report.trends
        engagement_trend = report.trends["engagement"]
        assert engagement_trend["direction"] == "improving"
        assert engagement_trend["rate_of_change"] > 0

        # Verify recommendations are generated
        assert len(report.recommendations) >= 0  # May be empty if metrics are good

        # Verify service metrics updated
        service_metrics = monitoring_service.get_service_metrics()
        assert service_metrics["analytics_reports_generated"] >= 1

    @pytest.mark.asyncio
    async def test_trend_analysis(self, monitoring_service):
        """Test trend analysis functionality."""
        # Test improving trend
        improving_values = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        trend = monitoring_service._calculate_trend(improving_values)
        assert trend == "improving"

        # Test declining trend
        declining_values = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
        trend = monitoring_service._calculate_trend(declining_values)
        assert trend == "declining"

        # Test stable trend
        stable_values = [0.5, 0.51, 0.49, 0.5, 0.52, 0.48]
        trend = monitoring_service._calculate_trend(stable_values)
        assert trend == "stable"

        # Test insufficient data
        insufficient_values = [0.5]
        trend = monitoring_service._calculate_trend(insufficient_values)
        assert trend == "stable"

    @pytest.mark.asyncio
    async def test_risk_protective_factor_identification(self, monitoring_service):
        """Test risk and protective factor identification."""
        user_id = "test_user_risk"

        # Create metrics summary with risk factors
        metrics_summary = {
            "safety": {"latest_value": 0.4},  # Low safety - risk factor
            "engagement": {"latest_value": 0.3},  # Poor engagement - risk factor
            "crisis_risk": {"latest_value": 0.8},  # High crisis risk - risk factor
            "therapeutic_alliance": {
                "latest_value": 0.8
            },  # Strong alliance - protective
            "coping_skills": {"latest_value": 0.7},  # Good coping - protective
            "progress": {"latest_value": 0.7},  # Good progress - protective
        }

        (
            risk_factors,
            protective_factors,
        ) = await monitoring_service._identify_risk_protective_factors(
            user_id, metrics_summary
        )

        # Verify risk factors identified
        assert "Low safety scores" in risk_factors
        assert "Poor engagement levels" in risk_factors
        assert "Elevated crisis risk" in risk_factors

        # Verify protective factors identified
        assert "Strong therapeutic alliance" in protective_factors
        assert "Good coping skills utilization" in protective_factors
        assert "Consistent therapeutic progress" in protective_factors

    @pytest.mark.asyncio
    async def test_caching_mechanism(self, monitoring_service):
        """Test metrics caching for performance."""
        user_id = "test_user_cache"

        # Collect some metrics
        await monitoring_service.collect_metric(
            user_id=user_id,
            session_id="session_cache",
            metric_type=MetricType.ENGAGEMENT,
            value=0.75,
        )

        # Generate report (should miss cache)
        report1 = await monitoring_service.generate_analytics_report(
            user_id=user_id, timeframe=AnalyticsTimeframe.WEEKLY
        )

        # Generate same report again (should hit cache)
        report2 = await monitoring_service.generate_analytics_report(
            user_id=user_id, timeframe=AnalyticsTimeframe.WEEKLY
        )

        # Verify both reports are identical (from cache)
        assert report1.report_id == report2.report_id
        assert report1.generated_at == report2.generated_at

        # Verify cache metrics
        service_metrics = monitoring_service.get_service_metrics()
        assert service_metrics["cache_hits"] >= 1
        assert service_metrics["cache_misses"] >= 1
        assert service_metrics["cache_hit_rate"] > 0.0

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, monitoring_service):
        """Test that monitoring service meets performance benchmarks."""
        import time

        user_id = "test_user_performance"
        session_id = "session_performance"

        # Test metric collection performance
        start_time = time.perf_counter()
        for i in range(100):
            await monitoring_service.collect_metric(
                user_id=user_id,
                session_id=session_id,
                metric_type=MetricType.ENGAGEMENT,
                value=0.5 + (i * 0.001),
            )
        collection_time = (time.perf_counter() - start_time) * 1000

        assert (
            collection_time < 1000.0
        )  # 100 metrics should be collected in under 1 second

        # Test real-time metrics retrieval performance
        start_time = time.perf_counter()
        real_time_metrics = await monitoring_service.get_real_time_metrics(user_id)
        retrieval_time = (time.perf_counter() - start_time) * 1000

        assert (
            retrieval_time < 100.0
        )  # Real-time metrics should be retrieved in under 100ms
        assert len(real_time_metrics) > 0

        # Test analytics report generation performance
        start_time = time.perf_counter()
        report = await monitoring_service.generate_analytics_report(user_id)
        report_time = (time.perf_counter() - start_time) * 1000

        assert (
            report_time < 500.0
        )  # Analytics report should be generated in under 500ms
        assert report is not None

        # Verify service metrics
        service_metrics = monitoring_service.get_service_metrics()
        assert service_metrics["metrics_collected"] >= 100
        assert service_metrics["analytics_reports_generated"] >= 1

    @pytest.mark.asyncio
    async def test_evidence_based_outcome_measures(self, monitoring_service):
        """Test evidence-based outcome measures implementation."""
        user_id = "test_user_evidence"

        # Test different outcome measures with baseline and follow-up
        outcome_measures = [
            (OutcomeMeasure.PHQ9, 12.0, 6.0),  # Depression improvement
            (OutcomeMeasure.GAD7, 14.0, 8.0),  # Anxiety improvement
            (OutcomeMeasure.THERAPEUTIC_ALLIANCE, 3.5, 4.2),  # Alliance strengthening
            (OutcomeMeasure.QUALITY_OF_LIFE, 2.8, 3.6),  # QoL improvement
        ]

        # Record baseline measurements
        for measure_type, baseline, _ in outcome_measures:
            outcome_id = await monitoring_service.record_outcome_measure(
                user_id=user_id,
                measure_type=measure_type,
                current_score=baseline,
                baseline_score=baseline,
                clinician_notes=f"Baseline {measure_type.value} measurement",
            )
            assert outcome_id != ""

        # Record follow-up measurements
        for measure_type, baseline, current in outcome_measures:
            outcome_id = await monitoring_service.record_outcome_measure(
                user_id=user_id,
                measure_type=measure_type,
                current_score=current,
                baseline_score=baseline,
                clinician_notes=f"Follow-up {measure_type.value} measurement",
            )
            assert outcome_id != ""

        # Verify all outcome measures recorded (baseline + follow-up = 8 total)
        progress = await monitoring_service.get_outcome_progress(user_id)
        assert (
            progress["total_measurements"] == len(outcome_measures) * 2
        )  # baseline + follow-up
        assert len(progress["measures"]) == len(outcome_measures)

        # Verify improvement calculations
        for measure_type, baseline, current in outcome_measures:
            measure_data = progress["measures"][measure_type.value]
            assert measure_data["baseline_score"] == baseline
            assert measure_data["current_score"] == current

            expected_improvement = ((current - baseline) / baseline) * 100
            assert (
                abs(measure_data["improvement_percentage"] - expected_improvement)
                < 0.01
            )
