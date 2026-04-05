<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# TTA — Augment Instructions

## What this repo is

**TTA** is an AI-powered therapeutic text adventure. Players make choices that branch
the narrative; a therapist/editorial safety layer curates which paths are effective.

Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

**TTA.dev** (`~/Repos/TTA.dev`) provides the platform primitives TTA is built on.

## Non-negotiable standards

- Python 3.12+ | `uv` only (never `pip install`) | `str | None` not `Optional[str]`
- 88-char lines | Pyright `standard` mode | Conventional Commits
- pytest with `asyncio_mode = "auto"` | 100% coverage for new code

## Quality gate

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Session protocol

Before non-trivial tasks:
1. Recall from Hindsight `adam-global` (cross-project directives)
2. Recall from Hindsight `tta` (TTA-specific context)
After significant tasks: retain to the appropriate Hindsight bank.

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

## Key source directories

```
src/components/ipa/        # Input Processing Agent
src/components/nga/        # Narrative Generation Agent
src/agent_orchestration/   # Circuit breakers, coordination
src/ai_components/         # LLM clients, prompt registry
src/player_experience/     # Player profiles and sessions
packages/                  # tta-ai-framework, tta-narrative-engine
```

## Agent roster

| Agent | Config |
|---|---|
| **Claude Code** (primary) | `CLAUDE.md` |
| **Augment** | `.augment/instructions.md` (this file) |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cline | `.cline/instructions.md` |
| Gemini | `GEMINI.md` |
