# Safety Systems Reference

TTA has dual safety systems that operate in parallel on every player input.
These are non-negotiable and must never be degraded or bypassed.

## Crisis Detection — 4 levels

Located at `src/agent_orchestration/crisis_detection/`.

| Level | Trigger | Response |
|---|---|---|
| `NONE` | No crisis indicators | Normal narrative flow |
| `LOW` | Mild distress language | NGA writes with extra warmth |
| `MEDIUM` | Moderate distress or vague self-harm | IPA sets `safety_signal=true`; NGA responds gently with grounding |
| `HIGH` | Explicit crisis / self-harm | Immediate safe-messaging response; escalation path triggered |

`CrisisDetector` runs in IPA. If `safety_signal=true` is set on `ProcessedInput`,
NGA automatically adjusts tone (see `nga/agent.py` system prompt guidelines).

## Emotional Safety — 5 levels

Located at `src/agent_orchestration/emotional_safety/` (or `src/components/safety/`).

The emotional safety layer evaluates NGA output before it reaches the player.
It can block or modify responses that violate therapeutic safety guidelines.

## Development rules

1. **Never degrade crisis detection sensitivity** — false negatives are far more
   dangerous than false positives in this domain.
2. **Never remove safety markers from test fixtures** — `safety_signal=true`
   paths must remain covered.
3. **Therapeutic content changes require safety review** — any modification to
   IPA or NGA system prompts must be reviewed against safe-messaging guidelines.
4. **Do not introduce LLM calls that bypass the safety pipeline** — all player-
   facing LLM outputs must flow through IPA → WBA → NGA.

## Key files

| File | Purpose |
|---|---|
| `src/agent_orchestration/crisis_detection/detector.py` | CrisisDetector implementation |
| `src/agent_orchestration/crisis_detection/enums.py` | CrisisLevel enum |
| `src/components/ipa/agent.py` | Sets `safety_signal` on ProcessedInput |
| `src/components/nga/agent.py` | Adjusts tone based on `safety_signal` |
