#!/bin/bash
# Extended Evaluation Framework Setup Script

echo "Setting up TTA Extended Session Quality Evaluation Framework..."
echo "================================================================"

# Check Python version
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Install core dependencies
echo "📦 Installing core dependencies..."
pip3 install aiohttp PyYAML psutil

# Install data analysis dependencies
echo "📊 Installing data analysis dependencies..."
pip3 install pandas numpy matplotlib seaborn scipy

# Install optional dependencies (with fallback)
echo "🔧 Installing optional dependencies..."
pip3 install redis neo4j tqdm rich || echo "⚠️  Some optional dependencies failed to install"

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
python3 -c "
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
    print('Run: pip3 install ' + ' '.join(missing))
    sys.exit(1)
else:
    print('✅ All core dependencies installed successfully!')
"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Configure your models in testing/configs/extended_evaluation_config.yaml"
echo "2. Run: python3 testing/run_extended_evaluation.py --mode status"
echo "3. Start with: python3 testing/run_extended_evaluation.py --mode quick-sample"
