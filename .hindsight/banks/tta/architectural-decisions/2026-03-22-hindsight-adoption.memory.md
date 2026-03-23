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
- Session protocol: recall from both banks at start → retain to appropriate bank at end

## Consequences
- `create-atomic-note` skill now calls `mcp__hindsight__retain` instead of writing files
  - Cross-project patterns → `adam-global`
  - TTA-specific decisions/failures → current derived `project-*`/`workspace-*` bank
- `docs/kb-exports/` is no longer a staging area (existing files kept, no new ones added)
- `tta-notes-kb` MCP server removed from `.mcp.json`
- `scripts/logseq_graph_agent.py` deleted
- All agent config files (CLAUDE.md, AGENTS.md, GEMINI.md, copilot-instructions.md) updated
