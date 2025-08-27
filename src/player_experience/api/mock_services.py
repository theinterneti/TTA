"""
Mock Services for Development and Testing

This module provides mock implementations of external services to enable
running the FastAPI application without external dependencies like Neo4j and Redis.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MockNeo4jDriver:
    """Mock Neo4j driver for development and testing."""
    
    def __init__(self, uri: str, auth: tuple):
        self.uri = uri
        self.auth = auth
        self.connected = False
        self._mock_data = {}
        logger.info(f"MockNeo4jDriver initialized for {uri}")
    
    def session(self):
        """Return a mock session context manager."""
        return MockNeo4jSession(self)
    
    def close(self):
        """Close the mock driver."""
        self.connected = False
        logger.debug("MockNeo4jDriver closed")


class MockNeo4jSession:
    """Mock Neo4j session."""
    
    def __init__(self, driver: MockNeo4jDriver):
        self.driver = driver
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def run(self, query: str, **parameters):
        """Mock query execution."""
        logger.debug(f"Mock Neo4j query: {query[:100]}...")
        
        # Return mock result based on query type
        if "CREATE" in query.upper():
            return MockNeo4jResult([{"created": True}])
        elif "MATCH" in query.upper():
            return MockNeo4jResult([])  # Empty result for non-existent data
        else:
            return MockNeo4jResult([{"result": "mock"}])


class MockNeo4jResult:
    """Mock Neo4j query result."""
    
    def __init__(self, records: List[Dict]):
        self.records = records
    
    def single(self):
        """Return single record or None."""
        return self.records[0] if self.records else None
    
    def data(self):
        """Return all records."""
        return self.records


class MockRedisClient:
    """Mock Redis client for development and testing."""
    
    def __init__(self, **kwargs):
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 6379)
        self.db = kwargs.get('db', 0)
        self._data = {}
        self.connected = False
        logger.info(f"MockRedisClient initialized for {self.host}:{self.port}/{self.db}")
    
    async def ping(self):
        """Mock ping operation."""
        self.connected = True
        return True
    
    async def get(self, key: str):
        """Mock get operation."""
        return self._data.get(key)
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None):
        """Mock set operation."""
        self._data[key] = value
        return True
    
    async def delete(self, key: str):
        """Mock delete operation."""
        return self._data.pop(key, None) is not None
    
    async def exists(self, key: str):
        """Mock exists operation."""
        return key in self._data
    
    async def expire(self, key: str, seconds: int):
        """Mock expire operation."""
        return key in self._data
    
    async def close(self):
        """Mock close operation."""
        self.connected = False


class MockUserRepository:
    """Mock user repository for development and testing."""
    
    def __init__(self):
        self.users = {}
        self.connected = False
        logger.info("MockUserRepository initialized")
    
    def connect(self):
        """Mock connect operation."""
        self.connected = True
        logger.debug("MockUserRepository connected")
    
    def disconnect(self):
        """Mock disconnect operation."""
        self.connected = False
        logger.debug("MockUserRepository disconnected")
    
    def create_user(self, user) -> bool:
        """Mock user creation."""
        self.users[user.user_id] = user
        logger.debug(f"Mock user created: {user.username}")
        return True
    
    def get_user_by_username(self, username: str):
        """Mock user retrieval by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email: str):
        """Mock user retrieval by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def update_user(self, user) -> bool:
        """Mock user update."""
        if user.user_id in self.users:
            self.users[user.user_id] = user
            logger.debug(f"Mock user updated: {user.username}")
            return True
        return False
    
    def delete_user(self, user_id: str) -> bool:
        """Mock user deletion."""
        if user_id in self.users:
            del self.users[user_id]
            logger.debug(f"Mock user deleted: {user_id}")
            return True
        return False


def create_mock_neo4j_driver(uri: str, auth: tuple):
    """Create a mock Neo4j driver."""
    return MockNeo4jDriver(uri, auth)


def create_mock_redis_client(**kwargs):
    """Create a mock Redis client."""
    return MockRedisClient(**kwargs)


def create_mock_user_repository():
    """Create a mock user repository."""
    return MockUserRepository()


# Mock service registry for easy access
MOCK_SERVICES = {
    'neo4j_driver': create_mock_neo4j_driver,
    'redis_client': create_mock_redis_client,
    'user_repository': create_mock_user_repository,
}


def get_mock_service(service_name: str, *args, **kwargs):
    """Get a mock service by name."""
    if service_name in MOCK_SERVICES:
        return MOCK_SERVICES[service_name](*args, **kwargs)
    else:
        raise ValueError(f"Unknown mock service: {service_name}")


def is_development_mode() -> bool:
    """Check if we're running in development mode."""
    import os
    return os.getenv("TTA_DEVELOPMENT_MODE", "false").lower() in ("true", "1", "yes")


def should_use_mocks() -> bool:
    """Check if we should use mock services."""
    import os
    return (
        is_development_mode() or 
        os.getenv("TTA_USE_MOCKS", "false").lower() in ("true", "1", "yes") or
        os.getenv("TTA_USE_NEO4J", "0") != "1"
    )
