<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# TTA — Gemini Agent Instructions

Gemini is a **secondary reviewer**. Primary decisions belong to Claude Code.

## Project

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.
Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

**Architecture:** Redis (session cache) + Neo4j (story graph) + FastAPI SSE
**Safety:** Crisis Detection (4-level) + Emotional Safety (5-level)

## Session protocol

1. `mcp__hindsight__recall` → `adam-global` — cross-project directives
2. `mcp__hindsight__recall` → `tta` — TTA-specific context
After significant tasks: retain to the appropriate bank.
Hindsight MCP: `http://localhost:8888/mcp/`

## Quality gate

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Standards

| Rule | Value |
|---|---|
| Package manager | `uv` only — never `pip install` |
| Python | 3.12+, `str \| None` not `Optional[str]` |
| Line length | 88 (Ruff) |
| Type checker | Pyright `standard` mode |
| Tests | pytest AAA pattern, `asyncio_mode = "auto"` |
| Commits | Conventional Commits |

## Domain guidance

| Topic | File |
|---|---|
| Architecture, pipeline | `docs/agents/dev/architecture.md` |
| Testing patterns | `docs/agents/dev/testing.md` |
| Safety systems | `docs/agents/dev/safety.md` |
| Genesis / onboarding | `docs/agents/dev/genesis.md` |
| L0 / TTA.dev boundary | `docs/agents/dev/l0-boundary.md` |
| IPA or NGA system prompts | `docs/agents/runtime/ipa.md` or `nga.md` |

## Agent roster

| Agent | Role | Config |
|---|---|---|
| **Claude Code** | Primary | `CLAUDE.md` |
| **Gemini** | Secondary reviewer | `GEMINI.md` (this file) |
| GitHub Copilot | IDE suggestions | `.github/copilot-instructions.md` |
| Augment | Code intelligence | `.augment/instructions.md` |
| Cline | AI coding assistant | `.cline/instructions.md` |

## L0 / TTA.dev boundary

`TTA.dev` owns the L0 developer control plane. Do not build a second one here.
Full rules: `docs/agents/dev/l0-boundary.md`
