# ADR-001: OpenHands Integration Postponement

**Status:** Accepted
**Date:** 2025-10-27
**Decision Makers:** TTA Development Team
**Related Documents:**
- `OPENHANDS_CONDENSATION_BUG_INVESTIGATION.md`
- `OPENHANDS_INVESTIGATION_EXECUTIVE_SUMMARY.md`
- `VALIDATION_REPORT.md`

---

## Context

The TTA project integrated OpenHands (version 0.59) for AI-powered code generation to support the agent orchestration workflow. After comprehensive validation and testing, we discovered critical bugs in OpenHands that prevent it from functioning correctly for code generation tasks.

### Investigation Summary

**What We Built:**
- Complete OpenHands integration (28 files, 8,388 lines of code)
- Docker runtime client with full tool access
- Configuration management and error recovery
- Metrics collection and monitoring
- Comprehensive test suite

**What We Discovered:**
- **Condensation Loop Bug** (GitHub Issue #8630) - Agent gets stuck in infinite loop
- **No File Generation** - Zero output files created despite "successful" execution
- **Unresolved Status** - Bug exists since version 0.39, no fixes in releases up to 1.0.2-cli
- **Deprecated CLI** - Command-line interface marked for removal

**What We Validated:**
- ✅ All 28 integration files present and functional
- ✅ Docker client initializes correctly
- ✅ Configuration loads from environment
- ✅ Infrastructure ready for future use
- ❌ Task execution blocked by condensation loop bug

---

## Decision

**We are POSTPONING (not abandoning) the OpenHands integration** and adopting a **Direct LLM Code Generation** approach for immediate code generation needs.

### Rationale

1. **Bug is Unfixable by Us**
   - Root cause is in OpenHands core (`conversation_window_condenser.py`)
   - Issue closed as "not planned" by OpenHands maintainers
   - No timeline for fix in upstream project

2. **Working Alternative Exists**
   - Direct LLM API calls provide reliable code generation
   - Simpler implementation (single Python script vs. Docker orchestration)
   - Faster execution (< 10 seconds vs. 110+ seconds)
   - Cost-effective (free DeepSeek Chat V3.1 model)

3. **Infrastructure Investment Preserved**
   - All OpenHands integration code remains in repository
   - Ready to activate when bugs are fixed
   - Valuable learning about agent orchestration patterns

4. **TTA Has Better Alternatives**
   - **Model Management Component** already provides multi-provider support
   - **OpenRouter Provider** for cloud-based models
   - **Ollama Provider** for local deployment
   - **Custom API Provider** for OpenAI/Anthropic
   - Direct integration with TTA's existing architecture

---

## Consequences

### Positive

✅ **Immediate Code Generation Capability**
- Working tool (`scripts/direct_llm_code_generation.py`) ready for use
- Production-quality code generation validated
- No dependency on buggy external framework

✅ **Simplified Architecture**
- Direct API calls easier to debug and maintain
- No Docker complexity for code generation
- Better integration with TTA's Model Management Component

✅ **Cost Optimization**
- Free models (DeepSeek Chat V3.1) produce excellent results
- No overhead from OpenHands agent orchestration
- Lower latency and resource usage

✅ **Preserved Investment**
- OpenHands integration code retained for future use
- Knowledge gained about agent orchestration
- Infrastructure ready when bugs are fixed

### Negative

⚠️ **Limited to Single-Shot Generation**
- No iterative refinement (OpenHands strength)
- No file system exploration
- No multi-step task execution

⚠️ **Manual Prompt Engineering**
- Requires crafting effective prompts
- No automatic task decomposition
- Less autonomous than OpenHands (when working)

⚠️ **Sunk Cost**
- 28 files (8,388 lines) not immediately usable
- Time invested in integration and testing
- However: Infrastructure ready for future activation

---

## Implementation Plan

### Phase 1: Archive OpenHands Integration (Immediate)

**Status:** ✅ COMPLETE

1. ✅ Update `VALIDATION_REPORT.md` with postponement status
2. ✅ Create investigation documentation
3. ✅ Implement direct LLM code generation tool
4. ✅ Test and validate alternative approach

### Phase 2: Enhance Direct LLM Tool (Next Sprint)

**Priority:** HIGH

1. **Integrate with TTA Model Management Component**
   - Use existing `OpenRouterProvider` instead of direct httpx calls
   - Leverage model selection and fallback mechanisms
   - Add streaming support for better UX

2. **Add Context Injection**
   - Read existing codebase for context
   - Include TTA architectural patterns (circuit breakers, agent orchestration)
   - Reference component maturity workflow

3. **Implement Iterative Refinement**
   - Multi-turn conversation for code improvement
   - Validation against quality gates
   - Test generation alongside code

4. **Create Prompt Library**
   - TTA-specific prompts for common tasks
   - Agent orchestration patterns
   - Circuit breaker implementations
   - Redis/Neo4j integration patterns

### Phase 3: Monitor OpenHands (Ongoing)

**Priority:** LOW

1. **Watch for Bug Fixes**
   - Monitor GitHub issue #8630
   - Track releases for condensation fixes
   - Test new versions when available

2. **Re-evaluation Criteria**
   - OpenHands version 0.60+ with condensation bug fix
   - Successful test of file generation
   - Stable release with no critical bugs

3. **Activation Plan**
   - Uncomment OpenHands integration code
   - Update configuration for new version
   - Run comprehensive test suite
   - Gradual rollout for complex tasks

---

## Alternatives Considered

### Alternative 1: Fix OpenHands Bug Ourselves

**Rejected** - Root cause is in OpenHands core, requires deep understanding of agent orchestration internals. Maintaining a fork would be costly.

### Alternative 2: Use OpenHands SDK Instead of Docker

**Rejected** - SDK likely has same condensation bug. Not tested due to time constraints and working alternative.

### Alternative 3: Use Ollama for Code Generation

**Considered** - Ollama is already running in TTA. Could be used as fallback, but OpenRouter free models provide better quality.

### Alternative 4: Abandon Code Generation Entirely

**Rejected** - Code generation is valuable for TTA development workflow. Direct LLM approach provides working solution.

---

## Integration with TTA Architecture

### Leverage Existing Model Management

**TTA already has a sophisticated model management system:**

```python
# Use TTA's OpenRouterProvider instead of direct API calls
from tta_ai.models.providers import OpenRouterProvider

provider = OpenRouterProvider()
await provider.initialize({
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "base_url": "https://openrouter.ai/api/v1",
    "free_models_only": False,
    "cost_limit_per_request": 0.01
})

# Select optimal model for task
model = await provider.load_model("deepseek/deepseek-chat-v3.1:free")
response = await model.generate(prompt)
```

**Benefits:**
- ✅ Consistent with TTA architecture
- ✅ Automatic model selection and fallback
- ✅ Cost tracking and limits
- ✅ Performance monitoring
- ✅ Therapeutic safety checks

### Component Maturity Workflow Integration

**Use code generation for component development:**

1. **Development Stage** (≥70% coverage, ≥75% mutation score)
   - Generate initial component implementation
   - Generate comprehensive test suite
   - Validate against quality gates

2. **Staging Stage** (≥80% coverage, ≥80% mutation score)
   - Generate additional edge case tests
   - Generate documentation
   - Validate production readiness

3. **Production Stage** (≥85% coverage, ≥85% mutation score)
   - Generate monitoring and observability code
   - Generate deployment scripts
   - Validate battle-tested status

---

## Success Metrics

### Short-term (1 month)

- ✅ Direct LLM tool integrated with TTA Model Management Component
- ✅ 10+ components generated using direct LLM approach
- ✅ 100% of generated code passes quality gates
- ✅ Developer satisfaction with code generation workflow

### Medium-term (3 months)

- ✅ Prompt library with 20+ TTA-specific templates
- ✅ Iterative refinement implemented
- ✅ Context injection from existing codebase
- ✅ 50% reduction in time to create new components

### Long-term (6 months)

- ⏸️ OpenHands bug fixed in upstream project
- ⏸️ OpenHands integration re-activated for complex tasks
- ⏸️ Hybrid approach: Direct LLM for simple tasks, OpenHands for complex

---

## References

- **GitHub Issue #8630:** "[Bug]: Endless 'CondensationAction' Loop Caused by Constant Context Overflow"
- **OpenHands Releases:** https://github.com/All-Hands-AI/OpenHands/releases
- **TTA Model Management:** `packages/tta-ai-framework/src/tta_ai/models/`
- **Investigation Report:** `OPENHANDS_CONDENSATION_BUG_INVESTIGATION.md`
- **Executive Summary:** `OPENHANDS_INVESTIGATION_EXECUTIVE_SUMMARY.md`

---

## Approval

**Approved by:** TTA Development Team
**Date:** 2025-10-27
**Status:** ✅ Accepted and Implemented

**Next Review:** 2026-01-27 (3 months) - Re-evaluate OpenHands status



---
**Logseq:** [[TTA.dev/Docs/Decisions/Adr-001-openhands-integration-postponement]]
