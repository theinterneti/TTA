# Pylance Configuration for TTA Project

**Last Updated**: 2025-10-27
**Status**: Active - Optimized for Python 3.12+ with workspace package support

## Overview

This document describes the Pylance and Pyright configuration for the TTA (Therapeutic Text Adventure) project. The configuration is optimized for:

- **Python 3.12+** type checking
- **Workspace package** support (`tta-ai-framework`, `tta-narrative-engine`)
- **Quality gate** alignment (Development: ≥70%, Staging: ≥80%, Production: ≥85% coverage)
- **Performance optimization** for large codebase analysis

## Configuration Files

### Primary Configuration: `pyrightconfig.json`

The main type checking configuration is in `pyrightconfig.json` (takes precedence over `pyproject.toml`):

```json
{
  "include": [
    "src",
    "packages/tta-ai-framework/src",
    "packages/tta-narrative-engine/src"
  ],
  "pythonVersion": "3.12",
  "pythonPlatform": "Linux",
  "typeCheckingMode": "standard",
  "executionEnvironments": [
    {
      "root": "src",
      "extraPaths": [
        "packages/tta-ai-framework/src",
        "packages/tta-narrative-engine/src"
      ]
    }
  ]
}
```

### VS Code Settings: `.vscode/settings.json`

Pylance-specific UI and performance settings (non-conflicting with `pyrightconfig.json`):

```json
{
  "python.analysis.diagnosticMode": "workspace",
  "python.analysis.indexing": true,
  "python.analysis.userFileIndexingLimit": 5000,
  "python.analysis.packageIndexDepths": [
    { "name": "fastapi", "depth": 3 },
    { "name": "pydantic", "depth": 3 },
    { "name": "redis", "depth": 2 },
    { "name": "neo4j", "depth": 2 }
  ],
  "python.analysis.autoImportCompletions": true,
  "python.analysis.inlayHints.functionReturnTypes": true,
  "python.analysis.persistAllIndices": true
}
```

### Backup Configuration: `pyproject.toml`

The `[tool.pyright]` section in `pyproject.toml` serves as a backup and is used by CLI tools:

```toml
[tool.pyright]
pythonVersion = "3.12"
pythonPlatform = "Linux"
include = ["src", "packages/tta-ai-framework/src", "packages/tta-narrative-engine/src"]
extraPaths = [
    "packages/tta-ai-framework/src",
    "packages/tta-narrative-engine/src"
]
typeCheckingMode = "standard"
```

## Key Features

### 1. Workspace Package Support

The configuration includes proper paths for workspace packages:

- `packages/tta-ai-framework/src` - AI framework and orchestration models
- `packages/tta-narrative-engine/src` - Narrative generation engine

This enables proper import resolution for:

```python
from tta_ai.orchestration.models import AgentType
from tta_narrative.engine import NarrativeGenerator
```

### 2. Package Index Depths

Optimized indexing depths for main dependencies:

| Package | Depth | Reason |
|---------|-------|--------|
| fastapi | 3 | Deep module structure (routers, dependencies, etc.) |
| pydantic | 3 | Complex validation and model hierarchy |
| redis | 2 | Common submodules (asyncio, sentinel) |
| neo4j | 2 | Driver and session management |
| langchain | 2 | Core and community packages |
| torch | 2 | Neural network modules |

### 3. Inlay Hints

Enabled for better code readability:

- **Function return types**: Shows return type annotations inline
- **Variable types**: Shows inferred types for variables
- **Call argument names**: Shows parameter names at call sites (partial mode)
- **Pytest parameters**: Shows fixture types in test functions

### 4. Performance Optimizations

- **Workspace diagnostic mode**: Analyzes entire workspace for comprehensive quality checks
- **Persistent indices**: Caches analysis results between VS Code sessions
- **User file indexing limit**: 5000 files (sufficient for TTA codebase)

## Type Checking Modes

### Current: Standard Mode

The project uses `"typeCheckingMode": "standard"` which provides:

- ✅ Type inference for variables and return types
- ✅ Error detection for type mismatches
- ✅ Optional type checking (None-safety)
- ⚠️ Warnings for missing type stubs
- ℹ️ Information for unknown parameter types

### Upgrade Path: Strict Mode

For production-level quality (≥85% coverage), consider upgrading to `"strict"`:

```json
{
  "typeCheckingMode": "strict"
}
```

This adds:
- ❌ Errors for untyped function definitions
- ❌ Errors for untyped class decorators
- ❌ Errors for unknown parameter types

## Quality Gate Alignment

### Development (≥70% coverage, ≥75% mutation score)

Current `standard` mode is appropriate. Focus on:
- Fixing type errors
- Adding type hints to new code
- Resolving import issues

### Staging (≥80% coverage, ≥80% mutation score)

Consider enabling stricter optional checks in `pyrightconfig.json`:

```json
{
  "reportOptionalMemberAccess": "error",
  "reportOptionalSubscript": "error",
  "reportOptionalCall": "error"
}
```

### Production (≥85% coverage, ≥85% mutation score)

Upgrade to `strict` mode and ensure:
- All functions have type annotations
- All class methods have return type hints
- No `Any` types in public APIs

## Verification

### Check Configuration

```bash
# Verify Pyright version and configuration
uv run pyright --version

# Check specific file
uv run pyright --stats src/agent_orchestration/models.py

# Check workspace packages
uv run pyright --stats packages/tta-ai-framework/src/tta_ai/orchestration/models.py
```

### Test Import Resolution

```bash
# Verify workspace package imports work
uv run python -c "from tta_ai.orchestration.models import AgentType; print(AgentType.IPA)"
```

### Expected Output

```
pyright 1.1.406
0 errors, 0 warnings, 0 informations
Completed in 2.073sec
```

## Troubleshooting

### Issue: "Cannot find module 'tta_ai'"

**Solution**: Ensure workspace packages are in `include` and `extraPaths`:

```json
{
  "include": ["src", "packages/tta-ai-framework/src"],
  "executionEnvironments": [{
    "root": "src",
    "extraPaths": ["packages/tta-ai-framework/src"]
  }]
}
```

### Issue: Pylance settings ignored

**Cause**: `pyrightconfig.json` takes precedence over VS Code settings.

**Solution**: Move type checking settings to `pyrightconfig.json`, keep only UI/performance settings in `.vscode/settings.json`.

### Issue: Slow analysis performance

**Solutions**:
1. Reduce `userFileIndexingLimit` (currently 5000)
2. Decrease package index depths
3. Add more paths to `exclude` in `pyrightconfig.json`

## Best Practices

### 1. Use Modern Type Hints

```python
from __future__ import annotations  # Enable forward references

# Use | instead of Union
def process(data: str | None) -> dict[str, Any]:
    pass

# Use collections.abc for generic types
from collections.abc import Callable, Awaitable

async def handler(fn: Callable[[str], Awaitable[int]]) -> int:
    pass
```

### 2. Leverage Pydantic Models

```python
from pydantic import BaseModel, Field

class AgentMessage(BaseModel):
    message_id: str = Field(..., min_length=6)
    payload: dict[str, Any] = Field(default_factory=dict)
```

### 3. Use Enum for Type Safety

```python
from enum import Enum

class AgentType(str, Enum):
    IPA = "input_processor"
    WBA = "world_builder"
    NGA = "narrative_generator"
```

## Related Documentation

- **AGENTS.md** - Universal context for all AI agents
- **CLAUDE.md** - Claude-specific instructions
- **pyproject.toml** - Project dependencies and tool configuration
- **pyrightconfig.json** - Primary type checking configuration

## Changelog

### 2025-10-27 - Initial Configuration

- ✅ Added Pylance-specific settings to `.vscode/settings.json`
- ✅ Updated `pythonVersion` from 3.10 to 3.12 in all configs
- ✅ Added workspace package paths to `pyrightconfig.json`
- ✅ Configured package index depths for main dependencies
- ✅ Enabled inlay hints for better code readability
- ✅ Aligned type checking mode to `standard` across all configs
- ✅ Added performance optimizations (persistent indices, workspace diagnostics)

---

**Maintained by**: TTA Development Team
**Contact**: See AGENTS.md for project context


---
**Logseq:** [[TTA.dev/Docs/Development/Pylance_configuration]]
