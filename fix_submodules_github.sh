#!/bin/bash

# This script fixes the submodule issues using GitHub API

# Get the GitHub token from the environment
GITHUB_TOKEN=$(grep GITHUB_PERSONAL_ACCESS_TOKEN .env | cut -d= -f2)

# Update the .gitmodules file
echo "Updating .gitmodules file..."
cat > .gitmodules.fixed << EOF
[submodule "TTA.prototype"]
	path = TTA.prototype
	url = https://github.com/theinterneti/TTA.prototype.git
	branch = Active

[submodule "tta.dev"]
	path = tta.dev
	url = https://github.com/theinterneti/tta.dev.git
	branch = MCP-integrations
EOF

# Encode the content in base64
CONTENT=$(base64 -w 0 .gitmodules.fixed)

# Get the current SHA of the .gitmodules file
SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/theinterneti/TTA/contents/.gitmodules \
  | grep sha | head -1 | cut -d'"' -f4)

# Update the .gitmodules file on GitHub
echo "Pushing changes to GitHub..."
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/theinterneti/TTA/contents/.gitmodules \
  -d "{\"message\":\"Fix submodule configuration\",\"content\":\"$CONTENT\",\"sha\":\"$SHA\",\"branch\":\"fix-submodules\"}"

echo "Done!"
