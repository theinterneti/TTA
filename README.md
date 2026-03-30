# TTA — Therapeutic Text Adventure

An AI-powered narrative game for mental health support. Players make choices
that branch the story; a therapist/editorial layer curates which paths are safe
and therapeutically effective.

Built on **[TTA.dev](https://github.com/theinterneti/TTA.dev)** — the reusable
platform primitives powering the game's AI orchestration, observability, and
workflow infrastructure.

---

## Features

### Core User Journey

- **User Registration & Authentication** — secure account creation with JWT auth
- **Character Creation** — player characters with therapeutic profiles
- **World Selection** — choose from curated therapeutic worlds
- **Therapeutic Conversation** — AI-driven narrative responses via OpenRouter
- **Progress Tracking** — milestone detection, therapeutic effectiveness scoring
- **Session History** — persistent conversation retrieval across sessions

### Therapeutic Safety

- **Crisis Detection** — five-level severity classification (NONE → IMMINENT)
- **Emotional Safety System** — real-time content filtering and trigger warnings
- **Therapeutic Integration** — evidence-based intervention generation
- **Safety Monitoring** — comprehensive audit logging and alerting

### Agent Orchestration

- **IPA** — Input Processing Agent: intent extraction, safety validation
- **WBA** — World Building Agent: world state management
- **NGA** — Narrative Generator Agent: therapeutic storytelling
- **Circuit Breaker** — graceful degradation with Redis-persisted state
- **Message Coordination** — Redis-based async agent messaging

---

## Architecture

```
User Input → IPA → WBA → NGA → SSE Stream → Player
```

**Persistence:** Redis (session cache) + Neo4j (story graph).

**API:** FastAPI with SSE streaming, JWT auth.

**Packages:**

| Package | Purpose |
|---------|---------|
| `tta-ai-framework` | AI orchestration, tool management, workflow engine |
| `tta-narrative-engine` | Story generation, narrative arc management |

See [Architecture Documentation](docs/architecture/README.md) for details.

---

## Getting Started

```bash
# Install deps (requires uv, Python 3.12+)
uv sync --all-extras

# Run unit tests (1382 tests, ~70 seconds)
uv run pytest tests/unit/ -q

# Lint + type check
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/

# Start the API
uv run python src/main.py start
```

### Services (Docker)

```bash
# Start Redis + Neo4j + Grafana
bash docker/scripts/tta-docker.sh dev up -d

# Or with docker compose directly
docker compose -f docker/compose/docker-compose.base.yml \
               -f docker/compose/docker-compose.dev.yml up -d
```

### Integration Tests

```bash
# Requires Redis and Neo4j running
uv run pytest -m "integration" tests/
```

---

## Repo Layout

```
src/                        # Game application code (339 Python files)
  agent_orchestration/      # Multi-agent coordination (IPA, WBA, NGA)
  ai_components/            # LLM integration, prompt engineering
  api_gateway/              # FastAPI backend
  components/               # Gameplay loop, narrative engine, safety systems
  player_experience/        # Player profiles, sessions, frontend
  common/                   # Shared utilities, config
  observability_integration/ # Monitoring primitives (cache, router, timeout)

packages/                   # Workspace packages
  tta-ai-framework/         # AI orchestration framework
  tta-narrative-engine/     # Story/narrative engine
  ai-dev-toolkit/           # Development tools (placeholder)

tests/                      # Test suite
  unit/                     # Unit tests (1382 tests)
  integration/              # Integration tests (Redis, Neo4j)
  e2e/                      # End-to-end tests (Playwright)

docs/                       # Documentation
  architecture/             # System architecture diagrams
  milestones/               # Milestone tracking and metrics
  development/              # Development guides
  agentic-primitives/       # Workflow primitive documentation

.github/workflows/          # CI/CD (6 workflows)
docker/                     # Docker configs (base, dev, test, prod)
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
- Circuit breakers on all external service calls
- Async-first architecture (55% of source files)
- Type annotations on 80%+ of source files

See `CLAUDE.md` for full development standards and quality gate.

---

**Logseq:** [[TTA]]


---
**Logseq:** [[TTA.dev/Readme]]
