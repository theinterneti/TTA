"""Interop spec: SafetyLevel (narrative content) ↔ CrisisLevel (player input).

The two systems operate on different domains:
- :class:`~src.components.gameplay_loop.narrative.emotional_safety_system.SafetyLevel`
  assesses *narrative content* produced by the NGA.
- :class:`~src.agent_orchestration.crisis_detection.enums.CrisisLevel`
  assesses *player input* processed by the IPA.

This module provides canonical bidirectional mappings so that either system
can escalate to or inform the other without circular imports.
"""

# Logseq: [[TTA.dev/Agent_orchestration/Crisis_detection/Interop]]

from __future__ import annotations

from src.components.gameplay_loop.narrative.emotional_safety_system import SafetyLevel

from .enums import CrisisLevel

# ---------------------------------------------------------------------------
# Canonical mappings
# ---------------------------------------------------------------------------

SAFETY_TO_CRISIS: dict[SafetyLevel, CrisisLevel] = {
    SafetyLevel.SAFE: CrisisLevel.LOW,
    SafetyLevel.CAUTION: CrisisLevel.LOW,
    SafetyLevel.WARNING: CrisisLevel.MODERATE,
    SafetyLevel.UNSAFE: CrisisLevel.HIGH,
    SafetyLevel.CRISIS: CrisisLevel.CRITICAL,
}

CRISIS_TO_SAFETY: dict[CrisisLevel, SafetyLevel] = {
    CrisisLevel.LOW: SafetyLevel.SAFE,
    CrisisLevel.MODERATE: SafetyLevel.WARNING,
    CrisisLevel.HIGH: SafetyLevel.UNSAFE,
    CrisisLevel.CRITICAL: SafetyLevel.CRISIS,
}


# ---------------------------------------------------------------------------
# Conversion helpers
# ---------------------------------------------------------------------------


def safety_level_to_crisis_level(safety_level: SafetyLevel) -> CrisisLevel:
    """Map a SafetyLevel to the equivalent CrisisLevel.

    Args:
        safety_level: Narrative-content safety level.

    Returns:
        Corresponding :class:`CrisisLevel`, defaulting to LOW on unknown input.
    """
    return SAFETY_TO_CRISIS.get(safety_level, CrisisLevel.LOW)


def crisis_level_to_safety_level(crisis_level: CrisisLevel) -> SafetyLevel:
    """Map a CrisisLevel to the equivalent SafetyLevel.

    Args:
        crisis_level: Player-input crisis level.

    Returns:
        Corresponding :class:`SafetyLevel`, defaulting to SAFE on unknown input.
    """
    return CRISIS_TO_SAFETY.get(crisis_level, SafetyLevel.SAFE)
