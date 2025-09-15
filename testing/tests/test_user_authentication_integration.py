"""
Integration tests for User Authentication system.

This module tests the complete authentication flow using Neo4j testcontainers
to verify database integration, user registration, login, and session management.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.player_experience.database.user_auth_schema import UserAuthSchemaManager
from src.player_experience.database.user_repository import User, UserRepository
from src.player_experience.models.auth import (
    MFAConfig,
    SecuritySettings,
    UserCredentials,
    UserRegistration,
    UserRole,
)
from src.player_experience.services.auth_service import EnhancedAuthService


@pytest.mark.neo4j
class TestUserAuthenticationIntegration:
    """Integration tests for user authentication with Neo4j."""

    @pytest.fixture(scope="class")
    def neo4j_auth_setup(self, neo4j_driver):
        """Set up Neo4j schema for authentication tests."""
        # Get connection details from the driver
        uri = neo4j_driver._pool._pool_config.address.host_port()
        uri = f"bolt://{uri[0]}:{uri[1]}"

        # Setup schema
        schema_manager = UserAuthSchemaManager(
            uri=uri, username="neo4j", password="testpassword"
        )
        schema_manager.connect()
        schema_manager.setup_user_auth_schema()

        yield schema_manager

        # Cleanup
        schema_manager.disconnect()

    @pytest.fixture
    def user_repository(self, neo4j_driver, neo4j_auth_setup):
        """Create a user repository connected to test Neo4j."""
        uri = neo4j_driver._pool._pool_config.address.host_port()
        uri = f"bolt://{uri[0]}:{uri[1]}"

        repository = UserRepository(uri=uri, username="neo4j", password="testpassword")
        repository.connect()

        yield repository

        repository.disconnect()

    @pytest.fixture
    def auth_service(self, user_repository):
        """Create an authentication service with database integration."""
        return EnhancedAuthService(
            secret_key="test-secret-key-for-integration-tests",
            user_repository=user_repository,
            security_settings=SecuritySettings(max_login_attempts=3),
            mfa_config=MFAConfig(enabled=False),  # Disable MFA for simpler tests
        )

    @pytest.fixture
    def sample_registration(self):
        """Create sample user registration data."""
        return UserRegistration(
            username="testuser_integration",
            email="test.integration@example.com",
            password="TestPassword123!",
            role=UserRole.PLAYER,
            therapeutic_preferences={"goals": ["anxiety"], "intensity": "medium"},
            privacy_settings={"data_sharing": True, "analytics": False},
        )

    def test_user_registration_flow(self, auth_service, sample_registration):
        """Test complete user registration flow with database persistence."""
        # Register user
        success, errors = auth_service.register_user(sample_registration)

        assert success is True
        assert len(errors) == 0

        # Verify user was created in database
        user = auth_service.user_repository.get_user_by_username(
            sample_registration.username
        )
        assert user is not None
        assert user.username == sample_registration.username
        assert user.email == sample_registration.email
        assert user.role == sample_registration.role
        assert user.email_verified is False
        assert user.account_status == "active"
        assert user.failed_login_attempts == 0

    def test_duplicate_registration_prevention(self, auth_service, sample_registration):
        """Test that duplicate usernames and emails are prevented."""
        # Register user first time
        success, errors = auth_service.register_user(sample_registration)
        assert success is True

        # Try to register with same username
        duplicate_username = UserRegistration(
            username=sample_registration.username,
            email="different@example.com",
            password="DifferentPassword123!",
            role=UserRole.PLAYER,
        )

        success, errors = auth_service.register_user(duplicate_username)
        assert success is False
        assert "Username already exists" in errors

        # Try to register with same email
        duplicate_email = UserRegistration(
            username="differentuser",
            email=sample_registration.email,
            password="DifferentPassword123!",
            role=UserRole.PLAYER,
        )

        success, errors = auth_service.register_user(duplicate_email)
        assert success is False
        assert "Email already exists" in errors

    def test_user_authentication_flow(self, auth_service, sample_registration):
        """Test complete user authentication flow."""
        # Register user first
        success, errors = auth_service.register_user(sample_registration)
        assert success is True

        # Test successful authentication
        credentials = UserCredentials(
            username=sample_registration.username, password=sample_registration.password
        )

        authenticated_user = auth_service.authenticate_user(credentials, "127.0.0.1")

        assert authenticated_user is not None
        assert authenticated_user.username == sample_registration.username
        assert authenticated_user.email == sample_registration.email
        assert authenticated_user.role == sample_registration.role
        assert authenticated_user.last_login is not None

        # Verify last_login was updated in database
        user = auth_service.user_repository.get_user_by_username(
            sample_registration.username
        )
        assert user.last_login is not None
        assert user.failed_login_attempts == 0

    def test_failed_authentication_tracking(self, auth_service, sample_registration):
        """Test failed authentication attempt tracking."""
        # Register user first
        success, errors = auth_service.register_user(sample_registration)
        assert success is True

        # Test failed authentication
        wrong_credentials = UserCredentials(
            username=sample_registration.username, password="WrongPassword123!"
        )

        # First failed attempt
        authenticated_user = auth_service.authenticate_user(
            wrong_credentials, "127.0.0.1"
        )
        assert authenticated_user is None

        # Check failed attempts were recorded in database
        user = auth_service.user_repository.get_user_by_username(
            sample_registration.username
        )
        assert user.failed_login_attempts == 1

        # Second failed attempt
        authenticated_user = auth_service.authenticate_user(
            wrong_credentials, "127.0.0.1"
        )
        assert authenticated_user is None

        user = auth_service.user_repository.get_user_by_username(
            sample_registration.username
        )
        assert user.failed_login_attempts == 2

        # Third failed attempt should lock account
        authenticated_user = auth_service.authenticate_user(
            wrong_credentials, "127.0.0.1"
        )
        assert authenticated_user is None

        user = auth_service.user_repository.get_user_by_username(
            sample_registration.username
        )
        assert user.failed_login_attempts == 3
        assert user.locked_until is not None

        # Account should be locked
        assert auth_service.is_account_locked(sample_registration.username) is True

    def test_account_lockout_and_unlock(self, auth_service, sample_registration):
        """Test account lockout and unlock functionality."""
        # Register user first
        success, errors = auth_service.register_user(sample_registration)
        assert success is True

        # Lock account by failing authentication multiple times
        wrong_credentials = UserCredentials(
            username=sample_registration.username, password="WrongPassword123!"
        )

        for _ in range(3):
            auth_service.authenticate_user(wrong_credentials, "127.0.0.1")

        # Verify account is locked
        assert auth_service.is_account_locked(sample_registration.username) is True

        # Even correct credentials should fail when locked
        correct_credentials = UserCredentials(
            username=sample_registration.username, password=sample_registration.password
        )

        with pytest.raises(Exception):  # Should raise AuthenticationError
            auth_service.authenticate_user(correct_credentials, "127.0.0.1")

        # Clear failed attempts (simulate admin unlock or time expiry)
        auth_service.clear_failed_login_attempts(sample_registration.username)

        # Verify account is unlocked
        assert auth_service.is_account_locked(sample_registration.username) is False

        # Should be able to authenticate now
        authenticated_user = auth_service.authenticate_user(
            correct_credentials, "127.0.0.1"
        )
        assert authenticated_user is not None

        # Verify database was updated
        user = auth_service.user_repository.get_user_by_username(
            sample_registration.username
        )
        assert user.failed_login_attempts == 0
        assert user.locked_until is None

    def test_user_repository_crud_operations(self, user_repository):
        """Test basic CRUD operations on user repository."""
        # Create user
        user = User(
            user_id=str(uuid4()),
            username="crud_test_user",
            email="crud@example.com",
            password_hash="$2b$12$hashed_password",
            role=UserRole.PLAYER,
            created_at=datetime.now(timezone.utc),
        )

        # Test create
        success = user_repository.create_user(user)
        assert success is True

        # Test read by ID
        retrieved_user = user_repository.get_user_by_id(user.user_id)
        assert retrieved_user is not None
        assert retrieved_user.username == user.username
        assert retrieved_user.email == user.email

        # Test read by username
        retrieved_user = user_repository.get_user_by_username(user.username)
        assert retrieved_user is not None
        assert retrieved_user.user_id == user.user_id

        # Test read by email
        retrieved_user = user_repository.get_user_by_email(user.email)
        assert retrieved_user is not None
        assert retrieved_user.user_id == user.user_id

        # Test update
        user.email = "updated@example.com"
        user.failed_login_attempts = 2
        success = user_repository.update_user(user)
        assert success is True

        retrieved_user = user_repository.get_user_by_id(user.user_id)
        assert retrieved_user.email == "updated@example.com"
        assert retrieved_user.failed_login_attempts == 2

        # Test existence checks
        assert user_repository.username_exists(user.username) is True
        assert user_repository.email_exists(user.email) is True
        assert user_repository.username_exists("nonexistent") is False

        # Test delete
        success = user_repository.delete_user(user.user_id)
        assert success is True

        # Verify deletion
        retrieved_user = user_repository.get_user_by_id(user.user_id)
        assert retrieved_user is None

    def test_session_creation_and_management(self, auth_service, sample_registration):
        """Test session creation and JWT token management."""
        # Register and authenticate user
        success, errors = auth_service.register_user(sample_registration)
        assert success is True

        credentials = UserCredentials(
            username=sample_registration.username, password=sample_registration.password
        )

        authenticated_user = auth_service.authenticate_user(credentials, "127.0.0.1")
        assert authenticated_user is not None

        # Create session
        session_id = auth_service.create_session(
            authenticated_user, ip_address="127.0.0.1", user_agent="Test Agent"
        )

        assert session_id is not None
        assert len(session_id) > 0

        # Create access token
        access_token = auth_service.create_access_token(authenticated_user, session_id)
        assert access_token is not None
        assert len(access_token) > 0

        # Verify token
        verified_user = auth_service.verify_access_token(access_token)
        assert verified_user is not None
        assert verified_user.user_id == authenticated_user.user_id
        assert verified_user.username == authenticated_user.username


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--neo4j"])
