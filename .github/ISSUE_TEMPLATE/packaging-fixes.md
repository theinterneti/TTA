---
name: Packaging Configuration Fixes
about: Fix critical packaging issues in TTA repository
title: '[PACKAGING] Fix workspace configuration and Python version standardization'
labels: bug, packaging, critical
assignees: ''
---

## Overview

Fix critical packaging configuration issues in the TTA repository that are blocking proper dependency resolution and workspace management.

## Issues Identified

### 1. Incomplete Workspace Configuration
**Problem:** Only 2 of 4 packages are included in workspace members
```toml
# Current (INCOMPLETE)
[tool.uv.workspace]
members = [
    "packages/tta-ai-framework",
    "packages/tta-narrative-engine",
]

# Missing:
# - packages/ai-dev-toolkit
# - packages/universal-agent-context
```

**Impact:**
- Missing packages not managed by workspace
- Dependency resolution issues
- Inconsistent build behavior

### 2. Python Version Inconsistency
**Problem:** Root project requires Python 3.10+, but packages require 3.12+
```toml
# Root pyproject.toml
requires-python = ">=3.10"

# Package pyproject.toml files
requires-python = ">=3.12"
```

**Impact:**
- Compatibility confusion
- Potential runtime errors
- CI/CD failures

### 3. Missing Version Constraints
**Problem:** Workspace packages use floating versions
```toml
# Current (NO VERSION PINNING)
[tool.uv.sources]
tta-ai-framework = { workspace = true }
tta-narrative-engine = { workspace = true }

# Should pin versions for stability
```

**Impact:**
- Unpredictable builds
- Dependency conflicts
- Difficult to reproduce issues

## Acceptance Criteria

### Workspace Configuration
- [ ] All 4 packages added to workspace members
- [ ] `uv sync --all-extras` runs without errors
- [ ] All workspace packages resolve correctly
- [ ] No dependency conflicts

### Python Version
- [ ] Root pyproject.toml uses `requires-python = ">=3.12"`
- [ ] All package pyproject.toml files use `requires-python = ">=3.12"`
- [ ] Consistent across all configuration files
- [ ] CI/CD updated to use Python 3.12

### Version Constraints
- [ ] Workspace package versions pinned in root dependencies
- [ ] External dependencies have version constraints
- [ ] Lock file (uv.lock) updated and committed
- [ ] Documentation updated with version requirements

## Implementation Plan

### Task 1: Fix Workspace Configuration
```toml
# pyproject.toml

[tool.uv.workspace]
members = [
    "packages/tta-ai-framework",
    "packages/tta-narrative-engine",
    "packages/ai-dev-toolkit",           # ADD
    "packages/universal-agent-context",  # ADD
]
```

**Validation:**
```bash
uv sync --all-extras
uv run pytest --collect-only  # Verify all packages discovered
```

### Task 2: Standardize Python Version
```toml
# Root pyproject.toml
[project]
requires-python = ">=3.12"

# All package pyproject.toml files
[project]
requires-python = ">=3.12"
```

**Files to Update:**
- [ ] `pyproject.toml` (root)
- [ ] `packages/tta-ai-framework/pyproject.toml`
- [ ] `packages/tta-narrative-engine/pyproject.toml`
- [ ] `packages/ai-dev-toolkit/pyproject.toml`
- [ ] `packages/universal-agent-context/pyproject.toml`

**Validation:**
```bash
grep -r "requires-python" pyproject.toml packages/*/pyproject.toml
# All should show: requires-python = ">=3.12"
```

### Task 3: Add Version Constraints
```toml
# pyproject.toml

[project]
dependencies = [
    "tta-ai-framework==0.1.0",
    "tta-narrative-engine==0.1.0",
    # ... other dependencies with versions
]

[tool.uv.sources]
tta-ai-framework = { workspace = true }
tta-narrative-engine = { workspace = true }
```

**Validation:**
```bash
uv sync --all-extras
uv pip list  # Verify versions
```

### Task 4: Update CI/CD
```yaml
# .github/workflows/*.yml

- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'  # Update from 3.10
```

**Files to Update:**
- [ ] `.github/workflows/ci.yml`
- [ ] `.github/workflows/quality-check.yml`
- [ ] `.github/workflows/test.yml`
- [ ] Any other workflow files using Python

## Testing Plan

### Pre-Change Validation
```bash
# Document current state
uv sync --all-extras 2>&1 | tee pre-fix-sync.log
uv pip list > pre-fix-packages.txt
```

### Post-Change Validation
```bash
# Clean environment
rm -rf .venv uv.lock

# Fresh install
uv sync --all-extras

# Verify all packages
uv pip list

# Run tests
uv run pytest -v

# Run quality checks
uv run ruff check .
uv run ruff format --check .
uvx pyright src/ packages/
```

### Regression Testing
- [ ] All existing tests pass
- [ ] No new dependency conflicts
- [ ] Build time comparable or improved
- [ ] No breaking changes to APIs

## Rollback Plan

If issues arise:
```bash
# Restore from backup
git checkout HEAD~1 pyproject.toml
git checkout HEAD~1 packages/*/pyproject.toml

# Reinstall
rm -rf .venv uv.lock
uv sync --all-extras
```

## Success Metrics

- [ ] `uv sync --all-extras` completes successfully
- [ ] All 4 packages recognized in workspace
- [ ] Python 3.12 used consistently
- [ ] All tests pass
- [ ] CI/CD passes
- [ ] No dependency conflicts
- [ ] Lock file committed and up-to-date

## Dependencies

**Blocks:**
- #[ISSUE_NUMBER] Extract tta-agent-coordination package
- #[ISSUE_NUMBER] Publish packages to PyPI
- All future packaging work

## Related Documentation

- [Packaging Strategy Analysis](../docs/PACKAGING_STRATEGY.md)
- [TTA.dev Migration Strategy](../docs/TTA_DEV_MIGRATION_STRATEGY.md)
- [UV Workspace Documentation](https://docs.astral.sh/uv/concepts/workspaces/)

## Notes

- **Priority: CRITICAL** - Blocks all other packaging work
- Estimated time: 2-4 hours
- Low risk: Changes are configuration-only
- Should be completed before any package extraction work

