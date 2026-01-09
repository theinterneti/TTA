# Agentic Primitives Consistency Management

**Date**: 2025-10-26
**Status**: Recommended Solutions
**Context**: Maintaining consistency across `.github/` agentic primitives files

## Problem Statement

The TTA project now has interconnected configuration and documentation files in the `.github/` directory structure:

- **Root Configuration**: `apm.yml`, `AGENTS.md`, `CLAUDE.md`
- **Instruction Files**: `.github/instructions/*.instructions.md`
- **Chat Modes**: `.github/chatmodes/*.chatmode.md`
- **Workflow Files**: `.github/prompts/*.prompt.md`
- **Specification Templates**: `.github/specs/*.spec.md`

**Challenges**:
1. **Cross-file consistency**: When information is updated in one file (e.g., new MCP server in `apm.yml`), related files need updates
2. **Conflict detection**: Identifying contradictory information or outdated references
3. **Update propagation**: Understanding which files need updates when a change is made

## Research Summary

### Tools Evaluated

1. **Yamale** - YAML schema validation with Python
2. **markdownlint-cli2** - Markdown linting with custom rules
3. **Dynaconf** - Configuration management with validation
4. **Existing TTA Tooling** - Ruff, Pyright, pre-commit hooks

## Recommended Solutions

### Solution 1: Schema-Based Validation with Yamale ⭐ **RECOMMENDED**

**Ease of Implementation**: ⭐⭐⭐⭐⭐ (Easiest)
**Maintenance Overhead**: Low
**Integration**: Seamless with existing Python tooling

#### Description
Use Yamale to validate YAML frontmatter in all agentic primitive files against defined schemas. This ensures structural consistency and catches missing required fields.

#### Pros
- ✅ **Python-native**: Integrates with existing `uv` tooling
- ✅ **Declarative schemas**: Easy to read and maintain
- ✅ **Fast validation**: Runs in seconds
- ✅ **Pre-commit integration**: Catches issues before commit
- ✅ **Clear error messages**: Pinpoints exact validation failures
- ✅ **Supports includes**: Can validate nested structures

#### Cons
- ❌ **YAML frontmatter only**: Doesn't validate markdown content
- ❌ **No cross-file validation**: Can't check references between files
- ❌ **Manual schema maintenance**: Schemas need updates when structure changes

#### Implementation Steps

**Step 1: Install Yamale**
```bash
uv add --dev yamale
```

**Step 2: Create Schema Files**

Create `.github/schemas/instruction.schema.yaml`:
```yaml
applyTo: list(str(), min=1, required=True)
priority: enum('critical', 'high', 'medium', 'low', required=True)
category: str(required=True)
description: str(required=True)
```

Create `.github/schemas/chatmode.schema.yaml`:
```yaml
mode: str(required=True)
model: str(required=True)
tools: include('tools-config', required=True)
description: str(required=True)
---
tools-config:
  allowed: list(str(), min=1, required=True)
  denied: list(str(), required=False)
```

Create `.github/schemas/prompt.schema.yaml`:
```yaml
mode: enum('agent', 'workflow', required=True)
model: str(required=True)
tools: list(str(), min=1, required=True)
description: str(required=True)
```

**Step 3: Create Validation Script**

Create `scripts/validate-agentic-frontmatter.py`:
```python
#!/usr/bin/env python3
"""Validate YAML frontmatter in agentic primitive files."""

import sys
from pathlib import Path
import yamale
import yaml

def extract_frontmatter(file_path: Path) -> dict | None:
    """Extract YAML frontmatter from markdown file."""
    with open(file_path) as f:
        content = f.read()

    if not content.startswith('---\n'):
        return None

    # Find second ---
    end_idx = content.find('\n---\n', 4)
    if end_idx == -1:
        return None

    frontmatter = content[4:end_idx]
    return yaml.safe_load(frontmatter)

def validate_file(file_path: Path, schema_path: Path) -> tuple[bool, list[str]]:
    """Validate a file's frontmatter against schema."""
    frontmatter = extract_frontmatter(file_path)
    if frontmatter is None:
        return False, [f"No YAML frontmatter found in {file_path}"]

    # Create temporary YAML file for validation
    temp_file = file_path.with_suffix('.temp.yaml')
    with open(temp_file, 'w') as f:
        yaml.dump(frontmatter, f)

    try:
        schema = yamale.make_schema(schema_path)
        data = yamale.make_data(temp_file)
        yamale.validate(schema, data)
        return True, []
    except yamale.YamaleError as e:
        errors = []
        for result in e.results:
            for error in result.errors:
                errors.append(f"{file_path}: {error}")
        return False, errors
    finally:
        temp_file.unlink(missing_ok=True)

def main():
    """Main validation function."""
    root = Path(__file__).parent.parent
    schemas_dir = root / '.github' / 'schemas'

    # Define file patterns and their schemas
    validations = [
        ('.github/instructions/*.instructions.md', 'instruction.schema.yaml'),
        ('.github/chatmodes/*.chatmode.md', 'chatmode.schema.yaml'),
        ('.github/prompts/*.prompt.md', 'prompt.schema.yaml'),
    ]

    all_passed = True
    for pattern, schema_name in validations:
        schema_path = schemas_dir / schema_name
        for file_path in root.glob(pattern):
            passed, errors = validate_file(file_path, schema_path)
            if not passed:
                all_passed = False
                for error in errors:
                    print(f"❌ {error}")
            else:
                print(f"✅ {file_path.name}")

    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
```

**Step 4: Add to Pre-commit**

Update `.pre-commit-config.yaml`:
```yaml
  - repo: local
    hooks:
      - id: validate-agentic-frontmatter
        name: Validate agentic primitives frontmatter
        entry: python scripts/validate-agentic-frontmatter.py
        language: system
        files: ^\.github/(instructions|chatmodes|prompts)/.*\.md$
        pass_filenames: false
```

**Step 5: Add to Quality Gates**

Update `scripts/validate-quality-gates.sh`:
```bash
# Add to quality gates
echo -e "${BLUE}Validating Agentic Primitives...${NC}"
if python scripts/validate-agentic-frontmatter.py; then
    echo -e "${GREEN}✓ Agentic primitives validation passed${NC}"
else
    echo -e "${RED}✗ Agentic primitives validation failed${NC}"
    FAILED_GATES+=("Agentic primitives validation")
fi
```

---

### Solution 2: Custom Markdown Linting Rules

**Ease of Implementation**: ⭐⭐⭐⭐ (Easy)
**Maintenance Overhead**: Medium
**Integration**: Requires Node.js tooling

#### Description
Use markdownlint-cli2 with custom rules to validate markdown content, cross-references, and consistency.

#### Pros
- ✅ **Content validation**: Can check markdown structure and content
- ✅ **Custom rules**: Flexible validation logic
- ✅ **Fast**: Runs quickly on large codebases
- ✅ **Pre-commit integration**: Catches issues early

#### Cons
- ❌ **Node.js dependency**: Adds JavaScript tooling to Python project
- ❌ **Complex custom rules**: Requires JavaScript knowledge
- ❌ **Limited cross-file validation**: Difficult to implement

#### Implementation Steps

**Step 1: Install markdownlint-cli2**
```bash
npm install --save-dev markdownlint-cli2
```

**Step 2: Create Custom Rules**

Create `.markdownlint-cli2/custom-rules.js`:
```javascript
module.exports = [{
  names: ["agentic-frontmatter"],
  description: "Validate YAML frontmatter in agentic primitives",
  tags: ["frontmatter"],
  function: function rule(params, onError) {
    const lines = params.lines;
    if (lines[0] !== "---") {
      onError({
        lineNumber: 1,
        detail: "Missing YAML frontmatter"
      });
    }
  }
}];
```

**Step 3: Configure markdownlint**

Create `.markdownlint-cli2.jsonc`:
```json
{
  "config": {
    "default": true,
    "MD013": false
  },
  "customRules": [".markdownlint-cli2/custom-rules.js"],
  "globs": [".github/**/*.md"]
}
```

---

### Solution 3: Python-Based Cross-File Validator

**Ease of Implementation**: ⭐⭐⭐ (Moderate)
**Maintenance Overhead**: Medium-High
**Integration**: Excellent with existing tooling

#### Description
Build a custom Python validator that checks cross-file references, consistency, and dependencies.

#### Pros
- ✅ **Full control**: Can implement any validation logic
- ✅ **Cross-file validation**: Can check references between files
- ✅ **Python-native**: Integrates seamlessly
- ✅ **Extensible**: Easy to add new checks

#### Cons
- ❌ **Custom code**: Requires development and maintenance
- ❌ **Testing overhead**: Needs comprehensive tests
- ❌ **Complexity**: More complex than schema-based validation

#### Implementation Outline

Create `scripts/validate-agentic-consistency.py`:
```python
#!/usr/bin/env python3
"""Validate consistency across agentic primitive files."""

from pathlib import Path
import yaml
from typing import Dict, List, Set

class ConsistencyValidator:
    def __init__(self, root: Path):
        self.root = root
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_mcp_servers(self):
        """Ensure MCP servers in apm.yml are documented in AGENTS.md."""
        # Load apm.yml
        apm_path = self.root / 'apm.yml'
        with open(apm_path) as f:
            apm = yaml.safe_load(f)

        mcp_servers = set(apm.get('mcpServers', {}).keys())

        # Check AGENTS.md
        agents_path = self.root / 'AGENTS.md'
        with open(agents_path) as f:
            agents_content = f.read()

        for server in mcp_servers:
            if server not in agents_content:
                self.warnings.append(
                    f"MCP server '{server}' in apm.yml not documented in AGENTS.md"
                )

    def validate_tool_references(self):
        """Ensure tools in chat modes are valid."""
        # Define valid tools
        valid_tools = {
            'fetch', 'search', 'githubRepo', 'codebase-retrieval',
            'editFiles', 'runCommands', 'deleteFiles',
            'read_memory_Serena', 'write_memory_Serena',
            # ... add all valid tools
        }

        # Check chat modes
        for chatmode_file in (self.root / '.github' / 'chatmodes').glob('*.chatmode.md'):
            frontmatter = self.extract_frontmatter(chatmode_file)
            if frontmatter and 'tools' in frontmatter:
                tools = frontmatter['tools']
                allowed = set(tools.get('allowed', []))
                denied = set(tools.get('denied', []))

                invalid_allowed = allowed - valid_tools
                invalid_denied = denied - valid_tools

                if invalid_allowed:
                    self.errors.append(
                        f"{chatmode_file.name}: Invalid allowed tools: {invalid_allowed}"
                    )
                if invalid_denied:
                    self.errors.append(
                        f"{chatmode_file.name}: Invalid denied tools: {invalid_denied}"
                    )
```

---

### Solution 4: Documentation Generation from Source

**Ease of Implementation**: ⭐⭐ (Complex)
**Maintenance Overhead**: Low (after setup)
**Integration**: Requires build step

#### Description
Generate documentation files (AGENTS.md, CLAUDE.md) from source configuration files (apm.yml, instruction files) to ensure single source of truth.

#### Pros
- ✅ **Single source of truth**: Configuration drives documentation
- ✅ **Always in sync**: Generated files can't be out of date
- ✅ **Reduced maintenance**: No manual synchronization

#### Cons
- ❌ **Complex setup**: Requires templating system
- ❌ **Build step**: Adds to development workflow
- ❌ **Less flexible**: Generated content may be rigid

---

## Recommended Approach for TTA

**Primary Solution**: **Solution 1 (Schema-Based Validation with Yamale)** ⭐

**Rationale**:
1. **Easiest to implement**: Minimal code, declarative schemas
2. **Python-native**: Fits existing tooling (uv, pytest, pre-commit)
3. **Fast**: Runs in seconds, suitable for pre-commit hooks
4. **Low maintenance**: Schemas are simple to update
5. **Clear errors**: Developers get actionable feedback

**Supplementary Solution**: **Solution 3 (Cross-File Validator)** for advanced checks

**Implementation Priority**:
1. **Week 1**: Implement Yamale validation for YAML frontmatter
2. **Week 2**: Add cross-file validator for MCP servers and tool references
3. **Week 3**: Integrate into CI/CD pipeline
4. **Week 4**: Add documentation and developer guide

## Next Steps

1. **Create schemas directory**: `.github/schemas/`
2. **Define schemas**: For instructions, chat modes, prompts, specs
3. **Implement validation script**: `scripts/validate-agentic-frontmatter.py`
4. **Add pre-commit hook**: Validate on commit
5. **Update quality gates**: Add to `validate-quality-gates.sh`
6. **Document process**: Add to `CONTRIBUTING.md`

## References

- **Yamale Documentation**: https://github.com/23andme/yamale
- **markdownlint-cli2**: https://github.com/davidanson/markdownlint-cli2
- **Dynaconf**: https://github.com/dynaconf/dynaconf
- **TTA Quality Gates**: `docs/development/QUALITY_GATES.md`

---

**Last Updated**: 2025-10-26
**Status**: Recommended - Ready for implementation


---
**Logseq:** [[TTA.dev/Docs/Development/Agentic_primitives_consistency]]
