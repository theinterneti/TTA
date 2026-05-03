# S18 — Therapeutic Framework

> **Status**: 📝 Stub (Future)
> **Level**: 5 — Future Vision
> **Dependencies**: S01 (Core Loop), S03 (Narrative Engine), S06 (Session Model)
> **Last Updated**: 2025-07-24

---

## Vision

The Therapeutic Framework integrates evidence-based therapeutic approaches — CBT,
ACT, exposure therapy, mindfulness, and narrative therapy — directly into gameplay
mechanics. Therapy is not a separate mode or overlay; it IS the game. A player
choosing to confront a fear in-narrative is doing exposure work. A player
reframing a setback through their character's inner monologue is practicing
cognitive restructuring.

The framework provides the narrative engine with therapeutic scaffolding:
structured progressions, validated outcome measures embedded in story beats, and
adaptive difficulty that responds to a player's emotional state and therapeutic
goals. Clinicians can configure therapeutic parameters for specific players or
cohorts without touching game content.

---

## v1 Constraints

What v1 MUST accommodate so this feature remains viable:

- **Extensible narrative engine**: The narrative generation pipeline must accept
  pluggable content strategies. Do not hardcode a single generation approach —
  use a strategy pattern or hook system that future therapeutic modules can
  extend.
- **Session data model supports tracking**: The session/turn data model must
  store structured metadata per turn (not just raw text). Future therapeutic
  tracking needs fields like `turn_metadata: dict` or equivalent — a place to
  attach therapeutic annotations without schema migration.
- **No hardcoded "just entertainment" assumptions**: Narrative prompts,
  genre definitions, and world templates must not assume the sole purpose is
  entertainment. Keep content framing neutral enough that therapeutic content
  can coexist.
- **Player profile extensibility**: The player/session model should have an
  extension point (e.g., `player_config: dict`) where future therapeutic
  preferences and goals can be stored.
- **Turn history is queryable**: Conversation history must be stored in a
  structured, queryable format — not opaque blobs. Therapeutic analysis
  needs to query across turns (e.g., "show all turns where the player
  expressed avoidance").

---

## Not in v1

- Therapeutic content strategies or clinical modules
- Outcome measurement or validated therapeutic assessments
- Clinician dashboards or configuration interfaces
- Adaptive therapeutic difficulty
- Any clinical claims or therapeutic branding
- Integration with EHR systems or clinical workflows
- IRB-approved research protocols

---

## Open Questions

1. What licensing or regulatory requirements apply when a game makes therapeutic
   claims? At what point does "game with therapeutic value" become "digital
   therapeutic" requiring FDA clearance?
2. Should therapeutic modules be first-party only, or could the community
   framework (S22) support clinician-authored therapeutic content?
3. How do we validate therapeutic effectiveness without running clinical trials
   in v1?
4. What's the right abstraction boundary between "narrative engine" and
   "therapeutic engine" — are they peers, or does therapeutic wrap narrative?

---

## Related Specs

- **S01 — Core Game Loop**: Turn processing pipeline where therapeutic hooks
  would attach
- **S03 — Narrative Engine**: Content generation that therapeutic strategies
  would extend
- **S06 — Session Model**: Data model that must support therapeutic metadata
- **S19 — Crisis & Content Safety**: Safety layer that therapeutic framework
  would interact with
