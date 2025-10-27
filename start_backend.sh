#!/bin/bash
#
# TTA Backend API Startup Script
#
# This script properly configures the environment and starts the FastAPI backend server.
# It handles PYTHONPATH configuration to ensure proper module imports.
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TTA Backend API Startup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo -e "${YELLOW}Project Root:${NC} $PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}Error: Virtual environment not found at $PROJECT_ROOT/.venv${NC}"
    echo "Please create a virtual environment first:"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$PROJECT_ROOT/.venv/bin/activate"

# Set PYTHONPATH to project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
echo -e "${YELLOW}PYTHONPATH:${NC} $PYTHONPATH"

# Check if required services are running
echo ""
echo -e "${YELLOW}Checking required services...${NC}"

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is running"
else
    echo -e "${YELLOW}⚠${NC} Redis is not running (optional for some features)"
fi

# Check Neo4j
if curl -s http://localhost:7474 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Neo4j is running"
else
    echo -e "${YELLOW}⚠${NC} Neo4j is not running (optional for some features)"
fi

# Parse command line arguments
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
RELOAD="${RELOAD:-true}"
LOG_LEVEL="${LOG_LEVEL:-info}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --no-reload)
            RELOAD="false"
            shift
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --host HOST          Host to bind to (default: 0.0.0.0)"
            echo "  --port PORT          Port to bind to (default: 8080)"
            echo "  --no-reload          Disable auto-reload"
            echo "  --log-level LEVEL    Log level (default: info)"
            echo "  --help               Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  HOST                 Same as --host"
            echo "  PORT                 Same as --port"
            echo "  RELOAD               Set to 'false' to disable reload"
            echo "  LOG_LEVEL            Same as --log-level"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Start the server
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting FastAPI Server${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Host:${NC} $HOST"
echo -e "${YELLOW}Port:${NC} $PORT"
echo -e "${YELLOW}Reload:${NC} $RELOAD"
echo -e "${YELLOW}Log Level:${NC} $LOG_LEVEL"
echo ""
echo -e "${GREEN}API Documentation:${NC} http://localhost:$PORT/docs"
echo -e "${GREEN}Health Check:${NC} http://localhost:$PORT/health"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Build uvicorn command
UVICORN_CMD="uvicorn src.player_experience.api.app:app --host $HOST --port $PORT --log-level $LOG_LEVEL"

if [ "$RELOAD" = "true" ]; then
    UVICORN_CMD="$UVICORN_CMD --reload"
fi

# Run the server
exec $UVICORN_CMD
