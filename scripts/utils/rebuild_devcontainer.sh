#!/bin/bash
set -e

echo "Rebuilding the TTA.prototype devcontainer..."

# Stop the container
cd TTA.prototype
docker-compose down

# Start the container
docker-compose up -d

# Wait for the container to start
sleep 5

# Run the test_docker.sh script inside the container
docker exec -it tta-app bash -c "/app/scripts/test_docker.sh"

echo "Done!"
