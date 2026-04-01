"""
Unit tests for NarrativeEngine and SceneGenerator.

All Neo4j / database dependencies are mocked via AsyncMock so no external
services are required.  The LLM path is exercised using a lightweight
AsyncMock that mimics langchain's response interface.
"""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Skip on Python 3.14 due to langchain_openai segfault in gameplay components
pytestmark = pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Gameplay components trigger langchain_openai segfault on Python 3.14",
)

if sys.version_info < (3, 14):
    from src.components.gameplay_loop.models.core import (
        DifficultyLevel,
        EmotionalState,
        Scene,
        SceneType,
        SessionState,
        TherapeuticContext,
    )
    from src.components.gameplay_loop.models.interactions import (
        ChoiceOutcome,
    )
    from src.components.gameplay_loop.narrative.scene_generator import (
        SceneGenerator,
    )
else:
    # Dummy imports for Python 3.14+
    _dummy = object()
    DifficultyLevel = SimpleNamespace(STANDARD=_dummy)  # type: ignore[misc,assignment]
    EmotionalState = SimpleNamespace(CALM=_dummy)  # type: ignore[misc,assignment]
    Scene = SimpleNamespace  # type: ignore[misc,assignment]
    SceneType = SimpleNamespace(THERAPEUTIC=_dummy)  # type: ignore[misc,assignment]
    SessionState = SimpleNamespace  # type: ignore[misc,assignment]
    TherapeuticContext = SimpleNamespace  # type: ignore[misc,assignment]
    ChoiceOutcome = SimpleNamespace  # type: ignore[misc,assignment]
    SceneGenerator = SimpleNamespace  # type: ignore[misc,assignment]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(
    emotional_state: EmotionalState = EmotionalState.CALM,
) -> SessionState:
    ss = SessionState(user_id="user-test")
    ss.emotional_state = emotional_state
    ss.therapeutic_context = TherapeuticContext()
    ss.difficulty_level = DifficultyLevel.STANDARD
    return ss


def _make_scene(scene_id: str = "scene-1") -> Scene:
    return Scene(
        scene_id=scene_id,
        title="Test Scene",
        description="A peaceful space.",
        narrative_content="The light is warm...",
        scene_type=SceneType.THERAPEUTIC,
    )


def _make_mock_db() -> AsyncMock:
    db = AsyncMock()
    db.initialize = AsyncMock(return_value=True)
    db.create_scene = AsyncMock(return_value=True)
    db.get_session = AsyncMock(return_value=None)
    return db


def _make_mock_llm(content: str = "You feel a gentle calm wash over you.") -> MagicMock:
    """Return a mock that behaves like a langchain BaseChatModel."""
    response = MagicMock()
    response.content = content
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=response)
    return llm


# ---------------------------------------------------------------------------
# Fixture: NarrativeEngine with mocked db
# ---------------------------------------------------------------------------


@pytest.fixture
async def engine():
    """NarrativeEngine with real sub-components and mocked DB, no LLM."""
    with patch(
        "src.components.gameplay_loop.narrative.engine.Neo4jGameplayManager",
        autospec=True,
    ) as MockDb:
        MockDb.return_value = _make_mock_db()
        from src.components.gameplay_loop.narrative.engine import NarrativeEngine

        eng = NarrativeEngine(db_manager=MockDb.return_value, llm=None)
        await eng.initialize()
        yield eng


@pytest.fixture
async def engine_with_llm():
    """NarrativeEngine with a mock LLM wired in."""
    with patch(
        "src.components.gameplay_loop.narrative.engine.Neo4jGameplayManager",
        autospec=True,
    ) as MockDb:
        MockDb.return_value = _make_mock_db()
        from src.components.gameplay_loop.narrative.engine import NarrativeEngine

        mock_llm = _make_mock_llm()
        eng = NarrativeEngine(db_manager=MockDb.return_value, llm=mock_llm)
        await eng.initialize()
        eng._mock_llm = mock_llm  # Expose for assertions
        yield eng


# ---------------------------------------------------------------------------
# SceneGenerator — standalone
# ---------------------------------------------------------------------------


class TestSceneGeneratorInit:
    async def test_initialize_returns_true(self):
        """Scene Generator Init: initialize returns true."""
        sg = SceneGenerator()
        result = await sg.initialize()
        assert result is True

    async def test_templates_populated_for_all_scene_types(self):
        """Scene Generator Init: templates populated for all scene types."""
        sg = SceneGenerator()
        await sg.initialize()
        for scene_type in SceneType:
            assert scene_type in sg.scene_templates

    async def test_therapeutic_settings_populated(self):
        """Scene Generator Init: therapeutic settings populated."""
        sg = SceneGenerator()
        await sg.initialize()
        assert len(sg.therapeutic_settings) > 0

    async def test_narrative_patterns_populated(self):
        """Scene Generator Init: narrative patterns populated."""
        sg = SceneGenerator()
        await sg.initialize()
        assert len(sg.narrative_patterns) > 0

    async def test_llm_none_by_default(self):
        """Scene Generator Init: llm none by default."""
        sg = SceneGenerator()
        assert sg.llm is None

    async def test_llm_stored_when_provided(self):
        """Scene Generator Init: llm stored when provided."""
        mock_llm = _make_mock_llm()
        sg = SceneGenerator(llm=mock_llm)
        assert sg.llm is mock_llm


class TestSceneGeneratorGenerateTherapeuticScene:
    async def test_returns_scene(self):
        """Scene Generator Generate Therapeutic Scene: returns scene."""
        sg = SceneGenerator()
        await sg.initialize()
        scene = await sg.generate_therapeutic_scene(
            scene_type=SceneType.INTRODUCTION,
            therapeutic_focus=["mindfulness"],
        )
        assert isinstance(scene, Scene)

    async def test_scene_type_matches(self):
        """Scene Generator Generate Therapeutic Scene: scene type matches."""
        sg = SceneGenerator()
        await sg.initialize()
        scene = await sg.generate_therapeutic_scene(
            scene_type=SceneType.EXPLORATION,
            therapeutic_focus=[],
        )
        assert scene is not None
        assert scene.scene_type == SceneType.EXPLORATION

    async def test_difficulty_level_respected(self):
        """Scene Generator Generate Therapeutic Scene: difficulty level respected."""
        sg = SceneGenerator()
        await sg.initialize()
        scene = await sg.generate_therapeutic_scene(
            scene_type=SceneType.THERAPEUTIC,
            therapeutic_focus=["mindfulness"],
            difficulty_level=DifficultyLevel.GENTLE,
        )
        assert scene is not None
        assert scene.difficulty_level == DifficultyLevel.GENTLE

    async def test_returns_none_without_templates(self):
        """Scene Generator Generate Therapeutic Scene: returns none without templates."""
        sg = SceneGenerator()
        await sg.initialize()
        sg.scene_templates = {}
        scene = await sg.generate_therapeutic_scene(
            scene_type=SceneType.INTRODUCTION,
            therapeutic_focus=[],
        )
        assert scene is None

    async def test_all_scene_types_produce_scene(self):
        """Scene Generator Generate Therapeutic Scene: all scene types produce scene."""
        sg = SceneGenerator()
        await sg.initialize()
        for scene_type in SceneType:
            scene = await sg.generate_therapeutic_scene(
                scene_type=scene_type,
                therapeutic_focus=[],
            )
            assert isinstance(scene, Scene), f"No scene for {scene_type}"

    async def test_llm_called_when_provided(self):
        """Scene Generator Generate Therapeutic Scene: llm called when provided."""
        mock_llm = _make_mock_llm("You find yourself in a sunlit clearing.")
        sg = SceneGenerator(llm=mock_llm)
        await sg.initialize()
        scene = await sg.generate_therapeutic_scene(
            scene_type=SceneType.INTRODUCTION,
            therapeutic_focus=["mindfulness"],
        )
        assert scene is not None
        mock_llm.ainvoke.assert_called_once()

    async def test_llm_failure_falls_back_to_template(self):
        """Scene Generator Generate Therapeutic Scene: llm failure falls back to template."""
        mock_llm = _make_mock_llm()
        mock_llm.ainvoke = AsyncMock(side_effect=RuntimeError("LLM down"))
        sg = SceneGenerator(llm=mock_llm)
        await sg.initialize()
        scene = await sg.generate_therapeutic_scene(
            scene_type=SceneType.INTRODUCTION,
            therapeutic_focus=["mindfulness"],
        )
        # Should still produce a scene from template fallback
        assert isinstance(scene, Scene)


class TestSceneGeneratorGenerateInterventionScene:
    async def test_returns_scene(self):
        """Scene Generator Generate Intervention Scene: returns scene."""
        sg = SceneGenerator()
        await sg.initialize()
        tc = TherapeuticContext()
        scene = await sg.generate_intervention_scene(
            intervention_type="grounding",
            emotional_state="anxious",
            therapeutic_context=tc,
            difficulty_level=DifficultyLevel.GENTLE,
        )
        assert isinstance(scene, Scene)

    async def test_scene_is_always_gentle(self):
        """Scene Generator Generate Intervention Scene: scene is always gentle."""
        sg = SceneGenerator()
        await sg.initialize()
        tc = TherapeuticContext()
        scene = await sg.generate_intervention_scene(
            intervention_type="mindfulness",
            emotional_state="overwhelmed",
            therapeutic_context=tc,
            difficulty_level=DifficultyLevel.CHALLENGING,
        )
        assert scene is not None
        assert scene.difficulty_level == DifficultyLevel.GENTLE

    async def test_scene_type_is_therapeutic(self):
        """Scene Generator Generate Intervention Scene: scene type is therapeutic."""
        sg = SceneGenerator()
        await sg.initialize()
        tc = TherapeuticContext()
        scene = await sg.generate_intervention_scene(
            intervention_type="grounding",
            emotional_state="calm",
            therapeutic_context=tc,
            difficulty_level=DifficultyLevel.STANDARD,
        )
        assert scene is not None
        assert scene.scene_type == SceneType.THERAPEUTIC


# ---------------------------------------------------------------------------
# NarrativeEngine — initialization
# ---------------------------------------------------------------------------


class TestNarrativeEngineInit:
    async def test_initialize_returns_true(self, engine):
        """Narrative Engine Init: initialize returns true."""
        result = await engine.initialize()
        assert result is True

    async def test_scene_generator_ready(self, engine):
        """Narrative Engine Init: scene generator ready."""
        assert engine.scene_generator is not None

    async def test_llm_none_by_default(self, engine):
        """Narrative Engine Init: llm none by default."""
        assert engine._llm is None

    async def test_llm_stored_when_provided(self, engine_with_llm):
        """Narrative Engine Init: llm stored when provided."""
        assert engine_with_llm._llm is not None


# ---------------------------------------------------------------------------
# NarrativeEngine — generate_opening_scene
# ---------------------------------------------------------------------------


class TestGenerateOpeningScene:
    async def test_returns_scene(self, engine):
        """Generate Opening Scene: returns scene."""
        session = _make_session()
        scene = await engine.generate_opening_scene(session)
        assert isinstance(scene, Scene)

    async def test_scene_cached_in_memory(self, engine):
        """Generate Opening Scene: scene cached in memory."""
        session = _make_session()
        scene = await engine.generate_opening_scene(session)
        assert scene is not None
        assert scene.scene_id in engine._scene_cache

    async def test_db_create_scene_called(self, engine):
        """Generate Opening Scene: db create scene called."""
        session = _make_session()
        await engine.generate_opening_scene(session)
        engine.db_manager.create_scene.assert_called()

    async def test_returns_none_when_no_template(self, engine):
        """Generate Opening Scene: returns none when no template."""
        engine.scene_generator.scene_templates = {}
        session = _make_session()
        scene = await engine.generate_opening_scene(session)
        assert scene is None

    async def test_anxious_state_uses_calm_setting(self, engine):
        """Generate Opening Scene: anxious state uses calm setting."""
        session = _make_session(EmotionalState.ANXIOUS)
        scene = await engine.generate_opening_scene(session)
        # Should still return a valid scene (calming path)
        assert isinstance(scene, Scene)

    async def test_distressed_state_returns_scene(self, engine):
        """Generate Opening Scene: distressed state returns scene."""
        session = _make_session(EmotionalState.DISTRESSED)
        scene = await engine.generate_opening_scene(session)
        assert isinstance(scene, Scene)

    async def test_opening_scene_is_introduction_type(self, engine):
        """Generate Opening Scene: opening scene is introduction type."""
        session = _make_session()
        scene = await engine.generate_opening_scene(session)
        assert scene is not None
        assert scene.scene_type == SceneType.INTRODUCTION

    async def test_db_failure_still_returns_scene(self, engine):
        """Generate Opening Scene: db failure still returns scene."""
        engine.db_manager.create_scene = AsyncMock(return_value=False)
        session = _make_session()
        scene = await engine.generate_opening_scene(session)
        assert isinstance(scene, Scene)


# ---------------------------------------------------------------------------
# NarrativeEngine — generate_next_scene
# ---------------------------------------------------------------------------


class TestGenerateNextScene:
    async def test_returns_scene(self, engine):
        """Generate Next Scene: returns scene."""
        session = _make_session()
        scene = await engine.generate_next_scene(session)
        assert isinstance(scene, Scene)

    async def test_scene_cached_after_generation(self, engine):
        """Generate Next Scene: scene cached after generation."""
        session = _make_session()
        scene = await engine.generate_next_scene(session)
        assert scene is not None
        assert scene.scene_id in engine._scene_cache

    async def test_no_previous_choice_returns_exploration(self, engine):
        """Generate Next Scene: no previous choice returns exploration."""
        session = _make_session()
        scene = await engine.generate_next_scene(session, previous_choice=None)
        assert scene is not None
        assert scene.scene_type == SceneType.EXPLORATION

    async def test_returns_none_when_scene_generator_empty(self, engine):
        """Generate Next Scene: returns none when scene generator empty."""
        engine.scene_generator.scene_templates = {}
        session = _make_session()
        scene = await engine.generate_next_scene(session)
        assert scene is None


# ---------------------------------------------------------------------------
# NarrativeEngine — adapt_scene_for_emotional_state
# ---------------------------------------------------------------------------


class TestAdaptSceneForEmotionalState:
    async def test_returns_scene(self, engine):
        """Adapt Scene For Emotional State: returns scene."""
        session = _make_session()
        scene = _make_scene()
        adapted = await engine.adapt_scene_for_emotional_state(
            scene, EmotionalState.ANXIOUS, session
        )
        assert isinstance(adapted, Scene)

    async def test_adapted_scene_has_new_id(self, engine):
        """Adapt Scene For Emotional State: adapted scene has new id."""
        session = _make_session()
        scene = _make_scene()
        adapted = await engine.adapt_scene_for_emotional_state(
            scene, EmotionalState.ANXIOUS, session
        )
        assert adapted.scene_id != scene.scene_id

    async def test_crisis_adapts_scene_type(self, engine):
        """Adapt Scene For Emotional State: crisis adapts scene type."""
        session = _make_session()
        scene = _make_scene()
        scene.scene_type = SceneType.EXPLORATION
        adapted = await engine.adapt_scene_for_emotional_state(
            scene, EmotionalState.CRISIS, session
        )
        assert adapted.scene_type == SceneType.THERAPEUTIC
        assert adapted.difficulty_level == DifficultyLevel.GENTLE

    async def test_anxious_adds_calming_content(self, engine):
        """Adapt Scene For Emotional State: anxious adds calming content."""
        session = _make_session()
        scene = _make_scene()
        original_content = scene.narrative_content
        adapted = await engine.adapt_scene_for_emotional_state(
            scene, EmotionalState.ANXIOUS, session
        )
        assert len(adapted.narrative_content) >= len(original_content)

    async def test_distressed_adds_grounding_content(self, engine):
        """Adapt Scene For Emotional State: distressed adds grounding content."""
        session = _make_session()
        scene = _make_scene()
        adapted = await engine.adapt_scene_for_emotional_state(
            scene, EmotionalState.DISTRESSED, session
        )
        assert "ground" in adapted.narrative_content.lower()

    async def test_calm_state_returns_valid_scene(self, engine):
        """Adapt Scene For Emotional State: calm state returns valid scene."""
        session = _make_session(EmotionalState.CALM)
        scene = _make_scene()
        adapted = await engine.adapt_scene_for_emotional_state(
            scene, EmotionalState.CALM, session
        )
        assert isinstance(adapted, Scene)

    async def test_returns_original_on_exception(self, engine):
        """Adapt Scene For Emotional State: returns original on exception."""
        session = _make_session()
        scene = _make_scene()
        # Break therapeutic_storyteller to force exception path
        engine.therapeutic_storyteller.enhance_scene_with_therapy = AsyncMock(
            side_effect=RuntimeError("oops")
        )
        result = await engine.adapt_scene_for_emotional_state(
            scene, EmotionalState.ANXIOUS, session
        )
        # Returns original scene on failure
        assert result is scene


# ---------------------------------------------------------------------------
# NarrativeEngine — _determine_emotional_tone
# ---------------------------------------------------------------------------


class TestDetermineEmotionalTone:
    def test_none_outcome_returns_neutral(self, engine):
        """Determine Emotional Tone: none outcome returns neutral."""
        tone = engine._determine_emotional_tone(None)
        assert tone == "neutral"

    def test_success_outcome_returns_encouraging(self, engine):
        """Determine Emotional Tone: success outcome returns encouraging."""
        outcome = ChoiceOutcome(
            choice_id="c1",
            outcome_type="success",
            therapeutic_impact={},
            narrative_consequences=[],
            learning_opportunities=[],
            emotional_response="positive",
            skill_development=[],
            progress_markers=[],
        )
        assert engine._determine_emotional_tone(outcome) == "encouraging"

    def test_failure_outcome_returns_compassionate(self, engine):
        """Determine Emotional Tone: failure outcome returns compassionate."""
        outcome = ChoiceOutcome(
            choice_id="c1",
            outcome_type="failure",
            therapeutic_impact={},
            narrative_consequences=[],
            learning_opportunities=[],
            emotional_response="negative",
            skill_development=[],
            progress_markers=[],
        )
        assert engine._determine_emotional_tone(outcome) == "compassionate"

    def test_unknown_outcome_returns_neutral(self, engine):
        """Determine Emotional Tone: unknown outcome returns neutral."""
        outcome = ChoiceOutcome(
            choice_id="c1",
            outcome_type="unknown_type",
            therapeutic_impact={},
            narrative_consequences=[],
            learning_opportunities=[],
            emotional_response="neutral",
            skill_development=[],
            progress_markers=[],
        )
        assert engine._determine_emotional_tone(outcome) == "neutral"


# ---------------------------------------------------------------------------
# NarrativeEngine — LLM path (engine_with_llm fixture)
# ---------------------------------------------------------------------------


class TestNarrativeEngineLLM:
    async def test_opening_scene_uses_llm(self, engine_with_llm):
        """Narrative Engine L L M: opening scene uses llm."""
        session = _make_session()
        scene = await engine_with_llm.generate_opening_scene(session)
        assert isinstance(scene, Scene)
        engine_with_llm._mock_llm.ainvoke.assert_called()

    async def test_llm_failure_falls_back_gracefully(self, engine_with_llm):
        """Narrative Engine L L M: llm failure falls back gracefully."""
        engine_with_llm._mock_llm.ainvoke = AsyncMock(
            side_effect=RuntimeError("LLM unavailable")
        )
        session = _make_session()
        scene = await engine_with_llm.generate_opening_scene(session)
        # Template fallback should still produce a scene
        assert isinstance(scene, Scene)
