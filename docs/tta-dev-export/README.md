# Universal Agent Context System

**Version**: 1.0.0  
**Status**: Production-Ready  
**License**: MIT  
**Compatibility**: Claude, Gemini, GitHub Copilot, Augment, OpenHands

---

## Overview

The **Universal Agent Context System** is a production-ready framework for managing AI agent instructions, role-based chat modes, and cross-platform context in AI-native development projects. It provides a modular, portable, and highly reusable system for organizing AI agent behavior across different platforms.

### Key Features

- 🎯 **Modular Instructions**: YAML frontmatter-based selective loading
- 🤖 **Role-Based Chat Modes**: Strict MCP tool boundaries for security
- 🌐 **Cross-Platform**: Works with Claude, Gemini, Copilot, Augment
- 📦 **Self-Contained**: Easy to adopt in any project
- 🔒 **Security-First**: Built-in approval gates and access controls
- 📊 **Quality Gates**: Automated maturity progression (dev → staging → production)

---

## Quick Start

### 1. Installation

```bash
# Clone or copy the export package to your project
cp -r universal-agent-context-system/.github .
cp universal-agent-context-system/AGENTS.md .
cp universal-agent-context-system/apm.yml .

# Optional: Copy agent-specific files
cp universal-agent-context-system/CLAUDE.md .
cp universal-agent-context-system/GEMINI.md .
cp universal-agent-context-system/.github/copilot-instructions.md .github/
```

### 2. Configuration

Edit `apm.yml` to match your project:

```yaml
name: your-project-name
version: 1.0.0
description: Your project description

# Configure MCP servers for your needs
mcp_servers:
  - name: context7
    package: "@upstash/context7-mcp"
    required: true
  # Add your MCP servers...

# Set environment variables
environment:
  required:
    - YOUR_API_KEY
    - YOUR_DATABASE_URL
```

### 3. Customize Instructions

Create project-specific instruction files in `.github/instructions/`:

```yaml
---
applyTo:
  - pattern: "src/your_module/**/*.py"
tags: ["python", "your-domain"]
description: "Your module-specific instructions"
---

# Your Module Instructions

## Core Principles
...
```

### 4. Define Chat Modes

Create role-based chat modes in `.github/chatmodes/`:

```yaml
---
mode: "your-role"
description: "Role description"
cognitive_focus: "Focus areas"
security_level: "MEDIUM"
---

# Your Role Chat Mode

## MCP Tool Access
...
```

---

## Architecture

### Directory Structure

```
your-project/
├── .github/
│   ├── instructions/           # Modular instruction files
│   │   ├── api-security.instructions.md
│   │   ├── testing-requirements.instructions.md
│   │   └── ...
│   ├── chatmodes/             # Role-based chat modes
│   │   ├── architect.chatmode.md
│   │   ├── backend-dev.chatmode.md
│   │   └── ...
│   ├── prompts/               # Agentic workflow files (optional)
│   └── specs/                 # Specification templates (optional)
├── AGENTS.md                  # Universal context (all agents)
├── CLAUDE.md                  # Claude-specific context (optional)
├── GEMINI.md                  # Gemini-specific context (optional)
├── apm.yml                    # Agent Package Manager config
└── ...
```

### Component Relationships

```
AGENTS.md (Universal Context)
    ↓
    ├─→ CLAUDE.md (Claude-specific)
    ├─→ GEMINI.md (Gemini-specific)
    └─→ .github/copilot-instructions.md (Copilot-specific)
    
.github/instructions/ (Modular Instructions)
    ↓
    └─→ Loaded selectively based on YAML frontmatter
    
.github/chatmodes/ (Role-Based Modes)
    ↓
    └─→ Activated by agent based on user role/task
```

---

## Core Concepts

### 1. Universal Context (AGENTS.md)

The `AGENTS.md` file provides a **universal context standard** that works across all AI agents. It contains:

- Project overview and architecture
- Development workflows
- Testing strategies
- Code conventions
- Quality gates
- Common commands
- Best practices

**When to use**: Always include this file. It's the foundation for all AI agents.

### 2. Agent-Specific Context

Agent-specific files (CLAUDE.md, GEMINI.md, etc.) provide platform-specific guidance:

- **CLAUDE.md**: Claude-specific capabilities and patterns
- **GEMINI.md**: Gemini CLI integration and workflows
- **.github/copilot-instructions.md**: GitHub Copilot integration

**When to use**: Include files for the AI agents you use in your project.

### 3. Modular Instructions

Instruction files in `.github/instructions/` provide **domain-specific guidance** with YAML frontmatter for selective loading:

```yaml
---
applyTo:
  - pattern: "src/api/**/*.py"
  - pattern: "**/*_api*.py"
tags: ["python", "api", "security"]
description: "API security and validation requirements"
---
```

**When to use**: Create instruction files for each major domain or concern in your project.

### 4. Role-Based Chat Modes

Chat mode files in `.github/chatmodes/` define **role-specific behavior** with MCP tool boundaries:

```yaml
---
mode: "backend-dev"
description: "Backend development and implementation"
cognitive_focus: "Implementation, refactoring, bug fixes"
security_level: "MEDIUM"
---
```

**When to use**: Define chat modes for different roles (architect, developer, QA, DevOps, etc.).

### 5. Agent Package Manager (apm.yml)

The `apm.yml` file functions like `package.json` for AI-native projects:

- Workflow scripts (test, lint, deploy, etc.)
- MCP server dependencies
- Environment variables
- Agent behavior configuration
- Quality gate thresholds

**When to use**: Always include this file. It's the central configuration for AI agents.

---

## Usage Examples

### Example 1: Selective Instruction Loading

**Scenario**: You're working on API security code.

**What happens**:
1. AI agent detects you're editing `src/api/auth.py`
2. Loads `api-security.instructions.md` (matches pattern `src/api/**/*.py`)
3. Applies security-specific guidelines
4. Enforces security best practices

### Example 2: Role-Based Development

**Scenario**: You activate "backend-dev" chat mode.

**What happens**:
1. AI agent loads backend-dev.chatmode.md
2. Enables allowed tools: `editFiles`, `runCommands`, `codebase-retrieval`
3. Denies restricted tools: `deleteFiles`, `deployProduction`
4. Focuses on implementation and refactoring tasks

### Example 3: Cross-Agent Compatibility

**Scenario**: You switch from Claude to Gemini.

**What happens**:
1. Both agents load AGENTS.md (universal context)
2. Claude loads CLAUDE.md (Claude-specific patterns)
3. Gemini loads GEMINI.md (Gemini-specific patterns)
4. Both agents have consistent base context + platform-specific optimizations

---

## Integration Guide

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for detailed adoption instructions.

---

## YAML Schema Reference

See [YAML_SCHEMA.md](./YAML_SCHEMA.md) for frontmatter specification.

---

## Migration Guide

See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for upgrading from legacy structures.

---

## Validation

### Validate YAML Frontmatter

```bash
# Run validation script
python scripts/validate-agentic-frontmatter.py

# Expected output:
# ✅ All instruction files valid
# ✅ All chat mode files valid
# ✅ YAML frontmatter schema compliant
```

### Test Cross-Agent Compatibility

```bash
# Test with different agents
claude "Review AGENTS.md and confirm understanding"
gemini "Review AGENTS.md and confirm understanding"
copilot "Review .github/copilot-instructions.md"
```

---

## Best Practices

### 1. Keep Instructions Modular
- One instruction file per domain/concern
- Use YAML frontmatter for selective loading
- Avoid duplication across files

### 2. Define Clear Role Boundaries
- Specify allowed/denied tools explicitly
- Document security rationale
- Include example scenarios

### 3. Maintain Universal Context
- Keep AGENTS.md up-to-date
- Sync changes across agent-specific files
- Document architectural decisions

### 4. Use Quality Gates
- Define maturity thresholds (dev → staging → production)
- Enforce coverage and complexity limits
- Automate promotion workflows

### 5. Version Control Everything
- Track all instruction files in git
- Use semantic versioning for apm.yml
- Document breaking changes

---

## Troubleshooting

### Issue: Instructions not loading

**Solution**: Check YAML frontmatter syntax and file patterns.

```bash
# Validate YAML
python scripts/validate-agentic-frontmatter.py

# Check file patterns
grep -r "applyTo:" .github/instructions/
```

### Issue: Chat mode not activating

**Solution**: Verify mode name and MCP tool access.

```yaml
# Ensure mode name matches activation command
mode: "backend-dev"  # Activate with: /mode backend-dev
```

### Issue: Cross-agent inconsistency

**Solution**: Ensure AGENTS.md is loaded by all agents.

```yaml
# In apm.yml
agent_config:
  context:
    auto_load:
      - "AGENTS.md"
      - ".github/copilot-instructions.md"
```

---

## Contributing

This system is designed to be extended and customized. Contributions welcome!

### Adding New Instructions

1. Create file in `.github/instructions/`
2. Add YAML frontmatter with `applyTo` patterns
3. Document core principles and patterns
4. Include code examples
5. Validate with `validate-agentic-frontmatter.py`

### Adding New Chat Modes

1. Create file in `.github/chatmodes/`
2. Add YAML frontmatter with mode metadata
3. Define MCP tool access (ALLOWED, RESTRICTED, DENIED)
4. Document security rationale
5. Include example scenarios

---

## License

MIT License - See LICENSE file for details.

---

## Support

- **Documentation**: See docs/ directory
- **Examples**: See examples/ directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## Changelog

### Version 1.0.0 (2025-10-28)
- Initial production release
- Universal context system (AGENTS.md)
- Modular instruction system with YAML frontmatter
- Role-based chat modes with MCP tool boundaries
- Agent Package Manager (apm.yml)
- Cross-platform compatibility (Claude, Gemini, Copilot, Augment)

