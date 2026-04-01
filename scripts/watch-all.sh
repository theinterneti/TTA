#!/usr/bin/env bash
# Continuous full test runner (requires Neo4j + Redis) — invoked by `make watch-all`.
exec uv run pytest -q -x --neo4j --redis tests/
