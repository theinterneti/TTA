"""
Unit tests for ChoiceSignificanceDetector — rule-based narrative impact classifier.

Covers:
- LOW significance detection (exploration, dialogue, movement verbs)
- MEDIUM significance detection (trade, combat, item use)
- HIGH significance detection (pledges, betrayals, revelations, destruction)
- CRITICAL significance detection (killing, sacrifice, irreversible world changes)
- Escalation marker bumping (e.g. "no turning back" raises level by one)
- Empty / whitespace input → safe LOW default
- Exception safety — never raises on bad input
- Helper predicates: is_dolt_commit_worthy(), is_world_state_update_worthy()
"""

from __future__ import annotations

import pytest

from src.components.choice_detector.detector import (
    ChoiceSignificanceDetector,
    SignificanceLevel,
    _rule_based_classify,
)

pytestmark = pytest.mark.unit


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def detector() -> ChoiceSignificanceDetector:
    """Return a fresh ChoiceSignificanceDetector instance."""
    return ChoiceSignificanceDetector()


# ── SignificanceLevel enum ────────────────────────────────────────────────────


def test_significance_level_values_are_strings() -> None:
    """SignificanceLevel is a StrEnum with correct lowercase values."""
    assert SignificanceLevel.LOW == "low"
    assert SignificanceLevel.MEDIUM == "medium"
    assert SignificanceLevel.HIGH == "high"
    assert SignificanceLevel.CRITICAL == "critical"


# ── LOW significance ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "player_text",
    [
        "I look around the room",
        "examine the old chest",
        "walk towards the market",
        "listen to the distant bells",
        "wait here for a while",
        "pick up the fallen coin",
        "say hello to the innkeeper",
    ],
)
def test_classify_low_significance_actions(
    detector: ChoiceSignificanceDetector, player_text: str
) -> None:
    """ChoiceSignificanceDetector.classify returns LOW for exploration and dialogue."""
    # Arrange — player_text provided by parametrize

    # Act
    level, confidence = detector.classify(player_text)

    # Assert
    assert level == SignificanceLevel.LOW
    assert confidence >= 0.80


# ── MEDIUM significance ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "player_text",
    [
        "buy provisions from the merchant",
        "give the map to the stranger",
        "attack the guard blocking the door",
        "help the wounded soldier",
        "open the locked gate",
    ],
)
def test_classify_medium_significance_actions(
    detector: ChoiceSignificanceDetector, player_text: str
) -> None:
    """ChoiceSignificanceDetector.classify returns MEDIUM for limited-consequence actions."""
    # Arrange — player_text provided by parametrize

    # Act
    level, confidence = detector.classify(player_text)

    # Assert
    assert level == SignificanceLevel.MEDIUM
    assert confidence >= 0.75


# ── HIGH significance ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "player_text",
    [
        "I pledge allegiance to the northern faction",
        "betray the captain to his enemies",
        "confess what really happened that night",
        "decide to leave the city behind",
        "destroy the treaty scroll",
        "swear an oath to protect the child",
    ],
)
def test_classify_high_significance_actions(
    detector: ChoiceSignificanceDetector, player_text: str
) -> None:
    """ChoiceSignificanceDetector.classify returns HIGH for life-altering decisions."""
    # Arrange — player_text provided by parametrize

    # Act
    level, confidence = detector.classify(player_text)

    # Assert
    assert level == SignificanceLevel.HIGH
    assert confidence >= 0.80


# ── CRITICAL significance ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "player_text",
    [
        "kill the corrupt magistrate",
        "sacrifice myself to save the village",
        "declare war on the eastern empire",
        "destroy the world-anchor forever",
        "this is my final decision",
    ],
)
def test_classify_critical_significance_actions(
    detector: ChoiceSignificanceDetector, player_text: str
) -> None:
    """ChoiceSignificanceDetector.classify returns CRITICAL for irreversible world actions."""
    # Arrange — player_text provided by parametrize

    # Act
    level, confidence = detector.classify(player_text)

    # Assert
    assert level == SignificanceLevel.CRITICAL
    assert confidence >= 0.85


# ── Escalation markers ────────────────────────────────────────────────────────


def test_escalation_marker_bumps_medium_to_high(
    detector: ChoiceSignificanceDetector,
) -> None:
    """Escalation marker 'no turning back' bumps MEDIUM action to HIGH."""
    # Arrange
    text = "open the sealed vault — there's no turning back"

    # Act
    level, confidence = detector.classify(text)

    # Assert
    assert level == SignificanceLevel.HIGH


def test_escalation_marker_bumps_high_to_critical(
    detector: ChoiceSignificanceDetector,
) -> None:
    """Escalation marker 'last chance' bumps HIGH action to CRITICAL."""
    # Arrange
    text = "betray the council — this is the last chance"

    # Act
    level, confidence = detector.classify(text)

    # Assert
    assert level == SignificanceLevel.CRITICAL


# ── Edge cases ────────────────────────────────────────────────────────────────


def test_empty_input_returns_low(detector: ChoiceSignificanceDetector) -> None:
    """ChoiceSignificanceDetector.classify returns LOW for empty string input."""
    # Arrange
    text = ""

    # Act
    level, confidence = detector.classify(text)

    # Assert
    assert level == SignificanceLevel.LOW
    assert confidence == pytest.approx(0.90)


def test_whitespace_only_returns_low(detector: ChoiceSignificanceDetector) -> None:
    """ChoiceSignificanceDetector.classify returns LOW for whitespace-only input."""
    # Arrange
    text = "   \t\n  "

    # Act
    level, confidence = detector.classify(text)

    # Assert
    assert level == SignificanceLevel.LOW


def test_classify_with_narrative_context(
    detector: ChoiceSignificanceDetector,
) -> None:
    """Classify uses narrative_context to extend match window for patterns."""
    # Arrange — by itself "go" is LOW, but combined with CRITICAL context it can still elevate
    player_text = "I go ahead with it"
    context = "The elder said: kill the beast or the village dies forever"

    # Act
    level, confidence = detector.classify(player_text, narrative_context=context)

    # Assert — with critical context, level is elevated
    assert level in (SignificanceLevel.CRITICAL, SignificanceLevel.HIGH)


def test_classify_never_raises_on_unusual_input(
    detector: ChoiceSignificanceDetector,
) -> None:
    """ChoiceSignificanceDetector.classify is exception-safe — never raises."""
    # Arrange
    weird_inputs = ["", "\x00\x01\x02", "🔥💀⚔️", "a" * 10_000]

    # Act & Assert — should not raise
    for inp in weird_inputs:
        level, confidence = detector.classify(inp)
        assert isinstance(level, SignificanceLevel)
        assert 0.0 <= confidence <= 1.0


# ── Helper predicates ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "level,expected",
    [
        (SignificanceLevel.LOW, False),
        (SignificanceLevel.MEDIUM, False),
        (SignificanceLevel.HIGH, True),
        (SignificanceLevel.CRITICAL, True),
    ],
)
def test_is_dolt_commit_worthy(
    detector: ChoiceSignificanceDetector,
    level: SignificanceLevel,
    expected: bool,
) -> None:
    """is_dolt_commit_worthy returns True only for HIGH and CRITICAL levels."""
    # Arrange — level provided by parametrize

    # Act
    result = detector.is_dolt_commit_worthy(level)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "level,expected",
    [
        (SignificanceLevel.LOW, False),
        (SignificanceLevel.MEDIUM, True),
        (SignificanceLevel.HIGH, True),
        (SignificanceLevel.CRITICAL, True),
    ],
)
def test_is_world_state_update_worthy(
    detector: ChoiceSignificanceDetector,
    level: SignificanceLevel,
    expected: bool,
) -> None:
    """is_world_state_update_worthy returns True for MEDIUM, HIGH, and CRITICAL."""
    # Arrange — level provided by parametrize

    # Act
    result = detector.is_world_state_update_worthy(level)

    # Assert
    assert result == expected


# ── Internal rule-based classifier ───────────────────────────────────────────


def test_rule_based_classify_inconclusive_returns_medium() -> None:
    """_rule_based_classify returns MEDIUM with low confidence for unknown input."""
    # Arrange
    text = "xyzzy plugh nothing matches here"

    # Act
    level, confidence = _rule_based_classify(text)

    # Assert
    assert level == SignificanceLevel.MEDIUM
    assert confidence == pytest.approx(0.40)
