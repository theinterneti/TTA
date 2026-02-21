"""

# Logseq: [[TTA.dev/Tests/Test_player_profile_manager]]
Unit tests for PlayerProfileManager service.

Tests CRUD operations, privacy controls, and data access restrictions
according to requirements 7.1, 7.2, 7.3.
"""

import unittest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

from src.player_experience.database.player_profile_repository import (
    PlayerProfileRepository,
    PlayerProfileRepositoryError,
)

# Import the classes we're testing
from src.player_experience.managers.player_profile_manager import (
    DataAccessRestrictedError,
    PlayerProfileManager,
    PlayerProfileManagerError,
    create_player_profile_manager,
)
from src.player_experience.models.enums import IntensityLevel, TherapeuticApproach
from src.player_experience.models.player import (
    PlayerProfile,
    PrivacySettings,
    TherapeuticPreferences,
)


class TestPlayerProfileManager(unittest.TestCase):
    """Test cases for PlayerProfileManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = Mock(spec=PlayerProfileRepository)
        self.manager = PlayerProfileManager(self.mock_repository)

        # Test data
        self.test_username = "testuser123"
        self.test_email = "test@example.com"
        self.test_player_id = str(uuid.uuid4())

        self.test_therapeutic_prefs = TherapeuticPreferences(
            intensity_level=IntensityLevel.MEDIUM,
            preferred_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.MINDFULNESS,
            ],
            trigger_warnings=["violence", "abandonment"],
            comfort_topics=["nature", "family"],
            avoid_topics=["death", "trauma"],
        )

        self.test_privacy_settings = PrivacySettings(
            data_collection_consent=True,
            research_participation_consent=False,
            progress_sharing_enabled=True,
            data_retention_period_days=365,
        )

        self.test_profile = PlayerProfile(
            player_id=self.test_player_id,
            username=self.test_username,
            email=self.test_email,
            created_at=datetime.now(),
            therapeutic_preferences=self.test_therapeutic_prefs,
            privacy_settings=self.test_privacy_settings,
        )

    def test_create_player_profile_success(self):
        """Test successful player profile creation."""
        # Setup mocks
        self.mock_repository.username_exists.return_value = False
        self.mock_repository.email_exists.return_value = False
        self.mock_repository.create_player_profile.return_value = True

        # Execute
        with patch(
            "src.player_experience.managers.player_profile_manager.uuid.uuid4"
        ) as mock_uuid:
            mock_uuid.return_value = uuid.UUID(self.test_player_id)

            profile = self.manager.create_player_profile(
                username=self.test_username,
                email=self.test_email,
                therapeutic_preferences=self.test_therapeutic_prefs,
                privacy_settings=self.test_privacy_settings,
            )

        # Verify
        self.assertIsInstance(profile, PlayerProfile)
        self.assertEqual(profile.username, self.test_username)
        self.assertEqual(profile.email, self.test_email)
        self.assertEqual(profile.player_id, self.test_player_id)

        # Verify repository calls
        self.mock_repository.username_exists.assert_called_once_with(self.test_username)
        self.mock_repository.email_exists.assert_called_once_with(self.test_email)
        self.mock_repository.create_player_profile.assert_called_once()

    def test_create_player_profile_duplicate_username(self):
        """Test player profile creation with duplicate username."""
        # Setup mocks
        self.mock_repository.username_exists.return_value = True

        # Execute and verify
        with self.assertRaises(PlayerProfileManagerError) as context:
            self.manager.create_player_profile(
                username=self.test_username, email=self.test_email
            )

        self.assertIn("already exists", str(context.exception))

    def test_create_player_profile_duplicate_email(self):
        """Test player profile creation with duplicate email."""
        # Setup mocks
        self.mock_repository.username_exists.return_value = False
        self.mock_repository.email_exists.return_value = True

        # Execute and verify
        with self.assertRaises(PlayerProfileManagerError) as context:
            self.manager.create_player_profile(
                username=self.test_username, email=self.test_email
            )

        self.assertIn("already exists", str(context.exception))

    def test_create_player_profile_invalid_username(self):
        """Test player profile creation with invalid username."""
        invalid_usernames = ["ab", "", "user@name", "user name", "a" * 51]

        for invalid_username in invalid_usernames:
            with self.subTest(username=invalid_username):
                with self.assertRaises(PlayerProfileManagerError):
                    self.manager.create_player_profile(
                        username=invalid_username, email=self.test_email
                    )

    def test_create_player_profile_invalid_email(self):
        """Test player profile creation with invalid email."""
        invalid_emails = ["", "invalid", "invalid@", "@invalid.com", "invalid.com"]

        for invalid_email in invalid_emails:
            with self.subTest(email=invalid_email):
                with self.assertRaises(PlayerProfileManagerError):
                    self.manager.create_player_profile(
                        username=self.test_username, email=invalid_email
                    )

    def test_create_player_profile_invalid_privacy_settings(self):
        """Test player profile creation with invalid privacy settings."""
        # Test invalid data retention period (too short)
        with self.assertRaises(ValueError):
            PrivacySettings(data_retention_period_days=15)

        # Test invalid data retention period (too long)
        with self.assertRaises(ValueError):
            PrivacySettings(data_retention_period_days=3000)

    def test_get_player_profile_success(self):
        """Test successful player profile retrieval."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = self.test_profile

        # Execute
        profile = self.manager.get_player_profile(
            self.test_player_id, self.test_player_id
        )

        # Verify
        self.assertIsInstance(profile, PlayerProfile)
        self.assertEqual(profile.player_id, self.test_player_id)
        self.mock_repository.get_player_profile.assert_called_once_with(
            self.test_player_id
        )

    def test_get_player_profile_not_found(self):
        """Test player profile retrieval when profile doesn't exist."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = None

        # Execute
        profile = self.manager.get_player_profile("nonexistent_id")

        # Verify
        self.assertIsNone(profile)

    def test_get_player_profile_privacy_filtering(self):
        """Test privacy filtering when accessed by different user."""
        # Setup profile with restricted privacy settings
        restricted_profile = PlayerProfile(
            player_id=self.test_player_id,
            username=self.test_username,
            email=self.test_email,
            created_at=datetime.now(),
            privacy_settings=PrivacySettings(progress_sharing_enabled=False),
        )

        self.mock_repository.get_player_profile.return_value = restricted_profile

        # Execute - access by different user
        other_user_id = str(uuid.uuid4())
        profile = self.manager.get_player_profile(self.test_player_id, other_user_id)

        # Verify privacy filtering applied
        self.assertEqual(profile.email, "***@***.***")
        self.assertEqual(profile.active_sessions, {})

    def test_get_player_profile_data_access_restricted(self):
        """Test data access restriction when consent is not given."""
        # Setup profile without data collection consent
        restricted_profile = PlayerProfile(
            player_id=self.test_player_id,
            username=self.test_username,
            email=self.test_email,
            created_at=datetime.now(),
            privacy_settings=PrivacySettings(data_collection_consent=False),
        )

        self.mock_repository.get_player_profile.return_value = restricted_profile

        # Execute and verify - access by different user should be restricted
        other_user_id = str(uuid.uuid4())
        with self.assertRaises(DataAccessRestrictedError):
            self.manager.get_player_profile(self.test_player_id, other_user_id)

        # But access by profile owner should work
        profile = self.manager.get_player_profile(
            self.test_player_id, self.test_player_id
        )
        self.assertIsNotNone(profile)

    def test_update_player_profile_success(self):
        """Test successful player profile update."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = self.test_profile
        self.mock_repository.update_player_profile.return_value = True

        # Execute
        updates = {"username": "newusername"}
        result = self.manager.update_player_profile(
            self.test_player_id, updates, self.test_player_id
        )

        # Verify
        self.assertTrue(result)
        self.mock_repository.update_player_profile.assert_called_once()

    def test_update_player_profile_not_found(self):
        """Test player profile update when profile doesn't exist."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = None

        # Execute and verify
        with self.assertRaises(PlayerProfileManagerError):
            self.manager.update_player_profile(
                "nonexistent_id", {"username": "newusername"}, "nonexistent_id"
            )

    def test_update_player_profile_unauthorized(self):
        """Test player profile update by unauthorized user."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = self.test_profile

        # Execute and verify
        other_user_id = str(uuid.uuid4())
        with self.assertRaises(DataAccessRestrictedError):
            self.manager.update_player_profile(
                self.test_player_id, {"username": "newusername"}, other_user_id
            )

    def test_update_player_profile_restricted_fields(self):
        """Test player profile update with restricted fields."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = self.test_profile

        # Execute and verify
        restricted_updates = {"player_id": "new_id", "created_at": datetime.now()}
        with self.assertRaises(DataAccessRestrictedError):
            self.manager.update_player_profile(
                self.test_player_id, restricted_updates, self.test_player_id
            )

    def test_delete_player_profile_success(self):
        """Test successful player profile deletion."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = self.test_profile
        self.mock_repository.delete_player_profile.return_value = True

        # Execute
        result = self.manager.delete_player_profile(
            self.test_player_id, self.test_player_id
        )

        # Verify
        self.assertTrue(result)
        self.mock_repository.delete_player_profile.assert_called_once_with(
            self.test_player_id
        )

    def test_delete_player_profile_not_found(self):
        """Test player profile deletion when profile doesn't exist."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = None

        # Execute
        result = self.manager.delete_player_profile("nonexistent_id", "nonexistent_id")

        # Verify
        self.assertFalse(result)

    def test_delete_player_profile_unauthorized(self):
        """Test player profile deletion by unauthorized user."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = self.test_profile

        # Execute and verify
        other_user_id = str(uuid.uuid4())
        with self.assertRaises(DataAccessRestrictedError):
            self.manager.delete_player_profile(self.test_player_id, other_user_id)

    def test_get_player_by_username(self):
        """Test player profile retrieval by username."""
        # Setup mocks
        self.mock_repository.get_player_by_username.return_value = self.test_profile
        self.mock_repository.get_player_profile.return_value = self.test_profile

        # Execute
        profile = self.manager.get_player_by_username(
            self.test_username, self.test_player_id
        )

        # Verify
        self.assertIsInstance(profile, PlayerProfile)
        self.assertEqual(profile.username, self.test_username)
        self.mock_repository.get_player_by_username.assert_called_once_with(
            self.test_username
        )

    def test_get_player_by_email(self):
        """Test player profile retrieval by email."""
        # Setup mocks
        self.mock_repository.get_player_by_email.return_value = self.test_profile
        self.mock_repository.get_player_profile.return_value = self.test_profile

        # Execute
        profile = self.manager.get_player_by_email(self.test_email, self.test_player_id)

        # Verify
        self.assertIsInstance(profile, PlayerProfile)
        self.assertEqual(profile.email, self.test_email)
        self.mock_repository.get_player_by_email.assert_called_once_with(
            self.test_email
        )

    def test_update_therapeutic_preferences(self):
        """Test therapeutic preferences update."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = self.test_profile
        self.mock_repository.update_player_profile.return_value = True

        # Execute
        new_prefs = TherapeuticPreferences(
            intensity_level=IntensityLevel.HIGH,
            preferred_approaches=[TherapeuticApproach.NARRATIVE_THERAPY],
        )

        result = self.manager.update_therapeutic_preferences(
            self.test_player_id, new_prefs, self.test_player_id
        )

        # Verify
        self.assertTrue(result)
        self.mock_repository.update_player_profile.assert_called_once()

    def test_update_privacy_settings(self):
        """Test privacy settings update."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = self.test_profile
        self.mock_repository.update_player_profile.return_value = True

        # Execute
        new_privacy = PrivacySettings(
            data_collection_consent=False, research_participation_consent=True
        )

        result = self.manager.update_privacy_settings(
            self.test_player_id, new_privacy, self.test_player_id
        )

        # Verify
        self.assertTrue(result)
        self.mock_repository.update_player_profile.assert_called_once()

    def test_update_privacy_settings_invalid(self):
        """Test privacy settings update with invalid settings."""
        # Execute and verify - the validation happens in the model constructor
        with self.assertRaises(ValueError):
            PrivacySettings(data_retention_period_days=15)

    def test_export_player_data_success(self):
        """Test successful player data export."""
        # Setup mocks
        self.mock_repository.get_player_profile.return_value = self.test_profile

        # Execute
        export_data = self.manager.export_player_data(
            self.test_player_id, self.test_player_id
        )

        # Verify
        self.assertIsInstance(export_data, dict)
        self.assertIn("player_profile", export_data)
        self.assertIn("therapeutic_preferences", export_data)
        self.assertIn("privacy_settings", export_data)
        self.assertIn("progress_summary", export_data)
        self.assertIn("export_metadata", export_data)

        # Verify data content
        self.assertEqual(
            export_data["player_profile"]["player_id"], self.test_player_id
        )
        self.assertEqual(export_data["player_profile"]["username"], self.test_username)
        self.assertEqual(export_data["player_profile"]["email"], self.test_email)

    def test_export_player_data_unauthorized(self):
        """Test player data export by unauthorized user."""
        # Setup profile without consent
        restricted_profile = PlayerProfile(
            player_id=self.test_player_id,
            username=self.test_username,
            email=self.test_email,
            created_at=datetime.now(),
            privacy_settings=PrivacySettings(data_collection_consent=False),
        )

        self.mock_repository.get_player_profile.return_value = restricted_profile

        # Execute and verify
        other_user_id = str(uuid.uuid4())
        with self.assertRaises(PlayerProfileManagerError):
            self.manager.export_player_data(self.test_player_id, other_user_id)

    def test_get_access_log_success(self):
        """Test access log retrieval."""
        # Add some log entries
        self.manager._log_access(self.test_player_id, "CREATE", "Profile created")
        self.manager._log_access(self.test_player_id, "READ", "Profile accessed")

        # Execute
        access_log = self.manager.get_access_log(
            self.test_player_id, self.test_player_id
        )

        # Verify
        self.assertEqual(len(access_log), 2)
        self.assertEqual(access_log[0]["operation"], "CREATE")
        self.assertEqual(access_log[1]["operation"], "READ")

    def test_get_access_log_unauthorized(self):
        """Test access log retrieval by unauthorized user."""
        # Execute and verify
        other_user_id = str(uuid.uuid4())
        with self.assertRaises(DataAccessRestrictedError):
            self.manager.get_access_log(self.test_player_id, other_user_id)

    def test_repository_error_handling(self):
        """Test handling of repository errors."""
        # Setup mock to raise repository error
        self.mock_repository.get_player_profile.side_effect = (
            PlayerProfileRepositoryError("Database error")
        )

        # Execute and verify
        with self.assertRaises(PlayerProfileManagerError):
            self.manager.get_player_profile(self.test_player_id)

    def test_create_player_profile_manager_utility(self):
        """Test utility function for creating manager."""
        mock_repo = Mock(spec=PlayerProfileRepository)
        manager = create_player_profile_manager(mock_repo)

        self.assertIsInstance(manager, PlayerProfileManager)
        self.assertEqual(manager.repository, mock_repo)


class TestPlayerProfileManagerIntegration(unittest.TestCase):
    """Integration tests for PlayerProfileManager with real repository."""

    def setUp(self):
        """Set up integration test fixtures."""
        # Create a mock repository that behaves more realistically
        self.mock_repository = Mock(spec=PlayerProfileRepository)
        self.manager = PlayerProfileManager(self.mock_repository)

        # Test data
        self.test_username = "integrationuser"
        self.test_email = "integration@example.com"
        self.test_player_id = str(uuid.uuid4())

    def test_full_profile_lifecycle(self):
        """Test complete profile lifecycle: create, read, update, delete."""
        # Setup repository behavior
        self.mock_repository.username_exists.return_value = False
        self.mock_repository.email_exists.return_value = False
        self.mock_repository.create_player_profile.return_value = True
        self.mock_repository.update_player_profile.return_value = True
        self.mock_repository.delete_player_profile.return_value = True

        # Create profile
        with patch(
            "src.player_experience.managers.player_profile_manager.uuid.uuid4"
        ) as mock_uuid:
            mock_uuid.return_value = uuid.UUID(self.test_player_id)

            profile = self.manager.create_player_profile(
                username=self.test_username, email=self.test_email
            )

        self.assertIsNotNone(profile)
        self.assertEqual(profile.player_id, self.test_player_id)

        # Setup for read
        self.mock_repository.get_player_profile.return_value = profile

        # Read profile
        retrieved_profile = self.manager.get_player_profile(
            self.test_player_id, self.test_player_id
        )
        self.assertEqual(retrieved_profile.username, self.test_username)

        # Update profile
        updates = {"username": "updateduser"}
        update_result = self.manager.update_player_profile(
            self.test_player_id, updates, self.test_player_id
        )
        self.assertTrue(update_result)

        # Delete profile
        delete_result = self.manager.delete_player_profile(
            self.test_player_id, self.test_player_id
        )
        self.assertTrue(delete_result)

    def test_privacy_controls_enforcement(self):
        """Test that privacy controls are properly enforced."""
        # Create profile with strict privacy settings
        strict_privacy = PrivacySettings(
            data_collection_consent=False,
            progress_sharing_enabled=False,
            anonymous_analytics_enabled=False,
        )

        profile = PlayerProfile(
            player_id=self.test_player_id,
            username=self.test_username,
            email=self.test_email,
            created_at=datetime.now(),
            privacy_settings=strict_privacy,
        )

        self.mock_repository.get_player_profile.return_value = profile

        # Test that external access is restricted
        other_user_id = str(uuid.uuid4())
        with self.assertRaises(DataAccessRestrictedError):
            self.manager.get_player_profile(self.test_player_id, other_user_id)

        # Test that owner access still works
        owner_profile = self.manager.get_player_profile(
            self.test_player_id, self.test_player_id
        )
        self.assertIsNotNone(owner_profile)


if __name__ == "__main__":
    unittest.main()
