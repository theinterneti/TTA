"""
Unit tests for gameplay loop models.

Tests all Pydantic models and dataclasses in:
  - src/components/gameplay_loop/models/core.py
  - src/components/gameplay_loop/models/interactions.py
  - src/components/gameplay_loop/models/progress.py
  - src/components/gameplay_loop/models/validation.py
"""

from __future__ import annotations

import time

import pytest
from pydantic import ValidationError

from src.components.gameplay_loop.models.core import (
    Choice,
    ChoiceType,
    ConsequenceSet,
    DifficultyLevel,
    EmotionalState,
    GameplayMetrics,
    Scene,
    SceneType,
    SessionState,
    TherapeuticContext,
)
from src.components.gameplay_loop.models.interactions import (
    AgencyAssessment,
    ChoiceOutcome,
    EventType,
    GameplaySession,
    InterventionType,
    NarrativeEvent,
    OutcomeType,
    TherapeuticIntervention,
    UserChoice,
)
from src.components.gameplay_loop.models.progress import (
    CharacterAttribute,
    CharacterState,
    ProgressMarker,
    ProgressType,
    SkillCategory,
    SkillDevelopment,
    TherapeuticProgress,
)
from src.components.gameplay_loop.models.validation import (
    ContentValidation,
    SafetyCheck,
    SafetyLevel,
    TherapeuticValidation,
    ValidationResult,
    ValidationStatus,
    ValidationType,
)

# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------


class TestEnums:
    """Test all StrEnum types."""

    def test_difficulty_level_values(self):
        assert DifficultyLevel.GENTLE == "gentle"
        assert DifficultyLevel.STANDARD == "standard"
        assert DifficultyLevel.CHALLENGING == "challenging"
        assert DifficultyLevel.INTENSIVE == "intensive"

    def test_emotional_state_values(self):
        assert EmotionalState.CALM == "calm"
        assert EmotionalState.ENGAGED == "engaged"
        assert EmotionalState.ANXIOUS == "anxious"
        assert EmotionalState.OVERWHELMED == "overwhelmed"
        assert EmotionalState.DISTRESSED == "distressed"
        assert EmotionalState.CRISIS == "crisis"

    def test_scene_type_values(self):
        assert SceneType.INTRODUCTION == "introduction"
        assert SceneType.EXPLORATION == "exploration"
        assert SceneType.CHALLENGE == "challenge"
        assert SceneType.REFLECTION == "reflection"
        assert SceneType.THERAPEUTIC == "therapeutic"
        assert SceneType.RESOLUTION == "resolution"

    def test_choice_type_values(self):
        assert ChoiceType.NARRATIVE == "narrative"
        assert ChoiceType.THERAPEUTIC == "therapeutic"
        assert ChoiceType.SKILL_BUILDING == "skill_building"
        assert ChoiceType.EMOTIONAL_REGULATION == "emotional_regulation"
        assert ChoiceType.SOCIAL_INTERACTION == "social_interaction"

    def test_intervention_type_values(self):
        assert InterventionType.MINDFULNESS == "mindfulness"
        assert InterventionType.CRISIS_SUPPORT == "crisis_support"

    def test_outcome_type_values(self):
        assert OutcomeType.SUCCESS == "success"
        assert OutcomeType.FAILURE == "failure"
        assert OutcomeType.NEUTRAL == "neutral"

    def test_event_type_values(self):
        assert EventType.SCENE_TRANSITION == "scene_transition"
        assert EventType.ACHIEVEMENT == "achievement"

    def test_progress_type_values(self):
        assert ProgressType.SKILL_ACQUIRED == "skill_acquired"
        assert ProgressType.THERAPEUTIC_BREAKTHROUGH == "therapeutic_breakthrough"
        assert ProgressType.RESILIENCE_BUILDING == "resilience_building"

    def test_skill_category_values(self):
        assert SkillCategory.EMOTIONAL_REGULATION == "emotional_regulation"
        assert SkillCategory.MINDFULNESS == "mindfulness"

    def test_character_attribute_values(self):
        assert CharacterAttribute.CONFIDENCE == "confidence"
        assert CharacterAttribute.RESILIENCE == "resilience"

    def test_validation_status_values(self):
        assert ValidationStatus.PASSED == "passed"
        assert ValidationStatus.FAILED == "failed"
        assert ValidationStatus.WARNING == "warning"
        assert ValidationStatus.PENDING == "pending"
        assert ValidationStatus.SKIPPED == "skipped"

    def test_safety_level_values(self):
        assert SafetyLevel.SAFE == "safe"
        assert SafetyLevel.CAUTION == "caution"
        assert SafetyLevel.DANGER == "danger"
        assert SafetyLevel.CRISIS == "crisis"

    def test_validation_type_values(self):
        assert ValidationType.CONTENT_SAFETY == "content_safety"
        assert ValidationType.CHOICE_VALIDITY == "choice_validity"


# ---------------------------------------------------------------------------
# TherapeuticContext dataclass
# ---------------------------------------------------------------------------


class TestTherapeuticContext:
    def test_default_instantiation(self):
        ctx = TherapeuticContext()
        assert ctx.primary_goals == []
        assert ctx.secondary_goals == []
        assert ctx.therapeutic_modalities == []
        assert ctx.contraindications == []
        assert ctx.safety_protocols == []
        assert ctx.session_objectives == []
        assert ctx.completed_objectives == []
        assert ctx.therapeutic_insights == []
        assert ctx.progress_markers == []

    def test_with_values(self):
        ctx = TherapeuticContext(
            primary_goals=["anxiety_management"],
            secondary_goals=["resilience"],
            therapeutic_modalities=["CBT"],
            contraindications=["none"],
            safety_protocols=["standard"],
            session_objectives=["obj1"],
            completed_objectives=["obj2"],
            therapeutic_insights=["insight1"],
            progress_markers=["marker1"],
        )
        assert ctx.primary_goals == ["anxiety_management"]
        assert ctx.therapeutic_modalities == ["CBT"]
        assert ctx.completed_objectives == ["obj2"]

    def test_lists_are_independent(self):
        ctx1 = TherapeuticContext()
        ctx2 = TherapeuticContext()
        ctx1.primary_goals.append("goal")
        assert ctx2.primary_goals == []


# ---------------------------------------------------------------------------
# GameplayMetrics dataclass
# ---------------------------------------------------------------------------


class TestGameplayMetrics:
    def test_default_instantiation(self):
        m = GameplayMetrics()
        assert m.total_choices_made == 0
        assert m.therapeutic_choices_made == 0
        assert m.average_response_time == 0.0
        assert m.engagement_score == 0.0
        assert m.therapeutic_effectiveness == 0.0
        assert m.session_duration == 0.0
        assert m.active_time == 0.0
        assert m.pause_time == 0.0
        assert m.safety_interventions == 0
        assert m.crisis_alerts == 0
        assert m.emotional_state_changes == []

    def test_with_values(self):
        m = GameplayMetrics(
            total_choices_made=5,
            therapeutic_choices_made=3,
            engagement_score=0.8,
        )
        assert m.total_choices_made == 5
        assert m.therapeutic_choices_made == 3
        assert m.engagement_score == 0.8


# ---------------------------------------------------------------------------
# Scene model
# ---------------------------------------------------------------------------


class TestScene:
    def test_required_fields(self):
        scene = Scene(
            title="Test Scene",
            description="A description",
            narrative_content="The narrative",
        )
        assert scene.title == "Test Scene"
        assert scene.description == "A description"
        assert scene.narrative_content == "The narrative"

    def test_default_values(self):
        scene = Scene(
            title="T", description="D", narrative_content="N"
        )
        assert scene.scene_type == SceneType.EXPLORATION
        assert scene.difficulty_level == DifficultyLevel.STANDARD
        assert scene.estimated_duration == 300
        assert scene.therapeutic_focus == []
        assert scene.learning_objectives == []
        assert scene.emotional_tone == "neutral"
        assert scene.interaction_frequency_preference is None
        assert scene.choice_complexity_preference is None
        assert scene.is_completed is False
        assert scene.completion_time is None
        assert scene.player_choices_made == []

    def test_scene_id_is_generated(self):
        s1 = Scene(title="T", description="D", narrative_content="N")
        s2 = Scene(title="T", description="D", narrative_content="N")
        assert s1.scene_id != s2.scene_id

    def test_custom_scene_type(self):
        scene = Scene(
            title="T",
            description="D",
            narrative_content="N",
            scene_type=SceneType.THERAPEUTIC,
        )
        assert scene.scene_type == SceneType.THERAPEUTIC

    def test_missing_required_fields_raises(self):
        with pytest.raises(ValidationError):
            Scene(description="D", narrative_content="N")  # missing title


# ---------------------------------------------------------------------------
# Choice model
# ---------------------------------------------------------------------------


class TestChoice:
    def test_required_fields(self):
        c = Choice(choice_text="Go left")
        assert c.choice_text == "Go left"

    def test_default_values(self):
        c = Choice(choice_text="Go left")
        assert c.scene_id == ""
        assert c.description is None
        assert c.choice_type == ChoiceType.NARRATIVE
        assert c.difficulty_level == DifficultyLevel.STANDARD
        assert c.therapeutic_value == 0.0
        assert c.prerequisites == []
        assert c.emotional_requirements == []
        assert c.skill_requirements == []
        assert c.immediate_consequences == []
        assert c.long_term_consequences == []
        assert c.therapeutic_outcomes == []
        assert c.therapeutic_tags == []
        assert c.agency_level == 0.5
        assert c.meaningfulness_score == 0.5
        assert c.emotional_context == []
        assert c.is_available is True
        assert c.availability_reason is None

    def test_therapeutic_value_bounds(self):
        with pytest.raises(ValidationError):
            Choice(choice_text="T", therapeutic_value=-0.1)
        with pytest.raises(ValidationError):
            Choice(choice_text="T", therapeutic_value=1.1)

    def test_agency_level_bounds(self):
        with pytest.raises(ValidationError):
            Choice(choice_text="T", agency_level=-0.1)
        with pytest.raises(ValidationError):
            Choice(choice_text="T", agency_level=1.1)

    def test_meaningfulness_score_bounds(self):
        with pytest.raises(ValidationError):
            Choice(choice_text="T", meaningfulness_score=-0.1)

    def test_choice_id_generated(self):
        c1 = Choice(choice_text="T")
        c2 = Choice(choice_text="T")
        assert c1.choice_id != c2.choice_id

    def test_full_instantiation(self):
        c = Choice(
            choice_text="Meditate",
            scene_id="scene-1",
            choice_type=ChoiceType.THERAPEUTIC,
            difficulty_level=DifficultyLevel.GENTLE,
            therapeutic_value=0.9,
            therapeutic_tags=["mindfulness"],
            agency_level=0.8,
            meaningfulness_score=0.7,
            is_available=True,
        )
        assert c.choice_type == ChoiceType.THERAPEUTIC
        assert c.therapeutic_value == 0.9
        assert "mindfulness" in c.therapeutic_tags


# ---------------------------------------------------------------------------
# ConsequenceSet model
# ---------------------------------------------------------------------------


class TestConsequenceSet:
    def test_required_fields(self):
        cs = ConsequenceSet(choice_id="choice-1")
        assert cs.choice_id == "choice-1"
        assert cs.session_id == ""

    def test_default_values(self):
        cs = ConsequenceSet(choice_id="c1")
        assert cs.immediate_effects == {}
        assert cs.delayed_effects == {}
        assert cs.narrative_changes == []
        assert cs.character_attribute_changes == {}
        assert cs.skill_developments == []
        assert cs.relationship_changes == {}
        assert cs.therapeutic_progress == {}
        assert cs.emotional_impact == {}
        assert cs.learning_opportunities == []
        assert cs.therapeutic_insights == []
        assert cs.therapeutic_value_realized == 0.0
        assert cs.immediate_outcomes == []
        assert cs.delayed_outcomes == []
        assert cs.narrative_consequences == []
        assert cs.causality_explanation == ""
        assert cs.progress_markers == []
        assert cs.skill_development == []
        assert cs.character_development == {}
        assert cs.world_state_changes == {}
        assert cs.is_applied is False
        assert cs.application_time is None

    def test_therapeutic_value_bounds(self):
        with pytest.raises(ValidationError):
            ConsequenceSet(choice_id="c1", therapeutic_value_realized=1.5)

    def test_consequence_id_generated(self):
        c1 = ConsequenceSet(choice_id="x")
        c2 = ConsequenceSet(choice_id="x")
        assert c1.consequence_id != c2.consequence_id


# ---------------------------------------------------------------------------
# SessionState model
# ---------------------------------------------------------------------------


class TestSessionState:
    def test_required_fields(self):
        ss = SessionState(user_id="user-1")
        assert ss.user_id == "user-1"

    def test_default_values(self):
        ss = SessionState(user_id="u1")
        assert ss.character_id is None
        assert ss.world_id is None
        assert ss.current_scene is None
        assert ss.current_scene_id is None
        assert isinstance(ss.therapeutic_context, TherapeuticContext)
        assert ss.emotional_state == EmotionalState.CALM
        assert ss.difficulty_level == DifficultyLevel.STANDARD
        assert ss.choice_history == []
        assert ss.scene_history == []
        assert ss.consequence_stack == []
        assert ss.total_session_time == 0.0
        assert isinstance(ss.metrics, GameplayMetrics)
        assert ss.is_active is True
        assert ss.is_paused is False
        assert ss.requires_therapeutic_intervention is False
        assert ss.safety_level == "standard"
        assert ss.last_safety_check is None
        assert ss.safety_alerts == []

    def test_session_id_generated(self):
        s1 = SessionState(user_id="u")
        s2 = SessionState(user_id="u")
        assert s1.session_id != s2.session_id

    def test_update_activity_increments_time(self):
        ss = SessionState(user_id="u1")
        ss.is_paused = False
        # Give it a tiny bit of time so total_session_time > 0
        time.sleep(0.01)
        ss.update_activity()
        assert ss.total_session_time > 0.0
        assert ss.metrics.active_time > 0.0

    def test_update_activity_while_paused(self):
        ss = SessionState(user_id="u1")
        ss.is_paused = True
        time.sleep(0.01)
        ss.update_activity()
        # Paused: no time should be added
        assert ss.total_session_time == 0.0
        assert ss.metrics.active_time == 0.0

    def test_add_choice_to_history_narrative(self):
        ss = SessionState(user_id="u1")
        choice = Choice(
            choice_text="Go north",
            choice_type=ChoiceType.NARRATIVE,
            therapeutic_value=0.3,
        )
        ss.add_choice_to_history(choice, {"result": "moved"})
        assert len(ss.choice_history) == 1
        assert ss.metrics.total_choices_made == 1
        assert ss.metrics.therapeutic_choices_made == 0

    def test_add_choice_to_history_therapeutic(self):
        ss = SessionState(user_id="u1")
        choice = Choice(
            choice_text="Breathe deeply",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_value=0.8,
        )
        ss.add_choice_to_history(choice, {})
        assert ss.metrics.therapeutic_choices_made == 1

    def test_add_choice_to_history_skill_building(self):
        ss = SessionState(user_id="u1")
        choice = Choice(
            choice_text="Practice skill",
            choice_type=ChoiceType.SKILL_BUILDING,
            therapeutic_value=0.6,
        )
        ss.add_choice_to_history(choice, {})
        assert ss.metrics.therapeutic_choices_made == 1

    def test_add_choice_to_history_emotional_regulation(self):
        ss = SessionState(user_id="u1")
        choice = Choice(
            choice_text="Regulate emotion",
            choice_type=ChoiceType.EMOTIONAL_REGULATION,
            therapeutic_value=0.7,
        )
        ss.add_choice_to_history(choice, {})
        assert ss.metrics.therapeutic_choices_made == 1

    def test_add_choice_records_fields(self):
        ss = SessionState(user_id="u1")
        choice = Choice(
            choice_text="Test choice",
            choice_type=ChoiceType.NARRATIVE,
            therapeutic_value=0.5,
        )
        outcome = {"key": "value"}
        ss.add_choice_to_history(choice, outcome)
        record = ss.choice_history[0]
        assert record["choice_id"] == choice.choice_id
        assert record["choice_text"] == "Test choice"
        assert record["outcome"] == outcome

    def test_transition_to_scene(self):
        ss = SessionState(user_id="u1")
        scene1 = Scene(title="S1", description="D1", narrative_content="N1")
        scene2 = Scene(title="S2", description="D2", narrative_content="N2")

        ss.transition_to_scene(scene1)
        assert ss.current_scene == scene1
        assert ss.current_scene_id == scene1.scene_id
        assert len(ss.scene_history) == 0

        ss.transition_to_scene(scene2)
        assert ss.current_scene == scene2
        assert ss.current_scene_id == scene2.scene_id
        assert scene1.scene_id in ss.scene_history

    def test_calculate_engagement_score_zero_time(self):
        ss = SessionState(user_id="u1")
        score = ss.calculate_engagement_score()
        assert score == 0.0

    def test_calculate_engagement_score_with_data(self):
        ss = SessionState(user_id="u1")
        ss.total_session_time = 120.0  # 2 minutes
        ss.metrics.total_choices_made = 4
        ss.metrics.therapeutic_choices_made = 2
        score = ss.calculate_engagement_score()
        assert 0.0 <= score <= 1.0
        assert ss.metrics.engagement_score == score


# ---------------------------------------------------------------------------
# Interactions models
# ---------------------------------------------------------------------------


class TestUserChoice:
    def test_required_fields(self):
        uc = UserChoice(
            choice_id="c1",
            session_id="s1",
            scene_id="sc1",
            choice_text="Go right",
            choice_type=ChoiceType.NARRATIVE,
            emotional_state_before=EmotionalState.CALM,
        )
        assert uc.choice_id == "c1"
        assert uc.session_id == "s1"
        assert uc.choice_text == "Go right"

    def test_default_values(self):
        uc = UserChoice(
            choice_id="c1",
            session_id="s1",
            scene_id="sc1",
            choice_text="T",
            choice_type=ChoiceType.NARRATIVE,
            emotional_state_before=EmotionalState.CALM,
        )
        assert uc.therapeutic_value == 0.0
        assert uc.therapeutic_tags == []
        assert uc.agency_level == 0.5
        assert uc.emotional_state_after is None
        assert uc.response_time == 0.0
        assert uc.user_confidence is None
        assert uc.difficulty_perceived is None

    def test_therapeutic_value_bounds(self):
        with pytest.raises(ValidationError):
            UserChoice(
                choice_id="c1",
                session_id="s1",
                scene_id="sc1",
                choice_text="T",
                choice_type=ChoiceType.NARRATIVE,
                emotional_state_before=EmotionalState.CALM,
                therapeutic_value=1.5,
            )

    def test_user_confidence_bounds(self):
        with pytest.raises(ValidationError):
            UserChoice(
                choice_id="c1",
                session_id="s1",
                scene_id="sc1",
                choice_text="T",
                choice_type=ChoiceType.NARRATIVE,
                emotional_state_before=EmotionalState.CALM,
                user_confidence=1.5,
            )


class TestChoiceOutcome:
    def test_required_fields(self):
        co = ChoiceOutcome(choice_id="c1", outcome_type="success")
        assert co.choice_id == "c1"
        assert co.outcome_type == "success"

    def test_defaults(self):
        co = ChoiceOutcome(choice_id="c1", outcome_type="neutral")
        assert co.session_id == ""
        assert co.narrative_response == ""
        assert co.immediate_effects == {}
        assert co.character_changes == {}
        assert co.therapeutic_progress == {}
        assert co.skills_developed == []
        assert co.insights_gained == []
        assert co.learning_opportunities == []
        assert co.narrative_consequences == []
        assert co.emotional_response == "neutral"
        assert co.next_scene_id is None
        assert co.available_choices == []
        assert co.requires_therapeutic_intervention is False
        assert co.safety_concerns == []


class TestNarrativeEvent:
    def test_required_fields(self):
        ev = NarrativeEvent(
            session_id="s1",
            event_type=EventType.SCENE_TRANSITION,
            title="A scene transition",
            description="Moving to next area",
            narrative_impact="Story changes",
        )
        assert ev.session_id == "s1"
        assert ev.event_type == EventType.SCENE_TRANSITION
        assert ev.title == "A scene transition"

    def test_defaults(self):
        ev = NarrativeEvent(
            session_id="s1",
            event_type=EventType.ACHIEVEMENT,
            title="T",
            description="D",
            narrative_impact="I",
        )
        assert ev.scene_id is None
        assert ev.triggered_by_choice is None
        assert ev.emotional_context == EmotionalState.CALM
        assert ev.character_impact == {}
        assert ev.therapeutic_significance == 0.0
        assert ev.unlocked_content == []
        assert ev.blocked_content == []


class TestTherapeuticIntervention:
    def test_required_fields(self):
        ti = TherapeuticIntervention(
            session_id="s1",
            intervention_type=InterventionType.MINDFULNESS,
            title="Breathe",
            description="Breathing exercise",
            content="Inhale for 4 counts",
            triggered_by="anxiety_detected",
            emotional_state=EmotionalState.ANXIOUS,
        )
        assert ti.session_id == "s1"
        assert ti.intervention_type == InterventionType.MINDFULNESS

    def test_defaults(self):
        ti = TherapeuticIntervention(
            session_id="s1",
            intervention_type=InterventionType.GROUNDING,
            title="T",
            description="D",
            content="C",
            triggered_by="trigger",
            emotional_state=EmotionalState.CALM,
        )
        assert ti.urgency_level == "standard"
        assert ti.is_mandatory is False
        assert ti.estimated_duration == 300
        assert ti.completion_status == "pending"
        assert ti.effectiveness_rating is None
        assert ti.user_feedback is None
        assert ti.follow_up_required is False
        assert ti.follow_up_scheduled is None
        assert ti.completed_at is None


class TestAgencyAssessment:
    def test_required_fields(self):
        aa = AgencyAssessment(
            choice_id="c1",
            agency_level="HIGH",
            empowerment_score=0.9,
        )
        assert aa.choice_id == "c1"
        assert aa.agency_level == "HIGH"
        assert aa.empowerment_score == 0.9

    def test_empowerment_score_bounds(self):
        with pytest.raises(ValidationError):
            AgencyAssessment(
                choice_id="c1", agency_level="HIGH", empowerment_score=1.5
            )

    def test_defaults(self):
        aa = AgencyAssessment(
            choice_id="c1", agency_level="MODERATE", empowerment_score=0.5
        )
        assert aa.empowerment_factors == []
        assert aa.agency_concerns == []
        assert aa.recommendations == []


class TestGameplaySession:
    def test_required_fields(self):
        gs = GameplaySession(session_id="s1", user_id="u1")
        assert gs.session_id == "s1"
        assert gs.user_id == "u1"

    def test_defaults(self):
        gs = GameplaySession(session_id="s1", user_id="u1")
        assert gs.current_scene_id is None
        assert gs.current_scene is None
        assert gs.available_choices == []
        assert gs.session_state is None
        assert gs.session_start_time is None
        assert gs.session_end_time is None
        assert gs.session_recap is None
        assert gs.is_active is True
        assert gs.therapeutic_context == {}


# ---------------------------------------------------------------------------
# Progress models
# ---------------------------------------------------------------------------


class TestProgressMarker:
    def test_defaults(self):
        pm = ProgressMarker()
        assert pm.session_id == ""
        assert pm.user_id == ""
        assert pm.progress_type == ProgressType.INSIGHT_GAINED
        assert pm.marker_type is None
        assert pm.title == ""
        assert pm.description == ""
        assert pm.significance == ""
        assert pm.triggered_by_choice is None
        assert pm.scene_context is None
        assert pm.progress_value == 1.0
        assert pm.difficulty_level == DifficultyLevel.STANDARD
        assert pm.therapeutic_domains == []
        assert pm.skills_involved == []

    def test_progress_value_bounds(self):
        with pytest.raises(ValidationError):
            ProgressMarker(progress_value=1.5)

    def test_marker_id_generated(self):
        m1 = ProgressMarker()
        m2 = ProgressMarker()
        assert m1.marker_id != m2.marker_id


class TestSkillDevelopment:
    def test_required_fields(self):
        sd = SkillDevelopment(
            user_id="u1",
            skill_category=SkillCategory.MINDFULNESS,
            skill_name="Breathing",
            description="Breathing techniques",
        )
        assert sd.user_id == "u1"
        assert sd.skill_category == SkillCategory.MINDFULNESS
        assert sd.skill_name == "Breathing"

    def test_defaults(self):
        sd = SkillDevelopment(
            user_id="u1",
            skill_category=SkillCategory.RESILIENCE,
            skill_name="Bouncing back",
            description="D",
        )
        assert sd.current_level == 0.0
        assert sd.target_level == 1.0
        assert sd.practice_sessions == 0
        assert sd.successful_applications == 0
        assert sd.total_attempts == 0
        assert sd.learning_rate == 0.1
        assert sd.retention_rate == 0.9
        assert sd.therapeutic_goals == []
        assert sd.related_skills == []
        assert sd.last_practiced is None
        assert sd.mastery_achieved is None

    def test_update_skill_level_improves_with_good_outcome(self):
        sd = SkillDevelopment(
            user_id="u1",
            skill_category=SkillCategory.MINDFULNESS,
            skill_name="Meditation",
            description="D",
        )
        initial_level = sd.current_level
        sd.update_skill_level(0.9)
        assert sd.current_level > initial_level
        assert sd.total_attempts == 1
        assert sd.successful_applications == 1
        assert sd.last_practiced is not None

    def test_update_skill_level_poor_outcome_counts_attempt(self):
        sd = SkillDevelopment(
            user_id="u1",
            skill_category=SkillCategory.MINDFULNESS,
            skill_name="Meditation",
            description="D",
        )
        sd.update_skill_level(0.3)
        assert sd.total_attempts == 1
        assert sd.successful_applications == 0

    def test_update_skill_level_achieves_mastery(self):
        # learning_rate=1.0 so improvement = 1.0 * (1.0 - 0.99) = 0.01
        # new level = 0.99 + 0.01 = 1.0 which equals target_level=1.0
        sd = SkillDevelopment(
            user_id="u1",
            skill_category=SkillCategory.RESILIENCE,
            skill_name="Coping",
            description="D",
            current_level=0.99,
            target_level=1.0,
            learning_rate=1.0,
        )
        sd.update_skill_level(1.0)
        assert sd.mastery_achieved is not None

    def test_update_skill_level_cap_at_1(self):
        sd = SkillDevelopment(
            user_id="u1",
            skill_category=SkillCategory.RESILIENCE,
            skill_name="Coping",
            description="D",
            current_level=0.98,
            learning_rate=0.5,
        )
        sd.update_skill_level(1.0)
        assert sd.current_level <= 1.0

    def test_skill_level_bounds(self):
        with pytest.raises(ValidationError):
            SkillDevelopment(
                user_id="u1",
                skill_category=SkillCategory.MINDFULNESS,
                skill_name="M",
                description="D",
                current_level=1.5,
            )


class TestCharacterState:
    def test_required_fields(self):
        cs = CharacterState(
            user_id="u1",
            session_id="s1",
            name="Hero",
        )
        assert cs.user_id == "u1"
        assert cs.name == "Hero"

    def test_defaults(self):
        cs = CharacterState(user_id="u1", session_id="s1", name="Hero")
        assert cs.background == ""
        assert cs.current_emotional_state == EmotionalState.CALM
        assert cs.energy_level == 1.0
        assert cs.stress_level == 0.0
        assert cs.total_experience == 0
        assert cs.level == 1
        assert cs.inventory == []
        assert cs.resources == {}

    def test_attributes_initialized_for_all_enum_values(self):
        cs = CharacterState(user_id="u1", session_id="s1", name="Hero")
        for attr in CharacterAttribute:
            assert attr in cs.attributes
            assert cs.attributes[attr] == 0.5

    def test_modify_attribute_clamps_at_bounds(self):
        cs = CharacterState(user_id="u1", session_id="s1", name="Hero")
        cs.modify_attribute(CharacterAttribute.CONFIDENCE, 2.0)
        assert cs.attributes[CharacterAttribute.CONFIDENCE] == 1.0

        cs.modify_attribute(CharacterAttribute.CONFIDENCE, -5.0)
        assert cs.attributes[CharacterAttribute.CONFIDENCE] == 0.0

    def test_modify_attribute_updates_timestamp(self):
        cs = CharacterState(user_id="u1", session_id="s1", name="Hero")
        before = cs.updated_at
        time.sleep(0.01)
        cs.modify_attribute(CharacterAttribute.EMPATHY, 0.1)
        assert cs.updated_at >= before

    def test_add_experience_no_level_up(self):
        cs = CharacterState(user_id="u1", session_id="s1", name="Hero")
        leveled_up = cs.add_experience(10)
        assert leveled_up is False
        assert cs.total_experience == 10
        assert cs.level == 1

    def test_add_experience_causes_level_up(self):
        cs = CharacterState(user_id="u1", session_id="s1", name="Hero")
        # level formula: int((experience / 100) ** 0.5) + 1
        # Need 100 xp to reach level 2
        leveled_up = cs.add_experience(100)
        assert leveled_up is True
        assert cs.level == 2

    def test_add_experience_multiple_increments(self):
        cs = CharacterState(user_id="u1", session_id="s1", name="Hero")
        cs.add_experience(50)
        cs.add_experience(50)
        assert cs.total_experience == 100
        assert cs.level == 2


class TestTherapeuticProgress:
    def test_required_fields(self):
        tp = TherapeuticProgress(user_id="u1")
        assert tp.user_id == "u1"

    def test_defaults(self):
        tp = TherapeuticProgress(user_id="u1")
        assert tp.primary_therapeutic_goals == []
        assert tp.secondary_goals == []
        assert tp.completed_goals == []
        assert tp.overall_progress == 0.0
        assert tp.goal_completion_rate == 0.0
        assert tp.engagement_level == 0.0
        assert tp.developed_skills == []
        assert tp.skills_in_progress == []
        assert tp.milestones_achieved == []
        assert tp.breakthrough_moments == []
        assert tp.total_sessions == 0
        assert tp.total_session_time == 0.0
        assert tp.average_session_length == 0.0

    def test_progress_id_generated(self):
        p1 = TherapeuticProgress(user_id="u1")
        p2 = TherapeuticProgress(user_id="u1")
        assert p1.progress_id != p2.progress_id

    def test_overall_progress_bounds(self):
        with pytest.raises(ValidationError):
            TherapeuticProgress(user_id="u1", overall_progress=1.5)


# ---------------------------------------------------------------------------
# Validation models
# ---------------------------------------------------------------------------


class TestValidationResult:
    def test_defaults(self):
        vr = ValidationResult()
        assert vr.session_id == ""
        assert vr.validation_type == ValidationType.CHOICE_VALIDITY
        assert vr.status == ValidationStatus.PENDING
        assert vr.content_type == ""
        assert vr.content_id is None
        assert vr.is_valid is True
        assert vr.confidence_score == 1.0
        assert vr.issues_found == []
        assert vr.issues == []
        assert vr.warnings == []
        assert vr.recommendations == []
        assert vr.validation_details == {}
        assert vr.user_context == {}
        assert vr.therapeutic_context == {}
        assert vr.validator_version == "1.0.0"

    def test_with_values(self):
        vr = ValidationResult(
            is_valid=False,
            confidence_score=0.7,
            issues=["Issue 1"],
            warnings=["Warning 1"],
            status=ValidationStatus.FAILED,
        )
        assert vr.is_valid is False
        assert vr.confidence_score == 0.7
        assert "Issue 1" in vr.issues


class TestSafetyCheck:
    def test_defaults(self):
        sc = SafetyCheck()
        assert sc.session_id == ""
        assert sc.user_id == ""
        assert sc.safety_level == "safe"
        assert sc.emotional_state == EmotionalState.CALM
        assert sc.is_safe is True
        assert sc.issues == []
        assert sc.risk_factors == []
        assert sc.protective_factors == []
        assert sc.potential_triggers == []
        assert sc.safety_concerns == []
        assert sc.immediate_actions == []
        assert sc.monitoring_required is False
        assert sc.intervention_recommended is False
        assert sc.crisis_indicators == []
        assert sc.requires_immediate_attention is False
        assert sc.triggering_content is None
        assert sc.user_history == {}

    def test_check_id_generated(self):
        sc1 = SafetyCheck()
        sc2 = SafetyCheck()
        assert sc1.check_id != sc2.check_id


class TestTherapeuticValidation:
    def test_defaults(self):
        tv = TherapeuticValidation()
        assert tv.session_id == ""
        assert tv.content_type == ""
        assert tv.content_description == ""
        assert tv.is_therapeutically_appropriate is True
        assert tv.therapeutic_alignment_score == 0.0
        assert tv.issues == []
        assert tv.therapeutic_benefits == []
        assert tv.validator_credentials is None
        assert tv.therapeutic_appropriateness == 0.0
        assert tv.evidence_based is False
        assert tv.contraindications == []
        assert tv.user_readiness == 0.0
        assert tv.difficulty_appropriate is True
        assert tv.timing_appropriate is True
        assert tv.aligned_goals == []
        assert tv.conflicting_goals == []
        assert tv.predicted_effectiveness == 0.0
        assert tv.potential_benefits == []
        assert tv.potential_risks == []
        assert tv.modifications_suggested == []
        assert tv.alternative_approaches == []
        assert tv.follow_up_required is False
        assert tv.is_approved is False
        assert tv.approval_conditions == []


class TestContentValidation:
    def test_required_fields(self):
        cv = ContentValidation(
            content_id="c1",
            content_type="scene",
            content_text="Some narrative text",
        )
        assert cv.content_id == "c1"
        assert cv.content_type == "scene"
        assert cv.content_text == "Some narrative text"

    def test_defaults(self):
        cv = ContentValidation(
            content_id="c1", content_type="scene", content_text="T"
        )
        assert cv.contains_triggers is False
        assert cv.trigger_types == []
        assert cv.safety_rating == SafetyLevel.SAFE
        assert cv.narrative_quality == 0.0
        assert cv.therapeutic_value == 0.0
        assert cv.age_appropriate is True
        assert cv.language_appropriate is True
        assert cv.tone_assessment == "neutral"
        assert cv.complexity_level == DifficultyLevel.STANDARD
        assert cv.bias_detected is False
        assert cv.bias_types == []
        assert cv.cultural_sensitivity == 1.0
        assert cv.is_approved is False
        assert cv.requires_modification is False
        assert cv.modification_suggestions == []
        assert cv.validation_version == "1.0.0"

    def test_missing_required_raises(self):
        with pytest.raises(ValidationError):
            ContentValidation(content_id="c1", content_type="scene")  # missing content_text
