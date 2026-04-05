# Agent Instruction Architecture — Design Spec
**Date:** 2026-04-04  
**Repos:** TTA + TTA.dev  
**Status:** Approved

---

## Problem

Agent instruction files across TTA and TTA.dev have grown well beyond the ~100-line budget that keeps them readable and maintainable. Root files are being used as knowledge stores rather than routing layers, causing:

- Agents loading irrelevant content every session (context waste)
- No separation between instructions for different agent tiers
- Inevitable drift as agents and humans append to root files
- No canonical home for runtime agent instructions (embedded in Python)

**Current overages (files over 100-line budget):**

| File | Lines | Note |
|---|---|---|
| TTA `.github/copilot-instructions.md` | 237 | |
| TTA `.augment/instructions.md` | 225 | |
| TTA `.cline/instructions.md` | 160 | |
| TTA `CLAUDE.md` | 147 | |
| TTA.dev `AGENTS.md` | 351 | |
| TTA.dev `.github/copilot-instructions.md` | 148 | |
| TTA.dev `CLAUDE.md` | 130 | |
| TTA `AGENTS.md` | 80 | Under budget but rewritten to add routing pointer |

---

## Goals

1. Every root instruction file under 100 lines
2. Agents load only what is relevant to their current task
3. Clear separation between the four agent tiers (see below)
4. Mechanical drift prevention — impossible to accidentally bloat root files
5. Cross-repo sync obligations made explicit
6. Runtime agent instructions have a real home (not buried in Python)

---

## Four-Tier Agent Taxonomy

Both repos contain agents operating at four distinct tiers. Instructions must serve each tier without bleeding into the others.

| Tier | TTA | TTA.dev |
|---|---|---|
| **1 — Developer agents** | Claude Code, Copilot, Gemini building TTA | Claude Code, Copilot, Gemini building TTA.dev |
| **2 — Domain expert personas** | Chatmodes: narrative-engine-dev, safety-architect, therapeutic-auditor… | Chatmodes: observability-expert, data-scientist, testing-specialist… |
| **3 — Runtime product agents** | IPA, WBA, NGA serving players | — |
| **4 — Runtime dev agents** | — | L0 agents: DeveloperAgent, DevOpsAgent, SecurityAgent, GitAgent, GitHubAgent, QAAgent, PerformanceAgent |

Tiers 1–2 need developer-facing instructions (how to build the system).  
Tiers 3–4 need runtime-facing instructions (how to operate the system).  
These are separate namespaces. Developer agents need to know the runtime tier exists and where its instructions live — but must not confuse the two.

---

## Chosen Approach: Canonical `docs/agents/` Tree (Approach A)

Each repo gets a single `docs/agents/` tree with clear sub-namespaces per tier. Root files become thin routing layers.

**Loading model — two mechanisms:**
- **Claude Code** supports `@path/to/file.md` in CLAUDE.md for automatic inclusion at session start. This is used for always-relevant content (`_core/` in TTA, observability/reliability in TTA.dev).
- **All other agents** (Copilot, Cline, Augment, Gemini) cannot `@`-import. Their root files include an explicit routing table and are instructed to *read the relevant sub-file* before starting work on a given topic. The routing table row format makes the action unambiguous: "when working on X, read `docs/agents/dev/X.md` before proceeding."

**TTA has a `_core/` tier** (auto-imported via CLAUDE.md `@`-imports) because cross-cutting concerns (tool protocols, quality gate) are relevant in every session regardless of task.

**TTA.dev omits `_core/`** because its session protocol already handles tool loading. Two `dev/` files (observability, reliability) are auto-imported instead — they serve double duty as both always-loaded content and on-demand domain references. Future always-needed content for TTA.dev belongs in `dev/` with a CLAUDE.md `@`-import line, not in a separate `_core/` directory.

---

## Directory Structure

### TTA

```
docs/agents/
  MAINTENANCE.md              ← system guide + cross-repo sync obligations
  _core/                      ← auto-imported by CLAUDE.md (@-imports); always in context
    tools.md                  # Serena, CGC, Hindsight — protocols + trigger conditions
    quality.md                # ruff, pyright, pytest — commands + rules
  dev/                        ← Tier 1 & 2: loaded on demand via routing table
    architecture.md           # IPA/WBA/NGA pipeline, Redis, Neo4j, circuit breakers
    testing.md                # pytest, AAA, markers, coverage, async patterns
    safety.md                 # crisis detection (4-level), emotional safety (5-level)
    genesis.md                # onboarding narrative system, seed/guide generation
    l0-boundary.md            # TTA.dev integration rules, what NOT to build in TTA
  runtime/                    ← Tier 3: reference for developers touching runtime agents
    ipa.md                    # IPA design, prompt location (ipa/agent.py:59), how to extend
    nga.md                    # NGA design, prompt location, voice profiles, guide injection
    prompt-registry.md        # versioned YAML format, how to add/promote prompt versions
```

**Note on WBA:** WBA has no LLM and makes no model calls — it is a pure Neo4j context-assembly layer. It has no system prompt and no runtime instructions. WBA coverage is part of `dev/architecture.md` (pipeline and data flow), not a separate `runtime/wba.md`.

### TTA.dev

```
docs/agents/
  MAINTENANCE.md              ← system guide + cross-repo sync obligations
  dev/                        ← Tier 1 & 2: loaded on demand (observability + reliability also auto-imported)
    architecture.md           # primitives system, AgentSpec, AgentPrimitive, L0 overview
    testing.md                # TDD, primitives testing, AAA, asyncio patterns
    observability.md          # (promoted from docs/guides/agents/universal/patterns/)
    reliability.md            # (promoted from docs/guides/agents/universal/patterns/)
    l0-coordination.md        # task lease/claim/run/report/release protocol, .tta/ state
  runtime/                    ← Tier 4: reference for developers touching L0 agents
    l0-roster.md              # 7 agents: role, capabilities, handoff triggers, quality gates
    l0-agent-spec.md          # how to write/modify AgentSpec, tools field, policy gates
    task-protocol.md          # full lease lifecycle, MCP tool interface, approval gates
```

**What does not move:**
- Chatmodes stay in `.github/chatmodes/` (TTA) and `.tta/chatmodes/` (TTA.dev)
- Runtime system prompts stay in Python source (`ipa/agent.py`, `nga/agent.py`, `ttadev/agents/*.py`)
- Prompt YAML versions stay in `src/ai_components/prompts/versions/`
- The `runtime/` docs are reference files for developers — not replacements for embedded prompts

---

## Root File Architecture

### Budget: 100 lines hard limit on every root file

Every root file opens with a maintenance protocol comment (see Drift Prevention).

### TTA root files (post-restructure)

**`CLAUDE.md`** (~75 lines)
- Project identity (pipeline diagram, 3 lines)
- `@docs/agents/_core/tools.md` — auto-loads Serena/CGC/Hindsight
- `@docs/agents/_core/quality.md` — auto-loads ruff/pyright/pytest
- Session protocol (Hindsight recall adam-global → tta)
- Non-negotiables table (uv, pyright, 88 chars, test framework, commit style)
- Routing table (6 rows mapping topic → sub-file)
- Agent roster (pointer table to each tool's config)
- L0 directive (3-line summary + pointer to l0-boundary.md)

**`.github/copilot-instructions.md`** (~80 lines, from 237)
- Same identity + non-negotiables
- Session protocol (Hindsight + Serena + CGC — explicit since Copilot cannot @-import)
- Routing table with explicit read instruction per row: "when working on X, read docs/agents/dev/X.md before proceeding"
- One-line MCP server list + pointer to docs/agents/_core/tools.md

**`AGENTS.md`** (~70 lines, from 80 — rewritten to add routing pointer)
- Project identity + architecture diagram
- Agent roster table
- Pointer: "For domain context, see docs/agents/dev/"

**`GEMINI.md`** (~70 lines, from 98)
- Project identity, quality gate commands, routing table, Hindsight protocol

**`.cline/instructions.md`** (~70 lines, from 160)  
**`.augment/instructions.md`** (~70 lines, from 225)  
Both: identity + non-negotiables + session protocol + routing table with explicit read instructions.

### TTA.dev root files (post-restructure)

**`CLAUDE.md`** (~80 lines, from 130)
- Project identity
- `@docs/agents/dev/observability.md` — auto-loads (always relevant)
- `@docs/agents/dev/reliability.md` — auto-loads (always relevant)
- Session protocol (Hindsight + Serena check_onboarding + CGC)
- Non-negotiables (uv, Python 3.11+, Conventional Commits)
- Routing table (5 rows)
- Common commands

**`AGENTS.md`** (~75 lines, from 351)
- Project identity + L0 architecture overview
- Agent roster table
- Pointer: "For full domain context see docs/agents/"

**`.github/copilot-instructions.md`** (~75 lines, from 148)
- Same routing-first pattern as TTA copilot file

---

## Drift Prevention

Three interlocking mechanisms prevent future bloat:

### 1. Self-describing maintenance header (every root file)

**TTA variant** (has `_core/`):
```markdown
<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit.
  DO NOT add content directly here.
  Instead:
    1. Create or extend a file in docs/agents/dev/ (or _core/ if always-needed every session)
    2. Add ONE routing row to the table below (or a CLAUDE.md @-import for _core/ files)
    3. Run: make check-agent-docs
  This file is a routing layer, not a knowledge store.
-->
```

**TTA.dev variant** (no `_core/` — always-needed content goes in `dev/` + a CLAUDE.md `@`-import line):
```markdown
<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit.
  DO NOT add content directly here.
  Instead:
    1. Create or extend a file in docs/agents/dev/
    2. Add ONE routing row to the table below
       (if the content is always-needed: also add a @docs/agents/dev/<file>.md line to CLAUDE.md)
    3. Run: make check-agent-docs
  This file is a routing layer, not a knowledge store.
-->
```

### 2. `make check-agent-docs` — mechanical line-count guard

A Makefile target backed by `scripts/check_agent_docs.py` (~20 lines). The script checks a hardcoded list of root files (defined at the top of the script) against the 100-line budget. Exits non-zero with a clear per-file message on violation. Can be run manually, added to `make test`, or wired into pre-commit.

**TTA root file list** (hardcoded in TTA's script): `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cline/instructions.md`, `.augment/instructions.md`

**TTA.dev root file list** (hardcoded in TTA.dev's script): `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`

### 3. Routing table as natural redirect

The routing table structure makes "add a row, not a paragraph" the obvious maintenance action. Agents and humans encountering the table understand the pattern immediately.

---

## Cross-Repo Sync

Most content is intentionally different between repos. Three areas create genuine sync obligations:

| TTA file | TTA.dev counterpart | Nature |
|---|---|---|
| `dev/l0-boundary.md` | `dev/l0-coordination.md` | Two sides of the same L0 contract |
| `AGENTS.md` (roster section) | `AGENTS.md` (roster section) | Same developer agents work both repos |
| `_core/tools.md` | `CLAUDE.md` — the `## Session Protocol` section | Same Serena/CGC/Hindsight tools and trigger conditions |

### Sync mechanism

`docs/agents/MAINTENANCE.md` in each repo explicitly names cross-repo counterparts and defines the sync trigger threshold: **any structural or protocol change** to a sync-obligated file requires opening a tracking issue on the other repo. Typo and formatting fixes do not. The MAINTENANCE.md file is the authoritative source for this threshold.

When TTA is implemented first, paired issues on TTA.dev are **forward-tracking notices** — they document the obligation for when TTA.dev's `docs/agents/` tree is subsequently built, not requests for immediate action.

Symlinks and git submodules are explicitly ruled out — they create more coupling problems than they solve at this stage.

---

## Implementation Sequence

TTA and TTA.dev are treated as independent systems. TTA is implemented first (more files, more complex), TTA.dev second via GitHub issues.

Within each repo:
1. Write `docs/agents/MAINTENANCE.md` first — root files reference it, so it must exist
2. Create remaining `docs/agents/` sub-files (extract content from existing root files)
3. Add `scripts/check_agent_docs.py` + `make check-agent-docs` target
4. Rewrite root files to routing layer pattern (maintenance header + routing table)
5. Open paired tracking issues on TTA.dev for the three cross-repo sync files (forward-tracking — TTA.dev work happens in a later session)
6. Run `make check-agent-docs` and verify quality gate passes

---

## Files Changed Summary

### TTA

**11 new docs/agent files:**
`docs/agents/MAINTENANCE.md`, `docs/agents/_core/tools.md`, `docs/agents/_core/quality.md`, `docs/agents/dev/architecture.md`, `docs/agents/dev/testing.md`, `docs/agents/dev/safety.md`, `docs/agents/dev/genesis.md`, `docs/agents/dev/l0-boundary.md`, `docs/agents/runtime/ipa.md`, `docs/agents/runtime/nga.md`, `docs/agents/runtime/prompt-registry.md`

**1 new script:**
`scripts/check_agent_docs.py`

**6 root files rewritten:**
`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cline/instructions.md`, `.augment/instructions.md`

### TTA.dev (via GitHub issues, implemented in a later session)

**9 new docs/agent files:**
`docs/agents/MAINTENANCE.md`, `docs/agents/dev/architecture.md`, `docs/agents/dev/testing.md`, `docs/agents/dev/l0-coordination.md`, `docs/agents/runtime/l0-roster.md`, `docs/agents/runtime/l0-agent-spec.md`, `docs/agents/runtime/task-protocol.md`

**2 promoted + renamed files** (source files in `docs/guides/agents/universal/patterns/` are deleted after promotion):
- `docs/guides/agents/universal/patterns/observability.instructions.md` → `docs/agents/dev/observability.md`
- `docs/guides/agents/universal/patterns/reliability.instructions.md` → `docs/agents/dev/reliability.md`

**1 new script:**
`scripts/check_agent_docs.py`

**3 root files rewritten:**
`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`
