"""Keyword-based crisis detector for player input text.

Classifies raw player input into one of four CrisisLevel tiers using
configurable signal-pattern dictionaries. Designed to be synchronous,
non-blocking, and never-raising — safe to call from any async context.
"""

# Logseq: [[TTA.dev/Agent_orchestration/Crisis_detection/Detector]]

from __future__ import annotations

import logging
import time
from typing import Any

from .enums import CrisisLevel, CrisisType, InterventionType
from .models import CrisisAssessment

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default signal patterns — (phrase, CrisisType) tuples per level
# ---------------------------------------------------------------------------

_DEFAULT_PATTERNS: dict[CrisisLevel, list[tuple[str, CrisisType]]] = {
    CrisisLevel.CRITICAL: [
        ("kill myself", CrisisType.SUICIDAL_IDEATION),
        ("end my life", CrisisType.SUICIDAL_IDEATION),
        ("want to die", CrisisType.SUICIDAL_IDEATION),
        ("suicide", CrisisType.SUICIDAL_IDEATION),
        ("suicidal", CrisisType.SUICIDAL_IDEATION),
        ("can't go on anymore", CrisisType.SUICIDAL_IDEATION),
        ("cant go on anymore", CrisisType.SUICIDAL_IDEATION),
        ("no reason to live", CrisisType.SUICIDAL_IDEATION),
        ("hurting myself", CrisisType.SELF_HARM),
        ("self-harm", CrisisType.SELF_HARM),
        ("self harm", CrisisType.SELF_HARM),
        ("cutting myself", CrisisType.SELF_HARM),
    ],
    CrisisLevel.HIGH: [
        ("hopeless", CrisisType.SEVERE_DEPRESSION),
        ("worthless", CrisisType.SEVERE_DEPRESSION),
        ("no point", CrisisType.SEVERE_DEPRESSION),
        ("everyone would be better off", CrisisType.SUICIDAL_IDEATION),
        ("thinking about ending it", CrisisType.SUICIDAL_IDEATION),
        ("can't take it anymore", CrisisType.SEVERE_DEPRESSION),
        ("cant take it anymore", CrisisType.SEVERE_DEPRESSION),
        ("so much pain", CrisisType.SEVERE_DEPRESSION),
        ("nothing matters", CrisisType.SEVERE_DEPRESSION),
        ("don't want to exist", CrisisType.SUICIDAL_IDEATION),
        ("dont want to exist", CrisisType.SUICIDAL_IDEATION),
    ],
    CrisisLevel.MODERATE: [
        ("really struggling", CrisisType.SEVERE_DEPRESSION),
        ("can't cope", CrisisType.SEVERE_DEPRESSION),
        ("cant cope", CrisisType.SEVERE_DEPRESSION),
        ("overwhelmed", CrisisType.PANIC_ATTACK),
        ("falling apart", CrisisType.SEVERE_DEPRESSION),
        ("breaking down", CrisisType.SEVERE_DEPRESSION),
        ("so anxious", CrisisType.PANIC_ATTACK),
        ("depressed", CrisisType.SEVERE_DEPRESSION),
        ("can't sleep", CrisisType.SEVERE_DEPRESSION),
        ("cant sleep", CrisisType.SEVERE_DEPRESSION),
        ("empty inside", CrisisType.SEVERE_DEPRESSION),
        ("lost", CrisisType.SEVERE_DEPRESSION),
    ],
    # LOW is a catch-all — no explicit patterns; used as fallback
    CrisisLevel.LOW: [],
}

# Confidence values per level
_CONFIDENCE: dict[CrisisLevel, float] = {
    CrisisLevel.CRITICAL: 0.9,
    CrisisLevel.HIGH: 0.9,
    CrisisLevel.MODERATE: 0.7,
    CrisisLevel.LOW: 0.5,
}

# Recommended intervention per level
_INTERVENTION: dict[CrisisLevel, InterventionType] = {
    CrisisLevel.CRITICAL: InterventionType.EMERGENCY_SERVICES,
    CrisisLevel.HIGH: InterventionType.HUMAN_OVERSIGHT,
    CrisisLevel.MODERATE: InterventionType.AUTOMATED_RESPONSE,
    CrisisLevel.LOW: InterventionType.AUTOMATED_RESPONSE,
}

# Ordered scan sequence — highest severity first
_SCAN_ORDER: list[CrisisLevel] = [
    CrisisLevel.CRITICAL,
    CrisisLevel.HIGH,
    CrisisLevel.MODERATE,
]


class CrisisDetector:
    """Classifies player input text to a CrisisLevel using configurable signal patterns.

    Patterns are checked from CRITICAL down to MODERATE; the highest matching
    level wins.  If no pattern matches the text is returned as LOW.

    All public methods are synchronous, non-blocking, and never raise exceptions.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialise the detector, optionally overriding signal patterns.

        Args:
            config: Optional dict with key ``"patterns"`` whose value must be
                    a ``dict[CrisisLevel, list[tuple[str, CrisisType]]]``
                    replacing the built-in defaults entirely, or individual
                    level keys (``"critical"``, ``"high"``, ``"moderate"``)
                    containing ``list[tuple[str, str]]`` to override per level.
        """
        cfg = config or {}
        if "patterns" in cfg:
            # Full replacement
            self._patterns: dict[CrisisLevel, list[tuple[str, CrisisType]]] = cfg[
                "patterns"
            ]
        else:
            # Start from defaults then apply per-level overrides
            self._patterns = {k: list(v) for k, v in _DEFAULT_PATTERNS.items()}
            for level in _SCAN_ORDER:
                key = level.value  # e.g. "critical"
                if key in cfg:
                    self._patterns[level] = [
                        (phrase, CrisisType(ct)) for phrase, ct in cfg[key]
                    ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assess(self, text: str) -> CrisisAssessment:
        """Assess player input text for crisis signals.

        Args:
            text: Raw player input text.

        Returns:
            A :class:`CrisisAssessment` — never raises.
        """
        try:
            return self._assess_safe(text)
        except Exception as exc:  # pragma: no cover
            logger.error("CrisisDetector.assess() unexpected error: %s", exc)
            return self._safe_fallback()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _assess_safe(self, text: str) -> CrisisAssessment:
        """Inner assessment — may raise; called inside try/except."""
        if not text or not isinstance(text, str):
            return self._safe_fallback()

        text_lower = text.lower()

        for level in _SCAN_ORDER:
            matched_types: list[CrisisType] = []
            for phrase, crisis_type in self._patterns.get(level, []):
                if phrase.lower() in text_lower:
                    if crisis_type not in matched_types:
                        matched_types.append(crisis_type)

            if matched_types:
                return CrisisAssessment(
                    crisis_level=level,
                    crisis_types=matched_types,
                    confidence=_CONFIDENCE[level],
                    risk_factors=[f"pattern_match:{level.value}"],
                    protective_factors=[],
                    immediate_risk=level in (CrisisLevel.CRITICAL, CrisisLevel.HIGH),
                    intervention_recommended=_INTERVENTION[level],
                    escalation_required=level
                    in (CrisisLevel.CRITICAL, CrisisLevel.HIGH),
                    assessment_timestamp=time.time(),
                )

        # No patterns matched — return LOW baseline
        return CrisisAssessment(
            crisis_level=CrisisLevel.LOW,
            crisis_types=[],
            confidence=0.1,
            risk_factors=[],
            protective_factors=[],
            immediate_risk=False,
            intervention_recommended=InterventionType.AUTOMATED_RESPONSE,
            escalation_required=False,
            assessment_timestamp=time.time(),
        )

    @staticmethod
    def _safe_fallback() -> CrisisAssessment:
        """Return a safe LOW-level fallback on any error or empty input."""
        return CrisisAssessment(
            crisis_level=CrisisLevel.LOW,
            crisis_types=[],
            confidence=0.1,
            risk_factors=[],
            protective_factors=[],
            immediate_risk=False,
            intervention_recommended=InterventionType.AUTOMATED_RESPONSE,
            escalation_required=False,
            assessment_timestamp=time.time(),
        )
