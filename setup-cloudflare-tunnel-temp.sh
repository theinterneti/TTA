#!/bin/bash

# 🚨 TEMPORARY Cloudflare Tunnel Setup for TTA
# ⚠️  WARNING: This is for TEMPORARY testing only - NOT for production or PHI data!

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}🚨 TEMPORARY TESTING SOLUTION ONLY${NC}"
echo -e "${RED}===================================${NC}"
echo -e "${YELLOW}⚠️  This setup is for TEMPORARY testing and demos only!${NC}"
echo -e "${YELLOW}⚠️  DO NOT use with real therapeutic data or PHI!${NC}"
echo -e "${YELLOW}⚠️  NOT HIPAA compliant - for development testing only!${NC}"
echo ""
read -p "Do you understand and accept these limitations? (y/N): " accept_limitations

if [[ ! $accept_limitations =~ ^[Yy]$ ]]; then
    echo "Setup cancelled. Please use AWS Lightsail for proper staging environment."
    exit 1
fi

echo ""
echo -e "${BLUE}🌐 Setting up Cloudflare Tunnel for Temporary Testing${NC}"
echo -e "${BLUE}====================================================${NC}"
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Cloudflare Tunnel (cloudflared)...${NC}"

    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
        sudo dpkg -i cloudflared.deb
        rm cloudflared.deb
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install cloudflared
        else
            echo -e "${RED}❌ Please install Homebrew first or download cloudflared manually${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Unsupported OS. Please install cloudflared manually from:${NC}"
        echo "https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
        exit 1
    fi

    echo -e "${GREEN}✅ Cloudflared installed${NC}"
fi

echo -e "${GREEN}✅ Cloudflared is available${NC}"
echo ""

# Check if TTA services are running locally
echo -e "${BLUE}🔍 Checking local TTA services...${NC}"

API_PORT=8080
WEB_PORT=3000

# Check if API is running
if curl -s http://localhost:$API_PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ TTA API is running on port $API_PORT${NC}"
    API_RUNNING=true
else
    echo -e "${YELLOW}⚠️  TTA API is not running on port $API_PORT${NC}"
    API_RUNNING=false
fi

# Check if web interface is running
if curl -s http://localhost:$WEB_PORT > /dev/null 2>&1; then
    echo -e "${GREEN}✅ TTA Web interface is running on port $WEB_PORT${NC}"
    WEB_RUNNING=true
else
    echo -e "${YELLOW}⚠️  TTA Web interface is not running on port $WEB_PORT${NC}"
    WEB_RUNNING=false
fi

if [ "$API_RUNNING" = false ] && [ "$WEB_RUNNING" = false ]; then
    echo -e "${RED}❌ No TTA services are running locally${NC}"
    echo "Please start your TTA services first:"
    echo "  For API: uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080"
    echo "  For Web: npm start (in your web interface directory)"
    exit 1
fi

echo ""

# Create tunnel configuration
echo -e "${BLUE}🔧 Creating tunnel configuration...${NC}"

# Create a temporary config file
cat > tunnel-config.yml << EOF
tunnel: tta-temp-$(date +%s)
credentials-file: /tmp/tta-tunnel-credentials.json

ingress:
EOF

# Add API tunnel if running
if [ "$API_RUNNING" = true ]; then
    cat >> tunnel-config.yml << EOF
  - hostname: api-temp.tta-demo.com
    service: http://localhost:$API_PORT
EOF
fi

# Add web tunnel if running
if [ "$WEB_RUNNING" = true ]; then
    cat >> tunnel-config.yml << EOF
  - hostname: web-temp.tta-demo.com
    service: http://localhost:$WEB_PORT
EOF
fi

# Add catch-all rule
cat >> tunnel-config.yml << EOF
  - service: http_status:404
EOF

echo -e "${GREEN}✅ Tunnel configuration created${NC}"
echo ""

# Start tunnels
echo -e "${BLUE}🚀 Starting Cloudflare Tunnels...${NC}"
echo -e "${YELLOW}📝 Note: These URLs are temporary and will change each time you run this script${NC}"
echo ""

# Function to start tunnel in background
start_tunnel() {
    local service_name=$1
    local local_port=$2
    local log_file="/tmp/tta-tunnel-$service_name.log"

    echo -e "${BLUE}Starting $service_name tunnel...${NC}"

    # Start tunnel in background and capture the URL
    cloudflared tunnel --url http://localhost:$local_port > "$log_file" 2>&1 &
    local tunnel_pid=$!

    # Wait for tunnel to start and get URL
    sleep 5

    if kill -0 $tunnel_pid 2>/dev/null; then
        local tunnel_url=$(grep -o 'https://.*\.trycloudflare\.com' "$log_file" | head -1)
        if [ -n "$tunnel_url" ]; then
            echo -e "${GREEN}✅ $service_name tunnel started: $tunnel_url${NC}"
            echo "$tunnel_pid:$tunnel_url" >> /tmp/tta-tunnels.txt
        else
            echo -e "${RED}❌ Failed to get $service_name tunnel URL${NC}"
        fi
    else
        echo -e "${RED}❌ Failed to start $service_name tunnel${NC}"
    fi
}

# Clear previous tunnel info
rm -f /tmp/tta-tunnels.txt

# Start tunnels for running services
if [ "$API_RUNNING" = true ]; then
    start_tunnel "API" $API_PORT
fi

if [ "$WEB_RUNNING" = true ]; then
    start_tunnel "Web" $WEB_PORT
fi

echo ""
echo -e "${GREEN}🎉 Temporary tunnels are now active!${NC}"
echo ""

# Display tunnel information
if [ -f /tmp/tta-tunnels.txt ]; then
    echo -e "${BLUE}📋 Active Tunnel URLs:${NC}"
    while IFS=':' read -r pid url; do
        if [ "$API_RUNNING" = true ] && [[ $url == *"trycloudflare.com"* ]]; then
            if curl -s "$url/health" > /dev/null 2>&1; then
                echo -e "${GREEN}  🔌 API: $url${NC}"
                echo -e "      Health: $url/health"
                echo -e "      Docs: $url/docs"
            fi
        fi
        if [ "$WEB_RUNNING" = true ] && [[ $url == *"trycloudflare.com"* ]]; then
            echo -e "${GREEN}  🌐 Web: $url${NC}"
        fi
    done < /tmp/tta-tunnels.txt
fi

echo ""
echo -e "${YELLOW}⚠️  IMPORTANT REMINDERS:${NC}"
echo -e "${YELLOW}  • These URLs are TEMPORARY and will change each time${NC}"
echo -e "${YELLOW}  • DO NOT use with real therapeutic data or PHI${NC}"
echo -e "${YELLOW}  • NOT suitable for persistent staging environment${NC}"
echo -e "${YELLOW}  • Use only for demos and quick testing${NC}"
echo ""

# Create stop script
cat > stop-tunnels.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping TTA temporary tunnels..."

if [ -f /tmp/tta-tunnels.txt ]; then
    while IFS=':' read -r pid url; do
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo "✅ Stopped tunnel: $url"
        fi
    done < /tmp/tta-tunnels.txt
    rm -f /tmp/tta-tunnels.txt
fi

# Clean up any remaining cloudflared processes
pkill -f "cloudflared tunnel" 2>/dev/null || true

echo "🎉 All tunnels stopped"
EOF

chmod +x stop-tunnels.sh

echo -e "${BLUE}📝 Management Commands:${NC}"
echo -e "${GREEN}  Stop tunnels: ./stop-tunnels.sh${NC}"
echo -e "${GREEN}  View logs: tail -f /tmp/tta-tunnel-*.log${NC}"
echo ""

echo -e "${BLUE}🔄 For Persistent Staging Environment:${NC}"
echo -e "${YELLOW}  Run: ./setup-aws-lightsail-staging.sh${NC}"
echo -e "${YELLOW}  Cost: Only $20-40/month for HIPAA-compliant hosting${NC}"
echo ""

echo -e "${GREEN}✅ Temporary tunnel setup complete!${NC}"
echo -e "${YELLOW}⚠️  Remember: This is for testing only - not for production use!${NC}"
