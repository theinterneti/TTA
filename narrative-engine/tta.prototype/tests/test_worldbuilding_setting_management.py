"""
Unit Tests for Worldbuilding and Setting Management

This module contains comprehensive unit tests for the worldbuilding and setting
management system, including world state tracking, consistency validation,
location management, and setting description generation.
"""

import json
import unittest
from unittest.mock import Mock, patch

# Import the classes to test
from ..core.worldbuilding_setting_management import (
    LocationDetails,
    LocationType,
    ValidationResult,
    ValidationSeverity,
    WorldbuildingSettingManagement,
    WorldChange,
    WorldChangeType,
    create_sample_location,
)
from ..models.data_models import NarrativeContext, ValidationError


class TestLocationDetails(unittest.TestCase):
    """Test cases for LocationDetails class."""

    def setUp(self):
        """Set up test fixtures."""
        self.location = LocationDetails(
            location_id="test_location",
            name="Test Location",
            description="A test location for unit testing",
            location_type=LocationType.SAFE_SPACE,
            therapeutic_themes=["mindfulness", "safety"],
            atmosphere="peaceful",
            safety_level=0.8,
            immersion_level=0.6
        )

    def test_location_creation(self):
        """Test basic location creation."""
        self.assertEqual(self.location.location_id, "test_location")
        self.assertEqual(self.location.name, "Test Location")
        self.assertEqual(self.location.location_type, LocationType.SAFE_SPACE)
        self.assertEqual(self.location.safety_level, 0.8)
        self.assertEqual(self.location.immersion_level, 0.6)

    def test_location_validation_success(self):
        """Test successful location validation."""
        self.assertTrue(self.location.validate())

    def test_location_validation_empty_id(self):
        """Test validation failure with empty location ID."""
        self.location.location_id = ""
        with self.assertRaises(ValidationError):
            self.location.validate()

    def test_location_validation_empty_name(self):
        """Test validation failure with empty name."""
        self.location.name = ""
        with self.assertRaises(ValidationError):
            self.location.validate()

    def test_location_validation_invalid_safety_level(self):
        """Test validation failure with invalid safety level."""
        self.location.safety_level = 1.5
        with self.assertRaises(ValidationError):
            self.location.validate()

        self.location.safety_level = -0.1
        with self.assertRaises(ValidationError):
            self.location.validate()

    def test_location_validation_invalid_immersion_level(self):
        """Test validation failure with invalid immersion level."""
        self.location.immersion_level = 1.1
        with self.assertRaises(ValidationError):
            self.location.validate()

        self.location.immersion_level = -0.1
        with self.assertRaises(ValidationError):
            self.location.validate()

    def test_location_to_dict(self):
        """Test location serialization to dictionary."""
        location_dict = self.location.to_dict()

        self.assertEqual(location_dict['location_id'], "test_location")
        self.assertEqual(location_dict['name'], "Test Location")
        self.assertEqual(location_dict['location_type'], "safe_space")
        self.assertIn('created_at', location_dict)
        self.assertIn('last_modified', location_dict)

    def test_location_from_dict(self):
        """Test location deserialization from dictionary."""
        location_dict = self.location.to_dict()
        restored_location = LocationDetails.from_dict(location_dict)

        self.assertEqual(restored_location.location_id, self.location.location_id)
        self.assertEqual(restored_location.name, self.location.name)
        self.assertEqual(restored_location.location_type, self.location.location_type)
        self.assertEqual(restored_location.safety_level, self.location.safety_level)


class TestWorldChange(unittest.TestCase):
    """Test cases for WorldChange class."""

    def setUp(self):
        """Set up test fixtures."""
        self.world_change = WorldChange(
            change_type=WorldChangeType.LOCATION_MODIFY,
            target_location_id="test_location",
            description="Test world change",
            changes={"atmosphere": "mysterious"},
            prerequisites=["flag:test_flag"],
            consequences=["location_atmosphere_changed"],
            therapeutic_impact="Increases mystery and exploration motivation"
        )

    def test_world_change_creation(self):
        """Test basic world change creation."""
        self.assertEqual(self.world_change.change_type, WorldChangeType.LOCATION_MODIFY)
        self.assertEqual(self.world_change.target_location_id, "test_location")
        self.assertEqual(self.world_change.description, "Test world change")
        self.assertFalse(self.world_change.applied)

    def test_world_change_validation_success(self):
        """Test successful world change validation."""
        self.assertTrue(self.world_change.validate())

    def test_world_change_validation_empty_target(self):
        """Test validation failure with empty target location."""
        self.world_change.target_location_id = ""
        with self.assertRaises(ValidationError):
            self.world_change.validate()

    def test_world_change_validation_empty_description(self):
        """Test validation failure with empty description."""
        self.world_change.description = ""
        with self.assertRaises(ValidationError):
            self.world_change.validate()


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult class."""

    def setUp(self):
        """Set up test fixtures."""
        self.validation_result = ValidationResult()

    def test_validation_result_creation(self):
        """Test basic validation result creation."""
        self.assertTrue(self.validation_result.is_valid)
        self.assertEqual(len(self.validation_result.issues), 0)
        self.assertEqual(self.validation_result.warnings_count, 0)
        self.assertEqual(self.validation_result.errors_count, 0)
        self.assertEqual(self.validation_result.critical_count, 0)

    def test_add_warning_issue(self):
        """Test adding a warning issue."""
        self.validation_result.add_issue(
            ValidationSeverity.WARNING,
            "test_category",
            "Test warning",
            "test_location",
            "Fix the warning"
        )

        self.assertTrue(self.validation_result.is_valid)  # Warnings don't invalidate
        self.assertEqual(len(self.validation_result.issues), 1)
        self.assertEqual(self.validation_result.warnings_count, 1)
        self.assertEqual(self.validation_result.errors_count, 0)

    def test_add_error_issue(self):
        """Test adding an error issue."""
        self.validation_result.add_issue(
            ValidationSeverity.ERROR,
            "test_category",
            "Test error",
            "test_location",
            "Fix the error"
        )

        self.assertFalse(self.validation_result.is_valid)  # Errors invalidate
        self.assertEqual(len(self.validation_result.issues), 1)
        self.assertEqual(self.validation_result.warnings_count, 0)
        self.assertEqual(self.validation_result.errors_count, 1)

    def test_add_critical_issue(self):
        """Test adding a critical issue."""
        self.validation_result.add_issue(
            ValidationSeverity.CRITICAL,
            "test_category",
            "Test critical issue",
            "test_location",
            "Fix the critical issue"
        )

        self.assertFalse(self.validation_result.is_valid)  # Critical issues invalidate
        self.assertEqual(len(self.validation_result.issues), 1)
        self.assertEqual(self.validation_result.warnings_count, 0)
        self.assertEqual(self.validation_result.critical_count, 1)


class TestWorldbuildingSettingManagement(unittest.TestCase):
    """Test cases for WorldbuildingSettingManagement class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_neo4j_driver = Mock()
        self.mock_redis_client = Mock()
        self.world_manager = WorldbuildingSettingManagement(
            neo4j_driver=self.mock_neo4j_driver,
            redis_client=self.mock_redis_client
        )

        # Create test locations
        self.test_location = create_sample_location(
            "test_location",
            "Test Location",
            LocationType.SAFE_SPACE
        )
        self.connected_location = create_sample_location(
            "connected_location",
            "Connected Location",
            LocationType.THERAPEUTIC_ENVIRONMENT
        )

        # Set up connections
        self.test_location.connected_locations = {"north": "connected_location"}
        self.connected_location.connected_locations = {"south": "test_location"}

        # Add to cache
        self.world_manager.locations_cache[self.test_location.location_id] = self.test_location
        self.world_manager.locations_cache[self.connected_location.location_id] = self.connected_location

    def test_worldbuilding_manager_initialization(self):
        """Test worldbuilding manager initialization."""
        self.assertIsNotNone(self.world_manager.neo4j_driver)
        self.assertIsNotNone(self.world_manager.redis_client)
        self.assertEqual(len(self.world_manager.locations_cache), 2)
        self.assertGreater(len(self.world_manager.consistency_rules), 0)

    def test_get_location_details_from_cache(self):
        """Test getting location details from cache."""
        location = self.world_manager.get_location_details("test_location")

        self.assertIsNotNone(location)
        self.assertEqual(location.location_id, "test_location")
        self.assertEqual(location.name, "Test Location")

    def test_get_location_details_not_found(self):
        """Test getting non-existent location details."""
        location = self.world_manager.get_location_details("non_existent")
        self.assertIsNone(location)

    @patch('json.loads')
    def test_get_location_details_from_redis(self):
        """Test getting location details from Redis cache."""
        # Clear local cache
        self.world_manager.locations_cache.clear()

        # Mock Redis response
        location_data = self.test_location.to_dict()
        self.mock_redis_client.get.return_value = json.dumps(location_data)

        location = self.world_manager.get_location_details("test_location")

        self.assertIsNotNone(location)
        self.assertEqual(location.location_id, "test_location")
        self.mock_redis_client.get.assert_called_once_with("location:test_location")

    def test_get_location_details_from_neo4j(self):
        """Test getting location details from Neo4j database."""
        # Clear local cache
        self.world_manager.locations_cache.clear()

        # Mock Redis miss
        self.mock_redis_client.get.return_value = None

        # Mock Neo4j response
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()
        mock_record.__getitem__ = Mock(return_value=self.test_location.to_dict())
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        self.mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        location = self.world_manager.get_location_details("test_location")

        self.assertIsNotNone(location)
        self.assertEqual(location.location_id, "test_location")

    def test_update_world_state_success(self):
        """Test successful world state update."""
        world_change = WorldChange(
            change_type=WorldChangeType.LOCATION_MODIFY,
            target_location_id="test_location",
            description="Change atmosphere",
            changes={"atmosphere": "mysterious"}
        )

        result = self.world_manager.update_world_state([world_change])

        self.assertTrue(result)
        self.assertTrue(world_change.applied)

        # Check that location was updated
        updated_location = self.world_manager.get_location_details("test_location")
        self.assertEqual(updated_location.atmosphere, "mysterious")

    def test_update_world_state_invalid_change(self):
        """Test world state update with invalid change."""
        world_change = WorldChange(
            change_type=WorldChangeType.LOCATION_MODIFY,
            target_location_id="",  # Invalid empty target
            description="Invalid change",
            changes={"atmosphere": "mysterious"}
        )

        result = self.world_manager.update_world_state([world_change])

        self.assertFalse(result)
        self.assertFalse(world_change.applied)

    def test_update_world_state_prerequisites_not_met(self):
        """Test world state update with unmet prerequisites."""
        world_change = WorldChange(
            change_type=WorldChangeType.LOCATION_MODIFY,
            target_location_id="test_location",
            description="Change with prerequisites",
            changes={"atmosphere": "mysterious"},
            prerequisites=["flag:non_existent_flag"]
        )

        result = self.world_manager.update_world_state([world_change])

        self.assertFalse(result)
        self.assertFalse(world_change.applied)

    def test_unlock_location(self):
        """Test location unlocking."""
        # Add unlock conditions to test location
        self.test_location.unlock_conditions = ["flag:test_completed"]

        world_change = WorldChange(
            change_type=WorldChangeType.LOCATION_UNLOCK,
            target_location_id="test_location",
            description="Unlock test location",
            changes={}
        )

        result = self.world_manager.update_world_state([world_change])

        self.assertTrue(result)

        # Check that unlock conditions were cleared
        updated_location = self.world_manager.get_location_details("test_location")
        self.assertEqual(len(updated_location.unlock_conditions), 0)

    def test_generate_setting_description_basic(self):
        """Test basic setting description generation."""
        context = NarrativeContext(session_id="test_session")

        description = self.world_manager.generate_setting_description("test_location", context)

        self.assertIsInstance(description, str)
        self.assertGreater(len(description), 0)
        self.assertIn("safe space", description.lower())

    def test_generate_setting_description_with_atmosphere(self):
        """Test setting description generation with specific atmosphere."""
        self.test_location.atmosphere = "mysterious"
        context = NarrativeContext(session_id="test_session")

        description = self.world_manager.generate_setting_description("test_location", context)

        self.assertIn("mystery", description.lower())

    def test_generate_setting_description_with_environmental_factors(self):
        """Test setting description generation with environmental factors."""
        self.test_location.environmental_factors = {
            "lighting": "dimly lit",
            "weather": "foggy",
            "sounds": "gentle wind"
        }
        context = NarrativeContext(session_id="test_session")

        description = self.world_manager.generate_setting_description("test_location", context)

        self.assertIn("dimly lit", description)
        self.assertIn("foggy", description)
        self.assertIn("gentle wind", description)

    def test_generate_setting_description_non_existent_location(self):
        """Test setting description generation for non-existent location."""
        context = NarrativeContext(session_id="test_session")

        description = self.world_manager.generate_setting_description("non_existent", context)

        self.assertIn("unknown place", description)
        self.assertIn("non_existent", description)

    def test_validate_world_consistency_success(self):
        """Test successful world consistency validation."""
        result = self.world_manager.validate_world_consistency()

        self.assertIsInstance(result, ValidationResult)
        # Should have minimal issues with our well-connected test locations
        self.assertLessEqual(result.errors_count, 0)

    def test_validate_world_consistency_with_issues(self):
        """Test world consistency validation with issues."""
        # Create a location with no connections
        isolated_location = create_sample_location("isolated", "Isolated Location")
        self.world_manager.locations_cache[isolated_location.location_id] = isolated_location

        result = self.world_manager.validate_world_consistency()

        self.assertGreater(len(result.issues), 0)
        # Should have at least one warning about the isolated location
        self.assertGreater(result.warnings_count, 0)

    def test_check_location_connectivity(self):
        """Test location connectivity checking."""
        issues = self.world_manager._check_location_connectivity()

        # Our test locations are properly connected, so should have no connectivity issues
        connectivity_issues = [issue for issue in issues if issue.category == "connectivity"]
        self.assertEqual(len(connectivity_issues), 0)

    def test_check_location_connectivity_with_missing_connection(self):
        """Test location connectivity checking with missing connection."""
        # Add connection to non-existent location
        self.test_location.connected_locations["east"] = "non_existent_location"

        issues = self.world_manager._check_location_connectivity()

        # Should find the missing connection
        connectivity_issues = [issue for issue in issues if issue.category == "connectivity"]
        self.assertGreater(len(connectivity_issues), 0)

        # Should be an error (not just warning) for non-existent location
        error_issues = [issue for issue in connectivity_issues if issue.severity == ValidationSeverity.ERROR]
        self.assertGreater(len(error_issues), 0)

    def test_check_therapeutic_coherence(self):
        """Test therapeutic coherence checking."""
        # Set up conflicting themes
        self.test_location.therapeutic_themes = ["relaxation"]
        self.connected_location.therapeutic_themes = ["high_stress"]

        issues = self.world_manager._check_therapeutic_coherence()

        # Should find therapeutic coherence issues
        coherence_issues = [issue for issue in issues if issue.category == "therapeutic_coherence"]
        self.assertGreater(len(coherence_issues), 0)

    def test_check_safety_progression(self):
        """Test safety progression checking."""
        # Set up large safety level difference
        self.test_location.safety_level = 0.9
        self.connected_location.safety_level = 0.1

        issues = self.world_manager._check_safety_progression()

        # Should find safety progression issues
        safety_issues = [issue for issue in issues if issue.category == "safety_progression"]
        self.assertGreater(len(safety_issues), 0)

    def test_check_unlock_dependencies(self):
        """Test unlock dependencies checking."""
        # Add unsatisfiable unlock condition
        self.test_location.unlock_conditions = ["impossible_condition:never_true"]

        issues = self.world_manager._check_unlock_dependencies()

        # Should find dependency issues
        dependency_issues = [issue for issue in issues if issue.category == "unlock_dependencies"]
        self.assertGreater(len(dependency_issues), 0)

    def test_save_location_success(self):
        """Test successful location saving."""
        # Mock successful Redis and Neo4j operations
        self.mock_redis_client.setex.return_value = True
        mock_session = Mock()
        self.mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = self.world_manager._save_location(self.test_location)

        self.assertTrue(result)
        self.mock_redis_client.setex.assert_called_once()
        mock_session.run.assert_called_once()

    def test_save_location_redis_failure(self):
        """Test location saving with Redis failure."""
        # Mock Redis failure
        self.mock_redis_client.setex.side_effect = Exception("Redis error")

        # Should still succeed if Neo4j works
        mock_session = Mock()
        self.mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = self.world_manager._save_location(self.test_location)

        # Should still return True despite Redis failure
        self.assertTrue(result)

    def test_prerequisite_evaluation(self):
        """Test prerequisite evaluation."""
        # Test flag prerequisite
        self.world_manager.world_state_flags["test_flag"] = True
        self.assertTrue(self.world_manager._evaluate_prerequisite("flag:test_flag"))

        self.world_manager.world_state_flags["test_flag"] = False
        self.assertFalse(self.world_manager._evaluate_prerequisite("flag:test_flag"))

        # Test location exists prerequisite
        self.assertTrue(self.world_manager._evaluate_prerequisite("location_exists:test_location"))
        self.assertFalse(self.world_manager._evaluate_prerequisite("location_exists:non_existent"))

        # Test unknown prerequisite (should default to True)
        self.assertTrue(self.world_manager._evaluate_prerequisite("unknown:prerequisite"))


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_create_sample_location(self):
        """Test sample location creation utility."""
        location = create_sample_location("sample", "Sample Location", LocationType.CHALLENGE_AREA)

        self.assertEqual(location.location_id, "sample")
        self.assertEqual(location.name, "Sample Location")
        self.assertEqual(location.location_type, LocationType.CHALLENGE_AREA)
        self.assertIn("mindfulness", location.therapeutic_themes)
        self.assertIn("safety", location.therapeutic_themes)
        self.assertEqual(location.atmosphere, "peaceful")
        self.assertEqual(location.safety_level, 0.8)
        self.assertEqual(location.immersion_level, 0.6)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
