"""
Unit tests for CharacterAvatarManager.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from src.player_experience.managers.character_avatar_manager import (
    CharacterAvatarManager, CharacterLimitExceededError, CharacterNotFoundError
)
from src.player_experience.models.character import (
    Character, CharacterCreationData, CharacterUpdates, CharacterAppearance,
    CharacterBackground, TherapeuticProfile, TherapeuticGoal
)
from src.player_experience.models.enums import IntensityLevel, TherapeuticApproach
from src.player_experience.database.character_repository import CharacterRepository


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
            clothing_style="professional"
        )
        
        self.test_background = CharacterBackground(
            name="Alice Johnson",
            backstory="A dedicated teacher seeking work-life balance",
            personality_traits=["empathetic", "organized", "patient"],
            core_values=["education", "family", "integrity"]
        )
        
        self.test_therapeutic_profile = TherapeuticProfile(
            primary_concerns=["work stress", "anxiety"],
            preferred_intensity=IntensityLevel.MEDIUM,
            comfort_zones=["nature", "creativity"],
            readiness_level=0.7
        )
        
        self.test_character_data = CharacterCreationData(
            name="Alice Johnson",
            appearance=self.test_appearance,
            background=self.test_background,
            therapeutic_profile=self.test_therapeutic_profile
        )
    
    def test_create_character_success(self):
        """Test successful character creation."""
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        self.assertIsNotNone(character.character_id)
        self.assertEqual(character.player_id, self.player_id)
        self.assertEqual(character.name, "Alice Johnson")
        self.assertEqual(character.appearance, self.test_appearance)
        self.assertEqual(character.background, self.test_background)
        self.assertEqual(character.therapeutic_profile, self.test_therapeutic_profile)
        self.assertTrue(character.is_active)
        self.assertIsInstance(character.created_at, datetime)
        self.assertIsInstance(character.last_active, datetime)
    
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
                therapeutic_profile=self.test_therapeutic_profile
            )
            self.manager.create_character(self.player_id, character_data)
        
        # Try to create one more - should fail
        with self.assertRaises(CharacterLimitExceededError):
            self.manager.create_character(self.player_id, self.test_character_data)
    
    def test_create_character_invalid_data(self):
        """Test character creation with invalid data."""
        # Test empty name - should fail at CharacterBackground level
        with self.assertRaises(ValueError):
            CharacterBackground(name="")
        
        # Test name too long - should fail at CharacterBackground level
        long_name = "A" * 60
        with self.assertRaises(ValueError):
            CharacterBackground(name=long_name)
        
        # Test invalid characters in name - should fail at CharacterBackground level
        with self.assertRaises(ValueError):
            CharacterBackground(name="Alice123")
        
        # Test mismatched names at manager level
        invalid_data = CharacterCreationData(
            name="Alice",
            appearance=self.test_appearance,
            background=CharacterBackground(name="Bob"),
            therapeutic_profile=self.test_therapeutic_profile
        )
        
        with self.assertRaises(ValueError):
            self.manager.create_character(self.player_id, invalid_data)
        
        # Test invalid therapeutic readiness level - should fail at TherapeuticProfile level
        with self.assertRaises(ValueError):
            TherapeuticProfile(readiness_level=1.5)  # Out of range
    
    def test_get_character(self):
        """Test getting a character by ID."""
        # Create character
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Get character
        retrieved = self.manager.get_character(character.character_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.character_id, character.character_id)
        self.assertEqual(retrieved.name, character.name)
        
        # Test non-existent character
        non_existent = self.manager.get_character("non_existent_id")
        self.assertIsNone(non_existent)
    
    def test_get_player_characters(self):
        """Test getting all characters for a player."""
        # Initially no characters
        characters = self.manager.get_player_characters(self.player_id)
        self.assertEqual(len(characters), 0)
        
        # Create multiple characters
        char1 = self.manager.create_character(self.player_id, self.test_character_data)
        
        char2_data = CharacterCreationData(
            name="Bob Smith",
            appearance=self.test_appearance,
            background=CharacterBackground(name="Bob Smith"),
            therapeutic_profile=self.test_therapeutic_profile
        )
        char2 = self.manager.create_character(self.player_id, char2_data)
        
        # Get all characters
        characters = self.manager.get_player_characters(self.player_id)
        self.assertEqual(len(characters), 2)
        
        character_ids = [char.character_id for char in characters]
        self.assertIn(char1.character_id, character_ids)
        self.assertIn(char2.character_id, character_ids)
    
    def test_update_character(self):
        """Test updating a character."""
        # Create character
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Create updates
        new_appearance = CharacterAppearance(
            age_range="adult",
            gender_identity="female",
            physical_description="Short with blonde hair",
            clothing_style="casual"
        )
        
        new_background = CharacterBackground(
            name="Alice Johnson",  # Keep same name
            backstory="Updated backstory",
            personality_traits=["creative", "adventurous"]
        )
        
        updates = CharacterUpdates(
            appearance=new_appearance,
            background=new_background
        )
        
        # Update character
        updated = self.manager.update_character(character.character_id, updates)
        
        self.assertEqual(updated.appearance, new_appearance)
        self.assertEqual(updated.background, new_background)
        self.assertEqual(updated.background.backstory, "Updated backstory")
        
        # Test updating non-existent character
        with self.assertRaises(CharacterNotFoundError):
            self.manager.update_character("non_existent_id", updates)
    
    def test_delete_character(self):
        """Test deleting a character."""
        # Create character
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Delete character
        result = self.manager.delete_character(character.character_id)
        self.assertTrue(result)
        
        # Character should no longer be retrievable
        retrieved = self.manager.get_character(character.character_id)
        self.assertIsNone(retrieved)
        
        # Should not appear in player's character list
        characters = self.manager.get_player_characters(self.player_id)
        self.assertEqual(len(characters), 0)
        
        # Test deleting non-existent character
        result = self.manager.delete_character("non_existent_id")
        self.assertFalse(result)
    
    def test_get_character_therapeutic_profile(self):
        """Test getting character therapeutic profile."""
        # Create character
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Get therapeutic profile
        profile = self.manager.get_character_therapeutic_profile(character.character_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.primary_concerns, ["work stress", "anxiety"])
        self.assertEqual(profile.preferred_intensity, IntensityLevel.MEDIUM)
        
        # Test non-existent character
        profile = self.manager.get_character_therapeutic_profile("non_existent_id")
        self.assertIsNone(profile)
    
    def test_update_character_therapeutic_profile(self):
        """Test updating character therapeutic profile."""
        # Create character
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Create new therapeutic profile
        new_profile = TherapeuticProfile(
            primary_concerns=["relationship issues", "self-esteem"],
            preferred_intensity=IntensityLevel.HIGH,
            comfort_zones=["music", "art"],
            readiness_level=0.9
        )
        
        # Update therapeutic profile
        result = self.manager.update_character_therapeutic_profile(
            character.character_id, new_profile
        )
        self.assertTrue(result)
        
        # Verify update
        updated_profile = self.manager.get_character_therapeutic_profile(character.character_id)
        self.assertEqual(updated_profile.primary_concerns, ["relationship issues", "self-esteem"])
        self.assertEqual(updated_profile.preferred_intensity, IntensityLevel.HIGH)
        self.assertEqual(updated_profile.readiness_level, 0.9)
        
        # Test updating non-existent character
        result = self.manager.update_character_therapeutic_profile("non_existent_id", new_profile)
        self.assertFalse(result)
    
    def test_get_character_statistics(self):
        """Test getting character statistics."""
        # Create character
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Get statistics
        stats = self.manager.get_character_statistics(character.character_id)
        self.assertIsNotNone(stats)
        
        expected_keys = [
            "character_id", "name", "created_at", "last_active",
            "total_session_time", "session_count", "active_worlds",
            "therapeutic_readiness", "active_therapeutic_goals", "is_active"
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
        
        self.assertEqual(stats["character_id"], character.character_id)
        self.assertEqual(stats["name"], character.name)
        self.assertEqual(stats["total_session_time"], 0)
        self.assertEqual(stats["session_count"], 0)
        self.assertEqual(stats["active_worlds"], 0)
        # Therapeutic readiness may be adjusted by the integration service
        self.assertGreaterEqual(stats["therapeutic_readiness"], 0.6)
        self.assertLessEqual(stats["therapeutic_readiness"], 1.0)
        self.assertTrue(stats["is_active"])
        
        # Test non-existent character
        stats = self.manager.get_character_statistics("non_existent_id")
        self.assertIsNone(stats)
    
    def test_extract_personality_traits(self):
        """Test personality trait extraction from character data."""
        # Test with various personality traits
        background = CharacterBackground(
            name="Test Character",
            personality_traits=["empathetic", "patient", "organized", "outgoing", "anxious"]
        )
        
        therapeutic_profile = TherapeuticProfile(
            preferred_intensity=IntensityLevel.HIGH
        )
        
        character_data = CharacterCreationData(
            name="Test Character",
            appearance=self.test_appearance,
            background=background,
            therapeutic_profile=therapeutic_profile
        )
        
        traits = self.manager._extract_personality_traits(character_data)
        
        # Check that traits are extracted correctly
        self.assertIn("empathy", traits)
        self.assertIn("patience", traits)
        self.assertIn("conscientiousness", traits)
        self.assertIn("extraversion", traits)
        self.assertIn("neuroticism", traits)
        self.assertIn("openness", traits)  # From high intensity preference
        
        # Check that all values are in valid range
        for trait_name, value in traits.items():
            self.assertGreaterEqual(value, -1.0)
            self.assertLessEqual(value, 1.0)


class TestCharacterAvatarManagerIntegration(unittest.TestCase):
    """Integration tests for CharacterAvatarManager with mocked dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repository = CharacterRepository()
        
        # Mock the TTA components
        with patch('src.player_experience.managers.character_avatar_manager.CharacterDevelopmentSystem') as mock_cds, \
             patch('src.player_experience.managers.character_avatar_manager.PersonalizationEngine') as mock_pe:
            
            self.mock_cds = mock_cds.return_value
            self.mock_pe = mock_pe.return_value
            self.manager = CharacterAvatarManager(self.repository)
        
        self.player_id = "test_player_123"
        
        # Create test data
        self.test_character_data = CharacterCreationData(
            name="Test Character",
            appearance=CharacterAppearance(age_range="adult"),
            background=CharacterBackground(name="Test Character"),
            therapeutic_profile=TherapeuticProfile()
        )
    
    def test_create_character_calls_development_system(self):
        """Test that character creation calls the development system."""
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Verify that the development system was called
        self.mock_cds.initialize_character.assert_called_once()
        call_args = self.mock_cds.initialize_character.call_args
        self.assertEqual(call_args[0][0], character.character_id)  # First positional arg is character_id
    
    def test_create_character_calls_personalization_engine(self):
        """Test that character creation calls the personalization engine."""
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Verify that the personalization engine was called
        self.mock_pe.create_personalization_profile.assert_called_once()
        call_args = self.mock_pe.create_personalization_profile.call_args
        self.assertEqual(call_args[0][0], character.character_id)  # First positional arg is character_id
    
    def test_update_character_calls_personalization_engine(self):
        """Test that character update calls the personalization engine."""
        # Create character
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Reset mock to clear creation calls
        self.mock_pe.reset_mock()
        
        # Update character with new therapeutic profile
        new_profile = TherapeuticProfile(
            primary_concerns=["test concern"],
            preferred_intensity=IntensityLevel.HIGH
        )
        
        updates = CharacterUpdates(therapeutic_profile=new_profile)
        self.manager.update_character(character.character_id, updates)
        
        # Verify that the personalization engine was called for update
        self.mock_pe.update_personalization_profile.assert_called_once()
    
    def test_get_character_personalization_recommendations(self):
        """Test getting personalization recommendations for a character."""
        # Create character
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Get recommendations
        recommendations = self.manager.get_character_personalization_recommendations(character.character_id)
        
        # Should return list of recommendation dictionaries
        self.assertIsInstance(recommendations, list)
        
        # If there are recommendations, check structure
        if recommendations:
            for rec in recommendations:
                self.assertIn("recommendation_id", rec)
                self.assertIn("type", rec)
                self.assertIn("title", rec)
                self.assertIn("description", rec)
                self.assertIn("rationale", rec)
                self.assertIn("priority", rec)
                self.assertIn("confidence_score", rec)
                self.assertIn("created_at", rec)
    
    def test_adapt_therapeutic_content_for_character(self):
        """Test adapting therapeutic content for a character."""
        # Create character
        character = self.manager.create_character(self.player_id, self.test_character_data)
        
        # Adapt content
        content = "Let's work on your stress management, [CHARACTER_NAME]."
        adaptation = self.manager.adapt_therapeutic_content_for_character(
            character.character_id, content, "dialogue"
        )
        
        # Should return adaptation dictionary
        self.assertIsNotNone(adaptation)
        self.assertIn("adaptation_id", adaptation)
        self.assertIn("original_content", adaptation)
        self.assertIn("adapted_content", adaptation)
        self.assertIn("adaptation_type", adaptation)
        self.assertIn("reasoning", adaptation)
        self.assertIn("effectiveness_score", adaptation)
        self.assertIn("created_at", adaptation)
        
        # Should replace character name
        self.assertIn("Test Character", adaptation["adapted_content"])
        
        # Test with non-existent character
        result = self.manager.adapt_therapeutic_content_for_character("non_existent_id", content)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()