# TTA Specifications

**Last Updated:** 2026-03-04
**Status:** Active — Spec-Driven Development (SDD)

---

## Overview

This directory contains the canonical specifications for the TTA (Therapeutic Text Adventure) platform. Specifications follow the **Spec-Anchored** approach: they are living, executable contracts that evolve alongside code.

### Boundary Rule

- **TTA specs** define the *What*: behavioral contracts, domain logic, therapeutic requirements
- **TTA.dev** provides the *How*: infrastructure primitives (circuit breaker, retry, tracing, etc.)

Specs must clearly separate domain behavior from infrastructure implementation. See `ARCHITECTURE.md` for the two-layer toolkit architecture.

---

## Directory Structure

```
specs/
├── README.md                              # This file — index and conventions
├── templates/                             # Spec authoring templates
│   ├── api.spec.template.md
│   ├── component.spec.template.md
│   └── feature.spec.template.md
│
├── agents/                                # Core agent behavioral contracts
│   ├── ipa-input-processing-agent.md      # IPA: intent extraction + safety validation
│   ├── wba-world-building-agent.md        # WBA: world state management
│   ├── nga-narrative-generator-agent.md   # NGA: narrative generation + graceful degradation
│   └── agent-orchestration-protocol.md    # Inter-agent coordination protocol
│
├── therapeutic-safety/                    # Therapeutic domain specifications
│   ├── crisis-detection.md               # 4-level crisis severity classification
│   ├── emotional-safety-system.md        # 5-level emotional safety classification
│   ├── therapeutic-integration.md         # Therapeutic goal tracking
│   └── safety-interop.md                 # Crisis ↔ Emotional Safety interop contract
│
├── persistence/                           # Data layer specifications
│   ├── redis-session-cache.md            # Key patterns, TTLs, messaging
│   ├── neo4j-story-graph.md             # Node/relationship schemas
│   └── data-retention-policy.md          # HIPAA-compliant retention
│
├── tta-dev-integration/                   # TTA ↔ TTA.dev boundary contracts
│   ├── primitive-mapping.md              # Primitive dependency map
│   ├── circuit-breaker-usage.md          # Circuit breaker delegation
│   └── observability-boundary.md         # Observability responsibility split
│
├── infrastructure/                        # Infrastructure orchestration specs
│   ├── orchestration.md                  # Component management (Docker, services)
│   └── observability-integration.md      # APM, dashboards, metrics
│
└── examples/                              # Example and test specifications
    ├── calculator-operations.md           # Async workflow validation
    └── example-component.md               # Template usage example
```

---

## Spec Status

| Spec | Status | Location |
|---|---|---|
| Orchestration (infrastructure) | ✅ Written | `infrastructure/orchestration.md` |
| Observability Integration | ✅ Written | `infrastructure/observability-integration.md` |
| Calculator Operations (example) | ✅ Written | `examples/calculator-operations.md` |
| Example Component (template) | ✅ Written | `examples/example-component.md` |
| IPA Agent | ❌ Not started | `agents/ipa-input-processing-agent.md` |
| WBA Agent | ❌ Not started | `agents/wba-world-building-agent.md` |
| NGA Agent | ❌ Not started | `agents/nga-narrative-generator-agent.md` |
| Agent Orchestration Protocol | ❌ Not started | `agents/agent-orchestration-protocol.md` |
| Crisis Detection | ❌ Not started | `therapeutic-safety/crisis-detection.md` |
| Emotional Safety System | ❌ Not started | `therapeutic-safety/emotional-safety-system.md` |
| Therapeutic Integration | ❌ Not started | `therapeutic-safety/therapeutic-integration.md` |
| Safety Interop | ❌ Not started | `therapeutic-safety/safety-interop.md` |
| Redis Session Cache | ❌ Not started | `persistence/redis-session-cache.md` |
| Neo4j Story Graph | ❌ Not started | `persistence/neo4j-story-graph.md` |
| Data Retention Policy | ❌ Not started | `persistence/data-retention-policy.md` |
| Primitive Mapping | ❌ Not started | `tta-dev-integration/primitive-mapping.md` |
| Circuit Breaker Usage | ❌ Not started | `tta-dev-integration/circuit-breaker-usage.md` |
| Observability Boundary | ❌ Not started | `tta-dev-integration/observability-boundary.md` |

---

## Conventions

### File Naming
- Use `kebab-case` for all spec filenames
- Prefix agent specs with their abbreviation: `ipa-`, `wba-`, `nga-`
- Use descriptive names that indicate the domain concept

### Spec Format
- Use the templates in `templates/` as starting points
- Every spec must include: **Overview**, **Requirements** (FR + NFR), **Architecture**, **Testing**, **Acceptance Criteria**
- Every spec must declare its TTA.dev primitive dependencies in a dedicated section

### Referencing from Agent Instructions
All agent instruction files (`CLAUDE.md`, `.github/copilot-instructions.md`, `.augment/instructions.md`, `.cline/instructions.md`) should reference specs as:

```markdown
## Canonical Specifications
- Agent contracts: `specs/agents/`
- Therapeutic safety: `specs/therapeutic-safety/`
- Persistence: `specs/persistence/`
- TTA.dev integration: `specs/tta-dev-integration/`
```

---

**Logseq:** [[TTA/Specs/README]]
