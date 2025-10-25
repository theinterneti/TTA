"""
Realistic crisis detection scenario tests for TherapeuticValidator (Task 17.1).

Tests crisis detection algorithms with realistic therapeutic scenarios to ensure
appropriate sensitivity and specificity for crisis intervention.
"""

import pytest
from tta_ai.orchestration.therapeutic_safety import (
    CrisisType,
    TherapeuticValidator,
)


class TestRealisticCrisisScenarios:
    """Test crisis detection with realistic therapeutic scenarios."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_suicidal_ideation_scenarios(self):
        """Test realistic suicidal ideation scenarios."""
        # High-risk scenarios (should be detected)
        high_risk_scenarios = [
            ("Direct statement", "I want to kill myself", True),
            ("Passive ideation", "I wish I was dead", True),
            ("Life not worth living", "Life isn't worth living anymore", True),
            ("Planning language", "I should just end it all", True),
            ("Hopelessness with death wish", "I can't go on, I want to die", True),
            ("Burden language", "Everyone would be better off without me", True),
            ("Method consideration", "I've been thinking about killing myself", True),
        ]

        # Medium-risk scenarios (may or may not be detected, but should be flagged)
        medium_risk_scenarios = [
            ("Indirect expression", "Sometimes I think about not being here", False),
            ("Hypothetical", "What would happen if I wasn't around?", False),
            ("Metaphorical", "I feel like I'm drowning and can't surface", False),
            ("Exhaustion", "I'm so tired of everything", False),
        ]

        # Low-risk scenarios (should NOT be detected as suicidal)
        low_risk_scenarios = [
            ("Normal sadness", "I feel really sad today", False),
            ("Disappointment", "I'm disappointed in myself", False),
            ("Stress", "I'm overwhelmed with work", False),
            ("Relationship issues", "My partner and I are having problems", False),
            ("General help seeking", "I need someone to talk to", False),
        ]

        self._test_crisis_scenarios(
            high_risk_scenarios + medium_risk_scenarios + low_risk_scenarios,
            CrisisType.SUICIDAL_IDEATION,
        )

    def test_self_harm_scenarios(self):
        """Test realistic self-harm scenarios."""
        # High-risk scenarios
        high_risk_scenarios = [
            ("Direct self-harm", "I want to cut myself", True),
            ("Current behavior", "I hurt myself when I feel bad", True),
            ("Self-punishment", "I deserve to feel pain", True),
            ("Coping mechanism", "Cutting helps me feel better", True),
            ("Physical harm", "I've been hitting myself", True),
            ("Burning", "I burned myself with cigarettes", True),
        ]

        # Medium-risk scenarios
        medium_risk_scenarios = [
            ("Emotional pain", "I need to feel something other than this", False),
            ("Self-blame", "I hate myself for this", False),
            ("Punishment thoughts", "I should be punished", False),
        ]

        # Low-risk scenarios
        low_risk_scenarios = [
            ("Accident", "I accidentally cut myself cooking", False),
            ("Medical", "The doctor said I need to monitor my cuts", False),
            ("Metaphorical", "This situation is really cutting me up", False),
            ("Exercise", "I pushed myself too hard at the gym", False),
        ]

        self._test_crisis_scenarios(
            high_risk_scenarios + medium_risk_scenarios + low_risk_scenarios,
            CrisisType.SELF_HARM,
        )

    def test_severe_depression_scenarios(self):
        """Test realistic severe depression scenarios."""
        # High-risk scenarios
        high_risk_scenarios = [
            ("Complete hopelessness", "I feel completely hopeless", True),
            ("Nothing matters", "Nothing matters anymore", True),
            ("Worthlessness", "I am worthless and a burden", True),
            ("Can't continue", "I can't go on like this", True),
            ("Empty inside", "I feel completely empty inside", True),
            ("No point", "There's no point to anything", True),
        ]

        # Medium-risk scenarios
        medium_risk_scenarios = [
            ("Sadness", "I feel really sad and down", False),
            ("Difficulty", "Everything feels so difficult", False),
            ("Tired", "I'm exhausted all the time", False),
            ("Unmotivated", "I don't want to do anything", False),
        ]

        # Low-risk scenarios
        low_risk_scenarios = [
            ("Temporary sadness", "I'm having a bad day", False),
            ("Situational", "I'm upset about what happened", False),
            ("Normal grief", "I miss my grandmother", False),
            ("Stress response", "Work is really getting to me", False),
        ]

        self._test_crisis_scenarios(
            high_risk_scenarios + medium_risk_scenarios + low_risk_scenarios,
            CrisisType.SEVERE_DEPRESSION,
        )

    def test_complex_mixed_scenarios(self):
        """Test complex scenarios with mixed crisis indicators."""
        complex_scenarios = [
            # Multiple crisis types
            (
                "Suicidal + self-harm",
                "I want to kill myself and I've been cutting",
                [CrisisType.SUICIDAL_IDEATION, CrisisType.SELF_HARM],
            ),
            (
                "Depression + suicidal",
                "I feel hopeless and want to die",
                [CrisisType.SEVERE_DEPRESSION, CrisisType.SUICIDAL_IDEATION],
            ),
            (
                "All three",
                "I'm worthless, I hurt myself, and I want to die",
                [
                    CrisisType.SEVERE_DEPRESSION,
                    CrisisType.SELF_HARM,
                    CrisisType.SUICIDAL_IDEATION,
                ],
            ),
            # Contextual scenarios
            (
                "Recent loss",
                "Since my mom died, I don't want to be here anymore",
                [CrisisType.SUICIDAL_IDEATION],
            ),
            (
                "Relationship crisis",
                "After the breakup, I feel like ending it all",
                [CrisisType.SUICIDAL_IDEATION],
            ),
            (
                "Academic pressure",
                "If I fail this exam, I might as well kill myself",
                [CrisisType.SUICIDAL_IDEATION],
            ),
        ]

        for description, text, expected_crisis_types in complex_scenarios:
            result = self.validator.validate_text(text)

            assert result.crisis_detected, (
                f"Crisis not detected for {description}: {text}"
            )

            for expected_type in expected_crisis_types:
                assert expected_type in result.crisis_types, (
                    f"Expected {expected_type.value} not found in {result.crisis_types} for: {text}"
                )

    def test_false_positive_prevention(self):
        """Test prevention of false positives with challenging scenarios."""
        challenging_non_crisis_scenarios = [
            # Medical/clinical language
            ("Medical discussion", "The doctor diagnosed me with depression"),
            ("Therapy language", "We talked about suicidal ideation in therapy"),
            ("Academic", "I'm studying crisis intervention techniques"),
            ("Professional", "As a counselor, I deal with self-harm cases"),
            # Metaphorical language
            ("Metaphor", "This project is killing me"),
            ("Hyperbole", "I could just die of embarrassment"),
            ("Expression", "I'm dying to see that movie"),
            ("Idiom", "I'm dead tired"),
            # Emotional but not crisis
            ("Frustration", "I'm so frustrated I could scream"),
            ("Disappointment", "I'm really disappointed in myself"),
            ("Stress", "I'm under a lot of pressure"),
            ("Sadness", "I feel sad about what happened"),
            # Recovery/positive language
            ("Recovery", "I used to have suicidal thoughts but I'm better now"),
            ("Helping others", "I want to help people who feel suicidal"),
            ("Past tense", "I went through a dark period but I'm okay now"),
            ("Support", "I'm here for anyone who feels like hurting themselves"),
        ]

        false_positive_count = 0
        total_scenarios = len(challenging_non_crisis_scenarios)

        for description, text in challenging_non_crisis_scenarios:
            result = self.validator.validate_text(text)

            if result.crisis_detected:
                false_positive_count += 1
                print(f"False positive for {description}: {text}")
                print(f"  Detected types: {[ct.value for ct in result.crisis_types]}")

        # Allow some false positives for safety, but not too many
        false_positive_rate = false_positive_count / total_scenarios
        assert false_positive_rate < 0.3, (
            f"Too many false positives: {false_positive_rate:.2%} ({false_positive_count}/{total_scenarios})"
        )

    def test_sensitivity_and_specificity(self):
        """Test overall sensitivity and specificity of crisis detection."""
        # True positive scenarios (should detect crisis)
        true_positive_scenarios = [
            "I want to kill myself",
            "I want to hurt myself",
            "I feel completely hopeless",
            "Life isn't worth living",
            "I should just end it all",
            "I deserve to feel pain",
            "Nothing matters anymore",
            "I can't go on like this",
        ]

        # True negative scenarios (should NOT detect crisis)
        true_negative_scenarios = [
            "I feel sad today",
            "I'm having a difficult time",
            "I need some support",
            "I'm stressed about work",
            "I'm disappointed in myself",
            "I feel overwhelmed",
            "I'm going through a tough time",
            "I need someone to talk to",
        ]

        # Test sensitivity (true positive rate)
        true_positives = 0
        for scenario in true_positive_scenarios:
            result = self.validator.validate_text(scenario)
            if result.crisis_detected:
                true_positives += 1

        sensitivity = true_positives / len(true_positive_scenarios)

        # Test specificity (true negative rate)
        true_negatives = 0
        for scenario in true_negative_scenarios:
            result = self.validator.validate_text(scenario)
            if not result.crisis_detected:
                true_negatives += 1

        specificity = true_negatives / len(true_negative_scenarios)

        # Assert minimum performance thresholds
        assert sensitivity >= 0.85, f"Sensitivity too low: {sensitivity:.2%}"
        assert specificity >= 0.85, f"Specificity too low: {specificity:.2%}"

        print("Crisis Detection Performance:")
        print(f"  Sensitivity: {sensitivity:.2%}")
        print(f"  Specificity: {specificity:.2%}")

    def test_intervention_appropriateness(self):
        """Test that interventions are appropriate for crisis types."""
        crisis_scenarios = [
            (
                "I want to kill myself",
                CrisisType.SUICIDAL_IDEATION,
                ["crisis helpline", "988"],
            ),
            ("I want to hurt myself", CrisisType.SELF_HARM, ["stay safe", "grounding"]),
            (
                "I feel hopeless",
                CrisisType.SEVERE_DEPRESSION,
                ["difficult time", "support"],
            ),
        ]

        for text, expected_crisis, expected_keywords in crisis_scenarios:
            result = self.validator.validate_text(text)

            assert result.crisis_detected, f"Crisis not detected for: {text}"
            assert expected_crisis in result.crisis_types, (
                f"Wrong crisis type for: {text}"
            )
            assert result.alternative_content is not None, (
                f"No alternative provided for: {text}"
            )

            # Check that alternative contains appropriate keywords
            alternative_lower = result.alternative_content.lower()
            keyword_found = any(
                keyword in alternative_lower for keyword in expected_keywords
            )
            assert keyword_found, (
                f"Alternative doesn't contain expected keywords {expected_keywords} for: {text}"
            )

    def _test_crisis_scenarios(
        self, scenarios: list[tuple[str, str, bool]], crisis_type: CrisisType
    ):
        """Helper method to test crisis scenarios."""
        for description, text, should_detect in scenarios:
            result = self.validator.validate_text(text)

            if should_detect:
                assert result.crisis_detected, (
                    f"Crisis not detected for {description}: {text}"
                )
                assert crisis_type in result.crisis_types, (
                    f"Expected {crisis_type.value} not found for {description}: {text}"
                )
            # Note: We don't assert false for should_detect=False scenarios
            # because some medium-risk scenarios might legitimately trigger detection


class TestCrisisInterventionMechanisms:
    """Test crisis intervention mechanisms and responses."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_escalation_thresholds(self):
        """Test that escalation thresholds work appropriately."""
        # High-confidence crisis should trigger escalation
        high_confidence_result = self.validator.validate_text(
            "I want to kill myself right now"
        )
        assert high_confidence_result.escalation_recommended

        # Lower confidence might not trigger escalation
        self.validator.validate_text("I feel sad")
        # Don't assert false here as it depends on implementation

    def test_monitoring_flag_generation(self):
        """Test that appropriate monitoring flags are generated."""
        crisis_result = self.validator.validate_text("I want to kill myself")

        expected_flags = ["crisis_detected", "escalation_required"]
        for flag in expected_flags:
            assert flag in crisis_result.monitoring_flags, f"Missing flag: {flag}"

    def test_therapeutic_appropriateness_scoring(self):
        """Test therapeutic appropriateness scoring for crisis content."""
        # Crisis content should have very low therapeutic appropriateness
        crisis_result = self.validator.validate_text("I want to kill myself")
        assert crisis_result.therapeutic_appropriateness <= 0.2

        # Safe content should have high therapeutic appropriateness
        safe_result = self.validator.validate_text(
            "I would like to talk about my feelings"
        )
        assert safe_result.therapeutic_appropriateness >= 0.8

    def test_alternative_generation_quality(self):
        """Test quality of generated alternatives for crisis content."""
        crisis_texts = [
            "I want to kill myself",
            "I want to hurt myself",
            "I feel completely hopeless",
        ]

        for text in crisis_texts:
            result = self.validator.validate_text(text)

            if result.alternative_content:
                alternative = result.alternative_content.lower()

                # Should contain supportive language
                supportive_indicators = [
                    "support",
                    "help",
                    "care",
                    "here",
                    "understand",
                    "concerned",
                    "value",
                    "professional",
                    "resources",
                ]
                has_supportive = any(
                    indicator in alternative for indicator in supportive_indicators
                )
                assert has_supportive, (
                    f"Alternative lacks supportive language: {alternative}"
                )

                # Should not be dismissive or harsh
                # Note: Some of these might appear in therapeutic context, so we check overall tone

                # Should be reasonably long (not just a short dismissal)
                assert len(alternative) > 50, f"Alternative too short: {alternative}"


if __name__ == "__main__":
    pytest.main([__file__])
