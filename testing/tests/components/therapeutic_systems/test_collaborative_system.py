"""
Tests for TherapeuticCollaborativeSystem

This module tests the production collaborative system implementation
including multi-user therapeutic experiences, peer support, and collaborative goal achievement.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from src.components.therapeutic_systems.collaborative_system import (
    CollaborativeGoal,
    CollaborativeMode,
    CollaborativeParticipant,
    CollaborativeSession,
    ParticipantRole,
    SessionStatus,
    SupportInteraction,
    SupportType,
    TherapeuticCollaborativeSystem,
)


class TestTherapeuticCollaborativeSystem:
    """Test TherapeuticCollaborativeSystem functionality."""

    @pytest.fixture
    def collaborative_system(self):
        """Create collaborative system instance."""
        return TherapeuticCollaborativeSystem()

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        return {
            "consequence_system": AsyncMock(),
            "emotional_safety_system": AsyncMock(),
            "adaptive_difficulty_engine": AsyncMock(),
            "character_development_system": AsyncMock(),
            "therapeutic_integration_system": AsyncMock(),
            "gameplay_loop_controller": AsyncMock(),
            "replayability_system": AsyncMock(),
        }

    @pytest.mark.asyncio
    async def test_initialization(self, collaborative_system):
        """Test system initialization."""
        await collaborative_system.initialize()

        # Should have empty collaborative tracking
        assert len(collaborative_system.collaborative_sessions) == 0
        assert len(collaborative_system.support_interactions) == 0
        assert len(collaborative_system.collaborative_goals) == 0
        assert len(collaborative_system.peer_connections) == 0

        # Should have default configuration
        assert collaborative_system.max_concurrent_sessions == 50
        assert collaborative_system.max_participants_per_session == 8
        assert collaborative_system.session_timeout_minutes == 180
        assert collaborative_system.crisis_response_enabled is True

        # Should have initialized metrics
        assert "sessions_created" in collaborative_system.metrics
        assert "participants_connected" in collaborative_system.metrics
        assert collaborative_system.metrics["sessions_created"] == 0

    def test_therapeutic_system_injection(self, collaborative_system, mock_therapeutic_systems):
        """Test therapeutic system dependency injection."""
        collaborative_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Should have all systems injected
        assert collaborative_system.consequence_system is not None
        assert collaborative_system.emotional_safety_system is not None
        assert collaborative_system.adaptive_difficulty_engine is not None
        assert collaborative_system.character_development_system is not None
        assert collaborative_system.therapeutic_integration_system is not None
        assert collaborative_system.gameplay_loop_controller is not None
        assert collaborative_system.replayability_system is not None

    @pytest.mark.asyncio
    async def test_create_collaborative_session(self, collaborative_system, mock_therapeutic_systems):
        """Test collaborative session creation."""
        await collaborative_system.initialize()
        collaborative_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses
        mock_therapeutic_systems["therapeutic_integration_system"].generate_personalized_recommendations.return_value = [
            Mock(framework=Mock(value="peer_support"))
        ]
        mock_therapeutic_systems["emotional_safety_system"].initialize_user_monitoring.return_value = {"status": "initialized"}

        session = await collaborative_system.create_collaborative_session(
            host_user_id="host_user_001",
            session_name="Peer Support Circle",
            collaborative_mode=CollaborativeMode.PEER_SUPPORT,
            therapeutic_focus=["anxiety_management", "confidence_building"],
            max_participants=6
        )

        # Should return valid session
        assert isinstance(session, CollaborativeSession)
        assert session.host_user_id == "host_user_001"
        assert session.session_name == "Peer Support Circle"
        assert session.collaborative_mode == CollaborativeMode.PEER_SUPPORT
        assert len(session.therapeutic_focus) >= 2
        assert session.max_participants == 6
        assert session.status == SessionStatus.WAITING_FOR_PARTICIPANTS

        # Should have host participant
        assert len(session.participants) == 1
        assert "host_user_001" in session.participants
        host_participant = session.participants["host_user_001"]
        assert host_participant.role == ParticipantRole.HOST

        # Should track session
        assert len(collaborative_system.collaborative_sessions) == 1
        assert session.session_id in collaborative_system.collaborative_sessions
        assert "host_user_001" in collaborative_system.user_sessions

        # Should update metrics
        assert collaborative_system.metrics["sessions_created"] == 1

    @pytest.mark.asyncio
    async def test_join_collaborative_session(self, collaborative_system, mock_therapeutic_systems):
        """Test joining a collaborative session."""
        await collaborative_system.initialize()
        collaborative_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses
        mock_therapeutic_systems["therapeutic_integration_system"].generate_personalized_recommendations.return_value = []
        mock_therapeutic_systems["emotional_safety_system"].initialize_user_monitoring.return_value = {"status": "initialized"}
        mock_therapeutic_systems["character_development_system"].create_character.return_value = Mock(
            character_id="char_001"
        )

        # Create session first
        session = await collaborative_system.create_collaborative_session(
            host_user_id="host_user_001",
            session_name="Group Therapy Session",
            collaborative_mode=CollaborativeMode.GROUP_THERAPY
        )

        # Join session
        participant = await collaborative_system.join_collaborative_session(
            session_id=session.session_id,
            user_id="participant_001",
            role=ParticipantRole.PARTICIPANT,
            therapeutic_goals=["emotional_regulation", "social_skills"]
        )

        # Should return valid participant
        assert isinstance(participant, CollaborativeParticipant)
        assert participant.user_id == "participant_001"
        assert participant.role == ParticipantRole.PARTICIPANT
        assert len(participant.therapeutic_goals) == 2
        assert participant.character_id == "char_001"

        # Should update session
        updated_session = collaborative_system.collaborative_sessions[session.session_id]
        assert len(updated_session.participants) == 2
        assert "participant_001" in updated_session.participants
        assert updated_session.status == SessionStatus.ACTIVE  # Should start with 2+ participants

        # Should track user sessions
        assert "participant_001" in collaborative_system.user_sessions

        # Should update metrics
        assert collaborative_system.metrics["participants_connected"] == 1

    @pytest.mark.asyncio
    async def test_provide_peer_support(self, collaborative_system, mock_therapeutic_systems):
        """Test peer support interaction."""
        await collaborative_system.initialize()
        collaborative_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses
        mock_therapeutic_systems["therapeutic_integration_system"].generate_personalized_recommendations.return_value = []
        mock_therapeutic_systems["emotional_safety_system"].initialize_user_monitoring.return_value = {"status": "initialized"}
        mock_therapeutic_systems["consequence_system"].process_choice_consequence.return_value = {
            "therapeutic_value": 2.5, "character_impact": {"empathy": 0.5}
        }

        # Create session with participants
        session = await collaborative_system.create_collaborative_session(
            host_user_id="host_user_001",
            session_name="Support Circle"
        )

        await collaborative_system.join_collaborative_session(
            session_id=session.session_id,
            user_id="participant_001"
        )

        # Provide peer support
        support_interaction = await collaborative_system.provide_peer_support(
            session_id=session.session_id,
            supporter_id="host_user_001",
            recipient_id="participant_001",
            support_type=SupportType.ENCOURAGEMENT,
            message="You're doing great! Keep going with your therapeutic journey.",
            therapeutic_context={"scenario": "confidence_building"}
        )

        # Should return valid interaction
        assert isinstance(support_interaction, SupportInteraction)
        assert support_interaction.session_id == session.session_id
        assert support_interaction.supporter_id == "host_user_001"
        assert support_interaction.recipient_id == "participant_001"
        assert support_interaction.support_type == SupportType.ENCOURAGEMENT
        assert support_interaction.therapeutic_value == 2.5

        # Should update participant tracking
        updated_session = collaborative_system.collaborative_sessions[session.session_id]
        supporter = updated_session.participants["host_user_001"]
        recipient = updated_session.participants["participant_001"]

        assert supporter.support_given == 1
        assert supporter.contributions_count == 1
        assert recipient.support_received == 1

        # Should track interaction
        assert len(collaborative_system.support_interactions) == 1
        assert support_interaction.interaction_id in collaborative_system.support_interactions
        assert support_interaction.interaction_id in updated_session.support_interactions

        # Should strengthen peer connection
        assert "host_user_001" in collaborative_system.peer_connections
        assert "participant_001" in collaborative_system.peer_connections["host_user_001"]

        # Should update metrics
        assert collaborative_system.metrics["support_interactions"] == 1
        assert collaborative_system.metrics["peer_connections_formed"] == 1

    @pytest.mark.asyncio
    async def test_create_collaborative_goal(self, collaborative_system, mock_therapeutic_systems):
        """Test collaborative goal creation."""
        await collaborative_system.initialize()
        collaborative_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses
        mock_therapeutic_systems["therapeutic_integration_system"].generate_personalized_recommendations.return_value = [
            Mock(framework=Mock(value="cbt"), integration_strategy=Mock(value="skill_practice"))
        ]
        mock_therapeutic_systems["emotional_safety_system"].initialize_user_monitoring.return_value = {"status": "initialized"}

        # Create session with participants
        session = await collaborative_system.create_collaborative_session(
            host_user_id="host_user_001",
            session_name="Goal Achievement Group"
        )

        await collaborative_system.join_collaborative_session(
            session_id=session.session_id,
            user_id="participant_001"
        )

        await collaborative_system.join_collaborative_session(
            session_id=session.session_id,
            user_id="participant_002"
        )

        # Create collaborative goal
        goal = await collaborative_system.create_collaborative_goal(
            session_id=session.session_id,
            goal_name="Build Social Confidence",
            goal_description="Work together to build confidence in social situations",
            primary_participants=["host_user_001", "participant_001"],
            therapeutic_framework="cbt",
            target_completion=datetime.utcnow() + timedelta(days=30)
        )

        # Should return valid goal
        assert isinstance(goal, CollaborativeGoal)
        assert goal.session_id == session.session_id
        assert goal.goal_name == "Build Social Confidence"
        assert goal.therapeutic_framework == "cbt"
        assert len(goal.primary_participants) == 2
        assert len(goal.supporting_participants) == 1  # participant_002
        assert len(goal.target_milestones) > 0

        # Should track goal
        assert len(collaborative_system.collaborative_goals) == 1
        assert goal.goal_id in collaborative_system.collaborative_goals

        # Should update session
        updated_session = collaborative_system.collaborative_sessions[session.session_id]
        assert goal.goal_id in updated_session.shared_goals

    @pytest.mark.asyncio
    async def test_collaborative_modes(self, collaborative_system):
        """Test different collaborative modes."""
        await collaborative_system.initialize()

        # Test all collaborative modes
        modes = [
            CollaborativeMode.PEER_SUPPORT,
            CollaborativeMode.GROUP_THERAPY,
            CollaborativeMode.MENTORSHIP,
            CollaborativeMode.SHARED_EXPLORATION,
            CollaborativeMode.THERAPEUTIC_PARTNERSHIP,
            CollaborativeMode.CRISIS_SUPPORT,
        ]

        for mode in modes:
            session = await collaborative_system.create_collaborative_session(
                host_user_id=f"host_{mode.value}",
                session_name=f"Test {mode.value.title()} Session",
                collaborative_mode=mode
            )

            assert session.collaborative_mode == mode

            # Check mode-specific configurations
            if mode == CollaborativeMode.GROUP_THERAPY:
                assert session.requires_facilitator is True
                assert session.safety_level == "high"
            elif mode == CollaborativeMode.MENTORSHIP:
                assert session.max_participants == 2
            elif mode == CollaborativeMode.CRISIS_SUPPORT:
                assert session.safety_level == "maximum"
                assert session.requires_facilitator is True

    @pytest.mark.asyncio
    async def test_crisis_support_handling(self, collaborative_system, mock_therapeutic_systems):
        """Test crisis support handling."""
        await collaborative_system.initialize()
        collaborative_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock crisis detection
        mock_therapeutic_systems["emotional_safety_system"].assess_crisis_risk.return_value = {
            "crisis_detected": True, "crisis_level": "HIGH"
        }
        mock_therapeutic_systems["emotional_safety_system"].initialize_user_monitoring.return_value = {"status": "initialized"}
        mock_therapeutic_systems["therapeutic_integration_system"].generate_personalized_recommendations.return_value = []
        mock_therapeutic_systems["consequence_system"].process_choice_consequence.return_value = {
            "therapeutic_value": 2.0, "character_impact": {"empathy": 0.5}
        }

        # Create session with participants
        session = await collaborative_system.create_collaborative_session(
            host_user_id="host_user_001",
            session_name="Crisis Support Session",
            collaborative_mode=CollaborativeMode.CRISIS_SUPPORT
        )

        await collaborative_system.join_collaborative_session(
            session_id=session.session_id,
            user_id="participant_001"
        )

        # Provide crisis support
        support_interaction = await collaborative_system.provide_peer_support(
            session_id=session.session_id,
            supporter_id="host_user_001",
            recipient_id="participant_001",
            support_type=SupportType.CRISIS_SUPPORT,
            message="I'm here for you. You're not alone in this."
        )

        # Should handle crisis appropriately
        assert support_interaction.is_crisis_related is True

        # Should update session status for emergency intervention
        updated_session = collaborative_system.collaborative_sessions[session.session_id]
        assert updated_session.status == SessionStatus.EMERGENCY_INTERVENTION
        assert updated_session.crisis_interventions == 1

        # Should update metrics
        assert collaborative_system.metrics["crisis_interventions"] == 1

    @pytest.mark.asyncio
    async def test_session_participant_limits(self, collaborative_system):
        """Test session participant limits."""
        await collaborative_system.initialize()

        # Create session with low participant limit
        session = await collaborative_system.create_collaborative_session(
            host_user_id="host_user_001",
            session_name="Small Group Session",
            max_participants=2
        )

        # Should have host participant
        assert len(session.participants) == 1

        # Join one more participant (should succeed)
        participant1 = await collaborative_system.join_collaborative_session(
            session_id=session.session_id,
            user_id="participant_001"
        )
        assert participant1.user_id == "participant_001"

        # Try to join another participant (should fail and add to waiting list)
        participant2 = await collaborative_system.join_collaborative_session(
            session_id=session.session_id,
            user_id="participant_002"
        )

        # Should return error participant
        assert "Error" in participant2.username

        # Should add to waiting list
        updated_session = collaborative_system.collaborative_sessions[session.session_id]
        assert "participant_002" in updated_session.waiting_list

    @pytest.mark.asyncio
    async def test_get_session_status(self, collaborative_system):
        """Test session status retrieval."""
        await collaborative_system.initialize()

        # Create session
        session = await collaborative_system.create_collaborative_session(
            host_user_id="host_user_001",
            session_name="Status Test Session",
            therapeutic_focus=["confidence_building"]
        )

        # Get session status
        status = await collaborative_system.get_session_status(session.session_id)

        # Should return comprehensive status
        assert status is not None
        assert status["session_id"] == session.session_id
        assert status["host_user_id"] == "host_user_001"
        assert status["session_name"] == "Status Test Session"
        assert status["collaborative_mode"] == "peer_support"
        assert status["status"] == "waiting_for_participants"
        assert status["participants"] == 1
        assert "confidence_building" in status["therapeutic_focus"]

    @pytest.mark.asyncio
    async def test_health_check(self, collaborative_system, mock_therapeutic_systems):
        """Test system health check."""
        await collaborative_system.initialize()
        collaborative_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        health = await collaborative_system.health_check()

        assert "status" in health
        assert health["status"] == "healthy"  # All 7 systems available
        assert "collaborative_modes" in health
        assert health["collaborative_modes"] == 6
        assert "participant_roles" in health
        assert health["participant_roles"] == 6
        assert "support_types" in health
        assert health["support_types"] == 8
        assert "therapeutic_systems" in health
        assert health["systems_available"] == "7/7"

    @pytest.mark.asyncio
    async def test_health_check_degraded(self, collaborative_system):
        """Test health check with missing systems."""
        await collaborative_system.initialize()
        # Don't inject all systems

        health = await collaborative_system.health_check()

        assert health["status"] == "degraded"  # Less than 4 systems available
        assert health["systems_available"] == "0/7"

    def test_get_metrics(self, collaborative_system):
        """Test metrics collection."""
        # Add some test data
        collaborative_system.metrics["sessions_created"] = 3
        collaborative_system.metrics["participants_connected"] = 8
        collaborative_system.collaborative_sessions["test1"] = Mock(participants={"u1": Mock(), "u2": Mock()}, status=SessionStatus.ACTIVE)
        collaborative_system.collaborative_sessions["test2"] = Mock(participants={"u3": Mock()}, status=SessionStatus.COMPLETED)
        collaborative_system.support_interactions["int1"] = Mock()
        collaborative_system.peer_connections["u1"] = {"u2"}
        collaborative_system.peer_connections["u2"] = {"u1"}

        metrics = collaborative_system.get_metrics()

        assert isinstance(metrics, dict)
        assert "sessions_created" in metrics
        assert "participants_connected" in metrics
        assert "active_sessions" in metrics
        assert "total_sessions" in metrics
        assert "average_session_size" in metrics
        assert metrics["sessions_created"] == 3
        assert metrics["active_sessions"] == 1
        assert metrics["total_sessions"] == 2
        assert metrics["average_session_size"] == 1.5  # (2+1)/2

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, collaborative_system, mock_therapeutic_systems):
        """Test compatibility with E2E test interface expectations."""
        await collaborative_system.initialize()
        collaborative_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses for E2E compatibility
        mock_therapeutic_systems["therapeutic_integration_system"].generate_personalized_recommendations.return_value = []
        mock_therapeutic_systems["emotional_safety_system"].initialize_user_monitoring.return_value = {"status": "initialized"}

        # Test session creation (E2E interface)
        session = await collaborative_system.create_collaborative_session(
            host_user_id="demo_user_001",
            session_name="Demo Collaborative Session",
            therapeutic_focus=["confidence_building"]
        )

        # Should match expected structure
        assert hasattr(session, "session_id")
        assert hasattr(session, "host_user_id")
        assert hasattr(session, "collaborative_mode")
        assert hasattr(session, "status")
        assert hasattr(session, "participants")

        # Test participant joining (E2E interface)
        participant = await collaborative_system.join_collaborative_session(
            session_id=session.session_id,
            user_id="demo_user_002"
        )

        # Should match expected structure
        assert hasattr(participant, "user_id")
        assert hasattr(participant, "role")
        assert hasattr(participant, "therapeutic_goals")
        assert hasattr(participant, "joined_at")
