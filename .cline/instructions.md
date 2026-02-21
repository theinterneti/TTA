# TTA (Therapeutic Text Adventure) — Cline Instructions

## Project Overview

TTA is an AI-powered therapeutic text adventure game. Players make choices that branch into different narrative paths; a therapist/editorial safety layer curates which paths are safe and therapeutically effective.

**TTA.dev** (`/home/thein/repos/TTA.dev`) provides the reusable platform primitives TTA is built on.

---

## Key Constraints

| Constraint | Rule |
|---|---|
| Python version | 3.12+ only |
| Package manager | `uv` — never `pip` |
| Type hints | `str \| None` not `Optional[str]` |
| Line length | 88 chars (Ruff) |
| Type checker | Pyright (`standard` mode) |
| Test framework | pytest, `asyncio_mode = "auto"` |
| Commit style | Conventional Commits |

## Before Committing

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
uv run pytest -q -m "not integration and not neo4j and not redis" tests/
```

---

## Architecture

### Multi-Agent Pipeline

```
User Input → IPA → WBA → NGA → SSE Stream → Player
```

- **IPA** (Input Processing Agent): parses intent, extracts entities, validates safety
- **WBA** (World Building Agent): updates world state
- **NGA** (Narrative Generator Agent): generates therapeutic narrative

All agents run via **LangGraph** workflows (`src/agent_orchestration/`).

### Data Stores

- **Redis** — session cache, workflow state, circuit breaker state
- **Neo4j** — story graph (`Scene -[:LEADS_TO]-> Scene`), character relationships
- **Dolt** — future: branching universe state (one branch per timeline fork)

### Key Source Dirs

```
src/agent_orchestration/          # Multi-agent coordination
src/components/gameplay_loop/     # Game loop, narrative engine
src/player_experience/            # Player profiles, sessions, frontend
src/api_gateway/                  # FastAPI + SSE endpoints
src/ai_components/                # LLM clients, prompt builders
packages/tta-ai-framework/        # Workspace package: AI orchestration
packages/tta-narrative-engine/    # Workspace package: narrative generation
```

---

## Development Workflow

```bash
# Install all deps (including TTA.dev path sources)
uv sync --all-extras

# Run unit tests
uv run pytest -q -m "not integration and not neo4j and not redis" tests/

# Run integration tests (needs Redis + Neo4j running)
uv run pytest -m "integration" tests/

# Start API server
uv run python src/main.py start
```

---

## Testing Conventions

```python
# Unit test (no marker needed)
async def test_something():
    ...

# Requires Redis
@pytest.mark.integration
@pytest.mark.redis
async def test_with_redis(redis_client):
    ...

# Requires Neo4j
@pytest.mark.integration
@pytest.mark.neo4j
async def test_with_neo4j(neo4j_driver):
    ...
```

**Never run `tests/post_deployment/` locally** — these require a live deployment.

---

## TTA.dev Dependency

TTA consumes TTA.dev platform packages via local path sources (editable):

- `tta-dev-primitives` — workflow primitives (Router, Retry, Cache, etc.)
- `tta-observability-integration` — metrics, tracing
- `universal-agent-context` — agent memory/context management
- `tta-dev-integrations` — external service integrations

Use `WorkflowPrimitive` composition patterns from `tta-dev-primitives` — don't reinvent retry, timeout, or circuit breaker logic.

---

## Important Files

| File | Purpose |
|---|---|
| `src/main.py` | CLI entrypoint |
| `src/agent_orchestration/agents.py` | Agent registry |
| `src/agent_orchestration/circuit_breaker.py` | Circuit breaker |
| `src/components/gameplay_loop/narrative/engine.py` | Narrative engine |
| `src/player_experience/` | Player management |
| `pyproject.toml` | Deps + tool config |
| `CLAUDE.md` | Primary agent instructions |


---
**Logseq:** [[TTA.dev/.cline/Instructions]]
