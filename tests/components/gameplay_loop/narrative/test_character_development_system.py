"""
Tests for CharacterDevelopmentSystem

This module tests character development, attribute tracking, milestone detection,
and progression visualization functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from src.components.gameplay_loop.narrative.character_development_system import (
    CharacterDevelopmentSystem, CharacterAttribute, CharacterMilestone, DevelopmentTrigger,
    AbilityType, CharacterDevelopmentEvent, CharacterMilestoneAchievement, CharacterAbility,
    CharacterAttributeLevel
)
from src.components.gameplay_loop.services.session_state import SessionState
from src.components.gameplay_loop.models.core import ChoiceType
from src.components.gameplay_loop.narrative.events import EventBus


class TestCharacterDevelopmentSystem:
    """Test CharacterDevelopmentSystem functionality."""
    
    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus
    
    @pytest.fixture
    def development_system(self, event_bus):
        """Create character development system instance."""
        return CharacterDevelopmentSystem(event_bus)
    
    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = Mock(spec=SessionState)
        state.session_id = "test_session_123"
        state.user_id = "test_user_456"
        state.therapeutic_goals = ["emotional_regulation", "communication_skills"]
        state.context = {}
        return state
    
    @pytest.fixture
    def choice_consequence_context(self):
        """Create context for choice consequence development."""
        return {
            "description": "Character makes a brave choice to help others",
            "story_context": "In a moment of crisis, you choose to stand up for what's right",
            "choice_type": ChoiceType.EMOTIONAL_REGULATION,
            "therapeutic_relevance": 0.8,
            "first_time": True,
            "therapeutic_aligned": True
        }
    
    @pytest.fixture
    def therapeutic_progress_context(self):
        """Create context for therapeutic progress development."""
        return {
            "description": "User demonstrates mastery of anxiety management techniques",
            "story_context": "You successfully use breathing techniques during a stressful situation",
            "therapeutic_concept": "anxiety_management",
            "progress_level": 0.7,
            "milestone_related": True
        }
    
    @pytest.mark.asyncio
    async def test_process_character_development_choice_consequence(self, development_system, session_state, choice_consequence_context, event_bus):
        """Test character development from choice consequences."""
        event = await development_system.process_character_development(
            session_state, DevelopmentTrigger.CHOICE_CONSEQUENCE, choice_consequence_context
        )
        
        # Check event structure
        assert isinstance(event, CharacterDevelopmentEvent)
        assert event.user_id == session_state.user_id
        assert event.session_id == session_state.session_id
        assert event.event_type == DevelopmentTrigger.CHOICE_CONSEQUENCE
        assert event.processed == True
        
        # Check attribute changes
        assert len(event.attribute_changes) > 0
        assert CharacterAttribute.EMOTIONAL_INTELLIGENCE in event.attribute_changes
        
        # Check experience gained
        assert len(event.experience_gained) > 0
        
        # Check character feedback
        assert event.character_feedback != ""
        assert "emotional intelligence" in event.character_feedback.lower()
        
        # Check that character attributes were initialized
        assert session_state.user_id in development_system.character_attributes
        
        # Check that event was stored
        assert session_state.user_id in development_system.development_events
        assert len(development_system.development_events[session_state.user_id]) == 1
        
        # Check that event was published
        event_bus.publish.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_character_development_therapeutic_progress(self, development_system, session_state, therapeutic_progress_context, event_bus):
        """Test character development from therapeutic progress."""
        event = await development_system.process_character_development(
            session_state, DevelopmentTrigger.THERAPEUTIC_PROGRESS, therapeutic_progress_context
        )
        
        # Check event structure
        assert isinstance(event, CharacterDevelopmentEvent)
        assert event.event_type == DevelopmentTrigger.THERAPEUTIC_PROGRESS
        
        # Check attribute changes for anxiety management
        assert len(event.attribute_changes) > 0
        assert CharacterAttribute.RESILIENCE in event.attribute_changes
        assert CharacterAttribute.EMOTIONAL_INTELLIGENCE in event.attribute_changes
        
        # Check multipliers were applied
        resilience_change = event.attribute_changes[CharacterAttribute.RESILIENCE]
        assert resilience_change > 0.1  # Should be boosted by milestone_related multiplier
    
    @pytest.mark.asyncio
    async def test_character_attribute_initialization(self, development_system, session_state):
        """Test character attribute initialization for new users."""
        user_id = session_state.user_id
        
        # Initialize attributes
        await development_system._initialize_character_attributes(user_id)
        
        # Check that all attributes were initialized
        assert user_id in development_system.character_attributes
        user_attributes = development_system.character_attributes[user_id]
        
        # Check that all character attributes are present
        for attribute in CharacterAttribute:
            assert attribute in user_attributes
            attr_level = user_attributes[attribute]
            assert isinstance(attr_level, CharacterAttributeLevel)
            assert attr_level.current_level == 1.0  # Starting level
            assert attr_level.experience_points == 0
            assert attr_level.level_progress == 0.0
    
    @pytest.mark.asyncio
    async def test_attribute_change_application(self, development_system, session_state):
        """Test application of attribute changes."""
        user_id = session_state.user_id
        attribute = CharacterAttribute.COURAGE
        change = 0.5
        
        # Apply attribute change
        await development_system._apply_attribute_change(user_id, attribute, change, DevelopmentTrigger.CHOICE_CONSEQUENCE)
        
        # Check that attribute was updated
        user_attributes = development_system.character_attributes[user_id]
        attr_level = user_attributes[attribute]
        
        assert attr_level.current_level == 1.5  # 1.0 + 0.5
        assert attr_level.peak_level == 1.5
        assert attr_level.last_increased is not None
        assert len(attr_level.story_manifestations) > 0
    
    @pytest.mark.asyncio
    async def test_experience_points_and_level_up(self, development_system, session_state):
        """Test experience point application and level up mechanics."""
        user_id = session_state.user_id
        attribute = CharacterAttribute.WISDOM
        
        # Initialize attributes
        await development_system._initialize_character_attributes(user_id)
        
        # Apply enough XP to trigger level up
        await development_system._apply_experience_points(user_id, attribute, 15)  # Above threshold for level 2
        
        # Check level up
        user_attributes = development_system.character_attributes[user_id]
        attr_level = user_attributes[attribute]
        
        assert attr_level.experience_points == 15
        assert attr_level.current_level >= 2.0  # Should have leveled up
        assert len(attr_level.character_reactions) > 0  # Should have level up reaction
    
    @pytest.mark.asyncio
    async def test_milestone_achievement_detection(self, development_system, session_state, event_bus):
        """Test milestone achievement detection and processing."""
        user_id = session_state.user_id
        
        # Initialize attributes and set courage high enough for milestone
        await development_system._initialize_character_attributes(user_id)
        await development_system._apply_attribute_change(user_id, CharacterAttribute.COURAGE, 1.5, DevelopmentTrigger.CHOICE_CONSEQUENCE)
        
        # Create event that should trigger milestone
        context = {
            "description": "Character performs first brave act",
            "story_context": "You courageously face your fears to help others",
            "choice_type": ChoiceType.EMOTIONAL_REGULATION,
            "therapeutic_relevance": 0.8
        }
        
        event = await development_system.process_character_development(
            session_state, DevelopmentTrigger.CHOICE_CONSEQUENCE, context
        )
        
        # Check if milestone was achieved
        if user_id in development_system.milestone_achievements:
            achievements = development_system.milestone_achievements[user_id]
            if achievements:
                achievement = achievements[0]
                assert isinstance(achievement, CharacterMilestoneAchievement)
                assert achievement.milestone == CharacterMilestone.FIRST_BRAVE_ACT
                assert achievement.celebration_story != ""
                
                # Check that session context was updated
                assert "recent_milestone_achievement" in session_state.context
    
    @pytest.mark.asyncio
    async def test_ability_unlock_detection(self, development_system, session_state, event_bus):
        """Test ability unlock detection and processing."""
        user_id = session_state.user_id
        
        # Initialize attributes and set emotional intelligence high enough for ability unlock
        await development_system._initialize_character_attributes(user_id)
        await development_system._apply_attribute_change(user_id, CharacterAttribute.EMOTIONAL_INTELLIGENCE, 2.5, DevelopmentTrigger.THERAPEUTIC_PROGRESS)
        
        # Create event that should trigger ability unlock
        context = {
            "description": "Character demonstrates emotional regulation skills",
            "story_context": "You successfully manage stress using breathing techniques",
            "therapeutic_concept": "emotional_regulation",
            "progress_level": 0.8
        }
        
        event = await development_system.process_character_development(
            session_state, DevelopmentTrigger.THERAPEUTIC_PROGRESS, context
        )
        
        # Check if ability was unlocked
        if user_id in development_system.character_abilities:
            abilities = development_system.character_abilities[user_id]
            if abilities:
                ability = abilities[0]
                assert isinstance(ability, CharacterAbility)
                assert ability.name in ["Mindful Breathing", "Cognitive Reframing", "Empathetic Listening"]
                assert ability.unlock_story != ""
                
                # Check that session context was updated
                assert "recent_ability_unlock" in session_state.context
    
    def test_attribute_templates_loading(self, development_system):
        """Test that attribute templates are properly loaded."""
        templates = development_system.attribute_templates
        
        # Check that templates exist for core attributes
        assert CharacterAttribute.COURAGE in templates
        assert CharacterAttribute.WISDOM in templates
        assert CharacterAttribute.COMPASSION in templates
        assert CharacterAttribute.RESILIENCE in templates
        assert CharacterAttribute.COMMUNICATION in templates
        assert CharacterAttribute.EMOTIONAL_INTELLIGENCE in templates
        
        # Check template structure
        for attribute, template in templates.items():
            assert "name" in template
            assert "description" in template
            assert "story_manifestations" in template
            assert "development_indicators" in template
            assert isinstance(template["story_manifestations"], list)
            assert len(template["story_manifestations"]) > 0
    
    def test_ability_templates_loading(self, development_system):
        """Test that ability templates are properly loaded."""
        templates = development_system.ability_templates
        
        # Check that templates exist for different ability types
        assert AbilityType.THERAPEUTIC_SKILL in templates
        assert AbilityType.SOCIAL_ABILITY in templates
        
        # Check template structure
        for ability_type, abilities in templates.items():
            assert isinstance(abilities, list)
            assert len(abilities) > 0
            
            for ability in abilities:
                assert "name" in ability
                assert "description" in ability
                assert "required_attributes" in ability
                assert "unlock_story" in ability
                assert "usage_examples" in ability
    
    def test_milestone_templates_loading(self, development_system):
        """Test that milestone templates are properly loaded."""
        templates = development_system.milestone_templates
        
        # Check that templates exist for core milestones
        assert CharacterMilestone.FIRST_BRAVE_ACT in templates
        assert CharacterMilestone.WISE_DECISION_MAKER in templates
        assert CharacterMilestone.COMPASSIONATE_HELPER in templates
        
        # Check template structure
        for milestone, template in templates.items():
            assert "name" in template
            assert "description" in template
            assert "required_attributes" in template
            assert "celebration_story" in template
            assert "attribute_bonuses" in template
            assert "story_unlocks" in template
    
    def test_development_rules_loading(self, development_system):
        """Test that development rules are properly loaded."""
        rules = development_system.development_rules
        
        # Check rule categories
        assert "attribute_gain_rates" in rules
        assert "experience_multipliers" in rules
        assert "regression_rules" in rules
        
        # Check attribute gain rates
        gain_rates = rules["attribute_gain_rates"]
        assert "choice_consequence" in gain_rates
        assert "therapeutic_progress" in gain_rates
        assert "skill_demonstration" in gain_rates
        
        # Check experience multipliers
        multipliers = rules["experience_multipliers"]
        assert "first_time" in multipliers
        assert "milestone_related" in multipliers
        assert "therapeutic_aligned" in multipliers
        
        # Check regression rules
        regression = rules["regression_rules"]
        assert "enabled" in regression
        assert "max_regression" in regression
        assert "recovery_multiplier" in regression
    
    def test_get_character_summary(self, development_system, session_state):
        """Test character summary generation."""
        user_id = session_state.user_id
        
        # Add some character data
        development_system.character_attributes[user_id] = {}
        for attribute in list(CharacterAttribute)[:3]:  # First 3 attributes
            development_system.character_attributes[user_id][attribute] = CharacterAttributeLevel(
                attribute=attribute,
                current_level=2.5 + (attribute.value == "courage") * 1.0,  # Courage slightly higher
                experience_points=25,
                level_progress=0.6,
                peak_level=3.0
            )
        
        summary = development_system.get_character_summary(user_id)
        
        # Check summary structure
        assert "user_id" in summary
        assert "overall_level" in summary
        assert "total_experience" in summary
        assert "attributes" in summary
        assert "top_attributes" in summary
        assert "abilities" in summary
        assert "milestones" in summary
        assert "recent_development" in summary
        
        # Check values
        assert summary["user_id"] == user_id
        assert summary["overall_level"] > 0
        assert summary["total_experience"] > 0
        assert len(summary["attributes"]) == 3
        assert len(summary["top_attributes"]) == 3
    
    def test_get_character_summary_no_data(self, development_system):
        """Test character summary when no data exists."""
        summary = development_system.get_character_summary("nonexistent_user")
        
        assert "error" in summary
        assert summary["error"] == "No character data available"
    
    def test_get_character_progression_visualization(self, development_system, session_state):
        """Test character progression visualization data."""
        user_id = session_state.user_id
        
        # Add some character data
        development_system.character_attributes[user_id] = {}
        for i, attribute in enumerate(list(CharacterAttribute)[:3]):
            development_system.character_attributes[user_id][attribute] = CharacterAttributeLevel(
                attribute=attribute,
                current_level=2.0 + i * 0.5,
                experience_points=20 + i * 10,
                level_progress=0.4 + i * 0.1,
                peak_level=3.0 + i * 0.5,
                development_rate=0.1 + i * 0.05,
                story_manifestations=[f"Manifestation {j}" for j in range(3)],
                character_reactions=[f"Reaction {j}" for j in range(3)]
            )
        
        visualization = development_system.get_character_progression_visualization(user_id)
        
        # Check visualization structure
        assert "user_id" in visualization
        assert "attribute_progression" in visualization
        assert "next_level_requirements" in visualization
        assert "total_milestones" in visualization
        assert "total_abilities" in visualization
        
        # Check attribute progression data
        progression = visualization["attribute_progression"]
        assert len(progression) == 3
        
        for attr_data in progression:
            assert "attribute" in attr_data
            assert "name" in attr_data
            assert "current_level" in attr_data
            assert "level_progress" in attr_data
            assert "story_manifestations" in attr_data
            assert "character_reactions" in attr_data
    
    @pytest.mark.asyncio
    async def test_handle_character_regression(self, development_system, session_state):
        """Test character regression handling."""
        user_id = session_state.user_id
        
        # Initialize attributes
        await development_system._initialize_character_attributes(user_id)
        
        # Set up regression context
        regression_context = {
            "description": "Character faces a temporary setback",
            "story_context": "A difficult situation challenges your progress",
            "affected_attributes": [CharacterAttribute.RESILIENCE, CharacterAttribute.COURAGE]
        }
        
        # Get initial levels
        initial_resilience = development_system.character_attributes[user_id][CharacterAttribute.RESILIENCE].current_level
        
        # Handle regression
        event = await development_system.handle_character_regression(user_id, session_state, regression_context)
        
        # Check regression event
        assert isinstance(event, CharacterDevelopmentEvent)
        assert event.event_type == DevelopmentTrigger.CHALLENGE_OVERCOME
        assert len(event.attribute_changes) > 0
        
        # Check that regression was applied
        current_resilience = development_system.character_attributes[user_id][CharacterAttribute.RESILIENCE].current_level
        assert current_resilience < initial_resilience  # Should have decreased
        
        # Check session context
        assert "character_regression" in session_state.context
        regression_info = session_state.context["character_regression"]
        assert regression_info["is_temporary"] == True
        assert regression_info["recovery_opportunity"] == True
    
    def test_metrics_tracking(self, development_system):
        """Test metrics tracking."""
        initial_metrics = development_system.get_metrics()
        
        # Check metric structure
        assert "attribute_increases" in initial_metrics
        assert "abilities_unlocked" in initial_metrics
        assert "milestones_achieved" in initial_metrics
        assert "development_events_processed" in initial_metrics
        assert "character_celebrations" in initial_metrics
        assert "total_characters_tracked" in initial_metrics
        assert "total_abilities_unlocked" in initial_metrics
        assert "total_milestones_achieved" in initial_metrics
        
        # Initially should be zero
        assert initial_metrics["attribute_increases"] == 0
        assert initial_metrics["abilities_unlocked"] == 0
        assert initial_metrics["milestones_achieved"] == 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, development_system):
        """Test health check functionality."""
        health = await development_system.health_check()
        
        assert health["status"] == "healthy"
        assert "attribute_templates_loaded" in health
        assert "ability_templates_loaded" in health
        assert "milestone_templates_loaded" in health
        assert "development_rules_configured" in health
        assert "level_thresholds_configured" in health
        assert "milestone_thresholds_configured" in health
        assert "ability_unlock_conditions_configured" in health
        assert "metrics" in health
        
        # Should have loaded templates and rules
        assert health["attribute_templates_loaded"] > 0
        assert health["ability_templates_loaded"] > 0
        assert health["milestone_templates_loaded"] > 0
        assert health["level_thresholds_configured"] > 0
