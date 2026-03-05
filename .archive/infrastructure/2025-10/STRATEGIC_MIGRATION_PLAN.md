# Strategic Branch Migration Plan

## Goal
Return to stable main, then move valuable dev infrastructure forward in organized PRs.

## Current State
- On `phase7-openhands-integration-results` with 14 commits ahead of main
- Contains mix of: cleanup, workflow primitives, TTA-specific work, experimental code
- Many local modifications (untracked/modified files)

## Strategy: Incremental Migration

### Phase 1: Clean Repository Organization (Priority 1) ✅
**What:** Just the cleanup - move docs, archive artifacts, organize structure
**Why:** Foundation for everything else, no dependencies
**Branch:** `feat/repository-organization`
**Files:**
- Repository structure changes
- .gitignore updates
- Cleanup script
- Documentation (REPOSITORY_RECOVERY_PLAN.md, etc.)

### Phase 2: Workflow Primitives Infrastructure (Priority 2)
**What:** Reusable AI workflow components (not TTA-specific)
**Why:** Core infrastructure for building AI workflows
**Branch:** `feat/workflow-primitives-v1`
**Files:**
- `packages/tta-workflow-primitives/` - Router, Cache, Timeout, etc.
- `packages/dev-primitives/` - Development utilities
- Agentic primitives documentation
- Examples and tests

**Benefits:**
- Reusable across projects
- Well-tested primitives
- Documented patterns
- Independent of TTA specifics

### Phase 3: Monitoring & Observability Stack (Priority 3)
**What:** Dev tools, monitoring, metrics
**Why:** Essential for development and debugging
**Branch:** `feat/monitoring-stack`
**Files:**
- `scripts/observability/` - Dashboard, metrics
- `scripts/maturity/` - Component maturity tracking
- `scripts/registry/` - Component registry
- Monitoring quickstart docs

### Phase 4: TTA-Specific Work (Priority 4)
**What:** TTA application code
**Why:** Depends on infrastructure above
**Branch:** `feat/tta-mvp-components` (review and clean up first)
**Files:**
- TTA-specific implementations
- MVP work
- Application code

## Execution Plan

### Step 1: Start Fresh from Main
```bash
# Stash all local changes
git stash push -m "WIP: Local modifications"

# Go to main
git checkout main
git pull TTA main

# Verify clean state
git status
```

### Step 2: Create Cleanup Branch
```bash
# Create branch from main
git checkout -b feat/repository-organization

# Manually apply cleanup changes (not cherry-pick)
# This avoids conflicts with local modifications
```

### Step 3: Create Each Infrastructure Branch
```bash
# After cleanup is merged, create workflow primitives branch
git checkout main
git pull TTA main
git checkout -b feat/workflow-primitives-v1

# Selectively add workflow primitive files
# Test, commit, push, PR
```

## File Classification

### Cleanup Only (Phase 1)
- scripts/cleanup_and_organize_repo.sh
- REPOSITORY_RECOVERY_PLAN.md
- CLEANUP_SUMMARY.md
- START_HERE.md
- Directory moves (docs/, .archive/, etc.)
- .gitignore updates

### Workflow Primitives (Phase 2)
- packages/tta-workflow-primitives/
- packages/dev-primitives/
- docs/agentic-primitives/
- examples/ (primitives demos)

### Monitoring (Phase 3)
- scripts/observability/
- scripts/maturity/
- scripts/registry/
- docs/guides/MONITORING_QUICKSTART.md

### TTA-Specific (Phase 4 - Review First)
- src/agent_orchestration/openhands_integration/ changes
- TTA MVP files
- Application-specific code

## Benefits of This Approach

1. **Incremental value delivery** - Each PR adds value independently
2. **Easy review** - Small, focused PRs
3. **Reduced risk** - Can test each piece separately
4. **Clear history** - Each feature has its own clean history
5. **Flexible** - Can prioritize what you need first

## Next Actions

1. Stash local changes
2. Start with Phase 1 (cleanup) from clean main
3. Create focused PR
4. After merge, move to Phase 2 (workflow primitives)

This gives you a clean path forward!


---
**Logseq:** [[TTA.dev/.archive/Infrastructure/2025-10/Strategic_migration_plan]]
