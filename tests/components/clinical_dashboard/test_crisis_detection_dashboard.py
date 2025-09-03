"""
Tests for Crisis Detection Dashboard Components

This module tests the crisis detection dashboard functionality including
EmotionalSafetySystem integration, real-time crisis notifications,
clinical intervention workflows, and crisis response management.
"""

import pytest
import pytest_asyncio

from src.components.clinical_dashboard.crisis_detection_dashboard import (
    CrisisDetectionDashboard,
    InterventionStatus,
    InterventionType,
)
from src.components.therapeutic_systems.emotional_safety_system import (
    CrisisIndicator,
    CrisisLevel,
)


class MockEmotionalSafetySystem:
    """Mock EmotionalSafetySystem for testing."""

    def __init__(self):
        self.crisis_assessments = []
        self.mock_assessment_result = {
            "crisis_detected": False,
            "crisis_level": "none",
            "immediate_intervention": False,
            "indicators": [],
            "response_time": 0.05,
            "assessment_id": "test_assessment_123",
            "risk_score": 0.1,
        }

    async def assess_crisis_risk(
        self, user_id, user_input, session_context=None, user_history=None
    ):
        """Mock crisis risk assessment."""
        self.crisis_assessments.append(
            {
                "user_id": user_id,
                "user_input": user_input,
                "session_context": session_context,
                "user_history": user_history,
            }
        )
        return self.mock_assessment_result.copy()


class TestCrisisDetectionDashboard:
    """Test Crisis Detection Dashboard Components functionality."""

    @pytest_asyncio.fixture
    async def mock_safety_system(self):
        """Create mock emotional safety system."""
        return MockEmotionalSafetySystem()

    @pytest_asyncio.fixture
    async def crisis_dashboard(self, mock_safety_system):
        """Create crisis detection dashboard with mock safety system."""
        dashboard = CrisisDetectionDashboard(mock_safety_system)
        await dashboard.initialize()
        yield dashboard
        await dashboard.shutdown()

    @pytest.mark.asyncio
    async def test_dashboard_initialization(self, crisis_dashboard):
        """Test crisis detection dashboard initialization."""
        # Verify dashboard is initialized
        health = await crisis_dashboard.health_check()
        assert health["status"] == "healthy"
        assert health["service"] == "crisis_detection_dashboard"

        # Verify monitoring task is running
        assert health["monitoring_task_running"] is True

        # Verify initial state
        assert len(crisis_dashboard.active_crisis_events) == 0
        assert len(crisis_dashboard.active_interventions) == 0
        assert len(crisis_dashboard.pending_notifications) == 0

    @pytest.mark.asyncio
    async def test_process_crisis_assessment_no_crisis(
        self, crisis_dashboard, mock_safety_system
    ):
        """Test processing crisis assessment when no crisis is detected."""
        user_id = "test_user_123"
        session_id = "session_456"
        user_input = "I'm feeling okay today"

        # Process assessment
        crisis_event = await crisis_dashboard.process_crisis_assessment(
            user_id=user_id,
            session_id=session_id,
            user_input=user_input,
        )

        # Verify assessment was called
        assert len(mock_safety_system.crisis_assessments) == 1
        assert mock_safety_system.crisis_assessments[0]["user_id"] == user_id
        assert mock_safety_system.crisis_assessments[0]["user_input"] == user_input

        # Verify crisis event
        assert crisis_event.user_id == user_id
        assert crisis_event.session_id == session_id
        assert crisis_event.crisis_level == CrisisLevel.NONE
        assert crisis_event.user_input == user_input
        assert crisis_event.response_time_ms > 0

        # Verify no active crisis events (since no crisis detected)
        assert len(crisis_dashboard.active_crisis_events) == 0

    @pytest.mark.asyncio
    async def test_process_crisis_assessment_with_crisis(
        self, crisis_dashboard, mock_safety_system
    ):
        """Test processing crisis assessment when crisis is detected."""
        user_id = "test_user_crisis"
        session_id = "session_crisis"
        user_input = "I want to end it all"

        # Configure mock to detect crisis
        mock_safety_system.mock_assessment_result = {
            "crisis_detected": True,
            "crisis_level": "high",
            "immediate_intervention": True,
            "indicators": ["suicide_ideation", "hopelessness"],
            "response_time": 0.08,
            "assessment_id": "crisis_assessment_456",
            "risk_score": 0.85,
        }

        # Process assessment
        crisis_event = await crisis_dashboard.process_crisis_assessment(
            user_id=user_id,
            session_id=session_id,
            user_input=user_input,
        )

        # Verify crisis event was created
        assert crisis_event.crisis_level == CrisisLevel.HIGH
        assert len(crisis_event.indicators) == 2
        assert CrisisIndicator.SUICIDE_IDEATION in crisis_event.indicators
        assert CrisisIndicator.HOPELESSNESS in crisis_event.indicators
        assert crisis_event.intervention_required is True
        assert crisis_event.escalation_needed is True

        # Verify active crisis event was stored
        assert len(crisis_dashboard.active_crisis_events) == 1
        assert crisis_event.event_id in crisis_dashboard.active_crisis_events

        # Verify crisis history was updated
        assert len(crisis_dashboard.crisis_history[user_id]) == 1

        # Verify metrics were updated
        assert crisis_dashboard.dashboard_metrics["crisis_events_detected"] == 1

    @pytest.mark.asyncio
    async def test_crisis_intervention_creation(
        self, crisis_dashboard, mock_safety_system
    ):
        """Test that appropriate interventions are created for crisis events."""
        user_id = "test_user_intervention"
        session_id = "session_intervention"
        user_input = "I'm thinking about suicide"

        # Configure mock for critical crisis
        mock_safety_system.mock_assessment_result = {
            "crisis_detected": True,
            "crisis_level": "critical",
            "immediate_intervention": True,
            "indicators": ["suicide_ideation", "self_harm"],
            "response_time": 0.06,
            "assessment_id": "critical_assessment_789",
            "risk_score": 0.95,
        }

        # Process assessment
        crisis_event = await crisis_dashboard.process_crisis_assessment(
            user_id=user_id,
            session_id=session_id,
            user_input=user_input,
        )

        # Verify interventions were created
        assert len(crisis_dashboard.active_interventions) > 0
        assert crisis_dashboard.dashboard_metrics["interventions_initiated"] > 0

        # Check for expected intervention types for critical crisis
        intervention_types = [
            intervention.intervention_type
            for intervention in crisis_dashboard.active_interventions.values()
        ]

        assert InterventionType.IMMEDIATE_CONTACT in intervention_types
        assert InterventionType.EMERGENCY_SERVICES in intervention_types
        assert InterventionType.SAFETY_PLANNING in intervention_types

        # Verify all interventions are for the correct user and crisis
        for intervention in crisis_dashboard.active_interventions.values():
            assert intervention.user_id == user_id
            assert intervention.crisis_event_id == crisis_event.event_id
            assert intervention.status == InterventionStatus.PENDING

    @pytest.mark.asyncio
    async def test_crisis_notification_system(
        self, crisis_dashboard, mock_safety_system
    ):
        """Test crisis notification system."""
        user_id = "test_user_notification"
        session_id = "session_notification"
        user_input = "I can't take it anymore"

        # Configure mock for high-risk crisis
        mock_safety_system.mock_assessment_result = {
            "crisis_detected": True,
            "crisis_level": "high",
            "immediate_intervention": True,
            "indicators": ["severe_depression", "hopelessness"],
            "response_time": 0.07,
            "assessment_id": "high_risk_assessment_101",
            "risk_score": 0.78,
        }

        # Process assessment
        crisis_event = await crisis_dashboard.process_crisis_assessment(
            user_id=user_id,
            session_id=session_id,
            user_input=user_input,
        )

        # Verify notifications were created
        assert len(crisis_dashboard.pending_notifications) > 0
        assert crisis_dashboard.dashboard_metrics["notifications_sent"] > 0

        # Check notification details
        notification = list(crisis_dashboard.pending_notifications.values())[0]
        assert notification.crisis_event_id == crisis_event.event_id
        assert notification.priority == "high"
        assert notification.response_required is True
        assert notification.response_deadline is not None
        assert not notification.acknowledged

        # Verify notification message contains crisis details
        assert user_id in notification.message
        assert "high" in notification.message.lower()
        assert "severe_depression" in notification.message

    @pytest.mark.asyncio
    async def test_dashboard_summary(self, crisis_dashboard, mock_safety_system):
        """Test crisis dashboard summary generation."""
        # Create multiple crisis events with different levels
        crisis_configs = [
            ("user1", "critical", ["suicide_ideation"]),
            ("user2", "high", ["self_harm", "hopelessness"]),
            ("user3", "moderate", ["severe_depression"]),
        ]

        for user_id, level, indicators in crisis_configs:
            mock_safety_system.mock_assessment_result = {
                "crisis_detected": True,
                "crisis_level": level,
                "immediate_intervention": level in ["critical", "high"],
                "indicators": indicators,
                "response_time": 0.05,
                "assessment_id": f"assessment_{user_id}",
                "risk_score": 0.8 if level == "critical" else 0.6,
            }

            await crisis_dashboard.process_crisis_assessment(
                user_id=user_id,
                session_id=f"session_{user_id}",
                user_input=f"Crisis input from {user_id}",
            )

        # Get dashboard summary
        summary = await crisis_dashboard.get_crisis_dashboard_summary()

        # Verify summary data
        assert summary["active_crisis_events"] == 3
        assert summary["crisis_counts_by_level"]["CRITICAL"] == 1
        assert summary["crisis_counts_by_level"]["HIGH"] == 1
        assert summary["crisis_counts_by_level"]["MODERATE"] == 1
        assert summary["pending_interventions"] > 0
        assert summary["unacknowledged_notifications"] > 0
        assert "dashboard_metrics" in summary
        assert "last_updated" in summary

    @pytest.mark.asyncio
    async def test_notification_acknowledgment(
        self, crisis_dashboard, mock_safety_system
    ):
        """Test notification acknowledgment functionality."""
        user_id = "test_user_ack"
        practitioner_id = "practitioner_123"

        # Create crisis event with notification
        mock_safety_system.mock_assessment_result = {
            "crisis_detected": True,
            "crisis_level": "high",
            "immediate_intervention": True,
            "indicators": ["panic_attack"],
            "response_time": 0.04,
            "assessment_id": "ack_test_assessment",
            "risk_score": 0.7,
        }

        await crisis_dashboard.process_crisis_assessment(
            user_id=user_id,
            session_id="session_ack",
            user_input="I'm having a panic attack",
        )

        # Get notification ID
        notification_id = list(crisis_dashboard.pending_notifications.keys())[0]
        notification = crisis_dashboard.pending_notifications[notification_id]

        # Verify notification is not acknowledged initially
        assert not notification.acknowledged
        assert notification.acknowledged_at is None

        # Acknowledge notification
        success = await crisis_dashboard.acknowledge_notification(
            notification_id, practitioner_id
        )
        assert success is True

        # Verify notification is now acknowledged
        assert notification.acknowledged is True
        assert notification.acknowledged_at is not None

    @pytest.mark.asyncio
    async def test_intervention_status_updates(
        self, crisis_dashboard, mock_safety_system
    ):
        """Test intervention status update functionality."""
        user_id = "test_user_intervention_update"
        practitioner_id = "practitioner_456"

        # Create crisis event with interventions
        mock_safety_system.mock_assessment_result = {
            "crisis_detected": True,
            "crisis_level": "high",
            "immediate_intervention": True,
            "indicators": ["suicide_ideation"],
            "response_time": 0.06,
            "assessment_id": "intervention_update_test",
            "risk_score": 0.82,
        }

        await crisis_dashboard.process_crisis_assessment(
            user_id=user_id,
            session_id="session_intervention_update",
            user_input="I want to hurt myself",
        )

        # Get intervention ID
        intervention_id = list(crisis_dashboard.active_interventions.keys())[0]
        intervention = crisis_dashboard.active_interventions[intervention_id]

        # Verify initial status
        assert intervention.status == InterventionStatus.PENDING
        assert intervention.assigned_practitioner is None
        assert intervention.started_at is None

        # Update to in progress
        success = await crisis_dashboard.update_intervention_status(
            intervention_id=intervention_id,
            status=InterventionStatus.IN_PROGRESS,
            practitioner_id=practitioner_id,
            notes="Starting immediate contact with patient",
        )
        assert success is True

        # Verify status update
        assert intervention.status == InterventionStatus.IN_PROGRESS
        assert intervention.assigned_practitioner == practitioner_id
        assert intervention.started_at is not None
        assert len(intervention.notes) == 1

        # Update to completed
        success = await crisis_dashboard.update_intervention_status(
            intervention_id=intervention_id,
            status=InterventionStatus.COMPLETED,
            practitioner_id=practitioner_id,
            notes="Patient stabilized and safety plan created",
        )
        assert success is True

        # Verify completion
        assert intervention.status == InterventionStatus.COMPLETED
        assert intervention.completed_at is not None
        assert len(intervention.notes) == 2
        assert crisis_dashboard.dashboard_metrics["successful_interventions"] == 1

    @pytest.mark.asyncio
    async def test_crisis_response_performance(
        self, crisis_dashboard, mock_safety_system
    ):
        """Test crisis response performance benchmarks."""
        import time

        user_id = "test_user_performance"
        session_id = "session_performance"
        user_input = "Crisis situation requiring immediate response"

        # Configure mock for crisis detection
        mock_safety_system.mock_assessment_result = {
            "crisis_detected": True,
            "crisis_level": "critical",
            "immediate_intervention": True,
            "indicators": ["suicide_ideation", "self_harm"],
            "response_time": 0.05,
            "assessment_id": "performance_test",
            "risk_score": 0.9,
        }

        # Measure crisis processing time
        start_time = time.perf_counter()
        crisis_event = await crisis_dashboard.process_crisis_assessment(
            user_id=user_id,
            session_id=session_id,
            user_input=user_input,
        )
        processing_time = (time.perf_counter() - start_time) * 1000

        # Verify performance benchmarks
        assert processing_time < 1000.0  # Should process in under 1 second
        assert crisis_event.response_time_ms < 500.0  # Crisis assessment should be fast

        # Verify crisis response was triggered quickly
        assert len(crisis_dashboard.active_interventions) > 0
        assert len(crisis_dashboard.pending_notifications) > 0

        # Test dashboard summary performance
        start_time = time.perf_counter()
        summary = await crisis_dashboard.get_crisis_dashboard_summary()
        summary_time = (time.perf_counter() - start_time) * 1000

        assert summary_time < 100.0  # Dashboard summary should be very fast
        assert "active_crisis_events" in summary

    @pytest.mark.asyncio
    async def test_crisis_escalation_logic(self, crisis_dashboard, mock_safety_system):
        """Test crisis escalation logic and timeouts."""
        user_id = "test_user_escalation"

        # Create critical crisis event
        mock_safety_system.mock_assessment_result = {
            "crisis_detected": True,
            "crisis_level": "critical",
            "immediate_intervention": True,
            "indicators": ["suicide_ideation", "psychosis"],
            "response_time": 0.04,
            "assessment_id": "escalation_test",
            "risk_score": 0.98,
        }

        crisis_event = await crisis_dashboard.process_crisis_assessment(
            user_id=user_id,
            session_id="session_escalation",
            user_input="I'm going to kill myself right now",
        )

        # Verify escalation is needed
        assert crisis_event.escalation_needed is True
        assert crisis_event.crisis_level == CrisisLevel.CRITICAL

        # Verify emergency interventions were created
        intervention_types = [
            intervention.intervention_type
            for intervention in crisis_dashboard.active_interventions.values()
        ]
        assert InterventionType.EMERGENCY_SERVICES in intervention_types
        assert InterventionType.IMMEDIATE_CONTACT in intervention_types

        # Verify critical priority notification was sent
        notifications = list(crisis_dashboard.pending_notifications.values())
        critical_notifications = [n for n in notifications if n.priority == "critical"]
        assert len(critical_notifications) > 0
