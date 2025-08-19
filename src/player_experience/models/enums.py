"""
Enumerations used throughout the Player Experience Interface.
"""

from enum import Enum, auto


class IntensityLevel(Enum):
    """Therapeutic intensity levels for personalized experiences."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TherapeuticApproach(Enum):
    """Available therapeutic approaches in the system."""
    CBT = "cognitive_behavioral_therapy"
    NARRATIVE_THERAPY = "narrative_therapy"
    MINDFULNESS = "mindfulness"
    ACCEPTANCE_COMMITMENT = "acceptance_commitment_therapy"
    DIALECTICAL_BEHAVIORAL = "dialectical_behavioral_therapy"
    SOLUTION_FOCUSED = "solution_focused_therapy"
    HUMANISTIC = "humanistic_therapy"
    BEHAVIORAL_ACTIVATION = "behavioral_activation"
    SKILL_BUILDING = "skill_building"
    INSIGHT_ORIENTED = "insight_oriented"


class DifficultyLevel(Enum):
    """Difficulty levels for worlds and therapeutic content."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CrisisType(Enum):
    """Types of crisis situations that may require intervention."""
    SUICIDAL_IDEATION = "suicidal_ideation"
    SELF_HARM = "self_harm"
    PANIC_ATTACK = "panic_attack"
    SEVERE_DEPRESSION = "severe_depression"
    TRAUMA_RESPONSE = "trauma_response"
    SUBSTANCE_ABUSE = "substance_abuse"
    GENERAL_DISTRESS = "general_distress"


class SessionStatus(Enum):
    """Status of therapeutic sessions."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ProgressMarkerType(Enum):
    """Types of progress markers for tracking therapeutic advancement."""
    MILESTONE = "milestone"
    BREAKTHROUGH = "breakthrough"
    SKILL_ACQUIRED = "skill_acquired"
    GOAL_ACHIEVED = "goal_achieved"
    SETBACK_OVERCOME = "setback_overcome"
    INSIGHT = "insight"
    THERAPEUTIC_GOAL = "therapeutic_goal"