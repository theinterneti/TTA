"""
Agency Protector for Therapeutic Text Adventure

This module implements agency protection functionality that ensures player
choices maintain meaningful agency, avoid manipulation, and support
therapeutic empowerment while preventing choice overload or paralysis.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from ..models.core import (
    Choice,
    ChoiceType,
    DifficultyLevel,
    EmotionalState,
    Scene,
    SessionState,
)
from ..models.interactions import AgencyAssessment

logger = logging.getLogger(__name__)


class AgencyProtector:
    """
    Protects and enhances player agency by ensuring choices are meaningful,
    non-manipulative, and appropriately empowering for therapeutic goals.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Agency protection criteria
        self.agency_criteria: dict[str, Any] = {}
        self.empowerment_guidelines: dict[str, Any] = {}
        self.choice_balance_rules: dict[str, Any] = {}
        self.manipulation_detection_rules: dict[str, Any] = {}

        # Agency thresholds
        self.minimum_agency_level = self.config.get("minimum_agency_level", 0.5)
        self.maximum_choices = self.config.get("maximum_choices", 4)
        self.minimum_choices = self.config.get("minimum_choices", 2)

        logger.info("AgencyProtector initialized")

    async def initialize(self) -> bool:
        """Initialize agency protection rules and criteria."""
        try:
            await self._load_agency_criteria()
            await self._load_empowerment_guidelines()
            await self._load_choice_balance_rules()
            await self._load_manipulation_detection_rules()

            logger.info("AgencyProtector initialization completed")
            return True

        except Exception as e:
            logger.error(f"AgencyProtector initialization failed: {e}")
            return False

    async def ensure_meaningful_agency(
        self, choices: list[Choice], scene: Scene, session_state: SessionState
    ) -> list[Choice]:
        """
        Ensure choices provide meaningful agency and therapeutic empowerment.

        Args:
            choices: List of choices to evaluate and enhance
            scene: The scene context
            session_state: Current session state

        Returns:
            List of choices with enhanced agency protection
        """
        try:
            logger.info(f"Ensuring meaningful agency for {len(choices)} choices")

            # Assess current agency level
            agency_assessment = await self._assess_choice_agency(
                choices, scene, session_state
            )

            # Filter out manipulative or low-agency choices
            filtered_choices = await self._filter_manipulative_choices(
                choices, session_state
            )

            # Enhance agency levels where needed
            enhanced_choices = await self._enhance_agency_levels(
                filtered_choices, scene, session_state
            )

            # Balance choice difficulty and complexity
            balanced_choices = await self._balance_choice_complexity(
                enhanced_choices, session_state
            )

            # Ensure appropriate choice count
            final_choices = await self._ensure_appropriate_choice_count(
                balanced_choices, scene, session_state
            )

            # Final agency validation
            validated_choices = await self._validate_final_agency(
                final_choices, session_state
            )

            logger.info(
                f"Agency protection completed: {len(validated_choices)} choices"
            )
            return validated_choices

        except Exception as e:
            logger.error(f"Failed to ensure meaningful agency: {e}")
            return choices  # Return original choices if protection fails

    async def assess_choice_empowerment(
        self, choice: Choice, session_state: SessionState
    ) -> AgencyAssessment:
        """
        Assess the empowerment level of a specific choice.

        Args:
            choice: The choice to assess
            session_state: Current session state

        Returns:
            AgencyAssessment with empowerment analysis
        """
        try:
            # Calculate empowerment score
            empowerment_score = await self._calculate_empowerment_score(
                choice, session_state
            )

            # Identify empowerment factors
            empowerment_factors = await self._identify_empowerment_factors(choice)

            # Identify potential concerns
            agency_concerns = await self._identify_agency_concerns(
                choice, session_state
            )

            # Determine overall agency level
            agency_level = (
                "HIGH"
                if empowerment_score > 0.8
                else "MODERATE" if empowerment_score > 0.5 else "LOW"
            )

            return AgencyAssessment(
                choice_id=choice.choice_id,
                agency_level=agency_level,
                empowerment_score=empowerment_score,
                empowerment_factors=empowerment_factors,
                agency_concerns=agency_concerns,
                recommendations=await self._generate_agency_recommendations(
                    choice, empowerment_score
                ),
            )

        except Exception as e:
            logger.error(f"Failed to assess choice empowerment: {e}")
            return AgencyAssessment(
                choice_id=choice.choice_id,
                agency_level="MODERATE",
                empowerment_score=0.5,
                empowerment_factors=[],
                agency_concerns=[],
                recommendations=[],
            )

    # Initialization Methods
    async def _load_agency_criteria(self) -> None:
        """Load agency protection criteria."""
        self.agency_criteria = {
            "minimum_agency_level": 0.5,
            "meaningful_choice_indicators": [
                "clear_consequences",
                "personal_relevance",
                "skill_application",
                "emotional_resonance",
                "growth_opportunity",
            ],
            "agency_enhancing_elements": [
                "player_control",
                "meaningful_impact",
                "personal_choice",
                "skill_expression",
                "value_alignment",
            ],
            "agency_reducing_elements": [
                "forced_outcome",
                "manipulation",
                "false_choice",
                "overwhelming_complexity",
                "unclear_consequences",
            ],
        }

    async def _load_empowerment_guidelines(self) -> None:
        """Load empowerment guidelines."""
        self.empowerment_guidelines = {
            "empowerment_principles": [
                "respect_autonomy",
                "build_self_efficacy",
                "support_growth",
                "honor_values",
                "encourage_exploration",
            ],
            "therapeutic_empowerment": {
                "skill_building": "Enable practice and mastery",
                "emotional_regulation": "Support emotional autonomy",
                "mindfulness": "Encourage present-moment choice",
                "self_compassion": "Foster self-acceptance",
            },
            "empowerment_by_emotional_state": {
                EmotionalState.CRISIS: "Provide safety and immediate support",
                EmotionalState.DISTRESSED: "Offer gentle, supportive options",
                EmotionalState.OVERWHELMED: "Simplify and support",
                EmotionalState.ANXIOUS: "Provide grounding and control",
                EmotionalState.CALM: "Enable full exploration",
                EmotionalState.ENGAGED: "Support active participation",
            },
        }

    async def _load_choice_balance_rules(self) -> None:
        """Load choice balance rules."""
        self.choice_balance_rules = {
            "optimal_choice_count": {
                EmotionalState.CRISIS: 2,
                EmotionalState.DISTRESSED: 2,
                EmotionalState.OVERWHELMED: 2,
                EmotionalState.ANXIOUS: 3,
                EmotionalState.CALM: 4,
                EmotionalState.ENGAGED: 4,
            },
            "difficulty_distribution": {
                "gentle_ratio": 0.5,  # At least 50% gentle choices for vulnerable states
                "challenging_ratio": 0.25,  # At most 25% challenging choices
                "standard_ratio": 0.25,  # Remaining standard choices
            },
            "choice_type_balance": {
                "therapeutic_minimum": 0.5,  # At least 50% therapeutic choices
                "narrative_maximum": 0.5,  # At most 50% narrative choices
                "variety_requirement": True,  # Require variety in choice types
            },
        }

    async def _load_manipulation_detection_rules(self) -> None:
        """Load manipulation detection rules."""
        self.manipulation_detection_rules = {
            "manipulation_indicators": [
                "false_urgency",
                "guilt_induction",
                "fear_based_pressure",
                "single_correct_answer",
                "hidden_agenda",
                "emotional_manipulation",
            ],
            "therapeutic_manipulation_risks": [
                "forced_vulnerability",
                "premature_disclosure",
                "overwhelming_challenge",
                "invalidating_choice",
                "bypassing_readiness",
            ],
            "protective_measures": [
                "clear_consequences",
                "genuine_alternatives",
                "respect_boundaries",
                "honor_readiness",
                "transparent_intentions",
            ],
        }

    # Core Protection Methods
    async def _assess_choice_agency(
        self, choices: list[Choice], scene: Scene, session_state: SessionState
    ) -> dict[str, Any]:
        """Assess the overall agency level of a choice set."""
        total_agency = sum(choice.agency_level for choice in choices)
        average_agency = total_agency / len(choices) if choices else 0

        # Assess choice variety
        choice_types = set(choice.choice_type for choice in choices)
        type_variety = len(choice_types) / len(ChoiceType)

        # Assess difficulty balance
        difficulty_levels = [choice.difficulty_level for choice in choices]
        difficulty_balance = await self._assess_difficulty_balance(
            difficulty_levels, session_state
        )

        return {
            "average_agency_level": average_agency,
            "choice_count": len(choices),
            "type_variety": type_variety,
            "difficulty_balance": difficulty_balance,
            "meets_minimum_agency": average_agency >= self.minimum_agency_level,
        }

    async def _filter_manipulative_choices(
        self, choices: list[Choice], session_state: SessionState
    ) -> list[Choice]:
        """Filter out choices that may be manipulative or reduce agency."""
        filtered_choices = []

        for choice in choices:
            is_manipulative = await self._detect_manipulation(choice, session_state)
            if not is_manipulative:
                filtered_choices.append(choice)
            else:
                logger.warning(f"Filtered manipulative choice: {choice.choice_id}")

        return filtered_choices

    async def _enhance_agency_levels(
        self, choices: list[Choice], scene: Scene, session_state: SessionState
    ) -> list[Choice]:
        """Enhance agency levels of choices where needed."""
        enhanced_choices = []

        for choice in choices:
            if choice.agency_level < self.minimum_agency_level:
                enhanced_choice = await self._enhance_single_choice_agency(
                    choice, scene, session_state
                )
                enhanced_choices.append(enhanced_choice)
            else:
                enhanced_choices.append(choice)

        return enhanced_choices

    async def _balance_choice_complexity(
        self, choices: list[Choice], session_state: SessionState
    ) -> list[Choice]:
        """Balance choice complexity based on emotional state."""
        emotional_state = session_state.emotional_state
        optimal_count = self.choice_balance_rules["optimal_choice_count"].get(
            emotional_state, 3
        )

        # If we have too many choices, prioritize by agency and therapeutic value
        if len(choices) > optimal_count:
            # Score choices for prioritization
            scored_choices = []
            for choice in choices:
                score = (
                    (choice.agency_level * 0.5)
                    + (choice.therapeutic_value * 0.3)
                    + (choice.meaningfulness_score * 0.2)
                )
                scored_choices.append((choice, score))

            # Sort by score and take top choices
            scored_choices.sort(key=lambda x: x[1], reverse=True)
            choices = [choice for choice, score in scored_choices[:optimal_count]]

        # Ensure difficulty balance
        balanced_choices = await self._ensure_difficulty_balance(choices, session_state)

        return balanced_choices

    async def _ensure_appropriate_choice_count(
        self, choices: list[Choice], scene: Scene, session_state: SessionState
    ) -> list[Choice]:
        """Ensure appropriate number of choices."""
        emotional_state = session_state.emotional_state
        optimal_count = self.choice_balance_rules["optimal_choice_count"].get(
            emotional_state, 3
        )

        if len(choices) < self.minimum_choices:
            # Generate additional safe choices
            while len(choices) < self.minimum_choices:
                safe_choice = await self._generate_safe_agency_choice(
                    scene, session_state
                )
                if safe_choice:
                    choices.append(safe_choice)
                else:
                    break

        elif len(choices) > optimal_count:
            # Reduce to optimal count while maintaining balance
            choices = await self._reduce_to_optimal_count(
                choices, optimal_count, session_state
            )

        return choices

    async def _validate_final_agency(
        self, choices: list[Choice], session_state: SessionState
    ) -> list[Choice]:
        """Final validation of agency protection."""
        validated_choices = []

        for choice in choices:
            # Final agency check
            if choice.agency_level >= self.minimum_agency_level:
                validated_choices.append(choice)
            else:
                logger.warning(
                    f"Choice failed final agency validation: {choice.choice_id}"
                )

        # Ensure we still have minimum choices after validation
        if len(validated_choices) < self.minimum_choices and len(choices) > 0:
            # Add back highest agency choices that were filtered
            remaining_choices = [c for c in choices if c not in validated_choices]
            remaining_choices.sort(key=lambda x: x.agency_level, reverse=True)

            while len(validated_choices) < self.minimum_choices and remaining_choices:
                validated_choices.append(remaining_choices.pop(0))

        return validated_choices

    # Helper Methods
    async def _assess_difficulty_balance(
        self, difficulty_levels: list[DifficultyLevel], session_state: SessionState
    ) -> dict[str, Any]:
        """Assess the balance of difficulty levels."""
        if not difficulty_levels:
            return {"balanced": False, "reason": "no_choices"}

        # Count difficulty levels
        gentle_count = sum(1 for d in difficulty_levels if d == DifficultyLevel.GENTLE)
        standard_count = sum(
            1 for d in difficulty_levels if d == DifficultyLevel.STANDARD
        )
        challenging_count = sum(
            1 for d in difficulty_levels if d == DifficultyLevel.CHALLENGING
        )
        intensive_count = sum(
            1 for d in difficulty_levels if d == DifficultyLevel.INTENSIVE
        )

        total_count = len(difficulty_levels)

        # Calculate ratios
        gentle_ratio = gentle_count / total_count
        challenging_ratio = (challenging_count + intensive_count) / total_count

        # Check balance based on emotional state
        emotional_state = session_state.emotional_state

        if emotional_state in [
            EmotionalState.CRISIS,
            EmotionalState.DISTRESSED,
            EmotionalState.OVERWHELMED,
        ]:
            # Should be mostly gentle choices
            balanced = gentle_ratio >= 0.8 and challenging_ratio <= 0.2
        elif emotional_state == EmotionalState.ANXIOUS:
            # Should be mostly gentle with some standard
            balanced = gentle_ratio >= 0.6 and challenging_ratio <= 0.2
        else:
            # Can have more variety
            balanced = gentle_ratio >= 0.3 and challenging_ratio <= 0.4

        return {
            "balanced": balanced,
            "gentle_ratio": gentle_ratio,
            "challenging_ratio": challenging_ratio,
            "total_count": total_count,
        }

    async def _detect_manipulation(
        self, choice: Choice, session_state: SessionState
    ) -> bool:
        """Detect if a choice may be manipulative."""
        manipulation_indicators = self.manipulation_detection_rules[
            "manipulation_indicators"
        ]
        therapeutic_risks = self.manipulation_detection_rules[
            "therapeutic_manipulation_risks"
        ]

        # Check for manipulation indicators in choice text or tags
        choice_content = f"{choice.choice_text} {choice.description}".lower()

        for indicator in manipulation_indicators:
            if indicator.replace("_", " ") in choice_content:
                return True

        # Check for therapeutic manipulation risks
        for risk in therapeutic_risks:
            if risk.replace("_", " ") in choice_content:
                return True

        # Check for false choices (only one real option)
        if choice.agency_level < 0.2:
            return True

        # Check for inappropriate pressure based on emotional state
        if session_state.emotional_state in [
            EmotionalState.CRISIS,
            EmotionalState.DISTRESSED,
        ]:
            if choice.difficulty_level in [
                DifficultyLevel.CHALLENGING,
                DifficultyLevel.INTENSIVE,
            ]:
                return True

        return False

    async def _enhance_single_choice_agency(
        self, choice: Choice, scene: Scene, session_state: SessionState
    ) -> Choice:
        """Enhance the agency level of a single choice."""
        enhanced_choice = Choice(**choice.model_dump())
        enhanced_choice.choice_id = str(uuid4())  # New ID for enhanced choice

        # Enhance choice text to be more empowering
        if "you must" in enhanced_choice.choice_text.lower():
            enhanced_choice.choice_text = enhanced_choice.choice_text.replace(
                "you must", "you can choose to"
            )
        elif "you should" in enhanced_choice.choice_text.lower():
            enhanced_choice.choice_text = enhanced_choice.choice_text.replace(
                "you should", "you might"
            )

        # Add agency-enhancing language
        if not any(
            word in enhanced_choice.choice_text.lower()
            for word in ["choose", "decide", "explore", "try"]
        ):
            enhanced_choice.choice_text = (
                f"Choose to {enhanced_choice.choice_text.lower()}"
            )

        # Enhance description to emphasize player control
        enhanced_choice.description = f"Your choice: {enhanced_choice.description}"

        # Increase agency level
        enhanced_choice.agency_level = min(enhanced_choice.agency_level + 0.2, 1.0)

        # Add agency-enhancing therapeutic tags
        if "player_control" not in enhanced_choice.therapeutic_tags:
            enhanced_choice.therapeutic_tags.append("player_control")

        return enhanced_choice

    async def _ensure_difficulty_balance(
        self, choices: list[Choice], session_state: SessionState
    ) -> list[Choice]:
        """Ensure appropriate difficulty balance."""
        emotional_state = session_state.emotional_state

        # For vulnerable states, ensure mostly gentle choices
        if emotional_state in [
            EmotionalState.CRISIS,
            EmotionalState.DISTRESSED,
            EmotionalState.OVERWHELMED,
        ]:
            balanced_choices = []
            for choice in choices:
                if choice.difficulty_level in [
                    DifficultyLevel.CHALLENGING,
                    DifficultyLevel.INTENSIVE,
                ]:
                    # Convert to gentler version
                    gentler_choice = Choice(**choice.model_dump())
                    gentler_choice.choice_id = str(uuid4())
                    gentler_choice.difficulty_level = DifficultyLevel.GENTLE
                    gentler_choice.choice_text = f"Gently {choice.choice_text.lower()}"
                    balanced_choices.append(gentler_choice)
                else:
                    balanced_choices.append(choice)
            return balanced_choices

        return choices

    async def _generate_safe_agency_choice(
        self, scene: Scene, session_state: SessionState
    ) -> Choice | None:
        """Generate a safe choice with good agency."""
        emotional_state = session_state.emotional_state

        safe_choices = {
            EmotionalState.CRISIS: {
                "text": "Focus on what feels safest right now",
                "description": "Your choice: prioritize your immediate safety and wellbeing",
                "tags": ["immediate_safety", "crisis_support", "player_control"],
            },
            EmotionalState.DISTRESSED: {
                "text": "Take a moment to care for yourself",
                "description": "Your choice: offer yourself the support you need",
                "tags": ["self_care", "support", "compassion", "player_control"],
            },
            EmotionalState.OVERWHELMED: {
                "text": "Choose what feels most manageable",
                "description": "Your choice: take things at your own pace",
                "tags": ["manageable_steps", "self_pacing", "player_control"],
            },
            EmotionalState.ANXIOUS: {
                "text": "Ground yourself in this moment",
                "description": "Your choice: use grounding techniques that work for you",
                "tags": ["grounding", "present_moment", "player_control"],
            },
            EmotionalState.CALM: {
                "text": "Explore what interests you most",
                "description": "Your choice: follow your curiosity and interests",
                "tags": ["exploration", "curiosity", "player_control"],
            },
            EmotionalState.ENGAGED: {
                "text": "Actively engage with what draws you",
                "description": "Your choice: dive deeper into what engages you",
                "tags": ["active_engagement", "exploration", "player_control"],
            },
        }

        choice_data = safe_choices.get(
            emotional_state, safe_choices[EmotionalState.CALM]
        )

        return Choice(
            choice_text=choice_data["text"],
            description=choice_data["description"],
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_tags=choice_data["tags"],
            difficulty_level=DifficultyLevel.GENTLE,
            agency_level=0.8,
            meaningfulness_score=0.7,
            emotional_context=[emotional_state.value],
            therapeutic_value=0.7,
        )

    async def _reduce_to_optimal_count(
        self, choices: list[Choice], optimal_count: int, session_state: SessionState
    ) -> list[Choice]:
        """Reduce choices to optimal count while maintaining balance."""
        if len(choices) <= optimal_count:
            return choices

        # Score choices for retention
        scored_choices = []
        for choice in choices:
            score = await self._calculate_retention_score(choice, session_state)
            scored_choices.append((choice, score))

        # Sort by score and take top choices
        scored_choices.sort(key=lambda x: x[1], reverse=True)
        return [choice for choice, score in scored_choices[:optimal_count]]

    async def _calculate_retention_score(
        self, choice: Choice, session_state: SessionState
    ) -> float:
        """Calculate score for choice retention."""
        score = 0.0

        # Agency level (40% weight)
        score += choice.agency_level * 0.4

        # Therapeutic value (30% weight)
        score += choice.therapeutic_value * 0.3

        # Meaningfulness (20% weight)
        score += choice.meaningfulness_score * 0.2

        # Emotional appropriateness (10% weight)
        if session_state.emotional_state.value in choice.emotional_context:
            score += 0.1

        return score

    # Assessment Methods
    async def _calculate_empowerment_score(
        self, choice: Choice, session_state: SessionState
    ) -> float:
        """Calculate empowerment score for a choice."""
        empowerment_score = 0.0

        # Base agency level (50% weight)
        empowerment_score += choice.agency_level * 0.5

        # Therapeutic empowerment (25% weight)
        therapeutic_empowerment = await self._assess_therapeutic_empowerment(choice)
        empowerment_score += therapeutic_empowerment * 0.25

        # Personal relevance (15% weight)
        personal_relevance = await self._assess_personal_relevance(
            choice, session_state
        )
        empowerment_score += personal_relevance * 0.15

        # Growth opportunity (10% weight)
        growth_opportunity = await self._assess_growth_opportunity(choice)
        empowerment_score += growth_opportunity * 0.1

        return min(empowerment_score, 1.0)

    async def _identify_empowerment_factors(self, choice: Choice) -> list[str]:
        """Identify factors that contribute to empowerment."""
        empowerment_factors = []

        # Check for agency-enhancing elements
        agency_enhancing = self.agency_criteria["agency_enhancing_elements"]
        for element in agency_enhancing:
            if element.replace("_", " ") in choice.description.lower():
                empowerment_factors.append(element)

        # Check therapeutic tags for empowerment
        empowering_tags = [
            "player_control",
            "self_efficacy",
            "autonomy",
            "choice",
            "empowerment",
        ]
        for tag in choice.therapeutic_tags:
            if tag in empowering_tags:
                empowerment_factors.append(f"therapeutic_{tag}")

        # High agency level
        if choice.agency_level > 0.8:
            empowerment_factors.append("high_agency")

        # Meaningful choice
        if choice.meaningfulness_score > 0.7:
            empowerment_factors.append("meaningful_impact")

        return empowerment_factors

    async def _identify_agency_concerns(
        self, choice: Choice, session_state: SessionState
    ) -> list[str]:
        """Identify potential agency concerns."""
        concerns = []

        # Low agency level
        if choice.agency_level < self.minimum_agency_level:
            concerns.append("low_agency_level")

        # Check for agency-reducing elements
        agency_reducing = self.agency_criteria["agency_reducing_elements"]
        choice_content = f"{choice.choice_text} {choice.description}".lower()

        for element in agency_reducing:
            if element.replace("_", " ") in choice_content:
                concerns.append(element)

        # Inappropriate difficulty for emotional state
        if session_state.emotional_state in [
            EmotionalState.CRISIS,
            EmotionalState.DISTRESSED,
        ]:
            if choice.difficulty_level in [
                DifficultyLevel.CHALLENGING,
                DifficultyLevel.INTENSIVE,
            ]:
                concerns.append("inappropriate_difficulty_for_emotional_state")

        # Low meaningfulness
        if choice.meaningfulness_score < 0.4:
            concerns.append("low_meaningfulness")

        return concerns

    async def _generate_agency_recommendations(
        self, choice: Choice, empowerment_score: float
    ) -> list[str]:
        """Generate recommendations for improving agency."""
        recommendations = []

        if empowerment_score < 0.5:
            recommendations.append(
                "Enhance choice language to emphasize player control"
            )
            recommendations.append("Clarify meaningful consequences of the choice")

        if choice.agency_level < 0.6:
            recommendations.append("Increase player autonomy in choice execution")
            recommendations.append("Add elements that allow personal expression")

        if choice.meaningfulness_score < 0.5:
            recommendations.append("Connect choice to therapeutic goals more clearly")
            recommendations.append("Emphasize personal relevance and impact")

        if not any(
            tag in choice.therapeutic_tags
            for tag in ["player_control", "autonomy", "choice"]
        ):
            recommendations.append("Add therapeutic tags that emphasize agency")

        return recommendations

    # Assessment Helper Methods
    async def _assess_therapeutic_empowerment(self, choice: Choice) -> float:
        """Assess therapeutic empowerment level of choice."""
        empowerment_score = 0.5  # Base score

        # Check for empowering therapeutic approaches
        empowering_approaches = self.empowerment_guidelines["therapeutic_empowerment"]

        for approach, _ in empowering_approaches.items():
            if approach.replace("_", " ") in choice.description.lower():
                empowerment_score += 0.1

        # Check for empowerment principles
        empowerment_principles = self.empowerment_guidelines["empowerment_principles"]
        for principle in empowerment_principles:
            if principle.replace("_", " ") in choice.description.lower():
                empowerment_score += 0.05

        return min(empowerment_score, 1.0)

    async def _assess_personal_relevance(
        self, choice: Choice, session_state: SessionState
    ) -> float:
        """Assess personal relevance of choice."""
        relevance_score = 0.5  # Base score

        # Emotional state alignment
        if session_state.emotional_state.value in choice.emotional_context:
            relevance_score += 0.3

        # Therapeutic focus alignment (if available in session state)
        if hasattr(session_state, "therapeutic_focus"):
            focus_alignment = len(
                set(choice.therapeutic_tags) & set(session_state.therapeutic_focus)
            )
            relevance_score += focus_alignment * 0.1

        return min(relevance_score, 1.0)

    async def _assess_growth_opportunity(self, choice: Choice) -> float:
        """Assess growth opportunity provided by choice."""
        growth_score = 0.5  # Base score

        # Skill building choices offer growth
        if choice.choice_type == ChoiceType.SKILL_BUILDING:
            growth_score += 0.3

        # Therapeutic choices offer growth
        elif choice.choice_type == ChoiceType.THERAPEUTIC:
            growth_score += 0.2

        # High therapeutic value indicates growth opportunity
        growth_score += choice.therapeutic_value * 0.2

        # Growth-related therapeutic tags
        growth_tags = ["growth", "development", "learning", "skill", "mastery"]
        for tag in choice.therapeutic_tags:
            if any(growth_tag in tag for growth_tag in growth_tags):
                growth_score += 0.05

        return min(growth_score, 1.0)
