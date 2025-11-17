# Platform Layout Bootstrap

This directory namespaces the two worlds we have to keep separate while TTA.dev continues building TTA:

- `app/` will eventually track the therapeutic experience (current `src/`, `tests/`, etc.). For now it's a placeholder so the destination exists before we start moving.
- `dev/` houses every TTA.dev artifact (agentic primitives, MCP configs, builder packages, docs). We will migrate the existing tooling directories here during Phase 1.

Each subdirectory receives its own README as we land content. Nothing has been moved yet; this scaffold simply gives every collaborating agent the same target paths before we begin rsyncing files.
