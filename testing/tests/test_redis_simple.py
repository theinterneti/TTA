"""
Simple Redis Integration Tests

Basic tests to verify Redis session management functionality.
"""

from datetime import datetime, timedelta

import pytest

from src.components.gameplay_loop.services.cache_strategies import (
    CacheMetrics,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
    SessionStateManager,
    SessionStateType,
    StateValidator,
)


@pytest.mark.redis
def test_session_state_creation():
    """Test creating a session state."""
    session_state = SessionState(
        session_id="test_session_123",
        user_id="test_user_456",
        state_type=SessionStateType.ACTIVE,
        therapeutic_goals=["anxiety_management"],
        safety_level="standard",
    )

    assert session_state.session_id == "test_session_123"
    assert session_state.user_id == "test_user_456"
    assert session_state.state_type == SessionStateType.ACTIVE
    assert len(session_state.therapeutic_goals) == 1


@pytest.mark.redis
def test_session_state_activity_tracking():
    """Test session activity tracking."""
    session_state = SessionState(session_id="test_session", user_id="test_user")

    original_activity = session_state.last_activity

    # Update activity
    session_state.update_activity()

    assert session_state.last_activity > original_activity
    assert "last_activity" in session_state.dirty_fields


@pytest.mark.redis
def test_session_state_scene_management():
    """Test scene management in session state."""
    session_state = SessionState(session_id="test_session", user_id="test_user")

    # Add scenes
    session_state.add_scene("scene_001")
    session_state.add_scene("scene_002")

    assert session_state.current_scene_id == "scene_002"
    assert len(session_state.scene_history) == 2
    assert "scene_001" in session_state.scene_history
    assert "scene_002" in session_state.scene_history


@pytest.mark.redis
def test_emotional_state_validation():
    """Test emotional state validation."""
    session_state = SessionState(session_id="test_session", user_id="test_user")

    # Valid emotional state
    session_state.update_emotional_state("calm", 0.7)
    assert session_state.emotional_state["calm"] == 0.7

    # Invalid emotional state should raise error
    with pytest.raises(ValueError):
        session_state.update_emotional_state("invalid", 1.5)


@pytest.mark.redis
def test_narrative_variables():
    """Test narrative variable management."""
    session_state = SessionState(session_id="test_session", user_id="test_user")

    # Set narrative variables
    session_state.set_narrative_variable("quest_started", True)
    session_state.set_narrative_variable("ally_trust", 0.8)

    assert session_state.get_narrative_variable("quest_started") is True
    assert session_state.get_narrative_variable("ally_trust") == 0.8
    assert session_state.get_narrative_variable("nonexistent", "default") == "default"


@pytest.mark.redis
def test_session_duration_calculation():
    """Test session duration calculation."""
    session_state = SessionState(session_id="test_session", user_id="test_user")

    duration = session_state.get_session_duration()
    assert isinstance(duration, timedelta)
    assert duration.total_seconds() >= 0


@pytest.mark.redis
def test_dirty_fields_tracking():
    """Test dirty fields tracking."""
    session_state = SessionState(session_id="test_session", user_id="test_user")

    # Initially no dirty fields
    assert not session_state.has_dirty_fields()

    # Make changes
    session_state.add_scene("scene_001")
    session_state.update_emotional_state("happy", 0.8)

    # Should have dirty fields
    assert session_state.has_dirty_fields()
    assert len(session_state.dirty_fields) > 0

    # Clear dirty fields
    session_state.clear_dirty_fields()
    assert not session_state.has_dirty_fields()


@pytest.mark.redis
def test_cache_metrics():
    """Test cache metrics functionality."""
    metrics = CacheMetrics()

    # Test initial state
    assert metrics.hits == 0
    assert metrics.misses == 0
    assert metrics.hit_rate() == 0.0
    assert metrics.miss_rate() == 1.0

    # Simulate some activity
    metrics.hits = 7
    metrics.misses = 3
    metrics.total_requests = 10

    assert abs(metrics.hit_rate() - 0.7) < 0.001
    assert abs(metrics.miss_rate() - 0.3) < 0.001


@pytest.mark.redis
def test_session_state_manager():
    """Test session state manager functionality."""
    manager = SessionStateManager()

    session_state = SessionState(
        session_id="test_session",
        user_id="test_user",
        state_type=SessionStateType.INITIALIZING,
    )

    # Test state validation
    is_valid, issues = manager.validate_session(session_state)
    assert is_valid
    assert len(issues) == 0


@pytest.mark.redis
def test_state_validator():
    """Test state validator functionality."""
    validator = StateValidator()

    session_state = SessionState(
        session_id="test_session",
        user_id="test_user",
        state_type=SessionStateType.ACTIVE,
        current_scene_id="scene_001",
        scene_history=["scene_001"],
    )

    # Test consistency validation
    is_valid, issues = validator.validate_state_consistency(session_state)
    assert is_valid
    assert len(issues) == 0


@pytest.mark.redis
def test_session_expiration():
    """Test session expiration functionality."""
    # Non-expired session
    session_state = SessionState(
        session_id="test_session",
        user_id="test_user",
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    assert not session_state.is_expired()

    # Expired session
    expired_session = SessionState(
        session_id="expired_session",
        user_id="test_user",
        expires_at=datetime.utcnow() - timedelta(hours=1),
    )
    assert expired_session.is_expired()


@pytest.mark.redis
def test_session_active_state():
    """Test session active state checking."""
    # Active session
    active_session = SessionState(
        session_id="active_session",
        user_id="test_user",
        state_type=SessionStateType.ACTIVE,
    )
    assert active_session.is_active()

    # Inactive session
    inactive_session = SessionState(
        session_id="inactive_session",
        user_id="test_user",
        state_type=SessionStateType.COMPLETED,
    )
    assert not inactive_session.is_active()


@pytest.mark.redis
def test_state_change_recording():
    """Test state change recording."""
    session_state = SessionState(
        session_id="test_session",
        user_id="test_user",
        state_type=SessionStateType.INITIALIZING,
    )

    # Record state change
    session_state.record_state_change(
        SessionStateType.INITIALIZING, SessionStateType.ACTIVE, "Session started"
    )

    assert len(session_state.state_history) == 1
    state_change = session_state.state_history[0]
    assert state_change["from_state"] == "initializing"
    assert state_change["to_state"] == "active"
    assert state_change["reason"] == "Session started"
    assert "timestamp" in state_change
