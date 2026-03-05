# Agent Specifications

Behavioral contracts for TTA's core agents.

| Spec | Agent | Status |
|---|---|---|
| `ipa-input-processing-agent.md` | Input Processing Agent (IPA) | ❌ Not started |
| `wba-world-building-agent.md` | World Building Agent (WBA) | ❌ Not started |
| `nga-narrative-generator-agent.md` | Narrative Generator Agent (NGA) | ❌ Not started |
| `agent-orchestration-protocol.md` | IPA → WBA → NGA coordination | ❌ Not started |

## Code References

- Agent types: `src/agent_orchestration/agents.py` (`AgentType` enum)
- Agent models: `src/agent_orchestration/models.py`
- Unified orchestrator: `src/agent_orchestration/unified_orchestrator.py`

## TTA.dev Primitives Used

Each agent spec must declare which TTA.dev primitives it depends on:
- **Circuit Breaker** — graceful degradation for LLM calls
- **Retry with Backoff** — transient failure recovery
- **Router** — intent-based agent selection
- **OpenTelemetry Tracing** — distributed tracing across agent calls
