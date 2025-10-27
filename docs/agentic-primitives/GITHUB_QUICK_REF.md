# GitHub Integration Quick Reference Card

## 🚀 Essential Commands

### UV Environment Management
```bash
uv sync --all-extras --dev    # Full setup
uv run pytest                 # Run tests
uv run python script.py       # Run Python
uv add package-name           # Add dependency
uv pip list                   # List packages
./uv-manager.sh full          # Automated setup
```

### Git Basics
```bash
git status                    # Check changes
git add .                     # Stage all
git commit -m "msg"          # Commit
git push                      # Push to remote
git pull --rebase            # Update from remote
git log --oneline --graph    # View history
```

### GitHub CLI
```bash
gh pr create                  # Create PR
gh pr list                    # List PRs
gh pr view                    # View PR details
gh run list                   # List workflow runs
gh run watch                  # Watch active run
gh workflow list              # List workflows
gh repo view                  # View repo info
```

### VS Code Quick Keys
```
Ctrl+Shift+P                 # Command palette
Ctrl+`                       # Terminal
Ctrl+Shift+B                 # Build/Run task
Ctrl+Shift+G                 # Source control
Ctrl+K Ctrl+O                # Open folder
```

## 📝 Daily Workflow

```bash
# 1. Start of day
git checkout development
git pull origin development
git checkout feature/your-branch
git rebase development

# 2. Work & commit
git add .
git commit -m "feat: add feature"

# 3. Run tests
uv run pytest
# or
uv run pytest --cov=src --cov-report=html

# 4. Push changes
git push origin feature/your-branch

# 5. Create PR when ready
gh pr create --base development --title "feat: your feature"
```

## 🔧 Troubleshooting

### VS Code can't find Python
```bash
# In VS Code: Ctrl+Shift+P
# Type: Python: Select Interpreter
# Choose: .venv/bin/python
```

### Pytest not found
```bash
rm -rf .venv
uv sync --all-extras --dev
# Restart VS Code
```

### Git merge conflicts
```bash
git status                    # See conflicts
# Edit files, resolve conflicts
git add .
git rebase --continue         # If rebasing
git merge --continue          # If merging
```

### Workflow failing
```bash
gh run list                   # Find run ID
gh run view <run-id> --log   # View logs
./github-workflow-validator.sh all  # Check setup
```

## 🎯 Branch Strategy

```
main ← staging ← development ← feature/your-branch
```

- Work in `feature/*` branches
- Merge to `development` when ready
- Test in `staging` before production
- Deploy from `main`

## 🧪 Testing Shortcuts

```bash
# Quick test
uv run pytest -x              # Stop on first failure

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test
uv run pytest tests/test_file.py::test_function

# Verbose
uv run pytest -v              # Verbose output

# Parallel
uv run pytest -n auto         # Use all CPUs
```

## 📊 Workflow Status

```bash
# Check all workflows
gh workflow list

# View specific workflow
gh workflow view tests.yml

# Recent runs
gh run list --limit 10

# Watch active run
gh run watch
```

## 🔐 Secrets & Config

Required secrets in GitHub Settings → Secrets:
- `OPENROUTER_API_KEY`
- `NEO4J_PASSWORD`
- `GRAFANA_ADMIN_PASSWORD`

## 📖 Important Files

```
.github/
├── workflows/              # CI/CD definitions
├── GITHUB_INTEGRATION_GUIDE.md  # Full guide
└── project-config.env     # Project config (git-ignored)

.vscode/
├── settings.json          # Editor config
├── extensions.json        # Recommended extensions
└── tasks.json             # Task definitions

.venv/                     # UV environment (git-ignored)
uv.lock                    # Dependency lock
pyproject.toml             # Project config
.python-version            # Python version
.gitignore                 # Git exclusions
```

## 🛠️ Helper Scripts

```bash
# UV environment manager
./uv-manager.sh full       # Full setup
./uv-manager.sh info       # Environment info
./uv-manager.sh verify     # Verify setup

# Workflow validator
./github-workflow-validator.sh all  # All checks
./github-workflow-validator.sh syntax  # Check syntax
```

## 💡 Tips

1. **Always work in feature branches** - Never commit directly to main
2. **Run tests before pushing** - `uv run pytest`
3. **Keep commits small** - One logical change per commit
4. **Write clear commit messages** - Use conventional commits
5. **Pull before push** - `git pull --rebase` to avoid conflicts
6. **Keep uv.lock committed** - Ensures reproducible builds
7. **Don't commit .venv/** - Virtual env is git-ignored
8. **Use draft PRs** - For work in progress

## 📚 Documentation Links

- Full Guide: `.github/GITHUB_INTEGRATION_GUIDE.md`
- UV Docs: https://github.com/astral-sh/uv
- GitHub CLI: https://cli.github.com/manual/
- VS Code Python: https://code.visualstudio.com/docs/python
- Conventional Commits: https://www.conventionalcommits.org/

---

**Quick Help**
```bash
./uv-manager.sh              # UV environment menu
./github-workflow-validator.sh  # Workflow validation menu
gh help                      # GitHub CLI help
git help <command>          # Git command help
```
