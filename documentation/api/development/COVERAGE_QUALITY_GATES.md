# TTA Coverage Quality Gates Configuration

**Date:** 2025-01-31
**Phase:** 2.2 - Testing Infrastructure Improvements
**Status:** Configured with baseline thresholds

## Overview

This document defines the coverage quality gates and thresholds for the TTA project. Quality gates ensure that code coverage meets minimum standards before code can be merged or deployed.

## Current Coverage Baseline

Based on the current state of the codebase and test suite:

### Baseline Measurements (Estimated)
- **Overall Coverage:** ~70% (target baseline)
- **Unit Test Coverage:** ~65% (fast tests, no external dependencies)
- **Integration Test Coverage:** ~75% (with Neo4j/Redis)
- **Critical Path Coverage:** ~85% (core business logic)

### Coverage by Module (Estimated)
- **Agent Orchestration:** ~75%
- **API Gateway:** ~70%
- **Player Experience:** ~65%
- **Components:** ~80%
- **Therapeutic Safety:** ~90% (critical for safety)

## Quality Gate Thresholds

### Minimum Coverage Requirements

#### Overall Project
- **Minimum Total Coverage:** 70%
- **Target Coverage:** 80%
- **Aspirational Coverage:** 90%

#### By Test Type
- **Unit Tests:** Minimum 65%, Target 75%
- **Integration Tests:** Minimum 70%, Target 80%
- **End-to-End Tests:** Minimum 60%, Target 70%

#### By Module Priority
- **Critical Modules (Therapeutic Safety):** Minimum 85%, Target 95%
- **Core Modules (Agent Orchestration):** Minimum 75%, Target 85%
- **API Modules (Gateway, Player Experience):** Minimum 70%, Target 80%
- **Utility Modules (Components):** Minimum 65%, Target 75%

### Branch Coverage Requirements
- **Minimum Branch Coverage:** 60%
- **Target Branch Coverage:** 70%
- **Critical Module Branch Coverage:** 80%

## Quality Gate Rules

### Pull Request Gates
1. **Coverage Decrease Prevention:** New code must not decrease overall coverage by more than 2%
2. **New Code Coverage:** All new code must have minimum 80% coverage
3. **Critical Path Coverage:** Changes to therapeutic safety modules require 95% coverage
4. **Branch Coverage:** New branches must have minimum 70% coverage

### CI/CD Pipeline Gates
1. **Build Failure:** Coverage below minimum threshold fails the build
2. **Warning Threshold:** Coverage between minimum and target generates warnings
3. **Success Threshold:** Coverage above target passes without warnings

### Release Gates
1. **Pre-release Coverage:** Minimum 75% overall coverage required for release
2. **Critical Module Coverage:** 90% coverage required for therapeutic safety modules
3. **Regression Prevention:** No coverage decrease from previous release

## Coverage Configuration

### pytest-cov Configuration
```toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/*_test.py",
    "*/conftest.py",
    "*/venv/*",
    "*/.venv/*",
    "*/migrations/*",
    "*/scripts/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
    "except ImportError:",
    "if TYPE_CHECKING:",
]
show_missing = true
skip_covered = false
precision = 2
fail_under = 70
```

### pytest Configuration
```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-report=xml:coverage.xml",
    "--cov-report=json:coverage.json",
    "--cov-branch",
    "--cov-fail-under=70",
]
```

## Implementation Strategy

### Phase 1: Baseline Establishment (Current)
- ✅ Configure coverage reporting tools
- ✅ Set initial thresholds at current levels
- ✅ Integrate with CI/CD pipeline
- ⚠️ Resolve test import issues

### Phase 2: Gradual Improvement (Next 2 weeks)
- 🔄 Fix failing tests and import issues
- 🔄 Increase thresholds by 5% increments
- 🔄 Add coverage for uncovered critical paths
- 🔄 Implement coverage diff reporting

### Phase 3: Target Achievement (Next 4 weeks)
- 📋 Reach target coverage levels
- 📋 Implement strict quality gates
- 📋 Add coverage monitoring and alerting
- 📋 Create coverage improvement automation

## Monitoring and Reporting

### Coverage Reports
- **HTML Reports:** Interactive coverage analysis at `htmlcov/index.html`
- **XML Reports:** Machine-readable format for CI/CD integration
- **JSON Reports:** Programmatic access to coverage data
- **Terminal Reports:** Quick coverage summary in CI logs

### Coverage Tracking
- **Trend Analysis:** Track coverage changes over time
- **Module Breakdown:** Per-module coverage tracking
- **Regression Detection:** Alert on coverage decreases
- **Improvement Tracking:** Monitor progress toward targets

### Alerts and Notifications
- **Coverage Drop:** Alert when coverage decreases significantly
- **Threshold Breach:** Notify when coverage falls below minimum
- **Target Achievement:** Celebrate when targets are reached
- **Quality Gate Failure:** Immediate notification of gate failures

## Exclusions and Exceptions

### Excluded from Coverage
- Test files and test utilities
- Migration scripts and database setup
- Third-party integrations (external APIs)
- Development and debugging utilities
- Generated code and protobuf files

### Temporary Exceptions
- Files with known import issues (until resolved)
- Legacy code being refactored
- Experimental features in development
- External service mocks and stubs

## Commands and Usage

### Running Coverage Analysis
```bash
# Unit tests with coverage
uv run pytest tests/ -k "not integration" --cov=src --cov-report=html

# Integration tests with coverage
uv run pytest tests/ --neo4j --redis --cov=src --cov-report=html

# Coverage report only (no tests)
uv run coverage report --show-missing

# Generate HTML report
uv run coverage html

# Check coverage threshold
uv run coverage report --fail-under=70
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Run tests with coverage
  run: uv run pytest tests/ --cov=src --cov-report=xml

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

## Troubleshooting

### Common Issues
1. **Import Errors:** Fix module structure and dependencies
2. **Low Coverage:** Add tests for uncovered code paths
3. **Flaky Tests:** Improve test reliability and isolation
4. **Performance:** Optimize test execution time

### Resolution Steps
1. Identify root cause of coverage issues
2. Prioritize fixes based on module criticality
3. Implement fixes incrementally
4. Validate improvements with automated testing
5. Update thresholds as coverage improves

## Future Enhancements

### Planned Improvements
- **Mutation Testing:** Add mutation testing for quality validation
- **Coverage Visualization:** Interactive coverage dashboards
- **Automated Improvement:** AI-powered test generation
- **Performance Metrics:** Coverage collection performance optimization

### Integration Opportunities
- **Code Review Tools:** Coverage information in PR reviews
- **IDE Integration:** Real-time coverage feedback
- **Monitoring Systems:** Coverage metrics in observability platforms
- **Quality Dashboards:** Executive-level coverage reporting

---

**Note:** This configuration is based on the current state of the codebase. Thresholds will be adjusted as test reliability improves and coverage increases.
