#!/bin/bash
set -e

echo "Fixing Docker access in the existing TTA.prototype container..."

# Create a script to set up Docker access inside the container
cat > docker_setup_inside.sh << 'EOF'
#!/bin/bash
set -e

echo "Setting up Docker access inside the container..."

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

# Create Docker socket directory if it doesn't exist
mkdir -p /var/run

# Test Docker access
echo "Testing Docker access..."
if docker ps &> /dev/null; then
    echo "Docker access is working!"
    docker ps
else
    echo "Docker access is not working. Checking socket..."
    if [ -e /var/run/docker.sock ]; then
        echo "Docker socket exists, checking permissions..."
        ls -la /var/run/docker.sock
        echo "Setting permissions..."
        chmod 666 /var/run/docker.sock

        # Test again
        if docker ps &> /dev/null; then
            echo "Docker access is now working!"
            docker ps
        else
            echo "Docker access still not working. The socket might not be properly mounted."
        fi
    else
        echo "Docker socket does not exist. It needs to be mounted from the host."
    fi
fi
EOF

# Make the script executable
chmod +x docker_setup_inside.sh

# Copy the script to the container
docker cp docker_setup_inside.sh tta-app:/tmp/

# Copy the Docker socket from the host to the container
echo "Copying Docker socket to container..."
docker cp /var/run/docker.sock tta-app:/var/run/docker.sock

# Run the setup script inside the container
echo "Running setup script inside the container..."
docker exec -it tta-app bash -c "chmod +x /tmp/docker_setup_inside.sh && /tmp/docker_setup_inside.sh"

# Clean up
rm docker_setup_inside.sh

echo "Done!"
