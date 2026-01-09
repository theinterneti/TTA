# Mutation Testing Environment Issue - Resolution and Alternatives

**Date:** 2025-10-10
**Issue:** Mutmut import errors preventing execution
**Status:** ⚠️ Blocker identified, alternative solutions provided

---

## Problem Summary

### Root Cause

Mutmut has a fundamental incompatibility with complex Python package structures:

1. **File Copying Behavior:** Mutmut copies only files from `paths_to_mutate` to a `mutants/` directory
2. **Missing Parent Packages:** It does NOT copy parent `__init__.py` files needed for package imports
3. **Test Discovery Issue:** Pytest auto-discovers ALL test files, even those not specified in the runner command
4. **Import Failures:** Tests fail with `ModuleNotFoundError` because Python can't recognize directories as packages without `__init__.py`

### Specific Issues Encountered

**Issue 1: Missing `__init__.py` Files**
```
mutants/
├── src/
│   ├── components/          # ❌ Missing __init__.py
│   │   └── model_management/
│   │       ├── __init__.py  # ✓ Present
│   │       └── services/
│   │           └── model_selector.py
│   └── __init__.py          # ❌ Missing
```

**Issue 2: Test Auto-Discovery**
```bash
# Even when specifying one test file:
runner=pytest tests/unit/model_management/services/test_model_selector_properties.py

# Pytest still tries to collect ALL tests:
ERROR collecting tests/agent_orchestration/test_agent_orchestration_service.py
ERROR collecting tests/integration/...
```

**Issue 3: Complex Package Dependencies**
```python
# src/components/__init__.py tries to import other components:
from .agent_orchestration_component import AgentOrchestrationComponent
# ❌ Fails because agent_orchestration isn't in mutants directory
```

---

## Attempted Solutions

### ❌ Solution 1: Copy Parent `__init__.py` Files
**Approach:** Created `scripts/setup_mutants_env.py` to copy missing files
**Result:** Failed - parent `__init__.py` files import other components not in mutants directory
**Blocker:** Circular dependencies and missing sibling packages

### ❌ Solution 2: Broader `paths_to_mutate`
**Approach:** Changed from `services/` to entire `model_management/` directory
**Result:** Failed - still missing `src/` and `src/components/` `__init__.py` files
**Blocker:** Would need to mutate entire `src/` directory (too broad)

### ❌ Solution 3: Pytest `--ignore` Flags
**Approach:** Added `--ignore` flags to skip other test directories
**Result:** Failed - pytest still auto-discovers and tries to import all tests
**Blocker:** Pytest's test discovery happens before `--ignore` is processed

### ❌ Solution 4: Custom Test Runner Script
**Approach:** Created wrapper script to run from project root
**Result:** Failed - mutmut modifies files in mutants directory, so imports must come from there
**Blocker:** Can't import from project root when testing mutated code

---

## Recommended Solutions

### ✅ Solution A: Use Cosmic Ray (Recommended)

**Cosmic Ray** is a more modern mutation testing tool that handles package structures better.

**Installation:**
```bash
uv add --dev cosmic-ray
```

**Configuration (`cosmic-ray.toml`):**
```toml
[cosmic-ray]
module-path = "src/components/model_management/services/model_selector.py"
timeout = 10.0
excluded-modules = []
test-command = "uv run pytest tests/unit/model_management/services/test_model_selector_properties.py -x -q"

[cosmic-ray.distributor]
name = "local"

[cosmic-ray.cloning]
method = "copy"
commands = []
```

**Usage:**
```bash
# Initialize
cosmic-ray init cosmic-ray.toml session.sqlite

# Run mutation testing
cosmic-ray exec session.sqlite

# View results
cr-report session.sqlite
```

**Advantages:**
- Better package structure handling
- More active development
- Cleaner configuration
- Better reporting

### ✅ Solution B: Manual Mutation Testing

For immediate results without tool setup issues:

**1. Create Manual Mutations:**
```python
# Example: Manually mutate model_selector.py
# Original:
if score > best_score:
    best_model = model

# Mutation 1: Change comparison operator
if score >= best_score:  # Changed > to >=
    best_model = model

# Mutation 2: Change assignment
if score > best_score:
    best_model = None  # Changed model to None
```

**2. Run Tests:**
```bash
uv run pytest tests/unit/model_management/services/test_model_selector_properties.py -v
```

**3. Check Results:**
- If tests PASS with mutation → Surviving mutant (test gap)
- If tests FAIL with mutation → Killed mutant (good coverage)

**Advantages:**
- No tool setup required
- Immediate results
- Full control over mutations
- Good for targeted testing

### ✅ Solution C: Simplified Mutmut Setup (Workaround)

**Approach:** Mutate entire `src/` directory to ensure all `__init__.py` files are copied.

**Configuration:**
```ini
[mutmut]
paths_to_mutate=src/
backup=False
runner=uv run pytest tests/unit/model_management/services/test_model_selector_properties.py::TestModelSelectorProperties -x -q --tb=no
tests_dir=tests/
```

**Limitations:**
- Will generate mutants for ALL code in `src/` (thousands of mutants)
- Very slow (could take 10+ hours)
- Most mutants won't be relevant to model_selector tests
- Not practical for regular use

### ✅ Solution D: CI/CD Integration with Isolated Environment

**Approach:** Run mutation testing in a clean Docker container or CI/CD environment.

**GitHub Actions Example:**
```yaml
name: Mutation Testing

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly

jobs:
  mutation-test:
    runs-on: ubuntu-latest
    container:
      image: python:3.12

    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          pip install uv
          uv sync

      - name: Run mutation testing (Cosmic Ray)
        run: |
          cosmic-ray init cosmic-ray.toml session.sqlite
          cosmic-ray exec session.sqlite
          cr-report session.sqlite > mutation-report.txt

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: mutation-report
          path: mutation-report.txt
```

**Advantages:**
- Clean environment each time
- No local setup issues
- Automated and scheduled
- Results archived

---

## Immediate Recommendation

**For this project, I recommend Solution B (Manual Mutation Testing) for immediate results, followed by Solution A (Cosmic Ray) for long-term automated mutation testing.**

### Why Manual Testing Now?

1. **Immediate Results:** Can validate test quality today
2. **No Setup Issues:** Works with existing test infrastructure
3. **Targeted:** Focus on critical code paths
4. **Educational:** Understand what mutations reveal about tests

### Example Manual Mutation Test Session

**Target:** `model_selector.py` - `_calculate_model_score()` method

**Mutation 1: Change scoring weight**
```python
# Original
score += model.therapeutic_safety_score * criteria.therapeutic_safety_weight

# Mutated
score += model.therapeutic_safety_score * 0  # Zero out weight
```

**Run Test:**
```bash
uv run pytest tests/unit/model_management/services/test_model_selector_properties.py::TestModelSelectorProperties::test_rank_models_returns_sorted_list -v
```

**Expected:** Test should FAIL (mutation killed)
**If PASS:** Test gap - need test that validates therapeutic safety scoring

---

## Long-Term Solution: Cosmic Ray

Once immediate testing is complete, set up Cosmic Ray for automated mutation testing:

**Steps:**
1. Install Cosmic Ray: `uv add --dev cosmic-ray`
2. Create configuration file (see Solution A above)
3. Run initial session on one module
4. Analyze results and improve tests
5. Integrate into CI/CD for weekly runs

---

## Updated Mutation Testing Guide

The `MUTATION_TESTING_GUIDE.md` should be updated with:

1. **Known Issues Section:** Document mutmut limitations
2. **Alternative Tools:** Add Cosmic Ray as primary recommendation
3. **Manual Testing Guide:** Step-by-step manual mutation testing
4. **Workarounds:** Document the solutions attempted and their limitations

---

## Conclusion

**Mutmut is not suitable for this project's package structure** due to its file copying behavior and inability to handle complex package hierarchies.

**Recommended Path Forward:**
1. **Short-term:** Use manual mutation testing to validate critical code paths
2. **Long-term:** Migrate to Cosmic Ray for automated mutation testing
3. **CI/CD:** Integrate Cosmic Ray into weekly scheduled runs

**Estimated Effort:**
- Manual testing: 2-4 hours for critical paths
- Cosmic Ray setup: 1-2 hours
- CI/CD integration: 1 hour

**Expected Benefits:**
- Identify 5-10 test gaps in critical code
- Improve mutation score from estimated 70% to >85%
- Automated weekly mutation testing
- Better long-term test quality assurance

---

## Files Created/Modified

**Created:**
- `scripts/setup_mutants_env.py` - Attempted fix (not successful)
- `scripts/run_mutation_tests.sh` - Test runner wrapper
- `docs/testing/MUTATION_TESTING_RESOLUTION.md` - This document

**Modified:**
- `setup.cfg` - Multiple attempts to configure mutmut
- `docs/testing/MUTATION_TESTING_GUIDE.md` - Needs update with findings
- `docs/testing/PHASE_3_IMPLEMENTATION_SUMMARY.md` - Needs update with resolution

---

## Next Steps

1. ✅ Document the issue and solutions (this document)
2. ⏭️ Perform manual mutation testing on ModelSelector (2-3 critical mutations)
3. ⏭️ Update Phase 3 summary with findings
4. ⏭️ Create Cosmic Ray configuration for future use
5. ⏭️ Update mutation testing guide with alternative approaches


---
**Logseq:** [[TTA.dev/Docs/Testing/Mutation_testing_resolution]]
