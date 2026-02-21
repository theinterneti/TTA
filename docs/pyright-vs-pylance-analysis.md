# Pyright vs Pylance: Comprehensive Analysis

**Date:** 2025-10-06
**Status:** ✅ Analysis Complete
**Recommendation:** Use both - Pylance for IDE, standalone Pyright CLI for automation

---

## Executive Summary

**Pylance** and **Pyright** are related but distinct tools:

- **Pyright** = Open-source static type checker (CLI tool + type checking engine)
- **Pylance** = Proprietary VS Code extension that **includes** Pyright + additional IDE features

**Key Finding:** Pylance bundles Pyright's type checking engine but adds VS Code-specific features like IntelliSense, code navigation, and semantic highlighting. The standalone Pyright CLI is still needed for command-line type checking, CI/CD, and pre-commit hooks.

---

## 1. Relationship Between Pyright and Pylance

### Pyright (Open Source)
**Repository:** https://github.com/microsoft/pyright
**What it is:**
- Standalone static type checker for Python
- Command-line tool (`pyright` CLI)
- Core type checking engine (written in TypeScript)
- Can be used independently of VS Code

**Components:**
- `pyright` - CLI tool for type checking
- Type checking engine - Core logic for analyzing Python code
- Language server protocol (LSP) implementation

### Pylance (Proprietary)
**Repository:** https://github.com/microsoft/pylance-release (issues/docs only)
**What it is:**
- VS Code extension for Python language support
- **Includes Pyright's type checking engine**
- Adds VS Code-specific features on top of Pyright

**Additional Features Beyond Pyright:**
- IntelliSense (auto-completion)
- Code navigation (go to definition, find references)
- Semantic highlighting
- Docstring support
- Import organization
- Refactoring tools
- Jupyter Notebook support
- Performance optimizations for VS Code

### The Relationship

```
┌─────────────────────────────────────────────────────────┐
│                      Pylance                            │
│  (VS Code Extension - Proprietary)                      │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │         Pyright Type Checking Engine              │ │
│  │         (Open Source - Bundled)                   │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  + IntelliSense                                         │
│  + Code Navigation                                      │
│  + Semantic Highlighting                                │
│  + Refactoring Tools                                    │
│  + VS Code Integration                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Standalone Pyright CLI                     │
│  (Open Source - Separate Installation)                  │
│                                                         │
│  - Command-line type checking                           │
│  - CI/CD integration                                    │
│  - Pre-commit hooks                                     │
│  - Automation scripts                                   │
└─────────────────────────────────────────────────────────┘
```

**Key Point:** Pylance **uses** Pyright's engine but is not a replacement for the standalone Pyright CLI.

---

## 2. Current Setup Analysis

### What We're Using

#### In VS Code (IDE)
- **Pylance extension** (installed with Python extension)
  - Provides type checking in the editor
  - Shows type errors as you type
  - Provides IntelliSense and code navigation
  - Uses bundled Pyright engine

#### In Command Line / CI/CD
- **Standalone Pyright CLI** (via `uvx pyright`)
  - Used in `scripts/dev.sh` for manual type checking
  - Used in `.github/workflows/code-quality.yml` for CI/CD
  - Independent of VS Code
  - Can be run in any environment

### Configuration

Both Pylance and standalone Pyright read the same configuration:
- `[tool.pyright]` section in `pyproject.toml`
- `pyrightconfig.json` (if present)

**Important:** Configuration is shared, so type checking behavior is consistent between IDE and CLI.

---

## 3. IDE vs CLI Usage

### Pylance (VS Code Extension)

**Purpose:** Real-time IDE features while coding

**Features:**
- ✅ Type checking as you type
- ✅ IntelliSense (auto-completion)
- ✅ Go to definition / Find references
- ✅ Semantic highlighting
- ✅ Hover information
- ✅ Signature help
- ✅ Code actions (quick fixes)
- ✅ Refactoring tools

**When to Use:**
- During active development in VS Code
- For immediate feedback while writing code
- For code navigation and exploration

**Limitations:**
- Only works in VS Code
- Cannot be used in CI/CD pipelines
- Cannot be run from command line
- Not available in other editors

### Standalone Pyright CLI

**Purpose:** Automated type checking in scripts, CI/CD, and command line

**Features:**
- ✅ Command-line type checking
- ✅ CI/CD integration
- ✅ Pre-commit hooks
- ✅ Automation scripts
- ✅ Works in any environment
- ✅ Can be run on servers
- ✅ Batch processing

**When to Use:**
- In CI/CD pipelines (GitHub Actions, etc.)
- In pre-commit hooks
- For command-line type checking
- In automated testing
- On servers without GUI
- In non-VS Code editors

**Limitations:**
- No IDE features (IntelliSense, navigation, etc.)
- No real-time feedback
- Terminal-only output

---

## 4. Recommendation: Use Both

### ✅ Recommended Approach

**Use Pylance for IDE features:**
- Install Pylance extension in VS Code (comes with Python extension)
- Get real-time type checking and IntelliSense while coding
- Benefit from code navigation and refactoring tools

**Use standalone Pyright CLI for automation:**
- Install via `uvx pyright` for command-line type checking
- Use in CI/CD workflows for automated validation
- Use in convenience scripts for manual checks
- Use in pre-commit hooks (optional)

### Why Both?

1. **Complementary Purposes:**
   - Pylance = IDE experience (real-time, interactive)
   - Pyright CLI = Automation (CI/CD, scripts, hooks)

2. **Consistent Behavior:**
   - Both use same configuration (`[tool.pyright]`)
   - Same type checking rules
   - Same error messages

3. **Best of Both Worlds:**
   - Real-time feedback in IDE (Pylance)
   - Automated validation in CI/CD (Pyright CLI)
   - Command-line access for scripts (Pyright CLI)

4. **No Redundancy:**
   - Pylance is for IDE only (cannot replace CLI)
   - Pyright CLI is for automation only (cannot replace IDE features)

---

## 5. Current Implementation Status

### ✅ Already Implemented Correctly

Our current setup already follows best practices:

#### Pylance (IDE)
- ✅ Installed via Python extension in VS Code
- ✅ Provides real-time type checking in editor
- ✅ Reads configuration from `[tool.pyright]` in `pyproject.toml`

#### Standalone Pyright CLI (Automation)
- ✅ Used in `scripts/dev.sh` via `uvx pyright src/`
- ✅ Used in CI/CD via `uvx pyright src/`
- ✅ Configuration in `pyproject.toml` (`[tool.pyright]`)
- ✅ Not in pre-commit hooks (intentionally moved to CI/CD for performance)

### Configuration Sharing

Both Pylance and Pyright CLI read the same configuration:

```toml
[tool.pyright]
pythonVersion = "3.10"
pythonPlatform = "Linux"
include = ["src"]
exclude = ["tests/", "docs/", ...]
typeCheckingMode = "standard"
# ... all other settings
```

**Result:** Consistent type checking behavior in IDE and CI/CD.

---

## 6. No Changes Needed

### Current Setup is Optimal

Our implementation already follows Microsoft's recommended approach:

1. **Pylance in VS Code:**
   - Automatically installed with Python extension
   - Provides IDE features
   - Uses bundled Pyright engine

2. **Standalone Pyright CLI:**
   - Installed via `uvx pyright` (no permanent installation)
   - Used for command-line type checking
   - Used in CI/CD workflows
   - Shares configuration with Pylance

### Why This Works

- **No Duplication:** Pylance and Pyright CLI serve different purposes
- **Consistent Configuration:** Both read `[tool.pyright]` from `pyproject.toml`
- **Performance:** Pyright CLI not in pre-commit (moved to CI/CD)
- **Flexibility:** `uvx` allows running without permanent installation

---

## 7. Common Misconceptions

### ❌ Misconception 1: "Pylance replaces Pyright CLI"
**Reality:** Pylance is VS Code-specific and cannot be used for command-line type checking or CI/CD.

### ❌ Misconception 2: "Installing Pyright CLI is redundant if you have Pylance"
**Reality:** Pylance's bundled Pyright is only accessible within VS Code. You need standalone Pyright CLI for automation.

### ❌ Misconception 3: "Pylance and Pyright CLI will conflict"
**Reality:** They share the same configuration and work together seamlessly.

### ❌ Misconception 4: "You should only use one or the other"
**Reality:** Microsoft designed them to be used together - Pylance for IDE, Pyright CLI for automation.

---

## 8. Verification

### Check Pylance in VS Code

1. Open VS Code
2. Open a Python file
3. Check status bar - should show "Pylance" as language server
4. Hover over a variable - should show type information
5. Type errors should appear in real-time

### Check Standalone Pyright CLI

```bash
# Check version
uvx pyright --version

# Run type checking
uvx pyright src/

# Should use configuration from pyproject.toml
```

### Verify Configuration Sharing

Both should report the same type errors for the same code.

---

## 9. Documentation Updates

### Files Already Updated

- ✅ `pyproject.toml` - Contains `[tool.pyright]` configuration
- ✅ `scripts/dev.sh` - Uses `uvx pyright src/`
- ✅ `.github/workflows/code-quality.yml` - Uses `uvx pyright src/`
- ✅ `docs/dev-workflow-quick-reference.md` - Documents Pyright usage
- ✅ `.augment/rules/prefer-uvx-for-tools.md` - Mentions Pyright

### No Changes Needed

All documentation correctly reflects the dual usage of Pylance (IDE) and Pyright CLI (automation).

---

## 10. Summary

### The Bottom Line

**Pylance** and **Pyright** are complementary tools, not alternatives:

| Tool | Purpose | Where Used | Installation |
|------|---------|------------|--------------|
| **Pylance** | IDE features | VS Code only | VS Code extension |
| **Pyright CLI** | Automation | Command line, CI/CD | `uvx pyright` |

**Our Setup:** ✅ Optimal - Using both tools for their intended purposes

**Configuration:** ✅ Shared via `[tool.pyright]` in `pyproject.toml`

**Performance:** ✅ Pyright CLI in CI/CD only (not in pre-commit for speed)

**Recommendation:** ✅ No changes needed - current implementation is correct

---

## References

- **Pyright GitHub:** https://github.com/microsoft/pyright
- **Pylance GitHub:** https://github.com/microsoft/pylance-release
- **Pyright Documentation:** https://microsoft.github.io/pyright/
- **Pylance Documentation:** https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance


---
**Logseq:** [[TTA.dev/Docs/Pyright-vs-pylance-analysis]]
