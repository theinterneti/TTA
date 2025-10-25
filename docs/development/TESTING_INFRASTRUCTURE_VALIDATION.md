# Testing Infrastructure Validation Checklist

**Comprehensive validation procedures for TTA's testing infrastructure.**

---

## Overview

This checklist provides a repeatable process for validating the entire testing infrastructure after changes. Use this checklist:

- After modifying pytest configuration
- After updating VS Code settings
- After changing CI/CD workflows
- After updating pre-commit hooks
- Before promoting testing infrastructure changes to production

**Expected Time:** 30-45 minutes for complete validation

---

## Master Checklist

- [ ] Coverage Configuration Validation
- [ ] VS Code Integration Validation
- [ ] CI/CD Workflow Validation
- [ ] Git Hooks Validation
- [ ] Documentation Validation

---

## 1. Coverage Configuration Validation

### 1.1 Run Tests with Coverage

```bash
# Run all tests with coverage
uv run pytest

# Expected output:
# - Tests run successfully
# - Coverage report displayed in terminal
# - Coverage percentage shown
# - htmlcov/ directory created
# - coverage.xml created
```

**Checklist:**
- [ ] Tests execute successfully
- [ ] Terminal shows coverage report
- [ ] Coverage percentage ≥ 70%
- [ ] `htmlcov/` directory created
- [ ] `coverage.xml` file created

### 1.2 Verify HTML Coverage Report

```bash
# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Checklist:**
- [ ] HTML report opens in browser
- [ ] Shows overall coverage percentage
- [ ] Lists all source files
- [ ] Can drill down into individual files
- [ ] Shows covered/uncovered lines

### 1.3 Verify Coverage Threshold Enforcement

```bash
# Test threshold enforcement
# 1. Edit pyproject.toml: set fail_under = 100.0
# 2. Run: uv run pytest
# 3. Verify tests FAIL with coverage error
# 4. Restore fail_under = 70.0
# 5. Run: uv run pytest
# 6. Verify tests PASS
```

**Checklist:**
- [ ] Tests fail when coverage < threshold
- [ ] Error message clearly indicates coverage failure
- [ ] Tests pass when coverage ≥ threshold

### 1.4 Troubleshooting

**Coverage shows 0%:**
- ✅ Using `uv run pytest` (not `uvx pytest`)
- ✅ Virtual environment activated
- ✅ Dependencies installed: `uv sync --all-extras`

**HTML report not generated:**
- ✅ Check `pyproject.toml` has `--cov-report=html`
- ✅ Check write permissions on `htmlcov/` directory

---

## 2. VS Code Integration Validation

### 2.1 Test Discovery

**Steps:**
1. Open VS Code
2. Open Testing panel (beaker icon in sidebar)
3. Wait for test discovery to complete

**Checklist:**
- [ ] Testing panel shows all tests
- [ ] Tests organized by file/class/function
- [ ] No discovery errors in Output panel
- [ ] Can expand/collapse test tree

### 2.2 Test Execution

**Steps:**
1. Click run button on single test
2. Click run button on test file
3. Click run button on root (all tests)

**Checklist:**
- [ ] Single test runs successfully
- [ ] All tests in file run successfully
- [ ] All tests run successfully
- [ ] Results display correctly (✓/✗)
- [ ] Failed tests show error messages

### 2.3 Test Debugging

**Steps:**
1. Open test file
2. Set breakpoint in test function
3. Right-click test in Testing panel → Debug Test
4. Step through code (F10, F11)

**Checklist:**
- [ ] Debugger stops at breakpoint
- [ ] Can step through code
- [ ] Variables panel shows values
- [ ] Can inspect variables
- [ ] Can continue/stop debugging

### 2.4 Coverage Visualization

**Steps:**
1. Run: `uv run pytest` in terminal
2. Open source file in editor
3. Check for coverage indicators in gutter

**Checklist:**
- [ ] Green indicators for covered lines
- [ ] Red indicators for uncovered lines
- [ ] Coverage Gutters extension active
- [ ] Can toggle coverage display

### 2.5 Tasks

**Steps:**
1. Open Command Palette (Ctrl+Shift+P)
2. Run "Tasks: Run Task"
3. Test each task:
   - Run All Tests
   - Run All Tests with Coverage
   - Run Unit Tests
   - Run Integration Tests
   - Run Current File Tests
   - Run Failed Tests

**Checklist:**
- [ ] All tasks execute successfully
- [ ] Output displayed in terminal
- [ ] Can cancel running tasks
- [ ] Tasks use correct commands

### 2.6 Troubleshooting

**Tests not discovered:**
- ✅ Check `.vscode/settings.json` has correct `python.testing.pytestPath`
- ✅ Verify virtual environment selected: Ctrl+Shift+P → "Python: Select Interpreter"
- ✅ Reload window: Ctrl+Shift+P → "Developer: Reload Window"

**Coverage indicators not showing:**
- ✅ Coverage Gutters extension installed
- ✅ Coverage report generated: `uv run pytest`
- ✅ Click "Watch" in Coverage Gutters status bar

---

## 3. CI/CD Workflow Validation

### 3.1 Check Recent Workflow Runs

**Steps:**
1. Go to GitHub repository
2. Click "Actions" tab
3. Review recent workflow runs

**Checklist:**
- [ ] `tests.yml` passing on main branch
- [ ] `code-quality.yml` passing on main branch
- [ ] `comprehensive-test-battery.yml` passing (if scheduled)
- [ ] `monorepo-ci.yml` passing (if applicable)

### 3.2 Verify Test Commands

**Steps:**
1. Click into a workflow run
2. Expand job logs
3. Search for pytest commands

**Checklist:**
- [ ] All workflows use `uv run pytest`
- [ ] No workflows use `uvx pytest`
- [ ] Coverage flags present (`--cov=src`)

### 3.3 Verify Coverage Artifacts

**Steps:**
1. Click into a workflow run
2. Scroll to "Artifacts" section
3. Download coverage artifacts

**Checklist:**
- [ ] Coverage artifacts uploaded
- [ ] Artifacts contain `coverage.xml`
- [ ] Artifacts contain `htmlcov/` directory
- [ ] Can open HTML report from artifact

### 3.4 Troubleshooting

**Workflows failing:**
- ✅ Check workflow logs for errors
- ✅ Verify services running (Redis, Neo4j)
- ✅ Check environment variables set
- ✅ Verify dependencies installed

---

## 4. Git Hooks Validation

### 4.1 Test Normal Commit

**Steps:**
```bash
# Create test file
echo '# test' >> test_file.py

# Stage file
git add test_file.py

# Commit
git commit -m "test: verify pre-commit hooks"

# Clean up
git reset HEAD test_file.py
rm test_file.py
```

**Checklist:**
- [ ] All hooks run
- [ ] Hooks pass for valid changes
- [ ] Commit succeeds

### 4.2 Test Hook Failure

**Steps:**
```bash
# Create file with linting error
echo 'import unused_module' >> test_file.py

# Stage file
git add test_file.py

# Commit (should fail)
git commit -m "test: verify hook failure"

# Clean up
rm test_file.py
```

**Checklist:**
- [ ] Ruff hook fails
- [ ] Error message displayed
- [ ] Commit blocked

### 4.3 Test Skipping Hooks

**Steps:**
```bash
# Create test file
echo '# test' >> test_file.py

# Stage file
git add test_file.py

# Skip specific hook
SKIP=run-tests-on-changed-files git commit -m "test: skip test hook"

# Clean up
git reset HEAD test_file.py
rm test_file.py
```

**Checklist:**
- [ ] Test hook skipped
- [ ] Other hooks still run
- [ ] Commit succeeds

### 4.4 Troubleshooting

**Hooks not running:**
- ✅ Pre-commit installed: `pre-commit --version`
- ✅ Hooks installed: `pre-commit install`
- ✅ Config valid: `pre-commit validate-config`

---

## 5. Documentation Validation

### 5.1 Verify Links

**Steps:**
1. Open `docs/development/TESTING_INFRASTRUCTURE.md`
2. Click all internal links
3. Verify they navigate correctly

**Checklist:**
- [ ] All links work
- [ ] Links point to correct sections
- [ ] No broken links

### 5.2 Verify Commands

**Steps:**
1. Copy commands from documentation
2. Run commands in terminal
3. Verify they work as documented

**Checklist:**
- [ ] All commands execute successfully
- [ ] Output matches documentation
- [ ] No errors or warnings

### 5.3 Troubleshooting

**Links broken:**
- ✅ Check file paths are correct
- ✅ Verify files exist
- ✅ Update links if files moved

---

## Validation Complete

✅ **All validation steps passed!**

Your testing infrastructure is fully validated and ready for use.

**Next Steps:**
- Document any issues found
- Update configuration if needed
- Share validation results with team
- Schedule next validation (quarterly recommended)

---

## Quick Reference

**Run all tests:**
```bash
uv run pytest
```

**Run with coverage:**
```bash
uv run pytest  # Coverage runs by default
```

**Open coverage report:**
```bash
open htmlcov/index.html
```

**Run pre-commit hooks:**
```bash
pre-commit run --all-files
```

**Skip test hook:**
```bash
SKIP=run-tests-on-changed-files git commit -m "message"
```

---

**Last Updated:** 2025-10-23
**Validation Frequency:** Quarterly or after major changes
