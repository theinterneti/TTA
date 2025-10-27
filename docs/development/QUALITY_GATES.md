# Quality Gates

This document defines the quality gates for the TTA project's three-tier branching strategy. Quality gates ensure that only code meeting specific quality standards can be promoted between branches.

## Overview

Quality gates are automated checks that must pass before code can be merged. The TTA project uses a tiered approach where more stringent checks are required as code moves closer to production.

```
feature/* → development → staging → main
   ↓            ↓           ↓         ↓
 Unit       Unit +      Full      Comprehensive
 Tests      Integration  Suite    + Manual Review
```

## Quality Gate Levels

### Level 1: Development Branch (Fast Feedback)

**Purpose:** Enable rapid iteration with basic quality assurance

**Required Checks:**
- ✅ Unit tests pass
- ✅ Code compiles/builds successfully

**Auto-Merge:** ✅ Enabled

**Typical Duration:** ~5-10 minutes

**Rationale:** Developers need fast feedback to maintain flow. Unit tests catch obvious bugs while allowing quick iteration.

---

### Level 2: Staging Branch (Pre-Production Validation)

**Purpose:** Validate integration and catch issues before production

**Required Checks:**
- ✅ All Level 1 checks
- ✅ Integration tests pass (Neo4j, Redis)
- ✅ E2E tests pass (core user flows)
  - Authentication flow
  - Dashboard functionality
- ✅ Code quality checks pass
  - Ruff linting
  - Black formatting
  - isort import sorting
  - mypy type checking
- ✅ Security scans pass
  - Bandit (Python security)
  - npm audit (JavaScript dependencies)
  - Semgrep (SAST)

**Auto-Merge:** ✅ Enabled

**Typical Duration:** ~20-30 minutes

**Rationale:** Staging should mirror production as closely as possible. Full integration testing ensures components work together correctly.

---

### Level 3: Main Branch (Production Ready)

**Purpose:** Ensure production-grade quality and stability

**Required Checks:**
- ✅ All Level 2 checks
- ✅ Comprehensive test battery
  - All E2E test suites (all browsers)
  - Performance tests
  - Accessibility tests
  - Responsive design tests
- ✅ Manual code review and approval
- ✅ Documentation updated
- ✅ Changelog updated

**Auto-Merge:** ❌ Disabled (Manual approval required)

**Typical Duration:** ~45-60 minutes + review time

**Rationale:** Production deployments require human oversight. Comprehensive testing catches edge cases and ensures system-wide stability.

---

## Test Categories

### Unit Tests
- **Scope:** Individual functions, classes, and modules
- **Dependencies:** Mocked
- **Speed:** Fast (~5-10 minutes)
- **Coverage Target:** ≥80%
- **Run Command:** `uv run pytest -m "not integration and not e2e"`

### Integration Tests
- **Scope:** Component interactions with real services
- **Dependencies:** Neo4j, Redis (Docker containers)
- **Speed:** Medium (~10-15 minutes)
- **Coverage Target:** Critical paths
- **Run Command:** `uv run pytest -m integration`

### E2E Tests (Core)
- **Scope:** Critical user journeys
- **Browser:** Chromium only
- **Flows:**
  - User authentication (login, logout, registration)
  - Dashboard navigation and functionality
- **Speed:** Medium (~10-15 minutes)
- **Run Command:** `npx playwright test tests/e2e/specs/auth.spec.ts tests/e2e/specs/dashboard.spec.ts --project=chromium`

### E2E Tests (Full)
- **Scope:** All user journeys
- **Browsers:** Chromium, Firefox, WebKit
- **Flows:**
  - All core flows
  - Character management
  - Chat functionality
  - Settings and preferences
  - Accessibility features
  - Responsive design
- **Speed:** Slow (~30-45 minutes)
- **Run Command:** `npx playwright test`

### Code Quality Checks
- **Ruff:** Fast Python linter
- **Black:** Python code formatter
- **isort:** Python import sorter
- **mypy:** Static type checker
- **Speed:** Fast (~2-3 minutes)
- **Run Command:** `./scripts/validate-quality-gates.sh`

### Security Scans
- **Bandit:** Python security linter
- **npm audit:** JavaScript dependency vulnerabilities
- **Semgrep:** Static application security testing (SAST)
- **Speed:** Medium (~5-10 minutes)
- **Run Command:** See `.github/workflows/security-scan.yml`

---

## Local Validation

Before pushing code, validate it meets quality gates locally:

```bash
# Validate for development branch
./scripts/validate-quality-gates.sh development

# Validate for staging branch
./scripts/validate-quality-gates.sh staging

# Validate for main branch
./scripts/validate-quality-gates.sh main
```

---

## Bypassing Quality Gates

Quality gates should **not** be bypassed except in emergencies. If you must bypass:

1. **Document the reason** in the PR description
2. **Create a follow-up issue** to address the skipped checks
3. **Get explicit approval** from a maintainer
4. **Use the emergency hotfix process** (see BRANCHING_STRATEGY.md)

---

## Quality Gate Failures

### Common Failures and Solutions

#### Unit Tests Failing
```bash
# Run tests locally to see failures
uv run pytest -v

# Run specific test
uv run pytest tests/path/to/test.py::test_name -v

# Check test coverage
uv run pytest --cov=src --cov-report=html
```

#### Integration Tests Failing
```bash
# Ensure services are running
docker compose up -d neo4j redis

# Check service health
docker compose ps

# View service logs
docker compose logs neo4j redis

# Run integration tests
uv run pytest -m integration -v
```

#### E2E Tests Failing
```bash
# Install browsers
npx playwright install

# Run tests in headed mode (see browser)
npx playwright test --headed

# Run specific test
npx playwright test tests/e2e/specs/auth.spec.ts

# View test report
npx playwright show-report
```

#### Code Quality Failing
```bash
# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Auto-format code
uv run black src/ tests/

# Auto-sort imports
uv run isort src/ tests/

# Check types
uv run mypy src/
```

---

## Monitoring Quality Gates

### GitHub Actions
- View workflow runs: https://github.com/theinterneti/TTA/actions
- Check branch protection: https://github.com/theinterneti/TTA/settings/branches

### Metrics
- **Pass Rate:** Percentage of PRs passing on first attempt
- **Average Duration:** Time from PR creation to merge
- **Failure Patterns:** Common reasons for quality gate failures

---

## Continuous Improvement

Quality gates should evolve with the project:

1. **Review metrics monthly** to identify bottlenecks
2. **Adjust test suites** based on failure patterns
3. **Optimize slow tests** to maintain fast feedback
4. **Add new checks** as quality standards evolve
5. **Remove obsolete checks** that no longer provide value

---

## Related Documentation

- [Branching Strategy](./BRANCHING_STRATEGY.md) - Branch hierarchy and workflow
- [Testing Guide](../testing-framework.md) - Comprehensive testing documentation
- [CI/CD Workflows](../../.github/workflows/README.md) - GitHub Actions configuration
