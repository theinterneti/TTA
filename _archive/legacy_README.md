# Legacy / Paused Technology Shelf

The `legacy/` tree is where we quarantine tooling that is no longer part of the active build. Nothing here should be auto-loaded by agents, linters, or CI.

| Folder | Purpose |
| --- | --- |
| `openhands/` | Parking spot for `src/agent_orchestration/openhands_integration/*`, related tests, docs, and scripts once relocated. |
| `kiro/` | Archive of `.kiro/` specs (no longer maintained). |
| `gemini/` | Gemini workflow experiments that are on hold. |

As we migrate files into these directories we will add README notes explaining why they were retired and how to re-enable them if the strategy changes.


---
**Logseq:** [[TTA.dev/_archive/Legacy_readme]]
