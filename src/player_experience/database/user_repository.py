"""
User Repository for authentication database operations.

This module provides the UserRepository class that handles all database
operations for user authentication data, including CRUD operations and queries.
"""

import logging
from datetime import datetime
from uuid import uuid4

from ..models.auth import UserRole
from ..models.player import PlayerProfile
from .player_profile_repository import (
    PlayerProfileRepository,
    PlayerProfileRepositoryError,
)

logger = logging.getLogger(__name__)


class User:
    """User model for authentication."""

    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.PLAYER,
        created_at: datetime | None = None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.utcnow()
        self.is_active = True
        self.is_verified = True  # For simplicity, assume verified


class UserRepositoryError(Exception):
    """Raised when user repository operations fail."""

    pass


class UserRepository:
    """Repository for user authentication database operations."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "tta_dev_password_2024",
    ):
        """Initialize the User Repository."""
        self.uri = uri
        self.username = username
        self.password = password
        self.player_repo = PlayerProfileRepository(uri, username, password)
        self._connected = False
        logger.info("UserRepository initialized")

    def connect(self) -> None:
        """Connect to the database."""
        try:
            self.player_repo.connect()
            self._connected = True
            logger.info("UserRepository connected to database")
        except Exception as e:
            logger.error(f"Failed to connect UserRepository: {e}")
            raise UserRepositoryError(f"Failed to connect to database: {e}") from e

    def close(self) -> None:
        """Close database connection."""
        if self._connected:
            self.player_repo.close()
            self._connected = False
            logger.info("UserRepository connection closed")

    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.PLAYER,
    ) -> User:
        """
        Create a new user.

        Args:
            username: User's username
            email: User's email
            password_hash: Hashed password
            role: User's role

        Returns:
            User: Created user object

        Raises:
            UserRepositoryError: If user creation fails
        """
        if not self._connected:
            raise UserRepositoryError("Not connected to database")

        try:
            # Check if username or email already exists
            if self.username_exists(username):
                raise UserRepositoryError(f"Username '{username}' already exists")

            if self.email_exists(email):
                raise UserRepositoryError(f"Email '{email}' already exists")

            # Create player profile
            user_id = str(uuid4())
            from ..models.player import (
                PrivacySettings,
                ProgressSummary,
                TherapeuticPreferences,
            )

            player_profile = PlayerProfile(
                player_id=user_id,
                username=username,
                email=email,
                created_at=datetime.utcnow(),
                last_login=None,
                is_active=True,
                therapeutic_preferences=TherapeuticPreferences(),
                privacy_settings=PrivacySettings(),
                progress_summary=ProgressSummary(),
            )

            # Store authentication data in privacy settings metadata (temporary solution)
            # In production, this should be in a separate User authentication table
            player_profile.privacy_settings.password_hash = password_hash
            player_profile.privacy_settings.role = role.value

            # Save to database
            success = self.player_repo.create_player_profile(player_profile)
            if not success:
                raise UserRepositoryError("Failed to create player profile in database")

            # Return User object
            return User(
                user_id=player_profile.player_id,
                username=player_profile.username,
                email=player_profile.email,
                password_hash=password_hash,
                role=role,
                created_at=player_profile.created_at,
            )

        except PlayerProfileRepositoryError as e:
            logger.error(f"Error creating user {username}: {e}")
            raise UserRepositoryError(f"Error creating user: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error creating user {username}: {e}")
            raise UserRepositoryError(f"Unexpected error creating user: {e}") from e

    def get_user_by_username(self, username: str) -> User | None:
        """
        Get user by username.

        Args:
            username: Username to search for

        Returns:
            Optional[User]: User if found, None otherwise
        """
        if not self._connected:
            raise UserRepositoryError("Not connected to database")

        try:
            player_profile = self.player_repo.get_player_by_username(username)
            if not player_profile:
                return None

            # Extract auth data from privacy settings metadata
            password_hash = getattr(
                player_profile.privacy_settings, "password_hash", ""
            )
            role_str = getattr(player_profile.privacy_settings, "role", "player")

            # If no password hash found, this user wasn't created through the auth system
            if not password_hash:
                logger.warning(f"No password hash found for user {username}")
                return None

            role = (
                UserRole(role_str)
                if role_str in [r.value for r in UserRole]
                else UserRole.PLAYER
            )

            return User(
                user_id=player_profile.player_id,
                username=player_profile.username,
                email=player_profile.email,
                password_hash=password_hash,
                role=role,
                created_at=player_profile.created_at,
            )

        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {e}")
            return None

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email.

        Args:
            email: Email to search for

        Returns:
            Optional[User]: User if found, None otherwise
        """
        if not self._connected:
            raise UserRepositoryError("Not connected to database")

        try:
            player_profile = self.player_repo.get_player_by_email(email)
            if not player_profile:
                return None

            # Extract auth data from privacy settings metadata
            password_hash = getattr(
                player_profile.privacy_settings, "password_hash", ""
            )
            role_str = getattr(player_profile.privacy_settings, "role", "player")

            # If no password hash found, this user wasn't created through the auth system
            if not password_hash:
                logger.warning(f"No password hash found for user with email {email}")
                return None

            role = (
                UserRole(role_str)
                if role_str in [r.value for r in UserRole]
                else UserRole.PLAYER
            )

            return User(
                user_id=player_profile.player_id,
                username=player_profile.username,
                email=player_profile.email,
                password_hash=password_hash,
                role=role,
                created_at=player_profile.created_at,
            )

        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {e}")
            return None

    def username_exists(self, username: str) -> bool:
        """
        Check if username exists.

        Args:
            username: Username to check

        Returns:
            bool: True if username exists
        """
        if not self._connected:
            return False

        try:
            return self.player_repo.username_exists(username)
        except Exception as e:
            logger.error(f"Error checking username existence {username}: {e}")
            return False

    def email_exists(self, email: str) -> bool:
        """
        Check if email exists.

        Args:
            email: Email to check

        Returns:
            bool: True if email exists
        """
        if not self._connected:
            return False

        try:
            return self.player_repo.get_player_by_email(email) is not None
        except Exception as e:
            logger.error(f"Error checking email existence {email}: {e}")
            return False

    def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp.

        Args:
            user_id: User ID

        Returns:
            bool: True if successful
        """
        if not self._connected:
            return False

        try:
            player_profile = self.player_repo.get_player_profile(user_id)
            if player_profile:
                player_profile.last_login = datetime.utcnow()
                self.player_repo.update_player_profile(player_profile)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
            return False
