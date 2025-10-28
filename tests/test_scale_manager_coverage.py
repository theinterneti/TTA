"""
Coverage tests for ScaleManager to reach 70%+ coverage.

This module contains tests specifically designed to cover previously
untested code paths in scale_manager.py.
"""

import pytest
from tta_narrative.orchestration.conflict_detection import (
    ScaleConflict,
)
from tta_narrative.orchestration.models import (
    NarrativeScale,
    PlayerChoice,
)
from tta_narrative.orchestration.resolution_engine import Resolution
from tta_narrative.orchestration.scale_manager import ScaleManager


class TestScaleManagerConflictResolution:
    """Tests for resolve_scale_conflicts method (lines 119-133)."""

    @pytest.mark.asyncio
    async def test_resolve_multiple_conflicts_sorted_by_priority(self, monkeypatch):
        """Test that conflicts are resolved in priority order."""
        sm = ScaleManager(config={})

        # Create conflicts with different priorities
        conflict1 = ScaleConflict(
            conflict_id="c1",
            involved_scales={NarrativeScale.SHORT_TERM},
            conflict_type="temporal",
            summary="Low priority conflict",
            resolution_priority=3,
            severity=0.5,
        )
        conflict2 = ScaleConflict(
            conflict_id="c2",
            involved_scales={NarrativeScale.MEDIUM_TERM},
            conflict_type="causal",
            summary="High priority conflict",
            resolution_priority=1,
            severity=0.8,
        )
        conflict3 = ScaleConflict(
            conflict_id="c3",
            involved_scales={NarrativeScale.LONG_TERM},
            conflict_type="thematic",
            summary="Medium priority conflict",
            resolution_priority=2,
            severity=0.6,
        )

        # Track resolution order
        resolution_order = []

        async def mock_generate_resolution(conflict):
            resolution_order.append(conflict.conflict_id)
            return Resolution(
                resolution_id=f"res_{conflict.conflict_id}",
                conflict_id=conflict.conflict_id,
                resolution_type="test_resolution",
                description="Test resolution for conflict",
                effectiveness_score=0.8,
            )

        async def mock_implement_resolution(resolution):
            pass

        monkeypatch.setattr(
            sm, "_generate_conflict_resolution", mock_generate_resolution
        )
        monkeypatch.setattr(sm, "_implement_resolution", mock_implement_resolution)

        # Resolve conflicts
        resolutions = await sm.resolve_scale_conflicts(
            [conflict1, conflict2, conflict3]
        )

        # Verify conflicts resolved in priority order (1, 2, 3)
        assert len(resolutions) == 3
        assert resolution_order == ["c2", "c3", "c1"]

    @pytest.mark.asyncio
    async def test_resolve_conflicts_with_exception_handling(self, monkeypatch):
        """Test that exceptions during resolution are handled gracefully."""
        sm = ScaleManager(config={})

        conflict = ScaleConflict(
            conflict_id="c1",
            involved_scales={NarrativeScale.SHORT_TERM},
            conflict_type="temporal",
            summary="Test conflict",
            resolution_priority=1,
            severity=0.5,
        )

        async def mock_generate_resolution_error(conflict):
            raise ValueError("Test error during resolution generation")

        monkeypatch.setattr(
            sm, "_generate_conflict_resolution", mock_generate_resolution_error
        )

        # Should return empty list on exception
        resolutions = await sm.resolve_scale_conflicts([conflict])
        assert resolutions == []

    @pytest.mark.asyncio
    async def test_resolve_conflicts_with_none_resolutions(self, monkeypatch):
        """Test handling when resolution generation returns None."""
        sm = ScaleManager(config={})

        conflict = ScaleConflict(
            conflict_id="c1",
            involved_scales={NarrativeScale.SHORT_TERM},
            conflict_type="temporal",
            summary="Test conflict",
            resolution_priority=1,
            severity=0.5,
        )

        async def mock_generate_none(conflict):
            return None

        async def mock_implement(resolution):
            pass

        monkeypatch.setattr(sm, "_generate_conflict_resolution", mock_generate_none)
        monkeypatch.setattr(sm, "_implement_resolution", mock_implement)

        resolutions = await sm.resolve_scale_conflicts([conflict])
        assert resolutions == []


class TestScaleManagerBaseMagnitude:
    """Tests for _calculate_base_magnitude method (lines 181-202)."""

    def test_base_magnitude_major_decision(self):
        """Test base magnitude for major_decision choice type."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Make a major decision",
            metadata={"choice_type": "major_decision"},
        )

        magnitude = sm._calculate_base_magnitude(choice, NarrativeScale.SHORT_TERM)
        # base=0.5, major_decision multiplier=1.5, SHORT_TERM multiplier=0.8
        # 0.5 * 1.5 * 0.8 = 0.6
        assert magnitude == pytest.approx(0.6, abs=0.01)

    def test_base_magnitude_character_interaction(self):
        """Test base magnitude for character_interaction choice type."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Interact with character",
            metadata={"choice_type": "character_interaction"},
        )

        magnitude = sm._calculate_base_magnitude(choice, NarrativeScale.MEDIUM_TERM)
        # base=0.5, character_interaction multiplier=1.2, MEDIUM_TERM multiplier=0.5
        # 0.5 * 1.2 * 0.5 = 0.3
        assert magnitude == pytest.approx(0.3, abs=0.01)

    def test_base_magnitude_world_action(self):
        """Test base magnitude for world_action choice type."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Perform world action",
            metadata={"choice_type": "world_action"},
        )

        magnitude = sm._calculate_base_magnitude(choice, NarrativeScale.LONG_TERM)
        # base=0.5, world_action multiplier=1.3, LONG_TERM multiplier=0.3
        # 0.5 * 1.3 * 0.3 = 0.195
        assert magnitude == pytest.approx(0.195, abs=0.01)

    def test_base_magnitude_dialogue_default(self):
        """Test base magnitude for dialogue (default) choice type."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Say something",
            metadata={"choice_type": "dialogue"},
        )

        magnitude = sm._calculate_base_magnitude(choice, NarrativeScale.EPIC_TERM)
        # base=0.5, dialogue multiplier=1.0, EPIC_TERM multiplier=0.1
        # 0.5 * 1.0 * 0.1 = 0.05
        assert magnitude == pytest.approx(0.05, abs=0.01)

    def test_base_magnitude_none_metadata(self):
        """Test base magnitude when metadata is None."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata=None,
        )

        magnitude = sm._calculate_base_magnitude(choice, NarrativeScale.SHORT_TERM)
        # Should use default "dialogue" choice_type
        # base=0.5, dialogue multiplier=1.0, SHORT_TERM multiplier=0.8
        # 0.5 * 1.0 * 0.8 = 0.4
        assert magnitude == pytest.approx(0.4, abs=0.01)

    def test_base_magnitude_all_scales(self):
        """Test base magnitude for all narrative scales."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={},
        )

        # Test all scales
        short_term = sm._calculate_base_magnitude(choice, NarrativeScale.SHORT_TERM)
        medium_term = sm._calculate_base_magnitude(choice, NarrativeScale.MEDIUM_TERM)
        long_term = sm._calculate_base_magnitude(choice, NarrativeScale.LONG_TERM)
        epic_term = sm._calculate_base_magnitude(choice, NarrativeScale.EPIC_TERM)

        # Verify scale multipliers applied correctly
        assert short_term == pytest.approx(0.4, abs=0.01)  # 0.5 * 0.8
        assert medium_term == pytest.approx(0.25, abs=0.01)  # 0.5 * 0.5
        assert long_term == pytest.approx(0.15, abs=0.01)  # 0.5 * 0.3
        assert epic_term == pytest.approx(0.05, abs=0.01)  # 0.5 * 0.1


class TestScaleManagerAffectedElements:
    """Tests for _identify_affected_elements method (lines 204-224)."""

    @pytest.mark.asyncio
    async def test_affected_elements_short_term(self):
        """Test affected elements for SHORT_TERM scale."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1", session_id="s1", choice_text="Test", metadata={}
        )

        elements = await sm._identify_affected_elements(
            choice, NarrativeScale.SHORT_TERM
        )
        assert "current_scene" in elements
        assert "immediate_dialogue" in elements
        assert "character_mood" in elements

    @pytest.mark.asyncio
    async def test_affected_elements_medium_term(self):
        """Test affected elements for MEDIUM_TERM scale."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1", session_id="s1", choice_text="Test", metadata={}
        )

        elements = await sm._identify_affected_elements(
            choice, NarrativeScale.MEDIUM_TERM
        )
        assert "character_relationships" in elements
        assert "personal_growth" in elements
        assert "skill_development" in elements

    @pytest.mark.asyncio
    async def test_affected_elements_long_term(self):
        """Test affected elements for LONG_TERM scale."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1", session_id="s1", choice_text="Test", metadata={}
        )

        elements = await sm._identify_affected_elements(
            choice, NarrativeScale.LONG_TERM
        )
        assert "world_state" in elements
        assert "faction_relationships" in elements
        assert "major_plot_threads" in elements

    @pytest.mark.asyncio
    async def test_affected_elements_epic_term(self):
        """Test affected elements for EPIC_TERM scale."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1", session_id="s1", choice_text="Test", metadata={}
        )

        elements = await sm._identify_affected_elements(
            choice, NarrativeScale.EPIC_TERM
        )
        assert "generational_legacy" in elements
        assert "world_history" in elements
        assert "cultural_impact" in elements

    @pytest.mark.asyncio
    async def test_affected_elements_with_character_name(self):
        """Test affected elements with character_name in metadata."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"character_name": "Alice"},
        )

        elements = await sm._identify_affected_elements(
            choice, NarrativeScale.SHORT_TERM
        )
        assert "character_Alice" in elements

    @pytest.mark.asyncio
    async def test_affected_elements_with_location(self):
        """Test affected elements with location in metadata."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"location": "Forest"},
        )

        elements = await sm._identify_affected_elements(
            choice, NarrativeScale.SHORT_TERM
        )
        assert "location_Forest" in elements

    @pytest.mark.asyncio
    async def test_affected_elements_with_both_character_and_location(self):
        """Test affected elements with both character_name and location."""
        sm = ScaleManager(config={})
        choice = PlayerChoice(
            choice_id="c1",
            session_id="s1",
            choice_text="Test",
            metadata={"character_name": "Bob", "location": "Castle"},
        )

        elements = await sm._identify_affected_elements(
            choice, NarrativeScale.MEDIUM_TERM
        )
        assert "character_Bob" in elements
        assert "location_Castle" in elements


class TestScaleManagerTemporalDecay:
    """Tests for _calculate_temporal_decay method (lines 245-252)."""

    def test_temporal_decay_short_term(self):
        """Test temporal decay for SHORT_TERM scale."""
        sm = ScaleManager(config={})
        decay = sm._calculate_temporal_decay(NarrativeScale.SHORT_TERM)
        assert decay == pytest.approx(0.7, abs=0.01)

    def test_temporal_decay_medium_term(self):
        """Test temporal decay for MEDIUM_TERM scale."""
        sm = ScaleManager(config={})
        decay = sm._calculate_temporal_decay(NarrativeScale.MEDIUM_TERM)
        assert decay == pytest.approx(0.85, abs=0.01)

    def test_temporal_decay_long_term(self):
        """Test temporal decay for LONG_TERM scale."""
        sm = ScaleManager(config={})
        decay = sm._calculate_temporal_decay(NarrativeScale.LONG_TERM)
        assert decay == pytest.approx(0.95, abs=0.01)

    def test_temporal_decay_epic_term(self):
        """Test temporal decay for EPIC_TERM scale."""
        sm = ScaleManager(config={})
        decay = sm._calculate_temporal_decay(NarrativeScale.EPIC_TERM)
        assert decay == pytest.approx(0.99, abs=0.01)
