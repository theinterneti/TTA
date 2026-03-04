# Persistence Specifications

Data layer contracts for TTA's storage systems.

| Spec | System | Status |
|---|---|---|
| `redis-session-cache.md` | Redis session cache + messaging | ❌ Not started |
| `neo4j-story-graph.md` | Neo4j story graph persistence | ❌ Not started |
| `data-retention-policy.md` | HIPAA-compliant data retention | ❌ Not started |

## Code References

- Redis messaging: `src/agent_orchestration/messaging.py`
- Redis circuit breaker state: `src/agent_orchestration/circuit_breaker.py`
- Neo4j gameplay: `src/player_experience/database/`
- Neo4j models: `src/components/`
