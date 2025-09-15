# Narrative Engine Architecture

This document describes the comprehensive narrative engine architecture for the TTA (Therapeutic Text Adventure) system, including scene management, choice processing, flow control, and therapeutic integration.

## Overview

The Narrative Engine is the core orchestrator that manages therapeutic text adventure experiences. It integrates with the Neo4j graph database for persistent narrative structure, Redis for real-time session management, and provides comprehensive therapeutic safety and progress tracking.

## Core Components

### 1. Narrative Engine (Main Orchestrator)

The `NarrativeEngine` class serves as the main coordinator for all narrative operations:

**Key Features:**
- Session lifecycle management (start, pause, resume, end)
- Component coordination (scene manager, choice processor, flow controller)
- Event-driven architecture with comprehensive event bus
- Background safety monitoring and session cleanup
- Metrics tracking and performance monitoring

**Operating Modes:**
- **GUIDED**: Structured, therapeutically focused experiences
- **EXPLORATORY**: Open-ended, user-driven narratives
- **CRISIS**: Safety-focused with immediate support options
- **REFLECTION**: Processing and integration focused
- **ADAPTIVE**: AI-driven adaptation based on user progress

**Engine States:**
- INITIALIZING → READY → RUNNING → PAUSED/COMPLETED/ERROR → SHUTDOWN

### 2. Event System

**Event Types:**
- **Scene Events**: SCENE_ENTERED, SCENE_EXITED, SCENE_COMPLETED
- **Choice Events**: CHOICE_PRESENTED, CHOICE_MADE, CHOICE_PROCESSED
- **Progress Events**: PROGRESS_UPDATED, MILESTONE_ACHIEVED, SKILL_DEVELOPED
- **Safety Events**: SAFETY_CONCERN_DETECTED, CRISIS_INTERVENTION_NEEDED
- **Flow Events**: NARRATIVE_STARTED, BRANCH_TAKEN, NARRATIVE_COMPLETED

**Event Bus Features:**
- Asynchronous event publishing and handling
- Event history tracking with configurable retention
- Priority-based event processing
- Error handling and retry mechanisms
- Subscriber management with type-based filtering

### 3. Scene Manager

Handles individual scene logic, transitions, and state management:

**Scene Context Tracking:**
- Entry time and duration tracking
- User interaction logging
- Therapeutic moment recording
- Emotional response monitoring
- Engagement score calculation

**Scene Validation:**
- Content length and quality checks
- Therapeutic focus validation
- Safety assessment integration
- Scene type verification

**Performance Metrics:**
- Completion rates and engagement scores
- Time spent analysis
- Therapeutic moment frequency
- User interaction patterns

### 4. Choice Processor

Processes user choices with comprehensive validation and consequence application:

**Choice Validation:**
- Safety score calculation
- Therapeutic alignment assessment
- Crisis mode restrictions
- Choice type validation

**Validation Results:**
- VALID: Choice passes all validation checks
- INVALID: Choice fails basic validation
- REQUIRES_CONFIRMATION: Choice needs user confirmation
- SAFETY_CONCERN: Choice has safety implications
- THERAPEUTIC_MISMATCH: Choice doesn't align with therapeutic goals

**Consequence Processing:**
- Immediate and delayed consequence application
- Narrative variable updates
- Emotional state modifications
- Progress impact calculation
- Therapeutic moment triggering

### 5. Flow Controller (Stub Implementation)

Manages narrative flow control and branching logic:

**Planned Features:**
- Scene transition validation
- Branching logic evaluation
- Narrative path optimization
- Conditional flow management
- Initial scene selection

### 6. Therapeutic Integrator (Stub Implementation)

Ensures therapeutic alignment and safety monitoring:

**Planned Features:**
- Session therapeutic context initialization
- Real-time safety monitoring
- Progress tracking integration
- Crisis intervention triggering
- Therapeutic goal alignment validation

## Data Models

### Session State Integration

The narrative engine integrates seamlessly with the Redis-based session state management:

```python
# Session state updates during narrative progression
session_state.add_scene(scene_id)
session_state.add_choice(choice_id)
session_state.update_emotional_state(emotion, intensity)
session_state.set_narrative_variable(key, value)
```

### Scene Context

Comprehensive scene context tracking:

```python
@dataclass
class SceneContext:
    scene: NarrativeScene
    session_state: SessionState
    status: SceneStatus
    variables: Dict[str, Any]
    therapeutic_moments: List[Dict[str, Any]]
    emotional_responses: Dict[str, float]
    engagement_score: float
```

### Choice Context

Detailed choice processing context:

```python
@dataclass
class ChoiceContext:
    choice: UserChoice
    session_state: SessionState
    validation_result: ChoiceValidationResult
    therapeutic_alignment: float
    safety_score: float
    emotional_impact: Dict[str, float]
    progress_impact: Dict[str, float]
```

## Integration Architecture

### Database Integration

**Neo4j Graph Database:**
- Persistent narrative structure storage
- Scene and choice relationship mapping
- Therapeutic goal and skill connections
- Progress tracking and milestone recording

**Redis Session Management:**
- Real-time session state persistence
- Narrative context caching
- Progress snapshot storage
- Session lifecycle management

### Event-Driven Communication

The narrative engine uses a comprehensive event system for decoupled communication:

```python
# Event publishing
event = create_scene_event(
    EventType.SCENE_ENTERED,
    session_id, user_id, scene_id,
    scene_type, therapeutic_focus
)
await event_bus.publish(event)

# Event subscription
event_bus.subscribe(EventType.THERAPEUTIC_MOMENT, handle_therapeutic_moment)
```

### Safety and Validation Pipeline

1. **Content Validation**: Scene and choice content validation
2. **Safety Assessment**: Risk factor analysis and protective factor identification
3. **Therapeutic Alignment**: Goal alignment and relevance scoring
4. **Crisis Detection**: Real-time monitoring for crisis situations
5. **Intervention Triggering**: Automatic safety intervention activation

## Configuration and Customization

### Engine Configuration

```python
config = NarrativeEngineConfig(
    mode=NarrativeMode.GUIDED,
    max_concurrent_sessions=100,
    enable_safety_monitoring=True,
    crisis_intervention_threshold=0.8,
    therapeutic_alignment_threshold=0.6,
    cache_scenes=True,
    preload_choices=True
)
```

### Validation Rules

```python
validation_rules = {
    "min_therapeutic_relevance": 0.3,
    "max_risk_tolerance": 0.7,
    "required_safety_score": 0.5,
    "crisis_mode_restrictions": True
}
```

## Performance and Scalability

### Caching Strategy

- **Scene Caching**: Configurable scene caching for performance
- **Choice Preloading**: Preload available choices for faster response
- **Context Caching**: Scene and choice context caching
- **Event History**: Configurable event history retention

### Background Processing

- **Safety Monitoring**: Continuous background safety assessment
- **Session Cleanup**: Automatic expired session cleanup
- **Delayed Consequences**: Asynchronous consequence processing
- **Metrics Collection**: Real-time performance metrics tracking

### Metrics and Monitoring

```python
metrics = {
    "sessions_started": 0,
    "sessions_completed": 0,
    "scenes_processed": 0,
    "choices_made": 0,
    "safety_interventions": 0,
    "therapeutic_moments": 0
}
```

## Usage Examples

### Starting a Narrative Session

```python
# Initialize engine
engine = NarrativeEngine(config, session_manager, database_manager)
await engine.initialize()

# Start session
session = GameplaySession(
    user_id="user_123",
    therapeutic_goals=["anxiety_management", "social_skills"],
    safety_level="standard"
)
success = await engine.start_session(session)
```

### Processing User Choices

```python
# Process user choice
success = await engine.process_choice(session_id, choice_id)

# Check validation results
context = await choice_processor.validate_choice(choice, session_state)
if context.validation_result == ChoiceValidationResult.VALID:
    # Apply consequences
    await choice_processor.apply_consequences(context)
```

### Scene Transitions

```python
# Enter new scene
success = await engine.enter_scene(session_id, scene_id)

# Get scene context
context = await scene_manager.get_scene_context(session_id, scene_id)
engagement_score = context.engagement_score
```

## Testing Strategy

### Unit Tests

- Event system functionality
- Scene and choice validation
- Context tracking and metrics
- Configuration and state management

### Integration Tests

- Database integration (Neo4j and Redis)
- Event bus communication
- Session lifecycle management
- Safety and validation pipelines

### Performance Tests

- Concurrent session handling
- Event processing throughput
- Cache performance and hit rates
- Memory usage and cleanup

## Future Enhancements

### Planned Features

1. **Advanced Flow Controller**: Complete implementation with sophisticated branching logic
2. **Enhanced Therapeutic Integrator**: Real-time therapeutic assessment and adaptation
3. **AI-Driven Adaptation**: Machine learning-based narrative personalization
4. **Advanced Analytics**: Comprehensive therapeutic outcome analysis
5. **Multi-Modal Support**: Integration with voice, visual, and haptic interfaces

### Extensibility Points

- **Custom Validation Rules**: Pluggable validation rule system
- **Event Handler Plugins**: Custom event processing extensions
- **Therapeutic Modules**: Specialized therapeutic intervention modules
- **Narrative Loaders**: Support for various narrative definition formats
- **Analytics Integrations**: Custom analytics and reporting systems

## Security and Privacy

### Data Protection

- Sensitive therapeutic data encryption
- Secure session token management
- Privacy-preserving analytics
- Audit logging for compliance

### Safety Measures

- Real-time crisis detection
- Automatic safety intervention
- Human oversight integration
- Emergency contact systems

The Narrative Engine provides a comprehensive, scalable, and therapeutically-focused foundation for interactive text adventures, with robust safety measures, extensive customization options, and seamless integration with the broader TTA system architecture.
