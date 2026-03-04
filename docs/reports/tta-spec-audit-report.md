# TTA Spec Audit Report

**Date:** 2026-03-04
**Author:** Copilot Coding Agent
**Status:** Complete
**Scope:** `specs/`, `docs/`, `ARCHITECTURE.md`, `AGENTS.md`, agent instruction files

---

## Executive Summary

This report audits all existing specifications, architecture documents, and agent instructions in the TTA repository. The goal is to ensure that narrative and therapeutic agent specifications clearly map to the primitives provided by `TTA.dev` without mixing domain logic with infrastructure logic.

### Key Findings

| Category | Finding | Severity |
|---|---|---|
| **Spec Coverage** | No formal specs exist for IPA, WBA, or NGA agents | Critical |
| **Spec Coverage** | No formal spec for the Therapeutic Safety subsystem (crisis detection, emotional safety) | Critical |
| **Spec Coverage** | No formal spec for persistence layer (Redis session cache, Neo4j story graph) | High |
| **TTA.dev Boundary** | `ARCHITECTURE.md` defines a clear two-layer separation but no spec enforces it | High |
| **TTA.dev Boundary** | Circuit breaker is implemented in TTA (`src/agent_orchestration/circuit_breaker.py`) but spec does not reference TTA.dev primitive extraction | Medium |
| **Consistency** | Agent instruction files (4 files) reference IPA/WBA/NGA but point to no canonical spec | High |
| **Consistency** | `AGENTS.md` and `GEMINI.md` are stale redirect stubs pointing to a Logseq KB not in this repo | Medium |
| **Organization** | `specs/` has only 4 files; 2 are examples/templates, none cover core game agents | Critical |
| **Organization** | Therapeutic documentation is scattered across `docs/design/`, `docs/clinical/`, `src/` docstrings | High |

---

## 1. Discovery & Mapping

### 1.1 Core Agent Specifications

#### Current State

The three core agent types are defined in code (`src/agent_orchestration/agents.py` and `src/agent_orchestration/models.py`) via the `AgentType` enum:

| Agent | Enum Value | Code Location | Formal Spec |
|---|---|---|---|
| **IPA** (Input Processing Agent) | `"input_processor"` | `src/agent_orchestration/agents.py` | ❌ None |
| **WBA** (World Building Agent) | `"world_builder"` | `src/agent_orchestration/agents.py` | ❌ None |
| **NGA** (Narrative Generator Agent) | `"narrative_generator"` | `src/agent_orchestration/agents.py` | ❌ None |

All three inherit from the base `Agent` class which provides lifecycle management (start/stop), async messaging, health checks, metrics, and state export/import for recovery. However:

- **No behavioral specification** exists for any agent describing its inputs, outputs, success criteria, or failure modes.
- **No orchestration contract** exists specifying how IPA → WBA → NGA coordinate (message schemas, sequencing, timeouts).
- The `specs/orchestration.md` file covers infrastructure orchestration (Docker Compose, component management), not agent orchestration.

#### Agent Instruction File References

| File | IPA/WBA/NGA Mentioned? | Points to Spec? |
|---|---|---|
| `.augment/instructions.md` | ✅ Yes, with workflow diagram | ❌ No canonical spec |
| `.cline/instructions.md` | ✅ Yes, "multi-agent pipeline" | ❌ No canonical spec |
| `.github/copilot-instructions.md` | ✅ Yes, explicitly named | ❌ No canonical spec |
| `CLAUDE.md` | ❌ No agent names | ❌ N/A |

### 1.2 Therapeutic Safety Systems

#### Crisis Detection

**Code Location:** `src/agent_orchestration/crisis_detection/`

The crisis detection system defines a **four-level** severity classification (not five):

| Level | Enum | Description |
|---|---|---|
| `LOW` | `CrisisLevel.LOW` | Low-risk situation |
| `MODERATE` | `CrisisLevel.MODERATE` | Moderate concern |
| `HIGH` | `CrisisLevel.HIGH` | High-risk, escalation recommended |
| `CRITICAL` | `CrisisLevel.CRITICAL` | Critical—emergency intervention required |

Supporting types:
- **CrisisType** (7 types): `SELF_HARM`, `SUICIDAL_IDEATION`, `SUBSTANCE_ABUSE`, `DOMESTIC_VIOLENCE`, `EATING_DISORDER`, `PANIC_ATTACK`, `SEVERE_DEPRESSION`
- **InterventionType** (4 types): `AUTOMATED_RESPONSE`, `HUMAN_OVERSIGHT`, `EMERGENCY_SERVICES`, `THERAPEUTIC_REFERRAL`
- **EscalationStatus** (5 states): `NONE` → `PENDING` → `IN_PROGRESS` → `COMPLETED` | `FAILED`

**Data Models:** `CrisisAssessment` (assessment with confidence scores, risk/protective factors) and `CrisisIntervention` (complete intervention record with action tracking).

**Formal Spec:** ❌ None. Behavior is defined only in code and docstrings.

#### Emotional Safety System

**Code Location:** `src/components/gameplay_loop/narrative/emotional_safety_system.py`

This system defines a **five-level** safety classification:

| Level | Enum | Protocol |
|---|---|---|
| `SAFE` | `SafetyLevel.SAFE` | No action needed |
| `CAUTION` | `SafetyLevel.CAUTION` | Log + monitor |
| `WARNING` | `SafetyLevel.WARNING` | Log + reduce intensity + offer break |
| `UNSAFE` | `SafetyLevel.UNSAFE` | Halt content + grounding + provide exit |
| `CRISIS` | `SafetyLevel.CRISIS` | Immediate intervention + resources + notify support |

Content flags: `TRIGGERING`, `OVERWHELMING`, `INAPPROPRIATE`, `RETRAUMATIZING`, `HARMFUL`.

**Formal Spec:** ❌ None.

**⚠️ Discrepancy:** The crisis detection subsystem uses 4 levels (`LOW`→`CRITICAL`) while the emotional safety system uses 5 levels (`SAFE`→`CRISIS`). These two systems are in different packages and there is no specification defining how they interoperate or map to each other.

### 1.3 Persistence Layer

| Store | Purpose | Code Location | Formal Spec |
|---|---|---|---|
| **Redis** | Session cache, agent messaging | `src/agent_orchestration/messaging.py`, circuit breaker persistence | ❌ None |
| **Neo4j** | Story graph, player relationships, narrative history | `src/player_experience/database/`, `src/components/` | ❌ None |

The `docs/architecture/README.md` mentions both stores and the `docs/technical-specifications.md` lists them, but no formal specification defines:
- Data schemas (Redis key patterns, Neo4j node/relationship types)
- Retention policies
- Failover behavior
- Migration strategies

---

## 2. TTA.dev Integration Audit

### 2.1 Architecture Boundary Definition

`ARCHITECTURE.md` (updated 2026-01-09) clearly defines a two-layer separation:

| Layer | Location | Responsibility | Examples |
|---|---|---|---|
| **Layer 1: TTA.dev** (Universal) | `~/repos/TTA.dev/platform/` | Domain-agnostic primitives | Retry, fallback, timeout, cache, circuit breaker, observability |
| **Layer 2: TTA** (Game) | `~/repos/TTA/src/` | Narrative & therapeutic extensions | Agent orchestration, gameplay loop, therapeutic systems |

**Decision tree:** "Could it work for a recipe app? → YES → TTA.dev / NO → TTA"

This is well-articulated. However:

### 2.2 Boundary Violations & Ambiguities

#### Circuit Breaker

- **Implementation:** `src/agent_orchestration/circuit_breaker.py` (in TTA, not TTA.dev)
- **Architecture intent:** Circuit breaker is listed as a TTA.dev universal primitive
- **Current state:** The circuit breaker is fully implemented in TTA with Redis persistence, metrics, and registry
- **Spec gap:** `specs/observability-integration.md` references circuit breaker monitoring but does not specify whether TTA's implementation should delegate to a TTA.dev primitive or remain self-contained
- **Status:** The NGA's graceful degradation behavior uses this circuit breaker, but no spec formalizes: "The NGA MUST use the TTA.dev Circuit Breaker primitive for graceful degradation"

#### Observability

- `specs/observability-integration.md` is comprehensive (defines APM, dashboards, metrics) but conflates TTA.dev concerns (OpenTelemetry tracing, Prometheus metrics) with TTA concerns (LLM cost tracking, narrative-specific dashboards)
- No clear boundary line: "These metrics are TTA.dev's responsibility" vs. "These metrics are TTA's responsibility"

#### Missing "What" vs "How" Separation

| Component | "What" (Behavior) | "How" (Infrastructure) | Status |
|---|---|---|---|
| **IPA** | Extract intent, validate safety | TTA.dev Router + OpenTelemetry tracing | ❌ Not specified |
| **WBA** | Build/update world state | Neo4j persistence + Redis caching | ❌ Not specified |
| **NGA** | Generate narrative response | LLM via OpenRouter + Circuit Breaker | ❌ Not specified |
| **Crisis Detection** | Assess crisis severity, recommend intervention | TTA.dev alerting + escalation primitives | ❌ Not specified |
| **Emotional Safety** | Assess content safety, trigger protocols | Real-time monitoring + safety dashboard | ❌ Not specified |

### 2.3 Package Boundary Audit

| Package | Purpose | Depends On | Boundary Clear? |
|---|---|---|---|
| `tta-ai-framework` | AI orchestration infrastructure | langchain, langgraph, redis | ⚠️ Contains game-specific crisis detection code mirrored from `src/` |
| `tta-narrative-engine` | Narrative generation system | `tta-ai-framework` | ⚠️ Contains coherence/generation logic that could reference TTA.dev primitives but doesn't |

The `tta-ai-framework` package at `packages/tta-ai-framework/src/tta_ai/orchestration/crisis_detection/` mirrors the crisis detection code from `src/agent_orchestration/crisis_detection/`. This duplication has no specification governing which is canonical.

---

## 3. Organization & Consistency

### 3.1 Current `specs/` Directory State

```
specs/
├── calculator_operations.md      # Test/example spec (Phase 2 validation)
├── example_component.md          # Template example (Calculator class)
├── observability-integration.md  # Comprehensive observability spec
├── orchestration.md              # Infrastructure orchestration spec
└── templates/
    ├── api.spec.template.md
    ├── component.spec.template.md
    └── feature.spec.template.md
```

**Assessment:** Only `observability-integration.md` and `orchestration.md` are real specs. Neither covers the core game agents, therapeutic safety, or persistence. The spec templates exist but are unused for the primary domain components.

### 3.2 Current `docs/` Directory State

Documentation is scattered across 100+ files in ~40 subdirectories. Therapeutic and safety documentation spans:

- `docs/clinical/` (3 files: consultation framework, content overview, evidence-based frameworks)
- `docs/design/therapeutic-integration.md`
- `docs/design/clinical-consultation-framework.md`
- `docs/design/evidence-based-frameworks.md`
- Source code docstrings in `src/agent_orchestration/crisis_detection/`
- Source code docstrings in `src/components/gameplay_loop/narrative/emotional_safety_system.py`

There is no single document that a developer can read to understand the complete therapeutic safety pipeline.

### 3.3 Agent Instruction Consistency

| Instruction File | Last Meaningful Update | IPA/WBA/NGA | TTA.dev Primitives | Canonical Spec Reference |
|---|---|---|---|---|
| `CLAUDE.md` | Active | ❌ | Mentions "reusable platform primitives" | ❌ None |
| `.github/copilot-instructions.md` | Active | ✅ Named | `WorkflowPrimitive`, `tta-workflow-primitives` | ❌ None |
| `.augment/instructions.md` | Active | ✅ With workflow diagram | `WorkflowPrimitive`, circuit breaker, retry | ❌ None |
| `.cline/instructions.md` | Active | ✅ "multi-agent pipeline" | `WorkflowPrimitive`, `tta-dev-primitives` | ❌ None |
| `AGENTS.md` | **Stale redirect** | ❌ | ❌ | Redirects to external Logseq KB |
| `GEMINI.md` | **Stale redirect** | ❌ | ❌ | Redirects to external Logseq KB |

**Key Issue:** All four active instruction files mention the agents and TTA.dev primitives but none reference a canonical specification document. If an agent generates code for the IPA, it has no formal contract to validate against.

### 3.4 Proposed `specs/` Directory Structure

```
specs/
├── README.md                              # Spec index and conventions
├── templates/
│   ├── api.spec.template.md
│   ├── component.spec.template.md
│   └── feature.spec.template.md
│
├── agents/                                # Core agent specifications
│   ├── ipa-input-processing-agent.md      # IPA behavioral contract
│   ├── wba-world-building-agent.md        # WBA behavioral contract
│   ├── nga-narrative-generator-agent.md   # NGA behavioral contract
│   └── agent-orchestration-protocol.md    # Inter-agent messaging contract
│
├── therapeutic-safety/                    # Therapeutic domain specs
│   ├── crisis-detection.md               # Crisis levels, types, interventions
│   ├── emotional-safety-system.md        # Safety levels, content flags, protocols
│   ├── therapeutic-integration.md         # Therapeutic goal tracking & narrative integration
│   └── safety-interop.md                 # How crisis detection & emotional safety interoperate
│
├── persistence/                           # Data layer specifications
│   ├── redis-session-cache.md            # Redis key patterns, TTLs, failover
│   ├── neo4j-story-graph.md             # Node/relationship schemas, queries
│   └── data-retention-policy.md          # HIPAA-compliant retention rules
│
├── tta-dev-integration/                   # TTA ↔ TTA.dev boundary contracts
│   ├── primitive-mapping.md              # Which TTA.dev primitives each TTA component uses
│   ├── circuit-breaker-usage.md          # How TTA agents use the circuit breaker primitive
│   └── observability-boundary.md         # TTA vs TTA.dev observability responsibilities
│
├── infrastructure/                        # Existing infra specs (reorganized)
│   ├── orchestration.md                  # (moved from specs/orchestration.md)
│   └── observability-integration.md      # (moved from specs/observability-integration.md)
│
└── examples/                              # Example/test specs (reorganized)
    ├── calculator-operations.md           # (moved from specs/calculator_operations.md)
    └── example-component.md               # (moved from specs/example_component.md)
```

### 3.5 Proposed `docs/` Therapeutic Documentation Consolidation

The following documents should be cross-referenced from a single therapeutic safety index:

```
docs/
├── clinical/
│   ├── README.md                          # Index: links to all clinical docs + canonical specs
│   ├── THERAPEUTIC_CONTENT_OVERVIEW.md    # (existing)
│   ├── CLINICAL_CONSULTATION_FRAMEWORK.md # (existing)
│   └── EVIDENCE_BASED_FRAMEWORKS.md       # (existing)
└── design/
    ├── therapeutic-integration.md          # (existing, should reference specs/)
    └── clinical-consultation-framework.md  # (existing, should reference specs/)
```

All agent instruction files should include a pointer:

```
## Therapeutic Safety
Canonical specification: `specs/therapeutic-safety/`
```

---

## 4. Gap Analysis & Logseq TODO Blocks

The following gaps were identified. Each is formatted as a Logseq-compliant `#dev-todo` block with required `type::`, `priority::`, and `package::` properties.

### GAP-01: Missing IPA Specification

```markdown
- TODO Write formal behavioral specification for the Input Processing Agent (IPA) #dev-todo
  type:: spec
  priority:: critical
  package:: tta-ai-framework
  description:: The IPA (AgentType.IPA = "input_processor") lacks a formal spec defining its inputs (raw player text), outputs (structured intent + safety assessment), success criteria, failure modes, and TTA.dev primitive dependencies (Router, OpenTelemetry tracing). Currently defined only in code at `src/agent_orchestration/agents.py`. Use `specs/templates/component.spec.template.md` as the base template. Target file: `specs/agents/ipa-input-processing-agent.md`.
```

### GAP-02: Missing WBA Specification

```markdown
- TODO Write formal behavioral specification for the World Building Agent (WBA) #dev-todo
  type:: spec
  priority:: critical
  package:: tta-ai-framework
  description:: The WBA (AgentType.WBA = "world_builder") lacks a formal spec defining its inputs (narrative context, player state), outputs (updated world state), Neo4j persistence contract, Redis caching strategy, and TTA.dev primitive usage. Currently defined only in code at `src/agent_orchestration/agents.py`. Target file: `specs/agents/wba-world-building-agent.md`.
```

### GAP-03: Missing NGA Specification

```markdown
- TODO Write formal behavioral specification for the Narrative Generator Agent (NGA) #dev-todo
  type:: spec
  priority:: critical
  package:: tta-narrative-engine
  description:: The NGA (AgentType.NGA = "narrative_generator") lacks a formal spec defining its inputs (world state, therapeutic goals, player history), outputs (narrative text), LLM integration via OpenRouter, graceful degradation via TTA.dev Circuit Breaker, and streaming behavior via SSE. Currently defined only in code at `src/agent_orchestration/agents.py`. Target file: `specs/agents/nga-narrative-generator-agent.md`.
```

### GAP-04: Missing Agent Orchestration Protocol Specification

```markdown
- TODO Write inter-agent orchestration protocol specification #dev-todo
  type:: spec
  priority:: critical
  package:: tta-ai-framework
  description:: No spec defines the IPA → WBA → NGA coordination contract: message schemas, sequencing, timeouts, error propagation, and retry behavior. The `specs/orchestration.md` covers Docker/infrastructure orchestration, not agent orchestration. Target file: `specs/agents/agent-orchestration-protocol.md`.
```

### GAP-05: Missing Crisis Detection Specification

```markdown
- TODO Write formal specification for the Crisis Detection subsystem #dev-todo
  type:: spec
  priority:: critical
  package:: tta-ai-framework
  description:: Crisis detection (4-level: LOW→MODERATE→HIGH→CRITICAL) is implemented in `src/agent_orchestration/crisis_detection/` but has no formal spec. Must document: severity thresholds, crisis type detection logic, intervention decision tree, escalation state machine, human notification requirements, and HIPAA-compliant audit logging. Target file: `specs/therapeutic-safety/crisis-detection.md`.
```

### GAP-06: Missing Emotional Safety System Specification

```markdown
- TODO Write formal specification for the Emotional Safety System #dev-todo
  type:: spec
  priority:: critical
  package:: tta-narrative-engine
  description:: Emotional safety (5-level: SAFE→CAUTION→WARNING→UNSAFE→CRISIS) is implemented in `src/components/gameplay_loop/narrative/emotional_safety_system.py` but has no formal spec. Must document: content flag definitions, severity calculation algorithm, crisis protocol actions per level, and intervention scene generation rules. Target file: `specs/therapeutic-safety/emotional-safety-system.md`.
```

### GAP-07: Crisis Detection / Emotional Safety Interop Gap

```markdown
- TODO Specify the interoperability contract between Crisis Detection and Emotional Safety #dev-todo
  type:: spec
  priority:: high
  package:: tta-ai-framework
  description:: Crisis Detection uses 4 levels (LOW→CRITICAL) while Emotional Safety uses 5 levels (SAFE→CRISIS). These systems are in different packages (`agent_orchestration` vs `components/gameplay_loop/narrative`) with no specification defining how they map to each other, which takes precedence, or how they coordinate during a crisis event. Target file: `specs/therapeutic-safety/safety-interop.md`.
```

### GAP-08: Missing Redis Persistence Specification

```markdown
- TODO Write formal specification for Redis session cache and messaging #dev-todo
  type:: spec
  priority:: high
  package:: tta-ai-framework
  description:: Redis is used for session caching, inter-agent messaging (RedisMessageCoordinator), and circuit breaker state persistence, but no spec defines key naming patterns, TTLs, serialization formats, failover behavior, or capacity planning. Target file: `specs/persistence/redis-session-cache.md`.
```

### GAP-09: Missing Neo4j Story Graph Specification

```markdown
- TODO Write formal specification for Neo4j story graph persistence #dev-todo
  type:: spec
  priority:: high
  package:: tta-narrative-engine
  description:: Neo4j is used for player state, narrative history, and world relationships, but no spec defines node labels, relationship types, property schemas, index requirements, query patterns, or transaction boundaries. Target file: `specs/persistence/neo4j-story-graph.md`.
```

### GAP-10: Missing TTA.dev Primitive Mapping Document

```markdown
- TODO Create TTA.dev primitive mapping specification #dev-todo
  type:: spec
  priority:: high
  package:: tta-ai-framework
  description:: ARCHITECTURE.md defines the TTA ↔ TTA.dev boundary conceptually, but no spec maps each TTA component to its TTA.dev primitive dependencies. Must document: which primitives each agent uses (circuit breaker, retry, timeout, cache, router), extraction status (implemented in TTA vs delegated to TTA.dev), and migration plan. Target file: `specs/tta-dev-integration/primitive-mapping.md`.
```

### GAP-11: Circuit Breaker Boundary Ambiguity

```markdown
- TODO Resolve circuit breaker ownership between TTA and TTA.dev #dev-todo
  type:: architecture-decision
  priority:: high
  package:: tta-ai-framework
  description:: Circuit breaker is listed as a TTA.dev universal primitive in ARCHITECTURE.md, but is fully implemented in TTA at `src/agent_orchestration/circuit_breaker.py` with Redis persistence. Need an ADR: (a) extract to TTA.dev and import, (b) keep in TTA and update ARCHITECTURE.md, or (c) maintain both with a defined interface contract. Target file: `docs/decisions/ADR-002-circuit-breaker-ownership.md`.
```

### GAP-12: Observability Spec Boundary Separation

```markdown
- TODO Separate TTA.dev vs TTA concerns in observability-integration spec #dev-todo
  type:: spec-update
  priority:: medium
  package:: tta-ai-framework
  description:: `specs/observability-integration.md` conflates universal concerns (OpenTelemetry tracing, Prometheus metrics) with game-specific concerns (LLM cost tracking, narrative dashboards). Split into a TTA.dev observability boundary section and a TTA-specific instrumentation section. Target file: `specs/tta-dev-integration/observability-boundary.md`.
```

### GAP-13: Stale AGENTS.md and GEMINI.md Redirects

```markdown
- TODO Update or remove stale AGENTS.md and GEMINI.md redirect stubs #dev-todo
  type:: documentation
  priority:: medium
  package:: tta-ai-framework
  description:: Both `AGENTS.md` and `GEMINI.md` redirect to an external Logseq KB at `~/repos/TTA-notes/logseq/pages/TTA/` which is not in this repository. Either inline the relevant content or replace with a clear note that the canonical source is in the separate TTA-notes repo, and add a summary of key agent roles for developer orientation.
```

### GAP-14: Agent Instructions Missing Canonical Spec Pointer

```markdown
- TODO Add canonical spec references to all agent instruction files #dev-todo
  type:: documentation
  priority:: high
  package:: tta-ai-framework
  description:: All four active agent instruction files (CLAUDE.md, .github/copilot-instructions.md, .augment/instructions.md, .cline/instructions.md) mention IPA/WBA/NGA and TTA.dev primitives but none reference a canonical specification document. Once the agent specs (GAP-01 through GAP-04) are created, add a "Canonical Specifications" section to each instruction file pointing to `specs/agents/` and `specs/therapeutic-safety/`.
```

### GAP-15: Crisis Detection Code Duplication Between src/ and packages/

```markdown
- TODO Resolve crisis detection code duplication between src/ and packages/ #dev-todo
  type:: refactor
  priority:: high
  package:: tta-ai-framework
  description:: Crisis detection code exists in both `src/agent_orchestration/crisis_detection/` and `packages/tta-ai-framework/src/tta_ai/orchestration/crisis_detection/`. No spec governs which is canonical, how they stay in sync, or whether one should import from the other. Resolve by designating one location as canonical and having the other re-export.
```

### GAP-16: Data Retention Policy for HIPAA Compliance

```markdown
- TODO Write data retention policy specification for HIPAA compliance #dev-todo
  type:: spec
  priority:: high
  package:: tta-narrative-engine
  description:: The therapeutic safety systems handle sensitive data (crisis assessments, intervention records, emotional state tracking) but no specification defines data retention periods, deletion procedures, encryption requirements, or audit trail retention. Required for HIPAA compliance. Target file: `specs/persistence/data-retention-policy.md`.
```

### GAP-17: Spec Directory Reorganization

```markdown
- TODO Reorganize specs/ directory with proposed hierarchy #dev-todo
  type:: chore
  priority:: medium
  package:: tta-ai-framework
  description:: The current `specs/` directory has 4 flat files and a templates/ directory. Reorganize into the proposed hierarchy: `agents/`, `therapeutic-safety/`, `persistence/`, `tta-dev-integration/`, `infrastructure/`, `examples/`. Move existing files to their appropriate subdirectories and create a `specs/README.md` index.
```

### GAP-18: Missing Therapeutic Safety Spec Index in docs/clinical/

```markdown
- TODO Create therapeutic safety documentation index in docs/clinical/ #dev-todo
  type:: documentation
  priority:: medium
  package:: tta-narrative-engine
  description:: Therapeutic documentation is scattered across `docs/clinical/`, `docs/design/`, and source code docstrings. Create a `docs/clinical/README.md` index that links to all clinical documents and points to the canonical specifications in `specs/therapeutic-safety/` once they are created.
```

---

## 5. Summary of Recommended Actions

### Immediate (Critical Priority)

1. **Create agent specs** (GAP-01, GAP-02, GAP-03, GAP-04) — These are the foundation. No agent instruction file can validate generated code without them.
2. **Create therapeutic safety specs** (GAP-05, GAP-06, GAP-07) — Crisis detection and emotional safety are safety-critical systems that must have formal contracts.

### Short-Term (High Priority)

3. **Create persistence specs** (GAP-08, GAP-09, GAP-16) — Data schemas and retention policies are prerequisites for HIPAA compliance.
4. **Create TTA.dev integration specs** (GAP-10, GAP-11, GAP-12) — Formalize the boundary between TTA and TTA.dev.
5. **Resolve code duplication** (GAP-15) — Crisis detection exists in two locations.
6. **Update agent instructions** (GAP-14) — Point all instruction files to canonical specs.

### Medium-Term (Medium Priority)

7. **Reorganize specs/ directory** (GAP-17) — Apply the proposed hierarchy.
8. **Update stale redirects** (GAP-13) — Fix AGENTS.md and GEMINI.md.
9. **Create documentation indices** (GAP-18) — Consolidate therapeutic docs.

---

## Appendix A: Files Audited

### Root-Level Documents
- `ARCHITECTURE.md` — Two-layer toolkit architecture (well-maintained)
- `AGENTS.md` — Stale redirect to Logseq KB
- `CLAUDE.md` — Primary agent instructions (active)
- `GEMINI.md` — Stale redirect to Logseq KB
- `CONTRIBUTING.md` — Contributor guidelines (active)
- `SECURITY.md` — Security policy

### Agent Instruction Files
- `.github/copilot-instructions.md`
- `.augment/instructions.md`
- `.cline/instructions.md`
- `CLAUDE.md`

### Specifications
- `specs/orchestration.md`
- `specs/observability-integration.md`
- `specs/calculator_operations.md`
- `specs/example_component.md`
- `specs/templates/component.spec.template.md`
- `specs/templates/api.spec.template.md`
- `specs/templates/feature.spec.template.md`

### Documentation
- `docs/architecture/README.md`
- `docs/technical-specifications.md`
- `docs/traceability-matrix.md`
- `docs/gap-analysis.md`
- `docs/clinical/THERAPEUTIC_CONTENT_OVERVIEW.md`
- `docs/clinical/CLINICAL_CONSULTATION_FRAMEWORK.md`
- `docs/clinical/EVIDENCE_BASED_FRAMEWORKS.md`
- `docs/design/therapeutic-integration.md`
- `docs/design/clinical-consultation-framework.md`
- `docs/TTA_DEV_MIGRATION_STRATEGY.md`

### Source Code (Structural Audit)
- `src/agent_orchestration/agents.py`
- `src/agent_orchestration/models.py`
- `src/agent_orchestration/circuit_breaker.py`
- `src/agent_orchestration/crisis_detection/enums.py`
- `src/agent_orchestration/crisis_detection/models.py`
- `src/agent_orchestration/crisis_detection/manager.py`
- `src/agent_orchestration/crisis_detection/escalation.py`
- `src/components/gameplay_loop/narrative/emotional_safety_system.py`
- `packages/tta-ai-framework/src/tta_ai/orchestration/crisis_detection/`

## Appendix B: Crisis Level Mapping Reference

For the future `specs/therapeutic-safety/safety-interop.md`, the following mapping should be considered:

| Emotional Safety Level | Suggested Crisis Detection Mapping | Action |
|---|---|---|
| `SAFE` | (No crisis assessment triggered) | Normal gameplay |
| `CAUTION` | `CrisisLevel.LOW` | Log and monitor |
| `WARNING` | `CrisisLevel.MODERATE` | Reduce intensity, offer break |
| `UNSAFE` | `CrisisLevel.HIGH` | Halt content, grounding, provide exit |
| `CRISIS` | `CrisisLevel.CRITICAL` | Immediate intervention, emergency resources |

---

**Logseq:** [[TTA/Reports/TTA Spec Audit Report]]
