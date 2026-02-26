"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Choice_architecture/Manager]]

# Logseq: [[TTA/Components/Gameplay_loop/Choice_architecture/Manager]]
Choice Architecture Manager for Therapeutic Text Adventure

This module implements the main choice architecture manager that orchestrates
choice generation, validation, and agency protection to create meaningful
decision-making experiences that support therapeutic goals.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from ..models.core import Choice, ChoiceType, DifficultyLevel, Scene, SessionState
from ..models.interactions import ChoiceOutcome, UserChoice
from .agency_protector import AgencyProtector
from .generator import ChoiceGenerator
from .validator import ChoiceValidator

logger = logging.getLogger(__name__)


class ChoiceArchitectureManager:
    """
    Main manager for choice architecture that orchestrates choice generation,
    validation, and agency protection to create meaningful therapeutic choices.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Initialize components
        self.choice_generator = ChoiceGenerator(
            self.config.get("choice_generation", {})
        )
        self.choice_validator = ChoiceValidator(
            self.config.get("choice_validation", {})
        )
        self.agency_protector = AgencyProtector(
            self.config.get("agency_protection", {})
        )

        # Choice architecture settings
        self.min_choices = self.config.get("min_choices", 2)
        self.max_choices = self.config.get("max_choices", 4)
        self.therapeutic_choice_ratio = self.config.get("therapeutic_choice_ratio", 0.6)

        logger.info("ChoiceArchitectureManager initialized")

    async def initialize(self) -> bool:
        """Initialize the choice architecture system."""
        try:
            await self.choice_generator.initialize()
            await self.choice_validator.initialize()
            await self.agency_protector.initialize()

            logger.info("ChoiceArchitectureManager initialization completed")
            return True

        except Exception as e:
            logger.error(f"ChoiceArchitectureManager initialization failed: {e}")
            return False

    async def generate_choices_for_scene(
        self, scene: Scene, session_state: SessionState
    ) -> list[Choice]:
        """
        Generate meaningful choices for a scene that support therapeutic goals
        while maintaining player agency.

        Args:
            scene: The scene to generate choices for
            session_state: Current session state for context

        Returns:
            List of validated, meaningful choices
        """
        try:
            logger.info(f"Generating choices for scene {scene.scene_id}")

            # Determine choice requirements
            choice_requirements = await self._determine_choice_requirements(
                scene, session_state
            )

            # Generate initial choice set
            raw_choices = await self.choice_generator.generate_choices(
                scene, session_state, choice_requirements
            )

            # Validate choices for therapeutic relevance and safety
            validated_choices = await self.choice_validator.validate_choices(
                raw_choices, scene, session_state
            )

            # Protect player agency
            agency_protected_choices = (
                await self.agency_protector.ensure_meaningful_agency(
                    validated_choices, scene, session_state
                )
            )

            # Final optimization
            optimized_choices = await self._optimize_choice_set(
                agency_protected_choices, scene, session_state
            )

            logger.info(f"Generated {len(optimized_choices)} choices for scene")
            return optimized_choices

        except Exception as e:
            logger.error(f"Failed to generate choices for scene: {e}")
            return await self._generate_fallback_choices(scene, session_state)

    async def evaluate_choice_outcome(
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> ChoiceOutcome:
        """
        Evaluate the outcome of a user's choice for therapeutic and narrative impact.

        Args:
            user_choice: The choice made by the user
            scene: The scene where the choice was made
            session_state: Current session state

        Returns:
            ChoiceOutcome with therapeutic and narrative implications
        """
        try:
            logger.info(f"Evaluating choice outcome for choice {user_choice.choice_id}")

            # Analyze choice for therapeutic value
            therapeutic_analysis = (
                await self.choice_validator.analyze_therapeutic_impact(
                    user_choice, scene, session_state
                )
            )

            # Analyze choice for narrative impact
            narrative_analysis = await self._analyze_narrative_impact(
                user_choice, scene, session_state
            )

            # Determine outcome type and consequences
            outcome_type = await self._determine_outcome_type(
                therapeutic_analysis, narrative_analysis
            )

            # Generate outcome
            outcome = ChoiceOutcome(
                choice_id=user_choice.choice_id,
                outcome_type=outcome_type,
                therapeutic_impact=therapeutic_analysis,
                narrative_consequences=narrative_analysis.get("consequences", []),
                learning_opportunities=therapeutic_analysis.get(
                    "learning_opportunities", []
                ),
                emotional_response=narrative_analysis.get(
                    "emotional_response", "neutral"
                ),
                skill_development=therapeutic_analysis.get("skill_development", []),
                progress_markers=therapeutic_analysis.get("progress_markers", []),
            )

            logger.info(f"Choice outcome evaluated: {outcome_type}")
            return outcome

        except Exception as e:
            logger.error(f"Failed to evaluate choice outcome: {e}")
            return await self._generate_fallback_outcome(user_choice)

    async def adapt_choices_for_emotional_state(
        self,
        choices: list[Choice],
        new_emotional_state: str,
        session_state: SessionState,
    ) -> list[Choice]:
        """
        Adapt existing choices for a changed emotional state.

        Args:
            choices: Original choices to adapt
            new_emotional_state: New emotional state to adapt for
            session_state: Current session state

        Returns:
            Adapted choices appropriate for the new emotional state
        """
        try:
            logger.info(f"Adapting choices for emotional state: {new_emotional_state}")

            adapted_choices = []

            for choice in choices:
                # Check if choice is still appropriate
                is_appropriate = (
                    await self.choice_validator.validate_for_emotional_state(
                        choice, new_emotional_state, session_state
                    )
                )

                if is_appropriate:
                    # Adapt choice content for new emotional state
                    adapted_choice = await self._adapt_choice_for_emotion(
                        choice, new_emotional_state
                    )
                    adapted_choices.append(adapted_choice)
                else:
                    # Replace with more appropriate choice
                    replacement_choice = (
                        await self.choice_generator.generate_emotion_appropriate_choice(
                            choice.choice_type, new_emotional_state, session_state
                        )
                    )
                    if replacement_choice:
                        adapted_choices.append(replacement_choice)

            # Ensure we have minimum number of choices
            while len(adapted_choices) < self.min_choices:
                fallback_choice = await self.choice_generator.generate_safe_choice(
                    new_emotional_state, session_state
                )
                if fallback_choice:
                    adapted_choices.append(fallback_choice)
                else:
                    break

            logger.info(f"Adapted {len(adapted_choices)} choices for emotional state")
            return adapted_choices

        except Exception as e:
            logger.error(f"Failed to adapt choices for emotional state: {e}")
            return choices  # Return original choices if adaptation fails

    # Helper Methods
    async def _determine_choice_requirements(
        self, scene: Scene, session_state: SessionState
    ) -> dict[str, Any]:
        """Determine requirements for choice generation."""
        requirements = {
            "min_choices": self.min_choices,
            "max_choices": self.max_choices,
            "therapeutic_focus": scene.therapeutic_focus,
            "difficulty_level": scene.difficulty_level,
            "scene_type": scene.scene_type,
            "emotional_state": session_state.emotional_state,
            "choice_types_needed": [],
        }

        # Determine needed choice types based on therapeutic focus
        max(1, int(self.max_choices * self.therapeutic_choice_ratio))

        if "mindfulness" in scene.therapeutic_focus:
            requirements["choice_types_needed"].append(ChoiceType.THERAPEUTIC)
        if "skill_building" in scene.therapeutic_focus:
            requirements["choice_types_needed"].append(ChoiceType.SKILL_BUILDING)
        if "emotional_regulation" in scene.therapeutic_focus:
            requirements["choice_types_needed"].append(ChoiceType.EMOTIONAL_REGULATION)

        # Always include narrative choices for story progression
        requirements["choice_types_needed"].append(ChoiceType.NARRATIVE)

        # Adjust for complexity preferences
        complexity_preference = getattr(
            scene, "choice_complexity_preference", "standard"
        )
        requirements["complexity_preference"] = complexity_preference

        return requirements

    async def _optimize_choice_set(
        self, choices: list[Choice], scene: Scene, session_state: SessionState
    ) -> list[Choice]:
        """Optimize the final choice set for balance and effectiveness."""
        if len(choices) <= self.max_choices:
            return choices

        # Score choices for optimization
        scored_choices = []
        for choice in choices:
            score = await self._calculate_choice_score(choice, scene, session_state)
            scored_choices.append((choice, score))

        # Sort by score and take top choices
        scored_choices.sort(key=lambda x: x[1], reverse=True)
        optimized_choices = [
            choice for choice, score in scored_choices[: self.max_choices]
        ]

        # Ensure we have at least one therapeutic choice
        has_therapeutic = any(
            choice.choice_type == ChoiceType.THERAPEUTIC for choice in optimized_choices
        )
        if not has_therapeutic and len(choices) > len(optimized_choices):
            # Replace lowest scoring non-therapeutic choice with highest scoring therapeutic choice
            therapeutic_choices = [
                choice
                for choice in choices
                if choice.choice_type == ChoiceType.THERAPEUTIC
            ]
            if therapeutic_choices:
                # Find lowest scoring non-therapeutic choice in optimized set
                non_therapeutic = [
                    (i, choice)
                    for i, choice in enumerate(optimized_choices)
                    if choice.choice_type != ChoiceType.THERAPEUTIC
                ]
                if non_therapeutic:
                    lowest_idx = min(
                        non_therapeutic, key=lambda x: scored_choices[x[0]][1]
                    )[0]
                    optimized_choices[lowest_idx] = therapeutic_choices[0]

        return optimized_choices

    async def _calculate_choice_score(
        self, choice: Choice, scene: Scene, session_state: SessionState
    ) -> float:
        """Calculate a score for choice optimization."""
        score = 0.0

        # Therapeutic relevance score
        therapeutic_relevance = len(
            set(choice.therapeutic_tags) & set(scene.therapeutic_focus)
        )
        score += therapeutic_relevance * 0.3

        # Difficulty appropriateness score
        _difficulty_order = {
            DifficultyLevel.GENTLE: 0,
            DifficultyLevel.STANDARD: 1,
            DifficultyLevel.CHALLENGING: 2,
            DifficultyLevel.INTENSIVE: 3,
        }
        if choice.difficulty_level == scene.difficulty_level:
            score += 0.2
        elif (
            abs(
                _difficulty_order.get(choice.difficulty_level, 1)
                - _difficulty_order.get(scene.difficulty_level, 1)
            )
            == 1
        ):
            score += 0.1

        # Emotional appropriateness score
        if session_state.emotional_state.value in choice.emotional_context:
            score += 0.2

        # Agency and meaningfulness score
        score += choice.agency_level * 0.15
        score += choice.meaningfulness_score * 0.15

        return score

    async def _analyze_narrative_impact(  # noqa: ARG002
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> dict[str, Any]:
        """Analyze the narrative impact of a user's choice."""
        impact_analysis = {
            "narrative_progression": "forward",
            "character_development": [],
            "world_state_changes": [],
            "consequences": [],
            "emotional_response": "neutral",
        }

        # Analyze based on choice type
        if user_choice.choice_type == ChoiceType.NARRATIVE:
            impact_analysis["narrative_progression"] = "significant"
            impact_analysis["consequences"].append("story_advancement")
        elif user_choice.choice_type == ChoiceType.THERAPEUTIC:
            impact_analysis["character_development"].append("therapeutic_growth")
            impact_analysis["emotional_response"] = "positive"
        elif user_choice.choice_type == ChoiceType.SKILL_BUILDING:
            impact_analysis["character_development"].append("skill_development")
            impact_analysis["consequences"].append("capability_increase")

        # Analyze therapeutic value impact
        if user_choice.therapeutic_value > 0.7:
            impact_analysis["emotional_response"] = "very_positive"
            impact_analysis["consequences"].append("therapeutic_breakthrough")
        elif user_choice.therapeutic_value < 0.3:
            impact_analysis["consequences"].append("learning_opportunity")

        return impact_analysis

    async def _determine_outcome_type(
        self, therapeutic_analysis: dict[str, Any], narrative_analysis: dict[str, Any]
    ) -> str:
        """Determine the type of outcome based on analysis."""
        therapeutic_impact = therapeutic_analysis.get("therapeutic_impact_score", 0.5)
        narrative_progression = narrative_analysis.get(
            "narrative_progression", "forward"
        )

        if therapeutic_impact > 0.8 and narrative_progression == "significant":
            return "therapeutic_success"
        if therapeutic_impact > 0.6:
            return "therapeutic_opportunity"
        if therapeutic_impact < 0.3:
            return "learning_opportunity"
        if narrative_progression == "significant":
            return "narrative_success"
        return "neutral_progression"

    async def _adapt_choice_for_emotion(
        self, choice: Choice, new_emotional_state: str
    ) -> Choice:
        """Adapt a choice for a new emotional state."""
        adapted_choice = Choice(**choice.model_dump())
        adapted_choice.choice_id = str(uuid4())  # New ID for adapted choice

        # Adjust choice text for emotional state
        if new_emotional_state in ["anxious", "overwhelmed"]:
            # Make choice more calming and supportive
            adapted_choice.choice_text = f"Gently {choice.choice_text.lower()}"
            adapted_choice.description = f"A calming approach: {choice.description}"
        elif new_emotional_state == "distressed":
            # Make choice more supportive and grounding
            adapted_choice.choice_text = f"With support, {choice.choice_text.lower()}"
            adapted_choice.description = f"A supported approach: {choice.description}"
        elif new_emotional_state == "engaged":
            # Make choice more dynamic and engaging
            adapted_choice.choice_text = f"Actively {choice.choice_text.lower()}"
            adapted_choice.description = f"An engaged approach: {choice.description}"

        # Update emotional context
        adapted_choice.emotional_context = [new_emotional_state]

        return adapted_choice

    async def _generate_fallback_choices(  # noqa: ARG002
        self, scene: Scene, session_state: SessionState
    ) -> list[Choice]:
        """Generate safe fallback choices when normal generation fails."""
        fallback_choices = []

        # Safe narrative choice
        narrative_choice = Choice(
            choice_text="Continue exploring this space",
            description="Take time to understand your current situation",
            choice_type=ChoiceType.NARRATIVE,
            therapeutic_tags=["exploration", "safety"],
            difficulty_level=DifficultyLevel.GENTLE,
            agency_level=0.7,
            meaningfulness_score=0.6,
            emotional_context=[session_state.emotional_state.value],
            therapeutic_value=0.5,
        )
        fallback_choices.append(narrative_choice)

        # Safe therapeutic choice
        therapeutic_choice = Choice(
            choice_text="Take a moment to breathe and center yourself",
            description="Use this moment for grounding and self-care",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_tags=["grounding", "mindfulness", "self_care"],
            difficulty_level=DifficultyLevel.GENTLE,
            agency_level=0.8,
            meaningfulness_score=0.7,
            emotional_context=[session_state.emotional_state.value],
            therapeutic_value=0.8,
        )
        fallback_choices.append(therapeutic_choice)

        return fallback_choices

    async def _generate_fallback_outcome(
        self, user_choice: UserChoice
    ) -> ChoiceOutcome:
        """Generate a safe fallback outcome when evaluation fails."""
        return ChoiceOutcome(
            choice_id=user_choice.choice_id,
            outcome_type="neutral_progression",
            therapeutic_impact={"therapeutic_impact_score": 0.5},
            narrative_consequences=["story_continues"],
            learning_opportunities=["self_awareness"],
            emotional_response="supportive",
            skill_development=[],
            progress_markers=[],
        )
