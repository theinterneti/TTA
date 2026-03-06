# Agent Configuration Schema

This document defines the structure and requirements for custom agent configuration files in `.github/agents/`.

## File Format

Each agent configuration file must:
1. Use YAML frontmatter for metadata
2. Include executable commands section
3. Provide concrete code examples from TTA codebase
4. Define three-tier boundaries (always/ask/never)

## YAML Frontmatter Schema

```yaml
---
agent_name: string              # Required: Agent identifier (e.g., "test-agent")
description: string             # Required: Brief agent purpose
version: string                 # Required: Semantic version (e.g., "1.0.0")
security_level: string          # Required: low | medium | high | critical
boundary_violations_fatal: bool # Required: Halt on boundary violation
audit_enabled: bool             # Required: Enable audit trail logging
---
```

## Required Sections

### 1. Purpose
Clear statement of agent's role and responsibilities.

### 2. Executable Commands (Run First)
Concrete terminal commands the agent uses, organized by category:
- Analysis commands
- Execution commands
- Validation commands
- Reporting commands

### 3. Code Examples from TTA Codebase
Real examples demonstrating:
- Expected patterns
- Best practices
- Common scenarios
- Anti-patterns to avoid

### 4. Scope and Boundaries

#### ✅ ALLOWED (Full Access)
File patterns with read/write permission.

#### 📖 READ-ONLY (Analysis Only)
File patterns for reference only.

#### ❌ DENIED (Never Touch)
File patterns that are off-limits.

### 5. Three-Tier Boundaries

#### ✅ ALWAYS
Actions the agent must perform every time.

#### ⚠️ ASK FIRST
Actions requiring human approval before execution.

#### ❌ NEVER
Actions that are strictly forbidden with rationale.

### 6. Operational Procedures
- Trigger conditions
- Execution workflow
- Approval gates
- Error recovery
- Audit trail format

## Example Agent Structure

```markdown
---
agent_name: example-agent
description: "Example agent for demonstration"
version: 1.0.0
security_level: medium
boundary_violations_fatal: true
audit_enabled: true
---

# @example-agent — Example Agent

## Purpose
Brief description of what this agent does.

## Executable Commands (Run First)

### Analysis
\```bash
# Command 1
uv run tool analyze
\```

## Code Examples from TTA Codebase

### Example 1: Pattern Name
\```python
# Real code from TTA showing expected pattern
\```

## Scope and Boundaries

### ✅ ALLOWED (Full Access)
- path/to/files/**

### 📖 READ-ONLY
- path/to/reference/**

### ❌ DENIED
- secrets/**

## Three-Tier Boundaries

### ✅ ALWAYS
1. Action agent must always perform

### ⚠️ ASK FIRST
1. Action requiring approval

### ❌ NEVER
1. Forbidden action with rationale

## Operational Procedures

### Trigger Conditions
When this agent should execute.

### Execution Workflow
Step-by-step execution flow.

### Approval Gates
When human approval is required.

### Audit Trail
\```json
{
  "agent": "example-agent",
  "action": "example_action",
  "timestamp": "2026-03-06T00:00:00Z"
}
\```
```

## Validation

Before committing an agent file, verify:
- [ ] YAML frontmatter is valid
- [ ] All required sections present
- [ ] Executable commands are concrete and runnable
- [ ] Code examples reference real TTA code
- [ ] Boundaries clearly defined
- [ ] Never/Ask/Always lists are complete
- [ ] Audit trail format specified

---

**Last Updated**: 2026-03-06
**Status**: Active schema definition
