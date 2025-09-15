#!/bin/bash

# This script updates the submodules to the latest commit on their respective branches

# Update TTA.prototype submodule
echo "Updating TTA.prototype submodule..."
cd TTA.prototype
git fetch
git checkout Active
git pull origin Active
cd ..

# Update tta.dev submodule
echo "Updating tta.dev submodule..."
cd tta.dev
git fetch
git checkout MCP-integrations
git pull origin MCP-integrations
cd ..

# Update the main repository to use the latest submodule commits
echo "Updating main repository..."
git add TTA.prototype tta.dev
git commit -m "Update submodules to latest commits"
git push origin main

echo "Done!"
