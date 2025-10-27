# Narrative Coherence Component

**Status**: Development → Staging Promotion
**Version**: 1.0.0
**Last Updated**: 2025-10-08
**Owner**: theinterneti
**Functional Group**: Therapeutic Content

---

## Overview

The Narrative Coherence component ensures consistency, logical flow, and therapeutic alignment across all narrative content in the TTA (Therapeutic Text Adventure) system. It validates story elements against established lore, character profiles, world rules, and therapeutic objectives to maintain a coherent and therapeutically effective narrative experience.

### Purpose

- **Maintain Narrative Consistency**: Ensure all story elements align with established lore and world rules
- **Validate Character Behavior**: Check that character actions and dialogue match their established personalities
- **Detect Contradictions**: Identify and resolve conflicts in narrative content across sessions
- **Ensure Therapeutic Alignment**: Validate that narrative content supports therapeutic objectives
- **Support Creative Solutions**: Provide intelligent suggestions for resolving narrative conflicts

---

## Key Features

### 1. Coherence Validation
- **Lore Compliance**: Validates content against established world lore and canonical facts
- **Character Consistency**: Ensures character behavior, dialogue, and actions match established profiles
- **World Rule Enforcement**: Checks adherence to physics, supernatural, social, and technological rules
- **Therapeutic Safety**: Validates content for harmful elements and therapeutic appropriateness

### 2. Causal Validation
- **Logical Flow**: Ensures cause-and-effect relationships are logical and believable
- **Temporal Consistency**: Validates event timing and sequence
- **Consequence Validation**: Checks that consequences are proportional and believable
- **Fallacy Detection**: Identifies logical fallacies and impossible scenarios

### 3. Contradiction Detection
- **Direct Conflict Detection**: Identifies explicit contradictions between narrative elements
- **Implicit Conflict Detection**: Finds subtle inconsistencies that may not be immediately obvious
- **Temporal Paradox Detection**: Identifies timeline inconsistencies
- **Causal Conflict Detection**: Finds conflicts in cause-and-effect chains

### 4. Creative Resolution
- **Intelligent Suggestions**: Provides context-aware correction suggestions
- **Multiple Solutions**: Offers various approaches to resolving conflicts
- **Narrative Cost Analysis**: Evaluates the impact of different resolution strategies
- **Retroactive Change Support**: Enables in-world explanations for narrative adjustments

---

## Architecture

### Core Components

```
narrative_coherence/
├── __init__.py                  # Package initialization and exports
├── models.py                    # Data models and enums
├── coherence_validator.py       # Main coherence validation logic
├── causal_validator.py          # Causal relationship validation
├── contradiction_detector.py    # Contradiction detection and resolution
└── rules.py                     # Validation rules and weights
```

### Data Models

#### `NarrativeContent`
Represents a piece of narrative content to be validated.

```python
@dataclass
class NarrativeContent:
    content_id: str
    content_type: str
    text: str
    related_characters: list[str]
    related_locations: list[str]
    related_events: list[str]
    themes: list[str]
    therapeutic_concepts: list[str]
    metadata: dict[str, Any]
```

#### `ValidationResult`
Contains the results of narrative validation.

```python
@dataclass
class ValidationResult:
    is_valid: bool
    consistency_score: float
    detected_issues: list[ConsistencyIssue]
    lore_consistency: float
    character_consistency: float
    world_rule_consistency: float
    causal_consistency: float
    therapeutic_alignment: float
    suggested_corrections: list[str]
```

#### `ConsistencyIssue`
Represents a detected consistency problem.

```python
@dataclass
class ConsistencyIssue:
    issue_id: str
    issue_type: ConsistencyIssueType
    severity: ValidationSeverity
    description: str
    affected_elements: list[str]
    suggested_fix: str
    confidence_score: float
```

---

## Usage Examples

### Basic Coherence Validation

```python
from src.components.narrative_coherence import CoherenceValidator, NarrativeContent

# Initialize validator
validator = CoherenceValidator()

# Create narrative content
content = NarrativeContent(
    content_id="scene_001",
    content_type="dialogue",
    text="The wizard cast a fireball spell...",
    related_characters=["wizard_merlin"],
    related_locations=["enchanted_forest"],
    themes=["magic", "conflict"]
)

# Validate coherence
result = await validator.validate_coherence(
    content=content,
    lore_database=lore_db,
    character_profiles=char_profiles,
    world_rules=world_rules
)

# Check results
if result.is_valid:
    print(f"Content is coherent (score: {result.consistency_score})")
else:
    print(f"Issues found: {len(result.detected_issues)}")
    for issue in result.detected_issues:
        print(f"- {issue.description}")
        print(f"  Suggested fix: {issue.suggested_fix}")
```

### Causal Validation

```python
from src.components.narrative_coherence import CausalValidator

# Initialize causal validator
causal_validator = CausalValidator()

# Validate causal relationships in a narrative branch
result = await causal_validator.validate_causal_consistency(
    narrative_branch=[content1, content2, content3]
)

print(f"Causal consistency score: {result.causal_consistency}")
```

### Contradiction Detection

```python
from src.components.narrative_coherence import ContradictionDetector

# Initialize detector
detector = ContradictionDetector()

# Detect contradictions across content history
contradictions = await detector.detect_contradictions(
    content_history=[content1, content2, content3, content4]
)

for contradiction in contradictions:
    print(f"Contradiction: {contradiction.description}")
    print(f"Severity: {contradiction.severity}")
    print("Resolution suggestions:")
    for suggestion in contradiction.resolution_suggestions:
        print(f"  - {suggestion}")
```

---

## Configuration

### Validation Weights

Customize the importance of different validation aspects:

```python
from src.components.narrative_coherence.rules import OVERALL_WEIGHTS

# Default weights
OVERALL_WEIGHTS = {
    "lore": 0.3,
    "character": 0.25,
    "causal": 0.25,
    "therapeutic": 0.2
}
```

### Severity Thresholds

Configure when issues should be flagged:

```python
from src.components.narrative_coherence.models import ValidationSeverity

# Severity levels
ValidationSeverity.INFO       # Informational only
ValidationSeverity.WARNING    # Should be reviewed
ValidationSeverity.ERROR      # Must be fixed
ValidationSeverity.CRITICAL   # Blocks progression
```

---

## Testing

### Unit Tests

```bash
# Run all narrative coherence tests
uvx pytest tests/test_narrative_coherence_engine.py -v

# Run with coverage
uvx pytest tests/test_narrative_coherence_engine.py --cov=src/components/narrative_coherence
```

### Test Coverage

**Current Coverage**: 100%

**Test Files**:
- `tests/test_narrative_coherence_engine.py` - Comprehensive unit tests

**Key Test Scenarios**:
- Lore compliance validation
- Character consistency checking
- Causal relationship validation
- Contradiction detection
- Creative solution generation

---

## Dependencies

- **Python**: 3.11+
- **Core Dependencies**: None (self-contained)
- **Optional Dependencies**:
  - Neo4j: For lore database integration
  - Redis: For caching validation results

---

## Performance

### Validation Speed
- **Single Content**: <50ms (p95)
- **Batch Validation (10 items)**: <200ms (p95)
- **Contradiction Detection (100 items)**: <1s (p95)

### Resource Usage
- **Memory**: ~50MB baseline
- **CPU**: Minimal (validation is I/O bound)

---

## Security

**Last Security Scan**: 2025-10-08
**Security Issues**: 0 (all severity levels)

The component has no external dependencies and operates on validated input data, minimizing security risks.

---

## Promotion Status

### Development → Staging Criteria

- [x] Core features complete (100% of planned functionality)
- [x] Unit tests passing (100% coverage)
- [x] API documented, no planned breaking changes
- [x] Passes linting (3 optional PERF401 warnings)
- [x] Passes type checking (0 errors)
- [x] Passes security scan (0 issues)
- [x] Component README with usage examples
- [x] All dependencies identified and stable
- [x] Successfully integrates with dependent components

**Status**: 9/9 criteria met ✅

**Blockers**: None (Issue #39 resolved)

---

## Related Documentation

- **Maturity Status**: `src/components/narrative_coherence/MATURITY.md`
- **API Documentation**: See inline docstrings and type hints
- **Architecture**: `Documentation/components/narrative-coherence/`
- **GitHub Issue**: [#39 - Promotion Blocker](https://github.com/theinterneti/TTA/issues/39)

---

## Contributing

When modifying this component:

1. Maintain 100% test coverage
2. Follow type hints strictly
3. Update this README for API changes
4. Run full validation suite before committing
5. Update MATURITY.md for significant changes

---

**Last Updated By**: theinterneti
**Last Review Date**: 2025-10-08
