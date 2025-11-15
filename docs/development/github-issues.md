# GitHub Issues to Create for Repository Reorganization

**Date**: October 29, 2025
**Epic**: Repository Reorganization and Workflow Escalation
**Timeline**: 3 weeks (Nov 4 - Nov 22, 2025)

---

## Epic Issue

### Issue #1: Repository Reorganization - Workflow Escalation and Component Organization

**Labels**: `epic`, `infrastructure`, `workflows`, `priority:high`

**Description**:
Comprehensive repository reorganization following TTA.dev migrations. Implement tier-based workflow escalation, formalize component inventory, and establish dependency management.

**Objectives**:
- ✅ Audit TTA.dev migrations and document current state
- ✅ Design 4-tier workflow escalation strategy
- ✅ Create comprehensive component inventory
- ⏳ Implement tier-aware GitHub Actions workflows
- ⏳ Formalize TTA.dev dependency management
- ⏳ Update all documentation

**Timeline**: 3 weeks (Nov 4-22)

**Related Documents**:
- `REPOSITORY_STATUS_AND_WORKFLOW_STRATEGY.md`
- `WORKFLOW_ESCALATION_IMPLEMENTATION.md`
- `COMPONENT_INVENTORY.md`
- `WORKFLOW_ESCALATION_CHECKLIST.md`

**Child Issues**: #2-#15

---

## Week 1: Workflow Foundation (Nov 4-8)

### Issue #2: Implement Tier Detection Workflow Template

**Labels**: `infrastructure`, `workflows`, `week-1`, `priority:critical`
**Milestone**: Week 1 - Workflow Foundation
**Assignee**: DevOps/Backend team

**Description**:
✅ **COMPLETED** - Create reusable workflow template for detecting branch tier (1-4).

**Status**: Created at `.github/workflows/templates/determine-tier.yml`

**Next Steps**:
- Integrate into existing workflows
- Test on all branch types
- Document usage

**Files**:
- ✅ `.github/workflows/templates/determine-tier.yml`

---

### Issue #3: Modify tests.yml for Tier-Aware Testing

**Labels**: `infrastructure`, `workflows`, `testing`, `week-1`, `priority:critical`
**Milestone**: Week 1 - Workflow Foundation
**Assignee**: QA/Backend team
**Dependencies**: #2

**Description**:
Update `tests.yml` to implement tier-based testing strategy:
- Tier 1 (Experimental): Unit tests only (allow failures)
- Tier 2 (Development): Unit + Integration tests
- Tier 3 (Staging): Unit + Integration + E2E tests
- Tier 4 (Production): Full test suite with strict enforcement

**Implementation Steps**:
1. Add tier detection job using `determine-tier.yml` template
2. Modify unit test job with tier-based conditionals
3. Modify integration test job (tier 2+)
4. Modify E2E test job (tier 3+)
5. Add continue-on-error for tier 1

**Files to Modify**:
- `.github/workflows/tests.yml`

**Reference**: `WORKFLOW_ESCALATION_IMPLEMENTATION.md` Section 4.1

**Acceptance Criteria**:
- [ ] Tier detection job added
- [ ] Unit tests run on all tiers
- [ ] Integration tests conditional (tier 2+)
- [ ] E2E tests conditional (tier 3+)
- [ ] Tier 1 allows test failures
- [ ] Workflow tested on all branch types

---

### Issue #4: Modify code-quality.yml for Tier-Aware Quality Checks

**Labels**: `infrastructure`, `workflows`, `code-quality`, `week-1`, `priority:high`
**Milestone**: Week 1 - Workflow Foundation
**Assignee**: Backend team
**Dependencies**: #2

**Description**:
Update `code-quality.yml` to implement tier-based quality gates:
- Tier 1 (Experimental): Format check only
- Tier 2 (Development): Format + Lint
- Tier 3 (Staging): Format + Lint + Type check
- Tier 4 (Production): All checks with strict enforcement

**Implementation Steps**:
1. Add tier detection job
2. Make format-check run on all tiers
3. Add lint conditional (tier 2+)
4. Add type-check conditional (tier 3+)
5. Add security scan conditional (tier 3+)

**Files to Modify**:
- `.github/workflows/code-quality.yml`

**Reference**: `WORKFLOW_ESCALATION_IMPLEMENTATION.md` Section 4.2

**Acceptance Criteria**:
- [ ] Tier detection job added
- [ ] Format check runs on all tiers
- [ ] Lint conditional on tier 2+
- [ ] Type check conditional on tier 3+
- [ ] Security scan conditional on tier 3+
- [ ] Tested on all branch types

---

### Issue #5: Modify coverage.yml for Tier-Aware Coverage Requirements

**Labels**: `infrastructure`, `workflows`, `testing`, `coverage`, `week-1`, `priority:high`
**Milestone**: Week 1 - Workflow Foundation
**Assignee**: QA team
**Dependencies**: #2

**Description**:
Update `coverage.yml` to implement tier-based coverage thresholds:
- Tier 1 (Experimental): Coverage reporting only, no enforcement
- Tier 2 (Development): ≥60% coverage required
- Tier 3 (Staging): ≥70% coverage required
- Tier 4 (Production): ≥85% coverage required

**Implementation Steps**:
1. Add tier detection job
2. Generate coverage report (all tiers)
3. Add tier-based threshold enforcement
4. Upload coverage to Codecov with tier tag
5. Generate GitHub summary with tier-specific messages

**Files to Modify**:
- `.github/workflows/coverage.yml`

**Reference**: `WORKFLOW_ESCALATION_IMPLEMENTATION.md` Section 4.3

**Acceptance Criteria**:
- [ ] Tier detection job added
- [ ] Coverage report generated on all tiers
- [ ] Threshold enforcement varies by tier
- [ ] Codecov upload includes tier tag
- [ ] GitHub summary shows tier-specific guidance
- [ ] Tested on all branch types

---

### Issue #6: Modify mutation-testing.yml for Tier-Aware Mutation Testing

**Labels**: `infrastructure`, `workflows`, `testing`, `mutation`, `week-1`, `priority:medium`
**Milestone**: Week 1 - Workflow Foundation
**Assignee**: QA team
**Dependencies**: #2

**Description**:
Update `mutation-testing.yml` to implement tier-based mutation testing:
- Tier 1-2: Skip mutation testing
- Tier 3 (Staging): Mutation testing required, ≥75% score
- Tier 4 (Production): Mutation testing required, ≥85% score

**Implementation Steps**:
1. Add tier detection job
2. Add tier conditional (run on tier 3+)
3. Add tier-based score thresholds
4. Generate GitHub summary with results

**Files to Modify**:
- `.github/workflows/mutation-testing.yml`

**Reference**: `WORKFLOW_ESCALATION_IMPLEMENTATION.md` Section 4.4

**Acceptance Criteria**:
- [ ] Tier detection job added
- [ ] Mutation testing skipped on tier 1-2
- [ ] Mutation testing runs on tier 3-4
- [ ] Score threshold varies by tier (75%/85%)
- [ ] GitHub summary shows results
- [ ] Tested on staging/main branches

---

## Week 2: Component Organization (Nov 11-15)

### Issue #7: Promote Narrative Coherence Component to Staging

**Labels**: `component`, `promotion`, `staging`, `week-2`, `priority:high`
**Milestone**: Week 2 - Component Organization
**Assignee**: Backend team
**Effort Estimate**: 2 hours

**Description**:
Promote `narrative_coherence` component from Development to Staging stage.

**Current Status**:
- Test coverage: 72% ✅ (≥70% required)
- Linting errors: 40 ❌
- Type errors: 20 ❌
- README: Missing ❌
- Security: Clean ✅

**Work Required**:
1. Fix 40 linting errors
2. Resolve 20 type errors
3. Create README.md
4. Update MATURITY.md to Staging
5. Create promotion PR

**Files**:
- `src/components/narrative_coherence/`
- `src/components/narrative_coherence/MATURITY.md`

**Reference**: `COMPONENT_INVENTORY.md` Section for Narrative Coherence

**Acceptance Criteria**:
- [ ] All linting errors resolved
- [ ] All type errors resolved
- [ ] README.md created with API documentation
- [ ] MATURITY.md updated to Staging
- [ ] PR created and merged
- [ ] 7-day staging observation begins

---

### Issue #8: Fix Gameplay Loop Quality Issues for Staging Promotion

**Labels**: `component`, `quality`, `week-2`, `priority:high`
**Milestone**: Week 2 - Component Organization
**Assignee**: Backend team
**Effort Estimate**: 6-7 hours

**Description**:
Resolve quality issues in `gameplay_loop` component to enable staging promotion.

**Current Status**:
- Test coverage: 100% ✅
- Linting errors: 108 ❌
- Type errors: 356 ❌
- README: Missing ❌

**Work Required**:
1. Fix 108 linting errors
2. Resolve 356 type errors (significant refactoring may be needed)
3. Create README.md
4. Validate test coverage remains ≥70%
5. Update MATURITY.md

**Files**:
- `src/components/gameplay_loop/`
- `src/components/gameplay_loop/MATURITY.md`

**Reference**: `COMPONENT_INVENTORY.md` Section for Gameplay Loop

**Acceptance Criteria**:
- [ ] All linting errors resolved
- [ ] All type errors resolved
- [ ] README.md created
- [ ] Test coverage ≥70%
- [ ] MATURITY.md updated
- [ ] Component ready for staging promotion PR

**Note**: This is significant work. Consider breaking into subtasks.

---

### Issue #9: Fix Model Management Quality Issues for Staging Promotion

**Labels**: `component`, `quality`, `week-2`, `priority:high`
**Milestone**: Week 2 - Component Organization
**Assignee**: Backend team
**Effort Estimate**: 2.75 hours

**Description**:
Resolve quality issues in `model_management` component to enable staging promotion.

**Current Status**:
- Test coverage: 100% ✅
- Linting errors: 59 ❌
- Type errors: 74 ❌
- README: Exists ✅

**Work Required**:
1. Fix 59 linting errors
2. Resolve 74 type errors
3. Update README if needed
4. Validate test coverage remains ≥70%
5. Update MATURITY.md

**Files**:
- `src/components/model_management/`
- `src/components/model_management/MATURITY.md`

**Reference**: `COMPONENT_INVENTORY.md` Section for Model Management

**Acceptance Criteria**:
- [ ] All linting errors resolved
- [ ] All type errors resolved
- [ ] README reviewed and updated
- [ ] Test coverage ≥70%
- [ ] MATURITY.md updated
- [ ] Component ready for staging promotion PR

---

### Issue #10: Refactor Neo4j Component Tests

**Labels**: `component`, `testing`, `week-2`, `priority:medium`
**Milestone**: Week 2 - Component Organization
**Assignee**: QA/Backend team

**Description**:
Refactor `neo4j` component tests to reduce mocking and achieve real coverage.

**Current Status**:
- Test coverage: 0% (tests use heavy mocking)
- Tests exist but don't execute real code paths

**Work Required**:
1. Analyze current test mocking patterns
2. Refactor tests to test actual code paths
3. Add integration tests with real Neo4j (Docker)
4. Achieve ≥70% coverage
5. Update MATURITY.md

**Files**:
- `src/components/neo4j/`
- `tests/unit/components/neo4j/`
- `tests/integration/components/neo4j/`
- `src/components/neo4j/MATURITY.md`

**Reference**: `COMPONENT_INVENTORY.md` Section for Neo4j Component

**Acceptance Criteria**:
- [ ] Test mocking reduced
- [ ] Integration tests added
- [ ] Test coverage ≥70%
- [ ] Tests pass with real Neo4j
- [ ] MATURITY.md updated

---

## Week 2-3: TTA.dev Integration (Nov 11-22)

### Issue #11: Merge Observability Integration to TTA.dev

**Labels**: `tta.dev`, `migration`, `observability`, `week-2`, `priority:critical`
**Milestone**: Week 2 - Component Organization
**Assignee**: DevOps/Backend team

**Description**:
Merge exported `tta-observability-integration` package into TTA.dev repository and publish.

**Current Status**:
- ✅ Exported to `export/tta-observability-integration/`
- ✅ 6 Grafana dashboards included
- ✅ OpenTelemetry integration complete
- ⏳ Needs merge to TTA.dev
- ⏳ Needs PyPI publication

**Work Required**:
1. Create PR in TTA.dev repository
2. Merge to `TTA.dev/packages/tta-observability-integration/`
3. Publish to PyPI as `tta-observability-integration`
4. Update TTA main repo to use published package
5. Remove local copy after migration

**Files**:
- Source: `export/tta-observability-integration/`
- Target: `TTA.dev/packages/tta-observability-integration/`
- Update: `pyproject.toml`

**Reference**: `COMPONENT_INVENTORY.md` Observability Integration section

**Acceptance Criteria**:
- [ ] PR created in TTA.dev
- [ ] PR merged
- [ ] Package published to PyPI
- [ ] TTA repo updated to use published package
- [ ] Local copy removed
- [ ] Documentation updated

---

### Issue #12: Formalize tta-dev-primitives Dependency

**Labels**: `tta.dev`, `dependencies`, `week-2`, `priority:high`
**Milestone**: Week 2-3 - TTA.dev Integration
**Assignee**: Backend team

**Description**:
Formalize dependency on `tta-dev-primitives` with semantic versioning.

**Current Status**:
- Currently using git reference to TTA.dev repository
- No version pinning or constraints
- Update process not documented

**Work Required**:
1. Determine appropriate version constraint (e.g., `^0.1.0`)
2. Update `pyproject.toml` with semantic version
3. Document update process
4. Test with pinned version
5. Update AGENTS.md with dependency info

**Files to Modify**:
- `pyproject.toml`
- `AGENTS.md`
- Create: `docs/development/tta-dev-dependencies.md`

**Reference**: `COMPONENT_INVENTORY.md` External Dependencies section

**Acceptance Criteria**:
- [ ] pyproject.toml uses semantic version
- [ ] Version constraint appropriate (^0.1.0 or similar)
- [ ] Update process documented
- [ ] Tests pass with pinned version
- [ ] AGENTS.md updated
- [ ] Dependency documentation created

---

### Issue #13: Publish tta-workflow-primitives Package

**Labels**: `tta.dev`, `primitives`, `week-2`, `priority:medium`
**Milestone**: Week 2-3 - TTA.dev Integration
**Assignee**: Backend/DevOps team

**Description**:
Complete and publish `tta-workflow-primitives` package for workflow composition.

**Current Status**:
- Referenced in documentation
- Not yet published or packaged

**Work Required**:
1. Complete `tta-workflow-primitives` implementation in TTA.dev
2. Add quality gate automation utilities
3. Add stage handler utilities
4. Publish to PyPI or as git package
5. Integrate into TTA workflows

**Files**:
- TTA.dev: `packages/tta-workflow-primitives/`
- TTA: Update `pyproject.toml`

**Reference**: `COMPONENT_INVENTORY.md` External Dependencies section

**Acceptance Criteria**:
- [ ] Package implementation complete
- [ ] Published to PyPI or git
- [ ] TTA repo updated to use package
- [ ] Workflows use primitives
- [ ] Documentation updated

---

## Week 3: Documentation and Rollout (Nov 18-22)

### Issue #14: Update Repository Documentation

**Labels**: `documentation`, `week-3`, `priority:high`
**Milestone**: Week 3 - Documentation and Rollout
**Assignee**: Technical writer/Lead dev

**Description**:
Update all repository documentation to reflect new workflow strategy and component inventory.

**Files to Update**:
1. `AGENTS.md` - Add workflow escalation, component inventory
2. `README.md` - Update workflow badges, add tier info
3. `CONTRIBUTING.md` - Add tier-based contribution guidelines
4. `docs/development/workflow-guide.md` - Create new guide

**Work Required**:
1. Update AGENTS.md with workflow escalation section
2. Update README.md with tier badges and workflow info
3. Update CONTRIBUTING.md with tier-specific guidelines
4. Create comprehensive workflow guide
5. Update component documentation references

**Reference**:
- `WORKFLOW_ESCALATION_IMPLEMENTATION.md`
- `COMPONENT_INVENTORY.md`

**Acceptance Criteria**:
- [ ] AGENTS.md updated with workflow info
- [ ] README.md updated with tier badges
- [ ] CONTRIBUTING.md updated with guidelines
- [ ] Workflow guide created
- [ ] All links working
- [ ] Documentation reviewed

---

### Issue #15: Configure Branch Protection Rules

**Labels**: `infrastructure`, `github`, `week-3`, `priority:critical`
**Milestone**: Week 3 - Documentation and Rollout
**Assignee**: DevOps/Admin

**Description**:
Configure GitHub branch protection rules for main, staging, and development branches.

**Branch Protection Configuration**:

**main (Tier 4 - Production)**:
- [x] Require pull request reviews (2 approvals)
- [x] Require status checks to pass
  - tests (all tests must pass)
  - code-quality (all checks must pass)
  - coverage (≥85%)
  - mutation-testing (≥85%)
- [x] Require conversation resolution
- [x] Restrict force push
- [x] Restrict deletions

**staging (Tier 3)**:
- [x] Require pull request reviews (1 approval)
- [x] Require status checks to pass
  - tests (all tests must pass)
  - code-quality (lint + type check must pass)
  - coverage (≥70%)
  - mutation-testing (≥75%)
- [x] Require conversation resolution
- [x] Restrict force push

**development (Tier 2)**:
- [x] Require pull request reviews (1 approval, can be stale)
- [x] Require status checks to pass
  - tests (unit + integration must pass)
  - code-quality (lint must pass)
  - coverage (≥60%)
- [x] Allow force push (for rebasing)

**Work Required**:
1. Configure main branch protection
2. Configure staging branch protection
3. Configure development branch protection
4. Document protection rules
5. Test with sample PRs
6. Train team on new rules

**Reference**: `WORKFLOW_ESCALATION_IMPLEMENTATION.md` Section 7

**Acceptance Criteria**:
- [ ] main branch protection configured
- [ ] staging branch protection configured
- [ ] development branch protection configured
- [ ] Rules documented
- [ ] Tested with sample PRs
- [ ] Team trained

---

## Additional Component Issues (As Needed)

### Issue Template: Component Promotion

**Title**: Promote [Component Name] to [Target Stage]

**Labels**: `component`, `promotion`, `[target-stage]`
**Milestone**: [Week/Sprint]
**Assignee**: [Team member]

**Description**:
Promote `[component-name]` component from [Current Stage] to [Target Stage].

**Current Status**:
- Test coverage: [X]%
- Linting: [status]
- Type checking: [status]
- Documentation: [status]
- Security: [status]

**Work Required**:
1. [List specific tasks]
2. Update MATURITY.md
3. Create promotion PR
4. Begin observation period (if staging)

**Files**:
- `src/components/[component-name]/`
- `src/components/[component-name]/MATURITY.md`

**Acceptance Criteria**:
- [ ] Quality gates met
- [ ] MATURITY.md updated
- [ ] PR created and merged
- [ ] Observation period (if applicable)

---

## Issue Creation Instructions

### Using GitHub Web Interface

1. Go to repository Issues tab
2. Click "New Issue"
3. Copy issue content from this document
4. Set appropriate labels, milestone, assignee
5. Submit issue

### Using GitHub CLI

```bash
# Install gh CLI if needed
# https://cli.github.com/

# Epic issue
gh issue create --title "Repository Reorganization - Workflow Escalation and Component Organization" \
  --label "epic,infrastructure,workflows,priority:high" \
  --body-file issue-1-epic.md

# Workflow issues
gh issue create --title "Implement Tier Detection Workflow Template" \
  --label "infrastructure,workflows,week-1,priority:critical" \
  --milestone "Week 1 - Workflow Foundation" \
  --body-file issue-2-tier-detection.md

gh issue create --title "Modify tests.yml for Tier-Aware Testing" \
  --label "infrastructure,workflows,testing,week-1,priority:critical" \
  --milestone "Week 1 - Workflow Foundation" \
  --body-file issue-3-tests-yml.md

# ... repeat for all issues
```

### Using GitHub API

```bash
# Set repository variables
REPO_OWNER="theinterneti"
REPO_NAME="recovered-tta-storytelling"
GITHUB_TOKEN="your-token"

# Create issue
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/issues \
  -d '{
    "title": "Issue Title",
    "body": "Issue body content",
    "labels": ["label1", "label2"]
  }'
```

---

## Issue Tracking

### Progress Dashboard

Track issue completion:

```
Epic: Repository Reorganization [#1]
├─ Week 1: Workflow Foundation
│  ├─ ✅ #2: Tier Detection Template (DONE)
│  ├─ ⏳ #3: tests.yml Modification (IN PROGRESS)
│  ├─ ⏳ #4: code-quality.yml Modification (IN PROGRESS)
│  ├─ ⏳ #5: coverage.yml Modification (TODO)
│  └─ ⏳ #6: mutation-testing.yml Modification (TODO)
├─ Week 2: Component Organization
│  ├─ ⏳ #7: Promote Narrative Coherence (TODO)
│  ├─ ⏳ #8: Fix Gameplay Loop (TODO)
│  ├─ ⏳ #9: Fix Model Management (TODO)
│  └─ ⏳ #10: Refactor Neo4j Tests (TODO)
├─ Week 2-3: TTA.dev Integration
│  ├─ ⏳ #11: Merge Observability Integration (TODO)
│  ├─ ⏳ #12: Formalize tta-dev-primitives (TODO)
│  └─ ⏳ #13: Publish workflow-primitives (TODO)
└─ Week 3: Documentation and Rollout
   ├─ ⏳ #14: Update Documentation (TODO)
   └─ ⏳ #15: Configure Branch Protection (TODO)
```

### Labels Used

- `epic` - Epic/meta issue
- `infrastructure` - Infrastructure changes
- `workflows` - GitHub Actions workflows
- `testing` - Testing-related
- `code-quality` - Code quality tools
- `coverage` - Code coverage
- `mutation` - Mutation testing
- `component` - Component work
- `promotion` - Component promotion
- `staging` - Staging stage
- `quality` - Quality improvements
- `tta.dev` - TTA.dev integration
- `dependencies` - Dependency management
- `migration` - Migration work
- `observability` - Observability features
- `primitives` - Primitive packages
- `documentation` - Documentation updates
- `github` - GitHub configuration
- `week-1`, `week-2`, `week-3` - Timeline markers
- `priority:critical`, `priority:high`, `priority:medium` - Priority levels

---

**Last Updated**: 2025-10-29
**Total Issues**: 15 (1 epic + 14 implementation)
**Estimated Total Effort**: 3 weeks
