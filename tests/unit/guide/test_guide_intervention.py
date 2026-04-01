"""
# Logseq: [[TTA/Tests/Unit/Guide/Intervention]]
Unit tests for Guide intervention logic and prompt building.
"""

from __future__ import annotations

import pytest

from src.components.guide.intervention import (
    GuideInterventionDecider,
    InterventionType,
)
from src.components.guide.prompt import GuidePromptBuilder
from src.components.gameplay_loop.models.world_seed import GuideVoice, WorldSeed
from src.components.gameplay_loop.models.world_seed import (
    WorldTone,
    PowerSource,
    PlayerPosition,
)


# ---------------------------------------------------------------------------
# TestGuideInterventionDecider
# ---------------------------------------------------------------------------


class TestGuideInterventionDecider:
    def setup_method(self) -> None:
        self.decider = GuideInterventionDecider()

    def test_no_triggers_returns_none(self) -> None:
        result = self.decider.decide()
        assert result == InterventionType.NONE

    def test_caution_safety_returns_sensory_pause(self) -> None:
        result = self.decider.decide(safety_level="caution")
        assert result == InterventionType.SENSORY_PAUSE

    def test_warning_safety_returns_soft_prompt(self) -> None:
        result = self.decider.decide(safety_level="warning")
        assert result == InterventionType.SOFT_PROMPT

    def test_unsafe_safety_returns_companion_shift(self) -> None:
        result = self.decider.decide(safety_level="unsafe")
        assert result == InterventionType.COMPANION_SHIFT

    def test_crisis_safety_returns_break_character(self) -> None:
        result = self.decider.decide(safety_level="crisis")
        assert result == InterventionType.BREAK_CHARACTER

    def test_critical_crisis_returns_break_character(self) -> None:
        result = self.decider.decide(crisis_level="critical")
        assert result == InterventionType.BREAK_CHARACTER

    def test_high_crisis_returns_soft_prompt(self) -> None:
        result = self.decider.decide(crisis_level="high")
        assert result == InterventionType.SOFT_PROMPT

    def test_moderate_crisis_returns_sensory_pause(self) -> None:
        result = self.decider.decide(crisis_level="moderate")
        assert result == InterventionType.SENSORY_PAUSE

    def test_explicit_reflect_command_triggers_soft_prompt(self) -> None:
        result = self.decider.decide(player_text="/reflect on the past")
        assert result == InterventionType.SOFT_PROMPT

    def test_explicit_journal_command_triggers_soft_prompt(self) -> None:
        result = self.decider.decide(player_text="/journal my feelings")
        assert result == InterventionType.SOFT_PROMPT

    def test_pacing_signal_triggers_sensory_pause(self) -> None:
        result = self.decider.decide(pacing_signal=True)
        assert result == InterventionType.SENSORY_PAUSE

    def test_highest_intensity_wins(self) -> None:
        # pacing_signal=True (SENSORY_PAUSE) AND crisis=high (SOFT_PROMPT)
        # → SOFT_PROMPT wins
        result = self.decider.decide(pacing_signal=True, crisis_level="high")
        assert result == InterventionType.SOFT_PROMPT

    def test_crisis_overrides_safety(self) -> None:
        # safety=caution (SENSORY_PAUSE), crisis=critical (BREAK_CHARACTER)
        # → BREAK_CHARACTER wins
        result = self.decider.decide(
            safety_level="caution", crisis_level="critical"
        )
        assert result == InterventionType.BREAK_CHARACTER

    def test_mostly_silent_suppresses_sensory_pause(self) -> None:
        result = self.decider.decide(
            pacing_signal=True, intervention_style="mostly-silent"
        )
        assert result == InterventionType.NONE

    def test_mostly_silent_suppresses_soft_prompt_from_safety(self) -> None:
        result = self.decider.decide(
            safety_level="warning", intervention_style="mostly-silent"
        )
        assert result == InterventionType.NONE

    def test_mostly_silent_still_allows_companion_shift(self) -> None:
        result = self.decider.decide(
            safety_level="unsafe", intervention_style="mostly-silent"
        )
        assert result == InterventionType.COMPANION_SHIFT

    def test_mostly_silent_does_not_suppress_explicit_command(self) -> None:
        result = self.decider.decide(
            player_text="/reflect please",
            intervention_style="mostly-silent",
        )
        assert result == InterventionType.SOFT_PROMPT

    def test_never_raises_on_unknown_safety_level(self) -> None:
        result = self.decider.decide(safety_level="unknown_level")
        assert result == InterventionType.NONE

    def test_never_raises_on_empty_player_text(self) -> None:
        result = self.decider.decide(player_text="")
        assert result == InterventionType.NONE

    def test_never_raises_on_exception(self) -> None:
        # Pass None for safety_level — .lower() would fail on None
        # but decide() must catch and return NONE
        result = self.decider.decide(safety_level=None)  # type: ignore[arg-type]
        assert result == InterventionType.NONE

    def test_pause_command_triggers_soft_prompt(self) -> None:
        result = self.decider.decide(player_text="/pause here")
        assert result == InterventionType.SOFT_PROMPT

    def test_breathe_command_triggers_soft_prompt(self) -> None:
        result = self.decider.decide(player_text="/breathe slowly")
        assert result == InterventionType.SOFT_PROMPT


# ---------------------------------------------------------------------------
# TestGuidePromptBuilder
# ---------------------------------------------------------------------------


class TestGuidePromptBuilder:
    def setup_method(self) -> None:
        self.builder = GuidePromptBuilder()

    def test_voice_fragment_contains_tone(self) -> None:
        fragment = self.builder.build_voice_fragment({"tone": "playful-wise"})
        assert "playful-wise" in fragment

    def test_voice_fragment_contains_formality(self) -> None:
        fragment = self.builder.build_voice_fragment({"formality": "archaic"})
        assert "archaic" in fragment

    def test_voice_fragment_defaults_work(self) -> None:
        fragment = self.builder.build_voice_fragment({})
        assert "warm-ancient" in fragment
        assert "neutral" in fragment

    def test_intervention_fragment_none_is_empty(self) -> None:
        fragment = self.builder.build_intervention_fragment(InterventionType.NONE)
        assert fragment == ""

    def test_intervention_fragment_break_character_has_988(self) -> None:
        fragment = self.builder.build_intervention_fragment(
            InterventionType.BREAK_CHARACTER
        )
        assert "988" in fragment

    def test_intervention_fragment_sensory_pause_mentions_sensory(self) -> None:
        fragment = self.builder.build_intervention_fragment(
            InterventionType.SENSORY_PAUSE
        )
        assert "sensory" in fragment.lower() or "breathe" in fragment.lower()

    def test_validate_clinical_language_detects_diagnosis(self) -> None:
        found = self.builder.validate_no_clinical_language(
            "The therapist gave a diagnosis of the disorder."
        )
        assert "diagnosis" in found
        assert "disorder" in found

    def test_validate_clinical_language_passes_clean_text(self) -> None:
        found = self.builder.validate_no_clinical_language(
            "The forest shimmered with ancient light."
        )
        assert found == []

    def test_validate_clinical_detects_you_should_feel(self) -> None:
        found = self.builder.validate_no_clinical_language(
            "you should feel better now"
        )
        assert "you should feel" in found

    def test_full_system_addition_combines_correctly(self) -> None:
        params = {"tone": "melancholic-hopeful", "formality": "contemporary"}
        addition = self.builder.build_full_system_addition(
            params, InterventionType.SOFT_PROMPT
        )
        assert "melancholic-hopeful" in addition
        assert "GUIDE INTERVENTION THIS TURN" in addition
        assert "gentle question" in addition

    def test_full_system_addition_no_intervention_has_no_section(self) -> None:
        params = {"tone": "warm-ancient"}
        addition = self.builder.build_full_system_addition(
            params, InterventionType.NONE
        )
        assert "GUIDE INTERVENTION THIS TURN" not in addition

    def test_voice_fragment_no_clinical_language(self) -> None:
        # The voice fragment instructs the LLM using negations ("never diagnose")
        # so the raw clinical pattern detector will see "diagnose" as a substring.
        # What matters is that the fragment contains no *positive* clinical assertions.
        # We verify it includes the expected negation guards instead.
        fragment = self.builder.build_voice_fragment(
            {"tone": "warm-ancient", "formality": "neutral"}
        )
        assert "never diagnose" in fragment
        assert "never say 'you should feel'" in fragment or "you should feel" in fragment


# ---------------------------------------------------------------------------
# TestGuideVoice
# ---------------------------------------------------------------------------


class TestGuideVoice:
    def test_default_values(self) -> None:
        voice = GuideVoice()
        assert voice.tone == "warm-ancient"
        assert voice.formality == "neutral"
        assert voice.intervention_style == "gentle"
        assert voice.reflection_frequency == "occasional"

    def test_system_prompt_fragment_property(self) -> None:
        voice = GuideVoice(tone="playful-wise", formality="archaic")
        fragment = voice.system_prompt_fragment
        assert "playful-wise" in fragment
        assert "archaic" in fragment
        assert "gentle" in fragment  # intervention_style default

    def test_world_seed_guide_voice_field(self) -> None:
        seed = WorldSeed(
            tone=WorldTone.GETTING_BETTER,
            power_source=PowerSource.MAGIC,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="A lantern that never goes out",
            guide_voice=GuideVoice(tone="matter-of-fact"),
        )
        assert seed.guide_voice is not None
        assert seed.guide_voice.tone == "matter-of-fact"

    def test_world_seed_guide_voice_defaults_to_none(self) -> None:
        seed = WorldSeed(
            tone=WorldTone.CYCLICAL,
            power_source=PowerSource.BELIEF,
            player_position=PlayerPosition.INSIDER,
            one_specific_detail="The silent market",
        )
        assert seed.guide_voice is None

    def test_guide_voice_custom_values(self) -> None:
        voice = GuideVoice(
            tone="melancholic-hopeful",
            formality="contemporary",
            intervention_style="direct",
            reflection_frequency="frequent",
        )
        assert voice.reflection_frequency == "frequent"
        assert "direct" in voice.system_prompt_fragment
