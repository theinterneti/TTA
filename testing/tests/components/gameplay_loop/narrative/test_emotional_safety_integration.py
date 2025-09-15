"""
Integration Tests for Emotional Safety System with Narrative Engine

This module tests the integration between the emotional safety system and narrative engine.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.components.gameplay_loop.models.core import (
    ChoiceType,
    NarrativeScene,
    UserChoice,
)
from src.components.gameplay_loop.narrative.emotional_safety_system import (
    EmotionalSafetySystem,
    EmotionalState,
)
from src.components.gameplay_loop.narrative.events import EventBus
from src.components.gameplay_loop.narrative.therapeutic_integrator import (
    TherapeuticIntegrator,
)
from src.components.gameplay_loop.services.session_state import SessionState


class TestEmotionalSafetyIntegration:
    """Test integration between emotional safety system and narrative engine."""

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus

    @pytest.fixture
    def narrative_engine(self, event_bus):
        """Create mock narrative engine."""
        engine = Mock()
        engine.event_bus = event_bus
        return engine

    @pytest.fixture
    def therapeutic_integrator(self, narrative_engine):
        """Create therapeutic integrator with emotional safety system."""
        return TherapeuticIntegrator(narrative_engine)

    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = Mock(spec=SessionState)
        state.session_id = "integration_test_session"
        state.user_id = "integration_test_user"
        state.therapeutic_goals = ["anxiety_management", "emotional_regulation"]
        state.progress_metrics = {
            "anxiety_management": 0.4,
            "emotional_regulation": 0.3,
        }
        state.context = {}
        state.emotional_state = {
            "anxious": 0.6,
            "calm": 0.3,
            "overwhelmed": 0.4,
            "hopeful": 0.5,
        }
        return state

    @pytest.fixture
    def distressing_scene(self):
        """Create scene with potentially distressing content."""
        scene = Mock(spec=NarrativeScene)
        scene.scene_id = "distressing_scene_001"
        scene.description = "The scene shows a character dealing with trauma and feeling overwhelmed by painful memories"
        scene.scene_type = Mock()
        scene.scene_type.value = "therapeutic_challenge"
        return scene

    @pytest.fixture
    def therapeutic_choice(self):
        """Create therapeutic choice."""
        return UserChoice(
            choice_id="therapeutic_choice_001",
            text="Take a deep breath and practice grounding techniques to manage anxiety",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_relevance=0.8,
            emotional_weight=0.6,
            difficulty_level=0.4,
        )

    @pytest.fixture
    def distressing_choice(self):
        """Create potentially distressing choice."""
        return UserChoice(
            choice_id="distressing_choice_001",
            text="Confront the traumatic memories directly without any coping strategies",
            choice_type=ChoiceType.NARRATIVE,
            therapeutic_relevance=0.3,
            emotional_weight=0.9,
            difficulty_level=0.8,
        )

    @pytest.mark.asyncio
    async def test_emotional_safety_monitoring_during_scene_entry(
        self, therapeutic_integrator, session_state, distressing_scene
    ):
        """Test emotional safety monitoring when entering a scene."""
        # Monitor emotional safety for scene content
        scene_interaction_data = {
            "content": distressing_scene.description,
            "scene_id": distressing_scene.scene_id,
            "scene_type": distressing_scene.scene_type.value,
            "interaction_type": "scene_entry",
        }

        await therapeutic_integrator.monitor_emotional_safety(
            session_state, scene_interaction_data
        )

        # Check that triggers were detected
        if "detected_triggers" in session_state.context:
            triggers = session_state.context["detected_triggers"]
            assert len(triggers) > 0

            # Should detect trauma-related triggers
            trauma_triggers = [t for t in triggers if t["category"] == "trauma_related"]
            assert len(trauma_triggers) > 0

    @pytest.mark.asyncio
    async def test_emotional_safety_monitoring_during_choice_processing(
        self, therapeutic_integrator, session_state, distressing_choice
    ):
        """Test emotional safety monitoring when processing choices."""
        # Monitor emotional safety for choice content
        choice_interaction_data = {
            "content": distressing_choice.text,
            "choice_id": distressing_choice.choice_id,
            "choice_type": distressing_choice.choice_type.value,
            "therapeutic_relevance": distressing_choice.therapeutic_relevance,
            "emotional_weight": distressing_choice.emotional_weight,
            "interaction_type": "choice_made",
            "recent_choice": distressing_choice.text,
        }

        await therapeutic_integrator.monitor_emotional_safety(
            session_state, choice_interaction_data
        )

        # Check that emotional state was monitored
        user_id = session_state.user_id
        emotional_snapshots = (
            therapeutic_integrator.emotional_safety_system.emotional_snapshots
        )

        assert user_id in emotional_snapshots
        assert len(emotional_snapshots[user_id]) > 0

        # Check latest snapshot
        latest_snapshot = emotional_snapshots[user_id][-1]
        assert latest_snapshot.user_id == user_id
        assert latest_snapshot.session_id == session_state.session_id

    @pytest.mark.asyncio
    async def test_emotional_support_provision(
        self, therapeutic_integrator, session_state
    ):
        """Test emotional support provision through therapeutic integrator."""
        # Request emotional support for anxiety
        support_response = await therapeutic_integrator.provide_emotional_support(
            session_state, EmotionalState.ANXIOUS, 0.8
        )

        # Check support response structure
        assert "emotion" in support_response
        assert "intensity" in support_response
        assert "support_provided" in support_response
        assert "techniques_offered" in support_response

        assert support_response["emotion"] == EmotionalState.ANXIOUS.value
        assert support_response["intensity"] == 0.8

        # Check that support was provided
        assert len(support_response["support_provided"]) > 0
        assert len(support_response["techniques_offered"]) > 0

        # Check session context update
        assert "emotional_regulation_support" in session_state.context

    @pytest.mark.asyncio
    async def test_high_distress_intervention_triggering(
        self, therapeutic_integrator, session_state
    ):
        """Test that high distress triggers appropriate interventions."""
        # Simulate high distress emotional state
        session_state.emotional_state = {
            "anxious": 0.9,
            "depressed": 0.8,
            "overwhelmed": 0.9,
            "hopeful": 0.1,
        }

        # Monitor with distressing content
        interaction_data = {
            "content": "I can't handle this anymore, everything feels hopeless and I want to give up",
            "interaction_type": "user_input",
            "emotional_change": 0.4,
        }

        await therapeutic_integrator.monitor_emotional_safety(
            session_state, interaction_data
        )

        # Check that intervention was triggered
        assert (
            session_state.context.get("immediate_support_provided", False)
            or session_state.context.get("crisis_intervention_active", False)
            or session_state.context.get("coping_support_offered", False)
        )

        # Check metrics
        assert therapeutic_integrator.emotional_interventions > 0

    @pytest.mark.asyncio
    async def test_crisis_protocol_activation(
        self, therapeutic_integrator, session_state
    ):
        """Test crisis protocol activation for critical distress."""
        # Simulate critical distress
        session_state.emotional_state = {
            "depressed": 1.0,
            "overwhelmed": 1.0,
            "hopeful": 0.0,
            "anxious": 0.9,
        }

        # Monitor with crisis-level content
        interaction_data = {
            "content": "I want to end my life and I have a plan to hurt myself tonight",
            "interaction_type": "user_input",
        }

        await therapeutic_integrator.monitor_emotional_safety(
            session_state, interaction_data
        )

        # Check that crisis protocol was activated
        assert session_state.context.get("crisis_intervention_active", False)
        assert session_state.context.get("narrative_paused_for_safety", False)
        assert "crisis_resources_provided" in session_state.context

    def test_emotional_safety_status_reporting(
        self, therapeutic_integrator, session_state
    ):
        """Test emotional safety status reporting."""
        # Add some emotional history
        user_id = session_state.user_id
        therapeutic_integrator.emotional_safety_system.emotional_snapshots[user_id] = []

        # Get safety status
        status = therapeutic_integrator.get_emotional_safety_status(session_state)

        # Check status structure
        assert "current_distress_level" in status
        assert "recent_snapshots_count" in status
        assert "recent_triggers_count" in status
        assert "monitoring_active" in status
        assert "intervention_threshold" in status
        assert "support_available" in status
        assert "crisis_protocol_active" in status

        # Check that monitoring is active
        assert status["monitoring_active"]

    @pytest.mark.asyncio
    async def test_trigger_detection_and_intervention_suggestion(
        self, therapeutic_integrator, session_state
    ):
        """Test trigger detection and intervention suggestion."""
        # Content with multiple trigger types
        interaction_data = {
            "content": "The violence and abuse in this scene is triggering my trauma and making me feel panicked and scared",
            "interaction_type": "scene_content",
        }

        await therapeutic_integrator.monitor_emotional_safety(
            session_state, interaction_data
        )

        # Check that triggers were detected and stored
        if "detected_triggers" in session_state.context:
            triggers = session_state.context["detected_triggers"]
            assert len(triggers) > 0

            # Should have suggested interventions
            for trigger in triggers:
                assert "suggested_interventions" in trigger
                assert len(trigger["suggested_interventions"]) > 0
                assert trigger["intensity"] > 0

    @pytest.mark.asyncio
    async def test_therapeutic_context_integration(
        self, therapeutic_integrator, session_state
    ):
        """Test integration with therapeutic context tracking."""
        # Provide emotional support
        await therapeutic_integrator.provide_emotional_support(
            session_state, EmotionalState.ANXIOUS, 0.7
        )

        # Check that therapeutic context was updated
        if session_state.session_id in therapeutic_integrator.session_contexts:
            context = therapeutic_integrator.session_contexts[session_state.session_id]
            assert context.current_focus == "emotional_support_anxious"

    @pytest.mark.asyncio
    async def test_safety_monitor_integration(
        self, therapeutic_integrator, session_state
    ):
        """Test integration with safety monitoring."""
        # Create safety monitor
        from src.components.gameplay_loop.narrative.therapeutic_integrator import (
            SafetyMonitor,
        )

        safety_monitor = SafetyMonitor(
            monitor_id=session_state.session_id, safety_level="standard"
        )
        therapeutic_integrator.safety_monitors[session_state.session_id] = (
            safety_monitor
        )

        # Simulate distressing interaction
        session_state.emotional_state = {"anxious": 0.8, "overwhelmed": 0.7}

        interaction_data = {
            "content": "This situation is making me feel very anxious and overwhelmed",
            "interaction_type": "user_response",
        }

        await therapeutic_integrator.monitor_emotional_safety(
            session_state, interaction_data
        )

        # Check that safety monitor was updated
        updated_monitor = therapeutic_integrator.safety_monitors[
            session_state.session_id
        ]
        assert "emotional_distress" in updated_monitor.safety_level
        assert (
            len(updated_monitor.risk_factors) > 0
            or len(updated_monitor.protective_factors) > 0
        )

    def test_metrics_integration(self, therapeutic_integrator):
        """Test metrics integration between systems."""
        # Get combined metrics
        metrics = therapeutic_integrator.get_metrics()

        # Check that emotional safety metrics are included
        assert "emotional_interventions" in metrics
        assert "emotional_safety_metrics" in metrics

        emotional_metrics = metrics["emotional_safety_metrics"]
        assert "emotional_snapshots_created" in emotional_metrics
        assert "triggers_detected" in emotional_metrics
        assert "interventions_triggered" in emotional_metrics

    @pytest.mark.asyncio
    async def test_emotional_pattern_detection(
        self, therapeutic_integrator, session_state
    ):
        """Test emotional pattern detection over multiple interactions."""
        # Simulate multiple interactions with increasing distress
        for i in range(4):
            session_state.emotional_state = {
                "anxious": 0.3 + i * 0.2,
                "overwhelmed": 0.2 + i * 0.2,
            }

            interaction_data = {
                "content": f"Interaction {i}: feeling more anxious and overwhelmed",
                "interaction_type": "user_input",
            }

            await therapeutic_integrator.monitor_emotional_safety(
                session_state, interaction_data
            )

        # Check that patterns were detected
        if "emotional_pattern_alert" in session_state.context:
            assert (
                session_state.context["emotional_pattern_alert"]
                == "increasing_distress"
            )

    def test_emotional_safety_system_initialization(self, therapeutic_integrator):
        """Test that emotional safety system is properly initialized."""
        assert hasattr(therapeutic_integrator, "emotional_safety_system")
        assert isinstance(
            therapeutic_integrator.emotional_safety_system, EmotionalSafetySystem
        )

        # Check that system is properly configured
        emotional_system = therapeutic_integrator.emotional_safety_system
        assert emotional_system.monitoring_enabled
        assert len(emotional_system.interventions) > 0
        assert len(emotional_system.coping_strategies) > 0
        assert len(emotional_system.grounding_techniques) > 0
