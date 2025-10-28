# Yamale-Based Agentic Primitives Validation - Implementation Summary

**Status**: ✅ Complete
**Date**: 2025-10-26
**Implementation**: Solution 1 from `AGENTIC_PRIMITIVES_CONSISTENCY.md`

## Overview

This document summarizes the implementation of Yamale-based schema validation for TTA's agentic primitives files. The validation ensures consistency and correctness of YAML frontmatter across all `.github/` directory files.

## What Was Implemented

### 1. Schema Files (`.github/schemas/`)

Created four schema files to validate different types of agentic primitives:

- **`instruction.schema.yaml`** - Validates `.github/instructions/*.instructions.md`
  - Required fields: `applyTo`, `priority`, `category`, `description`
  - Priority enum: `critical`, `high`, `medium`, `low`

- **`chatmode.schema.yaml`** - Validates `.github/chatmodes/*.chatmode.md`
  - Required fields: `mode`, `model`, `tools`, `description`
  - Tools structure: `allowed` (required list), `denied` (optional list)

- **`prompt.schema.yaml`** - Validates `.github/prompts/*.prompt.md`
  - Required fields: `mode`, `model`, `tools`, `description`
  - Mode enum: `agent`, `workflow`

- **`spec.schema.yaml`** - Validates `.github/specs/*.spec.md`
  - Required fields: `type`, `category`, `status`, `priority`, `created`, `updated`
  - Type enum: `feature`, `api`, `component`
  - Status enum: `draft`, `review`, `approved`, `implemented`
  - Priority enum: `critical`, `high`, `medium`, `low`

### 2. Validation Script (`scripts/validate-agentic-frontmatter.py`)

Created a comprehensive validation script with:

- **YAML Frontmatter Extraction**: Parses frontmatter from markdown files
- **Schema Validation**: Uses Yamale to validate against schemas
- **Clear Error Reporting**: Provides actionable error messages
- **Summary Statistics**: Shows pass/fail counts and overall status
- **Exit Codes**: Returns 0 for success, 1 for failure (CI/CD compatible)

**Features**:
- Validates all agentic primitive file types
- Handles missing frontmatter gracefully
- Provides helpful tips for fixing validation errors
- Supports both manual and automated execution

### 3. APM Integration (`apm.yml`)

Added two new scripts to the Agent Package Manager configuration:

```yaml
validate:primitives: "python scripts/validate-agentic-frontmatter.py"
validate:all: "bash scripts/validate-agentic-primitives.sh && python scripts/validate-agentic-frontmatter.py"
```

**Usage** (when Agent CLI Runtime is available):
```bash
copilot run validate:primitives
copilot run validate:all
```

### 4. Pre-Commit Integration (`.pre-commit-config.yaml`)

Added a new pre-commit hook that:
- Runs automatically before commits
- Only triggers when `.github/` files are modified
- Validates all agentic primitives in one pass
- Blocks commits if validation fails

**Hook Configuration**:
```yaml
- id: validate-agentic-frontmatter
  name: Validate agentic primitives frontmatter
  entry: python scripts/validate-agentic-frontmatter.py
  language: system
  files: ^\.github/(instructions|chatmodes|prompts|specs)/.*\.md$
  pass_filenames: false
```

### 5. Quality Gates Integration (`scripts/validate-quality-gates.sh`)

Added validation to the `code-quality` gate:
- Runs as part of the standard quality gate workflow
- Integrated with existing linting, formatting, and type checking
- Fails the quality gate if validation fails
- Provides clear pass/fail status in gate summary

### 6. Documentation Updates

**`CONTRIBUTING.md`**:
- Added new section: "🤖 Agentic Primitives Validation"
- Documented what gets validated
- Provided validation commands
- Listed common validation errors and fixes
- Referenced detailed documentation

**`docs/development/AGENTIC_PRIMITIVES_CONSISTENCY.md`**:
- Comprehensive research and solution analysis
- Implementation steps for all 4 solutions
- Schema examples and validation script templates
- Integration guides for pre-commit and quality gates

## Testing Results

### Initial Test Run

```
🔍 Validating Agentic Primitives Frontmatter...

📄 Validating 3 file(s) with instruction.schema.yaml:
  ✅ graph-db.instructions.md
  ✅ safety.instructions.md
  ✅ testing-battery.instructions.md

📄 Validating 2 file(s) with chatmode.schema.yaml:
  ✅ backend-implementer.chatmode.md
  ✅ safety-architect.chatmode.md

📄 Validating 1 file(s) with prompt.schema.yaml:
  ✅ narrative-creation.prompt.md

📄 Validating 2 file(s) with spec.schema.yaml:
  ✅ api-endpoint.spec.md
  ✅ therapeutic-feature.spec.md

============================================================
📊 Validation Summary: 8/8 files passed
============================================================
✅ All agentic primitives frontmatter validation passed!
```

### Pre-Commit Hook Test

```bash
$ git add .github/specs/api-endpoint.spec.md .pre-commit-config.yaml
$ pre-commit run validate-agentic-frontmatter
Validate agentic primitives frontmatter..................................Passed
```

## Usage

### Manual Validation

```bash
# Validate all agentic primitives
python scripts/validate-agentic-frontmatter.py

# Or use APM (when available)
copilot run validate:primitives
```

### Automatic Validation

**Pre-Commit Hook** (runs automatically):
```bash
git add .github/instructions/my-file.instructions.md
git commit -m "feat: add new instruction file"
# Validation runs automatically before commit
```

**Quality Gates** (runs in CI/CD):
```bash
bash scripts/validate-quality-gates.sh code-quality
# Includes agentic primitives validation
```

## Common Validation Errors

### 1. Missing Required Field

**Error**:
```
❌ safety.instructions.md: Required field 'priority' not found
```

**Fix**: Add the missing field to the YAML frontmatter:
```yaml
---
applyTo: ["**/*.py"]
priority: high  # Add this line
category: safety
description: Safety and security standards
---
```

### 2. Invalid Enum Value

**Error**:
```
❌ chatmode.md: mode: 'invalid' is not a valid enum value
```

**Fix**: Use one of the allowed values from the schema:
```yaml
---
mode: agent  # Must be 'agent' or 'workflow'
model: claude-sonnet-4.5
tools:
  allowed: [fetch, search]
description: Example chat mode
---
```

### 3. Invalid YAML Syntax

**Error**:
```
❌ No valid YAML frontmatter found in file.md
```

**Fix**: Ensure frontmatter starts and ends with `---`:
```yaml
---
type: feature
category: therapeutic
status: draft
priority: high
created: "2025-10-26"
updated: "2025-10-26"
---

# Your content here
```

### 4. Date Format Issues

**Error**:
```
❌ spec.md: created: '2025-10-26' is not a str.
```

**Fix**: Quote date strings in YAML:
```yaml
---
created: "2025-10-26"  # Quoted
updated: "2025-10-26"  # Quoted
---
```

## Benefits

### 1. Consistency
- All agentic primitives follow the same structure
- Required fields are enforced
- Enum values are validated

### 2. Early Error Detection
- Validation runs before commit (pre-commit hook)
- Validation runs in CI/CD (quality gates)
- Clear error messages guide developers

### 3. Maintainability
- Schemas are declarative and easy to update
- Validation logic is centralized
- Documentation is synchronized

### 4. Developer Experience
- Fast validation (runs in seconds)
- Actionable error messages
- Integrated with existing workflows

## Future Enhancements

### Phase 2: Cross-File Validation (Optional)

If needed, implement Solution 3 from `AGENTIC_PRIMITIVES_CONSISTENCY.md`:
- Validate MCP servers in `apm.yml` are documented in `AGENTS.md`
- Check instruction `applyTo` patterns reference existing files
- Verify chat mode `tools` reference valid tool names

**Implementation**: `scripts/validate-agentic-cross-references.py`

### Phase 3: Automated Synchronization (Optional)

If cross-file consistency becomes a burden:
- Auto-generate sections of `AGENTS.md` from `apm.yml`
- Auto-update related files when one file changes
- Provide "sync" command to propagate changes

**Implementation**: `scripts/sync-agentic-primitives.py`

## Related Documentation

- **`docs/development/AGENTIC_PRIMITIVES_CONSISTENCY.md`** - Research and solution analysis
- **`CONTRIBUTING.md`** - Developer guide for agentic primitives
- **`apm.yml`** - Agent Package Manager configuration
- **`.github/schemas/`** - Validation schema files

---

**Status**: ✅ Complete
**Last Updated**: 2025-10-26
**Implemented By**: Augment Agent
**Validated**: All 8 agentic primitive files passing
