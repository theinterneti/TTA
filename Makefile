# Test tiers

.PHONY: test test-neo4j test-redis test-integration test-status test-quick test-coverage watch watch-unit watch-all

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

# Quick unit-only run scoped to tests/unit/ — fastest feedback loop (~5s)
test-quick:
	uv run pytest -q -x -m "not integration and not neo4j and not redis" tests/unit/

# Per-module coverage report for src/ (unit tests only, no services required)
test-coverage:
	uv run pytest -q -m "not integration and not neo4j and not redis" \
		--cov=src --cov-report=term-missing:skip-covered --cov-fail-under=0

# Snapshot of test suite health: counts + collection errors (completes in <60s)
# Coverage is skipped here for speed — use make test-coverage for a full report.
test-status:
	@echo ""
	@echo "=== TTA Test Suite Status ==="
	@UNIT_LINE=$$(uv run pytest --collect-only --continue-on-collection-errors \
	              -m "not integration and not neo4j and not redis" 2>&1 \
	              | grep -E "tests? collected"); \
	 INTG_LINE=$$(uv run pytest --collect-only --continue-on-collection-errors \
	              -m "integration or neo4j or redis" 2>&1 \
	              | grep -E "tests? collected"); \
	 UNIT_COUNT=$$(echo "$$UNIT_LINE" | grep -oE "^[0-9]+" || echo "?"); \
	 INTG_COUNT=$$(echo "$$INTG_LINE" | grep -oE "^[0-9]+" || echo "?"); \
	 ERR_COUNT=$$(echo "$$UNIT_LINE $$INTG_LINE" | grep -oE "[0-9]+ error" | \
	              awk '{s+=$$1} END {print s+0}'); \
	 printf "Unit tests (no services):         %s collected\n" "$$UNIT_COUNT"; \
	 printf "Integration tests (Redis/Neo4j):  %s collected\n" "$$INTG_COUNT"; \
	 printf "Collection errors:                %s\n" "$$ERR_COUNT"; \
	 printf "Coverage (src/):                  -- (run make test-coverage for full report)\n"
	@echo "============================"
	@echo ""

# Continuous unit testing — cancels and restarts on each file save (-r)
watch:
	watchexec -r -e py,toml --clear -- uv run pytest -q -x -m "not integration and not neo4j and not redis" tests/

# Continuous unit testing scoped to tests/unit/ — faster feedback than watch
watch-unit:
	watchexec -r -e py,toml --clear -- uv run pytest -q -x -m "not integration and not neo4j and not redis" tests/unit/

# Continuous full testing — requires Neo4j + Redis services running
watch-all:
	watchexec -r -e py,toml --clear -- uv run pytest -q -x --neo4j --redis tests/
