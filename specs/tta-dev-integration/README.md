# TTA.dev Integration Specifications

Boundary contracts defining how TTA components use TTA.dev primitives.

| Spec | Topic | Status |
|---|---|---|
| `primitive-mapping.md` | Primitive dependency map per component | ❌ Not started |
| `circuit-breaker-usage.md` | Circuit breaker delegation contract | ❌ Not started |
| `observability-boundary.md` | TTA vs TTA.dev observability split | ❌ Not started |

## Boundary Rule

> **TTA** defines the *What* (behavioral contracts, domain logic, therapeutic requirements).
> **TTA.dev** provides the *How* (infrastructure primitives: circuit breaker, retry, tracing).

See `ARCHITECTURE.md` for the two-layer toolkit architecture and the decision tree:
"Could it work for a recipe app? → YES → TTA.dev / NO → TTA"
