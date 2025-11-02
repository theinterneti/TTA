# AGENTS.md - Universal Agent Context

> **Universal Standard for AI Agent Context**
> This file provides essential project context for AI coding agents (GitHub Copilot, Cursor, Claude Desktop, etc.)
> Following the AI-Native Development framework's context portability standard.

---

## Project: TTA (Therapeutic Text Adventure)

**Version:** 0.3.0
**Status:** Active Development
**Architecture:** Microservices, Event-Driven, Graph Database

---

## Overview

TTA (Therapeutic Text Adventure) is an AI-powered therapeutic gaming platform that combines:
- **Narrative Engine:** Graph-based story progression using Neo4j
- **Agent Orchestration:** Multi-agent AI system for dynamic storytelling
- **Player Experience:** Real-time therapeutic text adventure gameplay
- **Clinical Integration:** Evidence-based therapeutic interventions

**Core Purpose:** Deliver therapeutic value through AI-generated, personalized narrative experiences.

---

## Technology Stack

### Backend
- **Python:** 3.12+ (primary language)
- **Framework:** FastAPI (async web framework)
- **Package Manager:** UV (Astral's fast Python package manager)
- **Type Checking:** Pyright
- **Linting:** Ruff
- **Testing:** pytest, pytest-asyncio

### Databases
- **Redis:** Session state, caching, pub/sub
- **Neo4j:** Narrative graph, relationship modeling

### AI Integration
- **OpenRouter:** Multi-model AI routing
- **Local Models:** Fallback support

### Infrastructure
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Kubernetes (staging/production)
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus, Grafana

---

## Architecture

### Layered Architecture (Onion/Clean)
```
┌─────────────────────────────────────┐
│     Presentation (FastAPI)          │
├─────────────────────────────────────┤
│  Application (Use Cases/Workflows)  │
├─────────────────────────────────────┤
│     Domain (Business Logic)         │
├─────────────────────────────────────┤
│  Infrastructure (Redis/Neo4j/AI)    │
└─────────────────────────────────────┘
```

### Core Components
- **`src/agent_orchestration/`** - Multi-agent coordination and decision-making
- **`src/player_experience/`** - Player-facing APIs and session management
- **`src/narrative_engine/`** - Story generation and graph traversal
- **`src/common/`** - Shared utilities, models, and infrastructure

### Data Flow
```
Player Request → FastAPI → Agent Orchestration → Narrative Engine → Neo4j
                    ↓              ↓                    ↓
                  Redis    (AI Agents)             (Graph DB)
```

---

## Development Workflow

### Environment Setup
```bash
# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/theinterneti/TTA.git
cd TTA

# Create virtual environment and install dependencies
uv sync --all-extras

# Start development services
docker-compose -f docker-compose.dev.yml up -d
```

### Common Commands
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type check
uvx pyright src/

# Run quality checks
uv run ruff format . && uv run ruff check . --fix && uvx pyright src/
```

### VS Code Tasks
Available tasks (accessible via `Tasks: Run Task`):
- `🧪 Test: Run All Tests`
- `🧪 Test: Run with Coverage`
- `✨ Quality: Format Code (Ruff)`
- `🔍 Quality: Lint Code (Ruff)`
- `🔍 Quality: Type Check (Pyright)`
- `🚀 Dev: Start All Services`
- `🛑 Dev: Stop All Services`

---

## Component Maturity Workflow

TTA uses a three-stage maturity model:

### Development Stage
- **Coverage:** ≥60%
- **Testing:** Unit tests required
- **Files:** <1,000 lines, <500 statements
- **Purpose:** Initial implementation and iteration

### Staging Stage
- **Coverage:** ≥70%
- **Testing:** Integration tests required
- **Quality:** All linting/type-checking passes
- **Purpose:** Pre-production validation

### Production Stage
- **Coverage:** ≥80%
- **Testing:** E2E tests required
- **Quality:** Full quality gates pass
- **Purpose:** Production-ready deployment

**Promotion Command:**
```bash
python scripts/workflow/spec_to_production.py \
  --spec specs/component.md \
  --component component_name \
  --target staging
```

---

## Directory Structure

```
TTA/
├── .augment/                    # AI Agent Primitives
│   ├── chatmodes/              # Role-based AI modes
│   ├── workflows/              # Reusable prompts (.prompt.md)
│   ├── instructions/           # Context-specific rules (.instructions.md)
│   ├── memory/                 # Project learnings (.memory.md)
│   └── context/                # Context helpers (.context.md)
├── src/                        # Source code
│   ├── agent_orchestration/   # Agent coordination
│   ├── player_experience/     # Player APIs
│   ├── narrative_engine/      # Story generation
│   ├── common/                # Shared utilities
│   └── main.py                # Application entry
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── docs/                       # Documentation
├── scripts/                    # Automation scripts
├── monitoring/                 # Observability stack
└── AGENTS.md                   # This file
```

---

## Agent Primitive Instructions

### Where to Find Guidance

**Chatmodes** (`.augment/chatmodes/*.chatmode.md`):
- `architect.chatmode.md` - System design and architecture
- `backend-dev.chatmode.md` - Python/FastAPI implementation
- `devops.chatmode.md` - Infrastructure and deployment
- `qa-engineer.chatmode.md` - Testing and quality assurance
- `frontend-dev.chatmode.md` - UI development

**Workflows** (`.augment/workflows/*.prompt.md`):
- `component-promotion.prompt.md` - Maturity stage advancement
- `bug-fix.prompt.md` - Systematic debugging
- `feature-implementation.prompt.md` - Feature development
- `test-coverage-improvement.prompt.md` - Coverage enhancement

**Instructions** (`.augment/instructions/*.instructions.md`):
- `global.instructions.md` - Project-wide standards (applies to all Python files)
- `testing.instructions.md` - Test organization and patterns
- `quality-gates.instructions.md` - Quality requirements
- `component-maturity.instructions.md` - Maturity workflow guidance

**Memory** (`.augment/memory/*.memory.md`):
- `architectural-decisions/` - Design decisions and rationale
- `testing-patterns.memory.md` - Proven test patterns
- `workflow-learnings.memory.md` - Process insights

---

## Quality Gates

### All Stages
- ✅ Ruff linting passes (`uv run ruff check .`)
- ✅ Pyright type checking passes (`uvx pyright src/`)
- ✅ No secrets detected (`uvx detect-secrets scan`)
- ✅ File size limits: <1,000 lines, <500 statements

### Development → Staging
- ✅ Test coverage ≥70%
- ✅ Integration tests implemented
- ✅ All unit tests pass

### Staging → Production
- ✅ Test coverage ≥80%
- ✅ E2E tests implemented
- ✅ Performance benchmarks pass
- ✅ Security audit complete

---

## Coding Standards

### SOLID Principles
- **S**ingle Responsibility: One reason to change per class/function
- **O**pen-Closed: Extend through composition, not modification
- **L**iskov Substitution: Subtypes must be substitutable
- **I**nterface Segregation: Focused, minimal interfaces
- **D**ependency Inversion: Depend on abstractions, not implementations

### Python Best Practices
- Use type hints on all functions and class attributes
- Async/await for I/O operations
- Pydantic for data validation
- Dataclasses for simple data containers
- Protocol classes for interface definitions
- Context managers for resource management

### Testing Requirements
- AAA pattern (Arrange-Act-Assert)
- Fixtures for reusable test setup
- Markers for test categorization: `@pytest.mark.{component}`
- `@pytest_asyncio.fixture` for async fixtures
- Mock external dependencies (Redis, Neo4j, AI APIs)

---

## MCP Tool Boundaries

### Security Model
Each chatmode has explicit tool boundaries to prevent security issues:

- **Architect:** Read-only codebase analysis, documentation, diagram generation
- **Backend Developer:** Code editing, test writing, local execution
- **DevOps:** Deployment commands, infrastructure changes, monitoring
- **QA Engineer:** Test execution, coverage analysis, quality validation

**Critical:** Tools are scoped per role to prevent:
- Cross-domain interference (e.g., architect modifying production code)
- Security breaches (e.g., frontend accessing backend databases)
- Scope creep (e.g., backend developer deploying to production)

---

## Research Integration

TTA development is guided by AI-Native Development research:

**Query Research Notebook:**
```bash
uv run python scripts/query_notebook_helper.py "Your question here"
```

**Research Topics:**
- Three-layer AI-Native framework (Prompt Engineering, Agent Primitives, Context Engineering)
- MCP tool security patterns
- Agent orchestration best practices
- Context window optimization

**See:** `.augment/RESEARCH_QUICK_REF.md` for common queries

---

## Resources

### Documentation
- **Project Docs:** `docs/` directory
- **API Docs:** Auto-generated from FastAPI
- **Architecture:** `.augment/memory/architectural-decisions/`

### External Links
- **Repository:** https://github.com/theinterneti/TTA
- **FastAPI:** https://fastapi.tiangolo.com/
- **UV:** https://github.com/astral-sh/uv
- **Neo4j Python:** https://neo4j.com/docs/python-manual/
- **Redis Python:** https://redis-py.readthedocs.io/

### Getting Help
1. Check `.augment/memory/` for past learnings
2. Query research notebook for AI development patterns
3. Review relevant `.instructions.md` files for domain guidance
4. Consult chatmodes for role-specific best practices

---

## Agent Onboarding Checklist

When starting work on TTA:

- [ ] Read this AGENTS.md file completely
- [ ] Run `uv sync --all-extras` to install dependencies
- [ ] Start services: `docker-compose -f docker-compose.dev.yml up -d`
- [ ] Run tests to verify setup: `uv run pytest`
- [ ] Review relevant `.instructions.md` for your work area
- [ ] Check `.augment/memory/` for relevant learnings
- [ ] Understand component maturity stage of target component
- [ ] Review MCP tool boundaries for your role

---

**Last Updated:** November 1, 2025
**Maintainers:** TTA Development Team
**Standard:** AI-Native Development Framework (Layer 3: Context Engineering)
