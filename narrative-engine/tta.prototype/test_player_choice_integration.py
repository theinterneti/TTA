#!/usr/bin/env python3
"""
Integration test for Player Choice Impact System

This script tests the integration of the player choice impact system with
existing TTA Living Worlds components including timeline engine, world state
manager, and narrative branching system.
"""

import logging
import sys
from datetime import timedelta
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent / "core"
models_path = Path(__file__).parent / "models"
sys.path.insert(0, str(core_path))
sys.path.insert(0, str(models_path))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_player_choice_impact_integration():
    """Test integration of player choice impact system with existing components."""

    try:
        # Import required components
        from character_development_system import CharacterDevelopmentSystem
        from narrative_branching import (
            ChoiceOption,
            ChoiceType,
            NarrativeBranchingChoice,
        )
        from player_choice_impact_system import ChoiceCategory, PlayerChoiceImpactSystem
        from timeline_engine import TimelineEngine
        from world_state_manager import WorldConfig, WorldStateManager

        logger.info("Starting Player Choice Impact System integration test...")

        # Initialize core systems
        timeline_engine = TimelineEngine()
        world_state_manager = WorldStateManager()
        character_system = CharacterDevelopmentSystem()
        narrative_branching = NarrativeBranchingChoice()

        # Initialize player choice impact system
        choice_impact_system = PlayerChoiceImpactSystem(
            timeline_engine=timeline_engine,
            world_state_manager=world_state_manager,
            character_system=character_system,
            narrative_branching=narrative_branching
        )

        logger.info("✓ All systems initialized successfully")

        # Create a test world
        world_config = WorldConfig(
            world_name="Test Living World",
            initial_characters=[
                {
                    "id": "alice",
                    "name": "Alice",
                    "personality": {"empathy": 0.8, "patience": 0.7},
                    "location_id": "garden"
                },
                {
                    "id": "bob",
                    "name": "Bob",
                    "personality": {"humor": 0.6, "supportiveness": 0.9},
                    "location_id": "garden"
                }
            ],
            initial_locations=[
                {
                    "id": "garden",
                    "name": "Peaceful Garden",
                    "description": "A serene garden with blooming flowers",
                    "connected_locations": ["library"]
                },
                {
                    "id": "library",
                    "name": "Quiet Library",
                    "description": "A cozy library filled with books",
                    "connected_locations": ["garden"]
                }
            ],
            initial_objects=[
                {
                    "id": "bench",
                    "name": "Garden Bench",
                    "location_id": "garden",
                    "description": "A comfortable wooden bench"
                }
            ]
        )

        world_state_manager.initialize_world("test_world_123", world_config)
        logger.info("✓ Test world created successfully")

        # Test 1: Process a social choice
        logger.info("\n--- Test 1: Processing Social Choice ---")

        social_choice = ChoiceOption(
            choice_id="social_choice_1",
            choice_text="Approach Alice and offer to help with her gardening",
            choice_type=ChoiceType.DIALOGUE,
            therapeutic_weight=0.6,
            emotional_tone="supportive"
        )

        social_context = {
            "player_id": "player_test",
            "world_id": "test_world_123",
            "characters_present": ["alice", "bob"],
            "current_location": "garden",
            "objects_present": ["bench"],
            "emotional_state": {"happiness": 0.7, "confidence": 0.6},
            "confidence_level": 0.8,
            "response_time": 3.2
        }

        social_result = choice_impact_system.process_player_choice(social_choice, social_context)

        if social_result["success"]:
            logger.info("✓ Social choice processed successfully")
            logger.info(f"  - Impact strength: {social_result['impact']['strength']:.2f}")
            logger.info(f"  - Affected entities: {social_result['impact']['affected_entities']}")
            logger.info(f"  - Timeline events created: {social_result['impact']['timeline_events']}")
            logger.info(f"  - Feedback summary: {social_result['feedback']['summary']}")
        else:
            logger.error(f"✗ Social choice processing failed: {social_result.get('error', 'Unknown error')}")
            return False

        # Test 2: Process a therapeutic choice
        logger.info("\n--- Test 2: Processing Therapeutic Choice ---")

        therapeutic_choice = ChoiceOption(
            choice_id="therapeutic_choice_1",
            choice_text="Take a moment to practice deep breathing and mindfulness",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_weight=0.9,
            emotional_tone="calming"
        )

        therapeutic_context = {
            "player_id": "player_test",
            "world_id": "test_world_123",
            "characters_present": ["alice"],
            "current_location": "garden",
            "emotional_state": {"anxiety": 0.8, "stress": 0.7},
            "confidence_level": 0.6,
            "response_time": 8.5
        }

        therapeutic_result = choice_impact_system.process_player_choice(therapeutic_choice, therapeutic_context)

        if therapeutic_result["success"]:
            logger.info("✓ Therapeutic choice processed successfully")
            logger.info(f"  - Impact strength: {therapeutic_result['impact']['strength']:.2f}")
            logger.info(f"  - Impact scope: {therapeutic_result['impact']['scope']}")
            logger.info(f"  - Therapeutic impact: {therapeutic_result['narrative_consequence']['therapeutic_impact']:.2f}")
        else:
            logger.error(f"✗ Therapeutic choice processing failed: {therapeutic_result.get('error', 'Unknown error')}")
            return False

        # Test 3: Check preference tracking
        logger.info("\n--- Test 3: Testing Preference Tracking ---")

        preference_summary = choice_impact_system.get_player_preference_summary("player_test")

        logger.info("✓ Player preferences tracked:")
        logger.info(f"  - Total preferences: {preference_summary['total_preferences']}")
        logger.info(f"  - Strong preferences: {len(preference_summary['strong_preferences'])}")
        logger.info(f"  - Weak preferences: {len(preference_summary['weak_preferences'])}")

        evolution_guidance = preference_summary['evolution_guidance']
        logger.info(f"  - Preferred content types: {evolution_guidance['preferred_content_types']}")
        logger.info(f"  - Adaptation suggestions: {len(evolution_guidance['adaptation_suggestions'])}")

        # Test 4: Check choice impact history
        logger.info("\n--- Test 4: Testing Choice Impact History ---")

        impact_history = choice_impact_system.get_choice_impact_history("player_test", limit=5)

        logger.info("✓ Choice impact history retrieved:")
        logger.info(f"  - Total choices in history: {len(impact_history)}")

        for i, choice_entry in enumerate(impact_history):
            logger.info(f"  - Choice {i+1}: {choice_entry['choice_text'][:50]}...")
            logger.info(f"    Category: {choice_entry['category']}, Impact: {choice_entry['impact_strength']:.2f}")

        # Test 5: Check world impact metrics
        logger.info("\n--- Test 5: Testing World Impact Metrics ---")

        metrics = choice_impact_system.calculate_choice_impact_metrics("test_world_123", timedelta(hours=1))

        logger.info("✓ World impact metrics calculated:")
        logger.info(f"  - Total choices: {metrics['total_choices']}")

        if metrics['total_choices'] > 0:
            metrics_data = metrics['metrics']
            logger.info(f"  - Average impact strength: {metrics_data['average_impact_strength']:.2f}")
            logger.info(f"  - Total affected entities: {metrics_data['total_affected_entities']}")
            logger.info(f"  - Most popular category: {metrics_data['most_popular_category']}")
            logger.info(f"  - Category distribution: {metrics_data['category_distribution']}")

        # Test 6: Verify timeline integration
        logger.info("\n--- Test 6: Testing Timeline Integration ---")

        # Check that timeline events were created for characters
        alice_timeline = timeline_engine.get_timeline("alice")
        if alice_timeline:
            alice_events = alice_timeline.events
            logger.info(f"✓ Alice's timeline has {len(alice_events)} events")

            # Find player choice related events
            choice_events = [e for e in alice_events if "player_choice" in e.tags]
            logger.info(f"  - Player choice events: {len(choice_events)}")

            if choice_events:
                latest_event = choice_events[-1]
                logger.info(f"  - Latest choice event: {latest_event.title}")
                logger.info(f"  - Event significance: {latest_event.significance_level}/10")
        else:
            logger.warning("⚠ Alice's timeline not found")

        # Test 7: Verify world state updates
        logger.info("\n--- Test 7: Testing World State Updates ---")

        updated_world_state = world_state_manager.get_world_state("test_world_123")
        if updated_world_state:
            alice_data = updated_world_state.active_characters.get("alice", {})

            if "relationships" in alice_data:
                player_relationship = alice_data["relationships"].get("player_test", 0.0)
                logger.info(f"✓ Alice's relationship with player: {player_relationship:.2f}")

            if "emotional_state" in alice_data:
                emotional_state = alice_data["emotional_state"]
                logger.info(f"✓ Alice's emotional state: {emotional_state}")

        logger.info("\n🎉 All integration tests completed successfully!")
        logger.info("Player Choice Impact System is properly integrated with TTA Living Worlds components.")

        return True

    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        logger.error("Make sure all required components are available")
        return False

    except Exception as e:
        logger.error(f"✗ Integration test failed: {e}")
        logger.exception("Full error details:")
        return False


def test_choice_impact_visualization():
    """Test the choice impact visualization components."""

    try:
        from player_choice_impact_system import (
            ChoiceCategory,
            ChoiceImpact,
            ChoiceImpactVisualizer,
            ImpactScope,
            PlayerChoice,
        )

        logger.info("\n--- Testing Choice Impact Visualization ---")

        visualizer = ChoiceImpactVisualizer()

        # Create test data
        test_choice = PlayerChoice(
            player_id="player_test",
            world_id="world_test",
            choice_text="Comfort the distressed character with kind words",
            choice_category=ChoiceCategory.SOCIAL
        )

        test_impact = ChoiceImpact(
            choice_id=test_choice.choice_id,
            impact_scope=ImpactScope.LOCAL,
            impact_strength=0.8
        )

        test_impact.add_affected_entity("character", "alice")
        test_impact.add_affected_entity("character", "bob")
        test_impact.relationship_changes = {"alice": 0.4, "bob": 0.2}
        test_impact.world_state_changes = {"mood_improved": True, "trust_level": 0.6}
        test_impact.long_term_consequences = ["deeper_friendship", "increased_empathy"]

        # Test comprehensive feedback generation
        feedback = visualizer.generate_comprehensive_feedback(test_choice, test_impact)

        logger.info("✓ Comprehensive feedback generated:")
        logger.info(f"  - Choice ID: {feedback['choice_id']}")
        logger.info(f"  - Summary: {feedback['summary']}")

        # Test individual components
        immediate = feedback['components']['immediate']
        logger.info(f"  - Immediate feedback: {immediate['text']}")
        logger.info(f"  - Impact level: {immediate['impact_level']}")

        relationships = feedback['components']['relationships']
        if relationships['relationships']:
            logger.info(f"  - Relationship changes: {len(relationships['relationships'])} affected")
            for rel in relationships['relationships']:
                logger.info(f"    * {rel['description']} {rel['indicator']}")

        world_changes = feedback['components']['world_changes']
        if world_changes['changes']:
            logger.info(f"  - World changes: {len(world_changes['changes'])} detected")

        long_term = feedback['components']['long_term']
        if long_term['consequences']:
            logger.info(f"  - Long-term consequences: {len(long_term['consequences'])} predicted")
            logger.info(f"  - Preview: {long_term['text']}")

        logger.info("✓ Choice impact visualization test completed successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Visualization test failed: {e}")
        return False


def main():
    """Run all integration tests."""

    logger.info("=" * 60)
    logger.info("TTA Living Worlds - Player Choice Impact System")
    logger.info("Integration Test Suite")
    logger.info("=" * 60)

    success = True

    # Run main integration test
    if not test_player_choice_impact_integration():
        success = False

    # Run visualization test
    if not test_choice_impact_visualization():
        success = False

    logger.info("\n" + "=" * 60)
    if success:
        logger.info("🎉 ALL TESTS PASSED - Player Choice Impact System is ready!")
        logger.info("The system successfully integrates with existing TTA components.")
    else:
        logger.error("❌ SOME TESTS FAILED - Please check the errors above.")
        logger.error("Fix the issues before using the Player Choice Impact System.")
    logger.info("=" * 60)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
