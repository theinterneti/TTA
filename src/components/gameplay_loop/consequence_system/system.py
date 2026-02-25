"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Consequence_system/System]]

# Logseq: [[TTA/Components/Gameplay_loop/Consequence_system/System]]
Main Consequence System for Therapeutic Text Adventure

This module implements the main consequence system that orchestrates the
generation of logical, meaningful outcomes from player choices while
ensuring therapeutic value and clear causality understanding.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from ..models.core import ConsequenceSet, Scene, SessionState
from ..models.interactions import UserChoice
from .causality_explainer import CausalityExplainer
from .outcome_generator import OutcomeGenerator
from .progress_tracker import ProgressTracker
from .therapeutic_framer import TherapeuticFramer

logger = logging.getLogger(__name__)


class ConsequenceSystem:
    """
    Main consequence system that orchestrates the generation of logical,
    meaningful outcomes from player choices with therapeutic framing.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Initialize subsystems
        self.outcome_generator = OutcomeGenerator(self.config.get("outcome_generation", {}))
        self.therapeutic_framer = TherapeuticFramer(
            self.config.get("therapeutic_framing", {})
        )
        self.causality_explainer = CausalityExplainer(
            self.config.get("causality_explanation", {})
        )
        self.progress_tracker = ProgressTracker(self.config.get("progress_tracking", {}))

        # System configuration
        self.consequence_depth = self.config.get("consequence_depth", "moderate")
        self.therapeutic_emphasis = self.config.get("therapeutic_emphasis", 0.7)
        self.causality_clarity = self.config.get("causality_clarity", "high")

        logger.info("ConsequenceSystem initialized")

    async def initialize(self) -> bool:
        """Initialize the consequence system and all subsystems."""
        try:
            await self.outcome_generator.initialize()
            await self.therapeutic_framer.initialize()
            await self.causality_explainer.initialize()
            await self.progress_tracker.initialize()

            logger.info("ConsequenceSystem initialization completed")
            return True

        except Exception as e:
            logger.error(f"ConsequenceSystem initialization failed: {e}")
            return False

    async def generate_consequences(
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> ConsequenceSet:
        """
        Generate comprehensive consequences for a user's choice.

        Args:
            user_choice: The choice made by the user
            scene: The scene where the choice was made
            session_state: Current session state

        Returns:
            ConsequenceSet with all generated consequences and explanations
        """
        try:
            logger.info(f"Generating consequences for choice {user_choice.choice_id}")

            # Generate logical outcomes
            outcomes = await self.outcome_generator.generate_outcomes(
                user_choice, scene, session_state
            )

            # Frame outcomes therapeutically
            therapeutic_framing = await self.therapeutic_framer.frame_outcomes(
                outcomes, user_choice, session_state
            )

            # Generate causality explanations
            causality_explanation = await self.causality_explainer.explain_causality(
                user_choice, outcomes, scene, session_state
            )

            # Track therapeutic progress
            progress_update = await self.progress_tracker.track_progress(
                user_choice, outcomes, session_state
            )

            # Create comprehensive consequence set
            consequence_set = ConsequenceSet(
                choice_id=user_choice.choice_id,
                immediate_outcomes=outcomes.get("immediate", []),
                delayed_outcomes=outcomes.get("delayed", []),
                therapeutic_insights=therapeutic_framing.get("insights", []),
                learning_opportunities=therapeutic_framing.get(
                    "learning_opportunities", []
                ),
                causality_explanation=causality_explanation,
                progress_markers=progress_update.get("progress_markers", []),
                skill_development=progress_update.get("skill_development", []),
                emotional_impact=outcomes.get("emotional_impact", {}),
                narrative_consequences=outcomes.get("narrative", []),
                character_development=outcomes.get("character_development", {}),
                world_state_changes=outcomes.get("world_state_changes", {}),
                therapeutic_value_realized=therapeutic_framing.get(
                    "therapeutic_value", 0.0
                ),
            )

            logger.info("Generated comprehensive consequences for choice")
            return consequence_set

        except Exception as e:
            logger.error(f"Failed to generate consequences: {e}")
            return await self._generate_fallback_consequences(user_choice)

    async def evaluate_consequence_impact(
        self, consequence_set: ConsequenceSet, session_state: SessionState
    ) -> dict[str, Any]:
        """
        Evaluate the overall impact of a consequence set.

        Args:
            consequence_set: The consequences to evaluate
            session_state: Current session state

        Returns:
            Dictionary with impact analysis
        """
        try:
            impact_analysis = {
                "therapeutic_impact": 0.0,
                "narrative_impact": 0.0,
                "emotional_impact": 0.0,
                "learning_impact": 0.0,
                "overall_impact": 0.0,
                "impact_areas": [],
                "growth_indicators": [],
            }

            # Evaluate therapeutic impact
            therapeutic_impact = await self._evaluate_therapeutic_impact(
                consequence_set
            )
            impact_analysis["therapeutic_impact"] = therapeutic_impact

            # Evaluate narrative impact
            narrative_impact = await self._evaluate_narrative_impact(consequence_set)
            impact_analysis["narrative_impact"] = narrative_impact

            # Evaluate emotional impact
            emotional_impact = await self._evaluate_emotional_impact(
                consequence_set, session_state
            )
            impact_analysis["emotional_impact"] = emotional_impact

            # Evaluate learning impact
            learning_impact = await self._evaluate_learning_impact(consequence_set)
            impact_analysis["learning_impact"] = learning_impact

            # Calculate overall impact
            impact_analysis["overall_impact"] = (
                therapeutic_impact * 0.4
                + narrative_impact * 0.2
                + emotional_impact * 0.2
                + learning_impact * 0.2
            )

            # Identify impact areas
            impact_analysis["impact_areas"] = await self._identify_impact_areas(
                consequence_set
            )

            # Identify growth indicators
            impact_analysis[
                "growth_indicators"
            ] = await self._identify_growth_indicators(consequence_set)

            return impact_analysis

        except Exception as e:
            logger.error(f"Failed to evaluate consequence impact: {e}")
            return {"overall_impact": 0.5, "therapeutic_impact": 0.5}

    async def adapt_consequences_for_emotional_state(
        self,
        consequence_set: ConsequenceSet,
        new_emotional_state: str,
        session_state: SessionState,
    ) -> ConsequenceSet:
        """
        Adapt consequences for a changed emotional state.

        Args:
            consequence_set: Original consequences
            new_emotional_state: New emotional state to adapt for
            session_state: Current session state

        Returns:
            Adapted consequence set
        """
        try:
            logger.info(
                f"Adapting consequences for emotional state: {new_emotional_state}"
            )

            # Re-frame therapeutically for new emotional state
            adapted_framing = await self.therapeutic_framer.adapt_framing_for_emotion(
                consequence_set, new_emotional_state, session_state
            )

            # Adjust causality explanation for emotional state
            adapted_explanation = (
                await self.causality_explainer.adapt_explanation_for_emotion(
                    consequence_set.causality_explanation, new_emotional_state
                )
            )

            # Create adapted consequence set
            adapted_consequence_set = ConsequenceSet(**consequence_set.model_dump())
            adapted_consequence_set.consequence_id = str(
                uuid4()
            )  # New ID for adapted version

            # Update with adapted content
            adapted_consequence_set.therapeutic_insights = adapted_framing.get(
                "insights", []
            )
            adapted_consequence_set.learning_opportunities = adapted_framing.get(
                "learning_opportunities", []
            )
            adapted_consequence_set.causality_explanation = adapted_explanation
            adapted_consequence_set.therapeutic_value_realized = adapted_framing.get(
                "therapeutic_value", 0.0
            )

            logger.info("Consequences adapted for new emotional state")
            return adapted_consequence_set

        except Exception as e:
            logger.error(f"Failed to adapt consequences for emotional state: {e}")
            return consequence_set  # Return original if adaptation fails

    # Helper Methods
    async def _generate_fallback_consequences(
        self, user_choice: UserChoice
    ) -> ConsequenceSet:
        """Generate safe fallback consequences when normal generation fails."""
        return ConsequenceSet(
            choice_id=user_choice.choice_id,
            immediate_outcomes=["Your choice leads to new understanding"],
            delayed_outcomes=[],
            therapeutic_insights=["Every choice is an opportunity for growth"],
            learning_opportunities=["self_awareness", "choice_reflection"],
            causality_explanation="Your choice reflects your current state and opens new possibilities",
            progress_markers=[],
            skill_development=[],
            emotional_impact={"primary_emotion": "neutral", "intensity": 0.5},
            narrative_consequences=["The story continues"],
            character_development={},
            world_state_changes={},
            therapeutic_value_realized=0.5,
        )

    # Evaluation Methods
    async def _evaluate_therapeutic_impact(
        self, consequence_set: ConsequenceSet
    ) -> float:
        """Evaluate the therapeutic impact of consequences."""
        impact_score = 0.0

        # Base therapeutic value
        impact_score += consequence_set.therapeutic_value_realized * 0.4

        # Therapeutic insights count and quality
        insights_count = len(consequence_set.therapeutic_insights)
        impact_score += min(insights_count * 0.1, 0.3)

        # Learning opportunities
        learning_count = len(consequence_set.learning_opportunities)
        impact_score += min(learning_count * 0.05, 0.2)

        # Progress markers
        progress_count = len(consequence_set.progress_markers)
        impact_score += min(progress_count * 0.02, 0.1)

        return min(impact_score, 1.0)

    async def _evaluate_narrative_impact(
        self, consequence_set: ConsequenceSet
    ) -> float:
        """Evaluate the narrative impact of consequences."""
        impact_score = 0.0

        # Narrative consequences count
        narrative_count = len(consequence_set.narrative_consequences)
        impact_score += min(narrative_count * 0.2, 0.6)

        # Character development impact
        if consequence_set.character_development:
            development_areas = len(consequence_set.character_development)
            impact_score += min(development_areas * 0.1, 0.3)

        # World state changes
        if consequence_set.world_state_changes:
            world_changes = len(consequence_set.world_state_changes)
            impact_score += min(world_changes * 0.05, 0.1)

        return min(impact_score, 1.0)

    async def _evaluate_emotional_impact(  # noqa: ARG002
        self, consequence_set: ConsequenceSet, session_state: SessionState
    ) -> float:
        """Evaluate the emotional impact of consequences."""
        impact_score = 0.0

        # Emotional impact intensity
        if consequence_set.emotional_impact:
            intensity = consequence_set.emotional_impact.get("intensity", 0.5)
            impact_score += intensity * 0.5

            # Positive emotional progression
            primary_emotion = consequence_set.emotional_impact.get(
                "primary_emotion", "neutral"
            )
            if primary_emotion in ["positive", "hopeful", "empowered", "calm"]:
                impact_score += 0.3
            elif primary_emotion in ["reflective", "aware", "understanding"]:
                impact_score += 0.2

        # Emotional growth indicators
        if "emotional_growth" in consequence_set.skill_development:
            impact_score += 0.2

        return min(impact_score, 1.0)

    async def _evaluate_learning_impact(self, consequence_set: ConsequenceSet) -> float:
        """Evaluate the learning impact of consequences."""
        impact_score = 0.0

        # Learning opportunities count and quality
        learning_count = len(consequence_set.learning_opportunities)
        impact_score += min(learning_count * 0.15, 0.6)

        # Skill development
        skill_count = len(consequence_set.skill_development)
        impact_score += min(skill_count * 0.1, 0.3)

        # Causality explanation clarity (proxy for learning)
        if (
            consequence_set.causality_explanation
            and len(consequence_set.causality_explanation) > 50
        ):
            impact_score += 0.1

        return min(impact_score, 1.0)

    async def _identify_impact_areas(
        self, consequence_set: ConsequenceSet
    ) -> list[str]:
        """Identify areas where consequences have impact."""
        impact_areas = []

        # Therapeutic areas
        if consequence_set.therapeutic_insights:
            impact_areas.append("therapeutic_insight")
        if consequence_set.learning_opportunities:
            impact_areas.append("learning_development")
        if consequence_set.progress_markers:
            impact_areas.append("therapeutic_progress")

        # Narrative areas
        if consequence_set.narrative_consequences:
            impact_areas.append("story_progression")
        if consequence_set.character_development:
            impact_areas.append("character_growth")
        if consequence_set.world_state_changes:
            impact_areas.append("world_evolution")

        # Emotional areas
        if consequence_set.emotional_impact:
            impact_areas.append("emotional_development")

        # Skill areas
        if consequence_set.skill_development:
            impact_areas.append("skill_building")

        return impact_areas

    async def _identify_growth_indicators(
        self, consequence_set: ConsequenceSet
    ) -> list[str]:
        """Identify indicators of player growth from consequences."""
        growth_indicators = []

        # High therapeutic value
        if consequence_set.therapeutic_value_realized > 0.7:
            growth_indicators.append("high_therapeutic_value")

        # Multiple learning opportunities
        if len(consequence_set.learning_opportunities) >= 2:
            growth_indicators.append("multiple_learning_paths")

        # Progress markers present
        if consequence_set.progress_markers:
            growth_indicators.append("measurable_progress")

        # Skill development
        if consequence_set.skill_development:
            growth_indicators.append("skill_advancement")

        # Positive emotional impact
        if consequence_set.emotional_impact:
            primary_emotion = consequence_set.emotional_impact.get(
                "primary_emotion", "neutral"
            )
            if primary_emotion in ["positive", "hopeful", "empowered"]:
                growth_indicators.append("positive_emotional_growth")

        # Character development
        if consequence_set.character_development:
            growth_indicators.append("character_evolution")

        return growth_indicators
