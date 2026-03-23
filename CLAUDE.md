# TTA — Claude Code (Tier 1 Root Instructions)

Claude Code is the **primary/main agent** for this repository.

## Project

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.
Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`.

## Session Protocol

**Every session begins with memory recall:**
1. `mcp__hindsight__recall` — query `adam-global` for durable directives and cross-project patterns
2. `mcp__hindsight__recall` — query the current derived `project-*` or `workspace-*` bank for TTA-specific context

**Every significant task ends with a retain (choose the right bank):**
- Cross-project patterns, reusable workflow insights → `adam-global`
- TTA-specific decisions, commands, failure lessons → current derived `project-*`/`workspace-*` bank

MCP server: `http://localhost:8888/mcp/` | Start: `uvx --from hindsight-api hindsight-local-mcp`

## Non-Negotiable Standards

| Constraint | Rule |
|---|---|
| Python version | 3.12+ (`requires-python = ">=3.12"`) |
| Package manager | `uv` only — never `pip install`, never `pip -e .` |
| Type hints | `str | None` not `Optional[str]`; 3.10+ union syntax |
| Line length | 88 chars (Ruff) |
| Type checker | Pyright in `standard` mode |
| Test framework | pytest, `asyncio_mode = "auto"` |
| Commit style | Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`) |

## Mandatory Quality Gate

**Always run all three commands locally and verify they pass before finishing any task:**

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
uv run pytest -q -m "not integration and not neo4j and not redis" tests/
```

## Strict Boundaries

1. **Always run the Mandatory Quality Gate above before finishing any task.** (`ruff check`, `pyright`, `pytest` must all pass.)
2. **Never remove failing tests unless explicitly authorized by the repository owner.**
3. **Follow the AAA (Arrange-Act-Assert) pattern for all tests and enforce 100% coverage for new code.**
4. Never use `pip install` — use `uv` exclusively.
5. Never push broken commits to `main` — branch and PR instead.
6. Never commit `.log`, `.sqlite`, `.db`, coverage reports, or test output files.
7. Never add `torch`, `transformers`, or GPU deps to new modules without explicit justification.
8. Never add CI/CD workflows without strong justification — the suite was deliberately reduced from 35 to 6.

## Common Commands

```bash
uv sync --all-extras                            # Install all deps
uv run ruff check src/ --fix                    # Lint + auto-fix
uv run ruff format src/                         # Format
uv run pyright src/                             # Type check
uv run pytest -q -m "not integration and not neo4j and not redis" tests/  # Unit tests
uv run pytest --cov=src --cov-report=term-missing tests/                  # Coverage
uv run python src/main.py start                 # Start API server
```

## Repo Layout

```
src/                    # Application code
  agent_orchestration/  # Multi-agent coordination, circuit breakers
  ai_components/        # LLM clients, prompt engineering
  analytics/            # Player analytics, therapeutic metrics
  api_gateway/          # FastAPI + SSE endpoints
  common/               # Shared utilities, config, database
  components/           # Gameplay loop, narrative engine, model management
  player_experience/    # Player profiles, sessions
  main.py               # CLI entrypoint
packages/               # Workspace packages (tta-ai-framework, tta-narrative-engine)
tests/                  # pytest suite (unit/, integration/, e2e/)
.github/workflows/      # CI/CD (6 workflows — do not expand without justification)
```

## Key Architecture

- **Persistence**: Redis (session cache) + Neo4j (story graph). Future: Dolt for branching universes.
- **API**: FastAPI with SSE for streaming narrative responses.
- **Agents**: IPA (Input Processing), WBA (World Building), NGA (Narrative Generation).
- **Safety**: Dual safety systems — Crisis Detection (4-level) + Emotional Safety (5-level).

## Known Issues

Quality gate is currently clean — see `remediation_plan.md` for historical issues (all resolved as of 2026-03-06).

Remaining upstream warnings (not actionable by TTA):
- `langchain_core` Pydantic v1 compatibility (upstream)
- `torch/cuda` pynvml deprecation (upstream)
- `asyncio.DefaultEventLoopPolicy` in `packages/tta-narrative-engine/` (separate package, out of TTA src/ scope)

## Agent Roster

| Agent | Config |
|---|---|
| **Claude Code** (primary) | `CLAUDE.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Augment | `.augment/instructions.md` |
| Cline | `.cline/instructions.md` |
| Gemini | `GEMINI.md` |

## L0 Integration Directive

`TTA.dev` is now building the L0 developer control plane for coding agents.

When a task in this repo mentions L0, agent management, developer orchestration,
task leases, approvals, or build-plane coordination:

- assume the control-plane source of truth belongs in `TTA.dev`
- do not build a second developer-agent queue/lease system in TTA
- focus on the TTA side of the boundary: adapters, metadata, integration points,
  and safe separation from runtime player-session orchestration

### TTA-side priorities for L0

1. document or implement how TTA work items map onto TTA.dev L0 tasks/runs
2. expose TTA build/test/deploy workflows in a form L0 agents can claim safely
3. keep runtime orchestration (`IPA/WBA/NGA`, Redis, Neo4j, sessions) separate from developer-agent coordination
