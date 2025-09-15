"""
Tests for Intelligent Content Generation System

This module tests the intelligent content generation functionality including
AI-powered therapeutic scenario generation, adaptive dialogue generation,
custom therapeutic exercise creation, and narrative coherence maintenance.
"""

from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from src.components.advanced_therapeutic_intelligence.intelligent_content_generation_system import (
    ContentComplexity,
    ContentGenerationRequest,
    ContentType,
    GeneratedContent,
    IntelligentContentGenerationSystem,
    NarrativeContext,
    NarrativeStyle,
    TherapeuticIntent,
)


class TestIntelligentContentGenerationSystem:
    """Test Intelligent Content Generation System functionality."""

    @pytest_asyncio.fixture
    async def content_system(self):
        """Create test content generation system instance."""
        system = IntelligentContentGenerationSystem()
        await system.initialize()
        yield system
        await system.shutdown()

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        systems = {}

        for system_name in [
            "consequence_system",
            "emotional_safety_system",
            "adaptive_difficulty_engine",
            "character_development_system",
            "therapeutic_integration_system",
            "gameplay_loop_controller",
            "replayability_system",
            "collaborative_system",
            "error_recovery_manager"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.fixture
    def mock_integration_systems(self):
        """Create mock integration systems."""
        systems = {}

        for system_name in [
            "clinical_dashboard_manager",
            "cloud_deployment_manager",
            "clinical_validation_manager"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.fixture
    def mock_personalization_engine(self):
        """Create mock personalization engine."""
        engine = AsyncMock()
        engine.health_check.return_value = {"status": "healthy"}

        # Mock user profile
        mock_profile = Mock()
        mock_profile.interaction_preferences = {"communication_style": "supportive", "preferred_activities": ["mindfulness"]}
        mock_profile.therapeutic_preferences = {"preferred_framework": "cognitive_behavioral"}
        mock_profile.learning_characteristics = {"preferred_style": "visual"}
        mock_profile.engagement_metrics = {"average_engagement": 0.8, "current_engagement": 0.7, "average_session_duration": 20}
        mock_profile.skill_assessments = {"therapeutic_skills": 0.6}
        engine.get_user_profile.return_value = mock_profile

        return engine

    @pytest.fixture
    def mock_predictive_analytics(self):
        """Create mock predictive analytics."""
        analytics = AsyncMock()
        analytics.health_check.return_value = {"status": "healthy"}

        # Mock insights
        mock_insights = {
            "optimization_summary": {
                "total_optimizations": 5,
                "average_improvement_potential": 0.3
            }
        }
        analytics.get_predictive_insights.return_value = mock_insights

        return analytics

    @pytest.fixture
    def mock_ai_therapeutic_advisor(self):
        """Create mock AI therapeutic advisor."""
        advisor = AsyncMock()
        advisor.health_check.return_value = {"status": "healthy"}

        # Mock guidance
        mock_guidance = Mock()
        mock_guidance.title = "Session Planning Guidance"
        mock_guidance.description = "Recommended session structure"
        mock_guidance.recommended_actions = [{"action": "assess_mood", "priority": "high"}]
        advisor.generate_therapeutic_guidance.return_value = mock_guidance

        return advisor

    @pytest.fixture
    def sample_content_request(self):
        """Create sample content generation request."""
        return ContentGenerationRequest(
            user_id="test_user_001",
            content_type=ContentType.THERAPEUTIC_SCENARIO,
            therapeutic_intent=TherapeuticIntent.SKILL_BUILDING,
            complexity_level=ContentComplexity.MODERATE,
            narrative_style=NarrativeStyle.CONVERSATIONAL,
            context={
                "current_mood": "moderate",
                "therapeutic_goals": ["anxiety_management", "coping_skills"]
            },
            target_length=200,
            therapeutic_framework="cognitive_behavioral"
        )

    @pytest.mark.asyncio
    async def test_initialization(self, content_system):
        """Test content generation system initialization."""
        assert content_system.status == "running"
        assert len(content_system.scenario_generation_models) == 4
        assert len(content_system.dialogue_generation_models) == 4
        assert len(content_system.exercise_generation_models) == 4
        assert len(content_system.narrative_coherence_models) == 4

        # Should have background tasks running
        assert content_system._content_generation_task is not None
        assert content_system._narrative_maintenance_task is not None
        assert content_system._content_optimization_task is not None
        assert content_system._quality_validation_task is not None

    @pytest.mark.asyncio
    async def test_system_dependency_injection(self, content_system, mock_therapeutic_systems, mock_integration_systems, mock_personalization_engine, mock_predictive_analytics, mock_ai_therapeutic_advisor):
        """Test system dependency injection."""
        content_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        content_system.inject_integration_systems(**mock_integration_systems)
        content_system.inject_personalization_engine(mock_personalization_engine)
        content_system.inject_predictive_analytics(mock_predictive_analytics)
        content_system.inject_ai_therapeutic_advisor(mock_ai_therapeutic_advisor)

        # Should have all systems injected
        assert len(content_system.therapeutic_systems) == 9
        assert content_system.clinical_dashboard_manager is not None
        assert content_system.cloud_deployment_manager is not None
        assert content_system.clinical_validation_manager is not None
        assert content_system.personalization_engine is not None
        assert content_system.predictive_analytics is not None
        assert content_system.ai_therapeutic_advisor is not None

    @pytest.mark.asyncio
    async def test_generate_therapeutic_scenario(self, content_system, mock_personalization_engine, mock_ai_therapeutic_advisor):
        """Test therapeutic scenario generation."""
        content_system.inject_personalization_engine(mock_personalization_engine)
        content_system.inject_ai_therapeutic_advisor(mock_ai_therapeutic_advisor)

        user_id = "test_user_001"

        # Test different therapeutic intents
        therapeutic_intents = [
            TherapeuticIntent.SKILL_BUILDING,
            TherapeuticIntent.EMOTIONAL_REGULATION,
            TherapeuticIntent.COGNITIVE_RESTRUCTURING,
            TherapeuticIntent.MINDFULNESS_PRACTICE,
            TherapeuticIntent.CRISIS_INTERVENTION
        ]

        for intent in therapeutic_intents:
            content = await content_system.generate_therapeutic_scenario(
                user_id=user_id,
                therapeutic_intent=intent,
                complexity_level=ContentComplexity.MODERATE,
                context={"current_situation": "practice_session"}
            )

            # Should generate valid content
            assert isinstance(content, GeneratedContent)
            assert content.user_id == user_id
            assert content.content_type == ContentType.THERAPEUTIC_SCENARIO
            assert content.therapeutic_intent == intent
            assert content.title != ""
            assert content.content != ""
            assert content.word_count > 0
            assert content.estimated_duration > 0
            assert content.therapeutic_appropriateness >= 0.0
            assert content.narrative_coherence >= 0.0
            assert content.personalization_score >= 0.0
            assert content.engagement_potential >= 0.0
            assert len(content.sections) > 0

        # Should store content
        assert user_id in content_system.generated_content
        assert len(content_system.generated_content[user_id]) == len(therapeutic_intents)
        assert content_system.generation_metrics["total_content_generated"] == len(therapeutic_intents)
        assert content_system.generation_metrics["total_scenarios_created"] == len(therapeutic_intents)

    @pytest.mark.asyncio
    async def test_generate_adaptive_dialogue(self, content_system, mock_personalization_engine):
        """Test adaptive dialogue generation."""
        content_system.inject_personalization_engine(mock_personalization_engine)

        user_id = "test_user_002"

        # Test different dialogue contexts
        dialogue_contexts = [
            {
                "user_input": "I'm feeling anxious today",
                "user_emotional_state": "anxious",
                "conversation_history": ["Hello", "How are you feeling?"]
            },
            {
                "user_input": "I had a good day",
                "user_emotional_state": "positive",
                "conversation_history": ["Tell me about your day"]
            },
            {
                "user_input": "I'm struggling with this exercise",
                "user_emotional_state": "frustrated",
                "conversation_history": ["Let's try this exercise"]
            }
        ]

        for context in dialogue_contexts:
            content = await content_system.generate_adaptive_dialogue(
                user_id=user_id,
                dialogue_context=context,
                narrative_style=NarrativeStyle.SUPPORTIVE
            )

            # Should generate valid dialogue
            assert isinstance(content, GeneratedContent)
            assert content.user_id == user_id
            assert content.content_type == ContentType.DIALOGUE_RESPONSE
            assert content.narrative_style == NarrativeStyle.SUPPORTIVE
            assert content.content != ""
            assert content.word_count > 0
            assert content.therapeutic_appropriateness >= 0.0
            assert content.narrative_coherence >= 0.0
            assert content.personalization_score >= 0.0
            assert content.engagement_potential >= 0.0

        # Should store content
        assert user_id in content_system.generated_content
        assert len(content_system.generated_content[user_id]) == len(dialogue_contexts)
        assert content_system.generation_metrics["total_dialogues_generated"] == len(dialogue_contexts)

    @pytest.mark.asyncio
    async def test_create_custom_therapeutic_exercise(self, content_system, mock_personalization_engine, mock_predictive_analytics):
        """Test custom therapeutic exercise creation."""
        content_system.inject_personalization_engine(mock_personalization_engine)
        content_system.inject_predictive_analytics(mock_predictive_analytics)

        user_id = "test_user_003"

        # Test different therapeutic intents and difficulty levels
        test_cases = [
            (TherapeuticIntent.SKILL_BUILDING, ContentComplexity.SIMPLE),
            (TherapeuticIntent.EMOTIONAL_REGULATION, ContentComplexity.MODERATE),
            (TherapeuticIntent.MINDFULNESS_PRACTICE, ContentComplexity.COMPLEX),
            (TherapeuticIntent.COGNITIVE_RESTRUCTURING, ContentComplexity.MODERATE)
        ]

        for intent, difficulty in test_cases:
            content = await content_system.create_custom_therapeutic_exercise(
                user_id=user_id,
                therapeutic_intent=intent,
                difficulty_level=difficulty,
                therapeutic_framework="cognitive_behavioral"
            )

            # Should generate valid exercise
            assert isinstance(content, GeneratedContent)
            assert content.user_id == user_id
            assert content.content_type == ContentType.THERAPEUTIC_EXERCISE
            assert content.therapeutic_intent == intent
            assert content.complexity_level == difficulty
            assert content.title != ""
            assert content.content != ""
            assert content.word_count > 0
            assert content.estimated_duration > 0
            assert content.therapeutic_appropriateness >= 0.0
            assert content.narrative_coherence >= 0.0
            assert content.personalization_score >= 0.0
            assert content.engagement_potential >= 0.0
            assert len(content.sections) > 0
            assert len(content.interactive_elements) > 0

        # Should store content
        assert user_id in content_system.generated_content
        assert len(content_system.generated_content[user_id]) == len(test_cases)
        assert content_system.generation_metrics["total_exercises_created"] == len(test_cases)

    @pytest.mark.asyncio
    async def test_maintain_narrative_coherence(self, content_system):
        """Test narrative coherence maintenance."""
        user_id = "test_user_004"

        # Create test content
        content = GeneratedContent(
            user_id=user_id,
            content_type=ContentType.THERAPEUTIC_SCENARIO,
            title="Test Scenario",
            content="This is a test therapeutic scenario about resilience and growth.",
            therapeutic_intent=TherapeuticIntent.SKILL_BUILDING,
            metadata={"themes": ["resilience", "growth"]}
        )

        # Test coherence maintenance
        coherence_score = await content_system.maintain_narrative_coherence(
            user_id=user_id,
            new_content=content
        )

        # Should return valid coherence score
        assert isinstance(coherence_score, float)
        assert coherence_score >= 0.0 and coherence_score <= 1.0

        # Should create/update narrative context
        assert user_id in content_system.narrative_contexts
        narrative_context = content_system.narrative_contexts[user_id]
        assert isinstance(narrative_context, NarrativeContext)
        assert narrative_context.user_id == user_id
        assert narrative_context.total_interactions > 0

    @pytest.mark.asyncio
    async def test_generate_content_batch(self, content_system, mock_personalization_engine):
        """Test batch content generation."""
        content_system.inject_personalization_engine(mock_personalization_engine)

        # Create batch requests
        requests = [
            ContentGenerationRequest(
                user_id="batch_user_001",
                content_type=ContentType.THERAPEUTIC_SCENARIO,
                therapeutic_intent=TherapeuticIntent.SKILL_BUILDING
            ),
            ContentGenerationRequest(
                user_id="batch_user_002",
                content_type=ContentType.DIALOGUE_RESPONSE,
                therapeutic_intent=TherapeuticIntent.RELATIONSHIP_BUILDING,
                context={"user_input": "Hello"}
            ),
            ContentGenerationRequest(
                user_id="batch_user_003",
                content_type=ContentType.THERAPEUTIC_EXERCISE,
                therapeutic_intent=TherapeuticIntent.MINDFULNESS_PRACTICE
            )
        ]

        # Generate batch content
        generated_contents = await content_system.generate_content_batch(requests)

        # Should generate content for all requests
        assert isinstance(generated_contents, list)
        assert len(generated_contents) == len(requests)

        # All generated content should be valid
        for i, content in enumerate(generated_contents):
            assert isinstance(content, GeneratedContent)
            assert content.user_id == requests[i].user_id
            assert content.content_type == requests[i].content_type
            assert content.therapeutic_intent == requests[i].therapeutic_intent
            assert content.content != ""

    @pytest.mark.asyncio
    async def test_validate_content_quality(self, content_system):
        """Test content quality validation."""
        # Create test content
        content = GeneratedContent(
            user_id="quality_test_user",
            content_type=ContentType.THERAPEUTIC_SCENARIO,
            title="Quality Test Scenario",
            content="This is a therapeutic scenario designed to test quality validation with skill building and emotional regulation components.",
            therapeutic_intent=TherapeuticIntent.SKILL_BUILDING,
            therapeutic_appropriateness=0.8,
            narrative_coherence=0.7,
            personalization_score=0.6,
            engagement_potential=0.75
        )

        # Validate content quality
        quality_scores = await content_system.validate_content_quality(content)

        # Should return comprehensive quality scores
        assert isinstance(quality_scores, dict)
        assert "therapeutic_appropriateness" in quality_scores
        assert "narrative_coherence" in quality_scores
        assert "personalization_score" in quality_scores
        assert "engagement_potential" in quality_scores
        assert "clinical_safety" in quality_scores
        assert "overall_quality" in quality_scores

        # All scores should be valid
        for _score_name, score_value in quality_scores.items():
            assert isinstance(score_value, float)
            assert score_value >= 0.0 and score_value <= 1.0

        # Content should be updated with validated scores
        assert content.therapeutic_appropriateness >= 0.0
        assert content.narrative_coherence >= 0.0
        assert content.personalization_score >= 0.0
        assert content.engagement_potential >= 0.0

    @pytest.mark.asyncio
    async def test_get_content_generation_insights(self, content_system, mock_personalization_engine):
        """Test content generation insights."""
        content_system.inject_personalization_engine(mock_personalization_engine)

        user_id = "insights_test_user"

        # Generate some content first
        await content_system.generate_therapeutic_scenario(
            user_id=user_id,
            therapeutic_intent=TherapeuticIntent.SKILL_BUILDING
        )

        await content_system.generate_adaptive_dialogue(
            user_id=user_id,
            dialogue_context={"user_input": "Hello"}
        )

        await content_system.create_custom_therapeutic_exercise(
            user_id=user_id,
            therapeutic_intent=TherapeuticIntent.MINDFULNESS_PRACTICE
        )

        # Get insights
        insights = await content_system.get_content_generation_insights(user_id)

        # Should return comprehensive insights
        assert "user_id" in insights
        assert "analysis_timestamp" in insights
        assert "content_summary" in insights
        assert "narrative_analysis" in insights
        assert "personalization_effectiveness" in insights
        assert "content_recommendations" in insights
        assert "quality_trends" in insights

        # Validate content summary
        content_summary = insights["content_summary"]
        assert content_summary["total_content_generated"] > 0
        assert len(content_summary["content_types"]) > 0
        assert len(content_summary["therapeutic_intents"]) > 0
        assert content_summary["average_quality_score"] >= 0.0
        assert content_summary["total_word_count"] > 0
        assert content_summary["total_estimated_duration"] > 0

        # Validate narrative analysis
        narrative_analysis = insights["narrative_analysis"]
        assert "narrative_coherence_score" in narrative_analysis
        assert "character_development_progress" in narrative_analysis
        assert "completed_scenarios" in narrative_analysis

        # Validate recommendations
        recommendations = insights["content_recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, content_system, mock_personalization_engine, mock_ai_therapeutic_advisor):
        """Test performance benchmarks for content generation."""
        import time

        content_system.inject_personalization_engine(mock_personalization_engine)
        content_system.inject_ai_therapeutic_advisor(mock_ai_therapeutic_advisor)

        user_id = "performance_test_user"

        # Test scenario generation performance
        start_time = time.perf_counter()

        scenario = await content_system.generate_therapeutic_scenario(
            user_id=user_id,
            therapeutic_intent=TherapeuticIntent.SKILL_BUILDING,
            complexity_level=ContentComplexity.MODERATE
        )

        scenario_time = (time.perf_counter() - start_time) * 1000
        assert scenario_time < 500.0  # Should be under 500ms

        # Test dialogue generation performance
        start_time = time.perf_counter()

        await content_system.generate_adaptive_dialogue(
            user_id=user_id,
            dialogue_context={"user_input": "I'm feeling anxious"},
            narrative_style=NarrativeStyle.SUPPORTIVE
        )

        dialogue_time = (time.perf_counter() - start_time) * 1000
        assert dialogue_time < 500.0  # Should be under 500ms

        # Test exercise creation performance
        start_time = time.perf_counter()

        await content_system.create_custom_therapeutic_exercise(
            user_id=user_id,
            therapeutic_intent=TherapeuticIntent.MINDFULNESS_PRACTICE,
            difficulty_level=ContentComplexity.MODERATE
        )

        exercise_time = (time.perf_counter() - start_time) * 1000
        assert exercise_time < 500.0  # Should be under 500ms

        # Test narrative coherence performance
        start_time = time.perf_counter()

        await content_system.maintain_narrative_coherence(
            user_id=user_id,
            new_content=scenario
        )

        coherence_time = (time.perf_counter() - start_time) * 1000
        assert coherence_time < 200.0  # Should be under 200ms

        # Test insights generation performance
        start_time = time.perf_counter()

        await content_system.get_content_generation_insights(user_id)

        insights_time = (time.perf_counter() - start_time) * 1000
        assert insights_time < 300.0  # Should be under 300ms

    @pytest.mark.asyncio
    async def test_content_generation_interface_compatibility(self, content_system, mock_therapeutic_systems, mock_integration_systems, mock_personalization_engine, mock_predictive_analytics, mock_ai_therapeutic_advisor):
        """Test compatibility with content generation interface expectations."""
        # Inject all dependencies
        content_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        content_system.inject_integration_systems(**mock_integration_systems)
        content_system.inject_personalization_engine(mock_personalization_engine)
        content_system.inject_predictive_analytics(mock_predictive_analytics)
        content_system.inject_ai_therapeutic_advisor(mock_ai_therapeutic_advisor)

        user_id = "interface_test_user"

        # Test complete content generation workflow
        scenario = await content_system.generate_therapeutic_scenario(
            user_id=user_id,
            therapeutic_intent=TherapeuticIntent.SKILL_BUILDING
        )

        # Should match expected content structure
        assert hasattr(scenario, "content_id")
        assert hasattr(scenario, "content_type")
        assert hasattr(scenario, "title")
        assert hasattr(scenario, "content")
        assert hasattr(scenario, "therapeutic_intent")
        assert hasattr(scenario, "complexity_level")
        assert hasattr(scenario, "narrative_style")
        assert hasattr(scenario, "therapeutic_appropriateness")
        assert hasattr(scenario, "narrative_coherence")
        assert hasattr(scenario, "personalization_score")
        assert hasattr(scenario, "engagement_potential")
        assert hasattr(scenario, "sections")
        assert hasattr(scenario, "interactive_elements")

        # Test dialogue generation
        dialogue = await content_system.generate_adaptive_dialogue(
            user_id=user_id,
            dialogue_context={"user_input": "Hello"}
        )

        # Should match expected dialogue structure
        assert hasattr(dialogue, "content_id")
        assert hasattr(dialogue, "content")
        assert hasattr(dialogue, "dialogue_elements")

        # Test exercise creation
        exercise = await content_system.create_custom_therapeutic_exercise(
            user_id=user_id,
            therapeutic_intent=TherapeuticIntent.MINDFULNESS_PRACTICE
        )

        # Should match expected exercise structure
        assert hasattr(exercise, "content_id")
        assert hasattr(exercise, "title")
        assert hasattr(exercise, "content")
        assert hasattr(exercise, "sections")
        assert hasattr(exercise, "interactive_elements")

        # Test health check
        health_check = await content_system.health_check()

        # Should match expected health check structure
        assert "status" in health_check
        assert "generation_status" in health_check
        assert "total_content_generated" in health_check
        assert "generation_metrics" in health_check
