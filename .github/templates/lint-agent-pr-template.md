## 🎨 Automated Style Fix

**Triggered by**: {{ TRIGGER_DESCRIPTION }}
**Agent**: @lint-agent
**Timestamp**: {{ TIMESTAMP }}

---

### Changes

- Fixed {{ VIOLATIONS_COUNT }} Ruff violations
- Formatted {{ FILES_COUNT }} files to 88-char line length
- Sorted imports in {{ IMPORT_FILES_COUNT }} modules
- Modernized {{ TYPE_HINTS_COUNT }} type hints to Python 3.12 syntax

---

### Violations Fixed

| Rule | Count | Description |
|------|-------|-------------|
{{ VIOLATIONS_TABLE_ROWS }}

---

### Files Modified

{{ FILES_MODIFIED_LIST }}

---

### Verification

✅ All tests pass: `uv run pytest -q -m "not integration" tests/`
✅ No behavior changes (verified with `git diff --stat`)
✅ Pyright type check passes
✅ Only style modifications (no logic changes)

**Test Results**:
```
{{ TEST_OUTPUT }}
```

---

### Diff Summary

```
{{ GIT_DIFF_STAT }}
```

**Total Changes**: {{ TOTAL_LINES_CHANGED }} lines across {{ FILES_COUNT }} files

---

### Ruff Violations Before/After

**Before**: {{ VIOLATIONS_BEFORE }} violations
**After**: {{ VIOLATIONS_AFTER }} violations
**Fixed**: {{ VIOLATIONS_FIXED }} violations ({{ FIX_RATE }}% auto-fixed)

---

### Boundary Compliance

✅ Only style/formatting changes
✅ No function signature modifications
✅ No test assertion changes
✅ No business logic alterations
✅ All tests still pass

---

### Action Required

**Review Checklist**:
- [ ] Diff shows only whitespace/formatting changes
- [ ] No semantic changes to code
- [ ] All tests still pass
- [ ] No new imports added (only sorted/removed)

**Approval**: Review and approve for merge to `{{ BASE_BRANCH }}`

---

**Agent**: @lint-agent v1.0.0
**Audit Trail**: `docs/kb-exports/lint-agent-activity.md`
**CI Run**: [View original failure]({{ CI_RUN_URL }})
