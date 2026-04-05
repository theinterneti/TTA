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
