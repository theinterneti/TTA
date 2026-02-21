"""

# Logseq: [[TTA.dev/Tests/Test_world_management_module]]
Unit tests for WorldManagementModule.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

from src.player_experience.managers.world_management_module import WorldManagementModule
from src.player_experience.models.enums import DifficultyLevel
from src.player_experience.models.world import CompatibilityReport, WorldParameters


class TestWorldManagementModule(unittest.TestCase):
    """Test cases for WorldManagementModule."""

    def setUp(self):
        """Set up test fixtures."""
        self.world_manager = WorldManagementModule()
        self.test_player_id = "test_player_123"
        self.test_character_id = "test_character_456"

    def test_initialization(self):
        """Test WorldManagementModule initialization."""
        # Test basic initialization
        manager = WorldManagementModule()
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager._world_cache), 5)  # Five default worlds

        # Test initialization with external components
        mock_world_state_manager = Mock()
        mock_therapeutic_generator = Mock()

        manager_with_deps = WorldManagementModule(
            world_state_manager=mock_world_state_manager,
            therapeutic_environment_generator=mock_therapeutic_generator,
        )

        self.assertEqual(
            manager_with_deps.world_state_manager, mock_world_state_manager
        )
        self.assertEqual(
            manager_with_deps.therapeutic_environment_generator,
            mock_therapeutic_generator,
        )

    def test_get_available_worlds_without_character(self):
        """Test getting available worlds without character filtering."""
        worlds = self.world_manager.get_available_worlds(self.test_player_id)

        self.assertIsInstance(worlds, list)
        self.assertEqual(len(worlds), 5)  # Five default worlds

        # Check that worlds are sorted by rating (highest first)
        self.assertGreaterEqual(worlds[0].average_rating, worlds[1].average_rating)

        # Verify world summary structure
        world = worlds[0]
        self.assertIsNotNone(world.world_id)
        self.assertIsNotNone(world.name)
        self.assertIsNotNone(world.description)
        self.assertIsInstance(world.therapeutic_themes, list)
        self.assertIsInstance(world.therapeutic_approaches, list)
        self.assertIsInstance(world.difficulty_level, DifficultyLevel)
        self.assertIsInstance(world.estimated_duration, timedelta)
        self.assertEqual(world.compatibility_score, 0.0)  # No character specified

    def test_get_available_worlds_with_character(self):
        """Test getting available worlds with character compatibility filtering."""
        worlds = self.world_manager.get_available_worlds(
            self.test_player_id, self.test_character_id
        )

        self.assertIsInstance(worlds, list)
        self.assertEqual(len(worlds), 5)

        # Check that compatibility scores are calculated
        for world in worlds:
            self.assertGreater(world.compatibility_score, 0.0)
            self.assertLessEqual(world.compatibility_score, 1.0)

        # Check that worlds are sorted by compatibility score
        self.assertGreaterEqual(
            worlds[0].compatibility_score, worlds[1].compatibility_score
        )

    def test_get_world_details_existing_world(self):
        """Test getting details for an existing world."""
        # Get a world ID from available worlds
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        details = self.world_manager.get_world_details(world_id)

        self.assertIsNotNone(details)
        self.assertEqual(details.world_id, world_id)
        self.assertIsNotNone(details.name)
        self.assertIsNotNone(details.description)
        self.assertIsNotNone(details.long_description)
        self.assertIsInstance(details.therapeutic_themes, list)
        self.assertIsInstance(details.therapeutic_approaches, list)
        self.assertIsInstance(details.key_characters, list)
        self.assertIsInstance(details.main_storylines, list)
        self.assertIsInstance(details.therapeutic_techniques_used, list)
        self.assertIsInstance(details.prerequisites, list)
        self.assertIsInstance(details.available_parameters, list)

    def test_get_world_details_nonexistent_world(self):
        """Test getting details for a non-existent world."""
        details = self.world_manager.get_world_details("nonexistent_world")
        self.assertIsNone(details)

    def test_customize_world_parameters_valid(self):
        """Test customizing world parameters with valid parameters."""
        # Get a world ID
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        # Create valid parameters
        parameters = WorldParameters(
            therapeutic_intensity=0.7,
            narrative_pace="medium",
            interaction_frequency="balanced",
            challenge_level=DifficultyLevel.INTERMEDIATE,
            session_length_preference=45,
        )

        customized_world = self.world_manager.customize_world_parameters(
            world_id, parameters
        )

        self.assertIsNotNone(customized_world)
        self.assertEqual(customized_world.world_id, world_id)
        self.assertEqual(customized_world.customized_parameters, parameters)
        self.assertIsInstance(
            customized_world.compatibility_report, CompatibilityReport
        )

    def test_customize_world_parameters_invalid_world(self):
        """Test customizing parameters for a non-existent world."""
        parameters = WorldParameters()
        customized_world = self.world_manager.customize_world_parameters(
            "nonexistent_world", parameters
        )
        self.assertIsNone(customized_world)

    def test_customize_world_parameters_invalid_parameters(self):
        """Test customizing world parameters with invalid parameters."""
        # Test that invalid parameters raise ValueError during initialization
        with self.assertRaises(ValueError):
            WorldParameters(therapeutic_intensity=1.5)  # Invalid: > 1.0

        with self.assertRaises(ValueError):
            WorldParameters(session_length_preference=200)  # Invalid: > 120

    def test_check_world_compatibility_existing_world(self):
        """Test checking compatibility for an existing world."""
        # Get a world ID
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        compatibility_report = self.world_manager.check_world_compatibility_by_id(
            self.test_character_id, world_id
        )

        self.assertIsNotNone(compatibility_report)
        self.assertEqual(compatibility_report.character_id, self.test_character_id)
        self.assertEqual(compatibility_report.world_id, world_id)
        self.assertGreaterEqual(compatibility_report.overall_score, 0.0)
        self.assertLessEqual(compatibility_report.overall_score, 1.0)
        self.assertIsInstance(compatibility_report.compatibility_factors, list)
        self.assertGreater(len(compatibility_report.compatibility_factors), 0)
        self.assertIsInstance(compatibility_report.recommendations, list)
        self.assertIsInstance(compatibility_report.warnings, list)
        self.assertIsInstance(compatibility_report.prerequisites_met, bool)
        self.assertIsInstance(compatibility_report.unmet_prerequisites, list)

    def test_check_world_compatibility_nonexistent_world(self):
        """Test checking compatibility for a non-existent world."""
        compatibility_report = self.world_manager.check_world_compatibility_by_id(
            self.test_character_id, "nonexistent_world"
        )
        self.assertIsNone(compatibility_report)

    def test_initialize_character_in_world_basic(self):
        """Test basic character initialization in world."""
        # Get a world ID
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        session_data = self.world_manager.initialize_character_in_world(
            self.test_character_id, world_id
        )

        self.assertIsNotNone(session_data)
        self.assertIn("session_id", session_data)
        self.assertEqual(session_data["character_id"], self.test_character_id)
        self.assertEqual(session_data["world_id"], world_id)
        self.assertIn("world_parameters", session_data)
        self.assertIn("compatibility_report", session_data)
        self.assertIn("available_techniques", session_data)
        self.assertIn("session_goals", session_data)
        self.assertIn("created_at", session_data)
        self.assertIsInstance(session_data["created_at"], datetime)

    def test_initialize_character_in_world_with_parameters(self):
        """Test character initialization with custom parameters."""
        # Get a world ID
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        # Create custom parameters
        custom_parameters = WorldParameters(
            therapeutic_intensity=0.8,
            narrative_pace="slow",
            session_length_preference=60,
        )

        session_data = self.world_manager.initialize_character_in_world(
            self.test_character_id, world_id, custom_parameters
        )

        self.assertIsNotNone(session_data)
        self.assertEqual(session_data["world_parameters"], custom_parameters)

    def test_initialize_character_in_world_nonexistent_world(self):
        """Test character initialization in non-existent world."""
        session_data = self.world_manager.initialize_character_in_world(
            self.test_character_id, "nonexistent_world"
        )
        self.assertIsNone(session_data)

    def test_initialize_character_with_external_components(self):
        """Test character initialization with external component integration."""
        # Create mocks for external components
        mock_world_state_manager = Mock()
        mock_therapeutic_generator = Mock()

        manager = WorldManagementModule(
            world_state_manager=mock_world_state_manager,
            therapeutic_environment_generator=mock_therapeutic_generator,
        )

        # Get a world ID
        worlds = manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        session_data = manager.initialize_character_in_world(
            self.test_character_id, world_id
        )

        self.assertIsNotNone(session_data)
        # External components should be called (though they may fail gracefully)

    def test_compatibility_factors_calculation(self):
        """Test compatibility factors calculation."""
        # Get world details
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id
        world_details = self.world_manager.get_world_details(world_id)

        factors = self.world_manager._calculate_compatibility_factors(world_details)

        self.assertIsInstance(factors, list)
        self.assertGreater(len(factors), 0)

        for factor in factors:
            self.assertIsNotNone(factor.factor_name)
            self.assertGreaterEqual(factor.score, 0.0)
            self.assertLessEqual(factor.score, 1.0)
            self.assertIsNotNone(factor.explanation)
            self.assertGreater(factor.weight, 0.0)

    def test_basic_compatibility_score_calculation(self):
        """Test basic compatibility score calculation."""
        # Get world details
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id
        world_details = self.world_manager.get_world_details(world_id)

        score = self.world_manager._calculate_basic_compatibility_score(world_details)

        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_world_parameters_validation(self):
        """Test world parameters validation."""
        # Get world details
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id
        world_details = self.world_manager.get_world_details(world_id)

        # Valid parameters
        valid_params = WorldParameters(
            therapeutic_intensity=0.5, session_length_preference=30
        )

        is_valid = self.world_manager._validate_world_parameters(
            world_details, valid_params
        )
        self.assertTrue(is_valid)

        # Invalid parameters (would be caught by WorldParameters validation)
        with self.assertRaises(ValueError):
            WorldParameters(therapeutic_intensity=1.5)  # > 1.0

        with self.assertRaises(ValueError):
            WorldParameters(session_length_preference=5)  # < 10

    def test_advanced_compatibility_checking_with_character_object(self):
        """Test advanced compatibility checking with Character object."""
        from datetime import datetime

        from src.player_experience.models.character import (
            Character,
            CharacterAppearance,
            CharacterBackground,
            TherapeuticProfile,
        )
        from src.player_experience.models.enums import IntensityLevel

        # Create a test character
        therapeutic_profile = TherapeuticProfile(
            primary_concerns=["anxiety"],
            preferred_intensity=IntensityLevel.MEDIUM,
            readiness_level=0.5,
        )

        test_character = Character(
            character_id=self.test_character_id,
            player_id=self.test_player_id,
            name="Test Character",
            appearance=CharacterAppearance(),
            background=CharacterBackground(name="Test Character"),
            therapeutic_profile=therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        # Get a world ID
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        # Test advanced compatibility checking
        compatibility_report = self.world_manager.check_world_compatibility(
            test_character, world_id
        )

        self.assertIsNotNone(compatibility_report)
        self.assertEqual(compatibility_report.character_id, test_character.character_id)
        self.assertEqual(compatibility_report.world_id, world_id)
        self.assertGreaterEqual(compatibility_report.overall_score, 0.0)
        self.assertLessEqual(compatibility_report.overall_score, 1.0)

        # Should have more detailed compatibility factors from advanced checker
        self.assertGreaterEqual(len(compatibility_report.compatibility_factors), 4)

    def test_get_world_recommendations(self):
        """Test getting personalized world recommendations."""
        from datetime import datetime

        from src.player_experience.models.character import (
            Character,
            CharacterAppearance,
            CharacterBackground,
            TherapeuticProfile,
        )
        from src.player_experience.models.enums import IntensityLevel

        # Create a test character
        therapeutic_profile = TherapeuticProfile(
            primary_concerns=["anxiety"],
            preferred_intensity=IntensityLevel.MEDIUM,
            readiness_level=0.5,
        )

        test_character = Character(
            character_id=self.test_character_id,
            player_id=self.test_player_id,
            name="Test Character",
            appearance=CharacterAppearance(),
            background=CharacterBackground(name="Test Character"),
            therapeutic_profile=therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        # Get recommendations
        recommendations = self.world_manager.get_world_recommendations(
            test_character, max_recommendations=3
        )

        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)
        self.assertGreater(len(recommendations), 0)

        # Check recommendation structure
        for recommendation in recommendations:
            self.assertIn("world_summary", recommendation)
            self.assertIn("compatibility_report", recommendation)
            self.assertIn("suitability_assessment", recommendation)

            # Check that compatibility scores are sorted (highest first)
            self.assertGreaterEqual(
                recommendation["world_summary"].compatibility_score, 0.0
            )
            self.assertLessEqual(
                recommendation["world_summary"].compatibility_score, 1.0
            )

    def test_assess_world_suitability_for_character(self):
        """Test world suitability assessment for a character."""
        from datetime import datetime

        from src.player_experience.models.character import (
            Character,
            CharacterAppearance,
            CharacterBackground,
            TherapeuticProfile,
        )
        from src.player_experience.models.enums import IntensityLevel

        # Create a test character
        therapeutic_profile = TherapeuticProfile(
            primary_concerns=["anxiety"],
            preferred_intensity=IntensityLevel.MEDIUM,
            readiness_level=0.5,
        )

        test_character = Character(
            character_id=self.test_character_id,
            player_id=self.test_player_id,
            name="Test Character",
            appearance=CharacterAppearance(),
            background=CharacterBackground(name="Test Character"),
            therapeutic_profile=therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        # Get a world ID
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        # Assess suitability
        assessment = self.world_manager.assess_world_suitability_for_character(
            test_character, world_id
        )

        self.assertIsNotNone(assessment)
        self.assertIn("suitability_level", assessment)
        self.assertIn("compatibility_score", assessment)
        self.assertIn("compatibility_report", assessment)
        self.assertIn("is_recommended", assessment)
        self.assertIn("has_safety_concerns", assessment)
        self.assertIn("prerequisites_met", assessment)

        # Check data types
        self.assertIsInstance(assessment["suitability_level"], str)
        self.assertIsInstance(assessment["compatibility_score"], float)
        self.assertIsInstance(assessment["is_recommended"], bool)
        self.assertIsInstance(assessment["has_safety_concerns"], bool)
        self.assertIsInstance(assessment["prerequisites_met"], bool)

    def test_assess_world_suitability_nonexistent_world(self):
        """Test world suitability assessment for non-existent world."""
        from datetime import datetime

        from src.player_experience.models.character import (
            Character,
            CharacterAppearance,
            CharacterBackground,
            TherapeuticProfile,
        )
        from src.player_experience.models.enums import IntensityLevel

        # Create a test character
        therapeutic_profile = TherapeuticProfile(
            primary_concerns=["anxiety"],
            preferred_intensity=IntensityLevel.MEDIUM,
            readiness_level=0.5,
        )

        test_character = Character(
            character_id=self.test_character_id,
            player_id=self.test_player_id,
            name="Test Character",
            appearance=CharacterAppearance(),
            background=CharacterBackground(name="Test Character"),
            therapeutic_profile=therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        # Assess suitability for non-existent world
        assessment = self.world_manager.assess_world_suitability_for_character(
            test_character, "nonexistent_world"
        )

        self.assertIsNone(assessment)


if __name__ == "__main__":
    unittest.main()
