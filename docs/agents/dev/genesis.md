# Genesis System Reference

Genesis is TTA's metamorphic onboarding system — the first session experience
that transforms a neutral world into a personalized therapeutic narrative.

Related issues: #224, #259

## What Genesis does

1. **Seed extraction** — extracts meaningful themes from player's opening input
2. **Guide generation** — creates a personalized in-world guide character from the seed
3. **World personalization** — shapes the starting world state around the player's seed
4. **Narrator voice selection** — picks the appropriate narrative voice profile

## Architecture

Located at `src/components/genesis/`.

```
GenesisSession
  ├── SeedExtractor        — extracts WorldSeed from player input (ChatPrimitive)
  ├── GuideGenerator       — derives guide character from seed (ChatPrimitive)
  └── GenesisSessionState  — tracks 5-act onboarding progress
```

The Genesis agent uses `ChatPrimitive` (from TTA.dev) for all LLM calls.
The narrator adapter is passed into `derive_guide_character`.

## Narrator voice profiles

Narrator voices are defined separately from the guide character. They shape
the narrative style: tone, vocabulary, warmth level, metaphor density.

## 5-act structure

| Act | What happens |
|---|---|
| 1. BUILDING_WORLD | Player arrives; neutral world established |
| 2. SLIP_PHASE | Opening prompt; seed extraction |
| 3. BUILDING_CHARACTER | Guide character introduced |
| 4. FIRST_LIGHT | World begins to reflect player's seed |
| 5. THE_BECOMING | Transition to main game loop |

Terminal states: THE_THRESHOLD, SESSION_BEGUN

## Development rules

- Guide generation failure must fall back gracefully — use `FallbackPrimitive`
- Seeds should be abstract enough to personalise without being clinically diagnostic
- Never store raw seed text permanently without user consent
- Genesis state transitions are idempotent — re-running an act must be safe
