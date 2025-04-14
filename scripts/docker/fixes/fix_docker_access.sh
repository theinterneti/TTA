#!/bin/bash
set -e

echo "Fixing Docker access in the TTA.prototype container..."

# Install Docker CLI in the container
docker exec -it tta-app bash -c "apt-get update && \
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    \$(lsb_release -cs) stable\" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli"

# Ensure the Docker socket is properly mounted
docker exec -it tta-app bash -c "mkdir -p /var/run && \
    touch /var/run/docker.sock && \
    chmod 666 /var/run/docker.sock"

# Copy the host's Docker socket to the container
docker cp /var/run/docker.sock tta-app:/var/run/docker.sock

# Set proper permissions
docker exec -it tta-app bash -c "chmod 666 /var/run/docker.sock"

# Test Docker access
docker exec -it tta-app bash -c "docker ps"

echo "Docker access fix completed!"
