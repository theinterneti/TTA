"""
User Authentication Schema Manager for Neo4j.

This module manages the Neo4j schema for user authentication data,
including User nodes, constraints, indexes, and relationships with
PlayerProfile nodes for the therapeutic text adventure platform.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError, ClientError

logger = logging.getLogger(__name__)


class UserAuthSchemaError(Exception):
    """Raised when user authentication schema operations fail."""
    pass


class UserAuthSchemaManager:
    """
    Manages Neo4j schema for user authentication and related data.
    
    This class handles the creation and management of User nodes,
    authentication constraints, indexes, and relationships with
    PlayerProfile nodes for secure user management.
    """
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j", password: str = "password"):
        """
        Initialize the User Authentication Schema Manager.
        
        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.driver: Optional[Driver] = None
    
    def connect(self) -> None:
        """Establish connection to Neo4j database with retry/backoff for readiness races."""
        # Import here to access specific exception types without changing module import surface
        try:
            from neo4j.exceptions import AuthError, ServiceUnavailable as _ServiceUnavailable, ClientError as _ClientError
        except Exception:  # pragma: no cover - neo4j not installed path
            AuthError = Exception  # type: ignore
            _ServiceUnavailable = ServiceUnavailable  # type: ignore
            _ClientError = Exception  # type: ignore
        last_exc: Optional[Exception] = None
        base_delay = 0.5
        # Option B: increase attempts to 6 (0.5,1,2,4,8,8)
        attempts = 6
        for attempt in range(attempts):
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
                with self.driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"UserAuthSchemaManager connected to Neo4j at {self.uri}")
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
                        raise UserAuthSchemaError(f"Failed to connect to Neo4j after retries: {e}")
                    elif isinstance(e, _ServiceUnavailable):
                        raise UserAuthSchemaError(f"Failed to connect to Neo4j after retries: {e}")
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
                        raise UserAuthSchemaError(f"Failed to connect to Neo4j after retries: {e}")
                else:
                    raise UserAuthSchemaError(f"Failed to connect to Neo4j: {e}")
            except Exception as e:
                last_exc = e
                logger.error(f"Unexpected error connecting to Neo4j: {e}")
                raise UserAuthSchemaError(f"Unexpected error connecting to Neo4j: {e}")
        
        if last_exc:
            raise UserAuthSchemaError(f"Failed to connect to Neo4j after {attempts} attempts: {last_exc}")
    
    def disconnect(self) -> None:
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("UserAuthSchemaManager disconnected from Neo4j")
    
    def create_user_auth_constraints(self) -> bool:
        """
        Create constraints for user authentication nodes.
        
        Returns:
            bool: True if all constraints were created successfully
        """
        if not self.driver:
            raise UserAuthSchemaError("Not connected to Neo4j")
        
        constraints = [
            # User authentication constraints
            "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
            "CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE",
            "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
            
            # Session constraints
            "CREATE CONSTRAINT session_id IF NOT EXISTS FOR (s:UserSession) REQUIRE s.session_id IS UNIQUE",
            
            # MFA secret constraints
            "CREATE CONSTRAINT mfa_secret_id IF NOT EXISTS FOR (m:MFASecret) REQUIRE m.secret_id IS UNIQUE",
            
            # Security event constraints
            "CREATE CONSTRAINT security_event_id IF NOT EXISTS FOR (se:SecurityEvent) REQUIRE se.event_id IS UNIQUE",
        ]
        
        try:
            with self.driver.session() as session:
                for constraint in constraints:
                    try:
                        session.run(constraint)
                        logger.debug(f"Created user auth constraint: {constraint}")
                    except ClientError as e:
                        if "already exists" in str(e).lower() or "equivalent constraint already exists" in str(e).lower():
                            logger.debug(f"Constraint already exists: {constraint}")
                        else:
                            logger.error(f"Failed to create constraint {constraint}: {e}")
                            raise UserAuthSchemaError(f"Failed to create constraint: {e}")
            
            logger.info("Successfully created all user authentication constraints")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user authentication constraints: {e}")
            raise UserAuthSchemaError(f"Error creating constraints: {e}")
    
    def create_user_auth_indexes(self) -> bool:
        """
        Create indexes for user authentication nodes for performance.
        
        Returns:
            bool: True if all indexes were created successfully
        """
        if not self.driver:
            raise UserAuthSchemaError("Not connected to Neo4j")
        
        indexes = [
            # User indexes for performance
            "CREATE INDEX user_email_index IF NOT EXISTS FOR (u:User) ON (u.email)",
            "CREATE INDEX user_created_at_index IF NOT EXISTS FOR (u:User) ON (u.created_at)",
            "CREATE INDEX user_last_login_index IF NOT EXISTS FOR (u:User) ON (u.last_login)",
            "CREATE INDEX user_account_status_index IF NOT EXISTS FOR (u:User) ON (u.account_status)",
            
            # Session indexes
            "CREATE INDEX session_user_id_index IF NOT EXISTS FOR (s:UserSession) ON (s.user_id)",
            "CREATE INDEX session_created_at_index IF NOT EXISTS FOR (s:UserSession) ON (s.created_at)",
            "CREATE INDEX session_expires_at_index IF NOT EXISTS FOR (s:UserSession) ON (s.expires_at)",
            "CREATE INDEX session_is_active_index IF NOT EXISTS FOR (s:UserSession) ON (s.is_active)",
            
            # Security event indexes
            "CREATE INDEX security_event_user_id_index IF NOT EXISTS FOR (se:SecurityEvent) ON (se.user_id)",
            "CREATE INDEX security_event_type_index IF NOT EXISTS FOR (se:SecurityEvent) ON (se.event_type)",
            "CREATE INDEX security_event_timestamp_index IF NOT EXISTS FOR (se:SecurityEvent) ON (se.timestamp)",
            "CREATE INDEX security_event_severity_index IF NOT EXISTS FOR (se:SecurityEvent) ON (se.severity)",
        ]
        
        try:
            with self.driver.session() as session:
                for index in indexes:
                    try:
                        session.run(index)
                        logger.debug(f"Created user auth index: {index}")
                    except ClientError as e:
                        if "already exists" in str(e).lower() or "equivalent index already exists" in str(e).lower():
                            logger.debug(f"Index already exists: {index}")
                        else:
                            logger.error(f"Failed to create index {index}: {e}")
                            raise UserAuthSchemaError(f"Failed to create index: {e}")
            
            logger.info("Successfully created all user authentication indexes")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user authentication indexes: {e}")
            raise UserAuthSchemaError(f"Error creating indexes: {e}")
    
    def setup_user_auth_schema(self) -> bool:
        """
        Set up the complete user authentication schema.
        
        Returns:
            bool: True if schema setup was successful
        """
        try:
            logger.info("Setting up user authentication schema...")
            
            # Create constraints first
            self.create_user_auth_constraints()
            
            # Create indexes for performance
            self.create_user_auth_indexes()
            
            logger.info("User authentication schema setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup user authentication schema: {e}")
            raise UserAuthSchemaError(f"Schema setup failed: {e}")
    
    def verify_schema(self) -> Dict[str, Any]:
        """
        Verify the user authentication schema is properly set up.
        
        Returns:
            Dict containing schema verification results
        """
        if not self.driver:
            raise UserAuthSchemaError("Not connected to Neo4j")
        
        verification_results = {
            "constraints": [],
            "indexes": [],
            "schema_valid": False
        }
        
        try:
            with self.driver.session() as session:
                # Check constraints
                constraints_result = session.run("SHOW CONSTRAINTS")
                for record in constraints_result:
                    constraint_info = dict(record)
                    if any(label in str(constraint_info) for label in ["User", "UserSession", "MFASecret", "SecurityEvent"]):
                        verification_results["constraints"].append(constraint_info)
                
                # Check indexes
                indexes_result = session.run("SHOW INDEXES")
                for record in indexes_result:
                    index_info = dict(record)
                    if any(label in str(index_info) for label in ["User", "UserSession", "MFASecret", "SecurityEvent"]):
                        verification_results["indexes"].append(index_info)
                
                # Basic validation
                verification_results["schema_valid"] = (
                    len(verification_results["constraints"]) >= 6 and  # Minimum expected constraints
                    len(verification_results["indexes"]) >= 12  # Minimum expected indexes
                )
            
            logger.info(f"Schema verification completed: {verification_results['schema_valid']}")
            return verification_results
            
        except Exception as e:
            logger.error(f"Error verifying user authentication schema: {e}")
            raise UserAuthSchemaError(f"Schema verification failed: {e}")


# Utility functions for user authentication schema management
def create_user_auth_schema_manager(uri: str = "bolt://localhost:7687", 
                                   username: str = "neo4j", 
                                   password: str = "password") -> UserAuthSchemaManager:
    """
    Create and connect a user authentication schema manager.
    
    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password
        
    Returns:
        UserAuthSchemaManager: Connected schema manager instance
    """
    manager = UserAuthSchemaManager(uri, username, password)
    manager.connect()
    return manager
