# AGENTS.md — Universal Agent Context

This file is the shared entry point for all AI agents operating in the TTA
repository. Read this before acting.

## What This Repo Is

**Therapeutic Text Adventure (TTA)** — An AI-powered narrative game for mental
health support. Players make choices that branch the story; a therapist/editorial
layer curates which paths are safe and effective.

**TTA.dev** (`/home/thein/repos/TTA.dev`) provides reusable platform primitives.

## Agent Roster

| Agent | Role | Config |
|---|---|---|
| **Claude Code** | Main agent — primary decision maker | `CLAUDE.md` |
| GitHub Copilot | IDE suggestions | `.github/copilot-instructions.md` |
| Augment | Code intelligence | `.augment/instructions.md` |
| Cline | AI coding assistant | `.cline/instructions.md` |
| Gemini | Secondary review | `GEMINI.md` |

## Memory Access (MANDATORY)

Before any non-trivial task, recall context from Hindsight:
1. `mcp__hindsight__recall` — query `adam-global` for durable directives and cross-project patterns
2. `mcp__hindsight__recall` — query the current derived `project-*` or `workspace-*` bank for TTA-specific context

After completing a significant task (architecture decision, bug root-cause, resolved TODO):
- Cross-project patterns → retain to `adam-global`
- TTA-specific decisions, commands, failures → retain to current derived `project-*`/`workspace-*` bank

Hindsight MCP: `http://localhost:8888/mcp/` | Start: `uvx --from hindsight-api hindsight-local-mcp`

## Non-Negotiable Standards

- **Python**: 3.12+ only
- **Package manager**: `uv` — never `pip install`
- **Type hints**: `str | None` not `Optional[str]`
- **Line length**: 88 chars (Ruff)
- **Type checking**: Pyright `standard` mode
- **Commits**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`)
- **Tests**: pytest `asyncio_mode = "auto"`; integration tests use `@pytest.mark.integration`

## Quality Gate (run before committing)

```bash
uv run ruff check src/ --fix
uv run ruff format src/
uv run pyright src/
make test
```

## Continuous Testing

```bash
make watch        # Reruns unit tests on every .py/.toml save (cancels in-progress run)
make watch-all    # Same, but includes integration tests (requires Neo4j + Redis)
```

## L0 / TTA.dev Interaction Rule

`TTA.dev` owns the emerging **developer-agent L0 control plane**.

TTA does **not** own that layer. In this repo, L0-related work should focus on
**integrating with TTA.dev**, not recreating a second developer control plane
inside `src/agent_orchestration/`.

### What TTA agents should do next for L0

1. keep runtime/player-session orchestration separate from developer-agent orchestration
2. define how TTA build/test/release work should be represented as TTA.dev L0 tasks and runs
3. add adapters or scripts that let TTA.dev-managed agents safely operate on this repo
4. surface enough project/workflow metadata that TTA.dev can coordinate work without touching therapeutic runtime state

### Anti-goal

Do not treat IPA/WBA/NGA runtime coordination as the same problem as Claude/Copilot
developer coordination. Those are different control planes.
