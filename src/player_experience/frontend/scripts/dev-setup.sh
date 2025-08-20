#!/bin/bash

# TTA Frontend Development Setup Script

echo "🚀 Setting up TTA Player Experience Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16+ is required. Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created from .env.example"
else
    echo "✅ .env file already exists"
fi

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
npm test -- --run --passWithNoTests

if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo "✅ Tests passed"

echo ""
echo "🎉 Frontend setup complete!"
echo ""
echo "Available commands:"
echo "  npm start     - Start development server"
echo "  npm build     - Build for production"
echo "  npm test      - Run tests"
echo ""
echo "The development server will be available at: http://localhost:3000"
echo "Make sure the TTA backend is running at: http://localhost:8000"
echo ""