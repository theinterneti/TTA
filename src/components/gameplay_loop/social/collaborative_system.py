"""
Social and Collaborative Features System for Core Gameplay Loop

This module provides collaborative adventure framework, group experience management,
privacy and sharing controls, moderation tools and conflict resolution processes,
and comprehensive integration with therapeutic, session management, and replayability systems.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

from src.components.gameplay_loop.controllers.gameplay_loop_controller import (
    GameplayLoopController,
)
from src.components.gameplay_loop.models.core import ChoiceType, UserChoice
from src.components.gameplay_loop.narrative.events import (
    EventBus,
    EventType,
    NarrativeEvent,
)
from src.components.gameplay_loop.narrative.replayability_system import (
    ReplayabilitySystem,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
)

logger = logging.getLogger(__name__)


class CollaborativeMode(str, Enum):
    """Types of collaborative modes."""

    SOLO = "solo"  # Individual play
    COOPERATIVE = "cooperative"  # Working together toward shared goals
    PEER_SUPPORT = "peer_support"  # Mutual support and encouragement
    GROUP_THERAPY = "group_therapy"  # Structured therapeutic group experience
    MENTORSHIP = "mentorship"  # Experienced player guiding newcomer
    SHARED_EXPLORATION = "shared_exploration"  # Exploring different paths together


class ParticipantRole(str, Enum):
    """Roles participants can have in collaborative sessions."""

    HOST = "host"  # Session creator and primary facilitator
    PARTICIPANT = "participant"  # Active participant in collaborative experience
    OBSERVER = "observer"  # Can observe but not actively participate
    MENTOR = "mentor"  # Experienced player providing guidance
    MENTEE = "mentee"  # Learning from mentor's guidance
    FACILITATOR = "facilitator"  # Therapeutic facilitator (professional)


class PrivacyLevel(str, Enum):
    """Privacy levels for sharing experiences."""

    PRIVATE = "private"  # Only participant can see
    FRIENDS = "friends"  # Only approved friends can see
    GROUP = "group"  # Only group members can see
    COMMUNITY = "community"  # Community members can see (with moderation)
    PUBLIC = "public"  # Publicly visible (with strict moderation)


class ModerationAction(str, Enum):
    """Types of moderation actions."""

    WARNING = "warning"  # Issue warning to participant
    MUTE = "mute"  # Temporarily prevent communication
    REMOVE = "remove"  # Remove from collaborative session
    BAN = "ban"  # Prevent future participation
    ESCALATE = "escalate"  # Escalate to human moderator
    THERAPEUTIC_INTERVENTION = "therapeutic_intervention"  # Trigger therapeutic support


@dataclass
class CollaborativeParticipant:
    """Represents a participant in a collaborative session."""

    participant_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    username: str = ""

    # Participation details
    role: ParticipantRole = ParticipantRole.PARTICIPANT
    joined_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

    # Permissions and settings
    can_make_choices: bool = True
    can_communicate: bool = True
    can_view_others_progress: bool = True
    privacy_level: PrivacyLevel = PrivacyLevel.GROUP

    # Therapeutic context
    therapeutic_goals: list[str] = field(default_factory=list)
    comfort_level: float = 1.0  # 0.0 to 1.0
    needs_support: bool = False

    # Participation metrics
    choices_made: int = 0
    messages_sent: int = 0
    support_given: int = 0
    support_received: int = 0

    # Status
    is_active: bool = True
    is_muted: bool = False
    warnings_count: int = 0


@dataclass
class CollaborativeSession:
    """Represents a collaborative therapeutic session."""

    session_id: str = field(default_factory=lambda: str(uuid4()))
    host_user_id: str = ""

    # Session configuration
    collaborative_mode: CollaborativeMode = CollaborativeMode.COOPERATIVE
    session_name: str = ""
    description: str = ""
    max_participants: int = 4

    # Therapeutic configuration
    therapeutic_focus: list[str] = field(default_factory=list)
    requires_facilitator: bool = False
    safety_level: str = "standard"  # standard, high, maximum

    # Participants
    participants: dict[str, CollaborativeParticipant] = field(default_factory=dict)
    waiting_list: list[str] = field(default_factory=list)  # user_ids waiting to join

    # Session state
    base_session_state: SessionState | None = None
    shared_context: dict[str, Any] = field(default_factory=dict)
    group_choices: list[dict[str, Any]] = field(default_factory=list)

    # Communication
    chat_messages: list[dict[str, Any]] = field(default_factory=list)
    support_messages: list[dict[str, Any]] = field(default_factory=list)

    # Privacy and sharing
    privacy_level: PrivacyLevel = PrivacyLevel.GROUP
    sharing_enabled: bool = True
    consent_required: bool = True

    # Moderation
    moderation_enabled: bool = True
    auto_moderation: bool = True
    human_moderator_id: str | None = None
    moderation_log: list[dict[str, Any]] = field(default_factory=list)

    # Session lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    is_active: bool = False
    is_paused: bool = False


@dataclass
class GroupChoice:
    """Represents a choice made by the group."""

    choice_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""

    # Choice details
    choice_text: str = ""
    choice_type: ChoiceType = ChoiceType.NARRATIVE
    proposed_by: str = ""  # user_id

    # Group decision process
    votes: dict[str, str] = field(
        default_factory=dict
    )  # user_id -> vote (support/oppose/abstain)
    discussion_messages: list[str] = field(default_factory=list)  # message_ids

    # Decision outcome
    is_approved: bool = False
    approval_threshold: float = 0.6  # Percentage needed for approval
    decision_method: str = "consensus"  # consensus, majority, facilitator

    # Therapeutic considerations
    therapeutic_impact: dict[str, Any] = field(default_factory=dict)
    safety_assessment: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    proposed_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: datetime | None = None
    executed_at: datetime | None = None


@dataclass
class SupportMessage:
    """Represents a support message between participants."""

    message_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""

    # Message details
    sender_id: str = ""
    recipient_id: str = ""  # Empty for group messages
    message_text: str = ""
    message_type: str = "encouragement"  # encouragement, advice, empathy, celebration

    # Context
    related_choice_id: str | None = None
    related_milestone: str | None = None
    therapeutic_context: dict[str, Any] = field(default_factory=dict)

    # Moderation
    is_approved: bool = True
    moderation_notes: str = ""

    # Timestamps
    sent_at: datetime = field(default_factory=datetime.utcnow)
    delivered_at: datetime | None = None


@dataclass
class ConflictResolution:
    """Represents a conflict resolution process."""

    resolution_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""

    # Conflict details
    conflict_type: str = (
        "disagreement"  # disagreement, inappropriate_behavior, therapeutic_concern
    )
    involved_participants: list[str] = field(default_factory=list)  # user_ids
    description: str = ""

    # Resolution process
    resolution_method: str = (
        "mediation"  # mediation, voting, facilitator_decision, therapeutic_intervention
    )
    mediator_id: str | None = None
    resolution_steps: list[dict[str, Any]] = field(default_factory=list)

    # Outcome
    is_resolved: bool = False
    resolution_summary: str = ""
    agreed_actions: list[str] = field(default_factory=list)

    # Therapeutic considerations
    therapeutic_learning: list[str] = field(default_factory=list)
    safety_measures: list[str] = field(default_factory=list)

    # Timestamps
    reported_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: datetime | None = None


class CollaborativeSystem:
    """Main system for social and collaborative therapeutic experiences."""

    def __init__(
        self,
        event_bus: EventBus,
        gameplay_controller: GameplayLoopController,
        replayability_system: ReplayabilitySystem,
    ):
        self.event_bus = event_bus
        self.gameplay_controller = gameplay_controller
        self.replayability_system = replayability_system

        # Collaborative session storage
        self.collaborative_sessions: dict[str, CollaborativeSession] = {}
        self.group_choices: dict[str, GroupChoice] = {}
        self.support_messages: dict[str, SupportMessage] = {}
        self.conflict_resolutions: dict[str, ConflictResolution] = {}

        # User tracking
        self.user_sessions: dict[str, list[str]] = {}  # user_id -> session_ids
        self.user_friends: dict[str, set[str]] = {}  # user_id -> friend_user_ids
        self.user_preferences: dict[str, dict[str, Any]] = {}  # user_id -> preferences

        # Moderation system
        self.moderation_rules = self._load_moderation_rules()
        self.safety_keywords = self._load_safety_keywords()
        self.therapeutic_triggers = self._load_therapeutic_triggers()

        # Metrics
        self.metrics = {
            "collaborative_sessions_created": 0,
            "participants_joined": 0,
            "group_choices_made": 0,
            "support_messages_sent": 0,
            "conflicts_resolved": 0,
            "therapeutic_interventions": 0,
            "safety_escalations": 0,
        }

    def _load_moderation_rules(self) -> dict[str, Any]:
        """Load moderation rules and policies."""
        return {
            "inappropriate_language": {
                "action": ModerationAction.WARNING,
                "escalation_threshold": 2,
                "escalation_action": ModerationAction.MUTE,
            },
            "therapeutic_boundary_violation": {
                "action": ModerationAction.THERAPEUTIC_INTERVENTION,
                "escalation_threshold": 1,
                "escalation_action": ModerationAction.ESCALATE,
            },
            "harassment": {
                "action": ModerationAction.REMOVE,
                "escalation_threshold": 1,
                "escalation_action": ModerationAction.BAN,
            },
            "spam": {
                "action": ModerationAction.MUTE,
                "escalation_threshold": 3,
                "escalation_action": ModerationAction.REMOVE,
            },
            "safety_concern": {
                "action": ModerationAction.ESCALATE,
                "escalation_threshold": 1,
                "escalation_action": ModerationAction.THERAPEUTIC_INTERVENTION,
            },
        }

    async def create_collaborative_session(
        self,
        host_user_id: str,
        session_name: str,
        collaborative_mode: CollaborativeMode = CollaborativeMode.COOPERATIVE,
        therapeutic_focus: list[str] = None,
        max_participants: int = 4,
    ) -> CollaborativeSession:
        """Create a new collaborative therapeutic session."""
        try:
            # Create collaborative session
            session = CollaborativeSession(
                host_user_id=host_user_id,
                collaborative_mode=collaborative_mode,
                session_name=session_name
                or f"{collaborative_mode.value.title()} Session",
                description=f"Collaborative therapeutic experience focused on {', '.join(therapeutic_focus or ['general wellness'])}",
                max_participants=max_participants,
                therapeutic_focus=therapeutic_focus or ["general_wellness"],
            )

            # Add host as first participant
            host_participant = CollaborativeParticipant(
                user_id=host_user_id,
                username=f"User_{host_user_id[:8]}",  # Would be replaced with actual username
                role=ParticipantRole.HOST,
                therapeutic_goals=therapeutic_focus or [],
            )

            session.participants[host_user_id] = host_participant

            # Configure session based on mode
            if collaborative_mode == CollaborativeMode.GROUP_THERAPY:
                session.requires_facilitator = True
                session.safety_level = "high"
                session.consent_required = True
            elif collaborative_mode == CollaborativeMode.MENTORSHIP:
                session.max_participants = 2
                session.safety_level = "standard"
            elif collaborative_mode == CollaborativeMode.SHARED_EXPLORATION:
                session.sharing_enabled = True
                session.privacy_level = PrivacyLevel.GROUP

            # Store session
            self.collaborative_sessions[session.session_id] = session

            # Track user sessions
            if host_user_id not in self.user_sessions:
                self.user_sessions[host_user_id] = []
            self.user_sessions[host_user_id].append(session.session_id)

            # Publish session creation event
            await self._publish_collaborative_event(
                session,
                "collaborative_session_created",
                {
                    "session_id": session.session_id,
                    "collaborative_mode": collaborative_mode.value,
                    "therapeutic_focus": therapeutic_focus or [],
                    "max_participants": max_participants,
                },
            )

            self.metrics["collaborative_sessions_created"] += 1

            return session

        except Exception as e:
            logger.error(
                f"Failed to create collaborative session for user {host_user_id}: {e}"
            )
            raise

    async def join_collaborative_session(
        self,
        session_id: str,
        user_id: str,
        role: ParticipantRole = ParticipantRole.PARTICIPANT,
        therapeutic_goals: list[str] = None,
    ) -> CollaborativeParticipant:
        """Join an existing collaborative session."""
        try:
            # Get session
            session = self.collaborative_sessions.get(session_id)
            if not session:
                raise ValueError(f"Collaborative session {session_id} not found")

            if not session.is_active:
                raise ValueError(f"Session {session_id} is not active")

            # Check if user is already in session
            if user_id in session.participants:
                return session.participants[user_id]

            # Check capacity
            if len(session.participants) >= session.max_participants:
                # Add to waiting list
                if user_id not in session.waiting_list:
                    session.waiting_list.append(user_id)
                raise ValueError(
                    f"Session {session_id} is full. Added to waiting list."
                )

            # Check if facilitator is required and available
            if session.requires_facilitator and role != ParticipantRole.FACILITATOR:
                has_facilitator = any(
                    p.role == ParticipantRole.FACILITATOR
                    for p in session.participants.values()
                )
                if not has_facilitator:
                    raise ValueError(
                        f"Session {session_id} requires a facilitator to be present"
                    )

            # Create participant
            participant = CollaborativeParticipant(
                user_id=user_id,
                username=f"User_{user_id[:8]}",  # Would be replaced with actual username
                role=role,
                therapeutic_goals=therapeutic_goals or [],
            )

            # Add participant to session
            session.participants[user_id] = participant

            # Track user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)

            # Publish join event
            await self._publish_collaborative_event(
                session,
                "participant_joined",
                {
                    "user_id": user_id,
                    "role": role.value,
                    "participant_count": len(session.participants),
                },
            )

            self.metrics["participants_joined"] += 1

            return participant

        except Exception as e:
            logger.error(
                f"Failed to join collaborative session {session_id} for user {user_id}: {e}"
            )
            raise

    async def start_collaborative_session(
        self, session_id: str, base_session_state: SessionState
    ) -> CollaborativeSession:
        """Start a collaborative session with shared therapeutic experience."""
        try:
            # Get session
            session = self.collaborative_sessions.get(session_id)
            if not session:
                raise ValueError(f"Collaborative session {session_id} not found")

            if session.is_active:
                raise ValueError(f"Session {session_id} is already active")

            # Validate minimum participants
            if (
                len(session.participants) < 2
                and session.collaborative_mode != CollaborativeMode.SOLO
            ):
                raise ValueError(f"Session {session_id} needs at least 2 participants")

            # Check facilitator requirement
            if session.requires_facilitator:
                has_facilitator = any(
                    p.role == ParticipantRole.FACILITATOR
                    for p in session.participants.values()
                )
                if not has_facilitator:
                    raise ValueError(
                        f"Session {session_id} requires a facilitator to start"
                    )

            # Set up shared session state
            session.base_session_state = base_session_state
            session.shared_context = {
                "collaborative_mode": session.collaborative_mode.value,
                "therapeutic_focus": session.therapeutic_focus,
                "participants": {
                    user_id: {
                        "role": participant.role.value,
                        "therapeutic_goals": participant.therapeutic_goals,
                        "comfort_level": participant.comfort_level,
                    }
                    for user_id, participant in session.participants.items()
                },
                "group_dynamics": {
                    "consensus_threshold": 0.6,
                    "decision_timeout_minutes": 5,
                    "support_encouraged": True,
                },
            }

            # Start session
            session.is_active = True
            session.started_at = datetime.utcnow()

            # Initialize group therapeutic context
            await self._initialize_group_therapeutic_context(session)

            # Publish session start event
            await self._publish_collaborative_event(
                session,
                "collaborative_session_started",
                {
                    "participant_count": len(session.participants),
                    "therapeutic_focus": session.therapeutic_focus,
                    "collaborative_mode": session.collaborative_mode.value,
                },
            )

            return session

        except Exception as e:
            logger.error(f"Failed to start collaborative session {session_id}: {e}")
            raise

    async def propose_group_choice(
        self,
        session_id: str,
        proposer_user_id: str,
        choice_text: str,
        choice_type: ChoiceType = ChoiceType.NARRATIVE,
    ) -> GroupChoice:
        """Propose a choice for group consideration."""
        try:
            # Get session and validate
            session = self.collaborative_sessions.get(session_id)
            if not session or not session.is_active:
                raise ValueError(f"Session {session_id} not found or not active")

            # Validate proposer
            participant = session.participants.get(proposer_user_id)
            if not participant or not participant.can_make_choices:
                raise ValueError(
                    f"User {proposer_user_id} cannot propose choices in this session"
                )

            # Create group choice
            group_choice = GroupChoice(
                session_id=session_id,
                choice_text=choice_text,
                choice_type=choice_type,
                proposed_by=proposer_user_id,
                approval_threshold=session.shared_context.get(
                    "consensus_threshold", 0.6
                ),
            )

            # Assess therapeutic impact and safety
            group_choice.therapeutic_impact = (
                await self._assess_choice_therapeutic_impact(
                    choice_text, choice_type, session.therapeutic_focus
                )
            )
            group_choice.safety_assessment = await self._assess_choice_safety(
                choice_text, session.safety_level
            )

            # Check if choice needs immediate approval (safety concerns)
            if group_choice.safety_assessment.get("requires_immediate_review", False):
                await self._escalate_choice_for_review(group_choice, session)
                return group_choice

            # Store choice
            self.group_choices[group_choice.choice_id] = group_choice
            session.group_choices.append(
                {
                    "choice_id": group_choice.choice_id,
                    "proposed_at": group_choice.proposed_at.isoformat(),
                    "status": "pending_votes",
                }
            )

            # Notify all participants
            await self._notify_participants_of_choice(session, group_choice)

            # Publish choice proposal event
            await self._publish_collaborative_event(
                session,
                "group_choice_proposed",
                {
                    "choice_id": group_choice.choice_id,
                    "proposer_user_id": proposer_user_id,
                    "choice_text": choice_text,
                    "choice_type": choice_type.value,
                },
            )

            return group_choice

        except Exception as e:
            logger.error(f"Failed to propose group choice in session {session_id}: {e}")
            raise

    async def vote_on_group_choice(
        self, choice_id: str, voter_user_id: str, vote: str
    ) -> bool:
        """Vote on a proposed group choice."""
        try:
            # Get choice
            group_choice = self.group_choices.get(choice_id)
            if not group_choice:
                raise ValueError(f"Group choice {choice_id} not found")

            # Get session
            session = self.collaborative_sessions.get(group_choice.session_id)
            if not session or not session.is_active:
                raise ValueError("Session not found or not active")

            # Validate voter
            participant = session.participants.get(voter_user_id)
            if not participant or not participant.can_make_choices:
                raise ValueError(f"User {voter_user_id} cannot vote in this session")

            # Validate vote
            if vote not in ["support", "oppose", "abstain"]:
                raise ValueError(f"Invalid vote: {vote}")

            # Record vote
            group_choice.votes[voter_user_id] = vote

            # Check if decision can be made
            total_participants = len(
                [p for p in session.participants.values() if p.can_make_choices]
            )
            votes_cast = len(group_choice.votes)
            support_votes = len(
                [v for v in group_choice.votes.values() if v == "support"]
            )

            # Calculate approval percentage
            approval_percentage = (
                support_votes / total_participants if total_participants > 0 else 0
            )

            # Check if threshold is met or all votes are in
            if (
                approval_percentage >= group_choice.approval_threshold
                or votes_cast >= total_participants
            ):
                group_choice.is_approved = (
                    approval_percentage >= group_choice.approval_threshold
                )
                group_choice.decided_at = datetime.utcnow()

                # Execute choice if approved
                if group_choice.is_approved:
                    await self._execute_group_choice(group_choice, session)

                # Publish decision event
                await self._publish_collaborative_event(
                    session,
                    "group_choice_decided",
                    {
                        "choice_id": choice_id,
                        "is_approved": group_choice.is_approved,
                        "approval_percentage": approval_percentage,
                        "votes": dict(group_choice.votes),
                    },
                )

                return True  # Decision made

            # Publish vote event
            await self._publish_collaborative_event(
                session,
                "group_choice_vote_cast",
                {
                    "choice_id": choice_id,
                    "voter_user_id": voter_user_id,
                    "vote": vote,
                    "votes_cast": votes_cast,
                    "total_participants": total_participants,
                },
            )

            return False  # Decision pending

        except Exception as e:
            logger.error(f"Failed to vote on group choice {choice_id}: {e}")
            raise

    async def send_support_message(
        self,
        session_id: str,
        sender_id: str,
        recipient_id: str,
        message_text: str,
        message_type: str = "encouragement",
    ) -> SupportMessage:
        """Send a support message to another participant."""
        try:
            # Get session and validate
            session = self.collaborative_sessions.get(session_id)
            if not session or not session.is_active:
                raise ValueError(f"Session {session_id} not found or not active")

            # Validate sender
            sender = session.participants.get(sender_id)
            if not sender or not sender.can_communicate:
                raise ValueError(
                    f"User {sender_id} cannot send messages in this session"
                )

            # Validate recipient (empty for group messages)
            if recipient_id and recipient_id not in session.participants:
                raise ValueError(f"Recipient {recipient_id} not in session")

            # Create support message
            support_message = SupportMessage(
                session_id=session_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                message_text=message_text,
                message_type=message_type,
            )

            # Moderate message
            moderation_result = await self._moderate_message(support_message, session)
            support_message.is_approved = moderation_result["approved"]
            support_message.moderation_notes = moderation_result.get("notes", "")

            # Store message
            self.support_messages[support_message.message_id] = support_message
            session.support_messages.append(
                {
                    "message_id": support_message.message_id,
                    "sender_id": sender_id,
                    "recipient_id": recipient_id,
                    "message_type": message_type,
                    "sent_at": support_message.sent_at.isoformat(),
                    "is_approved": support_message.is_approved,
                }
            )

            # Update participant metrics
            sender.messages_sent += 1
            sender.support_given += 1

            if recipient_id and recipient_id in session.participants:
                session.participants[recipient_id].support_received += 1

            # Deliver message if approved
            if support_message.is_approved:
                support_message.delivered_at = datetime.utcnow()

                # Publish message event
                await self._publish_collaborative_event(
                    session,
                    "support_message_sent",
                    {
                        "message_id": support_message.message_id,
                        "sender_id": sender_id,
                        "recipient_id": recipient_id,
                        "message_type": message_type,
                        "is_group_message": not recipient_id,
                    },
                )

                self.metrics["support_messages_sent"] += 1

            return support_message

        except Exception as e:
            logger.error(f"Failed to send support message in session {session_id}: {e}")
            raise

    async def report_conflict(
        self,
        session_id: str,
        reporter_id: str,
        conflict_type: str,
        involved_participants: list[str],
        description: str,
    ) -> ConflictResolution:
        """Report a conflict that needs resolution."""
        try:
            # Get session and validate
            session = self.collaborative_sessions.get(session_id)
            if not session or not session.is_active:
                raise ValueError(f"Session {session_id} not found or not active")

            # Validate reporter
            if reporter_id not in session.participants:
                raise ValueError(f"Reporter {reporter_id} not in session")

            # Validate involved participants
            for participant_id in involved_participants:
                if participant_id not in session.participants:
                    raise ValueError(f"Participant {participant_id} not in session")

            # Create conflict resolution
            conflict_resolution = ConflictResolution(
                session_id=session_id,
                conflict_type=conflict_type,
                involved_participants=involved_participants,
                description=description,
            )

            # Determine resolution method based on conflict type and session settings
            if conflict_type == "therapeutic_concern":
                conflict_resolution.resolution_method = "therapeutic_intervention"
                conflict_resolution.mediator_id = session.human_moderator_id
            elif conflict_type == "inappropriate_behavior":
                conflict_resolution.resolution_method = "facilitator_decision"
                # Find facilitator
                facilitator = next(
                    (
                        p
                        for p in session.participants.values()
                        if p.role == ParticipantRole.FACILITATOR
                    ),
                    None,
                )
                if facilitator:
                    conflict_resolution.mediator_id = facilitator.user_id
            else:
                conflict_resolution.resolution_method = "mediation"

            # Store conflict resolution
            self.conflict_resolutions[conflict_resolution.resolution_id] = (
                conflict_resolution
            )
            session.moderation_log.append(
                {
                    "type": "conflict_reported",
                    "resolution_id": conflict_resolution.resolution_id,
                    "reporter_id": reporter_id,
                    "conflict_type": conflict_type,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Initiate resolution process
            await self._initiate_conflict_resolution(conflict_resolution, session)

            # Publish conflict report event
            await self._publish_collaborative_event(
                session,
                "conflict_reported",
                {
                    "resolution_id": conflict_resolution.resolution_id,
                    "conflict_type": conflict_type,
                    "involved_participants": involved_participants,
                    "resolution_method": conflict_resolution.resolution_method,
                },
            )

            return conflict_resolution

        except Exception as e:
            logger.error(f"Failed to report conflict in session {session_id}: {e}")
            raise

    async def moderate_participant(
        self,
        session_id: str,
        moderator_id: str,
        target_user_id: str,
        action: ModerationAction,
        reason: str,
    ) -> dict[str, Any]:
        """Apply moderation action to a participant."""
        try:
            # Get session and validate
            session = self.collaborative_sessions.get(session_id)
            if not session or not session.is_active:
                raise ValueError(f"Session {session_id} not found or not active")

            # Validate moderator permissions
            moderator = session.participants.get(moderator_id)
            if not moderator or moderator.role not in [
                ParticipantRole.HOST,
                ParticipantRole.FACILITATOR,
            ]:
                raise ValueError(
                    f"User {moderator_id} does not have moderation permissions"
                )

            # Validate target participant
            target_participant = session.participants.get(target_user_id)
            if not target_participant:
                raise ValueError(f"Target participant {target_user_id} not found")

            # Apply moderation action
            moderation_result = {
                "action": action.value,
                "target_user_id": target_user_id,
                "moderator_id": moderator_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
            }

            if action == ModerationAction.WARNING:
                target_participant.warnings_count += 1
                moderation_result["warnings_count"] = target_participant.warnings_count

            elif action == ModerationAction.MUTE:
                target_participant.is_muted = True
                target_participant.can_communicate = False
                moderation_result["mute_duration"] = "session"

            elif action == ModerationAction.REMOVE:
                target_participant.is_active = False
                # Remove from session
                del session.participants[target_user_id]
                moderation_result["removed_from_session"] = True

            elif action == ModerationAction.THERAPEUTIC_INTERVENTION:
                # Trigger therapeutic support
                await self._trigger_therapeutic_intervention(
                    target_user_id, session, reason
                )
                moderation_result["intervention_triggered"] = True

            elif action == ModerationAction.ESCALATE:
                # Escalate to human moderator
                await self._escalate_to_human_moderator(session, target_user_id, reason)
                moderation_result["escalated"] = True

            # Log moderation action
            session.moderation_log.append(
                {
                    "type": "moderation_action",
                    "action": action.value,
                    "target_user_id": target_user_id,
                    "moderator_id": moderator_id,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Publish moderation event
            await self._publish_collaborative_event(
                session,
                "moderation_action_applied",
                {
                    "action": action.value,
                    "target_user_id": target_user_id,
                    "moderator_id": moderator_id,
                    "reason": reason,
                },
            )

            return moderation_result

        except Exception as e:
            logger.error(
                f"Failed to moderate participant {target_user_id} in session {session_id}: {e}"
            )
            raise

    async def _initialize_group_therapeutic_context(
        self, session: CollaborativeSession
    ) -> None:
        """Initialize therapeutic context for group session."""
        try:
            # Aggregate therapeutic goals from all participants
            all_goals = set()
            for participant in session.participants.values():
                all_goals.update(participant.therapeutic_goals)

            # Set up group therapeutic framework
            session.shared_context["group_therapeutic_framework"] = {
                "collective_goals": list(all_goals),
                "support_mechanisms": [
                    "peer_encouragement",
                    "shared_experiences",
                    "group_reflection",
                ],
                "safety_protocols": [
                    "crisis_intervention",
                    "boundary_respect",
                    "confidentiality",
                ],
                "progress_tracking": "collective_and_individual",
            }

            # Initialize group dynamics
            session.shared_context["group_dynamics"][
                "established_at"
            ] = datetime.utcnow().isoformat()
            session.shared_context["group_dynamics"][
                "trust_level"
            ] = 0.5  # Starting trust level
            session.shared_context["group_dynamics"][
                "cohesion_score"
            ] = 0.3  # Starting cohesion

        except Exception as e:
            logger.error(f"Failed to initialize group therapeutic context: {e}")

    async def _assess_choice_therapeutic_impact(
        self, choice_text: str, choice_type: ChoiceType, therapeutic_focus: list[str]
    ) -> dict[str, Any]:
        """Assess the therapeutic impact of a proposed choice."""
        try:
            impact_assessment = {
                "therapeutic_relevance": 0.5,  # Default neutral
                "alignment_with_focus": 0.5,
                "potential_benefits": [],
                "potential_concerns": [],
                "group_suitability": 0.7,
            }

            # Analyze choice text for therapeutic keywords
            choice_lower = choice_text.lower()

            # Check alignment with therapeutic focus
            focus_keywords = {
                "anxiety_management": [
                    "calm",
                    "breathe",
                    "relax",
                    "peaceful",
                    "mindful",
                ],
                "communication_skills": [
                    "talk",
                    "listen",
                    "express",
                    "share",
                    "communicate",
                ],
                "emotional_regulation": [
                    "feel",
                    "emotion",
                    "manage",
                    "cope",
                    "process",
                ],
                "problem_solving": [
                    "solve",
                    "plan",
                    "strategy",
                    "approach",
                    "solution",
                ],
                "self_awareness": [
                    "reflect",
                    "understand",
                    "realize",
                    "insight",
                    "awareness",
                ],
            }

            alignment_score = 0.0
            for focus_area in therapeutic_focus:
                if focus_area in focus_keywords:
                    keywords = focus_keywords[focus_area]
                    matches = sum(1 for keyword in keywords if keyword in choice_lower)
                    if matches > 0:
                        alignment_score += matches / len(keywords)
                        impact_assessment["potential_benefits"].append(
                            f"Supports {focus_area}"
                        )

            if therapeutic_focus:
                impact_assessment["alignment_with_focus"] = min(
                    1.0, alignment_score / len(therapeutic_focus)
                )

            # Assess therapeutic relevance based on choice type
            therapeutic_choice_types = {
                ChoiceType.EMOTIONAL_REGULATION: 0.9,
                ChoiceType.COMMUNICATION: 0.8,
                ChoiceType.PROBLEM_SOLVING: 0.8,
                ChoiceType.SELF_REFLECTION: 0.9,
                ChoiceType.SOCIAL_INTERACTION: 0.7,
                ChoiceType.NARRATIVE: 0.5,
            }

            impact_assessment["therapeutic_relevance"] = therapeutic_choice_types.get(
                choice_type, 0.5
            )

            # Check for potential concerns
            concern_indicators = ["avoid", "ignore", "give up", "quit", "impossible"]
            if any(indicator in choice_lower for indicator in concern_indicators):
                impact_assessment["potential_concerns"].append(
                    "May discourage therapeutic progress"
                )
                impact_assessment["therapeutic_relevance"] *= 0.7

            return impact_assessment

        except Exception as e:
            logger.error(f"Failed to assess choice therapeutic impact: {e}")
            return {
                "therapeutic_relevance": 0.5,
                "alignment_with_focus": 0.5,
                "potential_benefits": [],
                "potential_concerns": [],
                "group_suitability": 0.5,
            }

    async def _assess_choice_safety(
        self, choice_text: str, safety_level: str
    ) -> dict[str, Any]:
        """Assess the safety of a proposed choice."""
        try:
            safety_assessment = {
                "safety_score": 1.0,  # 1.0 = completely safe, 0.0 = unsafe
                "safety_concerns": [],
                "requires_immediate_review": False,
                "recommended_modifications": [],
            }

            choice_lower = choice_text.lower()

            # Check for crisis indicators
            for indicator in self.safety_keywords["crisis_indicators"]:
                if indicator in choice_lower:
                    safety_assessment["safety_score"] = 0.0
                    safety_assessment["safety_concerns"].append(
                        "Contains crisis language"
                    )
                    safety_assessment["requires_immediate_review"] = True
                    break

            # Check for inappropriate content
            for category, keywords in self.safety_keywords.items():
                if category != "crisis_indicators":
                    for keyword in keywords:
                        if keyword in choice_lower:
                            safety_assessment["safety_score"] *= 0.5
                            safety_assessment["safety_concerns"].append(
                                f"Contains {category.replace('_', ' ')}"
                            )

            # Adjust based on safety level
            if safety_level == "high" and safety_assessment["safety_score"] < 0.8:
                safety_assessment["requires_immediate_review"] = True
            elif safety_level == "maximum" and safety_assessment["safety_score"] < 0.9:
                safety_assessment["requires_immediate_review"] = True

            return safety_assessment

        except Exception as e:
            logger.error(f"Failed to assess choice safety: {e}")
            return {
                "safety_score": 0.5,
                "safety_concerns": ["Assessment failed"],
                "requires_immediate_review": True,
                "recommended_modifications": [],
            }

    async def _moderate_message(
        self, message: SupportMessage, session: CollaborativeSession
    ) -> dict[str, Any]:
        """Moderate a support message for appropriateness."""
        try:
            moderation_result = {
                "approved": True,
                "confidence": 1.0,
                "notes": "",
                "required_actions": [],
            }

            message_lower = message.message_text.lower()

            # Check for safety keywords
            for category, keywords in self.safety_keywords.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        moderation_result["approved"] = False
                        moderation_result["notes"] = (
                            f"Contains {category.replace('_', ' ')}"
                        )
                        moderation_result["required_actions"].append("human_review")
                        break
                if not moderation_result["approved"]:
                    break

            # Check for therapeutic appropriateness
            if message.message_type == "advice" and session.requires_facilitator:
                # In facilitated sessions, advice should come from facilitators
                sender = session.participants.get(message.sender_id)
                if sender and sender.role not in [
                    ParticipantRole.FACILITATOR,
                    ParticipantRole.MENTOR,
                ]:
                    moderation_result["approved"] = False
                    moderation_result["notes"] = (
                        "Advice should come from facilitators in this session type"
                    )

            # Check message length and appropriateness
            if len(message.message_text) > 500:
                moderation_result["notes"] = "Message is quite long"
                moderation_result["confidence"] *= 0.9

            return moderation_result

        except Exception as e:
            logger.error(f"Failed to moderate message: {e}")
            return {
                "approved": False,
                "confidence": 0.0,
                "notes": "Moderation failed",
                "required_actions": ["human_review"],
            }

    async def _execute_group_choice(
        self, group_choice: GroupChoice, session: CollaborativeSession
    ) -> None:
        """Execute an approved group choice."""
        try:
            # Create user choice for the group
            UserChoice(
                choice_id=group_choice.choice_id,
                text=group_choice.choice_text,
                choice_type=group_choice.choice_type,
                user_id="group",  # Special identifier for group choices
                therapeutic_relevance=group_choice.therapeutic_impact.get(
                    "therapeutic_relevance", 0.5
                ),
            )

            # Process choice through gameplay controller for each participant
            for participant in session.participants.values():
                if participant.can_make_choices:
                    # Create individual session state if needed
                    individual_state = session.base_session_state
                    individual_state.user_id = participant.user_id

                    # Process choice (this would integrate with existing choice processing)
                    # await self.gameplay_controller.process_choice(individual_state, user_choice)

            group_choice.executed_at = datetime.utcnow()

            # Update group metrics
            self.metrics["group_choices_made"] += 1

        except Exception as e:
            logger.error(
                f"Failed to execute group choice {group_choice.choice_id}: {e}"
            )

    async def _notify_participants_of_choice(
        self, session: CollaborativeSession, group_choice: GroupChoice
    ) -> None:
        """Notify all participants of a proposed choice."""
        try:
            {
                "type": "group_choice_proposed",
                "choice_id": group_choice.choice_id,
                "choice_text": group_choice.choice_text,
                "proposed_by": group_choice.proposed_by,
                "voting_deadline": (
                    datetime.utcnow() + timedelta(minutes=5)
                ).isoformat(),
                "therapeutic_impact": group_choice.therapeutic_impact,
            }

            # Send notification to all participants who can vote
            for participant in session.participants.values():
                if (
                    participant.can_make_choices
                    and participant.user_id != group_choice.proposed_by
                ):
                    # This would integrate with notification system
                    pass

        except Exception as e:
            logger.error(f"Failed to notify participants of choice: {e}")

    async def _initiate_conflict_resolution(
        self, conflict_resolution: ConflictResolution, session: CollaborativeSession
    ) -> None:
        """Initiate the conflict resolution process."""
        try:
            if conflict_resolution.resolution_method == "therapeutic_intervention":
                # Trigger immediate therapeutic support
                for participant_id in conflict_resolution.involved_participants:
                    await self._trigger_therapeutic_intervention(
                        participant_id, session, conflict_resolution.description
                    )

            elif conflict_resolution.resolution_method == "mediation":
                # Set up mediation process
                conflict_resolution.resolution_steps.append(
                    {
                        "step": "mediation_initiated",
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": "Mediation process started",
                    }
                )

            elif conflict_resolution.resolution_method == "facilitator_decision":
                # Notify facilitator for decision
                if conflict_resolution.mediator_id:
                    # This would integrate with notification system
                    pass

        except Exception as e:
            logger.error(f"Failed to initiate conflict resolution: {e}")

    async def _trigger_therapeutic_intervention(
        self, user_id: str, session: CollaborativeSession, reason: str
    ) -> None:
        """Trigger therapeutic intervention for a participant."""
        try:
            {
                "user_id": user_id,
                "session_id": session.session_id,
                "intervention_type": "collaborative_support",
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "support_resources": [
                    "peer_support_available",
                    "facilitator_guidance",
                    "crisis_resources_if_needed",
                ],
            }

            # This would integrate with existing therapeutic intervention systems
            # await self.therapeutic_integrator.trigger_intervention(intervention_data)

            self.metrics["therapeutic_interventions"] += 1

        except Exception as e:
            logger.error(f"Failed to trigger therapeutic intervention: {e}")

    async def _escalate_to_human_moderator(
        self, session: CollaborativeSession, user_id: str, reason: str
    ) -> None:
        """Escalate issue to human moderator."""
        try:
            {
                "session_id": session.session_id,
                "user_id": user_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "priority": "high" if "safety" in reason.lower() else "medium",
            }

            # This would integrate with human moderator notification system
            # await self.moderation_service.escalate(escalation_data)

            self.metrics["safety_escalations"] += 1

        except Exception as e:
            logger.error(f"Failed to escalate to human moderator: {e}")

    async def _publish_collaborative_event(
        self, session: CollaborativeSession, event_type: str, context: dict[str, Any]
    ) -> None:
        """Publish collaborative event."""
        try:
            narrative_event = NarrativeEvent(
                event_type=EventType.COLLABORATIVE_EVENT,
                session_id=session.session_id,
                user_id=session.host_user_id,
                context={
                    "collaborative_event_type": event_type,
                    "collaborative_mode": session.collaborative_mode.value,
                    **context,
                },
            )

            await self.event_bus.publish(narrative_event)

        except Exception as e:
            logger.error(f"Failed to publish collaborative event {event_type}: {e}")

    def get_user_collaborative_summary(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive collaborative summary for a user."""
        try:
            user_sessions = self.user_sessions.get(user_id, [])

            # Get session details
            sessions = [
                self.collaborative_sessions[session_id]
                for session_id in user_sessions
                if session_id in self.collaborative_sessions
            ]
            active_sessions = [s for s in sessions if s.is_active]
            completed_sessions = [s for s in sessions if s.ended_at is not None]

            # Calculate participation metrics
            total_choices_made = 0
            total_messages_sent = 0
            total_support_given = 0
            total_support_received = 0

            for session in sessions:
                if user_id in session.participants:
                    participant = session.participants[user_id]
                    total_choices_made += participant.choices_made
                    total_messages_sent += participant.messages_sent
                    total_support_given += participant.support_given
                    total_support_received += participant.support_received

            # Get collaborative modes used
            modes_used = list(
                {session.collaborative_mode.value for session in sessions}
            )

            # Get roles played
            roles_played = list(
                {
                    session.participants[user_id].role.value
                    for session in sessions
                    if user_id in session.participants
                }
            )

            return {
                "user_id": user_id,
                "collaborative_summary": {
                    "sessions_joined": len(user_sessions),
                    "active_sessions": len(active_sessions),
                    "completed_sessions": len(completed_sessions),
                    "sessions_hosted": len(
                        [s for s in sessions if s.host_user_id == user_id]
                    ),
                },
                "participation_metrics": {
                    "total_choices_made": total_choices_made,
                    "total_messages_sent": total_messages_sent,
                    "total_support_given": total_support_given,
                    "total_support_received": total_support_received,
                    "support_ratio": total_support_given
                    / max(1, total_support_received),
                },
                "collaborative_experience": {
                    "modes_experienced": modes_used,
                    "roles_played": roles_played,
                    "preferred_mode": self._get_preferred_collaborative_mode(
                        sessions, user_id
                    ),
                    "collaboration_comfort_level": self._calculate_collaboration_comfort(
                        sessions, user_id
                    ),
                },
                "recent_sessions": [
                    {
                        "session_id": session.session_id,
                        "session_name": session.session_name,
                        "collaborative_mode": session.collaborative_mode.value,
                        "role": (
                            session.participants[user_id].role.value
                            if user_id in session.participants
                            else "unknown"
                        ),
                        "is_active": session.is_active,
                        "created_at": session.created_at.isoformat(),
                    }
                    for session in sorted(
                        sessions, key=lambda s: s.created_at, reverse=True
                    )[:5]
                ],
            }

        except Exception as e:
            logger.error(f"Failed to get collaborative summary for user {user_id}: {e}")
            return {"error": "Unable to generate collaborative summary"}

    def _get_preferred_collaborative_mode(
        self, sessions: list[CollaborativeSession], user_id: str
    ) -> str:
        """Get the user's preferred collaborative mode."""
        if not sessions:
            return "none"

        mode_counts = {}
        for session in sessions:
            if user_id in session.participants:
                mode = session.collaborative_mode.value
                mode_counts[mode] = mode_counts.get(mode, 0) + 1

        return (
            max(mode_counts.keys(), key=lambda k: mode_counts[k])
            if mode_counts
            else "cooperative"
        )

    def _calculate_collaboration_comfort(
        self, sessions: list[CollaborativeSession], user_id: str
    ) -> float:
        """Calculate user's comfort level with collaboration."""
        if not sessions:
            return 0.5

        comfort_scores = []
        for session in sessions:
            if user_id in session.participants:
                participant = session.participants[user_id]
                # Base comfort on participation metrics and session completion
                participation_score = min(
                    1.0, (participant.choices_made + participant.messages_sent) / 10
                )
                comfort_scores.append(participation_score)

        return sum(comfort_scores) / len(comfort_scores) if comfort_scores else 0.5

    def get_session_analytics(self, session_id: str) -> dict[str, Any]:
        """Get comprehensive analytics for a collaborative session."""
        try:
            session = self.collaborative_sessions.get(session_id)
            if not session:
                return {"error": "Session not found"}

            # Calculate session metrics
            total_participants = len(session.participants)
            active_participants = len(
                [p for p in session.participants.values() if p.is_active]
            )

            # Calculate engagement metrics
            total_choices = len(session.group_choices)
            total_messages = len(session.support_messages)
            total_support_given = sum(
                p.support_given for p in session.participants.values()
            )

            # Calculate therapeutic metrics
            therapeutic_goals = set()
            for participant in session.participants.values():
                therapeutic_goals.update(participant.therapeutic_goals)

            # Calculate group dynamics
            avg_comfort_level = sum(
                p.comfort_level for p in session.participants.values()
            ) / max(1, total_participants)
            support_ratio = total_support_given / max(1, total_participants)

            # Session duration
            duration_minutes = 0
            if session.started_at:
                end_time = session.ended_at or datetime.utcnow()
                duration_minutes = (end_time - session.started_at).total_seconds() / 60

            return {
                "session_id": session_id,
                "session_overview": {
                    "session_name": session.session_name,
                    "collaborative_mode": session.collaborative_mode.value,
                    "therapeutic_focus": session.therapeutic_focus,
                    "duration_minutes": duration_minutes,
                    "is_active": session.is_active,
                },
                "participation_metrics": {
                    "total_participants": total_participants,
                    "active_participants": active_participants,
                    "max_participants": session.max_participants,
                    "waiting_list_count": len(session.waiting_list),
                },
                "engagement_metrics": {
                    "total_group_choices": total_choices,
                    "total_support_messages": total_messages,
                    "total_support_given": total_support_given,
                    "avg_choices_per_participant": total_choices
                    / max(1, total_participants),
                    "avg_messages_per_participant": total_messages
                    / max(1, total_participants),
                },
                "therapeutic_metrics": {
                    "unique_therapeutic_goals": len(therapeutic_goals),
                    "avg_comfort_level": avg_comfort_level,
                    "support_ratio": support_ratio,
                    "therapeutic_interventions": len(
                        [
                            log
                            for log in session.moderation_log
                            if log.get("type") == "therapeutic_intervention"
                        ]
                    ),
                },
                "safety_metrics": {
                    "moderation_actions": len(session.moderation_log),
                    "conflicts_reported": len(
                        [
                            log
                            for log in session.moderation_log
                            if log.get("type") == "conflict_reported"
                        ]
                    ),
                    "safety_escalations": len(
                        [
                            log
                            for log in session.moderation_log
                            if "escalate" in log.get("type", "")
                        ]
                    ),
                },
                "participant_details": [
                    {
                        "user_id": participant.user_id,
                        "role": participant.role.value,
                        "choices_made": participant.choices_made,
                        "messages_sent": participant.messages_sent,
                        "support_given": participant.support_given,
                        "support_received": participant.support_received,
                        "comfort_level": participant.comfort_level,
                        "is_active": participant.is_active,
                    }
                    for participant in session.participants.values()
                ],
            }

        except Exception as e:
            logger.error(f"Failed to get session analytics for {session_id}: {e}")
            return {"error": "Unable to generate session analytics"}

    def get_metrics(self) -> dict[str, Any]:
        """Get collaborative system metrics."""
        return {
            **self.metrics,
            "total_collaborative_sessions": len(self.collaborative_sessions),
            "active_collaborative_sessions": len(
                [s for s in self.collaborative_sessions.values() if s.is_active]
            ),
            "total_group_choices": len(self.group_choices),
            "total_support_messages": len(self.support_messages),
            "total_conflict_resolutions": len(self.conflict_resolutions),
            "users_with_collaborative_experience": len(self.user_sessions),
            "avg_participants_per_session": sum(
                len(s.participants) for s in self.collaborative_sessions.values()
            )
            / max(1, len(self.collaborative_sessions)),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of collaborative system."""
        return {
            "status": "healthy",
            "moderation_rules_loaded": len(self.moderation_rules),
            "safety_keywords_loaded": sum(
                len(keywords) for keywords in self.safety_keywords.values()
            ),
            "therapeutic_triggers_loaded": len(self.therapeutic_triggers),
            "collaborative_sessions_stored": len(self.collaborative_sessions),
            "group_choices_stored": len(self.group_choices),
            "support_messages_stored": len(self.support_messages),
            "conflict_resolutions_stored": len(self.conflict_resolutions),
            "metrics": self.get_metrics(),
        }

    def _load_safety_keywords(self) -> dict[str, list[str]]:
        """Load safety keywords for content monitoring."""
        return {
            "crisis_indicators": [
                "hurt myself",
                "end it all",
                "can't go on",
                "no point",
                "give up",
                "suicide",
                "kill myself",
                "better off dead",
                "worthless",
                "hopeless",
            ],
            "inappropriate_content": [
                "explicit_content",
                "harassment_terms",
                "discriminatory_language",
            ],
            "therapeutic_boundaries": [
                "personal_information",
                "contact_details",
                "meeting_requests",
            ],
        }

    def _load_therapeutic_triggers(self) -> dict[str, dict[str, Any]]:
        """Load therapeutic intervention triggers."""
        return {
            "emotional_distress": {
                "indicators": ["overwhelmed", "can't cope", "breaking down", "panic"],
                "intervention": "emotional_support",
                "escalation_needed": False,
            },
            "crisis_situation": {
                "indicators": ["crisis_indicators"],  # References safety_keywords
                "intervention": "crisis_protocol",
                "escalation_needed": True,
            },
            "therapeutic_resistance": {
                "indicators": ["this is stupid", "waste of time", "doesn't work"],
                "intervention": "resistance_support",
                "escalation_needed": False,
            },
            "boundary_violation": {
                "indicators": ["therapeutic_boundaries"],  # References safety_keywords
                "intervention": "boundary_reinforcement",
                "escalation_needed": True,
            },
        }
