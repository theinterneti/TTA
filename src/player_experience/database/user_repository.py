"""
User Repository for database operations.

This module provides the UserRepository class that handles all database
operations for user authentication data, including CRUD operations and queries.
"""

import logging
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from uuid import uuid4

from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError, ClientError

from ..models.auth import UserRole, UserCredentials, UserRegistration, AuthenticatedUser

logger = logging.getLogger(__name__)


class UserRepositoryError(Exception):
    """Raised when user repository operations fail."""
    pass


class User:
    """User model for database operations."""
    
    def __init__(self, user_id: str, username: str, email: str, password_hash: str,
                 role: UserRole = UserRole.PLAYER, email_verified: bool = False,
                 created_at: Optional[datetime] = None, last_login: Optional[datetime] = None,
                 account_status: str = "active", failed_login_attempts: int = 0,
                 locked_until: Optional[datetime] = None, **kwargs):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role if isinstance(role, UserRole) else UserRole(role)
        self.email_verified = email_verified
        self.created_at = created_at or datetime.now(timezone.utc)
        self.last_login = last_login
        self.account_status = account_status
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until
        
        # Additional fields from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for database storage."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role.value,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "account_status": self.account_status,
            "failed_login_attempts": self.failed_login_attempts,
            "locked_until": self.locked_until.isoformat() if self.locked_until else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary data."""
        # Parse datetime fields
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
        
        last_login = None
        if data.get("last_login"):
            last_login = datetime.fromisoformat(data["last_login"].replace('Z', '+00:00'))
        
        locked_until = None
        if data.get("locked_until"):
            locked_until = datetime.fromisoformat(data["locked_until"].replace('Z', '+00:00'))
        
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            email=data["email"],
            password_hash=data["password_hash"],
            role=UserRole(data.get("role", "player")),
            email_verified=data.get("email_verified", False),
            created_at=created_at,
            last_login=last_login,
            account_status=data.get("account_status", "active"),
            failed_login_attempts=data.get("failed_login_attempts", 0),
            locked_until=locked_until,
        )


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j", password: str = "password"):
        """
        Initialize the User Repository.
        
        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.driver: Optional[Driver] = None
        logger.info("UserRepository initialized")
    
    def connect(self) -> None:
        """Establish connection to Neo4j database with retry/backoff for readiness races."""
        try:
            from neo4j.exceptions import AuthError, ServiceUnavailable as _ServiceUnavailable, ClientError as _ClientError
        except Exception:  # pragma: no cover - neo4j not installed path
            AuthError = Exception  # type: ignore
            _ServiceUnavailable = ServiceUnavailable  # type: ignore
            _ClientError = Exception  # type: ignore
        base_delay = 0.5
        last_exc: Optional[Exception] = None
        # Option B: increase attempts to 6 (0.5,1,2,4,8,8)
        attempts = 6
        for attempt in range(attempts):
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
                with self.driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"UserRepository connected to Neo4j at {self.uri}")
                return
            except (AuthError, _ServiceUnavailable) as e:
                last_exc = e
                delay = min(base_delay * (2 ** attempt), 8.0)
                logger.debug(f"Neo4j connect attempt {attempt+1}/{attempts} failed ({e!s}); retrying in {delay:.1f}s")
                try:
                    if self.driver:
                        self.driver.close()
                except Exception:
                    pass
                self.driver = None
                import time as _t
                if attempt < (attempts - 1):
                    _t.sleep(delay)
                else:
                    if isinstance(e, AuthError):
                        raise UserRepositoryError(f"Failed to connect to Neo4j after retries: {e}")
                    elif isinstance(e, _ServiceUnavailable):
                        raise UserRepositoryError(f"Failed to connect to Neo4j after retries: {e}")
            except _ClientError as e:
                emsg = str(e)
                last_exc = e
                if ("AuthenticationRateLimit" in emsg) or ("authentication details too many times" in emsg):
                    delay = min(base_delay * (2 ** attempt), 8.0)
                    logger.debug(f"Neo4j auth rate limit attempt {attempt+1}/{attempts}; retrying in {delay:.1f}s")
                    try:
                        if self.driver:
                            self.driver.close()
                    except Exception:
                        pass
                    self.driver = None
                    import time as _t
                    if attempt < (attempts - 1):
                        _t.sleep(delay)
                    else:
                        raise UserRepositoryError(f"Failed to connect to Neo4j after retries: {e}")
                else:
                    raise UserRepositoryError(f"Failed to connect to Neo4j: {e}")
            except Exception as e:
                last_exc = e
                logger.error(f"Unexpected error connecting to Neo4j: {e}")
                raise UserRepositoryError(f"Unexpected error connecting to Neo4j: {e}")
        
        if last_exc:
            raise UserRepositoryError(f"Failed to connect to Neo4j after {attempts} attempts: {last_exc}")
    
    def disconnect(self) -> None:
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("UserRepository disconnected from Neo4j")
    
    def create_user(self, user: User) -> bool:
        """
        Create a new user in the database.
        
        Args:
            user: User object to create
            
        Returns:
            bool: True if user was created successfully
        """
        if not self.driver:
            raise UserRepositoryError("Not connected to Neo4j")
        
        query = """
        CREATE (u:User {
            user_id: $user_id,
            username: $username,
            email: $email,
            password_hash: $password_hash,
            role: $role,
            email_verified: $email_verified,
            created_at: $created_at,
            last_login: $last_login,
            account_status: $account_status,
            failed_login_attempts: $failed_login_attempts,
            locked_until: $locked_until
        })
        RETURN u.user_id as user_id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query,
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    password_hash=user.password_hash,
                    role=user.role.value,
                    email_verified=user.email_verified,
                    created_at=user.created_at.isoformat() if user.created_at else None,
                    last_login=user.last_login.isoformat() if user.last_login else None,
                    account_status=user.account_status,
                    failed_login_attempts=user.failed_login_attempts,
                    locked_until=user.locked_until.isoformat() if user.locked_until else None
                )
                
                record = result.single()
                if record:
                    logger.info(f"Created user: {user.user_id}")
                    return True
                else:
                    logger.error(f"Failed to create user: {user.user_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating user {user.user_id}: {e}")
            raise UserRepositoryError(f"Error creating user: {e}")
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            Optional[User]: User if found, None otherwise
        """
        if not self.driver:
            raise UserRepositoryError("Not connected to Neo4j")
        
        query = """
        MATCH (u:User {user_id: $user_id})
        RETURN u
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, user_id=user_id)
                record = result.single()
                
                if record and record["u"]:
                    user_data = dict(record["u"])
                    return User.from_dict(user_data)
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}")
            raise UserRepositoryError(f"Error retrieving user: {e}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            Optional[User]: User if found, None otherwise
        """
        if not self.driver:
            raise UserRepositoryError("Not connected to Neo4j")
        
        query = """
        MATCH (u:User {username: $username})
        RETURN u
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, username=username)
                record = result.single()
                
                if record and record["u"]:
                    user_data = dict(record["u"])
                    return User.from_dict(user_data)
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {e}")
            raise UserRepositoryError(f"Error retrieving user by username: {e}")
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email.

        Args:
            email: Email to search for

        Returns:
            Optional[User]: User if found, None otherwise
        """
        if not self.driver:
            raise UserRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (u:User {email: $email})
        RETURN u
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, email=email)
                record = result.single()

                if record and record["u"]:
                    user_data = dict(record["u"])
                    return User.from_dict(user_data)
                else:
                    return None

        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {e}")
            raise UserRepositoryError(f"Error retrieving user by email: {e}")

    def update_user(self, user: User) -> bool:
        """
        Update an existing user in the database.

        Args:
            user: User object with updated data

        Returns:
            bool: True if user was updated successfully
        """
        if not self.driver:
            raise UserRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (u:User {user_id: $user_id})
        SET u.username = $username,
            u.email = $email,
            u.password_hash = $password_hash,
            u.role = $role,
            u.email_verified = $email_verified,
            u.last_login = $last_login,
            u.account_status = $account_status,
            u.failed_login_attempts = $failed_login_attempts,
            u.locked_until = $locked_until
        RETURN u.user_id as user_id
        """

        try:
            with self.driver.session() as session:
                result = session.run(query,
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    password_hash=user.password_hash,
                    role=user.role.value,
                    email_verified=user.email_verified,
                    last_login=user.last_login.isoformat() if user.last_login else None,
                    account_status=user.account_status,
                    failed_login_attempts=user.failed_login_attempts,
                    locked_until=user.locked_until.isoformat() if user.locked_until else None
                )

                record = result.single()
                if record:
                    logger.info(f"Updated user: {user.user_id}")
                    return True
                else:
                    logger.warning(f"User not found for update: {user.user_id}")
                    return False

        except Exception as e:
            logger.error(f"Error updating user {user.user_id}: {e}")
            raise UserRepositoryError(f"Error updating user: {e}")

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from the database.

        Args:
            user_id: User identifier

        Returns:
            bool: True if user was deleted successfully
        """
        if not self.driver:
            raise UserRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (u:User {user_id: $user_id})
        DELETE u
        RETURN count(u) as deleted_count
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, user_id=user_id)
                record = result.single()

                if record and record["deleted_count"] > 0:
                    logger.info(f"Deleted user: {user_id}")
                    return True
                else:
                    logger.warning(f"User not found for deletion: {user_id}")
                    return False

        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise UserRepositoryError(f"Error deleting user: {e}")

    def username_exists(self, username: str) -> bool:
        """
        Check if a username already exists.

        Args:
            username: Username to check

        Returns:
            bool: True if username exists
        """
        if not self.driver:
            raise UserRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (u:User {username: $username})
        RETURN count(u) > 0 as exists
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, username=username)
                record = result.single()
                return record["exists"] if record else False

        except Exception as e:
            logger.error(f"Error checking username existence {username}: {e}")
            raise UserRepositoryError(f"Error checking username existence: {e}")

    def email_exists(self, email: str) -> bool:
        """
        Check if an email already exists.

        Args:
            email: Email to check

        Returns:
            bool: True if email exists
        """
        if not self.driver:
            raise UserRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (u:User {email: $email})
        RETURN count(u) > 0 as exists
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, email=email)
                record = result.single()
                return record["exists"] if record else False

        except Exception as e:
            logger.error(f"Error checking email existence {email}: {e}")
            raise UserRepositoryError(f"Error checking email existence: {e}")

    def get_users_by_role(self, role: UserRole) -> List[User]:
        """
        Retrieve all users with a specific role.

        Args:
            role: User role to filter by

        Returns:
            List[User]: List of users with the specified role
        """
        if not self.driver:
            raise UserRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (u:User {role: $role})
        RETURN u
        ORDER BY u.created_at DESC
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, role=role.value)
                users = []

                for record in result:
                    if record["u"]:
                        user_data = dict(record["u"])
                        users.append(User.from_dict(user_data))

                return users

        except Exception as e:
            logger.error(f"Error retrieving users by role {role}: {e}")
            raise UserRepositoryError(f"Error retrieving users by role: {e}")


# Utility functions for user repository operations
def create_user_repository(uri: str = "bolt://localhost:7687",
                          username: str = "neo4j",
                          password: str = "password") -> UserRepository:
    """
    Create and connect a user repository.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        UserRepository: Connected repository instance
    """
    repository = UserRepository(uri, username, password)
    repository.connect()
    return repository
