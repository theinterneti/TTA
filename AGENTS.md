<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# AGENTS.md — Universal Agent Context

Shared entry point for all AI agents in the TTA repository. Read this before acting.

## What this repo is

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.
Players make choices that branch the story; a therapist/editorial layer curates safe paths.

Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

**TTA.dev** provides reusable platform primitives. It owns the L0 developer control plane.

## Agent roster

| Agent | Role | Config |
|---|---|---|
| **Claude Code** | Primary — main decision maker | `CLAUDE.md` |
| GitHub Copilot | AI coding assistant | `.github/copilot-instructions.md` |
| Augment | Code intelligence | `.augment/instructions.md` |
| Cline | AI coding assistant | `.cline/instructions.md` |
| Gemini | Secondary reviewer | `GEMINI.md` |

## Non-negotiables

- Python 3.12+ | `uv` only (never `pip`) | 88-char lines | Pyright `standard`
- Conventional Commits | AAA tests | 100% coverage for new code

## Quality gate (run before committing)

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test

# Running with 1Password secret injection (first copy .env.template to .env):
op run --env-file=.env -- python src/main.py start
```

## Domain guidance

For detailed context on any topic, read the relevant file before starting:

| Topic | File |
|---|---|
| Architecture, pipeline, key classes | `docs/agents/dev/architecture.md` |
| Testing patterns, markers, coverage | `docs/agents/dev/testing.md` |
| Safety systems | `docs/agents/dev/safety.md` |
| Genesis / onboarding | `docs/agents/dev/genesis.md` |
| L0 / TTA.dev boundary | `docs/agents/dev/l0-boundary.md` |

## Memory (Hindsight)

Before non-trivial tasks: recall `adam-global` then `tta` from Hindsight.
After significant tasks: retain to the appropriate bank.
MCP: `http://localhost:8888/mcp/`

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **TTA** (59526 symbols, 85464 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

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
| Work in the Components area (366 symbols) | `.claude/skills/generated/components/SKILL.md` |
| Work in the Agent_orchestration area (360 symbols) | `.claude/skills/generated/agent-orchestration/SKILL.md` |
| Work in the Services area (311 symbols) | `.claude/skills/generated/services/SKILL.md` |
| Work in the Gameplay_loop area (280 symbols) | `.claude/skills/generated/gameplay-loop/SKILL.md` |
| Work in the Orchestration area (269 symbols) | `.claude/skills/generated/orchestration/SKILL.md` |
| Work in the Scripts area (265 symbols) | `.claude/skills/generated/scripts/SKILL.md` |
| Work in the Realtime area (244 symbols) | `.claude/skills/generated/realtime/SKILL.md` |
| Work in the Page-objects area (221 symbols) | `.claude/skills/generated/page-objects/SKILL.md` |
| Work in the Routers area (141 symbols) | `.claude/skills/generated/routers/SKILL.md` |
| Work in the Api_gateway area (139 symbols) | `.claude/skills/generated/api-gateway/SKILL.md` |
| Work in the Narrative area (97 symbols) | `.claude/skills/generated/narrative/SKILL.md` |
| Work in the Tools area (86 symbols) | `.claude/skills/generated/tools/SKILL.md` |
| Work in the Openhands_integration area (83 symbols) | `.claude/skills/generated/openhands-integration/SKILL.md` |
| Work in the Genesis area (81 symbols) | `.claude/skills/generated/genesis/SKILL.md` |
| Work in the Player_experience area (81 symbols) | `.claude/skills/generated/player-experience/SKILL.md` |
| Work in the Api area (77 symbols) | `.claude/skills/generated/api/SKILL.md` |
| Work in the Narrative_coherence area (76 symbols) | `.claude/skills/generated/narrative-coherence/SKILL.md` |
| Work in the Extended_evaluation area (75 symbols) | `.claude/skills/generated/extended-evaluation/SKILL.md` |
| Work in the Performance area (74 symbols) | `.claude/skills/generated/performance/SKILL.md` |
| Work in the Database area (71 symbols) | `.claude/skills/generated/database/SKILL.md` |

<!-- gitnexus:end -->
