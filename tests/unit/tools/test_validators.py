"""
Unit tests for validators (Phase 3 Tool Optimization).

Parametrized tests for naming and description validators.
Target: >95% coverage.
"""

import pytest

from src.agent_orchestration.tools.validators import (
    ToolDescriptionValidator,
    ToolNameValidator,
    ValidationSeverity,
)


class TestToolNameValidator:
    """Tests for ToolNameValidator."""

    @pytest.mark.parametrize(
        "name,expected_valid",
        [
            ("get_player_profile", True),
            ("list_active_sessions", True),
            ("create_character", True),
            ("update_world_state", True),
            ("search_available_worlds", True),
            ("delete_session", True),
            ("execute_workflow", True),
            # Invalid names
            ("get", False),  # Too short
            ("GetPlayerProfile", False),  # CamelCase
            ("get-player-profile", False),  # Hyphens
            ("get_player_profile_extra_segment", False),  # Too many segments
            ("123_invalid", False),  # Starts with number
        ],
    )
    def test_name_validation(self, name, expected_valid):
        """Test name validation with various inputs."""
        validator = ToolNameValidator()
        result = validator.validate(name)
        assert result.is_valid == expected_valid

    def test_approved_action(self):
        """Test approved action is accepted."""
        validator = ToolNameValidator()
        result = validator.validate("get_player_profile")
        assert result.is_valid is True
        assert result.score == 1.0

    def test_unapproved_action_warning(self):
        """Test unapproved action generates warning."""
        validator = ToolNameValidator()
        result = validator.validate("unknown_player_profile")
        # Should still be valid but with lower score
        assert result.score < 1.0
        assert any(
            f.severity == ValidationSeverity.WARNING for f in result.findings
        )

    def test_approved_resource(self):
        """Test approved resource is accepted."""
        validator = ToolNameValidator()
        result = validator.validate("get_player")
        assert result.is_valid is True

    def test_unapproved_resource_info(self):
        """Test unapproved resource generates info."""
        validator = ToolNameValidator()
        result = validator.validate("get_unknown")
        # Should still be valid but with info finding
        assert any(f.severity == ValidationSeverity.INFO for f in result.findings)

    def test_name_too_short(self):
        """Test name too short is rejected."""
        validator = ToolNameValidator()
        result = validator.validate("ab")
        assert result.is_valid is False
        assert result.score == 0.0

    def test_name_too_long(self):
        """Test name too long is rejected."""
        validator = ToolNameValidator()
        long_name = "a" * 65
        result = validator.validate(long_name)
        assert result.is_valid is False

    def test_invalid_pattern(self):
        """Test invalid pattern is rejected."""
        validator = ToolNameValidator()
        result = validator.validate("InvalidPattern")
        assert result.is_valid is False

    def test_details_include_segments(self):
        """Test validation result includes segment details."""
        validator = ToolNameValidator()
        result = validator.validate("get_player_profile")
        assert "segments" in result.details
        assert result.details["segments"] == ["get", "player", "profile"]
        assert result.details["action"] == "get"


class TestToolDescriptionValidator:
    """Tests for ToolDescriptionValidator."""

    @pytest.mark.parametrize(
        "description,expected_score_range",
        [
            (
                "Retrieves player profile data including preferences and progress.",
                (4.0, 5.0),
            ),
            (
                "Gets player profile data including therapeutic preferences, "
                "privacy settings, and progress tracking information.",
                (4.0, 5.0),
            ),
            ("Short desc", (1.0, 2.0)),  # Too short
            ("This is a thing that does stuff", (2.0, 3.5)),  # Vague (adjusted range)
            ("get player", (1.0, 2.0)),  # Too short, no verb
        ],
    )
    def test_description_scoring(self, description, expected_score_range):
        """Test description scoring with various inputs."""
        validator = ToolDescriptionValidator()
        result = validator.validate(description)
        min_score, max_score = expected_score_range
        assert min_score <= result.score <= max_score

    def test_minimum_length_enforced(self):
        """Test minimum length is enforced."""
        validator = ToolDescriptionValidator()
        result = validator.validate("Short")
        assert result.is_valid is False
        assert result.score == 1.0

    def test_maximum_length_enforced(self):
        """Test maximum length is enforced."""
        validator = ToolDescriptionValidator()
        long_desc = "a" * 2049
        result = validator.validate(long_desc)
        assert result.is_valid is False

    def test_ideal_length_range(self):
        """Test ideal length range."""
        validator = ToolDescriptionValidator()

        # Too short for ideal
        result = validator.validate("This is a short description.")
        assert any(
            f.severity == ValidationSeverity.WARNING for f in result.findings
        )

        # Ideal length
        result = validator.validate(
            "Retrieves comprehensive player profile data including "
            "therapeutic preferences, privacy settings, and progress tracking."
        )
        assert result.score >= 4.0

    def test_vague_terms_detected(self):
        """Test vague terms are detected."""
        validator = ToolDescriptionValidator()
        result = validator.validate(
            "This tool does various things and stuff with the player data etc."
        )
        assert any(
            "vague terms" in f.message.lower() for f in result.findings
        )
        assert result.score < 5.0

    def test_action_verb_check(self):
        """Test action verb check."""
        validator = ToolDescriptionValidator()

        # With action verb
        result = validator.validate(
            "Retrieves player profile data including preferences."
        )
        assert result.score >= 4.0

        # Without action verb
        result = validator.validate(
            "Player profile data including preferences and settings."
        )
        assert result.score < 5.0

    def test_details_include_length(self):
        """Test validation result includes length details."""
        validator = ToolDescriptionValidator()
        description = "Retrieves player profile data."
        result = validator.validate(description)
        assert "length" in result.details
        assert result.details["length"] == len(description)

    @pytest.mark.parametrize(
        "first_word,expected_in_action_verbs",
        [
            ("retrieves", True),
            ("gets", True),
            ("creates", True),
            ("updates", True),
            ("deletes", True),
            ("player", False),
            ("the", False),
        ],
    )
    def test_first_word_detection(self, first_word, expected_in_action_verbs):
        """Test first word detection."""
        validator = ToolDescriptionValidator()
        description = f"{first_word} player profile data and preferences."
        result = validator.validate(description)

        if expected_in_action_verbs:
            # Should have higher score
            assert result.score >= 4.0
        else:
            # Should have info finding about action verb
            assert any(
                "action verb" in f.message.lower() for f in result.findings
            )


class TestValidationIntegration:
    """Integration tests for validators."""

    def test_both_validators_on_good_tool(self):
        """Test both validators on a well-designed tool."""
        name_validator = ToolNameValidator()
        desc_validator = ToolDescriptionValidator()

        name_result = name_validator.validate("get_player_profile")
        desc_result = desc_validator.validate(
            "Retrieves comprehensive player profile data including "
            "therapeutic preferences, privacy settings, and progress tracking."
        )

        assert name_result.is_valid is True
        assert desc_result.is_valid is True
        assert name_result.score >= 0.9
        assert desc_result.score >= 4.0

    def test_both_validators_on_poor_tool(self):
        """Test both validators on a poorly-designed tool."""
        name_validator = ToolNameValidator()
        desc_validator = ToolDescriptionValidator()

        name_result = name_validator.validate("BadToolName")
        desc_result = desc_validator.validate("Does stuff")

        assert name_result.is_valid is False
        assert desc_result.is_valid is False

