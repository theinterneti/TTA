# GitHub Actions Workflows

This directory contains all GitHub Actions workflows for the TTA repository. These workflows automate testing, code quality checks, security scanning, and deployment processes.

## 📋 Workflow Overview

### Core Workflows

#### 1. Code Quality (`code-quality.yml`) ⭐ NEW
**Purpose:** Enforce code quality standards on all pull requests
**Triggers:** PRs, push to main/feat branches, manual
**Status:** ✅ Active

**Jobs:**
- **Lint with Ruff** - Fast Python linting
- **Format Check** - Verify black and isort formatting
- **Type Check with mypy** - Static type analysis
- **Complexity Analysis** - Code complexity metrics (informational)

**Key Features:**
- Parallel job execution for speed
- Dependency caching with uv
- Clear, actionable error messages
- Solo-developer friendly

**Quick Fixes:**
```bash
# Fix formatting issues
uv run black src/ tests/
uv run isort src/ tests/

# Check linting
uv run ruff check src/ tests/

# Check types
uv run mypy src/
```

---

#### 2. Tests (`tests.yml`)
**Purpose:** Run unit and integration tests
**Triggers:** Push to main/staging/development branches, PRs
**Status:** ✅ Active

**Branch-Specific Behavior:**
- **development**: Unit tests only (~5-10 min)
- **staging**: Full test suite (~20-30 min)
- **main**: Comprehensive tests (~45-60 min)

**Jobs:**
- **Unit Tests** - Fast unit tests with coverage
- **Integration Tests** - Tests with Neo4j and Redis (skipped on development)
- **Monitoring Validation** - Prometheus/Grafana checks

**Services:**
- Neo4j 5-community
- Redis 7

---

#### 3. E2E Tests (`e2e-tests.yml`)
**Purpose:** End-to-end testing with Playwright
**Triggers:** Push to branches, PRs, scheduled daily, manual
**Status:** ✅ Active

**Test Matrix:**
- Browsers: Chromium, Firefox, WebKit
- Devices: Desktop, Mobile Chrome, Mobile Safari
- Test Suites: Auth, Dashboard, Character, Chat, Settings, Accessibility, Responsive

**Features:**
- Visual regression testing
- Accessibility testing with axe-core
- Performance benchmarks
- Notification integration (Slack, Discord)

---

#### 4. Security Scan (`security-scan.yml`)
**Purpose:** Security vulnerability scanning
**Triggers:** Push to branches, PRs, scheduled daily, manual
**Status:** ⚠️ Needs update (conditional execution)

**Tools:**
- Semgrep - Static analysis
- CodeQL - Code analysis
- Trivy - Vulnerability scanner
- TruffleHog - Secrets detection
- GitLeaks - Secrets detection

**Planned Updates:**
- Remove conditional execution
- Add Python security tools (bandit, safety)
- Add SBOM generation

---

#### 5. Comprehensive Test Battery (`comprehensive-test-battery.yml`)
**Purpose:** Multi-category comprehensive testing
**Triggers:** Push to branches, PRs, scheduled daily, manual
**Status:** ⚠️ Needs update (uses pip instead of uv)

**Test Categories:**
- Standard user flows
- Adversarial testing
- Load/stress testing
- Data pipeline validation
- Dashboard verification

**Planned Updates:**
- Migrate to uv package manager
- Add frontend build validation

---

#### 6. Auto-Merge Workflows
**Purpose:** Automatically enable auto-merge for PRs
**Files:** `auto-merge-development.yml`, `auto-merge-staging.yml`
**Status:** ✅ Active

**Behavior:**
- **development**: Auto-merge enabled when unit tests pass
- **staging**: Auto-merge enabled when full test suite passes
- **main**: Manual approval required (no auto-merge)

---

#### 7. Simulation Testing (`simulation-testing.yml`)
**Purpose:** Simulation framework testing
**Triggers:** Push to paths, PRs, scheduled daily, manual
**Status:** ⚠️ Incomplete implementation

**Test Types:**
- Quick validation
- Comprehensive testing
- Production validation

**Planned Updates:**
- Complete simulation test implementation

---

## 🚀 Workflow Execution

### Local Testing

Before pushing, test locally:

```bash
# Code quality checks
uv run ruff check src/ tests/
uv run black --check src/ tests/
uv run isort --check-only src/ tests/
uv run mypy src/

# Unit tests
uv run pytest -q

# Integration tests (requires services)
uv run pytest -q --neo4j --redis

# E2E tests
npm run test:e2e
```

### Workflow Triggers

**On Pull Request:**
- Code Quality ✅
- Tests (branch-specific) ✅
- E2E Tests ✅
- Security Scan ✅
- Auto-merge (for development/staging) ✅

**On Push to Branches:**
- **development**: Unit tests, code quality
- **staging**: Full test suite, E2E tests
- **main**: Comprehensive tests, security scans, deployment

**Scheduled (Daily 2-3 AM UTC):**
- Comprehensive Test Battery
- E2E Tests
- Security Scan
- Simulation Testing

**Manual (workflow_dispatch):**
- All workflows support manual triggering
- Useful for testing and debugging

### Three-Tier Branching Strategy

TTA uses a three-tier branching strategy with branch-specific quality gates:

| Branch | Purpose | Tests | Auto-Merge | Approval |
|--------|---------|-------|------------|----------|
| `development` | Active development | Unit tests (~5-10 min) | ✅ Yes | ❌ No |
| `staging` | Pre-production | Full suite (~20-30 min) | ✅ Yes | ❌ No |
| `main` | Production | Comprehensive (~45-60 min) | ❌ No | ✅ Yes |

See [Branching Strategy Documentation](../../docs/development/BRANCHING_STRATEGY.md) for complete details.

---

## 📊 Status Checks

### Required Status Checks by Branch

**Development Branch:**
- `lint / Lint with Ruff`
- `format-check / Format Check`
- `type-check / Type Check with mypy`
- `unit` (unit tests)

**Staging Branch:**
- All development checks, plus:
- `integration` (integration tests)
- `E2E Tests (chromium - critical paths)`

**Main Branch:**
- All staging checks, plus:
- `security-scan / Security Scan`
- `E2E Tests (all browsers)`
- Manual approval required

See [Branch Protection Configuration](../repository-config/branch-protection-three-tier.yml) for complete configuration.

---

## 🔧 Workflow Configuration

### Environment Variables

Common environment variables used across workflows:

```yaml
env:
  PYTHON_VERSION: '3.12'
  NODE_VERSION: '18'
  PROMETHEUS_ENABLED: true
  GRAFANA_ENABLED: true
```

### Secrets Required

See `.github/repository-config/secrets-configuration.yml` for full list.

**Critical Secrets:**
- `GITHUB_TOKEN` - Automatically provided
- `SEMGREP_APP_TOKEN` - For Semgrep scanning
- `SLACK_WEBHOOK_URL` - For notifications (optional)
- `DISCORD_WEBHOOK_URL` - For notifications (optional)

### Caching Strategy

All workflows use dependency caching for faster runs:

**Python (uv):**
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/uv
      .venv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/pyproject.toml', '**/uv.lock') }}
```

**Node.js:**
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'
```

---

## 📈 Monitoring and Artifacts

### Artifacts

Workflows upload artifacts for debugging:

- **Test Results** - JUnit XML, HTML reports
- **Coverage Reports** - Code coverage data
- **Lint Results** - Ruff cache
- **Type Check Results** - mypy cache
- **E2E Results** - Screenshots, videos, traces
- **Security Reports** - SARIF files

**Retention:** 7-30 days depending on artifact type

### GitHub Step Summary

All workflows generate step summaries visible in the Actions UI:
- Overall status
- Quick fix commands
- Links to detailed reports

---

## 🛠️ Maintenance

### Adding New Workflows

1. Create workflow file in `.github/workflows/`
2. Test locally with `act` (optional)
3. Commit and push
4. Verify workflow runs successfully
5. Add to required status checks if needed
6. Update this README

### Updating Existing Workflows

1. Make changes to workflow file
2. Test on feature branch
3. Verify all jobs pass
4. Update branch protection if status check names changed
5. Update this README

### Troubleshooting

**Workflow not triggering:**
- Check trigger conditions (branches, paths)
- Verify workflow file syntax
- Check if workflow is disabled

**Jobs failing:**
- Check job logs in Actions UI
- Review step summaries
- Test locally with same commands
- Check for missing secrets/variables

**Slow workflow runs:**
- Verify caching is working
- Check for unnecessary steps
- Consider parallelization
- Review artifact sizes

---

## 📚 Related Documentation

- [Branching Strategy](../../docs/development/BRANCHING_STRATEGY.md) - Three-tier branching workflow
- [Quality Gates](../../docs/development/QUALITY_GATES.md) - Quality gate definitions
- [Branch Protection Configuration](../repository-config/branch-protection-three-tier.yml) - Branch protection rules
- [Secrets Configuration](../repository-config/secrets-configuration.yml) - Required secrets
- [GitHub Actions Documentation](https://docs.github.com/en/actions) - Official GitHub Actions docs

---

## 🎯 Roadmap

### Phase 1: Foundation (In Progress)
- ✅ Code Quality Workflow
- ⏳ Standardize Package Manager (uv)
- ⏳ Fix Security Scanning
- ⏳ Configure Branch Protection

### Phase 2: Consolidation
- Consolidate test workflows
- Enhance E2E workflow
- Refactor comprehensive test battery
- Create monitoring validation workflow

### Phase 3: Docker Validation
- Create Docker build workflow
- Validate all Dockerfiles
- Implement build caching

### Phase 4: Deployment
- Create staging deployment workflow
- Create production deployment workflow
- Implement health checks
- Add rollback mechanisms

### Phase 5: Code Revalidation
- Run all workflows on main branch
- Fix code quality issues
- Fix security vulnerabilities
- Optimize performance

### Phase 6: Documentation
- Complete workflow documentation
- Create deployment runbooks
- Document CI/CD pipeline
- Final validation

---

**Last Updated:** 2025-10-01
**Maintained By:** @theinterneti
