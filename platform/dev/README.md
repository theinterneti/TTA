# TTA.dev Workspace (In-Repo Staging)

This subtree is the *only* place inside the TTA monorepo where builder tooling should live. Anything here should be safe to copy 1:1 into the standalone `theinterneti/TTA.dev` repository.

Planned contents:

- `agentic/` – Serena runtime, hypertool config, persona packs, cline rules, logseq mirrors, Anthropic/e2b skills.
- `packages/` – reusable packages currently under `packages/ai-dev-toolkit`, `packages/universal-agent-context`, etc.
- `docs/` – migrated `docs/TTA_DEV_*` and similar references.

> Phase 1 starts by moving agentic primitives into `agentic/`. Subsequent phases will bring over packages, docs, and scripts before final export.


---
**Logseq:** [[TTA.dev/Platform/Dev/Readme]]
