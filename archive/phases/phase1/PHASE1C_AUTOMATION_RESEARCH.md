# Phase 1C: Type Annotation Automation Research

**Date:** 2025-10-02
**Status:** 🔍 **RESEARCH COMPLETE**

---

## 📊 Problem Statement

**Mypy Error Count:** 4,695 errors in 334 files

**Time Estimate (Manual):** 48+ hours (at 97 errors/hour with automation from Phase 1B)

**Challenge:** Phase 1C is 13x larger than Phase 1B (4,695 vs 363 errors), making manual annotation impractical.

---

## 🔍 Automated Type Annotation Tools Research

### 1. MonkeyType (Instagram) ⭐ **MOST PROMISING**

**Source:** https://github.com/Instagram/MonkeyType
**Status:** Active, 4.9k stars, maintained by Instagram/Meta

**How it works:**
- Uses `sys.setprofile()` hook to collect runtime types
- Records function arguments, return values, and generator yields
- Generates stub files or applies annotations directly to code
- Uses libcst for code modification (preserves formatting)

**Key Features:**
- ✅ Runtime type inference (actual types used in execution)
- ✅ Can generate stub files or apply annotations directly
- ✅ Preserves code formatting
- ✅ Works with Python 3.9+
- ✅ Handles async/await functions
- ✅ SQLite database for storing type traces

**Installation:**
```bash
pip install MonkeyType
# or
uv pip install MonkeyType
```

**Usage Workflow:**
```bash
# 1. Run your code with MonkeyType to collect types
monkeytype run myscript.py

# 2. Generate stub file for a module
monkeytype stub some.module

# 3. Apply annotations directly to code
monkeytype apply some.module
```

**Pros:**
- ✅ Proven at scale (used by Instagram)
- ✅ Runtime inference = accurate for actual usage
- ✅ Can apply annotations directly to source
- ✅ Handles complex types (generics, unions, etc.)
- ✅ Works with existing test suites

**Cons:**
- ⚠️ Requires running code to collect types
- ⚠️ Only captures types actually used at runtime
- ⚠️ May generate overly specific types (e.g., `List[int]` instead of `Sequence[int]`)
- ⚠️ Requires comprehensive test coverage for best results

**Compatibility with TTA:**
- ✅ Python 3.12 compatible
- ✅ Works with async/await (FastAPI)
- ✅ Can handle complex types (Neo4j, Redis clients)
- ✅ Can be run with existing test suite

---

### 2. autotyping ⭐ **COMPLEMENTARY TOOL**

**Source:** https://pypi.org/project/autotyping/
**Status:** Active, recommended by mypy docs

**How it works:**
- Static analysis-based type inference
- Adds simple type annotations based on code patterns
- Can be used as pre-commit hook
- Focuses on low-hanging fruit (simple patterns)

**Key Features:**
- ✅ Static analysis (no runtime required)
- ✅ Can be automated via pre-commit
- ✅ Fast (no need to run tests)
- ✅ Handles simple patterns well

**Installation:**
```bash
pip install autotyping
# or
uv pip install autotyping
```

**Usage:**
```bash
# Apply to specific files
autotyping path/to/file.py

# Apply to entire directory
autotyping src/
```

**Pros:**
- ✅ No runtime execution required
- ✅ Fast and simple
- ✅ Good for simple patterns
- ✅ Can be automated

**Cons:**
- ⚠️ Limited to simple type inference
- ⚠️ Cannot infer complex types
- ⚠️ May miss many cases that require runtime info

**Compatibility with TTA:**
- ✅ Python 3.12 compatible
- ✅ Can handle simple cases quickly
- ⚠️ Limited effectiveness for complex TTA codebase

---

### 3. pytype (Google)

**Source:** https://github.com/google/pytype
**Status:** Active, maintained by Google

**How it works:**
- Static type inference and checking
- Can infer types without annotations
- Generates .pyi stub files
- More permissive than mypy

**Key Features:**
- ✅ Static analysis with type inference
- ✅ Can check code without annotations
- ✅ Generates stub files
- ✅ Used at Google scale

**Pros:**
- ✅ No runtime execution required
- ✅ Can infer types from code flow
- ✅ Proven at scale

**Cons:**
- ⚠️ Slower than mypy
- ⚠️ Different type system than mypy
- ⚠️ May conflict with mypy's stricter rules
- ⚠️ Complex setup

**Compatibility with TTA:**
- ⚠️ May conflict with existing mypy configuration
- ⚠️ Different type inference rules
- ❌ Not recommended for mypy-based projects

---

### 4. PyAnnotate (Dropbox) - DEPRECATED

**Status:** ⚠️ **DEPRECATED** - No longer maintained

**Note:** PyAnnotate was an early runtime type collector, but has been superseded by MonkeyType.

---

### 5. VS Code / Pylance

**Source:** VS Code Python extension with Pylance

**Features:**
- ✅ Type inference in IDE
- ✅ Auto-complete based on inferred types
- ✅ Can suggest type annotations
- ⚠️ Manual process (not bulk automation)

**Compatibility with TTA:**
- ✅ Already available in VS Code
- ⚠️ Not suitable for bulk annotation (4,695 errors)
- ✅ Good for manual review/refinement

---

## 🎯 Recommended Strategy: Hybrid Approach with MonkeyType

### Phase 1C Revised: "MonkeyType-Assisted Type Annotation"

**Approach:** Use MonkeyType to generate initial annotations, then manual review/refinement

**Estimated Time:** 8-12 hours (vs 48+ hours manual)

**Time Breakdown:**
1. **Setup & Test Run (1-2 hours):**
   - Install MonkeyType
   - Run comprehensive test suite with MonkeyType
   - Verify type collection works
   - Review collected types

2. **Batch 1: Public API Functions (2-3 hours):**
   - Apply MonkeyType to public API modules
   - Review and refine generated annotations
   - Focus on `src/player_experience/api/` and `src/components/`
   - Target: 500-800 annotations

3. **Batch 2: Core Components (2-3 hours):**
   - Apply to core gameplay and narrative modules
   - Review and refine
   - Target: 500-800 annotations

4. **Batch 3: Database & Infrastructure (2-3 hours):**
   - Apply to database repositories and infrastructure
   - Review and refine
   - Target: 400-600 annotations

5. **Manual Review: Critical Errors (1-2 hours):**
   - Focus on `attr-defined` (601 errors) - potential bugs
   - Focus on `call-arg` (424 errors) - wrong arguments
   - Fix high-priority type errors manually

**Expected Result:**
- 1,500-2,200 functions annotated (vs 2,101 `no-untyped-def` errors)
- 70-100% of `no-untyped-def` errors resolved
- 30-50% overall mypy error reduction (1,400-2,300 errors fixed)
- Remaining errors: Complex cases requiring manual review

---

## 📋 Implementation Plan

### Step 1: Install MonkeyType

```bash
uv pip install MonkeyType
```

### Step 2: Run Test Suite with MonkeyType

```bash
# Run comprehensive test suite to collect types
monkeytype run -m pytest tests/

# Or run specific test modules
monkeytype run -m pytest tests/test_end_to_end_workflows.py
monkeytype run -m pytest tests/integration/
```

### Step 3: Generate Stub Files (Preview)

```bash
# Preview annotations for a module
monkeytype stub src.player_experience.api.app

# Generate stub file
monkeytype stub src.player_experience.api.app > stubs/api_app.pyi
```

### Step 4: Apply Annotations (Batch)

```bash
# Apply to specific module
monkeytype apply src.player_experience.api.app

# Review changes with git diff
git diff src/player_experience/api/app.py
```

### Step 5: Verify & Refine

```bash
# Run mypy to check new annotations
uv run mypy src/player_experience/api/app.py

# Run tests to ensure no regressions
uv run pytest tests/

# Refine annotations manually where needed
```

### Step 6: Commit in Batches

```bash
# Commit each batch separately
git add src/player_experience/api/
git commit -m "feat(types): add type annotations to API modules (MonkeyType)"
```

---

## ⚠️ Limitations & Considerations

### MonkeyType Limitations

1. **Runtime Coverage:** Only captures types actually used during test execution
   - **Mitigation:** Run comprehensive test suite
   - **Mitigation:** Run with multiple test scenarios

2. **Overly Specific Types:** May generate `List[int]` instead of `Sequence[int]`
   - **Mitigation:** Manual review and refinement
   - **Mitigation:** Use abstract types where appropriate

3. **Missing Edge Cases:** Won't capture types for untested code paths
   - **Mitigation:** Focus on well-tested modules first
   - **Mitigation:** Manual annotation for untested code

4. **Complex Types:** May struggle with complex generics or protocols
   - **Mitigation:** Manual refinement for complex cases

### TTA-Specific Considerations

1. **Async/Await:** MonkeyType handles async functions
   - ✅ FastAPI routes will be annotated correctly

2. **Database Clients:** Neo4j and Redis types may need refinement
   - ⚠️ May generate overly specific client types
   - **Mitigation:** Use abstract types (e.g., `AsyncSession`)

3. **Test Coverage:** Requires good test coverage
   - ✅ TTA has comprehensive test suite
   - ✅ Can run integration tests for better coverage

4. **Type Complexity:** Some TTA types are complex (agents, narratives)
   - ⚠️ May require manual refinement
   - **Mitigation:** Focus on simpler modules first

---

## 💡 Recommendation

### Option A: Proceed with MonkeyType-Assisted Phase 1C ⭐ **RECOMMENDED**

**Rationale:**
- Reduces time from 48+ hours to 8-12 hours (75% time savings)
- Proven tool used at Instagram scale
- Works with existing test suite
- Generates accurate annotations for actual usage
- Can be done incrementally

**Next Steps:**
1. Install MonkeyType
2. Run test suite with MonkeyType to collect types
3. Apply annotations in batches (API → Core → Infrastructure)
4. Manual review and refinement
5. Commit in focused batches

**Expected Outcome:**
- 30-50% mypy error reduction (1,400-2,300 errors fixed)
- 70-100% of `no-untyped-def` errors resolved
- Improved code quality and IDE support
- Foundation for ongoing type annotation

### Option B: Quick Wins Only (No MonkeyType)

**Scope:** Fix only easiest errors manually (2-3 hours)
- unused-ignore (61 errors)
- import-untyped (69 errors)
- Simple public API annotations (~50-100 functions)

**Expected Outcome:** 200-300 errors fixed (5-6% reduction)

### Option C: Defer Phase 1C Entirely

**Rationale:** Focus on deployment infrastructure
**Next Steps:** Move to Phase 1D or Phase 2

---

## ✅ Decision Required

**Please choose:**

**A) Proceed with MonkeyType-Assisted Phase 1C** ⭐ **RECOMMENDED**
   - 8-12 hours, 30-50% error reduction
   - Install MonkeyType and begin type collection

**B) Quick Wins Only (No MonkeyType)**
   - 2-3 hours, 5-6% error reduction
   - Manual annotation of simple cases

**C) Defer Phase 1C Entirely**
   - 0 hours, move to Phase 1D or Phase 2
   - Address type checking incrementally later

---

**Awaiting your decision on Phase 1C approach!**


---
**Logseq:** [[TTA.dev/Archive/Phases/Phase1/Phase1c_automation_research]]
