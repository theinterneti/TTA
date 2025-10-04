# TTA Comprehensive Test Battery

A comprehensive testing framework for the Therapeutic Text Adventure (TTA) storytelling system, providing thorough validation of all system components including standard functionality, security, performance, data pipeline integrity, and dashboard operations.

## Overview

The Comprehensive Test Battery is designed to validate the complete TTA system through multiple test categories:

- **Standard Tests**: Normal user interactions and story generation flows
- **Adversarial Tests**: Edge cases, security vulnerabilities, and error scenarios
- **Load/Stress Tests**: Performance under concurrent load and resource constraints
- **Data Pipeline Validation**: End-to-end data flow verification
- **Dashboard Verification**: Real-time dashboard functionality and accuracy

## Architecture

```
tests/comprehensive_battery/
├── __init__.py                          # Main module exports
├── comprehensive_test_battery.py        # Main orchestrator
├── run_comprehensive_tests.py           # CLI execution script
├── README.md                           # This documentation
├── config/
│   └── comprehensive_test_config.yaml  # Configuration file
├── test_suites/
│   ├── __init__.py
│   ├── standard_test_suite.py          # Standard functionality tests
│   ├── adversarial_test_suite.py       # Security and edge case tests
│   └── load_stress_test_suite.py       # Performance and load tests
├── validators/
│   ├── __init__.py
│   ├── data_pipeline_validator.py      # Data pipeline validation
│   └── dashboard_validator.py          # Dashboard verification
└── utils/
    ├── __init__.py
    ├── test_data_generator.py          # Test data generation
    ├── metrics_collector.py            # System metrics collection
    └── report_generator.py             # Report generation
```

## Quick Start

### Prerequisites

1. **System Requirements**:
   - Python 3.8+
   - Neo4j database running
   - Redis server running
   - TTA application running

2. **Dependencies**:
   ```bash
   pip install pytest pytest-asyncio aioredis neo4j psutil websockets aiohttp
   ```

### Basic Usage

1. **Run all test categories**:
   ```bash
   python tests/comprehensive_battery/run_comprehensive_tests.py --all
   ```

2. **Run specific categories**:
   ```bash
   python tests/comprehensive_battery/run_comprehensive_tests.py --categories standard adversarial
   ```

3. **Run with detailed reporting**:
   ```bash
   python tests/comprehensive_battery/run_comprehensive_tests.py --all --detailed-report --metrics
   ```

### Configuration

Edit `tests/comprehensive_battery/config/comprehensive_test_config.yaml` to customize:

- Database connection settings
- Test execution parameters
- Load testing configurations
- Reporting options

## Test Categories

### 1. Standard Test Suite

Tests normal user interactions and core functionality:

- **User Registration & Authentication**: Account creation, login/logout flows
- **Character Creation**: Character generation with various attributes
- **Story Generation Pipeline**: End-to-end story creation and delivery
- **Choice Consequences**: Decision impact tracking and story branching
- **Session Management**: Multi-session continuity and state persistence
- **User Experience Flow**: Complete user journey validation

**Example**:
```bash
python run_comprehensive_tests.py --categories standard
```

### 2. Adversarial Test Suite

Tests security vulnerabilities and edge cases:

- **Input Injection Attacks**: SQL injection, XSS, command injection
- **Authentication Bypass**: Session hijacking, privilege escalation
- **Boundary Condition Testing**: Invalid inputs, extreme values
- **Database Failure Simulation**: Connection failures, data corruption
- **Resource Exhaustion**: Memory leaks, connection pool exhaustion
- **Malformed Request Handling**: Invalid API calls, corrupted data

**Example**:
```bash
python run_comprehensive_tests.py --categories adversarial --log-level DEBUG
```

### 3. Load/Stress Test Suite

Tests performance under various load conditions:

- **Concurrent User Simulation**: Multiple simultaneous users
- **Story Generation Load**: High-volume story requests
- **Memory Usage Monitoring**: Resource consumption tracking
- **Connection Pool Testing**: Database connection limits
- **Sustained Load Testing**: Extended duration performance
- **Spike Load Testing**: Sudden traffic increases

**Example**:
```bash
python run_comprehensive_tests.py --categories load_stress --max-concurrent 20
```

### 4. Data Pipeline Validation

Validates complete data flow integrity:

- **Story Generation Pipeline**: Input to storage validation
- **User Interaction Metrics**: Metrics capture and storage
- **Data Transformation Accuracy**: Processing correctness
- **Cross-Database Consistency**: Neo4j and Redis synchronization
- **Data Persistence Integrity**: Long-term storage validation
- **Real-time Data Flow**: Live update propagation

**Example**:
```bash
python run_comprehensive_tests.py --categories data_pipeline --detailed-report
```

### 5. Dashboard Verification

Validates dashboard functionality and real-time updates:

- **Real-time Data Updates**: Live dashboard refresh validation
- **WebSocket Connection Stability**: Connection reliability testing
- **Dashboard Data Accuracy**: Display vs. source data comparison
- **Metrics Display Correctness**: Chart and graph validation
- **User Interface Responsiveness**: Performance under load
- **Filtered Views & Drill-down**: Interactive functionality testing

**Example**:
```bash
python run_comprehensive_tests.py --categories dashboard --metrics
```

## Advanced Usage

### Custom Configuration

Create a custom configuration file:

```yaml
# custom_config.yaml
execution:
  max_concurrent_tests: 10
  test_timeout_seconds: 600

load_stress_tests:
  concurrent_users: [5, 15, 30, 60]
  test_duration_minutes: 10
```

Run with custom config:
```bash
python run_comprehensive_tests.py --all --config custom_config.yaml
```

### Metrics Collection

Enable comprehensive metrics collection:

```bash
python run_comprehensive_tests.py --all --metrics --detailed-report
```

This collects:
- CPU and memory usage
- Network and disk I/O
- Response times and throughput
- Error rates and patterns
- System stability indicators

### Environment-Specific Testing

Override database connections for different environments:

```bash
# Development environment
python run_comprehensive_tests.py --all --neo4j-uri bolt://dev-neo4j:7687

# Staging environment  
python run_comprehensive_tests.py --all --neo4j-uri bolt://staging-neo4j:7687 --redis-url redis://staging-redis:6379
```

### Continuous Integration

For CI/CD pipelines:

```bash
# Run with JSON output for parsing
python run_comprehensive_tests.py --all --detailed-report --log-level WARNING --output-dir ./ci-results
```

## Report Generation

The test battery generates multiple report formats:

### 1. Executive Summary (Text)
- High-level pass/fail statistics
- Key recommendations
- Critical issues identified

### 2. Detailed JSON Report
- Complete test results
- Performance metrics
- Configuration details
- Raw data export

### 3. CSV Export
- Test results in tabular format
- Suitable for spreadsheet analysis
- Performance data included

### 4. HTML Report
- Visual dashboard-style report
- Charts and graphs (when enabled)
- Interactive elements

## Troubleshooting

### Common Issues

1. **Database Connection Failures**:
   ```bash
   # Check database status
   python run_comprehensive_tests.py --dry-run --log-level DEBUG
   ```

2. **Memory Issues During Load Testing**:
   ```yaml
   # Reduce concurrent users in config
   load_stress_tests:
     concurrent_users: [1, 2, 5]
   ```

3. **Test Timeouts**:
   ```bash
   # Increase timeout
   python run_comprehensive_tests.py --all --timeout 600
   ```

### Debug Mode

Enable detailed debugging:

```bash
python run_comprehensive_tests.py --all --log-level DEBUG --log-file debug.log
```

### Partial Test Runs

Run individual test methods for debugging:

```python
# In Python shell or script
from tests.comprehensive_battery import ComprehensiveTestBattery

battery = ComprehensiveTestBattery("config/comprehensive_test_config.yaml")
results = await battery.run_standard_tests()
```

## Integration

### With pytest

The test battery integrates with existing pytest infrastructure:

```bash
# Run as pytest
pytest tests/comprehensive_battery/ -v --tb=short

# Run specific test suite
pytest tests/comprehensive_battery/test_suites/standard_test_suite.py -v
```

### With CI/CD

Example GitHub Actions workflow:

```yaml
- name: Run Comprehensive Tests
  run: |
    python tests/comprehensive_battery/run_comprehensive_tests.py \
      --all \
      --detailed-report \
      --output-dir ./test-results \
      --log-level INFO

- name: Upload Test Results
  uses: actions/upload-artifact@v2
  with:
    name: comprehensive-test-results
    path: ./test-results/
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add appropriate error handling
3. Include metrics collection
4. Update configuration as needed
5. Add documentation

### Adding New Test Categories

1. Create new test suite in `test_suites/`
2. Add to main orchestrator
3. Update CLI options
4. Add configuration section
5. Update documentation

## Performance Considerations

- **Resource Usage**: Monitor system resources during testing
- **Test Duration**: Balance thoroughness with execution time
- **Concurrent Limits**: Adjust based on system capacity
- **Database Load**: Consider impact on shared databases
- **Network Bandwidth**: Account for data transfer during tests

## Security Notes

- **Test Data**: Uses synthetic data only
- **Database Access**: Requires appropriate permissions
- **Network Security**: Tests may generate security-related traffic
- **Credential Management**: Store credentials securely
- **Test Isolation**: Ensure tests don't affect production data
