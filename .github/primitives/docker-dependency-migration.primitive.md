---
primitive_type: infrastructure_migration
category: docker
applies_to: ["docker", "docker-compose", "service management", "infrastructure migration", "compose file"]
auto_trigger: true
version: 1.0.0
created: 2025-10-26
last_updated: 2025-10-27
maturity: production
tags: [docker, migration, infrastructure, dependency-update, consolidation]
workflow_reference: ".augment/workflows/docker-migration.workflow.md"
---

# Docker Dependency Migration Primitive

**Auto-triggered when**: User mentions docker-compose, service management, infrastructure migration, or compose files.

**Detailed Workflow**: See `.augment/workflows/docker-migration.workflow.md` for step-by-step procedures.

## Overview

**Purpose**: Systematically migrate project dependencies after Docker architecture changes.

**Expected Outcome**: All files updated to new Docker architecture with migration guides and tooling.

## Pattern Overview

### Phase 1: Discovery
1. Search for all docker-compose references
2. Categorize by type and priority
3. Create dependency matrix

### Phase 2: Update Core Dependencies
1. Update cleanup/test scripts
2. Update configuration files
3. Update AI agent context
4. Update integration documentation

### Phase 3: Enhance Integration
1. Update APM configuration
2. Ensure consistent context across AI agents
3. Simplify command patterns

### Phase 4: Documentation
1. Create summary document
2. Create detailed report
3. Create navigation index
4. Document breaking changes

### Phase 5: Tooling
1. Create migration status checker
2. Make scripts executable
3. Test all tooling

## Common Update Patterns

### Pattern 1: Script Migration
**Before**:
```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

**After**:
```bash
bash docker/scripts/tta-docker.sh dev down -v
bash docker/scripts/tta-docker.sh dev up -d
```

### Pattern 2: Documentation Updates
**Before**:
```markdown
## Quick Start
\`\`\`bash
docker-compose -f docker-compose.dev.yml up -d
\`\`\`
```

**After**:
```markdown
## Quick Start
\`\`\`bash
bash docker/scripts/tta-docker.sh dev up -d
\`\`\`
```

### Pattern 3: APM Integration
**Add to `apm.yml`**:
```yaml
services:
  start:
    description: "Start development services"
    command: "bash docker/scripts/tta-docker.sh dev up -d"
```

## Success Criteria

### Immediate Success
- [ ] All critical path files updated
- [ ] No broken references in active scripts
- [ ] Development workflow functional
- [ ] APM commands working

### Short-term Success
- [ ] All documentation updated
- [ ] Team onboarded to new patterns
- [ ] Migration tools created
- [ ] Breaking changes documented

### Long-term Success
- [ ] Old files archived
- [ ] No legacy references remain
- [ ] New patterns consistently used
- [ ] Migration primitive documented

## Anti-Patterns (What NOT to Do)

❌ **Don't** update files without understanding context
❌ **Don't** skip documentation updates
❌ **Don't** forget to update AI agent context
❌ **Don't** leave broken references
❌ **Don't** ignore APM integration opportunities
❌ **Don't** forget to create migration tooling
❌ **Don't** skip validation testing

## Implementation Checklist

### Discovery Phase
- [ ] Search for all docker-compose references
- [ ] Categorize dependencies by type and priority
- [ ] Create dependency matrix
- [ ] Estimate effort and impact

### Critical Path Updates
- [ ] Update cleanup/test scripts
- [ ] Update configuration files (apm.yml, etc.)
- [ ] Update AI agent context files
- [ ] Update integration documentation
- [ ] Validate all changes

### Enhancement Phase
- [ ] Add new APM commands (status, restart)
- [ ] Ensure consistent context across AI agents
- [ ] Simplify command patterns
- [ ] Test new workflows

### Documentation Phase
- [ ] Create summary document
- [ ] Create detailed report
- [ ] Create navigation index
- [ ] Document breaking changes
- [ ] Provide migration examples

### Tooling Phase
- [ ] Create migration status checker
- [ ] Make scripts executable
- [ ] Test all tooling
- [ ] Document tool usage

### Validation Phase
- [ ] Manual testing of updated scripts
- [ ] APM command testing
- [ ] AI agent context verification
- [ ] Documentation review
- [ ] Team communication

## Variations

### Variation 1: Partial Migration
When full migration isn't feasible immediately:
1. Update critical path only
2. Add compatibility layer
3. Deprecate old patterns gradually
4. Document migration timeline

### Variation 2: Multi-Environment Migration
When different environments use different patterns:
1. Create environment-specific updates
2. Maintain environment parity documentation
3. Test each environment separately
4. Document environment differences

### Variation 3: Incremental Documentation
When documentation updates can be done separately:
1. Complete code updates first
2. Create migration documentation
3. Update developer docs incrementally
4. Archive old documentation

## Related Primitives

- `docker-compose-consolidation.primitive.md` - Consolidating multiple compose files
- `infrastructure-refactoring.primitive.md` - General infrastructure refactoring
- `dependency-update.primitive.md` - Updating project dependencies
- `documentation-migration.primitive.md` - Migrating documentation

## Real-World Example: TTA Docker Migration

**Context**: TTA had 42 docker-compose files, needed consolidation to 5 files with new management script.

**Execution**:
1. **Discovery**: Found 60+ references across scripts, docs, workflows
2. **Priority**: Identified 6 P0 files (cleanup scripts, apm.yml, AI context)
3. **Updates**: Systematic file-by-file updates with validation
4. **Enhancement**: Added 2 new APM commands (status, restart)
5. **Documentation**: Created 3 comprehensive guides + migration checker
6. **Result**: 6 core files updated, development workflow streamlined

**Files Updated**:
- `scripts/cleanup/reset-test-data.sh`
- `scripts/cleanup/wipe-dev-data.sh`
- `apm.yml`
- `.github/copilot-instructions.md`
- `AGENTS.md`
- `VS_CODE_DATABASE_INTEGRATION.md`

**Outcome**: Core migration complete, ~12 additional files identified for future updates (non-blocking).

## Tips & Best Practices

### Discovery
- Use regex searches for pattern matching
- Check both code and documentation
- Don't forget configuration files
- Look for indirect references (scripts calling scripts)

### Updates
- Always maintain 3-5 lines of context
- Test each update immediately
- Update related files together
- Validate with lint/type checks

### Documentation
- Create navigation/index documents
- Provide before/after examples
- Document breaking changes clearly
- Include quick reference commands

### Tooling
- Make scripts executable
- Include help/usage information
- Provide dry-run modes
- Test thoroughly before sharing

### Communication
- Update AI agent context immediately
- Document new patterns clearly
- Provide migration guides
- Support team during transition

---

**Last Updated**: 2025-10-27
**Status**: Active - TTA Docker migration primitive
**Detailed Workflow**: `.augment/workflows/docker-migration.workflow.md`
