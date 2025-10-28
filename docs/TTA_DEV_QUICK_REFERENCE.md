# TTA.dev Quick Reference Guide

**Your simple guide to working with TTA.dev using VS Code + Copilot**

---

## Daily Workflow

### 1. Starting Work on a Feature

```bash
# Pull latest changes
git checkout main
git pull origin main

# Create feature branch (max 2-3 days of work!)
git checkout -b feature/add-awesome-feature

# Start coding!
```

### 2. Making Changes

**In VS Code:**

1. Open file
2. Let Copilot help you write code
3. Save (auto-formats with Ruff)
4. VS Code Tasks menu → Run "Quality Check (All)"

**Or use keyboard shortcuts:**
- `Cmd/Ctrl+Shift+B` → Run build task (quality check)
- `Cmd/Ctrl+Shift+P` → Task menu

### 3. Before Committing

**Run the quality check:**

```bash
# Option 1: VS Code Task
# Press Cmd/Ctrl+Shift+P, type "Task: Run Task"
# Select "✅ Quality Check (All)"

# Option 2: Terminal
uv run ruff format .
uv run ruff check . --fix
uvx pyright packages/
uv run pytest -v
```

**All green? Great! Commit:**

```bash
git add .
git commit -m "feat(primitives): Add awesome feature

- Describe what you added
- Why you added it
- Any breaking changes

Tested-by: pytest (X/X passing)"
```

### 4. Creating a Pull Request

```bash
# Push your branch
git push origin feature/add-awesome-feature

# Create PR using GitHub CLI
gh pr create --title "feat: Add awesome feature" \
  --body "$(cat .github/PULL_REQUEST_TEMPLATE.md)"

# Or create PR on GitHub web interface
```

### 5. After PR Approval

```bash
# Squash merge via GitHub UI
# Delete your branch
git checkout main
git pull
git branch -d feature/add-awesome-feature
```

---

## VS Code Tasks (Press Cmd/Ctrl+Shift+P → "Run Task")

| Task | What It Does |
|------|--------------|
| 🧪 Run All Tests | Run pytest on all packages |
| 🧪 Run Tests with Coverage | Generate coverage report |
| ✨ Format Code | Auto-format with Ruff |
| 🔍 Lint Code | Check and fix lint issues |
| 🔬 Type Check | Run Pyright type checker |
| ✅ Quality Check (All) | Run all quality checks at once |
| 📦 Validate Package | Validate a specific package |
| 🧹 Clean Build Artifacts | Remove cache files |

---

## Common Commands

### Testing

```bash
# Run all tests
uv run pytest -v

# Run tests for specific package
uv run pytest packages/tta-workflow-primitives/tests/ -v

# Run with coverage
uv run pytest --cov=packages --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check . --fix

# Type check
uvx pyright packages/

# All at once
uv run ruff format . && uv run ruff check . --fix && uvx pyright packages/
```

### Package Management

```bash
# Install dependencies
uv sync --all-extras

# Add a new dependency
uv add <package-name>

# Add dev dependency
uv add --dev <package-name>

# Validate a package
./scripts/validate-package.sh tta-workflow-primitives
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Commit with semantic message
git commit -m "feat: Add something"

# Push and create PR
git push origin feature/my-feature
gh pr create

# Sync with main
git checkout main
git pull origin main
```

---

## Commit Message Format

**Follow Conventional Commits:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactor
- `test`: Tests
- `chore`: Maintenance

**Examples:**

```bash
# New feature
git commit -m "feat(primitives): Add timeout handling"

# Bug fix
git commit -m "fix(cache): Resolve cache invalidation bug"

# Documentation
git commit -m "docs: Update README with examples"
```

---

## Using GitHub Copilot

### In Chat

**Ask for help:**
```
@workspace How do I add a new primitive?
```

**Generate code:**
```
Create a new router primitive with support for weighted routing
```

**Explain code:**
```
/explain this function
```

### In Code

1. Start typing a function signature
2. Wait for Copilot suggestion (ghost text)
3. Press `Tab` to accept
4. Press `Esc` to dismiss

**Pro tip:** Write a detailed docstring first, Copilot will suggest better implementation!

---

## Package Migration Checklist

Migrating a new package from TTA repo? Follow this:

### Pre-Migration

- [ ] Package has 100% passing tests
- [ ] Package has comprehensive documentation
- [ ] Package has been used in production/staging
- [ ] No known critical bugs
- [ ] No TTA-specific dependencies

### Migration Steps

1. **Create feature branch**
   ```bash
   git checkout -b feature/add-<package-name>
   ```

2. **Copy package**
   ```bash
   rsync -av --exclude='__pycache__' \
     ~/recovered-tta-storytelling/packages/<package>/ \
     ./packages/<package>/
   ```

3. **Clean**
   ```bash
   find packages/<package> -name '__pycache__' -type d -exec rm -rf {} +
   find packages/<package> -name '*.pyc' -delete
   ```

4. **Validate**
   ```bash
   ./scripts/validate-package.sh <package-name>
   ```

5. **Commit**
   ```bash
   git add packages/<package>/
   git commit -m "feat: Add <package-name> package

   - List key features
   - Test results: X/X passing
   - Documentation: Complete

   Tested-by: pytest
   Documented-in: packages/<package>/README.md"
   ```

6. **Create PR**
   ```bash
   gh pr create --title "feat: Add <package-name>" \
     --body "$(cat .github/PULL_REQUEST_TEMPLATE.md)"
   ```

7. **After approval: Squash merge on GitHub**

---

## Troubleshooting

### Tests Failing

```bash
# Run tests with verbose output
uv run pytest -vv --tb=long

# Run specific test
uv run pytest packages/my-package/tests/test_file.py::test_name -v

# Run with print statements visible
uv run pytest -s
```

### Type Errors

```bash
# Run Pyright with detailed output
uvx pyright packages/ --verbose

# Check specific file
uvx pyright packages/my-package/src/module.py
```

### Dependency Issues

```bash
# Clean and reinstall
rm -rf .venv
uv venv
uv sync --all-extras

# Verify installation
uv pip list
```

### Git Issues

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git checkout -- .

# Clean untracked files
git clean -fd

# Update from main
git checkout main
git pull origin main
git checkout feature/my-branch
git rebase main
```

---

## Quality Standards

### Must Pass Before PR

✅ **Code Quality**
- [ ] `ruff format --check .` passes
- [ ] `ruff check .` passes
- [ ] `pyright packages/` passes

✅ **Testing**
- [ ] All tests pass (100%)
- [ ] Coverage >80%

✅ **Documentation**
- [ ] README updated
- [ ] Examples provided
- [ ] Docstrings complete

✅ **Git**
- [ ] Semantic commit messages
- [ ] No merge commits
- [ ] PR template filled

✅ **Security**
- [ ] No secrets
- [ ] No hardcoded paths

---

## Release Process

### Creating a Release

1. **Update version in `pyproject.toml`**

2. **Update CHANGELOG.md**

3. **Commit**
   ```bash
   git commit -m "chore: Bump version to v0.2.0"
   ```

4. **Tag**
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0 - Description"
   ```

5. **Push**
   ```bash
   git push origin main --tags
   ```

6. **GitHub will auto-publish** (via CI/CD)

---

## Getting Help

### In VS Code

1. **Copilot Chat** - Press `Cmd/Ctrl+I`
2. **Workspace context** - Use `@workspace` in chat
3. **Error explanations** - Hover over error, click "Copilot"

### Command Line

```bash
# Explain a command
gh copilot explain "git rebase -i HEAD~3"

# Suggest a command
gh copilot suggest "commit these changes with proper message"
```

### Documentation

- Project docs: `docs/`
- Package READMEs: `packages/*/README.md`
- Migration guide: `docs/TTA_DEV_MIGRATION_STRATEGY.md`

---

## Tips for Success

1. **Keep branches short-lived** - Max 2-3 days
2. **Commit often** - Small, logical commits
3. **Use VS Code tasks** - Don't memorize commands
4. **Let Copilot help** - But always review its suggestions
5. **Run tests frequently** - Don't wait until the end
6. **Read the PR template** - It's your checklist
7. **Squash merge** - Keeps main branch clean
8. **Document as you go** - Future you will thank you

---

## Remember

> **"Only proven code enters TTA.dev"**

If you're unsure whether a component is ready:
- Does it have 100% passing tests?
- Has it been used successfully?
- Is documentation complete?
- Are there no known critical bugs?

If "yes" to all → **Ready to migrate!**
If "no" to any → **Keep it in TTA repo until proven**

---

**Last Updated:** 2025-10-27
**Maintained By:** @theinterneti
