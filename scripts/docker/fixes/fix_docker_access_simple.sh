#!/bin/bash
set -e

echo "Fixing Docker access in the existing TTA.prototype container..."

# Check if the container is running
if ! docker ps | grep -q tta-app; then
    echo "Starting the TTA.prototype container..."
    cd TTA.prototype
    docker-compose up -d
    cd ..
    sleep 5
fi

# Create a script to test Docker access inside the container
cat > docker_test.sh << 'EOF'
#!/bin/bash
set -e

echo "Testing Docker access inside the container..."

# Check if Docker CLI is installed
if ! command -v docker &> /dev/null; then
    echo "Docker CLI not found, installing..."
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce-cli
else
    echo "Docker CLI is already installed"
    docker --version
fi

# Check Docker socket
echo "Checking Docker socket..."
ls -la /var/run/docker.sock || echo "Docker socket not found"

# Try to run Docker command
echo "Trying to run Docker command..."
docker ps && echo "Docker command succeeded!" || echo "Docker command failed"

echo "Docker access test completed"
EOF

# Make the script executable
chmod +x docker_test.sh

# Copy the script to the container
docker cp docker_test.sh tta-app:/tmp/

# Run the test script inside the container
echo "Running test script inside the container..."
docker exec -it tta-app bash -c "chmod +x /tmp/docker_test.sh && /tmp/docker_test.sh"

# Clean up
rm docker_test.sh

echo "Done!"
