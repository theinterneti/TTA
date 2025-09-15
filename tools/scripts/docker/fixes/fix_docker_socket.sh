#!/bin/bash
set -e

echo "Fixing Docker socket permissions..."

# Stop the container
docker-compose -f TTA.prototype/docker-compose.yml down

# Update the docker-compose.yml file to ensure proper Docker socket mounting
sed -i 's|/var/run/docker.sock:/var/run/docker.sock|/var/run/docker.sock:/var/run/docker.sock:rw|g' TTA.prototype/docker-compose.yml

# Start the container
docker-compose -f TTA.prototype/docker-compose.yml up -d

# Wait for the container to start
sleep 5

# Fix permissions on the Docker socket
docker exec -it tta-app bash -c "chmod 666 /var/run/docker.sock"

# Test Docker access
echo "Testing Docker access..."
docker exec -it tta-app bash -c "docker ps || echo 'Docker access still not working'"

echo "Done!"
