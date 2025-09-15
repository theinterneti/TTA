"""
Tests for CollaborativeSystem

This module tests collaborative adventure framework, group experience management,
privacy and sharing controls, moderation tools and conflict resolution processes,
and comprehensive integration with therapeutic, session management, and replayability systems.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from src.components.gameplay_loop.controllers.gameplay_loop_controller import (
    GameplayLoopController,
)
from src.components.gameplay_loop.models.core import ChoiceType
from src.components.gameplay_loop.narrative.events import EventBus
from src.components.gameplay_loop.narrative.replayability_system import (
    ReplayabilitySystem,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
    SessionStateType,
)
from src.components.gameplay_loop.social.collaborative_system import (
    CollaborativeMode,
    CollaborativeParticipant,
    CollaborativeSession,
    CollaborativeSystem,
    ConflictResolution,
    GroupChoice,
    ModerationAction,
    ParticipantRole,
    SupportMessage,
)


class TestCollaborativeSystem:
    """Test CollaborativeSystem functionality."""

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus

    @pytest.fixture
    def gameplay_controller(self):
        """Create mock gameplay controller."""
        controller = Mock(spec=GameplayLoopController)
        controller.process_choice = AsyncMock()
        return controller

    @pytest.fixture
    def replayability_system(self):
        """Create mock replayability system."""
        system = Mock(spec=ReplayabilitySystem)
        return system

    @pytest.fixture
    def collaborative_system(
        self, event_bus, gameplay_controller, replayability_system
    ):
        """Create collaborative system instance."""
        return CollaborativeSystem(event_bus, gameplay_controller, replayability_system)

    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = SessionState(
            session_id="test_session_123",
            user_id="test_user_456",
            state=SessionStateType.ACTIVE,
            therapeutic_goals=["anxiety_management", "communication_skills"],
        )
        return state

    @pytest.mark.asyncio
    async def test_create_collaborative_session(self, collaborative_system, event_bus):
        """Test creating collaborative sessions."""
        session = await collaborative_system.create_collaborative_session(
            "host_user_123",
            "Test Collaborative Session",
            CollaborativeMode.COOPERATIVE,
            ["anxiety_management", "communication_skills"],
            4,
        )

        # Check session structure
        assert isinstance(session, CollaborativeSession)
        assert session.host_user_id == "host_user_123"
        assert session.session_name == "Test Collaborative Session"
        assert session.collaborative_mode == CollaborativeMode.COOPERATIVE
        assert session.therapeutic_focus == [
            "anxiety_management",
            "communication_skills",
        ]
        assert session.max_participants == 4

        # Check host participant
        assert "host_user_123" in session.participants
        host_participant = session.participants["host_user_123"]
        assert host_participant.role == ParticipantRole.HOST
        assert host_participant.therapeutic_goals == [
            "anxiety_management",
            "communication_skills",
        ]

        # Check storage
        assert session.session_id in collaborative_system.collaborative_sessions
        assert "host_user_123" in collaborative_system.user_sessions
        assert session.session_id in collaborative_system.user_sessions["host_user_123"]

        # Check event publication
        event_bus.publish.assert_called()

        # Check metrics
        assert collaborative_system.metrics["collaborative_sessions_created"] == 1

    @pytest.mark.asyncio
    async def test_join_collaborative_session(self, collaborative_system, event_bus):
        """Test joining collaborative sessions."""
        # Create session first
        session = await collaborative_system.create_collaborative_session(
            "host_user_123", "Test Session", CollaborativeMode.COOPERATIVE
        )

        # Start session to make it active
        session.is_active = True

        # Join session
        participant = await collaborative_system.join_collaborative_session(
            session.session_id,
            "participant_user_456",
            ParticipantRole.PARTICIPANT,
            ["communication_skills"],
        )

        # Check participant structure
        assert isinstance(participant, CollaborativeParticipant)
        assert participant.user_id == "participant_user_456"
        assert participant.role == ParticipantRole.PARTICIPANT
        assert participant.therapeutic_goals == ["communication_skills"]

        # Check session update
        assert "participant_user_456" in session.participants
        assert len(session.participants) == 2

        # Check storage
        assert "participant_user_456" in collaborative_system.user_sessions
        assert (
            session.session_id
            in collaborative_system.user_sessions["participant_user_456"]
        )

        # Check event publication
        event_bus.publish.assert_called()

        # Check metrics
        assert collaborative_system.metrics["participants_joined"] == 1

    @pytest.mark.asyncio
    async def test_join_full_session(self, collaborative_system):
        """Test joining a session that is at capacity."""
        # Create session with max 2 participants
        session = await collaborative_system.create_collaborative_session(
            "host_user_123", "Small Session", CollaborativeMode.COOPERATIVE, [], 2
        )
        session.is_active = True

        # Add one more participant to reach capacity
        await collaborative_system.join_collaborative_session(
            session.session_id, "participant_user_456"
        )

        # Try to join when full - should add to waiting list
        with pytest.raises(ValueError, match="Session .* is full"):
            await collaborative_system.join_collaborative_session(
                session.session_id, "waiting_user_789"
            )

        # Check waiting list
        assert "waiting_user_789" in session.waiting_list

    @pytest.mark.asyncio
    async def test_start_collaborative_session(
        self, collaborative_system, session_state, event_bus
    ):
        """Test starting collaborative sessions."""
        # Create session and add participants
        session = await collaborative_system.create_collaborative_session(
            "host_user_123", "Test Session", CollaborativeMode.COOPERATIVE
        )
        await collaborative_system.join_collaborative_session(
            session.session_id, "participant_user_456"
        )

        # Start session
        started_session = await collaborative_system.start_collaborative_session(
            session.session_id, session_state
        )

        # Check session state
        assert started_session.is_active
        assert started_session.started_at is not None
        assert started_session.base_session_state == session_state

        # Check shared context
        assert "collaborative_mode" in started_session.shared_context
        assert "therapeutic_focus" in started_session.shared_context
        assert "participants" in started_session.shared_context
        assert "group_dynamics" in started_session.shared_context

        # Check group therapeutic framework
        assert "group_therapeutic_framework" in started_session.shared_context
        framework = started_session.shared_context["group_therapeutic_framework"]
        assert "collective_goals" in framework
        assert "support_mechanisms" in framework
        assert "safety_protocols" in framework

        # Check event publication
        event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_propose_group_choice(self, collaborative_system, event_bus):
        """Test proposing group choices."""
        # Create and start session
        session = await collaborative_system.create_collaborative_session(
            "host_user_123", "Test Session", CollaborativeMode.COOPERATIVE
        )
        await collaborative_system.join_collaborative_session(
            session.session_id, "participant_user_456"
        )
        session_state = Mock()
        await collaborative_system.start_collaborative_session(
            session.session_id, session_state
        )

        # Propose choice
        group_choice = await collaborative_system.propose_group_choice(
            session.session_id,
            "host_user_123",
            "Let's try a calming approach",
            ChoiceType.EMOTIONAL_REGULATION,
        )

        # Check choice structure
        assert isinstance(group_choice, GroupChoice)
        assert group_choice.session_id == session.session_id
        assert group_choice.choice_text == "Let's try a calming approach"
        assert group_choice.choice_type == ChoiceType.EMOTIONAL_REGULATION
        assert group_choice.proposed_by == "host_user_123"

        # Check therapeutic impact assessment
        assert "therapeutic_relevance" in group_choice.therapeutic_impact
        assert "alignment_with_focus" in group_choice.therapeutic_impact

        # Check safety assessment
        assert "safety_score" in group_choice.safety_assessment
        assert "safety_concerns" in group_choice.safety_assessment

        # Check storage
        assert group_choice.choice_id in collaborative_system.group_choices
        assert len(session.group_choices) == 1

        # Check event publication
        event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_vote_on_group_choice(self, collaborative_system, event_bus):
        """Test voting on group choices."""
        # Create session and propose choice
        session = await collaborative_system.create_collaborative_session(
            "host_user_123", "Test Session", CollaborativeMode.COOPERATIVE
        )
        await collaborative_system.join_collaborative_session(
            session.session_id, "participant_user_456"
        )
        session_state = Mock()
        await collaborative_system.start_collaborative_session(
            session.session_id, session_state
        )

        group_choice = await collaborative_system.propose_group_choice(
            session.session_id, "host_user_123", "Test choice"
        )

        # Vote on choice
        decision_made = await collaborative_system.vote_on_group_choice(
            group_choice.choice_id, "participant_user_456", "support"
        )

        # Check vote recording
        assert "participant_user_456" in group_choice.votes
        assert group_choice.votes["participant_user_456"] == "support"

        # Should not be decided yet (need more votes)
        assert not decision_made
        assert not group_choice.is_approved

        # Vote with host to reach threshold
        decision_made = await collaborative_system.vote_on_group_choice(
            group_choice.choice_id, "host_user_123", "support"
        )

        # Should be decided now
        assert decision_made
        assert group_choice.is_approved
        assert group_choice.decided_at is not None

        # Check event publication
        event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_send_support_message(self, collaborative_system, event_bus):
        """Test sending support messages."""
        # Create and start session
        session = await collaborative_system.create_collaborative_session(
            "host_user_123", "Test Session", CollaborativeMode.PEER_SUPPORT
        )
        await collaborative_system.join_collaborative_session(
            session.session_id, "participant_user_456"
        )
        session_state = Mock()
        await collaborative_system.start_collaborative_session(
            session.session_id, session_state
        )

        # Send support message
        support_message = await collaborative_system.send_support_message(
            session.session_id,
            "host_user_123",
            "participant_user_456",
            "You're doing great! Keep it up!",
            "encouragement",
        )

        # Check message structure
        assert isinstance(support_message, SupportMessage)
        assert support_message.session_id == session.session_id
        assert support_message.sender_id == "host_user_123"
        assert support_message.recipient_id == "participant_user_456"
        assert support_message.message_text == "You're doing great! Keep it up!"
        assert support_message.message_type == "encouragement"

        # Check moderation
        assert (
            support_message.is_approved
        )  # Should be approved for positive message

        # Check storage
        assert support_message.message_id in collaborative_system.support_messages
        assert len(session.support_messages) == 1

        # Check participant metrics update
        sender = session.participants["host_user_123"]
        recipient = session.participants["participant_user_456"]
        assert sender.messages_sent == 1
        assert sender.support_given == 1
        assert recipient.support_received == 1

        # Check event publication
        event_bus.publish.assert_called()

        # Check metrics
        assert collaborative_system.metrics["support_messages_sent"] == 1

    @pytest.mark.asyncio
    async def test_report_conflict(self, collaborative_system, event_bus):
        """Test reporting conflicts."""
        # Create and start session
        session = await collaborative_system.create_collaborative_session(
            "host_user_123", "Test Session", CollaborativeMode.COOPERATIVE
        )
        await collaborative_system.join_collaborative_session(
            session.session_id, "participant_user_456"
        )
        await collaborative_system.join_collaborative_session(
            session.session_id, "participant_user_789"
        )
        session_state = Mock()
        await collaborative_system.start_collaborative_session(
            session.session_id, session_state
        )

        # Report conflict
        conflict_resolution = await collaborative_system.report_conflict(
            session.session_id,
            "host_user_123",
            "disagreement",
            ["participant_user_456", "participant_user_789"],
            "Participants disagree on approach",
        )

        # Check conflict structure
        assert isinstance(conflict_resolution, ConflictResolution)
        assert conflict_resolution.session_id == session.session_id
        assert conflict_resolution.conflict_type == "disagreement"
        assert conflict_resolution.involved_participants == [
            "participant_user_456",
            "participant_user_789",
        ]
        assert conflict_resolution.description == "Participants disagree on approach"

        # Check resolution method assignment
        assert (
            conflict_resolution.resolution_method == "mediation"
        )  # Default for disagreement

        # Check storage
        assert (
            conflict_resolution.resolution_id
            in collaborative_system.conflict_resolutions
        )
        assert len(session.moderation_log) == 1

        # Check event publication
        event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_moderate_participant(self, collaborative_system, event_bus):
        """Test moderating participants."""
        # Create and start session
        session = await collaborative_system.create_collaborative_session(
            "host_user_123", "Test Session", CollaborativeMode.COOPERATIVE
        )
        await collaborative_system.join_collaborative_session(
            session.session_id, "participant_user_456"
        )
        session_state = Mock()
        await collaborative_system.start_collaborative_session(
            session.session_id, session_state
        )

        # Apply moderation action
        result = await collaborative_system.moderate_participant(
            session.session_id,
            "host_user_123",
            "participant_user_456",
            ModerationAction.WARNING,
            "Inappropriate language",
        )

        # Check moderation result
        assert result["success"]
        assert result["action"] == "warning"
        assert result["target_user_id"] == "participant_user_456"
        assert result["moderator_id"] == "host_user_123"
        assert result["reason"] == "Inappropriate language"

        # Check participant update
        target_participant = session.participants["participant_user_456"]
        assert target_participant.warnings_count == 1

        # Check moderation log
        assert len(session.moderation_log) == 1
        log_entry = session.moderation_log[0]
        assert log_entry["type"] == "moderation_action"
        assert log_entry["action"] == "warning"

        # Check event publication
        event_bus.publish.assert_called()

    def test_moderation_rules_loading(self, collaborative_system):
        """Test that moderation rules are properly loaded."""
        rules = collaborative_system.moderation_rules

        # Check that key moderation scenarios are configured
        assert "inappropriate_language" in rules
        assert "therapeutic_boundary_violation" in rules
        assert "harassment" in rules
        assert "safety_concern" in rules

        # Check rule structure
        for _rule_name, rule in rules.items():
            assert "action" in rule
            assert "escalation_threshold" in rule
            assert "escalation_action" in rule

    def test_safety_keywords_loading(self, collaborative_system):
        """Test that safety keywords are properly loaded."""
        keywords = collaborative_system.safety_keywords

        # Check that key safety categories are configured
        assert "crisis_indicators" in keywords
        assert "inappropriate_content" in keywords
        assert "therapeutic_boundaries" in keywords

        # Check that keywords are lists
        for _category, keyword_list in keywords.items():
            assert isinstance(keyword_list, list)
            assert len(keyword_list) > 0

    def test_therapeutic_triggers_loading(self, collaborative_system):
        """Test that therapeutic triggers are properly loaded."""
        triggers = collaborative_system.therapeutic_triggers

        # Check that key trigger types are configured
        assert "emotional_distress" in triggers
        assert "crisis_situation" in triggers
        assert "therapeutic_resistance" in triggers
        assert "boundary_violation" in triggers

        # Check trigger structure
        for _trigger_name, trigger in triggers.items():
            assert "indicators" in trigger
            assert "intervention" in trigger
            assert "escalation_needed" in trigger

    def test_get_user_collaborative_summary(self, collaborative_system):
        """Test user collaborative summary generation."""
        user_id = "test_user_123"

        # Add some collaborative data
        collaborative_system.user_sessions[user_id] = ["session_1", "session_2"]

        # Add mock sessions
        session1 = CollaborativeSession(
            session_id="session_1",
            host_user_id=user_id,
            collaborative_mode=CollaborativeMode.COOPERATIVE,
            session_name="Test Session 1",
            is_active=True,
        )
        session1.participants[user_id] = CollaborativeParticipant(
            user_id=user_id,
            role=ParticipantRole.HOST,
            choices_made=5,
            messages_sent=10,
            support_given=3,
            support_received=2,
        )

        session2 = CollaborativeSession(
            session_id="session_2",
            host_user_id="other_user",
            collaborative_mode=CollaborativeMode.PEER_SUPPORT,
            session_name="Test Session 2",
            ended_at=datetime.utcnow(),
        )
        session2.participants[user_id] = CollaborativeParticipant(
            user_id=user_id,
            role=ParticipantRole.PARTICIPANT,
            choices_made=3,
            messages_sent=8,
            support_given=5,
            support_received=4,
        )

        collaborative_system.collaborative_sessions["session_1"] = session1
        collaborative_system.collaborative_sessions["session_2"] = session2

        summary = collaborative_system.get_user_collaborative_summary(user_id)

        # Check summary structure
        assert "user_id" in summary
        assert "collaborative_summary" in summary
        assert "participation_metrics" in summary
        assert "collaborative_experience" in summary
        assert "recent_sessions" in summary

        # Check summary values
        collab_summary = summary["collaborative_summary"]
        assert collab_summary["sessions_joined"] == 2
        assert collab_summary["active_sessions"] == 1
        assert collab_summary["completed_sessions"] == 1
        assert collab_summary["sessions_hosted"] == 1

        # Check participation metrics
        metrics = summary["participation_metrics"]
        assert metrics["total_choices_made"] == 8
        assert metrics["total_messages_sent"] == 18
        assert metrics["total_support_given"] == 8
        assert metrics["total_support_received"] == 6
        assert metrics["support_ratio"] == 8 / 6

        # Check collaborative experience
        experience = summary["collaborative_experience"]
        assert "cooperative" in experience["modes_experienced"]
        assert "peer_support" in experience["modes_experienced"]
        assert "host" in experience["roles_played"]
        assert "participant" in experience["roles_played"]

    def test_get_session_analytics(self, collaborative_system):
        """Test session analytics generation."""
        # Create mock session with participants
        session = CollaborativeSession(
            session_id="test_session_123",
            host_user_id="host_user",
            collaborative_mode=CollaborativeMode.COOPERATIVE,
            session_name="Test Analytics Session",
            therapeutic_focus=["anxiety_management"],
            started_at=datetime.utcnow() - timedelta(minutes=30),
            is_active=True,
        )

        # Add participants
        session.participants["host_user"] = CollaborativeParticipant(
            user_id="host_user",
            role=ParticipantRole.HOST,
            choices_made=5,
            messages_sent=8,
            support_given=3,
            support_received=1,
            comfort_level=0.8,
        )
        session.participants["participant_1"] = CollaborativeParticipant(
            user_id="participant_1",
            role=ParticipantRole.PARTICIPANT,
            choices_made=3,
            messages_sent=5,
            support_given=2,
            support_received=3,
            comfort_level=0.7,
        )

        # Add some session data
        session.group_choices = [{"choice_id": "choice_1"}, {"choice_id": "choice_2"}]
        session.support_messages = [
            {"message_id": "msg_1"},
            {"message_id": "msg_2"},
            {"message_id": "msg_3"},
        ]
        session.moderation_log = [{"type": "moderation_action"}]

        collaborative_system.collaborative_sessions["test_session_123"] = session

        analytics = collaborative_system.get_session_analytics("test_session_123")

        # Check analytics structure
        assert "session_id" in analytics
        assert "session_overview" in analytics
        assert "participation_metrics" in analytics
        assert "engagement_metrics" in analytics
        assert "therapeutic_metrics" in analytics
        assert "safety_metrics" in analytics
        assert "participant_details" in analytics

        # Check session overview
        overview = analytics["session_overview"]
        assert overview["session_name"] == "Test Analytics Session"
        assert overview["collaborative_mode"] == "cooperative"
        assert overview["therapeutic_focus"] == ["anxiety_management"]
        assert overview["duration_minutes"] > 0
        assert overview["is_active"]

        # Check participation metrics
        participation = analytics["participation_metrics"]
        assert participation["total_participants"] == 2
        assert participation["active_participants"] == 2

        # Check engagement metrics
        engagement = analytics["engagement_metrics"]
        assert engagement["total_group_choices"] == 2
        assert engagement["total_support_messages"] == 3
        assert engagement["total_support_given"] == 5
        assert (
            engagement["avg_choices_per_participant"] == 1.0
        )  # 2 choices / 2 participants

        # Check therapeutic metrics
        therapeutic = analytics["therapeutic_metrics"]
        assert therapeutic["unique_therapeutic_goals"] == 1
        assert therapeutic["avg_comfort_level"] == 0.75  # (0.8 + 0.7) / 2
        assert therapeutic["support_ratio"] == 2.5  # 5 support given / 2 participants

        # Check participant details
        details = analytics["participant_details"]
        assert len(details) == 2
        assert details[0]["user_id"] in ["host_user", "participant_1"]
        assert "choices_made" in details[0]
        assert "support_given" in details[0]

    def test_metrics_tracking(self, collaborative_system):
        """Test metrics tracking."""
        initial_metrics = collaborative_system.get_metrics()

        # Check metric structure
        assert "collaborative_sessions_created" in initial_metrics
        assert "participants_joined" in initial_metrics
        assert "group_choices_made" in initial_metrics
        assert "support_messages_sent" in initial_metrics
        assert "conflicts_resolved" in initial_metrics
        assert "therapeutic_interventions" in initial_metrics
        assert "safety_escalations" in initial_metrics
        assert "total_collaborative_sessions" in initial_metrics
        assert "active_collaborative_sessions" in initial_metrics

        # Initially should be zero
        assert initial_metrics["collaborative_sessions_created"] == 0
        assert initial_metrics["participants_joined"] == 0
        assert initial_metrics["group_choices_made"] == 0

    @pytest.mark.asyncio
    async def test_health_check(self, collaborative_system):
        """Test health check functionality."""
        health = await collaborative_system.health_check()

        assert health["status"] == "healthy"
        assert "moderation_rules_loaded" in health
        assert "safety_keywords_loaded" in health
        assert "therapeutic_triggers_loaded" in health
        assert "collaborative_sessions_stored" in health
        assert "group_choices_stored" in health
        assert "support_messages_stored" in health
        assert "conflict_resolutions_stored" in health
        assert "metrics" in health

        # Should have loaded rules and keywords
        assert health["moderation_rules_loaded"] > 0
        assert health["safety_keywords_loaded"] > 0
        assert health["therapeutic_triggers_loaded"] > 0
