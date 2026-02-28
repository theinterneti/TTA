"""
Unit tests for TherapeuticFramer, CausalityExplainer, and ProgressTracker
in the consequence_system package.

No external services are required; all three components are template-based.
"""

from __future__ import annotations

import pytest

from src.components.gameplay_loop.consequence_system.causality_explainer import (
    CausalityExplainer,
)
from src.components.gameplay_loop.consequence_system.progress_tracker import (
    ProgressTracker,
)
from src.components.gameplay_loop.consequence_system.therapeutic_framer import (
    TherapeuticFramer,
)
from src.components.gameplay_loop.models.core import (
    ChoiceType,
    ConsequenceSet,
    DifficultyLevel,
    EmotionalState,
    Scene,
    SceneType,
    SessionState,
    TherapeuticContext,
)
from src.components.gameplay_loop.models.interactions import UserChoice
from src.components.gameplay_loop.models.progress import ProgressType

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_choice(
    choice_type: ChoiceType = ChoiceType.THERAPEUTIC,
    therapeutic_value: float = 0.8,
    therapeutic_tags: list[str] | None = None,
) -> UserChoice:
    return UserChoice(
        choice_id="uc-test",
        session_id="s-test",
        scene_id="sc-test",
        choice_text="Take a mindful breath",
        choice_type=choice_type,
        therapeutic_value=therapeutic_value,
        therapeutic_tags=therapeutic_tags or ["mindfulness", "grounding"],
        agency_level=0.7,
        emotional_state_before=EmotionalState.CALM,
    )


def _make_session(
    emotional_state: EmotionalState = EmotionalState.CALM,
    choice_history: list[dict] | None = None,
) -> SessionState:
    ss = SessionState(user_id="user-test")
    ss.emotional_state = emotional_state
    ss.therapeutic_context = TherapeuticContext()
    if choice_history is not None:
        ss.choice_history = choice_history
    return ss


def _make_scene() -> Scene:
    return Scene(
        title="Forest Path",
        description="A peaceful forest path.",
        narrative_content="Light filters through the trees...",
        scene_type=SceneType.THERAPEUTIC,
    )


def _make_outcomes(primary_emotion: str = "neutral") -> dict:
    return {
        "immediate": ["You feel a shift."],
        "delayed": [],
        "emotional_impact": {"primary_emotion": primary_emotion, "intensity": 0.7},
        "narrative": [],
        "character_development": {},
        "world_state_changes": {},
    }


def _make_consequence_set(therapeutic_value: float = 0.7) -> ConsequenceSet:
    return ConsequenceSet(
        choice_id="uc-test",
        therapeutic_value_realized=therapeutic_value,
        therapeutic_insights=["Growth is happening."],
        learning_opportunities=["self_awareness"],
        causality_explanation="Your choice led forward.",
    )


# ---------------------------------------------------------------------------
# TherapeuticFramer — fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def framer() -> TherapeuticFramer:
    tf = TherapeuticFramer()
    await tf.initialize()
    return tf


# ---------------------------------------------------------------------------
# TherapeuticFramer — initialization
# ---------------------------------------------------------------------------


class TestTherapeuticFramerInit:
    async def test_initialize_returns_true(self):
        tf = TherapeuticFramer()
        assert await tf.initialize() is True

    async def test_framing_templates_populated(self, framer):
        assert len(framer.framing_templates) > 0

    async def test_learning_patterns_populated(self, framer):
        assert len(framer.learning_opportunity_patterns) > 0

    async def test_insight_templates_populated(self, framer):
        assert len(framer.therapeutic_insight_templates) > 0

    async def test_growth_strategies_populated(self, framer):
        assert len(framer.growth_framing_strategies) > 0


# ---------------------------------------------------------------------------
# TherapeuticFramer — frame_outcomes
# ---------------------------------------------------------------------------


class TestFrameOutcomes:
    async def test_returns_dict_with_all_keys(self, framer):
        uc = _make_choice()
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        for key in ("insights", "learning_opportunities", "therapeutic_value",
                    "growth_aspects", "positive_reframes"):
            assert key in result

    async def test_high_value_insight_content(self, framer):
        uc = _make_choice(therapeutic_value=0.9)
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        assert any("strong therapeutic" in i.lower() for i in result["insights"])

    async def test_medium_value_insight_content(self, framer):
        uc = _make_choice(therapeutic_value=0.5)
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        assert len(result["insights"]) > 0

    async def test_low_value_insight_content(self, framer):
        uc = _make_choice(therapeutic_value=0.2)
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        assert any("learning" in i.lower() or "growth" in i.lower()
                   for i in result["insights"])

    async def test_positive_emotion_adds_insight(self, framer):
        uc = _make_choice(therapeutic_value=0.9)
        outcomes = _make_outcomes(primary_emotion="positive")
        result = await framer.frame_outcomes(outcomes, uc, _make_session())
        assert len(result["insights"]) >= 2

    async def test_known_tag_generates_learning_opportunity(self, framer):
        uc = _make_choice(therapeutic_tags=["mindfulness"])
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        assert len(result["learning_opportunities"]) > 0

    async def test_unknown_tags_still_return_fallback_learning(self, framer):
        uc = _make_choice(therapeutic_tags=["rare_tag_xyz"])
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        assert len(result["learning_opportunities"]) > 0

    async def test_therapeutic_value_in_range(self, framer):
        uc = _make_choice(therapeutic_value=0.6)
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        assert 0.0 <= result["therapeutic_value"] <= 1.0

    async def test_positive_emotion_boosts_therapeutic_value(self, framer):
        uc = _make_choice(therapeutic_value=0.6)
        result_neutral = await framer.frame_outcomes(
            _make_outcomes("neutral"), uc, _make_session()
        )
        result_positive = await framer.frame_outcomes(
            _make_outcomes("positive"), uc, _make_session()
        )
        assert result_positive["therapeutic_value"] >= result_neutral["therapeutic_value"]

    async def test_growth_aspects_include_resilience_tag(self, framer):
        uc = _make_choice(
            therapeutic_value=0.8,
            therapeutic_tags=["resilience", "mindfulness"],
        )
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        assert "resilience" in result["growth_aspects"]

    async def test_high_value_adds_therapeutic_engagement_aspect(self, framer):
        uc = _make_choice(therapeutic_value=0.8)
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        assert "therapeutic_engagement" in result["growth_aspects"]

    async def test_positive_reframes_non_empty(self, framer):
        uc = _make_choice()
        result = await framer.frame_outcomes(_make_outcomes(), uc, _make_session())
        assert len(result["positive_reframes"]) > 0


# ---------------------------------------------------------------------------
# TherapeuticFramer — adapt_framing_for_emotion
# ---------------------------------------------------------------------------


class TestAdaptFramingForEmotion:
    async def test_crisis_returns_safety_insight(self, framer):
        cs = _make_consequence_set()
        result = await framer.adapt_framing_for_emotion(cs, "crisis", _make_session())
        assert any("safe" in i.lower() for i in result["insights"])

    async def test_distressed_returns_safety_insight(self, framer):
        cs = _make_consequence_set()
        result = await framer.adapt_framing_for_emotion(cs, "distressed", _make_session())
        assert any("safe" in i.lower() or "grounding" in i.lower()
                   for i in result["insights"])

    async def test_anxious_appends_one_step_at_a_time(self, framer):
        cs = _make_consequence_set()
        result = await framer.adapt_framing_for_emotion(cs, "anxious", _make_session())
        assert any("one step" in i.lower() for i in result["insights"])

    async def test_calm_preserves_insights_unchanged(self, framer):
        cs = _make_consequence_set()
        result = await framer.adapt_framing_for_emotion(cs, "calm", _make_session())
        assert result["insights"] == cs.therapeutic_insights

    async def test_crisis_boosts_therapeutic_value_to_min_07(self, framer):
        cs = _make_consequence_set(therapeutic_value=0.3)
        result = await framer.adapt_framing_for_emotion(cs, "crisis", _make_session())
        assert result["therapeutic_value"] >= 0.7

    async def test_anxious_slightly_boosts_therapeutic_value(self, framer):
        cs = _make_consequence_set(therapeutic_value=0.5)
        result = await framer.adapt_framing_for_emotion(cs, "anxious", _make_session())
        assert result["therapeutic_value"] >= 0.5

    async def test_invalid_emotion_returns_fallback(self, framer):
        cs = _make_consequence_set()
        result = await framer.adapt_framing_for_emotion(
            cs, "not_a_real_state", _make_session()
        )
        assert "therapeutic_value" in result


# ---------------------------------------------------------------------------
# TherapeuticFramer — fallback
# ---------------------------------------------------------------------------


class TestTherapeuticFramerFallback:
    async def test_fallback_has_all_keys(self, framer):
        uc = _make_choice()
        result = await framer._generate_fallback_framing(uc)
        for key in ("insights", "learning_opportunities", "therapeutic_value",
                    "growth_aspects", "positive_reframes"):
            assert key in result

    async def test_fallback_value_at_least_03(self, framer):
        uc = _make_choice(therapeutic_value=0.1)
        result = await framer._generate_fallback_framing(uc)
        assert result["therapeutic_value"] >= 0.3


# ---------------------------------------------------------------------------
# CausalityExplainer — fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def explainer() -> CausalityExplainer:
    ce = CausalityExplainer()
    await ce.initialize()
    return ce


# ---------------------------------------------------------------------------
# CausalityExplainer — initialization
# ---------------------------------------------------------------------------


class TestCausalityExplainerInit:
    async def test_initialize_returns_true(self):
        ce = CausalityExplainer()
        assert await ce.initialize() is True

    async def test_explanation_templates_populated(self, explainer):
        assert len(explainer.explanation_templates) > 0

    async def test_causal_patterns_populated(self, explainer):
        assert len(explainer.causal_relationship_patterns) > 0

    async def test_clarity_levels_populated(self, explainer):
        assert len(explainer.clarity_levels) > 0


# ---------------------------------------------------------------------------
# CausalityExplainer — explain_causality
# ---------------------------------------------------------------------------


class TestExplainCausality:
    async def test_returns_non_empty_string(self, explainer):
        uc = _make_choice()
        result = await explainer.explain_causality(
            uc, _make_outcomes(), _make_scene(), _make_session()
        )
        assert isinstance(result, str) and len(result) > 0

    async def test_calm_state_gives_direct_explanation(self, explainer):
        uc = _make_choice()
        result = await explainer.explain_causality(
            uc, _make_outcomes(), _make_scene(), _make_session(EmotionalState.CALM)
        )
        assert not result.lower().startswith("gently") and not result.lower().startswith("naturally")

    async def test_anxious_state_prefixes_naturally(self, explainer):
        uc = _make_choice()
        result = await explainer.explain_causality(
            uc, _make_outcomes(), _make_scene(), _make_session(EmotionalState.ANXIOUS)
        )
        assert result.lower().startswith("naturally")

    async def test_overwhelmed_state_prefixes_gently(self, explainer):
        uc = _make_choice()
        result = await explainer.explain_causality(
            uc, _make_outcomes(), _make_scene(), _make_session(EmotionalState.OVERWHELMED)
        )
        assert result.lower().startswith("gently")

    async def test_crisis_state_prefixes_gently(self, explainer):
        uc = _make_choice()
        result = await explainer.explain_causality(
            uc, _make_outcomes(), _make_scene(), _make_session(EmotionalState.CRISIS)
        )
        assert result.lower().startswith("gently")

    async def test_all_choice_types_produce_explanation(self, explainer):
        for choice_type in ChoiceType:
            uc = _make_choice(choice_type=choice_type)
            result = await explainer.explain_causality(
                uc, _make_outcomes(), _make_scene(), _make_session()
            )
            assert len(result) > 0, f"Empty explanation for {choice_type}"


# ---------------------------------------------------------------------------
# CausalityExplainer — adapt_explanation_for_emotion
# ---------------------------------------------------------------------------


class TestAdaptExplanationForEmotion:
    async def test_crisis_adds_right_now_prefix(self, explainer):
        result = await explainer.adapt_explanation_for_emotion(
            "Your choice leads forward.", "crisis"
        )
        assert result.lower().startswith("right now")

    async def test_distressed_adds_gently_prefix(self, explainer):
        result = await explainer.adapt_explanation_for_emotion(
            "Your choice leads forward.", "distressed"
        )
        assert result.lower().startswith("gently")

    async def test_overwhelmed_adds_simply_put(self, explainer):
        result = await explainer.adapt_explanation_for_emotion(
            "Your choice leads forward.", "overwhelmed"
        )
        assert "simply" in result.lower()

    async def test_anxious_adds_reassuringly(self, explainer):
        result = await explainer.adapt_explanation_for_emotion(
            "Your choice leads forward.", "anxious"
        )
        assert result.lower().startswith("reassuringly")

    async def test_engaged_adds_encouragingly(self, explainer):
        result = await explainer.adapt_explanation_for_emotion(
            "Your choice leads forward.", "engaged"
        )
        assert result.lower().startswith("encouragingly")

    async def test_calm_returns_unchanged(self, explainer):
        original = "Your choice leads forward."
        result = await explainer.adapt_explanation_for_emotion(original, "calm")
        assert result == original

    async def test_invalid_emotion_returns_original(self, explainer):
        original = "Your choice leads forward."
        result = await explainer.adapt_explanation_for_emotion(original, "unknown_state")
        assert result == original


# ---------------------------------------------------------------------------
# CausalityExplainer — fallback
# ---------------------------------------------------------------------------


class TestCausalityFallback:
    async def test_fallback_contains_choice_text(self, explainer):
        uc = _make_choice()
        result = await explainer._generate_fallback_explanation(uc)
        assert "mindful breath" in result.lower()

    async def test_fallback_non_empty(self, explainer):
        uc = _make_choice()
        result = await explainer._generate_fallback_explanation(uc)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# ProgressTracker — fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def tracker() -> ProgressTracker:
    pt = ProgressTracker()
    await pt.initialize()
    return pt


# ---------------------------------------------------------------------------
# ProgressTracker — initialization
# ---------------------------------------------------------------------------


class TestProgressTrackerInit:
    async def test_initialize_returns_true(self):
        pt = ProgressTracker()
        assert await pt.initialize() is True

    async def test_progress_patterns_populated(self, tracker):
        assert len(tracker.progress_patterns) > 0

    async def test_milestone_definitions_populated(self, tracker):
        assert len(tracker.milestone_definitions) > 0

    async def test_skill_tracks_populated(self, tracker):
        assert len(tracker.skill_development_tracks) > 0

    async def test_growth_indicators_populated(self, tracker):
        assert len(tracker.growth_indicators) > 0


# ---------------------------------------------------------------------------
# ProgressTracker — track_progress
# ---------------------------------------------------------------------------


class TestTrackProgress:
    async def test_returns_dict_with_all_keys(self, tracker):
        uc = _make_choice()
        result = await tracker.track_progress(uc, _make_outcomes(), _make_session())
        for key in ("progress_markers", "skill_development", "growth_patterns",
                    "milestone_achievements", "therapeutic_gains"):
            assert key in result

    async def test_on_exception_returns_safe_fallback(self, tracker):
        uc = _make_choice()
        # Corrupt tracker to force exception path
        tracker.progress_patterns = None  # type: ignore
        result = await tracker.track_progress(uc, _make_outcomes(), _make_session())
        assert "progress_markers" in result
        assert "skill_development" in result


# ---------------------------------------------------------------------------
# ProgressTracker — _identify_progress_markers
# ---------------------------------------------------------------------------


class TestIdentifyProgressMarkers:
    async def test_high_value_creates_therapeutic_engagement_marker(self, tracker):
        uc = _make_choice(therapeutic_value=0.8)
        markers = await tracker._identify_progress_markers(
            uc, _make_outcomes(), _make_session()
        )
        types = [m.marker_type for m in markers]
        assert ProgressType.THERAPEUTIC_ENGAGEMENT in types

    async def test_low_value_no_therapeutic_marker(self, tracker):
        uc = _make_choice(therapeutic_value=0.5)
        markers = await tracker._identify_progress_markers(
            uc, _make_outcomes(), _make_session()
        )
        types = [m.marker_type for m in markers]
        assert ProgressType.THERAPEUTIC_ENGAGEMENT not in types

    async def test_skill_building_choice_creates_skill_marker(self, tracker):
        uc = _make_choice(choice_type=ChoiceType.SKILL_BUILDING)
        markers = await tracker._identify_progress_markers(
            uc, _make_outcomes(), _make_session()
        )
        types = [m.marker_type for m in markers]
        assert ProgressType.SKILL_DEVELOPMENT in types

    async def test_emotional_regulation_choice_creates_emotion_marker(self, tracker):
        uc = _make_choice(choice_type=ChoiceType.EMOTIONAL_REGULATION)
        markers = await tracker._identify_progress_markers(
            uc, _make_outcomes(), _make_session()
        )
        types = [m.marker_type for m in markers]
        assert ProgressType.EMOTIONAL_REGULATION in types

    async def test_self_awareness_tag_creates_self_awareness_marker(self, tracker):
        uc = _make_choice(therapeutic_tags=["self_awareness"])
        markers = await tracker._identify_progress_markers(
            uc, _make_outcomes(), _make_session()
        )
        types = [m.marker_type for m in markers]
        assert ProgressType.SELF_AWARENESS in types

    async def test_reflection_tag_creates_self_awareness_marker(self, tracker):
        uc = _make_choice(therapeutic_tags=["reflection"])
        markers = await tracker._identify_progress_markers(
            uc, _make_outcomes(), _make_session()
        )
        types = [m.marker_type for m in markers]
        assert ProgressType.SELF_AWARENESS in types

    async def test_narrative_choice_no_markers_when_low_value(self, tracker):
        uc = _make_choice(
            choice_type=ChoiceType.NARRATIVE,
            therapeutic_value=0.4,
            therapeutic_tags=[],
        )
        markers = await tracker._identify_progress_markers(
            uc, _make_outcomes(), _make_session()
        )
        assert len(markers) == 0


# ---------------------------------------------------------------------------
# ProgressTracker — _track_skill_development
# ---------------------------------------------------------------------------


class TestTrackSkillDevelopment:
    async def test_mindfulness_tag_maps_to_skill(self, tracker):
        uc = _make_choice(therapeutic_tags=["mindfulness"])
        skills = await tracker._track_skill_development(uc, _make_outcomes())
        assert "mindfulness_practice" in skills

    async def test_multiple_known_tags_map_to_multiple_skills(self, tracker):
        uc = _make_choice(therapeutic_tags=["mindfulness", "grounding", "resilience"])
        skills = await tracker._track_skill_development(uc, _make_outcomes())
        assert "mindfulness_practice" in skills
        assert "grounding_techniques" in skills
        assert "resilience_building" in skills

    async def test_therapeutic_choice_adds_engagement_skill(self, tracker):
        uc = _make_choice(choice_type=ChoiceType.THERAPEUTIC, therapeutic_tags=[])
        skills = await tracker._track_skill_development(uc, _make_outcomes())
        assert "therapeutic_engagement" in skills

    async def test_skill_building_choice_adds_general_skill(self, tracker):
        uc = _make_choice(choice_type=ChoiceType.SKILL_BUILDING, therapeutic_tags=[])
        skills = await tracker._track_skill_development(uc, _make_outcomes())
        assert "general_skill_building" in skills

    async def test_unknown_tags_produce_no_skills(self, tracker):
        uc = _make_choice(
            choice_type=ChoiceType.NARRATIVE,
            therapeutic_tags=["nonexistent_tag"],
        )
        skills = await tracker._track_skill_development(uc, _make_outcomes())
        assert "nonexistent_tag" not in skills

    async def test_no_duplicate_skills(self, tracker):
        uc = _make_choice(therapeutic_tags=["mindfulness", "mindfulness"])
        skills = await tracker._track_skill_development(uc, _make_outcomes())
        assert len(skills) == len(set(skills))


# ---------------------------------------------------------------------------
# ProgressTracker — _identify_growth_patterns
# ---------------------------------------------------------------------------


class TestIdentifyGrowthPatterns:
    async def test_increasing_values_detected(self, tracker):
        history = [
            {"therapeutic_value": 0.3, "therapeutic_tags": []},
            {"therapeutic_value": 0.5, "therapeutic_tags": []},
            {"therapeutic_value": 0.8, "therapeutic_tags": []},
        ]
        uc = _make_choice(therapeutic_value=0.8)
        patterns = await tracker._identify_growth_patterns(
            uc, _make_session(choice_history=history)
        )
        assert "increasing_therapeutic_engagement" in patterns

    async def test_high_value_choice_detected(self, tracker):
        uc = _make_choice(therapeutic_value=0.85)
        patterns = await tracker._identify_growth_patterns(uc, _make_session())
        assert "high_therapeutic_engagement" in patterns

    async def test_expanding_skill_variety_detected(self, tracker):
        history = [
            {"therapeutic_tags": ["a", "b"]},
            {"therapeutic_tags": ["c", "d"]},
            {"therapeutic_tags": ["e"]},
            {"therapeutic_tags": ["f"]},
            {"therapeutic_tags": ["g"]},
        ]
        uc = _make_choice()
        patterns = await tracker._identify_growth_patterns(
            uc, _make_session(choice_history=history)
        )
        assert "expanding_skill_variety" in patterns

    async def test_low_value_no_high_engagement_pattern(self, tracker):
        uc = _make_choice(therapeutic_value=0.5)
        patterns = await tracker._identify_growth_patterns(uc, _make_session())
        assert "high_therapeutic_engagement" not in patterns


# ---------------------------------------------------------------------------
# ProgressTracker — _check_milestone_achievements
# ---------------------------------------------------------------------------


class TestCheckMilestoneAchievements:
    async def test_first_therapeutic_choice_milestone(self, tracker):
        history = [{"choice_type": "therapeutic", "therapeutic_tags": []}]
        uc = _make_choice()
        milestones = await tracker._check_milestone_achievements(
            uc, _make_session(choice_history=history)
        )
        assert "first_therapeutic_choice" in milestones

    async def test_high_value_milestone(self, tracker):
        uc = _make_choice(therapeutic_value=0.85)
        milestones = await tracker._check_milestone_achievements(uc, _make_session())
        assert "high_value_choice" in milestones

    async def test_consistent_engagement_milestone(self, tracker):
        history = (
            [{"choice_type": "therapeutic", "therapeutic_tags": []}] * 5
            + [{"choice_type": "narrative", "therapeutic_tags": []}] * 5
        )
        uc = _make_choice()
        milestones = await tracker._check_milestone_achievements(
            uc, _make_session(choice_history=history)
        )
        assert "consistent_engagement" in milestones

    async def test_no_milestone_for_low_value_first_choice(self, tracker):
        history = [{"choice_type": "narrative", "therapeutic_tags": []}]
        uc = _make_choice(therapeutic_value=0.4)
        milestones = await tracker._check_milestone_achievements(
            uc, _make_session(choice_history=history)
        )
        assert "first_therapeutic_choice" not in milestones


# ---------------------------------------------------------------------------
# ProgressTracker — _assess_therapeutic_gains
# ---------------------------------------------------------------------------


class TestAssessTherapeuticGains:
    async def test_high_value_significant_benefit(self, tracker):
        uc = _make_choice(therapeutic_value=0.9)
        gains = await tracker._assess_therapeutic_gains(uc, _make_outcomes())
        assert "significant_therapeutic_benefit" in gains

    async def test_moderate_value_moderate_benefit(self, tracker):
        uc = _make_choice(therapeutic_value=0.7)
        gains = await tracker._assess_therapeutic_gains(uc, _make_outcomes())
        assert "moderate_therapeutic_benefit" in gains

    async def test_low_value_no_benefit_label(self, tracker):
        uc = _make_choice(therapeutic_value=0.4)
        gains = await tracker._assess_therapeutic_gains(uc, _make_outcomes())
        assert "significant_therapeutic_benefit" not in gains
        assert "moderate_therapeutic_benefit" not in gains

    async def test_therapeutic_choice_type_adds_skill_practice(self, tracker):
        uc = _make_choice(choice_type=ChoiceType.THERAPEUTIC)
        gains = await tracker._assess_therapeutic_gains(uc, _make_outcomes())
        assert "therapeutic_skill_practice" in gains

    async def test_skill_building_type_adds_development_progress(self, tracker):
        uc = _make_choice(choice_type=ChoiceType.SKILL_BUILDING)
        gains = await tracker._assess_therapeutic_gains(uc, _make_outcomes())
        assert "skill_development_progress" in gains

    async def test_emotional_regulation_type_adds_regulation_practice(self, tracker):
        uc = _make_choice(choice_type=ChoiceType.EMOTIONAL_REGULATION)
        gains = await tracker._assess_therapeutic_gains(uc, _make_outcomes())
        assert "emotional_regulation_practice" in gains

    async def test_positive_emotion_outcome_adds_positive_emotional_outcome(
        self, tracker
    ):
        uc = _make_choice()
        gains = await tracker._assess_therapeutic_gains(
            uc, _make_outcomes(primary_emotion="positive")
        )
        assert "positive_emotional_outcome" in gains
