# Testing Infrastructure Guide

**Complete guide to TTA's testing infrastructure, coverage reporting, VS Code integration, and troubleshooting.**

---

## Table of Contents

- [Overview](#overview)
- [Running Tests](#running-tests)
- [Coverage Reporting](#coverage-reporting)
- [VS Code Integration](#vs-code-integration)
- [CI/CD Integration](#cicd-integration)
- [Git Hooks](#git-hooks)
- [Troubleshooting](#troubleshooting)
- [AI Agent Guide](#ai-agent-guide)

---

## Overview

TTA's testing infrastructure provides comprehensive validation across multiple layers:

### Testing Philosophy

- **Automated by Default**: Coverage runs automatically with every test execution
- **Fast Feedback**: Unit tests run in seconds, integration tests in minutes
- **Developer-Friendly**: VS Code integration for seamless test discovery, execution, and debugging
- **Quality Gates**: Coverage thresholds enforced at staging (70%) and production (80%)
- **CI/CD Integration**: Automated testing on every PR and merge

### Testing Layers

| Layer | Purpose | Duration | Coverage Target |
|-------|---------|----------|-----------------|
| **Unit Tests** | Test individual functions/classes in isolation | ~30s | 80%+ |
| **Integration Tests** | Test component interactions with real services | ~2-5min | 70%+ |
| **E2E Tests** | Test complete user workflows | ~10-15min | 60%+ |
| **Comprehensive Battery** | Multi-dimensional testing (standard, adversarial, load) | ~30-60min | 70%+ |

### Key Components

- **pytest**: Test framework with async support
- **pytest-cov**: Coverage measurement and reporting
- **pytest-asyncio**: Async test support
- **pytest-benchmark**: Performance benchmarking
- **Hypothesis**: Property-based testing
- **Coverage Gutters**: VS Code extension for inline coverage visualization

---

## Running Tests

### Standard Commands

**IMPORTANT**: Always use `uv run pytest` (NOT `uvx pytest`) to ensure correct coverage reporting.

```bash
# Run all tests (coverage runs by default)
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with extra verbose output (show test names)
uv run pytest -vv

# Run quietly (minimal output)
uv run pytest -q
```

### Test Selection

```bash
# Run specific test types
uv run pytest tests/unit/              # Unit tests only
uv run pytest tests/integration/       # Integration tests only
uv run pytest tests/e2e/              # End-to-end tests only

# Run specific file
uv run pytest tests/unit/test_example.py

# Run specific test function
uv run pytest tests/unit/test_example.py::test_function_name

# Run specific test class
uv run pytest tests/unit/test_example.py::TestClassName

# Run specific test method
uv run pytest tests/unit/test_example.py::TestClassName::test_method_name
```

### Test Filtering with Markers

```bash
# Skip slow tests
uv run pytest -m "not slow"

# Run only database tests
uv run pytest -m "redis or neo4j"

# Run only unit tests (by marker)
uv run pytest -m unit

# Run only integration tests (by marker)
uv run pytest -m integration

# Combine markers
uv run pytest -m "unit and not slow"
```

### Test Re-running

```bash
# Run only failed tests from last run
uv run pytest --lf

# Run failed tests first, then all others
uv run pytest --ff

# Run tests that failed in the last run, stop on first failure
uv run pytest --lf -x
```

### Integration Tests with Services

Integration tests require Redis and Neo4j services:

```bash
# Start services
docker-compose up -d redis neo4j

# Run integration tests
uv run pytest tests/integration/ --neo4j --redis

# Stop services
docker-compose down
```

---

## Coverage Reporting

### Automatic Coverage

Coverage runs **automatically** with every test execution via `pyproject.toml` configuration:

```toml
[tool.pytest.ini_options]
addopts = "-ra -q --strict-markers --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml"
```

### Coverage Reports

Three coverage reports are generated automatically:

1. **Terminal Report**: Displayed after test execution
   - Shows coverage percentage per file
   - Highlights missing lines with `--cov-report=term-missing`

2. **HTML Report**: Interactive coverage visualization
   - Generated in `htmlcov/` directory
   - View with: `open htmlcov/index.html` (macOS) or `xdg-open htmlcov/index.html` (Linux)
   - Shows line-by-line coverage with color coding

3. **XML Report**: Machine-readable coverage data
   - Generated as `coverage.xml`
   - Used by CI/CD and coverage tools

### Coverage Thresholds

Coverage thresholds are enforced via `pyproject.toml`:

```toml
[tool.coverage.report]
fail_under = 70.0  # Tests fail if coverage < 70%
```

**Component Maturity Thresholds:**
- **Development**: No minimum (but aim for 70%+)
- **Staging**: 70% minimum (enforced)
- **Production**: 80% minimum (enforced)

### Viewing Coverage

```bash
# Run tests (coverage generated automatically)
uv run pytest

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# View terminal coverage report
uv run pytest  # Already shown after tests

# Generate coverage report without running tests
uv run coverage report

# Generate HTML report from existing coverage data
uv run coverage html
```

### Coverage Configuration

Coverage is configured in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
]
branch = true  # Measure branch coverage

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
fail_under = 70.0
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"

[tool.coverage.xml]
output = "coverage.xml"
```

---

## VS Code Integration

### Test Discovery and Execution

VS Code's Testing panel provides seamless test discovery and execution:

1. **Open Testing Panel**: Click beaker icon in Activity Bar (left sidebar)
2. **Discover Tests**: Tests are automatically discovered on workspace open
3. **Run Tests**:
   - Click ▶️ next to test/file/folder to run
   - Click ⟳ to refresh test discovery
   - Click ⏸️ to stop running tests

**Test Discovery Configuration** (`.vscode/settings.json`):

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests"
  ]
}
```

### Debugging Tests

Debug tests directly from VS Code:

**Method 1: Testing Panel**
1. Right-click test in Testing panel
2. Select "Debug Test"
3. Debugger starts with breakpoints active

**Method 2: Debug Configurations**

Available debug configurations (`.vscode/launch.json`):

- **Debug Current Test File**: Debug all tests in current file
- **Debug Current Test Function**: Debug selected test function
- **Debug All Tests**: Debug entire test suite
- **Debug Integration Tests**: Debug integration tests with service configuration

**Usage:**
1. Open test file
2. Set breakpoints (click left of line number)
3. Press `F5` or select debug configuration from Debug panel
4. Step through code with `F10` (step over), `F11` (step into), `Shift+F11` (step out)

### Coverage Visualization

**Coverage Gutters** extension provides inline coverage indicators:

**Installation:**
1. Install "Coverage Gutters" extension (ryanluker.vscode-coverage-gutters)
2. Run tests to generate coverage: `uv run pytest`
3. Open source file
4. Coverage indicators appear in gutter:
   - ✅ **Green**: Line covered by tests
   - ❌ **Red**: Line not covered by tests
   - ⚠️ **Yellow**: Partial branch coverage

**Usage:**
- **Watch Mode**: Click "Watch" in status bar to auto-update coverage
- **Manual Update**: Click "Display Coverage" in status bar
- **Remove Coverage**: Click "Remove Coverage" in status bar

### VS Code Tasks

Pre-configured tasks for common testing operations (`.vscode/tasks.json`):

**Run Tasks**: `Ctrl+Shift+P` → "Tasks: Run Task" → Select task

Available tasks:
- **Test: Run All Tests**: `uv run pytest`
- **Test: Run All Tests with Coverage**: `uv run pytest --cov=src --cov-report=html --cov-report=term-missing`
- **Test: Run Unit Tests**: `uv run pytest tests/unit/`
- **Test: Run Integration Tests**: `uv run pytest tests/integration/ --neo4j --redis`
- **Test: Run Current File Tests**: `uv run pytest ${file}`
- **Test: Run Failed Tests**: `uv run pytest --lf`

**Keyboard Shortcuts**: Configure in `.vscode/keybindings.json` (optional)

---

## CI/CD Integration

### GitHub Actions Workflows

Tests run automatically in CI/CD via GitHub Actions:

**Workflow Files:**
- `.github/workflows/tests.yml`: Unit and integration tests on every PR
- `.github/workflows/code-quality.yml`: Linting, type checking, security scans
- `.github/workflows/e2e-tests.yml`: End-to-end tests on main branch
- `.github/workflows/comprehensive-test-battery.yml`: Full test battery (scheduled)

### Test Execution in CI/CD

**On Pull Request:**
1. Unit tests run with coverage
2. Integration tests run with Docker services
3. Coverage report uploaded as artifact
4. Coverage threshold enforced (70% minimum)
5. PR blocked if tests fail or coverage < 70%

**On Merge to Main:**
1. Full test battery runs
2. E2E tests run
3. Performance benchmarks run
4. Coverage reports archived

**Scheduled (Daily 2 AM UTC):**
1. Comprehensive test battery runs
2. Mutation testing runs (weekly)
3. Security scans run
4. Reports emailed to maintainers

### Coverage Artifacts

Coverage reports are uploaded as GitHub Actions artifacts:

**Download Coverage Reports:**
1. Go to GitHub Actions run
2. Scroll to "Artifacts" section
3. Download `coverage-report` artifact
4. Extract and open `htmlcov/index.html`

### Coverage Enforcement

Coverage thresholds are enforced in CI/CD:

```yaml
# .github/workflows/tests.yml
- name: Run tests with coverage
  run: uv run pytest  # Fails if coverage < 70%
```

**Threshold Configuration:**
- Development: No enforcement (but aim for 70%+)
- Staging: 70% minimum (enforced in CI/CD)
- Production: 80% minimum (enforced in CI/CD)

---

## Git Hooks

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

**Configured Hooks** (`.pre-commit-config.yaml`):

1. **trailing-whitespace**: Remove trailing whitespace
2. **end-of-file-fixer**: Ensure files end with newline
3. **check-yaml/toml/json**: Validate file syntax
4. **check-added-large-files**: Prevent large files (>1MB)
5. **ruff**: Lint and auto-fix Python code
6. **ruff-format**: Format Python code
7. **bandit**: Security vulnerability scanning
8. **detect-secrets**: Prevent secret leaks
9. **conventional-pre-commit**: Enforce conventional commit messages
10. **run-tests-on-changed-files**: Run tests for changed source files (optional)

### Pre-commit Test Hook (Optional)

The `run-tests-on-changed-files` hook runs tests only for the source files you've changed, providing fast feedback before commit.

**How it works:**
- Detects changed Python files in `src/`
- Maps each file to corresponding test files:
  - `src/module/file.py` → `tests/unit/module/test_file.py`
  - `src/module/file.py` → `tests/integration/module/test_file.py`
- Runs only the relevant tests with `uv run pytest`
- Has a 60-second timeout for safety

**Example output:**
```
🧪 Running tests for 2 test file(s):
  - tests/unit/agent_orchestration/test_service.py
  - tests/integration/agent_orchestration/test_service.py

============================= test session starts ==============================
...
✅ All tests passed!
```

**Skipping the test hook:**

```bash
# Skip test hook only (other hooks still run)
SKIP=run-tests-on-changed-files git commit -m "wip: work in progress"

# Skip all hooks
git commit --no-verify -m "docs: update README"
```

**When to skip:**
- Work-in-progress commits
- Documentation-only changes
- Large refactoring (run tests manually instead)
- When tests are already passing (verified manually)

### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
pre-commit run bandit --all-files

# Run hooks on staged files only
pre-commit run
```

### Skipping Hooks

```bash
# Skip all hooks
git commit --no-verify -m "commit message"

# Skip specific hook
SKIP=ruff git commit -m "commit message"

# Skip multiple hooks
SKIP=ruff,bandit git commit -m "commit message"
```

**When to Skip:**
- Emergency hotfixes (use `--no-verify` sparingly)
- Work-in-progress commits (use `SKIP=` for specific hooks)
- Large refactoring (skip formatting temporarily)

---

## Troubleshooting

### Common Issues

#### Issue: Coverage Shows 0%

**Symptom**: Running tests shows 0% coverage or no coverage report

**Cause**: Using `uvx pytest` instead of `uv run pytest`

**Solution**:
```bash
# ❌ Wrong: uvx pytest (isolated environment, no coverage)
uvx pytest

# ✅ Correct: uv run pytest (project environment, coverage works)
uv run pytest
```

**Why**: `uvx pytest` runs in an isolated environment without access to project dependencies, causing coverage to fail.

#### Issue: Import Errors

**Symptom**: `ModuleNotFoundError` or `ImportError` when running tests

**Cause**: Virtual environment not activated or dependencies not installed

**Solution**:
```bash
# Verify virtual environment
which python  # Should show .venv/bin/python

# Activate virtual environment (if needed)
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate  # Windows

# Sync dependencies
uv sync --all-extras

# Run tests
uv run pytest
```

#### Issue: Database Connection Errors

**Symptom**: Tests fail with Redis or Neo4j connection errors

**Cause**: Services not running or incorrect configuration

**Solution**:
```bash
# Check services are running
docker-compose ps

# Start services
docker-compose up -d redis neo4j

# Verify services are healthy
docker-compose ps  # Should show "Up" status

# Run integration tests
uv run pytest tests/integration/ --neo4j --redis
```

#### Issue: Tests Hang or Timeout

**Symptom**: Tests run indefinitely or timeout

**Cause**: Async tests not properly configured or deadlock

**Solution**:
```bash
# Run with timeout
uv run pytest --timeout=60  # 60 second timeout per test

# Run with verbose output to see where it hangs
uv run pytest -vv -s

# Check for async issues
# Ensure pytest-asyncio is installed
uv add --dev pytest-asyncio

# Verify asyncio_mode in pyproject.toml
# [tool.pytest.ini_options]
# asyncio_mode = "auto"
```

#### Issue: Coverage Gutters Not Showing

**Symptom**: No coverage indicators in VS Code editor

**Cause**: Coverage Gutters extension not installed or coverage.xml not found

**Solution**:
1. Install Coverage Gutters extension: `ryanluker.vscode-coverage-gutters`
2. Run tests to generate coverage: `uv run pytest`
3. Verify `coverage.xml` exists in project root
4. Open source file
5. Click "Watch" in Coverage Gutters status bar
6. If still not showing, reload VS Code: `Ctrl+Shift+P` → "Reload Window"

#### Issue: Tests Pass Locally but Fail in CI/CD

**Symptom**: Tests pass on local machine but fail in GitHub Actions

**Cause**: Environment differences, missing dependencies, or timing issues

**Solution**:
```bash
# Run tests in clean environment
uv venv --force  # Recreate virtual environment
uv sync --all-extras  # Reinstall dependencies
uv run pytest  # Run tests

# Check for environment-specific issues
# - Hardcoded paths (use pathlib)
# - Timezone assumptions (use UTC)
# - File permissions (check in CI logs)
# - Service availability (ensure Docker services start)

# Review CI logs
# - Check GitHub Actions logs for specific error
# - Look for "FAILED" or "ERROR" messages
# - Check service startup logs
```

#### Issue: Slow Test Execution

**Symptom**: Tests take too long to run

**Cause**: Too many tests, slow fixtures, or inefficient test setup

**Solution**:
```bash
# Run only fast tests
uv run pytest -m "not slow"

# Run tests in parallel (requires pytest-xdist)
uv add --dev pytest-xdist
uv run pytest -n auto  # Auto-detect CPU cores

# Profile slow tests
uv run pytest --durations=10  # Show 10 slowest tests

# Optimize fixtures
# - Use session-scoped fixtures for expensive setup
# - Use function-scoped fixtures for test isolation
# - Mock external services when possible
```

### Debugging Tips

**Enable Verbose Output:**
```bash
# Show test names and outcomes
uv run pytest -v

# Show test names, outcomes, and print statements
uv run pytest -vv -s

# Show full diff on assertion failures
uv run pytest -vv --tb=long
```

**Use Debugger:**
```bash
# Drop into debugger on failure
uv run pytest --pdb

# Drop into debugger on first failure
uv run pytest -x --pdb

# Use VS Code debugger (recommended)
# Set breakpoint → F5 → Step through code
```

**Inspect Test Output:**
```bash
# Capture and display print statements
uv run pytest -s

# Show local variables on failure
uv run pytest -l

# Show full traceback
uv run pytest --tb=long
```

---

## AI Agent Guide

**Standardized commands for AI agents to ensure consistent, correct test execution.**

### Critical Rules

1. **ALWAYS use `uv run pytest`** (NOT `uvx pytest`)
   - `uvx pytest` runs in isolated environment → 0% coverage
   - `uv run pytest` runs in project environment → correct coverage

2. **Coverage runs by default** (no need for `--cov` flags)
   - Configured in `pyproject.toml`
   - Reports generated automatically in `htmlcov/` and `coverage.xml`

3. **Verify services before integration tests**
   - Check `docker-compose ps` shows services running
   - Start with `docker-compose up -d redis neo4j`

### Standard Commands

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test types
uv run pytest tests/unit/              # Unit tests
uv run pytest tests/integration/       # Integration tests (requires services)
uv run pytest tests/e2e/              # End-to-end tests

# Run specific file
uv run pytest tests/unit/test_example.py

# Run specific test
uv run pytest tests/unit/test_example.py::test_function_name

# Run failed tests only
uv run pytest --lf

# Run with timeout
uv run pytest --timeout=60
```

### Expected Outputs

**Successful Test Run:**
```
============================= test session starts ==============================
platform linux -- Python 3.12.0, pytest-8.0.0, pluggy-1.4.0
rootdir: /path/to/project
configfile: pyproject.toml
plugins: asyncio-0.23.0, cov-4.1.0
collected 150 items

tests/unit/test_example.py ......................                        [ 15%]
tests/integration/test_redis.py ..........                               [ 21%]
...

---------- coverage: platform linux, python 3.12.0-final-0 -----------
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
src/module.py              100     10    90%   45-50, 78
src/service.py             200     20    90%   120-125, 180-185
------------------------------------------------------
TOTAL                      300     30    90%

Required test coverage of 70.0% reached. Total coverage: 90.00%
========================== 150 passed in 5.23s ==============================
```

**Failed Test Run:**
```
============================= test session starts ==============================
...
FAILED tests/unit/test_example.py::test_function - AssertionError: ...
========================== 1 failed, 149 passed in 5.45s ====================
```

**Coverage Below Threshold:**
```
FAILED: Required test coverage of 70.0% not reached. Total coverage: 65.00%
```

### Common Failure Scenarios

| Symptom | Cause | Solution |
|---------|-------|----------|
| Coverage 0% | Using `uvx pytest` | Use `uv run pytest` |
| Import errors | Virtual environment not activated | Run `uv sync --all-extras` |
| Database errors | Services not running | Run `docker-compose up -d redis neo4j` |
| Tests hang | Async configuration issue | Check `asyncio_mode = "auto"` in `pyproject.toml` |
| Tests fail in CI | Environment differences | Check CI logs, verify dependencies |

### Troubleshooting Decision Tree

```
Test execution failed?
├─ Coverage shows 0%?
│  └─ YES → Using 'uvx pytest'? → Use 'uv run pytest' instead
│
├─ Import errors (ModuleNotFoundError)?
│  └─ YES → Run 'uv sync --all-extras' → Retry
│
├─ Database connection errors?
│  └─ YES → Run 'docker-compose up -d redis neo4j' → Retry
│
├─ Tests hang or timeout?
│  └─ YES → Add '--timeout=60' flag → Check async configuration
│
└─ Tests pass locally but fail in CI?
   └─ YES → Check GitHub Actions logs → Review environment differences
```

### Best Practices for AI Agents

1. **Always verify command before execution**
   - Check using `uv run pytest` (not `uvx pytest`)
   - Verify services running for integration tests

2. **Read test output carefully**
   - Check coverage percentage
   - Identify failed tests
   - Review error messages

3. **Follow troubleshooting decision tree**
   - Don't retry same command repeatedly
   - Apply appropriate fix based on error
   - Verify fix before retrying

4. **Report results clearly**
   - State pass/fail status
   - Report coverage percentage
   - List failed tests (if any)
   - Suggest next steps

### Example Workflow

```bash
# 1. Verify environment
uv sync --all-extras

# 2. Start services (if running integration tests)
docker-compose up -d redis neo4j

# 3. Run tests
uv run pytest -v

# 4. Check results
# - All tests passed? ✓
# - Coverage ≥ 70%? ✓
# - No errors? ✓

# 5. View coverage report (optional)
open htmlcov/index.html

# 6. Stop services (if started)
docker-compose down
```

---

## Additional Resources

- **[Testing Infrastructure Validation Checklist](TESTING_INFRASTRUCTURE_VALIDATION.md)**: Comprehensive validation procedures for testing infrastructure
- **[AI Agent Testing Guide](AI_AGENT_TESTING_GUIDE.md)**: Quick reference for AI agents (focused, concise)
- **[pytest Documentation](https://docs.pytest.org/)**: Official pytest documentation
- **[Coverage.py Documentation](https://coverage.readthedocs.io/)**: Coverage measurement documentation
- **[VS Code Testing](https://code.visualstudio.com/docs/python/testing)**: VS Code Python testing guide
- **[Component Maturity Workflow](COMPONENT_MATURITY_WORKFLOW.md)**: Quality gates and promotion criteria
- **[Contributing Guide](CONTRIBUTING.md)**: Development workflow and standards

---

**Last Updated**: 2025-10-23
**Maintained By**: TTA Development Team


