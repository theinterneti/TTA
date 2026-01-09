# TTA Application

The Therapeutic Text Adventure game application.

## Overview

TTA is an AI-powered therapeutic text adventure that combines evidence-based mental health support with interactive storytelling. The application uses a multi-agent orchestration architecture with circuit breaker patterns, Redis-based message coordination, and Neo4j graph databases.

## Structure (Post-Migration)

This directory will contain:

- `src/` - Application source code
- `tests/` - Application tests
- `packages/` - Application workspace packages
- `scripts/` - Application-specific scripts
- `docs/` - Game/therapy documentation

## Migration Status

**Status**: Awaiting migration

Content will be migrated from root-level directories in subsequent phases after platform_tta_dev components are established.

## Current Location

Application code is currently located at:

- Source: `/src/`
- Tests: `/tests/`
- Packages: `/packages/`
- Scripts: `/scripts/` (application-specific scripts)
- Docs: `/docs/` (therapeutic and game documentation)

## Architecture

See current architecture documentation:

- [Agent Orchestration](../docs/architecture/agent-orchestration.md)
- [Database Architecture](../docs/architecture/database-architecture.md)
- [Safety & Security](../.github/instructions/safety.instructions.md)

## Development

For the TTA application development workflow, see:

- [Dev Workflow Quick Reference](../docs/project/dev-workflow-quick-reference.md)
- [Testing Requirements](../.github/instructions/testing-requirements.instructions.md)

For platform development (agentic tools), see [platform_tta_dev/](../platform_tta_dev/).

## License

See [LICENSE](../LICENSE) in repository root.


---
**Logseq:** [[TTA.dev/App_tta/Readme]]
