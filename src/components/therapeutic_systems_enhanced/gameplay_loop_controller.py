"""
Production Therapeutic GameplayLoopController Implementation

This module provides production-ready session lifecycle management with seamless
integration of all therapeutic systems for comprehensive therapeutic gameplay
orchestration.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class SessionPhase(Enum):
    """Phases of a therapeutic gameplay session."""

    INITIALIZATION = "initialization"
    CHARACTER_CREATION = "character_creation"
    THERAPEUTIC_ASSESSMENT = "therapeutic_assessment"
    ACTIVE_GAMEPLAY = "active_gameplay"
    SKILL_PRACTICE = "skill_practice"
    REFLECTION = "reflection"
    INTEGRATION = "integration"
    CONCLUSION = "conclusion"
    WRAP_UP = "wrap_up"


class SessionStatus(Enum):
    """Status of a therapeutic session."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    ERROR = "error"


@dataclass
class SessionConfiguration:
    """Configuration for a therapeutic gameplay session."""

    session_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    therapeutic_goals: list[str] = field(default_factory=list)
    target_duration_minutes: int = 45
    difficulty_level: str = "moderate"
    framework_preferences: list[str] = field(default_factory=list)
    character_preferences: dict[str, Any] = field(default_factory=dict)
    safety_monitoring_enabled: bool = True
    adaptive_difficulty_enabled: bool = True
    auto_save_enabled: bool = True
    auto_save_interval_minutes: int = 5


@dataclass
class SessionState:
    """Current state of a therapeutic gameplay session."""

    session_id: str
    user_id: str
    status: SessionStatus
    current_phase: SessionPhase
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    # Therapeutic context
    therapeutic_goals: list[str] = field(default_factory=list)
    character_id: str | None = None
    current_scenario_id: str | None = None

    # Progress tracking
    choices_made: int = 0
    consequences_processed: int = 0
    milestones_achieved: int = 0
    therapeutic_value_accumulated: float = 0.0

    # System states
    emotional_safety_status: dict[str, Any] = field(default_factory=dict)
    difficulty_level: str = "moderate"
    character_attributes: dict[str, float] = field(default_factory=dict)

    # Session metrics
    session_duration_minutes: float = 0.0
    engagement_score: float = 0.0
    therapeutic_progress_score: float = 0.0


@dataclass
class SessionOutcome:
    """Outcome summary of a completed therapeutic session."""

    session_id: str
    user_id: str
    duration_minutes: float
    therapeutic_goals_addressed: list[str]
    milestones_achieved: list[str]
    character_progression: dict[str, float]
    therapeutic_value_total: float
    engagement_metrics: dict[str, float]
    safety_incidents: int
    recommendations_for_next_session: list[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


class TherapeuticGameplayLoopController:
    """
    Production GameplayLoopController that provides comprehensive session
    lifecycle management with seamless integration of all therapeutic systems.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the therapeutic gameplay loop controller."""
        self.config = config or {}

        # Session tracking
        self.active_sessions = {}  # session_id -> SessionState
        self.session_configurations = {}  # session_id -> SessionConfiguration
        self.session_outcomes = {}  # session_id -> SessionOutcome

        # Therapeutic system references (will be injected)
        self.consequence_system = None
        self.emotional_safety_system = None
        self.adaptive_difficulty_engine = None
        self.character_development_system = None
        self.therapeutic_integration_system = None

        # Adventure enhancement system
        self.adventure_enhancer = None

        # Configuration parameters
        self.max_concurrent_sessions = self.config.get("max_concurrent_sessions", 100)
        self.session_timeout_minutes = self.config.get("session_timeout_minutes", 120)
        self.auto_save_enabled = self.config.get("auto_save_enabled", True)
        self.safety_monitoring_interval = self.config.get(
            "safety_monitoring_interval", 30
        )

        # Performance metrics
        self.metrics = {
            "sessions_started": 0,
            "sessions_completed": 0,
            "sessions_terminated": 0,
            "total_therapeutic_value": 0.0,
            "average_session_duration": 0.0,
            "safety_interventions": 0,
        }

        logger.info("TherapeuticGameplayLoopController initialized")

    async def initialize(self):
        """Initialize the gameplay loop controller."""
        # Any async initialization can go here
        logger.info("TherapeuticGameplayLoopController initialization complete")

    def inject_therapeutic_systems(
        self,
        consequence_system=None,
        emotional_safety_system=None,
        adaptive_difficulty_engine=None,
        character_development_system=None,
        therapeutic_integration_system=None,
        adventure_enhancer=None,
    ):
        """Inject therapeutic system dependencies."""
        self.consequence_system = consequence_system
        self.emotional_safety_system = emotional_safety_system
        self.adaptive_difficulty_engine = adaptive_difficulty_engine
        self.character_development_system = character_development_system
        self.therapeutic_integration_system = therapeutic_integration_system
        self.adventure_enhancer = adventure_enhancer

        logger.info("Therapeutic systems injected into GameplayLoopController")

    async def start_session(
        self,
        user_id: str,
        session_config: SessionConfiguration | None = None,
        therapeutic_goals: list[str] | None = None,
    ) -> SessionState:
        """
        Start a new therapeutic gameplay session with comprehensive initialization.

        This method provides the core interface for session lifecycle management,
        integrating all therapeutic systems for a seamless user experience.

        Args:
            user_id: Unique identifier for the user
            session_config: Optional session configuration
            therapeutic_goals: List of therapeutic goals for the session

        Returns:
            SessionState representing the initialized session
        """
        try:
            start_time = datetime.utcnow()

            # Create or use provided configuration
            if session_config is None:
                session_config = SessionConfiguration(
                    user_id=user_id,
                    therapeutic_goals=therapeutic_goals or [],
                )

            session_id = session_config.session_id

            # Check session limits
            if len(self.active_sessions) >= self.max_concurrent_sessions:
                raise RuntimeError("Maximum concurrent sessions reached")

            # Create initial session state
            session_state = SessionState(
                session_id=session_id,
                user_id=user_id,
                status=SessionStatus.INITIALIZING,
                current_phase=SessionPhase.INITIALIZATION,
                therapeutic_goals=session_config.therapeutic_goals,
                difficulty_level=session_config.difficulty_level,
            )

            # Store session configuration and state
            self.session_configurations[session_id] = session_config
            self.active_sessions[session_id] = session_state

            # Phase 1: Initialize therapeutic systems
            await self._initialize_therapeutic_systems(session_state, session_config)

            # Phase 2: Character creation
            await self._handle_character_creation_phase(session_state, session_config)

            # Phase 3: Therapeutic assessment
            await self._handle_therapeutic_assessment_phase(
                session_state, session_config
            )

            # Phase 4: Transition to active gameplay
            session_state.status = SessionStatus.ACTIVE
            session_state.current_phase = SessionPhase.ACTIVE_GAMEPLAY
            session_state.last_updated = datetime.utcnow()

            # Update metrics
            self.metrics["sessions_started"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Started therapeutic session {session_id} for user {user_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return session_state

        except Exception as e:
            logger.error(f"Error starting session for user {user_id}: {e}")

            # Clean up failed session
            if "session_id" in locals():
                self.active_sessions.pop(session_id, None)
                self.session_configurations.pop(session_id, None)

            # Return error state
            error_session = SessionState(
                session_id=str(uuid4()),
                user_id=user_id,
                status=SessionStatus.ERROR,
                current_phase=SessionPhase.INITIALIZATION,
            )
            return error_session

    async def process_user_choice(
        self,
        session_id: str,
        user_choice: str,
        choice_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process a user choice through all therapeutic systems.

        This method coordinates all therapeutic systems to process user choices
        and generate comprehensive therapeutic responses.

        Args:
            session_id: Session identifier
            user_choice: User's choice or input
            choice_context: Additional context for the choice

        Returns:
            Comprehensive response including consequences, safety assessment, and progression
        """
        try:
            start_time = datetime.utcnow()

            # Get session state
            session_state = self.active_sessions.get(session_id)
            if not session_state or session_state.status != SessionStatus.ACTIVE:
                raise ValueError(f"Invalid or inactive session: {session_id}")

            # Safety check first
            safety_result = await self._assess_safety(
                session_state, user_choice, choice_context
            )
            if safety_result.get("crisis_detected", False):
                return await self._handle_crisis_intervention(
                    session_state, safety_result
                )

            # Process choice through consequence system
            consequence_result = await self._process_choice_consequence(
                session_state, user_choice, choice_context
            )

            # Update character development
            character_update = await self._update_character_development(
                session_state, consequence_result
            )

            # Adjust difficulty if needed
            difficulty_adjustment = await self._adjust_difficulty(
                session_state, consequence_result
            )

            # Generate therapeutic integration
            therapeutic_integration = await self._integrate_therapeutic_content(
                session_state, consequence_result
            )

            # Update session state
            session_state.choices_made += 1
            session_state.consequences_processed += 1
            session_state.therapeutic_value_accumulated += consequence_result.get(
                "therapeutic_value", 0.0
            )
            session_state.last_updated = datetime.utcnow()

            # Check for milestones
            milestone_check = await self._check_milestones(
                session_state, consequence_result
            )

            # Compile comprehensive response
            response = {
                "session_id": session_id,
                "choice_processed": True,
                "safety_assessment": safety_result,
                "consequence": consequence_result,
                "character_update": character_update,
                "difficulty_adjustment": difficulty_adjustment,
                "therapeutic_integration": therapeutic_integration,
                "milestone_achieved": milestone_check,
                "session_progress": {
                    "choices_made": session_state.choices_made,
                    "therapeutic_value": session_state.therapeutic_value_accumulated,
                    "engagement_score": session_state.engagement_score,
                },
                "processing_time": (datetime.utcnow() - start_time).total_seconds(),
            }

            # Enhance response with adventure elements if adventure enhancer is available
            if self.adventure_enhancer:
                try:
                    response = self.adventure_enhancer.enhance_choice_response(
                        session_id=session_id,
                        user_choice=user_choice,
                        choice_context=choice_context or {},
                        base_response=response,
                    )
                except Exception as e:
                    logger.warning(
                        f"Adventure enhancement failed for session {session_id}: {e}"
                    )
                    # Continue with base response if enhancement fails

            logger.info(
                f"Processed choice for session {session_id} in {response['processing_time']:.3f}s"
            )

            return response

        except Exception as e:
            logger.error(f"Error processing choice for session {session_id}: {e}")
            return {
                "session_id": session_id,
                "choice_processed": False,
                "error": str(e),
                "safety_fallback": True,
            }

    async def complete_session(
        self,
        session_id: str,
        completion_reason: str = "user_completed",
    ) -> SessionOutcome:
        """
        Complete a therapeutic session and generate comprehensive outcome summary.

        Args:
            session_id: Session identifier
            completion_reason: Reason for session completion

        Returns:
            SessionOutcome with comprehensive session summary
        """
        try:
            start_time = datetime.utcnow()

            # Get session state
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                raise ValueError(f"Session {session_id} not found")

            # Calculate session duration
            session_duration = (
                datetime.utcnow() - session_state.created_at
            ).total_seconds() / 60.0

            # Generate character progression summary
            character_progression = await self._generate_character_progression_summary(
                session_state
            )

            # Generate therapeutic recommendations
            recommendations = await self._generate_session_recommendations(
                session_state
            )

            # Create session outcome
            outcome = SessionOutcome(
                session_id=session_id,
                user_id=session_state.user_id,
                duration_minutes=session_duration,
                therapeutic_goals_addressed=session_state.therapeutic_goals,
                milestones_achieved=[],  # Will be populated by milestone check
                character_progression=character_progression,
                therapeutic_value_total=session_state.therapeutic_value_accumulated,
                engagement_metrics={
                    "choices_made": session_state.choices_made,
                    "engagement_score": session_state.engagement_score,
                    "therapeutic_progress_score": session_state.therapeutic_progress_score,
                },
                safety_incidents=session_state.emotional_safety_status.get(
                    "incidents", 0
                ),
                recommendations_for_next_session=recommendations,
            )

            # Update session state
            session_state.status = SessionStatus.COMPLETED
            session_state.current_phase = SessionPhase.CONCLUSION
            session_state.session_duration_minutes = session_duration
            session_state.last_updated = datetime.utcnow()

            # Store outcome
            self.session_outcomes[session_id] = outcome

            # Clean up active session
            self.active_sessions.pop(session_id, None)
            self.session_configurations.pop(session_id, None)

            # Update metrics
            self.metrics["sessions_completed"] += 1
            self.metrics["total_therapeutic_value"] += outcome.therapeutic_value_total
            self._update_average_session_duration(session_duration)

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Completed session {session_id} (duration: {session_duration:.1f}min) "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return outcome

        except Exception as e:
            logger.error(f"Error completing session {session_id}: {e}")

            # Return error outcome
            return SessionOutcome(
                session_id=session_id,
                user_id=session_state.user_id if session_state else "unknown",
                duration_minutes=0.0,
                therapeutic_goals_addressed=[],
                milestones_achieved=[],
                character_progression={},
                therapeutic_value_total=0.0,
                engagement_metrics={},
                safety_incidents=0,
                recommendations_for_next_session=[
                    "Session ended with error - please try again"
                ],
            )

    # Helper methods for therapeutic system integration

    async def _initialize_therapeutic_systems(
        self, session_state: SessionState, session_config: SessionConfiguration
    ):
        """Initialize all therapeutic systems for the session."""
        try:
            # Initialize emotional safety monitoring
            if (
                self.emotional_safety_system
                and session_config.safety_monitoring_enabled
            ):
                safety_init = (
                    await self.emotional_safety_system.initialize_user_monitoring(
                        user_id=session_state.user_id,
                        session_id=session_state.session_id,
                        monitoring_level="standard",
                    )
                )
                session_state.emotional_safety_status = safety_init

            # Initialize adaptive difficulty
            if (
                self.adaptive_difficulty_engine
                and session_config.adaptive_difficulty_enabled
            ):
                await self.adaptive_difficulty_engine.initialize_user_profile(
                    user_id=session_state.user_id,
                    initial_difficulty=session_config.difficulty_level,
                    therapeutic_goals=session_config.therapeutic_goals,
                )

            logger.info(
                f"Therapeutic systems initialized for session {session_state.session_id}"
            )

        except Exception as e:
            logger.error(f"Error initializing therapeutic systems: {e}")

    async def _handle_character_creation_phase(
        self, session_state: SessionState, session_config: SessionConfiguration
    ):
        """Handle character creation phase of session initialization."""
        try:
            session_state.current_phase = SessionPhase.CHARACTER_CREATION

            if self.character_development_system:
                character = await self.character_development_system.create_character(
                    user_id=session_state.user_id,
                    session_id=session_state.session_id,
                    therapeutic_goals=session_config.therapeutic_goals,
                    character_preferences=session_config.character_preferences,
                )

                session_state.character_id = character.character_id
                session_state.character_attributes = character.attributes

                logger.info(
                    f"Character created for session {session_state.session_id}: {character.character_id}"
                )

        except Exception as e:
            logger.error(f"Error in character creation phase: {e}")

    async def _handle_therapeutic_assessment_phase(
        self, session_state: SessionState, session_config: SessionConfiguration
    ):
        """Handle therapeutic assessment phase of session initialization."""
        try:
            session_state.current_phase = SessionPhase.THERAPEUTIC_ASSESSMENT

            if self.therapeutic_integration_system:
                # Generate personalized recommendations
                recommendations = await self.therapeutic_integration_system.generate_personalized_recommendations(
                    user_id=session_state.user_id,
                    therapeutic_goals=session_config.therapeutic_goals,
                    character_data={
                        "character_id": session_state.character_id,
                        "attributes": session_state.character_attributes,
                    },
                )

                # Store recommendations in session context
                session_state.therapeutic_goals.extend(
                    [rec.framework.value for rec in recommendations[:3]]
                )

                logger.info(
                    f"Therapeutic assessment completed for session {session_state.session_id}"
                )

        except Exception as e:
            logger.error(f"Error in therapeutic assessment phase: {e}")

    async def _assess_safety(
        self,
        session_state: SessionState,
        user_input: str,
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Assess emotional safety of user input."""
        try:
            if self.emotional_safety_system:
                safety_result = await self.emotional_safety_system.assess_crisis_risk(
                    user_id=session_state.user_id,
                    user_input=user_input,
                    session_context=context,
                )
                return safety_result
            return {"crisis_detected": False, "safety_level": "standard"}

        except Exception as e:
            logger.error(f"Error in safety assessment: {e}")
            return {
                "crisis_detected": False,
                "safety_level": "standard",
                "error": str(e),
            }

    async def _handle_crisis_intervention(
        self, session_state: SessionState, safety_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle crisis intervention when safety issues are detected."""
        try:
            # Update session state
            session_state.current_phase = SessionPhase.CONCLUSION
            session_state.emotional_safety_status["incidents"] = (
                session_state.emotional_safety_status.get("incidents", 0) + 1
            )

            # Update metrics
            self.metrics["safety_interventions"] += 1

            # Return crisis intervention response
            return {
                "session_id": session_state.session_id,
                "choice_processed": False,
                "crisis_intervention": True,
                "safety_assessment": safety_result,
                "intervention_message": "We've detected you might be going through a difficult time. Let's focus on your wellbeing.",
                "support_resources": safety_result.get("support_resources", []),
                "session_paused": True,
            }

        except Exception as e:
            logger.error(f"Error handling crisis intervention: {e}")
            return {
                "session_id": session_state.session_id,
                "crisis_intervention": True,
                "error": "Crisis intervention system error",
            }

    async def _process_choice_consequence(
        self,
        session_state: SessionState,
        user_choice: str,
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Process user choice through consequence system."""
        try:
            if self.consequence_system:
                consequence = await self.consequence_system.process_choice_consequence(
                    user_id=session_state.user_id,
                    choice=user_choice,
                    scenario_context=context or {},
                )
                return consequence
            return {
                "consequence_text": "Your choice has been noted.",
                "therapeutic_value": 1.0,
                "character_impact": {},
            }

        except Exception as e:
            logger.error(f"Error processing choice consequence: {e}")
            return {
                "consequence_text": "Unable to process choice at this time.",
                "therapeutic_value": 0.0,
                "character_impact": {},
                "error": str(e),
            }

    async def _update_character_development(
        self, session_state: SessionState, consequence_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Update character development based on consequence."""
        try:
            if self.character_development_system and session_state.character_id:
                character_update = await self.character_development_system.apply_consequence_to_character(
                    character_id=session_state.character_id,
                    consequence_data=consequence_result,
                )

                # Update session state with new attributes
                if "updated_attributes" in character_update:
                    session_state.character_attributes.update(
                        character_update["updated_attributes"]
                    )

                return character_update
            return {
                "character_updated": False,
                "reason": "No character development system",
            }

        except Exception as e:
            logger.error(f"Error updating character development: {e}")
            return {"character_updated": False, "error": str(e)}

    async def _adjust_difficulty(
        self, session_state: SessionState, consequence_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Adjust difficulty based on user performance."""
        try:
            if self.adaptive_difficulty_engine:
                difficulty_adjustment = (
                    await self.adaptive_difficulty_engine.adjust_difficulty(
                        user_id=session_state.user_id,
                        performance_data={
                            "therapeutic_value": consequence_result.get(
                                "therapeutic_value", 0.0
                            ),
                            "engagement_level": session_state.engagement_score,
                            "choices_made": session_state.choices_made,
                        },
                    )
                )

                # Update session difficulty if changed
                if "new_difficulty" in difficulty_adjustment:
                    session_state.difficulty_level = difficulty_adjustment[
                        "new_difficulty"
                    ]

                return difficulty_adjustment
            return {
                "difficulty_adjusted": False,
                "current_difficulty": session_state.difficulty_level,
            }

        except Exception as e:
            logger.error(f"Error adjusting difficulty: {e}")
            return {"difficulty_adjusted": False, "error": str(e)}

    async def _integrate_therapeutic_content(
        self, session_state: SessionState, consequence_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Integrate therapeutic content based on session progress."""
        try:
            if self.therapeutic_integration_system:
                # Determine appropriate therapeutic framework
                framework_recommendation = await self.therapeutic_integration_system.generate_personalized_recommendations(
                    user_id=session_state.user_id,
                    therapeutic_goals=session_state.therapeutic_goals,
                    character_data={
                        "character_id": session_state.character_id,
                        "attributes": session_state.character_attributes,
                    },
                    user_progress={
                        "therapeutic_value": session_state.therapeutic_value_accumulated,
                        "choices_made": session_state.choices_made,
                    },
                )

                if framework_recommendation:
                    # Create therapeutic scenario
                    scenario = await self.therapeutic_integration_system.create_therapeutic_scenario(
                        user_id=session_state.user_id,
                        framework=framework_recommendation[0].framework,
                        scenario_type=framework_recommendation[0].scenario_type,
                        difficulty_level=session_state.difficulty_level,
                        character_data={
                            "character_id": session_state.character_id,
                            "attributes": session_state.character_attributes,
                        },
                    )

                    session_state.current_scenario_id = scenario.scenario_id

                    return {
                        "therapeutic_integration": True,
                        "framework": framework_recommendation[0].framework.value,
                        "scenario": {
                            "id": scenario.scenario_id,
                            "title": scenario.title,
                            "description": scenario.description,
                            "therapeutic_goals": scenario.therapeutic_goals,
                        },
                    }

            return {
                "therapeutic_integration": False,
                "reason": "No therapeutic integration system",
            }

        except Exception as e:
            logger.error(f"Error integrating therapeutic content: {e}")
            return {"therapeutic_integration": False, "error": str(e)}

    async def _check_milestones(
        self, session_state: SessionState, consequence_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Check for milestone achievements."""
        try:
            milestones_achieved = []

            # Check therapeutic value milestones
            if (
                session_state.therapeutic_value_accumulated >= 10.0
                and session_state.milestones_achieved == 0
            ):
                milestones_achieved.append("first_therapeutic_breakthrough")
                session_state.milestones_achieved += 1

            # Check choice engagement milestones
            if (
                session_state.choices_made >= 5
                and "engagement_milestone" not in milestones_achieved
            ):
                milestones_achieved.append("active_engagement")

            # Check character development milestones
            if self.character_development_system and session_state.character_id:
                try:
                    character_milestones = (
                        await self.character_development_system.check_milestones(
                            character_id=session_state.character_id
                        )
                    )
                    if (
                        character_milestones
                        and "new_milestones" in character_milestones
                    ):
                        milestones_achieved.extend(
                            character_milestones["new_milestones"]
                        )
                except Exception as e:
                    logger.debug(f"Error checking character milestones: {e}")

            return {
                "milestones_achieved": milestones_achieved,
                "total_milestones": session_state.milestones_achieved
                + len(milestones_achieved),
            }

        except Exception as e:
            logger.error(f"Error checking milestones: {e}")
            return {"milestones_achieved": [], "total_milestones": 0}

    async def _generate_character_progression_summary(
        self, session_state: SessionState
    ) -> dict[str, float]:
        """Generate character progression summary for session outcome."""
        try:
            if self.character_development_system and session_state.character_id:
                progression = await self.character_development_system.get_character_progression_summary(
                    character_id=session_state.character_id
                )
                return progression.get("attribute_changes", {})
            return session_state.character_attributes

        except Exception as e:
            logger.error(f"Error generating character progression summary: {e}")
            return {}

    async def _generate_session_recommendations(
        self, session_state: SessionState
    ) -> list[str]:
        """Generate recommendations for next session."""
        try:
            recommendations = []

            # Therapeutic value recommendations
            if session_state.therapeutic_value_accumulated < 5.0:
                recommendations.append(
                    "Focus on deeper therapeutic engagement in next session"
                )

            # Character development recommendations
            if session_state.character_attributes:
                lowest_attribute = min(
                    session_state.character_attributes.items(), key=lambda x: x[1]
                )
                recommendations.append(
                    f"Consider working on {lowest_attribute[0]} development"
                )

            # Difficulty recommendations
            if session_state.choices_made < 3:
                recommendations.append("Try making more choices to increase engagement")
            elif session_state.choices_made > 10:
                recommendations.append(
                    "Great engagement! Consider exploring more complex scenarios"
                )

            # Therapeutic integration recommendations
            if self.therapeutic_integration_system:
                integration_recs = await self.therapeutic_integration_system.generate_personalized_recommendations(
                    user_id=session_state.user_id,
                    therapeutic_goals=session_state.therapeutic_goals,
                    user_progress={
                        "therapeutic_value": session_state.therapeutic_value_accumulated,
                        "session_count": 1,  # This would be tracked separately
                    },
                )

                if integration_recs:
                    recommendations.append(
                        f"Consider exploring {integration_recs[0].framework.value} approaches"
                    )

            return recommendations[:5]  # Limit to top 5 recommendations

        except Exception as e:
            logger.error(f"Error generating session recommendations: {e}")
            return ["Continue therapeutic journey in next session"]

    def _update_average_session_duration(self, session_duration: float):
        """Update average session duration metric."""
        try:
            current_avg = self.metrics.get("average_session_duration", 0.0)
            sessions_completed = self.metrics.get("sessions_completed", 1)

            # Calculate new average
            new_avg = (
                (current_avg * (sessions_completed - 1)) + session_duration
            ) / sessions_completed
            self.metrics["average_session_duration"] = new_avg

        except Exception as e:
            logger.error(f"Error updating average session duration: {e}")

    async def get_session_status(self, session_id: str) -> dict[str, Any] | None:
        """Get current status of a session."""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                return None

            return {
                "session_id": session_id,
                "user_id": session_state.user_id,
                "status": session_state.status.value,
                "current_phase": session_state.current_phase.value,
                "created_at": session_state.created_at.isoformat(),
                "last_updated": session_state.last_updated.isoformat(),
                "progress": {
                    "choices_made": session_state.choices_made,
                    "therapeutic_value": session_state.therapeutic_value_accumulated,
                    "milestones_achieved": session_state.milestones_achieved,
                    "engagement_score": session_state.engagement_score,
                },
                "character_id": session_state.character_id,
                "current_scenario_id": session_state.current_scenario_id,
                "difficulty_level": session_state.difficulty_level,
            }

        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return None

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the gameplay loop controller."""
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
                "adventure_enhancer": self.adventure_enhancer is not None,
            }

            systems_available = sum(systems_status.values())

            return {
                "status": "healthy" if systems_available >= 3 else "degraded",
                "active_sessions": len(self.active_sessions),
                "max_concurrent_sessions": self.max_concurrent_sessions,
                "therapeutic_systems": systems_status,
                "systems_available": f"{systems_available}/6",
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            logger.error(f"Error in gameplay loop controller health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_metrics(self) -> dict[str, Any]:
        """Get gameplay loop controller metrics."""
        return {
            **self.metrics,
            "active_sessions_count": len(self.active_sessions),
            "session_outcomes_stored": len(self.session_outcomes),
            "completion_rate": (
                self.metrics["sessions_completed"]
                / max(self.metrics["sessions_started"], 1)
            )
            * 100,
        }
