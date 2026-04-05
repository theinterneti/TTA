<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# TTA — GitHub Copilot Instructions

## Project

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.
Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

## Non-negotiables

- Python 3.12+ | `uv` only (never `pip`) | 88-char lines | Pyright `standard` mode
- Conventional Commits | AAA tests | 100% coverage for new code
- Never push broken commits to `main` — branch and PR instead

## Quality gate (run before committing)

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Session protocol

**Start of session:**
1. Recall from Hindsight `adam-global` (cross-project directives)
2. Recall from Hindsight `tta` (TTA-specific context)
3. Call `check_onboarding_performed` on Serena to confirm it is oriented to this repo

**After significant tasks:** retain decisions and patterns to the appropriate Hindsight bank.

## Routing — read the relevant file before starting work

| Working on… | Read this file first |
|---|---|
| Architecture, pipeline, agents, data stores | `docs/agents/dev/architecture.md` |
| Tests, coverage, markers, fixtures | `docs/agents/dev/testing.md` |
| Safety systems, crisis detection | `docs/agents/dev/safety.md` |
| Genesis / onboarding narrative system | `docs/agents/dev/genesis.md` |
| L0, TTA.dev boundary | `docs/agents/dev/l0-boundary.md` |
| IPA or NGA system prompts | `docs/agents/runtime/ipa.md` or `nga.md` |
| Prompt versioning | `docs/agents/runtime/prompt-registry.md` |
| Tool protocols (Serena, CGC, Hindsight) | `docs/agents/_core/tools.md` |

## MCP servers available

- **Serena** — symbol-aware code navigation (structural questions, refactor scoping)
- **CGC** — code graph analysis (dependency chains, dead code, complexity)
- **Hindsight** — persistent cross-session memory (`http://localhost:8888/mcp/`)
- **Context7** — current library/framework documentation
- Full protocols: `docs/agents/_core/tools.md`

## Agent roster

| Agent | Config |
|---|---|
| **Claude Code** (primary) | `CLAUDE.md` |
| **GitHub Copilot** | `.github/copilot-instructions.md` (this file) |
| Augment | `.augment/instructions.md` |
| Cline | `.cline/instructions.md` |
| Gemini | `GEMINI.md` |
