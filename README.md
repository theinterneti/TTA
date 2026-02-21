# TTA — Therapeutic Text Adventure

An AI-powered narrative game for mental health support. Players make choices that branch the story; a therapist/editorial layer curates which paths are safe and therapeutically effective.

Built on **[TTA.dev](../TTA.dev)** — the reusable platform primitives powering the game's AI orchestration, observability, and workflow infrastructure.

---

## Architecture

```
User Input → IPA → WBA → NGA → SSE Stream → Player
```

- **IPA** — Input Processing Agent: intent extraction, safety validation
- **WBA** — World Building Agent: world state management
- **NGA** — Narrative Generator Agent: therapeutic storytelling

**Persistence:** Redis (session cache) + Neo4j (story graph). Long-term plan: Dolt branches as universe forks.

**API:** FastAPI with SSE streaming, JWT auth.

---

## Getting Started

```bash
# Install deps (requires uv, Python 3.12+)
uv sync --all-extras

# Run unit tests
uv run pytest -q -m "not integration and not neo4j and not redis" tests/

# Lint + type check
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/

# Start the API
uv run python src/main.py start
```

---

## Repo Layout

```
src/                        # Game application code
  agent_orchestration/      # Multi-agent coordination (IPA, WBA, NGA)
  ai_components/            # LLM integration, prompt engineering
  api_gateway/              # FastAPI backend
  components/               # Gameplay loop, narrative engine
  player_experience/        # Player profiles, sessions, frontend
  common/                   # Shared utilities, config

packages/                   # Workspace packages
  tta-ai-framework/         # AI orchestration framework
  tta-narrative-engine/     # Story/narrative engine

tests/                      # Test suite (unit + integration + post_deployment)
.github/workflows/          # CI/CD (6 workflows)
```

---

## Agent Configuration

| Agent | Config |
|---|---|
| Claude Code | `CLAUDE.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Augment | `.augment/instructions.md` |
| Cline | `.cline/instructions.md` |

---

## Key Standards

- Python 3.12+, `uv` for package management
- Ruff for lint/format, Pyright for type checking
- Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`)

See `CLAUDE.md` for full development standards and quality gate.

---

**Logseq:** [[TTA]]


---
**Logseq:** [[TTA.dev/Readme]]
