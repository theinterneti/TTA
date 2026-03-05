"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Therapeutic_integrator]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Therapeutic_integrator]]
Therapeutic Integrator for Therapeutic Text Adventure

This module weaves therapeutic context into narrative scenes by selecting
an appropriate integration intensity and applying evidence-based narrative
techniques such as modeling, scaffolding, and psychoeducation.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import Any

from ..models.core import (
    EmotionalState,
    Scene,
    SessionState,
    TherapeuticContext,
)

logger = logging.getLogger(__name__)


class IntegrationMode(StrEnum):
    """Intensity of therapeutic integration into the narrative."""

    SUBTLE = "subtle"
    MODERATE = "moderate"
    DIRECT = "direct"
    INTENSIVE = "intensive"


class NarrativeTechnique(StrEnum):
    """Evidence-based narrative techniques for therapy delivery."""

    MODELING = "modeling"
    SCAFFOLDING = "scaffolding"
    REFLECTION = "reflection"
    PSYCHOEDUCATION = "psychoeducation"
    EXPERIENTIAL = "experiential"


class TherapeuticIntegrator:
    """
    Integrates therapeutic goals and techniques into narrative scenes,
    adapting intensity and technique based on player readiness and
    session context.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.integration_templates: dict[IntegrationMode, list[str]] = {}
        self.technique_library: dict[NarrativeTechnique, dict[str, Any]] = {}

        logger.info("TherapeuticIntegrator initialized")

    async def initialize(self) -> bool:
        """Initialize integration templates and technique library."""
        try:
            self.integration_templates = {
                IntegrationMode.SUBTLE: [
                    "The character quietly demonstrates {skill}.",
                    "A subtle moment of {concept} unfolds naturally.",
                ],
                IntegrationMode.MODERATE: [
                    "Your companion shares a thought about {concept}.",
                    "The situation invites you to practice {skill}.",
                ],
                IntegrationMode.DIRECT: [
                    "A mentor figure directly teaches you about {concept}.",
                    "You are guided step-by-step through {skill}.",
                ],
                IntegrationMode.INTENSIVE: [
                    "An immersive therapeutic experience focused on {concept} begins.",
                    "You engage deeply with {skill} through guided practice.",
                ],
            }

            self.technique_library = {
                NarrativeTechnique.MODELING: {
                    "description": "Characters model healthy behaviours",
                    "emotional_states": [
                        EmotionalState.CALM,
                        EmotionalState.ENGAGED,
                    ],
                    "narrative_prefix": (
                        "Watching your companion, you notice how they "
                    ),
                },
                NarrativeTechnique.SCAFFOLDING: {
                    "description": "Gradually build skill with support",
                    "emotional_states": [
                        EmotionalState.CALM,
                        EmotionalState.ENGAGED,
                        EmotionalState.ANXIOUS,
                    ],
                    "narrative_prefix": "With gentle guidance, you begin to ",
                },
                NarrativeTechnique.REFLECTION: {
                    "description": "Encourage self-reflection on experience",
                    "emotional_states": [
                        EmotionalState.CALM,
                        EmotionalState.ENGAGED,
                    ],
                    "narrative_prefix": "You take a moment to reflect on ",
                },
                NarrativeTechnique.PSYCHOEDUCATION: {
                    "description": "Deliver knowledge through narrative",
                    "emotional_states": [
                        EmotionalState.CALM,
                        EmotionalState.ENGAGED,
                    ],
                    "narrative_prefix": "A wise guide explains that ",
                },
                NarrativeTechnique.EXPERIENTIAL: {
                    "description": "Learn through in-narrative experience",
                    "emotional_states": [
                        EmotionalState.CALM,
                        EmotionalState.ENGAGED,
                        EmotionalState.ANXIOUS,
                    ],
                    "narrative_prefix": "You find yourself experiencing ",
                },
            }

            logger.info("TherapeuticIntegrator initialization completed")
            return True

        except Exception as e:
            logger.error(f"TherapeuticIntegrator initialization failed: {e}")
            return False

    async def integrate_therapeutic_context(
        self,
        scene: Scene,
        therapeutic_context: TherapeuticContext,
        session_state: SessionState,
    ) -> Scene:
        """
        Weave therapeutic goals into an existing narrative scene.

        Args:
            scene: Base scene to enhance
            therapeutic_context: Goals and therapeutic context
            session_state: Current session state

        Returns:
            Scene with integrated therapeutic elements
        """
        try:
            mode = await self.select_integration_mode(session_state)
            technique = self._select_technique(session_state.emotional_state)

            logger.info(
                f"Integrating therapy into scene {scene.scene_id}: "
                f"mode={mode}, technique={technique}"
            )

            scene = await self.apply_narrative_technique(
                scene, technique, therapeutic_context
            )

            # Tag the scene with therapeutic metadata
            goals = therapeutic_context.primary_goals or []
            for goal in goals:
                if goal not in scene.therapeutic_focus:
                    scene.therapeutic_focus.append(goal)

            if therapeutic_context.session_objectives:
                scene.learning_objectives = list(
                    {
                        *scene.learning_objectives,
                        *therapeutic_context.session_objectives,
                    }
                )

            return scene

        except Exception as e:
            logger.error(
                f"Therapeutic integration failed for scene {scene.scene_id}: {e}"
            )
            return scene

    async def select_integration_mode(
        self, session_state: SessionState
    ) -> IntegrationMode:
        """
        Determine how intensely to integrate therapeutic content.

        Args:
            session_state: Current session state

        Returns:
            Selected integration mode
        """
        try:
            emotional = session_state.emotional_state
            effectiveness = session_state.metrics.therapeutic_effectiveness
            choices_made = session_state.metrics.total_choices_made

            # Back off if the player is distressed
            if emotional in (EmotionalState.DISTRESSED, EmotionalState.CRISIS):
                return IntegrationMode.SUBTLE
            if emotional == EmotionalState.OVERWHELMED:
                return IntegrationMode.SUBTLE
            if emotional == EmotionalState.ANXIOUS:
                return IntegrationMode.MODERATE

            # Ramp up as player demonstrates readiness
            if effectiveness >= 0.7 and choices_made >= 10:
                return IntegrationMode.INTENSIVE
            if effectiveness >= 0.5 and choices_made >= 5:
                return IntegrationMode.DIRECT
            if choices_made >= 3:
                return IntegrationMode.MODERATE

            return IntegrationMode.SUBTLE

        except Exception as e:
            logger.warning(f"Mode selection failed, defaulting to SUBTLE: {e}")
            return IntegrationMode.SUBTLE

    async def apply_narrative_technique(
        self,
        scene: Scene,
        technique: NarrativeTechnique,
        context: TherapeuticContext,
    ) -> Scene:
        """
        Apply a specific narrative technique to a scene.

        Args:
            scene: Scene to modify
            technique: Technique to apply
            context: Therapeutic context

        Returns:
            Modified scene
        """
        try:
            lib_entry = self.technique_library.get(technique, {})
            prefix = lib_entry.get("narrative_prefix", "")
            focus = (
                context.primary_goals[0]
                if context.primary_goals
                else "your personal growth"
            )

            addition = f"\n\n{prefix}{focus}."

            scene.narrative_content += addition

            if str(technique) not in scene.therapeutic_focus:
                scene.therapeutic_focus.append(str(technique))

            logger.info(f"Applied technique {technique} to scene {scene.scene_id}")
            return scene

        except Exception as e:
            logger.error(
                f"Failed to apply technique {technique} to scene {scene.scene_id}: {e}"
            )
            return scene

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _select_technique(self, emotional_state: EmotionalState) -> NarrativeTechnique:
        """Choose the best technique for the player's current emotional state."""
        for technique, entry in self.technique_library.items():
            allowed = entry.get("emotional_states", [])
            if emotional_state in allowed:
                return technique

        return NarrativeTechnique.REFLECTION
