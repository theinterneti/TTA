"""
Tests for GameplayLoopController

This module tests session lifecycle management, break point detection,
session pacing, and therapeutic session orchestration functionality.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.components.gameplay_loop.controllers.gameplay_loop_controller import (
    BreakPointType,
    GameplayLoopController,
    SessionBreakPoint,
    SessionConfiguration,
    SessionPacing,
    SessionSummary,
)
from src.components.gameplay_loop.narrative.choice_processor import ChoiceProcessor
from src.components.gameplay_loop.narrative.events import EventBus
from src.components.gameplay_loop.narrative.narrative_engine import NarrativeEngine
from src.components.gameplay_loop.services.redis_session_manager import (
    RedisSessionManager,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
    SessionStateType,
)


class TestGameplayLoopController:
    """Test GameplayLoopController functionality."""

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus

    @pytest.fixture
    def session_manager(self):
        """Create mock session manager."""
        manager = Mock(spec=RedisSessionManager)
        manager.save_session = AsyncMock()
        manager.get_session = AsyncMock()
        manager.get_user_sessions = AsyncMock(return_value=[])
        return manager

    @pytest.fixture
    def narrative_engine(self):
        """Create mock narrative engine."""
        engine = Mock(spec=NarrativeEngine)
        engine.initialize_session = AsyncMock()
        engine.restore_session_context = AsyncMock()
        return engine

    @pytest.fixture
    def choice_processor(self):
        """Create mock choice processor."""
        processor = Mock(spec=ChoiceProcessor)
        return processor

    @pytest.fixture
    def controller(
        self, narrative_engine, choice_processor, session_manager, event_bus
    ):
        """Create gameplay loop controller instance."""
        return GameplayLoopController(
            narrative_engine, choice_processor, session_manager, event_bus
        )

    @pytest.fixture
    def session_config(self):
        """Create session configuration."""
        return SessionConfiguration(
            user_id="test_user_123",
            target_duration_minutes=30,
            pacing=SessionPacing.STANDARD,
            therapeutic_goals=["anxiety_management", "communication_skills"],
            break_point_notifications=True,
            time_reminders=True,
        )

    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = SessionState(
            session_id="test_session_456",
            user_id="test_user_123",
            state=SessionStateType.ACTIVE,
            therapeutic_goals=["anxiety_management", "communication_skills"],
        )
        state.scene_history = ["scene1", "scene2", "scene3"]
        state.choice_history = ["choice1", "choice2", "choice3", "choice4"]
        state.emotional_state = {"anxiety": 0.3, "confidence": 0.7}
        state.context = {
            "therapeutic_progress": {
                "concepts_integrated": 2,
                "goals_addressed": ["anxiety_management"],
                "skills_practiced": ["breathing_techniques"],
            },
            "character_development_summary": {
                "development_events": 3,
                "attributes_improved": {"courage": 0.5, "wisdom": 0.3},
            },
        }
        return state

    @pytest.mark.asyncio
    async def test_start_session_new_user(
        self, controller, session_config, session_manager, narrative_engine, event_bus
    ):
        """Test starting a new session for a user."""
        # Mock no existing sessions
        session_manager.get_user_sessions.return_value = []

        session_state, session_summary = await controller.start_session(
            session_config.user_id, session_config
        )

        # Check session state
        assert isinstance(session_state, SessionState)
        assert session_state.user_id == session_config.user_id
        assert session_state.state == SessionStateType.ACTIVE
        assert session_state.therapeutic_goals == session_config.therapeutic_goals

        # Check session summary
        assert isinstance(session_summary, SessionSummary)
        assert session_summary.user_id == session_config.user_id
        assert session_summary.start_time is not None

        # Check that session was stored
        assert session_state.session_id in controller.active_sessions
        assert session_state.session_id in controller.session_summaries

        # Check that narrative engine was initialized
        narrative_engine.initialize_session.assert_called_once_with(session_state)

        # Check that session was persisted
        session_manager.save_session.assert_called()

        # Check that event was published
        event_bus.publish.assert_called()

        # Check metrics
        assert controller.metrics["sessions_started"] == 1

    @pytest.mark.asyncio
    async def test_start_session_with_recovery(
        self, controller, session_config, session_manager
    ):
        """Test starting a session with recovery of existing paused session."""
        # Mock existing paused session
        existing_session = SessionState(
            session_id="existing_session",
            user_id=session_config.user_id,
            state=SessionStateType.PAUSED,
            last_activity=datetime.utcnow() - timedelta(minutes=30),
        )
        existing_session.context = {"session_recap": "Welcome back!"}

        session_manager.get_user_sessions.return_value = [existing_session]
        session_manager.get_session.return_value = existing_session

        session_state, session_summary = await controller.start_session(
            session_config.user_id, session_config
        )

        # Check that existing session was recovered
        assert session_state.session_id == existing_session.session_id
        assert session_state.state == SessionStateType.ACTIVE

        # Check metrics
        assert controller.metrics["session_recoveries"] == 1
        assert controller.metrics["sessions_resumed"] == 1

    @pytest.mark.asyncio
    async def test_pause_session(
        self, controller, session_state, session_manager, event_bus
    ):
        """Test pausing an active session."""
        session_manager.get_session.return_value = session_state

        paused_state = await controller.pause_session(
            session_state.session_id, "user_requested"
        )

        # Check session state
        assert paused_state.state == SessionStateType.PAUSED
        assert "pause_context" in paused_state.context
        assert "session_recap" in paused_state.context

        # Check pause context
        pause_context = paused_state.context["pause_context"]
        assert pause_context["pause_reason"] == "user_requested"
        assert pause_context["current_scene"] == session_state.current_scene_id

        # Check that session was persisted
        session_manager.save_session.assert_called()

        # Check that event was published
        event_bus.publish.assert_called()

        # Check metrics
        assert controller.metrics["sessions_paused"] == 1

    @pytest.mark.asyncio
    async def test_resume_session(
        self, controller, session_state, session_manager, narrative_engine, event_bus
    ):
        """Test resuming a paused session."""
        # Set up paused session
        session_state.state = SessionStateType.PAUSED
        session_state.context["session_recap"] = "Welcome back to your adventure!"
        session_state.context["pause_context"] = {
            "paused_at": datetime.utcnow().isoformat(),
            "pause_reason": "user_requested",
        }

        session_manager.get_session.return_value = session_state

        resumed_state, recap = await controller.resume_session(session_state.session_id)

        # Check session state
        assert resumed_state.state == SessionStateType.ACTIVE
        assert recap == "Welcome back to your adventure!"

        # Check that narrative engine context was restored
        narrative_engine.restore_session_context.assert_called_once_with(session_state)

        # Check that session was persisted
        session_manager.save_session.assert_called()

        # Check that event was published
        event_bus.publish.assert_called()

        # Check metrics
        assert controller.metrics["sessions_resumed"] == 1

    @pytest.mark.asyncio
    async def test_end_session(
        self, controller, session_state, session_manager, event_bus
    ):
        """Test ending a session with summary generation."""
        session_manager.get_session.return_value = session_state

        # Store session summary for testing
        controller.session_summaries[session_state.session_id] = SessionSummary(
            session_id=session_state.session_id,
            user_id=session_state.user_id,
            start_time=session_state.created_at,
        )

        session_summary = await controller.end_session(
            session_state.session_id, "user_completed"
        )

        # Check session summary
        assert isinstance(session_summary, SessionSummary)
        assert session_summary.end_time is not None
        assert session_summary.duration_minutes > 0
        assert session_summary.scenes_completed == len(session_state.scene_history)
        assert session_summary.choices_made == len(session_state.choice_history)

        # Check that session was persisted
        session_manager.save_session.assert_called()

        # Check that event was published
        event_bus.publish.assert_called()

        # Check metrics
        assert controller.metrics["sessions_completed"] == 1

    @pytest.mark.asyncio
    async def test_detect_break_points_time_based(
        self, controller, session_state, session_config
    ):
        """Test detection of time-based break points."""
        # Set up session configuration
        controller.active_sessions[session_state.session_id] = session_config

        # Mock time since last break
        with patch.object(controller, "_get_last_break_time") as mock_last_break:
            mock_last_break.return_value = datetime.utcnow() - timedelta(minutes=20)

            break_point = await controller.detect_break_points(session_state)

            # Check break point
            assert break_point is not None
            assert isinstance(break_point, SessionBreakPoint)
            assert break_point.break_type == BreakPointType.TIME_BASED
            assert break_point.session_id == session_state.session_id
            assert break_point.appropriateness_score > 0

            # Check metrics
            assert controller.metrics["break_points_detected"] == 1

    @pytest.mark.asyncio
    async def test_detect_break_points_milestone_achievement(
        self, controller, session_state, session_config
    ):
        """Test detection of milestone achievement break points."""
        # Set up session configuration
        controller.active_sessions[session_state.session_id] = session_config

        # Add milestone achievement to context
        session_state.context["recent_milestone_achievement"] = {
            "milestone": "first_brave_act",
            "name": "First Brave Act",
        }

        break_point = await controller.detect_break_points(session_state)

        # Check break point
        assert break_point is not None
        assert break_point.break_type == BreakPointType.MILESTONE_ACHIEVEMENT
        assert break_point.therapeutic_value > 0.8  # High therapeutic value

    @pytest.mark.asyncio
    async def test_detect_break_points_emotional_processing(
        self, controller, session_state, session_config
    ):
        """Test detection of emotional processing break points."""
        # Set up session configuration
        controller.active_sessions[session_state.session_id] = session_config

        # Set high emotional intensity
        session_state.emotional_state = {"anxiety": 0.8, "overwhelm": 0.7}

        break_point = await controller.detect_break_points(session_state)

        # Check break point
        assert break_point is not None
        assert break_point.break_type == BreakPointType.EMOTIONAL_PROCESSING
        assert break_point.emotional_intensity > 0.7

    @pytest.mark.asyncio
    async def test_offer_break(self, controller, session_state):
        """Test offering a break to the user."""
        # Create break point
        break_point = SessionBreakPoint(
            session_id=session_state.session_id,
            break_type=BreakPointType.SCENE_TRANSITION,
            appropriateness_score=0.8,
            therapeutic_value=0.6,
        )

        break_offer = await controller.offer_break(session_state, break_point)

        # Check break offer
        assert "break_point_id" in break_offer
        assert "message" in break_offer
        assert "options" in break_offer
        assert len(break_offer["options"]) >= 2

        # Check that break point was updated
        assert break_point.break_offered == True
        assert break_point.break_message != ""

    @pytest.mark.asyncio
    async def test_handle_break_response_accept(
        self, controller, session_state, session_manager
    ):
        """Test handling user acceptance of break offer."""
        # Create and store break point
        break_point = SessionBreakPoint(
            session_id=session_state.session_id,
            break_type=BreakPointType.SCENE_TRANSITION,
        )
        controller.session_break_points[session_state.session_id] = [break_point]

        # Mock session manager for pause
        session_manager.get_session.return_value = session_state

        response = await controller.handle_break_response(
            session_state, break_point.break_point_id, "accept_break"
        )

        # Check response
        assert response["action"] == "session_paused"
        assert "message" in response

        # Check that break point was marked as accepted
        assert break_point.break_accepted == True

        # Check metrics
        assert controller.metrics["break_points_accepted"] == 1

    @pytest.mark.asyncio
    async def test_handle_break_response_decline(self, controller, session_state):
        """Test handling user decline of break offer."""
        # Create and store break point
        break_point = SessionBreakPoint(
            session_id=session_state.session_id,
            break_type=BreakPointType.SCENE_TRANSITION,
            continuation_message="Continuing your adventure...",
        )
        controller.session_break_points[session_state.session_id] = [break_point]

        response = await controller.handle_break_response(
            session_state, break_point.break_point_id, "decline_break"
        )

        # Check response
        assert response["action"] == "continue"
        assert response["message"] == "Continuing your adventure..."

    def test_session_configuration_defaults(self):
        """Test session configuration default values."""
        config = SessionConfiguration(user_id="test_user")

        assert config.user_id == "test_user"
        assert config.target_duration_minutes == 30
        assert config.pacing == SessionPacing.STANDARD
        assert config.break_point_notifications == True
        assert config.time_reminders == True
        assert config.auto_recovery_enabled == True

    def test_pacing_configurations_loading(self, controller):
        """Test that pacing configurations are properly loaded."""
        pacing_configs = controller.pacing_configurations

        # Check that all pacing types are configured
        for pacing in SessionPacing:
            assert pacing in pacing_configs
            config = pacing_configs[pacing]
            assert "target_duration" in config
            assert "max_duration" in config
            assert "break_interval" in config
            assert "scene_pace" in config

    def test_break_point_detectors_loading(self, controller):
        """Test that break point detectors are properly loaded."""
        detectors = controller.break_point_detectors

        # Check that all break point types are configured
        for break_type in BreakPointType:
            assert break_type in detectors
            detector = detectors[break_type]
            assert "trigger_conditions" in detector
            assert "appropriateness_factors" in detector
            assert "message_templates" in detector

    def test_session_templates_loading(self, controller):
        """Test that session templates are properly loaded."""
        templates = controller.session_templates

        # Check that key templates exist
        assert "anxiety_management" in templates
        assert "communication_skills" in templates
        assert "emotional_regulation" in templates
        assert "general_wellbeing" in templates

        # Check template structure
        for template_name, template in templates.items():
            assert "phases" in template
            assert "therapeutic_goals" in template
            assert "recommended_duration" in template
            assert "break_point_emphasis" in template

    def test_calculate_engagement_score(self, controller, session_state):
        """Test engagement score calculation."""
        # Mock session duration
        session_state.created_at = datetime.utcnow() - timedelta(minutes=30)

        score = controller._calculate_engagement_score(session_state)

        # Check score is valid
        assert 0.0 <= score <= 1.0
        assert score > 0  # Should have some engagement based on choices and scenes

    def test_calculate_therapeutic_effectiveness(self, controller, session_state):
        """Test therapeutic effectiveness calculation."""
        score = controller._calculate_therapeutic_effectiveness(session_state)

        # Check score is valid
        assert 0.0 <= score <= 1.0
        assert score > 0  # Should have some effectiveness based on therapeutic progress

    def test_recommend_next_session_focus(self, controller, session_state):
        """Test next session focus recommendation."""
        focus = controller._recommend_next_session_focus(session_state)

        # Check that a focus is recommended
        assert focus is not None
        assert isinstance(focus, str)
        assert len(focus) > 0

    def test_suggest_next_session_goals(self, controller, session_state):
        """Test next session goals suggestion."""
        goals = controller._suggest_next_session_goals(session_state)

        # Check that goals are suggested
        assert isinstance(goals, list)
        assert len(goals) <= 3  # Should limit to 3 suggestions

    def test_metrics_tracking(self, controller):
        """Test metrics tracking."""
        initial_metrics = controller.get_metrics()

        # Check metric structure
        assert "sessions_started" in initial_metrics
        assert "sessions_completed" in initial_metrics
        assert "sessions_paused" in initial_metrics
        assert "sessions_resumed" in initial_metrics
        assert "break_points_detected" in initial_metrics
        assert "break_points_accepted" in initial_metrics
        assert "auto_saves_performed" in initial_metrics
        assert "session_recoveries" in initial_metrics
        assert "active_sessions_count" in initial_metrics

        # Initially should be zero
        assert initial_metrics["sessions_started"] == 0
        assert initial_metrics["sessions_completed"] == 0
        assert initial_metrics["active_sessions_count"] == 0

    @pytest.mark.asyncio
    async def test_health_check(self, controller):
        """Test health check functionality."""
        health = await controller.health_check()

        assert health["status"] == "healthy"
        assert "active_sessions" in health
        assert "pacing_configurations_loaded" in health
        assert "break_point_detectors_loaded" in health
        assert "session_templates_loaded" in health
        assert "auto_save_tasks_running" in health
        assert "session_monitors_running" in health
        assert "metrics" in health

        # Should have loaded configurations
        assert health["pacing_configurations_loaded"] > 0
        assert health["break_point_detectors_loaded"] > 0
        assert health["session_templates_loaded"] > 0
