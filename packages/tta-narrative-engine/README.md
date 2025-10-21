# TTA Narrative Engine

Reusable narrative generation system for therapeutic storytelling and interactive fiction.

## Features

- **Scene Generation**: AI-powered scene creation with therapeutic elements
- **Narrative Orchestration**: Multi-scale narrative management (scene, chapter, arc)
- **Coherence Validation**: Automatic detection of narrative contradictions and inconsistencies
- **Therapeutic Integration**: Built-in support for therapeutic storytelling frameworks

## Installation

```bash
# Install from workspace (development)
uv pip install -e packages/tta-narrative-engine

# Install from PyPI (when published)
uv pip install tta-narrative-engine
```

## Quick Start

```python
from tta_narrative.generation import SceneGenerator
from tta_narrative.orchestration import NarrativeArcOrchestrator

# Initialize scene generator
scene_gen = SceneGenerator()

# Generate a therapeutic scene
scene = await scene_gen.generate_scene(
    setting="peaceful forest",
    therapeutic_focus="mindfulness",
    player_state={"emotional_state": "anxious"}
)

# Orchestrate multi-scale narrative
orchestrator = NarrativeArcOrchestrator()
arc = await orchestrator.create_narrative_arc(
    theme="personal growth",
    duration="medium",
    therapeutic_goals=["emotional_regulation", "self_awareness"]
)
```

## Components

### Generation (`tta_narrative.generation`)

Scene and content generation:
- Therapeutic scene templates
- Dynamic content adaptation
- Character dialogue generation

### Orchestration (`tta_narrative.orchestration`)

Multi-scale narrative management:
- Scene-level coordination
- Chapter and arc planning
- Pacing and tension control

### Coherence (`tta_narrative.coherence`)

Narrative consistency validation:
- Contradiction detection
- Causal relationship tracking
- World state validation

## Development

```bash
# Install development dependencies
uv pip install -e "packages/tta-narrative-engine[dev]"

# Run tests
uvx pytest packages/tta-narrative-engine/tests/

# Lint and format
uvx ruff check packages/tta-narrative-engine/
uvx ruff format packages/tta-narrative-engine/

# Type checking
uvx pyright packages/tta-narrative-engine/
```

## License

MIT

