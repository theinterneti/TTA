#!/bin/bash
# Storybook Wrapper Script - Automatic Vite 6/7 Version Management
#
# This script ensures Storybook runs with Vite 6 while keeping
# the main application on Vite 7. It's a temporary solution until
# Storybook officially supports Vite 7.

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")"
STORYBOOK_DIR="$FRONTEND_DIR/.storybook"

echo -e "${BLUE}🔧 TTA Storybook Environment Manager${NC}"
echo -e "${YELLOW}📦 Managing dual Vite versions (Main: 7.x, Storybook: 6.x)${NC}"
echo ""

# Check if .storybook/package.json exists
if [ ! -f "$STORYBOOK_DIR/package.json" ]; then
    echo -e "${YELLOW}⚠️  .storybook/package.json not found${NC}"
    echo -e "Creating Storybook environment with Vite 6..."

    # Create .storybook directory if it doesn't exist
    mkdir -p "$STORYBOOK_DIR"

    # Copy template package.json
    cat > "$STORYBOOK_DIR/package.json" <<'EOF'
{
  "name": "tta-storybook-env",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "vite": "^6.0.0",
    "@storybook/addon-essentials": "^8.6.14",
    "@storybook/addon-interactions": "^8.6.14",
    "@storybook/addon-links": "^8.6.14",
    "@storybook/addon-onboarding": "^8.6.14",
    "@storybook/blocks": "^8.6.14",
    "@storybook/react-vite": "^8.6.14",
    "@storybook/test-runner": "^0.23.0",
    "storybook": "^8.6.14"
  }
}
EOF
fi

# Install Storybook dependencies with Vite 6
cd "$STORYBOOK_DIR"

if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
    echo -e "${BLUE}📥 Installing Storybook dependencies (Vite 6.x)...${NC}"
    npm install --legacy-peer-deps
    echo -e "${GREEN}✅ Storybook environment ready${NC}"
else
    echo -e "${GREEN}✅ Storybook environment already installed${NC}"
fi

# Determine command (dev or build)
COMMAND=${1:-dev}

cd "$FRONTEND_DIR"

case $COMMAND in
    dev|start)
        echo -e "${BLUE}🚀 Starting Storybook dev server (Vite 6.x)...${NC}"
        echo -e "${YELLOW}📍 Storybook will be available at http://localhost:6006${NC}"
        echo ""

        # Use Storybook's Vite 6 installation
        NODE_PATH="$STORYBOOK_DIR/node_modules:$NODE_PATH" \
        npx --prefix "$STORYBOOK_DIR" storybook dev -p 6006 --config-dir "$STORYBOOK_DIR"
        ;;

    build)
        echo -e "${BLUE}🏗️  Building Storybook (Vite 6.x)...${NC}"

        # Use Storybook's Vite 6 installation
        NODE_PATH="$STORYBOOK_DIR/node_modules:$NODE_PATH" \
        npx --prefix "$STORYBOOK_DIR" storybook build --config-dir "$STORYBOOK_DIR" --output-dir "$FRONTEND_DIR/storybook-static"

        echo -e "${GREEN}✅ Storybook built successfully${NC}"
        ;;

    test)
        echo -e "${BLUE}🧪 Running Storybook tests (Vite 6.x)...${NC}"

        # Ensure Storybook is built first
        if [ ! -d "$FRONTEND_DIR/storybook-static" ]; then
            echo -e "${YELLOW}Building Storybook first...${NC}"
            "$0" build
        fi

        # Run test runner
        NODE_PATH="$STORYBOOK_DIR/node_modules:$NODE_PATH" \
        npx --prefix "$STORYBOOK_DIR" test-storybook
        ;;

    clean)
        echo -e "${YELLOW}🧹 Cleaning Storybook environment...${NC}"
        rm -rf "$STORYBOOK_DIR/node_modules"
        rm -rf "$STORYBOOK_DIR/package-lock.json"
        rm -rf "$FRONTEND_DIR/storybook-static"
        echo -e "${GREEN}✅ Cleaned${NC}"
        ;;

    reinstall)
        echo -e "${YELLOW}🔄 Reinstalling Storybook environment...${NC}"
        "$0" clean
        rm -rf "$STORYBOOK_DIR/node_modules"
        cd "$STORYBOOK_DIR"
        npm install --legacy-peer-deps
        echo -e "${GREEN}✅ Reinstalled${NC}"
        ;;

    *)
        echo -e "${YELLOW}Usage: $0 {dev|build|test|clean|reinstall}${NC}"
        echo ""
        echo "Commands:"
        echo "  dev        - Start Storybook dev server (Vite 6)"
        echo "  build      - Build Storybook static site (Vite 6)"
        echo "  test       - Run Storybook test runner"
        echo "  clean      - Remove Storybook node_modules"
        echo "  reinstall  - Clean and reinstall Storybook environment"
        exit 1
        ;;
esac
