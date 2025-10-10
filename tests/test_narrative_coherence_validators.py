"""
Tests for Narrative Coherence validators.

This module tests the coherence validation, contradiction detection,
and causal validation components of the Narrative Coherence system.

Phase 1: CoherenceValidator tests (15 tests targeting 55-60% coverage)
"""

import uuid
from datetime import datetime

import pytest

from src.components.narrative_coherence.coherence_validator import CoherenceValidator
from src.components.narrative_coherence.models import (
    ConsistencyIssue,
    ConsistencyIssueType,
    LoreEntry,
    NarrativeContent,
    ValidationSeverity,
)


class TestCoherenceValidator:
    """Tests for CoherenceValidator - Phase 1 (15 tests)."""

    # ========== Group 1: Initialization Tests (2 tests) ==========

    def test_initialization_default_config(self):
        """Test validator initializes with default configuration."""
        config = {}
        validator = CoherenceValidator(config)

        assert validator is not None
        assert validator.config == config
        assert validator.lore_database == {}
        assert validator.character_profiles == {}
        assert validator.world_rules == {}
        assert validator.therapeutic_guidelines == {}
        # Default thresholds
        assert validator.consistency_threshold == 0.7
        assert validator.lore_compliance_threshold == 0.8
        assert validator.character_consistency_threshold == 0.75

    def test_initialization_custom_config(self):
        """Test validator initializes with custom configuration."""
        config = {
            "consistency_threshold": 0.85,
            "lore_compliance_threshold": 0.9,
            "character_consistency_threshold": 0.8,
        }
        validator = CoherenceValidator(config)

        assert validator.config == config
        assert validator.consistency_threshold == 0.85
        assert validator.lore_compliance_threshold == 0.9
        assert validator.character_consistency_threshold == 0.8

    # ========== Group 2: Core Validation Tests (5 tests) ==========

    @pytest.mark.asyncio
    async def test_validate_narrative_consistency_valid_narrative(self):
        """Test coherence validation with valid narrative."""
        config = {}
        validator = CoherenceValidator(config)

        content = NarrativeContent(
            content_id="test_001",
            content_type="dialogue",
            text="The hero walked through the peaceful garden.",
            related_characters=["hero"],
            related_locations=["garden"],
            themes=["peace"],
        )

        result = await validator.validate_narrative_consistency(content)

        assert result is not None
        assert result.is_valid is True
        assert result.consistency_score >= 0.7
        assert result.lore_compliance >= 0.0
        assert result.character_consistency >= 0.0
        assert result.therapeutic_alignment >= 0.0
        assert isinstance(result.detected_issues, list)
        assert isinstance(result.suggested_corrections, list)
        assert isinstance(result.validation_timestamp, datetime)

    @pytest.mark.asyncio
    async def test_validate_narrative_consistency_with_lore_violations(self):
        """Test coherence validation with lore violations."""
        config = {}
        validator = CoherenceValidator(config)

        # Add lore entry with constraints
        lore_entry = LoreEntry(
            lore_id="char_hero_001",
            category="character",
            title="Hero Background",
            description="The hero is a peaceful warrior",
            constraints=["must not violence", "must have peace"],
        )
        validator.lore_database["character_hero"] = lore_entry

        # Content that violates lore
        content = NarrativeContent(
            content_id="test_002",
            content_type="action",
            text="The hero engaged in violence and chaos.",
            related_characters=["hero"],
            related_locations=["battlefield"],
            themes=["war"],
        )

        result = await validator.validate_narrative_consistency(content)

        assert result is not None
        assert len(result.detected_issues) > 0
        # Should have lore violation issues
        lore_issues = [
            i
            for i in result.detected_issues
            if i.issue_type == ConsistencyIssueType.LORE_VIOLATION
        ]
        assert len(lore_issues) > 0
        assert result.lore_compliance < 1.0

    @pytest.mark.asyncio
    async def test_validate_narrative_consistency_missing_character(self):
        """Test validation with missing character profile."""
        config = {}
        validator = CoherenceValidator(config)

        content = NarrativeContent(
            content_id="test_003",
            content_type="dialogue",
            text="The unknown character speaks.",
            related_characters=["unknown_character"],
            related_locations=[],
            themes=[],
        )

        result = await validator.validate_narrative_consistency(content)

        assert result is not None
        # Should have character inconsistency warning
        char_issues = [
            i
            for i in result.detected_issues
            if i.issue_type == ConsistencyIssueType.CHARACTER_INCONSISTENCY
        ]
        assert len(char_issues) > 0
        assert char_issues[0].severity == ValidationSeverity.WARNING
        assert "not found" in char_issues[0].description.lower()

    @pytest.mark.asyncio
    async def test_validate_narrative_consistency_with_contradictory_elements(self):
        """Test validation with contradictory elements."""
        config = {"consistency_threshold": 0.9}
        validator = CoherenceValidator(config)

        # Add conflicting lore
        lore1 = LoreEntry(
            lore_id="loc_garden_001",
            category="location",
            title="Garden",
            description="A peaceful place",
            constraints=["must have tranquility"],
        )
        validator.lore_database["location_garden"] = lore1

        content = NarrativeContent(
            content_id="test_004",
            content_type="scene",
            text="The garden was filled with chaos and noise.",
            related_characters=[],
            related_locations=["garden"],
            themes=["chaos"],
        )

        result = await validator.validate_narrative_consistency(content)

        assert result is not None
        # High threshold should make it invalid
        assert result.consistency_score < 0.9 or len(result.detected_issues) > 0

    @pytest.mark.asyncio
    async def test_validate_narrative_consistency_edge_cases(self):
        """Test validation with edge cases (empty content, special characters)."""
        config = {}
        validator = CoherenceValidator(config)

        # Empty text
        content = NarrativeContent(
            content_id="test_005",
            content_type="empty",
            text="",
            related_characters=[],
            related_locations=[],
            themes=[],
        )

        result = await validator.validate_narrative_consistency(content)

        assert result is not None
        assert result.is_valid is True  # Empty content should be valid
        assert result.consistency_score >= 0.0

    # ========== Group 3: Coherence Checking Tests (4 tests) ==========

    @pytest.mark.asyncio
    async def test_lore_compliance_checking(self):
        """Test lore compliance checking algorithms."""
        config = {}
        validator = CoherenceValidator(config)

        # Add multiple lore entries
        validator.lore_database["character_alice"] = LoreEntry(
            lore_id="char_alice_001",
            category="character",
            title="Alice",
            description="A brave knight",
            constraints=["must have courage"],
        )

        content = NarrativeContent(
            content_id="test_006",
            content_type="action",
            text="Alice showed great courage in battle.",
            related_characters=["alice"],
            related_locations=[],
            themes=["bravery"],
        )

        issues = await validator._validate_lore_compliance(content)

        assert isinstance(issues, list)
        # Should have no issues since content matches lore
        assert len(issues) == 0

    @pytest.mark.asyncio
    async def test_threshold_based_validation(self):
        """Test threshold-based validation logic."""
        # Test with different thresholds
        configs = [
            {"consistency_threshold": 0.5},
            {"consistency_threshold": 0.7},
            {"consistency_threshold": 0.9},
        ]

        for config in configs:
            validator = CoherenceValidator(config)
            content = NarrativeContent(
                content_id=f"test_{uuid.uuid4()}",
                content_type="test",
                text="Test content",
                related_characters=[],
                related_locations=[],
                themes=[],
            )

            result = await validator.validate_narrative_consistency(content)

            # Validation should respect threshold
            if result.consistency_score >= config["consistency_threshold"]:
                assert result.is_valid is True
            else:
                assert result.is_valid is False

    @pytest.mark.asyncio
    async def test_multi_level_coherence_checks(self):
        """Test multi-level coherence checks (lore, character, world, therapeutic)."""
        config = {}
        validator = CoherenceValidator(config)

        # Add data for multi-level validation
        validator.lore_database["character_bob"] = LoreEntry(
            lore_id="char_bob_001",
            category="character",
            title="Bob",
            description="A wise wizard",
            constraints=["must have wisdom"],
        )
        validator.character_profiles["bob"] = {
            "name": "Bob",
            "personality": "wise",
            "traits": ["intelligent", "patient"],
        }

        content = NarrativeContent(
            content_id="test_007",
            content_type="dialogue",
            text="Bob spoke with wisdom and patience.",
            related_characters=["bob"],
            related_locations=["tower"],
            themes=["wisdom"],
        )

        result = await validator.validate_narrative_consistency(content)

        # Should validate across all levels
        assert result.lore_compliance >= 0.0
        assert result.character_consistency >= 0.0
        assert result.therapeutic_alignment >= 0.0
        assert result.consistency_score >= 0.0

    @pytest.mark.asyncio
    async def test_coherence_scoring_calculation(self):
        """Test coherence scoring calculation."""
        config = {}
        validator = CoherenceValidator(config)

        content = NarrativeContent(
            content_id="test_008",
            content_type="test",
            text="Test content for scoring",
            related_characters=[],
            related_locations=[],
            themes=[],
        )

        result = await validator.validate_narrative_consistency(content)

        # Score should be between 0 and 1
        assert 0.0 <= result.consistency_score <= 1.0
        assert 0.0 <= result.lore_compliance <= 1.0
        assert 0.0 <= result.character_consistency <= 1.0
        assert 0.0 <= result.therapeutic_alignment <= 1.0

    # ========== Group 4: Error Handling Tests (2 tests) ==========

    @pytest.mark.asyncio
    async def test_error_handling_invalid_input(self):
        """Test error handling for invalid input."""
        config = {}
        validator = CoherenceValidator(config)

        # Create content that might cause issues
        content = NarrativeContent(
            content_id="test_009",
            content_type="test",
            text="Test" * 10000,  # Very long text
            related_characters=["char" + str(i) for i in range(100)],  # Many characters
            related_locations=[],
            themes=[],
        )

        # Should handle gracefully without crashing
        result = await validator.validate_narrative_consistency(content)

        assert result is not None
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.consistency_score, float)

    @pytest.mark.asyncio
    async def test_error_handling_validation_failures(self):
        """Test error handling for validation failures."""
        config = {}
        validator = CoherenceValidator(config)

        # Add lore with problematic constraints
        validator.lore_database["character_error"] = LoreEntry(
            lore_id="char_error_001",
            category="character",
            title="Error Character",
            description="Test error handling",
            constraints=["must not error", "must have success"],
        )

        content = NarrativeContent(
            content_id="test_010",
            content_type="test",
            text="This content contains error but also success.",
            related_characters=["error"],
            related_locations=[],
            themes=[],
        )

        result = await validator.validate_narrative_consistency(content)

        # Should handle validation and return result
        assert result is not None
        assert isinstance(result.detected_issues, list)

    # ========== Group 5: Helper Method Tests (2 tests) ==========

    def test_lore_lookup_helpers(self):
        """Test helper methods for lore lookups."""
        config = {}
        validator = CoherenceValidator(config)

        # Add lore entries
        char_lore = LoreEntry(
            lore_id="char_test_001",
            category="character",
            title="Test Character",
            description="Test",
            constraints=[],
        )
        loc_lore = LoreEntry(
            lore_id="loc_test_001",
            category="location",
            title="Test Location",
            description="Test",
            constraints=[],
        )
        theme_lore = LoreEntry(
            lore_id="theme_test_001",
            category="theme",
            title="Test Theme",
            description="Test",
            constraints=[],
        )

        validator.lore_database["character_hero"] = char_lore
        validator.lore_database["location_castle"] = loc_lore
        validator.lore_database["theme_adventure"] = theme_lore

        # Test lookups
        assert validator._get_character_lore("hero") == char_lore
        assert validator._get_location_lore("castle") == loc_lore
        assert validator._get_theme_lore("adventure") == theme_lore
        assert validator._get_character_lore("nonexistent") is None

    @pytest.mark.asyncio
    async def test_scoring_calculation_helpers(self):
        """Test utility functions for score calculations."""
        config = {}
        validator = CoherenceValidator(config)

        # Test with no issues
        issues_empty = []
        score = validator._calculate_lore_compliance_score(issues_empty)
        assert score == 1.0

        # Test with issues
        issues = [
            ConsistencyIssue(
                issue_id=str(uuid.uuid4()),
                issue_type=ConsistencyIssueType.LORE_VIOLATION,
                severity=ValidationSeverity.WARNING,
                description="Test issue 1",
                confidence_score=0.8,
            ),
            ConsistencyIssue(
                issue_id=str(uuid.uuid4()),
                issue_type=ConsistencyIssueType.LORE_VIOLATION,
                severity=ValidationSeverity.ERROR,
                description="Test issue 2",
                confidence_score=0.9,
            ),
        ]

        lore_score = validator._calculate_lore_compliance_score(issues)
        char_score = validator._calculate_character_consistency_score(issues)
        therapeutic_score = validator._calculate_therapeutic_alignment_score(issues)

        # Scores should be between 0 and 1
        assert 0.0 <= lore_score <= 1.0
        assert 0.0 <= char_score <= 1.0
        assert 0.0 <= therapeutic_score <= 1.0

        # Scores should be less than 1.0 when there are issues
        assert lore_score < 1.0
        assert char_score < 1.0
        assert therapeutic_score < 1.0
