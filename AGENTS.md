# AGENTS.md — Universal Agent Context

This file is the shared entry point for all AI agents operating in the TTA
repository. Read this before acting.

## What This Repo Is

**Therapeutic Text Adventure (TTA)** — An AI-powered narrative game for mental
health support. Players make choices that branch the story; a therapist/editorial
layer curates which paths are safe and effective.

**TTA.dev** (`/home/thein/repos/TTA.dev`) provides reusable platform primitives.

## Agent Roster

| Agent | Role | Config |
|---|---|---|
| **Claude Code** | Main agent — primary decision maker | `CLAUDE.md` |
| GitHub Copilot | IDE suggestions | `.github/copilot-instructions.md` |
| Augment | Code intelligence | `.augment/instructions.md` |
| Cline | AI coding assistant | `.cline/instructions.md` |
| Gemini | Secondary review | `GEMINI.md` |

## Knowledge Base Access (MANDATORY)

Before executing any non-trivial task, query the `tta-notes-kb` MCP server:

1. Use `search_kb` to find relevant architectural decisions, prior work, and
   design rationale for the area you are about to change.
2. Use `get_high_priority_todos` to check for open work items related to your task.

The `tta-notes-kb` server runs from `/home/thein/repos/TTA-notes/mcp_server.py`
and is configured in `.mcp.json` (Claude Code) and
`.vscode/notebooklm-mcp-config.json` (VS Code).

Do NOT rely solely on code inspection or this file for project context — the KB
is the canonical source of architectural truth.

## Non-Negotiable Standards

- **Python**: 3.12+ only
- **Package manager**: `uv` — never `pip install`
- **Type hints**: `str | None` not `Optional[str]`
- **Line length**: 88 chars (Ruff)
- **Type checking**: Pyright `standard` mode
- **Commits**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`)
- **Tests**: pytest `asyncio_mode = "auto"`; integration tests use `@pytest.mark.integration`

## Quality Gate (run before committing)

```bash
uv run ruff check src/ --fix
uv run ruff format src/
uv run pyright src/
uv run pytest -q -m "not integration and not neo4j and not redis" tests/
```

## Documenting Your Work (MANDATORY)

After completing any significant task (new feature, architecture decision, bug
root-cause, resolved TODO), invoke the `create-atomic-note` skill:

1. Create a new file in `docs/kb-exports/` following the naming convention and
   frontmatter schema defined in `.claude/skills/create-atomic-note/SKILL.md`.
2. Keep the note to a single topic — split complex work into multiple notes.
3. The repo owner will ingest these files into `TTA-notes` manually.
