# Player Experience Component Start/Stop Policy

This document clarifies expected status semantics for the PlayerExperienceComponent lifecycle under orchestration.

## Status expectations

- RUNNING: Start succeeded and health check confirms API is up.
- STOPPED: Component is not running. Also used for graceful failure conditions such as an invalid docker-compose path or environment where we bail early without partial start.
- ERROR: Start/stop attempted but failed unexpectedly in a way that is not a known graceful failure.

## Start behavior

- Always invoke `docker-compose up -d` during start unless short-circuited by a confirmed healthy API.
- If `docker-compose` returns non-zero OR the compose directory is invalid:
  - Return `False` from start()
  - Set component status to STOPPED (graceful failure) so that orchestration integration tests can proceed deterministically.
- On success, wait for health up to 60s; if healthy, start() returns True and status transitions to RUNNING.

## Stop behavior

- Attempt `docker-compose down`.
- If compose errors or times out:
  - Treat as best-effort success; return True and allow status to STOPPED.
- Confirm API is not healthy within a short window.

## Rationale

- Using STOPPED for graceful failures keeps the orchestrator state consistent in tests and CI, while still providing a False return for start() to signal failure.
- Unexpected failures continue to mark ERROR to surface issues.
