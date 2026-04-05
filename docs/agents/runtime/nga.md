# NGA — Narrative Generation Agent

## What NGA does

Receives `ProcessedInput` (from IPA) + `WorldContext` (from WBA) and generates
the therapeutic narrative streamed back to the player.

## System prompt location

`src/components/nga/agent.py` — `_SYSTEM_PROMPT` constant at line 52.

**Do not hardcode this prompt elsewhere.** Edit it only in that file.

## Current prompt behaviour

- Writes 2–4 short paragraphs of vivid, present-tense narrative
- Honours the player's intent and emotional tone
- Grounds narrative in world facts from WorldContext
- Gives NPCs brief moments of life when present
- Never lectures, diagnoses, or breaks the fictional frame
- Applies extra warmth and gentleness when `safety_signal=true`
- Ends with a subtle open invitation to continue

## Guide voice injection

The NGA system prompt can be prepended with a guide voice instruction block,
injected by `GuidePromptBuilder` from `src/components/guide/prompt.py`.
This shapes the narrative voice to match the player's personalized guide character.

## Architecture

```
NGAAgent.generate(processed_input, world_context)
  └── _NGALLMCall — LLM call with assembled system + user message
        wrapped in FallbackPrimitive(RetryPrimitive(...))
```

## Extending NGA

- To change narrative style: edit the system prompt + test with therapeutic content review
- To add guide voice profiles: update `GuidePromptBuilder` + add narrator voice profiles
- Any prompt change requires safety review — see `docs/agents/dev/safety.md`
