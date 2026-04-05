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
