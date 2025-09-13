# Player Experience Interface

This module provides the player-facing interface for the TTA (Therapeutic Text Adventure) system, enabling players to create and manage characters, select worlds, customize their therapeutic experience, and interact with the system through a web-based interface.

## Project Structure

```
src/player_experience/
├── __init__.py                 # Main module exports
├── README.md                   # This documentation
├── models/                     # Data models
│   ├── __init__.py            # Model exports
│   ├── enums.py               # Enumerations and constants
│   ├── player.py              # Player profile models
│   ├── character.py           # Character and therapeutic models
│   ├── world.py               # World and compatibility models
│   ├── session.py             # Session management models
│   └── progress.py            # Progress tracking models
├── managers/                   # Business logic services
│   ├── __init__.py            # Manager exports
│   ├── player_experience_manager.py      # Central orchestrator
│   ├── character_avatar_manager.py       # Character management
│   ├── world_management_module.py        # World selection
│   ├── personalization_service_manager.py # Therapeutic personalization
│   └── session_integration_manager.py    # Session management
├── api/                       # Web API layer (to be implemented)
│   └── __init__.py
└── utils/                     # Utility functions
    ├── __init__.py
    ├── validation.py          # Data validation utilities
    └── serialization.py       # JSON serialization support
```

## Core Data Models

### Player Models (`models/player.py`)
- **PlayerProfile**: Complete player profile with therapeutic preferences and privacy settings
- **TherapeuticPreferences**: Player's therapeutic intensity, approaches, and boundaries
- **PrivacySettings**: Data collection, retention, and sharing preferences
- **CrisisContactInfo**: Emergency contact information for crisis situations

### Character Models (`models/character.py`)
- **Character**: Complete character with appearance, background, and therapeutic profile
- **CharacterAppearance**: Physical appearance and visual characteristics
- **CharacterBackground**: Backstory, personality traits, and relationships
- **TherapeuticProfile**: Character's therapeutic goals and treatment preferences
- **TherapeuticGoal**: Individual therapeutic objectives with progress tracking

### World Models (`models/world.py`)
- **WorldSummary**: Basic world information for browsing and selection
- **WorldDetails**: Comprehensive world information with therapeutic content
- **WorldParameters**: Customizable parameters for world instances
- **CompatibilityReport**: Character-world compatibility assessment
- **CompatibilityFactor**: Individual compatibility scoring factors

### Session Models (`models/session.py`)
- **SessionContext**: Complete therapeutic session state and context
- **TherapeuticSettings**: Real-time therapeutic delivery settings
- **ProgressMarker**: Individual progress achievements within sessions
- **PlayerDashboard**: Aggregated dashboard data for players
- **Recommendation**: Personalized recommendations for players

### Progress Models (`models/progress.py`)
- **ProgressSummary**: Comprehensive progress tracking for players
- **ProgressHighlight**: Significant achievements and breakthroughs
- **Milestone**: Therapeutic milestones with progress tracking
- **EngagementMetrics**: Player engagement and participation statistics
- **TherapeuticEffectivenessReport**: Therapeutic outcome assessments

## Key Features Implemented

### 1. Comprehensive Data Validation
- Input sanitization and format validation
- Business rule enforcement (e.g., character limits, therapeutic intensity ranges)
- Cross-field validation and consistency checks
- Custom validation exceptions with detailed error messages

### 2. Robust Serialization Support
- JSON serialization/deserialization for all data models
- Custom encoders for datetime, timedelta, and enum types
- Schema generation for API documentation
- Type-safe deserialization with validation

### 3. Therapeutic Safety Features
- Crisis contact information management
- Trigger warning and content filtering
- Therapeutic intensity controls
- Privacy and data protection settings

### 4. Character Management
- Up to 5 characters per player
- Rich character customization (appearance, background, personality)
- Therapeutic goal setting and progress tracking
- Character-specific therapeutic profiles

### 5. World Compatibility System
- Algorithmic compatibility scoring between characters and worlds
- Prerequisite checking and recommendations
- Customizable world parameters
- Safety-first content matching

### 6. Session State Management
- Complete session context preservation
- Character-world switching support
- Progress marker tracking
- Therapeutic intervention recording

## Validation Rules

### Player Profiles
- Username: 3-30 characters, alphanumeric with underscores/hyphens
- Email: Valid email format required
- Character limit: Maximum 5 characters per player
- Data retention: 30 days to 7 years

### Characters
- Name: 2-50 characters, letters/spaces/hyphens/apostrophes only
- Therapeutic readiness: 0.0 to 1.0 scale
- Progress percentages: 0.0 to 100.0

### Therapeutic Settings
- Intensity levels: 0.0 to 1.0 scale
- Session duration: 10 to 120 minutes
- Rating scales: 0.0 to 5.0

## Usage Examples

### Creating a Player Profile
```python
from src.player_experience.models import PlayerProfile, TherapeuticPreferences
from datetime import datetime

# Create therapeutic preferences
prefs = TherapeuticPreferences(
    intensity_level=IntensityLevel.MEDIUM,
    preferred_approaches=[TherapeuticApproach.CBT, TherapeuticApproach.MINDFULNESS],
    trigger_warnings=["violence", "abandonment"],
    session_duration_preference=45
)

# Create player profile
profile = PlayerProfile(
    player_id="player_123",
    username="therapeutic_user",
    email="user@example.com",
    created_at=datetime.now(),
    therapeutic_preferences=prefs
)
```

### Creating a Character
```python
from src.player_experience.models import Character, CharacterAppearance, CharacterBackground, TherapeuticProfile

# Create character components
appearance = CharacterAppearance(
    age_range="adult",
    gender_identity="non-binary",
    physical_description="Tall with curly hair"
)

background = CharacterBackground(
    name="Alex Rivera",
    backstory="A teacher seeking work-life balance",
    personality_traits=["empathetic", "perfectionist", "creative"]
)

therapeutic_profile = TherapeuticProfile(
    primary_concerns=["anxiety", "work stress"],
    preferred_intensity=IntensityLevel.MEDIUM,
    readiness_level=0.7
)

# Create complete character
character = Character(
    character_id="char_123",
    player_id="player_123",
    name="Alex Rivera",
    appearance=appearance,
    background=background,
    therapeutic_profile=therapeutic_profile,
    created_at=datetime.now(),
    last_active=datetime.now()
)
```

### Serialization
```python
from src.player_experience.utils import serialize_model, deserialize_model

# Serialize to JSON
json_data = serialize_model(character)

# Deserialize from JSON
restored_character = deserialize_model(json_data, Character)
```

## Testing

Comprehensive test suite covers:
- Data model creation and validation
- Business rule enforcement
- Serialization/deserialization
- Error handling and edge cases

Run tests with:
```bash
python3 -m unittest tests.test_player_experience_models -v
```

## Integration Points

This module is designed to integrate with:
- **TTA Core Components**: PersonalizationEngine, CharacterDevelopmentSystem, etc.
- **Database Layer**: Neo4j for graph relationships, Redis for caching
- **Web API**: FastAPI-based REST and WebSocket services
- **Frontend**: React-based web interface

## Next Steps

The following components will be implemented in subsequent tasks:
1. **Manager Services**: Business logic implementation
2. **Web API Layer**: REST endpoints and WebSocket handlers
3. **Frontend Interface**: React-based user interface
4. **Database Integration**: Persistence and querying
5. **Security Features**: Authentication and authorization
6. **Monitoring**: Analytics and therapeutic effectiveness tracking

## Requirements Addressed

This implementation addresses the following requirements from the specification:
- **1.1, 1.4, 7.1**: Player profile and character creation with validation
- **Data Model Foundation**: Complete data structures for all player experience functionality
- **Validation Framework**: Comprehensive input validation and business rule enforcement
- **Serialization Support**: JSON serialization for API and storage integration
