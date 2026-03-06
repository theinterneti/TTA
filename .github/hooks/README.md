# Copilot CLI Hooks

This directory contains automated quality gate enforcement hooks for GitHub Copilot CLI.

## Overview

These hooks ensure that all code modifications pass local quality gates before control returns to the user. This creates a tight feedback loop and maintains code quality automatically.

## Files

### Configuration
- **`copilot-hooks.yml`** - Hook configuration and agent behavior rules
- **`post-generation.sh`** - Executable bash script that runs quality gates

### Quality Gates

1. **Ruff** - Python linting and code style
2. **Pyright** - Static type checking
3. **Pytest** - Automated test suite

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Copilot CLI modifies code                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Post-generation hook automatically triggered             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Run quality gates (ruff, pyright, pytest)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                ┌────┴────┐
                │ Pass?   │
                └────┬────┘
                     │
        ┌────────────┼────────────┐
        │ YES        │ NO         │
        ▼            ▼            │
    ┌───────┐   ┌──────────┐     │
    │ Done! │   │ Auto-fix │     │
    └───────┘   └─────┬────┘     │
                      │           │
                      └───────────┘
                   (up to 5 iterations)
```

## Automatic Repair Strategies

### Ruff Failures
1. Apply `--fix` (safe auto-fixes)
2. Apply `--unsafe-fixes` if needed
3. Parse errors and apply manual fixes
4. Re-run check

### Pyright Failures
1. Analyze type errors
2. Add missing type hints
3. Fix import issues
4. Avoid `type: ignore` unless necessary

### Pytest Failures
1. Identify failing tests
2. Analyze assertions and error messages
3. Fix code logic or test expectations
4. Re-run affected tests

## Configuration

Edit `.github/copilot-hooks.yml` to customize:

- `max_iterations`: Maximum repair attempts (default: 5)
- `timeout`: Command timeout in seconds
- `required`: Make check required or optional
- `on_failure`: Action to take (auto_fix, report, ignore)

## Logs

Quality gate logs are stored in:
```
.github/hooks/logs/quality-gates-YYYYMMDD-HHMMSS.log
```

Logs are retained for 7 days and automatically cleaned up.

## Manual Execution

Test the hook manually:
```bash
bash .github/hooks/post-generation.sh
```

## Bypass (Emergency Only)

To skip quality gates in emergencies:
```bash
SKIP_QUALITY_GATES=1 <your command>
```

**Warning**: Only use in extreme cases. Bypassing quality gates defeats the purpose of automated enforcement.

## Requirements

- `uv` package manager installed
- Python 3.12+ environment
- All project dependencies installed

## Troubleshooting

### Hook not executing
1. Check hook is executable: `ls -l .github/hooks/post-generation.sh`
2. Verify Copilot CLI configuration recognizes hooks
3. Check logs for errors

### Quality gates timing out
1. Increase timeout in `copilot-hooks.yml`
2. Run checks manually to identify slow tests
3. Consider running subset of tests in hook

### Persistent failures
1. Review logs in `.github/hooks/logs/`
2. Run checks manually to debug
3. Check if max_iterations needs adjustment

## Best Practices

✅ **DO**:
- Let the automatic repair loop handle common issues
- Review logs when repairs fail
- Keep quality gate thresholds strict (0 errors)
- Trust the process - hooks catch issues early

❌ **DON'T**:
- Bypass quality gates unless absolutely necessary
- Ignore persistent failures
- Modify hook scripts without testing
- Set thresholds too lenient

## Integration with CI/CD

These local hooks complement (not replace) CI/CD pipelines:

- **Local hooks**: Fast feedback during development
- **CI/CD**: Comprehensive checks before merge

Both should enforce the same quality standards.

---

**Last Updated**: 2026-03-06  
**Status**: Active - Automated quality enforcement enabled
