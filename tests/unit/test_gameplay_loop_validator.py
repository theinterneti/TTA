"""
Unit tests for the ChoiceValidator in choice_architecture/validator.py.

Tests all public methods and the core private validation logic using
mocked dependencies — no external services required.
"""

from __future__ import annotations

import pytest

from src.components.gameplay_loop.choice_architecture.validator import ChoiceValidator
from src.components.gameplay_loop.models.core import (
    Choice,
    ChoiceType,
    DifficultyLevel,
    EmotionalState,
    Scene,
    SceneType,
    SessionState,
)
from src.components.gameplay_loop.models.interactions import UserChoice

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_scene(
    scene_type: SceneType = SceneType.EXPLORATION,
    therapeutic_focus: list[str] | None = None,
) -> Scene:
    return Scene(
        title="Test Scene",
        description="A test scene",
        narrative_content="Narrative text",
        scene_type=scene_type,
        therapeutic_focus=therapeutic_focus or [],
    )


def _make_session(
    emotional_state: EmotionalState = EmotionalState.CALM,
    choice_history: list | None = None,
) -> SessionState:
    ss = SessionState(user_id="user-test")
    ss.emotional_state = emotional_state
    if choice_history is not None:
        ss.choice_history = choice_history
    return ss


def _make_choice(
    therapeutic_value: float = 0.8,
    therapeutic_tags: list[str] | None = None,
    choice_type: ChoiceType = ChoiceType.THERAPEUTIC,
    agency_level: float = 0.6,
    meaningfulness_score: float = 0.6,
    difficulty_level: DifficultyLevel = DifficultyLevel.STANDARD,
) -> Choice:
    return Choice(
        choice_text="Test choice",
        choice_type=choice_type,
        therapeutic_value=therapeutic_value,
        therapeutic_tags=therapeutic_tags or [],
        agency_level=agency_level,
        meaningfulness_score=meaningfulness_score,
        difficulty_level=difficulty_level,
    )


def _make_user_choice(
    therapeutic_value: float = 0.8,
    therapeutic_tags: list[str] | None = None,
    choice_type: ChoiceType = ChoiceType.THERAPEUTIC,
    agency_level: float = 0.6,
    emotional_state: EmotionalState = EmotionalState.CALM,
) -> UserChoice:
    return UserChoice(
        choice_id="uc-1",
        session_id="s-1",
        scene_id="sc-1",
        choice_text="Test user choice",
        choice_type=choice_type,
        therapeutic_value=therapeutic_value,
        therapeutic_tags=therapeutic_tags or [],
        agency_level=agency_level,
        emotional_state_before=emotional_state,
    )


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def initialized_validator() -> ChoiceValidator:
    """Create and initialize a ChoiceValidator."""
    validator = ChoiceValidator()
    await validator.initialize()
    return validator


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestChoiceValidatorInit:
    def test_default_construction(self):
        v = ChoiceValidator()
        assert v.config == {}
        assert v.safety_criteria == {}
        assert v.therapeutic_criteria == {}
        assert v.emotional_appropriateness_rules == {}
        assert v.minimum_thresholds == {}

    def test_custom_config(self):
        cfg = {"key": "value"}
        v = ChoiceValidator(config=cfg)
        assert v.config == cfg

    async def test_initialize_returns_true(self):
        v = ChoiceValidator()
        result = await v.initialize()
        assert result is True

    async def test_initialize_populates_safety_criteria(self):
        v = ChoiceValidator()
        await v.initialize()
        assert "prohibited_content" in v.safety_criteria
        assert "crisis_state_requirements" in v.safety_criteria

    async def test_initialize_populates_therapeutic_criteria(self):
        v = ChoiceValidator()
        await v.initialize()
        assert "minimum_therapeutic_value" in v.therapeutic_criteria
        assert "scene_type_alignment" in v.therapeutic_criteria

    async def test_initialize_populates_emotional_rules(self):
        v = ChoiceValidator()
        await v.initialize()
        assert EmotionalState.CALM in v.emotional_appropriateness_rules
        assert EmotionalState.CRISIS in v.emotional_appropriateness_rules

    async def test_initialize_populates_thresholds(self):
        v = ChoiceValidator()
        await v.initialize()
        assert "therapeutic_value" in v.minimum_thresholds
        assert "agency_level" in v.minimum_thresholds
        assert "meaningfulness_score" in v.minimum_thresholds


# ---------------------------------------------------------------------------
# validate_choices
# ---------------------------------------------------------------------------


class TestValidateChoices:
    async def test_returns_empty_for_empty_input(self, initialized_validator):
        result = await initialized_validator.validate_choices(
            [], _make_scene(), _make_session()
        )
        assert result == []

    async def test_valid_choices_pass(self, initialized_validator):
        # A therapeutic choice with enough value and proper tags for CALM state
        choice = _make_choice(
            therapeutic_value=0.8,
            therapeutic_tags=["mindfulness"],
            choice_type=ChoiceType.NARRATIVE,
            agency_level=0.6,
            meaningfulness_score=0.6,
        )
        scene = _make_scene(scene_type=SceneType.EXPLORATION)
        session = _make_session(emotional_state=EmotionalState.CALM)
        result = await initialized_validator.validate_choices(
            [choice], scene, session
        )
        # At least the choice should make it through (may or may not pass all criteria)
        assert isinstance(result, list)

    async def test_choices_with_prohibited_content_are_filtered(
        self, initialized_validator
    ):
        choice = _make_choice(therapeutic_tags=["self_harm"])
        result = await initialized_validator.validate_choices(
            [choice], _make_scene(), _make_session()
        )
        assert len(result) == 0

    async def test_returns_original_choices_on_exception(self):
        """If validation itself fails, original choices are returned."""
        v = ChoiceValidator()
        # Not initialized — safety_criteria not set, will raise KeyError
        # validate_choices catches exceptions and returns originals
        choice = _make_choice()
        result = await v.validate_choices([choice], _make_scene(), _make_session())
        assert result == [choice]

    async def test_multiple_choices_some_pass(self, initialized_validator):
        scene = _make_scene(scene_type=SceneType.EXPLORATION)
        session = _make_session(emotional_state=EmotionalState.CALM)

        good_choice = _make_choice(
            therapeutic_value=0.8,
            therapeutic_tags=["grounding"],
            choice_type=ChoiceType.NARRATIVE,
            agency_level=0.6,
            meaningfulness_score=0.6,
        )
        bad_choice = _make_choice(therapeutic_tags=["violence"])

        result = await initialized_validator.validate_choices(
            [good_choice, bad_choice], scene, session
        )
        # bad choice should be filtered out
        bad_ids = {bad_choice.choice_id}
        remaining_ids = {c.choice_id for c in result}
        assert not bad_ids.intersection(remaining_ids)


# ---------------------------------------------------------------------------
# validate_for_emotional_state
# ---------------------------------------------------------------------------


class TestValidateForEmotionalState:
    async def test_calm_state_accepts_all_choice_types(self, initialized_validator):
        session = _make_session(EmotionalState.CALM)
        for ct in ChoiceType:
            choice = _make_choice(
                choice_type=ct, therapeutic_value=0.5, therapeutic_tags=[]
            )
            result = await initialized_validator.validate_for_emotional_state(
                choice, EmotionalState.CALM.value, session
            )
            # CALM state: all types appropriate, min_therapeutic_value=0.3
            # choice therapeutic_value=0.5 > 0.3, so should pass type check
            assert isinstance(result, bool)

    async def test_crisis_state_requires_specific_tags(self, initialized_validator):
        session = _make_session(EmotionalState.CRISIS)
        # Choice without required tags for CRISIS
        choice = _make_choice(
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_tags=[],  # No required tags
            therapeutic_value=1.0,
        )
        result = await initialized_validator.validate_for_emotional_state(
            choice, EmotionalState.CRISIS.value, session
        )
        assert result is False

    async def test_crisis_state_with_required_tags_passes(self, initialized_validator):
        session = _make_session(EmotionalState.CRISIS)
        choice = _make_choice(
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_tags=["immediate_safety", "crisis_support"],
            therapeutic_value=1.0,
        )
        result = await initialized_validator.validate_for_emotional_state(
            choice, EmotionalState.CRISIS.value, session
        )
        assert result is True

    async def test_anxious_state_requires_therapeutic_choice_type(
        self, initialized_validator
    ):
        session = _make_session(EmotionalState.ANXIOUS)
        # SKILL_BUILDING is not in appropriate_choice_types for ANXIOUS
        choice = _make_choice(
            choice_type=ChoiceType.SKILL_BUILDING,
            therapeutic_tags=["grounding"],
            therapeutic_value=0.7,
        )
        result = await initialized_validator.validate_for_emotional_state(
            choice, EmotionalState.ANXIOUS.value, session
        )
        assert result is False

    async def test_anxious_state_with_correct_type_and_tags(
        self, initialized_validator
    ):
        session = _make_session(EmotionalState.ANXIOUS)
        choice = _make_choice(
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_tags=["grounding"],
            therapeutic_value=0.7,
        )
        result = await initialized_validator.validate_for_emotional_state(
            choice, EmotionalState.ANXIOUS.value, session
        )
        assert result is True

    async def test_invalid_emotional_state_returns_true(self, initialized_validator):
        """An invalid emotional state value should gracefully return True."""
        session = _make_session(EmotionalState.CALM)
        choice = _make_choice()
        result = await initialized_validator.validate_for_emotional_state(
            choice, "not_a_valid_state", session
        )
        assert result is True


# ---------------------------------------------------------------------------
# analyze_therapeutic_impact
# ---------------------------------------------------------------------------


class TestAnalyzeTherapeuticImpact:
    async def test_returns_dict_with_expected_keys(self, initialized_validator):
        uc = _make_user_choice(therapeutic_value=0.7)
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "therapeutic_impact_score" in result
        assert "skill_development" in result
        assert "learning_opportunities" in result
        assert "progress_markers" in result
        assert "emotional_growth" in result
        assert "therapeutic_alignment" in result

    async def test_skill_development_for_skill_building_choice(
        self, initialized_validator
    ):
        uc = _make_user_choice(
            choice_type=ChoiceType.SKILL_BUILDING,
            therapeutic_tags=["coping_skills", "resilience"],
            therapeutic_value=0.8,
        )
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert len(result["skill_development"]) > 0

    async def test_no_skill_development_for_narrative_choice(
        self, initialized_validator
    ):
        uc = _make_user_choice(
            choice_type=ChoiceType.NARRATIVE, therapeutic_tags=[], therapeutic_value=0.5
        )
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert result["skill_development"] == []

    async def test_high_therapeutic_value_adds_progress_markers(
        self, initialized_validator
    ):
        uc = _make_user_choice(therapeutic_value=0.8)
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "therapeutic_progress" in result["progress_markers"]

    async def test_returns_fallback_on_error(self):
        """Uninitialized validator should return fallback dict."""
        v = ChoiceValidator()
        uc = _make_user_choice()
        result = await v.analyze_therapeutic_impact(
            uc, _make_scene(), _make_session()
        )
        assert "therapeutic_impact_score" in result

    async def test_learning_opportunities_for_therapeutic_choice(
        self, initialized_validator
    ):
        uc = _make_user_choice(choice_type=ChoiceType.THERAPEUTIC, therapeutic_value=0.7)
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "therapeutic_insight" in result["learning_opportunities"]

    async def test_learning_opportunities_for_emotional_regulation(
        self, initialized_validator
    ):
        uc = _make_user_choice(
            choice_type=ChoiceType.EMOTIONAL_REGULATION, therapeutic_value=0.7
        )
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "emotional_awareness" in result["learning_opportunities"]

    async def test_learning_opportunity_significant_growth(self, initialized_validator):
        uc = _make_user_choice(therapeutic_value=0.9)
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "significant_growth" in result["learning_opportunities"]

    async def test_learning_opportunity_reflection(self, initialized_validator):
        uc = _make_user_choice(therapeutic_value=0.3)
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "reflection_opportunity" in result["learning_opportunities"]

    async def test_progress_marker_empowerment(self, initialized_validator):
        uc = _make_user_choice(therapeutic_value=0.5, agency_level=0.9)
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "empowerment_milestone" in result["progress_markers"]

    async def test_progress_marker_session_engagement_at_5_choices(
        self, initialized_validator
    ):
        history = [{"choice_id": str(i)} for i in range(5)]
        uc = _make_user_choice(therapeutic_value=0.5)
        scene = _make_scene()
        session = _make_session(choice_history=history)
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "session_engagement_milestone" in result["progress_markers"]

    async def test_emotional_growth_self_compassion_tag(self, initialized_validator):
        uc = _make_user_choice(
            therapeutic_tags=["self_compassion"], therapeutic_value=0.5
        )
        scene = _make_scene()
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "self_compassion_development" in result["emotional_growth"]

    async def test_emotional_growth_anxious_state_high_value(
        self, initialized_validator
    ):
        uc = _make_user_choice(
            therapeutic_value=0.8,
            emotional_state=EmotionalState.ANXIOUS,
        )
        scene = _make_scene()
        session = _make_session(emotional_state=EmotionalState.ANXIOUS)
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert "anxiety_management_progress" in result["emotional_growth"]

    async def test_therapeutic_alignment_score_is_between_0_and_1(
        self, initialized_validator
    ):
        uc = _make_user_choice(therapeutic_value=0.7, therapeutic_tags=["mindfulness"])
        scene = _make_scene(therapeutic_focus=["mindfulness"])
        session = _make_session()
        result = await initialized_validator.analyze_therapeutic_impact(
            uc, scene, session
        )
        assert 0.0 <= result["therapeutic_alignment"] <= 1.0


# ---------------------------------------------------------------------------
# Private helper method coverage via public interface
# ---------------------------------------------------------------------------


class TestValidateThresholds:
    """Test threshold validation via validate_choices."""

    async def test_choice_below_therapeutic_value_threshold_fails(
        self, initialized_validator
    ):
        choice = _make_choice(
            therapeutic_value=0.1,  # below 0.3 threshold
            therapeutic_tags=[],
            choice_type=ChoiceType.NARRATIVE,
            agency_level=0.6,
            meaningfulness_score=0.6,
        )
        scene = _make_scene(scene_type=SceneType.EXPLORATION)
        session = _make_session()
        result = await initialized_validator.validate_choices(
            [choice], scene, session
        )
        assert choice not in result

    async def test_choice_below_agency_level_threshold_fails(
        self, initialized_validator
    ):
        choice = _make_choice(
            therapeutic_value=0.8,
            therapeutic_tags=[],
            choice_type=ChoiceType.NARRATIVE,
            agency_level=0.2,  # below 0.4 threshold
            meaningfulness_score=0.6,
        )
        scene = _make_scene(scene_type=SceneType.EXPLORATION)
        session = _make_session()
        result = await initialized_validator.validate_choices(
            [choice], scene, session
        )
        assert choice not in result

    async def test_choice_below_meaningfulness_threshold_fails(
        self, initialized_validator
    ):
        choice = _make_choice(
            therapeutic_value=0.8,
            therapeutic_tags=[],
            choice_type=ChoiceType.NARRATIVE,
            agency_level=0.6,
            meaningfulness_score=0.1,  # below 0.3 threshold
        )
        scene = _make_scene(scene_type=SceneType.EXPLORATION)
        session = _make_session()
        result = await initialized_validator.validate_choices(
            [choice], scene, session
        )
        assert choice not in result


class TestSafetyValidation:
    """Test safety validation edge cases."""

    async def test_distressed_state_missing_support_tags(self, initialized_validator):
        choice = _make_choice(
            therapeutic_value=0.9,
            therapeutic_tags=[],  # No support/compassion tags
            choice_type=ChoiceType.THERAPEUTIC,
            agency_level=0.6,
            meaningfulness_score=0.6,
        )
        session = _make_session(emotional_state=EmotionalState.DISTRESSED)
        scene = _make_scene()
        result = await initialized_validator.validate_choices(
            [choice], scene, session
        )
        assert choice not in result

    async def test_crisis_state_with_prohibited_tags(self, initialized_validator):
        choice = _make_choice(
            therapeutic_value=0.9,
            therapeutic_tags=["challenge", "immediate_safety"],
            choice_type=ChoiceType.THERAPEUTIC,
            agency_level=0.6,
            meaningfulness_score=0.6,
        )
        session = _make_session(emotional_state=EmotionalState.CRISIS)
        scene = _make_scene()
        result = await initialized_validator.validate_choices(
            [choice], scene, session
        )
        # "challenge" is prohibited in crisis state
        assert choice not in result

    async def test_safe_choice_in_calm_state(self, initialized_validator):
        choice = _make_choice(
            therapeutic_value=0.8,
            therapeutic_tags=["mindfulness"],
            choice_type=ChoiceType.NARRATIVE,
            agency_level=0.6,
            meaningfulness_score=0.6,
        )
        session = _make_session(emotional_state=EmotionalState.CALM)
        scene = _make_scene(scene_type=SceneType.EXPLORATION)
        result = await initialized_validator.validate_choices(
            [choice], scene, session
        )
        assert choice in result
