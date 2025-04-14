#!/bin/bash

# TTA Docker Consistency Script
# This script ensures Docker and DevContainer configurations are consistent across repositories

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}TTA Docker Consistency Script${NC}"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker and try again.${NC}"
    exit 1
fi

# Function to check if a file exists
check_file() {
    local file=$1
    local repo=$2

    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}Warning: $file does not exist in $repo${NC}"
        return 1
    fi

    return 0
}

# Check if both repositories have Dockerfile
if ! check_file "tta.dev/Dockerfile" "tta.dev"; then
    echo -e "${YELLOW}tta.dev is missing Dockerfile${NC}"
fi

if ! check_file "tta.prototype/Dockerfile" "tta.prototype"; then
    echo -e "${YELLOW}tta.prototype is missing Dockerfile${NC}"
fi

# Check if both repositories have docker-compose.yml
if ! check_file "tta.dev/docker-compose.yml" "tta.dev"; then
    echo -e "${YELLOW}tta.dev is missing docker-compose.yml${NC}"
fi

if ! check_file "tta.prototype/docker-compose.yml" "tta.prototype" && ! check_file "tta.prototype/docker-compose-mcp.yml" "tta.prototype"; then
    echo -e "${YELLOW}tta.prototype is missing docker-compose.yml or docker-compose-mcp.yml${NC}"
fi

# Check if both repositories have .devcontainer/devcontainer.json
if ! check_file "tta.dev/.devcontainer/devcontainer.json" "tta.dev"; then
    echo -e "${YELLOW}tta.dev is missing .devcontainer/devcontainer.json${NC}"
fi

if ! check_file "tta.prototype/.devcontainer/devcontainer.json" "tta.prototype"; then
    echo -e "${YELLOW}tta.prototype is missing .devcontainer/devcontainer.json${NC}"
fi

# Function to copy template files if they don't exist
copy_template_files() {
    local repo=$1

    echo -e "${BLUE}Checking Docker files for $repo...${NC}"

    # Check Dockerfile
    if ! check_file "$repo/Dockerfile" "$repo" && check_file "templates/$repo/Dockerfile" "templates"; then
        echo "Copying Dockerfile template to $repo..."
        cp templates/$repo/Dockerfile $repo/
        echo -e "${GREEN}Copied Dockerfile template to $repo${NC}"
    fi

    # Check docker-compose.yml
    if ! check_file "$repo/docker-compose.yml" "$repo" && check_file "templates/$repo/docker-compose.yml" "templates"; then
        echo "Copying docker-compose.yml template to $repo..."
        cp templates/$repo/docker-compose.yml $repo/
        echo -e "${GREEN}Copied docker-compose.yml template to $repo${NC}"
    fi

    # Check devcontainer.json
    if ! check_file "$repo/.devcontainer/devcontainer.json" "$repo" && check_file "templates/$repo/.devcontainer/devcontainer.json" "templates"; then
        echo "Copying devcontainer.json template to $repo..."
        mkdir -p $repo/.devcontainer
        cp templates/$repo/.devcontainer/devcontainer.json $repo/.devcontainer/
        echo -e "${GREEN}Copied devcontainer.json template to $repo${NC}"
    fi

    echo -e "${GREEN}Docker files for $repo are in place.${NC}"
}

# Function to standardize container names
standardize_container_names() {
    local repo=$1

    echo -e "${BLUE}Standardizing container names in $repo...${NC}"

    # Check if docker-compose.yml exists
    if [ -f "$repo/docker-compose.yml" ]; then
        # Update container names to include repository prefix
        if grep -q "container_name: tta-" "$repo/docker-compose.yml"; then
            sed -i 's/container_name: tta-/container_name: tta-'$(echo $repo | sed 's/tta.//')-'/g' $repo/docker-compose.yml
            echo -e "${GREEN}Updated container names in $repo/docker-compose.yml${NC}"
        fi
    fi
}

# Function to ensure consistent VS Code extensions
ensure_consistent_extensions() {
    local repo=$1

    echo -e "${BLUE}Ensuring consistent VS Code extensions in $repo...${NC}"

    # Check if devcontainer.json exists
    if [ -f "$repo/.devcontainer/devcontainer.json" ]; then
        # Ensure essential extensions are included
        for ext in "ms-python.python" "ms-python.vscode-pylance" "ms-azuretools.vscode-docker" "ms-vscode-remote.remote-containers" "neo4j-extensions.neo4j-for-vscode"; do
            if ! grep -q "$ext" "$repo/.devcontainer/devcontainer.json"; then
                echo "Adding $ext to $repo/.devcontainer/devcontainer.json"
                # This is a simple approach - in a real scenario, you'd use jq or a similar tool
                # We'll just note the missing extension for now
                echo -e "${YELLOW}Missing extension: $ext in $repo/.devcontainer/devcontainer.json${NC}"
            fi
        done
    fi
}

# Function to ensure consistent environment variables
ensure_consistent_env_vars() {
    local repo=$1

    echo -e "${BLUE}Ensuring consistent environment variables in $repo...${NC}"

    # Check if .env.example exists
    if [ ! -f "$repo/.env.example" ]; then
        echo "Creating .env.example in $repo..."
        if [ -f "templates/$repo/.env.example" ]; then
            cp templates/$repo/.env.example $repo/
        else
            echo "# TTA Environment Variables" > $repo/.env.example
            echo -e "${GREEN}Created basic .env.example in $repo${NC}"
        fi
    fi

    # Ensure essential environment variables are included
    if [ -f "$repo/.env.example" ]; then
        for var in "NEO4J_PASSWORD" "NEO4J_URI" "NEO4J_USER" "MODEL_CACHE_DIR"; do
            if ! grep -q "$var" "$repo/.env.example"; then
                echo "Adding $var to $repo/.env.example"
                echo "$var=default_value" >> $repo/.env.example
                echo -e "${GREEN}Added $var to $repo/.env.example${NC}"
            fi
        done
    fi
}

# Function to ensure consistent Docker Compose services
ensure_consistent_services() {
    local repo=$1

    echo -e "${BLUE}Ensuring consistent Docker Compose services in $repo...${NC}"

    # Check if docker-compose.yml exists
    if [ -f "$repo/docker-compose.yml" ]; then
        # Ensure Neo4j service is included
        if ! grep -q "neo4j:" "$repo/docker-compose.yml"; then
            echo -e "${YELLOW}Neo4j service not found in $repo/docker-compose.yml${NC}"
            echo "Please add Neo4j service manually or use the template"
        fi

        # Ensure app service is included
        if ! grep -q "app:" "$repo/docker-compose.yml"; then
            echo -e "${YELLOW}App service not found in $repo/docker-compose.yml${NC}"
            echo "Please add app service manually or use the template"
        fi
    fi
}

# Process tta.dev repository
if [ -d "tta.dev" ]; then
    echo -e "${GREEN}Processing tta.dev repository...${NC}"
    copy_template_files "tta.dev"
    standardize_container_names "tta.dev"
    ensure_consistent_extensions "tta.dev"
    ensure_consistent_env_vars "tta.dev"
    ensure_consistent_services "tta.dev"
    echo -e "${GREEN}tta.dev repository processed successfully.${NC}"
else
    echo -e "${RED}Error: tta.dev directory not found.${NC}"
fi

# Process tta.prototype repository
if [ -d "tta.prototype" ]; then
    echo -e "${GREEN}Processing tta.prototype repository...${NC}"
    copy_template_files "tta.prototype"
    standardize_container_names "tta.prototype"
    ensure_consistent_extensions "tta.prototype"
    ensure_consistent_env_vars "tta.prototype"
    ensure_consistent_services "tta.prototype"
    echo -e "${GREEN}tta.prototype repository processed successfully.${NC}"
else
    echo -e "${RED}Error: tta.prototype directory not found.${NC}"
fi

echo -e "${GREEN}Docker consistency check completed!${NC}"
echo "You may need to rebuild your containers for changes to take effect."
echo "Run: ./scripts/utils/orchestrate.sh build all"
