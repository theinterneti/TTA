"""
Tests for EmotionalSafetySystem

This module tests emotional state monitoring, trigger detection, intervention
mechanisms, and emotional regulation support functionality.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from src.components.gameplay_loop.narrative.emotional_safety_system import (
    DistressLevel,
    EmotionalSafetySystem,
    EmotionalState,
    EmotionalStateSnapshot,
    InterventionType,
    SafetyIntervention,
    TriggerCategory,
)
from src.components.gameplay_loop.narrative.events import EventBus
from src.components.gameplay_loop.services.session_state import SessionState


class TestEmotionalSafetySystem:
    """Test EmotionalSafetySystem functionality."""

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus

    @pytest.fixture
    def emotional_safety_system(self, event_bus):
        """Create emotional safety system instance."""
        return EmotionalSafetySystem(event_bus)

    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = Mock(spec=SessionState)
        state.session_id = "test_session_123"
        state.user_id = "test_user_456"
        state.therapeutic_goals = ["anxiety_management", "emotional_regulation"]
        state.progress_metrics = {
            "anxiety_management": 0.4,
            "emotional_regulation": 0.3,
        }
        state.context = {"narrative_context": "therapeutic_session"}
        state.emotional_state = {
            "anxious": 0.7,
            "calm": 0.2,
            "overwhelmed": 0.5,
            "hopeful": 0.3,
        }
        return state

    @pytest.fixture
    def distressed_session_state(self):
        """Create session state with high distress."""
        state = Mock(spec=SessionState)
        state.session_id = "distressed_session_789"
        state.user_id = "distressed_user_101"
        state.therapeutic_goals = ["crisis_management"]
        state.progress_metrics = {"crisis_management": 0.1}
        state.context = {}
        state.emotional_state = {
            "anxious": 0.9,
            "depressed": 0.8,
            "overwhelmed": 0.9,
            "hopeful": 0.1,
        }
        return state

    @pytest.mark.asyncio
    async def test_monitor_emotional_state_normal(
        self, emotional_safety_system, session_state
    ):
        """Test emotional state monitoring for normal emotional state."""
        interaction_data = {
            "content": "I'm feeling a bit anxious about the upcoming conversation",
            "recent_choice": "Take a moment to breathe before responding",
        }

        snapshot = await emotional_safety_system.monitor_emotional_state(
            session_state, interaction_data
        )

        # Check snapshot structure
        assert isinstance(snapshot, EmotionalStateSnapshot)
        assert snapshot.user_id == session_state.user_id
        assert snapshot.session_id == session_state.session_id

        # Check emotional state mapping
        assert EmotionalState.ANXIOUS in snapshot.primary_emotions
        assert snapshot.primary_emotions[EmotionalState.ANXIOUS] == 0.7

        # Check distress level calculation
        assert snapshot.distress_level in [DistressLevel.MODERATE, DistressLevel.HIGH]

        # Check that snapshot was stored
        assert session_state.user_id in emotional_safety_system.emotional_snapshots
        assert (
            len(emotional_safety_system.emotional_snapshots[session_state.user_id]) == 1
        )

    @pytest.mark.asyncio
    async def test_monitor_emotional_state_distressed(
        self, emotional_safety_system, distressed_session_state, event_bus
    ):
        """Test emotional state monitoring for distressed state."""
        interaction_data = {
            "content": "I can't handle this anymore, everything feels hopeless",
            "recent_choice": "Express feelings of overwhelm",
        }

        snapshot = await emotional_safety_system.monitor_emotional_state(
            distressed_session_state, interaction_data
        )

        # Check high distress level
        assert snapshot.distress_level >= DistressLevel.HIGH

        # Check that intervention was triggered
        assert (
            "immediate_support_provided" in distressed_session_state.context
            or "crisis_intervention_active" in distressed_session_state.context
        )

        # Check that safety event was published
        event_bus.publish.assert_called()

    def test_calculate_distress_level(self, emotional_safety_system):
        """Test distress level calculation."""
        # Test no distress
        emotions = {EmotionalState.CALM: 0.8, EmotionalState.HOPEFUL: 0.6}
        distress = emotional_safety_system._calculate_distress_level(emotions)
        assert distress == DistressLevel.NONE

        # Test mild distress
        emotions = {EmotionalState.ANXIOUS: 0.2, EmotionalState.CALM: 0.6}
        distress = emotional_safety_system._calculate_distress_level(emotions)
        assert distress == DistressLevel.MILD

        # Test high distress
        emotions = {EmotionalState.ANXIOUS: 0.8, EmotionalState.OVERWHELMED: 0.9}
        distress = emotional_safety_system._calculate_distress_level(emotions)
        assert distress >= DistressLevel.HIGH

        # Test critical distress
        emotions = {EmotionalState.DEPRESSED: 0.9, EmotionalState.OVERWHELMED: 1.0}
        distress = emotional_safety_system._calculate_distress_level(emotions)
        assert distress == DistressLevel.CRITICAL

    def test_detect_trigger_indicators(self, emotional_safety_system):
        """Test trigger indicator detection."""
        # Test trauma-related content
        interaction_data = {
            "content": "The violence in that scene reminded me of my trauma"
        }
        indicators = emotional_safety_system._detect_trigger_indicators(
            interaction_data
        )
        assert "potential_trauma_trigger" in indicators

        # Test anxiety-related content
        interaction_data = {
            "content": "I'm feeling really scared and panicked about this"
        }
        indicators = emotional_safety_system._detect_trigger_indicators(
            interaction_data
        )
        assert "potential_anxiety_trigger" in indicators

        # Test rapid emotional change
        interaction_data = {"emotional_change": 0.5}
        indicators = emotional_safety_system._detect_trigger_indicators(
            interaction_data
        )
        assert "rapid_emotional_change" in indicators

    def test_identify_protective_factors(self, emotional_safety_system, session_state):
        """Test protective factor identification."""
        # Add positive progress
        session_state.progress_metrics = {"anxiety_management": 0.7}
        session_state.emotional_state = {"calm": 0.8, "hopeful": 0.6}
        session_state.context = {
            "coping_skills_used": True,
            "support_system_active": True,
        }

        factors = emotional_safety_system._identify_protective_factors(session_state)

        assert "therapeutic_progress" in factors
        assert "positive_emotional_state" in factors
        assert "active_coping" in factors
        assert "social_support" in factors

    @pytest.mark.asyncio
    async def test_detect_triggers_in_content(self, emotional_safety_system):
        """Test trigger detection in content."""
        # Test trauma-related triggers
        content = "The scene showed violence and abuse that was very disturbing"
        triggers = await emotional_safety_system.detect_triggers(content, {})

        trauma_triggers = [
            t for t in triggers if t.category == TriggerCategory.TRAUMA_RELATED
        ]
        assert len(trauma_triggers) > 0
        assert trauma_triggers[0].intensity > 0.5

        # Test anxiety-inducing triggers
        content = "I'm feeling really scared and panicked about what might happen"
        triggers = await emotional_safety_system.detect_triggers(content, {})

        anxiety_triggers = [
            t for t in triggers if t.category == TriggerCategory.ANXIETY_INDUCING
        ]
        assert len(anxiety_triggers) > 0

        # Test depression-related triggers
        content = "Everything feels hopeless and I feel completely worthless"
        triggers = await emotional_safety_system.detect_triggers(content, {})

        depression_triggers = [
            t for t in triggers if t.category == TriggerCategory.DEPRESSION_TRIGGERING
        ]
        assert len(depression_triggers) > 0
        assert depression_triggers[0].expected_distress_level >= DistressLevel.HIGH

    @pytest.mark.asyncio
    async def test_select_interventions(self, emotional_safety_system):
        """Test intervention selection."""
        # Create snapshot with anxiety
        snapshot = EmotionalStateSnapshot(
            user_id="test_user",
            session_id="test_session",
            primary_emotions={EmotionalState.ANXIOUS: 0.8},
            distress_level=DistressLevel.HIGH,
        )

        interventions = await emotional_safety_system._select_interventions(snapshot)

        # Should select interventions targeting anxiety and high distress
        assert len(interventions) > 0

        for intervention in interventions:
            assert EmotionalState.ANXIOUS in intervention.target_emotions
            assert DistressLevel.HIGH in intervention.target_distress_levels

        # Should be sorted by effectiveness
        if len(interventions) > 1:
            assert (
                interventions[0].estimated_effectiveness
                >= interventions[1].estimated_effectiveness
            )

    @pytest.mark.asyncio
    async def test_crisis_protocol_activation(
        self, emotional_safety_system, distressed_session_state
    ):
        """Test crisis protocol activation."""
        snapshot = EmotionalStateSnapshot(
            user_id=distressed_session_state.user_id,
            session_id=distressed_session_state.session_id,
            primary_emotions={
                EmotionalState.DEPRESSED: 0.9,
                EmotionalState.OVERWHELMED: 1.0,
            },
            distress_level=DistressLevel.CRITICAL,
        )

        await emotional_safety_system._activate_crisis_protocol(
            distressed_session_state, snapshot
        )

        # Check crisis intervention markers
        assert distressed_session_state.context["crisis_intervention_active"] == True
        assert "crisis_intervention_time" in distressed_session_state.context
        assert "crisis_resources_provided" in distressed_session_state.context
        assert distressed_session_state.context["narrative_paused_for_safety"] == True

        # Check metrics
        assert emotional_safety_system.metrics["crisis_protocols_activated"] > 0

    @pytest.mark.asyncio
    async def test_provide_immediate_support(
        self, emotional_safety_system, session_state
    ):
        """Test immediate support provision."""
        snapshot = EmotionalStateSnapshot(
            user_id=session_state.user_id,
            session_id=session_state.session_id,
            primary_emotions={EmotionalState.ANXIOUS: 0.8},
            distress_level=DistressLevel.HIGH,
        )

        interventions = await emotional_safety_system._select_interventions(snapshot)
        await emotional_safety_system._provide_immediate_support(
            session_state, snapshot, interventions
        )

        # Check support provision markers
        assert session_state.context["immediate_support_provided"] == True
        assert "support_interventions" in session_state.context
        assert session_state.context["content_warning_suggested"] == True

        # Check intervention details
        support_interventions = session_state.context["support_interventions"]
        assert len(support_interventions) > 0

        for intervention in support_interventions:
            assert "type" in intervention
            assert "title" in intervention
            assert "description" in intervention
            assert "instructions" in intervention

    @pytest.mark.asyncio
    async def test_offer_coping_support(self, emotional_safety_system, session_state):
        """Test coping support offering."""
        snapshot = EmotionalStateSnapshot(
            user_id=session_state.user_id,
            session_id=session_state.session_id,
            primary_emotions={EmotionalState.ANXIOUS: 0.6},
            distress_level=DistressLevel.MODERATE,
        )

        interventions = await emotional_safety_system._select_interventions(snapshot)
        await emotional_safety_system._offer_coping_support(
            session_state, snapshot, interventions
        )

        # Check coping support markers
        assert session_state.context["coping_support_offered"] == True
        assert "coping_strategies" in session_state.context
        assert "available_interventions" in session_state.context

        # Check coping strategies
        coping_strategies = session_state.context["coping_strategies"]
        assert len(coping_strategies) > 0
        assert len(coping_strategies) <= 3  # Should limit to top 3

    @pytest.mark.asyncio
    async def test_emotional_regulation_support(
        self, emotional_safety_system, session_state
    ):
        """Test emotional regulation support provision."""
        support_response = (
            await emotional_safety_system.provide_emotional_regulation_support(
                session_state, EmotionalState.ANXIOUS, 0.8
            )
        )

        # Check response structure
        assert support_response["emotion"] == EmotionalState.ANXIOUS.value
        assert support_response["intensity"] == 0.8
        assert len(support_response["support_provided"]) > 0
        assert len(support_response["techniques_offered"]) > 0

        # High intensity should include grounding techniques
        assert "grounding_techniques" in support_response

        # Check session storage
        assert "emotional_regulation_support" in session_state.context

    def test_emotional_history_tracking(self, emotional_safety_system, session_state):
        """Test emotional history tracking."""
        user_id = session_state.user_id

        # Create multiple snapshots
        snapshots = []
        for i in range(5):
            snapshot = EmotionalStateSnapshot(
                user_id=user_id,
                session_id=session_state.session_id,
                primary_emotions={EmotionalState.ANXIOUS: 0.5 + i * 0.1},
                distress_level=DistressLevel.MILD,
                created_at=datetime.utcnow() - timedelta(hours=i),
            )
            snapshots.append(snapshot)

        emotional_safety_system.emotional_snapshots[user_id] = snapshots

        # Get recent history
        history = emotional_safety_system.get_emotional_history(user_id, hours=3)

        # Should return snapshots from last 3 hours
        assert len(history) == 3

        # Should be in chronological order
        for snapshot in history:
            assert snapshot.created_at > datetime.utcnow() - timedelta(hours=3)

    def test_pattern_analysis(self, emotional_safety_system, session_state):
        """Test emotional pattern analysis."""
        user_id = session_state.user_id

        # Create snapshots with increasing distress
        snapshots = []
        for i in range(5):
            snapshot = EmotionalStateSnapshot(
                user_id=user_id,
                session_id=session_state.session_id,
                distress_level=DistressLevel(i),
                emotional_stability=0.8 - i * 0.1,
                created_at=datetime.utcnow() - timedelta(minutes=i * 5),
            )
            snapshots.append(snapshot)

        emotional_safety_system.emotional_snapshots[user_id] = snapshots

        # Analyze patterns
        trend = emotional_safety_system._analyze_distress_trend(snapshots)
        assert trend == "increasing"

        stability_trend = emotional_safety_system._analyze_stability_trend(snapshots)
        assert stability_trend == "decreasing"

    def test_intervention_library_loading(self, emotional_safety_system):
        """Test that intervention library is properly loaded."""
        interventions = emotional_safety_system.interventions

        # Check that all intervention types are loaded
        assert InterventionType.GROUNDING_TECHNIQUE in interventions
        assert InterventionType.BREATHING_EXERCISE in interventions
        assert InterventionType.EMOTIONAL_VALIDATION in interventions
        assert InterventionType.RESOURCE_PROVISION in interventions

        # Check intervention structure
        for intervention_type, intervention_list in interventions.items():
            assert len(intervention_list) > 0

            for intervention in intervention_list:
                assert isinstance(intervention, SafetyIntervention)
                assert intervention.title != ""
                assert intervention.description != ""
                assert len(intervention.target_emotions) > 0
                assert len(intervention.target_distress_levels) > 0
                assert 0.0 <= intervention.estimated_effectiveness <= 1.0

    def test_coping_strategies_loading(self, emotional_safety_system):
        """Test that coping strategies are properly loaded."""
        strategies = emotional_safety_system.coping_strategies

        # Check that strategies exist for key emotions
        assert EmotionalState.ANXIOUS in strategies
        assert EmotionalState.DEPRESSED in strategies
        assert EmotionalState.ANGRY in strategies
        assert EmotionalState.OVERWHELMED in strategies

        # Check strategy content
        for emotion, strategy_list in strategies.items():
            assert len(strategy_list) > 0

            for strategy in strategy_list:
                assert isinstance(strategy, str)
                assert len(strategy) > 0

    def test_metrics_tracking(self, emotional_safety_system):
        """Test metrics tracking."""
        initial_metrics = emotional_safety_system.get_metrics()

        # Check metric structure
        assert "emotional_snapshots_created" in initial_metrics
        assert "triggers_detected" in initial_metrics
        assert "interventions_triggered" in initial_metrics
        assert "crisis_protocols_activated" in initial_metrics
        assert "successful_interventions" in initial_metrics
        assert "active_users_monitored" in initial_metrics

        # Initially should be zero
        assert initial_metrics["emotional_snapshots_created"] == 0
        assert initial_metrics["triggers_detected"] == 0

    @pytest.mark.asyncio
    async def test_health_check(self, emotional_safety_system):
        """Test health check functionality."""
        health = await emotional_safety_system.health_check()

        assert health["status"] == "healthy"
        assert health["monitoring_enabled"] == True
        assert "intervention_threshold" in health
        assert "interventions_loaded" in health
        assert "grounding_techniques_loaded" in health
        assert "coping_strategies_loaded" in health
        assert "metrics" in health

        # Should have loaded interventions and techniques
        assert health["interventions_loaded"] > 0
        assert health["grounding_techniques_loaded"] > 0
        assert health["coping_strategies_loaded"] > 0

    def test_monitoring_control(self, emotional_safety_system):
        """Test monitoring enable/disable functionality."""
        # Test disable
        emotional_safety_system.disable_monitoring()
        assert emotional_safety_system.monitoring_enabled == False

        # Test enable
        emotional_safety_system.enable_monitoring()
        assert emotional_safety_system.monitoring_enabled == True

    def test_intervention_threshold_setting(self, emotional_safety_system):
        """Test intervention threshold setting."""
        # Test setting threshold
        emotional_safety_system.set_intervention_threshold(DistressLevel.HIGH)
        assert emotional_safety_system.intervention_threshold == DistressLevel.HIGH

        # Test setting different threshold
        emotional_safety_system.set_intervention_threshold(DistressLevel.MILD)
        assert emotional_safety_system.intervention_threshold == DistressLevel.MILD
