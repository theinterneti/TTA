"""

# Logseq: [[TTA.dev/Player_experience/Utils/Compatibility_checker]]
Advanced compatibility checking system for character-world matching.

This module provides sophisticated algorithms for assessing compatibility
between characters and worlds based on therapeutic preferences, readiness levels,
and safety considerations.
"""

import logging
from dataclasses import dataclass
from typing import Any

from ..models.character import Character, TherapeuticProfile
from ..models.enums import DifficultyLevel
from ..models.world import (
    CompatibilityFactor,
    CompatibilityReport,
    WorldDetails,
    WorldPrerequisite,
)

logger = logging.getLogger(__name__)


@dataclass
class CompatibilityWeights:
    """Weights for different compatibility factors."""

    therapeutic_readiness: float = 0.25
    therapeutic_approach_alignment: float = 0.30
    content_safety: float = 0.25
    difficulty_appropriateness: float = 0.15
    prerequisite_fulfillment: float = 0.05


class CompatibilityChecker:
    """Advanced compatibility checking system for character-world matching."""

    def __init__(self, weights: CompatibilityWeights | None = None):
        """
        Initialize the compatibility checker.

        Args:
            weights: Optional custom weights for compatibility factors
        """
        self.weights = weights or CompatibilityWeights()
        self._compatibility_threshold = 0.6
        logger.info("CompatibilityChecker initialized")

    def calculate_comprehensive_compatibility(
        self, character: Character, world: WorldDetails
    ) -> CompatibilityReport:
        """
        Calculate comprehensive compatibility between a character and world.

        Args:
            character: Character to assess compatibility for
            world: World to assess compatibility with

        Returns:
            Detailed CompatibilityReport with scores and recommendations
        """
        logger.info(
            f"Calculating compatibility between character {character.character_id} and world {world.world_id}"
        )

        compatibility_report = CompatibilityReport(
            character_id=character.character_id,
            world_id=world.world_id,
            overall_score=0.0,
        )

        # Calculate individual compatibility factors
        factors = []

        # 1. Therapeutic Readiness Compatibility
        readiness_factor = self._calculate_therapeutic_readiness_compatibility(
            character.therapeutic_profile, world
        )
        factors.append(readiness_factor)

        # 2. Therapeutic Approach Alignment
        approach_factor = self._calculate_therapeutic_approach_alignment(
            character.therapeutic_profile, world
        )
        factors.append(approach_factor)

        # 3. Content Safety Assessment
        safety_factor = self._calculate_content_safety_compatibility(
            character.therapeutic_profile, world
        )
        factors.append(safety_factor)

        # 4. Difficulty Appropriateness
        difficulty_factor = self._calculate_difficulty_appropriateness(
            character.therapeutic_profile, world
        )
        factors.append(difficulty_factor)

        # 5. Prerequisite Fulfillment
        prerequisite_factor = self._calculate_prerequisite_fulfillment(
            character.therapeutic_profile, world
        )
        factors.append(prerequisite_factor)

        # Add all factors to the report
        for factor in factors:
            compatibility_report.add_compatibility_factor(factor)

        # Check prerequisites
        unmet_prerequisites = self._check_prerequisites(
            character.therapeutic_profile, world
        )
        compatibility_report.unmet_prerequisites = unmet_prerequisites
        compatibility_report.prerequisites_met = len(unmet_prerequisites) == 0

        # Generate recommendations and warnings
        self._generate_recommendations_and_warnings(
            compatibility_report, character, world
        )

        logger.info(f"Compatibility score: {compatibility_report.overall_score:.3f}")
        return compatibility_report

    def _calculate_therapeutic_readiness_compatibility(
        self, profile: TherapeuticProfile, world: WorldDetails
    ) -> CompatibilityFactor:
        """Calculate compatibility based on therapeutic readiness levels."""
        readiness_diff = abs(
            profile.readiness_level - world.recommended_therapeutic_readiness
        )

        # Score decreases as the difference increases
        # Perfect match (diff = 0) gets score 1.0
        # Maximum acceptable difference is 0.3 for score > 0
        max_acceptable_diff = 0.3
        score = max(0.0, 1.0 - (readiness_diff / max_acceptable_diff))

        explanation = f"Character readiness ({profile.readiness_level:.2f}) vs World requirement ({world.recommended_therapeutic_readiness:.2f})"

        return CompatibilityFactor(
            factor_name="Therapeutic Readiness",
            score=score,
            explanation=explanation,
            weight=self.weights.therapeutic_readiness,
        )

    def _calculate_therapeutic_approach_alignment(
        self, profile: TherapeuticProfile, world: WorldDetails
    ) -> CompatibilityFactor:
        """Calculate compatibility based on therapeutic approach alignment."""
        if not world.therapeutic_approaches:
            return CompatibilityFactor(
                factor_name="Therapeutic Approach Alignment",
                score=0.5,  # Neutral score if no approaches specified
                explanation="No specific therapeutic approaches defined for this world",
                weight=self.weights.therapeutic_approach_alignment,
            )

        # Get character's preferred approaches from therapeutic goals
        character_approaches = set()
        for goal in profile.therapeutic_goals:
            character_approaches.update(
                approach.value for approach in goal.therapeutic_approaches
            )

        world_approaches = {approach.value for approach in world.therapeutic_approaches}

        if not character_approaches:
            # If character has no specific preferences, give moderate score
            score = 0.6
            explanation = "Character has no specific therapeutic approach preferences"
        else:
            # Calculate overlap percentage
            overlap = character_approaches.intersection(world_approaches)
            overlap_percentage = len(overlap) / len(character_approaches)

            # Also consider how well the world covers character's needs
            coverage_percentage = (
                len(overlap) / len(world_approaches) if world_approaches else 0
            )

            # Weighted average of overlap and coverage
            score = (overlap_percentage * 0.7) + (coverage_percentage * 0.3)

            explanation = f"Approach overlap: {len(overlap)}/{len(character_approaches)} character preferences matched"

        return CompatibilityFactor(
            factor_name="Therapeutic Approach Alignment",
            score=score,
            explanation=explanation,
            weight=self.weights.therapeutic_approach_alignment,
        )

    def _calculate_content_safety_compatibility(
        self, profile: TherapeuticProfile, world: WorldDetails
    ) -> CompatibilityFactor:
        """Calculate compatibility based on content safety considerations."""
        character_triggers = set(profile.trigger_topics)
        world_warnings = set(world.content_warnings)

        if not character_triggers:
            # If no triggers specified, assume safe
            score = 1.0
            explanation = "No trigger topics specified for character"
        elif not world_warnings:
            # If no warnings specified for world, assume safe
            score = 0.9
            explanation = "No content warnings specified for world"
        else:
            # Check for overlap between triggers and warnings
            trigger_overlap = character_triggers.intersection(world_warnings)

            if trigger_overlap:
                # Reduce score based on number of overlapping triggers
                overlap_ratio = len(trigger_overlap) / len(character_triggers)
                score = max(
                    0.0, 1.0 - (overlap_ratio * 0.8)
                )  # Don't go below 0.2 for partial overlaps
                explanation = (
                    f"Potential triggers detected: {', '.join(trigger_overlap)}"
                )
            else:
                score = 1.0
                explanation = "No trigger topics overlap with world content"

        return CompatibilityFactor(
            factor_name="Content Safety",
            score=score,
            explanation=explanation,
            weight=self.weights.content_safety,
        )

    def _calculate_difficulty_appropriateness(
        self, profile: TherapeuticProfile, world: WorldDetails
    ) -> CompatibilityFactor:
        """Calculate compatibility based on difficulty level appropriateness."""
        # Map readiness levels to appropriate difficulty levels
        readiness_to_difficulty = [
            (0.0, 0.3, DifficultyLevel.BEGINNER),
            (0.3, 0.6, DifficultyLevel.INTERMEDIATE),
            (0.6, 0.8, DifficultyLevel.ADVANCED),
            (0.8, 1.0, DifficultyLevel.EXPERT),
        ]

        # Find appropriate difficulty for character's readiness
        appropriate_difficulty = DifficultyLevel.BEGINNER
        for min_readiness, max_readiness, difficulty in readiness_to_difficulty:
            if min_readiness <= profile.readiness_level < max_readiness:
                appropriate_difficulty = difficulty
                break

        # Handle edge case for exactly 1.0 readiness
        if profile.readiness_level >= 0.8:
            appropriate_difficulty = DifficultyLevel.EXPERT

        # Calculate score based on difficulty match
        difficulty_order = [
            DifficultyLevel.BEGINNER,
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.ADVANCED,
            DifficultyLevel.EXPERT,
        ]

        appropriate_index = difficulty_order.index(appropriate_difficulty)
        world_index = difficulty_order.index(world.difficulty_level)

        # Perfect match gets 1.0, adjacent levels get 0.7, further levels get lower scores
        index_diff = abs(appropriate_index - world_index)
        if index_diff == 0:
            score = 1.0
        elif index_diff == 1:
            score = 0.7
        elif index_diff == 2:
            score = 0.4
        else:
            score = 0.1

        explanation = f"Character readiness suggests {appropriate_difficulty.value}, world is {world.difficulty_level.value}"

        return CompatibilityFactor(
            factor_name="Difficulty Appropriateness",
            score=score,
            explanation=explanation,
            weight=self.weights.difficulty_appropriateness,
        )

    def _calculate_prerequisite_fulfillment(
        self, profile: TherapeuticProfile, world: WorldDetails
    ) -> CompatibilityFactor:
        """Calculate compatibility based on prerequisite fulfillment."""
        if not world.prerequisites:
            return CompatibilityFactor(
                factor_name="Prerequisite Fulfillment",
                score=1.0,
                explanation="No prerequisites required for this world",
                weight=self.weights.prerequisite_fulfillment,
            )

        unmet_prerequisites = self._check_prerequisites(profile, world)
        met_count = len(world.prerequisites) - len(unmet_prerequisites)

        if len(world.prerequisites) == 0:
            score = 1.0
        else:
            score = met_count / len(world.prerequisites)

        explanation = f"Prerequisites met: {met_count}/{len(world.prerequisites)}"

        return CompatibilityFactor(
            factor_name="Prerequisite Fulfillment",
            score=score,
            explanation=explanation,
            weight=self.weights.prerequisite_fulfillment,
        )

    def _check_prerequisites(
        self, profile: TherapeuticProfile, world: WorldDetails
    ) -> list[WorldPrerequisite]:
        """Check which prerequisites are not met by the character."""
        unmet_prerequisites = []

        for prerequisite in world.prerequisites:
            is_met = False

            if prerequisite.prerequisite_type == "therapeutic_readiness":
                is_met = profile.readiness_level >= prerequisite.required_value
            elif prerequisite.prerequisite_type == "completed_worlds":
                # This would require access to character's world completion history
                # For now, assume not met if we can't verify
                is_met = False
            elif prerequisite.prerequisite_type == "skill_level":
                # This would require access to character's skill assessments
                # For now, assume met if readiness is sufficient
                is_met = profile.readiness_level >= 0.5

            prerequisite.is_met = is_met
            if not is_met:
                unmet_prerequisites.append(prerequisite)

        return unmet_prerequisites

    def _generate_recommendations_and_warnings(
        self, report: CompatibilityReport, character: Character, world: WorldDetails
    ) -> None:
        """Generate recommendations and warnings based on compatibility assessment."""
        # Low overall compatibility
        if report.overall_score < self._compatibility_threshold:
            if report.overall_score < 0.3:
                report.recommendations.append(
                    "This world may not be suitable for your current therapeutic needs. "
                    "Consider starting with a beginner-level world to build readiness."
                )
            else:
                report.recommendations.append(
                    "This world has moderate compatibility. Consider customizing world parameters "
                    "to better match your preferences."
                )

        # Specific factor-based recommendations
        for factor in report.compatibility_factors:
            if factor.factor_name == "Therapeutic Readiness" and factor.score < 0.5:
                if (
                    character.therapeutic_profile.readiness_level
                    < world.recommended_therapeutic_readiness
                ):
                    report.recommendations.append(
                        "Consider building therapeutic readiness through easier worlds first."
                    )
                else:
                    report.recommendations.append(
                        "You may find this world less challenging than optimal. "
                        "Consider a more advanced world for better growth."
                    )

            elif factor.factor_name == "Content Safety" and factor.score < 0.7:
                report.warnings.append(
                    "This world contains content that may trigger difficult emotions. "
                    "Ensure you have adequate support available."
                )

            elif (
                factor.factor_name == "Difficulty Appropriateness"
                and factor.score < 0.5
            ):
                if world.difficulty_level.value in ["advanced", "expert"]:
                    report.recommendations.append(
                        "This world may be too challenging. Consider starting with an intermediate world."
                    )
                else:
                    report.recommendations.append(
                        "This world may be too easy. Consider a more challenging world for better engagement."
                    )

        # Prerequisite warnings
        if not report.prerequisites_met:
            report.warnings.append(
                f"You have {len(report.unmet_prerequisites)} unmet prerequisites for this world."
            )

        # Positive reinforcement for good matches
        if report.overall_score >= 0.8:
            report.recommendations.append(
                "This world appears to be an excellent match for your therapeutic goals and readiness level!"
            )

    def get_world_recommendations(
        self,
        character: Character,
        available_worlds: list[WorldDetails],
        max_recommendations: int = 5,
    ) -> list[tuple[WorldDetails, CompatibilityReport]]:
        """
        Get recommended worlds for a character based on compatibility scores.

        Args:
            character: Character to get recommendations for
            available_worlds: List of available worlds to choose from
            max_recommendations: Maximum number of recommendations to return

        Returns:
            List of (WorldDetails, CompatibilityReport) tuples, sorted by compatibility score
        """
        logger.info(
            f"Getting world recommendations for character {character.character_id}"
        )

        recommendations = []

        for world in available_worlds:
            compatibility_report = self.calculate_comprehensive_compatibility(
                character, world
            )
            recommendations.append((world, compatibility_report))

        # Sort by compatibility score (highest first)
        recommendations.sort(key=lambda x: x[1].overall_score, reverse=True)

        # Return top recommendations
        top_recommendations = recommendations[:max_recommendations]

        logger.info(f"Generated {len(top_recommendations)} world recommendations")
        return top_recommendations

    def assess_world_suitability(
        self, character: Character, world: WorldDetails
    ) -> dict[str, Any]:
        """
        Assess overall suitability of a world for a character.

        Args:
            character: Character to assess suitability for
            world: World to assess

        Returns:
            Dictionary with suitability assessment results
        """
        compatibility_report = self.calculate_comprehensive_compatibility(
            character, world
        )

        # Determine suitability level
        if compatibility_report.overall_score >= 0.8:
            suitability_level = "Excellent"
        elif compatibility_report.overall_score >= 0.6:
            suitability_level = "Good"
        elif compatibility_report.overall_score >= 0.4:
            suitability_level = "Fair"
        else:
            suitability_level = "Poor"

        return {
            "suitability_level": suitability_level,
            "compatibility_score": compatibility_report.overall_score,
            "compatibility_report": compatibility_report,
            "is_recommended": compatibility_report.overall_score
            >= self._compatibility_threshold,
            "has_safety_concerns": any(
                factor.factor_name == "Content Safety" and factor.score < 0.7
                for factor in compatibility_report.compatibility_factors
            ),
            "prerequisites_met": compatibility_report.prerequisites_met,
        }
