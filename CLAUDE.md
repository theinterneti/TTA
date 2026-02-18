# TTA — Claude Code (Main Agent)

Claude Code is the **primary/main agent** for this repository.

## What This Repo Is

**Therapeutic Text Adventure (TTA)** — An AI-powered narrative game for mental health support. Players make choices that branch the story; a therapist/editorial layer curates which paths are safe and effective.

**TTA.dev** (`/home/thein/repos/TTA.dev`) provides the reusable platform primitives this game is built on.

## Repo Layout

```
src/                    # Game application code (324 Python files)
  agent_orchestration/  # Multi-agent coordination
  ai_components/        # LLM integration, prompt engineering
  analytics/            # Player analytics, therapeutic metrics
  api_gateway/          # FastAPI backend
  common/               # Shared utilities, config
  components/           # Reusable game components
  living_worlds/        # Dynamic world state
  orchestration/        # Service orchestration
  player_experience/    # Player session, UX
  main.py               # CLI entrypoint

packages/               # Workspace packages
  tta-ai-framework/     # AI orchestration framework (game-specific)
  tta-narrative-engine/ # Narrative/story engine (game-specific)
  ai-dev-toolkit/       # Dev tools (excluded from workspace — depends on unpublished TTA.dev packages)

tests/                  # Test suite
  conftest.py           # Shared fixtures
  ...

.github/workflows/      # CI/CD (kept minimal — 6 workflows)
```

## Agent Context

| Agent | Role | Config |
|---|---|---|
| **Claude Code** | **Main agent — primary decision maker** | `CLAUDE.md` (this file) |
| Gemini | Secondary review | `GEMINI.md` |
| GitHub Copilot | IDE suggestions | `.github/copilot-instructions.md` |

## Non-Negotiable Standards

- **Python version**: 3.12+ (`requires-python = ">=3.12"`)
- **Package manager**: `uv` only — never `pip install`, never `pip -e .`
- **Type hints**: `str | None` not `Optional[str]`; 3.10+ union syntax
- **Line length**: 88 chars (Ruff)
- **Imports**: `ruff --fix` handles sorting
- **Type checking**: Pyright in `standard` mode
- **Commits**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`)
- **Tests**: pytest with `asyncio_mode = "auto"`; mark integration tests `@pytest.mark.integration`

## Quality Gate

Before committing:
```bash
cd /home/thein/repos/TTA
uv run ruff check src/ --fix
uv run ruff format src/
uv run pyright src/
uv run pytest -q -m "not integration and not neo4j and not redis" tests/
```

Run integration tests when services are available:
```bash
uv run pytest -m "integration" tests/
```

## Common Commands

```bash
# Install all deps
uv sync

# Run unit tests only (fast, no external services)
uv run pytest -q -m "not integration and not neo4j and not redis" tests/

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing tests/

# Lint and format
uv run ruff check src/ --fix && uv run ruff format src/

# Type check
uv run pyright src/

# Start the API server
uv run python src/main.py start
```

## Workspace Packages

```bash
# Add a dep to main project
uv add <package>

# Add a dep to a workspace package
uv add --package tta-ai-framework <package>

# Install workspace packages in editable mode
uv sync --all-extras
```

## Key Architecture Decisions

- **Persistence**: Currently Redis (session cache) + Neo4j (graph). Long-term: migrate to Dolt (branch = universe, commit = game state).
- **API**: FastAPI with SSE for streaming narrative responses.
- **Multi-agent**: Orchestration layer coordinates multiple LLMs (player model, therapeutic model, world model).
- **Branching universes**: Every significant player choice can fork a timeline. Dolt branches model this natively.

## Known Issues (Fix in Progress)

1. **httpx conflict**: `codecarbon>=3.0.7` conflicts with `openhands-sdk` on httpx version. Codecarbon is temporarily disabled in `pyproject.toml`.
2. **ai-dev-toolkit excluded**: `packages/ai-dev-toolkit` depends on unpublished TTA.dev packages — excluded from workspace until TTA.dev packages are published to PyPI.
3. **CI/CD**: Reduced from 35 → 6 workflows. Some workflows referenced scripts/services that don't exist in CI.

## What NOT to Do

- Don't add more CI/CD workflows without good reason — we deliberately cut from 35 to 6
- Don't commit `.log`, `.sqlite`, `.db`, coverage reports, or test output files
- Don't run `pip` or `pip install` — use `uv` exclusively
- Don't push broken commits to `main` — branch and PR instead
- Don't add `torch`, `transformers`, or GPU deps to new modules without justification


---
**Logseq:** [[TTA.dev/Claude]]
