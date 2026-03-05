# Knowledge Base Access

TTA project knowledge lives in the `TTA-notes` repository, accessible via the
`tta-notes-kb` MCP server. Local Logseq sync has been decommissioned.

## MCP Server

| Tool | Purpose |
|------|---------|
| `search_kb` | Full-text search across all KB documents |
| `get_high_priority_todos` | Retrieve open high-priority work items |

**Server path:** `/home/thein/repos/TTA-notes/mcp_server.py`

**Config files:**
- `.mcp.json` — Claude Code project-scoped MCP config
- `.vscode/notebooklm-mcp-config.json` — VS Code MCP config

## Atomic Notes Output

Agents write documentation to `docs/kb-exports/` after completing significant
work. The repo owner ingests those files into `TTA-notes` manually.

See `.claude/skills/create-atomic-note/SKILL.md` for the required frontmatter
schema and file naming convention.
