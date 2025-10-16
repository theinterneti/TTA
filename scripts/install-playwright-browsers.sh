#!/bin/bash

# Install Playwright Browsers for TTA E2E Testing
# This script installs Chromium, Firefox, and WebKit browsers for Playwright

set -e

echo "🎭 Installing Playwright Browsers for TTA E2E Testing"
echo "=================================================="
echo ""

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx is not installed"
    echo "Please install Node.js and npm first"
    exit 1
fi

# Check if Playwright is installed
if ! npm list @playwright/test &> /dev/null; then
    echo "⚠️  Warning: @playwright/test is not installed"
    echo "Installing @playwright/test..."
    npm install --save-dev @playwright/test
fi

echo "📦 Installing browsers..."
echo ""

# Kill any stuck Chrome installation processes
echo "🔍 Checking for stuck installation processes..."
pkill -f "chrome.*install" 2>/dev/null || true
pkill -f "playwright.*install" 2>/dev/null || true

# Remove lockfiles if they exist
if [ -d "$HOME/.cache/ms-playwright/__dirlock" ]; then
    echo "🧹 Removing stale lockfiles..."
    rm -rf "$HOME/.cache/ms-playwright/__dirlock"
fi

# Install browsers directly (not system Chrome)
echo "📥 Installing Chromium, Firefox, and WebKit..."
npx playwright install chromium firefox webkit --force

# Check installation
echo ""
echo "✅ Verifying installation..."
if npx playwright --version &> /dev/null; then
    echo "✓ Playwright is installed"
    npx playwright --version
else
    echo "❌ Playwright installation verification failed"
    exit 1
fi

# List installed browsers
echo ""
echo "📋 Installed browsers:"
npx playwright install --dry-run chromium firefox webkit 2>&1 | grep -E "chromium|firefox|webkit" || true

echo ""
echo "✅ Browser installation complete!"
echo ""
echo "You can now run E2E tests with:"
echo "  npm run test:staging"
echo "  npm run test:staging:headed"
echo "  npm run test:staging:ui"
echo ""
