# OpenHands Integration Summary

**Status:** Phase 2 Complete - Ready for Implementation
**Date:** 2025-10-24

## Executive Summary

The OpenHands Python SDK integration design is complete. This document summarizes the key design decisions and provides a roadmap for Phase 3 (Implementation).

## Design Overview

### Architecture

```
TTA Orchestrator
    ↓
OpenHandsAgentProxy (Agent Layer)
    ↓
OpenHandsAdapter (Communication Layer)
    ↓
OpenHandsClient (SDK Wrapper)
    ↓
OpenHands SDK → OpenRouter API → Free Models
```

### Key Components

1. **OpenHandsClient** (`client.py`)
   - Low-level SDK wrapper
   - Handles LLM initialization, conversation management
   - Timeout handling and result parsing
   - **Lines:** ~200

2. **OpenHandsAdapter** (`adapter.py`)
   - Communication layer with retry logic
   - Error classification and handling
   - Fallback to mock responses
   - **Lines:** ~150

3. **OpenHandsAgentProxy** (`proxy.py`)
   - TTA Agent integration
   - Message coordination
   - Real-time event publishing
   - Circuit breaker integration
   - **Lines:** ~250

4. **Configuration** (`config.py`)
   - Pydantic models for validation
   - Environment variable loading
   - Free model catalog
   - **Lines:** ~200

5. **Error Recovery** (`error_recovery.py`)
   - Error classification
   - Recovery strategy selection
   - Retry with exponential backoff
   - Circuit breaker integration
   - **Lines:** ~200

**Total Estimated Lines:** ~1,000 lines of implementation code

## Free Models Supported

1. **DeepSeek V3** (Default)
   - Model ID: `deepseek/deepseek-v3:free`
   - Context: 64K tokens
   - Parameters: 685B (MoE)
   - **Recommended:** ✅

2. **Google Gemini 2.0 Flash**
   - Model ID: `google/gemini-2.0-flash-exp:free`
   - Context: 1M tokens
   - **Recommended:** ✅

3. **Meta Llama 4 Scout**
   - Model ID: `meta-llama/llama-4-scout:free`
   - Context: 190M tokens
   - Parameters: 17B
   - **Recommended:** ⚠️ (Experimental)

4. **DeepSeek R1 Qwen3**
   - Model ID: `deepseek/deepseek-r1-0528-qwen3-8b:free`
   - Context: 32K tokens
   - Parameters: 8B

## Integration Points

### 1. Agent Type Enum
```python
# src/agent_orchestration/models.py
class AgentType(str, Enum):
    OPENHANDS = "openhands"  # NEW
```

### 2. Configuration Schema
```python
# src/agent_orchestration/config_schema.py
class AgentsConfig(BaseModel):
    openhands: OpenHandsAgentConfig  # NEW
```

### 3. Service Registration
```python
# src/agent_orchestration/service.py
async def _initialize_agents(self):
    self.openhands_proxy = OpenHandsAgentProxy(...)  # NEW
```

## Error Recovery Strategy

### Error Types
- `CONNECTION_ERROR`: Network/API connectivity issues
- `TIMEOUT_ERROR`: Task execution timeout
- `AUTHENTICATION_ERROR`: Invalid API key
- `RATE_LIMIT_ERROR`: OpenRouter rate limit
- `VALIDATION_ERROR`: Invalid task/configuration
- `SDK_ERROR`: OpenHands SDK internal error
- `UNKNOWN_ERROR`: Unclassified error

### Recovery Strategies
- `RETRY`: Retry with exponential backoff
- `RETRY_WITH_BACKOFF`: Retry with longer backoff
- `FALLBACK_MODEL`: Try different free model
- `FALLBACK_MOCK`: Return mock response
- `CIRCUIT_BREAK`: Open circuit breaker
- `ESCALATE`: Escalate to human intervention

### Example Recovery Flow
```
ConnectionError
  → RETRY_WITH_BACKOFF (3 attempts)
  → CIRCUIT_BREAK (if persistent)
  → FALLBACK_MOCK (if enabled)
```

## Environment Variables

### Required
- `OPENROUTER_API_KEY`: OpenRouter API key

### Optional
- `OPENHANDS_MODEL`: Model preset (default: `deepseek-v3`)
- `OPENHANDS_BASE_URL`: API base URL
- `OPENHANDS_WORKSPACE_ROOT`: Workspace directory
- `OPENHANDS_TIMEOUT`: Default timeout (default: `300.0`)
- `OPENHANDS_ENABLE_CIRCUIT_BREAKER`: Enable circuit breaker (default: `true`)

## Testing Strategy

### Unit Tests (~500 lines)
- Configuration loading and validation
- Error classification
- Mock response generation
- Pydantic model validation

### Integration Tests (~300 lines)
- Real OpenRouter API calls (requires API key)
- Retry logic with simulated failures
- Circuit breaker behavior
- End-to-end task execution

### Test Coverage Target
- **Minimum:** 70% (staging promotion requirement)
- **Target:** 85%

## Implementation Checklist

### Phase 3: Implementation

**Week 1: Core Components**
- [ ] Create package structure (`src/agent_orchestration/openhands_integration/`)
- [ ] Implement `OpenHandsClient` (client.py)
- [ ] Implement `OpenHandsAdapter` (adapter.py)
- [ ] Implement configuration models (config.py)
- [ ] Write unit tests for core components

**Week 2: Agent Integration**
- [ ] Implement `OpenHandsAgentProxy` (proxy.py)
- [ ] Implement error recovery (error_recovery.py)
- [ ] Update `AgentType` enum
- [ ] Update configuration schema
- [ ] Register proxy in `OrchestrationService`

**Week 3: Testing and Documentation**
- [ ] Write integration tests
- [ ] Test with real OpenRouter API
- [ ] Update architecture documentation
- [ ] Create integration guide
- [ ] Create troubleshooting guide

### Phase 4: Deployment

**Staging Deployment**
- [ ] Deploy to staging environment
- [ ] Run integration tests in staging
- [ ] Performance benchmarks
- [ ] Security review
- [ ] Component maturity assessment

**Production Deployment**
- [ ] Production deployment approval
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Monitor error rates and performance
- [ ] Update component maturity to production

## Success Metrics

### Performance
- **Task Execution Time:** <300s (95th percentile)
- **API Response Time:** <5s (95th percentile)
- **Error Rate:** <5%
- **Circuit Breaker Trips:** <1% of requests

### Quality
- **Test Coverage:** >70% (minimum), >85% (target)
- **Code Quality:** Passes ruff linting and pyright type checking
- **Security:** No secrets in code, API key via environment
- **Documentation:** Complete integration guide and troubleshooting

### Reliability
- **Uptime:** >99.5% (7-day average)
- **Retry Success Rate:** >80%
- **Fallback Success Rate:** 100% (mock responses)

## Risks and Mitigations

### Risk 1: OpenRouter API Rate Limits
**Mitigation:**
- Use free models with generous limits
- Implement circuit breaker to prevent cascading failures
- Fall back to mock responses during rate limit events

### Risk 2: OpenHands SDK Breaking Changes
**Mitigation:**
- Pin SDK version in dependencies
- Monitor SDK releases for breaking changes
- Maintain adapter layer for SDK abstraction

### Risk 3: API Key Exposure
**Mitigation:**
- Use Pydantic `SecretStr` for in-memory protection
- Load from environment variables only
- Never log API key
- Integrate with secrets manager (future)

### Risk 4: Workspace Isolation Failures
**Mitigation:**
- Create isolated workspace per task
- Clean up workspaces after task completion
- Implement workspace size limits
- Monitor disk usage

## Next Steps

1. **Review Design Document:** `docs/development/openhands-integration-design.md`
2. **Begin Implementation:** Start with `OpenHandsClient` (simplest component)
3. **Incremental Testing:** Test each component as it's implemented
4. **Integration Testing:** Test with real OpenRouter API early
5. **Documentation:** Update docs as implementation progresses

## Questions for User

Before proceeding to Phase 3 (Implementation), please confirm:

1. **API Key:** Do you have an OpenRouter API key? (Get from https://openrouter.ai/keys)
2. **Model Preference:** Which free model should be the default? (Recommend: DeepSeek V3)
3. **Workspace Location:** Where should OpenHands workspaces be created? (Default: `./openhands_workspace`)
4. **Testing Approach:** Should we test with real API or use mocks initially?
5. **Deployment Timeline:** When do you want this in staging/production?

---

**Design Status:** ✅ COMPLETE
**Implementation Status:** ⏳ READY TO START
**Estimated Completion:** 2-3 weeks (implementation + testing + deployment)
