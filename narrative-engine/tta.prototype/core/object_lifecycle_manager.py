"""
Object Lifecycle Manager for TTA Living Worlds

This module implements the ObjectLifecycleManager class that manages the history
and evolution of objects in the world. It handles object creation, aging, wear
simulation, interaction tracking, relationship management, and timeline integration.

Classes:
    ObjectLifecycleManager: Core manager for object lifecycle operations
    ObjectData: Data class for object initialization
    WearState: Result class for wear simulation operations
    Interaction: Data class for object interactions
"""

import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add models path for data models access
models_path = Path(__file__).parent.parent / "models"
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from living_worlds_models import (
        EntityType,
        EventType,
        ObjectHistory,
        ObjectRelationship,
        ObjectState,
        TimelineEvent,
        ValidationError,
        WearEvent,
    )
except ImportError:
    # Fallback for when running as part of package
    from ..models.living_worlds_models import (
        EntityType,
        EventType,
        ObjectHistory,
        ObjectState,
        TimelineEvent,
        ValidationError,
        WearEvent,
    )

# Import timeline engine for integration
try:
    from timeline_engine import TimelineEngine, TimeRange
except ImportError:
    from .timeline_engine import TimelineEngine

logger = logging.getLogger(__name__)


@dataclass
class ObjectData:
    """Data class for object initialization."""

    object_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    object_type: str = "generic"
    description: str = ""
    initial_condition: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    location_id: str | None = None
    owner_id: str | None = None
    creation_context: str = ""


@dataclass
class WearState:
    """Result class for wear simulation operations."""

    object_id: str = ""
    previous_condition: float = 1.0
    new_condition: float = 1.0
    previous_wear_level: float = 0.0
    new_wear_level: float = 0.0
    wear_applied: float = 0.0
    functionality_changed: bool = False
    was_functional: bool = True
    is_functional: bool = True
    wear_events_applied: int = 0
    simulation_successful: bool = True
    error_message: str = ""


@dataclass
class Interaction:
    """Data class for object interactions."""

    interaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    object_id: str = ""
    character_id: str = ""
    interaction_type: str = "use"  # use, examine, modify, repair, damage, etc.
    description: str = ""
    intensity: float = 1.0  # 0.0 to 1.0, how intense the interaction was
    duration_minutes: int = 1
    location_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    consequences: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ObjectLifecycleManager:
    """
    Core manager for object lifecycle operations.

    This class handles object creation, aging, wear simulation, interaction tracking,
    relationship management, and timeline integration for all objects in the living world.
    """

    def __init__(self, timeline_engine: TimelineEngine | None = None):
        """
        Initialize the Object Lifecycle Manager.

        Args:
            timeline_engine: Optional timeline engine for event integration
        """
        self.timeline_engine = timeline_engine
        self.object_histories: dict[str, ObjectHistory] = {}
        self.wear_simulation_enabled = True
        self.aging_rate = 1.0  # Multiplier for aging speed
        self.interaction_wear_multiplier = 1.0  # Multiplier for interaction-based wear

        logger.info("ObjectLifecycleManager initialized")

    def create_object_with_history(self, object_data: ObjectData) -> ObjectHistory:
        """
        Create a new object with complete history tracking.

        Args:
            object_data: Object initialization data

        Returns:
            ObjectHistory: The created object history

        Raises:
            ValidationError: If object data is invalid
        """
        try:
            # Validate object data
            if not object_data.name.strip():
                raise ValidationError("Object name cannot be empty")

            if not 0.0 <= object_data.initial_condition <= 1.0:
                raise ValidationError("Initial condition must be between 0.0 and 1.0")

            # Create object state
            object_state = ObjectState(
                object_id=object_data.object_id,
                name=object_data.name,
                object_type=object_data.object_type,
                description=object_data.description,
                current_condition=object_data.initial_condition,
                wear_level=0.0,
                current_location_id=object_data.location_id,
                current_owner_id=object_data.owner_id,
                is_functional=True,
                properties=object_data.properties.copy(),
                tags=object_data.tags.copy(),
            )

            # Create creation event
            creation_event = TimelineEvent(
                event_type=EventType.CREATION,
                title=f"Object Created: {object_data.name}",
                description=f"Object '{object_data.name}' of type '{object_data.object_type}' was created. {object_data.creation_context}",
                participants=[object_data.object_id],
                location_id=object_data.location_id,
                significance_level=7,
                tags=["creation", "object", object_data.object_type],
            )

            # Create object history
            object_history = ObjectHistory(
                object_id=object_data.object_id,
                object_state=object_state,
                creation_event=creation_event,
            )

            # Add initial ownership if specified
            if object_data.owner_id:
                object_history.ownership_history.append(object_data.owner_id)

            # Add initial location if specified
            if object_data.location_id:
                object_history.location_history.append(
                    (object_data.location_id, datetime.now())
                )

            # Validate the complete history
            object_history.validate()

            # Store in manager
            self.object_histories[object_data.object_id] = object_history

            # Add to timeline engine if available
            if self.timeline_engine:
                self.timeline_engine.create_timeline(
                    object_data.object_id, EntityType.OBJECT
                )
                self.timeline_engine.add_event(object_data.object_id, creation_event)

            logger.info(
                f"Created object with history: {object_data.name} ({object_data.object_id})"
            )
            return object_history

        except ValidationError as e:
            logger.error(f"Failed to create object with history: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating object: {e}")
            raise ValidationError(f"Failed to create object: {e}") from e

    def age_object(self, object_id: str, time_delta: timedelta) -> ObjectState:
        """
        Age an object over a specified time period.

        Args:
            object_id: Object identifier
            time_delta: Time period to age the object

        Returns:
            ObjectState: Updated object state after aging

        Raises:
            ValidationError: If object not found or aging fails
        """
        try:
            if object_id not in self.object_histories:
                raise ValidationError(f"Object not found: {object_id}")

            object_history = self.object_histories[object_id]

            # Calculate aging wear based on time delta
            days = time_delta.total_seconds() / (24 * 3600)
            base_aging_rate = 0.001  # 0.1% wear per day by default
            aging_wear = days * base_aging_rate * self.aging_rate

            # Apply material-specific aging modifiers
            object_type = object_history.object_state.object_type
            aging_modifiers = {
                "metal": 0.5,  # Metal ages slowly
                "wood": 1.2,  # Wood ages faster
                "fabric": 1.5,  # Fabric ages quickly
                "stone": 0.3,  # Stone ages very slowly
                "organic": 2.0,  # Organic materials age quickly
                "electronic": 0.8,  # Electronics age moderately
                "paper": 1.8,  # Paper ages quickly
                "glass": 0.4,  # Glass ages slowly
                "plastic": 0.7,  # Plastic ages moderately
                "generic": 1.0,  # Default aging rate
            }

            modifier = aging_modifiers.get(object_type, 1.0)
            aging_wear *= modifier

            # Cap aging wear to prevent excessive aging in single operation
            aging_wear = min(aging_wear, 0.1)  # Max 10% wear per aging operation

            if aging_wear > 0.001:  # Only apply if significant
                # Create aging wear event
                aging_event = WearEvent(
                    object_id=object_id,
                    wear_type="aging",
                    wear_amount=aging_wear,
                    description=f"Natural aging over {days:.1f} days",
                    timestamp=datetime.now(),
                )

                # Apply the aging
                if object_history.add_wear_event(aging_event):
                    logger.debug(
                        f"Applied aging wear {aging_wear:.3f} to object {object_id}"
                    )

                # Create timeline event for significant aging
                if aging_wear > 0.05:  # 5% threshold for timeline events
                    aging_timeline_event = TimelineEvent(
                        event_type=EventType.ENVIRONMENTAL_CHANGE,
                        title=f"Significant Aging: {object_history.object_state.name}",
                        description=f"Object has aged significantly over {days:.1f} days, showing visible wear",
                        participants=[object_id],
                        location_id=object_history.object_state.current_location_id,
                        significance_level=4,
                        emotional_impact=-0.2,  # Aging is generally negative
                        tags=["aging", "wear", "time"],
                    )

                    object_history.add_modification_event(aging_timeline_event)

                    # Add to timeline engine if available
                    if self.timeline_engine:
                        timeline = self.timeline_engine.get_timeline(object_id)
                        if timeline:
                            self.timeline_engine.add_event(
                                object_id, aging_timeline_event
                            )

            return object_history.object_state

        except ValidationError as e:
            logger.error(f"Failed to age object: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error aging object: {e}")
            raise ValidationError(f"Failed to age object: {e}") from e

    def handle_object_interaction(
        self, object_id: str, interaction: Interaction
    ) -> bool:
        """
        Handle an interaction with an object and update its state accordingly.

        Args:
            object_id: Object identifier
            interaction: Interaction details

        Returns:
            bool: True if interaction was handled successfully
        """
        try:
            if object_id not in self.object_histories:
                raise ValidationError(f"Object not found: {object_id}")

            # Validate interaction
            if not interaction.character_id.strip():
                raise ValidationError("Character ID cannot be empty")

            if not interaction.description.strip():
                raise ValidationError("Interaction description cannot be empty")

            if not 0.0 <= interaction.intensity <= 1.0:
                raise ValidationError(
                    "Interaction intensity must be between 0.0 and 1.0"
                )

            object_history = self.object_histories[object_id]

            # Create interaction timeline event
            interaction_event = TimelineEvent(
                event_type=EventType.PLAYER_INTERACTION,
                title=f"Interaction: {interaction.interaction_type}",
                description=interaction.description,
                participants=[object_id, interaction.character_id],
                location_id=interaction.location_id
                or object_history.object_state.current_location_id,
                timestamp=interaction.timestamp,
                significance_level=max(3, int(interaction.intensity * 5) + 2),
                emotional_impact=(
                    0.1 if interaction.interaction_type in ["use", "examine"] else 0.0
                ),
                consequences=interaction.consequences.copy(),
                tags=[interaction.interaction_type, "interaction", "object"],
                metadata=interaction.metadata.copy(),
            )

            # Add interaction event to history
            object_history.add_interaction_event(interaction_event)

            # Calculate wear from interaction
            wear_amount = self._calculate_interaction_wear(
                interaction, object_history.object_state
            )

            if wear_amount > 0.001:  # Apply wear if significant
                wear_event = WearEvent(
                    object_id=object_id,
                    wear_type="interaction",
                    wear_amount=wear_amount,
                    description=f"Wear from {interaction.interaction_type} interaction",
                    timestamp=interaction.timestamp,
                    caused_by=interaction.character_id,
                    location_id=interaction.location_id,
                )

                object_history.add_wear_event(wear_event)

            # Handle special interaction types
            if interaction.interaction_type == "repair":
                self._handle_repair_interaction(object_history, interaction)
            elif interaction.interaction_type == "damage":
                self._handle_damage_interaction(object_history, interaction)
            elif interaction.interaction_type == "modify":
                self._handle_modification_interaction(object_history, interaction)

            # Add to timeline engine if available
            if self.timeline_engine:
                timeline = self.timeline_engine.get_timeline(object_id)
                if timeline:
                    self.timeline_engine.add_event(object_id, interaction_event)

            logger.debug(
                f"Handled interaction {interaction.interaction_type} for object {object_id}"
            )
            return True

        except ValidationError as e:
            logger.error(f"Failed to handle object interaction: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error handling interaction: {e}")
            return False

    def get_object_history(self, object_id: str) -> ObjectHistory | None:
        """
        Get the complete history of an object.

        Args:
            object_id: Object identifier

        Returns:
            Optional[ObjectHistory]: Object history or None if not found
        """
        return self.object_histories.get(object_id)

    def update_object_relationships(
        self, object_id: str, relationships: dict[str, Any]
    ) -> bool:
        """
        Update relationships for an object.

        Args:
            object_id: Object identifier
            relationships: Dictionary of relationship updates
                Format: {
                    'add': [{'to_entity_id': str, 'to_entity_type': str, 'relationship_type': str, 'strength': float}],
                    'remove': [{'to_entity_id': str, 'relationship_type': str}],
                    'update': [{'to_entity_id': str, 'relationship_type': str, 'strength': float}]
                }

        Returns:
            bool: True if relationships were updated successfully
        """
        try:
            if object_id not in self.object_histories:
                raise ValidationError(f"Object not found: {object_id}")

            object_history = self.object_histories[object_id]

            # Add new relationships
            if "add" in relationships:
                for rel_data in relationships["add"]:
                    success = object_history.add_relationship(
                        rel_data["to_entity_id"],
                        rel_data["to_entity_type"],
                        rel_data["relationship_type"],
                        rel_data.get("strength", 1.0),
                    )
                    if not success:
                        logger.warning(f"Failed to add relationship: {rel_data}")

            # Remove relationships
            if "remove" in relationships:
                for rel_data in relationships["remove"]:
                    relationship = object_history.get_relationship(
                        rel_data["to_entity_id"], rel_data["relationship_type"]
                    )
                    if relationship:
                        relationship.is_active = False
                        logger.debug(f"Deactivated relationship: {rel_data}")

            # Update existing relationships
            if "update" in relationships:
                for rel_data in relationships["update"]:
                    relationship = object_history.get_relationship(
                        rel_data["to_entity_id"], rel_data["relationship_type"]
                    )
                    if relationship:
                        relationship.strength = rel_data.get(
                            "strength", relationship.strength
                        )
                        logger.debug(f"Updated relationship strength: {rel_data}")

            object_history.last_updated = datetime.now()
            logger.info(f"Updated relationships for object {object_id}")
            return True

        except ValidationError as e:
            logger.error(f"Failed to update object relationships: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating relationships: {e}")
            return False

    def simulate_object_wear(
        self, object_id: str, usage_events: list[TimelineEvent]
    ) -> WearState:
        """
        Simulate wear on an object based on usage events.

        Args:
            object_id: Object identifier
            usage_events: List of timeline events representing usage

        Returns:
            WearState: Result of wear simulation
        """
        wear_state = WearState(object_id=object_id)

        try:
            if object_id not in self.object_histories:
                wear_state.simulation_successful = False
                wear_state.error_message = f"Object not found: {object_id}"
                return wear_state

            object_history = self.object_histories[object_id]

            # Record initial state
            wear_state.previous_condition = (
                object_history.object_state.current_condition
            )
            wear_state.previous_wear_level = object_history.object_state.wear_level
            wear_state.was_functional = object_history.object_state.is_functional

            total_wear = 0.0
            events_processed = 0

            for event in usage_events:
                # Calculate wear based on event properties
                base_wear = 0.01  # 1% base wear per usage event

                # Adjust wear based on event type
                wear_multipliers = {
                    EventType.PLAYER_INTERACTION: 1.0,
                    EventType.CONFLICT: 2.0,
                    EventType.ENVIRONMENTAL_CHANGE: 0.5,
                    EventType.CUSTOM: 1.0,
                }

                multiplier = wear_multipliers.get(event.event_type, 1.0)

                # Adjust based on emotional impact (negative impact = more wear)
                if event.emotional_impact < 0:
                    multiplier *= 1.0 + abs(event.emotional_impact)

                # Adjust based on significance level
                significance_multiplier = (
                    event.significance_level / 5.0
                )  # Normalize to ~1.0

                event_wear = (
                    base_wear
                    * multiplier
                    * significance_multiplier
                    * self.interaction_wear_multiplier
                )
                event_wear = min(event_wear, 0.05)  # Cap at 5% per event

                if event_wear > 0.001:  # Only apply significant wear
                    wear_event = WearEvent(
                        object_id=object_id,
                        wear_type="usage",
                        wear_amount=event_wear,
                        description=f"Wear from event: {event.title}",
                        timestamp=event.timestamp,
                        caused_by=event.participants[0] if event.participants else None,
                        location_id=event.location_id,
                    )

                    if object_history.add_wear_event(wear_event):
                        total_wear += event_wear
                        events_processed += 1

            # Record final state
            wear_state.new_condition = object_history.object_state.current_condition
            wear_state.new_wear_level = object_history.object_state.wear_level
            wear_state.is_functional = object_history.object_state.is_functional
            wear_state.wear_applied = total_wear
            wear_state.functionality_changed = (
                wear_state.was_functional != wear_state.is_functional
            )
            wear_state.wear_events_applied = events_processed
            wear_state.simulation_successful = True

            logger.info(
                f"Simulated wear for object {object_id}: {total_wear:.3f} total wear from {events_processed} events"
            )
            return wear_state

        except Exception as e:
            wear_state.simulation_successful = False
            wear_state.error_message = str(e)
            logger.error(f"Failed to simulate object wear: {e}")
            return wear_state

    def get_object_summary(self, object_id: str) -> dict[str, Any] | None:
        """
        Get a summary of an object's current state and history.

        Args:
            object_id: Object identifier

        Returns:
            Optional[Dict[str, Any]]: Object summary or None if not found
        """
        if object_id not in self.object_histories:
            return None

        object_history = self.object_histories[object_id]

        return {
            "object_id": object_id,
            "name": object_history.object_state.name,
            "type": object_history.object_state.object_type,
            "condition": object_history.object_state.current_condition,
            "wear_level": object_history.object_state.wear_level,
            "is_functional": object_history.object_state.is_functional,
            "current_location": object_history.object_state.current_location_id,
            "current_owner": object_history.object_state.current_owner_id,
            "creation_date": (
                object_history.creation_event.timestamp
                if object_history.creation_event
                else None
            ),
            "total_interactions": len(object_history.interaction_events),
            "total_modifications": len(object_history.modification_events),
            "total_wear_events": len(object_history.wear_timeline),
            "active_relationships": len(
                [r for r in object_history.relationships if r.is_active]
            ),
            "wear_summary": object_history.get_wear_summary(),
            "recent_interactions": len(object_history.get_recent_interactions()),
            "last_updated": object_history.last_updated,
        }

    def _calculate_interaction_wear(
        self, interaction: Interaction, object_state: ObjectState
    ) -> float:
        """Calculate wear amount from an interaction."""
        base_wear = 0.005  # 0.5% base wear per interaction

        # Adjust based on interaction type
        wear_rates = {
            "use": 1.0,
            "examine": 0.1,
            "repair": -0.5,  # Repair reduces wear (handled separately)
            "damage": 3.0,
            "modify": 1.5,
            "move": 0.3,
            "clean": 0.2,
        }

        type_multiplier = wear_rates.get(interaction.interaction_type, 1.0)

        # Adjust based on intensity and duration
        intensity_multiplier = interaction.intensity
        duration_multiplier = min(
            interaction.duration_minutes / 60.0, 2.0
        )  # Cap at 2 hours

        # Adjust based on object condition (worn objects wear faster)
        condition_multiplier = 1.0 + (1.0 - object_state.current_condition) * 0.5

        wear_amount = (
            base_wear
            * type_multiplier
            * intensity_multiplier
            * duration_multiplier
            * condition_multiplier
        )

        # Ensure wear is positive (except for repair)
        if interaction.interaction_type != "repair":
            wear_amount = max(0.0, wear_amount)

        return min(wear_amount, 0.1)  # Cap at 10% per interaction

    def _handle_repair_interaction(
        self, object_history: ObjectHistory, interaction: Interaction
    ):
        """Handle repair-specific interaction logic."""
        repair_amount = (
            interaction.intensity * 0.3
        )  # Up to 30% repair based on intensity

        if object_history.object_state.repair(repair_amount):
            repair_event = TimelineEvent(
                event_type=EventType.OBJECT_MODIFICATION,
                title=f"Repair: {object_history.object_state.name}",
                description=f"Object repaired by {interaction.character_id}, condition improved",
                participants=[object_history.object_id, interaction.character_id],
                location_id=interaction.location_id,
                timestamp=interaction.timestamp,
                significance_level=6,
                emotional_impact=0.3,  # Repair is positive
                tags=["repair", "improvement", "maintenance"],
            )

            object_history.add_modification_event(repair_event)

    def _handle_damage_interaction(
        self, object_history: ObjectHistory, interaction: Interaction
    ):
        """Handle damage-specific interaction logic."""
        damage_amount = (
            interaction.intensity * 0.2
        )  # Up to 20% damage based on intensity

        # Apply additional wear for damage
        damage_wear = WearEvent(
            object_id=object_history.object_id,
            wear_type="damage",
            wear_amount=damage_amount,
            description=f"Damage from {interaction.interaction_type} interaction",
            timestamp=interaction.timestamp,
            caused_by=interaction.character_id,
            location_id=interaction.location_id,
        )

        object_history.add_wear_event(damage_wear)

        damage_event = TimelineEvent(
            event_type=EventType.CONFLICT,
            title=f"Damage: {object_history.object_state.name}",
            description="Object damaged during interaction, condition reduced",
            participants=[object_history.object_id, interaction.character_id],
            location_id=interaction.location_id,
            timestamp=interaction.timestamp,
            significance_level=7,
            emotional_impact=-0.4,  # Damage is negative
            tags=["damage", "conflict", "deterioration"],
        )

        object_history.add_modification_event(damage_event)

    def _handle_modification_interaction(
        self, object_history: ObjectHistory, interaction: Interaction
    ):
        """Handle modification-specific interaction logic."""
        modification_event = TimelineEvent(
            event_type=EventType.OBJECT_MODIFICATION,
            title=f"Modification: {object_history.object_state.name}",
            description=f"Object modified by {interaction.character_id}",
            participants=[object_history.object_id, interaction.character_id],
            location_id=interaction.location_id,
            timestamp=interaction.timestamp,
            significance_level=5,
            emotional_impact=0.1,
            tags=["modification", "change", "customization"],
        )

        object_history.add_modification_event(modification_event)

    def cleanup_old_events(
        self, days_to_keep: int = 365, min_significance: int = 7
    ) -> dict[str, int]:
        """
        Clean up old, low-significance events from object histories.

        Args:
            days_to_keep: Keep events from the last N days
            min_significance: Always keep events above this significance level

        Returns:
            Dict[str, int]: Summary of cleanup results
        """
        cleanup_results = {
            "objects_processed": 0,
            "interaction_events_removed": 0,
            "modification_events_removed": 0,
            "wear_events_removed": 0,
            "total_events_removed": 0,
        }

        cutoff_time = datetime.now() - timedelta(days=days_to_keep)

        for _object_id, object_history in self.object_histories.items():
            initial_interaction_count = len(object_history.interaction_events)
            initial_modification_count = len(object_history.modification_events)
            initial_wear_count = len(object_history.wear_timeline)

            # Clean interaction events
            object_history.interaction_events = [
                event
                for event in object_history.interaction_events
                if (
                    event.timestamp >= cutoff_time
                    or event.significance_level >= min_significance
                )
            ]

            # Clean modification events
            object_history.modification_events = [
                event
                for event in object_history.modification_events
                if (
                    event.timestamp >= cutoff_time
                    or event.significance_level >= min_significance
                )
            ]

            # Clean wear events (keep more recent ones as they affect current state)
            wear_cutoff = datetime.now() - timedelta(
                days=days_to_keep // 2
            )  # Keep wear events longer
            object_history.wear_timeline = [
                wear
                for wear in object_history.wear_timeline
                if wear.timestamp >= wear_cutoff
            ]

            # Update counts
            interaction_removed = initial_interaction_count - len(
                object_history.interaction_events
            )
            modification_removed = initial_modification_count - len(
                object_history.modification_events
            )
            wear_removed = initial_wear_count - len(object_history.wear_timeline)

            if interaction_removed > 0 or modification_removed > 0 or wear_removed > 0:
                object_history.last_updated = datetime.now()
                cleanup_results["objects_processed"] += 1
                cleanup_results["interaction_events_removed"] += interaction_removed
                cleanup_results["modification_events_removed"] += modification_removed
                cleanup_results["wear_events_removed"] += wear_removed

        cleanup_results["total_events_removed"] = (
            cleanup_results["interaction_events_removed"]
            + cleanup_results["modification_events_removed"]
            + cleanup_results["wear_events_removed"]
        )

        logger.info(f"Cleanup completed: {cleanup_results}")
        return cleanup_results

    def get_manager_statistics(self) -> dict[str, Any]:
        """Get statistics about the object lifecycle manager."""
        total_objects = len(self.object_histories)
        total_interactions = sum(
            len(oh.interaction_events) for oh in self.object_histories.values()
        )
        total_modifications = sum(
            len(oh.modification_events) for oh in self.object_histories.values()
        )
        total_wear_events = sum(
            len(oh.wear_timeline) for oh in self.object_histories.values()
        )
        total_relationships = sum(
            len([r for r in oh.relationships if r.is_active])
            for oh in self.object_histories.values()
        )

        functional_objects = sum(
            1 for oh in self.object_histories.values() if oh.object_state.is_functional
        )
        average_condition = sum(
            oh.object_state.current_condition for oh in self.object_histories.values()
        ) / max(total_objects, 1)
        average_wear = sum(
            oh.object_state.wear_level for oh in self.object_histories.values()
        ) / max(total_objects, 1)

        return {
            "total_objects": total_objects,
            "functional_objects": functional_objects,
            "broken_objects": total_objects - functional_objects,
            "total_interactions": total_interactions,
            "total_modifications": total_modifications,
            "total_wear_events": total_wear_events,
            "total_relationships": total_relationships,
            "average_condition": round(average_condition, 3),
            "average_wear_level": round(average_wear, 3),
            "wear_simulation_enabled": self.wear_simulation_enabled,
            "aging_rate": self.aging_rate,
            "interaction_wear_multiplier": self.interaction_wear_multiplier,
        }


# Utility functions for object lifecycle management
def create_sample_object_data(name: str, object_type: str = "generic") -> ObjectData:
    """Create sample object data for testing."""
    return ObjectData(
        name=name,
        object_type=object_type,
        description=f"A {object_type} object named {name}",
        initial_condition=1.0,
        properties={"material": object_type, "size": "medium"},
        tags=[object_type, "sample"],
        creation_context=f"Created as sample {object_type} object",
    )


def create_sample_interaction(
    object_id: str, character_id: str, interaction_type: str = "use"
) -> Interaction:
    """Create sample interaction for testing."""
    return Interaction(
        object_id=object_id,
        character_id=character_id,
        interaction_type=interaction_type,
        description=f"Character {character_id} performed {interaction_type} on object {object_id}",
        intensity=0.5,
        duration_minutes=10,
        consequences=[f"Object was {interaction_type}d"],
    )


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)

    # Create manager
    manager = ObjectLifecycleManager()

    # Create sample object
    object_data = create_sample_object_data("Test Sword", "weapon")
    object_history = manager.create_object_with_history(object_data)

    # Simulate some interactions
    interaction = create_sample_interaction(object_data.object_id, "player1", "use")
    manager.handle_object_interaction(object_data.object_id, interaction)

    # Age the object
    manager.age_object(object_data.object_id, timedelta(days=30))

    # Get summary
    summary = manager.get_object_summary(object_data.object_id)
    print(f"Object summary: {summary}")

    # Get manager statistics
    stats = manager.get_manager_statistics()
    print(f"Manager statistics: {stats}")
