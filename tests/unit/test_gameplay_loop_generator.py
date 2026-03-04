"""
Unit tests for ChoiceGenerator in choice_architecture/generator.py.

Tests initialization, choice generation, template rotation, and the
slot_index mechanism that prevents identical choices.
"""

from __future__ import annotations

import pytest

from src.components.gameplay_loop.choice_architecture.generator import (
    ChoiceGenerator,
    ChoiceTemplate,
)
from src.components.gameplay_loop.models.core import (
    Choice,
    ChoiceType,
    DifficultyLevel,
    EmotionalState,
    Scene,
    SceneType,
    SessionState,
    TherapeuticContext,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_scene(
    scene_type: SceneType = SceneType.EXPLORATION,
    therapeutic_focus: list[str] | None = None,
    difficulty_level: DifficultyLevel = DifficultyLevel.STANDARD,
) -> Scene:
    return Scene(
        title="Test Scene",
        description="A peaceful clearing where healing begins.",
        narrative_content="You stand at the edge of a forest...",
        scene_type=scene_type,
        therapeutic_focus=therapeutic_focus or [],
        difficulty_level=difficulty_level,
    )


def _make_session(
    emotional_state: EmotionalState = EmotionalState.CALM,
) -> SessionState:
    ss = SessionState(user_id="user-test")
    ss.emotional_state = emotional_state
    ss.therapeutic_context = TherapeuticContext()
    return ss


def _base_requirements(
    choice_types: list[ChoiceType] | None = None,
    max_choices: int = 3,
) -> dict:
    return {
        "choice_types_needed": choice_types or [],
        "max_choices": max_choices,
        "therapeutic_choice_ratio": 0.6,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def generator() -> ChoiceGenerator:
    """Initialized ChoiceGenerator, no external services needed."""
    gen = ChoiceGenerator()
    await gen.initialize()
    return gen


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestChoiceGeneratorInit:
    async def test_initialize_returns_true(self):
        gen = ChoiceGenerator()
        result = await gen.initialize()
        assert result is True

    async def test_templates_populated_after_init(self, generator: ChoiceGenerator):
        assert len(generator.choice_templates) > 0
        assert ChoiceType.THERAPEUTIC in generator.choice_templates
        assert ChoiceType.NARRATIVE in generator.choice_templates

    async def test_emotional_adaptations_populated(self, generator: ChoiceGenerator):
        assert EmotionalState.CALM in generator.emotional_adaptations
        assert EmotionalState.CRISIS in generator.emotional_adaptations

    async def test_double_initialize_still_returns_true(self):
        gen = ChoiceGenerator()
        await gen.initialize()
        result = await gen.initialize()
        assert result is True


# ---------------------------------------------------------------------------
# generate_choices — count and types
# ---------------------------------------------------------------------------


class TestGenerateChoices:
    async def test_returns_up_to_max_choices(
        self, generator: ChoiceGenerator
    ):
        scene = _make_scene()
        session = _make_session()
        reqs = _base_requirements(max_choices=3)
        choices = await generator.generate_choices(scene, session, reqs)
        assert len(choices) <= 3

    async def test_fills_max_choices_slots(self, generator: ChoiceGenerator):
        scene = _make_scene()
        session = _make_session()
        reqs = _base_requirements(max_choices=3)
        choices = await generator.generate_choices(scene, session, reqs)
        assert len(choices) == 3

    async def test_returns_choice_objects(self, generator: ChoiceGenerator):
        scene = _make_scene()
        session = _make_session()
        choices = await generator.generate_choices(scene, session, _base_requirements())
        for c in choices:
            assert isinstance(c, Choice)

    async def test_choices_have_unique_ids(self, generator: ChoiceGenerator):
        scene = _make_scene()
        session = _make_session()
        choices = await generator.generate_choices(scene, session, _base_requirements())
        ids = [c.choice_id for c in choices]
        assert len(ids) == len(set(ids)), "All choice IDs must be unique"

    async def test_requested_types_included(self, generator: ChoiceGenerator):
        scene = _make_scene()
        session = _make_session()
        reqs = _base_requirements(
            choice_types=[ChoiceType.NARRATIVE, ChoiceType.THERAPEUTIC],
            max_choices=4,
        )
        choices = await generator.generate_choices(scene, session, reqs)
        types = [c.choice_type for c in choices]
        assert ChoiceType.NARRATIVE in types
        assert ChoiceType.THERAPEUTIC in types

    async def test_empty_requirements_still_fills_choices(
        self, generator: ChoiceGenerator
    ):
        scene = _make_scene()
        session = _make_session()
        reqs = _base_requirements(choice_types=[], max_choices=2)
        choices = await generator.generate_choices(scene, session, reqs)
        assert len(choices) == 2


# ---------------------------------------------------------------------------
# Distinct choices — the slot_index fix
# ---------------------------------------------------------------------------


class TestDistinctChoices:
    """Regression tests for the repetitive-choices bug (slot_index fix)."""

    async def test_three_choices_have_distinct_texts(
        self, generator: ChoiceGenerator
    ):
        scene = _make_scene()
        session = _make_session()
        reqs = _base_requirements(max_choices=3)
        choices = await generator.generate_choices(scene, session, reqs)
        texts = [c.choice_text for c in choices]
        assert len(texts) == len(set(texts)), (
            f"Choices must have distinct text, got: {texts}"
        )

    async def test_four_choices_have_distinct_texts(
        self, generator: ChoiceGenerator
    ):
        scene = _make_scene()
        session = _make_session()
        reqs = _base_requirements(max_choices=4)
        choices = await generator.generate_choices(scene, session, reqs)
        texts = [c.choice_text for c in choices]
        assert len(texts) == len(set(texts)), (
            f"All 4 choices must have distinct text, got: {texts}"
        )

    async def test_all_therapeutic_choices_differ(
        self, generator: ChoiceGenerator
    ):
        """Specifically test the case that caused the original bug."""
        scene = _make_scene()
        session = _make_session()
        # Ask for 3 therapeutic choices — the original bug returned the same
        # "Practice mindful awareness" text for all 3.
        reqs = {
            "choice_types_needed": [
                ChoiceType.THERAPEUTIC,
                ChoiceType.THERAPEUTIC,
                ChoiceType.THERAPEUTIC,
            ],
            "max_choices": 3,
            "therapeutic_choice_ratio": 1.0,
        }
        choices = await generator.generate_choices(scene, session, reqs)
        texts = [c.choice_text for c in choices]
        assert len(texts) == len(set(texts)), (
            f"Therapeutic choices must differ, got: {texts}"
        )


# ---------------------------------------------------------------------------
# _select_template — rotation
# ---------------------------------------------------------------------------


class TestSelectTemplate:
    async def test_returns_a_template(self, generator: ChoiceGenerator):
        templates = generator.choice_templates[ChoiceType.THERAPEUTIC]
        scene = _make_scene()
        session = _make_session()
        result = await generator._select_template(templates, scene, session, 0)
        assert isinstance(result, ChoiceTemplate)

    async def test_slot0_and_slot1_differ_when_multiple_templates(
        self, generator: ChoiceGenerator
    ):
        templates = generator.choice_templates[ChoiceType.THERAPEUTIC]
        if len(templates) < 2:
            pytest.skip("Need at least 2 templates for rotation test")
        scene = _make_scene()
        session = _make_session()
        t0 = await generator._select_template(templates, scene, session, 0)
        t1 = await generator._select_template(templates, scene, session, 1)
        # With 2 templates of equal score, slot 0 and 1 should return different ones
        assert t0 is not t1

    async def test_rotation_wraps_around(self, generator: ChoiceGenerator):
        templates = generator.choice_templates[ChoiceType.THERAPEUTIC]
        scene = _make_scene()
        session = _make_session()
        n = len(templates)
        t0 = await generator._select_template(templates, scene, session, 0)
        tn = await generator._select_template(templates, scene, session, n)
        # slot n should wrap back to the same template as slot 0
        assert t0 is tn

    async def test_high_score_template_wins_regardless_of_slot(
        self, generator: ChoiceGenerator
    ):
        """When one template scores higher, it's always selected."""
        templates = generator.choice_templates[ChoiceType.THERAPEUTIC]
        # Scene with mindfulness focus — the mindfulness template should win
        scene = _make_scene(therapeutic_focus=["mindfulness"])
        session = _make_session()
        t0 = await generator._select_template(templates, scene, session, 0)
        t1 = await generator._select_template(templates, scene, session, 1)
        # The highest-scoring template should always be returned
        assert t0 is t1


# ---------------------------------------------------------------------------
# _generate_from_template — text variety
# ---------------------------------------------------------------------------


class TestGenerateFromTemplate:
    async def test_uses_text_patterns(self, generator: ChoiceGenerator):
        templates = generator.choice_templates[ChoiceType.THERAPEUTIC]
        template = templates[0]
        scene = _make_scene()
        session = _make_session()
        reqs: dict = {}
        choice = await generator._generate_from_template(
            template, scene, session, reqs, slot_index=0
        )
        assert choice.choice_text in template.text_patterns or (
            choice.choice_text in template.difficulty_variants.values()
        )

    async def test_different_slots_produce_different_text(
        self, generator: ChoiceGenerator
    ):
        templates = generator.choice_templates[ChoiceType.THERAPEUTIC]
        template = templates[0]
        if len(template.text_patterns) < 2:
            pytest.skip("Template needs ≥2 patterns")
        scene = _make_scene()
        session = _make_session()
        reqs: dict = {}
        c0 = await generator._generate_from_template(
            template, scene, session, reqs, slot_index=0
        )
        c1 = await generator._generate_from_template(
            template, scene, session, reqs, slot_index=1
        )
        assert c0.choice_text != c1.choice_text

    async def test_slot_wraps_modulo_pattern_count(
        self, generator: ChoiceGenerator
    ):
        templates = generator.choice_templates[ChoiceType.THERAPEUTIC]
        template = templates[0]
        scene = _make_scene()
        session = _make_session()
        reqs: dict = {}
        n = len(template.text_patterns)
        c0 = await generator._generate_from_template(
            template, scene, session, reqs, slot_index=0
        )
        cn = await generator._generate_from_template(
            template, scene, session, reqs, slot_index=n
        )
        assert c0.choice_text == cn.choice_text

    async def test_choice_has_valid_therapeutic_value(
        self, generator: ChoiceGenerator
    ):
        templates = generator.choice_templates[ChoiceType.THERAPEUTIC]
        template = templates[0]
        scene = _make_scene()
        session = _make_session()
        choice = await generator._generate_from_template(
            template, scene, session, {}, slot_index=0
        )
        assert 0.0 <= choice.therapeutic_value <= 1.0

    async def test_choice_has_valid_agency_level(
        self, generator: ChoiceGenerator
    ):
        templates = generator.choice_templates[ChoiceType.NARRATIVE]
        template = templates[0]
        scene = _make_scene()
        session = _make_session()
        choice = await generator._generate_from_template(
            template, scene, session, {}, slot_index=0
        )
        assert 0.0 <= choice.agency_level <= 1.0


# ---------------------------------------------------------------------------
# generate_safe_choice
# ---------------------------------------------------------------------------


class TestGenerateSafeChoice:
    async def test_returns_a_choice(self, generator: ChoiceGenerator):
        session = _make_session()
        choice = await generator.generate_safe_choice("anxious", session)
        assert isinstance(choice, Choice)

    async def test_anxious_text_is_calming(self, generator: ChoiceGenerator):
        session = _make_session(EmotionalState.ANXIOUS)
        choice = await generator.generate_safe_choice("anxious", session)
        assert choice is not None
        assert "breath" in choice.choice_text.lower() or "ground" in choice.choice_text.lower()

    async def test_unknown_state_returns_generic_choice(
        self, generator: ChoiceGenerator
    ):
        session = _make_session()
        choice = await generator.generate_safe_choice("unknown_state", session)
        assert isinstance(choice, Choice)
        assert choice.choice_text  # non-empty

    async def test_safe_choice_type_is_therapeutic(self, generator: ChoiceGenerator):
        session = _make_session()
        choice = await generator.generate_safe_choice("anxious", session)
        assert choice is not None
        assert choice.choice_type == ChoiceType.THERAPEUTIC

    async def test_safe_choice_difficulty_is_gentle(self, generator: ChoiceGenerator):
        session = _make_session()
        choice = await generator.generate_safe_choice("overwhelmed", session)
        assert choice is not None
        assert choice.difficulty_level == DifficultyLevel.GENTLE


# ---------------------------------------------------------------------------
# generate_emotion_appropriate_choice
# ---------------------------------------------------------------------------


class TestGenerateEmotionAppropriateChoice:
    async def test_returns_choice_for_known_state(self, generator: ChoiceGenerator):
        session = _make_session(EmotionalState.ANXIOUS)
        choice = await generator.generate_emotion_appropriate_choice(
            ChoiceType.THERAPEUTIC, "anxious", session
        )
        assert isinstance(choice, Choice)

    async def test_returns_none_for_missing_templates(
        self, generator: ChoiceGenerator
    ):
        """If templates dict is empty (edge case) the method should not crash."""
        session = _make_session()
        # Remove templates temporarily
        original = generator.choice_templates.copy()
        generator.choice_templates = {}
        result = await generator.generate_emotion_appropriate_choice(
            ChoiceType.THERAPEUTIC, "calm", session
        )
        generator.choice_templates = original
        assert result is None

    async def test_calming_tone_applied_for_anxious(self, generator: ChoiceGenerator):
        session = _make_session(EmotionalState.ANXIOUS)
        choice = await generator.generate_emotion_appropriate_choice(
            ChoiceType.THERAPEUTIC, "anxious", session
        )
        assert choice is not None
        # Anxious state → tone="calming" → text prefixed with "Gently"
        assert choice.choice_text.lower().startswith("gently")

    async def test_difficulty_reduced_for_overwhelmed(
        self, generator: ChoiceGenerator
    ):
        session = _make_session(EmotionalState.OVERWHELMED)
        choice = await generator.generate_emotion_appropriate_choice(
            ChoiceType.THERAPEUTIC, "overwhelmed", session
        )
        assert choice is not None
        assert choice.difficulty_level == DifficultyLevel.GENTLE
