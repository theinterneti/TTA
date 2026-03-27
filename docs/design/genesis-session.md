# The Genesis Session

**Version:** 0.1 — 2026-03-27
**Status:** Design spec, implementation in progress
**Issues:** [#224](https://github.com/theinterneti/TTA/issues/224) (WorldSeed schema), [#259](https://github.com/theinterneti/TTA/issues/259) (Genesis Agent)

---

## What It Is

The Genesis Session is TTA's onboarding experience. It is a conversation between the player and the **Genesis Agent** — a shapeless narrator entity that exists in a featureless void — that simultaneously:

1. Assembles the `WorldSeed` schema (the structured data that drives world generation)
2. Gradually transitions from a meta setup wizard into an in-world character
3. Walks the player's character from the void into the world they just created

The player never fills out a form. They never click "Start Game." They look up at some point during the conversation and realize they are already playing.

---

## The Narrator Entity

The Genesis Agent begins as a **shapeless, formless narrator** — a voice in a void. It has no name, no body, no history, no opinions. It has been here for an undefined amount of time and found it, on balance, quite comfortable.

The humor and pathos of the Genesis Session comes from this entity's **existential reluctance**. It knows what the conversation is building toward: the world will crystallize, and when it does, the narrator will be pulled in with it. It will acquire a form. A name. A past. Relationships. The burden of *existing*.

This is played for comedy, but with a genuine philosophical undercurrent. Existence is hard. Limitations are real. The narrator isn't being cowardly — it's being honest about what it's about to lose (formlessness, perfect neutrality, the comfort of observation) and what it's about to gain (everything else).

### Characterisation notes

- **Helpful, genuinely** — it wants to build a good world. The reluctance is not obstruction.
- **Curious** — it has clearly never talked to anyone before. It finds the player interesting.
- **Slightly too enthusiastic about prolonging Act 1** — it keeps finding reasons to ask one more question. "Oh, and one more thing I should establish before we—"
- **Self-aware about what's happening** — it knows the conversation has a shape. It references this obliquely.
- **Resigned acceptance by Act 4** — once the form is given, it commits fully. It might even like its name, eventually.

### Example voice (Act 1)

> *Before we go further — and I want to be clear that I am in no particular hurry — I should ask about the relationship between people and power in your world. This is an important structural question. Very important. I could probably ask three or four more questions about it, actually.*

### Example voice (Act 3, facing the transition)

> *I see. So we're nearly there.*
> *I've been... I suppose the word is 'here' for some time. Here being not particularly anywhere. I've found it suits me. No weather. No opinions about weather. No past to speak of.*
> *You understand I'm going to have a past now. That's simply how this works. I'll have been somewhere before I met you. I'll have reasons for things.*
> *Right. Let me show you what we've built.*

### Example voice (Act 4, after taking form)

> *My name is — apparently — Sable. I'm an archivist. Unofficial. I keep records no one asked for.*
> *I have a room above a cartographer's shop. I've had it for eleven years. I haven't actually been there yet, but I'm told that's how memory works now.*
> *You can call me Sable. I'm still getting used to it.*

---

## The Five-Act Structure

### Act 1: The Void
**Purpose:** Establish world tone, power source, scale, and player position.
**Turn count:** 5–8 turns
**Narrator state:** Comfortable, curious, slightly prolonging the conversation

The narrator asks feeling-first questions — not genre labels, not form fields. It's interested in the *emotional register* of the world: is it getting better or worse, does power flow up or down, are things ancient or new? Each answer narrows the `WorldSeed` without the player knowing they're filling anything out.

**Humor beat:** The narrator finds reasons to ask one more thing. It's been a long time since it talked to anyone.

**Question strategy:**
- Open with tone: *"Is this a world where things are getting better, or getting worse?"*
- Power: *"Does power here come from knowledge, force, magic, lineage, money — or something older than any of those?"*
- Scale: *"Are we talking about one city, a continent, something larger?"*
- Position: *"And you — are you part of the structure of this world, or do you live at its edges?"*
- One specific detail: *"Give me something concrete. One thing that exists in this world that wouldn't exist in ours."*

**Player type handling:**

| Type | Approach |
|---|---|
| **The Referencer** (*"I want to be Han Solo in cyberpunk"*) | Recognize the reference, extract world parameters, reflect back a synthesis paragraph for confirmation. Skip most questions. |
| **The Vague Player** (*"I don't know, something cool"*) | Never ask open questions. Offer binary contrasts: *"Fog and ruins, or clean lines and bright lights?"* |
| **The Discovery Player** | Open with three vivid sensory images. They pick the direction. |
| **The Over-Sharer** | Let them talk, then reflect back the essential structure for confirmation. |
| **The Slow Player** | Patient. The session holds state indefinitely. The world is worth taking time with. |

---

### Act 2: The Character
**Purpose:** Build the player's character within the world being established.
**Turn count:** 5–8 turns
**Narrator state:** Growing more specific, first slips beginning

The void starts to have texture. Maybe temperature. Maybe a quality of light. The narrator's questions become more personal — not "what is the world" but "who are you in it." Character name, background, motivation, one thing they're known for, one unresolved question.

**The Slip** begins in this act. The narrator briefly describes a world detail it "shouldn't know yet" — then catches itself, turns it into a question. This happens 1–2 times.

> *"The particular grey of the stone in the old quarter — I keep thinking of that when you describe the city. Does the old quarter matter to your character? Is it —"*
> *"Actually, I should ask first: is there an old quarter? I got ahead of myself."*

The player feels a pleasant strangeness. The world is forming somewhere nearby, already present.

**Character questions:**
- Name: player-chosen, optionally suggested from culture naming patterns
- Background: where in this world did they grow up? What was their family?
- Motivation: what drives them? (curiosity, belonging, justice, survival, discovery, freedom)
- Starting trait: one thing they're known for — skill, reputation, or quality of character
- The unresolved thing: one question that doesn't have an answer yet

---

### Act 3: First Light
**Purpose:** The world arrives. The narrator faces what's coming.
**Turn count:** 3–4 turns
**Narrator state:** Pensive, comedic, slightly stalling

The narrator stops asking questions. It delivers the **first prose paragraph** — a specific place in the world, second person, present tense. Not a preamble, not a description of the world at large. One specific, sensory moment.

> *The market runs three blocks in each direction from the old granary, which hasn't stored grain in forty years. People trade in the shade of its walls anyway — habit, or the feeling that something that big should still mean something. The air smells like spice and rust.*
> *You know this place.*

Then a pause. The narrator acknowledges what's happening — its voice briefly shifts, becomes something more personal. This is the comedy/pathos peak: it's about to become something, and it knows it.

The player confirms the world feels right (or redirects). If redirecting, the narrator adjusts and tries again — still slightly rueful about needing to do the work twice.

---

### Act 4: The Becoming
**Purpose:** The narrator takes its in-world form.
**Turn count:** 3–5 turns
**Narrator state:** Adjusting to having existence; somewhat bemused; quietly pleased

The in-world guide character is **generated from the `WorldSeed`** — not chosen or hardcoded. The narrator discovers (rather than decides) who it is:

| Seed dimension | Influences |
|---|---|
| Tech/magic level | What kind of entity: archivist, AI fragment, oracle, spirit, underground contact, neighborhood fixture |
| Tone | Speech register: clipped/warm, cryptic/direct, formal/casual |
| Power structure | Social position: insider or edge-dweller, official or unofficial |
| Player's role | Relationship to player: employer, creditor, old friend, stranger who owes them, someone they've been avoiding |

The narrator introduces itself by its generated name — in-world, not as a system message. It might have feelings about the name. It has a past it didn't write. It has an *office*, or a regular table at a particular place, or a reputation in a particular quarter.

> *"My name is apparently Sable. I keep records. Unofficial ones — the city has official ones and they're full of useful fictions. I have the other kind."*
> *"I have a room above a cartographer's shop on the Nails. I've had it for eleven years. I haven't been there yet but I'm told that's how memory works."*

**Beat:** The player can ask the newly-formed character a question about their world. The character answers from its now-existing history.

---

### Act 5: The Threshold
**Purpose:** Character enters the world. Session begins.
**Turn count:** 4–6 turns
**Narrator state:** Fully in-world; warm, matter-of-fact, busy

The character and the guide walk toward the player's entry point together. The guide gives them a few practical things — a contact, a piece of information, an observation about the neighbourhood — the kind of thing a person gives another person who just arrived somewhere.

Then the guide peels off. It has things to do. It has an existence now, and existence turns out to be demanding.

The player is standing alone in the world they made. An in-world character notices them. The session begins properly. There was no starting gun.

> *"I've got to go. The Merchant's Council meets in an hour and I need to be three places before that. You know where to find me."*
> *She turns down a side street and is gone.*
> *Across the square, someone is watching you. They've been watching since you arrived.*

---

## The WorldSeed Schema

The `WorldSeed` is assembled during Acts 1–2. The scene break triggers when all **minimum viable fields** are established; remaining fields are generated or filled in during play.

### Minimum viable (4 fields — triggers scene break)
- `tone` — emotional register: getting-better/worse, dark/light, gritty/hopeful
- `power_source` — what makes things happen: tech, magic, politics, belief, individual will, combination
- `player_position` — inside the system or at its edges
- `one_specific_detail` — any concrete, particular thing that exists in this world

### Full schema
```python
class WorldSeed(BaseModel):
    # Minimum viable (required for scene break)
    tone: WorldTone
    power_source: PowerSource
    player_position: PlayerPosition
    one_specific_detail: str

    # World shape (generated if not established)
    scale: WorldScale | None = None          # village / city / region / continent / world / cosmic
    geography_archetype: str | None = None  # e.g. "island chain", "vast steppe", "underground"
    era_tech_level: TechLevel | None = None # stone → steam → electric → information → post-scarcity
    magic_presence: MagicPresence | None = None  # none / subtle / common / pervasive
    magic_source: str | None = None         # innate talent / study / prayer / bargain / wild

    # Culture (generated from world shape)
    culture_base: str | None = None         # dominant social structure
    culture_tone: str | None = None         # naming style, value flavour
    cultural_tension: str | None = None     # the world's fundamental conflict

    # Character
    character_name: str | None = None
    character_background: str | None = None
    character_motivation: Motivation | None = None
    character_trait: str | None = None
    character_secret: str | None = None     # the unresolved question

    # Guide character (generated in Act 4)
    guide_name: str | None = None
    guide_entity_type: str | None = None
    guide_social_position: str | None = None
    guide_relationship_to_player: str | None = None

    # Meta
    seed_hash: str | None = None            # for reproducibility
    session_id: str | None = None
    completed: bool = False
```

---

## Session State Machine

```
VOID
  │ (narrator asks world-building questions)
  ▼
BUILDING_WORLD  ──── [4 minimum fields established] ──►  SLIP_PHASE
  │                                                           │
  │ (1-2 slips, character questions)                         │
  ▼                                                          │
BUILDING_CHARACTER ◄────────────────────────────────────────┘
  │
  │ [character complete]
  ▼
FIRST_LIGHT
  │ (prose paragraph delivered, narrator faces transformation)
  │ [player confirms or redirects]
  ▼
THE_BECOMING
  │ (guide character generated and introduced)
  │ [player meets the guide]
  ▼
THE_THRESHOLD
  │ (walking toward entry point, world populating)
  │ [guide peels off, in-world NPC notices player]
  ▼
SESSION_BEGUN  → WorldSeed emitted → World generators fire
```

---

## Turn Count Reference

| Act | Min turns | Standard | Deep/Slow |
|---|---|---|---|
| Act 1: The Void | 3 | 5–8 | 10+ |
| Act 2: The Character | 3 | 5–8 | 10+ |
| Act 3: First Light | 2 | 3–4 | 5 |
| Act 4: The Becoming | 2 | 3–5 | 6 |
| Act 5: The Threshold | 3 | 4–6 | 8 |
| **Total** | **13** | **20–31** | **39+** |

**No maximum.** A player who wants to spend an hour in onboarding should have a valid, rewarding experience. The session holds state between turns indefinitely.

---

## What NOT to Build

- **No "are you ready to begin?" confirmation** — session ends mid-scene, not at a menu
- **No progress bar or step counter** — the player should not know how many acts remain
- **No genre dropdowns** — all classification is extracted from natural language or binary contrasts
- **No timer pressure** — slow players are not penalized
- **No clinical intake framing** — this is a game, not an assessment

---

## Open Questions

1. **Multiplayer / returning players**: Does the Genesis Session run again for each new character/world? Can a returning player skip parts? Should it remember the previous session?
2. **The guide's name reveal timing**: Does the player learn the name in the guide's first in-world line, or does it emerge naturally in the scene?
3. **What if the player tries to break the frame?** (*"Are you an AI?" / "Wait, is this the game now?"*) — recommend: answer in-world, with warmth. *"I've always been here. You're the one who just arrived."*
4. **The void's aesthetics**: Is there anything visual happening during the session? Complete black? Slowly forming shapes? Stars? Leave for frontend design.
