# Memory System & Packaging Strategy - Implementation Roadmap

**Date:** 2025-10-28
**Status:** 🎯 READY FOR EXECUTION
**Tracking:** Hybrid (Task List + GitHub Issues)

---

## Overview

This roadmap tracks the extraction of the Redis-based memory system from TTA to TTA.dev and fixes critical packaging issues. Work is tracked using:

1. **Task List** - Immediate planning and progress tracking (this conversation)
2. **GitHub Issues** - Long-term tracking, PR integration, collaboration

---

## Phase 0: Immediate Fixes (Critical) 🔴

**Timeline:** 1-2 days
**Priority:** CRITICAL - Blocks all other work
**GitHub Issue:** Create issue using `.github/ISSUE_TEMPLATE/packaging-fixes.md`

### Tasks

- [ ] Fix workspace configuration in pyproject.toml
  - Add `packages/ai-dev-toolkit` to workspace members
  - Add `packages/universal-agent-context` to workspace members
  - Validate with `uv sync --all-extras`

- [ ] Standardize Python version to 3.12+
  - Update root `pyproject.toml`: `requires-python = ">=3.12"`
  - Update all package `pyproject.toml` files
  - Update CI/CD workflows to use Python 3.12

- [ ] Add version constraints for workspace packages
  - Pin workspace package versions in root dependencies
  - Update lock file (`uv.lock`)
  - Commit and validate

- [ ] Validate workspace configuration
  - Clean environment: `rm -rf .venv uv.lock`
  - Fresh install: `uv sync --all-extras`
  - Run tests: `uv run pytest -v`
  - Run quality checks: Ruff + Pyright

### Success Criteria

✅ All 4 packages recognized in workspace
✅ Python 3.12 used consistently
✅ All tests pass
✅ CI/CD passes
✅ No dependency conflicts

---

## Phase 1: Memory System Extraction Planning 📋

**Timeline:** 2-3 days
**Priority:** HIGH
**Dependencies:** Phase 0 complete

### Tasks

- [ ] Analyze current memory system implementation
  - Document all components to extract
  - Identify TTA-specific vs. generic code
  - Map dependencies and call sites

- [ ] Design tta-agent-coordination package
  - Define package structure
  - Design generic interfaces
  - Plan API surface

- [ ] Create extraction specification
  - List files to extract
  - List files to keep in TTA
  - Define generalization strategy

- [ ] Write migration guide
  - Document how TTA will use new package
  - Plan refactoring steps
  - Identify breaking changes

### Deliverables

📄 `docs/MEMORY_SYSTEM_EXTRACTION_SPEC.md`
📄 `docs/TTA_MIGRATION_GUIDE.md`
📄 Package design document

---

## Phase 2: TTA.dev Package Creation 🏗️

**Timeline:** 1-2 weeks
**Priority:** HIGH
**Dependencies:** Phase 1 complete
**GitHub Issue:** Create issue using `.github/ISSUE_TEMPLATE/memory-system-extraction.md`

### Week 1: Package Setup & Code Extraction

**Day 1-2: Package Setup**
- [ ] Create `packages/tta-agent-coordination/` in TTA.dev
- [ ] Set up directory structure
- [ ] Create `pyproject.toml`
- [ ] Add to TTA.dev workspace configuration
- [ ] Set up CI/CD workflows

**Day 3-4: Code Extraction**
- [ ] Copy `RedisMessageCoordinator`
- [ ] Copy `RedisAgentRegistry`
- [ ] Copy circuit breaker patterns
- [ ] Copy retry logic
- [ ] Generalize agent types and models
- [ ] Remove TTA-specific code

**Day 5-6: Testing**
- [ ] Write unit tests (target: 100% coverage)
- [ ] Write integration tests
- [ ] Write adversarial tests
- [ ] Set up FakeRedis fallback for CI
- [ ] Run mutation testing

**Day 7: Documentation**
- [ ] Write README.md
- [ ] Write API documentation
- [ ] Create examples
- [ ] Write migration guide
- [ ] Update CHANGELOG.md

### Week 2: Review & Merge

**Day 8-9: Review & Merge**
- [ ] Self-review code
- [ ] Run validation script: `./scripts/validate-package.sh tta-agent-coordination`
- [ ] Create PR in TTA.dev
- [ ] Address review feedback
- [ ] Squash merge to main
- [ ] Tag release v0.1.0

### Success Criteria

✅ Package published to TTA.dev repository
✅ 100% test pass rate
✅ >80% test coverage (target: 100%)
✅ Zero critical security vulnerabilities
✅ Documentation complete and accurate
✅ Examples run without errors

---

## Phase 3: TTA Repository Refactoring 🔧

**Timeline:** 1 week
**Priority:** MEDIUM
**Dependencies:** Phase 2 complete
**GitHub Issue:** Create separate issue for TTA refactoring

### Tasks

**Day 1-2: Add Dependency**
- [ ] Add `tta-agent-coordination` to TTA dependencies
- [ ] Configure git source in `[tool.uv.sources]`
- [ ] Run `uv sync --all-extras`
- [ ] Verify package installation

**Day 3-4: Refactor TTA Code**
- [ ] Update imports to use `tta-agent-coordination`
- [ ] Refactor `enhanced_coordinator.py` to extend generic coordinator
- [ ] Update agent types to use generic `AgentId`
- [ ] Keep TTA-specific extensions separate

**Day 5: Update Tests**
- [ ] Update test imports
- [ ] Add tests for TTA-specific extensions
- [ ] Verify all tests pass
- [ ] Update test documentation

**Day 6-7: Validation & Deployment**
- [ ] Run full test suite
- [ ] Run quality checks
- [ ] Deploy to staging
- [ ] Validate in staging environment
- [ ] Deploy to production

### Success Criteria

✅ TTA uses `tta-agent-coordination` from TTA.dev
✅ All tests pass
✅ No regression in functionality
✅ Staging deployment successful
✅ Production deployment successful

---

## Phase 4: PyPI Publishing Setup 📦

**Timeline:** 3-5 days
**Priority:** MEDIUM
**Dependencies:** Phase 2 complete
**GitHub Issue:** Create separate issue for PyPI setup

### Tasks

**Day 1-2: PyPI Configuration**
- [ ] Create PyPI account (if needed)
- [ ] Configure PyPI API token
- [ ] Add token to GitHub Secrets
- [ ] Create publishing workflow

**Day 3: Test Publishing**
- [ ] Publish to TestPyPI
- [ ] Verify package installation from TestPyPI
- [ ] Test in clean environment
- [ ] Fix any issues

**Day 4: Production Publishing**
- [ ] Publish `tta-agent-coordination` v0.1.0 to PyPI
- [ ] Verify package on PyPI
- [ ] Test installation: `pip install tta-agent-coordination`
- [ ] Update documentation

**Day 5: Update TTA Dependency**
- [ ] Change TTA dependency from git to PyPI
- [ ] Update `pyproject.toml`: `tta-agent-coordination>=0.1.0`
- [ ] Remove git source configuration
- [ ] Validate and deploy

### Success Criteria

✅ Package published to PyPI
✅ Package installable via pip
✅ TTA uses PyPI package (not git)
✅ Version constraints working
✅ Documentation updated

---

## Tracking Strategy

### Task List (This Conversation)
**Use For:**
- Immediate planning and breakdown
- Progress tracking during active work
- Quick status updates
- Adjusting priorities on the fly

**Update Frequency:** Real-time during work sessions

### GitHub Issues
**Use For:**
- Long-term tracking (multi-day/week work)
- PR integration and review tracking
- Cross-repository coordination
- Permanent record and discussion

**Update Frequency:** Daily or at major milestones

### Synchronization
- Update task list → Mark GitHub issue progress
- Complete phase in task list → Close GitHub issue
- GitHub issue discussion → Update task list if scope changes

---

## Issue Creation Checklist

When creating GitHub issues:

### For TTA Repository
- [ ] Use `.github/ISSUE_TEMPLATE/packaging-fixes.md` for Phase 0
- [ ] Create custom issue for Phase 3 (TTA refactoring)
- [ ] Link to TTA.dev issues for context
- [ ] Add labels: `packaging`, `refactoring`, `tta.dev-migration`

### For TTA.dev Repository
- [ ] Use `.github/ISSUE_TEMPLATE/memory-system-extraction.md` for Phase 2
- [ ] Create custom issue for Phase 4 (PyPI publishing)
- [ ] Link to TTA issues for context
- [ ] Add labels: `enhancement`, `packaging`, `new-package`

### Cross-Repository Linking
```markdown
**Related Issues:**
- TTA: theinterneti/TTA#[ISSUE_NUMBER]
- TTA.dev: theinterneti/TTA.dev#[ISSUE_NUMBER]
```

---

## Next Steps

### Immediate (Today)
1. ✅ Review this roadmap
2. ⏭️ Create GitHub issue for Phase 0 (packaging fixes)
3. ⏭️ Start Phase 0 work (fix workspace configuration)

### This Week
1. Complete Phase 0 (packaging fixes)
2. Begin Phase 1 (extraction planning)
3. Create GitHub issue for Phase 2 (package creation)

### Next 2-4 Weeks
1. Complete Phase 2 (TTA.dev package creation)
2. Complete Phase 3 (TTA refactoring)
3. Begin Phase 4 (PyPI publishing)

---

## Success Metrics

### Overall Project Success
- [ ] All phases complete
- [ ] `tta-agent-coordination` published to PyPI
- [ ] TTA using PyPI package
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Zero critical issues

### Quality Metrics
- [ ] 100% test pass rate across all phases
- [ ] >80% test coverage for new package
- [ ] Zero security vulnerabilities
- [ ] CI/CD green across both repositories

---

**Last Updated:** 2025-10-28
**Maintained By:** @theinterneti
**Status:** 🎯 READY FOR EXECUTION



---
**Logseq:** [[TTA.dev/Docs/Memory_system_packaging_roadmap]]
