"""
Narrative Engine Tests

This module tests the narrative engine components including scene management,
choice processing, and event handling.
"""

from datetime import timedelta

import pytest

from src.components.gameplay_loop.models.core import (
    ChoiceType,
    NarrativeScene,
    SceneType,
    UserChoice,
)
from src.components.gameplay_loop.narrative.choice_processor import (
    ChoiceContext,
    ChoiceValidationResult,
    ChoiceValidator,
)
from src.components.gameplay_loop.narrative.engine import (
    EngineState,
    NarrativeEngineConfig,
    NarrativeMode,
)
from src.components.gameplay_loop.narrative.events import (
    ChoiceEvent,
    EventBus,
    EventPriority,
    EventType,
    NarrativeEvent,
    SceneEvent,
    create_choice_event,
    create_scene_event,
)
from src.components.gameplay_loop.narrative.scene_manager import (
    SceneContext,
    SceneStatus,
    SceneValidator,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
)


class TestNarrativeEvents:
    """Test narrative event system."""

    def test_narrative_event_creation(self):
        """Test creating narrative events."""
        event = NarrativeEvent(
            event_type=EventType.SCENE_ENTERED,
            session_id="test_session",
            user_id="test_user",
            priority=EventPriority.HIGH,
        )

        assert event.event_type == EventType.SCENE_ENTERED
        assert event.session_id == "test_session"
        assert event.user_id == "test_user"
        assert event.priority == EventPriority.HIGH
        assert not event.processed
        assert event.retry_count == 0

    def test_scene_event_creation(self):
        """Test creating scene-specific events."""
        event = create_scene_event(
            EventType.SCENE_ENTERED,
            "test_session",
            "test_user",
            "scene_001",
            "exploration",
            ["mindfulness", "grounding"],
        )

        assert isinstance(event, SceneEvent)
        assert event.scene_id == "scene_001"
        assert event.scene_type == "exploration"
        assert "mindfulness" in event.therapeutic_focus
        assert event.context["scene_id"] == "scene_001"

    def test_choice_event_creation(self):
        """Test creating choice-specific events."""
        event = create_choice_event(
            EventType.CHOICE_MADE,
            "test_session",
            "test_user",
            "choice_001",
            "Practice deep breathing",
            "therapeutic",
            0.9,
        )

        assert isinstance(event, ChoiceEvent)
        assert event.choice_id == "choice_001"
        assert event.choice_text == "Practice deep breathing"
        assert event.therapeutic_relevance == 0.9
        assert event.context["choice_type"] == "therapeutic"

    def test_event_serialization(self):
        """Test event serialization to/from dict."""
        original_event = NarrativeEvent(
            event_type=EventType.PROGRESS_UPDATED,
            session_id="test_session",
            user_id="test_user",
            data={"progress": 0.75},
            context={"metric": "anxiety_level"},
        )

        # Serialize to dict
        event_dict = original_event.to_dict()

        # Deserialize from dict
        restored_event = NarrativeEvent.from_dict(event_dict)

        assert restored_event.event_type == original_event.event_type
        assert restored_event.session_id == original_event.session_id
        assert restored_event.data == original_event.data
        assert restored_event.context == original_event.context


class TestEventBus:
    """Test event bus functionality."""

    def test_event_bus_subscription(self):
        """Test subscribing to events."""
        bus = EventBus()
        handler_called = []

        def test_handler(event):
            handler_called.append(event)

        bus.subscribe(EventType.SCENE_ENTERED, test_handler)
        assert EventType.SCENE_ENTERED in bus.subscribers
        assert test_handler in bus.subscribers[EventType.SCENE_ENTERED]

    @pytest.mark.asyncio
    async def test_event_bus_publishing(self):
        """Test publishing events."""
        bus = EventBus()
        received_events = []

        async def async_handler(event):
            received_events.append(event)

        def sync_handler(event):
            received_events.append(event)

        bus.subscribe(EventType.SCENE_ENTERED, async_handler)
        bus.subscribe(EventType.SCENE_ENTERED, sync_handler)

        event = NarrativeEvent(
            event_type=EventType.SCENE_ENTERED, session_id="test_session"
        )

        await bus.publish(event)

        assert len(received_events) == 2
        assert all(e.event_type == EventType.SCENE_ENTERED for e in received_events)

    def test_event_history(self):
        """Test event history tracking."""
        bus = EventBus()

        # Publish some events
        for i in range(5):
            event = NarrativeEvent(
                event_type=EventType.SCENE_ENTERED, session_id=f"session_{i}"
            )
            bus.event_history.append(event)

        # Get all events
        all_events = bus.get_events()
        assert len(all_events) == 5

        # Get events by type
        scene_events = bus.get_events(event_type=EventType.SCENE_ENTERED)
        assert len(scene_events) == 5

        # Get events by session
        session_events = bus.get_events(session_id="session_1")
        assert len(session_events) == 1
        assert session_events[0].session_id == "session_1"


class TestNarrativeEngineConfig:
    """Test narrative engine configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = NarrativeEngineConfig()

        assert config.mode == NarrativeMode.GUIDED
        assert config.max_concurrent_sessions == 100
        assert config.enable_safety_monitoring is True
        assert config.enable_progress_tracking is True
        assert config.cache_scenes is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = NarrativeEngineConfig(
            mode=NarrativeMode.EXPLORATORY,
            max_concurrent_sessions=50,
            session_timeout=timedelta(hours=1),
            enable_safety_monitoring=False,
        )

        assert config.mode == NarrativeMode.EXPLORATORY
        assert config.max_concurrent_sessions == 50
        assert config.session_timeout == timedelta(hours=1)
        assert config.enable_safety_monitoring is False


class TestSceneContext:
    """Test scene context functionality."""

    def test_scene_context_creation(self):
        """Test creating scene context."""
        scene = NarrativeScene(
            scene_id="test_scene",
            session_id="test_session",
            title="Test Scene",
            description="A test scene",
            narrative_content="This is a test scene for validation.",
            scene_type=SceneType.EXPLORATION,
        )

        session_state = SessionState(session_id="test_session", user_id="test_user")

        context = SceneContext(scene=scene, session_state=session_state)

        assert context.scene.scene_id == "test_scene"
        assert context.session_state.session_id == "test_session"
        assert context.status == SceneStatus.LOADING
        assert len(context.variables) == 0
        assert len(context.therapeutic_moments) == 0

    def test_scene_context_interactions(self):
        """Test scene context interaction tracking."""
        scene = NarrativeScene(
            scene_id="test_scene",
            session_id="test_session",
            title="Test Scene",
            description="A test scene",
            narrative_content="This is a test scene for validation.",
            scene_type=SceneType.EXPLORATION,
        )

        session_state = SessionState(session_id="test_session", user_id="test_user")

        context = SceneContext(scene=scene, session_state=session_state)

        # Add interaction
        context.add_interaction("choice_made", {"choice_id": "choice_001"})

        assert len(context.user_interactions) == 1
        assert context.user_interactions[0]["type"] == "choice_made"
        assert context.user_interactions[0]["data"]["choice_id"] == "choice_001"

    def test_therapeutic_moment_recording(self):
        """Test recording therapeutic moments."""
        scene = NarrativeScene(
            scene_id="test_scene",
            session_id="test_session",
            title="Test Scene",
            description="A test scene",
            narrative_content="This is a test scene for validation.",
            scene_type=SceneType.THERAPEUTIC_MOMENT,
        )

        session_state = SessionState(session_id="test_session", user_id="test_user")

        context = SceneContext(scene=scene, session_state=session_state)

        # Record therapeutic moment
        context.record_therapeutic_moment(
            "skill_practice", "User practiced deep breathing technique", 0.9
        )

        assert len(context.therapeutic_moments) == 1
        moment = context.therapeutic_moments[0]
        assert moment["type"] == "skill_practice"
        assert moment["description"] == "User practiced deep breathing technique"
        assert moment["relevance"] == 0.9


class TestSceneValidator:
    """Test scene validation."""

    def test_valid_scene_validation(self):
        """Test validation of a valid scene."""
        validator = SceneValidator()

        scene = NarrativeScene(
            scene_id="valid_scene",
            session_id="test_session",
            title="Valid Scene",
            description="A valid test scene",
            narrative_content="This is a valid scene with sufficient content for testing purposes.",
            scene_type=SceneType.EXPLORATION,
            therapeutic_focus=["mindfulness"],
        )

        is_valid, issues = validator.validate_scene(scene)

        assert is_valid
        assert len(issues) == 0

    def test_invalid_scene_validation(self):
        """Test validation of an invalid scene."""
        validator = SceneValidator()

        # Scene with missing required fields
        scene = NarrativeScene(
            scene_id="",  # Missing scene_id
            session_id="test_session",
            title="",  # Missing title
            description="A test scene",
            narrative_content="Short",  # Too short
            scene_type=SceneType.EXPLORATION,
        )

        is_valid, issues = validator.validate_scene(scene)

        assert not is_valid
        assert len(issues) > 0
        assert any("Missing required field" in issue for issue in issues)
        assert any("Content too short" in issue for issue in issues)


class TestChoiceValidator:
    """Test choice validation."""

    def test_valid_choice_validation(self):
        """Test validation of a valid choice."""
        validator = ChoiceValidator()

        choice = UserChoice(
            choice_id="valid_choice",
            scene_id="test_scene",
            choice_text="Practice mindfulness meditation",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_relevance=0.8,
        )

        session_state = SessionState(
            session_id="test_session",
            user_id="test_user",
            therapeutic_goals=["mindfulness", "anxiety_management"],
        )

        context = validator.validate_choice(choice, session_state)

        assert context.validation_result == ChoiceValidationResult.VALID
        assert len(context.validation_issues) == 0
        assert context.therapeutic_alignment > 0.5
        assert context.safety_score > 0.5

    def test_safety_concern_validation(self):
        """Test validation with safety concerns."""
        validator = ChoiceValidator()

        choice = UserChoice(
            choice_id="risky_choice",
            scene_id="test_scene",
            choice_text="Take a risky action",
            choice_type=ChoiceType.BEHAVIORAL,
            therapeutic_relevance=0.2,
        )

        session_state = SessionState(
            session_id="test_session", user_id="test_user", safety_level="crisis"
        )

        context = validator.validate_choice(choice, session_state)

        # Should have validation issues due to safety concerns
        assert context.validation_result != ChoiceValidationResult.VALID
        assert len(context.validation_issues) > 0

    def test_therapeutic_mismatch_validation(self):
        """Test validation with therapeutic mismatch."""
        validator = ChoiceValidator()

        choice = UserChoice(
            choice_id="irrelevant_choice",
            scene_id="test_scene",
            choice_text="Do something unrelated",
            choice_type=ChoiceType.NARRATIVE,
            therapeutic_relevance=0.1,  # Very low therapeutic relevance
        )

        session_state = SessionState(
            session_id="test_session",
            user_id="test_user",
            therapeutic_goals=["anxiety_management"],
        )

        context = validator.validate_choice(choice, session_state)

        assert context.validation_result == ChoiceValidationResult.THERAPEUTIC_MISMATCH
        assert any(
            "not therapeutically aligned" in issue
            for issue in context.validation_issues
        )


class TestChoiceContext:
    """Test choice context functionality."""

    def test_choice_context_creation(self):
        """Test creating choice context."""
        choice = UserChoice(
            choice_id="test_choice",
            scene_id="test_scene",
            choice_text="Test choice",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_relevance=0.7,
        )

        session_state = SessionState(session_id="test_session", user_id="test_user")

        context = ChoiceContext(choice=choice, session_state=session_state)

        assert context.choice.choice_id == "test_choice"
        assert context.session_state.session_id == "test_session"
        assert context.validation_result == ChoiceValidationResult.VALID
        assert len(context.validation_issues) == 0
        assert context.therapeutic_alignment == 0.0  # Not calculated yet
        assert context.safety_score == 1.0  # Default value


class TestEngineStates:
    """Test engine state management."""

    def test_engine_states(self):
        """Test engine state enumeration."""
        assert EngineState.INITIALIZING == "initializing"
        assert EngineState.READY == "ready"
        assert EngineState.RUNNING == "running"
        assert EngineState.PAUSED == "paused"
        assert EngineState.ERROR == "error"
        assert EngineState.SHUTDOWN == "shutdown"

    def test_narrative_modes(self):
        """Test narrative mode enumeration."""
        assert NarrativeMode.GUIDED == "guided"
        assert NarrativeMode.EXPLORATORY == "exploratory"
        assert NarrativeMode.CRISIS == "crisis"
        assert NarrativeMode.REFLECTION == "reflection"
        assert NarrativeMode.ADAPTIVE == "adaptive"
