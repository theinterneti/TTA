# Multi-Agent Workflow Integration Tests

This directory contains comprehensive integration tests for the AI Agent Orchestration System, implementing Task 12.2 requirements for multi-agent workflow testing.

## Overview

The integration test suite validates complete IPA → WBA → NGA workflows, including:

- **End-to-end workflow testing**: Complete agent orchestration workflows
- **Error handling and recovery**: Failover mechanisms and graceful degradation
- **Performance and concurrency**: Load testing and resource management
- **State persistence**: Neo4j and Redis data consistency
- **Message routing**: Agent communication and coordination

## Test Structure

### Core Test Files

| File | Purpose | Markers | Dependencies |
|------|---------|---------|--------------|
| `test_multi_agent_workflow_integration.py` | Test fixtures and utilities | - | Core |
| `test_end_to_end_workflows.py` | Complete workflow integration | `@integration`, `@redis`, `@neo4j` | Redis, Neo4j |
| `test_error_handling_recovery.py` | Error scenarios and recovery | `@integration`, `@redis`, `@neo4j` | Redis, Neo4j |
| `test_state_persistence_aggregation.py` | State management and aggregation | `@integration`, `@redis`, `@neo4j` | Redis, Neo4j |
| `test_performance_concurrency.py` | Performance and scaling tests | `@integration`, `@redis`, `@neo4j` | Redis, Neo4j |

### Test Utilities

- **WorkflowStateVerifier**: Validates workflow state transitions and data consistency
- **PerformanceMetrics**: Collects and analyzes performance data
- **IntegrationTestHelper**: Manages test environment setup and cleanup
- **Neo4jStateVerifier**: Verifies Neo4j state persistence
- **RedisStateVerifier**: Validates Redis message queue states

## Test Categories

### 1. End-to-End Workflow Testing

**File**: `test_end_to_end_workflows.py`

Tests complete IPA → WBA → NGA workflows:
- Basic workflow execution with all agents
- Therapeutic content validation and safety
- State persistence across agent handoffs
- Message routing and transformation
- Response aggregation and coherence

**Key Test Cases**:
- `test_basic_workflow_execution`: Standard workflow completion
- `test_therapeutic_workflow_validation`: Therapeutic content safety
- `test_workflow_with_state_persistence`: Multi-step state management
- `test_message_routing_sequence`: Agent communication flow
- `test_message_delivery_confirmation`: Message reliability

### 2. Error Handling and Recovery

**File**: `test_error_handling_recovery.py`

Tests system resilience and recovery:
- Agent unavailability and failover mechanisms
- Network communication failures
- Invalid message format handling
- Timeout scenarios and recovery
- Circuit breaker patterns

**Key Test Cases**:
- `test_agent_unavailability_failover`: Agent failure handling
- `test_circuit_breaker_pattern`: Failure threshold management
- `test_redis_connection_failure`: Network resilience
- `test_neo4j_write_failure_recovery`: Database failure recovery
- `test_agent_timeout_and_recovery`: Timeout handling

### 3. State Persistence and Aggregation

**File**: `test_state_persistence_aggregation.py`

Tests data consistency and response aggregation:
- Session state persistence across handoffs
- Workflow state transitions in Neo4j
- Concurrent state updates consistency
- Multi-agent response aggregation
- Data integrity validation

**Key Test Cases**:
- `test_session_state_persistence_across_handoffs`: State continuity
- `test_workflow_state_transitions_persistence`: Workflow tracking
- `test_concurrent_state_updates_consistency`: Concurrent safety
- `test_multi_agent_response_aggregation`: Response synthesis

### 4. Performance and Concurrency

**File**: `test_performance_concurrency.py`

Tests system performance and scalability:
- Concurrent workflow execution and isolation
- Resource contention handling
- Performance benchmarks and regression detection
- Memory and CPU usage monitoring
- Agent pool scaling behavior

**Key Test Cases**:
- `test_concurrent_workflow_isolation`: Concurrent execution safety
- `test_workflow_resource_contention`: Resource management
- `test_workflow_performance_benchmarks`: Performance validation
- `test_memory_and_cpu_usage_monitoring`: Resource efficiency
- `test_dynamic_agent_scaling`: Scalability testing

## Running Tests

### Three-Tier Test Execution

The integration tests follow the established three-tier pattern:

```bash
# Tier 1: Unit tests only (fast)
uv run pytest tests/agent_orchestration/test_*integration*.py

# Tier 2: Include Redis integration tests
uv run pytest tests/agent_orchestration/test_*integration*.py --redis

# Tier 3: Include Neo4j integration tests
uv run pytest tests/agent_orchestration/test_*integration*.py --neo4j

# Full integration: Redis + Neo4j
uv run pytest tests/agent_orchestration/test_*integration*.py --redis --neo4j
```

### Individual Test Categories

```bash
# End-to-end workflow tests
uv run pytest tests/agent_orchestration/test_end_to_end_workflows.py --redis --neo4j

# Error handling tests
uv run pytest tests/agent_orchestration/test_error_handling_recovery.py --redis --neo4j

# State persistence tests
uv run pytest tests/agent_orchestration/test_state_persistence_aggregation.py --redis --neo4j

# Performance tests
uv run pytest tests/agent_orchestration/test_performance_concurrency.py --redis --neo4j
```

### Makefile Integration

```bash
# Use project Makefile for standardized execution
make test-integration  # Full integration tests
make test-redis        # Redis integration tests
make test-neo4j        # Neo4j integration tests
```

## Test Data and Fixtures

### Therapeutic Scenarios

The tests use realistic therapeutic text adventure scenarios:

- **Anxiety Management**: Player expressing anxiety about challenges
- **Self-Confidence Building**: Supporting player self-doubt
- **Grief Processing**: Handling loss and memory triggers
- **Mindfulness Practice**: Grounding and present-moment awareness

### Performance Test Scenarios

- **Low Load**: 3 concurrent workflows, 30s duration
- **Medium Load**: 10 concurrent workflows, 60s duration
- **High Load**: 25 concurrent workflows, 120s duration
- **Stress Test**: 50 concurrent workflows, 180s duration

### Error Scenarios

- **Agent Timeouts**: Slow agent processing
- **Network Failures**: Redis/Neo4j connectivity issues
- **Invalid Messages**: Malformed message handling
- **Resource Contention**: Multiple workflows competing for agents

## Infrastructure Requirements

### Redis Configuration

- **Purpose**: Message coordination and agent registry
- **Test Database**: Separate database index for isolation
- **Cleanup**: Automatic cleanup after each test
- **Testcontainers**: Used for CI/CD environments

### Neo4j Configuration

- **Purpose**: State persistence and workflow tracking
- **Test Database**: Isolated test database
- **Cleanup**: Automatic cleanup after each test
- **Testcontainers**: Used for CI/CD environments

### Environment Variables

```bash
# CI/CD Service Configuration
TEST_REDIS_URI=redis://localhost:6379/0
TEST_NEO4J_URI=bolt://localhost:7687
TEST_NEO4J_USERNAME=neo4j
TEST_NEO4J_PASSWORD=testpassword

# Test Execution Flags
RUN_REDIS_TESTS=1
RUN_NEO4J_TESTS=1
```

## CI/CD Integration

The integration tests are configured for GitHub Actions:

```yaml
# .github/workflows/tests.yml
services:
  redis:
    image: redis:7
    ports:
      - 6379:6379
  neo4j:
    image: neo4j:5-community
    env:
      NEO4J_AUTH: neo4j/testpassword
    ports:
      - 7687:7687
```

## Performance Expectations

### Response Time Benchmarks

- **Low Load**: ≤ 2.0s average response time
- **Medium Load**: ≤ 5.0s average response time
- **High Load**: ≤ 10.0s average response time

### Success Rate Targets

- **Low Load**: ≥ 98% success rate
- **Medium Load**: ≥ 95% success rate
- **High Load**: ≥ 90% success rate

### Resource Usage Limits

- **Memory**: < 2GB peak usage, < 500MB increase under load
- **CPU**: < 80% average usage during load tests
- **Concurrency**: Support for 25+ concurrent workflows

## Troubleshooting

### Common Issues

1. **Redis Connection Failures**
   - Verify Redis is running: `redis-cli ping`
   - Check port availability: `netstat -an | grep 6379`
   - Use `--redis` flag for Redis-dependent tests

2. **Neo4j Connection Issues**
   - Verify Neo4j is running: `cypher-shell -u neo4j -p testpassword "RETURN 1"`
   - Check authentication: Ensure correct username/password
   - Use `--neo4j` flag for Neo4j-dependent tests

3. **Test Timeouts**
   - Increase timeout values in test configuration
   - Check system resources during test execution
   - Consider reducing concurrent workflow counts

4. **Memory Issues**
   - Monitor memory usage with `psutil` tests
   - Verify cleanup functions are called
   - Check for memory leaks in long-running tests

### Debug Mode

```bash
# Run with verbose output
uv run pytest tests/agent_orchestration/test_*integration*.py -v --redis --neo4j

# Run specific test with debugging
uv run pytest tests/agent_orchestration/test_end_to_end_workflows.py::TestCompleteWorkflowIntegration::test_basic_workflow_execution -v -s --redis --neo4j
```

## Contributing

When adding new integration tests:

1. **Use appropriate pytest markers**: `@integration`, `@redis`, `@neo4j`
2. **Follow naming conventions**: `test_*integration*.py` for discovery
3. **Include cleanup**: Always clean up test data in `finally` blocks
4. **Document test scenarios**: Add clear docstrings and comments
5. **Verify three-tier execution**: Test with and without infrastructure dependencies

## Validation

Run the test structure validation:

```bash
uv run python tests/agent_orchestration/test_integration_runner.py
```

This validates:
- Test module imports and structure
- Test fixture functionality
- Performance metrics utilities
- Workflow state verification
- Mock workflow execution


---
**Logseq:** [[TTA.dev/Tests/Agent_orchestration/Readme_integration_tests]]
