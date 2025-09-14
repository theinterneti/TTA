"""
Living Worlds Database Migration Scripts

This module provides migration scripts specifically for Living Worlds features
including timeline data, family relationships, and world state management.
It extends the base migration functionality for Living Worlds specific data.

Classes:
    LivingWorldsMigrationManager: Manages Living Worlds specific migrations
    TimelineDataSeeder: Seeds timeline and event data
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from neo4j import Driver
except ImportError:
    Driver = None

try:
    from .living_worlds_schema import LivingWorldsQueryHelper, LivingWorldsSchemaManager
    from .migrations import MigrationError, MigrationManager
except ImportError:
    from living_worlds_schema import LivingWorldsQueryHelper, LivingWorldsSchemaManager
    from migrations import MigrationError, MigrationManager

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

logger = logging.getLogger(__name__)


class LivingWorldsMigrationManager(MigrationManager):
    """
    Manages database migrations specific to Living Worlds features.

    This class extends the base MigrationManager to handle timeline data,
    family relationships, world states, and Living Worlds specific content.
    """

    def __init__(self, schema_manager: LivingWorldsSchemaManager):
        """
        Initialize Living Worlds migration manager.

        Args:
            schema_manager: Living Worlds schema manager instance
        """
        super().__init__(schema_manager)
        self.living_worlds_query_helper = LivingWorldsQueryHelper(schema_manager.driver) if schema_manager.driver else None

    def migrate_timeline_data(self, timeline_data: list[dict[str, Any]]) -> bool:
        """
        Migrate timeline data to Neo4j.

        Args:
            timeline_data: List of timeline data dictionaries

        Returns:
            bool: True if migration was successful
        """
        if not self.living_worlds_query_helper:
            raise MigrationError("No database connection available")

        logger.info(f"Migrating {len(timeline_data)} timelines")

        try:
            for timeline_dict in timeline_data:
                timeline_id = timeline_dict.get('timeline_id')
                entity_id = timeline_dict.get('entity_id')
                entity_type = timeline_dict.get('entity_type')

                if not timeline_id or not entity_id or not entity_type:
                    logger.warning(f"Skipping timeline with missing required fields: {timeline_dict}")
                    continue

                # Extract timeline properties
                properties = {
                    'created_at': timeline_dict.get('created_at', datetime.now().isoformat()),
                    'last_updated': timeline_dict.get('last_updated', datetime.now().isoformat()),
                    'metadata': json.dumps(timeline_dict.get('metadata', {}))
                }

                # Create timeline
                if self.living_worlds_query_helper.create_timeline(timeline_id, entity_id, entity_type, **properties):
                    logger.debug(f"Created timeline: {timeline_id} for {entity_type} {entity_id}")

                    # Create events for this timeline
                    events = timeline_dict.get('events', [])
                    for event_dict in events:
                        self._create_timeline_event(timeline_id, event_dict)
                else:
                    logger.error(f"Failed to create timeline: {timeline_id}")
                    return False

            logger.info("Timeline data migration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error migrating timeline data: {e}")
            return False

    def migrate_family_tree_data(self, family_tree_data: list[dict[str, Any]]) -> bool:
        """
        Migrate family tree data to Neo4j.

        Args:
            family_tree_data: List of family tree data dictionaries

        Returns:
            bool: True if migration was successful
        """
        if not self.living_worlds_query_helper:
            raise MigrationError("No database connection available")

        logger.info(f"Migrating {len(family_tree_data)} family trees")

        try:
            for tree_dict in family_tree_data:
                tree_id = tree_dict.get('tree_id')
                root_character_id = tree_dict.get('root_character_id')

                if not tree_id or not root_character_id:
                    logger.warning(f"Skipping family tree with missing required fields: {tree_dict}")
                    continue

                # Extract family tree properties
                properties = {
                    'generations_tracked': tree_dict.get('generations_tracked', 3),
                    'created_at': tree_dict.get('created_at', datetime.now().isoformat()),
                    'last_updated': tree_dict.get('last_updated', datetime.now().isoformat()),
                    'metadata': json.dumps(tree_dict.get('metadata', {}))
                }

                # Create family tree
                if self.living_worlds_query_helper.create_family_tree(tree_id, root_character_id, **properties):
                    logger.debug(f"Created family tree: {tree_id} for character {root_character_id}")

                    # Create relationships for this family tree
                    relationships = tree_dict.get('relationships', [])
                    for relationship_dict in relationships:
                        self._create_family_relationship(relationship_dict)

                    # Create family events
                    family_events = tree_dict.get('family_events', [])
                    for event_dict in family_events:
                        # Family events are stored as timeline events with special tags
                        event_dict['tags'] = event_dict.get('tags', []) + ['family_event']
                        # We'll need to find or create a timeline for family events
                        family_timeline_id = f"family_{tree_id}"
                        self._ensure_family_timeline_exists(family_timeline_id, root_character_id)
                        self._create_timeline_event(family_timeline_id, event_dict)
                else:
                    logger.error(f"Failed to create family tree: {tree_id}")
                    return False

            logger.info("Family tree data migration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error migrating family tree data: {e}")
            return False

    def migrate_world_state_data(self, world_state_data: list[dict[str, Any]]) -> bool:
        """
        Migrate world state data to Neo4j.

        Args:
            world_state_data: List of world state data dictionaries

        Returns:
            bool: True if migration was successful
        """
        if not self.living_worlds_query_helper:
            raise MigrationError("No database connection available")

        logger.info(f"Migrating {len(world_state_data)} world states")

        try:
            for world_dict in world_state_data:
                world_id = world_dict.get('world_id')
                world_name = world_dict.get('world_name')

                if not world_id or not world_name:
                    logger.warning(f"Skipping world state with missing required fields: {world_dict}")
                    continue

                # Extract world state properties
                properties = {
                    'current_time': world_dict.get('current_time', datetime.now().isoformat()),
                    'world_status': world_dict.get('world_status', 'active'),
                    'last_evolution': world_dict.get('last_evolution', datetime.now().isoformat()),
                    'player_last_visit': world_dict.get('player_last_visit'),
                    'world_flags': json.dumps(world_dict.get('world_flags', {})),
                    'evolution_schedule': json.dumps(world_dict.get('evolution_schedule', [])),
                    'created_at': world_dict.get('created_at', datetime.now().isoformat()),
                    'last_updated': world_dict.get('last_updated', datetime.now().isoformat()),
                    'metadata': json.dumps(world_dict.get('metadata', {}))
                }

                # Create world state
                if self.living_worlds_query_helper.create_world_state(world_id, world_name, **properties):
                    logger.debug(f"Created world state: {world_name} ({world_id})")

                    # Link active characters, locations, and objects to the world
                    self._link_world_entities(world_id, world_dict)
                else:
                    logger.error(f"Failed to create world state: {world_id}")
                    return False

            logger.info("World state data migration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error migrating world state data: {e}")
            return False

    def _create_timeline_event(self, timeline_id: str, event_dict: dict[str, Any]) -> bool:
        """Create a timeline event from dictionary data."""
        event_id = event_dict.get('event_id', str(uuid.uuid4()))
        event_type = event_dict.get('event_type', 'custom')
        title = event_dict.get('title', '')
        description = event_dict.get('description', '')

        if not title or not description:
            logger.warning(f"Skipping event with missing title or description: {event_dict}")
            return False

        # Prepare event properties
        properties = {
            'timestamp': event_dict.get('timestamp', datetime.now().isoformat()),
            'significance_level': event_dict.get('significance_level', 5),
            'emotional_impact': event_dict.get('emotional_impact', 0.0),
            'participants': event_dict.get('participants', []),
            'consequences': event_dict.get('consequences', []),
            'tags': event_dict.get('tags', []),
            'location_id': event_dict.get('location_id'),
            'metadata': json.dumps(event_dict.get('metadata', {}))
        }

        return self.living_worlds_query_helper.create_timeline_event(
            event_id, timeline_id, event_type, title, description, **properties
        )

    def _create_family_relationship(self, relationship_dict: dict[str, Any]) -> bool:
        """Create a family relationship from dictionary data."""
        relationship_id = relationship_dict.get('relationship_id', str(uuid.uuid4()))
        from_character_id = relationship_dict.get('from_character_id')
        to_character_id = relationship_dict.get('to_character_id')
        relationship_type = relationship_dict.get('relationship_type')

        if not from_character_id or not to_character_id or not relationship_type:
            logger.warning(f"Skipping relationship with missing required fields: {relationship_dict}")
            return False

        strength = relationship_dict.get('strength', 1.0)

        # Prepare relationship properties
        properties = {
            'established_date': relationship_dict.get('established_date', datetime.now().isoformat()),
            'notes': relationship_dict.get('notes', ''),
            'is_active': relationship_dict.get('is_active', True)
        }

        return self.living_worlds_query_helper.create_family_relationship(
            relationship_id, from_character_id, to_character_id, relationship_type, strength, **properties
        )

    def _ensure_family_timeline_exists(self, family_timeline_id: str, root_character_id: str) -> bool:
        """Ensure a family timeline exists for family events."""
        # Check if timeline already exists
        if not self.schema_manager.driver:
            return False

        query = "MATCH (t:Timeline {timeline_id: $timeline_id}) RETURN t"

        try:
            with self.schema_manager.driver.session() as session:
                result = session.run(query, timeline_id=family_timeline_id)
                if result.single():
                    return True  # Timeline already exists

                # Create family timeline
                return self.living_worlds_query_helper.create_timeline(
                    family_timeline_id, root_character_id, "family",
                    description=f"Family events timeline for character {root_character_id}"
                )
        except Exception as e:
            logger.error(f"Error ensuring family timeline exists: {e}")
            return False

    def _link_world_entities(self, world_id: str, world_dict: dict[str, Any]) -> bool:
        """Link characters, locations, and objects to a world."""
        if not self.schema_manager.driver:
            return False

        try:
            with self.schema_manager.driver.session() as session:
                # Link active characters
                active_characters = world_dict.get('active_characters', {})
                for character_id in active_characters.keys():
                    query = """
                    MATCH (w:World {world_id: $world_id})
                    MATCH (c:Character {character_id: $character_id})
                    MERGE (w)-[:CONTAINS_CHARACTER]->(c)
                    """
                    session.run(query, world_id=world_id, character_id=character_id)

                # Link active locations
                active_locations = world_dict.get('active_locations', {})
                for location_id in active_locations.keys():
                    query = """
                    MATCH (w:World {world_id: $world_id})
                    MATCH (l:Location {location_id: $location_id})
                    MERGE (w)-[:CONTAINS_LOCATION]->(l)
                    """
                    session.run(query, world_id=world_id, location_id=location_id)

                # Link active objects
                active_objects = world_dict.get('active_objects', {})
                for object_id in active_objects.keys():
                    query = """
                    MATCH (w:World {world_id: $world_id})
                    MATCH (o:Object {object_id: $object_id})
                    MERGE (w)-[:CONTAINS_OBJECT]->(o)
                    """
                    session.run(query, world_id=world_id, object_id=object_id)

                return True

        except Exception as e:
            logger.error(f"Error linking world entities: {e}")
            return False


class TimelineDataSeeder:
    """
    Seeds the database with sample timeline and event data for testing and development.

    This class provides methods to populate the database with sample timelines,
    events, family relationships, and world states for Living Worlds features.
    """

    def __init__(self, migration_manager: LivingWorldsMigrationManager):
        """
        Initialize timeline data seeder.

        Args:
            migration_manager: Living Worlds migration manager instance
        """
        self.migration_manager = migration_manager

    def seed_sample_timelines(self) -> bool:
        """Seed the database with sample character timelines."""
        sample_timelines = [
            {
                "timeline_id": "timeline_alice",
                "entity_id": "therapist_alice",
                "entity_type": "character",
                "created_at": (datetime.now() - timedelta(days=365)).isoformat(),
                "last_updated": datetime.now().isoformat(),
                "metadata": {"description": "Dr. Alice Chen's professional timeline"},
                "events": [
                    {
                        "event_id": "alice_graduation",
                        "event_type": "achievement",
                        "title": "Graduated with PhD in Clinical Psychology",
                        "description": "Completed doctoral studies at Stanford University with specialization in CBT",
                        "timestamp": (datetime.now() - timedelta(days=2000)).isoformat(),
                        "significance_level": 9,
                        "emotional_impact": 0.8,
                        "participants": ["therapist_alice"],
                        "consequences": ["Became licensed clinical psychologist", "Started private practice"],
                        "tags": ["education", "achievement", "career"]
                    },
                    {
                        "event_id": "alice_first_patient",
                        "event_type": "meeting",
                        "title": "First Patient Session",
                        "description": "Successfully conducted first therapy session as licensed practitioner",
                        "timestamp": (datetime.now() - timedelta(days=1800)).isoformat(),
                        "significance_level": 8,
                        "emotional_impact": 0.6,
                        "participants": ["therapist_alice"],
                        "consequences": ["Gained confidence in therapeutic skills", "Established therapeutic approach"],
                        "tags": ["career", "milestone", "therapy"]
                    },
                    {
                        "event_id": "alice_specialization",
                        "event_type": "learning",
                        "title": "Specialized in Anxiety Disorders",
                        "description": "Completed advanced training in anxiety and panic disorder treatment",
                        "timestamp": (datetime.now() - timedelta(days=1200)).isoformat(),
                        "significance_level": 7,
                        "emotional_impact": 0.5,
                        "participants": ["therapist_alice"],
                        "consequences": ["Became expert in anxiety treatment", "Developed specialized techniques"],
                        "tags": ["education", "specialization", "anxiety"]
                    }
                ]
            },
            {
                "timeline_id": "timeline_max",
                "entity_id": "companion_max",
                "entity_type": "character",
                "created_at": (datetime.now() - timedelta(days=300)).isoformat(),
                "last_updated": datetime.now().isoformat(),
                "metadata": {"description": "Max's peer support journey"},
                "events": [
                    {
                        "event_id": "max_recovery",
                        "event_type": "achievement",
                        "title": "Completed Recovery Program",
                        "description": "Successfully completed 12-month recovery program for anxiety and depression",
                        "timestamp": (datetime.now() - timedelta(days=400)).isoformat(),
                        "significance_level": 10,
                        "emotional_impact": 0.9,
                        "participants": ["companion_max"],
                        "consequences": ["Gained coping skills", "Developed resilience", "Became peer mentor"],
                        "tags": ["recovery", "achievement", "mental_health"]
                    },
                    {
                        "event_id": "max_peer_training",
                        "event_type": "learning",
                        "title": "Peer Support Training",
                        "description": "Completed certification in peer support counseling",
                        "timestamp": (datetime.now() - timedelta(days=200)).isoformat(),
                        "significance_level": 8,
                        "emotional_impact": 0.7,
                        "participants": ["companion_max"],
                        "consequences": ["Became certified peer counselor", "Started helping others"],
                        "tags": ["training", "certification", "peer_support"]
                    }
                ]
            }
        ]

        return self.migration_manager.migrate_timeline_data(sample_timelines)

    def seed_sample_family_trees(self) -> bool:
        """Seed the database with sample family trees."""
        sample_family_trees = [
            {
                "tree_id": "family_alice",
                "root_character_id": "therapist_alice",
                "generations_tracked": 3,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "metadata": {"description": "Dr. Alice Chen's family tree"},
                "relationships": [
                    {
                        "relationship_id": "alice_parent_1",
                        "from_character_id": "alice_mother",
                        "to_character_id": "therapist_alice",
                        "relationship_type": "parent",
                        "strength": 0.9,
                        "established_date": (datetime.now() - timedelta(days=12000)).isoformat(),
                        "notes": "Strong supportive relationship"
                    },
                    {
                        "relationship_id": "alice_parent_2",
                        "from_character_id": "alice_father",
                        "to_character_id": "therapist_alice",
                        "relationship_type": "parent",
                        "strength": 0.8,
                        "established_date": (datetime.now() - timedelta(days=12000)).isoformat(),
                        "notes": "Supportive but more distant"
                    },
                    {
                        "relationship_id": "alice_sibling",
                        "from_character_id": "therapist_alice",
                        "to_character_id": "alice_brother",
                        "relationship_type": "sibling",
                        "strength": 0.7,
                        "established_date": (datetime.now() - timedelta(days=10000)).isoformat(),
                        "notes": "Close sibling relationship"
                    }
                ],
                "family_events": [
                    {
                        "event_id": "alice_family_graduation",
                        "event_type": "celebration",
                        "title": "Family Graduation Celebration",
                        "description": "Family gathered to celebrate Alice's PhD graduation",
                        "timestamp": (datetime.now() - timedelta(days=2000)).isoformat(),
                        "significance_level": 8,
                        "emotional_impact": 0.8,
                        "participants": ["therapist_alice", "alice_mother", "alice_father", "alice_brother"],
                        "consequences": ["Strengthened family bonds", "Increased family pride"],
                        "tags": ["family", "celebration", "achievement"]
                    }
                ]
            }
        ]

        return self.migration_manager.migrate_family_tree_data(sample_family_trees)

    def seed_sample_world_states(self) -> bool:
        """Seed the database with sample world states."""
        sample_world_states = [
            {
                "world_id": "therapeutic_garden_world",
                "world_name": "Therapeutic Garden World",
                "current_time": datetime.now().isoformat(),
                "world_status": "active",
                "last_evolution": (datetime.now() - timedelta(hours=6)).isoformat(),
                "player_last_visit": (datetime.now() - timedelta(days=1)).isoformat(),
                "world_flags": {
                    "season": "spring",
                    "weather": "sunny",
                    "time_of_day": "afternoon",
                    "player_progress_level": 3
                },
                "evolution_schedule": [
                    {
                        "task_id": str(uuid.uuid4()),
                        "task_type": "seasonal_change",
                        "scheduled_time": (datetime.now() + timedelta(days=30)).isoformat(),
                        "task_data": {"new_season": "summer"}
                    }
                ],
                "active_characters": {
                    "therapist_alice": {"status": "available", "location": "therapy_office"},
                    "companion_max": {"status": "available", "location": "therapy_garden"}
                },
                "active_locations": {
                    "therapy_garden": {"status": "accessible", "weather": "sunny"},
                    "therapy_office": {"status": "accessible", "occupancy": "low"},
                    "reflection_room": {"status": "accessible", "atmosphere": "peaceful"}
                },
                "active_objects": {
                    "garden_bench": {"location": "therapy_garden", "condition": "good"},
                    "therapy_chair": {"location": "therapy_office", "condition": "excellent"},
                    "meditation_cushion": {"location": "reflection_room", "condition": "good"}
                },
                "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "last_updated": datetime.now().isoformat(),
                "metadata": {
                    "theme": "therapeutic_healing",
                    "difficulty_level": "beginner",
                    "therapeutic_focus": ["anxiety", "mindfulness", "self_reflection"]
                }
            }
        ]

        return self.migration_manager.migrate_world_state_data(sample_world_states)

    def seed_all_living_worlds_data(self) -> bool:
        """Seed all Living Worlds sample data."""
        logger.info("Seeding all Living Worlds sample data")

        try:
            if not self.seed_sample_timelines():
                logger.error("Failed to seed sample timelines")
                return False

            if not self.seed_sample_family_trees():
                logger.error("Failed to seed sample family trees")
                return False

            if not self.seed_sample_world_states():
                logger.error("Failed to seed sample world states")
                return False

            logger.info("All Living Worlds sample data seeded successfully")
            return True

        except Exception as e:
            logger.error(f"Error seeding Living Worlds data: {e}")
            return False


def run_living_worlds_migrations(uri: str = "bolt://localhost:7688",
                                username: str = "neo4j",
                                password: str = "password") -> bool:
    """
    Run complete Living Worlds migrations including schema setup and data seeding.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        bool: True if migrations completed successfully
    """
    logger.info("Running Living Worlds migrations")

    try:
        # Set up schema
        with LivingWorldsSchemaManager(uri, username, password) as schema_manager:
            if not schema_manager.setup_living_worlds_schema():
                logger.error("Failed to set up Living Worlds schema")
                return False

            # Run migrations
            migration_manager = LivingWorldsMigrationManager(schema_manager)
            data_seeder = TimelineDataSeeder(migration_manager)

            if not data_seeder.seed_all_living_worlds_data():
                logger.error("Failed to seed Living Worlds data")
                return False

        logger.info("Living Worlds migrations completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error running Living Worlds migrations: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Run Living Worlds migrations
    if run_living_worlds_migrations():
        print("Living Worlds migrations completed successfully")
    else:
        print("Living Worlds migrations failed")
