#!/bin/bash
# Keploy Recording Script for TTA
# This script starts your API and records test cases

set -e

echo "🎯 TTA Keploy Test Recording"
echo "================================"
echo ""

# Check if Keploy is installed
if ! command -v keploy &> /dev/null; then
    echo "❌ Keploy not found. Installing..."
    curl --silent -O -L https://keploy.io/install.sh && source install.sh
fi

# Choose API to test
echo "Which API do you want to test?"
echo "1) Main Player Experience API (port 8080) - Recommended"
echo "2) Minimal Test API (port 8000) - Simpler"
echo "3) Simple Demo API (port 8000) - Lightest"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        CMD="python -m uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080"
        API_URL="http://localhost:8080"
        ;;
    2)
        CMD="python scripts/minimal_api_server.py"
        API_URL="http://localhost:8000"
        ;;
    3)
        CMD="python simple_api_server.py"
        API_URL="http://localhost:8000"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🚀 Starting Keploy recording..."
echo "📍 API URL: $API_URL"
echo "💻 Command: $CMD"
echo ""
echo "⚡ Once the server starts, use your API from another terminal:"
echo "   curl $API_URL/health"
echo "   curl $API_URL/"
echo "   curl $API_URL/docs (for interactive testing)"
echo ""
echo "⏸️  Press Ctrl+C when done to save test cases"
echo ""

# Run Keploy record
keploy record -c "$CMD"
