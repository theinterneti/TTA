"""
Unit tests for PlayerProfile database schema and repository operations.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
import uuid

from src.player_experience.models.player import (
    PlayerProfile, TherapeuticPreferences, PrivacySettings, 
    CrisisContactInfo, ProgressSummary
)
from src.player_experience.models.enums import IntensityLevel, TherapeuticApproach
from src.player_experience.database.player_profile_schema import (
    PlayerProfileSchemaManager, PlayerProfileSchemaError, setup_player_profile_schema
)
from src.player_experience.database.player_profile_repository import (
    PlayerProfileRepository, PlayerProfileRepositoryError, create_player_profile_repository
)


import pytest


class TestPlayerProfileSchemaManager(unittest.TestCase):
    """Test PlayerProfileSchemaManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.schema_manager = PlayerProfileSchemaManager()
        self.mock_driver = MagicMock()
        self.mock_session = MagicMock()
        self.schema_manager.driver = self.mock_driver
        # MagicMock provides __enter__/__exit__; we still set the session's __enter__ return
        self.mock_driver.session.return_value.__enter__.return_value = self.mock_session
    
    def test_schema_manager_initialization(self):
        """Test schema manager initialization."""
        manager = PlayerProfileSchemaManager(
            uri="bolt://localhost:7687",
            username="test_user",
            password="test_pass"
        )
        
        self.assertEqual(manager.uri, "bolt://localhost:7687")
        self.assertEqual(manager.username, "test_user")
        self.assertEqual(manager.password, "test_pass")
        self.assertEqual(manager.player_schema_version, "1.0.0")
        self.assertIsNone(manager.driver)
    
    @patch('src.player_experience.database.player_profile_schema.GraphDatabase')
    def test_connect_success(self, mock_graph_db):
        """Test successful database connection."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        manager = PlayerProfileSchemaManager()
        manager.connect()
        
        self.assertEqual(manager.driver, mock_driver)
        mock_graph_db.driver.assert_called_once_with(
            "bolt://localhost:7687", 
            auth=("neo4j", "password")
        )
        mock_session.run.assert_called_once_with("RETURN 1")
    
    @patch('src.player_experience.database.player_profile_schema.GraphDatabase')
    def test_connect_failure(self, mock_graph_db):
        """Test database connection failure."""
        from src.player_experience.database.player_profile_schema import ServiceUnavailable
        mock_graph_db.driver.side_effect = ServiceUnavailable("Connection failed")
        
        manager = PlayerProfileSchemaManager()
        
        with self.assertRaises(PlayerProfileSchemaError):
            manager.connect()
    
    def test_disconnect(self):
        """Test database disconnection."""
        mock_driver = MagicMock()
        self.schema_manager.driver = mock_driver

        self.schema_manager.disconnect()

        mock_driver.close.assert_called_once()
        self.assertIsNone(self.schema_manager.driver)
    
    def test_is_connected_true(self):
        """Test connection check when connected."""
        self.assertTrue(self.schema_manager.is_connected())
        self.mock_session.run.assert_called_with("RETURN 1")
    
    def test_is_connected_false_no_driver(self):
        """Test connection check when no driver."""
        self.schema_manager.driver = None
        self.assertFalse(self.schema_manager.is_connected())
    
    def test_is_connected_false_exception(self):
        """Test connection check when exception occurs."""
        self.mock_session.run.side_effect = Exception("Connection error")
        self.assertFalse(self.schema_manager.is_connected())
    
    def test_create_player_profile_constraints_success(self):
        """Test successful constraint creation."""
        self.mock_session.run.return_value = None
        
        result = self.schema_manager.create_player_profile_constraints()
        
        self.assertTrue(result)
        # Verify that multiple constraint creation queries were called
        self.assertGreater(self.mock_session.run.call_count, 5)
    
    def test_create_player_profile_constraints_already_exists(self):
        """Test constraint creation when constraints already exist."""
        from src.player_experience.database.player_profile_schema import ClientError
        self.mock_session.run.side_effect = ClientError("already exists")
        
        result = self.schema_manager.create_player_profile_constraints()
        
        self.assertTrue(result)
    
    def test_create_player_profile_constraints_failure(self):
        """Test constraint creation failure."""
        from src.player_experience.database.player_profile_schema import ClientError
        self.mock_session.run.side_effect = ClientError("Constraint creation failed")
        
        result = self.schema_manager.create_player_profile_constraints()
        
        self.assertFalse(result)
    
    def test_create_player_profile_indexes_success(self):
        """Test successful index creation."""
        self.mock_session.run.return_value = None
        
        result = self.schema_manager.create_player_profile_indexes()
        
        self.assertTrue(result)
        # Verify that multiple index creation queries were called
        self.assertGreater(self.mock_session.run.call_count, 10)
    
    def test_setup_player_profile_schema_success(self):
        """Test successful complete schema setup."""
        self.mock_session.run.return_value = None
        
        result = self.schema_manager.setup_player_profile_schema()
        
        self.assertTrue(result)
        # Verify that schema version was recorded
        self.assertGreater(self.mock_session.run.call_count, 15)
    
    def test_setup_player_profile_schema_constraint_failure(self):
        """Test schema setup failure during constraint creation."""
        from src.player_experience.database.player_profile_schema import ClientError
        self.mock_session.run.side_effect = ClientError("Constraint creation failed")
        
        result = self.schema_manager.setup_player_profile_schema()
        
        self.assertFalse(result)
    
    def test_get_player_schema_version_success(self):
        """Test getting schema version successfully."""
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = "1.0.0"
        self.mock_session.run.return_value.single.return_value = mock_record
        
        version = self.schema_manager.get_player_schema_version()
        
        self.assertEqual(version, "1.0.0")
    
    def test_get_player_schema_version_not_found(self):
        """Test getting schema version when not found."""
        self.mock_session.run.return_value.single.return_value = None
        
        version = self.schema_manager.get_player_schema_version()
        
        self.assertIsNone(version)
    
    def test_validate_player_profile_schema_success(self):
        """Test successful schema validation."""
        # Mock constraints result
        mock_constraints = [
            {"name": "player_profile_id"},
            {"name": "player_username"},
            {"name": "player_email"},
            {"name": "therapeutic_prefs_id"},
            {"name": "privacy_settings_id"}
        ]
        
        # Mock indexes result
        mock_indexes = [
            {"name": "player_username_idx"},
            {"name": "player_email_idx"},
            {"name": "player_created_at_idx"}
        ]
        
        self.mock_session.run.side_effect = [mock_constraints, mock_indexes]
        
        result = self.schema_manager.validate_player_profile_schema()
        
        self.assertTrue(result)
    
    def test_validate_player_profile_schema_missing_constraints(self):
        """Test schema validation with missing constraints."""
        # Mock empty constraints result
        self.mock_session.run.side_effect = [[], []]
        
        result = self.schema_manager.validate_player_profile_schema()
        
        self.assertFalse(result)
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with patch.object(self.schema_manager, 'connect') as mock_connect, \
             patch.object(self.schema_manager, 'disconnect') as mock_disconnect:
            
            with self.schema_manager:
                pass
            
            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()


import pytest


class TestPlayerProfileRepository(unittest.TestCase):
    """Test PlayerProfileRepository functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repository = PlayerProfileRepository()
        self.mock_driver = MagicMock()
        self.mock_session = MagicMock()
        self.repository.driver = self.mock_driver
        self.mock_driver.session.return_value.__enter__.return_value = self.mock_session
        self.mock_driver.session.return_value.__exit__.return_value = None
        
        # Create test player profile
        self.test_profile = PlayerProfile(
            player_id="test_player_123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now()
        )
    
    def test_repository_initialization(self):
        """Test repository initialization."""
        repo = PlayerProfileRepository(
            uri="bolt://localhost:7687",
            username="test_user",
            password="test_pass"
        )
        
        self.assertEqual(repo.uri, "bolt://localhost:7687")
        self.assertEqual(repo.username, "test_user")
        self.assertEqual(repo.password, "test_pass")
        self.assertIsNone(repo.driver)
    
    @patch('src.player_experience.database.player_profile_repository.GraphDatabase')
    def test_connect_success(self, mock_graph_db):
        """Test successful repository connection."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        repo = PlayerProfileRepository()
        repo.connect()
        
        self.assertEqual(repo.driver, mock_driver)
        mock_session.run.assert_called_once_with("RETURN 1")
    
    def test_serialize_therapeutic_preferences(self):
        """Test therapeutic preferences serialization."""
        prefs = TherapeuticPreferences(
            intensity_level=IntensityLevel.HIGH,
            preferred_approaches=[TherapeuticApproach.CBT, TherapeuticApproach.MINDFULNESS],
            trigger_warnings=["violence"],
            comfort_topics=["nature"],
            session_duration_preference=45
        )
        
        serialized = self.repository._serialize_therapeutic_preferences(prefs)
        
        self.assertEqual(serialized["intensity_level"], "high")
        self.assertEqual(serialized["preferred_approaches"], ["cognitive_behavioral_therapy", "mindfulness"])
        self.assertEqual(serialized["trigger_warnings"], ["violence"])
        self.assertEqual(serialized["comfort_topics"], ["nature"])
        self.assertEqual(serialized["session_duration_preference"], 45)
        self.assertIn("preferences_id", serialized)
    
    def test_serialize_privacy_settings(self):
        """Test privacy settings serialization."""
        privacy = PrivacySettings(
            data_collection_consent=True,
            research_participation_consent=False,
            data_retention_period_days=180
        )
        
        serialized = self.repository._serialize_privacy_settings(privacy)
        
        self.assertTrue(serialized["data_collection_consent"])
        self.assertFalse(serialized["research_participation_consent"])
        self.assertEqual(serialized["data_retention_period_days"], 180)
        self.assertIn("settings_id", serialized)
    
    def test_serialize_progress_summary(self):
        """Test progress summary serialization."""
        progress = ProgressSummary(
            total_sessions=10,
            total_time_minutes=300,
            milestones_achieved=3,
            current_streak_days=5
        )
        
        serialized = self.repository._serialize_progress_summary(progress)
        
        self.assertEqual(serialized["total_sessions"], 10)
        self.assertEqual(serialized["total_time_minutes"], 300)
        self.assertEqual(serialized["milestones_achieved"], 3)
        self.assertEqual(serialized["current_streak_days"], 5)
        self.assertIn("summary_id", serialized)
    
    def test_create_player_profile_success(self):
        """Test successful player profile creation."""
        mock_record = MagicMock()
        self.mock_session.run.return_value.single.return_value = mock_record
        
        result = self.repository.create_player_profile(self.test_profile)
        
        self.assertTrue(result)
        self.mock_session.run.assert_called_once()
        
        # Verify the query was called with correct parameters
        call_args = self.mock_session.run.call_args
        self.assertIn("player_id", call_args[1])
        self.assertEqual(call_args[1]["player_id"], "test_player_123")
        self.assertEqual(call_args[1]["username"], "testuser")
        self.assertEqual(call_args[1]["email"], "test@example.com")
    
    def test_create_player_profile_already_exists(self):
        """Test player profile creation when profile already exists."""
        from src.player_experience.database.player_profile_repository import ClientError
        self.mock_session.run.side_effect = ClientError("already exists")
        
        with self.assertRaises(PlayerProfileRepositoryError):
            self.repository.create_player_profile(self.test_profile)
    
    def test_create_player_profile_failure(self):
        """Test player profile creation failure."""
        self.mock_session.run.return_value.single.return_value = None
        
        result = self.repository.create_player_profile(self.test_profile)
        
        self.assertFalse(result)
    
    def test_get_player_profile_success(self):
        """Test successful player profile retrieval."""
        # Mock database response
        mock_record = MagicMock()
        mock_record.__getitem__.side_effect = lambda key: {
            "p": {
                "player_id": "test_player_123",
                "username": "testuser",
                "email": "test@example.com",
                "created_at": datetime.now().isoformat(),
                "is_active": True,
                "characters": [],
                "active_sessions": "{}"
            },
            "tp": {
                "intensity_level": "medium",
                "preferred_approaches": [],
                "trigger_warnings": [],
                "comfort_topics": [],
                "avoid_topics": [],
                "session_duration_preference": 30,
                "reminder_frequency": "weekly",
                "crisis_contact_info": None
            },
            "ps": {
                "data_collection_consent": True,
                "research_participation_consent": False,
                "data_retention_period_days": 365
            },
            "pr": {
                "total_sessions": 0,
                "total_time_minutes": 0,
                "milestones_achieved": 0,
                "current_streak_days": 0,
                "longest_streak_days": 0
            }
        }[key]
        
        self.mock_session.run.return_value.single.return_value = mock_record
        
        profile = self.repository.get_player_profile("test_player_123")
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.player_id, "test_player_123")
        self.assertEqual(profile.username, "testuser")
        self.assertEqual(profile.email, "test@example.com")
    
    def test_get_player_profile_not_found(self):
        """Test player profile retrieval when not found."""
        self.mock_session.run.return_value.single.return_value = None
        
        profile = self.repository.get_player_profile("nonexistent_player")
        
        self.assertIsNone(profile)
    
    def test_update_player_profile_success(self):
        """Test successful player profile update."""
        mock_record = MagicMock()
        self.mock_session.run.return_value.single.return_value = mock_record
        
        result = self.repository.update_player_profile(self.test_profile)
        
        self.assertTrue(result)
        self.mock_session.run.assert_called_once()
    
    def test_update_player_profile_not_found(self):
        """Test player profile update when profile not found."""
        self.mock_session.run.return_value.single.return_value = None
        
        result = self.repository.update_player_profile(self.test_profile)
        
        self.assertFalse(result)
    
    def test_delete_player_profile_success(self):
        """Test successful player profile deletion."""
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = 1
        self.mock_session.run.return_value.single.return_value = mock_record
        
        result = self.repository.delete_player_profile("test_player_123")
        
        self.assertTrue(result)
        self.mock_session.run.assert_called_once()
    
    def test_delete_player_profile_not_found(self):
        """Test player profile deletion when profile not found."""
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = 0
        self.mock_session.run.return_value.single.return_value = mock_record
        
        result = self.repository.delete_player_profile("nonexistent_player")
        
        self.assertFalse(result)
    
    def test_username_exists_true(self):
        """Test username existence check when username exists."""
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = True
        self.mock_session.run.return_value.single.return_value = mock_record
        
        exists = self.repository.username_exists("testuser")
        
        self.assertTrue(exists)
    
    def test_username_exists_false(self):
        """Test username existence check when username doesn't exist."""
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = False
        self.mock_session.run.return_value.single.return_value = mock_record
        
        exists = self.repository.username_exists("nonexistent_user")
        
        self.assertFalse(exists)
    
    def test_email_exists_true(self):
        """Test email existence check when email exists."""
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = True
        self.mock_session.run.return_value.single.return_value = mock_record
        
        exists = self.repository.email_exists("test@example.com")
        
        self.assertTrue(exists)
    
    def test_email_exists_false(self):
        """Test email existence check when email doesn't exist."""
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = False
        self.mock_session.run.return_value.single.return_value = mock_record
        
        exists = self.repository.email_exists("nonexistent@example.com")
        
        self.assertFalse(exists)
    
    def test_list_active_players(self):
        """Test listing active players."""
        mock_records = [
            {"player_id": "player_1"},
            {"player_id": "player_2"}
        ]
        self.mock_session.run.return_value = mock_records
        
        # Mock get_player_profile calls
        with patch.object(self.repository, 'get_player_profile') as mock_get:
            mock_profile_1 = Mock()
            mock_profile_2 = Mock()
            mock_get.side_effect = [mock_profile_1, mock_profile_2]
            
            profiles = self.repository.list_active_players(limit=10)
            
            self.assertEqual(len(profiles), 2)
            self.assertEqual(profiles[0], mock_profile_1)
            self.assertEqual(profiles[1], mock_profile_2)
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with patch.object(self.repository, 'connect') as mock_connect, \
             patch.object(self.repository, 'disconnect') as mock_disconnect:
            
            with self.repository:
                pass
            
            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()


class TestPlayerProfileValidation(unittest.TestCase):
    """Test PlayerProfile model validation."""
    
    def test_valid_player_profile_creation(self):
        """Test creating a valid player profile."""
        profile = PlayerProfile(
            player_id="player_123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now()
        )
        
        self.assertEqual(profile.player_id, "player_123")
        self.assertEqual(profile.username, "testuser")
        self.assertEqual(profile.email, "test@example.com")
        self.assertTrue(profile.is_active)
        self.assertEqual(len(profile.characters), 0)
    
    def test_player_profile_validation_empty_id(self):
        """Test player profile validation with empty ID."""
        with self.assertRaises(ValueError):
            PlayerProfile(
                player_id="",
                username="testuser",
                email="test@example.com",
                created_at=datetime.now()
            )
    
    def test_player_profile_validation_short_username(self):
        """Test player profile validation with short username."""
        with self.assertRaises(ValueError):
            PlayerProfile(
                player_id="player_123",
                username="ab",  # Too short
                email="test@example.com",
                created_at=datetime.now()
            )
    
    def test_player_profile_validation_invalid_email(self):
        """Test player profile validation with invalid email."""
        with self.assertRaises(ValueError):
            PlayerProfile(
                player_id="player_123",
                username="testuser",
                email="invalid_email",  # No @ symbol
                created_at=datetime.now()
            )
    
    def test_player_profile_character_limit(self):
        """Test player profile character limit enforcement."""
        profile = PlayerProfile(
            player_id="player_123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now()
        )
        
        # Add maximum allowed characters
        for i in range(5):
            profile.add_character(f"char_{i}")
        
        # Try to add one more (should fail)
        with self.assertRaises(ValueError):
            profile.add_character("char_6")
    
    def test_player_profile_character_management(self):
        """Test player profile character management methods."""
        profile = PlayerProfile(
            player_id="player_123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now()
        )
        
        # Add character
        profile.add_character("char_1")
        self.assertIn("char_1", profile.characters)
        
        # Set active session
        profile.set_active_session("char_1", "session_1")
        self.assertEqual(profile.get_active_session("char_1"), "session_1")
        
        # Remove character
        profile.remove_character("char_1")
        self.assertNotIn("char_1", profile.characters)
        self.assertIsNone(profile.get_active_session("char_1"))
    
    def test_therapeutic_preferences_validation(self):
        """Test therapeutic preferences validation."""
        # Valid preferences
        prefs = TherapeuticPreferences(
            intensity_level=IntensityLevel.MEDIUM,
            session_duration_preference=45
        )
        self.assertEqual(prefs.intensity_level, IntensityLevel.MEDIUM)
        self.assertEqual(prefs.session_duration_preference, 45)
        
        # Invalid session duration (too short)
        with self.assertRaises(ValueError):
            TherapeuticPreferences(session_duration_preference=5)
        
        # Invalid session duration (too long)
        with self.assertRaises(ValueError):
            TherapeuticPreferences(session_duration_preference=150)
    
    def test_privacy_settings_validation(self):
        """Test privacy settings validation."""
        # Valid privacy settings
        privacy = PrivacySettings(data_retention_period_days=180)
        self.assertEqual(privacy.data_retention_period_days, 180)
        
        # Invalid retention period (too short)
        with self.assertRaises(ValueError):
            PrivacySettings(data_retention_period_days=20)
        
        # Invalid retention period (too long)
        with self.assertRaises(ValueError):
            PrivacySettings(data_retention_period_days=3000)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    @patch('src.player_experience.database.player_profile_schema.PlayerProfileSchemaManager')
    def test_setup_player_profile_schema_success(self, mock_manager_class):
        """Test successful schema setup utility function."""
        mock_manager = Mock()
        mock_manager.setup_player_profile_schema.return_value = True
        mock_manager_class.return_value.__enter__.return_value = mock_manager
        mock_manager_class.return_value.__exit__.return_value = None
        
        result = setup_player_profile_schema()
        
        self.assertTrue(result)
        mock_manager.setup_player_profile_schema.assert_called_once()
    
    @patch('src.player_experience.database.player_profile_schema.PlayerProfileSchemaManager')
    def test_setup_player_profile_schema_failure(self, mock_manager_class):
        """Test schema setup utility function failure."""
        mock_manager_class.side_effect = Exception("Setup failed")
        
        result = setup_player_profile_schema()
        
        self.assertFalse(result)
    
    @patch('src.player_experience.database.player_profile_repository.PlayerProfileRepository')
    def test_create_player_profile_repository(self, mock_repo_class):
        """Test repository creation utility function."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        repo = create_player_profile_repository()
        
        self.assertEqual(repo, mock_repo)
        mock_repo.connect.assert_called_once()


if __name__ == '__main__':
    unittest.main()