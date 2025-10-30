# Workflow Escalation Implementation Guide

**Status**: Ready for Implementation
**Timeline**: 3 weeks
**Dependencies**: GitHub Actions, existing workflow infrastructure

---

## Quick Start

### Step 1: Add Branch Tier Detection (Common Template)

Create `.github/workflows/templates/determine-tier.yml`:

```yaml
name: Determine Quality Tier

on:
  workflow_call:
    outputs:
      tier:
        description: "Quality tier (1-4) based on target branch"
        value: ${{ jobs.detect-tier.outputs.tier }}
      tier_name:
        description: "Human-readable tier name"
        value: ${{ jobs.detect-tier.outputs.tier_name }}

jobs:
  detect-tier:
    name: Detect Quality Tier
    runs-on: ubuntu-latest
    outputs:
      tier: ${{ steps.determine.outputs.tier }}
      tier_name: ${{ steps.determine.outputs.tier_name }}
    steps:
      - name: Determine quality tier from branch
        id: determine
        run: |
          BASE_REF="${{ github.base_ref || github.ref_name }}"
          echo "Base reference: $BASE_REF"

          if [[ "$BASE_REF" == "main" || "$BASE_REF" == "refs/heads/main" ]]; then
            echo "tier=4" >> $GITHUB_OUTPUT
            echo "tier_name=Production" >> $GITHUB_OUTPUT
            echo "📦 Production tier (4) - Maximum quality gates"
          elif [[ "$BASE_REF" == "staging" || "$BASE_REF" == "refs/heads/staging" ]]; then
            echo "tier=3" >> $GITHUB_OUTPUT
            echo "tier_name=Staging" >> $GITHUB_OUTPUT
            echo "🎭 Staging tier (3) - Strict quality gates"
          elif [[ "$BASE_REF" == "development" || "$BASE_REF" == "refs/heads/development" ]]; then
            echo "tier=2" >> $GITHUB_OUTPUT
            echo "tier_name=Development" >> $GITHUB_OUTPUT
            echo "🔨 Development tier (2) - Moderate quality gates"
          else
            echo "tier=1" >> $GITHUB_OUTPUT
            echo "tier_name=Experimental" >> $GITHUB_OUTPUT
            echo "🧪 Experimental tier (1) - Minimal quality gates"
          fi

      - name: Add tier info to summary
        run: |
          echo "## Quality Tier: ${{ steps.determine.outputs.tier_name }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "Target branch: \`${{ github.base_ref || github.ref_name }}\`" >> $GITHUB_STEP_SUMMARY
          echo "Tier level: **${{ steps.determine.outputs.tier }}**" >> $GITHUB_STEP_SUMMARY
```

---

## Step 2: Modify Existing Workflows

### Example: tests.yml (Tier-Aware Testing)

Add to `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches:
      - main
      - staging
      - development
      - 'experimental/**'
      - 'feat/**'
      - 'fix/**'
  pull_request:

jobs:
  # First, determine quality tier
  tier:
    uses: ./.github/workflows/templates/determine-tier.yml

  # Unit tests run on ALL tiers (but with different subsets)
  unit:
    needs: tier
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
        with:
          version: "0.8.17"

      - name: Sync deps
        run: uv sync --all-groups

      - name: Run unit tests (tier ${{ needs.tier.outputs.tier }})
        run: |
          if [ "${{ needs.tier.outputs.tier }}" == "1" ]; then
            # Experimental: Quick tests only
            echo "Running quick unit tests for experimental branch..."
            uv run pytest tests/unit/ -m "not slow" --tb=short -q
          else
            # All other tiers: Full unit tests
            echo "Running full unit tests..."
            uv run pytest tests/unit/ -q --tb=short \
              --junitxml=test-results/unit-tests.xml \
              --cov=src --cov-branch --cov-report=xml:coverage-unit.xml
          fi

      - name: Upload coverage (tier 2+)
        if: needs.tier.outputs.tier >= 2
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage-unit.xml
          flags: unit
          fail_ci_if_error: false

  # Integration tests: Only tier 2+ (development, staging, production)
  integration:
    needs: tier
    if: needs.tier.outputs.tier >= 2
    runs-on: ubuntu-latest
    services:
      neo4j:
        image: neo4j:5-community
        env:
          NEO4J_AUTH: neo4j/testpassword
        ports:
          - 7687:7687
      redis:
        image: redis:7
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1

      - name: Run integration tests
        run: |
          if [ "${{ needs.tier.outputs.tier }}" == "2" ]; then
            # Development: Core integration tests only
            echo "Running core integration tests..."
            uv run pytest tests/integration/ -m "core" --neo4j --redis
          else
            # Staging/Production: Full integration tests
            echo "Running full integration tests..."
            uv run pytest tests/integration/ --neo4j --redis \
              --junitxml=test-results/integration-tests.xml \
              --cov=src --cov-branch --cov-report=xml:coverage-integration.xml
          fi
        env:
          TEST_NEO4J_URI: "bolt://localhost:7687"
          TEST_REDIS_URI: "redis://localhost:6379/0"
```

---

### Example: code-quality.yml (Tier-Aware Quality Checks)

Add to `.github/workflows/code-quality.yml`:

```yaml
name: Code Quality

on:
  pull_request:
  push:
    branches:
      - main
      - staging
      - development

jobs:
  tier:
    uses: ./.github/workflows/templates/determine-tier.yml

  # Basic formatting: ALL tiers
  format-check:
    needs: tier
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1

      - name: Check formatting
        run: |
          echo "Running format check (required for all tiers)..."
          uvx ruff format --check --diff src/ tests/

  # Full linting: Tier 2+ only
  lint:
    needs: tier
    if: needs.tier.outputs.tier >= 2
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1

      - name: Run ruff linter
        run: |
          echo "Running full linting for tier ${{ needs.tier.outputs.tier }}..."
          uvx ruff check src/ tests/ --output-format=github
        continue-on-error: false

  # Type checking: Tier 2+ (warnings OK for tier 2, strict for tier 3+)
  type-check:
    needs: tier
    if: needs.tier.outputs.tier >= 2
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1

      - name: Run Pyright
        run: |
          if [ "${{ needs.tier.outputs.tier }}" == "2" ]; then
            echo "Running Pyright (warnings allowed for development)..."
            uvx pyright src/ || true
          else
            echo "Running Pyright (strict mode for staging/production)..."
            uvx pyright src/
          fi
```

---

### Example: mutation-testing.yml (Tier 3+ Only)

Add to `.github/workflows/mutation-testing.yml`:

```yaml
name: Mutation Testing

on:
  pull_request:
    branches:
      - main
      - staging
  push:
    branches:
      - main
      - staging

jobs:
  tier:
    uses: ./.github/workflows/templates/determine-tier.yml

  mutation:
    needs: tier
    # Only run on staging (tier 3) and production (tier 4)
    if: needs.tier.outputs.tier >= 3
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1

      - name: Run mutation testing
        run: |
          THRESHOLD="75"
          if [ "${{ needs.tier.outputs.tier }}" == "4" ]; then
            THRESHOLD="85"
            echo "Production tier - requiring 85% mutation score"
          else
            echo "Staging tier - requiring 75% mutation score"
          fi

          # Run mutation testing
          uv run mutmut run

          # Check score meets threshold
          SCORE=$(uv run mutmut results | grep -oP '\d+(?=% survived)' || echo "0")
          if [ "$SCORE" -lt "$THRESHOLD" ]; then
            echo "❌ Mutation score $SCORE% below threshold $THRESHOLD%"
            exit 1
          else
            echo "✅ Mutation score $SCORE% meets threshold $THRESHOLD%"
          fi
```

---

### Example: coverage.yml (Tier-Aware Coverage Requirements)

Add to `.github/workflows/coverage.yml`:

```yaml
name: Coverage

on:
  pull_request:
  push:
    branches:
      - main
      - staging
      - development

jobs:
  tier:
    uses: ./.github/workflows/templates/determine-tier.yml

  coverage:
    needs: tier
    # Skip for experimental (tier 1)
    if: needs.tier.outputs.tier >= 2
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1

      - name: Run tests with coverage
        run: |
          uv run pytest --cov=src --cov-branch --cov-report=xml --cov-report=term

      - name: Check coverage threshold
        run: |
          # Set threshold based on tier
          case "${{ needs.tier.outputs.tier }}" in
            2) THRESHOLD=60 ;;  # Development
            3) THRESHOLD=70 ;;  # Staging
            4) THRESHOLD=85 ;;  # Production
            *) THRESHOLD=0 ;;
          esac

          echo "Required coverage for ${{ needs.tier.outputs.tier_name }}: ${THRESHOLD}%"

          # Extract coverage percentage
          COVERAGE=$(python -c "import xml.etree.ElementTree as ET; print(ET.parse('coverage.xml').getroot().attrib['line-rate'])" | awk '{print int($1*100)}')

          echo "Current coverage: ${COVERAGE}%"

          if [ "$COVERAGE" -lt "$THRESHOLD" ]; then
            echo "❌ Coverage ${COVERAGE}% below threshold ${THRESHOLD}%"
            exit 1
          else
            echo "✅ Coverage ${COVERAGE}% meets threshold ${THRESHOLD}%"
          fi
```

---

## Step 3: Update Branch Protection Rules

### GitHub Repository Settings

Navigate to: Settings → Branches → Branch protection rules

#### For `main` (Production - Tier 4)

**Require status checks before merging**:
- [x] Require branches to be up to date before merging
- [x] Status checks:
  - format-check
  - lint
  - type-check (strict)
  - unit (all)
  - integration (all)
  - e2e (comprehensive)
  - mutation (≥85%)
  - coverage (≥85%)
  - security-scan
  - load-tests

**Additional settings**:
- [x] Require pull request reviews (2 approvers)
- [x] Require conversation resolution
- [x] Require signed commits
- [ ] Allow force pushes (disabled)
- [ ] Allow deletions (disabled)

#### For `staging` (Tier 3)

**Require status checks before merging**:
- [x] Status checks:
  - format-check
  - lint
  - type-check (strict)
  - unit (all)
  - integration (all)
  - e2e (core)
  - mutation (≥75%)
  - coverage (≥70%)
  - security-scan

**Additional settings**:
- [x] Require pull request reviews (1 approver)
- [x] Require conversation resolution
- [ ] Allow force pushes (disabled)

#### For `development` (Tier 2)

**Require status checks before merging**:
- [x] Status checks:
  - format-check
  - lint
  - type-check (warnings OK)
  - unit (all)
  - integration (core)
  - coverage (≥60%)

**Additional settings**:
- [ ] Require pull request reviews (optional)
- [ ] Allow force pushes (enabled for maintainers)

#### For `experimental/*` (Tier 1)

**No branch protection rules** - fast iteration

---

## Step 4: Developer Communication

### Update CONTRIBUTING.md

Add section:

````markdown
## Branch Strategy and Quality Gates

TTA uses a tiered branch strategy with escalating quality gates:

### Tier 1: Experimental Branches (`experimental/*`, `feat/*`, `fix/*`)
- **Purpose**: Rapid prototyping, spike solutions
- **Checks**: Basic syntax only
- **CI Time**: ~3 minutes
- **Coverage**: None required

### Tier 2: Development (`development`)
- **Purpose**: Regular development work
- **Checks**: Linting, unit tests, type checking (warnings OK)
- **CI Time**: ~10 minutes
- **Coverage**: ≥60% required

### Tier 3: Staging (`staging`)
- **Purpose**: Pre-production validation
- **Checks**: Full testing suite, mutation testing
- **CI Time**: ~30 minutes
- **Coverage**: ≥70%, Mutation: ≥75%

### Tier 4: Production (`main`)
- **Purpose**: Production releases
- **Checks**: Maximum quality gates, manual approval
- **CI Time**: ~60 minutes
- **Coverage**: ≥85%, Mutation: ≥85%

### Workflow

1. Create feature branch from `development`
2. Develop with tier 2 checks
3. Open PR to `development` (auto-merge after checks)
4. Merge to `staging` for tier 3 validation
5. After 7-day observation, merge to `main` with manual approval
````

---

## Step 5: Testing the Implementation

### Test Plan

1. **Tier 1 Test** (Experimental):
   ```bash
   git checkout -b experimental/test-tier1
   # Make minimal changes
   git push origin experimental/test-tier1
   # Verify: Only format-check runs (~3 min)
   ```

2. **Tier 2 Test** (Development):
   ```bash
   git checkout development
   git checkout -b feat/test-tier2
   # Make changes with tests
   git push origin feat/test-tier2
   # Create PR to development
   # Verify: Format, lint, type-check, unit tests, integration (core) run (~10 min)
   ```

3. **Tier 3 Test** (Staging):
   ```bash
   git checkout staging
   git checkout -b fix/test-tier3
   # Make changes
   git push origin fix/test-tier3
   # Create PR to staging
   # Verify: Full suite + mutation testing runs (~30 min)
   ```

4. **Tier 4 Test** (Production):
   ```bash
   # Create PR from staging to main
   # Verify: Maximum quality gates + manual approval required (~60 min)
   ```

---

## Rollback Plan

If issues arise:

1. **Disable tier detection**:
   ```yaml
   # Add to workflow:
   env:
     FORCE_TIER: 4  # Forces all branches to production tier
   ```

2. **Revert workflow changes**:
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

3. **Remove branch protection rules**:
   - Navigate to Settings → Branches
   - Delete or modify protection rules

---

## Monitoring Success

### Key Metrics

1. **CI/CD Times**:
   - Tier 1: Target < 3 min
   - Tier 2: Target < 10 min
   - Tier 3: Target < 30 min
   - Tier 4: Target < 60 min

2. **False Positive Rate**:
   - Track checks that fail but shouldn't
   - Adjust thresholds if >5% false positive rate

3. **Developer Satisfaction**:
   - Survey team on workflow friction
   - Gather feedback on tier appropriateness

4. **Quality Metrics**:
   - Track bugs introduced per tier
   - Monitor production incident rate
   - Compare pre/post implementation

---

## FAQ

**Q: Can I run higher-tier checks on a lower-tier branch?**
A: Yes, use `workflow_dispatch` to manually trigger higher-tier workflows.

**Q: What if my experimental branch needs full testing?**
A: Rename to `feat/` prefix or target `development` branch instead.

**Q: Can we add more tiers?**
A: Yes, but avoid over-complicating. 4 tiers strikes a good balance.

**Q: What about hotfixes?**
A: Create `hotfix/` branches that target `main` directly (tier 4 checks apply).

**Q: How do we handle component promotion?**
A: Component promotion workflows use separate gates defined in `component-promotion-validation.yml`.

---

**Last Updated**: 2025-10-29
**Status**: Ready for implementation
**Estimated Time**: 3 weeks for full rollout
