"""

# Logseq: [[TTA.dev/Tests/Test_world_management_module]]
Unit tests for WorldManagementModule.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

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
        assert manager is not None
        assert len(manager._world_cache) == 5  # Five default worlds

        # Test initialization with external components
        mock_world_state_manager = Mock()
        mock_therapeutic_generator = Mock()

        manager_with_deps = WorldManagementModule(
            world_state_manager=mock_world_state_manager,
            therapeutic_environment_generator=mock_therapeutic_generator,
        )

        assert manager_with_deps.world_state_manager == mock_world_state_manager
        assert manager_with_deps.therapeutic_environment_generator == mock_therapeutic_generator

    def test_get_available_worlds_without_character(self):
        """Test getting available worlds without character filtering."""
        worlds = self.world_manager.get_available_worlds(self.test_player_id)

        assert isinstance(worlds, list)
        assert len(worlds) == 5  # Five default worlds

        # Check that worlds are sorted by rating (highest first)
        assert worlds[0].average_rating >= worlds[1].average_rating

        # Verify world summary structure
        world = worlds[0]
        assert world.world_id is not None
        assert world.name is not None
        assert world.description is not None
        assert isinstance(world.therapeutic_themes, list)
        assert isinstance(world.therapeutic_approaches, list)
        assert isinstance(world.difficulty_level, DifficultyLevel)
        assert isinstance(world.estimated_duration, timedelta)
        assert world.compatibility_score == 0.0  # No character specified

    def test_get_available_worlds_with_character(self):
        """Test getting available worlds with character compatibility filtering."""
        worlds = self.world_manager.get_available_worlds(
            self.test_player_id, self.test_character_id
        )

        assert isinstance(worlds, list)
        assert len(worlds) == 5

        # Check that compatibility scores are calculated
        for world in worlds:
            assert world.compatibility_score > 0.0
            assert world.compatibility_score <= 1.0

        # Check that worlds are sorted by compatibility score
        assert worlds[0].compatibility_score >= worlds[1].compatibility_score

    def test_get_world_details_existing_world(self):
        """Test getting details for an existing world."""
        # Get a world ID from available worlds
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        details = self.world_manager.get_world_details(world_id)

        assert details is not None
        assert details.world_id == world_id
        assert details.name is not None
        assert details.description is not None
        assert details.long_description is not None
        assert isinstance(details.therapeutic_themes, list)
        assert isinstance(details.therapeutic_approaches, list)
        assert isinstance(details.key_characters, list)
        assert isinstance(details.main_storylines, list)
        assert isinstance(details.therapeutic_techniques_used, list)
        assert isinstance(details.prerequisites, list)
        assert isinstance(details.available_parameters, list)

    def test_get_world_details_nonexistent_world(self):
        """Test getting details for a non-existent world."""
        details = self.world_manager.get_world_details("nonexistent_world")
        assert details is None

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

        assert customized_world is not None
        assert customized_world.world_id == world_id
        assert customized_world.customized_parameters == parameters
        assert isinstance(customized_world.compatibility_report, CompatibilityReport)

    def test_customize_world_parameters_invalid_world(self):
        """Test customizing parameters for a non-existent world."""
        parameters = WorldParameters()
        customized_world = self.world_manager.customize_world_parameters(
            "nonexistent_world", parameters
        )
        assert customized_world is None

    def test_customize_world_parameters_invalid_parameters(self):
        """Test customizing world parameters with invalid parameters."""
        # Test that invalid parameters raise ValueError during initialization
        with pytest.raises(ValueError):
            WorldParameters(therapeutic_intensity=1.5)  # Invalid: > 1.0

        with pytest.raises(ValueError):
            WorldParameters(session_length_preference=200)  # Invalid: > 120

    def test_check_world_compatibility_existing_world(self):
        """Test checking compatibility for an existing world."""
        # Get a world ID
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        compatibility_report = self.world_manager.check_world_compatibility_by_id(
            self.test_character_id, world_id
        )

        assert compatibility_report is not None
        assert compatibility_report.character_id == self.test_character_id
        assert compatibility_report.world_id == world_id
        assert compatibility_report.overall_score >= 0.0
        assert compatibility_report.overall_score <= 1.0
        assert isinstance(compatibility_report.compatibility_factors, list)
        assert len(compatibility_report.compatibility_factors) > 0
        assert isinstance(compatibility_report.recommendations, list)
        assert isinstance(compatibility_report.warnings, list)
        assert isinstance(compatibility_report.prerequisites_met, bool)
        assert isinstance(compatibility_report.unmet_prerequisites, list)

    def test_check_world_compatibility_nonexistent_world(self):
        """Test checking compatibility for a non-existent world."""
        compatibility_report = self.world_manager.check_world_compatibility_by_id(
            self.test_character_id, "nonexistent_world"
        )
        assert compatibility_report is None

    def test_initialize_character_in_world_basic(self):
        """Test basic character initialization in world."""
        # Get a world ID
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id

        session_data = self.world_manager.initialize_character_in_world(
            self.test_character_id, world_id
        )

        assert session_data is not None
        assert "session_id" in session_data
        assert session_data["character_id"] == self.test_character_id
        assert session_data["world_id"] == world_id
        assert "world_parameters" in session_data
        assert "compatibility_report" in session_data
        assert "available_techniques" in session_data
        assert "session_goals" in session_data
        assert "created_at" in session_data
        assert isinstance(session_data["created_at"], datetime)

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

        assert session_data is not None
        assert session_data["world_parameters"] == custom_parameters

    def test_initialize_character_in_world_nonexistent_world(self):
        """Test character initialization in non-existent world."""
        session_data = self.world_manager.initialize_character_in_world(
            self.test_character_id, "nonexistent_world"
        )
        assert session_data is None

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

        assert session_data is not None
        # External components should be called (though they may fail gracefully)

    def test_compatibility_factors_calculation(self):
        """Test compatibility factors calculation."""
        # Get world details
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id
        world_details = self.world_manager.get_world_details(world_id)

        factors = self.world_manager._calculate_compatibility_factors(world_details)

        assert isinstance(factors, list)
        assert len(factors) > 0

        for factor in factors:
            assert factor.factor_name is not None
            assert factor.score >= 0.0
            assert factor.score <= 1.0
            assert factor.explanation is not None
            assert factor.weight > 0.0

    def test_basic_compatibility_score_calculation(self):
        """Test basic compatibility score calculation."""
        # Get world details
        worlds = self.world_manager.get_available_worlds(self.test_player_id)
        world_id = worlds[0].world_id
        world_details = self.world_manager.get_world_details(world_id)

        score = self.world_manager._calculate_basic_compatibility_score(world_details)

        assert score >= 0.0
        assert score <= 1.0

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
        assert is_valid

        # Invalid parameters (would be caught by WorldParameters validation)
        with pytest.raises(ValueError):
            WorldParameters(therapeutic_intensity=1.5)  # > 1.0

        with pytest.raises(ValueError):
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

        assert compatibility_report is not None
        assert compatibility_report.character_id == test_character.character_id
        assert compatibility_report.world_id == world_id
        assert compatibility_report.overall_score >= 0.0
        assert compatibility_report.overall_score <= 1.0

        # Should have more detailed compatibility factors from advanced checker
        assert len(compatibility_report.compatibility_factors) >= 4

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

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 3
        assert len(recommendations) > 0

        # Check recommendation structure
        for recommendation in recommendations:
            assert "world_summary" in recommendation
            assert "compatibility_report" in recommendation
            assert "suitability_assessment" in recommendation

            # Check that compatibility scores are sorted (highest first)
            assert recommendation["world_summary"].compatibility_score >= 0.0
            assert recommendation["world_summary"].compatibility_score <= 1.0

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

        assert assessment is not None
        assert "suitability_level" in assessment
        assert "compatibility_score" in assessment
        assert "compatibility_report" in assessment
        assert "is_recommended" in assessment
        assert "has_safety_concerns" in assessment
        assert "prerequisites_met" in assessment

        # Check data types
        assert isinstance(assessment["suitability_level"], str)
        assert isinstance(assessment["compatibility_score"], float)
        assert isinstance(assessment["is_recommended"], bool)
        assert isinstance(assessment["has_safety_concerns"], bool)
        assert isinstance(assessment["prerequisites_met"], bool)

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

        assert assessment is None


if __name__ == "__main__":
    unittest.main()
