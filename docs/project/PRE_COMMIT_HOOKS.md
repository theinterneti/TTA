# Pre-Commit Hooks Guide

This document describes the pre-commit hooks configuration for the TTA project, optimized for our solo developer WSL2 workflow.

## Overview

Pre-commit hooks automatically run quality checks before each commit, catching issues early and maintaining code quality. Our configuration is designed to be:

- **Fast**: Optimized for quick feedback during development
- **Comprehensive**: Covers code quality, security, and formatting
- **Solo-dev friendly**: Easy to bypass when needed, clear error messages
- **WSL2 optimized**: Works seamlessly in our WSL2 environment

## Installation

### 1. Install pre-commit

Pre-commit is included in our dev dependencies:

```bash
# Install all dev dependencies including pre-commit
uv sync --dev

# Or install pre-commit specifically
uv pip install pre-commit
```

### 2. Install the git hooks

```bash
# Install pre-commit hooks into .git/hooks/
uv run pre-commit install

# Also install commit-msg hook for conventional commits
uv run pre-commit install --hook-type commit-msg
```

### 3. (Optional) Run on all files

```bash
# Run all hooks on all files (useful for initial setup)
uv run pre-commit run --all-files
```

## Configured Hooks

### 🧹 Code Quality & Formatting

#### **Ruff** (Primary Linter & Formatter)
- **What**: Modern, fast Python linter and formatter
- **When**: On every commit
- **Speed**: ⚡ Very fast (Rust-based)
- **Auto-fix**: Yes
- **Config**: `pyproject.toml` → `[tool.ruff]`

#### **Black** (Code Formatter)
- **What**: Opinionated Python code formatter
- **When**: On every commit
- **Speed**: ⚡ Fast
- **Auto-fix**: Yes
- **Config**: Line length 88

#### **isort** (Import Sorter)
- **What**: Sorts and organizes imports
- **When**: On every commit
- **Speed**: ⚡ Fast
- **Auto-fix**: Yes
- **Config**: Black-compatible profile

### 🔒 Security

#### **Bandit** (Security Scanner)
- **What**: Finds common security issues in Python code
- **When**: On every commit
- **Speed**: ⚡ Fast
- **Scope**: `src/` directory only (excludes tests)
- **Output**: `bandit-report.json`

#### **detect-secrets** (Secret Detection)
- **What**: Prevents committing secrets, API keys, passwords
- **When**: On every commit
- **Speed**: ⚡ Fast
- **Baseline**: `.secrets.baseline`
- **What it catches**:
  - API keys and tokens
  - Private keys
  - Passwords in code
  - AWS credentials
  - Database connection strings

### ✅ File Validation

#### **Built-in Hooks**
- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with newline
- **check-yaml**: Validates YAML syntax
- **check-toml**: Validates TOML syntax
- **check-json**: Validates JSON syntax
- **check-added-large-files**: Prevents files >1000KB
- **check-merge-conflict**: Detects merge conflict markers
- **check-case-conflict**: Prevents case-sensitive filename conflicts
- **debug-statements**: Catches leftover `print()` and `pdb` statements

### 🧪 Test Quality

#### **pytest-asyncio Fixture Validator** (Custom Hook)
- **What**: Ensures async fixtures use `@pytest_asyncio.fixture`
- **When**: On every commit (test files only)
- **Speed**: ⚡ Very fast
- **Why**: Prevents pytest-asyncio deprecation warnings
- **Script**: `scripts/pre-commit/check-pytest-asyncio-fixtures.py`

#### **name-tests-test**
- **What**: Ensures test files follow naming convention
- **Pattern**: `test_*.py` or `*_test.py`

### 📝 Commit Messages

#### **Conventional Commits**
- **What**: Enforces conventional commit message format
- **When**: On commit-msg hook
- **Format**: `<type>(<scope>): <description>`
- **Types**: feat, fix, docs, chore, test, refactor, perf, ci, build, style
- **Example**: `feat(api): add user authentication endpoint`

### 🎨 Documentation

#### **pydocstyle** (Docstring Checker)
- **What**: Validates Python docstrings
- **Convention**: Google style
- **Scope**: `src/` only (excludes tests)
- **Mode**: Warning only (non-blocking)

#### **MyPy** (Type Checker)
- **What**: Static type checking
- **When**: On every commit
- **Speed**: 🐢 Can be slow on large changes
- **Scope**: `src/` only (excludes tests, docs, scripts)
- **Config**: Lenient settings for development

## Usage

### Normal Workflow

Pre-commit hooks run automatically on `git commit`:

```bash
# Make your changes
git add .

# Hooks run automatically
git commit -m "feat: add new feature"

# If hooks fail, fix issues and try again
# Many hooks auto-fix issues, so just re-stage and commit
git add .
git commit -m "feat: add new feature"
```

### Bypassing Hooks

Sometimes you need to commit without running hooks (use sparingly):

```bash
# Skip all pre-commit hooks
git commit --no-verify -m "wip: work in progress"

# Or use the shorthand
git commit -n -m "wip: work in progress"
```

**When to bypass:**
- Work-in-progress commits on feature branches
- Emergency hotfixes (but run hooks before pushing!)
- When hooks are failing due to infrastructure issues

### Running Hooks Manually

```bash
# Run all hooks on staged files
uv run pre-commit run

# Run all hooks on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files
uv run pre-commit run detect-secrets --all-files

# Run hooks on specific files
uv run pre-commit run --files src/agent_orchestration/*.py
```

### Updating Hooks

```bash
# Update all hooks to latest versions
uv run pre-commit autoupdate

# Update and run on all files
uv run pre-commit autoupdate && uv run pre-commit run --all-files
```

## Configuration Files

### `.pre-commit-config.yaml`
Main configuration file defining all hooks, versions, and settings.

### `.secrets.baseline`
Baseline file for detect-secrets. Contains known false positives.

To update the baseline:
```bash
uv run detect-secrets scan > .secrets.baseline
```

### `pyproject.toml`
Contains configuration for:
- Ruff (`[tool.ruff]`)
- Black (`[tool.black]`)
- isort (`[tool.isort]`)
- MyPy (`[tool.mypy]`)

## Troubleshooting

### Hooks are slow

**MyPy** can be slow on large changes. Options:
1. Skip MyPy temporarily: `SKIP=mypy git commit -m "..."`
2. Run MyPy separately: `uv run mypy src/`
3. Disable MyPy in `.pre-commit-config.yaml` if not needed

### False positive in secret detection

Add to `.secrets.baseline`:
```bash
uv run detect-secrets scan > .secrets.baseline
```

### Hook fails but I can't see why

Run the hook manually with verbose output:
```bash
uv run pre-commit run <hook-id> --verbose --all-files
```

### Hooks not running

Ensure hooks are installed:
```bash
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

Check `.git/hooks/pre-commit` exists and is executable.

### WSL2-specific issues

If hooks fail with permission errors:
```bash
# Make hook scripts executable
chmod +x scripts/pre-commit/*.py

# Reinstall hooks
uv run pre-commit uninstall
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

## Performance Tips

1. **Stage only what you need**: Hooks run on staged files only
2. **Use `--no-verify` for WIP commits**: Run hooks before final commit
3. **Skip slow hooks**: `SKIP=mypy git commit -m "..."`
4. **Run hooks in parallel**: Pre-commit does this automatically
5. **Keep hooks updated**: `uv run pre-commit autoupdate`

## Integration with Development Workflow

### Daily Development
```bash
# 1. Make changes
vim src/agent_orchestration/workflow_manager.py

# 2. Stage changes
git add src/agent_orchestration/workflow_manager.py

# 3. Commit (hooks run automatically)
git commit -m "refactor: improve workflow manager performance"

# 4. If hooks auto-fix issues, re-stage and commit
git add src/agent_orchestration/workflow_manager.py
git commit -m "refactor: improve workflow manager performance"
```

### Before Pushing
```bash
# Run all hooks on all files to ensure everything passes
uv run pre-commit run --all-files

# If all pass, push
git push origin main
```

### CI/CD Integration
Pre-commit hooks also run in CI/CD (GitHub Actions) to ensure consistency.

## Customization

To add or modify hooks, edit `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/your/hook-repo
    rev: v1.0.0
    hooks:
      - id: your-hook-id
        args: [--your-arg]
```

Then update:
```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## Summary

Our pre-commit setup provides:
- ✅ Automatic code quality checks
- ✅ Security scanning
- ✅ Consistent formatting
- ✅ Fast feedback loop
- ✅ Easy to bypass when needed
- ✅ WSL2 optimized
- ✅ Solo developer friendly

For questions or issues, refer to the [pre-commit documentation](https://pre-commit.com/).
