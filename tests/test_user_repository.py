"""
Tests for UserRepository database operations.

This module tests the UserRepository class with comprehensive unit tests
using mock Neo4j driver and error handling scenarios.
"""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from src.player_experience.database.user_repository import (
    User,
    UserRepository,
    UserRepositoryError,
    create_user_repository,
)
from src.player_experience.models.auth import UserRole


@pytest.fixture
def mock_neo4j_driver():
    """Create a mock Neo4j driver for testing."""
    mock_driver = Mock()
    mock_session = Mock()
    mock_result = Mock()
    mock_record = Mock()

    # Setup the mock chain
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_driver.session.return_value.__exit__.return_value = None
    mock_session.run.return_value = mock_result
    mock_result.single.return_value = mock_record

    return mock_driver, mock_session, mock_result, mock_record


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        user_id="test_user_123",
        username="testuser",
        email="test@example.com",
        password_hash="$2b$12$hashed_password",
        role=UserRole.PLAYER,
        email_verified=True,
        created_at=datetime.now(timezone.utc),
        account_status="active",
        failed_login_attempts=0,
    )


@pytest.fixture
def user_repository():
    """Create a UserRepository instance for testing."""
    return UserRepository("bolt://localhost:7687", "neo4j", "password")


class TestUser:
    """Test the User model class."""

    def test_user_creation(self, sample_user):
        """Test user object creation."""
        assert sample_user.user_id == "test_user_123"
        assert sample_user.username == "testuser"
        assert sample_user.email == "test@example.com"
        assert sample_user.role == UserRole.PLAYER
        assert sample_user.email_verified is True
        assert sample_user.account_status == "active"
        assert sample_user.failed_login_attempts == 0

    def test_user_to_dict(self, sample_user):
        """Test user to dictionary conversion."""
        user_dict = sample_user.to_dict()

        assert user_dict["user_id"] == "test_user_123"
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["role"] == "player"
        assert user_dict["email_verified"] is True
        assert user_dict["account_status"] == "active"
        assert user_dict["failed_login_attempts"] == 0
        assert isinstance(user_dict["created_at"], str)

    def test_user_from_dict(self):
        """Test user creation from dictionary."""
        user_data = {
            "user_id": "test_user_456",
            "username": "testuser2",
            "email": "test2@example.com",
            "password_hash": "$2b$12$hashed_password2",
            "role": "admin",
            "email_verified": False,
            "created_at": "2024-01-01T00:00:00+00:00",
            "account_status": "pending",
            "failed_login_attempts": 2,
        }

        user = User.from_dict(user_data)

        assert user.user_id == "test_user_456"
        assert user.username == "testuser2"
        assert user.email == "test2@example.com"
        assert user.role == UserRole.ADMIN
        assert user.email_verified is False
        assert user.account_status == "pending"
        assert user.failed_login_attempts == 2
        assert isinstance(user.created_at, datetime)


class TestUserRepository:
    """Test the UserRepository class."""

    def test_repository_initialization(self, user_repository):
        """Test repository initialization."""
        assert user_repository.uri == "bolt://localhost:7687"
        assert user_repository.username == "neo4j"
        assert user_repository.password == "password"
        assert user_repository.driver is None

    @patch("src.player_experience.database.user_repository.GraphDatabase")
    def test_connect_success(self, mock_graph_db, user_repository):
        """Test successful database connection."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_driver.session.return_value.__exit__.return_value = None
        mock_session.run.return_value = Mock()

        user_repository.connect()

        assert user_repository.driver == mock_driver
        mock_graph_db.driver.assert_called_once_with(
            "bolt://localhost:7687", auth=("neo4j", "password")
        )

    @patch("src.player_experience.database.user_repository.GraphDatabase")
    def test_connect_failure(self, mock_graph_db, user_repository):
        """Test database connection failure."""
        from neo4j.exceptions import ServiceUnavailable

        mock_graph_db.driver.side_effect = ServiceUnavailable("Connection failed")

        with pytest.raises(UserRepositoryError):
            user_repository.connect()

    def test_disconnect(self, user_repository):
        """Test database disconnection."""
        mock_driver = Mock()
        user_repository.driver = mock_driver

        user_repository.disconnect()

        mock_driver.close.assert_called_once()
        assert user_repository.driver is None

    def test_create_user_success(self, user_repository, sample_user, mock_neo4j_driver):
        """Test successful user creation."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver
        mock_record.__getitem__.return_value = "test_user_123"

        result = user_repository.create_user(sample_user)

        assert result is True
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "CREATE (u:User" in call_args[0][0]

    def test_create_user_not_connected(self, user_repository, sample_user):
        """Test user creation when not connected."""
        with pytest.raises(UserRepositoryError, match="Not connected to Neo4j"):
            user_repository.create_user(sample_user)

    def test_get_user_by_id_success(self, user_repository, mock_neo4j_driver):
        """Test successful user retrieval by ID."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver

        # Mock the returned user data
        user_data = {
            "user_id": "test_user_123",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "$2b$12$hashed_password",
            "role": "player",
            "email_verified": True,
            "created_at": "2024-01-01T00:00:00+00:00",
            "account_status": "active",
            "failed_login_attempts": 0,
        }
        mock_record.__getitem__.return_value = user_data
        mock_record.__bool__.return_value = True

        user = user_repository.get_user_by_id("test_user_123")

        assert user is not None
        assert user.user_id == "test_user_123"
        assert user.username == "testuser"
        assert user.role == UserRole.PLAYER

    def test_get_user_by_id_not_found(self, user_repository, mock_neo4j_driver):
        """Test user retrieval when user not found."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver
        mock_result.single.return_value = None

        user = user_repository.get_user_by_id("nonexistent_user")

        assert user is None

    def test_get_user_by_username_success(self, user_repository, mock_neo4j_driver):
        """Test successful user retrieval by username."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver

        user_data = {
            "user_id": "test_user_123",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "$2b$12$hashed_password",
            "role": "player",
            "email_verified": True,
            "created_at": "2024-01-01T00:00:00+00:00",
            "account_status": "active",
            "failed_login_attempts": 0,
        }
        mock_record.__getitem__.return_value = user_data
        mock_record.__bool__.return_value = True

        user = user_repository.get_user_by_username("testuser")

        assert user is not None
        assert user.username == "testuser"
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "MATCH (u:User {username: $username})" in call_args[0][0]

    def test_get_user_by_email_success(self, user_repository, mock_neo4j_driver):
        """Test successful user retrieval by email."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver

        user_data = {
            "user_id": "test_user_123",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "$2b$12$hashed_password",
            "role": "player",
            "email_verified": True,
            "created_at": "2024-01-01T00:00:00+00:00",
            "account_status": "active",
            "failed_login_attempts": 0,
        }
        mock_record.__getitem__.return_value = user_data
        mock_record.__bool__.return_value = True

        user = user_repository.get_user_by_email("test@example.com")

        assert user is not None
        assert user.email == "test@example.com"

    def test_update_user_success(self, user_repository, sample_user, mock_neo4j_driver):
        """Test successful user update."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver
        mock_record.__getitem__.return_value = "test_user_123"

        result = user_repository.update_user(sample_user)

        assert result is True
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "MATCH (u:User {user_id: $user_id})" in call_args[0][0]
        assert "SET u.username = $username" in call_args[0][0]

    def test_delete_user_success(self, user_repository, mock_neo4j_driver):
        """Test successful user deletion."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver
        mock_record.__getitem__.return_value = 1  # deleted_count

        result = user_repository.delete_user("test_user_123")

        assert result is True
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "DELETE u" in call_args[0][0]

    def test_username_exists_true(self, user_repository, mock_neo4j_driver):
        """Test username existence check when username exists."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver
        mock_record.__getitem__.return_value = True

        exists = user_repository.username_exists("testuser")

        assert exists is True

    def test_username_exists_false(self, user_repository, mock_neo4j_driver):
        """Test username existence check when username doesn't exist."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver
        mock_record.__getitem__.return_value = False

        exists = user_repository.username_exists("nonexistent")

        assert exists is False

    def test_email_exists_true(self, user_repository, mock_neo4j_driver):
        """Test email existence check when email exists."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver
        mock_record.__getitem__.return_value = True

        exists = user_repository.email_exists("test@example.com")

        assert exists is True

    def test_get_users_by_role(self, user_repository, mock_neo4j_driver):
        """Test retrieving users by role."""
        mock_driver, mock_session, mock_result, mock_record = mock_neo4j_driver
        user_repository.driver = mock_driver

        # Mock multiple user records
        user_data = {
            "user_id": "test_user_123",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "$2b$12$hashed_password",
            "role": "admin",
            "email_verified": True,
            "created_at": "2024-01-01T00:00:00+00:00",
            "account_status": "active",
            "failed_login_attempts": 0,
        }

        mock_records = [Mock(), Mock()]
        for record in mock_records:
            record.__getitem__.return_value = user_data

        mock_result.__iter__.return_value = mock_records

        users = user_repository.get_users_by_role(UserRole.ADMIN)

        assert len(users) == 2
        assert all(user.role == UserRole.ADMIN for user in users)


class TestUtilityFunctions:
    """Test utility functions."""

    @patch("src.player_experience.database.user_repository.UserRepository")
    def test_create_user_repository(self, mock_repo_class):
        """Test create_user_repository utility function."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        result = create_user_repository("bolt://test:7687", "testuser", "testpass")

        mock_repo_class.assert_called_once_with(
            "bolt://test:7687", "testuser", "testpass"
        )
        mock_repo.connect.assert_called_once()
        assert result == mock_repo


if __name__ == "__main__":
    pytest.main([__file__])
