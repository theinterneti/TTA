#!/bin/bash

# TTA Recovered Project Setup Script
# This script helps set up the recovered TTA project for development

set -e

echo "🎯 TTA Recovered Project Setup"
echo "================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "core" ]; then
    echo "❌ Error: Please run this script from the recovered-tta-storytelling directory"
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "   Python version: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Error: Python 3.10 or higher is required"
    exit 1
fi
echo "✅ Python version is compatible"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -e .
echo "✅ Python dependencies installed"
echo ""

# Set up environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment configuration..."
    if [ -f "configuration/environment/.env.development.example" ]; then
        cp configuration/environment/.env.development.example .env
        echo "✅ Environment file created from template"
        echo "   📝 Please edit .env with your specific configuration"
    else
        echo "⚠️  No environment template found, creating basic .env"
        cat > .env << 'ENVEOF'
# TTA Environment Configuration
# Edit these values according to your setup

# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# API Configuration
API_HOST=localhost
API_PORT=8000

# AI Configuration
OPENAI_API_KEY=your_openai_key_here

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
ENVEOF
        echo "✅ Basic .env file created"
    fi
else
    echo "✅ Environment file already exists"
fi
echo ""

# Check for Node.js (optional)
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "📦 Node.js found: $node_version"
    
    # Install frontend dependencies if package.json exists
    if [ -f "frontend/package.json" ]; then
        echo "🔧 Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
        echo "✅ Frontend dependencies installed"
    fi
    
    # Install web interface dependencies
    for interface in web-interfaces/*/; do
        if [ -f "$interface/package.json" ]; then
            interface_name=$(basename "$interface")
            echo "🔧 Installing dependencies for $interface_name..."
            cd "$interface"
            npm install
            cd - > /dev/null
            echo "✅ $interface_name dependencies installed"
        fi
    done
else
    echo "⚠️  Node.js not found - web interface dependencies will need to be installed manually"
fi
echo ""

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x tools/tta.sh 2>/dev/null || true
chmod +x tools/scripts/*.sh 2>/dev/null || true
echo "✅ Scripts made executable"
echo ""

# Run basic tests to verify setup
echo "🧪 Running basic verification tests..."
if [ -f "testing/pytest.ini" ]; then
    cd testing
    if python -m pytest --version &> /dev/null; then
        echo "   Running a quick test to verify setup..."
        python -m pytest tests/ -x -q --tb=short || echo "   ⚠️  Some tests failed - this may be expected for initial setup"
    else
        echo "   ⚠️  pytest not available - install with: pip install pytest"
    fi
    cd ..
else
    echo "   ⚠️  No test configuration found"
fi
echo ""

# Display next steps
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. 📝 Edit .env file with your specific configuration"
echo "2. 🗄️  Set up required databases (Neo4j, etc.)"
echo "3. 🧪 Run tests: cd testing && pytest tests/"
echo "4. 🚀 Start the system: ./tools/tta.sh start"
echo ""
echo "📚 Documentation:"
echo "   - Project overview: RECOVERED_PROJECT_README.md"
echo "   - Migration details: MIGRATION_SUMMARY.md"
echo "   - Setup guides: documentation/Documentation/setup/"
echo ""
echo "🔧 Development commands:"
echo "   - Check status: ./tools/tta.sh status"
echo "   - Start system: ./tools/tta.sh start"
echo "   - Stop system: ./tools/tta.sh stop"
echo ""
echo "Happy coding! 🚀"
