#!/bin/bash

# TTA Development Environment Setup Script
# This script sets up a complete development environment for the TTA project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check if running on supported OS
check_os() {
    log_info "Checking operating system..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_success "Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_success "macOS detected"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check if required tools are installed
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check for Python 3.11+
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python $PYTHON_VERSION found"
    else
        log_error "Python 3.11+ is required but not found"
        exit 1
    fi

    # Check for Git
    if command -v git &> /dev/null; then
        log_success "Git found"
    else
        log_error "Git is required but not found"
        exit 1
    fi

    # Check for curl
    if command -v curl &> /dev/null; then
        log_success "curl found"
    else
        log_error "curl is required but not found"
        exit 1
    fi
}

# Install uv if not present
install_uv() {
    if command -v uv &> /dev/null; then
        log_success "uv is already installed"
        uv --version
    else
        log_info "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
        log_success "uv installed successfully"
    fi
}

# Setup Python virtual environment
setup_virtual_environment() {
    log_info "Setting up Python virtual environment..."

    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        log_info "Creating virtual environment..."
        uv venv
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi

    # Install dependencies
    log_info "Installing dependencies..."
    uv sync --dev
    log_success "Dependencies installed"
}

# Setup pre-commit hooks
setup_pre_commit() {
    log_info "Setting up pre-commit hooks..."

    # Install pre-commit hooks
    uv run pre-commit install
    uv run pre-commit install --hook-type commit-msg

    log_success "Pre-commit hooks installed"

    # Run pre-commit on all files (optional, can be skipped for large repos)
    read -p "Run pre-commit on all files? This may take a while (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Running pre-commit on all files..."
        uv run pre-commit run --all-files || log_warning "Some pre-commit checks failed - this is normal for initial setup"
    fi
}

# Setup IDE configuration
setup_ide() {
    log_info "IDE configuration files are already in place:"
    log_success "  - .vscode/ directory with VS Code settings"
    log_success "  - .editorconfig for consistent formatting"

    if command -v code &> /dev/null; then
        log_info "VS Code detected. You can open the project with: code ."
        log_info "Recommended extensions are listed in .vscode/extensions.json"
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    # Test uv environment
    if uv run python --version &> /dev/null; then
        log_success "Python environment is working"
    else
        log_error "Python environment setup failed"
        exit 1
    fi

    # Test pytest
    if uv run pytest --version &> /dev/null; then
        log_success "pytest is working"
    else
        log_error "pytest setup failed"
        exit 1
    fi

    # Test pre-commit
    if uv run pre-commit --version &> /dev/null; then
        log_success "pre-commit is working"
    else
        log_error "pre-commit setup failed"
        exit 1
    fi

    # Test linting tools
    if uv run black --version &> /dev/null && uv run ruff --version &> /dev/null; then
        log_success "Code formatting tools are working"
    else
        log_error "Code formatting tools setup failed"
        exit 1
    fi
}

# Display next steps
show_next_steps() {
    log_success "Development environment setup complete!"
    echo
    log_info "Next steps:"
    echo "  1. Activate the virtual environment: source .venv/bin/activate"
    echo "  2. Run tests: uv run pytest tests/"
    echo "  3. Start the main application: uv run python src/main.py"
    echo "  4. Start the Player Experience API: uv run python src/player_experience/api/main.py"
    echo "  5. Open in VS Code: code ."
    echo
    log_info "Available commands:"
    echo "  - uv run pytest tests/                    # Run all tests"
    echo "  - uv run pytest tests/ --neo4j           # Run Neo4j integration tests"
    echo "  - uv run pytest tests/ --redis           # Run Redis integration tests"
    echo "  - uv run black src/ tests/               # Format code"
    echo "  - uv run ruff check src/ tests/          # Lint code"
    echo "  - uv run mypy src/                       # Type check"
    echo "  - uv run pre-commit run --all-files      # Run all quality checks"
    echo
    log_info "Documentation:"
    echo "  - Development setup: docs/development/BASELINE_ASSESSMENT.md"
    echo "  - Project structure: README.md"
    echo "  - API documentation: Available when services are running"
}

# Main execution
main() {
    echo "=========================================="
    echo "TTA Development Environment Setup"
    echo "=========================================="
    echo

    check_os
    check_prerequisites
    install_uv
    setup_virtual_environment
    setup_pre_commit
    setup_ide
    verify_installation
    show_next_steps

    log_success "Setup completed successfully!"
}

# Run main function
main "$@"
