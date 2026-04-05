<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# TTA — Cline Instructions

## Project

**TTA** is an AI-powered therapeutic text adventure. Players make choices that branch
the narrative; a safety layer curates which paths are therapeutically effective.

Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

## Non-negotiables

| Constraint | Rule |
|---|---|
| Python version | 3.12+ only |
| Package manager | `uv` — never `pip` |
| Type hints | `str \| None` not `Optional[str]` |
| Line length | 88 chars (Ruff) |
| Type checker | Pyright (`standard` mode) |
| Test framework | pytest, `asyncio_mode = "auto"` |
| Commit style | Conventional Commits |

## Quality gate (run before committing)

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Session protocol

Before any non-trivial task:
1. Recall from Hindsight `adam-global` (cross-project directives)
2. Recall from Hindsight `tta` (TTA-specific context)
After significant tasks: retain decisions to the appropriate Hindsight bank.

## Routing — read the relevant file before starting work

| Working on… | Read this file first |
|---|---|
| Architecture, pipeline, agents, data stores | `docs/agents/dev/architecture.md` |
| Tests, coverage, markers, fixtures | `docs/agents/dev/testing.md` |
| Safety systems, crisis detection | `docs/agents/dev/safety.md` |
| Genesis / onboarding narrative system | `docs/agents/dev/genesis.md` |
| L0, TTA.dev boundary | `docs/agents/dev/l0-boundary.md` |
| IPA or NGA system prompts | `docs/agents/runtime/ipa.md` or `nga.md` |
| Tool protocols (Serena, CGC, Hindsight) | `docs/agents/_core/tools.md` |

## Agent roster

| Agent | Config |
|---|---|
| **Claude Code** (primary) | `CLAUDE.md` |
| **Cline** | `.cline/instructions.md` (this file) |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Augment | `.augment/instructions.md` |
| Gemini | `GEMINI.md` |
