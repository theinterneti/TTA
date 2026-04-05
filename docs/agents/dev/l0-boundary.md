# L0 / TTA.dev Integration Boundary

`TTA.dev` owns the L0 developer control plane for coding agents.
This file defines what TTA owns vs what belongs in TTA.dev.

## What TTA does NOT own

- Developer-agent task queues, leases, or approval systems
- The L0 control plane itself (runs in TTA.dev)
- Routing logic for which L0 agent handles which type of task

If you encounter a request to build developer-agent coordination inside
`src/agent_orchestration/`, stop and re-read this file.

## What TTA owns at the L0 boundary

1. **Work item representation** — how TTA build/test/release tasks map to TTA.dev L0 tasks and runs
2. **Safe adapters** — scripts and adapters that let TTA.dev-managed agents operate on this repo without touching therapeutic runtime state
3. **Metadata exposure** — surfacing enough project/workflow metadata that TTA.dev can coordinate work
4. **Runtime separation** — keeping IPA/WBA/NGA player-session orchestration completely separate from developer-agent coordination

## Anti-goals

- Do not treat IPA/WBA/NGA runtime orchestration as the same problem as Claude/Copilot developer coordination — those are different control planes
- Do not build a second circuit breaker registry or agent registry for developer tasks
- Do not add L0 state management to Redis keys that also hold player session state

## Cross-repo sync

This file has a counterpart in TTA.dev: `docs/agents/dev/l0-coordination.md`.
Any structural or protocol change here requires a tracking issue in TTA.dev.
See `docs/agents/MAINTENANCE.md` for the sync protocol.

## Current L0 integration status

See open issues tagged `l0` for current integration tasks.
TTA.dev L0 phase-1 is complete as of 2026-03-30.
