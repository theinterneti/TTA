"""
Normalization helpers for therapeutic settings.

Centralizes alias mapping for TherapeuticApproach and IntensityLevel so both
REST and WebSocket paths stay consistent.
"""

from __future__ import annotations

from collections.abc import Iterable

from ..models.enums import IntensityLevel, TherapeuticApproach

# Canonical alias map for approaches
_APPROACH_ALIAS = {
    # Short aliases
    "cbt": TherapeuticApproach.CBT,
    # Common long names
    "cognitive_behavioral_therapy": TherapeuticApproach.CBT,
    "mindfulness": TherapeuticApproach.MINDFULNESS,
    "narrative_therapy": TherapeuticApproach.NARRATIVE_THERAPY,
    "acceptance_commitment": TherapeuticApproach.ACCEPTANCE_COMMITMENT,
    "acceptance_commitment_therapy": TherapeuticApproach.ACCEPTANCE_COMMITMENT,
}


def normalize_approach(value: str | TherapeuticApproach) -> TherapeuticApproach:
    """Normalize a single approach value into a TherapeuticApproach enum.

    - Accepts enum or string (case-insensitive for known aliases)
    - Falls back to constructing enum from string when possible
    """
    if isinstance(value, TherapeuticApproach):
        return value
    key = str(value).strip().lower()
    mapped = _APPROACH_ALIAS.get(key)
    if mapped:
        return mapped
    # Attempt enum construction from provided string (must match enum value)
    return TherapeuticApproach(key)


def normalize_approaches(
    values: Iterable[str | TherapeuticApproach],
) -> list[TherapeuticApproach]:
    """Normalize a collection of approach designators into enums.

    Invalid entries are skipped (conservative behavior).
    """
    result: list[TherapeuticApproach] = []
    for v in values or []:
        try:
            result.append(normalize_approach(v))
        except Exception as e:
            # Skip invalid entries with debug logging
            logger.debug(
                f"Skipping invalid therapeutic approach '{v}': {type(e).__name__}: {e}"
            )
            continue
    return result


def normalize_intensity(
    value: str | IntensityLevel | None,
    default: IntensityLevel = IntensityLevel.MEDIUM,
) -> IntensityLevel:
    """Normalize an intensity designator to IntensityLevel.

    Accepts enum or string; returns provided default for None.
    """
    if value is None:
        return default
    if isinstance(value, IntensityLevel):
        return value
    return IntensityLevel(str(value))
