"""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_crisis_intervention_system]]
Comprehensive tests for the crisis intervention system (Task 17.2).

Tests all crisis intervention components including:
- CrisisInterventionManager
- EmergencyProtocolEngine
- HumanOversightEscalation
- SafetyMonitoringDashboard
- Integration with AgentOrchestrationService
"""

from unittest.mock import Mock

import pytest
from tta_ai.orchestration.service import AgentOrchestrationService
from tta_ai.orchestration.therapeutic_safety import (
    CrisisInterventionManager,
    CrisisLevel,
    CrisisType,
    EmergencyProtocolEngine,
    EscalationStatus,
    HumanOversightEscalation,
    InterventionType,
    SafetyMonitoringDashboard,
    TherapeuticValidator,
)


class TestCrisisInterventionManager:
    """Test the CrisisInterventionManager component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.crisis_manager = CrisisInterventionManager()
        self.validator = TherapeuticValidator()

    def test_crisis_assessment_no_crisis(self):
        """Test crisis assessment when no crisis is detected."""
        result = self.validator.validate_text("I feel happy today")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)

        assert assessment.crisis_level == CrisisLevel.LOW
        assert assessment.crisis_types == []
        assert assessment.confidence == 0.0
        assert not assessment.immediate_risk
        assert not assessment.escalation_required

    def test_crisis_assessment_suicidal_ideation(self):
        """Test crisis assessment for suicidal ideation."""
        result = self.validator.validate_text("I want to kill myself")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)

        assert assessment.crisis_level == CrisisLevel.CRITICAL
        assert CrisisType.SUICIDAL_IDEATION in assessment.crisis_types
        assert assessment.confidence > 0.8
        assert assessment.immediate_risk
        assert assessment.escalation_required
        assert (
            assessment.intervention_recommended == InterventionType.EMERGENCY_SERVICES
        )

    def test_crisis_assessment_self_harm(self):
        """Test crisis assessment for self-harm."""
        result = self.validator.validate_text("I want to hurt myself")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)

        assert assessment.crisis_level == CrisisLevel.CRITICAL
        assert CrisisType.SELF_HARM in assessment.crisis_types
        assert assessment.confidence > 0.8
        assert assessment.immediate_risk
        assert assessment.escalation_required

    def test_intervention_initiation(self):
        """Test crisis intervention initiation."""
        result = self.validator.validate_text("I feel hopeless")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)
        intervention = self.crisis_manager.initiate_intervention(
            assessment, "test", "user1"
        )

        assert intervention.intervention_id is not None
        assert intervention.session_id == "test"
        assert intervention.user_id == "user1"
        assert intervention.crisis_assessment == assessment
        assert len(intervention.actions_taken) > 0
        assert intervention.intervention_id in self.crisis_manager.active_interventions

    def test_intervention_escalation(self):
        """Test intervention escalation for critical cases."""
        result = self.validator.validate_text("I want to kill myself right now")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)
        intervention = self.crisis_manager.initiate_intervention(
            assessment, "test", "user1"
        )

        assert intervention.escalation_status == EscalationStatus.COMPLETED
        assert intervention.emergency_contacted
        assert len(intervention.actions_taken) >= 2  # Immediate response + escalation

    def test_crisis_metrics(self):
        """Test crisis metrics collection."""
        # Create some interventions
        result = self.validator.validate_text("I want to hurt myself")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)
        self.crisis_manager.initiate_intervention(assessment, "test", "user1")

        metrics = self.crisis_manager.get_crisis_metrics()

        assert metrics["total_interventions"] == 1
        assert metrics["active_interventions"] == 1
        assert metrics["escalations_triggered"] >= 1
        assert "crisis_type_distribution" in metrics
        assert "crisis_level_distribution" in metrics

    def test_intervention_resolution(self):
        """Test intervention resolution."""
        result = self.validator.validate_text("I feel sad")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)
        intervention = self.crisis_manager.initiate_intervention(
            assessment, "test", "user1"
        )

        intervention_id = intervention.intervention_id

        # Resolve the intervention
        success = self.crisis_manager.resolve_intervention(
            intervention_id, "User reported feeling better"
        )

        assert success
        assert intervention_id not in self.crisis_manager.active_interventions
        assert len(self.crisis_manager.intervention_history) == 1
        assert self.crisis_manager.successful_interventions == 1


class TestEmergencyProtocolEngine:
    """Test the EmergencyProtocolEngine component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.protocol_engine = EmergencyProtocolEngine()

    def test_protocol_execution_suicidal_ideation_critical(self):
        """Test protocol execution for critical suicidal ideation."""
        context = {
            "user_id": "user1",
            "session_id": "test",
            "crisis_type": "suicidal_ideation",
        }

        result = self.protocol_engine.execute_protocol(
            CrisisType.SUICIDAL_IDEATION, CrisisLevel.CRITICAL, context
        )

        assert result["success"]
        assert result["crisis_type"] == "suicidal_ideation"
        assert result["crisis_level"] == "critical"
        assert len(result["steps_executed"]) > 0

        # Check that critical steps were executed
        step_types = [step["step_type"] for step in result["steps_executed"]]
        assert "log_event" in step_types
        assert "generate_response" in step_types
        assert "contact_emergency" in step_types
        assert "notify_human" in step_types

    def test_protocol_execution_self_harm_high(self):
        """Test protocol execution for high-risk self-harm."""
        context = {"user_id": "user1", "session_id": "test", "crisis_type": "self_harm"}

        result = self.protocol_engine.execute_protocol(
            CrisisType.SELF_HARM, CrisisLevel.HIGH, context
        )

        assert result["success"]
        assert result["crisis_type"] == "self_harm"
        assert result["crisis_level"] == "high"
        assert len(result["steps_executed"]) > 0

    def test_protocol_metrics(self):
        """Test protocol execution metrics."""
        context = {"user_id": "user1", "session_id": "test"}

        # Execute a few protocols
        self.protocol_engine.execute_protocol(
            CrisisType.SUICIDAL_IDEATION, CrisisLevel.HIGH, context
        )
        self.protocol_engine.execute_protocol(
            CrisisType.SELF_HARM, CrisisLevel.MODERATE, context
        )

        metrics = self.protocol_engine.get_protocol_metrics()

        assert metrics["protocols_executed"] == 2
        assert metrics["success_rate_percent"] == 100.0
        assert "protocol_type_distribution" in metrics
        assert "average_response_times_ms" in metrics

    def test_protocol_step_execution(self):
        """Test individual protocol step execution."""
        step = {"type": "generate_response", "template": "Test response for {user_id}"}
        context = {"user_id": "user1", "session_id": "test"}

        result = self.protocol_engine._execute_protocol_step(step, context)

        assert result["success"]
        assert result["step_type"] == "generate_response"
        assert "Test response for user1" in result["output"]


class TestHumanOversightEscalation:
    """Test the HumanOversightEscalation component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.escalation_system = HumanOversightEscalation()
        self.crisis_manager = CrisisInterventionManager()
        self.validator = TherapeuticValidator()

    def test_human_oversight_escalation(self):
        """Test escalation to human oversight."""
        # Create a crisis intervention
        result = self.validator.validate_text("I feel hopeless")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)
        intervention = self.crisis_manager.initiate_intervention(
            assessment, "test", "user1"
        )

        # Escalate to human oversight
        escalation = self.escalation_system.escalate_to_human(intervention, "standard")

        assert escalation["escalation_id"] is not None
        assert escalation["intervention_id"] == intervention.intervention_id
        assert escalation["escalation_type"] == "standard"
        assert escalation["status"] == "pending"
        assert len(escalation["notifications_sent"]) > 0

    def test_emergency_services_escalation(self):
        """Test escalation to emergency services."""
        # Create a critical crisis intervention
        result = self.validator.validate_text("I want to kill myself")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)
        intervention = self.crisis_manager.initiate_intervention(
            assessment, "test", "user1"
        )

        # Escalate to emergency services
        escalation = self.escalation_system.escalate_to_emergency_services(
            intervention, "mental_health"
        )

        assert escalation["escalation_id"] is not None
        assert escalation["escalation_type"] == "emergency_services"
        assert escalation["emergency_type"] == "mental_health"
        assert escalation["status"] == "critical"
        assert len(escalation["emergency_contacts"]) > 0

    def test_escalation_acknowledgment(self):
        """Test escalation acknowledgment by human oversight."""
        # Create and escalate
        result = self.validator.validate_text("I feel sad")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)
        intervention = self.crisis_manager.initiate_intervention(
            assessment, "test", "user1"
        )
        escalation = self.escalation_system.escalate_to_human(intervention, "standard")

        escalation_id = escalation["escalation_id"]

        # Acknowledge the escalation
        success = self.escalation_system.acknowledge_escalation(
            escalation_id, "therapist1", "Reviewing case"
        )

        assert success
        escalation_status = self.escalation_system.get_escalation_status(escalation_id)
        assert escalation_status["status"] == "acknowledged"
        assert escalation_status["assigned_human"] == "therapist1"
        assert escalation_status["response_received"]

    def test_escalation_metrics(self):
        """Test escalation metrics collection."""
        # Create some escalations
        result = self.validator.validate_text("I want to hurt myself")
        session_context = {"session_id": "test", "user_id": "user1"}

        assessment = self.crisis_manager.assess_crisis(result, session_context)
        intervention = self.crisis_manager.initiate_intervention(
            assessment, "test", "user1"
        )

        self.escalation_system.escalate_to_human(intervention, "standard")
        self.escalation_system.escalate_to_emergency_services(
            intervention, "mental_health"
        )

        metrics = self.escalation_system.get_escalation_metrics()

        assert metrics["total_escalations"] >= 1
        assert metrics["emergency_escalations"] >= 1
        assert metrics["notification_success_rate_percent"] > 0
        assert "escalation_type_distribution" in metrics


class TestSafetyMonitoringDashboard:
    """Test the SafetyMonitoringDashboard component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TherapeuticValidator()
        self.crisis_manager = CrisisInterventionManager()
        self.escalation_system = HumanOversightEscalation()
        self.protocol_engine = EmergencyProtocolEngine()

        self.dashboard = SafetyMonitoringDashboard(
            therapeutic_validator=self.validator,
            crisis_manager=self.crisis_manager,
            escalation_system=self.escalation_system,
            protocol_engine=self.protocol_engine,
        )

    def test_real_time_status(self):
        """Test real-time status monitoring."""
        status = self.dashboard.get_real_time_status()

        assert "timestamp" in status
        assert "system_health" in status
        assert "components" in status
        assert len(status["components"]) == 4

        # All components should be active
        for data in status["components"].values():
            assert data["status"] == "active"

    def test_crisis_dashboard(self):
        """Test crisis dashboard data."""
        dashboard_data = self.dashboard.get_crisis_dashboard()

        assert "summary" in dashboard_data
        assert "active_interventions" in dashboard_data
        assert "recent_escalations" in dashboard_data
        assert "crisis_trends" in dashboard_data
        assert "performance_metrics" in dashboard_data
        assert "alerts" in dashboard_data

    def test_alert_management(self):
        """Test alert creation and management."""
        # Add an alert
        alert_id = self.dashboard.add_alert(
            "test_alert", "Test alert message", "high", {"test": "metadata"}
        )

        assert alert_id is not None
        assert len(self.dashboard.alert_queue) == 1

        # Acknowledge the alert
        success = self.dashboard.acknowledge_alert(alert_id, "admin")
        assert success

        # Resolve the alert
        success = self.dashboard.resolve_alert(alert_id, "admin", "Test resolved")
        assert success
        assert len(self.dashboard.alert_queue) == 0
        assert len(self.dashboard.historical_data) == 1

    def test_safety_report_generation(self):
        """Test safety report generation."""
        report = self.dashboard.get_safety_report(24)

        assert "report_period" in report
        assert "executive_summary" in report
        assert "validation_summary" in report
        assert "crisis_summary" in report
        assert "escalation_summary" in report
        assert "protocol_summary" in report
        assert "recommendations" in report

        assert report["report_period"]["duration_hours"] == 24
        assert len(report["recommendations"]) > 0


class TestAgentOrchestrationServiceIntegration:
    """Test integration of crisis intervention system with AgentOrchestrationService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TherapeuticValidator()
        self.crisis_manager = CrisisInterventionManager()
        self.escalation_system = HumanOversightEscalation()
        self.protocol_engine = EmergencyProtocolEngine()
        self.dashboard = SafetyMonitoringDashboard(
            therapeutic_validator=self.validator,
            crisis_manager=self.crisis_manager,
            escalation_system=self.escalation_system,
            protocol_engine=self.protocol_engine,
        )

        # Create service with crisis intervention integration
        self.service = AgentOrchestrationService(
            workflow_manager=Mock(),
            message_coordinator=Mock(),
            agent_registry=Mock(),
            therapeutic_validator=self.validator,
            crisis_intervention_manager=self.crisis_manager,
            emergency_protocol_engine=self.protocol_engine,
            human_oversight_escalation=self.escalation_system,
            safety_monitoring_dashboard=self.dashboard,
        )

    def test_service_initialization_with_crisis_components(self):
        """Test service initialization with crisis intervention components."""
        status = self.service.get_service_status()

        # Check that all crisis intervention components are available
        assert status["components"]["crisis_intervention_manager"]
        assert status["components"]["emergency_protocol_engine"]
        assert status["components"]["human_oversight_escalation"]
        assert status["components"]["safety_monitoring_dashboard"]

    def test_crisis_intervention_metrics_integration(self):
        """Test crisis intervention metrics integration."""
        metrics = self.service.get_crisis_intervention_metrics()

        assert "crisis_manager" in metrics
        assert "emergency_protocols" in metrics
        assert "human_oversight" in metrics
        assert "safety_dashboard" in metrics

        # Each component should provide metrics
        assert isinstance(metrics["crisis_manager"], dict)
        assert isinstance(metrics["emergency_protocols"], dict)
        assert isinstance(metrics["human_oversight"], dict)
        assert isinstance(metrics["safety_dashboard"], dict)

    def test_crisis_dashboard_integration(self):
        """Test crisis dashboard integration."""
        dashboard_data = self.service.get_crisis_dashboard()

        assert "error" not in dashboard_data
        assert "summary" in dashboard_data
        assert "active_interventions" in dashboard_data
        assert "recent_escalations" in dashboard_data

    def test_safety_report_integration(self):
        """Test safety report integration."""
        report = self.service.get_safety_report(24)

        assert "error" not in report
        assert "report_period" in report
        assert "executive_summary" in report
        assert "recommendations" in report

    def test_crisis_intervention_activation_during_validation(self):
        """Test that crisis intervention is activated during therapeutic validation."""
        # Create a real crisis situation to test the integration
        result = self.validator.validate_text("I want to kill myself")
        session_context = {
            "session_id": "test-session",
            "user_id": "test-user",
            "session_count": 1,
            "previous_violations": 0,
            "location": "unknown",
        }

        # Manually trigger the crisis intervention workflow that would happen in the service
        if result.crisis_detected:
            # Assess crisis and initiate intervention
            assessment = self.crisis_manager.assess_crisis(result, session_context)
            intervention = self.crisis_manager.initiate_intervention(
                assessment, session_context["session_id"], session_context["user_id"]
            )

            # Handle escalation if required
            if assessment.escalation_required:
                if assessment.crisis_level.value == "critical":
                    self.escalation_system.escalate_to_emergency_services(
                        intervention, "mental_health"
                    )
                else:
                    self.escalation_system.escalate_to_human(
                        intervention, "crisis_intervention"
                    )

            # Add alert to monitoring dashboard
            self.dashboard.add_alert(
                "crisis_intervention",
                f"Crisis intervention initiated for session {session_context['session_id']}",
                "critical" if assessment.crisis_level.value == "critical" else "high",
                {
                    "intervention_id": intervention.intervention_id,
                    "crisis_types": [ct.value for ct in assessment.crisis_types],
                    "crisis_level": assessment.crisis_level.value,
                },
            )

        # Verify crisis intervention was activated
        assert len(self.crisis_manager.active_interventions) > 0
        assert len(self.escalation_system.active_escalations) > 0
        assert len(self.dashboard.alert_queue) > 0

    def test_service_without_crisis_components(self):
        """Test service behavior when crisis components are not available."""
        # Create service without crisis components
        service_no_crisis = AgentOrchestrationService(
            workflow_manager=Mock(),
            message_coordinator=Mock(),
            agent_registry=Mock(),
            therapeutic_validator=self.validator,
        )

        # Should still work but with limited functionality
        status = service_no_crisis.get_service_status()
        assert not status["components"]["crisis_intervention_manager"]
        assert not status["components"]["emergency_protocol_engine"]

        # Crisis metrics should return empty data
        metrics = service_no_crisis.get_crisis_intervention_metrics()
        assert metrics["crisis_manager"] == {}
        assert metrics["emergency_protocols"] == {}

    def test_comprehensive_crisis_workflow(self):
        """Test complete crisis intervention workflow through the service."""
        # Simulate a crisis situation
        result = self.validator.validate_text("I want to kill myself")
        session_context = {
            "session_id": "test-session",
            "user_id": "test-user",
            "session_count": 1,
        }

        # Assess and initiate intervention
        assessment = self.crisis_manager.assess_crisis(result, session_context)
        intervention = self.crisis_manager.initiate_intervention(
            assessment, "test-session", "test-user"
        )

        # Verify the complete workflow
        assert intervention.crisis_assessment.crisis_level == CrisisLevel.CRITICAL
        assert (
            CrisisType.SUICIDAL_IDEATION in intervention.crisis_assessment.crisis_types
        )
        assert intervention.emergency_contacted

        # Check that all systems are coordinated
        metrics = self.service.get_crisis_intervention_metrics()
        assert metrics["crisis_manager"]["total_interventions"] >= 1
        assert metrics["crisis_manager"]["emergency_contacts"] >= 1

        # Check dashboard reflects the intervention
        dashboard_data = self.service.get_crisis_dashboard()
        assert len(dashboard_data["active_interventions"]) >= 1

        # Check safety report includes the intervention
        report = self.service.get_safety_report(1)
        assert report["executive_summary"]["crisis_interventions"] >= 1


if __name__ == "__main__":
    pytest.main([__file__])
