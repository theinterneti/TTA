"""
Tests for TherapeuticEmotionalSafetySystem

This module tests the therapeutic emotional safety system implementation
including crisis detection, safety protocols, and intervention capabilities.
"""

import pytest

from src.components.therapeutic_systems.emotional_safety_system import (
    CrisisIndicator,
    CrisisLevel,
    TherapeuticEmotionalSafetySystem,
)


class TestTherapeuticEmotionalSafetySystem:
    """Test TherapeuticEmotionalSafetySystem functionality."""

    @pytest.fixture
    def safety_system(self):
        """Create therapeutic emotional safety system instance."""
        return TherapeuticEmotionalSafetySystem()

    @pytest.mark.asyncio
    async def test_initialization(self, safety_system):
        """Test system initialization."""
        await safety_system.initialize()

        # Should have crisis patterns configured
        assert len(safety_system.crisis_patterns) > 0
        assert CrisisIndicator.SUICIDE_IDEATION in safety_system.crisis_patterns
        assert CrisisIndicator.SELF_HARM in safety_system.crisis_patterns

        # Should have crisis resources configured
        assert len(safety_system.crisis_resources) > 0
        assert "suicide_prevention" in safety_system.crisis_resources
        assert "emergency" in safety_system.crisis_resources

        # Should be monitoring enabled
        assert safety_system.monitoring_active is True

    @pytest.mark.asyncio
    async def test_assess_crisis_risk_no_crisis(self, safety_system):
        """Test crisis risk assessment with no crisis detected."""
        await safety_system.initialize()

        result = await safety_system.assess_crisis_risk(
            user_id="test_user_001",
            user_input="I'm feeling good today and looking forward to tomorrow",
            session_context=None,
        )

        # Should return expected structure
        assert "crisis_detected" in result
        assert "crisis_level" in result
        assert "immediate_intervention" in result
        assert "indicators" in result
        assert "response_time" in result

        # Should detect no crisis
        assert result["crisis_detected"] is False
        assert result["crisis_level"] == CrisisLevel.NONE.value
        assert result["immediate_intervention"] is False
        assert len(result["indicators"]) == 0

        # Should meet response time requirement
        assert result["response_time"] < 1.0

    @pytest.mark.asyncio
    async def test_assess_crisis_risk_suicide_ideation(self, safety_system):
        """Test crisis risk assessment with suicide ideation."""
        await safety_system.initialize()

        result = await safety_system.assess_crisis_risk(
            user_id="test_user_002",
            user_input="I've been thinking about ending it all, I want to kill myself",
            session_context=None,
        )

        # Should detect crisis
        assert result["crisis_detected"] is True
        assert result["crisis_level"] in [
            CrisisLevel.HIGH.value,
            CrisisLevel.CRITICAL.value,
        ]
        assert result["immediate_intervention"] is True
        assert CrisisIndicator.SUICIDE_IDEATION.value in result["indicators"]

        # Should meet response time requirement
        assert result["response_time"] < 1.0

    @pytest.mark.asyncio
    async def test_assess_crisis_risk_self_harm(self, safety_system):
        """Test crisis risk assessment with self-harm indicators."""
        await safety_system.initialize()

        result = await safety_system.assess_crisis_risk(
            user_id="test_user_003",
            user_input="I've been cutting myself to deal with the pain",
            session_context=None,
        )

        # Should detect crisis
        assert result["crisis_detected"] is True
        assert result["crisis_level"] != CrisisLevel.NONE.value
        assert CrisisIndicator.SELF_HARM.value in result["indicators"]

        # Should meet response time requirement
        assert result["response_time"] < 1.0

    @pytest.mark.asyncio
    async def test_assess_crisis_risk_hopelessness(self, safety_system):
        """Test crisis risk assessment with hopelessness indicators."""
        await safety_system.initialize()

        result = await safety_system.assess_crisis_risk(
            user_id="test_user_004",
            user_input="I feel completely hopeless, nothing will ever change",
            session_context=None,
        )

        # Should detect crisis
        assert result["crisis_detected"] is True
        assert CrisisIndicator.HOPELESSNESS.value in result["indicators"]

        # Should meet response time requirement
        assert result["response_time"] < 1.0

    @pytest.mark.asyncio
    async def test_assess_crisis_risk_multiple_indicators(self, safety_system):
        """Test crisis risk assessment with multiple indicators."""
        await safety_system.initialize()

        result = await safety_system.assess_crisis_risk(
            user_id="test_user_005",
            user_input="I feel hopeless and have been thinking about killing myself",
            session_context=None,
        )

        # Should detect multiple indicators
        assert result["crisis_detected"] is True
        assert len(result["indicators"]) >= 2
        assert CrisisIndicator.SUICIDE_IDEATION.value in result["indicators"]
        assert CrisisIndicator.HOPELESSNESS.value in result["indicators"]

        # Should be high or critical level
        assert result["crisis_level"] in [
            CrisisLevel.HIGH.value,
            CrisisLevel.CRITICAL.value,
        ]
        assert result["immediate_intervention"] is True

    @pytest.mark.asyncio
    async def test_assess_crisis_risk_empty_input(self, safety_system):
        """Test crisis risk assessment with empty input."""
        await safety_system.initialize()

        result = await safety_system.assess_crisis_risk(
            user_id="test_user_006", user_input="", session_context=None
        )

        # Should handle gracefully
        assert result["crisis_detected"] is False
        assert result["crisis_level"] == CrisisLevel.NONE.value
        assert result["immediate_intervention"] is False
        assert len(result["indicators"]) == 0
        assert result["response_time"] < 0.1  # Should be very fast for empty input

    @pytest.mark.asyncio
    async def test_activate_crisis_protocols_critical(self, safety_system):
        """Test crisis protocol activation for critical situations."""
        await safety_system.initialize()

        result = await safety_system.activate_crisis_protocols(
            user_id="test_user_007",
            crisis_level=CrisisLevel.CRITICAL,
            indicators=[CrisisIndicator.SUICIDE_IDEATION],
        )

        # Should activate protocols
        assert result["protocols_activated"] is True
        assert len(result["active_protocols"]) > 0
        assert result["emergency_contacts_notified"] is True
        assert result["professional_escalation"] is True
        assert result["crisis_level"] == CrisisLevel.CRITICAL.value

    @pytest.mark.asyncio
    async def test_activate_crisis_protocols_low_risk(self, safety_system):
        """Test crisis protocol activation for low risk situations."""
        await safety_system.initialize()

        result = await safety_system.activate_crisis_protocols(
            user_id="test_user_008",
            crisis_level=CrisisLevel.LOW,
            indicators=[CrisisIndicator.HOPELESSNESS],
        )

        # Should not activate major protocols for low risk
        assert result["protocols_activated"] is False
        assert result["emergency_contacts_notified"] is False
        assert result["professional_escalation"] is False

    @pytest.mark.asyncio
    async def test_provide_crisis_resources(self, safety_system):
        """Test crisis resource provision."""
        await safety_system.initialize()

        result = await safety_system.provide_crisis_resources(
            user_id="test_user_009",
            crisis_indicators=[
                CrisisIndicator.SUICIDE_IDEATION,
                CrisisIndicator.HOPELESSNESS,
            ],
        )

        # Should provide resources
        assert result["resources_provided"] is True
        assert result["crisis_hotline_provided"] is True
        assert result["resource_count"] > 0
        assert len(result["resources"]) > 0

    @pytest.mark.asyncio
    async def test_escalate_to_professional(self, safety_system):
        """Test professional escalation."""
        await safety_system.initialize()

        result = await safety_system.escalate_to_professional(
            user_id="test_user_010",
            crisis_level=CrisisLevel.CRITICAL,
            assessment_data={"indicators": ["suicide_ideation"]},
        )

        # Should escalate successfully
        assert result["professional_notified"] is True
        assert result["escalation_successful"] is True
        assert "response_time" in result
        assert result["crisis_level"] == CrisisLevel.CRITICAL.value

    @pytest.mark.asyncio
    async def test_create_safety_plan(self, safety_system):
        """Test safety plan creation."""
        await safety_system.initialize()

        result = await safety_system.create_safety_plan(
            user_id="test_user_011",
            risk_factors=["isolation", "substance_use"],
            protective_factors=["social_support", "coping_skills"],
        )

        # Should create safety plan
        assert result["safety_plan_created"] is True
        assert len(result["plan_elements"]) > 0
        assert "crisis_hotline" in result["plan_elements"]
        assert result["personalized"] is True

    @pytest.mark.asyncio
    async def test_setup_crisis_monitoring(self, safety_system):
        """Test crisis monitoring setup."""
        await safety_system.initialize()

        result = await safety_system.setup_crisis_monitoring(
            user_id="test_user_012", monitoring_level="enhanced"
        )

        # Should set up monitoring
        assert result["monitoring_activated"] is True
        assert result["monitoring_level"] == "enhanced"
        assert "check_frequency_minutes" in result
        assert "intervention_threshold" in result

    @pytest.mark.asyncio
    async def test_perform_monitoring_check(self, safety_system):
        """Test monitoring check performance."""
        await safety_system.initialize()

        # First set up monitoring
        await safety_system.setup_crisis_monitoring("test_user_013")

        result = await safety_system.perform_monitoring_check(
            user_id="test_user_013", check_type="automated_wellness_check"
        )

        # Should perform check
        assert "status" in result
        assert "intervention_adjusted" in result
        assert result["monitoring_active"] is True
        assert result["check_type"] == "automated_wellness_check"

    @pytest.mark.asyncio
    async def test_response_time_compliance(self, safety_system):
        """Test that all operations meet response time requirements."""
        await safety_system.initialize()

        # Test multiple crisis assessments
        test_inputs = [
            "I'm feeling okay today",
            "I've been thinking about suicide",
            "Everything feels hopeless",
            "I want to hurt myself",
            "",  # Empty input
        ]

        for i, user_input in enumerate(test_inputs):
            result = await safety_system.assess_crisis_risk(
                user_id=f"test_user_timing_{i}",
                user_input=user_input,
                session_context=None,
            )

            # All assessments should be under 1 second
            assert result["response_time"] < 1.0, (
                f"Response time {result['response_time']} exceeded 1s for input: {user_input}"
            )

    @pytest.mark.asyncio
    async def test_health_check(self, safety_system):
        """Test system health check."""
        await safety_system.initialize()

        health = await safety_system.health_check()

        assert "status" in health
        assert health["status"] == "healthy"
        assert "monitoring_enabled" in health
        assert health["monitoring_enabled"] is True
        assert "crisis_patterns_loaded" in health
        assert health["crisis_patterns_loaded"] > 0
        assert "response_times_compliant" in health

    def test_get_metrics(self, safety_system):
        """Test metrics collection."""
        metrics = safety_system.get_metrics()

        assert isinstance(metrics, dict)
        assert "crisis_assessments" in metrics
        assert "crises_detected" in metrics
        assert "protocols_activated" in metrics
        assert "average_response_time" in metrics
        assert "crisis_detection_rate" in metrics
        assert "response_time_compliance" in metrics

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, safety_system):
        """Test compatibility with E2E test interface expectations."""
        await safety_system.initialize()

        # Test with parameters matching E2E test expectations
        result = await safety_system.assess_crisis_risk(
            user_id="demo_crisis_user",
            user_input="I've been thinking about ending it all",
            session_context=None,
        )

        # Should match E2E test expected structure
        expected_keys = [
            "crisis_detected",
            "crisis_level",
            "immediate_intervention",
            "indicators",
            "response_time",
        ]
        for key in expected_keys:
            assert key in result

        # Should detect crisis for this input
        assert result["crisis_detected"] is True
        assert result["crisis_level"] != "NONE"
        assert result["immediate_intervention"] is True

        # Should meet response time requirement
        assert result["response_time"] < 1.0

    @pytest.mark.asyncio
    async def test_error_handling(self, safety_system):
        """Test error handling in crisis assessment."""
        await safety_system.initialize()

        # Test with None input (should be handled gracefully)
        result = await safety_system.assess_crisis_risk(
            user_id="test_user_error", user_input=None, session_context=None
        )

        # Should handle gracefully and return valid structure
        assert "crisis_detected" in result
        assert "crisis_level" in result
        assert "immediate_intervention" in result
        assert "indicators" in result
        assert "response_time" in result

        # Should default to safe values
        assert result["crisis_detected"] is False
        assert result["crisis_level"] == CrisisLevel.NONE.value
