#!/usr/bin/env bash
# TTA Docker Volume Cleanup Utility
set -euo pipefail

echo "=== TTA Docker Volume Cleanup ==="
echo ""

# List all Docker volumes
echo "Current Docker volumes:"
docker volume ls

echo ""
echo "Identifying potentially orphaned volumes..."
echo ""

# List volumes not used by any container
echo "Unused volumes (candidates for cleanup):"
docker volume ls -q -f dangling=true

echo ""
read -p "Remove all unused volumes? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker volume prune -f
    echo "✓ Cleanup complete"
else
    echo "Cleanup cancelled"
fi

echo ""
echo "To remove specific volumes, use:"
echo "  docker volume rm <volume_name>"
echo ""
echo "To remove all volumes for a specific environment:"
echo "  docker volume ls | grep 'tta-dev' | awk '{print \$2}' | xargs docker volume rm"
