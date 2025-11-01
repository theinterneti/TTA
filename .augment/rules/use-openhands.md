---
type: "agent_requested"
description: "Use OpenHands for automated test generation and development tasks"
---

# Use OpenHands for Automated Test Generation

## Rule Priority
**HIGH** - Apply when generating tests, improving test coverage, or automating development tasks

## When to Use OpenHands Integration

Use OpenHands integration for automated test generation and development tasks:

### 1. Unit Test Generation
- **Use**: `UnitTestGenerationService.generate_tests()` or `generate_tests_for_file()`
- **When**: Generating unit tests for existing code with insufficient coverage
- **Example**: Component has <70% coverage and needs tests for staging promotion

### 2. Package Test Generation
- **Use**: `generate_tests_for_package()`
- **When**: Generating tests for entire packages or modules
- **Example**: New package needs comprehensive test suite

### 3. Test Coverage Improvement
- **Use**: `UnitTestGenerationService` with iterative feedback
- **When**: Existing tests don't meet coverage thresholds (≥70% for staging, ≥80% for production)
- **Example**: Component maturity assessment shows coverage gaps

### 4. Test Scaffolding
- **Use**: `generate_tests_for_file()` with low coverage threshold
- **When**: Creating initial test structure for new components
- **Example**: New feature needs test framework setup

## When NOT to Use OpenHands Integration

**Do NOT use OpenHands integration for:**

1. **Simple Test Fixes** - Use direct editing instead
   - Fixing single test failures
   - Updating test assertions
   - Modifying test data

2. **Test Debugging** - Use diagnostics and manual debugging
   - Investigating test failures
   - Debugging flaky tests
   - Analyzing test output

3. **Non-Python Tests** - OpenHands optimized for Python/pytest
   - JavaScript/TypeScript tests
   - Integration tests requiring specific infrastructure
   - Performance/load tests

4. **E2E Testing** - Use Playwright integration instead
   - Browser automation tests
   - UI interaction tests
   - Visual regression tests

5. **Quick Queries** - Don't use for simple questions
   - "What does this function do?"
   - "How do I run tests?"
   - "What's the test coverage?"

**Rationale:** OpenHands is specialized for unit/integration test generation. Other tools are better suited for other testing needs.

## Quick Commands

### Python API (Recommended)

```python
from src.agent_orchestration.openhands_integration import (
    generate_tests_for_file,
    generate_tests_for_package,
    validate_test_result,
)

# Generate tests for single file
result = await generate_tests_for_file(
    "src/agent_orchestration/tools/callable_registry.py",
    coverage_threshold=70.0,
)

# Generate tests for package
results = await generate_tests_for_package(
    "src/agent_orchestration/tools/",
    coverage_threshold=75.0,
)

# Validate result
success, issues = validate_test_result(result, coverage_threshold=70.0)
if success:
    print(f"✓ Tests generated successfully (coverage: {result.coverage_percentage}%)")
else:
    print(f"✗ Issues: {issues}")
```

### Advanced API (Full Control)

```python
from pathlib import Path
from src.agent_orchestration.openhands_integration import (
    OpenHandsIntegrationConfig,
    UnitTestGenerationService,
    TestTaskSpecification,
)

# Load config from environment
config = OpenHandsIntegrationConfig.from_env()

# Create service
service = UnitTestGenerationService(config.to_client_config())

# Generate tests with custom specification
spec = TestTaskSpecification(
    target_file=Path("src/module/file.py"),
    coverage_threshold=80.0,
    test_framework="pytest",
    timeout_seconds=600.0,
)
result = await service.generate_tests(spec, max_iterations=5)
```

## Best Practices

### 1. Start with Low Coverage Threshold
- Begin with 70% coverage threshold
- Iterate to improve coverage
- Avoid over-testing (diminishing returns above 90%)

### 2. Review Generated Tests
- **Always review** generated tests before committing
- Verify test logic is correct
- Check for edge cases and error handling
- Ensure tests follow TTA conventions

### 3. Use Iterative Feedback
- Set `max_iterations=5` for quality improvement
- OpenHands will retry with feedback if validation fails
- Each iteration improves test quality

### 4. Provide Context Files
- For complex dependencies, provide context files
- Helps OpenHands understand imports and usage
- Improves test accuracy

### 5. Validate Tests Execute Successfully
- Run generated tests: `uv run pytest <test_file> -v`
- Check coverage: `uv run pytest <test_file> --cov=<module> --cov-report=term`
- Fix any failures before relying on tests

### 6. Track Test Generation Sessions
- Test generation automatically creates AI context sessions
- Session ID format: `openhands-test-gen-{file}-{timestamp}`
- Review sessions for multi-day development

## Integration with Other Rules

### Testing Command Standard
**Always use `uv run pytest` (NOT `uvx pytest`)**
- Reference: `prefer-uvx-for-tools.md`
- Rationale: `uvx pytest` causes false 0% coverage readings

### File Size Limits
**Generated test files should follow `avoid-long-files.md`**
- Soft limit: 300-400 lines (consider splitting)
- Hard limit: 1,000 lines (MUST split - blocks staging promotion)
- If tests exceed limits, split into multiple test files

### Component Maturity
**Use OpenHands to meet staging promotion criteria**
- Reference: `integrated-workflow.md`
- Dev → Staging: ≥70% test coverage
- Staging → Production: ≥80% integration test coverage

### Workflow Integration
**OpenHands integrates with TTA agentic workflow primitives**
- AI Context Management: Automatic session tracking
- Error Recovery: Retry with exponential backoff, circuit breaker
- Development Observability: Metrics tracking, dashboard integration

## Troubleshooting

### API Key Not Set

**Symptom:** `ValueError: OPENROUTER_API_KEY environment variable is required`

**Solutions:**
1. Set environment variable: `export OPENROUTER_API_KEY=your-key`
2. Get API key from https://openrouter.ai/keys (free tier available)
3. Add to `.env` file: `OPENROUTER_API_KEY=your-key`
4. Verify: `echo $OPENROUTER_API_KEY`

### Test Generation Fails

**Symptom:** `result.success == False`

**Solutions:**
1. Check error message: `print(result.error)`
2. Review validation issues: `print(result.issues)`
3. Increase timeout: `timeout_seconds=900.0`
4. Reduce coverage threshold: `coverage_threshold=60.0`
5. Provide context files for complex dependencies

### Generated Tests Don't Pass

**Symptom:** `result.tests_pass == False`

**Solutions:**
1. Review validation issues: `print(result.issues)`
2. Check coverage: `print(result.coverage_percentage)`
3. Manually review generated tests
4. Fix import errors or missing dependencies
5. Retry with feedback: `max_iterations > 1`

### Timeout Errors

**Symptom:** `OpenHandsErrorType.TIMEOUT_ERROR`

**Solutions:**
1. Increase timeout: `timeout_seconds=900.0` (15 minutes)
2. Simplify target file (split large files first)
3. Check OpenRouter API status
4. Retry with exponential backoff (automatic)

### Low Coverage Results

**Symptom:** `result.coverage_percentage < threshold`

**Solutions:**
1. Review generated tests for completeness
2. Manually add tests for uncovered code paths
3. Retry with higher `max_iterations`
4. Provide additional context about edge cases

### Circuit Breaker Open

**Symptom:** `CircuitBreakerOpenError`

**Solutions:**
1. Wait for recovery timeout (60 seconds)
2. Check OpenRouter API status
3. Verify API key is valid
4. Manually reset circuit breaker if needed

## Examples

### Example 1: Generate Tests for Single File

```python
import asyncio
from src.agent_orchestration.openhands_integration import generate_tests_for_file

async def main():
    result = await generate_tests_for_file(
        "src/agent_orchestration/tools/callable_registry.py",
        coverage_threshold=70.0,
        max_iterations=5,
    )

    if result.syntax_valid and result.tests_pass:
        print(f"✓ Tests generated successfully")
        print(f"  Coverage: {result.coverage_percentage}%")
        print(f"  Test file: {result.test_file_path}")
    else:
        print(f"✗ Test generation failed")
        print(f"  Issues: {result.issues}")

asyncio.run(main())
```

### Example 2: Generate Tests for Package

```python
import asyncio
from src.agent_orchestration.openhands_integration import generate_tests_for_package

async def main():
    results = await generate_tests_for_package(
        "src/agent_orchestration/tools/",
        coverage_threshold=75.0,
    )

    for file_path, result in results.items():
        if result.syntax_valid and result.tests_pass:
            print(f"✓ {file_path}: {result.coverage_percentage}%")
        else:
            print(f"✗ {file_path}: {result.issues}")

asyncio.run(main())
```

### Example 3: Validate Test Result

```python
from src.agent_orchestration.openhands_integration import (
    generate_tests_for_file,
    validate_test_result,
)

async def main():
    result = await generate_tests_for_file("src/module/file.py")

    success, issues = validate_test_result(result, coverage_threshold=70.0)

    if success:
        print("✓ All validation checks passed")
    else:
        print(f"✗ Validation failed:")
        for issue in issues:
            print(f"  - {issue}")

asyncio.run(main())
```

---

**Status:** Active (Production Ready)
**Last Updated:** 2025-10-24
**Related Rules:** `prefer-uvx-for-tools.md`, `avoid-long-files.md`, `integrated-workflow.md`, `ai-context-management.md`
