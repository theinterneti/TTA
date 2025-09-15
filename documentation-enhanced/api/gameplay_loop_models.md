# Gameplay Loop Data Models

This document describes the comprehensive data model architecture for the TTA (Therapeutic Text Adventure) gameplay loop system.

## Overview

The gameplay loop data models provide a robust foundation for therapeutic gaming experiences, encompassing user interactions, progress tracking, narrative management, and safety validation. All models are built using Pydantic 2.0+ for comprehensive validation and serialization.

## Core Models

### GameplaySession
The central model representing a complete therapeutic gameplay session.

**Key Features:**
- Session state management (initializing, active, paused, completed, error)
- Therapeutic goal tracking
- Safety level monitoring (standard, elevated, crisis)
- Comprehensive session metrics
- Scene and choice history tracking

**Usage:**
```python
session = GameplaySession(
    user_id="user123",
    therapeutic_goals=["anxiety_management", "social_skills"],
    safety_level="standard"
)
```

### NarrativeScene
Represents individual scenes within the therapeutic narrative.

**Key Features:**
- Scene type classification (exploration, dialogue, therapeutic_moment, etc.)
- Therapeutic focus areas
- Emotional tone mapping
- Available user choices
- Safety considerations

### UserChoice
Models user decisions and their therapeutic implications.

**Key Features:**
- Choice type categorization (narrative, therapeutic, emotional, etc.)
- Therapeutic relevance scoring (0.0-1.0)
- Emotional weight assessment
- Difficulty level tracking
- Consequence management

### TherapeuticOutcome
Captures therapeutic benefits from gameplay interactions.

**Key Features:**
- Outcome type classification
- Therapeutic value scoring
- Skills practiced tracking
- Emotional growth measurement
- Behavioral insights

## Interaction Models

### UserInteraction
Comprehensive model for all user interactions during gameplay.

**Key Features:**
- Interaction type classification (text_input, choice_selection, etc.)
- Context-aware processing
- Validation and response management
- Safety assessment
- Processing time tracking

### InteractionValidation
Validates user interactions for safety and therapeutic appropriateness.

**Key Features:**
- Multi-dimensional scoring (safety, therapeutic relevance, emotional appropriateness)
- Status classification (valid, invalid, requires_review, safety_concern)
- Automated safety concern detection
- Human review flagging

### InteractionResponse
Models system responses to user interactions.

**Key Features:**
- Response type classification (acknowledgment, therapeutic_guidance, etc.)
- Therapeutic intent tracking
- Emotional tone management
- Follow-up action planning

## Progress Tracking Models

### TherapeuticProgress
Comprehensive progress tracking across multiple dimensions.

**Key Features:**
- Multi-metric progress assessment
- Skill development tracking
- Emotional growth monitoring
- Behavioral change measurement
- Milestone achievement

### ProgressMetric
Individual progress measurements with baseline and target tracking.

**Key Features:**
- Progress type classification
- Baseline to target progression
- Confidence level assessment
- Update frequency management
- Improvement detection

### SkillDevelopment
Tracks development of specific therapeutic skills.

**Key Features:**
- Skill level progression (novice to expert)
- Proficiency scoring
- Practice session tracking
- Learning objective management
- Mastery indicator assessment

### EmotionalGrowth
Monitors emotional regulation and awareness development.

**Key Features:**
- Emotion-specific tracking
- Regulation, awareness, and expression scoring
- Coping strategy effectiveness
- Trigger pattern identification
- Breakthrough moment recording

### BehavioralChange
Tracks behavioral modifications and pattern changes.

**Key Features:**
- Behavior frequency monitoring
- Change type classification (increase, decrease, modify)
- Trigger and intervention tracking
- Environmental factor consideration
- Progress percentage calculation

## Validation Models

### ValidationRule
Defines rules for content and interaction validation.

**Key Features:**
- Rule type classification (safety, therapeutic alignment, etc.)
- Context-aware application
- Severity level management
- Cultural and age considerations
- Remediation suggestions

### SafetyCheck
Comprehensive safety assessment for all content.

**Key Features:**
- Safety level classification (safe to crisis)
- Risk and protective factor identification
- Crisis indicator detection
- Intervention recommendations
- Human review requirements

### TherapeuticAlignment
Assesses therapeutic value and alignment of content.

**Key Features:**
- Alignment type classification
- Therapeutic goal mapping
- Skill and benefit identification
- Contraindication detection
- Evidence-based assessment

### ContentValidation
Comprehensive validation results for gameplay content.

**Key Features:**
- Multi-dimensional validation scoring
- Approval status management
- Blocking issue identification
- Revision requirement assessment
- Ready-for-use determination

## Validation and Safety Features

All models include comprehensive validation:

- **Range Validation**: Scores constrained to 0.0-1.0 range
- **Enum Validation**: Strict type checking for categorical fields
- **Cross-Field Validation**: Consistency checks across related fields
- **Safety Validation**: Automatic safety assessment integration
- **Therapeutic Validation**: Alignment with therapeutic goals

## Serialization and Persistence

Models support:
- **JSON Serialization**: Full Pydantic serialization support
- **Database Persistence**: Compatible with Neo4j and Redis storage
- **API Integration**: Direct FastAPI integration support
- **Validation Errors**: Comprehensive error reporting

## Usage Patterns

### Creating a Gameplay Session
```python
session = GameplaySession(
    user_id="user123",
    therapeutic_goals=["anxiety_management"],
    safety_level="standard"
)

# Add a scene
scene = NarrativeScene(
    session_id=session.session_id,
    title="Peaceful Garden",
    description="A calming garden scene",
    narrative_content="You find yourself in a peaceful garden...",
    therapeutic_focus=["mindfulness", "grounding"]
)

session.add_scene(scene)
```

### Processing User Interactions
```python
context = InteractionContext(
    session_id=session.session_id,
    user_emotional_state={"anxiety": 0.6, "curiosity": 0.4}
)

interaction = UserInteraction(
    session_id=session.session_id,
    user_id="user123",
    interaction_type=InteractionType.TEXT_INPUT,
    content="I'm feeling nervous about this situation",
    context=context
)

# Validate interaction
validation = InteractionValidation(
    interaction_id=interaction.interaction_id,
    status=ValidationStatus.VALID,
    safety_score=0.9,
    therapeutic_relevance=0.8,
    emotional_appropriateness=0.7
)

interaction.add_validation(validation)
```

### Tracking Progress
```python
progress = TherapeuticProgress(
    user_id="user123",
    session_id=session.session_id
)

# Add skill development
skill = SkillDevelopment(
    skill_name="Deep Breathing",
    skill_category="Anxiety Management",
    current_level=SkillLevel.DEVELOPING,
    proficiency_score=0.6
)

progress.skill_developments.append(skill)
```

## Integration Points

The models integrate seamlessly with:
- **Neo4j Graph Database**: For relationship and narrative tracking
- **Redis Cache**: For session state and real-time data
- **Therapeutic Safety System**: For content validation
- **Agent Orchestration**: For AI-driven interactions
- **Progress Monitoring**: For therapeutic effectiveness tracking

## Testing

Comprehensive test coverage includes:
- **Unit Tests**: Individual model validation and behavior
- **Integration Tests**: Cross-model interactions
- **Validation Tests**: Edge cases and error conditions
- **Performance Tests**: Serialization and processing speed

All tests use pytest with appropriate markers for database integration testing.
