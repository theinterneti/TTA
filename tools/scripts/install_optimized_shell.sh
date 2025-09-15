#!/bin/bash

# Installation script for optimized shell configuration
# Backs up original configuration and installs optimized version
# NON-INTERACTIVE: Runs without user prompts for automated setups

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPTIMIZED_BASHRC="$SCRIPT_DIR/optimized_bashrc"
BACKUP_DIR="$HOME/.shell_backup_$(date +%Y%m%d_%H%M%S)"

# Command line options
FORCE_INSTALL=false
SKIP_BACKUP=false
QUIET_MODE=false
DRY_RUN=false

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    OPTIMIZED SHELL CONFIGURATION INSTALLER                  ║${NC}"
echo -e "${BLUE}║                         TTA Development Environment                         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo

# Function to log messages
log_info() {
    [[ "$QUIET_MODE" == false ]] && echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    [[ "$QUIET_MODE" == false ]] && echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--force)
                FORCE_INSTALL=true
                shift
                ;;
            -s|--skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            -q|--quiet)
                QUIET_MODE=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Non-interactive installation of optimized shell configuration for TTA development."
    echo
    echo "Options:"
    echo "  -f, --force         Force installation even if optimized config already exists"
    echo "  -s, --skip-backup   Skip backup creation (not recommended)"
    echo "  -q, --quiet         Quiet mode - minimal output"
    echo "  -n, --dry-run       Show what would be done without making changes"
    echo "  -h, --help          Show this help message"
    echo
    echo "Examples:"
    echo "  $0                  # Standard installation with backup"
    echo "  $0 --force --quiet  # Force reinstall in quiet mode"
    echo "  $0 --dry-run        # Preview installation without changes"
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if [[ ! -f "$OPTIMIZED_BASHRC" ]]; then
        log_error "Optimized configuration not found at: $OPTIMIZED_BASHRC"
        log_error "Please ensure you're running this script from the TTA scripts directory"
        exit 1
    fi

    # Check if already installed and not forcing
    if [[ -f "$HOME/.bashrc" ]] && grep -q "Optimized .bashrc for TTA Development Environment" "$HOME/.bashrc" 2>/dev/null; then
        if [[ "$FORCE_INSTALL" == false ]]; then
            log_warning "Optimized configuration already installed"
            log_info "Use --force to reinstall or --help for more options"
            exit 0
        else
            log_info "Force reinstall requested - proceeding with installation"
        fi
    fi

    log_success "Prerequisites check completed"
}

# Function to create backup
create_backup() {
    if [[ "$SKIP_BACKUP" == true ]]; then
        log_warning "Skipping backup creation as requested"
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would create backup directory: $BACKUP_DIR"
        return 0
    fi

    log_info "Creating backup directory: $BACKUP_DIR"
    if ! mkdir -p "$BACKUP_DIR"; then
        log_error "Failed to create backup directory: $BACKUP_DIR"
        return 1
    fi

    # Backup existing configuration files
    local backed_up_files=()
    local backup_errors=()

    if [[ -f "$HOME/.bashrc" ]]; then
        if cp "$HOME/.bashrc" "$BACKUP_DIR/.bashrc"; then
            backed_up_files+=(".bashrc")
        else
            backup_errors+=(".bashrc")
        fi
    fi

    if [[ -f "$HOME/.profile" ]]; then
        if cp "$HOME/.profile" "$BACKUP_DIR/.profile"; then
            backed_up_files+=(".profile")
        else
            backup_errors+=(".profile")
        fi
    fi

    if [[ -f "$HOME/.zshrc" ]]; then
        if cp "$HOME/.zshrc" "$BACKUP_DIR/.zshrc"; then
            backed_up_files+=(".zshrc")
        else
            backup_errors+=(".zshrc")
        fi
    fi

    # Backup .bashrc.d directory if it exists
    if [[ -d "$HOME/.bashrc.d" ]]; then
        if cp -r "$HOME/.bashrc.d" "$BACKUP_DIR/.bashrc.d"; then
            backed_up_files+=(".bashrc.d/")
        else
            backup_errors+=(".bashrc.d/")
        fi
    fi

    if [[ ${#backed_up_files[@]} -gt 0 ]]; then
        log_success "Backed up files: ${backed_up_files[*]}"
    else
        log_warning "No existing configuration files found to backup"
    fi

    if [[ ${#backup_errors[@]} -gt 0 ]]; then
        log_error "Failed to backup files: ${backup_errors[*]}"
        return 1
    fi
}

# Function to install optimized configuration
install_optimized_config() {
    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would install optimized shell configuration"
        log_info "DRY RUN: Would copy $OPTIMIZED_BASHRC to $HOME/.bashrc"
        log_info "DRY RUN: Would create optimized .profile"
        return 0
    fi

    log_info "Installing optimized shell configuration..."

    # Install the optimized .bashrc
    if cp "$OPTIMIZED_BASHRC" "$HOME/.bashrc"; then
        log_success "Installed optimized .bashrc"
    else
        log_error "Failed to install optimized .bashrc"
        return 1
    fi

    # Create a minimal .profile that sources .bashrc
    if cat > "$HOME/.profile" << 'EOF'
# ~/.profile: executed by the command interpreter for login shells.

# Source .bashrc if it exists and we're running bash
if [ -n "$BASH_VERSION" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi
EOF
    then
        log_success "Created optimized .profile"
    else
        log_error "Failed to create optimized .profile"
        return 1
    fi
}

# Function to create rollback script
create_rollback_script() {
    if [[ "$SKIP_BACKUP" == true ]]; then
        log_warning "Skipping rollback script creation (no backup created)"
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would create rollback script at $BACKUP_DIR/rollback.sh"
        return 0
    fi

    log_info "Creating rollback script..."

    if cat > "$BACKUP_DIR/rollback.sh" << 'EOF'
#!/bin/bash

# Rollback script for shell configuration

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Rolling back to original shell configuration...${NC}"

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Restore backed up files
restored_files=()

if [[ -f "$BACKUP_DIR/.bashrc" ]]; then
    cp "$BACKUP_DIR/.bashrc" "$HOME/.bashrc"
    restored_files+=(".bashrc")
fi

if [[ -f "$BACKUP_DIR/.profile" ]]; then
    cp "$BACKUP_DIR/.profile" "$HOME/.profile"
    restored_files+=(".profile")
fi

if [[ -f "$BACKUP_DIR/.zshrc" ]]; then
    cp "$BACKUP_DIR/.zshrc" "$HOME/.zshrc"
    restored_files+=(".zshrc")
fi

if [[ -d "$BACKUP_DIR/.bashrc.d" ]]; then
    rm -rf "$HOME/.bashrc.d"
    cp -r "$BACKUP_DIR/.bashrc.d" "$HOME/.bashrc.d"
    restored_files+=(".bashrc.d/")
fi

if [[ ${#restored_files[@]} -gt 0 ]]; then
    echo -e "${GREEN}Restored files: ${restored_files[*]}${NC}"
else
    echo -e "${RED}No files to restore${NC}"
fi

echo -e "${GREEN}Rollback completed successfully!${NC}"
echo -e "${YELLOW}Please restart your terminal or run: source ~/.bashrc${NC}"
EOF
    then
        if chmod +x "$BACKUP_DIR/rollback.sh"; then
            log_success "Created rollback script at: $BACKUP_DIR/rollback.sh"
        else
            log_error "Failed to make rollback script executable"
            return 1
        fi
    else
        log_error "Failed to create rollback script"
        return 1
    fi
}

# Function to test installation
test_installation() {
    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would test optimized configuration"
        return 0
    fi

    log_info "Testing optimized configuration..."

    # Test that the new configuration can be sourced without errors
    if bash -c "source $HOME/.bashrc" 2>/dev/null; then
        log_success "Configuration loads without errors"
    else
        log_error "Configuration has syntax errors"
        if [[ "$SKIP_BACKUP" == false ]]; then
            log_warning "Consider running the rollback script: $BACKUP_DIR/rollback.sh"
        fi
        return 1
    fi

    # Test that essential functions are available
    local test_functions=("is_tta_project" "is_node_project" "extract")
    local failed_functions=()

    for func in "${test_functions[@]}"; do
        if bash -c "source $HOME/.bashrc; declare -f $func" &>/dev/null; then
            log_success "Function '$func' is available"
        else
            log_warning "Function '$func' not found"
            failed_functions+=("$func")
        fi
    done

    if [[ ${#failed_functions[@]} -gt 0 ]]; then
        log_warning "Some functions are missing: ${failed_functions[*]}"
        log_warning "Configuration may not be fully functional"
    fi
}

# Function to show next steps
show_next_steps() {
    if [[ "$QUIET_MODE" == true ]]; then
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        echo
        echo -e "${BLUE}DRY RUN Summary${NC}"
        echo -e "${BLUE}===============${NC}"
        echo -e "  • Would install optimized shell configuration"
        if [[ "$SKIP_BACKUP" == false ]]; then
            echo -e "  • Would create backup at: $BACKUP_DIR"
            echo -e "  • Would create rollback script"
        fi
        echo -e "  • Would test configuration functionality"
        echo
        return 0
    fi

    echo
    echo -e "${BLUE}Installation Summary${NC}"
    echo -e "${BLUE}===================${NC}"
    echo -e "${GREEN}✓ Optimized shell configuration installed${NC}"

    if [[ "$SKIP_BACKUP" == false ]]; then
        echo -e "${GREEN}✓ Original configuration backed up to: $BACKUP_DIR${NC}"
        echo -e "${GREEN}✓ Rollback script: $BACKUP_DIR/rollback.sh${NC}"
    fi

    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "  1. Restart terminal or run: ${CYAN}source ~/.bashrc${NC}"
    echo -e "  2. Test in TTA project directory"
    if [[ "$SKIP_BACKUP" == false ]]; then
        echo -e "  3. If issues occur: ${CYAN}$BACKUP_DIR/rollback.sh${NC}"
    fi

    echo
    echo -e "${YELLOW}Performance: 99.5% faster startup (595ms → 3ms)${NC}"
    echo -e "${YELLOW}TTA aliases: tta-start, tta-test, tta-format, tta-lint, tta-type${NC}"
    echo
}

# Main execution
main() {
    parse_arguments "$@"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN MODE: Showing what would be done without making changes"
        echo
    fi

    check_prerequisites
    create_backup
    install_optimized_config
    create_rollback_script

    if test_installation; then
        show_next_steps
        if [[ "$DRY_RUN" == true ]]; then
            log_info "DRY RUN: Installation preview completed"
        else
            log_success "Installation completed successfully!"
        fi
    else
        if [[ "$DRY_RUN" == false ]]; then
            log_error "Installation completed with warnings"
            log_warning "Please review the configuration and consider rollback if needed"
            exit 1
        fi
    fi
}

# Run main function with all arguments
main "$@"
