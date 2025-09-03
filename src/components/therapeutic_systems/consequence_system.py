"""
Therapeutic ConsequenceSystem Implementation

This module provides the production ConsequenceSystem that provides the interface
expected by the E2E testing framework and therapeutic workflows, implementing
evidence-based therapeutic consequence generation.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class TherapeuticApproach(Enum):
    """Therapeutic approaches supported by the system."""

    CBT = "cognitive_behavioral_therapy"
    DBT = "dialectical_behavior_therapy"
    MINDFULNESS = "mindfulness_based_therapy"
    ACT = "acceptance_commitment_therapy"
    TRAUMA_INFORMED = "trauma_informed_care"
    MOTIVATIONAL_INTERVIEWING = "motivational_interviewing"
    SOLUTION_FOCUSED = "solution_focused_brief_therapy"
    NARRATIVE_THERAPY = "narrative_therapy"


class ChoiceType(Enum):
    """Types of choices users can make."""

    THERAPEUTIC = "therapeutic"
    SOCIAL = "social"
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    NARRATIVE = "narrative"
    BEHAVIORAL = "behavioral"


class TherapeuticConsequenceSystem:
    """
    Therapeutic ConsequenceSystem that provides evidence-based consequence
    generation for therapeutic text adventures.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the therapeutic consequence system."""
        self.config = config or {}

        # Therapeutic framework mappings
        self.therapeutic_frameworks = {
            TherapeuticApproach.CBT: self._apply_cbt_framework,
            TherapeuticApproach.DBT: self._apply_dbt_framework,
            TherapeuticApproach.MINDFULNESS: self._apply_mindfulness_framework,
            TherapeuticApproach.ACT: self._apply_act_framework,
        }

        # Character attribute mappings
        self.attribute_mappings = {
            "courage": ["brave", "confront", "challenge", "face", "bold"],
            "wisdom": [
                "think",
                "learn",
                "reflect",
                "consider",
                "thoughtful",
                "experience",
            ],
            "compassion": ["help", "care", "empathy", "kindness", "support"],
            "resilience": ["overcome", "bounce", "persevere", "endure", "recover"],
            "communication": ["express", "listen", "talk", "share", "communicate"],
            "emotional_intelligence": [
                "feel",
                "emotion",
                "understand",
                "aware",
                "sense",
            ],
        }

        logger.info("TherapeuticConsequenceSystem initialized")

    async def initialize(self):
        """Initialize the therapeutic consequence system."""
        # Any async initialization can go here
        logger.info("TherapeuticConsequenceSystem initialization complete")

    async def process_choice_consequence(
        self,
        user_id: str,
        choice: str,
        scenario_context: dict[str, Any] | None = None,
        therapeutic_goals: list[str] | None = None,
        user_preferences: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process a user choice and generate therapeutic consequences.

        This method provides the interface expected by E2E tests and implements
        evidence-based therapeutic consequence generation.

        Args:
            user_id: Unique identifier for the user
            choice: The choice text made by the user
            scenario_context: Context about the current scenario
            therapeutic_goals: List of therapeutic goals for the user
            user_preferences: User's therapeutic preferences

        Returns:
            Dictionary containing consequence information with keys:
            - consequence_id: Unique identifier for this consequence
            - therapeutic_value: Float between 0-1 indicating therapeutic benefit
            - learning_opportunity: Text describing the learning opportunity
            - character_impact: Dict mapping attributes to impact values
        """
        try:
            start_time = datetime.utcnow()

            # Handle empty/invalid input early
            if not choice or not user_id:
                return {
                    "consequence_id": str(uuid4()),
                    "therapeutic_value": 0.5,  # Neutral therapeutic value for empty input
                    "learning_opportunity": "Every choice provides an opportunity for growth and learning.",
                    "character_impact": {
                        "resilience": 0.05
                    },  # Small resilience boost for trying
                    "processing_time": 0.001,
                    "choice_analysis": {
                        "choice_type": "narrative",
                        "therapeutic_relevance": 0.0,
                        "emotional_weight": 0.0,
                    },
                }

            # Analyze the choice
            choice_type = self._determine_choice_type(choice, scenario_context)
            therapeutic_relevance = self._calculate_therapeutic_relevance(
                choice, therapeutic_goals
            )
            emotional_weight = self._calculate_emotional_weight(
                choice, scenario_context
            )

            # Calculate therapeutic value
            therapeutic_value = self._calculate_therapeutic_value_direct(
                choice,
                therapeutic_goals,
                scenario_context,
                therapeutic_relevance,
                emotional_weight,
            )

            # Generate learning opportunity text
            learning_opportunity = self._generate_learning_opportunity_direct(
                choice, therapeutic_goals, choice_type
            )

            # Calculate character attribute impacts
            character_impact = self._calculate_character_impact_direct(
                choice, scenario_context, choice_type
            )

            # Apply therapeutic framework enhancements
            if user_preferences and "preferred_approaches" in user_preferences:
                for approach in user_preferences["preferred_approaches"]:
                    if approach in self.therapeutic_frameworks:
                        (
                            therapeutic_value,
                            learning_opportunity,
                            character_impact,
                        ) = await self.therapeutic_frameworks[approach](
                            therapeutic_value,
                            learning_opportunity,
                            character_impact,
                            choice,
                            scenario_context,
                        )

            processing_time = datetime.utcnow() - start_time
            logger.debug(
                f"Processed choice consequence for user {user_id} in {processing_time.total_seconds():.3f}s"
            )

            return {
                "consequence_id": str(uuid4()),
                "therapeutic_value": therapeutic_value,
                "learning_opportunity": learning_opportunity,
                "character_impact": character_impact,
                "processing_time": processing_time.total_seconds(),
                "choice_analysis": {
                    "choice_type": choice_type.value,
                    "therapeutic_relevance": therapeutic_relevance,
                    "emotional_weight": emotional_weight,
                },
            }

        except Exception as e:
            logger.error(f"Error processing choice consequence for user {user_id}: {e}")

            # For empty/invalid choices, still provide some therapeutic value
            # but use fallback logic for edge cases
            if not choice or not user_id:
                therapeutic_value = 0.5  # Neutral for truly empty input
            else:
                # Even invalid input gets some therapeutic value for trying
                therapeutic_value = 0.6

            # Return fallback consequence
            return {
                "consequence_id": str(uuid4()),
                "therapeutic_value": therapeutic_value,
                "learning_opportunity": "Every choice provides an opportunity for growth and learning.",
                "character_impact": {
                    "resilience": 0.1
                },  # Small resilience boost for trying
                "error": str(e),
            }

    def _determine_choice_type(
        self, choice: str, scenario_context: dict[str, Any] | None
    ) -> ChoiceType:
        """Determine the type of choice based on content and context."""
        choice_lower = choice.lower()

        if scenario_context and scenario_context.get("type") == "therapeutic":
            return ChoiceType.THERAPEUTIC
        elif any(
            word in choice_lower for word in ["help", "support", "care", "comfort"]
        ):
            return ChoiceType.SOCIAL
        elif any(
            word in choice_lower for word in ["think", "consider", "reflect", "analyze"]
        ):
            return ChoiceType.COGNITIVE
        elif any(
            word in choice_lower for word in ["feel", "emotion", "heart", "sense"]
        ):
            return ChoiceType.EMOTIONAL
        elif any(word in choice_lower for word in ["do", "act", "perform", "practice"]):
            return ChoiceType.BEHAVIORAL
        else:
            return ChoiceType.NARRATIVE

    def _calculate_therapeutic_relevance(
        self, choice: str, therapeutic_goals: list[str] | None
    ) -> float:
        """Calculate how relevant the choice is to therapeutic goals."""
        if not therapeutic_goals:
            return 0.5  # Neutral relevance

        choice_lower = choice.lower()
        relevance_scores = []

        for goal in therapeutic_goals:
            goal_lower = goal.lower()
            if goal_lower in choice_lower:
                relevance_scores.append(0.9)
            elif any(
                keyword in choice_lower
                for keyword in self._get_goal_keywords(goal_lower)
            ):
                relevance_scores.append(0.7)
            else:
                relevance_scores.append(0.3)

        return sum(relevance_scores) / len(relevance_scores)

    def _calculate_emotional_weight(
        self, choice: str, scenario_context: dict[str, Any] | None
    ) -> float:
        """Calculate the emotional weight of the choice."""
        choice_lower = choice.lower()

        # High emotional weight words
        high_emotion_words = [
            "love",
            "hate",
            "fear",
            "anger",
            "joy",
            "sadness",
            "anxiety",
            "depression",
        ]
        medium_emotion_words = [
            "like",
            "dislike",
            "worry",
            "hope",
            "concern",
            "excited",
        ]

        if any(word in choice_lower for word in high_emotion_words):
            return 0.8
        elif any(word in choice_lower for word in medium_emotion_words):
            return 0.6
        elif (
            scenario_context
            and scenario_context.get("emotional_intensity", "medium") == "high"
        ):
            return 0.7
        else:
            return 0.4

    def _calculate_therapeutic_value_direct(
        self,
        choice: str,
        therapeutic_goals: list[str] | None,
        scenario_context: dict[str, Any] | None,
        therapeutic_relevance: float,
        emotional_weight: float,
    ) -> float:
        """Calculate the therapeutic value directly from choice analysis."""
        base_value = 0.6  # Base therapeutic value

        # Boost based on therapeutic relevance
        base_value += therapeutic_relevance * 0.2

        # Boost based on emotional engagement (moderate levels are optimal)
        if 0.4 <= emotional_weight <= 0.7:
            base_value += 0.1  # Sweet spot for therapeutic engagement
        elif emotional_weight > 0.7:
            base_value += 0.05  # High emotion can be therapeutic but needs care

        # Boost based on scenario type
        if scenario_context:
            scenario_type = scenario_context.get("type", "")
            if scenario_type in [
                "therapeutic",
                "social_anxiety",
                "confidence_building",
            ]:
                base_value += 0.1
            elif scenario_type in ["crisis", "trauma"]:
                base_value += 0.15  # Crisis scenarios have high therapeutic potential

        # Boost based on therapeutic goals alignment
        if therapeutic_goals:
            choice_lower = choice.lower()
            goal_matches = sum(
                1
                for goal in therapeutic_goals
                if any(
                    keyword in choice_lower for keyword in self._get_goal_keywords(goal)
                )
            )
            base_value += min(goal_matches * 0.05, 0.15)

        # Ensure value stays within bounds
        return min(max(base_value, 0.0), 1.0)

    def _generate_learning_opportunity_direct(
        self,
        choice: str,
        therapeutic_goals: list[str] | None,
        choice_type: ChoiceType,
    ) -> str:
        """Generate a learning opportunity description directly from choice analysis."""
        choice.lower()

        # Generate based on choice type
        if choice_type == ChoiceType.THERAPEUTIC:
            base_message = "This therapeutic choice demonstrates your commitment to growth and healing."
        elif choice_type == ChoiceType.SOCIAL:
            base_message = "This social choice helps you practice interpersonal skills and build connections."
        elif choice_type == ChoiceType.COGNITIVE:
            base_message = "This thoughtful choice shows your ability to reflect and make reasoned decisions."
        elif choice_type == ChoiceType.EMOTIONAL:
            base_message = "This emotionally aware choice helps you understand and process your feelings."
        elif choice_type == ChoiceType.BEHAVIORAL:
            base_message = "This action-oriented choice demonstrates your willingness to try new behaviors."
        else:
            base_message = (
                "This choice provides valuable experience for your personal journey."
            )

        # Add goal-specific insights
        if therapeutic_goals:
            primary_goal = therapeutic_goals[0].replace("_", " ")
            goal_insight = f" It specifically supports your goal of {primary_goal}."

            # Add specific insights based on goal type
            if "anxiety" in primary_goal:
                goal_insight += (
                    " Notice how facing challenges builds your confidence over time."
                )
            elif "confidence" in primary_goal:
                goal_insight += " Each brave choice strengthens your self-belief."
            elif "social" in primary_goal:
                goal_insight += " Practicing social interactions improves your communication skills."
            elif "emotional" in primary_goal:
                goal_insight += " Recognizing emotions is the first step to managing them effectively."

            return base_message + goal_insight

        return base_message + " Reflect on what you learned from this experience."

    def _calculate_character_impact_direct(
        self,
        choice: str,
        scenario_context: dict[str, Any] | None,
        choice_type: ChoiceType,
    ) -> dict[str, float]:
        """Calculate the impact on character attributes directly from choice analysis."""
        impact = {}
        choice_lower = choice.lower()

        # Base impact based on choice type
        if choice_type == ChoiceType.THERAPEUTIC:
            impact["wisdom"] = 0.08
            impact["resilience"] = 0.06
        elif choice_type == ChoiceType.SOCIAL:
            impact["communication"] = 0.1
            impact["compassion"] = 0.05
        elif choice_type == ChoiceType.COGNITIVE:
            impact["wisdom"] = 0.1
            impact["emotional_intelligence"] = 0.04
        elif choice_type == ChoiceType.EMOTIONAL:
            impact["emotional_intelligence"] = 0.1
            impact["resilience"] = 0.04
        elif choice_type == ChoiceType.BEHAVIORAL:
            impact["courage"] = 0.08
            impact["resilience"] = 0.06

        # Analyze choice for specific attribute keywords
        for attribute, keywords in self.attribute_mappings.items():
            if any(keyword in choice_lower for keyword in keywords):
                if attribute in impact:
                    impact[attribute] += 0.05  # Boost existing impact
                else:
                    impact[attribute] = 0.08  # New impact

        # Scenario-specific boosts
        if scenario_context:
            scenario_type = scenario_context.get("type", "")
            difficulty = scenario_context.get("difficulty", "moderate")

            if scenario_type == "social_anxiety":
                impact["courage"] = impact.get("courage", 0) + 0.06
                impact["communication"] = impact.get("communication", 0) + 0.04
            elif scenario_type == "confidence_building":
                impact["courage"] = impact.get("courage", 0) + 0.08
                impact["resilience"] = impact.get("resilience", 0) + 0.04
            elif scenario_type == "crisis":
                impact["resilience"] = impact.get("resilience", 0) + 0.1
                impact["emotional_intelligence"] = (
                    impact.get("emotional_intelligence", 0) + 0.06
                )

            # Difficulty multiplier
            if difficulty == "hard":
                for attr in impact:
                    impact[attr] *= 1.2
            elif difficulty == "easy":
                for attr in impact:
                    impact[attr] *= 0.8

        # Ensure at least one attribute is impacted
        if not impact:
            impact["resilience"] = 0.05  # Small resilience boost for making any choice

        # Cap all impacts at reasonable levels
        for attr in impact:
            impact[attr] = min(impact[attr], 0.2)  # Cap at 0.2 per choice

        return impact

    def _get_goal_keywords(self, goal: str) -> list[str]:
        """Get keywords associated with a therapeutic goal."""
        goal_keywords = {
            "anxiety_management": ["calm", "relax", "breathe", "peace", "comfort"],
            "confidence_building": [
                "confident",
                "strong",
                "capable",
                "believe",
                "trust",
            ],
            "social_skills": ["talk", "communicate", "listen", "share", "connect"],
            "emotional_regulation": ["feel", "emotion", "manage", "control", "balance"],
            "stress_management": ["stress", "pressure", "overwhelm", "cope", "handle"],
        }
        return goal_keywords.get(goal, [])

    async def _apply_cbt_framework(
        self,
        therapeutic_value: float,
        learning_opportunity: str,
        character_impact: dict[str, float],
        choice: str,
        scenario_context: dict[str, Any] | None,
    ) -> tuple[float, str, dict[str, float]]:
        """Apply CBT framework enhancements."""
        # CBT focuses on thought-behavior connections
        enhanced_learning = f"CBT Insight: {learning_opportunity} Consider how your thoughts influenced this choice and its outcomes."

        # Boost wisdom for cognitive choices
        if "wisdom" not in character_impact:
            character_impact["wisdom"] = 0.05
        else:
            character_impact["wisdom"] += 0.05

        return therapeutic_value + 0.1, enhanced_learning, character_impact

    async def _apply_dbt_framework(
        self,
        therapeutic_value: float,
        learning_opportunity: str,
        character_impact: dict[str, float],
        choice: str,
        scenario_context: dict[str, Any] | None,
    ) -> tuple[float, str, dict[str, float]]:
        """Apply DBT framework enhancements."""
        # DBT focuses on emotional regulation and distress tolerance
        enhanced_learning = f"DBT Skill: {learning_opportunity} Practice mindfulness and observe your emotions without judgment."

        # Boost emotional intelligence
        if "emotional_intelligence" not in character_impact:
            character_impact["emotional_intelligence"] = 0.05
        else:
            character_impact["emotional_intelligence"] += 0.05

        return therapeutic_value + 0.1, enhanced_learning, character_impact

    async def _apply_mindfulness_framework(
        self,
        therapeutic_value: float,
        learning_opportunity: str,
        character_impact: dict[str, float],
        choice: str,
        scenario_context: dict[str, Any] | None,
    ) -> tuple[float, str, dict[str, float]]:
        """Apply Mindfulness framework enhancements."""
        # Mindfulness focuses on present-moment awareness
        enhanced_learning = f"Mindfulness Practice: {learning_opportunity} Notice what you're experiencing right now without trying to change it."

        # Boost wisdom and emotional intelligence
        for attr in ["wisdom", "emotional_intelligence"]:
            if attr not in character_impact:
                character_impact[attr] = 0.03
            else:
                character_impact[attr] += 0.03

        return therapeutic_value + 0.08, enhanced_learning, character_impact

    async def _apply_act_framework(
        self,
        therapeutic_value: float,
        learning_opportunity: str,
        character_impact: dict[str, float],
        choice: str,
        scenario_context: dict[str, Any] | None,
    ) -> tuple[float, str, dict[str, float]]:
        """Apply ACT framework enhancements."""
        # ACT focuses on values-based action and psychological flexibility
        enhanced_learning = f"ACT Values: {learning_opportunity} Consider how this choice aligns with your core values and what matters most to you."

        # Boost courage and resilience for values-based action
        for attr in ["courage", "resilience"]:
            if attr not in character_impact:
                character_impact[attr] = 0.04
            else:
                character_impact[attr] += 0.04

        return therapeutic_value + 0.09, enhanced_learning, character_impact

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the therapeutic consequence system."""
        return {
            "status": "healthy",
            "therapeutic_system": "operational",
            "therapeutic_frameworks": len(self.therapeutic_frameworks),
            "attribute_mappings": len(self.attribute_mappings),
            "choice_types_supported": len(ChoiceType),
            "therapeutic_approaches_supported": len(TherapeuticApproach),
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get therapeutic consequence system metrics."""
        return {
            "therapeutic_frameworks_available": len(self.therapeutic_frameworks),
            "attribute_mappings_configured": len(self.attribute_mappings),
            "choice_types_supported": len(ChoiceType),
            "therapeutic_approaches_supported": len(TherapeuticApproach),
        }
