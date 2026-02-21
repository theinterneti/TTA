# OpenHands Test Generation Plan

**Date:** October 26, 2025
**Status:** Ready for Execution
**Total Modules:** 58 Python modules identified for test generation

---

## Overview

This document outlines the comprehensive test generation plan using the validated OpenHands Docker integration. Tests will be generated in three batches based on module complexity.

---

## Module Inventory

### Batch 1: Small Modules (<50 lines) - 13 modules

| Lines | Module | Priority |
|-------|--------|----------|
| 8 | src/monitoring/metrics_collector.py | 1 |
| 18 | src/agent_orchestration/validators.py | 2 |
| 19 | src/monitoring/performance_monitor.py | 3 |
| 23 | src/monitoring/logging_config.py | 4 |
| 26 | src/player_experience/api/main.py | 5 |
| 30 | src/components/narrative_arc_orchestrator/resolution_engine.py | 6 |
| 31 | src/components/narrative_coherence/rules.py | 7 |
| 32 | src/components/narrative_arc_orchestrator/causal_graph.py | 8 |
| 39 | src/agent_orchestration/state.py | 9 |
| 39 | src/player_experience/monitoring/alerting.py | 10 |
| 40 | src/components/narrative_arc_orchestrator/conflict_detection.py | 11 |
| 45 | src/player_experience/api/routers/progress.py | 12 |
| 48 | src/agent_orchestration/messaging.py | 13 |

**Estimated Cost:** $0.30-0.50
**Estimated Time:** 50-75 seconds per module (10-15 minutes total)

---

### Batch 2: Medium Modules (50-150 lines) - 18 modules

| Lines | Module |
|-------|--------|
| 52 | src/agent_orchestration/workflow.py |
| 53 | src/common/time_utils.py |
| 57 | src/agent_orchestration/admin/recover.py |
| 59 | src/agent_orchestration/tools/callable_registry.py |
| 70 | src/player_experience/models/enums.py |
| 75 | src/player_experience/utils/normalization.py |
| 80 | src/agent_orchestration/metrics.py |
| 81 | src/agent_orchestration/interfaces.py |
| 87 | src/agent_orchestration/openhands_integration/models.py |
| 88 | src/agent_orchestration/performance/step_aggregator.py |
| 89 | src/player_experience/api/routers/metrics.py |
| 107 | src/agent_orchestration/langgraph_integration.py |
| 112 | src/components/narrative_arc_orchestrator/models.py |
| 113 | src/player_experience/api/test_containerized.py |
| 114 | src/agent_orchestration/tools/coordinator.py |
| 125 | src/common/process_utils.py |
| 138 | src/player_experience/api/routers/sessions.py |
| 149 | src/player_experience/frontend/node_modules/flatted/python/flatted.py |

**Estimated Cost:** $0.90-1.50
**Estimated Time:** 75-120 seconds per module (25-35 minutes total)

---

### Batch 3: Large Modules (>150 lines) - 27 modules

| Lines | Module |
|-------|--------|
| 154 | src/agent_orchestration/workflow_transaction.py |
| 155 | src/agent_orchestration/openhands_integration/test_generation_models.py |
| 159 | src/agent_orchestration/tools/invocation_service.py |
| 161 | src/agent_orchestration/tools/metrics.py |
| 161 | src/agent_orchestration/tools/policy_config.py |
| 162 | src/components/narrative_coherence/models.py |
| 163 | src/player_experience/models/player.py |
| 164 | src/agent_orchestration/tools/models.py |
| 165 | src/components/narrative_arc_orchestrator/impact_analysis.py |
| 171 | src/player_experience/utils/validation.py |
| 185 | src/agent_orchestration/config/real_agent_config.py |
| 188 | src/player_experience/api/test_sentry_integration.py |
| 188 | src/player_experience/managers/player_experience_manager.py |
| 197 | src/agent_orchestration/openhands_integration/test_task_builder.py |
| 202 | src/player_experience/api/config.py |
| 212 | src/player_experience/models/character.py |
| 222 | src/agent_orchestration/tools/redis_tool_registry.py |
| 222 | src/components/gameplay_loop/models/validation.py |
| 225 | src/components/app_component.py |
| 228 | src/agent_orchestration/openhands_integration/test_file_extractor.py |
| 231 | src/agent_orchestration/openhands_integration/retry_policy.py |
| 231 | src/player_experience/api/routers/health.py |
| 234 | src/player_experience/models/session.py |
| 235 | src/orchestration/decorators.py |
| 236 | src/agent_orchestration/openhands_integration/metrics_collector.py |

**Estimated Cost:** $2.00-3.50
**Estimated Time:** 120-180 seconds per module (50-75 minutes total)

---

## Execution Strategy

### Phase 1: Small Modules (Batch 1)
- **Duration:** 10-15 minutes
- **Cost:** $0.30-0.50
- **Objective:** Validate end-to-end workflow with simple modules
- **Success Criteria:** All 13 modules have passing tests with >80% coverage

### Phase 2: Medium Modules (Batch 2)
- **Duration:** 25-35 minutes
- **Cost:** $0.90-1.50
- **Objective:** Generate tests for moderately complex modules
- **Success Criteria:** All 18 modules have passing tests with >80% coverage

### Phase 3: Large Modules (Batch 3)
- **Duration:** 50-75 minutes
- **Cost:** $2.00-3.50
- **Objective:** Generate tests for complex modules
- **Success Criteria:** All 27 modules have passing tests with >80% coverage

---

## Total Estimates

| Metric | Value |
|--------|-------|
| Total Modules | 58 |
| Total Estimated Time | 85-125 minutes (~2 hours) |
| Total Estimated Cost | $3.20-5.50 |
| Average Cost per Module | $0.05-0.10 |
| Average Time per Module | 90-130 seconds |

---

## Test Generation Template

For each module, OpenHands will:

1. **Analyze** the module's functionality and dependencies
2. **Generate** comprehensive unit tests with:
   - Test coverage >80%
   - pytest framework
   - Edge cases and error handling
   - Docstrings for all test functions
3. **Save** tests to `tests/` directory (mirroring source structure)
4. **Validate** tests run successfully with pytest
5. **Report** execution time and coverage metrics

---

## Success Criteria

✅ All 58 modules have generated tests
✅ All tests are syntactically correct
✅ All tests pass with pytest
✅ Coverage >80% for each module
✅ Total execution time <2.5 hours
✅ Total cost <$6.00

---

## Next Steps

1. Execute Batch 1 (Small Modules)
2. Validate results and adjust if needed
3. Execute Batch 2 (Medium Modules)
4. Execute Batch 3 (Large Modules)
5. Validate all tests and generate final report
6. Integrate tests into CI/CD pipeline


---
**Logseq:** [[TTA.dev/Docs/Test_generation_plan]]
