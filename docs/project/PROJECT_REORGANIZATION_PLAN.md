# TTA Project Reorganization Plan

**Date:** 2025-10-04
**Purpose:** Comprehensive directory reorganization to align with dev/staging environment separation
**Status:** Phase 1 - Analysis and Categorization

---

## Executive Summary

This document provides a detailed categorization and reorganization plan for 100+ markdown files, test files, screenshots, and docker-compose configurations currently scattered in the root directory.

**Key Findings:**
- **106 markdown files** in root directory (all AI-generated)
- **20+ test files** scattered in root
- **60 PNG screenshots** in root
- **9 docker-compose files** (some obsolete)
- **3 tta.* subdirectories** (minimal/empty content)

**Timeline Analysis:**
- Sept 14-15: Early integration work
- Sept 16-18: Deployment and testing setup
- Sept 26-30: Major validation, fixes, and security work
- Oct 1-3: Recent type checking, pytest fixes, testing analysis

---

## File Categorization

### Category 1: ARCHIVE - Phase Completion Reports (Historical)

**Purpose:** Historical records of completed development phases
**Destination:** `archive/phases/`
**Action:** ARCHIVE (keep for historical reference)

**Phase 1 Reports (Oct 1-2, 2025):**
- PHASE1A_COMPLETE.md
- PHASE1A_FORMAT_CHECK_FIX_SUMMARY.md
- PHASE1A_FORMAT_CHECK_RESOLUTION_SUMMARY.md
- PHASE1B1_COMPLETION_SUMMARY.md
- PHASE1B2_BATCH1_SUMMARY.md
- PHASE1B2_BATCH_STRATEGY.md
- PHASE1B2_COMPLETION_SUMMARY.md
- PHASE1B3_ERROR_ANALYSIS.md
- PHASE1B3_PARTIAL_SUMMARY.md
- PHASE1B_COMPLETION_SUMMARY.md
- PHASE1B_ERROR_ANALYSIS.md
- PHASE1B_PROGRESS_TRACKER.md
- PHASE1C_AUTOMATION_RESEARCH.md
- PHASE1C_PROGRESS_TRACKER.md
- PHASE1_ACTION_PLAN.md
- PHASE1_WORKFLOW_RESULTS_ANALYSIS.md
- PHASE_1A_INTEGRATION_COMPLETE.md (Sept 14)
- PHASE_2A_INTEGRATION_COMPLETE.md (Sept 14)

**Phase 2-3 Reports (Sept 27-29):**
- phase1_completion_summary.md
- phase1_infrastructure_restoration_report.md
- phase2_completion_report.md
- phase3_advanced_analytics_plan.md
- phase3_browser_validation_report.md
- phase3_comprehensive_report.md
- phase3_final_validation_report.md
- phase3_implementation_summary.md

**Stage Reports:**
- STAGE1_COMPLETION_REPORT.md (Oct 2)

**Total:** 27 files → `archive/phases/phase1/`, `archive/phases/phase2/`, `archive/phases/phase3/`

---

### Category 2: ARCHIVE - Task Completion Reports (Historical)

**Purpose:** Historical records of specific task completions
**Destination:** `archive/tasks/`
**Action:** ARCHIVE (keep for historical reference)

**Files (Sept 14, 2025):**
- TASKS_9_10_COMPLETION_SUMMARY.md
- TASK_13_1_DEPENDENCY_RESOLUTION_SUMMARY.md
- TASK_13_2_DATABASE_INTEGRATION_SUMMARY.md
- TASK_14_2_DATA_PRIVACY_PROTECTION_SUMMARY.md
- TASK_19_COMPLETION_SUMMARY.md
- TASK_2_SECURITY_SCAN_STATUS_REPORT.md (Sept 29)
- TASK_4_WORLD_MANAGEMENT_SUMMARY.md
- TASK_9_2_PROGRESS_TRACKING_SERVICE_SUMMARY.md
- TASK_COMPLETION_SUMMARY.md (Sept 29)

**Total:** 9 files → `archive/tasks/`

---

### Category 3: ARCHIVE - Fix and Resolution Reports (Historical)

**Purpose:** Historical records of bugs fixed and issues resolved
**Destination:** `archive/fixes/`
**Action:** ARCHIVE (keep for historical reference)

**Files:**
- API_VALIDATION_IMPROVEMENTS.md (Sept 29)
- BACKEND_STARTUP_FIX.md (Sept 29)
- COMPREHENSIVE_FIX_SUMMARY.md (Sept 29)
- DOCKER_BUILD_FAILURE_ANALYSIS.md (Sept 26)
- E2E_WORKFLOW_OPTIMIZATION_SUMMARY.md (Sept 16)
- FIX_LIST_DIRECTORY_RECREATION.md (Oct 3)
- NEO4J_BROWSER_RESOLUTION_SUMMARY.md (Sept 16)
- PYTEST_VSCODE_FIX_SUMMARY.md (Oct 3)
- ROOT_CAUSE_ANALYSIS_LIST_DIRECTORY.md (Oct 3)
- TEST_FAILURE_ANALYSIS_REPORT.md (Sept 29)
- TEST_FIXES_PROGRESS.md (Sept 30)
- TEST_FIXES_SUMMARY.md (Sept 30)
- VSCODE_PYTEST_CACHE_FIX_COMPLETE.md (Oct 3)
- VSCODE_PYTEST_INTEGRATION_FIX.md (Oct 3)

**Total:** 14 files → `archive/fixes/`

---

### Category 4: ARCHIVE - Validation and Test Reports (Historical)

**Purpose:** Historical validation and test execution reports
**Destination:** `archive/validation/`
**Action:** ARCHIVE (keep for historical reference)

**Files:**
- COMPREHENSIVE_VALIDATION_SUMMARY.md (Sept 29)
- FINAL_VALIDATION_REPORT.md (Sept 29)
- OPENROUTER_AUTHENTICATION_TEST_REPORT.md (Sept 16)
- TEST_RESULTS_BASELINE.md (Sept 30)
- TESTING_SUMMARY.md (Sept 16)
- VALIDATION_RESULTS.md (Sept 29)
- VALIDATION_TEST_RESULTS.md (Sept 29)

**Total:** 7 files → `archive/validation/`

---

### Category 5: ARCHIVE - CI/CD and GitHub Reports (Historical)

**Purpose:** Historical CI/CD workflow and GitHub sync reports
**Destination:** `archive/ci-cd/`
**Action:** ARCHIVE (keep for historical reference)

**Files:**
- CI_CD_FINAL_STATUS_REPORT.md (Sept 29)
- CI_CD_FIX_STATUS_REPORT.md (Sept 29)
- GITHUB_ACTIONS_ASSESSMENT_REPORT.md (Oct 1)
- GITHUB_SYNC_COMPLETE.md (Sept 29)
- PULL_REQUEST_SUMMARY.md (Sept 29)
- WORKFLOW_STATUS_REPORT.md (Sept 29)

**Total:** 6 files → `archive/ci-cd/`

---

### Category 6: ARCHIVE - Integration Completion Reports (Historical)

**Purpose:** Historical integration completion reports
**Destination:** `archive/integration/`
**Action:** ARCHIVE (keep for historical reference)

**Files:**
- ENVIRONMENT_MIGRATION_SUMMARY.md (Sept 15)
- FRONTEND_INTEGRATION_COMPLETE.md (Sept 15)
- FRONTEND_MODEL_MANAGEMENT_INTEGRATION.md (Sept 15)
- INTEGRATION_COMPLETE.md (Sept 22)
- MODEL_MANAGEMENT_INTEGRATION.md (Sept 15)
- OPENROUTER_AUTHENTICATION_INTEGRATION.md (Sept 15)
- PLAYER_PREFERENCE_SYSTEM_IMPLEMENTATION_REPORT.md (Sept 18)
- THERAPEUTIC_CONTENT_INTEGRATION_SUMMARY.md (Sept 14)
- TTA_SINGLE_PLAYER_TESTING_IMPLEMENTATION_SUMMARY.md (Sept 15)

**Total:** 9 files → `archive/integration/`

---

### Category 7: KEEP - Current Setup and Configuration Guides

**Purpose:** Active setup and configuration documentation
**Destination:** `docs/setup/`
**Action:** KEEP and MOVE

**Files:**
- DEVELOPMENT_SETUP.md (Sept 26) → `docs/setup/`
- ENVIRONMENT_SETUP.md (Sept 15) → `docs/setup/`
- MCP_SETUP_README.md (Sept 15) → `docs/setup/`
- TESTING_DATABASE_SETUP.md (Sept 30) → `docs/setup/`
- UV_CONFIGURATION_GUIDE.md (Oct 3) → `docs/setup/`
- UV_CONFIGURATION_SUMMARY.md (Oct 3) → **REVIEW** (may consolidate with UV_CONFIGURATION_GUIDE.md)

**Total:** 6 files (5 keep, 1 review for consolidation)

---

### Category 8: KEEP - Deployment Guides

**Purpose:** Active deployment documentation
**Destination:** `docs/deployment/`
**Action:** KEEP and MOVE

**Files:**
- CLOUDFLARE_STAGING_SETUP.md (Sept 16) → `docs/deployment/`
- PRODUCTION_DEPLOYMENT_GUIDE.md (Sept 16) → `docs/deployment/`
- STAGING_DEPLOYMENT_PLAN.md (Sept 15) → `docs/deployment/`
- STAGING_DEPLOYMENT_READY.md (Sept 15) → **REVIEW** (may consolidate with STAGING_DEPLOYMENT_PLAN.md)
- STAGING_HOSTING_ANALYSIS.md (Sept 17) → `docs/deployment/`

**Total:** 5 files (4 keep, 1 review for consolidation)

---

### Category 9: KEEP - Testing Documentation

**Purpose:** Active testing documentation
**Destination:** `docs/testing/`
**Action:** KEEP and MOVE

**Files:**
- TESTING_DIRECTORIES_ANALYSIS.md (Oct 3) → `docs/testing/`
- TESTING_GUIDE.md (Oct 3) → `docs/testing/`

**Note:** These are recent (Oct 3) and provide valuable testing structure documentation.

**Total:** 2 files

---

### Category 10: KEEP - Development Guides

**Purpose:** Active development documentation
**Destination:** `docs/development/`
**Action:** KEEP and MOVE

**Files:**
- EXECUTIVE_SUMMARY_TYPE_STRATEGY.md (Oct 2) → `docs/development/`
- FREE_MODELS_FILTER_GUIDE.md (Sept 15) → `docs/development/`
- GIT_COMMIT_STRATEGY.md (Sept 29) → `docs/development/`
- PROOF_OF_CONCEPT_PYRIGHT.md (Oct 2) → `docs/development/`
- TYPE_ANNOTATION_STRATEGY_ANALYSIS.md (Oct 2) → `docs/development/`

**Total:** 5 files

---

### Category 11: KEEP - Operations and Maintenance

**Purpose:** Active operational documentation
**Destination:** `docs/operations/`
**Action:** KEEP and MOVE

**Files:**
- DATABASE_PERFORMANCE_OPTIMIZATION.md (Sept 29) → `docs/operations/`
- FILESYSTEM_OPTIMIZATION_REPORT.md (Sept 26) → `docs/operations/`
- OPERATIONAL_EXCELLENCE_REPORT.md (Sept 26) → `docs/operations/`
- PRODUCTION_READINESS_ASSESSMENT.md (Sept 29) → `docs/operations/`
- SECURITY_FINDINGS_ACCEPTED_RISKS.md (Sept 30) → `docs/operations/security/`
- SECURITY_HARDENING_REPORT.md (Sept 29) → `docs/operations/security/`
- SECURITY_REMEDIATION_SUMMARY.md (Sept 30) → `docs/operations/security/`

**Total:** 7 files

---

### Category 12: KEEP - Integration Guides

**Purpose:** Active integration documentation
**Destination:** `docs/integration/`
**Action:** KEEP and MOVE

**Files:**
- GITHUB_SECRETS_GUIDE.md (Sept 16) → `docs/integration/`
- MCP_VERIFICATION_REPORT.md (Sept 15) → `docs/integration/`
- SENTRY_INTEGRATION_GUIDE.md (Sept 16) → `docs/integration/`

**Total:** 3 files

---

### Category 13: KEEP - Analytics and Monitoring

**Purpose:** Active analytics and monitoring documentation
**Destination:** `docs/operations/monitoring/`
**Action:** KEEP and MOVE

**Files:**
- grafana_access_guide.md (Sept 27) → `docs/operations/monitoring/`
- neo4j_browser_troubleshooting.md (Sept 16) → `docs/operations/monitoring/`
- tta_analytics_executive_summary.md (Sept 27) → `docs/operations/monitoring/`
- tta_analytics_report.md (Sept 27) → `docs/operations/monitoring/`
- tta_data_visualization_assessment.md (Sept 27) → `docs/operations/monitoring/`

**Total:** 5 files

---

### Category 14: REVIEW - Potentially Obsolete or Duplicate

**Purpose:** Files that need content review before categorization
**Action:** REVIEW CONTENT, then decide

**Files:**
- NEXT_STEPS_GUIDE.md (Sept 29) - **REVIEW:** May be outdated operational guide
- UI_UX_ENHANCEMENT_RECOMMENDATIONS.md (Sept 29) - **REVIEW:** Recommendations may be implemented or outdated

**Total:** 2 files

---

### Category 15: KEEP - Main Documentation

**Purpose:** Core project documentation
**Destination:** Root directory (keep in place)
**Action:** KEEP IN ROOT, UPDATE CONTENT

**Files:**
- README.md (Sept 15) - **UPDATE:** Add references to new directory structure

**Total:** 1 file

---

## Summary Statistics

| Category | Files | Action | Destination |
|----------|-------|--------|-------------|
| Phase Reports | 27 | ARCHIVE | `archive/phases/` |
| Task Reports | 9 | ARCHIVE | `archive/tasks/` |
| Fix Reports | 14 | ARCHIVE | `archive/fixes/` |
| Validation Reports | 7 | ARCHIVE | `archive/validation/` |
| CI/CD Reports | 6 | ARCHIVE | `archive/ci-cd/` |
| Integration Reports | 9 | ARCHIVE | `archive/integration/` |
| Setup Guides | 6 | KEEP | `docs/setup/` |
| Deployment Guides | 5 | KEEP | `docs/deployment/` |
| Testing Docs | 2 | KEEP | `docs/testing/` |
| Development Guides | 5 | KEEP | `docs/development/` |
| Operations Docs | 7 | KEEP | `docs/operations/` |
| Integration Guides | 3 | KEEP | `docs/integration/` |
| Monitoring Docs | 5 | KEEP | `docs/operations/monitoring/` |
| Review Needed | 2 | REVIEW | TBD |
| Main Docs | 1 | UPDATE | Root |
| **TOTAL** | **108** | | |

**Archive:** 72 files (67%)
**Keep/Move:** 33 files (31%)
**Review:** 2 files (2%)

---

## Next Steps

1. Review the 2 files flagged for content review
2. Identify consolidation opportunities (UV_CONFIGURATION_*, STAGING_DEPLOYMENT_*)
3. Categorize test files and screenshots
4. Evaluate docker-compose files
5. Create migration script
6. Execute reorganization

---

## Test Files Categorization

### Category 16: MOVE - Test Scripts to Testing Directory

**Purpose:** Scattered test scripts from development sessions
**Destination:** `artifacts/test-scripts/` (historical) or `tests/manual/` (if still relevant)
**Action:** MOVE to artifacts (most are historical one-off tests)

**Python Test Scripts:**
- test-character-creation-fixed.py (Sept 29)
- test_auth_flow_complete.py (Sept 23)
- test_containerized_deployment.py (Sept 26)
- test_world_selection.py (Sept 24)

**JavaScript Test Scripts:**
- test-character-creation-success.js (Sept 18)
- test-character-creation.js (Sept 17)
- test-complete-character-creation-fixed.js (Sept 17)
- test-complete-flow.js (Sept 17)
- test-dev-server-character-creation-complete.js (Sept 17)
- test-dev-server-simple.js (Sept 17)
- test-enhanced-ai-narrative-e2e.js (Sept 18)
- test-playwright-tools.js (Sept 18)
- test-playwright.js (Sept 17)
- test_openrouter_auth_integration.js (Sept 15)

**Shell Scripts:**
- test-grafana-mcp.sh (Sept 15)

**HTML Test Files:**
- test_auth_ui.html (Sept 15)

**Test Output Files:**
- test_run_after_priority2.txt (Sept 30)
- test_run_full.txt (Sept 30)
- test_run_output.txt (Sept 30)
- test_summary.txt (Sept 30)

**Total:** 20 files → `artifacts/test-scripts/`

**Rationale:** These are one-off test scripts from development sessions, not part of the formal test suite (tests/ or testing/). They're historical artifacts showing how features were tested during development.

---

## Screenshots and Artifacts Categorization

### Category 17: MOVE - Screenshots to Artifacts

**Purpose:** UI screenshots from testing sessions
**Destination:** `artifacts/screenshots/`
**Action:** MOVE and organize by category

**Authentication Flow Screenshots (5 files):**
- auth-01-initial.png
- auth-02-before-login.png
- auth-03-after-login.png
- button-not-clickable.png
- character-creation-error.png

→ `artifacts/screenshots/auth/`

**Character Creation Screenshots (7 files):**
- all-char-01-after-login.png
- all-char-02-after-3-Create_First_Character.png
- char-01-after-login.png
- char-02-after-char-button.png
- char-05-final.png
- character-creation-final-success.png

→ `artifacts/screenshots/character/`

**Chat Interface Screenshots (10 files):**
- chat-focused-01-dashboard.png
- chat-focused-02-chat-interface.png
- chat-focused-03-turn-2.png
- chat-focused-03-turn-4.png
- chat-focused-04-final.png
- chat-focused-error.png
- chat-test-01-landing.png
- chat-test-02-dashboard.png
- chat-test-error-final.png

→ `artifacts/screenshots/chat/`

**Additional Screenshots (~38 more files):**
→ Categorize remaining 38 PNG files by prefix/purpose

**Total:** ~60 PNG files → `artifacts/screenshots/`

---

## Docker Compose Files Evaluation

### Category 18: KEEP - Current Docker Compose Files

**Purpose:** Active docker-compose configurations
**Destination:** Root directory (keep in place)
**Action:** KEEP

**Files:**
- docker-compose.yml - Base/shared configuration
- docker-compose.dev.yml - Development environment ✅ (aligned with .env.dev)
- docker-compose.staging-homelab.yml - Staging homelab ✅ (aligned with .env.staging)
- docker-compose.test.yml - Test environment
- docker-compose.analytics.yml - Analytics services (if still used)

**Total:** 5 files (keep in root)

---

### Category 19: EVALUATE - Potentially Obsolete Docker Compose Files

**Purpose:** Docker compose files that may be superseded
**Destination:** `obsolete/docker-compose/` (temporary holding)
**Action:** EVALUATE, then DELETE or KEEP

**Files to Evaluate:**

1. **docker-compose.homelab.yml**
   - **Status:** Likely obsolete (superseded by docker-compose.staging-homelab.yml)
   - **Action:** MOVE to obsolete/, verify no references, then DELETE

2. **docker-compose.staging.yml**
   - **Status:** Likely obsolete (superseded by docker-compose.staging-homelab.yml)
   - **Action:** MOVE to obsolete/, verify no references, then DELETE

3. **docker-compose.hotreload.yml**
   - **Status:** References tta.dev/ which is minimal
   - **Action:** EVALUATE if hot reload is still used, update or DELETE

4. **docker-compose.phase2a.yml**
   - **Status:** Phase-specific, likely obsolete
   - **Action:** MOVE to obsolete/, verify no references, then DELETE

**Total:** 4 files → Evaluate and likely delete

---

## Subdirectory Evaluation

### Category 20: REMOVE - Obsolete Subdirectories

**Purpose:** Minimal/empty subdirectories from old structure
**Destination:** `obsolete/` (temporary) or DELETE
**Action:** EVALUATE then REMOVE

**tta.dev/ (2 files):**
- Dockerfile (old)
- docker-compose.yml (old)
- **Status:** Minimal content, not part of current architecture
- **Action:** MOVE to obsolete/, then DELETE after verification

**tta.prototype/ (minimal):**
- Dockerfile (old)
- docker-compose.yml (old)
- neo4j/ directory (empty subdirs)
- **Status:** Prototype artifacts, not current
- **Action:** MOVE to obsolete/, then DELETE after verification

**tta.prod/ (empty):**
- **Status:** Empty directory
- **Action:** DELETE immediately

**Total:** 3 subdirectories → Remove

---

## Updated Summary Statistics

| Category | Files | Action | Destination |
|----------|-------|--------|-------------|
| **MARKDOWN FILES** | | | |
| Phase Reports | 27 | ARCHIVE | `archive/phases/` |
| Task Reports | 9 | ARCHIVE | `archive/tasks/` |
| Fix Reports | 14 | ARCHIVE | `archive/fixes/` |
| Validation Reports | 7 | ARCHIVE | `archive/validation/` |
| CI/CD Reports | 6 | ARCHIVE | `archive/ci-cd/` |
| Integration Reports | 9 | ARCHIVE | `archive/integration/` |
| Setup Guides | 6 | KEEP | `docs/setup/` |
| Deployment Guides | 5 | KEEP | `docs/deployment/` |
| Testing Docs | 2 | KEEP | `docs/testing/` |
| Development Guides | 5 | KEEP | `docs/development/` |
| Operations Docs | 7 | KEEP | `docs/operations/` |
| Integration Guides | 3 | KEEP | `docs/integration/` |
| Monitoring Docs | 5 | KEEP | `docs/operations/monitoring/` |
| Review Needed | 2 | ARCHIVE | `archive/recommendations/` |
| Main Docs | 1 | UPDATE | Root |
| **TEST FILES** | | | |
| Test Scripts | 20 | MOVE | `artifacts/test-scripts/` |
| **SCREENSHOTS** | | | |
| Screenshots | ~60 | MOVE | `artifacts/screenshots/` |
| **DOCKER COMPOSE** | | | |
| Current Compose | 5 | KEEP | Root |
| Obsolete Compose | 4 | EVALUATE | `obsolete/` → DELETE |
| **SUBDIRECTORIES** | | | |
| tta.* directories | 3 | REMOVE | `obsolete/` → DELETE |
| **TOTALS** | | | |
| Archive | 74 | 67% | `archive/` |
| Keep/Move | 46 | 42% | `docs/`, `artifacts/` |
| Evaluate/Delete | 7 | 6% | `obsolete/` → DELETE |
| **GRAND TOTAL** | **~200** | | |

---

## Consolidation Opportunities

### Files to Review for Consolidation:

1. **UV Configuration:**
   - UV_CONFIGURATION_GUIDE.md (Oct 3) - Comprehensive guide
   - UV_CONFIGURATION_SUMMARY.md (Oct 3) - Summary
   - **Recommendation:** Keep GUIDE, archive SUMMARY (redundant)

2. **Staging Deployment:**
   - STAGING_DEPLOYMENT_PLAN.md (Sept 15) - Planning document
   - STAGING_DEPLOYMENT_READY.md (Sept 15) - Readiness checklist
   - **Recommendation:** Consolidate into single STAGING_DEPLOYMENT_GUIDE.md

3. **UI/UX Recommendations:**
   - UI_UX_ENHANCEMENT_RECOMMENDATIONS.md (Sept 29) - Status: COMPLETE
   - **Recommendation:** ARCHIVE (historical recommendations that were implemented)

4. **Next Steps Guide:**
   - NEXT_STEPS_GUIDE.md (Sept 29) - Operational guide from Sept 29
   - **Recommendation:** REVIEW content, likely outdated, ARCHIVE

---

**Status:** ✅ Phase 1-2 Complete - Full Categorization
**Next:** Phase 3 - Create Migration Script


---
**Logseq:** [[TTA.dev/Docs/Project/Project_reorganization_plan]]
