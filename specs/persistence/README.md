# Persistence Specifications

**Last Updated:** 2026-03-23

Data layer contracts for TTA's storage systems.

| Spec | System | Status |
|---|---|---|
| `redis-session-cache.md` | Redis session cache + messaging | ✅ Drafted |
| `neo4j-story-graph.md` | Neo4j story graph persistence | ✅ Drafted |
| `data-retention-policy.md` | HIPAA-compliant data retention | ✅ Drafted |

## Code References

- Redis messaging: `src/agent_orchestration/messaging.py`
- Redis circuit breaker state: `src/agent_orchestration/circuit_breaker.py`
- Neo4j gameplay: `src/player_experience/database/`
- Neo4j models: `src/components/`
