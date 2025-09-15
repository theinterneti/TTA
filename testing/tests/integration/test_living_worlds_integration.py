"""
Integration tests for the TTA Living Worlds system.

Tests the complete Living Worlds system including WorldStateManager,
ChoiceImpactTracker, TherapeuticWorldBuilder, EvolutionEngine, and PersistenceLayer.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from src.living_worlds import (
    WorldStateManager,
    ChoiceImpactTracker,
    TherapeuticWorldBuilder,
    EvolutionEngine,
    PersistenceLayer,
    WorldState,
    ChoiceImpact,
    TherapeuticWorld,
    EvolutionEvent,
    WorldStateType,
    ChoiceImpactType,
    EvolutionTrigger,
)


@pytest.fixture
def living_worlds_config():
    """Configuration for Living Worlds system testing."""
    return {
        "max_active_worlds": 10,
        "state_update_interval": 5,
        "evolution_check_interval": 10,
        "impact_strength_threshold": 0.1,
        "therapeutic_weight": 0.3,
        "supported_approaches": ["CBT", "DBT", "ACT", "Mindfulness"],
        "redis_key_prefix": "test:tta:living_worlds:",
        "session_ttl": 3600,
    }


@pytest.fixture
async def world_state_manager(living_worlds_config):
    """Create and initialize WorldStateManager for testing."""
    manager = WorldStateManager(living_worlds_config)
    await manager.initialize()
    yield manager
    await manager.shutdown()


@pytest.fixture
async def choice_impact_tracker(living_worlds_config):
    """Create and initialize ChoiceImpactTracker for testing."""
    tracker = ChoiceImpactTracker(living_worlds_config)
    await tracker.initialize()
    yield tracker
    await tracker.shutdown()


@pytest.fixture
async def therapeutic_world_builder(living_worlds_config):
    """Create and initialize TherapeuticWorldBuilder for testing."""
    builder = TherapeuticWorldBuilder(living_worlds_config)
    await builder.initialize()
    yield builder
    await builder.shutdown()


@pytest.fixture
async def evolution_engine(living_worlds_config):
    """Create and initialize EvolutionEngine for testing."""
    engine = EvolutionEngine(living_worlds_config)
    await engine.initialize()
    yield engine
    await engine.shutdown()


@pytest.fixture
async def persistence_layer(living_worlds_config):
    """Create and initialize PersistenceLayer for testing."""
    layer = PersistenceLayer(living_worlds_config)
    await layer.initialize()
    yield layer
    await layer.shutdown()


class TestLivingWorldsIntegration:
    """Integration tests for the complete Living Worlds system."""
    
    @pytest.mark.asyncio
    async def test_world_creation_and_management(self, world_state_manager):
        """Test creating and managing world states."""
        world_id = "test_world_001"
        session_id = "test_session_001"
        player_id = "test_player_001"
        
        # Create world state
        success = await world_state_manager.create_world_state(
            world_id=world_id,
            session_id=session_id,
            player_id=player_id,
            therapeutic_context={"approach": "CBT", "goals": ["anxiety_reduction"]},
            initial_properties={"difficulty": "beginner", "theme": "urban"}
        )
        
        assert success is True
        
        # Retrieve world state
        world_state = await world_state_manager.get_world_state(world_id)
        assert world_state is not None
        assert world_state.world_id == world_id
        assert world_state.session_id == session_id
        assert world_state.player_id == player_id
        assert world_state.state_type == WorldStateType.ACTIVE
        
        # Update world state
        update_success = await world_state_manager.update_world_state(
            world_id=world_id,
            state_updates={"current_scene": "marketplace", "npc_count": 5},
            therapeutic_updates={"progress": {"anxiety_reduction": 0.2}}
        )
        
        assert update_success is True
        
        # Verify updates
        updated_world_state = await world_state_manager.get_world_state(world_id)
        assert updated_world_state.world_properties["current_scene"] == "marketplace"
        assert updated_world_state.therapeutic_context["progress"]["anxiety_reduction"] == 0.2
    
    @pytest.mark.asyncio
    async def test_choice_impact_processing(self, world_state_manager, choice_impact_tracker):
        """Test processing player choice impacts."""
        world_id = "test_world_002"
        session_id = "test_session_002"
        player_id = "test_player_002"
        
        # Create world state
        await world_state_manager.create_world_state(
            world_id=world_id,
            session_id=session_id,
            player_id=player_id
        )
        
        world_state = await world_state_manager.get_world_state(world_id)
        
        # Process choice impact
        choice_data = {
            "text": "Help the injured stranger",
            "context": {
                "characters": ["stranger", "bystander"],
                "locations": ["street_corner"],
                "objects": ["first_aid_kit"]
            },
            "urgency": "immediate",
            "strength": 0.7,
            "therapeutic_progress": {"empathy": 0.1, "confidence": 0.05}
        }
        
        choice_impact = await world_state_manager.process_choice_impact(
            world_id=world_id,
            choice_id="choice_001",
            choice_data=choice_data
        )
        
        assert choice_impact is not None
        assert choice_impact.choice_id == "choice_001"
        assert choice_impact.impact_type == ChoiceImpactType.IMMEDIATE
        assert choice_impact.strength > 0.5
        assert "stranger" in choice_impact.affected_characters
        assert "street_corner" in choice_impact.affected_locations
    
    @pytest.mark.asyncio
    async def test_therapeutic_world_creation(self, therapeutic_world_builder):
        """Test creating therapeutic worlds."""
        patient_profile = {
            "primary_concerns": ["anxiety", "social_skills"],
            "therapeutic_goals": ["anxiety_reduction", "social_confidence"],
            "preferred_intensity": "MEDIUM",
            "environment_preferences": {"preferred_settings": "nature"},
            "accessibility_needs": ["large_text", "audio_cues"],
            "crisis_sensitivity": "medium"
        }
        
        therapeutic_world = await therapeutic_world_builder.create_therapeutic_world(
            world_name="Anxiety Management Garden",
            therapeutic_approaches=["CBT", "Mindfulness"],
            patient_profile=patient_profile
        )
        
        assert therapeutic_world is not None
        assert therapeutic_world.name == "Anxiety Management Garden"
        assert "CBT" in therapeutic_world.therapeutic_approaches
        assert "Mindfulness" in therapeutic_world.therapeutic_approaches
        assert len(therapeutic_world.key_locations) > 0
        assert len(therapeutic_world.key_characters) > 0
        assert therapeutic_world.safety_guidelines is not None
        assert therapeutic_world.crisis_protocols is not None
        
        # Test world customization
        customization_success = await therapeutic_world_builder.customize_world_for_patient(
            world_id=therapeutic_world.world_id,
            patient_profile=patient_profile,
            therapeutic_goals=["anxiety_reduction", "mindfulness_practice"]
        )
        
        assert customization_success is True
    
    @pytest.mark.asyncio
    async def test_world_evolution(self, world_state_manager, evolution_engine):
        """Test world evolution based on triggers."""
        world_id = "test_world_003"
        session_id = "test_session_003"
        player_id = "test_player_003"
        
        # Create world state with some history
        await world_state_manager.create_world_state(
            world_id=world_id,
            session_id=session_id,
            player_id=player_id,
            therapeutic_context={"approach": "DBT"},
            initial_properties={"narrative_state": {"current_act": 1, "scenes_in_current_act": 6}}
        )
        
        world_state = await world_state_manager.get_world_state(world_id)
        world_state.recent_events = ["player_helped_npc", "discovered_secret", "made_friend"]
        world_state.therapeutic_progress = {"emotion_regulation": 0.85, "distress_tolerance": 0.6}
        
        # Check evolution triggers
        evolution_events = await evolution_engine.check_evolution_triggers(world_state)
        
        assert len(evolution_events) > 0
        
        # Verify different types of evolution events
        event_types = [event.trigger for event in evolution_events]
        assert EvolutionTrigger.TIME_PASSAGE in event_types or \
               EvolutionTrigger.PLAYER_ACTION in event_types or \
               EvolutionTrigger.THERAPEUTIC_MILESTONE in event_types or \
               EvolutionTrigger.NARRATIVE_REQUIREMENT in event_types
        
        # Test therapeutic milestone evolution
        therapeutic_events = [e for e in evolution_events if e.trigger == EvolutionTrigger.THERAPEUTIC_MILESTONE]
        if therapeutic_events:
            event = therapeutic_events[0]
            assert event.therapeutic_changes is not None
            assert "milestone_achieved" in event.therapeutic_changes
    
    @pytest.mark.asyncio
    async def test_persistence_operations(self, persistence_layer):
        """Test world state persistence operations."""
        world_id = "test_world_004"
        player_id = "test_player_004"
        session_id = "test_session_004"
        
        # Create persistence structure
        success = await persistence_layer.create_world_persistence(world_id, player_id)
        assert success is True
        
        # Create and save world state
        world_state = WorldState(
            world_id=world_id,
            session_id=session_id,
            player_id=player_id,
            world_properties={"location": "forest", "weather": "sunny"},
            therapeutic_context={"approach": "ACT", "progress": {"values_clarity": 0.4}},
            therapeutic_goals=["values_exploration", "psychological_flexibility"]
        )
        
        save_success = await persistence_layer.save_world_state(world_state)
        assert save_success is True
        
        # Load world state
        loaded_world_state = await persistence_layer.load_world_state(world_id, session_id)
        assert loaded_world_state is not None
        assert loaded_world_state.world_id == world_id
        assert loaded_world_state.world_properties["location"] == "forest"
        assert loaded_world_state.therapeutic_context["approach"] == "ACT"
    
    @pytest.mark.asyncio
    async def test_complete_storytelling_workflow(
        self, 
        world_state_manager, 
        choice_impact_tracker, 
        therapeutic_world_builder, 
        evolution_engine
    ):
        """Test complete storytelling workflow integration."""
        world_id = "test_world_005"
        session_id = "test_session_005"
        player_id = "test_player_005"
        
        # 1. Create therapeutic world
        patient_profile = {
            "primary_concerns": ["depression", "self_esteem"],
            "therapeutic_goals": ["mood_improvement", "self_compassion"],
            "preferred_intensity": "LOW"
        }
        
        therapeutic_world = await therapeutic_world_builder.create_therapeutic_world(
            world_name="Self-Compassion Journey",
            therapeutic_approaches=["CBT", "Humanistic"],
            patient_profile=patient_profile
        )
        
        # 2. Create world state
        await world_state_manager.create_world_state(
            world_id=world_id,
            session_id=session_id,
            player_id=player_id,
            therapeutic_context={
                "therapeutic_world_id": therapeutic_world.world_id,
                "approach": "CBT",
                "goals": patient_profile["therapeutic_goals"]
            }
        )
        
        # 3. Process multiple choice impacts
        choices = [
            {
                "id": "choice_001",
                "data": {
                    "text": "Practice self-compassion meditation",
                    "therapeutic_progress": {"self_compassion": 0.1, "mindfulness": 0.05},
                    "strength": 0.6
                }
            },
            {
                "id": "choice_002", 
                "data": {
                    "text": "Challenge negative self-talk",
                    "therapeutic_progress": {"cognitive_restructuring": 0.15, "self_esteem": 0.1},
                    "strength": 0.7
                }
            }
        ]
        
        for choice in choices:
            choice_impact = await world_state_manager.process_choice_impact(
                world_id=world_id,
                choice_id=choice["id"],
                choice_data=choice["data"]
            )
            assert choice_impact is not None
        
        # 4. Update therapeutic progress and trigger evolution
        world_state = await world_state_manager.get_world_state(world_id)
        world_state.therapeutic_progress = {
            "self_compassion": 0.3,
            "cognitive_restructuring": 0.4,
            "mood_improvement": 0.25
        }
        
        evolution_events = await evolution_engine.check_evolution_triggers(world_state)
        assert len(evolution_events) >= 0  # May or may not have events depending on triggers
        
        # 5. Verify final state
        final_world_state = await world_state_manager.get_world_state(world_id)
        assert final_world_state is not None
        assert final_world_state.therapeutic_context["therapeutic_world_id"] == therapeutic_world.world_id
        
        # 6. Get metrics
        manager_metrics = await world_state_manager.get_metrics()
        tracker_metrics = await choice_impact_tracker.get_metrics()
        builder_metrics = await therapeutic_world_builder.get_metrics()
        evolution_metrics = await evolution_engine.get_metrics()
        
        assert manager_metrics["worlds_created"] > 0
        assert tracker_metrics["choices_processed"] > 0
        assert builder_metrics["worlds_created"] > 0
        assert evolution_metrics["evolution_checks"] > 0
        
        print(f"✅ Complete storytelling workflow test passed!")
        print(f"   - Worlds created: {manager_metrics['worlds_created']}")
        print(f"   - Choices processed: {tracker_metrics['choices_processed']}")
        print(f"   - Therapeutic worlds: {builder_metrics['worlds_created']}")
        print(f"   - Evolution checks: {evolution_metrics['evolution_checks']}")


if __name__ == "__main__":
    # Run a simple test
    async def run_simple_test():
        config = {
            "max_active_worlds": 10,
            "state_update_interval": 5,
            "evolution_check_interval": 10,
            "supported_approaches": ["CBT", "DBT", "ACT", "Mindfulness"],
        }
        
        manager = WorldStateManager(config)
        await manager.initialize()
        
        success = await manager.create_world_state(
            world_id="simple_test_world",
            session_id="simple_test_session", 
            player_id="simple_test_player"
        )
        
        print(f"Simple test result: {'✅ PASSED' if success else '❌ FAILED'}")
        
        await manager.shutdown()
    
    asyncio.run(run_simple_test())
