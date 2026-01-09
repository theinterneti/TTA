# recovered-tta-storytelling Bloat Analysis

**Date:** 2026-01-09
**Total Size:** 24GB (!)
**Status:** 🔴 CRITICAL - 90% of all repository disk usage

---

## 🔥 Critical Findings

### Size Breakdown
| Item | Size | Should Be | Problem |
|------|------|-----------|---------|
| **venv-staging/** | 7.6GB | 0 (ignored) | ❌ Virtual env in git |
| **.venv/** | 8.3GB | 0 (ignored) | ❌ Virtual env in git |
| **list/** | 805MB | 0 (ignored) | ❌ Virtual env (Python libs) |
| **node_modules/** | 410MB | 0 (ignored) | ✓ Properly ignored |
| **test-results-staging/** | 95MB | 0 (ignored) | ❌ Test artifacts in git |
| **playwright-staging-report/** | 79MB | 0 (ignored) | ❌ Test reports in git |
| **htmlcov/** | 41M | 0 (ignored) | ❌ Coverage reports in git |
| **src/** | 1.2GB | ~50MB | ⚠️ Likely contains bloat |
| **Git objects** | 183MB | Normal | ✓ OK |
| **Other** | 5.4GB | ~500MB | ⚠️ Unknown |

**Total Removable:** ~17-18GB (71-75% reduction)

---

## 🎯 Root Cause

### The Problem
Despite having `.gitignore` rules for `venv/` and `.venv/`, the repository contains:

1. **Two virtual environments tracked by git:**
   - `venv-staging/` (7.6GB)
   - `.venv/` (8.3GB) - Has some files in git history
   - `list/` (805MB) - Another venv with different name

2. **Test artifacts committed:**
   - `test-results-staging/` (95MB)
   - `playwright-staging-report/` (79MB)
   - `htmlcov/` (41MB)

3. **Duplicate structure:**
   - Both `platform/` and `platform_tta_dev/` exist
   - Suggests incomplete migration/cleanup

### Why This Happened
- `.gitignore` added AFTER files were committed
- Virtual environments created with non-standard names
- Test artifacts not properly ignored
- Repository "got completely unmanageable" (as noted)

---

## 📊 Comparison with TTA.dev

| Metric | recovered-tta-storytelling | TTA.dev | Difference |
|--------|---------------------------|---------|------------|
| **Total Size** | 24GB | 2.0GB | **12x larger** |
| **Virtual Envs** | 16.7GB (2 venvs) | 0 | ∞ |
| **Test Artifacts** | 215MB | 0 | ∞ |
| **Platform Code** | Duplicated | Clean | - |
| **Git Objects** | 183MB | ~200MB | Similar |

### What TTA.dev Has That This Doesn't
- Clean separation of concerns
- No virtual environments in repo
- No test artifacts committed
- Single platform/ directory
- Optimized documentation
- Clean archive (576KB vs 12MB here)

---

## 🔧 Cleanup Strategy

### Phase 1: Remove Virtual Environments (16.7GB)
```bash
# These should NEVER be in a git repo
rm -rf venv-staging/      # 7.6GB
rm -rf .venv/             # 8.3GB
rm -rf list/              # 805MB (another venv)
```

### Phase 2: Remove Test Artifacts (215MB)
```bash
rm -rf test-results-staging/
rm -rf playwright-staging-report/
rm -rf htmlcov/
rm -rf .pytest_cache/
```

### Phase 3: Clean Git History
```bash
# Remove from git history (BFG Repo Cleaner recommended)
git filter-repo --path venv-staging --invert-paths
git filter-repo --path .venv --invert-paths
git filter-repo --path list --invert-paths
git filter-repo --path test-results-staging --invert-paths
git filter-repo --path playwright-staging-report --invert-paths
```

### Phase 4: Consolidate Duplicates
```bash
# Investigate and merge
# - platform/ vs platform_tta_dev/
# - What's already in TTA.dev?
```

### Phase 5: Update .gitignore
```bash
# Ensure these patterns exist:
venv*/
.venv*/
list/
**/node_modules/
**/__pycache__/
*.pyc
*.pyo
test-results*/
playwright-report*/
htmlcov/
.coverage
.pytest_cache/
```

---

## 📋 Detailed Action Plan

### Pre-Flight
```bash
# 1. Create backup
cd ~/repos
tar -czf recovered-tta-storytelling-backup-$(date +%Y%m%d).tar.gz recovered-tta-storytelling/

# 2. Check what's actually needed
cd recovered-tta-storytelling
git log --oneline | head -20  # Recent activity?
git diff main..refactor/repo-reorg  # What's being refactored?
```

### Execute Cleanup
```bash
cd ~/repos/recovered-tta-storytelling

# Phase 1: Remove local bloat
echo "Removing virtual environments..."
rm -rf venv-staging/ .venv/ list/

echo "Removing test artifacts..."
rm -rf test-results-staging/ playwright-staging-report/ htmlcov/
rm -rf .pytest_cache/ node_modules/

# Check size
du -sh .
# Expected: 24GB → ~6GB (75% reduction)

# Phase 2: Commit removal
git add -A
git commit -m "cleanup: Remove virtual environments and test artifacts

Removed:
- venv-staging/ (7.6GB)
- .venv/ (8.3GB)
- list/ (805MB)
- test-results-staging/ (95MB)
- playwright-staging-report/ (79MB)
- htmlcov/ (41MB)
- node_modules/ (410MB)

Total: ~17GB removed

These should never have been committed. Updated .gitignore to prevent recurrence.
"

# Phase 3: Clean git history (DESTRUCTIVE - needs backup first)
# Install git-filter-repo if not available
pip install git-filter-repo

# Remove from history
git filter-repo --path venv-staging --invert-paths
git filter-repo --path .venv --invert-paths
git filter-repo --path list --invert-paths
git filter-repo --path test-results-staging --invert-paths
git filter-repo --path playwright-staging-report --invert-paths
git filter-repo --path htmlcov --invert-paths

# Force push (if needed)
git push origin --force --all
git push origin --force --tags

# Clean up
git gc --aggressive --prune=now
```

---

## 🎯 Expected Results

| Phase | Size Before | Size After | Reduction |
|-------|-------------|------------|-----------|
| Initial | 24GB | 24GB | - |
| Remove local files | 24GB | ~6GB | 18GB (75%) |
| Clean git history | ~6GB | ~500MB-1GB | 5-5.5GB (83-92%) |
| **Final** | **24GB** | **~500MB-1GB** | **~23GB (95%)** |

---

## ⚠️ Risks & Mitigations

### High Risk
1. **Data Loss** - Virtual envs might contain custom modifications
   - **Mitigation:** Full backup before cleanup
   - **Check:** Review any custom scripts in venv/bin

2. **Git History Rewrite** - Changes all commit SHAs
   - **Mitigation:** Coordinate with any collaborators
   - **Backup:** Keep original backup indefinitely

### Medium Risk
3. **Missing Dependencies** - Some might be undocumented
   - **Mitigation:** Extract requirements.txt first
   - **Document:** All Python and Node dependencies

### Low Risk  
4. **Branch Divergence** - refactor/repo-reorg branch might have changes
   - **Mitigation:** Review diff first
   - **Merge:** Cherry-pick useful changes

---

## 📝 Comparison with TTA.dev

### What to Keep vs What TTA.dev Already Has

**Already in TTA.dev:**
- `platform/` - Core TTA platform code
- `docs/` - Documentation
- `tests/` - Test suites

**Unique to recovered-tta-storytelling:**
- `src/` (1.2GB) - Application code (storytelling features?)
- `_archive/` (12MB) - Historical records
- `nginx/` (27MB) - Web server config
- `site/` (25MB) - Built documentation

**Should Extract:**
- Any unique storytelling/narrative features
- Documentation not in TTA.dev
- Configuration examples
- Historical decisions (from _archive)

**Should Delete:**
- Everything else (bloat, duplicates, build artifacts)

---

## 🚀 Recommended Approach

Given that TTA.dev is the current working version:

### Option A: Archive Completely
```bash
# If nothing unique is needed
cd ~/repos
mv recovered-tta-storytelling recovered-tta-storytelling.OLD
tar -czf recovered-tta-storytelling-ARCHIVED-$(date +%Y%m%d).tar.gz recovered-tta-storytelling.OLD
rm -rf recovered-tta-storytelling.OLD
```

### Option B: Extract Unique Content
```bash
# 1. Clean up bloat first (get to ~1GB)
# 2. Compare src/ with TTA.dev
# 3. Extract any unique features to TTA.dev
# 4. Archive the cleaned version
```

### Option C: Hybrid (RECOMMENDED)
```bash
# 1. Create full backup
# 2. Remove bloat (24GB → ~1GB)
# 3. Compare with TTA.dev, extract uniquely valuable content
# 4. Archive as reference
# 5. Delete or keep minimal (~1GB) for historical reference
```

---

## ✅ Success Criteria

- [ ] Repository size < 1GB
- [ ] No virtual environments in repo
- [ ] No test artifacts in repo  
- [ ] No duplicate platform/ directories
- [ ] Clean git history (no venv commits)
- [ ] Backup created and verified
- [ ] Unique content extracted to TTA.dev (if any)
- [ ] .gitignore updated to prevent recurrence

---

**Generated:** 2026-01-09
**Priority:** 🔴 CRITICAL
**Estimated Time:** 2-3 hours
**Potential Savings:** ~23GB (95% reduction)
