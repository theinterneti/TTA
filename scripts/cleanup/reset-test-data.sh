#!/bin/bash
# scripts/cleanup/reset-test-data.sh
# Reset test environment to clean state (for CI/CD)
# This is designed for automated testing pipelines

set -e  # Exit on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Resetting test environment to clean state..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Stop and remove containers + volumes in one command
echo "🛑 Stopping test containers and removing volumes..."
docker-compose -f docker/compose/docker-compose.base.yml \
               -f docker/compose/docker-compose.test.yml down -v

# Recreate containers
echo "🔄 Recreating test containers..."
docker-compose -f docker/compose/docker-compose.base.yml \
               -f docker/compose/docker-compose.test.yml up -d

# Wait for health checks
echo "⏳ Waiting for services to be healthy..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    neo4j_health=$(docker inspect -f '{{.State.Health.Status}}' tta-test-neo4j 2>/dev/null || echo "not found")
    redis_health=$(docker inspect -f '{{.State.Health.Status}}' tta-test-redis 2>/dev/null || echo "not found")

    if [ "$neo4j_health" = "healthy" ] && [ "$redis_health" = "healthy" ]; then
        echo "✅ All services healthy!"
        break
    fi

    echo "   Neo4j: $neo4j_health | Redis: $redis_health (${elapsed}s elapsed)"
    sleep 5
    elapsed=$((elapsed + 5))
done

if [ $elapsed -ge $timeout ]; then
    echo "⚠️  Warning: Health checks did not complete in ${timeout}s"
    echo "   Services may still be starting. Check manually with:"
    echo "   bash docker/scripts/tta-docker.sh test status"
fi

echo ""
echo "✅ Test environment reset complete!"
echo ""
echo "Test services are now running on:"
echo "  • Neo4j:  http://localhost:8474 (bolt://localhost:8687)"
echo "  • Redis:  localhost:7379"
echo ""
echo "Verify with:"
echo "  docker-compose -f docker-compose.test.yml ps"
