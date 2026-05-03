# S20 — Story Sharing

> **Status**: 📝 Stub (Future)
> **Level**: 5 — Future Vision
> **Dependencies**: S03 (Narrative Engine), S06 (Session Model)
> **Last Updated**: 2025-07-24

---

## Vision

Story Sharing lets players export and share their adventures as readable
narratives. A completed (or in-progress) story is not a chat log — it is a
formatted, coherent narrative with chapters, character voices, and dramatic
structure. Players can share stories publicly, with friends, or export them as
personal keepsakes.

Beyond export, Story Sharing enables social discovery: featured stories,
genre-based browsing, recommendations, and community curation. A player who
finishes a compelling horror adventure can share it as a short story that others
read for enjoyment — or as inspiration to start their own adventure in that
world. Stories become the social currency of the TTA community.

---

## v1 Constraints

What v1 MUST accommodate so this feature remains viable:

- **Structured conversation history**: Conversation history must be stored in a
  structured format (not opaque text blobs) that distinguishes narrator voice,
  player input, NPC dialogue, and system events. Future story formatting needs
  to know WHO said WHAT.
- **Clean narrative prose**: The narrative engine's output should be clean prose
  suitable for reading. Avoid embedding system metadata, markdown artifacts, or
  control tokens in the narrative text that a reader would see. Keep metadata
  in a separate channel/field.
- **Story arc tracking**: The session model should capture enough structure to
  identify story arcs — at minimum, mark session boundaries and major narrative
  beats. Future excerpt generation needs to know where "chapters" begin and
  end.
- **Consent-aware data model**: The session/player model should include a field
  for sharing consent. Never assume all content is shareable — players must
  opt in per story. Design the model so `sharing_status` (private/friends/
  public) can be added without migration.
- **Deterministic replay**: Given the same conversation history, the system
  should be able to reconstruct the story. Don't rely on ephemeral state that
  disappears after a session ends.

---

## Not in v1

- Story export (PDF, ePub, or any format)
- Public story feeds or discovery
- Story recommendations or curation
- Social features (likes, comments, follows)
- Story formatting or chapter generation
- Privacy controls for shared stories
- Content moderation for shared stories
- Featured stories or editorial curation
- Story remix or branching from shared stories

---

## Open Questions

1. What is the right unit of sharing — a full session, a story arc spanning
   multiple sessions, or player-selected excerpts?
2. How do we handle stories that contain sensitive therapeutic content? The
   therapeutic framework (S18) may produce deeply personal narratives that
   should never be shared.
3. Should AI-generated narrative be attributed differently from player-written
   input in a shared story?
4. What copyright model applies? Is the story the player's, the AI's, or
   shared? This has legal implications for sharing.
5. How do we prevent sharing from becoming a vector for harmful content
   distribution?

---

## Related Specs

- **S03 — Narrative Engine**: Produces the prose that becomes shareable stories
- **S06 — Session Model**: Stores the conversation history that stories are
  built from
- **S18 — Therapeutic Framework**: Therapeutic stories need special sharing
  rules
- **S19 — Crisis & Content Safety**: Shared stories need content moderation
- **S22 — Community**: Story sharing is a community feature
