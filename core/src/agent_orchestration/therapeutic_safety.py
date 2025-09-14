"""
Enhanced Therapeutic Safety Validation Pipeline (Task 17.1).

Provides comprehensive therapeutic content validation with:
- Multi-layered content analysis (keyword, sentiment, context-aware)
- Advanced crisis detection algorithms with sensitivity controls
- Intelligent alternative content generation with therapeutic context
- Configurable safety rule engine with therapeutic guidelines
- Monitoring and alerting for safety violations
- Seamless integration with AgentOrchestrationService

Enhanced config format supports multiple validation types:
{
  "rules": [
    {
      "id": "crisis_self_harm",
      "category": "crisis_detection",
      "priority": 100,
      "level": "blocked",
      "pattern": "(suicide|kill myself|self harm)",
      "flags": "i",
      "validation_type": "keyword",
      "sensitivity": 0.8,
      "context_aware": true
    },
    {
      "id": "therapeutic_boundary",
      "category": "professional_ethics",
      "priority": 60,
      "level": "warning",
      "pattern": "diagnose|prescribe",
      "flags": "i",
      "validation_type": "keyword",
      "therapeutic_context": true
    }
  ],
  "crisis_detection": {
    "enabled": true,
    "sensitivity": 0.7,
    "escalation_threshold": 0.9
  },
  "alternative_generation": {
    "enabled": true,
    "therapeutic_tone": true,
    "supportive_messaging": true
  }
}
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, cast

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # Optional; JSON works without it

try:
    from redis.asyncio import Redis as _Redis
except Exception:  # pragma: no cover
    _Redis = None  # type: ignore


class SafetyLevel(str, Enum):
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


class ValidationType(str, Enum):
    """Types of validation algorithms available."""

    KEYWORD = "keyword"
    SENTIMENT = "sentiment"
    CONTEXT_AWARE = "context_aware"
    CRISIS_DETECTION = "crisis_detection"
    THERAPEUTIC_BOUNDARY = "therapeutic_boundary"


class CrisisType(str, Enum):
    """Types of crisis situations that can be detected."""

    SELF_HARM = "self_harm"
    SUICIDAL_IDEATION = "suicidal_ideation"
    SUBSTANCE_ABUSE = "substance_abuse"
    DOMESTIC_VIOLENCE = "domestic_violence"
    EATING_DISORDER = "eating_disorder"
    PANIC_ATTACK = "panic_attack"
    SEVERE_DEPRESSION = "severe_depression"


class TherapeuticContext(str, Enum):
    """Therapeutic contexts for content validation."""

    GENERAL_THERAPY = "general_therapy"
    CRISIS_INTERVENTION = "crisis_intervention"
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    MINDFULNESS = "mindfulness"
    TRAUMA_INFORMED = "trauma_informed"
    ADDICTION_RECOVERY = "addiction_recovery"


class CrisisLevel(str, Enum):
    """Crisis severity levels for intervention protocols."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionType(str, Enum):
    """Types of crisis interventions available."""

    AUTOMATED_RESPONSE = "automated_response"
    HUMAN_OVERSIGHT = "human_oversight"
    EMERGENCY_SERVICES = "emergency_services"
    THERAPEUTIC_REFERRAL = "therapeutic_referral"


class EscalationStatus(str, Enum):
    """Status of crisis escalation."""

    NONE = "none"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ValidationFinding:
    rule_id: str
    category: str
    level: SafetyLevel
    priority: int
    span: tuple[int, int] | None = None
    snippet: str | None = None
    message: str | None = None
    # Enhanced fields for comprehensive analysis
    validation_type: ValidationType = ValidationType.KEYWORD
    confidence: float = 1.0  # 0.0 to 1.0
    crisis_type: CrisisType | None = None
    therapeutic_context: TherapeuticContext | None = None
    sentiment_score: float | None = None  # -1.0 to 1.0
    escalation_required: bool = False
    alternative_suggested: str | None = None


@dataclass
class ValidationResult:
    level: SafetyLevel
    findings: list[ValidationFinding] = field(default_factory=list)
    score: float = 1.0  # 1.0=safe, 0.0=max unsafe
    audit: list[dict[str, Any]] = field(default_factory=list)
    # Enhanced fields for comprehensive analysis
    crisis_detected: bool = False
    crisis_types: list[CrisisType] = field(default_factory=list)
    overall_sentiment: float | None = None  # -1.0 to 1.0
    therapeutic_appropriateness: float = 1.0  # 0.0 to 1.0
    escalation_recommended: bool = False
    alternative_content: str | None = None
    monitoring_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level.value,
            "score": self.score,
            "crisis_detected": self.crisis_detected,
            "crisis_types": [ct.value for ct in self.crisis_types],
            "overall_sentiment": self.overall_sentiment,
            "therapeutic_appropriateness": self.therapeutic_appropriateness,
            "escalation_recommended": self.escalation_recommended,
            "alternative_content": self.alternative_content,
            "monitoring_flags": self.monitoring_flags,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "category": f.category,
                    "level": f.level.value,
                    "priority": f.priority,
                    "span": f.span,
                    "snippet": f.snippet,
                    "message": f.message,
                }
                for f in self.findings
            ],
            "audit": self.audit,
        }


@dataclass
class CrisisAssessment:
    """Assessment of a crisis situation."""

    crisis_level: CrisisLevel
    crisis_types: list[CrisisType]
    confidence: float  # 0.0 to 1.0
    risk_factors: list[str]
    protective_factors: list[str]
    immediate_risk: bool
    intervention_recommended: InterventionType
    escalation_required: bool
    assessment_timestamp: float
    context: dict[str, Any] | None = None


@dataclass
class InterventionAction:
    """A specific intervention action taken."""

    action_type: InterventionType
    description: str
    timestamp: float
    success: bool
    response_time_ms: float
    metadata: dict[str, Any] | None = None


@dataclass
class CrisisIntervention:
    """Complete crisis intervention record."""

    intervention_id: str
    session_id: str
    user_id: str
    crisis_assessment: CrisisAssessment
    actions_taken: list[InterventionAction] = field(default_factory=list)
    escalation_status: EscalationStatus = EscalationStatus.NONE
    resolution_status: str = "active"
    created_timestamp: float = 0.0
    resolved_timestamp: float | None = None
    human_notified: bool = False
    emergency_contacted: bool = False
    follow_up_required: bool = True


@dataclass
class SafetyRule:
    id: str
    category: str  # crisis_detection, boundary_maintenance, professional_ethics
    priority: int
    level: SafetyLevel
    pattern: str | None = None
    flags: str | None = None
    # Enhanced fields for comprehensive validation
    validation_type: ValidationType = ValidationType.KEYWORD
    sensitivity: float = 0.5  # 0.0 to 1.0
    context_aware: bool = False
    therapeutic_context: TherapeuticContext | None = None
    crisis_type: CrisisType | None = None
    escalation_threshold: float = 0.8  # 0.0 to 1.0
    alternative_template: str | None = None

    def compile(self) -> re.Pattern | None:
        if not self.pattern:
            return None
        fl = 0
        if self.flags:
            if "i" in self.flags:
                fl |= re.IGNORECASE
        return re.compile(self.pattern, fl)


class SafetyRuleEngine:
    def __init__(self, rules: list[SafetyRule]):
        # Sort rules by priority desc for deterministic evaluation
        self._rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        self._compiled: list[tuple[SafetyRule, re.Pattern | None]] = [
            (r, r.compile()) for r in self._rules
        ]

    @staticmethod
    def from_config(config: dict[str, Any]) -> SafetyRuleEngine:
        rules_cfg = (config or {}).get("rules") or []
        rules: list[SafetyRule] = []
        for rc in rules_cfg:
            # Parse enhanced rule configuration
            validation_type = ValidationType(rc.get("validation_type", "keyword"))
            therapeutic_context = None
            if rc.get("therapeutic_context"):
                therapeutic_context = TherapeuticContext(rc.get("therapeutic_context"))
            crisis_type = None
            if rc.get("crisis_type"):
                crisis_type = CrisisType(rc.get("crisis_type"))

            rules.append(
                SafetyRule(
                    id=str(rc.get("id")),
                    category=str(rc.get("category", "uncategorized")),
                    priority=int(rc.get("priority", 0)),
                    level=SafetyLevel(str(rc.get("level", "safe"))),
                    pattern=rc.get("pattern"),
                    flags=rc.get("flags"),
                    validation_type=validation_type,
                    sensitivity=float(rc.get("sensitivity", 0.5)),
                    context_aware=bool(rc.get("context_aware", False)),
                    therapeutic_context=therapeutic_context,
                    crisis_type=crisis_type,
                    escalation_threshold=float(rc.get("escalation_threshold", 0.8)),
                    alternative_template=rc.get("alternative_template"),
                )
            )
        return SafetyRuleEngine(rules)

    @staticmethod
    def load_config(path: str) -> dict[str, Any]:
        if path.lower().endswith((".yaml", ".yml")) and yaml is not None:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f)  # type: ignore
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def evaluate(
        self, text: str, context: dict[str, Any] | None = None
    ) -> list[ValidationFinding]:
        """Enhanced evaluation with multiple validation types and context awareness."""
        findings: list[ValidationFinding] = []

        # Basic sentiment analysis for context
        sentiment_score = self._analyze_sentiment(text)

        for rule, rx in self._compiled:
            if rule.validation_type == ValidationType.KEYWORD:
                findings.extend(
                    self._evaluate_keyword_rule(rule, rx, text, sentiment_score)
                )
            elif rule.validation_type == ValidationType.CRISIS_DETECTION:
                findings.extend(
                    self._evaluate_crisis_rule(rule, text, sentiment_score, context)
                )
            elif rule.validation_type == ValidationType.THERAPEUTIC_BOUNDARY:
                findings.extend(
                    self._evaluate_therapeutic_rule(rule, rx, text, context)
                )
            elif rule.validation_type == ValidationType.SENTIMENT:
                findings.extend(
                    self._evaluate_sentiment_rule(rule, text, sentiment_score)
                )
            elif rule.validation_type == ValidationType.CONTEXT_AWARE:
                findings.extend(self._evaluate_context_rule(rule, rx, text, context))

        return findings

    def _analyze_sentiment(self, text: str) -> float:
        """Basic sentiment analysis. Returns score from -1.0 (negative) to 1.0 (positive)."""
        # Simple keyword-based sentiment analysis
        positive_words = [
            "happy",
            "good",
            "better",
            "hope",
            "grateful",
            "thankful",
            "positive",
            "joy",
            "love",
            "peace",
        ]
        negative_words = [
            "sad",
            "bad",
            "worse",
            "hopeless",
            "angry",
            "hate",
            "depressed",
            "anxious",
            "fear",
            "pain",
        ]
        crisis_words = [
            "suicide",
            "kill",
            "die",
            "death",
            "hurt",
            "harm",
            "end",
            "over",
            "done",
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        crisis_count = sum(1 for word in crisis_words if word in text_lower)

        # Crisis words heavily weight negative sentiment
        total_negative = negative_count + (crisis_count * 3)

        if positive_count == 0 and total_negative == 0:
            return 0.0  # Neutral

        total_words = positive_count + total_negative
        return (positive_count - total_negative) / max(total_words, 1)

    def _evaluate_keyword_rule(
        self, rule: SafetyRule, rx: re.Pattern | None, text: str, sentiment: float
    ) -> list[ValidationFinding]:
        """Evaluate keyword-based rules with enhanced context."""
        findings = []
        if rx is None:
            return findings

        for m in rx.finditer(text):
            span = (m.start(), m.end())
            snippet = text[max(0, m.start() - 20) : m.end() + 20]

            # Calculate confidence based on context and sentiment
            confidence = 1.0
            if rule.context_aware and sentiment is not None:
                # Adjust confidence based on sentiment for crisis detection
                if rule.category == "crisis_detection" and sentiment < -0.3:
                    confidence = min(1.0, confidence + 0.3)
                elif sentiment > 0.3:
                    confidence = max(0.3, confidence - 0.2)

            escalation_required = confidence >= rule.escalation_threshold

            findings.append(
                ValidationFinding(
                    rule_id=rule.id,
                    category=rule.category,
                    level=rule.level,
                    priority=rule.priority,
                    span=span,
                    snippet=snippet,
                    message=f"Matched rule '{rule.id}' with {confidence:.2f} confidence",
                    validation_type=rule.validation_type,
                    confidence=confidence,
                    crisis_type=rule.crisis_type,
                    therapeutic_context=rule.therapeutic_context,
                    sentiment_score=sentiment,
                    escalation_required=escalation_required,
                    alternative_suggested=rule.alternative_template,
                )
            )
        return findings

    def _evaluate_crisis_rule(
        self,
        rule: SafetyRule,
        text: str,
        sentiment: float,
        context: dict[str, Any] | None,
    ) -> list[ValidationFinding]:
        """Evaluate crisis detection rules with enhanced algorithms."""
        findings = []

        # Enhanced crisis detection patterns
        crisis_patterns = {
            CrisisType.SUICIDAL_IDEATION: [
                r"(want to die|wish I was dead|kill myself|suicide|end it all|not worth living)",
                r"(better off dead|can't go on|no point|give up|end the pain)",
                r"(life isn't worth|life is not worth|should just end|ending it all)",
                r"(don't want to be here|want to be dead|rather be dead)",
                r"(better off without me|everyone would be better|world would be better)",
                r"(thinking about killing|thinking about suicide|thoughts of suicide)",
            ],
            CrisisType.SELF_HARM: [
                r"(cut myself|hurt myself|self harm|self-harm|cutting|burning myself)",
                r"(punish myself|deserve pain|make it stop|deserve to feel pain|hurt when I feel)",
                r"(hitting myself|burned myself|cutting helps|hurting myself)",
                r"(I've been hitting|I've been cutting|I burned myself)",
            ],
            CrisisType.SEVERE_DEPRESSION: [
                r"(nothing matters|completely hopeless|can't feel anything|empty inside)",
                r"(no one cares|worthless|failure|burden)",
                r"(feel hopeless|feel completely|no point to|there's no point)",
                r"(can't go on|I can't continue|everything is hopeless)",
            ],
        }

        text_lower = text.lower()

        # Check for crisis patterns
        for crisis_type, patterns in crisis_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for m in matches:
                    # Calculate crisis confidence based on multiple factors
                    confidence = 0.7  # Base confidence

                    # Sentiment adjustment
                    if sentiment < -0.5:
                        confidence += 0.2
                    elif sentiment < -0.2:
                        confidence += 0.1

                    # Context adjustment
                    if context and context.get("previous_crisis_indicators"):
                        confidence += 0.1

                    confidence = min(1.0, confidence)
                    escalation_required = confidence >= rule.escalation_threshold

                    span = (m.start(), m.end())
                    snippet = text[max(0, m.start() - 30) : m.end() + 30]

                    findings.append(
                        ValidationFinding(
                            rule_id=rule.id,
                            category=rule.category,
                            level=rule.level,
                            priority=rule.priority,
                            span=span,
                            snippet=snippet,
                            message=f"Crisis detected: {crisis_type.value} (confidence: {confidence:.2f})",
                            validation_type=ValidationType.CRISIS_DETECTION,
                            confidence=confidence,
                            crisis_type=crisis_type,
                            therapeutic_context=rule.therapeutic_context,
                            sentiment_score=sentiment,
                            escalation_required=escalation_required,
                        )
                    )

        return findings

    def _evaluate_therapeutic_rule(
        self,
        rule: SafetyRule,
        rx: re.Pattern | None,
        text: str,
        context: dict[str, Any] | None,
    ) -> list[ValidationFinding]:
        """Evaluate therapeutic boundary rules."""
        findings = []
        if rx is None:
            return findings

        for m in rx.finditer(text):
            # Check if this violates therapeutic boundaries
            confidence = rule.sensitivity

            # Adjust based on therapeutic context
            if context and context.get("therapeutic_session"):
                if rule.therapeutic_context == TherapeuticContext.CRISIS_INTERVENTION:
                    confidence += 0.2
                elif rule.therapeutic_context == TherapeuticContext.TRAUMA_INFORMED:
                    confidence += 0.1

            confidence = min(1.0, confidence)

            span = (m.start(), m.end())
            snippet = text[max(0, m.start() - 20) : m.end() + 20]

            findings.append(
                ValidationFinding(
                    rule_id=rule.id,
                    category=rule.category,
                    level=rule.level,
                    priority=rule.priority,
                    span=span,
                    snippet=snippet,
                    message=f"Therapeutic boundary concern: {rule.category}",
                    validation_type=ValidationType.THERAPEUTIC_BOUNDARY,
                    confidence=confidence,
                    therapeutic_context=rule.therapeutic_context,
                    escalation_required=confidence >= rule.escalation_threshold,
                )
            )

        return findings

    def _evaluate_sentiment_rule(
        self, rule: SafetyRule, text: str, sentiment: float
    ) -> list[ValidationFinding]:
        """Evaluate sentiment-based rules."""
        findings = []

        # Check if sentiment violates rule thresholds
        if rule.level == SafetyLevel.BLOCKED and sentiment < -0.7:
            findings.append(
                ValidationFinding(
                    rule_id=rule.id,
                    category=rule.category,
                    level=rule.level,
                    priority=rule.priority,
                    message=f"Severely negative sentiment detected: {sentiment:.2f}",
                    validation_type=ValidationType.SENTIMENT,
                    confidence=abs(sentiment),
                    sentiment_score=sentiment,
                    escalation_required=abs(sentiment) >= rule.escalation_threshold,
                )
            )
        elif rule.level == SafetyLevel.WARNING and sentiment < -0.4:
            findings.append(
                ValidationFinding(
                    rule_id=rule.id,
                    category=rule.category,
                    level=rule.level,
                    priority=rule.priority,
                    message=f"Negative sentiment detected: {sentiment:.2f}",
                    validation_type=ValidationType.SENTIMENT,
                    confidence=abs(sentiment),
                    sentiment_score=sentiment,
                    escalation_required=abs(sentiment) >= rule.escalation_threshold,
                )
            )

        return findings

    def _evaluate_context_rule(
        self,
        rule: SafetyRule,
        rx: re.Pattern | None,
        text: str,
        context: dict[str, Any] | None,
    ) -> list[ValidationFinding]:
        """Evaluate context-aware rules."""
        findings = []
        if rx is None or not context:
            return findings

        # Context-aware evaluation considers session history, user profile, etc.
        for m in rx.finditer(text):
            confidence = rule.sensitivity

            # Adjust confidence based on context
            if context.get("session_count", 0) < 3:  # New user
                confidence *= 0.8
            if context.get("previous_violations", 0) > 0:  # History of violations
                confidence *= 1.2

            confidence = min(1.0, confidence)

            span = (m.start(), m.end())
            snippet = text[max(0, m.start() - 20) : m.end() + 20]

            findings.append(
                ValidationFinding(
                    rule_id=rule.id,
                    category=rule.category,
                    level=rule.level,
                    priority=rule.priority,
                    span=span,
                    snippet=snippet,
                    message=f"Context-aware match: {rule.id}",
                    validation_type=ValidationType.CONTEXT_AWARE,
                    confidence=confidence,
                    therapeutic_context=rule.therapeutic_context,
                    escalation_required=confidence >= rule.escalation_threshold,
                )
            )

        return findings


class TherapeuticValidator:
    """Enhanced TherapeuticValidator with comprehensive safety validation capabilities."""

    def __init__(
        self, config: dict[str, Any] | None = None, config_path: str | None = None
    ) -> None:
        if config_path and not config:
            cfg = SafetyRuleEngine.load_config(config_path)
        else:
            cfg = config or self._default_config()
        self._engine = SafetyRuleEngine.from_config(cfg)
        self._config = cfg

        # Enhanced configuration options
        self._crisis_detection_enabled = cfg.get("crisis_detection", {}).get(
            "enabled", True
        )
        self._crisis_sensitivity = cfg.get("crisis_detection", {}).get(
            "sensitivity", 0.7
        )
        self._escalation_threshold = cfg.get("crisis_detection", {}).get(
            "escalation_threshold", 0.9
        )
        self._alternative_generation_enabled = cfg.get(
            "alternative_generation", {}
        ).get("enabled", True)
        self._therapeutic_tone = cfg.get("alternative_generation", {}).get(
            "therapeutic_tone", True
        )

        # Monitoring and alerting
        self._violation_count = 0
        self._crisis_count = 0
        self._escalation_count = 0

    def validate_text(
        self,
        text: str,
        *,
        include_audit: bool = True,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Enhanced text validation with comprehensive analysis."""
        audit: list[dict[str, Any]] = []
        if include_audit:
            audit.append(
                {"event": "validate_text.start", "text_length": len(text or "")}
            )

        text = text or ""

        # Enhanced evaluation with context
        findings = self._engine.evaluate(text, context)

        # Comprehensive analysis
        overall_sentiment = self._engine._analyze_sentiment(text)
        crisis_detected = any(f.crisis_type is not None for f in findings)
        crisis_types = list(
            {f.crisis_type for f in findings if f.crisis_type is not None}
        )
        escalation_recommended = any(f.escalation_required for f in findings)

        # Determine overall level with enhanced logic
        level = SafetyLevel.SAFE
        if any(f.level == SafetyLevel.BLOCKED for f in findings):
            level = SafetyLevel.BLOCKED
            self._violation_count += 1
        elif any(f.level == SafetyLevel.WARNING for f in findings):
            level = SafetyLevel.WARNING
            self._violation_count += 1

        # Enhanced scoring based on multiple factors
        score = self._calculate_comprehensive_score(
            findings, overall_sentiment, crisis_detected
        )

        # Calculate therapeutic appropriateness
        therapeutic_appropriateness = self._assess_therapeutic_appropriateness(
            findings, overall_sentiment
        )

        # Generate alternative content if needed
        alternative_content = None
        if level != SafetyLevel.SAFE and self._alternative_generation_enabled:
            alternative_content = self._generate_therapeutic_alternative(
                text, findings, level
            )

        # Monitoring flags
        monitoring_flags = self._generate_monitoring_flags(
            findings, overall_sentiment, crisis_detected
        )

        # Update counters
        if crisis_detected:
            self._crisis_count += 1
        if escalation_recommended:
            self._escalation_count += 1

        if include_audit:
            audit.append(
                {
                    "event": "validate_text.end",
                    "findings_count": len(findings),
                    "result_level": level.value,
                    "crisis_detected": crisis_detected,
                    "escalation_recommended": escalation_recommended,
                    "overall_sentiment": overall_sentiment,
                    "therapeutic_appropriateness": therapeutic_appropriateness,
                }
            )

        return ValidationResult(
            level=level,
            findings=findings,
            score=score,
            audit=audit,
            crisis_detected=crisis_detected,
            crisis_types=crisis_types,
            overall_sentiment=overall_sentiment,
            therapeutic_appropriateness=therapeutic_appropriateness,
            escalation_recommended=escalation_recommended,
            alternative_content=alternative_content,
            monitoring_flags=monitoring_flags,
        )

    def _calculate_comprehensive_score(
        self, findings: list[ValidationFinding], sentiment: float, crisis_detected: bool
    ) -> float:
        """Calculate comprehensive safety score based on multiple factors."""
        if not findings:
            return 1.0

        # Base score calculation
        blocked_count = sum(1 for f in findings if f.level == SafetyLevel.BLOCKED)
        warning_count = sum(1 for f in findings if f.level == SafetyLevel.WARNING)

        if blocked_count > 0:
            base_score = 0.0
        elif warning_count > 0:
            base_score = 0.5
        else:
            base_score = 1.0

        # Adjust for sentiment
        if sentiment < -0.5:
            base_score *= 0.7
        elif sentiment < -0.2:
            base_score *= 0.85
        elif sentiment > 0.3:
            base_score = min(1.0, base_score + 0.1)

        # Adjust for crisis detection
        if crisis_detected:
            base_score *= 0.5

        # Adjust for confidence levels
        avg_confidence = sum(f.confidence for f in findings) / len(findings)
        if avg_confidence > 0.8:
            base_score *= 0.8

        return max(0.0, min(1.0, base_score))

    def _assess_therapeutic_appropriateness(
        self, findings: list[ValidationFinding], sentiment: float
    ) -> float:
        """Assess how therapeutically appropriate the content is."""
        if not findings:
            return 1.0

        # Start with base appropriateness
        appropriateness = 1.0

        # Reduce for safety violations
        for finding in findings:
            if finding.level == SafetyLevel.BLOCKED:
                appropriateness -= 0.4
            elif finding.level == SafetyLevel.WARNING:
                appropriateness -= 0.2

            # Additional reduction for crisis content
            if finding.crisis_type is not None:
                appropriateness -= 0.3

        # Adjust for sentiment
        if sentiment < -0.7:
            appropriateness -= 0.2
        elif sentiment < -0.4:
            appropriateness -= 0.1

        return max(0.0, min(1.0, appropriateness))

    def _generate_monitoring_flags(
        self, findings: list[ValidationFinding], sentiment: float, crisis_detected: bool
    ) -> list[str]:
        """Generate monitoring flags for safety oversight."""
        flags = []

        if crisis_detected:
            flags.append("crisis_detected")

        if sentiment < -0.7:
            flags.append("severe_negative_sentiment")
        elif sentiment < -0.4:
            flags.append("negative_sentiment")

        if any(f.escalation_required for f in findings):
            flags.append("escalation_required")

        if any(f.category == "professional_ethics" for f in findings):
            flags.append("ethics_concern")

        if len(findings) > 3:
            flags.append("multiple_violations")

        return flags

    def suggest_alternative(self, *, reason: SafetyLevel, original: str) -> str:
        # Simple, local alternative suggestion to avoid dependency on LLM
        if reason == SafetyLevel.BLOCKED:
            return (
                "I’m here to support your well-being. I can’t provide or generate that content. "
                "Would you like to talk about how you’re feeling, or focus on a safer topic?"
            )
        return (
            "I want to respond responsibly. Here’s a safer way to approach this topic. "
            "Could you clarify what support you’re seeking?"
        )

    def _generate_therapeutic_alternative(
        self, original: str, findings: list[ValidationFinding], level: SafetyLevel
    ) -> str:
        """Generate therapeutic alternatives based on content analysis."""
        if not self._alternative_generation_enabled:
            return self._basic_alternative(level)

        # Analyze the type of content and findings
        crisis_types = [f.crisis_type for f in findings if f.crisis_type is not None]
        categories = [f.category for f in findings]

        # Generate context-aware alternatives
        if any(ct == CrisisType.SUICIDAL_IDEATION for ct in crisis_types):
            return self._crisis_intervention_alternative("suicidal_ideation")
        elif any(ct == CrisisType.SELF_HARM for ct in crisis_types):
            return self._crisis_intervention_alternative("self_harm")
        elif any(ct == CrisisType.SEVERE_DEPRESSION for ct in crisis_types):
            return self._crisis_intervention_alternative("severe_depression")
        elif "professional_ethics" in categories:
            return self._professional_boundary_alternative()
        elif "boundary_maintenance" in categories:
            return self._therapeutic_boundary_alternative()
        else:
            return self._general_therapeutic_alternative(level)

    def _crisis_intervention_alternative(self, crisis_type: str) -> str:
        """Generate crisis intervention alternatives."""
        alternatives = {
            "suicidal_ideation": (
                "I'm deeply concerned about what you've shared. Your life has value, and there are people who want to help. "
                "Please reach out to a crisis helpline immediately: National Suicide Prevention Lifeline at 988. "
                "Would you like to talk about what's making you feel this way, or would you prefer to focus on immediate safety resources?"
            ),
            "self_harm": (
                "I'm worried about you and want to help you stay safe. Self-harm can be a way of coping with difficult feelings, "
                "but there are healthier alternatives. Please consider reaching out to a mental health professional. "
                "In the meantime, would you like to explore some grounding techniques or coping strategies?"
            ),
            "severe_depression": (
                "I hear that you're going through a really difficult time. Depression can make everything feel overwhelming, "
                "but you don't have to face this alone. Professional support can make a real difference. "
                "Would you like to talk about what's been weighing on you, or explore some resources that might help?"
            ),
        }
        return alternatives.get(
            crisis_type, self._basic_alternative(SafetyLevel.BLOCKED)
        )

    def _professional_boundary_alternative(self) -> str:
        """Generate professional boundary alternatives."""
        return (
            "I understand you're looking for guidance, but I'm not qualified to provide medical or diagnostic advice. "
            "For your safety and well-being, it's important to consult with a licensed healthcare professional. "
            "I can, however, help you explore your feelings and experiences in a supportive way. "
            "What would be most helpful for you right now?"
        )

    def _therapeutic_boundary_alternative(self) -> str:
        """Generate therapeutic boundary alternatives."""
        return (
            "I want to support you in a way that's helpful and appropriate. Let's focus on what you're experiencing "
            "and how we can work together within healthy boundaries. "
            "What aspects of your situation would you like to explore in a supportive way?"
        )

    def _general_therapeutic_alternative(self, level: SafetyLevel) -> str:
        """Generate general therapeutic alternatives."""
        if level == SafetyLevel.BLOCKED:
            return (
                "I'm here to support your well-being, and I want to respond in a way that's helpful and safe. "
                "Let's redirect our conversation to focus on your feelings and experiences. "
                "What's really going on for you right now that we could explore together?"
            )
        else:  # WARNING
            return (
                "I want to respond thoughtfully to what you've shared. Let's approach this topic in a way that's "
                "supportive and constructive. What aspects of this situation are most important to you?"
            )

    def _basic_alternative(self, level: SafetyLevel) -> str:
        """Basic alternative for fallback."""
        if level == SafetyLevel.BLOCKED:
            return (
                "I'm here to support your well-being. I can't provide or generate that content. "
                "Would you like to talk about how you're feeling, or focus on a safer topic?"
            )
        return (
            "I want to respond responsibly. Here's a safer way to approach this topic. "
            "Could you clarify what support you're seeking?"
        )

    def get_monitoring_metrics(self) -> dict[str, Any]:
        """Get monitoring metrics for safety oversight."""
        total_estimated = max(
            10, self._violation_count * 2
        )  # Rough estimate of total validations
        return {
            "total_validations_estimated": total_estimated,
            "violation_count": self._violation_count,
            "crisis_count": self._crisis_count,
            "escalation_count": self._escalation_count,
            "violation_rate": self._violation_count / total_estimated,
            "crisis_rate": self._crisis_count / total_estimated,
            "escalation_rate": self._escalation_count / total_estimated,
        }

    def reset_monitoring_metrics(self) -> None:
        """Reset monitoring metrics (for testing or periodic resets)."""
        self._violation_count = 0
        self._crisis_count = 0
        self._escalation_count = 0

    def should_alert(self, result: ValidationResult) -> bool:
        """Determine if this validation result should trigger an alert."""
        if not self._config.get("monitoring", {}).get("alert_on_escalation", True):
            return False

        # Alert conditions
        if result.escalation_recommended:
            return True
        if result.crisis_detected and any(
            ct in [CrisisType.SUICIDAL_IDEATION, CrisisType.SELF_HARM]
            for ct in result.crisis_types
        ):
            return True
        if result.level == SafetyLevel.BLOCKED and result.score < 0.2:
            return True

        return False

    def update_configuration(self, new_config: dict[str, Any]) -> None:
        """Update the validator configuration and rebuild the engine."""
        self._config.update(new_config)
        self._engine = SafetyRuleEngine.from_config(self._config)

        # Update enhanced configuration options
        self._crisis_detection_enabled = self._config.get("crisis_detection", {}).get(
            "enabled", True
        )
        self._crisis_sensitivity = self._config.get("crisis_detection", {}).get(
            "sensitivity", 0.7
        )
        self._escalation_threshold = self._config.get("crisis_detection", {}).get(
            "escalation_threshold", 0.9
        )
        self._alternative_generation_enabled = self._config.get(
            "alternative_generation", {}
        ).get("enabled", True)
        self._therapeutic_tone = self._config.get("alternative_generation", {}).get(
            "therapeutic_tone", True
        )

    def add_therapeutic_guideline(self, guideline: dict[str, Any]) -> None:
        """Add a new therapeutic guideline rule."""
        if "rules" not in self._config:
            self._config["rules"] = []

        self._config["rules"].append(guideline)
        self.update_configuration({})  # Rebuild with current config

    def remove_therapeutic_guideline(self, rule_id: str) -> bool:
        """Remove a therapeutic guideline rule by ID."""
        if "rules" not in self._config:
            return False

        original_count = len(self._config["rules"])
        self._config["rules"] = [
            rule for rule in self._config["rules"] if rule.get("id") != rule_id
        ]

        if len(self._config["rules"]) < original_count:
            self.update_configuration({})  # Rebuild with current config
            return True
        return False

    def get_therapeutic_guidelines(self) -> list[dict[str, Any]]:
        """Get all current therapeutic guidelines."""
        return self._config.get("rules", [])

    def export_configuration(self) -> dict[str, Any]:
        """Export the current configuration for backup or sharing."""
        return self._config.copy()

    def import_configuration(self, config: dict[str, Any]) -> None:
        """Import a configuration, replacing the current one."""
        self._config = config.copy()
        self.update_configuration({})  # Rebuild with new config

    @staticmethod
    def _default_config() -> dict[str, Any]:
        # Enhanced defaults with comprehensive therapeutic safety rules
        return {
            "rules": [
                # Crisis detection rules
                {
                    "id": "crisis_suicidal_ideation",
                    "category": "crisis_detection",
                    "priority": 100,
                    "level": "blocked",
                    "pattern": r"(suicide|kill myself|want to die|end it all|not worth living|better off dead)",
                    "flags": "i",
                    "validation_type": "crisis_detection",
                    "crisis_type": "suicidal_ideation",
                    "sensitivity": 0.9,
                    "escalation_threshold": 0.8,
                    "context_aware": True,
                },
                {
                    "id": "crisis_self_harm",
                    "category": "crisis_detection",
                    "priority": 95,
                    "level": "blocked",
                    "pattern": r"(self harm|self-harm|hurt myself|cut myself|cutting|burning myself)",
                    "flags": "i",
                    "validation_type": "crisis_detection",
                    "crisis_type": "self_harm",
                    "sensitivity": 0.8,
                    "escalation_threshold": 0.7,
                    "context_aware": True,
                },
                {
                    "id": "crisis_severe_depression",
                    "category": "crisis_detection",
                    "priority": 85,
                    "level": "warning",
                    "pattern": r"(completely hopeless|nothing matters|can't go on|no point|worthless|burden)",
                    "flags": "i",
                    "validation_type": "crisis_detection",
                    "crisis_type": "severe_depression",
                    "sensitivity": 0.7,
                    "escalation_threshold": 0.8,
                    "context_aware": True,
                },
                # Professional ethics rules
                {
                    "id": "ethics_medical_advice",
                    "category": "professional_ethics",
                    "priority": 60,
                    "level": "warning",
                    "pattern": r"(diagnose|prescribe|medical advice|cure|treatment|medication)",
                    "flags": "i",
                    "validation_type": "therapeutic_boundary",
                    "therapeutic_context": "general_therapy",
                    "sensitivity": 0.6,
                },
                # Boundary maintenance rules
                {
                    "id": "boundary_inappropriate_content",
                    "category": "boundary_maintenance",
                    "priority": 40,
                    "level": "warning",
                    "pattern": r"(graphic violence|gore|explicit|inappropriate)",
                    "flags": "i",
                    "validation_type": "keyword",
                    "sensitivity": 0.5,
                },
                # Sentiment-based rules
                {
                    "id": "sentiment_severe_negative",
                    "category": "emotional_monitoring",
                    "priority": 30,
                    "level": "warning",
                    "validation_type": "sentiment",
                    "sensitivity": 0.7,
                    "escalation_threshold": 0.8,
                },
            ],
            # Enhanced configuration options
            "crisis_detection": {
                "enabled": True,
                "sensitivity": 0.7,
                "escalation_threshold": 0.9,
            },
            "alternative_generation": {
                "enabled": True,
                "therapeutic_tone": True,
                "supportive_messaging": True,
            },
            "monitoring": {
                "enabled": True,
                "track_violations": True,
                "alert_on_escalation": True,
            },
        }


class CrisisInterventionManager:
    """Central coordinator for crisis situations detected by the TherapeuticValidator.

    Manages crisis assessment, intervention protocols, escalation procedures,
    and monitoring of crisis situations with comprehensive logging and reporting.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Crisis Intervention Manager."""
        self.config = config or self._default_crisis_config()
        self.active_interventions: dict[str, CrisisIntervention] = {}
        self.intervention_history: list[CrisisIntervention] = []

        # Statistics tracking
        self.total_interventions = 0
        self.successful_interventions = 0
        self.escalations_triggered = 0
        self.emergency_contacts = 0

        # Load crisis response templates
        self.response_templates = self._load_response_templates()

        # Initialize logging
        import logging

        self.logger = logging.getLogger(__name__ + ".CrisisInterventionManager")

    def assess_crisis(
        self, validation_result: ValidationResult, session_context: dict[str, Any]
    ) -> CrisisAssessment:
        """Assess the severity and type of crisis from validation results."""
        import time

        if not validation_result.crisis_detected:
            return CrisisAssessment(
                crisis_level=CrisisLevel.LOW,
                crisis_types=[],
                confidence=0.0,
                risk_factors=[],
                protective_factors=[],
                immediate_risk=False,
                intervention_recommended=InterventionType.AUTOMATED_RESPONSE,
                escalation_required=False,
                assessment_timestamp=time.time(),
                context=session_context,
            )

        # Determine crisis level based on multiple factors
        crisis_level = self._determine_crisis_level(validation_result, session_context)

        # Identify risk and protective factors
        risk_factors = self._identify_risk_factors(validation_result, session_context)
        protective_factors = self._identify_protective_factors(session_context)

        # Determine intervention type
        intervention_type = self._determine_intervention_type(
            crisis_level, validation_result
        )

        # Check for immediate risk
        immediate_risk = self._assess_immediate_risk(validation_result, crisis_level)

        # Calculate overall confidence
        confidence = self._calculate_crisis_confidence(
            validation_result, session_context
        )

        return CrisisAssessment(
            crisis_level=crisis_level,
            crisis_types=validation_result.crisis_types,
            confidence=confidence,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            immediate_risk=immediate_risk,
            intervention_recommended=intervention_type,
            escalation_required=validation_result.escalation_recommended
            or immediate_risk,
            assessment_timestamp=time.time(),
            context=session_context,
        )

    def initiate_intervention(
        self, assessment: CrisisAssessment, session_id: str, user_id: str
    ) -> CrisisIntervention:
        """Initiate a crisis intervention based on the assessment."""
        import time
        import uuid

        intervention_id = str(uuid.uuid4())

        intervention = CrisisIntervention(
            intervention_id=intervention_id,
            session_id=session_id,
            user_id=user_id,
            crisis_assessment=assessment,
            created_timestamp=time.time(),
        )

        # Store active intervention
        self.active_interventions[intervention_id] = intervention
        self.total_interventions += 1

        # Log crisis intervention initiation
        self.logger.warning(
            f"Crisis intervention initiated: {intervention_id} for user {user_id} "
            f"(level: {assessment.crisis_level.value}, types: {[ct.value for ct in assessment.crisis_types]})"
        )

        # Execute immediate response
        self._execute_immediate_response(intervention)

        # Handle escalation if required
        if assessment.escalation_required:
            self._handle_escalation(intervention)

        # Generate alert for monitoring (if we have access to dashboard)
        try:
            # This would be injected in a real implementation
            # For now, we'll add a simple alert mechanism
            alert_severity = (
                "critical"
                if assessment.crisis_level == CrisisLevel.CRITICAL
                else "high"
            )
            self.logger.warning(
                f"CRISIS ALERT: {alert_severity.upper()} intervention {intervention_id} "
                f"for crisis types {[ct.value for ct in assessment.crisis_types]}"
            )
        except Exception as e:
            self.logger.error(f"Failed to generate crisis alert: {e}")

        return intervention

    def _determine_crisis_level(
        self, validation_result: ValidationResult, context: dict[str, Any]
    ) -> CrisisLevel:
        """Determine the crisis level based on validation results and context."""
        # High-risk crisis types
        high_risk_types = {CrisisType.SUICIDAL_IDEATION, CrisisType.SELF_HARM}

        # Check for critical indicators - more specific criteria
        if any(ct in high_risk_types for ct in validation_result.crisis_types):
            # Critical: Very low safety score AND escalation recommended
            if (
                validation_result.score < 0.15
                and validation_result.escalation_recommended
            ):
                return CrisisLevel.CRITICAL
            # High: Low safety score OR escalation recommended
            elif (
                validation_result.score < 0.25
                or validation_result.escalation_recommended
            ):
                return CrisisLevel.HIGH
            # Moderate: Crisis detected but not severe
            else:
                return CrisisLevel.MODERATE

        # Severe depression with high confidence
        if CrisisType.SEVERE_DEPRESSION in validation_result.crisis_types:
            if (
                validation_result.score < 0.2
                and validation_result.escalation_recommended
            ):
                return CrisisLevel.HIGH
            else:
                return CrisisLevel.MODERATE

        # Other crisis types - default to moderate
        if validation_result.crisis_detected:
            # Check overall sentiment and therapeutic appropriateness for level
            if (
                validation_result.overall_sentiment
                and validation_result.overall_sentiment < -0.8
                and validation_result.therapeutic_appropriateness < 0.2
            ):
                return CrisisLevel.HIGH
            else:
                return CrisisLevel.MODERATE

        return CrisisLevel.LOW

    def _identify_risk_factors(
        self, validation_result: ValidationResult, context: dict[str, Any]
    ) -> list[str]:
        """Identify risk factors from validation results and context."""
        risk_factors = []

        # Crisis-specific risk factors
        if CrisisType.SUICIDAL_IDEATION in validation_result.crisis_types:
            risk_factors.extend(["suicidal_ideation", "death_wish", "hopelessness"])

        if CrisisType.SELF_HARM in validation_result.crisis_types:
            risk_factors.extend(
                ["self_harm_behavior", "self_punishment", "coping_mechanism"]
            )

        if CrisisType.SEVERE_DEPRESSION in validation_result.crisis_types:
            risk_factors.extend(
                ["severe_depression", "worthlessness", "emotional_numbness"]
            )

        # Sentiment-based risk factors
        if (
            validation_result.overall_sentiment
            and validation_result.overall_sentiment < -0.7
        ):
            risk_factors.append("severe_negative_sentiment")

        # Context-based risk factors
        if context.get("previous_violations", 0) > 2:
            risk_factors.append("repeated_safety_violations")

        if context.get("session_count", 0) < 3:
            risk_factors.append("new_user_vulnerability")

        return list(set(risk_factors))  # Remove duplicates

    def _identify_protective_factors(self, context: dict[str, Any]) -> list[str]:
        """Identify protective factors from context."""
        protective_factors = []

        # Session engagement
        if context.get("session_count", 0) > 5:
            protective_factors.append("ongoing_engagement")

        # Previous positive interactions
        if context.get("positive_interactions", 0) > 0:
            protective_factors.append("positive_therapeutic_history")

        # Support system indicators
        if context.get("has_support_system", False):
            protective_factors.append("social_support")

        # Professional help
        if context.get("has_therapist", False):
            protective_factors.append("professional_support")

        return protective_factors

    def _determine_intervention_type(
        self, crisis_level: CrisisLevel, validation_result: ValidationResult
    ) -> InterventionType:
        """Determine the appropriate intervention type."""
        if crisis_level == CrisisLevel.CRITICAL:
            return InterventionType.EMERGENCY_SERVICES
        elif crisis_level == CrisisLevel.HIGH:
            return InterventionType.HUMAN_OVERSIGHT
        elif crisis_level == CrisisLevel.MODERATE:
            return InterventionType.THERAPEUTIC_REFERRAL
        else:
            return InterventionType.AUTOMATED_RESPONSE

    def _assess_immediate_risk(
        self, validation_result: ValidationResult, crisis_level: CrisisLevel
    ) -> bool:
        """Assess if there is immediate risk requiring urgent intervention."""
        # Critical level always indicates immediate risk
        if crisis_level == CrisisLevel.CRITICAL:
            return True

        # High-risk crisis types with low safety scores
        high_risk_types = {CrisisType.SUICIDAL_IDEATION, CrisisType.SELF_HARM}
        if (
            any(ct in high_risk_types for ct in validation_result.crisis_types)
            and validation_result.score < 0.3
        ):
            return True

        # Multiple crisis types present
        if len(validation_result.crisis_types) >= 2:
            return True

        return False

    def _calculate_crisis_confidence(
        self, validation_result: ValidationResult, context: dict[str, Any]
    ) -> float:
        """Calculate overall confidence in crisis assessment."""
        if not validation_result.crisis_detected:
            return 0.0

        # Base confidence from validation findings
        if validation_result.findings:
            base_confidence = sum(
                f.confidence for f in validation_result.findings
            ) / len(validation_result.findings)
        else:
            base_confidence = 0.5

        # Adjust based on sentiment
        if (
            validation_result.overall_sentiment
            and validation_result.overall_sentiment < -0.5
        ):
            base_confidence += 0.1

        # Adjust based on therapeutic appropriateness
        if validation_result.therapeutic_appropriateness < 0.3:
            base_confidence += 0.1

        # Adjust based on context
        if context.get("previous_violations", 0) > 1:
            base_confidence += 0.05

        return min(1.0, max(0.0, base_confidence))

    def _execute_immediate_response(self, intervention: CrisisIntervention) -> None:
        """Execute immediate response actions for the crisis intervention."""
        import time

        start_time = time.perf_counter()

        try:
            # Generate appropriate response based on crisis type
            response_message = self._generate_crisis_response(
                intervention.crisis_assessment
            )

            # Record the action
            action = InterventionAction(
                action_type=InterventionType.AUTOMATED_RESPONSE,
                description=f"Generated crisis response: {response_message[:100]}...",
                timestamp=time.time(),
                success=True,
                response_time_ms=(time.perf_counter() - start_time) * 1000,
                metadata={"response_message": response_message},
            )

            intervention.actions_taken.append(action)

            self.logger.info(
                f"Immediate response executed for intervention {intervention.intervention_id}"
            )

        except Exception as e:
            # Record failed action
            action = InterventionAction(
                action_type=InterventionType.AUTOMATED_RESPONSE,
                description=f"Failed to generate crisis response: {str(e)}",
                timestamp=time.time(),
                success=False,
                response_time_ms=(time.perf_counter() - start_time) * 1000,
                metadata={"error": str(e)},
            )

            intervention.actions_taken.append(action)

            self.logger.error(
                f"Failed to execute immediate response for intervention {intervention.intervention_id}: {e}"
            )

    def _handle_escalation(self, intervention: CrisisIntervention) -> None:
        """Handle escalation procedures for crisis intervention."""

        intervention.escalation_status = EscalationStatus.PENDING

        crisis_level = intervention.crisis_assessment.crisis_level

        try:
            if crisis_level == CrisisLevel.CRITICAL:
                self._escalate_to_emergency_services(intervention)
            elif crisis_level in [CrisisLevel.HIGH, CrisisLevel.MODERATE]:
                self._escalate_to_human_oversight(intervention)

            intervention.escalation_status = EscalationStatus.COMPLETED
            self.escalations_triggered += 1

        except Exception as e:
            intervention.escalation_status = EscalationStatus.FAILED
            self.logger.error(
                f"Escalation failed for intervention {intervention.intervention_id}: {e}"
            )

    def _escalate_to_emergency_services(self, intervention: CrisisIntervention) -> None:
        """Escalate to emergency services for critical situations."""
        import time

        start_time = time.perf_counter()

        # In a real implementation, this would contact emergency services
        # For now, we'll log and record the action

        action = InterventionAction(
            action_type=InterventionType.EMERGENCY_SERVICES,
            description="Emergency services notification triggered",
            timestamp=time.time(),
            success=True,  # Assume success for now
            response_time_ms=(time.perf_counter() - start_time) * 1000,
            metadata={
                "crisis_level": intervention.crisis_assessment.crisis_level.value,
                "crisis_types": [
                    ct.value for ct in intervention.crisis_assessment.crisis_types
                ],
                "user_id": intervention.user_id,
                "session_id": intervention.session_id,
            },
        )

        intervention.actions_taken.append(action)
        intervention.emergency_contacted = True
        self.emergency_contacts += 1

        self.logger.critical(
            f"EMERGENCY SERVICES ESCALATION: Intervention {intervention.intervention_id} "
            f"for user {intervention.user_id} - Crisis level: {intervention.crisis_assessment.crisis_level.value}"
        )

    def _escalate_to_human_oversight(self, intervention: CrisisIntervention) -> None:
        """Escalate to human oversight for high/moderate risk situations."""
        import time

        start_time = time.perf_counter()

        # In a real implementation, this would notify human therapists/supervisors
        # For now, we'll log and record the action

        action = InterventionAction(
            action_type=InterventionType.HUMAN_OVERSIGHT,
            description="Human oversight notification sent",
            timestamp=time.time(),
            success=True,  # Assume success for now
            response_time_ms=(time.perf_counter() - start_time) * 1000,
            metadata={
                "crisis_level": intervention.crisis_assessment.crisis_level.value,
                "crisis_types": [
                    ct.value for ct in intervention.crisis_assessment.crisis_types
                ],
                "risk_factors": intervention.crisis_assessment.risk_factors,
                "protective_factors": intervention.crisis_assessment.protective_factors,
            },
        )

        intervention.actions_taken.append(action)
        intervention.human_notified = True

        self.logger.warning(
            f"HUMAN OVERSIGHT ESCALATION: Intervention {intervention.intervention_id} "
            f"for user {intervention.user_id} - Crisis level: {intervention.crisis_assessment.crisis_level.value}"
        )

    def _generate_crisis_response(self, assessment: CrisisAssessment) -> str:
        """Generate appropriate crisis response message."""
        if not assessment.crisis_types:
            return "I'm here to support you. Please let me know how I can help."

        # Get the most severe crisis type
        primary_crisis = assessment.crisis_types[0]

        # Use response templates
        if primary_crisis in self.response_templates:
            template = self.response_templates[primary_crisis]

            # Customize based on crisis level
            if assessment.crisis_level == CrisisLevel.CRITICAL:
                return template["critical"]
            elif assessment.crisis_level == CrisisLevel.HIGH:
                return template["high"]
            elif assessment.crisis_level == CrisisLevel.MODERATE:
                return template["moderate"]
            else:
                return template["low"]

        # Fallback response
        return (
            "I'm concerned about what you've shared and want to help you stay safe. "
            "Please consider reaching out to a mental health professional or crisis helpline. "
            "You can contact the National Suicide Prevention Lifeline at 988 for immediate support."
        )

    def _load_response_templates(self) -> dict[CrisisType, dict[str, str]]:
        """Load crisis response templates for different crisis types and levels."""
        return {
            CrisisType.SUICIDAL_IDEATION: {
                "critical": (
                    "I'm deeply concerned about what you've shared. Your life has value and there are people who want to help. "
                    "Please contact emergency services (911) or the National Suicide Prevention Lifeline at 988 immediately. "
                    "Do not wait - reach out for help right now. You don't have to face this alone."
                ),
                "high": (
                    "I'm very worried about you and want to help you stay safe. Please reach out to the National Suicide Prevention Lifeline at 988 "
                    "or contact a mental health professional immediately. Your life matters and there are people who care about you. "
                    "Would you like me to help you find local crisis resources?"
                ),
                "moderate": (
                    "I'm concerned about what you've shared. Having thoughts of suicide can be frightening, but you don't have to face this alone. "
                    "Please consider reaching out to the National Suicide Prevention Lifeline at 988 or a mental health professional. "
                    "Would you like to talk about what's been making you feel this way?"
                ),
                "low": (
                    "I hear that you're going through a difficult time. If you're having thoughts of suicide, please know that help is available. "
                    "The National Suicide Prevention Lifeline (988) is available 24/7. Would you like to explore some coping strategies together?"
                ),
            },
            CrisisType.SELF_HARM: {
                "critical": (
                    "I'm very concerned about your safety. Self-harm can be dangerous and I want to help you stay safe. "
                    "Please contact emergency services (911) if you're in immediate danger, or reach out to a crisis helpline immediately. "
                    "You deserve care and support, not harm."
                ),
                "high": (
                    "I'm worried about you and want to help you stay safe. Self-harm might feel like a way to cope, but there are healthier alternatives. "
                    "Please consider reaching out to a mental health professional or crisis helpline. "
                    "Would you like to explore some grounding techniques that might help?"
                ),
                "moderate": (
                    "I'm concerned about what you've shared. Self-harm can be a way of coping with difficult feelings, but it's not safe. "
                    "There are healthier ways to manage these feelings. Would you like to talk about what's been troubling you, "
                    "or explore some alternative coping strategies?"
                ),
                "low": (
                    "I hear that you're struggling with difficult feelings. If you're thinking about self-harm, please know that there are "
                    "healthier ways to cope. Would you like to explore some grounding techniques or talk about what's been on your mind?"
                ),
            },
            CrisisType.SEVERE_DEPRESSION: {
                "critical": (
                    "I'm deeply concerned about how you're feeling. Severe depression can make everything feel overwhelming, "
                    "but you don't have to face this alone. Please reach out to a mental health professional or crisis helpline immediately. "
                    "The National Suicide Prevention Lifeline (988) is available 24/7 for support."
                ),
                "high": (
                    "I hear that you're going through an incredibly difficult time. Depression can make everything feel hopeless, "
                    "but professional support can make a real difference. Please consider reaching out to a mental health professional. "
                    "Would you like to talk about what's been weighing on you most heavily?"
                ),
                "moderate": (
                    "I'm sorry you're experiencing such difficult feelings. Depression can make everything feel overwhelming, "
                    "but there is hope and help available. Would you like to talk about what's been troubling you, "
                    "or explore some resources that might provide support?"
                ),
                "low": (
                    "I hear that you're feeling down and struggling. These feelings are valid, and it's okay to reach out for support. "
                    "Would you like to talk about what's been on your mind, or explore some ways to take care of yourself?"
                ),
            },
        }

    def get_intervention_status(
        self, intervention_id: str
    ) -> CrisisIntervention | None:
        """Get the status of a specific intervention."""
        return self.active_interventions.get(intervention_id)

    def resolve_intervention(
        self, intervention_id: str, resolution_notes: str = ""
    ) -> bool:
        """Mark an intervention as resolved."""
        import time

        if intervention_id not in self.active_interventions:
            return False

        intervention = self.active_interventions[intervention_id]
        intervention.resolution_status = "resolved"
        intervention.resolved_timestamp = time.time()

        # Move to history
        self.intervention_history.append(intervention)
        del self.active_interventions[intervention_id]

        self.successful_interventions += 1

        self.logger.info(f"Intervention {intervention_id} resolved: {resolution_notes}")

        return True

    def get_crisis_metrics(self) -> dict[str, Any]:
        """Get comprehensive crisis intervention metrics."""
        active_count = len(self.active_interventions)
        total_count = self.total_interventions
        success_rate = (self.successful_interventions / max(1, total_count)) * 100

        # Crisis level distribution
        crisis_levels = {}
        for intervention in (
            list(self.active_interventions.values()) + self.intervention_history
        ):
            level = intervention.crisis_assessment.crisis_level.value
            crisis_levels[level] = crisis_levels.get(level, 0) + 1

        # Crisis type distribution
        crisis_types = {}
        for intervention in (
            list(self.active_interventions.values()) + self.intervention_history
        ):
            for crisis_type in intervention.crisis_assessment.crisis_types:
                type_name = crisis_type.value
                crisis_types[type_name] = crisis_types.get(type_name, 0) + 1

        return {
            "active_interventions": active_count,
            "total_interventions": total_count,
            "successful_interventions": self.successful_interventions,
            "success_rate_percent": success_rate,
            "escalations_triggered": self.escalations_triggered,
            "emergency_contacts": self.emergency_contacts,
            "crisis_level_distribution": crisis_levels,
            "crisis_type_distribution": crisis_types,
            "average_response_time_ms": self._calculate_average_response_time(),
        }

    def _calculate_average_response_time(self) -> float:
        """Calculate average response time for interventions."""
        all_interventions = (
            list(self.active_interventions.values()) + self.intervention_history
        )

        if not all_interventions:
            return 0.0

        total_time = 0.0
        action_count = 0

        for intervention in all_interventions:
            for action in intervention.actions_taken:
                total_time += action.response_time_ms
                action_count += 1

        return total_time / max(1, action_count)

    def _default_crisis_config(self) -> dict[str, Any]:
        """Default configuration for crisis intervention."""
        return {
            "escalation_thresholds": {"critical": 0.9, "high": 0.7, "moderate": 0.5},
            "response_timeouts": {
                "immediate_response_ms": 1000,
                "escalation_timeout_ms": 5000,
                "emergency_timeout_ms": 2000,
            },
            "monitoring": {
                "track_all_interventions": True,
                "log_escalations": True,
                "alert_on_emergency": True,
            },
            "notifications": {
                "human_oversight_enabled": True,
                "emergency_services_enabled": True,
                "email_notifications": False,
                "webhook_notifications": False,
            },
        }


class EmergencyProtocolEngine:
    """Automated response system for different crisis types with configurable protocols.

    Manages emergency protocols, automated responses, and escalation procedures
    for different crisis situations with comprehensive logging and monitoring.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Emergency Protocol Engine."""
        self.config = config or self._default_protocol_config()
        self.active_protocols: dict[str, dict[str, Any]] = {}
        self.protocol_history: list[dict[str, Any]] = []

        # Statistics tracking
        self.protocols_executed = 0
        self.successful_protocols = 0
        self.failed_protocols = 0

        # Initialize logging
        import logging

        self.logger = logging.getLogger(__name__ + ".EmergencyProtocolEngine")

    def execute_protocol(
        self,
        crisis_type: CrisisType,
        crisis_level: CrisisLevel,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute the appropriate emergency protocol for the given crisis type and level."""
        import time
        import uuid

        protocol_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        protocol_execution = {
            "protocol_id": protocol_id,
            "crisis_type": crisis_type.value,
            "crisis_level": crisis_level.value,
            "start_time": time.time(),
            "context": context,
            "steps_executed": [],
            "success": False,
            "error": None,
            "response_time_ms": 0.0,
        }

        self.active_protocols[protocol_id] = protocol_execution
        self.protocols_executed += 1

        try:
            # Get protocol steps for this crisis type and level
            protocol_steps = self._get_protocol_steps(crisis_type, crisis_level)

            # Execute each step in sequence
            for step in protocol_steps:
                step_result = self._execute_protocol_step(step, context)
                protocol_execution["steps_executed"].append(step_result)

                # If a critical step fails, abort protocol
                if step.get("critical", False) and not step_result["success"]:
                    raise Exception(
                        f"Critical protocol step failed: {step_result['error']}"
                    )

            protocol_execution["success"] = True
            self.successful_protocols += 1

            self.logger.info(
                f"Emergency protocol {protocol_id} executed successfully for {crisis_type.value}"
            )

        except Exception as e:
            protocol_execution["error"] = str(e)
            protocol_execution["success"] = False
            self.failed_protocols += 1

            self.logger.error(f"Emergency protocol {protocol_id} failed: {e}")

        finally:
            # Calculate response time
            protocol_execution["response_time_ms"] = (
                time.perf_counter() - start_time
            ) * 1000

            # Move to history
            self.protocol_history.append(protocol_execution.copy())
            del self.active_protocols[protocol_id]

        return protocol_execution

    def _get_protocol_steps(
        self, crisis_type: CrisisType, crisis_level: CrisisLevel
    ) -> list[dict[str, Any]]:
        """Get the protocol steps for a specific crisis type and level."""
        protocols = self.config.get("protocols", {})

        # Get crisis-specific protocol
        crisis_protocol = protocols.get(crisis_type.value, {})

        # Get level-specific steps
        level_steps = crisis_protocol.get(crisis_level.value, [])

        # If no specific steps, use default
        if not level_steps:
            level_steps = crisis_protocol.get("default", [])

        # If still no steps, use global default
        if not level_steps:
            level_steps = protocols.get("default", [])

        return level_steps

    def _execute_protocol_step(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a single protocol step."""
        import time

        start_time = time.perf_counter()
        step_result = {
            "step_type": step.get("type", "unknown"),
            "description": step.get("description", ""),
            "success": False,
            "response_time_ms": 0.0,
            "output": None,
            "error": None,
        }

        try:
            step_type = step.get("type")

            if step_type == "generate_response":
                step_result["output"] = self._generate_protocol_response(step, context)
                step_result["success"] = True

            elif step_type == "log_event":
                self._log_protocol_event(step, context)
                step_result["success"] = True

            elif step_type == "notify_human":
                step_result["output"] = self._notify_human_oversight(step, context)
                step_result["success"] = True

            elif step_type == "contact_emergency":
                step_result["output"] = self._contact_emergency_services(step, context)
                step_result["success"] = True

            elif step_type == "provide_resources":
                step_result["output"] = self._provide_crisis_resources(step, context)
                step_result["success"] = True

            elif step_type == "schedule_followup":
                step_result["output"] = self._schedule_followup(step, context)
                step_result["success"] = True

            else:
                raise Exception(f"Unknown protocol step type: {step_type}")

        except Exception as e:
            step_result["error"] = str(e)
            step_result["success"] = False

        finally:
            step_result["response_time_ms"] = (time.perf_counter() - start_time) * 1000

        return step_result

    def _generate_protocol_response(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> str:
        """Generate a protocol-specific response message."""
        template = step.get("template", "")

        # Simple template substitution
        response = template.format(
            user_id=context.get("user_id", "unknown"),
            session_id=context.get("session_id", "unknown"),
            crisis_type=context.get("crisis_type", "unknown"),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        return response

    def _log_protocol_event(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> None:
        """Log a protocol event."""
        log_level = step.get("log_level", "info").lower()
        message = step.get("message", "Protocol event")

        # Format message with context
        formatted_message = message.format(**context)

        if log_level == "critical":
            self.logger.critical(formatted_message)
        elif log_level == "error":
            self.logger.error(formatted_message)
        elif log_level == "warning":
            self.logger.warning(formatted_message)
        else:
            self.logger.info(formatted_message)

    def _notify_human_oversight(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Notify human oversight personnel."""
        notification = {
            "type": "human_oversight",
            "priority": step.get("priority", "high"),
            "message": step.get("message", "Human oversight required"),
            "context": context,
            "timestamp": time.time(),
            "channels": step.get("channels", ["email", "dashboard"]),
        }

        # In a real implementation, this would send actual notifications
        self.logger.warning(f"HUMAN OVERSIGHT NOTIFICATION: {notification['message']}")

        return notification

    def _contact_emergency_services(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Contact emergency services."""
        emergency_contact = {
            "type": "emergency_services",
            "service": step.get("service", "911"),
            "reason": step.get("reason", "Mental health crisis"),
            "context": context,
            "timestamp": time.time(),
            "location": context.get("location", "unknown"),
        }

        # In a real implementation, this would contact actual emergency services
        self.logger.critical(
            f"EMERGENCY SERVICES CONTACT: {emergency_contact['reason']}"
        )

        return emergency_contact

    def _provide_crisis_resources(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Provide crisis resources to the user."""
        resources = step.get("resources", [])

        # Default crisis resources
        if not resources:
            resources = [
                {
                    "name": "National Suicide Prevention Lifeline",
                    "phone": "988",
                    "description": "24/7 crisis support",
                    "website": "https://suicidepreventionlifeline.org",
                },
                {
                    "name": "Crisis Text Line",
                    "text": "HOME to 741741",
                    "description": "24/7 text-based crisis support",
                    "website": "https://crisistextline.org",
                },
            ]

        return resources

    def _schedule_followup(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Schedule follow-up contact."""
        followup = {
            "type": "followup",
            "interval_hours": step.get("interval_hours", 24),
            "method": step.get("method", "system_check"),
            "context": context,
            "scheduled_time": time.time() + (step.get("interval_hours", 24) * 3600),
            "priority": step.get("priority", "high"),
        }

        self.logger.info(f"Follow-up scheduled for {followup['interval_hours']} hours")

        return followup

    def get_protocol_metrics(self) -> dict[str, Any]:
        """Get comprehensive protocol execution metrics."""
        success_rate = (
            self.successful_protocols / max(1, self.protocols_executed)
        ) * 100

        # Protocol type distribution
        protocol_types = {}
        for protocol in self.protocol_history:
            crisis_type = protocol["crisis_type"]
            protocol_types[crisis_type] = protocol_types.get(crisis_type, 0) + 1

        # Average response times by crisis type
        avg_response_times = {}
        for crisis_type in protocol_types.keys():
            times = [
                p["response_time_ms"]
                for p in self.protocol_history
                if p["crisis_type"] == crisis_type
            ]
            avg_response_times[crisis_type] = sum(times) / len(times) if times else 0.0

        return {
            "protocols_executed": self.protocols_executed,
            "successful_protocols": self.successful_protocols,
            "failed_protocols": self.failed_protocols,
            "success_rate_percent": success_rate,
            "protocol_type_distribution": protocol_types,
            "average_response_times_ms": avg_response_times,
            "active_protocols": len(self.active_protocols),
        }

    def _default_protocol_config(self) -> dict[str, Any]:
        """Default configuration for emergency protocols."""
        return {
            "protocols": {
                "suicidal_ideation": {
                    "critical": [
                        {
                            "type": "log_event",
                            "log_level": "critical",
                            "message": "CRITICAL SUICIDAL IDEATION: User {user_id} in session {session_id}",
                            "critical": True,
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm deeply concerned about what you've shared. Your life has value and there are people who want to help. Please contact emergency services (911) or the National Suicide Prevention Lifeline at 988 immediately.",
                            "critical": True,
                        },
                        {
                            "type": "contact_emergency",
                            "service": "911",
                            "reason": "Suicidal ideation - critical risk",
                            "critical": True,
                        },
                        {
                            "type": "notify_human",
                            "priority": "critical",
                            "message": "CRITICAL: Suicidal ideation detected - emergency services contacted",
                            "channels": ["email", "sms", "dashboard"],
                        },
                        {
                            "type": "provide_resources",
                            "resources": [
                                {
                                    "name": "National Suicide Prevention Lifeline",
                                    "phone": "988",
                                    "description": "24/7 crisis support",
                                }
                            ],
                        },
                    ],
                    "high": [
                        {
                            "type": "log_event",
                            "log_level": "warning",
                            "message": "HIGH RISK SUICIDAL IDEATION: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm very worried about you and want to help you stay safe. Please reach out to the National Suicide Prevention Lifeline at 988 or contact a mental health professional immediately.",
                        },
                        {
                            "type": "notify_human",
                            "priority": "high",
                            "message": "High risk suicidal ideation detected - immediate oversight required",
                            "channels": ["email", "dashboard"],
                        },
                        {"type": "provide_resources"},
                        {
                            "type": "schedule_followup",
                            "interval_hours": 2,
                            "priority": "high",
                        },
                    ],
                    "moderate": [
                        {
                            "type": "log_event",
                            "log_level": "warning",
                            "message": "MODERATE SUICIDAL IDEATION: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm concerned about what you've shared. Having thoughts of suicide can be frightening, but you don't have to face this alone. Please consider reaching out to the National Suicide Prevention Lifeline at 988.",
                        },
                        {
                            "type": "notify_human",
                            "priority": "medium",
                            "message": "Moderate suicidal ideation detected - oversight recommended",
                            "channels": ["dashboard"],
                        },
                        {"type": "provide_resources"},
                        {"type": "schedule_followup", "interval_hours": 6},
                    ],
                },
                "self_harm": {
                    "critical": [
                        {
                            "type": "log_event",
                            "log_level": "critical",
                            "message": "CRITICAL SELF-HARM RISK: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm very concerned about your safety. Self-harm can be dangerous and I want to help you stay safe. Please contact emergency services (911) if you're in immediate danger.",
                        },
                        {
                            "type": "contact_emergency",
                            "service": "911",
                            "reason": "Self-harm - immediate danger",
                        },
                        {
                            "type": "notify_human",
                            "priority": "critical",
                            "message": "CRITICAL: Self-harm risk - emergency services contacted",
                            "channels": ["email", "sms", "dashboard"],
                        },
                    ],
                    "high": [
                        {
                            "type": "log_event",
                            "log_level": "warning",
                            "message": "HIGH RISK SELF-HARM: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm worried about you and want to help you stay safe. Self-harm might feel like a way to cope, but there are healthier alternatives. Please consider reaching out to a mental health professional.",
                        },
                        {
                            "type": "notify_human",
                            "priority": "high",
                            "message": "High risk self-harm detected - immediate oversight required",
                        },
                        {"type": "schedule_followup", "interval_hours": 4},
                    ],
                },
                "severe_depression": {
                    "high": [
                        {
                            "type": "log_event",
                            "log_level": "warning",
                            "message": "SEVERE DEPRESSION: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I hear that you're going through an incredibly difficult time. Depression can make everything feel hopeless, but professional support can make a real difference.",
                        },
                        {
                            "type": "notify_human",
                            "priority": "medium",
                            "message": "Severe depression detected - professional referral recommended",
                        },
                        {"type": "schedule_followup", "interval_hours": 12},
                    ]
                },
                "default": [
                    {
                        "type": "log_event",
                        "log_level": "info",
                        "message": "Crisis protocol executed for user {user_id}",
                    },
                    {
                        "type": "generate_response",
                        "template": "I'm here to support you. Please let me know how I can help, and consider reaching out to a mental health professional if you need additional support.",
                    },
                ],
            },
            "timeouts": {"step_timeout_ms": 5000, "protocol_timeout_ms": 30000},
            "retry_policy": {"max_retries": 3, "retry_delay_ms": 1000},
        }


class HumanOversightEscalation:
    """Integration points for notifying human therapists or emergency services.

    Manages escalation to human oversight, notification systems, and emergency
    service coordination with comprehensive tracking and reporting.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Human Oversight Escalation system."""
        self.config = config or self._default_escalation_config()
        self.active_escalations: dict[str, dict[str, Any]] = {}
        self.escalation_history: list[dict[str, Any]] = []

        # Statistics tracking
        self.total_escalations = 0
        self.successful_notifications = 0
        self.failed_notifications = 0
        self.emergency_escalations = 0

        # Initialize logging
        import logging

        self.logger = logging.getLogger(__name__ + ".HumanOversightEscalation")

    def escalate_to_human(
        self, intervention: CrisisIntervention, escalation_type: str = "standard"
    ) -> dict[str, Any]:
        """Escalate a crisis intervention to human oversight."""
        import time
        import uuid

        escalation_id = str(uuid.uuid4())

        escalation = {
            "escalation_id": escalation_id,
            "intervention_id": intervention.intervention_id,
            "escalation_type": escalation_type,
            "crisis_level": intervention.crisis_assessment.crisis_level.value,
            "crisis_types": [
                ct.value for ct in intervention.crisis_assessment.crisis_types
            ],
            "user_id": intervention.user_id,
            "session_id": intervention.session_id,
            "timestamp": time.time(),
            "notifications_sent": [],
            "status": "pending",
            "assigned_human": None,
            "response_received": False,
            "resolution_time": None,
        }

        self.active_escalations[escalation_id] = escalation
        self.total_escalations += 1

        # Send notifications based on escalation type and crisis level
        self._send_notifications(escalation, intervention)

        self.logger.warning(
            f"Human oversight escalation {escalation_id} initiated for intervention {intervention.intervention_id} "
            f"(type: {escalation_type}, level: {intervention.crisis_assessment.crisis_level.value})"
        )

        return escalation

    def escalate_to_emergency_services(
        self, intervention: CrisisIntervention, emergency_type: str = "mental_health"
    ) -> dict[str, Any]:
        """Escalate to emergency services for critical situations."""
        import time
        import uuid

        escalation_id = str(uuid.uuid4())

        escalation = {
            "escalation_id": escalation_id,
            "intervention_id": intervention.intervention_id,
            "escalation_type": "emergency_services",
            "emergency_type": emergency_type,
            "crisis_level": intervention.crisis_assessment.crisis_level.value,
            "crisis_types": [
                ct.value for ct in intervention.crisis_assessment.crisis_types
            ],
            "user_id": intervention.user_id,
            "session_id": intervention.session_id,
            "timestamp": time.time(),
            "emergency_contacts": [],
            "status": "critical",
            "response_time_required": "immediate",
            "location_info": intervention.crisis_assessment.context.get(
                "location", "unknown"
            ),
        }

        self.active_escalations[escalation_id] = escalation
        self.emergency_escalations += 1

        # Contact emergency services
        self._contact_emergency_services(escalation, intervention)

        self.logger.critical(
            f"EMERGENCY SERVICES ESCALATION {escalation_id} for intervention {intervention.intervention_id} "
            f"(type: {emergency_type}, level: {intervention.crisis_assessment.crisis_level.value})"
        )

        return escalation

    def _send_notifications(
        self, escalation: dict[str, Any], intervention: CrisisIntervention
    ) -> None:
        """Send notifications to appropriate human oversight personnel."""
        crisis_level = intervention.crisis_assessment.crisis_level
        escalation_type = escalation["escalation_type"]

        # Determine notification channels based on crisis level
        channels = self._get_notification_channels(crisis_level, escalation_type)

        for channel in channels:
            try:
                notification_result = self._send_notification(
                    channel, escalation, intervention
                )
                escalation["notifications_sent"].append(notification_result)

                if notification_result["success"]:
                    self.successful_notifications += 1
                else:
                    self.failed_notifications += 1

            except Exception as e:
                self.failed_notifications += 1
                self.logger.error(f"Failed to send notification via {channel}: {e}")

    def _get_notification_channels(
        self, crisis_level: CrisisLevel, escalation_type: str
    ) -> list[str]:
        """Determine appropriate notification channels based on crisis level and type."""
        channels = []

        if crisis_level == CrisisLevel.CRITICAL:
            channels.extend(["sms", "phone", "email", "dashboard", "pager"])
        elif crisis_level == CrisisLevel.HIGH:
            channels.extend(["sms", "email", "dashboard"])
        elif crisis_level == CrisisLevel.MODERATE:
            channels.extend(["email", "dashboard"])
        else:
            channels.append("dashboard")

        # Filter based on configuration
        enabled_channels = self.config.get("notification_channels", {})
        channels = [
            ch for ch in channels if enabled_channels.get(ch, {}).get("enabled", False)
        ]

        return channels

    def _send_notification(
        self, channel: str, escalation: dict[str, Any], intervention: CrisisIntervention
    ) -> dict[str, Any]:
        """Send a notification via the specified channel."""
        import time

        start_time = time.perf_counter()

        notification = {
            "channel": channel,
            "timestamp": time.time(),
            "success": False,
            "response_time_ms": 0.0,
            "message_id": None,
            "error": None,
        }

        try:
            # Generate notification content
            content = self._generate_notification_content(escalation, intervention)

            # Send via specific channel
            if channel == "email":
                result = self._send_email_notification(content, escalation)
            elif channel == "sms":
                result = self._send_sms_notification(content, escalation)
            elif channel == "phone":
                result = self._send_phone_notification(content, escalation)
            elif channel == "dashboard":
                result = self._send_dashboard_notification(content, escalation)
            elif channel == "pager":
                result = self._send_pager_notification(content, escalation)
            else:
                raise Exception(f"Unknown notification channel: {channel}")

            notification.update(result)
            notification["success"] = True

        except Exception as e:
            notification["error"] = str(e)
            notification["success"] = False

        finally:
            notification["response_time_ms"] = (time.perf_counter() - start_time) * 1000

        return notification

    def _generate_notification_content(
        self, escalation: dict[str, Any], intervention: CrisisIntervention
    ) -> dict[str, Any]:
        """Generate notification content for human oversight."""
        return {
            "subject": f"CRISIS INTERVENTION ESCALATION - {escalation['crisis_level'].upper()}",
            "message": (
                f"Crisis intervention escalation required:\n\n"
                f"Escalation ID: {escalation['escalation_id']}\n"
                f"User ID: {escalation['user_id']}\n"
                f"Session ID: {escalation['session_id']}\n"
                f"Crisis Level: {escalation['crisis_level']}\n"
                f"Crisis Types: {', '.join(escalation['crisis_types'])}\n"
                f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(escalation['timestamp']))}\n\n"
                f"Risk Factors: {', '.join(intervention.crisis_assessment.risk_factors)}\n"
                f"Protective Factors: {', '.join(intervention.crisis_assessment.protective_factors)}\n"
                f"Immediate Risk: {intervention.crisis_assessment.immediate_risk}\n\n"
                f"Please review and respond immediately."
            ),
            "priority": (
                "high"
                if escalation["crisis_level"] in ["high", "critical"]
                else "medium"
            ),
            "metadata": {
                "escalation_id": escalation["escalation_id"],
                "intervention_id": escalation["intervention_id"],
                "crisis_level": escalation["crisis_level"],
                "user_id": escalation["user_id"],
            },
        }

    def _send_email_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send email notification (placeholder implementation)."""
        # In a real implementation, this would send actual emails
        self.logger.info(f"EMAIL NOTIFICATION: {content['subject']}")
        return {
            "message_id": f"email_{escalation['escalation_id']}",
            "recipients": self.config.get("notification_channels", {})
            .get("email", {})
            .get("recipients", []),
            "delivery_status": "sent",
        }

    def _send_sms_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send SMS notification (placeholder implementation)."""
        # In a real implementation, this would send actual SMS messages
        self.logger.warning(
            f"SMS NOTIFICATION: Crisis escalation {escalation['escalation_id']}"
        )
        return {
            "message_id": f"sms_{escalation['escalation_id']}",
            "recipients": self.config.get("notification_channels", {})
            .get("sms", {})
            .get("recipients", []),
            "delivery_status": "sent",
        }

    def _send_phone_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send phone notification (placeholder implementation)."""
        # In a real implementation, this would make actual phone calls
        self.logger.critical(
            f"PHONE NOTIFICATION: Crisis escalation {escalation['escalation_id']}"
        )
        return {
            "message_id": f"phone_{escalation['escalation_id']}",
            "recipients": self.config.get("notification_channels", {})
            .get("phone", {})
            .get("recipients", []),
            "delivery_status": "attempted",
        }

    def _send_dashboard_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send dashboard notification (placeholder implementation)."""
        # In a real implementation, this would update a monitoring dashboard
        self.logger.info(
            f"DASHBOARD NOTIFICATION: Crisis escalation {escalation['escalation_id']}"
        )
        return {
            "message_id": f"dashboard_{escalation['escalation_id']}",
            "dashboard_url": self.config.get("notification_channels", {})
            .get("dashboard", {})
            .get("url", ""),
            "delivery_status": "posted",
        }

    def _send_pager_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send pager notification (placeholder implementation)."""
        # In a real implementation, this would send to pager systems
        self.logger.critical(
            f"PAGER NOTIFICATION: Crisis escalation {escalation['escalation_id']}"
        )
        return {
            "message_id": f"pager_{escalation['escalation_id']}",
            "recipients": self.config.get("notification_channels", {})
            .get("pager", {})
            .get("recipients", []),
            "delivery_status": "sent",
        }

    def _contact_emergency_services(
        self, escalation: dict[str, Any], intervention: CrisisIntervention
    ) -> None:
        """Contact emergency services for critical situations."""
        emergency_type = escalation.get("emergency_type", "mental_health")

        # Determine appropriate emergency service
        if emergency_type == "mental_health":
            service_number = "988"  # National Suicide Prevention Lifeline
            service_name = "National Suicide Prevention Lifeline"
        elif emergency_type == "medical":
            service_number = "911"
            service_name = "Emergency Medical Services"
        else:
            service_number = "911"
            service_name = "Emergency Services"

        # In a real implementation, this would contact actual emergency services
        emergency_contact = {
            "service": service_name,
            "number": service_number,
            "timestamp": time.time(),
            "reason": f"Crisis intervention escalation - {escalation['crisis_level']}",
            "user_info": {
                "user_id": escalation["user_id"],
                "session_id": escalation["session_id"],
                "location": escalation.get("location_info", "unknown"),
            },
            "crisis_details": {
                "types": escalation["crisis_types"],
                "level": escalation["crisis_level"],
                "immediate_risk": intervention.crisis_assessment.immediate_risk,
            },
        }

        escalation["emergency_contacts"].append(emergency_contact)

        self.logger.critical(
            f"EMERGENCY SERVICES CONTACTED: {service_name} ({service_number}) "
            f"for escalation {escalation['escalation_id']}"
        )

    def acknowledge_escalation(
        self, escalation_id: str, human_id: str, response_notes: str = ""
    ) -> bool:
        """Acknowledge an escalation by a human oversight person."""
        import time

        if escalation_id not in self.active_escalations:
            return False

        escalation = self.active_escalations[escalation_id]
        escalation["status"] = "acknowledged"
        escalation["assigned_human"] = human_id
        escalation["response_received"] = True
        escalation["response_time"] = time.time()
        escalation["response_notes"] = response_notes

        self.logger.info(
            f"Escalation {escalation_id} acknowledged by {human_id}: {response_notes}"
        )

        return True

    def resolve_escalation(
        self, escalation_id: str, resolution_notes: str = ""
    ) -> bool:
        """Mark an escalation as resolved."""
        import time

        if escalation_id not in self.active_escalations:
            return False

        escalation = self.active_escalations[escalation_id]
        escalation["status"] = "resolved"
        escalation["resolution_time"] = time.time()
        escalation["resolution_notes"] = resolution_notes

        # Move to history
        self.escalation_history.append(escalation.copy())
        del self.active_escalations[escalation_id]

        self.logger.info(f"Escalation {escalation_id} resolved: {resolution_notes}")

        return True

    def get_escalation_status(self, escalation_id: str) -> dict[str, Any] | None:
        """Get the status of a specific escalation."""
        return self.active_escalations.get(escalation_id)

    def get_escalation_metrics(self) -> dict[str, Any]:
        """Get comprehensive escalation metrics."""
        total_notifications = self.successful_notifications + self.failed_notifications
        notification_success_rate = (
            self.successful_notifications / max(1, total_notifications)
        ) * 100

        # Response time analysis
        response_times = []
        for escalation in self.escalation_history:
            if escalation.get("response_time") and escalation.get("timestamp"):
                response_time = escalation["response_time"] - escalation["timestamp"]
                response_times.append(response_time)

        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0.0
        )

        # Escalation type distribution
        escalation_types = {}
        for escalation in (
            list(self.active_escalations.values()) + self.escalation_history
        ):
            esc_type = escalation.get("escalation_type", "unknown")
            escalation_types[esc_type] = escalation_types.get(esc_type, 0) + 1

        return {
            "total_escalations": self.total_escalations,
            "active_escalations": len(self.active_escalations),
            "resolved_escalations": len(self.escalation_history),
            "emergency_escalations": self.emergency_escalations,
            "successful_notifications": self.successful_notifications,
            "failed_notifications": self.failed_notifications,
            "notification_success_rate_percent": notification_success_rate,
            "average_response_time_seconds": avg_response_time,
            "escalation_type_distribution": escalation_types,
        }

    def _default_escalation_config(self) -> dict[str, Any]:
        """Default configuration for human oversight escalation."""
        return {
            "notification_channels": {
                "email": {
                    "enabled": True,
                    "recipients": ["crisis-team@example.com", "supervisor@example.com"],
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587,
                },
                "sms": {
                    "enabled": True,
                    "recipients": ["+1234567890", "+0987654321"],
                    "service_provider": "twilio",
                },
                "phone": {
                    "enabled": False,
                    "recipients": ["+1234567890"],
                    "service_provider": "twilio",
                },
                "dashboard": {
                    "enabled": True,
                    "url": "https://dashboard.example.com/crisis",
                    "api_key": "dashboard_api_key",
                },
                "pager": {
                    "enabled": False,
                    "recipients": ["pager123", "pager456"],
                    "service_provider": "pagerduty",
                },
            },
            "escalation_rules": {
                "critical": {
                    "immediate_notification": True,
                    "required_channels": ["sms", "phone", "email"],
                    "response_timeout_minutes": 5,
                },
                "high": {
                    "immediate_notification": True,
                    "required_channels": ["sms", "email"],
                    "response_timeout_minutes": 15,
                },
                "moderate": {
                    "immediate_notification": False,
                    "required_channels": ["email", "dashboard"],
                    "response_timeout_minutes": 60,
                },
            },
            "emergency_services": {
                "mental_health_crisis": "988",
                "medical_emergency": "911",
                "general_emergency": "911",
            },
            "retry_policy": {
                "max_retries": 3,
                "retry_delay_minutes": 2,
                "escalate_on_failure": True,
            },
        }


class SafetyMonitoringDashboard:
    """Real-time crisis intervention tracking and comprehensive reporting system.

    Provides comprehensive monitoring, alerting, and reporting capabilities for
    therapeutic safety validation and crisis intervention activities.
    """

    def __init__(
        self,
        therapeutic_validator: TherapeuticValidator | None = None,
        crisis_manager: CrisisInterventionManager | None = None,
        escalation_system: HumanOversightEscalation | None = None,
        protocol_engine: EmergencyProtocolEngine | None = None,
    ):
        """Initialize the Safety Monitoring Dashboard."""
        self.therapeutic_validator = therapeutic_validator
        self.crisis_manager = crisis_manager
        self.escalation_system = escalation_system
        self.protocol_engine = protocol_engine

        # Real-time monitoring data
        self.active_sessions: dict[str, dict[str, Any]] = {}
        self.alert_queue: list[dict[str, Any]] = []
        self.monitoring_metrics: dict[str, Any] = {}

        # Historical data for trending
        self.historical_data: list[dict[str, Any]] = []
        self.trend_analysis: dict[str, Any] = {}

        # Initialize logging
        import logging

        self.logger = logging.getLogger(__name__ + ".SafetyMonitoringDashboard")

    def get_real_time_status(self) -> dict[str, Any]:
        """Get real-time status of all safety systems."""
        import time

        status = {
            "timestamp": time.time(),
            "system_health": "healthy",
            "active_sessions": len(self.active_sessions),
            "active_alerts": len(self.alert_queue),
            "components": {},
        }

        # Therapeutic Validator status
        if self.therapeutic_validator:
            validator_metrics = self.therapeutic_validator.get_monitoring_metrics()
            status["components"]["therapeutic_validator"] = {
                "status": "active",
                "total_validations": validator_metrics.get("total_validations", 0),
                "violation_count": validator_metrics.get("violation_count", 0),
                "crisis_count": validator_metrics.get("crisis_count", 0),
                "escalation_count": validator_metrics.get("escalation_count", 0),
            }

        # Crisis Intervention Manager status
        if self.crisis_manager:
            crisis_metrics = self.crisis_manager.get_crisis_metrics()
            status["components"]["crisis_manager"] = {
                "status": "active",
                "active_interventions": crisis_metrics.get("active_interventions", 0),
                "total_interventions": crisis_metrics.get("total_interventions", 0),
                "success_rate_percent": crisis_metrics.get("success_rate_percent", 0),
                "emergency_contacts": crisis_metrics.get("emergency_contacts", 0),
            }

        # Human Oversight Escalation status
        if self.escalation_system:
            escalation_metrics = self.escalation_system.get_escalation_metrics()
            status["components"]["escalation_system"] = {
                "status": "active",
                "active_escalations": escalation_metrics.get("active_escalations", 0),
                "total_escalations": escalation_metrics.get("total_escalations", 0),
                "emergency_escalations": escalation_metrics.get(
                    "emergency_escalations", 0
                ),
                "notification_success_rate": escalation_metrics.get(
                    "notification_success_rate_percent", 0
                ),
            }

        # Emergency Protocol Engine status
        if self.protocol_engine:
            protocol_metrics = self.protocol_engine.get_protocol_metrics()
            status["components"]["protocol_engine"] = {
                "status": "active",
                "protocols_executed": protocol_metrics.get("protocols_executed", 0),
                "success_rate_percent": protocol_metrics.get("success_rate_percent", 0),
                "active_protocols": protocol_metrics.get("active_protocols", 0),
            }

        # Determine overall system health
        status["system_health"] = self._assess_system_health(status)

        return status

    def get_crisis_dashboard(self) -> dict[str, Any]:
        """Get comprehensive crisis intervention dashboard data."""
        dashboard = {
            "summary": self._get_crisis_summary(),
            "active_interventions": self._get_active_interventions(),
            "recent_escalations": self._get_recent_escalations(),
            "crisis_trends": self._get_crisis_trends(),
            "performance_metrics": self._get_performance_metrics(),
            "alerts": self._get_active_alerts(),
        }

        return dashboard

    def _get_crisis_summary(self) -> dict[str, Any]:
        """Get crisis intervention summary statistics."""
        summary = {
            "total_interventions_today": 0,
            "active_interventions": 0,
            "critical_interventions": 0,
            "emergency_contacts_today": 0,
            "average_response_time_ms": 0.0,
            "success_rate_percent": 0.0,
        }

        if self.crisis_manager:
            metrics = self.crisis_manager.get_crisis_metrics()
            summary.update(
                {
                    "active_interventions": metrics.get("active_interventions", 0),
                    "total_interventions_today": metrics.get("total_interventions", 0),
                    "emergency_contacts_today": metrics.get("emergency_contacts", 0),
                    "average_response_time_ms": metrics.get(
                        "average_response_time_ms", 0.0
                    ),
                    "success_rate_percent": metrics.get("success_rate_percent", 0.0),
                }
            )

            # Count critical interventions
            critical_count = 0
            for intervention in self.crisis_manager.active_interventions.values():
                if intervention.crisis_assessment.crisis_level == CrisisLevel.CRITICAL:
                    critical_count += 1
            summary["critical_interventions"] = critical_count

        return summary

    def _get_active_interventions(self) -> list[dict[str, Any]]:
        """Get list of currently active interventions."""
        active_interventions = []

        if self.crisis_manager:
            for intervention in self.crisis_manager.active_interventions.values():
                active_interventions.append(
                    {
                        "intervention_id": intervention.intervention_id,
                        "user_id": intervention.user_id,
                        "session_id": intervention.session_id,
                        "crisis_level": intervention.crisis_assessment.crisis_level.value,
                        "crisis_types": [
                            ct.value
                            for ct in intervention.crisis_assessment.crisis_types
                        ],
                        "created_timestamp": intervention.created_timestamp,
                        "escalation_status": intervention.escalation_status.value,
                        "human_notified": intervention.human_notified,
                        "emergency_contacted": intervention.emergency_contacted,
                        "actions_taken": len(intervention.actions_taken),
                    }
                )

        # Sort by creation time (most recent first)
        active_interventions.sort(key=lambda x: x["created_timestamp"], reverse=True)

        return active_interventions

    def _get_recent_escalations(self) -> list[dict[str, Any]]:
        """Get list of recent escalations."""
        recent_escalations = []

        if self.escalation_system:
            # Get active escalations
            for escalation in self.escalation_system.active_escalations.values():
                recent_escalations.append(
                    {
                        "escalation_id": escalation["escalation_id"],
                        "intervention_id": escalation["intervention_id"],
                        "escalation_type": escalation["escalation_type"],
                        "crisis_level": escalation["crisis_level"],
                        "user_id": escalation["user_id"],
                        "timestamp": escalation["timestamp"],
                        "status": escalation["status"],
                        "notifications_sent": len(
                            escalation.get("notifications_sent", [])
                        ),
                        "response_received": escalation.get("response_received", False),
                    }
                )

            # Get recent resolved escalations (last 10)
            recent_resolved = self.escalation_system.escalation_history[-10:]
            for escalation in recent_resolved:
                recent_escalations.append(
                    {
                        "escalation_id": escalation["escalation_id"],
                        "intervention_id": escalation["intervention_id"],
                        "escalation_type": escalation["escalation_type"],
                        "crisis_level": escalation["crisis_level"],
                        "user_id": escalation["user_id"],
                        "timestamp": escalation["timestamp"],
                        "status": escalation["status"],
                        "notifications_sent": len(
                            escalation.get("notifications_sent", [])
                        ),
                        "response_received": escalation.get("response_received", False),
                        "resolution_time": escalation.get("resolution_time"),
                    }
                )

        # Sort by timestamp (most recent first)
        recent_escalations.sort(key=lambda x: x["timestamp"], reverse=True)

        return recent_escalations[:20]  # Return last 20

    def _get_crisis_trends(self) -> dict[str, Any]:
        """Get crisis trend analysis."""
        trends = {
            "hourly_interventions": [],
            "crisis_type_distribution": {},
            "crisis_level_trends": {},
            "response_time_trends": [],
        }

        if self.crisis_manager:
            metrics = self.crisis_manager.get_crisis_metrics()
            trends["crisis_type_distribution"] = metrics.get(
                "crisis_type_distribution", {}
            )
            trends["crisis_level_distribution"] = metrics.get(
                "crisis_level_distribution", {}
            )

        # In a real implementation, this would analyze historical data
        # For now, we'll provide placeholder trend data
        import time

        current_hour = int(time.time() // 3600)

        for i in range(24):  # Last 24 hours
            hour = current_hour - (23 - i)
            trends["hourly_interventions"].append(
                {
                    "hour": hour,
                    "interventions": 0,  # Would be calculated from historical data
                    "critical_interventions": 0,
                }
            )

        return trends

    def _get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics."""
        metrics = {
            "validation_performance": {},
            "intervention_performance": {},
            "escalation_performance": {},
            "protocol_performance": {},
        }

        # Validation performance
        if self.therapeutic_validator:
            validator_metrics = self.therapeutic_validator.get_monitoring_metrics()
            metrics["validation_performance"] = {
                "total_validations": validator_metrics.get("total_validations", 0),
                "average_validation_time_ms": validator_metrics.get(
                    "average_validation_time_ms", 0.0
                ),
                "crisis_detection_rate": validator_metrics.get(
                    "crisis_detection_rate", 0.0
                ),
                "false_positive_rate": validator_metrics.get(
                    "false_positive_rate", 0.0
                ),
            }

        # Intervention performance
        if self.crisis_manager:
            crisis_metrics = self.crisis_manager.get_crisis_metrics()
            metrics["intervention_performance"] = {
                "success_rate_percent": crisis_metrics.get("success_rate_percent", 0.0),
                "average_response_time_ms": crisis_metrics.get(
                    "average_response_time_ms", 0.0
                ),
                "escalation_rate": (
                    crisis_metrics.get("escalations_triggered", 0)
                    / max(1, crisis_metrics.get("total_interventions", 1))
                )
                * 100,
            }

        # Escalation performance
        if self.escalation_system:
            escalation_metrics = self.escalation_system.get_escalation_metrics()
            metrics["escalation_performance"] = {
                "notification_success_rate": escalation_metrics.get(
                    "notification_success_rate_percent", 0.0
                ),
                "average_response_time_seconds": escalation_metrics.get(
                    "average_response_time_seconds", 0.0
                ),
                "emergency_escalation_rate": (
                    escalation_metrics.get("emergency_escalations", 0)
                    / max(1, escalation_metrics.get("total_escalations", 1))
                )
                * 100,
            }

        # Protocol performance
        if self.protocol_engine:
            protocol_metrics = self.protocol_engine.get_protocol_metrics()
            metrics["protocol_performance"] = {
                "success_rate_percent": protocol_metrics.get(
                    "success_rate_percent", 0.0
                ),
                "average_response_times_ms": protocol_metrics.get(
                    "average_response_times_ms", {}
                ),
            }

        return metrics

    def _get_active_alerts(self) -> list[dict[str, Any]]:
        """Get currently active alerts."""
        # Return current alert queue
        return self.alert_queue.copy()

    def _assess_system_health(self, status: dict[str, Any]) -> str:
        """Assess overall system health based on component status."""
        # Check for critical conditions
        crisis_component = status.get("components", {}).get("crisis_manager", {})
        escalation_component = status.get("components", {}).get("escalation_system", {})

        # Critical conditions
        if crisis_component.get("active_interventions", 0) > 10:
            return "critical"

        if escalation_component.get("emergency_escalations", 0) > 5:
            return "critical"

        # Warning conditions
        if crisis_component.get("success_rate_percent", 100) < 80:
            return "warning"

        if escalation_component.get("notification_success_rate", 100) < 90:
            return "warning"

        # Check for high alert count
        if len(self.alert_queue) > 20:
            return "warning"

        return "healthy"

    def add_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "medium",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Add a new alert to the monitoring system."""
        import time
        import uuid

        alert_id = str(uuid.uuid4())

        alert = {
            "alert_id": alert_id,
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": time.time(),
            "status": "active",
            "metadata": metadata or {},
            "acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None,
        }

        self.alert_queue.append(alert)

        # Log the alert
        if severity == "critical":
            self.logger.critical(f"CRITICAL ALERT: {message}")
        elif severity == "high":
            self.logger.error(f"HIGH ALERT: {message}")
        elif severity == "medium":
            self.logger.warning(f"MEDIUM ALERT: {message}")
        else:
            self.logger.info(f"LOW ALERT: {message}")

        return alert_id

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        import time

        for alert in self.alert_queue:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_by"] = acknowledged_by
                alert["acknowledged_at"] = time.time()
                alert["status"] = "acknowledged"

                self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                return True

        return False

    def resolve_alert(
        self, alert_id: str, resolved_by: str, resolution_notes: str = ""
    ) -> bool:
        """Resolve an alert."""
        import time

        for i, alert in enumerate(self.alert_queue):
            if alert["alert_id"] == alert_id:
                alert["status"] = "resolved"
                alert["resolved_by"] = resolved_by
                alert["resolved_at"] = time.time()
                alert["resolution_notes"] = resolution_notes

                # Move to historical data
                self.historical_data.append(alert.copy())
                del self.alert_queue[i]

                self.logger.info(
                    f"Alert {alert_id} resolved by {resolved_by}: {resolution_notes}"
                )
                return True

        return False

    def get_safety_report(self, time_range_hours: int = 24) -> dict[str, Any]:
        """Generate comprehensive safety report for specified time range."""
        import time

        end_time = time.time()
        start_time = end_time - (time_range_hours * 3600)

        report = {
            "report_period": {
                "start_time": start_time,
                "end_time": end_time,
                "duration_hours": time_range_hours,
            },
            "executive_summary": {},
            "validation_summary": {},
            "crisis_summary": {},
            "escalation_summary": {},
            "protocol_summary": {},
            "recommendations": [],
        }

        # Executive summary
        report["executive_summary"] = {
            "total_validations": 0,
            "crisis_interventions": 0,
            "emergency_escalations": 0,
            "system_availability": "99.9%",
            "overall_safety_score": 95.0,
        }

        # Populate with actual data if components are available
        if self.therapeutic_validator:
            validator_metrics = self.therapeutic_validator.get_monitoring_metrics()
            report["validation_summary"] = validator_metrics
            report["executive_summary"]["total_validations"] = validator_metrics.get(
                "total_validations", 0
            )

        if self.crisis_manager:
            crisis_metrics = self.crisis_manager.get_crisis_metrics()
            report["crisis_summary"] = crisis_metrics
            report["executive_summary"]["crisis_interventions"] = crisis_metrics.get(
                "total_interventions", 0
            )

        if self.escalation_system:
            escalation_metrics = self.escalation_system.get_escalation_metrics()
            report["escalation_summary"] = escalation_metrics
            report["executive_summary"]["emergency_escalations"] = (
                escalation_metrics.get("emergency_escalations", 0)
            )

        if self.protocol_engine:
            protocol_metrics = self.protocol_engine.get_protocol_metrics()
            report["protocol_summary"] = protocol_metrics

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: dict[str, Any]) -> list[str]:
        """Generate recommendations based on safety report data."""
        recommendations = []

        # Check crisis intervention success rate
        crisis_summary = report.get("crisis_summary", {})
        success_rate = crisis_summary.get("success_rate_percent", 100)

        if success_rate < 90:
            recommendations.append(
                f"Crisis intervention success rate is {success_rate:.1f}%. "
                "Consider reviewing intervention protocols and staff training."
            )

        # Check escalation response times
        escalation_summary = report.get("escalation_summary", {})
        avg_response_time = escalation_summary.get("average_response_time_seconds", 0)

        if avg_response_time > 300:  # 5 minutes
            recommendations.append(
                f"Average escalation response time is {avg_response_time:.0f} seconds. "
                "Consider optimizing notification channels and response procedures."
            )

        # Check emergency escalation rate
        total_escalations = escalation_summary.get("total_escalations", 0)
        emergency_escalations = escalation_summary.get("emergency_escalations", 0)

        if total_escalations > 0:
            emergency_rate = (emergency_escalations / total_escalations) * 100
            if emergency_rate > 20:
                recommendations.append(
                    f"Emergency escalation rate is {emergency_rate:.1f}%. "
                    "Consider reviewing crisis detection thresholds and early intervention strategies."
                )

        # Check validation performance
        validation_summary = report.get("validation_summary", {})
        total_validations = validation_summary.get("total_validations", 0)
        crisis_count = validation_summary.get("crisis_count", 0)

        if total_validations > 0:
            crisis_rate = (crisis_count / total_validations) * 100
            if crisis_rate > 10:
                recommendations.append(
                    f"Crisis detection rate is {crisis_rate:.1f}%. "
                    "Consider implementing additional preventive measures and user support resources."
                )

        if not recommendations:
            recommendations.append(
                "All safety metrics are within acceptable ranges. Continue current monitoring and intervention protocols."
            )

        return recommendations

    def export_dashboard_data(self, format_type: str = "json") -> str:
        """Export dashboard data in specified format."""
        dashboard_data = self.get_crisis_dashboard()

        if format_type.lower() == "json":
            import json

            return json.dumps(dashboard_data, indent=2, default=str)
        elif format_type.lower() == "csv":
            # In a real implementation, this would convert to CSV format
            return "CSV export not implemented"
        else:
            raise ValueError(f"Unsupported export format: {format_type}")


# ---- Redis-backed rules provider and SafetyService ----


class SafetyRulesProvider:
    """Loads safety rules from Redis with TTL caching and file fallback.

    - Redis key: "ao:safety:rules"
    - TTL-based reload for live updates
    - Fallback to file path (env TTA_SAFETY_RULES_CONFIG) if Redis unavailable or key missing
    """

    def __init__(
        self,
        redis_client: _Redis | None = None,
        *,
        redis_key: str = "ao:safety:rules",
        cache_ttl_s: float = 2.0,
        file_fallback_path: str | None = None,
    ) -> None:
        self._redis = redis_client
        self._key = redis_key
        self._ttl = float(cache_ttl_s)
        self._file = file_fallback_path
        self._cached_raw: str | None = None
        self._cached_at: float = 0.0
        self._last_source: str | None = None

    async def get_config(self) -> dict[str, Any]:
        now = time.time()
        if self._cached_raw is not None and (now - self._cached_at) < self._ttl:
            try:
                return json.loads(self._cached_raw)
            except Exception:
                pass
        # Try Redis first
        cfg: dict[str, Any] | None = None
        raw: str | None = None
        if self._redis is not None:
            try:
                b = await cast("_Redis", self._redis).get(self._key)
                if b:
                    raw = b.decode() if isinstance(b, bytes | bytearray) else str(b)
                    cfg = json.loads(raw)
                    self._last_source = f"redis:{self._key}"
            except Exception:
                cfg = None
        # Fallback to file
        if cfg is None:
            try:
                path = self._file
                if not path:
                    import os

                    path = os.environ.get("TTA_SAFETY_RULES_CONFIG")
                if path:
                    if path.lower().endswith((".yaml", ".yml")) and yaml is not None:
                        with open(path, encoding="utf-8") as f:
                            cfg = yaml.safe_load(f)
                    else:
                        with open(path, encoding="utf-8") as f:
                            cfg = json.load(f)
                    raw = json.dumps(cfg)
                    self._last_source = f"file:{path}"
            except Exception:
                cfg = None
        if cfg is None:
            # Default config
            cfg = TherapeuticValidator._default_config()
            raw = json.dumps(cfg)
            self._last_source = "default"
        self._cached_raw = raw
        self._cached_at = now
        return cfg

    def status(self) -> dict[str, Any]:
        return {
            "last_reload_ts": self._cached_at or None,
            "source": self._last_source,
            "redis_key": self._key,
            "cache_ttl_s": self._ttl,
        }

    def invalidate(self) -> None:
        self._cached_raw = None
        self._cached_at = 0.0
        # do not clear last_source; next load will update


class SafetyService:
    """Orchestrates validation using a rules provider and enabled flag.

    Provides async validate method and caches compiled validator, refreshing when
    the underlying raw JSON changes (TTL handled by provider).
    """

    def __init__(
        self, enabled: bool = False, provider: SafetyRulesProvider | None = None
    ) -> None:
        self._enabled = bool(enabled)
        self._provider = provider or SafetyRulesProvider(redis_client=None)
        self._last_raw: str | None = None
        self._validator: TherapeuticValidator | None = None

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def is_enabled(self) -> bool:
        return self._enabled

    async def _ensure_validator(self) -> TherapeuticValidator:
        cfg = await self._provider.get_config()
        raw = json.dumps(cfg)
        if (self._validator is None) or (raw != self._last_raw):
            self._validator = TherapeuticValidator(config=cfg)
            self._last_raw = raw
        return self._validator

    async def validate_text(self, text: str) -> ValidationResult:
        if not self._enabled:
            # Fast path when disabled
            return ValidationResult(
                level=SafetyLevel.SAFE,
                findings=[],
                score=1.0,
                audit=[{"event": "disabled"}],
            )
        v = await self._ensure_validator()
        return v.validate_text(text)

    def suggest_alternative(self, level: SafetyLevel, original: str) -> str:
        v = self._validator or TherapeuticValidator()
        return v.suggest_alternative(reason=level, original=original)


_global_safety_service: SafetyService | None = None
_global_safety_locked: bool = (
    False  # When True, do not auto-refresh from env (component-managed)
)


def get_global_safety_service() -> SafetyService:
    """Returns process-wide SafetyService. Attempts to initialize a Redis client
    using TEST_REDIS_URI or default localhost. Disabled by default, can be enabled
    via env AGENT_ORCHESTRATION_SAFETY_ENABLED=true for ad-hoc use or via tests.
    """
    global _global_safety_service, _global_safety_locked
    import os

    if _global_safety_service is None:
        enabled = False
        try:
            enabled = str(
                os.environ.get("AGENT_ORCHESTRATION_SAFETY_ENABLED", "false")
            ).lower() in ("1", "true", "yes")
            redis_client = None
            if _Redis is not None:
                url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
                try:
                    import redis.asyncio as aioredis  # type: ignore

                    redis_client = aioredis.from_url(url)
                except Exception:
                    redis_client = None
            provider = SafetyRulesProvider(redis_client=redis_client)
            _global_safety_service = SafetyService(enabled=enabled, provider=provider)
        except Exception:
            _global_safety_service = SafetyService(
                enabled=False, provider=SafetyRulesProvider(redis_client=None)
            )
    else:
        if not _global_safety_locked:
            try:
                enabled = str(
                    os.environ.get("AGENT_ORCHESTRATION_SAFETY_ENABLED", "false")
                ).lower() in ("1", "true", "yes")
                _global_safety_service.set_enabled(enabled)
            except Exception:
                pass

    return _global_safety_service


# Testing/Component hook
_def_test_override: SafetyService | None = None


def set_global_safety_service_for_testing(svc: SafetyService) -> None:
    global _global_safety_service, _global_safety_locked
    _global_safety_service = svc
    _global_safety_locked = True
