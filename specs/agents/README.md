# Agent Specifications

**Last Updated:** 2026-03-23

Behavioral contracts for TTA's core agents.

| Spec | Agent | Status |
|---|---|---|
| `ipa-input-processing-agent.md` | Input Processing Agent (IPA) | ✅ Drafted |
| `wba-world-building-agent.md` | World Building Agent (WBA) | ✅ Drafted |
| `nga-narrative-generator-agent.md` | Narrative Generator Agent (NGA) | ✅ Drafted |
| `agent-orchestration-protocol.md` | IPA → WBA → NGA coordination | ✅ Drafted |

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
