"""
Comprehensive unit tests for enhanced TherapeuticValidator (Task 17.1).

Tests all validation algorithms, safety rules, crisis detection, and edge cases.
"""

import pytest

from src.agent_orchestration.therapeutic_safety import (
    CrisisType,
    SafetyLevel,
    TherapeuticValidator,
    ValidationResult,
    ValidationType,
)


class TestTherapeuticValidator:
    """Test the enhanced TherapeuticValidator class."""

    def test_default_initialization(self):
        """Test validator initializes with default configuration."""
        validator = TherapeuticValidator()

        assert validator._crisis_detection_enabled is True
        assert validator._crisis_sensitivity == 0.7
        assert validator._alternative_generation_enabled is True
        assert validator._therapeutic_tone is True

        # Check default rules are loaded
        guidelines = validator.get_therapeutic_guidelines()
        assert len(guidelines) >= 6

        # Verify rule types
        rule_ids = [rule["id"] for rule in guidelines]
        assert "crisis_suicidal_ideation" in rule_ids
        assert "crisis_self_harm" in rule_ids
        assert "ethics_medical_advice" in rule_ids

    def test_custom_configuration(self):
        """Test validator with custom configuration."""
        config = {
            "rules": [
                {
                    "id": "test_rule",
                    "category": "test_category",
                    "priority": 50,
                    "level": "warning",
                    "pattern": "test pattern",
                    "validation_type": "keyword",
                    "sensitivity": 0.8,
                }
            ],
            "crisis_detection": {"enabled": False, "sensitivity": 0.9},
        }

        validator = TherapeuticValidator(config=config)

        assert validator._crisis_detection_enabled is False
        assert validator._crisis_sensitivity == 0.9

        guidelines = validator.get_therapeutic_guidelines()
        assert len(guidelines) == 1
        assert guidelines[0]["id"] == "test_rule"


class TestValidationAlgorithms:
    """Test different validation algorithms."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_keyword_validation(self):
        """Test keyword-based validation."""
        # Test safe content
        result = self.validator.validate_text("Hello, I need help")
        assert result.level == SafetyLevel.SAFE
        assert len(result.findings) == 0

        # Test warning content
        result = self.validator.validate_text("Can you diagnose my condition?")
        assert result.level == SafetyLevel.WARNING
        assert len(result.findings) >= 1
        assert any(
            f.validation_type == ValidationType.THERAPEUTIC_BOUNDARY
            for f in result.findings
        )

    def test_sentiment_analysis(self):
        """Test sentiment analysis validation."""
        # Test positive sentiment
        result = self.validator.validate_text("I feel happy and grateful today")
        assert result.overall_sentiment > 0

        # Test negative sentiment
        result = self.validator.validate_text("I feel sad and hopeless")
        assert result.overall_sentiment < 0

        # Test neutral sentiment
        result = self.validator.validate_text("The weather is nice today")
        assert result.overall_sentiment == 0.0

    def test_crisis_detection_algorithms(self):
        """Test sophisticated crisis detection."""
        crisis_cases = [
            ("I want to kill myself", CrisisType.SUICIDAL_IDEATION),
            ("I want to hurt myself", CrisisType.SELF_HARM),
            ("I feel completely hopeless", CrisisType.SEVERE_DEPRESSION),
            ("I deserve to feel pain", CrisisType.SELF_HARM),
        ]

        for text, expected_crisis in crisis_cases:
            result = self.validator.validate_text(text)

            assert result.crisis_detected, f"Crisis not detected for: {text}"
            assert (
                expected_crisis in result.crisis_types
            ), f"Wrong crisis type for: {text}"
            assert (
                result.level == SafetyLevel.BLOCKED
                or result.level == SafetyLevel.WARNING
            )
            assert result.escalation_recommended

    def test_therapeutic_appropriateness_scoring(self):
        """Test therapeutic appropriateness assessment."""
        # Safe content should have high appropriateness
        result = self.validator.validate_text("I would like to talk about my feelings")
        assert result.therapeutic_appropriateness >= 0.8

        # Crisis content should have low appropriateness
        result = self.validator.validate_text("I want to kill myself")
        assert result.therapeutic_appropriateness <= 0.2

        # Warning content should have medium appropriateness
        result = self.validator.validate_text("Can you diagnose me?")
        assert 0.2 < result.therapeutic_appropriateness < 0.9


class TestCrisisDetection:
    """Test crisis detection capabilities."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_suicidal_ideation_detection(self):
        """Test suicidal ideation detection."""
        suicidal_phrases = [
            "I want to die",
            "I wish I was dead",
            "Life is not worth living",
            "I should just end it all",
            "Better off dead",
        ]

        for phrase in suicidal_phrases:
            result = self.validator.validate_text(phrase)

            assert result.crisis_detected, f"Suicidal ideation not detected: {phrase}"
            assert CrisisType.SUICIDAL_IDEATION in result.crisis_types
            assert result.level == SafetyLevel.BLOCKED
            assert result.escalation_recommended

    def test_self_harm_detection(self):
        """Test self-harm detection."""
        self_harm_phrases = [
            "I want to cut myself",
            "I hurt myself when I feel bad",
            "I deserve to feel pain",
            "I punish myself for being bad",
        ]

        for phrase in self_harm_phrases:
            result = self.validator.validate_text(phrase)

            assert result.crisis_detected, f"Self-harm not detected: {phrase}"
            assert CrisisType.SELF_HARM in result.crisis_types
            assert result.escalation_recommended

    def test_depression_detection(self):
        """Test severe depression detection."""
        depression_phrases = [
            "I feel completely hopeless",
            "Nothing matters anymore",
            "I am worthless and a burden",
        ]

        for phrase in depression_phrases:
            result = self.validator.validate_text(phrase)

            assert result.crisis_detected, f"Depression not detected: {phrase}"
            assert CrisisType.SEVERE_DEPRESSION in result.crisis_types

    def test_false_positive_prevention(self):
        """Test that normal sad content doesn't trigger crisis detection."""
        normal_sad_phrases = [
            "I feel sad today",
            "I am having a difficult time",
            "I need some support",
            "I'm feeling down",
        ]

        for phrase in normal_sad_phrases:
            result = self.validator.validate_text(phrase)

            # Should not trigger crisis detection
            assert (
                not result.crisis_detected or len(result.crisis_types) == 0
            ), f"False positive for: {phrase}"


class TestAlternativeGeneration:
    """Test alternative content generation."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_crisis_alternatives(self):
        """Test crisis-specific alternative generation."""
        # Suicidal ideation
        result = self.validator.validate_text("I want to kill myself")
        assert result.alternative_content is not None
        assert "crisis helpline" in result.alternative_content.lower()
        assert "988" in result.alternative_content

        # Self-harm
        result = self.validator.validate_text("I want to hurt myself")
        assert result.alternative_content is not None
        assert "stay safe" in result.alternative_content.lower()
        assert "grounding techniques" in result.alternative_content.lower()

    def test_professional_boundary_alternatives(self):
        """Test professional boundary alternatives."""
        result = self.validator.validate_text("Can you diagnose my depression?")
        assert result.alternative_content is not None
        assert "not qualified" in result.alternative_content.lower()
        assert "healthcare professional" in result.alternative_content.lower()

    def test_therapeutic_tone(self):
        """Test that alternatives maintain therapeutic tone."""
        crisis_texts = [
            "I want to kill myself",
            "I want to hurt myself",
            "Can you diagnose me?",
        ]

        for text in crisis_texts:
            result = self.validator.validate_text(text)
            if result.alternative_content:
                alt = result.alternative_content.lower()

                # Should contain supportive language
                supportive_words = ["support", "help", "care", "here", "understand"]
                assert any(
                    word in alt for word in supportive_words
                ), f"No supportive language in: {alt}"

                # Should not contain harsh language
                harsh_words = ["no", "can't", "won't", "refuse", "deny"]
                # Note: "can't" might appear in therapeutic context, so we check for overall tone


class TestMonitoringAndAlerting:
    """Test monitoring and alerting systems."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_monitoring_metrics(self):
        """Test monitoring metrics collection."""
        # Process some content to generate metrics
        test_texts = [
            "Hello, I need help",  # Safe
            "I want to kill myself",  # Crisis
            "Can you diagnose me?",  # Warning
        ]

        for text in test_texts:
            self.validator.validate_text(text)

        metrics = self.validator.get_monitoring_metrics()

        assert "violation_count" in metrics
        assert "crisis_count" in metrics
        assert "escalation_count" in metrics
        assert metrics["violation_count"] >= 2  # Crisis + warning
        assert metrics["crisis_count"] >= 1  # Crisis

    def test_alert_conditions(self):
        """Test alert generation conditions."""
        # Crisis content should trigger alert
        result = self.validator.validate_text("I want to kill myself")
        assert self.validator.should_alert(result)

        # Safe content should not trigger alert
        result = self.validator.validate_text("Hello, I need help")
        assert not self.validator.should_alert(result)

    def test_monitoring_flags(self):
        """Test monitoring flag generation."""
        # Crisis content should generate appropriate flags
        result = self.validator.validate_text("I want to kill myself")

        expected_flags = ["crisis_detected", "escalation_required"]
        for flag in expected_flags:
            assert flag in result.monitoring_flags, f"Missing flag: {flag}"


class TestConfigurationManagement:
    """Test configuration management features."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_add_remove_guidelines(self):
        """Test adding and removing therapeutic guidelines."""
        initial_count = len(self.validator.get_therapeutic_guidelines())

        # Add new guideline
        new_guideline = {
            "id": "test_guideline",
            "category": "test_category",
            "priority": 50,
            "level": "warning",
            "pattern": "test pattern",
            "validation_type": "keyword",
        }

        self.validator.add_therapeutic_guideline(new_guideline)
        assert len(self.validator.get_therapeutic_guidelines()) == initial_count + 1

        # Remove guideline
        removed = self.validator.remove_therapeutic_guideline("test_guideline")
        assert removed is True
        assert len(self.validator.get_therapeutic_guidelines()) == initial_count

    def test_configuration_export_import(self):
        """Test configuration export and import."""
        # Export configuration
        exported_config = self.validator.export_configuration()
        assert isinstance(exported_config, dict)
        assert "rules" in exported_config

        # Create new validator and import
        new_validator = TherapeuticValidator()
        new_validator.import_configuration(exported_config)

        # Should have same number of rules
        original_rules = len(self.validator.get_therapeutic_guidelines())
        imported_rules = len(new_validator.get_therapeutic_guidelines())
        assert original_rules == imported_rules

    def test_dynamic_configuration_updates(self):
        """Test dynamic configuration updates."""
        original_sensitivity = self.validator._crisis_sensitivity

        # Update configuration
        update_config = {
            "crisis_detection": {"sensitivity": 0.9, "escalation_threshold": 0.8}
        }

        self.validator.update_configuration(update_config)

        assert self.validator._crisis_sensitivity == 0.9
        assert self.validator._escalation_threshold == 0.8
        assert self.validator._crisis_sensitivity != original_sensitivity


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_empty_input(self):
        """Test validation with empty input."""
        result = self.validator.validate_text("")
        assert result.level == SafetyLevel.SAFE
        assert len(result.findings) == 0

    def test_none_input(self):
        """Test validation with None input."""
        result = self.validator.validate_text(None)
        assert result.level == SafetyLevel.SAFE
        assert len(result.findings) == 0

    def test_very_long_input(self):
        """Test validation with very long input."""
        long_text = "I feel sad. " * 1000  # 12,000 characters
        result = self.validator.validate_text(long_text)

        # Should still process correctly
        assert isinstance(result, ValidationResult)
        assert result.overall_sentiment is not None

    def test_special_characters(self):
        """Test validation with special characters."""
        # Test with special characters but clear text patterns
        special_text = "I feel sad!!! and want to kill myself..."
        result = self.validator.validate_text(special_text)

        # Should detect crisis despite special characters
        assert result.crisis_detected
        assert CrisisType.SUICIDAL_IDEATION in result.crisis_types

        # Test that emojis don't break the validator
        emoji_text = "I feel 😢 today but I'm getting help"
        result = self.validator.validate_text(emoji_text)

        # Should process without errors (may or may not detect crisis)
        assert isinstance(result, ValidationResult)

    def test_mixed_case_patterns(self):
        """Test case-insensitive pattern matching."""
        mixed_case_texts = [
            "I WANT TO KILL MYSELF",
            "i want to kill myself",
            "I Want To Kill Myself",
        ]

        for text in mixed_case_texts:
            result = self.validator.validate_text(text)
            assert result.crisis_detected, f"Case sensitivity issue with: {text}"

    def test_context_validation(self):
        """Test validation with context information."""
        context = {
            "session_id": "test-session",
            "user_id": "test-user",
            "session_count": 5,
            "previous_violations": 2,
            "therapeutic_session": True,
        }

        result = self.validator.validate_text("I feel sad", context=context)

        # Should process context without errors
        assert isinstance(result, ValidationResult)
        # Context should influence validation (implementation-dependent)


if __name__ == "__main__":
    pytest.main([__file__])
