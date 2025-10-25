#!/usr/bin/env bash
# GitHub Workflow Validation Script
# Validates GitHub Actions workflow files and checks for common issues

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        echo "Install: https://cli.github.com/"
        return 1
    fi
    print_success "GitHub CLI is installed: $(gh --version | head -1)"
}

check_workflow_syntax() {
    print_header "Checking Workflow Syntax"
    
    local workflows_dir=".github/workflows"
    local errors=0
    
    if [ ! -d "$workflows_dir" ]; then
        print_error "Workflows directory not found: $workflows_dir"
        return 1
    fi
    
    for workflow in "$workflows_dir"/*.yml "$workflows_dir"/*.yaml; do
        if [ -f "$workflow" ]; then
            local name=$(basename "$workflow")
            
            # Basic YAML validation using Python
            if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
                print_success "$name - Valid YAML syntax"
            else
                print_error "$name - Invalid YAML syntax"
                ((errors++))
            fi
            
            # Check for common issues
            if grep -q "uses: actions/checkout@v[1-2]" "$workflow"; then
                print_warning "$name - Uses old checkout action (v1 or v2)"
            fi
            
            if grep -q "python-version: 3\\.12" "$workflow"; then
                print_success "$name - Uses Python 3.12"
            fi
            
            if grep -q "astral-sh/setup-uv" "$workflow"; then
                print_success "$name - Uses UV setup action"
            fi
        fi
    done
    
    if [ $errors -eq 0 ]; then
        print_success "All workflows have valid syntax"
        return 0
    else
        print_error "Found $errors workflow(s) with syntax errors"
        return 1
    fi
}

list_workflows() {
    print_header "GitHub Workflows"
    
    if command -v gh &> /dev/null; then
        gh workflow list
    else
        echo "Workflows in .github/workflows/:"
        ls -1 .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null | xargs -n1 basename
    fi
}

check_recent_runs() {
    print_header "Recent Workflow Runs"
    
    if ! command -v gh &> /dev/null; then
        print_warning "GitHub CLI not installed. Skipping run history."
        return
    fi
    
    gh run list --limit 10
}

check_workflow_status() {
    print_header "Workflow Status"
    
    if ! command -v gh &> /dev/null; then
        print_warning "GitHub CLI not installed. Skipping status check."
        return
    fi
    
    local workflows=("tests.yml" "code-quality.yml" "docker-build.yml")
    
    for workflow in "${workflows[@]}"; do
        echo ""
        echo "Status for $workflow:"
        gh workflow view "$workflow" 2>/dev/null || print_warning "Workflow $workflow not found"
    done
}

check_secrets() {
    print_header "Checking Required Secrets"
    
    local required_secrets=(
        "OPENROUTER_API_KEY"
        "NEO4J_PASSWORD"
        "GRAFANA_ADMIN_PASSWORD"
    )
    
    echo "Required secrets for workflows:"
    for secret in "${required_secrets[@]}"; do
        echo "  - $secret"
    done
    
    echo ""
    print_warning "Verify secrets in: GitHub → Settings → Secrets and variables → Actions"
    
    if command -v gh &> /dev/null; then
        echo ""
        echo "Repository secrets (names only):"
        gh secret list 2>/dev/null || print_warning "Unable to list secrets (may need authentication)"
    fi
}

validate_uv_setup() {
    print_header "Validating UV Setup in Workflows"
    
    local workflow=".github/workflows/tests.yml"
    
    if [ ! -f "$workflow" ]; then
        print_error "tests.yml not found"
        return 1
    fi
    
    if grep -q "astral-sh/setup-uv@v1" "$workflow"; then
        print_success "Uses astral-sh/setup-uv@v1"
    else
        print_warning "setup-uv action not found or wrong version"
    fi
    
    if grep -q "uv sync" "$workflow"; then
        print_success "Uses 'uv sync' for dependency installation"
    else
        print_warning "No 'uv sync' command found"
    fi
    
    if grep -q "uv run pytest" "$workflow"; then
        print_success "Uses 'uv run pytest' for test execution"
    else
        print_warning "No 'uv run pytest' command found"
    fi
}

check_branch_protection() {
    print_header "Branch Protection Settings"
    
    if ! command -v gh &> /dev/null; then
        print_warning "GitHub CLI not installed. Cannot check branch protection."
        return
    fi
    
    local branches=("main" "staging" "development")
    
    for branch in "${branches[@]}"; do
        echo ""
        echo "Checking protection for '$branch':"
        if gh api "repos/:owner/:repo/branches/$branch/protection" 2>/dev/null | jq -r '.required_status_checks.contexts[]' 2>/dev/null; then
            print_success "Branch protection enabled"
        else
            print_warning "No branch protection or unable to fetch"
        fi
    done
}

test_workflow_locally() {
    print_header "Local Workflow Testing"
    
    print_warning "To test workflows locally, use act: https://github.com/nektos/act"
    
    if command -v act &> /dev/null; then
        print_success "act is installed"
        echo ""
        echo "Test workflows locally with:"
        echo "  act -l                    # List workflows"
        echo "  act pull_request          # Run PR workflows"
        echo "  act push                  # Run push workflows"
    else
        print_warning "act is not installed"
        echo "Install: https://github.com/nektos/act#installation"
    fi
}

generate_workflow_report() {
    print_header "Generating Workflow Report"
    
    local report_file="workflow-validation-report.txt"
    
    {
        echo "GitHub Workflow Validation Report"
        echo "Generated: $(date)"
        echo "Repository: $(git remote get-url TTA 2>/dev/null || echo 'Unknown')"
        echo ""
        echo "=========================================="
        echo ""
        
        echo "Workflows Found:"
        ls -1 .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null | xargs -n1 basename
        echo ""
        
        echo "Python Version in .python-version:"
        cat .python-version 2>/dev/null || echo "Not found"
        echo ""
        
        echo "UV Lock File:"
        [ -f uv.lock ] && echo "Present ($(du -h uv.lock | cut -f1))" || echo "Missing"
        echo ""
        
        if command -v gh &> /dev/null; then
            echo "Recent Workflow Runs:"
            gh run list --limit 5
            echo ""
        fi
        
        echo "Environment Setup:"
        [ -d .venv ] && echo "✓ .venv exists" || echo "✗ .venv missing"
        [ -f pyproject.toml ] && echo "✓ pyproject.toml exists" || echo "✗ pyproject.toml missing"
        [ -f .gitignore ] && echo "✓ .gitignore exists" || echo "✗ .gitignore missing"
        echo ""
        
    } > "$report_file"
    
    print_success "Report saved to: $report_file"
    cat "$report_file"
}

show_menu() {
    echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   GitHub Workflow Validator            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"
    
    echo "1) Check workflow syntax"
    echo "2) List workflows"
    echo "3) Check recent runs"
    echo "4) Check workflow status"
    echo "5) Check required secrets"
    echo "6) Validate UV setup"
    echo "7) Check branch protection"
    echo "8) Test workflow locally (act)"
    echo "9) Generate full report"
    echo "a) Run all checks"
    echo "q) Quit"
    echo ""
    echo -n "Choose option: "
}

main() {
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -r choice
            case $choice in
                1) check_workflow_syntax ;;
                2) list_workflows ;;
                3) check_recent_runs ;;
                4) check_workflow_status ;;
                5) check_secrets ;;
                6) validate_uv_setup ;;
                7) check_branch_protection ;;
                8) test_workflow_locally ;;
                9) generate_workflow_report ;;
                a|A)
                    check_gh_cli
                    check_workflow_syntax
                    list_workflows
                    validate_uv_setup
                    check_secrets
                    check_recent_runs
                    generate_workflow_report
                    ;;
                q|Q)
                    print_success "Goodbye!"
                    exit 0
                    ;;
                *) print_error "Invalid option" ;;
            esac
            
            echo ""
            echo "Press Enter to continue..."
            read -r
        done
    else
        # Command line mode
        case "$1" in
            syntax) check_workflow_syntax ;;
            list) list_workflows ;;
            runs) check_recent_runs ;;
            status) check_workflow_status ;;
            secrets) check_secrets ;;
            uv) validate_uv_setup ;;
            branches) check_branch_protection ;;
            local) test_workflow_locally ;;
            report) generate_workflow_report ;;
            all)
                check_gh_cli
                check_workflow_syntax
                list_workflows
                validate_uv_setup
                check_secrets
                check_recent_runs
                generate_workflow_report
                ;;
            *)
                echo "Usage: $0 [command]"
                echo ""
                echo "Commands:"
                echo "  syntax    - Check workflow syntax"
                echo "  list      - List workflows"
                echo "  runs      - Check recent runs"
                echo "  status    - Check workflow status"
                echo "  secrets   - Check required secrets"
                echo "  uv        - Validate UV setup"
                echo "  branches  - Check branch protection"
                echo "  local     - Test workflow locally"
                echo "  report    - Generate report"
                echo "  all       - Run all checks"
                echo ""
                echo "Run without arguments for interactive menu"
                exit 1
                ;;
        esac
    fi
}

main "$@"
