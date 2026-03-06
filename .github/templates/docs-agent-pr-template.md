## 📚 Automated Documentation Update

**Triggered by**: {{ TRIGGER_DESCRIPTION }}
**Agent**: @docs-agent
**Timestamp**: {{ TIMESTAMP }}

---

### Changes

{{ CHANGE_SUMMARY }}

---

### Documentation Updated

| File | Status | Changes |
|------|--------|---------|
{{ DOCS_TABLE_ROWS }}

---

### Source Modules

| Module | Docstrings Extracted | Examples Found |
|--------|---------------------|----------------|
{{ MODULES_TABLE_ROWS }}

---

### Validation Results

✅ MkDocs build successful (`mkdocs build --strict`)
✅ No broken links detected
✅ All code examples valid Python
✅ Cross-references verified
✅ Navigation updated in `mkdocs.yml`

**Build Output**:
```
{{ MKDOCS_BUILD_OUTPUT }}
```

---

### Preview

🔗 **Local Preview**: Run `uv run mkdocs serve` and visit http://localhost:8000

**Updated Pages**:
{{ UPDATED_PAGES_LIST }}

---

### Boundary Compliance

✅ Only `docs/` and `mkdocs.yml` modified
✅ No `src/` application code changes
✅ No dependency modifications
✅ Existing docs archived before major rewrites

---

### Action Required

**Review Checklist**:
- [ ] Documentation is accurate and complete
- [ ] Code examples compile and match current codebase
- [ ] Cross-references are correct
- [ ] Navigation structure makes sense
- [ ] "Last Updated" timestamps included

**Approval**: Review and approve for merge to `{{ BASE_BRANCH }}`

---

**Agent**: @docs-agent v1.0.0
**Audit Trail**: `docs/kb-exports/docs-agent-activity.md`
**Related Code PR**: #{{ SOURCE_PR_NUMBER }}
