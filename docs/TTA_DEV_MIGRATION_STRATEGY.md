# TTA.dev Migration Strategy

**Date:** 2025-10-27
**Status:** 🎯 READY FOR EXECUTION
**Target Repo:** https://github.com/theinterneti/TTA.dev
**Approach:** Trunk-Based Development with GitHub Flow

---

## Executive Summary

This document outlines a rigorous, professional approach to packaging proven agentic development components from the TTA repository into a clean, production-ready TTA.dev repository. **Only battle-tested, proven components will be migrated.**

### Core Principles

1. **Proven Only** - Components must have:
   - ✅ 12+ passing tests (100% pass rate)
   - ✅ Production documentation
   - ✅ Real-world usage validation
   - ✅ Zero known critical bugs

2. **Clean History** - Trunk-based development:
   - Short-lived feature branches (max 2-3 days)
   - Squash merges to main
   - Semantic commit messages
   - No WIP commits in main

3. **Professional Standards**:
   - Strict .gitignore (no build artifacts, secrets, or temp files)
   - Mandatory PR reviews (even for solo dev)
   - GitHub Actions for CI/CD
   - Comprehensive documentation

4. **VS Code Native**:
   - Copilot-powered workflows
   - Task definitions for all operations
   - Extension recommendations
   - Workspace-aware tooling

---

## Phase 1: Repository Setup (Day 1)

### 1.1 Initialize TTA.dev Repository

```bash
# Clone the new repo
cd ~/repos
git clone https://github.com/theinterneti/TTA.dev
cd TTA.dev

# Set up main branch protection (via GitHub UI)
# - Require PR before merge
# - Require status checks
# - No direct commits to main
```

### 1.2 Create Professional .gitignore

**Strategy:** Start with comprehensive Python + Node.js + VS Code ignore patterns

```gitignore
# === Python ===
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/

# Testing
.pytest_cache/
.coverage
htmlcov/
*.log

# Type checking & linting
.mypy_cache/
.ruff_cache/
.pyright/

# === Node.js ===
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Build outputs
dist/
build/
*.tsbuildinfo

# === VS Code ===
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/extensions.json
!.vscode/launch.json

# === Environment & Secrets ===
.env
.env.local
.env.*.local
*.pem
*.key
secrets/

# === OS ===
.DS_Store
Thumbs.db
*~

# === Project-Specific ===
# Logs
logs/
*.log

# Temporary files
tmp/
temp/
.tmp/

# Documentation builds
site/
docs/_build/

# Coverage reports
coverage/
.nyc_output/

# Lock files (we'll commit these)
!uv.lock
!package-lock.json
```

### 1.3 Create Repository Structure

```
TTA.dev/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # CI pipeline
│   │   ├── quality-check.yml   # Linting, type checking
│   │   └── publish.yml         # Package publishing
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── CODEOWNERS
│
├── packages/
│   ├── tta-workflow-primitives/
│   ├── dev-primitives/
│   └── tta-ai-framework/
│
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   └── architecture.md
│
├── scripts/
│   └── validate-package.sh
│
├── .vscode/
│   ├── settings.json
│   ├── tasks.json
│   ├── extensions.json
│   └── launch.json
│
├── .gitignore
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── pyproject.toml
```

---

## Phase 2: Package Migration (Days 2-3)

### 2.1 Proven Components for Migration

Based on inventory analysis, these components are **proven and ready**:

#### ✅ Tier 1: Battle-Tested (Migrate First)

| Component | Evidence | Tests | Status |
|-----------|----------|-------|--------|
| `tta-workflow-primitives` | 12/12 tests passing, production docs | ✅ 100% | READY |
| `dev-primitives` | Used in real workflows, validated | ✅ 100% | READY |

#### ✅ Tier 2: Proven with Usage (Migrate Second)

| Component | Evidence | Tests | Status |
|-----------|----------|-------|--------|
| `.github/instructions/*.instructions.md` | Used by agents, validated patterns | N/A | READY |
| Monitoring stack (observability/) | Production-ready dashboards | ✅ Manual | READY |

#### 🔄 Tier 3: Mature but Needs Validation

| Component | Evidence | Tests | Status |
|-----------|----------|-------|--------|
| AI Context Manager | Used successfully, needs more tests | ⚠️ Partial | REVIEW |
| Workflow orchestration scripts | Working but not fully tested | ⚠️ Partial | REVIEW |

#### ❌ NOT READY for TTA.dev

- TTA application code (game-specific)
- Experimental features
- Augment-specific chatmodes (until generalized)
- Anything without tests

### 2.2 Migration Workflow (Per Package)

**Branch Strategy:**
```
main (protected)
  └── feature/add-workflow-primitives (short-lived, 1-2 days max)
```

**Process:**
```bash
# 1. Create feature branch
git checkout -b feature/add-workflow-primitives

# 2. Copy proven component (clean extraction)
rsync -av --exclude='__pycache__' \
  ~/recovered-tta-storytelling/packages/tta-workflow-primitives/ \
  ./packages/tta-workflow-primitives/

# 3. Clean and validate
rm -rf packages/tta-workflow-primitives/__pycache__
rm -rf packages/tta-workflow-primitives/**/*.pyc

# 4. Run quality checks
uv run ruff check packages/tta-workflow-primitives/
uv run ruff format packages/tta-workflow-primitives/
uvx pyright packages/tta-workflow-primitives/

# 5. Run tests
uv run pytest packages/tta-workflow-primitives/tests/ -v

# 6. Commit with semantic message
git add packages/tta-workflow-primitives/
git commit -m "feat: Add tta-workflow-primitives package

- Add composable workflow primitives
- Include router, cache, timeout, retry patterns
- Add comprehensive test suite (12 tests, 100% pass)
- Add production documentation
- Supports 30-40% cost reduction via caching

Tested-by: pytest (12/12 passing)
Documented-in: packages/tta-workflow-primitives/README.md"

# 7. Push and create PR
git push origin feature/add-workflow-primitives
gh pr create --title "feat: Add tta-workflow-primitives package" \
  --body "$(cat .github/PULL_REQUEST_TEMPLATE.md)"
```

---

## Phase 3: GitHub Flow + Trunk-Based Development

### 3.1 Branch Strategy

**Main Branch (Protected):**
- Only clean, squashed commits
- All commits must pass CI
- Semantic commit messages
- Linear history

**Feature Branches:**
- Short-lived (max 2-3 days)
- Named: `feature/`, `fix/`, `docs/`, `chore/`
- One logical change per branch
- Squash merge to main

**Hotfix Branches:**
- Critical fixes only
- Named: `hotfix/`
- Immediate merge after review

### 3.2 Commit Message Standards

Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change that neither fixes bug nor adds feature
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat(primitives): Add timeout primitive with configurable strategies

- Implement TimeoutPrimitive with sync/async support
- Add configurable timeout strategies (fail-fast, graceful)
- Include comprehensive error messages
- Add 4 test cases covering edge cases

Breaking-change: None
Tested-by: pytest (4/4 passing)
Closes: #12
```

### 3.3 Pull Request Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description
<!-- Clear description of what this PR does -->

## Type of Change
- [ ] feat: New feature
- [ ] fix: Bug fix
- [ ] docs: Documentation update
- [ ] refactor: Code refactoring
- [ ] test: Test additions/improvements
- [ ] chore: Maintenance

## Checklist
- [ ] Code follows project style guidelines (Ruff, Pyright)
- [ ] Self-review completed
- [ ] Tests added/updated (if applicable)
- [ ] All tests passing locally
- [ ] Documentation updated (if applicable)
- [ ] No secrets or sensitive data included
- [ ] Commit messages follow Conventional Commits

## Testing
<!-- Describe testing performed -->
- [ ] Unit tests: X/X passing
- [ ] Integration tests: X/X passing
- [ ] Manual testing: Describe what you tested

## Related Issues
Closes #

## Breaking Changes
<!-- List any breaking changes or write "None" -->

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->
```

---

## Phase 4: CI/CD Pipeline

### 4.1 Quality Check Workflow

Create `.github/workflows/quality-check.yml`:

```yaml
name: Quality Checks

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run Ruff (format check)
        run: uv run ruff format --check .

      - name: Run Ruff (lint)
        run: uv run ruff check .

      - name: Run Pyright
        run: uvx pyright packages/

      - name: Run tests
        run: uv run pytest --cov=packages --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### 4.2 CI Pipeline

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest -v
```

---

## Phase 5: VS Code Integration

### 5.1 Workspace Settings

Create `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit",
    "source.fixAll": "explicit"
  },

  "python.analysis.typeCheckingMode": "basic",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,

  "ruff.enable": true,
  "ruff.lint.run": "onSave",
  "ruff.format.args": ["--line-length=88"],

  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },

  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true
  },

  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "plaintext": false,
    "markdown": true
  }
}
```

### 5.2 Tasks Configuration

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "🧪 Run All Tests",
      "type": "shell",
      "command": "uv run pytest -v",
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "✨ Format Code",
      "type": "shell",
      "command": "uv run ruff format .",
      "group": "build",
      "presentation": {
        "reveal": "silent"
      }
    },
    {
      "label": "🔍 Lint Code",
      "type": "shell",
      "command": "uv run ruff check . --fix",
      "group": "build"
    },
    {
      "label": "🔬 Type Check",
      "type": "shell",
      "command": "uvx pyright packages/",
      "group": "build"
    },
    {
      "label": "✅ Quality Check (All)",
      "type": "shell",
      "command": "uv run ruff format . && uv run ruff check . --fix && uvx pyright packages/ && uv run pytest",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "📦 Validate Package",
      "type": "shell",
      "command": "./scripts/validate-package.sh ${input:packageName}",
      "group": "build"
    }
  ],
  "inputs": [
    {
      "id": "packageName",
      "type": "promptString",
      "description": "Package name to validate"
    }
  ]
}
```

### 5.3 Extension Recommendations

Create `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "github.copilot",
    "github.copilot-chat",
    "charliermarsh.ruff",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.debugpy",
    "ms-azuretools.vscode-docker",
    "eamodio.gitlens",
    "usernamehw.errorlens",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml"
  ]
}
```

---

## Phase 6: Documentation Standards

### 6.1 README.md Structure

```markdown
# TTA.dev - AI Development Toolkit

**Production-ready agentic primitives and workflow patterns for building reliable AI applications.**

[![CI](https://github.com/theinterneti/TTA.dev/workflows/CI/badge.svg)](https://github.com/theinterneti/TTA.dev/actions)
[![codecov](https://codecov.io/gh/theinterneti/TTA.dev/branch/main/graph/badge.svg)](https://codecov.io/gh/theinterneti/TTA.dev)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Features

- 🎯 **Workflow Primitives** - Composable patterns for agent workflows
- 🔧 **Dev Utilities** - Development and debugging tools
- 📊 **Observability** - Built-in monitoring and metrics
- ✅ **Battle-Tested** - 100% test coverage, production-validated

## Quick Start

\`\`\`bash
# Install
pip install tta-workflow-primitives

# Use
from tta_workflow_primitives import RouterPrimitive, CachePrimitive

workflow = RouterPrimitive(...) >> CachePrimitive(...)
\`\`\`

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api/)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)
```

### 6.2 Package Documentation Requirements

Each package must have:

1. **README.md** with:
   - Purpose and features
   - Installation instructions
   - Quick start example
   - API overview
   - Links to full docs

2. **CHANGELOG.md** following Keep a Changelog format

3. **API documentation** (docstrings + generated docs)

4. **Examples** directory with runnable code

---

## Phase 7: Migration Execution Plan

### Week 1: Setup and First Package

**Day 1: Repository Setup**
- [ ] Create TTA.dev repository
- [ ] Set up branch protection
- [ ] Add .gitignore
- [ ] Create directory structure
- [ ] Add CI/CD workflows
- [ ] Configure VS Code workspace

**Day 2: First Package Migration**
- [ ] Create feature branch: `feature/add-workflow-primitives`
- [ ] Migrate `tta-workflow-primitives`
- [ ] Clean and validate
- [ ] Run all tests
- [ ] Update documentation
- [ ] Create PR

**Day 3: Review and Merge**
- [ ] Self-review PR
- [ ] Run CI checks
- [ ] Squash merge to main
- [ ] Verify main branch
- [ ] Tag release: `v0.1.0`

### Week 2: Additional Packages

**Day 4-5: dev-primitives**
- [ ] Migrate `dev-primitives`
- [ ] Same process as above

**Day 6-7: Instructions and Documentation**
- [ ] Migrate `.github/instructions/`
- [ ] Generalize for cross-platform
- [ ] Create universal `AGENTS.md`

---

## Phase 8: Quality Gates

### 8.1 Pre-Merge Checklist

Every PR must pass:

✅ **Code Quality**
- [ ] Ruff format check passes
- [ ] Ruff lint check passes
- [ ] Pyright type check passes
- [ ] No hardcoded secrets or paths

✅ **Testing**
- [ ] All tests passing (100%)
- [ ] New tests added for new features
- [ ] Coverage maintained (>80%)

✅ **Documentation**
- [ ] README updated
- [ ] API docs updated
- [ ] CHANGELOG updated
- [ ] Examples provided

✅ **Git Hygiene**
- [ ] Semantic commit messages
- [ ] No merge commits in branch
- [ ] PR template filled out
- [ ] Breaking changes documented

✅ **Security**
- [ ] No secrets committed
- [ ] No sensitive data
- [ ] Dependencies reviewed

### 8.2 Package Validation Script

Create `scripts/validate-package.sh`:

```bash
#!/bin/bash
set -e

PACKAGE=$1

if [ -z "$PACKAGE" ]; then
  echo "Usage: ./scripts/validate-package.sh <package-name>"
  exit 1
fi

echo "🔍 Validating package: $PACKAGE"
echo ""

echo "📦 Checking structure..."
[ -f "packages/$PACKAGE/pyproject.toml" ] || { echo "❌ Missing pyproject.toml"; exit 1; }
[ -f "packages/$PACKAGE/README.md" ] || { echo "❌ Missing README.md"; exit 1; }
[ -d "packages/$PACKAGE/tests" ] || { echo "❌ Missing tests directory"; exit 1; }

echo "✅ Structure valid"
echo ""

echo "✨ Running formatter..."
uv run ruff format packages/$PACKAGE/
echo "✅ Format complete"
echo ""

echo "🔍 Running linter..."
uv run ruff check packages/$PACKAGE/ --fix
echo "✅ Lint complete"
echo ""

echo "🔬 Running type checker..."
uvx pyright packages/$PACKAGE/
echo "✅ Type check complete"
echo ""

echo "🧪 Running tests..."
uv run pytest packages/$PACKAGE/tests/ -v
echo "✅ Tests complete"
echo ""

echo "🎉 Package validation complete!"
```

---

## Phase 9: Copilot Integration

### 9.1 Copilot-Friendly Workflow

**In VS Code:**

1. **Use Copilot Chat for planning:**
   ```
   @workspace How should I structure the next package migration?
   ```

2. **Use Copilot for boilerplate:**
   - Open new file
   - Start typing docstring
   - Let Copilot suggest structure

3. **Use GitHub Copilot CLI:**
   ```bash
   # Suggest git commands
   gh copilot suggest "commit these changes with semantic message"

   # Explain commands
   gh copilot explain "git rebase -i HEAD~3"
   ```

### 9.2 Copilot Instructions

Create `.github/copilot-instructions.md`:

```markdown
# Copilot Instructions for TTA.dev

## Code Style
- Use Ruff for formatting (88 char lines)
- Type hints required for all functions
- Google-style docstrings
- Async-first where applicable

## Testing
- Use pytest with AAA pattern
- Mock external dependencies
- Aim for >80% coverage

## Commits
- Follow Conventional Commits
- Squash before merging
- Include test evidence in commit body

## Documentation
- Update README for public APIs
- Add examples for new features
- Keep CHANGELOG current
```

---

## Phase 10: Maintenance and Growth

### 10.1 Release Strategy

**Semantic Versioning:**
- `v0.x.x` - Pre-1.0, breaking changes allowed
- `v1.0.0` - First stable release
- `v1.x.0` - New features (backward compatible)
- `v1.0.x` - Bug fixes

**Release Process:**
```bash
# 1. Update CHANGELOG
# 2. Bump version in pyproject.toml
# 3. Commit
git commit -m "chore: Bump version to 0.2.0"

# 4. Tag
git tag -a v0.2.0 -m "Release v0.2.0 - Add caching primitives"

# 5. Push
git push origin main --tags

# 6. Publish (automated via GitHub Actions)
```

### 10.2 Monitoring Repository Health

**Weekly checks:**
- [ ] All CI/CD passing
- [ ] No stale PRs (>7 days)
- [ ] Dependencies up to date
- [ ] Issues triaged
- [ ] Documentation current

**Monthly:**
- [ ] Review test coverage
- [ ] Update dependencies
- [ ] Review GitHub Insights
- [ ] Plan next package migrations

---

## Success Criteria

### Repository Health
- ✅ 100% CI passing rate
- ✅ All packages have >80% test coverage
- ✅ Zero critical security vulnerabilities
- ✅ Clean, linear git history

### Developer Experience
- ✅ VS Code workflow is smooth
- ✅ Copilot provides helpful suggestions
- ✅ Tasks work without manual commands
- ✅ Documentation is clear and complete

### Code Quality
- ✅ All code passes Ruff + Pyright
- ✅ No secrets or sensitive data
- ✅ Consistent style throughout
- ✅ Type-safe APIs

### Community Ready
- ✅ README is professional
- ✅ Examples are runnable
- ✅ Contributing guide is clear
- ✅ License is appropriate

---

## Lessons from Previous Failure

### What Went Wrong Before
1. Tried to migrate everything at once
2. Didn't enforce quality gates
3. Allowed dirty git history
4. No clear "done" criteria

### How We're Fixing It
1. ✅ Migrate one package at a time
2. ✅ Strict PR process with quality checks
3. ✅ Squash merges only to main
4. ✅ Clear validation checklist per package

---

## Next Steps

1. **Review this plan** - Make sure it's achievable
2. **Set up repository** - Follow Phase 1
3. **Migrate first package** - Start with `tta-workflow-primitives`
4. **Iterate** - Learn and improve process
5. **Document learnings** - Update this guide

---

## Appendix: Command Cheatsheet

```bash
# Setup
git clone https://github.com/theinterneti/TTA.dev
cd TTA.dev

# Create feature branch
git checkout -b feature/add-new-package

# Quality checks
uv run ruff format .
uv run ruff check . --fix
uvx pyright packages/
uv run pytest -v

# Commit
git add .
git commit -m "feat(package): Add description"

# Create PR
gh pr create --title "feat: ..." --body "..."

# After merge, cleanup
git checkout main
git pull
git branch -d feature/add-new-package

# Tag release
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-27
**Maintained By:** @theinterneti
**Status:** 🎯 READY FOR EXECUTION


---
**Logseq:** [[TTA.dev/Docs/Tta_dev_migration_strategy]]
