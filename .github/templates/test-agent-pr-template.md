## 🧪 Automated Test Coverage Improvement

**Triggered by**: {{ TRIGGER_DESCRIPTION }}
**Agent**: @test-agent
**Module**: `{{ MODULE_PATH }}`
**Timestamp**: {{ TIMESTAMP }}

---

### Changes

- Added {{ TESTS_ADDED }} tests for `{{ TARGET_CLASS }}` class/module
- Increased coverage from {{ COVERAGE_BEFORE }}% → {{ COVERAGE_AFTER }}% (+{{ COVERAGE_DELTA }}%)
- Added/reused fixtures from conftest.py

---

### Tests Added

| Test Function | Purpose | Coverage Impact |
|---------------|---------|-----------------|
{{ TEST_TABLE_ROWS }}

---

### Verification

✅ All tests pass: `uv run pytest {{ TEST_FILE_PATH }} -v`
✅ Coverage target met: {{ COVERAGE_AFTER }}% ≥ {{ COVERAGE_THRESHOLD }}%
✅ No application code modified (tests/ only)
✅ Fixtures reused from conftest.py
✅ Type hints included on all test functions
✅ AAA pattern (Arrange-Act-Assert) followed
✅ Pytest markers added appropriately

---

### Test Organization

**Test File**: `{{ TEST_FILE_PATH }}`
**Markers Used**: {{ MARKERS_LIST }}
**Fixtures Used**: {{ FIXTURES_LIST }}

---

### Code Quality

```bash
# Run tests
uv run pytest {{ TEST_FILE_PATH }} -v

# Check coverage
uv run pytest --cov={{ MODULE_PATH }} tests/

# Verify no src/ changes
git diff --stat | grep -v "tests/"
```

---

### Boundary Compliance

✅ Only `tests/` directory modified
✅ No `src/` application code changes
✅ No test deletions
✅ All tests documented with docstrings

---

### Action Required

**Review Checklist**:
- [ ] Tests are meaningful and add value
- [ ] Coverage increase justifies changes
- [ ] No business logic bugs masked by new tests
- [ ] Fixtures are appropriate and reusable

**Approval**: Review and approve for merge to `{{ BASE_BRANCH }}`

---

**Agent**: @test-agent v1.0.0
**Audit Trail**: `docs/kb-exports/test-agent-activity.md`
