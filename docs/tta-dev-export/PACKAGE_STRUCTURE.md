# Package Structure - Universal Agent Context System

**Aligned with TTA.dev Repository Conventions**

This document describes the complete directory structure and file organization of the export package, following TTA.dev's established patterns.

---

## TTA.dev Repository Conventions

Based on analysis of the target repository, TTA.dev follows these conventions:

1. **Package-Based Organization**: Components organized under `packages/` directory
2. **Comprehensive Documentation**: Structured docs in `docs/` with subdirectories (architecture, development, guides, integration, mcp, models)
3. **Root-Level Guides**: Key guides at root (README.md, GETTING_STARTED.md, CONTRIBUTING.md)
4. **Quality Standards**: 100% test coverage, comprehensive documentation, battle-tested code only
5. **VS Code Integration**: `.vscode/` with tasks for common operations
6. **Archive Pattern**: Legacy code preserved in `archive/` directory

---

## Export Package Structure (Aligned with TTA.dev)

```
packages/universal-agent-context/       # Main package (follows TTA.dev pattern)
│
├── README.md                           # Package overview and quick start
├── GETTING_STARTED.md                  # 5-minute quickstart guide
├── CONTRIBUTING.md                     # Contribution guidelines
├── LICENSE                             # MIT License
│
├── .github/                            # Modern agent primitive system
│   ├── copilot-instructions.md         # GitHub Copilot instructions
│   │
│   ├── instructions/                   # Modular instruction files (NEW)
│   │   ├── therapeutic-safety.instructions.md
│   │   ├── langgraph-orchestration.instructions.md
│   │   ├── frontend-react.instructions.md
│   │   ├── api-security.instructions.md
│   │   ├── python-quality-standards.instructions.md
│   │   ├── testing-requirements.instructions.md
│   │   ├── testing-battery.instructions.md
│   │   ├── safety.instructions.md
│   │   ├── graph-db.instructions.md
│   │   ├── package-management.md
│   │   ├── docker-improvements.md
│   │   ├── data-separation-strategy.md
│   │   ├── ai-context-sessions.md
│   │   └── serena-code-navigation.md
│   │
│   └── chatmodes/                      # Role-based chat modes (NEW)
│       ├── therapeutic-safety-auditor.chatmode.md
│       ├── langgraph-engineer.chatmode.md
│       ├── database-admin.chatmode.md
│       ├── frontend-developer.chatmode.md
│       ├── architect.chatmode.md
│       ├── backend-dev.chatmode.md
│       ├── backend-implementer.chatmode.md
│       ├── devops.chatmode.md
│       ├── devops-engineer.chatmode.md
│       ├── frontend-dev.chatmode.md
│       ├── qa-engineer.chatmode.md
│       ├── safety-architect.chatmode.md
│       ├── therapeutic-content-creator.chatmode.md
│       ├── narrative-engine-developer.chatmode.md
│       └── api-gateway-engineer.chatmode.md
│
├── .augment/                           # Legacy agent primitive system (DEPRECATED)
│   ├── README.md                       # Deprecation notice and migration guide
│   │
│   ├── chatmodes/                      # Legacy chat modes
│   │   ├── architect.chatmode.md
│   │   ├── backend-dev.chatmode.md
│   │   ├── backend-implementer.chatmode.md
│   │   ├── devops.chatmode.md
│   │   ├── frontend-dev.chatmode.md
│   │   ├── qa-engineer.chatmode.md
│   │   └── safety-architect.chatmode.md
│   │
│   ├── instructions/                   # Legacy instruction files
│   │   ├── agent-orchestration.instructions.md
│   │   ├── augster-communication.instructions.md
│   │   ├── augster-core-identity.instructions.md
│   │   ├── augster-heuristics.instructions.md
│   │   ├── augster-maxims.instructions.md
│   │   ├── augster-operational-loop.instructions.md
│   │   ├── augster-protocols.instructions.md
│   │   ├── component-maturity.instructions.md
│   │   ├── global.instructions.md
│   │   ├── memory-capture.instructions.md
│   │   ├── narrative-engine.instructions.md
│   │   ├── player-experience.instructions.md
│   │   ├── quality-gates.instructions.md
│   │   └── testing.instructions.md
│   │
│   ├── workflows/                      # Legacy workflow prompts
│   │   ├── augster-axiomatic-workflow.prompt.md
│   │   ├── bug-fix.prompt.md
│   │   ├── component-promotion.prompt.md
│   │   ├── context-management.workflow.md
│   │   ├── docker-migration.workflow.md
│   │   ├── feature-implementation.prompt.md
│   │   ├── quality-gate-fix.prompt.md
│   │   └── test-coverage-improvement.prompt.md
│   │
│   ├── context/                        # Legacy context management
│   │   ├── README.md
│   │   ├── cli.py
│   │   ├── conversation_manager.py
│   │   ├── debugging.context.md
│   │   ├── deployment.context.md
│   │   ├── integration.context.md
│   │   ├── performance.context.md
│   │   ├── refactoring.context.md
│   │   ├── security.context.md
│   │   └── testing.context.md
│   │
│   ├── memory/                         # Legacy memory system
│   │   ├── README.md
│   │   ├── component-failures.memory.md
│   │   ├── quality-gates.memory.md
│   │   ├── testing-patterns.memory.md
│   │   └── workflow-learnings.memory.md
│   │
│   ├── rules/                          # Legacy rules
│   │   ├── Use-your-tools.md
│   │   └── avoid-long-files.md
│   │
│   └── user_guidelines.md              # Legacy user guidelines
│
├── docs/                               # Documentation (TTA.dev pattern)
│   ├── guides/                         # User guides
│   │   ├── INTEGRATION_GUIDE.md        # Step-by-step adoption
│   │   ├── MIGRATION_GUIDE.md          # Migration from legacy
│   │   └── GETTING_STARTED.md          # Quick start (symlink to root)
│   │
│   ├── architecture/                   # Architecture documentation
│   │   ├── OVERVIEW.md                 # System architecture
│   │   ├── YAML_SCHEMA.md              # Frontmatter specification
│   │   └── SELECTIVE_LOADING.md        # Loading mechanism
│   │
│   ├── development/                    # Development guides
│   │   ├── CONTRIBUTING.md             # Contribution guide (symlink to root)
│   │   ├── CODING_STANDARDS.md         # Code quality standards
│   │   └── TESTING.md                  # Testing guidelines
│   │
│   ├── integration/                    # Integration guides
│   │   ├── CLAUDE.md                   # Claude integration
│   │   ├── GEMINI.md                   # Gemini integration
│   │   ├── COPILOT.md                  # GitHub Copilot integration
│   │   └── AUGMENT.md                  # Augment integration
│   │
│   ├── mcp/                            # MCP server documentation
│   │   ├── README.md                   # MCP overview
│   │   ├── CONTEXT7.md                 # Context7 integration
│   │   ├── SERENA.md                   # Serena integration
│   │   └── CUSTOM_SERVERS.md           # Custom MCP servers
│   │
│   ├── examples/                       # Usage examples
│   │   ├── basic-usage.md              # Basic usage examples
│   │   ├── custom-instruction.md       # Custom instruction example
│   │   ├── custom-chatmode.md          # Custom chat mode example
│   │   └── example-project/            # Complete example project
│   │
│   └── knowledge/                      # Knowledge base
│       ├── EXPORT_READINESS_ASSESSMENT.md
│       ├── EXPORT_MANIFEST.md
│       ├── EXPORT_SUMMARY.md
│       ├── EXPORT_CHECKLIST.md
│       └── PACKAGE_STRUCTURE.md        # This file
│
├── scripts/                            # Utility scripts
│   ├── validate-export-package.py      # Validation script
│   ├── migrate-from-augment.sh         # Migration helper
│   └── setup-dev-environment.sh        # Development setup
│
├── tests/                              # Test suite
│   ├── test_yaml_frontmatter.py        # YAML validation tests
│   ├── test_selective_loading.py       # Loading mechanism tests
│   └── test_cross_agent_compat.py      # Cross-agent compatibility tests
│
├── .vscode/                            # VS Code configuration
│   ├── tasks.json                      # Common tasks
│   └── settings.json                   # Workspace settings
│
├── AGENTS.md                           # Universal context (root level)
├── apm.yml                             # Agent Package Manager config
│
└── archive/                            # Archived/deprecated content
    └── legacy-augment-structure/       # Original .augment/ backup
```

---

## Legacy to New Structure Mapping

This export package includes **BOTH** the legacy `.augment/` structure and the new `.github/` structure to demonstrate the migration path and maintain backward compatibility.

### Why Include Both?

1. **Migration Demonstration**: Shows the complete evolution from legacy to modern structure
2. **Backward Compatibility**: Existing projects can continue using `.augment/` while migrating
3. **Comparison Reference**: Side-by-side comparison helps understand improvements
4. **Educational Value**: Illustrates best practices evolution in AI-native development

### File Location Mapping

| Legacy Location (.augment/) | New Location (.github/) | Status | Notes |
|----------------------------|------------------------|--------|-------|
| `.augment/chatmodes/architect.chatmode.md` | `.github/chatmodes/architect.chatmode.md` | ✅ Migrated | Updated with YAML frontmatter |
| `.augment/chatmodes/backend-dev.chatmode.md` | `.github/chatmodes/backend-dev.chatmode.md` | ✅ Migrated | Updated with YAML frontmatter |
| `.augment/chatmodes/devops.chatmode.md` | `.github/chatmodes/devops.chatmode.md` | ✅ Migrated | Updated with YAML frontmatter |
| `.augment/chatmodes/frontend-dev.chatmode.md` | `.github/chatmodes/frontend-dev.chatmode.md` | ✅ Migrated | Updated with YAML frontmatter |
| `.augment/chatmodes/qa-engineer.chatmode.md` | `.github/chatmodes/qa-engineer.chatmode.md` | ✅ Migrated | Updated with YAML frontmatter |
| `.augment/chatmodes/safety-architect.chatmode.md` | `.github/chatmodes/safety-architect.chatmode.md` | ✅ Migrated | Updated with YAML frontmatter |
| `.augment/instructions/testing.instructions.md` | `.github/instructions/testing-requirements.instructions.md` | ✅ Migrated | Renamed and enhanced |
| `.augment/instructions/quality-gates.instructions.md` | `.github/instructions/python-quality-standards.instructions.md` | ✅ Migrated | Renamed and enhanced |
| `.augment/workflows/*.prompt.md` | `docs/examples/` | ⚠️ Archived | Converted to examples |
| `.augment/context/*.context.md` | `docs/guides/` | ⚠️ Archived | Converted to guides |
| `.augment/memory/*.memory.md` | `docs/knowledge/` | ⚠️ Archived | Converted to knowledge base |

### New Files (Not in Legacy)

| File | Purpose | Why New? |
|------|---------|----------|
| `.github/instructions/therapeutic-safety.instructions.md` | Therapeutic safety requirements | Domain-specific addition |
| `.github/instructions/langgraph-orchestration.instructions.md` | LangGraph patterns | Technology-specific addition |
| `.github/instructions/frontend-react.instructions.md` | React development | Technology-specific addition |
| `.github/instructions/api-security.instructions.md` | API security | Domain-specific addition |
| `.github/chatmodes/therapeutic-safety-auditor.chatmode.md` | Safety auditing role | Role-specific addition |
| `.github/chatmodes/langgraph-engineer.chatmode.md` | LangGraph development role | Role-specific addition |
| `.github/chatmodes/database-admin.chatmode.md` | Database administration role | Role-specific addition |
| `AGENTS.md` | Universal context | Cross-platform standardization |
| `apm.yml` | Agent Package Manager | Configuration standardization |

### Deprecated Files (Legacy Only)

| File | Reason for Deprecation | Replacement |
|------|----------------------|-------------|
| `.augment/instructions/augster-*.instructions.md` | TTA-specific agent identity | Generic patterns in AGENTS.md |
| `.augment/instructions/narrative-engine.instructions.md` | TTA-specific domain | Removed (project-specific) |
| `.augment/instructions/player-experience.instructions.md` | TTA-specific domain | Removed (project-specific) |
| `.augment/context/cli.py` | Python implementation | Conceptual guide in docs/ |
| `.augment/context/conversation_manager.py` | Python implementation | Conceptual guide in docs/ |
| `.augment/user_guidelines.md` | Informal guidelines | Formalized in CONTRIBUTING.md |

### Key Improvements in New Structure

1. **YAML Frontmatter**: All instruction and chat mode files now have structured metadata
2. **Selective Loading**: Pattern-based loading mechanism for relevant instructions
3. **Security Levels**: Explicit security boundaries for chat modes
4. **MCP Tool Access**: Defined tool access controls (allowed, denied, approval-required)
5. **Cross-Platform**: Universal context works across multiple AI agents
6. **Documentation Structure**: Organized into guides/, architecture/, development/, etc.
7. **TTA.dev Alignment**: Follows established patterns from target repository

---

## File Descriptions

### Root Level Files

#### `README.md`
- **Purpose**: Main package documentation
- **Contents**: Quick start, architecture overview, usage examples
- **Audience**: All users
- **Size**: ~300 lines

#### `AGENTS.md`
- **Purpose**: Universal context for all AI agents
- **Contents**: Project overview, architecture, workflows, best practices
- **Audience**: All AI agents (Claude, Gemini, Copilot, Augment)
- **Size**: 346 lines

#### `CLAUDE.md`
- **Purpose**: Claude-specific instructions
- **Contents**: Claude capabilities, usage patterns, TTA-specific guidance
- **Audience**: Claude users
- **Size**: 170 lines

#### `GEMINI.md`
- **Purpose**: Gemini-specific instructions
- **Contents**: Gemini CLI integration, project structure, current tasks
- **Audience**: Gemini users
- **Size**: 164 lines

#### `apm.yml`
- **Purpose**: Agent Package Manager configuration
- **Contents**: Scripts, MCP servers, environment, quality gates
- **Audience**: All AI agents
- **Size**: 209 lines

#### `LICENSE`
- **Purpose**: MIT License
- **Contents**: License terms and conditions
- **Audience**: All users
- **Size**: ~20 lines

---

### `.github/` Directory

#### `.github/copilot-instructions.md`
- **Purpose**: GitHub Copilot instructions
- **Contents**: Project overview, architecture, MCP integration
- **Audience**: GitHub Copilot users
- **Size**: 194 lines

#### `.github/instructions/`
- **Purpose**: Modular instruction files with YAML frontmatter
- **Contents**: Domain-specific guidelines (14 files)
- **Audience**: AI agents (selective loading based on file patterns)
- **File Count**: 14 files

**Instruction Files**:
1. `therapeutic-safety.instructions.md` - Therapeutic safety requirements
2. `langgraph-orchestration.instructions.md` - LangGraph workflow patterns
3. `frontend-react.instructions.md` - React frontend development
4. `api-security.instructions.md` - API security and validation
5. `python-quality-standards.instructions.md` - Python code quality
6. `testing-requirements.instructions.md` - Testing standards
7. `testing-battery.instructions.md` - Comprehensive test battery
8. `safety.instructions.md` - Safety validation
9. `graph-db.instructions.md` - Graph database operations
10. `package-management.md` - Package management with UV
11. `docker-improvements.md` - Docker best practices
12. `data-separation-strategy.md` - Data separation architecture
13. `ai-context-sessions.md` - AI context management
14. `serena-code-navigation.md` - Serena MCP usage

#### `.github/chatmodes/`
- **Purpose**: Role-based chat modes with MCP tool boundaries
- **Contents**: Role-specific behavior definitions (15 files)
- **Audience**: AI agents (activated by user role/task)
- **File Count**: 15 files

**Chat Mode Files**:
1. `therapeutic-safety-auditor.chatmode.md` - Safety auditing (read-only)
2. `langgraph-engineer.chatmode.md` - LangGraph development
3. `database-admin.chatmode.md` - Database administration
4. `frontend-developer.chatmode.md` - Frontend development
5. `architect.chatmode.md` - System architecture
6. `backend-dev.chatmode.md` - Backend development
7. `backend-implementer.chatmode.md` - Backend implementation
8. `devops.chatmode.md` - DevOps operations
9. `devops-engineer.chatmode.md` - DevOps engineering
10. `frontend-dev.chatmode.md` - Frontend development
11. `qa-engineer.chatmode.md` - Quality assurance
12. `safety-architect.chatmode.md` - Safety architecture
13. `therapeutic-content-creator.chatmode.md` - Content creation
14. `narrative-engine-developer.chatmode.md` - Narrative development
15. `api-gateway-engineer.chatmode.md` - API gateway development

---

### `docs/` Directory

#### `docs/INTEGRATION_GUIDE.md`
- **Purpose**: Step-by-step adoption guide
- **Contents**: Installation, configuration, customization, validation
- **Audience**: New adopters
- **Size**: ~300 lines

#### `docs/YAML_SCHEMA.md`
- **Purpose**: YAML frontmatter specification
- **Contents**: Schema definitions, field specifications, validation rules
- **Audience**: Advanced users, contributors
- **Size**: ~300 lines

#### `docs/MIGRATION_GUIDE.md`
- **Purpose**: Migration from legacy structures
- **Contents**: Migration scenarios, checklists, troubleshooting
- **Audience**: Users migrating from legacy systems
- **Size**: ~300 lines

#### `docs/EXPORT_READINESS_ASSESSMENT.md`
- **Purpose**: Export readiness assessment
- **Contents**: Criteria evaluation, scores, recommendations
- **Audience**: Maintainers, reviewers
- **Size**: ~300 lines

#### `docs/EXPORT_MANIFEST.md`
- **Purpose**: Export manifest and inventory
- **Contents**: File inventory, version info, compatibility matrix
- **Audience**: Maintainers, users
- **Size**: ~300 lines

#### `docs/PACKAGE_STRUCTURE.md`
- **Purpose**: Package structure documentation
- **Contents**: Directory tree, file descriptions, organization
- **Audience**: All users
- **Size**: ~300 lines

---

### `scripts/` Directory

#### `scripts/validate-export-package.py`
- **Purpose**: Validation script for export package
- **Contents**: YAML validation, schema compliance, cross-reference checks
- **Audience**: Maintainers, contributors
- **Language**: Python 3.8+
- **Size**: ~300 lines

**Usage**:
```bash
python scripts/validate-export-package.py
python scripts/validate-export-package.py --strict
```

---

### `examples/` Directory (Optional)

#### `examples/example-project/`
- **Purpose**: Example project demonstrating usage
- **Contents**: Sample project structure with agent context
- **Audience**: New users
- **Size**: Varies

#### `examples/custom-instruction.md`
- **Purpose**: Example custom instruction file
- **Contents**: Template with YAML frontmatter
- **Audience**: Users creating custom instructions
- **Size**: ~50 lines

#### `examples/custom-chatmode.md`
- **Purpose**: Example custom chat mode file
- **Contents**: Template with YAML frontmatter
- **Audience**: Users creating custom chat modes
- **Size**: ~100 lines

---

## File Organization Principles

### 1. Separation of Concerns
- **Core files** (root): Universal context and configuration
- **Agent-specific files** (root): Platform-specific instructions
- **Modular instructions** (.github/instructions/): Domain-specific guidelines
- **Chat modes** (.github/chatmodes/): Role-specific behavior
- **Documentation** (docs/): Guides and references
- **Scripts** (scripts/): Utility tools

### 2. Discoverability
- **Root level**: Most important files (README, AGENTS.md, apm.yml)
- **Subdirectories**: Organized by type (instructions, chatmodes, docs, scripts)
- **Naming conventions**: Clear, descriptive names with extensions

### 3. Modularity
- **Instruction files**: One file per domain/concern
- **Chat modes**: One file per role
- **Documentation**: One file per topic
- **Scripts**: One file per utility

### 4. Extensibility
- **Custom instructions**: Add to .github/instructions/
- **Custom chat modes**: Add to .github/chatmodes/
- **Custom scripts**: Add to scripts/
- **Custom examples**: Add to examples/

---

## File Naming Conventions

### Instruction Files
- **Format**: `{domain}.instructions.md`
- **Examples**: `api-security.instructions.md`, `testing-requirements.instructions.md`
- **Location**: `.github/instructions/`

### Chat Mode Files
- **Format**: `{role}.chatmode.md`
- **Examples**: `backend-dev.chatmode.md`, `qa-engineer.chatmode.md`
- **Location**: `.github/chatmodes/`

### Documentation Files
- **Format**: `{TOPIC}.md` (uppercase for main docs)
- **Examples**: `INTEGRATION_GUIDE.md`, `YAML_SCHEMA.md`
- **Location**: `docs/`

### Script Files
- **Format**: `{purpose}-{action}.py`
- **Examples**: `validate-export-package.py`
- **Location**: `scripts/`

---

## Size Guidelines

### File Size Limits
- **Production maturity**: ≤800 lines
- **Staging maturity**: ≤1,000 lines
- **Development maturity**: ≤1,200 lines

### Current Package Size
- **Total files**: 41 files
- **Total lines**: ~8,500 lines
- **Estimated size**: ~350 KB (text files)
- **Largest file**: AGENTS.md (346 lines)
- **Average file size**: ~200 lines

---

## Maintenance Guidelines

### Adding New Files

1. **Instruction files**: Add to `.github/instructions/` with YAML frontmatter
2. **Chat modes**: Add to `.github/chatmodes/` with YAML frontmatter
3. **Documentation**: Add to `docs/` with clear purpose
4. **Scripts**: Add to `scripts/` with usage documentation

### Updating Existing Files

1. **Update version** in YAML frontmatter (if applicable)
2. **Update description** if purpose changes
3. **Run validation** script before committing
4. **Update cross-references** in related files

### Removing Files

1. **Check cross-references** in other files
2. **Update documentation** to remove references
3. **Run validation** script after removal
4. **Document removal** in changelog

---

## Best Practices

1. **Keep files focused**: One domain/role per file
2. **Use YAML frontmatter**: For selective loading and metadata
3. **Document changes**: Update descriptions and versions
4. **Validate regularly**: Run validation script before committing
5. **Maintain consistency**: Follow naming conventions and structure
6. **Keep sizes manageable**: Stay within file size limits
7. **Cross-reference carefully**: Ensure all references are valid

---

## References

- **README.md**: Package overview and quick start
- **INTEGRATION_GUIDE.md**: Adoption instructions
- **YAML_SCHEMA.md**: Frontmatter specification
- **MIGRATION_GUIDE.md**: Migration from legacy structures
- **EXPORT_MANIFEST.md**: Complete file inventory

