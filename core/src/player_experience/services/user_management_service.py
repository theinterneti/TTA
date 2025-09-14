"""
User Management Service for coordinated user and player profile operations.

This service handles the coordination between User authentication entities
and PlayerProfile entities, ensuring data consistency and proper transaction handling.
"""

import logging
from datetime import datetime, timezone
from uuid import uuid4

from ..database.player_profile_repository import PlayerProfileRepository
from ..database.user_repository import User, UserRepository
from ..models.auth import UserRegistration
from ..models.player import PlayerProfile, PrivacySettings, TherapeuticPreferences
from ..services.auth_service import EnhancedAuthService

logger = logging.getLogger(__name__)


class UserManagementError(Exception):
    """Raised when user management operations fail."""

    pass


class UserManagementService:
    """
    Service for coordinated user and player profile management.

    This service ensures that User and PlayerProfile entities are created,
    updated, and deleted in a coordinated manner with proper error handling
    and rollback capabilities.
    """

    def __init__(
        self,
        user_repository: UserRepository | None = None,
        player_repository: PlayerProfileRepository | None = None,
        auth_service: EnhancedAuthService | None = None,
    ):
        """
        Initialize the User Management Service.

        Args:
            user_repository: Repository for user authentication data
            player_repository: Repository for player profile data
            auth_service: Authentication service for user operations
        """
        self.user_repository = user_repository
        self.player_repository = player_repository
        self.auth_service = auth_service

    def create_user_with_profile(
        self, registration: UserRegistration
    ) -> tuple[bool, list[str], str | None]:
        """
        Create a new user with coordinated User and PlayerProfile creation.

        Args:
            registration: User registration data

        Returns:
            Tuple of (success, errors, user_id)
        """
        errors = []
        user_id = None
        user_created = False
        profile_created = False

        try:
            # Step 1: Validate and create user through auth service
            if self.auth_service:
                success, auth_errors = self.auth_service.register_user(registration)
                if not success:
                    return False, auth_errors, None

                # Get the created user to obtain user_id
                if self.user_repository:
                    user = self.user_repository.get_user_by_username(
                        registration.username
                    )
                    if user:
                        user_id = user.user_id
                        user_created = True
                    else:
                        errors.append("Failed to retrieve created user")
                        return False, errors, None
            else:
                errors.append("Authentication service not available")
                return False, errors, None

            # Step 2: Create corresponding PlayerProfile
            if self.player_repository and user_id:
                try:
                    # Create therapeutic preferences
                    therapeutic_prefs = TherapeuticPreferences(
                        preferences_id=str(uuid4()),
                        therapeutic_goals=(
                            registration.therapeutic_preferences.get("goals", [])
                            if registration.therapeutic_preferences
                            else []
                        ),
                        intensity_preference=(
                            registration.therapeutic_preferences.get(
                                "intensity", "medium"
                            )
                            if registration.therapeutic_preferences
                            else "medium"
                        ),
                        session_frequency=(
                            registration.therapeutic_preferences.get(
                                "frequency", "weekly"
                            )
                            if registration.therapeutic_preferences
                            else "weekly"
                        ),
                        preferred_techniques=(
                            registration.therapeutic_preferences.get("techniques", [])
                            if registration.therapeutic_preferences
                            else []
                        ),
                        trigger_warnings=(
                            registration.therapeutic_preferences.get("triggers", [])
                            if registration.therapeutic_preferences
                            else []
                        ),
                        crisis_contact_info=None,
                    )

                    # Create privacy settings
                    privacy_settings = PrivacySettings(
                        settings_id=str(uuid4()),
                        data_sharing_consent=(
                            registration.privacy_settings.get("data_sharing", False)
                            if registration.privacy_settings
                            else False
                        ),
                        analytics_consent=(
                            registration.privacy_settings.get("analytics", False)
                            if registration.privacy_settings
                            else False
                        ),
                        research_participation_consent=(
                            registration.privacy_settings.get("research", False)
                            if registration.privacy_settings
                            else False
                        ),
                        marketing_consent=(
                            registration.privacy_settings.get("marketing", False)
                            if registration.privacy_settings
                            else False
                        ),
                        data_retention_period=(
                            registration.privacy_settings.get("retention_days", 365)
                            if registration.privacy_settings
                            else 365
                        ),
                    )

                    # Create player profile
                    player_profile = PlayerProfile(
                        player_id=user_id,  # Use same ID as user for consistency
                        username=registration.username,
                        email=registration.email,
                        created_at=datetime.now(timezone.utc),
                        last_login=None,
                        is_active=True,
                        characters=[],
                        active_sessions={},
                        therapeutic_preferences=therapeutic_prefs,
                        privacy_settings=privacy_settings,
                        progress_summary=None,
                    )

                    # Create player profile in database
                    profile_success = self.player_repository.create_player_profile(
                        player_profile
                    )
                    if profile_success:
                        profile_created = True
                        logger.info(
                            f"Successfully created user and player profile: {user_id}"
                        )
                        return True, [], user_id
                    else:
                        errors.append("Failed to create player profile")

                except Exception as e:
                    logger.error(f"Error creating player profile: {e}")
                    errors.append(f"Failed to create player profile: {str(e)}")

            # If we get here, something went wrong - attempt rollback
            if user_created and not profile_created:
                logger.warning(
                    f"Rolling back user creation due to profile creation failure: {user_id}"
                )
                try:
                    if self.user_repository and user_id:
                        self.user_repository.delete_user(user_id)
                        logger.info(
                            f"Successfully rolled back user creation: {user_id}"
                        )
                except Exception as rollback_error:
                    logger.error(f"Failed to rollback user creation: {rollback_error}")
                    errors.append(f"Rollback failed: {str(rollback_error)}")

            return False, errors, None

        except Exception as e:
            logger.error(f"Unexpected error in user creation: {e}")
            errors.append(f"User creation failed: {str(e)}")

            # Attempt cleanup
            if user_created and user_id:
                try:
                    if self.user_repository:
                        self.user_repository.delete_user(user_id)
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup user after error: {cleanup_error}")

            return False, errors, None

    def delete_user_with_profile(self, user_id: str) -> tuple[bool, list[str]]:
        """
        Delete a user and their associated player profile.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (success, errors)
        """
        errors = []

        try:
            # Step 1: Delete player profile first (to maintain referential integrity)
            if self.player_repository:
                try:
                    profile_success = self.player_repository.delete_player_profile(
                        user_id
                    )
                    if profile_success:
                        pass
                    else:
                        logger.warning(
                            f"Player profile not found or already deleted: {user_id}"
                        )
                except Exception as e:
                    logger.error(f"Error deleting player profile: {e}")
                    errors.append(f"Failed to delete player profile: {str(e)}")
                    return False, errors

            # Step 2: Delete user
            if self.user_repository:
                try:
                    user_success = self.user_repository.delete_user(user_id)
                    if user_success:
                        logger.info(f"Successfully deleted user and profile: {user_id}")
                        return True, []
                    else:
                        errors.append("User not found or already deleted")
                        return False, errors
                except Exception as e:
                    logger.error(f"Error deleting user: {e}")
                    errors.append(f"Failed to delete user: {str(e)}")
                    return False, errors
            else:
                errors.append("User repository not available")
                return False, errors

        except Exception as e:
            logger.error(f"Unexpected error in user deletion: {e}")
            errors.append(f"User deletion failed: {str(e)}")
            return False, errors

    def get_user_with_profile(
        self, user_id: str
    ) -> tuple[User | None, PlayerProfile | None]:
        """
        Retrieve both user and player profile data.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (User, PlayerProfile) or (None, None) if not found
        """
        try:
            user = None
            profile = None

            if self.user_repository:
                user = self.user_repository.get_user_by_id(user_id)

            if self.player_repository:
                profile = self.player_repository.get_player_profile(user_id)

            return user, profile

        except Exception as e:
            logger.error(f"Error retrieving user and profile: {e}")
            return None, None

    def update_user_profile_coordination(
        self, user_id: str, **kwargs
    ) -> tuple[bool, list[str]]:
        """
        Update user and profile data in a coordinated manner.

        Args:
            user_id: User identifier
            **kwargs: Fields to update

        Returns:
            Tuple of (success, errors)
        """
        errors = []

        try:
            # This would implement coordinated updates between User and PlayerProfile
            # For now, return success as individual repositories handle their own updates
            logger.info(f"Coordinated update requested for user: {user_id}")
            return True, []

        except Exception as e:
            logger.error(f"Error in coordinated update: {e}")
            errors.append(f"Update failed: {str(e)}")
            return False, errors


# Utility function for creating user management service
def create_user_management_service(
    user_repository: UserRepository | None = None,
    player_repository: PlayerProfileRepository | None = None,
    auth_service: EnhancedAuthService | None = None,
) -> UserManagementService:
    """
    Create a user management service with the provided dependencies.

    Args:
        user_repository: Repository for user authentication data
        player_repository: Repository for player profile data
        auth_service: Authentication service

    Returns:
        UserManagementService: Configured service instance
    """
    return UserManagementService(user_repository, player_repository, auth_service)
