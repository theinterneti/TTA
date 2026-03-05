# TTA CI Remediation Plan

**Date:** 2026-03-05  
**Author:** Staff DevOps Engineer (Copilot Agent)  
**Status:** DRAFT — awaiting repo owner review before execution  

---

## Baseline Assessment

Captured by running the full quality gate on commit `HEAD` of `copilot/remediate-tta-ci-standards`:

```
uv run ruff check src/        → 16 errors (15 auto-fixable)
uv run pyright src/           → 5 errors, 1 warning
uv run pytest tests/unit/ -q  → 1428 passed, 1 skipped, 1 xpassed — ALL GREEN
```

### Ruff errors (16 total)

| Rule | Count | Files |
|------|-------|-------|
| `UP043` – Unnecessary default type arguments | 14 | `streaming_response.py`, `metrics.py`, `database.py` (×3), `interfaces.py`, providers (×4), `app.py` |
| `I001`  – Import block unsorted/unformatted  |  1 | `src/monitoring/metrics_middleware.py` |
| `PT028` – Test param with default argument   |  1 | `src/components/model_management/api.py:275` |

### Pyright errors (5 total)

| File | Line | Rule | Description |
|------|------|------|-------------|
| `src/agent_orchestration/state_validator.py` | 272 | `reportUnhashable` | `bytes \| bytearray \| str` used as dict key — not fully hashable |
| `src/components/gameplay_loop/narrative/character_development_system.py` | 205 | `reportCallIssue` | Missing required args: `marker_type`, `triggered_by_choice`, `scene_context` |
| `src/components/gameplay_loop/narrative/error_recovery_manager.py` | 217 | `reportCallIssue` | Missing required args: `character_id`, `world_id`, `current_scene`, `current_scene_id` |
| `src/player_experience/uow/player_experience_uow.py` | 40 | `reportAttributeAccessIssue` | `CharacterRepository` not assignable to `AbstractCharacterRepository` |
| `src/player_experience/uow/player_experience_uow.py` | 41 | `reportAttributeAccessIssue` | `SessionRepository` not assignable to `AbstractSessionRepository` |

### Pyright warnings (1 total)

| File | Rule | Description |
|------|------|-------------|
| `src/developer_dashboard/test_battery_integration.py:19` | `reportMissingModuleSource` | `aiofiles` cannot be resolved from source |

### Runtime deprecation warnings (pytest)

- `asyncio.DefaultEventLoopPolicy` deprecated — slated for removal in Python 3.16
  (in `src/components/narrative_arc_orchestrator/scale_manager.py`)
- `asyncio.get_event_loop_policy` / `asyncio.set_event_loop_policy` — same file/same risk
- `pydantic.v1.fields` — Pydantic V1 core functionality not compatible with Python 3.14+
  (surfaced from `langchain_core`)
- `ToolParameter.schema` field name shadows Pydantic `BaseModel.schema` attribute

---

## Phase 1 — Deterministic, Low-Risk Fixes

**Goal:** Zero ruff errors, zero auto-fixable issues. No logic changes.  
**Risk:** Very low — all changes are mechanical; tests must stay green throughout.  
**Estimated effort:** 30–60 minutes.

### 1.1 Auto-fix all ruff-fixable issues

```bash
uv run ruff check src/ --fix
uv run ruff format src/
```

Expected outcome: resolves all 14 `UP043` (remove trailing `None` from `AsyncGenerator[T, None]`,
`Generator[T, None, None]` etc.) and the 1 `I001` import-sort violation.

**Files touched:**
- `src/agent_orchestration/realtime/streaming_response.py`
- `src/agent_orchestration/tools/metrics.py`
- `src/common/database.py`
- `src/components/model_management/interfaces.py`
- `src/components/model_management/providers/custom_api.py`
- `src/components/model_management/providers/lm_studio.py`
- `src/components/model_management/providers/local.py`
- `src/components/model_management/providers/ollama.py`
- `src/components/model_management/providers/openrouter.py`
- `src/monitoring/metrics_middleware.py`
- `src/player_experience/api/app.py`

**Checklist:**
- [ ] Run `uv run ruff check src/ --fix && uv run ruff format src/`
- [ ] Confirm `ruff check src/` reports 0 errors (except PT028 — handled separately)
- [ ] Run `uv run pytest tests/unit/ -q --tb=short -m "not integration and not neo4j and not redis"` — must still show 1428 passed

### 1.2 Fix the remaining non-auto-fixable ruff error

**`PT028`** — `src/components/model_management/api.py:275`  
The `model_mgmt` parameter has `Depends(get_model_management)` as a default, which pytest
flags as a test-function default argument. This is a FastAPI endpoint, not a test function.
Fix: add `# noqa: PT028` inline comment OR rename the function so pytest doesn't pick it up
as a test (the function is named `test_model_connectivity` — it's a FastAPI route, not a test).

Preferred fix: rename the route handler to `check_model_connectivity` (or add `# noqa: PT028`
if renaming would break the API surface/OpenAPI schema in ways the team hasn't budgeted for).

**Checklist:**
- [ ] Decide: rename or suppress with `# noqa: PT028`
- [ ] Apply the chosen fix
- [ ] Confirm `ruff check src/` reports 0 errors
- [ ] Run unit tests — must still pass

### 1.3 Resolve the `aiofiles` missing-source warning

**`reportMissingModuleSource`** — `src/developer_dashboard/test_battery_integration.py:19`  
`aiofiles` is installed as a runtime dep but Pyright cannot find its source stubs.

Fix options (in order of preference):
1. Add `aiofiles` to `pyrightconfig.json` under `reportMissingModuleSource = "none"` scoped
   to `src/developer_dashboard/` (no code change).
2. Add `# type: ignore[import]` at the import line (fallback).

**Checklist:**
- [ ] Confirm `aiofiles` is in `pyproject.toml` dependencies
- [ ] Apply one of the two fix options above
- [ ] Run `uv run pyright src/` — warning count must drop to 0

---

## Phase 2 — Complex Logical Fixes

**Goal:** Zero pyright type errors; eliminate Python 3.16-targeted deprecations.  
**Risk:** Medium — changes touch business logic and abstract base classes.  
**Estimated effort:** 2–4 hours.  
**Pre-condition:** Phase 1 must be complete and tests green before starting Phase 2.

### 2.1 Fix `reportUnhashable` in `state_validator.py`

**File:** `src/agent_orchestration/state_validator.py:272`  
**Error:** `bytes | bytearray | str` used as a dict key — `bytearray` is mutable and not hashable.

Investigation required:
- Read lines 265–280 to understand the dict key usage
- Determine if `bytearray` values will ever appear in practice
- If not: narrow the type annotation to `bytes | str`
- If yes: convert `bytearray → bytes` before using as a dict key

**Checklist:**
- [ ] Read context around line 272 in `state_validator.py`
- [ ] Narrow type or add `bytes()` conversion
- [ ] Add/update unit test covering the fixed code path (AAA pattern)
- [ ] Run `uv run pyright src/` — error at 272 must be gone

### 2.2 Fix `reportCallIssue` in `character_development_system.py`

**File:** `src/components/gameplay_loop/narrative/character_development_system.py:205`  
**Error:** Missing args `marker_type`, `triggered_by_choice`, `scene_context` at call site.

Investigation required:
- Read the constructor/factory signature for the class being instantiated at line 205
- Determine if the caller should pass the missing args (likely) or if the constructor
  should add defaults for backward compatibility
- Prefer passing all required args; add defaults only if the call site legitimately
  cannot provide them (document the reason)

**Checklist:**
- [ ] Read lines 195–215 in `character_development_system.py`
- [ ] Read the target class `__init__` signature
- [ ] Provide missing arguments at the call site OR add typed defaults
- [ ] Add/update unit test (AAA pattern)
- [ ] Run `uv run pyright src/` — error at 205 must be gone

### 2.3 Fix `reportCallIssue` in `error_recovery_manager.py`

**File:** `src/components/gameplay_loop/narrative/error_recovery_manager.py:217`  
**Error:** Missing args `character_id`, `world_id`, `current_scene`, `current_scene_id`.

Same approach as 2.2.

**Checklist:**
- [ ] Read lines 207–225 in `error_recovery_manager.py`
- [ ] Read the target class `__init__` signature
- [ ] Provide missing arguments at the call site OR add typed defaults
- [ ] Add/update unit test (AAA pattern)
- [ ] Run `uv run pyright src/` — error at 217 must be gone

### 2.4 Fix `reportAttributeAccessIssue` in `player_experience_uow.py`

**File:** `src/player_experience/uow/player_experience_uow.py:40–41`  
**Error:** Concrete repositories (`CharacterRepository`, `SessionRepository`) are not
assignable to their abstract base classes (`AbstractCharacterRepository`,
`AbstractSessionRepository`).

Root causes (one or more may apply):
- The concrete class does not fully implement the abstract interface (missing methods)
- The attribute type annotation on the UoW class is too narrow (already expects the abstract)
- A Pyright version bump tightened invariant checks on abstract classes

Investigation steps:
1. Read `player_experience_uow.py` lines 30–55
2. Compare method signatures in `CharacterRepository` vs `AbstractCharacterRepository`
3. Compare method signatures in `SessionRepository` vs `AbstractSessionRepository`
4. Add any missing abstract method implementations, OR fix a type annotation mismatch

**Checklist:**
- [ ] Read `player_experience_uow.py` and both Repository + AbstractRepository classes
- [ ] Identify concrete vs abstract mismatches
- [ ] Implement missing methods or fix type annotations (do not change test behavior)
- [ ] Add/update unit tests covering the fixed classes (AAA pattern)
- [ ] Run `uv run pyright src/` — errors at 40–41 must be gone

### 2.5 Eliminate `asyncio.DefaultEventLoopPolicy` deprecation

**File:** `src/components/narrative_arc_orchestrator/scale_manager.py:47–59`  
**Risk:** Medium — touches event loop initialization used in async tests.

Python 3.16 will remove `asyncio.DefaultEventLoopPolicy`, `asyncio.get_event_loop_policy`,
and `asyncio.set_event_loop_policy`. Recommended remediation:

- Remove the custom `_RobustEventLoopPolicy` subclass entirely if the only goal was
  "use the default policy" (it adds no value).
- If the custom policy is needed for Windows compatibility (most likely the original reason),
  replace with the `winloop` / `uvloop` conditional pattern that doesn't subclass deprecated APIs.

**Checklist:**
- [ ] Read `scale_manager.py` lines 40–65 and understand the original intent
- [ ] Determine if the custom event loop policy is needed
- [ ] Remove the class or replace with a deprecation-safe alternative
- [ ] Run `uv run pytest tests/unit/ -q --tb=short` — must still pass

### 2.6 Track Pydantic v1 validator migration (issue #117)

**Context:** `langchain_core` imports `pydantic.v1.fields` which is incompatible with Python 3.14.
Several TTA validators still use the v1 `@validator` decorator.

This is partially blocked by upstream (`langchain_core`). Track via **issue #117**.

**Checklist:**
- [ ] Audit: `grep -rn "@validator" src/` — list all remaining v1-style validators
- [ ] Convert TTA-owned validators to Pydantic v2 `@field_validator` / `model_validator`
- [ ] Leave `langchain_core`-originated warnings as upstream's responsibility
- [ ] Update issue #117 with list of converted validators

---

## Definition of Done

The remediation is complete when all of the following are true:

```bash
uv run ruff check src/       # Exit 0 — zero errors
uv run pyright src/          # Exit 0 — zero errors, zero warnings
uv run pytest tests/unit/ -q -m "not integration and not neo4j and not redis"
                             # All tests pass (≥1428 passed, 0 failed)
```

No tests may be deleted or downgraded (e.g., from `xfail` to skip) to reach green.

---

## Appendix: Full Raw Output

### `ruff check src/` output (baseline)

```
UP043 src/agent_orchestration/realtime/streaming_response.py:189:40
UP043 src/agent_orchestration/tools/metrics.py:133:51
UP043 src/common/database.py:120:6
UP043 src/common/database.py:145:6
UP043 src/common/database.py:230:6
PT028 src/components/model_management/api.py:275:44
UP043 src/components/model_management/interfaces.py:138:62
UP043 src/components/model_management/providers/custom_api.py:105:10
UP043 src/components/model_management/providers/custom_api.py:201:58
UP043 src/components/model_management/providers/custom_api.py:221:61
UP043 src/components/model_management/providers/lm_studio.py:100:10
UP043 src/components/model_management/providers/local.py:151:10
UP043 src/components/model_management/providers/ollama.py:125:10
UP043 src/components/model_management/providers/openrouter.py:102:10
I001  src/monitoring/metrics_middleware.py:10:1
UP043 src/player_experience/api/app.py:126:37
Found 16 errors. [*] 15 fixable with --fix
```

### `pyright src/` output (baseline)

```
src/agent_orchestration/state_validator.py:272:51
  error: Dictionary key must be hashable — Type "bytes | bytearray | str" is not hashable (reportUnhashable)
src/components/gameplay_loop/narrative/character_development_system.py:205:22
  error: Arguments missing for parameters "marker_type", "triggered_by_choice", "scene_context" (reportCallIssue)
src/components/gameplay_loop/narrative/error_recovery_manager.py:217:25
  error: Arguments missing for parameters "character_id", "world_id", "current_scene", "current_scene_id" (reportCallIssue)
src/developer_dashboard/test_battery_integration.py:19:8
  warning: Import "aiofiles" could not be resolved from source (reportMissingModuleSource)
src/player_experience/uow/player_experience_uow.py:40:27
  error: Cannot assign "CharacterRepository" to "AbstractCharacterRepository" (reportAttributeAccessIssue)
src/player_experience/uow/player_experience_uow.py:41:25
  error: Cannot assign "SessionRepository" to "AbstractSessionRepository" (reportAttributeAccessIssue)
5 errors, 1 warning
```

### `pytest tests/unit/` output (baseline)

```
1428 passed, 1 skipped, 1 xpassed, 11 warnings in 68.02s
```
