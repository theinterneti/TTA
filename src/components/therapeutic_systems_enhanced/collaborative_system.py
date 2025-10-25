"""
Production Therapeutic CollaborativeSystem Implementation

This module provides multi-user therapeutic experiences with peer support,
collaborative therapeutic goal achievement, and integration with all
therapeutic systems for comprehensive collaborative workflows.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class CollaborativeMode(Enum):
    """Modes of collaborative therapeutic experiences."""

    PEER_SUPPORT = "peer_support"  # Mutual support and encouragement
    GROUP_THERAPY = "group_therapy"  # Structured group therapy sessions
    MENTORSHIP = "mentorship"  # One-on-one mentoring relationships
    SHARED_EXPLORATION = "shared_exploration"  # Collaborative scenario exploration
    THERAPEUTIC_PARTNERSHIP = "therapeutic_partnership"  # Therapeutic buddy system
    CRISIS_SUPPORT = "crisis_support"  # Emergency peer support network


class ParticipantRole(Enum):
    """Roles within collaborative therapeutic sessions."""

    HOST = "host"  # Session creator and primary facilitator
    FACILITATOR = "facilitator"  # Professional or trained facilitator
    MENTOR = "mentor"  # Experienced peer providing guidance
    PARTICIPANT = "participant"  # Active session participant
    OBSERVER = "observer"  # Passive observer (learning mode)
    SUPPORT_BUDDY = "support_buddy"  # Designated support partner


class SessionStatus(Enum):
    """Status of collaborative therapeutic sessions."""

    INITIALIZING = "initializing"
    WAITING_FOR_PARTICIPANTS = "waiting_for_participants"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EMERGENCY_INTERVENTION = "emergency_intervention"


class SupportType(Enum):
    """Types of peer support interactions."""

    ENCOURAGEMENT = "encouragement"
    SHARED_EXPERIENCE = "shared_experience"
    PRACTICAL_ADVICE = "practical_advice"
    EMOTIONAL_VALIDATION = "emotional_validation"
    CRISIS_SUPPORT = "crisis_support"
    CELEBRATION = "celebration"
    ACCOUNTABILITY = "accountability"
    RESOURCE_SHARING = "resource_sharing"


@dataclass
class CollaborativeParticipant:
    """Represents a participant in a collaborative therapeutic session."""

    user_id: str
    username: str
    role: ParticipantRole

    # Therapeutic context
    therapeutic_goals: list[str] = field(default_factory=list)
    character_id: str | None = None
    current_emotional_state: dict[str, Any] = field(default_factory=dict)

    # Participation tracking
    joined_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    contributions_count: int = 0
    support_given: int = 0
    support_received: int = 0

    # Preferences and settings
    privacy_level: str = "standard"  # minimal, standard, open
    support_preferences: list[SupportType] = field(default_factory=list)
    crisis_contact_enabled: bool = True

    # Session progress
    therapeutic_progress: dict[str, float] = field(default_factory=dict)
    milestones_achieved: list[str] = field(default_factory=list)
    session_satisfaction: float | None = None  # 0.0 to 1.0


@dataclass
class SupportInteraction:
    """Represents a peer support interaction."""

    interaction_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""

    # Participants
    supporter_id: str = ""
    recipient_id: str = ""

    # Interaction details
    support_type: SupportType = SupportType.ENCOURAGEMENT
    message: str = ""
    therapeutic_context: dict[str, Any] = field(default_factory=dict)

    # Impact tracking
    therapeutic_value: float = 0.0
    emotional_impact: dict[str, float] = field(default_factory=dict)
    recipient_feedback: str | None = None
    effectiveness_score: float | None = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_crisis_related: bool = False


@dataclass
class CollaborativeGoal:
    """Represents a shared therapeutic goal."""

    goal_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""

    # Goal definition
    goal_name: str = ""
    goal_description: str = ""
    therapeutic_framework: str | None = None

    # Participants
    primary_participants: list[str] = field(default_factory=list)  # user_ids
    supporting_participants: list[str] = field(default_factory=list)  # user_ids

    # Progress tracking
    target_milestones: list[str] = field(default_factory=list)
    achieved_milestones: list[str] = field(default_factory=list)
    progress_percentage: float = 0.0

    # Collaborative elements
    shared_activities: list[str] = field(default_factory=list)
    peer_accountability: bool = True
    celebration_triggers: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    target_completion: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class CollaborativeSession:
    """Manages a collaborative therapeutic session."""

    session_id: str = field(default_factory=lambda: str(uuid4()))
    host_user_id: str = ""

    # Session configuration
    session_name: str = ""
    session_description: str = ""
    collaborative_mode: CollaborativeMode = CollaborativeMode.PEER_SUPPORT
    max_participants: int = 6

    # Therapeutic configuration
    therapeutic_focus: list[str] = field(default_factory=list)
    therapeutic_frameworks: list[str] = field(default_factory=list)
    requires_facilitator: bool = False
    safety_level: str = "standard"  # standard, high, maximum

    # Participants and roles
    participants: dict[str, CollaborativeParticipant] = field(default_factory=dict)
    waiting_list: list[str] = field(default_factory=list)
    facilitator_id: str | None = None

    # Session state
    status: SessionStatus = SessionStatus.INITIALIZING
    started_at: datetime | None = None
    ended_at: datetime | None = None
    current_activity: str | None = None

    # Collaborative elements
    shared_goals: list[str] = field(default_factory=list)  # goal_ids
    support_interactions: list[str] = field(default_factory=list)  # interaction_ids
    group_achievements: list[str] = field(default_factory=list)

    # Session tracking
    total_therapeutic_value: float = 0.0
    participant_satisfaction: dict[str, float] = field(default_factory=dict)
    crisis_interventions: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)


class TherapeuticCollaborativeSystem:
    """
    Production CollaborativeSystem that provides multi-user therapeutic experiences
    with peer support, collaborative goal achievement, and comprehensive integration
    with all therapeutic systems.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the therapeutic collaborative system."""
        self.config = config or {}

        # Collaborative session storage
        self.collaborative_sessions = {}  # session_id -> CollaborativeSession
        self.collaborative_participants = {}  # user_id -> List[CollaborativeParticipant]
        self.support_interactions = {}  # interaction_id -> SupportInteraction
        self.collaborative_goals = {}  # goal_id -> CollaborativeGoal

        # User tracking and relationships
        self.user_sessions = {}  # user_id -> List[session_id]
        self.peer_connections = {}  # user_id -> Set[user_id] (mutual connections)
        self.support_networks = {}  # user_id -> Dict[user_id, relationship_strength]

        # Therapeutic system references (will be injected)
        self.consequence_system = None
        self.emotional_safety_system = None
        self.adaptive_difficulty_engine = None
        self.character_development_system = None
        self.therapeutic_integration_system = None
        self.gameplay_loop_controller = None
        self.replayability_system = None

        # Configuration parameters
        self.max_concurrent_sessions = self.config.get("max_concurrent_sessions", 50)
        self.max_participants_per_session = self.config.get(
            "max_participants_per_session", 8
        )
        self.session_timeout_minutes = self.config.get("session_timeout_minutes", 180)
        self.crisis_response_enabled = self.config.get("crisis_response_enabled", True)
        self.peer_matching_enabled = self.config.get("peer_matching_enabled", True)

        # Performance metrics
        self.metrics = {
            "sessions_created": 0,
            "participants_connected": 0,
            "support_interactions": 0,
            "collaborative_goals_achieved": 0,
            "crisis_interventions": 0,
            "peer_connections_formed": 0,
        }

        logger.info("TherapeuticCollaborativeSystem initialized")

    async def initialize(self):
        """Initialize the collaborative system."""
        # Any async initialization can go here
        logger.info("TherapeuticCollaborativeSystem initialization complete")

    def inject_therapeutic_systems(
        self,
        consequence_system=None,
        emotional_safety_system=None,
        adaptive_difficulty_engine=None,
        character_development_system=None,
        therapeutic_integration_system=None,
        gameplay_loop_controller=None,
        replayability_system=None,
    ):
        """Inject therapeutic system dependencies."""
        self.consequence_system = consequence_system
        self.emotional_safety_system = emotional_safety_system
        self.adaptive_difficulty_engine = adaptive_difficulty_engine
        self.character_development_system = character_development_system
        self.therapeutic_integration_system = therapeutic_integration_system
        self.gameplay_loop_controller = gameplay_loop_controller
        self.replayability_system = replayability_system

        logger.info("Therapeutic systems injected into CollaborativeSystem")

    async def create_collaborative_session(
        self,
        host_user_id: str,
        session_name: str,
        collaborative_mode: CollaborativeMode = CollaborativeMode.PEER_SUPPORT,
        therapeutic_focus: list[str] | None = None,
        max_participants: int = 6,
        requires_facilitator: bool = False,
    ) -> CollaborativeSession:
        """
        Create a new collaborative therapeutic session.

        This method provides the core interface for creating multi-user therapeutic
        experiences with peer support and collaborative goal achievement.

        Args:
            host_user_id: User creating the session
            session_name: Name for the collaborative session
            collaborative_mode: Type of collaborative experience
            therapeutic_focus: List of therapeutic areas to focus on
            max_participants: Maximum number of participants
            requires_facilitator: Whether a facilitator is required

        Returns:
            CollaborativeSession representing the created session
        """
        try:
            start_time = datetime.utcnow()

            # Check session limits
            if len(self.collaborative_sessions) >= self.max_concurrent_sessions:
                raise RuntimeError("Maximum concurrent collaborative sessions reached")

            # Create collaborative session
            session = CollaborativeSession(
                host_user_id=host_user_id,
                session_name=session_name,
                session_description=f"Collaborative {collaborative_mode.value.replace('_', ' ').title()} session focusing on {', '.join(therapeutic_focus or ['general wellness'])}",
                collaborative_mode=collaborative_mode,
                max_participants=min(
                    max_participants, self.max_participants_per_session
                ),
                therapeutic_focus=therapeutic_focus or ["general_wellness"],
                requires_facilitator=requires_facilitator,
            )

            # Configure session based on mode (but preserve explicit max_participants)
            original_max_participants = session.max_participants
            await self._configure_session_by_mode(session, collaborative_mode)

            # Restore explicit max_participants if it was set
            if max_participants != 6:  # 6 is the default
                session.max_participants = original_max_participants

            # Create host participant
            host_participant = CollaborativeParticipant(
                user_id=host_user_id,
                username=f"Host_{host_user_id[:8]}",  # Would be replaced with actual username
                role=ParticipantRole.HOST,
                therapeutic_goals=therapeutic_focus or [],
                support_preferences=[
                    SupportType.ENCOURAGEMENT,
                    SupportType.SHARED_EXPERIENCE,
                ],
            )

            # Add host to session
            session.participants[host_user_id] = host_participant

            # Initialize therapeutic context
            await self._initialize_therapeutic_context(session)

            # Store session
            self.collaborative_sessions[session.session_id] = session

            # Track user sessions
            if host_user_id not in self.user_sessions:
                self.user_sessions[host_user_id] = []
            self.user_sessions[host_user_id].append(session.session_id)

            # Update session status
            session.status = SessionStatus.WAITING_FOR_PARTICIPANTS
            session.last_activity = datetime.utcnow()

            # Update metrics
            self.metrics["sessions_created"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Created collaborative session {session.session_id} for host {host_user_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return session

        except Exception as e:
            logger.error(
                f"Error creating collaborative session for host {host_user_id}: {e}"
            )

            # Return error session
            return CollaborativeSession(
                host_user_id=host_user_id,
                session_name=f"Error Session: {str(e)}",
                status=SessionStatus.CANCELLED,
            )

    async def join_collaborative_session(
        self,
        session_id: str,
        user_id: str,
        role: ParticipantRole = ParticipantRole.PARTICIPANT,
        therapeutic_goals: list[str] | None = None,
    ) -> CollaborativeParticipant:
        """
        Join an existing collaborative therapeutic session.

        Args:
            session_id: Session to join
            user_id: User joining the session
            role: Role in the collaborative session
            therapeutic_goals: User's therapeutic goals for the session

        Returns:
            CollaborativeParticipant representing the joined participant
        """
        try:
            start_time = datetime.utcnow()

            # Get session
            session = self.collaborative_sessions.get(session_id)
            if not session:
                raise ValueError(f"Collaborative session {session_id} not found")

            # Check session status
            if session.status not in [
                SessionStatus.WAITING_FOR_PARTICIPANTS,
                SessionStatus.ACTIVE,
            ]:
                raise ValueError(
                    f"Session {session_id} is not accepting participants (status: {session.status.value})"
                )

            # Check if user is already in session
            if user_id in session.participants:
                return session.participants[user_id]

            # Check participant limits
            if len(session.participants) >= session.max_participants:
                # Add to waiting list
                if user_id not in session.waiting_list:
                    session.waiting_list.append(user_id)

                # Return error participant instead of raising exception
                return CollaborativeParticipant(
                    user_id=user_id,
                    username=f"Error_{user_id[:8]}",
                    role=role,
                    therapeutic_goals=therapeutic_goals or [],
                )

            # Check facilitator requirements
            if session.requires_facilitator and role == ParticipantRole.FACILITATOR:
                if session.facilitator_id is None:
                    session.facilitator_id = user_id
                else:
                    role = (
                        ParticipantRole.PARTICIPANT
                    )  # Downgrade if facilitator already exists

            # Create participant
            participant = CollaborativeParticipant(
                user_id=user_id,
                username=f"User_{user_id[:8]}",  # Would be replaced with actual username
                role=role,
                therapeutic_goals=therapeutic_goals or [],
                support_preferences=await self._determine_support_preferences(user_id),
            )

            # Initialize participant therapeutic context
            await self._initialize_participant_context(participant, session)

            # Add participant to session
            session.participants[user_id] = participant
            session.last_activity = datetime.utcnow()

            # Track user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)

            # Start session if minimum participants reached
            if (
                session.status == SessionStatus.WAITING_FOR_PARTICIPANTS
                and len(session.participants) >= 2
            ):
                await self._start_collaborative_session(session)

            # Update metrics
            self.metrics["participants_connected"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"User {user_id} joined collaborative session {session_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return participant

        except Exception as e:
            logger.error(
                f"Error joining collaborative session {session_id} for user {user_id}: {e}"
            )

            # Return error participant
            return CollaborativeParticipant(
                user_id=user_id,
                username=f"Error_{user_id[:8]}",
                role=role,
                therapeutic_goals=therapeutic_goals or [],
            )

    async def provide_peer_support(
        self,
        session_id: str,
        supporter_id: str,
        recipient_id: str,
        support_type: SupportType,
        message: str,
        therapeutic_context: dict[str, Any] | None = None,
    ) -> SupportInteraction:
        """
        Provide peer support within a collaborative session.

        Args:
            session_id: Session where support is being provided
            supporter_id: User providing support
            recipient_id: User receiving support
            support_type: Type of support being provided
            message: Support message or content
            therapeutic_context: Additional therapeutic context

        Returns:
            SupportInteraction representing the support provided
        """
        try:
            start_time = datetime.utcnow()

            # Get session and validate participants
            session = self.collaborative_sessions.get(session_id)
            if not session:
                raise ValueError(f"Collaborative session {session_id} not found")

            if (
                supporter_id not in session.participants
                or recipient_id not in session.participants
            ):
                raise ValueError(
                    "Both supporter and recipient must be session participants"
                )

            # Check for crisis support
            is_crisis_related = support_type == SupportType.CRISIS_SUPPORT
            if is_crisis_related and self.crisis_response_enabled:
                await self._handle_crisis_support(
                    session, supporter_id, recipient_id, message
                )

            # Create support interaction
            interaction = SupportInteraction(
                session_id=session_id,
                supporter_id=supporter_id,
                recipient_id=recipient_id,
                support_type=support_type,
                message=message,
                therapeutic_context=therapeutic_context or {},
                is_crisis_related=is_crisis_related,
            )

            # Calculate therapeutic value using integrated systems
            if self.consequence_system:
                try:
                    consequence_result = (
                        await self.consequence_system.process_choice_consequence(
                            user_id=supporter_id,
                            choice=f"provide_{support_type.value}_support",
                            scenario_context={
                                "collaborative_session": True,
                                "support_interaction": True,
                            },
                        )
                    )
                    interaction.therapeutic_value = consequence_result.get(
                        "therapeutic_value", 1.0
                    )
                except Exception as e:
                    logger.debug(f"Error calculating therapeutic value: {e}")
                    interaction.therapeutic_value = 1.0

            # Update participant tracking
            supporter = session.participants[supporter_id]
            recipient = session.participants[recipient_id]

            supporter.support_given += 1
            supporter.contributions_count += 1
            supporter.last_activity = datetime.utcnow()

            recipient.support_received += 1
            recipient.last_activity = datetime.utcnow()

            # Store interaction
            self.support_interactions[interaction.interaction_id] = interaction
            session.support_interactions.append(interaction.interaction_id)
            session.total_therapeutic_value += interaction.therapeutic_value
            session.last_activity = datetime.utcnow()

            # Update peer connections
            await self._strengthen_peer_connection(supporter_id, recipient_id)

            # Update metrics
            self.metrics["support_interactions"] += 1
            if is_crisis_related:
                self.metrics["crisis_interventions"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Peer support provided in session {session_id} "
                f"({support_type.value}) in {processing_time.total_seconds():.3f}s"
            )

            return interaction

        except Exception as e:
            logger.error(f"Error providing peer support in session {session_id}: {e}")

            # Return minimal interaction
            return SupportInteraction(
                session_id=session_id,
                supporter_id=supporter_id,
                recipient_id=recipient_id,
                support_type=support_type,
                message=f"Error providing support: {str(e)}",
            )

    async def create_collaborative_goal(
        self,
        session_id: str,
        goal_name: str,
        goal_description: str,
        primary_participants: list[str],
        therapeutic_framework: str | None = None,
        target_completion: datetime | None = None,
    ) -> CollaborativeGoal:
        """
        Create a shared therapeutic goal for collaborative achievement.

        Args:
            session_id: Session for the collaborative goal
            goal_name: Name of the shared goal
            goal_description: Description of what the goal entails
            primary_participants: Users primarily responsible for the goal
            therapeutic_framework: Therapeutic framework to use
            target_completion: Target completion date

        Returns:
            CollaborativeGoal representing the shared goal
        """
        try:
            start_time = datetime.utcnow()

            # Get session
            session = self.collaborative_sessions.get(session_id)
            if not session:
                raise ValueError(f"Collaborative session {session_id} not found")

            # Validate participants
            for participant_id in primary_participants:
                if participant_id not in session.participants:
                    raise ValueError(f"Participant {participant_id} not in session")

            # Create collaborative goal
            goal = CollaborativeGoal(
                session_id=session_id,
                goal_name=goal_name,
                goal_description=goal_description,
                therapeutic_framework=therapeutic_framework,
                primary_participants=primary_participants,
                supporting_participants=[
                    p_id
                    for p_id in session.participants
                    if p_id not in primary_participants
                ],
                target_completion=target_completion,
            )

            # Generate therapeutic milestones using integration system
            if self.therapeutic_integration_system:
                try:
                    recommendations = await self.therapeutic_integration_system.generate_personalized_recommendations(
                        user_id=primary_participants[
                            0
                        ],  # Use first participant as reference
                        therapeutic_goals=[goal_name],
                        character_data={"collaborative_context": True},
                    )

                    if recommendations:
                        # Use the first recommendation for milestone generation
                        first_rec = recommendations[0]
                        goal.target_milestones = [
                            f"Complete {first_rec.framework.value} exercise",
                            f"Practice {first_rec.integration_strategy.value}",
                            "Achieve therapeutic breakthrough",
                        ]
                except Exception as e:
                    logger.debug(f"Error generating goal milestones: {e}")

            # Set default milestones if none generated
            if not goal.target_milestones:
                goal.target_milestones = [
                    "Initial goal commitment",
                    "Progress checkpoint",
                    "Goal achievement celebration",
                ]

            # Store goal
            self.collaborative_goals[goal.goal_id] = goal
            session.shared_goals.append(goal.goal_id)
            session.last_activity = datetime.utcnow()

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Created collaborative goal {goal.goal_id} for session {session_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return goal

        except Exception as e:
            logger.error(
                f"Error creating collaborative goal for session {session_id}: {e}"
            )

            # Return minimal goal
            return CollaborativeGoal(
                session_id=session_id,
                goal_name=f"Error Goal: {str(e)}",
                goal_description="Goal creation failed",
                primary_participants=primary_participants,
            )

    # Helper methods for therapeutic system integration

    async def _configure_session_by_mode(
        self, session: CollaborativeSession, mode: CollaborativeMode
    ):
        """Configure session settings based on collaborative mode."""
        try:
            if mode == CollaborativeMode.GROUP_THERAPY:
                session.requires_facilitator = True
                session.safety_level = "high"
                session.max_participants = 8
                session.therapeutic_frameworks = ["group_therapy", "cbt", "dbt"]
            elif mode == CollaborativeMode.MENTORSHIP:
                session.max_participants = 2
                session.safety_level = "standard"
                session.therapeutic_frameworks = ["humanistic", "solution_focused"]
            elif mode == CollaborativeMode.CRISIS_SUPPORT:
                session.safety_level = "maximum"
                session.requires_facilitator = True
                session.max_participants = 4
                session.therapeutic_frameworks = ["crisis_intervention", "dbt"]
            elif mode == CollaborativeMode.PEER_SUPPORT:
                session.safety_level = "standard"
                session.max_participants = 6
                session.therapeutic_frameworks = ["peer_support", "mutual_aid"]
            elif mode == CollaborativeMode.SHARED_EXPLORATION:
                session.safety_level = "standard"
                session.max_participants = 4
                session.therapeutic_frameworks = ["experiential", "narrative"]
            elif mode == CollaborativeMode.THERAPEUTIC_PARTNERSHIP:
                session.max_participants = 2
                session.safety_level = "standard"
                session.therapeutic_frameworks = ["partnership", "accountability"]

        except Exception as e:
            logger.error(f"Error configuring session by mode: {e}")

    async def _initialize_therapeutic_context(self, session: CollaborativeSession):
        """Initialize therapeutic context for the session."""
        try:
            # Set up therapeutic framework integration
            if self.therapeutic_integration_system and session.therapeutic_focus:
                recommendations = await self.therapeutic_integration_system.generate_personalized_recommendations(
                    user_id=session.host_user_id,
                    therapeutic_goals=session.therapeutic_focus,
                    character_data={"collaborative_session": True},
                )

                if recommendations:
                    session.therapeutic_frameworks.extend(
                        [rec.framework.value for rec in recommendations[:3]]
                    )

            # Initialize safety monitoring
            if self.emotional_safety_system:
                await self.emotional_safety_system.initialize_user_monitoring(
                    user_id=session.host_user_id,
                    session_id=session.session_id,
                    monitoring_level="collaborative",
                )

        except Exception as e:
            logger.error(f"Error initializing therapeutic context: {e}")

    async def _initialize_participant_context(
        self, participant: CollaborativeParticipant, session: CollaborativeSession
    ):
        """Initialize therapeutic context for a new participant."""
        try:
            # Initialize character development if available
            if self.character_development_system and participant.therapeutic_goals:
                character = await self.character_development_system.create_character(
                    user_id=participant.user_id,
                    session_id=session.session_id,
                    therapeutic_goals=participant.therapeutic_goals,
                    character_preferences={"collaborative": True},
                )
                participant.character_id = character.character_id

            # Initialize safety monitoring
            if self.emotional_safety_system:
                await self.emotional_safety_system.initialize_user_monitoring(
                    user_id=participant.user_id,
                    session_id=session.session_id,
                    monitoring_level="collaborative",
                )

        except Exception as e:
            logger.error(f"Error initializing participant context: {e}")

    async def _determine_support_preferences(self, user_id: str) -> list[SupportType]:
        """Determine support preferences for a user."""
        try:
            # Default support preferences
            return [
                SupportType.ENCOURAGEMENT,
                SupportType.SHARED_EXPERIENCE,
                SupportType.EMOTIONAL_VALIDATION,
            ]

            # Could be enhanced with user preference learning

        except Exception as e:
            logger.error(f"Error determining support preferences: {e}")
            return [SupportType.ENCOURAGEMENT]

    async def _start_collaborative_session(self, session: CollaborativeSession):
        """Start an active collaborative session."""
        try:
            session.status = SessionStatus.ACTIVE
            session.started_at = datetime.utcnow()
            session.current_activity = "collaborative_introduction"

            # Initialize group therapeutic context
            await self._initialize_group_therapeutic_context(session)

            logger.info(
                f"Started collaborative session {session.session_id} with {len(session.participants)} participants"
            )

        except Exception as e:
            logger.error(f"Error starting collaborative session: {e}")

    async def _initialize_group_therapeutic_context(
        self, session: CollaborativeSession
    ):
        """Initialize therapeutic context for group dynamics."""
        try:
            # Aggregate therapeutic goals from all participants
            all_goals = set()
            for participant in session.participants.values():
                all_goals.update(participant.therapeutic_goals)

            # Update session therapeutic focus with participant goals
            session.therapeutic_focus.extend(list(all_goals))
            session.therapeutic_focus = list(
                set(session.therapeutic_focus)
            )  # Remove duplicates

        except Exception as e:
            logger.error(f"Error initializing group therapeutic context: {e}")

    async def _handle_crisis_support(
        self,
        session: CollaborativeSession,
        supporter_id: str,
        recipient_id: str,
        message: str,
    ):
        """Handle crisis support situation."""
        try:
            # Escalate to emotional safety system
            if self.emotional_safety_system:
                crisis_assessment = (
                    await self.emotional_safety_system.assess_crisis_risk(
                        user_id=recipient_id,
                        user_input=message,
                        session_context={
                            "collaborative_session": True,
                            "peer_support": True,
                        },
                    )
                )

                if crisis_assessment.get("crisis_detected", False):
                    session.status = SessionStatus.EMERGENCY_INTERVENTION
                    session.crisis_interventions += 1

        except Exception as e:
            logger.error(f"Error handling crisis support: {e}")

    async def _strengthen_peer_connection(self, user1_id: str, user2_id: str):
        """Strengthen peer connection between two users."""
        try:
            # Initialize peer connections if needed
            if user1_id not in self.peer_connections:
                self.peer_connections[user1_id] = set()
            if user2_id not in self.peer_connections:
                self.peer_connections[user2_id] = set()

            # Add mutual connections
            if user2_id not in self.peer_connections[user1_id]:
                self.peer_connections[user1_id].add(user2_id)
                self.peer_connections[user2_id].add(user1_id)
                self.metrics["peer_connections_formed"] += 1

            # Update support network strength
            if user1_id not in self.support_networks:
                self.support_networks[user1_id] = {}
            if user2_id not in self.support_networks:
                self.support_networks[user2_id] = {}

            # Increase relationship strength
            current_strength = self.support_networks[user1_id].get(user2_id, 0.0)
            self.support_networks[user1_id][user2_id] = min(1.0, current_strength + 0.1)
            self.support_networks[user2_id][user1_id] = min(1.0, current_strength + 0.1)

        except Exception as e:
            logger.error(f"Error strengthening peer connection: {e}")

    async def get_session_status(self, session_id: str) -> dict[str, Any] | None:
        """Get current status of a collaborative session."""
        try:
            session = self.collaborative_sessions.get(session_id)
            if not session:
                return None

            return {
                "session_id": session_id,
                "host_user_id": session.host_user_id,
                "session_name": session.session_name,
                "collaborative_mode": session.collaborative_mode.value,
                "status": session.status.value,
                "participants": len(session.participants),
                "max_participants": session.max_participants,
                "therapeutic_focus": session.therapeutic_focus,
                "total_therapeutic_value": session.total_therapeutic_value,
                "support_interactions": len(session.support_interactions),
                "shared_goals": len(session.shared_goals),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return None

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the collaborative system."""
        try:
            # Check therapeutic system availability
            systems_status = {
                "consequence_system": self.consequence_system is not None,
                "emotional_safety_system": self.emotional_safety_system is not None,
                "adaptive_difficulty_engine": self.adaptive_difficulty_engine
                is not None,
                "character_development_system": self.character_development_system
                is not None,
                "therapeutic_integration_system": self.therapeutic_integration_system
                is not None,
                "gameplay_loop_controller": self.gameplay_loop_controller is not None,
                "replayability_system": self.replayability_system is not None,
            }

            systems_available = sum(systems_status.values())

            return {
                "status": "healthy" if systems_available >= 4 else "degraded",
                "collaborative_modes": len(CollaborativeMode),
                "participant_roles": len(ParticipantRole),
                "support_types": len(SupportType),
                "active_sessions": len(
                    [
                        s
                        for s in self.collaborative_sessions.values()
                        if s.status == SessionStatus.ACTIVE
                    ]
                ),
                "total_sessions": len(self.collaborative_sessions),
                "total_participants": sum(
                    len(s.participants) for s in self.collaborative_sessions.values()
                ),
                "support_interactions": len(self.support_interactions),
                "collaborative_goals": len(self.collaborative_goals),
                "peer_connections": sum(
                    len(connections) for connections in self.peer_connections.values()
                )
                // 2,
                "therapeutic_systems": systems_status,
                "systems_available": f"{systems_available}/7",
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            logger.error(f"Error in collaborative system health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_metrics(self) -> dict[str, Any]:
        """Get collaborative system metrics."""
        # Calculate additional metrics
        active_sessions = len(
            [
                s
                for s in self.collaborative_sessions.values()
                if s.status == SessionStatus.ACTIVE
            ]
        )
        total_participants = sum(
            len(s.participants) for s in self.collaborative_sessions.values()
        )

        average_session_size = 0.0
        if len(self.collaborative_sessions) > 0:
            average_session_size = total_participants / len(self.collaborative_sessions)

        return {
            **self.metrics,
            "active_sessions": active_sessions,
            "total_sessions": len(self.collaborative_sessions),
            "total_participants": total_participants,
            "average_session_size": round(average_session_size, 1),
            "support_interactions_total": len(self.support_interactions),
            "collaborative_goals_total": len(self.collaborative_goals),
            "peer_connections_total": sum(
                len(connections) for connections in self.peer_connections.values()
            )
            // 2,
            "users_with_connections": len(self.peer_connections),
        }
