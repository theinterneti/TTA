# Skill: create-atomic-note

## Purpose

Save a single-topic documentation artifact to `docs/kb-exports/` for later
ingestion into the TTA-notes Knowledge Base.

## When to invoke

After completing any task that produces durable knowledge:

- New architectural decision made
- Bug root-cause identified and fixed
- New module or API surface documented
- Resolved TODO with explanation of how/why
- Design rationale for a non-obvious implementation choice

## File naming convention

```
docs/kb-exports/YYYY-MM-DD_<kebab-case-topic>.md
```

Example: `docs/kb-exports/2026-03-04_unit-of-work-pattern.md`

## Required YAML frontmatter

Every atomic note MUST begin with this block (all fields required):

```yaml
---
type: <architecture|decision|bug-fix|todo-resolved|api-doc|narrative-design>
priority: <high|medium|low>
tags: [tta-game, <domain-tag>, <component-tag>]
date: YYYY-MM-DD
source_files:
  - src/path/to/relevant/file.py
related_notes: []
---
```

### Field guidance

| Field | Allowed values | Notes |
|-------|----------------|-------|
| `type` | `architecture`, `decision`, `bug-fix`, `todo-resolved`, `api-doc`, `narrative-design` | Pick exactly one |
| `priority` | `high`, `medium`, `low` | High = referenced often or blocks other work |
| `tags` | array of strings | Always include `tta-game`; add component tags e.g. `player-experience`, `llm-factory`, `dolt`, `redis`, `narrative-engine`, `unit-of-work`, `mcp` |
| `date` | ISO-8601 (`YYYY-MM-DD`) | Today's date |
| `source_files` | repo-relative paths | Files most relevant to this note |
| `related_notes` | filenames in `docs/kb-exports/` | Other atomic notes this connects to (empty list if none) |

## Body format

After frontmatter: plain Markdown, **max ~300 lines**.

Use this structure:

```markdown
## Context
<1–3 sentences: why this topic matters, what prompted it>

## Decision / Finding
<the actual content — the architectural decision, bug root-cause, API description, etc.>

## Consequences / Next Steps
<what changed as a result, what to watch for, any open follow-up questions>
```

## Anti-patterns — DO NOT

- Write more than one distinct topic per file — split into multiple notes instead
- Omit or partially fill the YAML frontmatter
- Use Logseq wiki-links (`[[...]]`) — this staging area is not a Logseq graph
- Paste raw code blocks longer than ~40 lines — reference the source file path instead
- Edit an existing atomic note — always create a new one
