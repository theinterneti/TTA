"""
Tests for ConsequenceSystem

This module tests the consequence generation, learning opportunity framing,
and causality explanation functionality.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.components.gameplay_loop.models.core import (
    ChoiceType,
    ConsequenceType,
    TherapeuticOutcome,
    UserChoice,
)
from src.components.gameplay_loop.narrative.consequence_system import (
    CausalityExplanation,
    ConsequenceGenerationContext,
    ConsequencePattern,
    ConsequenceSeverity,
    ConsequenceSystem,
)
from src.components.gameplay_loop.narrative.events import EventBus
from src.components.gameplay_loop.services.session_state import SessionState


class TestConsequenceSystem:
    """Test ConsequenceSystem functionality."""

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        return Mock(spec=EventBus)

    @pytest.fixture
    def consequence_system(self, event_bus):
        """Create consequence system instance."""
        return ConsequenceSystem(event_bus)

    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = Mock(spec=SessionState)
        state.session_id = "test_session_123"
        state.user_id = "test_user_456"
        state.therapeutic_goals = ["anxiety_management", "communication_skills"]
        state.progress_metrics = {
            "anxiety_management": 0.3,
            "communication_skills": 0.5,
        }
        state.context = {"narrative_context": "therapeutic_session"}
        state.emotional_state = {"anxious": 0.6, "confident": 0.4}
        return state

    @pytest.fixture
    def positive_choice(self):
        """Create positive therapeutic choice."""
        return UserChoice(
            choice_id="choice_positive",
            text="Take a deep breath and express your feelings calmly",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_relevance=0.8,
            emotional_weight=0.6,
            difficulty_level=0.4,
        )

    @pytest.fixture
    def challenging_choice(self):
        """Create challenging choice that might lead to learning."""
        return UserChoice(
            choice_id="choice_challenging",
            text="Avoid the conversation and walk away",
            choice_type=ChoiceType.NARRATIVE,
            therapeutic_relevance=0.3,
            emotional_weight=0.7,
            difficulty_level=0.6,
        )

    @pytest.mark.asyncio
    async def test_generate_consequences_positive_choice(
        self, consequence_system, session_state, positive_choice
    ):
        """Test consequence generation for positive therapeutic choice."""
        context = ConsequenceGenerationContext(
            choice=positive_choice,
            session_state=session_state,
            therapeutic_goals=["anxiety_management", "communication_skills"],
            user_progress={"anxiety_management": 0.3},
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Check basic structure
        assert consequence_set.choice_id == positive_choice.choice_id
        assert len(consequence_set.consequences) > 0
        assert consequence_set.consequence_type in [
            ConsequenceType.IMMEDIATE,
            ConsequenceType.THERAPEUTIC,
        ]

        # Check therapeutic outcomes
        assert len(consequence_set.therapeutic_outcomes) > 0
        for outcome in consequence_set.therapeutic_outcomes:
            assert isinstance(outcome, TherapeuticOutcome)
            assert outcome.therapeutic_value > 0

        # Check learning opportunities
        assert len(consequence_set.learning_opportunities) > 0

        # Check that consequences have therapeutic framing
        for consequence in consequence_set.consequences:
            assert "therapeutic_frame" in consequence
            assert "reflection_prompts" in consequence

    @pytest.mark.asyncio
    async def test_generate_consequences_challenging_choice(
        self, consequence_system, session_state, challenging_choice
    ):
        """Test consequence generation for challenging choice (framed as learning)."""
        context = ConsequenceGenerationContext(
            choice=challenging_choice,
            session_state=session_state,
            therapeutic_goals=["anxiety_management"],
            user_progress={"anxiety_management": 0.3},
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Check basic structure
        assert consequence_set.choice_id == challenging_choice.choice_id
        assert len(consequence_set.consequences) > 0

        # Should still have learning opportunities even for challenging choices
        assert len(consequence_set.learning_opportunities) > 0

        # Check that consequences are framed therapeutically
        for consequence in consequence_set.consequences:
            assert "therapeutic_frame" in consequence
            # Should have learning-focused framing for challenging choices
            frame = consequence["therapeutic_frame"]
            assert any(
                word in frame.lower()
                for word in ["learn", "opportunity", "experience", "growth"]
            )

    @pytest.mark.asyncio
    async def test_therapeutic_outcome_generation(
        self, consequence_system, session_state, positive_choice
    ):
        """Test therapeutic outcome generation."""
        context = ConsequenceGenerationContext(
            choice=positive_choice,
            session_state=session_state,
            therapeutic_goals=["emotional_regulation"],
            user_progress={"emotional_regulation": 0.2},
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Check therapeutic outcomes
        assert len(consequence_set.therapeutic_outcomes) > 0

        for outcome in consequence_set.therapeutic_outcomes:
            assert outcome.therapeutic_value > 0
            assert outcome.therapeutic_value <= 1.0
            assert outcome.outcome_type != ""
            assert outcome.description != ""
            assert isinstance(outcome.achieved_at, datetime)

    @pytest.mark.asyncio
    async def test_learning_opportunity_creation(
        self, consequence_system, session_state, positive_choice
    ):
        """Test learning opportunity creation."""
        context = ConsequenceGenerationContext(
            choice=positive_choice,
            session_state=session_state,
            therapeutic_goals=["communication_skills"],
            user_progress={},
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Check learning opportunities
        assert len(consequence_set.learning_opportunities) > 0

        for opportunity in consequence_set.learning_opportunities:
            assert isinstance(opportunity, str)
            assert len(opportunity) > 0
            # Should be user-friendly text
            assert any(
                word in opportunity.lower()
                for word in ["practice", "opportunity", "chance", "learn"]
            )

    @pytest.mark.asyncio
    async def test_consequence_framing_approaches(
        self, consequence_system, session_state
    ):
        """Test different consequence framing approaches."""
        # Test positive reinforcement framing
        positive_choice = UserChoice(
            choice_id="positive_test",
            text="Communicate openly and honestly",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_relevance=0.9,
            emotional_weight=0.5,
        )

        context = ConsequenceGenerationContext(
            choice=positive_choice,
            session_state=session_state,
            therapeutic_goals=["communication_skills"],
            user_progress={"communication_skills": 0.7},
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Should have positive framing for high-alignment choices
        for consequence in consequence_set.consequences:
            frame = consequence["therapeutic_frame"]
            assert any(
                word in frame.lower()
                for word in ["positive", "well done", "skills", "growing"]
            )

    @pytest.mark.asyncio
    async def test_reflection_prompt_generation(
        self, consequence_system, session_state, positive_choice
    ):
        """Test reflection prompt generation."""
        context = ConsequenceGenerationContext(
            choice=positive_choice,
            session_state=session_state,
            therapeutic_goals=["self_awareness"],
            user_progress={},
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Check reflection prompts
        for consequence in consequence_set.consequences:
            prompts = consequence["reflection_prompts"]
            assert isinstance(prompts, list)
            assert len(prompts) > 0
            assert len(prompts) <= 3  # Should limit to max 3 prompts

            for prompt in prompts:
                assert isinstance(prompt, str)
                assert len(prompt) > 0
                assert prompt.endswith("?")  # Should be questions

    @pytest.mark.asyncio
    async def test_choice_pattern_tracking(
        self, consequence_system, session_state, positive_choice
    ):
        """Test choice pattern tracking and recognition."""
        context = ConsequenceGenerationContext(
            choice=positive_choice,
            session_state=session_state,
            therapeutic_goals=["communication_skills"],
            user_progress={},
        )

        # Generate consequences multiple times to build pattern
        for _ in range(3):
            await consequence_system.generate_consequences(context)

        # Check that patterns are being tracked
        patterns = await consequence_system.recognize_patterns(session_state.user_id)

        # Should have at least one pattern
        assert len(patterns) > 0

        for pattern in patterns:
            assert isinstance(pattern, ConsequencePattern)
            assert pattern.frequency >= 3
            assert pattern.choice_pattern != ""
            assert len(pattern.learning_opportunities) > 0

    @pytest.mark.asyncio
    async def test_causality_explanation(
        self, consequence_system, session_state, positive_choice
    ):
        """Test causality explanation generation."""
        context = ConsequenceGenerationContext(
            choice=positive_choice,
            session_state=session_state,
            therapeutic_goals=["communication_skills"],
            user_progress={},
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Generate causality explanation
        explanation = await consequence_system.explain_causality(
            positive_choice.choice_id, consequence_set.consequence_id, context
        )

        assert isinstance(explanation, CausalityExplanation)
        assert explanation.choice_id == positive_choice.choice_id
        assert explanation.consequence_id == consequence_set.consequence_id
        assert len(explanation.causal_chain) > 0
        assert explanation.therapeutic_insight != ""
        assert len(explanation.learning_points) > 0
        assert 0.0 <= explanation.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_template_selection(self, consequence_system, session_state):
        """Test consequence template selection based on choice content."""
        # Test communication choice
        comm_choice = UserChoice(
            choice_id="comm_test",
            text="Talk openly about your feelings",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_relevance=0.7,
        )

        context = ConsequenceGenerationContext(
            choice=comm_choice,
            session_state=session_state,
            therapeutic_goals=["communication_skills"],
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Should generate communication-related consequences
        assert len(consequence_set.consequences) > 0

        # Check that therapeutic outcomes relate to communication
        comm_related = any(
            "communication" in outcome.outcome_type.lower()
            or "expression" in outcome.outcome_type.lower()
            for outcome in consequence_set.therapeutic_outcomes
        )
        assert comm_related

    @pytest.mark.asyncio
    async def test_therapeutic_framework_selection(
        self, consequence_system, session_state
    ):
        """Test therapeutic framework selection for learning prompts."""
        # Test with anxiety-related goals
        anxiety_choice = UserChoice(
            choice_id="anxiety_test",
            text="Practice breathing exercises to manage anxiety",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_relevance=0.8,
        )

        context = ConsequenceGenerationContext(
            choice=anxiety_choice,
            session_state=session_state,
            therapeutic_goals=["anxiety_management", "stress_management"],
            user_progress={},
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Should include framework-specific learning opportunities
        assert len(consequence_set.learning_opportunities) > 0

        # Should have anxiety/stress-related learning opportunities
        anxiety_related = any(
            "anxiety" in opportunity.lower()
            or "stress" in opportunity.lower()
            or "thoughts" in opportunity.lower()
            or "feelings" in opportunity.lower()
            for opportunity in consequence_set.learning_opportunities
        )
        assert anxiety_related

    @pytest.mark.asyncio
    async def test_consequence_severity_determination(
        self, consequence_system, session_state
    ):
        """Test consequence severity determination."""
        # High emotional weight choice
        high_emotion_choice = UserChoice(
            choice_id="high_emotion",
            text="Confront the person angrily",
            choice_type=ChoiceType.NARRATIVE,
            therapeutic_relevance=0.3,
            emotional_weight=0.9,
        )

        context = ConsequenceGenerationContext(
            choice=high_emotion_choice,
            session_state=session_state,
            therapeutic_goals=["emotional_regulation"],
        )

        consequence_set = await consequence_system.generate_consequences(context)

        # Should have consequences with appropriate severity
        for consequence in consequence_set.consequences:
            assert "severity" in consequence
            severity = consequence["severity"]
            # High emotional weight should lead to moderate or significant severity
            assert severity in [
                ConsequenceSeverity.MODERATE.value,
                ConsequenceSeverity.SIGNIFICANT.value,
            ]

    def test_get_metrics(self, consequence_system):
        """Test metrics collection."""
        metrics = consequence_system.get_metrics()

        assert "consequences_generated" in metrics
        assert "learning_opportunities_created" in metrics
        assert "positive_reinforcements" in metrics
        assert "pattern_recognitions" in metrics
        assert "causality_explanations" in metrics
        assert "active_patterns" in metrics
        assert "causality_explanations_stored" in metrics

        # Initially should be zero
        assert metrics["consequences_generated"] == 0
        assert metrics["learning_opportunities_created"] == 0

    @pytest.mark.asyncio
    async def test_health_check(self, consequence_system):
        """Test health check functionality."""
        health = await consequence_system.health_check()

        assert health["status"] == "healthy"
        assert "templates_loaded" in health
        assert "frameworks_loaded" in health
        assert "patterns_tracked" in health
        assert "metrics" in health

        # Should have loaded templates and frameworks
        assert health["templates_loaded"] > 0
        assert health["frameworks_loaded"] > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, consequence_system, session_state):
        """Test error handling in consequence generation."""
        # Create invalid choice
        invalid_choice = UserChoice(
            choice_id="",  # Invalid empty ID
            text="",  # Invalid empty text
            choice_type=ChoiceType.NARRATIVE,
        )

        context = ConsequenceGenerationContext(
            choice=invalid_choice, session_state=session_state, therapeutic_goals=[]
        )

        # Should handle gracefully and return minimal consequence set
        consequence_set = await consequence_system.generate_consequences(context)

        assert consequence_set is not None
        assert consequence_set.choice_id == ""
        assert len(consequence_set.consequences) > 0  # Should have error consequence

    @pytest.mark.asyncio
    async def test_event_publishing(
        self, consequence_system, session_state, positive_choice, event_bus
    ):
        """Test that consequence events are published."""
        event_bus.publish = AsyncMock()

        context = ConsequenceGenerationContext(
            choice=positive_choice,
            session_state=session_state,
            therapeutic_goals=["communication_skills"],
        )

        await consequence_system.generate_consequences(context)

        # Should have published consequence event
        event_bus.publish.assert_called_once()

        # Check event details
        published_event = event_bus.publish.call_args[0][0]
        assert published_event.session_id == session_state.session_id
        assert published_event.user_id == session_state.user_id
