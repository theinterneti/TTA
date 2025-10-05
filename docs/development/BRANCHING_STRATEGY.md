# TTA Git Branching Strategy

**Version:** 1.0.0  
**Last Updated:** 2025-10-05  
**Status:** Active

## Overview

This document defines the git branching strategy for the TTA (Therapeutic Text Adventure) repository. The strategy is optimized for solo developer workflow while maintaining production-ready quality gates.

## Branch Hierarchy

```
feature/clinical-* ──┐
feature/game-*    ──┼──> development ──> staging ──> main
feature/infra-*   ──┘
```

## Branch Definitions

### `main` Branch
- **Purpose:** Production-ready code only
- **Protection Level:** Highest
- **Merge Source:** `staging` branch only
- **Deployment:** Automatic to production environment
- **Quality Gate:** ALL tests + manual approval

### `staging` Branch
- **Purpose:** Pre-production testing, "green" code only
- **Protection Level:** High
- **Merge Source:** `development` branch only
- **Deployment:** Automatic to staging environment
- **Quality Gate:** ALL tests pass (automated)

### `development` Branch
- **Purpose:** Active development, work-in-progress
- **Protection Level:** Minimal
- **Merge Source:** Feature branches
- **Deployment:** Optional to development environment
- **Quality Gate:** Unit tests pass (fast feedback)

### Feature Branches

**Naming Conventions:**
- `feature/clinical-*` - Clinical/therapeutic features
- `feature/game-*` - Single-player game features
- `feature/infra-*` - Infrastructure/DevOps changes
- `feature/docs-*` - Documentation updates
- `feature/fix-*` - Bug fixes

**Protection Level:** None (allow force push, rebasing)  
**Quality Gate:** None (local development)

## Quality Gates

### Level 1: Development → Staging (Automated)

**Required Checks:**
- ✅ All unit tests pass (`pytest tests/`)
- ✅ All integration tests pass (`pytest --neo4j --redis`)
- ✅ Code quality checks pass (Ruff, Black, isort)
- ✅ Type checking passes (mypy)
- ✅ Security scan passes (Bandit, Semgrep)
- ✅ E2E tests pass (Playwright - core flows)
- ✅ No merge conflicts

**Auto-merge:** Yes (when all checks pass)

### Level 2: Staging → Main (Automated + Manual)

**Required Checks:**
- ✅ All Level 1 checks pass
- ✅ Comprehensive test battery passes
- ✅ Performance benchmarks within budget
- ✅ Accessibility audit passes
- ✅ Visual regression tests pass
- ✅ Simulation tests pass (if applicable)
- ✅ Manual smoke testing complete
- ✅ Deployment to staging successful
- ✅ Manual approval (self-approval allowed for solo dev)

**Auto-merge:** No (requires manual approval)

## Daily Workflow

### 1. Create Feature Branch

```bash
# From development branch
git checkout development
git pull origin development

# Create feature branch
git checkout -b feature/game-narrative-engine
```

### 2. Develop and Commit

```bash
# Make changes
git add .
git commit -m "feat(game): add narrative branching system"

# Pre-commit hooks run automatically:
# - Linting (Ruff)
# - Formatting (Black, isort)
# - Type checking (mypy)
# - Security scanning (Bandit)
```

### 3. Push and Create PR to Development

```bash
git push origin feature/game-narrative-engine

# Create PR
gh pr create --base development --fill
```

**CI runs:** Unit tests (fast feedback ~5-10 min)  
**Merge when:** Unit tests pass

### 4. Promote to Staging

```bash
# When ready for staging
gh pr create --base staging --head development --fill
```

**CI runs:** Full test suite (~20-30 min)  
**Auto-merge:** Yes (when all tests pass)

### 5. Promote to Production

```bash
# When ready for production
gh pr create --base main --head staging --fill
```

**CI runs:** Full test suite + comprehensive battery (~45-60 min)  
**Auto-merge:** No (requires manual approval)

## Branch Protection Rules

### `main` Branch

```yaml
required_status_checks:
  strict: true
  contexts:
    - "unit"
    - "integration"
    - "e2e-tests / E2E Tests (chromium - auth)"
    - "e2e-tests / E2E Tests (chromium - dashboard)"
    - "code-quality / Lint and Format"
    - "code-quality / Type Check"
    - "security-scan / Security Scan"
    - "comprehensive-tests / Core Tests"

required_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true

enforce_admins: false
allow_force_pushes: false
allow_deletions: false
required_linear_history: true
allow_auto_merge: false  # Manual approval required
```

### `staging` Branch

```yaml
required_status_checks:
  strict: true
  contexts:
    - "unit"
    - "integration"
    - "e2e-tests / E2E Tests (chromium - auth)"
    - "code-quality / Lint and Format"
    - "security-scan / Security Scan"

required_pull_request_reviews:
  required_approving_review_count: 0  # Auto-merge allowed

enforce_admins: false
allow_force_pushes: false
allow_deletions: false
required_linear_history: true
allow_auto_merge: true  # Auto-merge when tests pass
```

### `development` Branch

```yaml
required_status_checks:
  strict: false
  contexts:
    - "unit"  # Only unit tests required

required_pull_request_reviews:
  required_approving_review_count: 0

enforce_admins: false
allow_force_pushes: false
allow_deletions: false
required_linear_history: false  # Allow merge commits
allow_auto_merge: true
```

### Feature Branches (`feature/*`)

```yaml
# No protection - allow experimentation
allow_force_pushes: true
allow_deletions: true
```

## CI/CD Strategy

### On Feature Branch Push
- **Run:** Linting, formatting checks (fast feedback)
- **Optional:** Unit tests
- **Time:** ~2-3 minutes

### On PR to `development`
- **Run:** Unit tests, basic integration tests
- **Time:** ~5-10 minutes
- **Auto-merge:** Yes (if tests pass)

### On PR to `staging`
- **Run:** Full test suite (unit, integration, E2E)
- **Run:** Security scans, code quality
- **Run:** Performance benchmarks
- **Time:** ~20-30 minutes
- **Auto-merge:** Yes (if all pass)

### On PR to `main`
- **Run:** Full test suite + comprehensive battery
- **Run:** All quality gates
- **Run:** Simulation tests
- **Time:** ~45-60 minutes
- **Auto-merge:** No (require manual approval)

## Emergency Procedures

### Hotfix to Production

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug-fix

# Make fix and commit
git add .
git commit -m "fix: critical security vulnerability"

# Create PR directly to main
gh pr create --base main --fill

# Requires manual approval but can bypass some checks
```

### Rollback

```bash
# Revert to previous commit on main
git checkout main
git revert HEAD
git push origin main

# Or reset to specific commit (use with caution)
git reset --hard <commit-hash>
git push origin main --force-with-lease
```

## Best Practices

1. **Keep feature branches small** - Easier to review and merge
2. **Commit frequently** - Small, atomic commits with clear messages
3. **Use conventional commits** - `feat:`, `fix:`, `docs:`, `refactor:`, etc.
4. **Run tests locally** - Before pushing to remote
5. **Keep branches up to date** - Regularly merge from development
6. **Delete merged branches** - Keep repository clean
7. **Use draft PRs** - For work-in-progress features
8. **Write descriptive PR descriptions** - Explain what and why

## Troubleshooting

### PR Blocked by Failed Tests

```bash
# Check CI logs
gh pr checks

# Run tests locally
uv run pytest

# Fix issues and push
git add .
git commit -m "fix: resolve test failures"
git push
```

### Merge Conflicts

```bash
# Update your branch
git checkout feature/your-branch
git fetch origin
git merge origin/development

# Resolve conflicts
# ... edit files ...
git add .
git commit -m "chore: resolve merge conflicts"
git push
```

### Need to Update Branch Protection

```bash
# Use the configuration script
.github/scripts/configure-branch-protection.sh

# Or manually via GitHub web UI
# Settings > Branches > Edit rule
```

## Related Documentation

- [Quality Gates Reference](./QUALITY_GATES.md)
- [CI/CD Workflows](./.github/workflows/README.md)
- [Contributing Guide](../../CONTRIBUTING.md)
- [Git Commit Strategy](./GIT_COMMIT_STRATEGY.md)

## Changelog

### 2025-10-05 - v1.0.0
- Initial branching strategy implementation
- Three-tier hierarchy (development, staging, main)
- Feature branch naming conventions
- Quality gate definitions
- Branch protection rules

