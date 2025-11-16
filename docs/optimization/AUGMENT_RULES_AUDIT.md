# Augment Rules Audit - Migration to TTA Agentic Primitives

**Date**: 2025-10-27
**Status**: Audit Complete - Migration Plan Ready

## Executive Summary

Current `.augment/rules/` contains **41,738 bytes** of content, with only **373 bytes** (0.9%) being truly Augment-specific. The remaining **41,365 bytes** (99.1%) should be migrated to TTA's agentic primitives system for better organization and reduced AI agent context clutter.

**Recommendation**: Migrate all files except `Use-your-tools.md` and `avoid-long-files.md` to appropriate TTA locations.

## File-by-File Analysis

### 1. Use-your-tools.md (241 bytes) ✅ KEEP
**Content Type**: Tool availability reference
**Applicability**: Augment-specific (lists Augment MCP tools)
**Loading**: Always-on
**Current Size**: 241 bytes

**Analysis**:
- Lists Augment-specific MCP tools (Playwright, Context7, Sequential Thinking, GitHub)
- Truly Augment-specific content
- Minimal size impact
- Provides quick reference for available tools

**Recommendation**: ✅ **KEEP** - This is the only truly Augment-specific rule

---

### 2. avoid-long-files.md (132 bytes) ✅ KEEP
**Content Type**: Best practice
**Applicability**: Universal coding standard
**Loading**: Always-on
**Current Size**: 132 bytes

**Analysis**:
- Simple best practice: "Break up files longer than 300-400 lines"
- Universal coding standard, not Augment-specific
- Minimal size impact
- Could be moved to AGENTS.md, but size is negligible

**Recommendation**: ✅ **KEEP** - Minimal size, universal best practice

---

### 3. prefer-uvx-for-tools.md (4,376 bytes) 🔄 MIGRATE
**Content Type**: Tool usage pattern + workflow procedure
**Applicability**: TTA-specific (UV package manager)
**Loading**: Auto-triggered
**Current Size**: 4,376 bytes

**Analysis**:
- TTA-specific guidance for UV package manager
- Contains workflow procedures (when to use `uvx` vs `uv run`)
- Contains examples and migration patterns
- Should be in TTA's instruction system, not Augment-specific

**Migration Target**: `.github/instructions/package-management.md`
**Format**: Instruction file with `applyTo` patterns
**Estimated Size After Migration**: 4,376 bytes (no reduction, just reorganization)

**Migration Plan**:
```yaml
---
applyTo:
  - "pyproject.toml"
  - "uv.lock"
  - "scripts/**"
  - "**/*.sh"
auto_trigger: true
applies_to: ["uv", "uvx", "package manager", "dependencies", "tool execution"]
description: "UV package manager usage patterns for TTA"
---
```

---

### 4. use-serena-tools.md (13,371 bytes) 🔄 MIGRATE
**Content Type**: Tool usage guide + best practices
**Applicability**: Universal (Serena is available to all AI agents)
**Loading**: Auto-triggered
**Current Size**: 13,371 bytes

**Analysis**:
- Comprehensive guide for using Serena MCP tools
- Contains semantic code operation patterns
- Contains examples and anti-patterns
- Should be in TTA's instruction system as universal AI agent guidance

**Migration Target**: `.github/instructions/serena-code-navigation.md`
**Format**: Instruction file with `applyTo` patterns
**Estimated Size After Migration**: 13,371 bytes (no reduction, just reorganization)

**Migration Plan**:
```yaml
---
applyTo:
  - "src/**/*.py"
  - "tests/**/*.py"
  - "**/*.ts"
  - "**/*.js"
auto_trigger: true
applies_to: ["code navigation", "refactoring", "symbol search", "code analysis", "serena"]
description: "Serena MCP tool usage for semantic code operations"
---
```

---

### 5. ai-context-management.md (4,166 bytes) 🔄 MIGRATE
**Content Type**: Workflow reference + tool usage
**Applicability**: TTA-specific (references TTA's context management system)
**Loading**: Auto-triggered
**Current Size**: 4,166 bytes

**Analysis**:
- References `.augment/context/cli.py` (TTA-specific)
- References `.augment/workflows/context-management.workflow.md`
- Should be in TTA's instruction system
- Already has workflow file (context-management.workflow.md)

**Migration Target**: `.github/instructions/ai-context-sessions.md`
**Format**: Instruction file with `applyTo` patterns
**Estimated Size After Migration**: 2,083 bytes (50% reduction - remove duplicates with workflow)

**Migration Plan**:
```yaml
---
applyTo:
  - ".augment/context/**"
  - "**/*.workflow.md"
auto_trigger: true
applies_to: ["multi-session", "context management", "ai session", "development workflow"]
description: "AI context session management for multi-session development"
---
```

**Content to Keep**: Quick commands, importance scores, when to use
**Content to Remove**: Detailed patterns (already in workflow file)

---

### 6. docker-dependency-migration.primitive.md (13,389 bytes) 🔄 MIGRATE
**Content Type**: Agentic primitive (workflow pattern)
**Applicability**: TTA-specific (Docker migration pattern)
**Loading**: Auto-triggered
**Current Size**: 13,389 bytes

**Analysis**:
- Comprehensive Docker migration primitive
- Contains detailed workflow procedures
- Already has workflow file (docker-migration.workflow.md)
- Should be in TTA's primitives system, not Augment-specific

**Migration Target**: `.github/primitives/docker-dependency-migration.primitive.md`
**Format**: Primitive file (new directory structure)
**Estimated Size After Migration**: 6,695 bytes (50% reduction - remove duplicates with workflow)

**Migration Plan**:
```yaml
---
primitive_type: infrastructure_migration
category: docker
applies_to: ["docker", "docker-compose", "service management", "infrastructure migration"]
auto_trigger: true
description: "Systematic Docker dependency migration pattern"
---
```

**Content to Keep**: Pattern overview, success criteria, anti-patterns
**Content to Remove**: Detailed step-by-step procedures (already in workflow file)

---

### 7. imported/copilot-instructions.md (8,063 bytes) 🔄 MIGRATE
**Content Type**: Project context + architecture patterns
**Applicability**: Universal (TTA project overview)
**Loading**: Auto-triggered (imported from .github/copilot-instructions.md)
**Current Size**: 8,063 bytes

**Analysis**:
- Duplicate of `.github/copilot-instructions.md`
- Should not be in `.augment/rules/` at all
- Already exists in proper location

**Migration Target**: DELETE (already exists in `.github/copilot-instructions.md`)
**Estimated Size After Migration**: 0 bytes (100% reduction - remove duplicate)

**Migration Plan**: Simply delete this file, it's a duplicate

---

## Migration Summary

### Files to Keep (373 bytes)
1. ✅ `Use-your-tools.md` (241 bytes) - Augment-specific tool reference
2. ✅ `avoid-long-files.md` (132 bytes) - Universal best practice

### Files to Migrate (41,365 bytes)
1. 🔄 `prefer-uvx-for-tools.md` → `.github/instructions/package-management.md` (4,376 bytes)
2. 🔄 `use-serena-tools.md` → `.github/instructions/serena-code-navigation.md` (13,371 bytes)
3. 🔄 `ai-context-management.md` → `.github/instructions/ai-context-sessions.md` (2,083 bytes after reduction)
4. 🔄 `docker-dependency-migration.primitive.md` → `.github/primitives/docker-dependency-migration.primitive.md` (6,695 bytes after reduction)
5. ❌ `imported/copilot-instructions.md` → DELETE (duplicate, 0 bytes after deletion)

### Expected Savings
- **Before Migration**: 41,738 bytes in `.augment/rules/`
- **After Migration**: 373 bytes in `.augment/rules/`
- **Reduction**: 41,365 bytes (99.1% reduction)
- **New Location Sizes**:
  - `.github/instructions/`: +19,830 bytes (3 new files)
  - `.github/primitives/`: +6,695 bytes (1 new file)
  - Total migrated: 26,525 bytes (36% reduction from deduplication)

## Directory Structure Changes

### Before
```
.augment/rules/
├── Use-your-tools.md (241 bytes) [always-on]
├── avoid-long-files.md (132 bytes) [always-on]
├── prefer-uvx-for-tools.md (4,376 bytes) [auto-trigger]
├── use-serena-tools.md (13,371 bytes) [auto-trigger]
├── ai-context-management.md (4,166 bytes) [auto-trigger]
├── docker-dependency-migration.primitive.md (13,389 bytes) [auto-trigger]
└── imported/
    └── copilot-instructions.md (8,063 bytes) [duplicate]
Total: 41,738 bytes
```

### After
```
.augment/rules/
├── Use-your-tools.md (241 bytes) [always-on]
└── avoid-long-files.md (132 bytes) [always-on]
Total: 373 bytes

.github/instructions/
├── package-management.md (4,376 bytes) [auto-trigger]
├── serena-code-navigation.md (13,371 bytes) [auto-trigger]
└── ai-context-sessions.md (2,083 bytes) [auto-trigger]
Total: 19,830 bytes

.github/primitives/ (NEW)
└── docker-dependency-migration.primitive.md (6,695 bytes) [auto-trigger]
Total: 6,695 bytes
```

## Benefits of Migration

### 1. Reduced Augment-Specific Context
- 99.1% reduction in `.augment/rules/` size
- Only truly Augment-specific content remains
- Cleaner separation of concerns

### 2. Better Organization
- TTA-specific patterns in TTA's agentic primitives system
- Universal AI agent guidance in `.github/instructions/`
- Primitives in dedicated `.github/primitives/` directory

### 3. Improved Discoverability
- Instructions co-located with related files
- Primitives in dedicated directory
- Clear separation between Augment and TTA content

### 4. Deduplication
- Remove duplicate copilot-instructions.md (8,063 bytes saved)
- Condense files that reference workflows (8,777 bytes saved)
- Total deduplication: 16,840 bytes (40% of migrated content)

## Migration Execution Plan

### Phase 1: Create New Directories
```bash
mkdir -p .github/primitives
```

### Phase 2: Migrate Files
1. Create `.github/instructions/package-management.md` from `prefer-uvx-for-tools.md`
2. Create `.github/instructions/serena-code-navigation.md` from `use-serena-tools.md`
3. Create `.github/instructions/ai-context-sessions.md` from `ai-context-management.md` (condensed)
4. Create `.github/primitives/docker-dependency-migration.primitive.md` from `docker-dependency-migration.primitive.md` (condensed)

### Phase 3: Update Cross-References
1. Update AGENTS.md references to new locations
2. Update workflow files to reference new instruction files
3. Update any scripts that reference old locations

### Phase 4: Remove Old Files
```bash
rm .augment/rules/prefer-uvx-for-tools.md
rm .augment/rules/use-serena-tools.md
rm .augment/rules/ai-context-management.md
rm .augment/rules/docker-dependency-migration.primitive.md
rm -rf .augment/rules/imported/
```

### Phase 5: Verify
1. Test auto-trigger behavior
2. Verify character count reduction
3. Confirm functionality preserved

## Success Criteria

- [ ] `.augment/rules/` reduced to 373 bytes (99.1% reduction)
- [ ] All migrated files have proper YAML frontmatter
- [ ] All cross-references updated
- [ ] No functionality lost
- [ ] Auto-trigger behavior verified
- [ ] Character count within limit

## Related Documentation

- **INVESTIGATION_SUMMARY.md** - Character limit investigation
- **OPTIMIZATION_REPORT.md** - Overall optimization status
- **FILE_LOADING_ANALYSIS.md** - File loading behavior analysis

---

**Last Updated**: 2025-10-27
**Status**: Audit Complete - Ready for Migration
**Next**: Execute migration plan (pending approval)
