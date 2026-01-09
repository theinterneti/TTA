# TTA Comprehensive Test Battery

The TTA Comprehensive Test Battery is a robust testing framework designed to validate the entire TTA storytelling system across multiple dimensions including functionality, performance, security, and data integrity.

## Overview

The comprehensive test battery provides:

- **Multi-Category Testing**: Standard, adversarial, load/stress, data pipeline, and dashboard verification tests
- **Mock/Real Service Support**: Automatic fallback to mock implementations when real services are unavailable
- **CI/CD Integration**: GitHub Actions workflows for automated testing
- **Developer Dashboard**: Real-time monitoring and results visualization
- **Flexible Execution**: Run individual categories or full battery with configurable parameters

## Quick Start

### Prerequisites

```bash
# Install required dependencies
pip install psutil pydantic cryptography websockets aiohttp

# Optional: Start services for real testing
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name neo4j -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/testpassword neo4j:5-community
```

### Basic Usage

```bash
# Run standard tests (quick validation)
python tests/comprehensive_battery/run_comprehensive_tests.py --categories standard

# Run all test categories
python tests/comprehensive_battery/run_comprehensive_tests.py --all

# Run with detailed reporting
python tests/comprehensive_battery/run_comprehensive_tests.py --all --detailed-report --metrics

# Force mock mode (useful for CI/CD)
python tests/comprehensive_battery/run_comprehensive_tests.py --all --force-mock
```

### Using Makefile

```bash
# Quick test execution
make test-standard
make test-adversarial
make test-load
make test-all

# With detailed reporting
make test-all-detailed

# Clean test results
make clean-test-results
```

## Test Categories

### 1. Standard Tests
**Purpose**: Validate normal user interactions and story generation flows

**Coverage**:
- User registration and authentication
- Story creation and progression
- Choice handling and branching
- Session management
- Basic API endpoints

**Example**:
```bash
python tests/comprehensive_battery/run_comprehensive_tests.py --categories standard --max-concurrent 3
```

### 2. Adversarial Tests
**Purpose**: Test edge cases, security vulnerabilities, and error handling

**Coverage**:
- SQL injection attempts
- XSS prevention
- Authentication bypass attempts
- Malformed input handling
- Rate limiting validation
- Data validation edge cases

**Example**:
```bash
python tests/comprehensive_battery/run_comprehensive_tests.py --categories adversarial --timeout 600
```

### 3. Load/Stress Tests
**Purpose**: Validate system performance under concurrent load

**Coverage**:
- Concurrent user sessions
- Database connection pooling
- Memory usage under load
- Response time degradation
- Resource cleanup

**Example**:
```bash
python tests/comprehensive_battery/run_comprehensive_tests.py --categories load_stress --max-concurrent 10
```

### 4. Data Pipeline Tests
**Purpose**: Validate end-to-end data flow from story generation to storage

**Coverage**:
- Story data persistence
- User preference tracking
- Session state management
- Cross-database consistency
- Data migration scenarios

### 5. Dashboard Verification Tests
**Purpose**: Validate real-time dashboard functionality

**Coverage**:
- WebSocket connections
- Real-time data updates
- Dashboard API endpoints
- Metrics calculation
- Alert generation

## Configuration

### Environment Variables

```bash
# Service connections
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="testpassword"
export REDIS_URL="redis://localhost:6379"

# Test execution
export MAX_CONCURRENT_TESTS=5
export TEST_TIMEOUT_SECONDS=600
export FORCE_MOCK_MODE=false

# Reporting
export TEST_OUTPUT_DIR="./test-results"
export DETAILED_REPORTING=true
export ENABLE_METRICS=true
```

### Configuration File

Create `tests/comprehensive_battery/config/local_config.yaml`:

```yaml
# Local development configuration
database:
  neo4j:
    uri: "bolt://localhost:7687"
    user: "neo4j"
    password: "testpassword"
  redis:
    url: "redis://localhost:6379"

execution:
  max_concurrent_tests: 3
  test_timeout_seconds: 300
  cleanup_between_tests: true

mock_mode:
  enabled: true
  force_mock: false
  log_mock_operations: true

reporting:
  output_formats: ["json", "html", "csv"]
  detailed_reports: true
  include_metrics: true
  save_logs: true
```

## Mock vs Real Services

### Mock Mode Benefits
- **No Infrastructure Required**: Tests run without external dependencies
- **Consistent Results**: Predictable behavior for CI/CD environments
- **Fast Execution**: No network latency or service startup time
- **Isolation**: Tests don't affect real data or services

### Real Service Benefits
- **Authentic Testing**: Tests actual database interactions and performance
- **Integration Validation**: Verifies real service configurations
- **Performance Metrics**: Actual response times and resource usage
- **Production Similarity**: Closest to production environment behavior

### Automatic Fallback
The test battery automatically detects service availability:

```python
# Automatic service detection
if neo4j_available:
    use_real_neo4j()
else:
    use_mock_neo4j()
    log_recommendation("Install Neo4j for full testing")
```

## CI/CD Integration

### GitHub Actions

The test battery integrates with GitHub Actions through multiple workflows:

#### Pull Request Validation
```yaml
# .github/workflows/test-integration.yml
- name: Run comprehensive test battery (quick validation)
  run: |
    python tests/comprehensive_battery/run_comprehensive_tests.py \
      --categories standard \
      --max-concurrent 2 \
      --timeout 300
```

#### Full Testing (Main Branch)
```yaml
# .github/workflows/comprehensive-test-battery.yml
- name: Run comprehensive test battery
  run: |
    python tests/comprehensive_battery/run_comprehensive_tests.py \
      --categories ${{ matrix.test-suite.categories }} \
      --detailed-report \
      --metrics
```

### Custom Workflows

Create custom workflows for specific needs:

```bash
# Security-focused testing
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --categories adversarial \
  --security-focus \
  --detailed-report

# Performance benchmarking
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --categories load_stress \
  --benchmark-mode \
  --metrics
```

## Developer Dashboard Integration

### Starting the Dashboard

```bash
# Start dashboard server
python src/developer_dashboard/dashboard_config.py

# Or with custom configuration
export DASHBOARD_PORT=8080
export DASHBOARD_DEBUG=true
python src/developer_dashboard/dashboard_config.py
```

### Dashboard Features

- **Real-time Test Monitoring**: Live updates during test execution
- **Service Status**: Current status of Neo4j, Redis, and other services
- **Historical Trends**: Success rates and performance over time
- **Detailed Results**: Drill-down into individual test failures
- **Alerts**: Notifications for test failures and performance degradation

### WebSocket API

Connect to real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8080/dashboard/test-battery/ws');

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);

    if (message.type === 'battery_status') {
        updateDashboard(message.data);
    } else if (message.type === 'test_result') {
        updateTestResult(message.data);
    }
};
```

## Troubleshooting

### Common Issues

#### Neo4j Authentication Errors
```bash
# Check Neo4j status
docker logs neo4j

# Verify credentials
cypher-shell -a bolt://localhost:7687 -u neo4j -p testpassword "RETURN 1"

# Solution: Test battery will automatically fall back to mock mode
```

#### Redis Connection Issues
```bash
# Check Redis status
redis-cli ping

# Verify connection
redis-cli -h localhost -p 6379 ping

# Solution: Test battery will use mock Redis if real service unavailable
```

#### Import Errors
```bash
# Install missing dependencies
pip install psutil pydantic cryptography websockets aiohttp

# Verify installation
python -c "from tests.comprehensive_battery.comprehensive_test_battery import ComprehensiveTestBattery; print('✓ Import successful')"
```

### Debug Mode

Enable debug logging:

```bash
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --all \
  --log-level DEBUG \
  --save-logs
```

### Test Result Analysis

Check test results:

```bash
# View summary
cat ./test-results/latest/test_summary.json

# View detailed logs
cat ./test-results/latest/comprehensive_test_battery.log

# View HTML report
open ./test-results/latest/test_report.html
```

## Best Practices

### Development Workflow

1. **Local Testing**: Use mock mode for rapid development
2. **Integration Testing**: Use real services for thorough validation
3. **CI/CD**: Combine both modes based on environment capabilities
4. **Production Monitoring**: Regular execution with real services

### Test Organization

1. **Categorize Tests**: Use appropriate test categories for different validation needs
2. **Concurrent Execution**: Balance speed vs resource usage with `--max-concurrent`
3. **Timeout Management**: Set appropriate timeouts for different test types
4. **Result Retention**: Configure result retention based on storage capacity

### Performance Optimization

1. **Mock Mode**: Use for development and quick validation
2. **Selective Testing**: Run only relevant categories during development
3. **Parallel Execution**: Increase concurrency for faster execution
4. **Resource Cleanup**: Enable cleanup between tests for consistent results

## Advanced Usage

### Custom Test Suites

Create custom test configurations:

```yaml
# custom_test_config.yaml
custom_suite:
  name: "Security Validation"
  categories: ["adversarial"]
  max_concurrent: 1
  timeout: 900
  focus_areas:
    - "authentication"
    - "input_validation"
    - "rate_limiting"
```

### Integration with External Tools

```bash
# Integration with pytest
COMPREHENSIVE_TEST_MODE=true pytest tests/test_comprehensive_integration.py

# Integration with coverage tools
python tests/comprehensive_battery/run_comprehensive_tests.py --all --coverage

# Integration with performance profilers
python tests/comprehensive_battery/run_comprehensive_tests.py --categories load_stress --profile
```

### Monitoring and Alerting

Set up automated monitoring:

```bash
# Scheduled execution
0 2 * * * cd /path/to/tta && python tests/comprehensive_battery/run_comprehensive_tests.py --all --alert-on-failure

# Integration with monitoring systems
python tests/comprehensive_battery/run_comprehensive_tests.py --all --webhook-url https://monitoring.example.com/webhook
```

## Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Review test logs in `./test-results/latest/`
3. Enable debug logging for detailed information
4. Check service status in the developer dashboard
5. Verify mock fallback is working correctly

The comprehensive test battery is designed to be robust and provide meaningful feedback even when external dependencies are unavailable.


---
**Logseq:** [[TTA.dev/Docs/Testing/Comprehensive-test-battery]]
