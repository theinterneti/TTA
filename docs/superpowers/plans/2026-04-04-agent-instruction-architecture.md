# Agent Instruction Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure all TTA agent instruction files into a `docs/agents/` canonical tree with thin (<100-line) root files, drift-prevention enforcement, and clear four-tier agent separation. TTA.dev work is tracked via GitHub issues opened in the final task.

**Architecture:** Root files become routing layers with a 100-line hard budget. Always-needed content auto-loads via Claude Code `@`-imports from `docs/agents/_core/`. Domain-specific content lives in `docs/agents/dev/` and loads on demand. Runtime agent reference docs live in `docs/agents/runtime/`.

**Tech Stack:** Markdown (docs), Python 3.12+ (check_agent_docs.py), pytest, Makefile, GitHub CLI (`gh`)

**Spec:** `docs/superpowers/specs/2026-04-04-agent-instruction-architecture-design.md`

---

## File Map

### New files (create)
| File | Purpose |
|---|---|
| `docs/agents/MAINTENANCE.md` | System guide + cross-repo sync obligations |
| `docs/agents/_core/tools.md` | Serena, CGC, Hindsight protocols |
| `docs/agents/_core/quality.md` | ruff, pyright, pytest commands + rules |
| `docs/agents/dev/architecture.md` | Pipeline, agents, data stores, key classes |
| `docs/agents/dev/testing.md` | pytest patterns, markers, coverage, async |
| `docs/agents/dev/safety.md` | Crisis detection, emotional safety systems |
| `docs/agents/dev/genesis.md` | Onboarding narrative system |
| `docs/agents/dev/l0-boundary.md` | TTA.dev integration rules |
| `docs/agents/runtime/ipa.md` | IPA design + prompt reference |
| `docs/agents/runtime/nga.md` | NGA design + prompt reference |
| `docs/agents/runtime/prompt-registry.md` | Versioned YAML prompt system |
| `scripts/check_agent_docs.py` | Line-count budget enforcement |
| `tests/unit/scripts/test_check_agent_docs.py` | Tests for the script |

### Root files (rewrite)
| File | From | To |
|---|---|---|
| `CLAUDE.md` | 147 lines | ~75 lines |
| `AGENTS.md` | 80 lines | ~70 lines |
| `GEMINI.md` | 98 lines | ~70 lines |
| `.github/copilot-instructions.md` | 237 lines | ~80 lines |
| `.cline/instructions.md` | 160 lines | ~70 lines |
| `.augment/instructions.md` | 225 lines | ~70 lines |

---

## Task 1: Create directory structure + MAINTENANCE.md

**Files:**
- Create: `docs/agents/MAINTENANCE.md`
- Create dirs: `docs/agents/_core/`, `docs/agents/dev/`, `docs/agents/runtime/`

- [ ] **Step 1: Create directories**

```bash
mkdir -p docs/agents/_core docs/agents/dev docs/agents/runtime
```

- [ ] **Step 2: Write docs/agents/MAINTENANCE.md**

Write this exact content:

```markdown
# Agent Instruction System — Maintenance Guide

## Architecture

This directory is the single source of truth for all developer-facing agent
instructions in TTA. Root files (CLAUDE.md, AGENTS.md, etc.) are **routing
layers** with a 100-line hard budget. Knowledge lives here, not in root files.

### Directory structure

| Directory | Purpose | Loading |
|---|---|---|
| `_core/` | Always-needed cross-cutting guidance | Auto-imported via CLAUDE.md `@`-imports |
| `dev/` | Domain-specific developer guidance | On demand — agent reads when working on topic |
| `runtime/` | Reference docs for Tier 3 runtime agents | On demand — read when modifying IPA/NGA/prompts |

### Four-tier agent taxonomy

| Tier | Who | Instructions |
|---|---|---|
| 1 — Developer agents | Claude Code, Copilot, Gemini, Cline, Augment | Root files + this tree |
| 2 — Domain expert personas | Chatmodes in `.github/chatmodes/` | Chatmode files (not in this tree) |
| 3 — Runtime product agents | IPA, NGA (in `src/components/`) | `runtime/` reference docs |
| 4 — Runtime dev agents | TTA.dev L0 agents | TTA.dev `docs/agents/` (separate repo) |

---

## How to extend the system

### Adding developer-facing guidance
1. Create or extend a file in `docs/agents/dev/`
2. Add ONE row to each root file's routing table:
   `| Working on <topic> | docs/agents/dev/<topic>.md |`
3. Run `make check-agent-docs` — root files must stay under 100 lines

### Adding always-needed guidance (loads every Claude Code session)
1. Create a file in `docs/agents/_core/`
2. Add `@docs/agents/_core/<file>.md` to `CLAUDE.md`
3. Add a note in other agents' root files: "See docs/agents/_core/<file>.md"

### Adding runtime agent reference docs
1. Create a file in `docs/agents/runtime/`
2. Add a routing entry: `| Editing IPA/NGA prompts | docs/agents/runtime/<agent>.md |`

---

## Maintenance header (paste into every root file you edit)

**TTA variant** (has `_core/`):
```
<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit.
  DO NOT add content directly here.
  Instead:
    1. Create or extend a file in docs/agents/dev/ (or _core/ if always-needed every session)
    2. Add ONE routing row to the table below (or a CLAUDE.md @-import for _core/ files)
    3. Run: make check-agent-docs
  This file is a routing layer, not a knowledge store.
-->
```

---

## Cross-repo sync obligations

Any **structural or protocol change** (not typo/formatting) to these files requires
opening a tracking issue in TTA.dev. Typos and formatting fixes do not require issues.

| This file | TTA.dev counterpart |
|---|---|
| `docs/agents/dev/l0-boundary.md` | `docs/agents/dev/l0-coordination.md` |
| `AGENTS.md` (roster section) | `AGENTS.md` (roster section) |
| `docs/agents/_core/tools.md` | `CLAUDE.md` — `## Session Protocol` section |

---

## Budget enforcement

`make check-agent-docs` checks these root files against the 100-line budget:
`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`,
`.cline/instructions.md`, `.augment/instructions.md`

Script: `scripts/check_agent_docs.py`
```

- [ ] **Step 3: Commit**

```bash
git add docs/agents/
git commit -m "docs(agents): scaffold docs/agents/ tree and MAINTENANCE.md"
```

---

## Task 2: Write _core/tools.md

**Files:**
- Create: `docs/agents/_core/tools.md`
- Source: `CLAUDE.md` lines 22–39, `.github/copilot-instructions.md` lines 164–183

- [ ] **Step 1: Write the file**

```markdown
# Tool Protocols

These tools are available in every TTA development session. Use them deliberately.

## Serena — Structural code navigation

Prefer Serena over Grep/Glob for structural questions.

| Question | Tool |
|---|---|
| "What calls `X`?" | `mcp__plugin_serena_serena__find_referencing_symbols` |
| "What's defined in module Y?" | `mcp__plugin_serena_serena__get_symbols_overview` |
| "Show me the body of class/function Z" | `mcp__plugin_serena_serena__find_symbol` |

- Before any refactor: map all references to the target symbol with Serena first
- At session start: call `mcp__plugin_serena_serena__check_onboarding_performed` to confirm Serena is oriented

## CGC — Code graph analysis

Use before large refactors and for impact analysis.

| Use case | Tool |
|---|---|
| Scope a refactor | `mcp__codegraphcontext__analyze_code_relationships` |
| Find unused code | `mcp__codegraphcontext__find_dead_code` |
| Complexity hotspots | `mcp__codegraphcontext__find_most_complex_functions` |
| Semantic search | `mcp__codegraphcontext__find_code` |

CGC worktree note: orientation hook blocks Write calls in git worktrees.
Fix: create `/tmp/tta_hooks/<session-id>/cgc_oriented` manually, or symlink `scripts/hooks`.

## Hindsight — Persistent cross-session memory

MCP server: `http://localhost:8888/mcp/` | Start: `uvx --from hindsight-api hindsight-local-mcp`

**Every session start:**
1. `mcp__hindsight__recall` → `adam-global` — cross-project directives and preferences
2. `mcp__hindsight__recall` → `tta` — TTA-specific architecture, decisions, known issues

**After significant tasks:**
- Cross-project patterns → `adam-global`
- TTA-specific decisions, failures, patterns → `tta`

Rules: use `document_id` for evolving notes (same ID = upsert). Never retain secrets.
If Hindsight is unavailable, say so and continue — never pretend recall happened.

## Other MCP servers

- **Context7** — fetch current library/framework docs before implementing against an API
- **Sequential Thinking** — break down complex multi-step refactoring workflows
- **Redis MCP** — inspect session state and debug cache issues directly
```

- [ ] **Step 2: Commit**

```bash
git add docs/agents/_core/tools.md
git commit -m "docs(agents): add _core/tools.md — Serena, CGC, Hindsight protocols"
```

---

## Task 3: Write _core/quality.md

**Files:**
- Create: `docs/agents/_core/quality.md`
- Source: `CLAUDE.md` lines 41–72, `AGENTS.md` lines 38–53

- [ ] **Step 1: Write the file**

```markdown
# Quality Gate & Standards

## Mandatory quality gate

**Run all three before finishing any task. All must pass.**

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Non-negotiable standards

| Constraint | Rule |
|---|---|
| Python version | 3.12+ (`requires-python = ">=3.12"`) |
| Package manager | `uv` only — never `pip install`, never `pip -e .` |
| Type hints | `str \| None` not `Optional[str]`; 3.10+ union syntax |
| Line length | 88 chars (Ruff) |
| Type checker | Pyright in `standard` mode |
| Test framework | pytest, `asyncio_mode = "auto"` |
| Commit style | Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`) |

## Strict boundaries

1. Never remove failing tests unless explicitly authorized by the repository owner
2. Follow AAA (Arrange-Act-Assert) pattern for all tests; 100% coverage for new code
3. Never push broken commits to `main` — branch and PR instead
4. Never commit `.log`, `.sqlite`, `.db`, coverage reports, or test output files
5. Never add `torch`, `transformers`, or GPU deps without explicit justification
6. Never add CI/CD workflows without strong justification (suite was reduced from 35 to 6)

## Common commands

```bash
uv sync --all-extras                                          # Install all deps
uv run ruff check src/ --fix && uv run ruff format src/      # Lint + format
uv run pyright src/                                           # Type check
make test                                                     # Unit tests (no services)
make test-integration                                         # Full suite (Neo4j + Redis)
make watch                                                    # Continuous unit tests
uv run pytest --cov=src --cov-report=term-missing tests/      # Coverage report
uv run python src/main.py start                               # Start API server
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/agents/_core/quality.md
git commit -m "docs(agents): add _core/quality.md — quality gate, standards, commands"
```

---

## Task 4: Write dev/architecture.md

**Files:**
- Create: `docs/agents/dev/architecture.md`
- Source: `CLAUDE.md` lines 88–119, `.github/copilot-instructions.md` lines 8–24 and 78–95, `.cline/instructions.md` lines 36–63, `.augment/instructions.md` lines 60–90

- [ ] **Step 1: Write the file**

```markdown
# Architecture Reference

## Multi-agent pipeline

```
User Input → IPA → WBA → NGA → SSE Stream → Player
```

- **IPA** (Input Processing Agent) — classifies intent, extracts entities, detects emotional tone and safety signals. System prompt at `src/components/ipa/agent.py:59`. Produces `ProcessedInput`.
- **WBA** (World Building Agent) — pure Neo4j context-assembly layer; no LLM calls. Produces `WorldContext`.
- **NGA** (Narrative Generation Agent) — generates therapeutic narrative from ProcessedInput + WorldContext. System prompt at `src/components/nga/agent.py:53`. Streams response to player.

All three wrapped in TTA.dev `FallbackPrimitive(RetryPrimitive(...))` for resilience.

## Data stores

| Store | Role | Status |
|---|---|---|
| Redis | Session cache, workflow state, circuit breaker state | Active |
| Neo4j | Story graph (`Scene -[:LEADS_TO]-> Scene`), character relationships | Active |
| Dolt | Branching universe state (one branch per timeline fork) | Future |

## Key source directories

```
src/
  agent_orchestration/      # Multi-agent coordination, circuit breakers, messaging
  ai_components/            # LLM clients, prompt engineering, prompt registry
  analytics/                # Player analytics, therapeutic metrics
  api_gateway/              # FastAPI + SSE endpoints
  common/                   # Shared utilities, config, database
  components/               # IPA, WBA, NGA, gameplay loop, narrative engine, genesis
  player_experience/        # Player profiles, sessions, frontend
  main.py                   # CLI entrypoint
packages/
  tta-ai-framework/         # Workspace package: AI orchestration
  tta-narrative-engine/     # Workspace package: narrative generation
tests/
  unit/                     # Fast, no external services
  integration/              # Require Redis + Neo4j
  e2e/                      # Require live deployment
```

## Key classes

| Class | Location | Purpose |
|---|---|---|
| `IPAAgent` | `src/components/ipa/agent.py` | Input processing |
| `NGAAgent` | `src/components/nga/agent.py` | Narrative generation |
| `WorldContextBuilder` | `src/components/world_context/` | Neo4j context assembly |
| `CircuitBreaker` | `src/agent_orchestration/circuit_breaker.py` | Redis-persisted error recovery |
| `UnifiedAgentOrchestrator` | `src/agent_orchestration/` | IPA/WBA/NGA coordination |
| `NarrativeEngine` | `src/components/gameplay_loop/narrative/engine.py` | Scene generation |
| `PlayerExperienceManager` | `src/player_experience/` | Player profiles + sessions |

## Circuit breaker pattern

States: `CLOSED → OPEN → HALF_OPEN` with configurable thresholds.
Redis-persisted at `src/agent_orchestration/circuit_breaker.py`.

```python
try:
    result = await circuit_breaker.call(agent_function)
except CircuitBreakerOpenError:
    return fallback_response()
```

## TTA.dev dependency

TTA consumes TTA.dev platform packages via local path sources (editable):
- `ttadev.primitives` — `FallbackPrimitive`, `RetryPrimitive`, `TimeoutPrimitive`, etc.
- `ttadev.observability` — metrics and tracing

Use `WorkflowPrimitive` composition — don't reinvent retry, timeout, or circuit breaker logic.
```

- [ ] **Step 2: Commit**

```bash
git add docs/agents/dev/architecture.md
git commit -m "docs(agents): add dev/architecture.md — pipeline, data stores, key classes"
```

---

## Task 5: Write dev/testing.md

**Files:**
- Create: `docs/agents/dev/testing.md`
- Source: `.cline/instructions.md` lines 88–108, `.github/copilot-instructions.md` lines 30–36, `CLAUDE.md` line 67

- [ ] **Step 1: Write the file**

```markdown
# Testing Reference

## Test tiers

| Tier | Marker | Requires | Command |
|---|---|---|---|
| Unit | (none) | Nothing | `make test` |
| Integration | `@pytest.mark.integration` | Redis + Neo4j | `make test-integration` |
| E2E / post-deploy | `@pytest.mark.e2e` | Live deployment | Never run locally |

## Test patterns

```python
# Unit test — no external services
async def test_something():
    # Arrange
    input_data = ProcessedInput(intent="explore", ...)
    # Act
    result = await process(input_data)
    # Assert
    assert result.status == "ok"

# Integration test — requires Redis
@pytest.mark.integration
@pytest.mark.redis
async def test_with_redis(redis_client):
    ...

# Integration test — requires Neo4j
@pytest.mark.integration
@pytest.mark.neo4j
async def test_with_neo4j(neo4j_driver):
    ...
```

## AAA pattern (mandatory)

Every test must follow Arrange-Act-Assert with clear separation:
```python
async def test_ipa_classifies_explore_intent():
    # Arrange
    agent = IPAAgent(llm=mock_llm)
    raw_input = "I want to look around the room"
    # Act
    result = await agent.process(raw_input)
    # Assert
    assert result.intent == Intent.EXPLORE
    assert result.intent_confidence > 0.8
```

## Coverage rules

- 100% coverage for all new code
- Run: `uv run pytest --cov=src --cov-report=term-missing tests/`
- Never commit with uncovered lines in new modules

## Continuous testing

```bash
make watch       # Reruns unit tests on every .py/.toml save
make watch-all   # Same, includes integration tests (needs Redis + Neo4j)
```

## Fixtures

`tests/conftest.py` provides fixtures with automatic mock fallbacks — if Redis/Neo4j
are not running, integration fixtures return mocks rather than failing.

Do **not** use `tests/post_deployment/` locally — these require a live deployment.
```

- [ ] **Step 2: Commit**

```bash
git add docs/agents/dev/testing.md
git commit -m "docs(agents): add dev/testing.md — AAA, markers, coverage, fixtures"
```

---

## Task 6: Write dev/safety.md

**Files:**
- Create: `docs/agents/dev/safety.md`
- Source: `src/agent_orchestration/crisis_detection/` (read for accuracy), `CLAUDE.md` line 110

- [ ] **Step 1: Write the file**

```markdown
# Safety Systems Reference

TTA has dual safety systems that operate in parallel on every player input.
These are non-negotiable and must never be degraded or bypassed.

## Crisis Detection — 4 levels

Located at `src/agent_orchestration/crisis_detection/`.

| Level | Trigger | Response |
|---|---|---|
| `NONE` | No crisis indicators | Normal narrative flow |
| `LOW` | Mild distress language | NGA writes with extra warmth |
| `MEDIUM` | Moderate distress or vague self-harm | IPA sets `safety_signal=true`; NGA responds gently with grounding |
| `HIGH` | Explicit crisis / self-harm | Immediate safe-messaging response; escalation path triggered |

`CrisisDetector` runs in IPA. If `safety_signal=true` is set on `ProcessedInput`,
NGA automatically adjusts tone (see `nga/agent.py` system prompt guidelines).

## Emotional Safety — 5 levels

Located at `src/agent_orchestration/emotional_safety/` (or `src/components/safety/`).

The emotional safety layer evaluates NGA output before it reaches the player.
It can block or modify responses that violate therapeutic safety guidelines.

## Development rules

1. **Never degrade crisis detection sensitivity** — false negatives are far more
   dangerous than false positives in this domain.
2. **Never remove safety markers from test fixtures** — `safety_signal=true`
   paths must remain covered.
3. **Therapeutic content changes require safety review** — any modification to
   IPA or NGA system prompts must be reviewed against safe-messaging guidelines.
4. **Do not introduce LLM calls that bypass the safety pipeline** — all player-
   facing LLM outputs must flow through IPA → WBA → NGA.

## Key files

| File | Purpose |
|---|---|
| `src/agent_orchestration/crisis_detection/detector.py` | CrisisDetector implementation |
| `src/agent_orchestration/crisis_detection/enums.py` | CrisisLevel enum |
| `src/components/ipa/agent.py` | Sets `safety_signal` on ProcessedInput |
| `src/components/nga/agent.py` | Adjusts tone based on `safety_signal` |
```

- [ ] **Step 2: Commit**

```bash
git add docs/agents/dev/safety.md
git commit -m "docs(agents): add dev/safety.md — crisis detection, emotional safety, dev rules"
```

---

## Task 7: Write dev/genesis.md

**Files:**
- Create: `docs/agents/dev/genesis.md`
- Source: memory context (issues #224, #259), `src/components/genesis/`

- [ ] **Step 1: Write the file**

```markdown
# Genesis System Reference

Genesis is TTA's metamorphic onboarding system — the first session experience
that transforms a neutral world into a personalized therapeutic narrative.

Related issues: #224, #259

## What Genesis does

1. **Seed extraction** — extracts meaningful themes from player's opening input
2. **Guide generation** — creates a personalized in-world guide character from the seed
3. **World personalization** — shapes the starting world state around the player's seed
4. **Narrator voice selection** — picks the appropriate narrative voice profile

## Architecture

Located at `src/components/genesis/`.

```
GenesisSession
  ├── SeedExtractor        — extracts WorldSeed from player input (ChatPrimitive)
  ├── GuideGenerator       — derives guide character from seed (ChatPrimitive)
  └── GenesisSessionState  — tracks 5-act onboarding progress
```

The Genesis agent uses `ChatPrimitive` (from TTA.dev) for all LLM calls.
The narrator adapter is passed into `derive_guide_character`.

## Narrator voice profiles

Narrator voices are defined separately from the guide character. They shape
the narrative style: tone, vocabulary, warmth level, metaphor density.

## 5-act structure

| Act | What happens |
|---|---|
| 1 | Player arrives; neutral world established |
| 2 | Opening prompt; seed extraction |
| 3 | Guide character introduced |
| 4 | World begins to reflect player's seed |
| 5 | Transition to main game loop |

## Development rules

- Guide generation failure must fall back gracefully — use `FallbackPrimitive`
- Seeds should be abstract enough to personalise without being clinically diagnostic
- Never store raw seed text permanently without user consent
- Genesis state transitions are idempotent — re-running an act must be safe
```

- [ ] **Step 2: Commit**

```bash
git add docs/agents/dev/genesis.md
git commit -m "docs(agents): add dev/genesis.md — onboarding system, seed/guide, 5-act structure"
```

---

## Task 8: Write dev/l0-boundary.md

**Files:**
- Create: `docs/agents/dev/l0-boundary.md`
- Source: `CLAUDE.md` lines 131–147, `AGENTS.md` lines 62–79, `GEMINI.md` lines 63–73

- [ ] **Step 1: Write the file**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add docs/agents/dev/l0-boundary.md
git commit -m "docs(agents): add dev/l0-boundary.md — L0/TTA.dev separation rules"
```

---

## Task 9: Write runtime agent reference docs

**Files:**
- Create: `docs/agents/runtime/ipa.md`
- Create: `docs/agents/runtime/nga.md`
- Create: `docs/agents/runtime/prompt-registry.md`
- Source: `src/components/ipa/agent.py:1-82`, `src/components/nga/agent.py:1-66`, `src/ai_components/prompts/`

- [ ] **Step 1: Write runtime/ipa.md**

```markdown
# IPA — Input Processing Agent

## What IPA does

Classifies player intent, extracts named entities, detects emotional tone, and
sets safety signals. Produces a `ProcessedInput` fed into the WBA.

## System prompt location

`src/components/ipa/agent.py` — `_SYSTEM_PROMPT` constant at line 59.

**Do not hardcode this prompt elsewhere.** Edit it only in that file.
To version it via the prompt registry, see `docs/agents/runtime/prompt-registry.md`.

## Current prompt behaviour

- Classifies intent: `explore | interact | query | action | journal | unknown`
- Extracts entities with type and confidence score
- Detects emotional tone (primary + intensity)
- Sets `safety_signal=true` for self-harm, crisis, or severe distress language
- Returns structured JSON only — no prose

## Fallback behaviour

On LLM failure, IPA returns `_FALLBACK_RESULT`:
```python
{"intent": "unknown", "intent_confidence": 0.5, "entities": [],
 "emotional_tone": {"primary": "neutral", "intensity": 0.0, "safety_signal": False},
 "normalized_text": ""}
```

## Architecture

```
IPAAgent.process(raw_text)
  └── _IPACall — LLM call → IntentClassification JSON
        wrapped in FallbackPrimitive(RetryPrimitive(...))
```

## Extending IPA

- To add a new intent type: update `Intent` enum in `src/components/ipa/models.py` + update the system prompt
- To add an entity type: update `ExtractedEntity.entity_type` + update the system prompt
- Always update tests in `tests/unit/components/ipa/`
```

- [ ] **Step 2: Write runtime/nga.md**

```markdown
# NGA — Narrative Generation Agent

## What NGA does

Receives `ProcessedInput` (from IPA) + `WorldContext` (from WBA) and generates
the therapeutic narrative streamed back to the player.

## System prompt location

`src/components/nga/agent.py` — `_SYSTEM_PROMPT` constant at line 53.

**Do not hardcode this prompt elsewhere.** Edit it only in that file.

## Current prompt behaviour

- Writes 2–4 short paragraphs of vivid, present-tense narrative
- Honours the player's intent and emotional tone
- Grounds narrative in world facts from WorldContext
- Gives NPCs brief moments of life when present
- Never lectures, diagnoses, or breaks the fictional frame
- Applies extra warmth and gentleness when `safety_signal=true`
- Ends with a subtle open invitation to continue

## Guide voice injection

The NGA system prompt can be prepended with a guide voice instruction block,
injected by `GuidePromptBuilder` from `src/components/guide/prompt.py`.
This shapes the narrative voice to match the player's personalized guide character.

## Architecture

```
NGAAgent.generate(processed_input, world_context)
  └── _NGALLMCall — LLM call with assembled system + user message
        wrapped in FallbackPrimitive(RetryPrimitive(...))
```

## Extending NGA

- To change narrative style: edit the system prompt + test with therapeutic content review
- To add guide voice profiles: update `GuidePromptBuilder` + add narrator voice profiles
- Any prompt change requires safety review — see `docs/agents/dev/safety.md`
```

- [ ] **Step 3: Write runtime/prompt-registry.md**

```markdown
# Prompt Registry

The prompt registry provides versioned, metrics-tracked prompt management.

## Location

`src/ai_components/prompts/` — `PromptRegistry`, `PromptTemplate`, `PromptMetrics`

## Active versions

Versioned YAML files live in `src/ai_components/prompts/versions/v1.0.0/`.
Active versions are symlinked from `src/ai_components/prompts/active/`.

Current active versions:
- `narrative_generation.yaml` — NGA narrative generation prompt
- `safety_check.yaml` — safety classification prompt

## YAML format

```yaml
name: narrative_generation
version: "1.0.0"
description: "NGA main narrative generation prompt"
template: |
  You are the narrator of a therapeutic text adventure...
variables:
  - world_context
  - player_intent
```

## Adding a new prompt version

1. Create `src/ai_components/prompts/versions/v<X.Y.Z>/<prompt_name>.yaml`
2. Test against the full NGA pipeline with `make test`
3. Update the symlink in `active/` to point to the new version
4. Retain the old version — never delete versioned prompts

## Promoting to active

```bash
cd src/ai_components/prompts/active
ln -sfn ../versions/v<X.Y.Z>/<name>.yaml <name>.yaml
```
```

- [ ] **Step 4: Commit**

```bash
git add docs/agents/runtime/
git commit -m "docs(agents): add runtime/ reference docs — IPA, NGA, prompt-registry"
```

---

## Task 10: TDD — scripts/check_agent_docs.py

**Files:**
- Create: `tests/unit/scripts/test_check_agent_docs.py`
- Create: `scripts/check_agent_docs.py`

- [ ] **Step 1: Create test directory if needed**

```bash
mkdir -p tests/unit/scripts
touch tests/unit/scripts/__init__.py
```

- [ ] **Step 2: Write the failing test**

Create `tests/unit/scripts/test_check_agent_docs.py`:

```python
"""Tests for scripts/check_agent_docs.py budget enforcement."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[3] / "scripts" / "check_agent_docs.py"


def run_check(tmp_path: Path, files: dict[str, str]) -> tuple[int, str]:
    """Write files to tmp_path and run the checker against them."""
    for name, content in files.items():
        (tmp_path / name).write_text(content)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout + result.stderr


def make_lines(n: int) -> str:
    return "\n".join(f"line {i}" for i in range(n))


class TestBudgetEnforcement:
    def test_passes_when_all_files_under_budget(self, tmp_path: Path) -> None:
        files = {
            "CLAUDE.md": make_lines(80),
            "AGENTS.md": make_lines(70),
        }
        returncode, _ = run_check(tmp_path, files)
        assert returncode == 0

    def test_fails_when_file_over_budget(self, tmp_path: Path) -> None:
        files = {
            "CLAUDE.md": make_lines(101),
            "AGENTS.md": make_lines(70),
        }
        returncode, output = run_check(tmp_path, files)
        assert returncode != 0
        assert "CLAUDE.md" in output

    def test_reports_exact_line_count(self, tmp_path: Path) -> None:
        files = {"CLAUDE.md": make_lines(110)}
        _, output = run_check(tmp_path, files)
        assert "110" in output

    def test_reports_all_over_budget_files(self, tmp_path: Path) -> None:
        files = {
            "CLAUDE.md": make_lines(105),
            "AGENTS.md": make_lines(120),
        }
        _, output = run_check(tmp_path, files)
        assert "CLAUDE.md" in output
        assert "AGENTS.md" in output

    def test_missing_file_is_skipped_not_error(self, tmp_path: Path) -> None:
        # Only CLAUDE.md present — missing files are just skipped
        files = {"CLAUDE.md": make_lines(50)}
        returncode, _ = run_check(tmp_path, files)
        assert returncode == 0

    def test_exactly_100_lines_passes(self, tmp_path: Path) -> None:
        files = {"CLAUDE.md": make_lines(100)}
        returncode, _ = run_check(tmp_path, files)
        assert returncode == 0

    def test_101_lines_fails(self, tmp_path: Path) -> None:
        files = {"CLAUDE.md": make_lines(101)}
        returncode, _ = run_check(tmp_path, files)
        assert returncode != 0
```

- [ ] **Step 3: Run the tests — confirm the expected failures**

```bash
uv run pytest tests/unit/scripts/test_check_agent_docs.py -v
```

Expected: **two tests FAIL, five tests PASS (for the wrong reason)**. Because the test
uses `subprocess.run`, a missing script exits non-zero — so tests asserting
`returncode != 0` (the "file over budget" tests) will incorrectly pass. Only the
tests asserting `returncode == 0` (passes_when_under_budget, exactly_100_passes)
will correctly FAIL. This is the expected red state — proceed to implementation.

- [ ] **Step 4: Write scripts/check_agent_docs.py**

```python
#!/usr/bin/env python3
"""Check that root agent instruction files stay within the 100-line budget.

Usage:
    python scripts/check_agent_docs.py                  # check repo root
    python scripts/check_agent_docs.py --root /path     # check alternate root
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BUDGET = 100

# Hardcoded list of root files that must stay under budget.
ROOT_FILES = [
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
    ".cline/instructions.md",
    ".augment/instructions.md",
]


def check(root: Path) -> list[tuple[str, int]]:
    """Return list of (filename, line_count) for files over budget."""
    violations: list[tuple[str, int]] = []
    for rel in ROOT_FILES:
        path = root / rel
        if not path.exists():
            continue
        lines = len(path.read_text().splitlines())
        if lines > BUDGET:
            violations.append((rel, lines))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: cwd)",
    )
    args = parser.parse_args()

    violations = check(args.root)
    if not violations:
        print("check-agent-docs: all root files within 100-line budget")
        return 0

    print("check-agent-docs: BUDGET VIOLATION — root files must stay under 100 lines")
    print()
    for rel, count in violations:
        print(f"  {rel}: {count} lines (over by {count - BUDGET})")
    print()
    print("Fix: move content to docs/agents/dev/<topic>.md and add a routing row.")
    print("See docs/agents/MAINTENANCE.md for instructions.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run the tests — expect all to pass**

```bash
uv run pytest tests/unit/scripts/test_check_agent_docs.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/check_agent_docs.py tests/unit/scripts/
git commit -m "feat(scripts): add check_agent_docs.py — 100-line budget enforcement with tests"
```

---

## Task 11: Add make check-agent-docs target

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Add target to Makefile**

Open `Makefile`. After the `.PHONY` declaration line, add `check-agent-docs` to the list, then append this target at the end of the file:

```makefile
check-agent-docs:
	uv run python scripts/check_agent_docs.py
```

**Important:** The indented line must use a **tab character**, not spaces. Makefiles
require tabs. Verify with: `cat -A Makefile | grep check-agent-docs` — the recipe
line should start with `^I` (tab), not spaces.

Also update the `.PHONY` line to include `check-agent-docs`.

- [ ] **Step 2: Verify it works**

```bash
make check-agent-docs
```

Expected output (before root files are rewritten):
```
check-agent-docs: BUDGET VIOLATION — root files must stay under 100 lines
  CLAUDE.md: 147 lines (over by 47)
  .github/copilot-instructions.md: 237 lines (over by 137)
  ...
```

- [ ] **Step 3: Run quality gate**

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

All must pass.

- [ ] **Step 4: Commit**

```bash
git add Makefile
git commit -m "chore(make): add check-agent-docs target for 100-line budget enforcement"
```

---

## Task 12: Rewrite CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` (147 → ~75 lines)

Content to **extract** (moves to sub-files already written):
- Lines 22–39 (Tool Usage Protocol) → already in `_core/tools.md`
- Lines 53–72 (Quality Gate + Strict Boundaries) → already in `_core/quality.md`
- Lines 88–119 (Repo Layout + Key Architecture) → already in `dev/architecture.md`
- Lines 131–147 (L0 Integration details) → already in `dev/l0-boundary.md`

- [ ] **Step 1: Overwrite CLAUDE.md with the new routing-layer version**

```markdown
<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit.
  DO NOT add content directly here.
  Instead:
    1. Create or extend a file in docs/agents/dev/ (or _core/ if always-needed every session)
    2. Add ONE routing row to the table below (or a CLAUDE.md @-import for _core/ files)
    3. Run: make check-agent-docs
  This file is a routing layer, not a knowledge store.
-->

# TTA — Claude Code

Claude Code is the **primary/main agent** for this repository.

## Project

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.
Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`.

@docs/agents/_core/tools.md
@docs/agents/_core/quality.md

## Session Protocol

**Every session begins with memory recall:**
1. `mcp__hindsight__recall` → `adam-global` — cross-project directives and patterns
2. `mcp__hindsight__recall` → `tta` — TTA-specific context, decisions, known issues

**Every significant task ends with a retain:**
- Cross-project patterns → `adam-global`
- TTA-specific decisions and failures → `tta`

## Routing

Read the relevant sub-file **before starting work** on any of these topics:

| Working on… | Read first |
|---|---|
| Architecture, pipeline, agents, data stores | `docs/agents/dev/architecture.md` |
| Tests, coverage, markers, fixtures | `docs/agents/dev/testing.md` |
| Safety systems, crisis detection | `docs/agents/dev/safety.md` |
| Genesis / onboarding narrative system | `docs/agents/dev/genesis.md` |
| L0, TTA.dev boundary, developer control plane | `docs/agents/dev/l0-boundary.md` |
| IPA or NGA system prompts | `docs/agents/runtime/ipa.md` or `nga.md` |
| Prompt versioning | `docs/agents/runtime/prompt-registry.md` |

## Agent roster

| Agent | Config |
|---|---|
| **Claude Code** (primary) | `CLAUDE.md` (this file) |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Augment | `.augment/instructions.md` |
| Cline | `.cline/instructions.md` |
| Gemini | `GEMINI.md` |

## L0 directive

`TTA.dev` owns the L0 developer control plane. Do not build a second one here.
Full rules: `docs/agents/dev/l0-boundary.md`
```

- [ ] **Step 2: Verify line count**

```bash
wc -l CLAUDE.md
```

Must be ≤ 100.

- [ ] **Step 3: Run budget check**

```bash
make check-agent-docs
```

CLAUDE.md should no longer appear in violations.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "refactor(docs): slim CLAUDE.md to routing layer — 147 → ~75 lines"
```

---

## Task 13: Rewrite AGENTS.md

**Files:**
- Modify: `AGENTS.md` (80 → ~65 lines)

- [ ] **Step 1: Overwrite AGENTS.md**

```markdown
<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# AGENTS.md — Universal Agent Context

Shared entry point for all AI agents in the TTA repository. Read this before acting.

## What this repo is

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.
Players make choices that branch the story; a therapist/editorial layer curates safe paths.

Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

**TTA.dev** provides reusable platform primitives. It owns the L0 developer control plane.

## Agent roster

| Agent | Role | Config |
|---|---|---|
| **Claude Code** | Primary — main decision maker | `CLAUDE.md` |
| GitHub Copilot | AI coding assistant | `.github/copilot-instructions.md` |
| Augment | Code intelligence | `.augment/instructions.md` |
| Cline | AI coding assistant | `.cline/instructions.md` |
| Gemini | Secondary reviewer | `GEMINI.md` |

## Non-negotiables

- Python 3.12+ | `uv` only (never `pip`) | 88-char lines | Pyright `standard`
- Conventional Commits | AAA tests | 100% coverage for new code

## Quality gate (run before committing)

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Domain guidance

For detailed context on any topic, read the relevant file before starting:

| Topic | File |
|---|---|
| Architecture, pipeline, key classes | `docs/agents/dev/architecture.md` |
| Testing patterns, markers, coverage | `docs/agents/dev/testing.md` |
| Safety systems | `docs/agents/dev/safety.md` |
| Genesis / onboarding | `docs/agents/dev/genesis.md` |
| L0 / TTA.dev boundary | `docs/agents/dev/l0-boundary.md` |

## Memory (Hindsight)

Before non-trivial tasks: recall `adam-global` then `tta` from Hindsight.
After significant tasks: retain to the appropriate bank.
MCP: `http://localhost:8888/mcp/`
```

- [ ] **Step 2: Verify and commit**

```bash
wc -l AGENTS.md
make check-agent-docs
git add AGENTS.md
git commit -m "refactor(docs): slim AGENTS.md to routing layer with domain guidance table"
```

---

## Task 14: Rewrite GEMINI.md

**Files:**
- Modify: `GEMINI.md` (98 → ~65 lines)

- [ ] **Step 1: Overwrite GEMINI.md**

```markdown
<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# TTA — Gemini Agent Instructions

Gemini is a **secondary reviewer**. Primary decisions belong to Claude Code.

## Project

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.
Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

**Architecture:** Redis (session cache) + Neo4j (story graph) + FastAPI SSE
**Safety:** Crisis Detection (4-level) + Emotional Safety (5-level)

## Session protocol

1. `mcp__hindsight__recall` → `adam-global` — cross-project directives
2. `mcp__hindsight__recall` → `tta` — TTA-specific context
After significant tasks: retain to the appropriate bank.
Hindsight MCP: `http://localhost:8888/mcp/`

## Quality gate

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Standards

| Rule | Value |
|---|---|
| Package manager | `uv` only — never `pip install` |
| Python | 3.12+, `str \| None` not `Optional[str]` |
| Line length | 88 (Ruff) |
| Type checker | Pyright `standard` mode |
| Tests | pytest AAA pattern, `asyncio_mode = "auto"` |
| Commits | Conventional Commits |

## Domain guidance

| Topic | File |
|---|---|
| Architecture, pipeline | `docs/agents/dev/architecture.md` |
| Testing patterns | `docs/agents/dev/testing.md` |
| Safety systems | `docs/agents/dev/safety.md` |
| Genesis / onboarding | `docs/agents/dev/genesis.md` |
| L0 / TTA.dev boundary | `docs/agents/dev/l0-boundary.md` |
| IPA or NGA system prompts | `docs/agents/runtime/ipa.md` or `nga.md` |

## Agent roster

| Agent | Role | Config |
|---|---|---|
| **Claude Code** | Primary | `CLAUDE.md` |
| **Gemini** | Secondary reviewer | `GEMINI.md` (this file) |
| GitHub Copilot | IDE suggestions | `.github/copilot-instructions.md` |
| Augment | Code intelligence | `.augment/instructions.md` |
| Cline | AI coding assistant | `.cline/instructions.md` |

## L0 / TTA.dev boundary

`TTA.dev` owns the L0 developer control plane. Do not build a second one here.
Full rules: `docs/agents/dev/l0-boundary.md`
```

- [ ] **Step 2: Verify and commit**

```bash
wc -l GEMINI.md
make check-agent-docs
git add GEMINI.md
git commit -m "refactor(docs): slim GEMINI.md to routing layer — 98 → ~65 lines"
```

---

## Task 15: Rewrite .github/copilot-instructions.md

**Files:**
- Modify: `.github/copilot-instructions.md` (237 → ~80 lines)

Note: Copilot cannot use `@`-imports. Routing table must include explicit "read before starting" instructions.

- [ ] **Step 1: Overwrite the file**

```markdown
<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# TTA — GitHub Copilot Instructions

## Project

**Therapeutic Text Adventure (TTA)** — AI-powered narrative game for mental health support.
Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

## Non-negotiables

- Python 3.12+ | `uv` only (never `pip`) | 88-char lines | Pyright `standard` mode
- Conventional Commits | AAA tests | 100% coverage for new code
- Never push broken commits to `main` — branch and PR instead

## Quality gate (run before committing)

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Session protocol

**Start of session:**
1. Recall from Hindsight `adam-global` (cross-project directives)
2. Recall from Hindsight `tta` (TTA-specific context)
3. Call `check_onboarding_performed` on Serena to confirm it is oriented to this repo

**After significant tasks:** retain decisions and patterns to the appropriate Hindsight bank.

## Routing — read the relevant file before starting work

| Working on… | Read this file first |
|---|---|
| Architecture, pipeline, agents, data stores | `docs/agents/dev/architecture.md` |
| Tests, coverage, markers, fixtures | `docs/agents/dev/testing.md` |
| Safety systems, crisis detection | `docs/agents/dev/safety.md` |
| Genesis / onboarding narrative system | `docs/agents/dev/genesis.md` |
| L0, TTA.dev boundary | `docs/agents/dev/l0-boundary.md` |
| IPA or NGA system prompts | `docs/agents/runtime/ipa.md` or `nga.md` |
| Prompt versioning | `docs/agents/runtime/prompt-registry.md` |
| Tool protocols (Serena, CGC, Hindsight) | `docs/agents/_core/tools.md` |

## MCP servers available

- **Serena** — symbol-aware code navigation (structural questions, refactor scoping)
- **CGC** — code graph analysis (dependency chains, dead code, complexity)
- **Hindsight** — persistent cross-session memory (`http://localhost:8888/mcp/`)
- **Context7** — current library/framework documentation
- Full protocols: `docs/agents/_core/tools.md`

## Agent roster

| Agent | Config |
|---|---|
| **Claude Code** (primary) | `CLAUDE.md` |
| **GitHub Copilot** | `.github/copilot-instructions.md` (this file) |
| Augment | `.augment/instructions.md` |
| Cline | `.cline/instructions.md` |
| Gemini | `GEMINI.md` |
```

- [ ] **Step 2: Verify and commit**

```bash
wc -l .github/copilot-instructions.md
make check-agent-docs
git add .github/copilot-instructions.md
git commit -m "refactor(docs): slim copilot-instructions.md to routing layer — 237 → ~80 lines"
```

---

## Task 16: Rewrite .cline/instructions.md

**Files:**
- Modify: `.cline/instructions.md` (160 → ~70 lines)

- [ ] **Step 1: Overwrite the file**

```markdown
<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# TTA — Cline Instructions

## Project

**TTA** is an AI-powered therapeutic text adventure. Players make choices that branch
the narrative; a safety layer curates which paths are therapeutically effective.

Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

## Non-negotiables

| Constraint | Rule |
|---|---|
| Python version | 3.12+ only |
| Package manager | `uv` — never `pip` |
| Type hints | `str \| None` not `Optional[str]` |
| Line length | 88 chars (Ruff) |
| Type checker | Pyright (`standard` mode) |
| Test framework | pytest, `asyncio_mode = "auto"` |
| Commit style | Conventional Commits |

## Quality gate (run before committing)

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Session protocol

Before any non-trivial task:
1. Recall from Hindsight `adam-global` (cross-project directives)
2. Recall from Hindsight `tta` (TTA-specific context)
After significant tasks: retain decisions to the appropriate Hindsight bank.

## Routing — read the relevant file before starting work

| Working on… | Read this file first |
|---|---|
| Architecture, pipeline, agents, data stores | `docs/agents/dev/architecture.md` |
| Tests, coverage, markers, fixtures | `docs/agents/dev/testing.md` |
| Safety systems, crisis detection | `docs/agents/dev/safety.md` |
| Genesis / onboarding narrative system | `docs/agents/dev/genesis.md` |
| L0, TTA.dev boundary | `docs/agents/dev/l0-boundary.md` |
| IPA or NGA system prompts | `docs/agents/runtime/ipa.md` or `nga.md` |
| Tool protocols (Serena, CGC, Hindsight) | `docs/agents/_core/tools.md` |

## Agent roster

| Agent | Config |
|---|---|
| **Claude Code** (primary) | `CLAUDE.md` |
| **Cline** | `.cline/instructions.md` (this file) |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Augment | `.augment/instructions.md` |
| Gemini | `GEMINI.md` |
```

- [ ] **Step 2: Verify and commit**

```bash
wc -l .cline/instructions.md
make check-agent-docs
git add .cline/instructions.md
git commit -m "refactor(docs): slim .cline/instructions.md to routing layer — 160 → ~70 lines"
```

---

## Task 17: Rewrite .augment/instructions.md

**Files:**
- Modify: `.augment/instructions.md` (225 → ~75 lines)

- [ ] **Step 1: Overwrite the file**

```markdown
<!--
  MAINTENANCE PROTOCOL — read before editing this file
  Budget: 100 lines hard limit. Add content to docs/agents/dev/, not here.
  Run: make check-agent-docs
-->

# TTA — Augment Instructions

## What this repo is

**TTA** is an AI-powered therapeutic text adventure. Players make choices that branch
the narrative; a therapist/editorial safety layer curates which paths are effective.

Multi-agent pipeline: `User Input → IPA → WBA → NGA → SSE Stream → Player`

**TTA.dev** (`~/Repos/TTA.dev`) provides the platform primitives TTA is built on.

## Non-negotiable standards

- Python 3.12+ | `uv` only (never `pip install`) | `str | None` not `Optional[str]`
- 88-char lines | Pyright `standard` mode | Conventional Commits
- pytest with `asyncio_mode = "auto"` | 100% coverage for new code

## Quality gate

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Session protocol

Before non-trivial tasks:
1. Recall from Hindsight `adam-global` (cross-project directives)
2. Recall from Hindsight `tta` (TTA-specific context)
After significant tasks: retain to the appropriate Hindsight bank.

## Routing — read the relevant file before starting work

| Working on… | Read this file first |
|---|---|
| Architecture, pipeline, agents, data stores | `docs/agents/dev/architecture.md` |
| Tests, coverage, markers, fixtures | `docs/agents/dev/testing.md` |
| Safety systems, crisis detection | `docs/agents/dev/safety.md` |
| Genesis / onboarding narrative system | `docs/agents/dev/genesis.md` |
| L0, TTA.dev boundary | `docs/agents/dev/l0-boundary.md` |
| IPA or NGA system prompts | `docs/agents/runtime/ipa.md` or `nga.md` |
| Tool protocols (Serena, CGC, Hindsight) | `docs/agents/_core/tools.md` |

## Key source directories

```
src/components/ipa/        # Input Processing Agent
src/components/nga/        # Narrative Generation Agent
src/agent_orchestration/   # Circuit breakers, coordination
src/ai_components/         # LLM clients, prompt registry
src/player_experience/     # Player profiles and sessions
packages/                  # tta-ai-framework, tta-narrative-engine
```

## Agent roster

| Agent | Config |
|---|---|
| **Claude Code** (primary) | `CLAUDE.md` |
| **Augment** | `.augment/instructions.md` (this file) |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cline | `.cline/instructions.md` |
| Gemini | `GEMINI.md` |
```

- [ ] **Step 2: Verify and commit**

```bash
wc -l .augment/instructions.md
make check-agent-docs
git add .augment/instructions.md
git commit -m "refactor(docs): slim .augment/instructions.md to routing layer — 225 → ~75 lines"
```

---

## Task 18: Final verification

- [ ] **Step 1: Run full budget check — expect zero violations**

```bash
make check-agent-docs
```

Expected:
```
check-agent-docs: all root files within 100-line budget
```

- [ ] **Step 2: Run full quality gate**

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

All must pass with zero errors.

- [ ] **Step 3: Verify all new files exist**

```bash
ls docs/agents/_core/ docs/agents/dev/ docs/agents/runtime/
```

Expected files:
- `_core/`: `tools.md`, `quality.md`
- `dev/`: `architecture.md`, `testing.md`, `safety.md`, `genesis.md`, `l0-boundary.md`
- `runtime/`: `ipa.md`, `nga.md`, `prompt-registry.md`

- [ ] **Step 4: Spot-check line counts on all root files**

```bash
wc -l CLAUDE.md AGENTS.md GEMINI.md .github/copilot-instructions.md .cline/instructions.md .augment/instructions.md
```

All must be ≤ 100.

---

## Task 19: Open TTA.dev GitHub issues (cross-repo sync)

These are **forward-tracking** issues — they document the obligation to build the
TTA.dev `docs/agents/` tree in a future session, not requests for immediate action.

- [ ] **Step 1: Open a consolidated tracking issue on TTA.dev**

```bash
gh issue create \
  --repo theinterneti/TTA.dev \
  --title "docs(agents): build docs/agents/ canonical instruction tree" \
  --body "$(cat <<'EOF'
## Context

TTA has completed its docs/agents/ restructuring (see TTA commit 2026-04-04).
TTA.dev needs an equivalent system per the design spec:
docs/superpowers/specs/2026-04-04-agent-instruction-architecture-design.md

## Work required

Per spec, TTA.dev needs:

### New docs/agent files (9):
- docs/agents/MAINTENANCE.md
- docs/agents/dev/architecture.md
- docs/agents/dev/testing.md
- docs/agents/dev/l0-coordination.md
- docs/agents/dev/observability.md (promoted + renamed from docs/guides/agents/universal/patterns/observability.instructions.md — delete source after promoting)
- docs/agents/dev/reliability.md (promoted + renamed from docs/guides/agents/universal/patterns/reliability.instructions.md — delete source after promoting)
- docs/agents/runtime/l0-roster.md
- docs/agents/runtime/l0-agent-spec.md
- docs/agents/runtime/task-protocol.md

### New script:
- scripts/check_agent_docs.py (same pattern as TTA's version, checking CLAUDE.md, AGENTS.md, .github/copilot-instructions.md)

### Root files to rewrite (3):
- CLAUDE.md (130 → ~80 lines)
- AGENTS.md (351 → ~75 lines)
- .github/copilot-instructions.md (148 → ~75 lines)

### Cross-repo sync obligations
When implementing, ensure l0-coordination.md stays coherent with TTA's dev/l0-boundary.md.
See docs/agents/MAINTENANCE.md in TTA for the sync protocol.

## Spec reference
docs/superpowers/specs/2026-04-04-agent-instruction-architecture-design.md (in TTA repo)
EOF
)"
```

- [ ] **Step 2: Confirm issue was created**

```bash
gh issue list --repo theinterneti/TTA.dev --limit 5
```

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "chore: open TTA.dev tracking issues for docs/agents/ cross-repo sync

All TTA agent instruction restructuring complete. TTA.dev work tracked
in paired GitHub issue."
```
