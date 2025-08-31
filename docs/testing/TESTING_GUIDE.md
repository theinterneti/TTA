# TTA Testing Guide

**Version:** 1.0  
**Date:** 2025-01-31  
**Phase:** 2.2 - Testing Infrastructure Improvements

## Overview

This guide provides comprehensive documentation for testing in the TTA (Therapeutic Text Adventure) project. It covers testing patterns, fixture usage, best practices, and the three-tier test structure that ensures reliable and maintainable tests.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Three-Tier Test Structure](#three-tier-test-structure)
3. [Test Categories and Markers](#test-categories-and-markers)
4. [Fixture Usage Guide](#fixture-usage-guide)
5. [Testing Patterns](#testing-patterns)
6. [Best Practices](#best-practices)
7. [Coverage Requirements](#coverage-requirements)
8. [Troubleshooting](#troubleshooting)

## Testing Philosophy

The TTA project follows a comprehensive testing strategy based on:

- **Reliability First**: Tests must be reliable and deterministic
- **Fast Feedback**: Unit tests provide immediate feedback
- **Realistic Integration**: Integration tests use real services when possible
- **Safety Critical**: Therapeutic safety components require extensive testing
- **Maintainable**: Tests should be easy to understand and maintain

### Testing Pyramid

```
    /\     E2E Tests (Few)
   /  \    - Full system integration
  /____\   - User journey validation
 /      \  
/________\  Integration Tests (Some)
           - Service integration
           - Database operations
           - External API calls

Unit Tests (Many)
- Business logic
- Individual components
- Fast execution
```

## Three-Tier Test Structure

The TTA project uses a three-tier test structure that allows for flexible test execution:

### Tier 1: Unit Tests (Default)
- **Command**: `uv run pytest tests/`
- **Characteristics**: Fast, no external dependencies, mocked services
- **Purpose**: Test business logic, individual components, and algorithms
- **Execution Time**: < 30 seconds for full suite

### Tier 2: Neo4j Integration Tests
- **Command**: `uv run pytest tests/ --neo4j`
- **Characteristics**: Uses real Neo4j database via Testcontainers
- **Purpose**: Test graph database operations, complex queries, data relationships
- **Execution Time**: 1-3 minutes

### Tier 3: Redis Integration Tests
- **Command**: `uv run pytest tests/ --redis`
- **Characteristics**: Uses real Redis instance via Testcontainers
- **Purpose**: Test caching, session management, real-time features
- **Execution Time**: 30 seconds - 1 minute

### Combined Integration Tests
- **Command**: `uv run pytest tests/ --neo4j --redis`
- **Characteristics**: Full integration with all external services
- **Purpose**: End-to-end workflows, complete system validation
- **Execution Time**: 2-5 minutes

## Test Categories and Markers

### Built-in Markers

```python
@pytest.mark.neo4j          # Requires Neo4j database
@pytest.mark.redis          # Requires Redis cache
@pytest.mark.integration    # Integration test
@pytest.mark.unit           # Unit test (explicit)
@pytest.mark.slow           # Slow-running test
@pytest.mark.performance    # Performance benchmark
```

### Usage Examples

```python
import pytest

@pytest.mark.unit
def test_business_logic():
    """Fast unit test with no external dependencies."""
    pass

@pytest.mark.neo4j
def test_graph_operations(neo4j_driver):
    """Test requiring Neo4j database."""
    pass

@pytest.mark.redis
def test_caching_behavior(redis_client):
    """Test requiring Redis cache."""
    pass

@pytest.mark.integration
@pytest.mark.neo4j
@pytest.mark.redis
def test_full_workflow(neo4j_driver, redis_client):
    """Full integration test with all services."""
    pass
```

## Fixture Usage Guide

### Database Fixtures

#### Neo4j Fixtures

```python
# Session-scoped container (recommended for most tests)
def test_with_neo4j_container(neo4j_container):
    """Use container configuration directly."""
    uri = neo4j_container["uri"]
    username = neo4j_container["username"]
    password = neo4j_container["password"]

# Driver fixture (higher level, recommended)
def test_with_neo4j_driver(neo4j_driver):
    """Use ready-to-use Neo4j driver."""
    with neo4j_driver.session() as session:
        result = session.run("RETURN 1")
        assert result.single()[0] == 1

# Enhanced reliability fixture
def test_with_enhanced_neo4j(enhanced_neo4j_container):
    """Use enhanced container with better error handling."""
    # Automatically includes retry logic and health checks
    pass
```

#### Redis Fixtures

```python
# Synchronous Redis client
def test_with_redis_sync(redis_client_sync):
    """Use synchronous Redis client."""
    redis_client_sync.set("key", "value")
    assert redis_client_sync.get("key") == b"value"

# Asynchronous Redis client
@pytest.mark.asyncio
async def test_with_redis_async(redis_client):
    """Use asynchronous Redis client."""
    await redis_client.set("key", "value")
    result = await redis_client.get("key")
    assert result == b"value"
```

### Mock Fixtures

```python
# Mock Neo4j driver for unit tests
def test_with_mock_neo4j(mock_neo4j_driver):
    """Use mocked Neo4j driver for unit tests."""
    # Driver is pre-configured with common mock responses
    pass

# Custom mocks
@pytest.fixture
def mock_external_api():
    """Mock external API calls."""
    with patch('src.external.api_client') as mock:
        mock.get_data.return_value = {"status": "success"}
        yield mock
```

## Testing Patterns

### 1. Arrange-Act-Assert Pattern

```python
def test_user_creation():
    # Arrange
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    
    # Act
    user = create_user(user_data)
    
    # Assert
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.id is not None
```

### 2. Parameterized Tests

```python
@pytest.mark.parametrize("input_value,expected", [
    ("valid_input", True),
    ("invalid_input", False),
    ("", False),
    (None, False),
])
def test_validation_function(input_value, expected):
    result = validate_input(input_value)
    assert result == expected
```

### 3. Fixture Factories

```python
@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    def _create_user(**kwargs):
        defaults = {
            "name": "Test User",
            "email": "test@example.com",
            "active": True
        }
        defaults.update(kwargs)
        return User(**defaults)
    return _create_user

def test_user_creation(user_factory):
    user = user_factory(name="Custom Name")
    assert user.name == "Custom Name"
```

### 4. Context Managers for Setup/Teardown

```python
@pytest.fixture
def temporary_data():
    """Create temporary data and clean up after test."""
    # Setup
    data = create_test_data()
    
    yield data
    
    # Teardown
    cleanup_test_data(data)
```

### 5. Async Testing Patterns

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test asynchronous operations."""
    result = await async_function()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_timeout():
    """Test async operations with timeout."""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_async_function(), timeout=1.0)
```

## Best Practices

### 1. Test Organization

```
tests/
├── unit/                    # Pure unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/             # Integration tests
│   ├── test_database.py
│   ├── test_api_endpoints.py
│   └── test_workflows.py
├── e2e/                     # End-to-end tests
│   ├── test_user_journeys.py
│   └── conftest.py
├── fixtures/                # Shared fixtures
│   ├── data_fixtures.py
│   └── service_fixtures.py
└── utils/                   # Test utilities
    ├── testcontainer_reliability.py
    └── enhanced_conftest.py
```

### 2. Test Naming Conventions

```python
# Good: Descriptive test names
def test_user_creation_with_valid_data_creates_user():
    pass

def test_user_creation_with_invalid_email_raises_validation_error():
    pass

def test_password_reset_sends_email_to_user():
    pass

# Bad: Vague test names
def test_user():
    pass

def test_create():
    pass
```

### 3. Test Data Management

```python
# Use factories for complex test data
@pytest.fixture
def sample_therapeutic_session():
    return TherapeuticSession(
        user_id="test_user_123",
        session_type=SessionType.GUIDED,
        start_time=datetime.now(),
        status=SessionStatus.ACTIVE
    )

# Use builders for flexible test data
class UserBuilder:
    def __init__(self):
        self.data = {"name": "Test User", "active": True}
    
    def with_name(self, name):
        self.data["name"] = name
        return self
    
    def inactive(self):
        self.data["active"] = False
        return self
    
    def build(self):
        return User(**self.data)

def test_with_builder():
    user = UserBuilder().with_name("John").inactive().build()
    assert user.name == "John"
    assert not user.active
```

### 4. Error Testing

```python
def test_error_handling():
    """Test that errors are handled appropriately."""
    with pytest.raises(ValidationError) as exc_info:
        create_user({"email": "invalid-email"})
    
    assert "Invalid email format" in str(exc_info.value)

def test_error_logging(caplog):
    """Test that errors are logged correctly."""
    with caplog.at_level(logging.ERROR):
        process_invalid_data()
    
    assert "Processing failed" in caplog.text
```

### 5. Performance Testing

```python
@pytest.mark.performance
def test_query_performance():
    """Test that queries complete within acceptable time."""
    start_time = time.time()
    
    result = execute_complex_query()
    
    execution_time = time.time() - start_time
    assert execution_time < 2.0  # Should complete in under 2 seconds
    assert len(result) > 0

@pytest.mark.performance
def test_memory_usage():
    """Test memory usage stays within bounds."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Perform memory-intensive operation
    large_operation()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Should not increase memory by more than 100MB
    assert memory_increase < 100 * 1024 * 1024
```

## Coverage Requirements

### Overall Coverage Targets

- **Minimum Coverage**: 70%
- **Target Coverage**: 80%
- **Critical Modules**: 90%+ (therapeutic safety)

### Coverage by Test Type

```bash
# Unit test coverage
uv run pytest tests/ -k "not integration" --cov=src --cov-report=html

# Integration test coverage
uv run pytest tests/ --neo4j --redis --cov=src --cov-report=html

# Combined coverage report
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

### Coverage Exclusions

```python
# Exclude from coverage with pragma
def debug_function():  # pragma: no cover
    print("Debug information")

# Exclude entire blocks
if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional
```

## Troubleshooting

### Common Issues

#### 1. Container Startup Failures

```bash
# Check container logs
docker logs <container_id>

# Verify container health
docker ps -a

# Clean up containers
docker system prune -f
```

#### 2. Test Isolation Issues

```python
# Use fresh fixtures for each test
@pytest.fixture
def clean_database(neo4j_driver):
    """Ensure clean database state."""
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    yield neo4j_driver
```

#### 3. Flaky Tests

```python
# Add retry logic for flaky operations
@retry_with_backoff(max_attempts=3, base_delay=0.5)
def flaky_operation():
    # Operation that might fail intermittently
    pass

# Use proper waits instead of sleep
def wait_for_condition(condition_func, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(0.1)
    return False
```

#### 4. Memory Leaks in Tests

```python
# Properly close resources
@pytest.fixture
def database_connection():
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()

# Use context managers
def test_with_context_manager():
    with create_resource() as resource:
        # Use resource
        pass
    # Resource automatically cleaned up
```

### Debugging Tips

1. **Use pytest flags for debugging**:
   ```bash
   # Stop on first failure
   uv run pytest tests/ -x
   
   # Show local variables on failure
   uv run pytest tests/ -l
   
   # Enter debugger on failure
   uv run pytest tests/ --pdb
   
   # Verbose output
   uv run pytest tests/ -v -s
   ```

2. **Capture logs during tests**:
   ```python
   def test_with_logging(caplog):
       with caplog.at_level(logging.DEBUG):
           function_that_logs()
       assert "Expected log message" in caplog.text
   ```

3. **Use temporary directories**:
   ```python
   def test_file_operations(tmp_path):
       test_file = tmp_path / "test.txt"
       test_file.write_text("test content")
       assert test_file.read_text() == "test content"
   ```

---

**Next Steps**: See [Advanced Testing Patterns](ADVANCED_TESTING.md) for more sophisticated testing techniques and [Performance Testing Guide](PERFORMANCE_TESTING.md) for detailed performance testing strategies.
