# Agentic Primitives Hub

All assistant-facing primitives now live under a single root so MCP servers,
VS Code tasks, and Serena/ACE tooling can mount one directory without touching
therapeutic product code.

## Current Layout (2025-11-16)

```text
agentic/
├── augment/                 # formerly `.augment/`
├── personas/                # formerly `.tta/`
├── cline/                   # `.cline/` + `.clinerules/`
│   ├── hooks/
│   └── rules/
├── hypertool/
│   └── config.json          # moved from `.mcp.hypertool.json`
└── serena/
    ├── runtime/             # full `serena/` repo
    └── state/               # cache + metadata from `.serena/`
```

Each legacy path in the repo root is a symlink into this directory so existing
scripts (e.g., `.augment`, `.tta`, `.cline`, `.clinerules`, `.serena`, `serena`,
and `.mcp.hypertool.json`) keep working while we update automation. New tools
should import files directly from `platform/dev/agentic/*`.

## Primitive Reference

| Primitive | Legacy entry point | New path |
| --- | --- | --- |
| Hypertool MCP manifest | `.mcp.hypertool.json` | `platform/dev/agentic/hypertool/config.json` |
| Serena runtime | `serena/` | `platform/dev/agentic/serena/runtime/` |
| Serena persisted state | `.serena/` | `platform/dev/agentic/serena/state/` |
| ACE personas & overrides | `.tta/` | `platform/dev/agentic/personas/` |
| Cline CLI hooks | `.cline/` | `platform/dev/agentic/cline/` |
| Cline rulesets | `.clinerules/` | `platform/dev/agentic/cline/rules/` |
| Logseq KB, chatmodes, workflows | `.augment/` | `platform/dev/agentic/augment/` |
| Future skills (Anthropic, e2b, etc.) | *not yet migrated* | `platform/dev/agentic/skills/` (placeholder) |

## Automation Status

- `TTA-AI-Workflow.code-workspace` now mounts `platform/dev/agentic/augment/*`
  for chatmodes, contexts, workflows, and memory so future symlink removal
  won't break editor tooling.
- Remaining automation (devcontainers, standalone scripts) still reads through
  the root-level symlinks—track updates here as they land.

## Follow-up Work

- Update `.vscode/settings.json`, devcontainers, and CLI scripts to read the new
  paths (symlinks act as an interim bridge).
- Add `skills/` once the Anthropic/e2b helpers move out of `scripts/`.
- Mirror this directory into the upcoming `TTA.dev` repository when Phase 2
  begins.
