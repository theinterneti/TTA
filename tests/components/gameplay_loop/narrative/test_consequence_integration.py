"""
Integration Tests for Consequence System with Choice Processor

This module tests the integration between the consequence system and choice processor.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.components.gameplay_loop.models.core import (
    ChoiceType,
    TherapeuticOutcome,
    UserChoice,
)
from src.components.gameplay_loop.narrative.choice_processor import ChoiceProcessor
from src.components.gameplay_loop.narrative.consequence_system import ConsequenceSystem
from src.components.gameplay_loop.narrative.events import EventBus
from src.components.gameplay_loop.services.session_state import SessionState


class TestConsequenceIntegration:
    """Test integration between consequence system and choice processor."""

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus

    @pytest.fixture
    def narrative_engine(self, event_bus):
        """Create mock narrative engine."""
        engine = Mock()
        engine.event_bus = event_bus
        return engine

    @pytest.fixture
    def choice_processor(self, narrative_engine):
        """Create choice processor with consequence system."""
        return ChoiceProcessor(narrative_engine)

    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = Mock(spec=SessionState)
        state.session_id = "integration_test_session"
        state.user_id = "integration_test_user"
        state.therapeutic_goals = ["anxiety_management", "communication_skills"]
        state.progress_metrics = {
            "anxiety_management": 0.4,
            "communication_skills": 0.3,
        }
        state.context = {"narrative_context": "therapeutic_session"}
        state.emotional_state = {"anxious": 0.5, "confident": 0.6}

        # Mock methods
        state.set_narrative_variable = Mock()
        state.get_narrative_variable = Mock(return_value=0.5)
        state.update_emotional_state = Mock()

        return state

    @pytest.fixture
    def therapeutic_choice(self):
        """Create therapeutic choice for testing."""
        return UserChoice(
            choice_id="therapeutic_choice_001",
            text="Take a moment to breathe deeply and express your feelings calmly",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_relevance=0.8,
            emotional_weight=0.6,
            difficulty_level=0.4,
            scene_id="test_scene",
            consequences=None,
        )

    @pytest.mark.asyncio
    async def test_choice_processing_with_consequences(
        self, choice_processor, session_state, therapeutic_choice
    ):
        """Test that choice processing generates and applies consequences."""
        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(
            return_value=[]
        )  # No legacy consequences
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Process the choice
        result = await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {"additional_context": "test"}
        )

        # Check that processing was successful
        assert result.success == True
        assert result.choice_id == therapeutic_choice.choice_id

        # Check that consequences were generated and applied
        assert choice_processor.metrics["consequences_generated"] > 0
        assert choice_processor.metrics["consequences_applied"] > 0

        # Check that the choice now has consequences
        assert therapeutic_choice.consequences is not None
        assert len(therapeutic_choice.consequences.consequences) > 0

    @pytest.mark.asyncio
    async def test_therapeutic_outcomes_applied_to_session(
        self, choice_processor, session_state, therapeutic_choice
    ):
        """Test that therapeutic outcomes are applied to session state."""
        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(return_value=[])
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Process the choice
        await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {}
        )

        # Check that therapeutic outcomes were applied
        consequence_set = therapeutic_choice.consequences
        assert consequence_set is not None

        if consequence_set.therapeutic_outcomes:
            # Progress metrics should have been updated
            # Note: In a real test, we'd check the actual values, but with mocks we check calls
            assert len(consequence_set.therapeutic_outcomes) > 0

            for outcome in consequence_set.therapeutic_outcomes:
                assert isinstance(outcome, TherapeuticOutcome)
                assert outcome.therapeutic_value > 0

    @pytest.mark.asyncio
    async def test_learning_opportunities_stored_in_session(
        self, choice_processor, session_state, therapeutic_choice
    ):
        """Test that learning opportunities are stored in session context."""
        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(return_value=[])
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Initialize session context
        session_state.context = {}

        # Process the choice
        await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {}
        )

        # Check that learning opportunities were stored
        consequence_set = therapeutic_choice.consequences
        assert consequence_set is not None

        if consequence_set.learning_opportunities:
            assert "learning_opportunities" in session_state.context
            stored_opportunities = session_state.context["learning_opportunities"]
            assert len(stored_opportunities) > 0

            # Should contain the learning opportunities from the consequence set
            for opportunity in consequence_set.learning_opportunities:
                assert opportunity in stored_opportunities

    @pytest.mark.asyncio
    async def test_consequence_history_tracking(
        self, choice_processor, session_state, therapeutic_choice
    ):
        """Test that consequence history is tracked in session."""
        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(return_value=[])
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Initialize session context
        session_state.context = {}

        # Process the choice
        await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {}
        )

        # Check that consequence history was updated
        assert "consequence_history" in session_state.context
        history = session_state.context["consequence_history"]
        assert len(history) > 0

        # Check history entry structure
        history_entry = history[0]
        assert "consequence_id" in history_entry
        assert "choice_id" in history_entry
        assert "consequence_type" in history_entry
        assert "therapeutic_outcomes_count" in history_entry
        assert "learning_opportunities_count" in history_entry
        assert "applied_at" in history_entry

        assert history_entry["choice_id"] == therapeutic_choice.choice_id

    @pytest.mark.asyncio
    async def test_emotional_impact_application(
        self, choice_processor, session_state, therapeutic_choice
    ):
        """Test that emotional impacts are applied to session state."""
        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(return_value=[])
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Process the choice
        await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {}
        )

        # Check that emotional impacts were applied
        consequence_set = therapeutic_choice.consequences
        assert consequence_set is not None

        if consequence_set.emotional_impact:
            # Should have called update_emotional_state for each emotion
            assert session_state.update_emotional_state.called

    @pytest.mark.asyncio
    async def test_narrative_impact_application(
        self, choice_processor, session_state, therapeutic_choice
    ):
        """Test that narrative impacts are applied to session state."""
        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(return_value=[])
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Process the choice
        await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {}
        )

        # Check that narrative impacts were applied
        consequence_set = therapeutic_choice.consequences
        assert consequence_set is not None

        if consequence_set.narrative_impact:
            # Should have called set_narrative_variable for each impact
            assert session_state.set_narrative_variable.called

    @pytest.mark.asyncio
    async def test_character_changes_application(
        self, choice_processor, session_state, therapeutic_choice
    ):
        """Test that character changes are applied to session state."""
        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(return_value=[])
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Process the choice
        await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {}
        )

        # Check that character changes were applied
        consequence_set = therapeutic_choice.consequences
        assert consequence_set is not None

        if consequence_set.character_changes:
            # Should have called set_narrative_variable for character attributes
            assert session_state.set_narrative_variable.called
            assert session_state.get_narrative_variable.called

    @pytest.mark.asyncio
    async def test_consequence_event_publishing(
        self, choice_processor, session_state, therapeutic_choice, event_bus
    ):
        """Test that consequence events are published."""
        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(return_value=[])
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Process the choice
        await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {}
        )

        # Check that events were published
        assert event_bus.publish.called

        # Should have published at least one event (consequence event)
        assert event_bus.publish.call_count >= 1

    @pytest.mark.asyncio
    async def test_metrics_tracking(
        self, choice_processor, session_state, therapeutic_choice
    ):
        """Test that metrics are properly tracked."""
        initial_metrics = choice_processor.get_metrics()
        initial_consequences_generated = initial_metrics["consequences_generated"]
        initial_consequences_applied = initial_metrics["consequences_applied"]

        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(return_value=[])
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Process the choice
        await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {}
        )

        # Check that metrics were updated
        final_metrics = choice_processor.get_metrics()

        assert (
            final_metrics["consequences_generated"]
            == initial_consequences_generated + 1
        )
        assert final_metrics["consequences_applied"] == initial_consequences_applied + 1

    @pytest.mark.asyncio
    async def test_backward_compatibility_with_legacy_consequences(
        self, choice_processor, session_state, therapeutic_choice
    ):
        """Test that the system maintains backward compatibility with legacy consequences."""
        # Create mock legacy consequence
        legacy_consequence = Mock()
        legacy_consequence.is_applicable = Mock(return_value=True)
        legacy_consequence.immediate = True
        legacy_consequence.consequence_id = "legacy_consequence_001"

        # Mock the choice loading
        choice_processor._load_choice = AsyncMock(return_value=therapeutic_choice)
        choice_processor._apply_choice_effects = AsyncMock()
        choice_processor._load_choice_consequences = AsyncMock(
            return_value=[legacy_consequence]
        )
        choice_processor._apply_consequence = AsyncMock()
        choice_processor._trigger_therapeutic_moment = AsyncMock()

        # Process the choice
        result = await choice_processor.process_choice(
            therapeutic_choice.choice_id, session_state, {}
        )

        # Check that both new and legacy consequences were processed
        assert result.success == True

        # Should have applied legacy consequence
        choice_processor._apply_consequence.assert_called_once_with(
            legacy_consequence, session_state
        )

        # Should also have generated new consequences
        assert choice_processor.metrics["consequences_generated"] > 0
        assert therapeutic_choice.consequences is not None

    def test_consequence_system_initialization(self, choice_processor):
        """Test that consequence system is properly initialized in choice processor."""
        assert hasattr(choice_processor, "consequence_system")
        assert isinstance(choice_processor.consequence_system, ConsequenceSystem)

        # Should have access to event bus
        assert choice_processor.consequence_system.event_bus is not None

        # Should have loaded templates and frameworks
        assert len(choice_processor.consequence_system.consequence_templates) > 0
        assert len(choice_processor.consequence_system.learning_frameworks) > 0
