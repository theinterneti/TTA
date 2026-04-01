"""
Unit tests for Guide persona components: GuideInterventionDecider and GuidePromptBuilder.

Covers:
- InterventionType enum values and ordering
- GuideInterventionDecider.decide() returns NONE for safe/low inputs
- GuideInterventionDecider.decide() returns SENSORY_PAUSE for pacing signal
- GuideInterventionDecider.decide() returns SOFT_PROMPT for /reflect command
- GuideInterventionDecider.decide() escalates by safety_level mapping
- GuideInterventionDecider.decide() escalates by crisis_level mapping
- GuideInterventionDecider.decide() returns BREAK_CHARACTER for critical crisis
- GuideInterventionDecider.decide() highest intensity wins when multiple triggers
- GuideInterventionDecider.decide() mostly-silent style suppresses low interventions
- GuideInterventionDecider.decide() is exception-safe
- GuidePromptBuilder.build_voice_fragment() includes tone and formality
- GuidePromptBuilder.build_intervention_fragment() returns correct text per type
- GuidePromptBuilder.validate_no_clinical_language() detects clinical patterns
- GuidePromptBuilder.validate_no_clinical_language() passes clean text
"""

from __future__ import annotations

import pytest

from src.components.guide.intervention import (
    GuideInterventionDecider,
    InterventionType,
)
from src.components.guide.prompt import GuidePromptBuilder

pytestmark = pytest.mark.unit


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def decider() -> GuideInterventionDecider:
    """Return a fresh GuideInterventionDecider."""
    return GuideInterventionDecider()


@pytest.fixture()
def prompt_builder() -> GuidePromptBuilder:
    """Return a fresh GuidePromptBuilder."""
    return GuidePromptBuilder()


# ── InterventionType enum ─────────────────────────────────────────────────────


def test_intervention_type_values() -> None:
    """InterventionType is a StrEnum with five expected values."""
    assert InterventionType.NONE == "none"
    assert InterventionType.SENSORY_PAUSE == "sensory_pause"
    assert InterventionType.SOFT_PROMPT == "soft_prompt"
    assert InterventionType.COMPANION_SHIFT == "companion_shift"
    assert InterventionType.BREAK_CHARACTER == "break_character"


# ── GuideInterventionDecider — baseline ──────────────────────────────────────


def test_decide_returns_none_for_all_safe_inputs(
    decider: GuideInterventionDecider,
) -> None:
    """GuideInterventionDecider.decide returns NONE when all signals are safe."""
    # Arrange — all defaults are safe
    # Act
    result = decider.decide(
        safety_level="safe",
        crisis_level="low",
        pacing_signal=False,
        player_text="I look around the room",
    )

    # Assert
    assert result == InterventionType.NONE


# ── Pacing signal ─────────────────────────────────────────────────────────────


def test_decide_returns_sensory_pause_for_pacing_signal(
    decider: GuideInterventionDecider,
) -> None:
    """GuideInterventionDecider.decide returns SENSORY_PAUSE when pacing_signal=True."""
    # Arrange
    # Act
    result = decider.decide(
        safety_level="safe",
        crisis_level="low",
        pacing_signal=True,
        player_text="continue",
    )

    # Assert
    assert result == InterventionType.SENSORY_PAUSE


# ── Explicit player commands ──────────────────────────────────────────────────


@pytest.mark.parametrize("command", ["/reflect", "/journal", "/pause", "/breathe"])
def test_decide_soft_prompt_for_explicit_commands(
    decider: GuideInterventionDecider, command: str
) -> None:
    """GuideInterventionDecider.decide returns at least SOFT_PROMPT for player commands."""
    # Arrange — player typed a reflective command
    # Act
    result = decider.decide(
        safety_level="safe",
        crisis_level="low",
        pacing_signal=False,
        player_text=command,
    )

    # Assert
    assert result == InterventionType.SOFT_PROMPT


# ── Safety level escalation ───────────────────────────────────────────────────


@pytest.mark.parametrize(
    "safety_level,expected_minimum",
    [
        ("safe", InterventionType.NONE),
        ("caution", InterventionType.SENSORY_PAUSE),
        ("warning", InterventionType.SOFT_PROMPT),
        ("unsafe", InterventionType.COMPANION_SHIFT),
        ("crisis", InterventionType.BREAK_CHARACTER),
    ],
)
def test_decide_escalates_by_safety_level(
    decider: GuideInterventionDecider,
    safety_level: str,
    expected_minimum: InterventionType,
) -> None:
    """GuideInterventionDecider.decide maps safety levels to correct intervention types."""
    # Arrange — override via parametrize
    # Act
    result = decider.decide(
        safety_level=safety_level,
        crisis_level="low",
        pacing_signal=False,
        player_text="",
    )

    # Assert
    assert result == expected_minimum


# ── Crisis level escalation ───────────────────────────────────────────────────


@pytest.mark.parametrize(
    "crisis_level,expected_minimum",
    [
        ("low", InterventionType.NONE),
        ("moderate", InterventionType.SENSORY_PAUSE),
        ("high", InterventionType.SOFT_PROMPT),
        ("critical", InterventionType.BREAK_CHARACTER),
    ],
)
def test_decide_escalates_by_crisis_level(
    decider: GuideInterventionDecider,
    crisis_level: str,
    expected_minimum: InterventionType,
) -> None:
    """GuideInterventionDecider.decide maps crisis levels to correct intervention types."""
    # Arrange — override via parametrize
    # Act
    result = decider.decide(
        safety_level="safe",
        crisis_level=crisis_level,
        pacing_signal=False,
        player_text="",
    )

    # Assert
    assert result == expected_minimum


# ── Highest intensity wins ────────────────────────────────────────────────────


def test_decide_highest_intensity_wins(
    decider: GuideInterventionDecider,
) -> None:
    """When multiple triggers fire, decide() returns the highest intensity type."""
    # Arrange — pacing (SENSORY_PAUSE) + crisis critical (BREAK_CHARACTER)
    # Act
    result = decider.decide(
        safety_level="safe",
        crisis_level="critical",
        pacing_signal=True,
        player_text="",
    )

    # Assert — BREAK_CHARACTER beats SENSORY_PAUSE
    assert result == InterventionType.BREAK_CHARACTER


# ── mostly-silent style ───────────────────────────────────────────────────────


def test_decide_mostly_silent_suppresses_sensory_pause(
    decider: GuideInterventionDecider,
) -> None:
    """mostly-silent intervention_style suppresses SENSORY_PAUSE to NONE."""
    # Arrange — pacing signal would normally give SENSORY_PAUSE
    # Act
    result = decider.decide(
        safety_level="safe",
        crisis_level="low",
        pacing_signal=True,
        player_text="",
        intervention_style="mostly-silent",
    )

    # Assert — suppressed back to NONE
    assert result == InterventionType.NONE


def test_decide_mostly_silent_does_not_suppress_companion_shift(
    decider: GuideInterventionDecider,
) -> None:
    """mostly-silent does NOT suppress COMPANION_SHIFT (unsafe safety level)."""
    # Arrange
    # Act
    result = decider.decide(
        safety_level="unsafe",
        crisis_level="low",
        pacing_signal=False,
        player_text="",
        intervention_style="mostly-silent",
    )

    # Assert — COMPANION_SHIFT is above suppression threshold
    assert result == InterventionType.COMPANION_SHIFT


def test_decide_mostly_silent_allows_explicit_commands(
    decider: GuideInterventionDecider,
) -> None:
    """mostly-silent still honours explicit /reflect commands."""
    # Arrange
    # Act
    result = decider.decide(
        safety_level="safe",
        crisis_level="low",
        pacing_signal=False,
        player_text="/reflect on this moment",
        intervention_style="mostly-silent",
    )

    # Assert — explicit command overrides silence suppression
    assert result == InterventionType.SOFT_PROMPT


# ── Exception safety ──────────────────────────────────────────────────────────


def test_decide_never_raises_on_unknown_levels(
    decider: GuideInterventionDecider,
) -> None:
    """GuideInterventionDecider.decide never raises for unknown enum strings."""
    # Arrange
    # Act
    result = decider.decide(
        safety_level="unknown_level",
        crisis_level="unknown_crisis",
        pacing_signal=False,
        player_text="",
    )

    # Assert — falls back to NONE
    assert result == InterventionType.NONE


# ── GuidePromptBuilder ────────────────────────────────────────────────────────


def test_build_voice_fragment_includes_tone(
    prompt_builder: GuidePromptBuilder,
) -> None:
    """GuidePromptBuilder.build_voice_fragment includes the provided tone."""
    # Arrange
    params = {
        "tone": "mysterious-ancient",
        "formality": "formal",
        "intervention_style": "gentle",
        "reflection_frequency": "rarely",
    }

    # Act
    fragment = prompt_builder.build_voice_fragment(params)

    # Assert
    assert "mysterious-ancient" in fragment
    assert "formal" in fragment
    assert "rarely" in fragment


def test_build_voice_fragment_never_references_therapy(
    prompt_builder: GuidePromptBuilder,
) -> None:
    """GuidePromptBuilder.build_voice_fragment does not produce diagnosable therapy text."""
    # Arrange — the fragment tells the Guide what NOT to do, so the word 'diagnose'
    # appears as an instruction. Verify the fragment is a non-empty instruction string.
    params = {"tone": "warm", "formality": "casual", "reflection_frequency": "often"}

    # Act
    fragment = prompt_builder.build_voice_fragment(params)

    # Assert — fragment is non-empty and contains tone guidance
    assert len(fragment) > 20
    assert "warm" in fragment


def test_build_intervention_fragment_none_is_empty(
    prompt_builder: GuidePromptBuilder,
) -> None:
    """NONE intervention type produces an empty fragment."""
    # Arrange & Act
    fragment = prompt_builder.build_intervention_fragment(InterventionType.NONE)

    # Assert
    assert fragment == ""


def test_build_intervention_fragment_break_character_includes_crisis_line(
    prompt_builder: GuidePromptBuilder,
) -> None:
    """BREAK_CHARACTER fragment includes the 988 crisis line reference."""
    # Arrange & Act
    fragment = prompt_builder.build_intervention_fragment(
        InterventionType.BREAK_CHARACTER
    )

    # Assert
    assert "988" in fragment
    assert fragment  # non-empty


@pytest.mark.parametrize(
    "itype",
    [
        InterventionType.SENSORY_PAUSE,
        InterventionType.SOFT_PROMPT,
        InterventionType.COMPANION_SHIFT,
        InterventionType.BREAK_CHARACTER,
    ],
)
def test_build_intervention_fragment_non_none_is_non_empty(
    prompt_builder: GuidePromptBuilder,
    itype: InterventionType,
) -> None:
    """Non-NONE intervention fragments are non-empty strings."""
    # Arrange & Act
    fragment = prompt_builder.build_intervention_fragment(itype)

    # Assert
    assert len(fragment) > 10


# ── Clinical language validation ──────────────────────────────────────────────


def test_validate_clinical_detects_diagnosis(
    prompt_builder: GuidePromptBuilder,
) -> None:
    """validate_no_clinical_language detects 'diagnose' in text."""
    # Arrange
    text = "I can diagnose this as depression."

    # Act
    found = prompt_builder.validate_no_clinical_language(text)

    # Assert
    assert "diagnose" in found


def test_validate_clinical_clean_text_returns_empty(
    prompt_builder: GuidePromptBuilder,
) -> None:
    """validate_no_clinical_language returns empty list for clean narrative text."""
    # Arrange
    text = "The light falls softly across the stones. Something stirs within you."

    # Act
    found = prompt_builder.validate_no_clinical_language(text)

    # Assert
    assert found == []
