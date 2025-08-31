#!/usr/bin/env python3
"""
Setup script for TTA Therapeutic Gaming Frontend Application.

This script initializes the React frontend application with all necessary
dependencies and creates the basic project structure.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, shell=True, cwd=cwd, check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")

    # Check Node.js
    try:
        result = run_command("node --version", check=False)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print(
                "❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/"
            )
            return False
    except FileNotFoundError:
        print(
            "❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/"
        )
        return False

    # Check npm
    try:
        result = run_command("npm --version", check=False)
        if result.returncode == 0:
            print(f"✅ npm: {result.stdout.strip()}")
        else:
            print("❌ npm not found. Please install npm.")
            return False
    except FileNotFoundError:
        print("❌ npm not found. Please install npm.")
        return False

    return True


def create_project_structure():
    """Create the React project structure."""
    print("📁 Creating project structure...")

    frontend_dir = Path("frontend")

    # Create directories
    directories = [
        "src/components/auth",
        "src/components/character",
        "src/components/world",
        "src/components/session",
        "src/components/chat",
        "src/components/export",
        "src/components/common",
        "src/pages",
        "src/services",
        "src/store/slices",
        "src/types",
        "src/utils",
        "src/assets/images",
        "src/assets/icons",
        "public",
    ]

    for directory in directories:
        dir_path = frontend_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def install_dependencies():
    """Install npm dependencies."""
    print("📦 Installing dependencies...")

    frontend_dir = Path("frontend")

    if not (frontend_dir / "package.json").exists():
        print(
            "❌ package.json not found. Please ensure the frontend directory is set up correctly."
        )
        return False

    # Install dependencies
    result = run_command("npm install", cwd=frontend_dir, check=False)
    if result.returncode != 0:
        print("❌ Failed to install dependencies")
        return False

    print("✅ Dependencies installed successfully")
    return True


def create_missing_files():
    """Create essential missing files."""
    print("📄 Creating essential files...")

    frontend_dir = Path("frontend")

    # Create public/index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#4A90A4" />
    <meta name="description" content="TTA Therapeutic Gaming Experience - AI-powered therapeutic gaming for personal growth and healing" />
    <title>TTA Therapeutic Gaming Experience</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>"""

    with open(frontend_dir / "public/index.html", "w") as f:
        f.write(index_html)
    print("✅ Created public/index.html")

    # Create src/index.tsx
    index_tsx = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""

    with open(frontend_dir / "src/index.tsx", "w") as f:
        f.write(index_tsx)
    print("✅ Created src/index.tsx")

    # Create placeholder components
    placeholder_files = [
        ("src/pages/LoginPage.tsx", "LoginPage"),
        ("src/pages/RegisterPage.tsx", "RegisterPage"),
        ("src/pages/Dashboard.tsx", "Dashboard"),
        ("src/pages/CharacterStudio.tsx", "CharacterStudio"),
        ("src/pages/WorldExplorer.tsx", "WorldExplorer"),
        ("src/pages/TherapeuticSession.tsx", "TherapeuticSession"),
        ("src/pages/ProfilePage.tsx", "ProfilePage"),
        ("src/components/common/NavigationBar.tsx", "NavigationBar"),
        ("src/components/common/CrisisSupport.tsx", "CrisisSupport"),
        ("src/components/common/LoadingScreen.tsx", "LoadingScreen"),
    ]

    for file_path, component_name in placeholder_files:
        placeholder_content = f"""import React from 'react';
import {{ Box, Typography }} from '@mui/material';

const {component_name}: React.FC<any> = (props) => {{
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {component_name}
      </Typography>
      <Typography variant="body1" color="text.secondary">
        This component is under development.
      </Typography>
    </Box>
  );
}};

export default {component_name};"""

        with open(frontend_dir / file_path, "w") as f:
            f.write(placeholder_content)
        print(f"✅ Created placeholder: {file_path}")

    # Create remaining Redux slices
    slice_files = [
        "charactersSlice.ts",
        "worldsSlice.ts",
        "sessionsSlice.ts",
        "uiSlice.ts",
    ]

    for slice_file in slice_files:
        slice_name = slice_file.replace("Slice.ts", "")
        slice_content = f"""import {{ createSlice }} from '@reduxjs/toolkit';

interface {slice_name.capitalize()}State {{
  // TODO: Define state interface
}}

const initialState: {slice_name.capitalize()}State = {{
  // TODO: Define initial state
}};

const {slice_name}Slice = createSlice({{
  name: '{slice_name}',
  initialState,
  reducers: {{
    // TODO: Define reducers
  }},
}});

export default {slice_name}Slice.reducer;"""

        with open(frontend_dir / f"src/store/slices/{slice_file}", "w") as f:
            f.write(slice_content)
        print(f"✅ Created Redux slice: {slice_file}")


def create_start_script():
    """Create a convenient start script."""
    print("🚀 Creating start script...")

    start_script = """#!/bin/bash
# TTA Therapeutic Gaming Experience - Development Start Script

echo "🎮 Starting TTA Therapeutic Gaming Experience"
echo "=============================================="

# Check if backend is running
echo "🔍 Checking TTA API backend..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ TTA API backend is running on http://localhost:8080"
else
    echo "❌ TTA API backend is not running!"
    echo "Please start the backend first:"
    echo "   cd .."
    echo "   uv run python -m src.player_experience.api.main"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Start frontend development server
echo "🚀 Starting frontend development server..."
cd frontend
npm start
"""

    with open("start_frontend.sh", "w") as f:
        f.write(start_script)

    # Make script executable
    os.chmod("start_frontend.sh", 0o755)
    print("✅ Created start_frontend.sh script")


def main():
    """Main setup function."""
    print("🎮 TTA Therapeutic Gaming Frontend Setup")
    print("=" * 50)

    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please install required tools and try again.")
        sys.exit(1)

    # Create project structure
    create_project_structure()

    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)

    # Create missing files
    create_missing_files()

    # Create start script
    create_start_script()

    print("\n🎉 Frontend setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the TTA API backend:")
    print("   uv run python -m src.player_experience.api.main")
    print("\n2. Start the frontend development server:")
    print("   ./start_frontend.sh")
    print("   OR")
    print("   cd frontend && npm start")
    print("\n3. Open your browser to http://localhost:3000")
    print("\n🎯 The TTA Therapeutic Gaming Experience will be ready for user testing!")


if __name__ == "__main__":
    main()
