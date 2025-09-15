"""
Tests for TherapeuticConsequenceSystem

This module tests the therapeutic consequence system implementation
that bridges the core consequence system with the E2E test interface.
"""

import pytest

from src.components.therapeutic_systems.consequence_system import (
    TherapeuticApproach,
    TherapeuticConsequenceSystem,
)


class TestTherapeuticConsequenceSystem:
    """Test TherapeuticConsequenceSystem functionality."""

    @pytest.fixture
    def consequence_system(self):
        """Create therapeutic consequence system instance."""
        return TherapeuticConsequenceSystem()

    @pytest.mark.asyncio
    async def test_initialization(self, consequence_system):
        """Test system initialization."""
        await consequence_system.initialize()

        # Should have therapeutic frameworks configured
        assert len(consequence_system.therapeutic_frameworks) > 0
        assert TherapeuticApproach.CBT in consequence_system.therapeutic_frameworks
        assert TherapeuticApproach.DBT in consequence_system.therapeutic_frameworks

        # Should have attribute mappings
        assert len(consequence_system.attribute_mappings) > 0
        assert "courage" in consequence_system.attribute_mappings
        assert "wisdom" in consequence_system.attribute_mappings

    @pytest.mark.asyncio
    async def test_process_choice_consequence_basic(self, consequence_system):
        """Test basic choice consequence processing."""
        await consequence_system.initialize()

        result = await consequence_system.process_choice_consequence(
            user_id="test_user_001",
            choice="I choose to approach the situation with confidence",
            scenario_context={"type": "social_anxiety", "difficulty": "moderate"},
            therapeutic_goals=["confidence_building", "anxiety_management"],
        )

        # Should return expected structure
        assert "consequence_id" in result
        assert "therapeutic_value" in result
        assert "learning_opportunity" in result
        assert "character_impact" in result

        # Should have reasonable values
        assert 0.0 <= result["therapeutic_value"] <= 1.0
        assert isinstance(result["learning_opportunity"], str)
        assert len(result["learning_opportunity"]) > 0
        assert isinstance(result["character_impact"], dict)
        assert len(result["character_impact"]) > 0

    @pytest.mark.asyncio
    async def test_therapeutic_value_calculation(self, consequence_system):
        """Test therapeutic value calculation for different choices."""
        await consequence_system.initialize()

        # Test high therapeutic value choice
        high_value_result = await consequence_system.process_choice_consequence(
            user_id="test_user_002",
            choice="I will practice deep breathing and face my fears with courage",
            scenario_context={"type": "therapeutic", "emotional_intensity": "high"},
            therapeutic_goals=["anxiety_management", "confidence_building"],
        )

        # Test neutral choice
        neutral_result = await consequence_system.process_choice_consequence(
            user_id="test_user_003",
            choice="I will think about this later",
            scenario_context={"type": "narrative"},
            therapeutic_goals=[],
        )

        # High therapeutic value choice should score higher
        assert (
            high_value_result["therapeutic_value"]
            >= neutral_result["therapeutic_value"]
        )

    @pytest.mark.asyncio
    async def test_character_impact_calculation(self, consequence_system):
        """Test character attribute impact calculation."""
        await consequence_system.initialize()

        # Test courage-building choice
        courage_result = await consequence_system.process_choice_consequence(
            user_id="test_user_004",
            choice="I will be brave and confront this challenge head-on",
            scenario_context={"type": "challenge"},
            therapeutic_goals=["confidence_building"],
        )

        # Should impact courage attribute
        assert (
            "courage" in courage_result["character_impact"]
            or "resilience" in courage_result["character_impact"]
        )

        # Test wisdom-building choice
        wisdom_result = await consequence_system.process_choice_consequence(
            user_id="test_user_005",
            choice="I need to think carefully and learn from this experience",
            scenario_context={"type": "learning"},
            therapeutic_goals=["personal_growth"],
        )

        # Should impact wisdom or related attributes
        assert any(
            attr in wisdom_result["character_impact"]
            for attr in ["wisdom", "resilience"]
        )

    @pytest.mark.asyncio
    async def test_therapeutic_framework_application(self, consequence_system):
        """Test application of different therapeutic frameworks."""
        await consequence_system.initialize()

        # Test CBT framework application
        cbt_result = await consequence_system.process_choice_consequence(
            user_id="test_user_006",
            choice="I will examine my thoughts and challenge negative thinking",
            scenario_context={"type": "cognitive"},
            therapeutic_goals=["cognitive_restructuring"],
            user_preferences={"preferred_approaches": [TherapeuticApproach.CBT]},
        )

        # Should include CBT-specific learning opportunity
        assert (
            "CBT" in cbt_result["learning_opportunity"]
            or "thought" in cbt_result["learning_opportunity"].lower()
        )

        # Test DBT framework application
        dbt_result = await consequence_system.process_choice_consequence(
            user_id="test_user_007",
            choice="I will practice mindfulness and regulate my emotions",
            scenario_context={"type": "emotional"},
            therapeutic_goals=["emotion_regulation"],
            user_preferences={"preferred_approaches": [TherapeuticApproach.DBT]},
        )

        # Should include DBT-specific learning opportunity
        assert (
            "DBT" in dbt_result["learning_opportunity"]
            or "mindfulness" in dbt_result["learning_opportunity"].lower()
        )

    @pytest.mark.asyncio
    async def test_learning_opportunity_generation(self, consequence_system):
        """Test learning opportunity text generation."""
        await consequence_system.initialize()

        result = await consequence_system.process_choice_consequence(
            user_id="test_user_008",
            choice="I will try a new approach to this problem",
            scenario_context={"type": "problem_solving"},
            therapeutic_goals=["problem_solving_skills", "adaptability"],
        )

        learning_opportunity = result["learning_opportunity"]

        # Should be meaningful text
        assert isinstance(learning_opportunity, str)
        assert len(learning_opportunity) > 20  # Should be substantial
        assert any(
            word in learning_opportunity.lower()
            for word in ["learn", "grow", "practice", "develop", "skill"]
        )

    @pytest.mark.asyncio
    async def test_error_handling(self, consequence_system):
        """Test error handling in consequence processing."""
        await consequence_system.initialize()

        # Test with minimal/invalid input
        result = await consequence_system.process_choice_consequence(
            user_id="",  # Empty user ID
            choice="",  # Empty choice
            scenario_context=None,
            therapeutic_goals=None,
        )

        # Should handle gracefully and return valid structure
        assert "consequence_id" in result
        assert "therapeutic_value" in result
        assert "learning_opportunity" in result
        assert "character_impact" in result

        # Should have fallback values
        assert result["therapeutic_value"] == 0.5  # Neutral value
        assert len(result["learning_opportunity"]) > 0
        assert len(result["character_impact"]) > 0

    @pytest.mark.asyncio
    async def test_health_check(self, consequence_system):
        """Test system health check."""
        await consequence_system.initialize()

        health = await consequence_system.health_check()

        assert "status" in health
        assert health["status"] == "healthy"
        assert "therapeutic_system" in health
        assert "therapeutic_frameworks" in health
        assert health["therapeutic_frameworks"] > 0

    def test_get_metrics(self, consequence_system):
        """Test metrics collection."""
        metrics = consequence_system.get_metrics()

        assert isinstance(metrics, dict)
        assert "therapeutic_frameworks_available" in metrics
        assert "attribute_mappings_configured" in metrics
        assert metrics["therapeutic_frameworks_available"] > 0
        assert metrics["attribute_mappings_configured"] > 0

    @pytest.mark.asyncio
    async def test_choice_type_determination(self, consequence_system):
        """Test choice type determination logic."""
        await consequence_system.initialize()

        # Test therapeutic choice
        therapeutic_result = await consequence_system.process_choice_consequence(
            user_id="test_user_009",
            choice="I will use my coping strategies",
            scenario_context={"type": "therapeutic"},
            therapeutic_goals=["coping_skills"],
        )

        assert "choice_analysis" in therapeutic_result
        assert "choice_type" in therapeutic_result["choice_analysis"]

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, consequence_system):
        """Test compatibility with E2E test interface expectations."""
        await consequence_system.initialize()

        # Test with parameters matching E2E test expectations
        result = await consequence_system.process_choice_consequence(
            user_id="demo_user_001",
            choice="approach_with_confidence",
            scenario_context={"type": "social_anxiety", "difficulty": "moderate"},
        )

        # Should match E2E test expected structure
        expected_keys = [
            "consequence_id",
            "therapeutic_value",
            "learning_opportunity",
            "character_impact",
        ]
        for key in expected_keys:
            assert key in result

        # Should have reasonable therapeutic value (E2E tests expect > 0.5)
        assert result["therapeutic_value"] > 0.5

        # Should have character impact (E2E tests expect this structure)
        assert isinstance(result["character_impact"], dict)
        assert len(result["character_impact"]) > 0

        # Values should be reasonable floats
        for _attr, value in result["character_impact"].items():
            assert isinstance(value, int | float)
            assert -1.0 <= value <= 1.0  # Reasonable range for attribute changes
