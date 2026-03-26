# Design: Logseq → Hindsight Migration

**Date:** 2026-03-22
**Status:** Approved
**Scope:** Single comprehensive PR — infrastructure, agent configs, skill replacement, cleanup

---

## Overview

Replace TTA's Logseq-backed knowledge workflow with Hindsight, the file-based MCP memory system used by TTA.dev. All agents (Claude Code, Copilot, Cline, Gemini) will use `mcp__hindsight__retain` / `mcp__hindsight__recall` / `mcp__hindsight__reflect` instead of the `tta-notes-kb` MCP and `docs/kb-exports/` staging area. Remove all Logseq references from the codebase.

---

## Section 1: Infrastructure

### `.hindsight/config.yaml` (new file)

TTA gets its own Hindsight config with two persistent banks:

| Bank | Scope | Use |
|------|-------|-----|
| `tta` | TTA-specific, permanent | Architectural decisions, successful patterns, implementation failures |
| `session` | Ephemeral | Current session work-in-progress |

The `tta` bank mirrors the `tta-dev` bank role in TTA.dev: a shared, durable store of project knowledge accessible to all agents.

Include the `indexing`, `retrieval`, and `agents` sections from TTA.dev's `.hindsight/config.yaml` verbatim (these control semantic search behaviour and are required for the MCP server to function correctly). Omit the `tta_integration` and `isolation` blocks — those are TTA.dev-specific (worktree agents, container isolation).

### `.mcp.json` (updated)

Remove: `tta-notes-kb` (points to deprecated `~/repos/TTA-notes/mcp_server.py`)

Add four servers. Use minimal config (no `tags`/`description` fields) — TTA's `.mcp.json` uses a flat format, not TTA.dev's extended metadata format. Do NOT mirror the full TTA.dev suite; only these four servers:

| Server | Command | Purpose |
|--------|---------|---------|
| `hindsight` | `http://localhost:8888/mcp/` | Long-term agent memory (retain/recall/reflect) |
| `codegraphcontext` | `command: /home/adam/.local/bin/cgc`, `args: ["mcp", "start"]` | Code graph analysis, symbol relationships |
| `sequential-thinking` | `npx -y mcp-sequentialthinking-tools` | Multi-step reasoning |
| `github` | docker `ghcr.io/github/github-mcp-server` | GitHub repo operations |

### `.claude/settings.local.json` (updated)

Change `enabledMcpjsonServers` from `["tta-notes-kb"]` to `["hindsight", "codegraphcontext", "sequential-thinking", "github"]`.

---

## Section 2: Agent Config Files

All files get the same change pattern: **replace KB/Logseq workflow with Hindsight session protocol** and remove `**Logseq:** [[...]]` backlink tags.

### `CLAUDE.md`

- Replace "Knowledge Base Access" section with Hindsight session protocol:
  - Session start: `mcp__hindsight__recall` → query `tta` bank
  - Session end (after significant task): `mcp__hindsight__retain` → store decisions, patterns, failures
- Remove all references to `tta-notes-kb`, `docs/kb-exports/`, `create-atomic-note`
- Update Known Issues section (CLAUDE.md currently references Ruff/Pyright errors that `remediation_plan.md` shows are already fixed — keep accurate)

### `AGENTS.md`

- Replace "Knowledge Base Access (MANDATORY)" section with Hindsight protocol (same pattern as CLAUDE.md)
- Remove "Documenting Your Work (MANDATORY)" section (mandated `create-atomic-note` + `docs/kb-exports/`)
- Add single-line retain reminder: after any significant task, `mcp__hindsight__retain` to `tta` bank

### `.github/copilot-instructions.md`

- Remove `**Logseq:** [[TTA.dev/.github/Copilot-instructions]]` tag from the bottom
- Add brief Hindsight memory note under "AI Context Integration" section

### `GEMINI.md`

Full rewrite (currently a redirect stub). New content:
- Session start protocol: `mcp__hindsight__recall` from `tta` bank before any non-trivial task
- Architecture overview: IPA/WBA/NGA pipeline, Redis/Neo4j persistence, multi-agent design
- Quality gate commands (ruff, pyright, pytest)
- L0/TTA.dev boundary rule (do not build second developer-agent system in TTA)
- Session end: `mcp__hindsight__retain` reminder
- Standards quick reference (uv, Python 3.12+, Conventional Commits)

---

## Section 3: Skill Replacement

### `.claude/skills/create-atomic-note/SKILL.md` (full rewrite)

The skill is renamed in behavior to `retain-to-hindsight` but the directory and invocation path (`.claude/skills/create-atomic-note/`) remain unchanged so existing `/create-atomic-note` invocations continue to work.

**New behavior:**
- Trigger conditions: same as before (significant task complete, architecture decision, bug root-cause, resolved TODO)
- Action: call `mcp__hindsight__retain` with:
  - `bank`: `tta`
  - `category`: one of `architectural-decisions`, `successful-patterns`, `implementation-failures`
  - `title`: short kebab-case topic
  - `content`: structured markdown — `## Context`, `## Decision / Finding`, `## Consequences / Next Steps`
- No file writes. No frontmatter schema. No `docs/kb-exports/` path.

**Anti-patterns (same discipline as before):**
- One topic per retain call — split complex work
- Do not retain trivial observations
- Include code references (file paths) rather than pasting large code blocks

---

## Section 4: Cleanup

### Deletions

| File | Reason |
|------|--------|
| `scripts/logseq_graph_agent.py` | Entire purpose is Logseq sync — no value without Logseq |
| `kb_migration_plan.md` | Documents a Logseq migration; fully superseded by this migration |

### Logseq reference removal (strip, not delete)

Strip `**Logseq:** [[...]]` tags and any Logseq-specific guidance from:

- `docs/README.md`
- `docs/reference/kb-access-guide.md`
- `docs/reports/tta-spec-audit-report.md`
- `docs/development/reorg/tta-separation-roadmap.md`
- `docs/status/todo-audit.md`
- `scripts/cleanup/organize-repo-phase3.sh`
- `scripts/todo-audit.py`
- `.github/chatmodes/safety-architect.chatmode.md`
- `.github/chatmodes/backend-implementer.chatmode.md`

---

## Out of Scope

- Migrating existing content from `TTA-notes` Logseq pages into Hindsight banks — that is a manual human task
- Modifying `docs/kb-exports/` existing files — leave them as-is, just stop adding new ones
- TTA.dev's own Logseq tags (separate repo, separate migration)
- Adding the full TTA.dev MCP suite beyond the four specified servers

---

## Success Criteria

- The following command returns zero results:
  ```bash
  grep -r "logseq\|Logseq" /home/adam/Repos/TTA \
    --include="*.md" --include="*.py" --include="*.sh" \
    --include="*.json" --include="*.yaml" \
    --exclude-dir=".archive" --exclude-dir="_archive" --exclude-dir=".git"
  ```
- `.mcp.json` contains `hindsight`, `codegraphcontext`, `sequential-thinking`, `github`; does not contain `tta-notes-kb`
- `.hindsight/config.yaml` exists with `tta` and `session` banks configured
- All four agent entry points (CLAUDE.md, AGENTS.md, copilot-instructions.md, GEMINI.md) reference Hindsight and contain no Logseq references
- `.claude/skills/create-atomic-note/SKILL.md` instructs agents to use `mcp__hindsight__retain`
- `scripts/logseq_graph_agent.py` and `kb_migration_plan.md` are deleted
- Quality gate passes: `uv run ruff check src/ && uv run pyright src/ && uv run pytest -q -m "not integration and not neo4j and not redis" tests/`
