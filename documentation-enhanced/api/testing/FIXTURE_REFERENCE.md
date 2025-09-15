# TTA Fixture Reference Guide

**Version:** 1.0  
**Date:** 2025-01-31  
**Purpose:** Complete reference for all available test fixtures

## Overview

This document provides a comprehensive reference for all test fixtures available in the TTA project. Fixtures are organized by category and include usage examples, scope information, and dependencies.

## Table of Contents

1. [Database Fixtures](#database-fixtures)
2. [Service Fixtures](#service-fixtures)
3. [Mock Fixtures](#mock-fixtures)
4. [Data Fixtures](#data-fixtures)
5. [Utility Fixtures](#utility-fixtures)
6. [Enhanced Reliability Fixtures](#enhanced-reliability-fixtures)

## Database Fixtures

### Neo4j Fixtures

#### `neo4j_container` (Session Scope)
**Location**: `tests/conftest.py`  
**Scope**: Session  
**Dependencies**: `--neo4j` flag or `RUN_NEO4J_TESTS=1`

```python
def test_with_neo4j_container(neo4j_container):
    """Basic Neo4j container access."""
    uri = neo4j_container["uri"]
    username = neo4j_container["username"]
    password = neo4j_container["password"]
    
    # Manual driver creation
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(username, password))
    # ... use driver
    driver.close()
```

**Returns**: Dictionary with keys:
- `uri`: Connection URI (e.g., `bolt://localhost:7687`)
- `username`: Database username (default: `neo4j`)
- `password`: Database password (default: `testpassword`)

#### `neo4j_driver` (Session Scope)
**Location**: `tests/conftest.py`  
**Scope**: Session  
**Dependencies**: `neo4j_container`

```python
def test_with_neo4j_driver(neo4j_driver):
    """Ready-to-use Neo4j driver with retry logic."""
    with neo4j_driver.session() as session:
        result = session.run("CREATE (n:TestNode {name: $name}) RETURN n", name="test")
        node = result.single()["n"]
        assert node["name"] == "test"
```

**Returns**: Configured Neo4j driver with built-in retry logic

#### `enhanced_neo4j_container` (Session Scope)
**Location**: `tests/utils/enhanced_conftest.py`  
**Scope**: Session  
**Dependencies**: `--neo4j` flag

```python
def test_with_enhanced_neo4j(enhanced_neo4j_container):
    """Enhanced Neo4j container with improved reliability."""
    # Includes automatic health checks and retry mechanisms
    uri = enhanced_neo4j_container["uri"]
    # Container is guaranteed to be healthy when fixture yields
```

**Features**:
- Enhanced health checking
- Automatic retry mechanisms
- Better error handling
- Performance optimizations

### Redis Fixtures

#### `redis_container` (Session Scope)
**Location**: `tests/conftest.py`  
**Scope**: Session  
**Dependencies**: `--redis` flag or `RUN_REDIS_TESTS=1`

```python
def test_with_redis_container(redis_container):
    """Basic Redis container access."""
    connection_url = redis_container  # String URL
    
    import redis
    client = redis.from_url(connection_url)
    client.set("test_key", "test_value")
    assert client.get("test_key") == b"test_value"
    client.close()
```

**Returns**: Redis connection URL string

#### `redis_client_sync` (Function Scope)
**Location**: `tests/conftest.py`  
**Scope**: Function  
**Dependencies**: `redis_container`

```python
def test_with_redis_sync_client(redis_client_sync):
    """Synchronous Redis client."""
    redis_client_sync.set("key", "value")
    assert redis_client_sync.get("key") == b"value"
    # Client automatically closed after test
```

**Returns**: Configured synchronous Redis client

#### `redis_client` (Function Scope, Async)
**Location**: `tests/conftest.py`  
**Scope**: Function  
**Dependencies**: `redis_container`

```python
@pytest.mark.asyncio
async def test_with_redis_async_client(redis_client):
    """Asynchronous Redis client."""
    await redis_client.set("key", "value")
    result = await redis_client.get("key")
    assert result == b"value"
    # Client automatically closed after test
```

**Returns**: Configured asynchronous Redis client

## Service Fixtures

### Mock Service Fixtures

#### `mock_neo4j_driver` (Function Scope)
**Location**: `tests/conftest.py`  
**Scope**: Function  
**Dependencies**: None

```python
def test_with_mock_neo4j(mock_neo4j_driver):
    """Mock Neo4j driver for unit tests."""
    # Pre-configured mock with common responses
    with mock_neo4j_driver.session() as session:
        result = session.run("RETURN 1")
        # Mock returns None by default
```

**Features**:
- Pre-configured mock responses
- Context manager support
- No external dependencies

### API Client Fixtures

#### `mock_external_api` (Function Scope)
**Location**: Custom fixture (example)

```python
@pytest.fixture
def mock_external_api():
    """Mock external API client."""
    with patch('src.external.api_client') as mock:
        mock.get.return_value = {"status": "success", "data": {}}
        mock.post.return_value = {"status": "created", "id": "123"}
        yield mock

def test_with_mock_api(mock_external_api):
    """Test with mocked external API."""
    from src.services.data_service import fetch_external_data
    
    result = fetch_external_data("endpoint")
    assert result["status"] == "success"
    mock_external_api.get.assert_called_once_with("endpoint")
```

## Data Fixtures

### User Data Fixtures

#### `sample_user_data` (Function Scope)
**Location**: Custom fixture (example)

```python
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "role": "user",
        "active": True,
        "preferences": {
            "theme": "light",
            "notifications": True
        }
    }

def test_user_creation(sample_user_data):
    """Test user creation with sample data."""
    user = create_user(sample_user_data)
    assert user.name == "Test User"
```

#### `user_factory` (Function Scope)
**Location**: Custom fixture (example)

```python
@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    def _create_user(**kwargs):
        defaults = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "user",
            "active": True
        }
        defaults.update(kwargs)
        return defaults
    return _create_user

def test_with_user_factory(user_factory):
    """Test with user factory."""
    admin_user = user_factory(role="admin", name="Admin User")
    assert admin_user["role"] == "admin"
    assert admin_user["name"] == "Admin User"
```

### Therapeutic Session Fixtures

#### `sample_therapeutic_session` (Function Scope)
**Location**: Custom fixture (example)

```python
@pytest.fixture
def sample_therapeutic_session():
    """Sample therapeutic session data."""
    from datetime import datetime
    return {
        "user_id": "test_user_123",
        "session_type": "guided",
        "start_time": datetime.now(),
        "status": "active",
        "metadata": {
            "initial_mood": 5,
            "goals": ["anxiety_reduction", "mood_improvement"]
        }
    }
```

## Utility Fixtures

### Temporary Data Fixtures

#### `tmp_path` (Function Scope)
**Location**: Built-in pytest fixture  
**Scope**: Function

```python
def test_file_operations(tmp_path):
    """Test with temporary directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    assert test_file.read_text() == "test content"
    # Directory automatically cleaned up
```

#### `caplog` (Function Scope)
**Location**: Built-in pytest fixture  
**Scope**: Function

```python
import logging

def test_logging_behavior(caplog):
    """Test logging output."""
    with caplog.at_level(logging.INFO):
        logger = logging.getLogger("test")
        logger.info("Test message")
        logger.error("Error message")
    
    assert "Test message" in caplog.text
    assert "Error message" in caplog.text
    assert len(caplog.records) == 2
```

### Time and Date Fixtures

#### `freeze_time` (Function Scope)
**Location**: Custom fixture using freezegun

```python
from freezegun import freeze_time
import pytest
from datetime import datetime

@pytest.fixture
def frozen_time():
    """Freeze time for consistent testing."""
    with freeze_time("2025-01-31 12:00:00"):
        yield datetime(2025, 1, 31, 12, 0, 0)

def test_time_dependent_function(frozen_time):
    """Test function that depends on current time."""
    result = get_current_timestamp()
    assert result == frozen_time
```

## Enhanced Reliability Fixtures

### Enhanced Container Fixtures

#### `enhanced_neo4j_driver` (Session Scope)
**Location**: `tests/utils/enhanced_conftest.py`  
**Scope**: Session  
**Dependencies**: `enhanced_neo4j_container`

```python
def test_with_enhanced_driver(enhanced_neo4j_driver):
    """Enhanced Neo4j driver with retry logic."""
    # Driver includes automatic retry on connection failures
    with enhanced_neo4j_driver.session() as session:
        result = session.run("RETURN 1")
        assert result.single()[0] == 1
```

**Features**:
- Automatic retry on connection failures
- Enhanced error handling
- Connection validation

#### `enhanced_redis_client_sync` (Session Scope)
**Location**: `tests/utils/enhanced_conftest.py`  
**Scope**: Session  
**Dependencies**: `enhanced_redis_container`

```python
def test_with_enhanced_redis(enhanced_redis_client_sync):
    """Enhanced Redis client with reliability features."""
    # Client includes retry logic and connection validation
    enhanced_redis_client_sync.set("key", "value")
    assert enhanced_redis_client_sync.get("key") == b"value"
```

### Diagnostic Fixtures

#### `container_failure_diagnostics` (Auto-use)
**Location**: `tests/utils/enhanced_conftest.py`  
**Scope**: Function  
**Auto-use**: True

```python
# This fixture runs automatically and captures container logs on test failures
def test_that_might_fail():
    """Test that might fail - diagnostics captured automatically."""
    # If this test fails, container logs will be automatically captured
    assert some_condition_that_might_fail()
```

**Features**:
- Automatic activation on test failures
- Container log capture
- Diagnostic information collection

## Fixture Combinations

### Common Fixture Combinations

#### Database + Service Testing
```python
@pytest.mark.neo4j
def test_user_service_integration(neo4j_driver, user_factory):
    """Test user service with real database."""
    from src.services.user_service import UserService
    
    service = UserService(neo4j_driver)
    user_data = user_factory(name="Integration Test User")
    
    user = service.create_user(user_data)
    assert user.id is not None
    
    retrieved = service.get_user(user.id)
    assert retrieved.name == "Integration Test User"
```

#### Multi-Service Integration
```python
@pytest.mark.neo4j
@pytest.mark.redis
def test_full_stack_integration(neo4j_driver, redis_client_sync, user_factory):
    """Test full stack with multiple services."""
    from src.services.user_service import UserService
    from src.services.cache_service import CacheService
    
    user_service = UserService(neo4j_driver)
    cache_service = CacheService(redis_client_sync)
    
    user_data = user_factory()
    user = user_service.create_user(user_data)
    
    # Cache the user
    cache_service.cache_user(user)
    
    # Retrieve from cache
    cached_user = cache_service.get_cached_user(user.id)
    assert cached_user.name == user.name
```

## Custom Fixture Creation

### Creating Project-Specific Fixtures

```python
# tests/fixtures/therapeutic_fixtures.py
import pytest
from datetime import datetime, timedelta

@pytest.fixture
def therapeutic_session_builder():
    """Builder for therapeutic sessions."""
    class SessionBuilder:
        def __init__(self):
            self.data = {
                "user_id": "default_user",
                "session_type": "guided",
                "start_time": datetime.now(),
                "status": "active"
            }
        
        def with_user(self, user_id):
            self.data["user_id"] = user_id
            return self
        
        def crisis_session(self):
            self.data["session_type"] = "crisis"
            self.data["priority"] = "high"
            return self
        
        def completed(self):
            self.data["status"] = "completed"
            self.data["end_time"] = datetime.now()
            return self
        
        def build(self):
            return self.data.copy()
    
    return SessionBuilder()

# Usage
def test_crisis_session_handling(therapeutic_session_builder):
    """Test crisis session handling."""
    session_data = (therapeutic_session_builder
                   .with_user("crisis_user_123")
                   .crisis_session()
                   .build())
    
    session = create_therapeutic_session(session_data)
    assert session.session_type == "crisis"
    assert session.priority == "high"
```

### Fixture Dependencies and Scopes

```python
# Fixture dependency chain example
@pytest.fixture(scope="session")
def database_connection():
    """Session-scoped database connection."""
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def clean_database(database_connection):
    """Function-scoped clean database."""
    # Setup: Clean the database
    database_connection.execute("DELETE FROM test_tables")
    
    yield database_connection
    
    # Teardown: Clean up after test
    database_connection.execute("DELETE FROM test_tables")

@pytest.fixture
def user_repository(clean_database):
    """Repository with clean database."""
    return UserRepository(clean_database)
```

## Best Practices for Fixture Usage

### 1. Choose Appropriate Scope
- **Session**: Expensive setup (containers, connections)
- **Module**: Shared across test file
- **Class**: Shared across test class
- **Function**: Fresh for each test (default)

### 2. Use Fixture Factories for Flexibility
```python
@pytest.fixture
def user_factory():
    """Flexible user creation."""
    created_users = []
    
    def _create_user(**kwargs):
        user = create_user(kwargs)
        created_users.append(user)
        return user
    
    yield _create_user
    
    # Cleanup all created users
    for user in created_users:
        delete_user(user.id)
```

### 3. Combine Fixtures Effectively
```python
@pytest.fixture
def authenticated_user(user_factory, auth_service):
    """User with valid authentication."""
    user = user_factory(role="user")
    token = auth_service.create_token(user)
    user.auth_token = token
    return user
```

### 4. Use Parametrized Fixtures for Variations
```python
@pytest.fixture(params=["admin", "user", "guest"])
def user_with_role(request, user_factory):
    """User with different roles."""
    return user_factory(role=request.param)

def test_role_based_access(user_with_role):
    """Test runs once for each role."""
    # Test logic here
    pass
```

---

**Related Documentation**:
- [Testing Guide](TESTING_GUIDE.md) - Main testing documentation
- [Advanced Testing](ADVANCED_TESTING.md) - Advanced testing patterns
- [Testcontainer Reliability](../utils/testcontainer_reliability.py) - Enhanced container utilities
