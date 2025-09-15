#!/bin/bash
set -e

echo "Organizing TTA repository..."

# Create necessary directories
mkdir -p scripts/utils
mkdir -p scripts/setup
mkdir -p scripts/docker
mkdir -p scripts/maintenance
mkdir -p Documentation/setup
mkdir -p Documentation/docker
mkdir -p Documentation/development
mkdir -p config/docker

# Standardize repository names (if needed)
# Uncomment the following line if you want to rename TTA.prototype to tta.prototype
# mv TTA.prototype tta.prototype

# Clean up root directory - move utility scripts to scripts directory
mv *.sh scripts/ 2>/dev/null || true

# Move Docker-related files to config/docker
mv docker_setup_guide.md Documentation/docker/ 2>/dev/null || true
mv devcontainer_troubleshooting_guide.md Documentation/docker/ 2>/dev/null || true

# Move documentation files to Documentation directory
mv *.md Documentation/ 2>/dev/null || true

# Remove backup files
find . -name "*.bak" -delete

# Ensure both repositories have consistent structure
# Create necessary directories in tta.dev if they don't exist
mkdir -p tta.dev/.devcontainer
mkdir -p tta.dev/scripts/utils
mkdir -p tta.dev/scripts/setup
mkdir -p tta.dev/scripts/docker
mkdir -p tta.dev/Documentation/setup
mkdir -p tta.dev/Documentation/docker
mkdir -p tta.dev/Documentation/development

# Create necessary directories in TTA.prototype if they don't exist
mkdir -p TTA.prototype/.devcontainer
mkdir -p TTA.prototype/scripts/utils
mkdir -p TTA.prototype/scripts/setup
mkdir -p TTA.prototype/scripts/docker
mkdir -p TTA.prototype/Documentation/setup
mkdir -p TTA.prototype/Documentation/docker
mkdir -p TTA.prototype/Documentation/development

echo "Files organized successfully!"
