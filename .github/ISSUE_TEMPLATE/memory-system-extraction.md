---
name: Memory System Extraction
about: Track extraction of memory system components to TTA.dev
title: '[EXTRACTION] Extract tta-agent-coordination package to TTA.dev'
labels: enhancement, packaging, tta.dev-migration
assignees: ''
---

## Overview

Extract the generic Redis-based agent coordination system from the TTA repository into a reusable `tta-agent-coordination` package in the TTA.dev repository.

## Scope

### Components to Extract

**From TTA Repository:**
- `packages/tta-ai-framework/src/tta_ai/orchestration/coordinators/redis_message_coordinator.py`
- `packages/tta-ai-framework/src/tta_ai/orchestration/registries/redis_agent_registry.py`
- `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker.py`
- `packages/tta-ai-framework/src/tta_ai/orchestration/interfaces.py`
- `packages/tta-ai-framework/src/tta_ai/orchestration/messaging.py`
- `packages/tta-ai-framework/src/tta_ai/orchestration/models.py` (generic parts only)

**Generalization Required:**
- Remove TTA-specific agent types (IPA, WBA, NGA)
- Replace with generic `AgentId(type: str, instance: str | None)`
- Remove therapeutic safety validators
- Remove narrative-specific state management

### Components to Keep in TTA

**TTA-Specific (Do NOT Extract):**
- `src/player_experience/api/session_manager.py` (OAuth, user sessions)
- `src/agent_orchestration/therapeutic_safety.py`
- `src/agent_orchestration/enhanced_coordinator.py` (TTA-specific extensions)
- Narrative state management

## Acceptance Criteria

### Code Quality
- [ ] 100% test coverage for all extracted components
- [ ] All tests passing (pytest)
- [ ] Ruff format check passes
- [ ] Ruff lint check passes
- [ ] Pyright type check passes (strict mode)
- [ ] No TTA-specific dependencies in extracted code

### Documentation
- [ ] Comprehensive README.md with:
  - [ ] Feature overview
  - [ ] Installation instructions
  - [ ] Quick start example
  - [ ] Architecture diagram
  - [ ] API reference
- [ ] Docstrings for all public APIs (Google style)
- [ ] Examples directory with runnable code
- [ ] Migration guide for TTA repository

### Testing
- [ ] Unit tests for all coordinators
- [ ] Unit tests for all registries
- [ ] Integration tests with real Redis
- [ ] Fallback tests with FakeRedis (for CI/CD)
- [ ] Performance benchmarks
- [ ] Adversarial tests (edge cases, error conditions)

### Package Structure
- [ ] Valid pyproject.toml with correct dependencies
- [ ] LICENSE file (MIT)
- [ ] CHANGELOG.md
- [ ] .gitignore
- [ ] GitHub Actions CI/CD workflows

## Implementation Plan

### Phase 1: Package Setup (Day 1-2)
- [ ] Create `packages/tta-agent-coordination/` in TTA.dev
- [ ] Set up directory structure
- [ ] Create pyproject.toml
- [ ] Add to TTA.dev workspace configuration
- [ ] Set up CI/CD workflows

### Phase 2: Code Extraction (Day 3-4)
- [ ] Copy RedisMessageCoordinator
- [ ] Copy RedisAgentRegistry
- [ ] Copy circuit breaker patterns
- [ ] Copy retry logic
- [ ] Generalize agent types and models
- [ ] Remove TTA-specific code

### Phase 3: Testing (Day 5-6)
- [ ] Write unit tests (target: 100% coverage)
- [ ] Write integration tests
- [ ] Write adversarial tests
- [ ] Set up FakeRedis fallback for CI
- [ ] Run mutation testing

### Phase 4: Documentation (Day 7)
- [ ] Write README.md
- [ ] Write API documentation
- [ ] Create examples
- [ ] Write migration guide
- [ ] Update CHANGELOG.md

### Phase 5: Review & Merge (Day 8-9)
- [ ] Self-review code
- [ ] Run validation script
- [ ] Create PR in TTA.dev
- [ ] Address review feedback
- [ ] Squash merge to main
- [ ] Tag release v0.1.0

## Dependencies

**Blocked By:**
- #[ISSUE_NUMBER] Fix workspace configuration in TTA repository
- #[ISSUE_NUMBER] Standardize Python version to 3.12+

**Blocks:**
- #[ISSUE_NUMBER] Update TTA repository to use tta-agent-coordination
- #[ISSUE_NUMBER] Publish tta-agent-coordination to PyPI

## Success Metrics

- [ ] Package published to TTA.dev repository
- [ ] 100% test pass rate
- [ ] >80% test coverage (target: 100%)
- [ ] Zero critical security vulnerabilities
- [ ] Documentation complete and accurate
- [ ] Examples run without errors

## Related Documentation

- [TTA.dev Migration Strategy](../docs/TTA_DEV_MIGRATION_STRATEGY.md)
- [Memory System Analysis](../docs/MEMORY_SYSTEM_ANALYSIS.md)
- [Packaging Strategy](../docs/PACKAGING_STRATEGY.md)

## Notes

- This is a **generic, reusable package** - no TTA-specific logic allowed
- Follow TTA.dev quality standards: "Only proven code enters this repository"
- Use semantic versioning: v0.1.0 for initial release
- Ensure backward compatibility for future versions



---
**Logseq:** [[TTA.dev/.github/Issue_template/Memory-system-extraction]]
