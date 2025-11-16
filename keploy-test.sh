#!/bin/bash
# Replay recorded Keploy tests
# Usage: ./keploy-test.sh

set -e

if [ ! -d "keploy/tests" ] || [ -z "$(ls -A keploy/tests)" ]; then
    echo "❌ No test cases found!"
    echo "Run './keploy-record.sh' first to record some API interactions"
    exit 1
fi

echo "🧪 Replaying recorded tests..."
echo ""

# Replay tests
keploy test \
    -c "uv run python scripts/minimal_api_server.py" \
    --delay 10 \
    --ports 8000

echo ""
echo "✅ Test replay complete!"
