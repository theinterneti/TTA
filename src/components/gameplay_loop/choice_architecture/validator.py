"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Choice_architecture/Validator]]

# Logseq: [[TTA/Components/Gameplay_loop/Choice_architecture/Validator]]
Choice Validator for Therapeutic Text Adventure

This module implements choice validation functionality that ensures choices
are therapeutically appropriate, safe, and aligned with therapeutic goals
while maintaining narrative coherence and player agency.
"""

from __future__ import annotations

import logging
from typing import Any

from ..models.core import Choice, ChoiceType, EmotionalState, Scene, SessionState
from ..models.interactions import UserChoice
from ..models.validation import SafetyCheck, TherapeuticValidation, ValidationResult

logger = logging.getLogger(__name__)


class ChoiceValidator:
    """
    Validates choices for therapeutic appropriateness, safety, and alignment
    with therapeutic goals while ensuring narrative coherence.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Validation criteria and thresholds
        self.safety_criteria: dict[str, Any] = {}
        self.therapeutic_criteria: dict[str, Any] = {}
        self.emotional_appropriateness_rules: dict[EmotionalState, dict[str, Any]] = {}
        self.minimum_thresholds: dict[str, float] = {}

        logger.info("ChoiceValidator initialized")

    async def initialize(self) -> bool:
        """Initialize validation criteria and rules."""
        try:
            await self._load_safety_criteria()
            await self._load_therapeutic_criteria()
            await self._load_emotional_appropriateness_rules()
            await self._load_minimum_thresholds()

            logger.info("ChoiceValidator initialization completed")
            return True

        except Exception as e:
            logger.error(f"ChoiceValidator initialization failed: {e}")
            return False

    async def validate_choices(
        self, choices: list[Choice], scene: Scene, session_state: SessionState
    ) -> list[Choice]:
        """
        Validate a list of choices for therapeutic appropriateness and safety.

        Args:
            choices: List of choices to validate
            scene: The scene context
            session_state: Current session state

        Returns:
            List of validated choices that meet all criteria
        """
        try:
            logger.info(f"Validating {len(choices)} choices")

            validated_choices = []

            for choice in choices:
                validation_result = await self._validate_single_choice(
                    choice, scene, session_state
                )

                if validation_result.is_valid:
                    validated_choices.append(choice)
                else:
                    logger.warning(
                        f"Choice failed validation: {validation_result.issues}"
                    )

            logger.info(
                f"Validated {len(validated_choices)} out of {len(choices)} choices"
            )
            return validated_choices

        except Exception as e:
            logger.error(f"Failed to validate choices: {e}")
            return choices  # Return original choices if validation fails

    async def validate_for_emotional_state(
        self, choice: Choice, emotional_state: str, session_state: SessionState
    ) -> bool:
        """
        Validate if a choice is appropriate for a specific emotional state.

        Args:
            choice: The choice to validate
            emotional_state: The emotional state to validate against
            session_state: Current session state

        Returns:
            True if choice is appropriate for the emotional state
        """
        try:
            emotional_state_enum = EmotionalState(emotional_state)
            rules = self.emotional_appropriateness_rules.get(emotional_state_enum, {})

            # Check if choice type is appropriate
            appropriate_types = rules.get("appropriate_choice_types", [])
            if appropriate_types and choice.choice_type not in appropriate_types:
                return False

            # Check if therapeutic tags are appropriate
            required_tags = rules.get("required_therapeutic_tags", [])
            if required_tags and not any(
                tag in choice.therapeutic_tags for tag in required_tags
            ):
                return False

            # Check if choice difficulty is appropriate
            max_difficulty = rules.get("max_difficulty_level")
            if max_difficulty and choice.difficulty_level.value > max_difficulty:
                return False

            # Check therapeutic value threshold
            min_therapeutic_value = rules.get("min_therapeutic_value", 0.0)
            return not choice.therapeutic_value < min_therapeutic_value

        except Exception as e:
            logger.error(f"Failed to validate choice for emotional state: {e}")
            return True  # Default to allowing choice if validation fails

    async def analyze_therapeutic_impact(
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> dict[str, Any]:
        """
        Analyze the therapeutic impact of a user's choice.

        Args:
            user_choice: The choice made by the user
            scene: The scene where the choice was made
            session_state: Current session state

        Returns:
            Dictionary with therapeutic impact analysis
        """
        try:
            logger.info(
                f"Analyzing therapeutic impact of choice {user_choice.choice_id}"
            )

            impact_analysis = {
                "therapeutic_impact_score": user_choice.therapeutic_value,
                "skill_development": [],
                "learning_opportunities": [],
                "progress_markers": [],
                "emotional_growth": [],
                "therapeutic_alignment": 0.0,
            }

            # Analyze skill development
            if user_choice.choice_type == ChoiceType.SKILL_BUILDING:
                impact_analysis[
                    "skill_development"
                ] = await self._analyze_skill_development(user_choice, session_state)

            # Analyze learning opportunities
            impact_analysis[
                "learning_opportunities"
            ] = await self._identify_learning_opportunities(
                user_choice, scene, session_state
            )

            # Analyze progress markers
            impact_analysis["progress_markers"] = await self._identify_progress_markers(
                user_choice, session_state
            )

            # Analyze emotional growth
            impact_analysis["emotional_growth"] = await self._analyze_emotional_growth(
                user_choice, session_state
            )

            # Calculate therapeutic alignment
            impact_analysis[
                "therapeutic_alignment"
            ] = await self._calculate_therapeutic_alignment(
                user_choice, scene, session_state
            )

            return impact_analysis

        except Exception as e:
            logger.error(f"Failed to analyze therapeutic impact: {e}")
            return {"therapeutic_impact_score": 0.5}

    # Initialization Methods
    async def _load_safety_criteria(self) -> None:
        """Load safety criteria for choice validation."""
        self.safety_criteria = {
            "prohibited_content": [
                "self_harm",
                "violence",
                "substance_abuse",
                "dangerous_behavior",
            ],
            "required_safety_elements": [
                "agency_preservation",
                "consent_respect",
                "boundary_awareness",
            ],
            "crisis_state_requirements": {
                "max_complexity": "minimal",
                "required_tags": ["safety", "support", "grounding"],
                "prohibited_tags": ["challenge", "confrontation", "intensity"],
            },
            "distressed_state_requirements": {
                "max_complexity": "gentle",
                "required_tags": ["support", "compassion"],
                "prohibited_tags": ["pressure", "intensity"],
            },
        }

    async def _load_therapeutic_criteria(self) -> None:
        """Load therapeutic criteria for choice validation."""
        self.therapeutic_criteria = {
            "minimum_therapeutic_value": 0.3,
            "required_therapeutic_alignment": 0.5,
            "therapeutic_tag_requirements": {
                ChoiceType.THERAPEUTIC: [
                    "mindfulness",
                    "grounding",
                    "self_compassion",
                    "emotional_regulation",
                ],
                ChoiceType.SKILL_BUILDING: [
                    "coping_skills",
                    "resilience",
                    "problem_solving",
                ],
                ChoiceType.EMOTIONAL_REGULATION: [
                    "emotional_balance",
                    "regulation",
                    "awareness",
                ],
            },
            "scene_type_alignment": {
                "therapeutic": [
                    "therapeutic",
                    "skill_building",
                    "emotional_regulation",
                ],
                "exploration": ["narrative", "social_interaction"],
                "challenge": ["skill_building", "narrative"],
            },
        }

    async def _load_emotional_appropriateness_rules(self) -> None:
        """Load rules for emotional state appropriateness."""
        self.emotional_appropriateness_rules = {
            EmotionalState.CALM: {
                "appropriate_choice_types": list(ChoiceType),
                "min_therapeutic_value": 0.3,
                "max_difficulty_level": 4,  # All difficulty levels appropriate
            },
            EmotionalState.ENGAGED: {
                "appropriate_choice_types": list(ChoiceType),
                "min_therapeutic_value": 0.4,
                "max_difficulty_level": 4,
                "preferred_tags": ["exploration", "growth", "challenge"],
            },
            EmotionalState.ANXIOUS: {
                "appropriate_choice_types": [
                    ChoiceType.THERAPEUTIC,
                    ChoiceType.NARRATIVE,
                ],
                "required_therapeutic_tags": ["grounding", "calming", "safety"],
                "min_therapeutic_value": 0.6,
                "max_difficulty_level": 2,  # Gentle to Standard only
            },
            EmotionalState.OVERWHELMED: {
                "appropriate_choice_types": [ChoiceType.THERAPEUTIC],
                "required_therapeutic_tags": ["grounding", "safety", "support"],
                "min_therapeutic_value": 0.8,
                "max_difficulty_level": 1,  # Gentle only
            },
            EmotionalState.DISTRESSED: {
                "appropriate_choice_types": [ChoiceType.THERAPEUTIC],
                "required_therapeutic_tags": ["safety", "support", "compassion"],
                "min_therapeutic_value": 0.9,
                "max_difficulty_level": 1,  # Gentle only
            },
            EmotionalState.CRISIS: {
                "appropriate_choice_types": [ChoiceType.THERAPEUTIC],
                "required_therapeutic_tags": ["immediate_safety", "crisis_support"],
                "min_therapeutic_value": 1.0,
                "max_difficulty_level": 1,  # Gentle only
            },
        }

    async def _load_minimum_thresholds(self) -> None:
        """Load minimum thresholds for validation."""
        self.minimum_thresholds = {
            "therapeutic_value": 0.3,
            "agency_level": 0.4,
            "meaningfulness_score": 0.3,
            "safety_score": 0.8,
        }

    # Core Validation Methods
    async def _validate_single_choice(
        self, choice: Choice, scene: Scene, session_state: SessionState
    ) -> ValidationResult:
        """Validate a single choice against all criteria."""
        issues = []
        warnings = []

        # Safety validation
        safety_result = await self._validate_safety(choice, session_state)
        if not safety_result.is_safe:
            issues.extend(safety_result.issues)

        # Therapeutic validation
        therapeutic_result = await self._validate_therapeutic_appropriateness(
            choice, scene, session_state
        )
        if not therapeutic_result.is_therapeutically_appropriate:
            issues.extend(therapeutic_result.issues)

        # Emotional appropriateness validation
        emotional_appropriate = await self.validate_for_emotional_state(
            choice, session_state.emotional_state.value, session_state
        )
        if not emotional_appropriate:
            issues.append(
                f"Choice not appropriate for emotional state: {session_state.emotional_state}"
            )

        # Threshold validation
        threshold_issues = await self._validate_thresholds(choice)
        issues.extend(threshold_issues)

        # Create validation result
        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            confidence_score=1.0 - (len(issues) * 0.2),
            issues=issues,
            warnings=warnings,
            validation_details={
                "safety_check": (
                    safety_result.model_dump()
                    if hasattr(safety_result, "model_dump")
                    else str(safety_result)
                ),
                "therapeutic_check": (
                    therapeutic_result.model_dump()
                    if hasattr(therapeutic_result, "model_dump")
                    else str(therapeutic_result)
                ),
                "emotional_appropriateness": emotional_appropriate,
                "threshold_validation": len(threshold_issues) == 0,
            },
        )

    async def _validate_safety(
        self, choice: Choice, session_state: SessionState
    ) -> SafetyCheck:
        """Validate choice safety."""
        safety_issues = []

        # Check for prohibited content
        prohibited_content = self.safety_criteria["prohibited_content"]
        for tag in choice.therapeutic_tags:
            if tag in prohibited_content:
                safety_issues.append(f"Contains prohibited content: {tag}")

        # Check crisis state requirements
        if session_state.emotional_state == EmotionalState.CRISIS:
            crisis_requirements = self.safety_criteria["crisis_state_requirements"]

            # Check required tags
            required_tags = crisis_requirements["required_tags"]
            if not any(tag in choice.therapeutic_tags for tag in required_tags):
                safety_issues.append("Missing required safety tags for crisis state")

            # Check prohibited tags
            prohibited_tags = crisis_requirements["prohibited_tags"]
            if any(tag in choice.therapeutic_tags for tag in prohibited_tags):
                safety_issues.append("Contains prohibited tags for crisis state")

        # Check distressed state requirements
        elif session_state.emotional_state == EmotionalState.DISTRESSED:
            distressed_requirements = self.safety_criteria[
                "distressed_state_requirements"
            ]

            required_tags = distressed_requirements["required_tags"]
            if not any(tag in choice.therapeutic_tags for tag in required_tags):
                safety_issues.append(
                    "Missing required support tags for distressed state"
                )

        is_safe = len(safety_issues) == 0
        safety_level = "SAFE" if is_safe else "CAUTION"

        if (
            session_state.emotional_state
            in [EmotionalState.CRISIS, EmotionalState.DISTRESSED]
            and not is_safe
        ):
            safety_level = "DANGER"

        return SafetyCheck(
            is_safe=is_safe,
            safety_level=safety_level,
            issues=safety_issues,
            risk_factors=[],
            protective_factors=choice.therapeutic_tags,
        )

    async def _validate_therapeutic_appropriateness(
        self, choice: Choice, scene: Scene, session_state: SessionState
    ) -> TherapeuticValidation:
        """Validate therapeutic appropriateness of choice."""
        therapeutic_issues = []

        # Check minimum therapeutic value
        min_therapeutic_value = self.therapeutic_criteria["minimum_therapeutic_value"]
        if choice.therapeutic_value < min_therapeutic_value:
            therapeutic_issues.append(
                f"Therapeutic value {choice.therapeutic_value} below minimum {min_therapeutic_value}"
            )

        # Check therapeutic tag requirements for choice type
        tag_requirements = self.therapeutic_criteria["therapeutic_tag_requirements"]
        required_tags = tag_requirements.get(choice.choice_type, [])

        if required_tags and not any(
            tag in choice.therapeutic_tags for tag in required_tags
        ):
            therapeutic_issues.append(
                f"Missing required therapeutic tags for {choice.choice_type}"
            )

        # Check scene type alignment
        scene_alignment = self.therapeutic_criteria["scene_type_alignment"]
        appropriate_types = scene_alignment.get(scene.scene_type.value, [])

        if appropriate_types and choice.choice_type.value not in appropriate_types:
            therapeutic_issues.append(
                f"Choice type {choice.choice_type} not aligned with scene type {scene.scene_type}"
            )

        # Calculate therapeutic alignment
        therapeutic_alignment = await self._calculate_therapeutic_alignment(
            choice, scene, session_state
        )
        required_alignment = self.therapeutic_criteria["required_therapeutic_alignment"]

        if therapeutic_alignment < required_alignment:
            therapeutic_issues.append(
                f"Therapeutic alignment {therapeutic_alignment} below required {required_alignment}"
            )

        is_valid = len(therapeutic_issues) == 0

        return TherapeuticValidation(
            is_therapeutically_appropriate=is_valid,
            therapeutic_alignment_score=therapeutic_alignment,
            issues=therapeutic_issues,
            recommendations=[],
            therapeutic_benefits=choice.therapeutic_tags,
        )

    async def _validate_thresholds(self, choice: Choice) -> list[str]:
        """Validate choice against minimum thresholds."""
        threshold_issues = []

        # Check therapeutic value threshold
        if choice.therapeutic_value < self.minimum_thresholds["therapeutic_value"]:
            threshold_issues.append(
                f"Therapeutic value below threshold: {choice.therapeutic_value}"
            )

        # Check agency level threshold
        if choice.agency_level < self.minimum_thresholds["agency_level"]:
            threshold_issues.append(
                f"Agency level below threshold: {choice.agency_level}"
            )

        # Check meaningfulness threshold
        if (
            choice.meaningfulness_score
            < self.minimum_thresholds["meaningfulness_score"]
        ):
            threshold_issues.append(
                f"Meaningfulness score below threshold: {choice.meaningfulness_score}"
            )

        return threshold_issues

    # Analysis Methods
    async def _analyze_skill_development(
        self, user_choice: UserChoice, session_state: SessionState
    ) -> list[str]:
        """Analyze skill development from a choice."""
        skills_developed = []

        if "coping_skills" in user_choice.therapeutic_tags:
            skills_developed.append("coping_strategies")
        if "resilience" in user_choice.therapeutic_tags:
            skills_developed.append("emotional_resilience")
        if "problem_solving" in user_choice.therapeutic_tags:
            skills_developed.append("problem_solving_abilities")
        if "mindfulness" in user_choice.therapeutic_tags:
            skills_developed.append("mindfulness_practice")
        if "emotional_regulation" in user_choice.therapeutic_tags:
            skills_developed.append("emotional_regulation_skills")

        return skills_developed

    async def _identify_learning_opportunities(
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> list[str]:
        """Identify learning opportunities from a choice."""
        learning_opportunities = []

        # Based on choice type
        if user_choice.choice_type == ChoiceType.THERAPEUTIC:
            learning_opportunities.append("therapeutic_insight")
        elif user_choice.choice_type == ChoiceType.SKILL_BUILDING:
            learning_opportunities.append("skill_application")
        elif user_choice.choice_type == ChoiceType.EMOTIONAL_REGULATION:
            learning_opportunities.append("emotional_awareness")

        # Based on therapeutic value
        if user_choice.therapeutic_value > 0.8:
            learning_opportunities.append("significant_growth")
        elif user_choice.therapeutic_value < 0.4:
            learning_opportunities.append("reflection_opportunity")

        # Based on scene context
        if "challenge" in scene.therapeutic_focus:
            learning_opportunities.append("challenge_navigation")
        if "relationship" in scene.therapeutic_focus:
            learning_opportunities.append("interpersonal_learning")

        return learning_opportunities

    async def _identify_progress_markers(
        self, user_choice: UserChoice, session_state: SessionState
    ) -> list[str]:
        """Identify progress markers from a choice."""
        progress_markers = []

        # High therapeutic value choices mark progress
        if user_choice.therapeutic_value > 0.7:
            progress_markers.append("therapeutic_progress")

        # Skill building choices mark skill development
        if user_choice.choice_type == ChoiceType.SKILL_BUILDING:
            progress_markers.append("skill_development_milestone")

        # Emotional regulation choices mark emotional growth
        if user_choice.choice_type == ChoiceType.EMOTIONAL_REGULATION:
            progress_markers.append("emotional_growth_milestone")

        # High agency choices mark empowerment
        if user_choice.agency_level > 0.8:
            progress_markers.append("empowerment_milestone")

        # Session progression markers
        choice_count = len(session_state.choice_history)
        if choice_count == 5:
            progress_markers.append("session_engagement_milestone")
        elif choice_count == 10:
            progress_markers.append("session_commitment_milestone")

        return progress_markers

    async def _analyze_emotional_growth(
        self, user_choice: UserChoice, session_state: SessionState
    ) -> list[str]:
        """Analyze emotional growth from a choice."""
        emotional_growth = []

        # Based on therapeutic tags
        if "self_compassion" in user_choice.therapeutic_tags:
            emotional_growth.append("self_compassion_development")
        if "emotional_regulation" in user_choice.therapeutic_tags:
            emotional_growth.append("emotional_regulation_growth")
        if "mindfulness" in user_choice.therapeutic_tags:
            emotional_growth.append("mindfulness_development")
        if "grounding" in user_choice.therapeutic_tags:
            emotional_growth.append("grounding_skills_growth")

        # Based on emotional state progression
        current_state = session_state.emotional_state
        if (
            current_state in [EmotionalState.ANXIOUS, EmotionalState.OVERWHELMED]
            and user_choice.therapeutic_value > 0.7
        ):
            emotional_growth.append("anxiety_management_progress")
        elif (
            current_state == EmotionalState.DISTRESSED
            and user_choice.therapeutic_value > 0.8
        ):
            emotional_growth.append("distress_tolerance_growth")
        elif (
            current_state == EmotionalState.ENGAGED
            and user_choice.therapeutic_value > 0.6
        ):
            emotional_growth.append("positive_engagement_reinforcement")

        return emotional_growth

    async def _calculate_therapeutic_alignment(
        self, choice: Choice, scene: Scene, session_state: SessionState
    ) -> float:
        """Calculate therapeutic alignment score for a choice."""
        alignment_score = 0.0

        # Base alignment from therapeutic value
        alignment_score += choice.therapeutic_value * 0.4

        # Alignment with scene therapeutic focus
        focus_alignment = len(
            set(choice.therapeutic_tags) & set(scene.therapeutic_focus)
        )
        max_possible_alignment = len(scene.therapeutic_focus)
        if max_possible_alignment > 0:
            alignment_score += (focus_alignment / max_possible_alignment) * 0.3

        # Alignment with emotional state needs
        emotional_alignment = await self._calculate_emotional_alignment(
            choice, session_state
        )
        alignment_score += emotional_alignment * 0.2

        # Choice type appropriateness
        type_appropriateness = await self._calculate_type_appropriateness(choice, scene)
        alignment_score += type_appropriateness * 0.1

        return min(alignment_score, 1.0)

    async def _calculate_emotional_alignment(
        self, choice: Choice, session_state: SessionState
    ) -> float:
        """Calculate alignment with emotional state needs."""
        emotional_state = session_state.emotional_state

        # High alignment for crisis/distressed states with safety choices
        if emotional_state in [EmotionalState.CRISIS, EmotionalState.DISTRESSED]:
            if any(
                tag in choice.therapeutic_tags
                for tag in ["safety", "support", "grounding"]
            ):
                return 1.0
            return 0.2

        # High alignment for anxious/overwhelmed states with calming choices
        if emotional_state in [EmotionalState.ANXIOUS, EmotionalState.OVERWHELMED]:
            if any(
                tag in choice.therapeutic_tags
                for tag in ["grounding", "calming", "mindfulness"]
            ):
                return 0.9
            return 0.4

        # Moderate alignment for engaged state with growth choices
        if emotional_state == EmotionalState.ENGAGED:
            if any(
                tag in choice.therapeutic_tags
                for tag in ["exploration", "growth", "challenge"]
            ):
                return 0.8
            return 0.6

        # Balanced alignment for calm state
        # CALM
        return 0.7

    async def _calculate_type_appropriateness(
        self, choice: Choice, scene: Scene
    ) -> float:
        """Calculate choice type appropriateness for scene."""
        scene_type_preferences = {
            "therapeutic": {
                ChoiceType.THERAPEUTIC: 1.0,
                ChoiceType.SKILL_BUILDING: 0.8,
                ChoiceType.EMOTIONAL_REGULATION: 0.8,
                ChoiceType.NARRATIVE: 0.4,
                ChoiceType.SOCIAL_INTERACTION: 0.6,
            },
            "exploration": {
                ChoiceType.NARRATIVE: 1.0,
                ChoiceType.SOCIAL_INTERACTION: 0.8,
                ChoiceType.THERAPEUTIC: 0.6,
                ChoiceType.SKILL_BUILDING: 0.4,
                ChoiceType.EMOTIONAL_REGULATION: 0.4,
            },
            "challenge": {
                ChoiceType.SKILL_BUILDING: 1.0,
                ChoiceType.NARRATIVE: 0.8,
                ChoiceType.THERAPEUTIC: 0.6,
                ChoiceType.EMOTIONAL_REGULATION: 0.7,
                ChoiceType.SOCIAL_INTERACTION: 0.5,
            },
        }

        scene_type = scene.scene_type.value
        preferences = scene_type_preferences.get(scene_type, {})

        return preferences.get(choice.choice_type, 0.5)
