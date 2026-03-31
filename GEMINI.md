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
make test
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
