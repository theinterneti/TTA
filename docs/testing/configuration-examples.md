# TTA Comprehensive Test Battery - Configuration Examples

This document provides configuration examples for different environments and use cases.

## Environment Configurations

### Development Environment

**File**: `tests/comprehensive_battery/config/development.yaml`

```yaml
# Development environment - optimized for speed and local testing
database:
  neo4j:
    uri: "bolt://localhost:7687"
    user: "neo4j"
    password: "devpassword"
    max_connection_pool_size: 10
  redis:
    url: "redis://localhost:6379"
    max_connections: 20

execution:
  max_concurrent_tests: 3
  test_timeout_seconds: 300
  cleanup_between_tests: true
  retry_failed_tests: 1

mock_mode:
  enabled: true
  force_mock: false
  log_mock_operations: true
  fallback_on_error: true

reporting:
  output_formats: ["json", "txt"]
  detailed_reports: false
  include_metrics: true
  save_logs: true
  log_level: "INFO"

categories:
  standard:
    enabled: true
    max_concurrent: 2
  adversarial:
    enabled: true
    max_concurrent: 1
  load_stress:
    enabled: false  # Skip in development
  data_pipeline:
    enabled: true
    max_concurrent: 1
  dashboard:
    enabled: false  # Skip in development
```

### Staging Environment

**File**: `tests/comprehensive_battery/config/staging.yaml`

```yaml
# Staging environment - comprehensive testing with real services
database:
  neo4j:
    uri: "bolt://staging-neo4j:7687"
    user: "neo4j"
    password: "${NEO4J_PASSWORD}"
    max_connection_pool_size: 50
    connection_timeout: 30
  redis:
    url: "redis://staging-redis:6379"
    max_connections: 100
    socket_timeout: 10

execution:
  max_concurrent_tests: 5
  test_timeout_seconds: 600
  cleanup_between_tests: true
  retry_failed_tests: 2
  fail_fast: false

mock_mode:
  enabled: true
  force_mock: false
  log_mock_operations: false
  fallback_on_error: true

reporting:
  output_formats: ["json", "html", "csv"]
  detailed_reports: true
  include_metrics: true
  save_logs: true
  log_level: "INFO"
  webhook_url: "${SLACK_WEBHOOK_URL}"

categories:
  standard:
    enabled: true
    max_concurrent: 3
    timeout: 300
  adversarial:
    enabled: true
    max_concurrent: 2
    timeout: 600
  load_stress:
    enabled: true
    max_concurrent: 5
    timeout: 900
    concurrent_users: 50
  data_pipeline:
    enabled: true
    max_concurrent: 2
    timeout: 600
  dashboard:
    enabled: true
    max_concurrent: 1
    timeout: 300

alerts:
  enabled: true
  failure_threshold: 0.9
  email_recipients: ["team@example.com"]
  slack_channel: "#tta-alerts"
```

### Production Environment

**File**: `tests/comprehensive_battery/config/production.yaml`

```yaml
# Production environment - full testing with monitoring
database:
  neo4j:
    uri: "bolt://prod-neo4j-cluster:7687"
    user: "neo4j"
    password: "${NEO4J_PROD_PASSWORD}"
    max_connection_pool_size: 100
    connection_timeout: 60
    encrypted: true
  redis:
    url: "rediss://prod-redis-cluster:6380"
    max_connections: 200
    socket_timeout: 30
    ssl_cert_reqs: "required"

execution:
  max_concurrent_tests: 10
  test_timeout_seconds: 1200
  cleanup_between_tests: true
  retry_failed_tests: 3
  fail_fast: false
  resource_monitoring: true

mock_mode:
  enabled: false  # Production uses real services only
  force_mock: false
  log_mock_operations: false
  fallback_on_error: false

reporting:
  output_formats: ["json", "html", "csv", "junit"]
  detailed_reports: true
  include_metrics: true
  save_logs: true
  log_level: "WARNING"
  retention_days: 90
  webhook_url: "${MONITORING_WEBHOOK_URL}"

categories:
  standard:
    enabled: true
    max_concurrent: 5
    timeout: 600
  adversarial:
    enabled: true
    max_concurrent: 3
    timeout: 900
    security_focus: true
  load_stress:
    enabled: true
    max_concurrent: 10
    timeout: 1800
    concurrent_users: 200
    ramp_up_time: 300
  data_pipeline:
    enabled: true
    max_concurrent: 3
    timeout: 900
    data_consistency_checks: true
  dashboard:
    enabled: true
    max_concurrent: 2
    timeout: 600

monitoring:
  enabled: true
  metrics_endpoint: "https://metrics.example.com/tta"
  health_check_interval: 300
  performance_baseline: true

alerts:
  enabled: true
  failure_threshold: 0.95
  performance_threshold: 2.0  # seconds
  email_recipients: ["oncall@example.com", "team-lead@example.com"]
  slack_channel: "#tta-production-alerts"
  pagerduty_integration: true
```

### CI/CD Environment

**File**: `tests/comprehensive_battery/config/ci.yaml`

```yaml
# CI/CD environment - optimized for automated testing
database:
  neo4j:
    uri: "bolt://localhost:7687"
    user: "neo4j"
    password: "testpassword"
    max_connection_pool_size: 20
  redis:
    url: "redis://localhost:6379"
    max_connections: 50

execution:
  max_concurrent_tests: 3
  test_timeout_seconds: 300
  cleanup_between_tests: true
  retry_failed_tests: 1
  fail_fast: true  # Fail quickly in CI

mock_mode:
  enabled: true
  force_mock: true  # Always use mocks in CI
  log_mock_operations: false
  fallback_on_error: true

reporting:
  output_formats: ["json", "junit"]
  detailed_reports: false
  include_metrics: false
  save_logs: false
  log_level: "ERROR"

categories:
  standard:
    enabled: true
    max_concurrent: 2
    timeout: 180
  adversarial:
    enabled: true
    max_concurrent: 1
    timeout: 300
  load_stress:
    enabled: false  # Skip load tests in CI
  data_pipeline:
    enabled: true
    max_concurrent: 1
    timeout: 240
  dashboard:
    enabled: false  # Skip dashboard tests in CI

ci_specific:
  artifact_upload: true
  test_result_annotation: true
  github_status_check: true
  coverage_reporting: false
```

## Use Case Configurations

### Security Testing Focus

```yaml
# Security-focused configuration
name: "Security Validation Suite"

categories:
  adversarial:
    enabled: true
    max_concurrent: 1
    timeout: 1200
    security_tests:
      - sql_injection
      - xss_prevention
      - authentication_bypass
      - rate_limiting
      - input_validation
      - session_hijacking
      - csrf_protection

execution:
  max_concurrent_tests: 1  # Sequential for security tests
  test_timeout_seconds: 1200
  detailed_logging: true

reporting:
  security_report: true
  vulnerability_scan: true
  compliance_check: true
```

### Performance Testing Focus

```yaml
# Performance-focused configuration
name: "Performance Validation Suite"

categories:
  load_stress:
    enabled: true
    max_concurrent: 10
    timeout: 3600
    load_patterns:
      - gradual_ramp:
          start_users: 1
          end_users: 100
          duration: 600
      - spike_test:
          users: 200
          duration: 300
      - sustained_load:
          users: 50
          duration: 1800

monitoring:
  resource_tracking: true
  performance_metrics: true
  memory_profiling: true
  response_time_tracking: true

reporting:
  performance_report: true
  benchmark_comparison: true
  resource_usage_charts: true
```

### Data Integrity Focus

```yaml
# Data integrity focused configuration
name: "Data Pipeline Validation Suite"

categories:
  data_pipeline:
    enabled: true
    max_concurrent: 2
    timeout: 900
    validation_tests:
      - cross_database_consistency
      - data_migration_integrity
      - backup_restore_validation
      - concurrent_write_safety
      - transaction_rollback

database:
  consistency_checks: true
  backup_validation: true
  migration_testing: true

reporting:
  data_integrity_report: true
  consistency_metrics: true
  migration_logs: true
```

## Environment-Specific Variables

### Development (.env.development)

```bash
# Development environment variables
NODE_ENV=development
LOG_LEVEL=DEBUG

# Database connections
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=devpassword
REDIS_URL=redis://localhost:6379

# Test configuration
COMPREHENSIVE_TEST_CONFIG=development
MAX_CONCURRENT_TESTS=3
TEST_TIMEOUT=300
FORCE_MOCK_MODE=false

# Dashboard
DASHBOARD_ENABLED=true
DASHBOARD_PORT=8080
DASHBOARD_DEBUG=true
```

### Staging (.env.staging)

```bash
# Staging environment variables
NODE_ENV=staging
LOG_LEVEL=INFO

# Database connections
NEO4J_URI=bolt://staging-neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=${STAGING_NEO4J_PASSWORD}
REDIS_URL=redis://staging-redis:6379

# Test configuration
COMPREHENSIVE_TEST_CONFIG=staging
MAX_CONCURRENT_TESTS=5
TEST_TIMEOUT=600
FORCE_MOCK_MODE=false

# Monitoring
WEBHOOK_URL=${STAGING_WEBHOOK_URL}
ALERT_EMAIL=staging-team@example.com

# Dashboard
DASHBOARD_ENABLED=true
DASHBOARD_PORT=8080
DASHBOARD_DEBUG=false
```

### Production (.env.production)

```bash
# Production environment variables
NODE_ENV=production
LOG_LEVEL=WARNING

# Database connections (use secrets management)
NEO4J_URI=bolt://prod-neo4j-cluster:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=${PROD_NEO4J_PASSWORD}
REDIS_URL=rediss://prod-redis-cluster:6380

# Test configuration
COMPREHENSIVE_TEST_CONFIG=production
MAX_CONCURRENT_TESTS=10
TEST_TIMEOUT=1200
FORCE_MOCK_MODE=false

# Monitoring and alerts
WEBHOOK_URL=${PROD_MONITORING_WEBHOOK}
ALERT_EMAIL=oncall@example.com
PAGERDUTY_KEY=${PAGERDUTY_INTEGRATION_KEY}

# Dashboard
DASHBOARD_ENABLED=true
DASHBOARD_PORT=8080
DASHBOARD_DEBUG=false
DASHBOARD_API_KEY=${DASHBOARD_API_KEY}
```

## Docker Compose Configurations

### Development Stack

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  neo4j:
    image: neo4j:5-community
    ports:
      - "7687:7687"
      - "7474:7474"
    environment:
      NEO4J_AUTH: neo4j/devpassword
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_dev_data:/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data

  test-runner:
    build: .
    depends_on:
      - neo4j
      - redis
    environment:
      - COMPREHENSIVE_TEST_CONFIG=development
      - NEO4J_URI=bolt://neo4j:7687
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./test-results:/app/test-results

volumes:
  neo4j_dev_data:
  redis_dev_data:
```

### CI/CD Stack

```yaml
# docker-compose.ci.yml
version: '3.8'

services:
  neo4j:
    image: neo4j:5-community
    environment:
      NEO4J_AUTH: neo4j/testpassword
      NEO4J_PLUGINS: '["apoc"]'
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "testpassword", "RETURN 1"]
      interval: 10s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  test-runner:
    build: .
    depends_on:
      neo4j:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - COMPREHENSIVE_TEST_CONFIG=ci
      - NEO4J_URI=bolt://neo4j:7687
      - REDIS_URL=redis://redis:6379
      - FORCE_MOCK_MODE=true
    command: >
      python tests/comprehensive_battery/run_comprehensive_tests.py
      --categories standard,adversarial,data_pipeline
      --max-concurrent 2
      --timeout 300
      --output-dir /app/test-results
```

## Configuration Validation

### Validation Script

```python
# validate_config.py
import yaml
import sys
from pathlib import Path

def validate_config(config_path):
    """Validate comprehensive test battery configuration."""

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Required sections
        required_sections = ['database', 'execution', 'mock_mode', 'reporting', 'categories']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required section: {section}")
                return False

        # Validate database configuration
        db_config = config['database']
        if 'neo4j' not in db_config or 'redis' not in db_config:
            print("❌ Database configuration must include neo4j and redis")
            return False

        # Validate execution parameters
        exec_config = config['execution']
        if exec_config.get('max_concurrent_tests', 0) <= 0:
            print("❌ max_concurrent_tests must be positive")
            return False

        print("✅ Configuration validation passed")
        return True

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_config.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    if not validate_config(config_file):
        sys.exit(1)
```

## Usage Examples

### Load Configuration

```bash
# Use specific configuration file
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --config tests/comprehensive_battery/config/staging.yaml \
  --all

# Use environment-based configuration
export COMPREHENSIVE_TEST_CONFIG=production
python tests/comprehensive_battery/run_comprehensive_tests.py --all

# Override specific settings
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --config development.yaml \
  --max-concurrent 5 \
  --timeout 900 \
  --force-mock
```

### Validate Configuration

```bash
# Validate configuration file
python validate_config.py tests/comprehensive_battery/config/staging.yaml

# Test configuration with dry run
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --config staging.yaml \
  --dry-run \
  --all
```

These configuration examples provide a solid foundation for running the comprehensive test battery in different environments while maintaining flexibility and proper separation of concerns.


---
**Logseq:** [[TTA.dev/Docs/Testing/Configuration-examples]]
