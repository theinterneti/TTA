# Repository Cleanup Plan

**Date:** 2025-11-02
**Status:** 🔄 IN PROGRESS
**Goal:** Organize 184 markdown files, 98 logs/JSON files, and reduce root directory clutter

---

## Executive Summary

The TTA repository root contains **282+ files** that need organization. This plan consolidates status reports, archives historical documents, and establishes clear documentation hierarchy.

### Current State
- **184 Markdown files** in root directory
- **98 Log/JSON files** in root directory
- Multiple overlapping status reports
- Difficult to find current vs. historical information

### Target State
- **< 10 essential files** in root (README, CHANGELOG, core docs)
- **Archived historical reports** by category and date
- **Clear documentation hierarchy** in `docs/`
- **Logs consolidated** to `logs/` directory

---

## Phase 1: Quick Wins (30 minutes)

### 1.1 Archive Old Logs (10 min)
Move execution logs older than 30 days to archive:

```bash
# Create archive structure
mkdir -p .archive/logs/{2025-10,2025-09,older}

# Move logs by date pattern
mv *_execution.log .archive/logs/2025-10/
mv phase*_*.log .archive/logs/2025-10/
mv test_*.log .archive/logs/2025-10/
mv validation_*.log .archive/logs/2025-10/
```

**Files to Archive (48 logs):**
- `batch*_execution.log` (12 files)
- `phase*_*.log` (15 files)
- `test_*.log` (8 files)
- `validation_*.log` (5 files)
- `workflow_*.log` (3 files)
- Other execution logs (5 files)

### 1.2 Consolidate Test Results (10 min)
Move JSON test results to proper locations:

```bash
# Create test results archive
mkdir -p .archive/test-results/2025-10

# Move test result JSON files
mv *_test_results.json .archive/test-results/2025-10/
mv *_results.json .archive/test-results/2025-10/
mv test_*.json .archive/test-results/2025-10/
```

**Files to Archive (30 JSON files):**
- Model test results (8 files)
- Phase test results (6 files)
- Coverage reports (5 files)
- Integration results (11 files)

### 1.3 Clean Up Temporary Files (5 min)
Remove or archive temporary/duplicate files:

```bash
# Archive backups
mv *.backup .archive/backups/
mv *.backup2 .archive/backups/

# Archive numbered directories
mv 400/ .archive/http-codes/
mv 500/ .archive/http-codes/
mv =0.2.0/ .archive/versions/
mv =0.3.0/ .archive/versions/

# Remove empty "result" file
rm result
```

### 1.4 Organize Docker/Config Files (5 min)
Move docker-compose variants to docker directory:

```bash
# Already have docker/ directory
mv docker-compose*.yml docker/compose/
```

---

## Phase 2: Status Report Consolidation (1 hour)

### 2.1 Current vs Historical Status (20 min)

**Keep in Root (Current/Active):**
1. `README.md` - Project overview
2. `CHANGELOG.md` - Version history
3. `CONTRIBUTING.md` - Contributor guide
4. `SECURITY.md` - Security policy
5. `CURRENT_STATUS.md` - Latest sprint status
6. `TODO-AUDIT-QUICK-REF.md` - Active TODO reference

**Move to `docs/status/` (Active Status Dashboards):**
7. `ACCURATE_P0_COMPONENT_STATUS.md` → `docs/status/p0-components.md`
8. `DEPLOYMENT_STATUS.md` → `docs/status/deployment.md`
9. `TESTING_GUIDE.md` → `docs/guides/testing.md`

**Archive to `.archive/status-reports/2025-10/`:**
- All `PHASE*_*.md` files (38 files)
- All `*_COMPLETE.md` files (22 files)
- All `*_SUMMARY.md` files (31 files)
- All `*_REPORT.md` files (18 files)

### 2.2 Group by Category

#### CI/CD Reports → `.archive/cicd/`
- `CI_CD_*.md` (7 files)
- `CICD_*.md` (1 file)
- `WORKFLOW_*.md` (6 files)
- `PR_*.md` (5 files)

#### Testing Reports → `.archive/testing/`
- `E2E_*.md` (3 files)
- `TEST_*.md` (5 files)
- `TESTING_*.md` (2 files)
- `TIER_*.md` (2 files)
- `VALIDATION_*.md` (3 files)

#### Database Setup → `.archive/database/`
- `DATABASE_*.md` (4 files)
- `NEO4J_*.md` (5 files)
- `REDIS_*.md` (if any)

#### Docker/Infrastructure → `.archive/infrastructure/`
- `DOCKER_*.md` (8 files)
- `DEPLOYMENT_*.md` (3 files)
- `INFRASTRUCTURE_*.md` (1 file)

#### Observability → `.archive/observability/`
- `OBSERVABILITY_*.md` (11 files)
- `MONITORING_*.md` (if any)

#### OpenHands/Keploy → `.archive/tooling/`
- `OPENHANDS_*.md` (9 files)
- `KEPLOY_*.md` (6 files)

#### Component Development → `.archive/components/`
- `COMPONENT_*.md` (4 files)
- `CARBON_*.md` (1 file)
- `NARRATIVE_*.md` (1 file)
- `CHARACTER_*.md` (1 file)

#### Package Development → `.archive/packages/`
- `*_PACKAGE.md` (3 files)
- `APM_*.md` (1 file)
- `AI_DEV_TOOLKIT_*.md` (1 file)

---

## Phase 3: Documentation Hierarchy (45 minutes)

### 3.1 Establish `docs/` Structure

```
docs/
├── guides/           # How-to guides
│   ├── testing.md
│   ├── deployment.md
│   ├── docker-setup.md
│   └── database-setup.md
├── status/           # Current status dashboards
│   ├── p0-components.md
│   ├── deployment.md
│   └── test-coverage.md
├── architecture/     # System design docs
│   ├── agent-orchestration.md
│   ├── database-schema.md
│   └── observability.md
├── setup/            # Environment setup
│   ├── local-dev.md
│   ├── wsl2.md
│   └── mcp-servers.md
└── reference/        # API references
    ├── agents.md     (link to KB)
    ├── api/
    └── database/
```

### 3.2 Create Guide Documents

**Keep and Relocate:**
1. `TESTING_GUIDE.md` → `docs/guides/testing.md`
2. `DOCKER_QUICK_START.md` → `docs/guides/docker-setup.md`
3. `DATABASE_QUICK_REF.md` → `docs/guides/database-setup.md`
4. `ADVANCED_TESTING_GETTING_STARTED.md` → `docs/guides/advanced-testing.md`

**Create Quick Start Guide:**
- `docs/guides/quick-start.md` (consolidate setup docs)

### 3.3 Create Reference Links

Since documentation has moved to Logseq KB, create reference documents:

```markdown
# docs/reference/agents.md
# Agent Documentation

> 📚 **This documentation lives in the TTA Knowledge Base**
>
> **Location:** `.augment/kb/TTA___References___Agents Document.md`
> **Logseq:** `~/repos/TTA-notes/logseq/pages/TTA/`
>
> See [AGENTS.md](../../AGENTS.md) for access instructions.
```

---

## Phase 4: Archive Structure (30 minutes)

### 4.1 Create Archive Directories

```bash
mkdir -p .archive/{
  status-reports/2025-{10,09,08},
  cicd/2025-10,
  testing/2025-10,
  database/2025-10,
  infrastructure/2025-10,
  observability/2025-10,
  tooling/2025-10,
  components/2025-10,
  packages/2025-10,
  logs/2025-{10,09},
  test-results/2025-10,
  backups,
  versions,
  http-codes
}
```

### 4.2 Preserve Archive Context

Create `.archive/README.md`:

```markdown
# TTA Archive

Historical reports, logs, and documentation organized by category and date.

## Structure

- `status-reports/` - Phase completion reports, summaries
- `cicd/` - CI/CD setup and workflow reports
- `testing/` - Test execution and validation reports
- `database/` - Database setup and migration docs
- `infrastructure/` - Docker, deployment, infrastructure
- `observability/` - Monitoring and observability setup
- `tooling/` - OpenHands, Keploy, tool integration
- `components/` - Component development reports
- `packages/` - Package extraction and setup
- `logs/` - Execution logs by date
- `test-results/` - Test result JSON files
- `backups/` - Configuration backups

## Retention Policy

- Logs: Keep last 90 days
- Status Reports: Keep all (historical record)
- Test Results: Keep last 60 days
```

---

## Phase 5: Automation (1 hour)

### 5.1 Create Cleanup Script

`scripts/cleanup/organize-repo.sh`:

```bash
#!/bin/bash
# Organize TTA repository structure

set -e

ARCHIVE_DIR=".archive"
DOCS_DIR="docs"
ROOT_DIR="."

# Archive old logs
archive_logs() {
    echo "📦 Archiving logs..."
    find . -maxdepth 1 -name "*.log" -mtime +30 -exec mv {} "$ARCHIVE_DIR/logs/older/" \;
}

# Archive test results
archive_test_results() {
    echo "📊 Archiving test results..."
    find . -maxdepth 1 -name "*_results.json" -mtime +30 -exec mv {} "$ARCHIVE_DIR/test-results/older/" \;
}

# Clean temporary files
clean_temp() {
    echo "🧹 Cleaning temporary files..."
    rm -f result
    find . -maxdepth 1 -name "*.pyc" -delete
    find . -maxdepth 1 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
}

# Main execution
main() {
    echo "🚀 Starting repository cleanup..."

    archive_logs
    archive_test_results
    clean_temp

    echo "✅ Cleanup complete!"
}

main "$@"
```

### 5.2 Add Pre-Commit Hook

`.git/hooks/pre-commit` (or use pre-commit framework):

```bash
#!/bin/bash
# Warn if adding files to root that should be elsewhere

ROOT_FILES=$(git diff --cached --name-only --diff-filter=A | grep -E "^[^/]+\.(md|log|json)$" || true)

if [ -n "$ROOT_FILES" ]; then
    echo "⚠️  Warning: Adding files to repository root:"
    echo "$ROOT_FILES"
    echo ""
    echo "Consider placing in:"
    echo "  - docs/ for documentation"
    echo "  - .archive/ for historical reports"
    echo "  - logs/ for log files"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

---

## Implementation Timeline

### Immediate (Today)
- ✅ Create this cleanup plan
- ⏳ Execute Phase 1 (Quick Wins - 30 min)
- ⏳ Create archive structure

### This Week
- ⏳ Execute Phase 2 (Status Report Consolidation)
- ⏳ Execute Phase 3 (Documentation Hierarchy)
- ⏳ Update README with new structure

### Ongoing
- ⏳ Implement cleanup automation (Phase 5)
- ⏳ Establish retention policies
- ⏳ Update contributor guidelines

---

## Success Metrics

### Before
- **282+ files** in root directory
- **No clear organization** by category
- **Duplicate information** across multiple files
- **Hard to find** current vs. historical docs

### After
- **< 10 essential files** in root
- **Clear hierarchy** in `docs/` and `.archive/`
- **Single source of truth** for current status
- **Easy navigation** with guides and references

### Tracking
- [ ] Root directory files reduced by 90%
- [ ] All historical reports archived
- [ ] Documentation hierarchy established
- [ ] Cleanup automation implemented
- [ ] README updated with new structure

---

## Rollback Plan

All moves are non-destructive:
1. Archive contains all original files
2. Git history preserves all versions
3. Rollback: `git checkout HEAD -- <file>`
4. Bulk restore: `cp -r .archive/* .`

---

## Next Actions

1. **Review this plan** with team
2. **Execute Phase 1** (Quick Wins)
3. **Test archive structure** before bulk moves
4. **Update README** with new organization
5. **Document new contribution workflow**

**Estimated Total Time:** 3-4 hours
**Priority:** MEDIUM (improves maintainability)
**Risk:** LOW (non-destructive, git-tracked)
