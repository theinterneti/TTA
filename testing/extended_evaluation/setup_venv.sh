#!/bin/bash
# Extended Evaluation Framework Setup with Virtual Environment

echo "Setting up TTA Extended Session Quality Evaluation Framework with Virtual Environment..."
echo "======================================================================================"

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "📦 Virtual environment already exists. Activating..."
    source venv/bin/activate
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv

    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "💡 Try: sudo apt install python3-venv python3-full"
        exit 1
    fi

    echo "✅ Virtual environment created"
    source venv/bin/activate
fi

echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
echo "📦 Installing core dependencies..."
pip install aiohttp PyYAML psutil

# Install data analysis dependencies
echo "📊 Installing data analysis dependencies..."
pip install pandas numpy matplotlib seaborn scipy

# Install optional dependencies
echo "🔧 Installing optional dependencies..."
pip install redis neo4j tqdm rich

# Create results directories
echo "📁 Creating results directories..."
mkdir -p testing/results/extended_evaluation/reports
mkdir -p testing/results/extended_evaluation/visualizations

# Set permissions
echo "🔐 Setting permissions..."
chmod +x testing/run_extended_evaluation.py
chmod +x testing/extended_evaluation/example_usage.py

# Verify installation
echo "✅ Verifying installation..."
python -c "
import sys
required_modules = ['aiohttp', 'yaml', 'psutil', 'pandas', 'numpy', 'matplotlib']
missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f'  ✓ {module}')
    except ImportError:
        missing.append(module)
        print(f'  ✗ {module}')

if missing:
    print(f'❌ Missing modules: {missing}')
    sys.exit(1)
else:
    print('✅ All core dependencies installed successfully!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 To use the framework:"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Configure models in: testing/configs/production_extended_evaluation.yaml"
    echo "3. Run status check: python testing/run_extended_evaluation.py --mode status"
    echo "4. Start with quick test: python testing/run_extended_evaluation.py --mode quick-sample"
    echo ""
    echo "💡 The virtual environment is now active for this session"
else
    echo "❌ Setup failed. Please check error messages above."
    exit 1
fi
