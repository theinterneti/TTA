# 🚨 Repository Recovery & Organization Plan

**Date:** 2025-10-26
**Status:** Ready to Execute
**Your Branch:** phase7-openhands-integration-results

---

## 📊 Current Problems Identified

### 🔴 Critical Issues

1. **Root Directory Chaos**: 220 files in root (should be <30)
   - 66 markdown documentation files
   - 74 test/log artifacts
   - 3 backup directories

2. **Branch Instability**:
   - 14 commits ahead of main
   - 22 untracked files with untested code
   - On experimental feature branch, not main

3. **Workflow Failures**: 90% failure rate
   - 18 failed workflows
   - 2 successful workflows
   - Most failing on your current branch

4. **Directory Bloat**:
   - 40MB htmlcov (test coverage)
   - 5.9MB artifacts
   - Multiple unnecessary backups

---

## 🎯 Recovery Strategy (4 Phases)

### Phase 1: Emergency Stabilization ✅ READY
**Goal:** Get to a stable state without losing work
**Time:** 10 minutes
**Risk:** Low (creates backups first)

**Actions:**
1. ✅ Create safety backup branch (automated)
2. ✅ Organize root directory (script ready)
3. ✅ Update .gitignore (automated)
4. ✅ Commit organized structure

**Script:** `./scripts/cleanup_and_organize_repo.sh --execute`

---

### Phase 2: Branch Hygiene 🔄 NEXT
**Goal:** Separate experimental work from stable code
**Time:** 15 minutes
**Risk:** Low (uses git, reversible)

**Problem:** You're on `phase7-openhands-integration-results` which is:
- 14 commits ahead of main
- Contains experimental work
- Has failing workflows

**Solution Options:**

#### Option A: Archive Experimental Work (Recommended)
```bash
# 1. Commit current cleanup
git add -A
git commit -m "chore: organize repository structure

- Move 66 docs to docs/
- Archive 74 test artifacts
- Organize scripts
- Clean root directory"

# 2. Tag this as experimental work
git tag experimental-phase7-work

# 3. Return to stable main
git checkout main

# 4. Create fresh feature branch for real work
git checkout -b feat/repository-organization

# 5. Cherry-pick just the cleanup
git cherry-pick <cleanup-commit-sha>
```

**Why this works:**
- Preserves ALL your experimental work (tagged)
- Starts fresh from stable main
- Can review experimental commits later
- Workflows will work on main

#### Option B: Clean Up Current Branch
```bash
# 1. Commit cleanup
git add -A
git commit -m "chore: organize repository structure"

# 2. Interactive rebase to clean up history
git rebase -i main

# 3. Keep only commits that:
   - Are tested
   - Pass workflows
   - Are documented

# 4. Create PR to merge to main
```

**Why this might be harder:**
- Need to review all 14 commits
- Some may have workflow failures
- Risky if commits are interdependent

---

### Phase 3: Workflow Recovery 🔧 AFTER
**Goal:** Get workflows passing
**Time:** 30 minutes
**Risk:** Low (can test on branch first)

**Current Workflow Status:**
```
✗ Performance Regression Tracking - FAILING
✗ Security Scan - FAILING
✗ TTA Simulation Framework - FAILING
✗ Comprehensive Test Battery - FAILING
✗ E2E Tests - FAILING
✗ Post-deployment Tests - FAILING
```

**Root Causes (likely):**
1. Broken imports from file moves
2. Missing dependencies in experimental code
3. Environment issues
4. Test configuration problems

**Fix Strategy:**
```bash
# 1. Check workflow logs
gh run list --limit 5
gh run view <run-id> --log-failed

# 2. Run tests locally first
make test

# 3. Fix issues one by one
# 4. Commit fixes
# 5. Push and verify workflows pass
```

---

### Phase 4: Prevent Future Issues 🛡️ ONGOING
**Goal:** Keep repository clean going forward
**Time:** Ongoing
**Risk:** None

**New Practices:**

1. **Use Agentic Primitives Workflow**
   - Location: `docs/agentic-primitives/` (after cleanup)
   - Review before starting work
   - Follow documented patterns

2. **Branch Strategy**
   ```
   main (production) ← Always stable
   ├── development (integration) ← Tested code only
   │   ├── feat/your-feature ← Your work
   │   └── fix/bug-name ← Bug fixes
   └── experimental/* ← Untested/risky work
   ```

3. **Pre-commit Checks**
   ```bash
   # Add to .git/hooks/pre-commit
   - Run tests
   - Check linting
   - Verify no root clutter
   ```

4. **Regular Cleanup**
   ```bash
   # Weekly command
   ./scripts/cleanup_and_organize_repo.sh
   ```

---

## 🚀 Execution Plan (Start Now)

### Step 1: Run Cleanup Script (2 minutes)

```bash
# Execute the cleanup
./scripts/cleanup_and_organize_repo.sh --execute

# Review changes
git status
git diff --stat
```

**Expected Result:**
- Root reduced from 220 to ~30 files
- All docs in docs/
- All logs/artifacts archived
- Scripts organized

---

### Step 2: Commit Cleanup (2 minutes)

```bash
git add -A
git commit -m "chore: organize repository structure

Cleanup actions:
- Move 66 documentation files to docs/
- Archive 74 test artifacts to .archive/
- Organize scripts into scripts/ subdirectories
- Move coverage reports to artifacts/
- Update .gitignore for organized structure

Benefits:
- Clean root directory (220 → ~30 files)
- Professional repository structure
- Easier to navigate and maintain
- Follows best practices

Files can be restored from backup branch if needed:
backup-pre-cleanup-$(date +%Y%m%d)"
```

---

### Step 3: Decide on Branch Strategy (5 minutes)

**Ask yourself:**
1. Do I need the experimental code from this branch?
   - **Yes** → Use Option B (clean up commits)
   - **No** → Use Option A (start fresh from main)

2. Are the 14 commits ahead of main important?
   - **Yes** → Review each commit, keep good ones
   - **No** → Just keep the cleanup, discard rest

3. Do I want to fix workflows on this branch?
   - **Yes** → Continue on this branch
   - **No** → Start fresh on main

**Recommended:** Option A (start fresh)

---

### Step 4: Execute Branch Strategy (5 minutes)

**If Option A (Recommended):**

```bash
# Tag current work
git tag experimental-phase7-$(date +%Y%m%d)

# Return to main
git checkout main

# Pull latest
git pull origin main

# Create organized branch
git checkout -b feat/repository-organization

# Cherry-pick cleanup (get SHA from log)
git log experimental-phase7-$(date +%Y%m%d) --oneline -1
git cherry-pick <cleanup-commit-sha>

# Push
git push -u origin feat/repository-organization

# Create PR
gh pr create --base main \
  --title "chore: Organize repository structure" \
  --body "Cleans up root directory, organizes documentation and scripts. See commit message for details."
```

**If Option B:**

```bash
# Stay on current branch
git push origin phase7-openhands-integration-results

# Create PR with cleanup
gh pr create --base main \
  --title "feat: Phase 7 work + repository organization" \
  --body "Contains experimental phase 7 work and repository cleanup. May need workflow fixes."
```

---

### Step 5: Fix Workflows (ongoing)

```bash
# Check what's failing
gh run list --limit 5

# View specific failure
gh run view <run-id> --log-failed

# Run tests locally
make test

# Fix and iterate
```

---

## 📋 Quick Command Reference

### Cleanup Commands
```bash
# Dry run (safe, shows what would happen)
./scripts/cleanup_and_organize_repo.sh

# Execute cleanup
./scripts/cleanup_and_organize_repo.sh --execute

# View backup branches
git branch | grep backup

# Restore from backup if needed
git checkout backup-pre-cleanup-<date>
```

### Branch Management
```bash
# See all branches
git branch -a

# See commits ahead/behind
git log --oneline main..HEAD  # Commits ahead
git log --oneline HEAD..main  # Commits behind

# Tag current work
git tag experimental-work-$(date +%Y%m%d)

# Switch to main
git checkout main

# Create fresh branch
git checkout -b feat/new-feature
```

### Workflow Debugging
```bash
# List recent runs
gh run list --limit 10

# View failed run logs
gh run view <run-id> --log-failed

# Re-run failed workflow
gh run rerun <run-id>

# Watch workflow in real-time
gh run watch
```

---

## 🎯 Success Criteria

After completing all steps, you should have:

- ✅ Clean root directory (<30 files)
- ✅ All docs in docs/
- ✅ All scripts organized
- ✅ All artifacts archived
- ✅ On a stable branch (main or clean feature branch)
- ✅ Workflows passing (or know what to fix)
- ✅ Clear git history
- ✅ Tagged experimental work (preserved)

---

## 🆘 Emergency Rollback

If anything goes wrong:

```bash
# 1. Find backup branch
git branch | grep backup-pre-cleanup

# 2. Restore from backup
git checkout backup-pre-cleanup-<date>

# 3. Create new branch from backup
git checkout -b recovery-branch

# 4. You're back to before cleanup
```

**ALL your work is safe!** The script creates backups before any changes.

---

## 📚 Resources

After cleanup, these will be in organized locations:

- **Agentic Primitives:** `docs/agentic-primitives/`
- **Workflow Guides:** `docs/guides/`
- **Phase Reports:** `docs/phases/`
- **Scripts:** `scripts/` (organized by purpose)
- **Test Results:** `.archive/test-results/`

---

## 🎉 Next Steps After Cleanup

1. **Review Your Work**
   ```bash
   git log --oneline -10
   git diff main..HEAD
   ```

2. **Test Everything**
   ```bash
   make test
   make lint
   ```

3. **Create PR**
   ```bash
   gh pr create --web
   ```

4. **Plan Next Feature**
   - Use agentic primitives from `docs/agentic-primitives/`
   - Follow branch strategy
   - Keep root clean

---

## 💡 Pro Tips

1. **Before starting new work:**
   ```bash
   ./scripts/cleanup_and_organize_repo.sh  # Check if cleanup needed
   ```

2. **Keep documentation current:**
   - Update docs/ when you make changes
   - Don't let files pile up in root

3. **Use feature branches:**
   - Never work directly on main
   - Use descriptive names: `feat/add-caching`
   - Keep branches short-lived (<1 week)

4. **Tag experimental work:**
   - Use `experimental/*` prefix
   - Tag before switching to stable work
   - Document what was experimental

---

## ✅ Ready to Execute?

Run this now:
```bash
./scripts/cleanup_and_organize_repo.sh --execute
```

Then review this document for next steps!

---

**Questions?**
- Everything is backed up automatically
- You can rollback at any time
- No destructive operations (moves only, no deletions)
- All your work is preserved
