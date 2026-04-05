# IPA — Input Processing Agent

## What IPA does

Classifies player intent, extracts named entities, detects emotional tone, and
sets safety signals. Produces a `ProcessedInput` fed into the WBA.

## System prompt location

`src/components/ipa/agent.py` — `_SYSTEM_PROMPT` constant at line 58.

**Do not hardcode this prompt elsewhere.** Edit it only in that file.
To version it via the prompt registry, see `docs/agents/runtime/prompt-registry.md`.

## Current prompt behaviour

- Classifies intent: `explore | interact | query | action | journal | unknown`
- Extracts entities with type and confidence score
- Detects emotional tone (primary + intensity)
- Sets `safety_signal=true` for self-harm, crisis, or severe distress language
- Returns structured JSON only — no prose

## Fallback behaviour

On LLM failure, IPA returns `_FALLBACK_RESULT`:
```python
{"intent": "unknown", "intent_confidence": 0.5, "entities": [],
 "emotional_tone": {"primary": "neutral", "intensity": 0.0, "safety_signal": False},
 "normalized_text": ""}
```

## Architecture

```
IPAAgent.process(raw_text)
  └── _IPACall — LLM call → IntentClassification JSON
        wrapped in FallbackPrimitive(RetryPrimitive(...))
```

## Extending IPA

- To add a new intent type: update `Intent` enum in `src/components/ipa/models.py` + update the system prompt
- To add an entity type: update `ExtractedEntity.entity_type` + update the system prompt
- Always update tests in `tests/unit/components/ipa/`
