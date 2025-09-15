#!/bin/bash
set -e

echo "Fixing Docker socket permissions in the TTA.prototype container..."

# Stop the container
echo "Stopping the container..."
docker-compose -f TTA.prototype/docker-compose.yml down

# Start the container with the Docker socket mounted
echo "Starting the container with Docker socket mounted..."
docker-compose -f TTA.prototype/docker-compose.yml up -d

# Wait for the container to start
echo "Waiting for the container to start..."
sleep 5

# Fix permissions on the Docker socket on the host
echo "Fixing Docker socket permissions on the host..."
sudo chmod 666 /var/run/docker.sock || echo "Could not change permissions on host (no sudo). Will try inside container."

# Create a script to test Docker access inside the container
cat > test_docker_access.sh << 'EOF'
#!/bin/bash
set -e

echo "Testing Docker access inside the container..."

# Check if Docker CLI is installed
if command -v docker &> /dev/null; then
    echo "Docker CLI is installed"
    docker --version
else
    echo "Docker CLI is not installed"
    exit 1
fi

# Check Docker socket
echo "Checking Docker socket..."
ls -la /var/run/docker.sock

# Fix permissions if needed
echo "Setting permissions on Docker socket..."
chmod 666 /var/run/docker.sock || echo "Could not change permissions (not root)"

# Try to run Docker command
echo "Trying to run Docker command..."
docker ps && echo "Docker command succeeded!" || echo "Docker command failed"

# Check Docker socket group
echo "Checking Docker socket group..."
stat -c '%g' /var/run/docker.sock

# Check current user groups
echo "Checking current user groups..."
id

# Try running with sudo if available
echo "Trying with sudo if available..."
sudo docker ps 2>/dev/null || echo "Sudo not available or Docker still not working"

echo "Docker access test completed"
EOF

# Make the script executable
chmod +x test_docker_access.sh

# Copy the script to the container
docker cp test_docker_access.sh tta-app:/tmp/

# Run the test script inside the container
echo "Running test script inside the container..."
docker exec -it tta-app bash -c "chmod +x /tmp/test_docker_access.sh && /tmp/test_docker_access.sh"

# Clean up
rm test_docker_access.sh

echo "Done!"
