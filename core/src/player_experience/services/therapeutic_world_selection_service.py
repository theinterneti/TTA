"""
Therapeutic World Selection Service

This service selects appropriate story worlds and scenarios based on player therapeutic goals
and character attributes, ensuring optimal therapeutic alignment and engagement.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..managers.world_management_module import WorldManagementModule
from ..models.character import Character
from ..models.world import WorldDetails as World

logger = logging.getLogger(__name__)


class TherapeuticGoal(str, Enum):
    """Standardized therapeutic goals."""

    ANXIETY_MANAGEMENT = "anxiety_management"
    SOCIAL_SKILLS = "social_skills"
    SELF_ESTEEM = "self_esteem"
    EMOTIONAL_REGULATION = "emotional_regulation"
    DEPRESSION_SUPPORT = "depression_support"
    TRAUMA_PROCESSING = "trauma_processing"
    GRIEF_PROCESSING = "grief_processing"
    ANGER_MANAGEMENT = "anger_management"
    COMMUNICATION_SKILLS = "communication_skills"
    BOUNDARY_SETTING = "boundary_setting"
    MINDFULNESS = "mindfulness"
    STRESS_MANAGEMENT = "stress_management"
    SELF_AWARENESS = "self_awareness"
    RESILIENCE_BUILDING = "resilience_building"
    RELATIONSHIP_SKILLS = "relationship_skills"


class WorldTheme(str, Enum):
    """World themes for therapeutic alignment."""

    NATURE_HEALING = "nature_healing"
    URBAN_EXPLORATION = "urban_exploration"
    FANTASY_ADVENTURE = "fantasy_adventure"
    HISTORICAL_JOURNEY = "historical_journey"
    SPACE_EXPLORATION = "space_exploration"
    MYSTERY_SOLVING = "mystery_solving"
    COMMUNITY_BUILDING = "community_building"
    ARTISTIC_EXPRESSION = "artistic_expression"
    SCIENTIFIC_DISCOVERY = "scientific_discovery"
    SPIRITUAL_JOURNEY = "spiritual_journey"
    FAMILY_DYNAMICS = "family_dynamics"
    WORKPLACE_SCENARIOS = "workplace_scenarios"
    EDUCATIONAL_SETTING = "educational_setting"
    THERAPEUTIC_SANCTUARY = "therapeutic_sanctuary"


@dataclass
class WorldSelectionCriteria:
    """Criteria for world selection."""

    therapeutic_goals: list[str]
    character_attributes: dict[str, Any]
    player_preferences: dict[str, Any]
    difficulty_preference: str = "medium"
    theme_preferences: list[str] = None
    avoid_themes: list[str] = None

    def __post_init__(self):
        if self.theme_preferences is None:
            self.theme_preferences = []
        if self.avoid_themes is None:
            self.avoid_themes = []


@dataclass
class WorldSelectionResult:
    """Result of world selection process."""

    selected_world: World | None
    compatibility_score: float
    therapeutic_alignment: dict[str, float]
    selection_reasoning: list[str]
    alternative_worlds: list[tuple[World, float]]
    success: bool
    error_message: str | None = None


class TherapeuticWorldSelectionService:
    """
    Service for selecting story worlds based on therapeutic goals and character attributes.

    Provides intelligent world selection that maximizes therapeutic benefit while
    maintaining player engagement and narrative coherence.
    """

    def __init__(self, world_manager: WorldManagementModule | None = None):
        """
        Initialize the Therapeutic World Selection Service.

        Args:
            world_manager: Manager for world data and operations
        """
        self.world_manager = world_manager or WorldManagementModule()

        # Therapeutic alignment matrices
        self.goal_world_alignment = self._build_goal_world_alignment_matrix()
        self.character_world_compatibility = self._build_character_world_compatibility()
        self.therapeutic_effectiveness_weights = self._build_effectiveness_weights()

        # Selection parameters
        self.min_compatibility_score = 0.6
        self.max_alternatives = 5
        self.diversity_bonus = 0.1

        # Metrics
        self.metrics = {
            "worlds_evaluated": 0,
            "selections_made": 0,
            "high_compatibility_selections": 0,
            "therapeutic_alignments_calculated": 0,
            "selection_failures": 0,
        }

        logger.info("TherapeuticWorldSelectionService initialized")

    async def select_optimal_world(
        self,
        therapeutic_goals: list[str],
        character_data: Character,
        player_preferences: dict[str, Any] | None = None,
    ) -> WorldSelectionResult:
        """
        Select the optimal world for therapeutic goals and character.

        Args:
            therapeutic_goals: List of therapeutic goals
            character_data: Character data and attributes
            player_preferences: Optional player preferences

        Returns:
            WorldSelectionResult with selected world and analysis
        """
        try:
            # Create selection criteria
            criteria = WorldSelectionCriteria(
                therapeutic_goals=therapeutic_goals,
                character_attributes=getattr(character_data, "attributes", {}) or {},
                player_preferences=player_preferences or {},
            )

            # Get available worlds
            available_worlds = await self.world_manager.get_available_worlds()
            if not available_worlds:
                return WorldSelectionResult(
                    selected_world=None,
                    compatibility_score=0.0,
                    therapeutic_alignment={},
                    selection_reasoning=["No worlds available"],
                    alternative_worlds=[],
                    success=False,
                    error_message="No worlds available for selection",
                )

            # Evaluate all worlds
            world_evaluations = []
            for world in available_worlds:
                evaluation = await self._evaluate_world_compatibility(world, criteria)
                world_evaluations.append((world, evaluation))
                self.metrics["worlds_evaluated"] += 1

            # Sort by compatibility score
            world_evaluations.sort(key=lambda x: x[1]["total_score"], reverse=True)

            # Select best world
            best_world, best_evaluation = world_evaluations[0]

            # Check if compatibility meets minimum threshold
            if best_evaluation["total_score"] < self.min_compatibility_score:
                return WorldSelectionResult(
                    selected_world=None,
                    compatibility_score=best_evaluation["total_score"],
                    therapeutic_alignment=best_evaluation["therapeutic_alignment"],
                    selection_reasoning=[
                        "No worlds meet minimum compatibility threshold"
                    ],
                    alternative_worlds=[
                        (w, e["total_score"])
                        for w, e in world_evaluations[: self.max_alternatives]
                    ],
                    success=False,
                    error_message=f"Best compatibility score {best_evaluation['total_score']:.2f} below threshold {self.min_compatibility_score}",
                )

            # Prepare alternative worlds
            alternatives = [
                (world, evaluation["total_score"])
                for world, evaluation in world_evaluations[
                    1 : self.max_alternatives + 1
                ]
            ]

            # Update metrics
            self.metrics["selections_made"] += 1
            if best_evaluation["total_score"] > 0.8:
                self.metrics["high_compatibility_selections"] += 1

            return WorldSelectionResult(
                selected_world=best_world,
                compatibility_score=best_evaluation["total_score"],
                therapeutic_alignment=best_evaluation["therapeutic_alignment"],
                selection_reasoning=best_evaluation["reasoning"],
                alternative_worlds=alternatives,
                success=True,
            )

        except Exception as e:
            logger.error(f"Error selecting optimal world: {e}")
            self.metrics["selection_failures"] += 1
            return WorldSelectionResult(
                selected_world=None,
                compatibility_score=0.0,
                therapeutic_alignment={},
                selection_reasoning=[],
                alternative_worlds=[],
                success=False,
                error_message=str(e),
            )

    async def _evaluate_world_compatibility(
        self, world: World, criteria: WorldSelectionCriteria
    ) -> dict[str, Any]:
        """Evaluate compatibility between a world and selection criteria."""
        try:
            evaluation = {
                "therapeutic_alignment": {},
                "character_compatibility": 0.0,
                "preference_match": 0.0,
                "total_score": 0.0,
                "reasoning": [],
            }

            # Calculate therapeutic alignment for each goal
            therapeutic_scores = []
            for goal in criteria.therapeutic_goals:
                alignment_score = self._calculate_therapeutic_alignment(world, goal)
                evaluation["therapeutic_alignment"][goal] = alignment_score
                therapeutic_scores.append(alignment_score)

                if alignment_score > 0.7:
                    evaluation["reasoning"].append(
                        f"Strong therapeutic alignment for {goal}"
                    )
                elif alignment_score < 0.3:
                    evaluation["reasoning"].append(
                        f"Weak therapeutic alignment for {goal}"
                    )

            # Average therapeutic alignment
            avg_therapeutic_score = (
                sum(therapeutic_scores) / len(therapeutic_scores)
                if therapeutic_scores
                else 0.0
            )

            # Calculate character compatibility
            character_score = self._calculate_character_compatibility(
                world, criteria.character_attributes
            )
            evaluation["character_compatibility"] = character_score

            if character_score > 0.7:
                evaluation["reasoning"].append("High character compatibility")
            elif character_score < 0.3:
                evaluation["reasoning"].append("Low character compatibility")

            # Calculate preference match
            preference_score = self._calculate_preference_match(
                world, criteria.player_preferences
            )
            evaluation["preference_match"] = preference_score

            # Calculate total score with weights
            total_score = (
                avg_therapeutic_score * 0.5  # 50% weight on therapeutic alignment
                + character_score * 0.3  # 30% weight on character compatibility
                + preference_score * 0.2  # 20% weight on preferences
            )

            evaluation["total_score"] = total_score
            self.metrics["therapeutic_alignments_calculated"] += 1

            return evaluation

        except Exception as e:
            logger.error(f"Error evaluating world compatibility: {e}")
            return {
                "therapeutic_alignment": {},
                "character_compatibility": 0.0,
                "preference_match": 0.0,
                "total_score": 0.0,
                "reasoning": [f"Evaluation error: {str(e)}"],
            }

    def _calculate_therapeutic_alignment(
        self, world: World, therapeutic_goal: str
    ) -> float:
        """Calculate how well a world aligns with a specific therapeutic goal."""
        try:
            # Get world's therapeutic focus
            world_therapeutic_focus = getattr(world, "therapeutic_focus", []) or []
            world_themes = getattr(world, "themes", []) or []

            # Direct therapeutic focus match
            if therapeutic_goal in world_therapeutic_focus:
                return 1.0

            # Use alignment matrix for indirect matches
            alignment_scores = self.goal_world_alignment.get(therapeutic_goal, {})

            # Check theme alignments
            theme_scores = []
            for theme in world_themes:
                if theme in alignment_scores:
                    theme_scores.append(alignment_scores[theme])

            # Return highest theme alignment or default
            return max(theme_scores) if theme_scores else 0.2

        except Exception as e:
            logger.error(f"Error calculating therapeutic alignment: {e}")
            return 0.0

    def _calculate_character_compatibility(
        self, world: World, character_attributes: dict[str, Any]
    ) -> float:
        """Calculate compatibility between world and character attributes."""
        try:
            compatibility_score = 0.0
            factors_evaluated = 0

            # Personality compatibility
            personality = character_attributes.get("personality_type", "")
            if personality:
                personality_scores = self.character_world_compatibility.get(
                    "personality", {}
                )
                world_themes = getattr(world, "themes", []) or []

                for theme in world_themes:
                    theme_compatibility = personality_scores.get(personality, {}).get(
                        theme, 0.5
                    )
                    compatibility_score += theme_compatibility
                    factors_evaluated += 1

            # Experience level compatibility
            experience_level = character_attributes.get("experience_level", "beginner")
            world_difficulty = getattr(world, "difficulty_level", "medium")

            difficulty_compatibility = {
                ("beginner", "easy"): 1.0,
                ("beginner", "medium"): 0.7,
                ("beginner", "hard"): 0.3,
                ("intermediate", "easy"): 0.8,
                ("intermediate", "medium"): 1.0,
                ("intermediate", "hard"): 0.8,
                ("advanced", "easy"): 0.6,
                ("advanced", "medium"): 0.9,
                ("advanced", "hard"): 1.0,
            }

            difficulty_score = difficulty_compatibility.get(
                (experience_level, world_difficulty), 0.5
            )
            compatibility_score += difficulty_score
            factors_evaluated += 1

            # Interest alignment
            interests = character_attributes.get("interests", [])
            if interests:
                world_themes = getattr(world, "themes", []) or []
                interest_matches = len(set(interests) & set(world_themes))
                interest_score = (
                    min(interest_matches / len(interests), 1.0) if interests else 0.5
                )
                compatibility_score += interest_score
                factors_evaluated += 1

            # Average the compatibility factors
            return (
                compatibility_score / factors_evaluated
                if factors_evaluated > 0
                else 0.5
            )

        except Exception as e:
            logger.error(f"Error calculating character compatibility: {e}")
            return 0.0

    def _calculate_preference_match(
        self, world: World, player_preferences: dict[str, Any]
    ) -> float:
        """Calculate how well a world matches player preferences."""
        try:
            preference_score = 0.0
            preferences_evaluated = 0

            # Theme preferences
            preferred_themes = player_preferences.get("preferred_themes", [])
            avoided_themes = player_preferences.get("avoided_themes", [])
            world_themes = getattr(world, "themes", []) or []

            if preferred_themes:
                theme_matches = len(set(preferred_themes) & set(world_themes))
                theme_score = min(theme_matches / len(preferred_themes), 1.0)
                preference_score += theme_score
                preferences_evaluated += 1

            if avoided_themes:
                theme_conflicts = len(set(avoided_themes) & set(world_themes))
                avoidance_score = 1.0 - min(theme_conflicts / len(avoided_themes), 1.0)
                preference_score += avoidance_score
                preferences_evaluated += 1

            # Difficulty preference
            preferred_difficulty = player_preferences.get("difficulty", "medium")
            world_difficulty = getattr(world, "difficulty_level", "medium")

            if preferred_difficulty == world_difficulty:
                preference_score += 1.0
            elif (
                abs(
                    ["easy", "medium", "hard"].index(preferred_difficulty)
                    - ["easy", "medium", "hard"].index(world_difficulty)
                )
                == 1
            ):
                preference_score += 0.7
            else:
                preference_score += 0.3
            preferences_evaluated += 1

            # Session length preference
            preferred_length = player_preferences.get("session_length", "medium")
            world_typical_length = getattr(world, "typical_session_length", "medium")

            if preferred_length == world_typical_length:
                preference_score += 1.0
            else:
                preference_score += 0.6
            preferences_evaluated += 1

            return (
                preference_score / preferences_evaluated
                if preferences_evaluated > 0
                else 0.5
            )

        except Exception as e:
            logger.error(f"Error calculating preference match: {e}")
            return 0.0

    def _build_goal_world_alignment_matrix(self) -> dict[str, dict[str, float]]:
        """Build the therapeutic goal to world theme alignment matrix."""
        return {
            TherapeuticGoal.ANXIETY_MANAGEMENT: {
                WorldTheme.NATURE_HEALING: 0.9,
                WorldTheme.THERAPEUTIC_SANCTUARY: 1.0,
                WorldTheme.MINDFULNESS: 0.8,
                WorldTheme.ARTISTIC_EXPRESSION: 0.7,
                WorldTheme.SPACE_EXPLORATION: 0.3,  # Can be overwhelming
                WorldTheme.MYSTERY_SOLVING: 0.4,  # May increase anxiety
            },
            TherapeuticGoal.SOCIAL_SKILLS: {
                WorldTheme.COMMUNITY_BUILDING: 1.0,
                WorldTheme.WORKPLACE_SCENARIOS: 0.9,
                WorldTheme.EDUCATIONAL_SETTING: 0.8,
                WorldTheme.FAMILY_DYNAMICS: 0.8,
                WorldTheme.URBAN_EXPLORATION: 0.6,
                WorldTheme.NATURE_HEALING: 0.3,  # Limited social interaction
            },
            TherapeuticGoal.SELF_ESTEEM: {
                WorldTheme.ARTISTIC_EXPRESSION: 0.9,
                WorldTheme.SCIENTIFIC_DISCOVERY: 0.8,
                WorldTheme.FANTASY_ADVENTURE: 0.8,
                WorldTheme.COMMUNITY_BUILDING: 0.7,
                WorldTheme.EDUCATIONAL_SETTING: 0.6,
                WorldTheme.MYSTERY_SOLVING: 0.7,
            },
            TherapeuticGoal.EMOTIONAL_REGULATION: {
                WorldTheme.NATURE_HEALING: 0.9,
                WorldTheme.THERAPEUTIC_SANCTUARY: 1.0,
                WorldTheme.ARTISTIC_EXPRESSION: 0.8,
                WorldTheme.SPIRITUAL_JOURNEY: 0.8,
                WorldTheme.FAMILY_DYNAMICS: 0.6,
                WorldTheme.WORKPLACE_SCENARIOS: 0.5,
            },
            TherapeuticGoal.DEPRESSION_SUPPORT: {
                WorldTheme.NATURE_HEALING: 0.8,
                WorldTheme.COMMUNITY_BUILDING: 0.9,
                WorldTheme.ARTISTIC_EXPRESSION: 0.8,
                WorldTheme.FANTASY_ADVENTURE: 0.7,
                WorldTheme.THERAPEUTIC_SANCTUARY: 0.9,
                WorldTheme.SPIRITUAL_JOURNEY: 0.7,
            },
            TherapeuticGoal.TRAUMA_PROCESSING: {
                WorldTheme.THERAPEUTIC_SANCTUARY: 1.0,
                WorldTheme.NATURE_HEALING: 0.8,
                WorldTheme.SPIRITUAL_JOURNEY: 0.7,
                WorldTheme.ARTISTIC_EXPRESSION: 0.6,
                WorldTheme.FANTASY_ADVENTURE: 0.4,  # May be triggering
                WorldTheme.MYSTERY_SOLVING: 0.2,  # May be triggering
            },
            TherapeuticGoal.COMMUNICATION_SKILLS: {
                WorldTheme.WORKPLACE_SCENARIOS: 0.9,
                WorldTheme.FAMILY_DYNAMICS: 0.9,
                WorldTheme.COMMUNITY_BUILDING: 0.8,
                WorldTheme.EDUCATIONAL_SETTING: 0.8,
                WorldTheme.URBAN_EXPLORATION: 0.6,
                WorldTheme.MYSTERY_SOLVING: 0.5,
            },
            TherapeuticGoal.MINDFULNESS: {
                WorldTheme.NATURE_HEALING: 1.0,
                WorldTheme.THERAPEUTIC_SANCTUARY: 0.9,
                WorldTheme.SPIRITUAL_JOURNEY: 0.9,
                WorldTheme.ARTISTIC_EXPRESSION: 0.7,
                WorldTheme.SCIENTIFIC_DISCOVERY: 0.5,
                WorldTheme.SPACE_EXPLORATION: 0.6,
            },
            TherapeuticGoal.RESILIENCE_BUILDING: {
                WorldTheme.FANTASY_ADVENTURE: 0.9,
                WorldTheme.SPACE_EXPLORATION: 0.8,
                WorldTheme.MYSTERY_SOLVING: 0.8,
                WorldTheme.SCIENTIFIC_DISCOVERY: 0.7,
                WorldTheme.HISTORICAL_JOURNEY: 0.7,
                WorldTheme.COMMUNITY_BUILDING: 0.6,
            },
        }

    def _build_character_world_compatibility(
        self,
    ) -> dict[str, dict[str, dict[str, float]]]:
        """Build character attribute to world compatibility matrix."""
        return {
            "personality": {
                "adventurous": {
                    WorldTheme.FANTASY_ADVENTURE: 0.9,
                    WorldTheme.SPACE_EXPLORATION: 0.8,
                    WorldTheme.MYSTERY_SOLVING: 0.7,
                    WorldTheme.HISTORICAL_JOURNEY: 0.6,
                    WorldTheme.THERAPEUTIC_SANCTUARY: 0.3,
                },
                "analytical": {
                    WorldTheme.MYSTERY_SOLVING: 0.9,
                    WorldTheme.SCIENTIFIC_DISCOVERY: 0.9,
                    WorldTheme.SPACE_EXPLORATION: 0.7,
                    WorldTheme.EDUCATIONAL_SETTING: 0.6,
                    WorldTheme.ARTISTIC_EXPRESSION: 0.4,
                },
                "social": {
                    WorldTheme.COMMUNITY_BUILDING: 0.9,
                    WorldTheme.WORKPLACE_SCENARIOS: 0.8,
                    WorldTheme.FAMILY_DYNAMICS: 0.8,
                    WorldTheme.URBAN_EXPLORATION: 0.7,
                    WorldTheme.NATURE_HEALING: 0.4,
                },
                "creative": {
                    WorldTheme.ARTISTIC_EXPRESSION: 0.9,
                    WorldTheme.FANTASY_ADVENTURE: 0.8,
                    WorldTheme.SPIRITUAL_JOURNEY: 0.7,
                    WorldTheme.SCIENTIFIC_DISCOVERY: 0.6,
                    WorldTheme.WORKPLACE_SCENARIOS: 0.4,
                },
                "introspective": {
                    WorldTheme.NATURE_HEALING: 0.9,
                    WorldTheme.THERAPEUTIC_SANCTUARY: 0.9,
                    WorldTheme.SPIRITUAL_JOURNEY: 0.8,
                    WorldTheme.ARTISTIC_EXPRESSION: 0.7,
                    WorldTheme.COMMUNITY_BUILDING: 0.3,
                },
            }
        }

    def _build_effectiveness_weights(self) -> dict[str, float]:
        """Build therapeutic effectiveness weights for different factors."""
        return {
            "direct_therapeutic_match": 1.0,
            "indirect_therapeutic_benefit": 0.7,
            "character_personality_match": 0.8,
            "experience_level_appropriate": 0.6,
            "player_preference_match": 0.5,
            "theme_diversity_bonus": 0.1,
            "safety_considerations": 0.9,
        }

    async def get_world_recommendations(
        self,
        therapeutic_goals: list[str],
        character_data: Character,
        player_preferences: dict[str, Any] | None = None,
        num_recommendations: int = 3,
    ) -> list[WorldSelectionResult]:
        """
        Get multiple world recommendations ranked by compatibility.

        Args:
            therapeutic_goals: List of therapeutic goals
            character_data: Character data and attributes
            player_preferences: Optional player preferences
            num_recommendations: Number of recommendations to return

        Returns:
            List of WorldSelectionResult objects ranked by compatibility
        """
        try:
            # Get the optimal world selection
            primary_result = await self.select_optimal_world(
                therapeutic_goals, character_data, player_preferences
            )

            if not primary_result.success:
                return [primary_result]

            # Create additional recommendations from alternatives
            recommendations = [primary_result]

            for world, score in primary_result.alternative_worlds[
                : num_recommendations - 1
            ]:
                # Create detailed evaluation for each alternative
                criteria = WorldSelectionCriteria(
                    therapeutic_goals=therapeutic_goals,
                    character_attributes=getattr(character_data, "attributes", {})
                    or {},
                    player_preferences=player_preferences or {},
                )

                evaluation = await self._evaluate_world_compatibility(world, criteria)

                alt_result = WorldSelectionResult(
                    selected_world=world,
                    compatibility_score=score,
                    therapeutic_alignment=evaluation["therapeutic_alignment"],
                    selection_reasoning=evaluation["reasoning"],
                    alternative_worlds=[],
                    success=True,
                )

                recommendations.append(alt_result)

            return recommendations

        except Exception as e:
            logger.error(f"Error getting world recommendations: {e}")
            return [
                WorldSelectionResult(
                    selected_world=None,
                    compatibility_score=0.0,
                    therapeutic_alignment={},
                    selection_reasoning=[],
                    alternative_worlds=[],
                    success=False,
                    error_message=str(e),
                )
            ]

    def get_therapeutic_world_mapping(self) -> dict[str, list[str]]:
        """Get mapping of therapeutic goals to recommended world themes."""
        mapping = {}
        for goal, theme_scores in self.goal_world_alignment.items():
            # Get themes with score > 0.6
            recommended_themes = [
                theme for theme, score in theme_scores.items() if score > 0.6
            ]
            mapping[goal] = recommended_themes
        return mapping

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the world selection service."""
        return {
            **self.metrics,
            "alignment_matrix_size": len(self.goal_world_alignment),
            "compatibility_matrix_size": len(self.character_world_compatibility),
        }
