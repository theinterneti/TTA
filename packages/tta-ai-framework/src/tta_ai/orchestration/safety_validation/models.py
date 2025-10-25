"""Safety validation data models."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .enums import SafetyLevel, ValidationType


@dataclass
class ValidationFinding:
    """A single validation finding from rule evaluation."""

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
    crisis_type: str | None = None  # Will be CrisisType from crisis_detection
    therapeutic_context: str | None = None  # Will be TherapeuticContext from therapeutic_scoring
    sentiment_score: float | None = None  # -1.0 to 1.0
    escalation_required: bool = False
    alternative_suggested: str | None = None


@dataclass
class ValidationResult:
    """Complete validation result with findings and metadata."""

    level: SafetyLevel
    findings: list[ValidationFinding] = field(default_factory=list)
    score: float = 1.0  # 1.0=safe, 0.0=max unsafe
    audit: list[dict[str, Any]] = field(default_factory=list)
    # Enhanced fields for comprehensive analysis
    crisis_detected: bool = False
    crisis_types: list[str] = field(default_factory=list)  # Will be list[CrisisType]
    overall_sentiment: float | None = None  # -1.0 to 1.0
    therapeutic_appropriateness: float = 1.0  # 0.0 to 1.0
    escalation_recommended: bool = False
    alternative_content: str | None = None
    monitoring_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "level": self.level.value,
            "score": self.score,
            "crisis_detected": self.crisis_detected,
            "crisis_types": self.crisis_types,
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
class SafetyRule:
    """Definition of a safety validation rule."""

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
    therapeutic_context: str | None = None  # Will be TherapeuticContext
    crisis_type: str | None = None  # Will be CrisisType
    escalation_threshold: float = 0.8  # 0.0 to 1.0
    alternative_template: str | None = None

    def compile(self) -> re.Pattern[str] | None:
        """Compile the pattern into a regex pattern."""
        if not self.pattern:
            return None
        fl = 0
        if self.flags and "i" in self.flags:
            fl |= re.IGNORECASE
        return re.compile(self.pattern, fl)
