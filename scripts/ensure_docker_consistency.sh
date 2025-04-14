#!/bin/bash
set -e

echo "Ensuring Docker and DevContainer consistency across repositories..."

# Check if both repositories have Dockerfile
if [ ! -f "tta.dev/Dockerfile" ]; then
  echo "tta.dev is missing Dockerfile"
fi

if [ ! -f "TTA.prototype/Dockerfile" ]; then
  echo "TTA.prototype is missing Dockerfile"
fi

# Check if both repositories have docker-compose.yml
if [ ! -f "tta.dev/docker-compose.yml" ]; then
  echo "tta.dev is missing docker-compose.yml"
fi

if [ ! -f "TTA.prototype/docker-compose.yml" ] && [ ! -f "TTA.prototype/docker-compose-mcp.yml" ]; then
  echo "TTA.prototype is missing docker-compose.yml or docker-compose-mcp.yml"
fi

# Check if both repositories have .devcontainer/devcontainer.json
if [ ! -f "tta.dev/.devcontainer/devcontainer.json" ]; then
  echo "tta.dev is missing .devcontainer/devcontainer.json"
fi

if [ ! -f "TTA.prototype/.devcontainer/devcontainer.json" ]; then
  echo "TTA.prototype is missing .devcontainer/devcontainer.json"
fi

# Copy template files if needed
if [ ! -f "tta.dev/Dockerfile" ] && [ -f "templates/tta.dev/Dockerfile" ]; then
  cp templates/tta.dev/Dockerfile tta.dev/
  echo "Copied Dockerfile template to tta.dev"
fi

if [ ! -f "TTA.prototype/Dockerfile" ] && [ -f "templates/TTA.prototype/Dockerfile" ]; then
  cp templates/TTA.prototype/Dockerfile TTA.prototype/
  echo "Copied Dockerfile template to TTA.prototype"
fi

if [ ! -f "tta.dev/docker-compose.yml" ] && [ -f "templates/tta.dev/docker-compose.yml" ]; then
  cp templates/tta.dev/docker-compose.yml tta.dev/
  echo "Copied docker-compose.yml template to tta.dev"
fi

if [ ! -f "TTA.prototype/docker-compose.yml" ] && [ -f "templates/TTA.prototype/docker-compose.yml" ]; then
  cp templates/TTA.prototype/docker-compose.yml TTA.prototype/
  echo "Copied docker-compose.yml template to TTA.prototype"
fi

if [ ! -f "tta.dev/.devcontainer/devcontainer.json" ] && [ -f "templates/tta.dev/.devcontainer/devcontainer.json" ]; then
  mkdir -p tta.dev/.devcontainer
  cp templates/tta.dev/.devcontainer/devcontainer.json tta.dev/.devcontainer/
  echo "Copied devcontainer.json template to tta.dev"
fi

if [ ! -f "TTA.prototype/.devcontainer/devcontainer.json" ] && [ -f "templates/TTA.prototype/.devcontainer/devcontainer.json" ]; then
  mkdir -p TTA.prototype/.devcontainer
  cp templates/TTA.prototype/.devcontainer/devcontainer.json TTA.prototype/.devcontainer/
  echo "Copied devcontainer.json template to TTA.prototype"
fi

echo "Docker and DevContainer consistency check completed!"
