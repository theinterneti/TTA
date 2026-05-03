# S19 — Crisis & Content Safety

> **Status**: 📝 Stub (Future)
> **Level**: 5 — Future Vision
> **Dependencies**: S01 (Core Loop), S03 (Narrative Engine), S05 (SSE Streaming)
> **Last Updated**: 2025-07-24

---

## Vision

Crisis & Content Safety is a multi-layered safety system that protects players
from harmful content and detects when a player may be in crisis. It operates at
four severity levels — from gentle content filtering (Level 1) through active
crisis intervention with escalation to human professionals (Level 4).

The system is not a gatekeeper that blocks gameplay — it is a safety net woven
into the narrative experience. Content filtering shapes what the AI generates.
Emotional safety validation ensures the narrative doesn't push a vulnerable
player too hard. Crisis detection monitors player input for distress signals.
Intervention protocols provide immediate, clinically-informed responses when
crisis is detected, including warm handoffs to crisis hotlines and human
therapists.

---

## v1 Constraints

What v1 MUST accommodate so this feature remains viable:

- **Turn pipeline hook point**: The turn processing pipeline (between player
  input and narrative output) MUST have a clearly defined middleware/hook point
  where safety checks can be inserted. This is non-negotiable — retrofitting
  safety into a pipeline that doesn't expect it is a rewrite.
- **Bidirectional hook**: Safety needs to inspect BOTH player input (crisis
  detection) AND AI output (content filtering) before delivery. The pipeline
  must support pre-generation and post-generation hooks.
- **Stream interruption**: The SSE streaming system must support mid-stream
  interruption. If a safety check triggers after streaming has started, the
  system must be able to halt the stream and substitute a safety response.
  Design the SSE protocol with a `stream_interrupted` event type.
- **Session flagging**: The session data model must support a `flags` or
  `status` field that safety systems can write to. Flags like
  `crisis_detected`, `content_filtered`, `escalation_pending` must be
  persistable without schema changes.
- **Audit trail**: All turns must be stored with enough context to reconstruct
  what happened. Safety incidents require an audit trail — don't discard or
  summarize conversation history in ways that lose fidelity.
- **No response caching that bypasses safety**: If v1 implements any response
  caching, cached responses must still pass through safety hooks on retrieval.
  Never serve cached content that skips the safety layer.

---

## Not in v1

- Crisis detection algorithms or ML models
- Content filtering rules or blocklists
- Emotional safety scoring
- Escalation protocols or crisis hotline integration
- Therapist notification systems
- Real-time emotional state tracking
- Safety analytics dashboards
- Mandatory reporting compliance
- Clinical supervision interfaces

---

## Open Questions

1. What is the right granularity for safety hook points — per-turn, per-token,
   or per-sentence? Token-level is expensive but catches partial unsafe
   generations.
2. Should safety state be per-session or per-player? A player in crisis in one
   session is likely in crisis in all sessions.
3. How do we handle false positives gracefully? Overly aggressive safety
   filtering ruins the experience; under-filtering risks harm.
4. What's the liability model when AI-detected crisis is wrong (false positive)
   or missed (false negative)?
5. Does HIPAA apply to crisis detection data even if we're "just a game"?

---

## Related Specs

- **S01 — Core Game Loop**: Pipeline where safety hooks must be insertable
- **S03 — Narrative Engine**: Content generation that safety must be able to
  filter or halt
- **S05 — SSE Streaming**: Stream protocol that must support interruption
- **S06 — Session Model**: Data model that must support safety flags
- **S18 — Therapeutic Framework**: Therapeutic context informs safety thresholds
