"""

# Logseq: [[TTA.dev/Tests/Test_character_avatar_manager]]
Unit tests for CharacterAvatarManager.
"""

import unittest
from datetime import datetime
from unittest.mock import patch

import pytest

from src.player_experience.database.character_repository import CharacterRepository
from src.player_experience.managers.character_avatar_manager import (
    CharacterAvatarManager,
    CharacterLimitExceededError,
    CharacterNotFoundError,
)
from src.player_experience.models.character import (
    CharacterAppearance,
    CharacterBackground,
    CharacterCreationData,
    CharacterUpdates,
    TherapeuticProfile,
)
from src.player_experience.models.enums import IntensityLevel


class TestCharacterAvatarManager(unittest.TestCase):
    """Test CharacterAvatarManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.repository = CharacterRepository()
        self.manager = CharacterAvatarManager(self.repository)
        self.player_id = "test_player_123"

        # Create test character data
        self.test_appearance = CharacterAppearance(
            age_range="adult",
            gender_identity="female",
            physical_description="Tall with brown hair",
            clothing_style="professional",
        )

        self.test_background = CharacterBackground(
            name="Alice Johnson",
            backstory="A dedicated teacher seeking work-life balance",
            personality_traits=["empathetic", "organized", "patient"],
            core_values=["education", "family", "integrity"],
        )

        self.test_therapeutic_profile = TherapeuticProfile(
            primary_concerns=["work stress", "anxiety"],
            preferred_intensity=IntensityLevel.MEDIUM,
            comfort_zones=["nature", "creativity"],
            readiness_level=0.7,
        )

        self.test_character_data = CharacterCreationData(
            name="Alice Johnson",
            appearance=self.test_appearance,
            background=self.test_background,
            therapeutic_profile=self.test_therapeutic_profile,
        )

    def test_create_character_success(self):
        """Test successful character creation."""
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        assert character.character_id is not None
        assert character.player_id == self.player_id
        assert character.name == "Alice Johnson"
        assert character.appearance == self.test_appearance
        assert character.background == self.test_background
        assert character.therapeutic_profile == self.test_therapeutic_profile
        assert character.is_active
        assert isinstance(character.created_at, datetime)
        assert isinstance(character.last_active, datetime)

    def test_create_character_limit_exceeded(self):
        """Test character creation when limit is exceeded."""
        # Create maximum number of characters
        character_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        for i in range(CharacterAvatarManager.MAX_CHARACTERS_PER_PLAYER):
            character_name = character_names[i]
            character_data = CharacterCreationData(
                name=character_name,
                appearance=self.test_appearance,
                background=CharacterBackground(name=character_name),
                therapeutic_profile=self.test_therapeutic_profile,
            )
            self.manager.create_character(self.player_id, character_data)

        # Try to create one more - should fail
        with pytest.raises(CharacterLimitExceededError):
            self.manager.create_character(self.player_id, self.test_character_data)

    def test_create_character_invalid_data(self):
        """Test character creation with invalid data."""
        # Test empty name - should fail at CharacterBackground level
        with pytest.raises(ValueError):
            CharacterBackground(name="")

        # Test name too long - should fail at CharacterBackground level
        long_name = "A" * 60
        with pytest.raises(ValueError):
            CharacterBackground(name=long_name)

        # Test invalid characters in name - should fail at CharacterBackground level
        with pytest.raises(ValueError):
            CharacterBackground(name="Alice123")

        # Test mismatched names at manager level
        invalid_data = CharacterCreationData(
            name="Alice",
            appearance=self.test_appearance,
            background=CharacterBackground(name="Bob"),
            therapeutic_profile=self.test_therapeutic_profile,
        )

        with pytest.raises(ValueError):
            self.manager.create_character(self.player_id, invalid_data)

        # Test invalid therapeutic readiness level - should fail at TherapeuticProfile level
        with pytest.raises(ValueError):
            TherapeuticProfile(readiness_level=1.5)  # Out of range

    def test_get_character(self):
        """Test getting a character by ID."""
        # Create character
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Get character
        retrieved = self.manager.get_character(character.character_id)
        assert retrieved is not None
        assert retrieved.character_id == character.character_id
        assert retrieved.name == character.name

        # Test non-existent character
        non_existent = self.manager.get_character("non_existent_id")
        assert non_existent is None

    def test_get_player_characters(self):
        """Test getting all characters for a player."""
        # Initially no characters
        characters = self.manager.get_player_characters(self.player_id)
        assert len(characters) == 0

        # Create multiple characters
        char1 = self.manager.create_character(self.player_id, self.test_character_data)

        char2_data = CharacterCreationData(
            name="Bob Smith",
            appearance=self.test_appearance,
            background=CharacterBackground(name="Bob Smith"),
            therapeutic_profile=self.test_therapeutic_profile,
        )
        char2 = self.manager.create_character(self.player_id, char2_data)

        # Get all characters
        characters = self.manager.get_player_characters(self.player_id)
        assert len(characters) == 2

        character_ids = [char.character_id for char in characters]
        assert char1.character_id in character_ids
        assert char2.character_id in character_ids

    def test_update_character(self):
        """Test updating a character."""
        # Create character
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Create updates
        new_appearance = CharacterAppearance(
            age_range="adult",
            gender_identity="female",
            physical_description="Short with blonde hair",
            clothing_style="casual",
        )

        new_background = CharacterBackground(
            name="Alice Johnson",  # Keep same name
            backstory="Updated backstory",
            personality_traits=["creative", "adventurous"],
        )

        updates = CharacterUpdates(appearance=new_appearance, background=new_background)

        # Update character
        updated = self.manager.update_character(character.character_id, updates)

        assert updated.appearance == new_appearance
        assert updated.background == new_background
        assert updated.background.backstory == "Updated backstory"

        # Test updating non-existent character
        with pytest.raises(CharacterNotFoundError):
            self.manager.update_character("non_existent_id", updates)

    def test_delete_character(self):
        """Test deleting a character."""
        # Create character
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Delete character
        result = self.manager.delete_character(character.character_id)
        assert result

        # Character should no longer be retrievable
        retrieved = self.manager.get_character(character.character_id)
        assert retrieved is None

        # Should not appear in player's character list
        characters = self.manager.get_player_characters(self.player_id)
        assert len(characters) == 0

        # Test deleting non-existent character
        result = self.manager.delete_character("non_existent_id")
        assert not result

    def test_get_character_therapeutic_profile(self):
        """Test getting character therapeutic profile."""
        # Create character
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Get therapeutic profile
        profile = self.manager.get_character_therapeutic_profile(character.character_id)
        assert profile is not None
        assert profile.primary_concerns == ["work stress", "anxiety"]
        assert profile.preferred_intensity == IntensityLevel.MEDIUM

        # Test non-existent character
        profile = self.manager.get_character_therapeutic_profile("non_existent_id")
        assert profile is None

    def test_update_character_therapeutic_profile(self):
        """Test updating character therapeutic profile."""
        # Create character
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Create new therapeutic profile
        new_profile = TherapeuticProfile(
            primary_concerns=["relationship issues", "self-esteem"],
            preferred_intensity=IntensityLevel.HIGH,
            comfort_zones=["music", "art"],
            readiness_level=0.9,
        )

        # Update therapeutic profile
        result = self.manager.update_character_therapeutic_profile(
            character.character_id, new_profile
        )
        assert result

        # Verify update
        updated_profile = self.manager.get_character_therapeutic_profile(
            character.character_id
        )
        assert updated_profile.primary_concerns == [
            "relationship issues",
            "self-esteem",
        ]
        assert updated_profile.preferred_intensity == IntensityLevel.HIGH
        assert updated_profile.readiness_level == 0.9

        # Test updating non-existent character
        result = self.manager.update_character_therapeutic_profile(
            "non_existent_id", new_profile
        )
        assert not result

    def test_get_character_statistics(self):
        """Test getting character statistics."""
        # Create character
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Get statistics
        stats = self.manager.get_character_statistics(character.character_id)
        assert stats is not None

        expected_keys = [
            "character_id",
            "name",
            "created_at",
            "last_active",
            "total_session_time",
            "session_count",
            "active_worlds",
            "therapeutic_readiness",
            "active_therapeutic_goals",
            "is_active",
        ]

        for key in expected_keys:
            assert key in stats

        assert stats["character_id"] == character.character_id
        assert stats["name"] == character.name
        assert stats["total_session_time"] == 0
        assert stats["session_count"] == 0
        assert stats["active_worlds"] == 0
        # Therapeutic readiness may be adjusted by the integration service
        assert stats["therapeutic_readiness"] >= 0.6
        assert stats["therapeutic_readiness"] <= 1.0
        assert stats["is_active"]

        # Test non-existent character
        stats = self.manager.get_character_statistics("non_existent_id")
        assert stats is None

    def test_extract_personality_traits(self):
        """Test personality trait extraction from character data."""
        # Test with various personality traits
        background = CharacterBackground(
            name="Test Character",
            personality_traits=[
                "empathetic",
                "patient",
                "organized",
                "outgoing",
                "anxious",
            ],
        )

        therapeutic_profile = TherapeuticProfile(
            preferred_intensity=IntensityLevel.HIGH
        )

        character_data = CharacterCreationData(
            name="Test Character",
            appearance=self.test_appearance,
            background=background,
            therapeutic_profile=therapeutic_profile,
        )

        traits = self.manager._extract_personality_traits(character_data)

        # Check that traits are extracted correctly
        assert "empathy" in traits
        assert "patience" in traits
        assert "conscientiousness" in traits
        assert "extraversion" in traits
        assert "neuroticism" in traits
        assert "openness" in traits  # From high intensity preference

        # Check that all values are in valid range
        for value in traits.values():
            assert value >= -1.0
            assert value <= 1.0


class TestCharacterAvatarManagerIntegration(unittest.TestCase):
    """Integration tests for CharacterAvatarManager with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.repository = CharacterRepository()

        # Mock the TTA components
        with (
            patch(
                "src.player_experience.managers.character_avatar_manager.CharacterDevelopmentSystem"
            ) as mock_cds,
            patch(
                "src.player_experience.managers.character_avatar_manager.PersonalizationEngine"
            ) as mock_pe,
        ):
            self.mock_cds = mock_cds.return_value
            self.mock_pe = mock_pe.return_value
            self.manager = CharacterAvatarManager(self.repository)

        self.player_id = "test_player_123"

        # Create test data
        self.test_character_data = CharacterCreationData(
            name="Test Character",
            appearance=CharacterAppearance(age_range="adult"),
            background=CharacterBackground(name="Test Character"),
            therapeutic_profile=TherapeuticProfile(),
        )

    def test_create_character_calls_development_system(self):
        """Test that character creation calls the development system."""
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Verify that the development system was called
        self.mock_cds.initialize_character.assert_called_once()
        call_args = self.mock_cds.initialize_character.call_args
        assert (
            call_args[0][0] == character.character_id
        )  # First positional arg is character_id

    def test_create_character_calls_personalization_engine(self):
        """Test that character creation calls the personalization engine."""
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Verify that the personalization engine was called
        self.mock_pe.create_personalization_profile.assert_called_once()
        call_args = self.mock_pe.create_personalization_profile.call_args
        assert (
            call_args[0][0] == character.character_id
        )  # First positional arg is character_id

    def test_update_character_calls_personalization_engine(self):
        """Test that character update calls the personalization engine."""
        # Create character
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Reset mock to clear creation calls
        self.mock_pe.reset_mock()

        # Update character with new therapeutic profile
        new_profile = TherapeuticProfile(
            primary_concerns=["test concern"], preferred_intensity=IntensityLevel.HIGH
        )

        updates = CharacterUpdates(therapeutic_profile=new_profile)
        self.manager.update_character(character.character_id, updates)

        # Verify that the personalization engine was called for update
        self.mock_pe.update_personalization_profile.assert_called_once()

    def test_get_character_personalization_recommendations(self):
        """Test getting personalization recommendations for a character."""
        # Create character
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Get recommendations
        recommendations = self.manager.get_character_personalization_recommendations(
            character.character_id
        )

        # Should return list of recommendation dictionaries
        assert isinstance(recommendations, list)

        # If there are recommendations, check structure
        if recommendations:
            for rec in recommendations:
                assert "recommendation_id" in rec
                assert "type" in rec
                assert "title" in rec
                assert "description" in rec
                assert "rationale" in rec
                assert "priority" in rec
                assert "confidence_score" in rec
                assert "created_at" in rec

    def test_adapt_therapeutic_content_for_character(self):
        """Test adapting therapeutic content for a character."""
        # Create character
        character = self.manager.create_character(
            self.player_id, self.test_character_data
        )

        # Adapt content
        content = "Let's work on your stress management, [CHARACTER_NAME]."
        adaptation = self.manager.adapt_therapeutic_content_for_character(
            character.character_id, content, "dialogue"
        )

        # Should return adaptation dictionary
        assert adaptation is not None
        assert "adaptation_id" in adaptation
        assert "original_content" in adaptation
        assert "adapted_content" in adaptation
        assert "adaptation_type" in adaptation
        assert "reasoning" in adaptation
        assert "effectiveness_score" in adaptation
        assert "created_at" in adaptation

        # Should replace character name
        assert "Test Character" in adaptation["adapted_content"]

        # Test with non-existent character
        result = self.manager.adapt_therapeutic_content_for_character(
            "non_existent_id", content
        )
        assert result is None


if __name__ == "__main__":
    unittest.main()
