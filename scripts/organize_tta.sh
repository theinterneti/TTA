#!/bin/bash
set -e

echo "Starting TTA repository organization..."

# Make sure we have the necessary scripts
cp organize_documentation.sh scripts/ 2>/dev/null || true
cp scripts/docker/ensure_docker_consistency.sh . 2>/dev/null || true

# Run the organization scripts
echo "Step 1: Organizing files..."
if [ -f "./organize_files.sh" ]; then
  ./organize_files.sh
elif [ -f "./scripts/organize_files.sh" ]; then
  ./scripts/organize_files.sh
else
  echo "Warning: Could not find organize_files.sh"
fi

# Since organize_files.sh might have moved our scripts, let's find them
if [ -f "scripts/organize_documentation.sh" ]; then
  echo "Step 2: Organizing documentation..."
  chmod +x scripts/organize_documentation.sh
  ./scripts/organize_documentation.sh
elif [ -f "organize_documentation.sh" ]; then
  echo "Step 2: Organizing documentation..."
  chmod +x organize_documentation.sh
  ./organize_documentation.sh
else
  echo "Warning: Could not find organize_documentation.sh"
fi

# Check for Docker consistency script
if [ -f "scripts/docker/ensure_docker_consistency.sh" ]; then
  echo "Step 3: Ensuring Docker consistency..."
  chmod +x scripts/docker/ensure_docker_consistency.sh
  ./scripts/docker/ensure_docker_consistency.sh
elif [ -f "ensure_docker_consistency.sh" ]; then
  echo "Step 3: Ensuring Docker consistency..."
  chmod +x ensure_docker_consistency.sh
  ./ensure_docker_consistency.sh
else
  echo "Warning: Could not find ensure_docker_consistency.sh"
fi

echo "TTA repository organization completed!"
echo ""
echo "Repository structure has been standardized:"
echo "- Files have been organized into appropriate directories"
echo "- Documentation has been organized"
echo "- Docker and DevContainer configurations have been checked for consistency"
echo ""
echo "You may want to review the changes and make any additional adjustments as needed."
