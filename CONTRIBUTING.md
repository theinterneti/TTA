# Contributing to TTA

## Quick Start

```bash
# Clone and install
git clone https://github.com/theinterneti/TTA.git
cd TTA
uv sync --all-extras

# Verify setup
uv run pytest tests/unit/ -q          # Should pass 1382 tests
uv run ruff check src/ --fix          # Lint
uv run ruff format src/               # Format
```

## Development Workflow

1. **Branch** from `main` using conventional naming: `feat/`, `fix/`, `refactor/`
2. **Make changes** following the standards below
3. **Run quality gate** before committing:

```bash
uv run ruff check src/ --fix
uv run ruff format src/
uv run pyright src/
uv run pytest tests/unit/ -q
```

4. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new feature
   - `fix:` bug fix
   - `refactor:` code restructuring
   - `test:` test additions/changes
   - `chore:` maintenance tasks
   - `docs:` documentation updates

5. **Open a PR** against `main`

## Code Standards

### Python

- **Version:** 3.12+ required
- **Package manager:** `uv` only (never `pip install`)
- **Type hints:** `str | None` (not `Optional[str]`)
- **Line length:** 88 characters (Ruff)
- **Async:** prefer `async def` for I/O-bound operations
- **Logging:** use `logging.getLogger(__name__)` in every module

### Error Handling

```python
# Wrap external calls with circuit breaker
from src.agent_orchestration.circuit_breaker import CircuitBreaker

circuit_breaker = CircuitBreaker(name="my_service", failure_threshold=5)
result = await circuit_breaker.call(external_function)
```

### Testing

- **Unit tests** in `tests/unit/` — fast, no external services
- **Integration tests** in `tests/integration/` — require Redis/Neo4j
- **Markers:** `@pytest.mark.redis`, `@pytest.mark.neo4j`, `@pytest.mark.integration`

```bash
# Unit tests only (CI default)
uv run pytest tests/unit/ -q

# Integration tests (requires services)
uv run pytest -m "integration" tests/

# Coverage report
uv run pytest --cov=src --cov-report=term-missing tests/unit/
```

## Project Structure

```
src/
  agent_orchestration/     # Multi-agent pipeline (IPA → WBA → NGA)
  ai_components/           # LLM integration
  api_gateway/             # FastAPI routes
  components/              # Gameplay loop, narrative, safety
  player_experience/       # Player-facing features
  common/                  # Shared utilities

packages/
  tta-ai-framework/        # AI orchestration package
  tta-narrative-engine/    # Narrative engine package

tests/
  unit/                    # Fast unit tests (1382 tests)
  integration/             # Service integration tests
  e2e/                     # End-to-end browser tests
```

## Services

Start local services for integration testing:

```bash
bash docker/scripts/tta-docker.sh dev up -d
```

This starts Redis (6379), Neo4j (7474/7687), and Grafana.

## Documentation

- **Architecture:** `docs/architecture/`
- **Milestones:** `docs/milestones/`
- **Development guides:** `docs/development/`
- **Agentic primitives:** `docs/agentic-primitives/`

## Key Patterns

| Pattern | Where Used | Purpose |
|---------|-----------|---------|
| Circuit breaker | `agent_orchestration/` | Graceful degradation |
| Retry with backoff | `agent_orchestration/`, `openhands_integration/` | Transient failure recovery |
| Fallback handler | `model_management/` | Model fallback strategies |
| Cache primitive | `observability_integration/` | Redis caching with metrics |
| Error recovery | `gameplay_loop/narrative/` | Session checkpointing |

---

**Logseq:** [[TTA.dev/Contributing]]
