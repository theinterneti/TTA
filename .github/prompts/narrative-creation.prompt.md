---
mode: agent
model: anthropic/claude-sonnet-4
tools: ['codebase-retrieval', 'find_symbol_Serena', 'editFiles', 'runCommands', 'testFailure']
description: 'Multi-step narrative module creation and integration workflow with validation gates'
---

# Narrative Creation Workflow

**Purpose**: Orchestrate the multi-step process for generating and integrating a new narrative module into TTA.

## Workflow Overview

This workflow guides the creation of a new narrative module from specification to integration, with structured thinking steps and human validation gates.

## Prerequisites

- [ ] Narrative specification document exists in `specs/narratives/`
- [ ] Therapeutic content guidelines reviewed
- [ ] Target audience and safety considerations documented
- [ ] Integration points identified

## Phase 1: Context Loading

### Step 1.1: Review Specification
```markdown
**Action**: Load and analyze narrative specification

**Tools**: codebase-retrieval, find_symbol_Serena

**Checklist**:
- [ ] Read specification document
- [ ] Understand narrative goals
- [ ] Identify therapeutic objectives
- [ ] Note safety requirements
- [ ] List integration points
```

### Step 1.2: Analyze Existing Patterns
```markdown
**Action**: Study existing narrative modules

**Search Queries**:
- "narrative generation patterns"
- "therapeutic content structure"
- "narrative arc implementation"

**Checklist**:
- [ ] Review existing narrative modules
- [ ] Understand narrative engine architecture
- [ ] Identify reusable components
- [ ] Note testing patterns
```

### Step 1.3: Load Context Helpers
```markdown
**Action**: Load relevant context files

**Files to Review**:
- `.augment/context/narrative-design.context.md`
- `.github/instructions/safety.instructions.md`
- `docs/therapeutic-content/narrative-guidelines.md`

**Checklist**:
- [ ] Safety guidelines understood
- [ ] Therapeutic principles reviewed
- [ ] Technical constraints noted
```

## Phase 2: Design

### Step 2.1: Design Narrative Structure
```markdown
**Action**: Create narrative structure design

**Deliverables**:
- Narrative arc definition
- Character profiles
- Scene breakdown
- Therapeutic integration points
- Safety checkpoints

**Validation Criteria**:
- [ ] Aligns with therapeutic goals
- [ ] Includes safety mechanisms
- [ ] Follows TTA narrative patterns
- [ ] Addresses target audience needs
```

### Step 2.2: Design Technical Implementation
```markdown
**Action**: Plan technical implementation

**Components**:
- Narrative data models
- Generation logic
- Integration with narrative engine
- Testing strategy

**Validation Criteria**:
- [ ] Follows SOLID principles
- [ ] Integrates with existing systems
- [ ] Includes error handling
- [ ] Has comprehensive tests
```

## 🚨 VALIDATION GATE 1: Design Review

**STOP**: Before proceeding to implementation, validate the design.

### Review Checklist
- [ ] Narrative structure aligns with specification
- [ ] Therapeutic objectives are clear
- [ ] Safety mechanisms are defined
- [ ] Technical design is sound
- [ ] Integration points are identified
- [ ] Testing strategy is comprehensive

### Required Approvals
- [ ] Therapeutic content review
- [ ] Technical architecture review
- [ ] Safety review

**Action**: Get human approval before proceeding.

---

## Phase 3: Implementation

### Step 3.1: Create Data Models
```markdown
**Action**: Implement narrative data models

**Files to Create**:
- `src/components/narrative_engine/models/[narrative_name].py`

**Requirements**:
- Pydantic models for validation
- Type hints for all fields
- Docstrings for all classes
- Validation logic

**Validation**:
- [ ] Models follow TTA patterns
- [ ] All fields have type hints
- [ ] Validation logic is comprehensive
- [ ] Docstrings are complete
```

### Step 3.2: Implement Generation Logic
```markdown
**Action**: Implement narrative generation logic

**Files to Create**:
- `src/components/narrative_engine/generators/[narrative_name].py`

**Requirements**:
- Async implementation
- Error handling with circuit breakers
- Logging and monitoring
- Safety checks

**Validation**:
- [ ] Follows async patterns
- [ ] Has circuit breaker protection
- [ ] Includes comprehensive logging
- [ ] Implements safety checks
```

### Step 3.3: Integrate with Narrative Engine
```markdown
**Action**: Integrate new narrative module

**Files to Modify**:
- `src/components/narrative_engine/engine.py`
- `src/components/narrative_engine/registry.py`

**Requirements**:
- Register narrative module
- Add routing logic
- Update configuration
- Add monitoring

**Validation**:
- [ ] Module is registered correctly
- [ ] Routing logic is correct
- [ ] Configuration is updated
- [ ] Monitoring is in place
```

## Phase 4: Testing

### Step 4.1: Write Unit Tests
```markdown
**Action**: Create comprehensive unit tests

**Files to Create**:
- `tests/unit/narrative_engine/test_[narrative_name].py`

**Requirements**:
- Test all data models
- Test generation logic
- Test error handling
- Test safety mechanisms
- Coverage ≥70%

**Validation**:
- [ ] All models tested
- [ ] All logic paths tested
- [ ] Error cases tested
- [ ] Safety checks tested
- [ ] Coverage ≥70%
```

### Step 4.2: Write Integration Tests
```markdown
**Action**: Create integration tests

**Files to Create**:
- `tests/integration/narrative_engine/test_[narrative_name]_integration.py`

**Requirements**:
- Test end-to-end narrative generation
- Test integration with narrative engine
- Test database interactions
- Test safety mechanisms

**Validation**:
- [ ] End-to-end flow tested
- [ ] Integration points tested
- [ ] Database operations tested
- [ ] Safety mechanisms tested
```

### Step 4.3: Run Test Suite
```markdown
**Action**: Execute all tests

**Commands**:
```bash
# Run unit tests
uv run pytest tests/unit/narrative_engine/test_[narrative_name].py -v

# Run integration tests
uv run pytest tests/integration/narrative_engine/test_[narrative_name]_integration.py -v

# Check coverage
uv run pytest tests/unit/narrative_engine/test_[narrative_name].py --cov=src/components/narrative_engine/generators/[narrative_name] --cov-report=html
```

**Validation**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Coverage ≥70%
- [ ] No test failures
```

## 🚨 VALIDATION GATE 2: Implementation Review

**STOP**: Before proceeding to integration, validate the implementation.

### Review Checklist
- [ ] All code follows TTA standards
- [ ] All tests pass
- [ ] Coverage ≥70%
- [ ] Safety mechanisms work correctly
- [ ] Error handling is comprehensive
- [ ] Logging is in place
- [ ] Documentation is complete

### Quality Gates
- [ ] Ruff linting passes
- [ ] Pyright type checking passes
- [ ] No security issues
- [ ] File size ≤1,000 lines
- [ ] Complexity ≤10

**Action**: Get human approval before proceeding.

---

## Phase 5: Integration

### Step 5.1: Update Configuration
```markdown
**Action**: Update system configuration

**Files to Modify**:
- `config/tta_config.yaml`
- `config/narrative_modules.yaml`

**Requirements**:
- Add narrative module configuration
- Set default parameters
- Configure safety thresholds

**Validation**:
- [ ] Configuration is valid
- [ ] Parameters are documented
- [ ] Safety thresholds are appropriate
```

### Step 5.2: Update Documentation
```markdown
**Action**: Create/update documentation

**Files to Create/Modify**:
- `docs/narratives/[narrative_name].md`
- `docs/api/narrative-engine.md`

**Requirements**:
- Narrative description
- Usage examples
- API documentation
- Safety guidelines

**Validation**:
- [ ] Documentation is complete
- [ ] Examples are working
- [ ] API is documented
- [ ] Safety guidelines are clear
```

### Step 5.3: Run Integration Validation
```markdown
**Action**: Validate full integration

**Commands**:
```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# Run comprehensive tests
uv run pytest tests/comprehensive_battery/ -k narrative

# Run E2E tests
uv run playwright test tests/e2e/narrative/
```

**Validation**:
- [ ] Services start successfully
- [ ] Comprehensive tests pass
- [ ] E2E tests pass
- [ ] No integration issues
```

## 🚨 VALIDATION GATE 3: Final Review

**STOP**: Before marking complete, perform final validation.

### Final Checklist
- [ ] All tests pass
- [ ] Documentation is complete
- [ ] Configuration is correct
- [ ] Safety mechanisms validated
- [ ] Integration is successful
- [ ] No regressions introduced

### Deployment Readiness
- [ ] Ready for development environment
- [ ] Meets staging promotion criteria
- [ ] Production deployment plan exists

**Action**: Get final approval and mark workflow complete.

---

## Rollback Procedure

If issues are discovered:

1. **Identify Issue**: Document the problem
2. **Assess Impact**: Determine severity
3. **Rollback Changes**: Revert commits if needed
4. **Fix Issue**: Address root cause
5. **Re-test**: Validate fix
6. **Re-deploy**: Deploy corrected version

## Success Criteria

- [ ] Narrative module is fully implemented
- [ ] All tests pass (unit, integration, E2E)
- [ ] Coverage ≥70%
- [ ] Documentation is complete
- [ ] Safety mechanisms are validated
- [ ] Integration is successful
- [ ] No regressions introduced

## References

- **Narrative Guidelines**: `docs/therapeutic-content/narrative-guidelines.md`
- **Safety Instructions**: `.github/instructions/safety.instructions.md`
- **Testing Standards**: `.github/instructions/testing-battery.instructions.md`
- **Component Maturity**: `docs/development/COMPONENT_MATURITY_WORKFLOW.md`

---

**Last Updated**: 2025-10-26
**Status**: Active - Narrative creation workflow with validation gates


---
**Logseq:** [[TTA.dev/.github/Prompts/Narrative-creation.prompt]]
