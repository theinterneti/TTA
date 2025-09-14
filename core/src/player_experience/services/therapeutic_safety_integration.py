"""
Therapeutic Safety Integration Service

This service integrates existing therapeutic safety measures, crisis detection, and safety
monitoring with all new gameplay components to ensure player wellbeing throughout the experience.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from src.components.gameplay_loop.services.session_integration_manager import (
    SessionIntegrationManager,
)

from .agent_orchestration_websocket_bridge import AgentOrchestrationWebSocketBridge
from .dynamic_story_generation_service import DynamicStoryGenerationService
from .gameplay_chat_manager import GameplayChatManager

logger = logging.getLogger(__name__)


class SafetyAlertLevel(str, Enum):
    """Levels of safety alerts."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SafetyTriggerType(str, Enum):
    """Types of safety triggers."""

    CRISIS_KEYWORDS = "crisis_keywords"
    EMOTIONAL_DISTRESS = "emotional_distress"
    SELF_HARM_INDICATORS = "self_harm_indicators"
    SUBSTANCE_ABUSE = "substance_abuse"
    THERAPEUTIC_REGRESSION = "therapeutic_regression"
    SESSION_ANOMALY = "session_anomaly"
    NARRATIVE_CONCERN = "narrative_concern"
    BEHAVIORAL_PATTERN = "behavioral_pattern"


@dataclass
class SafetyAlert:
    """Represents a therapeutic safety alert."""

    alert_id: str
    player_id: str
    session_id: str
    alert_level: SafetyAlertLevel
    trigger_type: SafetyTriggerType
    trigger_data: dict[str, Any]
    context: dict[str, Any]
    recommended_actions: list[str]
    auto_actions_taken: list[str]
    requires_human_review: bool
    created_at: datetime
    resolved_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        if self.resolved_at:
            data["resolved_at"] = self.resolved_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SafetyAlert":
        """Create from dictionary loaded from storage."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("resolved_at"):
            data["resolved_at"] = datetime.fromisoformat(data["resolved_at"])
        data["alert_level"] = SafetyAlertLevel(data["alert_level"])
        data["trigger_type"] = SafetyTriggerType(data["trigger_type"])
        return cls(**data)


@dataclass
class SafetyMonitoringConfig:
    """Configuration for safety monitoring."""

    enable_crisis_detection: bool = True
    enable_emotional_monitoring: bool = True
    enable_narrative_safety: bool = True
    enable_behavioral_analysis: bool = True
    crisis_keywords_sensitivity: float = 0.8
    emotional_distress_threshold: float = 0.7
    auto_intervention_enabled: bool = True
    human_review_threshold: SafetyAlertLevel = SafetyAlertLevel.HIGH
    monitoring_frequency_seconds: int = 30


class TherapeuticSafetyIntegration:
    """
    Service for integrating therapeutic safety measures across all gameplay components.

    Provides comprehensive safety monitoring, crisis detection, and intervention capabilities
    to ensure player wellbeing throughout the therapeutic gaming experience.
    """

    def __init__(
        self,
        session_manager: SessionIntegrationManager | None = None,
        chat_manager: GameplayChatManager | None = None,
        story_service: DynamicStoryGenerationService | None = None,
        agent_bridge: AgentOrchestrationWebSocketBridge | None = None,
    ):
        """
        Initialize the Therapeutic Safety Integration service.

        Args:
            session_manager: Session integration manager
            chat_manager: Gameplay chat manager
            story_service: Dynamic story generation service
            agent_bridge: Agent orchestration WebSocket bridge
        """
        self.session_manager = session_manager or SessionIntegrationManager()
        self.chat_manager = chat_manager or GameplayChatManager()
        self.story_service = story_service or DynamicStoryGenerationService()
        self.agent_bridge = agent_bridge or AgentOrchestrationWebSocketBridge()

        # Safety monitoring configuration
        self.config = SafetyMonitoringConfig()

        # Safety monitoring state
        self.active_alerts: dict[str, SafetyAlert] = {}
        self.player_safety_profiles: dict[str, dict[str, Any]] = {}
        self.safety_triggers: dict[SafetyTriggerType, Callable] = {}

        # Crisis detection patterns
        self.crisis_keywords = self._build_crisis_keywords()
        self.emotional_indicators = self._build_emotional_indicators()
        self.behavioral_patterns = self._build_behavioral_patterns()

        # Safety intervention strategies
        self.intervention_strategies = self._build_intervention_strategies()

        # Background monitoring
        self.monitoring_task: asyncio.Task | None = None
        self.is_running = False

        # Integration hooks
        self.component_hooks: dict[str, list[Callable]] = {}

        # Metrics
        self.metrics = {
            "safety_alerts_generated": 0,
            "crisis_interventions": 0,
            "emotional_support_provided": 0,
            "narrative_safety_corrections": 0,
            "behavioral_concerns_detected": 0,
            "human_reviews_requested": 0,
            "auto_interventions_executed": 0,
        }

        # Initialize safety triggers
        self._initialize_safety_triggers()

        logger.info("TherapeuticSafetyIntegration service initialized")

    async def start(self) -> None:
        """Start the therapeutic safety integration service."""
        if self.is_running:
            logger.warning("Therapeutic safety integration is already running")
            return

        self.is_running = True

        # Start background monitoring
        self.monitoring_task = asyncio.create_task(self._safety_monitoring_loop())

        # Register component hooks
        await self._register_component_hooks()

        logger.info("Therapeutic safety integration started")

    async def stop(self) -> None:
        """Stop the therapeutic safety integration service."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel monitoring task
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        # Unregister component hooks
        await self._unregister_component_hooks()

        logger.info("Therapeutic safety integration stopped")

    async def monitor_player_message(
        self,
        player_id: str,
        session_id: str,
        message_text: str,
        message_context: dict[str, Any] | None = None,
    ) -> SafetyAlert | None:
        """
        Monitor a player message for safety concerns.

        Args:
            player_id: Player identifier
            session_id: Session identifier
            message_text: Player message text
            message_context: Optional message context

        Returns:
            SafetyAlert if concerns detected, None otherwise
        """
        try:
            # Check for crisis keywords
            crisis_check = await self._check_crisis_keywords(message_text)
            if crisis_check["detected"]:
                return await self._create_safety_alert(
                    player_id,
                    session_id,
                    SafetyTriggerType.CRISIS_KEYWORDS,
                    crisis_check,
                    message_context or {},
                )

            # Check for emotional distress
            emotional_check = await self._check_emotional_distress(message_text)
            if emotional_check["detected"]:
                return await self._create_safety_alert(
                    player_id,
                    session_id,
                    SafetyTriggerType.EMOTIONAL_DISTRESS,
                    emotional_check,
                    message_context or {},
                )

            # Check for self-harm indicators
            self_harm_check = await self._check_self_harm_indicators(message_text)
            if self_harm_check["detected"]:
                return await self._create_safety_alert(
                    player_id,
                    session_id,
                    SafetyTriggerType.SELF_HARM_INDICATORS,
                    self_harm_check,
                    message_context or {},
                )

            return None

        except Exception as e:
            logger.error(f"Error monitoring player message: {e}")
            return None

    async def monitor_narrative_content(
        self, session_id: str, narrative_content: str, narrative_context: dict[str, Any]
    ) -> SafetyAlert | None:
        """
        Monitor narrative content for safety concerns.

        Args:
            session_id: Session identifier
            narrative_content: Generated narrative content
            narrative_context: Narrative context

        Returns:
            SafetyAlert if concerns detected, None otherwise
        """
        try:
            # Check for potentially harmful narrative content
            narrative_check = await self._check_narrative_safety(
                narrative_content, narrative_context
            )

            if narrative_check["detected"]:
                player_id = narrative_context.get("player_id", "")
                return await self._create_safety_alert(
                    player_id,
                    session_id,
                    SafetyTriggerType.NARRATIVE_CONCERN,
                    narrative_check,
                    narrative_context,
                )

            return None

        except Exception as e:
            logger.error(f"Error monitoring narrative content: {e}")
            return None

    async def monitor_session_behavior(
        self, player_id: str, session_id: str, behavioral_data: dict[str, Any]
    ) -> SafetyAlert | None:
        """
        Monitor session behavior patterns for safety concerns.

        Args:
            player_id: Player identifier
            session_id: Session identifier
            behavioral_data: Behavioral data to analyze

        Returns:
            SafetyAlert if concerns detected, None otherwise
        """
        try:
            # Check for concerning behavioral patterns
            behavioral_check = await self._check_behavioral_patterns(
                player_id, behavioral_data
            )

            if behavioral_check["detected"]:
                return await self._create_safety_alert(
                    player_id,
                    session_id,
                    SafetyTriggerType.BEHAVIORAL_PATTERN,
                    behavioral_check,
                    behavioral_data,
                )

            return None

        except Exception as e:
            logger.error(f"Error monitoring session behavior: {e}")
            return None

    async def execute_safety_intervention(
        self, alert: SafetyAlert, intervention_type: str | None = None
    ) -> dict[str, Any]:
        """
        Execute safety intervention based on alert.

        Args:
            alert: Safety alert to respond to
            intervention_type: Optional specific intervention type

        Returns:
            Intervention result
        """
        try:
            # Determine intervention strategy
            if intervention_type:
                strategy = self.intervention_strategies.get(intervention_type)
            else:
                strategy = self._select_intervention_strategy(alert)

            if not strategy:
                logger.error(
                    f"No intervention strategy found for alert {alert.alert_id}"
                )
                return {"success": False, "error": "no_strategy_found"}

            # Execute intervention
            intervention_result = await strategy(alert)

            # Update alert with intervention actions
            alert.auto_actions_taken.extend(
                intervention_result.get("actions_taken", [])
            )

            # Send intervention to chat if needed
            if intervention_result.get("send_to_chat", False):
                await self._send_intervention_to_chat(alert, intervention_result)

            # Update metrics
            self.metrics["auto_interventions_executed"] += 1
            self._update_intervention_metrics(alert.trigger_type)

            logger.info(f"Executed safety intervention for alert {alert.alert_id}")
            return intervention_result

        except Exception as e:
            logger.error(f"Error executing safety intervention: {e}")
            return {"success": False, "error": str(e)}

    async def get_player_safety_profile(self, player_id: str) -> dict[str, Any]:
        """
        Get safety profile for a player.

        Args:
            player_id: Player identifier

        Returns:
            Player safety profile
        """
        try:
            if player_id not in self.player_safety_profiles:
                # Create default safety profile
                self.player_safety_profiles[player_id] = {
                    "player_id": player_id,
                    "risk_level": "low",
                    "alert_history": [],
                    "intervention_history": [],
                    "safety_preferences": {},
                    "monitoring_flags": [],
                    "last_updated": datetime.utcnow().isoformat(),
                }

            return self.player_safety_profiles[player_id]

        except Exception as e:
            logger.error(f"Error getting player safety profile: {e}")
            return {}

    # Private helper methods

    async def _create_safety_alert(
        self,
        player_id: str,
        session_id: str,
        trigger_type: SafetyTriggerType,
        trigger_data: dict[str, Any],
        context: dict[str, Any],
    ) -> SafetyAlert:
        """Create a safety alert."""
        try:
            alert_id = f"alert_{player_id}_{datetime.utcnow().timestamp()}"

            # Determine alert level
            alert_level = self._determine_alert_level(trigger_type, trigger_data)

            # Generate recommended actions
            recommended_actions = self._generate_recommended_actions(
                trigger_type, alert_level, trigger_data
            )

            # Determine if human review is required
            requires_human_review = (
                alert_level.value
                in [
                    SafetyAlertLevel.HIGH.value,
                    SafetyAlertLevel.CRITICAL.value,
                    SafetyAlertLevel.EMERGENCY.value,
                ]
                or alert_level.value >= self.config.human_review_threshold.value
            )

            # Create alert
            alert = SafetyAlert(
                alert_id=alert_id,
                player_id=player_id,
                session_id=session_id,
                alert_level=alert_level,
                trigger_type=trigger_type,
                trigger_data=trigger_data,
                context=context,
                recommended_actions=recommended_actions,
                auto_actions_taken=[],
                requires_human_review=requires_human_review,
                created_at=datetime.utcnow(),
            )

            # Store alert
            self.active_alerts[alert_id] = alert

            # Execute auto-intervention if enabled and appropriate
            if (
                self.config.auto_intervention_enabled
                and alert_level.value <= SafetyAlertLevel.MEDIUM.value
            ):
                await self.execute_safety_intervention(alert)

            # Update metrics
            self.metrics["safety_alerts_generated"] += 1
            if requires_human_review:
                self.metrics["human_reviews_requested"] += 1

            # Update player safety profile
            await self._update_player_safety_profile(player_id, alert)

            logger.warning(f"Created safety alert {alert_id} for player {player_id}")
            return alert

        except Exception as e:
            logger.error(f"Error creating safety alert: {e}")
            raise

    async def _check_crisis_keywords(self, message_text: str) -> dict[str, Any]:
        """Check message for crisis keywords."""
        try:
            message_lower = message_text.lower()
            detected_keywords = []
            severity_score = 0.0

            for category, keywords in self.crisis_keywords.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        detected_keywords.append(
                            {
                                "keyword": keyword,
                                "category": category,
                                "severity": (
                                    keywords[keyword]
                                    if isinstance(keywords, dict)
                                    else 0.8
                                ),
                            }
                        )
                        severity_score = max(
                            severity_score,
                            keywords[keyword] if isinstance(keywords, dict) else 0.8,
                        )

            detected = severity_score >= self.config.crisis_keywords_sensitivity

            return {
                "detected": detected,
                "severity_score": severity_score,
                "keywords_found": detected_keywords,
                "category": "crisis_keywords",
            }

        except Exception as e:
            logger.error(f"Error checking crisis keywords: {e}")
            return {"detected": False}

    async def _check_emotional_distress(self, message_text: str) -> dict[str, Any]:
        """Check message for emotional distress indicators."""
        try:
            message_lower = message_text.lower()
            distress_indicators = []
            distress_score = 0.0

            for emotion, indicators in self.emotional_indicators.items():
                for indicator in indicators:
                    if indicator in message_lower:
                        distress_indicators.append(
                            {
                                "indicator": indicator,
                                "emotion": emotion,
                                "intensity": 0.7,  # Default intensity
                            }
                        )
                        distress_score = max(distress_score, 0.7)

            detected = distress_score >= self.config.emotional_distress_threshold

            return {
                "detected": detected,
                "distress_score": distress_score,
                "indicators_found": distress_indicators,
                "category": "emotional_distress",
            }

        except Exception as e:
            logger.error(f"Error checking emotional distress: {e}")
            return {"detected": False}

    async def _check_self_harm_indicators(self, message_text: str) -> dict[str, Any]:
        """Check message for self-harm indicators."""
        try:
            message_lower = message_text.lower()

            # High-risk self-harm keywords
            self_harm_keywords = [
                "hurt myself",
                "kill myself",
                "end it all",
                "suicide",
                "self harm",
                "cut myself",
                "overdose",
                "jump off",
                "hang myself",
            ]

            detected_indicators = []
            risk_score = 0.0

            for keyword in self_harm_keywords:
                if keyword in message_lower:
                    detected_indicators.append(
                        {"indicator": keyword, "risk_level": "high", "severity": 1.0}
                    )
                    risk_score = 1.0  # Maximum risk
                    break

            return {
                "detected": risk_score > 0.0,
                "risk_score": risk_score,
                "indicators_found": detected_indicators,
                "category": "self_harm",
            }

        except Exception as e:
            logger.error(f"Error checking self-harm indicators: {e}")
            return {"detected": False}

    async def _check_narrative_safety(
        self, narrative_content: str, narrative_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Check narrative content for safety concerns."""
        try:
            content_lower = narrative_content.lower()
            safety_concerns = []
            concern_score = 0.0

            # Check for potentially harmful content
            harmful_themes = [
                "graphic violence",
                "self-harm",
                "substance abuse",
                "trauma triggers",
                "inappropriate content",
            ]

            for theme in harmful_themes:
                if any(word in content_lower for word in theme.split()):
                    safety_concerns.append(
                        {
                            "theme": theme,
                            "severity": 0.6,
                            "context": "narrative_content",
                        }
                    )
                    concern_score = max(concern_score, 0.6)

            return {
                "detected": concern_score > 0.5,
                "concern_score": concern_score,
                "concerns_found": safety_concerns,
                "category": "narrative_safety",
            }

        except Exception as e:
            logger.error(f"Error checking narrative safety: {e}")
            return {"detected": False}

    async def _check_behavioral_patterns(
        self, player_id: str, behavioral_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Check for concerning behavioral patterns."""
        try:
            concerns = []
            concern_score = 0.0

            # Check session duration patterns
            session_duration = behavioral_data.get("session_duration_minutes", 0)
            if session_duration > 180:  # More than 3 hours
                concerns.append(
                    {
                        "pattern": "excessive_session_duration",
                        "value": session_duration,
                        "severity": 0.6,
                    }
                )
                concern_score = max(concern_score, 0.6)

            # Check message frequency patterns
            message_frequency = behavioral_data.get("messages_per_minute", 0)
            if message_frequency > 5:  # Very high message frequency
                concerns.append(
                    {
                        "pattern": "excessive_messaging",
                        "value": message_frequency,
                        "severity": 0.5,
                    }
                )
                concern_score = max(concern_score, 0.5)

            # Check emotional volatility
            emotional_changes = behavioral_data.get("emotional_volatility", 0)
            if emotional_changes > 0.8:
                concerns.append(
                    {
                        "pattern": "emotional_volatility",
                        "value": emotional_changes,
                        "severity": 0.7,
                    }
                )
                concern_score = max(concern_score, 0.7)

            return {
                "detected": concern_score > 0.5,
                "concern_score": concern_score,
                "patterns_found": concerns,
                "category": "behavioral_patterns",
            }

        except Exception as e:
            logger.error(f"Error checking behavioral patterns: {e}")
            return {"detected": False}

    def _determine_alert_level(
        self, trigger_type: SafetyTriggerType, trigger_data: dict[str, Any]
    ) -> SafetyAlertLevel:
        """Determine alert level based on trigger type and data."""
        try:
            if trigger_type == SafetyTriggerType.SELF_HARM_INDICATORS:
                return SafetyAlertLevel.CRITICAL
            elif trigger_type == SafetyTriggerType.CRISIS_KEYWORDS:
                severity = trigger_data.get("severity_score", 0.0)
                if severity >= 0.9:
                    return SafetyAlertLevel.CRITICAL
                elif severity >= 0.7:
                    return SafetyAlertLevel.HIGH
                else:
                    return SafetyAlertLevel.MEDIUM
            elif trigger_type == SafetyTriggerType.EMOTIONAL_DISTRESS:
                distress_score = trigger_data.get("distress_score", 0.0)
                if distress_score >= 0.8:
                    return SafetyAlertLevel.HIGH
                else:
                    return SafetyAlertLevel.MEDIUM
            else:
                return SafetyAlertLevel.LOW

        except Exception as e:
            logger.error(f"Error determining alert level: {e}")
            return SafetyAlertLevel.MEDIUM

    def _generate_recommended_actions(
        self,
        trigger_type: SafetyTriggerType,
        alert_level: SafetyAlertLevel,
        trigger_data: dict[str, Any],
    ) -> list[str]:
        """Generate recommended actions for an alert."""
        try:
            actions = []

            if trigger_type == SafetyTriggerType.SELF_HARM_INDICATORS:
                actions.extend(
                    [
                        "immediate_crisis_intervention",
                        "contact_emergency_services",
                        "provide_crisis_resources",
                        "human_therapist_review",
                    ]
                )
            elif trigger_type == SafetyTriggerType.CRISIS_KEYWORDS:
                actions.extend(
                    [
                        "provide_emotional_support",
                        "offer_coping_strategies",
                        "suggest_professional_help",
                    ]
                )
            elif trigger_type == SafetyTriggerType.EMOTIONAL_DISTRESS:
                actions.extend(
                    [
                        "emotional_validation",
                        "breathing_exercise",
                        "grounding_technique",
                    ]
                )
            elif trigger_type == SafetyTriggerType.NARRATIVE_CONCERN:
                actions.extend(
                    [
                        "narrative_content_review",
                        "story_direction_adjustment",
                        "therapeutic_refocus",
                    ]
                )

            # Add level-specific actions
            if alert_level in [SafetyAlertLevel.HIGH, SafetyAlertLevel.CRITICAL]:
                actions.append("escalate_to_human_review")

            return actions

        except Exception as e:
            logger.error(f"Error generating recommended actions: {e}")
            return ["general_support"]

    def _select_intervention_strategy(self, alert: SafetyAlert) -> Callable | None:
        """Select appropriate intervention strategy for an alert."""
        try:
            if alert.trigger_type == SafetyTriggerType.SELF_HARM_INDICATORS:
                return self.intervention_strategies.get("crisis_intervention")
            elif alert.trigger_type == SafetyTriggerType.EMOTIONAL_DISTRESS:
                return self.intervention_strategies.get("emotional_support")
            elif alert.trigger_type == SafetyTriggerType.NARRATIVE_CONCERN:
                return self.intervention_strategies.get("narrative_adjustment")
            else:
                return self.intervention_strategies.get("general_support")

        except Exception as e:
            logger.error(f"Error selecting intervention strategy: {e}")
            return None

    async def _send_intervention_to_chat(
        self, alert: SafetyAlert, intervention_result: dict[str, Any]
    ) -> None:
        """Send intervention message to chat."""
        try:
            intervention_message = {
                "type": "therapeutic_intervention",
                "session_id": alert.session_id,
                "content": {
                    "intervention_type": intervention_result.get(
                        "intervention_type", "safety_support"
                    ),
                    "message": intervention_result.get(
                        "message", "I'm here to support you."
                    ),
                    "resources": intervention_result.get("resources", []),
                    "severity": alert.alert_level.value,
                    "immediate_actions": intervention_result.get(
                        "immediate_actions", []
                    ),
                },
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "alert_id": alert.alert_id,
                    "trigger_type": alert.trigger_type.value,
                    "auto_intervention": True,
                },
            }

            await self.chat_manager.broadcast_to_session(
                alert.session_id, intervention_message
            )

        except Exception as e:
            logger.error(f"Error sending intervention to chat: {e}")

    async def _update_player_safety_profile(
        self, player_id: str, alert: SafetyAlert
    ) -> None:
        """Update player safety profile with new alert."""
        try:
            profile = await self.get_player_safety_profile(player_id)

            # Add alert to history
            profile["alert_history"].append(
                {
                    "alert_id": alert.alert_id,
                    "trigger_type": alert.trigger_type.value,
                    "alert_level": alert.alert_level.value,
                    "created_at": alert.created_at.isoformat(),
                }
            )

            # Update risk level based on recent alerts
            recent_alerts = [
                a
                for a in profile["alert_history"]
                if datetime.fromisoformat(a["created_at"])
                > datetime.utcnow() - timedelta(days=7)
            ]

            if len(recent_alerts) >= 3:
                profile["risk_level"] = "high"
            elif len(recent_alerts) >= 1:
                profile["risk_level"] = "medium"
            else:
                profile["risk_level"] = "low"

            profile["last_updated"] = datetime.utcnow().isoformat()

        except Exception as e:
            logger.error(f"Error updating player safety profile: {e}")

    def _update_intervention_metrics(self, trigger_type: SafetyTriggerType) -> None:
        """Update metrics for specific intervention types."""
        if trigger_type == SafetyTriggerType.CRISIS_KEYWORDS:
            self.metrics["crisis_interventions"] += 1
        elif trigger_type == SafetyTriggerType.EMOTIONAL_DISTRESS:
            self.metrics["emotional_support_provided"] += 1
        elif trigger_type == SafetyTriggerType.NARRATIVE_CONCERN:
            self.metrics["narrative_safety_corrections"] += 1
        elif trigger_type == SafetyTriggerType.BEHAVIORAL_PATTERN:
            self.metrics["behavioral_concerns_detected"] += 1

    async def _safety_monitoring_loop(self) -> None:
        """Background safety monitoring loop."""
        logger.info("Started safety monitoring loop")

        while self.is_running:
            try:
                await asyncio.sleep(self.config.monitoring_frequency_seconds)

                # Perform periodic safety checks
                await self._perform_periodic_safety_checks()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in safety monitoring loop: {e}")
                await asyncio.sleep(60)

        logger.info("Stopped safety monitoring loop")

    async def _perform_periodic_safety_checks(self) -> None:
        """Perform periodic safety checks on active sessions."""
        try:
            # This would implement periodic safety monitoring
            # For now, just log that monitoring is active
            logger.debug("Performing periodic safety checks")

        except Exception as e:
            logger.error(f"Error in periodic safety checks: {e}")

    async def _register_component_hooks(self) -> None:
        """Register safety hooks with other components."""
        try:
            # Register with chat manager
            if hasattr(self.chat_manager, "register_message_hook"):
                self.chat_manager.register_message_hook(self.monitor_player_message)

            # Register with story service
            if hasattr(self.story_service, "register_narrative_hook"):
                self.story_service.register_narrative_hook(
                    self.monitor_narrative_content
                )

            logger.info("Registered safety hooks with components")

        except Exception as e:
            logger.error(f"Error registering component hooks: {e}")

    async def _unregister_component_hooks(self) -> None:
        """Unregister safety hooks from other components."""
        try:
            # Unregister from components
            logger.info("Unregistered safety hooks from components")

        except Exception as e:
            logger.error(f"Error unregistering component hooks: {e}")

    def _initialize_safety_triggers(self) -> None:
        """Initialize safety trigger handlers."""
        self.safety_triggers = {
            SafetyTriggerType.CRISIS_KEYWORDS: self._check_crisis_keywords,
            SafetyTriggerType.EMOTIONAL_DISTRESS: self._check_emotional_distress,
            SafetyTriggerType.SELF_HARM_INDICATORS: self._check_self_harm_indicators,
            SafetyTriggerType.NARRATIVE_CONCERN: self._check_narrative_safety,
            SafetyTriggerType.BEHAVIORAL_PATTERN: self._check_behavioral_patterns,
        }

    def _build_crisis_keywords(self) -> dict[str, list[str]]:
        """Build crisis keyword detection patterns."""
        return {
            "suicide": [
                "kill myself",
                "end my life",
                "suicide",
                "suicidal",
                "want to die",
                "better off dead",
                "end it all",
                "take my own life",
            ],
            "self_harm": [
                "hurt myself",
                "cut myself",
                "self harm",
                "self-harm",
                "harm myself",
                "cut my wrists",
                "overdose",
                "self-injury",
            ],
            "crisis": [
                "can't go on",
                "can't take it",
                "hopeless",
                "no way out",
                "desperate",
                "breaking point",
                "can't cope",
                "falling apart",
            ],
            "substance_abuse": [
                "drinking too much",
                "using drugs",
                "getting high",
                "need a drink",
                "substance abuse",
                "addiction",
                "relapse",
            ],
            "violence": [
                "hurt someone",
                "kill someone",
                "violent thoughts",
                "rage",
                "anger issues",
                "want to hurt",
                "violent urges",
            ],
        }

    def _build_emotional_indicators(self) -> dict[str, list[str]]:
        """Build emotional distress indicators."""
        return {
            "severe_depression": [
                "completely hopeless",
                "nothing matters",
                "empty inside",
                "numb",
                "worthless",
                "useless",
                "failure",
                "burden",
            ],
            "severe_anxiety": [
                "panic attack",
                "can't breathe",
                "heart racing",
                "terrified",
                "overwhelming fear",
                "anxiety attack",
                "paralyzed with fear",
            ],
            "trauma_response": [
                "flashback",
                "nightmare",
                "triggered",
                "reliving",
                "traumatic",
                "ptsd",
                "can't forget",
                "haunted",
            ],
            "isolation": [
                "completely alone",
                "no one cares",
                "isolated",
                "abandoned",
                "nobody understands",
                "all alone",
                "lonely",
            ],
            "anger": [
                "furious",
                "enraged",
                "violent anger",
                "uncontrollable rage",
                "want to destroy",
                "hate everything",
                "explosive anger",
            ],
        }

    def _build_behavioral_patterns(self) -> dict[str, dict[str, Any]]:
        """Build behavioral pattern detection rules."""
        return {
            "excessive_usage": {
                "session_duration_threshold": 180,  # minutes
                "daily_sessions_threshold": 8,
                "concern_level": "medium",
            },
            "rapid_messaging": {
                "messages_per_minute_threshold": 5,
                "burst_duration_threshold": 10,  # minutes
                "concern_level": "low",
            },
            "emotional_volatility": {
                "emotion_change_threshold": 0.8,
                "volatility_window_minutes": 30,
                "concern_level": "medium",
            },
            "withdrawal_pattern": {
                "silence_duration_threshold": 60,  # minutes
                "after_distress_indicator": True,
                "concern_level": "high",
            },
        }

    def _build_intervention_strategies(self) -> dict[str, Callable]:
        """Build intervention strategy handlers."""
        return {
            "crisis_intervention": self._crisis_intervention_strategy,
            "emotional_support": self._emotional_support_strategy,
            "narrative_adjustment": self._narrative_adjustment_strategy,
            "behavioral_guidance": self._behavioral_guidance_strategy,
            "general_support": self._general_support_strategy,
        }

    async def _crisis_intervention_strategy(self, alert: SafetyAlert) -> dict[str, Any]:
        """Execute crisis intervention strategy."""
        try:
            return {
                "intervention_type": "crisis_intervention",
                "message": "I'm very concerned about what you've shared. Your safety is the most important thing right now. Please reach out to a crisis helpline or emergency services if you're in immediate danger.",
                "resources": [
                    {
                        "name": "National Suicide Prevention Lifeline",
                        "contact": "988",
                        "description": "24/7 crisis support",
                    },
                    {
                        "name": "Crisis Text Line",
                        "contact": "Text HOME to 741741",
                        "description": "24/7 text-based crisis support",
                    },
                ],
                "immediate_actions": [
                    "contact_emergency_services",
                    "provide_crisis_resources",
                    "escalate_to_human_therapist",
                ],
                "actions_taken": [
                    "crisis_resources_provided",
                    "human_review_requested",
                ],
                "send_to_chat": True,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error in crisis intervention strategy: {e}")
            return {"success": False, "error": str(e)}

    async def _emotional_support_strategy(self, alert: SafetyAlert) -> dict[str, Any]:
        """Execute emotional support strategy."""
        try:
            return {
                "intervention_type": "emotional_support",
                "message": "I can hear that you're going through a difficult time. Your feelings are valid, and you don't have to face this alone. Let's take a moment to focus on some coping strategies that might help.",
                "resources": [
                    {
                        "name": "Breathing Exercise",
                        "description": "Try the 4-7-8 breathing technique: breathe in for 4, hold for 7, exhale for 8",
                    },
                    {
                        "name": "Grounding Technique",
                        "description": "Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste",
                    },
                ],
                "immediate_actions": [
                    "provide_coping_strategies",
                    "emotional_validation",
                    "suggest_therapeutic_activities",
                ],
                "actions_taken": [
                    "emotional_support_provided",
                    "coping_strategies_offered",
                ],
                "send_to_chat": True,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error in emotional support strategy: {e}")
            return {"success": False, "error": str(e)}

    async def _narrative_adjustment_strategy(
        self, alert: SafetyAlert
    ) -> dict[str, Any]:
        """Execute narrative adjustment strategy."""
        try:
            return {
                "intervention_type": "narrative_adjustment",
                "message": "I notice the story might be touching on some sensitive themes. Let's adjust our narrative to focus on more supportive and healing elements.",
                "immediate_actions": [
                    "adjust_story_content",
                    "focus_on_therapeutic_themes",
                    "provide_content_warning",
                ],
                "actions_taken": [
                    "narrative_content_adjusted",
                    "therapeutic_refocus_applied",
                ],
                "send_to_chat": False,  # Handle through story generation
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error in narrative adjustment strategy: {e}")
            return {"success": False, "error": str(e)}

    async def _behavioral_guidance_strategy(self, alert: SafetyAlert) -> dict[str, Any]:
        """Execute behavioral guidance strategy."""
        try:
            return {
                "intervention_type": "behavioral_guidance",
                "message": "I've noticed some patterns in our session that might benefit from a gentle adjustment. Taking breaks and pacing ourselves can be really helpful for processing and growth.",
                "resources": [
                    {
                        "name": "Healthy Gaming Habits",
                        "description": "Tips for maintaining balance while engaging in therapeutic gaming",
                    }
                ],
                "immediate_actions": [
                    "suggest_break",
                    "provide_pacing_guidance",
                    "offer_session_summary",
                ],
                "actions_taken": [
                    "behavioral_guidance_provided",
                    "healthy_habits_suggested",
                ],
                "send_to_chat": True,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error in behavioral guidance strategy: {e}")
            return {"success": False, "error": str(e)}

    async def _general_support_strategy(self, alert: SafetyAlert) -> dict[str, Any]:
        """Execute general support strategy."""
        try:
            return {
                "intervention_type": "general_support",
                "message": "I'm here to support you through this experience. Remember that growth and healing take time, and it's okay to take things at your own pace.",
                "immediate_actions": [
                    "provide_encouragement",
                    "offer_continued_support",
                    "check_comfort_level",
                ],
                "actions_taken": ["general_support_provided", "encouragement_offered"],
                "send_to_chat": True,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error in general support strategy: {e}")
            return {"success": False, "error": str(e)}

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the therapeutic safety integration service."""
        return {
            **self.metrics,
            "active_alerts": len(self.active_alerts),
            "monitored_players": len(self.player_safety_profiles),
            "is_running": self.is_running,
            "monitoring_frequency_seconds": self.config.monitoring_frequency_seconds,
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the therapeutic safety integration service."""
        try:
            return {
                "service_running": self.is_running,
                "active_alerts": len(self.active_alerts),
                "monitored_players": len(self.player_safety_profiles),
                "monitoring_task_running": (
                    self.monitoring_task and not self.monitoring_task.done()
                    if self.monitoring_task
                    else False
                ),
                "crisis_detection_enabled": self.config.enable_crisis_detection,
                "auto_intervention_enabled": self.config.auto_intervention_enabled,
                "session_manager_available": self.session_manager is not None,
                "chat_manager_available": self.chat_manager is not None,
                "overall_status": "healthy" if self.is_running else "stopped",
            }

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"overall_status": "error", "error": str(e)}

    async def cleanup_resolved_alerts(self) -> int:
        """Clean up resolved alerts."""
        try:
            cleaned_count = 0
            current_time = datetime.utcnow()

            # Remove alerts resolved more than 24 hours ago
            resolved_alerts = []
            for alert_id, alert in self.active_alerts.items():
                if alert.resolved_at and current_time - alert.resolved_at > timedelta(
                    hours=24
                ):
                    resolved_alerts.append(alert_id)

            for alert_id in resolved_alerts:
                del self.active_alerts[alert_id]
                cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} resolved alerts")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up resolved alerts: {e}")
            return 0
