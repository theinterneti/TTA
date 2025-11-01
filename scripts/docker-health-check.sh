#!/bin/bash

# Docker Health Check and Diagnostic Script
# Comprehensive system health analysis for Docker build failures

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to check command availability
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to run command with error handling
safe_run() {
    local cmd="$1"
    local description="$2"

    print_info "Checking: $description"
    if eval "$cmd" >/dev/null 2>&1; then
        print_status "$description - OK"
        return 0
    else
        print_error "$description - FAILED"
        return 1
    fi
}

# Main diagnostic function
run_diagnostics() {
    print_header "🔍 Docker Health Check and Diagnostic Report"
    echo "Generated: $(date)"
    echo "System: $(uname -a)"
    echo ""

    # 1. System Resources Check
    print_header "📊 System Resources"
    echo "Memory Usage:"
    free -h
    echo ""
    echo "Disk Usage:"
    df -h | grep -E "(Filesystem|/dev/|C:|tmpfs)" | head -10
    echo ""

    # 2. Docker Installation Check
    print_header "🐳 Docker Installation Status"

    if check_command docker; then
        print_status "Docker command available"

        # Check Docker version
        echo "Docker Version:"
        docker version 2>&1 || print_error "Docker version check failed"
        echo ""

        # Check Docker info
        echo "Docker System Info:"
        if docker info >/dev/null 2>&1; then
            print_status "Docker daemon responding"
            docker info | grep -E "(Server Version|Total Memory|CPUs|Storage Driver|Operating System)"
        else
            print_error "Docker daemon not responding"
            docker info 2>&1 | head -10
        fi
        echo ""

    else
        print_error "Docker command not found"
    fi

    # 3. Docker Plugin Health
    print_header "🔌 Docker Plugin Status"

    local plugins_dir="/usr/local/lib/docker/cli-plugins"
    if [ -d "$plugins_dir" ]; then
        echo "Checking Docker plugins for SIGBUS errors:"
        for plugin in "$plugins_dir"/*; do
            if [ -f "$plugin" ]; then
                plugin_name=$(basename "$plugin")
                if "$plugin" --help >/dev/null 2>&1; then
                    print_status "$plugin_name - OK"
                else
                    print_error "$plugin_name - FAILED (possible SIGBUS)"
                fi
            fi
        done
    else
        print_warning "Docker plugins directory not found"
    fi
    echo ""

    # 4. WSL2 Integration Check
    print_header "🐧 WSL2 Integration"

    if check_command wsl; then
        echo "WSL Distributions:"
        wsl --list --verbose 2>/dev/null || echo "WSL command failed"
        echo ""

        echo "WSL Status:"
        wsl --status 2>/dev/null || echo "WSL status unavailable"
        echo ""
    else
        print_warning "WSL command not available in this environment"
    fi

    # 5. Build Environment Check
    print_header "🏗️ Build Environment"

    # Check Python
    if check_command python3; then
        print_status "Python available: $(python3 --version)"
    else
        print_warning "Python not available"
    fi

    # Check build files
    if [ -f "pyproject.toml" ]; then
        print_status "pyproject.toml found ($(wc -l < pyproject.toml) lines)"
    else
        print_warning "pyproject.toml not found"
    fi

    if [ -f "uv.lock" ]; then
        local lock_size=$(wc -l < uv.lock)
        print_status "uv.lock found ($lock_size lines)"
        if [ "$lock_size" -gt 5000 ]; then
            print_warning "Large uv.lock file may cause memory pressure during build"
        fi
    else
        print_warning "uv.lock not found"
    fi
    echo ""

    # 6. Docker Build Test
    print_header "🧪 Docker Build Test"

    echo "Testing basic Docker functionality:"
    if docker run --rm hello-world >/dev/null 2>&1; then
        print_status "Basic Docker run test - OK"
    else
        print_error "Basic Docker run test - FAILED"
    fi

    echo "Testing Python base image:"
    if docker run --rm python:3.11-slim python --version >/dev/null 2>&1; then
        print_status "Python base image test - OK"
    else
        print_error "Python base image test - FAILED"
    fi

    echo "Testing UV installation:"
    if timeout 60 docker run --rm python:3.11-slim pip install uv==0.4.18 >/dev/null 2>&1; then
        print_status "UV installation test - OK"
    else
        print_error "UV installation test - FAILED or TIMEOUT"
    fi
    echo ""

    # 7. System Health Indicators
    print_header "🏥 System Health Indicators"

    # Check for recent errors in system logs
    echo "Recent system errors:"
    if check_command dmesg; then
        local error_count=$(dmesg | grep -i -E "(error|fault|kill|oom)" | tail -10 | wc -l)
        if [ "$error_count" -gt 0 ]; then
            print_warning "$error_count recent system errors found"
            dmesg | grep -i -E "(error|fault|kill|oom)" | tail -5
        else
            print_status "No recent critical system errors"
        fi
    else
        print_warning "Cannot access system logs"
    fi
    echo ""

    # Check disk space warnings
    echo "Disk space warnings:"
    local disk_warnings=$(df -h | awk '$5 ~ /^[89][0-9]%|^100%/ {print $0}' | wc -l)
    if [ "$disk_warnings" -gt 0 ]; then
        print_warning "$disk_warnings filesystems with >80% usage"
        df -h | awk '$5 ~ /^[89][0-9]%|^100%/ {print $0}'
    else
        print_status "Disk space levels acceptable"
    fi
    echo ""

    # 8. Recommendations
    print_header "💡 Recommendations"

    # Critical issues
    local critical_issues=0

    if ! docker info >/dev/null 2>&1; then
        print_error "CRITICAL: Docker daemon not responding - restart Docker Desktop"
        ((critical_issues++))
    fi

    if df -h | grep -q "100%.*C:"; then
        print_error "CRITICAL: C: drive full - free up disk space immediately"
        ((critical_issues++))
    fi

    if docker info 2>&1 | grep -q "bus error"; then
        print_error "CRITICAL: Docker plugins corrupted - reinstall Docker Desktop"
        ((critical_issues++))
    fi

    # Warnings
    local warnings=0

    if [ -f "uv.lock" ] && [ "$(wc -l < uv.lock)" -gt 5000 ]; then
        print_warning "Large dependency file may cause build issues - consider optimization"
        ((warnings++))
    fi

    if df -h | awk '$5 ~ /^[89][0-9]%/ {print $0}' | grep -q .; then
        print_warning "High disk usage detected - monitor space closely"
        ((warnings++))
    fi

    # Summary
    echo ""
    print_header "📋 Summary"
    if [ "$critical_issues" -eq 0 ]; then
        if [ "$warnings" -eq 0 ]; then
            print_status "System appears healthy for Docker builds"
        else
            print_warning "$warnings warning(s) detected - monitor closely"
        fi
    else
        print_error "$critical_issues critical issue(s) require immediate attention"
        echo ""
        echo "Next steps:"
        echo "1. Address critical issues above"
        echo "2. Restart Docker Desktop"
        echo "3. Re-run this diagnostic"
        echo "4. If issues persist, see DOCKER_BUILD_FAILURE_ANALYSIS.md"
    fi

    echo ""
    print_info "For detailed analysis, see: DOCKER_BUILD_FAILURE_ANALYSIS.md"
    print_info "For build optimization, see: DEVELOPMENT_SETUP.md"
}

# Main execution
main() {
    case "${1:-check}" in
        "check"|"diagnostic"|"health")
            run_diagnostics
            ;;
        "help"|"-h"|"--help")
            echo "Docker Health Check Script"
            echo ""
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  check       Run full diagnostic (default)"
            echo "  diagnostic  Same as check"
            echo "  health      Same as check"
            echo "  help        Show this help"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
