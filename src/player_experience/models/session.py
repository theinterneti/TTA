"""
Session management and dashboard data models.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from .enums import SessionStatus, ProgressMarkerType, TherapeuticApproach


@dataclass
class ProgressMarker:
    """Individual progress marker within a session."""
    marker_id: str
    marker_type: ProgressMarkerType
    description: str
    achieved_at: datetime
    therapeutic_value: float = 0.0  # 0.0 to 1.0
    related_goal_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate progress marker after initialization."""
        if not 0.0 <= self.therapeutic_value <= 1.0:
            raise ValueError("Therapeutic value must be between 0.0 and 1.0")


@dataclass
class TherapeuticSettings:
    """Settings for therapeutic content delivery in a session."""
    intensity_level: float = 0.5  # 0.0 to 1.0
    preferred_approaches: List[TherapeuticApproach] = field(default_factory=list)
    intervention_frequency: str = "balanced"  # minimal, balanced, frequent
    feedback_sensitivity: float = 0.5  # 0.0 to 1.0
    crisis_monitoring_enabled: bool = True
    adaptive_difficulty: bool = True
    
    def __post_init__(self):
        """Validate therapeutic settings after initialization."""
        if not 0.0 <= self.intensity_level <= 1.0:
            raise ValueError("Intensity level must be between 0.0 and 1.0")
        
        if not 0.0 <= self.feedback_sensitivity <= 1.0:
            raise ValueError("Feedback sensitivity must be between 0.0 and 1.0")
        
        valid_frequencies = ["minimal", "balanced", "frequent"]
        if self.intervention_frequency not in valid_frequencies:
            raise ValueError(f"Intervention frequency must be one of: {valid_frequencies}")


@dataclass
class SessionContext:
    """Complete context for an active therapeutic session."""
    session_id: str
    player_id: str
    character_id: str
    world_id: str
    therapeutic_settings: TherapeuticSettings
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_interaction: datetime = field(default_factory=datetime.now)
    progress_markers: List[ProgressMarker] = field(default_factory=list)
    
    # Session state
    current_scene_id: Optional[str] = None
    session_variables: Dict[str, Any] = field(default_factory=dict)
    interaction_count: int = 0
    total_duration_minutes: int = 0
    
    # Therapeutic tracking
    therapeutic_interventions_used: List[str] = field(default_factory=list)
    emotional_state_history: List[Dict[str, Any]] = field(default_factory=list)
    crisis_alerts_triggered: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate session context after initialization."""
        if not self.session_id:
            raise ValueError("Session ID cannot be empty")
        
        if not self.player_id:
            raise ValueError("Player ID cannot be empty")
        
        if not self.character_id:
            raise ValueError("Character ID cannot be empty")
        
        if not self.world_id:
            raise ValueError("World ID cannot be empty")
    
    def add_progress_marker(self, marker: ProgressMarker) -> None:
        """Add a progress marker to the session."""
        self.progress_markers.append(marker)
    
    def update_interaction(self) -> None:
        """Update session interaction statistics."""
        self.last_interaction = datetime.now()
        self.interaction_count += 1
    
    def add_therapeutic_intervention(self, intervention_name: str) -> None:
        """Record a therapeutic intervention used in the session."""
        if intervention_name not in self.therapeutic_interventions_used:
            self.therapeutic_interventions_used.append(intervention_name)
    
    def record_emotional_state(self, emotional_data: Dict[str, Any]) -> None:
        """Record emotional state data for the session."""
        emotional_entry = {
            "timestamp": datetime.now(),
            "data": emotional_data
        }
        self.emotional_state_history.append(emotional_entry)
    
    def trigger_crisis_alert(self, alert_data: Dict[str, Any]) -> None:
        """Record a crisis alert for the session."""
        crisis_entry = {
            "timestamp": datetime.now(),
            "alert_data": alert_data,
            "resolved": False
        }
        self.crisis_alerts_triggered.append(crisis_entry)
    
    def get_session_duration(self) -> timedelta:
        """Get the total duration of the session."""
        return self.last_interaction - self.created_at
    
    def is_active(self) -> bool:
        """Check if the session is currently active."""
        return self.status == SessionStatus.ACTIVE


@dataclass
class SessionSummary:
    """Summary of a completed or paused session."""
    session_id: str
    character_name: str
    world_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: int
    status: SessionStatus
    progress_markers_count: int
    therapeutic_interventions_count: int
    emotional_highlights: List[str] = field(default_factory=list)
    key_achievements: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate session summary after initialization."""
        if self.duration_minutes < 0:
            raise ValueError("Duration cannot be negative")


@dataclass
class Recommendation:
    """Personalized recommendation for a player."""
    recommendation_id: str
    title: str
    description: str
    recommendation_type: str  # world, character, therapeutic_approach, etc.
    priority: int = 1  # 1 (high) to 5 (low)
    target_entity_id: Optional[str] = None  # ID of recommended world, character, etc.
    reasoning: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_dismissed: bool = False
    
    def __post_init__(self):
        """Validate recommendation after initialization."""
        if not 1 <= self.priority <= 5:
            raise ValueError("Priority must be between 1 and 5")


@dataclass
class PlayerDashboard:
    """Complete dashboard data for a player."""
    player_id: str
    active_characters: List[Dict[str, Any]] = field(default_factory=list)  # Character summaries
    recent_sessions: List[SessionSummary] = field(default_factory=list)
    progress_highlights: List[str] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    upcoming_milestones: List[str] = field(default_factory=list)
    
    # Quick stats
    total_session_time_today: int = 0  # minutes
    current_streak_days: int = 0
    next_recommended_session: Optional[datetime] = None
    
    # Therapeutic insights
    most_effective_approach: Optional[TherapeuticApproach] = None
    preferred_session_time: Optional[str] = None  # "morning", "afternoon", "evening"
    therapeutic_momentum: float = 0.5  # 0.0 to 1.0
    
    generated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate player dashboard after initialization."""
        if not self.player_id:
            raise ValueError("Player ID cannot be empty")
        
        if not 0.0 <= self.therapeutic_momentum <= 1.0:
            raise ValueError("Therapeutic momentum must be between 0.0 and 1.0")
    
    def add_recommendation(self, recommendation: Recommendation) -> None:
        """Add a recommendation to the dashboard."""
        # Remove any existing recommendation with the same ID
        self.recommendations = [r for r in self.recommendations if r.recommendation_id != recommendation.recommendation_id]
        self.recommendations.append(recommendation)
        
        # Sort by priority (1 = highest priority)
        self.recommendations.sort(key=lambda r: r.priority)
    
    def dismiss_recommendation(self, recommendation_id: str) -> None:
        """Dismiss a recommendation."""
        for recommendation in self.recommendations:
            if recommendation.recommendation_id == recommendation_id:
                recommendation.is_dismissed = True
                break
    
    def get_active_recommendations(self) -> List[Recommendation]:
        """Get all non-dismissed, non-expired recommendations."""
        now = datetime.now()
        return [
            r for r in self.recommendations 
            if not r.is_dismissed and (r.expires_at is None or r.expires_at > now)
        ]