import pytest
"""

# Logseq: [[TTA.dev/Tests/Test_therapeutic_profile_integration]]
Unit tests for TherapeuticProfileIntegrationService.
"""

import unittest
from datetime import datetime

from src.player_experience.managers.therapeutic_profile_integration import (
    TherapeuticProfileIntegrationService,
)
from src.player_experience.models.character import (
    Character,
    CharacterAppearance,
    CharacterBackground,
    TherapeuticProfile,
)
from src.player_experience.models.enums import IntensityLevel

pytestmark = pytest.mark.unit


class TestTherapeuticProfileIntegrationService(unittest.TestCase):
    """Test TherapeuticProfileIntegrationService functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = TherapeuticProfileIntegrationService()

        # Create test character
        self.test_appearance = CharacterAppearance(age_range="adult")

        self.test_background = CharacterBackground(
            name="Alice Johnson",
            backstory="A dedicated teacher experiencing work stress and seeking better work-life balance",
            personality_traits=["empathetic", "organized", "anxious", "perfectionist"],
            core_values=["education", "family", "integrity"],
            fears_and_anxieties=["failure", "social judgment"],
            strengths_and_skills=["teaching", "communication", "problem-solving"],
            relationships={
                "family": "close-knit family",
                "professional": "supportive colleagues",
            },
        )

        self.test_therapeutic_profile = TherapeuticProfile(
            primary_concerns=["work stress"],
            preferred_intensity=IntensityLevel.MEDIUM,
            comfort_zones=["nature", "learning"],
            challenge_areas=["perfectionism"],
            trigger_topics=["criticism"],
            readiness_level=0.6,
        )

        self.test_character = Character(
            character_id="test_char_123",
            player_id="test_player_123",
            name="Alice Johnson",
            appearance=self.test_appearance,
            background=self.test_background,
            therapeutic_profile=self.test_therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

    def test_create_therapeutic_profile_from_character(self):
        """Test creating enhanced therapeutic profile from character data."""
        enhanced_profile = self.service.create_therapeutic_profile_from_character(
            self.test_character
        )

        # Should have original concerns plus extracted ones
        assert "work stress" in enhanced_profile.primary_concerns
        assert "anxiety" in enhanced_profile.primary_concerns  # From anxious trait
        assert (
            "perfectionism" in enhanced_profile.primary_concerns
        )  # From perfectionist trait

        # Should have comfort zones from values and traits
        assert "nature" in enhanced_profile.comfort_zones
        assert "learning" in enhanced_profile.comfort_zones
        assert (
            "learning and growth" in enhanced_profile.comfort_zones
        )  # From education value

        # Should have challenge areas
        assert "perfectionism" in enhanced_profile.challenge_areas
        assert (
            "stress management" in enhanced_profile.challenge_areas
        )  # From anxious trait

        # Should have coping strategies
        assert (
            "social support" in enhanced_profile.coping_strategies
        )  # From empathetic trait
        assert "planning" in enhanced_profile.coping_strategies  # From organized trait

        # Should have generated therapeutic goals
        assert len(enhanced_profile.therapeutic_goals) > 0

        # Check for specific generated goals
        goal_descriptions = [
            goal.description for goal in enhanced_profile.therapeutic_goals
        ]
        assert any("anxiety" in desc.lower() for desc in goal_descriptions)
        assert any("work" in desc.lower() for desc in goal_descriptions)

    def test_create_personalization_context(self):
        """Test creating personalization context for a character."""
        context = self.service.create_personalization_context(self.test_character)

        assert context.character_id == self.test_character.character_id
        assert context.character_name == self.test_character.name
        assert (
            context.personality_traits
            == self.test_character.background.personality_traits
        )
        assert context.core_values == self.test_character.background.core_values
        assert (
            context.preferred_intensity
            == self.test_character.therapeutic_profile.preferred_intensity
        )
        assert (
            context.readiness_level
            == self.test_character.therapeutic_profile.readiness_level
        )

        # Should extract life experiences
        assert len(context.life_experiences) > 0
        assert any("educational" in exp.lower() for exp in context.life_experiences)

        # Should be stored in service
        assert self.test_character.character_id in self.service.personalization_contexts

    def test_generate_personalization_recommendations(self):
        """Test generating personalization recommendations."""
        recommendations = self.service.generate_personalization_recommendations(
            self.test_character
        )

        assert len(recommendations) > 0

        # Should have recommendations for different types
        rec_types = [rec.recommendation_type for rec in recommendations]
        assert "therapeutic_approach" in rec_types

        # Should recommend CBT for anxiety
        cbt_recs = [
            rec
            for rec in recommendations
            if "CBT" in rec.title or "Cognitive" in rec.title
        ]
        assert len(cbt_recs) > 0

        # Should have proper structure
        for rec in recommendations:
            assert rec.recommendation_id is not None
            assert rec.character_id == self.test_character.character_id
            assert rec.title is not None
            assert rec.description is not None
            assert rec.rationale is not None
            assert rec.priority >= 1
            assert rec.priority <= 5
            assert rec.confidence_score >= 0.0
            assert rec.confidence_score <= 1.0

        # Should be stored in service
        assert self.test_character.character_id in self.service.recommendations

    def test_adapt_therapeutic_content(self):
        """Test adapting therapeutic content for a character."""
        original_content = (
            "Let's work on managing your stress levels, [CHARACTER_NAME]."
        )

        adaptation = self.service.adapt_therapeutic_content(
            self.test_character, original_content, "dialogue"
        )

        assert adaptation.adaptation_id is not None
        assert adaptation.character_id == self.test_character.character_id
        assert adaptation.original_content == original_content
        assert adaptation.adapted_content != original_content
        assert adaptation.reasoning is not None
        assert adaptation.effectiveness_score >= 0.0
        assert adaptation.effectiveness_score <= 1.0

        # Should replace character name
        assert "Alice Johnson" in adaptation.adapted_content

        # Should be stored in service
        assert self.test_character.character_id in self.service.adaptations
        adaptations = self.service.adaptations[self.test_character.character_id]
        assert adaptation in adaptations

    def test_adapt_content_for_anxious_character(self):
        """Test content adaptation for character with anxiety traits."""
        # Create character with high anxiety
        anxious_background = CharacterBackground(
            name="Bob Smith", personality_traits=["anxious", "worried", "sensitive"]
        )
        anxious_profile = TherapeuticProfile(preferred_intensity=IntensityLevel.LOW)
        anxious_character = Character(
            character_id="anxious_char",
            player_id="test_player",
            name="Bob Smith",
            appearance=self.test_appearance,
            background=anxious_background,
            therapeutic_profile=anxious_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        content = "We need to address your problems directly."
        adaptation = self.service.adapt_therapeutic_content(anxious_character, content)

        # Should use anxiety-aware adaptation
        assert adaptation.adaptation_type == "anxiety_aware_adaptation"
        assert "anxiety" in adaptation.reasoning.lower()
        assert "reassuring" in adaptation.adapted_content.lower()

    def test_adapt_content_for_high_intensity_character(self):
        """Test content adaptation for character preferring high intensity."""
        # Create character with high intensity preference
        high_intensity_profile = TherapeuticProfile(
            preferred_intensity=IntensityLevel.HIGH
        )
        high_intensity_character = Character(
            character_id="high_intensity_char",
            player_id="test_player",
            name="Charlie Brown",
            appearance=self.test_appearance,
            background=CharacterBackground(name="Charlie Brown"),
            therapeutic_profile=high_intensity_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        content = "Let's explore your feelings."
        adaptation = self.service.adapt_therapeutic_content(
            high_intensity_character, content
        )

        # Should use intensive adaptation
        assert adaptation.adaptation_type == "intensive_adaptation"
        assert "high-intensity" in adaptation.reasoning.lower()
        assert "direct" in adaptation.adapted_content.lower()

    def test_get_character_adaptations(self):
        """Test getting adaptations for a character."""
        # Initially no adaptations
        adaptations = self.service.get_character_adaptations(
            self.test_character.character_id
        )
        assert len(adaptations) == 0

        # Create some adaptations
        self.service.adapt_therapeutic_content(self.test_character, "Content 1")
        self.service.adapt_therapeutic_content(self.test_character, "Content 2")

        # Should return all adaptations
        adaptations = self.service.get_character_adaptations(
            self.test_character.character_id
        )
        assert len(adaptations) == 2

    def test_get_character_recommendations(self):
        """Test getting recommendations for a character."""
        # Initially no recommendations
        recommendations = self.service.get_character_recommendations(
            self.test_character.character_id
        )
        assert len(recommendations) == 0

        # Generate recommendations
        self.service.generate_personalization_recommendations(self.test_character)

        # Should return all recommendations
        recommendations = self.service.get_character_recommendations(
            self.test_character.character_id
        )
        assert len(recommendations) > 0

    def test_update_adaptation_effectiveness(self):
        """Test updating adaptation effectiveness score."""
        # Create adaptation
        adaptation = self.service.adapt_therapeutic_content(
            self.test_character, "Test content"
        )
        original_score = adaptation.effectiveness_score

        # Update effectiveness
        new_score = 0.9
        result = self.service.update_adaptation_effectiveness(
            adaptation.adaptation_id, new_score
        )

        assert result
        assert adaptation.effectiveness_score == new_score
        assert adaptation.effectiveness_score != original_score

        # Test updating non-existent adaptation
        result = self.service.update_adaptation_effectiveness("non_existent_id", 0.5)
        assert not result

        # Test score clamping
        self.service.update_adaptation_effectiveness(
            adaptation.adaptation_id, 1.5
        )  # Too high
        assert adaptation.effectiveness_score == 1.0

        self.service.update_adaptation_effectiveness(
            adaptation.adaptation_id, -0.5
        )  # Too low
        assert adaptation.effectiveness_score == 0.0

    def test_extract_therapeutic_insights(self):
        """Test extracting therapeutic insights from character background."""
        insights = self.service._extract_therapeutic_insights(self.test_background)

        # Should extract anxiety from anxious trait
        assert "anxiety" in insights["primary_concerns"]

        # Should extract perfectionism from perfectionist trait
        assert "perfectionism" in insights["primary_concerns"]

        # Should extract comfort zones from empathetic trait
        assert "helping others" in insights["comfort_zones"]

        # Should extract coping strategies from organized trait
        assert "planning" in insights["coping_strategies"]

        # Should extract comfort zones from core values
        assert (
            "learning and growth" in insights["comfort_zones"]
        )  # From education value

    def test_generate_therapeutic_goals(self):
        """Test generating therapeutic goals from character data."""
        # First test the enhanced profile creation which should add anxiety to primary concerns
        enhanced_profile = self.service.create_therapeutic_profile_from_character(
            self.test_character
        )

        # Create a character with the enhanced profile
        enhanced_character = Character(
            character_id=self.test_character.character_id,
            player_id=self.test_character.player_id,
            name=self.test_character.name,
            appearance=self.test_character.appearance,
            background=self.test_character.background,
            therapeutic_profile=enhanced_profile,
            created_at=self.test_character.created_at,
            last_active=self.test_character.last_active,
        )

        goals = self.service._generate_therapeutic_goals(enhanced_character)

        assert len(goals) > 0

        # Should generate anxiety management goal (from extracted anxiety concern)
        anxiety_goals = [
            goal for goal in goals if "anxiety" in goal.description.lower()
        ]
        assert len(anxiety_goals) > 0

        # Should generate work stress goal (from original concern)
        work_goals = [goal for goal in goals if "work" in goal.description.lower()]
        assert len(work_goals) > 0

        # Goals should have proper structure
        for goal in goals:
            assert goal.goal_id is not None
            assert goal.description is not None
            assert len(goal.therapeutic_approaches) > 0
            assert len(goal.milestones) > 0
            assert goal.is_active

    def test_calculate_readiness_adjustment(self):
        """Test calculating readiness adjustment based on character traits."""
        # Test positive traits
        positive_background = CharacterBackground(
            name="Positive Person",
            personality_traits=["empathetic", "patient", "resilient"],
        )
        adjustment = self.service._calculate_readiness_adjustment(positive_background)
        assert adjustment > 0

        # Test challenging traits
        challenging_background = CharacterBackground(
            name="Challenging Person",
            personality_traits=["anxious", "perfectionist", "defensive"],
        )
        adjustment = self.service._calculate_readiness_adjustment(
            challenging_background
        )
        assert adjustment < 0

        # Test mixed traits
        mixed_background = CharacterBackground(
            name="Mixed Person",
            personality_traits=["empathetic", "anxious", "patient", "perfectionist"],
        )
        adjustment = self.service._calculate_readiness_adjustment(mixed_background)
        # Should be close to neutral due to mixed traits
        assert adjustment >= -0.2
        assert adjustment <= 0.2

    def test_recommend_therapeutic_approaches(self):
        """Test recommending therapeutic approaches."""
        recommendations = self.service._recommend_therapeutic_approaches(
            self.test_character
        )

        # Should recommend CBT for anxious character
        cbt_recs = [rec for rec in recommendations if "CBT" in rec.title]
        assert len(cbt_recs) > 0

        # Test creative character
        creative_background = CharacterBackground(
            name="Creative Person", personality_traits=["creative", "artistic"]
        )
        creative_character = Character(
            character_id="creative_char",
            player_id="test_player",
            name="Creative Person",
            appearance=self.test_appearance,
            background=creative_background,
            therapeutic_profile=TherapeuticProfile(),
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        creative_recs = self.service._recommend_therapeutic_approaches(
            creative_character
        )
        narrative_recs = [rec for rec in creative_recs if "Narrative" in rec.title]
        assert len(narrative_recs) > 0

    def test_recommend_intensity_adjustments(self):
        """Test recommending intensity adjustments."""
        # Test low readiness character
        low_readiness_profile = TherapeuticProfile(readiness_level=0.3)
        low_readiness_character = Character(
            character_id="low_readiness_char",
            player_id="test_player",
            name="Low Readiness",
            appearance=self.test_appearance,
            background=CharacterBackground(name="Low Readiness"),
            therapeutic_profile=low_readiness_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        recommendations = self.service._recommend_intensity_adjustments(
            low_readiness_character
        )
        low_intensity_recs = [
            rec for rec in recommendations if "Low Intensity" in rec.title
        ]
        assert len(low_intensity_recs) > 0

        # Test high readiness character
        high_readiness_profile = TherapeuticProfile(readiness_level=0.9)
        high_readiness_character = Character(
            character_id="high_readiness_char",
            player_id="test_player",
            name="High Readiness",
            appearance=self.test_appearance,
            background=CharacterBackground(name="High Readiness"),
            therapeutic_profile=high_readiness_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        recommendations = self.service._recommend_intensity_adjustments(
            high_readiness_character
        )
        high_intensity_recs = [
            rec for rec in recommendations if "Higher Intensity" in rec.title
        ]
        assert len(high_intensity_recs) > 0


if __name__ == "__main__":
    unittest.main()
