# Database Testing Setup Guide

## Overview

The TTA test suite includes integration tests that require Neo4j and Redis databases. These tests are **intentionally skipped by default** to allow the test suite to run in environments without database infrastructure.

## Test Categories

### Unit Tests (Run by Default)
- **686 tests** that run without external dependencies
- Use mocked database connections
- Fast execution
- **Pass Rate: 93.3%**

### Integration Tests (Skipped by Default)
- **213 tests** that require real Neo4j or Redis databases
- Marked with `@pytest.mark.neo4j` or `@pytest.mark.redis`
- Automatically skipped unless databases are explicitly enabled
- Use testcontainers to spin up temporary Docker containers

## Current Test Results

**Without Databases (Default):**
```
Total Tests: 952
Passed: 686 (72.1%)
Failed: 49 (5.1%)
Skipped: 213 (22.4%)
Pass Rate: 93.3% (excluding skipped tests)
```

## Running Tests with Databases

### Option 1: Using Environment Variables

```bash
# Enable Neo4j tests
export RUN_NEO4J_TESTS=1

# Enable Redis tests
export RUN_REDIS_TESTS=1

# Run tests
pytest
```

### Option 2: Using Command Line Flags

```bash
# Run tests with Neo4j
pytest --neo4j

# Run tests with Redis
pytest --redis

# Run tests with both databases
pytest --neo4j --redis
```

### Option 3: Using Existing Docker Containers

If you have Neo4j and Redis running in Docker (e.g., from docker-compose), you can point tests to them:

```bash
# Set environment variables to use existing containers
export TEST_NEO4J_URI="bolt://localhost:7688"
export TEST_NEO4J_USERNAME="neo4j"
export TEST_NEO4J_PASSWORD="your_password"
export TEST_REDIS_URI="redis://localhost:6380/0"

# Enable and run tests
pytest --neo4j --redis
```

## Testcontainers Setup

When you run tests with `--neo4j` or `--redis` flags, the test suite uses **testcontainers** to automatically:

1. Pull the required Docker images (neo4j:5-community, redis:7)
2. Start temporary containers
3. Wait for containers to be ready
4. Run tests against the containers
5. Clean up containers after tests complete

### Requirements

- Docker installed and running
- Docker daemon accessible
- Sufficient disk space for Docker images (~500MB for Neo4j, ~100MB for Redis)
- Network access to pull Docker images

### Troubleshooting Testcontainers

**Issue: Authentication failures with Neo4j**
- Testcontainers may take time to initialize Neo4j authentication
- The test suite includes retry logic with exponential backoff
- If tests fail, try running again - the container may need more time

**Issue: Port conflicts**
- Testcontainers automatically assigns random ports
- No manual port configuration needed
- Containers are isolated from your development databases

**Issue: Docker permission denied**
- Ensure your user is in the `docker` group: `sudo usermod -aG docker $USER`
- Log out and back in for group changes to take effect
- Or run tests with `sudo` (not recommended)

## Mock Database Fixtures

For unit tests that need database-like behavior without real databases, use the provided mock fixtures:

### Mock Neo4j Driver

```python
def test_with_mock_neo4j(mock_neo4j_driver):
    """Test using mocked Neo4j driver."""
    # mock_neo4j_driver provides basic Neo4j driver interface
    session = mock_neo4j_driver.session()
    result = session.run("MATCH (n) RETURN n")
    # Assertions...
```

### Mock Redis Client

```python
async def test_with_mock_redis(mock_redis_client):
    """Test using mocked Redis client."""
    # mock_redis_client provides async Redis interface
    await mock_redis_client.set("key", "value")
    value = await mock_redis_client.get("key")
    # Assertions...
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests (no databases)
        run: pytest
        # Skips 213 integration tests automatically

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests with databases
        run: pytest --neo4j --redis
        # Testcontainers will start temporary databases
```

## Best Practices

### For Unit Tests
- ✅ Use mock fixtures (`mock_neo4j_driver`, `mock_redis_client`)
- ✅ Test business logic without external dependencies
- ✅ Fast execution (< 1 second per test)
- ❌ Don't mark with `@pytest.mark.neo4j` or `@pytest.mark.redis`

### For Integration Tests
- ✅ Mark with `@pytest.mark.neo4j` or `@pytest.mark.redis`
- ✅ Test actual database interactions
- ✅ Use testcontainers for isolation
- ❌ Don't assume specific database state
- ❌ Don't use hardcoded connection strings

### Writing New Tests

**Unit Test Example:**
```python
def test_user_creation(mock_neo4j_driver):
    """Test user creation logic without real database."""
    user_service = UserService(mock_neo4j_driver)
    user = user_service.create_user("test@example.com")
    assert user.email == "test@example.com"
```

**Integration Test Example:**
```python
@pytest.mark.neo4j
def test_user_persistence(neo4j_driver):
    """Test user persistence with real Neo4j database."""
    user_service = UserService(neo4j_driver)
    user = user_service.create_user("test@example.com")

    # Verify user was actually saved to database
    retrieved = user_service.get_user(user.id)
    assert retrieved.email == "test@example.com"
```

## Database Test Markers

The test suite uses pytest markers to categorize database tests:

- `@pytest.mark.neo4j` - Requires Neo4j database
- `@pytest.mark.redis` - Requires Redis database
- `@pytest.mark.integration` - Integration test (may require databases)

### Viewing Tests by Marker

```bash
# List all Neo4j tests
pytest --collect-only -m neo4j

# List all Redis tests
pytest --collect-only -m redis

# Run only integration tests (excluding database tests)
pytest -m "integration and not neo4j and not redis"
```

## Performance Considerations

### Test Execution Times

- **Unit tests (no databases):** ~45 seconds for 686 tests
- **Integration tests (with testcontainers):** ~2-5 minutes additional (first run)
- **Integration tests (with testcontainers):** ~1-2 minutes additional (subsequent runs, images cached)

### Optimizing Test Runs

```bash
# Run only fast unit tests
pytest -m "not neo4j and not redis"

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Run tests that failed, then all others
pytest --ff
```

## Summary

- **213 skipped tests are expected behavior** - they're integration tests requiring databases
- **93.3% pass rate** for tests that run without databases
- **Use `--neo4j` and `--redis` flags** to run integration tests
- **Testcontainers handles database setup automatically**
- **Mock fixtures available** for unit tests that need database-like behavior

The current test design is **correct and follows best practices** for separating unit tests from integration tests.


---
**Logseq:** [[TTA.dev/Docs/Setup/Testing_database_setup]]
