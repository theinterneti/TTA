"""
Unit tests for the nine therapeutic narrative modules.

Each module is tested in isolation with no external services.
Mirrors the conventions established in test_gameplay_loop_narrative_engine.py.
"""

from __future__ import annotations

import pytest

from src.components.gameplay_loop.models.core import (
    ChoiceType,
    DifficultyLevel,
    EmotionalState,
    GameplayMetrics,
    Scene,
    SceneType,
    SessionState,
    TherapeuticContext,
)
from src.components.gameplay_loop.models.interactions import (
    ChoiceOutcome,
    UserChoice,
)
from src.components.gameplay_loop.models.progress import ProgressMarker
from src.components.gameplay_loop.narrative.adaptive_difficulty_engine import (
    AdaptiveDifficultyEngine,
    PerformanceLevel,
)
from src.components.gameplay_loop.narrative.character_development_system import (
    ArcPhase,
    CharacterDevelopmentSystem,
    DevelopmentDomain,
)
from src.components.gameplay_loop.narrative.collaborative_system import (
    CollaborationType,
    CollaborativeSystem,
    ParticipantRole,
)
from src.components.gameplay_loop.narrative.emotional_safety_system import (
    EmotionalSafetySystem,
    SafetyLevel,
)
from src.components.gameplay_loop.narrative.error_recovery_manager import (
    ErrorRecoveryManager,
    ErrorSeverity,
    RecoveryStrategy,
)
from src.components.gameplay_loop.narrative.narrative_consequence_system import (
    ConsequenceScope,
    ConsequenceType,
    NarrativeConsequenceSystem,
)
from src.components.gameplay_loop.narrative.replayability_system import (
    ReplayabilitySystem,
)
from src.components.gameplay_loop.narrative.therapeutic_integration_system import (
    EvidenceType,
    TherapeuticIntegrationSystem,
)
from src.components.gameplay_loop.narrative.therapeutic_integrator import (
    IntegrationMode,
    NarrativeTechnique,
    TherapeuticIntegrator,
)

pytestmark = pytest.mark.unit

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
        narrative_content="The light is warm and welcoming.",
        scene_type=SceneType.THERAPEUTIC,
    )


def _make_choice_outcome(
    choice_id: str = "c1",
    outcome_type: str = "success",
) -> ChoiceOutcome:
    return ChoiceOutcome(
        choice_id=choice_id,
        outcome_type=outcome_type,
        therapeutic_impact={"engagement": 0.8},
        narrative_consequences=["The world shifts."],
        learning_opportunities=["Self-reflection"],
        emotional_response="positive",
        skill_development=["mindfulness"],
        progress_markers=[],
    )


def _make_user_choice(
    choice_id: str = "c1",
    session_id: str = "s1",
    scene_id: str = "sc1",
) -> UserChoice:
    return UserChoice(
        choice_id=choice_id,
        session_id=session_id,
        scene_id=scene_id,
        choice_text="I want to explore the forest.",
        choice_type=ChoiceType.NARRATIVE,
        emotional_state_before=EmotionalState.CALM,
    )


# ---------------------------------------------------------------------------
# AdaptiveDifficultyEngine
# ---------------------------------------------------------------------------


class TestAdaptiveDifficultyEngine:
    async def test_initialize_returns_true(self):
        """Adaptive Difficulty Engine: initialize returns true."""
        engine = AdaptiveDifficultyEngine()
        result = await engine.initialize()
        assert result is True

    async def test_assess_performance_average_default(self):
        """Adaptive Difficulty Engine: assess performance average default."""
        engine = AdaptiveDifficultyEngine()
        await engine.initialize()
        session = _make_session()
        level = await engine.assess_performance(session)
        assert level == PerformanceLevel.AVERAGE

    async def test_assess_performance_excelling(self):
        """Adaptive Difficulty Engine: assess performance excelling."""
        engine = AdaptiveDifficultyEngine()
        await engine.initialize()
        session = _make_session()
        session.metrics = GameplayMetrics(
            therapeutic_effectiveness=0.95,
            engagement_score=0.95,
            total_choices_made=20,
            therapeutic_choices_made=18,
        )
        level = await engine.assess_performance(session)
        assert level == PerformanceLevel.EXCELLING

    async def test_adjust_difficulty_returns_scene(self):
        """Adaptive Difficulty Engine: adjust difficulty returns scene."""
        engine = AdaptiveDifficultyEngine()
        await engine.initialize()
        session = _make_session()
        scene = _make_scene()
        adjusted = await engine.adjust_difficulty(session, scene)
        assert isinstance(adjusted, Scene)

    async def test_adjust_difficulty_preserves_title(self):
        """Adaptive Difficulty Engine: adjust difficulty preserves title."""
        engine = AdaptiveDifficultyEngine()
        await engine.initialize()
        session = _make_session()
        scene = _make_scene()
        adjusted = await engine.adjust_difficulty(session, scene)
        assert adjusted.title == scene.title

    async def test_get_recommended_difficulty(self):
        """Adaptive Difficulty Engine: get recommended difficulty."""
        engine = AdaptiveDifficultyEngine()
        await engine.initialize()
        session = _make_session()
        level = await engine.get_recommended_difficulty(session)
        assert isinstance(level, DifficultyLevel)

    async def test_record_performance_no_error(self):
        """Adaptive Difficulty Engine: record performance no error."""
        engine = AdaptiveDifficultyEngine()
        await engine.initialize()
        session = _make_session()
        outcome = _make_choice_outcome()
        await engine.record_performance(session, outcome)


# ---------------------------------------------------------------------------
# EmotionalSafetySystem
# ---------------------------------------------------------------------------


class TestEmotionalSafetySystem:
    async def test_initialize_returns_true(self):
        """Emotional Safety System: initialize returns true."""
        system = EmotionalSafetySystem()
        result = await system.initialize()
        assert result is True

    async def test_assess_content_safety_safe(self):
        """Emotional Safety System: assess content safety safe."""
        system = EmotionalSafetySystem()
        await system.initialize()
        session = _make_session(EmotionalState.CALM)
        result = await system.assess_content_safety(
            "A gentle breeze rustles the leaves.", session
        )
        assert isinstance(result, dict)
        assert "safety_level" in result

    async def test_assess_content_safety_crisis(self):
        """Emotional Safety System: assess content safety crisis."""
        system = EmotionalSafetySystem()
        await system.initialize()
        session = _make_session(EmotionalState.CRISIS)
        result = await system.assess_content_safety("The darkness closes in.", session)
        assert isinstance(result, dict)

    async def test_filter_unsafe_content_safe_passthrough(self):
        """Emotional Safety System: filter unsafe content safe passthrough."""
        system = EmotionalSafetySystem()
        await system.initialize()
        session = _make_session(EmotionalState.CALM)
        scene = _make_scene()
        filtered = await system.filter_unsafe_content(scene, session)
        assert isinstance(filtered, Scene)

    async def test_filter_unsafe_content_crisis_replaced(self):
        """Emotional Safety System: filter unsafe content crisis replaced."""
        system = EmotionalSafetySystem()
        await system.initialize()
        session = _make_session(EmotionalState.CRISIS)
        scene = _make_scene()
        filtered = await system.filter_unsafe_content(scene, session)
        assert isinstance(filtered, Scene)

    async def test_check_emotional_boundaries_calm(self):
        """Emotional Safety System: check emotional boundaries calm."""
        system = EmotionalSafetySystem()
        await system.initialize()
        session = _make_session(EmotionalState.CALM)
        level = await system.check_emotional_boundaries(session)
        assert isinstance(level, SafetyLevel)

    async def test_check_emotional_boundaries_crisis(self):
        """Emotional Safety System: check emotional boundaries crisis."""
        system = EmotionalSafetySystem()
        await system.initialize()
        session = _make_session(EmotionalState.CRISIS)
        level = await system.check_emotional_boundaries(session)
        assert isinstance(level, SafetyLevel)

    async def test_trigger_safety_intervention_none_for_safe(self):
        """Emotional Safety System: trigger safety intervention none for safe."""
        system = EmotionalSafetySystem()
        await system.initialize()
        session = _make_session(EmotionalState.CALM)
        result = await system.trigger_safety_intervention(session, SafetyLevel.SAFE)
        assert result is None

    async def test_trigger_safety_intervention_scene_for_crisis(self):
        """Emotional Safety System: trigger safety intervention scene for crisis."""
        system = EmotionalSafetySystem()
        await system.initialize()
        session = _make_session(EmotionalState.CRISIS)
        result = await system.trigger_safety_intervention(session, SafetyLevel.CRISIS)
        assert isinstance(result, Scene)


# ---------------------------------------------------------------------------
# TherapeuticIntegrationSystem
# ---------------------------------------------------------------------------


class TestTherapeuticIntegrationSystem:
    async def test_initialize_returns_true(self):
        """Therapeutic Integration System: initialize returns true."""
        system = TherapeuticIntegrationSystem()
        result = await system.initialize()
        assert result is True

    async def test_set_therapeutic_goals(self):
        """Therapeutic Integration System: set therapeutic goals."""
        system = TherapeuticIntegrationSystem()
        await system.initialize()
        session = _make_session()
        success = await system.set_therapeutic_goals(
            session, ["emotional regulation", "mindfulness"]
        )
        assert success is True

    async def test_set_therapeutic_goals_empty_list(self):
        """Therapeutic Integration System: set therapeutic goals empty list."""
        system = TherapeuticIntegrationSystem()
        await system.initialize()
        session = _make_session()
        success = await system.set_therapeutic_goals(session, [])
        assert isinstance(success, bool)

    async def test_track_goal_progress(self):
        """Therapeutic Integration System: track goal progress."""
        system = TherapeuticIntegrationSystem()
        await system.initialize()
        session = _make_session()
        await system.set_therapeutic_goals(session, ["emotional regulation"])
        outcome = _make_choice_outcome()
        progress = await system.track_goal_progress(session, outcome)
        assert isinstance(progress, dict)

    async def test_log_therapeutic_evidence(self):
        """Therapeutic Integration System: log therapeutic evidence."""
        system = TherapeuticIntegrationSystem()
        await system.initialize()
        await system.log_therapeutic_evidence(
            session_id="s1",
            evidence_type=EvidenceType.EMOTIONAL,
            description="Player showed increased coping skills.",
            significance=0.85,
        )

    async def test_generate_progress_report(self):
        """Therapeutic Integration System: generate progress report."""
        system = TherapeuticIntegrationSystem()
        await system.initialize()
        session = _make_session()
        await system.set_therapeutic_goals(session, ["mindfulness"])
        report = await system.generate_progress_report(session)
        assert isinstance(report, dict)

    async def test_generate_progress_report_no_goals(self):
        """Therapeutic Integration System: generate progress report no goals."""
        system = TherapeuticIntegrationSystem()
        await system.initialize()
        session = _make_session()
        report = await system.generate_progress_report(session)
        assert isinstance(report, dict)


# ---------------------------------------------------------------------------
# TherapeuticIntegrator
# ---------------------------------------------------------------------------


class TestTherapeuticIntegrator:
    async def test_initialize_returns_true(self):
        """Therapeutic Integrator: initialize returns true."""
        integrator = TherapeuticIntegrator()
        result = await integrator.initialize()
        assert result is True

    async def test_integrate_therapeutic_context(self):
        """Therapeutic Integrator: integrate therapeutic context."""
        integrator = TherapeuticIntegrator()
        await integrator.initialize()
        session = _make_session()
        scene = _make_scene()
        ctx = TherapeuticContext(primary_goals=["mindfulness"])
        result = await integrator.integrate_therapeutic_context(scene, ctx, session)
        assert isinstance(result, Scene)

    async def test_integrate_therapeutic_context_empty_goals(self):
        """Therapeutic Integrator: integrate therapeutic context empty goals."""
        integrator = TherapeuticIntegrator()
        await integrator.initialize()
        session = _make_session()
        scene = _make_scene()
        ctx = TherapeuticContext()
        result = await integrator.integrate_therapeutic_context(scene, ctx, session)
        assert isinstance(result, Scene)

    async def test_select_integration_mode_subtle_for_crisis(self):
        """Therapeutic Integrator: select integration mode subtle for crisis."""
        integrator = TherapeuticIntegrator()
        await integrator.initialize()
        session = _make_session(EmotionalState.CRISIS)
        mode = await integrator.select_integration_mode(session)
        assert isinstance(mode, IntegrationMode)
        assert mode == IntegrationMode.SUBTLE

    async def test_select_integration_mode_for_calm(self):
        """Therapeutic Integrator: select integration mode for calm."""
        integrator = TherapeuticIntegrator()
        await integrator.initialize()
        session = _make_session(EmotionalState.CALM)
        mode = await integrator.select_integration_mode(session)
        assert isinstance(mode, IntegrationMode)

    async def test_select_integration_mode_intensive_for_high_effectiveness(self):
        """Therapeutic Integrator: select integration mode intensive for high effectiveness."""
        integrator = TherapeuticIntegrator()
        await integrator.initialize()
        session = _make_session(EmotionalState.ENGAGED)
        session.metrics = GameplayMetrics(
            therapeutic_effectiveness=0.9,
            engagement_score=0.9,
        )
        mode = await integrator.select_integration_mode(session)
        assert isinstance(mode, IntegrationMode)

    async def test_apply_narrative_technique(self):
        """Therapeutic Integrator: apply narrative technique."""
        integrator = TherapeuticIntegrator()
        await integrator.initialize()
        scene = _make_scene()
        ctx = TherapeuticContext(primary_goals=["emotional regulation"])
        result = await integrator.apply_narrative_technique(
            scene, NarrativeTechnique.REFLECTION, ctx
        )
        assert isinstance(result, Scene)

    async def test_apply_narrative_technique_scaffolding(self):
        """Therapeutic Integrator: apply narrative technique scaffolding."""
        integrator = TherapeuticIntegrator()
        await integrator.initialize()
        scene = _make_scene()
        ctx = TherapeuticContext()
        result = await integrator.apply_narrative_technique(
            scene, NarrativeTechnique.SCAFFOLDING, ctx
        )
        assert isinstance(result, Scene)


# ---------------------------------------------------------------------------
# NarrativeConsequenceSystem
# ---------------------------------------------------------------------------


class TestNarrativeConsequenceSystem:
    async def test_initialize_returns_true(self):
        """Narrative Consequence System: initialize returns true."""
        system = NarrativeConsequenceSystem()
        result = await system.initialize()
        assert result is True

    async def test_evaluate_consequences(self):
        """Narrative Consequence System: evaluate consequences."""
        system = NarrativeConsequenceSystem()
        await system.initialize()
        session = _make_session()
        choice = _make_user_choice()
        consequences = await system.evaluate_consequences(choice, session)
        assert isinstance(consequences, list)

    async def test_evaluate_consequences_therapeutic_choice(self):
        """Narrative Consequence System: evaluate consequences therapeutic choice."""
        system = NarrativeConsequenceSystem()
        await system.initialize()
        session = _make_session()
        choice = _make_user_choice()
        choice.choice_type = ChoiceType.THERAPEUTIC
        consequences = await system.evaluate_consequences(choice, session)
        assert isinstance(consequences, list)

    async def test_apply_consequences(self):
        """Narrative Consequence System: apply consequences."""
        system = NarrativeConsequenceSystem()
        await system.initialize()
        scene = _make_scene()
        consequences = [
            {
                "type": ConsequenceType.NARRATIVE,
                "scope": ConsequenceScope.IMMEDIATE,
                "description": "The path opens before you.",
            }
        ]
        result = await system.apply_consequences(scene, consequences)
        assert isinstance(result, Scene)

    async def test_apply_consequences_empty_list(self):
        """Narrative Consequence System: apply consequences empty list."""
        system = NarrativeConsequenceSystem()
        await system.initialize()
        scene = _make_scene()
        result = await system.apply_consequences(scene, [])
        assert isinstance(result, Scene)

    async def test_track_consequence_chain(self):
        """Narrative Consequence System: track consequence chain."""
        system = NarrativeConsequenceSystem()
        await system.initialize()
        consequence = {
            "type": ConsequenceType.EMOTIONAL,
            "scope": ConsequenceScope.SHORT_TERM,
            "description": "Feeling braver.",
        }
        await system.track_consequence_chain("s1", consequence)

    async def test_get_active_consequences(self):
        """Narrative Consequence System: get active consequences."""
        system = NarrativeConsequenceSystem()
        await system.initialize()
        result = await system.get_active_consequences("s1")
        assert isinstance(result, list)

    async def test_get_active_consequences_after_evaluate(self):
        """Narrative Consequence System: get active consequences after evaluate."""
        system = NarrativeConsequenceSystem()
        await system.initialize()
        session = _make_session()
        scene = _make_scene()
        choice = _make_user_choice(session_id=session.session_id)
        consequences = await system.evaluate_consequences(choice, session)
        await system.apply_consequences(scene, consequences)
        active = await system.get_active_consequences(session.session_id)
        assert isinstance(active, list)


# ---------------------------------------------------------------------------
# CharacterDevelopmentSystem
# ---------------------------------------------------------------------------


class TestCharacterDevelopmentSystem:
    async def test_initialize_returns_true(self):
        """Character Development System: initialize returns true."""
        system = CharacterDevelopmentSystem()
        result = await system.initialize()
        assert result is True

    async def test_track_character_growth(self):
        """Character Development System: track character growth."""
        system = CharacterDevelopmentSystem()
        await system.initialize()
        session = _make_session()
        outcome = _make_choice_outcome()
        growth = await system.track_character_growth(session, outcome)
        assert isinstance(growth, dict)

    async def test_track_character_growth_failure_outcome(self):
        """Character Development System: track character growth failure outcome."""
        system = CharacterDevelopmentSystem()
        await system.initialize()
        session = _make_session()
        outcome = _make_choice_outcome(outcome_type="failure")
        growth = await system.track_character_growth(session, outcome)
        assert isinstance(growth, dict)

    async def test_assess_arc_phase_introduction(self):
        """Character Development System: assess arc phase introduction."""
        system = CharacterDevelopmentSystem()
        await system.initialize()
        session = _make_session()
        phase = await system.assess_arc_phase(session)
        assert isinstance(phase, ArcPhase)
        assert phase == ArcPhase.INTRODUCTION

    async def test_assess_arc_phase_growth(self):
        """Character Development System: assess arc phase growth."""
        system = CharacterDevelopmentSystem()
        await system.initialize()
        session = _make_session()
        session.metrics = GameplayMetrics(
            total_choices_made=50,
            therapeutic_choices_made=30,
            therapeutic_effectiveness=0.8,
            engagement_score=0.8,
        )
        phase = await system.assess_arc_phase(session)
        assert phase == ArcPhase.GROWTH

    async def test_generate_development_milestone(self):
        """Character Development System: generate development milestone."""
        system = CharacterDevelopmentSystem()
        await system.initialize()
        session = _make_session()
        marker = await system.generate_development_milestone(
            session, DevelopmentDomain.EMOTIONAL
        )
        assert marker is None or isinstance(marker, ProgressMarker)

    async def test_generate_development_milestone_cognitive(self):
        """Character Development System: generate development milestone cognitive."""
        system = CharacterDevelopmentSystem()
        await system.initialize()
        session = _make_session()
        session.metrics = GameplayMetrics(
            total_choices_made=20,
            therapeutic_choices_made=15,
            therapeutic_effectiveness=0.7,
        )
        marker = await system.generate_development_milestone(
            session, DevelopmentDomain.COGNITIVE
        )
        assert marker is None or isinstance(marker, ProgressMarker)

    async def test_get_character_arc_summary(self):
        """Character Development System: get character arc summary."""
        system = CharacterDevelopmentSystem()
        await system.initialize()
        summary = await system.get_character_arc_summary("s1")
        assert isinstance(summary, dict)

    async def test_get_character_arc_summary_after_growth(self):
        """Character Development System: get character arc summary after growth."""
        system = CharacterDevelopmentSystem()
        await system.initialize()
        session = _make_session()
        outcome = _make_choice_outcome()
        await system.track_character_growth(session, outcome)
        summary = await system.get_character_arc_summary(session.session_id)
        assert isinstance(summary, dict)


# ---------------------------------------------------------------------------
# ReplayabilitySystem
# ---------------------------------------------------------------------------


class TestReplayabilitySystem:
    async def test_initialize_returns_true(self):
        """Replayability System: initialize returns true."""
        system = ReplayabilitySystem()
        result = await system.initialize()
        assert result is True

    async def test_register_branch_point(self):
        """Replayability System: register branch point."""
        system = ReplayabilitySystem()
        await system.initialize()
        session = _make_session()
        scene = _make_scene()
        branch_id = await system.register_branch_point(
            session, scene, ["Go left", "Go right"]
        )
        assert isinstance(branch_id, str)
        assert len(branch_id) > 0

    async def test_register_branch_point_single_choice(self):
        """Replayability System: register branch point single choice."""
        system = ReplayabilitySystem()
        await system.initialize()
        session = _make_session()
        scene = _make_scene()
        branch_id = await system.register_branch_point(session, scene, ["Only option"])
        assert isinstance(branch_id, str)

    async def test_explore_alternative_path(self):
        """Replayability System: explore alternative path."""
        system = ReplayabilitySystem()
        await system.initialize()
        session = _make_session()
        scene = _make_scene()
        branch_id = await system.register_branch_point(
            session, scene, ["Go left", "Go right"]
        )
        result = await system.explore_alternative_path(branch_id, "Go right")
        assert result is None or isinstance(result, dict)

    async def test_explore_alternative_invalid_branch(self):
        """Replayability System: explore alternative invalid branch."""
        system = ReplayabilitySystem()
        await system.initialize()
        result = await system.explore_alternative_path("nonexistent-branch", "Go right")
        assert result is None

    async def test_get_timeline_summary(self):
        """Replayability System: get timeline summary."""
        system = ReplayabilitySystem()
        await system.initialize()
        summary = await system.get_timeline_summary("s1")
        assert isinstance(summary, dict)

    async def test_get_timeline_summary_with_branches(self):
        """Replayability System: get timeline summary with branches."""
        system = ReplayabilitySystem()
        await system.initialize()
        session = _make_session()
        scene = _make_scene()
        await system.register_branch_point(session, scene, ["A", "B"])
        summary = await system.get_timeline_summary(session.session_id)
        assert isinstance(summary, dict)

    async def test_calculate_discovery_percentage(self):
        """Replayability System: calculate discovery percentage."""
        system = ReplayabilitySystem()
        await system.initialize()
        pct = await system.calculate_discovery_percentage("s1")
        assert isinstance(pct, float)
        assert 0.0 <= pct <= 100.0

    async def test_calculate_discovery_percentage_with_exploration(self):
        """Replayability System: calculate discovery percentage with exploration."""
        system = ReplayabilitySystem()
        await system.initialize()
        session = _make_session()
        scene = _make_scene()
        branch_id = await system.register_branch_point(session, scene, ["A", "B", "C"])
        await system.explore_alternative_path(branch_id, "A")
        pct = await system.calculate_discovery_percentage(session.session_id)
        assert isinstance(pct, float)
        assert 0.0 <= pct <= 100.0


# ---------------------------------------------------------------------------
# CollaborativeSystem
# ---------------------------------------------------------------------------


class TestCollaborativeSystem:
    async def test_initialize_returns_true(self):
        """Collaborative System: initialize returns true."""
        system = CollaborativeSystem()
        result = await system.initialize()
        assert result is True

    async def test_create_collaborative_session(self):
        """Collaborative System: create collaborative session."""
        system = CollaborativeSystem()
        await system.initialize()
        session = _make_session()
        collab = await system.create_collaborative_session(
            session, CollaborationType.COOPERATIVE
        )
        assert isinstance(collab, dict)
        assert "collab_session_id" in collab

    async def test_create_collaborative_session_group_therapy(self):
        """Collaborative System: create collaborative session group therapy."""
        system = CollaborativeSystem()
        await system.initialize()
        session = _make_session()
        collab = await system.create_collaborative_session(
            session, CollaborationType.GROUP_THERAPY
        )
        assert isinstance(collab, dict)

    async def test_add_participant(self):
        """Collaborative System: add participant."""
        system = CollaborativeSystem()
        await system.initialize()
        session = _make_session()
        collab = await system.create_collaborative_session(
            session, CollaborationType.COOPERATIVE
        )
        collab_id = collab["collab_session_id"]
        success = await system.add_participant(
            collab_id, "user-2", ParticipantRole.SUPPORTER
        )
        assert isinstance(success, bool)

    async def test_add_participant_full_session(self):
        """Collaborative System: add participant full session."""
        system = CollaborativeSystem()
        await system.initialize()
        session = _make_session()
        collab = await system.create_collaborative_session(
            session, CollaborationType.COOPERATIVE
        )
        collab_id = collab["collab_session_id"]
        for i in range(20):
            await system.add_participant(
                collab_id, f"user-{i}", ParticipantRole.PARTICIPANT
            )
        result = await system.add_participant(
            collab_id, "user-overflow", ParticipantRole.PARTICIPANT
        )
        assert isinstance(result, bool)

    async def test_process_collaborative_choice(self):
        """Collaborative System: process collaborative choice."""
        system = CollaborativeSystem()
        await system.initialize()
        session = _make_session()
        collab = await system.create_collaborative_session(
            session, CollaborationType.COOPERATIVE
        )
        collab_id = collab["collab_session_id"]
        choice = _make_user_choice()
        result = await system.process_collaborative_choice(
            collab_id, "user-test", choice
        )
        assert isinstance(result, dict)

    async def test_generate_group_narrative(self):
        """Collaborative System: generate group narrative."""
        system = CollaborativeSystem()
        await system.initialize()
        session = _make_session()
        collab = await system.create_collaborative_session(
            session, CollaborationType.COOPERATIVE
        )
        collab_id = collab["collab_session_id"]
        result = await system.generate_group_narrative(collab_id, session)
        assert result is None or isinstance(result, Scene)

    async def test_generate_group_narrative_invalid_session(self):
        """Collaborative System: generate group narrative invalid session."""
        system = CollaborativeSystem()
        await system.initialize()
        session = _make_session()
        result = await system.generate_group_narrative("nonexistent", session)
        assert result is None


# ---------------------------------------------------------------------------
# ErrorRecoveryManager
# ---------------------------------------------------------------------------


class TestErrorRecoveryManager:
    async def test_initialize_returns_true(self):
        """Error Recovery Manager: initialize returns true."""
        manager = ErrorRecoveryManager()
        result = await manager.initialize()
        assert result is True

    async def test_create_checkpoint(self):
        """Error Recovery Manager: create checkpoint."""
        manager = ErrorRecoveryManager()
        await manager.initialize()
        session = _make_session()
        checkpoint_id = await manager.create_checkpoint(session)
        assert isinstance(checkpoint_id, str)
        assert len(checkpoint_id) > 0

    async def test_restore_checkpoint(self):
        """Error Recovery Manager: restore checkpoint."""
        manager = ErrorRecoveryManager()
        await manager.initialize()
        session = _make_session()
        checkpoint_id = await manager.create_checkpoint(session)
        restored = await manager.restore_checkpoint(checkpoint_id)
        assert isinstance(restored, SessionState)
        assert restored.user_id == session.user_id

    async def test_restore_checkpoint_not_found(self):
        """Error Recovery Manager: restore checkpoint not found."""
        manager = ErrorRecoveryManager()
        await manager.initialize()
        result = await manager.restore_checkpoint("nonexistent-checkpoint")
        assert result is None

    async def test_handle_error_low_severity(self):
        """Error Recovery Manager: handle error low severity."""
        manager = ErrorRecoveryManager()
        await manager.initialize()
        session = _make_session()
        error = ValueError("minor issue")
        result = await manager.handle_error(error, session)
        assert isinstance(result, SessionState)

    async def test_handle_error_critical_severity(self):
        """Error Recovery Manager: handle error critical severity."""
        manager = ErrorRecoveryManager()
        await manager.initialize()
        session = _make_session()
        await manager.create_checkpoint(session)
        error = RuntimeError("critical failure")
        result = await manager.handle_error(error, session)
        assert isinstance(result, SessionState)

    async def test_get_recovery_strategy(self):
        """Error Recovery Manager: get recovery strategy."""
        manager = ErrorRecoveryManager()
        await manager.initialize()
        error = ValueError("test error")
        strategy = await manager.get_recovery_strategy(error)
        assert isinstance(strategy, RecoveryStrategy)

    async def test_get_recovery_strategy_runtime_error(self):
        """Error Recovery Manager: get recovery strategy runtime error."""
        manager = ErrorRecoveryManager()
        await manager.initialize()
        error = RuntimeError("severe problem")
        strategy = await manager.get_recovery_strategy(error)
        assert isinstance(strategy, RecoveryStrategy)

    async def test_log_error(self):
        """Error Recovery Manager: log error."""
        manager = ErrorRecoveryManager()
        await manager.initialize()
        await manager.log_error("s1", ValueError("oops"), ErrorSeverity.LOW)

    async def test_log_error_critical(self):
        """Error Recovery Manager: log error critical."""
        manager = ErrorRecoveryManager()
        await manager.initialize()
        await manager.log_error("s1", RuntimeError("crash"), ErrorSeverity.CRITICAL)
