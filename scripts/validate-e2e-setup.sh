#!/bin/bash

# TTA E2E Setup Validation Script
# Validates that all components needed for E2E testing are properly configured

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  TTA E2E Setup Validation${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_file_exists() {
    local file_path="$1"
    local description="$2"

    if [ -f "$file_path" ]; then
        print_success "$description exists: $file_path"
        return 0
    else
        print_error "$description missing: $file_path"
        return 1
    fi
}

check_directory_exists() {
    local dir_path="$1"
    local description="$2"

    if [ -d "$dir_path" ]; then
        print_success "$description exists: $dir_path"
        return 0
    else
        print_error "$description missing: $dir_path"
        return 1
    fi
}

check_command_exists() {
    local command="$1"
    local description="$2"

    if command -v "$command" &> /dev/null; then
        local version=$($command --version 2>/dev/null | head -n1 || echo "unknown")
        print_success "$description available: $version"
        return 0
    else
        print_error "$description not found: $command"
        return 1
    fi
}

validate_prerequisites() {
    print_info "Validating prerequisites..."
    local errors=0

    # Check Node.js
    if ! check_command_exists "node" "Node.js"; then
        ((errors++))
    fi

    # Check npm
    if ! check_command_exists "npm" "npm"; then
        ((errors++))
    fi

    # Check curl
    if ! check_command_exists "curl" "curl"; then
        ((errors++))
    fi

    return $errors
}

validate_project_structure() {
    print_info "Validating project structure..."
    local errors=0

    # Check main directories
    if ! check_directory_exists "$PROJECT_ROOT/src/player_experience/frontend" "Frontend directory"; then
        ((errors++))
    fi

    if ! check_directory_exists "$PROJECT_ROOT/tests/e2e" "E2E tests directory"; then
        ((errors++))
    fi

    if ! check_directory_exists "$PROJECT_ROOT/tests/e2e/specs" "Test specs directory"; then
        ((errors++))
    fi

    if ! check_directory_exists "$PROJECT_ROOT/tests/e2e/page-objects" "Page objects directory"; then
        ((errors++))
    fi

    if ! check_directory_exists "$PROJECT_ROOT/tests/e2e/mocks" "Mock server directory"; then
        ((errors++))
    fi

    return $errors
}

validate_configuration_files() {
    print_info "Validating configuration files..."
    local errors=0

    # Check main config files
    if ! check_file_exists "$PROJECT_ROOT/package.json" "Root package.json"; then
        ((errors++))
    fi

    if ! check_file_exists "$PROJECT_ROOT/playwright.config.ts" "Playwright config"; then
        ((errors++))
    fi

    if ! check_file_exists "$PROJECT_ROOT/.env.test" "Test environment config"; then
        ((errors++))
    fi

    # Check frontend files
    if ! check_file_exists "$PROJECT_ROOT/src/player_experience/frontend/package.json" "Frontend package.json"; then
        ((errors++))
    fi

    # Check mock server files
    if ! check_file_exists "$PROJECT_ROOT/tests/e2e/mocks/package.json" "Mock server package.json"; then
        ((errors++))
    fi

    if ! check_file_exists "$PROJECT_ROOT/tests/e2e/mocks/api-server.js" "Mock API server"; then
        ((errors++))
    fi

    # Check GitHub Actions workflow
    if ! check_file_exists "$PROJECT_ROOT/.github/workflows/e2e-tests.yml" "GitHub Actions workflow"; then
        ((errors++))
    fi

    return $errors
}

validate_test_files() {
    print_info "Validating test files..."
    local errors=0

    # Check test specs
    local test_specs=(
        "auth.spec.ts"
        "dashboard.spec.ts"
        "character-management.spec.ts"
        "chat.spec.ts"
        "settings.spec.ts"
        "accessibility.spec.ts"
        "responsive.spec.ts"
    )

    for spec in "${test_specs[@]}"; do
        if ! check_file_exists "$PROJECT_ROOT/tests/e2e/specs/$spec" "Test spec: $spec"; then
            ((errors++))
        fi
    done

    # Check page objects
    local page_objects=(
        "BasePage.ts"
        "LoginPage.ts"
        "DashboardPage.ts"
        "CharacterManagementPage.ts"
        "ChatPage.ts"
        "SettingsPage.ts"
    )

    for page_object in "${page_objects[@]}"; do
        if ! check_file_exists "$PROJECT_ROOT/tests/e2e/page-objects/$page_object" "Page object: $page_object"; then
            ((errors++))
        fi
    done

    # Check fixtures and utilities
    if ! check_file_exists "$PROJECT_ROOT/tests/e2e/fixtures/test-data.ts" "Test data fixtures"; then
        ((errors++))
    fi

    if ! check_file_exists "$PROJECT_ROOT/tests/e2e/utils/test-helpers.ts" "Test utilities"; then
        ((errors++))
    fi

    return $errors
}

validate_scripts() {
    print_info "Validating scripts..."
    local errors=0

    # Check scripts
    if ! check_file_exists "$PROJECT_ROOT/scripts/run-e2e-tests.sh" "E2E test runner script"; then
        ((errors++))
    fi

    if ! check_file_exists "$PROJECT_ROOT/scripts/start-test-environment.sh" "Test environment script"; then
        ((errors++))
    fi

    # Check script permissions
    if [ -f "$PROJECT_ROOT/scripts/run-e2e-tests.sh" ]; then
        if [ -x "$PROJECT_ROOT/scripts/run-e2e-tests.sh" ]; then
            print_success "E2E test runner script is executable"
        else
            print_warning "E2E test runner script is not executable (run: chmod +x scripts/run-e2e-tests.sh)"
        fi
    fi

    if [ -f "$PROJECT_ROOT/scripts/start-test-environment.sh" ]; then
        if [ -x "$PROJECT_ROOT/scripts/start-test-environment.sh" ]; then
            print_success "Test environment script is executable"
        else
            print_warning "Test environment script is not executable (run: chmod +x scripts/start-test-environment.sh)"
        fi
    fi

    return $errors
}

validate_dependencies() {
    print_info "Validating dependencies..."
    local errors=0

    cd "$PROJECT_ROOT"

    # Check if root dependencies are installed
    if [ -d "node_modules" ]; then
        print_success "Root node_modules exists"

        # Check for key dependencies
        if [ -d "node_modules/@playwright" ]; then
            print_success "Playwright is installed"
        else
            print_warning "Playwright not found in node_modules (run: npm install)"
        fi
    else
        print_warning "Root node_modules missing (run: npm install)"
    fi

    # Check frontend dependencies
    if [ -d "src/player_experience/frontend/node_modules" ]; then
        print_success "Frontend node_modules exists"
    else
        print_warning "Frontend node_modules missing (run: cd src/player_experience/frontend && npm install)"
    fi

    # Check mock server dependencies
    if [ -d "tests/e2e/mocks/node_modules" ]; then
        print_success "Mock server node_modules exists"
    else
        print_warning "Mock server node_modules missing (run: cd tests/e2e/mocks && npm install)"
    fi

    return $errors
}

test_mock_server() {
    print_info "Testing mock server functionality..."

    cd "$PROJECT_ROOT/tests/e2e/mocks"

    # Start mock server in background
    npm start &
    MOCK_PID=$!

    # Wait for server to start
    sleep 3

    # Test health endpoint
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Mock server health check passed"

        # Test API endpoints
        if curl -s http://localhost:8000/auth/login -X POST -H "Content-Type: application/json" -d '{"username":"test","password":"test"}' > /dev/null; then
            print_success "Mock API endpoints responding"
        else
            print_warning "Mock API endpoints not responding properly"
        fi
    else
        print_error "Mock server health check failed"
    fi

    # Cleanup
    kill $MOCK_PID 2>/dev/null || true
    wait $MOCK_PID 2>/dev/null || true
}

generate_summary() {
    local total_errors=$1

    echo ""
    print_info "Validation Summary:"
    echo ""

    if [ $total_errors -eq 0 ]; then
        print_success "All validations passed! E2E testing setup is ready."
        echo ""
        print_info "Next steps:"
        echo "  1. Install dependencies: npm install"
        echo "  2. Install Playwright browsers: npm run test:e2e:install"
        echo "  3. Start test environment: npm run test:env:start"
        echo "  4. Run tests: npm run test:e2e"
        echo ""
        return 0
    else
        print_error "Found $total_errors validation errors. Please fix the issues above."
        echo ""
        print_info "Common fixes:"
        echo "  - Install dependencies: npm install"
        echo "  - Install frontend deps: cd src/player_experience/frontend && npm install"
        echo "  - Install mock server deps: cd tests/e2e/mocks && npm install"
        echo "  - Make scripts executable: chmod +x scripts/*.sh"
        echo ""
        return 1
    fi
}

# Main validation
main() {
    print_header

    local total_errors=0

    validate_prerequisites
    ((total_errors += $?))

    validate_project_structure
    ((total_errors += $?))

    validate_configuration_files
    ((total_errors += $?))

    validate_test_files
    ((total_errors += $?))

    validate_scripts
    ((total_errors += $?))

    validate_dependencies
    ((total_errors += $?))

    # Only test mock server if basic validation passes
    if [ $total_errors -eq 0 ]; then
        test_mock_server
    fi

    generate_summary $total_errors
    exit $total_errors
}

# Run main function
main "$@"
