#!/bin/bash
# Record API interactions with Keploy
# Usage: ./keploy-record.sh [API_URL]

set -e

API_URL="${1:-http://localhost:8000}"

echo "🎬 Recording API interactions..."
echo "API URL: $API_URL"
echo ""
echo "Keploy will record your API calls as test cases."
echo "After this script starts, interact with your API normally."
echo "Press Ctrl+C when done recording."
echo ""

# Start TTA API with Keploy recording
keploy record \
    -c "uv run python scripts/minimal_api_server.py" \
    --delay 10 \
    --ports 8000

echo ""
echo "✅ Recording complete! Test cases saved in keploy/tests/"
echo "Run './keploy-test.sh' to replay the recorded tests"
