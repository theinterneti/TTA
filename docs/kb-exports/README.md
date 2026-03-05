# docs/kb-exports/

This directory is the **Atomic Notes staging area** for the TTA project.

## Contract

- **Agents write here.** After completing a significant task, agents save a single-topic
  Markdown file here using the `create-atomic-note` skill.
- **Humans ingest from here.** The repo owner periodically imports these files into the
  `TTA-notes` Knowledge Base repository.
- **Never edit existing files here.** Create new ones instead — notes are immutable
  once written.

## File naming

```
YYYY-MM-DD_<kebab-case-topic>.md
```

Example: `2026-03-04_unit-of-work-pattern.md`

## Required frontmatter

Every file must begin with YAML frontmatter. See the full schema in
`.claude/skills/create-atomic-note/SKILL.md`.

## What does NOT belong here

- Large data dumps or logs
- Temporary debugging notes
- Files larger than ~300 lines (split into multiple notes instead)
