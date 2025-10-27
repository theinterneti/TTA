# Rule Structure Quick Reference

**Last Updated**: 2025-10-27

## File Organization

```
.augment/rules/
├── README.md                              # Overview and structure
├── OPTIMIZATION_SUMMARY.md                # Optimization strategy
├── OPTIMIZATION_REPORT.md                 # Current state and next steps
├── QUICK_REFERENCE.md                     # This file
│
├── Always-On Rules (Core Patterns)
│   ├── avoid-long-files.md                # File size limits (132 bytes)
│   └── Use-your-tools.md                  # Tool usage patterns (241 bytes)
│
├── Auto-Triggered Rules (Context-Specific)
│   ├── docker-dependency-migration.primitive.md  # Docker migration
│   ├── ai-context-management.md                  # Context management
│   ├── use-serena-tools.md                       # Serena MCP usage
│   └── prefer-uvx-for-tools.md                   # Package management
│
└── imported/
    └── copilot-instructions.md            # Legacy import

.augment/workflows/
├── docker-migration.workflow.md           # Docker migration steps
├── context-management.workflow.md         # Multi-session development
├── component-promotion.prompt.md          # Component maturity
├── test-coverage-improvement.prompt.md    # Coverage improvement
├── bug-fix.prompt.md                      # Debugging workflow
└── feature-implementation.prompt.md       # Feature development

.github/instructions/
├── docker-improvements.md                 # Docker architecture review
├── data-separation-strategy.md            # Environment isolation
├── testing-battery.instructions.md        # Testing standards
├── graph-db.instructions.md               # Neo4j patterns
└── safety.instructions.md                 # Security guidelines

Root Files (Always-On)
├── AGENTS.md                              # Universal context (9,517 bytes)
├── CLAUDE.md                              # Claude-specific (9,140 bytes)
├── GEMINI.md                              # Gemini CLI context (7,739 bytes)
└── .github/copilot-instructions.md        # Copilot (8,514 bytes)
```

## When to Use Each Type

### Always-On Rules
**Use for**: Core patterns that apply to every interaction
**Examples**: File size limits, SOLID principles, package management

### Auto-Triggered Rules
**Use for**: Context-specific patterns that apply to certain tasks
**Examples**: Docker migration, context management, Serena tools

**How to trigger**: Mention keywords in `applies_to` field
- "docker-compose" → `docker-dependency-migration.primitive.md`
- "multi-session" → `ai-context-management.md`
- "code navigation" → `use-serena-tools.md`

### Workflow Files
**Use for**: Detailed step-by-step procedures
**Examples**: Migration workflows, testing strategies, deployment procedures

**How to reference**: Rules reference workflows for detailed steps
- Rule: Quick reference and patterns
- Workflow: Detailed procedures and examples

### Instruction Files
**Use for**: File-specific or component-specific guidelines
**Examples**: Testing standards for `tests/**`, Docker patterns for `docker/**`

**How to apply**: YAML frontmatter with `applyTo` patterns
```yaml
---
applyTo: ["tests/**", "src/**/test_*.py"]
---
```

## Auto-Trigger Examples

### Example 1: Docker Migration
**User Request**: "Update docker-compose references in scripts"

**Triggered**:
- `docker-dependency-migration.primitive.md` (matches "docker-compose")

**Loaded**:
- Quick reference and patterns from rule
- References `docker-migration.workflow.md` for detailed steps

### Example 2: Multi-Session Development
**User Request**: "I'm working on a complex feature that will take multiple sessions"

**Triggered**:
- `ai-context-management.md` (matches "multi-session")

**Loaded**:
- Quick commands and importance scores from rule
- References `context-management.workflow.md` for detailed patterns

### Example 3: Code Navigation
**User Request**: "Find all usages of the CircuitBreaker class"

**Triggered**:
- `use-serena-tools.md` (matches "find usages")

**Loaded**:
- Serena tool patterns and examples from rule

## Creating New Rules

### 1. Determine Rule Type

**Always-On**: Core pattern that applies to every interaction?
- Yes → Add to `.augment/rules/` without auto-trigger
- No → Continue to next question

**Auto-Triggered**: Context-specific pattern?
- Yes → Add YAML frontmatter with `applies_to` conditions
- No → Continue to next question

**Workflow**: Detailed step-by-step procedure?
- Yes → Create in `.augment/workflows/`
- No → Continue to next question

**Instruction**: File-specific or component-specific?
- Yes → Create in `.github/instructions/` with `applyTo` patterns

### 2. Add YAML Frontmatter

```yaml
---
rule_type: <type>
category: <category>
applies_to: ["keyword1", "keyword2", "pattern"]
auto_trigger: true
version: 1.0.0
created: YYYY-MM-DD
maturity: <development|staging|production>
tags: [tag1, tag2, tag3]
---
```

### 3. Structure Content

**Rule File** (Quick Reference):
- Overview (1-2 sentences)
- When to use (bullet points)
- Quick commands (code blocks)
- Reference to workflow (link)

**Workflow File** (Detailed Procedure):
- Purpose and when to use
- Step-by-step instructions
- Examples and patterns
- Success criteria
- Related resources

### 4. Reference Workflow

In rule file:
```markdown
**Quick Start**: See `.augment/workflows/my-workflow.workflow.md` for detailed steps.
```

In workflow file:
```markdown
**Related Rule**: `.augment/rules/my-rule.md` (quick reference)
```

## Best Practices

### Keep Rules Concise
- Quick reference only (target: <5,000 bytes)
- Reference workflows for details
- Avoid duplicating examples

### Create Workflows for Procedures
- Step-by-step instructions
- Detailed examples
- Troubleshooting guides
- Success criteria

### Use Auto-Triggers Wisely
- Choose specific, relevant keywords
- Avoid overly broad triggers
- Test with sample prompts

### Maintain Single Source of Truth
- Don't duplicate content across files
- Reference authoritative source
- Update in one place only

## Troubleshooting

### Rule Not Loading
**Symptom**: Expected rule not loaded for user request

**Solutions**:
1. Check `applies_to` keywords match user request
2. Verify YAML frontmatter is valid
3. Check `auto_trigger: true` is set
4. Test with explicit keyword mention

### Workflow Not Found
**Symptom**: Rule references workflow that doesn't exist

**Solutions**:
1. Verify workflow file exists in `.augment/workflows/`
2. Check file path in rule is correct
3. Verify workflow file has `.workflow.md` extension

### Duplicate Content
**Symptom**: Same content in multiple files

**Solutions**:
1. Identify authoritative source
2. Remove duplicates from other files
3. Add references to authoritative source
4. Update OPTIMIZATION_SUMMARY.md

## Related Documentation

- `OPTIMIZATION_SUMMARY.md` - Detailed optimization strategy
- `OPTIMIZATION_REPORT.md` - Current state and next steps
- `README.md` - Overview and structure
- `.augment/workflows/` - Workflow files

---

**For questions or issues, see OPTIMIZATION_SUMMARY.md or OPTIMIZATION_REPORT.md**
