# Keploy Visual Guide

Quick visual reference for TTA's automated testing with Keploy.

## 🎯 Master Testing Menu

The interactive control panel for all testing operations:

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🚀 TTA AUTOMATED TESTING - COMPLETE INTEGRATION 🚀          ║
║                                                                ║
║   Powered by Keploy - Zero Manual Test Writing                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📊 Current Status: 9 test cases ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
What would you like to do?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1) 🎬 Record New Tests (Simple API)
  2) 🧪 Run All Automated Tests
  3) 📊 View Test Results
  4) 🔄 Re-record Tests (Fresh)
  5) 🎮 Record Player Experience API Tests (when available)
  6) 📈 Generate Coverage Report
  7) 🚀 Full Workflow (Record + Test + Report)
  8) ⚙️  Setup Pre-Commit Hook
  9) 📝 View Documentation
  0) 🚪 Exit

Enter choice [0-9]:
```

**Command**: `./master-tta-testing.sh`

---

## 📊 Test Execution Output

Example output from running Keploy tests:

```bash
$ ./complete-keploy-workflow.sh

🚀 TTA Keploy Automated Testing Workflow
========================================

Step 1/3: Starting API Server...
✅ API server started on port 8000

Step 2/3: Running Keploy Tests...

🧪 Test Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Suite: Health & Status
  ✅ test-1.yaml - GET /health (PASS)
  ✅ test-2.yaml - GET / (PASS)

Suite: Session Management
  ✅ test-3.yaml - POST /api/v1/sessions (adventure) (PASS)
  ✅ test-4.yaml - POST /api/v1/sessions (mystery) (PASS)
  ✅ test-5.yaml - GET /api/v1/sessions/:id (PASS)
  ✅ test-6.yaml - GET /api/v1/sessions (PASS)
  ⚠️  test-7.yaml - DELETE /api/v1/sessions/:id (FAIL)
      Expected: 204 No Content
      Got: 404 Not Found
      Reason: Session already deleted

Suite: Error Handling
  ✅ test-8.yaml - GET /api/v1/sessions/invalid (PASS)
  ✅ test-9.yaml - POST /api/v1/sessions (invalid) (PASS)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Summary:
   Total: 9 tests
   Passed: 8 (88.9%)
   Failed: 1 (11.1%)

✅ Test suite execution complete!

---

## 🔗 Reusable Keploy Framework (TTA.dev)

**Status**: ✅ Production-ready and tested (October 2025)

We've extracted a generic, production-ready Keploy automation framework into the `TTA.dev` repository at `packages/keploy-framework`. This package is now available for any Python project that wants to add Keploy-based API testing.

**What it provides:**

- **One-command setup**: `keploy-setup` (creates `keploy.yml`, `scripts/`, templates)
- **Python API**: `KeployTestRunner`, `RecordingSession`, `ResultValidator` (programmatic test runs)
- **CLI Tools**: `keploy-setup`, `keploy-test`, `keploy-record` commands
- **Templates**: GitHub Actions workflow, pre-commit hook, `keploy.yml` template
- **Examples**: `examples/fastapi_example.py` with complete FastAPI demo
- **Documentation**: Comprehensive README (400+ lines) and developer guide

**Installation:**

```bash
# From PyPI (when published)
pip install keploy-framework

# From source (development)
pip install git+https://github.com/theinterneti/TTA.dev.git#subdirectory=packages/keploy-framework

# Local development install
cd ~/repos/TTA.dev/packages/keploy-framework
pip install -e ".[dev]"
```

**Quick Start:**

```python
from keploy_framework import KeployTestRunner, ResultValidator

# Run tests with validation
runner = KeployTestRunner(api_url="http://localhost:8000")
results = await runner.run_all_tests(validate=True, generate_report=True)

# Validate results
validator = ResultValidator(min_pass_rate=0.8)
validator.assert_pass_rate(results)  # Raises if <80% pass rate
```

**Reference Implementation:**

TTA uses this framework and serves as the reference implementation:
- 9 automated test cases
- 88.9% pass rate in production
- Complete CI/CD integration
- Interactive menu system

**Full documentation:**

https://github.com/theinterneti/TTA.dev/tree/feature/keploy-framework/packages/keploy-framework

---
```

---

## 📁 Test Case Structure

Each test is stored as a YAML file with complete request/response data:

### Example: Create Session Test

**File**: `keploy/tests/test-3.yaml`

```yaml
version: api.keploy.io/v1beta2
kind: Http
name: create-adventure-session
spec:
  metadata:
    name: Create Adventure Session
    type: http
  req:
    method: POST
    proto_major: 1
    proto_minor: 1
    url: http://localhost:8000/api/v1/sessions
    header:
      Content-Type: application/json
      Accept: application/json
    body: |
      {
        "type": "adventure",
        "title": "The Lost Temple",
        "description": "A thrilling adventure quest"
      }
  resp:
    status_code: 201
    header:
      Content-Type: application/json
    body: |
      {
        "id": "session-12345",
        "type": "adventure",
        "title": "The Lost Temple",
        "description": "A thrilling adventure quest",
        "created_at": "2025-10-28T14:00:00Z",
        "status": "active"
      }
  created: 1730123456
  noise:
    - id
    - created_at
```

---

## 🔄 Recording Workflow

Visual representation of the test recording process:

```
Developer Action          Keploy Action           Result
─────────────────        ─────────────────       ────────────────

1. Start API              Monitor traffic         🎧 Listening...
   ./record-tests.sh      on port 8000

2. Make API calls         Capture requests        📝 Recording...
   POST /sessions         and responses
   GET /sessions
   DELETE /sessions

3. Stop recording         Save test cases         ✅ 9 tests saved
   Ctrl+C                 to YAML files

4. Review tests           Validate format         ✅ All valid
   cat keploy/tests/

5. Commit tests           Version control         ✅ In git
   git add keploy/
```

---

## 🎮 API Coverage Map

Visual map of tested endpoints:

```
TTA Simple API (Port 8000)
│
├── Health & Status
│   ├── ✅ GET /health

    # Act
    result = await function_with_bug()

    # Assert
    assert result == expected_result  # Currently fails
```
**Implement Fix:**
```python
# Step 2: Implement fix
async def function_with_bug():
    # Before: Buggy implementation
    # if condition:  # ❌ Wrong condition

    # After: Fixed implementation
    if correct_condition:  # ✅ Correct condition
        return expected_result
```
**Verify Fix:**
```bash
# Step 3: Run regression test
uv run pytest tests/test_{component}.py::test_bug_fix_regression -v

# Step 4: Run all tests
uv run pytest tests/{component}/ -v

# Step 5: Check coverage
uv run pytest tests/{component}/ --cov=src/{component} --cov-report=term

# Step 6: Run quality gates
uvx ruff check src/{component}/
uvx pyright src/{component}/
```
**Validation Criteria:**
- [ ] Regression test passes
- [ ] All existing tests pass
- [ ] Coverage maintained or improved
- [ ] Linting clean
- [ ] Type checking clean

---

### Step 5: Verify No Regressions

**Goal:** Ensure fix doesn't break other functionality

**Actions:**
1. Run full test suite
2. Run integration tests
3. Test related functionality
4. Check for side effects

**Commands:**
```bash
# Run all unit tests
uv run pytest tests/ -v

# Run integration tests
uv run pytest tests/integration/ -v -m integration

# Run E2E tests (if applicable)
uv run pytest tests/e2e/ -v -m e2e

# Run full workflow
python scripts/workflow/spec_to_production.py \
    --spec specs/{component}.md \
    --component {component} \
    --target staging
```
**Validation Criteria:**
- [ ] All tests pass
- [ ] No new failures introduced
- [ ] Integration tests pass
- [ ] Quality gates pass
- [ ] No performance degradation

---

### Step 6: Document the Fix

**Goal:** Document bug and fix for future reference

**Actions:**
1. Update component failures memory
2. Add code comments
3. Update AI context
4. Create/update GitHub issue

**Update Memory:**
```bash
# Document in component failures
cat >> .augment/memory/component-failures.memory.md << EOF

## Bug: {brief description}

**Date:** {date}
**Component:** {component}
**Severity:** {severity}

**Root Cause:**
{root cause description}

**Fix:**
{fix description}

**Lesson Learned:**
{what we learned}

**Prevention:**
{how to prevent similar bugs}

EOF
```
**Add Code Comments:**
```python
# Add comment explaining the fix
async def fixed_function():
    # Fix for bug #{issue_number}: {brief description}
    # Previous implementation had {problem}
    # Now correctly handles {scenario}
    if correct_condition:  # Fixed: was using wrong_condition
        return expected_result
```
**Update AI Context:**
```bash
python .augment/context/cli.py add integrated-workflow-2025-10-20 \
    "Fixed bug in {component}: {brief description}. Root cause: {root_cause}. Added regression test." \
    --importance 0.9
```
**GitHub Issue:**
```markdown
## Bug Fix: {brief description}

**Component:** {component}
**Severity:** {severity}
**Status:** Fixed

### Description
{detailed description}

### Root Cause
{root cause}

### Fix
{fix description}

### Testing
- [x] Regression test added
- [x] All tests pass
- [x] Integration tests pass
- [x] Quality gates pass

### Files Changed
- src/{component}/{file}.py
- tests/test_{component}.py

Closes #{issue_number}
```
---

## Validation Criteria

### Overall Success Criteria
- [ ] Bug reproduces reliably
- [ ] Root cause identified
- [ ] Fix implemented with regression test
- [ ] All tests pass
- [ ] No regressions introduced
- [ ] Quality gates pass
- [ ] Bug documented
- [ ] AI context updated

### Failure Criteria (Need More Work)
- Cannot reproduce bug
- Root cause unclear
- Fix introduces regressions
- Tests fail
- Quality gates fail

---

## Output/Deliverables

### 1. Bug Fix Report
```json
{
  "bug": {
    "description": "{description}",
    "component": "{component}",
    "severity": "{severity}",
    "reported_date": "{date}"
  },
  "investigation": {
    "root_cause": "{root_cause}",
    "affected_code": ["{file1}", "{file2}"]
  },
  "fix": {
    "description": "{fix_description}",
    "files_changed": ["{file1}", "{file2}"],
    "regression_test": "tests/test_{component}.py::test_bug_fix"
  },
  "validation": {
    "all_tests_pass": true,
    "coverage": "{coverage}%",
    "quality_gates": "passed"
  }
}
```
### 2. Regression Test
- New test that catches the bug
- Prevents future regressions
- Documents expected behavior

### 3. Updated Documentation
- Component failures memory updated
- Code comments added
- AI context updated

### 4. GitHub Issue
- Bug documented
- Fix documented
- Issue closed

---

## Integration with Primitives

### AI Context Management
```python
# Track bug investigation
context_manager.add_message(
    session_id="integrated-workflow-2025-10-20",
    role="user",
    content=f"Investigating bug in {component}: {description}",
    importance=0.9
)

# Track root cause discovery
context_manager.add_message(
    session_id="integrated-workflow-2025-10-20",
    role="assistant",
    content=f"Root cause identified: {root_cause}",
    importance=0.9
)

# Track fix implementation
context_manager.add_message(
    session_id="integrated-workflow-2025-10-20",
    role="assistant",
    content=f"Bug fixed with regression test. All tests pass.",
    importance=0.9
)
```
### Error Recovery
```python
# Use error recovery for flaky tests
@with_retry(RetryConfig(max_retries=3, base_delay=1.0))
async def run_regression_test():
    # Test with automatic retry for transient failures
    pass
```
### Development Observability
```python
# Track bug fix metrics
@track_execution("bug_fix")
async def fix_bug(component: str, bug_id: str):
    # Bug fix tracked automatically
    pass

# Metrics tracked:
# - Time to reproduce
# - Time to fix
# - Number of files changed
# - Test coverage impact
```
---

## Common Bug Patterns

### 1. Async/Await Issues
```python
# Bug: Missing await
async def get_data():
    result = fetch_data()  # ❌ Missing await
    return result

# Fix:
async def get_data():
    result = await fetch_data()  # ✅ Added await
    return result
```
### 2. Database Connection Leaks
```python
# Bug: Connection not closed
async def get_session(session_id):
    redis = await create_redis_connection()
    data = await redis.get(f"session:{session_id}")
    return data  # ❌ Connection not closed

# Fix:
async def get_session(session_id):
    redis = await create_redis_connection()
    try:
        data = await redis.get(f"session:{session_id}")
        return data
    finally:
        await redis.close()  # ✅ Connection closed
```
### 3. Missing Error Handling
```python
# Bug: No error handling
async def get_ai_response(prompt):
    response = await ai_provider.generate(prompt)  # ❌ No error handling
    return response

# Fix:
async def get_ai_response(prompt):
    try:
        response = await ai_provider.generate(prompt)
        return response
    except RateLimitError:  # ✅ Handle rate limits
        logger.warning("Rate limit hit, using fallback")
        return await fallback_provider.generate(prompt)
    except AIProviderError as e:  # ✅ Handle other errors
        logger.error(f"AI provider error: {e}")
        raise
```

---

## Resources

### TTA Documentation
- Debugging Context: `.augment/context/debugging.context.md`
- Component Failures: `.augment/memory/component-failures.memory.md`
- Testing Patterns: `.augment/memory/testing-patterns.memory.md`

### Tools
- pytest: `uv run pytest`
- Debugger: `pdb`, `ipdb`
- Linting: `uvx ruff check`
- Type checking: `uvx pyright`

---

**Note:** Always write a regression test before fixing the bug. This ensures the bug is caught if it reappears.
./complete-keploy-workflow.sh

# Interactive testing menu
./master-tta-testing.sh
```

### Current Coverage

| Test Suite | Tests | Pass Rate |
|------------|-------|-----------|
| Health & Status | 2 | 100% ✅ |
| Session Management | 5 | 80% ✅ |
| Error Handling | 2 | 100% ✅ |
| **Total** | **9** | **88.9%** |

[Learn more about Keploy Automated Testing →](keploy-automated-testing.md)

## 🎭 Test Categories

### Standard Tests
Core functionality validation with expected inputs and outputs.

**Location**: `tests/unit/`, `tests/integration/`

### Adversarial Tests
Edge cases, error conditions, and boundary testing.

**Location**: `tests/comprehensive_battery/adversarial/`

**Focus**:
- Invalid input handling
- Rate limiting
- Resource exhaustion
- Concurrent access

### Load & Stress Tests
Performance validation under high load.

**Location**: `tests/comprehensive_battery/load_stress/`

**Metrics**:
- Response time under load
- Throughput degradation
- Circuit breaker activation
- Graceful degradation

### Data Pipeline Tests
Data integrity and consistency validation.

**Location**: `tests/comprehensive_battery/data_pipeline/`

**Coverage**:
- Redis message coordination
- Neo4j graph operations
- State management
- Cache consistency

## 🔄 CI/CD Integration

### GitHub Actions
Every push triggers:

1. ✅ **Keploy API tests** - Instant regression detection
2. ✅ **Unit test suite** - Component validation
3. ✅ **Coverage reports** - Quality metrics
4. ✅ **PR comments** - Automated feedback

**Configuration**: `.github/workflows/keploy-tests.yml`

### Nightly Builds
Complete test suite runs at 2 AM UTC:

- ✅ Full unit test suite
- ✅ Integration tests
- ✅ E2E tests
- ✅ Performance benchmarks
- ✅ Coverage reports to Codecov

### Pre-Commit Hooks
**Never commit broken code!**

Install the pre-commit hook:

```bash
./master-tta-testing.sh
# Select option 8: Setup Pre-Commit Hook
```

Every commit automatically:
1. Checks code formatting (Ruff)
2. Runs Keploy API tests
3. Validates all tests pass
4. Blocks commit if tests fail

## 📈 Quality Gates

### Component Maturity Levels

| Level | Coverage | Mutation Score | File Size |
|-------|----------|----------------|-----------|
| **Development** | ≥70% | ≥75% | ≤1,000 lines |
| **Staging** | ≥80% | ≥80% | ≤800 lines |
| **Production** | ≥85% | ≥85% | ≤600 lines |

### Required Checks

Before merging to `main`:
- ✅ All tests passing
- ✅ Coverage thresholds met
- ✅ No critical security issues
- ✅ Code formatted (Ruff)
- ✅ Type checks pass (Pyright)

## 🛠️ Testing Tools

### Core Framework
- **pytest** - Test framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting
- **pytest-xdist** - Parallel execution

### Mocking & Fixtures
- **unittest.mock** - Python mocking
- **pytest-mock** - Pytest integration
- **factory_boy** - Test data generation

### API Testing
- **Keploy** - Automated API test generation
- **httpx** - HTTP client for testing
- **FastAPI TestClient** - API testing utilities

### Database Testing
- **pytest-redis** - Redis test fixtures
- **pytest-neo4j** - Neo4j test fixtures
- **fakeredis** - In-memory Redis mock
- **neograph** - In-memory graph mock

### UI Testing
- **Playwright** - Browser automation
- **pytest-playwright** - Pytest integration

## 📝 Writing Tests

### AAA Pattern
All tests follow **Arrange-Act-Assert**:

```python
import pytest

def test_session_creation():
    # Arrange - Setup test data
    session_data = {"type": "adventure", "title": "Test Quest"}

    # Act - Execute the operation
    session = create_session(session_data)

    # Assert - Verify the result
    assert session.type == "adventure"
    assert session.title == "Test Quest"
```

### Async Testing
Use `@pytest.mark.asyncio` for async code:

```python
@pytest.mark.asyncio
async def test_async_operation():
    # Arrange
    coordinator = RedisMessageCoordinator()

    # Act
    result = await coordinator.send_message("test_queue", {"data": "test"})

    # Assert
    assert result.success is True
```

### Fixtures
Reuse common setup:

```python
@pytest.fixture
def mock_redis():
    """Provide a mock Redis client for testing."""
    return FakeRedis()

def test_with_redis(mock_redis):
    # Test uses the fixture
    mock_redis.set("key", "value")
    assert mock_redis.get("key") == "value"
```

## 🎮 Running Tests

### All Tests
```bash
uv run pytest
```

### Specific Category
```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests
uv run pytest tests/integration/

# With markers
uv run pytest -m "redis or neo4j"
```

### Coverage Report
```bash
uv run pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Fast Feedback
```bash
# Failed tests only
uv run pytest --lf

# Parallel execution
uv run pytest -n auto
```

### Interactive Menu
```bash
./master-tta-testing.sh
```

## 🔍 Test Organization

```
tests/
├── unit/                          # Unit tests (70%)
│   ├── agent_orchestration/       # Agent coordination
│   ├── model_management/          # AI model services
│   └── observability_integration/ # Monitoring primitives
├── integration/                   # Integration tests (20%)
│   ├── database/                  # Redis + Neo4j
│   └── api/                       # API integration
├── e2e/                           # E2E tests (10%)
│   └── playwright/                # Browser tests
├── comprehensive_battery/         # Advanced testing
│   ├── standard/                  # Standard test cases
│   ├── adversarial/               # Edge cases
│   ├── load_stress/               # Performance
│   └── data_pipeline/             # Data integrity
└── conftest.py                    # Shared fixtures
```

## 📚 Best Practices

### ✅ Do

- Write tests alongside code (not after)
- Use descriptive test names
- Follow AAA pattern consistently
- Mock external dependencies
- Test error paths, not just happy paths
- Use Keploy for API testing (zero manual effort!)

### ❌ Don't

- Write brittle tests dependent on execution order
- Test implementation details (test behavior)
- Ignore failing tests
- Commit code without tests
- Skip edge case testing
- Write manual API tests (use Keploy!)

## 🚨 Troubleshooting

### Tests Failing Locally?

```bash
# Check service availability
docker compose ps

# Restart services
docker compose down
docker compose up -d

# Clear cache
rm -rf .pytest_cache
uv run pytest --cache-clear
```

### Coverage Not Meeting Threshold?

```bash
# Generate detailed report
uv run pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html
```

### Keploy Tests Failing?

```bash
# Re-record tests
./record-real-api-tests.sh

# Verify API is running
curl http://localhost:8000/health
```

## 📖 Further Reading

- [Keploy Automated Testing Guide](keploy-automated-testing.md) - Complete automation setup
- [Component Maturity Workflow](component-maturity.md) - Quality gates
- [Contributing Guide](contributing.md) - How to contribute tests
- [CI/CD Documentation](cicd.md) - Automation pipelines

---

**Remember**: With Keploy automated testing, you'll never have testing lag behind development again! 🚀
