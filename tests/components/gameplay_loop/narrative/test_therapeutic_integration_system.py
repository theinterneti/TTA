"""
Tests for TherapeuticIntegrationSystem

This module tests therapeutic concept integration, progress tracking,
and adaptive therapeutic approaches functionality.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from src.components.gameplay_loop.narrative.events import EventBus
from src.components.gameplay_loop.narrative.therapeutic_integration_system import (
    IntegrationStrategy,
    ProgressMilestone,
    ResistancePattern,
    ResistanceType,
    TherapeuticApproach,
    TherapeuticConcept,
    TherapeuticIntegration,
    TherapeuticIntegrationSystem,
    TherapeuticProgress,
)
from src.components.gameplay_loop.services.session_state import SessionState


class TestTherapeuticIntegrationSystem:
    """Test TherapeuticIntegrationSystem functionality."""

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus

    @pytest.fixture
    def integration_system(self, event_bus):
        """Create therapeutic integration system instance."""
        return TherapeuticIntegrationSystem(event_bus)

    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = Mock(spec=SessionState)
        state.session_id = "test_session_123"
        state.user_id = "test_user_456"
        state.therapeutic_goals = ["anxiety_management", "emotional_regulation"]
        state.context = {
            "preferred_therapeutic_approach": TherapeuticApproach.COGNITIVE_BEHAVIORAL,
            "therapeutic_preferences": {"learning_style": "experiential"},
        }
        return state

    @pytest.fixture
    def cbt_session_state(self):
        """Create session state with CBT approach."""
        state = Mock(spec=SessionState)
        state.session_id = "cbt_session_789"
        state.user_id = "cbt_user_101"
        state.therapeutic_goals = ["thought_challenging", "behavioral_activation"]
        state.context = {
            "preferred_therapeutic_approach": TherapeuticApproach.COGNITIVE_BEHAVIORAL,
            "therapeutic_preferences": {"learning_style": "analytical"},
        }
        return state

    @pytest.fixture
    def mindfulness_session_state(self):
        """Create session state with mindfulness approach."""
        state = Mock(spec=SessionState)
        state.session_id = "mindfulness_session_456"
        state.user_id = "mindfulness_user_202"
        state.therapeutic_goals = ["present_moment_awareness", "emotional_regulation"]
        state.context = {
            "preferred_therapeutic_approach": TherapeuticApproach.MINDFULNESS_BASED,
            "therapeutic_preferences": {"learning_style": "mindful"},
        }
        return state

    @pytest.mark.asyncio
    async def test_integrate_therapeutic_concept_experiential(
        self, integration_system, session_state, event_bus
    ):
        """Test therapeutic concept integration with experiential learning."""
        concept_id = "thought_challenging"
        story_context = "You face a difficult decision that challenges your assumptions"
        strategy = IntegrationStrategy.EXPERIENTIAL_LEARNING

        integration = await integration_system.integrate_therapeutic_concept(
            session_state, concept_id, story_context, strategy
        )

        # Check integration structure
        assert isinstance(integration, TherapeuticIntegration)
        assert integration.user_id == session_state.user_id
        assert integration.session_id == session_state.session_id
        assert integration.concept_id == concept_id
        assert integration.strategy == strategy
        assert integration.story_context == story_context

        # Check narrative embedding
        assert integration.narrative_embedding != ""
        assert "practice" in integration.narrative_embedding.lower()

        # Check practice opportunities
        assert len(integration.practice_opportunities) > 0
        assert any(
            "experience" in opp.lower() for opp in integration.practice_opportunities
        )

        # Check that concept was created
        assert concept_id in integration_system.therapeutic_concepts

        # Check that integration was stored
        assert session_state.user_id in integration_system.integration_history
        assert len(integration_system.integration_history[session_state.user_id]) == 1

        # Check that event was published
        event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_integrate_therapeutic_concept_metaphorical(
        self, integration_system, session_state, event_bus
    ):
        """Test therapeutic concept integration with metaphorical embedding."""
        concept_id = "thought_challenging"
        story_context = "The path ahead is shrouded in uncertainty"
        strategy = IntegrationStrategy.METAPHORICAL_EMBEDDING

        integration = await integration_system.integrate_therapeutic_concept(
            session_state, concept_id, story_context, strategy
        )

        # Check metaphorical embedding
        assert integration.narrative_embedding != ""
        # Should include metaphorical language
        assert any(
            word in integration.narrative_embedding.lower()
            for word in ["detective", "scientist", "judge"]
        )

        # Check practice opportunities include metaphorical exploration
        assert any(
            "metaphorical" in opp.lower() for opp in integration.practice_opportunities
        )

    @pytest.mark.asyncio
    async def test_track_therapeutic_progress_new_concept(
        self, integration_system, session_state, event_bus
    ):
        """Test tracking therapeutic progress for new concept."""
        concept_id = "emotional_regulation"
        progress_data = {
            "skill_demonstration": 0.6,
            "practice_attempt": True,
            "successful": True,
            "story_context": "Successfully managed anger in conflict situation",
        }

        progress = await integration_system.track_therapeutic_progress(
            session_state, concept_id, progress_data
        )

        # Check progress structure
        assert isinstance(progress, TherapeuticProgress)
        assert progress.user_id == session_state.user_id
        assert progress.concept_id == concept_id
        assert progress.current_level == 0.6
        assert progress.practice_sessions == 1
        assert progress.successful_applications == 1
        assert progress.total_attempts == 1

        # Check story integration
        assert len(progress.story_contexts) == 1
        assert progress.story_contexts[0] == progress_data["story_context"]

        # Check that progress was stored
        assert session_state.user_id in integration_system.user_progress
        assert len(integration_system.user_progress[session_state.user_id]) == 1

        # Check that event was published
        event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_track_therapeutic_progress_milestone_achievement(
        self, integration_system, session_state, event_bus
    ):
        """Test milestone achievement during progress tracking."""
        concept_id = "anxiety_management"

        # Create initial progress
        progress = await integration_system.track_therapeutic_progress(
            session_state, concept_id, {"skill_demonstration": 0.5}
        )

        # Update progress to trigger milestone
        progress_data = {
            "skill_demonstration": 0.9,  # Above threshold
            "practice_attempt": True,
            "successful": True,
            "story_context": "Successfully used breathing techniques during panic",
        }

        updated_progress = await integration_system.track_therapeutic_progress(
            session_state, concept_id, progress_data
        )

        # Check milestone achievement
        assert (
            ProgressMilestone.SKILL_ACQUISITION in updated_progress.milestones_achieved
        )
        assert len(updated_progress.narrative_celebrations) > 0

        # Check session context was updated
        assert "recent_milestone" in session_state.context
        milestone_info = session_state.context["recent_milestone"]
        assert milestone_info["type"] == ProgressMilestone.SKILL_ACQUISITION.value

        # Check that multiple events were published (progress + milestone)
        assert event_bus.publish.call_count >= 2

    @pytest.mark.asyncio
    async def test_detect_therapeutic_resistance_low_engagement(
        self, integration_system, session_state, event_bus
    ):
        """Test detection of therapeutic resistance due to low engagement."""
        concept_id = "behavioral_activation"
        interaction_data = {
            "engagement_level": 0.2,  # Low engagement
            "skill_demonstration": 0.1,  # Low skill demonstration
            "emotional_response": "frustrated",
            "choice_pattern": "avoidant",
        }

        resistance_pattern = await integration_system.detect_therapeutic_resistance(
            session_state, concept_id, interaction_data
        )

        # Check resistance pattern
        assert isinstance(resistance_pattern, ResistancePattern)
        assert resistance_pattern.user_id == session_state.user_id
        assert concept_id in resistance_pattern.concept_areas
        assert resistance_pattern.resistance_type in [
            ResistanceType.EMOTIONAL_AVOIDANCE,
            ResistanceType.BEHAVIORAL_RELUCTANCE,
            ResistanceType.MOTIVATIONAL_AMBIVALENCE,
        ]

        # Check that resistance was stored
        assert session_state.user_id in integration_system.resistance_patterns
        assert len(integration_system.resistance_patterns[session_state.user_id]) == 1

        # Check that intervention was triggered
        assert "therapeutic_resistance_detected" in session_state.context

        # Check that event was published
        event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_detect_therapeutic_resistance_insufficient_indicators(
        self, integration_system, session_state
    ):
        """Test that resistance is not detected with insufficient indicators."""
        concept_id = "mindfulness_practice"
        interaction_data = {
            "engagement_level": 0.8,  # Good engagement
            "skill_demonstration": 0.7,  # Good skill demonstration
            "emotional_response": "calm",
        }

        resistance_pattern = await integration_system.detect_therapeutic_resistance(
            session_state, concept_id, interaction_data
        )

        # Should not detect resistance
        assert resistance_pattern is None
        assert session_state.user_id not in integration_system.resistance_patterns

    @pytest.mark.asyncio
    async def test_provide_alternative_pathway(self, integration_system, session_state):
        """Test providing alternative therapeutic pathway."""
        concept_id = "emotional_regulation"
        current_approach = TherapeuticApproach.COGNITIVE_BEHAVIORAL

        pathway = await integration_system.provide_alternative_pathway(
            session_state, concept_id, current_approach
        )

        # Check pathway structure
        assert "alternative_approach" in pathway
        assert "integration_strategy" in pathway
        assert "story_adaptation" in pathway
        assert "support_level" in pathway
        assert "pacing" in pathway

        # Should provide different approach
        assert pathway["alternative_approach"] != current_approach.value

        # Check session context was updated
        assert "alternative_pathway" in session_state.context

    def test_concept_template_loading(self, integration_system):
        """Test that therapeutic concept templates are properly loaded."""
        templates = integration_system.concept_templates

        # Check that templates exist for different approaches
        assert TherapeuticApproach.COGNITIVE_BEHAVIORAL in templates
        assert TherapeuticApproach.MINDFULNESS_BASED in templates
        assert TherapeuticApproach.DIALECTICAL_BEHAVIORAL in templates

        # Check CBT templates
        cbt_templates = templates[TherapeuticApproach.COGNITIVE_BEHAVIORAL]
        assert len(cbt_templates) > 0

        for template in cbt_templates:
            assert "name" in template
            assert "description" in template
            assert "core_principles" in template
            assert "learning_objectives" in template
            assert "story_metaphors" in template
            assert "difficulty_level" in template

    def test_integration_strategy_loading(self, integration_system):
        """Test that integration strategies are properly loaded."""
        strategies = integration_system.integration_strategies

        # Check that all strategies are loaded
        for strategy in IntegrationStrategy:
            assert strategy in strategies

            strategy_config = strategies[strategy]
            assert "description" in strategy_config
            assert "implementation" in strategy_config
            assert "feedback_style" in strategy_config
            assert "engagement_level" in strategy_config

    def test_story_metaphor_loading(self, integration_system):
        """Test that story metaphors are properly loaded."""
        metaphors = integration_system.story_metaphors

        # Check that metaphors exist for common therapeutic concepts
        assert "emotional_regulation" in metaphors
        assert "anxiety_management" in metaphors
        assert "depression_recovery" in metaphors

        # Check metaphor structure
        for concept, metaphor_list in metaphors.items():
            assert isinstance(metaphor_list, list)
            assert len(metaphor_list) > 0
            for metaphor in metaphor_list:
                assert isinstance(metaphor, str)
                assert len(metaphor) > 0

    def test_celebration_template_loading(self, integration_system):
        """Test that celebration templates are properly loaded."""
        celebrations = integration_system.celebration_templates

        # Check that templates exist for different milestone types
        assert ProgressMilestone.SKILL_ACQUISITION in celebrations
        assert ProgressMilestone.INSIGHT_DEVELOPMENT in celebrations
        assert ProgressMilestone.BEHAVIORAL_CHANGE in celebrations

        # Check template structure
        for milestone, templates in celebrations.items():
            assert isinstance(templates, list)
            assert len(templates) > 0
            for template in templates:
                assert isinstance(template, str)
                assert len(template) > 0

    @pytest.mark.asyncio
    async def test_get_or_create_concept_from_template(
        self, integration_system, cbt_session_state
    ):
        """Test concept creation from template."""
        concept_id = "thought_challenging"

        concept = await integration_system._get_or_create_concept(
            concept_id, cbt_session_state
        )

        # Check concept structure
        assert isinstance(concept, TherapeuticConcept)
        assert concept.concept_id == concept_id
        assert concept.name == "Thought Challenging"
        assert concept.approach == TherapeuticApproach.COGNITIVE_BEHAVIORAL
        assert len(concept.core_principles) > 0
        assert len(concept.learning_objectives) > 0
        assert len(concept.story_metaphors) > 0

        # Check that concept was stored
        assert concept_id in integration_system.therapeutic_concepts

    @pytest.mark.asyncio
    async def test_get_or_create_concept_generic(
        self, integration_system, session_state
    ):
        """Test generic concept creation when no template matches."""
        concept_id = "custom_therapeutic_concept"

        concept = await integration_system._get_or_create_concept(
            concept_id, session_state
        )

        # Check generic concept structure
        assert isinstance(concept, TherapeuticConcept)
        assert concept.concept_id == concept_id
        assert concept.name == "Custom Therapeutic Concept"
        assert concept.description == f"Therapeutic concept: {concept_id}"
        assert concept.approach == TherapeuticApproach.COGNITIVE_BEHAVIORAL  # Default

    def test_determine_resistance_type(self, integration_system):
        """Test resistance type determination."""
        # Test emotional avoidance
        indicators = ["emotional_frustration", "low_engagement"]
        resistance_type = integration_system._determine_resistance_type(indicators)
        assert resistance_type == ResistanceType.EMOTIONAL_AVOIDANCE

        # Test behavioral reluctance
        indicators = ["skill_avoidance", "avoidant_choices"]
        resistance_type = integration_system._determine_resistance_type(indicators)
        assert resistance_type == ResistanceType.BEHAVIORAL_RELUCTANCE

        # Test motivational ambivalence
        indicators = ["low_engagement"]
        resistance_type = integration_system._determine_resistance_type(indicators)
        assert resistance_type == ResistanceType.MOTIVATIONAL_AMBIVALENCE

        # Test cognitive resistance (default)
        indicators = ["avoidant_choices"]
        resistance_type = integration_system._determine_resistance_type(indicators)
        assert resistance_type == ResistanceType.COGNITIVE_RESISTANCE

    def test_get_therapeutic_progress_summary(self, integration_system, session_state):
        """Test therapeutic progress summary generation."""
        user_id = session_state.user_id

        # Add some progress data
        progress_list = []
        for i, concept in enumerate(
            ["anxiety_management", "emotional_regulation", "thought_challenging"]
        ):
            progress = TherapeuticProgress(
                user_id=user_id,
                session_id=session_state.session_id,
                concept_id=concept,
                concept_name=concept.replace("_", " ").title(),
                current_level=0.3 + i * 0.2,
                practice_sessions=i + 1,
                successful_applications=i,
                total_attempts=i + 1,
                milestones_achieved=(
                    [ProgressMilestone.SKILL_ACQUISITION] if i > 0 else []
                ),
                last_updated=datetime.utcnow() - timedelta(days=i),
            )
            progress_list.append(progress)

        integration_system.user_progress[user_id] = progress_list

        summary = integration_system.get_therapeutic_progress_summary(user_id)

        # Check summary structure
        assert "user_id" in summary
        assert "total_concepts" in summary
        assert "total_milestones" in summary
        assert "average_progress" in summary
        assert "recent_activity" in summary
        assert "milestone_summary" in summary
        assert "concept_progress" in summary

        # Check values
        assert summary["total_concepts"] == 3
        assert summary["total_milestones"] == 2  # Two concepts have milestones
        assert summary["average_progress"] > 0
        assert len(summary["concept_progress"]) == 3

    def test_get_therapeutic_progress_summary_no_data(self, integration_system):
        """Test progress summary when no data exists."""
        summary = integration_system.get_therapeutic_progress_summary(
            "nonexistent_user"
        )

        assert "error" in summary
        assert summary["error"] == "No progress data available"

    def test_metrics_tracking(self, integration_system):
        """Test metrics tracking."""
        initial_metrics = integration_system.get_metrics()

        # Check metric structure
        assert "concepts_integrated" in initial_metrics
        assert "progress_milestones_achieved" in initial_metrics
        assert "resistance_patterns_detected" in initial_metrics
        assert "adaptive_interventions" in initial_metrics
        assert "celebration_events" in initial_metrics
        assert "total_concepts_loaded" in initial_metrics
        assert "active_users_tracked" in initial_metrics

        # Initially should be zero
        assert initial_metrics["concepts_integrated"] == 0
        assert initial_metrics["progress_milestones_achieved"] == 0

    @pytest.mark.asyncio
    async def test_health_check(self, integration_system):
        """Test health check functionality."""
        health = await integration_system.health_check()

        assert health["status"] == "healthy"
        assert "concept_templates_loaded" in health
        assert "integration_strategies_configured" in health
        assert "story_metaphors_available" in health
        assert "celebration_templates_loaded" in health
        assert "progress_threshold" in health
        assert "resistance_detection_threshold" in health
        assert "metrics" in health

        # Should have loaded templates and strategies
        assert health["concept_templates_loaded"] > 0
        assert health["integration_strategies_configured"] == len(IntegrationStrategy)
        assert health["story_metaphors_available"] > 0
        assert health["celebration_templates_loaded"] > 0
