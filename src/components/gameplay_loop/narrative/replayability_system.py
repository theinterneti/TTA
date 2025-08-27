"""
Replayability and Exploration System for Core Gameplay Loop

This module provides alternative path exploration, progress preservation during experimentation,
outcome comparison and learning insights, scenario restart capabilities, and comprehensive
integration with therapeutic and character development systems.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from uuid import uuid4
import json
import copy

from src.components.gameplay_loop.services.session_state import SessionState, SessionStateType
from src.components.gameplay_loop.models.core import UserChoice, ChoiceType, ConsequenceSet
from src.components.gameplay_loop.narrative.character_development_system import (
    CharacterDevelopmentSystem, CharacterAttribute, CharacterDevelopmentEvent
)
from .events import EventBus, EventType, NarrativeEvent


logger = logging.getLogger(__name__)


class ExplorationMode(str, Enum):
    """Types of exploration modes."""
    SANDBOX = "sandbox"  # Free exploration without consequences
    GUIDED = "guided"  # Guided exploration with learning insights
    COMPARATIVE = "comparative"  # Compare different approaches
    THERAPEUTIC = "therapeutic"  # Focus on therapeutic outcomes
    CHARACTER_FOCUSED = "character_focused"  # Focus on character development


class PathType(str, Enum):
    """Types of alternative paths."""
    CHOICE_ALTERNATIVE = "choice_alternative"
    THERAPEUTIC_APPROACH = "therapeutic_approach"
    CHARACTER_DEVELOPMENT = "character_development"
    EMOTIONAL_RESPONSE = "emotional_response"
    SKILL_APPLICATION = "skill_application"
    SCENARIO_VARIATION = "scenario_variation"


class ComparisonMetric(str, Enum):
    """Metrics for comparing different paths."""
    THERAPEUTIC_EFFECTIVENESS = "therapeutic_effectiveness"
    CHARACTER_GROWTH = "character_growth"
    EMOTIONAL_IMPACT = "emotional_impact"
    SKILL_DEVELOPMENT = "skill_development"
    ENGAGEMENT_LEVEL = "engagement_level"
    LEARNING_OUTCOMES = "learning_outcomes"
    STORY_SATISFACTION = "story_satisfaction"


@dataclass
class ExplorationSnapshot:
    """Snapshot of session state for exploration."""
    snapshot_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    user_id: str = ""
    
    # Snapshot metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    snapshot_name: str = ""
    description: str = ""
    
    # Session state snapshot
    session_state: Optional[SessionState] = None
    character_attributes: Dict[str, Any] = field(default_factory=dict)
    therapeutic_progress: Dict[str, Any] = field(default_factory=dict)
    
    # Context preservation
    scene_context: Dict[str, Any] = field(default_factory=dict)
    narrative_context: Dict[str, Any] = field(default_factory=dict)
    choice_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Exploration metadata
    exploration_mode: ExplorationMode = ExplorationMode.GUIDED
    parent_snapshot_id: Optional[str] = None
    branch_point_description: str = ""


@dataclass
class AlternativePath:
    """Represents an alternative path through the narrative."""
    path_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    user_id: str = ""
    
    # Path metadata
    path_type: PathType = PathType.CHOICE_ALTERNATIVE
    path_name: str = ""
    description: str = ""
    
    # Path definition
    starting_snapshot_id: str = ""
    choices_made: List[Dict[str, Any]] = field(default_factory=list)
    outcomes_achieved: List[Dict[str, Any]] = field(default_factory=list)
    
    # Path results
    therapeutic_outcomes: Dict[str, Any] = field(default_factory=dict)
    character_development: Dict[str, Any] = field(default_factory=dict)
    emotional_journey: List[Dict[str, Any]] = field(default_factory=list)
    
    # Path analytics
    completion_time_minutes: float = 0.0
    engagement_score: float = 0.0
    therapeutic_effectiveness: float = 0.0
    learning_value: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    is_completed: bool = False


@dataclass
class PathComparison:
    """Comparison between different alternative paths."""
    comparison_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    session_id: str = ""
    
    # Comparison metadata
    comparison_name: str = ""
    description: str = ""
    paths_compared: List[str] = field(default_factory=list)  # Path IDs
    
    # Comparison metrics
    metric_comparisons: Dict[ComparisonMetric, Dict[str, float]] = field(default_factory=dict)
    
    # Learning insights
    key_differences: List[str] = field(default_factory=list)
    therapeutic_insights: List[str] = field(default_factory=list)
    character_development_insights: List[str] = field(default_factory=list)
    
    # Recommendations
    recommended_approach: Optional[str] = None  # Path ID
    recommendation_reasoning: str = ""
    learning_opportunities: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExplorationSession:
    """Represents an exploration session with multiple paths."""
    exploration_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    base_session_id: str = ""
    
    # Exploration metadata
    exploration_name: str = ""
    exploration_mode: ExplorationMode = ExplorationMode.GUIDED
    focus_area: str = ""  # What aspect to focus exploration on
    
    # Exploration state
    base_snapshot_id: str = ""  # Starting point for exploration
    current_path_id: Optional[str] = None
    paths_explored: List[str] = field(default_factory=list)  # Path IDs
    
    # Exploration results
    comparisons_generated: List[str] = field(default_factory=list)  # Comparison IDs
    insights_discovered: List[str] = field(default_factory=list)
    learning_outcomes: Dict[str, Any] = field(default_factory=dict)
    
    # Session management
    is_active: bool = True
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ReplayabilitySystem:
    """Main system for alternative path exploration, outcome comparison, and therapeutic learning."""
    
    def __init__(self, event_bus: EventBus, character_development: CharacterDevelopmentSystem):
        self.event_bus = event_bus
        self.character_development = character_development
        
        # Exploration data storage
        self.exploration_snapshots: Dict[str, ExplorationSnapshot] = {}
        self.alternative_paths: Dict[str, AlternativePath] = {}
        self.path_comparisons: Dict[str, PathComparison] = {}
        self.exploration_sessions: Dict[str, ExplorationSession] = {}
        
        # User exploration tracking
        self.user_snapshots: Dict[str, List[str]] = {}  # user_id -> snapshot_ids
        self.user_paths: Dict[str, List[str]] = {}  # user_id -> path_ids
        self.user_explorations: Dict[str, List[str]] = {}  # user_id -> exploration_ids
        
        # Exploration configuration
        self.exploration_templates = self._load_exploration_templates()
        self.comparison_algorithms = self._load_comparison_algorithms()
        self.insight_generators = self._load_insight_generators()
        
        # Metrics
        self.metrics = {
            "snapshots_created": 0,
            "paths_explored": 0,
            "comparisons_generated": 0,
            "insights_discovered": 0,
            "exploration_sessions_started": 0,
            "therapeutic_learning_events": 0
        }
    
    def _load_exploration_templates(self) -> Dict[ExplorationMode, Dict[str, Any]]:
        """Load exploration templates for different modes."""
        return {
            ExplorationMode.SANDBOX: {
                "name": "Sandbox Exploration",
                "description": "Free exploration without permanent consequences",
                "features": ["unlimited_retries", "no_permanent_changes", "creative_freedom"],
                "guidance_level": "minimal",
                "learning_focus": "experimentation"
            },
            ExplorationMode.GUIDED: {
                "name": "Guided Exploration",
                "description": "Structured exploration with learning insights",
                "features": ["guided_choices", "learning_prompts", "insight_generation"],
                "guidance_level": "moderate",
                "learning_focus": "understanding"
            },
            ExplorationMode.COMPARATIVE: {
                "name": "Comparative Analysis",
                "description": "Compare different approaches and outcomes",
                "features": ["side_by_side_comparison", "outcome_analysis", "effectiveness_metrics"],
                "guidance_level": "analytical",
                "learning_focus": "evaluation"
            },
            ExplorationMode.THERAPEUTIC: {
                "name": "Therapeutic Focus",
                "description": "Focus on therapeutic outcomes and learning",
                "features": ["therapeutic_metrics", "clinical_insights", "progress_tracking"],
                "guidance_level": "therapeutic",
                "learning_focus": "therapeutic_growth"
            },
            ExplorationMode.CHARACTER_FOCUSED: {
                "name": "Character Development Focus",
                "description": "Focus on character growth and development paths",
                "features": ["character_progression", "attribute_tracking", "milestone_analysis"],
                "guidance_level": "developmental",
                "learning_focus": "character_growth"
            }
        }
    
    def _load_comparison_algorithms(self) -> Dict[ComparisonMetric, Dict[str, Any]]:
        """Load algorithms for comparing different paths."""
        return {
            ComparisonMetric.THERAPEUTIC_EFFECTIVENESS: {
                "weight_factors": {
                    "therapeutic_goals_achieved": 0.3,
                    "skills_practiced": 0.2,
                    "emotional_regulation": 0.2,
                    "insight_generation": 0.15,
                    "resistance_overcome": 0.15
                },
                "calculation_method": "weighted_sum",
                "normalization": "0_to_1_scale"
            },
            ComparisonMetric.CHARACTER_GROWTH: {
                "weight_factors": {
                    "attribute_improvements": 0.4,
                    "milestones_achieved": 0.3,
                    "abilities_unlocked": 0.2,
                    "growth_consistency": 0.1
                },
                "calculation_method": "weighted_sum",
                "normalization": "0_to_1_scale"
            },
            ComparisonMetric.EMOTIONAL_IMPACT: {
                "weight_factors": {
                    "emotional_intensity": 0.25,
                    "emotional_variety": 0.25,
                    "emotional_regulation": 0.25,
                    "emotional_growth": 0.25
                },
                "calculation_method": "weighted_sum",
                "normalization": "0_to_1_scale"
            },
            ComparisonMetric.ENGAGEMENT_LEVEL: {
                "weight_factors": {
                    "choice_frequency": 0.3,
                    "exploration_depth": 0.3,
                    "time_investment": 0.2,
                    "return_frequency": 0.2
                },
                "calculation_method": "weighted_sum",
                "normalization": "0_to_1_scale"
            }
        }
    
    def _load_insight_generators(self) -> Dict[str, Dict[str, Any]]:
        """Load insight generation templates."""
        return {
            "therapeutic_insights": {
                "patterns": [
                    "choice_outcome_patterns",
                    "therapeutic_approach_effectiveness",
                    "resistance_pattern_analysis",
                    "skill_application_success"
                ],
                "templates": [
                    "When you chose {choice}, it led to {outcome}, which suggests {insight}",
                    "Your {therapeutic_approach} approach was {effectiveness_level} effective because {reasoning}",
                    "Comparing your different approaches, {comparison_insight}"
                ]
            },
            "character_development_insights": {
                "patterns": [
                    "attribute_growth_patterns",
                    "milestone_achievement_paths",
                    "ability_unlock_sequences",
                    "development_consistency"
                ],
                "templates": [
                    "Your character's {attribute} grew most when you {action_pattern}",
                    "The path to {milestone} was achieved through {key_choices}",
                    "Different approaches led to {development_comparison}"
                ]
            },
            "learning_insights": {
                "patterns": [
                    "learning_effectiveness",
                    "skill_transfer",
                    "insight_application",
                    "growth_acceleration"
                ],
                "templates": [
                    "You learned most effectively when {learning_condition}",
                    "Skills from {source_area} transferred well to {target_area}",
                    "Your insights about {topic} led to {application_success}"
                ]
            }
        }

    async def create_exploration_snapshot(self, session_state: SessionState,
                                        snapshot_name: str = "",
                                        description: str = "") -> ExplorationSnapshot:
        """Create a snapshot of current session state for exploration."""
        try:
            # Create snapshot
            snapshot = ExplorationSnapshot(
                session_id=session_state.session_id,
                user_id=session_state.user_id,
                snapshot_name=snapshot_name or f"Snapshot at {datetime.utcnow().strftime('%H:%M')}",
                description=description or "Exploration starting point"
            )

            # Deep copy session state to preserve current state
            snapshot.session_state = copy.deepcopy(session_state)

            # Capture character development state
            if session_state.user_id in self.character_development.character_attributes:
                snapshot.character_attributes = {
                    attr.value: {
                        "current_level": attr_level.current_level,
                        "experience_points": attr_level.experience_points,
                        "level_progress": attr_level.level_progress,
                        "peak_level": attr_level.peak_level
                    }
                    for attr, attr_level in self.character_development.character_attributes[session_state.user_id].items()
                }

            # Capture therapeutic progress
            snapshot.therapeutic_progress = session_state.context.get("therapeutic_progress", {}).copy()

            # Capture scene and narrative context
            snapshot.scene_context = {
                "current_scene_id": session_state.current_scene_id,
                "scene_history": session_state.scene_history.copy(),
                "narrative_state": session_state.context.get("narrative_state", {}).copy()
            }

            snapshot.narrative_context = session_state.context.get("narrative_context", {}).copy()

            # Capture choice history
            snapshot.choice_history = [
                {
                    "choice_id": choice.choice_id if hasattr(choice, 'choice_id') else str(i),
                    "text": choice.text if hasattr(choice, 'text') else str(choice),
                    "choice_type": choice.choice_type.value if hasattr(choice, 'choice_type') else "unknown",
                    "timestamp": choice.timestamp.isoformat() if hasattr(choice, 'timestamp') else datetime.utcnow().isoformat()
                }
                for i, choice in enumerate(session_state.choice_history)
            ]

            # Store snapshot
            self.exploration_snapshots[snapshot.snapshot_id] = snapshot

            # Track user snapshots
            if session_state.user_id not in self.user_snapshots:
                self.user_snapshots[session_state.user_id] = []
            self.user_snapshots[session_state.user_id].append(snapshot.snapshot_id)

            # Publish snapshot creation event
            await self._publish_exploration_event(session_state, "snapshot_created", {
                "snapshot_id": snapshot.snapshot_id,
                "snapshot_name": snapshot.snapshot_name,
                "character_attributes_count": len(snapshot.character_attributes),
                "choice_history_length": len(snapshot.choice_history)
            })

            self.metrics["snapshots_created"] += 1

            return snapshot

        except Exception as e:
            logger.error(f"Failed to create exploration snapshot for session {session_state.session_id}: {e}")
            raise

    async def start_exploration_session(self, user_id: str, base_session_id: str,
                                      exploration_mode: ExplorationMode = ExplorationMode.GUIDED,
                                      focus_area: str = "") -> ExplorationSession:
        """Start a new exploration session."""
        try:
            # Create exploration session
            exploration = ExplorationSession(
                user_id=user_id,
                base_session_id=base_session_id,
                exploration_name=f"{exploration_mode.value.title()} Exploration",
                exploration_mode=exploration_mode,
                focus_area=focus_area or "general_exploration"
            )

            # Store exploration session
            self.exploration_sessions[exploration.exploration_id] = exploration

            # Track user explorations
            if user_id not in self.user_explorations:
                self.user_explorations[user_id] = []
            self.user_explorations[user_id].append(exploration.exploration_id)

            # Publish exploration start event
            await self._publish_exploration_event_by_user(user_id, "exploration_started", {
                "exploration_id": exploration.exploration_id,
                "exploration_mode": exploration_mode.value,
                "focus_area": focus_area
            })

            self.metrics["exploration_sessions_started"] += 1

            return exploration

        except Exception as e:
            logger.error(f"Failed to start exploration session for user {user_id}: {e}")
            raise

    async def create_alternative_path(self, exploration_id: str, starting_snapshot_id: str,
                                    path_type: PathType = PathType.CHOICE_ALTERNATIVE,
                                    path_name: str = "", description: str = "") -> AlternativePath:
        """Create a new alternative path for exploration."""
        try:
            # Get exploration session
            exploration = self.exploration_sessions.get(exploration_id)
            if not exploration:
                raise ValueError(f"Exploration session {exploration_id} not found")

            # Get starting snapshot
            snapshot = self.exploration_snapshots.get(starting_snapshot_id)
            if not snapshot:
                raise ValueError(f"Snapshot {starting_snapshot_id} not found")

            # Create alternative path
            path = AlternativePath(
                session_id=exploration.base_session_id,
                user_id=exploration.user_id,
                path_type=path_type,
                path_name=path_name or f"{path_type.value.title()} Path",
                description=description or f"Alternative path exploring {path_type.value}",
                starting_snapshot_id=starting_snapshot_id
            )

            # Store path
            self.alternative_paths[path.path_id] = path

            # Track user paths
            if exploration.user_id not in self.user_paths:
                self.user_paths[exploration.user_id] = []
            self.user_paths[exploration.user_id].append(path.path_id)

            # Update exploration session
            exploration.paths_explored.append(path.path_id)
            exploration.current_path_id = path.path_id
            exploration.last_activity = datetime.utcnow()

            # Publish path creation event
            await self._publish_exploration_event_by_user(exploration.user_id, "alternative_path_created", {
                "path_id": path.path_id,
                "path_type": path_type.value,
                "exploration_id": exploration_id,
                "starting_snapshot_id": starting_snapshot_id
            })

            self.metrics["paths_explored"] += 1

            return path

        except Exception as e:
            logger.error(f"Failed to create alternative path for exploration {exploration_id}: {e}")
            raise

    async def restore_from_snapshot(self, snapshot_id: str, target_session_state: SessionState) -> SessionState:
        """Restore session state from a snapshot."""
        try:
            # Get snapshot
            snapshot = self.exploration_snapshots.get(snapshot_id)
            if not snapshot:
                raise ValueError(f"Snapshot {snapshot_id} not found")

            if not snapshot.session_state:
                raise ValueError(f"Snapshot {snapshot_id} has no session state data")

            # Restore session state
            restored_state = copy.deepcopy(snapshot.session_state)

            # Update session ID to current session
            restored_state.session_id = target_session_state.session_id
            restored_state.last_activity = datetime.utcnow()

            # Restore character development state
            if snapshot.character_attributes and snapshot.user_id in self.character_development.character_attributes:
                for attr_name, attr_data in snapshot.character_attributes.items():
                    try:
                        attr = CharacterAttribute(attr_name)
                        if attr in self.character_development.character_attributes[snapshot.user_id]:
                            attr_level = self.character_development.character_attributes[snapshot.user_id][attr]
                            attr_level.current_level = attr_data["current_level"]
                            attr_level.experience_points = attr_data["experience_points"]
                            attr_level.level_progress = attr_data["level_progress"]
                            attr_level.peak_level = attr_data["peak_level"]
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to restore character attribute {attr_name}: {e}")

            # Restore therapeutic progress
            if snapshot.therapeutic_progress:
                restored_state.context["therapeutic_progress"] = snapshot.therapeutic_progress.copy()

            # Restore scene and narrative context
            if snapshot.scene_context:
                restored_state.current_scene_id = snapshot.scene_context.get("current_scene_id")
                restored_state.scene_history = snapshot.scene_context.get("scene_history", []).copy()
                if "narrative_state" in snapshot.scene_context:
                    restored_state.context["narrative_state"] = snapshot.scene_context["narrative_state"].copy()

            if snapshot.narrative_context:
                restored_state.context["narrative_context"] = snapshot.narrative_context.copy()

            # Mark as exploration state
            restored_state.context["exploration_mode"] = True
            restored_state.context["restored_from_snapshot"] = snapshot_id
            restored_state.context["exploration_timestamp"] = datetime.utcnow().isoformat()

            # Publish restoration event
            await self._publish_exploration_event(restored_state, "snapshot_restored", {
                "snapshot_id": snapshot_id,
                "snapshot_name": snapshot.snapshot_name,
                "restoration_timestamp": datetime.utcnow().isoformat()
            })

            return restored_state

        except Exception as e:
            logger.error(f"Failed to restore from snapshot {snapshot_id}: {e}")
            raise

    async def record_path_choice(self, path_id: str, choice: UserChoice, outcomes: List[Dict[str, Any]]) -> None:
        """Record a choice and its outcomes for an alternative path."""
        try:
            # Get path
            path = self.alternative_paths.get(path_id)
            if not path:
                raise ValueError(f"Alternative path {path_id} not found")

            # Record choice
            choice_record = {
                "choice_id": choice.choice_id if hasattr(choice, 'choice_id') else str(uuid4()),
                "text": choice.text,
                "choice_type": choice.choice_type.value,
                "therapeutic_relevance": getattr(choice, 'therapeutic_relevance', 0.0),
                "timestamp": datetime.utcnow().isoformat()
            }

            path.choices_made.append(choice_record)

            # Record outcomes
            for outcome in outcomes:
                outcome_record = {
                    "outcome_id": outcome.get("outcome_id", str(uuid4())),
                    "description": outcome.get("description", ""),
                    "outcome_type": outcome.get("outcome_type", "general"),
                    "therapeutic_value": outcome.get("therapeutic_value", 0.0),
                    "character_impact": outcome.get("character_impact", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }

                path.outcomes_achieved.append(outcome_record)

            # Update path analytics
            await self._update_path_analytics(path)

        except Exception as e:
            logger.error(f"Failed to record path choice for path {path_id}: {e}")

    async def complete_alternative_path(self, path_id: str, final_outcomes: Dict[str, Any]) -> AlternativePath:
        """Complete an alternative path and calculate final analytics."""
        try:
            # Get path
            path = self.alternative_paths.get(path_id)
            if not path:
                raise ValueError(f"Alternative path {path_id} not found")

            # Mark as completed
            path.is_completed = True
            path.completed_at = datetime.utcnow()

            # Calculate completion time
            path.completion_time_minutes = (path.completed_at - path.created_at).total_seconds() / 60

            # Store final outcomes
            path.therapeutic_outcomes = final_outcomes.get("therapeutic_outcomes", {})
            path.character_development = final_outcomes.get("character_development", {})
            path.emotional_journey = final_outcomes.get("emotional_journey", [])

            # Calculate final analytics
            await self._calculate_final_path_analytics(path)

            # Publish path completion event
            await self._publish_exploration_event_by_user(path.user_id, "alternative_path_completed", {
                "path_id": path.path_id,
                "path_type": path.path_type.value,
                "completion_time_minutes": path.completion_time_minutes,
                "therapeutic_effectiveness": path.therapeutic_effectiveness,
                "engagement_score": path.engagement_score
            })

            return path

        except Exception as e:
            logger.error(f"Failed to complete alternative path {path_id}: {e}")
            raise

    async def compare_paths(self, path_ids: List[str], comparison_name: str = "",
                          focus_metrics: List[ComparisonMetric] = None) -> PathComparison:
        """Compare multiple alternative paths and generate insights."""
        try:
            if len(path_ids) < 2:
                raise ValueError("At least 2 paths required for comparison")

            # Get paths
            paths = []
            for path_id in path_ids:
                path = self.alternative_paths.get(path_id)
                if not path:
                    raise ValueError(f"Path {path_id} not found")
                paths.append(path)

            # Ensure all paths are from same user
            user_ids = set(path.user_id for path in paths)
            if len(user_ids) > 1:
                raise ValueError("Cannot compare paths from different users")

            user_id = paths[0].user_id

            # Create comparison
            comparison = PathComparison(
                user_id=user_id,
                session_id=paths[0].session_id,
                comparison_name=comparison_name or f"Comparison of {len(paths)} paths",
                description=f"Comparing {', '.join(path.path_name for path in paths)}",
                paths_compared=path_ids
            )

            # Use default metrics if none specified
            if focus_metrics is None:
                focus_metrics = [
                    ComparisonMetric.THERAPEUTIC_EFFECTIVENESS,
                    ComparisonMetric.CHARACTER_GROWTH,
                    ComparisonMetric.ENGAGEMENT_LEVEL
                ]

            # Calculate metric comparisons
            for metric in focus_metrics:
                comparison.metric_comparisons[metric] = {}
                for path in paths:
                    score = await self._calculate_path_metric(path, metric)
                    comparison.metric_comparisons[metric][path.path_id] = score

            # Generate insights
            comparison.key_differences = await self._identify_key_differences(paths)
            comparison.therapeutic_insights = await self._generate_therapeutic_insights(paths, comparison.metric_comparisons)
            comparison.character_development_insights = await self._generate_character_insights(paths)

            # Generate recommendations
            comparison.recommended_approach = await self._recommend_best_approach(paths, comparison.metric_comparisons)
            comparison.recommendation_reasoning = await self._generate_recommendation_reasoning(paths, comparison)
            comparison.learning_opportunities = await self._identify_learning_opportunities(paths, comparison)

            # Store comparison
            self.path_comparisons[comparison.comparison_id] = comparison

            # Publish comparison event
            await self._publish_exploration_event_by_user(user_id, "path_comparison_generated", {
                "comparison_id": comparison.comparison_id,
                "paths_compared_count": len(path_ids),
                "focus_metrics": [metric.value for metric in focus_metrics],
                "recommended_approach": comparison.recommended_approach
            })

            self.metrics["comparisons_generated"] += 1

            return comparison

        except Exception as e:
            logger.error(f"Failed to compare paths {path_ids}: {e}")
            raise

    async def _update_path_analytics(self, path: AlternativePath) -> None:
        """Update analytics for a path based on current progress."""
        try:
            # Calculate engagement score based on choices and outcomes
            choice_count = len(path.choices_made)
            outcome_count = len(path.outcomes_achieved)

            if choice_count > 0:
                # Base engagement on choice frequency and variety
                choice_variety = len(set(choice["choice_type"] for choice in path.choices_made))
                path.engagement_score = min(1.0, (choice_count * 0.1) + (choice_variety * 0.2))

            # Calculate therapeutic effectiveness based on outcomes
            therapeutic_outcomes = [outcome for outcome in path.outcomes_achieved
                                  if outcome.get("therapeutic_value", 0) > 0]
            if therapeutic_outcomes:
                avg_therapeutic_value = sum(outcome["therapeutic_value"] for outcome in therapeutic_outcomes) / len(therapeutic_outcomes)
                path.therapeutic_effectiveness = min(1.0, avg_therapeutic_value)

            # Calculate learning value based on outcome diversity
            outcome_types = set(outcome.get("outcome_type", "general") for outcome in path.outcomes_achieved)
            path.learning_value = min(1.0, len(outcome_types) * 0.2)

        except Exception as e:
            logger.error(f"Failed to update path analytics for path {path.path_id}: {e}")

    async def _calculate_final_path_analytics(self, path: AlternativePath) -> None:
        """Calculate final analytics for a completed path."""
        try:
            # Update basic analytics
            await self._update_path_analytics(path)

            # Calculate completion-based metrics
            if path.completion_time_minutes > 0:
                # Adjust engagement based on completion time (optimal around 20-40 minutes)
                time_factor = 1.0
                if path.completion_time_minutes < 10:
                    time_factor = 0.7  # Too rushed
                elif path.completion_time_minutes > 60:
                    time_factor = 0.8  # Too long

                path.engagement_score *= time_factor

            # Enhance therapeutic effectiveness with character development
            if path.character_development:
                char_growth_score = sum(path.character_development.get("attributes_improved", {}).values())
                if char_growth_score > 0:
                    path.therapeutic_effectiveness = min(1.0, path.therapeutic_effectiveness + (char_growth_score * 0.1))

            # Enhance learning value with emotional journey
            if path.emotional_journey:
                emotional_variety = len(set(event.get("emotion_type", "neutral") for event in path.emotional_journey))
                path.learning_value = min(1.0, path.learning_value + (emotional_variety * 0.05))

        except Exception as e:
            logger.error(f"Failed to calculate final path analytics for path {path.path_id}: {e}")

    async def _calculate_path_metric(self, path: AlternativePath, metric: ComparisonMetric) -> float:
        """Calculate a specific metric for a path."""
        try:
            algorithm = self.comparison_algorithms.get(metric, {})
            weight_factors = algorithm.get("weight_factors", {})

            if metric == ComparisonMetric.THERAPEUTIC_EFFECTIVENESS:
                score = 0.0

                # Therapeutic goals achieved
                therapeutic_goals = path.therapeutic_outcomes.get("goals_achieved", 0)
                score += weight_factors.get("therapeutic_goals_achieved", 0.3) * min(1.0, therapeutic_goals / 3)

                # Skills practiced
                skills_practiced = len(path.therapeutic_outcomes.get("skills_practiced", []))
                score += weight_factors.get("skills_practiced", 0.2) * min(1.0, skills_practiced / 5)

                # Emotional regulation events
                emotional_regulation = path.therapeutic_outcomes.get("emotional_regulation_events", 0)
                score += weight_factors.get("emotional_regulation", 0.2) * min(1.0, emotional_regulation / 3)

                # Use stored therapeutic effectiveness as baseline
                score = max(score, path.therapeutic_effectiveness)

                return min(1.0, score)

            elif metric == ComparisonMetric.CHARACTER_GROWTH:
                score = 0.0

                # Attribute improvements
                attr_improvements = sum(path.character_development.get("attributes_improved", {}).values())
                score += weight_factors.get("attribute_improvements", 0.4) * min(1.0, attr_improvements / 2)

                # Milestones achieved
                milestones = len(path.character_development.get("milestones_achieved", []))
                score += weight_factors.get("milestones_achieved", 0.3) * min(1.0, milestones / 2)

                # Abilities unlocked
                abilities = len(path.character_development.get("abilities_unlocked", []))
                score += weight_factors.get("abilities_unlocked", 0.2) * min(1.0, abilities / 3)

                return min(1.0, score)

            elif metric == ComparisonMetric.ENGAGEMENT_LEVEL:
                return path.engagement_score

            elif metric == ComparisonMetric.EMOTIONAL_IMPACT:
                if not path.emotional_journey:
                    return 0.0

                # Calculate emotional variety and intensity
                emotions = [event.get("emotion_type", "neutral") for event in path.emotional_journey]
                emotional_variety = len(set(emotions)) / 10  # Normalize to 0-1

                intensities = [event.get("intensity", 0.5) for event in path.emotional_journey]
                avg_intensity = sum(intensities) / len(intensities) if intensities else 0.0

                return min(1.0, (emotional_variety + avg_intensity) / 2)

            else:
                return 0.5  # Default neutral score

        except Exception as e:
            logger.error(f"Failed to calculate metric {metric} for path {path.path_id}: {e}")
            return 0.0

    async def _identify_key_differences(self, paths: List[AlternativePath]) -> List[str]:
        """Identify key differences between paths."""
        try:
            differences = []

            # Compare path types
            path_types = set(path.path_type for path in paths)
            if len(path_types) > 1:
                differences.append(f"Different exploration focuses: {', '.join(pt.value for pt in path_types)}")

            # Compare choice patterns
            choice_types_by_path = {}
            for path in paths:
                choice_types = [choice["choice_type"] for choice in path.choices_made]
                choice_types_by_path[path.path_id] = set(choice_types)

            # Find unique choice types per path
            all_choice_types = set()
            for choice_types in choice_types_by_path.values():
                all_choice_types.update(choice_types)

            for choice_type in all_choice_types:
                paths_with_type = [path_id for path_id, types in choice_types_by_path.items() if choice_type in types]
                if len(paths_with_type) < len(paths):
                    differences.append(f"Choice type '{choice_type}' used in {len(paths_with_type)} of {len(paths)} paths")

            # Compare completion times
            completion_times = [path.completion_time_minutes for path in paths if path.is_completed]
            if len(completion_times) > 1:
                min_time = min(completion_times)
                max_time = max(completion_times)
                if max_time - min_time > 10:  # Significant difference
                    differences.append(f"Completion times varied significantly: {min_time:.1f} to {max_time:.1f} minutes")

            return differences[:5]  # Limit to top 5 differences

        except Exception as e:
            logger.error(f"Failed to identify key differences: {e}")
            return ["Unable to identify key differences"]

    async def _generate_therapeutic_insights(self, paths: List[AlternativePath],
                                           metric_comparisons: Dict[ComparisonMetric, Dict[str, float]]) -> List[str]:
        """Generate therapeutic insights from path comparison."""
        try:
            insights = []

            # Analyze therapeutic effectiveness differences
            if ComparisonMetric.THERAPEUTIC_EFFECTIVENESS in metric_comparisons:
                effectiveness_scores = metric_comparisons[ComparisonMetric.THERAPEUTIC_EFFECTIVENESS]
                best_path_id = max(effectiveness_scores.keys(), key=lambda k: effectiveness_scores[k])
                best_path = next(path for path in paths if path.path_id == best_path_id)

                insights.append(f"The '{best_path.path_name}' approach was most therapeutically effective")

                # Analyze what made it effective
                if best_path.therapeutic_outcomes.get("skills_practiced"):
                    skills = best_path.therapeutic_outcomes["skills_practiced"]
                    insights.append(f"Practicing {', '.join(skills[:2])} contributed to therapeutic success")

            # Analyze choice patterns
            for path in paths:
                therapeutic_choices = [choice for choice in path.choices_made
                                     if choice.get("therapeutic_relevance", 0) > 0.7]
                if len(therapeutic_choices) > len(path.choices_made) * 0.6:
                    insights.append(f"The '{path.path_name}' path focused heavily on therapeutic choices")

            return insights[:3]  # Limit to top 3 insights

        except Exception as e:
            logger.error(f"Failed to generate therapeutic insights: {e}")
            return ["Unable to generate therapeutic insights"]

    async def _generate_character_insights(self, paths: List[AlternativePath]) -> List[str]:
        """Generate character development insights from path comparison."""
        try:
            insights = []

            # Analyze character development patterns
            for path in paths:
                char_dev = path.character_development
                if char_dev.get("attributes_improved"):
                    top_attribute = max(char_dev["attributes_improved"].items(), key=lambda x: x[1])
                    insights.append(f"The '{path.path_name}' path most improved {top_attribute[0]} (+{top_attribute[1]:.1f})")

                if char_dev.get("milestones_achieved"):
                    milestones = char_dev["milestones_achieved"]
                    insights.append(f"The '{path.path_name}' path achieved {len(milestones)} character milestones")

            return insights[:3]  # Limit to top 3 insights

        except Exception as e:
            logger.error(f"Failed to generate character insights: {e}")
            return ["Unable to generate character development insights"]

    async def _recommend_best_approach(self, paths: List[AlternativePath],
                                     metric_comparisons: Dict[ComparisonMetric, Dict[str, float]]) -> Optional[str]:
        """Recommend the best approach based on metric comparisons."""
        try:
            # Calculate overall scores for each path
            path_scores = {}

            for path in paths:
                score = 0.0
                metric_count = 0

                for metric, path_scores_dict in metric_comparisons.items():
                    if path.path_id in path_scores_dict:
                        score += path_scores_dict[path.path_id]
                        metric_count += 1

                if metric_count > 0:
                    path_scores[path.path_id] = score / metric_count

            if path_scores:
                return max(path_scores.keys(), key=lambda k: path_scores[k])

            return None

        except Exception as e:
            logger.error(f"Failed to recommend best approach: {e}")
            return None

    async def _generate_recommendation_reasoning(self, paths: List[AlternativePath],
                                               comparison: PathComparison) -> str:
        """Generate reasoning for the recommendation."""
        try:
            if not comparison.recommended_approach:
                return "No clear recommendation could be determined"

            recommended_path = next((path for path in paths if path.path_id == comparison.recommended_approach), None)
            if not recommended_path:
                return "Recommended path not found"

            reasoning_parts = []

            # Analyze why this path was recommended
            for metric, scores in comparison.metric_comparisons.items():
                if comparison.recommended_approach in scores:
                    score = scores[comparison.recommended_approach]
                    if score > 0.7:  # High score
                        reasoning_parts.append(f"high {metric.value.replace('_', ' ')} ({score:.1f})")

            if reasoning_parts:
                return f"Recommended due to {', '.join(reasoning_parts[:2])}"
            else:
                return f"Recommended based on overall balanced performance"

        except Exception as e:
            logger.error(f"Failed to generate recommendation reasoning: {e}")
            return "Unable to generate recommendation reasoning"

    async def _identify_learning_opportunities(self, paths: List[AlternativePath],
                                             comparison: PathComparison) -> List[str]:
        """Identify learning opportunities from path comparison."""
        try:
            opportunities = []

            # Identify areas where paths differed significantly
            for metric, scores in comparison.metric_comparisons.items():
                if len(scores) >= 2:
                    score_values = list(scores.values())
                    max_score = max(score_values)
                    min_score = min(score_values)

                    if max_score - min_score > 0.3:  # Significant difference
                        opportunities.append(f"Explore different approaches to improve {metric.value.replace('_', ' ')}")

            # Identify unexplored choice types
            all_choice_types = set()
            used_choice_types = set()

            for path in paths:
                path_choice_types = set(choice["choice_type"] for choice in path.choices_made)
                used_choice_types.update(path_choice_types)

            # Common choice types that might not have been explored
            common_types = {"emotional_regulation", "communication", "problem_solving", "self_reflection"}
            unexplored = common_types - used_choice_types

            for choice_type in list(unexplored)[:2]:  # Limit to 2
                opportunities.append(f"Try more {choice_type.replace('_', ' ')} focused choices")

            return opportunities[:4]  # Limit to top 4 opportunities

        except Exception as e:
            logger.error(f"Failed to identify learning opportunities: {e}")
            return ["Explore different choice patterns and approaches"]

    async def _publish_exploration_event(self, session_state: SessionState, event_type: str, context: Dict[str, Any]) -> None:
        """Publish exploration event."""
        try:
            narrative_event = NarrativeEvent(
                event_type=EventType.EXPLORATION_EVENT,
                session_id=session_state.session_id,
                user_id=session_state.user_id,
                context={
                    "exploration_event_type": event_type,
                    **context
                }
            )

            await self.event_bus.publish(narrative_event)

        except Exception as e:
            logger.error(f"Failed to publish exploration event {event_type}: {e}")

    async def _publish_exploration_event_by_user(self, user_id: str, event_type: str, context: Dict[str, Any]) -> None:
        """Publish exploration event by user ID."""
        try:
            narrative_event = NarrativeEvent(
                event_type=EventType.EXPLORATION_EVENT,
                session_id="exploration_session",
                user_id=user_id,
                context={
                    "exploration_event_type": event_type,
                    **context
                }
            )

            await self.event_bus.publish(narrative_event)

        except Exception as e:
            logger.error(f"Failed to publish exploration event {event_type} for user {user_id}: {e}")

    def get_user_exploration_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive exploration summary for a user."""
        try:
            user_snapshots = self.user_snapshots.get(user_id, [])
            user_paths = self.user_paths.get(user_id, [])
            user_explorations = self.user_explorations.get(user_id, [])

            # Get path details
            paths = [self.alternative_paths[path_id] for path_id in user_paths if path_id in self.alternative_paths]
            completed_paths = [path for path in paths if path.is_completed]

            # Calculate summary statistics
            total_exploration_time = sum(path.completion_time_minutes for path in completed_paths)
            avg_therapeutic_effectiveness = sum(path.therapeutic_effectiveness for path in completed_paths) / len(completed_paths) if completed_paths else 0.0
            avg_engagement = sum(path.engagement_score for path in completed_paths) / len(completed_paths) if completed_paths else 0.0

            # Get comparisons
            user_comparisons = [comp for comp in self.path_comparisons.values() if comp.user_id == user_id]

            return {
                "user_id": user_id,
                "exploration_summary": {
                    "snapshots_created": len(user_snapshots),
                    "paths_explored": len(user_paths),
                    "paths_completed": len(completed_paths),
                    "exploration_sessions": len(user_explorations),
                    "comparisons_generated": len(user_comparisons)
                },
                "exploration_analytics": {
                    "total_exploration_time_minutes": total_exploration_time,
                    "average_therapeutic_effectiveness": avg_therapeutic_effectiveness,
                    "average_engagement_score": avg_engagement,
                    "most_explored_path_type": self._get_most_explored_path_type(paths),
                    "preferred_exploration_mode": self._get_preferred_exploration_mode(user_explorations)
                },
                "recent_paths": [
                    {
                        "path_id": path.path_id,
                        "path_name": path.path_name,
                        "path_type": path.path_type.value,
                        "is_completed": path.is_completed,
                        "therapeutic_effectiveness": path.therapeutic_effectiveness,
                        "created_at": path.created_at.isoformat()
                    }
                    for path in sorted(paths, key=lambda p: p.created_at, reverse=True)[:5]
                ],
                "recent_comparisons": [
                    {
                        "comparison_id": comp.comparison_id,
                        "comparison_name": comp.comparison_name,
                        "paths_compared_count": len(comp.paths_compared),
                        "recommended_approach": comp.recommended_approach,
                        "created_at": comp.created_at.isoformat()
                    }
                    for comp in sorted(user_comparisons, key=lambda c: c.created_at, reverse=True)[:3]
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get exploration summary for user {user_id}: {e}")
            return {"error": "Unable to generate exploration summary"}

    def _get_most_explored_path_type(self, paths: List[AlternativePath]) -> str:
        """Get the most explored path type for a user."""
        if not paths:
            return "none"

        path_type_counts = {}
        for path in paths:
            path_type_counts[path.path_type.value] = path_type_counts.get(path.path_type.value, 0) + 1

        return max(path_type_counts.keys(), key=lambda k: path_type_counts[k])

    def _get_preferred_exploration_mode(self, exploration_ids: List[str]) -> str:
        """Get the preferred exploration mode for a user."""
        if not exploration_ids:
            return "none"

        explorations = [self.exploration_sessions[exp_id] for exp_id in exploration_ids if exp_id in self.exploration_sessions]
        if not explorations:
            return "none"

        mode_counts = {}
        for exploration in explorations:
            mode_counts[exploration.exploration_mode.value] = mode_counts.get(exploration.exploration_mode.value, 0) + 1

        return max(mode_counts.keys(), key=lambda k: mode_counts[k])

    def get_metrics(self) -> Dict[str, Any]:
        """Get replayability system metrics."""
        return {
            **self.metrics,
            "total_snapshots": len(self.exploration_snapshots),
            "total_paths": len(self.alternative_paths),
            "total_comparisons": len(self.path_comparisons),
            "total_exploration_sessions": len(self.exploration_sessions),
            "active_exploration_sessions": len([exp for exp in self.exploration_sessions.values() if exp.is_active]),
            "users_with_explorations": len(self.user_explorations)
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of replayability system."""
        return {
            "status": "healthy",
            "exploration_templates_loaded": len(self.exploration_templates),
            "comparison_algorithms_loaded": len(self.comparison_algorithms),
            "insight_generators_loaded": len(self.insight_generators),
            "snapshots_stored": len(self.exploration_snapshots),
            "paths_stored": len(self.alternative_paths),
            "comparisons_stored": len(self.path_comparisons),
            "exploration_sessions_stored": len(self.exploration_sessions),
            "metrics": self.get_metrics()
        }
