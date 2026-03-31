# Test tiers

.PHONY: test test-neo4j test-redis test-integration watch watch-all

# Unit tests only (fast, no services required — matches quality gate)
test:
	uv run pytest -q -m "not integration and not neo4j and not redis"

# Include Neo4j integration tests (requires Neo4j running)
test-neo4j:
	uv run pytest -q --neo4j

# Include Redis integration tests (requires Redis running)
test-redis:
	uv run pytest -q --redis

# Full integration suite (requires Neo4j + Redis)
test-integration:
	uv run pytest -q --neo4j --redis

# Continuous unit testing — cancels and restarts on each file save (-r)
watch:
	watchexec -r -e py,toml --clear -- uv run pytest -q -x -m "not integration and not neo4j and not redis" tests/

# Continuous full testing — requires Neo4j + Redis services running
watch-all:
	watchexec -r -e py,toml --clear -- uv run pytest -q -x --neo4j --redis tests/
