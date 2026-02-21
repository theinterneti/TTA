# Next Test Generation Targets - Phase 2

**Date:** 2025-10-25
**Status:** 📋 **PLANNING PHASE**

## Overview

This document identifies high-priority modules for test generation in Phase 2, following the successful integration of generated tests for protocol_bridge, capability_matcher, and circuit_breaker in Phase 1.

## Selection Criteria

Modules selected based on:
1. **File Size:** Under 500 lines (manageable for test generation)
2. **Coverage:** Low or zero existing test coverage
3. **Importance:** Critical to system functionality
4. **API Clarity:** Well-documented, clear interfaces
5. **Dependencies:** Minimal external dependencies

## Recommended Phase 2 Targets

### Tier 1: High Priority (Immediate)

#### 1. **adapters.py** (419 lines)
- **Importance:** ⭐⭐⭐⭐⭐ Critical - Bridges orchestration with real agents
- **Current Coverage:** ~0% (no dedicated tests)
- **Key Classes:**
  - `IPAAdapter` - Input processor agent communication
  - `WBAAdapter` - World builder agent communication
  - `NGAAdapter` - Narrative generator agent communication
  - `AgentAdapterFactory` - Factory pattern for adapter creation
- **Test Focus:**
  - Adapter initialization and configuration
  - Message processing and routing
  - Error handling and fallback mechanisms
  - Retry logic and resilience
- **Estimated Tests:** 25-30
- **Estimated Generation Time:** 10-15 minutes

#### 2. **models.py** (338 lines)
- **Importance:** ⭐⭐⭐⭐⭐ Critical - Core data models
- **Current Coverage:** ~5% (minimal tests)
- **Key Classes:**
  - `AgentType` - Enum for agent types
  - `MessageType` - Enum for message types
  - `AgentId` - Agent identification model
  - `AgentMessage` - Core message model
  - `OrchestrationRequest/Response` - Request/response models
  - `CapabilityMatchCriteria` - Capability matching criteria
- **Test Focus:**
  - Model validation and constraints
  - Enum values and behavior
  - Field validation (min_length, defaults)
  - Serialization/deserialization
- **Estimated Tests:** 20-25
- **Estimated Generation Time:** 8-12 minutes

#### 3. **messaging.py** (48 lines)
- **Importance:** ⭐⭐⭐⭐ High - Message passing infrastructure
- **Current Coverage:** ~0% (no tests)
- **Key Classes:**
  - `MessageResult` - Message delivery result
  - `MessageSubscription` - Subscription model
  - `FailureType` - Enum for failure types
  - `QueueMessage` - Queue message wrapper
  - `ReceivedMessage` - Received message wrapper
- **Test Focus:**
  - Model creation and validation
  - Enum values
  - Field defaults and constraints
- **Estimated Tests:** 12-15
- **Estimated Generation Time:** 5-8 minutes

### Tier 2: Medium Priority (Phase 2b)

#### 4. **router.py** (304 lines)
- **Importance:** ⭐⭐⭐⭐ High - Message routing logic
- **Current Coverage:** ~10%
- **Key Classes:** Message routing and dispatch
- **Estimated Tests:** 20-25

#### 5. **state_validator.py** (284 lines)
- **Importance:** ⭐⭐⭐⭐ High - State validation
- **Current Coverage:** ~15%
- **Key Classes:** State validation and repair
- **Estimated Tests:** 18-22

#### 6. **workflow_monitor.py** (316 lines)
- **Importance:** ⭐⭐⭐ Medium - Workflow monitoring
- **Current Coverage:** ~5%
- **Key Classes:** Workflow monitoring and metrics
- **Estimated Tests:** 15-20

## Phase 2 Implementation Plan

### Week 1: Tier 1 Modules

**Day 1-2: adapters.py**
```bash
# Generate tests for adapters
uv run python scripts/execute_test_generation.py \
  --module adapters \
  --coverage-threshold 70.0
```

**Day 3: models.py**
```bash
# Generate tests for models
uv run python scripts/execute_test_generation.py \
  --module models \
  --coverage-threshold 70.0
```

**Day 4: messaging.py**
```bash
# Generate tests for messaging
uv run python scripts/execute_test_generation.py \
  --module messaging \
  --coverage-threshold 70.0
```

**Day 5: Integration & Verification**
- Run all generated tests
- Verify coverage thresholds met
- Update CI/CD workflow if needed
- Create summary report

### Expected Outcomes

**Total Tests Generated:** 57-70 tests
**Total Coverage Improvement:** +15-20% for agent_orchestration
**Estimated Time:** 2-3 hours (generation + verification)
**Cost:** ~$0.05-0.10 (OpenRouter API)

## Execution Workflow

### Step 1: Generate Tests
```bash
# Using the documented workflow from TEST_GENERATION_WORKFLOW.md
uv run python scripts/execute_test_generation.py \
  --module <module_name> \
  --coverage-threshold 70.0 \
  --max-iterations 3
```

### Step 2: Verify Tests
```bash
# Run generated tests
uv run pytest tests/agent_orchestration/test_<module_name>.py -v

# Check coverage
uv run pytest tests/agent_orchestration/test_<module_name>.py \
  --cov=src/agent_orchestration/<module_name> \
  --cov-report=term
```

### Step 3: Fix Failures
- Review test failures
- Update tests or module code as needed
- Re-run until all tests pass

### Step 4: Integrate into CI/CD
- Update `.github/workflows/tests.yml` if needed
- Commit changes
- Verify workflow runs successfully

## Success Criteria

✅ All generated tests pass (100% pass rate)
✅ Coverage ≥70% for each module
✅ Tests follow TTA conventions
✅ CI/CD integration successful
✅ Documentation updated

## Risk Mitigation

**Risk:** API mismatches in generated tests
- **Mitigation:** Review generated tests before committing
- **Fallback:** Manually fix tests or regenerate with updated specs

**Risk:** Rate limiting on OpenRouter API
- **Mitigation:** Use fallback models from registry
- **Fallback:** Stagger generation across multiple days

**Risk:** Test generation timeout
- **Mitigation:** Set max_iterations=3 for faster generation
- **Fallback:** Manually write critical tests

## Next Steps

1. ✅ Commit Phase 1 changes (DONE)
2. ⏳ Generate tests for adapters.py (NEXT)
3. ⏳ Generate tests for models.py
4. ⏳ Generate tests for messaging.py
5. ⏳ Integrate into CI/CD
6. ⏳ Create Phase 2 completion report

## Related Documentation

- **Test Generation Workflow:** `docs/testing/TEST_GENERATION_WORKFLOW.md`
- **Generated Tests Summary:** `docs/testing/GENERATED_TESTS_SUMMARY.md`
- **Phase 1 Completion:** `CI_CD_INTEGRATION_COMPLETE.md`


---
**Logseq:** [[TTA.dev/Docs/Development/Test-targets]]
