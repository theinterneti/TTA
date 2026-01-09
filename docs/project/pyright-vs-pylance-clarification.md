# Pyright vs Pylance: Clarification and Best Practices

**Date:** 2025-10-06
**Status:** ✅ Clarified

---

## Executive Summary

**Pylance** and **Pyright** are related but distinct tools:
- **Pylance** = VS Code extension (closed-source) that includes Pyright's type checking engine + additional IDE features
- **Pyright** = Open-source Python type checker that can run standalone (CLI) or as a language server

**Our Approach:** Use **both**:
- **Pylance** for IDE features (autocomplete, hover, refactoring, etc.)
- **Standalone Pyright CLI** for automation (CI/CD, pre-commit hooks, command-line type checking)

---

## 1. Relationship Between Pyright and Pylance

### What is Pyright?

**Pyright** is an open-source Python type checker developed by Microsoft:
- **Repository:** https://github.com/microsoft/pyright
- **Purpose:** Static type checking for Python code
- **Usage:** Can run as CLI tool or language server
- **Speed:** 10-100x faster than MyPy (written in TypeScript/Node.js)

### What is Pylance?

**Pylance** is a VS Code extension that:
- **Includes** Pyright's type checking engine internally
- **Adds** additional IDE features:
  - Semantic highlighting
  - Auto-imports
  - Code navigation (go to definition, find references)
  - Refactoring tools
  - IntelliSense (autocomplete)
  - Signature help
- **Closed-source** (proprietary Microsoft extension)
- **Repository:** https://github.com/microsoft/pylance-release (issue tracker only)

### Key Insight

**Pylance uses Pyright internally**, but they are **not the same thing**:

```
┌─────────────────────────────────────────┐
│           Pylance Extension             │
│  (VS Code - Closed Source)              │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Pyright Type Checker            │ │
│  │   (Open Source Core)              │ │
│  └───────────────────────────────────┘ │
│                                         │
│  + Semantic Highlighting                │
│  + Auto-imports                         │
│  + Code Navigation                      │
│  + Refactoring                          │
│  + IntelliSense                         │
└─────────────────────────────────────────┘
```

---

## 2. Current Setup Analysis

### What We're Using

#### In VS Code (IDE)
- **Pylance extension** provides:
  - Type checking (via embedded Pyright)
  - Autocomplete
  - Hover information
  - Go to definition
  - Find references
  - Refactoring
  - Semantic highlighting

#### In Automation (CLI/CI/CD)
- **Standalone Pyright CLI** (`uvx pyright`) provides:
  - Type checking in CI/CD workflows
  - Command-line type checking
  - Pre-commit hooks (if needed)
  - Consistent type checking across environments

### Configuration

Both Pylance and standalone Pyright read the same configuration:
- **File:** `pyproject.toml` under `[tool.pyright]`
- **Shared settings:** Both tools use the same configuration
- **Result:** Consistent type checking behavior

---

## 3. IDE vs CLI Usage

### Pylance (VS Code Extension)

**Purpose:** IDE features + type checking
**Installation:** VS Code extension marketplace
**Usage:** Automatic when editing Python files in VS Code
**Configuration:** VS Code settings.json + pyproject.toml

**Features:**
- ✅ Real-time type checking as you type
- ✅ Autocomplete with type information
- ✅ Hover tooltips with type info
- ✅ Go to definition/references
- ✅ Refactoring (rename, extract, etc.)
- ✅ Semantic syntax highlighting
- ✅ Auto-imports
- ❌ Cannot run from command line
- ❌ Cannot use in CI/CD

### Standalone Pyright CLI

**Purpose:** Type checking only (no IDE features)
**Installation:** `uvx pyright` or `npm install -g pyright`
**Usage:** Command-line tool
**Configuration:** pyproject.toml only

**Features:**
- ✅ Command-line type checking
- ✅ CI/CD integration
- ✅ Pre-commit hooks
- ✅ JSON output for tooling
- ✅ Consistent with Pylance (same engine)
- ❌ No IDE features
- ❌ No autocomplete/hover/navigation

---

## 4. Why Use Both?

### Scenario 1: Developer Workflow

**Problem:** Developer edits code in VS Code
**Solution:** Pylance provides real-time feedback

```
Developer types code → Pylance shows errors immediately
                    → Pylance provides autocomplete
                    → Pylance enables navigation
```

### Scenario 2: CI/CD Pipeline

**Problem:** Need to validate types before merging PR
**Solution:** Standalone Pyright CLI in GitHub Actions

```
git push → GitHub Actions runs → uvx pyright src/
                              → Fails if type errors found
                              → Blocks merge
```

### Scenario 3: Command-Line Validation

**Problem:** Developer wants to check types before committing
**Solution:** Run Pyright CLI manually

```bash
# Quick type check before commit
uvx pyright src/

# Or use convenience script
./scripts/dev.sh typecheck
```

### Scenario 4: Pre-commit Hooks (Optional)

**Problem:** Want to catch type errors before commit
**Solution:** Add Pyright to pre-commit hooks

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/RobertCraigie/pyright-python
  rev: v1.1.350
  hooks:
    - id: pyright
```

**Note:** We currently don't use this because:
- Pyright is slower than Ruff (~3-5 seconds)
- Type checking is better suited for CI/CD
- Developers can run `./scripts/dev.sh typecheck` manually

---

## 5. Version Synchronization

### Challenge

Pylance and standalone Pyright have different release cadences:
- **Pylance:** Bundled with specific Pyright version
- **Standalone Pyright:** Independent releases

**Result:** Pylance might use Pyright 1.1.400 while standalone CLI uses 1.1.406

### Solution Options

#### Option 1: Accept Version Differences (Our Current Approach)
- ✅ Simple - no extra configuration
- ✅ Both tools stay up-to-date
- ⚠️ Minor differences possible (rare)
- **Best for:** Most projects

#### Option 2: Pin Pyright Version to Match Pylance
```bash
# In CI/CD, use specific version
uvx pyright@1.1.400 src/
```
- ✅ Exact version match
- ⚠️ Requires manual version updates
- **Best for:** Projects requiring exact consistency

#### Option 3: Configure Pylance to Use Specific Pyright
```json
// settings.json
"python.analysis.diagnosticsSource": "Pyright",
"python.analysis.pyrightVersion": "1.1.400"
```
- ✅ Pylance uses specific Pyright version
- ⚠️ Runs two copies of Pyright (2x memory/CPU)
- **Best for:** Matching CI/CD exactly in IDE

---

## 6. Configuration Best Practices

### Single Source of Truth

Use `pyproject.toml` for all Pyright configuration:

```toml
[tool.pyright]
# This configuration is used by BOTH Pylance and standalone Pyright
pythonVersion = "3.10"
typeCheckingMode = "standard"
include = ["src"]
exclude = ["tests/", "docs/"]

# Type checking rules
reportGeneralTypeIssues = "error"
reportMissingImports = "error"
# ... etc
```

### VS Code Settings (Optional)

Only use `settings.json` for Pylance-specific IDE features:

```json
{
  // Pylance-specific settings (not used by standalone Pyright)
  "python.analysis.autoImportCompletions": true,
  "python.analysis.indexing": true,
  "python.analysis.packageIndexDepths": [
    { "name": "sklearn", "depth": 2 }
  ]
}
```

---

## 7. Our Recommended Approach

### ✅ What We're Doing (Correct)

1. **Pylance in VS Code:**
   - Installed as VS Code extension
   - Provides IDE features + type checking
   - Reads configuration from `pyproject.toml`

2. **Standalone Pyright CLI:**
   - Run via `uvx pyright` (no installation needed)
   - Used in CI/CD workflows
   - Used in convenience script (`./scripts/dev.sh typecheck`)
   - Reads same configuration from `pyproject.toml`

3. **Single Configuration:**
   - All settings in `pyproject.toml` under `[tool.pyright]`
   - Both tools use same configuration
   - Consistent behavior across IDE and automation

### ❌ What We're NOT Doing (Unnecessary)

1. **Installing Pyright as project dependency:**
   - ❌ Don't add `pyright` to `pyproject.toml` dependencies
   - ✅ Use `uvx pyright` instead (isolated, always latest)

2. **Duplicate configuration:**
   - ❌ Don't configure Pyright in both `pyproject.toml` and `settings.json`
   - ✅ Use `pyproject.toml` as single source of truth

3. **Running Pyright in pre-commit hooks:**
   - ❌ Too slow for pre-commit (3-5 seconds)
   - ✅ Run in CI/CD instead
   - ✅ Developers can run manually when needed

---

## 8. Migration from MyPy

### What Changed

**Before (MyPy):**
- MyPy for type checking (slow, 10-100x slower than Pyright)
- Separate configuration in `[tool.mypy]`
- Different CLI commands

**After (Pyright):**
- Pyright for type checking (fast)
- Configuration in `[tool.pyright]`
- Same engine as Pylance (consistency)

### Benefits

1. **Speed:** 10-100x faster than MyPy
2. **Consistency:** Same engine in IDE (Pylance) and CLI (Pyright)
3. **Better IDE Integration:** Pylance is optimized for VS Code
4. **Active Development:** Microsoft actively maintains both

---

## 9. Common Questions

### Q: Do I need to install Pyright if I have Pylance?

**A:** For IDE use, no. For CI/CD and command-line, yes (via `uvx pyright`).

### Q: Will Pylance and Pyright give different results?

**A:** Rarely. They use the same engine and configuration. Minor differences possible if versions differ significantly.

### Q: Should I add Pyright to my project dependencies?

**A:** No. Use `uvx pyright` instead for isolated, always-updated execution.

### Q: Can I use Pyright without VS Code?

**A:** Yes! Pyright CLI works in any environment (terminal, CI/CD, other editors).

### Q: Should I use Pyright in pre-commit hooks?

**A:** Optional. We don't because it's slower than Ruff. Better suited for CI/CD.

### Q: How do I ensure Pylance and Pyright match exactly?

**A:** Use the same configuration in `pyproject.toml`. Optionally pin Pyright version to match Pylance.

---

## 10. Summary

**Pylance** = VS Code extension with IDE features + embedded Pyright
**Pyright** = Standalone CLI tool for type checking

**Best Practice:**
- ✅ Use Pylance in VS Code for IDE features
- ✅ Use standalone Pyright CLI (`uvx pyright`) for automation
- ✅ Configure both via `pyproject.toml`
- ✅ Accept minor version differences (or pin if needed)

**Our Setup:**
- Pylance installed in VS Code
- Pyright CLI via `uvx pyright` (no installation)
- Single configuration in `pyproject.toml`
- Used in CI/CD and convenience script

**Result:** Fast, consistent type checking across IDE and automation with minimal configuration overhead.

---

## References

- **Pyright Documentation:** https://microsoft.github.io/pyright/
- **Pylance Documentation:** https://github.com/microsoft/pylance-release
- **Using Pyright with Pylance:** https://github.com/microsoft/pylance-release/blob/main/USING_WITH_PYRIGHT.md
- **Our Configuration:** `pyproject.toml` under `[tool.pyright]`
- **Our Convenience Script:** `scripts/dev.sh typecheck`


---
**Logseq:** [[TTA.dev/Docs/Project/Pyright-vs-pylance-clarification]]
