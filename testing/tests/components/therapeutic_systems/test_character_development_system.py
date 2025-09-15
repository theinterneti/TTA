"""
Tests for TherapeuticCharacterDevelopmentSystem

This module tests the therapeutic character development system implementation
including character creation, attribute progression, and milestone achievements.
"""


import pytest

from src.components.therapeutic_systems.character_development_system import (
    CharacterAttributes,
    MilestoneType,
    TherapeuticAttribute,
    TherapeuticCharacter,
    TherapeuticCharacterDevelopmentSystem,
    TherapeuticMilestone,
)


class TestTherapeuticCharacterDevelopmentSystem:
    """Test TherapeuticCharacterDevelopmentSystem functionality."""

    @pytest.fixture
    def character_system(self):
        """Create therapeutic character development system instance."""
        return TherapeuticCharacterDevelopmentSystem()

    @pytest.mark.asyncio
    async def test_initialization(self, character_system):
        """Test system initialization."""
        await character_system.initialize()

        # Should have therapeutic attributes configured
        assert len(TherapeuticAttribute) == 12  # 12 therapeutic attributes

        # Should have milestone types configured
        assert len(MilestoneType) == 8  # 8 milestone types

        # Should have framework mappings
        assert len(character_system.framework_attribute_mappings) > 0
        assert "CBT" in character_system.framework_attribute_mappings
        assert "DBT" in character_system.framework_attribute_mappings

        # Should have milestone templates
        assert len(character_system.milestone_templates) > 0

    @pytest.mark.asyncio
    async def test_create_character_basic(self, character_system):
        """Test basic character creation."""
        await character_system.initialize()

        character = await character_system.create_character(
            user_id="test_user_001",
            session_id="test_session_001"
        )

        # Should return valid character
        assert isinstance(character, TherapeuticCharacter)
        assert character.user_id == "test_user_001"
        assert character.character_id.startswith("char_test_user_001_")
        assert character.name == "Therapeutic Character"  # Default name

        # Should have default attributes (all 5.0)
        attributes_dict = character.attributes.to_dict()
        assert len(attributes_dict) == 12  # All 12 attributes
        for attr_value in attributes_dict.values():
            assert attr_value == 5.0  # Default value

    @pytest.mark.asyncio
    async def test_create_character_with_therapeutic_goals(self, character_system):
        """Test character creation with therapeutic goals."""
        await character_system.initialize()

        therapeutic_goals = ["anxiety_management", "confidence_building"]

        character = await character_system.create_character(
            user_id="test_user_002",
            session_id="test_session_002",
            therapeutic_goals=therapeutic_goals
        )

        # Should have therapeutic goals
        assert character.therapeutic_goals == therapeutic_goals

        # Should have goal-aligned name
        assert character.name == "Serenity"  # anxiety_management -> Serenity

        # Should have boosted attributes based on goals
        attributes_dict = character.attributes.to_dict()

        # Anxiety management should boost mindfulness, resilience, self_awareness
        assert attributes_dict["mindfulness"] > 5.0
        assert attributes_dict["resilience"] > 5.0
        assert attributes_dict["self_awareness"] > 5.0

        # Confidence building should boost courage, confidence, resilience
        assert attributes_dict["courage"] > 5.0
        assert attributes_dict["confidence"] > 5.0

    @pytest.mark.asyncio
    async def test_create_character_with_initial_attributes(self, character_system):
        """Test character creation with initial attributes."""
        await character_system.initialize()

        initial_attributes = {
            "courage": 7.5,
            "wisdom": 8.0,
            "compassion": 6.5,
        }

        character = await character_system.create_character(
            user_id="test_user_003",
            initial_attributes=initial_attributes
        )

        # Should use provided initial attributes
        assert character.attributes.courage == 7.5
        assert character.attributes.wisdom == 8.0
        assert character.attributes.compassion == 6.5

        # Other attributes should remain default
        assert character.attributes.resilience == 5.0

    def test_character_attributes_functionality(self, character_system):
        """Test CharacterAttributes class functionality."""
        attributes = CharacterAttributes()

        # Test default values
        assert attributes.courage == 5.0
        assert attributes.wisdom == 5.0

        # Test to_dict conversion
        attr_dict = attributes.to_dict()
        assert len(attr_dict) == 12
        assert attr_dict["courage"] == 5.0

        # Test get_attribute
        assert attributes.get_attribute(TherapeuticAttribute.COURAGE) == 5.0

        # Test set_attribute with clamping
        attributes.set_attribute(TherapeuticAttribute.COURAGE, 15.0)  # Should clamp to 10.0
        assert attributes.get_attribute(TherapeuticAttribute.COURAGE) == 10.0

        attributes.set_attribute(TherapeuticAttribute.WISDOM, -5.0)  # Should clamp to 0.0
        assert attributes.get_attribute(TherapeuticAttribute.WISDOM) == 0.0

    def test_therapeutic_goal_bonuses(self, character_system):
        """Test therapeutic goal bonus calculations."""
        # Test anxiety management bonuses
        bonuses = character_system._calculate_therapeutic_goal_bonuses(["anxiety_management"])
        assert "mindfulness" in bonuses
        assert "resilience" in bonuses
        assert "self_awareness" in bonuses
        assert bonuses["mindfulness"] == 1.0

        # Test multiple goals accumulation
        bonuses = character_system._calculate_therapeutic_goal_bonuses(
            ["anxiety_management", "confidence_building"]
        )
        # Resilience should get bonuses from both goals
        assert bonuses["resilience"] == 0.8 + 0.5  # From both goals

    def test_character_name_generation(self, character_system):
        """Test character name generation based on therapeutic goals."""
        # Test specific goal names
        assert character_system._generate_character_name(["anxiety_management"]) == "Serenity"
        assert character_system._generate_character_name(["confidence_building"]) == "Valor"
        assert character_system._generate_character_name(["mindfulness"]) == "Zen"

        # Test unknown goal
        assert character_system._generate_character_name(["unknown_goal"]) == "Journey"

        # Test no goals
        assert character_system._generate_character_name([]) == "Therapeutic Character"
        assert character_system._generate_character_name(None) == "Therapeutic Character"

    @pytest.mark.asyncio
    async def test_process_therapeutic_consequence(self, character_system):
        """Test processing therapeutic consequences for character development."""
        await character_system.initialize()

        # Create character first
        character = await character_system.create_character(
            user_id="test_user_004",
            therapeutic_goals=["confidence_building"]
        )

        # Process consequence with character impact
        consequence_data = {
            "character_impact": {
                "courage": 2.0,
                "confidence": 1.5,
                "resilience": 1.0,
            },
            "therapeutic_value": 2.5,
            "consequence_type": "positive_choice",
        }

        result = await character_system.process_therapeutic_consequence(
            user_id="test_user_004",
            consequence_data=consequence_data,
            session_context={"session_id": "test_session"}
        )

        # Should return processing results
        assert result["character_id"] == character.character_id
        assert "attribute_changes" in result
        assert "total_therapeutic_value" in result

        # Should have applied attribute changes (capture original values first)
        original_courage = 6.2  # confidence_building gives courage bonus of 1.2
        original_confidence = 6.0  # confidence_building gives confidence bonus of 1.0

        updated_character = character_system.characters["test_user_004"]
        assert updated_character.attributes.courage > original_courage
        assert updated_character.attributes.confidence > original_confidence

        # Should have updated therapeutic value
        assert updated_character.total_therapeutic_value == 2.5

    @pytest.mark.asyncio
    async def test_milestone_achievement(self, character_system):
        """Test milestone achievement detection."""
        await character_system.initialize()

        # Create character
        await character_system.create_character(
            user_id="test_user_005",
            therapeutic_goals=["self_awareness"]
        )

        # Process consequence with high therapeutic value (should trigger milestone)
        consequence_data = {
            "character_impact": {
                "self_awareness": 3.0,
                "wisdom": 2.0,
            },
            "therapeutic_value": 3.5,  # Above milestone threshold
            "consequence_type": "breakthrough_moment",
        }

        result = await character_system.process_therapeutic_consequence(
            user_id="test_user_005",
            consequence_data=consequence_data
        )

        # Should have achieved milestone
        assert result["milestone_achieved"] is not None

        # Character should have milestone recorded
        updated_character = character_system.characters["test_user_005"]
        assert len(updated_character.milestones) == 1

        milestone = updated_character.milestones[0]
        assert isinstance(milestone, TherapeuticMilestone)
        assert milestone.milestone_type == MilestoneType.THERAPEUTIC_BREAKTHROUGH

    def test_milestone_type_determination(self, character_system):
        """Test milestone type determination logic."""
        # Test self-awareness -> therapeutic breakthrough
        milestone_type = character_system._determine_milestone_type(
            {"self_awareness": 2.0, "wisdom": 1.0}, 3.0
        )
        assert milestone_type == MilestoneType.THERAPEUTIC_BREAKTHROUGH

        # Test confidence -> confidence building
        milestone_type = character_system._determine_milestone_type(
            {"confidence": 2.5}, 2.5
        )
        assert milestone_type == MilestoneType.CONFIDENCE_BUILDING

        # Test high therapeutic value -> therapeutic breakthrough
        milestone_type = character_system._determine_milestone_type(
            {"communication": 1.0}, 3.5
        )
        assert milestone_type == MilestoneType.THERAPEUTIC_BREAKTHROUGH

        # Test no positive changes
        milestone_type = character_system._determine_milestone_type(
            {"courage": -1.0}, 2.0
        )
        assert milestone_type is None

    def test_alignment_bonus_calculation(self, character_system):
        """Test therapeutic alignment bonus calculation."""
        # Test aligned attribute gets bonus
        bonus = character_system._calculate_alignment_bonus(
            "mindfulness", ["anxiety_management", "mindfulness"]
        )
        assert bonus > 0.0

        # Test non-aligned attribute gets no bonus
        bonus = character_system._calculate_alignment_bonus(
            "courage", ["anxiety_management"]
        )
        assert bonus == 0.0

        # Test no goals
        bonus = character_system._calculate_alignment_bonus("mindfulness", [])
        assert bonus == 0.0

    @pytest.mark.asyncio
    async def test_get_character_summary(self, character_system):
        """Test character summary generation."""
        await character_system.initialize()

        # Create character with some progression
        await character_system.create_character(
            user_id="test_user_006",
            therapeutic_goals=["confidence_building"]
        )

        # Add some progression
        await character_system.process_therapeutic_consequence(
            user_id="test_user_006",
            consequence_data={
                "character_impact": {"courage": 2.0, "confidence": 1.5},
                "therapeutic_value": 3.0,
            }
        )

        summary = await character_system.get_character_summary("test_user_006")

        # Should contain expected summary fields
        assert "character_id" in summary
        assert "name" in summary
        assert "overall_level" in summary
        assert "attributes" in summary
        assert "top_attributes" in summary
        assert "milestone_count" in summary
        assert "therapeutic_goals" in summary

        # Should have calculated overall level
        assert isinstance(summary["overall_level"], float)
        assert summary["overall_level"] > 0

        # Should have top attributes
        assert len(summary["top_attributes"]) == 3
        assert all("name" in attr and "value" in attr for attr in summary["top_attributes"])

    @pytest.mark.asyncio
    async def test_character_summary_no_character(self, character_system):
        """Test character summary for non-existent character."""
        await character_system.initialize()

        summary = await character_system.get_character_summary("nonexistent_user")

        assert "error" in summary
        assert summary["error"] == "No character found for user"

    def test_progression_rate_calculation(self, character_system):
        """Test progression rate calculation."""
        # Create character with progression events
        character = TherapeuticCharacter(
            character_id="test_char",
            user_id="test_user",
            name="Test Character",
            attributes=CharacterAttributes(),
        )

        # Add progression events with therapeutic values
        from datetime import datetime, timedelta

        from src.components.therapeutic_systems.character_development_system import (
            CharacterProgressionEvent,
        )

        recent_event = CharacterProgressionEvent(
            event_id="event1",
            character_id="test_char",
            event_type="test",
            attribute_changes={},
            milestone_achieved=None,
            therapeutic_context={"therapeutic_value": 2.5},
            timestamp=datetime.utcnow() - timedelta(days=1),
        )

        character.progression_events = [recent_event]

        rate = character_system._calculate_progression_rate(character)
        assert rate == 2.5

        # Test no events
        character.progression_events = []
        rate = character_system._calculate_progression_rate(character)
        assert rate == 0.0

    @pytest.mark.asyncio
    async def test_health_check(self, character_system):
        """Test system health check."""
        await character_system.initialize()

        health = await character_system.health_check()

        assert "status" in health
        assert health["status"] == "healthy"
        assert "characters_tracked" in health
        assert "therapeutic_attributes" in health
        assert health["therapeutic_attributes"] == 12
        assert "milestone_types" in health
        assert health["milestone_types"] == 8

    def test_get_metrics(self, character_system):
        """Test metrics collection."""
        metrics = character_system.get_metrics()

        assert isinstance(metrics, dict)
        assert "characters_created" in metrics
        assert "milestones_achieved" in metrics
        assert "attribute_progressions" in metrics
        assert "therapeutic_attributes_available" in metrics
        assert metrics["therapeutic_attributes_available"] == 12

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, character_system):
        """Test compatibility with E2E test interface expectations."""
        await character_system.initialize()

        # Test create_character method (E2E interface)
        character = await character_system.create_character(
            user_id="demo_user_001",
            session_id="demo_session_001",
            therapeutic_goals=["confidence_building"]
        )

        # Should match E2E test expected structure
        assert hasattr(character, "character_id")
        assert hasattr(character, "attributes")
        assert hasattr(character.attributes, "courage")
        assert hasattr(character.attributes, "wisdom")
        assert hasattr(character.attributes, "compassion")

        # Attributes should be accessible as expected by E2E tests
        attributes_dict = character.attributes.to_dict()
        assert "courage" in attributes_dict
        assert "wisdom" in attributes_dict
        assert "compassion" in attributes_dict

    @pytest.mark.asyncio
    async def test_error_handling(self, character_system):
        """Test error handling in character development operations."""
        await character_system.initialize()

        # Test processing consequence for non-existent user (should create character)
        result = await character_system.process_therapeutic_consequence(
            user_id="new_user",
            consequence_data={"character_impact": {"courage": 1.0}, "therapeutic_value": 1.0}
        )

        # Should handle gracefully by creating character
        assert "error" not in result
        assert result["character_id"] is not None

        # Should have created character
        assert "new_user" in character_system.characters
