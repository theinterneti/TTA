# YAML Schema Reference - Universal Agent Context System

This document specifies the YAML frontmatter schema for instruction files and chat mode files.

---

## Instruction File Schema

### Overview

Instruction files use YAML frontmatter to define selective loading rules and metadata.

### Schema Definition

```yaml
---
applyTo:                          # Required: List of file patterns
  - pattern: "src/module/**/*.py" # Glob pattern for file matching
  - pattern: "**/*_suffix*.py"    # Multiple patterns supported
tags:                             # Required: List of tags
  - "python"                      # Language tag
  - "domain"                      # Domain tag
  - "concern"                     # Concern tag
description: "Brief description"  # Required: One-line description
priority: 1                       # Optional: Loading priority (1-10, default: 5)
version: "1.0.0"                  # Optional: Instruction version
---
```

### Field Specifications

#### `applyTo` (Required)

**Type**: Array of objects  
**Purpose**: Define when this instruction file should be loaded

**Structure**:
```yaml
applyTo:
  - pattern: "glob/pattern/**/*.ext"
```

**Pattern Syntax**:
- `*` - Matches any characters except `/`
- `**` - Matches any characters including `/`
- `?` - Matches single character
- `[abc]` - Matches any character in set
- `{a,b}` - Matches any of the alternatives

**Examples**:
```yaml
# Match all Python files in src/api/
applyTo:
  - pattern: "src/api/**/*.py"

# Match all test files
applyTo:
  - pattern: "tests/**/*.py"
  - pattern: "**/*_test.py"

# Match specific file types
applyTo:
  - pattern: "**/*.{py,pyi}"
```

#### `tags` (Required)

**Type**: Array of strings  
**Purpose**: Categorize and filter instructions

**Recommended Tags**:
- **Language**: `python`, `javascript`, `typescript`, `rust`, etc.
- **Domain**: `api`, `database`, `frontend`, `backend`, etc.
- **Concern**: `security`, `testing`, `performance`, `documentation`, etc.
- **Framework**: `fastapi`, `react`, `django`, `nextjs`, etc.

**Examples**:
```yaml
# API security instructions
tags: ["python", "api", "security", "fastapi"]

# Frontend testing instructions
tags: ["typescript", "frontend", "testing", "react"]

# Database performance instructions
tags: ["python", "database", "performance", "postgresql"]
```

#### `description` (Required)

**Type**: String  
**Purpose**: Brief one-line description of the instruction file

**Guidelines**:
- Keep under 100 characters
- Be specific and actionable
- Describe what the instructions cover

**Examples**:
```yaml
description: "API security and validation requirements for FastAPI endpoints"
description: "React component testing patterns with Jest and React Testing Library"
description: "PostgreSQL query optimization and indexing strategies"
```

#### `priority` (Optional)

**Type**: Integer (1-10)  
**Default**: 5  
**Purpose**: Control loading order when multiple instructions match

**Priority Levels**:
- `1-3`: Low priority (general guidelines)
- `4-6`: Medium priority (standard practices)
- `7-9`: High priority (critical requirements)
- `10`: Critical priority (security, compliance)

**Examples**:
```yaml
# Security instructions (high priority)
priority: 9

# General coding standards (medium priority)
priority: 5

# Optional best practices (low priority)
priority: 2
```

#### `version` (Optional)

**Type**: String (semantic versioning)  
**Default**: "1.0.0"  
**Purpose**: Track instruction file versions

**Format**: `MAJOR.MINOR.PATCH`

**Examples**:
```yaml
version: "1.0.0"  # Initial version
version: "1.1.0"  # Added new guidelines
version: "2.0.0"  # Breaking changes
```

---

## Chat Mode File Schema

### Overview

Chat mode files use YAML frontmatter to define role-specific behavior and tool access.

### Schema Definition

```yaml
---
mode: "role-name"                 # Required: Unique mode identifier
description: "Role description"   # Required: One-line description
cognitive_focus: "Focus areas"    # Required: Cognitive focus areas
security_level: "MEDIUM"          # Required: Security level (LOW, MEDIUM, HIGH)
allowed_tools:                    # Optional: Explicitly allowed tools
  - "tool-name"
denied_tools:                     # Optional: Explicitly denied tools
  - "tool-name"
approval_required:                # Optional: Tools requiring approval
  - "tool-name"
version: "1.0.0"                  # Optional: Chat mode version
---
```

### Field Specifications

#### `mode` (Required)

**Type**: String  
**Purpose**: Unique identifier for the chat mode

**Naming Convention**:
- Use lowercase with hyphens
- Be descriptive and role-specific
- Avoid generic names

**Examples**:
```yaml
mode: "backend-dev"
mode: "frontend-dev"
mode: "qa-engineer"
mode: "security-auditor"
mode: "devops-engineer"
```

#### `description` (Required)

**Type**: String  
**Purpose**: Brief one-line description of the role

**Guidelines**:
- Keep under 100 characters
- Describe the role's primary responsibility
- Be specific and actionable

**Examples**:
```yaml
description: "Backend development and API implementation"
description: "Frontend development with React and TypeScript"
description: "Quality assurance and test automation"
description: "Security auditing and compliance verification"
```

#### `cognitive_focus` (Required)

**Type**: String  
**Purpose**: Define the role's cognitive focus areas

**Guidelines**:
- List 2-4 focus areas
- Separate with commas
- Be specific to the role

**Examples**:
```yaml
cognitive_focus: "Implementation, refactoring, bug fixes"
cognitive_focus: "UI/UX, component design, state management"
cognitive_focus: "Test coverage, quality metrics, automation"
cognitive_focus: "Security, compliance, vulnerability assessment"
```

#### `security_level` (Required)

**Type**: Enum  
**Values**: `LOW`, `MEDIUM`, `HIGH`  
**Purpose**: Define the security level for the role

**Security Levels**:
- **LOW**: Read-only access, no modifications
- **MEDIUM**: Standard development access with restrictions
- **HIGH**: Full access with approval gates

**Examples**:
```yaml
# Read-only auditor
security_level: "LOW"

# Standard developer
security_level: "MEDIUM"

# DevOps with deployment access
security_level: "HIGH"
```

#### `allowed_tools` (Optional)

**Type**: Array of strings  
**Purpose**: Explicitly list allowed MCP tools

**Common Tools**:
- `str-replace-editor` - Modify code
- `save-file` - Create new files
- `view` - View files
- `codebase-retrieval` - Search codebase
- `launch-process` - Run commands
- `github-api` - GitHub operations

**Examples**:
```yaml
# Backend developer
allowed_tools:
  - "str-replace-editor"
  - "save-file"
  - "view"
  - "codebase-retrieval"
  - "launch-process"

# Read-only auditor
allowed_tools:
  - "view"
  - "codebase-retrieval"
```

#### `denied_tools` (Optional)

**Type**: Array of strings  
**Purpose**: Explicitly list denied MCP tools

**Examples**:
```yaml
# Backend developer (no deployment)
denied_tools:
  - "deployProduction"
  - "deleteFiles"

# Security auditor (no modifications)
denied_tools:
  - "str-replace-editor"
  - "save-file"
  - "remove-files"
  - "launch-process"
```

#### `approval_required` (Optional)

**Type**: Array of strings  
**Purpose**: List tools requiring explicit approval

**Examples**:
```yaml
# DevOps engineer
approval_required:
  - "deployProduction"
  - "remove-files"
  - "github-api"
```

#### `version` (Optional)

**Type**: String (semantic versioning)  
**Default**: "1.0.0"  
**Purpose**: Track chat mode versions

**Examples**:
```yaml
version: "1.0.0"  # Initial version
version: "1.1.0"  # Added new tool access
version: "2.0.0"  # Changed security level
```

---

## Validation Rules

### Instruction File Validation

1. **Required Fields**: `applyTo`, `tags`, `description` must be present
2. **Pattern Syntax**: All patterns must be valid glob patterns
3. **Tag Format**: Tags must be lowercase alphanumeric with hyphens
4. **Priority Range**: If specified, must be 1-10
5. **Version Format**: If specified, must follow semantic versioning

### Chat Mode File Validation

1. **Required Fields**: `mode`, `description`, `cognitive_focus`, `security_level` must be present
2. **Mode Format**: Must be lowercase alphanumeric with hyphens
3. **Security Level**: Must be one of `LOW`, `MEDIUM`, `HIGH`
4. **Tool Lists**: No duplicates between `allowed_tools` and `denied_tools`
5. **Version Format**: If specified, must follow semantic versioning

---

## Selective Loading Mechanism

### How It Works

1. **File Change Detection**: AI agent detects file being edited
2. **Pattern Matching**: Matches file path against `applyTo` patterns
3. **Priority Sorting**: Sorts matching instructions by priority
4. **Context Loading**: Loads instructions in priority order
5. **Application**: Applies instructions to current context

### Example Flow

```
User edits: src/api/auth.py

Step 1: Detect file change
  → File: src/api/auth.py

Step 2: Match patterns
  → api-security.instructions.md (pattern: "src/api/**/*.py") ✅
  → python-quality-standards.instructions.md (pattern: "**/*.py") ✅
  → frontend-react.instructions.md (pattern: "src/frontend/**/*.tsx") ❌

Step 3: Sort by priority
  → api-security.instructions.md (priority: 9)
  → python-quality-standards.instructions.md (priority: 5)

Step 4: Load instructions
  → Load api-security.instructions.md
  → Load python-quality-standards.instructions.md

Step 5: Apply to context
  → AI agent now has API security and Python quality guidelines
```

---

## Extension Points

### Custom Fields

You can add custom fields to the YAML frontmatter:

```yaml
---
applyTo:
  - pattern: "src/**/*.py"
tags: ["python"]
description: "Custom instructions"
# Custom fields
team: "backend-team"
reviewer: "john.doe"
last_updated: "2025-10-28"
---
```

### Custom Validation

Implement custom validation logic:

```python
def validate_custom_fields(frontmatter: dict) -> bool:
    """Validate custom fields in frontmatter."""
    if "team" in frontmatter:
        valid_teams = ["backend-team", "frontend-team", "devops-team"]
        if frontmatter["team"] not in valid_teams:
            return False
    return True
```

---

## Best Practices

1. **Be Specific**: Use precise patterns to avoid over-matching
2. **Use Priorities**: Set appropriate priorities for critical instructions
3. **Tag Consistently**: Use consistent tag naming across files
4. **Version Control**: Track versions for breaking changes
5. **Document Changes**: Update descriptions when modifying instructions
6. **Validate Regularly**: Run validation scripts before committing

---

## References

- **Glob Pattern Syntax**: https://en.wikipedia.org/wiki/Glob_(programming)
- **Semantic Versioning**: https://semver.org/
- **YAML Specification**: https://yaml.org/spec/1.2/spec.html

