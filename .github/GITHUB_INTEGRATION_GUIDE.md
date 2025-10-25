# GitHub Integration Guide for TTA

This guide covers the complete GitHub integration setup for the Therapeutic Text Adventure (TTA) project, including UV environment management, VS Code configuration, and CI/CD workflows.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [UV Environment Setup](#uv-environment-setup)
- [VS Code Configuration](#vs-code-configuration)
- [Git Workflow](#git-workflow)
- [GitHub Actions](#github-actions)
- [Branch Strategy](#branch-strategy)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/theinterneti/TTA.git
cd TTA

# 2. Setup UV environment
uv sync --all-extras --dev

# 3. Activate VS Code Python interpreter
# In VS Code: Ctrl+Shift+P → "Python: Select Interpreter" → Choose .venv/bin/python

# 4. Verify setup
uv run pytest --version
git status
```

## 🐍 UV Environment Setup

### Current Configuration

- **Python Version**: 3.12 (managed by `.python-version`)
- **Environment Location**: `.venv/` (uv-managed)
- **Lock File**: `uv.lock` (tracks exact dependencies)
- **Staging Environment**: `venv-staging/` (separate environment for staging tests)

### Environment Commands

```bash
# Create/sync environment (recommended)
uv sync --all-extras --dev

# Sync minimal dependencies
uv sync

# Sync with test dependencies only
uv sync --group test

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade

# Show installed packages
uv pip list

# Run commands in the environment
uv run pytest
uv run python script.py
uv run ruff check .
```

### Environment Variables

Key environment variables for development:

```bash
# Testing
export RUN_NEO4J_TESTS=1
export RUN_REDIS_TESTS=1
export TEST_NEO4J_URI="bolt://localhost:7687"
export TEST_REDIS_URI="redis://localhost:6379/0"

# Monitoring
export PROMETHEUS_ENABLED=true
export GRAFANA_ENABLED=true
export TTA_METRICS_ENABLED=true

# AI/LLM
export OPENROUTER_API_KEY="your-key-here"
```

### .gitignore Configuration

The following are ignored by git (already configured):

```
# Virtual environments
.venv/
venv/
venv-staging/
.python-version

# Test artifacts
.pytest_cache/
htmlcov/
coverage.xml
test-results/
*_test_results*.json

# Build artifacts
dist/
build/
*.egg-info/
```

## 💻 VS Code Configuration

### Current Setup

Your VS Code is already configured in `.vscode/settings.json` with:

- ✅ Python interpreter: `.venv/bin/python`
- ✅ Pytest integration with auto-discovery
- ✅ Coverage gutters for visual coverage
- ✅ Pylance language server with type checking
- ✅ Proper exclusions for virtual environments

### Recommended Extensions

Install these VS Code extensions:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "ms-python.pytest",
    "ryanluker.vscode-coverage-gutters",
    "github.vscode-github-actions",
    "eamodio.gitlens",
    "donjayamanne.githistory"
  ]
}
```

### Source Control Settings

Add to `.vscode/settings.json` for better git integration:

```json
{
  "git.autofetch": true,
  "git.enableSmartCommit": true,
  "git.confirmSync": false,
  "git.pruneOnFetch": true,
  "gitlens.hovers.currentLine.over": "line",
  "gitlens.currentLine.enabled": false,
  "scm.defaultViewMode": "tree"
}
```

### Testing in VS Code

1. **Discover Tests**: Click the "Testing" icon in the sidebar (beaker icon)
2. **Run Tests**: Click the play button next to any test
3. **Debug Tests**: Click the debug icon next to any test
4. **View Coverage**: After running tests with coverage, click "Watch" in the status bar

### Tasks Configuration

The `.vscode/tasks.json` includes useful commands:

- `Ctrl+Shift+B` → Build/Run default task
- Run tests with coverage
- Lint with ruff
- Type check with pyright

## 🌿 Git Workflow

### Branch Strategy

```
main (production)
├── staging (pre-production)
│   └── development (integration)
│       ├── feature/mvp-implementation
│       ├── feature/agentic-primitives-phase1
│       └── feat/production-deployment-infrastructure
```

### Branch Naming Convention

- `feature/*` - New features
- `feat/*` - Feature work (alternative)
- `fix/*` - Bug fixes
- `docs/*` - Documentation
- `test/*` - Test improvements
- `refactor/*` - Code refactoring
- `chore/*` - Maintenance tasks

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `chore`: Maintenance
- `ci`: CI/CD changes

Examples:
```bash
git commit -m "feat(auth): add JWT token refresh"
git commit -m "fix(api): resolve Neo4j connection timeout"
git commit -m "test(orchestration): add circuit breaker tests"
git commit -m "docs: update GitHub integration guide"
```

### Daily Workflow

```bash
# Start of day - update your branch
git checkout development
git pull origin development
git checkout feature/your-feature
git rebase development

# During work - commit frequently
git add .
git commit -m "feat: add new functionality"

# Push to remote
git push origin feature/your-feature

# End of day - create PR if ready
gh pr create --base development --title "feat: your feature" --body "Description"
```

### Useful Git Commands

```bash
# View status
git status
git diff

# View commit history
git log --oneline --graph --all

# Stash changes
git stash
git stash pop

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo changes to a file
git checkout -- filename

# Update from remote
git fetch --all --prune
git pull --rebase

# Clean up merged branches
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d
```

## ⚙️ GitHub Actions

### Workflow Files

Located in `.github/workflows/`:

- `tests.yml` - Unit & integration tests (runs on push/PR)
- `code-quality.yml` - Linting and type checking
- `docker-build.yml` - Docker image builds
- `deploy-staging.yml` - Staging deployment
- `deploy-production.yml` - Production deployment
- `security-scan.yml` - Security scanning
- `e2e-tests.yml` - End-to-end tests

### Tests Workflow Details

The main test workflow (`tests.yml`) includes:

1. **Unit Tests**:
   - Runs on: all branches
   - Uses: `uv sync --group test`
   - Coverage: `--cov=src --cov-report=xml`
   - Matrix: Python 3.12

2. **Integration Tests**:
   - Runs on: main, staging, development (not on feature branches)
   - Services: Neo4j 5, Redis 7
   - Environment variables for test databases

3. **Monitoring Validation**:
   - Runs after tests pass
   - Validates Prometheus & Grafana setup
   - Performance regression detection

### Running Locally to Match CI

```bash
# Unit tests (like CI)
uv run pytest -q --tb=short \
  --junitxml=test-results/unit-tests.xml \
  --cov=src --cov-report=xml:coverage.xml

# Integration tests (like CI - requires Docker)
docker compose up -d neo4j redis
uv run pytest -q --neo4j --redis --tb=short
docker compose down

# Full test battery
uv run pytest --cov=src --cov-report=html --cov-report=xml
```

### Workflow Secrets

Configure these in GitHub Settings → Secrets:

- `OPENROUTER_API_KEY` - For AI/LLM tests
- `NEO4J_PASSWORD` - Neo4j database password
- `GRAFANA_ADMIN_PASSWORD` - Grafana admin password
- `DOCKER_HUB_USERNAME` & `DOCKER_HUB_TOKEN` - For Docker builds

### Viewing Workflow Results

```bash
# View workflow runs
gh run list

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id> --failed
```

## 🔄 Branch Strategy

### Current Branches

- **main** - Production-ready code
- **staging** - Pre-production testing
- **development** - Integration branch for features
- **feature/mvp-implementation** - Your current working branch
- **feature/agentic-primitives-phase1** - Agentic primitives work

### Merge Strategy

1. **Feature → Development**:
   - Create PR when feature is complete
   - Requires: passing tests, code review
   - Merge: Squash and merge

2. **Development → Staging**:
   - Weekly or when ready for testing
   - Requires: all tests passing
   - Merge: Merge commit (preserve history)

3. **Staging → Main**:
   - After successful staging validation
   - Requires: approval from maintainers
   - Merge: Merge commit
   - Triggers: production deployment

### PR Templates

Use `.github/pull_request_template.md` for consistent PRs:

```markdown
## Description
<!-- Describe your changes -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

## 🔧 Troubleshooting

### VS Code Can't Find Interpreter

```bash
# 1. Verify .venv exists
ls -la .venv/bin/python

# 2. Recreate if needed
rm -rf .venv
uv sync --all-extras --dev

# 3. In VS Code: Ctrl+Shift+P → "Python: Select Interpreter"
# Choose: .venv/bin/python
```

### Pytest Not Discovering Tests

```bash
# 1. Check pytest is in .venv
uv run pytest --version

# 2. Verify settings.json has correct paths
# Should have: "python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest"

# 3. Reload VS Code window
# Ctrl+Shift+P → "Developer: Reload Window"
```

### Git Remote Issues

```bash
# Check remote configuration
git remote -v

# Should show:
# TTA	https://github.com/theinterneti/TTA.git (fetch)
# TTA	https://github.com/theinterneti/TTA.git (push)

# Fix if incorrect
git remote set-url TTA https://github.com/theinterneti/TTA.git
```

### UV Lock File Conflicts

```bash
# After merge conflicts in uv.lock
uv sync --upgrade

# Or regenerate completely
rm uv.lock
uv sync --all-extras --dev
```

### CI Tests Pass But Local Tests Fail

```bash
# 1. Ensure clean environment
rm -rf .venv
uv sync --all-extras --dev

# 2. Clear pytest cache
rm -rf .pytest_cache

# 3. Run with same flags as CI
uv run pytest -q --tb=short --cov=src

# 4. Check environment variables
env | grep -E "TEST_|TTA_|NEO4J|REDIS"
```

### GitHub Actions Not Triggering

```yaml
# Verify workflow file syntax
gh workflow view tests.yml

# Check workflow runs
gh run list --workflow=tests.yml

# View workflow file
cat .github/workflows/tests.yml
```

## 📚 Additional Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [VS Code Python Documentation](https://code.visualstudio.com/docs/python/python-tutorial)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub CLI Documentation](https://cli.github.com/manual/)

## 🎯 Quick Reference Card

```bash
# Environment
uv sync --all-extras --dev    # Setup environment
uv run pytest                 # Run tests
uv pip list                   # List packages

# Git
git status                    # Check status
git add .                     # Stage changes
git commit -m "msg"          # Commit
git push                      # Push to remote
gh pr create                  # Create PR

# VS Code
Ctrl+Shift+P                 # Command palette
Ctrl+`                       # Terminal
Ctrl+Shift+B                 # Build/Run task
```

## 📝 Notes

- Always work in a feature branch
- Keep commits small and focused
- Write descriptive commit messages
- Update tests with code changes
- Run tests before pushing
- Keep `uv.lock` committed to git
- Don't commit `.venv/` or test artifacts
