# Knowledge Base Access Guide

TTA uses **Hindsight** for agent memory and architectural knowledge.

## Accessing Knowledge

### For AI Agents (MCP)

```bash
# Recall relevant context before a task
mcp__hindsight__recall   # query "tta" bank

# Reflect on accumulated patterns
mcp__hindsight__reflect  # synthesize guidance

# Store new knowledge after a task
mcp__hindsight__retain   # write to "tta" bank
```

**MCP server:** `http://localhost:8888/mcp/`
**Start server:** `uvx --from hindsight-api hindsight-local-mcp`

### Memory Banks

| Bank | Type | Contents |
|------|------|---------|
| `tta` | Persistent | Architectural decisions, patterns, failure lessons |
| `session` | Ephemeral | Current session work-in-progress |

### Categories in `tta` bank

| Category | When to use |
|----------|-------------|
| `architectural-decisions` | Design choices, technology selection |
| `successful-patterns` | Approaches worth reusing |
| `implementation-failures` | Anti-patterns, debugging lessons |

## Writing a Memory

Use the `create-atomic-note` skill (rewired to Hindsight):
- One topic per retain call
- Structure: `## Context`, `## Decision / Finding`, `## Consequences / Next Steps`
- Always include `tta-game` tag plus a component tag

## Memory Files Location

`.hindsight/banks/tta/` — persistent memories (git-tracked)
`.hindsight/banks/session/` — ephemeral (gitignored)
