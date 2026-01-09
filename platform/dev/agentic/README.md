# ⚠️ DEPRECATED: Agentic Components Migrated

**This directory structure is now deprecated!**

All agentic components have been migrated to the new **`platform_tta_dev`** structure as of 2025-11-17.

## New Location

All components are now at: **`platform_tta_dev/components/`**

```text
platform_tta_dev/
└── components/
    ├── augment/     # AI workflow primitives (chatmodes, workflows, memory, KB)
    ├── cline/       # CLI automation hooks and quality assurance
    ├── hypertool/   # MCP server orchestration + workflow foundation
    ├── personas/    # Agent persona definitions and metrics
    └── serena/      # Code search & architectural analysis toolkit
```

## Migration Status (2025-11-17)

**All components successfully migrated:**
- ✅ Hypertool (26 files) - MCP servers, chatmodes, workflows
- ✅ Serena (472 files) - Complete Python package (serena-agent==0.1.4)
- ✅ Augment (393 files) - Chatmodes, workflows, memory, context, KB
- ✅ Cline (5 files) - JavaScript hooks and rules
- ✅ Personas (9 files) - Persona definitions, metrics, configs

**Root-level symlinks** (`.mcp.hypertool.json`) now point to the new locations in `platform_tta_dev/components/`.

## Component Reference

| Component | New Location | Description |
| --- | --- | --- |
| Hypertool | `platform_tta_dev/components/hypertool/` | MCP server orchestration + workflow foundation |
| Serena | `platform_tta_dev/components/serena/` | Code search & architectural analysis toolkit |
| Augment | `platform_tta_dev/components/augment/` | AI workflow primitives (chatmodes, workflows, memory, KB) |
| Cline | `platform_tta_dev/components/cline/` | CLI automation hooks and quality assurance |
| Personas | `platform_tta_dev/components/personas/` | Agent persona definitions and metrics |

## Next Steps

If you're looking for the old `platform/dev/agentic/` components:

1. **Update imports/paths** to reference `platform_tta_dev/components/`
2. **Update .vscode/settings.json** to reference new component locations
3. **Update workspace files** to mount from new locations
4. **Remove this deprecated directory** once all references are updated

See `platform_tta_dev/README.md` for the new component-centric structure and guidelines.


---
**Logseq:** [[TTA.dev/Platform/Dev/Agentic/Readme]]
