# Repository Status and Workflow Escalation Strategy

**Date**: October 29, 2025
**Status**: Planning Document
**Branch**: fix/codecov-upload-on-failure

---

## Executive Summary

This document addresses two critical needs:

1. **Repository Status**: Audit and update documentation based on TTA.dev migrations
2. **Workflow Escalation**: Implement branch-based quality gate escalation

---

## Part 1: TTA.dev Migration Status Audit

### Components Already Migrated to TTA.dev

Based on `TTA_DEV_EXTRACTION_ASSESSMENT_REVISED.md` and repo analysis:

#### ✅ Completed Migrations

1. **Keploy Framework**
   - Location: `TTA.dev/packages/keploy-framework`
   - Status: Complete
   - Documentation: `KEPLOY_FRAMEWORK_EXTRACTION_COMPLETE.md`

2. **Observability Integration** (INCLUDING Dashboard)
   - Exported to: `export/tta-observability-integration/`
   - Status: Needs merge into TTA.dev
   - Features:
     - OpenTelemetry APM integration
     - Router/Cache/Timeout primitives
     - 6 Grafana dashboards (System, Agent, LLM, Component Maturity, Circuit Breaker, Performance)
     - Component maturity metrics
     - Circuit breaker observability
     - LLM usage and cost tracking

3. **Universal Agent Context**
   - Location: `packages/universal-agent-context/`
   - Status: Complete, already packaged
   - Features:
     - Cross-platform agentic primitives (`.github/`)
     - Augment CLI-specific primitives (`.augment/`)
     - Chat modes, workflows, instructions
     - Context management, memory system
   - Universal: Works across Claude, Gemini, Copilot, Augment

4. **AI Development Toolkit**
   - Location: `packages/ai-dev-toolkit/`
   - Status: Complete, already bundled
   - Components:
     - Workflow primitives (Router, Cache, Timeout, Retry)
     - Development primitives
     - OpenHands integration tools
     - Monitoring & observability
     - Workflow management (quality gates, stage handlers)

5. **TTA Dev Primitives** (Referenced in pyproject.toml)
   - Git Reference: `https://github.com/theinterneti/TTA.dev.git`
   - Branch: main
   - Subdirectory: `packages/tta-dev-primitives`

#### ⚠️ Python-Specific Components (Require Integration Strategy)

These components could be extracted but need careful integration to avoid context pollution:

1. **Comprehensive Test Battery**
   - Location: `tests/comprehensive_battery/`
   - Concern: Python-specific, may pollute universal context
   - Integration Strategy Needed: Language markers, clear boundaries

2. **Testing Infrastructure**
   - Mutation testing frameworks
   - Performance testing tools
   - Data pipeline tests

### Components Remaining in Main Repo

#### Core TTA Platform Components

1. **Agent Orchestration** (`src/agent_orchestration/`)
   - Multi-agent coordination
   - Circuit breakers
   - Messaging infrastructure
   - Status: Core TTA functionality, stays in main repo

2. **Gameplay Loop** (`src/components/gameplay_loop/`)
   - Narrative engine
   - Core mechanics
   - Status: P0 component, 100% coverage, needs staging promotion

3. **Player Experience** (`src/player_experience/`)
   - User-facing APIs
   - Frontend services
   - Status: TTA-specific, stays in main repo

4. **Living Worlds** (`src/living_worlds/`)
   - World state management
   - Dynamic world systems
   - Status: TTA-specific, stays in main repo

5. **Developer Dashboard** (`src/developer_dashboard/`)
   - TTA-specific configuration
   - Local monitoring UI
   - Status: TTA-specific (observability dashboards migrated to TTA.dev)

### Documentation That Needs Updating

1. **AGENTS.md** - Update with TTA.dev migration status
2. **README.md** - Clarify what's in TTA vs TTA.dev
3. **GEMINI.md** - Update with current architecture
4. **TTA_DEV_EXTRACTION_ASSESSMENT_REVISED.md** - Mark as accurate/verified

### Recommendations

1. **Complete Observability Migration**: Merge `export/tta-observability-integration/` into TTA.dev
2. **Document Boundary**: Create clear documentation on what belongs in TTA vs TTA.dev
3. **Test Battery Decision**: Decide whether to extract with language markers or keep in main repo
4. **Remove Dead References**: Clean up any references to `tta.dev/` directory (it doesn't exist locally, only remote repo)

---

## Part 2: Branch-Based Workflow Escalation Strategy

### Current Problem

All branches (experimental → production) receive the same level of quality checks, causing:
- Unnecessary friction on experimental work
- Slower iteration cycles
- CI/CD bottlenecks on low-risk branches

### Proposed Branch Hierarchy

```
experimental/* → development → staging → main (production)
   ↓                ↓            ↓          ↓
 Minimal       Moderate      Strict    Very Strict
```

### Quality Gate Definitions by Branch

#### Tier 1: Experimental Branches (`experimental/*`, `feat/*`, `fix/*`)

**Philosophy**: Fast iteration, minimal friction

**Required Checks**:
- ✅ Basic syntax check (ruff format check)
- ✅ Unit tests only (quick subset)
- ❌ NO integration tests
- ❌ NO type checking
- ❌ NO mutation testing
- ❌ NO security scans
- ❌ NO coverage requirements

**CI Time Target**: < 3 minutes

**Auto-Merge**: Disabled

**Example Use Case**: Rapid prototyping, spike solutions, proof-of-concepts

---

#### Tier 2: Development Branch (`development`)

**Philosophy**: Regular development work, moderate quality gates

**Required Checks**:
- ✅ Full linting (ruff check + format)
- ✅ Unit tests (all)
- ✅ Type checking (Pyright) - warnings allowed
- ✅ Basic security scan (Bandit)
- ⚠️ Integration tests (core only, mock fallbacks allowed)
- ❌ NO mutation testing
- ❌ NO E2E tests
- ❌ NO load tests

**Coverage Requirement**: ≥ 60%

**CI Time Target**: < 10 minutes

**Auto-Merge**: Enabled after checks pass

**Example Use Case**: Feature development, bug fixes, general iteration

---

#### Tier 3: Staging Branch (`staging`)

**Philosophy**: Pre-production validation, strict quality gates

**Required Checks**:
- ✅ Full linting (ruff check + format) - MUST pass
- ✅ Unit tests (all) - 100% pass rate
- ✅ Type checking (Pyright) - NO errors allowed
- ✅ Integration tests (all) - with real services
- ✅ E2E tests (core flows)
- ✅ Security scan (comprehensive)
- ✅ Mutation testing (targeted, ≥ 75% score)
- ⚠️ Load tests (smoke tests only)

**Coverage Requirement**: ≥ 70%

**Mutation Score**: ≥ 75%

**CI Time Target**: < 30 minutes

**Auto-Merge**: Enabled after 7-day observation period

**Component Promotion**: Development → Staging allowed

**Example Use Case**: Release candidates, pre-production testing

---

#### Tier 4: Main/Production Branch (`main`)

**Philosophy**: Production-ready code only, maximum quality gates

**Required Checks**:
- ✅ Full linting (ruff check + format) - MUST pass
- ✅ Unit tests (all) - 100% pass rate
- ✅ Type checking (Pyright) - NO errors, minimal warnings
- ✅ Integration tests (all) - with real services
- ✅ E2E tests (comprehensive)
- ✅ Security scan (comprehensive + manual review)
- ✅ Mutation testing (comprehensive, ≥ 85% score)
- ✅ Load tests (full suite)
- ✅ Performance regression tests
- ✅ Dependency vulnerability scan

**Coverage Requirement**: ≥ 85%

**Mutation Score**: ≥ 85%

**Cyclomatic Complexity**: ≤ 8

**File Size Limit**: ≤ 800 lines

**CI Time Target**: < 60 minutes (parallelized)

**Auto-Merge**: Disabled (manual approval required)

**Component Promotion**: Staging → Production allowed

**Example Use Case**: Production releases, critical patches

---

### Implementation Strategy

#### Phase 1: Workflow Configuration (Week 1)

1. Create reusable workflow templates:
   - `.github/workflows/templates/quality-tier1.yml` (Experimental)
   - `.github/workflows/templates/quality-tier2.yml` (Development)
   - `.github/workflows/templates/quality-tier3.yml` (Staging)
   - `.github/workflows/templates/quality-tier4.yml` (Production)

2. Add branch detection logic to existing workflows:
   ```yaml
   jobs:
     determine-tier:
       runs-on: ubuntu-latest
       outputs:
         tier: ${{ steps.detect.outputs.tier }}
       steps:
         - id: detect
           run: |
             if [[ "${{ github.base_ref }}" == "main" ]]; then
               echo "tier=4" >> $GITHUB_OUTPUT
             elif [[ "${{ github.base_ref }}" == "staging" ]]; then
               echo "tier=3" >> $GITHUB_OUTPUT
             elif [[ "${{ github.base_ref }}" == "development" ]]; then
               echo "tier=2" >> $GITHUB_OUTPUT
             else
               echo "tier=1" >> $GITHUB_OUTPUT
             fi
   ```

3. Modify existing workflows to conditionally run based on tier:
   ```yaml
   mutation-testing:
     needs: determine-tier
     if: needs.determine-tier.outputs.tier >= 3
     # ... mutation testing job
   ```

#### Phase 2: Testing & Validation (Week 2)

1. Test tier 1 (experimental) with dummy PRs
2. Test tier 2 (development) with active branches
3. Test tier 3 (staging) with promotion workflows
4. Test tier 4 (main) with controlled merge

#### Phase 3: Documentation & Rollout (Week 3)

1. Update `CONTRIBUTING.md` with branch strategy
2. Create `docs/WORKFLOW_ESCALATION_GUIDE.md`
3. Update GitHub branch protection rules
4. Train team on new workflow

#### Phase 4: Monitoring & Optimization (Ongoing)

1. Track CI/CD times per tier
2. Monitor false positive rates
3. Adjust thresholds based on feedback
4. Add more parallelization as needed

---

### Quality Gate Matrix

| Check | Experimental | Development | Staging | Production |
|-------|-------------|-------------|---------|------------|
| Syntax (Ruff Format) | ✅ | ✅ | ✅ | ✅ |
| Linting (Ruff Check) | ❌ | ✅ | ✅ | ✅ |
| Type Checking (Pyright) | ❌ | ⚠️ | ✅ | ✅ |
| Unit Tests | ⚠️ (subset) | ✅ | ✅ | ✅ |
| Integration Tests | ❌ | ⚠️ (core) | ✅ | ✅ |
| E2E Tests | ❌ | ❌ | ⚠️ (core) | ✅ |
| Security Scan | ❌ | ⚠️ (basic) | ✅ | ✅ |
| Mutation Testing | ❌ | ❌ | ⚠️ (≥75%) | ✅ (≥85%) |
| Load Tests | ❌ | ❌ | ⚠️ (smoke) | ✅ |
| Coverage Requirement | None | ≥60% | ≥70% | ≥85% |
| Auto-Merge | ❌ | ✅ | ⚠️ (7-day) | ❌ |
| Manual Approval | ❌ | ❌ | ❌ | ✅ |

**Legend**: ✅ = Required, ⚠️ = Partial/Conditional, ❌ = Not Required

---

### Benefits of This Approach

1. **Faster Iteration**: Experimental branches get immediate feedback without heavy checks
2. **Progressive Confidence**: Quality increases as code moves up the branch hierarchy
3. **Resource Optimization**: Expensive checks (mutation, load tests) only run when needed
4. **Clear Expectations**: Developers know what to expect based on target branch
5. **Risk Management**: Production changes get maximum scrutiny
6. **Component Maturity Alignment**: Matches TTA's development → staging → production component workflow

---

### Workflow Files to Modify

Priority order for implementation:

1. **High Priority** (Core CI/CD):
   - `.github/workflows/tests.yml` - Add tier-based test selection
   - `.github/workflows/code-quality.yml` - Add tier-based linting/type checking
   - `.github/workflows/coverage.yml` - Add tier-based coverage requirements

2. **Medium Priority** (Advanced Testing):
   - `.github/workflows/mutation-testing.yml` - Only run on staging/main
   - `.github/workflows/comprehensive-test-battery.yml` - Only run on staging/main
   - `.github/workflows/e2e-staging-advanced.yml` - Only run on staging/main
   - `.github/workflows/simulation-testing.yml` - Only run on staging/main

3. **Low Priority** (Monitoring/Reporting):
   - `.github/workflows/component-status-report.yml` - Run on all branches
   - `.github/workflows/pr-automation.yml` - Add tier-aware messaging
   - `.github/workflows/component-promotion-validation.yml` - Adjust for tiers

---

### Next Steps

1. **Immediate** (This Week):
   - [ ] Review and approve this strategy
   - [ ] Update `TTA_DEV_EXTRACTION_ASSESSMENT_REVISED.md` to mark as verified
   - [ ] Create branch protection rules in GitHub

2. **Short-term** (Next Week):
   - [ ] Implement tier detection in workflows
   - [ ] Test with experimental branches
   - [ ] Update documentation

3. **Medium-term** (Next 2 Weeks):
   - [ ] Complete observability migration to TTA.dev
   - [ ] Roll out to staging/production branches
   - [ ] Monitor and optimize CI times

4. **Long-term** (Next Month):
   - [ ] Decide on test battery extraction strategy
   - [ ] Implement performance monitoring per tier
   - [ ] Create automated tier promotion workflows

---

## Questions for Discussion

1. **Test Battery Extraction**: Should we extract the comprehensive test battery to TTA.dev with language markers, or keep it in the main repo?

2. **Branch Naming**: Should we enforce branch prefixes (`experimental/*`, `feat/*`, `fix/*`) to trigger tier 1 checks automatically?

3. **Tier Overrides**: Should developers be able to manually trigger higher-tier checks on lower-tier branches (e.g., run full staging checks on a feature branch)?

4. **Component Promotion**: Should component promotion workflows (development → staging → production) bypass or include these tier checks?

5. **TTA.dev Sync**: How often should we sync changes between TTA main repo and TTA.dev packages?

---

## Appendix: Current Branch Status

Based on `git branch -a` output:

**Active Development Branches**:
- `development` - Main development branch (Tier 2)
- `staging` - Not visible in local branches (needs creation or is remote-only)
- `main` - Production branch (Tier 4)

**Feature Branches** (Tier 1 candidates):
- `feat/apm-opentelemetry-integration`
- `feat/dev-tools-openhands-workflow`
- `feat/enhance-monitoring-observability`
- `feat/generic-dev-tools-phase3.5`
- `feat/github-integration-tooling`
- `feat/integrate-tta-dev-primitives`
- `feat/migrate-to-tta-dev-primitives`
- `feat/repository-organization`
- `feat/workflow-primitives-infrastructure`

**Current Branch**: `fix/codecov-upload-on-failure` (would be Tier 1)

**Recommendation**: Create `staging` branch if it doesn't exist remotely, or document why it's not needed.

---

**Last Updated**: 2025-10-29
**Author**: Analysis based on repository audit
**Status**: Awaiting approval and implementation
