---
inclusion: always
---

# Project Structure & Code Organization

## Multi-Repository Architecture

TTA uses Git submodules for separation of concerns:
- **tta.dev/**: AI infrastructure, database layers, MCP tools
- **tta.prototype/**: Narrative engines, therapeutic content, worldbuilding
- **tta.prod/**: Production deployment and monitoring
- **src/**: Main orchestration layer and component management

## File Location Rules

### Where to Place New Code
- **Orchestration logic**: `src/orchestration/`
- **Component implementations**: `src/components/` (auto-discovered)
- **Shared utilities**: `src/components/` or appropriate submodule
- **Tests**: `tests/` (mirror source structure)
- **Configuration**: `config/tta_config.yaml` (central config only)
- **Scripts**: `scripts/` organized by function (setup/, docker/, utils/, etc.)

### Critical Files to Know
- **config/tta_config.yaml**: All component ports, services, and feature flags
- **tta.sh**: Main CLI entry point (use for all operations)
- **src/main.py**: Python orchestration CLI with Rich formatting
- **docker-compose.yml**: Shared services (Redis, databases)

## Naming Conventions (Strict)

### Python Code
- **Modules**: `snake_case` (e.g., `therapeutic_engine.py`)
- **Classes**: `PascalCase` (e.g., `TherapeuticEngine`)
- **Functions/Variables**: `snake_case` (e.g., `process_narrative`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PORT`)

### Files & Directories
- **Python files**: `snake_case.py`
- **Config files**: `snake_case.yaml`
- **Documentation**: `kebab-case.md`
- **Scripts**: `action_verb.sh` (e.g., `setup_database.sh`)

### Component Naming
- **Component names**: lowercase (e.g., `neo4j`, `llm`, `redis`)
- **Config keys**: dot notation with repo prefix (e.g., `tta.dev.neo4j.port`)

## Component Development Pattern

### Required Implementation
```python
class MyComponent(Component):
    def __init__(self):
        super().__init__(
            name="my_component",
            dependencies=["redis", "neo4j"]  # Optional
        )
    
    def _start_impl(self) -> bool:
        # Implementation here
        return True
    
    def _stop_impl(self) -> bool:
        # Cleanup here
        return True
```

### Auto-Discovery Rules
- Place in `src/components/`
- Inherit from base `Component` class
- Use descriptive, therapeutic-context names
- Define dependencies explicitly

## Configuration Management

### Central Configuration
- **Single source**: `config/tta_config.yaml`
- **Hierarchical keys**: `repository.component.setting`
- **Environment overrides**: Supported via CLI
- **Port management**: All ports defined centrally

### CLI Configuration Access
```bash
./tta.sh config get tta.dev.neo4j.port
./tta.sh config set tta.dev.enabled true
```

## Development Workflow Rules

### Submodule Operations
- **Setup**: Always use `./scripts/setup.sh`
- **Updates**: Use `./scripts/update_submodules.sh`
- **Issues**: Use `./scripts/fix_submodules.sh`
- **Never**: Manually edit `.gitmodules`

### Service Management
- **Start services**: `./tta.sh start [component]`
- **Stop services**: `./tta.sh stop`
- **Check status**: `./tta.sh status`
- **Docker operations**: `./tta.sh docker compose up -d`

## Code Organization Principles

### Therapeutic Context Requirements
- All therapeutic components must include safety checks
- Use descriptive names that reflect therapeutic purpose
- Include comprehensive docstrings for therapeutic functions
- Implement proper error handling with user-friendly messages

### Dependency Management
- Components declare dependencies in constructor
- Use configuration-driven service discovery
- Implement health checks for all services
- Maintain backward compatibility across updates

### Testing Structure
- Mirror source directory structure in `tests/`
- Use descriptive test names: `test_therapeutic_narrative_generation`
- Include integration tests for component interactions
- Maintain 80%+ coverage for therapeutic pathways