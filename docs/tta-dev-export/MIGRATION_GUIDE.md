# Migration Guide - Universal Agent Context System

This guide helps you migrate from legacy AI agent context structures to the Universal Agent Context System.

---

## Migration Scenarios

### Scenario 1: From `.augment/` to `.github/`

**Legacy Structure**:
```
.augment/
├── chatmodes/
├── context/
├── workflows/
└── rules/
```

**New Structure**:
```
.github/
├── instructions/
├── chatmodes/
├── prompts/
└── specs/
```

**Migration Steps**:

1. **Create new directory structure**:
```bash
mkdir -p .github/instructions
mkdir -p .github/chatmodes
mkdir -p .github/prompts
mkdir -p .github/specs
```

2. **Migrate chat modes**:
```bash
# Copy chat mode files
cp .augment/chatmodes/*.chatmode.md .github/chatmodes/

# Update frontmatter to new schema
# See YAML_SCHEMA.md for new schema
```

3. **Convert context files to instructions**:
```bash
# Convert .augment/context/*.context.md to .github/instructions/*.instructions.md
# Add YAML frontmatter with applyTo patterns
```

4. **Migrate workflows to prompts**:
```bash
# Copy workflow files
cp .augment/workflows/*.prompt.md .github/prompts/
```

5. **Update references**:
```bash
# Update AGENTS.md to reference new structure
# Update apm.yml to reference new paths
```

---

### Scenario 2: From Monolithic to Modular Instructions

**Legacy**: Single large instruction file (e.g., `INSTRUCTIONS.md`)

**New**: Multiple modular instruction files with selective loading

**Migration Steps**:

1. **Analyze monolithic file**:
```bash
# Identify distinct sections/domains
# Example sections:
# - API Security
# - Testing Requirements
# - Code Quality Standards
# - Database Operations
```

2. **Split into modular files**:
```bash
# Create separate instruction files
cat > .github/instructions/api-security.instructions.md << 'EOF'
---
applyTo:
  - pattern: "src/api/**/*.py"
tags: ["python", "api", "security"]
description: "API security requirements"
---

# API Security Requirements
[Content from API Security section]
EOF

cat > .github/instructions/testing-requirements.instructions.md << 'EOF'
---
applyTo:
  - pattern: "tests/**/*.py"
tags: ["python", "testing"]
description: "Testing requirements and patterns"
---

# Testing Requirements
[Content from Testing section]
EOF
```

3. **Add YAML frontmatter**:
```yaml
---
applyTo:
  - pattern: "relevant/path/**/*.ext"
tags: ["language", "domain", "concern"]
description: "Brief description"
---
```

4. **Validate migration**:
```bash
python scripts/validate-agentic-frontmatter.py
```

---

### Scenario 3: From Agent-Specific to Universal Context

**Legacy**: Separate files for each agent with duplicated content

**New**: Universal context (AGENTS.md) + agent-specific overrides

**Migration Steps**:

1. **Identify common content**:
```bash
# Find content that appears in multiple agent files
# Example: Project overview, architecture, common commands
```

2. **Create AGENTS.md**:
```bash
# Extract common content to AGENTS.md
# This becomes the universal context for all agents
```

3. **Create agent-specific files**:
```bash
# Keep only agent-specific content in:
# - CLAUDE.md (Claude-specific patterns)
# - GEMINI.md (Gemini-specific patterns)
# - .github/copilot-instructions.md (Copilot-specific)
```

4. **Add cross-references**:
```markdown
# In CLAUDE.md
**See AGENTS.md** for universal context and common workflows.

# In GEMINI.md
**See AGENTS.md** for universal context and common workflows.
```

---

### Scenario 4: Adding Quality Gates

**Legacy**: No automated quality gates

**New**: Component maturity workflow with quality gates

**Migration Steps**:

1. **Define maturity stages**:
```yaml
# In apm.yml
quality_gates:
  development:
    coverage: 70
    mutation_score: 75
    complexity: 10
    file_size: 1000
  
  staging:
    coverage: 80
    mutation_score: 80
    complexity: 8
    file_size: 800
  
  production:
    coverage: 85
    mutation_score: 85
    complexity: 6
    file_size: 600
```

2. **Create promotion scripts**:
```bash
# Add to apm.yml
scripts:
  promote:staging: "python scripts/workflow/spec_to_production.py --target staging"
  promote:production: "python scripts/workflow/spec_to_production.py --target production"
```

3. **Document workflow**:
```markdown
# In AGENTS.md
## Component Maturity Workflow

Components progress through three maturity stages:
1. **Development**: Initial implementation
2. **Staging**: Production-ready
3. **Production**: Battle-tested
```

---

## Migration Checklist

### Pre-Migration

- [ ] Backup existing structure
- [ ] Review current agent context files
- [ ] Identify distinct domains/concerns
- [ ] Plan new directory structure
- [ ] Review YAML_SCHEMA.md

### During Migration

- [ ] Create `.github/instructions/` directory
- [ ] Create `.github/chatmodes/` directory
- [ ] Create `AGENTS.md` (universal context)
- [ ] Create `apm.yml` (agent package manager)
- [ ] Migrate chat modes with new frontmatter
- [ ] Split monolithic instructions into modular files
- [ ] Add YAML frontmatter to all instruction files
- [ ] Create agent-specific files (CLAUDE.md, GEMINI.md, etc.)
- [ ] Update cross-references

### Post-Migration

- [ ] Validate YAML frontmatter
- [ ] Test with AI agents
- [ ] Update team documentation
- [ ] Train team on new structure
- [ ] Archive legacy structure
- [ ] Update CI/CD pipelines

---

## Common Migration Issues

### Issue 1: Pattern Matching Not Working

**Problem**: Instruction files not loading when expected

**Solution**: Check glob patterns in `applyTo`

```yaml
# ❌ Incorrect: Missing **
applyTo:
  - pattern: "src/api/*.py"  # Only matches files directly in src/api/

# ✅ Correct: Use ** for recursive matching
applyTo:
  - pattern: "src/api/**/*.py"  # Matches all .py files in src/api/ and subdirectories
```

### Issue 2: Duplicate Content

**Problem**: Same content in multiple files

**Solution**: Extract to AGENTS.md or create shared instruction file

```bash
# Extract common content to AGENTS.md
# Reference from agent-specific files:
# "See AGENTS.md for [topic]"
```

### Issue 3: Chat Mode Not Activating

**Problem**: Chat mode file exists but doesn't activate

**Solution**: Check mode name and frontmatter

```yaml
# ❌ Incorrect: Mode name doesn't match file name
# File: backend-developer.chatmode.md
mode: "backend-dev"  # Mismatch!

# ✅ Correct: Mode name matches file name
# File: backend-dev.chatmode.md
mode: "backend-dev"
```

### Issue 4: Tool Access Conflicts

**Problem**: Tool appears in both allowed and denied lists

**Solution**: Remove from one list (denied takes precedence)

```yaml
# ❌ Incorrect: Conflict
allowed_tools:
  - "str-replace-editor"
denied_tools:
  - "str-replace-editor"  # Conflict!

# ✅ Correct: No conflict
allowed_tools:
  - "str-replace-editor"
denied_tools:
  - "remove-files"
```

---

## Backward Compatibility

### Maintaining Legacy Structure

If you need to maintain backward compatibility:

1. **Keep both structures**:
```
.augment/          # Legacy structure (deprecated)
.github/           # New structure (active)
AGENTS.md          # Universal context
```

2. **Add deprecation notice**:
```markdown
# .augment/README.md

⚠️ **DEPRECATED**: This structure is deprecated.
Please use the new structure in `.github/` and `AGENTS.md`.

See MIGRATION_GUIDE.md for migration instructions.
```

3. **Gradual migration**:
```bash
# Migrate one domain at a time
# Week 1: Migrate API security
# Week 2: Migrate testing requirements
# Week 3: Migrate code quality standards
# etc.
```

---

## Validation After Migration

### 1. Validate YAML Frontmatter

```bash
python scripts/validate-agentic-frontmatter.py
```

### 2. Test with AI Agents

```bash
# Test with Claude
claude "Review AGENTS.md and summarize project architecture"

# Test with Gemini
gemini "Review GEMINI.md and confirm understanding"

# Test with GitHub Copilot
# Open a file and verify Copilot loads .github/copilot-instructions.md
```

### 3. Verify Selective Loading

```bash
# Edit a file that should trigger instruction loading
# Example: Edit src/api/auth.py
# Verify that api-security.instructions.md is loaded

# Ask AI agent:
"What security requirements apply to this file?"
```

### 4. Test Chat Modes

```bash
# Activate a chat mode
/mode backend-dev

# Verify tool access
# Try allowed tools (should work)
# Try denied tools (should be blocked)
```

---

## Rollback Plan

If migration fails, you can rollback:

1. **Restore from backup**:
```bash
# Restore legacy structure
cp -r backup/.augment .
cp backup/INSTRUCTIONS.md .
```

2. **Remove new structure**:
```bash
# Remove new structure
rm -rf .github/instructions
rm -rf .github/chatmodes
rm AGENTS.md apm.yml
```

3. **Revert git changes**:
```bash
git checkout -- .
```

---

## Post-Migration Best Practices

1. **Keep AGENTS.md updated**: Update when architecture changes
2. **Version instruction files**: Use semantic versioning
3. **Document changes**: Update descriptions when modifying
4. **Validate regularly**: Run validation before committing
5. **Train team**: Ensure team understands new structure
6. **Monitor usage**: Track which instructions are loaded most
7. **Iterate**: Refine patterns and priorities based on usage

---

## Support

- **Documentation**: See docs/ directory
- **Examples**: See examples/ directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## Migration Timeline

### Week 1: Planning
- Review current structure
- Identify domains/concerns
- Plan new structure
- Create migration plan

### Week 2: Core Migration
- Create AGENTS.md
- Create apm.yml
- Migrate chat modes
- Split monolithic instructions

### Week 3: Validation & Testing
- Validate YAML frontmatter
- Test with AI agents
- Fix issues
- Document changes

### Week 4: Team Training & Rollout
- Train team on new structure
- Update documentation
- Monitor usage
- Gather feedback

---

## Success Criteria

Migration is successful when:

- [ ] All YAML frontmatter validates
- [ ] AI agents load correct instructions
- [ ] Chat modes activate properly
- [ ] Team understands new structure
- [ ] No critical issues reported
- [ ] Legacy structure archived
- [ ] Documentation updated
- [ ] CI/CD pipelines updated

