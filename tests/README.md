# TTA Test Suite

This README is the authoritative map for the TTA test suite. Read it before adding a test, running CI locally, or debugging a failure.

---

## 1. Overview

The suite covers unit, integration, and agent-orchestration layers of the TTA platform (player pipeline: IPA → WBA → NGA). Tests are partitioned so the fast unit tier gives sub-10 s feedback with no services, while the integration and agent-orchestration tiers gate on explicit flags.

**Quality goals**

| Component | Coverage target |
|-----------|----------------|
| Player-facing API / safety | ≥ 80 % |
| Agent orchestration pipeline | ≥ 75 % |
| Crisis / therapeutic safety | ≥ 90 % |
| Utilities / common | ≥ 70 % |
| New code (PR stage) | ≥ 60 % |

CI runs unit tests on every push/PR and uploads coverage to Codecov. Integration tests run when services are available.

---

## 2. Directory Structure

```
tests/
├── unit/                          # Fast, no services required
│   ├── agent_orchestration/       # src/agent_orchestration — adapters, CB, protocol bridge
│   │   └── safety_validation/     # Crisis detection, therapeutic safety validators
│   ├── ai_components/             # LLM clients, prompt registry
│   ├── api_gateway/               # FastAPI route handlers (mocked)
│   ├── choice_detector/           # ChoiceSignificanceDetector
│   ├── common/                    # Shared utilities, config, time_utils, retry
│   ├── components/                # Narrative arc, coherence, world seed, therapeutic modules
│   │   └── gameplay_loop/         # Gameplay loop controller, models, validator, generator
│   ├── dolt/                      # Dolt schema & repository (mocked)
│   ├── first_scene/               # FirstSceneSpec and builder
│   ├── genesis/                   # Genesis agent seed/guide extraction
│   ├── guide/                     # Guide persona
│   ├── model_management/          # ModelSelector, FallbackHandler, providers
│   │   ├── providers/             # Provider-specific model tests
│   │   └── services/              # Model selection and fallback services
│   ├── narrative/                 # Narrative coherence engine, validators
│   ├── observability_integration/ # APM, caching, routing, timeout primitives
│   ├── orchestration/             # ComponentRegistry, orchestrator config, lifecycle
│   ├── player_character/          # PlayerCharacter model and service
│   ├── player_experience/         # Player profile, session, privacy, therapeutic
│   │   └── api/                   # Player-facing API integration (mocked)
│   ├── tools/                     # Tool-calling helpers
│   └── world_context/             # World context builder
│
├── integration/                   # Requires --neo4j / --redis flags
│   ├── agent_orchestration/       # tta-ai-framework IPA/WBA/NGA — needs TTA.dev + Redis
│   │   ├── openhands_integration/ # OpenHands agent wiring
│   │   └── tools/                 # Agent tool surface integration
│   ├── cli/                       # CLI admin commands (Redis required)
│   ├── framework/                 # Comprehensive framework integration
│   ├── model_management/          # ModelSelector with real DB
│   ├── neo4j/                     # Neo4j graph persistence tests
│   ├── openhands/                 # OpenHands integration
│   ├── openhands_integration/     # Openhands agent integration
│   ├── player_experience/         # Player API + session with real Redis/Neo4j
│   └── redis/                     # Redis messaging, session store
│
├── fakes/                         # Reusable in-process fakes (Redis, Neo4j, LLM)
├── helpers/                       # Test utilities shared across tiers
├── security/                      # Security and OWASP tests
├── monitoring/                    # Metrics and Grafana tests
├── workflow/                      # Workflow primitive tests
├── contract/                      # Contract tests (pact)
│
│   ─── Excluded from normal pytest runs (norecursedirs) ───
├── e2e/                           # Playwright end-to-end (TypeScript + Python)
├── e2e-staging/                   # Staging-environment E2E
├── comprehensive_battery/         # Production-like load/adversarial scenarios
├── performance/                   # Benchmarks (pytest-benchmark)
├── mutation/                      # Mutation testing (cosmic-ray)
└── post_deployment/               # Smoke tests after deploy
```

> **`tests/unit/agent_orchestration/`** tests `src/agent_orchestration/` (the TTA runtime).
> **`tests/integration/agent_orchestration/`** tests `tta-ai-framework` (`packages/tta-ai-framework`) — requires TTA.dev cloned as a sibling and Redis running. Both directories are in `norecursedirs` so they are excluded from the default `make test` run.

---

## 3. Running Tests

### Make targets (recommended)

```bash
make test              # Unit tests — no services, ~10–30 s
make test-quick        # tests/unit/ only — fastest feedback, ~5 s
make test-coverage     # Unit tests + coverage report (term-missing)
make test-integration  # Full suite: Redis + Neo4j required
make test-neo4j        # Neo4j tests only
make test-redis        # Redis tests only
make test-status       # Print test counts + coverage % (< 60 s)
make watch             # Continuous unit tests — restarts on every .py/.toml save
make watch-unit        # Continuous tests/unit/ only — sub-5 s loop
make watch-all         # Continuous full suite — services required
```

### Fine-grained pytest commands

```bash
# Single file
uv run pytest tests/unit/agent_orchestration/test_adapter_circuit_breaker.py -v

# Name pattern
uv run pytest -k "test_crisis" -v

# By marker
uv run pytest -m "unit" -v
uv run pytest -m "not slow" -v

# With Redis
uv run pytest --redis tests/integration/ -v

# With Neo4j
uv run pytest --neo4j tests/integration/ -v

# Agent orchestration package tests (IPA/WBA/NGA)
uv run pytest tests/agent_orchestration/ --redis --neo4j -v

# Coverage for a module
uv run pytest tests/unit/ --cov=src/agent_orchestration --cov-report=term-missing
```

### Environment variable alternatives to flags

```bash
RUN_NEO4J_TESTS=1 uv run pytest tests/
RUN_REDIS_TESTS=1 uv run pytest tests/
```

---

## 4. Pytest Markers

All markers must be declared (`--strict-markers` is on). Apply at least one to every test.

| Marker | Meaning |
|--------|---------|
| `unit` | Pure unit test — no network, no DB, no real I/O |
| `integration` | Requires live services; skipped without `--neo4j`/`--redis` |
| `neo4j` | Skipped unless `--neo4j` flag or `RUN_NEO4J_TESTS=1` |
| `redis` | Skipped unless `--redis` flag or `RUN_REDIS_TESTS=1` |
| `e2e` | Full system, Playwright — excluded from normal runs |
| `slow` | Takes > 1 s; skip with `-m "not slow"` for faster loops |
| `property` | Hypothesis property-based test |
| `concrete` | Concrete implementation tests for abstract components |
| `performance` | Benchmark test (pytest-benchmark) |
| `contract` | Contract test (pact-python) |
| `flaky` | Non-deterministic or timing-sensitive — tracked separately |
| `quarantine` | Allowed to fail; does not block CI |
| `comprehensive` | Comprehensive battery — excluded from normal runs |

---

## 5. Writing Tests

### File placement

| Code under test | Test location |
|----------------|--------------|
| `src/agent_orchestration/` | `tests/unit/agent_orchestration/` |
| `src/components/` | `tests/unit/components/` |
| `src/player_experience/` | `tests/player_experience/` |
| `packages/tta-ai-framework` | `tests/agent_orchestration/` |
| Redis/Neo4j integration | `tests/integration/` |

### Conventions

- **AAA pattern** — Arrange / Act / Assert with a blank line between each phase.
- **Docstring required** — One-line docstring describing *what* is tested and *why* it matters.
- **Naming** — `test_<unit>_<scenario>_<expected_outcome>`, e.g. `test_circuit_breaker_opens_after_5_failures`.
- **Markers** — Every test carries `@pytest.mark.unit` or `@pytest.mark.integration` (plus service markers as needed).
- **No magic numbers** — Extract constants with descriptive names.
- **Mock externals** — Use `unittest.mock.AsyncMock` / `MagicMock` for Redis, Neo4j, and LLM clients in unit tests.
- **asyncio** — `asyncio_mode = "auto"` is on; no `@pytest.mark.asyncio` decorator needed.

### Example

```python
import pytest
from unittest.mock import AsyncMock
from src.agent_orchestration.circuit_breaker import (
    CircuitBreakerPrimitive,
    CircuitBreakerOpenError,
    CircuitState,
)

FAILURE_THRESHOLD = 3


@pytest.mark.unit
async def test_circuit_breaker_transitions_to_open_after_threshold():
    """CircuitBreaker opens after consecutive failures, preventing further calls.

    Ensures downstream services are protected from repeated calls
    when they are already unhealthy.
    """
    # Arrange
    breaker = CircuitBreakerPrimitive(failure_threshold=FAILURE_THRESHOLD)
    failing_fn = AsyncMock(side_effect=RuntimeError("service down"))

    # Act — trigger failures up to threshold
    for _ in range(FAILURE_THRESHOLD):
        with pytest.raises(RuntimeError):
            await breaker.execute(failing_fn)

    # Assert — circuit is now open; next call raises immediately
    assert breaker.state == CircuitState.OPEN
    with pytest.raises(CircuitBreakerOpenError):
        await breaker.execute(failing_fn)
```

### Reusable fakes

`tests/fakes/` contains in-process fakes for Redis, Neo4j, and LLM clients. Prefer them over `MagicMock` when you need realistic behaviour (e.g. TTL semantics, Cypher-like query routing).

---

## 6. Continuous Testing Workflow

`make watch-unit` is the recommended inner loop during development:

```
watchexec -r -e py,toml --clear -- uv run pytest -q -x -m "not integration ..." tests/unit/
```

- **`-x`** — stops on the first failure so you see the error immediately.
- **`-r`** — restarts the process on every `.py` or `.toml` change.
- **`--clear`** — clears the terminal before each run for a clean read.

> **Rule:** red bar = stop and fix before continuing. Never let failures accumulate.

`make watch` covers the full `tests/` directory (still no services). `make watch-all` adds `--neo4j --redis` for service-level feedback.

---

## 7. CI Integration

Six GitHub Actions workflows gate merges (intentionally lean — do not add more without strong justification):

| Workflow | Trigger | What it runs |
|----------|---------|--------------|
| `tests.yml` | push / PR | Unit tests (`-m "not integration and not neo4j and not redis"`); uploads coverage to Codecov |
| `coverage.yml` | push / PR | Integration tests with Redis + Neo4j services; uploads integration coverage |
| `code-quality.yml` | push / PR | `ruff check`, `ruff format --check`, `pyright` |
| `security-scan.yml` | push / PR | Bandit, dependency audit |
| `deploy-staging.yml` | merge to `main` | Staging deploy + post-deployment smoke tests |
| `deploy-production.yml` | manual / tag | Production deploy |

The **mandatory quality gate** before committing:

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
uv run pytest -q -m "not integration and not neo4j and not redis" tests/
```
