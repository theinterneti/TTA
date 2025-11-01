# Narrative Arc Orchestrator

The Narrative Arc Orchestrator manages multi-scale narrative coherence across the TTA system, ensuring that story events at different scales (micro, meso, macro) remain causally consistent and therapeutically aligned.

## Overview

This component provides the core orchestration layer for managing narrative arcs across multiple temporal and thematic scales. It tracks causal relationships, detects conflicts, analyzes impacts, and proposes resolutions to maintain narrative coherence.

## Key Features

- **Causal Graph Management**: Tracks cause-effect relationships across narrative events
- **Conflict Detection**: Identifies temporal, character, thematic, and therapeutic conflicts
- **Impact Analysis**: Analyzes ripple effects of narrative decisions across scales
- **Resolution Engine**: Proposes conflict resolutions while maintaining narrative coherence
- **Scale Management**: Coordinates narrative consistency across micro/meso/macro scales

## Architecture

### Components

1. **Causal Graph** (`causal_graph.py`)
   - Builds and validates causal relationships between events
   - Detects circular dependencies
   - Provides graph traversal utilities

2. **Conflict Detection** (`conflict_detection.py`)
   - Detects temporal conflicts (timeline inconsistencies)
   - Identifies character conflicts (contradictory character actions)
   - Finds thematic conflicts (inconsistent themes)
   - Validates therapeutic alignment

3. **Impact Analysis** (`impact_analysis.py`)
   - Analyzes event impacts across scales
   - Evaluates character involvement
   - Assesses location/setting impacts
   - Validates therapeutic implications

4. **Resolution Engine** (`resolution_engine.py`)
   - Proposes conflict resolutions
   - Maintains narrative coherence
   - Preserves therapeutic goals

5. **Scale Manager** (`scale_manager.py`)
   - Coordinates micro/meso/macro scale events
   - Manages cross-scale consistency
   - Handles scale transitions

## Installation

This component is part of the TTA monorepo. No separate installation required.

### Dependencies

- Python 3.12+
- No external dependencies (self-contained)

## Usage

### Basic Usage

```python
from src.components.narrative_arc_orchestrator.scale_manager import ScaleManager
from src.components.narrative_arc_orchestrator.models import NarrativeEvent

# Initialize scale manager
manager = ScaleManager()

# Create narrative events
event1 = NarrativeEvent(
    event_id="evt_001",
    scale="micro",
    timestamp=1.0,
    description="Character makes a decision",
    metadata={"character_name": "Alice"}
)

event2 = NarrativeEvent(
    event_id="evt_002",
    scale="meso",
    timestamp=2.0,
    description="Decision impacts relationship",
    metadata={"character_name": "Alice", "location": "home"}
)

# Add events
manager.add_event(event1)
manager.add_event(event2)

# Detect conflicts
conflicts = manager.detect_conflicts()

# Analyze impacts
impacts = manager.analyze_impacts()
```

### Advanced Usage

See `tests/test_narrative_arc_orchestrator_component.py` for comprehensive examples.

## API Reference

### ScaleManager

Main orchestration class for managing multi-scale narrative events.

**Methods**:
- `add_event(event: NarrativeEvent) -> None`: Add event to manager
- `detect_conflicts() -> list[ScaleConflict]`: Detect all conflicts
- `analyze_impacts() -> list[ImpactReport]`: Analyze event impacts
- `get_events_by_scale(scale: str) -> list[NarrativeEvent]`: Get events for scale

### NarrativeEvent

Represents a narrative event at a specific scale.

**Attributes**:
- `event_id: str`: Unique event identifier
- `scale: str`: Event scale (micro/meso/macro)
- `timestamp: float`: Event timestamp
- `description: str`: Event description
- `metadata: dict[str, Any] | None`: Optional metadata

## Configuration

No configuration required. Component is self-contained.

## Testing

### Running Tests

```bash
# Run component tests
uv run pytest tests/test_narrative_arc_orchestrator_component.py

# Run with coverage
uv run pytest tests/test_narrative_arc_orchestrator_component.py \
    --cov=src/components/narrative_arc_orchestrator \
    --cov-report=term
```

### Test Coverage

**Current Coverage**: 70.3% (exceeds 70% threshold)

**Test Scenarios**:
- Causal graph construction ✅
- Conflict detection ✅
- Impact analysis ✅
- Resolution engine ✅
- Scale management ✅

## Contributing

### Development Setup

1. Install dependencies: `uv sync`
2. Run tests: `uv run pytest tests/test_narrative_arc_orchestrator_component.py`
3. Run linting: `uvx ruff check src/components/narrative_arc_orchestrator/`
4. Run type checking: `uvx pyright src/components/narrative_arc_orchestrator/`

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public APIs
- Maintain test coverage ≥70%

### Pull Request Process

1. Create feature branch
2. Make changes
3. Run tests and quality checks
4. Submit PR with description
5. Address review feedback

## Maturity Status

**Current Stage**: Development → Staging
**Promotion Issue**: #45
**Test Coverage**: 70.3%
**Last Updated**: 2025-10-13

See `MATURITY.md` for detailed maturity tracking.

## License

Part of the TTA project. See repository LICENSE for details.

## Related Documentation

- Component Maturity: `MATURITY.md`
- Promotion Blockers: `docs/component-promotion/NARRATIVE_ARC_ORCHESTRATOR_BLOCKERS.md`
- Component Maturity Workflow: `docs/development/COMPONENT_MATURITY_WORKFLOW.md`
