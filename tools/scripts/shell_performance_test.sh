#!/bin/bash

# Shell Performance Testing Script
# Tests and compares shell startup performance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ITERATIONS=5
ORIGINAL_BASHRC="$HOME/.bashrc"
OPTIMIZED_BASHRC="$(dirname "$0")/optimized_bashrc"
TEMP_BASHRC="/tmp/test_bashrc"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                        SHELL PERFORMANCE TESTING                            ║${NC}"
echo -e "${BLUE}║                     TTA Development Environment                             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo

# Function to measure shell startup time
measure_startup_time() {
    local config_file="$1"
    local description="$2"
    local total_time=0
    local times=()
    
    echo -e "${CYAN}Testing: $description${NC}"
    
    for i in $(seq 1 $ITERATIONS); do
        # Measure time to source the configuration and exit
        local time_output=$(TIMEFORMAT='%3R'; time (bash --rcfile "$config_file" -c 'exit' 2>/dev/null) 2>&1)
        local time_value=$(echo "$time_output" | grep -o '[0-9]*\.[0-9]*' | head -1)
        
        if [[ -n "$time_value" ]]; then
            times+=("$time_value")
            total_time=$(echo "$total_time + $time_value" | bc -l)
            echo -e "  Run $i: ${time_value}s"
        else
            echo -e "  Run $i: ${RED}Failed to measure${NC}"
        fi
    done
    
    if [[ ${#times[@]} -gt 0 ]]; then
        local avg_time=$(echo "scale=3; $total_time / ${#times[@]}" | bc -l)
        echo -e "  ${GREEN}Average: ${avg_time}s${NC}"
        echo "$avg_time"
    else
        echo -e "  ${RED}No valid measurements${NC}"
        echo "0"
    fi
    echo
}

# Function to test individual tool loading times
test_tool_loading() {
    local config_file="$1"
    local tool_name="$2"
    local test_command="$3"
    
    echo -e "${YELLOW}Testing $tool_name loading time:${NC}"
    
    local time_output=$(TIMEFORMAT='%3R'; time (bash --rcfile "$config_file" -c "$test_command" 2>/dev/null) 2>&1)
    local time_value=$(echo "$time_output" | grep -o '[0-9]*\.[0-9]*' | head -1)
    
    if [[ -n "$time_value" ]]; then
        echo -e "  ${GREEN}$tool_name: ${time_value}s${NC}"
    else
        echo -e "  ${RED}$tool_name: Failed to measure${NC}"
    fi
}

# Function to check if required tools are available
check_dependencies() {
    echo -e "${CYAN}Checking dependencies...${NC}"
    
    local missing_tools=()
    
    if ! command -v bc &> /dev/null; then
        missing_tools+=("bc")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        echo -e "${RED}Missing required tools: ${missing_tools[*]}${NC}"
        echo -e "${YELLOW}Install with: sudo apt-get install ${missing_tools[*]}${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}All dependencies available${NC}"
    echo
}

# Function to create minimal test configuration
create_minimal_config() {
    cat > "$TEMP_BASHRC" << 'EOF'
# Minimal configuration for baseline testing
export PATH="$HOME/.local/bin:$PATH"
EOF
}

# Function to analyze current configuration
analyze_current_config() {
    echo -e "${PURPLE}Analyzing current shell configuration...${NC}"
    
    if [[ -f "$ORIGINAL_BASHRC" ]]; then
        local line_count=$(wc -l < "$ORIGINAL_BASHRC")
        echo -e "  Configuration file: $ORIGINAL_BASHRC"
        echo -e "  Lines of code: $line_count"
        
        # Check for expensive operations
        echo -e "\n${YELLOW}Potentially expensive operations found:${NC}"
        
        if grep -q "eval.*pyenv" "$ORIGINAL_BASHRC"; then
            echo -e "  ${RED}✗${NC} pyenv initialization"
        fi
        
        if grep -q "nvm.sh" "$ORIGINAL_BASHRC"; then
            echo -e "  ${RED}✗${NC} NVM loading"
        fi
        
        if grep -q "register-python-argcomplete" "$ORIGINAL_BASHRC"; then
            echo -e "  ${RED}✗${NC} pipx argcomplete"
        fi
        
        if grep -q "code.*shell-integration" "$ORIGINAL_BASHRC"; then
            echo -e "  ${RED}✗${NC} VS Code integration"
        fi
        
        echo
    else
        echo -e "${YELLOW}No .bashrc found at $ORIGINAL_BASHRC${NC}"
        echo
    fi
}

# Function to test optimized configuration features
test_optimized_features() {
    echo -e "${PURPLE}Testing optimized configuration features...${NC}"
    
    # Test lazy loading detection
    echo -e "${CYAN}Testing lazy loading functions:${NC}"
    
    # Test TTA project detection
    local tta_test=$(bash --rcfile "$OPTIMIZED_BASHRC" -c 'is_tta_project && echo "detected" || echo "not detected"' 2>/dev/null)
    echo -e "  TTA project detection: $tta_test"
    
    # Test Node.js project detection
    local node_test=$(bash --rcfile "$OPTIMIZED_BASHRC" -c 'is_node_project && echo "detected" || echo "not detected"' 2>/dev/null)
    echo -e "  Node.js project detection: $node_test"
    
    # Test alias availability
    echo -e "\n${CYAN}Testing TTA-specific aliases:${NC}"
    local aliases=("tta-start" "tta-test" "tta-format" "tta-lint")
    
    for alias_name in "${aliases[@]}"; do
        local alias_test=$(bash --rcfile "$OPTIMIZED_BASHRC" -c "type $alias_name &>/dev/null && echo 'available' || echo 'missing'" 2>/dev/null)
        if [[ "$alias_test" == "available" ]]; then
            echo -e "  ${GREEN}✓${NC} $alias_name"
        else
            echo -e "  ${RED}✗${NC} $alias_name"
        fi
    done
    
    echo
}

# Main execution
main() {
    check_dependencies
    analyze_current_config
    
    # Create minimal baseline configuration
    create_minimal_config
    
    echo -e "${BLUE}Performance Comparison${NC}"
    echo -e "${BLUE}=====================${NC}"
    echo
    
    # Test minimal configuration (baseline)
    local minimal_time=$(measure_startup_time "$TEMP_BASHRC" "Minimal Configuration (baseline)")
    
    # Test original configuration
    local original_time=0
    if [[ -f "$ORIGINAL_BASHRC" ]]; then
        original_time=$(measure_startup_time "$ORIGINAL_BASHRC" "Original Configuration")
    else
        echo -e "${YELLOW}Skipping original configuration test (file not found)${NC}"
        echo
    fi
    
    # Test optimized configuration
    local optimized_time=0
    if [[ -f "$OPTIMIZED_BASHRC" ]]; then
        optimized_time=$(measure_startup_time "$OPTIMIZED_BASHRC" "Optimized Configuration")
        test_optimized_features
    else
        echo -e "${RED}Optimized configuration not found at: $OPTIMIZED_BASHRC${NC}"
        echo
    fi
    
    # Calculate improvements
    echo -e "${BLUE}Performance Summary${NC}"
    echo -e "${BLUE}==================${NC}"
    echo
    
    if [[ $(echo "$original_time > 0" | bc -l) -eq 1 && $(echo "$optimized_time > 0" | bc -l) -eq 1 ]]; then
        local improvement=$(echo "scale=1; ($original_time - $optimized_time) / $original_time * 100" | bc -l)
        local speedup=$(echo "scale=2; $original_time / $optimized_time" | bc -l)
        
        echo -e "  Minimal baseline:     ${minimal_time}s"
        echo -e "  Original config:      ${original_time}s"
        echo -e "  Optimized config:     ${optimized_time}s"
        echo
        echo -e "  ${GREEN}Performance improvement: ${improvement}%${NC}"
        echo -e "  ${GREEN}Speedup factor: ${speedup}x${NC}"
        
        if [[ $(echo "$improvement > 50" | bc -l) -eq 1 ]]; then
            echo -e "  ${GREEN}✓ Significant improvement achieved!${NC}"
        elif [[ $(echo "$improvement > 20" | bc -l) -eq 1 ]]; then
            echo -e "  ${YELLOW}✓ Moderate improvement achieved${NC}"
        else
            echo -e "  ${RED}✗ Limited improvement${NC}"
        fi
    else
        echo -e "  ${YELLOW}Unable to calculate improvement (missing measurements)${NC}"
    fi
    
    echo
    
    # Individual tool testing (if original config exists)
    if [[ -f "$ORIGINAL_BASHRC" ]]; then
        echo -e "${BLUE}Individual Tool Loading Times${NC}"
        echo -e "${BLUE}=============================${NC}"
        echo
        
        test_tool_loading "$ORIGINAL_BASHRC" "pyenv" 'eval "$(pyenv init - bash)"'
        test_tool_loading "$ORIGINAL_BASHRC" "NVM" '. "$HOME/.nvm/nvm.sh"'
        test_tool_loading "$ORIGINAL_BASHRC" "pipx completion" 'eval "$(register-python-argcomplete pipx)"'
        
        echo
    fi
    
    # Cleanup
    rm -f "$TEMP_BASHRC"
    
    echo -e "${GREEN}Performance testing completed!${NC}"
}

# Run main function
main "$@"
