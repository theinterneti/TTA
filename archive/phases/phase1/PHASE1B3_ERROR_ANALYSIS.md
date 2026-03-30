# Phase 1B.3: Code Cleanup - Error Analysis

**Date:** 2025-10-02
**Total Errors:** 126 (F841: ~89, B007: ~37)

---

## 📊 Error Breakdown

### By Type

| Error Code | Description | Count | Priority |
|------------|-------------|-------|----------|
| **F841** | Local variable assigned but never used | ~89 | HIGH |
| **B007** | Loop control variable not used within loop body | ~37 | MEDIUM |

### By Category

**Tests (60 errors - 48%):**
- Safer to modify
- Less risk of breaking functionality
- Good starting point

**Source (66 errors - 52%):**
- Requires careful review
- May have intentional unused variables
- Higher risk

---

## 🎯 Batching Strategy

### Batch 1: Test Files - High Volume (30 errors)
**Files:**
- `tests/comprehensive_battery/test_suites/load_stress_test_suite.py` (5 errors)
- `tests/agent_orchestration/test_real_agent_performance.py` (5 errors)
- `tests/test_privacy_api.py` (4 errors)
- `tests/agent_orchestration/test_websocket_real_agent_integration.py` (4 errors)
- `tests/agent_orchestration/test_performance_concurrency.py` (4 errors)
- `tests/integration/test_phase2a_integration.py` (3 errors)
- `tests/agent_orchestration/test_workflow_chain_validation.py` (3 errors)
- `tests/test_player_profile_manager.py` (2 errors)

### Batch 2: Test Files - Medium Volume (20 errors)
**Files:**
- `tests/comprehensive_battery/containers/enhanced_service_manager.py` (2 errors)
- `tests/agent_orchestration/test_websocket_performance.py` (2 errors)
- `tests/agent_orchestration/test_therapeutic_content_validation.py` (2 errors)
- `tests/agent_orchestration/test_session_state_validation.py` (2 errors)
- `tests/agent_orchestration/test_performance_validation.py` (2 errors)
- `tests/agent_orchestration/test_end_to_end_validation.py` (2 errors)
- `tests/agent_orchestration/test_crisis_intervention_system.py` (2 errors)
- `tests/agent_orchestration/test_crisis_detection_scenarios.py` (2 errors)
- `tests/agent_orchestration/test_circuit_breaker_integration.py` (2 errors)
- `tests/agent_orchestration/test_agent_orchestration_service_integration.py` (2 errors)

### Batch 3: Test Files - Low Volume (10 errors)
**Files:**
- Single-error test files (10 files with 1 error each)

### Batch 4: Source - Player Experience (10 errors)
**Files:**
- `src/player_experience/api/routers/players.py` (4 errors)
- `src/player_experience/managers/progress_tracking_service.py` (3 errors)
- `src/player_experience/services/gameplay_service.py` (1 error)
- `src/player_experience/managers/therapeutic_profile_integration.py` (1 error)
- `src/player_experience/database/character_repository.py` (1 error)

### Batch 5: Source - Components (16 errors)
**Files:**
- `src/components/narrative_arc_orchestrator/scale_manager.py` (4 errors)
- `src/components/gameplay_loop/choice_architecture/agency_protector.py` (3 errors)
- `src/components/character_arc_manager.py` (3 errors)
- `src/components/agent_orchestration_component.py` (3 errors)
- Others (3 errors total)

### Batch 6: Source - Agent Orchestration (20 errors)
**Files:**
- `src/agent_orchestration/tools/invocation_service.py` (3 errors)
- `src/agent_orchestration/protocol_bridge.py` (3 errors)
- `src/agent_orchestration/optimization/optimization_engine.py` (3 errors)
- `src/agent_orchestration/realtime/dashboard.py` (2 errors)
- `src/agent_orchestration/profiling.py` (2 errors)
- `src/agent_orchestration/performance/optimization.py` (2 errors)
- Others (5 errors total)

---

## 🔍 Common Patterns

### F841 Patterns

1. **Debugging Variables** - Variables assigned for debugging but not used
   ```python
   result = some_function()  # F841 - result never used
   ```

2. **Unpacking Remnants** - Variables from tuple unpacking not used
   ```python
   x, y, z = get_coords()  # F841 - z never used
   ```

3. **API Call Side Effects** - Variables assigned from API calls for side effects
   ```python
   response = api.call()  # F841 - call needed but response unused
   ```

4. **Loop Accumulation** - Variables that accumulate but final value unused
   ```python
   total = 0
   for item in items:
       total += item.value  # F841 - total never used after loop
   ```

### B007 Patterns

1. **Iteration for Side Effects** - Looping just to execute body
   ```python
   for item in items:  # B007 - item not used
       do_something()
   ```

2. **Dictionary Iteration** - Iterating over keys/values but not using them
   ```python
   for key in dict:  # B007 - key not used
       process(dict[key])
   ```

3. **Range Iteration** - Using range() but not the counter
   ```python
   for i in range(10):  # B007 - i not used
       do_something()
   ```

---

## ✅ Fix Strategies

### For F841 (Unused Variables)

**Strategy 1: Remove if truly unused**
```python
# Before
result = some_function()
do_something_else()

# After
some_function()
do_something_else()
```

**Strategy 2: Prefix with `_` if intentional**
```python
# Before
result = api_call()  # F841 but call needed for side effect

# After
_result = api_call()  # Indicates intentionally unused
```

**Strategy 3: Use in unpacking**
```python
# Before
x, y, z = get_coords()  # F841 - z never used

# After
x, y, _ = get_coords()  # Use _ for unused values
```

### For B007 (Unused Loop Variables)

**Strategy 1: Replace with `_`**
```python
# Before
for item in items:  # B007
    do_something()

# After
for _ in items:
    do_something()
```

**Strategy 2: Use the variable**
```python
# Before
for key in dict:  # B007
    process(dict[key])

# After
for key in dict:
    process(key)  # Or use dict.values() if key not needed
```

---

## ⚠️ Caution Areas

### DO NOT Remove

1. **API Contract Variables** - Required by framework/library signatures
2. **Future Use Variables** - Marked with TODO/FIXME comments
3. **Side Effect Variables** - Assignments that trigger important side effects
4. **Debugging Variables** - In development/testing code

### Verify Before Removing

1. **Exception Handling** - Variables in except blocks may be needed
2. **Context Managers** - Variables from `with` statements
3. **Unpacking** - May need to maintain tuple structure
4. **Loop Variables** - May be used in nested scopes

---

## 📝 Review Checklist

For each unused variable:
- [ ] Check if used in comments/docstrings
- [ ] Check if part of unpacking that needs other values
- [ ] Check if assigned from API calls (side effects)
- [ ] Check if used in exception handling
- [ ] Check if used in nested scopes
- [ ] Check if marked with TODO/FIXME
- [ ] Check if required by API contract
- [ ] Run tests after removal

---

## 🎯 Success Criteria

- [ ] All F841 errors resolved or justified
- [ ] All B007 errors resolved or justified
- [ ] Format Check continues to pass
- [ ] All tests continue to pass
- [ ] No functionality broken
- [ ] Code remains readable and maintainable

---

**Estimated Time:** 2-3 hours (manual review)
**Batches:** 6 batches
**Files:** ~70 files


---
**Logseq:** [[TTA.dev/Archive/Phases/Phase1/Phase1b3_error_analysis]]
