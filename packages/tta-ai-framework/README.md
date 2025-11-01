# TTA AI Framework

Reusable AI infrastructure for multi-agent orchestration and model management.

## Features

- **Multi-Agent Orchestration**: LangGraph-based agent coordination and workflow management
- **Model Management**: Unified interface for multiple LLM providers (OpenRouter, Ollama, local models)
- **Prompt Engineering**: Versioned prompt registry with template management
- **State Management**: Redis-based state persistence for agent workflows

## Installation

```bash
# Install from workspace (development)
uv pip install -e packages/tta-ai-framework

# Install from PyPI (when published)
uv pip install tta-ai-framework
```

## Quick Start

```python
from tta_ai.orchestration import LangGraphOrchestrator
from tta_ai.models import ModelManager

# Initialize model manager
model_manager = ModelManager()

# Create orchestrator
orchestrator = LangGraphOrchestrator(model_manager=model_manager)

# Run agent workflow
result = await orchestrator.run_workflow(
    workflow_name="narrative_generation",
    input_data={"prompt": "Generate a story scene"}
)
```

## Components

### Orchestration (`tta_ai.orchestration`)

Multi-agent coordination using LangGraph:
- Agent workflow definition and execution
- State management and persistence
- Error recovery and retry logic

### Models (`tta_ai.models`)

LLM provider abstraction:
- Unified interface for multiple providers
- Automatic fallback and retry
- Cost tracking and optimization

### Prompts (`tta_ai.prompts`)

Prompt management system:
- Versioned prompt templates
- Dynamic prompt generation
- Prompt performance tracking

## Development

```bash
# Install development dependencies
uv pip install -e "packages/tta-ai-framework[dev]"

# Run tests
uvx pytest packages/tta-ai-framework/tests/

# Lint and format
uvx ruff check packages/tta-ai-framework/
uvx ruff format packages/tta-ai-framework/

# Type checking
uvx pyright packages/tta-ai-framework/
```

## License

MIT
