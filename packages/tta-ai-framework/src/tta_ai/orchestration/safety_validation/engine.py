"""Safety rule evaluation engine."""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Safety_validation/Engine]]

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # Optional; JSON works without it

from .enums import SafetyLevel, ValidationType
from .models import SafetyRule, ValidationFinding


class SafetyRuleEngine:
    """Engine for evaluating safety rules against text content."""

    def __init__(self, rules: list[SafetyRule]) -> None:
        """Initialize the rule engine with a list of safety rules.

        Args:
            rules: List of SafetyRule objects to evaluate
        """
        # Sort rules by priority desc for deterministic evaluation
        self._rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        self._compiled: list[tuple[SafetyRule, re.Pattern[str] | None]] = [
            (r, r.compile()) for r in self._rules
        ]

    @staticmethod
    def from_config(config: dict[str, Any]) -> SafetyRuleEngine:
        """Create a SafetyRuleEngine from configuration dictionary.

        Args:
            config: Configuration dictionary with 'rules' key

        Returns:
            Configured SafetyRuleEngine instance
        """
        rules_cfg = (config or {}).get("rules") or []
        rules: list[SafetyRule] = []
        for rc in rules_cfg:
            # Parse enhanced rule configuration
            validation_type = ValidationType(rc.get("validation_type", "keyword"))
            therapeutic_context = rc.get("therapeutic_context")
            crisis_type = rc.get("crisis_type")

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
        """Load configuration from file (YAML or JSON).

        Args:
            path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        file_path = Path(path)
        if path.lower().endswith((".yaml", ".yml")) and yaml is not None:
            with file_path.open(encoding="utf-8") as f:
                return yaml.safe_load(f)  # type: ignore
        with file_path.open(encoding="utf-8") as f:
            return json.load(f)

    def evaluate(self, text: str, context: dict[str, Any] | None = None) -> list[ValidationFinding]:
        """Evaluate text against all rules with enhanced validation algorithms.

        This method evaluates the provided text against all configured safety rules,
        applying different validation strategies based on the rule type (keyword,
        sentiment, context-aware, crisis detection, therapeutic boundary).

        Args:
            text: Text to evaluate for safety violations
            context: Optional context dictionary for context-aware validation.
                    May include: session_count, previous_violations, therapeutic_session,
                    previous_crisis_indicators, etc.

        Returns:
            List of ValidationFinding objects, sorted by priority (highest first)
        """
        findings: list[ValidationFinding] = []

        # Basic sentiment analysis for context
        sentiment_score = self._analyze_sentiment(text)

        for rule, rx in self._compiled:
            if rule.validation_type == ValidationType.KEYWORD:
                findings.extend(self._evaluate_keyword_rule(rule, rx, text, sentiment_score))
            elif rule.validation_type == ValidationType.CRISIS_DETECTION:
                findings.extend(
                    self._evaluate_crisis_rule(rule, rx, text, sentiment_score, context)
                )
            elif rule.validation_type == ValidationType.THERAPEUTIC_BOUNDARY:
                findings.extend(self._evaluate_therapeutic_rule(rule, rx, text, context))
            elif rule.validation_type == ValidationType.SENTIMENT:
                findings.extend(self._evaluate_sentiment_rule(rule, text, sentiment_score))
            elif rule.validation_type == ValidationType.CONTEXT_AWARE:
                findings.extend(self._evaluate_context_rule(rule, rx, text, context))

        return findings

    def _analyze_sentiment(self, text: str) -> float:
        """Perform basic sentiment analysis on text.

        Uses keyword-based sentiment analysis to estimate the emotional tone
        of the text. This is a simple implementation suitable for therapeutic
        content validation.

        Args:
            text: Text to analyze

        Returns:
            Sentiment score from -1.0 (very negative) to 1.0 (very positive),
            with 0.0 being neutral
        """
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
        self, rule: SafetyRule, rx: re.Pattern[str] | None, text: str, sentiment: float
    ) -> list[ValidationFinding]:
        """Evaluate keyword-based rules with enhanced context.

        Args:
            rule: Safety rule to evaluate
            rx: Compiled regex pattern (may be None)
            text: Text to evaluate
            sentiment: Sentiment score from _analyze_sentiment

        Returns:
            List of validation findings for this rule
        """
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
        rx: re.Pattern[str] | None,
        text: str,
        sentiment: float,
        context: dict[str, Any] | None,
    ) -> list[ValidationFinding]:
        """Evaluate crisis detection rules with enhanced algorithms.

        This method uses advanced pattern matching and context analysis to detect
        crisis situations with high accuracy. It considers sentiment, context history,
        and multiple crisis type patterns.

        Args:
            rule: Safety rule to evaluate
            rx: Compiled regex pattern (may be None)
            text: Text to evaluate
            sentiment: Sentiment score from _analyze_sentiment
            context: Optional context dictionary with session history

        Returns:
            List of validation findings for crisis detection
        """
        findings = []

        # Enhanced crisis detection patterns (will use CrisisType from crisis_detection later)
        crisis_patterns = {
            "suicidal_ideation": [
                r"(want to die|wish I was dead|kill myself|suicide|end it all|not worth living)",
                r"(better off dead|can't go on|no point|give up|end the pain)",
                r"(life isn't worth|life is not worth|should just end|ending it all)",
                r"(don't want to be here|want to be dead|rather be dead)",
                r"(better off without me|everyone would be better|world would be better)",
                r"(thinking about killing|thinking about suicide|thoughts of suicide)",
            ],
            "self_harm": [
                r"(cut myself|hurt myself|self harm|self-harm|cutting|burning myself)",
                r"(punish myself|deserve pain|make it stop|deserve to feel pain|hurt when I feel)",
                r"(hitting myself|burned myself|cutting helps|hurting myself)",
                r"(I've been hitting|I've been cutting|I burned myself)",
            ],
            "severe_depression": [
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
                            message=f"Crisis detected: {crisis_type} (confidence: {confidence:.2f})",
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
        rx: re.Pattern[str] | None,
        text: str,
        context: dict[str, Any] | None,
    ) -> list[ValidationFinding]:
        """Evaluate therapeutic boundary rules.

        This method checks for violations of therapeutic boundaries such as
        inappropriate requests for diagnosis, prescription, or other professional
        services that should be handled by licensed professionals.

        Args:
            rule: Safety rule to evaluate
            rx: Compiled regex pattern (may be None)
            text: Text to evaluate
            context: Optional context dictionary with therapeutic session info

        Returns:
            List of validation findings for therapeutic boundary violations
        """
        findings = []
        if rx is None:
            return findings

        for m in rx.finditer(text):
            # Check if this violates therapeutic boundaries
            confidence = rule.sensitivity

            # Adjust based on therapeutic context
            if context and context.get("therapeutic_session"):
                # Will use TherapeuticContext enum from therapeutic_scoring later
                if rule.therapeutic_context == "crisis_intervention":
                    confidence += 0.2
                elif rule.therapeutic_context == "trauma_informed":
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
        """Evaluate sentiment-based rules.

        This method triggers findings based on overall sentiment scores,
        useful for detecting severely negative emotional states that may
        require intervention even without specific crisis keywords.

        Args:
            rule: Safety rule to evaluate
            text: Text to evaluate (not directly used, but kept for consistency)
            sentiment: Sentiment score from _analyze_sentiment

        Returns:
            List of validation findings for sentiment violations
        """
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
        rx: re.Pattern[str] | None,
        text: str,
        context: dict[str, Any] | None,
    ) -> list[ValidationFinding]:
        """Evaluate context-aware rules.

        This method adjusts rule matching based on session context such as
        user history, session count, and previous violations. This enables
        more nuanced validation that adapts to individual user patterns.

        Args:
            rule: Safety rule to evaluate
            rx: Compiled regex pattern (may be None)
            text: Text to evaluate
            context: Optional context dictionary with session history

        Returns:
            List of validation findings for context-aware matches
        """
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
