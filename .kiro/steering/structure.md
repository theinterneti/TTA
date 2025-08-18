# Project Structure & Organization

## Repository Architecture

TTA uses a multi-repository structure managed through Git submodules:

```
TTA/                           # Main orchestration repository
├── tta.dev/                   # AI components & development tools (submodule)
├── tta.prototype/             # Narrative & therapeutic content (submodule)
├── tta.prod/                  # Production deployment configs (submodule)
└── src/                       # Orchestration layer
```

## Directory Structure

### Root Level
```
├── config/                    # Configuration files
│   ├── tta_config.yaml       # Main system configuration
│   └── README.md             # Configuration documentation
├── src/                      # Orchestration source code
│   ├── orchestration/        # Core orchestration modules
│   ├── components/           # Component implementations
│   └── main.py              # CLI entry point
├── scripts/                  # Utility and maintenance scripts
│   ├── setup/               # Setup scripts
│   ├── docker/              # Docker-related scripts
│   ├── utils/               # General utilities
│   ├── maintenance/         # Maintenance scripts
│   └── dev/                 # Development scripts
├── Documentation/            # Centralized documentation
│   ├── setup/               # Setup guides
│   ├── architecture/        # System architecture docs
│   ├── ai-framework/        # AI component documentation
│   ├── development/         # Development guidelines
│   ├── deployment/          # Deployment guides
│   ├── guides/              # User and developer guides
│   └── therapeutic-content/ # Content guidelines
├── tests/                   # Test suite
├── templates/               # Template files for submodules
└── .kiro/                   # Kiro IDE configuration
```

## Key Files & Their Purpose

### Configuration
- **config/tta_config.yaml**: Central configuration for all components, ports, and services
- **docker-compose.yml**: Shared services (Redis) configuration
- **gpu_requirements.txt**: GPU-dependent Python packages
- **.gitmodules**: Submodule definitions and URLs

### Entry Points
- **tta.sh**: Main CLI wrapper script
- **src/main.py**: Python orchestration CLI
- **scripts/setup.sh**: Initial project setup

### Documentation Structure
- **Documentation/index.md**: Main documentation index
- **Documentation/README.md**: Documentation overview
- Component-specific docs remain in their respective submodules

## Component Organization

### Orchestration Layer (src/)
- **orchestration/**: Core orchestration logic and component management
- **components/**: Individual component implementations
- **main.py**: CLI interface with Rich formatting

### Submodule Responsibilities
- **tta.dev**: Reusable AI components, agents, RAG systems, MCP tools
- **tta.prototype**: Narrative content, characters, worldbuilding
- **tta.prod**: Production configurations and deployment scripts

## Naming Conventions

### Files & Directories
- Use lowercase with underscores for Python modules: `tta_config.yaml`
- Use kebab-case for documentation: `docker-setup-guide.md`
- Use descriptive names that indicate purpose: `organize_tta.sh`

### Components
- Component names use lowercase: `neo4j`, `llm`, `app`
- Repository prefixes in config: `tta.dev.neo4j`, `tta.prototype.app`

### Scripts
- Action-oriented names: `setup.sh`, `update_submodules.sh`
- Organized by function in subdirectories
- Include README.md in script directories

## Development Workflow

### Working with Submodules
1. Use `./scripts/setup.sh` for initial setup
2. Update with `./scripts/update_submodules.sh`
3. Fix issues with `./scripts/fix_submodules.sh`

### Component Development
1. Components auto-discovered in `src/components/`
2. Inherit from base `Component` class
3. Implement `_start_impl()` and `_stop_impl()` methods
4. Define dependencies in constructor

### Configuration Management
- Central config in `config/tta_config.yaml`
- Environment-specific overrides supported
- CLI commands for config get/set operations

## File Organization Principles

1. **Centralized Documentation**: All docs in `Documentation/` with cross-references
2. **Component Separation**: Clear boundaries between orchestration and submodules
3. **Script Organization**: Grouped by purpose in `scripts/` subdirectories
4. **Template System**: Reusable templates in `templates/` for submodule setup
5. **Test Isolation**: All tests in dedicated `tests/` directory