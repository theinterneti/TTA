#!/bin/bash
# Keploy Docker wrapper script for TTA
# Usage: ./keploy.sh [record|test]

KEPLOY_IMAGE="ghcr.io/keploy/keploy:latest"
NETWORK_NAME="keploy-network"

# Create network if it doesn't exist
docker network create ${NETWORK_NAME} 2>/dev/null || true

case "$1" in
    record)
        echo "🎬 Recording API interactions with Keploy..."
        echo "Starting in 3 seconds. Make API calls in another terminal."
        echo "Press Ctrl+C when done recording."
        sleep 3

        docker run --rm -it \
            --name keploy \
            --network ${NETWORK_NAME} \
            -v "$(pwd):/workspace" \
            -v "/tmp:/tmp" \
            --privileged \
            ${KEPLOY_IMAGE} \
            record \
            -c "python simple_test_api.py" \
            --delay 10 \
            --path "/workspace/keploy"
        ;;

    test)
        echo "🧪 Running Keploy tests..."

        if [ ! -d "keploy/tests" ] || [ -z "$(ls -A keploy/tests 2>/dev/null)" ]; then
            echo "❌ No test cases found!"
            echo "Run './keploy.sh record' first to record some API interactions"
            exit 1
        fi

        docker run --rm -it \
            --name keploy \
            --network ${NETWORK_NAME} \
            -v "$(pwd):/workspace" \
            -v "/tmp:/tmp" \
            --privileged \
            ${KEPLOY_IMAGE} \
            test \
            -c "python simple_test_api.py" \
            --delay 10 \
            --path "/workspace/keploy"
        ;;

    *)
        echo "Keploy Docker Wrapper for TTA"
        echo ""
        echo "Usage: $0 {record|test}"
        echo ""
        echo "Commands:"
        echo "  record  - Record API interactions as test cases"
        echo "  test    - Replay recorded tests"
        echo ""
        echo "Examples:"
        echo "  $0 record   # Start recording"
        echo "  $0 test     # Run tests"
        exit 1
        ;;
esac
