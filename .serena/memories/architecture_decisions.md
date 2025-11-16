# TTA Architecture Decisions

## Monorepo Structure

The TTA project uses a **single monorepo approach** at `/home/thein/recovered-tta-storytelling`:

```
recovered-tta-storytelling/
├── tta/                    # Legacy/reference subdirectory
├── src/                    # Main source code
│   ├── agent_orchestration/
│   ├── player_experience/
│   ├── ai_components/
│   ├── infrastructure/
│   └── ...
├── tests/                  # Test suites
├── docs/                   # Documentation
├── scripts/                # Development scripts
└── config/                 # Configuration files
```

**Key Decision**: Single monorepo rather than multi-repo architecture. The `tta.dev/`, `tta.prototype/`, `tta.prod/` references are **subdirectories within the main repo**, not separate repositories or submodules.

## Component Maturity Promotion Workflow

Components progress **independently** through maturity stages:

```
Development → Staging → Production
```

**Tracking Mechanism**:
- **GitHub Projects**: Columns for each stage (Development, Staging, Production)
- **GitHub Issues**: Track promotion blockers and requirements
- **TODO Comments**: Reference specific issues (e.g., `# TODO(#123): Fix before staging`)
- **Component Labels**: `component:player-experience`, `component:agent-orchestration`, `target:staging`, etc.

**Philosophy**: Individual components mature at their own pace based on quality criteria, not monolithic releases.

## Three-Environment Separation

### Development Environment
- **Purpose**: Active feature development, rapid iteration
- **Testing**: Unit tests, local integration tests
- **Database**: Local Redis/Neo4j instances
- **Docker**: `docker-compose.dev.yml`

### Staging Environment
- **Purpose**: Pre-production validation, integration testing
- **Testing**: Integration tests, comprehensive E2E tests
- **Database**: Staging Redis/Neo4j with production-like data
- **Docker**: `docker-compose.staging.yml`, `docker-compose.staging-homelab.yml`
- **Deployment**: Home lab for multi-user testing

### Production Environment
- **Purpose**: Live therapeutic storytelling platform
- **Testing**: Smoke tests, monitoring validation
- **Database**: Production Redis/Neo4j with full persistence
- **Docker**: `docker-compose.yml` (production config)

## Database Architecture

### Redis - State Management
- **Purpose**: Session state, player progress, real-time data
- **Usage Patterns**:
  - Session management (player state, active sessions)
  - Caching (frequently accessed data)
  - Pub/Sub (real-time events, WebSocket coordination)
  - Tool registry (agent orchestration)
- **Test Marker**: `@pytest.mark.redis`

### Neo4j - Story Graphs
- **Purpose**: Narrative structure, story relationships, world building
- **Usage Patterns**:
  - Story node graphs (narrative choices, branching paths)
  - Character relationships
  - World state and causal connections
  - Therapeutic journey tracking
- **Test Marker**: `@pytest.mark.neo4j`

**Integration**: Both databases work together - Redis for ephemeral state, Neo4j for persistent narrative structure.

## Agent Orchestration Architecture

### Workflow-Based Design

Core components in `src/agent_orchestration/`:

- **`workflow.py`**: Workflow definitions
  - `WorkflowType`: INPUT_PROCESSING, WORLD_BUILDING, NARRATIVE_GENERATION, COLLABORATIVE
  - `WorkflowDefinition`: Agent sequences, parallel steps, error handling
  - `AgentStep`: Individual agent execution units
  - `ErrorHandlingStrategy`: FAIL_FAST, RETRY, SKIP_ON_ERROR

- **`agents.py`**: Agent registry and metrics
  - `Agent`: Base agent abstraction
  - `AgentRegistry`: Dynamic agent discovery and management
  - `AgentMetrics`: Performance tracking

- **`unified_orchestrator.py`**: Central orchestration logic
- **`langgraph_integration.py`**: LangGraph framework integration
- **`circuit_breaker.py`**: Fault tolerance and resilience

### Key Patterns

1. **Workflow Composition**: Agents composed into workflows (sequential, parallel, conditional)
2. **Circuit Breaker**: Fault tolerance for agent failures
3. **Real-time Streaming**: Progressive feedback via WebSocket (`src/agent_orchestration/realtime/`)
4. **Tool Coordination**: Centralized tool registry and invocation (`src/agent_orchestration/tools/`)

## API Gateway and Service Communication

### Service Architecture

- **API Gateway**: `src/api_gateway/` - Central entry point, routing, authentication
- **Service Modules**:
  - `src/player_experience/` - Player-facing features
  - `src/agent_orchestration/` - AI agent coordination
  - `src/ai_components/` - AI model integration
  - `src/infrastructure/` - Database, monitoring, shared services

### Communication Patterns

1. **REST APIs**: Standard HTTP endpoints for CRUD operations
2. **WebSocket**: Real-time bidirectional communication (chat, progress updates)
3. **Redis Pub/Sub**: Inter-service event messaging
4. **Direct Function Calls**: Within monorepo, services can import and call directly

### Authentication Flow

- **OAuth Integration**: Secure third-party authentication
- **Session Management**: Redis-backed sessions
- **API Key Handling**: Server-side storage, never in localStorage
- **Security**: Proper CORS, CSRF protection, secure cookie handling

## Technology Stack

- **Language**: Python 3.11+
- **Package Manager**: UV (uv/uvx for tools)
- **Web Framework**: FastAPI (async/await)
- **AI Framework**: LangGraph, OpenRouter integration
- **Databases**: Redis, Neo4j
- **Testing**: pytest, pytest-asyncio, Playwright
- **Linting**: Ruff
- **Type Checking**: Pyright
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
