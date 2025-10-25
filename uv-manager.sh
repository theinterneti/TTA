#!/usr/bin/env bash
# UV Environment Management Script for TTA
# This script helps manage UV virtual environments and ensures consistent setup across the team

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Functions
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

check_uv_installed() {
    if ! command -v uv &> /dev/null; then
        print_error "UV is not installed. Please install it first:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    print_success "UV is installed: $(uv --version)"
}

check_python_version() {
    local required_version="3.12"
    if [ -f .python-version ]; then
        local version=$(cat .python-version)
        print_success "Python version specified: $version"
    else
        print_warning "No .python-version file found. Creating one with $required_version"
        echo "$required_version" > .python-version
    fi
}

setup_main_environment() {
    print_header "Setting up main UV environment (.venv)"
    
    if [ -d .venv ]; then
        print_warning ".venv directory exists. Remove it? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            rm -rf .venv
            print_success "Removed existing .venv"
        else
            print_warning "Keeping existing .venv"
        fi
    fi
    
    # Sync with all extras and dev dependencies
    print_success "Running: uv sync --all-extras --dev"
    uv sync --all-extras --dev
    
    print_success "Main environment setup complete!"
    
    # Verify installation
    print_success "Installed packages count: $(uv pip list | wc -l)"
}

setup_staging_environment() {
    print_header "Setting up staging environment (venv-staging)"
    
    if [ -d venv-staging ]; then
        print_warning "venv-staging exists. This is for staging-specific testing."
        print_warning "Remove it? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            rm -rf venv-staging
            print_success "Removed existing venv-staging"
        else
            print_warning "Keeping existing venv-staging"
            return
        fi
    fi
    
    # Create staging environment
    print_success "Creating staging virtual environment"
    uv venv venv-staging
    
    # Sync dependencies for staging
    print_success "Installing dependencies in staging environment"
    VIRTUAL_ENV=venv-staging uv sync --all-extras --dev
    
    print_success "Staging environment setup complete!"
}

verify_environment() {
    print_header "Verifying UV environment"
    
    # Check if .venv exists
    if [ ! -d .venv ]; then
        print_error ".venv directory not found. Run setup first."
        return 1
    fi
    
    # Check key packages
    local packages=("pytest" "coverage" "ruff" "neo4j" "redis" "fastapi")
    for pkg in "${packages[@]}"; do
        if uv pip show "$pkg" &> /dev/null; then
            print_success "$pkg is installed"
        else
            print_warning "$pkg is NOT installed"
        fi
    done
    
    # Test pytest
    print_success "Testing pytest..."
    uv run pytest --version
    
    # Check Python version
    print_success "Python version in .venv:"
    uv run python --version
    
    print_success "Environment verification complete!"
}

show_environment_info() {
    print_header "UV Environment Information"
    
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    if [ -f .python-version ]; then
        echo "Python Version: $(cat .python-version)"
    fi
    
    if [ -f uv.lock ]; then
        echo "UV Lock File: ✓ Present"
        echo "Lock File Size: $(du -h uv.lock | cut -f1)"
    else
        print_warning "UV Lock File: ✗ Missing"
    fi
    
    echo ""
    echo "Environments:"
    
    if [ -d .venv ]; then
        print_success ".venv/ (main development environment)"
        echo "  Python: $(uv run python --version 2>&1 | grep -o 'Python [0-9.]*' || echo 'Unknown')"
        echo "  Packages: $(uv pip list 2>/dev/null | wc -l) installed"
    else
        print_warning ".venv/ NOT FOUND"
    fi
    
    if [ -d venv-staging ]; then
        print_success "venv-staging/ (staging environment)"
    else
        echo "  venv-staging/ not present (optional)"
    fi
    
    echo ""
    echo "Key Files:"
    [ -f pyproject.toml ] && print_success "pyproject.toml" || print_error "pyproject.toml missing!"
    [ -f uv.lock ] && print_success "uv.lock" || print_warning "uv.lock missing (will be created on sync)"
    [ -f .gitignore ] && print_success ".gitignore" || print_warning ".gitignore missing"
}

clean_environment() {
    print_header "Cleaning UV environment artifacts"
    
    print_warning "This will remove:"
    echo "  - .venv/"
    echo "  - venv-staging/"
    echo "  - __pycache__/"
    echo "  - *.pyc files"
    echo "  - .pytest_cache/"
    echo ""
    echo "Continue? (y/N)"
    read -r response
    
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_warning "Cancelled"
        return
    fi
    
    # Remove environments
    [ -d .venv ] && rm -rf .venv && print_success "Removed .venv/"
    [ -d venv-staging ] && rm -rf venv-staging && print_success "Removed venv-staging/"
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && print_success "Removed __pycache__/" || true
    find . -type f -name "*.pyc" -delete 2>/dev/null && print_success "Removed *.pyc files" || true
    
    # Remove pytest cache
    [ -d .pytest_cache ] && rm -rf .pytest_cache && print_success "Removed .pytest_cache/"
    
    print_success "Cleanup complete!"
}

update_dependencies() {
    print_header "Updating dependencies"
    
    print_success "Updating all dependencies to latest compatible versions"
    uv sync --upgrade
    
    print_success "Dependencies updated!"
    print_warning "Review changes to uv.lock before committing"
}

install_vscode_python() {
    print_header "Configuring VS Code Python interpreter"
    
    local python_path="$PROJECT_ROOT/.venv/bin/python"
    
    if [ ! -f "$python_path" ]; then
        print_error "Python interpreter not found at $python_path"
        print_error "Run setup first: ./uv-manager.sh setup"
        return 1
    fi
    
    # Create/update .vscode settings
    mkdir -p .vscode
    
    local settings_file=".vscode/python-interpreter.txt"
    echo "$python_path" > "$settings_file"
    print_success "Python interpreter path saved to $settings_file"
    
    print_success "In VS Code:"
    echo "  1. Press Ctrl+Shift+P"
    echo "  2. Type 'Python: Select Interpreter'"
    echo "  3. Choose: $python_path"
    echo ""
    echo "Or VS Code should auto-detect it from settings.json"
}

run_tests() {
    print_header "Running tests with UV"
    
    if [ ! -d .venv ]; then
        print_error ".venv not found. Run setup first."
        return 1
    fi
    
    print_success "Running pytest..."
    uv run pytest -v
}

# Main menu
show_menu() {
    echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   TTA UV Environment Manager          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"
    
    echo "1) Setup main environment (.venv)"
    echo "2) Setup staging environment (venv-staging)"
    echo "3) Verify environment"
    echo "4) Show environment info"
    echo "5) Update dependencies"
    echo "6) Configure VS Code interpreter"
    echo "7) Run tests"
    echo "8) Clean environment"
    echo "9) Full setup (main + verification)"
    echo "q) Quit"
    echo ""
    echo -n "Choose option: "
}

# Main script
main() {
    check_uv_installed
    check_python_version
    
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -r choice
            case $choice in
                1) setup_main_environment ;;
                2) setup_staging_environment ;;
                3) verify_environment ;;
                4) show_environment_info ;;
                5) update_dependencies ;;
                6) install_vscode_python ;;
                7) run_tests ;;
                8) clean_environment ;;
                9) 
                    setup_main_environment
                    verify_environment
                    install_vscode_python
                    print_success "Full setup complete!"
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
            setup) setup_main_environment ;;
            setup-staging) setup_staging_environment ;;
            verify) verify_environment ;;
            info) show_environment_info ;;
            update) update_dependencies ;;
            vscode) install_vscode_python ;;
            test) run_tests ;;
            clean) clean_environment ;;
            full) 
                setup_main_environment
                verify_environment
                install_vscode_python
                ;;
            *)
                echo "Usage: $0 [command]"
                echo ""
                echo "Commands:"
                echo "  setup          - Setup main environment"
                echo "  setup-staging  - Setup staging environment"
                echo "  verify         - Verify environment"
                echo "  info           - Show environment info"
                echo "  update         - Update dependencies"
                echo "  vscode         - Configure VS Code"
                echo "  test           - Run tests"
                echo "  clean          - Clean environment"
                echo "  full           - Full setup (recommended)"
                echo ""
                echo "Run without arguments for interactive menu"
                exit 1
                ;;
        esac
    fi
}

main "$@"
