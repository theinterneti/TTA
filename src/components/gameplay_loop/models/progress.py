"""
Progress Tracking Models

This module defines data structures for tracking therapeutic progress,
skill development, emotional growth, and behavioral changes.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class ProgressType(str, Enum):
    """Types of therapeutic progress."""
    SKILL_DEVELOPMENT = "skill_development"
    EMOTIONAL_GROWTH = "emotional_growth"
    BEHAVIORAL_CHANGE = "behavioral_change"
    COGNITIVE_INSIGHT = "cognitive_insight"
    RELATIONSHIP_IMPROVEMENT = "relationship_improvement"
    COPING_STRATEGY = "coping_strategy"
    SELF_AWARENESS = "self_awareness"


class MilestoneType(str, Enum):
    """Types of progress milestones."""
    BREAKTHROUGH = "breakthrough"
    SKILL_MASTERY = "skill_mastery"
    EMOTIONAL_REGULATION = "emotional_regulation"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    THERAPEUTIC_GOAL = "therapeutic_goal"
    CRISIS_MANAGEMENT = "crisis_management"
    RELATIONSHIP_MILESTONE = "relationship_milestone"


class SkillLevel(str, Enum):
    """Levels of skill development."""
    NOVICE = "novice"
    DEVELOPING = "developing"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"


class ProgressMetric(BaseModel):
    """Individual progress metric tracking."""
    metric_id: str = Field(default_factory=lambda: str(uuid4()))
    metric_name: str = Field(..., description="Name of the progress metric")
    progress_type: ProgressType = Field(..., description="Type of progress being tracked")
    current_value: float = Field(..., ge=0.0, le=1.0, description="Current progress value (0.0-1.0)")
    baseline_value: float = Field(default=0.0, ge=0.0, le=1.0, description="Starting baseline value")
    target_value: float = Field(default=1.0, ge=0.0, le=1.0, description="Target progress value")
    measurement_unit: str = Field(default="score", description="Unit of measurement")
    measurement_method: str = Field(..., description="How this metric is measured")
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in measurement")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    update_frequency: timedelta = Field(default=timedelta(days=7), description="How often to update")
    
    @field_validator('current_value', 'baseline_value', 'target_value', 'confidence_level')
    @classmethod
    def validate_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    def calculate_progress_percentage(self) -> float:
        """Calculate progress as percentage from baseline to target."""
        if self.target_value == self.baseline_value:
            return 1.0 if self.current_value >= self.target_value else 0.0
        
        progress = (self.current_value - self.baseline_value) / (self.target_value - self.baseline_value)
        return max(0.0, min(1.0, progress))
    
    def is_improving(self) -> bool:
        """Check if metric shows improvement from baseline."""
        return self.current_value > self.baseline_value
    
    def needs_update(self) -> bool:
        """Check if metric needs updating based on frequency."""
        return datetime.utcnow() - self.last_updated >= self.update_frequency


class SkillDevelopment(BaseModel):
    """Tracking of specific skill development."""
    skill_id: str = Field(default_factory=lambda: str(uuid4()))
    skill_name: str = Field(..., description="Name of the skill")
    skill_category: str = Field(..., description="Category of the skill")
    current_level: SkillLevel = Field(default=SkillLevel.NOVICE)
    proficiency_score: float = Field(default=0.0, ge=0.0, le=1.0)
    practice_sessions: int = Field(default=0, description="Number of practice sessions")
    successful_applications: int = Field(default=0, description="Successful real-world applications")
    learning_objectives: List[str] = Field(default_factory=list)
    completed_objectives: List[str] = Field(default_factory=list)
    practice_opportunities: List[str] = Field(default_factory=list)
    mastery_indicators: List[str] = Field(default_factory=list)
    development_notes: List[str] = Field(default_factory=list)
    last_practiced: Optional[datetime] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('proficiency_score')
    @classmethod
    def validate_proficiency_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Proficiency score must be between 0.0 and 1.0')
        return v
    
    def advance_level(self) -> bool:
        """Advance skill level if criteria are met."""
        level_requirements = {
            SkillLevel.NOVICE: 0.2,
            SkillLevel.DEVELOPING: 0.4,
            SkillLevel.COMPETENT: 0.6,
            SkillLevel.PROFICIENT: 0.8,
            SkillLevel.EXPERT: 1.0
        }
        
        current_threshold = level_requirements.get(self.current_level, 1.0)
        if self.proficiency_score >= current_threshold and self.practice_sessions >= 3:
            levels = list(SkillLevel)
            current_index = levels.index(self.current_level)
            if current_index < len(levels) - 1:
                self.current_level = levels[current_index + 1]
                return True
        return False


class EmotionalGrowth(BaseModel):
    """Tracking of emotional growth and regulation."""
    growth_id: str = Field(default_factory=lambda: str(uuid4()))
    emotion_category: str = Field(..., description="Category of emotion (e.g., anxiety, anger)")
    regulation_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Emotional regulation ability")
    awareness_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Emotional awareness level")
    expression_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Healthy expression ability")
    coping_strategies: List[str] = Field(default_factory=list)
    effective_strategies: List[str] = Field(default_factory=list)
    trigger_patterns: List[str] = Field(default_factory=list)
    growth_indicators: List[str] = Field(default_factory=list)
    emotional_incidents: int = Field(default=0, description="Number of emotional incidents")
    successful_regulations: int = Field(default=0, description="Successful regulation instances")
    breakthrough_moments: List[str] = Field(default_factory=list)
    last_incident: Optional[datetime] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('regulation_score', 'awareness_score', 'expression_score')
    @classmethod
    def validate_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    def calculate_overall_growth(self) -> float:
        """Calculate overall emotional growth score."""
        return (self.regulation_score + self.awareness_score + self.expression_score) / 3.0
    
    def add_successful_regulation(self, strategy: str) -> None:
        """Record a successful emotional regulation."""
        self.successful_regulations += 1
        if strategy not in self.effective_strategies:
            self.effective_strategies.append(strategy)


class BehavioralChange(BaseModel):
    """Tracking of behavioral changes and patterns."""
    change_id: str = Field(default_factory=lambda: str(uuid4()))
    behavior_name: str = Field(..., description="Name of the behavior being tracked")
    change_type: str = Field(..., description="Type of change (increase, decrease, modify)")
    target_behavior: str = Field(..., description="Desired behavior outcome")
    baseline_frequency: float = Field(default=0.0, description="Baseline frequency of behavior")
    current_frequency: float = Field(default=0.0, description="Current frequency of behavior")
    target_frequency: float = Field(..., description="Target frequency of behavior")
    measurement_period: str = Field(default="weekly", description="Measurement period")
    behavior_triggers: List[str] = Field(default_factory=list)
    intervention_strategies: List[str] = Field(default_factory=list)
    successful_interventions: int = Field(default=0)
    behavior_incidents: int = Field(default=0)
    pattern_observations: List[str] = Field(default_factory=list)
    environmental_factors: List[str] = Field(default_factory=list)
    last_occurrence: Optional[datetime] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_change_percentage(self) -> float:
        """Calculate percentage change from baseline."""
        if self.baseline_frequency == 0:
            return 1.0 if self.current_frequency > 0 else 0.0
        
        return (self.current_frequency - self.baseline_frequency) / self.baseline_frequency
    
    def is_improving(self) -> bool:
        """Check if behavior is improving toward target."""
        if self.change_type == "increase":
            return self.current_frequency > self.baseline_frequency
        elif self.change_type == "decrease":
            return self.current_frequency < self.baseline_frequency
        else:  # modify
            target_diff = abs(self.target_frequency - self.baseline_frequency)
            current_diff = abs(self.current_frequency - self.target_frequency)
            baseline_diff = abs(self.baseline_frequency - self.target_frequency)
            return current_diff < baseline_diff


class ProgressMilestone(BaseModel):
    """Significant milestone in therapeutic progress."""
    milestone_id: str = Field(default_factory=lambda: str(uuid4()))
    milestone_type: MilestoneType = Field(..., description="Type of milestone")
    title: str = Field(..., description="Title of the milestone")
    description: str = Field(..., description="Detailed description")
    achievement_criteria: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    therapeutic_significance: float = Field(..., ge=0.0, le=1.0, description="Therapeutic significance")
    celebration_content: Optional[str] = Field(None, description="Content for celebrating milestone")
    related_skills: List[str] = Field(default_factory=list)
    related_goals: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    achieved_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('therapeutic_significance')
    @classmethod
    def validate_therapeutic_significance(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Therapeutic significance must be between 0.0 and 1.0')
        return v


class TherapeuticProgress(BaseModel):
    """Comprehensive therapeutic progress tracking."""
    progress_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(..., description="ID of the user")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    progress_metrics: List[ProgressMetric] = Field(default_factory=list)
    skill_developments: List[SkillDevelopment] = Field(default_factory=list)
    emotional_growth: List[EmotionalGrowth] = Field(default_factory=list)
    behavioral_changes: List[BehavioralChange] = Field(default_factory=list)
    milestones: List[ProgressMilestone] = Field(default_factory=list)
    overall_progress_score: float = Field(default=0.0, ge=0.0, le=1.0)
    therapeutic_momentum: float = Field(default=0.5, ge=0.0, le=1.0)
    engagement_level: float = Field(default=0.5, ge=0.0, le=1.0)
    progress_notes: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('overall_progress_score', 'therapeutic_momentum', 'engagement_level')
    @classmethod
    def validate_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    def calculate_overall_progress(self) -> float:
        """Calculate overall progress score from all metrics."""
        if not self.progress_metrics:
            return 0.0
        
        total_progress = sum(metric.calculate_progress_percentage() for metric in self.progress_metrics)
        return total_progress / len(self.progress_metrics)
    
    def get_recent_milestones(self, days: int = 30) -> List[ProgressMilestone]:
        """Get milestones achieved in the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [
            milestone for milestone in self.milestones
            if milestone.achieved_at >= cutoff_date
        ]
    
    def needs_attention(self) -> bool:
        """Check if progress needs therapeutic attention."""
        return (
            self.overall_progress_score < 0.3 or
            self.therapeutic_momentum < 0.3 or
            self.engagement_level < 0.4
        )
