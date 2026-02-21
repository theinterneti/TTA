# Package Overview

TTA is organized as a monorepo with reusable packages that can be extracted and used in other projects.

## Package Structure

```
packages/
├── tta-ai-framework/       # AI infrastructure
│   ├── src/tta_ai/
│   │   ├── orchestration/  # Agent coordination
│   │   ├── models/         # Model management
│   │   └── prompts/        # Prompt registry
│   └── pyproject.toml
│
└── tta-narrative-engine/   # Narrative generation
    ├── src/tta_narrative/
    │   ├── generation/     # Scene generation
    │   ├── orchestration/  # Narrative orchestration
    │   └── coherence/      # Coherence validation
    └── pyproject.toml
```

## TTA AI Framework

**Purpose**: Reusable AI infrastructure for building multi-agent systems

**Key Features**:
- Multi-agent orchestration with LangGraph
- Model provider abstraction (OpenRouter, Ollama, LM Studio, etc.)
- Prompt versioning and registry
- Circuit breakers and error recovery
- Redis-based agent coordination

**Dependencies**: None (base package)

[Full documentation →](tta-ai-framework/index.md)

## TTA Narrative Engine

**Purpose**: Reusable narrative generation system for interactive storytelling

**Key Features**:
- Dynamic scene generation
- Multi-scale narrative orchestration
- Coherence validation and contradiction detection
- Therapeutic storytelling patterns
- Pacing and complexity adaptation

**Dependencies**: TTA AI Framework

[Full documentation →](tta-narrative-engine/index.md)

## Using Packages in Other Projects

### Installation

```bash
# Install from local workspace
uv pip install -e packages/tta-ai-framework
uv pip install -e packages/tta-narrative-engine

# Or install from git (future)
uv pip install git+https://github.com/theinterneti/TTA.git#subdirectory=packages/tta-ai-framework
```

### Example Usage

```python
from tta_ai.orchestration import AgentOrchestrator
from tta_ai.models import ModelSelector
from tta_narrative.generation import SceneGenerator

# Initialize AI infrastructure
orchestrator = AgentOrchestrator()
model_selector = ModelSelector()

# Generate narrative content
scene_gen = SceneGenerator(model_selector=model_selector)
scene = await scene_gen.generate_scene(context={...})
```

## Package Maturity

Each package tracks its maturity independently:

| Package | Stage | Coverage | Status |
|---------|-------|----------|--------|
| tta-ai-framework | Development | 65% | Active development |
| tta-narrative-engine | Development | 60% | Active development |

See [Component Maturity](../development/component-maturity.md) for details.

## Future Packages

Planned packages for extraction:

- **tta-database**: Redis and Neo4j integration patterns
- **tta-monitoring**: Observability and metrics
- **tta-testing**: Testing utilities and fixtures

## Contributing to Packages

When contributing to packages, ensure:

1. **No TTA-specific dependencies**: Packages should be reusable
2. **Comprehensive tests**: Maintain coverage thresholds
3. **Clear documentation**: Document all public APIs
4. **Semantic versioning**: Follow semver for releases

[Contributing guide →](../development/contributing.md)


---
**Logseq:** [[TTA.dev/Docs/Packages/Overview]]
