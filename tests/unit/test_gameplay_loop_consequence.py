"""
Unit tests for:
  - src/components/gameplay_loop/consequence_system/system.py (ConsequenceSystem)
  - src/components/gameplay_loop/consequence_system/therapeutic_framer.py (TherapeuticFramer)

All external sub-systems (OutcomeGenerator, CausalityExplainer, ProgressTracker) are
mocked so these tests remain pure unit tests with no external service dependencies.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.components.gameplay_loop.consequence_system.therapeutic_framer import (
    TherapeuticFramer,
)
from src.components.gameplay_loop.models.core import (
    ChoiceType,
    ConsequenceSet,
    EmotionalState,
    Scene,
    SceneType,
    SessionState,
)
from src.components.gameplay_loop.models.interactions import UserChoice

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_user_choice(
    therapeutic_value: float = 0.7,
    therapeutic_tags: list[str] | None = None,
    choice_type: ChoiceType = ChoiceType.THERAPEUTIC,
    agency_level: float = 0.6,
) -> UserChoice:
    return UserChoice(
        choice_id="uc-test",
        session_id="s-test",
        scene_id="sc-test",
        choice_text="Test choice",
        choice_type=choice_type,
        therapeutic_value=therapeutic_value,
        therapeutic_tags=therapeutic_tags or [],
        agency_level=agency_level,
        emotional_state_before=EmotionalState.CALM,
    )


def _make_scene(therapeutic_focus: list[str] | None = None) -> Scene:
    return Scene(
        title="Test Scene",
        description="A test scene",
        narrative_content="Narrative text",
        scene_type=SceneType.THERAPEUTIC,
        therapeutic_focus=therapeutic_focus or [],
    )


def _make_session(emotional_state: EmotionalState = EmotionalState.CALM) -> SessionState:
    ss = SessionState(user_id="test-user")
    ss.emotional_state = emotional_state
    return ss


def _make_consequence_set(
    choice_id: str = "c1",
    therapeutic_value: float = 0.5,
    therapeutic_insights: list[str] | None = None,
    learning_opportunities: list[str] | None = None,
    narrative_consequences: list[str] | None = None,
    progress_markers: list | None = None,
    skill_development: list[str] | None = None,
    emotional_impact: dict | None = None,
    character_development: dict | None = None,
    world_state_changes: dict | None = None,
) -> ConsequenceSet:
    return ConsequenceSet(
        choice_id=choice_id,
        therapeutic_value_realized=therapeutic_value,
        therapeutic_insights=therapeutic_insights or [],
        learning_opportunities=learning_opportunities or [],
        narrative_consequences=narrative_consequences or [],
        progress_markers=progress_markers or [],
        skill_development=skill_development or [],
        emotional_impact=emotional_impact or {},
        character_development=character_development or {},
        world_state_changes=world_state_changes or {},
    )


# ---------------------------------------------------------------------------
# ConsequenceSystem tests
# ---------------------------------------------------------------------------


class TestConsequenceSystemInit:
    """Test construction and initialization of ConsequenceSystem."""

    def test_default_construction(self):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cs = ConsequenceSystem()
        assert cs.config == {}
        assert cs.consequence_depth == "moderate"
        assert cs.therapeutic_emphasis == 0.7
        assert cs.causality_clarity == "high"

    def test_custom_config(self):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cfg = {
            "consequence_depth": "deep",
            "therapeutic_emphasis": 0.9,
            "causality_clarity": "medium",
        }
        cs = ConsequenceSystem(config=cfg)
        assert cs.consequence_depth == "deep"
        assert cs.therapeutic_emphasis == 0.9
        assert cs.causality_clarity == "medium"

    async def test_initialize_calls_subsystem_initializers(self):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cs = ConsequenceSystem()
        cs.outcome_generator.initialize = AsyncMock(return_value=True)
        cs.therapeutic_framer.initialize = AsyncMock(return_value=True)
        cs.causality_explainer.initialize = AsyncMock(return_value=True)
        cs.progress_tracker.initialize = AsyncMock(return_value=True)

        result = await cs.initialize()
        assert result is True
        cs.outcome_generator.initialize.assert_called_once()
        cs.therapeutic_framer.initialize.assert_called_once()
        cs.causality_explainer.initialize.assert_called_once()
        cs.progress_tracker.initialize.assert_called_once()

    async def test_initialize_returns_false_on_error(self):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cs = ConsequenceSystem()
        cs.outcome_generator.initialize = AsyncMock(side_effect=RuntimeError("boom"))

        result = await cs.initialize()
        assert result is False


# ---------------------------------------------------------------------------
# ConsequenceSystem.generate_consequences
# ---------------------------------------------------------------------------


class TestGenerateConsequences:
    def _make_system_with_mocks(
        self,
        outcomes: dict | None = None,
        framing: dict | None = None,
        causality: str = "Because of your choice",
        progress: dict | None = None,
    ):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cs = ConsequenceSystem()
        cs.outcome_generator.generate_outcomes = AsyncMock(
            return_value=outcomes
            or {
                "immediate": ["You feel calmer"],
                "delayed": ["Stress reduces over time"],
                "emotional_impact": {"primary_emotion": "calm", "intensity": 0.6},
                "narrative": ["The world shifts"],
                "character_development": {"confidence": 0.1},
                "world_state_changes": {"mood": "peaceful"},
            }
        )
        cs.therapeutic_framer.frame_outcomes = AsyncMock(
            return_value=framing
            or {
                "insights": ["You showed courage"],
                "learning_opportunities": ["mindfulness"],
                "therapeutic_value": 0.75,
            }
        )
        cs.causality_explainer.explain_causality = AsyncMock(
            return_value=causality
        )
        cs.progress_tracker.track_progress = AsyncMock(
            return_value=progress
            or {
                "progress_markers": ["therapeutic_milestone"],
                "skill_development": ["coping_strategies"],
            }
        )
        return cs

    async def test_returns_consequence_set(self):
        cs = self._make_system_with_mocks()
        uc = _make_user_choice()
        scene = _make_scene()
        session = _make_session()

        result = await cs.generate_consequences(uc, scene, session)

        assert isinstance(result, ConsequenceSet)
        assert result.choice_id == uc.choice_id

    async def test_consequence_set_has_immediate_outcomes(self):
        cs = self._make_system_with_mocks()
        result = await cs.generate_consequences(_make_user_choice(), _make_scene(), _make_session())
        assert "You feel calmer" in result.immediate_outcomes

    async def test_consequence_set_has_therapeutic_insights(self):
        cs = self._make_system_with_mocks()
        result = await cs.generate_consequences(_make_user_choice(), _make_scene(), _make_session())
        assert "You showed courage" in result.therapeutic_insights

    async def test_consequence_set_has_causality_explanation(self):
        cs = self._make_system_with_mocks()
        result = await cs.generate_consequences(_make_user_choice(), _make_scene(), _make_session())
        assert result.causality_explanation == "Because of your choice"

    async def test_consequence_set_has_progress_markers(self):
        cs = self._make_system_with_mocks()
        result = await cs.generate_consequences(_make_user_choice(), _make_scene(), _make_session())
        assert "therapeutic_milestone" in result.progress_markers

    async def test_consequence_set_has_skill_development(self):
        cs = self._make_system_with_mocks()
        result = await cs.generate_consequences(_make_user_choice(), _make_scene(), _make_session())
        assert "coping_strategies" in result.skill_development

    async def test_falls_back_on_exception(self):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cs = ConsequenceSystem()
        cs.outcome_generator.generate_outcomes = AsyncMock(
            side_effect=RuntimeError("generation error")
        )
        # Fallback generation should work
        result = await cs.generate_consequences(
            _make_user_choice(), _make_scene(), _make_session()
        )
        assert isinstance(result, ConsequenceSet)
        assert len(result.therapeutic_insights) > 0


# ---------------------------------------------------------------------------
# ConsequenceSystem.evaluate_consequence_impact
# ---------------------------------------------------------------------------


class TestEvaluateConsequenceImpact:
    def _make_system(self):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        return ConsequenceSystem()

    async def test_returns_dict_with_expected_keys(self):
        cs = self._make_system()
        cs_set = _make_consequence_set()
        result = await cs.evaluate_consequence_impact(cs_set, _make_session())
        assert "therapeutic_impact" in result
        assert "narrative_impact" in result
        assert "emotional_impact" in result
        assert "learning_impact" in result
        assert "overall_impact" in result
        assert "impact_areas" in result
        assert "growth_indicators" in result

    async def test_overall_impact_between_0_and_1(self):
        cs = self._make_system()
        cs_set = _make_consequence_set(
            therapeutic_value=0.8,
            therapeutic_insights=["insight1"],
            learning_opportunities=["learn1"],
            narrative_consequences=["narr1"],
        )
        result = await cs.evaluate_consequence_impact(cs_set, _make_session())
        assert 0.0 <= result["overall_impact"] <= 1.0

    async def test_impact_areas_populated(self):
        cs = self._make_system()
        cs_set = _make_consequence_set(
            therapeutic_insights=["insight"],
            learning_opportunities=["learn"],
            narrative_consequences=["narr"],
            character_development={"confidence": 0.1},
            world_state_changes={"mood": "calm"},
            skill_development=["coping"],
        )
        result = await cs.evaluate_consequence_impact(cs_set, _make_session())
        assert "therapeutic_insight" in result["impact_areas"]
        assert "learning_development" in result["impact_areas"]
        assert "story_progression" in result["impact_areas"]

    async def test_growth_indicators_high_therapeutic_value(self):
        cs = self._make_system()
        cs_set = _make_consequence_set(therapeutic_value=0.9)
        result = await cs.evaluate_consequence_impact(cs_set, _make_session())
        assert "high_therapeutic_value" in result["growth_indicators"]

    async def test_growth_indicators_multiple_learning_paths(self):
        cs = self._make_system()
        cs_set = _make_consequence_set(
            learning_opportunities=["path1", "path2"]
        )
        result = await cs.evaluate_consequence_impact(cs_set, _make_session())
        assert "multiple_learning_paths" in result["growth_indicators"]

    async def test_growth_indicators_positive_emotional(self):
        cs = self._make_system()
        cs_set = _make_consequence_set(
            emotional_impact={"primary_emotion": "positive", "intensity": 0.8}
        )
        result = await cs.evaluate_consequence_impact(cs_set, _make_session())
        assert "positive_emotional_growth" in result["growth_indicators"]

    async def test_returns_fallback_on_exception(self):
        """Simulate exception in evaluation."""
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cs = ConsequenceSystem()
        # Pass non-ConsequenceSet to force error in internal eval
        result = await cs.evaluate_consequence_impact(
            None,  # type: ignore[arg-type]
            _make_session(),
        )
        assert "overall_impact" in result

    async def test_learning_impact_with_long_causality(self):
        cs = self._make_system()
        cs_set = _make_consequence_set(
            learning_opportunities=["path1", "path2", "path3"],
            skill_development=["skill1"],
        )
        cs_set.causality_explanation = "A" * 60
        result = await cs.evaluate_consequence_impact(cs_set, _make_session())
        assert result["learning_impact"] > 0.0

    async def test_emotional_impact_with_positive_emotion(self):
        cs = self._make_system()
        cs_set = _make_consequence_set(
            emotional_impact={"primary_emotion": "hopeful", "intensity": 0.7},
            skill_development=["emotional_growth"],
        )
        result = await cs.evaluate_consequence_impact(cs_set, _make_session())
        assert result["emotional_impact"] > 0.0


# ---------------------------------------------------------------------------
# ConsequenceSystem.adapt_consequences_for_emotional_state
# ---------------------------------------------------------------------------


class TestAdaptConsequences:
    def _make_system_with_mocks(self):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cs = ConsequenceSystem()
        cs.therapeutic_framer.adapt_framing_for_emotion = AsyncMock(
            return_value={
                "insights": ["Adapted insight"],
                "learning_opportunities": ["Adapted learning"],
                "therapeutic_value": 0.8,
            }
        )
        cs.causality_explainer.adapt_explanation_for_emotion = AsyncMock(
            return_value="Adapted causality explanation"
        )
        return cs

    async def test_returns_adapted_consequence_set(self):
        cs = self._make_system_with_mocks()
        original = _make_consequence_set(choice_id="c1")
        result = await cs.adapt_consequences_for_emotional_state(
            original, EmotionalState.ANXIOUS.value, _make_session()
        )
        assert isinstance(result, ConsequenceSet)
        assert result.consequence_id != original.consequence_id  # new ID

    async def test_adapted_insights_are_applied(self):
        cs = self._make_system_with_mocks()
        original = _make_consequence_set()
        result = await cs.adapt_consequences_for_emotional_state(
            original, EmotionalState.ANXIOUS.value, _make_session()
        )
        assert result.therapeutic_insights == ["Adapted insight"]

    async def test_adapted_causality_is_applied(self):
        cs = self._make_system_with_mocks()
        original = _make_consequence_set()
        result = await cs.adapt_consequences_for_emotional_state(
            original, EmotionalState.CALM.value, _make_session()
        )
        assert result.causality_explanation == "Adapted causality explanation"

    async def test_returns_original_on_exception(self):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cs = ConsequenceSystem()
        cs.therapeutic_framer.adapt_framing_for_emotion = AsyncMock(
            side_effect=RuntimeError("framing error")
        )
        original = _make_consequence_set()
        result = await cs.adapt_consequences_for_emotional_state(
            original, EmotionalState.CALM.value, _make_session()
        )
        assert result is original


# ---------------------------------------------------------------------------
# ConsequenceSystem fallback consequence generation
# ---------------------------------------------------------------------------


class TestFallbackConsequences:
    async def test_fallback_has_required_fields(self):
        from src.components.gameplay_loop.consequence_system.system import (
            ConsequenceSystem,
        )

        cs = ConsequenceSystem()
        uc = _make_user_choice()
        result = await cs._generate_fallback_consequences(uc)

        assert isinstance(result, ConsequenceSet)
        assert result.choice_id == uc.choice_id
        assert len(result.immediate_outcomes) > 0
        assert len(result.therapeutic_insights) > 0
        assert len(result.learning_opportunities) > 0
        assert result.therapeutic_value_realized == 0.5
        assert result.causality_explanation != ""


# ---------------------------------------------------------------------------
# TherapeuticFramer tests
# ---------------------------------------------------------------------------


class TestTherapeuticFramerInit:
    def test_default_construction(self):
        tf = TherapeuticFramer()
        assert tf.config == {}
        assert tf.framing_templates == {}
        assert tf.learning_opportunity_patterns == {}
        assert tf.therapeutic_insight_templates == {}
        assert tf.growth_framing_strategies == {}

    async def test_initialize_returns_true(self):
        tf = TherapeuticFramer()
        result = await tf.initialize()
        assert result is True

    async def test_initialize_populates_templates(self):
        tf = TherapeuticFramer()
        await tf.initialize()
        assert "positive_outcome" in tf.framing_templates
        assert "challenging_outcome" in tf.framing_templates
        assert "neutral_outcome" in tf.framing_templates

    async def test_initialize_populates_learning_patterns(self):
        tf = TherapeuticFramer()
        await tf.initialize()
        assert "self_awareness" in tf.learning_opportunity_patterns
        assert "emotional_regulation" in tf.learning_opportunity_patterns
        assert "mindfulness_practice" in tf.learning_opportunity_patterns

    async def test_initialize_populates_growth_strategies(self):
        tf = TherapeuticFramer()
        await tf.initialize()
        assert "reframe_challenges" in tf.growth_framing_strategies
        assert "highlight_progress" in tf.growth_framing_strategies

    async def test_initialize_returns_false_on_error(self):
        tf = TherapeuticFramer()
        with patch.object(
            tf, "_load_framing_templates", side_effect=RuntimeError("err")
        ):
            result = await tf.initialize()
        assert result is False


# ---------------------------------------------------------------------------
# TherapeuticFramer.frame_outcomes
# ---------------------------------------------------------------------------


class TestFrameOutcomes:
    @pytest.fixture
    async def initialized_framer(self) -> TherapeuticFramer:
        tf = TherapeuticFramer()
        await tf.initialize()
        return tf

    async def test_returns_dict_with_expected_keys(self, initialized_framer):
        uc = _make_user_choice()
        result = await initialized_framer.frame_outcomes({}, uc, _make_session())
        assert "insights" in result
        assert "learning_opportunities" in result
        assert "therapeutic_value" in result
        assert "growth_aspects" in result
        assert "positive_reframes" in result

    async def test_high_therapeutic_value_insight(self, initialized_framer):
        uc = _make_user_choice(therapeutic_value=0.8)
        result = await initialized_framer.frame_outcomes({}, uc, _make_session())
        assert len(result["insights"]) > 0
        combined = " ".join(result["insights"])
        assert "strong therapeutic engagement" in combined

    async def test_medium_therapeutic_value_insight(self, initialized_framer):
        uc = _make_user_choice(therapeutic_value=0.5)
        result = await initialized_framer.frame_outcomes({}, uc, _make_session())
        combined = " ".join(result["insights"])
        assert "therapeutic journey" in combined

    async def test_low_therapeutic_value_insight(self, initialized_framer):
        uc = _make_user_choice(therapeutic_value=0.2)
        result = await initialized_framer.frame_outcomes({}, uc, _make_session())
        combined = " ".join(result["insights"])
        assert "Every choice" in combined

    async def test_positive_emotional_outcome_adds_insight(self, initialized_framer):
        uc = _make_user_choice(therapeutic_value=0.7)
        outcomes = {"emotional_impact": {"primary_emotion": "positive"}}
        result = await initialized_framer.frame_outcomes(outcomes, uc, _make_session())
        combined = " ".join(result["insights"])
        assert "positive emotional shift" in combined

    async def test_therapeutic_value_boosted_for_positive_emotion(self, initialized_framer):
        uc = _make_user_choice(therapeutic_value=0.7)
        outcomes = {"emotional_impact": {"primary_emotion": "hopeful"}}
        result = await initialized_framer.frame_outcomes(outcomes, uc, _make_session())
        # Should be 0.7 + 0.1 = 0.8
        assert result["therapeutic_value"] == pytest.approx(0.8, abs=0.01)

    async def test_learning_opportunities_from_tags(self, initialized_framer):
        uc = _make_user_choice(therapeutic_tags=["self_awareness"])
        result = await initialized_framer.frame_outcomes({}, uc, _make_session())
        assert len(result["learning_opportunities"]) > 0

    async def test_learning_opportunities_fallback_when_no_tags(self, initialized_framer):
        uc = _make_user_choice(therapeutic_tags=[])
        result = await initialized_framer.frame_outcomes({}, uc, _make_session())
        assert len(result["learning_opportunities"]) > 0
        assert "values" in result["learning_opportunities"][0]

    async def test_growth_aspects_therapeutic_engagement(self, initialized_framer):
        uc = _make_user_choice(therapeutic_value=0.7)
        result = await initialized_framer.frame_outcomes({}, uc, _make_session())
        assert "therapeutic_engagement" in result["growth_aspects"]

    async def test_growth_aspects_resilience_tag(self, initialized_framer):
        uc = _make_user_choice(
            therapeutic_value=0.7, therapeutic_tags=["resilience"]
        )
        result = await initialized_framer.frame_outcomes({}, uc, _make_session())
        assert "resilience" in result["growth_aspects"]

    async def test_positive_reframes_not_empty(self, initialized_framer):
        uc = _make_user_choice()
        result = await initialized_framer.frame_outcomes({}, uc, _make_session())
        assert len(result["positive_reframes"]) > 0

    async def test_fallback_framing_on_exception(self):
        """Uninitialized framer should return fallback framing."""
        tf = TherapeuticFramer()
        uc = _make_user_choice(therapeutic_value=0.6)
        result = await tf.frame_outcomes({}, uc, _make_session())
        # Should use fallback
        assert "insights" in result
        assert result["therapeutic_value"] >= 0.3


# ---------------------------------------------------------------------------
# TherapeuticFramer.adapt_framing_for_emotion
# ---------------------------------------------------------------------------


class TestAdaptFramingForEmotion:
    @pytest.fixture
    async def initialized_framer(self) -> TherapeuticFramer:
        tf = TherapeuticFramer()
        await tf.initialize()
        return tf

    async def test_crisis_state_returns_safety_insight(self, initialized_framer):
        cs_set = _make_consequence_set(
            therapeutic_insights=["Original insight"],
            learning_opportunities=["Original learning"],
            therapeutic_value=0.5,
        )
        result = await initialized_framer.adapt_framing_for_emotion(
            cs_set, EmotionalState.CRISIS.value, _make_session()
        )
        assert "safe" in result["insights"][0].lower()

    async def test_crisis_state_boosts_therapeutic_value(self, initialized_framer):
        cs_set = _make_consequence_set(therapeutic_value=0.3)
        result = await initialized_framer.adapt_framing_for_emotion(
            cs_set, EmotionalState.CRISIS.value, _make_session()
        )
        assert result["therapeutic_value"] >= 0.7

    async def test_anxious_state_limits_insights_to_one(self, initialized_framer):
        cs_set = _make_consequence_set(
            therapeutic_insights=["Insight 1", "Insight 2", "Insight 3"],
            therapeutic_value=0.5,
        )
        result = await initialized_framer.adapt_framing_for_emotion(
            cs_set, EmotionalState.ANXIOUS.value, _make_session()
        )
        assert len(result["insights"]) == 1
        assert "one step" in result["insights"][0].lower()

    async def test_anxious_state_limits_learning_to_one(self, initialized_framer):
        cs_set = _make_consequence_set(
            learning_opportunities=["learn1", "learn2"],
            therapeutic_value=0.5,
        )
        result = await initialized_framer.adapt_framing_for_emotion(
            cs_set, EmotionalState.ANXIOUS.value, _make_session()
        )
        assert len(result["learning_opportunities"]) == 1

    async def test_anxious_state_boosts_value_slightly(self, initialized_framer):
        cs_set = _make_consequence_set(therapeutic_value=0.6)
        result = await initialized_framer.adapt_framing_for_emotion(
            cs_set, EmotionalState.ANXIOUS.value, _make_session()
        )
        assert result["therapeutic_value"] >= 0.6

    async def test_calm_state_preserves_insights(self, initialized_framer):
        cs_set = _make_consequence_set(
            therapeutic_insights=["A", "B", "C"],
            therapeutic_value=0.5,
        )
        result = await initialized_framer.adapt_framing_for_emotion(
            cs_set, EmotionalState.CALM.value, _make_session()
        )
        assert result["insights"] == ["A", "B", "C"]

    async def test_distressed_state_safety_focus(self, initialized_framer):
        cs_set = _make_consequence_set(
            therapeutic_insights=["Normal insight"],
            learning_opportunities=["Normal learning"],
            therapeutic_value=0.4,
        )
        result = await initialized_framer.adapt_framing_for_emotion(
            cs_set, EmotionalState.DISTRESSED.value, _make_session()
        )
        assert "safe" in result["insights"][0].lower()
        assert "focus on safety" in result["learning_opportunities"][0].lower()

    async def test_empty_insights_returns_fallback(self, initialized_framer):
        cs_set = _make_consequence_set(therapeutic_insights=[], therapeutic_value=0.5)
        result = await initialized_framer.adapt_framing_for_emotion(
            cs_set, EmotionalState.CALM.value, _make_session()
        )
        assert len(result["insights"]) > 0

    async def test_returns_fallback_on_invalid_state(self, initialized_framer):
        cs_set = _make_consequence_set()
        result = await initialized_framer.adapt_framing_for_emotion(
            cs_set, "not_a_valid_state", _make_session()
        )
        assert "therapeutic_value" in result
