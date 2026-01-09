# VS Code Testing Integration Verification Guide

**Purpose:** Verify all VS Code testing features work correctly after testing infrastructure changes.

**When to Use:** After modifying testing configuration, VS Code settings, or pytest configuration.

**Estimated Time:** 15-20 minutes

---

## Prerequisites

1. **VS Code Extensions Installed:**
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)
   - Python Debugger (ms-python.debugpy)
   - Coverage Gutters (ryanluker.vscode-coverage-gutters)
   - Ruff (charliermarsh.ruff)

2. **Environment Setup:**
   - Virtual environment activated (`.venv`)
   - Dependencies installed (`uv sync --all-extras`)
   - VS Code opened at workspace root

3. **Verify Configuration:**
   - Check `.vscode/settings.json` exists
   - Check `.vscode/tasks.json` exists
   - Check `.vscode/launch.json` exists
   - Check `.vscode/extensions.json` exists

---

## Verification Checklist

### 1. Test Discovery

**Objective:** Verify VS Code can discover all tests automatically.

**Steps:**
1. Open VS Code
2. Click **Testing** icon in Activity Bar (left sidebar, beaker icon)
3. Wait for test discovery to complete (may take 10-30 seconds)
4. Expand test tree

**Expected Outcomes:**
- ✅ Testing panel shows test tree
- ✅ Tests organized by directory (tests/unit/, tests/integration/, etc.)
- ✅ Test count matches `uv run pytest --collect-only -q` output (~1,700+ tests)
- ✅ No "No tests discovered" message

**Troubleshooting:**
- **No tests shown:** Click refresh button (⟳) in Testing panel
- **"Python extension loading":** Wait for Python extension to finish loading
- **Import errors:** Verify virtual environment is activated (check status bar)
- **Still no tests:** Check Output panel → Python → Look for pytest discovery errors

---

### 2. Test Execution

**Objective:** Verify tests can be run from VS Code Testing panel.

**Steps:**
1. In Testing panel, find `tests/unit/tools/test_cursor.py`
2. Click **▶️ Run Test** button next to `test_cursor.py`
3. Wait for tests to complete
4. Verify results display

**Expected Outcomes:**
- ✅ Tests execute (progress indicator shows)
- ✅ Results display in Testing panel (green ✓ for pass, red ✗ for fail)
- ✅ Test output appears in Terminal panel
- ✅ Can click individual test to see details

**Additional Tests:**
- Run single test: Click ▶️ next to individual test function
- Run all tests: Click ▶️ next to root "tests" folder
- Re-run failed tests: Click "Run Failed Tests" button

**Troubleshooting:**
- **Tests don't run:** Check Python interpreter is set to `.venv/bin/python`
- **Import errors:** Verify `PYTHONPATH` includes `src/` (should be automatic)
- **Coverage 0%:** This is expected when running from Testing panel (coverage only runs from terminal or tasks)

---

### 3. Test Debugging

**Objective:** Verify debugger works with tests.

**Steps:**
1. Open `tests/unit/tools/test_cursor.py`
2. Set breakpoint (click left of line number) in `test_cursor_initialization` function
3. In Testing panel, right-click `test_cursor_initialization`
4. Select **Debug Test**
5. Wait for debugger to start
6. Verify debugger stops at breakpoint

**Expected Outcomes:**
- ✅ Debugger starts (yellow highlight on breakpoint line)
- ✅ Debug toolbar appears (Continue, Step Over, Step Into, etc.)
- ✅ Variables panel shows local variables
- ✅ Call stack panel shows execution path
- ✅ Can step through code (F10 = Step Over, F11 = Step Into)
- ✅ Can inspect variables (hover over variable names)

**Additional Tests:**
- Use debug configurations from Run & Debug panel:
  - "Debug Current Test File"
  - "Debug Current Test Function"
  - "Debug All Tests"
  - "Debug Integration Tests"

**Troubleshooting:**
- **Debugger doesn't start:** Verify Python Debugger extension installed
- **Breakpoint not hit:** Verify test actually runs (check test name matches)
- **Variables not shown:** Expand "Locals" section in Variables panel

---

### 4. Coverage Visualization

**Objective:** Verify Coverage Gutters shows coverage indicators in editor.

**Steps:**
1. Run tests with coverage from terminal:
   ```bash
   uv run pytest tests/unit/tools/test_cursor.py --cov=src --cov-report=xml
   ```
2. Wait for tests to complete
3. Verify `coverage.xml` exists in workspace root
4. Open source file: `src/agent_orchestration/tools/cursor.py`
5. Look for coverage indicators in gutter (left of line numbers)
6. Click **Watch** in Coverage Gutters status bar (bottom right)

**Expected Outcomes:**
- ✅ Green indicators on covered lines
- ✅ Red indicators on uncovered lines
- ✅ Coverage Gutters status bar shows coverage percentage
- ✅ Clicking "Watch" enables auto-refresh
- ✅ Running tests again updates indicators automatically

**Coverage Indicator Colors:**
- 🟢 **Green:** Line is covered by tests
- 🔴 **Red:** Line is not covered by tests
- 🟡 **Yellow:** Line is partially covered (branch coverage)
- ⚪ **No indicator:** Line is not executable (comments, blank lines)

**Troubleshooting:**
- **No indicators:** Click "Watch" in Coverage Gutters status bar
- **Still no indicators:** Verify `coverage.xml` exists and is recent
- **Wrong coverage:** Delete `.coverage` and `coverage.xml`, re-run tests
- **Extension not working:** Reload VS Code window (Ctrl+Shift+P → "Reload Window")

---

### 5. Task Execution

**Objective:** Verify all test tasks execute correctly.

**Steps:**
1. Open Command Palette (Ctrl+Shift+P)
2. Type "Tasks: Run Task"
3. Select each test task and verify execution:

**Tasks to Test:**
- ✅ **Test: Run All Tests**
  - Command: `uv run pytest`
  - Expected: All tests run, coverage report shown

- ✅ **Test: Run All Tests with Coverage**
  - Command: `uv run pytest --cov=src --cov-report=html --cov-report=term-missing`
  - Expected: Tests run, HTML coverage report generated

- ✅ **Test: Run Unit Tests**
  - Command: `uv run pytest tests/unit/`
  - Expected: Only unit tests run

- ✅ **Test: Run Integration Tests**
  - Command: `uv run pytest tests/integration/ --neo4j --redis`
  - Expected: Integration tests run (requires services)

- ✅ **Test: Run Current File Tests**
  - Command: `uv run pytest ${file}`
  - Expected: Tests in currently open file run

- ✅ **Test: Run Failed Tests**
  - Command: `uv run pytest --lf`
  - Expected: Only previously failed tests run

**Expected Outcomes:**
- ✅ Each task executes in dedicated terminal
- ✅ Commands use `uv run pytest` (not `uvx pytest`)
- ✅ Output appears in Terminal panel
- ✅ Can stop running task (trash can icon)

**Troubleshooting:**
- **Task not found:** Verify `.vscode/tasks.json` exists
- **Command fails:** Check virtual environment is activated
- **Integration tests fail:** Ensure Docker services running (`docker compose up -d neo4j redis`)

---

## Validation Summary

After completing all verification steps, confirm:

- [ ] Test discovery works (1,700+ tests discovered)
- [ ] Can run tests from Testing panel
- [ ] Can debug tests with breakpoints
- [ ] Coverage indicators appear in editor
- [ ] All test tasks execute correctly
- [ ] No errors in Output panel → Python
- [ ] No errors in Output panel → Coverage Gutters

**If all items checked:** ✅ VS Code testing integration is working correctly

**If any items unchecked:** Review troubleshooting sections and verify configuration files

---

## Common Issues and Solutions

### Issue: Tests Not Discovered

**Symptoms:**
- Testing panel shows "No tests discovered"
- Refresh button doesn't help

**Solutions:**
1. Check Python interpreter: Click interpreter in status bar → Select `.venv/bin/python`
2. Check pytest path: Verify `.vscode/settings.json` has `python.testing.pytestPath: "${workspaceFolder}/.venv/bin/python"`
3. Check Output panel: Output → Python → Look for discovery errors
4. Reload window: Ctrl+Shift+P → "Reload Window"

### Issue: Coverage Indicators Not Showing

**Symptoms:**
- No green/red indicators in gutter
- Coverage Gutters status bar shows "No coverage"

**Solutions:**
1. Run tests with coverage: `uv run pytest --cov=src --cov-report=xml`
2. Verify `coverage.xml` exists: `ls -la coverage.xml`
3. Click "Watch" in Coverage Gutters status bar
4. Check Coverage Gutters settings: `.vscode/settings.json` should have `coverage-gutters.coverageFileNames: ["coverage.xml", "htmlcov/index.html"]`
5. Reload window: Ctrl+Shift+P → "Reload Window"

### Issue: Debugger Not Stopping at Breakpoints

**Symptoms:**
- Breakpoint set but debugger doesn't stop
- Test runs to completion without pausing

**Solutions:**
1. Verify breakpoint is on executable line (not comment or blank line)
2. Verify test actually runs (check test name matches)
3. Check `justMyCode` setting: `.vscode/launch.json` should have `"justMyCode": false`
4. Try setting breakpoint in test function body (not in setup/teardown)

### Issue: Tasks Use Wrong Command

**Symptoms:**
- Tasks run `uvx pytest` instead of `uv run pytest`
- Coverage shows 0%

**Solutions:**
1. Check `.vscode/tasks.json`: All test tasks should use `uv run pytest`
2. If wrong, update tasks.json and reload window
3. Verify by running task and checking terminal output

---

## Related Documentation

- **Testing Infrastructure Guide:** `docs/development/TESTING_INFRASTRUCTURE.md`
- **AI Agent Testing Guide:** `docs/development/AI_AGENT_TESTING_GUIDE.md`
- **VS Code Settings:** `.vscode/settings.json`
- **VS Code Tasks:** `.vscode/tasks.json`
- **VS Code Launch Configs:** `.vscode/launch.json`

---

**Last Updated:** 2025-10-23
**Status:** Active


---
**Logseq:** [[TTA.dev/Docs/Development/Vscode_testing_verification]]
