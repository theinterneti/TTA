# Contributing to TTA

> ⚠️ **This document has moved to the TTA Knowledge Base!**

**New location:** `.augment/kb/TTA___Workflows___Docs Development Contributing.md`

## 📚 Working with the Knowledge Base

When contributing to TTA, follow these KB conventions:

### Documentation Location
- **Core docs:** `.augment/kb/TTA___Category___PageName.md`
- **Format:** Flat structure, triple-underscore naming
- **Accessible via:** `~/repos/TTA-notes/logseq/pages/TTA/` (Logseq)

### Creating New Documentation

1. **Choose category:** Architecture, Components, Workflows, References, Status, Testing, Research
2. **Name format:** `TTA___Category___Your Page Name.md`
3. **Add frontmatter:**
```yaml
---
title: Your Page Title
tags: #TTA #Category
status: Active
repo: theinterneti/TTA
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```
4. **Use wiki-links:** `[[TTA___Category___Other Page]]` for cross-references
5. **Add to KB:** Files in `.augment/kb/` automatically visible in Logseq

### Updating Existing Docs

- **Stubs in repo root:** Update KB file, not the stub
- **Original locations:** Use stub redirects for backward compatibility
- **KB files:** Edit directly in `.augment/kb/`
- **Update dates:** Change `updated:` field in frontmatter

### Code Documentation Conventions

When referencing KB docs from code:

```python
# Reference KB doc in docstrings
"""
Agent orchestration implementation.

Architecture: See [[TTA___Architecture___Agent Orchestration]]
Status: See [[TTA___Status___Implementation Dashboard]]
"""
```

### Finding Documentation

**In Logseq:**
- Open `~/repos/TTA-notes`
- Search: `Ctrl+K` (or `Cmd+K`)
- Browse: Click TTA namespace
- Tags: Search `#TTA #Category`

**In Terminal:**
```bash
# Search KB files
cd .augment/kb
grep -r "search term" .

# List by category
ls -1 TTA___Architecture___*.md
ls -1 TTA___Components___*.md
```

### Related Documents

- **[[TTA___References___Agents Document]]** - Universal agent context
- **[[TTA___Status___Project Timeline]]** - Development history
- **[[TTA___Status___Implementation Dashboard]]** - Component status

**See AGENTS.md for complete KB structure and navigation guide.**

**Migration date:** 2025-11-01
