# TTA Specifications

**Last Updated:** 2026-03-23
**Status:** Active — Spec-Driven Development (SDD)

---

## Overview

This directory contains the canonical specifications for the TTA (Therapeutic Text Adventure) platform. Specifications follow the **Spec-Anchored** approach: they are living contracts that evolve alongside code and tests.

### Boundary Rule

- **TTA specs** define the *What*: behavioral contracts, domain logic, therapeutic requirements.
- **TTA.dev** provides the *How*: infrastructure primitives such as retry, timeout, circuit breaker, and observability.

Specs should keep that split explicit. See `ARCHITECTURE.md` for the two-layer toolkit architecture and the “Could it work for a recipe app?” decision rule.

---

## Directory Structure

```
specs/
├── README.md                              # This file — index and conventions
├── agents/
│   ├── README.md                          # Agent spec index
│   ├── agent-orchestration-protocol.md    # IPA ↔ WBA ↔ NGA contract
│   ├── ipa-input-processing-agent.md      # IPA behavior and dependencies
│   ├── nga-narrative-generator-agent.md   # NGA behavior and dependencies
│   └── wba-world-building-agent.md        # WBA behavior and dependencies
├── persistence/
│   ├── README.md                          # Persistence spec index
│   ├── data-retention-policy.md           # Retention + deletion policy draft
│   ├── neo4j-story-graph.md              # Neo4j graph persistence draft
│   └── redis-session-cache.md             # Redis cache/state contract
├── therapeutic-safety/
│   ├── README.md                          # Therapeutic safety spec index
│   ├── crisis-detection.md                # 4-level crisis detection contract
│   ├── emotional-safety-system.md         # 5-level output safety contract
│   ├── safety-interop.md                  # Crisis ↔ emotional safety boundary
│   └── therapeutic-integration.md         # Narrative therapeutic integration
├── tta-dev-integration/
│   ├── README.md                          # TTA ↔ TTA.dev boundary index
│   ├── circuit-breaker-usage.md           # Circuit breaker delegation contract
│   ├── observability-boundary.md          # Observability ownership split
│   └── primitive-mapping.md               # Primitive dependency map
├── examples/
│   └── README.md                          # Example-spec placeholder index
├── infrastructure/
│   └── README.md                          # Infrastructure-spec placeholder index
├── templates/
│   ├── api.spec.template.md
│   ├── component.spec.template.md
│   └── feature.spec.template.md
├── calculator_operations.md               # Existing example spec
├── example_component.md                   # Existing template example
├── observability-integration.md           # Existing observability spec
└── orchestration.md                       # Existing orchestration spec
```

---

## Spec Status

| Spec | Status | Location |
|---|---|---|
| Orchestration | ✅ Written | `specs/orchestration.md` |
| Observability Integration | ✅ Written | `specs/observability-integration.md` |
| Calculator Operations | ✅ Written | `specs/calculator_operations.md` |
| Example Component | ✅ Written | `specs/example_component.md` |
| IPA Input Processing Agent | ✅ Drafted | `specs/agents/ipa-input-processing-agent.md` |
| WBA World Building Agent | ✅ Drafted | `specs/agents/wba-world-building-agent.md` |
| NGA Narrative Generator Agent | ✅ Drafted | `specs/agents/nga-narrative-generator-agent.md` |
| Agent Orchestration Protocol | ✅ Drafted | `specs/agents/agent-orchestration-protocol.md` |
| Crisis Detection | ✅ Drafted | `specs/therapeutic-safety/crisis-detection.md` |
| Emotional Safety System | ✅ Drafted | `specs/therapeutic-safety/emotional-safety-system.md` |
| Therapeutic Integration | ✅ Drafted | `specs/therapeutic-safety/therapeutic-integration.md` |
| Safety Interop | ✅ Drafted | `specs/therapeutic-safety/safety-interop.md` |
| Redis Session Cache | ✅ Drafted | `specs/persistence/redis-session-cache.md` |
| Neo4j Story Graph | ✅ Drafted | `specs/persistence/neo4j-story-graph.md` |
| Data Retention Policy | ✅ Drafted | `specs/persistence/data-retention-policy.md` |
| Primitive Mapping | ✅ Drafted | `specs/tta-dev-integration/primitive-mapping.md` |
| Circuit Breaker Usage | ✅ Drafted | `specs/tta-dev-integration/circuit-breaker-usage.md` |
| Observability Boundary | ✅ Drafted | `specs/tta-dev-integration/observability-boundary.md` |

---

## Conventions

### File Naming
- Use `kebab-case` for new spec filenames.
- Prefix agent specs with their abbreviation where helpful: `ipa-`, `wba-`, `nga-`.
- Keep names aligned with the bounded context they describe.

### Spec Format
- Start from the templates in `specs/templates/` when possible.
- Lightweight specs in this repository usually include: **Overview**, **Scope/Responsibilities**, **Requirements**, **Interfaces/Dependencies**, **Testing/Validation**, and **Acceptance Criteria**.
- Every integration-oriented spec should name its relevant TTA.dev primitive dependencies explicitly.
- Draft status is acceptable when the code anchor exists but the implementation is still incomplete or split across adapters, shims, and tests.

### Layout Notes
- The top-level spec files are legacy but still canonical until migrated.
- The nested domain folders (`agents/`, `therapeutic-safety/`, `persistence/`, `tta-dev-integration/`) now hold the newer domain-specific drafts.

### Referencing from Agent Instructions
Agent instruction files should reference specs as:

```markdown
## Canonical Specifications
- Agent contracts: `specs/agents/`
- Therapeutic safety: `specs/therapeutic-safety/`
- Persistence: `specs/persistence/`
- TTA.dev integration: `specs/tta-dev-integration/`
- Existing legacy specs: `specs/*.md`
```

---

**Logseq:** [[TTA/Specs/README]]
