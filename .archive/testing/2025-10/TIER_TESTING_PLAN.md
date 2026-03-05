# Tier-Aware Workflow Testing Plan

**Status**: ✅ Ready for Testing
**Date**: 2025-10-29
**Branch Pushed**: fix/codecov-upload-on-failure

---

## Overview

Phase 1 implementation is complete and committed. All workflows now use progressive quality gates based on branch tier. This document outlines the testing strategy to validate the implementation.

## What Was Pushed

**Commit**: `58418ee05` - "feat: implement tier-aware workflow escalation system"

### Files Modified (5 workflows)
- ✅ `.github/workflows/templates/determine-tier.yml` (created)
- ✅ `.github/workflows/tests.yml` (modified)
- ✅ `.github/workflows/code-quality.yml` (modified)
- ✅ `.github/workflows/coverage.yml` (modified)
- ✅ `.github/workflows/mutation-testing.yml` (modified)

### Documentation Added
- ✅ `COMPONENT_INVENTORY.md` (24 components)
- ✅ `REPOSITORY_STATUS_AND_WORKFLOW_STRATEGY.md` (strategy)
- ✅ `WORKFLOW_ESCALATION_IMPLEMENTATION.md` (implementation guide)
- ✅ `WORKFLOW_ESCALATION_CHECKLIST.md` (rollout checklist)
- ✅ `REPOSITORY_REORGANIZATION_PROGRESS.md` (dashboard)

---

## Testing Strategy

### Step 1: Create PR from Current Branch

**Current Branch**: `fix/codecov-upload-on-failure`
**Target Branch**: Choose based on tier you want to test

#### Option A: Test Tier 2 (Development) - RECOMMENDED FIRST
```bash
# Current branch targets development
# This will test Tier 2 workflows
gh pr create --base development \
  --title "test: validate tier 2 workflow escalation" \
  --body "Testing tier 2 (development) workflow behavior:
- Format + Lint required
- Unit + Integration tests required
- Coverage ≥60% required
- No mutation testing"
```

#### Option B: Test Tier 3 (Staging)
```bash
# Change PR target to staging
gh pr create --base staging \
  --title "test: validate tier 3 workflow escalation" \
  --body "Testing tier 3 (staging) workflow behavior:
- Format + Lint + Type + Security required
- Full test suite required
- Coverage ≥70% required
- Mutation testing ≥75% required"
```

#### Option C: Test Tier 4 (Production)
```bash
# Change PR target to main
gh pr create --base main \
  --title "test: validate tier 4 workflow escalation" \
  --body "Testing tier 4 (production) workflow behavior:
- All quality checks required
- Full test suite required
- Coverage ≥85% required
- Mutation testing ≥85% required"
```

### Step 2: Create Tier 1 Test Branch

```bash
# Create new experimental feature branch
git checkout development
git pull origin development
git checkout -b feat/test-tier-1-validation

# Add test file
git add TIER_1_TEST.md
git commit -m "test: tier 1 workflow validation"
git push -u origin feat/test-tier-1-validation

# Create PR targeting development (tier 1)
gh pr create --base development \
  --title "test: validate tier 1 workflow escalation" \
  --body "Testing tier 1 (experimental) workflow behavior:
- Format check only (failures allowed)
- Unit tests only (failures allowed)
- No coverage threshold
- No mutation testing"
```

### Step 3: Validation Checklist

For each PR created, verify:

#### Workflow Execution
- [ ] Tier detection job runs first
- [ ] Tier correctly detected (check Actions logs)
- [ ] GitHub Step Summary shows tier name
- [ ] Conditional jobs skip as expected
- [ ] Required jobs run as expected

#### Tier-Specific Behavior
- [ ] **Tier 1**: Format only, failures allowed, no blocking
- [ ] **Tier 2**: Format + Lint + Integration tests, coverage ≥60%
- [ ] **Tier 3**: + Type check + Security + E2E, coverage ≥70%, mutation ≥75%
- [ ] **Tier 4**: All checks strict, coverage ≥85%, mutation ≥85%

#### GitHub UI
- [ ] Status checks appear in PR
- [ ] Check names indicate tier
- [ ] Summary shows tier-specific thresholds
- [ ] Failure messages are helpful
- [ ] PR comments include tier info

---

## Expected Results by Tier

### Tier 1 (feat/* → development)

**Jobs That Run**:
- ✅ tier (detect tier)
- ✅ format-check (failures allowed)
- ✅ unit tests (failures allowed)
- ✅ test-summary (informational)

**Jobs That Skip**:
- ⏭️ lint
- ⏭️ type-check
- ⏭️ security
- ⏭️ integration tests
- ⏭️ monitoring-validation
- ⏭️ mutation testing

**Thresholds**:
- Coverage: 0% (report only)
- Mutation: N/A (skipped)

**PR Merge**: ✅ Allowed even with failures

---

### Tier 2 (feat/* → development base)

**Jobs That Run**:
- ✅ tier
- ✅ format-check (required)
- ✅ lint (required)
- ✅ unit tests (required)
- ✅ integration tests (required)
- ✅ coverage (≥60% required)

**Jobs That Skip**:
- ⏭️ type-check
- ⏭️ security
- ⏭️ monitoring-validation
- ⏭️ mutation testing

**Thresholds**:
- Coverage: ≥60% (blocks if below)
- Mutation: N/A (skipped)

**PR Merge**: ❌ Blocked if checks fail

---

### Tier 3 (feat/* → staging)

**Jobs That Run**:
- ✅ tier
- ✅ format-check (required)
- ✅ lint (required)
- ✅ type-check (required)
- ✅ security scan (required)
- ✅ unit tests (required)
- ✅ integration tests (required)
- ✅ monitoring-validation (required)
- ✅ coverage (≥70% required)
- ✅ mutation testing (≥75% required)

**Jobs That Skip**:
- None (all checks required)

**Thresholds**:
- Coverage: ≥70% (blocks if below)
- Mutation: ≥75% (blocks if below)

**PR Merge**: ❌ Blocked if checks fail

---

### Tier 4 (hotfix/* → main)

**Jobs That Run**:
- ✅ All checks from Tier 3
- ✅ Stricter thresholds

**Jobs That Skip**:
- None (all checks required)

**Thresholds**:
- Coverage: ≥85% (blocks if below)
- Mutation: ≥85% (blocks if below)

**PR Merge**: ❌ Blocked if checks fail

---

## Quick Start Commands

### Test Current Branch (Tier 2 or 3)

```bash
# For Tier 2 (development)
gh pr create --base development --title "test: tier 2 validation" \
  --body "Testing tier 2 workflows"

# For Tier 3 (staging)
gh pr create --base staging --title "test: tier 3 validation" \
  --body "Testing tier 3 workflows"

# For Tier 4 (production)
gh pr create --base main --title "test: tier 4 validation" \
  --body "Testing tier 4 workflows"
```

### Create Tier 1 Test Branch

```bash
git checkout development
git checkout -b feat/test-tier-1
echo "# Tier 1 Test" > TIER_1_TEST.md
git add TIER_1_TEST.md
git commit -m "test: tier 1 validation"
git push -u origin feat/test-tier-1
gh pr create --base development --title "test: tier 1 validation"
```

---

## Troubleshooting

### Tier Not Detected

**Symptom**: Tier job fails or outputs wrong tier
**Solution**: Check PR base_ref matches expected branch name

### Workflows Don't Run

**Symptom**: No checks appear on PR
**Solution**: Verify workflow files committed and pushed

### Jobs Don't Skip

**Symptom**: Jobs run that should be skipped
**Solution**: Check `if:` conditionals and needs dependencies

### Thresholds Not Enforced

**Symptom**: PR passes with low coverage
**Solution**: Check coverage.yml threshold calculation logic

---

## Next Steps After Testing

1. ✅ Validate all 4 tiers work correctly
2. ✅ Document any issues found
3. ✅ Fix workflow bugs if needed
4. ✅ Create GitHub tracking issues (15 templates ready)
5. ✅ Proceed to Phase 2 (Component Organization)

---

## PR Links (To Be Created)

- [ ] **Tier 1 Test**: [Create PR]
- [ ] **Tier 2 Test**: [Create PR]
- [ ] **Tier 3 Test**: [Create PR]
- [ ] **Tier 4 Test**: [Create PR]

Once PRs are created, add links here for easy tracking.

---

**Status**: Ready to create test PRs
**Action Required**: Run commands above to create PRs and validate workflows


---
**Logseq:** [[TTA.dev/.archive/Testing/2025-10/Tier_testing_plan]]
