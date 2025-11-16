#!/bin/bash
# Keploy Test Runner for TTA
# This script runs recorded test cases

set -e

echo "🧪 TTA Keploy Test Runner"
echo "================================"
echo ""

# Check if Keploy is installed
if ! command -v keploy &> /dev/null; then
    echo "❌ Keploy not found. Please install first:"
    echo "   curl --silent -O -L https://keploy.io/install.sh && source install.sh"
    exit 1
fi

# Check if tests exist
if [ ! -d "keploy/tests" ]; then
    echo "❌ No test cases found. Please record tests first:"
    echo "   bash scripts/keploy_record.sh"
    exit 1
fi

# Choose API to test
echo "Which API did you record tests for?"
echo "1) Main Player Experience API (port 8080)"
echo "2) Minimal Test API (port 8000)"
echo "3) Simple Demo API (port 8000)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        CMD="python -m uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080"
        ;;
    2)
        CMD="python scripts/minimal_api_server.py"
        ;;
    3)
        CMD="python simple_api_server.py"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "⚠️  Note: You don't need Redis or Neo4j running!"
echo "   Keploy uses recorded mocks instead."
echo ""
echo "🚀 Running tests..."
echo "💻 Command: $CMD"
echo ""

# Run Keploy tests
keploy test -c "$CMD" --delay 10
