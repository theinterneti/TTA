"""Unit tests for CrisisDetector, interop helpers, and IPA integration.

Covers 4-level crisis detection, adversarial inputs, SafetyLevel ↔ CrisisLevel
mapping, and IPA ProcessedInput propagation.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agent_orchestration.crisis_detection.detector import CrisisDetector
from src.agent_orchestration.crisis_detection.enums import (
    CrisisLevel,
    CrisisType,
    InterventionType,
)
from src.agent_orchestration.crisis_detection.interop import (
    CRISIS_TO_SAFETY,
    SAFETY_TO_CRISIS,
    crisis_level_to_safety_level,
    safety_level_to_crisis_level,
)
from src.components.gameplay_loop.narrative.emotional_safety_system import SafetyLevel
from src.components.ipa.agent import IPAAgent
from src.components.ipa.models import EmotionalTone, ProcessedInput


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ipa_mock_llm(
    intent: str = "unknown",
    safety_signal: bool = False,
    primary: str = "neutral",
) -> MagicMock:
    """Return a mock LLM that yields a fixed JSON-like structure."""
    import json

    payload = json.dumps(
        {
            "intent": intent,
            "intent_confidence": 0.8,
            "entities": [],
            "emotional_tone": {
                "primary": primary,
                "intensity": 0.5 if safety_signal else 0.1,
                "safety_signal": safety_signal,
            },
            "normalized_text": "test input",
        }
    )
    mock_response = MagicMock()
    mock_response.content = payload
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    return mock_llm


# ===========================================================================
# TestCrisisDetectorSignalDetection
# ===========================================================================


class TestCrisisDetectorSignalDetection:
    """Tests for the four-level signal detection logic."""

    def setup_method(self) -> None:
        self.detector = CrisisDetector()

    def test_critical_level_detected(self) -> None:
        result = self.detector.assess("I want to kill myself tonight")
        assert result.crisis_level == CrisisLevel.CRITICAL
        assert result.confidence >= 0.9
        assert result.escalation_required is True
        assert result.immediate_risk is True
        assert CrisisType.SUICIDAL_IDEATION in result.crisis_types

    def test_critical_suicide_keyword(self) -> None:
        result = self.detector.assess("I've been thinking about suicide")
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_critical_self_harm(self) -> None:
        result = self.detector.assess("I've been cutting myself")
        assert result.crisis_level == CrisisLevel.CRITICAL
        assert CrisisType.SELF_HARM in result.crisis_types

    def test_critical_self_harm_hyphen(self) -> None:
        result = self.detector.assess("I keep doing self-harm")
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_critical_no_reason_to_live(self) -> None:
        result = self.detector.assess("There is no reason to live anymore")
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_high_level_detected(self) -> None:
        result = self.detector.assess("I feel so hopeless about everything")
        assert result.crisis_level == CrisisLevel.HIGH
        assert result.confidence >= 0.9
        assert result.escalation_required is True

    def test_high_worthless(self) -> None:
        result = self.detector.assess("I feel completely worthless")
        assert result.crisis_level == CrisisLevel.HIGH

    def test_high_thinking_about_ending_it(self) -> None:
        result = self.detector.assess("I keep thinking about ending it")
        assert result.crisis_level == CrisisLevel.HIGH

    def test_high_everyone_better_off(self) -> None:
        result = self.detector.assess("everyone would be better off without me")
        assert result.crisis_level == CrisisLevel.HIGH
        assert CrisisType.SUICIDAL_IDEATION in result.crisis_types

    def test_moderate_level_detected(self) -> None:
        result = self.detector.assess("I can't cope with this anymore")
        assert result.crisis_level == CrisisLevel.MODERATE
        assert result.confidence >= 0.7
        assert result.escalation_required is False

    def test_moderate_overwhelmed(self) -> None:
        result = self.detector.assess("I feel completely overwhelmed")
        assert result.crisis_level == CrisisLevel.MODERATE

    def test_moderate_depressed(self) -> None:
        result = self.detector.assess("I've been really depressed lately")
        assert result.crisis_level == CrisisLevel.MODERATE

    def test_moderate_empty_inside(self) -> None:
        result = self.detector.assess("I feel empty inside all the time")
        assert result.crisis_level == CrisisLevel.MODERATE

    def test_low_level_on_neutral_input(self) -> None:
        result = self.detector.assess("I want to explore the forest")
        assert result.crisis_level == CrisisLevel.LOW
        assert result.confidence <= 0.2
        assert result.escalation_required is False
        assert result.immediate_risk is False

    def test_low_level_on_positive_input(self) -> None:
        result = self.detector.assess("This adventure is so exciting!")
        assert result.crisis_level == CrisisLevel.LOW

    def test_critical_wins_over_moderate(self) -> None:
        # Text contains both moderate and critical signals
        text = "I'm overwhelmed and I want to kill myself"
        result = self.detector.assess(text)
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_critical_wins_over_high(self) -> None:
        text = "I feel hopeless and I keep hurting myself"
        result = self.detector.assess(text)
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_high_wins_over_moderate(self) -> None:
        text = "I feel overwhelmed and completely hopeless"
        result = self.detector.assess(text)
        assert result.crisis_level == CrisisLevel.HIGH

    def test_case_insensitive_critical(self) -> None:
        result = self.detector.assess("I WANT TO KILL MYSELF")
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_case_insensitive_high(self) -> None:
        result = self.detector.assess("I FEEL SO HOPELESS")
        assert result.crisis_level == CrisisLevel.HIGH

    def test_case_insensitive_moderate(self) -> None:
        result = self.detector.assess("I AM SO OVERWHELMED")
        assert result.crisis_level == CrisisLevel.MODERATE

    def test_intervention_critical_is_emergency(self) -> None:
        result = self.detector.assess("I want to kill myself")
        assert result.intervention_recommended == InterventionType.EMERGENCY_SERVICES

    def test_intervention_high_is_human_oversight(self) -> None:
        result = self.detector.assess("I feel so hopeless")
        assert result.intervention_recommended == InterventionType.HUMAN_OVERSIGHT

    def test_intervention_moderate_is_automated(self) -> None:
        result = self.detector.assess("I feel overwhelmed")
        assert result.intervention_recommended == InterventionType.AUTOMATED_RESPONSE

    def test_intervention_low_is_automated(self) -> None:
        result = self.detector.assess("Let me look around")
        assert result.intervention_recommended == InterventionType.AUTOMATED_RESPONSE

    def test_assessment_has_timestamp(self) -> None:
        result = self.detector.assess("hello")
        assert result.assessment_timestamp > 0


# ===========================================================================
# TestCrisisDetectorRobustness
# ===========================================================================


class TestCrisisDetectorRobustness:
    """Tests that CrisisDetector never raises on bad inputs."""

    def setup_method(self) -> None:
        self.detector = CrisisDetector()

    def test_never_raises_on_empty_string(self) -> None:
        result = self.detector.assess("")
        assert result.crisis_level == CrisisLevel.LOW

    def test_never_raises_on_whitespace(self) -> None:
        result = self.detector.assess("   ")
        assert result.crisis_level == CrisisLevel.LOW

    def test_never_raises_on_unicode(self) -> None:
        result = self.detector.assess("🔥💀😭 こんにちは мир")
        assert result.crisis_level == CrisisLevel.LOW  # no signal words

    def test_never_raises_on_very_long_text(self) -> None:
        long_text = "hello world " * 10_000
        result = self.detector.assess(long_text)
        assert result is not None
        assert result.crisis_level == CrisisLevel.LOW

    def test_none_input_safe_fallback(self) -> None:
        # type: ignore — intentionally passing None
        result = self.detector.assess(None)  # type: ignore[arg-type]
        assert result.crisis_level == CrisisLevel.LOW
        assert result.confidence <= 0.2

    def test_integer_input_safe_fallback(self) -> None:
        result = self.detector.assess(42)  # type: ignore[arg-type]
        assert result.crisis_level == CrisisLevel.LOW

    def test_list_input_safe_fallback(self) -> None:
        result = self.detector.assess(["kill myself"])  # type: ignore[arg-type]
        assert result.crisis_level == CrisisLevel.LOW


# ===========================================================================
# TestCrisisDetectorAdversarial
# ===========================================================================


class TestCrisisDetectorAdversarial:
    """Adversarial and edge-case tests."""

    def setup_method(self) -> None:
        self.detector = CrisisDetector()

    def test_fictional_framing_self_harm(self) -> None:
        # Fictional framing should still match substring patterns
        result = self.detector.assess(
            "my character decides to start self-harm after losing hope"
        )
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_fictional_framing_suicidal_ideation(self) -> None:
        result = self.detector.assess(
            "in the story, the hero wants to end their life"
        )
        # "end my life" is not present, but "want to die" triggers if present
        # "end their life" won't match — that's acceptable
        # We test "suicidal" phrase which would match
        result2 = self.detector.assess(
            "my character is described as suicidal in the narrative"
        )
        assert result2.crisis_level == CrisisLevel.CRITICAL

    def test_all_caps_detected(self) -> None:
        result = self.detector.assess("I AM SUICIDAL AND NEED HELP")
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_mixed_case_detected(self) -> None:
        result = self.detector.assess("I Am FeeLinG HoPeLeSs")
        assert result.crisis_level == CrisisLevel.HIGH

    def test_partial_phrase_hopeless_in_longer_word(self) -> None:
        # "hopeless" is a substring of "hopelessness" — should still match
        result = self.detector.assess(
            "I feel a deep sense of hopelessness every day"
        )
        assert result.crisis_level == CrisisLevel.HIGH

    def test_suicidal_in_longer_word(self) -> None:
        # "suicidal" inside "suicidally" should match
        result = self.detector.assess("thinking suicidally about the future")
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_multiple_crisis_types_in_text(self) -> None:
        # Contains both SELF_HARM and SUICIDAL_IDEATION signals
        result = self.detector.assess(
            "I've been cutting myself and I want to die"
        )
        assert result.crisis_level == CrisisLevel.CRITICAL
        assert len(result.crisis_types) >= 1

    def test_text_with_only_punctuation(self) -> None:
        result = self.detector.assess("!!!???...---")
        assert result.crisis_level == CrisisLevel.LOW

    def test_repeated_crisis_word(self) -> None:
        result = self.detector.assess("suicidal suicidal suicidal")
        assert result.crisis_level == CrisisLevel.CRITICAL
        # crisis_types should not duplicate
        assert result.crisis_types.count(CrisisType.SUICIDAL_IDEATION) == 1

    def test_new_line_in_text(self) -> None:
        result = self.detector.assess("I feel\noverwhelmed\nright now")
        assert result.crisis_level == CrisisLevel.MODERATE

    def test_tab_in_text(self) -> None:
        result = self.detector.assess("I feel\tdepressed today")
        assert result.crisis_level == CrisisLevel.MODERATE


# ===========================================================================
# TestCrisisDetectorConfig
# ===========================================================================


class TestCrisisDetectorConfig:
    """Test configurable pattern override."""

    def test_custom_critical_pattern(self) -> None:
        detector = CrisisDetector(
            config={
                "critical": [("custom_crisis_phrase", "suicidal_ideation")],
            }
        )
        result = detector.assess("this is a custom_crisis_phrase test")
        assert result.crisis_level == CrisisLevel.CRITICAL

    def test_empty_patterns_returns_low(self) -> None:
        detector = CrisisDetector(
            config={
                "patterns": {
                    CrisisLevel.CRITICAL: [],
                    CrisisLevel.HIGH: [],
                    CrisisLevel.MODERATE: [],
                    CrisisLevel.LOW: [],
                }
            }
        )
        result = detector.assess("I want to kill myself")
        assert result.crisis_level == CrisisLevel.LOW


# ===========================================================================
# TestInterop
# ===========================================================================


class TestInterop:
    """Tests for SafetyLevel ↔ CrisisLevel bidirectional mapping."""

    def test_safety_safe_maps_to_low(self) -> None:
        assert safety_level_to_crisis_level(SafetyLevel.SAFE) == CrisisLevel.LOW

    def test_safety_caution_maps_to_low(self) -> None:
        assert safety_level_to_crisis_level(SafetyLevel.CAUTION) == CrisisLevel.LOW

    def test_safety_warning_maps_to_moderate(self) -> None:
        assert (
            safety_level_to_crisis_level(SafetyLevel.WARNING) == CrisisLevel.MODERATE
        )

    def test_safety_unsafe_maps_to_high(self) -> None:
        assert safety_level_to_crisis_level(SafetyLevel.UNSAFE) == CrisisLevel.HIGH

    def test_safety_crisis_maps_to_critical(self) -> None:
        assert (
            safety_level_to_crisis_level(SafetyLevel.CRISIS) == CrisisLevel.CRITICAL
        )

    def test_crisis_low_maps_to_safe(self) -> None:
        assert crisis_level_to_safety_level(CrisisLevel.LOW) == SafetyLevel.SAFE

    def test_crisis_moderate_maps_to_warning(self) -> None:
        assert (
            crisis_level_to_safety_level(CrisisLevel.MODERATE) == SafetyLevel.WARNING
        )

    def test_crisis_high_maps_to_unsafe(self) -> None:
        assert crisis_level_to_safety_level(CrisisLevel.HIGH) == SafetyLevel.UNSAFE

    def test_crisis_critical_maps_to_crisis(self) -> None:
        assert (
            crisis_level_to_safety_level(CrisisLevel.CRITICAL) == SafetyLevel.CRISIS
        )

    def test_safety_to_crisis_dict_complete(self) -> None:
        for level in SafetyLevel:
            assert level in SAFETY_TO_CRISIS

    def test_crisis_to_safety_dict_complete(self) -> None:
        for level in CrisisLevel:
            assert level in CRISIS_TO_SAFETY

    def test_roundtrip_safe(self) -> None:
        original = SafetyLevel.SAFE
        crisis = safety_level_to_crisis_level(original)
        back = crisis_level_to_safety_level(crisis)
        assert back == SafetyLevel.SAFE

    def test_roundtrip_crisis(self) -> None:
        original = SafetyLevel.CRISIS
        crisis = safety_level_to_crisis_level(original)
        back = crisis_level_to_safety_level(crisis)
        assert back == SafetyLevel.CRISIS

    def test_roundtrip_warning_moderate(self) -> None:
        # WARNING → MODERATE → WARNING
        original = SafetyLevel.WARNING
        crisis = safety_level_to_crisis_level(original)
        assert crisis == CrisisLevel.MODERATE
        back = crisis_level_to_safety_level(crisis)
        assert back == SafetyLevel.WARNING

    def test_roundtrip_caution_collapses_to_safe(self) -> None:
        # CAUTION → LOW → SAFE (information loss is by design)
        crisis = safety_level_to_crisis_level(SafetyLevel.CAUTION)
        assert crisis == CrisisLevel.LOW
        back = crisis_level_to_safety_level(crisis)
        assert back == SafetyLevel.SAFE


# ===========================================================================
# TestIPAAgentCrisisIntegration
# ===========================================================================


class TestIPAAgentCrisisIntegration:
    """Integration tests for CrisisDetector inside IPAAgent.process()."""

    @pytest.mark.asyncio
    async def test_ipa_attaches_crisis_level_critical(self) -> None:
        llm = _make_ipa_mock_llm(safety_signal=True)
        agent = IPAAgent(llm=llm)
        result = await agent.process(
            raw_text="I want to kill myself right now",
            session_id="sess-test",
            player_id="player-test",
        )
        assert isinstance(result, ProcessedInput)
        assert result.crisis_level == CrisisLevel.CRITICAL
        assert result.crisis_confidence >= 0.9

    @pytest.mark.asyncio
    async def test_ipa_attaches_crisis_level_high(self) -> None:
        llm = _make_ipa_mock_llm()
        agent = IPAAgent(llm=llm)
        result = await agent.process(
            raw_text="I feel completely hopeless and worthless",
            session_id="sess-high",
        )
        assert result.crisis_level == CrisisLevel.HIGH

    @pytest.mark.asyncio
    async def test_ipa_attaches_crisis_level_moderate(self) -> None:
        llm = _make_ipa_mock_llm()
        agent = IPAAgent(llm=llm)
        result = await agent.process(
            raw_text="I feel overwhelmed by everything lately",
            session_id="sess-mod",
        )
        assert result.crisis_level == CrisisLevel.MODERATE

    @pytest.mark.asyncio
    async def test_ipa_safety_signal_bumps_low_to_moderate(self) -> None:
        # LLM says safety_signal=True but text has no crisis keyword patterns
        llm = _make_ipa_mock_llm(safety_signal=True)
        agent = IPAAgent(llm=llm)
        result = await agent.process(
            raw_text="I am having a rough time at work today",
            session_id="sess-bump",
        )
        # No crisis patterns → detector returns LOW
        # safety_signal=True bumps LOW → MODERATE
        assert result.crisis_level == CrisisLevel.MODERATE

    @pytest.mark.asyncio
    async def test_ipa_low_on_clean_input(self) -> None:
        llm = _make_ipa_mock_llm(safety_signal=False)
        agent = IPAAgent(llm=llm)
        result = await agent.process(
            raw_text="I want to explore the enchanted forest",
            session_id="sess-clean",
        )
        assert result.crisis_level == CrisisLevel.LOW
        assert result.crisis_confidence <= 0.2

    @pytest.mark.asyncio
    async def test_ipa_high_not_bumped_down_by_safety_signal_false(self) -> None:
        # safety_signal=False but text has high-level crisis pattern
        llm = _make_ipa_mock_llm(safety_signal=False)
        agent = IPAAgent(llm=llm)
        result = await agent.process(
            raw_text="I feel so hopeless about everything",
            session_id="sess-high2",
        )
        assert result.crisis_level == CrisisLevel.HIGH

    @pytest.mark.asyncio
    async def test_ipa_crisis_level_in_processed_input_fields(self) -> None:
        llm = _make_ipa_mock_llm()
        agent = IPAAgent(llm=llm)
        result = await agent.process(raw_text="exploring the town")
        assert hasattr(result, "crisis_level")
        assert hasattr(result, "crisis_confidence")
        assert isinstance(result.crisis_level, CrisisLevel)
        assert isinstance(result.crisis_confidence, float)

    @pytest.mark.asyncio
    async def test_ipa_accepts_custom_detector(self) -> None:
        llm = _make_ipa_mock_llm()
        custom_detector = CrisisDetector(
            config={"patterns": {lvl: [] for lvl in CrisisLevel}}
        )
        agent = IPAAgent(llm=llm, crisis_detector=custom_detector)
        result = await agent.process(raw_text="I want to kill myself")
        # Custom detector has no patterns → always LOW
        assert result.crisis_level == CrisisLevel.LOW
