# TTA Documentation Migration Map

**Date:** November 2, 2025
**Status:** Active Reference
**Purpose:** Mapping table from old documentation paths to new Knowledge Base locations

---

## Overview

This document provides a comprehensive mapping of documentation that has been migrated from various locations to the centralized TTA Knowledge Base (`.augment/kb/`).

**Migration Date:** November 1, 2025
**Total Migrated Documents:** 306 files
**KB Format:** Triple-underscore naming (`TTA___Category___Title.md`)

---

## Core Project Documentation

| Old Path | New KB Path | Status |
|----------|-------------|--------|
| `AGENTS.md` | `.augment/kb/TTA___References___Agents Document.md` | ✅ Migrated |
| `CLAUDE.md` | `.augment/kb/TTA___References___Claude Document.md` | ✅ Migrated |
| `README.md` (content) | `.augment/kb/TTA___References___Overview Document.md` | ✅ Migrated |
| `GEMINI.md` | `GEMINI.md` | ⚠️ Not Migrated (active) |

**Notes:**
- `AGENTS.md`, `CLAUDE.md` now contain migration notices pointing to KB
- `GEMINI.md` remains in root for quick AI assistant access
- Root README.md still exists but major content consolidated to KB

---

## Specification Documents

### API Specifications

| Old Path | New KB Path | Status |
|----------|-------------|--------|
| `.github/specs/api-endpoint.spec.md` | `.augment/kb/TTA___Components___API Endpoint Specification Template.md` | ✅ Migrated |
| `.github/specs/therapeutic-feature.spec.md` | `.augment/kb/TTA___Components___Therapeutic Feature Specification Template.md` | ✅ Migrated |

**Notes:**
- Old `.github/specs/` files are now stubs with migration notices
- Backup files (`.backup`) remain for safety

### Component Specifications

| Old Path | New KB Path | Status |
|----------|-------------|--------|
| `docs/technical-specifications.md` | `.augment/kb/TTA___Components___TTA Technical Specifications.md` | ✅ Migrated |
| `docs/project/technical-specifications.md` | `.augment/kb/TTA___Components___TTA Technical Specifications.md` | ✅ Migrated (duplicate) |

### Spec Templates (Not Migrated)

| Path | Status | Reason |
|------|--------|--------|
| `specs/templates/component.spec.template.md` | ⚠️ Active | Used by CI/CD and workflows |
| `specs/templates/api.spec.template.md` | ⚠️ Active | Used by CI/CD and workflows |
| `specs/templates/feature.spec.template.md` | ⚠️ Active | Used by CI/CD and workflows |

**Notes:**
- Templates remain in `specs/templates/` for operational use
- Schema validation references these templates
- Do NOT migrate - actively used by scripts

---

## Architecture Documentation

| Old Path | New KB Path | Status |
|----------|-------------|--------|
| `docs/architecture/system-architecture-diagram.md` | `.augment/kb/TTA___Architecture___System Architecture Diagram.md` | ✅ Migrated |
| `docs/application/architecture.md` | `.augment/kb/TTA___Architecture___Application Architecture.md` | ✅ Migrated |
| `AI_AGENT_ORCHESTRATION.md` (content) | `.augment/kb/TTA___Architecture___Docs Architecture Agent Orchestration.md` | ✅ Migrated |

**Notes:**
- Architecture docs consolidated under `TTA___Architecture___` namespace
- Agent orchestration patterns documented in KB

---

## Status & Tracking Documentation

| Old Path | New KB Path | Status |
|----------|-------------|--------|
| `docs/status/component-maturity.md` | `.augment/kb/TTA___Status___Component Maturity Re-Analysis Results.md` | ✅ Migrated |
| `docs/project/component-maturity-assessment-*.md` | `.augment/kb/TTA___Status___Component Maturity Assessment.md` | ✅ Migrated |
| Project timeline (various) | `.augment/kb/TTA___Status___Project Timeline.md` | ✅ Migrated |
| Implementation status (various) | `.augment/kb/TTA___Status___Implementation Dashboard.md` | ✅ Migrated |

**Notes:**
- Status documents consolidated and updated in KB
- `component-maturity-analysis.json` remains in root (active data file)

---

## Development Documentation

### Not Migrated (Still Active)

| Path | Status | Reason |
|------|--------|--------|
| `docs/development/*.md` | ⚠️ Active | Working development guides |
| `.github/instructions/*.instructions.md` | ⚠️ Active | Used by Copilot and CI/CD |
| `.kiro/specs/**/*.md` | ⚠️ Active | 54 active specification files |
| `CONTRIBUTING.md` | ⚠️ Active | Essential onboarding doc |

**Notes:**
- Development docs remain in place - frequently updated during active work
- Instruction files must stay in `.github/instructions/` for Copilot integration
- `.kiro/specs/` is the primary specification repository (NOT migrated)

---

## API Documentation

| Old Path | New KB Path | Status |
|----------|-------------|--------|
| `src/player_experience/api/API_DOCUMENTATION.md` | `src/player_experience/api/API_DOCUMENTATION.md` | ⚠️ Not Migrated |
| `docs/project/API_VALIDATION_IMPROVEMENTS.md` | `docs/project/API_VALIDATION_IMPROVEMENTS.md` | ⚠️ Not Migrated |

**Notes:**
- API docs remain co-located with implementation code
- These are living documents that change with API implementation
- Consider KB migration after API stabilizes

---

## Context & Workflow Documentation

### Augment Directory

| Old Path | New KB Path | Status |
|----------|-------------|--------|
| `.augment/context/specs/context_management_spec.md` | `.augment/context/specs/context_management_spec.md` | ⚠️ Not Migrated |
| `.augment/chatmodes/*.chatmode.md` | `.augment/chatmodes/*.chatmode.md` | ⚠️ Not Migrated |
| `.augment/workflows/*.prompt.md` | `.augment/workflows/*.prompt.md` | ⚠️ Not Migrated |

**Notes:**
- Augment files remain for AI assistant functionality
- These are operational files, not documentation
- Do NOT migrate - part of AI workflow system

---

## Quick Lookup: Common Documents

### Frequently Accessed Docs

| Document | Current Location | Notes |
|----------|------------------|-------|
| **Agents Context** | `.augment/kb/TTA___References___Agents Document.md` | Migrated - use KB |
| **Claude Context** | `.augment/kb/TTA___References___Claude Document.md` | Migrated - use KB |
| **Technical Specs** | `.augment/kb/TTA___Components___TTA Technical Specifications.md` | Migrated - use KB |
| **API Endpoint Template** | `.augment/kb/TTA___Components___API Endpoint Specification Template.md` | Migrated - use KB |
| **Component Specs** | `.kiro/specs/` | NOT migrated - use original |
| **Instruction Files** | `.github/instructions/` | NOT migrated - use original |
| **Spec Templates** | `specs/templates/` | NOT migrated - use original |
| **Maturity Analysis** | `component-maturity-analysis.json` | NOT migrated - active data |

---

## Migration Status by Category

### ✅ Fully Migrated Categories

**These document types are in KB:**
- Core project documentation (AGENTS, CLAUDE, README content)
- API specification templates (`.github/specs/`)
- Technical specifications (`docs/technical-specifications.md`)
- Architecture documentation (`docs/architecture/`, `docs/application/`)
- Status tracking (`docs/status/`, project timelines)
- Component maturity reports

### ⚠️ Not Migrated (Intentionally)

**These document types remain in original locations:**
- Specification documents (`.kiro/specs/` - 54 files)
- Instruction files (`.github/instructions/` - 14 files)
- Specification templates (`specs/templates/` - 3 files)
- Development guides (`docs/development/`)
- API documentation (co-located with code)
- Context management files (`.augment/context/`)
- AI workflow files (`.augment/chatmodes/`, `.augment/workflows/`)
- Active data files (`*.json`, `*.yaml`)

### 🔄 Hybrid Status

**These documents have dual presence:**
- `AGENTS.md` - Stub in root, content in KB
- `CLAUDE.md` - Stub in root, content in KB
- `README.md` - Active in root, extended content in KB

---

## Search Strategies

### Finding a Document

**Strategy 1: Check this map**
1. Search this file for old path
2. Use new KB path from table

**Strategy 2: Grep search**
```bash
# Search for content in KB
grep -r "search term" .augment/kb/

# Find document by partial name
find .augment/kb -name "*partial_name*"
```

**Strategy 3: Logseq search**
1. Open Logseq → TTA graph
2. Press `Ctrl+K` (or `Cmd+K`)
3. Type document name or content

### Handling Broken Links

**If you find a broken link:**

1. **Check if document migrated:**
   - Look up old path in this map
   - Update link to new KB path

2. **Check if document NOT migrated:**
   - Verify document is in original location
   - Update link to correct original path

3. **Document missing entirely:**
   - Check if it was intentionally removed
   - Search git history: `git log --all --full-history -- path/to/file`
   - Consider if content was consolidated elsewhere

---

## Path Conversion Examples

### Example 1: Stub File Reference

**Old code:**
```markdown
See [API Endpoint Spec](.github/specs/api-endpoint.spec.md)
```

**New code:**
```markdown
See [API Endpoint Spec](.augment/kb/TTA___Components___API Endpoint Specification Template.md)
```

### Example 2: Technical Docs Reference

**Old code:**
```python
# For technical specs, see docs/technical-specifications.md
```

**New code:**
```python
# For technical specs, see .augment/kb/TTA___Components___TTA Technical Specifications.md
```

### Example 3: Architecture Reference

**Old code:**
```markdown
See [Architecture](docs/application/architecture.md) for system design.
```

**New code:**
```markdown
See [Architecture](.augment/kb/TTA___Architecture___Application Architecture.md) for system design.
```

### Example 4: Spec Template Reference (NO CHANGE)

**Correct code (unchanged):**
```python
# Template location: specs/templates/component.spec.template.md
```

**Do NOT change to:**
```python
# Template location: .augment/kb/... (WRONG)
```

**Why:** Spec templates are NOT migrated; they remain operational.

---

## Related Documentation

- [KB Access Guide](./kb-access-guide.md) - How to access and navigate the Knowledge Base
- [Documentation Migration Audit](../../DOCUMENTATION_MIGRATION_AUDIT_2025-11-02.md) - Comprehensive audit of migration
- [Spec Review Audit](../../SPEC_REVIEW_AUDIT_2025-11-02.md) - Specification quality analysis
- [TTA-NOTES-INTEGRATION.md](../../.augment/TTA-NOTES-INTEGRATION.md) - Technical migration details

---

## Maintenance

### When to Update This Map

**Add entries when:**
- New documents are migrated to KB
- Old stub files are created
- Document paths change in KB

**Review frequency:**
- After each major documentation migration
- Quarterly as part of documentation audit
- When broken links are discovered

### How to Update This Map

1. Identify migrated document
2. Add row to appropriate category table
3. Update migration status
4. Add notes if special considerations apply
5. Update "Last Updated" date below

---

**Last Updated:** November 2, 2025
**Maintainer:** TTA Development Team
**Version:** 1.0
**Next Review:** February 2026
