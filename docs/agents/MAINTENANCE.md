# Agent Instruction System — Maintenance Guide

## Architecture

This directory is the single source of truth for all developer-facing agent
instructions in TTA. Root files (CLAUDE.md, AGENTS.md, etc.) are **routing
layers** with a 100-line hard budget. Knowledge lives here, not in root files.

### Directory structure

| Directory | Purpose | Loading |
|---|---|---|
| `_core/` | Always-needed cross-cutting guidance | Auto-imported via CLAUDE.md `@`-imports |
| `dev/` | Domain-specific developer guidance | On demand — agent reads when working on topic |
| `runtime/` | Reference docs for Tier 3 runtime agents | On demand — read when modifying IPA/NGA/prompts |

### Four-tier agent taxonomy

| Tier | Who | Instructions |
|---|---|---|
| 1 — Developer agents | Claude Code, Copilot, Gemini, Cline, Augment | Root files + this tree |
| 2 — Domain expert personas | Chatmodes in `.github/chatmodes/` | Chatmode files (not in this tree) |
| 3 — Runtime product agents | IPA, NGA (in `src/components/`) | `runtime/` reference docs |
| 4 — Runtime dev agents | TTA.dev L0 agents | TTA.dev `docs/agents/` (separate repo) |

---

## How to extend the system

### Adding developer-facing guidance
1. Create or extend a file in `docs/agents/dev/`
2. Add ONE row to each root file's routing table:
   `| Working on <topic> | docs/agents/dev/<topic>.md |`
3. Run `make check-agent-docs` — root files must stay under 100 lines

### Adding always-needed guidance (loads every Claude Code session)
1. Create a file in `docs/agents/_core/`
2. Add `@docs/agents/_core/<file>.md` to `CLAUDE.md`
3. Add a note in other agents' root files: "See docs/agents/_core/<file>.md"

### Adding runtime agent reference docs
1. Create a file in `docs/agents/runtime/`
2. Add a routing entry: `| Editing IPA/NGA prompts | docs/agents/runtime/<agent>.md |`

---

## Maintenance header (paste into every root file you edit)

**TTA variant** (has `_core/`):
```
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

---

## Cross-repo sync obligations

Any **structural or protocol change** (not typo/formatting) to these files requires
opening a tracking issue in TTA.dev. Typos and formatting fixes do not require issues.

| This file | TTA.dev counterpart |
|---|---|
| `docs/agents/dev/l0-boundary.md` | `docs/agents/dev/l0-coordination.md` |
| `AGENTS.md` (roster section) | `AGENTS.md` (roster section) |
| `docs/agents/_core/tools.md` | `CLAUDE.md` — `## Session Protocol` section |

---

## Budget enforcement

`make check-agent-docs` checks these root files against the 100-line budget:
`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`,
`.cline/instructions.md`, `.augment/instructions.md`

Script: `scripts/check_agent_docs.py`
