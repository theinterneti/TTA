# S21 — Collaborative Writing

> **Status**: 📝 Stub (Future)
> **Level**: 5 — Future Vision
> **Dependencies**: S01 (Core Loop), S04 (World Model), S05 (SSE Streaming),
>   S06 (Session Model)
> **Last Updated**: 2025-07-24

---

## Vision

Collaborative Writing brings multiple players into the same world to co-author
a story in real time. Each player controls a character with their own
perspective, goals, and voice. The AI narrator weaves their individual actions
into a coherent shared narrative — like a tabletop RPG with an AI game master.

The collaboration model supports multiple modes: synchronous co-op (players
in the same scene, turns interleaved), asynchronous co-op (players in different
parts of the world, narratives merge at plot points), and spectator mode
(readers watching a story unfold live). The transport shifts from SSE to
WebSocket to support bidirectional real-time communication.

---

## v1 Constraints

What v1 MUST accommodate so this feature remains viable:

- **World model supports multiple actors**: The world/state model must not
  hardcode a single player. Use abstractions like `actor` or `participant`
  rather than `player` in the world state schema. A world should be able to
  contain multiple actors without structural changes.
- **Session ≠ world**: The session model and world model must be separable.
  In v1, one session maps to one world — but the data model must not enforce
  this as a hard constraint. Future: many sessions (one per player) can
  reference the same world.
- **Clean SSE → WebSocket migration path**: Design the SSE event protocol so
  that the same event types and payload shapes work over WebSocket. Use
  event type strings and JSON payloads — not SSE-specific framing that would
  need to be re-invented for WebSocket.
- **Turn pipeline supports actor context**: The turn processing pipeline must
  accept an `actor_id` (or equivalent) that identifies WHO is taking this
  turn. Do not assume the turn-taker is always "the player." Future: different
  actors may have different narrative contexts, permissions, and safety
  profiles.
- **No single-player mutex**: Do not design the turn pipeline with a global
  lock or mutex that assumes only one turn processes at a time per world.
  Future collaborative mode needs concurrent turn processing.
- **Event-sourced history (preferred)**: If feasible, store world state changes
  as an event log rather than mutable snapshots. Collaborative writing needs
  to merge concurrent actions — event sourcing makes conflict resolution
  tractable.

---

## Not in v1

- Multi-player sessions or lobbies
- WebSocket transport
- Real-time collaboration or presence
- Shared world state synchronization
- Character-perspective narrative generation
- Conflict resolution for concurrent actions
- Spectator mode
- Player-to-player communication (chat)
- Matchmaking or party systems
- Asynchronous collaboration workflows

---

## Open Questions

1. What consistency model works for concurrent narrative actions? Last-write-wins
   is wrong for stories — you can't just overwrite narrative. Do we need
   operational transforms or CRDTs for story state?
2. How does the AI narrator handle contradictory player actions? (Player A says
   "I open the door," Player B says "I barricade the door.")
3. What's the right turn model — strict round-robin, free-form with ordering,
   or something else?
4. How do safety checks work in multi-player? One player's crisis shouldn't
   necessarily halt another player's experience — but it might.
5. Does collaborative writing change the therapeutic model? Group therapy is
   fundamentally different from individual therapy.

---

## Related Specs

- **S01 — Core Game Loop**: Turn pipeline that must support multi-actor
- **S04 — World Model**: World state that must support multiple participants
- **S05 — SSE Streaming**: Transport layer that must have a WebSocket migration
  path
- **S06 — Session Model**: Session architecture that must decouple from world
- **S18 — Therapeutic Framework**: Group therapeutic dynamics differ from solo
- **S19 — Crisis & Content Safety**: Multi-player safety has different
  requirements
