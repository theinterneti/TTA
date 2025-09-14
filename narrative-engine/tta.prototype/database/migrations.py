"""
Database Migration Scripts for TTA Prototype

This module provides migration scripts for character, location, and therapeutic data
in the Neo4j database. It handles data migration between schema versions and
provides utilities for data import/export.

Classes:
    MigrationManager: Manages database migrations and data import/export
    DataSeeder: Seeds the database with initial therapeutic content
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from neo4j import Driver
except ImportError:
    Driver = None

try:
    from .neo4j_schema import Neo4jQueryHelper, Neo4jSchemaManager
except ImportError:
    from neo4j_schema import Neo4jQueryHelper, Neo4jSchemaManager

logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Raised when migration operations fail."""
    pass


class MigrationManager:
    """
    Manages database migrations and data import/export for therapeutic text adventure.

    This class handles migration of character data, location data, therapeutic content,
    and user progress between different schema versions.
    """

    def __init__(self, schema_manager: Neo4jSchemaManager):
        """
        Initialize migration manager.

        Args:
            schema_manager: Neo4j schema manager instance
        """
        self.schema_manager = schema_manager
        self.query_helper = Neo4jQueryHelper(schema_manager.driver) if schema_manager.driver else None

    def migrate_character_data(self, character_data: list[dict[str, Any]]) -> bool:
        """
        Migrate character data to Neo4j.

        Args:
            character_data: List of character data dictionaries

        Returns:
            bool: True if migration was successful
        """
        if not self.query_helper:
            raise MigrationError("No database connection available")

        logger.info(f"Migrating {len(character_data)} characters")

        try:
            for character in character_data:
                character_id = character.get('character_id')
                name = character.get('name')

                if not character_id or not name:
                    logger.warning(f"Skipping character with missing ID or name: {character}")
                    continue

                # Extract character properties
                properties = {
                    'therapeutic_role': character.get('therapeutic_role', 'companion'),
                    'personality_traits': json.dumps(character.get('personality_traits', {})),
                    'current_mood': character.get('current_mood', 'neutral'),
                    'dialogue_style': json.dumps(character.get('dialogue_style', {})),
                    'background_story': character.get('background_story', ''),
                    'specializations': json.dumps(character.get('specializations', []))
                }

                # Create character
                if self.query_helper.create_character(character_id, name, **properties):
                    logger.debug(f"Created character: {name} ({character_id})")

                    # Create memories if present
                    memories = character.get('memories', [])
                    for memory in memories:
                        self._create_character_memory(character_id, memory)

                    # Create relationships if present
                    relationships = character.get('relationships', {})
                    for other_char_id, relationship_data in relationships.items():
                        self._create_character_relationship(
                            character_id,
                            other_char_id,
                            relationship_data
                        )
                else:
                    logger.error(f"Failed to create character: {name} ({character_id})")
                    return False

            logger.info("Character data migration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error migrating character data: {e}")
            return False

    def migrate_location_data(self, location_data: list[dict[str, Any]]) -> bool:
        """
        Migrate location data to Neo4j.

        Args:
            location_data: List of location data dictionaries

        Returns:
            bool: True if migration was successful
        """
        if not self.query_helper:
            raise MigrationError("No database connection available")

        logger.info(f"Migrating {len(location_data)} locations")

        try:
            for location in location_data:
                location_id = location.get('location_id')
                name = location.get('name')

                if not location_id or not name:
                    logger.warning(f"Skipping location with missing ID or name: {location}")
                    continue

                # Extract location properties
                properties = {
                    'location_type': location.get('location_type', 'general'),
                    'description': location.get('description', ''),
                    'therapeutic_themes': json.dumps(location.get('therapeutic_themes', [])),
                    'mood_atmosphere': location.get('mood_atmosphere', 'neutral'),
                    'available_activities': json.dumps(location.get('available_activities', [])),
                    'safety_level': location.get('safety_level', 'safe')
                }

                # Create location
                if self.query_helper.create_location(location_id, name, **properties):
                    logger.debug(f"Created location: {name} ({location_id})")

                    # Create connections to other locations
                    connections = location.get('connections', {})
                    for connected_location_id, connection_data in connections.items():
                        self._create_location_connection(
                            location_id,
                            connected_location_id,
                            connection_data
                        )
                else:
                    logger.error(f"Failed to create location: {name} ({location_id})")
                    return False

            logger.info("Location data migration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error migrating location data: {e}")
            return False

    def migrate_therapeutic_data(self, therapeutic_data: dict[str, Any]) -> bool:
        """
        Migrate therapeutic content data to Neo4j.

        Args:
            therapeutic_data: Dictionary containing therapeutic content

        Returns:
            bool: True if migration was successful
        """
        if not self.schema_manager.driver:
            raise MigrationError("No database connection available")

        logger.info("Migrating therapeutic data")

        try:
            with self.schema_manager.driver.session() as session:
                # Migrate coping strategies
                strategies = therapeutic_data.get('coping_strategies', [])
                for strategy in strategies:
                    self._create_coping_strategy(session, strategy)

                # Migrate intervention templates
                interventions = therapeutic_data.get('intervention_templates', [])
                for intervention in interventions:
                    self._create_intervention_template(session, intervention)

                # Migrate therapeutic techniques
                techniques = therapeutic_data.get('therapeutic_techniques', [])
                for technique in techniques:
                    self._create_therapeutic_technique(session, technique)

                # Migrate emotional patterns
                patterns = therapeutic_data.get('emotional_patterns', [])
                for pattern in patterns:
                    self._create_emotional_pattern(session, pattern)

            logger.info("Therapeutic data migration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error migrating therapeutic data: {e}")
            return False

    def _create_character_memory(self, character_id: str, memory_data: dict[str, Any]) -> bool:
        """Create a memory node for a character."""
        if not self.schema_manager.driver:
            return False

        query = """
        MATCH (c:Character {character_id: $character_id})
        CREATE (m:Memory {
            memory_id: $memory_id,
            content: $content,
            emotional_weight: $emotional_weight,
            timestamp: datetime($timestamp),
            tags: $tags
        })
        CREATE (c)-[:HAS_MEMORY]->(m)
        RETURN m
        """

        try:
            with self.schema_manager.driver.session() as session:
                result = session.run(query,
                                   character_id=character_id,
                                   memory_id=memory_data.get('memory_id', f"mem_{datetime.now().timestamp()}"),
                                   content=memory_data.get('content', ''),
                                   emotional_weight=memory_data.get('emotional_weight', 0.0),
                                   timestamp=memory_data.get('timestamp', datetime.now().isoformat()),
                                   tags=memory_data.get('tags', []))
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating character memory: {e}")
            return False

    def _create_character_relationship(self, char1_id: str, char2_id: str, relationship_data: dict[str, Any]) -> bool:
        """Create a relationship between characters."""
        relationship_type = relationship_data.get('type', 'knows')
        strength = relationship_data.get('strength', 0.0)
        return self.query_helper.create_character_relationship(char1_id, char2_id, relationship_type, strength)

    def _create_location_connection(self, location1_id: str, location2_id: str, connection_data: dict[str, Any]) -> bool:
        """Create a connection between locations."""
        if not self.schema_manager.driver:
            return False

        query = """
        MATCH (l1:Location {location_id: $location1_id})
        MATCH (l2:Location {location_id: $location2_id})
        CREATE (l1)-[:CONNECTS_TO {
            direction: $direction,
            description: $description,
            travel_time: $travel_time,
            requirements: $requirements
        }]->(l2)
        RETURN l1, l2
        """

        try:
            with self.schema_manager.driver.session() as session:
                result = session.run(query,
                                   location1_id=location1_id,
                                   location2_id=location2_id,
                                   direction=connection_data.get('direction', 'bidirectional'),
                                   description=connection_data.get('description', ''),
                                   travel_time=connection_data.get('travel_time', 1),
                                   requirements=json.dumps(connection_data.get('requirements', [])))
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating location connection: {e}")
            return False

    def _create_coping_strategy(self, session, strategy_data: dict[str, Any]) -> bool:
        """Create a coping strategy node."""
        query = """
        CREATE (cs:CopingStrategy {
            strategy_id: $strategy_id,
            name: $name,
            description: $description,
            technique_steps: $technique_steps,
            applicable_situations: $applicable_situations,
            effectiveness_rating: $effectiveness_rating,
            created_at: datetime()
        })
        RETURN cs
        """

        try:
            result = session.run(query,
                               strategy_id=strategy_data.get('strategy_id', f"strategy_{datetime.now().timestamp()}"),
                               name=strategy_data.get('name', ''),
                               description=strategy_data.get('description', ''),
                               technique_steps=json.dumps(strategy_data.get('technique_steps', [])),
                               applicable_situations=json.dumps(strategy_data.get('applicable_situations', [])),
                               effectiveness_rating=strategy_data.get('effectiveness_rating', 0.0))
            return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating coping strategy: {e}")
            return False

    def _create_intervention_template(self, session, intervention_data: dict[str, Any]) -> bool:
        """Create an intervention template node."""
        query = """
        CREATE (it:InterventionTemplate {
            template_id: $template_id,
            intervention_type: $intervention_type,
            name: $name,
            description: $description,
            steps: $steps,
            duration_minutes: $duration_minutes,
            target_conditions: $target_conditions,
            created_at: datetime()
        })
        RETURN it
        """

        try:
            result = session.run(query,
                               template_id=intervention_data.get('template_id', f"template_{datetime.now().timestamp()}"),
                               intervention_type=intervention_data.get('intervention_type', 'general'),
                               name=intervention_data.get('name', ''),
                               description=intervention_data.get('description', ''),
                               steps=json.dumps(intervention_data.get('steps', [])),
                               duration_minutes=intervention_data.get('duration_minutes', 10),
                               target_conditions=json.dumps(intervention_data.get('target_conditions', [])))
            return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating intervention template: {e}")
            return False

    def _create_therapeutic_technique(self, session, technique_data: dict[str, Any]) -> bool:
        """Create a therapeutic technique node."""
        query = """
        CREATE (tt:TherapeuticTechnique {
            technique_id: $technique_id,
            name: $name,
            category: $category,
            description: $description,
            instructions: $instructions,
            evidence_base: $evidence_base,
            contraindications: $contraindications,
            created_at: datetime()
        })
        RETURN tt
        """

        try:
            result = session.run(query,
                               technique_id=technique_data.get('technique_id', f"technique_{datetime.now().timestamp()}"),
                               name=technique_data.get('name', ''),
                               category=technique_data.get('category', 'general'),
                               description=technique_data.get('description', ''),
                               instructions=technique_data.get('instructions', ''),
                               evidence_base=technique_data.get('evidence_base', ''),
                               contraindications=json.dumps(technique_data.get('contraindications', [])))
            return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating therapeutic technique: {e}")
            return False

    def _create_emotional_pattern(self, session, pattern_data: dict[str, Any]) -> bool:
        """Create an emotional pattern node."""
        query = """
        CREATE (ep:EmotionalPattern {
            pattern_id: $pattern_id,
            name: $name,
            description: $description,
            triggers: $triggers,
            typical_responses: $typical_responses,
            coping_suggestions: $coping_suggestions,
            severity_indicators: $severity_indicators,
            created_at: datetime()
        })
        RETURN ep
        """

        try:
            result = session.run(query,
                               pattern_id=pattern_data.get('pattern_id', f"pattern_{datetime.now().timestamp()}"),
                               name=pattern_data.get('name', ''),
                               description=pattern_data.get('description', ''),
                               triggers=json.dumps(pattern_data.get('triggers', [])),
                               typical_responses=json.dumps(pattern_data.get('typical_responses', [])),
                               coping_suggestions=json.dumps(pattern_data.get('coping_suggestions', [])),
                               severity_indicators=json.dumps(pattern_data.get('severity_indicators', [])))
            return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating emotional pattern: {e}")
            return False

    def export_data(self, output_dir: str) -> bool:
        """
        Export all data from Neo4j to JSON files.

        Args:
            output_dir: Directory to save exported data

        Returns:
            bool: True if export was successful
        """
        if not self.schema_manager.driver:
            raise MigrationError("No database connection available")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting data to {output_dir}")

        try:
            with self.schema_manager.driver.session() as session:
                # Export characters
                characters_result = session.run("MATCH (c:Character) RETURN c")
                characters = [dict(record["c"]) for record in characters_result]
                with open(output_path / "characters.json", "w") as f:
                    json.dump(characters, f, indent=2, default=str)

                # Export locations
                locations_result = session.run("MATCH (l:Location) RETURN l")
                locations = [dict(record["l"]) for record in locations_result]
                with open(output_path / "locations.json", "w") as f:
                    json.dump(locations, f, indent=2, default=str)

                # Export users
                users_result = session.run("MATCH (u:User) RETURN u")
                users = [dict(record["u"]) for record in users_result]
                with open(output_path / "users.json", "w") as f:
                    json.dump(users, f, indent=2, default=str)

                # Export therapeutic data
                therapeutic_data = {}

                strategies_result = session.run("MATCH (cs:CopingStrategy) RETURN cs")
                therapeutic_data["coping_strategies"] = [dict(record["cs"]) for record in strategies_result]

                templates_result = session.run("MATCH (it:InterventionTemplate) RETURN it")
                therapeutic_data["intervention_templates"] = [dict(record["it"]) for record in templates_result]

                techniques_result = session.run("MATCH (tt:TherapeuticTechnique) RETURN tt")
                therapeutic_data["therapeutic_techniques"] = [dict(record["tt"]) for record in techniques_result]

                with open(output_path / "therapeutic_data.json", "w") as f:
                    json.dump(therapeutic_data, f, indent=2, default=str)

            logger.info("Data export completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False


class DataSeeder:
    """
    Seeds the database with initial therapeutic content and sample data.

    This class provides methods to populate the database with initial characters,
    locations, therapeutic content, and sample scenarios for testing and development.
    """

    def __init__(self, migration_manager: MigrationManager):
        """
        Initialize data seeder.

        Args:
            migration_manager: Migration manager instance
        """
        self.migration_manager = migration_manager

    def seed_sample_characters(self) -> bool:
        """Seed the database with sample therapeutic characters."""
        sample_characters = [
            {
                "character_id": "therapist_alice",
                "name": "Dr. Alice Chen",
                "therapeutic_role": "primary_therapist",
                "personality_traits": {
                    "empathy": 0.9,
                    "patience": 0.8,
                    "wisdom": 0.85,
                    "humor": 0.6
                },
                "current_mood": "calm",
                "dialogue_style": {
                    "formality_level": 0.7,
                    "empathy_level": 0.9,
                    "directness": 0.6,
                    "humor_usage": 0.4,
                    "therapeutic_approach": "supportive"
                },
                "background_story": "Dr. Alice Chen is a licensed clinical psychologist specializing in cognitive-behavioral therapy and mindfulness-based interventions.",
                "specializations": ["CBT", "mindfulness", "anxiety_disorders", "depression"]
            },
            {
                "character_id": "companion_max",
                "name": "Max",
                "therapeutic_role": "peer_companion",
                "personality_traits": {
                    "openness": 0.8,
                    "optimism": 0.7,
                    "relatability": 0.9,
                    "humor": 0.8
                },
                "current_mood": "friendly",
                "dialogue_style": {
                    "formality_level": 0.3,
                    "empathy_level": 0.8,
                    "directness": 0.7,
                    "humor_usage": 0.7,
                    "therapeutic_approach": "exploratory"
                },
                "background_story": "Max is a peer support companion who has overcome similar challenges and offers relatable guidance.",
                "specializations": ["peer_support", "motivation", "goal_setting"]
            },
            {
                "character_id": "guide_sage",
                "name": "Sage",
                "therapeutic_role": "wisdom_guide",
                "personality_traits": {
                    "wisdom": 0.95,
                    "patience": 0.9,
                    "insight": 0.85,
                    "calmness": 0.9
                },
                "current_mood": "serene",
                "dialogue_style": {
                    "formality_level": 0.6,
                    "empathy_level": 0.8,
                    "directness": 0.5,
                    "humor_usage": 0.3,
                    "therapeutic_approach": "exploratory"
                },
                "background_story": "Sage is an ancient wisdom guide who helps users explore deeper meanings and find inner peace.",
                "specializations": ["mindfulness", "self_reflection", "meaning_making", "spiritual_growth"]
            }
        ]

        return self.migration_manager.migrate_character_data(sample_characters)

    def seed_sample_locations(self) -> bool:
        """Seed the database with sample therapeutic locations."""
        sample_locations = [
            {
                "location_id": "therapy_garden",
                "name": "Peaceful Garden",
                "location_type": "therapeutic_space",
                "description": "A serene garden with flowing water, comfortable seating, and calming natural sounds.",
                "therapeutic_themes": ["relaxation", "mindfulness", "nature_connection"],
                "mood_atmosphere": "peaceful",
                "available_activities": ["meditation", "breathing_exercises", "nature_observation"],
                "safety_level": "very_safe",
                "connections": {
                    "therapy_office": {
                        "direction": "bidirectional",
                        "description": "A short walk through a covered pathway",
                        "travel_time": 1
                    }
                }
            },
            {
                "location_id": "therapy_office",
                "name": "Therapy Office",
                "location_type": "clinical_space",
                "description": "A warm, comfortable office with soft lighting and supportive seating arrangements.",
                "therapeutic_themes": ["safety", "confidentiality", "professional_support"],
                "mood_atmosphere": "safe",
                "available_activities": ["therapy_sessions", "goal_setting", "progress_review"],
                "safety_level": "very_safe",
                "connections": {
                    "therapy_garden": {
                        "direction": "bidirectional",
                        "description": "A short walk through a covered pathway",
                        "travel_time": 1
                    },
                    "reflection_room": {
                        "direction": "bidirectional",
                        "description": "Down the hall to a quiet reflection space",
                        "travel_time": 1
                    }
                }
            },
            {
                "location_id": "reflection_room",
                "name": "Reflection Room",
                "location_type": "contemplative_space",
                "description": "A quiet room with soft cushions, gentle lighting, and inspiring artwork.",
                "therapeutic_themes": ["self_reflection", "emotional_processing", "insight"],
                "mood_atmosphere": "contemplative",
                "available_activities": ["journaling", "self_reflection", "emotional_processing"],
                "safety_level": "very_safe",
                "connections": {
                    "therapy_office": {
                        "direction": "bidirectional",
                        "description": "Down the hall from the therapy office",
                        "travel_time": 1
                    }
                }
            }
        ]

        return self.migration_manager.migrate_location_data(sample_locations)

    def seed_therapeutic_content(self) -> bool:
        """Seed the database with therapeutic content."""
        therapeutic_content = {
            "coping_strategies": [
                {
                    "strategy_id": "deep_breathing",
                    "name": "Deep Breathing Exercise",
                    "description": "A simple breathing technique to reduce anxiety and promote relaxation.",
                    "technique_steps": [
                        "Find a comfortable seated position",
                        "Place one hand on chest, one on belly",
                        "Breathe in slowly through nose for 4 counts",
                        "Hold breath for 4 counts",
                        "Exhale slowly through mouth for 6 counts",
                        "Repeat 5-10 times"
                    ],
                    "applicable_situations": ["anxiety", "stress", "panic", "insomnia"],
                    "effectiveness_rating": 8.5
                },
                {
                    "strategy_id": "grounding_5_4_3_2_1",
                    "name": "5-4-3-2-1 Grounding Technique",
                    "description": "A sensory grounding technique to manage anxiety and stay present.",
                    "technique_steps": [
                        "Notice 5 things you can see",
                        "Notice 4 things you can touch",
                        "Notice 3 things you can hear",
                        "Notice 2 things you can smell",
                        "Notice 1 thing you can taste"
                    ],
                    "applicable_situations": ["anxiety", "panic", "dissociation", "overwhelm"],
                    "effectiveness_rating": 8.0
                }
            ],
            "intervention_templates": [
                {
                    "template_id": "cbt_thought_challenge",
                    "intervention_type": "cognitive_restructuring",
                    "name": "Thought Challenging Exercise",
                    "description": "Help identify and challenge negative thought patterns.",
                    "steps": [
                        "Identify the negative thought",
                        "Examine the evidence for and against",
                        "Consider alternative perspectives",
                        "Develop a balanced thought",
                        "Practice the new thought pattern"
                    ],
                    "duration_minutes": 15,
                    "target_conditions": ["depression", "anxiety", "negative_thinking"]
                },
                {
                    "template_id": "mindfulness_body_scan",
                    "intervention_type": "mindfulness",
                    "name": "Mindful Body Scan",
                    "description": "A guided body scan to increase awareness and relaxation.",
                    "steps": [
                        "Find comfortable position",
                        "Close eyes and focus on breathing",
                        "Start with toes, notice sensations",
                        "Slowly move attention up the body",
                        "Notice without judgment",
                        "End with full body awareness"
                    ],
                    "duration_minutes": 20,
                    "target_conditions": ["stress", "anxiety", "chronic_pain", "insomnia"]
                }
            ],
            "therapeutic_techniques": [
                {
                    "technique_id": "active_listening",
                    "name": "Active Listening",
                    "category": "communication",
                    "description": "Fully focusing on and understanding what the person is saying.",
                    "instructions": "Give full attention, reflect back what you hear, ask clarifying questions, avoid judgment.",
                    "evidence_base": "Widely supported in therapeutic literature as fundamental to building rapport.",
                    "contraindications": []
                },
                {
                    "technique_id": "socratic_questioning",
                    "name": "Socratic Questioning",
                    "category": "cognitive",
                    "description": "Using questions to help people examine their thoughts and beliefs.",
                    "instructions": "Ask open-ended questions that encourage self-reflection and discovery.",
                    "evidence_base": "Core component of CBT with strong empirical support.",
                    "contraindications": ["severe_depression", "acute_crisis"]
                }
            ],
            "emotional_patterns": [
                {
                    "pattern_id": "anxiety_spiral",
                    "name": "Anxiety Spiral",
                    "description": "Escalating cycle of anxious thoughts leading to increased physical symptoms.",
                    "triggers": ["uncertainty", "social_situations", "performance_pressure"],
                    "typical_responses": ["racing_thoughts", "physical_tension", "avoidance"],
                    "coping_suggestions": ["deep_breathing", "grounding_techniques", "thought_challenging"],
                    "severity_indicators": ["panic_attacks", "complete_avoidance", "physical_symptoms"]
                }
            ]
        }

        return self.migration_manager.migrate_therapeutic_data(therapeutic_content)

    def seed_all_sample_data(self) -> bool:
        """Seed all sample data into the database."""
        logger.info("Seeding all sample data")

        success = True

        if not self.seed_sample_characters():
            logger.error("Failed to seed sample characters")
            success = False

        if not self.seed_sample_locations():
            logger.error("Failed to seed sample locations")
            success = False

        if not self.seed_therapeutic_content():
            logger.error("Failed to seed therapeutic content")
            success = False

        if success:
            logger.info("All sample data seeded successfully")
        else:
            logger.error("Some sample data failed to seed")

        return success


# Utility functions
def run_migrations(uri: str = "bolt://localhost:7688", username: str = "neo4j", password: str = "password") -> bool:
    """
    Run all necessary migrations and seed sample data.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        bool: True if migrations completed successfully
    """
    try:
        with Neo4jSchemaManager(uri, username, password) as schema_manager:
            # Setup schema first
            if not schema_manager.setup_schema():
                logger.error("Failed to setup schema")
                return False

            # Run migrations
            migration_manager = MigrationManager(schema_manager)
            data_seeder = DataSeeder(migration_manager)

            # Seed sample data
            if not data_seeder.seed_all_sample_data():
                logger.error("Failed to seed sample data")
                return False

            logger.info("All migrations completed successfully")
            return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    if run_migrations():
        print("✅ Migrations completed successfully")
    else:
        print("❌ Migrations failed")
