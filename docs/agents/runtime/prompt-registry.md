# Prompt Registry

The prompt registry provides versioned, metrics-tracked prompt management.

## Location

`src/ai_components/prompts/` — `PromptRegistry`, `PromptTemplate`, `PromptMetrics`

## Active versions

Versioned YAML files live in `src/ai_components/prompts/versions/v1.0.0/`.
Active versions are symlinked from `src/ai_components/prompts/active/`.

Current active versions:
- `narrative_generation.yaml` — NGA narrative generation prompt
- `safety_check.yaml` — safety classification prompt

## YAML format

```yaml
name: narrative_generation
version: "1.0.0"
description: "NGA main narrative generation prompt"
template: |
  You are the narrator of a therapeutic text adventure...
variables:
  - world_context
  - player_intent
```

## Adding a new prompt version

1. Create `src/ai_components/prompts/versions/v<X.Y.Z>/<prompt_name>.yaml`
2. Test against the full NGA pipeline with `make test`
3. Update the symlink in `active/` to point to the new version
4. Retain the old version — never delete versioned prompts

## Promoting to active

```bash
cd src/ai_components/prompts/active
ln -sfn ../versions/v<X.Y.Z>/<name>.yaml <name>.yaml
```
