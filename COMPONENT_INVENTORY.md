# TTA Component Inventory

**Date**: October 29, 2025
**Status**: Active - Complete Inventory
**Purpose**: Track all TTA components, their maturity, dependencies, and TTA.dev migration status

---

## Executive Summary

| Category | Count | In Development | In Staging | In Production |
|----------|-------|----------------|------------|---------------|
| Core Components | 12 | 8 | 4 | 0 |
| Integrations | 5 | 3 | 2 | 0 |
| Infrastructure | 4 | 4 | 0 | 0 |
| Testing Tools | 3 | 3 | 0 | 0 |
| **Total** | **24** | **18** | **6** | **0** |

---

## Core TTA Components

### 1. Agent Orchestration (`src/agent_orchestration/`)

**Status**: Development
**Priority**: P0
**Test Coverage**: ~65%
**TTA.dev Status**: Stays in TTA (core platform logic)

**Description**: Multi-agent coordination with circuit breaker patterns, Redis messaging, and health monitoring.

**Key Files**:
- `agents.py` - Agent registry and lifecycle
- `circuit_breaker.py` - Circuit breaker implementation
- `messaging.py` - Redis-based message coordination
- `protocol_bridge.py` - Real/mock agent adapter

**Dependencies**:
- Redis (message queue)
- Neo4j (state persistence)
- `tta-dev-primitives` (retry, fallback patterns)

**Blockers**:
- Test coverage needs improvement
- Circuit breaker metrics integration

**Next Steps**:
- Increase test coverage to ≥70%
- Add integration tests with real Redis
- Document agent protocol

---

### 2. Carbon (`src/components/carbon/`)

**Status**: Staging (Promoted 2025-10-21)
**Priority**: P1
**Test Coverage**: 76.2%
**TTA.dev Status**: Stays in TTA

**Description**: Core infrastructure component for content management and caching.

**Maturity File**: `src/components/carbon/MATURITY.md`

**Quality Gates**:
- ✅ Test coverage ≥70%
- ✅ Linting clean
- ✅ Type checking clean
- ✅ Security scan clean

**Dependencies**:
- Redis (caching)
- Internal: `common/` utilities

**Next Steps**:
- 7-day staging observation
- Integration validation
- Production promotion readiness

---

### 3. Gameplay Loop (`src/components/gameplay_loop/`)

**Status**: Development
**Priority**: P0
**Test Coverage**: 100%
**TTA.dev Status**: Stays in TTA

**Description**: Core gameplay mechanics, narrative engine, player interactions.

**Key Files**:
- `narrative_engine.py`
- `player_input_handler.py`
- `world_state_manager.py`

**Quality Issues**:
- ❌ 108 linting errors (MUST fix)
- ❌ 356 type errors (SIGNIFICANT work)
- ❌ README missing

**Estimated Effort to Staging**: 6-7 hours

**Dependencies**:
- Neo4j (world state)
- Narrative Coherence component
- Model Management component

**Next Steps**:
- Fix linting errors
- Resolve type errors
- Create README
- Target staging promotion

---

### 4. LLM Component (`src/components/llm/`)

**Status**: Staging (Promoted 2025-10-21)
**Priority**: P1
**Test Coverage**: 73%
**TTA.dev Status**: Stays in TTA

**Description**: LLM integration layer with model selection, fallback handling, and circuit breaker protection.

**Maturity File**: `src/components/llm/MATURITY.md`

**Dependencies**:
- OpenRouter API
- `tta-dev-primitives` (circuit breakers)
- Model Management component

**Next Steps**:
- Staging observation period
- Performance validation
- Cost tracking verification

---

### 5. Model Management (`src/components/model_management/`)

**Status**: Development
**Priority**: P0
**Test Coverage**: 100%
**TTA.dev Status**: Stays in TTA

**Description**: Model selection, configuration, and performance tracking.

**Quality Issues**:
- ❌ 59 linting errors
- ❌ 74 type errors
- ✅ README exists

**Estimated Effort to Staging**: 2.75 hours

**Dependencies**:
- `common/config`
- LLM component

**Next Steps**:
- Fix linting errors
- Resolve type errors
- Target staging promotion

---

### 6. Narrative Coherence (`src/components/narrative_coherence/`)

**Status**: Development (Ready for Staging)
**Priority**: P0
**Test Coverage**: 72%
**TTA.dev Status**: Stays in TTA

**Description**: Narrative validation, coherence checking, story arc management.

**Maturity File**: `src/components/narrative_coherence/MATURITY.md`

**Quality Gates**:
- ✅ Test coverage 72% (≥70%)
- ⚠️ 40 linting errors (needs fixing)
- ⚠️ 20 type errors (needs fixing)
- ✅ Security clean
- ❌ README missing

**Estimated Effort to Staging**: 2 hours

**Dependencies**:
- Gameplay Loop
- Neo4j (narrative graph)

**Next Steps**:
- Fix linting errors
- Resolve type errors
- Create README
- **RECOMMENDED NEXT** for staging promotion

---

### 7. Neo4j Component (`src/components/neo4j/`)

**Status**: Development
**Priority**: P1
**Test Coverage**: 0% (tests need refactoring)
**TTA.dev Status**: Stays in TTA

**Description**: Neo4j database abstraction, query management, connection pooling.

**Maturity File**: `src/components/neo4j/MATURITY.md`

**Blocker**:
- ❌ Tests use heavy mocking, need refactoring for actual execution
- Coverage shows 0% due to mock-only tests

**Dependencies**:
- Neo4j database
- `common/config`

**Next Steps**:
- Refactor tests to reduce mocking
- Achieve ≥70% real coverage
- Integration test with real Neo4j

---

### 8. Player Experience (`src/components/player_experience/`)

**Status**: Development
**Priority**: P1
**Test Coverage**: Unknown
**TTA.dev Status**: Stays in TTA

**Description**: User-facing APIs, session management, player state tracking.

**Dependencies**:
- Gameplay Loop
- Agent Orchestration
- Redis (sessions)

**Next Steps**:
- Add test coverage measurement
- Create MATURITY.md
- Document API

---

### 9. App Component (`src/components/app/`)

**Status**: Staging (Promoted 2025-10-21)
**Priority**: P1
**Test Coverage**: 72%
**TTA.dev Status**: Stays in TTA

**Description**: Application initialization, configuration, lifecycle management.

**Maturity File**: `src/components/app/MATURITY.md`

**Quality Gates**: All passed

**Next Steps**:
- Complete 7-day staging observation
- Production promotion readiness

---

### 10. Docker Component (`src/components/docker/`)

**Status**: Development
**Priority**: P2
**Test Coverage**: Unknown
**TTA.dev Status**: Stays in TTA

**Description**: Docker orchestration utilities, container management.

**Next Steps**:
- Add test coverage
- Create MATURITY.md
- Document usage

---

### 11. Narrative Arc Orchestrator (`src/components/narrative_arc_orchestrator/`)

**Status**: Development
**Priority**: P1
**Test Coverage**: Unknown
**TTA.dev Status**: Stays in TTA

**Description**: High-level narrative arc management, story progression.

**Dependencies**:
- Narrative Coherence
- Gameplay Loop
- Neo4j

**Next Steps**:
- Add test coverage
- Create MATURITY.md
- Integration testing

---

### 12. User Experience (`src/components/user_experience/`)

**Status**: Development
**Priority**: P2
**Test Coverage**: Unknown
**TTA.dev Status**: Stays in TTA

**Description**: UI/UX utilities, player interaction patterns.

**Next Steps**:
- Define scope
- Add test coverage
- Create MATURITY.md

---

## Infrastructure Components

### 1. Common Utilities (`src/common/`)

**Status**: Development
**Priority**: P0
**Test Coverage**: Varies by module
**TTA.dev Status**: Some utilities could migrate

**Description**: Shared utilities, models, configuration.

**Key Modules**:
- `config/` - Configuration management
- `models/` - Shared data models
- `utils/` - Utility functions
- `logging/` - Logging infrastructure

**Potential TTA.dev Candidates**:
- Retry decorators → `tta-dev-primitives`
- Configuration patterns → `tta-dev-primitives`
- Logging patterns → `tta-observability-integration`

---

### 2. Observability Integration (`src/observability_integration/`)

**Status**: Development (Exported)
**Priority**: P1
**Test Coverage**: ~75%
**TTA.dev Status**: ✅ **EXPORTED** - Needs merge

**Description**: OpenTelemetry APM, Grafana dashboards, metrics collection.

**Export Location**: `export/tta-observability-integration/`

**Features**:
- 6 Grafana dashboards
- OpenTelemetry integration
- Component maturity metrics
- Circuit breaker observability
- LLM cost tracking

**Next Steps**:
- **MERGE into TTA.dev repository**
- Publish as `tta-observability-integration` package
- Update TTA to use published package

---

### 3. Developer Dashboard (`src/developer_dashboard/`)

**Status**: Development
**Priority**: P2
**Test Coverage**: Unknown
**TTA.dev Status**: Stays in TTA (config only)

**Description**: Local development dashboard, TTA-specific configuration.

**Note**: Dashboards themselves migrated to `tta-observability-integration`.

---

### 4. Monitoring (`src/monitoring/`)

**Status**: Development
**Priority**: P2
**Test Coverage**: Unknown
**TTA.dev Status**: Evaluate for TTA.dev

**Description**: Monitoring utilities, health checks.

**Potential Migration**: Consider merging with `tta-observability-integration`.

---

## Integration Components

### 1. Living Worlds (`src/living_worlds/`)

**Status**: Development
**Priority**: P1
**Test Coverage**: Unknown
**TTA.dev Status**: Stays in TTA

**Description**: Dynamic world simulation, NPC behavior, environmental systems.

**Dependencies**:
- Neo4j (world graph)
- Agent Orchestration
- Gameplay Loop

**Next Steps**:
- Add test coverage
- Create MATURITY.md
- Define world simulation API

---

### 2. Analytics (`src/analytics/`)

**Status**: Development
**Priority**: P2
**Test Coverage**: Unknown
**TTA.dev Status**: Stays in TTA

**Description**: Player analytics, session tracking, usage metrics.

**Next Steps**:
- Define analytics requirements
- Add test coverage
- Privacy/HIPAA compliance review

---

### 3. API Gateway (`src/api_gateway/`)

**Status**: Development
**Priority**: P1
**Test Coverage**: Unknown
**TTA.dev Status**: Stays in TTA

**Description**: API routing, authentication, rate limiting.

**Next Steps**:
- Add test coverage
- Create MATURITY.md
- Security review

---

### 4. AI Components (`src/ai_components/`)

**Status**: Development
**Priority**: P1
**Test Coverage**: Unknown
**TTA.dev Status**: Evaluate for TTA.dev

**Description**: AI-specific utilities and components.

**Potential Migration**: Generic AI utilities could move to TTA.dev.

---

### 5. Test Components (`src/test_components/`)

**Status**: Development
**Priority**: P2
**Test Coverage**: N/A (testing infrastructure)
**TTA.dev Status**: Evaluate for TTA.dev

**Description**: Testing utilities, fixtures, mocks.

**Potential Migration**: Generic testing tools could move to TTA.dev.

---

## Packages (Already in TTA.dev or Packaged)

### 1. Universal Agent Context (`packages/universal-agent-context/`)

**Status**: ✅ **PACKAGED**
**TTA.dev Status**: ✅ Already published

**Description**: Cross-platform agentic primitives.

**Repository**: TTA main repo (for development)
**Published**: Available for other projects

---

### 2. AI Dev Toolkit (`packages/ai-dev-toolkit/`)

**Status**: ✅ **PACKAGED**
**TTA.dev Status**: ✅ Already published

**Description**: AI development utilities and workflow primitives.

**Repository**: TTA main repo (for development)
**Published**: Available for other projects

---

### 3. TTA AI Framework (`packages/tta-ai-framework/`)

**Status**: Development
**TTA.dev Status**: In development

**Description**: TTA-specific AI framework extensions.

---

### 4. TTA Narrative Engine (`packages/tta-narrative-engine/`)

**Status**: Development
**TTA.dev Status**: In development

**Description**: Narrative engine abstractions.

---

## External Dependencies on TTA.dev

### 1. tta-dev-primitives

**Source**: `https://github.com/theinterneti/TTA.dev.git`
**Branch**: main
**Subdirectory**: `packages/tta-dev-primitives`

**Usage in TTA**:
- Retry decorators
- Fallback handlers
- Circuit breaker patterns
- Error recovery

**Status**: ✅ Active dependency

**Version Control**: Currently git reference, needs semantic versioning

---

### 2. tta-workflow-primitives

**Source**: TTA.dev repository
**Status**: Referenced but not yet published

**Planned Usage**:
- Workflow composition
- Quality gate automation
- Stage handlers

**Next Steps**: Publish to PyPI or as git package

---

### 3. Keploy Framework

**Source**: TTA.dev repository
**Package**: `keploy-framework`

**Status**: ✅ Extracted and packaged

**Documentation**: `KEPLOY_FRAMEWORK_EXTRACTION_COMPLETE.md`

---

## Testing Infrastructure

### 1. Comprehensive Test Battery (`tests/comprehensive_battery/`)

**Status**: Development
**TTA.dev Status**: **DECISION NEEDED**

**Description**: Multi-category testing framework.

**Categories**:
- Standard tests (unit, integration, E2E)
- Adversarial tests
- Load/stress tests
- Data pipeline tests
- Dashboard tests

**Migration Options**:
- **Option A**: Extract to TTA.dev with Python language markers
- **Option B**: Keep in TTA main repo

**Concern**: Python-specific, may pollute context engineering

---

### 2. Mutation Testing (`tests/mutation/`)

**Status**: Development
**TTA.dev Status**: Keep in TTA

**Description**: Mutation testing infrastructure.

**Tools**: mutmut, cosmic-ray

---

### 3. Performance Testing (`tests/performance/`)

**Status**: Development
**TTA.dev Status**: Keep in TTA

**Description**: Load testing, stress testing, performance benchmarks.

---

## Component Promotion Pipeline

### Ready for Staging (Immediate)

1. **Narrative Coherence** (~2 hours effort)
   - Fix 40 linting errors
   - Resolve 20 type errors
   - Create README

### In Staging (Observation Period)

1. **Carbon** (Promoted 2025-10-21)
2. **LLM** (Promoted 2025-10-21)
3. **App** (Promoted 2025-10-21)

### Development (Needs Work)

1. **Gameplay Loop** (~6-7 hours effort)
2. **Model Management** (~2.75 hours effort)
3. **Neo4j** (Test refactoring needed)
4. **Agent Orchestration** (Coverage improvement needed)

---

## TTA.dev Migration Action Items

### Immediate Actions

1. **Merge Observability Integration** to TTA.dev
   - Source: `export/tta-observability-integration/`
   - Target: `TTA.dev/packages/tta-observability-integration/`
   - Publish to PyPI

2. **Formalize tta-dev-primitives Dependency**
   - Add semantic versioning
   - Pin to specific version or version range
   - Document update process

3. **Test Battery Decision**
   - Decide: Extract or keep in main repo?
   - If extract: Add language markers
   - If keep: Document rationale

### Medium-term Actions

1. **Evaluate Common Utilities**
   - Identify generic utilities
   - Extract to TTA.dev if applicable
   - Update import paths in TTA

2. **Publish Workflow Primitives**
   - Complete `tta-workflow-primitives` package
   - Publish to TTA.dev
   - Integrate into TTA workflows

3. **Component Documentation**
   - Ensure all components have MATURITY.md
   - Document dependencies clearly
   - Track TTA.dev migration status

---

## Quality Gate Tracking

### Coverage by Stage

| Stage | Required | Components Meeting |
|-------|----------|-------------------|
| Development | ≥60% | Most components |
| Staging | ≥70% | 4 components |
| Production | ≥85% | 0 components |

### Blockers by Type

| Type | Count | Top Issues |
|------|-------|-----------|
| Linting | 207 | Gameplay Loop (108), Model Mgmt (59), Narrative (40) |
| Type Errors | 450 | Gameplay Loop (356), Model Mgmt (74), Narrative (20) |
| Test Coverage | 3 | Neo4j (0%), several unknown |
| Documentation | 5 | READMEs missing |

---

## Next Steps

### Week 1 (Nov 4-8)
1. ✅ Create tier detection workflow template
2. Modify tests.yml for tier-aware testing
3. Promote Narrative Coherence to staging
4. Merge observability integration to TTA.dev

### Week 2 (Nov 11-15)
1. Complete workflow escalation implementation
2. Fix Gameplay Loop quality issues
3. Fix Model Management quality issues
4. Update pyproject.toml dependencies

### Week 3 (Nov 18-22)
1. Update all documentation
2. Create component promotion PRs
3. Formalize TTA.dev dependency management
4. Complete repository reorganization

---

**Last Updated**: 2025-10-29
**Maintainer**: Repository reorganization team
**Review Frequency**: Weekly during active reorganization
