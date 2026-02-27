"""
Logseq: [[TTA.dev/Components/Character_arc_integration]]

# Logseq: [[TTA/Components/Character_arc_integration]]
Character Arc Integration Module

This module provides integration between the new CharacterArcManager component
and the existing tta.prototype Character Development System. It handles data
synchronization, character arc data mapping, and relationship dynamics management
across both systems.

Classes:
    CharacterArcIntegration: Main integration class
    CharacterDataSynchronizer: Handles data sync between systems
    RelationshipDynamicsManager: Manages relationship evolution across systems
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add tta.prototype path for imports
prototype_path = Path(__file__).parent.parent.parent / "tta.prototype"
if str(prototype_path) not in sys.path:
    sys.path.append(str(prototype_path))

try:
    from core.character_development_system import (  # type: ignore[import-not-found]
        CharacterDevelopmentSystem,
        Interaction,
    )
    from models.data_models import CharacterState  # type: ignore[import-not-found]
except ImportError as e:
    logging.warning(f"Could not import tta.prototype modules: {e}")

    # Create mock classes for development
    class CharacterDevelopmentSystem:
        def __init__(self):
            pass

        def get_character_state(self, character_id: str):
            return None

        def update_character_from_interaction(self, character_id: str, interaction):
            return True

        def create_character(self, character_id: str, name: str, **kwargs):
            return None

    class CharacterState:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Interaction:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


from .character_arc_manager import (  # noqa: E402
    CharacterArc,
    CharacterArcManagerComponent,
    InteractionContext,
    PlayerInteraction,
    RelationshipState,
    RelationshipType,
)

logger = logging.getLogger(__name__)


class CharacterDataSynchronizer:
    """Handles data synchronization between CharacterArcManager and Character Development System."""

    def __init__(self, character_development_system: CharacterDevelopmentSystem):
        self.character_development_system = character_development_system
        self.sync_mapping = self._create_sync_mapping()

    def _create_sync_mapping(self) -> dict[str, str]:
        """Create mapping between CharacterArc and CharacterState fields."""
        return {
            # Personality trait mappings
            "openness": "openness",
            "conscientiousness": "conscientiousness",
            "extraversion": "extraversion",
            "agreeableness": "agreeableness",
            "neuroticism": "neuroticism",
            "empathy": "empathy",
            "patience": "patience",
            "wisdom": "wisdom",
            "humor": "humor",
            "supportiveness": "supportiveness",
            # Relationship mappings
            "trust_level": "trust_level",
            "affection_level": "affection_level",
            "respect_level": "respect_level",
            # Other mappings
            "current_mood": "current_mood",
            "therapeutic_role": "therapeutic_role",
        }

    async def sync_character_to_development_system(
        self, character_arc: CharacterArc
    ) -> bool:
        """Sync CharacterArc data to Character Development System."""
        try:
            logger.debug(
                f"Syncing character arc {character_arc.character_id} to development system"
            )

            # Get existing character state or create new one
            character_state = self.character_development_system.get_character_state(
                character_arc.character_id
            )

            if not character_state:
                # Create new character in development system
                character_state = self.character_development_system.create_character(
                    character_id=character_arc.character_id,
                    name=character_arc.character_name,
                    personality_traits=character_arc.personality_evolution.copy(),
                    therapeutic_role=character_arc.metadata.get(
                        "therapeutic_role", "companion"
                    ),
                )

                if not character_state:
                    logger.error(
                        f"Failed to create character {character_arc.character_id} in development system"
                    )
                    return False

            # Sync personality traits
            await self._sync_personality_traits(character_arc, character_state)

            # Sync relationship data
            await self._sync_relationship_data(character_arc, character_state)

            # Sync memory data
            await self._sync_memory_data(character_arc, character_state)

            # Update last interaction timestamp
            character_state.last_interaction = character_arc.last_updated

            logger.debug(f"Successfully synced character {character_arc.character_id}")
            return True

        except Exception as e:
            logger.error(f"Error syncing character {character_arc.character_id}: {e}")
            return False

    async def sync_character_from_development_system(
        self, character_arc: CharacterArc
    ) -> bool:
        """Sync data from Character Development System to CharacterArc."""
        try:
            logger.debug(
                f"Syncing character {character_arc.character_id} from development system"
            )

            character_state = self.character_development_system.get_character_state(
                character_arc.character_id
            )
            if not character_state:
                logger.warning(
                    f"Character {character_arc.character_id} not found in development system"
                )
                return False

            # Sync personality traits back
            for trait_name, value in character_state.personality_traits.items():
                if trait_name in character_arc.personality_evolution:
                    character_arc.personality_evolution[trait_name] = value

            # Sync relationship scores back
            player_relationship = character_arc.relationship_dynamics.get("player")
            if player_relationship and "player" in character_state.relationship_scores:
                # Map development system relationship score to our relationship metrics
                dev_score = character_state.relationship_scores["player"]
                player_relationship.trust_level = max(
                    0.0, min(1.0, (dev_score + 1.0) / 2.0)
                )
                player_relationship.affection_level = max(
                    0.0, min(1.0, (dev_score + 1.0) / 2.0)
                )

            # Update last sync timestamp
            character_arc.last_updated = datetime.now()

            logger.debug(
                f"Successfully synced character {character_arc.character_id} from development system"
            )
            return True

        except Exception as e:
            logger.error(f"Error syncing character from development system: {e}")
            return False

    async def _sync_personality_traits(
        self, character_arc: CharacterArc, character_state: CharacterState
    ) -> None:
        """Sync personality traits between systems."""
        try:
            for trait_name, value in character_arc.personality_evolution.items():
                if trait_name in self.sync_mapping:
                    mapped_trait = self.sync_mapping[trait_name]
                    character_state.personality_traits[mapped_trait] = value  # type: ignore[attr-defined]

            logger.debug(
                f"Synced {len(character_arc.personality_evolution)} personality traits"
            )

        except Exception as e:
            logger.error(f"Error syncing personality traits: {e}")

    async def _sync_relationship_data(
        self, character_arc: CharacterArc, character_state: CharacterState
    ) -> None:
        """Sync relationship data between systems."""
        try:
            # Convert our relationship states to development system relationship scores
            for (
                character_id,
                relationship_state,
            ) in character_arc.relationship_dynamics.items():
                # Calculate overall relationship score from our detailed metrics
                overall_score = (
                    relationship_state.trust_level * 0.4
                    + relationship_state.affection_level * 0.3
                    + relationship_state.respect_level * 0.3
                ) * 2.0 - 1.0  # Convert from 0-1 to -1 to 1 range

                character_state.relationship_scores[character_id] = max(  # type: ignore[attr-defined]
                    -1.0, min(1.0, overall_score)
                )

            logger.debug(
                f"Synced {len(character_arc.relationship_dynamics)} relationships"
            )

        except Exception as e:
            logger.error(f"Error syncing relationship data: {e}")

    async def _sync_memory_data(
        self, character_arc: CharacterArc, character_state: CharacterState
    ) -> None:
        """Sync memory data between systems."""
        try:
            # Convert character history to memory fragments
            for history_entry in character_arc.character_history[
                -10:
            ]:  # Last 10 interactions
                memory_content = f"Interaction: {history_entry.get('player_choice', 'Unknown choice')}"
                emotional_weight = sum(
                    history_entry.get("emotional_impact", {}).values()
                ) / max(1, len(history_entry.get("emotional_impact", {})))

                # Check if this memory already exists
                existing_memory = any(
                    memory_content in memory.content
                    for memory in character_state.memory_fragments  # type: ignore[attr-defined]
                )

                if not existing_memory:
                    character_state.add_memory(  # type: ignore[attr-defined]
                        content=memory_content,
                        emotional_weight=emotional_weight,
                        tags=["interaction", "player"],
                    )

            logger.debug(
                f"Synced memory data for character {character_arc.character_id}"
            )

        except Exception as e:
            logger.error(f"Error syncing memory data: {e}")


class RelationshipDynamicsManager:
    """Manages relationship evolution across both character systems."""

    def __init__(self, character_development_system: CharacterDevelopmentSystem):
        self.character_development_system = character_development_system
        self.relationship_evolution_rate = 0.1

    async def evolve_relationships_across_scales(
        self,
        character_arc: CharacterArc,
        interactions: list[PlayerInteraction],
        time_period: timedelta | None = None,
    ) -> dict[str, float]:
        """Evolve relationships across both systems based on interactions."""
        try:
            if time_period is None:
                time_period = timedelta(days=1)

            relationship_changes = {}

            # Convert PlayerInteractions to development system Interactions
            dev_interactions = []
            for player_interaction in interactions:
                dev_interaction = Interaction(
                    participants=[character_arc.character_id, "player"],
                    interaction_type=player_interaction.interaction_type,
                    content=player_interaction.player_choice,
                    emotional_impact=sum(player_interaction.emotional_impact.values())
                    / max(1, len(player_interaction.emotional_impact)),
                    therapeutic_value=player_interaction.therapeutic_relevance,
                )
                dev_interactions.append(dev_interaction)

            # Update development system
            for interaction in dev_interactions:
                success = (
                    self.character_development_system.update_character_from_interaction(
                        character_arc.character_id, interaction
                    )
                )
                if not success:
                    logger.warning(
                        f"Failed to update character {character_arc.character_id} in development system"
                    )

            # Update our relationship dynamics based on interactions
            for interaction in interactions:
                await self._update_arc_relationships(character_arc, interaction)

                # Track changes
                for character_id, changes in interaction.relationship_changes.items():
                    if character_id not in relationship_changes:
                        relationship_changes[character_id] = 0.0
                    relationship_changes[character_id] += (
                        sum(changes.values()) if isinstance(changes, dict) else changes
                    )

            logger.debug(
                f"Evolved relationships for character {character_arc.character_id}"
            )
            return relationship_changes

        except Exception as e:
            logger.error(f"Error evolving relationships: {e}")
            return {}

    async def _update_arc_relationships(
        self, character_arc: CharacterArc, interaction: PlayerInteraction
    ) -> None:
        """Update character arc relationships based on interaction."""
        try:
            player_id = "player"

            # Get or create player relationship
            if player_id not in character_arc.relationship_dynamics:
                character_arc.relationship_dynamics[player_id] = RelationshipState(
                    character_id=character_arc.character_id,
                    relationship_type=RelationshipType.STRANGER,
                )

            relationship = character_arc.relationship_dynamics[player_id]

            # Update relationship metrics based on interaction
            for metric, change in interaction.relationship_changes.items():
                if hasattr(relationship, metric):
                    current_value = getattr(relationship, metric)
                    new_value = max(
                        0.0,
                        min(
                            1.0,
                            current_value + change * self.relationship_evolution_rate,
                        ),
                    )
                    setattr(relationship, metric, new_value)

            # Update relationship type based on trust level
            if relationship.trust_level > 0.8:
                relationship.relationship_type = RelationshipType.CLOSE_FRIEND
            elif relationship.trust_level > 0.6:
                relationship.relationship_type = RelationshipType.FRIEND
            elif relationship.trust_level > 0.3:
                relationship.relationship_type = RelationshipType.ACQUAINTANCE

            # Update interaction tracking
            relationship.last_interaction = interaction.timestamp
            relationship.interaction_count += 1
            relationship.shared_experiences.append(interaction.interaction_id)

            logger.debug(
                f"Updated relationship for character {character_arc.character_id}"
            )

        except Exception as e:
            logger.error(f"Error updating arc relationships: {e}")

    async def calculate_relationship_compatibility(
        self, character_arc: CharacterArc, other_character_id: str
    ) -> float:
        """Calculate relationship compatibility between characters."""
        try:
            # Get character states from development system
            char1_state = self.character_development_system.get_character_state(
                character_arc.character_id
            )
            char2_state = self.character_development_system.get_character_state(
                other_character_id
            )

            if not char1_state or not char2_state:
                return 0.5  # Neutral compatibility if data unavailable

            # Use development system's compatibility calculation
            return self.character_development_system.personality_manager.calculate_personality_compatibility(  # type: ignore[attr-defined]
                char1_state.personality_traits, char2_state.personality_traits
            )

        except Exception as e:
            logger.error(f"Error calculating relationship compatibility: {e}")
            return 0.5


class CharacterArcIntegration:
    """Main integration class between CharacterArcManager and Character Development System."""

    def __init__(self, character_arc_manager: CharacterArcManagerComponent):
        self.character_arc_manager = character_arc_manager
        self.character_development_system = CharacterDevelopmentSystem()
        self.data_synchronizer = CharacterDataSynchronizer(
            self.character_development_system
        )
        self.relationship_manager = RelationshipDynamicsManager(
            self.character_development_system
        )

        # Integration settings
        self.sync_interval = timedelta(minutes=5)  # Sync every 5 minutes
        self.last_sync_times: dict[str, datetime] = {}

        logger.info("Character Arc Integration initialized")

    async def initialize_character_integration(
        self, character_id: str, base_personality: dict[str, Any]
    ) -> tuple[CharacterArc, Any]:
        """Initialize a character in both systems with integration."""
        try:
            logger.info(f"Initializing integrated character {character_id}")

            # Create character in arc manager
            character_arc = await self.character_arc_manager.initialize_character_arc(
                character_id, base_personality
            )

            # Create character in development system
            character_state = self.character_development_system.create_character(
                character_id=character_id,
                name=base_personality.get("name", f"Character_{character_id}"),
                personality_traits=base_personality.copy(),
                therapeutic_role=base_personality.get("therapeutic_role", "companion"),
            )

            # Initial sync
            await self.data_synchronizer.sync_character_to_development_system(
                character_arc
            )

            # Record sync time
            self.last_sync_times[character_id] = datetime.now()

            logger.info(f"Successfully initialized integrated character {character_id}")
            return character_arc, character_state

        except Exception as e:
            logger.error(f"Error initializing integrated character {character_id}: {e}")
            raise

    async def process_integrated_interaction(
        self, character_id: str, player_interaction: PlayerInteraction
    ) -> bool:
        """Process an interaction through both systems with synchronization."""
        try:
            logger.debug(
                f"Processing integrated interaction for character {character_id}"
            )

            # Update character arc manager
            arc_success = await self.character_arc_manager.update_character_development(
                character_id, player_interaction
            )

            # Convert to development system interaction
            dev_interaction = Interaction(
                participants=[character_id, "player"],
                interaction_type=player_interaction.interaction_type,
                content=player_interaction.player_choice,
                emotional_impact=sum(player_interaction.emotional_impact.values())
                / max(1, len(player_interaction.emotional_impact)),
                therapeutic_value=player_interaction.therapeutic_relevance,
            )

            # Update development system
            dev_success = (
                self.character_development_system.update_character_from_interaction(
                    character_id, dev_interaction
                )
            )

            # Sync data between systems
            character_arc = self.character_arc_manager.get_character_arc(character_id)
            if character_arc:
                sync_success = (
                    await self.data_synchronizer.sync_character_to_development_system(
                        character_arc
                    )
                )
            else:
                sync_success = False

            success = arc_success and dev_success and sync_success

            if success:
                logger.debug(
                    f"Successfully processed integrated interaction for character {character_id}"
                )
            else:
                logger.warning(
                    f"Partial failure processing interaction for character {character_id}"
                )

            return success

        except Exception as e:
            logger.error(
                f"Error processing integrated interaction for character {character_id}: {e}"
            )
            return False

    async def generate_integrated_character_response(
        self, character_id: str, context: InteractionContext
    ) -> dict[str, Any]:
        """Generate character response using both systems for enhanced consistency."""
        try:
            logger.debug(f"Generating integrated response for character {character_id}")

            # Get response from arc manager
            arc_response = await self.character_arc_manager.generate_character_response(
                character_id, context
            )

            # Get dialogue context from development system
            from models.data_models import DialogueContext  # type: ignore[import-not-found]

            dialogue_context = DialogueContext(
                participants=[character_id] + context.participants,
                current_topic=context.metadata.get("topic", "general"),
                emotional_context=context.mood,
            )

            dev_context = (
                self.character_development_system.generate_character_dialogue_context(  # type: ignore[attr-defined]
                    character_id, dialogue_context
                )
            )

            # Validate consistency between systems
            character_state = self.character_development_system.get_character_state(
                character_id
            )
            if character_state:
                is_consistent, consistency_message = (
                    self.character_development_system.validate_character_consistency(  # type: ignore[attr-defined]
                        character_id, arc_response.response_text, dev_context
                    )
                )

                if not is_consistent:
                    logger.warning(
                        f"Consistency issue for character {character_id}: {consistency_message}"
                    )
                    # Could implement response adjustment here

            # Combine information from both systems
            integrated_response = {
                "response_text": arc_response.response_text,
                "emotional_tone": arc_response.emotional_tone,
                "personality_consistency_score": arc_response.personality_consistency_score,
                "therapeutic_modeling": arc_response.therapeutic_modeling,
                "relationship_impact": arc_response.relationship_impact,
                "arc_progression": arc_response.arc_progression,
                "development_system_context": dev_context,
                "consistency_validated": is_consistent if character_state else False,  # type: ignore[possibly-unbound]
                "metadata": {
                    **arc_response.metadata,
                    "integration_timestamp": datetime.now(),
                    "systems_synced": True,
                },
            }

            logger.debug(f"Generated integrated response for character {character_id}")
            return integrated_response

        except Exception as e:
            logger.error(
                f"Error generating integrated response for character {character_id}: {e}"
            )
            return {
                "response_text": "I'm having trouble responding right now.",
                "emotional_tone": "neutral",
                "error": str(e),
            }

    async def sync_character_data(
        self, character_id: str, force_sync: bool = False
    ) -> bool:
        """Synchronize character data between systems."""
        try:
            # Check if sync is needed
            last_sync = self.last_sync_times.get(character_id)
            if (
                not force_sync
                and last_sync
                and (datetime.now() - last_sync) < self.sync_interval
            ):
                return True  # No sync needed

            logger.debug(f"Syncing character data for {character_id}")

            character_arc = self.character_arc_manager.get_character_arc(character_id)
            if not character_arc:
                logger.warning(f"Character arc not found for {character_id}")
                return False

            # Sync to development system
            sync_to_success = (
                await self.data_synchronizer.sync_character_to_development_system(
                    character_arc
                )
            )

            # Sync from development system (to get any updates)
            sync_from_success = (
                await self.data_synchronizer.sync_character_from_development_system(
                    character_arc
                )
            )

            if sync_to_success and sync_from_success:
                self.last_sync_times[character_id] = datetime.now()
                logger.debug(f"Successfully synced character data for {character_id}")
                return True
            logger.warning(f"Partial sync failure for character {character_id}")
            return False

        except Exception as e:
            logger.error(f"Error syncing character data for {character_id}: {e}")
            return False

    async def evolve_integrated_relationships(
        self,
        character_id: str,
        interactions: list[PlayerInteraction],
        time_period: timedelta | None = None,
    ) -> dict[str, Any]:
        """Evolve relationships across both systems."""
        try:
            logger.debug(
                f"Evolving integrated relationships for character {character_id}"
            )

            character_arc = self.character_arc_manager.get_character_arc(character_id)
            if not character_arc:
                logger.warning(f"Character arc not found for {character_id}")
                return {}

            # Evolve relationships using relationship manager
            relationship_changes = (
                await self.relationship_manager.evolve_relationships_across_scales(
                    character_arc, interactions, time_period
                )
            )

            # Sync data after evolution
            await self.sync_character_data(character_id, force_sync=True)

            # Get updated relationship summary
            character_state = self.character_development_system.get_character_state(
                character_id
            )
            relationship_summary = {}

            if character_state:
                for other_char_id, score in character_state.relationship_scores.items():  # type: ignore[misc]
                    relationship_summary[other_char_id] = {
                        "score": score,
                        "description": self.character_development_system.relationship_tracker.get_relationship_description(  # type: ignore[attr-defined]
                            score
                        ),
                        "change": relationship_changes.get(other_char_id, 0.0),
                    }

            result = {
                "character_id": character_id,
                "relationship_changes": relationship_changes,
                "relationship_summary": relationship_summary,
                "evolution_timestamp": datetime.now(),
            }

            logger.debug(
                f"Successfully evolved relationships for character {character_id}"
            )
            return result

        except Exception as e:
            logger.error(
                f"Error evolving integrated relationships for character {character_id}: {e}"
            )
            return {}

    async def get_integrated_character_summary(
        self, character_id: str
    ) -> dict[str, Any]:
        """Get comprehensive character summary from both systems."""
        try:
            logger.debug(f"Getting integrated summary for character {character_id}")

            # Get arc manager data
            character_arc = self.character_arc_manager.get_character_arc(character_id)

            # Get development system data
            dev_summary = (
                self.character_development_system.get_character_development_summary(  # type: ignore[attr-defined]
                    character_id
                )
            )

            # Combine data
            integrated_summary = {
                "character_id": character_id,
                "arc_manager_data": {
                    "current_stage": (
                        character_arc.current_stage.value if character_arc else None
                    ),
                    "completed_milestones": (
                        len(character_arc.completed_milestones) if character_arc else 0
                    ),
                    "active_goals": (
                        len(character_arc.current_goals) if character_arc else 0
                    ),
                    "therapeutic_modeling": (
                        len(character_arc.therapeutic_modeling) if character_arc else 0
                    ),
                    "relationship_count": (
                        len(character_arc.relationship_dynamics) if character_arc else 0
                    ),
                },
                "development_system_data": dev_summary,
                "integration_status": {
                    "last_sync": self.last_sync_times.get(character_id),
                    "systems_connected": character_arc is not None
                    and bool(dev_summary),
                    "data_consistency": await self._check_data_consistency(
                        character_id
                    ),
                },
                "summary_timestamp": datetime.now(),
            }

            logger.debug(f"Generated integrated summary for character {character_id}")
            return integrated_summary

        except Exception as e:
            logger.error(
                f"Error getting integrated summary for character {character_id}: {e}"
            )
            return {"error": str(e)}

    async def _check_data_consistency(self, character_id: str) -> dict[str, bool]:
        """Check data consistency between systems."""
        try:
            character_arc = self.character_arc_manager.get_character_arc(character_id)
            character_state = self.character_development_system.get_character_state(
                character_id
            )

            if not character_arc or not character_state:
                return {"overall": False, "reason": "Missing character data"}  # type: ignore[return-value]

            consistency_checks = {
                "personality_traits": self._check_personality_consistency(
                    character_arc, character_state
                ),
                "relationships": self._check_relationship_consistency(
                    character_arc, character_state
                ),
                "basic_info": character_arc.character_name == character_state.name,
            }

            consistency_checks["overall"] = all(consistency_checks.values())

            return consistency_checks

        except Exception as e:
            logger.error(f"Error checking data consistency: {e}")
            return {"overall": False, "error": str(e)}  # type: ignore[return-value]

    def _check_personality_consistency(
        self, character_arc: CharacterArc, character_state
    ) -> bool:
        """Check personality trait consistency between systems."""
        try:
            for trait_name, arc_value in character_arc.personality_evolution.items():
                if trait_name in character_state.personality_traits:
                    dev_value = character_state.personality_traits[trait_name]
                    # Allow small differences due to different update mechanisms
                    if abs(arc_value - dev_value) > 0.2:
                        return False
            return True
        except Exception:
            return False

    def _check_relationship_consistency(
        self, character_arc: CharacterArc, character_state
    ) -> bool:
        """Check relationship consistency between systems."""
        try:
            # Check if player relationship exists in both systems
            player_relationship = character_arc.relationship_dynamics.get("player")
            player_score = character_state.relationship_scores.get("player")

            if player_relationship and player_score is not None:
                # Convert our detailed metrics to overall score
                arc_overall = (
                    player_relationship.trust_level
                    + player_relationship.affection_level
                ) / 2.0
                dev_overall = (player_score + 1.0) / 2.0  # Convert -1,1 to 0,1

                # Allow reasonable difference
                return abs(arc_overall - dev_overall) <= 0.3

            return True  # If no relationships to compare, consider consistent
        except Exception:
            return False
