"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Engine]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Engine]]
Narrative Engine for Therapeutic Text Adventure

This module implements the core narrative engine that orchestrates scene generation,
therapeutic storytelling, complexity adaptation, and immersion management for the
therapeutic text adventure gameplay loop system.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from ..database.neo4j_manager import Neo4jGameplayManager
from ..models.core import (
    DifficultyLevel,
    EmotionalState,
    Scene,
    SceneType,
    SessionState,
)
from ..models.interactions import ChoiceOutcome, UserChoice
from .complexity_adapter import NarrativeComplexityAdapter
from .immersion_manager import ImmersionManager
from .pacing_controller import PacingController
from .scene_generator import SceneGenerator

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
from .therapeutic_storyteller import TherapeuticStoryteller

logger = logging.getLogger(__name__)


class NarrativeEngine:
    """
    Core narrative engine for therapeutic text adventure experiences.

    Orchestrates scene generation, therapeutic storytelling, complexity adaptation,
    and immersion management to create engaging and therapeutically effective
    narrative experiences.
    """

    def __init__(
        self,
        db_manager: Neo4jGameplayManager,
        config: dict[str, Any] | None = None,
        llm: BaseChatModel | None = None,
    ):
        self.db_manager = db_manager
        self.config = config or {}
        self._llm = llm

        # Initialize narrative components
        self.scene_generator = SceneGenerator(
            self.config.get("scene_generation", {}), llm=llm
        )
        self.therapeutic_storyteller = TherapeuticStoryteller(
            self.config.get("therapeutic_storytelling", {})
        )
        self.complexity_adapter = NarrativeComplexityAdapter(
            self.config.get("complexity_adaptation", {})
        )
        self.immersion_manager = ImmersionManager(self.config.get("immersion", {}))
        self.pacing_controller = PacingController(self.config.get("pacing", {}))

        # Engine state
        self._active_sessions: dict[str, SessionState] = {}
        self._scene_cache: dict[str, Scene] = {}

        logger.info("NarrativeEngine initialized")

    async def initialize(self) -> bool:
        """Initialize the narrative engine and all components."""
        try:
            # Initialize all narrative components
            await self.scene_generator.initialize()
            await self.therapeutic_storyteller.initialize()
            await self.complexity_adapter.initialize()
            await self.immersion_manager.initialize()
            await self.pacing_controller.initialize()

            logger.info("NarrativeEngine initialization completed")
            return True

        except Exception as e:
            logger.error(f"NarrativeEngine initialization failed: {e}")
            return False

    async def generate_opening_scene(self, session_state: SessionState) -> Scene | None:
        """
        Generate the opening scene for a new therapeutic session.

        Args:
            session_state: Current session state

        Returns:
            Generated opening scene or None if generation failed
        """
        try:
            logger.info(
                f"Generating opening scene for session {session_state.session_id}"
            )

            # Determine therapeutic context and goals
            therapeutic_context = session_state.therapeutic_context
            emotional_state = session_state.emotional_state
            difficulty_level = session_state.difficulty_level

            # Generate scene parameters based on therapeutic needs
            scene_params = await self._determine_opening_scene_parameters(
                therapeutic_context, emotional_state, difficulty_level
            )

            # Generate the scene using the scene generator
            scene = await self.scene_generator.generate_therapeutic_scene(
                scene_type=SceneType.INTRODUCTION,
                therapeutic_focus=therapeutic_context.primary_goals,
                emotional_tone="welcoming",
                difficulty_level=difficulty_level,
                **scene_params,
            )

            if scene:
                # Enhance with therapeutic storytelling
                scene = await self.therapeutic_storyteller.enhance_scene_with_therapy(
                    scene, therapeutic_context
                )

                # Adapt complexity based on user profile
                scene = await self.complexity_adapter.adapt_scene_complexity(
                    scene, session_state
                )

                # Apply immersion enhancements
                scene = await self.immersion_manager.enhance_scene_immersion(
                    scene, session_state
                )

                # Cache in-memory always; attempt DB persist (non-blocking)
                self._scene_cache[scene.scene_id] = scene
                persisted = await self.db_manager.create_scene(scene)
                if not persisted:
                    logger.warning(
                        f"Scene {scene.scene_id} generated but DB persist failed; "
                        "using in-memory cache only"
                    )

                logger.info(f"Generated opening scene: {scene.scene_id}")
                return scene

            return None

        except Exception as e:
            logger.error(f"Failed to generate opening scene: {e}")
            return None

    async def generate_next_scene(
        self,
        session_state: SessionState,
        previous_choice: UserChoice | None = None,
        choice_outcome: ChoiceOutcome | None = None,
    ) -> Scene | None:
        """
        Generate the next scene based on player choice and outcome.

        Args:
            session_state: Current session state
            previous_choice: The choice the player made
            choice_outcome: The outcome of that choice

        Returns:
            Generated next scene or None if generation failed
        """
        try:
            logger.info(f"Generating next scene for session {session_state.session_id}")

            # Analyze choice outcome for narrative direction
            narrative_direction = await self._analyze_choice_for_narrative_direction(
                previous_choice, choice_outcome
            )

            # Determine scene type based on narrative flow
            scene_type = await self._determine_next_scene_type(
                session_state, narrative_direction
            )

            # Check pacing and adjust if needed
            pacing_adjustment = await self.pacing_controller.analyze_session_pacing(
                session_state
            )

            # Generate scene parameters
            scene_params = await self._determine_scene_parameters(
                session_state, narrative_direction, pacing_adjustment
            )

            # Generate the scene (strip keys already passed as explicit args)
            extra_params = {
                k: v
                for k, v in scene_params.items()
                if k
                not in {
                    "scene_type",
                    "therapeutic_focus",
                    "emotional_tone",
                    "difficulty_level",
                    "previous_scene_context",
                    "choice_context",
                }
            }
            scene = await self.scene_generator.generate_therapeutic_scene(
                scene_type=scene_type,
                therapeutic_focus=session_state.therapeutic_context.primary_goals,
                emotional_tone=self._determine_emotional_tone(choice_outcome),
                difficulty_level=session_state.difficulty_level,
                previous_scene_context=session_state.current_scene,
                choice_context=previous_choice,
                **extra_params,
            )

            if scene:
                # Apply therapeutic enhancements
                scene = await self.therapeutic_storyteller.enhance_scene_with_therapy(
                    scene, session_state.therapeutic_context
                )

                # Adapt complexity
                scene = await self.complexity_adapter.adapt_scene_complexity(
                    scene, session_state
                )

                # Enhance immersion
                scene = await self.immersion_manager.enhance_scene_immersion(
                    scene, session_state
                )

                # Apply pacing adjustments
                scene = await self.pacing_controller.apply_pacing_adjustments(
                    scene, pacing_adjustment
                )

                # Cache in-memory always; attempt DB persist (non-blocking)
                self._scene_cache[scene.scene_id] = scene
                persisted = await self.db_manager.create_scene(scene)
                if not persisted:
                    logger.warning(
                        f"Scene {scene.scene_id} generated but DB persist failed; "
                        "using in-memory cache only"
                    )

                logger.info(f"Generated next scene: {scene.scene_id}")
                return scene

            return None

        except Exception as e:
            logger.error(f"Failed to generate next scene: {e}")
            return None

    async def adapt_scene_for_emotional_state(
        self,
        scene: Scene,
        new_emotional_state: EmotionalState,
        session_state: SessionState,
    ) -> Scene:
        """
        Adapt an existing scene for a changed emotional state.

        Args:
            scene: The scene to adapt
            new_emotional_state: The new emotional state
            session_state: Current session state

        Returns:
            Adapted scene
        """
        try:
            logger.info(
                f"Adapting scene {scene.scene_id} for emotional state {new_emotional_state}"
            )

            # Create adapted scene copy
            adapted_scene = Scene(**scene.model_dump())
            adapted_scene.scene_id = str(uuid4())  # New ID for adapted scene

            # Apply emotional state adaptations
            if new_emotional_state in [
                EmotionalState.ANXIOUS,
                EmotionalState.OVERWHELMED,
            ]:
                # Make scene more calming and supportive
                adapted_scene = await self._apply_calming_adaptations(adapted_scene)
            elif new_emotional_state == EmotionalState.DISTRESSED:
                # Apply grounding and safety adaptations
                adapted_scene = await self._apply_grounding_adaptations(adapted_scene)
            elif new_emotional_state == EmotionalState.CRISIS:
                # Apply crisis intervention adaptations
                adapted_scene = await self._apply_crisis_adaptations(adapted_scene)

            # Re-enhance with therapeutic storytelling
            adapted_scene = (
                await self.therapeutic_storyteller.enhance_scene_with_therapy(
                    adapted_scene, session_state.therapeutic_context
                )
            )

            # Update immersion for new emotional context
            adapted_scene = await self.immersion_manager.enhance_scene_immersion(
                adapted_scene, session_state
            )

            logger.info(f"Adapted scene for emotional state: {adapted_scene.scene_id}")
            return adapted_scene

        except Exception as e:
            logger.error(f"Failed to adapt scene for emotional state: {e}")
            return scene  # Return original scene if adaptation fails

    async def generate_therapeutic_intervention_scene(
        self, session_state: SessionState, intervention_type: str
    ) -> Scene | None:
        """
        Generate a scene specifically for therapeutic intervention.

        Args:
            session_state: Current session state
            intervention_type: Type of therapeutic intervention needed

        Returns:
            Generated intervention scene or None if generation failed
        """
        try:
            logger.info(
                f"Generating therapeutic intervention scene: {intervention_type}"
            )

            # Generate intervention-specific scene
            scene = await self.scene_generator.generate_intervention_scene(
                intervention_type=intervention_type,
                emotional_state=session_state.emotional_state,
                therapeutic_context=session_state.therapeutic_context,
                difficulty_level=DifficultyLevel.GENTLE,  # Always gentle for interventions
            )

            if scene:
                # Apply therapeutic storytelling
                scene = await self.therapeutic_storyteller.enhance_intervention_scene(
                    scene, intervention_type, session_state.therapeutic_context
                )

                # Ensure appropriate complexity (usually simplified for interventions)
                scene = await self.complexity_adapter.simplify_for_intervention(
                    scene, session_state
                )

                # Cache in-memory always; attempt DB persist (non-blocking)
                self._scene_cache[scene.scene_id] = scene
                persisted = await self.db_manager.create_scene(scene)
                if not persisted:
                    logger.warning(
                        f"Scene {scene.scene_id} generated but DB persist failed; "
                        "using in-memory cache only"
                    )

                logger.info(f"Generated intervention scene: {scene.scene_id}")
                return scene

            return None

        except Exception as e:
            logger.error(f"Failed to generate intervention scene: {e}")
            return None

    # Helper Methods
    async def _determine_opening_scene_parameters(  # noqa: ARG002
        self,
        therapeutic_context,
        emotional_state: EmotionalState,
        difficulty_level: DifficultyLevel,
    ) -> dict[str, Any]:
        """Determine parameters for opening scene generation."""
        params = {
            "setting": "peaceful_garden",  # Default safe setting
            "atmosphere": "welcoming",
            "safety_level": "high",
            "therapeutic_elements": therapeutic_context.primary_goals[
                :2
            ],  # Limit to top 2 goals
        }

        # Adjust based on emotional state
        if emotional_state in [EmotionalState.ANXIOUS, EmotionalState.OVERWHELMED]:
            params.update(
                {
                    "setting": "quiet_sanctuary",
                    "atmosphere": "deeply_calming",
                    "safety_level": "maximum",
                }
            )
        elif emotional_state == EmotionalState.DISTRESSED:
            params.update(
                {
                    "setting": "safe_haven",
                    "atmosphere": "protective",
                    "safety_level": "maximum",
                    "grounding_elements": True,
                }
            )

        return params

    async def _analyze_choice_for_narrative_direction(
        self,
        choice: UserChoice | None,
        outcome: ChoiceOutcome | None,
    ) -> dict[str, Any]:
        """Analyze choice and outcome to determine narrative direction."""
        direction = {
            "narrative_momentum": "forward",
            "emotional_trajectory": "stable",
            "therapeutic_progress": "maintained",
            "complexity_adjustment": "none",
        }

        # Analyze choice type and therapeutic value
        if choice is not None:
            if choice.therapeutic_value > 0.7:
                direction["therapeutic_progress"] = "advanced"
                direction["narrative_momentum"] = "accelerated"
            elif choice.therapeutic_value < 0.3:
                direction["therapeutic_progress"] = "needs_support"
                direction["complexity_adjustment"] = "simplify"

        # Analyze outcome type
        if outcome is not None:
            if outcome.outcome_type in ["success", "therapeutic_opportunity"]:
                direction["emotional_trajectory"] = "positive"
            elif outcome.outcome_type in ["challenge", "failure"]:
                direction["emotional_trajectory"] = "needs_support"
                direction["narrative_momentum"] = "reflective"

        return direction

    async def _determine_next_scene_type(
        self, session_state: SessionState, narrative_direction: dict[str, Any]
    ) -> SceneType:
        """Determine the type of the next scene based on context."""
        # Default progression
        if not session_state.scene_history:
            return SceneType.EXPLORATION

        # Analyze narrative direction
        if narrative_direction["therapeutic_progress"] == "needs_support":
            return SceneType.THERAPEUTIC
        if narrative_direction["emotional_trajectory"] == "needs_support":
            return SceneType.REFLECTION
        if narrative_direction["narrative_momentum"] == "accelerated":
            return SceneType.CHALLENGE
        return SceneType.EXPLORATION

    async def _determine_scene_parameters(
        self,
        session_state: SessionState,
        narrative_direction: dict[str, Any],
        pacing_adjustment: dict[str, Any],
    ) -> dict[str, Any]:
        """Determine parameters for scene generation."""
        params = {
            "continuity_elements": (
                session_state.scene_history[-3:] if session_state.scene_history else []
            ),
            "therapeutic_focus": session_state.therapeutic_context.primary_goals,
            "character_context": session_state.character_id,
            "world_context": session_state.world_id,
        }

        # Apply narrative direction
        if narrative_direction["complexity_adjustment"] == "simplify":
            params["complexity_level"] = "reduced"
        elif narrative_direction["therapeutic_progress"] == "advanced":
            params["therapeutic_depth"] = "enhanced"

        # Apply pacing adjustments
        if pacing_adjustment.get("needs_acceleration"):
            params["pacing"] = "faster"
        elif pacing_adjustment.get("needs_deceleration"):
            params["pacing"] = "slower"

        return params

    def _determine_emotional_tone(self, choice_outcome: ChoiceOutcome | None) -> str:
        """Determine emotional tone based on choice outcome."""
        if choice_outcome is None:
            return "neutral"
        tone_mapping = {
            "success": "encouraging",
            "partial_success": "supportive",
            "neutral": "balanced",
            "challenge": "understanding",
            "failure": "compassionate",
            "therapeutic_opportunity": "hopeful",
        }
        return tone_mapping.get(choice_outcome.outcome_type, "neutral")

    async def _apply_calming_adaptations(self, scene: Scene) -> Scene:
        """Apply calming adaptations to a scene."""
        # Modify narrative content to be more calming
        calming_elements = [
            "The gentle sound of flowing water creates a peaceful atmosphere.",
            "Soft, warm light filters through the space, creating a sense of safety.",
            "The air is fresh and clean, helping you feel more grounded.",
        ]

        # Add calming elements to the narrative
        scene.narrative_content += f"\n\n{' '.join(calming_elements[:2])}"
        scene.emotional_tone = "deeply_calming"
        scene.therapeutic_focus.extend(["grounding", "anxiety_relief"])

        return scene

    async def _apply_grounding_adaptations(self, scene: Scene) -> Scene:
        """Apply grounding adaptations to a scene."""
        grounding_elements = [
            "Notice the solid ground beneath your feet, providing stability and support.",
            "Take a moment to observe five things you can see, four things you can hear, three things you can touch.",
            "Your breathing naturally slows as you connect with the present moment.",
        ]

        scene.narrative_content += f"\n\n{grounding_elements[0]}"
        scene.emotional_tone = "grounding"
        scene.therapeutic_focus.extend(["grounding", "present_moment_awareness"])

        return scene

    async def _apply_crisis_adaptations(self, scene: Scene) -> Scene:
        """Apply crisis intervention adaptations to a scene."""
        # Transform scene into a crisis support environment
        scene.scene_type = SceneType.THERAPEUTIC
        scene.difficulty_level = DifficultyLevel.GENTLE
        scene.emotional_tone = "deeply_supportive"

        crisis_content = (
            "You find yourself in a completely safe space, surrounded by warmth and protection. "
            "Here, you are valued and supported. Take all the time you need. "
            "Remember that you are not alone, and help is always available."
        )

        scene.narrative_content = crisis_content
        scene.therapeutic_focus = ["crisis_support", "safety", "connection"]

        return scene
