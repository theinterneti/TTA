# Testing Infrastructure Backlog

This document tracks the remaining testing improvement work identified during
the March 2026 testing audit. Each section corresponds to a GitHub issue.

---

## Issue 1: Migrate 65 root-level test files into proper subdirectories

**Labels:** `testing`, `refactoring`, `good first issue`  
**Priority:** High

### Problem
65 files in `tests/test_*.py` (~989 test functions) sit at the root of the tests
directory with no consistent structure. This means:
- They're NOT run by the fast unit test CI job (which only scans `tests/unit/`)
- They're collected by the integration test CI job even if they don't need services
- Locally, `pytest tests/` includes them in every run, adding minutes of overhead
- New contributors have no idea where to add tests

### Details
- ~51 files are unit-test eligible (no Redis/Neo4j/Docker deps)
- ~14 files need external services (Docker, Neo4j, Redis)
- ~7 of these files are already guarded with `pytest.importorskip` for tta_ai/tta_narrative

### Acceptance Criteria
- [ ] All unit-eligible files moved to `tests/unit/` with appropriate subdirectory
- [ ] All service-dependent files moved to `tests/integration/` with proper markers
- [ ] Docker-dependent tests get `@pytest.mark.docker` (new marker, added to `pyproject.toml`)
- [ ] `tests/test_*.py` root directory is empty (only `conftest.py` at root)
- [ ] CI unit test command continues to pass after migration
- [ ] No test is lost (same count passes)

### Files needing migration
Unit-eligible (move to `tests/unit/`):
```
test_adapters_generated_sample.py, test_api_integration.py, test_api_structure.py,
test_character_avatar_manager.py, test_character_management_api.py,
test_cli_admin_recover.py, test_compatibility_checker.py, test_component_loader.py,
test_component_registry.py, test_end_to_end_workflows.py, test_enhanced_authentication.py,
test_free_models_filter.py, test_metrics_endpoint.py, test_model_management.py,
test_narrative_coherence_engine.py, test_orchestrator.py, test_orchestrator_component_lifecycle.py,
test_orchestrator_config.py, test_orchestrator_decorators.py, test_orchestrator_lifecycle_validation.py,
test_orchestrator_topo_sort.py, test_personalization_service_manager.py,
test_player_experience_manager.py, test_player_experience_models.py,
test_player_management_api.py, test_player_profile_database.py,
test_player_profile_database_param.py, test_player_profile_manager.py,
test_privacy_api.py, test_privacy_service.py, test_process_utils.py,
test_progress_tracking_highlights.py, test_progress_tracking_service.py,
test_progress_viz_endpoint.py, test_session_integration_manager_simple.py,
test_session_management.py, test_session_narrative_integration.py,
test_therapeutic_effectiveness_integration.py, test_therapeutic_profile_integration.py,
test_therapeutic_settings.py, test_websocket_chat_backend.py,
test_websocket_chat_backend_task8_2.py, test_websocket_chat_interactive.py,
test_websocket_chat_typing_and_metrics.py, test_world_management_api.py,
test_world_management_module.py, test_scale_manager_coverage.py,
test_scale_manager_extraction.py, test_causal_graph_coverage.py,
test_impact_analysis_coverage.py, test_wave3_facades.py
```

Integration-eligible (move to `tests/integration/`):
```
test_components_legacy.py, test_config.py, test_docker_component_enhanced.py,
test_neo4j_component.py, test_neo4j_component_enhanced.py, test_orchestrator.py,
test_orchestrator_config.py, test_orchestrator_docker.py,
test_player_experience_component_integration.py, test_player_experience_orchestration_integration.py,
test_comprehensive_integration.py, test_orchestration_integration.py,
test_redis_integration.py, test_session_repository_redis_integration.py
```

---

## Issue 2: Replace asyncio.sleep() polling in tests with event-driven patterns

**Labels:** `testing`, `performance`, `slow-tests`  
**Priority:** Medium

### Problem
24 occurrences of `asyncio.sleep(>=2s)` in test files cause tests to spend real
wall-clock time waiting rather than testing logic. Key offenders:

| File | Sleep calls | Approx. added wait |
|------|-------------|-------------------|
| `tests/agent_orchestration/test_capability_system_integration.py` | 8× (1-2s each) | ~12s |
| `tests/agent_orchestration/test_websocket_performance.py` | 12× | ~15s |
| `tests/agent_orchestration/test_websocket_error_recovery.py` | 6× | ~8s |
| `tests/unit/test_session_cleanup_task.py` | 9× | ~5s |

### Fix Pattern
Replace `await asyncio.sleep(N)` polling with condition-based waiting:
```python
# Before (slow):
await asyncio.sleep(2.0)
assert something_happened

# After (fast):
async def wait_for_condition(check_fn, timeout=2.0, interval=0.05):
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        if check_fn():
            return
        await asyncio.sleep(interval)
    raise TimeoutError("condition not met")

await wait_for_condition(lambda: something_happened)
```

### Acceptance Criteria
- [ ] All `asyncio.sleep(>=1s)` in `tests/unit/` replaced with event-driven waits
- [ ] `tests/agent_orchestration/test_capability_system_integration.py` fixed
- [ ] `tests/agent_orchestration/test_websocket_*` fixed
- [ ] Unit test suite completes in <3 minutes locally (currently ~2m 20s in CI)
- [ ] No test behavior changes — only timing mechanism changes

---

## Issue 3: Audit and delete dead/low-value tests

**Labels:** `testing`, `cleanup`  
**Priority:** Medium

### Problem
Several test files appear to be low-value or testing deprecated code paths:

1. **`test_websocket_chat_backend_task8_2.py`** — name suggests a task-specific generated
   test, likely no longer relevant
2. **`test_wave3_facades.py`** — 77% of asserts are `assert X is not None` or import
   existence checks with no behavioral validation
3. **`test_adapters_generated_sample.py`** — generated by OpenHands as a "sample",
   docstring says "Coverage Target: 70%, Quality Score: 82/100"
4. **`tests/comprehensive_battery/`** — 24 files, 0 pytest functions; this is a custom
   test orchestration framework that never runs in pytest. Should either be converted
   to real pytest tests or moved out of the `tests/` directory entirely.
5. **`tests/agent_orchestration/validate_integration_tests.py`** — file name suggests
   a validation script, not a test file

### Acceptance Criteria
- [ ] Each flagged test reviewed: keep, rewrite, or delete decision documented
- [ ] `tests/comprehensive_battery/` either converted to pytest or moved to `scripts/`
- [ ] Any deleted tests have their coverage covered by better tests elsewhere
- [ ] Test count reduced with no loss of actual behavior coverage

---

## Issue 4: Fix npm audit high-severity vulnerabilities in frontend

**Labels:** `security`, `frontend`, `dependencies`  
**Priority:** High

### Problem
`npm audit` reports 16 high-severity vulnerabilities in
`src/player_experience/frontend/`. The Security Scan CI step currently has
`continue-on-error: true` to avoid blocking the PR, but these are real
security issues that need resolution.

Run `npm audit` in `src/player_experience/frontend/` to see the current list.

### Acceptance Criteria
- [ ] `npm audit --audit-level=high` returns 0 findings
- [ ] All Storybook and other dev dependencies updated to patched versions
- [ ] `continue-on-error: true` removed from "Fail on high-severity vulnerabilities"
  step in `security-scan.yml` (line ~157)
- [ ] Package lock file updated and committed

### Notes
Many of the vulnerabilities are likely in dev/Storybook dependencies (not
production code). These can be fixed with `npm audit fix --only=dev` or by
upgrading Storybook to a newer major version.

---

## Issue 5: Add `@pytest.mark.slow` enforcement for load/performance tests

**Labels:** `testing`, `ci`, `performance`  
**Priority:** Low

### Problem
Load and performance tests in `tests/agent_orchestration/test_*_performance.py`
and `tests/agent_orchestration/test_websocket_performance.py` are not consistently
marked with `@pytest.mark.slow`. They run in the integration test CI job and
can take 5-15 minutes per file.

### Acceptance Criteria
- [ ] All files in `tests/performance/` and all `test_*_performance.py`,
  `test_*_load*.py` files have `@pytest.mark.slow` on the class or individual tests
- [ ] Integration test CI command excludes `@pytest.mark.slow` unless
  `--run-slow` flag is passed (or a separate CI job)
- [ ] `pyproject.toml` markers section documents `slow: Long-running tests (>10s)`
- [ ] Local dev docs updated with how to run slow tests explicitly

---

## Summary Table

| Issue | Priority | Estimated Effort | Impact |
|-------|----------|-----------------|--------|
| Migrate 65 root-level test files | High | 2-4h | Tests fully organized, CI integration job faster |
| Replace asyncio.sleep polling | Medium | 2-3h | Faster local test runs |
| Audit and delete dead tests | Medium | 1-2h | Reduced noise, faster collection |
| Fix npm audit high-severity vulns | High | 2-4h | Security compliance |
| Add @pytest.mark.slow enforcement | Low | 1h | More granular CI control |
