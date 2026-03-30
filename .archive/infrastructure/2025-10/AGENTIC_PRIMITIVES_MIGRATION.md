# Agentic Primitives Migration Summary

**Date**: 2025-10-26
**Status**: Complete
**Migration Type**: Dual Structure (`.github/` + `.augment/`)

## Overview

This document summarizes the migration of TTA's agentic primitives to match GitHub's proposed structure while maintaining backward compatibility with the existing `.augment/` structure.

## What Was Created

### 1. Root-Level Configuration Files

#### `apm.yml` - Agent Package Manager Configuration
- **Purpose**: Functions like `package.json` for AI-native projects
- **Contents**:
  - Workflow scripts for Agent CLI Runtimes (Copilot CLI, Auggie CLI)
  - MCP server dependencies
  - Environment variable requirements
  - Agent behavior configuration
  - Tool boundaries by role
  - Quality gates configuration

#### `AGENTS.md` - Universal Agent Context
- **Purpose**: Universal context standard for all AI agents
- **Contents**:
  - Project overview and architecture
  - Core patterns (multi-agent orchestration, circuit breakers)
  - Development workflow
  - Code conventions
  - Quality gates
  - Common commands
  - MCP server integration
  - Agent role boundaries

#### `CLAUDE.md` - Claude-Specific Instructions
- **Purpose**: Claude agent-specific guidance
- **Contents**:
  - Claude-specific capabilities
  - Recommended usage patterns
  - TTA-specific guidance
  - Component maturity workflow
  - Testing strategy
  - Code quality standards
  - Error handling patterns
  - AI context management

### 2. GitHub Directory Structure

#### `.github/instructions/` - Modular Instruction Files
Created instruction files with YAML frontmatter for selective context loading:

1. **`safety.instructions.md`**
   - **Applies To**: `src/components/therapeutic_safety/**`, `src/player_experience/**`, `tests/security/**`
   - **Priority**: Critical
   - **Contents**: Therapeutic safety principles, security requirements, compliance (HIPAA, GDPR, WCAG), error handling, testing requirements

2. **`graph-db.instructions.md`**
   - **Applies To**: `src/agent_orchestration/**`, `src/components/gameplay_loop/**`, `src/living_worlds/**`, `tests/integration/**`
   - **Priority**: High
   - **Contents**: LangGraph agent orchestration, Neo4j query optimization, state management patterns, circuit breaker integration, performance monitoring

3. **`testing-battery.instructions.md`**
   - **Applies To**: `tests/**`, `src/**/test_*.py`
   - **Priority**: High
   - **Contents**: Testing philosophy, test organization, unit/integration/E2E patterns, comprehensive test battery, mutation testing, fixtures and mocks

#### `.github/chatmodes/` - Role-Based Chat Modes
Created chat mode files with tool boundaries:

1. **`safety-architect.chatmode.md`**
   - **Role**: Planning Specialist for therapeutic safety and security
   - **Model**: `anthropic/claude-sonnet-4`
   - **Allowed Tools**: fetch, search, githubRepo, codebase-retrieval, read/write_memory_Serena
   - **Denied Tools**: editFiles, runCommands, deleteFiles, deployStaging, deployProduction
   - **Focus**: Design and planning, code review, documentation

2. **`backend-implementer.chatmode.md`**
   - **Role**: Execution Specialist for secure API development
   - **Model**: `anthropic/claude-sonnet-4`
   - **Allowed Tools**: editFiles, runCommands, codebase-retrieval, testFailure, Serena tools
   - **Denied Tools**: deleteFiles, deployStaging, deployProduction, editFrontendAssets
   - **Focus**: Implementation, testing, refactoring

#### `.github/prompts/` - Agentic Workflow Files
Created workflow files for common tasks:

1. **`narrative-creation.prompt.md`**
   - **Purpose**: Multi-step narrative module creation and integration
   - **Model**: `anthropic/claude-sonnet-4`
   - **Tools**: codebase-retrieval, find_symbol_Serena, editFiles, runCommands, testFailure
   - **Phases**: Context Loading, Design, Implementation, Testing, Integration
   - **Validation Gates**: 3 human validation gates (Design Review, Implementation Review, Final Review)

#### `.github/specs/` - Specification Templates
Created specification templates for standardized blueprints:

1. **`therapeutic-feature.spec.md`**
   - **Type**: Feature specification
   - **Contents**: Overview, requirements (functional/non-functional), core components, API contracts, data models, database schema, therapeutic safety, testing strategy, validation criteria, implementation plan, risks, dependencies

2. **`api-endpoint.spec.md`**
   - **Type**: API endpoint specification
   - **Contents**: API contract (request/response), implementation, security, performance, testing, monitoring, documentation, validation criteria

## Directory Structure Comparison

### Before (`.augment/` only)
```
.augment/
├── chatmodes/
├── context/
├── docs/
├── instructions/
├── memory/
├── rules/
└── workflows/
```

### After (Dual Structure)
```
.github/
├── instructions/          # NEW: Modular instruction files
│   ├── safety.instructions.md
│   ├── graph-db.instructions.md
│   └── testing-battery.instructions.md
├── chatmodes/            # NEW: Role-based chat modes
│   ├── safety-architect.chatmode.md
│   └── backend-implementer.chatmode.md
├── prompts/              # NEW: Agentic workflow files
│   └── narrative-creation.prompt.md
└── specs/                # NEW: Specification templates
    ├── therapeutic-feature.spec.md
    └── api-endpoint.spec.md

.augment/                 # EXISTING: Maintained for backward compatibility
├── chatmodes/
├── context/
├── docs/
├── instructions/
├── memory/
├── rules/
└── workflows/

Root Files:
├── apm.yml               # NEW: Agent Package Manager config
├── AGENTS.md             # NEW: Universal agent context
└── CLAUDE.md             # NEW: Claude-specific instructions
```

## Key Features

### 1. YAML Frontmatter for Selective Loading
All instruction files use YAML frontmatter with `applyTo` patterns:

```yaml
---
applyTo:
  - "src/components/therapeutic_safety/**"
  - "src/player_experience/**"
priority: critical
category: safety
description: "Security and therapeutic safety standards"
---
```

### 2. Tool Boundaries for Security
Chat modes define explicit tool boundaries:

```yaml
---
mode: safety-architect
tools:
  allowed:
    - fetch
    - search
    - codebase-retrieval
  denied:
    - editFiles
    - deployProduction
---
```

### 3. Human Validation Gates
Workflow files include explicit validation gates:

```markdown
## 🚨 VALIDATION GATE 1: Design Review

**STOP**: Before proceeding to implementation, validate the design.

### Review Checklist
- [ ] Narrative structure aligns with specification
- [ ] Therapeutic objectives are clear
- [ ] Safety mechanisms are defined

**Action**: Get human approval before proceeding.
```

### 4. Specification-Driven Development
Specification templates provide implementation-ready blueprints:

- Explicit validation criteria
- Verifiable acceptance criteria
- Quality gate requirements
- Testing strategy
- Implementation plan

## Migration Strategy

### Phase 1: Dual Structure (Current)
- **Status**: Complete
- **Approach**: Maintain both `.github/` and `.augment/` structures
- **Rationale**: Backward compatibility while adopting new standards

### Phase 2: Gradual Migration (Future)
- **Timeline**: Next 2-4 weeks
- **Approach**: Gradually migrate `.augment/` content to `.github/`
- **Priority**: High-traffic files first

### Phase 3: Deprecation (Future)
- **Timeline**: After full migration
- **Approach**: Deprecate `.augment/` structure
- **Note**: Keep `.augment/context/` for session management

## Benefits

### 1. Standardization
- Aligns with GitHub's proposed agentic primitives structure
- Portable across different AI agents (Copilot, Claude, Auggie)
- Industry-standard approach

### 2. Security
- Explicit tool boundaries prevent unauthorized actions
- Role-based access control for AI agents
- Human validation gates for critical operations

### 3. Predictability
- Deterministic requirements in specifications
- Structured workflows with validation gates
- Clear acceptance criteria

### 4. Maintainability
- Modular instruction files
- Selective context loading
- Clear separation of concerns

## Usage Examples

### Using APM Scripts
```bash
# Run audit workflow
copilot run audit
# or
auggie run audit

# Promote component to staging
copilot run promote:staging
```

### Using Chat Modes
```
# Activate safety architect mode
@safety-architect Review the authentication implementation

# Activate backend implementer mode
@backend-implementer Implement the new preferences endpoint
```

### Using Workflow Files
```
# Execute narrative creation workflow
copilot run .github/prompts/narrative-creation.prompt.md
```

### Using Specification Templates
```bash
# Create new feature specification
cp .github/specs/therapeutic-feature.spec.md specs/my-feature.spec.md
# Edit and fill in details
```

## Next Steps

### Immediate (This Week)
- [x] Create `.github/` directory structure
- [x] Create `apm.yml` configuration
- [x] Create `AGENTS.md` and `CLAUDE.md`
- [x] Create initial instruction files
- [x] Create initial chat modes
- [x] Create initial workflow files
- [x] Create specification templates

### Short-Term (Next 2 Weeks)
- [ ] Create additional chat modes (frontend-dev, qa-engineer, devops)
- [ ] Create additional workflow files (bug-fix, refactoring, test-coverage-improvement)
- [ ] Create additional specification templates (component, integration)
- [ ] Update existing documentation to reference new structure
- [ ] Test with different AI agents (Copilot, Claude, Auggie)

### Long-Term (Next Month)
- [ ] Migrate remaining `.augment/` content to `.github/`
- [ ] Integrate with GitHub Copilot CLI
- [ ] Implement spec-kit for specification-driven development
- [ ] Add session splitting strategy for workflow phases
- [ ] Create comprehensive migration guide for developers

## References

- **GitHub Agentic Primitives**: `docs/development/github-agentic-primitives-comparison.md`
- **Original Proposal**: User-provided table of agentic primitives
- **TTA Context Files**: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- **APM Configuration**: `apm.yml`

---

**Last Updated**: 2025-10-26
**Status**: Complete - Dual structure implemented, ready for gradual migration


---
**Logseq:** [[TTA.dev/.archive/Infrastructure/2025-10/Agentic_primitives_migration]]
