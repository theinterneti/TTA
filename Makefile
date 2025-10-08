# Test tiers

.PHONY: test test-neo4j test-redis test-integration

# Unit tests only (fast)
test:
	uv run pytest -q

# Include Neo4j integration tests
test-neo4j:
	uv run pytest -q --neo4j

# Include Redis integration tests
test-redis:
	uv run pytest -q --redis

# Full integration (Neo4j + Redis)
test-integration:
	uv run pytest -q --neo4j --redis
