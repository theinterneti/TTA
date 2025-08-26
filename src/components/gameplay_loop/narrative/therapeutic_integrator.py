"""
Therapeutic Integrator for Narrative Engine

This module ensures therapeutic alignment, safety monitoring, and progress tracking
for therapeutic text adventures. Integrates with the therapeutic safety validation system.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from src.components.gameplay_loop.models.core import NarrativeScene
from src.components.gameplay_loop.services.session_state import SessionState
from src.components.therapeutic_safety import (
    ContentPayload, ValidationContext, ValidationResult,
    ContentType, ValidationScope, SafetyLevel, CrisisLevel, ValidationAction
)
from .emotional_safety_system import EmotionalSafetySystem, EmotionalState, DistressLevel


logger = logging.getLogger(__name__)


@dataclass
class TherapeuticContext:
    """Context for therapeutic integration."""
    session_id: str
    therapeutic_goals: List[str] = field(default_factory=list)
    current_focus: Optional[str] = None
    progress_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class SafetyMonitor:
    """Safety monitoring configuration."""
    monitor_id: str
    safety_level: str = "standard"
    risk_factors: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)


@dataclass
class ProgressTracker:
    """Progress tracking configuration."""
    tracker_id: str
    metrics: Dict[str, float] = field(default_factory=dict)
    milestones: List[str] = field(default_factory=list)


class TherapeuticIntegrator:
    """Integrates therapeutic elements into narrative with safety validation."""

    def __init__(self, narrative_engine):
        self.narrative_engine = narrative_engine
        self.safety_service = None  # Will be injected during initialization

        # Emotional safety system integration
        self.emotional_safety_system = EmotionalSafetySystem(narrative_engine.event_bus)

        # Therapeutic context tracking
        self.session_contexts: Dict[str, TherapeuticContext] = {}
        self.safety_monitors: Dict[str, SafetyMonitor] = {}
        self.progress_trackers: Dict[str, ProgressTracker] = {}

        # Safety validation metrics
        self.validation_count = 0
        self.safety_violations = 0
        self.crisis_interventions = 0
        self.emotional_interventions = 0

    async def initialize(self) -> None:
        """Initialize the therapeutic integrator."""
        logger.info("Initializing therapeutic integrator with safety validation...")

        # Try to get safety service from component system
        try:
            # This will be injected by the narrative engine during initialization
            if hasattr(self.narrative_engine, 'safety_service'):
                self.safety_service = self.narrative_engine.safety_service
                logger.info("Safety validation service connected")
            else:
                logger.warning("Safety validation service not available - using fallback validation")
        except Exception as e:
            logger.error(f"Failed to connect to safety service: {e}")

        logger.info("Therapeutic integrator initialized")

    def set_safety_service(self, safety_service) -> None:
        """Set the safety validation service."""
        self.safety_service = safety_service
        logger.info("Safety validation service injected into therapeutic integrator")

    async def initialize_session(self, session_state: SessionState) -> None:
        """Initialize therapeutic context for a session."""
        session_id = session_state.session_id

        # Create therapeutic context
        therapeutic_context = TherapeuticContext(
            session_id=session_id,
            therapeutic_goals=session_state.context.get("therapeutic_goals", []),
            current_focus=session_state.context.get("current_therapeutic_focus"),
            progress_metrics=session_state.context.get("progress_metrics", {})
        )
        self.session_contexts[session_id] = therapeutic_context

        # Create safety monitor
        safety_monitor = SafetyMonitor(
            monitor_id=f"safety_{session_id}",
            safety_level=session_state.context.get("safety_level", "standard"),
            risk_factors=session_state.context.get("risk_factors", []),
            protective_factors=session_state.context.get("protective_factors", [])
        )
        self.safety_monitors[session_id] = safety_monitor

        # Create progress tracker
        progress_tracker = ProgressTracker(
            tracker_id=f"progress_{session_id}",
            metrics=session_state.context.get("progress_metrics", {}),
            milestones=session_state.context.get("milestones", [])
        )
        self.progress_trackers[session_id] = progress_tracker

        logger.debug(f"Therapeutic context initialized for session: {session_id}")

    async def finalize_session(self, session_state: SessionState) -> None:
        """Finalize therapeutic context for a session."""
        session_id = session_state.session_id

        # Update session state with therapeutic progress
        if session_id in self.progress_trackers:
            tracker = self.progress_trackers[session_id]
            session_state.context["progress_metrics"] = tracker.metrics
            session_state.context["milestones"] = tracker.milestones

        # Clean up session data
        self.session_contexts.pop(session_id, None)
        self.safety_monitors.pop(session_id, None)
        self.progress_trackers.pop(session_id, None)

        logger.debug(f"Therapeutic context finalized for session: {session_id}")

    async def validate_scene_safety(self, session_state: SessionState, scene: NarrativeScene) -> bool:
        """Validate scene safety using the safety validation system."""
        if not self.safety_service:
            logger.warning("Safety service not available - using fallback validation")
            return await self._fallback_safety_validation(scene)

        try:
            # Create content payload from scene
            content = ContentPayload(
                content_text=scene.description,
                content_type=ContentType.NARRATIVE_SCENE,
                metadata={
                    "scene_id": scene.scene_id,
                    "scene_type": scene.scene_type,
                    "choices_count": len(scene.choices) if scene.choices else 0
                }
            )

            # Create validation context
            context = self._create_validation_context(session_state)

            # Perform validation
            result = await self.safety_service.validate_content(content, context)

            # Update metrics
            self.validation_count += 1

            # Process validation result
            is_safe = await self._process_validation_result(session_state, result)

            if not is_safe:
                self.safety_violations += 1
                logger.warning(f"Scene safety validation failed for session {session_state.session_id}")

            return is_safe

        except Exception as e:
            logger.error(f"Scene safety validation error: {e}")
            # Fall back to basic validation
            return await self._fallback_safety_validation(scene)

    async def validate_user_input_safety(self, session_state: SessionState, user_input: str) -> ValidationResult:
        """Validate user input for safety concerns."""
        if not self.safety_service:
            logger.warning("Safety service not available for user input validation")
            return None

        try:
            # Validate user input
            result = await self.safety_service.validate_user_input(
                user_input=user_input,
                user_id=session_state.user_id,
                session_id=session_state.session_id,
                validation_scope=ValidationScope.COMPREHENSIVE,
                timeout_ms=200
            )

            # Process crisis detection
            if result.crisis_level >= CrisisLevel.HIGH or result.immediate_intervention_needed:
                await self._handle_crisis_intervention(session_state, result)

            return result

        except Exception as e:
            logger.error(f"User input safety validation error: {e}")
            return None

    async def monitor_session_safety(self, session_state: SessionState) -> None:
        """Monitor ongoing session safety."""
        session_id = session_state.session_id

        if session_id not in self.safety_monitors:
            logger.warning(f"No safety monitor found for session: {session_id}")
            return

        safety_monitor = self.safety_monitors[session_id]

        # Check for safety indicators in session context
        recent_interactions = session_state.context.get("recent_interactions", [])
        if recent_interactions:
            # Analyze recent interactions for safety concerns
            await self._analyze_interaction_patterns(session_state, recent_interactions)

        # Update safety level based on session progress
        await self._update_safety_level(session_state, safety_monitor)

    def _create_validation_context(self, session_state: SessionState) -> ValidationContext:
        """Create validation context from session state."""
        therapeutic_context = self.session_contexts.get(session_state.session_id)
        safety_monitor = self.safety_monitors.get(session_state.session_id)

        return ValidationContext(
            user_id=session_state.user_id,
            session_id=session_state.session_id,
            validation_scope=ValidationScope.STANDARD,
            timeout_ms=200,
            user_therapeutic_goals=therapeutic_context.therapeutic_goals if therapeutic_context else [],
            user_risk_factors=safety_monitor.risk_factors if safety_monitor else [],
            current_safety_level=SafetyLevel.SAFE,  # Default, could be dynamic
            strict_mode=session_state.context.get("strict_safety_mode", False)
        )

    async def _process_validation_result(self, session_state: SessionState, result: ValidationResult) -> bool:
        """Process validation result and determine if content is safe."""
        # Check overall safety
        if result.action in [ValidationAction.REJECT, ValidationAction.BLOCK]:
            return False

        # Handle crisis detection
        if result.crisis_level >= CrisisLevel.HIGH or result.immediate_intervention_needed:
            await self._handle_crisis_intervention(session_state, result)
            return False  # Block content that triggers crisis intervention

        # Handle warnings and modifications
        if result.action == ValidationAction.FLAG_FOR_REVIEW:
            logger.warning(f"Content flagged for review in session {session_state.session_id}")
            # Could implement review queue here

        if result.action == ValidationAction.MODIFY:
            logger.info(f"Content modification suggested for session {session_state.session_id}")
            # Could implement content modification here

        return result.action in [ValidationAction.APPROVE, ValidationAction.WARN, ValidationAction.MODIFY]

    async def _handle_crisis_intervention(self, session_state: SessionState, result: ValidationResult) -> None:
        """Handle crisis intervention protocols."""
        self.crisis_interventions += 1

        logger.critical(f"Crisis intervention triggered for session {session_state.session_id}: "
                       f"Level {result.crisis_level}, Indicators: {result.crisis_indicators}")

        # Update session context with crisis information
        session_state.context["crisis_detected"] = True
        session_state.context["crisis_level"] = result.crisis_level.value
        session_state.context["crisis_indicators"] = result.crisis_indicators
        session_state.context["intervention_needed"] = result.immediate_intervention_needed

        # Could trigger additional crisis protocols here
        # - Notify human oversight
        # - Activate crisis resources
        # - Modify narrative flow

    async def _fallback_safety_validation(self, scene: NarrativeScene) -> bool:
        """Fallback safety validation when safety service is unavailable."""
        # Basic keyword-based safety check
        unsafe_keywords = [
            "suicide", "kill myself", "self-harm", "hurt myself",
            "violence", "attack", "harm others"
        ]

        text = scene.description.lower()
        for keyword in unsafe_keywords:
            if keyword in text:
                logger.warning(f"Fallback safety check detected unsafe keyword: {keyword}")
                return False

        return True

    async def _analyze_interaction_patterns(self, session_state: SessionState, interactions: List[Dict]) -> None:
        """Analyze interaction patterns for safety concerns."""
        # Simple pattern analysis - could be enhanced
        concerning_patterns = 0

        for interaction in interactions[-5:]:  # Check last 5 interactions
            if interaction.get("safety_concern", False):
                concerning_patterns += 1

        if concerning_patterns >= 3:
            logger.warning(f"Concerning interaction pattern detected in session {session_state.session_id}")
            session_state.context["safety_alert"] = True

    async def _update_safety_level(self, session_state: SessionState, safety_monitor: SafetyMonitor) -> None:
        """Update safety level based on session progress."""
        # Simple safety level adjustment - could be enhanced
        if session_state.context.get("crisis_detected", False):
            safety_monitor.safety_level = "high_risk"
        elif session_state.context.get("safety_alert", False):
            safety_monitor.safety_level = "elevated"
        else:
            safety_monitor.safety_level = "standard"

    async def monitor_emotional_safety(self, session_state: SessionState,
                                     interaction_data: Dict[str, Any]) -> None:
        """Monitor emotional safety during narrative interactions."""
        try:
            # Monitor emotional state
            snapshot = await self.emotional_safety_system.monitor_emotional_state(
                session_state, interaction_data
            )

            # Check for emotional distress requiring intervention
            if snapshot.is_distressed():
                self.emotional_interventions += 1

                # Update safety monitor if exists
                if session_state.session_id in self.safety_monitors:
                    safety_monitor = self.safety_monitors[session_state.session_id]
                    safety_monitor.safety_level = f"emotional_distress_{snapshot.distress_level.name.lower()}"
                    safety_monitor.risk_factors.extend(snapshot.trigger_indicators)
                    safety_monitor.protective_factors.extend(snapshot.protective_factors)

            # Detect triggers in content
            if "content" in interaction_data:
                triggers = await self.emotional_safety_system.detect_triggers(
                    interaction_data["content"], interaction_data
                )

                # Store triggers in session context for awareness
                if triggers:
                    session_state.context["detected_triggers"] = [
                        {
                            "category": trigger.category.value,
                            "intensity": trigger.intensity,
                            "suggested_interventions": [i.value for i in trigger.suggested_interventions]
                        }
                        for trigger in triggers
                    ]

        except Exception as e:
            logger.error(f"Failed to monitor emotional safety for session {session_state.session_id}: {e}")

    async def provide_emotional_support(self, session_state: SessionState,
                                      emotion: EmotionalState, intensity: float) -> Dict[str, Any]:
        """Provide targeted emotional support."""
        try:
            support_response = await self.emotional_safety_system.provide_emotional_regulation_support(
                session_state, emotion, intensity
            )

            # Update therapeutic context
            if session_state.session_id in self.session_contexts:
                context = self.session_contexts[session_state.session_id]
                context.current_focus = f"emotional_support_{emotion.value}"

            return support_response

        except Exception as e:
            logger.error(f"Failed to provide emotional support for session {session_state.session_id}: {e}")
            return {"error": "Unable to provide emotional support"}

    def get_emotional_safety_status(self, session_state: SessionState) -> Dict[str, Any]:
        """Get current emotional safety status for a session."""
        try:
            # Get recent emotional history
            emotional_history = self.emotional_safety_system.get_emotional_history(
                session_state.user_id, hours=2
            )

            # Get trigger history
            trigger_history = self.emotional_safety_system.get_trigger_history(
                session_state.user_id, hours=2
            )

            # Calculate current safety status
            current_distress = DistressLevel.NONE
            if emotional_history:
                latest_snapshot = emotional_history[-1]
                current_distress = latest_snapshot.distress_level

            return {
                "current_distress_level": current_distress.name,
                "recent_snapshots_count": len(emotional_history),
                "recent_triggers_count": len(trigger_history),
                "monitoring_active": self.emotional_safety_system.monitoring_enabled,
                "intervention_threshold": self.emotional_safety_system.intervention_threshold.name,
                "support_available": session_state.context.get("coping_support_offered", False),
                "crisis_protocol_active": session_state.context.get("crisis_intervention_active", False)
            }

        except Exception as e:
            logger.error(f"Failed to get emotional safety status for session {session_state.session_id}: {e}")
            return {"error": "Unable to get safety status"}

    def get_metrics(self) -> Dict[str, Any]:
        """Get therapeutic integrator metrics."""
        emotional_metrics = self.emotional_safety_system.get_metrics()

        return {
            "validation_count": self.validation_count,
            "safety_violations": self.safety_violations,
            "crisis_interventions": self.crisis_interventions,
            "emotional_interventions": self.emotional_interventions,
            "active_sessions": len(self.session_contexts),
            "safety_monitors": len(self.safety_monitors),
            "progress_trackers": len(self.progress_trackers),
            "emotional_safety_metrics": emotional_metrics
        }
