# Therapeutic Safety Specifications

Domain specifications for TTA's therapeutic safety systems.

| Spec | System | Status |
|---|---|---|
| `crisis-detection.md` | Crisis Detection (4-level severity) | ❌ Not started |
| `emotional-safety-system.md` | Emotional Safety (5-level safety) | ❌ Not started |
| `therapeutic-integration.md` | Therapeutic Goal Integration | ❌ Not started |
| `safety-interop.md` | Crisis ↔ Emotional Safety Interop | ❌ Not started |

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
