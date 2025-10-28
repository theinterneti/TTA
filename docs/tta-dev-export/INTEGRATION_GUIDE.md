# Integration Guide - Universal Agent Context System

This guide provides step-by-step instructions for adopting the Universal Agent Context System in your project.

---

## Prerequisites

- Git repository for your project
- At least one AI agent (Claude, Gemini, GitHub Copilot, or Augment)
- Basic understanding of YAML and markdown
- (Optional) MCP servers for enhanced capabilities

---

## Step 1: Install Core Files

### 1.1 Copy Universal Context

```bash
# Copy AGENTS.md to your project root
cp universal-agent-context-system/AGENTS.md /path/to/your/project/

# Customize for your project
# Edit AGENTS.md and replace TTA-specific content with your project details
```

**What to customize in AGENTS.md**:
- Project Overview section (name, description, tech stack)
- Core Architecture Patterns (your architecture)
- Key Directories (your directory structure)
- Common Commands (your development commands)
- Related Documentation (your docs)

### 1.2 Copy Agent Package Manager Config

```bash
# Copy apm.yml to your project root
cp universal-agent-context-system/apm.yml /path/to/your/project/

# Customize for your project
# Edit apm.yml with your project details
```

**What to customize in apm.yml**:
- `name`: Your project name
- `version`: Your project version
- `description`: Your project description
- `scripts`: Your development scripts
- `mcp_servers`: Your MCP server dependencies
- `environment`: Your environment variables
- `quality_gates`: Your quality thresholds

### 1.3 Copy Agent-Specific Files (Optional)

```bash
# For Claude users
cp universal-agent-context-system/CLAUDE.md /path/to/your/project/

# For Gemini users
cp universal-agent-context-system/GEMINI.md /path/to/your/project/

# For GitHub Copilot users
mkdir -p /path/to/your/project/.github
cp universal-agent-context-system/.github/copilot-instructions.md \
   /path/to/your/project/.github/
```

---

## Step 2: Set Up Modular Instructions

### 2.1 Create Instructions Directory

```bash
mkdir -p /path/to/your/project/.github/instructions
```

### 2.2 Copy Template Instructions

```bash
# Copy relevant instruction files for your project
cp universal-agent-context-system/.github/instructions/python-quality-standards.instructions.md \
   /path/to/your/project/.github/instructions/

cp universal-agent-context-system/.github/instructions/testing-requirements.instructions.md \
   /path/to/your/project/.github/instructions/

# Add more as needed...
```

### 2.3 Create Custom Instructions

Create a new instruction file for your domain:

```bash
# Example: Create API security instructions
cat > /path/to/your/project/.github/instructions/api-security.instructions.md << 'EOF'
---
applyTo:
  - pattern: "src/api/**/*.py"
  - pattern: "**/*_api*.py"
tags: ["python", "api", "security"]
description: "API security and validation requirements"
---

# API Security Requirements

## Core Principles

### 1. Input Validation
- All API inputs must be validated
- Use Pydantic models for request validation
- Sanitize user inputs to prevent injection attacks

### 2. Authentication & Authorization
- All endpoints require authentication (except public endpoints)
- Use JWT tokens for authentication
- Implement role-based access control (RBAC)

## Implementation Standards

### Request Validation
```python
from pydantic import BaseModel, Field

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
```

## Testing Requirements
- Test all validation rules
- Test authentication/authorization
- Test error handling
EOF
```

---

## Step 3: Set Up Role-Based Chat Modes

### 3.1 Create Chat Modes Directory

```bash
mkdir -p /path/to/your/project/.github/chatmodes
```

### 3.2 Copy Template Chat Modes

```bash
# Copy relevant chat modes for your team
cp universal-agent-context-system/.github/chatmodes/architect.chatmode.md \
   /path/to/your/project/.github/chatmodes/

cp universal-agent-context-system/.github/chatmodes/backend-dev.chatmode.md \
   /path/to/your/project/.github/chatmodes/

cp universal-agent-context-system/.github/chatmodes/qa-engineer.chatmode.md \
   /path/to/your/project/.github/chatmodes/

# Add more as needed...
```

### 3.3 Create Custom Chat Modes

Create a new chat mode for your role:

```bash
# Example: Create frontend developer chat mode
cat > /path/to/your/project/.github/chatmodes/frontend-dev.chatmode.md << 'EOF'
---
mode: "frontend-dev"
description: "Frontend development with React/TypeScript"
cognitive_focus: "UI/UX, component design, state management"
security_level: "MEDIUM"
---

# Frontend Developer Chat Mode

## Purpose
Responsible for implementing React components, managing state, and ensuring UI/UX quality.

## Scope

### Accessible Directories
- `src/frontend/` - Full read/write access
- `src/components/` - Full read/write access
- `tests/frontend/` - Full read/write access

## MCP Tool Access

### ✅ ALLOWED Tools
- `str-replace-editor` - Modify frontend code
- `save-file` - Create new components
- `view` - View code and documentation
- `browser_snapshot_Playwright` - Test UI

### ❌ DENIED Tools
- `str-replace-editor` (backend) - Cannot modify backend code
- `launch-process` (database) - Cannot access databases
EOF
```

---

## Step 4: Configure MCP Servers

### 4.1 Install Required MCP Servers

```bash
# Install Context7 for documentation lookup
npm install -g @upstash/context7-mcp

# Install other MCP servers as needed
# See apm.yml for your project's MCP server dependencies
```

### 4.2 Configure VS Code (if using)

Add MCP server configurations to `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "context7": {
      "command": "npx",
      "args": ["@upstash/context7-mcp"]
    }
  }
}
```

---

## Step 5: Validate Installation

### 5.1 Validate YAML Frontmatter

```bash
# Copy validation script
cp universal-agent-context-system/scripts/validate-agentic-frontmatter.py \
   /path/to/your/project/scripts/

# Run validation
python scripts/validate-agentic-frontmatter.py

# Expected output:
# ✅ All instruction files valid
# ✅ All chat mode files valid
```

### 5.2 Test with AI Agent

```bash
# Test with Claude
claude "Review AGENTS.md and summarize the project architecture"

# Test with Gemini
gemini "Review GEMINI.md and confirm understanding"

# Test with GitHub Copilot
# Open a file and ask Copilot to review .github/copilot-instructions.md
```

---

## Step 6: Customize for Your Project

### 6.1 Update Project-Specific Content

**In AGENTS.md**:
- Replace "TTA" with your project name
- Update tech stack and architecture
- Modify directory structure
- Update common commands
- Add your quality gates

**In apm.yml**:
- Set your project name and version
- Configure your development scripts
- Add your MCP server dependencies
- Set your environment variables
- Define your quality thresholds

### 6.2 Create Project-Specific Instructions

Identify your project's key domains and create instruction files:

```bash
# Example domains:
# - Database operations
# - API security
# - Frontend components
# - Testing strategies
# - Deployment procedures

# Create instruction file for each domain
# Follow the template in Step 2.3
```

### 6.3 Define Your Team Roles

Create chat modes for your team's roles:

```bash
# Example roles:
# - Architect
# - Backend Developer
# - Frontend Developer
# - QA Engineer
# - DevOps Engineer
# - Security Auditor

# Create chat mode file for each role
# Follow the template in Step 3.3
```

---

## Step 7: Integrate with Development Workflow

### 7.1 Add to Git

```bash
cd /path/to/your/project

# Add all agent context files
git add AGENTS.md apm.yml
git add .github/instructions/
git add .github/chatmodes/

# Optional: Add agent-specific files
git add CLAUDE.md GEMINI.md .github/copilot-instructions.md

# Commit
git commit -m "Add Universal Agent Context System"
```

### 7.2 Update CI/CD

Add validation to your CI pipeline:

```yaml
# .github/workflows/validate-agent-context.yml
name: Validate Agent Context

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate YAML Frontmatter
        run: python scripts/validate-agentic-frontmatter.py
```

### 7.3 Document for Team

Create a team guide:

```markdown
# AI Agent Usage Guide

## Available Chat Modes
- `/mode architect` - System design and architecture
- `/mode backend-dev` - Backend implementation
- `/mode frontend-dev` - Frontend development
- `/mode qa-engineer` - Testing and quality assurance

## Instruction Files
- `api-security.instructions.md` - API security requirements
- `testing-requirements.instructions.md` - Testing standards
- `python-quality-standards.instructions.md` - Python code quality

## MCP Servers
- Context7 - Documentation lookup
- Serena - Code navigation
- (Add your MCP servers...)
```

---

## Step 8: Train Your Team

### 8.1 Onboarding Checklist

- [ ] Review AGENTS.md to understand project context
- [ ] Review apm.yml to understand available scripts
- [ ] Familiarize with instruction files in `.github/instructions/`
- [ ] Understand chat modes in `.github/chatmodes/`
- [ ] Test AI agent with sample tasks
- [ ] Practice activating different chat modes

### 8.2 Best Practices

1. **Always load universal context**: Ensure AGENTS.md is loaded
2. **Use appropriate chat mode**: Activate role-specific mode for tasks
3. **Follow instruction patterns**: Adhere to domain-specific guidelines
4. **Validate before committing**: Run validation scripts
5. **Keep context updated**: Update AGENTS.md when architecture changes

---

## Troubleshooting

### Issue: AI agent not loading instructions

**Solution**: Check YAML frontmatter and file patterns

```bash
# Validate YAML
python scripts/validate-agentic-frontmatter.py

# Check file patterns match your code
grep -r "applyTo:" .github/instructions/
```

### Issue: Chat mode not activating

**Solution**: Verify mode name and activation command

```yaml
# In chat mode file
mode: "backend-dev"

# Activation command
/mode backend-dev
```

### Issue: MCP server not working

**Solution**: Check MCP server installation and configuration

```bash
# Verify installation
npm list -g @upstash/context7-mcp

# Check VS Code settings
cat .vscode/settings.json | grep mcp
```

---

## Next Steps

1. ✅ Complete installation (Steps 1-5)
2. ✅ Customize for your project (Step 6)
3. ✅ Integrate with workflow (Step 7)
4. ✅ Train your team (Step 8)
5. 📚 Review [YAML_SCHEMA.md](./YAML_SCHEMA.md) for advanced customization
6. 📚 Review [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) if migrating from legacy structure
7. 🚀 Start using AI agents with your new context system!

---

## Support

- **Documentation**: See docs/ directory
- **Examples**: See examples/ directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

