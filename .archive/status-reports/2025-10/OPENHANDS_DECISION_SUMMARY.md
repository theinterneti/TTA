# OpenHands Integration - Decision Summary & Action Items

**Date:** 2025-10-27
**Status:** ✅ Investigation Complete, Decision Made, Actions Defined
**Decision:** Postpone OpenHands, Enhance Direct LLM Approach

---

## 🎯 Executive Decision

**We are POSTPONING (not abandoning) the OpenHands integration** due to critical upstream bugs, while implementing an enhanced direct LLM code generation approach that leverages TTA's existing Model Management Component.

---

## 📋 Quick Reference

### What We Keep

✅ **All OpenHands integration code** (28 files, 8,388 lines)
- Location: `src/agent_orchestration/openhands_integration/`
- Status: Ready for future activation when bugs are fixed
- Maintenance: Minimal (code is stable, no active development)

### What We Build

✅ **Enhanced Direct LLM Code Generation Tool**
- Integration with TTA Model Management Component
- Streaming support for better UX
- Context injection from existing codebase
- Iterative refinement with quality gates
- TTA-specific prompt library

### What We Monitor

⏸️ **OpenHands Releases** (Monthly check)
- GitHub issue #8630 for condensation bug fix
- New releases for bug fixes
- Re-evaluate when version 0.60+ available

---

## 🔧 Specific Action Items

### 1. Repository Organization (Immediate - 1 hour)

**Task:** Mark OpenHands integration as postponed

**Actions:**
```bash
# Add postponement marker to OpenHands integration
cat > src/agent_orchestration/openhands_integration/POSTPONED.md << 'EOF'
# OpenHands Integration - POSTPONED

**Status:** ⏸️ Postponed due to upstream bugs
**Date:** 2025-10-27
**Decision:** See docs/decisions/ADR-001-OPENHANDS-INTEGRATION-POSTPONEMENT.md

## Why Postponed

OpenHands 0.59 has a critical condensation loop bug (GitHub Issue #8630) that prevents
any task execution. The bug has existed since version 0.39 and is unresolved in current
releases up to 1.0.2-cli.

## Infrastructure Status

✅ All 28 files present and functional
✅ Docker client initializes correctly
✅ Configuration loads from environment
✅ Ready for immediate activation when bugs are fixed

## Alternative

Use `scripts/direct_llm_code_generation.py` for code generation needs.

## Re-evaluation

Check monthly for OpenHands bug fixes. Re-activate when version 0.60+ is released
with condensation bug fix.

## References

- Investigation: OPENHANDS_CONDENSATION_BUG_INVESTIGATION.md
- Decision: docs/decisions/ADR-001-OPENHANDS-INTEGRATION-POSTPONEMENT.md
- Strategy: docs/decisions/OPENHANDS-STRATEGIC-RECOMMENDATIONS.md
EOF

# Update __init__.py with postponement comment
sed -i '1i# POSTPONED: See POSTPONED.md and docs/decisions/ADR-001-OPENHANDS-INTEGRATION-POSTPONEMENT.md\n' \
    src/agent_orchestration/openhands_integration/__init__.py
```

**Deliverable:** Clear postponement markers in OpenHands integration directory

---

### 2. Enhance Direct LLM Tool (Sprint 1 - Week 1-2)

**Task:** Integrate with TTA Model Management Component

**Current File:** `scripts/direct_llm_code_generation.py`

**New File:** `src/agent_orchestration/code_generation/llm_code_generator.py`

**Key Changes:**

```python
# BEFORE (current - direct httpx)
from httpx import AsyncClient

client = AsyncClient()
response = await client.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json=payload
)

# AFTER (recommended - TTA Model Management)
from tta_ai.models import ModelManagementComponent

model_manager = ModelManagementComponent(config)
await model_manager.start()

model = await model_manager.select_model(
    task_type="code_generation",
    requirements={"max_latency_ms": 10000, "prefer_free": True}
)

response = await model.generate(prompt)
```

**Benefits:**
- ✅ Automatic model selection and fallback
- ✅ Cost tracking and limits
- ✅ Performance monitoring
- ✅ Consistent with TTA architecture

**Effort:** 2-3 days

**Deliverable:** `src/agent_orchestration/code_generation/llm_code_generator.py`

---

### 3. Add Streaming Support (Sprint 1 - Week 1-2)

**Task:** Implement streaming responses for better UX

**Implementation:**

```python
async def generate_code_streaming(
    task_description: str,
    output_file: Path
) -> AsyncIterator[str]:
    """Generate code with streaming responses."""

    prompt = build_prompt(task_description)

    complete_response = ""
    async for chunk in model.generate_stream(prompt):
        complete_response += chunk
        yield chunk  # Stream to user

    # Save complete response
    output_file.write_text(complete_response)
```

**Effort:** 1-2 days

**Deliverable:** Streaming support in code generator

---

### 4. Create Prompt Library (Sprint 2 - Week 3-4)

**Task:** Build TTA-specific prompt templates

**Location:** `src/agent_orchestration/code_generation/prompts/`

**Initial Templates:**

1. `circuit_breaker.py` - Circuit breaker implementation
2. `redis_integration.py` - Redis connection and operations
3. `neo4j_integration.py` - Neo4j graph operations
4. `fastapi_endpoint.py` - API endpoint creation
5. `agent_orchestration.py` - Agent communication patterns
6. `error_recovery.py` - Error handling and retry logic
7. `unit_tests.py` - Unit test generation
8. `integration_tests.py` - Integration test generation
9. `data_validation.py` - Data validation classes
10. `async_utilities.py` - Async utility functions

**Example Template:**

```python
# prompts/circuit_breaker.py

CIRCUIT_BREAKER_PROMPT = """Create a circuit breaker implementation for TTA.

REQUIREMENTS:
- Use Redis for state persistence
- Support CLOSED, OPEN, HALF_OPEN states
- Configurable failure threshold and recovery timeout
- Async/await support
- Type hints and docstrings
- Comprehensive error handling

REFERENCE:
See src/agent_orchestration/circuit_breaker.py for existing implementation.

INTEGRATION:
- Must work with TTA's agent orchestration
- Use RedisMessageCoordinator for state storage
- Follow component maturity workflow (≥70% coverage, ≥75% mutation score)

Generate production-quality code:"""
```

**Effort:** 2-3 days (initial library)

**Deliverable:** 10+ prompt templates in `prompts/` directory

---

### 5. Implement Context Injection (Sprint 2 - Week 3-4)

**Task:** Inject TTA codebase context into prompts

**Implementation:**

```python
def build_prompt_with_context(
    task_description: str,
    context_type: str = "agent_orchestration"
) -> str:
    """Build prompt with TTA-specific context."""

    # Load relevant code examples
    examples = {
        "agent_orchestration": load_file("src/agent_orchestration/circuit_breaker.py"),
        "redis": load_file("src/common/redis_coordinator.py"),
        "neo4j": load_file("src/common/neo4j_client.py"),
    }

    # Load architectural patterns
    patterns = load_file("AGENTS.md")  # TTA architectural guidelines

    prompt = f"""You are an expert Python developer working on the TTA project.

TASK:
{task_description}

TTA ARCHITECTURAL PATTERNS:
{patterns}

RELEVANT CODE EXAMPLES:
{examples.get(context_type, "")}

REQUIREMENTS:
- Follow TTA component maturity workflow
- Use circuit breakers for external calls
- Implement retry logic with exponential backoff
- Add comprehensive docstrings and type hints
- Include error handling and logging
- Follow SOLID principles
- File size limit: 300-400 lines (soft), 1,000 lines (hard)

Generate production-quality code:"""

    return prompt
```

**Effort:** 3-4 days

**Deliverable:** Context injection in code generator

---

### 6. Add Iterative Refinement (Sprint 2 - Week 3-4)

**Task:** Implement multi-turn refinement loop

**Implementation:**

```python
async def generate_with_refinement(
    task_description: str,
    max_iterations: int = 3
) -> dict:
    """Generate code with iterative refinement."""

    # Initial generation
    code = await generate_code(task_description)

    for iteration in range(max_iterations):
        # Validate against quality gates
        validation = validate_code(code)

        if validation.passed:
            break

        # Refine based on feedback
        refinement_prompt = f"""The generated code has the following issues:
{validation.issues}

Please fix these issues while maintaining the original functionality:
{code}"""

        code = await generate_code(refinement_prompt)

    # Generate tests
    tests = await generate_tests(code)

    return {"code": code, "tests": tests, "iterations": iteration + 1}
```

**Effort:** 4-5 days

**Deliverable:** Iterative refinement in code generator

---

### 7. Documentation (Sprint 3 - Week 5-6)

**Task:** Create comprehensive documentation

**Files to Create:**

1. `docs/development/CODE_GENERATION_GUIDE.md` - Developer guide
2. `src/agent_orchestration/code_generation/README.md` - Component README
3. `src/agent_orchestration/code_generation/prompts/README.md` - Prompt library guide

**Content:**
- How to use code generation tool
- Available prompt templates
- Best practices for prompts
- Quality gate requirements
- Examples and tutorials

**Effort:** 2-3 days

**Deliverable:** Complete documentation for code generation workflow

---

### 8. OpenHands Monitoring (Ongoing - Monthly)

**Task:** Monitor OpenHands releases for bug fixes

**Schedule:** First Monday of each month

**Checklist:**
1. Check GitHub issue #8630 for updates
2. Review OpenHands releases page
3. Test new versions if condensation bug fix mentioned
4. Update ADR-001 with findings

**Re-evaluation Criteria:**
- Version 0.60+ with condensation bug fix
- Successful test of file generation
- Stable release with no critical bugs
- Community validation (2+ weeks)

**Effort:** 1 hour/month

**Deliverable:** Monthly status update in ADR-001

---

## 📊 Success Metrics

### Sprint 1 (Week 1-2)

- ✅ Direct LLM tool integrated with Model Management Component
- ✅ Streaming support implemented
- ✅ 5+ components generated using enhanced tool

### Sprint 2 (Week 3-4)

- ✅ Context injection implemented
- ✅ Prompt library with 10+ templates
- ✅ Iterative refinement working
- ✅ 10+ components generated

### Sprint 3 (Week 5-6)

- ✅ Complete documentation
- ✅ Team trained on code generation workflow
- ✅ 20+ components generated
- ✅ Developer satisfaction ≥ 8/10

---

## 🎁 Deliverables Summary

### Documentation (Complete)

- ✅ `OPENHANDS_CONDENSATION_BUG_INVESTIGATION.md` - Bug investigation
- ✅ `OPENHANDS_INVESTIGATION_EXECUTIVE_SUMMARY.md` - Executive summary
- ✅ `docs/decisions/ADR-001-OPENHANDS-INTEGRATION-POSTPONEMENT.md` - Decision record
- ✅ `docs/decisions/OPENHANDS-STRATEGIC-RECOMMENDATIONS.md` - Strategic plan
- ✅ `OPENHANDS_DECISION_SUMMARY.md` - This document

### Code (To Build)

- ⏸️ `src/agent_orchestration/openhands_integration/POSTPONED.md` - Postponement marker
- ⏸️ `src/agent_orchestration/code_generation/llm_code_generator.py` - Enhanced generator
- ⏸️ `src/agent_orchestration/code_generation/prompts/` - Prompt library (10+ templates)
- ⏸️ `docs/development/CODE_GENERATION_GUIDE.md` - Developer guide

### Tools (Complete)

- ✅ `scripts/direct_llm_code_generation.py` - Working code generation tool

---

## 🚀 Next Steps

### Immediate (This Week)

1. ✅ Review and approve ADR-001
2. ⏸️ Add postponement markers to OpenHands integration
3. ⏸️ Start Sprint 1: Integrate with Model Management Component

### Short-term (Next 2 Weeks)

1. ⏸️ Complete Sprint 1: Enhanced tool with streaming
2. ⏸️ Start Sprint 2: Prompt library and context injection

### Medium-term (Next 6 Weeks)

1. ⏸️ Complete Sprint 2: Iterative refinement
2. ⏸️ Complete Sprint 3: Documentation and training
3. ⏸️ First monthly OpenHands status check

---

**Decision Approved:** 2025-10-27
**Implementation Start:** 2025-10-28
**Expected Completion:** 2025-12-08 (6 weeks)
**Next Review:** 2026-01-27 (3 months)


---
**Logseq:** [[TTA.dev/.archive/Status-reports/2025-10/Openhands_decision_summary]]
