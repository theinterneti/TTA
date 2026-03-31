# TTA (Therapeutic Text Adventure) — Augment Instructions

## What This Repo Is

**TTA** is an AI-powered therapeutic text adventure game. Players make choices that branch the narrative; a therapist/editorial layer curates which paths are safe and effective.

**TTA.dev** (`/home/thein/repos/TTA.dev`) provides the reusable platform primitives this game is built on.

---

## Repo Layout

```
src/                        # Game application code
  agent_orchestration/      # Multi-agent coordination (IPA, WBA, NGA)
  ai_components/            # LLM integration, prompt engineering
  analytics/                # Player analytics, therapeutic metrics
  api_gateway/              # FastAPI backend
  common/                   # Shared utilities, config
  components/               # Reusable game components (gameplay loop, etc.)
  living_worlds/            # Dynamic world state
  orchestration/            # Service orchestration
  player_experience/        # Player session, UX, frontend
  main.py                   # CLI entrypoint

packages/                   # Workspace packages
  tta-ai-framework/         # AI orchestration framework (game-specific)
  tta-narrative-engine/     # Narrative/story engine (game-specific)
  ai-dev-toolkit/           # Dev tools (depends on TTA.dev packages)

tests/                      # Test suite
  unit/                     # Fast, no external services
  integration/              # Require Redis/Neo4j
  post_deployment/          # Require live deployment
```

---

## Non-Negotiable Standards

- **Python**: 3.12+ (`requires-python = ">=3.12"`)
- **Package manager**: `uv` only — never `pip install`
- **Type hints**: `str | None` not `Optional[str]`; 3.10+ union syntax
- **Line length**: 88 chars (Ruff)
- **Type checking**: Pyright in `standard` mode
- **Commits**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`)
- **Tests**: pytest with `asyncio_mode = "auto"`; mark integration tests `@pytest.mark.integration`

## Quality Gate

```bash
uv run ruff check src/ --fix
uv run ruff format src/
uv run pyright src/
make test
```

---

## Core Architecture: Multi-Agent Workflow

```
User Input
    ↓
IPA (Input Processing Agent) — intent, entities, safety validation
    ↓
WBA (World Building Agent) — world state updates
    ↓
NGA (Narrative Generator Agent) — therapeutic narrative response
    ↓
User Output (SSE stream via FastAPI)
```

**Key classes:**
- `LangGraphAgentOrchestrator` — LangGraph workflow integration (`src/agent_orchestration/`)
- `UnifiedAgentOrchestrator` — IPA/WBA/NGA coordination
- `CircuitBreaker` — Redis-persisted error recovery (`src/agent_orchestration/circuit_breaker.py`)
- `NarrativeEngine` — Scene generation and therapeutic storytelling (`src/components/gameplay_loop/narrative/`)
- `PlayerExperienceManager` — Player profiles and sessions (`src/player_experience/`)

---

## Data Stores

| Store | Role | Current |
|---|---|---|
| Redis | Session cache, workflow state, circuit breaker | Active |
| Neo4j | Story graph, character relationships | Active |
| Dolt | Branching universe state (planned migration) | Future |

---

## Agent Workflow State

```python
class AgentWorkflowState(TypedDict):
    messages: list[BaseMessage]
    player_id: str
    session_id: str
    user_input: str
    ipa_result: dict[str, Any] | None
    wba_result: dict[str, Any] | None
    nga_result: dict[str, Any] | None
    world_context: dict[str, Any]
    therapeutic_context: dict[str, Any]
    safety_level: str
    narrative_response: str
    next_actions: list[str]
```

---

## Story Graph (Neo4j)

```cypher
(Scene)-[:LEADS_TO]->(Scene)
(Character)-[:APPEARS_IN]->(Scene)
(Character)-[:RELATES_TO]->(Character)
(TherapeuticConcept)-[:MODELED_IN]->(Scene)
(PlayerChoice)-[:IMPACTS]->(Scene)
```

---

## Testing Strategy

```bash
# Unit tests (fast, no services)
make test

# Continuous testing (reruns on every .py/.toml save)
make watch

# Integration tests (needs Redis + Neo4j)
make test-integration

# Never run post_deployment locally — needs live deployment
```

**Coverage thresholds:**
- Player-facing features: ≥80%
- Agent orchestration, circuit breaker: ≥75-80%
- Narrative generation: ≥70%

---

## Component Instructions

### Agent Orchestration (`src/agent_orchestration/`)

- Always use async/await — no blocking calls in async workflows
- Wrap agent calls with `CircuitBreaker.call()` for graceful degradation
- Redis key convention: `workflow:{workflow_id}`, `circuit_breaker:{name}`
- Test with `@pytest.mark.integration` for Redis-dependent tests

### Narrative Engine (`src/components/gameplay_loop/narrative/`, `packages/tta-narrative-engine/`)

- Scene generation must include `therapeutic_focus` parameter
- Always inject session context into prompts — no hardcoded prompts
- Persist scenes to Neo4j immediately after generation
- Character archetypes: `wise_guide`, `fellow_traveler`, `inner_voice`

### Player Experience (`src/player_experience/`)

- `PlayerExperienceManager` is the only entry point — don't access repos directly
- Sessions are ephemeral (Redis); player profiles are persistent (Neo4j)
- Therapeutic settings are player-controlled and must be validated before use

### API Gateway (`src/api_gateway/`)

- FastAPI with SSE for streaming narrative responses
- Auth via JWT; player_id in JWT payload
- All routes must handle `CircuitBreakerOpenError` gracefully

---

## TTA.dev Integration

TTA depends on TTA.dev platform packages via path sources:

```toml
[tool.uv.sources]
tta-dev-primitives = { path = "../TTA.dev/platform/primitives", editable = true }
tta-observability-integration = { path = "../TTA.dev/platform/observability", editable = true }
universal-agent-context = { path = "../TTA.dev/platform/agent-context", editable = true }
tta-dev-integrations = { path = "../TTA.dev/platform/integrations", editable = true }
```

Use `WorkflowPrimitive` composition from `tta-dev-primitives` for all orchestration. Don't reimplement retry, circuit breaker, or timeout patterns from scratch.

---

## Common Anti-Patterns

❌ Blocking sync calls inside `async def` functions
❌ Hardcoded prompts without session/therapeutic context injection
❌ Direct database access bypassing manager classes
❌ `pip install` — use `uv add` or `uv sync`
❌ `Optional[str]` — use `str | None`
❌ Tests that require live services without `@pytest.mark.integration`

---

## Knowledge Base Access (MANDATORY)

Before executing any non-trivial task, query the `tta-notes-kb` MCP server:

1. Use `search_kb` to find relevant architectural decisions, prior work, and
   design rationale for the area you are about to change.
2. Use `get_high_priority_todos` to check for open work items related to your task.

Do NOT rely solely on code inspection or this instructions file for project
context — the KB is the canonical source of architectural truth.

## Documenting Your Work (MANDATORY)

After completing any significant task (new feature, architecture decision, bug
root-cause, resolved TODO), invoke the `create-atomic-note` skill:

1. Create a new file in `docs/kb-exports/` following the naming convention and
   frontmatter schema defined in `.claude/skills/create-atomic-note/SKILL.md`.
2. Keep the note to a single topic — split complex work into multiple notes.
3. The repo owner will ingest these files into `TTA-notes` manually.

---
