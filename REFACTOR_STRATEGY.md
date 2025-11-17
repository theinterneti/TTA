# Repository Reorganization Strategy

**Branch**: `refactor/repo-reorg`
**Date**: 2025-11-16
**Architect**: GitHub Copilot (Lead)
**Execution**: Cline (Mechanical), Copilot (Architectural)

## Vision

Separate **TTA.dev platform** (agentic development tools) from **TTA application** (therapeutic game) to create clear boundaries, improve maintainability, and enable independent evolution.

## Directory Structure

### Top-Level Organization

```text
/
├── _archive/              # Deprecated tools (kiro, openhands, gemini workflows)
├── platform_tta_dev/      # TTA.dev agentic platform
├── app_tta/               # TTA therapeutic game application
├── .github/               # Shared CI/CD
├── docker/                # Shared infrastructure
└── monitoring/            # Cross-platform observability
```

### platform_tta_dev Structure

```text
platform_tta_dev/
├── shared/
│   ├── observability_core/    # Tracing, metrics, logging frameworks
│   ├── mcp_core/              # MCP server base scaffolding
│   ├── cli_core/              # CLI utilities
│   └── workflows_core/        # Workflow runner, prompt loader, MD validation
├── docs/
└── components/
    ├── hypertool/
    ├── serena/
    ├── ace_framework/
    ├── anthropic_skills/
    ├── cline_cli/
    ├── e2b/
    └── logseq/
```

### Component Internal Structure (Standard)

Each component follows this pattern:

```text
component_name/
├── README.md              # Component overview, usage, integration points
├── core/                  # Implementation (language-agnostic)
├── mcp/                   # MCP server definitions
│   ├── servers/           # Server entrypoints
│   └── config/            # Capabilities, transport, auth
├── cli/                   # Command-line interfaces (if applicable)
├── workflows/             # Markdown-as-code
│   ├── prompts/           # Prompt templates with tracing metadata
│   ├── chatmodes/         # Chatmode/persona definitions
│   └── scenarios/         # Scripted flows
├── personas/              # Persona definitions (md/json/yaml)
├── integrations/          # Adapters
│   ├── tta_app/           # Integration with TTA game
│   ├── platform/          # Integration with other components
│   └── external/          # Third-party services
└── observability/
    ├── tracing/           # Span naming, attributes, prompt tracing
    ├── metrics/           # Counters, histograms, dashboards
    └── logging/           # Structured log schemas
```

## Migration Sequence

Components will be migrated sequentially to ensure stability and enable review at each step.

### Sequence

1. **hypertool** - Personas, MCPs, workflows (foundation)
2. **serena** - Code search, memory (core dev primitive)
3. **ace_framework** - Agent architecture (behavioral framework)
4. **anthropic_skills** - Claude-specific capabilities
5. **cline_cli** - CLI interface over platform
6. **e2b** - Sandboxed execution runtime
7. **logseq** - Knowledge base integration

### Migration Protocol

For each component:

1. **Plan** - Architect maps current → target structure
2. **Issue** - Create tracking issue with acceptance criteria
3. **Execute** - Cline performs mechanical migration
4. **Verify** - Architect reviews, approves, merges
5. **Commit** - Single atomic commit per component
6. **Report** - Status update, await go-ahead for next

## Architectural Decisions

### Markdown as Code

`.md` files in `workflows/` and `personas/` are treated as first-class code:

- Version controlled
- Validated via schema
- Tested for reference correctness
- Traced via frontmatter metadata

Example prompt with tracing:

```markdown
---
trace_id: "hypertool.persona.activate"
span_attributes:
  persona: "QualityGuardian"
  context: "code_review"
---

# Quality Guardian Activation

You are the Quality Guardian...
```

### Observability Integration

Each component defines observability hooks at migration time:

- **Tracing**: Span naming conventions, attribute schemas
- **Metrics**: Component-specific counters/histograms
- **Logging**: Structured log field definitions

Shared observability core provides:

- Common instrumentation helpers
- Circuit breaker integration
- Standardized metric/log naming

### MCP vs CLI vs Integration

**MCP** (`mcp/`):

- Present when component exposes MCP server endpoints
- Contains server definitions, capabilities, transport config

**CLI** (`cli/`):

- Present when component provides command-line interface
- May consume MCP servers internally

**Integrations** (`integrations/`):

- Adapters for connecting to TTA app or other components
- Distinguishes "component logic" from "how it plugs in"

## Delegation Strategy

### Cline (Mechanical)

- File/directory moves
- Symlink updates
- Boilerplate READMEs (from templates)
- Archive consolidation
- Reference path updates (verified by tests)

### Copilot (Architectural)

- Component boundary decisions
- Observability hook definitions
- Integration point design
- Migration sequence approval
- Final structure validation

## Success Criteria

- [ ] All deprecated tools in `_archive/` with documentation
- [ ] `platform_tta_dev/` and `app_tta/` directories established
- [ ] All 7 components migrated sequentially
- [ ] All symlinks updated, no broken references
- [ ] Observability hooks documented per component
- [ ] CI/CD pipelines functional
- [ ] Single clean commit history on `refactor/repo-reorg`

## Next Steps

1. Cline executes Issue #126 (archive consolidation)
2. Cline executes Issue #127 (directory structure)
3. Copilot approves structure, defines hypertool boundaries
4. Cline executes Issue #128 (augment migration)
5. Begin component migrations (hypertool → serena → ...)

---

**Status**: Phase 2 in progress
**Last Updated**: 2025-11-16
**Tracking**: See GitHub issues #126-129
