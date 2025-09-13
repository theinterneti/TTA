"""
Data models for the TTA Living Worlds system.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class WorldStateType(Enum):
    """Types of world states."""
    ACTIVE = "active"
    PAUSED = "paused"
    EVOLVING = "evolving"
    ARCHIVED = "archived"


class ChoiceImpactType(Enum):
    """Types of choice impacts."""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    CASCADING = "cascading"
    THERAPEUTIC = "therapeutic"


class EvolutionTrigger(Enum):
    """Triggers for world evolution."""
    PLAYER_ACTION = "player_action"
    TIME_PASSAGE = "time_passage"
    THERAPEUTIC_MILESTONE = "therapeutic_milestone"
    NARRATIVE_REQUIREMENT = "narrative_requirement"


@dataclass
class WorldState:
    """Represents the current state of a living world."""
    
    world_id: str
    session_id: str
    player_id: str
    state_type: WorldStateType = WorldStateType.ACTIVE
    
    # World properties
    world_properties: Dict[str, Any] = field(default_factory=dict)
    character_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    location_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    object_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Therapeutic context
    therapeutic_context: Dict[str, Any] = field(default_factory=dict)
    therapeutic_goals: List[str] = field(default_factory=list)
    therapeutic_progress: Dict[str, float] = field(default_factory=dict)
    
    # Evolution tracking
    evolution_preference_bias: Dict[str, float] = field(default_factory=dict)
    recent_events: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    version: int = 1


@dataclass
class ChoiceImpact:
    """Represents the impact of a player choice on the world."""
    
    impact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    choice_id: str = ""
    player_id: str = ""
    world_id: str = ""
    
    impact_type: ChoiceImpactType = ChoiceImpactType.IMMEDIATE
    scope: List[str] = field(default_factory=list)  # affected entities
    strength: float = 0.5  # 0.0 to 1.0
    
    # Impact details
    affected_characters: List[str] = field(default_factory=list)
    affected_locations: List[str] = field(default_factory=list)
    affected_objects: List[str] = field(default_factory=list)
    
    # Consequences
    immediate_consequences: Dict[str, Any] = field(default_factory=dict)
    delayed_consequences: Dict[str, Any] = field(default_factory=dict)
    therapeutic_consequences: Dict[str, Any] = field(default_factory=dict)
    
    # Feedback
    feedback_summary: str = ""
    world_evolution_guidance: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TherapeuticWorld:
    """Represents a therapeutically designed world environment."""
    
    world_id: str
    name: str
    description: str
    
    # Therapeutic design
    therapeutic_themes: List[str] = field(default_factory=list)
    therapeutic_approaches: List[str] = field(default_factory=list)
    therapeutic_techniques: List[str] = field(default_factory=list)
    
    # World structure
    key_locations: List[Dict[str, Any]] = field(default_factory=list)
    key_characters: List[Dict[str, Any]] = field(default_factory=list)
    narrative_elements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Therapeutic configuration
    safety_guidelines: Dict[str, Any] = field(default_factory=dict)
    crisis_protocols: Dict[str, Any] = field(default_factory=dict)
    progress_milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    is_active: bool = True


@dataclass
class EvolutionEvent:
    """Represents an event in world evolution."""
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    world_id: str = ""
    trigger: EvolutionTrigger = EvolutionTrigger.TIME_PASSAGE
    
    # Event details
    event_type: str = ""
    event_description: str = ""
    affected_entities: List[str] = field(default_factory=list)
    
    # Changes
    state_changes: Dict[str, Any] = field(default_factory=dict)
    narrative_changes: Dict[str, Any] = field(default_factory=dict)
    therapeutic_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed: bool = False
    processing_result: Optional[Dict[str, Any]] = None


@dataclass
class WorldPersistenceData:
    """Data structure for persisting world state across sessions."""
    
    world_id: str
    player_id: str
    session_ids: List[str] = field(default_factory=list)
    
    # Persistent state
    persistent_world_state: Dict[str, Any] = field(default_factory=dict)
    character_continuity: Dict[str, Any] = field(default_factory=dict)
    narrative_continuity: Dict[str, Any] = field(default_factory=dict)
    therapeutic_continuity: Dict[str, Any] = field(default_factory=dict)
    
    # Evolution history
    evolution_history: List[str] = field(default_factory=list)  # event IDs
    choice_impact_history: List[str] = field(default_factory=list)  # impact IDs
    
    # Metadata
    first_session: datetime = field(default_factory=datetime.utcnow)
    last_session: datetime = field(default_factory=datetime.utcnow)
    total_sessions: int = 0
    total_playtime: float = 0.0  # in hours
