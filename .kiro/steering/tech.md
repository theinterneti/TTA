---
inclusion: always
---

# TTA Technology Stack & Development Guidelines

## Required Command Patterns

### Always Use UV for Python Operations
- **Package management**: `uv add package_name` (never use pip directly)
- **Running scripts**: `uv run python script.py` (ensures correct environment)
- **Installing dependencies**: `uv sync` (not pip install -r requirements.txt)
- **Development mode**: `uv sync --dev` for development dependencies

### Always Use ./tta.sh for Service Operations
- **Start services**: `./tta.sh start [component_name]` (not docker-compose directly)
- **Stop services**: `./tta.sh stop` (handles all cleanup)
- **Check status**: `./tta.sh status` (shows all component states)
- **Configuration**: `./tta.sh config get/set key value` (not manual YAML editing)

## Critical Architecture Rules

### Multi-Repository Structure (Git Submodules)
- **tta.dev/**: AI infrastructure, database layers, MCP tools
- **tta.prototype/**: Narrative engines, therapeutic content
- **tta.prod/**: Production deployment configurations
- **NEVER**: Manually edit .gitmodules - use provided scripts

### Component Development Pattern
```python
# All components MUST inherit from base Component class
class MyComponent(Component):
    def __init__(self):
        super().__init__(
            name="component_name",  # lowercase, no spaces
            dependencies=["redis", "neo4j"]  # explicit dependencies
        )
    
    def _start_impl(self) -> bool:
        # Implementation here
        return True  # MUST return boolean
    
    def _stop_impl(self) -> bool:
        # Cleanup here  
        return True  # MUST return boolean
```

### Configuration Management Rules
- **Single source**: All configuration in `config/tta_config.yaml`
- **Hierarchical keys**: Use `repository.component.setting` format
- **Port management**: All ports defined centrally, never hardcoded
- **Access pattern**: Use `./tta.sh config` commands, not direct file editing

## Technology Stack Specifics

### Core Technologies
- **Python 3.x**: Primary language with UV package management
- **Neo4j**: Knowledge graph database (ports 7687, 7688)
- **Redis**: Caching and session storage
- **Docker**: Containerization with custom orchestration via tta.sh

### AI/ML Stack
- **PyTorch**: Deep learning with GPU support
- **Transformers**: Hugging Face NLP models
- **CodeCarbon**: Energy consumption tracking (therapeutic AI ethics requirement)

## Development Workflow Requirements

### Setup & Maintenance Scripts
- **Initial setup**: `./scripts/setup.sh` (handles all submodules and dependencies)
- **Submodule updates**: `./scripts/update_submodules.sh` (never git submodule update directly)
- **Fix issues**: `./scripts/fix_submodules.sh` (when submodules break)

### Testing Patterns
- **Run all tests**: `uv run python -m unittest discover tests`
- **Component tests**: `uv run python -m unittest tests.test_component_name`
- **Coverage requirement**: 80%+ for therapeutic pathways

### File Organization Rules
- **Components**: Place in `src/components/` for auto-discovery
- **Tests**: Mirror source structure in `tests/`
- **Scripts**: Organize by function in `scripts/` subdirectories
- **Config**: Central config only in `config/tta_config.yaml`

## Therapeutic Safety Requirements
- All AI components must include safety checks and bias monitoring
- User privacy and data protection are paramount
- Implement safeguards against harmful content
- Use descriptive names reflecting therapeutic context
- Include comprehensive docstrings for therapeutic functions