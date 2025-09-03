"""
Tests for TherapeuticGameplayLoopController

This module tests the production gameplay loop controller implementation
including session lifecycle management, therapeutic system integration, and workflow orchestration.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.components.therapeutic_systems.gameplay_loop_controller import (
    SessionConfiguration,
    SessionOutcome,
    SessionPhase,
    SessionState,
    SessionStatus,
    TherapeuticGameplayLoopController,
)


class TestTherapeuticGameplayLoopController:
    """Test TherapeuticGameplayLoopController functionality."""

    @pytest.fixture
    def controller(self):
        """Create gameplay loop controller instance."""
        return TherapeuticGameplayLoopController()

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        return {
            "consequence_system": AsyncMock(),
            "emotional_safety_system": AsyncMock(),
            "adaptive_difficulty_engine": AsyncMock(),
            "character_development_system": AsyncMock(),
            "therapeutic_integration_system": AsyncMock(),
        }

    @pytest.mark.asyncio
    async def test_initialization(self, controller):
        """Test controller initialization."""
        await controller.initialize()

        # Should have empty session tracking
        assert len(controller.active_sessions) == 0
        assert len(controller.session_configurations) == 0
        assert len(controller.session_outcomes) == 0

        # Should have default configuration
        assert controller.max_concurrent_sessions == 100
        assert controller.session_timeout_minutes == 120
        assert controller.auto_save_enabled is True

        # Should have initialized metrics
        assert "sessions_started" in controller.metrics
        assert "sessions_completed" in controller.metrics
        assert controller.metrics["sessions_started"] == 0

    def test_therapeutic_system_injection(self, controller, mock_therapeutic_systems):
        """Test therapeutic system dependency injection."""
        controller.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Should have all systems injected
        assert controller.consequence_system is not None
        assert controller.emotional_safety_system is not None
        assert controller.adaptive_difficulty_engine is not None
        assert controller.character_development_system is not None
        assert controller.therapeutic_integration_system is not None

    @pytest.mark.asyncio
    async def test_start_session_basic(self, controller, mock_therapeutic_systems):
        """Test basic session start functionality."""
        await controller.initialize()
        controller.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses
        mock_therapeutic_systems[
            "emotional_safety_system"
        ].initialize_user_monitoring.return_value = {"status": "initialized"}
        mock_therapeutic_systems[
            "character_development_system"
        ].create_character.return_value = Mock(
            character_id="char_001", attributes={"courage": 5.0, "wisdom": 4.0}
        )
        mock_therapeutic_systems[
            "therapeutic_integration_system"
        ].generate_personalized_recommendations.return_value = [
            Mock(
                framework=Mock(value="cbt"),
                scenario_type=Mock(value="confidence_building"),
            )
        ]

        session_state = await controller.start_session(
            user_id="test_user_001",
            therapeutic_goals=["confidence_building", "anxiety_management"],
        )

        # Should return valid session state
        assert isinstance(session_state, SessionState)
        assert session_state.user_id == "test_user_001"
        assert session_state.status == SessionStatus.ACTIVE
        assert session_state.current_phase == SessionPhase.ACTIVE_GAMEPLAY
        assert len(session_state.therapeutic_goals) > 0

        # Should track session
        assert len(controller.active_sessions) == 1
        assert session_state.session_id in controller.active_sessions

        # Should update metrics
        assert controller.metrics["sessions_started"] == 1

    @pytest.mark.asyncio
    async def test_start_session_with_configuration(
        self, controller, mock_therapeutic_systems
    ):
        """Test session start with custom configuration."""
        await controller.initialize()
        controller.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses
        mock_therapeutic_systems[
            "emotional_safety_system"
        ].initialize_user_monitoring.return_value = {"status": "initialized"}
        mock_therapeutic_systems[
            "character_development_system"
        ].create_character.return_value = Mock(
            character_id="char_002", attributes={"courage": 6.0, "wisdom": 5.0}
        )
        mock_therapeutic_systems[
            "therapeutic_integration_system"
        ].generate_personalized_recommendations.return_value = [
            Mock(
                framework=Mock(value="dbt"),
                scenario_type=Mock(value="emotional_regulation"),
            )
        ]

        config = SessionConfiguration(
            user_id="test_user_002",
            therapeutic_goals=["emotional_regulation"],
            target_duration_minutes=30,
            difficulty_level="easy",
            framework_preferences=["dbt", "mindfulness"],
        )

        session_state = await controller.start_session(
            user_id="test_user_002", session_config=config
        )

        # Should use configuration
        assert session_state.user_id == "test_user_002"
        assert session_state.difficulty_level == "easy"
        assert "emotional_regulation" in session_state.therapeutic_goals

    @pytest.mark.asyncio
    async def test_process_user_choice(self, controller, mock_therapeutic_systems):
        """Test user choice processing through all therapeutic systems."""
        await controller.initialize()
        controller.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Set up session
        session_state = SessionState(
            session_id="session_001",
            user_id="test_user_003",
            status=SessionStatus.ACTIVE,
            current_phase=SessionPhase.ACTIVE_GAMEPLAY,
            character_id="char_003",
        )
        controller.active_sessions["session_001"] = session_state

        # Mock system responses
        mock_therapeutic_systems[
            "emotional_safety_system"
        ].assess_crisis_risk.return_value = {
            "crisis_detected": False,
            "safety_level": "standard",
        }
        mock_therapeutic_systems[
            "consequence_system"
        ].process_choice_consequence.return_value = {
            "consequence_text": "You feel more confident.",
            "therapeutic_value": 2.5,
            "character_impact": {"courage": 0.5},
        }
        mock_therapeutic_systems[
            "character_development_system"
        ].apply_consequence_to_character.return_value = {
            "character_updated": True,
            "updated_attributes": {"courage": 5.5},
        }
        mock_therapeutic_systems[
            "adaptive_difficulty_engine"
        ].adjust_difficulty.return_value = {
            "difficulty_adjusted": False,
            "current_difficulty": "moderate",
        }
        mock_therapeutic_systems[
            "therapeutic_integration_system"
        ].generate_personalized_recommendations.return_value = [
            Mock(
                framework=Mock(value="cbt"),
                scenario_type=Mock(value="confidence_building"),
            )
        ]
        mock_therapeutic_systems[
            "therapeutic_integration_system"
        ].create_therapeutic_scenario.return_value = Mock(
            scenario_id="scenario_001",
            title="Building Confidence",
            description="A confidence-building scenario",
            therapeutic_goals=["confidence_building"],
        )

        response = await controller.process_user_choice(
            session_id="session_001",
            user_choice="approach_with_confidence",
            choice_context={"scenario": "social_interaction"},
        )

        # Should return comprehensive response
        assert response["choice_processed"] is True
        assert "safety_assessment" in response
        assert "consequence" in response
        assert "character_update" in response
        assert "difficulty_adjustment" in response
        assert "therapeutic_integration" in response
        assert "session_progress" in response

        # Should update session state
        assert session_state.choices_made == 1
        assert session_state.consequences_processed == 1
        assert session_state.therapeutic_value_accumulated == 2.5

    @pytest.mark.asyncio
    async def test_process_choice_crisis_intervention(
        self, controller, mock_therapeutic_systems
    ):
        """Test crisis intervention during choice processing."""
        await controller.initialize()
        controller.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Set up session
        session_state = SessionState(
            session_id="session_002",
            user_id="test_user_004",
            status=SessionStatus.ACTIVE,
            current_phase=SessionPhase.ACTIVE_GAMEPLAY,
        )
        controller.active_sessions["session_002"] = session_state

        # Mock crisis detection
        mock_therapeutic_systems[
            "emotional_safety_system"
        ].assess_crisis_risk.return_value = {
            "crisis_detected": True,
            "crisis_level": "HIGH",
            "support_resources": ["crisis_hotline"],
        }

        response = await controller.process_user_choice(
            session_id="session_002",
            user_choice="I don't want to continue",
            choice_context={},
        )

        # Should trigger crisis intervention
        assert response["choice_processed"] is False
        assert response["crisis_intervention"] is True
        assert "intervention_message" in response
        assert "support_resources" in response
        assert response["session_paused"] is True

        # Should update metrics
        assert controller.metrics["safety_interventions"] == 1

    @pytest.mark.asyncio
    async def test_complete_session(self, controller, mock_therapeutic_systems):
        """Test session completion and outcome generation."""
        await controller.initialize()
        controller.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Set up session with some progress
        session_state = SessionState(
            session_id="session_003",
            user_id="test_user_005",
            status=SessionStatus.ACTIVE,
            current_phase=SessionPhase.ACTIVE_GAMEPLAY,
            character_id="char_005",
            choices_made=5,
            therapeutic_value_accumulated=12.5,
            milestones_achieved=2,
            therapeutic_goals=["confidence_building", "anxiety_management"],
        )
        controller.active_sessions["session_003"] = session_state

        # Mock system responses
        mock_therapeutic_systems[
            "character_development_system"
        ].get_character_progression_summary.return_value = {
            "attribute_changes": {"courage": 2.0, "wisdom": 1.5}
        }
        mock_therapeutic_systems[
            "therapeutic_integration_system"
        ].generate_personalized_recommendations.return_value = [
            Mock(framework=Mock(value="mindfulness"))
        ]

        outcome = await controller.complete_session("session_003")

        # Should return valid outcome
        assert isinstance(outcome, SessionOutcome)
        assert outcome.session_id == "session_003"
        assert outcome.user_id == "test_user_005"
        assert outcome.duration_minutes > 0
        assert outcome.therapeutic_value_total == 12.5
        assert len(outcome.therapeutic_goals_addressed) == 2
        assert len(outcome.recommendations_for_next_session) > 0

        # Should clean up session
        assert "session_003" not in controller.active_sessions
        assert "session_003" in controller.session_outcomes

        # Should update metrics
        assert controller.metrics["sessions_completed"] == 1
        assert controller.metrics["total_therapeutic_value"] == 12.5

    @pytest.mark.asyncio
    async def test_session_status_tracking(self, controller):
        """Test session status retrieval."""
        await controller.initialize()

        # Create session state
        session_state = SessionState(
            session_id="session_004",
            user_id="test_user_006",
            status=SessionStatus.ACTIVE,
            current_phase=SessionPhase.SKILL_PRACTICE,
            character_id="char_006",
            choices_made=3,
            therapeutic_value_accumulated=7.5,
        )
        controller.active_sessions["session_004"] = session_state

        status = await controller.get_session_status("session_004")

        # Should return comprehensive status
        assert status is not None
        assert status["session_id"] == "session_004"
        assert status["user_id"] == "test_user_006"
        assert status["status"] == "active"
        assert status["current_phase"] == "skill_practice"
        assert status["progress"]["choices_made"] == 3
        assert status["progress"]["therapeutic_value"] == 7.5
        assert status["character_id"] == "char_006"

    @pytest.mark.asyncio
    async def test_concurrent_session_limits(self, controller):
        """Test concurrent session limits."""
        await controller.initialize()
        controller.max_concurrent_sessions = 2  # Set low limit for testing

        # Start first session
        session1 = await controller.start_session("user_001")
        assert session1.status == SessionStatus.ACTIVE

        # Start second session
        session2 = await controller.start_session("user_002")
        assert session2.status == SessionStatus.ACTIVE

        # Third session should return error state instead of raising
        session3 = await controller.start_session("user_003")
        assert session3.status == SessionStatus.ERROR

    @pytest.mark.asyncio
    async def test_error_handling(self, controller, mock_therapeutic_systems):
        """Test error handling in various operations."""
        await controller.initialize()
        controller.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Test processing choice for non-existent session
        response = await controller.process_user_choice(
            session_id="non_existent", user_choice="test_choice"
        )

        assert response["choice_processed"] is False
        assert "error" in response
        assert response["safety_fallback"] is True

    @pytest.mark.asyncio
    async def test_health_check(self, controller, mock_therapeutic_systems):
        """Test system health check."""
        await controller.initialize()
        controller.inject_therapeutic_systems(**mock_therapeutic_systems)

        health = await controller.health_check()

        assert "status" in health
        assert health["status"] == "healthy"  # All 5 systems available
        assert "active_sessions" in health
        assert "therapeutic_systems" in health
        assert health["systems_available"] == "5/6"
        assert "metrics" in health

    @pytest.mark.asyncio
    async def test_health_check_degraded(self, controller):
        """Test health check with missing systems."""
        await controller.initialize()
        # Don't inject all systems

        health = await controller.health_check()

        assert health["status"] == "degraded"  # Less than 3 systems available
        assert health["systems_available"] == "0/6"

    def test_get_metrics(self, controller):
        """Test metrics collection."""
        # Add some test data
        controller.metrics["sessions_started"] = 10
        controller.metrics["sessions_completed"] = 8
        controller.active_sessions["test"] = Mock()
        controller.session_outcomes["test"] = Mock()

        metrics = controller.get_metrics()

        assert isinstance(metrics, dict)
        assert "sessions_started" in metrics
        assert "sessions_completed" in metrics
        assert "active_sessions_count" in metrics
        assert "session_outcomes_stored" in metrics
        assert "completion_rate" in metrics
        assert metrics["completion_rate"] == 80.0  # 8/10 * 100

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(
        self, controller, mock_therapeutic_systems
    ):
        """Test compatibility with E2E test interface expectations."""
        await controller.initialize()
        controller.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses for E2E compatibility
        mock_therapeutic_systems[
            "emotional_safety_system"
        ].initialize_user_monitoring.return_value = {"status": "initialized"}
        mock_therapeutic_systems[
            "character_development_system"
        ].create_character.return_value = Mock(
            character_id="demo_char", attributes={"courage": 5.0}
        )
        mock_therapeutic_systems[
            "therapeutic_integration_system"
        ].generate_personalized_recommendations.return_value = [
            Mock(
                framework=Mock(value="cbt"),
                scenario_type=Mock(value="confidence_building"),
            )
        ]

        # Test session start (E2E interface)
        session_state = await controller.start_session(
            user_id="demo_user_001", therapeutic_goals=["confidence_building"]
        )

        # Should match expected structure
        assert hasattr(session_state, "session_id")
        assert hasattr(session_state, "user_id")
        assert hasattr(session_state, "status")
        assert hasattr(session_state, "therapeutic_goals")
        assert hasattr(session_state, "character_id")

        # Test choice processing (E2E interface)
        mock_therapeutic_systems[
            "emotional_safety_system"
        ].assess_crisis_risk.return_value = {
            "crisis_detected": False,
            "safety_level": "standard",
        }
        mock_therapeutic_systems[
            "consequence_system"
        ].process_choice_consequence.return_value = {
            "consequence_text": "Test consequence",
            "therapeutic_value": 1.0,
        }

        response = await controller.process_user_choice(
            session_id=session_state.session_id, user_choice="test_choice"
        )

        # Should match expected structure
        assert "choice_processed" in response
        assert "safety_assessment" in response
        assert "consequence" in response
        assert "session_progress" in response
