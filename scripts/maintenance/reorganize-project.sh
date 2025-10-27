#!/bin/bash
# TTA Project Reorganization Script
# Purpose: Reorganize 200+ files according to PROJECT_REORGANIZATION_PLAN.md
# Date: 2025-10-04
# Usage: ./scripts/maintenance/reorganize-project.sh [--dry-run] [--execute]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DRY_RUN=true
BACKUP_DIR="${PROJECT_ROOT}/backup-$(date +%Y%m%d-%H%M%S)"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            ;;
        --execute)
            DRY_RUN=false
            ;;
        --help)
            echo "Usage: $0 [--dry-run] [--execute]"
            echo "  --dry-run   Show what would be done (default)"
            echo "  --execute   Actually perform the reorganization"
            exit 0
            ;;
    esac
done

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

create_directory() {
    local dir="$1"
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Would create directory: $dir"
    else
        mkdir -p "$dir"
        log_success "Created directory: $dir"
    fi
}

move_file() {
    local src="$1"
    local dest="$2"

    if [ ! -f "$src" ]; then
        log_warning "Source file not found: $src"
        return 0  # Don't exit script, just skip this file
    fi

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Would move: $src -> $dest"
    else
        mv "$src" "$dest"
        log_success "Moved: $(basename $src) -> $dest"
    fi
}

move_files_by_pattern() {
    local pattern="$1"
    local dest_dir="$2"
    local description="$3"

    log_info "Processing: $description"

    for file in $pattern; do
        if [ -f "$file" ]; then
            move_file "$file" "$dest_dir/$(basename $file)"
        fi
    done
}

# Main execution
main() {
    cd "$PROJECT_ROOT"

    if [ "$DRY_RUN" = true ]; then
        log_warning "=== DRY RUN MODE ==="
        log_warning "No files will be moved. Use --execute to perform actual reorganization."
        echo ""
    else
        log_warning "=== EXECUTION MODE ==="
        log_warning "Files will be moved. Creating backup first..."
        mkdir -p "$BACKUP_DIR"
        log_success "Backup directory created: $BACKUP_DIR"
        echo ""
    fi

    log_info "Starting TTA Project Reorganization..."
    echo ""

    # ========================================
    # Phase 1: Create Directory Structure
    # ========================================
    log_info "=== Phase 1: Creating Directory Structure ==="

    # Archive directories
    create_directory "archive"
    create_directory "archive/phases/phase1"
    create_directory "archive/phases/phase2"
    create_directory "archive/phases/phase3"
    create_directory "archive/tasks"
    create_directory "archive/fixes"
    create_directory "archive/validation"
    create_directory "archive/ci-cd"
    create_directory "archive/integration"
    create_directory "archive/recommendations"

    # Docs directories
    create_directory "docs/setup"
    create_directory "docs/deployment"
    create_directory "docs/testing"
    create_directory "docs/development"
    create_directory "docs/operations"
    create_directory "docs/operations/security"
    create_directory "docs/operations/monitoring"
    create_directory "docs/integration"

    # Artifacts directories
    create_directory "artifacts"
    create_directory "artifacts/test-scripts"
    create_directory "artifacts/screenshots"
    create_directory "artifacts/screenshots/auth"
    create_directory "artifacts/screenshots/character"
    create_directory "artifacts/screenshots/chat"
    create_directory "artifacts/screenshots/testing"
    create_directory "artifacts/test-results"

    # Obsolete directory (temporary)
    create_directory "obsolete"
    create_directory "obsolete/docker-compose"
    create_directory "obsolete/subdirectories"

    echo ""

    # ========================================
    # Phase 2: Move Markdown Files
    # ========================================
    log_info "=== Phase 2: Moving Markdown Files ==="

    # Phase 1 Reports
    log_info "Moving Phase 1 reports..."
    move_files_by_pattern "PHASE1*.md" "archive/phases/phase1" "Phase 1 reports"
    move_files_by_pattern "PHASE_1*.md" "archive/phases/phase1" "Phase 1 reports (alt naming)"
    move_file "PHASE1_ACTION_PLAN.md" "archive/phases/phase1/PHASE1_ACTION_PLAN.md"
    move_file "PHASE1_WORKFLOW_RESULTS_ANALYSIS.md" "archive/phases/phase1/PHASE1_WORKFLOW_RESULTS_ANALYSIS.md"
    move_file "STAGE1_COMPLETION_REPORT.md" "archive/phases/phase1/STAGE1_COMPLETION_REPORT.md"

    # Phase 2-3 Reports
    log_info "Moving Phase 2-3 reports..."
    move_file "phase1_completion_summary.md" "archive/phases/phase1/phase1_completion_summary.md"
    move_file "phase1_infrastructure_restoration_report.md" "archive/phases/phase1/phase1_infrastructure_restoration_report.md"
    move_file "phase2_completion_report.md" "archive/phases/phase2/phase2_completion_report.md"
    move_files_by_pattern "phase3*.md" "archive/phases/phase3" "Phase 3 reports"

    # Task Reports
    log_info "Moving task reports..."
    move_files_by_pattern "TASK*.md" "archive/tasks" "Task completion reports"

    # Fix Reports
    log_info "Moving fix reports..."
    move_file "API_VALIDATION_IMPROVEMENTS.md" "archive/fixes/API_VALIDATION_IMPROVEMENTS.md"
    move_file "BACKEND_STARTUP_FIX.md" "archive/fixes/BACKEND_STARTUP_FIX.md"
    move_file "COMPREHENSIVE_FIX_SUMMARY.md" "archive/fixes/COMPREHENSIVE_FIX_SUMMARY.md"
    move_file "DOCKER_BUILD_FAILURE_ANALYSIS.md" "archive/fixes/DOCKER_BUILD_FAILURE_ANALYSIS.md"
    move_file "E2E_WORKFLOW_OPTIMIZATION_SUMMARY.md" "archive/fixes/E2E_WORKFLOW_OPTIMIZATION_SUMMARY.md"
    move_file "FIX_LIST_DIRECTORY_RECREATION.md" "archive/fixes/FIX_LIST_DIRECTORY_RECREATION.md"
    move_file "NEO4J_BROWSER_RESOLUTION_SUMMARY.md" "archive/fixes/NEO4J_BROWSER_RESOLUTION_SUMMARY.md"
    move_file "PYTEST_VSCODE_FIX_SUMMARY.md" "archive/fixes/PYTEST_VSCODE_FIX_SUMMARY.md"
    move_file "ROOT_CAUSE_ANALYSIS_LIST_DIRECTORY.md" "archive/fixes/ROOT_CAUSE_ANALYSIS_LIST_DIRECTORY.md"
    move_file "TEST_FAILURE_ANALYSIS_REPORT.md" "archive/fixes/TEST_FAILURE_ANALYSIS_REPORT.md"
    move_file "TEST_FIXES_PROGRESS.md" "archive/fixes/TEST_FIXES_PROGRESS.md"
    move_file "TEST_FIXES_SUMMARY.md" "archive/fixes/TEST_FIXES_SUMMARY.md"
    move_file "VSCODE_PYTEST_CACHE_FIX_COMPLETE.md" "archive/fixes/VSCODE_PYTEST_CACHE_FIX_COMPLETE.md"
    move_file "VSCODE_PYTEST_INTEGRATION_FIX.md" "archive/fixes/VSCODE_PYTEST_INTEGRATION_FIX.md"

    # Validation Reports
    log_info "Moving validation reports..."
    move_file "COMPREHENSIVE_VALIDATION_SUMMARY.md" "archive/validation/COMPREHENSIVE_VALIDATION_SUMMARY.md"
    move_file "FINAL_VALIDATION_REPORT.md" "archive/validation/FINAL_VALIDATION_REPORT.md"
    move_file "OPENROUTER_AUTHENTICATION_TEST_REPORT.md" "archive/validation/OPENROUTER_AUTHENTICATION_TEST_REPORT.md"
    move_file "TEST_RESULTS_BASELINE.md" "archive/validation/TEST_RESULTS_BASELINE.md"
    move_file "TESTING_SUMMARY.md" "archive/validation/TESTING_SUMMARY.md"
    move_file "VALIDATION_RESULTS.md" "archive/validation/VALIDATION_RESULTS.md"
    move_file "VALIDATION_TEST_RESULTS.md" "archive/validation/VALIDATION_TEST_RESULTS.md"

    # CI/CD Reports
    log_info "Moving CI/CD reports..."
    move_file "CI_CD_FINAL_STATUS_REPORT.md" "archive/ci-cd/CI_CD_FINAL_STATUS_REPORT.md"
    move_file "CI_CD_FIX_STATUS_REPORT.md" "archive/ci-cd/CI_CD_FIX_STATUS_REPORT.md"
    move_file "GITHUB_ACTIONS_ASSESSMENT_REPORT.md" "archive/ci-cd/GITHUB_ACTIONS_ASSESSMENT_REPORT.md"
    move_file "GITHUB_SYNC_COMPLETE.md" "archive/ci-cd/GITHUB_SYNC_COMPLETE.md"
    move_file "PULL_REQUEST_SUMMARY.md" "archive/ci-cd/PULL_REQUEST_SUMMARY.md"
    move_file "WORKFLOW_STATUS_REPORT.md" "archive/ci-cd/WORKFLOW_STATUS_REPORT.md"

    # Integration Reports
    log_info "Moving integration reports..."
    move_file "ENVIRONMENT_MIGRATION_SUMMARY.md" "archive/integration/ENVIRONMENT_MIGRATION_SUMMARY.md"
    move_file "FRONTEND_INTEGRATION_COMPLETE.md" "archive/integration/FRONTEND_INTEGRATION_COMPLETE.md"
    move_file "FRONTEND_MODEL_MANAGEMENT_INTEGRATION.md" "archive/integration/FRONTEND_MODEL_MANAGEMENT_INTEGRATION.md"
    move_file "INTEGRATION_COMPLETE.md" "archive/integration/INTEGRATION_COMPLETE.md"
    move_file "MODEL_MANAGEMENT_INTEGRATION.md" "archive/integration/MODEL_MANAGEMENT_INTEGRATION.md"
    move_file "OPENROUTER_AUTHENTICATION_INTEGRATION.md" "archive/integration/OPENROUTER_AUTHENTICATION_INTEGRATION.md"
    move_file "PLAYER_PREFERENCE_SYSTEM_IMPLEMENTATION_REPORT.md" "archive/integration/PLAYER_PREFERENCE_SYSTEM_IMPLEMENTATION_REPORT.md"
    move_file "THERAPEUTIC_CONTENT_INTEGRATION_SUMMARY.md" "archive/integration/THERAPEUTIC_CONTENT_INTEGRATION_SUMMARY.md"
    move_file "TTA_SINGLE_PLAYER_TESTING_IMPLEMENTATION_SUMMARY.md" "archive/integration/TTA_SINGLE_PLAYER_TESTING_IMPLEMENTATION_SUMMARY.md"

    # Recommendations (archive)
    log_info "Moving recommendations..."
    move_file "UI_UX_ENHANCEMENT_RECOMMENDATIONS.md" "archive/recommendations/UI_UX_ENHANCEMENT_RECOMMENDATIONS.md"
    move_file "NEXT_STEPS_GUIDE.md" "archive/recommendations/NEXT_STEPS_GUIDE.md"

    echo ""

    # ========================================
    # Phase 3: Move Current Documentation
    # ========================================
    log_info "=== Phase 3: Moving Current Documentation ==="

    # Setup Guides
    log_info "Moving setup guides..."
    move_file "DEVELOPMENT_SETUP.md" "docs/setup/DEVELOPMENT_SETUP.md"
    move_file "ENVIRONMENT_SETUP.md" "docs/setup/ENVIRONMENT_SETUP.md"
    move_file "MCP_SETUP_README.md" "docs/setup/MCP_SETUP_README.md"
    move_file "TESTING_DATABASE_SETUP.md" "docs/setup/TESTING_DATABASE_SETUP.md"
    move_file "UV_CONFIGURATION_GUIDE.md" "docs/setup/UV_CONFIGURATION_GUIDE.md"
    move_file "UV_CONFIGURATION_SUMMARY.md" "archive/recommendations/UV_CONFIGURATION_SUMMARY.md"  # Consolidate

    # Deployment Guides
    log_info "Moving deployment guides..."
    move_file "CLOUDFLARE_STAGING_SETUP.md" "docs/deployment/CLOUDFLARE_STAGING_SETUP.md"
    move_file "PRODUCTION_DEPLOYMENT_GUIDE.md" "docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md"
    move_file "STAGING_DEPLOYMENT_PLAN.md" "docs/deployment/STAGING_DEPLOYMENT_PLAN.md"
    move_file "STAGING_DEPLOYMENT_READY.md" "archive/recommendations/STAGING_DEPLOYMENT_READY.md"  # Consolidate
    move_file "STAGING_HOSTING_ANALYSIS.md" "docs/deployment/STAGING_HOSTING_ANALYSIS.md"

    # Testing Documentation
    log_info "Moving testing documentation..."
    move_file "TESTING_DIRECTORIES_ANALYSIS.md" "docs/testing/TESTING_DIRECTORIES_ANALYSIS.md"
    move_file "TESTING_GUIDE.md" "docs/testing/TESTING_GUIDE.md"

    # Development Guides
    log_info "Moving development guides..."
    move_file "EXECUTIVE_SUMMARY_TYPE_STRATEGY.md" "docs/development/EXECUTIVE_SUMMARY_TYPE_STRATEGY.md"
    move_file "FREE_MODELS_FILTER_GUIDE.md" "docs/development/FREE_MODELS_FILTER_GUIDE.md"
    move_file "GIT_COMMIT_STRATEGY.md" "docs/development/GIT_COMMIT_STRATEGY.md"
    move_file "PROOF_OF_CONCEPT_PYRIGHT.md" "docs/development/PROOF_OF_CONCEPT_PYRIGHT.md"
    move_file "TYPE_ANNOTATION_STRATEGY_ANALYSIS.md" "docs/development/TYPE_ANNOTATION_STRATEGY_ANALYSIS.md"

    echo ""
    log_success "Phase 3 complete: Current documentation moved"

    # ========================================
    # Phase 4: Move Operations Documentation
    # ========================================
    log_info "=== Phase 4: Moving Operations Documentation ==="

    # Operations Docs
    log_info "Moving operations documentation..."
    move_file "DATABASE_PERFORMANCE_OPTIMIZATION.md" "docs/operations/DATABASE_PERFORMANCE_OPTIMIZATION.md"
    move_file "FILESYSTEM_OPTIMIZATION_REPORT.md" "docs/operations/FILESYSTEM_OPTIMIZATION_REPORT.md"
    move_file "OPERATIONAL_EXCELLENCE_REPORT.md" "docs/operations/OPERATIONAL_EXCELLENCE_REPORT.md"
    move_file "PRODUCTION_READINESS_ASSESSMENT.md" "docs/operations/PRODUCTION_READINESS_ASSESSMENT.md"

    # Security Docs
    log_info "Moving security documentation..."
    move_file "SECURITY_FINDINGS_ACCEPTED_RISKS.md" "docs/operations/security/SECURITY_FINDINGS_ACCEPTED_RISKS.md"
    move_file "SECURITY_HARDENING_REPORT.md" "docs/operations/security/SECURITY_HARDENING_REPORT.md"
    move_file "SECURITY_REMEDIATION_SUMMARY.md" "docs/operations/security/SECURITY_REMEDIATION_SUMMARY.md"

    # Integration Guides
    log_info "Moving integration guides..."
    move_file "GITHUB_SECRETS_GUIDE.md" "docs/integration/GITHUB_SECRETS_GUIDE.md"
    move_file "MCP_VERIFICATION_REPORT.md" "docs/integration/MCP_VERIFICATION_REPORT.md"
    move_file "SENTRY_INTEGRATION_GUIDE.md" "docs/integration/SENTRY_INTEGRATION_GUIDE.md"

    # Monitoring Docs
    log_info "Moving monitoring documentation..."
    move_file "grafana_access_guide.md" "docs/operations/monitoring/grafana_access_guide.md"
    move_file "neo4j_browser_troubleshooting.md" "docs/operations/monitoring/neo4j_browser_troubleshooting.md"
    move_file "tta_analytics_executive_summary.md" "docs/operations/monitoring/tta_analytics_executive_summary.md"
    move_file "tta_analytics_report.md" "docs/operations/monitoring/tta_analytics_report.md"
    move_file "tta_data_visualization_assessment.md" "docs/operations/monitoring/tta_data_visualization_assessment.md"

    echo ""
    log_success "Phase 4 complete: Operations documentation moved"

    # ========================================
    # Phase 5: Move Test Files and Artifacts
    # ========================================
    log_info "=== Phase 5: Moving Test Files and Artifacts ==="

    # Test Scripts
    log_info "Moving test scripts..."
    move_files_by_pattern "test-*.py" "artifacts/test-scripts" "Python test scripts"
    move_files_by_pattern "test_*.py" "artifacts/test-scripts" "Python test scripts (underscore)"
    move_files_by_pattern "test-*.js" "artifacts/test-scripts" "JavaScript test scripts"
    move_files_by_pattern "test_*.js" "artifacts/test-scripts" "JavaScript test scripts (underscore)"
    move_files_by_pattern "test-*.sh" "artifacts/test-scripts" "Shell test scripts"
    move_file "test_auth_ui.html" "artifacts/test-scripts/test_auth_ui.html"

    # Test Results
    log_info "Moving test results..."
    move_files_by_pattern "test_*.txt" "artifacts/test-results" "Test output files"

    # Screenshots - Auth
    log_info "Moving authentication screenshots..."
    move_file "auth-01-initial.png" "artifacts/screenshots/auth/auth-01-initial.png"
    move_file "auth-02-before-login.png" "artifacts/screenshots/auth/auth-02-before-login.png"
    move_file "auth-03-after-login.png" "artifacts/screenshots/auth/auth-03-after-login.png"
    move_file "button-not-clickable.png" "artifacts/screenshots/auth/button-not-clickable.png"
    move_file "character-creation-error.png" "artifacts/screenshots/auth/character-creation-error.png"

    # Screenshots - Character
    log_info "Moving character creation screenshots..."
    move_files_by_pattern "all-char-*.png" "artifacts/screenshots/character" "Character screenshots (all-char)"
    move_files_by_pattern "char-*.png" "artifacts/screenshots/character" "Character screenshots (char)"
    move_file "character-creation-final-success.png" "artifacts/screenshots/character/character-creation-final-success.png"

    # Screenshots - Chat
    log_info "Moving chat interface screenshots..."
    move_files_by_pattern "chat-*.png" "artifacts/screenshots/chat" "Chat screenshots"

    # Remaining screenshots
    log_info "Moving remaining screenshots..."
    move_files_by_pattern "*.png" "artifacts/screenshots/testing" "Other screenshots"

    echo ""
    log_success "Phase 5 complete: Test files and artifacts moved"

    # ========================================
    # Phase 6: Handle Obsolete Files
    # ========================================
    log_info "=== Phase 6: Moving Obsolete Files ==="

    # Obsolete Docker Compose Files
    log_info "Moving obsolete docker-compose files..."
    move_file "docker-compose.homelab.yml" "obsolete/docker-compose/docker-compose.homelab.yml"
    move_file "docker-compose.staging.yml" "obsolete/docker-compose/docker-compose.staging.yml"
    move_file "docker-compose.hotreload.yml" "obsolete/docker-compose/docker-compose.hotreload.yml"
    move_file "docker-compose.phase2a.yml" "obsolete/docker-compose/docker-compose.phase2a.yml"

    # Obsolete Subdirectories
    log_info "Moving obsolete subdirectories..."
    if [ -d "tta.dev" ]; then
        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY-RUN] Would move directory: tta.dev -> obsolete/subdirectories/"
        else
            mv "tta.dev" "obsolete/subdirectories/tta.dev"
            log_success "Moved directory: tta.dev"
        fi
    fi

    if [ -d "tta.prototype" ]; then
        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY-RUN] Would move directory: tta.prototype -> obsolete/subdirectories/"
        else
            mv "tta.prototype" "obsolete/subdirectories/tta.prototype"
            log_success "Moved directory: tta.prototype"
        fi
    fi

    if [ -d "tta.prod" ]; then
        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY-RUN] Would remove empty directory: tta.prod"
        else
            rmdir "tta.prod" 2>/dev/null || log_warning "tta.prod not empty or doesn't exist"
            log_success "Removed directory: tta.prod"
        fi
    fi

    echo ""
    log_success "Phase 6 complete: Obsolete files moved"

    # ========================================
    # Phase 7: Create README Files
    # ========================================
    log_info "=== Phase 7: Creating README Files ==="

    if [ "$DRY_RUN" = false ]; then
        # Archive README
        cat > "archive/README.md" << 'EOF'
# TTA Project Archive

This directory contains historical documents from TTA development sessions.

## Purpose

These files are preserved for historical reference and project continuity. They document:
- Completed development phases
- Task completion reports
- Bug fixes and resolutions
- Validation and test reports
- CI/CD workflow reports
- Integration completion reports

## Organization

- `phases/` - Phase completion reports (Phase 1, 2, 3)
- `tasks/` - Task-specific completion summaries
- `fixes/` - Bug fix and resolution reports
- `validation/` - Validation and test execution reports
- `ci-cd/` - CI/CD workflow and GitHub sync reports
- `integration/` - Integration completion reports
- `recommendations/` - Historical recommendations and guides

## Note

These documents are **historical** and may contain outdated information. For current documentation, see the `docs/` directory.

**Last Updated:** 2025-10-04
EOF
        log_success "Created archive/README.md"

        # Artifacts README
        cat > "artifacts/README.md" << 'EOF'
# TTA Project Artifacts

This directory contains test artifacts, screenshots, and generated reports from development and testing sessions.

## Organization

- `test-scripts/` - One-off test scripts from development sessions
- `screenshots/` - UI screenshots from testing
  - `auth/` - Authentication flow screenshots
  - `character/` - Character creation screenshots
  - `chat/` - Chat interface screenshots
  - `testing/` - General testing screenshots
- `test-results/` - Test execution output files

## Purpose

These artifacts provide visual and execution evidence of:
- Feature development and testing
- UI/UX validation
- Bug reproduction and verification
- Integration testing results

## Note

These are **historical artifacts** from development sessions. For current test suites, see `tests/` and `testing/` directories.

**Last Updated:** 2025-10-04
EOF
        log_success "Created artifacts/README.md"

        # Obsolete README
        cat > "obsolete/README.md" << 'EOF'
# Obsolete Files - Pending Deletion

This directory contains files that are no longer part of the current TTA architecture.

## Contents

- `docker-compose/` - Superseded docker-compose configurations
- `subdirectories/` - Old directory structures (tta.dev, tta.prototype, tta.prod)

## Action Required

These files should be reviewed and deleted after verification that:
1. No active references exist in the codebase
2. No critical information is lost
3. Functionality is preserved in current files

## Timeline

- **Created:** 2025-10-04
- **Review By:** 2025-10-11
- **Delete By:** 2025-10-18

**Status:** Pending Review
EOF
        log_success "Created obsolete/README.md"
    else
        log_info "[DRY-RUN] Would create README files in archive/, artifacts/, obsolete/"
    fi

    echo ""
    log_success "Phase 7 complete: README files created"
}

# Run main function
main "$@"

echo ""
if [ "$DRY_RUN" = true ]; then
    log_warning "=== DRY RUN COMPLETE ==="
    log_info "Review the planned changes above."
    log_info "Run with --execute to perform actual reorganization."
else
    log_success "=== REORGANIZATION COMPLETE ==="
    log_info "Backup created at: $BACKUP_DIR"
    log_info "Next steps:"
    log_info "  1. Review moved files in new locations"
    log_info "  2. Run validation: ./scripts/maintenance/validate-structure.sh"
    log_info "  3. Update cross-references in documentation"
    log_info "  4. Review obsolete/ directory and delete after verification"
    log_info "  5. Update main README.md with new structure"
fi
