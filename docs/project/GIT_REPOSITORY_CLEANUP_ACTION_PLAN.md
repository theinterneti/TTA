# Git Repository Cleanup & Organization Action Plan

**Date:** 2025-10-08
**Repository:** `/home/thein/recovered-tta-storytelling`
**Remote:** https://github.com/theinterneti/TTA.git

## Executive Summary

### Current State Analysis

**Repository Statistics:**
- **Local main branch:** 7 commits ahead of origin/main
- **Modified tracked files:** 834 files
- **Untracked files:** 241 files
- **Files violating .gitignore:** 3 categories identified

**Issues Identified:**

1. **Remote Repository Violations:**
   - `.coverage` (Python coverage file) - should be ignored
   - `package.json` and `package-lock.json` (root level) - should be ignored
   - `tests/e2e/mocks/node_modules/` (entire directory) - should be ignored

2. **Local Untracked Changes:**
   - 241 new files across multiple components
   - Need categorization and structured commits

3. **Modified Files:**
   - 834 files with uncommitted changes
   - Mostly minor formatting/whitespace changes

---

## Phase 1: Repository State Backup ✅ COMPLETE

**Status:** Analysis complete. Current state documented.

**Findings:**
- Local commits not yet pushed: 7 commits
- No staged changes currently
- All changes are in working directory

---

## Phase 2: Remote Repository Cleanup

### Objective
Remove files from Git history that violate .gitignore rules without losing any work.

### Strategy
Since you have unpushed local commits, we can handle this cleanly by:
1. Removing files from Git tracking (but keeping local copies)
2. Committing the removal
3. Pushing changes

### Files to Remove from Tracking

**Category 1: Coverage Files**
```
.coverage
```

**Category 2: Root-level Node.js Files** (testing artifacts)
```
package.json
package-lock.json
```

**Category 3: Node Modules** (test mocks)
```
tests/e2e/mocks/node_modules/
```

**Note:** `src/player_experience/frontend/package.json` and `package-lock.json` should REMAIN tracked (legitimate frontend subproject).

### Execution Steps

**Step 2.1: Create Safety Backup**
```bash
# Create a backup branch
git branch backup-before-cleanup-$(date +%Y%m%d-%H%M%S)
```

**Step 2.2: Remove Files from Tracking**
```bash
# Remove .coverage from tracking but keep local file
git rm --cached .coverage

# Remove root-level Node.js files from tracking
git rm --cached package.json package-lock.json

# Remove node_modules from tracking
git rm -r --cached tests/e2e/mocks/node_modules/
```

**Step 2.3: Verify .gitignore**
```bash
# Ensure .gitignore has proper rules (already present)
grep -E "(\.coverage|node_modules|package\.json|package-lock\.json)" .gitignore
```

**Step 2.4: Commit Removal**
```bash
git commit -m "chore: remove files that violate .gitignore from tracking

- Remove .coverage (Python coverage artifact)
- Remove root-level package.json and package-lock.json (test artifacts)
- Remove tests/e2e/mocks/node_modules/ (should not be tracked)

These files are now properly ignored per .gitignore rules.
Files remain in local filesystem but are no longer tracked."
```

**Step 2.5: Verify Removal**
```bash
# Verify files are no longer tracked
git ls-files | grep -E "(\.coverage|^package\.json|^package-lock\.json|tests/e2e/mocks/node_modules)"

# Should return empty (except frontend package files which should remain)
```

---

## Phase 3: .gitignore Enhancement

### Current .gitignore Analysis
The existing .gitignore already covers these patterns. No updates needed.

**Verification:**
- ✅ Line 50: `.coverage` is ignored
- ✅ Line 257: `/node_modules/` is ignored
- ✅ Line 259: `/package-lock.json` is ignored
- ✅ Line 258: `/package.json` is ignored

### Recommendation
No changes needed to .gitignore. Current rules are comprehensive.

---

## Phase 4: Local Untracked Changes Organization

### Categorization by Component/Purpose

Based on analysis, untracked files fall into these categories:

**Category A: Infrastructure & Configuration (14 files)**
- `.devcontainer/` - Development container configuration
- `.dockerignore` - Docker ignore rules
- `.env.*.example` - Environment templates (4 files)
- `config/` staging configs (4 files)
- `nginx/` - Nginx configuration
- Dockerfiles (5 API-specific)

**Category B: GitHub Workflows & Templates (14 files)**
- `.github/workflows/` - New workflows (6 files)
- `.github/ISSUE_TEMPLATE/` - Issue templates (4 files)
- `.github/repository-config/` - Repository configuration (3 files)
- `.github/dependabot.yml` - Dependency management

**Category C: Documentation (45 files)**
- `docs/development/` - Component maturity workflow docs (13 files)
- `docs/deployment/` - Deployment guides
- `docs/testing/` - Testing documentation
- `docs/validation/` - Validation reports
- `docs/environments/`, `docs/roadmap/`, `docs/pr-consolidation/`, `docs/staging-homelab/`
- Root-level status/analysis docs (8 files)

**Category D: Testing Framework (45 files)**
- `testing/` - Comprehensive testing infrastructure
- `testing/simulation/` - Simulation framework
- `tests/e2e-staging/` - Staging E2E tests
- `tests/post_deployment/` - Post-deployment tests
- Test configuration files

**Category E: Scripts & Tooling (50 files)**
- `scripts/` - Development, deployment, and utility scripts
- Pre-commit hooks
- Component maturity analysis scripts
- Health check scripts

**Category F: Monitoring & Observability (14 files)**
- `monitoring/` - Prometheus, Grafana, Alertmanager configs
- Health check service
- Metrics configurations

**Category G: Source Code Components (16 files)**
- `src/components/*/MATURITY.md` - Component maturity tracking
- `src/components/carbon/` - New carbon component
- `src/components/neo4j/` - Neo4j component
- `src/agent_orchestration/` - New orchestration modules
- `src/common/` - Common utilities
- `src/player_experience/api/routers/health.py` - Health endpoint
- `src/player_experience/frontend/src/components/Auth/` - Auth components

**Category H: Web Interfaces (9 files)**
- `web-interfaces/admin-interface/` - Admin interface
- `web-interfaces/developer-interface/` - Developer interface
- Additional interface components

**Category I: Examples & Templates (3 files)**
- `examples/` - Demo and example code
- `templates/` - Project templates

**Category J: Artifacts & Reports (8 files)**
- `.secrets.baseline` - Secret scanning baseline
- `bandit-report.json` - Security scan report
- `component-maturity-analysis.json` - Component analysis
- `coverage.json` - Coverage report
- `debug-login.png` - Debug screenshot
- Test result files
- Playwright reports

### Commit Strategy

Following your multi-commit approach with conventional commit messages:

**Commit 1: Infrastructure & Configuration**
```bash
git add .devcontainer/ .dockerignore .env.*.example config/ nginx/ Dockerfile.*
git commit -m "feat(infrastructure): add development containers and environment configurations

- Add .devcontainer for VSCode development container support
- Add .dockerignore for optimized Docker builds
- Add environment template files (.env.*.example)
- Add staging-specific configurations (Neo4j, Redis, Postgres)
- Add Nginx configuration for reverse proxy
- Add API-specific Dockerfiles (admin, clinical, developer, patient, langgraph)

Supports: WSL2 development workflow, staging environment deployment"
```

**Commit 2: GitHub Workflows & Automation**
```bash
git add .github/
git commit -m "ci: add component maturity workflow automation and enhanced templates

- Add component-promotion-validation.yml workflow
- Add component-status-report.yml workflow
- Add frontend-deploy.yml workflow
- Add post-deployment-tests.yml workflow
- Add simulation-testing.yml workflow
- Add component promotion issue templates
- Add repository configuration files (branch protection, environments, secrets)
- Add dependabot.yml for automated dependency updates

Implements: Component maturity promotion workflow, automated quality gates"
```

**Commit 3: Documentation - Component Maturity Workflow**
```bash
git add docs/development/COMPONENT_*.md docs/development/PHASE*.md docs/development/GITHUB_PROJECT_SETUP.md
git commit -m "docs: add component maturity promotion workflow documentation

- Add comprehensive component maturity workflow guide
- Add component inventory and analysis documentation
- Add component promotion guide with criteria
- Add GitHub Projects setup guide
- Add phase-by-phase implementation guides (Phases 1-6)
- Add component labels guide

Supports: Solo developer workflow, component-based development lifecycle"
```

**Commit 4: Documentation - Deployment & Operations**
```bash
git add docs/deployment/ docs/environments/ docs/staging-homelab/ docs/validation/ docs/roadmap/
git commit -m "docs: add deployment guides and operational documentation

- Add staging deployment guide and hosting analysis
- Add environment-specific documentation
- Add staging homelab setup guides
- Add validation and testing documentation
- Add project roadmap documentation

Supports: Staging environment deployment, production readiness"
```

**Commit 5: Documentation - Development & Tooling**
```bash
git add docs/dev-workflow-quick-reference.md docs/tooling-*.md docs/pyright-*.md docs/PRE_COMMIT_HOOKS.md docs/AI_AGENT_ORCHESTRATION.md docs/pr-consolidation/
git commit -m "docs: add development workflow and tooling documentation

- Add dev workflow quick reference guide
- Add tooling optimization and cleanup documentation
- Add Pyright vs Pylance analysis
- Add pre-commit hooks documentation
- Add AI agent orchestration documentation
- Add PR consolidation guides

Supports: Solo developer efficiency, tool selection decisions"
```

**Commit 6: Documentation - Architecture & Design**
```bash
git add docs/master-glossary.md docs/technical-specifications.md docs/entertainment-first-design.md docs/simulation-framework-overview.md docs/testing-framework.md docs/*-matrix.md docs/gap-analysis.md docs/implementation-roadmap.md docs/conflict-resolution-report.md docs/documentation-audit-summary.md docs/solo-development-adjustment.md
git commit -m "docs: add architecture, design, and planning documentation

- Add master glossary for consistent terminology
- Add technical specifications
- Add entertainment-first design philosophy
- Add simulation framework overview
- Add testing framework documentation
- Add traceability, test execution, and user journey matrices
- Add gap analysis and implementation roadmap
- Add conflict resolution and documentation audit reports
- Add solo development workflow adjustments

Supports: System architecture understanding, development planning"
```

**Commit 7: Testing Framework & Infrastructure**
```bash
git add testing/ tests/e2e-staging/ tests/post_deployment/ test-results-staging/ playwright*.config.ts
git commit -m "test: add comprehensive testing framework and simulation infrastructure

- Add testing/ directory with comprehensive test battery
- Add simulation framework for multi-user testing
- Add staging-specific E2E tests
- Add post-deployment test suite
- Add load testing infrastructure
- Add Playwright configurations for staging and coverage
- Add test result directories

Supports: QA validation, production readiness assessment, multi-user simulation"
```

**Commit 8: Scripts & Development Tools**
```bash
git add scripts/ .augment/rules/prefer-uvx-for-tools.md
git commit -m "feat(tooling): add development, deployment, and maintenance scripts

- Add component maturity analysis scripts
- Add deployment scripts (staging, homelab)
- Add health check and validation scripts
- Add pre-commit hook setup
- Add E2E test runners
- Add performance testing scripts
- Add environment management scripts
- Add Augment AI rule for uvx tool preference

Supports: Development workflow automation, deployment automation, quality assurance"
```

**Commit 9: Monitoring & Observability**
```bash
git add monitoring/
git commit -m "feat(monitoring): add comprehensive monitoring and observability stack

- Add Prometheus configuration (staging, homelab, production)
- Add Grafana dashboards and configuration
- Add Alertmanager configuration
- Add health check service
- Add monitoring documentation

Supports: System observability, performance tracking, alerting"
```

**Commit 10: Source Code - Component Maturity Tracking**
```bash
git add src/components/*/MATURITY.md src/components/MATURITY.md.template
git commit -m "feat(components): add component maturity tracking system

- Add MATURITY.md files for all components
- Add MATURITY.md template for new components
- Track development/staging/production readiness per component

Implements: Component maturity promotion workflow"
```

**Commit 11: Source Code - New Components & Features**
```bash
git add src/components/carbon/ src/components/neo4j/ src/agent_orchestration/langgraph_orchestrator.py src/agent_orchestration/unified_orchestrator.py src/common/ src/player_experience/api/routers/health.py src/player_experience/api/session_manager.py src/player_experience/frontend/src/components/Auth/ src/player_experience/frontend/craco.config.js
git commit -m "feat: add new components and orchestration modules

- Add carbon component for emissions tracking
- Add Neo4j component for graph database integration
- Add LangGraph and unified orchestrators
- Add common utilities (health checks, process utils, time utils)
- Add health endpoint for player experience API
- Add session manager for player experience
- Add Auth components for frontend
- Add Craco configuration for frontend build customization

Supports: System functionality expansion, better orchestration"
```

**Commit 12: Web Interfaces**
```bash
git add web-interfaces/
git commit -m "feat(interfaces): add admin and developer web interfaces

- Add admin interface for system administration
- Add developer interface for development tools
- Add shared interface components

Supports: Multi-role system access, administrative capabilities"
```

**Commit 13: Examples & Templates**
```bash
git add examples/ templates/
git commit -m "docs: add examples and project templates

- Add free models filter demo
- Add frontend integration example
- Add model management demo
- Add project templates for consistency

Supports: Developer onboarding, consistent project structure"
```

**Commit 14: Artifacts & Reports**
```bash
git add .secrets.baseline bandit-report.json component-maturity-analysis.json coverage.json *.png playwright-staging-report/ preference_integration_demo_results.json player_preference_ai_pipeline_validation.json
git commit -m "chore: add security baselines and analysis reports

- Add secrets detection baseline (.secrets.baseline)
- Add Bandit security scan report
- Add component maturity analysis results
- Add coverage reports
- Add test result artifacts
- Add debug screenshots

Note: These are baseline/reference files for tracking security and quality metrics"
```

**Commit 15: Root-level Status Documents**
```bash
git add ACCURATE_P0_COMPONENT_STATUS.md CARBON_STAGING_PROMOTION.md CHARACTER_CREATION_FORM_RESTORATION.md COMPONENT_MATURITY_*.md DEPLOYMENT_STATUS*.md NARRATIVE_COHERENCE_VALIDATION_STAGING_PROMOTION.md
git commit -m "docs: add component status and deployment tracking documents

- Add P0 component status tracking
- Add component promotion status documents
- Add deployment status tracking
- Add component maturity analysis summaries

Supports: Project status visibility, promotion tracking"
```

---

## Phase 5: Modified Files Review & Commit

### Analysis of Modified Files

The 834 modified files show mostly minor changes:
- Trailing newline removals
- Whitespace cleanup
- Minor formatting adjustments
- .coverage binary file update

### Recommended Approach

**Option A: Commit All Modified Files Together** (Recommended)
```bash
git add -u
git commit -m "chore: apply formatting and whitespace cleanup across codebase

- Remove trailing newlines for consistency
- Apply whitespace cleanup
- Update .coverage from recent test runs

Automated cleanup for code consistency"
```

**Option B: Review and Commit Selectively**
If you want to review changes first:
```bash
# Review changes in batches
git diff --stat | less

# Add specific directories
git add .github/
git commit -m "chore: update GitHub workflows and templates formatting"

# Continue for other directories...
```

---

## Phase 6: Push Strategy

### Pre-Push Checklist

Before pushing, ensure:
- [ ] Pre-commit hooks are installed and passing
- [ ] All commits follow conventional commit format
- [ ] No sensitive data in commits
- [ ] .gitignore violations are removed

### Push Commands

**Step 6.1: Verify Pre-commit Hooks**
```bash
# Install pre-commit hooks if not already installed
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

**Step 6.2: Final Review**
```bash
# Review all commits to be pushed
git log origin/main..HEAD --oneline

# Review total changes
git diff origin/main..HEAD --stat
```

**Step 6.3: Push to Remote**
```bash
# Push to main branch
git push origin main

# If force push is needed (only if remote history needs rewriting)
# git push origin main --force-with-lease
```

**Step 6.4: Verify Remote State**
```bash
# Verify push succeeded
git log origin/main --oneline -10

# Verify removed files are gone from remote
git ls-remote origin | grep -E "(coverage|package\.json|node_modules)"
```

---

## Safety & Rollback Procedures

### If Something Goes Wrong

**Rollback to Backup Branch:**
```bash
# List backup branches
git branch | grep backup-before-cleanup

# Reset to backup
git reset --hard backup-before-cleanup-YYYYMMDD-HHMMSS
```

**Undo Last Commit (if not pushed):**
```bash
git reset --soft HEAD~1
```

**Undo Push (if already pushed):**
```bash
# Only if absolutely necessary and you're the only developer
git push origin main --force-with-lease
```

---

## Execution Timeline

**Estimated Time:** 2-3 hours

1. **Phase 2 (Remote Cleanup):** 15 minutes
2. **Phase 4 (Local Changes - 15 commits):** 90-120 minutes
3. **Phase 5 (Modified Files):** 15 minutes
4. **Phase 6 (Push & Verify):** 15 minutes

---

## Next Steps

1. **Review this plan** and confirm approach
2. **Execute Phase 2** (Remote cleanup) first
3. **Execute Phase 4** (Local changes) in batches
4. **Execute Phase 5** (Modified files)
5. **Execute Phase 6** (Push to remote)

**Ready to proceed?** Let me know which phase you'd like to start with, and I'll guide you through each step with confirmation before executing any commands.
