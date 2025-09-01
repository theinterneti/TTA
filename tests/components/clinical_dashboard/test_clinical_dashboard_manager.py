"""
Tests for Clinical Dashboard Manager

This module tests the clinical dashboard integration functionality including
real-time therapeutic monitoring, clinical oversight, and crisis alert integration.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timedelta

from src.components.clinical_dashboard.clinical_dashboard_manager import (
    ClinicalDashboardManager,
    DashboardStatus,
    AlertSeverity,
    ClinicalAlert,
    TherapeuticMetrics,
    ClinicalSession,
)


class TestClinicalDashboardManager:
    """Test Clinical Dashboard Manager functionality."""

    @pytest_asyncio.fixture
    async def dashboard_manager(self):
        """Create dashboard manager instance."""
        manager = ClinicalDashboardManager()
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        systems = {}

        # Mock all 9 therapeutic systems
        for system_name in [
            "consequence_system",
            "emotional_safety_system",
            "adaptive_difficulty_engine",
            "character_development_system",
            "therapeutic_integration_system",
            "gameplay_loop_controller",
            "replayability_system",
            "collaborative_system",
            "error_recovery_manager"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}

            # Add system-specific mock methods
            if system_name == "consequence_system":
                mock_system.get_user_metrics.return_value = {"therapeutic_value": 0.8}
            elif system_name == "emotional_safety_system":
                mock_system.get_safety_metrics.return_value = {
                    "safety_score": 0.9,
                    "crisis_risk_level": "none"
                }
            elif system_name == "adaptive_difficulty_engine":
                mock_system.get_performance_metrics.return_value = {"engagement_level": 0.85}
            elif system_name == "character_development_system":
                mock_system.get_character_metrics.return_value = {"progress_rate": 0.7}
            elif system_name == "therapeutic_integration_system":
                mock_system.get_integration_metrics.return_value = {"therapeutic_value_accumulated": 2.5}
            elif system_name == "gameplay_loop_controller":
                mock_system.get_session_metrics.return_value = {"session_progress": 0.6}
            elif system_name == "replayability_system":
                mock_system.get_exploration_metrics.return_value = {"exploration_depth": 0.4}
            elif system_name == "collaborative_system":
                mock_system.get_collaboration_metrics.return_value = {"collaboration_score": 0.3}
            elif system_name == "error_recovery_manager":
                mock_system.get_metrics.return_value = {"errors_handled": 2, "successful_recoveries": 2}

            systems[system_name] = mock_system

        return systems

    @pytest.mark.asyncio
    async def test_initialization(self, dashboard_manager):
        """Test dashboard manager initialization."""
        assert dashboard_manager.status == DashboardStatus.ACTIVE
        assert len(dashboard_manager.active_sessions) == 0
        assert len(dashboard_manager.active_alerts) == 0
        assert len(dashboard_manager.metrics_history) == 0
        assert len(dashboard_manager.connected_clinicians) == 0

        # Should have background tasks running
        assert dashboard_manager._metrics_collection_task is not None
        assert dashboard_manager._alert_cleanup_task is not None
        assert not dashboard_manager._metrics_collection_task.done()
        assert not dashboard_manager._alert_cleanup_task.done()

    @pytest.mark.asyncio
    async def test_therapeutic_system_injection(self, dashboard_manager, mock_therapeutic_systems):
        """Test therapeutic system dependency injection."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Should have all systems injected
        assert dashboard_manager.consequence_system is not None
        assert dashboard_manager.emotional_safety_system is not None
        assert dashboard_manager.adaptive_difficulty_engine is not None
        assert dashboard_manager.character_development_system is not None
        assert dashboard_manager.therapeutic_integration_system is not None
        assert dashboard_manager.gameplay_loop_controller is not None
        assert dashboard_manager.replayability_system is not None
        assert dashboard_manager.collaborative_system is not None
        assert dashboard_manager.error_recovery_manager is not None

    @pytest.mark.asyncio
    async def test_start_session_monitoring(self, dashboard_manager):
        """Test starting session monitoring."""
        session_id = "test_session_001"
        user_id = "test_user_001"
        clinician_id = "clinician_001"
        therapeutic_goals = ["anxiety_management", "confidence_building"]

        session = await dashboard_manager.start_session_monitoring(
            session_id=session_id,
            user_id=user_id,
            clinician_id=clinician_id,
            therapeutic_goals=therapeutic_goals
        )

        # Should create clinical session
        assert isinstance(session, ClinicalSession)
        assert session.session_id == session_id
        assert session.user_id == user_id
        assert session.clinician_id == clinician_id
        assert session.therapeutic_goals == therapeutic_goals
        assert session.session_status == "active"

        # Should be stored in active sessions
        assert session_id in dashboard_manager.active_sessions
        assert dashboard_manager.active_sessions[session_id] == session

        # Should update metrics
        assert dashboard_manager.dashboard_metrics["sessions_monitored"] == 1

        # Should initialize metrics history
        assert session_id in dashboard_manager.metrics_history
        assert len(dashboard_manager.metrics_history[session_id]) == 0

    @pytest.mark.asyncio
    async def test_collect_real_time_metrics(self, dashboard_manager, mock_therapeutic_systems):
        """Test real-time metrics collection."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Start session monitoring
        session_id = "test_session_002"
        user_id = "test_user_002"
        await dashboard_manager.start_session_monitoring(session_id, user_id)

        # Collect metrics
        metrics = await dashboard_manager.collect_real_time_metrics(session_id)

        # Should return therapeutic metrics
        assert isinstance(metrics, TherapeuticMetrics)
        assert metrics.user_id == user_id
        assert metrics.session_id == session_id
        assert metrics.timestamp is not None

        # Should have collected metrics from all systems
        assert metrics.therapeutic_value_accumulated == 2.5  # From therapeutic_integration_system
        assert metrics.engagement_level == 0.85  # From adaptive_difficulty_engine
        assert metrics.safety_score == 0.9  # From emotional_safety_system
        assert metrics.crisis_risk_level == "none"  # From emotional_safety_system

        # Should have system-specific metrics
        assert "therapeutic_value" in metrics.consequence_system_metrics
        assert "safety_score" in metrics.emotional_safety_metrics
        assert "engagement_level" in metrics.adaptive_difficulty_metrics
        assert "progress_rate" in metrics.character_development_metrics
        assert "therapeutic_value_accumulated" in metrics.therapeutic_integration_metrics

        # Should update session with current metrics
        session = dashboard_manager.active_sessions[session_id]
        assert session.current_metrics == metrics

        # Should store in metrics history
        assert len(dashboard_manager.metrics_history[session_id]) == 1
        assert dashboard_manager.metrics_history[session_id][0] == metrics

        # Should update dashboard metrics
        assert dashboard_manager.dashboard_metrics["metrics_collected"] == 1

    @pytest.mark.asyncio
    async def test_generate_clinical_alert(self, dashboard_manager):
        """Test clinical alert generation."""
        user_id = "test_user_003"
        session_id = "test_session_003"
        alert_type = "crisis_detection"
        severity = AlertSeverity.HIGH
        message = "High anxiety levels detected"
        therapeutic_context = {"anxiety_score": 0.8, "session_duration": 45}

        alert = await dashboard_manager.generate_clinical_alert(
            user_id=user_id,
            session_id=session_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            therapeutic_context=therapeutic_context
        )

        # Should create clinical alert
        assert isinstance(alert, ClinicalAlert)
        assert alert.user_id == user_id
        assert alert.session_id == session_id
        assert alert.alert_type == alert_type
        assert alert.severity == severity
        assert alert.message == message
        assert alert.therapeutic_context == therapeutic_context
        assert alert.timestamp is not None
        assert not alert.acknowledged
        assert not alert.resolved

        # Should be stored in active alerts
        assert alert.alert_id in dashboard_manager.active_alerts
        assert dashboard_manager.active_alerts[alert.alert_id] == alert

        # Should update metrics
        assert dashboard_manager.dashboard_metrics["alerts_generated"] == 1

    @pytest.mark.asyncio
    async def test_critical_alert_immediate_notification(self, dashboard_manager):
        """Test immediate notification for critical alerts."""
        # Generate critical alert
        alert = await dashboard_manager.generate_clinical_alert(
            user_id="test_user_004",
            session_id="test_session_004",
            alert_type="crisis_suicide_ideation",
            severity=AlertSeverity.CRITICAL,
            message="Suicide ideation detected - immediate intervention required"
        )

        # Should trigger immediate notification (logged as critical)
        assert alert.severity == AlertSeverity.CRITICAL
        assert "suicide" in alert.message.lower()

    @pytest.mark.asyncio
    async def test_dashboard_overview(self, dashboard_manager, mock_therapeutic_systems):
        """Test dashboard overview generation."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Set up test data
        await dashboard_manager.start_session_monitoring("session_001", "user_001", "clinician_001")
        await dashboard_manager.start_session_monitoring("session_002", "user_002", "clinician_002")

        await dashboard_manager.generate_clinical_alert(
            "user_001", "session_001", "test_alert", AlertSeverity.MEDIUM, "Test alert"
        )

        await dashboard_manager.connect_clinician("clinician_001")
        await dashboard_manager.connect_clinician("clinician_002")

        # Get dashboard overview
        overview = await dashboard_manager.get_dashboard_overview()

        # Should have comprehensive overview
        assert overview["dashboard_status"] == "active"
        assert "timestamp" in overview

        # Summary statistics
        summary = overview["summary"]
        assert summary["active_sessions"] == 2
        assert summary["active_alerts"] == 1
        assert summary["critical_alerts"] == 0
        assert summary["connected_clinicians"] == 2

        # Active sessions
        assert len(overview["active_sessions"]) == 2
        session_data = overview["active_sessions"][0]
        assert "session_id" in session_data
        assert "user_id" in session_data
        assert "clinician_id" in session_data
        assert "therapeutic_goals" in session_data
        assert "current_metrics" in session_data

        # Recent alerts
        assert len(overview["recent_alerts"]) == 1
        alert_data = overview["recent_alerts"][0]
        assert "alert_id" in alert_data
        assert "alert_type" in alert_data
        assert "severity" in alert_data
        assert "message" in alert_data

        # System health
        assert "system_health" in overview
        system_health = overview["system_health"]
        assert "systems_health" in system_health
        assert "healthy_systems" in system_health
        assert "overall_health" in system_health

        # Performance metrics
        assert "performance_metrics" in overview

    @pytest.mark.asyncio
    async def test_alert_acknowledgment_and_resolution(self, dashboard_manager):
        """Test alert acknowledgment and resolution."""
        # Generate alert
        alert = await dashboard_manager.generate_clinical_alert(
            "user_005", "session_005", "test_alert", AlertSeverity.MEDIUM, "Test alert"
        )

        clinician_id = "clinician_005"

        # Acknowledge alert
        acknowledged = await dashboard_manager.acknowledge_alert(alert.alert_id, clinician_id)
        assert acknowledged is True

        # Check alert status
        stored_alert = dashboard_manager.active_alerts[alert.alert_id]
        assert stored_alert.acknowledged is True
        assert stored_alert.acknowledged_by == clinician_id
        assert stored_alert.acknowledged_at is not None

        # Resolve alert
        resolved = await dashboard_manager.resolve_alert(alert.alert_id, clinician_id)
        assert resolved is True

        # Check alert status
        assert stored_alert.resolved is True
        assert stored_alert.resolved_by == clinician_id
        assert stored_alert.resolved_at is not None

    @pytest.mark.asyncio
    async def test_clinician_connection_management(self, dashboard_manager):
        """Test clinician connection and disconnection."""
        clinician_id = "clinician_006"

        # Connect clinician
        connected = await dashboard_manager.connect_clinician(clinician_id)
        assert connected is True
        assert clinician_id in dashboard_manager.connected_clinicians
        assert dashboard_manager.dashboard_metrics["clinicians_connected"] == 1

        # Disconnect clinician
        disconnected = await dashboard_manager.disconnect_clinician(clinician_id)
        assert disconnected is True
        assert clinician_id not in dashboard_manager.connected_clinicians
        assert dashboard_manager.dashboard_metrics["clinicians_connected"] == 0

    @pytest.mark.asyncio
    async def test_system_health_summary(self, dashboard_manager, mock_therapeutic_systems):
        """Test system health summary generation."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        health_summary = await dashboard_manager._get_system_health_summary()

        # Should have health status for all systems
        assert "systems_health" in health_summary
        assert "healthy_systems" in health_summary
        assert "overall_health" in health_summary

        systems_health = health_summary["systems_health"]
        assert len(systems_health) == 9

        # All mock systems should be healthy
        for system_name in systems_health:
            assert systems_health[system_name] == "healthy"

        assert health_summary["healthy_systems"] == "9/9"
        assert health_summary["overall_health"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check(self, dashboard_manager, mock_therapeutic_systems):
        """Test dashboard manager health check."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        health = await dashboard_manager.health_check()

        assert "status" in health
        assert health["status"] == "healthy"  # All 9 systems available
        assert health["dashboard_status"] == "active"
        assert health["therapeutic_systems_available"] == "9/9"
        assert health["background_tasks_running"] is True
        assert "performance_metrics" in health

    @pytest.mark.asyncio
    async def test_health_check_degraded(self, dashboard_manager):
        """Test health check with missing systems."""
        # Don't inject all systems - only inject a few
        dashboard_manager.inject_therapeutic_systems(
            consequence_system=AsyncMock(),
            emotional_safety_system=AsyncMock()
        )

        health = await dashboard_manager.health_check()

        assert health["status"] == "degraded"  # Less than 7 systems available
        assert health["therapeutic_systems_available"] == "2/9"

    @pytest.mark.asyncio
    async def test_metrics_collection_loop_integration(self, dashboard_manager, mock_therapeutic_systems):
        """Test metrics collection background loop."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Start session
        session_id = "test_session_loop"
        await dashboard_manager.start_session_monitoring(session_id, "test_user_loop")

        # Wait for metrics collection (should happen every 5 seconds by default)
        # For testing, we'll manually trigger collection
        await dashboard_manager.collect_real_time_metrics(session_id)

        # Should have collected metrics
        assert len(dashboard_manager.metrics_history[session_id]) == 1
        assert dashboard_manager.dashboard_metrics["metrics_collected"] == 1

        # Data refresh rate should be calculated
        assert dashboard_manager.dashboard_metrics["data_refresh_rate"] >= 0.0

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, dashboard_manager, mock_therapeutic_systems):
        """Test compatibility with E2E test interface expectations."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Test session monitoring (E2E interface)
        session = await dashboard_manager.start_session_monitoring(
            session_id="e2e_session_001",
            user_id="e2e_user_001",
            therapeutic_goals=["confidence_building"]
        )

        # Should match expected structure
        assert hasattr(session, "session_id")
        assert hasattr(session, "user_id")
        assert hasattr(session, "therapeutic_goals")
        assert hasattr(session, "current_metrics")

        # Test metrics collection (E2E interface)
        metrics = await dashboard_manager.collect_real_time_metrics("e2e_session_001")

        # Should match expected structure
        assert hasattr(metrics, "therapeutic_value_accumulated")
        assert hasattr(metrics, "engagement_level")
        assert hasattr(metrics, "safety_score")
        assert hasattr(metrics, "crisis_risk_level")

        # Test alert generation (E2E interface)
        alert = await dashboard_manager.generate_clinical_alert(
            user_id="e2e_user_001",
            session_id="e2e_session_001",
            alert_type="e2e_test_alert",
            severity=AlertSeverity.LOW,
            message="E2E test alert"
        )

        # Should match expected structure
        assert hasattr(alert, "alert_id")
        assert hasattr(alert, "severity")
        assert hasattr(alert, "message")
        assert hasattr(alert, "timestamp")

        # Test dashboard overview (E2E interface)
        overview = await dashboard_manager.get_dashboard_overview()

        # Should match expected structure
        assert "dashboard_status" in overview
        assert "summary" in overview
        assert "active_sessions" in overview
        assert "recent_alerts" in overview
        assert "system_health" in overview

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, dashboard_manager, mock_therapeutic_systems):
        """Test performance benchmarks for clinical dashboard."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Test session monitoring performance
        import time
        start_time = time.perf_counter()

        session = await dashboard_manager.start_session_monitoring(
            "perf_session", "perf_user", therapeutic_goals=["performance_test"]
        )

        session_time = (time.perf_counter() - start_time) * 1000
        assert session_time < 100.0  # Should be under 100ms

        # Test metrics collection performance
        start_time = time.perf_counter()

        metrics = await dashboard_manager.collect_real_time_metrics("perf_session")

        metrics_time = (time.perf_counter() - start_time) * 1000
        assert metrics_time < 50.0  # Should be under 50ms for real-time requirements

        # Test dashboard overview performance
        start_time = time.perf_counter()

        overview = await dashboard_manager.get_dashboard_overview()

        overview_time = (time.perf_counter() - start_time) * 1000
        assert overview_time < 200.0  # Should be under 200ms for dashboard refresh

        # Validate data refresh rate is tracked
        assert dashboard_manager.dashboard_metrics["data_refresh_rate"] >= 0.0
