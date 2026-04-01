#!/usr/bin/env bash
# Continuous unit test runner — invoked by `make watch-unit` via watchexec.
# Using a script avoids shell quoting issues with complex marker expressions.
exec uv run pytest -q -x -m "not integration and not neo4j and not redis" tests/unit/
