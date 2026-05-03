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

# TTA — Claude Code

Claude Code is the **primary/main agent** for this repository.

## Project

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.
Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`.

@docs/agents/_core/tools.md
@docs/agents/_core/quality.md

## Session Protocol

**Every session begins with memory recall:**
1. `mcp__hindsight__recall` → `adam-global` — cross-project directives and patterns
2. `mcp__hindsight__recall` → `tta` — TTA-specific context, decisions, known issues

**Every significant task ends with a retain:**
- Cross-project patterns → `adam-global`
- TTA-specific decisions and failures → `tta`

## Routing

Read the relevant sub-file **before starting work** on any of these topics:

| Working on… | Read first |
|---|---|
| Architecture, pipeline, agents, data stores | `docs/agents/dev/architecture.md` |
| Tests, coverage, markers, fixtures | `docs/agents/dev/testing.md` |
| Safety systems, crisis detection | `docs/agents/dev/safety.md` |
| Genesis / onboarding narrative system | `docs/agents/dev/genesis.md` |
| L0, TTA.dev boundary, developer control plane | `docs/agents/dev/l0-boundary.md` |
| IPA or NGA system prompts | `docs/agents/runtime/ipa.md` or `nga.md` |
| Prompt versioning | `docs/agents/runtime/prompt-registry.md` |

## Agent roster

| Agent | Config |
|---|---|
| **Claude Code** (primary) | `CLAUDE.md` (this file) |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Augment | `.augment/instructions.md` |
| Cline | `.cline/instructions.md` |
| Gemini | `GEMINI.md` |

## L0 directive

`TTA.dev` owns the L0 developer control plane. Do not build a second one here.
Full rules: `docs/agents/dev/l0-boundary.md`

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **TTA** (77054 symbols, 114439 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/TTA/context` | Codebase overview, check index freshness |
| `gitnexus://repo/TTA/clusters` | All functional areas |
| `gitnexus://repo/TTA/processes` | All execution flows |
| `gitnexus://repo/TTA/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |
| Work in the Agent_orchestration area (302 symbols) | `.claude/skills/generated/agent-orchestration/SKILL.md` |
| Work in the Services area (242 symbols) | `.claude/skills/generated/services/SKILL.md` |
| Work in the Orchestration area (242 symbols) | `.claude/skills/generated/orchestration/SKILL.md` |
| Work in the Scripts area (236 symbols) | `.claude/skills/generated/scripts/SKILL.md` |
| Work in the Page-objects area (231 symbols) | `.claude/skills/generated/page-objects/SKILL.md` |
| Work in the Gameplay_loop area (220 symbols) | `.claude/skills/generated/gameplay-loop/SKILL.md` |
| Work in the Realtime area (196 symbols) | `.claude/skills/generated/realtime/SKILL.md` |
| Work in the Components area (191 symbols) | `.claude/skills/generated/components/SKILL.md` |
| Work in the Api_gateway area (151 symbols) | `.claude/skills/generated/api-gateway/SKILL.md` |
| Work in the Tools area (84 symbols) | `.claude/skills/generated/tools/SKILL.md` |
| Work in the Genesis area (81 symbols) | `.claude/skills/generated/genesis/SKILL.md` |
| Work in the Openhands_integration area (79 symbols) | `.claude/skills/generated/openhands-integration/SKILL.md` |
| Work in the Player_experience area (71 symbols) | `.claude/skills/generated/player-experience/SKILL.md` |
| Work in the Performance area (68 symbols) | `.claude/skills/generated/performance/SKILL.md` |
| Work in the Api area (65 symbols) | `.claude/skills/generated/api/SKILL.md` |
| Work in the Integration area (61 symbols) | `.claude/skills/generated/integration/SKILL.md` |
| Work in the Monitoring area (59 symbols) | `.claude/skills/generated/monitoring/SKILL.md` |
| Work in the Database area (55 symbols) | `.claude/skills/generated/database/SKILL.md` |
| Work in the Extended_evaluation area (54 symbols) | `.claude/skills/generated/extended-evaluation/SKILL.md` |
| Work in the Optimization area (50 symbols) | `.claude/skills/generated/optimization/SKILL.md` |

<!-- gitnexus:end -->
