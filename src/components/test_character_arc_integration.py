"""

# Logseq: [[TTA.dev/Components/Test_character_arc_integration]]
Test Character Arc Integration

This module provides tests for the integration between CharacterArcManager
and the tta.prototype Character Development System.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add paths for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

try:
    from components.character_arc_manager import (
        CharacterArcManagerComponent,
        InteractionContext,
        PlayerInteraction,
    )
    from orchestration import TTAConfig
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


async def test_character_arc_integration():
    """Test the integration between CharacterArcManager and Character Development System."""
    try:
        logger.info("Starting Character Arc Integration test")

        # Create configuration
        config = TTAConfig() if "TTAConfig" in globals() else {}

        # Initialize CharacterArcManager
        arc_manager = CharacterArcManagerComponent(config)

        # Start the component
        if not arc_manager.start():
            logger.error("Failed to start CharacterArcManager")
            return False

        # Test character creation with integration
        character_id = "test_integration_char_001"
        base_personality = {
            "name": "Dr. Elena Rodriguez",
            "empathy": 0.9,
            "patience": 0.8,
            "wisdom": 0.7,
            "supportiveness": 0.9,
            "therapeutic_role": "therapist",
        }

        logger.info(f"Creating integrated character: {character_id}")

        # Initialize character with integration
        if hasattr(arc_manager, "initialize_integrated_character_arc"):
            character_arc = await arc_manager.initialize_integrated_character_arc(
                character_id, base_personality
            )
        else:
            character_arc = await arc_manager.initialize_character_arc(
                character_id, base_personality
            )

        if not character_arc:
            logger.error("Failed to create character arc")
            return False

        logger.info(f"Created character arc for {character_arc.character_name}")

        # Test interaction processing with integration
        player_interaction = PlayerInteraction(
            interaction_id="test_interaction_001",
            session_id="test_session_001",
            character_id=character_id,
            player_choice="I've been feeling anxious lately and could use some guidance.",
            character_response="I understand that anxiety can be overwhelming. Let's explore some coping strategies together.",
            interaction_type="therapeutic",
            emotional_impact={"anxiety": -0.2, "hope": 0.3},
            relationship_changes={"trust_level": 0.1, "affection_level": 0.05},
            therapeutic_relevance=0.8,
        )

        logger.info("Processing integrated interaction")

        # Update character development with integration
        if hasattr(arc_manager, "update_integrated_character_development"):
            update_success = await arc_manager.update_integrated_character_development(
                character_id, player_interaction
            )
        else:
            update_success = await arc_manager.update_character_development(
                character_id, player_interaction
            )

        if not update_success:
            logger.error("Failed to update character development")
            return False

        logger.info("Successfully updated character development")

        # Test response generation with integration
        context = InteractionContext(
            session_id="test_session_001",
            scene_id="therapy_office",
            location="Dr. Rodriguez's office",
            participants=["player"],
            mood="concerned",
            therapeutic_opportunity=True,
        )

        logger.info("Generating integrated character response")

        # Generate response with integration
        if hasattr(arc_manager, "generate_integrated_character_response"):
            response_data = await arc_manager.generate_integrated_character_response(
                character_id, context
            )
        else:
            response = await arc_manager.generate_character_response(
                character_id, context
            )
            response_data = {
                "response_text": response.response_text,
                "emotional_tone": response.emotional_tone,
                "personality_consistency_score": response.personality_consistency_score,
            }

        logger.info(
            f"Generated response: {response_data.get('response_text', 'No response')[:100]}..."
        )

        # Test data synchronization
        if hasattr(arc_manager, "sync_with_character_development_system"):
            logger.info("Testing data synchronization")
            sync_success = await arc_manager.sync_with_character_development_system(
                character_id
            )
            if sync_success:
                logger.info("Data synchronization successful")
            else:
                logger.warning("Data synchronization failed or not available")

        # Test integrated summary
        if hasattr(arc_manager, "get_integrated_character_summary"):
            logger.info("Getting integrated character summary")
            summary = await arc_manager.get_integrated_character_summary(character_id)

            if summary and "error" not in summary:
                logger.info("Integrated summary retrieved successfully")
                logger.info(
                    f"Character stage: {summary.get('arc_manager_data', {}).get('current_stage', 'Unknown')}"
                )
                logger.info(
                    f"Integration status: {summary.get('integration_status', {}).get('systems_connected', False)}"
                )
            else:
                logger.warning(
                    "Failed to get integrated summary or integration not available"
                )

        # Test milestone resolution
        milestones = arc_manager.get_character_milestones(character_id)
        if milestones:
            first_milestone = milestones[0]
            logger.info(f"Testing milestone resolution: {first_milestone.name}")

            # Mark milestone as ready for completion (simulate progress)
            first_milestone.metadata["progress"] = 1.0

            resolution_result = await arc_manager.resolve_character_arc_milestone(
                character_id, first_milestone
            )

            if resolution_result.get("success", False):
                logger.info(f"Successfully resolved milestone: {first_milestone.name}")
            else:
                logger.warning(
                    f"Failed to resolve milestone: {resolution_result.get('reason', 'Unknown')}"
                )

        # Stop the component
        arc_manager.stop()

        logger.info("Character Arc Integration test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Character Arc Integration test failed: {e}")
        return False


async def test_integration_fallback():
    """Test that the system works even when integration is not available."""
    try:
        logger.info("Testing integration fallback behavior")

        # Create a mock config
        config = {}

        # Initialize CharacterArcManager (should work without integration)
        arc_manager = CharacterArcManagerComponent(config)

        if not arc_manager.start():
            logger.error("Failed to start CharacterArcManager in fallback mode")
            return False

        # Test basic functionality without integration
        character_id = "test_fallback_char_001"
        base_personality = {"name": "Test Character", "empathy": 0.7, "patience": 0.6}

        character_arc = await arc_manager.initialize_character_arc(
            character_id, base_personality
        )

        if character_arc:
            logger.info("Fallback character creation successful")
        else:
            logger.error("Fallback character creation failed")
            return False

        arc_manager.stop()

        logger.info("Integration fallback test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Integration fallback test failed: {e}")
        return False


async def main():
    """Run all integration tests."""
    logger.info("Starting Character Arc Integration tests")

    # Test integration functionality
    integration_test_result = await test_character_arc_integration()

    # Test fallback behavior
    fallback_test_result = await test_integration_fallback()

    # Summary
    if integration_test_result and fallback_test_result:
        logger.info("All Character Arc Integration tests passed")
        return True
    logger.error("Some Character Arc Integration tests failed")
    return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
