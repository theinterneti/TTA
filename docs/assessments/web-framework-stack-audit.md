# Web Framework Stack Audit: FastAPI, Pydantic, Uvicorn, Starlette

**Date:** 2026-03-04
**Scope:** Phase 1 — Dependency Audit & Research
**Issue:** #153 — Audit Web Framework Stack
**Effort Estimate:** 4 hours (research), 8–12 hours (migration implementation)
**Priority:** High

---

## Executive Summary

TTA's web framework stack uses permissive lower-bound version constraints (`>=0.95.0` for FastAPI, `>=2.0.0` for Pydantic, etc.) that allow installation of the latest versions but do not enforce the minimum versions needed for full compatibility with modern features and Python 3.14. The codebase is **already fully migrated to Pydantic v2** (zero v1 patterns found), but has **65+ FastAPI endpoints using the legacy `Depends()` pattern** instead of the recommended `Annotated` pattern, and **2–3 instances of deprecated Starlette lifecycle decorators**. Raising the version floors and migrating these patterns is low-risk and positions TTA for Python 3.14 and Starlette 1.0.

---

## 1. Version Compatibility Matrix

| Package | Current Constraint | Latest Stable | Recommended Minimum | Python 3.14 Support |
|---|---|---|---|---|
| **FastAPI** | `>=0.95.0` | 0.135.1 | `>=0.115.0` | ✅ Yes (0.126.0+) |
| **Pydantic** | `>=2.0.0` | 2.12.5 | `>=2.10.0` | ✅ Yes (2.12.0+) |
| **Pydantic-Settings** | `>=2.0.0` | 2.8.1 | `>=2.5.0` | ✅ Yes |
| **Uvicorn** | `>=0.22.0` | 0.41.0 | `>=0.32.0` | ✅ Yes |
| **Starlette** | `>=0.46.0` | 0.52.1 (1.0.0rc1 available) | `>=0.50.0` | ✅ Yes |
| **SSE-Starlette** | `>=2.2.0` | 2.2.1 | `>=2.2.0` | ✅ Yes |
| **httpx** | `>=0.24.0` | 0.28.1 | `>=0.27.0` | ✅ Yes |
| **aiohttp** | `>=3.13.3` | 3.13.3 | `>=3.13.3` | ✅ Yes |

### Python Version Requirements

| Package Version | Minimum Python |
|---|---|
| FastAPI 0.125.0+ | 3.9+ |
| Pydantic 2.12.0+ | 3.9+ |
| Uvicorn 0.34.0+ | 3.9+ |
| Uvicorn 0.40.0+ | 3.10+ |
| Starlette 0.50.0+ | 3.10+ |

TTA requires Python `>=3.12`, so all version constraints are satisfied.

---

## 2. Breaking Changes Analysis

### 2.1 FastAPI (0.95.0 → 0.135.1)

| Version | Breaking Change | Impact on TTA | Effort |
|---|---|---|---|
| 0.95.0 | `Annotated` type introduced for dependency injection | **65+ endpoints** use legacy `Depends()` pattern | Medium (refactor) |
| 0.125.0 | Minimum Python raised to 3.9+ | ✅ No impact (TTA requires 3.12+) | None |
| 0.126.0 | Pydantic v2 required (v1 support dropped) | ✅ No impact (already on Pydantic v2) | None |
| 0.128.0 | `pydantic.v1` compatibility layer removed | ✅ No impact (zero v1 imports found) | None |
| 0.132.0 | Strict `Content-Type: application/json` checking | 🟡 Test API clients may need header updates | Low |

#### Codebase Impact — `Depends()` Without `Annotated`

Files with legacy `Depends()` pattern (non-exhaustive):

- `src/player_experience/api/routers/worlds.py`
- `src/player_experience/api/routers/characters.py`
- `src/player_experience/api/routers/health.py`
- `src/player_experience/api/routers/conversation.py`
- `src/player_experience/api/routers/progress.py`
- `src/player_experience/api/routers/auth.py`
- `src/player_experience/api/routers/sessions.py`
- `src/player_experience/api/routers/gameplay.py`
- `src/player_experience/api/routers/settings.py`
- `src/player_experience/api/routers/metrics.py`
- `src/player_experience/api/routers/privacy.py`
- `src/components/model_management/api.py`
- `src/api_gateway/interfaces/patient_api.py`
- `src/agent_orchestration/api/diagnostics.py`

**Migration pattern:**

```python
# Before (legacy)
@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    ...

# After (recommended)
from typing import Annotated

DBSession = Annotated[Session, Depends(get_db)]

@router.get("/items")
async def get_items(db: DBSession):
    ...
```

> **Note:** The legacy pattern still works and is not removed. Migration is recommended but not required for functionality.

### 2.2 Pydantic (2.0.0 → 2.12.5)

| Version | Change | Impact on TTA | Effort |
|---|---|---|---|
| 2.7.0 | Required by FastAPI 0.126.0+ | ✅ Compatible | None |
| 2.10.0 | Performance improvements, better error messages | ✅ Compatible | None |
| 2.12.0 | Python 3.14 support, PEP 649/749 compliance | ✅ Compatible | None |
| 2.12.0 | Experimental `MISSING` sentinel | Informational only | None |

#### Codebase Audit Results — Pydantic v2 Migration Status: ✅ COMPLETE

| Pattern | Count | Status |
|---|---|---|
| `from pydantic.v1 import` | 0 | ✅ No v1 imports |
| `@validator` (v1) | 0 | ✅ All using `@field_validator` (14 instances) |
| `class Config:` (v1) | 0 | ✅ All using `model_config` / `ConfigDict` |
| `.dict()` (v1) | 0 | ✅ All using `.model_dump()` (65+ instances) |
| `.json()` (v1) | 0 | ✅ All using `.model_dump_json()` (13+ instances) |
| `orm_mode` (v1) | 0 | ✅ Not used |
| `regex=` in Field (v1) | 0 | ✅ Not used |

**No Pydantic migration work required.**

### 2.3 Uvicorn (0.22.0 → 0.41.0)

| Version | Breaking Change | Impact on TTA | Effort |
|---|---|---|---|
| 0.33.0 | WatchGod support removed (use `watchfiles`) | ✅ No impact | None |
| 0.34.0 | Python 3.8 support dropped | ✅ No impact (TTA requires 3.12+) | None |
| 0.34.1 | `ServerState` export deprecated | 🟡 Check for direct usage | Low |
| 0.40.0 | Python 3.9 support dropped | ✅ No impact | None |
| 0.41.0 | `error_occured` → `error_occurred` (typo fix) | 🟡 Check lifespan hooks | Low |

**No critical Uvicorn migration work required.**

### 2.4 Starlette (0.46.0 → 0.52.1 / 1.0.0rc1)

| Version | Breaking Change | Impact on TTA | Effort |
|---|---|---|---|
| 0.47.1 | AnyIO dependency introduced | ✅ Compatible | None |
| 0.50.0 | Python 3.9 dropped | ✅ No impact (TTA requires 3.12+) | None |
| 0.52.0 | State dictionary access with type checking | ✅ Compatible | None |
| **1.0.0rc1** | `on_startup`/`on_shutdown` removed | 🔴 **2 instances must migrate** | Low |
| **1.0.0rc1** | `@app.on_event()` removed | 🔴 **2 instances must migrate** | Low |
| **1.0.0rc1** | `@app.route()` removed | ✅ Not used | None |
| **1.0.0rc1** | `@app.middleware()` removed | 🟡 **1 instance to review** | Low |
| **1.0.0rc1** | `@app.exception_handler()` removed | 🟡 Check usage | Low |

#### Deprecated Lifecycle Patterns Found

**`@app.on_event()` — 2 instances:**
- `src/analytics/services/realtime_monitoring_service.py`

**`@app.middleware("http")` — 1 instance:**
- `src/player_experience/franchise_worlds/api/main.py`

**Migration pattern for lifecycle events:**

```python
# Before (deprecated)
@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

# After (recommended)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)
```

---

## 3. Performance Improvements Available

### FastAPI 0.115+
- Improved OpenAPI schema generation performance
- Better request validation caching
- Optimized dependency injection resolution

### Pydantic 2.10+
- Rust-based core validation (pydantic-core) with continued optimization
- Faster model initialization and validation
- Reduced memory footprint for large model hierarchies
- Better error message formatting

### Uvicorn 0.30+
- Improved HTTP/1.1 parsing performance
- Better WebSocket connection handling
- Enhanced worker health check mechanisms
- New `--limit-max-requests-jitter` for graceful load distribution

### Starlette 0.50+
- Improved routing performance
- Better type safety with state management
- Enhanced middleware processing pipeline

---

## 4. Migration Effort Estimate

### Phase 1: Raise Version Floors (Low Risk) — 1 hour

Update `pyproject.toml` minimum version constraints to ensure compatible versions are installed:

| Package | Current | Recommended |
|---|---|---|
| `fastapi` | `>=0.95.0` | `>=0.115.0` |
| `pydantic` | `>=2.0.0` | `>=2.10.0` |
| `pydantic-settings` | `>=2.0.0` | `>=2.5.0` |
| `uvicorn` | `>=0.22.0` | `>=0.32.0` |
| `starlette` | `>=0.46.0` | `>=0.50.0` (security: O(n²) DoS via Range header, patched in 0.49.1) |
| `httpx` | `>=0.24.0` | `>=0.27.0` |

**Risk:** Low. These are minimum floors — the resolver already installs newer versions.

### Phase 2: Fix Deprecated Starlette Patterns — 2 hours

- Migrate 2 `@app.on_event()` usages to `lifespan` context manager
- Review 1 `@app.middleware()` usage
- Test lifecycle behavior after changes

**Risk:** Low. Patterns are localized and well-understood.

### Phase 3: Adopt `Annotated` Dependency Injection — 8–12 hours

- Refactor 65+ endpoints to use `Annotated[Type, Depends()]` pattern
- Create reusable type aliases for common dependencies
- Update corresponding tests

**Risk:** Low–Medium. Mechanical refactoring, but touches many files. Old pattern continues to work, so this can be done incrementally.

### Phase 4: Starlette 1.0 Readiness (Future) — 2 hours

- Final review of deprecated patterns after Starlette 1.0 stable release
- Verify no `@app.exception_handler()` usage needs migration
- Test with Starlette 1.0rc1

**Risk:** Low. Only needed when Starlette 1.0 ships and FastAPI requires it.

### Total Estimated Effort

| Phase | Effort | Priority | Risk |
|---|---|---|---|
| Raise version floors | 1 hour | **High** | Low |
| Fix deprecated lifecycle | 2 hours | **High** | Low |
| Adopt `Annotated` DI | 8–12 hours | Medium | Low–Medium |
| Starlette 1.0 readiness | 2 hours | Low | Low |
| **Total** | **13–17 hours** | | |

---

## 5. Upgrade Recommendations

### Immediate Actions (This PR)

1. **Raise `pyproject.toml` version floors** to recommended minimums. This does not change what gets installed (the resolver already picks the latest compatible version) but ensures that incompatible older versions cannot be resolved.

### Short-Term (Next Sprint)

2. **Migrate deprecated Starlette lifecycle patterns** (2–3 instances). Small, localized changes that eliminate deprecation warnings and prepare for Starlette 1.0.

3. **Add `Content-Type` headers to test HTTP clients** if not already present, to comply with FastAPI 0.132+ strict checking.

### Medium-Term (Dedicated Refactoring Sprint)

4. **Adopt `Annotated` dependency injection** across all 65+ endpoints. This is a mechanical refactoring that improves editor support, reduces duplication, and follows the official FastAPI recommendation. Can be done file-by-file.

### Long-Term (When Starlette 1.0 Releases)

5. **Validate Starlette 1.0 compatibility** once it moves from rc to stable and FastAPI updates its constraint.

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Raising version floors breaks resolution | Low | Medium | Test with `uv lock --check` before merging |
| Strict Content-Type checking breaks tests | Medium | Low | Add headers to test clients |
| `Annotated` refactoring introduces bugs | Low | Medium | Incremental migration with per-file testing |
| Starlette 1.0 incompatibility | Low | High | Pin Starlette below 1.0 until validated |

---

## References

- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/)
- [FastAPI Breaking Changes & Migration](https://deepwiki.com/fastapi/fastapi/8.2-breaking-changes-and-migration)
- [Pydantic V2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Pydantic V2.12 Release Announcement](https://pydantic.dev/articles/pydantic-v2-12-release)
- [Uvicorn Release Notes](https://uvicorn.dev/release-notes/)
- [Starlette Release Notes](https://starlette.dev/release-notes/)
- [Starlette 1.0.0rc1 Changelog](https://github.com/Kludex/starlette/releases)
