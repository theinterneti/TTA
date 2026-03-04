"""
Unit tests for OutcomeGenerator in consequence_system/outcome_generator.py.

Tests initialization, placeholder substitution, outcome generation for all
choice types, and fallback behaviour.
"""

from __future__ import annotations

import re

import pytest

from src.components.gameplay_loop.consequence_system.outcome_generator import (
    OutcomeGenerator,
)
from src.components.gameplay_loop.models.core import (
    ChoiceType,
    DifficultyLevel,
    EmotionalState,
    Scene,
    SceneType,
    SessionState,
    TherapeuticContext,
)
from src.components.gameplay_loop.models.interactions import UserChoice

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PLACEHOLDER_RE = re.compile(r"\{[a-z_]+\}")


def _has_unfilled_placeholder(text: str) -> bool:
    """Return True if text still contains a raw {placeholder}."""
    return bool(_PLACEHOLDER_RE.search(text))


def _make_scene(
    scene_type: SceneType = SceneType.THERAPEUTIC,
    therapeutic_focus: list[str] | None = None,
) -> Scene:
    return Scene(
        title="Test Scene",
        description="A healing space opens before you.",
        narrative_content="The air is calm...",
        scene_type=scene_type,
        therapeutic_focus=therapeutic_focus or ["mindfulness"],
    )


def _make_session(
    emotional_state: EmotionalState = EmotionalState.CALM,
) -> SessionState:
    ss = SessionState(user_id="user-test")
    ss.emotional_state = emotional_state
    ss.therapeutic_context = TherapeuticContext()
    return ss


def _make_user_choice(
    choice_type: ChoiceType = ChoiceType.THERAPEUTIC,
    therapeutic_tags: list[str] | None = None,
    therapeutic_value: float = 0.8,
    choice_text: str = "Take a mindful breath and center yourself",
) -> UserChoice:
    return UserChoice(
        choice_id="uc-test",
        session_id="s-test",
        scene_id="sc-test",
        choice_text=choice_text,
        choice_type=choice_type,
        therapeutic_value=therapeutic_value,
        therapeutic_tags=therapeutic_tags or ["mindfulness", "grounding"],
        agency_level=0.7,
        emotional_state_before=EmotionalState.CALM,
    )


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def gen() -> OutcomeGenerator:
    """Initialized OutcomeGenerator, no external services."""
    og = OutcomeGenerator()
    await og.initialize()
    return og


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestOutcomeGeneratorInit:
    async def test_initialize_returns_true(self):
        og = OutcomeGenerator()
        assert await og.initialize() is True

    async def test_templates_populated_for_all_types(self, gen: OutcomeGenerator):
        for choice_type in ChoiceType:
            assert choice_type in gen.outcome_templates

    async def test_emotional_mappings_populated(self, gen: OutcomeGenerator):
        for state in EmotionalState:
            assert state in gen.emotional_outcome_mappings

    async def test_causality_patterns_populated(self, gen: OutcomeGenerator):
        assert len(gen.causality_patterns) > 0


# ---------------------------------------------------------------------------
# _build_substitutions
# ---------------------------------------------------------------------------


class TestBuildSubstitutions:
    async def test_returns_dict(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session()
        subs = gen._build_substitutions(uc, scene, session)
        assert isinstance(subs, dict)

    async def test_action_matches_choice_text_lower(self, gen: OutcomeGenerator):
        uc = _make_user_choice(choice_text="Breathe Deeply")
        scene = _make_scene()
        session = _make_session()
        subs = gen._build_substitutions(uc, scene, session)
        assert subs["action"] == "breathe deeply"

    async def test_emotion_matches_session_state(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session(EmotionalState.ANXIOUS)
        subs = gen._build_substitutions(uc, scene, session)
        assert subs["emotion"] == "anxious"
        assert subs["emotional_response"] == "anxious"

    async def test_technique_from_first_tag(self, gen: OutcomeGenerator):
        uc = _make_user_choice(therapeutic_tags=["self_compassion", "grounding"])
        scene = _make_scene()
        session = _make_session()
        subs = gen._build_substitutions(uc, scene, session)
        assert subs["therapeutic_technique"] == "self compassion"

    async def test_technique_fallback_when_no_tags(self, gen: OutcomeGenerator):
        # Construct UserChoice directly so therapeutic_tags is unambiguously []
        uc = UserChoice(
            choice_id="uc-empty",
            session_id="s-test",
            scene_id="sc-test",
            choice_text="test choice",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_value=0.8,
            therapeutic_tags=[],
            agency_level=0.7,
            emotional_state_before=EmotionalState.CALM,
        )
        scene = _make_scene()
        session = _make_session()
        subs = gen._build_substitutions(uc, scene, session)
        assert subs["therapeutic_technique"] == "this practice"

    async def test_skill_from_second_tag(self, gen: OutcomeGenerator):
        uc = _make_user_choice(therapeutic_tags=["mindfulness", "emotional_regulation"])
        scene = _make_scene()
        session = _make_session()
        subs = gen._build_substitutions(uc, scene, session)
        assert subs["skill_area"] == "emotional regulation"

    async def test_all_required_keys_present(self, gen: OutcomeGenerator):
        """Every placeholder used in templates must be in the substitutions dict."""
        required = {
            "emotional_response", "action", "therapeutic_technique",
            "immediate_benefit", "awareness_insight", "skill_area",
            "technique", "therapeutic_goal",
            "new_location", "interesting_element", "significance",
            "path_description", "future_opportunity", "future_challenge",
            "time_frame", "skill_name", "situation", "difficulty_level",
            "encouraging_aspect", "regulation_action", "emotion",
            "change_direction", "positive_emotion", "interaction_style",
            "social_outcome", "response_type", "social_emotion",
            "relationship_aspect", "positive_element", "interaction_learning",
        }
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session()
        subs = gen._build_substitutions(uc, scene, session)
        missing = required - set(subs.keys())
        assert not missing, f"Missing substitution keys: {missing}"


# ---------------------------------------------------------------------------
# _generate_immediate_outcomes — placeholder regression
# ---------------------------------------------------------------------------


class TestGenerateImmediateOutcomes:
    async def test_returns_list(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session()
        result = await gen._generate_immediate_outcomes(uc, scene, session)
        assert isinstance(result, list)

    async def test_returns_nonempty_list(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session()
        result = await gen._generate_immediate_outcomes(uc, scene, session)
        assert len(result) > 0

    async def test_no_unfilled_placeholders_therapeutic(
        self, gen: OutcomeGenerator
    ):
        uc = _make_user_choice(choice_type=ChoiceType.THERAPEUTIC)
        scene = _make_scene()
        session = _make_session()
        outcomes = await gen._generate_immediate_outcomes(uc, scene, session)
        for text in outcomes:
            assert not _has_unfilled_placeholder(text), (
                f"Unfilled placeholder in: {text!r}"
            )

    async def test_no_unfilled_placeholders_narrative(
        self, gen: OutcomeGenerator
    ):
        uc = _make_user_choice(choice_type=ChoiceType.NARRATIVE)
        scene = _make_scene(scene_type=SceneType.EXPLORATION)
        session = _make_session()
        outcomes = await gen._generate_immediate_outcomes(uc, scene, session)
        for text in outcomes:
            assert not _has_unfilled_placeholder(text), (
                f"Unfilled placeholder in: {text!r}"
            )

    async def test_no_unfilled_placeholders_skill_building(
        self, gen: OutcomeGenerator
    ):
        uc = _make_user_choice(
            choice_type=ChoiceType.SKILL_BUILDING,
            therapeutic_tags=["coping_skills"],
        )
        scene = _make_scene()
        session = _make_session()
        outcomes = await gen._generate_immediate_outcomes(uc, scene, session)
        for text in outcomes:
            assert not _has_unfilled_placeholder(text), (
                f"Unfilled placeholder in: {text!r}"
            )

    async def test_no_unfilled_placeholders_emotional_regulation(
        self, gen: OutcomeGenerator
    ):
        uc = _make_user_choice(choice_type=ChoiceType.EMOTIONAL_REGULATION)
        scene = _make_scene()
        session = _make_session(EmotionalState.ANXIOUS)
        outcomes = await gen._generate_immediate_outcomes(uc, scene, session)
        for text in outcomes:
            assert not _has_unfilled_placeholder(text), (
                f"Unfilled placeholder in: {text!r}"
            )

    async def test_no_unfilled_placeholders_social_interaction(
        self, gen: OutcomeGenerator
    ):
        uc = _make_user_choice(choice_type=ChoiceType.SOCIAL_INTERACTION)
        scene = _make_scene()
        session = _make_session()
        outcomes = await gen._generate_immediate_outcomes(uc, scene, session)
        for text in outcomes:
            assert not _has_unfilled_placeholder(text), (
                f"Unfilled placeholder in: {text!r}"
            )

    async def test_fallback_for_unknown_type(self, gen: OutcomeGenerator):
        """If templates don't exist for a type, fallback string is returned."""
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session()
        # Temporarily empty templates
        original = gen.outcome_templates.copy()
        gen.outcome_templates = {}
        outcomes = await gen._generate_immediate_outcomes(uc, scene, session)
        gen.outcome_templates = original
        assert len(outcomes) == 1
        assert not _has_unfilled_placeholder(outcomes[0])


# ---------------------------------------------------------------------------
# _generate_delayed_outcomes
# ---------------------------------------------------------------------------


class TestGenerateDelayedOutcomes:
    async def test_returns_list(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session()
        result = await gen._generate_delayed_outcomes(uc, scene, session)
        assert isinstance(result, list)

    async def test_no_unfilled_placeholders(self, gen: OutcomeGenerator):
        for choice_type in ChoiceType:
            uc = _make_user_choice(choice_type=choice_type)
            scene = _make_scene()
            session = _make_session()
            outcomes = await gen._generate_delayed_outcomes(uc, scene, session)
            for text in outcomes:
                assert not _has_unfilled_placeholder(text), (
                    f"Unfilled placeholder in delayed outcome ({choice_type}): {text!r}"
                )

    async def test_returns_at_most_one_item(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session()
        result = await gen._generate_delayed_outcomes(uc, scene, session)
        assert len(result) <= 1


# ---------------------------------------------------------------------------
# generate_outcomes — full pipeline
# ---------------------------------------------------------------------------


class TestGenerateOutcomes:
    async def test_returns_all_expected_keys(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session()
        outcomes = await gen.generate_outcomes(uc, scene, session)
        assert "immediate" in outcomes
        assert "delayed" in outcomes
        assert "emotional_impact" in outcomes
        assert "narrative" in outcomes
        assert "character_development" in outcomes
        assert "world_state_changes" in outcomes

    async def test_immediate_is_list(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        outcomes = await gen.generate_outcomes(uc, _make_scene(), _make_session())
        assert isinstance(outcomes["immediate"], list)

    async def test_no_placeholders_in_full_pipeline(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        outcomes = await gen.generate_outcomes(uc, _make_scene(), _make_session())
        for text in outcomes["immediate"] + outcomes["delayed"] + outcomes["narrative"]:
            assert not _has_unfilled_placeholder(text), (
                f"Unfilled placeholder leaked into output: {text!r}"
            )

    async def test_emotional_impact_has_primary_emotion(
        self, gen: OutcomeGenerator
    ):
        uc = _make_user_choice()
        outcomes = await gen.generate_outcomes(uc, _make_scene(), _make_session())
        assert "primary_emotion" in outcomes["emotional_impact"]

    async def test_high_therapeutic_value_generates_character_development(
        self, gen: OutcomeGenerator
    ):
        uc = _make_user_choice(therapeutic_value=0.9)
        outcomes = await gen.generate_outcomes(uc, _make_scene(), _make_session())
        assert outcomes["character_development"].get("resilience", 0) > 0

    async def test_low_therapeutic_value_no_character_development(
        self, gen: OutcomeGenerator
    ):
        uc = _make_user_choice(therapeutic_value=0.3)
        outcomes = await gen.generate_outcomes(uc, _make_scene(), _make_session())
        assert outcomes["character_development"] == {}

    async def test_works_for_all_choice_types(self, gen: OutcomeGenerator):
        scene = _make_scene()
        session = _make_session()
        for choice_type in ChoiceType:
            uc = _make_user_choice(choice_type=choice_type)
            outcomes = await gen.generate_outcomes(uc, scene, session)
            assert "immediate" in outcomes


# ---------------------------------------------------------------------------
# _generate_emotional_impact
# ---------------------------------------------------------------------------


class TestGenerateEmotionalImpact:
    async def test_returns_dict(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        result = await gen._generate_emotional_impact(
            uc, _make_scene(), _make_session()
        )
        assert isinstance(result, dict)

    async def test_intensity_matches_therapeutic_value(self, gen: OutcomeGenerator):
        uc = _make_user_choice(therapeutic_value=0.75)
        result = await gen._generate_emotional_impact(
            uc, _make_scene(), _make_session()
        )
        assert result["intensity"] == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# Fallback outcomes
# ---------------------------------------------------------------------------


class TestFallbackOutcomes:
    async def test_fallback_has_all_keys(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        result = await gen._generate_fallback_outcomes(uc)
        assert "immediate" in result
        assert "delayed" in result
        assert "emotional_impact" in result
        assert "narrative" in result
        assert "character_development" in result
        assert "world_state_changes" in result

    async def test_fallback_immediate_is_nonempty(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        result = await gen._generate_fallback_outcomes(uc)
        assert len(result["immediate"]) > 0

    async def test_fallback_no_placeholders(self, gen: OutcomeGenerator):
        uc = _make_user_choice()
        result = await gen._generate_fallback_outcomes(uc)
        for text in result["immediate"] + result["narrative"]:
            assert not _has_unfilled_placeholder(text)
