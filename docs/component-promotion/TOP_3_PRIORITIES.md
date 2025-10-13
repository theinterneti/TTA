# Top 3 Priority Components for Staging Promotion

**Last Updated**: 2025-10-13
**Planning Horizon**: Next 2 weeks (2025-10-14 to 2025-10-27)

---

## Executive Summary

Based on the comprehensive component maturity assessment, the following 3 components are prioritized for staging promotion over the next 2 weeks:

| Priority | Component | Coverage | Effort | Target Date | Status |
|----------|-----------|----------|--------|-------------|--------|
| **P0** | Narrative Arc Orchestrator | 70.3% ✅ | 1-2 days | 2025-10-15 | 🟡 Ready (after blockers) |
| **P1** | Model Management | 100% ✅ | 2-3 days | 2025-10-17 | 🔴 Code quality issues |
| **P1** | Gameplay Loop | 100% ✅ | 2-3 days | 2025-10-17 | 🔴 Code quality issues |

**Total Estimated Effort**: 5-8 days
**Expected Outcome**: 3 additional components in staging by 2025-10-17

---

## Priority 1: Narrative Arc Orchestrator ⭐

### Status
🟡 **READY FOR STAGING** (after blocker resolution)

### Why This Component First?
- ✅ Already exceeds 70% coverage threshold (70.3%)
- ✅ All blockers are fixable within 1-2 days
- ✅ No architectural or design issues
- ✅ Quick win to validate promotion workflow
- ✅ Low risk (no external dependencies)

### Current Metrics
- **Test Coverage**: 70.3% (exceeds 70% requirement by 0.3%)
- **Tests Passing**: ✅ All passing
- **Core Features**: ✅ Complete
- **Security**: ✅ Passing

### Blockers (3 total)
1. ❌ **150 linting issues** (2-3 hours to fix)
2. ❌ **21 type checking errors** (3-4 hours to fix)
3. ❌ **Missing README** (1-2 hours to create)

### Action Plan
**Script**: `scripts/promote-narrative-arc-orchestrator.sh`
**Tracking**: `docs/component-promotion/NARRATIVE_ARC_ORCHESTRATOR_BLOCKERS.md`
**Promotion Issue**: #45

**Timeline**:
- **Day 1 (2025-10-14)**: Fix linting + type checking (5-7 hours)
- **Day 2 (2025-10-15)**: Create README, validate, deploy (3-4 hours)

**Commands**:
```bash
# Run automated promotion script
./scripts/promote-narrative-arc-orchestrator.sh

# Or run phases individually
./scripts/promote-narrative-arc-orchestrator.sh --phase 1  # Linting
./scripts/promote-narrative-arc-orchestrator.sh --phase 2  # Type checking
./scripts/promote-narrative-arc-orchestrator.sh --phase 3  # README
./scripts/promote-narrative-arc-orchestrator.sh --phase 4  # Validate
```

### Success Criteria
- ✅ All linting issues resolved (0 errors)
- ✅ All type checking errors resolved (0 errors)
- ✅ README created with all required sections
- ✅ Test coverage maintained at ≥70%
- ✅ All tests passing
- ✅ Deployed to staging environment

### Next Steps After Promotion
1. Monitor staging deployment for 7 days
2. Run integration tests
3. Collect performance metrics
4. Consider production promotion after observation period

---

## Priority 2: Model Management

### Status
🔴 **DEVELOPMENT** (needs code quality fixes)

### Why This Component Second?
- ✅ Already at 100% test coverage
- ✅ Only needs code quality fixes (no new tests required)
- ✅ Critical for LLM integration
- ⚠️ Has security issue that needs addressing

### Current Metrics
- **Test Coverage**: 100% ✅ (exceeds 70% requirement)
- **Tests Passing**: ✅ All passing
- **Core Features**: ✅ Complete
- **Security**: ⚠️ Medium severity issue (B615)

### Blockers (3 total)
1. ❌ **665 linting issues**
2. ❌ **Type checking errors**
3. ❌ **Security: B615** (Hugging Face unsafe download)

### Action Plan
**Estimated Effort**: 2-3 days
**Target Deployment**: 2025-10-17

**Phase 1: Linting (1 day)**
```bash
# Scan for issues
uvx ruff check src/components/model_management/ > model_mgmt_linting.txt

# Auto-fix
uvx ruff check --fix src/components/model_management/

# Verify
uvx ruff check src/components/model_management/
```

**Phase 2: Type Checking (1 day)**
```bash
# Scan for errors
uvx pyright src/components/model_management/ > model_mgmt_types.txt

# Fix manually (add type hints, null checks)
# ...

# Verify
uvx pyright src/components/model_management/
```

**Phase 3: Security (4 hours)**
```bash
# Scan for security issues
uvx bandit -r src/components/model_management/ -ll

# Fix B615: Use safe download methods for Hugging Face
# Replace unsafe download with verified download
# ...

# Verify
uvx bandit -r src/components/model_management/ -ll
```

**Phase 4: Validation (1 hour)**
```bash
# Run all checks
uvx ruff check src/components/model_management/
uvx pyright src/components/model_management/
uvx bandit -r src/components/model_management/ -ll
uv run pytest tests/test_model_management_component.py --cov=src/components/model_management
```

### Success Criteria
- ✅ All linting issues resolved (0 errors)
- ✅ All type checking errors resolved (0 errors)
- ✅ Security issue B615 resolved
- ✅ Test coverage maintained at 100%
- ✅ All tests passing
- ✅ Deployed to staging environment

### Next Steps
1. Create promotion issue
2. Document blockers
3. Execute action plan
4. Deploy to staging
5. Monitor for 7 days

---

## Priority 3: Gameplay Loop

### Status
🔴 **DEVELOPMENT** (needs code quality fixes)

### Why This Component Third?
- ✅ Already at 100% test coverage
- ✅ Only needs code quality fixes (no new tests required)
- ✅ **Critical for player experience** (P0 priority)
- ⚠️ Has significant linting issues (1,247 issues)

### Current Metrics
- **Test Coverage**: 100% ✅ (exceeds 70% requirement)
- **Tests Passing**: ✅ All passing
- **Core Features**: ✅ Complete
- **Security**: ✅ Passing

### Blockers (3 total)
1. ❌ **1,247 linting issues** (Issue #22)
2. ❌ **Type checking errors**
3. ❌ **Missing README**

### Action Plan
**Estimated Effort**: 2-3 days
**Target Deployment**: 2025-10-17
**Blocker Issue**: #22

**Phase 1: Linting (1-2 days)**
```bash
# Scan for issues (already documented in Issue #22)
uvx ruff check src/components/gameplay_loop/ > gameplay_linting.txt

# Auto-fix (will resolve ~80% of issues)
uvx ruff check --fix src/components/gameplay_loop/

# Manual fixes for remaining issues
# ...

# Verify
uvx ruff check src/components/gameplay_loop/
```

**Phase 2: Type Checking (1 day)**
```bash
# Scan for errors
uvx pyright src/components/gameplay_loop/ > gameplay_types.txt

# Fix manually (add type hints, null checks)
# ...

# Verify
uvx pyright src/components/gameplay_loop/
```

**Phase 3: README (2 hours)**
```bash
# Copy template
cp src/components/carbon/README.md src/components/gameplay_loop/README.md

# Edit with component-specific details
nano src/components/gameplay_loop/README.md
```

**Phase 4: Validation (1 hour)**
```bash
# Run all checks
uvx ruff check src/components/gameplay_loop/
uvx pyright src/components/gameplay_loop/
uvx bandit -r src/components/gameplay_loop/ -ll
uv run pytest tests/test_gameplay_loop_component.py --cov=src/components/gameplay_loop
```

### Success Criteria
- ✅ All 1,247 linting issues resolved (0 errors)
- ✅ All type checking errors resolved (0 errors)
- ✅ README created with all required sections
- ✅ Test coverage maintained at 100%
- ✅ All tests passing
- ✅ Deployed to staging environment

### Next Steps
1. Update Issue #22 with action plan
2. Execute action plan
3. Deploy to staging
4. Monitor for 7 days
5. Consider production promotion (critical for player experience)

---

## Timeline Summary

### Week 1: 2025-10-14 to 2025-10-20

**Monday 2025-10-14**
- ✅ Narrative Arc Orchestrator: Fix linting + type checking

**Tuesday 2025-10-15**
- ✅ Narrative Arc Orchestrator: Create README, validate, deploy to staging
- ✅ Model Management: Begin linting fixes

**Wednesday 2025-10-16**
- ✅ Model Management: Complete linting, begin type checking
- ✅ Gameplay Loop: Begin linting fixes

**Thursday 2025-10-17**
- ✅ Model Management: Complete type checking, fix security issue
- ✅ Gameplay Loop: Continue linting fixes

**Friday 2025-10-18**
- ✅ Model Management: Validate and deploy to staging
- ✅ Gameplay Loop: Complete linting, begin type checking

### Week 2: 2025-10-21 to 2025-10-27

**Monday 2025-10-21**
- ✅ Gameplay Loop: Complete type checking, create README

**Tuesday 2025-10-22**
- ✅ Gameplay Loop: Validate and deploy to staging
- ✅ Monitor all 3 components in staging

**Wednesday-Friday 2025-10-23 to 2025-10-25**
- ✅ Continue monitoring staging deployments
- ✅ Begin work on next priority components (LLM, Docker, Player Experience)

---

## Success Metrics

### By 2025-10-17 (End of Week 1)
- ✅ 3 components promoted to staging
- ✅ 6 total components in staging (50% of total)
- ✅ Promotion workflow validated with 3 successful promotions

### By 2025-10-27 (End of Week 2)
- ✅ All 3 components stable in staging
- ✅ Integration tests passing
- ✅ Performance metrics collected
- ✅ Ready to begin production promotions

---

## Risk Mitigation

### Risk 1: Linting Fixes Take Longer Than Expected
**Mitigation**: Use auto-fix for 80% of issues, focus manual effort on critical issues only

### Risk 2: Type Checking Reveals Architectural Issues
**Mitigation**: Document issues, create follow-up tasks, don't block promotion for non-critical issues

### Risk 3: Security Issue (B615) Requires Significant Refactoring
**Mitigation**: Implement safe download wrapper, defer full refactoring to post-staging

### Risk 4: Staging Deployment Failures
**Mitigation**: Test deployment in dev environment first, have rollback plan ready

---

## Related Documentation

- **Component Maturity Status**: `docs/component-promotion/COMPONENT_MATURITY_STATUS.md`
- **Narrative Arc Orchestrator Blockers**: `docs/component-promotion/NARRATIVE_ARC_ORCHESTRATOR_BLOCKERS.md`
- **Promotion Script**: `scripts/promote-narrative-arc-orchestrator.sh`
- **Promotion Issues**: #45 (Narrative Arc Orchestrator), #22 (Gameplay Loop)
- **Status Report**: Issue #42

---

**Last Updated**: 2025-10-13
**Next Review**: 2025-10-14
**Maintained By**: @theinterneti
