"""
Therapeutic Profile Integration Service.

This module provides integration between character data and therapeutic profiles,
creating personalized therapeutic experiences based on character backgrounds,
personality traits, and therapeutic preferences.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..models.character import (
    Character,
    CharacterBackground,
    TherapeuticGoal,
    TherapeuticProfile,
)
from ..models.enums import IntensityLevel, TherapeuticApproach

logger = logging.getLogger(__name__)


@dataclass
class PersonalizationContext:
    """Context information for personalizing therapeutic content."""

    character_id: str
    character_name: str
    personality_traits: list[str] = field(default_factory=list)
    core_values: list[str] = field(default_factory=list)
    life_experiences: list[str] = field(default_factory=list)
    therapeutic_goals: list[TherapeuticGoal] = field(default_factory=list)
    preferred_intensity: IntensityLevel = IntensityLevel.MEDIUM
    comfort_zones: list[str] = field(default_factory=list)
    challenge_areas: list[str] = field(default_factory=list)
    trigger_topics: list[str] = field(default_factory=list)
    readiness_level: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TherapeuticAdaptation:
    """Represents an adaptation made to therapeutic content for a character."""

    adaptation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str = ""
    adaptation_type: str = (
        ""  # content_tone, difficulty_level, approach_selection, etc.
    )
    original_content: str = ""
    adapted_content: str = ""
    reasoning: str = ""
    effectiveness_score: float = 0.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PersonalizationRecommendation:
    """Recommendation for personalizing therapeutic content."""

    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str = ""
    recommendation_type: str = (
        ""  # therapeutic_approach, content_focus, intensity_adjustment
    )
    title: str = ""
    description: str = ""
    rationale: str = ""
    priority: int = 1  # 1 (highest) to 5 (lowest)
    confidence_score: float = 0.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)


class TherapeuticProfileIntegrationService:
    """Service for integrating character data with therapeutic profiles."""

    def __init__(self):
        """Initialize the Therapeutic Profile Integration Service."""
        self.personalization_contexts: dict[str, PersonalizationContext] = {}
        self.adaptations: dict[str, list[TherapeuticAdaptation]] = {}
        self.recommendations: dict[str, list[PersonalizationRecommendation]] = {}
        logger.info("TherapeuticProfileIntegrationService initialized")

    def create_therapeutic_profile_from_character(
        self, character: Character
    ) -> TherapeuticProfile:
        """
        Create or enhance a therapeutic profile based on character data.

        Args:
            character: The character to create a profile for

        Returns:
            Enhanced TherapeuticProfile
        """
        # Start with existing profile or create new one
        profile = character.therapeutic_profile or TherapeuticProfile()

        # Extract therapeutic insights from character background
        insights = self._extract_therapeutic_insights(character.background)

        # Update profile with insights
        if insights.get("primary_concerns"):
            profile.primary_concerns.extend(insights["primary_concerns"])
            # Remove duplicates while preserving order
            profile.primary_concerns = list(dict.fromkeys(profile.primary_concerns))

        if insights.get("comfort_zones"):
            profile.comfort_zones.extend(insights["comfort_zones"])
            profile.comfort_zones = list(dict.fromkeys(profile.comfort_zones))

        if insights.get("challenge_areas"):
            profile.challenge_areas.extend(insights["challenge_areas"])
            profile.challenge_areas = list(dict.fromkeys(profile.challenge_areas))

        if insights.get("coping_strategies"):
            profile.coping_strategies.extend(insights["coping_strategies"])
            profile.coping_strategies = list(dict.fromkeys(profile.coping_strategies))

        # Generate therapeutic goals based on enhanced profile
        # Create a temporary character with the enhanced profile for goal generation
        temp_character = Character(
            character_id=character.character_id,
            player_id=character.player_id,
            name=character.name,
            appearance=character.appearance,
            background=character.background,
            therapeutic_profile=profile,  # Use the enhanced profile
            created_at=character.created_at,
            last_active=character.last_active,
        )

        generated_goals = self._generate_therapeutic_goals(temp_character)
        for goal in generated_goals:
            if not any(g.goal_id == goal.goal_id for g in profile.therapeutic_goals):
                profile.therapeutic_goals.append(goal)

        # Adjust readiness level based on character traits
        readiness_adjustment = self._calculate_readiness_adjustment(
            character.background
        )
        profile.readiness_level = max(
            0.0, min(1.0, profile.readiness_level + readiness_adjustment)
        )

        logger.info(
            f"Enhanced therapeutic profile for character {character.character_id}"
        )
        return profile

    def create_personalization_context(
        self, character: Character
    ) -> PersonalizationContext:
        """
        Create a personalization context for a character.

        Args:
            character: The character to create context for

        Returns:
            PersonalizationContext object
        """
        context = PersonalizationContext(
            character_id=character.character_id,
            character_name=character.name,
            personality_traits=character.background.personality_traits.copy(),
            core_values=character.background.core_values.copy(),
            life_experiences=self._extract_life_experiences(character.background),
            therapeutic_goals=character.therapeutic_profile.therapeutic_goals.copy(),
            preferred_intensity=character.therapeutic_profile.preferred_intensity,
            comfort_zones=character.therapeutic_profile.comfort_zones.copy(),
            challenge_areas=character.therapeutic_profile.challenge_areas.copy(),
            trigger_topics=character.therapeutic_profile.trigger_topics.copy(),
            readiness_level=character.therapeutic_profile.readiness_level,
        )

        # Store context for future use
        self.personalization_contexts[character.character_id] = context

        logger.info(
            f"Created personalization context for character {character.character_id}"
        )
        return context

    def generate_personalization_recommendations(
        self, character: Character
    ) -> list[PersonalizationRecommendation]:
        """
        Generate personalization recommendations for a character.

        Args:
            character: The character to generate recommendations for

        Returns:
            List of PersonalizationRecommendation objects
        """
        recommendations = []

        # Analyze character for therapeutic approach recommendations
        approach_recs = self._recommend_therapeutic_approaches(character)
        recommendations.extend(approach_recs)

        # Analyze for content focus recommendations
        content_recs = self._recommend_content_focus(character)
        recommendations.extend(content_recs)

        # Analyze for intensity adjustments
        intensity_recs = self._recommend_intensity_adjustments(character)
        recommendations.extend(intensity_recs)

        # Store recommendations
        self.recommendations[character.character_id] = recommendations

        logger.info(
            f"Generated {len(recommendations)} personalization recommendations for character {character.character_id}"
        )
        return recommendations

    def adapt_therapeutic_content(
        self, character: Character, content: str, content_type: str = "general"
    ) -> TherapeuticAdaptation:
        """
        Adapt therapeutic content for a specific character.

        Args:
            character: The character to adapt content for
            content: The original content to adapt
            content_type: Type of content (dialogue, exercise, reflection, etc.)

        Returns:
            TherapeuticAdaptation object
        """
        context = self.personalization_contexts.get(character.character_id)
        if not context:
            context = self.create_personalization_context(character)

        # Determine adaptation strategy based on character traits and preferences
        adaptation_strategy = self._determine_adaptation_strategy(
            character, content_type
        )

        # Apply adaptations
        adapted_content = self._apply_content_adaptations(
            content, adaptation_strategy, context
        )

        # Create adaptation record
        adaptation = TherapeuticAdaptation(
            character_id=character.character_id,
            adaptation_type=adaptation_strategy["type"],
            original_content=content,
            adapted_content=adapted_content,
            reasoning=adaptation_strategy["reasoning"],
            effectiveness_score=adaptation_strategy.get("confidence", 0.7),
        )

        # Store adaptation
        if character.character_id not in self.adaptations:
            self.adaptations[character.character_id] = []
        self.adaptations[character.character_id].append(adaptation)

        logger.info(
            f"Adapted therapeutic content for character {character.character_id}"
        )
        return adaptation

    def get_character_adaptations(
        self, character_id: str
    ) -> list[TherapeuticAdaptation]:
        """Get all adaptations for a character."""
        return self.adaptations.get(character_id, [])

    def get_character_recommendations(
        self, character_id: str
    ) -> list[PersonalizationRecommendation]:
        """Get all recommendations for a character."""
        return self.recommendations.get(character_id, [])

    def update_adaptation_effectiveness(
        self, adaptation_id: str, effectiveness_score: float
    ) -> bool:
        """
        Update the effectiveness score of an adaptation based on feedback.

        Args:
            adaptation_id: The adaptation ID
            effectiveness_score: New effectiveness score (0.0 to 1.0)

        Returns:
            True if updated successfully, False if adaptation not found
        """
        for character_adaptations in self.adaptations.values():
            for adaptation in character_adaptations:
                if adaptation.adaptation_id == adaptation_id:
                    adaptation.effectiveness_score = max(
                        0.0, min(1.0, effectiveness_score)
                    )
                    logger.info(
                        f"Updated effectiveness score for adaptation {adaptation_id}"
                    )
                    return True
        return False

    def _extract_therapeutic_insights(
        self, background: CharacterBackground
    ) -> dict[str, list[str]]:
        """Extract therapeutic insights from character background."""
        insights = {
            "primary_concerns": [],
            "comfort_zones": [],
            "challenge_areas": [],
            "coping_strategies": [],
        }

        # Analyze personality traits for therapeutic insights
        for trait in background.personality_traits:
            trait_lower = trait.lower()

            if "anxious" in trait_lower or "worried" in trait_lower:
                insights["primary_concerns"].append("anxiety")
                insights["challenge_areas"].append("stress management")
            elif "perfectionist" in trait_lower:
                insights["primary_concerns"].append("perfectionism")
                insights["challenge_areas"].append("self-acceptance")
            elif "empathetic" in trait_lower or "caring" in trait_lower:
                insights["comfort_zones"].append("helping others")
                insights["coping_strategies"].append("social support")
            elif "organized" in trait_lower:
                insights["comfort_zones"].append("structure")
                insights["coping_strategies"].append("planning")
            elif "creative" in trait_lower:
                insights["comfort_zones"].append("creative expression")
                insights["coping_strategies"].append("artistic activities")

        # Analyze fears and anxieties
        for fear in background.fears_and_anxieties:
            fear_lower = fear.lower()
            if "social" in fear_lower:
                insights["primary_concerns"].append("social anxiety")
            elif "failure" in fear_lower:
                insights["primary_concerns"].append("fear of failure")
            elif "abandonment" in fear_lower:
                insights["primary_concerns"].append("attachment issues")

        # Analyze core values for comfort zones
        for value in background.core_values:
            value_lower = value.lower()
            if "family" in value_lower:
                insights["comfort_zones"].append("family relationships")
            elif "education" in value_lower or "learning" in value_lower:
                insights["comfort_zones"].append("learning and growth")
            elif "nature" in value_lower:
                insights["comfort_zones"].append("nature and outdoors")

        return insights

    def _generate_therapeutic_goals(
        self, character: Character
    ) -> list[TherapeuticGoal]:
        """Generate therapeutic goals based on character data."""
        goals = []

        # Generate goals based on primary concerns
        for concern in character.therapeutic_profile.primary_concerns:
            if concern == "anxiety":
                goal = TherapeuticGoal(
                    goal_id=f"anxiety_management_{character.character_id}",
                    description="Develop effective anxiety management techniques",
                    therapeutic_approaches=[
                        TherapeuticApproach.CBT,
                        TherapeuticApproach.MINDFULNESS,
                    ],
                    milestones=[
                        "Learn breathing techniques",
                        "Practice grounding exercises",
                        "Identify anxiety triggers",
                    ],
                )
                goals.append(goal)
            elif concern == "work stress":
                goal = TherapeuticGoal(
                    goal_id=f"work_stress_{character.character_id}",
                    description="Improve work-life balance and stress management",
                    therapeutic_approaches=[
                        TherapeuticApproach.CBT,
                        TherapeuticApproach.SOLUTION_FOCUSED,
                    ],
                    milestones=[
                        "Set healthy boundaries",
                        "Develop time management skills",
                        "Practice stress reduction",
                    ],
                )
                goals.append(goal)

        # Generate goals based on challenge areas
        for challenge in character.therapeutic_profile.challenge_areas:
            if challenge == "self-acceptance":
                goal = TherapeuticGoal(
                    goal_id=f"self_acceptance_{character.character_id}",
                    description="Develop greater self-acceptance and self-compassion",
                    therapeutic_approaches=[
                        TherapeuticApproach.HUMANISTIC,
                        TherapeuticApproach.MINDFULNESS,
                    ],
                    milestones=[
                        "Practice self-compassion",
                        "Challenge negative self-talk",
                        "Celebrate achievements",
                    ],
                )
                goals.append(goal)

        return goals

    def _extract_life_experiences(self, background: CharacterBackground) -> list[str]:
        """Extract key life experiences from character background."""
        experiences = []

        # Extract from backstory
        if background.backstory:
            backstory_lower = background.backstory.lower()
            if "teacher" in backstory_lower or "education" in backstory_lower:
                experiences.append("educational career")
            if "family" in backstory_lower:
                experiences.append("family-focused life")
            if "stress" in backstory_lower or "pressure" in backstory_lower:
                experiences.append("high-stress environment")

        # Extract from relationships
        for rel_type, description in background.relationships.items():
            if rel_type == "family":
                experiences.append("strong family connections")
            elif rel_type == "professional":
                experiences.append("professional relationships")

        return experiences

    def _calculate_readiness_adjustment(self, background: CharacterBackground) -> float:
        """Calculate adjustment to therapeutic readiness based on character traits."""
        adjustment = 0.0

        # Positive traits that increase readiness
        positive_traits = [
            "empathetic",
            "patient",
            "open-minded",
            "resilient",
            "supportive",
        ]
        for trait in background.personality_traits:
            if any(pos_trait in trait.lower() for pos_trait in positive_traits):
                adjustment += 0.05

        # Traits that might decrease initial readiness
        challenging_traits = ["anxious", "perfectionist", "stubborn", "defensive"]
        for trait in background.personality_traits:
            if any(chal_trait in trait.lower() for chal_trait in challenging_traits):
                adjustment -= 0.03

        # Cap adjustment to reasonable range
        return max(-0.2, min(0.2, adjustment))

    def _recommend_therapeutic_approaches(
        self, character: Character
    ) -> list[PersonalizationRecommendation]:
        """Recommend therapeutic approaches based on character data."""
        recommendations = []

        # Analyze personality traits for approach recommendations
        if any(
            "anxious" in trait.lower()
            for trait in character.background.personality_traits
        ):
            rec = PersonalizationRecommendation(
                character_id=character.character_id,
                recommendation_type="therapeutic_approach",
                title="Cognitive Behavioral Therapy (CBT)",
                description="CBT is highly effective for anxiety management",
                rationale="Character shows anxiety-related traits that respond well to CBT techniques",
                priority=1,
                confidence_score=0.8,
            )
            recommendations.append(rec)

        if any(
            "creative" in trait.lower()
            for trait in character.background.personality_traits
        ):
            rec = PersonalizationRecommendation(
                character_id=character.character_id,
                recommendation_type="therapeutic_approach",
                title="Narrative Therapy",
                description="Use storytelling and creative expression in therapy",
                rationale="Character's creative traits suggest narrative approaches would be engaging",
                priority=2,
                confidence_score=0.7,
            )
            recommendations.append(rec)

        return recommendations

    def _recommend_content_focus(
        self, character: Character
    ) -> list[PersonalizationRecommendation]:
        """Recommend content focus areas based on character data."""
        recommendations = []

        # Focus on comfort zones for initial engagement
        for comfort_zone in character.therapeutic_profile.comfort_zones:
            if comfort_zone == "nature":
                rec = PersonalizationRecommendation(
                    character_id=character.character_id,
                    recommendation_type="content_focus",
                    title="Nature-Based Therapeutic Content",
                    description="Incorporate nature themes and outdoor settings",
                    rationale="Character finds comfort in nature-related content",
                    priority=2,
                    confidence_score=0.6,
                )
                recommendations.append(rec)

        return recommendations

    def _recommend_intensity_adjustments(
        self, character: Character
    ) -> list[PersonalizationRecommendation]:
        """Recommend intensity adjustments based on character readiness."""
        recommendations = []

        if character.therapeutic_profile.readiness_level < 0.4:
            rec = PersonalizationRecommendation(
                character_id=character.character_id,
                recommendation_type="intensity_adjustment",
                title="Start with Low Intensity",
                description="Begin with gentle, low-intensity therapeutic content",
                rationale="Character's readiness level suggests starting slowly",
                priority=1,
                confidence_score=0.9,
            )
            recommendations.append(rec)
        elif character.therapeutic_profile.readiness_level > 0.8:
            rec = PersonalizationRecommendation(
                character_id=character.character_id,
                recommendation_type="intensity_adjustment",
                title="Use Higher Intensity Content",
                description="Character is ready for more challenging therapeutic work",
                rationale="High readiness level indicates capacity for intensive work",
                priority=2,
                confidence_score=0.8,
            )
            recommendations.append(rec)

        return recommendations

    def _determine_adaptation_strategy(
        self, character: Character, content_type: str
    ) -> dict[str, Any]:
        """Determine how to adapt content for a character."""
        strategy = {
            "type": "general_adaptation",
            "reasoning": "Standard adaptation based on character profile",
            "confidence": 0.5,
        }

        # Adapt based on preferred intensity
        if character.therapeutic_profile.preferred_intensity == IntensityLevel.LOW:
            strategy.update(
                {
                    "type": "gentle_adaptation",
                    "reasoning": "Character prefers low-intensity therapeutic content",
                    "confidence": 0.7,
                    "tone": "gentle",
                    "pacing": "slow",
                }
            )
        elif character.therapeutic_profile.preferred_intensity == IntensityLevel.HIGH:
            strategy.update(
                {
                    "type": "intensive_adaptation",
                    "reasoning": "Character is ready for high-intensity therapeutic work",
                    "confidence": 0.8,
                    "tone": "direct",
                    "pacing": "fast",
                }
            )

        # Adapt based on personality traits
        if any(
            "anxious" in trait.lower()
            for trait in character.background.personality_traits
        ):
            strategy.update(
                {
                    "type": "anxiety_aware_adaptation",
                    "reasoning": "Character shows anxiety traits, content adapted to be reassuring",
                    "confidence": 0.8,
                    "tone": "reassuring",
                    "avoid_triggers": True,
                }
            )

        return strategy

    def _apply_content_adaptations(
        self, content: str, strategy: dict[str, Any], context: PersonalizationContext
    ) -> str:
        """Apply adaptations to content based on strategy and context."""
        adapted_content = content

        # Apply tone adaptations
        tone = strategy.get("tone", "neutral")
        if tone == "gentle":
            adapted_content = f"[Gentle tone] {adapted_content}"
        elif tone == "reassuring":
            adapted_content = f"[Reassuring tone] {adapted_content}"
        elif tone == "direct":
            adapted_content = f"[Direct tone] {adapted_content}"

        # Apply personalization based on character name and traits
        if context.character_name:
            adapted_content = adapted_content.replace(
                "[CHARACTER_NAME]", context.character_name
            )

        # Add comfort zone references if appropriate
        if context.comfort_zones and "nature" in context.comfort_zones:
            adapted_content += " [Consider incorporating nature imagery]"

        return adapted_content
