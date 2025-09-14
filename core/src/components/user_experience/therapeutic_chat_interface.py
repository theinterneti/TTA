"""
Therapeutic Chat Interface System.

Comprehensive chat interface system providing real-time therapeutic interactions
with integration to all therapeutic systems, accessibility features, and
clinical-grade performance for the TTA therapeutic platform.
"""

import asyncio
import logging
import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of chat messages."""
    USER_MESSAGE = "user_message"
    THERAPEUTIC_RESPONSE = "therapeutic_response"
    SYSTEM_MESSAGE = "system_message"
    CRISIS_INTERVENTION = "crisis_intervention"
    ACHIEVEMENT_NOTIFICATION = "achievement_notification"
    PROGRESS_UPDATE = "progress_update"
    THERAPEUTIC_SUGGESTION = "therapeutic_suggestion"
    SESSION_SUMMARY = "session_summary"


class ConversationState(Enum):
    """States of therapeutic conversation."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    THERAPEUTIC_FOCUS = "therapeutic_focus"
    CRISIS_INTERVENTION = "crisis_intervention"
    SKILL_PRACTICE = "skill_practice"
    REFLECTION = "reflection"
    GOAL_SETTING = "goal_setting"
    SESSION_CLOSING = "session_closing"
    PAUSED = "paused"
    COMPLETED = "completed"


class TherapeuticFramework(Enum):
    """Therapeutic frameworks for response generation."""
    CBT = "cognitive_behavioral_therapy"
    DBT = "dialectical_behavior_therapy"
    ACT = "acceptance_commitment_therapy"
    MINDFULNESS = "mindfulness_based"
    HUMANISTIC = "humanistic_therapy"
    PSYCHODYNAMIC = "psychodynamic_therapy"
    SOLUTION_FOCUSED = "solution_focused_therapy"
    NARRATIVE = "narrative_therapy"


class ResponsePriority(Enum):
    """Priority levels for therapeutic responses."""
    CRISIS = "crisis"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class ChatMessage:
    """Individual chat message with therapeutic context."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    user_id: str = ""

    # Message content
    message_type: MessageType = MessageType.USER_MESSAGE
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Therapeutic context
    therapeutic_context: dict[str, Any] = field(default_factory=dict)
    emotional_indicators: dict[str, float] = field(default_factory=dict)
    crisis_risk_level: float = 0.0
    therapeutic_goals: list[str] = field(default_factory=list)

    # Processing metadata
    processing_time_ms: float = 0.0
    confidence_score: float = 0.0
    therapeutic_frameworks: list[TherapeuticFramework] = field(default_factory=list)

    # Response metadata
    response_priority: ResponsePriority = ResponsePriority.NORMAL
    requires_human_review: bool = False
    automated_response: bool = True


@dataclass
class ChatSession:
    """Therapeutic chat session with context and flow control."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""

    # Session metadata
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    session_duration: timedelta = field(default_factory=timedelta)

    # Conversation state
    conversation_state: ConversationState = ConversationState.INITIALIZING
    current_therapeutic_focus: str | None = None
    active_therapeutic_frameworks: list[TherapeuticFramework] = field(default_factory=list)

    # Therapeutic context
    session_goals: list[str] = field(default_factory=list)
    therapeutic_progress: dict[str, float] = field(default_factory=dict)
    emotional_journey: list[dict[str, Any]] = field(default_factory=list)

    # Message history
    messages: list[ChatMessage] = field(default_factory=list)
    message_count: int = 0

    # Session analytics
    engagement_metrics: dict[str, Any] = field(default_factory=dict)
    therapeutic_outcomes: dict[str, Any] = field(default_factory=dict)

    # Session configuration
    max_duration_minutes: int = 60
    auto_save_interval: int = 300  # 5 minutes
    is_active: bool = True


@dataclass
class TherapeuticContext:
    """Comprehensive therapeutic context for chat interactions."""
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""

    # User therapeutic profile
    therapeutic_goals: list[str] = field(default_factory=list)
    current_challenges: list[str] = field(default_factory=list)
    therapeutic_preferences: dict[str, Any] = field(default_factory=dict)

    # Current therapeutic state
    emotional_state: dict[str, float] = field(default_factory=dict)
    stress_level: float = 0.0
    engagement_level: float = 0.5
    crisis_risk_assessment: dict[str, Any] = field(default_factory=dict)

    # Therapeutic history
    previous_sessions: list[str] = field(default_factory=list)
    therapeutic_progress: dict[str, float] = field(default_factory=dict)
    successful_interventions: list[str] = field(default_factory=list)
    emotional_journey: list[dict[str, Any]] = field(default_factory=list)

    # Contextual factors
    time_of_day: str = ""
    session_context: dict[str, Any] = field(default_factory=dict)
    environmental_factors: dict[str, Any] = field(default_factory=dict)

    # Personalization data
    communication_style: str = "supportive"
    preferred_therapeutic_approaches: list[TherapeuticFramework] = field(default_factory=list)
    response_preferences: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationFlow:
    """Therapeutic conversation flow control and guidance."""
    flow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""

    # Flow configuration
    therapeutic_objectives: list[str] = field(default_factory=list)
    conversation_stages: list[dict[str, Any]] = field(default_factory=list)
    current_stage: int = 0

    # Flow control
    stage_transitions: dict[str, Any] = field(default_factory=dict)
    intervention_triggers: dict[str, Any] = field(default_factory=dict)
    flow_adaptations: list[dict[str, Any]] = field(default_factory=list)

    # Progress tracking
    stage_completion: dict[int, bool] = field(default_factory=dict)
    therapeutic_milestones: list[dict[str, Any]] = field(default_factory=list)

    # Timing and pacing
    stage_durations: dict[int, timedelta] = field(default_factory=dict)
    optimal_pacing: dict[str, Any] = field(default_factory=dict)

    # Adaptation metadata
    flow_effectiveness: float = 0.0
    user_engagement_per_stage: dict[int, float] = field(default_factory=dict)
    adaptation_history: list[dict[str, Any]] = field(default_factory=list)


class TherapeuticChatInterface:
    """
    Comprehensive therapeutic chat interface system.

    Provides real-time therapeutic interactions with integration to all therapeutic
    systems, accessibility features, and clinical-grade performance.
    """

    def __init__(self):
        """Initialize the Therapeutic Chat Interface System."""
        self.status = "initializing"

        # Core chat components
        self.active_sessions: dict[str, ChatSession] = {}
        self.therapeutic_contexts: dict[str, TherapeuticContext] = {}
        self.conversation_flows: dict[str, ConversationFlow] = {}
        self.message_history: dict[str, list[ChatMessage]] = defaultdict(list)

        # Message processing
        self.message_processors: dict[MessageType, Callable] = {}
        self.response_generators: dict[TherapeuticFramework, Callable] = {}
        self.intervention_handlers: dict[str, Callable] = {}

        # System integrations (injected)
        self.accessibility_system = None
        self.ui_engine = None
        self.engagement_system = None
        self.personalization_engine = None
        self.therapeutic_systems = {}
        self.clinical_dashboard_manager = None
        self.cloud_deployment_manager = None

        # Real-time messaging
        self.websocket_connections: dict[str, Any] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.broadcast_channels: dict[str, set[str]] = defaultdict(set)

        # Background tasks
        self._message_processing_task = None
        self._session_management_task = None
        self._therapeutic_monitoring_task = None
        self._performance_monitoring_task = None
        self._shutdown_event = asyncio.Event()

        # Performance metrics
        self.chat_system_metrics = {
            "total_active_sessions": 0,
            "total_messages_processed": 0,
            "average_response_time_ms": 0.0,
            "therapeutic_interventions": 0,
            "crisis_interventions": 0,
            "user_satisfaction_score": 0.0,
            "system_availability": 1.0,
            "concurrent_users": 0,
        }

        # Configuration
        self.config = {
            "max_concurrent_sessions": 1000,
            "message_processing_timeout": 5.0,
            "session_timeout_minutes": 30,
            "crisis_response_time_ms": 500,
            "therapeutic_response_time_ms": 1000,
            "auto_save_interval": 300,
            "max_message_length": 5000,
            "enable_real_time_messaging": True,
        }

    async def initialize(self):
        """Initialize the Therapeutic Chat Interface System."""
        try:
            logger.info("Initializing TherapeuticChatInterface")

            # Initialize core chat components
            await self._initialize_message_processors()
            await self._initialize_response_generators()
            await self._initialize_intervention_handlers()
            await self._initialize_conversation_flows()
            await self._initialize_therapeutic_templates()

            # Start background processing tasks
            self._message_processing_task = asyncio.create_task(
                self._message_processing_loop()
            )
            self._session_management_task = asyncio.create_task(
                self._session_management_loop()
            )
            self._therapeutic_monitoring_task = asyncio.create_task(
                self._therapeutic_monitoring_loop()
            )
            self._performance_monitoring_task = asyncio.create_task(
                self._performance_monitoring_loop()
            )

            self.status = "running"
            logger.info("TherapeuticChatInterface initialization complete")

        except Exception as e:
            logger.error(f"Error initializing TherapeuticChatInterface: {e}")
            self.status = "failed"
            raise

    def inject_accessibility_system(self, accessibility_system):
        """Inject accessibility system dependency."""
        self.accessibility_system = accessibility_system
        logger.info("Accessibility system injected into TherapeuticChatInterface")

    def inject_ui_engine(self, ui_engine):
        """Inject UI engine dependency."""
        self.ui_engine = ui_engine
        logger.info("UI engine injected into TherapeuticChatInterface")

    def inject_engagement_system(self, engagement_system):
        """Inject engagement system dependency."""
        self.engagement_system = engagement_system
        logger.info("Engagement system injected into TherapeuticChatInterface")

    def inject_personalization_engine(self, personalization_engine):
        """Inject personalization engine dependency."""
        self.personalization_engine = personalization_engine
        logger.info("Personalization engine injected into TherapeuticChatInterface")

    def inject_therapeutic_systems(self, **therapeutic_systems):
        """Inject therapeutic system dependencies."""
        self.therapeutic_systems = therapeutic_systems
        logger.info("Therapeutic systems injected into TherapeuticChatInterface")

    def inject_integration_systems(
        self,
        clinical_dashboard_manager=None,
        cloud_deployment_manager=None,
    ):
        """Inject integration system dependencies."""
        self.clinical_dashboard_manager = clinical_dashboard_manager
        self.cloud_deployment_manager = cloud_deployment_manager

        logger.info("Integration systems injected into TherapeuticChatInterface")

    async def start_chat_session(
        self,
        user_id: str,
        therapeutic_goals: list[str],
        session_config: dict[str, Any] | None = None
    ) -> ChatSession:
        """Start a new therapeutic chat session."""
        try:
            # Create new session
            session = ChatSession(
                user_id=user_id,
                session_goals=therapeutic_goals,
                max_duration_minutes=session_config.get("max_duration", 60) if session_config else 60
            )

            # Initialize therapeutic context
            therapeutic_context = await self._create_therapeutic_context(user_id, session.session_id)
            therapeutic_context.therapeutic_goals = therapeutic_goals

            # Create conversation flow
            conversation_flow = await self._create_conversation_flow(session.session_id, therapeutic_goals)

            # Store session data
            self.active_sessions[session.session_id] = session
            self.therapeutic_contexts[session.session_id] = therapeutic_context
            self.conversation_flows[session.session_id] = conversation_flow

            # Update metrics
            self.chat_system_metrics["total_active_sessions"] += 1
            self.chat_system_metrics["concurrent_users"] = len(self.active_sessions)

            # Send welcome message
            welcome_message = await self._generate_welcome_message(session, therapeutic_context)
            await self._add_message_to_session(session.session_id, welcome_message)

            logger.info(f"Started chat session {session.session_id} for user {user_id}")
            return session

        except Exception as e:
            logger.error(f"Error starting chat session: {e}")
            raise

    async def process_user_message(
        self,
        session_id: str,
        message_content: str,
        message_metadata: dict[str, Any] | None = None
    ) -> ChatMessage:
        """Process user message and generate therapeutic response."""
        try:
            start_time = time.perf_counter()

            # Get session and context
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            therapeutic_context = self.therapeutic_contexts.get(session_id)
            conversation_flow = self.conversation_flows.get(session_id)

            # Create user message
            user_message = ChatMessage(
                session_id=session_id,
                user_id=session.user_id,
                message_type=MessageType.USER_MESSAGE,
                content=message_content,
                therapeutic_context=message_metadata or {}
            )

            # Process message for therapeutic analysis
            await self._analyze_message_content(user_message, therapeutic_context)

            # Check for crisis indicators
            crisis_detected = await self._assess_crisis_risk(user_message, therapeutic_context)

            # Add message to session
            await self._add_message_to_session(session_id, user_message)

            # Generate therapeutic response
            if crisis_detected:
                response_message = await self._generate_crisis_response(user_message, therapeutic_context)
            else:
                response_message = await self._generate_therapeutic_response(
                    user_message, therapeutic_context, conversation_flow
                )

            # Add response to session
            await self._add_message_to_session(session_id, response_message)

            # Update conversation flow
            await self._update_conversation_flow(conversation_flow, user_message, response_message)

            # Update therapeutic context
            await self._update_therapeutic_context(therapeutic_context, user_message, response_message)

            # Track engagement
            if self.engagement_system:
                await self._track_message_engagement(session, user_message, response_message)

            # Update performance metrics
            processing_time = (time.perf_counter() - start_time) * 1000
            user_message.processing_time_ms = processing_time
            response_message.processing_time_ms = processing_time

            self.chat_system_metrics["total_messages_processed"] += 1
            self.chat_system_metrics["average_response_time_ms"] = (
                (self.chat_system_metrics["average_response_time_ms"] *
                 (self.chat_system_metrics["total_messages_processed"] - 1) + processing_time) /
                self.chat_system_metrics["total_messages_processed"]
            )

            logger.debug(f"Processed message in {processing_time:.2f}ms for session {session_id}")
            return response_message

        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            # Generate error response
            error_response = ChatMessage(
                session_id=session_id,
                user_id=session.user_id if session else "",
                message_type=MessageType.SYSTEM_MESSAGE,
                content="I apologize, but I'm having trouble processing your message right now. Please try again.",
                therapeutic_context={"error": str(e)}
            )
            return error_response

    async def get_session_history(
        self,
        session_id: str,
        limit: int | None = None
    ) -> list[ChatMessage]:
        """Get chat session message history."""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            messages = session.messages
            if limit:
                messages = messages[-limit:]

            return messages

        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []

    async def update_therapeutic_goals(
        self,
        session_id: str,
        new_goals: list[str]
    ) -> bool:
        """Update therapeutic goals for active session."""
        try:
            session = self.active_sessions.get(session_id)
            therapeutic_context = self.therapeutic_contexts.get(session_id)
            conversation_flow = self.conversation_flows.get(session_id)

            if not all([session, therapeutic_context, conversation_flow]):
                return False

            # Update goals
            session.session_goals = new_goals
            therapeutic_context.therapeutic_goals = new_goals
            conversation_flow.therapeutic_objectives = new_goals

            # Generate goal update message
            goal_message = ChatMessage(
                session_id=session_id,
                user_id=session.user_id,
                message_type=MessageType.SYSTEM_MESSAGE,
                content=f"I've updated your therapeutic goals: {', '.join(new_goals)}. Let's work together on these areas.",
                therapeutic_context={"updated_goals": new_goals}
            )

            await self._add_message_to_session(session_id, goal_message)

            logger.info(f"Updated therapeutic goals for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating therapeutic goals: {e}")
            return False

    async def end_chat_session(
        self,
        session_id: str,
        session_summary: str | None = None
    ) -> dict[str, Any]:
        """End therapeutic chat session and generate summary."""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            # Update session status
            session.is_active = False
            session.conversation_state = ConversationState.COMPLETED
            session.session_duration = datetime.utcnow() - session.started_at

            # Generate session summary
            summary = await self._generate_session_summary(session)

            # Create summary message
            summary_message = ChatMessage(
                session_id=session_id,
                user_id=session.user_id,
                message_type=MessageType.SESSION_SUMMARY,
                content=session_summary or summary["summary_text"],
                therapeutic_context=summary
            )

            await self._add_message_to_session(session_id, summary_message)

            # Update engagement metrics
            if self.engagement_system:
                await self._finalize_session_engagement(session)

            # Archive session data
            await self._archive_session(session)

            # Clean up active session
            self.active_sessions.pop(session_id, None)
            self.therapeutic_contexts.pop(session_id, None)
            self.conversation_flows.pop(session_id, None)

            # Update metrics
            self.chat_system_metrics["total_active_sessions"] -= 1
            self.chat_system_metrics["concurrent_users"] = len(self.active_sessions)

            logger.info(f"Ended chat session {session_id}")
            return summary

        except Exception as e:
            logger.error(f"Error ending chat session: {e}")
            return {"error": str(e)}

    async def get_therapeutic_insights(
        self,
        session_id: str
    ) -> dict[str, Any]:
        """Get therapeutic insights for current session."""
        try:
            session = self.active_sessions.get(session_id)
            therapeutic_context = self.therapeutic_contexts.get(session_id)
            conversation_flow = self.conversation_flows.get(session_id)

            if not all([session, therapeutic_context, conversation_flow]):
                return {"error": "Session data not found"}

            insights = {
                "session_id": session_id,
                "user_id": session.user_id,
                "session_duration": str(session.session_duration),
                "message_count": session.message_count,
                "conversation_state": session.conversation_state.value,
                "therapeutic_progress": therapeutic_context.therapeutic_progress,
                "emotional_journey": therapeutic_context.emotional_journey,
                "engagement_metrics": session.engagement_metrics,
                "therapeutic_outcomes": session.therapeutic_outcomes,
                "current_therapeutic_focus": session.current_therapeutic_focus,
                "active_frameworks": [fw.value for fw in session.active_therapeutic_frameworks],
                "crisis_risk_level": therapeutic_context.crisis_risk_assessment.get("risk_level", 0.0),
                "recommendations": await self._generate_therapeutic_recommendations(session, therapeutic_context)
            }

            return insights

        except Exception as e:
            logger.error(f"Error getting therapeutic insights: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check of the chat interface system."""
        try:
            health_status = {
                "status": "healthy" if self.status == "running" else self.status,
                "chat_interface_status": self.status,
                "active_sessions": len(self.active_sessions),
                "concurrent_users": self.chat_system_metrics["concurrent_users"],
                "total_messages_processed": self.chat_system_metrics["total_messages_processed"],
                "average_response_time_ms": self.chat_system_metrics["average_response_time_ms"],
                "therapeutic_interventions": self.chat_system_metrics["therapeutic_interventions"],
                "crisis_interventions": self.chat_system_metrics["crisis_interventions"],
                "system_availability": self.chat_system_metrics["system_availability"],
                "background_tasks_running": (
                    self._message_processing_task is not None and not self._message_processing_task.done()
                ),
                "websocket_connections": len(self.websocket_connections),
                "message_queue_size": self.message_queue.qsize(),
                "chat_system_metrics": self.chat_system_metrics,
                "system_integrations": {
                    "accessibility_system": self.accessibility_system is not None,
                    "ui_engine": self.ui_engine is not None,
                    "engagement_system": self.engagement_system is not None,
                    "personalization_engine": self.personalization_engine is not None,
                    "therapeutic_systems": len(self.therapeutic_systems),
                    "clinical_dashboard_manager": self.clinical_dashboard_manager is not None,
                    "cloud_deployment_manager": self.cloud_deployment_manager is not None,
                }
            }

            return health_status

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def shutdown(self):
        """Shutdown the Therapeutic Chat Interface System."""
        try:
            logger.info("Shutting down TherapeuticChatInterface")

            # Signal shutdown to background tasks
            self._shutdown_event.set()

            # End all active sessions
            for session_id in list(self.active_sessions.keys()):
                await self.end_chat_session(session_id, "System shutdown")

            # Cancel background tasks
            tasks = [
                self._message_processing_task,
                self._session_management_task,
                self._therapeutic_monitoring_task,
                self._performance_monitoring_task,
            ]

            for task in tasks:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            # Close websocket connections
            for connection in self.websocket_connections.values():
                if hasattr(connection, 'close'):
                    await connection.close()

            self.status = "shutdown"
            logger.info("TherapeuticChatInterface shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    # Helper methods for system initialization
    async def _initialize_message_processors(self):
        """Initialize message processors for different message types."""
        try:
            self.message_processors = {
                MessageType.USER_MESSAGE: self._process_user_message_content,
                MessageType.THERAPEUTIC_RESPONSE: self._process_therapeutic_response,
                MessageType.SYSTEM_MESSAGE: self._process_system_message,
                MessageType.CRISIS_INTERVENTION: self._process_crisis_intervention,
                MessageType.ACHIEVEMENT_NOTIFICATION: self._process_achievement_notification,
                MessageType.PROGRESS_UPDATE: self._process_progress_update,
                MessageType.THERAPEUTIC_SUGGESTION: self._process_therapeutic_suggestion,
                MessageType.SESSION_SUMMARY: self._process_session_summary,
            }

            logger.info("Message processors initialized")

        except Exception as e:
            logger.error(f"Error initializing message processors: {e}")
            raise

    async def _initialize_response_generators(self):
        """Initialize response generators for different therapeutic frameworks."""
        try:
            self.response_generators = {
                TherapeuticFramework.CBT: self._generate_cbt_response,
                TherapeuticFramework.DBT: self._generate_dbt_response,
                TherapeuticFramework.ACT: self._generate_act_response,
                TherapeuticFramework.MINDFULNESS: self._generate_mindfulness_response,
                TherapeuticFramework.HUMANISTIC: self._generate_humanistic_response,
                TherapeuticFramework.PSYCHODYNAMIC: self._generate_psychodynamic_response,
                TherapeuticFramework.SOLUTION_FOCUSED: self._generate_solution_focused_response,
                TherapeuticFramework.NARRATIVE: self._generate_narrative_response,
            }

            logger.info("Response generators initialized")

        except Exception as e:
            logger.error(f"Error initializing response generators: {e}")
            raise

    async def _initialize_intervention_handlers(self):
        """Initialize intervention handlers for different therapeutic situations."""
        try:
            self.intervention_handlers = {
                "crisis_intervention": self._handle_crisis_intervention,
                "emotional_support": self._handle_emotional_support,
                "skill_practice": self._handle_skill_practice,
                "goal_setting": self._handle_goal_setting,
                "progress_review": self._handle_progress_review,
                "therapeutic_homework": self._handle_therapeutic_homework,
                "mindfulness_exercise": self._handle_mindfulness_exercise,
                "cognitive_restructuring": self._handle_cognitive_restructuring,
            }

            logger.info("Intervention handlers initialized")

        except Exception as e:
            logger.error(f"Error initializing intervention handlers: {e}")
            raise

    async def _initialize_conversation_flows(self):
        """Initialize conversation flow templates."""
        try:
            # Define standard therapeutic conversation flows
            self.conversation_flow_templates = {
                "initial_assessment": {
                    "stages": [
                        {"name": "welcome", "duration": 5, "objectives": ["establish_rapport", "explain_process"]},
                        {"name": "assessment", "duration": 15, "objectives": ["identify_goals", "assess_needs"]},
                        {"name": "planning", "duration": 10, "objectives": ["create_plan", "set_expectations"]},
                    ]
                },
                "therapeutic_session": {
                    "stages": [
                        {"name": "check_in", "duration": 5, "objectives": ["assess_current_state", "review_progress"]},
                        {"name": "therapeutic_work", "duration": 40, "objectives": ["address_goals", "practice_skills"]},
                        {"name": "integration", "duration": 10, "objectives": ["summarize_insights", "plan_next_steps"]},
                        {"name": "closing", "duration": 5, "objectives": ["provide_support", "schedule_follow_up"]},
                    ]
                },
                "crisis_intervention": {
                    "stages": [
                        {"name": "safety_assessment", "duration": 2, "objectives": ["assess_immediate_risk", "ensure_safety"]},
                        {"name": "stabilization", "duration": 10, "objectives": ["provide_support", "reduce_distress"]},
                        {"name": "resource_connection", "duration": 5, "objectives": ["connect_resources", "create_safety_plan"]},
                    ]
                }
            }

            logger.info("Conversation flows initialized")

        except Exception as e:
            logger.error(f"Error initializing conversation flows: {e}")
            raise

    async def _initialize_therapeutic_templates(self):
        """Initialize therapeutic response templates."""
        try:
            self.therapeutic_templates = {
                "welcome_messages": [
                    "Hello! I'm here to support you on your therapeutic journey. How are you feeling today?",
                    "Welcome! I'm glad you're here. What would you like to work on in our session today?",
                    "Hi there! I'm here to listen and help. What's on your mind today?",
                ],
                "empathy_responses": [
                    "I can hear that this is really difficult for you.",
                    "It sounds like you're going through a challenging time.",
                    "Thank you for sharing that with me. That takes courage.",
                ],
                "validation_responses": [
                    "Your feelings are completely valid.",
                    "It makes sense that you would feel this way.",
                    "You're not alone in feeling like this.",
                ],
                "encouragement_responses": [
                    "You're taking important steps by being here.",
                    "I can see the strength it takes to work on these challenges.",
                    "You've shown real resilience in dealing with this.",
                ],
                "crisis_responses": [
                    "I'm concerned about your safety right now. Let's talk about how to keep you safe.",
                    "Thank you for telling me about these thoughts. You're not alone, and we can work through this together.",
                    "I want to help you through this difficult time. Let's focus on your immediate safety.",
                ],
                # Framework-specific response templates
                "framework_responses": {
                    "narrative_therapy": [
                        "That's an important part of your story. How would you like this chapter to unfold?",
                        "I'm curious about the unique outcomes in your story - times when things were different.",
                        "It sounds like you're the author of your own story. What would you like to rewrite?",
                        "How would you externalize this problem? What would you call it if it were separate from you?",
                        "What would the people who know you best say about your character strengths?",
                        "If this were a story being told, what themes would emerge about your resilience?",
                        "What meaning are you making from this experience in your life narrative?",
                        "How does this fit into the larger story of who you're becoming?",
                        "Let's explore this story together. What details would help me understand your experience better?",
                        "I can see this is a significant chapter. What would you want readers to know about this part of your journey?",
                        "Your story has many layers. Which aspect feels most important to develop right now?",
                        "If we were co-writing this story, what direction would you want to take it next?"
                    ],
                    "cognitive_behavioral_therapy": [
                        "I notice you mentioned some thoughts. Let's explore how those thoughts might be affecting how you feel.",
                        "What evidence do you have for and against this thought?",
                        "How might we challenge this thinking pattern together?",
                        "What would you tell a friend who had this same thought?",
                        "Let's examine the connection between your thoughts, feelings, and behaviors here.",
                        "What alternative ways could we look at this situation?"
                    ],
                    "dialectical_behavior_therapy": [
                        "It sounds like you're experiencing some intense emotions. Let's practice some distress tolerance skills.",
                        "Can you try taking three deep breaths with me right now?",
                        "What would wise mind tell you about this situation?",
                        "Let's practice radical acceptance - what would that look like here?",
                        "How might we use some interpersonal effectiveness skills in this situation?",
                        "What emotion regulation strategies have worked for you before?"
                    ],
                    "mindfulness_based": [
                        "Let's take a moment to be present. Can you notice three things you can see right now?",
                        "What do you notice in your body as you share this with me?",
                        "How might we bring some mindful awareness to this experience?",
                        "Can you observe these thoughts and feelings without judgment?",
                        "What would it be like to approach this with beginner's mind?",
                        "Let's practice grounding together - what can you feel, hear, and see?"
                    ],
                    "solution_focused_therapy": [
                        "What has worked for you in similar situations before?",
                        "What strengths can you draw upon here?",
                        "On a scale of 1-10, where are you now, and what would move you up just one point?",
                        "Tell me about a time when this problem wasn't as present in your life.",
                        "What would your best friend say are your greatest resources?",
                        "If this issue were resolved, what would be different in your daily life?"
                    ],
                    "humanistic_therapy": [
                        "I'm curious about your authentic experience of this situation.",
                        "What feels most true for you right now?",
                        "How does this align with your core values and sense of self?",
                        "What would it mean to honor your feelings fully here?",
                        "I sense there's something important you're trying to express.",
                        "What would self-compassion look like in this moment?"
                    ],
                    "psychodynamic_therapy": [
                        "I'm curious about the patterns you're noticing. Have you experienced similar feelings before?",
                        "What comes up for you when you think about the relationships in your life?",
                        "How might your past experiences be influencing this current situation?",
                        "What themes do you notice recurring in your relationships?",
                        "I wonder what this might represent on a deeper level.",
                        "What feelings or memories does this bring up from earlier in your life?"
                    ],
                    "acceptance_commitment_therapy": [
                        "What values are most important to you in this situation?",
                        "How might you move toward what matters most, even with these difficult feelings?",
                        "What would psychological flexibility look like here?",
                        "Can you make room for these feelings while still taking valued action?",
                        "What metaphor might help us understand your experience?",
                        "How might you defuse from these thoughts and connect with your values?"
                    ]
                },
                # Interactive storytelling templates
                "interactive_storytelling": {
                    "story_starters": [
                        "Let's begin your story. What's the setting where this important experience takes place?",
                        "Every story has a beginning. Where would you like to start telling yours?",
                        "I'm ready to listen to your story. What's the first thing you'd like me to know?",
                        "Let's create this story together. What scene would you like to set first?"
                    ],
                    "story_development": [
                        "That's a compelling beginning. What happens next in your story?",
                        "I can picture that scene. What details would help me understand it even better?",
                        "This story is developing beautifully. What would you like to explore next?",
                        "I'm following your narrative. What other characters or elements are important to include?"
                    ],
                    "story_deepening": [
                        "There's so much depth to this story. What emotions were you experiencing during this part?",
                        "I sense there's more to this chapter. What wasn't said or expressed at the time?",
                        "This part of your story seems particularly significant. What made it so meaningful?",
                        "I'm curious about the inner experience during this part of your story. What was going on inside?"
                    ],
                    "story_reflection": [
                        "As we pause in your story, what stands out most to you about what you've shared?",
                        "Looking at this story from where you are now, what do you notice?",
                        "What themes are emerging as you tell this story?",
                        "How does it feel to put this experience into story form?"
                    ],
                    "story_continuation": [
                        "Your story doesn't end there. What would you like to explore next?",
                        "This story has more chapters. Which one calls to you now?",
                        "I sense there's more to this narrative. What other parts want to be told?",
                        "Your story is rich with possibilities. What direction feels right to explore?"
                    ]
                }
            }

            logger.info("Therapeutic templates initialized")

        except Exception as e:
            logger.error(f"Error initializing therapeutic templates: {e}")
            raise

    def _get_framework_response_template(self, framework: TherapeuticFramework) -> str:
        """Get a random response template for the specified therapeutic framework."""
        import random

        framework_key = framework.value
        framework_responses = self.therapeutic_templates.get("framework_responses", {})

        if framework_key in framework_responses:
            templates = framework_responses[framework_key]
            return random.choice(templates)

        # Fallback to empathy response if framework not found
        empathy_responses = self.therapeutic_templates.get("empathy_responses", [
            "I can hear that this is really difficult for you."
        ])
        return random.choice(empathy_responses)

    def _detect_story_context(self, message: ChatMessage) -> dict[str, Any]:
        """Detect story context and narrative elements in user message."""
        content = message.content.lower()
        story_context = {
            "has_narrative_elements": False,
            "story_indicators": [],
            "narrative_elements": {},
            "emotional_tone": "neutral",
            "story_type": None
        }

        # Story structure indicators (enhanced patterns)
        story_structure_patterns = {
            "temporal_markers": ["when i was", "yesterday", "last week", "growing up", "back then", "once upon", "there was a time", "childhood", "one time", "this time"],
            "character_references": ["my mother", "my father", "my friend", "someone", "this person", "he said", "she told me", "she always", "he always"],
            "plot_elements": ["what happened was", "then", "after that", "suddenly", "it turned out", "in the end", "what happened", "then i"],
            "setting_descriptions": ["at home", "at work", "in school", "where i lived", "this place", "in class"]
        }

        # Narrative therapy specific elements (enhanced patterns)
        narrative_therapy_elements = {
            "externalization_language": ["the depression", "the anxiety", "this problem", "it makes me", "it tells me", "keeps telling me"],
            "identity_statements": ["i am", "i'm the kind of person", "people see me as", "i've always been", "who i am", "figure out who"],
            "meaning_making": ["what this means", "the significance", "why this matters", "what i learned"],
            "unique_outcomes": ["except when", "but there was this time", "different from usual", "surprisingly", "there was this one time", "one time when"]
        }

        detected_elements = []
        narrative_elements = {}

        # Check for story structure patterns
        for category, patterns in story_structure_patterns.items():
            matches = [pattern for pattern in patterns if pattern in content]
            if matches:
                detected_elements.extend(matches)
                narrative_elements[category] = matches

        # Check for narrative therapy elements
        for category, patterns in narrative_therapy_elements.items():
            matches = [pattern for pattern in patterns if pattern in content]
            if matches:
                detected_elements.extend(matches)
                narrative_elements[category] = matches

        # Determine if message has significant narrative content (lowered threshold)
        story_context["has_narrative_elements"] = len(detected_elements) >= 1
        story_context["story_indicators"] = detected_elements
        story_context["narrative_elements"] = narrative_elements

        # Determine story type
        if narrative_elements.get("temporal_markers"):
            story_context["story_type"] = "personal_history"
        elif narrative_elements.get("externalization_language"):
            story_context["story_type"] = "problem_externalization"
        elif narrative_elements.get("identity_statements"):
            story_context["story_type"] = "identity_narrative"
        elif narrative_elements.get("unique_outcomes"):
            story_context["story_type"] = "exception_story"

        return story_context

    def _extract_narrative_elements(self, message: ChatMessage, story_context: dict[str, Any]) -> dict[str, Any]:
        """Extract and categorize specific narrative elements from the message."""
        content = message.content
        narrative_elements = {
            "characters": [],
            "plot_points": [],
            "themes": [],
            "emotions": [],
            "settings": [],
            "conflicts": [],
            "resolutions": []
        }

        # Character extraction patterns
        character_patterns = [
            r"my (?:mother|mom|father|dad|sister|brother|friend|partner|spouse|boss|teacher|therapist)",
            r"(?:he|she|they) (?:said|told|asked|did|was|were)",
            r"someone (?:who|that)",
            r"this person (?:who|that)"
        ]

        # Plot point indicators
        plot_indicators = [
            "what happened", "then", "after that", "suddenly", "meanwhile",
            "it turned out", "in the end", "finally", "eventually"
        ]

        # Theme extraction (therapeutic themes)
        therapeutic_themes = {
            "loss": ["lost", "grief", "missing", "gone", "died", "ended"],
            "growth": ["learned", "grew", "developed", "changed", "became"],
            "struggle": ["difficult", "hard", "challenging", "tough", "struggled"],
            "resilience": ["overcame", "survived", "endured", "persevered", "strong"],
            "relationships": ["connected", "loved", "supported", "together", "alone"],
            "identity": ["who i am", "myself", "identity", "self", "person i am"]
        }

        # Emotional indicators
        emotion_words = {
            "positive": ["happy", "joy", "excited", "proud", "grateful", "hopeful"],
            "negative": ["sad", "angry", "frustrated", "disappointed", "hurt", "afraid"],
            "complex": ["confused", "conflicted", "ambivalent", "uncertain", "mixed"]
        }

        content_lower = content.lower()

        # Extract characters (simplified)
        import re
        for pattern in character_patterns:
            matches = re.findall(pattern, content_lower)
            narrative_elements["characters"].extend(matches)

        # Extract plot points
        for indicator in plot_indicators:
            if indicator in content_lower:
                narrative_elements["plot_points"].append(indicator)

        # Extract themes
        for theme, keywords in therapeutic_themes.items():
            if any(keyword in content_lower for keyword in keywords):
                narrative_elements["themes"].append(theme)

        # Extract emotions
        for emotion_type, words in emotion_words.items():
            found_emotions = [word for word in words if word in content_lower]
            if found_emotions:
                narrative_elements["emotions"].extend([(emotion_type, word) for word in found_emotions])

        # Extract conflicts and resolutions
        conflict_indicators = ["problem", "issue", "struggle", "difficulty", "challenge", "conflict"]
        resolution_indicators = ["solved", "resolved", "overcame", "figured out", "worked through"]

        narrative_elements["conflicts"] = [word for word in conflict_indicators if word in content_lower]
        narrative_elements["resolutions"] = [word for word in resolution_indicators if word in content_lower]

        return narrative_elements

    def _track_narrative_progression(self, session_id: str, narrative_elements: dict[str, Any]) -> None:
        """Track narrative progression across conversation turns."""
        if not hasattr(self, 'narrative_tracking'):
            self.narrative_tracking = {}

        if session_id not in self.narrative_tracking:
            self.narrative_tracking[session_id] = {
                "story_threads": [],
                "character_mentions": {},
                "recurring_themes": {},
                "emotional_journey": [],
                "narrative_coherence_score": 0.0
            }

        session_narrative = self.narrative_tracking[session_id]

        # Track character mentions
        for character in narrative_elements.get("characters", []):
            if character not in session_narrative["character_mentions"]:
                session_narrative["character_mentions"][character] = 0
            session_narrative["character_mentions"][character] += 1

        # Track recurring themes
        for theme in narrative_elements.get("themes", []):
            if theme not in session_narrative["recurring_themes"]:
                session_narrative["recurring_themes"][theme] = 0
            session_narrative["recurring_themes"][theme] += 1

        # Track emotional journey
        emotions = narrative_elements.get("emotions", [])
        if emotions:
            session_narrative["emotional_journey"].append({
                "turn": len(session_narrative["emotional_journey"]) + 1,
                "emotions": emotions
            })

        # Update narrative coherence score (simplified)
        coherence_factors = [
            len(session_narrative["character_mentions"]) > 0,  # Has characters
            len(session_narrative["recurring_themes"]) > 0,   # Has themes
            len(session_narrative["emotional_journey"]) > 1   # Emotional progression
        ]
        session_narrative["narrative_coherence_score"] = sum(coherence_factors) / len(coherence_factors)

    def _enhance_narrative_state_management(self, session_id: str) -> dict[str, Any]:
        """Enhanced narrative state management for sustained story contexts."""
        if not hasattr(self, 'narrative_tracking'):
            self.narrative_tracking = {}

        if session_id not in self.narrative_tracking:
            self.narrative_tracking[session_id] = {
                "story_threads": [],
                "character_mentions": {},
                "recurring_themes": {},
                "emotional_journey": [],
                "narrative_coherence_score": 0.0,
                "world_building_elements": {},
                "therapeutic_progress": {},
                "story_arcs": [],
                "session_continuity": {}
            }

        session_narrative = self.narrative_tracking[session_id]

        # Enhanced world building tracking
        if "world_building_elements" not in session_narrative:
            session_narrative["world_building_elements"] = {
                "settings": [],
                "relationships": {},
                "conflicts": [],
                "resolutions": [],
                "symbolic_elements": [],
                "therapeutic_metaphors": []
            }

        # Enhanced therapeutic progress tracking
        if "therapeutic_progress" not in session_narrative:
            session_narrative["therapeutic_progress"] = {
                "externalization_progress": 0.0,
                "reauthoring_attempts": 0,
                "unique_outcomes_identified": 0,
                "identity_exploration_depth": 0.0,
                "meaning_making_instances": 0
            }

        # Story arc tracking for sustained narratives
        if "story_arcs" not in session_narrative:
            session_narrative["story_arcs"] = []

        return session_narrative

    def _maintain_story_continuity(self, session_id: str, current_narrative_elements: dict[str, Any]) -> dict[str, Any]:
        """Maintain story continuity across conversation turns."""
        session_narrative = self._enhance_narrative_state_management(session_id)

        # Update world building elements
        world_elements = session_narrative["world_building_elements"]

        # Track settings mentioned
        if current_narrative_elements.get("settings"):
            for setting in current_narrative_elements["settings"]:
                if setting not in world_elements["settings"]:
                    world_elements["settings"].append(setting)

        # Track relationship dynamics
        if current_narrative_elements.get("characters"):
            for character in current_narrative_elements["characters"]:
                if character not in world_elements["relationships"]:
                    world_elements["relationships"][character] = {
                        "first_mentioned": len(session_narrative["emotional_journey"]) + 1,
                        "relationship_type": "unknown",
                        "significance": "emerging"
                    }

        # Track conflicts and resolutions
        if current_narrative_elements.get("conflicts"):
            world_elements["conflicts"].extend(current_narrative_elements["conflicts"])

        if current_narrative_elements.get("resolutions"):
            world_elements["resolutions"].extend(current_narrative_elements["resolutions"])

        # Update therapeutic progress metrics
        therapeutic_progress = session_narrative["therapeutic_progress"]

        # Track externalization progress
        if "externalization_language" in current_narrative_elements:
            therapeutic_progress["externalization_progress"] += 0.1

        # Track reauthoring attempts
        if any(theme in ["growth", "resilience"] for theme in current_narrative_elements.get("themes", [])):
            therapeutic_progress["reauthoring_attempts"] += 1

        # Track unique outcomes
        if "unique_outcomes" in current_narrative_elements:
            therapeutic_progress["unique_outcomes_identified"] += len(current_narrative_elements["unique_outcomes"])

        # Track identity exploration
        if "identity_statements" in current_narrative_elements:
            therapeutic_progress["identity_exploration_depth"] += 0.2

        # Track meaning making
        if current_narrative_elements.get("themes"):
            therapeutic_progress["meaning_making_instances"] += 1

        return session_narrative

    def _generate_continuity_aware_response(self, session_id: str, current_story_context: dict[str, Any]) -> str:
        """Generate response that maintains awareness of ongoing story continuity."""
        session_narrative = self._enhance_narrative_state_management(session_id)

        # Check for recurring elements
        recurring_characters = [char for char, count in session_narrative["character_mentions"].items() if count > 1]
        recurring_themes = [theme for theme, count in session_narrative["recurring_themes"].items() if count > 1]

        continuity_responses = []

        # Reference recurring characters
        if recurring_characters:
            char = recurring_characters[0]
            continuity_responses.append(f"I notice {char} has been an important figure in your story. How does this current experience connect to what you've shared about them before?")

        # Reference recurring themes
        if recurring_themes:
            theme = recurring_themes[0]
            continuity_responses.append(f"This connects to the theme of {theme} that's been present throughout your story. How do you see this pattern developing?")

        # Reference therapeutic progress
        therapeutic_progress = session_narrative.get("therapeutic_progress", {})
        if therapeutic_progress.get("externalization_progress", 0) > 0.3:
            continuity_responses.append("I can see how you've been working to separate yourself from the problem in your story. How does this current experience fit with that process?")

        if therapeutic_progress.get("reauthoring_attempts", 0) > 2:
            continuity_responses.append("You've been exploring different ways to tell your story. What new perspective might this experience add?")

        # Default continuity response
        if not continuity_responses:
            continuity_responses.append("This adds another layer to the story you've been sharing. How does this connect to the larger narrative of your journey?")

        import random
        return random.choice(continuity_responses)

    def _generate_story_engaged_response(self, message: ChatMessage, story_context: dict[str, Any], narrative_elements: dict[str, Any]) -> str:
        """Generate response that actively engages with story elements."""
        import random

        # Story-specific response templates based on story type
        story_type = story_context.get("story_type")

        if story_type == "personal_history":
            templates = [
                "That sounds like a significant moment in your story. What did that experience teach you about yourself?",
                "I can hear how important this memory is to you. How does it connect to who you are today?",
                "Thank you for sharing that part of your journey. What would you want others to know about that experience?",
                "That chapter of your life sounds meaningful. How has it shaped the story you're writing now?"
            ]
        elif story_type == "problem_externalization":
            templates = [
                "I notice you're talking about [the problem] as something separate from you. What would you call this problem if you gave it a name?",
                "It sounds like this problem has been trying to convince you of certain things. What has it been telling you?",
                "When this problem isn't so present, what's different about your story?",
                "What would it look like to not let this problem be the author of your story?"
            ]
        elif story_type == "identity_narrative":
            templates = [
                "You're sharing something important about who you are. What other aspects of your identity feel significant?",
                "I hear you describing yourself in a particular way. Are there other ways people who know you well might describe you?",
                "That's one part of your identity story. What other chapters would you want to include?",
                "How would you like this aspect of your identity to evolve in your ongoing story?"
            ]
        elif story_type == "exception_story":
            templates = [
                "That sounds like a unique outcome - a time when things were different. What made that possible?",
                "I'm curious about this exception to the usual pattern. What was happening differently then?",
                "That's an interesting plot twist in your story. What does it tell you about your capabilities?",
                "These exceptions are important - they show other possibilities in your story. What can we learn from them?"
            ]
        else:
            # General narrative engagement templates
            templates = [
                "I can hear the story you're telling. What feels most important about this part of your narrative?",
                "Thank you for sharing your story with me. What meaning are you making from this experience?",
                "Every story has multiple perspectives. How might this story look from a different angle?",
                "What would you want the next chapter of this story to look like?"
            ]

        # Select base response
        base_response = random.choice(templates)

        # Enhance response based on narrative elements
        if narrative_elements.get("themes"):
            prominent_theme = narrative_elements["themes"][0]
            if prominent_theme == "resilience":
                base_response += " I'm struck by the strength I hear in your story."
            elif prominent_theme == "growth":
                base_response += " It sounds like this experience has been part of your growth journey."
            elif prominent_theme == "struggle":
                base_response += " I can hear how challenging this has been for you."

        if narrative_elements.get("emotions"):
            emotion_type, emotion_word = narrative_elements["emotions"][0]
            if emotion_type == "complex":
                base_response += f" I notice you mentioned feeling {emotion_word} - that sounds like a complex emotional experience."

        return base_response

    async def _integrate_story_context_in_response(self, message: ChatMessage, context: TherapeuticContext) -> str:
        """Integrate story context detection into response generation."""
        # Detect story context
        story_context = self._detect_story_context(message)

        # If significant narrative elements are detected, use story-engaged response
        if story_context["has_narrative_elements"]:
            narrative_elements = self._extract_narrative_elements(message, story_context)
            self._track_narrative_progression(message.session_id, narrative_elements)

            # Generate story-engaged response
            return self._generate_story_engaged_response(message, story_context, narrative_elements)

        # Otherwise, use standard framework response
        framework = self._select_therapeutic_framework(message, context)
        return self._get_framework_response_template(framework)

    def _initiate_collaborative_narrative_building(self, message: ChatMessage, story_context: dict[str, Any]) -> str:
        """Initiate collaborative narrative building with the user."""
        import random

        story_type = story_context.get("story_type")

        # Collaborative prompts based on story type
        collaborative_prompts = {
            "personal_history": [
                "I'd love to explore this story with you. What would you like to focus on - the characters, the setting, or what this experience meant to you?",
                "This sounds like an important chapter in your life story. Should we explore what led up to this moment, or what happened next?",
                "I'm curious about the different perspectives in this story. How might other people involved have experienced this?",
                "What details about this story feel most significant to you right now?"
            ],
            "problem_externalization": [
                "Let's work together to understand this problem better. If we gave it a character in your story, what would it look like?",
                "I'm interested in exploring when this problem has less power in your story. Can we build that part together?",
                "What would it look like if you were the director of this story instead of this problem?",
                "Let's co-author a different ending to this story. What would need to change?"
            ],
            "identity_narrative": [
                "I'd like to help you explore the different aspects of your identity story. Which part feels most important to develop?",
                "Let's build a richer picture of who you are together. What other qualities would your story include?",
                "If we were writing your character description, what strengths would we definitely include?",
                "What would you want the next chapter of your identity story to emphasize?"
            ],
            "exception_story": [
                "This exception sounds important - let's explore it together. What made this different outcome possible?",
                "I'd like to help you build on this unique outcome. What other times have you experienced something similar?",
                "Let's develop this part of your story more. What resources or strengths were you drawing on?",
                "If we could recreate the conditions that made this exception possible, what would that look like?"
            ]
        }

        # Default collaborative prompts
        default_prompts = [
            "I'd like to explore this story with you. What aspect feels most important to develop together?",
            "Let's build on this narrative together. What would you like to focus on next?",
            "I'm here to help you develop your story. What direction would you like to take it?",
            "This story has many possibilities. What would you like to explore together?"
        ]

        prompts = collaborative_prompts.get(story_type, default_prompts)
        return random.choice(prompts)

    def _suggest_narrative_development_options(self, narrative_elements: dict[str, Any]) -> list[str]:
        """Suggest specific options for developing the narrative further."""
        options = []

        # Character development options
        if narrative_elements.get("characters"):
            options.append("Explore the relationships and dynamics between the characters in your story")
            options.append("Develop the backstory or motivations of key characters")

        # Theme development options
        if narrative_elements.get("themes"):
            prominent_theme = narrative_elements["themes"][0]
            if prominent_theme == "resilience":
                options.append("Explore other times you've shown resilience in your story")
            elif prominent_theme == "growth":
                options.append("Identify the key moments of growth and transformation")
            elif prominent_theme == "struggle":
                options.append("Examine how struggles have shaped your character development")

        # Plot development options
        if narrative_elements.get("plot_points"):
            options.append("Explore what led up to these key moments in your story")
            options.append("Consider alternative ways these events could have unfolded")

        # Emotional development options
        if narrative_elements.get("emotions"):
            options.append("Explore the emotional journey and how feelings evolved")
            options.append("Identify moments of emotional strength or breakthrough")

        # Conflict and resolution options
        if narrative_elements.get("conflicts"):
            options.append("Examine how conflicts have been resolved or could be resolved")
            options.append("Explore what resources you've used to handle challenges")

        # Default options if none specific found
        if not options:
            options = [
                "Explore the meaning and significance of this experience",
                "Consider different perspectives on this story",
                "Identify the strengths and resources present in your narrative",
                "Examine how this story connects to your larger life journey"
            ]

        return options[:3]  # Return top 3 options

    def _facilitate_story_co_creation(self, message: ChatMessage, story_context: dict[str, Any], narrative_elements: dict[str, Any]) -> str:
        """Facilitate collaborative story creation with therapeutic guidance."""

        # Get collaborative prompt
        base_response = self._initiate_collaborative_narrative_building(message, story_context)

        # Add development options
        development_options = self._suggest_narrative_development_options(narrative_elements)

        if development_options:
            base_response += "\n\nSome directions we could explore together:"
            for i, option in enumerate(development_options, 1):
                base_response += f"\n{i}. {option}"
            base_response += "\n\nWhat feels most meaningful to you right now?"

        return base_response

    def _apply_narrative_therapeutic_interventions(self, message: ChatMessage, story_context: dict[str, Any], narrative_elements: dict[str, Any]) -> str:
        """Apply specific narrative therapy interventions based on story content."""
        import random

        story_type = story_context.get("story_type")
        interventions = []

        # Externalization interventions
        if story_type == "problem_externalization" or narrative_elements.get("conflicts"):
            externalization_interventions = [
                "Let's give this problem a name. What would you call it if it were a character in your story?",
                "When this problem isn't around, what's different about your story? What becomes possible?",
                "What tactics does this problem use to convince you of things? How does it operate in your story?",
                "If you were to write a letter to this problem, what would you want to say to it?",
                "What would it look like to not invite this problem to be the narrator of your story?"
            ]
            interventions.extend(externalization_interventions)

        # Re-authoring interventions
        if story_type == "identity_narrative" or narrative_elements.get("themes"):
            reauthoring_interventions = [
                "If you were rewriting this chapter of your story, what would you change?",
                "What alternative story about yourself might be equally true?",
                "If a close friend were telling your story, what strengths would they emphasize?",
                "What would the preferred version of this story look like?",
                "How might you author a different ending to this narrative?"
            ]
            interventions.extend(reauthoring_interventions)

        # Unique outcomes interventions
        if story_type == "exception_story" or "resilience" in narrative_elements.get("themes", []):
            unique_outcomes_interventions = [
                "This sounds like a unique outcome - tell me more about what made this different experience possible.",
                "What does this exception tell us about your capabilities and resources?",
                "How might we thicken this alternative story? What other examples support it?",
                "What would need to happen for more of these unique outcomes to occur in your story?",
                "Who else has witnessed these moments when you've shown this strength?"
            ]
            interventions.extend(unique_outcomes_interventions)

        # Definitional ceremony interventions
        if narrative_elements.get("characters") or story_type == "personal_history":
            definitional_interventions = [
                "Who in your life has witnessed your strength in this story? What would they say about you?",
                "If we invited the people who know you best to comment on this story, what would they highlight?",
                "What would your younger self think about how you've handled this situation?",
                "Who would be least surprised by the resilience you've shown in this story?",
                "What audience would you want to hear this story of your growth and strength?"
            ]
            interventions.extend(definitional_interventions)

        # Landscape of action vs landscape of identity
        if narrative_elements.get("plot_points"):
            landscape_interventions = [
                "We've talked about what happened (landscape of action). What does this say about who you are (landscape of identity)?",
                "Beyond the events themselves, what do these actions reveal about your values and commitments?",
                "What intentions and purposes were guiding you through these experiences?",
                "How do these actions connect to your hopes and dreams for your life?",
                "What do these choices say about what matters most to you?"
            ]
            interventions.extend(landscape_interventions)

        # Default narrative interventions
        if not interventions:
            default_interventions = [
                "What meaning are you making from this story?",
                "How does this story connect to your values and what's important to you?",
                "What would you want others to learn from your story?",
                "How might this story be part of a larger narrative of growth and resilience?"
            ]
            interventions.extend(default_interventions)

        return random.choice(interventions)

    def _create_therapeutic_story_metaphor(self, narrative_elements: dict[str, Any]) -> str:
        """Create therapeutic metaphors based on narrative elements."""
        import random

        themes = narrative_elements.get("themes", [])
        narrative_elements.get("emotions", [])

        metaphor_templates = {
            "resilience": [
                "Your story reminds me of a tree that bends in strong winds but doesn't break. What has helped you stay rooted?",
                "Like a river that finds its way around obstacles, your story shows how you've navigated challenges. What keeps you flowing forward?",
                "Your narrative is like a phoenix story - rising from difficult circumstances. What fuels your ability to rise?"
            ],
            "growth": [
                "Your story is like a garden where new growth emerges from difficult seasons. What conditions help you flourish?",
                "Like a butterfly emerging from its cocoon, your story shows transformation. What supports your metamorphosis?",
                "Your narrative reminds me of a mountain climber who discovers new vistas with each challenge overcome."
            ],
            "struggle": [
                "Your story is like a hero's journey - facing challenges that ultimately reveal your strength. What allies do you have on this journey?",
                "Like a ship navigating stormy seas, your story shows courage in difficult waters. What serves as your compass?",
                "Your narrative reminds me of a warrior who fights not just external battles, but discovers inner strength."
            ],
            "identity": [
                "Your story is like an artist discovering their unique style - exploring different aspects of who you are. What colors feel most authentic?",
                "Like an author finding their voice, your story shows you discovering what makes you uniquely you.",
                "Your narrative reminds me of an explorer mapping new territory - the territory of your own identity and possibilities."
            ]
        }

        # Select metaphor based on prominent theme
        if themes:
            prominent_theme = themes[0]
            if prominent_theme in metaphor_templates:
                return random.choice(metaphor_templates[prominent_theme])

        # Default metaphor
        default_metaphors = [
            "Your story is like a book being written - each chapter adds depth and meaning to the whole narrative.",
            "Like a tapestry being woven, your story shows how different threads come together to create something beautiful.",
            "Your narrative reminds me of a journey where each step, even the difficult ones, leads to new discoveries."
        ]

        return random.choice(default_metaphors)

    # Background task methods
    async def _message_processing_loop(self):
        """Background task for processing message queue."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Process messages from queue
                    if not self.message_queue.empty():
                        message_data = await asyncio.wait_for(
                            self.message_queue.get(), timeout=1.0
                        )
                        await self._process_queued_message(message_data)
                    else:
                        await asyncio.sleep(0.1)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in message processing loop: {e}")
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Message processing loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in message processing loop: {e}")

    async def _session_management_loop(self):
        """Background task for session management and cleanup."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Check for inactive sessions
                    current_time = datetime.utcnow()
                    inactive_sessions = []

                    for session_id, session in self.active_sessions.items():
                        time_since_activity = current_time - session.last_activity
                        if time_since_activity.total_seconds() > (self.config["session_timeout_minutes"] * 60):
                            inactive_sessions.append(session_id)

                    # Clean up inactive sessions
                    for session_id in inactive_sessions:
                        await self.end_chat_session(session_id, "Session timeout")

                    # Auto-save active sessions
                    for session in self.active_sessions.values():
                        await self._auto_save_session(session)

                    # Wait before next cycle
                    await asyncio.sleep(60)  # Check every minute

                except Exception as e:
                    logger.error(f"Error in session management loop: {e}")
                    await asyncio.sleep(60)

        except asyncio.CancelledError:
            logger.info("Session management loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in session management loop: {e}")

    async def _therapeutic_monitoring_loop(self):
        """Background task for therapeutic monitoring and interventions."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Monitor therapeutic progress for all active sessions
                    for session_id, session in self.active_sessions.items():
                        therapeutic_context = self.therapeutic_contexts.get(session_id)
                        if therapeutic_context:
                            await self._monitor_therapeutic_progress(session, therapeutic_context)

                    # Check for intervention opportunities
                    await self._check_intervention_opportunities()

                    # Update therapeutic metrics
                    await self._update_therapeutic_metrics()

                    # Wait before next monitoring cycle
                    await asyncio.sleep(300)  # 5 minutes

                except Exception as e:
                    logger.error(f"Error in therapeutic monitoring loop: {e}")
                    await asyncio.sleep(60)

        except asyncio.CancelledError:
            logger.info("Therapeutic monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in therapeutic monitoring loop: {e}")

    async def _performance_monitoring_loop(self):
        """Background task for performance monitoring and optimization."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Update system availability
                    self.chat_system_metrics["system_availability"] = 1.0 if self.status == "running" else 0.0

                    # Monitor response times
                    await self._monitor_response_times()

                    # Check system resources
                    await self._monitor_system_resources()

                    # Update performance metrics
                    await self._update_performance_metrics()

                    # Wait before next monitoring cycle
                    await asyncio.sleep(120)  # 2 minutes

                except Exception as e:
                    logger.error(f"Error in performance monitoring loop: {e}")
                    await asyncio.sleep(60)

        except asyncio.CancelledError:
            logger.info("Performance monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in performance monitoring loop: {e}")

    # Core helper methods
    async def _create_therapeutic_context(self, user_id: str, session_id: str) -> TherapeuticContext:
        """Create therapeutic context for user session."""
        context = TherapeuticContext(
            user_id=user_id,
            session_id=session_id,
            time_of_day=datetime.utcnow().strftime("%H:%M"),
        )

        # Get user personalization data if available
        if self.personalization_engine:
            try:
                user_profile = await self.personalization_engine.get_user_profile(user_id)
                if user_profile:
                    context.therapeutic_preferences = getattr(user_profile, 'therapeutic_preferences', {})
                    context.preferred_therapeutic_approaches = [
                        TherapeuticFramework.CBT,  # Default frameworks
                        TherapeuticFramework.MINDFULNESS
                    ]
            except Exception as e:
                logger.warning(f"Could not load user personalization data: {e}")

        return context

    async def _create_conversation_flow(self, session_id: str, therapeutic_goals: list[str]) -> ConversationFlow:
        """Create conversation flow for session."""
        flow = ConversationFlow(
            session_id=session_id,
            therapeutic_objectives=therapeutic_goals
        )

        # Select appropriate flow template based on goals
        if any("crisis" in goal.lower() for goal in therapeutic_goals):
            template = self.conversation_flow_templates["crisis_intervention"]
        elif len(therapeutic_goals) == 0:
            template = self.conversation_flow_templates["initial_assessment"]
        else:
            template = self.conversation_flow_templates["therapeutic_session"]

        flow.conversation_stages = template["stages"]
        return flow

    async def _generate_welcome_message(self, session: ChatSession, context: TherapeuticContext) -> ChatMessage:
        """Generate personalized welcome message."""
        welcome_templates = self.therapeutic_templates["welcome_messages"]
        welcome_text = welcome_templates[0]  # Use first template for now

        # Personalize based on context
        if context.therapeutic_goals:
            welcome_text += f" I see we'll be working on {', '.join(context.therapeutic_goals[:2])} today."

        return ChatMessage(
            session_id=session.session_id,
            user_id=session.user_id,
            message_type=MessageType.THERAPEUTIC_RESPONSE,
            content=welcome_text,
            therapeutic_context={"message_type": "welcome", "personalized": True}
        )

    async def _add_message_to_session(self, session_id: str, message: ChatMessage):
        """Add message to session history."""
        session = self.active_sessions.get(session_id)
        if session:
            session.messages.append(message)
            session.message_count += 1
            session.last_activity = datetime.utcnow()

            # Store in message history
            self.message_history[session_id].append(message)

    async def _analyze_message_content(self, message: ChatMessage, context: TherapeuticContext):
        """Analyze message content for therapeutic indicators."""
        content = message.content.lower()

        # Simple emotional analysis
        emotional_indicators = {}

        # Positive emotions
        positive_words = ["happy", "good", "better", "excited", "grateful", "hopeful"]
        positive_score = sum(1 for word in positive_words if word in content) / len(positive_words)
        emotional_indicators["positive"] = positive_score

        # Negative emotions
        negative_words = ["sad", "angry", "frustrated", "worried", "anxious", "depressed"]
        negative_score = sum(1 for word in negative_words if word in content) / len(negative_words)
        emotional_indicators["negative"] = negative_score

        # Crisis indicators
        crisis_words = ["suicide", "kill", "die", "hurt", "harm", "end it all", "can't take", "want to end"]
        crisis_score = sum(1 for word in crisis_words if word in content)
        if crisis_score > 0:
            crisis_score = min(crisis_score / len(crisis_words) + 0.3, 1.0)  # Boost crisis score
        emotional_indicators["crisis"] = crisis_score

        message.emotional_indicators = emotional_indicators

        # Update therapeutic context
        context.emotional_state = emotional_indicators
        context.stress_level = negative_score

    async def _assess_crisis_risk(self, message: ChatMessage, context: TherapeuticContext) -> bool:
        """Assess crisis risk from message content."""
        crisis_score = message.emotional_indicators.get("crisis", 0.0)

        # Use emotional safety system if available
        if self.therapeutic_systems.get("emotional_safety_system"):
            try:
                safety_system = self.therapeutic_systems["emotional_safety_system"]
                risk_assessment = await safety_system.assess_crisis_risk(
                    user_id=message.user_id,
                    message_content=message.content,
                    context=context.session_context
                )
                crisis_score = max(crisis_score, risk_assessment.get("risk_level", 0.0))
            except Exception as e:
                logger.warning(f"Could not assess crisis risk: {e}")

        message.crisis_risk_level = crisis_score
        context.crisis_risk_assessment = {"risk_level": crisis_score, "timestamp": datetime.utcnow()}

        return crisis_score > 0.3  # Threshold for crisis intervention

    async def _generate_crisis_response(self, message: ChatMessage, context: TherapeuticContext) -> ChatMessage:
        """Generate crisis intervention response."""
        crisis_templates = self.therapeutic_templates["crisis_responses"]
        response_text = crisis_templates[0]  # Use first template

        # Use emotional safety system if available
        if self.therapeutic_systems.get("emotional_safety_system"):
            try:
                safety_system = self.therapeutic_systems["emotional_safety_system"]
                intervention = await safety_system.provide_crisis_intervention(
                    user_id=message.user_id,
                    crisis_context=context.crisis_risk_assessment
                )
                response_text = intervention.get("intervention_message", response_text)
            except Exception as e:
                logger.warning(f"Could not generate crisis intervention: {e}")

        self.chat_system_metrics["crisis_interventions"] += 1

        return ChatMessage(
            session_id=message.session_id,
            user_id=message.user_id,
            message_type=MessageType.CRISIS_INTERVENTION,
            content=response_text,
            therapeutic_context={"crisis_intervention": True, "risk_level": message.crisis_risk_level},
            response_priority=ResponsePriority.CRISIS,
            requires_human_review=True
        )

    async def _generate_therapeutic_response(
        self,
        message: ChatMessage,
        context: TherapeuticContext,
        flow: ConversationFlow
    ) -> ChatMessage:
        """Generate therapeutic response based on context and flow."""
        # Determine appropriate therapeutic framework
        framework = self._select_therapeutic_framework(message, context)

        # Generate response using selected framework
        response_generator = self.response_generators.get(framework, self._generate_default_response)
        response_text = await response_generator(message, context, flow)

        # Use therapeutic integration system if available
        if self.therapeutic_systems.get("therapeutic_integration_system"):
            try:
                integration_system = self.therapeutic_systems["therapeutic_integration_system"]
                enhanced_response = await integration_system.generate_therapeutic_response(
                    user_message=message.content,
                    therapeutic_context=context.__dict__,
                    framework=framework.value
                )
                response_text = enhanced_response.get("response_text", response_text)
            except Exception as e:
                logger.warning(f"Could not enhance therapeutic response: {e}")

        self.chat_system_metrics["therapeutic_interventions"] += 1

        return ChatMessage(
            session_id=message.session_id,
            user_id=message.user_id,
            message_type=MessageType.THERAPEUTIC_RESPONSE,
            content=response_text,
            therapeutic_context={"framework": framework.value, "generated": True},
            therapeutic_frameworks=[framework],
            confidence_score=0.8
        )

    def _select_therapeutic_framework(self, message: ChatMessage, context: TherapeuticContext) -> TherapeuticFramework:
        """Select appropriate therapeutic framework for response."""
        # Enhanced framework selection based on content and context
        content = message.content.lower()

        # Narrative therapy keywords (highest priority for story-based content)
        narrative_keywords = [
            "story", "narrative", "tale", "chapter", "plot", "character", "protagonist",
            "identity", "meaning", "purpose", "values", "who i am", "define me",
            "externalize", "separate from", "outside of me", "not me", "the problem",
            "rewrite", "different ending", "new chapter", "alternative story", "preferred story",
            "exception", "times when", "different experience", "when it wasn't", "unique outcome",
            "witness", "audience", "tell others", "share my story", "others would say",
            "journey", "path", "crossroads", "turning point", "transformation"
        ]

        if any(word in content for word in narrative_keywords):
            return TherapeuticFramework.NARRATIVE
        elif any(word in content for word in ["think", "thought", "believe", "assumption"]):
            return TherapeuticFramework.CBT
        elif any(word in content for word in ["feel", "emotion", "overwhelmed", "intense"]):
            return TherapeuticFramework.DBT
        elif any(word in content for word in ["mindful", "present", "meditation", "breathing"]):
            return TherapeuticFramework.MINDFULNESS
        elif any(word in content for word in ["goal", "solution", "what works", "strength"]):
            return TherapeuticFramework.SOLUTION_FOCUSED
        else:
            # Use preferred framework from context or default to CBT
            if context.preferred_therapeutic_approaches:
                return context.preferred_therapeutic_approaches[0]
            return TherapeuticFramework.CBT

    # Enhanced response generators using template system
    async def _generate_cbt_response(self, message: ChatMessage, context: TherapeuticContext, flow: ConversationFlow) -> str:
        """Generate CBT-based therapeutic response."""
        return self._get_framework_response_template(TherapeuticFramework.CBT)

    async def _generate_dbt_response(self, message: ChatMessage, context: TherapeuticContext, flow: ConversationFlow) -> str:
        """Generate DBT-based therapeutic response."""
        return self._get_framework_response_template(TherapeuticFramework.DBT)

    async def _generate_mindfulness_response(self, message: ChatMessage, context: TherapeuticContext, flow: ConversationFlow) -> str:
        """Generate mindfulness-based therapeutic response."""
        return self._get_framework_response_template(TherapeuticFramework.MINDFULNESS)

    async def _generate_default_response(self, message: ChatMessage, context: TherapeuticContext, flow: ConversationFlow) -> str:
        """Generate default therapeutic response."""
        import random
        empathy_responses = self.therapeutic_templates["empathy_responses"]
        return random.choice(empathy_responses) + " Can you tell me more about what you're experiencing?"

    async def _generate_act_response(self, message: ChatMessage, context: TherapeuticContext, flow: ConversationFlow) -> str:
        """Generate ACT-based therapeutic response."""
        return self._get_framework_response_template(TherapeuticFramework.ACT)

    async def _generate_humanistic_response(self, message: ChatMessage, context: TherapeuticContext, flow: ConversationFlow) -> str:
        """Generate humanistic therapeutic response."""
        return self._get_framework_response_template(TherapeuticFramework.HUMANISTIC)

    async def _generate_psychodynamic_response(self, message: ChatMessage, context: TherapeuticContext, flow: ConversationFlow) -> str:
        """Generate psychodynamic therapeutic response."""
        return self._get_framework_response_template(TherapeuticFramework.PSYCHODYNAMIC)

    async def _generate_solution_focused_response(self, message: ChatMessage, context: TherapeuticContext, flow: ConversationFlow) -> str:
        """Generate solution-focused therapeutic response."""
        return self._get_framework_response_template(TherapeuticFramework.SOLUTION_FOCUSED)

    async def _generate_narrative_response(self, message: ChatMessage, context: TherapeuticContext, flow: ConversationFlow) -> str:
        """Generate enhanced narrative therapy response with story engagement."""
        # Detect story context and narrative elements
        story_context = self._detect_story_context(message)

        if story_context["has_narrative_elements"]:
            # Extract narrative elements for deeper analysis
            narrative_elements = self._extract_narrative_elements(message, story_context)

            # Track narrative progression
            self._track_narrative_progression(message.session_id, narrative_elements)

            # Determine response approach based on conversation flow and story development
            if hasattr(self, 'narrative_tracking') and message.session_id in self.narrative_tracking:
                session_narrative = self.narrative_tracking[message.session_id]
                coherence_score = session_narrative.get("narrative_coherence_score", 0.0)

                # Use different approaches based on narrative development
                if coherence_score < 0.3:
                    # Early story development - use story starters
                    templates = self.therapeutic_templates["interactive_storytelling"]["story_starters"]
                elif coherence_score < 0.6:
                    # Mid-story development - use development prompts
                    templates = self.therapeutic_templates["interactive_storytelling"]["story_development"]
                else:
                    # Well-developed story - use deepening or reflection
                    import random
                    template_categories = ["story_deepening", "story_reflection"]
                    category = random.choice(template_categories)
                    templates = self.therapeutic_templates["interactive_storytelling"][category]

                import random
                base_response = random.choice(templates)

                # Add therapeutic intervention if appropriate
                if coherence_score > 0.5:
                    intervention = self._apply_narrative_therapeutic_interventions(message, story_context, narrative_elements)
                    base_response += f"\n\n{intervention}"

                return base_response
            else:
                # First narrative interaction - use collaborative approach
                return self._facilitate_story_co_creation(message, story_context, narrative_elements)
        else:
            # No significant narrative elements - use standard narrative therapy response
            return self._get_framework_response_template(TherapeuticFramework.NARRATIVE)

    async def _update_conversation_flow(self, flow: ConversationFlow, user_message: ChatMessage, response_message: ChatMessage):
        """Update conversation flow based on interaction."""
        # Simple flow progression
        if flow.current_stage < len(flow.conversation_stages) - 1:
            flow.conversation_stages[flow.current_stage]
            # Check if stage objectives are met (simplified)
            if len(user_message.content) > 50:  # Simple engagement check
                flow.stage_completion[flow.current_stage] = True
                flow.current_stage += 1

    async def _update_therapeutic_context(self, context: TherapeuticContext, user_message: ChatMessage, response_message: ChatMessage):
        """Update therapeutic context based on interaction."""
        # Update emotional journey
        context.emotional_journey.append({
            "timestamp": user_message.timestamp.isoformat(),
            "emotional_state": user_message.emotional_indicators,
            "message_content": user_message.content[:100],  # First 100 chars
        })

        # Update engagement level based on message length and emotional indicators
        engagement_score = min(len(user_message.content) / 200, 1.0)  # Normalize by 200 chars
        positive_emotion = user_message.emotional_indicators.get("positive", 0.0)
        context.engagement_level = (engagement_score + positive_emotion) / 2

    async def _track_message_engagement(self, session: ChatSession, user_message: ChatMessage, response_message: ChatMessage):
        """Track engagement metrics for messages."""
        if self.engagement_system:
            try:
                session_data = {
                    "duration": (datetime.utcnow() - session.started_at).total_seconds() / 60,
                    "message_count": session.message_count,
                    "engagement_indicators": user_message.emotional_indicators,
                    "response_time_ms": response_message.processing_time_ms
                }

                therapeutic_context = {
                    "therapeutic_goals": session.session_goals,
                    "conversation_state": session.conversation_state.value,
                    "frameworks_used": [fw.value for fw in response_message.therapeutic_frameworks]
                }

                await self.engagement_system.track_user_engagement(
                    user_id=session.user_id,
                    session_data=session_data,
                    therapeutic_context=therapeutic_context
                )
            except Exception as e:
                logger.warning(f"Could not track engagement: {e}")

    async def _generate_session_summary(self, session: ChatSession) -> dict[str, Any]:
        """Generate comprehensive session summary."""
        summary = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "duration_minutes": session.session_duration.total_seconds() / 60,
            "message_count": session.message_count,
            "therapeutic_goals": session.session_goals,
            "conversation_state": session.conversation_state.value,
            "key_topics": [],  # Would be extracted from message analysis
            "emotional_journey": [],  # Would be compiled from context
            "therapeutic_progress": {},  # Would be assessed from interactions
            "recommendations": [],  # Would be generated based on session
            "summary_text": f"Session completed with {session.message_count} messages over {session.session_duration.total_seconds() / 60:.1f} minutes."
        }

        return summary

    async def _generate_therapeutic_recommendations(self, session: ChatSession, context: TherapeuticContext) -> list[str]:
        """Generate therapeutic recommendations based on session."""
        recommendations = []

        # Simple recommendation logic
        if context.stress_level > 0.5:
            recommendations.append("Consider practicing stress reduction techniques")

        if context.engagement_level < 0.3:
            recommendations.append("Explore ways to increase engagement in therapeutic activities")

        if session.message_count < 5:
            recommendations.append("Consider longer sessions for deeper therapeutic work")

        return recommendations

    # Placeholder methods for background tasks
    async def _process_queued_message(self, message_data):
        """Process message from queue."""
        pass

    async def _auto_save_session(self, session):
        """Auto-save session data."""
        pass

    async def _monitor_therapeutic_progress(self, session, context):
        """Monitor therapeutic progress."""
        pass

    async def _check_intervention_opportunities(self):
        """Check for intervention opportunities."""
        pass

    async def _update_therapeutic_metrics(self):
        """Update therapeutic metrics."""
        pass

    async def _monitor_response_times(self):
        """Monitor system response times."""
        pass

    async def _monitor_system_resources(self):
        """Monitor system resources."""
        pass

    async def _update_performance_metrics(self):
        """Update performance metrics."""
        pass

    async def _archive_session(self, session):
        """Archive completed session."""
        pass

    async def _finalize_session_engagement(self, session):
        """Finalize engagement metrics for session."""
        pass

    # Message processor placeholder methods
    async def _process_user_message_content(self, message):
        """Process user message content."""
        pass

    async def _process_therapeutic_response(self, message):
        """Process therapeutic response."""
        pass

    async def _process_system_message(self, message):
        """Process system message."""
        pass

    async def _process_crisis_intervention(self, message):
        """Process crisis intervention message."""
        pass

    async def _process_achievement_notification(self, message):
        """Process achievement notification."""
        pass

    async def _process_progress_update(self, message):
        """Process progress update."""
        pass

    async def _process_therapeutic_suggestion(self, message):
        """Process therapeutic suggestion."""
        pass

    async def _process_session_summary(self, message):
        """Process session summary."""
        pass

    # Intervention handler placeholder methods
    async def _handle_crisis_intervention(self, context):
        """Handle crisis intervention."""
        pass

    async def _handle_emotional_support(self, context):
        """Handle emotional support."""
        pass

    async def _handle_skill_practice(self, context):
        """Handle skill practice."""
        pass

    async def _handle_goal_setting(self, context):
        """Handle goal setting."""
        pass

    async def _handle_progress_review(self, context):
        """Handle progress review."""
        pass

    async def _handle_therapeutic_homework(self, context):
        """Handle therapeutic homework."""
        pass

    async def _handle_mindfulness_exercise(self, context):
        """Handle mindfulness exercise."""
        pass

    async def _handle_cognitive_restructuring(self, context):
        """Handle cognitive restructuring."""
        pass
