"""
Causality Explainer for Therapeutic Text Adventure

This module implements causality explanation functionality that provides clear,
understandable explanations of cause-and-effect relationships between player
choices and their consequences to support learning and understanding.
"""

from __future__ import annotations

import logging
from typing import Any

from ..models.core import EmotionalState, Scene, SessionState
from ..models.interactions import UserChoice

logger = logging.getLogger(__name__)


class CausalityExplainer:
    """
    Provides clear explanations of cause-and-effect relationships between
    player choices and their consequences to support learning and understanding.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Causality explanation resources
        self.explanation_templates: dict[str, list[str]] = {}
        self.causal_relationship_patterns: dict[str, dict[str, Any]] = {}
        self.clarity_levels: dict[str, dict[str, Any]] = {}

        logger.info("CausalityExplainer initialized")

    async def initialize(self) -> bool:
        """Initialize causality explanation templates and patterns."""
        try:
            await self._load_explanation_templates()
            await self._load_causal_patterns()
            await self._load_clarity_levels()

            logger.info("CausalityExplainer initialization completed")
            return True

        except Exception as e:
            logger.error(f"CausalityExplainer initialization failed: {e}")
            return False

    async def explain_causality(
        self,
        user_choice: UserChoice,
        outcomes: dict[str, Any],
        scene: Scene,
        session_state: SessionState,
    ) -> str:
        """
        Generate clear causality explanation for choice and outcomes.

        Args:
            user_choice: The choice made by the user
            outcomes: Generated outcomes from the choice
            scene: The scene where the choice was made
            session_state: Current session state

        Returns:
            Clear causality explanation string
        """
        try:
            logger.info(
                f"Generating causality explanation for choice {user_choice.choice_id}"
            )

            # Determine explanation approach based on choice type and outcomes
            explanation_approach = await self._determine_explanation_approach(
                user_choice, outcomes, session_state
            )

            # Generate core causality explanation
            core_explanation = await self._generate_core_explanation(
                user_choice, outcomes, explanation_approach
            )

            # Add therapeutic context
            therapeutic_context = await self._add_therapeutic_context(
                core_explanation, user_choice, session_state
            )

            # Adjust for emotional state
            adjusted_explanation = await self._adjust_for_emotional_state(
                therapeutic_context, session_state.emotional_state
            )

            logger.info("Causality explanation generated")
            return adjusted_explanation

        except Exception as e:
            logger.error(f"Failed to generate causality explanation: {e}")
            return await self._generate_fallback_explanation(user_choice)

    async def adapt_explanation_for_emotion(
        self, original_explanation: str, emotional_state: str
    ) -> str:
        """
        Adapt causality explanation for a specific emotional state.

        Args:
            original_explanation: Original explanation to adapt
            emotional_state: Target emotional state

        Returns:
            Adapted explanation
        """
        try:
            emotional_state_enum = EmotionalState(emotional_state)

            # Get adaptation strategy for emotional state
            adaptation_strategy = await self._get_adaptation_strategy(
                emotional_state_enum
            )

            # Apply adaptation
            adapted_explanation = await self._apply_adaptation_strategy(
                original_explanation, adaptation_strategy
            )

            return adapted_explanation

        except Exception as e:
            logger.error(f"Failed to adapt explanation for emotional state: {e}")
            return original_explanation

    # Initialization Methods
    async def _load_explanation_templates(self) -> None:
        """Load causality explanation templates."""
        self.explanation_templates = {
            "therapeutic_choice": [
                "When you chose to {choice_action}, you engaged with {therapeutic_principle}, which naturally leads to {positive_outcome}",
                "Your decision to {choice_action} demonstrates {therapeutic_skill}, creating {beneficial_result}",
                "By choosing {choice_action}, you practiced {therapeutic_technique}, resulting in {growth_outcome}",
            ],
            "narrative_choice": [
                "Your choice to {choice_action} moved the story toward {narrative_direction}, opening {new_possibilities}",
                "When you decided to {choice_action}, it created {story_consequence} and revealed {story_element}",
                "This choice to {choice_action} shaped your journey by {narrative_impact}",
            ],
            "skill_building_choice": [
                "Practicing {skill_name} through {choice_action} strengthened your {skill_area} and led to {skill_outcome}",
                "Your effort to {choice_action} developed {capability} and created {competence_result}",
                "By applying {skill_name} in this situation, you built {skill_aspect} and achieved {success_outcome}",
            ],
            "emotional_regulation_choice": [
                "Working with your emotions through {choice_action} helped you {regulation_outcome} and feel {emotional_result}",
                "Your choice to {choice_action} supported emotional balance by {regulation_mechanism}",
                "Engaging in {choice_action} allowed you to {emotional_process} and experience {positive_emotion}",
            ],
            "social_interaction_choice": [
                "Your approach of {choice_action} created {social_outcome} and strengthened {relationship_aspect}",
                "When you chose to {choice_action}, it fostered {connection_type} and led to {social_result}",
                "This social choice to {choice_action} built {relationship_quality} and opened {social_opportunity}",
            ],
        }

    async def _load_causal_patterns(self) -> None:
        """Load causal relationship patterns."""
        self.causal_relationship_patterns = {
            "direct_causality": {
                "pattern": "Action A directly leads to Result B",
                "template": "Your {action} directly created {result} because {causal_mechanism}",
                "strength": "strong",
            },
            "therapeutic_causality": {
                "pattern": "Therapeutic action leads to therapeutic benefit",
                "template": "Engaging in {therapeutic_action} supports {therapeutic_goal} through {therapeutic_process}",
                "strength": "strong",
            },
            "skill_development_causality": {
                "pattern": "Practice leads to skill improvement",
                "template": "Practicing {skill} through {action} builds {capability} over time",
                "strength": "moderate",
            },
            "emotional_causality": {
                "pattern": "Emotional work leads to emotional growth",
                "template": "Working with {emotion} through {technique} creates {emotional_outcome}",
                "strength": "moderate",
            },
            "narrative_causality": {
                "pattern": "Story choice leads to story consequence",
                "template": "Your choice to {story_action} moves the narrative toward {story_outcome}",
                "strength": "variable",
            },
        }

    async def _load_clarity_levels(self) -> None:
        """Load clarity levels for explanations."""
        self.clarity_levels = {
            "high": {
                "characteristics": [
                    "explicit_connections",
                    "clear_language",
                    "step_by_step",
                ],
                "emotional_states": [EmotionalState.CALM, EmotionalState.ENGAGED],
                "template_modifiers": ["clearly", "directly", "specifically"],
            },
            "moderate": {
                "characteristics": [
                    "general_connections",
                    "supportive_language",
                    "encouraging",
                ],
                "emotional_states": [EmotionalState.ANXIOUS],
                "template_modifiers": ["gently", "naturally", "gradually"],
            },
            "gentle": {
                "characteristics": [
                    "soft_connections",
                    "reassuring_language",
                    "simple",
                ],
                "emotional_states": [
                    EmotionalState.OVERWHELMED,
                    EmotionalState.DISTRESSED,
                    EmotionalState.CRISIS,
                ],
                "template_modifiers": ["softly", "kindly", "simply"],
            },
        }

    # Core Methods
    async def _determine_explanation_approach(
        self,
        user_choice: UserChoice,
        outcomes: dict[str, Any],
        session_state: SessionState,
    ) -> str:
        """Determine the best approach for explaining causality."""
        # Base approach on choice type
        choice_type_approaches = {
            "therapeutic": "therapeutic_causality",
            "narrative": "narrative_causality",
            "skill_building": "skill_development_causality",
            "emotional_regulation": "emotional_causality",
            "social_interaction": "direct_causality",
        }

        return choice_type_approaches.get(
            user_choice.choice_type.value, "direct_causality"
        )

    async def _generate_core_explanation(
        self, user_choice: UserChoice, outcomes: dict[str, Any], approach: str
    ) -> str:
        """Generate core causality explanation."""
        pattern = self.causal_relationship_patterns.get(
            approach, self.causal_relationship_patterns["direct_causality"]
        )
        template = pattern["template"]

        # Simple template filling - in a full implementation, this would be more sophisticated
        explanation = template.format(
            action=user_choice.choice_text.lower(),
            result="positive change",
            causal_mechanism="therapeutic principles",
            therapeutic_action=user_choice.choice_text.lower(),
            therapeutic_goal="wellbeing",
            therapeutic_process="evidence-based practices",
        )

        return explanation

    async def _add_therapeutic_context(
        self,
        core_explanation: str,
        user_choice: UserChoice,
        session_state: SessionState,
    ) -> str:
        """Add therapeutic context to explanation."""
        therapeutic_context = f" This supports your therapeutic journey by building {', '.join(user_choice.therapeutic_tags[:2])}."
        return core_explanation + therapeutic_context

    async def _adjust_for_emotional_state(
        self, explanation: str, emotional_state: EmotionalState
    ) -> str:
        """Adjust explanation for emotional state."""
        # Determine clarity level
        clarity_level = "high"
        for level, data in self.clarity_levels.items():
            if emotional_state in data["emotional_states"]:
                clarity_level = level
                break

        # Apply modifiers based on clarity level
        self.clarity_levels[clarity_level]["template_modifiers"]

        if clarity_level == "gentle":
            explanation = f"Gently, {explanation.lower()}"
        elif clarity_level == "moderate":
            explanation = f"Naturally, {explanation.lower()}"

        return explanation

    async def _generate_fallback_explanation(self, user_choice: UserChoice) -> str:
        """Generate fallback explanation when normal generation fails."""
        return f"Your choice to {user_choice.choice_text.lower()} reflects your values and creates positive change in your journey of growth and self-discovery."

    async def _get_adaptation_strategy(
        self, emotional_state: EmotionalState
    ) -> dict[str, Any]:
        """Get adaptation strategy for emotional state."""
        strategies = {
            EmotionalState.CRISIS: {"tone": "immediate_support", "focus": "safety"},
            EmotionalState.DISTRESSED: {"tone": "gentle_support", "focus": "comfort"},
            EmotionalState.OVERWHELMED: {"tone": "simplifying", "focus": "clarity"},
            EmotionalState.ANXIOUS: {"tone": "reassuring", "focus": "stability"},
            EmotionalState.CALM: {"tone": "balanced", "focus": "understanding"},
            EmotionalState.ENGAGED: {"tone": "encouraging", "focus": "growth"},
        }

        return strategies.get(
            emotional_state, {"tone": "balanced", "focus": "understanding"}
        )

    async def _apply_adaptation_strategy(
        self, explanation: str, strategy: dict[str, Any]
    ) -> str:
        """Apply adaptation strategy to explanation."""
        tone = strategy.get("tone", "balanced")

        if tone == "immediate_support":
            return f"Right now, {explanation.lower()} This supports your immediate safety and wellbeing."
        elif tone == "gentle_support":
            return f"Gently, {explanation.lower()} This offers comfort and support."
        elif tone == "simplifying":
            return f"Simply put, {explanation.lower()}"
        elif tone == "reassuring":
            return f"Reassuringly, {explanation.lower()} This creates stability."
        elif tone == "encouraging":
            return f"Encouragingly, {explanation.lower()} This supports your growth."
        else:
            return explanation
