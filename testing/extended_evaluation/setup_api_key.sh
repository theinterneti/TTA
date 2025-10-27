#!/bin/bash
# Setup OpenRouter API Key for TTA Extended Evaluation

echo "🔑 OpenRouter API Key Setup"
echo "=========================="
echo ""
echo "To use Meta's Llama 3.3 8B Instruct model via OpenRouter, you need an API key."
echo ""
echo "Steps to get your free OpenRouter API key:"
echo "1. Visit: https://openrouter.ai/"
echo "2. Sign up for a free account"
echo "3. Go to Keys section and create a new API key"
echo "4. Copy the API key"
echo ""

# Check if API key is already set
if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "✅ OpenRouter API key is already set in environment"
    echo "Current key: ${OPENROUTER_API_KEY:0:8}..."
    echo ""
    read -p "Do you want to update it? (y/N): " update_key
    if [[ $update_key != "y" && $update_key != "Y" ]]; then
        echo "Keeping existing API key."
        exit 0
    fi
fi

echo ""
read -p "Enter your OpenRouter API key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

# Validate API key format (basic check)
if [[ ! $api_key =~ ^sk-or-v1- ]]; then
    echo "⚠️  Warning: API key doesn't match expected OpenRouter format (sk-or-v1-...)"
    read -p "Continue anyway? (y/N): " continue_anyway
    if [[ $continue_anyway != "y" && $continue_anyway != "Y" ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Export for current session
export OPENROUTER_API_KEY="$api_key"

# Add to .bashrc for persistence
if ! grep -q "OPENROUTER_API_KEY" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# OpenRouter API Key for TTA Extended Evaluation" >> ~/.bashrc
    echo "export OPENROUTER_API_KEY=\"$api_key\"" >> ~/.bashrc
    echo "✅ Added API key to ~/.bashrc for future sessions"
else
    # Update existing entry
    sed -i "s/export OPENROUTER_API_KEY=.*/export OPENROUTER_API_KEY=\"$api_key\"/" ~/.bashrc
    echo "✅ Updated API key in ~/.bashrc"
fi

# Create .env file for the project
echo "OPENROUTER_API_KEY=$api_key" > .env
echo "✅ Created .env file in project root"

echo ""
echo "🎉 OpenRouter API key setup complete!"
echo ""
echo "The API key is now available for:"
echo "  • Current terminal session"
echo "  • Future terminal sessions (via ~/.bashrc)"
echo "  • Project environment (via .env file)"
echo ""
echo "Next steps:"
echo "1. Test the configuration: python testing/run_extended_evaluation.py --mode status --config testing/configs/production_extended_evaluation.yaml"
echo "2. Run quick sample: python testing/run_extended_evaluation.py --mode quick-sample --config testing/configs/production_extended_evaluation.yaml"
echo ""
echo "💡 Your API key gives you access to:"
echo "   • Meta Llama 3.3 8B Instruct (free tier)"
echo "   • Rate limits: ~20 requests/minute"
echo "   • Perfect for extended session testing!"
