# Therapeutic Safety Specifications

**Last Updated:** 2026-03-23

Domain specifications for TTA's therapeutic safety systems.

| Spec | System | Status |
|---|---|---|
| `crisis-detection.md` | Crisis Detection (4-level severity) | ✅ Drafted |
| `emotional-safety-system.md` | Emotional Safety (5-level safety) | ✅ Drafted |
| `therapeutic-integration.md` | Therapeutic Goal Integration | ✅ Drafted |
| `safety-interop.md` | Crisis ↔ Emotional Safety Interop | ✅ Drafted |

## Code References

- Crisis detection: `src/agent_orchestration/crisis_detection/`
- Emotional safety: `src/components/gameplay_loop/narrative/emotional_safety_system.py`
- Therapeutic integrator: `src/components/gameplay_loop/narrative/therapeutic_integrator.py`

## Level Mapping (Proposed)

| Emotional Safety | Crisis Detection | Action |
|---|---|---|
| SAFE | — | Normal gameplay |
| CAUTION | LOW | Log + monitor |
| WARNING | MODERATE | Reduce intensity, offer break |
| UNSAFE | HIGH | Halt content, grounding, exit |
| CRISIS | CRITICAL | Immediate intervention |
