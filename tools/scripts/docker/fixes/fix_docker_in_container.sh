#!/bin/bash
set -e

echo "Installing Docker CLI in the container and fixing permissions..."

# Install Docker CLI in the container
docker exec -it tta-app bash -c "apt-get update && \
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    \$(lsb_release -cs) stable\" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli"

# Copy the Docker socket from the host to the container
docker cp /var/run/docker.sock tta-app:/var/run/docker.sock

# Fix permissions on the Docker socket
docker exec -it tta-app bash -c "chmod 666 /var/run/docker.sock"

# Test Docker access
echo "Testing Docker access..."
docker exec -it tta-app bash -c "docker ps || echo 'Docker access still not working'"

echo "Done!"
