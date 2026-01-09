# TTA ↔︎ TTA.dev Separation Roadmap


> **Note**: The `platform_tta_dev` directory has been migrated to the TTA.dev repository.
> See https://github.com/yourusername/TTA.dev for the toolkit components.



Date: **2025-11-16**

## 1. Intent and Guardrails

- **Mission:** give the therapeutic product (TTA) a clean, production-grade tree while housing _all_ builder tooling (TTA.dev, agentic primitives, MCP inventories, persona packs, etc.) in a clearly bounded workspace.
- **Non-goals:** we are _not_ migrating code to a different repo yet; this pass inventories and stages internal moves so we can later push to `theinterneti/TTA.dev` with confidence.
- **Constraints:** honor existing security/safety guidance (`.github/instructions/*.md`), keep UV + pyproject authority, maintain observability hooks, and avoid breaking the multi-agent orchestration runtime while files are in flight.

## 2. Current-State Inventory Snapshot

| Zone | Directories / Artifacts | Notes |
| --- | --- | --- |
| **TTA product** | `src/`, `tests/`, `deployment/`, `docker/`, `docs/` (player + therapy), `monitoring/`, `living_worlds/`, `player_experience/`, `api_gateway/`, `components/`, `scripts/` (platform ops) | Live therapeutic experience, must stay online; dependencies reference these paths directly. |
| **Shared foundation** | `packages/tta-ai-framework/`, `packages/tta-narrative-engine/`, `narrative-engine/`, `tta/` (prod) | Libraries consumed by both TTA product code and future builders. |
| **TTA.dev & agentic primitives** | `.augment/` (chatmodes, workflows, kb, logseq mirror), `.serena/` + `serena/` (ACE runtime), `.tta/` (persona orchestration), `.cline/`, `.clinerules/`, `.kiro/` (retired spec backlog), `.mcp.hypertool.json`, `packages/ai-dev-toolkit/`, `packages/universal-agent-context/`, `ai-components/` (empty placeholder), `observability` exports, keploy/e2b helpers in `scripts/` | Must be isolated into `tta-dev/` (or exported) so AI assistants stop tripping over product code. |
| **Deprecated / parking lot** | `src/agent_orchestration/openhands_integration/` (plus related tests/docs/scripts), `docs/development/openhands-*`, `.kiro/` specs, `GEMINI.md` workflows earmarked for pause | Keep history but move under `legacy/` buckets. |

> ✅ Inventory covers initial agentic primitives: hypertool config, Serena runtime, ACE personas (`.tta/personas/*.md`), cline CLI hooks, logseq knowledge base (`.augment/logseq`), plus upcoming e2b hooks (currently absent but reserved under `packages/ai-dev-toolkit`).

## 3. Clean Target Layout (within repo before final export)

```text
platform/
  app/                # canonical therapeutic product (current src/tests/docs)
  dev/                # sealed TTA.dev workspace
    agentic/
      hypertool/
      serena/
      personas/
      cline/
      logseq/
      skills/        # slot for Anthropic/e2b assets
    packages/
      ai-dev-toolkit/
      universal-agent-context/
      keploy-framework/ (symlink to exported copy)
    observability/
legacy/
  openhands/
  kiro/
  gemini-workflows/
```

Key ideas:

1. **Single entry points**: anything under `platform/dev/` is safe to copy wholesale into `theinterneti/TTA.dev` — no therapeutic PHI nearby.
2. **Legacy shelf** keeps paused tech (.kiro, openhands, Gemini workflows) but removes them from default import paths so new agents do not autoload them.
- **Observability + MCP connectors** live inside `platform_tta_dev/components/` so hooking Serena/ACE/Hypertool/e2b is trivial.

## 4. Migration Phases

1. **Phase 0 – Freeze & tags (current)**
   - Document authoritative inventory (this file) ✅
   - Tag directories slated for relocation via CODEOWNERS or lint rule (follow-up)
2. **Phase 1 – Agentic primitives first (priority in user request)** ✅ _completed 2025-11-17_
   - Created `platform_tta_dev/components/` and physically moved:
     - `.mcp.hypertool.json` → `platform_tta_dev/components/hypertool/mcp/config.json`
     - `.augment/` → `platform_tta_dev/components/augment/`
     - `.tta/` personas, metrics → `platform_tta_dev/components/personas/`
     - `.cline/` + `.clinerules/` → `platform_tta_dev/components/cline/`
     - `.serena/` + `serena/` → `platform_tta_dev/components/serena/`
   - Wired symlinks/back-compat wrappers (e.g., `.augment`, `.cline`, `.serena` symlinks at root) so automation keeps running.
3. **Phase 2 – Tooling packages & docs**
   - Move `packages/ai-dev-toolkit/` and `packages/universal-agent-context/` under `platform/dev/packages/`
   - Consolidate TTA.dev docs: `docs/TTA_DEV_*` → `platform/dev/docs/`
   - Provide UV workspace entry for `platform/dev/packages/*`
4. **Phase 3 – Legacy quarantine**
   - Relocate `src/agent_orchestration/openhands_integration/*`, related tests, and docs into `legacy/openhands/`
   - Park `.kiro/` inside `legacy/specs/`
   - Move `GEMINI.md` + `docs/project/GEMINI.md` into `legacy/gemini/`
5. **Phase 4 – Export-ready**
   - Ensure `platform/dev` matches `theinterneti/TTA.dev` layout
   - Create scripts to rsync `platform/dev` → external repo
   - Update build/test automation to ignore `platform/dev` when running product pipelines

## 5. Immediate Work Items

1. **Stand up `platform_tta_dev` scaffold** with README + placeholder subfolders ✅ _completed 2025-11-17_
2. **Relocate agentic primitives** (hypertool, Serena, personas, cline rules) ✅ _completed 2025-11-17_: assets now live in `platform_tta_dev/components/` with compatibility symlinks (`.augment`, `.cline`, `.serena`) at repository root. See `MIGRATION_SUMMARY.md` for complete details.
3. **Draft deprecation notices** for `.kiro` and openhands integrations so other agents stop reviving them.
4. **Observability hookup**: ensure Grafana/Redis/Neo4j MCP configs move with agentic workspace so telemetry remains intact.
5. **Automation updates**: update `.vscode/settings.json`, `.devcontainer`, and `scripts/dev.sh` to look under `platform/dev` for agent assistants.

## 6. Dependencies & Risks

- **CI references**: GitHub workflows might reference `.augment/` or `.cline/` — create temp symlinks or update paths before merging.
- **Package imports**: `pyproject.toml` currently excludes `ai-dev-toolkit`; moving it must not reintroduce it to product install.
- **VS Code tasks**: existing tasks rely on root-level `.cline` hooks; plan to update `package.json`-style scripts concurrently.
- **Knowledge base**: `.augment/logseq` replicates the Logseq KB; relocating it must not break the symlinks described in `AGENTS.md`.

## 7. Next Steps (2025-11-17)

- [x] Create `platform_tta_dev/components` tree and move all agentic components (Phase 1 complete) — landed 2025-11-17 with symlink bridge for existing tooling. See branch `refactor/repo-reorg`.
- [ ] Announce legacy quarantine plan (README under `legacy/` summarizing `.kiro`, openhands, Gemini status)
- [x] Update workspace docs (`docs/development/environment-overlays.md`) to mention new structure once scaffold lands (see “Platform Reorg Context” section).
- [ ] Schedule automation updates (VS Code, devcontainer, scripts) once directories move

Once Phase 1 is complete, we can begin copying `platform/dev` into the external `TTA.dev` repository or expose it as a git submodule. For now, this roadmap keeps the effort scoped and visible to every collaborating agent.


---
**Logseq:** [[TTA.dev/Docs/Development/Reorg/Tta-separation-roadmap]]
