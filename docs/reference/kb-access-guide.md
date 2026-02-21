# TTA Knowledge Base Access Guide

**Date:** November 2, 2025
**Status:** Active
**Purpose:** Guide for accessing TTA documentation in the centralized Knowledge Base

---

## Overview

As of November 1, 2025, TTA documentation has been migrated to a centralized **Knowledge Base** using Logseq. This guide explains how to access, navigate, and reference KB documents.

### Why the Migration?

**Before:** Documentation fragmented across multiple directories
- `.github/specs/` - API and feature specs
- `docs/` - Various documentation
- Inline README files
- Ad-hoc markdown files

**After:** Centralized Knowledge Base
- ✅ Single source of truth
- ✅ Bidirectional linking
- ✅ Graph-based navigation
- ✅ Consistent naming convention
- ✅ 306 consolidated documents

---

## Knowledge Base Structure

### Location

**Primary Location:** `~/repos/TTA-notes/logseq/pages/TTA/`
**Symlink in Project:** `.augment/kb/`
**Total Documents:** 306 markdown files

### Naming Convention

All KB files follow the **triple-underscore naming pattern**:

```
TTA___Category___Page Title.md
```

**Examples:**
- `TTA___References___Agents Document.md`
- `TTA___Architecture___Docs Architecture Agent Orchestration.md`
- `TTA___Status___Implementation Dashboard.md`
- `TTA___Components___API Endpoint Specification Template.md`

**Categories:**
- `References` - Key reference documents (AGENTS.md, CLAUDE.md, etc.)
- `Architecture` - System architecture and design docs
- `Status` - Project status, timeline, dashboards
- `Components` - Component specifications and technical details
- `Development` - Development guides and workflows
- `Testing` - Testing strategies and test documentation

---

## Access Methods

### Method 1: Logseq (Recommended)

**Best for:** Interactive exploration, graph navigation, bidirectional links

**Setup:**
1. Install Logseq: https://logseq.com/
2. Open graph: `File > Open...` → Select `~/repos/TTA-notes`
3. Navigate to TTA namespace

**Navigation:**
- **Search:** `Ctrl+K` (or `Cmd+K` on Mac) → Type page name
- **Wiki Links:** Click `[[TTA___Category___Page]]` to jump
- **Graph View:** Click graph icon to see connections
- **Backlinks:** See all pages linking to current page
- **Tags:** Search by `#TTA` to see all TTA pages

**Advantages:**
- ✅ Visual graph exploration
- ✅ Instant search across all content
- ✅ Bidirectional link following
- ✅ Real-time sync with file system
- ✅ Block-level references

### Method 2: Direct File Access

**Best for:** Viewing in VS Code, grep searches, scripts

**Path:** `.augment/kb/` (symlink to KB)

**Examples:**
```bash
# Read a specific document
cat .augment/kb/TTA___References___Agents\ Document.md

# Search across KB
grep -r "circuit breaker" .augment/kb/

# List all components
ls .augment/kb/TTA___Components___*

# Open in VS Code
code .augment/kb/TTA___Architecture___Docs\ Architecture\ Agent\ Orchestration.md
```

**Advantages:**
- ✅ Works with existing tools
- ✅ No special software required
- ✅ Scriptable access
- ✅ Works in terminal

### Method 3: GitHub Navigation

**Best for:** Sharing links, PR reviews, CI/CD

**Path:** `https://github.com/theinterneti/TTA/tree/main/.augment/kb/`

**Note:** Wiki-style links (`[[Page]]`) won't work on GitHub; use markdown links

**Advantages:**
- ✅ Shareable URLs
- ✅ Markdown rendering
- ✅ Version control integration

---

## Wiki-Links vs Markdown Links

### In Logseq (Wiki-Links)

Use double-bracket notation for internal links:

```markdown
See [[TTA___References___Agents Document]] for agent context.
```

**Advantages:**
- ✅ Autocomplete in Logseq
- ✅ Creates backlinks automatically
- ✅ Cleaner syntax

### In Other Tools (Markdown Links)

Convert to standard markdown for GitHub, VS Code preview, etc.:

```markdown
See [Agents Document](.augment/kb/TTA___References___Agents Document.md) for agent context.
```

**When to Use:**
- README files in GitHub
- Documentation that needs GitHub rendering
- CI/CD scripts that parse markdown

---

## Common Access Patterns

### Finding a Migrated Document

**If you know the old path:**

See [Documentation Migration Map](./documentation-migration-map.md) for full mapping table.

**Common migrations:**
```
OLD: .github/specs/api-endpoint.spec.md
NEW: .augment/kb/TTA___Components___API Endpoint Specification Template.md

OLD: docs/technical-specifications.md
NEW: .augment/kb/TTA___Components___TTA Technical Specifications.md

OLD: AGENTS.md
NEW: .augment/kb/TTA___References___Agents Document.md
```

### Searching for Content

**In Logseq:**
1. Press `Ctrl+K` (or `Cmd+K`)
2. Type search query
3. Results show matching pages and content
4. Click to jump to page

**In Terminal:**
```bash
# Find all references to "circuit breaker"
grep -r "circuit breaker" .augment/kb/ | less

# Find component specs
find .augment/kb -name "TTA___Components___*" -type f

# Search with context
grep -C 3 "therapeutic safety" .augment/kb/TTA___References___*
```

**In VS Code:**
1. `Ctrl+Shift+F` to open search
2. Set "files to include": `.augment/kb/**/*.md`
3. Enter search query

### Referencing KB Docs in Code

**In Python comments:**
```python
# For agent orchestration patterns, see:
# .augment/kb/TTA___Architecture___Docs Architecture Agent Orchestration.md
```

**In markdown documentation:**
```markdown
For detailed agent context, see the
[Agents Document](./.augment/kb/TTA___References___Agents Document.md).
```

**In commit messages:**
```
feat: Add circuit breaker to agent calls

Implements pattern from TTA___Architecture___Docs Architecture Agent Orchestration.md
See section "Circuit Breaker Pattern" for design rationale.
```

---

## Migration Status Reference

### Fully Migrated

The following document categories have been **fully migrated** to KB:

- ✅ **Technical Specifications** (`docs/technical-specifications.md`)
- ✅ **API Specifications** (`.github/specs/*.spec.md`)
- ✅ **Agent Context** (`AGENTS.md`)
- ✅ **Claude Context** (`CLAUDE.md`)
- ✅ **Project Overview** (`README.md` content consolidated)

**These files now contain migration notices:**
```markdown
> ⚠️ **This document has moved!**
> **New location:** [[TTA/Category/Page Title]]
> **Path:** `.augment/kb/TTA___Category___Page Title.md`
```

### Not Migrated (Still Active)

The following document categories remain in their **original locations**:

- ✅ **Specification Documents** (`.kiro/specs/`) - 54 active spec files
- ✅ **Instruction Files** (`.github/instructions/`) - 14 active instruction files
- ✅ **Spec Templates** (`specs/templates/`) - 3 active templates
- ✅ **Component Maturity** (`component-maturity-analysis.json`)
- ✅ **Development Guides** (most files in `docs/development/`)

**Reason:** These are actively used in CI/CD, scripts, and development workflows.

---

## Best Practices

### For Developers

1. **Check KB First:** Before creating new documentation, search KB
2. **Update KB:** When updating migrated docs, update KB not stub files
3. **Link to KB:** Reference KB paths in new documentation
4. **Use Absolute Paths:** When linking from code, use `.augment/kb/` prefix

### For AI Assistants

1. **Read from KB:** For migrated docs, always read from `.augment/kb/`
2. **Respect Stubs:** Don't edit stub files; update the KB location
3. **Cross-Reference:** When answering questions, provide KB paths
4. **Maintain Links:** When creating docs, use proper KB references

### For Documentation Authors

1. **Naming Convention:** Follow `TTA___Category___Title.md` pattern
2. **Bidirectional Links:** Use wiki-links within KB documents
3. **Update Migration Map:** When adding new KB docs, update the map
4. **Keep Stubs:** Leave migration notices in old locations

---

## Troubleshooting

### "I can't find a document"

1. **Check Migration Map:** See [documentation-migration-map.md](./documentation-migration-map.md)
2. **Search KB:** Use `grep -r "search term" .augment/kb/`
3. **Check Original Location:** Some docs haven't migrated yet
4. **Use Logseq Search:** Press `Ctrl+K` for fuzzy search

### "Wiki-links don't work in VS Code"

**Solution:** VS Code doesn't support wiki-links natively.

**Options:**
- Use Logseq for wiki-link navigation
- Install VS Code extension: "Markdown Wiki Links"
- Convert to markdown links for viewing: `[Title](path.md)`

### "The KB path is too long"

**Solution:** Use relative paths or symlinks.

**Example:**
```bash
# Create a shorter symlink
ln -s .augment/kb/TTA___Components___API\ Endpoint\ Specification\ Template.md docs/api-spec.md

# Reference it
cat docs/api-spec.md
```

### "How do I contribute to the KB?"

**Workflow:**
1. Open Logseq → TTA graph
2. Create or edit page
3. Save changes (auto-syncs to filesystem)
4. Commit changes from `~/repos/TTA-notes`
5. File appears in `.augment/kb/` via symlink

**Or via filesystem:**
1. Edit file directly in `.augment/kb/`
2. Logseq will detect changes automatically
3. Commit to version control

---

## Quick Reference

### Essential Paths

| Description | Path |
|-------------|------|
| **KB Root** | `.augment/kb/` |
| **KB Source** | `~/repos/TTA-notes/logseq/pages/TTA/` |
| **Spec Files** | `.kiro/specs/` |
| **Instructions** | `.github/instructions/` |
| **Templates** | `specs/templates/` |
| **Migration Map** | `docs/reference/documentation-migration-map.md` |

### Essential Commands

```bash
# List all KB documents
ls .augment/kb/TTA___*

# Search KB content
grep -r "pattern" .augment/kb/

# Count KB documents
find .augment/kb -name "TTA___*" -type f | wc -l

# Find document by partial name
find .augment/kb -name "*Agent*" -type f

# Open KB in Logseq
logseq ~/repos/TTA-notes
```

### Essential Logseq Shortcuts

| Action | Shortcut |
|--------|----------|
| **Search** | `Ctrl+K` / `Cmd+K` |
| **Graph View** | Click graph icon (top right) |
| **Create Page** | `[[New Page Name]]` |
| **Go Back** | `Alt+Left` / `Cmd+[` |
| **Go Forward** | `Alt+Right` / `Cmd+]` |
| **Toggle Sidebar** | `Ctrl+Shift+E` / `Cmd+Shift+E` |

---

## Related Documentation

- [Documentation Migration Map](./documentation-migration-map.md) - Old to new path mappings
- [Documentation Migration Audit](../../DOCUMENTATION_MIGRATION_AUDIT_2025-11-02.md) - Comprehensive audit report
- [Spec Review Audit](../../SPEC_REVIEW_AUDIT_2025-11-02.md) - Specification quality analysis
- [TTA-NOTES-INTEGRATION.md](../../.augment/TTA-NOTES-INTEGRATION.md) - Migration technical details

---

## Support

**Questions?**
- Check the [Migration Map](./documentation-migration-map.md)
- Search KB: `grep -r "your question" .augment/kb/`
- Ask in project chat with context about which doc you're looking for

**Found a broken link?**
- Update the link to point to KB path
- Check [Migration Audit](../../DOCUMENTATION_MIGRATION_AUDIT_2025-11-02.md) for correct path
- Submit PR with fix

**Migration issues?**
- See [TTA-NOTES-INTEGRATION.md](../../.augment/TTA-NOTES-INTEGRATION.md)
- Check if document should be in KB or original location
- Consult [Spec Review Audit](../../SPEC_REVIEW_AUDIT_2025-11-02.md) for guidance

---

**Last Updated:** November 2, 2025
**Maintainer:** TTA Development Team
**Version:** 1.0


---
**Logseq:** [[TTA.dev/Docs/Reference/Kb-access-guide]]
