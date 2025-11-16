# Sub-Agent Orchestration Analysis for TTA Development Workflow

**Date**: 2025-10-28  
**Status**: Research & Recommendation  
**Context**: Replacing OpenHands with more effective sub-agent solutions

## Executive Summary

After analyzing LiteLLM and alternative frameworks for sub-agent orchestration, I recommend a **hybrid approach** combining:

1. **LiteLLM** as the unified LLM gateway/router (infrastructure layer)
2. **LangGraph** for complex multi-step development workflows (already in stack)
3. **Custom lightweight sub-agents** for specialized tasks (test generation, scaffolding)

This approach leverages your existing architecture while adding minimal complexity.

---

## 1. LiteLLM Analysis

### What LiteLLM Provides

**Core Capabilities:**
- **Unified LLM Interface**: Single API for 100+ LLM providers (OpenAI, Anthropic, Google, local models)
- **Router/Proxy**: Load balancing, fallback, and circuit breaker patterns
- **Cost Management**: Track usage, set budgets, enforce rate limits
- **Model Fallback**: Automatic failover between models/providers
- **Caching**: Response caching to reduce costs and latency

**What LiteLLM Does NOT Provide:**
- ❌ Multi-agent orchestration (not an agent framework)
- ❌ Task delegation or sub-agent management
- ❌ Workflow state management
- ❌ Agent-to-agent communication patterns

### LiteLLM's Role in Your Stack

**Best Use Case**: Infrastructure layer for model access, NOT agent orchestration

```python
# LiteLLM as unified model gateway
from litellm import Router

router = Router(
    model_list=[
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "openai/gpt-4-turbo-preview",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
        {
            "model_name": "gpt-4",  # Same name for fallback
            "litellm_params": {
                "model": "openrouter/anthropic/claude-3-opus",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
            }
        },
        {
            "model_name": "local-model",
            "litellm_params": {
                "model": "ollama/llama3.1:8b",
                "api_base": "http://localhost:11434",
            }
        }
    ],
    # Circuit breaker configuration
    num_retries=3,
    timeout=30,
    fallbacks=[{"gpt-4": ["local-model"]}],
    # Redis for state persistence
    redis_host="localhost",
    redis_port=6379,
)

# Use in your existing adapters
response = await router.acompletion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Generate test for function X"}]
)
```

**Integration Points:**
- Replace direct OpenRouter calls in `OpenRouterProvider`
- Add as fallback layer in `ModelManagementComponent`
- Use for circuit breaker persistence (already using Redis)

---

## 2. Alternative Frameworks Comparison

### Framework Landscape (2025)

| Framework | Best For | Complexity | Integration Effort | Verdict |
|-----------|----------|------------|-------------------|---------|
| **LangGraph** | Complex workflows, state machines | Medium | ✅ Already integrated | **Use for workflows** |
| **CrewAI** | Role-based multi-agent teams | Low-Medium | Medium | ❌ Overlaps with existing arch |
| **AutoGen** | Conversational multi-agent | Medium-High | High | ❌ Too heavyweight |
| **Google ADK** | Multi-agent orchestration | Medium | Medium-High | ⚠️ Consider for future |
| **OpenAI Agents SDK** | Simple agent patterns | Low | Low | ⚠️ Limited to OpenAI models |
| **Custom Solution** | Specialized dev tasks | Low | Low | ✅ **Recommended** |

### Detailed Analysis

#### LangGraph (Already in Stack)
**Strengths:**
- ✅ Already integrated (`langgraph>=0.2.0` in dependencies)
- ✅ Excellent for stateful workflows (test generation → validation → fix)
- ✅ Graph-based execution with conditional branching
- ✅ Built-in state persistence (Redis-compatible)
- ✅ Works with any LLM provider (via LangChain)

**Use Cases for TTA:**
- Multi-step test generation workflows
- Code scaffolding with validation loops
- Refactoring workflows with safety checks

**Example:**
```python
from langgraph.graph import StateGraph, END

# Define workflow for test generation
workflow = StateGraph(TestGenState)

workflow.add_node("analyze_code", analyze_code_node)
workflow.add_node("generate_tests", generate_tests_node)
workflow.add_node("validate_tests", validate_tests_node)
workflow.add_node("fix_tests", fix_tests_node)

workflow.add_edge("analyze_code", "generate_tests")
workflow.add_edge("generate_tests", "validate_tests")
workflow.add_conditional_edges(
    "validate_tests",
    should_fix_tests,
    {
        "fix": "fix_tests",
        "done": END
    }
)
workflow.add_edge("fix_tests", "validate_tests")

workflow.set_entry_point("analyze_code")
```

#### CrewAI
**Strengths:**
- Role-based agent teams (e.g., "Test Engineer", "Code Reviewer")
- Simple API for task delegation
- Built-in memory and context sharing

**Weaknesses:**
- ❌ Overlaps with your existing IPA/WBA/NGA architecture
- ❌ Opinionated about agent roles (conflicts with therapeutic agents)
- ❌ Less control over execution flow vs LangGraph

**Verdict**: Skip - would create architectural confusion

#### Google ADK (Agent Development Kit)
**Strengths:**
- ✅ Excellent multi-agent orchestration
- ✅ Sub-agent delegation patterns
- ✅ Model-agnostic (works with LiteLLM)
- ✅ Rich tool integration

**Weaknesses:**
- ⚠️ Relatively new (April 2025)
- ⚠️ Optimized for Google ecosystem (but works with others)
- ⚠️ Medium learning curve

**Verdict**: Consider for future, but not urgent given LangGraph coverage

#### Custom Lightweight Sub-Agents
**Strengths:**
- ✅ Minimal complexity
- ✅ Perfect fit for specialized tasks
- ✅ Full control over behavior
- ✅ Easy to integrate with existing circuit breakers

**Use Cases:**
- Test generation sub-agent
- Code scaffolding sub-agent
- Documentation generation sub-agent

---

## 3. Recommended Architecture

### Hybrid Approach: LiteLLM + LangGraph + Custom Sub-Agents

```
┌─────────────────────────────────────────────────────────────┐
│                    Development Workflow                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Workflow Orchestrator                 │
│  (Multi-step workflows: test gen → validate → fix)          │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  Test    │  │  Scaffold│  │  Refactor│
        │  Agent   │  │  Agent   │  │  Agent   │
        └──────────┘  └──────────┘  └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  LiteLLM Router/Gateway                      │
│  (Unified model access, fallback, circuit breakers)         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  OpenRouter  │    │    Ollama    │    │  OpenAI API  │
│  (Primary)   │    │  (Fallback)  │    │  (Premium)   │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Integration with Existing Architecture

**Existing Runtime Agents** (unchanged):
- IPA (Input Processing Agent)
- WBA (World Building Agent)
- NGA (Narrative Generation Agent)

**New Development-Time Sub-Agents**:
- Test Generation Agent
- Code Scaffolding Agent
- Refactoring Agent

**Key Principle**: Development agents are **separate** from runtime therapeutic agents

---

## 4. Implementation Roadmap

### Phase 1: LiteLLM Integration (Week 1)

**Goal**: Replace direct OpenRouter calls with LiteLLM router

**Tasks**:
1. Add `litellm>=1.0.0` to dependencies
2. Create `LiteLLMProvider` in `packages/tta-ai-framework/src/tta_ai/models/providers/`
3. Update `ModelManagementComponent` to use LiteLLM for fallback
4. Configure circuit breakers to use LiteLLM's built-in retry logic
5. Add cost tracking and budget enforcement

**Benefits**:
- Unified model access across all providers
- Better fallback handling
- Cost visibility and control
- Foundation for sub-agents

### Phase 2: Custom Sub-Agents (Week 2-3)

**Goal**: Create lightweight sub-agents for common development tasks

**Test Generation Agent**:
```python
# packages/tta-ai-framework/src/tta_ai/dev_agents/test_generator.py

from typing import Any
from litellm import Router
from tta_ai.orchestration import CircuitBreaker

class TestGenerationAgent:
    """Specialized agent for generating comprehensive tests."""
    
    def __init__(self, llm_router: Router, circuit_breaker: CircuitBreaker):
        self.router = llm_router
        self.circuit_breaker = circuit_breaker
    
    async def generate_tests(
        self,
        source_code: str,
        test_type: str = "unit",  # unit, integration, e2e
        coverage_target: float = 0.80,
    ) -> dict[str, Any]:
        """Generate tests for given source code."""
        
        prompt = self._build_test_prompt(source_code, test_type, coverage_target)
        
        # Use circuit breaker for resilience
        response = await self.circuit_breaker.call(
            self.router.acompletion,
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Lower temp for code generation
        )
        
        return {
            "test_code": response.choices[0].message.content,
            "test_type": test_type,
            "estimated_coverage": self._estimate_coverage(response),
        }
```

**Code Scaffolding Agent**:
- Generate boilerplate for new components
- Follow TTA architectural patterns
- Include proper type hints and docstrings

**Refactoring Agent**:
- Suggest refactorings based on code smells
- Ensure SOLID principles compliance
- Maintain backward compatibility

### Phase 3: LangGraph Workflows (Week 4)

**Goal**: Orchestrate sub-agents with stateful workflows

**Test Generation Workflow**:
```python
# packages/tta-ai-framework/src/tta_ai/dev_workflows/test_generation.py

from langgraph.graph import StateGraph, END
from typing import TypedDict

class TestGenState(TypedDict):
    source_file: str
    source_code: str
    test_code: str
    validation_result: dict
    iteration: int
    max_iterations: int

async def analyze_code(state: TestGenState) -> TestGenState:
    """Analyze source code to determine test strategy."""
    # Use codebase-retrieval to find dependencies
    # Identify edge cases and boundary conditions
    return state

async def generate_tests(state: TestGenState) -> TestGenState:
    """Generate test code using TestGenerationAgent."""
    agent = TestGenerationAgent(llm_router, circuit_breaker)
    result = await agent.generate_tests(state["source_code"])
    state["test_code"] = result["test_code"]
    return state

async def validate_tests(state: TestGenState) -> TestGenState:
    """Run tests and check coverage."""
    # Execute pytest
    # Measure coverage
    # Identify failures
    return state

def should_retry(state: TestGenState) -> str:
    """Decide whether to retry test generation."""
    if state["validation_result"]["passed"]:
        return "done"
    if state["iteration"] >= state["max_iterations"]:
        return "done"
    return "retry"

# Build workflow
workflow = StateGraph(TestGenState)
workflow.add_node("analyze", analyze_code)
workflow.add_node("generate", generate_tests)
workflow.add_node("validate", validate_tests)
workflow.add_node("fix", fix_failing_tests)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "generate")
workflow.add_edge("generate", "validate")
workflow.add_conditional_edges("validate", should_retry, {
    "retry": "fix",
    "done": END
})
workflow.add_edge("fix", "generate")
```

---

## 5. Cost and Performance Considerations

### LiteLLM Cost Management

```python
# config/litellm_config.yaml
model_list:
  - model_name: dev-agent-primary
    litellm_params:
      model: openrouter/meta-llama/llama-3.1-8b-instruct:free
      api_key: ${OPENROUTER_API_KEY}
    model_info:
      max_tokens: 8192
      cost_per_token: 0.0  # Free tier
  
  - model_name: dev-agent-premium
    litellm_params:
      model: openai/gpt-4-turbo-preview
      api_key: ${OPENAI_API_KEY}
    model_info:
      max_tokens: 128000
      cost_per_token: 0.00001  # $0.01 per 1K tokens

router_settings:
  routing_strategy: "cost-based"  # Prefer free models
  fallbacks:
    dev-agent-primary: ["dev-agent-premium"]
  budget_manager:
    daily_budget: 5.00  # $5/day for dev agents
    alert_threshold: 0.8  # Alert at 80% budget
```

### Performance Optimization

**Caching Strategy**:
- Cache test generation results by source code hash
- Cache scaffolding templates
- TTL: 24 hours for dev tasks

**Parallel Execution**:
- Use LangGraph's parallel node execution
- Generate multiple test variants simultaneously
- Select best based on coverage/quality metrics

---

## 6. Comparison with OpenHands

| Aspect | OpenHands | Recommended Approach |
|--------|-----------|---------------------|
| **Complexity** | High (full SDK) | Low-Medium (focused tools) |
| **Integration** | Tight coupling | Loose coupling |
| **Flexibility** | Limited | High (custom agents) |
| **Cost** | Opaque | Transparent (LiteLLM tracking) |
| **Maintenance** | External dependency | Internal control |
| **Circuit Breakers** | Not integrated | ✅ Fully integrated |
| **Redis Coordination** | Not integrated | ✅ Fully integrated |
| **Model Choice** | Limited | ✅ 100+ models via LiteLLM |

---

## 7. Next Steps

### Immediate Actions (This Week)

1. **Add LiteLLM to dependencies**:
   ```bash
   uv add litellm>=1.0.0
   ```

2. **Create proof-of-concept**:
   - Simple test generation agent
   - LiteLLM router configuration
   - Integration with existing circuit breakers

3. **Validate approach**:
   - Generate tests for 3-5 existing modules
   - Measure quality and coverage
   - Compare cost vs OpenRouter direct calls

### Success Criteria

- ✅ Test generation achieves ≥70% coverage on first attempt
- ✅ Cost per test generation < $0.05
- ✅ Integration with circuit breakers (no new patterns needed)
- ✅ Fallback to local models works seamlessly
- ✅ Development workflow feels natural (not forced)

---

## 8. Conclusion

**Recommendation**: Implement the hybrid approach with LiteLLM + LangGraph + Custom Sub-Agents

**Rationale**:
1. **LiteLLM** provides the infrastructure you need (routing, fallback, cost control) without forcing an agent framework
2. **LangGraph** is already in your stack and perfect for complex workflows
3. **Custom sub-agents** give you full control and minimal complexity
4. **Seamless integration** with existing circuit breakers, Redis coordination, and Neo4j state

**Avoid**:
- ❌ CrewAI (architectural overlap)
- ❌ AutoGen (too heavyweight)
- ❌ OpenHands (ineffective for your use case)

**Consider for Future**:
- ⚠️ Google ADK (if multi-agent orchestration needs grow)
- ⚠️ OpenAI Agents SDK (if standardizing on OpenAI models)

This approach aligns with your existing architecture, respects your circuit breaker patterns, and provides a clear path forward without introducing unnecessary complexity.

