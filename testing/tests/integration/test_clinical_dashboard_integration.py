"""
Integration Tests for Clinical Dashboard Components

This module tests the integration between all therapeutic systems and
clinical dashboard components, validating end-to-end workflows and
performance benchmarks for clinical deployment.
"""

import asyncio
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.components.clinical_dashboard.clinical_dashboard_manager import (
    AlertSeverity,
    ClinicalDashboardManager,
)
from src.components.clinical_dashboard.crisis_detection_dashboard import (
    CrisisDetectionDashboard,
)
from src.components.clinical_dashboard.therapeutic_monitoring_service import (
    MetricType,
    TherapeuticMonitoringService,
)


def utc_now() -> datetime:
    """Get current UTC time with timezone awareness."""
    return datetime.now(timezone.utc)


class TestClinicalDashboardIntegration:
    """Test integration between all clinical dashboard components."""

    @pytest_asyncio.fixture
    async def integrated_dashboard(self):
        """Create fully integrated clinical dashboard system."""
        # Initialize all components
        dashboard_manager = ClinicalDashboardManager()
        monitoring_service = TherapeuticMonitoringService()

        # Mock emotional safety system for crisis detection
        mock_safety_system = AsyncMock()
        mock_safety_system.assess_crisis_risk.return_value = {
            "crisis_detected": False,
            "crisis_level": "none",
            "immediate_intervention": False,
            "indicators": [],
            "response_time": 0.05,
            "assessment_id": "test_assessment",
            "risk_score": 0.1,
        }

        crisis_dashboard = CrisisDetectionDashboard(mock_safety_system)

        # Initialize all components
        await dashboard_manager.initialize()
        await monitoring_service.initialize()
        await crisis_dashboard.initialize()

        yield {
            "dashboard_manager": dashboard_manager,
            "monitoring_service": monitoring_service,
            "crisis_dashboard": crisis_dashboard,
            "mock_safety_system": mock_safety_system,
        }

        # Cleanup
        await dashboard_manager.shutdown()
        await monitoring_service.shutdown()
        await crisis_dashboard.shutdown()

    @pytest.mark.asyncio
    async def test_end_to_end_clinical_workflow(self, integrated_dashboard):
        """Test complete end-to-end clinical workflow."""
        dashboard = integrated_dashboard["dashboard_manager"]
        monitoring = integrated_dashboard["monitoring_service"]
        crisis = integrated_dashboard["crisis_dashboard"]

        # Step 1: Start clinical session
        session_id = "e2e_session_001"
        user_id = "patient_001"
        clinician_id = "clinician_001"

        session = await dashboard.start_session_monitoring(
            session_id=session_id,
            user_id=user_id,
            clinician_id=clinician_id,
            therapeutic_goals=["anxiety_management", "confidence_building"],
        )

        assert session.session_id == session_id
        assert session.user_id == user_id

        # Step 2: Collect therapeutic metrics
        metrics_collected = []
        for i in range(5):
            success = await monitoring.collect_metric(
                user_id=user_id,
                session_id=session_id,
                metric_type=MetricType.ENGAGEMENT,
                value=0.7 + (i * 0.05),  # Improving engagement
                context={"step": i + 1},
            )
            assert success is True
            metrics_collected.append(0.7 + (i * 0.05))

        # Step 3: Generate analytics report
        report = await monitoring.generate_analytics_report(user_id)
        assert report is not None
        assert report.user_id == user_id
        assert "engagement" in report.metrics_summary

        # Step 4: Process crisis assessment (no crisis)
        crisis_event = await crisis.process_crisis_assessment(
            user_id=user_id,
            session_id=session_id,
            user_input="I'm feeling better today",
        )

        assert crisis_event.user_id == user_id
        assert crisis_event.crisis_level.value == "NONE"

        # Step 5: Generate clinical alert
        alert = await dashboard.generate_clinical_alert(
            user_id=user_id,
            session_id=session_id,
            alert_type="progress_milestone",
            severity=AlertSeverity.LOW,
            message="Patient showing consistent improvement",
        )

        assert alert.user_id == user_id
        assert alert.severity == AlertSeverity.LOW

        # Step 6: Get dashboard overview
        overview = await dashboard.get_dashboard_overview()
        assert overview["dashboard_status"] == "active"
        assert overview["summary"]["active_sessions"] >= 1
        assert overview["summary"]["active_alerts"] >= 1

        # Verify integration metrics
        dashboard_metrics = dashboard.dashboard_metrics
        monitoring_metrics = monitoring.get_service_metrics()
        crisis_metrics = crisis.dashboard_metrics

        assert dashboard_metrics["sessions_monitored"] >= 1
        assert monitoring_metrics["metrics_collected"] >= 5
        assert crisis_metrics["crisis_events_detected"] == 0  # No crisis detected

    @pytest.mark.asyncio
    async def test_crisis_workflow_integration(self, integrated_dashboard):
        """Test integrated crisis detection and response workflow."""
        dashboard = integrated_dashboard["dashboard_manager"]
        crisis = integrated_dashboard["crisis_dashboard"]
        mock_safety = integrated_dashboard["mock_safety_system"]

        # Configure mock to detect crisis
        mock_safety.assess_crisis_risk.return_value = {
            "crisis_detected": True,
            "crisis_level": "high",
            "immediate_intervention": True,
            "indicators": ["suicide_ideation", "hopelessness"],
            "response_time": 0.08,
            "assessment_id": "crisis_assessment_001",
            "risk_score": 0.85,
        }

        user_id = "patient_crisis"
        session_id = "crisis_session_001"

        # Start session monitoring
        await dashboard.start_session_monitoring(
            session_id=session_id,
            user_id=user_id,
            therapeutic_goals=["crisis_intervention"],
        )

        # Process crisis assessment
        crisis_event = await crisis.process_crisis_assessment(
            user_id=user_id,
            session_id=session_id,
            user_input="I want to end it all",
        )

        # Verify crisis was detected and processed
        assert crisis_event.crisis_level.value == "HIGH"
        assert crisis_event.intervention_required is True
        assert len(crisis_event.indicators) == 2

        # Verify interventions were created
        pending_interventions = await crisis.get_pending_interventions()
        assert len(pending_interventions) > 0

        # Verify crisis notifications were sent
        crisis_summary = await crisis.get_crisis_dashboard_summary()
        assert crisis_summary["active_crisis_events"] == 1
        assert crisis_summary["unacknowledged_notifications"] > 0

        # Create corresponding alert in dashboard manager (integration point)
        await dashboard.generate_clinical_alert(
            user_id=user_id,
            session_id=session_id,
            alert_type="crisis_detected",
            severity=AlertSeverity.CRITICAL,
            message=f"Crisis detected: {crisis_event.crisis_level.value}",
            therapeutic_context={
                "crisis_event_id": crisis_event.event_id,
                "indicators": [ind.value for ind in crisis_event.indicators],
                "risk_score": crisis_event.risk_score,
            },
        )

        # Verify dashboard received crisis alert
        overview = await dashboard.get_dashboard_overview()
        assert overview["summary"]["active_alerts"] >= 1

    @pytest.mark.asyncio
    async def test_system_health_monitoring_integration(self, integrated_dashboard):
        """Test system health monitoring integration."""
        dashboard = integrated_dashboard["dashboard_manager"]

        # Mock therapeutic systems
        mock_systems = {}
        for system_name in [
            "consequence_system",
            "emotional_safety_system",
            "adaptive_difficulty_engine",
            "character_development_system",
            "therapeutic_integration_system",
            "gameplay_loop_controller",
            "replayability_system",
            "collaborative_system",
            "error_recovery_manager",
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            mock_systems[system_name] = mock_system

        # Inject systems
        dashboard.inject_therapeutic_systems(**mock_systems)

        # Get comprehensive system health
        health_status = await dashboard.get_comprehensive_system_health()

        assert health_status["overall_status"] == "healthy"
        assert health_status["overall_health_percentage"] == 100.0
        assert health_status["systems_summary"]["total"] == 9
        assert health_status["systems_summary"]["healthy"] == 9

        # Test degraded system scenario
        mock_systems["consequence_system"].health_check.return_value = {
            "status": "degraded"
        }
        mock_systems["emotional_safety_system"].health_check.return_value = {
            "status": "unhealthy"
        }

        # Force refresh of health data
        dashboard.last_health_check = utc_now() - timedelta(minutes=5)

        health_status = await dashboard.get_comprehensive_system_health()

        assert health_status["overall_status"] in ["degraded", "critical"]
        assert health_status["overall_health_percentage"] < 100.0
        assert health_status["systems_summary"]["healthy"] < 9

    @pytest.mark.asyncio
    async def test_performance_benchmarks_integration(self, integrated_dashboard):
        """Test that integrated system meets performance benchmarks."""
        dashboard = integrated_dashboard["dashboard_manager"]
        monitoring = integrated_dashboard["monitoring_service"]
        crisis = integrated_dashboard["crisis_dashboard"]

        user_id = "perf_test_user"
        session_id = "perf_test_session"

        # Test session creation performance
        start_time = time.perf_counter()
        session = await dashboard.start_session_monitoring(
            session_id=session_id,
            user_id=user_id,
            therapeutic_goals=["performance_testing"],
        )
        session_time = (time.perf_counter() - start_time) * 1000

        assert session_time < 100.0  # Should be under 100ms
        assert session.session_id == session_id

        # Test metrics collection performance
        start_time = time.perf_counter()
        success = await monitoring.collect_metric(
            user_id=user_id,
            session_id=session_id,
            metric_type=MetricType.THERAPEUTIC_VALUE,
            value=0.8,
        )
        metrics_time = (time.perf_counter() - start_time) * 1000

        assert metrics_time < 50.0  # Should be under 50ms for real-time requirements
        assert success is True

        # Test crisis assessment performance
        start_time = time.perf_counter()
        crisis_event = await crisis.process_crisis_assessment(
            user_id=user_id,
            session_id=session_id,
            user_input="Performance test input",
        )
        crisis_time = (time.perf_counter() - start_time) * 1000

        assert crisis_time < 1000.0  # Should be under 1 second for crisis detection
        assert crisis_event.user_id == user_id

        # Test dashboard overview performance
        start_time = time.perf_counter()
        overview = await dashboard.get_dashboard_overview()
        overview_time = (time.perf_counter() - start_time) * 1000

        assert overview_time < 200.0  # Should be under 200ms for dashboard refresh
        assert "dashboard_status" in overview

        # Test system health check performance
        start_time = time.perf_counter()
        health = await dashboard.health_check()
        health_time = (time.perf_counter() - start_time) * 1000

        assert health_time < 100.0  # Should be under 100ms
        assert "status" in health

    @pytest.mark.asyncio
    async def test_concurrent_operations_stability(self, integrated_dashboard):
        """Test system stability under concurrent operations."""
        dashboard = integrated_dashboard["dashboard_manager"]
        monitoring = integrated_dashboard["monitoring_service"]
        crisis = integrated_dashboard["crisis_dashboard"]

        # Create multiple concurrent sessions
        tasks = []
        for i in range(10):
            user_id = f"concurrent_user_{i}"
            session_id = f"concurrent_session_{i}"

            # Create session monitoring task
            task = asyncio.create_task(
                dashboard.start_session_monitoring(
                    session_id=session_id,
                    user_id=user_id,
                    therapeutic_goals=["concurrent_testing"],
                )
            )
            tasks.append(task)

        # Wait for all sessions to be created
        sessions = await asyncio.gather(*tasks)
        assert len(sessions) == 10

        # Create concurrent metrics collection tasks
        metrics_tasks = []
        for i in range(10):
            user_id = f"concurrent_user_{i}"
            session_id = f"concurrent_session_{i}"

            task = asyncio.create_task(
                monitoring.collect_metric(
                    user_id=user_id,
                    session_id=session_id,
                    metric_type=MetricType.ENGAGEMENT,
                    value=0.5 + (i * 0.05),
                )
            )
            metrics_tasks.append(task)

        # Wait for all metrics to be collected
        results = await asyncio.gather(*metrics_tasks)
        assert all(results)  # All should be True

        # Verify system health under load
        health = await dashboard.health_check()
        assert health["status"] in ["healthy", "degraded"]  # Should not be unhealthy

        monitoring_health = await monitoring.health_check()
        assert monitoring_health["status"] == "healthy"

        crisis_health = await crisis.health_check()
        assert crisis_health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, integrated_dashboard):
        """Test error recovery and graceful degradation."""
        dashboard = integrated_dashboard["dashboard_manager"]
        monitoring = integrated_dashboard["monitoring_service"]

        # Test with invalid user ID
        try:
            await dashboard.start_session_monitoring(
                session_id="",  # Invalid session ID
                user_id="",  # Invalid user ID
                therapeutic_goals=[],
            )
        except Exception:
            pass  # Expected to fail gracefully

        # System should still be healthy
        health = await dashboard.health_check()
        assert health["status"] in ["healthy", "degraded"]

        # Test metrics collection with invalid data
        await monitoring.collect_metric(
            user_id="valid_user",
            session_id="valid_session",
            metric_type=MetricType.ENGAGEMENT,
            value=999.0,  # Invalid value (should be 0-1)
        )

        # Should handle gracefully
        monitoring_health = await monitoring.health_check()
        assert monitoring_health["status"] == "healthy"
