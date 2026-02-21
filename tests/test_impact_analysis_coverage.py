"""

# Logseq: [[TTA.dev/Tests/Test_impact_analysis_coverage]]
Coverage tests for impact_analysis module to reach 70%+ coverage.

This module contains tests specifically designed to cover previously
untested code paths in impact_analysis.py, particularly null checks
and edge cases.
"""

import pytest
from tta_narrative.orchestration.impact_analysis import (
    assess_therapeutic_alignment,
    calculate_base_magnitude,
    calculate_causal_strength,
    calculate_confidence_score,
    identify_affected_elements,
)
from tta_narrative.orchestration.models import (
    NarrativeScale,
    PlayerChoice,
)


class TestImpactAnalysisNullChecks:
    """Tests for null checks and edge cases in impact_analysis functions."""

    def test_calculate_base_magnitude_none_metadata(self):
        """Test calculate_base_magnitude with None metadata."""
        choice = PlayerChoice(
            choice_id="c1", session_id="s1", choice_text="Test", metadata=None
        )

        magnitude = calculate_base_magnitude(choice, NarrativeScale.SHORT_TERM)

        # Should use default "dialogue" choice_type
        assert magnitude > 0
        assert magnitude <= 1.0

    def test_calculate_base_magnitude_major_decision(self):
        """Test calculate_base_magnitude with major_decision choice type."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"choice_type": "major_decision"},
        )

        magnitude = calculate_base_magnitude(choice, NarrativeScale.SHORT_TERM)

        # major_decision should have higher magnitude
        assert magnitude == pytest.approx(0.6, abs=0.01)

    def test_calculate_base_magnitude_character_interaction(self):
        """Test calculate_base_magnitude with character_interaction."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"choice_type": "character_interaction"},
        )

        magnitude = calculate_base_magnitude(choice, NarrativeScale.MEDIUM_TERM)

        assert magnitude == pytest.approx(0.3, abs=0.01)

    def test_calculate_base_magnitude_world_action(self):
        """Test calculate_base_magnitude with world_action."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"choice_type": "world_action"},
        )

        magnitude = calculate_base_magnitude(choice, NarrativeScale.LONG_TERM)

        assert magnitude == pytest.approx(0.195, abs=0.01)

    def test_identify_affected_elements_with_character_name(self):
        """Test identify_affected_elements with character_name metadata."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"character_name": "Alice"},
        )

        elements = identify_affected_elements(choice, NarrativeScale.SHORT_TERM)

        assert "character_Alice" in elements
        assert "current_scene" in elements

    def test_identify_affected_elements_with_location(self):
        """Test identify_affected_elements with location metadata."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"location": "Forest"},
        )

        elements = identify_affected_elements(choice, NarrativeScale.MEDIUM_TERM)

        assert "location_Forest" in elements
        assert "character_relationships" in elements

    def test_identify_affected_elements_none_metadata(self):
        """Test identify_affected_elements with None metadata."""
        choice = PlayerChoice(
            choice_id="c1", session_id="s1", choice_text="Test", metadata=None
        )

        elements = identify_affected_elements(choice, NarrativeScale.SHORT_TERM)

        # Should still return scale-specific elements
        assert "current_scene" in elements
        assert len(elements) > 0

    def test_calculate_causal_strength_with_consequences(self):
        """Test calculate_causal_strength with consequences metadata."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"consequences": "high"},
        )

        strength = calculate_causal_strength(choice, NarrativeScale.SHORT_TERM)

        # consequences should increase strength
        assert strength > 0.5

    def test_calculate_causal_strength_with_risk_level(self):
        """Test calculate_causal_strength with risk_level metadata."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"risk_level": 0.8},
        )

        strength = calculate_causal_strength(choice, NarrativeScale.MEDIUM_TERM)

        # risk_level should affect strength
        assert strength > 0
        assert strength <= 1.0

    def test_calculate_causal_strength_none_metadata(self):
        """Test calculate_causal_strength with None metadata."""
        choice = PlayerChoice(
            choice_id="c1", session_id="s1", choice_text="Test", metadata=None
        )

        strength = calculate_causal_strength(choice, NarrativeScale.SHORT_TERM)

        # Should return base strength
        assert strength > 0
        assert strength <= 1.0

    def test_assess_therapeutic_alignment_empathy_theme(self):
        """Test assess_therapeutic_alignment with empathy theme."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"therapeutic_theme": "empathy"},
        )

        alignment = assess_therapeutic_alignment(choice, NarrativeScale.MEDIUM_TERM)

        # empathy should increase alignment
        assert alignment > 0.5

    def test_assess_therapeutic_alignment_growth_theme(self):
        """Test assess_therapeutic_alignment with growth theme."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"therapeutic_theme": "growth"},
        )

        alignment = assess_therapeutic_alignment(choice, NarrativeScale.LONG_TERM)

        # growth should increase alignment
        assert alignment > 0.5

    def test_assess_therapeutic_alignment_healing_theme(self):
        """Test assess_therapeutic_alignment with healing theme."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"therapeutic_theme": "healing"},
        )

        alignment = assess_therapeutic_alignment(choice, NarrativeScale.MEDIUM_TERM)

        # healing should increase alignment
        assert alignment > 0.5

    def test_assess_therapeutic_alignment_harm_theme(self):
        """Test assess_therapeutic_alignment with harm theme."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"therapeutic_theme": "harm"},
        )

        alignment = assess_therapeutic_alignment(choice, NarrativeScale.SHORT_TERM)

        # harm should decrease alignment
        assert alignment < 0.5

    def test_assess_therapeutic_alignment_trauma_theme(self):
        """Test assess_therapeutic_alignment with trauma theme."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"therapeutic_theme": "trauma"},
        )

        alignment = assess_therapeutic_alignment(choice, NarrativeScale.SHORT_TERM)

        # trauma should decrease alignment
        assert alignment < 0.5

    def test_assess_therapeutic_alignment_medium_long_term_scales(self):
        """Test assess_therapeutic_alignment for MEDIUM/LONG_TERM scales."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"therapeutic_theme": "self_reflection"},
        )

        medium_alignment = assess_therapeutic_alignment(
            choice, NarrativeScale.MEDIUM_TERM
        )
        long_alignment = assess_therapeutic_alignment(choice, NarrativeScale.LONG_TERM)

        # MEDIUM and LONG_TERM should have higher alignment
        assert medium_alignment > 0.5
        assert long_alignment > 0.5

    def test_assess_therapeutic_alignment_none_metadata(self):
        """Test assess_therapeutic_alignment with None metadata."""
        choice = PlayerChoice(
            choice_id="c1", session_id="s1", choice_text="Test", metadata=None
        )

        alignment = assess_therapeutic_alignment(choice, NarrativeScale.SHORT_TERM)

        # Should return base alignment
        assert alignment > 0
        assert alignment <= 1.0

    def test_calculate_confidence_score_with_evidence(self):
        """Test calculate_confidence_score with evidence metadata."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"evidence": "strong"},
        )

        confidence = calculate_confidence_score(choice, NarrativeScale.SHORT_TERM)

        # evidence should increase confidence
        assert confidence > 0.5

    def test_calculate_confidence_score_with_ambiguity(self):
        """Test calculate_confidence_score with ambiguity metadata."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"ambiguity": 0.5},
        )

        confidence = calculate_confidence_score(choice, NarrativeScale.SHORT_TERM)

        # ambiguity should decrease confidence
        assert confidence < 0.5

    def test_calculate_confidence_score_high_ambiguity(self):
        """Test calculate_confidence_score with high ambiguity."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"ambiguity": 0.9},
        )

        confidence = calculate_confidence_score(choice, NarrativeScale.SHORT_TERM)

        # high ambiguity should significantly decrease confidence
        assert confidence < 0.3

    def test_calculate_confidence_score_none_metadata(self):
        """Test calculate_confidence_score with None metadata."""
        choice = PlayerChoice(
            choice_id="c1", session_id="s1", choice_text="Test", metadata=None
        )

        confidence = calculate_confidence_score(choice, NarrativeScale.SHORT_TERM)

        # Should return base confidence
        assert confidence > 0
        assert confidence <= 1.0

    def test_calculate_confidence_score_with_both_evidence_and_ambiguity(self):
        """Test calculate_confidence_score with both evidence and ambiguity."""
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"evidence": "strong", "ambiguity": 0.3},
        )

        confidence = calculate_confidence_score(choice, NarrativeScale.SHORT_TERM)

        # Both factors should affect confidence
        assert confidence > 0
        assert confidence <= 1.0
