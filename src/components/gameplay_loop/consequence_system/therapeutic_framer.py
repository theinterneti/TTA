"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Consequence_system/Therapeutic_framer]]

# Logseq: [[TTA/Components/Gameplay_loop/Consequence_system/Therapeutic_framer]]
Therapeutic Framer for Therapeutic Text Adventure

This module implements therapeutic framing functionality that frames all
outcomes and consequences as learning opportunities and therapeutic growth
experiences, ensuring positive therapeutic value regardless of choice outcomes.
"""

from __future__ import annotations

import logging
from typing import Any

from ..models.core import ConsequenceSet, EmotionalState, SessionState
from ..models.interactions import UserChoice

logger = logging.getLogger(__name__)


class TherapeuticFramer:
    """
    Frames all outcomes and consequences as therapeutic learning opportunities
    and growth experiences, maintaining positive therapeutic value.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Therapeutic framing resources
        self.framing_templates: dict[str, dict[str, Any]] = {}
        self.learning_opportunity_patterns: dict[str, list[str]] = {}
        self.therapeutic_insight_templates: dict[str, list[str]] = {}
        self.growth_framing_strategies: dict[str, dict[str, Any]] = {}

        logger.info("TherapeuticFramer initialized")

    async def initialize(self) -> bool:
        """Initialize therapeutic framing templates and patterns."""
        try:
            await self._load_framing_templates()
            await self._load_learning_patterns()
            await self._load_insight_templates()
            await self._load_growth_strategies()

            logger.info("TherapeuticFramer initialization completed")
            return True

        except Exception as e:
            logger.error(f"TherapeuticFramer initialization failed: {e}")
            return False

    async def frame_outcomes(
        self,
        outcomes: dict[str, Any],
        user_choice: UserChoice,
        session_state: SessionState,
    ) -> dict[str, Any]:
        """
        Frame outcomes as therapeutic learning opportunities.

        Args:
            outcomes: Generated outcomes to frame
            user_choice: The choice that led to outcomes
            session_state: Current session state

        Returns:
            Dictionary with therapeutic framing
        """
        try:
            logger.info(
                f"Framing outcomes therapeutically for choice {user_choice.choice_id}"
            )

            therapeutic_framing = {
                "insights": [],
                "learning_opportunities": [],
                "therapeutic_value": 0.0,
                "growth_aspects": [],
                "positive_reframes": [],
            }

            # Generate therapeutic insights
            insights = await self._generate_therapeutic_insights(
                outcomes, user_choice, session_state
            )
            therapeutic_framing["insights"] = insights

            # Identify learning opportunities
            learning_opportunities = await self._identify_learning_opportunities(
                outcomes, user_choice
            )
            therapeutic_framing["learning_opportunities"] = learning_opportunities

            # Calculate therapeutic value
            therapeutic_value = await self._calculate_therapeutic_value(
                outcomes, user_choice
            )
            therapeutic_framing["therapeutic_value"] = therapeutic_value

            # Identify growth aspects
            growth_aspects = await self._identify_growth_aspects(
                outcomes, user_choice, session_state
            )
            therapeutic_framing["growth_aspects"] = growth_aspects

            # Generate positive reframes
            positive_reframes = await self._generate_positive_reframes(
                outcomes, session_state
            )
            therapeutic_framing["positive_reframes"] = positive_reframes

            logger.info("Therapeutic framing completed")
            return therapeutic_framing

        except Exception as e:
            logger.error(f"Failed to frame outcomes therapeutically: {e}")
            return await self._generate_fallback_framing(user_choice)

    async def adapt_framing_for_emotion(  # noqa: ARG002
        self,
        consequence_set: ConsequenceSet,
        emotional_state: str,
        session_state: SessionState,
    ) -> dict[str, Any]:
        """
        Adapt therapeutic framing for a specific emotional state.

        Args:
            consequence_set: Original consequences
            emotional_state: Target emotional state
            session_state: Current session state

        Returns:
            Adapted therapeutic framing
        """
        try:
            emotional_state_enum = EmotionalState(emotional_state)

            adapted_framing = {
                "insights": [],
                "learning_opportunities": [],
                "therapeutic_value": consequence_set.therapeutic_value_realized,
                "growth_aspects": [],
                "positive_reframes": [],
            }

            # Adapt insights for emotional state
            adapted_insights = await self._adapt_insights_for_emotion(
                consequence_set.therapeutic_insights, emotional_state_enum
            )
            adapted_framing["insights"] = adapted_insights

            # Adapt learning opportunities
            adapted_learning = await self._adapt_learning_for_emotion(
                consequence_set.learning_opportunities, emotional_state_enum
            )
            adapted_framing["learning_opportunities"] = adapted_learning

            # Adjust therapeutic value for emotional appropriateness
            adjusted_value = await self._adjust_therapeutic_value_for_emotion(
                consequence_set.therapeutic_value_realized, emotional_state_enum
            )
            adapted_framing["therapeutic_value"] = adjusted_value

            return adapted_framing

        except Exception as e:
            logger.error(f"Failed to adapt framing for emotional state: {e}")
            return {
                "therapeutic_value": 0.5,
                "insights": ["Every experience offers learning"],
            }

    # Initialization Methods
    async def _load_framing_templates(self) -> None:
        """Load therapeutic framing templates."""
        self.framing_templates = {
            "positive_outcome": {
                "insights": [
                    "Your choice demonstrates {positive_quality} and leads to {positive_result}",
                    "This outcome reflects your growing {skill_area} and {therapeutic_benefit}",
                    "You can see how {choice_aspect} creates {positive_change}",
                ],
                "learning_opportunities": [
                    "Notice how {positive_action} leads to {beneficial_outcome}",
                    "This experience strengthens your {therapeutic_skill}",
                    "You're developing greater {capacity_area}",
                ],
            },
            "challenging_outcome": {
                "insights": [
                    "Even challenging outcomes offer valuable learning about {learning_area}",
                    "This experience provides insight into {growth_opportunity}",
                    "Difficult moments often reveal our {inner_strength}",
                ],
                "learning_opportunities": [
                    "Practice {coping_skill} when facing similar challenges",
                    "Develop {resilience_aspect} through this experience",
                    "Build {therapeutic_capacity} by working with difficulty",
                ],
            },
            "neutral_outcome": {
                "insights": [
                    "Every choice contributes to your ongoing {therapeutic_journey}",
                    "This moment offers an opportunity for {mindful_awareness}",
                    "You're building {life_skill} through consistent practice",
                ],
                "learning_opportunities": [
                    "Cultivate {awareness_skill} in everyday moments",
                    "Practice {therapeutic_technique} regularly",
                    "Develop {emotional_capacity} through mindful engagement",
                ],
            },
        }

    async def _load_learning_patterns(self) -> None:
        """Load learning opportunity patterns."""
        self.learning_opportunity_patterns = {
            "self_awareness": [
                "Notice your thoughts and feelings in this moment",
                "Observe your reactions without judgment",
                "Become aware of your patterns and habits",
            ],
            "emotional_regulation": [
                "Practice working with difficult emotions",
                "Develop skills for emotional balance",
                "Learn to respond rather than react",
            ],
            "resilience_building": [
                "Build strength through facing challenges",
                "Develop coping strategies for difficult times",
                "Cultivate inner resources for support",
            ],
            "relationship_skills": [
                "Practice authentic communication",
                "Develop empathy and understanding",
                "Build healthy relationship patterns",
            ],
            "mindfulness_practice": [
                "Cultivate present-moment awareness",
                "Practice non-judgmental observation",
                "Develop mindful attention skills",
            ],
        }

    async def _load_insight_templates(self) -> None:
        """Load therapeutic insight templates."""
        self.therapeutic_insight_templates = {
            "growth_oriented": [
                "This experience shows your capacity for {growth_area}",
                "You're developing greater {therapeutic_skill} through practice",
                "Your willingness to {positive_action} demonstrates {character_strength}",
            ],
            "learning_focused": [
                "Every choice teaches us something about {learning_domain}",
                "This moment offers insight into {self_understanding_area}",
                "You're gaining wisdom about {life_skill_area}",
            ],
            "strength_based": [
                "You showed {personal_strength} in this situation",
                "Your {positive_quality} helped you navigate this challenge",
                "This demonstrates your growing {therapeutic_capacity}",
            ],
            "process_oriented": [
                "The journey of {therapeutic_process} continues to unfold",
                "Each step in your {growth_journey} has value",
                "You're engaged in the important work of {therapeutic_goal}",
            ],
        }

    async def _load_growth_strategies(self) -> None:
        """Load growth framing strategies."""
        self.growth_framing_strategies = {
            "reframe_challenges": {
                "strategy": "Present challenges as growth opportunities",
                "templates": [
                    "This challenge offers a chance to develop {skill}",
                    "Difficult moments help us discover our {strength}",
                    "Working through this builds {therapeutic_capacity}",
                ],
            },
            "highlight_progress": {
                "strategy": "Emphasize progress and development",
                "templates": [
                    "Notice how you've grown in {area}",
                    "Your {skill} is developing through practice",
                    "You're making progress in {therapeutic_goal}",
                ],
            },
            "connect_to_values": {
                "strategy": "Link outcomes to personal values and meaning",
                "templates": [
                    "This aligns with your value of {personal_value}",
                    "Your choice reflects what matters most to you",
                    "This supports your goal of {meaningful_objective}",
                ],
            },
            "normalize_experience": {
                "strategy": "Normalize and validate the human experience",
                "templates": [
                    "This is a natural part of the {therapeutic_process}",
                    "Many people experience {common_challenge}",
                    "Your response shows your humanity and {positive_quality}",
                ],
            },
        }

    # Core Framing Methods
    async def _generate_therapeutic_insights(  # noqa: ARG002
        self,
        outcomes: dict[str, Any],
        user_choice: UserChoice,
        session_state: SessionState,
    ) -> list[str]:
        """Generate therapeutic insights from outcomes and choice."""
        insights = []

        if user_choice.therapeutic_value > 0.7:
            insights.append(
                "Your choice demonstrates strong therapeutic engagement and self-awareness."
            )
        elif user_choice.therapeutic_value > 0.4:
            insights.append(
                "This choice reflects your ongoing therapeutic journey and growth."
            )
        else:
            insights.append("Every choice offers an opportunity for learning and growth.")

        if outcomes.get("emotional_impact", {}).get("primary_emotion") in [
            "positive",
            "hopeful",
            "empowered",
        ]:
            insights.append(
                "Notice the positive emotional shift this choice creates."
            )

        return insights

    async def _identify_learning_opportunities(  # noqa: ARG002
        self,
        outcomes: dict[str, Any],
        user_choice: UserChoice,
    ) -> list[str]:
        """Identify learning opportunities from outcomes and choice."""
        opportunities = []

        for tag in user_choice.therapeutic_tags:
            if tag in self.learning_opportunity_patterns:
                opportunities.extend(self.learning_opportunity_patterns[tag][:1])

        if not opportunities:
            opportunities.append("Reflect on what this choice reveals about your values.")

        return opportunities

    async def _calculate_therapeutic_value(
        self,
        outcomes: dict[str, Any],
        user_choice: UserChoice,
    ) -> float:
        """Calculate the therapeutic value of outcomes."""
        base_value = user_choice.therapeutic_value

        # Boost for positive emotional outcomes
        emotional_impact = outcomes.get("emotional_impact", {})
        if emotional_impact.get("primary_emotion") in ["positive", "hopeful", "empowered"]:
            base_value = min(1.0, base_value + 0.1)

        return base_value

    async def _identify_growth_aspects(  # noqa: ARG002
        self,
        outcomes: dict[str, Any],
        user_choice: UserChoice,
        session_state: SessionState,
    ) -> list[str]:
        """Identify aspects of growth demonstrated in choice and outcomes."""
        growth_aspects = []

        if user_choice.therapeutic_value > 0.6:
            growth_aspects.append("therapeutic_engagement")

        growth_aspects.extend(
            tag
            for tag in user_choice.therapeutic_tags
            if tag in ["resilience", "self_compassion", "mindfulness"]
        )

        return growth_aspects

    async def _generate_positive_reframes(  # noqa: ARG002
        self,
        outcomes: dict[str, Any],
        session_state: SessionState,
    ) -> list[str]:
        """Generate positive reframes for outcomes."""
        reframes = []

        strategy = self.growth_framing_strategies.get("reframe_challenges", {})
        templates = strategy.get("templates", [])
        if templates:
            reframes.append(
                templates[0].format(
                    skill="self-awareness",
                    strength="inner resilience",
                    therapeutic_capacity="emotional regulation",
                )
            )

        reframes.append("This experience contributes to your ongoing growth and healing.")

        return reframes

    async def _generate_fallback_framing(
        self, user_choice: UserChoice
    ) -> dict[str, Any]:
        """Generate safe fallback therapeutic framing."""
        return {
            "insights": ["Every experience offers an opportunity for learning and growth."],
            "learning_opportunities": ["Reflect on what this moment reveals about your journey."],
            "therapeutic_value": max(0.3, user_choice.therapeutic_value),
            "growth_aspects": ["therapeutic_participation"],
            "positive_reframes": ["This experience is part of your healing journey."],
        }

    async def _adapt_insights_for_emotion(
        self,
        insights: list[str],
        emotional_state: EmotionalState,
    ) -> list[str]:
        """Adapt therapeutic insights for a specific emotional state."""
        if not insights:
            return ["Every experience offers an opportunity for growth."]

        if emotional_state in [EmotionalState.CRISIS, EmotionalState.DISTRESSED]:
            return [
                "You are safe. Focus on what feels grounding and supportive right now."
            ]

        if emotional_state in [EmotionalState.ANXIOUS, EmotionalState.OVERWHELMED]:
            return [insight + " Take it one step at a time." for insight in insights[:1]]

        return insights

    async def _adapt_learning_for_emotion(
        self,
        learning_opportunities: list[str],
        emotional_state: EmotionalState,
    ) -> list[str]:
        """Adapt learning opportunities for a specific emotional state."""
        if emotional_state in [EmotionalState.CRISIS, EmotionalState.DISTRESSED]:
            return ["Focus on safety and grounding in this moment."]

        if emotional_state in [EmotionalState.ANXIOUS, EmotionalState.OVERWHELMED]:
            return learning_opportunities[:1] if learning_opportunities else [
                "Practice one small grounding technique."
            ]

        return learning_opportunities

    async def _adjust_therapeutic_value_for_emotion(
        self,
        therapeutic_value: float,
        emotional_state: EmotionalState,
    ) -> float:
        """Adjust therapeutic value based on emotional state appropriateness."""
        if emotional_state in [EmotionalState.CRISIS, EmotionalState.DISTRESSED]:
            # In crisis, any engagement has high therapeutic value
            return max(therapeutic_value, 0.7)

        if emotional_state in [EmotionalState.ANXIOUS, EmotionalState.OVERWHELMED]:
            # Slightly boost value for anxious states to encourage engagement
            return min(1.0, therapeutic_value + 0.05)

        return therapeutic_value
