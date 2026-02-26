# Gameplay Loop Component

The `gameplay_loop` component implements the complete therapeutic text adventure gameplay
loop, coordinating narrative presentation, choice architecture, consequence processing,
and adaptive difficulty for a mental-health-support game experience.

## Sub-modules

### `models/`

Pure Pydantic models and dataclasses shared across the entire component.

| Module | Key Classes |
|---|---|
| `core.py` | `Scene`, `Choice`, `ConsequenceSet`, `SessionState`, `GameplayMetrics`, `TherapeuticContext` — plus enums `DifficultyLevel`, `EmotionalState`, `SceneType`, `ChoiceType` |
| `interactions.py` | `UserChoice`, `ChoiceOutcome`, `NarrativeEvent`, `TherapeuticIntervention`, `AgencyAssessment`, `GameplaySession` |
| `progress.py` | `ProgressMarker`, `SkillDevelopment`, `CharacterState`, `TherapeuticProgress` — plus enums `ProgressType`, `SkillCategory`, `CharacterAttribute` |
| `validation.py` | `ValidationResult`, `SafetyCheck`, `TherapeuticValidation`, `ContentValidation` — plus enums `ValidationStatus`, `SafetyLevel`, `ValidationType` |

### `choice_architecture/`

Manages generation, filtering, and validation of player choices.

- `ChoiceArchitectureManager` — orchestrates choice generation and agency protection.
- `ChoiceValidator` — validates each choice for safety, therapeutic appropriateness,
  emotional-state suitability, and minimum quality thresholds.

### `narrative/`

Generates narrative content, scene descriptions, and story progression.

- `NarrativeEngine` — generates opening scenes, next scenes, and adapts narrative
  complexity/pacing to the player's current state.

### `consequence_system/`

Converts player choices into rich, therapeutically framed outcomes.

| Class | Responsibility |
|---|---|
| `ConsequenceSystem` | Orchestrates all consequence sub-systems |
| `OutcomeGenerator` | Generates logical immediate and delayed outcomes |
| `TherapeuticFramer` | Reframes every outcome as a learning and growth opportunity |
| `CausalityExplainer` | Produces clear cause-and-effect narratives |
| `ProgressTracker` | Tracks therapeutic progress milestones from choices |

### `database/`

Persistence layer for session state and gameplay history.

- `Neo4jGameplayManager` — stores and retrieves sessions, choices, and narrative events
  in Neo4j; uses Redis for caching.

## Key Classes

### `GameplayLoopController`

The top-level orchestrator for a player's gameplay session. Holds references to all
sub-components and manages the session lifecycle.

**Responsibilities:**
- Starting, resuming, pausing, and ending sessions.
- Routing player choice input through validation → consequence generation → scene
  generation → next-choice generation.
- Tracking response times and cleaning up idle sessions.

### `SessionState`

A Pydantic model holding the full in-memory state of one therapeutic session:
current scene, choice history, emotional state, therapeutic context, and metrics.

### `ChoiceValidator`

Validates whether a given `Choice` is appropriate given the current `Scene` and
`SessionState`. Checks safety criteria, therapeutic value thresholds, emotional-state
rules, and scene-type alignment. Must be initialized via `await validator.initialize()`
before use.

### `TherapeuticFramer`

Takes raw consequence outcomes and wraps them in psychologically constructive framing:
generating insights, learning opportunities, growth aspects, and positive reframes.
Adapts its language to the player's current emotional state.

## How to Use GameplayLoopController

```python
from src.components.gameplay_loop import GameplayLoopController

# 1. Instantiate with optional config
controller = GameplayLoopController(config={
    "database": {
        "neo4j_uri": "bolt://localhost:7688",
        "neo4j_user": "neo4j",
        "neo4j_password": "password",
        "redis_url": "redis://localhost:6379",
    },
    "session_timeout": 3600,
    "response_time_target": 2.0,
})

# 2. Initialize all sub-components
await controller.initialize()

# 3. Start a session
session = await controller.start_session(
    user_id="player-001",
    therapeutic_context={"primary_goals": ["anxiety_management"]},
)

# 4. Process player choices
next_scene, new_choices, consequences = await controller.process_user_choice(
    session_id=session.session_id,
    choice_id=session.available_choices[0].choice_id,
)

# 5. Pause / resume / end
await controller.pause_session(session.session_id)
resumed = await controller.resume_session(session.session_id)
await controller.end_session(session.session_id)
```

## Quick Example: Validate a Choice

```python
from src.components.gameplay_loop.choice_architecture.validator import ChoiceValidator
from src.components.gameplay_loop.models.core import Choice, ChoiceType, Scene, SessionState

validator = ChoiceValidator()
await validator.initialize()

scene = Scene(title="Forest Path", description="...", narrative_content="...")
session = SessionState(user_id="player-001")
choice = Choice(
    choice_text="Breathe deeply",
    choice_type=ChoiceType.THERAPEUTIC,
    therapeutic_value=0.8,
    therapeutic_tags=["mindfulness"],
    agency_level=0.7,
    meaningfulness_score=0.6,
)

validated = await validator.validate_choices([choice], scene, session)
# validated contains only choices that pass all criteria
```
