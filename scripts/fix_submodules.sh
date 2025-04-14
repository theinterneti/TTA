#!/bin/bash

# This script fixes the submodule configuration

# Remove the old submodule configuration
rm -f .gitmodules

# Create a new .gitmodules file
cat > .gitmodules << EOF
[submodule "TTA.prototype"]
	path = TTA.prototype
	url = https://github.com/theinterneti/TTA.prototype.git
	branch = Active

[submodule "tta.dev"]
	path = tta.dev
	url = https://github.com/theinterneti/tta.dev.git
	branch = MCP-integrations
EOF

# Reinitialize the submodules
git submodule init
git submodule update

echo "Submodules fixed!"
