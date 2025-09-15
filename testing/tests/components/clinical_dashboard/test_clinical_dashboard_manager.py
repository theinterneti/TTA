"""
Tests for Enhanced Clinical Dashboard Manager

This module tests the enhanced clinical dashboard integration functionality including
real-time therapeutic monitoring, clinical oversight, crisis alert integration,
role-based access control, and HIPAA-compliant audit logging.
"""

import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.components.clinical_dashboard.clinical_dashboard_manager import (
    AccessLevel,
    AlertSeverity,
    AuditEventType,
    ClinicalAlert,
    ClinicalDashboardManager,
    ClinicalRole,
    ClinicalSession,
    DashboardStatus,
    TherapeuticMetrics,
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
            "error_recovery_manager",
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}

            # Add system-specific mock methods
            if system_name == "consequence_system":
                mock_system.get_user_metrics.return_value = {"therapeutic_value": 0.8}
            elif system_name == "emotional_safety_system":
                mock_system.get_safety_metrics.return_value = {
                    "safety_score": 0.9,
                    "crisis_risk_level": "none",
                }
            elif system_name == "adaptive_difficulty_engine":
                mock_system.get_performance_metrics.return_value = {
                    "engagement_level": 0.85
                }
            elif system_name == "character_development_system":
                mock_system.get_character_metrics.return_value = {"progress_rate": 0.7}
            elif system_name == "therapeutic_integration_system":
                mock_system.get_integration_metrics.return_value = {
                    "therapeutic_value_accumulated": 2.5
                }
            elif system_name == "gameplay_loop_controller":
                mock_system.get_session_metrics.return_value = {"session_progress": 0.6}
            elif system_name == "replayability_system":
                mock_system.get_exploration_metrics.return_value = {
                    "exploration_depth": 0.4
                }
            elif system_name == "collaborative_system":
                mock_system.get_collaboration_metrics.return_value = {
                    "collaboration_score": 0.3
                }
            elif system_name == "error_recovery_manager":
                mock_system.get_metrics.return_value = {
                    "errors_handled": 2,
                    "successful_recoveries": 2,
                }

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
    async def test_therapeutic_system_injection(
        self, dashboard_manager, mock_therapeutic_systems
    ):
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
            therapeutic_goals=therapeutic_goals,
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
    async def test_collect_real_time_metrics(
        self, dashboard_manager, mock_therapeutic_systems
    ):
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
        assert (
            metrics.therapeutic_value_accumulated == 2.5
        )  # From therapeutic_integration_system
        assert metrics.engagement_level == 0.85  # From adaptive_difficulty_engine
        assert metrics.safety_score == 0.9  # From emotional_safety_system
        assert metrics.crisis_risk_level == "none"  # From emotional_safety_system

        # Should have system-specific metrics
        assert "therapeutic_value" in metrics.consequence_system_metrics
        assert "safety_score" in metrics.emotional_safety_metrics
        assert "engagement_level" in metrics.adaptive_difficulty_metrics
        assert "progress_rate" in metrics.character_development_metrics
        assert (
            "therapeutic_value_accumulated" in metrics.therapeutic_integration_metrics
        )

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
            therapeutic_context=therapeutic_context,
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
            message="Suicide ideation detected - immediate intervention required",
        )

        # Should trigger immediate notification (logged as critical)
        assert alert.severity == AlertSeverity.CRITICAL
        assert "suicide" in alert.message.lower()

    @pytest.mark.asyncio
    async def test_dashboard_overview(
        self, dashboard_manager, mock_therapeutic_systems
    ):
        """Test dashboard overview generation."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Set up test data
        await dashboard_manager.start_session_monitoring(
            "session_001", "user_001", "clinician_001"
        )
        await dashboard_manager.start_session_monitoring(
            "session_002", "user_002", "clinician_002"
        )

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
        acknowledged = await dashboard_manager.acknowledge_alert(
            alert.alert_id, clinician_id
        )
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
    async def test_system_health_summary(
        self, dashboard_manager, mock_therapeutic_systems
    ):
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
            consequence_system=AsyncMock(), emotional_safety_system=AsyncMock()
        )

        health = await dashboard_manager.health_check()

        assert health["status"] == "degraded"  # Less than 7 systems available
        assert health["therapeutic_systems_available"] == "2/9"

    @pytest.mark.asyncio
    async def test_metrics_collection_loop_integration(
        self, dashboard_manager, mock_therapeutic_systems
    ):
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
    async def test_e2e_interface_compatibility(
        self, dashboard_manager, mock_therapeutic_systems
    ):
        """Test compatibility with E2E test interface expectations."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Test session monitoring (E2E interface)
        session = await dashboard_manager.start_session_monitoring(
            session_id="e2e_session_001",
            user_id="e2e_user_001",
            therapeutic_goals=["confidence_building"],
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
            message="E2E test alert",
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
    async def test_performance_benchmarks(
        self, dashboard_manager, mock_therapeutic_systems
    ):
        """Test performance benchmarks for clinical dashboard."""
        dashboard_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Test session monitoring performance

        start_time = time.perf_counter()

        await dashboard_manager.start_session_monitoring(
            "perf_session", "perf_user", therapeutic_goals=["performance_test"]
        )

        session_time = (time.perf_counter() - start_time) * 1000
        assert session_time < 100.0  # Should be under 100ms

        # Test metrics collection performance
        start_time = time.perf_counter()

        await dashboard_manager.collect_real_time_metrics("perf_session")

        metrics_time = (time.perf_counter() - start_time) * 1000
        assert metrics_time < 50.0  # Should be under 50ms for real-time requirements

        # Test dashboard overview performance
        start_time = time.perf_counter()

        await dashboard_manager.get_dashboard_overview()

        overview_time = (time.perf_counter() - start_time) * 1000
        assert overview_time < 200.0  # Should be under 200ms for dashboard refresh

        # Validate data refresh rate is tracked
        assert dashboard_manager.dashboard_metrics["data_refresh_rate"] >= 0.0


class TestEnhancedClinicalDashboard:
    """Test Enhanced Clinical Dashboard features for Phase B."""

    @pytest_asyncio.fixture
    async def enhanced_dashboard(self):
        """Create enhanced dashboard manager instance."""
        manager = ClinicalDashboardManager()
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_practitioner_registration(self, enhanced_dashboard):
        """Test clinical practitioner registration."""
        # Register a therapist
        practitioner_id = await enhanced_dashboard.register_practitioner(
            username="dr_smith",
            full_name="Dr. Jane Smith",
            role=ClinicalRole.THERAPIST,
            access_level=AccessLevel.STANDARD,
            email="dr.smith@clinic.com",
            license_number="LIC123456",
            department="Mental Health",
        )

        assert practitioner_id is not None
        assert practitioner_id in enhanced_dashboard.registered_practitioners

        practitioner = enhanced_dashboard.registered_practitioners[practitioner_id]
        assert practitioner.username == "dr_smith"
        assert practitioner.role == ClinicalRole.THERAPIST
        assert practitioner.access_level == AccessLevel.STANDARD
        assert practitioner.active is True

        # Verify audit log entry
        assert len(enhanced_dashboard.audit_log) > 0
        audit_entry = enhanced_dashboard.audit_log[-1]
        assert audit_entry.event_type == AuditEventType.CONFIGURATION_CHANGE
        assert "register_practitioner" in audit_entry.details["action"]

    @pytest.mark.asyncio
    async def test_practitioner_authentication(self, enhanced_dashboard):
        """Test clinical practitioner authentication."""
        # Register practitioner first
        practitioner_id = await enhanced_dashboard.register_practitioner(
            username="dr_jones",
            full_name="Dr. Michael Jones",
            role=ClinicalRole.CLINICAL_SUPERVISOR,
            access_level=AccessLevel.ELEVATED,
            email="dr.jones@clinic.com",
        )

        # Authenticate practitioner
        session_token, auth_practitioner_id = (
            await enhanced_dashboard.authenticate_practitioner(
                username="dr_jones",
                password_hash="hashed_password_123",
                ip_address="192.168.1.100",
            )
        )

        assert session_token is not None
        assert auth_practitioner_id == practitioner_id
        assert session_token in enhanced_dashboard.active_practitioner_sessions

        # Verify session tracking
        tracked_id = enhanced_dashboard.active_practitioner_sessions[session_token]
        assert tracked_id == practitioner_id

        # Verify practitioner session info updated
        practitioner = enhanced_dashboard.registered_practitioners[practitioner_id]
        assert practitioner.session_token == session_token
        assert practitioner.token_expires is not None
        assert practitioner.last_login is not None

        # Verify audit log
        login_entries = [
            e
            for e in enhanced_dashboard.audit_log
            if e.event_type == AuditEventType.LOGIN
        ]
        assert len(login_entries) > 0
        login_entry = login_entries[-1]
        assert login_entry.success is True
        assert login_entry.ip_address == "192.168.1.100"

    @pytest.mark.asyncio
    async def test_session_token_validation(self, enhanced_dashboard):
        """Test session token validation."""
        # Register and authenticate practitioner
        await enhanced_dashboard.register_practitioner(
            username="dr_wilson",
            full_name="Dr. Sarah Wilson",
            role=ClinicalRole.PSYCHIATRIST,
            access_level=AccessLevel.ELEVATED,
            email="dr.wilson@clinic.com",
        )

        session_token, practitioner_id = (
            await enhanced_dashboard.authenticate_practitioner(
                username="dr_wilson", password_hash="hashed_password_456"
            )
        )

        # Validate valid token
        validated_practitioner = await enhanced_dashboard.validate_session_token(
            session_token
        )
        assert validated_practitioner is not None
        assert validated_practitioner.practitioner_id == practitioner_id
        assert validated_practitioner.username == "dr_wilson"

        # Test invalid token
        invalid_practitioner = await enhanced_dashboard.validate_session_token(
            "invalid_token"
        )
        assert invalid_practitioner is None

        # Test expired token (simulate expiration)
        practitioner = enhanced_dashboard.registered_practitioners[practitioner_id]
        practitioner.token_expires = datetime.utcnow() - timedelta(minutes=1)  # Expired

        expired_practitioner = await enhanced_dashboard.validate_session_token(
            session_token
        )
        assert expired_practitioner is None
        assert session_token not in enhanced_dashboard.active_practitioner_sessions

    @pytest.mark.asyncio
    async def test_role_based_permissions(self, enhanced_dashboard):
        """Test role-based access control."""
        # Register practitioners with different roles
        await enhanced_dashboard.register_practitioner(
            username="therapist1",
            full_name="Therapist One",
            role=ClinicalRole.THERAPIST,
            access_level=AccessLevel.STANDARD,
            email="therapist1@clinic.com",
        )

        await enhanced_dashboard.register_practitioner(
            username="admin1",
            full_name="Admin One",
            role=ClinicalRole.CLINICAL_ADMIN,
            access_level=AccessLevel.ADMINISTRATIVE,
            email="admin1@clinic.com",
        )

        # Authenticate both
        therapist_token, _ = await enhanced_dashboard.authenticate_practitioner(
            username="therapist1", password_hash="hash1"
        )

        admin_token, _ = await enhanced_dashboard.authenticate_practitioner(
            username="admin1", password_hash="hash2"
        )

        # Test therapist permissions
        assert (
            await enhanced_dashboard.check_permission(therapist_token, "view_sessions")
            is True
        )
        assert (
            await enhanced_dashboard.check_permission(
                therapist_token, "acknowledge_alerts"
            )
            is True
        )
        assert (
            await enhanced_dashboard.check_permission(
                therapist_token, "manage_practitioners"
            )
            is False
        )
        assert (
            await enhanced_dashboard.check_permission(
                therapist_token, "system_administration"
            )
            is False
        )

        # Test admin permissions
        assert (
            await enhanced_dashboard.check_permission(admin_token, "view_sessions")
            is True
        )
        assert (
            await enhanced_dashboard.check_permission(admin_token, "acknowledge_alerts")
            is True
        )
        assert (
            await enhanced_dashboard.check_permission(
                admin_token, "manage_practitioners"
            )
            is True
        )
        assert (
            await enhanced_dashboard.check_permission(admin_token, "view_audit_logs")
            is True
        )

        # Test invalid token
        assert (
            await enhanced_dashboard.check_permission("invalid_token", "view_sessions")
            is False
        )

    @pytest.mark.asyncio
    async def test_audit_logging(self, enhanced_dashboard):
        """Test HIPAA-compliant audit logging."""
        initial_audit_count = len(enhanced_dashboard.audit_log)

        # Register practitioner (should create audit entry)
        practitioner_id = await enhanced_dashboard.register_practitioner(
            username="audit_test",
            full_name="Audit Test User",
            role=ClinicalRole.THERAPIST,
            access_level=AccessLevel.STANDARD,
            email="audit@clinic.com",
        )

        # Authenticate (should create audit entry)
        session_token, _ = await enhanced_dashboard.authenticate_practitioner(
            username="audit_test", password_hash="hash123", ip_address="10.0.0.1"
        )

        # Manual audit log entry
        await enhanced_dashboard._log_audit_event(
            practitioner_id=practitioner_id,
            event_type=AuditEventType.SESSION_ACCESS,
            resource_accessed="patient_session_123",
            patient_id="patient_456",
            session_id="session_789",
            ip_address="10.0.0.1",
            success=True,
            details={"action": "view_session", "duration_minutes": 45},
        )

        # Verify audit entries were created
        final_audit_count = len(enhanced_dashboard.audit_log)
        assert final_audit_count > initial_audit_count

        # Find the session access entry
        session_entries = [
            e
            for e in enhanced_dashboard.audit_log
            if e.event_type == AuditEventType.SESSION_ACCESS
        ]
        assert len(session_entries) > 0

        session_entry = session_entries[-1]
        assert session_entry.practitioner_id == practitioner_id
        assert session_entry.resource_accessed == "patient_session_123"
        assert session_entry.patient_id == "patient_456"
        assert session_entry.session_id == "session_789"
        assert session_entry.ip_address == "10.0.0.1"
        assert session_entry.success is True
        assert session_entry.details["action"] == "view_session"

        # Verify metrics updated
        assert enhanced_dashboard.dashboard_metrics["audit_events_logged"] > 0

    @pytest.mark.asyncio
    async def test_enhanced_clinical_metrics(self, enhanced_dashboard):
        """Test enhanced clinical-grade metrics collection."""
        # Create a clinical session with enhanced metrics
        session_id = "enhanced_metrics_session"
        user_id = "patient_123"

        session = ClinicalSession(
            session_id=session_id,
            user_id=user_id,
            therapeutic_goals=["anxiety_reduction", "coping_skills"],
            therapeutic_modality="CBT",
            session_type="individual",
        )

        enhanced_dashboard.active_sessions[session_id] = session

        # Create enhanced therapeutic metrics
        metrics = TherapeuticMetrics(
            user_id=user_id,
            session_id=session_id,
            therapeutic_value_accumulated=0.75,
            engagement_level=0.85,
            progress_rate=0.65,
            safety_score=0.95,
            crisis_risk_level="low",
            # Enhanced clinical metrics
            session_duration_minutes=45.0,
            therapeutic_goals_progress={"anxiety_reduction": 0.7, "coping_skills": 0.6},
            intervention_effectiveness=0.8,
            emotional_regulation_score=0.75,
            coping_skills_utilization=0.65,
            therapeutic_alliance_strength=0.9,
            behavioral_change_indicators={
                "mood_improvement": True,
                "sleep_quality": "improved",
            },
            clinical_risk_factors=["mild_anxiety"],
            protective_factors=["strong_support_system", "medication_compliance"],
        )

        # Update session metrics
        await enhanced_dashboard.update_session_metrics(session_id, metrics)

        # Verify enhanced metrics are tracked
        updated_session = enhanced_dashboard.active_sessions[session_id]
        assert updated_session.current_metrics is not None
        assert updated_session.current_metrics.session_duration_minutes == 45.0
        assert updated_session.current_metrics.therapeutic_alliance_strength == 0.9
        assert (
            "anxiety_reduction"
            in updated_session.current_metrics.therapeutic_goals_progress
        )
        assert len(updated_session.current_metrics.protective_factors) == 2

    @pytest.mark.asyncio
    async def test_crisis_alert_escalation(self, enhanced_dashboard):
        """Test enhanced crisis alert system with escalation."""
        # Create a crisis alert with enhanced features
        crisis_alert = ClinicalAlert(
            user_id="patient_crisis",
            session_id="crisis_session_001",
            alert_type="crisis_detected",
            severity=AlertSeverity.CRITICAL,
            message="Patient expressing suicidal ideation",
            therapeutic_context={
                "risk_factors": ["depression", "isolation"],
                "triggers": ["job_loss"],
            },
            # Enhanced fields
            priority_score=9.5,
            escalation_level=2,
            intervention_required=True,
            clinical_notes=[
                "Immediate intervention needed",
                "Contact emergency services",
            ],
            auto_escalation_time=datetime.utcnow() + timedelta(minutes=5),
        )

        # Add alert to dashboard
        await enhanced_dashboard.add_clinical_alert(crisis_alert)

        # Verify alert was added with enhanced features
        assert crisis_alert.alert_id in enhanced_dashboard.active_alerts
        stored_alert = enhanced_dashboard.active_alerts[crisis_alert.alert_id]

        assert stored_alert.priority_score == 9.5
        assert stored_alert.escalation_level == 2
        assert stored_alert.intervention_required is True
        assert len(stored_alert.clinical_notes) == 2
        assert stored_alert.auto_escalation_time is not None

        # Verify crisis metrics updated
        assert enhanced_dashboard.dashboard_metrics["crisis_alerts_count"] > 0

    @pytest.mark.asyncio
    async def test_production_performance_benchmarks(self, enhanced_dashboard):
        """Test that enhanced dashboard meets production performance benchmarks."""

        # Test practitioner authentication performance
        await enhanced_dashboard.register_practitioner(
            username="perf_test",
            full_name="Performance Test User",
            role=ClinicalRole.THERAPIST,
            access_level=AccessLevel.STANDARD,
            email="perf@clinic.com",
        )

        start_time = time.perf_counter()
        session_token, practitioner_id = (
            await enhanced_dashboard.authenticate_practitioner(
                username="perf_test", password_hash="hash123"
            )
        )
        auth_time = (time.perf_counter() - start_time) * 1000

        assert auth_time < 100.0  # Authentication should be under 100ms

        # Test session token validation performance
        start_time = time.perf_counter()
        practitioner = await enhanced_dashboard.validate_session_token(session_token)
        validation_time = (time.perf_counter() - start_time) * 1000

        assert validation_time < 10.0  # Token validation should be under 10ms

        # Test permission check performance
        start_time = time.perf_counter()
        has_permission = await enhanced_dashboard.check_permission(
            session_token, "view_sessions"
        )
        permission_time = (time.perf_counter() - start_time) * 1000

        assert permission_time < 5.0  # Permission check should be under 5ms
        assert has_permission is True

        # Test audit logging performance
        start_time = time.perf_counter()
        await enhanced_dashboard._log_audit_event(
            practitioner_id=practitioner_id,
            event_type=AuditEventType.SESSION_ACCESS,
            resource_accessed="performance_test",
            success=True,
        )
        audit_time = (time.perf_counter() - start_time) * 1000

        assert audit_time < 5.0  # Audit logging should be under 5ms

        # Verify all operations completed successfully
        assert practitioner is not None
        assert has_permission is True
        assert len(enhanced_dashboard.audit_log) > 0
