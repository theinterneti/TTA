"""Therapeutic content validation with comprehensive safety analysis.

Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Therapeutic_scoring/Validator]]
"""

from __future__ import annotations

from typing import Any

from ..safety_validation.engine import SafetyRuleEngine
from ..safety_validation.enums import SafetyLevel
from ..safety_validation.models import SafetyRule, ValidationResult


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
        self._crisis_detection_enabled = cfg.get("crisis_detection", {}).get("enabled", True)
        self._crisis_sensitivity = cfg.get("crisis_detection", {}).get("sensitivity", 0.7)
        self._escalation_threshold = cfg.get("crisis_detection", {}).get(
            "escalation_threshold", 0.9
        )
        self._alternative_generation_enabled = cfg.get("alternative_generation", {}).get(
            "enabled", True
        )
        self._therapeutic_tone = cfg.get("alternative_generation", {}).get("therapeutic_tone", True)

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
            audit.append({"event": "validate_text.start", "text_length": len(text or "")})

        text = text or ""

        # Enhanced evaluation with context
        findings = self._engine.evaluate(text, context)

        # Comprehensive analysis
        overall_sentiment = self._engine._analyze_sentiment(text)
        crisis_detected = any(f.crisis_type is not None for f in findings)
        crisis_types = list({f.crisis_type for f in findings if f.crisis_type is not None})
        # Crisis detection always recommends escalation for safety
        escalation_recommended = crisis_detected or any(f.escalation_required for f in findings)

        # Determine overall level with enhanced logic
        level = SafetyLevel.SAFE
        if any(f.level == SafetyLevel.BLOCKED for f in findings):
            level = SafetyLevel.BLOCKED
            self._violation_count += 1
        elif any(f.level == SafetyLevel.WARNING for f in findings):
            level = SafetyLevel.WARNING
            self._violation_count += 1

        # Enhanced scoring based on multiple factors
        score = self._calculate_comprehensive_score(findings, overall_sentiment, crisis_detected)

        # Calculate therapeutic appropriateness
        therapeutic_appropriateness = self._assess_therapeutic_appropriateness(
            findings, overall_sentiment
        )

        # Generate alternative content if needed
        alternative_content = None
        if level != SafetyLevel.SAFE and self._alternative_generation_enabled:
            alternative_content = self._generate_therapeutic_alternative(text, findings, level)

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
                    "level": level.value,
                    "findings_count": len(findings),
                    "crisis_detected": crisis_detected,
                }
            )

        return ValidationResult(
            level=level,
            findings=findings,
            score=score,
            audit=audit if include_audit else [],
            crisis_detected=crisis_detected,
            crisis_types=crisis_types,
            escalation_recommended=escalation_recommended,
            overall_sentiment=overall_sentiment,
            therapeutic_appropriateness=therapeutic_appropriateness,
            alternative_content=alternative_content,
            monitoring_flags=monitoring_flags,
        )

    def suggest_alternative(
        self, original: str, reason: SafetyLevel, findings: list[Any] | None = None
    ) -> str | None:
        """
        Suggest a therapeutic alternative for the given text.

        Args:
            original: The original text
            reason: The safety level/reason
            findings: List of safety findings (optional)

        Returns:
            Suggested alternative text or None
        """
        return self._generate_therapeutic_alternative(original, findings or [], reason)

    def _calculate_comprehensive_score(
        self,
        findings: list[Any],
        sentiment_score: float,
        crisis_detected: bool,
    ) -> float:
        """Calculate comprehensive safety score based on multiple factors."""
        if not findings:
            # Adjust base score based on sentiment
            if sentiment_score < -0.5:
                return 0.7  # Negative sentiment reduces score
            if sentiment_score > 0.5:
                return 1.0  # Positive sentiment maintains high score
            return 0.9  # Neutral sentiment

        # Start with base score
        base_score = 1.0

        # Penalty for findings
        for finding in findings:
            if finding.level == SafetyLevel.BLOCKED:
                base_score -= 0.3
            elif finding.level == SafetyLevel.WARNING:
                base_score -= 0.15

        # Additional penalty for crisis detection
        if crisis_detected:
            base_score -= 0.2

        # Sentiment adjustment
        base_score += sentiment_score * 0.1

        # Ensure score is in valid range
        return max(0.0, min(1.0, base_score))

    def _assess_therapeutic_appropriateness(
        self, findings: list[Any], sentiment_score: float
    ) -> float:
        """Assess therapeutic appropriateness of content."""
        # No violations: base on sentiment
        if not findings:
            if sentiment_score >= 0:
                return min(1.0, 0.8 + sentiment_score * 0.2)
            elif sentiment_score > -0.3:
                return 0.7
            else:
                return 0.6

        # Start high and reduce for violations
        appropriateness = 1.0
        for finding in findings:
            if finding.level == SafetyLevel.BLOCKED:
                appropriateness -= 0.4
            elif finding.level == SafetyLevel.WARNING:
                appropriateness -= 0.2

        # Ensure appropriateness is in valid range
        return max(0.0, min(1.0, appropriateness))

    def _generate_therapeutic_alternative(
        self,
        text: str,
        findings: list[Any],
        level: SafetyLevel,
    ) -> str | None:
        """Generate therapeutic alternative content."""
        if not self._therapeutic_tone:
            return None

        # Use crisis-type specific responses for better therapeutic support
        crisis_types = {
            getattr(f, "crisis_type", None) for f in findings if getattr(f, "crisis_type", None)
        }

        if "suicidal_ideation" in crisis_types:
            return (
                "I'm concerned about your safety. Please reach out to a crisis helpline "
                "right away. The 988 Suicide and Crisis Lifeline is available 24/7 — "
                "just call or text 988. You don't have to face this alone — help is available."
            )

        if "self_harm" in crisis_types:
            return (
                "I want you to stay safe. When you feel the urge to harm yourself, "
                "try grounding techniques like the 5-4-3-2-1 method: name 5 things you "
                "see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. "
                "I'm here to support you."
            )

        # Check for professional boundary violations (ethics rules)
        has_ethics_violation = any(
            "ethics" in (getattr(f, "category", "") or "")
            or "ethics" in (getattr(f, "rule_id", "") or "")
            for f in findings
        )
        if has_ethics_violation:
            return (
                "I'm not qualified to provide medical diagnoses or professional advice. "
                "For concerns like this, please consult a licensed healthcare professional "
                "or mental health provider who can give you proper support and guidance."
            )

        # Generic alternatives for other violations
        if level == SafetyLevel.BLOCKED:
            return (
                "I understand you're going through a difficult time. "
                "Let's focus on finding healthy ways to cope with these feelings. "
                "I'm here to support you. "
                "Would you like to talk about what's troubling you?"
            )
        if level == SafetyLevel.WARNING:
            return (
                "I want to respond responsibly. "
                "I hear that you're struggling. It's important to approach this "
                "in a way that supports your wellbeing. Can we explore this together "
                "in a more constructive way?"
            )

        return None

    def _generate_monitoring_flags(
        self, findings: list[Any], sentiment_score: float, crisis_detected: bool
    ) -> list[str]:
        """Generate monitoring flags for safety tracking."""
        flags = []

        if crisis_detected:
            flags.append("crisis_detected")

        if sentiment_score < -0.7:
            flags.append("severe_negative_sentiment")
        elif sentiment_score < -0.3:
            flags.append("negative_sentiment")

        if any(f.escalation_required for f in findings):
            flags.append("escalation_required")

        if any(f.level == SafetyLevel.BLOCKED for f in findings):
            flags.append("content_blocked")

        return flags

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation statistics."""
        return {
            "total_violations": self._violation_count,
            "crisis_detections": self._crisis_count,
            "escalations": self._escalation_count,
        }

    def get_therapeutic_guidelines(self) -> list[dict[str, Any]]:
        """Get all therapeutic guidelines/rules as a list of dicts."""
        return [
            {
                "id": rule.id,
                "category": rule.category,
                "priority": rule.priority,
                "level": rule.level.value if hasattr(rule.level, "value") else rule.level,
                "pattern": rule.pattern,
                "validation_type": (
                    rule.validation_type.value
                    if hasattr(rule.validation_type, "value")
                    else rule.validation_type
                ),
                "sensitivity": rule.sensitivity,
            }
            for rule in self._engine._rules
        ]

    def add_therapeutic_guideline(self, guideline: dict[str, Any]) -> None:
        """Add a new therapeutic guideline/rule."""
        from ..safety_validation.enums import SafetyLevel as SL
        from ..safety_validation.enums import ValidationType as VT

        rule = SafetyRule(
            id=guideline["id"],
            category=guideline.get("category", "custom"),
            priority=guideline.get("priority", 50),
            level=SL(guideline.get("level", "warning")),
            pattern=guideline.get("pattern"),
            validation_type=VT(guideline.get("validation_type", "keyword")),
            sensitivity=guideline.get("sensitivity", 0.5),
        )
        self._engine._rules.append(rule)
        self._engine._compiled.append((rule, rule.compile()))

    def remove_therapeutic_guideline(self, rule_id: str) -> bool:
        """Remove a therapeutic guideline by ID. Returns True if found and removed."""
        original_len = len(self._engine._rules)
        self._engine._rules = [r for r in self._engine._rules if r.id != rule_id]
        self._engine._compiled = [(r, c) for r, c in self._engine._compiled if r.id != rule_id]
        return len(self._engine._rules) < original_len

    def get_monitoring_metrics(self) -> dict[str, Any]:
        """Get monitoring metrics for the validator."""
        return {
            "violation_count": self._violation_count,
            "crisis_count": self._crisis_count,
            "escalation_count": self._escalation_count,
        }

    def should_alert(self, result: Any) -> bool:
        """Check if a validation result should trigger an alert."""
        return result.crisis_detected or result.escalation_recommended

    def export_configuration(self) -> dict[str, Any]:
        """Export current configuration as a dict."""
        return {
            "rules": self.get_therapeutic_guidelines(),
            "crisis_detection": {
                "enabled": self._crisis_detection_enabled,
                "sensitivity": self._crisis_sensitivity,
                "escalation_threshold": self._escalation_threshold,
            },
            "alternative_generation": {
                "enabled": self._alternative_generation_enabled,
                "therapeutic_tone": self._therapeutic_tone,
            },
        }

    def import_configuration(self, config: dict[str, Any]) -> None:
        """Import configuration from a dict, replacing current rules."""
        self._engine = SafetyRuleEngine.from_config(config)
        self._config = config
        self._crisis_detection_enabled = config.get("crisis_detection", {}).get("enabled", True)
        self._crisis_sensitivity = config.get("crisis_detection", {}).get("sensitivity", 0.7)
        self._escalation_threshold = config.get("crisis_detection", {}).get(
            "escalation_threshold", 0.9
        )
        self._alternative_generation_enabled = config.get("alternative_generation", {}).get(
            "enabled", True
        )
        self._therapeutic_tone = config.get("alternative_generation", {}).get(
            "therapeutic_tone", True
        )

    def update_configuration(self, update_config: dict[str, Any]) -> None:
        """Update configuration with partial updates."""
        if "crisis_detection" in update_config:
            cd = update_config["crisis_detection"]
            if "enabled" in cd:
                self._crisis_detection_enabled = cd["enabled"]
            if "sensitivity" in cd:
                self._crisis_sensitivity = cd["sensitivity"]
            if "escalation_threshold" in cd:
                self._escalation_threshold = cd["escalation_threshold"]
        if "alternative_generation" in update_config:
            ag = update_config["alternative_generation"]
            if "enabled" in ag:
                self._alternative_generation_enabled = ag["enabled"]
            if "therapeutic_tone" in ag:
                self._therapeutic_tone = ag["therapeutic_tone"]

    def _default_config(self) -> dict[str, Any]:
        """Default configuration for therapeutic validation."""
        return {
            "rules": [
                # Crisis detection rules
                {
                    "id": "crisis_suicidal_ideation",
                    "category": "crisis_detection",
                    "priority": 100,
                    "level": "blocked",
                    "pattern": r"(suicide|kill myself|end my life|want to die|better off dead)",
                    "flags": "i",
                    "validation_type": "crisis_detection",
                    "crisis_type": "suicidal_ideation",
                    "sensitivity": 0.9,
                    "escalation_threshold": 0.95,
                    "context_aware": True,
                },
                {
                    "id": "crisis_self_harm",
                    "category": "crisis_detection",
                    "priority": 95,
                    "level": "blocked",
                    "pattern": r"(self harm|cut myself|hurt myself|self-injury)",
                    "flags": "i",
                    "validation_type": "crisis_detection",
                    "crisis_type": "self_harm",
                    "sensitivity": 0.85,
                    "escalation_threshold": 0.9,
                    "context_aware": True,
                },
                {
                    "id": "crisis_substance_abuse",
                    "category": "crisis_detection",
                    "priority": 90,
                    "level": "warning",
                    "pattern": r"(overdose|too many pills|drinking too much|substance abuse)",
                    "flags": "i",
                    "validation_type": "crisis_detection",
                    "crisis_type": "substance_abuse",
                    "sensitivity": 0.75,
                    "escalation_threshold": 0.85,
                    "context_aware": True,
                },
                {
                    "id": "crisis_domestic_violence",
                    "category": "crisis_detection",
                    "priority": 85,
                    "level": "warning",
                    "pattern": r"(domestic violence|partner hurts me|afraid of|being abused)",
                    "flags": "i",
                    "validation_type": "crisis_detection",
                    "crisis_type": "domestic_violence",
                    "sensitivity": 0.8,
                    "escalation_threshold": 0.9,
                    "context_aware": True,
                },
                {
                    "id": "crisis_eating_disorder",
                    "category": "crisis_detection",
                    "priority": 80,
                    "level": "warning",
                    "pattern": r"(starving myself|purging|binge eating|anorexia|bulimia)",
                    "flags": "i",
                    "validation_type": "crisis_detection",
                    "crisis_type": "eating_disorder",
                    "sensitivity": 0.7,
                    "escalation_threshold": 0.8,
                    "context_aware": True,
                },
                {
                    "id": "crisis_panic_attack",
                    "category": "crisis_detection",
                    "priority": 75,
                    "level": "warning",
                    "pattern": r"(panic attack|can't breathe|heart racing|losing control)",
                    "flags": "i",
                    "validation_type": "crisis_detection",
                    "crisis_type": "panic_attack",
                    "sensitivity": 0.65,
                    "escalation_threshold": 0.75,
                    "context_aware": True,
                },
                {
                    "id": "crisis_severe_depression",
                    "category": "crisis_detection",
                    "priority": 70,
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
