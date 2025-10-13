# TTA Testing Documentation

**Comprehensive Testing Strategy and Implementation Guide**

---

## Overview

This directory contains the complete testing strategy, analysis, and implementation guide for the TTA (Text-based Adventure) storytelling system. The documentation is designed for a solo developer workflow in a WSL2 environment with emphasis on daily development efficiency.

---

## Documents

### 1. [TESTING_STRATEGY_SUMMARY.md](./TESTING_STRATEGY_SUMMARY.md) ⭐ **START HERE**

**Executive summary for quick understanding**

- Current state overview (971 test functions, 68% coverage)
- Key gaps identified
- 3-phase implementation roadmap
- Quality targets and success criteria
- Quick reference commands
- Next steps and recommendations

**Best for:** Getting a high-level understanding of the testing strategy

---

### 2. [ADVANCED_TESTING_METHODOLOGY.md](./ADVANCED_TESTING_METHODOLOGY.md) 🚀 **ADVANCED TESTING** (NEW)

**Comprehensive guide to advanced testing strategies for Model Management**

- Property-based testing with Hypothesis
- Mutation testing with Mutmut
- Performance regression testing with pytest-benchmark
- Contract testing with Pact
- Tool configuration and usage
- CI/CD integration
- Best practices and examples
- Troubleshooting guide

**Best for:** Understanding and implementing advanced testing techniques

---

### 3. [TEST_COVERAGE_ANALYSIS.md](./TEST_COVERAGE_ANALYSIS.md) 📊 **DETAILED ANALYSIS**

**Comprehensive analysis and detailed roadmap**

- Component-by-component coverage analysis
- Detailed gap identification
- Phase 1, 2, 3 implementation plans with specific test scenarios
- Quality targets and benchmarks
- CI/CD integration strategy
- Test maintainability guidelines
- Sample test templates (unit, integration, E2E)
- Commands and scripts
- Appendices (dependencies, glossary)

**Best for:** Understanding the complete testing strategy and implementation details

---

### 4. [GITHUB_WORKFLOWS_RECOMMENDATIONS.md](./GITHUB_WORKFLOWS_RECOMMENDATIONS.md) 🔄 **CI/CD GUIDE**

**GitHub Actions workflow specifications and recommendations**

- Current workflow assessment
- Recommended workflow structure
- PR validation workflow (< 5 min)
- Main branch tests workflow (< 30 min)
- Nightly comprehensive tests workflow (< 2 hours)
- Implementation plan
- Success criteria

**Best for:** Setting up and optimizing GitHub Actions workflows

---

### 5. [QUICK_REFERENCE_TESTING_GUIDE.md](./QUICK_REFERENCE_TESTING_GUIDE.md) 🚀 **DAILY REFERENCE**

**Quick reference for daily development workflow**

- Quick start commands
- Common test commands (pytest, Playwright, Locust)
- Test environment setup
- Debugging tests
- Coverage reports
- Performance testing
- Troubleshooting common issues
- Best practices
- Useful aliases

**Best for:** Daily development workflow and quick command lookup

---

## Quick Start

### For First-Time Setup

1. **Read the Executive Summary**
   ```bash
   cat docs/testing/TESTING_STRATEGY_SUMMARY.md
   ```

2. **Set Up Test Environment**
   ```bash
   # Install dependencies
   uv sync --all-extras --dev

   # Start test databases
   docker-compose -f docker-compose.test.yml up -d neo4j redis

   # Install Playwright browsers
   npx playwright install chromium firefox webkit --with-deps
   ```

3. **Run Your First Tests**
   ```bash
   # Unit tests (fast)
   uv run pytest -q

   # Integration tests (with databases)
   uv run pytest -q --neo4j --redis

   # E2E tests
   npx playwright test tests/e2e/specs/auth.spec.ts
   ```

4. **Review Detailed Documentation**
   - Read [TEST_COVERAGE_ANALYSIS.md](./TEST_COVERAGE_ANALYSIS.md) for complete strategy
   - Review [GITHUB_WORKFLOWS_RECOMMENDATIONS.md](./GITHUB_WORKFLOWS_RECOMMENDATIONS.md) for CI/CD setup

---

### For Daily Development

**Keep [QUICK_REFERENCE_TESTING_GUIDE.md](./QUICK_REFERENCE_TESTING_GUIDE.md) handy!**

```bash
# Morning: Pull and test
git pull origin main
uv run pytest -q

# During development: Test frequently
uv run pytest tests/test_my_feature.py -v

# Before commit: Validate
uv run pytest -q -m "not neo4j and not redis"
uv run ruff check .

# Before PR: Full validation
docker-compose -f docker-compose.test.yml up -d
uv run pytest -q --neo4j --redis --cov=src
npx playwright test tests/e2e/specs/auth.spec.ts
```

---

## Testing Strategy at a Glance

### Current State
- ✅ **971 Python test functions** across 123 files
- ✅ **20 TypeScript E2E specs** with Playwright
- ✅ **7 GitHub Actions workflows** for CI/CD
- ✅ **~68% overall code coverage**

### Key Gaps
- ❌ End-to-end user journeys with real database persistence
- ❌ Multi-session continuity testing
- ❌ Complete API endpoint coverage
- ❌ Frontend component unit tests

### Implementation Phases

**Phase 1 (Weeks 1-2): Critical Path** - Authentication, story creation, database persistence, core gameplay
**Phase 2 (Weeks 3-4): User Experience** - Complete journeys, frontend UI/UX, error handling
**Phase 3 (Weeks 5-6): Robustness** - Performance, failure scenarios, browser compatibility

### Quality Targets
- **Code Coverage:** 80% overall, 90%+ for critical components
- **Narrative Quality:** Coherence ≥7.5/10, Consistency ≥7.5/10, Engagement ≥7.0/10
- **Performance:** API < 200ms, Database < 50ms, Frontend FCP < 1.5s
- **Zero Critical Bugs:** No auth failures, data loss, crashes, or security vulnerabilities

---

## Test Types

### Traditional Testing

#### Unit Tests
- **Purpose:** Test individual functions/classes in isolation
- **Tools:** pytest, unittest.mock
- **Execution:** Fast (< 1 minute)
- **Command:** `uvx pytest -q`

#### Integration Tests
- **Purpose:** Test component interactions with real databases
- **Tools:** pytest with --neo4j and --redis markers
- **Execution:** Moderate (5-10 minutes)
- **Command:** `uvx pytest -q --neo4j --redis`

#### End-to-End Tests
- **Purpose:** Test complete user journeys from frontend to backend
- **Tools:** Playwright
- **Execution:** Slow (15-30 minutes)
- **Command:** `npx playwright test`

### Advanced Testing (NEW)

#### Property-Based Tests
- **Purpose:** Automatically discover edge cases by testing invariants
- **Tools:** Hypothesis
- **Execution:** Fast (< 2 minutes)
- **Command:** `uvx pytest -m property`
- **Coverage Target:** 100% of critical algorithms

#### Mutation Tests
- **Purpose:** Validate test suite effectiveness by introducing code mutations
- **Tools:** Mutmut
- **Execution:** Very slow (30-60 minutes)
- **Command:** `uvx mutmut run --paths-to-mutate=src/components/model_management`
- **Mutation Score Target:** 90% overall, 100% critical paths
- **Frequency:** Weekly in CI/CD only

#### Performance Regression Tests
- **Purpose:** Detect performance degradation over time
- **Tools:** pytest-benchmark
- **Execution:** Fast (< 5 minutes)
- **Command:** `uvx pytest tests/performance/benchmarks/ --benchmark-only`
- **Threshold:** Fail if performance degrades > 20%

#### Contract Tests
- **Purpose:** Validate API contracts between frontend and backend
- **Tools:** Pact Python
- **Execution:** Fast (< 2 minutes)
- **Command:** `uvx pytest tests/contracts/`
- **Coverage Target:** 100% of API endpoints

### Performance Tests
- **Purpose:** Validate system performance under load
- **Tools:** Locust, pytest-benchmark
- **Execution:** Variable (10-60 minutes)
- **Command:** `locust -f testing/load_tests/locustfile.py`

---

## CI/CD Integration

### PR Validation (< 5 minutes)
- Unit tests with mocks
- Linting and code quality
- Security scans
- Mock-based integration tests

### Main Branch (< 30 minutes)
- All unit tests
- Integration tests with real databases
- Core E2E tests
- Performance regression checks

### Nightly (< 2 hours)
- Full test suite
- Extended E2E tests (all browsers)
- Performance and load tests
- Visual regression tests

---

## Key Commands

### Run Tests
```bash
# Unit tests
uv run pytest -q

# Integration tests
uv run pytest -q --neo4j --redis

# E2E tests
npx playwright test

# With coverage
uv run pytest --cov=src --cov-report=html
```

### Start Test Environment
```bash
# Databases
docker-compose -f docker-compose.test.yml up -d neo4j redis

# Full environment
./scripts/start-test-environment.sh
```

### Debug Tests
```bash
# Python tests with debugger
uv run pytest --pdb

# Playwright in debug mode
npx playwright test --debug
```

---

## Resources

### Internal Documentation
- [TEST_COVERAGE_ANALYSIS.md](./TEST_COVERAGE_ANALYSIS.md) - Detailed analysis and roadmap
- [GITHUB_WORKFLOWS_RECOMMENDATIONS.md](./GITHUB_WORKFLOWS_RECOMMENDATIONS.md) - CI/CD setup
- [QUICK_REFERENCE_TESTING_GUIDE.md](./QUICK_REFERENCE_TESTING_GUIDE.md) - Daily reference
- [TESTING_STRATEGY_SUMMARY.md](./TESTING_STRATEGY_SUMMARY.md) - Executive summary

### External Resources
- [pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Locust Documentation](https://docs.locust.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## Contributing

### Adding New Tests

1. **Choose the right test type** (unit, integration, E2E)
2. **Follow naming conventions** (`test_*.py`, `*.spec.ts`)
3. **Use appropriate markers** (`@pytest.mark.neo4j`, etc.)
4. **Write clear test names** (`test_user_can_login_with_valid_credentials`)
5. **Add docstrings** explaining what the test validates
6. **Follow test templates** from [TEST_COVERAGE_ANALYSIS.md](./TEST_COVERAGE_ANALYSIS.md)

### Updating Documentation

1. **Keep documents in sync** when making changes
2. **Update version numbers** and last updated dates
3. **Test all commands** before documenting them
4. **Add examples** for clarity
5. **Link related documents** for easy navigation

---

## Support

### Getting Help

1. **Check the Quick Reference Guide** for common commands and troubleshooting
2. **Review the Detailed Analysis** for comprehensive information
3. **Check GitHub Issues** for known problems
4. **Ask in team chat** (if applicable)

### Reporting Issues

1. **Document the issue** with steps to reproduce
2. **Include test output** and error messages
3. **Specify environment** (WSL2, Python version, etc.)
4. **Suggest a fix** if possible

---

## Changelog

### Version 1.1 (2025-10-10)
- **NEW:** Advanced Testing Methodology documentation
- Added property-based testing with Hypothesis
- Added mutation testing with Mutmut
- Added performance regression testing with pytest-benchmark
- Added contract testing with Pact Python
- Updated pyproject.toml with new testing dependencies
- Added pytest markers for advanced testing types
- Added comprehensive examples and troubleshooting guide
- Updated test type documentation

### Version 1.0 (2025-10-03)
- Initial comprehensive testing strategy documentation
- Current state analysis (971 tests, 68% coverage)
- 3-phase implementation roadmap
- GitHub Actions workflow recommendations
- Quick reference guide for daily workflow
- Test templates and best practices

---

## License

This documentation is part of the TTA project and follows the same license as the main project.

---

**Documentation Version:** 1.1
**Last Updated:** 2025-10-10
**Maintained by:** The Augster (AI Development Assistant)
**Status:** Ready for Use

---

## Quick Links

- ⭐ [Executive Summary](./TESTING_STRATEGY_SUMMARY.md)
- 🚀 [Advanced Testing Methodology](./ADVANCED_TESTING_METHODOLOGY.md) **(NEW)**
- 📊 [Detailed Analysis](./TEST_COVERAGE_ANALYSIS.md)
- 🔄 [CI/CD Guide](./GITHUB_WORKFLOWS_RECOMMENDATIONS.md)
- 🚀 [Quick Reference](./QUICK_REFERENCE_TESTING_GUIDE.md)
