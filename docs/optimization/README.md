# TTA Agentic Primitives - Rules & Patterns

This directory contains reusable primitives and rules that codify proven patterns for common development workflows. These are designed to be used by AI agents and human developers alike.

## Rule Structure (Optimized)

**Status**: Phase 1 Complete - Auto-trigger system implemented (see `OPTIMIZATION_SUMMARY.md`)

### Rule Types

1. **Always-On Rules**: Core patterns loaded for every interaction (target: <30,000 bytes)
2. **Auto-Triggered Rules**: Context-specific rules loaded when user request matches `applies_to` conditions
3. **Workflow Files**: Detailed procedures referenced by rules, loaded on-demand
4. **Instruction Files**: File-specific rules loaded based on file patterns

### Auto-Trigger System

Rules with YAML frontmatter are loaded only when relevant:

```yaml
---
applies_to: ["docker", "docker-compose", "service management"]
auto_trigger: true
version: 1.0.0
---
```

**Example**: `docker-dependency-migration.primitive.md` loads only when user mentions Docker-related work.

## What are Primitives?

**Primitives** are documented, repeatable patterns for solving specific types of problems. They:
- Capture proven workflows
- Reduce cognitive load
- Ensure consistency
- Enable reuse across contexts
- Support both AI agents and humans
- **Auto-trigger** when user request matches their domain

## Available Primitives

### Infrastructure Primitives

#### `docker-dependency-migration.primitive.md`
**Purpose**: Systematically migrate project dependencies after Docker architecture changes

**When to Use**:
- After major Docker refactoring
- When consolidating compose files
- When introducing new orchestration patterns

**Key Phases**:
1. Discovery - Find all dependencies
2. Critical Path - Update core files
3. Enhancement - Add new capabilities
4. Documentation - Create guides
5. Tooling - Build migration aids

**Real Example**: TTA Docker migration (42 → 5 compose files, 6 core files updated)

---

## Using Primitives

### For AI Agents

Reference primitives in prompts:
```
Use the docker-dependency-migration primitive to update all
references from old compose structure to new architecture.
```

Primitives provide:
- Step-by-step procedures
- File patterns to search for
- Update templates
- Validation checklists
- Success criteria

### For Human Developers

Read primitives to:
- Understand proven patterns
- Follow consistent procedures
- Avoid common pitfalls
- Create migration plans
- Document your own patterns

---

## Primitive Structure

Each primitive follows this structure:

```markdown
---
primitive_type: <type>
category: <category>
applies_to: [<contexts>]
version: <semver>
created: <date>
last_updated: <date>
maturity: <development|staging|production>
tags: [<tags>]
---

# Primitive Name

## Overview
- Purpose
- When to Use
- Expected Outcome

## Pattern
- Phase-by-phase breakdown
- Decision points
- Implementation details

## Implementation Checklist
- Actionable steps
- Validation points

## Common Patterns
- Before/after examples
- Anti-patterns

## Success Criteria
- Measurable outcomes

## Real-World Example
- Actual usage from TTA
- Results achieved

## Related Primitives
- Cross-references
```

---

## Creating New Primitives

### When to Create a Primitive

Create a primitive when you've:
1. Solved a problem that will recur
2. Identified a clear, repeatable pattern
3. Validated the approach works
4. Want to ensure consistency

### Primitive Creation Checklist

- [ ] Clear purpose and scope
- [ ] Step-by-step procedure
- [ ] Before/after examples
- [ ] Anti-patterns documented
- [ ] Success criteria defined
- [ ] Real-world validation
- [ ] Related primitives linked
- [ ] YAML frontmatter complete

### Primitive Maturity Levels

- **Development**: Being tested, may change
- **Staging**: Validated, ready for wider use
- **Production**: Proven, stable, recommended

---

## Primitive Categories

### Infrastructure
- Docker architecture
- Service orchestration
- Configuration management
- Deployment patterns

### Development
- Refactoring workflows
- Testing strategies
- Code organization
- Quality gates

### Documentation
- Migration guides
- API documentation
- Setup instructions
- Troubleshooting

### Integration
- AI agent context
- Tool configuration
- Workflow automation
- CI/CD pipelines

---

## Contributing Primitives

1. **Identify Pattern**: Notice a repeatable workflow
2. **Validate**: Use it successfully 2-3 times
3. **Document**: Create primitive following structure
4. **Test**: Verify with AI agent and human
5. **Submit**: Add to this directory
6. **Maintain**: Update as patterns evolve

---

## Examples of Good Primitives

✅ **Specific**: "Docker dependency migration" not "updating things"
✅ **Actionable**: Step-by-step with clear outcomes
✅ **Validated**: Includes real-world example
✅ **Complete**: Covers discovery, implementation, validation
✅ **Reusable**: Can be applied to similar situations

❌ **Too Vague**: "Make things better"
❌ **Too Specific**: "Update line 42 of file X"
❌ **Untested**: No real-world validation
❌ **Incomplete**: Missing key phases
❌ **One-off**: Can't be reused elsewhere

---

## Primitive Naming Convention

Format: `<category>-<specific-task>.primitive.md`

Examples:
- `docker-dependency-migration.primitive.md`
- `api-versioning-strategy.primitive.md`
- `test-coverage-improvement.primitive.md`
- `documentation-restructuring.primitive.md`

---

## Related Resources

- **Workflows** (`.augment/workflows/`): Multi-step procedures
- **Chatmodes** (`.augment/chatmodes/`): AI agent role definitions
- **Instructions** (`.github/instructions/`): Project-specific rules
- **Memory** (`.augment/memory/`): Project knowledge base

---

## Version History

- **1.0.0** (2025-10-26): Initial structure with docker-dependency-migration primitive

---

## Future Additions

Planned primitives:
- `api-versioning-strategy.primitive.md`
- `test-coverage-improvement.primitive.md`
- `documentation-restructuring.primitive.md`
- `ci-cd-pipeline-migration.primitive.md`
- `dependency-upgrade-workflow.primitive.md`
- `component-maturity-promotion.primitive.md`
