"""
Session State Management

This module defines session state structures, transitions, and validation
for the therapeutic gameplay loop system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SessionStateType(str, Enum):
    """Types of session states."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    TRANSITIONING = "transitioning"
    COMPLETED = "completed"
    ERROR = "error"
    EXPIRED = "expired"


class TransitionType(str, Enum):
    """Types of state transitions."""

    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    COMPLETE = "complete"
    ERROR = "error"
    EXPIRE = "expire"
    RESET = "reset"


@dataclass
class StateTransition:
    """Represents a state transition with validation rules."""

    from_state: SessionStateType
    to_state: SessionStateType
    transition_type: TransitionType
    conditions: list[str] = field(default_factory=list)
    side_effects: list[str] = field(default_factory=list)

    def is_valid(self, current_context: dict[str, Any]) -> bool:
        """Check if transition is valid given current context."""
        # Basic state transition validation
        valid_transitions = {
            SessionStateType.INITIALIZING: [
                SessionStateType.ACTIVE,
                SessionStateType.ERROR,
            ],
            SessionStateType.ACTIVE: [
                SessionStateType.PAUSED,
                SessionStateType.TRANSITIONING,
                SessionStateType.COMPLETED,
                SessionStateType.ERROR,
            ],
            SessionStateType.PAUSED: [
                SessionStateType.ACTIVE,
                SessionStateType.COMPLETED,
                SessionStateType.EXPIRED,
                SessionStateType.ERROR,
            ],
            SessionStateType.TRANSITIONING: [
                SessionStateType.ACTIVE,
                SessionStateType.ERROR,
            ],
            SessionStateType.COMPLETED: [],  # Terminal state
            SessionStateType.ERROR: [
                SessionStateType.INITIALIZING,
                SessionStateType.ACTIVE,
            ],
            SessionStateType.EXPIRED: [SessionStateType.INITIALIZING],  # Can restart
        }

        if self.to_state not in valid_transitions.get(self.from_state, []):
            return False

        # Check custom conditions
        for condition in self.conditions:
            if not self._evaluate_condition(condition, current_context):
                return False

        return True

    def _evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate a transition condition."""
        # Simple condition evaluation - can be extended
        if condition == "has_active_scene":
            return context.get("current_scene_id") is not None
        elif condition == "no_safety_concerns":
            return context.get("safety_level", "standard") != "crisis"
        elif condition == "session_not_expired":
            last_activity = context.get("last_activity")
            if last_activity:
                return datetime.utcnow() - last_activity < timedelta(hours=24)
            return True

        return True  # Default to true for unknown conditions


class SessionState(BaseModel):
    """Comprehensive session state representation."""

    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    state_type: SessionStateType = Field(default=SessionStateType.INITIALIZING)

    # Core session data
    current_scene_id: str | None = Field(None, description="Current active scene")
    scene_history: list[str] = Field(
        default_factory=list, description="Scene ID history"
    )
    choice_history: list[str] = Field(
        default_factory=list, description="Choice ID history"
    )

    # Therapeutic context
    therapeutic_goals: list[str] = Field(default_factory=list)
    safety_level: str = Field(default="standard")
    therapeutic_context: dict[str, Any] = Field(default_factory=dict)

    # User preferences and settings
    user_preferences: dict[str, Any] = Field(default_factory=dict)
    accessibility_settings: dict[str, Any] = Field(default_factory=dict)

    # Progress and metrics
    session_metrics: dict[str, Any] = Field(default_factory=dict)
    progress_snapshots: list[dict[str, Any]] = Field(default_factory=list)

    # Narrative context
    narrative_variables: dict[str, Any] = Field(default_factory=dict)
    character_relationships: dict[str, float] = Field(default_factory=dict)
    world_state: dict[str, Any] = Field(default_factory=dict)

    # Interaction context
    recent_interactions: list[str] = Field(default_factory=list)  # Interaction IDs
    emotional_state: dict[str, float] = Field(default_factory=dict)
    engagement_metrics: dict[str, float] = Field(default_factory=dict)

    # Timing and lifecycle
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = Field(None, description="Session expiration time")
    completed_at: datetime | None = Field(None, description="Session completion time")

    # State management
    state_history: list[dict[str, Any]] = Field(default_factory=list)
    transition_locks: list[str] = Field(default_factory=list)

    # Cache metadata
    cache_version: int = Field(default=1, description="Cache version for invalidation")
    last_persisted: datetime | None = Field(
        None, description="Last persistence timestamp"
    )
    dirty_fields: list[str] = Field(
        default_factory=list, description="Fields needing persistence"
    )

    @field_validator("emotional_state")
    @classmethod
    def validate_emotional_state(cls, v):
        for emotion, intensity in v.items():
            if not 0.0 <= intensity <= 1.0:
                raise ValueError(
                    f"Emotional intensity for {emotion} must be between 0.0 and 1.0"
                )
        return v

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
        if "last_activity" not in self.dirty_fields:
            self.dirty_fields.append("last_activity")

    def add_scene(self, scene_id: str) -> None:
        """Add a scene to the session history."""
        if scene_id not in self.scene_history:
            self.scene_history.append(scene_id)
        self.current_scene_id = scene_id
        self.update_activity()
        for field_name in ["scene_history", "current_scene_id"]:
            if field_name not in self.dirty_fields:
                self.dirty_fields.append(field_name)

    def add_choice(self, choice_id: str) -> None:
        """Add a choice to the session history."""
        if choice_id not in self.choice_history:
            self.choice_history.append(choice_id)
        self.update_activity()
        if "choice_history" not in self.dirty_fields:
            self.dirty_fields.append("choice_history")

    def update_emotional_state(self, emotion: str, intensity: float) -> None:
        """Update emotional state for a specific emotion."""
        if not 0.0 <= intensity <= 1.0:
            raise ValueError("Emotional intensity must be between 0.0 and 1.0")

        self.emotional_state[emotion] = intensity
        self.update_activity()
        if "emotional_state" not in self.dirty_fields:
            self.dirty_fields.append("emotional_state")

    def set_narrative_variable(self, key: str, value: Any) -> None:
        """Set a narrative variable."""
        self.narrative_variables[key] = value
        self.update_activity()
        if "narrative_variables" not in self.dirty_fields:
            self.dirty_fields.append("narrative_variables")

    def get_narrative_variable(self, key: str, default: Any = None) -> Any:
        """Get a narrative variable."""
        return self.narrative_variables.get(key, default)

    def add_progress_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Add a progress snapshot."""
        snapshot["timestamp"] = datetime.utcnow().isoformat()
        self.progress_snapshots.append(snapshot)
        self.update_activity()
        if "progress_snapshots" not in self.dirty_fields:
            self.dirty_fields.append("progress_snapshots")

    def is_expired(self) -> bool:
        """Check if session is expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def is_active(self) -> bool:
        """Check if session is in an active state."""
        return self.state_type in [
            SessionStateType.ACTIVE,
            SessionStateType.TRANSITIONING,
        ]

    def get_session_duration(self) -> timedelta:
        """Get total session duration."""
        end_time = self.completed_at or datetime.utcnow()
        return end_time - self.created_at

    def get_idle_time(self) -> timedelta:
        """Get time since last activity."""
        return datetime.utcnow() - self.last_activity

    def record_state_change(
        self, from_state: SessionStateType, to_state: SessionStateType, reason: str = ""
    ) -> None:
        """Record a state change in history."""
        state_change = {
            "from_state": from_state.value,
            "to_state": to_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
        }
        self.state_history.append(state_change)
        if "state_history" not in self.dirty_fields:
            self.dirty_fields.append("state_history")

    def clear_dirty_fields(self) -> None:
        """Clear dirty fields after successful persistence."""
        self.dirty_fields.clear()
        self.last_persisted = datetime.utcnow()

    def has_dirty_fields(self) -> bool:
        """Check if there are unsaved changes."""
        return len(self.dirty_fields) > 0


class StateValidator:
    """Validates session state transitions and consistency."""

    def __init__(self):
        self.transition_rules = self._define_transition_rules()

    def _define_transition_rules(self) -> list[StateTransition]:
        """Define all valid state transitions."""
        return [
            # Initialization transitions
            StateTransition(
                SessionStateType.INITIALIZING,
                SessionStateType.ACTIVE,
                TransitionType.START,
                conditions=["no_safety_concerns"],
                side_effects=["set_start_time", "initialize_metrics"],
            ),
            # Active state transitions
            StateTransition(
                SessionStateType.ACTIVE,
                SessionStateType.PAUSED,
                TransitionType.PAUSE,
                conditions=["has_active_scene"],
                side_effects=["save_current_state", "set_pause_time"],
            ),
            StateTransition(
                SessionStateType.ACTIVE,
                SessionStateType.TRANSITIONING,
                TransitionType.START,
                conditions=["scene_transition_requested"],
                side_effects=["prepare_scene_transition"],
            ),
            StateTransition(
                SessionStateType.ACTIVE,
                SessionStateType.COMPLETED,
                TransitionType.COMPLETE,
                conditions=["completion_criteria_met"],
                side_effects=["finalize_session", "save_final_state"],
            ),
            # Paused state transitions
            StateTransition(
                SessionStateType.PAUSED,
                SessionStateType.ACTIVE,
                TransitionType.RESUME,
                conditions=["session_not_expired", "no_safety_concerns"],
                side_effects=["restore_session_state", "update_activity"],
            ),
            # Transitioning state transitions
            StateTransition(
                SessionStateType.TRANSITIONING,
                SessionStateType.ACTIVE,
                TransitionType.COMPLETE,
                conditions=["transition_completed"],
                side_effects=["activate_new_scene", "update_narrative_state"],
            ),
            # Error recovery transitions
            StateTransition(
                SessionStateType.ERROR,
                SessionStateType.ACTIVE,
                TransitionType.RESET,
                conditions=["error_resolved", "no_safety_concerns"],
                side_effects=["clear_error_state", "restore_last_good_state"],
            ),
            # Expiration transitions
            StateTransition(
                SessionStateType.PAUSED,
                SessionStateType.EXPIRED,
                TransitionType.EXPIRE,
                conditions=["session_expired"],
                side_effects=["cleanup_session_data", "notify_expiration"],
            ),
        ]

    def validate_transition(
        self,
        current_state: SessionState,
        new_state_type: SessionStateType,
        transition_type: TransitionType,
    ) -> tuple[bool, str]:
        """Validate a state transition."""
        # Find applicable transition rule
        applicable_rule = None
        for rule in self.transition_rules:
            if (
                rule.from_state == current_state.state_type
                and rule.to_state == new_state_type
                and rule.transition_type == transition_type
            ):
                applicable_rule = rule
                break

        if not applicable_rule:
            return (
                False,
                f"No transition rule found for {current_state.state_type} -> {new_state_type}",
            )

        # Check if transition is valid
        context = {
            "current_scene_id": current_state.current_scene_id,
            "safety_level": current_state.safety_level,
            "last_activity": current_state.last_activity,
            "session_duration": current_state.get_session_duration(),
            "idle_time": current_state.get_idle_time(),
        }

        if not applicable_rule.is_valid(context):
            return (
                False,
                f"Transition conditions not met for {current_state.state_type} -> {new_state_type}",
            )

        return True, "Transition valid"

    def validate_state_consistency(self, state: SessionState) -> tuple[bool, list[str]]:
        """Validate internal state consistency."""
        issues = []

        # Check basic consistency
        if state.completed_at and state.state_type != SessionStateType.COMPLETED:
            issues.append("Session has completion time but is not in completed state")

        if state.state_type == SessionStateType.COMPLETED and not state.completed_at:
            issues.append("Session is completed but has no completion time")

        if state.is_expired() and state.state_type not in [
            SessionStateType.EXPIRED,
            SessionStateType.COMPLETED,
        ]:
            issues.append("Session is expired but not in expired or completed state")

        # Check scene consistency
        if state.current_scene_id and state.current_scene_id not in state.scene_history:
            issues.append("Current scene is not in scene history")

        # Check safety level consistency
        if (
            state.safety_level == "crisis"
            and state.state_type == SessionStateType.ACTIVE
        ):
            issues.append("Session is active but has crisis safety level")

        # Check emotional state values
        for emotion, intensity in state.emotional_state.items():
            if not 0.0 <= intensity <= 1.0:
                issues.append(f"Invalid emotional intensity for {emotion}: {intensity}")

        return len(issues) == 0, issues


class SessionStateManager:
    """Manages session state transitions and validation."""

    def __init__(self):
        self.validator = StateValidator()

    def transition_state(
        self,
        session_state: SessionState,
        new_state_type: SessionStateType,
        transition_type: TransitionType,
        reason: str = "",
    ) -> tuple[bool, str]:
        """Transition session to new state."""
        # Validate transition
        is_valid, message = self.validator.validate_transition(
            session_state, new_state_type, transition_type
        )

        if not is_valid:
            return False, message

        # Record state change
        old_state = session_state.state_type
        session_state.record_state_change(old_state, new_state_type, reason)

        # Update state
        session_state.state_type = new_state_type
        session_state.update_activity()

        # Handle special state transitions
        if new_state_type == SessionStateType.COMPLETED:
            session_state.completed_at = datetime.utcnow()
        elif new_state_type == SessionStateType.EXPIRED:
            session_state.expires_at = datetime.utcnow()

        return (
            True,
            f"Successfully transitioned from {old_state.value} to {new_state_type.value}",
        )

    def validate_session(self, session_state: SessionState) -> tuple[bool, list[str]]:
        """Validate session state consistency."""
        return self.validator.validate_state_consistency(session_state)

    def auto_expire_check(
        self, session_state: SessionState, max_idle_time: timedelta = timedelta(hours=2)
    ) -> bool:
        """Check if session should be auto-expired."""
        if session_state.state_type in [
            SessionStateType.COMPLETED,
            SessionStateType.EXPIRED,
        ]:
            return False

        if session_state.get_idle_time() > max_idle_time:
            success, _ = self.transition_state(
                session_state,
                SessionStateType.EXPIRED,
                TransitionType.EXPIRE,
                f"Auto-expired after {max_idle_time} idle time",
            )
            return success

        return False
