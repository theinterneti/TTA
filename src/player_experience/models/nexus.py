"""
Nexus Codex Data Models.

This module defines the data models for The Nexus Codex therapeutic gaming platform,
extending the existing TTA models with world creation and narrative management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum
import uuid

from pydantic import BaseModel, Field
from .enums import DifficultyLevel, TherapeuticApproach


class GenreType(Enum):
    """Available world genres in the Nexus Codex."""
    FANTASY = "fantasy"
    SCI_FI = "sci-fi"
    CONTEMPORARY = "contemporary"
    HISTORICAL = "historical"
    HYBRID = "hybrid"
    POST_APOCALYPTIC = "post-apocalyptic"
    MYSTERY = "mystery"
    ADVENTURE = "adventure"


class NarrativeState(Enum):
    """States of narrative strength in worlds."""
    ACTIVE = "active"
    THREATENED = "threatened"
    STRENGTHENED = "strengthened"
    DORMANT = "dormant"


class VisualState(Enum):
    """Visual states for story spheres in the Nexus."""
    BRIGHT_GLOW = "bright_glow"
    GENTLE_PULSE = "gentle_pulse"
    DIM_FLICKER = "dim_flicker"
    DARK_VOID = "dark_void"


@dataclass
class NexusCodex:
    """The central Nexus Codex hub containing all story worlds."""
    codex_id: str = "central_nexus"
    name: str = "The Nexus Codex"
    total_worlds: int = 0
    active_story_weavers: int = 0
    silence_threat_level: float = 0.1  # 0.0 to 1.0
    narrative_strength: float = 1.0    # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate Nexus Codex data."""
        if not 0.0 <= self.silence_threat_level <= 1.0:
            raise ValueError("Silence threat level must be between 0.0 and 1.0")
        if not 0.0 <= self.narrative_strength <= 1.0:
            raise ValueError("Narrative strength must be between 0.0 and 1.0")


@dataclass
class StoryWorld:
    """A therapeutic gaming world within the Nexus Codex."""
    world_id: str
    title: str
    description: str
    genre: GenreType
    therapeutic_focus: List[str] = field(default_factory=list)
    narrative_state: NarrativeState = NarrativeState.ACTIVE
    creator_id: str = ""
    strength_level: float = 0.5        # 0.0 to 1.0
    silence_threat: float = 0.1        # 0.0 to 1.0
    completion_rate: float = 0.0       # 0.0 to 1.0
    therapeutic_efficacy: float = 0.0  # 0.0 to 1.0
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    estimated_duration: int = 45       # minutes
    player_count: int = 0
    rating: float = 0.0               # 0.0 to 5.0
    tags: List[str] = field(default_factory=list)
    is_public: bool = True
    is_featured: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Extended world properties
    long_description: str = ""
    setting_description: str = ""
    key_characters: List[Dict[str, str]] = field(default_factory=list)
    main_storylines: List[str] = field(default_factory=list)
    therapeutic_techniques_used: List[str] = field(default_factory=list)
    content_warnings: List[str] = field(default_factory=list)
    world_parameters: Dict[str, Any] = field(default_factory=dict)
    narrative_structure: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate story world data."""
        if not self.world_id:
            self.world_id = str(uuid.uuid4())
        
        if not self.title or len(self.title.strip()) < 3:
            raise ValueError("World title must be at least 3 characters long")
        
        if not 0.0 <= self.strength_level <= 1.0:
            raise ValueError("Strength level must be between 0.0 and 1.0")
        
        if not 0.0 <= self.silence_threat <= 1.0:
            raise ValueError("Silence threat must be between 0.0 and 1.0")
        
        if not 0.0 <= self.completion_rate <= 1.0:
            raise ValueError("Completion rate must be between 0.0 and 1.0")
        
        if not 0.0 <= self.therapeutic_efficacy <= 1.0:
            raise ValueError("Therapeutic efficacy must be between 0.0 and 1.0")
        
        if not 0.0 <= self.rating <= 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        
        if not 10 <= self.estimated_duration <= 180:
            raise ValueError("Estimated duration must be between 10 and 180 minutes")
    
    def get_visual_state(self) -> VisualState:
        """Determine visual state based on strength level."""
        if self.strength_level > 0.8:
            return VisualState.BRIGHT_GLOW
        elif self.strength_level > 0.5:
            return VisualState.GENTLE_PULSE
        elif self.strength_level > 0.2:
            return VisualState.DIM_FLICKER
        else:
            return VisualState.DARK_VOID
    
    def calculate_therapeutic_score(self) -> float:
        """Calculate overall therapeutic effectiveness score."""
        factors = [
            self.therapeutic_efficacy * 0.4,
            self.completion_rate * 0.3,
            (self.rating / 5.0) * 0.2,
            self.strength_level * 0.1
        ]
        return sum(factors)


@dataclass
class StorySphere:
    """Visual representation of a StoryWorld in the Nexus."""
    sphere_id: str
    world_id: str
    visual_state: VisualState = VisualState.GENTLE_PULSE
    pulse_frequency: float = 0.5       # 0.0 to 1.0
    connection_strength: float = 0.5   # 0.0 to 1.0
    position_x: float = 0.0
    position_y: float = 0.0
    position_z: float = 0.0
    color_primary: str = "#2E86AB"
    color_secondary: str = "#FFFFFF"
    size_scale: float = 1.0
    
    def __post_init__(self):
        """Validate story sphere data."""
        if not self.sphere_id:
            self.sphere_id = f"{self.world_id}_sphere"
        
        if not 0.0 <= self.pulse_frequency <= 1.0:
            raise ValueError("Pulse frequency must be between 0.0 and 1.0")
        
        if not 0.0 <= self.connection_strength <= 1.0:
            raise ValueError("Connection strength must be between 0.0 and 1.0")
        
        if not 0.1 <= self.size_scale <= 3.0:
            raise ValueError("Size scale must be between 0.1 and 3.0")


@dataclass
class StoryWeaver:
    """Extended player profile for Nexus Codex participation."""
    weaver_id: str
    player_id: str
    nexus_level: int = 1
    worlds_created: int = 0
    worlds_completed: int = 0
    stories_strengthened: int = 0
    therapeutic_impact_score: float = 0.0
    preferred_genres: List[GenreType] = field(default_factory=list)
    creation_specialties: List[str] = field(default_factory=list)
    community_reputation: float = 0.0  # 0.0 to 5.0
    mentor_status: bool = False
    total_play_time: int = 0           # minutes
    achievements: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate story weaver data."""
        if not self.weaver_id:
            self.weaver_id = f"{self.player_id}_weaver"
        
        if not self.player_id:
            raise ValueError("Player ID is required")
        
        if self.nexus_level < 1:
            raise ValueError("Nexus level must be at least 1")
        
        if not 0.0 <= self.therapeutic_impact_score <= 10.0:
            raise ValueError("Therapeutic impact score must be between 0.0 and 10.0")
        
        if not 0.0 <= self.community_reputation <= 5.0:
            raise ValueError("Community reputation must be between 0.0 and 5.0")
    
    def calculate_experience_level(self) -> str:
        """Calculate experience level based on activity."""
        if self.worlds_created >= 10 and self.stories_strengthened >= 50:
            return "Master Weaver"
        elif self.worlds_created >= 5 and self.stories_strengthened >= 20:
            return "Expert Weaver"
        elif self.worlds_created >= 2 and self.stories_strengthened >= 10:
            return "Skilled Weaver"
        elif self.worlds_created >= 1 or self.stories_strengthened >= 5:
            return "Apprentice Weaver"
        else:
            return "Novice Weaver"


@dataclass
class WorldTemplate:
    """Reusable template for world creation."""
    template_id: str
    name: str
    description: str
    genre: GenreType
    therapeutic_goals: List[str] = field(default_factory=list)
    narrative_structure: Dict[str, Any] = field(default_factory=dict)
    character_archetypes: List[Dict[str, Any]] = field(default_factory=list)
    world_parameters: Dict[str, Any] = field(default_factory=dict)
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    estimated_creation_time: int = 30  # minutes
    usage_count: int = 0
    success_rate: float = 0.0          # 0.0 to 1.0
    creator_id: str = ""
    is_official: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate world template data."""
        if not self.template_id:
            self.template_id = str(uuid.uuid4())
        
        if not self.name or len(self.name.strip()) < 3:
            raise ValueError("Template name must be at least 3 characters long")
        
        if not 0.0 <= self.success_rate <= 1.0:
            raise ValueError("Success rate must be between 0.0 and 1.0")
        
        if not 5 <= self.estimated_creation_time <= 120:
            raise ValueError("Estimated creation time must be between 5 and 120 minutes")


@dataclass
class WorldConnection:
    """Connection between two story worlds."""
    connection_id: str
    source_world_id: str
    target_world_id: str
    connection_type: str  # sequel, prequel, crossover, thematic
    connection_strength: float = 0.5   # 0.0 to 1.0
    bidirectional: bool = False
    narrative_bridge: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate world connection data."""
        if not self.connection_id:
            self.connection_id = str(uuid.uuid4())
        
        if not 0.0 <= self.connection_strength <= 1.0:
            raise ValueError("Connection strength must be between 0.0 and 1.0")
        
        valid_types = ["sequel", "prequel", "crossover", "thematic"]
        if self.connection_type not in valid_types:
            raise ValueError(f"Connection type must be one of: {valid_types}")


@dataclass
class ActivityEvent:
    """Community activity event in the Nexus."""
    event_id: str
    event_type: str  # world_created, world_completed, achievement_earned, etc.
    user_id: str
    user_name: str
    world_id: Optional[str] = None
    world_title: Optional[str] = None
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    likes_count: int = 0
    comments_count: int = 0
    is_featured: bool = False
    
    def __post_init__(self):
        """Validate activity event data."""
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        
        valid_types = [
            "world_created", "world_completed", "achievement_earned",
            "world_strengthened", "collaboration_started", "milestone_reached"
        ]
        if self.event_type not in valid_types:
            raise ValueError(f"Event type must be one of: {valid_types}")


@dataclass
class WorldReview:
    """User review of a story world."""
    review_id: str
    world_id: str
    user_id: str
    rating: float                      # 1.0 to 5.0
    review_text: str = ""
    therapeutic_effectiveness: float = 0.0  # 1.0 to 5.0
    engagement_level: float = 0.0      # 1.0 to 5.0
    would_recommend: bool = True
    completed_world: bool = False
    helpful_votes: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    moderation_status: str = "pending"  # pending, approved, rejected
    
    def __post_init__(self):
        """Validate world review data."""
        if not self.review_id:
            self.review_id = str(uuid.uuid4())
        
        if not 1.0 <= self.rating <= 5.0:
            raise ValueError("Rating must be between 1.0 and 5.0")
        
        if self.therapeutic_effectiveness and not 1.0 <= self.therapeutic_effectiveness <= 5.0:
            raise ValueError("Therapeutic effectiveness must be between 1.0 and 5.0")
        
        if self.engagement_level and not 1.0 <= self.engagement_level <= 5.0:
            raise ValueError("Engagement level must be between 1.0 and 5.0")
        
        valid_statuses = ["pending", "approved", "rejected"]
        if self.moderation_status not in valid_statuses:
            raise ValueError(f"Moderation status must be one of: {valid_statuses}")


# Response models for API endpoints
@dataclass
class NexusStateResponse:
    """Response model for Nexus Codex state."""
    codex_id: str
    total_worlds: int
    active_story_weavers: int
    silence_threat_level: float
    narrative_strength: float
    featured_worlds: List[Dict[str, Any]] = field(default_factory=list)
    recent_activity: List[ActivityEvent] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class WorldCreationRequest(BaseModel):
    """Request model for creating a new world."""
    title: str
    description: str
    genre: GenreType
    therapeutic_focus: List[str]
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    estimated_duration: int = 45
    is_public: bool = True
    template_id: Optional[str] = None
    world_parameters: Dict[str, Any] = Field(default_factory=dict)
    narrative_structure: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class WorldSearchRequest:
    """Request model for searching worlds."""
    query: Optional[str] = None
    genre: Optional[GenreType] = None
    therapeutic_focus: Optional[List[str]] = None
    difficulty: Optional[DifficultyLevel] = None
    duration_min: Optional[int] = None
    duration_max: Optional[int] = None
    rating_min: Optional[float] = None
    sort_by: str = "rating"  # rating, popularity, recent, therapeutic_efficacy
    limit: int = 20
    offset: int = 0
