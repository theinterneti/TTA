"""
Tests for TherapeuticIntegrationSystem

This module tests the therapeutic integration system implementation
including framework integration, personalized recommendations, and scenario generation.
"""


import pytest

from src.components.therapeutic_systems.therapeutic_integration_system import (
    IntegrationStrategy,
    ScenarioType,
    TherapeuticFramework,
    TherapeuticIntegrationSystem,
    TherapeuticRecommendation,
    TherapeuticScenario,
)


class TestTherapeuticIntegrationSystem:
    """Test TherapeuticIntegrationSystem functionality."""

    @pytest.fixture
    def integration_system(self):
        """Create therapeutic integration system instance."""
        return TherapeuticIntegrationSystem()

    @pytest.mark.asyncio
    async def test_initialization(self, integration_system):
        """Test system initialization."""
        await integration_system.initialize()

        # Should have therapeutic frameworks configured
        assert len(TherapeuticFramework) >= 8  # 8+ therapeutic frameworks

        # Should have integration strategies configured
        assert len(IntegrationStrategy) == 8  # 8 integration strategies

        # Should have scenario types configured
        assert len(ScenarioType) >= 5  # 5+ scenario types

        # Should have framework configurations
        assert len(integration_system.framework_configurations) >= 8
        assert TherapeuticFramework.CBT in integration_system.framework_configurations
        assert TherapeuticFramework.DBT in integration_system.framework_configurations

        # Should have integration strategies
        assert len(integration_system.integration_strategies) == 8
        assert IntegrationStrategy.EXPERIENTIAL_LEARNING in integration_system.integration_strategies

    @pytest.mark.asyncio
    async def test_generate_personalized_recommendations_basic(self, integration_system):
        """Test basic personalized recommendation generation."""
        await integration_system.initialize()

        recommendations = await integration_system.generate_personalized_recommendations(
            user_id="test_user_001",
            therapeutic_goals=["anxiety_management", "confidence_building"]
        )

        # Should return recommendations
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert len(recommendations) <= integration_system.max_recommendations_per_user

        # Each recommendation should be valid
        for rec in recommendations:
            assert isinstance(rec, TherapeuticRecommendation)
            assert rec.user_id == "test_user_001"
            assert isinstance(rec.framework, TherapeuticFramework)
            assert isinstance(rec.scenario_type, ScenarioType)
            assert isinstance(rec.integration_strategy, IntegrationStrategy)
            assert 0.0 <= rec.priority_score <= 1.0

    @pytest.mark.asyncio
    async def test_generate_recommendations_with_character_data(self, integration_system):
        """Test recommendation generation with character development data."""
        await integration_system.initialize()

        character_data = {
            "name": "Hero",
            "attributes": {
                "courage": 8.0,
                "wisdom": 6.0,
                "compassion": 7.5,
                "mindfulness": 5.5,
                "confidence": 4.0,  # Growth area
            }
        }

        recommendations = await integration_system.generate_personalized_recommendations(
            user_id="test_user_002",
            therapeutic_goals=["confidence_building"],
            character_data=character_data
        )

        # Should generate recommendations
        assert len(recommendations) > 0

        # Should consider character strengths and growth areas
        for rec in recommendations:
            assert rec.character_alignment is not None
            assert isinstance(rec.character_alignment, dict)

    @pytest.mark.asyncio
    async def test_generate_recommendations_with_emotional_state(self, integration_system):
        """Test recommendation generation with emotional state considerations."""
        await integration_system.initialize()

        # Crisis emotional state
        emotional_state = {
            "crisis_detected": True,
            "emotional_stability": 0.3,
            "crisis_level": "HIGH"
        }

        recommendations = await integration_system.generate_personalized_recommendations(
            user_id="test_user_003",
            therapeutic_goals=["anxiety_management"],
            emotional_state=emotional_state
        )

        # Should prioritize stabilizing frameworks during crisis
        assert len(recommendations) > 0

        # Should favor DBT or Mindfulness for crisis situations
        framework_names = [rec.framework for rec in recommendations]
        assert any(fw in [TherapeuticFramework.DBT, TherapeuticFramework.MINDFULNESS] for fw in framework_names)

    @pytest.mark.asyncio
    async def test_create_therapeutic_scenario_basic(self, integration_system):
        """Test basic therapeutic scenario creation."""
        await integration_system.initialize()

        scenario = await integration_system.create_therapeutic_scenario(
            user_id="test_user_004",
            framework=TherapeuticFramework.CBT,
            scenario_type=ScenarioType.ANXIETY_MANAGEMENT
        )

        # Should return valid scenario
        assert isinstance(scenario, TherapeuticScenario)
        assert scenario.user_id == "test_user_004"
        assert scenario.framework == TherapeuticFramework.CBT
        assert scenario.scenario_type == ScenarioType.ANXIETY_MANAGEMENT

        # Should have required scenario elements
        assert scenario.title is not None
        assert scenario.description is not None
        assert scenario.narrative_context is not None
        assert isinstance(scenario.therapeutic_goals, list)
        assert isinstance(scenario.practice_opportunities, list)
        assert isinstance(scenario.reflection_prompts, list)
        assert isinstance(scenario.success_criteria, list)
        assert scenario.estimated_duration > 0

    @pytest.mark.asyncio
    async def test_create_scenario_with_character_data(self, integration_system):
        """Test scenario creation with character development integration."""
        await integration_system.initialize()

        character_data = {
            "name": "Brave Explorer",
            "attributes": {
                "courage": 7.0,
                "wisdom": 6.5,
                "empathy": 8.0,
            }
        }

        scenario = await integration_system.create_therapeutic_scenario(
            user_id="test_user_005",
            framework=TherapeuticFramework.HUMANISTIC,
            scenario_type=ScenarioType.CONFIDENCE_BUILDING,
            character_data=character_data
        )

        # Should incorporate character data
        assert "Brave Explorer" in scenario.narrative_context or scenario.character_involvement
        assert scenario.character_involvement is not None
        assert isinstance(scenario.character_involvement, dict)

    @pytest.mark.asyncio
    async def test_create_scenario_with_difficulty_adaptation(self, integration_system):
        """Test scenario creation with adaptive difficulty."""
        await integration_system.initialize()

        # Test easy difficulty
        easy_scenario = await integration_system.create_therapeutic_scenario(
            user_id="test_user_006",
            framework=TherapeuticFramework.MINDFULNESS,
            scenario_type=ScenarioType.ANXIETY_MANAGEMENT,
            difficulty_level="easy"
        )

        # Test hard difficulty
        hard_scenario = await integration_system.create_therapeutic_scenario(
            user_id="test_user_007",
            framework=TherapeuticFramework.MINDFULNESS,
            scenario_type=ScenarioType.ANXIETY_MANAGEMENT,
            difficulty_level="hard"
        )

        # Hard scenario should have more practice opportunities
        assert len(hard_scenario.practice_opportunities) >= len(easy_scenario.practice_opportunities)
        assert len(hard_scenario.success_criteria) >= len(easy_scenario.success_criteria)

    def test_framework_configurations(self, integration_system):
        """Test therapeutic framework configurations."""
        configs = integration_system.framework_configurations

        # Test CBT configuration
        cbt_config = configs[TherapeuticFramework.CBT]
        assert cbt_config["name"] == "Cognitive Behavioral Therapy"
        assert "cognitive_restructuring" in cbt_config["techniques"]
        assert "anxiety" in cbt_config["suitable_for"]
        assert "self_awareness" in cbt_config["character_attributes"]

        # Test DBT configuration
        dbt_config = configs[TherapeuticFramework.DBT]
        assert dbt_config["name"] == "Dialectical Behavior Therapy"
        assert "mindfulness" in dbt_config["techniques"]
        assert "emotional_dysregulation" in dbt_config["suitable_for"]
        assert "emotional_intelligence" in dbt_config["character_attributes"]

    def test_integration_strategy_configurations(self, integration_system):
        """Test integration strategy configurations."""
        strategies = integration_system.integration_strategies

        # Test experiential learning
        exp_learning = strategies[IntegrationStrategy.EXPERIENTIAL_LEARNING]
        assert exp_learning["engagement_level"] == "high"
        assert exp_learning["retention_rate"] == "high"
        assert "skill_practice" in exp_learning["suitable_for"]

        # Test metaphorical embedding
        metaphorical = strategies[IntegrationStrategy.METAPHORICAL_EMBEDDING]
        assert metaphorical["engagement_level"] == "high"
        assert "complex_concepts" in metaphorical["suitable_for"]

    def test_scenario_templates(self, integration_system):
        """Test scenario template configurations."""
        templates = integration_system.scenario_templates

        # Test anxiety management template
        anxiety_template = templates[ScenarioType.ANXIETY_MANAGEMENT]
        assert anxiety_template["title"] == "Facing the Challenge"
        assert "anxiety_reduction" in anxiety_template["therapeutic_goals"]
        assert "breathing_exercises" in anxiety_template["practice_opportunities"]
        assert len(anxiety_template["reflection_prompts"]) > 0

        # Test confidence building template
        confidence_template = templates[ScenarioType.CONFIDENCE_BUILDING]
        assert confidence_template["title"] == "Stepping Into Power"
        assert "self_efficacy" in confidence_template["therapeutic_goals"]

    def test_user_context_analysis(self, integration_system):
        """Test user context analysis functionality."""
        character_data = {
            "attributes": {
                "courage": 8.0,
                "wisdom": 6.0,
                "compassion": 4.0,
                "confidence": 3.0,
            }
        }

        emotional_state = {
            "emotional_stability": 0.6,
            "crisis_detected": False,
        }

        context = integration_system._analyze_user_context(
            "test_user", ["anxiety_management"], character_data, None, emotional_state
        )

        # Should identify character strengths and growth areas
        assert "courage" in context["character_strengths"]
        assert "confidence" in context["character_growth_areas"]
        assert context["emotional_stability"] == 0.6
        assert context["crisis_risk"] is False

    def test_framework_suitability_calculation(self, integration_system):
        """Test framework suitability scoring."""
        user_context = {
            "therapeutic_goals": ["anxiety_management", "confidence_building"],
            "character_strengths": ["courage", "wisdom"],
            "crisis_risk": False,
            "emotional_stability": 0.7,
            "preferred_frameworks": ["cognitive_behavioral_therapy"],
        }

        scores = integration_system._calculate_framework_suitability(user_context)

        # Should return scores for all frameworks
        assert len(scores) == len(TherapeuticFramework)

        # All scores should be between 0 and 1
        for score in scores.values():
            assert 0.0 <= score <= 1.0

        # CBT should have high score due to goal alignment and preference
        assert scores[TherapeuticFramework.CBT] > 0.7

    def test_scenario_type_determination(self, integration_system):
        """Test scenario type determination logic."""
        # Test direct goal mapping
        scenario_type = integration_system._determine_scenario_type(
            ["anxiety_management"], TherapeuticFramework.CBT
        )
        assert scenario_type == ScenarioType.ANXIETY_MANAGEMENT

        # Test framework default
        scenario_type = integration_system._determine_scenario_type(
            ["unknown_goal"], TherapeuticFramework.DBT
        )
        assert scenario_type == ScenarioType.EMOTIONAL_REGULATION

    def test_integration_strategy_determination(self, integration_system):
        """Test integration strategy determination."""
        # Test crisis situation
        crisis_context = {"crisis_risk": True, "emotional_stability": 0.3}
        strategy = integration_system._determine_integration_strategy(
            crisis_context, TherapeuticFramework.CBT
        )
        assert strategy == IntegrationStrategy.DIRECT_TEACHING

        # Test normal situation
        normal_context = {"crisis_risk": False, "emotional_stability": 0.7}
        strategy = integration_system._determine_integration_strategy(
            normal_context, TherapeuticFramework.CBT
        )
        assert strategy == IntegrationStrategy.SKILL_PRACTICE

    def test_character_alignment_calculation(self, integration_system):
        """Test character attribute alignment calculation."""
        user_context = {
            "character_strengths": ["self_awareness", "wisdom", "courage"]
        }

        alignment = integration_system._calculate_character_alignment(
            user_context, TherapeuticFramework.CBT
        )

        # Should return alignment scores
        assert isinstance(alignment, dict)

        # CBT attributes should have alignment scores
        cbt_attributes = integration_system.framework_configurations[TherapeuticFramework.CBT]["character_attributes"]
        for attr in cbt_attributes:
            assert attr in alignment
            assert 0.0 <= alignment[attr] <= 1.0

    def test_duration_estimation(self, integration_system):
        """Test duration estimation for scenarios."""
        # Test different scenario types
        anxiety_duration = integration_system._estimate_duration(
            TherapeuticFramework.CBT, ScenarioType.ANXIETY_MANAGEMENT
        )
        assert anxiety_duration > 0

        depression_duration = integration_system._estimate_duration(
            TherapeuticFramework.DBT, ScenarioType.DEPRESSION_SUPPORT
        )
        assert depression_duration > 0

        # DBT should generally take longer than CBT
        assert depression_duration >= anxiety_duration

    @pytest.mark.asyncio
    async def test_health_check(self, integration_system):
        """Test system health check."""
        await integration_system.initialize()

        health = await integration_system.health_check()

        assert "status" in health
        assert health["status"] == "healthy"
        assert "frameworks_supported" in health
        assert health["frameworks_supported"] >= 8
        assert "integration_strategies" in health
        assert health["integration_strategies"] == 8
        assert "scenario_types" in health
        assert health["scenario_types"] >= 5

    def test_get_metrics(self, integration_system):
        """Test metrics collection."""
        metrics = integration_system.get_metrics()

        assert isinstance(metrics, dict)
        assert "recommendations_generated" in metrics
        assert "scenarios_created" in metrics
        assert "frameworks_integrated" in metrics
        assert "frameworks_supported" in metrics
        assert metrics["frameworks_supported"] >= 8

    @pytest.mark.asyncio
    async def test_error_handling(self, integration_system):
        """Test error handling in integration operations."""
        await integration_system.initialize()

        # Test with invalid input
        recommendations = await integration_system.generate_personalized_recommendations(
            user_id="",  # Empty user ID
            therapeutic_goals=None
        )

        # Should handle gracefully and return recommendations
        assert len(recommendations) >= 1
        assert isinstance(recommendations[0], TherapeuticRecommendation)
        # Should include mindfulness as a gentle framework option
        framework_names = [rec.framework for rec in recommendations]
        assert TherapeuticFramework.MINDFULNESS in framework_names

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, integration_system):
        """Test compatibility with E2E test interface expectations."""
        await integration_system.initialize()

        # Test recommendation generation (E2E interface)
        recommendations = await integration_system.generate_personalized_recommendations(
            user_id="demo_user_001",
            therapeutic_goals=["confidence_building", "anxiety_management"]
        )

        # Should match expected structure
        assert len(recommendations) > 0
        for rec in recommendations:
            assert hasattr(rec, "framework")
            assert hasattr(rec, "scenario_type")
            assert hasattr(rec, "priority_score")
            assert hasattr(rec, "rationale")

        # Test scenario creation (E2E interface)
        scenario = await integration_system.create_therapeutic_scenario(
            user_id="demo_user_001",
            framework=TherapeuticFramework.CBT,
            scenario_type=ScenarioType.CONFIDENCE_BUILDING
        )

        # Should match expected structure
        assert hasattr(scenario, "title")
        assert hasattr(scenario, "description")
        assert hasattr(scenario, "therapeutic_goals")
        assert hasattr(scenario, "practice_opportunities")
