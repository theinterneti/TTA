#!/bin/bash
set -e

echo "Standardizing naming conventions in TTA repository..."

# Check if TTA.prototype exists
if [ -d "TTA.prototype" ]; then
  echo "Renaming TTA.prototype to tta.prototype..."

  # Create a temporary directory for the rename
  mkdir -p tta.prototype.temp

  # Copy all files from TTA.prototype to tta.prototype.temp
  cp -r TTA.prototype/* tta.prototype.temp/
  cp -r TTA.prototype/.* tta.prototype.temp/ 2>/dev/null || true

  # Remove TTA.prototype
  rm -rf TTA.prototype

  # Rename tta.prototype.temp to tta.prototype
  mv tta.prototype.temp tta.prototype

  echo "Successfully renamed TTA.prototype to tta.prototype"

  # Update references in files
  echo "Updating references to TTA.prototype in files..."
  find . -type f -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.yml" -o -name "*.json" | xargs grep -l "TTA.prototype" | xargs sed -i 's/TTA\.prototype/tta.prototype/g' 2>/dev/null || true

  echo "Naming standardization completed!"
else
  echo "TTA.prototype directory not found. No renaming needed."
fi
