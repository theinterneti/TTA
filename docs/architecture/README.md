# TTA Architecture Documentation

## System Overview

TTA uses a multi-agent orchestration architecture with three core agents
coordinated through Redis-based messaging and protected by circuit breakers.

```
User Input → IPA → WBA → NGA → SSE Stream → Player
```

### Agent Pipeline

| Agent | Role | Key Module |
|-------|------|-----------|
| **IPA** (Input Processing) | Intent extraction, safety validation | `src/agent_orchestration/agents.py` |
| **WBA** (World Building) | World state management | `src/agent_orchestration/agents.py` |
| **NGA** (Narrative Generation) | Therapeutic storytelling | `src/agent_orchestration/agents.py` |

### Data Stores

| Store | Purpose | Port |
|-------|---------|------|
| **Redis** | Session cache, message coordination, circuit breaker state | 6379 |
| **Neo4j** | Story graph, player relationships, world state | 7474/7687 |

### API Layer

- **FastAPI** with SSE streaming for real-time narrative delivery
- **JWT authentication** for secure session management
- **Rate limiting** and input validation on all endpoints

## Package Dependencies

```
tta-ai-framework          # AI orchestration, tool management
  └── tta-narrative-engine # Story generation, narrative arcs

src/agent_orchestration    # Multi-agent coordination
  ├── circuit_breaker      # Graceful degradation
  ├── messaging            # Redis message coordination
  └── capabilities         # Auto-discovery, diagnostics

src/components/gameplay_loop
  ├── narrative/           # 15 narrative modules
  ├── consequence_system/  # Outcome generation
  └── choice_architecture/ # Player agency

src/player_experience
  ├── api/                 # FastAPI routers
  ├── managers/            # Business logic
  ├── services/            # Session, progress, safety
  └── models/              # Pydantic data models
```

## Resilience Patterns

| Pattern | Implementation | Usage |
|---------|---------------|-------|
| Circuit Breaker | `agent_orchestration/circuit_breaker.py` | External service calls |
| Retry with Backoff | `agent_orchestration/retry.py` | Transient failures |
| Fallback Handler | `model_management/services/fallback_handler.py` | Model routing |
| Error Recovery | `gameplay_loop/narrative/error_recovery_manager.py` | Session checkpointing |
| Cache Primitive | `observability_integration/primitives/cache.py` | Redis caching |
| Timeout Primitive | `observability_integration/primitives/timeout.py` | Async deadlines |

## Detailed Documentation

| Document | Description |
|----------|-------------|
| [Agent Orchestration](agent-orchestration.md) | Multi-agent coordination details |
| [System Architecture](system-architecture-diagram.md) | High-level system diagram |
| [Data Flow](data-flow-diagram.md) | Request/response data flow |
| [Database](database.md) | Neo4j and Redis schema |
| [Dependency Graph](dependency-graph.md) | Module dependency map |
| [Component Interactions](component-interaction-diagram.md) | Inter-component communication |
| [Agentic Primitives](agentic-primitives-analysis.md) | Workflow primitive analysis |


---