# TTA Component Registry

Centralized registry system for tracking TTA component maturity and quality metrics.

## Overview

The Component Registry automatically discovers all TTA components, collects quality metrics (coverage, linting, type checking, security), and provides a unified interface for querying component status and promotion readiness.

## Quick Start

### List All Components

```bash
python scripts/registry_cli.py list
```

Shows all components with their current stage, coverage, and MATURITY.md status.

### Show Component Details

```bash
python scripts/registry_cli.py show carbon
```

Displays detailed information about a specific component including:
- Metadata (name, owner, functional group, stage)
- File paths (source, tests, MATURITY.md)
- Quality metrics (coverage, linting, type checking, security, tests)
- Staging criteria status

### Update Component Metrics

```bash
# Update all components
python scripts/registry_cli.py update-maturity --all

# Update single component
python scripts/registry_cli.py update-maturity carbon

# Dry run (don't save changes)
python scripts/registry_cli.py update-maturity --all --dry-run
```

Collects fresh metrics from pytest, ruff, pyright, and bandit for components.

### Validate Promotion Readiness

```bash
# Validate all components
python scripts/registry_cli.py validate --all

# Validate single component
python scripts/registry_cli.py validate carbon
```

Checks if components meet staging promotion criteria:
- Coverage ≥ 70%
- 0 linting violations
- 0 type errors
- 0 security issues
- All tests passing

### Find Promotion Candidates

```bash
python scripts/registry_cli.py promotion-candidates
```

Lists components that meet all staging promotion criteria.

## Staging Promotion Criteria

A component is ready for staging promotion when it meets ALL of these criteria:

- ✅ **Test Coverage**: ≥70%
- ✅ **Linting**: 0 violations (ruff)
- ✅ **Type Checking**: 0 errors (pyright)
- ✅ **Security**: 0 issues (bandit)
- ✅ **Tests**: All passing (0 failed)

## Workflow

### Before Starting Work on a Component

1. **Check current status**:
   ```bash
   python scripts/registry_cli.py show <component>
   ```

2. **Identify gaps**:
   - Review coverage percentage
   - Check linting/type/security violations
   - Note test failures

3. **Plan remediation**:
   - Estimate effort based on gaps
   - Prioritize blocking issues

### During Development

1. **Make changes** to component code

2. **Update metrics** to see progress:
   ```bash
   python scripts/registry_cli.py update-maturity <component>
   ```

3. **Validate** when ready:
   ```bash
   python scripts/registry_cli.py validate <component>
   ```

### Before Promotion to Staging

1. **Final validation**:
   ```bash
   python scripts/registry_cli.py validate <component>
   ```

2. **Verify all criteria met** (should show ✅)

3. **Update MATURITY.md** with promotion details

4. **Create promotion PR** with validation evidence

## Component Discovery

The registry automatically discovers components by:

1. Scanning `src/components/` for `*_component.py` files
2. Finding associated test files in `tests/`
3. Locating `MATURITY.md` files in component directories
4. Parsing MATURITY.md headers for metadata

**Discovered Components** (as of 2025-10-21):
- agent_orchestration
- app
- carbon
- docker
- gameplay_loop
- llm
- model_management
- narrative_arc_orchestrator
- neo4j
- player_experience

## Registry Cache

The registry stores component metadata and metrics in:
```
scripts/registry/.component_registry.json
```

This file is:
- ✅ Auto-generated (don't edit manually)
- ✅ Gitignored (not committed)
- ✅ Refreshed on each discovery
- ✅ Loaded automatically by CLI

**Cache invalidation**: The cache is considered stale after 24 hours and will trigger automatic re-discovery.

## Integration with Existing Tools

The registry integrates with:

- **`scripts/maturity/metrics_collector.py`**: Collects quality metrics
- **MATURITY.md files**: Parses component metadata
- **pytest**: Test coverage and status
- **ruff**: Linting violations
- **pyright**: Type checking errors
- **bandit**: Security issues

## Troubleshooting

### "Component not found"

The component may not have a `*_component.py` file in `src/components/`. Check:
```bash
find src/components -name "*_component.py"
```

### "No metrics available"

Run metrics collection:
```bash
python scripts/registry_cli.py update-maturity --all
```

### Metrics seem outdated

The cache may be stale. Force refresh:
```bash
# Delete cache and re-run
rm scripts/registry/.component_registry.json
python scripts/registry_cli.py update-maturity --all
```

### Coverage shows 0% but tests exist

Check that:
1. Test file path is correct in registry
2. Tests are actually running (check test output)
3. Coverage JSON is being generated

## Architecture

```
scripts/registry/
├── __init__.py              # Package exports
├── component_registry.py    # Core registry implementation
└── README.md               # This file

scripts/registry_cli.py      # CLI interface
scripts/maturity/
└── metrics_collector.py     # Metrics collection (integrated)
```

**Key Classes**:
- `ComponentMetadata`: Dataclass storing component information
- `ComponentRegistry`: Central registry with discovery and query API

## Future Enhancements

Planned improvements:
- [ ] Pre-commit hook integration for automatic updates
- [ ] CI/CD integration for automated validation
- [ ] MATURITY.md auto-generation from metrics
- [ ] Historical metrics tracking
- [ ] Component dependency graph
- [ ] Promotion workflow automation

## Related Documentation

- **Metrics Collector**: `scripts/maturity/ARCHITECTURE.md`
- **Component Maturity**: `src/components/MATURITY.md` (template)
- **Quality Gates**: Project README

## Support

For issues or questions:
1. Check this README
2. Review component MATURITY.md files
3. Examine registry cache: `scripts/registry/.component_registry.json`
4. Run with verbose logging: `python -v scripts/registry_cli.py ...`
