---
name: CI/CD Parallel Testing Infrastructure
about: Configure isolated database instances for parallel test execution
title: "CI/CD: Multi-Instance Databases for Parallel Test Execution"
labels: ci-cd, testing, infrastructure, enhancement
milestone: Automated Testing Pipeline
assignees: ''

---

## Overview
Set up multiple isolated database instances to enable parallel test execution in CI/CD pipelines, dramatically reducing test execution time.

## Context
Current simplified setup uses:
- ✅ Single Neo4j instance with multiple databases (tta_dev, tta_test, tta_staging)
- ✅ Single Redis instance with multiple DB numbers (0-15)

This works well for sequential testing but **parallel tests can interfere** with each other when using the same database instance.

## Problem Statement
When running tests in parallel (e.g., via pytest-xdist, GitHub Actions matrix, etc.):
- ❌ Tests can read/write same data causing race conditions
- ❌ Database cleanup between tests becomes unreliable
- ❌ One slow test blocks others
- ❌ Difficult to isolate failures

## Solution: Ephemeral Test Databases
Use testcontainers or similar to spin up isolated database instances per test run/worker.

## Requirements

### Test Infrastructure
- [ ] Testcontainers integration for Neo4j
- [ ] Testcontainers integration for Redis
- [ ] Pytest plugin for parallel execution
- [ ] Database cleanup between test runs
- [ ] Resource limits per container

### CI/CD Pipeline
- [ ] GitHub Actions workflow with matrix strategy
- [ ] Docker-in-Docker or Docker socket mounting
- [ ] Parallel job execution (4-8 workers)
- [ ] Test result aggregation
- [ ] Coverage report merging

### Performance
- [ ] Test suite completes in <10 minutes (target)
- [ ] Efficient container reuse where possible
- [ ] Fast database initialization
- [ ] Resource cleanup after tests

## Implementation Plan

### Phase 1: Local Testcontainers Setup
```python
# tests/conftest.py
import pytest
from testcontainers.neo4j import Neo4jContainer
from testcontainers.redis import RedisContainer

@pytest.fixture(scope="session")
def neo4j_test_container():
    """Spin up isolated Neo4j for testing"""
    with Neo4jContainer("neo4j:5.26.1-community") as neo4j:
        yield neo4j

@pytest.fixture(scope="session")
def redis_test_container():
    """Spin up isolated Redis for testing"""
    with RedisContainer("redis:7-alpine") as redis:
        yield redis

@pytest.fixture
def neo4j_driver(neo4j_test_container):
    """Neo4j driver connected to test container"""
    driver = GraphDatabase.driver(
        neo4j_test_container.get_connection_url(),
        auth=(
            neo4j_test_container.NEO4J_USER,
            neo4j_test_container.NEO4J_ADMIN_PASSWORD
        )
    )
    yield driver
    driver.close()
```

### Phase 2: Pytest-xdist Integration
```ini
# pytest.ini
[pytest]
addopts =
    -n auto  # Auto-detect number of CPUs
    --dist loadfile  # Distribute by file
    --maxfail=5  # Stop after 5 failures
```

### Phase 3: GitHub Actions Matrix
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
        test-group: [unit, integration, e2e]
      fail-fast: false

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-extras

      - name: Run tests (${{ matrix.test-group }})
        run: |
          uv run pytest tests/${{ matrix.test-group }} \
            -n auto \
            --cov=src \
            --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Phase 4: Resource Optimization
- [ ] Implement container caching
- [ ] Reuse containers across test modules where safe
- [ ] Implement database fixtures with proper cleanup
- [ ] Profile and optimize slow tests

## Benefits

### Speed
- 🚀 **4-8x faster**: Parallel execution vs sequential
- ⏱️ **<10 min**: Full test suite (currently 30-40 min)
- 🔄 **Faster iteration**: Quick feedback on PRs

### Reliability
- ✅ **Isolated tests**: No interference between parallel runs
- 🐛 **Easier debugging**: Clear test separation
- 🧹 **Clean state**: Fresh database per test run

### CI/CD
- 🔁 **Matrix testing**: Multiple Python versions simultaneously
- 📊 **Better coverage**: More comprehensive testing
- 💰 **Cost efficient**: Faster CI = lower costs

## Example Usage

```bash
# Local parallel testing
pytest -n 4  # Run with 4 workers

# Specific test groups in parallel
pytest tests/unit -n auto
pytest tests/integration -n 4

# CI/CD (automatic)
# GitHub Actions runs matrix of test groups in parallel
```

## Success Criteria
- [ ] Test suite runs in <10 minutes (vs current 30-40 min)
- [ ] Zero test interference/flakiness due to parallel execution
- [ ] All tests pass reliably with parallel execution
- [ ] CI/CD cost reduced by 50%+
- [ ] Developer productivity improved (faster feedback)

## Dependencies
- Docker available in CI/CD environment
- Testcontainers package installed
- Pytest-xdist configured
- Sufficient CI/CD resources (runners)

## Risks & Mitigations

### Risk: Resource Exhaustion
**Mitigation**:
- Limit parallel workers based on available resources
- Implement container resource limits
- Use container cleanup

### Risk: Docker-in-Docker Issues
**Mitigation**:
- Use Docker socket mounting in CI/CD
- Test with testcontainers cloud
- Fallback to sequential execution if needed

### Risk: Flaky Tests
**Mitigation**:
- Implement proper test isolation
- Use database cleanup fixtures
- Retry flaky tests (pytest-rerunfailures)

## Documentation
- [ ] Update testing guide with parallel execution
- [ ] Document testcontainers setup
- [ ] CI/CD pipeline documentation
- [ ] Troubleshooting guide

## Related Issues
- Issue #X: Production Database Infrastructure
- Issue #Y: Database Version Migration Testing

## Notes
- Keep local development simple with shared instance
- Use testcontainers only for CI/CD and parallel testing
- Document how to run tests both sequentially and in parallel
- Monitor CI/CD costs and optimize

---

**Priority**: Medium (for efficient testing)
**Complexity**: Medium
**Estimated Effort**: 1-2 weeks


---
**Logseq:** [[TTA.dev/.github/Issue_template/Cicd-parallel-testing]]
