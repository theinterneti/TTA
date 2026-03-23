# Logseq → Hindsight Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace TTA's Logseq-backed knowledge workflow with Hindsight MCP memory, remove all Logseq references, and modernize the agent config stack.

**Architecture:** File-based `.hindsight/banks/tta/` replaces `docs/kb-exports/` as the agent memory store. Agents call `mcp__hindsight__retain` / `mcp__hindsight__recall` instead of writing files or querying `tta-notes-kb`. The `create-atomic-note` skill is rewired to Hindsight retain; all agent config files get a consistent session protocol.

**Tech Stack:** Hindsight MCP (`uvx --from hindsight-api hindsight-local-mcp` at `http://localhost:8888/mcp/`), CodeGraphContext (`cgc`), GitHub MCP (docker), sequential-thinking (npx). No Python source changes — this is entirely config/docs/skills.

---

## Pre-flight Check

**IMPORTANT:** There are already uncommitted changes in the working tree (L0 sections added to `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`). All tasks below preserve and build on those changes. Do NOT stash or discard them.

```bash
git -C /home/adam/Repos/TTA diff --stat HEAD
# Expected: 3 files changed, 51 insertions
```

Reference config: `/home/adam/Repos/TTA.dev/.hindsight/config.yaml` and `/home/adam/Repos/TTA.dev/.mcp/config.json`

---

## File Map

| Action | Path | What changes |
|--------|------|-------------|
| **Create** | `.hindsight/config.yaml` | Hindsight memory bank config (tta + session banks) |
| **Create** | `.hindsight/banks/tta/index.json` | Empty bank index |
| **Create** | `.hindsight/banks/session/` | Session bank directory (gitkeep) |
| **Create** | `.hindsight/banks/tta/architectural-decisions/2026-03-22-hindsight-adoption.memory.md` | Seed memory for this migration |
| **Modify** | `.mcp.json` | Swap `tta-notes-kb` → hindsight + codegraphcontext + sequential-thinking + github |
| **Modify** | `.claude/settings.local.json` | Update `enabledMcpjsonServers` |
| **Modify** | `CLAUDE.md` | Add Hindsight session protocol; update stale Known Issues |
| **Modify** | `AGENTS.md` | Replace KB Access section; remove create-atomic-note mandate |
| **Modify** | `GEMINI.md` | Full rewrite with real content + session protocol |
| **Modify** | `.github/copilot-instructions.md` | Remove Logseq tag; add Hindsight note |
| **Rewrite** | `.claude/skills/create-atomic-note/SKILL.md` | Replace with Hindsight retain workflow |
| **Delete** | `scripts/logseq_graph_agent.py` | Entire purpose is Logseq sync |
| **Delete** | `kb_migration_plan.md` | Superseded by this migration |
| **Strip** | `scripts/todo-audit.py` | Remove `# Logseq: [[...]]` docstring tag |
| **Strip** | `docs/README.md` | Remove Logseq KB references (6 lines) |
| **Strip** | `docs/reference/kb-access-guide.md` | Full file is Logseq guide — replace with Hindsight guide |
| **Strip** | `docs/reports/tta-spec-audit-report.md` | Remove Logseq backlink tag |
| **Strip** | `docs/development/reorg/tta-separation-roadmap.md` | Remove Logseq backlink tag + inline refs |
| **Strip** | `docs/status/todo-audit.md` | Remove Logseq integration section |
| **Strip** | `scripts/cleanup/organize-repo-phase3.sh` | Remove Logseq references |
| **Strip** | `.github/chatmodes/safety-architect.chatmode.md` | Remove `mcp-logseq` + 6 backlink tags |
| **Strip** | `.github/chatmodes/backend-implementer.chatmode.md` | Remove `mcp-logseq` + 6 backlink tags |

---

## Task 1: Create Hindsight directory structure

**Files:**
- Create: `.hindsight/config.yaml`
- Create: `.hindsight/banks/tta/index.json`
- Create: `.hindsight/banks/tta/architectural-decisions/2026-03-22-hindsight-adoption.memory.md`
- Create: `.hindsight/banks/session/.gitkeep`

- [ ] **Step 1: Create `.hindsight/config.yaml`**

```yaml
# TTA Hindsight Memory Configuration
# Docs: https://github.com/hindsight-ai/hindsight-api
# Reference: /home/adam/Repos/TTA.dev/.hindsight/config.yaml
#
# NOTE:
# This file describes the older repo-local, file-based Hindsight layout.
# The live runtime used in active sessions is API-backed and follows a
# different bank model:
#   - global durable bank:     adam-global
#   - repo/workspace context:  derived project-* or workspace-* bank
# Keep that distinction in mind when reading or extending this config.

version: "1.0"

# Memory banks (file-based reference layout)
banks:
  - name: tta
    path: banks/tta
    persistent: true
    description: "TTA architectural decisions, patterns, and learnings (file-based reference)"
    categories:
      - implementation-failures
      - successful-patterns
      - architectural-decisions

  - name: session
    path: banks/session
    persistent: false
    description: "Current session work-in-progress"

# Semantic indexing (from TTA.dev reference config)
indexing:
  enabled: true
  embedding_model: "text-embedding-3-small"
  chunk_size: 1000
  chunk_overlap: 200
  watch_enabled: false
  watch_interval_seconds: 300

# Retrieval settings
retrieval:
  max_results: 10
  similarity_threshold: 0.7
  include_metadata: true
  recency_weight: 0.2

# Agent integration
agents:
  auto_load_on_start: true
  share_session_memories: true
  sync_interval_minutes: 5
  sub_agent_memory_scope: workflow
```

- [ ] **Step 2: Create `.hindsight/banks/tta/index.json`**

```json
{
  "bank": "tta",
  "version": "1.0",
  "created": "2026-03-22",
  "categories": [
    "implementation-failures",
    "successful-patterns",
    "architectural-decisions"
  ],
  "memories": []
}
```

- [ ] **Step 3: Create seed memory file**

Create `.hindsight/banks/tta/architectural-decisions/2026-03-22-hindsight-adoption.memory.md`:

```markdown
---
category: architectural-decisions
date: 2026-03-22
component: global
severity: critical
tags: [memory, hindsight, logseq-migration, architecture]
---
# Adoption of Hindsight as Agent Memory System

## Context
TTA previously used a Logseq-backed knowledge base (`TTA-notes`) as the canonical
source of architectural truth. Agents wrote to `docs/kb-exports/` via the
`create-atomic-note` skill; a human ingested those files into Logseq manually.
The AI landscape has evolved significantly since TTA was started — Hindsight
provides a direct, programmatic alternative that eliminates the manual ingestion step.

## Decision
Adopted Hindsight as the standard memory system for all TTA agents (Claude Code,
Copilot, Cline, Gemini), mirroring TTA.dev's architecture.

- MCP server: `http://localhost:8888/mcp/` (tools: retain, recall, reflect)
- Live runtime banks: `adam-global` (durable cross-project) + derived `project-*`/`workspace-*` (TTA-specific)
- File-based reference layout kept in `.hindsight/banks/tta/` for documentation
- Session protocol: `recall` from both banks at start → `retain` to appropriate bank at end

## Consequences
- `create-atomic-note` skill now calls `mcp__hindsight__retain` instead of writing files
  - Cross-project patterns → `adam-global`
  - TTA-specific decisions/failures → current derived `project-*`/`workspace-*` bank
- `docs/kb-exports/` is no longer a staging area (existing files kept, no new ones added)
- `tta-notes-kb` MCP server removed from `.mcp.json`
- `scripts/logseq_graph_agent.py` deleted
- All agent config files (CLAUDE.md, AGENTS.md, GEMINI.md, copilot-instructions.md) updated
```

- [ ] **Step 4: Create session bank placeholder with gitignore**

```bash
mkdir -p /home/adam/Repos/TTA/.hindsight/banks/session
touch /home/adam/Repos/TTA/.hindsight/banks/session/.gitkeep
```

Create `.hindsight/banks/session/.gitignore` to prevent committing ephemeral session memories:

```
*
!.gitkeep
!.gitignore
```

- [ ] **Step 5: Verify structure**

```bash
find /home/adam/Repos/TTA/.hindsight -type f | sort
```

Expected output:
```
.hindsight/banks/session/.gitkeep
.hindsight/banks/tta/architectural-decisions/2026-03-22-hindsight-adoption.memory.md
.hindsight/banks/tta/index.json
.hindsight/config.yaml
```

- [ ] **Step 6: Commit**

```bash
git -C /home/adam/Repos/TTA add .hindsight/
git -C /home/adam/Repos/TTA commit -m "feat: add Hindsight memory bank infrastructure"
```

---

## Task 2: Update `.mcp.json`

**Files:**
- Modify: `.mcp.json`

Current content has a single server `tta-notes-kb`. Replace the entire file.

- [ ] **Step 1: Verify current state**

```bash
cat /home/adam/Repos/TTA/.mcp.json
```
Expected: single `tta-notes-kb` entry pointing to `/home/thein/repos/TTA-notes/mcp_server.py`

- [ ] **Step 2: Replace `.mcp.json` with 4 new servers**

```json
{
  "mcpServers": {
    "hindsight": {
      "url": "http://localhost:8888/mcp/"
    },
    "codegraphcontext": {
      "command": "/home/adam/.local/bin/cgc",
      "args": ["mcp", "start"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "mcp-sequentialthinking-tools"],
      "env": {
        "MAX_HISTORY_SIZE": "1000"
      }
    },
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}",
        "GITHUB_TOOLSETS": "default,projects,labels,orgs"
      }
    }
  }
}
```

- [ ] **Step 3: Update `.claude/settings.local.json`**

The file currently has `"enabledMcpjsonServers": ["tta-notes-kb"]` plus permissions. Update just the `enabledMcpjsonServers` array. Keep all existing `permissions.allow` entries unchanged.

```json
{
  "permissions": {
    "allow": [
      "Read(//home/adam/repos/**)",
      "Read(//home/thein/repos/**)",
      "Read(//home/**)",
      "Bash(find /home/adam/Repos/TTA.dev -name *.json -path *mcp*)"
    ]
  },
  "enabledMcpjsonServers": [
    "hindsight",
    "codegraphcontext",
    "sequential-thinking",
    "github"
  ]
}
```

- [ ] **Step 4: Verify**

```bash
grep "tta-notes-kb" /home/adam/Repos/TTA/.mcp.json /home/adam/Repos/TTA/.claude/settings.local.json
```
Expected: no output (zero matches)

- [ ] **Step 5: Commit**

```bash
git -C /home/adam/Repos/TTA add .mcp.json .claude/settings.local.json
git -C /home/adam/Repos/TTA commit -m "feat: replace tta-notes-kb with Hindsight + codegraphcontext + sequential-thinking + github MCPs"
```

---

## Task 3: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

Two changes: (1) add Hindsight session protocol section after `## Project`, (2) update `## Known Issues` to reflect that all issues from `remediation_plan.md` are now resolved.

Note: There are already uncommitted additions (L0 Integration Directive section). Do not overwrite those.

- [ ] **Step 1: Add Hindsight Session Protocol section**

Insert this block **after** the `## Project` section and **before** `## Non-Negotiable Standards`:

```markdown
## Session Protocol

**Every session begins with a memory recall:**
1. `mcp__hindsight__recall` — query `adam-global` for durable directives and cross-project patterns
2. `mcp__hindsight__recall` — query the current derived `project-*` or `workspace-*` bank for TTA-specific context

**Every significant task ends with a retain (choose the right bank):**
- Cross-project patterns, reusable workflow insights → `adam-global`
- TTA-specific decisions, commands, failure lessons → current derived `project-*`/`workspace-*` bank

MCP server: `http://localhost:8888/mcp/` | Start: `uvx --from hindsight-api hindsight-local-mcp`
```

- [ ] **Step 2: Update Known Issues section**

Replace the current `## Known Issues (Fix via \`remediation_plan.md\`)` block (which lists stale Ruff/Pyright errors) with:

```markdown
## Known Issues

Quality gate is currently clean — see `remediation_plan.md` for historical issues (all resolved as of 2026-03-06).

Remaining upstream warnings (not actionable):
- `langchain_core` Pydantic v1 compatibility (upstream)
- `torch/cuda` pynvml deprecation (upstream)
- `asyncio.DefaultEventLoopPolicy` in `packages/tta-narrative-engine/` (out of scope for TTA src/)
```

- [ ] **Step 3: Verify no tta-notes-kb references remain**

```bash
grep -n "tta-notes-kb\|kb-exports\|create-atomic-note\|logseq\|Logseq" /home/adam/Repos/TTA/CLAUDE.md
```
Expected: no output

- [ ] **Step 4: Commit**

```bash
git -C /home/adam/Repos/TTA add CLAUDE.md
git -C /home/adam/Repos/TTA commit -m "docs: add Hindsight session protocol to CLAUDE.md; update Known Issues"
```

---

## Task 4: Update `AGENTS.md`

**Files:**
- Modify: `AGENTS.md`

Two changes: (1) replace `## Knowledge Base Access (MANDATORY)` section, (2) replace `## Documenting Your Work (MANDATORY)` section.

Note: The L0 section has been added as an uncommitted change — preserve it.

- [ ] **Step 1: Replace KB Access section**

Replace this block:
```
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
```

With:
```markdown
## Memory Access (MANDATORY)

Before any non-trivial task, recall context from Hindsight:
1. `mcp__hindsight__recall` — query `adam-global` for durable directives and cross-project patterns
2. `mcp__hindsight__recall` — query the current derived `project-*` or `workspace-*` bank for TTA-specific context

After completing a significant task (architecture decision, bug root-cause, resolved TODO):
- Cross-project patterns → retain to `adam-global`
- TTA-specific decisions, commands, failures → retain to current derived `project-*`/`workspace-*` bank

Hindsight MCP: `http://localhost:8888/mcp/` | Start: `uvx --from hindsight-api hindsight-local-mcp`
```

- [ ] **Step 2: Replace Documenting section**

Replace this block:
```
## Documenting Your Work (MANDATORY)

After completing any significant task (new feature, architecture decision, bug
root-cause, resolved TODO), invoke the `create-atomic-note` skill:

1. Create a new file in `docs/kb-exports/` following the naming convention and
   frontmatter schema defined in `.claude/skills/create-atomic-note/SKILL.md`.
2. Keep the note to a single topic — split complex work into multiple notes.
3. The repo owner will ingest these files into `TTA-notes` manually.
```

With nothing (delete the section entirely). The Memory Access section above covers this.

- [ ] **Step 3: Verify**

```bash
grep -n "tta-notes-kb\|TTA-notes\|kb-exports\|create-atomic-note\|Logseq\|logseq" /home/adam/Repos/TTA/AGENTS.md
```
Expected: no output

- [ ] **Step 4: Commit**

```bash
git -C /home/adam/Repos/TTA add AGENTS.md
git -C /home/adam/Repos/TTA commit -m "docs: replace Logseq KB workflow with Hindsight in AGENTS.md"
```

---

## Task 5: Rewrite `GEMINI.md`

**Files:**
- Modify: `GEMINI.md` (full rewrite — current content is a redirect stub)

- [ ] **Step 1: Verify current state is stub**

```bash
wc -l /home/adam/Repos/TTA/GEMINI.md
cat /home/adam/Repos/TTA/GEMINI.md
```
Expected: ~17 lines, redirect stub pointing to Logseq.

- [ ] **Step 2: Replace with full content**

```markdown
# TTA — Gemini Agent Instructions

Gemini is a **secondary reviewer** in the TTA multi-agent roster.
Primary decisions belong to Claude Code (`CLAUDE.md`).

---

## Session Protocol

**Start of session — recall context:**
1. `mcp__hindsight__recall` — query `adam-global` for durable directives and cross-project patterns
2. `mcp__hindsight__recall` — query the current derived `project-*` or `workspace-*` bank for TTA-specific context

**End of significant task — retain knowledge:**
- Cross-project patterns, reusable insights → `adam-global`
- TTA-specific decisions, commands, failures → current derived `project-*`/`workspace-*` bank

Hindsight MCP: `http://localhost:8888/mcp/` | Start: `uvx --from hindsight-api hindsight-local-mcp`

---

## What This Repo Is

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.

Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

**Architecture:**
- **Persistence**: Redis (session cache) + Neo4j (story graph)
- **API**: FastAPI with SSE for streaming narrative responses
- **Agents**: IPA (Input Processing), WBA (World Building), NGA (Narrative Generation)
- **Safety**: Crisis Detection (4-level) + Emotional Safety (5-level)
- **Workspace packages**: `tta-ai-framework`, `tta-narrative-engine` (in `packages/`)

**Repo layout:**
```
src/
  agent_orchestration/  # Multi-agent coordination, circuit breakers
  ai_components/        # LLM clients, prompt engineering
  api_gateway/          # FastAPI + SSE endpoints
  common/               # Shared utilities, config, database
  components/           # Gameplay loop, narrative engine, model management
  player_experience/    # Player profiles, sessions
  main.py               # CLI entrypoint
packages/               # Workspace packages
tests/                  # pytest suite (unit/, integration/, e2e/)
```

---

## Quality Gate

Always run before finishing any task:

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
uv run pytest -q -m "not integration and not neo4j and not redis" tests/
```

---

## L0 / TTA.dev Boundary

`TTA.dev` owns the L0 developer control plane.

Do **not** build a second developer-agent queue, lease, or approval system inside TTA.
Focus on runtime therapeutic/player-session orchestration only.

When L0 work arises in TTA:
1. Integration points with TTA.dev
2. Repo metadata agents can consume
3. Keep IPA/WBA/NGA orchestration separate from developer-agent coordination

---

## Standards

| Rule | Value |
|------|-------|
| Package manager | `uv` only — never `pip install` |
| Python | 3.12+, `str \| None` not `Optional[str]` |
| Line length | 88 (Ruff) |
| Type checker | Pyright `standard` mode |
| Tests | pytest AAA pattern, `asyncio_mode = "auto"` |
| Commits | Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`) |

---

## Agent Roster

| Agent | Role | Config |
|-------|------|--------|
| **Claude Code** | Primary — main decision maker | `CLAUDE.md` |
| GitHub Copilot | IDE suggestions | `.github/copilot-instructions.md` |
| **Gemini** | Secondary reviewer | `GEMINI.md` (this file) |
| Augment | Code intelligence | `.augment/instructions.md` |
| Cline | AI coding assistant | `.cline/instructions.md` |
```

- [ ] **Step 3: Verify no Logseq refs in new content**

```bash
grep -n "Logseq\|logseq\|TTA-notes\|kb-exports" /home/adam/Repos/TTA/GEMINI.md
```
Expected: no output

- [ ] **Step 4: Commit**

```bash
git -C /home/adam/Repos/TTA add GEMINI.md
git -C /home/adam/Repos/TTA commit -m "docs: rewrite GEMINI.md with real content and Hindsight session protocol"
```

---

## Task 6: Update `.github/copilot-instructions.md`

**Files:**
- Modify: `.github/copilot-instructions.md`

Two changes: (1) remove the `**Logseq:** [[...]]` tag at line 210, (2) add a Hindsight memory note under the "AI Context Integration" section.

Note: Uncommitted L0 section is already present — preserve it.

- [ ] **Step 1: Remove Logseq backlink tag**

The last line of the file (line 210) is:
```
**Logseq:** [[TTA.dev/.github/Copilot-instructions]]
```
Delete this line (and the blank line above it if present).

- [ ] **Step 2: Add Hindsight note to AI Context Integration section**

Find the "### Chat Modes" heading under "## AI Context Integration" and insert before it:

```markdown
### Agent Memory (Hindsight)

TTA uses Hindsight for cross-session agent memory.

- **Recall** at session start: query `adam-global` (cross-project patterns), then derived `project-*`/`workspace-*` bank (TTA-specific context)
- **Retain** after significant tasks: cross-project patterns → `adam-global`; TTA-specific → derived `project-*`/`workspace-*` bank
- MCP server: `http://localhost:8888/mcp/` | Start: `uvx --from hindsight-api hindsight-local-mcp`

```

- [ ] **Step 3: Verify**

```bash
grep -n "Logseq\|logseq\|tta-notes-kb" /home/adam/Repos/TTA/.github/copilot-instructions.md
```
Expected: no output

- [ ] **Step 4: Commit**

```bash
git -C /home/adam/Repos/TTA add .github/copilot-instructions.md
git -C /home/adam/Repos/TTA commit -m "docs: replace Logseq tag with Hindsight memory note in copilot-instructions"
```

---

## Task 7: Rewrite `create-atomic-note` skill

**Files:**
- Modify: `.claude/skills/create-atomic-note/SKILL.md` (full rewrite)

The directory name and invocation path stay unchanged so `/create-atomic-note` continues to work. Only the behavior changes.

- [ ] **Step 1: Verify current content**

```bash
head -5 /home/adam/Repos/TTA/.claude/skills/create-atomic-note/SKILL.md
```
Expected: `# Skill: create-atomic-note` with `docs/kb-exports/` instructions.

- [ ] **Step 2: Replace with Hindsight retain workflow**

```markdown
# Skill: retain-to-hindsight

## Purpose

Store a single-topic knowledge artifact to the TTA Hindsight memory bank (`tta`)
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
```

- [ ] **Step 3: Verify**

```bash
grep -n "kb-exports\|TTA-notes\|frontmatter\|Logseq\|logseq" /home/adam/Repos/TTA/.claude/skills/create-atomic-note/SKILL.md
```
Expected: no output

- [ ] **Step 4: Commit**

```bash
git -C /home/adam/Repos/TTA add .claude/skills/create-atomic-note/SKILL.md
git -C /home/adam/Repos/TTA commit -m "feat: rewire create-atomic-note skill to use mcp__hindsight__retain"
```

---

## Task 8: Delete deprecated files

**Files:**
- Delete: `scripts/logseq_graph_agent.py`
- Delete: `kb_migration_plan.md`

- [ ] **Step 1: Verify files exist**

```bash
ls /home/adam/Repos/TTA/scripts/logseq_graph_agent.py /home/adam/Repos/TTA/kb_migration_plan.md
```

- [ ] **Step 2: Delete both files**

```bash
git -C /home/adam/Repos/TTA rm scripts/logseq_graph_agent.py kb_migration_plan.md
```

- [ ] **Step 3: Commit**

```bash
git -C /home/adam/Repos/TTA commit -m "chore: delete logseq_graph_agent.py and kb_migration_plan.md"
```

---

## Task 9: Strip Logseq references from `scripts/todo-audit.py`

**Files:**
- Modify: `scripts/todo-audit.py`

Only change needed: remove the `# Logseq: [[TTA.dev/Scripts/Todo-audit]]` tag from the module docstring (line 4).

- [ ] **Step 1: Make the edit**

Remove line 4:
```
# Logseq: [[TTA.dev/Scripts/Todo-audit]]
```

The docstring should go from:
```python
"""

# Logseq: [[TTA.dev/Scripts/Todo-audit]]
TTA TODO & GitHub Issue Audit Script
```
to:
```python
"""
TTA TODO & GitHub Issue Audit Script
```

- [ ] **Step 2: Verify**

```bash
grep -n "Logseq\|logseq" /home/adam/Repos/TTA/scripts/todo-audit.py
```
Expected: no output

- [ ] **Step 3: Commit**

```bash
git -C /home/adam/Repos/TTA add scripts/todo-audit.py
git -C /home/adam/Repos/TTA commit -m "chore: remove Logseq tag from todo-audit.py"
```

---

## Task 10: Strip Logseq from chatmodes and remaining docs

**Files:**
- Modify: `.github/chatmodes/safety-architect.chatmode.md`
- Modify: `.github/chatmodes/backend-implementer.chatmode.md`
- Modify: `docs/README.md`
- Modify: `docs/reference/kb-access-guide.md`
- Modify: `docs/reports/tta-spec-audit-report.md`
- Modify: `docs/development/reorg/tta-separation-roadmap.md`
- Modify: `docs/status/todo-audit.md`
- Modify: `scripts/cleanup/organize-repo-phase3.sh`

### Chatmodes (both files, same pattern)

Each has `- mcp-logseq` in the MCP list (line 18) and 6 `**Logseq:** [[...]]` backlink tags at the bottom.

- [ ] **Step 1: Edit `.github/chatmodes/backend-implementer.chatmode.md`**
  - Remove line 18: `- mcp-logseq`
  - Remove lines 404–421 (the block of 6 `**Logseq:**` tags including blank separator lines before them)

- [ ] **Step 2: Edit `.github/chatmodes/safety-architect.chatmode.md`**
  - Remove line 18: `- mcp-logseq`
  - Remove lines 337–354 (same pattern — 6 `**Logseq:**` tags)

- [ ] **Step 3: Verify both chatmodes**

```bash
grep -n "logseq\|Logseq" \
  /home/adam/Repos/TTA/.github/chatmodes/safety-architect.chatmode.md \
  /home/adam/Repos/TTA/.github/chatmodes/backend-implementer.chatmode.md
```
Expected: no output

### `docs/README.md`

Has 6 Logseq references: "Most documentation lives in the Logseq Knowledge Base", links to `reference/logseq-kb.md`, a "Logseq KB" section header, etc.

- [ ] **Step 4: Update `docs/README.md`**
  - Replace the sentence "Most documentation lives in the **Logseq Knowledge Base** at `.augment/kb/`:" with "Most documentation lives in this `docs/` directory."
  - Remove the line `- See [docs/reference/logseq-kb.md](reference/logseq-kb.md) for navigation`
  - Remove the link `- [Logseq KB Guide](reference/logseq-kb.md) - Navigate the knowledge base` from the index
  - Remove the entire `### Logseq KB (.augment/kb/)` section
  - Remove the line `**Questions?** Check the [Logseq KB Guide](reference/logseq-kb.md) or ask in team chat!`
  - Remove the `**Logseq:** [[TTA.dev/Docs/Readme]]` tag at the end

### `docs/reference/kb-access-guide.md`

This file is entirely a Logseq navigation guide. Replace with a minimal Hindsight guide.

- [ ] **Step 5: Replace `docs/reference/kb-access-guide.md`**

```markdown
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
```

### Remaining doc files (backlink-tag-only changes)

- [ ] **Step 6: `docs/reports/tta-spec-audit-report.md`**
  Remove the last line: `**Logseq:** [[TTA/Reports/TTA Spec Audit Report]]`
  (and blank line above it if present)

- [ ] **Step 7: `docs/development/reorg/tta-separation-roadmap.md`**
  - Line 24: Remove `logseq mirror` from the cell describing `.augment/`
  - Line 40: Remove the `logseq/` line from the directory tree
  - Line 98: Remove the sentence about `.augment/logseq` symlinks
  - Last line: Remove `**Logseq:** [[TTA.dev/Docs/Development/Reorg/Tta-separation-roadmap]]`

- [ ] **Step 8: `docs/status/todo-audit.md`**
  Remove the `### 3. Logseq Integration` section (lines 47–65 approximately) and any remaining `**Logseq:**` backlink at the end. Preserve all non-Logseq content.

- [ ] **Step 9: `scripts/cleanup/organize-repo-phase3.sh`**

```bash
grep -n "logseq\|Logseq" /home/adam/Repos/TTA/scripts/cleanup/organize-repo-phase3.sh
```
Remove or comment out any Logseq-specific commands found.

- [ ] **Step 10: Verify all clean**

```bash
grep -rn "logseq\|Logseq" \
  /home/adam/Repos/TTA/.github/chatmodes/ \
  /home/adam/Repos/TTA/docs/README.md \
  /home/adam/Repos/TTA/docs/reference/kb-access-guide.md \
  /home/adam/Repos/TTA/docs/reports/tta-spec-audit-report.md \
  /home/adam/Repos/TTA/docs/development/reorg/tta-separation-roadmap.md \
  /home/adam/Repos/TTA/docs/status/todo-audit.md \
  /home/adam/Repos/TTA/scripts/cleanup/organize-repo-phase3.sh
```
Expected: no output

- [ ] **Step 11: Commit**

```bash
git -C /home/adam/Repos/TTA add \
  .github/chatmodes/ \
  docs/README.md \
  docs/reference/kb-access-guide.md \
  docs/reports/tta-spec-audit-report.md \
  docs/development/reorg/tta-separation-roadmap.md \
  docs/status/todo-audit.md \
  scripts/cleanup/organize-repo-phase3.sh
git -C /home/adam/Repos/TTA commit -m "chore: remove Logseq references from docs and chatmodes"
```

---

## Task 11: Final verification + quality gate

- [ ] **Step 1: Run success-criteria grep**

```bash
grep -r "logseq\|Logseq" /home/adam/Repos/TTA \
  --include="*.md" --include="*.py" --include="*.sh" \
  --include="*.json" --include="*.yaml" \
  --exclude-dir=".archive" --exclude-dir="_archive" --exclude-dir=".git" \
  --exclude-dir=".hindsight"
```
Expected: **zero results**

If any remain, fix them and commit before continuing.

- [ ] **Step 2: Verify `.mcp.json` has correct servers**

```bash
python3 -c "import json; d=json.load(open('/home/adam/Repos/TTA/.mcp.json')); print(list(d['mcpServers'].keys()))"
```
Expected: `['hindsight', 'codegraphcontext', 'sequential-thinking', 'github']`

- [ ] **Step 3: Verify `.hindsight/` structure**

```bash
find /home/adam/Repos/TTA/.hindsight -type f | sort
```
Expected: config.yaml, index.json, seed memory file, session/.gitkeep

- [ ] **Step 4: Verify Hindsight protocol present in all agent files**

```bash
grep -l "mcp__hindsight__" \
  /home/adam/Repos/TTA/CLAUDE.md \
  /home/adam/Repos/TTA/AGENTS.md \
  /home/adam/Repos/TTA/.github/copilot-instructions.md \
  /home/adam/Repos/TTA/GEMINI.md \
  /home/adam/Repos/TTA/.claude/skills/create-atomic-note/SKILL.md
```
Expected: all 5 files listed.

```bash
grep -l "adam-global" \
  /home/adam/Repos/TTA/CLAUDE.md \
  /home/adam/Repos/TTA/AGENTS.md \
  /home/adam/Repos/TTA/GEMINI.md \
  /home/adam/Repos/TTA/.claude/skills/create-atomic-note/SKILL.md
```
Expected: all 4 files listed.

- [ ] **Step 5: Run mandatory quality gate**

```bash
cd /home/adam/Repos/TTA
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
uv run pytest -q -m "not integration and not neo4j and not redis" tests/
```
Expected: ruff 0 errors, pyright 0 errors, all tests pass.

- [ ] **Step 6: Commit design + plan docs**

```bash
git -C /home/adam/Repos/TTA add docs/superpowers/
git -C /home/adam/Repos/TTA commit -m "docs: add Hindsight migration spec and implementation plan"
```

- [ ] **Step 7: Final status check**

```bash
git -C /home/adam/Repos/TTA log --oneline -10
git -C /home/adam/Repos/TTA status
```
Expected: clean working tree, 8-10 commits for this migration.

---

## Commit Summary

| Task | Commit message |
|------|---------------|
| 1 | `feat: add Hindsight memory bank infrastructure` |
| 2 | `feat: replace tta-notes-kb with Hindsight + codegraphcontext + sequential-thinking + github MCPs` |
| 3 | `docs: add Hindsight session protocol to CLAUDE.md; update Known Issues` |
| 4 | `docs: replace Logseq KB workflow with Hindsight in AGENTS.md` |
| 5 | `docs: rewrite GEMINI.md with real content and Hindsight session protocol` |
| 6 | `docs: replace Logseq tag with Hindsight memory note in copilot-instructions` |
| 7 | `feat: rewire create-atomic-note skill to use mcp__hindsight__retain` |
| 8 | `chore: delete logseq_graph_agent.py and kb_migration_plan.md` |
| 9 | `chore: remove Logseq tag from todo-audit.py` |
| 10 | `chore: remove Logseq references from docs and chatmodes` |
| 11 | `docs: add Hindsight migration spec and implementation plan` |
