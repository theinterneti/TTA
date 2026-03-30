# Skill: retain-to-hindsight

## Purpose

Store a single-topic knowledge artifact to the TTA Hindsight memory bank
for persistent cross-session agent recall.

## When to invoke

After completing any task that produces durable knowledge:

- New architectural decision made
- Bug root-cause identified and fixed
- New module or API surface documented
- Resolved TODO with explanation of how/why
- Design rationale for a non-obvious implementation choice

## How to invoke

Call `mcp__hindsight__retain` with:

| Field | Value |
|-------|-------|
| `bank` | `adam-global` for cross-project patterns; derived `project-*`/`workspace-*` bank for TTA-specific |
| `category` | `architectural-decisions` \| `successful-patterns` \| `implementation-failures` |
| `title` | Short kebab-case topic (e.g. `circuit-breaker-redis-persistence`) |
| `content` | Structured markdown (see Body Format below) |
| `tags` | Array of relevant tags — always include `tta-game` + component tag |
| `severity` | `critical` \| `high` \| `medium` \| `low` |

**Which bank?**
- Use `adam-global` when the insight is reusable beyond TTA (general Python patterns, workflow lessons, tooling preferences)
- Use the derived `project-*`/`workspace-*` bank when the insight is TTA-specific (TTA architecture, crisis detection design, specific module quirks)

## Body format

```markdown
## Context
<1–3 sentences: why this topic matters, what prompted it>

## Decision / Finding
<the actual content — decision, root-cause, API description, etc.>

## Consequences / Next Steps
<what changed as a result, what to watch for, any open follow-up>
```

## Category guidance

| Category | Use when |
|----------|----------|
| `architectural-decisions` | Design choices, technology selection, structural changes |
| `successful-patterns` | Approaches that worked well and should be reused |
| `implementation-failures` | Failed approaches, anti-patterns, debugging lessons |

## Anti-patterns — DO NOT

- Retain more than one distinct topic in a single call — split into multiple retains
- Retain trivial observations (e.g. "ran tests, they passed")
- Paste raw code blocks longer than ~20 lines — reference the source file path instead
- Retain implementation details that are obvious from reading the code

## Recall

To retrieve prior knowledge before starting a task:

```bash
# 1. Cross-project patterns and preferences
mcp__hindsight__recall   # query "adam-global"
# 2. TTA-specific context
mcp__hindsight__recall   # query current derived "project-*" or "workspace-*" bank
# 3. Synthesize into reasoned guidance
mcp__hindsight__reflect
```

## MCP server

Hindsight must be running locally: `uvx --from hindsight-api hindsight-local-mcp`
URL: `http://localhost:8888/mcp/`
