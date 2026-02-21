# Quick Action Plan for PR #73 🚀

## Current Status

**PR**: #73 - feat: Phase 2 Async OpenHands Integration + MockPrimitive Refactoring
**Copilot Comments**: 5 (unresolved)
**Status Checks**: Unknown
**Auto-merge**: Not enabled

## 🎯 Action Items

### 1. Fix Copilot Comments (Required)

#### Issue 1 & 2: `test_router_primitive.py` and `test_cache_primitive.py`

**Problem**: MockPrimitive modifies `__class__.__name__`

**Files**:
- `tests/unit/observability_integration/test_router_primitive.py` (line 16)
- `tests/unit/observability_integration/test_cache_primitive.py` (line 19)

**Fix**: Remove `self.__class__.__name__ = name` from MockPrimitive

**Working example** (already done in `test_timeout_primitive.py`):

```python
class MockPrimitive:
    """Mock primitive for testing."""

    def __init__(self, name="mock", delay=0.0, raise_error=False):
        # ✅ Store name as instance variable (not class attribute)
        self.name = name
        self.delay = delay
        self.raise_error = raise_error
        self.call_count = 0
        # ❌ REMOVE THIS LINE:
        # self.__class__.__name__ = name
```

#### Issue 3: `openhands_stage.py`

**Problem**: `_generate_tests_for_module` creates new event loop

**File**: `scripts/workflow/openhands_stage.py`

**Current code**:
```python
def _generate_tests_for_module(...):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(...)
```

**Fix**: Use `asyncio.run()` instead:
```python
def _generate_tests_for_module(...):
    return asyncio.run(
        self._async_generate_tests_for_module(...)
    )
```

#### Issue 4: `main.py`

**Problem**: Incomplete install command in error message

**File**: `src/main.py` (line 75)

**Current**:
```python
"Observability integration not available - install with: uv add opentelemetry-api opentelemetry-sdk"
```

**Fix**:
```python
"Observability integration not available - install with: uv add opentelemetry-api opentelemetry-sdk opentelemetry-exporter-prometheus"
```

### 2. Apply Fixes

```bash
# Navigate to repo
cd /home/thein/recovered-tta-storytelling

# Option A: Manual edits
# Edit the 4 files mentioned above

# Option B: Use sed for quick fixes (example)
# Fix main.py
sed -i 's/opentelemetry-sdk"/opentelemetry-sdk opentelemetry-exporter-prometheus"/' src/main.py

# Commit and push
git add tests/unit/observability_integration/test_router_primitive.py \
        tests/unit/observability_integration/test_cache_primitive.py \
        scripts/workflow/openhands_stage.py \
        src/main.py

git commit -m "fix: address Copilot review feedback

- Remove __class__.__name__ modifications in MockPrimitive (test_router_primitive.py, test_cache_primitive.py)
- Use asyncio.run() instead of new_event_loop in openhands_stage.py
- Complete OpenTelemetry installation command in main.py

Resolves Copilot review comments.
"

git push
```

### 3. Monitor Workflow

```bash
# Watch PR status in real-time
./scripts/pr-manager.sh watch 73 30

# Or check status manually
./scripts/pr-manager.sh details 73
./scripts/pr-manager.sh copilot 73
```

### 4. Enable Auto-Merge (When Ready)

Once all checks pass and Copilot comments are resolved:

```bash
./scripts/pr-manager.sh automerge 73
```

Or approve and merge manually:

```bash
# Approve
./scripts/pr-manager.sh approve 73 "Copilot feedback addressed, all checks passing ✅"

# Merge
./scripts/pr-manager.sh merge 73 squash
```

## ⏱️ Estimated Time

- **Fix code**: 5-10 minutes (simple changes)
- **Commit/push**: 1 minute
- **CI workflow**: 5-10 minutes
- **Total**: ~15-20 minutes

## ✅ Success Criteria

Before auto-merge can happen:

- ✅ All 5 Copilot comments resolved
- ✅ Quality gates passing (ruff, pyright, coverage)
- ✅ Tests passing (23/23)
- ✅ At least 1 approval
- ✅ Branch up to date with main

## 🎯 Quick Commands

```bash
# Check current Copilot comments
./scripts/pr-manager.sh copilot 73

# After pushing fixes, watch for completion
./scripts/pr-manager.sh watch 73 30

# When ready, enable auto-merge
./scripts/pr-manager.sh automerge 73
```

## 📝 Notes

- The fixes are straightforward - mostly removing problematic code
- Your PR already has comprehensive tests (23/23 passing)
- Documentation is complete
- Just need to address these 5 Copilot comments and you're done!

## 🚀 After Merge

Once PR #73 merges:

1. All future PRs will use the new automation
2. Reviewers auto-assigned based on changed files
3. Copilot reviews every PR automatically
4. Auto-merge kicks in when criteria met

---

**Ready to go?** Start with fixing the MockPrimitive issues - they're identical in both files! 🎉


---
**Logseq:** [[TTA.dev/.archive/Cicd/2025-10/Pr_73_action_plan]]
