# ML/AI Stack Audit: PyTorch, Transformers, LangChain, LangGraph

**Date:** 2026-03-04
**Assessed by:** GitHub Copilot
**Issue:** Phase 1 — Dependency Audit & Research
**Effort:** 4 hours (research)
**Priority:** Critical

---

## Executive Summary

This audit evaluates the current ML/AI dependency stack in TTA against latest available
versions, focusing on Python 3.14 compatibility, breaking changes, and migration effort.

**Key Findings:**
- ✅ **PyTorch Python 3.14**: Fully supported since PyTorch 2.10.0 (released Jan 21, 2026). TTA already resolves to 2.10.0 — **no blocker**.
- ⚠️ **Transformers v4→v5**: Major version jump. v5 drops TensorFlow/Flax, requires PyTorch 2.4+, Python 3.10+. Lock file shows both 4.57.6 and 5.2.0 resolved.
- ⚠️ **LangChain v0.3→v1.0**: Significant breaking changes — new agent API (`create_agent`), TypedDict state (no Pydantic), middleware-driven architecture.
- ⚠️ **LangGraph v0.2→v1.0**: Context API replaces config, typed interrupts, new streaming modes. Tightly coupled to LangChain v1.0.

**Recommendation:** **GO** for Phase 4 migration. PyTorch 3.14 blocker is resolved. Prioritize LangChain/LangGraph migration (highest impact), then Transformers.

---

## 1. Current State

### Version Floors (pyproject.toml)

| Package | Spec (pyproject.toml) | Resolved (uv.lock) | Latest Available |
|---------|----------------------|---------------------|------------------|
| torch | `>=2.0.0` | 2.10.0 | 2.10.0 |
| transformers | `>=4.30.0` | 4.57.6 / 5.2.0 | 5.2.0 |
| datasets | `>=2.12.0` | 2.14.4 / 4.5.0 | 4.5.0 |
| accelerate | `>=0.20.0` | 1.12.0 | 1.12.0 |
| huggingface_hub | `>=0.20.0` | 0.36.2 / 1.4.1 | 1.4.1 |
| sentencepiece | `>=0.1.99` | 0.2.1 | 0.2.1 |
| tokenizers | `>=0.13.3` | 0.22.2 | 0.22.2 |
| timm | `>=1.0.0` | 1.0.24 | 1.0.24 |
| torchvision | `>=0.21.0` | 0.25.0 | 0.25.0 |
| torchaudio | `>=2.6.0` | 2.10.0 | 2.10.0 |
| tensorboard | `>=2.19.0` | 2.20.0 | 2.20.0 |
| tensorboardX | `>=2.6.0` | 2.6.4 | 2.6.4 |
| langchain-core | `>=0.3.0` | 1.2.14 | 1.2.14 |
| langchain-openai | `>=0.2.0` | 1.1.10 | 1.1.10 |
| langgraph | `>=0.2.0` | 1.0.9 | 1.0.9 |
| langgraph-checkpoint | (transitive) | 4.0.0 | 4.0.0 |
| langgraph-prebuilt | (transitive) | 1.0.8 | 1.0.8 |
| langgraph-sdk | (transitive) | 0.3.8 | 0.3.8 |

### Dependency Locations

The ML/AI dependencies appear in three places in `pyproject.toml`:
1. **Main dependencies** (lines 43–54, 96–98): Full ML stack + LangChain/LangGraph
2. **`[project.optional-dependencies] minimal`** (lines 159–161): torch, transformers, huggingface_hub
3. **`[project.optional-dependencies] gpu`** (lines 247–254): torch, transformers, accelerate, timm, torchvision, torchaudio, tensorboard

Additionally, `packages/tta-ai-framework/pyproject.toml` (lines 21–23) declares:
- `langchain-core>=0.3.0`
- `langchain-openai>=0.2.0`
- `langgraph>=0.2.0`

---

## 2. PyTorch Python 3.14 Support

### ✅ Status: RESOLVED — No Longer Blocking

| Milestone | Date | Status |
|-----------|------|--------|
| Python 3.14 released | Oct 2025 | ✅ |
| PyTorch nightly builds with 3.14 | Nov 2025 | ✅ |
| PyTorch 2.10 RC with 3.14 support | Jan 2026 | ✅ |
| PyTorch 2.10.0 GA | Jan 21, 2026 | ✅ |
| torch.compile on Python 3.14 | Jan 2026 | ✅ |
| Free-threaded Python 3.14t | Experimental | ⚠️ |

**Details:**
- PyTorch 2.10.0 officially supports Python 3.14 on Linux, macOS, and Windows.
- `torch.compile` is fully compatible with Python 3.14.
- Free-threaded (no-GIL) Python 3.14t has experimental support in nightly builds; multi-threading features are still being refined.
- **TorchScript caveat:** Some TorchScript functionality is broken on Python 3.14+; tests are being skipped upstream. TTA does not use TorchScript, so this is not a concern.

**TTA Impact:** The uv.lock already resolves to torch 2.10.0. No code changes needed for PyTorch Python 3.14 support. The version floor `>=2.0.0` is very permissive and could be raised to `>=2.4.0` for security/compatibility reasons.

### References
- [PyTorch 2.10 Release Blog](https://pytorch.org/blog/pytorch-2-10-release-blog/)
- [Python 3.14 Support Issue #156856](https://github.com/pytorch/pytorch/issues/156856)
- [torch.compile Python 3.14 Announcement](https://dev-discuss.pytorch.org/t/torch-compile-support-for-python-3-14-completed/3276)

---

## 3. Transformers v4 → v5

### Breaking Changes

| Change | Impact on TTA | Severity |
|--------|---------------|----------|
| TensorFlow/Flax dropped | None (TTA uses PyTorch only) | 🟢 None |
| Requires Python 3.10+ | TTA requires 3.12+ already | 🟢 None |
| Requires PyTorch 2.4+ | TTA resolves to 2.10.0 | 🟢 None |
| Unified processor APIs | Low impact (AutoClasses used) | 🟡 Low |
| Quantization first-class | Beneficial (no migration needed) | 🟢 None |
| Cache utilities changed | Check local provider code | 🟡 Low |
| `transformers serve` command | New feature, no migration | 🟢 None |

### TTA Usage (2 files)

**`src/components/model_management/providers/local.py`**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
```

**`packages/tta-ai-framework/src/tta_ai/models/providers/local.py`**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
```

**Migration Assessment:** LOW effort. TTA uses AutoClasses (`AutoModelForCausalLM`, `AutoTokenizer`) and the `pipeline` API, which are the recommended forward-compatible patterns in Transformers v5. The `>=4.30.0` floor allows both v4 and v5; the lock file already resolves a v5 version (5.2.0) on some platforms.

### Recommended Version Floor Update
- Current: `transformers>=4.30.0`
- Recommended: `transformers>=4.45.0` (minimum for stable v4 with v5-compatible APIs)
- Aggressive: `transformers>=5.0.0` (commit to v5-only)

### References
- [Transformers v5 Blog](https://huggingface.co/blog/transformers-v5)
- [Transformers v5 Compatibility Guide](https://markaicode.com/transformers-version-compatibility-guide/)
- [PyPI: transformers](https://pypi.org/project/transformers/)

---

## 4. LangChain v0.3 → v1.0

### Breaking Changes

| Change | Impact on TTA | Severity |
|--------|---------------|----------|
| `create_agent` replaces `AgentExecutor` | TTA uses `StateGraph` directly | 🟡 Low |
| Agent state: TypedDict only (no Pydantic) | Must audit state definitions | 🟠 Medium |
| `prompt` → `system_prompt` | Check prompt construction | 🟡 Low |
| Middleware replaces callbacks | Check hook/callback usage | 🟡 Low |
| `langchain-classic` for legacy chains | TTA doesn't use legacy chains | 🟢 None |
| Structured message content blocks | Message type changes | 🟠 Medium |
| Streaming node `"agent"` → `"model"` | Check streaming code | 🟡 Low |
| Graph-based execution default | Aligns with existing LangGraph use | 🟢 None |

### TTA Usage (6 files)

**langchain_core (message types):**
- `src/ai_components/langgraph_integration.py` — `AIMessage, BaseMessage, HumanMessage, SystemMessage`
- `src/player_experience/services/message_service.py` — `AIMessage, HumanMessage, SystemMessage`
- `src/agent_orchestration/langgraph_orchestrator.py` — `AIMessage, BaseMessage, HumanMessage, SystemMessage`

**langchain_openai (LLM client):**
- `src/ai_components/langgraph_integration.py` — `ChatOpenAI`
- `src/ai_components/llm_factory.py` — `ChatOpenAI`
- `src/agent_orchestration/langgraph_orchestrator.py` — `ChatOpenAI`

**Migration Assessment:** MEDIUM effort. The core message types (`AIMessage`, `HumanMessage`, `SystemMessage`) are preserved in v1.0 but now support structured content blocks. `ChatOpenAI` is maintained in `langchain-openai`. The main risk is if TTA accesses `.content` as a plain string — in v1.0, content may be a list of content blocks.

### Key Migration Steps
1. Audit all `.content` accesses on message objects for string vs content-block handling
2. Verify `ChatOpenAI` constructor parameters haven't changed
3. Check if any code uses `AgentExecutor` or legacy chain patterns (not found in current code)
4. Update any callback-based patterns to middleware if applicable

### Recommended Version Floor Update
- Current: `langchain-core>=0.3.0`, `langchain-openai>=0.2.0`
- Already resolved: `langchain-core==1.2.14`, `langchain-openai==1.1.10`
- Recommended: Raise floors to `langchain-core>=1.0.0`, `langchain-openai>=1.0.0` after validation

### References
- [LangChain v1 Migration Guide](https://docs.langchain.com/oss/python/migrate/langchain-v1)
- [LangChain v1 GA Announcement](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/langchain-v1-is-now-generally-available/4462159)
- [Lessons Learned from Upgrading to LangChain 1.0](https://towardsdatascience.com/lessons-learnt-from-upgrading-to-langchain-1-0-in-production/)

---

## 5. LangGraph v0.2 → v1.0

### Breaking Changes

| Change | Impact on TTA | Severity |
|--------|---------------|----------|
| `config_schema` → `context_schema` | Check graph construction | 🟠 Medium |
| Typed interrupts API | Check interrupt usage | 🟡 Low |
| `createReactAgent` → `createAgent` | TTA uses `StateGraph` directly | 🟢 None |
| State: TypedDict required | Audit state definitions | 🟠 Medium |
| Streaming modes refined | Check stream consumers | 🟡 Low |
| Checkpointing/time-travel | New feature (beneficial) | 🟢 None |
| Context API for run-scoped data | Check runtime config patterns | 🟠 Medium |

### TTA Usage (2 files)

**`src/ai_components/langgraph_integration.py`:**
```python
from langgraph.graph import END, StateGraph
```

**`src/agent_orchestration/langgraph_orchestrator.py`:**
```python
from langgraph.graph import END, StateGraph
```

**Migration Assessment:** MEDIUM effort. TTA uses `StateGraph` and `END` from LangGraph, which are the core building blocks preserved in v1.0. The main risks are:
1. State definition format changes (must be TypedDict)
2. Runtime config vs context API changes
3. Any graph construction parameter changes

### Key Migration Steps
1. Verify `StateGraph` constructor API compatibility
2. Audit all state type definitions (ensure TypedDict, not Pydantic)
3. Replace any `config_schema` usage with `context_schema`
4. Test graph compilation and execution
5. Verify streaming behavior if used

### Recommended Version Floor Update
- Current: `langgraph>=0.2.0`
- Already resolved: `langgraph==1.0.9`
- Recommended: Raise floor to `langgraph>=1.0.0` after validation

### References
- [LangGraph v1 Migration Guide](https://docs.langchain.com/oss/javascript/migrate/langgraph-v1)
- [LangGraph 0.6.0 Release](https://newreleases.io/project/github/langchain-ai/langgraph/release/0.6.0)
- [LangGraph on PyPI](https://pypi.org/project/langgraph/)

---

## 6. Migration Effort Estimate

### Summary Table

| Component | Files Affected | Effort | Risk | Priority |
|-----------|---------------|--------|------|----------|
| PyTorch 3.14 support | 0 (already resolved) | None | 🟢 None | — |
| Raise version floors | 3 (pyproject.toml files) | 1 hour | 🟢 Low | P2 |
| Transformers v4→v5 | 2 source files | 2–4 hours | 🟡 Low | P3 |
| LangChain v0.3→v1.0 | 4 source files | 4–8 hours | 🟠 Medium | P1 |
| LangGraph v0.2→v1.0 | 2 source files | 4–8 hours | 🟠 Medium | P1 |
| Integration testing | All affected files | 4–8 hours | 🟠 Medium | P1 |
| **Total** | **8 unique files** | **15–29 hours** | | |

### Detailed Breakdown

#### Phase 4a: Version Floor Updates (1 hour)
- Update `pyproject.toml` version floors to match resolved versions
- Update `packages/tta-ai-framework/pyproject.toml`
- Run `uv lock` to verify resolution
- No code changes needed

#### Phase 4b: LangChain + LangGraph Migration (8–16 hours)
- **Coupled migration** — LangChain and LangGraph v1.0 should be migrated together
- Audit message `.content` usage for content-block compatibility
- Audit state definitions for TypedDict compliance
- Update any `config_schema` → `context_schema`
- Update streaming consumers if applicable
- Comprehensive integration testing

#### Phase 4c: Transformers v5 Migration (2–4 hours)
- Verify AutoClass API compatibility
- Test `pipeline` function with v5
- Check for deprecated tokenizer patterns
- Run local model loading tests

#### Phase 4d: Validation & Testing (4–8 hours)
- Run full test suite with updated dependencies
- Test agent orchestration workflows end-to-end
- Test local model loading and inference
- Performance regression testing

---

## 7. Go/No-Go Decision

### ✅ GO — Phase 4 Migration Approved

| Criterion | Status | Notes |
|-----------|--------|-------|
| PyTorch Python 3.14 | ✅ Supported | 2.10.0 GA since Jan 2026 |
| Transformers compatible | ✅ Compatible | v5.2.0 works with PyTorch 2.10 |
| LangChain stable | ✅ v1.0 GA | Migration guide available |
| LangGraph stable | ✅ v1.0 GA | Coupled with LangChain v1.0 |
| Migration effort reasonable | ✅ 15–29 hours | 8 files, well-scoped |
| Breaking changes manageable | ✅ Medium risk | No architectural overhaul needed |

### Risk Mitigation
1. **Branch-based migration:** Create a feature branch for the full migration
2. **Coupled LangChain+LangGraph:** Migrate together to avoid version incompatibilities
3. **Incremental testing:** Test each component migration independently
4. **Rollback plan:** Version floors can be reverted if issues arise

### Timeline Recommendation
- **Immediate:** Raise version floors to codify already-resolved versions
- **Sprint 1 (1–2 weeks):** LangChain + LangGraph v1.0 migration
- **Sprint 2 (1 week):** Transformers v5 migration + validation
- **Sprint 3 (1 week):** Integration testing + performance validation

---

## 8. Security Considerations

| Package | Known Vulnerabilities | Action |
|---------|----------------------|--------|
| transformers 5.2.0 | Deserialization vulnerabilities reported | Review Sonatype advisory; ensure untrusted model loading is sandboxed |
| torch 2.10.0 | None critical at time of audit | Monitor PyTorch security advisories |
| langchain-core 1.2.14 | None critical at time of audit | Monitor LangChain security advisories |
| langgraph 1.0.9 | None critical at time of audit | Monitor LangGraph security advisories |

---

## Appendix A: Files Requiring Migration

| File | Dependencies Used | Migration Type |
|------|-------------------|----------------|
| `src/components/model_management/providers/local.py` | torch, transformers | Transformers v5 API check |
| `packages/tta-ai-framework/src/tta_ai/models/providers/local.py` | torch, transformers | Transformers v5 API check |
| `src/ai_components/langgraph_integration.py` | langchain-core, langchain-openai, langgraph | LangChain+LangGraph v1.0 |
| `src/ai_components/llm_factory.py` | langchain-openai | LangChain v1.0 |
| `src/player_experience/services/message_service.py` | langchain-core | LangChain v1.0 message types |
| `src/agent_orchestration/langgraph_orchestrator.py` | langchain-core, langchain-openai, langgraph | LangChain+LangGraph v1.0 |

## Appendix B: Unused Dependencies

The following ML/AI dependencies are declared but have **no imports found** in the codebase:

| Package | Spec | Recommendation |
|---------|------|----------------|
| accelerate | `>=0.20.0` | Keep for GPU training workflows |
| datasets | `>=2.12.0` | Keep for data pipeline support |
| sentencepiece | `>=0.1.99` | Keep as tokenizer backend |
| tokenizers | `>=0.13.3` | Keep as transformers dependency |
| timm | `>=1.0.0` | Evaluate — may be removable if no vision models used |
| tensorboard | `>=2.19.0` | Keep for training monitoring |
| tensorboardX | `>=2.6.0` | Evaluate — may be redundant with tensorboard |

---

**Last Updated:** 2026-03-04
**Status:** Complete — Research Phase
**Next Action:** Phase 4 migration (estimated 15–29 hours)
