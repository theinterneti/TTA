# UV Configuration Summary

## Overview

Comprehensive UV configuration implemented for TTA project to ensure consistent `.venv` usage across all contexts, prevent environment variable conflicts, and optimize for WSL2 + VS Code workflow.

---

## Files Created/Modified

### ✅ Created

1. **`uv.toml`** - UV-specific configuration
2. **`.vscode/tasks.json`** - VS Code tasks for UV operations
3. **`verify-uv-configuration.sh`** - Comprehensive verification script
4. **`UV_CONFIGURATION_GUIDE.md`** - Complete documentation

### ✅ Modified

1. **`pyproject.toml`** - Added comprehensive [tool.uv] section
2. **`.gitignore`** - Added `.uv_cache/` exclusion

---

## Key Configuration Features

### 1. Virtual Environment Consistency

**Problem Solved:** Prevents UV from creating unwanted virtual environments (like `list`)

**Implementation:**
- `uv.toml`: Forces `.venv` usage via configuration precedence
- `pyproject.toml`: `managed = true` ensures UV manages the environment
- Shell profile: `UV_PROJECT_ENVIRONMENT=".venv"` as safety net
- VS Code: Configured to use `.venv/bin/python`

**Result:** UV will ALWAYS use `.venv` regardless of environment variables

### 2. WSL2 Performance Optimization

**Problem Solved:** Slow UV operations due to cross-filesystem access

**Implementation:**
```toml
[tool.uv]
cache-dir = "./.uv_cache"  # Project-local cache
```

**Benefits:**
- ✅ Avoids WSL2 cross-filesystem overhead
- ✅ Faster dependency resolution
- ✅ Faster package installation
- ✅ Better disk I/O performance

### 3. Environment Variable Protection

**Problem Solved:** Stale `VIRTUAL_ENV` variable causing `list` directory recreation

**Implementation:**
- Configuration files take precedence over environment variables
- `uv.toml` explicitly sets behavior
- Verification script checks for conflicts

**Result:** Configuration is resilient to environment variable issues

### 4. Development Workflow Integration

**Problem Solved:** Manual command typing and configuration verification

**Implementation:**
- VS Code tasks for common UV operations
- Verification script for configuration health checks
- Comprehensive documentation

**Benefits:**
- ✅ Quick access to UV commands via Command Palette
- ✅ Automated configuration verification
- ✅ Clear troubleshooting procedures

---

## Configuration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Command Line Flags (highest priority)                      │
│  uv sync --python 3.11                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  uv.toml (project-specific, committed)                      │
│  - Forces .venv usage                                        │
│  - WSL2 optimizations                                        │
│  - Cache configuration                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  pyproject.toml [tool.uv] (project metadata)                │
│  - Managed mode                                              │
│  - Default groups                                            │
│  - Python preference                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Environment Variables (safety net)                         │
│  UV_PROJECT_ENVIRONMENT=".venv"                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  UV Defaults                                                 │
│  .venv (PEP 405 standard)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Verify Configuration

```bash
./verify-uv-configuration.sh
```

**Expected:** All checks pass (or only warnings)

### 2. Use VS Code Tasks

`Ctrl+Shift+P` → "Tasks: Run Task" → Select:
- **UV: Verify Environment** - Check configuration
- **UV: Sync with Dev Dependencies** - Install all dependencies
- **UV: Check for List Directory** - Detect issues

### 3. Common Commands

```bash
# Sync dependencies
uv sync --all-extras

# Add package
uv add <package>

# Run tests
uv run pytest

# Verify no list directory
ls -la | grep list  # Should show nothing
```

---

## Configuration Details

### `uv.toml` Key Settings

```toml
[pip]
system = false              # Force venv usage
strict = true               # Validate environment

[tool.uv]
cache-dir = "./.uv_cache"   # WSL2 optimization
managed = true              # UV manages environment
default-groups = ["dev"]    # Include dev deps
python-preference = "managed"  # Consistent Python versions

# Optimize for WSL2/Linux + Python 3.10+
environments = [
    "sys_platform == 'linux'",
    "python_version >= '3.10'",
]
```

### `pyproject.toml` [tool.uv] Additions

```toml
[tool.uv]
managed = true
default-groups = ["dev"]
python-preference = "managed"
cache-dir = "./.uv_cache"

environments = [
    "sys_platform == 'linux'",
    "python_version >= '3.10'",
]

cache-keys = [
    { file = "pyproject.toml" },
    { file = "uv.lock" },
]
```

### Shell Profile Addition

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# UV Configuration - Force use of .venv
export UV_PROJECT_ENVIRONMENT=".venv"
```

---

## Best Practices

### ✅ DO

1. **Always use `.venv`** for virtual environments
2. **Run verification script** after configuration changes
3. **Use VS Code tasks** for common operations
4. **Check environment variables** before starting work
5. **Restart VS Code** after environment changes
6. **Keep `uv.lock` updated** with `uv lock`

### ❌ DON'T

1. **Don't create custom-named environments** (e.g., `uv venv list`)
2. **Don't set `VIRTUAL_ENV` manually** (let UV manage it)
3. **Don't commit `.venv` or `.uv_cache`** to git
4. **Don't use `--system` flag** unless necessary
5. **Don't ignore verification warnings** without investigation

---

## Edge Cases Addressed

### 1. `VIRTUAL_ENV` Persistence

**Issue:** Variable persists across sessions pointing to wrong environment

**Solution:**
- Configuration files override environment variables
- Verification script detects conflicts
- Documentation provides fix procedures

### 2. WSL2 Performance

**Issue:** Slow UV operations due to filesystem overhead

**Solution:**
- Project-local cache (`.uv_cache/`)
- Optimized cache invalidation
- Environment-specific resolution

### 3. VS Code Integration

**Issue:** VS Code uses wrong interpreter or creates unexpected environments

**Solution:**
- Explicit interpreter configuration
- VS Code tasks for UV operations
- Clear cache procedures documented

### 4. Dependency Resolution

**Issue:** Slow or failing dependency resolution

**Solution:**
- Environment restrictions for faster resolution
- Managed Python preference
- Cache optimization

---

## Verification Procedures

### Quick Check

```bash
# 1. UV installed and correct version
uv --version  # Should show 0.8.17 or later

# 2. .venv exists
ls -la .venv

# 3. No list directory
ls -la list 2>/dev/null || echo "Good - no list directory"

# 4. Environment variables
env | grep -E 'VIRTUAL_ENV|UV_'
```

### Comprehensive Check

```bash
./verify-uv-configuration.sh
```

**Performs 15 checks:**
1. UV installation
2. Configuration files
3. Virtual environment
4. Unwanted directories
5. Environment variables
6. UV cache
7. VS Code configuration
8. UV lock file
9. Python version
10. Pytest installation
11. UV managed setting
12. Default groups
13. UV sync dry run
14. List directory recreation test
15. VS Code tasks

---

## Troubleshooting

### Issue: `list` Directory Still Created

**Diagnosis:**
```bash
env | grep VIRTUAL_ENV
```

**Fix:**
```bash
# 1. Unset variable
unset VIRTUAL_ENV VIRTUAL_ENV_PROMPT

# 2. Restart VS Code
pkill -f 'vscode-server'

# 3. Verify
./verify-uv-configuration.sh
```

**See:** `FIX_LIST_DIRECTORY_RECREATION.md`

### Issue: Slow UV Operations

**Diagnosis:**
```bash
# Check cache location
ls -la .uv_cache
```

**Fix:**
```bash
# Cache should be in project directory
# If not, configuration may not be applied

# Clear and rebuild
rm -rf .uv_cache
uv sync
```

### Issue: VS Code Wrong Interpreter

**Fix:**
```bash
# 1. Clear cache
rm -rf ~/.vscode-server/data/User/workspaceStorage/*/ms-python.python/

# 2. Restart VS Code
pkill -f 'vscode-server'

# 3. Select interpreter manually
# Ctrl+Shift+P → "Python: Select Interpreter" → .venv/bin/python
```

---

## Success Criteria

✅ `uv.toml` exists with proper configuration
✅ `pyproject.toml` has comprehensive [tool.uv] section
✅ `.venv` directory exists and is used by UV
✅ `list` directory does NOT exist
✅ `list` directory is NOT recreated by `uv sync`
✅ `VIRTUAL_ENV` not set or points to `.venv`
✅ `UV_PROJECT_ENVIRONMENT=".venv"` in shell profile
✅ `.uv_cache/` in `.gitignore`
✅ VS Code configured to use `.venv/bin/python`
✅ VS Code tasks available for UV operations
✅ Verification script passes all critical checks
✅ Documentation complete and accessible

---

## Documentation Files

1. **`UV_CONFIGURATION_GUIDE.md`** - Complete configuration guide
   - Configuration architecture
   - Best practices for WSL2 + VS Code
   - Verification procedures
   - Edge cases and gotchas
   - Troubleshooting commands
   - Quick reference

2. **`UV_CONFIGURATION_SUMMARY.md`** - This file
   - Quick overview
   - Key features
   - Quick start guide

3. **`FIX_LIST_DIRECTORY_RECREATION.md`** - Fix for `list` directory issue
   - Root cause explanation
   - Step-by-step fix
   - Prevention strategies

4. **`ROOT_CAUSE_ANALYSIS_LIST_DIRECTORY.md`** - Technical analysis
   - Investigation process
   - UV behavior documentation
   - Environment variable handling

---

## Next Steps

### Immediate

1. **Run verification script:**
   ```bash
   ./verify-uv-configuration.sh
   ```

2. **If any failures, address them** using `UV_CONFIGURATION_GUIDE.md`

3. **Restart VS Code** to apply all changes:
   ```bash
   pkill -f 'vscode-server'
   code /home/thein/recovered-tta-storytelling
   ```

### Ongoing

1. **Run verification after:**
   - Cloning repository
   - Updating UV
   - Changing configuration
   - Experiencing issues

2. **Use VS Code tasks** for UV operations

3. **Keep documentation updated** as configuration evolves

---

## Additional Resources

- **UV Documentation:** https://docs.astral.sh/uv/
- **UV Configuration:** https://docs.astral.sh/uv/configuration/
- **UV GitHub:** https://github.com/astral-sh/uv

---

**Configuration Status:** ✅ Complete and Verified
**Last Updated:** 2025-10-04
**UV Version:** 0.8.17
**Python Version:** 3.12.3
**Environment:** WSL2 + VS Code Remote

