# Testing Stack Audit

**Issue**: #150 — Audit Testing Stack (pytest, hypothesis, mutmut)
**Date**: 2026-03-04
**Phase**: Phase 1 — Dependency Audit & Research
**Effort Estimate**: 2 hours (research), 4–8 hours (migration)

---

## 1. Version Matrix

| Package | pyproject.toml Floor | Resolved (uv.lock) | Latest Stable | Status |
|---|---|---|---|---|
| pytest | `>=7.3.1` | 9.0.2 | 9.0.2 | ✅ Already on latest |
| pytest-asyncio | `>=0.23.0` | 1.3.0 | 1.3.0 | ✅ Already on latest |
| hypothesis | `>=6.100.0` | 6.151.9 | 6.151.8+ | ✅ Already on latest |
| mutmut | `>=2.4.0` | 3.4.0 | 3.5.0 | ⚠️ One minor behind |
| pytest-benchmark | `>=4.0.0` | 5.2.3 | 5.2.3 | ✅ Already on latest |

### Key Insight

The `uv.lock` already resolves to the latest (or near-latest) versions. The version floor
constraints in `pyproject.toml` are conservative but don't block upgrades. This audit
recommends raising the floors to prevent accidental downgrades.

---

## 2. Python 3.14 Compatibility

| Package | Python 3.14 | Python 3.14t (free-threaded) | Notes |
|---|---|---|---|
| pytest 9.0.2 | ✅ Compatible | ✅ Tested in CI | Dropped Python 3.8 |
| pytest-asyncio 1.3.0 | ✅ Compatible | ✅ Tested in CI | Dropped Python 3.9 |
| hypothesis 6.151.x | ✅ Compatible | ✅ Expected | Actively maintained |
| mutmut 3.4.0+ | ❌ **Segfaults** | ❌ Broken | `setproctitle` crash on 3.14 ([#457](https://github.com/boxed/mutmut/issues/457)) |
| pytest-benchmark 5.2.3 | ✅ Compatible | ⚠️ Untested | No known issues |

### ⚠️ Mutmut Python 3.14 Blocker

Mutmut 3.x segfaults (exit code -11/SIGSEGV) on Python 3.14 due to the `setproctitle`
native extension. All mutants crash in the worker process. This is tracked in
[boxed/mutmut#457](https://github.com/boxed/mutmut/issues/457).

**Workarounds**:
- Run mutmut under Python ≤3.13 until upstream fix lands
- Use `cosmic-ray` (already in our deps) as an alternative mutation testing tool
- Monkey-patch `setproctitle` (unsupported, may break features)

---

## 3. Breaking Changes — pytest 7.x → 8.x → 9.x

### 3.1 High-Impact Changes

| Change | Impact | TTA Status |
|---|---|---|
| `py.path.local` → `pathlib.Path` | `tmpdir` fixture deprecated; use `tmp_path` | ✅ Minimal usage (2 files) |
| Test return values must be `None` | Tests returning non-None raise errors | ⚠️ ~200 files with `return` in tests — needs audit |
| Yield-style tests removed | Old parametrization pattern no longer works | ⚠️ ~30 tests use `yield` — needs verification |
| `pytest.warns()` re-emits unmatched warnings | May cause unexpected warning propagation | ✅ Not used in codebase |
| Collection order changes | Package/directory discovery may differ | ⚠️ Low risk with explicit `testpaths` config |
| Dropped Python 3.8 support | Minimum Python 3.9+ | ✅ TTA requires Python 3.12+ |

### 3.2 Low-Impact Changes

- `setup.py` removed from pytest itself (no impact on TTA)
- `FixtureManager` API internals changed (affects plugin authors only)
- Exception group support added (new feature, no migration needed)
- `verbosity_assertions` config option added (opt-in)
- `config.inicfg` deprecated (removed in pytest 10)

### 3.3 Codebase Scan Results

```
Pattern                          Files Found    Risk
─────────────────────────────    ───────────    ────
event_loop direct access         2              Medium — refactor to pytest-asyncio managed
py.path.local / tmpdir           2              Low — minimal usage
Scoped async fixtures            16+            Medium — verify loop_scope compat
Yield in test functions           ~30            Medium — verify they're fixtures not tests
pytest.warns()                   0              None
Custom event_loop fixture        0              None — using pytest-asyncio defaults
Total async test functions       200+           Low — asyncio_mode="auto" handles this
```

---

## 4. Breaking Changes — pytest-asyncio 0.23.x → 1.3.0

### 4.1 Critical Changes

| Change | Impact | TTA Status |
|---|---|---|
| `event_loop` fixture removed | Tests using the fixture will break | ✅ Not used as fixture |
| Loop scope semantics changed | `loop_scope` replaces `scope` for async | ✅ Config has `asyncio_default_fixture_loop_scope = "function"` |
| Dropped Python 3.9 | Minimum Python 3.10+ | ✅ TTA requires Python 3.12+ |
| Stricter config validation | Misconfigured scopes raise `UsageError` | ✅ Config is correct |
| `--asyncio-debug` CLI flag | New feature, opt-in | No action needed |

### 4.2 Async Test Improvements (New Features)

- **Optimized event loop creation**: Scoped loops created once per scope (faster test suites)
- **Flexible `loop_scope`**: Works outside class structures now
- **pytest 9 support**: First-class compatibility
- **Debug mode**: `--asyncio-debug` for event loop debugging

### 4.3 TTA-Specific Assessment

TTA's async test configuration is already well-aligned:
- `asyncio_mode = "auto"` — correct for pytest-asyncio 1.x
- `asyncio_default_fixture_loop_scope = "function"` — correct modern setting
- No custom `event_loop` fixtures — no migration needed
- 200+ async tests use `@pytest.mark.asyncio` or rely on auto mode — compatible

---

## 5. Breaking Changes — mutmut 2.x → 3.x

| Change | Impact | TTA Status |
|---|---|---|
| No module-level mutation | Only mutates inside functions | ⚠️ Reduced mutation coverage |
| Parallel worker model | Different process management | ✅ Should be transparent |
| `pyproject.toml` config preferred | Replaces `setup.cfg` | ✅ Already using pyproject.toml |
| Python 3.14 segfault | `setproctitle` crash | ❌ **Blocker for 3.14** |
| POSIX fork required | No Windows support without WSL | ✅ Linux/macOS development |

---

## 6. Migration Effort Estimate

### Immediate (No Code Changes Required)

| Task | Effort | Description |
|---|---|---|
| Raise version floors in `pyproject.toml` | 15 min | Align floors with resolved versions |
| Verify `uv.lock` resolves correctly | 5 min | Run `uv sync` and confirm |

**Total**: ~20 minutes

### Short-Term (Minor Refactoring)

| Task | Effort | Description |
|---|---|---|
| Audit `return` in test functions | 1 hour | Verify tests don't return non-None |
| Verify `yield` test patterns | 30 min | Confirm they're fixtures, not yield-tests |
| Refactor `event_loop` direct access | 30 min | 2 files using `asyncio.get_event_loop()` |
| Replace `tmpdir` with `tmp_path` | 15 min | 2 files with minimal usage |

**Total**: ~2.5 hours

### Future (When Upgrading to Python 3.14)

| Task | Effort | Description |
|---|---|---|
| Resolve mutmut Python 3.14 segfault | Blocked | Wait for upstream fix or switch to cosmic-ray |
| Test full suite on Python 3.14 | 2 hours | CI matrix addition |
| Address any 3.14 annotation changes | 1 hour | Deferred evaluation (PEP 649) |

**Total**: ~3 hours (once mutmut fix lands)

---

## 7. Recommended Version Floor Updates

```toml
# Current → Recommended
"pytest>=7.3.1"            →  "pytest>=9.0.0"
"pytest-asyncio>=0.23.0"   →  "pytest-asyncio>=1.0.0"
"hypothesis>=6.100.0"      →  "hypothesis>=6.130.0"
"mutmut>=2.4.0"            →  "mutmut>=3.4.0"
"pytest-benchmark>=4.0.0"  →  "pytest-benchmark>=5.0.0"
```

### Rationale

- **pytest ≥9.0.0**: We're already running 9.0.2; raising the floor prevents
  accidental use of 7.x/8.x which have different collection/path behavior.
- **pytest-asyncio ≥1.0.0**: The `event_loop` fixture removal and loop scope
  changes are foundational; locking to 1.x prevents regression.
- **hypothesis ≥6.130.0**: Conservative bump; ensures modern strategies and
  Python 3.14 compatibility fixes.
- **mutmut ≥3.4.0**: Major version with parallel execution; 2.x has different
  mutation scope. Note: Python 3.14 blocked.
- **pytest-benchmark ≥5.0.0**: Major version bump with improved timing accuracy.

---

## 8. Action Items

- [x] Check latest versions and Python 3.14 compatibility
- [x] Review pytest 8.x/9.x breaking changes
- [x] Document async test improvements
- [x] Estimate migration effort
- [x] Scan codebase for affected patterns
- [x] Document mutmut Python 3.14 blocker
- [ ] Raise version floors in `pyproject.toml` (this PR)
- [ ] Audit `return` statements in test functions (follow-up)
- [ ] Refactor `event_loop` direct access in 2 test files (follow-up)
- [ ] Add Python 3.14 to CI matrix when mutmut fix lands (follow-up)

---

## References

- [pytest Changelog](https://docs.pytest.org/en/stable/changelog.html)
- [pytest 9.0.0 Release](https://docs.pytest.org/en/stable/announce/release-9.0.0.html)
- [pytest-asyncio Changelog](https://pytest-asyncio.readthedocs.io/en/stable/reference/changelog.html)
- [pytest-asyncio 1.0 Migration Guide](https://thinhdanggroup.github.io/pytest-asyncio-v1-migrate/)
- [Hypothesis Changelog](https://hypothesis.readthedocs.io/en/latest/changelog.html)
- [mutmut Python 3.14 Segfault Issue](https://github.com/boxed/mutmut/issues/457)
- [Python 3.14 What's New](https://docs.python.org/3/whatsnew/3.14.html)
- [PyReadiness 3.14](https://pyreadiness.org/3.14/)
