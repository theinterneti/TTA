#!/bin/bash
# scripts/cleanup/wipe-dev-data.sh
# Safely wipe ALL development data and recreate containers
# This is safe to run anytime - dev data is disposable

set -e  # Exit on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  WARNING: This will DELETE ALL development data!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will remove:"
echo "  • All Neo4j development data (nodes, relationships, indexes)"
echo "  • All Redis development data (keys, sessions, cache)"
echo "  • All Grafana dashboards and settings"
echo "  • All Prometheus metrics history"
echo ""
echo "This will NOT affect:"
echo "  ✓ Test environment (port 8687/7379)"
echo "  ✓ Staging environment (port 9687/8379)"
echo "  ✓ Your source code"
echo "  ✓ Your .env files"
echo ""
read -p "Type 'DELETE DEV DATA' to confirm: " confirm

if [ "$confirm" != "DELETE DEV DATA" ]; then
    echo "❌ Cancelled. No changes made."
    exit 1
fi

echo ""
echo "🛑 Stopping dev containers..."
bash docker/scripts/tta-docker.sh dev down

echo ""
echo "🗑️  Removing dev volumes..."
docker volume rm -f tta_neo4j_dev_data || true
docker volume rm -f tta_neo4j_dev_logs || true
docker volume rm -f tta_neo4j_dev_import || true
docker volume rm -f tta_neo4j_dev_plugins || true
docker volume rm -f tta_redis_dev_data || true
docker volume rm -f tta_grafana_dev_data || true
docker volume rm -f tta_prometheus_dev_data || true

echo ""
echo "🔄 Recreating dev containers..."
bash docker/scripts/tta-docker.sh dev up -d

echo ""
echo "⏳ Waiting for services to be healthy (30 seconds)..."
sleep 30

echo ""
echo "✅ Development data wiped clean!"
echo ""
echo "Your development environment is now fresh and ready to use."
echo "Manage with:"
echo "  bash docker/scripts/tta-docker.sh dev status"
echo "  bash docker/scripts/tta-docker.sh dev logs"
echo ""
