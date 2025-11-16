#!/bin/bash
# Keploy Setup Script for TTA
# Downloads and installs Keploy for API test recording/replay

set -e

echo "🚀 Installing Keploy for TTA..."

# Install Keploy
curl --silent --location "https://github.com/keploy/keploy/releases/latest/download/keploy_linux_amd64.tar.gz" | tar xz -C /tmp
sudo mkdir -p /usr/local/bin && sudo mv /tmp/keploy /usr/local/bin

# Verify installation
if command -v keploy &> /dev/null; then
    echo "✅ Keploy installed successfully!"
    keploy --version
else
    echo "❌ Keploy installation failed"
    exit 1
fi

# Create keploy directory structure
mkdir -p keploy/{tests,mocks}

echo ""
echo "📝 Next steps:"
echo "1. Start your TTA API: uv run python src/main.py start"
echo "2. Record tests: ./keploy-record.sh"
echo "3. Replay tests: ./keploy-test.sh"
