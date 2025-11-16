#!/bin/bash

# =============================================================================
# MCP SERVERS SETUP SCRIPT
# =============================================================================
# Automated setup script for Model Context Protocol (MCP) servers
# Compatible with TTA (Therapeutic Text Adventure) Docker environment
# =============================================================================

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Docker service is running
check_docker_service() {
    local service_name=$1
    local container_name=$2

    if docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        log_success "${service_name} container is running"
        return 0
    else
        log_error "${service_name} container is not running"
        return 1
    fi
}

# Test database connection
test_connection() {
    local service=$1
    local test_command=$2

    log_info "Testing ${service} connection..."
    if eval "$test_command" >/dev/null 2>&1; then
        log_success "${service} connection successful"
        return 0
    else
        log_error "${service} connection failed"
        return 1
    fi
}

echo "==============================================================================="
echo "                        MCP SERVERS SETUP SCRIPT"
echo "==============================================================================="
echo "Setting up Model Context Protocol servers for TTA environment"
echo "==============================================================================="

# =============================================================================
# STEP 1: Check Prerequisites
# =============================================================================
log_info "Checking prerequisites..."

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    log_success "Node.js found: ${NODE_VERSION}"
else
    log_error "Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    log_success "npm found: ${NPM_VERSION}"
else
    log_error "npm not found. Please install npm first."
    exit 1
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    log_success "Python found: ${PYTHON_VERSION}"
else
    log_warning "Python3 not found. Some MCP servers may not be available."
fi

# Check Go (optional)
if command_exists go; then
    GO_VERSION=$(go version)
    log_success "Go found: ${GO_VERSION}"
else
    log_warning "Go not found. Grafana MCP server will use Docker instead."
fi

# Check Docker
if command_exists docker; then
    log_success "Docker found"
else
    log_error "Docker not found. Please install Docker first."
    exit 1
fi

# =============================================================================
# STEP 2: Check TTA Docker Services
# =============================================================================
log_info "Checking TTA Docker services..."

SERVICES_OK=true

# Check Redis
if ! check_docker_service "Redis" "tta-redis"; then
    SERVICES_OK=false
fi

# Check Neo4j
if ! check_docker_service "Neo4j" "tta-neo4j"; then
    SERVICES_OK=false
fi

# Check PostgreSQL
if ! check_docker_service "PostgreSQL" "tta-postgres"; then
    SERVICES_OK=false
fi

if [ "$SERVICES_OK" = false ]; then
    log_error "Some TTA services are not running. Please start them first:"
    echo "  docker-compose -f docker-compose.phase2a.yml up -d redis neo4j postgres"
    exit 1
fi

# =============================================================================
# STEP 3: Install MCP Servers
# =============================================================================
log_info "Installing MCP servers..."

# Install PostgreSQL MCP Server
log_info "Installing PostgreSQL MCP server..."
if npm install -g @executeautomation/database-server; then
    log_success "PostgreSQL MCP server installed"
else
    log_error "Failed to install PostgreSQL MCP server"
    exit 1
fi

# Install uv (Python package manager)
if command_exists python3; then
    log_info "Installing uv (Python package manager)..."
    if pip3 install uv; then
        log_success "uv installed"

        # Install Neo4j MCP Server
        log_info "Installing Neo4j MCP server..."
        if uvx --help >/dev/null 2>&1; then
            log_success "Neo4j MCP server available via uvx"
        else
            log_warning "uvx not available, Neo4j MCP server may need manual installation"
        fi
    else
        log_warning "Failed to install uv, Neo4j MCP server may not be available"
    fi
fi

# Install Grafana MCP Server
if command_exists go; then
    log_info "Installing Grafana MCP server..."
    if GOBIN="$HOME/go/bin" go install github.com/grafana/mcp-grafana/cmd/mcp-grafana@latest; then
        log_success "Grafana MCP server installed"
        # Add Go bin to PATH if not already there
        if [[ ":$PATH:" != *":$HOME/go/bin:"* ]]; then
            echo 'export PATH="$HOME/go/bin:$PATH"' >> ~/.bashrc
            export PATH="$HOME/go/bin:$PATH"
            log_info "Added Go bin directory to PATH"
        fi
    else
        log_warning "Failed to install Grafana MCP server"
    fi
else
    log_warning "Go not available, Grafana MCP server will use Docker"
fi

# =============================================================================
# STEP 4: Test Database Connections
# =============================================================================
log_info "Testing database connections..."

# Load environment variables
if [ -f "mcp-servers.env" ]; then
    source mcp-servers.env
    log_success "Environment variables loaded"
else
    log_warning "mcp-servers.env not found, using defaults"
fi

# Test Redis
test_connection "Redis" "redis-cli -h localhost -p 6379 ping"

# Test Neo4j
test_connection "Neo4j" "docker exec tta-neo4j cypher-shell -u neo4j -p neo4j_password 'RETURN 1'"

# Test PostgreSQL
test_connection "PostgreSQL" "docker exec tta-postgres pg_isready -U tta_user -d tta_db"

# =============================================================================
# STEP 5: Generate Claude Desktop Configuration
# =============================================================================
log_info "Generating Claude Desktop configuration..."

CLAUDE_CONFIG_DIR="$HOME/.config/claude-desktop"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# Create directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Generate configuration
cat > "$CLAUDE_CONFIG_FILE" << 'EOF'
{
  "mcpServers": {
    "neo4j": {
      "command": "uvx",
      "args": ["mcp-neo4j-cypher@0.3.0", "--transport", "stdio"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "neo4j_password",
        "NEO4J_DATABASE": "neo4j",
        "NEO4J_NAMESPACE": "tta"
      }
    },
    "postgresql": {
      "command": "npx",
      "args": [
        "-y",
        "@executeautomation/database-server",
        "--postgresql",
        "--host", "localhost",
        "--database", "tta_db",
        "--user", "tta_user",
        "--password", "tta_password"
      ]
    }
  }
}
EOF

log_success "Claude Desktop configuration generated: $CLAUDE_CONFIG_FILE"

# =============================================================================
# STEP 6: Setup Instructions
# =============================================================================
echo ""
echo "==============================================================================="
echo "                              SETUP COMPLETE"
echo "==============================================================================="
log_success "MCP servers setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set up Grafana API key:"
echo "   - Open http://localhost:3000 (admin/admin)"
echo "   - Go to Administration > Service Accounts"
echo "   - Create service account with appropriate permissions"
echo "   - Generate API key and update GRAFANA_API_KEY in mcp-servers.env"
echo ""
echo "2. Source environment variables:"
echo "   source mcp-servers.env"
echo ""
echo "3. Test MCP servers:"
echo "   - PostgreSQL: npx @executeautomation/database-server --postgresql --host localhost --database tta_db --user tta_user --password tta_password"
echo "   - Neo4j: uvx mcp-neo4j-cypher@0.3.0 --transport stdio"
echo ""
echo "4. Configure Claude Desktop:"
echo "   - Configuration saved to: $CLAUDE_CONFIG_FILE"
echo "   - Restart Claude Desktop to load new configuration"
echo ""
echo "5. Available MCP servers:"
echo "   ✅ PostgreSQL MCP Server (database operations)"
echo "   ✅ Neo4j MCP Server (graph database queries)"
if command_exists go && [ -f "$HOME/go/bin/mcp-grafana" ]; then
    echo "   ✅ Grafana MCP Server (monitoring and visualization)"
else
    echo "   ⚠️  Grafana MCP Server (requires API key setup)"
fi
echo ""
echo "For troubleshooting, check the logs and ensure all Docker services are running."
echo "==============================================================================="
