# Codecov Setup for TTA

This document describes how to set up and use Codecov for the TTA repository.

## Overview

TTA uses [Codecov](https://codecov.io) to track code coverage metrics across the codebase. Coverage reports are automatically generated and uploaded on every push to `main`, `staging`, and on all pull requests.

## Setup Instructions

### 1. Sign up for Codecov

1. Visit [codecov.io](https://codecov.io)
2. Sign in with your GitHub account
3. Authorize Codecov to access the `theinterneti/TTA` repository

### 2. Get Your Upload Token

1. Go to https://app.codecov.io/gh/theinterneti/TTA
2. Navigate to **Settings** → **General**
3. Copy your repository upload token (starts with `981b16ab-...`)

### 3. Add Token to GitHub Secrets

1. Go to your GitHub repository: https://github.com/theinterneti/TTA
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `CODECOV_TOKEN`
5. Value: Paste your upload token from step 2
6. Click **Add secret**

## How It Works

### Automated Coverage Reports

The `.github/workflows/coverage.yml` workflow automatically:

1. ✅ Runs on every push to `main`, `staging`, `develop`
2. ✅ Runs on every pull request
3. ✅ Executes full test suite with coverage measurement
4. ✅ Generates XML coverage report (`coverage.xml`)
5. ✅ Uploads report to Codecov
6. ✅ Comments coverage summary on PRs
7. ✅ Creates HTML coverage artifacts

### Coverage Configuration

The `codecov.yml` file defines:

- **Project Coverage Target**: 70% (aligned with staging promotion)
- **Patch Coverage Target**: 60% (new code in PRs)
- **Component-Specific Targets**:
  - Agent Orchestration: 70%
  - Player Experience: 70%
  - Core Components: 70%
  - Observability: 85% (production-ready)
  - Orchestration: 70%

### Coverage Thresholds (TTA Maturity Workflow)

| Stage | Coverage Requirement | Purpose |
|-------|---------------------|---------|
| **Development** | ≥70% | Ready for staging promotion |
| **Staging** | ≥80% | Production candidate |
| **Production** | ≥85% | Battle-tested, high confidence |

## Using Codecov

### View Coverage Reports

1. **Web Dashboard**: https://app.codecov.io/gh/theinterneti/TTA
2. **PR Comments**: Automatic coverage summary on every pull request
3. **GitHub Checks**: Coverage status checks on PRs
4. **Artifacts**: Download HTML coverage reports from workflow runs

### Reading Coverage Data

#### Overall Coverage
```
Coverage: 28.33%
12,032 / 43,859 statements covered
```

#### Component Coverage
The dashboard shows coverage for each component:
- `src/agent_orchestration/` - 17.88%
- `src/player_experience/` - 56.34%
- `src/observability_integration/` - 75.93% ✅

#### File-Level Coverage
Click any file to see:
- Line-by-line coverage (green = covered, red = not covered)
- Branch coverage for conditionals
- Function/method coverage

### Coverage Badges

Add the Codecov badge to your README:

```markdown
[![codecov](https://codecov.io/gh/theinterneti/TTA/branch/main/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/theinterneti/TTA)
```

## Local Coverage Reports

Generate coverage reports locally:

```bash
# Run tests with coverage
uv run pytest tests/ --cov=src --cov-report=html --cov-report=xml --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# View XML report (for Codecov)
cat coverage.xml
```

## Troubleshooting

### Coverage Not Uploading

1. **Check Token**: Ensure `CODECOV_TOKEN` secret is set correctly
2. **Check Workflow**: View workflow logs in Actions tab
3. **Validate XML**: Ensure `coverage.xml` is generated
4. **Test Locally**: Run `uv run pytest --cov=src --cov-report=xml`

### Low Coverage Warnings

If you see "Coverage decreased" on your PR:

1. **Add Tests**: Write tests for new code
2. **Check Diff**: View the "Coverage Diff" on Codecov
3. **Target Patch Coverage**: Aim for 60%+ on new code
4. **Component Targets**: Follow maturity workflow targets

### Coverage Report Missing

If coverage.xml is not generated:

1. Check pytest-cov is installed: `uv run pip list | grep coverage`
2. Verify pyproject.toml has `[tool.coverage.xml]` section
3. Run tests with explicit XML flag: `pytest --cov-report=xml`

## Integration with TTA Workflows

### Component Promotion

Coverage requirements for component promotion:

```bash
# Development → Staging (70% required)
python scripts/workflow/spec_to_production.py \
  --spec specs/my_component.md \
  --component my_component \
  --target staging

# Staging → Production (80% required)
python scripts/workflow/spec_to_production.py \
  --spec specs/my_component.md \
  --component my_component \
  --target production
```

### Continuous Monitoring

The comprehensive test battery includes coverage checks:

```bash
# View current coverage baseline
cat COVERAGE_BASELINE_REPORT.md

# Track progress
cat CURRENT_STATUS.md
```

## Best Practices

### Writing Testable Code

1. **Small Functions**: Easier to test thoroughly
2. **Pure Functions**: No side effects = easier testing
3. **Dependency Injection**: Mock external dependencies
4. **Clear Interfaces**: Well-defined contracts

### Improving Coverage

1. **Start with High-Value**: Focus on core business logic
2. **Test Edge Cases**: Boundary conditions, error paths
3. **Use Parametrize**: Test multiple scenarios efficiently
4. **Mock External Services**: Don't test external APIs

### Coverage Targets

| Priority | Component | Current | Target | Effort |
|----------|-----------|---------|--------|--------|
| 🥇 Quick Win | orchestration | 68% | 70% | 1-2 days |
| 🥇 Ready Now | observability | 76% | 85% | 1-2 weeks |
| 🥈 High Value | player_experience | 56% | 70% | 2-3 weeks |
| 🥈 Utility | common | 56% | 70% | 3-5 days |
| 🥉 Core Infra | agent_orchestration | 18% | 70% | 4-6 weeks |

See `COVERAGE_BASELINE_REPORT.md` for detailed improvement plan.

## Resources

- **Codecov Docs**: https://docs.codecov.com
- **Coverage.py Docs**: https://coverage.readthedocs.io
- **pytest-cov**: https://pytest-cov.readthedocs.io
- **TTA Coverage Baseline**: `COVERAGE_BASELINE_REPORT.md`
- **TTA Status**: `CURRENT_STATUS.md`

## Support

For Codecov issues:
1. Check [Codecov Support](https://about.codecov.io/support/)
2. Review [GitHub Action Logs](https://github.com/theinterneti/TTA/actions)
3. Contact TTA team for repository-specific questions


---
**Logseq:** [[TTA.dev/Docs/Codecov_setup]]
