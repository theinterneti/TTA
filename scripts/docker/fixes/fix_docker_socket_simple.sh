#!/bin/bash
set -e

echo "Fixing Docker socket permissions in the TTA.prototype container..."

# Copy the Docker socket from the host to the container
echo "Copying Docker socket to container..."
docker cp /var/run/docker.sock tta-app:/var/run/docker.sock

# Fix permissions on the Docker socket
echo "Setting permissions on Docker socket..."
docker exec -it tta-app bash -c "chmod 666 /var/run/docker.sock"

# Test Docker access
echo "Testing Docker access..."
docker exec -it tta-app bash -c "docker ps || echo 'Docker access still not working'"

echo "Done!"
