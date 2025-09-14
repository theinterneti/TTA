"""
Living Worlds Persistence Layer

This module provides the persistence layer for Living Worlds features,
integrating with Neo4j for data storage and Redis for caching.
It handles timeline events, world state data, and family relationships.

Classes:
    LivingWorldsPersistence: Main persistence interface for Living Worlds
    TimelinePersistence: Specialized persistence for timeline data
    WorldStatePersistence: Specialized persistence for world state data
"""

import json
import logging
from datetime import datetime
from typing import Any

try:
    from neo4j import Driver
except ImportError:
    Driver = None

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    from .living_worlds_schema import LivingWorldsQueryHelper, LivingWorldsSchemaManager
    from .redis_cache import RedisCache
except ImportError:
    from living_worlds_schema import LivingWorldsQueryHelper, LivingWorldsSchemaManager
    try:
        from redis_cache import RedisCache
    except ImportError:
        RedisCache = None

# Import Living Worlds models
try:
    from ..models.living_worlds_models import (
        EntityType,
        EventType,
        FamilyRelationship,
        FamilyTree,
        RelationshipType,
        Timeline,
        TimelineEvent,
        ValidationError,
        WorldState,
        WorldStateFlag,
    )
except ImportError:
    try:
        from models.living_worlds_models import (
            EntityType,
            EventType,
            FamilyRelationship,
            FamilyTree,
            RelationshipType,
            Timeline,
            TimelineEvent,
            ValidationError,
            WorldState,
            WorldStateFlag,
        )
    except ImportError:
        # Direct import for standalone testing
        import sys
        from pathlib import Path
        models_path = Path(__file__).parent.parent / "models"
        if str(models_path) not in sys.path:
            sys.path.insert(0, str(models_path))
        from living_worlds_models import (
            EventType,
            FamilyTree,
            Timeline,
            TimelineEvent,
            ValidationError,
            WorldState,
        )

logger = logging.getLogger(__name__)


class PersistenceError(Exception):
    """Raised when persistence operations fail."""
    pass


class TimelinePersistence:
    """
    Specialized persistence layer for timeline data.

    Handles storage and retrieval of timelines and timeline events
    with caching support for performance optimization.
    """

    def __init__(self, query_helper: LivingWorldsQueryHelper, cache: RedisCache | None = None):
        """
        Initialize timeline persistence.

        Args:
            query_helper: Living Worlds query helper instance
            cache: Optional Redis cache instance
        """
        self.query_helper = query_helper
        self.cache = cache
        self.cache_ttl = 3600  # 1 hour default TTL

    def save_timeline(self, timeline: Timeline) -> bool:
        """
        Save a timeline to Neo4j and cache.

        Args:
            timeline: Timeline instance to save

        Returns:
            bool: True if save was successful
        """
        try:
            timeline.validate()

            # Save timeline to Neo4j
            timeline_data = timeline.to_dict()

            # Create or update timeline node
            success = self.query_helper.create_timeline(
                timeline.timeline_id,
                timeline.entity_id,
                timeline.entity_type.value,
                created_at=timeline.created_at.isoformat(),
                last_updated=timeline.last_updated.isoformat(),
                metadata=json.dumps(timeline.metadata)
            )

            if not success:
                logger.error(f"Failed to save timeline {timeline.timeline_id} to Neo4j")
                return False

            # Save events
            for event in timeline.events:
                if not self.save_timeline_event(timeline.timeline_id, event):
                    logger.error(f"Failed to save event {event.event_id}")
                    return False

            # Cache the timeline
            if self.cache:
                cache_key = f"timeline:{timeline.timeline_id}"
                self.cache.set(cache_key, timeline_data, ttl=self.cache_ttl)

            logger.debug(f"Successfully saved timeline {timeline.timeline_id}")
            return True

        except ValidationError as e:
            logger.error(f"Timeline validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving timeline: {e}")
            return False

    def load_timeline(self, timeline_id: str) -> Timeline | None:
        """
        Load a timeline from cache or Neo4j.

        Args:
            timeline_id: Timeline identifier

        Returns:
            Optional[Timeline]: Timeline instance or None if not found
        """
        try:
            # Try cache first
            if self.cache:
                cache_key = f"timeline:{timeline_id}"
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    return Timeline.from_dict(cached_data)

            # Load from Neo4j
            timeline_data = self._load_timeline_from_neo4j(timeline_id)
            if not timeline_data:
                return None

            timeline = Timeline.from_dict(timeline_data)

            # Cache the loaded timeline
            if self.cache:
                cache_key = f"timeline:{timeline_id}"
                self.cache.set(cache_key, timeline_data, ttl=self.cache_ttl)

            return timeline

        except Exception as e:
            logger.error(f"Error loading timeline {timeline_id}: {e}")
            return None

    def save_timeline_event(self, timeline_id: str, event: TimelineEvent) -> bool:
        """
        Save a timeline event to Neo4j.

        Args:
            timeline_id: Timeline identifier
            event: Timeline event to save

        Returns:
            bool: True if save was successful
        """
        try:
            event.validate()

            success = self.query_helper.create_timeline_event(
                event.event_id,
                timeline_id,
                event.event_type.value,
                event.title,
                event.description,
                timestamp=event.timestamp.isoformat(),
                significance_level=event.significance_level,
                emotional_impact=event.emotional_impact,
                participants=event.participants,
                consequences=event.consequences,
                tags=event.tags,
                location_id=event.location_id,
                metadata=json.dumps(event.metadata)
            )

            if success:
                # Invalidate timeline cache since it has new events
                if self.cache:
                    cache_key = f"timeline:{timeline_id}"
                    self.cache.delete(cache_key)

                logger.debug(f"Successfully saved event {event.event_id}")

            return success

        except ValidationError as e:
            logger.error(f"Event validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving timeline event: {e}")
            return False

    def get_timeline_events(self, timeline_id: str, limit: int = 50,
                          min_significance: int = 1,
                          world_id: str | None = None,
                          entity_id: str | None = None) -> list[TimelineEvent]:
        """
        Get events from a timeline.

        Args:
            timeline_id: Timeline identifier
            limit: Maximum number of events to return
            min_significance: Minimum significance level
            world_id: Optional world context to prefer LW recent cache
            entity_id: Optional entity context to prefer LW recent cache

            # LW keyspace short-circuit when context provided
            if world_id and entity_id and self.cache:
                try:
                    from .living_worlds_cache import LivingWorldsCache
                except Exception:
                    from living_worlds_cache import LivingWorldsCache  # type: ignore
                lwc = LivingWorldsCache(self.cache)
                recent = lwc.get_recent_timeline_events(world_id, entity_id)
                if recent:
                    return [TimelineEvent.from_dict(e) for e in recent][:limit]

        Returns:
            List[TimelineEvent]: List of timeline events
        """
        try:
            # Try cache first for recent events (legacy + LW keyspace)
            cache_key = f"timeline_events:{timeline_id}:{limit}:{min_significance}"
            if self.cache:
                cached_events = self.cache.get(cache_key)
                if cached_events:
                    return [TimelineEvent.from_dict(event_data) for event_data in cached_events]

            # Load from Neo4j
            event_data_list = self.query_helper.get_timeline_events(timeline_id, limit, min_significance)
            events = []

            for event_data in event_data_list:
                try:
                    # Convert Neo4j data to TimelineEvent
                    event = self._neo4j_data_to_timeline_event(event_data)
                    events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to convert event data: {e}")
                    continue

            # Cache the events (legacy key)
            if self.cache and events:
                event_dicts = [event.to_dict() for event in events]
                self.cache.set(cache_key, event_dicts, ttl=self.cache_ttl // 2)  # Shorter TTL for events

            # Additionally store recent events by LW keyspace when possible
            try:
                # Try to derive entity_id: the timeline node contains entity_id
                tl = self._load_timeline_from_neo4j(timeline_id)
                if tl and self.cache:
                    entity_id = tl.get("entity_id")
                    # Attempt to find a world_id from events metadata
                    world_id = None
                    for e in events:
                        md = getattr(e, 'metadata', {}) or {}
                        wid = md.get('world_id')
                        if wid:
                            world_id = wid
                            break
                    if entity_id and world_id:
                        try:
                            from .living_worlds_cache import LivingWorldsCache
                        except Exception:
                            from living_worlds_cache import (
                                LivingWorldsCache,  # type: ignore
                            )
                        lwc = LivingWorldsCache(self.cache)
                        lwc.set_recent_timeline_events(world_id, entity_id, [ev.to_dict() for ev in events[:50]], ttl=600)
            except Exception:
                logger.debug("LW recent timeline cache fill failed", exc_info=True)

            return events

        except Exception as e:
            logger.error(f"Error getting timeline events: {e}")
            return []

    def delete_timeline(self, timeline_id: str) -> bool:
        """
        Delete a timeline and all its events.

        Args:
            timeline_id: Timeline identifier

        Returns:
            bool: True if deletion was successful
        """
        try:
            # Delete from Neo4j
            query = """
            MATCH (t:Timeline {timeline_id: $timeline_id})
            OPTIONAL MATCH (t)-[:CONTAINS_EVENT]->(e:TimelineEvent)
            DETACH DELETE t, e
            """

            with self.query_helper.driver.session() as session:
                session.run(query, timeline_id=timeline_id)

            # Remove from cache
            if self.cache:
                cache_key = f"timeline:{timeline_id}"
                self.cache.delete(cache_key)
                # Also remove any cached events
                pattern = f"timeline_events:{timeline_id}:*"
                self.cache.delete_pattern(pattern)

            logger.debug(f"Successfully deleted timeline {timeline_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting timeline {timeline_id}: {e}")
            return False

    def _load_timeline_from_neo4j(self, timeline_id: str) -> dict[str, Any] | None:
        """Load timeline data from Neo4j."""
        query = """
        MATCH (t:Timeline {timeline_id: $timeline_id})
        OPTIONAL MATCH (t)-[:CONTAINS_EVENT]->(e:TimelineEvent)
        RETURN t,
               collect(e) as events
        ORDER BY e.timestamp
        """

        try:
            with self.query_helper.driver.session() as session:
                result = session.run(query, timeline_id=timeline_id)
                record = result.single()

                if not record:
                    return None

                timeline_data = dict(record["t"])
                events_data = [dict(event) for event in record["events"] if event]

                # Convert to Timeline format
                timeline_dict = {
                    "timeline_id": timeline_data["timeline_id"],
                    "entity_id": timeline_data["entity_id"],
                    "entity_type": timeline_data["entity_type"],
                    "created_at": timeline_data["created_at"],
                    "last_updated": timeline_data["last_updated"],
                    "metadata": json.loads(timeline_data.get("metadata", "{}")),
                    "events": [self._neo4j_data_to_timeline_event(event_data).to_dict()
                              for event_data in events_data]
                }

                return timeline_dict

        except Exception as e:
            logger.error(f"Error loading timeline from Neo4j: {e}")
            return None

    def _neo4j_data_to_timeline_event(self, event_data: dict[str, Any]) -> TimelineEvent:
        """Convert Neo4j event data to TimelineEvent instance."""
        return TimelineEvent(
            event_id=event_data["event_id"],
            event_type=EventType(event_data["event_type"]),
            title=event_data["title"],
            description=event_data["description"],
            participants=event_data.get("participants", []),
            location_id=event_data.get("location_id"),
            timestamp=event_data["timestamp"],
            consequences=event_data.get("consequences", []),
            emotional_impact=event_data.get("emotional_impact", 0.0),
            significance_level=event_data.get("significance_level", 5),
            tags=event_data.get("tags", []),
            metadata=json.loads(event_data.get("metadata", "{}")),
            created_at=event_data.get("created_at", datetime.now())
        )


class WorldStatePersistence:
    """
    Specialized persistence layer for world state data.

    Handles storage and retrieval of world states with caching
    and efficient updates for frequently changing data.
    """

    def __init__(self, query_helper: LivingWorldsQueryHelper, cache: RedisCache | None = None):
        """
        Initialize world state persistence.

        Args:
            query_helper: Living Worlds query helper instance
            cache: Optional Redis cache instance
        """
        self.query_helper = query_helper
        self.cache = cache
        self.cache_ttl = 1800  # 30 minutes default TTL for world states

    def save_world_state(self, world_state: WorldState) -> bool:
        """
        Save a world state to Neo4j and cache.

        Args:
            world_state: WorldState instance to save

        Returns:
            bool: True if save was successful
        """
        try:
            world_state.validate()

            # Prepare world state data
            world_data = {
                'current_time': world_state.current_time.isoformat(),
                'world_status': world_state.world_status.value,
                'last_evolution': world_state.last_evolution.isoformat(),
                'player_last_visit': world_state.player_last_visit.isoformat() if world_state.player_last_visit else None,
                'world_flags': json.dumps(world_state.world_flags),
                'evolution_schedule': json.dumps(world_state.evolution_schedule),
                'active_characters': json.dumps(world_state.active_characters),
                'active_locations': json.dumps(world_state.active_locations),
                'active_objects': json.dumps(world_state.active_objects),
                'created_at': world_state.created_at.isoformat(),
                'last_updated': world_state.last_updated.isoformat(),
                'metadata': json.dumps(world_state.metadata)
            }

            # Save to Neo4j
            success = self.query_helper.create_world_state(
                world_state.world_id,
                world_state.world_name,
                **world_data
            )

            if not success:
                # Try updating existing world state
                success = self.query_helper.update_world_state(world_state.world_id, world_data)

            if success:
                # Cache the world state
                if self.cache:
                    cache_key = f"world_state:{world_state.world_id}"
                    self.cache.set(cache_key, world_state.to_dict(), ttl=self.cache_ttl)

                logger.debug(f"Successfully saved world state {world_state.world_id}")

            return success

        except ValidationError as e:
            logger.error(f"World state validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving world state: {e}")
            return False

    def load_world_state(self, world_id: str) -> WorldState | None:
        """
        Load a world state from cache or Neo4j.

        Args:
            world_id: World identifier

        Returns:
            Optional[WorldState]: WorldState instance or None if not found
        """
        try:
            # Try cache first
            if self.cache:
                cache_key = f"world_state:{world_id}"
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    return WorldState.from_dict(cached_data)

            # Load from Neo4j
            world_data = self.query_helper.get_world_state(world_id)
            if not world_data:
                return None

            # Convert Neo4j data to WorldState
            world_state_dict = self._neo4j_data_to_world_state(world_data)
            world_state = WorldState.from_dict(world_state_dict)

            # Cache the loaded world state
            if self.cache:
                cache_key = f"world_state:{world_id}"
                self.cache.set(cache_key, world_state.to_dict(), ttl=self.cache_ttl)

            return world_state

        except Exception as e:
            logger.error(f"Error loading world state {world_id}: {e}")
            return None

    def update_world_state(self, world_id: str, updates: dict[str, Any]) -> bool:
        """
        Update specific world state properties.

        Args:
            world_id: World identifier
            updates: Dictionary of properties to update

        Returns:
            bool: True if update was successful
        """
        try:
            # Add last_updated timestamp
            updates['last_updated'] = datetime.now().isoformat()

            # Update in Neo4j
            success = self.query_helper.update_world_state(world_id, updates)

            if success:
                # Invalidate cache to force reload
                if self.cache:
                    cache_key = f"world_state:{world_id}"
                    self.cache.delete(cache_key)

                logger.debug(f"Successfully updated world state {world_id}")

            return success

        except Exception as e:
            logger.error(f"Error updating world state: {e}")
            return False

    def _neo4j_data_to_world_state(self, world_data: dict[str, Any]) -> dict[str, Any]:
        """Convert Neo4j world data to WorldState format."""
        return {
            "world_id": world_data["world_id"],
            "world_name": world_data["world_name"],
            "current_time": world_data["current_time"],
            "world_status": world_data["world_status"],
            "last_evolution": world_data["last_evolution"],
            "player_last_visit": world_data.get("player_last_visit"),
            "world_flags": json.loads(world_data.get("world_flags", "{}")),
            "evolution_schedule": json.loads(world_data.get("evolution_schedule", "[]")),
            "active_characters": json.loads(world_data.get("active_characters", "{}")),
            "active_locations": json.loads(world_data.get("active_locations", "{}")),
            "active_objects": json.loads(world_data.get("active_objects", "{}")),
            "created_at": world_data["created_at"],
            "last_updated": world_data["last_updated"],
            "metadata": json.loads(world_data.get("metadata", "{}"))
        }


class LivingWorldsPersistence:
    """
    Main persistence interface for Living Worlds features.

    Provides a unified interface for all Living Worlds persistence operations
    including timelines, world states, and family relationships.
    """

    def __init__(self, uri: str = "bolt://localhost:7688", username: str = "neo4j",
                 password: str = "password", redis_host: str = "localhost",
                 redis_port: int = 6379, redis_db: int = 0):
        """
        Initialize Living Worlds persistence.

        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
            redis_host: Redis host
            redis_port: Redis port
            redis_db: Redis database number
        """
        # Initialize Neo4j connection
        self.schema_manager = LivingWorldsSchemaManager(uri, username, password)
        self.query_helper = None

        # Initialize Redis cache if available
        self.cache = None
        if REDIS_AVAILABLE and RedisCache:
            try:
                self.cache = RedisCache(host=redis_host, port=redis_port, db=redis_db)
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")

        # Initialize specialized persistence layers
        self.timeline_persistence = None
        self.world_state_persistence = None

    def connect(self) -> bool:
        """
        Establish connections to Neo4j and Redis.

        Returns:
            bool: True if connection was successful
        """
        try:
            self.schema_manager.connect()
            self.query_helper = LivingWorldsQueryHelper(self.schema_manager.driver)

            # Initialize specialized persistence layers
            self.timeline_persistence = TimelinePersistence(self.query_helper, self.cache)
            self.world_state_persistence = WorldStatePersistence(self.query_helper, self.cache)

            logger.info("Living Worlds persistence connected successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect Living Worlds persistence: {e}")
            return False

    def disconnect(self) -> None:
        """Close all connections."""
        if self.schema_manager:
            self.schema_manager.disconnect()
        if self.cache:
            self.cache.close()
        logger.info("Living Worlds persistence disconnected")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    # Timeline operations
    def save_timeline(self, timeline: Timeline) -> bool:
        """Save a timeline."""
        if not self.timeline_persistence:
            raise PersistenceError("Not connected to database")
        return self.timeline_persistence.save_timeline(timeline)

    def load_timeline(self, timeline_id: str) -> Timeline | None:
        """Load a timeline."""
        if not self.timeline_persistence:
            raise PersistenceError("Not connected to database")
        return self.timeline_persistence.load_timeline(timeline_id)

    def save_timeline_event(self, timeline_id: str, event: TimelineEvent) -> bool:
        """Save a timeline event."""
        if not self.timeline_persistence:
            raise PersistenceError("Not connected to database")
        return self.timeline_persistence.save_timeline_event(timeline_id, event)

    def get_timeline_events(self, timeline_id: str, limit: int = 50,
                          min_significance: int = 1,
                          world_id: str | None = None,
                          entity_id: str | None = None) -> list[TimelineEvent]:
        """Get timeline events."""
        # Allow LW cache short-circuit even if DB is unavailable
        if world_id and entity_id and self.cache:
            try:
                from .living_worlds_cache import LivingWorldsCache
            except Exception:
                from living_worlds_cache import LivingWorldsCache  # type: ignore
            lwc = LivingWorldsCache(self.cache)
            recent = lwc.get_recent_timeline_events(world_id, entity_id)
            if recent:
                return [TimelineEvent.from_dict(e) for e in recent][:limit]
        if not self.timeline_persistence:
            raise PersistenceError("Not connected to database")
        return self.timeline_persistence.get_timeline_events(timeline_id, limit, min_significance, world_id, entity_id)

    # World state operations
    def save_world_state(self, world_state: WorldState) -> bool:
        """Save a world state."""
        if not self.world_state_persistence:
            raise PersistenceError("Not connected to database")
        return self.world_state_persistence.save_world_state(world_state)

    def load_world_state(self, world_id: str) -> WorldState | None:
        """Load a world state."""
        if not self.world_state_persistence:
            raise PersistenceError("Not connected to database")
        return self.world_state_persistence.load_world_state(world_id)

    def update_world_state(self, world_id: str, updates: dict[str, Any]) -> bool:
        """Update world state properties."""
        if not self.world_state_persistence:
            raise PersistenceError("Not connected to database")
        return self.world_state_persistence.update_world_state(world_id, updates)

    # Family relationship operations
    def save_family_tree(self, family_tree: FamilyTree) -> bool:
        """Save a family tree."""
        if not self.query_helper:
            raise PersistenceError("Not connected to database")

        try:
            family_tree.validate()

            # Create family tree
            success = self.query_helper.create_family_tree(
                family_tree.tree_id,
                family_tree.root_character_id,
                generations_tracked=family_tree.generations_tracked,
                created_at=family_tree.created_at.isoformat(),
                last_updated=family_tree.last_updated.isoformat(),
                metadata=json.dumps(family_tree.metadata)
            )

            if not success:
                return False

            # Create relationships
            for relationship in family_tree.relationships:
                if not self.query_helper.create_family_relationship(
                    relationship.relationship_id,
                    relationship.from_character_id,
                    relationship.to_character_id,
                    relationship.relationship_type.value,
                    relationship.strength,
                    established_date=relationship.established_date.isoformat(),
                    notes=relationship.notes,
                    is_active=relationship.is_active
                ):
                    logger.error(f"Failed to create relationship {relationship.relationship_id}")
                    return False

            return True

        except ValidationError as e:
            logger.error(f"Family tree validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving family tree: {e}")
            return False

    def get_character_family_relationships(self, character_id: str) -> list[dict[str, Any]]:
        """Get family relationships for a character."""
        if not self.query_helper:
            raise PersistenceError("Not connected to database")
        return self.query_helper.get_character_family_relationships(character_id)

    # Utility methods
    def setup_schema(self) -> bool:
        """Set up the Living Worlds schema."""
        if not self.schema_manager:
            return False
        return self.schema_manager.setup_living_worlds_schema()

    def validate_schema(self) -> bool:
        """Validate the Living Worlds schema."""
        if not self.schema_manager:
            return False
        return self.schema_manager.validate_schema()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Test persistence operations
    with LivingWorldsPersistence() as persistence:
        if persistence.setup_schema():
            print("Living Worlds persistence setup completed successfully")
        else:
            print("Living Worlds persistence setup failed")
