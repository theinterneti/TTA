# VS Code Pytest Integration Fix

## Problem

VS Code's testing integration not working properly after updating the Python interpreter. Tests don't appear in the Testing panel even though pytest discovery works from the command line.

## Root Cause

VS Code Python extension caches interpreter and test discovery information. After changing interpreters or updating configuration, the cache becomes stale and prevents proper test discovery.

**Common Symptoms:**
- Testing panel shows "No tests discovered"
- Tests work fine from command line (`pytest tests`)
- Interpreter was recently changed or updated
- VS Code logs show test discovery errors

---

## Solution

### Quick Fix (Automated)

```bash
./fix-vscode-pytest-integration.sh
```

Then **restart VS Code** (see steps below).

### Manual Fix

If the automated script doesn't work, follow these steps:

#### 1. Verify Pytest Works from Command Line

```bash
.venv/bin/python -m pytest --collect-only tests
```

**Expected:** Should list all 952 tests

**If this fails:** Pytest configuration issue (not VS Code issue)

#### 2. Clear Python Extension Cache

```bash
# Clear workspace storage
find ~/.vscode-server/data/User/workspaceStorage -type d -name "ms-python.python" -exec rm -rf {} + 2>/dev/null

# Clear pytest cache
rm -rf .pytest_cache
```

#### 3. Verify VS Code Settings

Check `.vscode/settings.json` has:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.nosetestsEnabled": false,

  "python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest",

  "python.testing.pytestArgs": [
    "${workspaceFolder}/tests",
    "-v",
    "--rootdir=${workspaceFolder}"
  ],

  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",

  "python.testing.autoTestDiscoverOnSaveEnabled": true,
  "python.testing.promptToConfigure": false
}
```

#### 4. Restart VS Code

**CRITICAL:** Cache clearing only takes effect after restart.

```bash
# Close all terminals in VS Code
# Then close VS Code completely
pkill -f 'vscode-server'

# Wait 5 seconds
sleep 5

# Reopen
code /home/thein/recovered-tta-storytelling
```

#### 5. Select Interpreter

After reopening VS Code:

1. Press `Ctrl+Shift+P`
2. Type: `Python: Select Interpreter`
3. Choose: `.venv/bin/python` (Python 3.12.3)

#### 6. Configure Tests (if prompted)

If VS Code prompts to configure tests:

1. Press `Ctrl+Shift+P`
2. Type: `Python: Configure Tests`
3. Select: `pytest`
4. Select: `tests` (directory)

#### 7. Refresh Tests

1. Open Testing panel (flask icon in sidebar)
2. Click "Refresh Tests" button (circular arrow icon)

**Expected:** All 952 tests should appear in the tree view

---

## Configuration Details

### VS Code Settings Explained

```json
// Explicitly use .venv pytest (prevents using system pytest)
"python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest"
```

**Why:** Ensures VS Code uses the correct pytest with all project dependencies.

```json
// Use absolute paths for reliable discovery
"python.testing.pytestArgs": [
  "${workspaceFolder}/tests",
  "-v",
  "--rootdir=${workspaceFolder}"
]
```

**Why:**
- Absolute paths prevent path resolution issues
- `--rootdir` ensures pytest uses correct project root
- `-v` provides verbose output for debugging

```json
// Disable conflicting test frameworks
"python.testing.unittestEnabled": false,
"python.testing.nosetestsEnabled": false
```

**Why:** Multiple test frameworks can interfere with discovery.

```json
// Auto-discover tests on save
"python.testing.autoTestDiscoverOnSaveEnabled": true
```

**Why:** Automatically updates test list when files change.

### pytest.ini Configuration

```ini
[pytest]
testpaths = tests
addopts = -q
```

**Why:**
- `testpaths` restricts discovery to `tests/` directory
- `addopts` sets default options for all pytest runs

---

## Verification

### Quick Verification

```bash
# Run the verification script
./.vscode/pytest-discovery-test.sh
```

**Expected output:**
```
Testing pytest discovery...
tests/agent_orchestration/test_agent_orchestration_service.py::test_service_initialization_success
tests/agent_orchestration/test_agent_orchestration_service.py::test_service_initialization_failure
...

Test count:
952
```

### Manual Verification

```bash
# 1. Pytest works from command line
.venv/bin/python -m pytest --collect-only tests | grep -c "::test_"
# Should show: 952

# 2. Pytest path is correct
which pytest
# Should show: /home/thein/recovered-tta-storytelling/.venv/bin/pytest

# 3. Python interpreter is correct
which python
# Should show: /home/thein/recovered-tta-storytelling/.venv/bin/python
```

### VS Code Verification

1. **Testing Panel:**
   - Open Testing panel (flask icon)
   - Should show test tree with 952 tests

2. **Python Test Log:**
   - Open Output panel (`Ctrl+Shift+U`)
   - Select "Python Test Log" from dropdown
   - Should show successful test discovery

3. **Run a Test:**
   - Click any test in Testing panel
   - Click "Run Test" button
   - Should execute successfully

---

## Troubleshooting

### Issue: Tests Still Don't Appear

**Check Python Test Log:**

1. Open Output panel (`Ctrl+Shift+U`)
2. Select "Python Test Log" from dropdown
3. Look for error messages

**Common errors:**

#### Error: "No module named pytest"

**Solution:**
```bash
uv sync --all-extras
```

#### Error: "pytest: command not found"

**Solution:**
```bash
# Verify pytest is in .venv
ls -la .venv/bin/pytest

# If missing, reinstall
uv sync --all-extras
```

#### Error: "No tests discovered"

**Solution:**
```bash
# Verify tests directory exists
ls -la tests/

# Verify pytest.ini is correct
cat pytest.ini

# Test discovery manually
.venv/bin/python -m pytest --collect-only tests
```

### Issue: Wrong Interpreter Selected

**Symptoms:**
- Tests use system Python instead of .venv
- Import errors for project dependencies

**Solution:**
```bash
# 1. Clear interpreter cache
rm -rf ~/.vscode-server/data/User/workspaceStorage/*/ms-python.python/

# 2. Restart VS Code
pkill -f 'vscode-server'

# 3. Manually select interpreter
# Ctrl+Shift+P → "Python: Select Interpreter" → .venv/bin/python
```

### Issue: Slow Test Discovery

**Symptoms:**
- Test discovery takes > 30 seconds
- VS Code becomes unresponsive during discovery

**Solution:**
```bash
# 1. Reduce test collection scope in pytest.ini
[pytest]
testpaths = tests
addopts = -q --ignore=tests/slow_tests

# 2. Disable auto-discovery on save
# In .vscode/settings.json:
"python.testing.autoTestDiscoverOnSaveEnabled": false
```

### Issue: Tests Discovered But Won't Run

**Symptoms:**
- Tests appear in Testing panel
- Clicking "Run Test" does nothing or shows error

**Solution:**
```bash
# 1. Check pytest can run tests
.venv/bin/python -m pytest tests/agent_orchestration/test_agent_orchestration_service.py::test_service_initialization_success -v

# 2. Check for import errors
.venv/bin/python -c "import sys; sys.path.insert(0, '.'); import tests.agent_orchestration.test_agent_orchestration_service"

# 3. Verify PYTHONPATH
echo $PYTHONPATH
# Should include project root
```

---

## Best Practices

### 1. Always Use Virtual Environment

```bash
# Never use system Python for testing
# Always activate .venv or use uv run
```

### 2. Keep Configuration in Sync

Ensure these files are consistent:
- `.vscode/settings.json` - VS Code configuration
- `pytest.ini` - Pytest configuration
- `pyproject.toml` - Project metadata

### 3. Restart VS Code After Configuration Changes

```bash
# After changing:
# - .vscode/settings.json
# - pytest.ini
# - Python interpreter
# - Installing/updating pytest

pkill -f 'vscode-server'
code /path/to/workspace
```

### 4. Use Absolute Paths

```json
// Good
"python.testing.pytestArgs": ["${workspaceFolder}/tests"]

// Bad (can cause path resolution issues)
"python.testing.pytestArgs": ["tests"]
```

### 5. Monitor Python Test Log

Keep Output panel open to "Python Test Log" during development to catch issues early.

---

## Additional Resources

### VS Code Python Testing Documentation

- **Official Docs:** https://code.visualstudio.com/docs/python/testing
- **Pytest Integration:** https://code.visualstudio.com/docs/python/testing#_pytest

### Common VS Code Commands

```
Ctrl+Shift+P → "Python: Select Interpreter"
Ctrl+Shift+P → "Python: Configure Tests"
Ctrl+Shift+P → "Python: Clear Cache and Reload Window"
Ctrl+Shift+P → "Terminal: Kill All Terminals"
Ctrl+Shift+U → Open Output Panel
```

### Project-Specific Files

- `fix-vscode-pytest-integration.sh` - Automated fix script
- `.vscode/pytest-discovery-test.sh` - Quick verification script
- `.vscode/settings.json` - VS Code configuration
- `pytest.ini` - Pytest configuration

---

## Summary

**Problem:** VS Code testing integration not working after interpreter update

**Root Cause:** Stale Python extension cache

**Solution:**
1. Run `./fix-vscode-pytest-integration.sh`
2. Restart VS Code
3. Select `.venv/bin/python` interpreter
4. Refresh tests in Testing panel

**Verification:** All 952 tests should appear in Testing panel

**Key Configuration:**
- `python.testing.pytestPath`: Points to `.venv/bin/pytest`
- `python.testing.pytestArgs`: Uses absolute paths
- `python.defaultInterpreterPath`: Points to `.venv/bin/python`

---

**Status:** ✅ Fixed
**Tests Discovered:** 952
**Last Updated:** 2025-10-04
