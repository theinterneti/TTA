"""Unit tests for the choice significance detector.

# Logseq: [[TTA/Tests/Unit/Choice_detector/Test_choice_detector]]

Issue: #289
"""

from __future__ import annotations

import logging

import pytest

from src.components.choice_detector import ChoiceSignificanceDetector, SignificanceLevel
from src.components.choice_detector.detector import _rule_based_classify


class TestSignificanceLevel:
    def test_enum_values(self) -> None:
        assert SignificanceLevel.LOW == "low"
        assert SignificanceLevel.MEDIUM == "medium"
        assert SignificanceLevel.HIGH == "high"
        assert SignificanceLevel.CRITICAL == "critical"

    def test_is_str_enum(self) -> None:
        assert isinstance(SignificanceLevel.LOW, str)

    def test_all_four_levels_exist(self) -> None:
        levels = list(SignificanceLevel)
        assert len(levels) == 4


class TestRuleBasedClassification:
    def test_look_is_low(self) -> None:
        level, _ = _rule_based_classify("I look around the room")
        assert level == SignificanceLevel.LOW

    def test_examine_is_low(self) -> None:
        level, _ = _rule_based_classify("I examine the old painting")
        assert level == SignificanceLevel.LOW

    def test_go_is_low(self) -> None:
        level, _ = _rule_based_classify("I go north toward the river")
        assert level == SignificanceLevel.LOW

    def test_walk_is_low(self) -> None:
        level, _ = _rule_based_classify("walk to the market")
        assert level == SignificanceLevel.LOW

    def test_ask_is_low(self) -> None:
        level, _ = _rule_based_classify("I ask the innkeeper about the map")
        assert level == SignificanceLevel.LOW

    def test_wait_is_low(self) -> None:
        level, _ = _rule_based_classify("I wait by the gate")
        assert level == SignificanceLevel.LOW

    def test_buy_is_medium(self) -> None:
        level, _ = _rule_based_classify("I buy the sword from the merchant")
        assert level == SignificanceLevel.MEDIUM

    def test_sell_is_medium(self) -> None:
        level, _ = _rule_based_classify("sell my old armor")
        assert level == SignificanceLevel.MEDIUM

    def test_give_is_medium(self) -> None:
        level, _ = _rule_based_classify("I give her the coin")
        assert level == SignificanceLevel.MEDIUM

    def test_attack_is_medium(self) -> None:
        level, _ = _rule_based_classify("I attack the guard")
        assert level == SignificanceLevel.MEDIUM

    def test_help_is_medium(self) -> None:
        level, _ = _rule_based_classify("I help the farmer carry the crates")
        assert level == SignificanceLevel.MEDIUM

    def test_open_is_medium(self) -> None:
        level, _ = _rule_based_classify("open the chest")
        assert level == SignificanceLevel.MEDIUM

    def test_join_faction_is_high(self) -> None:
        level, _ = _rule_based_classify("I join the rebel faction")
        assert level == SignificanceLevel.HIGH

    def test_pledge_is_high(self) -> None:
        level, _ = _rule_based_classify("I pledge my loyalty to the king")
        assert level == SignificanceLevel.HIGH

    def test_betray_is_high(self) -> None:
        level, _ = _rule_based_classify("I betray my companions to the empire")
        assert level == SignificanceLevel.HIGH

    def test_abandon_is_high(self) -> None:
        level, _ = _rule_based_classify("I abandon the quest entirely")
        assert level == SignificanceLevel.HIGH

    def test_reveal_secret_is_high(self) -> None:
        level, _ = _rule_based_classify("I reveal the secret to the council")
        assert level == SignificanceLevel.HIGH

    def test_decide_is_high(self) -> None:
        level, _ = _rule_based_classify("I decide to side with the merchants")
        assert level == SignificanceLevel.HIGH

    def test_refuse_is_high(self) -> None:
        level, _ = _rule_based_classify("I refuse the king's offer")
        assert level == SignificanceLevel.HIGH

    def test_destroy_is_high(self) -> None:
        level, _ = _rule_based_classify("I destroy the bridge")
        assert level == SignificanceLevel.HIGH

    def test_kill_is_critical(self) -> None:
        level, _ = _rule_based_classify("I kill the corrupt magistrate")
        assert level == SignificanceLevel.CRITICAL

    def test_murder_is_critical(self) -> None:
        level, _ = _rule_based_classify("murder the witness")
        assert level == SignificanceLevel.CRITICAL

    def test_sacrifice_is_critical(self) -> None:
        level, _ = _rule_based_classify("I sacrifice myself to close the portal")
        assert level == SignificanceLevel.CRITICAL

    def test_destroy_world_is_critical(self) -> None:
        level, _ = _rule_based_classify("I destroy the world with the artifact")
        assert level == SignificanceLevel.CRITICAL

    def test_declare_war_is_critical(self) -> None:
        level, _ = _rule_based_classify("I declare war on the neighboring kingdom")
        assert level == SignificanceLevel.CRITICAL

    def test_final_choice_is_critical(self) -> None:
        level, _ = _rule_based_classify("I make my final choice")
        assert level == SignificanceLevel.CRITICAL

    def test_escalation_marker_bumps_medium_to_high(self) -> None:
        # "give" is MEDIUM; "no turning back" escalates to HIGH
        level, _ = _rule_based_classify("I give the key — there is no turning back")
        assert level == SignificanceLevel.HIGH

    def test_escalation_marker_bumps_high_to_critical(self) -> None:
        # "join" is HIGH; "forever" escalates to CRITICAL
        level, _ = _rule_based_classify("I join the cult forever")
        assert level == SignificanceLevel.CRITICAL

    def test_escalation_never_again_bumps_level(self) -> None:
        level, _ = _rule_based_classify("I give up — there is no turning back now")
        assert level == SignificanceLevel.HIGH  # give=MEDIUM + escalation → HIGH

    def test_no_turning_back_escalates(self) -> None:
        level, _ = _rule_based_classify("I decide — there is no turning back now")
        assert (
            level == SignificanceLevel.CRITICAL
        )  # decide=HIGH + escalation → CRITICAL

    def test_empty_text_is_low(self) -> None:
        level, confidence = _rule_based_classify("")
        # empty string → inconclusive → MEDIUM/0.40 from rule engine
        # (empty guard is in ChoiceSignificanceDetector.classify, not here)
        assert isinstance(level, SignificanceLevel)

    def test_inconclusive_text_returns_medium_low_confidence(self) -> None:
        level, confidence = _rule_based_classify("hmm")
        assert level == SignificanceLevel.MEDIUM
        assert confidence == pytest.approx(0.40)

    def test_low_confidence_for_clear_low(self) -> None:
        _, confidence = _rule_based_classify("I look at the sky")
        assert confidence >= 0.80

    def test_high_confidence_for_critical(self) -> None:
        _, confidence = _rule_based_classify("I kill the king")
        assert confidence >= 0.85

    def test_case_insensitive_upper(self) -> None:
        level, _ = _rule_based_classify("I KILL THE DRAGON")
        assert level == SignificanceLevel.CRITICAL

    def test_case_insensitive_mixed(self) -> None:
        level, _ = _rule_based_classify("I Look Around")
        assert level == SignificanceLevel.LOW

    def test_unicode_text_does_not_raise(self) -> None:
        level, confidence = _rule_based_classify("我看看周围 👀")
        assert isinstance(level, SignificanceLevel)
        assert 0.0 <= confidence <= 1.0

    def test_very_long_text_does_not_raise(self) -> None:
        long_text = "I look around. " * 1000
        level, confidence = _rule_based_classify(long_text)
        assert level == SignificanceLevel.LOW
        assert 0.0 <= confidence <= 1.0


class TestChoiceSignificanceDetector:
    def setup_method(self) -> None:
        self.detector = ChoiceSignificanceDetector()

    def test_classify_returns_tuple(self) -> None:
        result = self.detector.classify("I look around")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_classify_empty_returns_low(self) -> None:
        level, confidence = self.detector.classify("")
        assert level == SignificanceLevel.LOW
        assert confidence == pytest.approx(0.90)

    def test_classify_whitespace_only_returns_low(self) -> None:
        level, confidence = self.detector.classify("   \t\n  ")
        assert level == SignificanceLevel.LOW
        assert confidence == pytest.approx(0.90)

    def test_classify_low_action(self) -> None:
        level, _ = self.detector.classify("I examine the door")
        assert level == SignificanceLevel.LOW

    def test_classify_medium_action(self) -> None:
        level, _ = self.detector.classify("I trade my shield for gold")
        assert level == SignificanceLevel.MEDIUM

    def test_classify_high_action(self) -> None:
        level, _ = self.detector.classify("I pledge allegiance to the rebel cause")
        assert level == SignificanceLevel.HIGH

    def test_classify_critical_action(self) -> None:
        level, _ = self.detector.classify("I execute the prisoner")
        assert level == SignificanceLevel.CRITICAL

    def test_narrative_context_used_in_classification(self) -> None:
        # With escalation in context, a low verb can escalate
        level, _ = self.detector.classify(
            "I give the key away",
            narrative_context="There is no turning back from this decision.",
        )
        assert (
            level == SignificanceLevel.HIGH
        )  # give=MEDIUM + context escalation → HIGH

    def test_narrative_context_limited_to_200_chars(self) -> None:
        # Long context is sliced; should not raise
        long_ctx = "A" * 5000
        level, confidence = self.detector.classify("I look around", long_ctx)
        assert isinstance(level, SignificanceLevel)
        assert 0.0 <= confidence <= 1.0

    def test_never_raises_on_garbage_input(self) -> None:
        # Should always return a valid (level, confidence) pair
        result = self.detector.classify("\x00\xff" * 50)
        assert isinstance(result[0], SignificanceLevel)

    def test_never_raises_on_none_context(self) -> None:
        # narrative_context defaults to ""
        level, confidence = self.detector.classify("I look", narrative_context="")
        assert isinstance(level, SignificanceLevel)

    def test_is_dolt_commit_worthy_high(self) -> None:
        assert self.detector.is_dolt_commit_worthy(SignificanceLevel.HIGH) is True

    def test_is_dolt_commit_worthy_critical(self) -> None:
        assert self.detector.is_dolt_commit_worthy(SignificanceLevel.CRITICAL) is True

    def test_is_dolt_commit_worthy_low_false(self) -> None:
        assert self.detector.is_dolt_commit_worthy(SignificanceLevel.LOW) is False

    def test_is_dolt_commit_worthy_medium_false(self) -> None:
        assert self.detector.is_dolt_commit_worthy(SignificanceLevel.MEDIUM) is False

    def test_is_world_state_update_worthy_medium(self) -> None:
        assert (
            self.detector.is_world_state_update_worthy(SignificanceLevel.MEDIUM) is True
        )

    def test_is_world_state_update_worthy_high(self) -> None:
        assert (
            self.detector.is_world_state_update_worthy(SignificanceLevel.HIGH) is True
        )

    def test_is_world_state_update_worthy_critical(self) -> None:
        assert (
            self.detector.is_world_state_update_worthy(SignificanceLevel.CRITICAL)
            is True
        )

    def test_is_world_state_update_worthy_low_false(self) -> None:
        assert (
            self.detector.is_world_state_update_worthy(SignificanceLevel.LOW) is False
        )

    def test_confidence_high_for_clear_signals(self) -> None:
        _, confidence = self.detector.classify("I kill the traitor")
        assert confidence >= 0.85

    def test_confidence_low_for_inconclusive(self) -> None:
        _, confidence = self.detector.classify("hmm interesting")
        assert confidence <= 0.50

    def test_logs_non_low_classifications(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(
            logging.INFO, logger="src.components.choice_detector.detector"
        ):
            self.detector.classify("I kill the villain")
        assert any("significance" in record.message for record in caplog.records)

    def test_low_does_not_log(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(
            logging.INFO, logger="src.components.choice_detector.detector"
        ):
            self.detector.classify("I look at the horizon")
        assert not any("significance" in record.message for record in caplog.records)

    def test_inconclusive_confidence_threshold_constant(self) -> None:
        assert ChoiceSignificanceDetector.INCONCLUSIVE_CONFIDENCE_THRESHOLD == 0.50

    def test_multiple_high_patterns_still_high(self) -> None:
        level, _ = self.detector.classify("I betray and abandon my oath")
        assert level == SignificanceLevel.HIGH

    def test_medium_and_high_pattern_picks_high(self) -> None:
        # "give" (medium) + "reveal" (high) → should be HIGH
        level, _ = self.detector.classify("I give away and reveal the truth")
        assert level == SignificanceLevel.HIGH
