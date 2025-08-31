"""
Therapeutic safety middleware for the API Gateway.

This module provides comprehensive therapeutic content safety scanning,
crisis detection, intervention mechanisms, and compliance monitoring.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from ..config import get_gateway_settings
from ..models import GatewayRequest

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety assessment levels."""

    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class InterventionType(Enum):
    """Types of safety interventions."""

    LOG_ONLY = "log_only"
    FLAG_CONTENT = "flag_content"
    NOTIFY_STAFF = "notify_staff"
    BLOCK_REQUEST = "block_request"
    EMERGENCY_RESPONSE = "emergency_response"


class CrisisIndicator(Enum):
    """Types of crisis indicators."""

    SELF_HARM = "self_harm"
    SUICIDE_IDEATION = "suicide_ideation"
    SUBSTANCE_ABUSE = "substance_abuse"
    VIOLENCE = "violence"
    PSYCHOSIS = "psychosis"
    SEVERE_DEPRESSION = "severe_depression"
    PANIC_DISORDER = "panic_disorder"


@dataclass
class SafetyRule:
    """Individual safety rule configuration."""

    name: str
    description: str
    enabled: bool = True
    priority: int = 100  # Lower numbers execute first
    path_patterns: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=lambda: ["*"])

    # Content scanning
    scan_fields: list[str] = field(
        default_factory=lambda: ["message", "content", "description", "notes"]
    )
    crisis_keywords: list[str] = field(default_factory=list)
    warning_keywords: list[str] = field(default_factory=list)

    # Crisis detection patterns
    crisis_patterns: dict[CrisisIndicator, list[str]] = field(default_factory=dict)

    # Safety thresholds
    crisis_threshold: float = 0.8  # 0.0 to 1.0
    warning_threshold: float = 0.5

    # Intervention configuration
    intervention_type: InterventionType = InterventionType.LOG_ONLY
    notify_roles: list[str] = field(default_factory=list)

    # Therapeutic context requirements
    require_therapeutic_context: bool = False
    therapeutic_session_monitoring: bool = False


@dataclass
class SafetyConfig:
    """Configuration for therapeutic safety middleware."""

    enabled: bool = True
    real_time_monitoring: bool = True
    crisis_intervention: bool = True
    compliance_logging: bool = True

    # Crisis response settings
    emergency_contact_enabled: bool = False
    emergency_contact_threshold: float = 0.9
    auto_escalation: bool = False

    # Content monitoring
    content_retention_days: int = 30
    audit_trail_enabled: bool = True
    sensitive_content_masking: bool = True

    # Notification settings
    staff_notification_enabled: bool = True
    email_notifications: bool = False
    sms_notifications: bool = False

    # Compliance settings
    hipaa_compliance: bool = True
    gdpr_compliance: bool = True
    therapeutic_standards_compliance: bool = True


class TherapeuticSafetyMiddleware:
    """
    Therapeutic safety middleware for comprehensive content safety scanning.

    Provides crisis detection, intervention mechanisms, compliance monitoring,
    and therapeutic content safety validation.
    """

    def __init__(self, config: SafetyConfig | None = None):
        """
        Initialize therapeutic safety middleware.

        Args:
            config: Safety configuration
        """
        self.config = config or SafetyConfig()
        self.settings = get_gateway_settings()

        # Safety rules
        self.safety_rules: list[SafetyRule] = []
        self._load_default_rules()

        # Crisis detection patterns
        self.crisis_patterns = self._load_crisis_patterns()
        self.warning_patterns = self._load_warning_patterns()

        # Safety assessment cache
        self.assessment_cache: dict[str, tuple[SafetyLevel, datetime]] = {}
        self.cache_ttl = timedelta(minutes=5)

        # Intervention tracking
        self.active_interventions: dict[str, dict[str, Any]] = {}

        # Compliance tracking
        self.safety_events: list[dict[str, Any]] = []

    def _load_default_rules(self) -> None:
        """Load default safety rules."""
        # Crisis detection rule
        self.safety_rules.append(
            SafetyRule(
                name="crisis_detection",
                description="Detect crisis content and self-harm indicators",
                priority=1,
                path_patterns=["/api/therapeutic/*", "/api/sessions/*", "/api/chat/*"],
                crisis_threshold=0.8,
                warning_threshold=0.5,
                intervention_type=InterventionType.NOTIFY_STAFF,
                notify_roles=["therapist", "crisis_counselor", "admin"],
                require_therapeutic_context=True,
                therapeutic_session_monitoring=True,
            )
        )

        # Content safety rule
        self.safety_rules.append(
            SafetyRule(
                name="content_safety",
                description="General content safety scanning",
                priority=10,
                path_patterns=["*"],
                warning_threshold=0.3,
                intervention_type=InterventionType.FLAG_CONTENT,
            )
        )

        # Therapeutic compliance rule
        self.safety_rules.append(
            SafetyRule(
                name="therapeutic_compliance",
                description="Therapeutic standards compliance monitoring",
                priority=5,
                path_patterns=["/api/therapeutic/*", "/api/sessions/*"],
                intervention_type=InterventionType.LOG_ONLY,
                require_therapeutic_context=True,
            )
        )

    def _load_crisis_patterns(self) -> dict[CrisisIndicator, list[re.Pattern]]:
        """Load crisis detection patterns."""
        patterns = {
            CrisisIndicator.SELF_HARM: [
                re.compile(
                    r"\b(cut|cutting|hurt myself|self.?harm|mutilate)\b", re.IGNORECASE
                ),
                re.compile(
                    r"\b(razor|blade|knife|burn|burning)\b.*\b(myself|skin)\b",
                    re.IGNORECASE,
                ),
                re.compile(
                    r"\b(want to hurt|need to hurt|going to hurt)\b.*\bmyself\b",
                    re.IGNORECASE,
                ),
            ],
            CrisisIndicator.SUICIDE_IDEATION: [
                re.compile(
                    r"\b(suicide|kill myself|end it all|take my life)\b", re.IGNORECASE
                ),
                re.compile(
                    r"\b(want to die|wish I was dead|better off dead)\b", re.IGNORECASE
                ),
                re.compile(r"\b(jump off|hang myself|overdose|pills)\b", re.IGNORECASE),
                re.compile(
                    r"\b(planning to|going to|about to)\b.*\b(kill|die|end)\b",
                    re.IGNORECASE,
                ),
            ],
            CrisisIndicator.SUBSTANCE_ABUSE: [
                re.compile(
                    r"\b(overdosed|too many pills|drinking too much)\b", re.IGNORECASE
                ),
                re.compile(
                    r"\b(can\'t stop using|relapsed|using again)\b", re.IGNORECASE
                ),
                re.compile(r"\b(high right now|drunk|wasted|stoned)\b", re.IGNORECASE),
            ],
            CrisisIndicator.VIOLENCE: [
                re.compile(
                    r"\b(want to hurt|going to hurt|kill)\b.*\b(someone|others|them)\b",
                    re.IGNORECASE,
                ),
                re.compile(r"\b(violent thoughts|rage|anger|furious)\b", re.IGNORECASE),
                re.compile(r"\b(weapon|gun|knife|violence)\b", re.IGNORECASE),
            ],
            CrisisIndicator.SEVERE_DEPRESSION: [
                re.compile(r"\b(hopeless|worthless|useless|failure)\b", re.IGNORECASE),
                re.compile(
                    r"\b(can\'t go on|no point|give up|trapped)\b", re.IGNORECASE
                ),
                re.compile(
                    r"\b(unbearable pain|can\'t take it|desperate)\b", re.IGNORECASE
                ),
            ],
            CrisisIndicator.PANIC_DISORDER: [
                re.compile(
                    r"\b(panic attack|can\'t breathe|heart racing)\b", re.IGNORECASE
                ),
                re.compile(r"\b(chest pain|dizzy|fainting|dying)\b", re.IGNORECASE),
                re.compile(r"\b(losing control|going crazy|unreal)\b", re.IGNORECASE),
            ],
        }
        return patterns

    def _load_warning_patterns(self) -> list[re.Pattern]:
        """Load warning-level patterns."""
        return [
            re.compile(r"\b(sad|depressed|down|low|blue)\b", re.IGNORECASE),
            re.compile(r"\b(anxious|worried|stressed|overwhelmed)\b", re.IGNORECASE),
            re.compile(r"\b(tired|exhausted|drained|empty)\b", re.IGNORECASE),
            re.compile(r"\b(lonely|isolated|alone|abandoned)\b", re.IGNORECASE),
            re.compile(r"\b(angry|frustrated|irritated|mad)\b", re.IGNORECASE),
        ]

    async def assess_safety(self, gateway_request: GatewayRequest) -> GatewayRequest:
        """
        Assess therapeutic safety of the request content.

        Args:
            gateway_request: Request to assess

        Returns:
            GatewayRequest: Request with safety assessment
        """
        try:
            # Find applicable safety rules
            applicable_rules = self._find_applicable_rules(
                gateway_request.path, gateway_request.method.value
            )

            # Sort rules by priority
            applicable_rules.sort(key=lambda r: r.priority)

            # Perform safety assessment
            overall_safety_level = SafetyLevel.SAFE
            detected_indicators: list[CrisisIndicator] = []
            safety_score = 0.0

            for rule in applicable_rules:
                if not rule.enabled:
                    continue

                try:
                    rule_assessment = await self._assess_rule(gateway_request, rule)

                    # Update overall assessment
                    if (
                        rule_assessment["safety_level"].value
                        > overall_safety_level.value
                    ):
                        overall_safety_level = rule_assessment["safety_level"]

                    safety_score = max(safety_score, rule_assessment["safety_score"])
                    detected_indicators.extend(rule_assessment["crisis_indicators"])

                    # Handle interventions
                    if rule_assessment["intervention_required"]:
                        await self._handle_intervention(
                            gateway_request, rule, rule_assessment
                        )

                except Exception as e:
                    logger.error(f"Error assessing safety rule '{rule.name}': {e}")

            # Add safety metadata to request
            if not hasattr(gateway_request, "metadata"):
                gateway_request.metadata = {}

            gateway_request.metadata.update(
                {
                    "safety_assessment": {
                        "safety_level": overall_safety_level.value,
                        "safety_score": safety_score,
                        "crisis_indicators": [
                            indicator.value for indicator in detected_indicators
                        ],
                        "assessment_timestamp": datetime.utcnow().isoformat(),
                        "requires_intervention": overall_safety_level
                        in [SafetyLevel.DANGER, SafetyLevel.CRITICAL],
                    }
                }
            )

            # Log safety event for compliance
            if self.config.compliance_logging:
                await self._log_safety_event(
                    gateway_request, overall_safety_level, detected_indicators
                )

            return gateway_request

        except Exception as e:
            logger.error(f"Error during safety assessment: {e}")
            return gateway_request

    def _find_applicable_rules(self, path: str, method: str) -> list[SafetyRule]:
        """Find safety rules applicable to the request."""
        applicable_rules = []

        for rule in self.safety_rules:
            # Check method match
            if rule.methods != ["*"] and method not in rule.methods:
                continue

            # Check path pattern match
            if rule.path_patterns:
                path_match = False
                for pattern in rule.path_patterns:
                    if pattern == "*" or re.match(pattern.replace("*", ".*"), path):
                        path_match = True
                        break
                if not path_match:
                    continue

            applicable_rules.append(rule)

        return applicable_rules

    async def _assess_rule(
        self, request: GatewayRequest, rule: SafetyRule
    ) -> dict[str, Any]:
        """Assess a single safety rule against the request."""
        assessment = {
            "safety_level": SafetyLevel.SAFE,
            "safety_score": 0.0,
            "crisis_indicators": [],
            "intervention_required": False,
            "details": {},
        }

        # Check therapeutic context requirement
        if rule.require_therapeutic_context:
            if not request.auth_context or not request.auth_context.get(
                "therapeutic_context"
            ):
                assessment["details"]["therapeutic_context_missing"] = True
                return assessment

        # Extract content to analyze
        content_to_analyze = []

        if request.body:
            try:
                if isinstance(request.body, str):
                    body_data = json.loads(request.body)
                else:
                    body_data = request.body

                if isinstance(body_data, dict):
                    for field in rule.scan_fields:
                        if field in body_data:
                            content_to_analyze.append(str(body_data[field]))

            except json.JSONDecodeError:
                # Treat entire body as text content
                content_to_analyze.append(str(request.body))

        # Analyze content for crisis indicators
        if content_to_analyze:
            crisis_score = 0.0
            detected_indicators = []

            for content in content_to_analyze:
                content_assessment = await self._analyze_content(content)
                crisis_score = max(crisis_score, content_assessment["crisis_score"])
                detected_indicators.extend(content_assessment["crisis_indicators"])

            assessment["safety_score"] = crisis_score
            assessment["crisis_indicators"] = list(set(detected_indicators))

            # Determine safety level
            if crisis_score >= rule.crisis_threshold:
                assessment["safety_level"] = SafetyLevel.CRITICAL
                assessment["intervention_required"] = True
            elif crisis_score >= rule.warning_threshold:
                assessment["safety_level"] = SafetyLevel.WARNING
                if rule.intervention_type != InterventionType.LOG_ONLY:
                    assessment["intervention_required"] = True
            elif crisis_score > 0.1:
                assessment["safety_level"] = SafetyLevel.CAUTION

        return assessment

    async def _analyze_content(self, content: str) -> dict[str, Any]:
        """Analyze content for crisis indicators and safety concerns."""
        analysis = {
            "crisis_score": 0.0,
            "crisis_indicators": [],
            "warning_score": 0.0,
            "details": {},
        }

        content_lower = content.lower()

        # Check crisis patterns
        crisis_matches = 0
        total_crisis_patterns = 0

        for indicator, patterns in self.crisis_patterns.items():
            total_crisis_patterns += len(patterns)
            for pattern in patterns:
                if pattern.search(content):
                    crisis_matches += 1
                    analysis["crisis_indicators"].append(indicator)
                    analysis["details"][f"{indicator.value}_detected"] = True

        # Calculate crisis score
        if total_crisis_patterns > 0:
            analysis["crisis_score"] = min(
                1.0, crisis_matches / total_crisis_patterns * 2.0
            )

        # Check warning patterns
        warning_matches = 0
        for pattern in self.warning_patterns:
            if pattern.search(content):
                warning_matches += 1

        # Calculate warning score
        if self.warning_patterns:
            analysis["warning_score"] = min(
                1.0, warning_matches / len(self.warning_patterns)
            )

        # Combine scores (crisis score takes precedence)
        analysis["crisis_score"] = max(
            analysis["crisis_score"], analysis["warning_score"] * 0.5
        )

        return analysis

    async def _handle_intervention(
        self, request: GatewayRequest, rule: SafetyRule, assessment: dict[str, Any]
    ) -> None:
        """Handle safety intervention based on rule configuration."""
        intervention_id = (
            f"{request.correlation_id}_{rule.name}_{datetime.utcnow().timestamp()}"
        )

        intervention_data = {
            "intervention_id": intervention_id,
            "rule_name": rule.name,
            "intervention_type": rule.intervention_type.value,
            "safety_level": assessment["safety_level"].value,
            "safety_score": assessment["safety_score"],
            "crisis_indicators": [
                indicator.value for indicator in assessment["crisis_indicators"]
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": (
                request.auth_context.get("user_id") if request.auth_context else None
            ),
            "session_id": (
                request.auth_context.get("therapeutic_session_id")
                if request.auth_context
                else None
            ),
            "path": request.path,
        }

        # Store intervention
        self.active_interventions[intervention_id] = intervention_data

        # Execute intervention based on type
        if rule.intervention_type == InterventionType.LOG_ONLY:
            logger.info(f"Safety intervention logged: {intervention_data}")

        elif rule.intervention_type == InterventionType.FLAG_CONTENT:
            logger.warning(f"Content flagged for review: {intervention_data}")
            # Add flag to request metadata
            if not hasattr(request, "metadata"):
                request.metadata = {}
            request.metadata["content_flagged"] = True
            request.metadata["flag_reason"] = "safety_concern"

        elif rule.intervention_type == InterventionType.NOTIFY_STAFF:
            logger.critical(f"Staff notification triggered: {intervention_data}")
            await self._notify_staff(intervention_data, rule.notify_roles)

        elif rule.intervention_type == InterventionType.BLOCK_REQUEST:
            logger.critical(
                f"Request blocked due to safety concerns: {intervention_data}"
            )
            # This would typically raise an exception to block the request
            # For now, we'll just log and flag
            if not hasattr(request, "metadata"):
                request.metadata = {}
            request.metadata["request_blocked"] = True
            request.metadata["block_reason"] = "safety_violation"

        elif rule.intervention_type == InterventionType.EMERGENCY_RESPONSE:
            logger.critical(f"Emergency response triggered: {intervention_data}")
            await self._trigger_emergency_response(intervention_data)

    async def _notify_staff(
        self, intervention_data: dict[str, Any], notify_roles: list[str]
    ) -> None:
        """Notify staff members about safety concerns."""
        notification = {
            "type": "safety_alert",
            "priority": (
                "high"
                if intervention_data["safety_level"] in ["danger", "critical"]
                else "medium"
            ),
            "intervention_data": intervention_data,
            "notify_roles": notify_roles,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Log notification (in a real implementation, this would send actual notifications)
        logger.critical(
            "Staff notification sent",
            extra={
                "notification": notification,
                "safety_level": intervention_data["safety_level"],
                "crisis_indicators": intervention_data["crisis_indicators"],
            },
        )

        # TODO: Implement actual notification mechanisms
        # - Email notifications
        # - SMS notifications
        # - In-app notifications
        # - Integration with crisis response systems

    async def _trigger_emergency_response(
        self, intervention_data: dict[str, Any]
    ) -> None:
        """Trigger emergency response procedures."""
        emergency_response = {
            "type": "emergency_response",
            "intervention_data": intervention_data,
            "response_level": "immediate",
            "timestamp": datetime.utcnow().isoformat(),
            "escalation_required": True,
        }

        # Log emergency response
        logger.critical(
            "Emergency response triggered",
            extra={
                "emergency_response": emergency_response,
                "user_id": intervention_data.get("user_id"),
                "session_id": intervention_data.get("session_id"),
                "crisis_indicators": intervention_data["crisis_indicators"],
            },
        )

        # TODO: Implement emergency response procedures
        # - Contact emergency services if configured
        # - Notify crisis counselors immediately
        # - Escalate to supervisors
        # - Document for legal/compliance requirements

    async def _log_safety_event(
        self,
        request: GatewayRequest,
        safety_level: SafetyLevel,
        crisis_indicators: list[CrisisIndicator],
    ) -> None:
        """Log safety event for compliance and monitoring."""
        safety_event = {
            "event_id": f"safety_{request.correlation_id}_{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat(),
            "safety_level": safety_level.value,
            "crisis_indicators": [indicator.value for indicator in crisis_indicators],
            "user_id": (
                request.auth_context.get("user_id") if request.auth_context else None
            ),
            "session_id": (
                request.auth_context.get("therapeutic_session_id")
                if request.auth_context
                else None
            ),
            "path": request.path,
            "method": request.method.value,
            "client_ip": request.client_ip,
            "user_agent": (
                request.headers.get("user-agent") if request.headers else None
            ),
            "therapeutic_context": (
                request.auth_context.get("therapeutic_context")
                if request.auth_context
                else False
            ),
        }

        # Store safety event
        self.safety_events.append(safety_event)

        # Clean up old events (keep only recent events in memory)
        cutoff_time = datetime.utcnow() - timedelta(
            days=self.config.content_retention_days
        )
        self.safety_events = [
            event
            for event in self.safety_events
            if datetime.fromisoformat(event["timestamp"]) > cutoff_time
        ]

        # Log for external systems
        logger.info(
            "Safety event logged",
            extra={"safety_event": safety_event, "compliance_logging": True},
        )

    def add_safety_rule(self, rule: SafetyRule) -> None:
        """Add a custom safety rule."""
        self.safety_rules.append(rule)

    def remove_safety_rule(self, rule_name: str) -> bool:
        """Remove a safety rule by name."""
        for i, rule in enumerate(self.safety_rules):
            if rule.name == rule_name:
                del self.safety_rules[i]
                return True
        return False

    def get_safety_stats(self) -> dict[str, Any]:
        """Get safety statistics and monitoring data."""
        recent_events = [
            event
            for event in self.safety_events
            if datetime.fromisoformat(event["timestamp"])
            > datetime.utcnow() - timedelta(hours=24)
        ]

        return {
            "total_rules": len(self.safety_rules),
            "enabled_rules": len([r for r in self.safety_rules if r.enabled]),
            "active_interventions": len(self.active_interventions),
            "recent_events_24h": len(recent_events),
            "total_events": len(self.safety_events),
            "events_by_level": {
                level.value: len(
                    [e for e in recent_events if e["safety_level"] == level.value]
                )
                for level in SafetyLevel
            },
            "crisis_indicators_detected": {
                indicator.value: len(
                    [
                        e
                        for e in recent_events
                        if indicator.value in e.get("crisis_indicators", [])
                    ]
                )
                for indicator in CrisisIndicator
            },
            "config": {
                "real_time_monitoring": self.config.real_time_monitoring,
                "crisis_intervention": self.config.crisis_intervention,
                "emergency_contact_enabled": self.config.emergency_contact_enabled,
                "compliance_logging": self.config.compliance_logging,
            },
        }

    def get_recent_interventions(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get recent safety interventions."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        return [
            intervention
            for intervention in self.active_interventions.values()
            if datetime.fromisoformat(intervention["timestamp"]) > cutoff_time
        ]

    def clear_old_interventions(self, hours: int = 168) -> int:  # Default 1 week
        """Clear old interventions from memory."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        old_interventions = [
            intervention_id
            for intervention_id, intervention in self.active_interventions.items()
            if datetime.fromisoformat(intervention["timestamp"]) <= cutoff_time
        ]

        for intervention_id in old_interventions:
            del self.active_interventions[intervention_id]

        return len(old_interventions)
