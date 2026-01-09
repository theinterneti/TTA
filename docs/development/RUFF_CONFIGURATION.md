# Ruff Linter and Formatter Configuration

**Last Updated**: 2025-10-27
**Ruff Version**: 0.11.0+
**Python Version**: 3.12+

## Overview

Ruff is an extremely fast Python linter and formatter written in Rust. It replaces multiple tools (Black, isort, flake8, pylint) with a single, unified tool that runs 10-100x faster.

### Key Benefits

- **Speed**: 10-100x faster than traditional Python linters
- **Unified**: Replaces Black, isort, flake8, pylint, and more
- **Auto-fix**: Automatically fixes most issues with `--fix`
- **Comprehensive**: 800+ rules covering style, bugs, performance, and security

## Configuration Location

All Ruff configuration is in `pyproject.toml` under the `[tool.ruff]` section.

## Current Configuration Summary

### Error Reduction

After configuration optimization:
- **Before**: 2,161 errors
- **After**: 206 errors
- **Reduction**: 90.5%

### Enabled Rule Sets

We enable a carefully selected set of rules that balance code quality with development velocity:

- **F** (Pyflakes) - Essential error detection
- **E, W** (pycodestyle) - Style consistency
- **I** (isort) - Import sorting
- **B** (flake8-bugbear) - Common bugs and design problems
- **C4** (flake8-comprehensions) - Better comprehensions
- **UP** (pyupgrade) - Upgrade syntax for newer Python versions
- **SIM** (flake8-simplify) - Simplification suggestions

### Disabled Rule Sets

We intentionally **do not** enable these rule sets to avoid excessive noise:

- **S** (flake8-bandit) - Security rules (too many false positives in tests)
- **T20** (flake8-print) - Print statements (allowed in scripts and tests)
- **ARG** (flake8-unused-arguments) - Unused arguments (common in interfaces)
- **PTH** (flake8-use-pathlib) - Pathlib usage (not always better)
- **ERA** (eradicate) - Commented code (acceptable during development)
- **PL** (pylint) - Pylint rules (too strict for practical development)
- **PERF** (perflint) - Performance anti-patterns (too strict)
- **RET** (flake8-return) - Return statement rules (too opinionated)

## Per-File Ignores

Different files have different requirements. We configure exceptions for:

### Test Files (`tests/**/*.py`)

Tests have more lenient rules:
- Allow `assert` statements (required for pytest)
- Allow unused arguments (fixtures, parametrize)
- Allow magic values (test data)
- Allow print statements (debugging)
- Allow pseudo-random generators
- Allow imports outside top-level (test isolation)

### Scripts (`scripts/**/*.py`)

Scripts need CLI-friendly patterns:
- Allow print statements (CLI output)
- Allow complex branching (CLI logic)
- Allow many statements (script logic)
- Allow unused arguments (CLI interfaces)
- Allow `open()` instead of pathlib

### Agent Orchestration (`src/agent_orchestration/**/*.py`)

Dynamic agent loading requires:
- Allow imports outside top-level (dynamic agent loading)
- Allow try-except in loops (async retry patterns)

### Components (`src/components/**/*.py`)

Interface implementations may have:
- Unused method arguments (interface methods)
- Imports outside top-level (dynamic imports)

## Common Commands

### Check for Issues

```bash
# Check all files
uv run ruff check src/ tests/

# Check with statistics
uv run ruff check src/ tests/ --statistics

# Check specific file
uv run ruff check src/agent_orchestration/circuit_breaker.py
```

### Auto-Fix Issues

```bash
# Fix all auto-fixable issues
uv run ruff check --fix src/ tests/

# Fix with unsafe fixes (use with caution)
uv run ruff check --fix --unsafe-fixes src/ tests/
```

### Format Code

```bash
# Format all files
uv run ruff format src/ tests/

# Check formatting without changing files
uv run ruff format --check src/ tests/

# Show diff of formatting changes
uv run ruff format --check --diff src/ tests/
```

### Combined Workflow

```bash
# Fix linting issues, then format
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/
```

## CI/CD Integration

Ruff runs in the `code-quality.yml` workflow:

1. **Linting**: `uvx ruff check src/ tests/ --output-format=github --statistics`
2. **Formatting**: `uvx ruff format --check --diff src/ tests/`

Both must pass for the workflow to succeed.

## Quality Gates

### Development → Staging

- All Ruff checks must pass
- No critical linting errors
- Code must be formatted

### Staging → Production

- All Ruff checks must pass
- No linting warnings
- Code must be formatted

## Troubleshooting

### "Too many errors"

If you see hundreds of errors after pulling changes:

```bash
# Auto-fix what can be fixed
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/

# Check remaining issues
uv run ruff check src/ tests/ --statistics
```

### "Import sorting issues"

Ruff handles import sorting automatically:

```bash
# Fix import sorting
uv run ruff check --fix --select I src/ tests/
```

### "Formatting conflicts"

If Ruff formatting conflicts with your editor:

1. Configure your editor to use Ruff formatter
2. Disable other formatters (Black, autopep8)
3. Run `uv run ruff format` before committing

### "False positives"

If Ruff flags valid code:

1. Add a `# noqa: <code>` comment to suppress the specific rule
2. If it's a common pattern, add to per-file ignores in `pyproject.toml`
3. If it's a bug, report to https://github.com/astral-sh/ruff/issues

## Best Practices

### Before Committing

```bash
# Run quality checks
bash scripts/dev.sh quality

# Or manually
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/
uvx pyright src/
```

### During Development

- Enable Ruff in your editor for real-time feedback
- Fix issues as you write code
- Don't accumulate linting debt

### Code Review

- Ruff checks run automatically in CI
- Fix all Ruff issues before requesting review
- Don't disable rules without discussion

## Editor Integration

### VS Code

Install the Ruff extension:

```json
{
  "ruff.enable": true,
  "ruff.organizeImports": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff"
}
```

### PyCharm

1. Install Ruff plugin
2. Configure as external tool
3. Enable format on save

### Vim/Neovim

Use `ruff-lsp` or `null-ls.nvim` with Ruff integration.

## Migration from Black/isort

Ruff replaces both Black and isort:

- **Black** → `ruff format`
- **isort** → `ruff check --select I --fix`

Configuration is compatible with Black defaults (line length 88, double quotes).

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Ruff Rules](https://docs.astral.sh/ruff/rules/)
- [Ruff Configuration](https://docs.astral.sh/ruff/configuration/)
- [Ruff GitHub](https://github.com/astral-sh/ruff)

## Support

For questions or issues:

1. Check this documentation
2. Review `pyproject.toml` configuration
3. Check Ruff documentation
4. Ask in team chat
5. Create an issue in the repository


---
**Logseq:** [[TTA.dev/Docs/Development/Ruff_configuration]]
