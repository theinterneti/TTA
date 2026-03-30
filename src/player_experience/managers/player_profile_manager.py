"""

# Logseq: [[TTA.dev/Player_experience/Managers/Player_profile_manager]]
Player Profile Manager service.

This module provides business logic for player profile management,
including CRUD operations, privacy controls, and data access restrictions.
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Any

from ..database.player_profile_repository import (
    PlayerProfileRepository,
    PlayerProfileRepositoryError,
)
from ..models.player import (
    PlayerProfile,
    PrivacySettings,
    ProgressSummary,
    TherapeuticPreferences,
)

logger = logging.getLogger(__name__)


class PlayerProfileManagerError(Exception):
    """Raised when player profile manager operations fail."""

    pass


class PrivacyViolationError(PlayerProfileManagerError):
    """Raised when an operation violates privacy settings."""

    pass


class DataAccessRestrictedError(PlayerProfileManagerError):
    """Raised when data access is restricted by privacy settings."""

    pass


class PlayerProfileManager:
    """
    Service for managing player profiles with privacy controls and data access restrictions.

    This class provides high-level business logic for player profile operations,
    enforcing privacy settings and data access controls according to requirements 7.1, 7.2, 7.3.
    """

    def __init__(self, repository: PlayerProfileRepository):
        """
        Initialize Player Profile Manager.

        Args:
            repository: PlayerProfileRepository instance for data access
        """
        self.repository = repository
        self._access_log: list[dict[str, Any]] = []

    def create_player_profile(
        self,
        username: str,
        email: str,
        therapeutic_preferences: TherapeuticPreferences | None = None,
        privacy_settings: PrivacySettings | None = None,
        player_id: str | None = None,
    ) -> PlayerProfile:
        """
        Create a new player profile with validation and privacy controls.

        Args:
            username: Unique username for the player
            email: Player's email address
            therapeutic_preferences: Optional therapeutic preferences
            privacy_settings: Optional privacy settings

        Returns:
            PlayerProfile: Created player profile

        Raises:
            PlayerProfileManagerError: If profile creation fails
            PrivacyViolationError: If privacy requirements are not met
        """
        try:
            logger.info(
                f"📝 Creating player profile for username={username}, email={email}"
            )

            # Validate input data
            logger.debug(f"  Validating username: {username}")
            self._validate_username(username)
            logger.debug(f"  Validating email: {email}")
            self._validate_email(email)

            # Check for existing username/email
            logger.debug(f"  Checking if username exists: {username}")
            if self.repository.username_exists(username):
                raise PlayerProfileManagerError(f"Username '{username}' already exists")

            logger.debug(f"  Checking if email exists: {email}")
            if self.repository.email_exists(email):
                raise PlayerProfileManagerError(f"Email '{email}' already exists")

            # Generate unique player ID (allow external override for E2E determinism)
            player_id = player_id or self._generate_player_id()
            logger.debug(f"  Generated player_id: {player_id}")

            # Use defaults if not provided
            if therapeutic_preferences is None:
                therapeutic_preferences = TherapeuticPreferences()

            if privacy_settings is None:
                privacy_settings = PrivacySettings()

            # Validate privacy settings compliance
            logger.debug("  Validating privacy compliance")
            self._validate_privacy_compliance(privacy_settings)

            # Create player profile
            logger.debug("  Creating PlayerProfile object")
            profile = PlayerProfile(
                player_id=player_id,
                username=username,
                email=email,
                created_at=datetime.now(),
                therapeutic_preferences=therapeutic_preferences,
                privacy_settings=privacy_settings,
                progress_summary=ProgressSummary(),
            )

            # Store in repository
            logger.debug("  Storing profile in repository")
            success = self.repository.create_player_profile(profile)
            if not success:
                raise PlayerProfileManagerError(
                    "Failed to create player profile in database"
                )

            # Log access for audit
            self._log_access(player_id, "CREATE", "Player profile created")

            logger.info(
                f"✅ Created player profile: {player_id} (username: {username})"
            )
            return profile

        except PlayerProfileRepositoryError as e:
            logger.error(
                f"❌ Repository error creating player profile: {e}", exc_info=True
            )
            raise PlayerProfileManagerError(
                f"Failed to create player profile: {e}"
            ) from e
        except Exception as e:
            logger.error(
                f"❌ Unexpected error creating player profile: {e}", exc_info=True
            )
            raise PlayerProfileManagerError(
                f"Unexpected error creating player profile: {e}"
            ) from e

    def get_player_profile(
        self, player_id: str, accessor_id: str | None = None
    ) -> PlayerProfile | None:
        """
        Retrieve a player profile with privacy controls.

        Args:
            player_id: Player identifier
            accessor_id: ID of the entity requesting access (for audit)

        Returns:
            Optional[PlayerProfile]: Player profile if found and accessible

        Raises:
            DataAccessRestrictedError: If access is restricted by privacy settings
        """
        try:
            logger.debug(
                f"🔍 Getting player profile for player_id={player_id}, accessor_id={accessor_id}"
            )

            # Retrieve profile from repository
            profile = self.repository.get_player_profile(player_id)
            if not profile:
                logger.debug(
                    f"✓ Player profile not found for player_id={player_id} (returning None)"
                )
                return None

            logger.debug(f"✓ Retrieved player profile for player_id={player_id}")

            # Check data access restrictions
            self._check_data_access_permissions(profile, accessor_id)

            # Apply privacy filtering
            filtered_profile = self._apply_privacy_filtering(profile, accessor_id)

            # Log access for audit
            self._log_access(
                player_id, "READ", f"Profile accessed by {accessor_id or 'system'}"
            )

            logger.debug(
                f"✓ Successfully retrieved and filtered player profile for player_id={player_id}"
            )
            return filtered_profile

        except PlayerProfileRepositoryError as e:
            logger.error(
                f"❌ Repository error retrieving player profile {player_id}: {e}",
                exc_info=True,
            )
            raise PlayerProfileManagerError(
                f"Failed to retrieve player profile: {e}"
            ) from e
        except DataAccessRestrictedError:
            # Re-raise privacy violations
            logger.warning(f"⚠️ Data access restricted for player_id={player_id}")
            raise
        except Exception as e:
            logger.error(
                f"❌ Unexpected error retrieving player profile {player_id}: {e}",
                exc_info=True,
            )
            raise PlayerProfileManagerError(
                f"Unexpected error retrieving player profile: {e}"
            ) from e

    def update_player_profile(
        self, player_id: str, updates: dict[str, Any], accessor_id: str | None = None
    ) -> bool:
        """
        Update a player profile with privacy controls and validation.

        Args:
            player_id: Player identifier
            updates: Dictionary of fields to update
            accessor_id: ID of the entity making the update

        Returns:
            bool: True if update was successful

        Raises:
            PlayerProfileManagerError: If update fails
            DataAccessRestrictedError: If update is restricted by privacy settings
        """
        try:
            # Retrieve existing profile
            profile = self.repository.get_player_profile(player_id)
            if not profile:
                raise PlayerProfileManagerError(
                    f"Player profile not found: {player_id}"
                )

            # Check update permissions
            self._check_update_permissions(profile, updates, accessor_id)

            # Validate updates
            self._validate_profile_updates(updates)

            # Apply updates to profile
            updated_profile = self._apply_profile_updates(profile, updates)

            # Store updated profile
            success = self.repository.update_player_profile(updated_profile)
            if not success:
                raise PlayerProfileManagerError(
                    "Failed to update player profile in database"
                )

            # Log access for audit
            self._log_access(
                player_id,
                "UPDATE",
                f"Profile updated by {accessor_id or 'system'}: {list(updates.keys())}",
            )

            logger.info(f"Updated player profile: {player_id}")
            return True

        except PlayerProfileRepositoryError as e:
            logger.error(f"Repository error updating player profile {player_id}: {e}")
            raise PlayerProfileManagerError(
                f"Failed to update player profile: {e}"
            ) from e
        except DataAccessRestrictedError:
            # Re-raise privacy violations
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating player profile {player_id}: {e}")
            raise PlayerProfileManagerError(
                f"Unexpected error updating player profile: {e}"
            ) from e

    def delete_player_profile(
        self, player_id: str, accessor_id: str | None = None
    ) -> bool:
        """
        Delete a player profile with privacy compliance (GDPR right to erasure).

        Args:
            player_id: Player identifier
            accessor_id: ID of the entity requesting deletion

        Returns:
            bool: True if deletion was successful

        Raises:
            PlayerProfileManagerError: If deletion fails
            DataAccessRestrictedError: If deletion is restricted
        """
        try:
            # Retrieve profile to check permissions
            profile = self.repository.get_player_profile(player_id)
            if not profile:
                logger.warning(f"Player profile not found for deletion: {player_id}")
                return False

            # Check deletion permissions
            self._check_deletion_permissions(profile, accessor_id)

            # Perform secure deletion
            success = self.repository.delete_player_profile(player_id)
            if not success:
                raise PlayerProfileManagerError(
                    "Failed to delete player profile from database"
                )

            # Log deletion for audit (before profile is gone)
            self._log_access(
                player_id, "DELETE", f"Profile deleted by {accessor_id or 'system'}"
            )

            logger.info(f"Deleted player profile: {player_id}")
            return True

        except PlayerProfileRepositoryError as e:
            logger.error(f"Repository error deleting player profile {player_id}: {e}")
            raise PlayerProfileManagerError(
                f"Failed to delete player profile: {e}"
            ) from e
        except DataAccessRestrictedError:
            # Re-raise privacy violations
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting player profile {player_id}: {e}")
            raise PlayerProfileManagerError(
                f"Unexpected error deleting player profile: {e}"
            ) from e

    def get_player_by_username(
        self, username: str, accessor_id: str | None = None
    ) -> PlayerProfile | None:
        """
        Retrieve a player profile by username with privacy controls.

        Args:
            username: Player username
            accessor_id: ID of the entity requesting access

        Returns:
            Optional[PlayerProfile]: Player profile if found and accessible
        """
        try:
            profile = self.repository.get_player_by_username(username)
            if not profile:
                return None

            return self.get_player_profile(profile.player_id, accessor_id)

        except Exception as e:
            logger.error(f"Error retrieving player by username {username}: {e}")
            raise PlayerProfileManagerError(
                f"Error retrieving player by username: {e}"
            ) from e

    def get_player_by_email(
        self, email: str, accessor_id: str | None = None
    ) -> PlayerProfile | None:
        """
        Retrieve a player profile by email with privacy controls.

        Args:
            email: Player email
            accessor_id: ID of the entity requesting access

        Returns:
            Optional[PlayerProfile]: Player profile if found and accessible
        """
        try:
            profile = self.repository.get_player_by_email(email)
            if not profile:
                return None

            return self.get_player_profile(profile.player_id, accessor_id)

        except Exception as e:
            logger.error(f"Error retrieving player by email: {e}")
            raise PlayerProfileManagerError(
                f"Error retrieving player by email: {e}"
            ) from e

    def update_therapeutic_preferences(
        self,
        player_id: str,
        preferences: TherapeuticPreferences,
        accessor_id: str | None = None,
    ) -> bool:
        """
        Update therapeutic preferences for a player.

        Args:
            player_id: Player identifier
            preferences: New therapeutic preferences
            accessor_id: ID of the entity making the update

        Returns:
            bool: True if update was successful
        """
        return self.update_player_profile(
            player_id, {"therapeutic_preferences": preferences}, accessor_id
        )

    def update_privacy_settings(
        self,
        player_id: str,
        privacy_settings: PrivacySettings,
        accessor_id: str | None = None,
    ) -> bool:
        """
        Update privacy settings for a player.

        Args:
            player_id: Player identifier
            privacy_settings: New privacy settings
            accessor_id: ID of the entity making the update

        Returns:
            bool: True if update was successful
        """
        # Validate privacy settings compliance
        self._validate_privacy_compliance(privacy_settings)

        return self.update_player_profile(
            player_id, {"privacy_settings": privacy_settings}, accessor_id
        )

    def export_player_data(
        self, player_id: str, accessor_id: str | None = None
    ) -> dict[str, Any]:
        """
        Export all player data for GDPR compliance.

        Args:
            player_id: Player identifier
            accessor_id: ID of the entity requesting export

        Returns:
            Dict[str, Any]: Complete player data in readable format

        Raises:
            DataAccessRestrictedError: If export is not allowed
        """
        try:
            profile = self.repository.get_player_profile(player_id)
            if not profile:
                raise PlayerProfileManagerError(
                    f"Player profile not found: {player_id}"
                )

            # Check export permissions (player must consent or be the accessor)
            if (
                accessor_id != player_id
                and not profile.privacy_settings.data_collection_consent
            ):
                raise DataAccessRestrictedError(
                    "Data export not permitted without consent"
                )

            # Create comprehensive data export
            export_data = {
                "player_profile": {
                    "player_id": profile.player_id,
                    "username": profile.username,
                    "email": profile.email,
                    "created_at": profile.created_at.isoformat(),
                    "last_login": (
                        profile.last_login.isoformat() if profile.last_login else None
                    ),
                    "is_active": profile.is_active,
                    "characters": profile.characters,
                    "active_sessions": profile.active_sessions,
                },
                "therapeutic_preferences": {
                    "intensity_level": profile.therapeutic_preferences.intensity_level.value,
                    "preferred_approaches": [
                        approach.value
                        for approach in profile.therapeutic_preferences.preferred_approaches
                    ],
                    "trigger_warnings": profile.therapeutic_preferences.trigger_warnings,
                    "comfort_topics": profile.therapeutic_preferences.comfort_topics,
                    "avoid_topics": profile.therapeutic_preferences.avoid_topics,
                    "session_duration_preference": profile.therapeutic_preferences.session_duration_preference,
                    "reminder_frequency": profile.therapeutic_preferences.reminder_frequency,
                    "crisis_contact_info": (
                        {
                            "primary_contact_name": (
                                profile.therapeutic_preferences.crisis_contact_info.primary_contact_name
                                if profile.therapeutic_preferences.crisis_contact_info
                                else None
                            ),
                            "primary_contact_phone": (
                                profile.therapeutic_preferences.crisis_contact_info.primary_contact_phone
                                if profile.therapeutic_preferences.crisis_contact_info
                                else None
                            ),
                            "therapist_name": (
                                profile.therapeutic_preferences.crisis_contact_info.therapist_name
                                if profile.therapeutic_preferences.crisis_contact_info
                                else None
                            ),
                            "therapist_phone": (
                                profile.therapeutic_preferences.crisis_contact_info.therapist_phone
                                if profile.therapeutic_preferences.crisis_contact_info
                                else None
                            ),
                            "crisis_hotline_preference": (
                                profile.therapeutic_preferences.crisis_contact_info.crisis_hotline_preference
                                if profile.therapeutic_preferences.crisis_contact_info
                                else None
                            ),
                            "emergency_instructions": (
                                profile.therapeutic_preferences.crisis_contact_info.emergency_instructions
                                if profile.therapeutic_preferences.crisis_contact_info
                                else None
                            ),
                        }
                        if profile.therapeutic_preferences.crisis_contact_info
                        else None
                    ),
                },
                "privacy_settings": {
                    "data_collection_consent": profile.privacy_settings.data_collection_consent,
                    "research_participation_consent": profile.privacy_settings.research_participation_consent,
                    "progress_sharing_enabled": profile.privacy_settings.progress_sharing_enabled,
                    "anonymous_analytics_enabled": profile.privacy_settings.anonymous_analytics_enabled,
                    "session_recording_enabled": profile.privacy_settings.session_recording_enabled,
                    "data_retention_period_days": profile.privacy_settings.data_retention_period_days,
                    "third_party_sharing_consent": profile.privacy_settings.third_party_sharing_consent,
                    "collect_interaction_patterns": profile.privacy_settings.collect_interaction_patterns,
                    "collect_emotional_responses": profile.privacy_settings.collect_emotional_responses,
                    "collect_therapeutic_outcomes": profile.privacy_settings.collect_therapeutic_outcomes,
                    "collect_usage_statistics": profile.privacy_settings.collect_usage_statistics,
                },
                "progress_summary": {
                    "total_sessions": profile.progress_summary.total_sessions,
                    "total_time_minutes": profile.progress_summary.total_time_minutes,
                    "milestones_achieved": profile.progress_summary.milestones_achieved,
                    "current_streak_days": profile.progress_summary.current_streak_days,
                    "longest_streak_days": profile.progress_summary.longest_streak_days,
                    "favorite_therapeutic_approach": (
                        profile.progress_summary.favorite_therapeutic_approach.value
                        if profile.progress_summary.favorite_therapeutic_approach
                        else None
                    ),
                    "most_effective_world_type": profile.progress_summary.most_effective_world_type,
                    "last_session_date": (
                        profile.progress_summary.last_session_date.isoformat()
                        if profile.progress_summary.last_session_date
                        else None
                    ),
                    "next_recommended_session": (
                        profile.progress_summary.next_recommended_session.isoformat()
                        if profile.progress_summary.next_recommended_session
                        else None
                    ),
                },
                "export_metadata": {
                    "export_date": datetime.now().isoformat(),
                    "export_requested_by": accessor_id,
                    "data_format_version": "1.0",
                },
            }

            # Log data export for audit
            self._log_access(
                player_id, "EXPORT", f"Data exported by {accessor_id or 'system'}"
            )

            return export_data

        except Exception as e:
            logger.error(f"Error exporting player data {player_id}: {e}")
            raise PlayerProfileManagerError(f"Error exporting player data: {e}") from e

    def get_access_log(
        self, player_id: str, accessor_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get access log for a player profile (for transparency).

        Args:
            player_id: Player identifier
            accessor_id: ID of the entity requesting access log

        Returns:
            List[Dict[str, Any]]: Access log entries

        Raises:
            DataAccessRestrictedError: If access log viewing is restricted
        """
        # Only allow player themselves or authorized entities to view access log
        if accessor_id != player_id:
            raise DataAccessRestrictedError(
                "Access log viewing restricted to profile owner"
            )

        # Filter access log for this player
        return [
            entry for entry in self._access_log if entry.get("player_id") == player_id
        ]

    # Private helper methods

    def _generate_player_id(self) -> str:
        """Generate a unique player ID."""
        return str(uuid.uuid4())

    def _validate_username(self, username: str) -> None:
        """Validate username format and constraints."""
        if not username or len(username) < 3:
            raise PlayerProfileManagerError(
                "Username must be at least 3 characters long"
            )

        if len(username) > 50:
            raise PlayerProfileManagerError("Username cannot exceed 50 characters")

        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            raise PlayerProfileManagerError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

    def _validate_email(self, email: str) -> None:
        """Validate email format."""
        if not email or "@" not in email:
            raise PlayerProfileManagerError("Valid email address is required")

        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise PlayerProfileManagerError("Invalid email format")

    def _validate_privacy_compliance(self, privacy_settings: PrivacySettings) -> None:
        """Validate privacy settings for compliance requirements."""
        # Ensure minimum data retention period
        if privacy_settings.data_retention_period_days < 30:
            raise PrivacyViolationError(
                "Data retention period must be at least 30 days"
            )

        # Ensure maximum data retention period
        if privacy_settings.data_retention_period_days > 2555:  # ~7 years
            raise PrivacyViolationError("Data retention period cannot exceed 7 years")

    def _check_data_access_permissions(
        self, profile: PlayerProfile, accessor_id: str | None
    ) -> None:
        """Check if data access is permitted based on privacy settings."""
        # If accessor is the profile owner, always allow
        if accessor_id == profile.player_id:
            return

        # Check if data collection consent is given
        if not profile.privacy_settings.data_collection_consent:
            raise DataAccessRestrictedError(
                "Data access restricted: no data collection consent"
            )

        # Additional checks can be added here based on specific access patterns

    def _check_update_permissions(
        self,
        profile: PlayerProfile,
        updates: dict[str, Any],
        accessor_id: str | None,
    ) -> None:
        """Check if profile updates are permitted."""
        # Only profile owner can update their profile
        if accessor_id != profile.player_id:
            raise DataAccessRestrictedError(
                "Profile updates restricted to profile owner"
            )

        # Check for restricted fields
        restricted_fields = {"player_id", "created_at"}
        for field in restricted_fields:
            if field in updates:
                raise DataAccessRestrictedError(f"Field '{field}' cannot be updated")

    def _check_deletion_permissions(
        self, profile: PlayerProfile, accessor_id: str | None
    ) -> None:
        """Check if profile deletion is permitted."""
        # Only profile owner can delete their profile
        if accessor_id != profile.player_id:
            raise DataAccessRestrictedError(
                "Profile deletion restricted to profile owner"
            )

    def _apply_privacy_filtering(
        self, profile: PlayerProfile, accessor_id: str | None
    ) -> PlayerProfile:
        """Apply privacy filtering to profile data based on settings and accessor."""
        # If accessor is the profile owner, return full profile
        if accessor_id == profile.player_id:
            return profile

        # Create filtered copy of profile
        return PlayerProfile(
            player_id=profile.player_id,
            username=profile.username,
            email=(
                profile.email
                if profile.privacy_settings.progress_sharing_enabled
                else "***@***.***"
            ),
            created_at=profile.created_at,
            therapeutic_preferences=profile.therapeutic_preferences,
            privacy_settings=profile.privacy_settings,
            characters=profile.characters,
            active_sessions=(
                profile.active_sessions
                if profile.privacy_settings.progress_sharing_enabled
                else {}
            ),
            progress_summary=(
                profile.progress_summary
                if profile.privacy_settings.progress_sharing_enabled
                else ProgressSummary()
            ),
            last_login=(
                profile.last_login
                if profile.privacy_settings.collect_usage_statistics
                else None
            ),
            is_active=profile.is_active,
        )

    def _validate_profile_updates(self, updates: dict[str, Any]) -> None:
        """Validate profile update data."""
        if "username" in updates:
            self._validate_username(updates["username"])

        if "email" in updates:
            self._validate_email(updates["email"])

        if "privacy_settings" in updates:
            self._validate_privacy_compliance(updates["privacy_settings"])

    def _apply_profile_updates(
        self, profile: PlayerProfile, updates: dict[str, Any]
    ) -> PlayerProfile:
        """Apply updates to a player profile."""
        # Create a copy of the profile
        return PlayerProfile(
            player_id=profile.player_id,
            username=updates.get("username", profile.username),
            email=updates.get("email", profile.email),
            created_at=profile.created_at,
            therapeutic_preferences=updates.get(
                "therapeutic_preferences", profile.therapeutic_preferences
            ),
            privacy_settings=updates.get("privacy_settings", profile.privacy_settings),
            characters=updates.get("characters", profile.characters),
            active_sessions=updates.get("active_sessions", profile.active_sessions),
            progress_summary=updates.get("progress_summary", profile.progress_summary),
            last_login=updates.get("last_login", profile.last_login),
            is_active=updates.get("is_active", profile.is_active),
        )

    def _log_access(self, player_id: str, operation: str, details: str) -> None:
        """Log access for audit purposes."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "player_id": player_id,
            "operation": operation,
            "details": details,
        }

        self._access_log.append(log_entry)

        # Keep only recent entries (last 1000)
        if len(self._access_log) > 1000:
            self._access_log = self._access_log[-1000:]


# Utility functions for player profile manager operations
def create_player_profile_manager(
    repository: PlayerProfileRepository,
) -> PlayerProfileManager:
    """
    Create a player profile manager with the given repository.

    Args:
        repository: PlayerProfileRepository instance

    Returns:
        PlayerProfileManager: Manager instance
    """
    return PlayerProfileManager(repository)
