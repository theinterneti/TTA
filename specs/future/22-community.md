# S22 — Community

> **Status**: 📝 Stub (Future)
> **Level**: 5 — Future Vision
> **Dependencies**: S04 (World Model), S06 (Session Model), S20 (Story Sharing)
> **Last Updated**: 2025-07-24

---

## Vision

Community transforms TTA from a single-player tool into a platform. Players
create, share, and discover content: world templates, genre packs, custom
prompts, NPC personalities, and story seeds. Think Steam Workshop for text
adventures — a marketplace of creativity where the best community content
surfaces through curation, ratings, and editorial features.

The community layer includes player identity (public profiles, play history,
authored content), social features (following, recommendations, collections),
content management (publishing, versioning, moderation), and discovery (search,
categories, featured content, algorithmic recommendations). It turns every
creative player into a potential world-builder and every world-builder into a
community contributor.

---

## v1 Constraints

What v1 MUST accommodate so this feature remains viable:

- **Portable content format**: Content assets — world templates, genre
  definitions, system prompts, NPC configurations — must be stored in a
  self-contained, serializable format (JSON, YAML, or similar). Do not embed
  content in code or database schemas that can't be exported. Future community
  sharing needs to package and transfer these assets.
- **Player identity extensibility**: The player/auth model should support
  adding public profile fields later (display name, bio, avatar, authored
  content). Do not design auth as "just a session token" — it should be a
  foundation for player identity.
- **Parameterized world generation**: World creation must be driven by
  configuration/parameters, not hardcoded logic. Future community templates
  are just parameter sets that anyone can author. If world generation takes
  a config dict, community templates are trivial to add later.
- **Content has metadata**: Every content asset (prompt, template, genre pack)
  should carry metadata: author, version, description, tags. This is the
  foundation for future search, discovery, and attribution.
- **Separation of engine and content**: The narrative engine must be cleanly
  separated from the content it operates on. The engine is platform; content
  is community. Don't couple them.

---

## Not in v1

- Public player profiles or social identity
- Content publishing or sharing workflows
- Community content discovery or search
- Ratings, reviews, or curation systems
- Content moderation tools or policies
- User-generated world templates or genre packs
- Content versioning or update mechanisms
- Creator analytics or metrics
- Monetization or creator economy features
- Forums, comments, or social communication
- Recommendation algorithms
- Editorial or featured content programs
- Content licensing or rights management
- Abuse reporting or trust & safety tooling

---

## Open Questions

1. What's the right content packaging format? A world template needs prompts,
   NPC configs, genre settings, and possibly custom assets — how are these
   bundled?
2. How do we handle content quality? Community content ranges from brilliant to
   broken. Do we need a review/approval process, or is rating-based surfacing
   sufficient?
3. What moderation model works for AI-adjacent content? A world template itself
   might be benign, but the AI content it generates could be harmful.
4. Should community content be free, paid, or both? What's the creator
   incentive model?
5. How does therapeutic content (S18) interact with community content? Should
   clinician-authored therapeutic templates be a special category?
6. What's the IP model for community content — does the platform have rights,
   or does the creator retain full ownership?

---

## Related Specs

- **S04 — World Model**: World structure that community templates will define
- **S06 — Session Model**: Player identity foundation for community profiles
- **S18 — Therapeutic Framework**: Clinician-authored content may be a community
  category
- **S19 — Crisis & Content Safety**: Community content needs safety review
- **S20 — Story Sharing**: Shared stories are community content
- **S21 — Collaborative Writing**: Collaborative worlds may be community-shared
