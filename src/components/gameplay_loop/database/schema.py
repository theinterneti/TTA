"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Database/Schema]]

# Logseq: [[TTA/Components/Gameplay_loop/Database/Schema]]
Neo4j Schema for Gameplay Loop

This module defines the Neo4j database schema for the therapeutic text adventure
gameplay loop system, including nodes, relationships, and constraints.
"""

import logging

logger = logging.getLogger(__name__)


class GameplayLoopSchema:
    """Neo4j schema management for gameplay loop data."""

    # Node labels
    NODE_LABELS = {
        "SESSION": "GameplaySession",
        "SCENE": "NarrativeScene",
        "CHOICE": "PlayerChoice",
        "CONSEQUENCE": "ChoiceConsequence",
        "CHARACTER": "Character",
        "PROGRESS": "TherapeuticProgress",
        "SKILL": "Skill",
        "VALIDATION": "ValidationResult",
        "INTERVENTION": "TherapeuticIntervention",
    }

    # Relationship types
    RELATIONSHIPS = {
        "HAS_SCENE": "HAS_SCENE",
        "CURRENT_SCENE": "CURRENT_SCENE",
        "HAS_CHOICE": "HAS_CHOICE",
        "MADE_CHOICE": "MADE_CHOICE",
        "LEADS_TO": "LEADS_TO",
        "HAS_CONSEQUENCE": "HAS_CONSEQUENCE",
        "DEVELOPS_SKILL": "DEVELOPS_SKILL",
        "ACHIEVES_PROGRESS": "ACHIEVES_PROGRESS",
        "REQUIRES_VALIDATION": "REQUIRES_VALIDATION",
        "TRIGGERS_INTERVENTION": "TRIGGERS_INTERVENTION",
        "NEXT_SCENE": "NEXT_SCENE",
        "PREVIOUS_SCENE": "PREVIOUS_SCENE",
    }

    @classmethod
    def get_node_constraints(cls) -> list[str]:
        """Get list of node constraints to create."""
        return [
            # Unique constraints
            f"CREATE CONSTRAINT session_id_unique IF NOT EXISTS FOR (s:{cls.NODE_LABELS['SESSION']}) REQUIRE s.session_id IS UNIQUE",
            f"CREATE CONSTRAINT scene_id_unique IF NOT EXISTS FOR (sc:{cls.NODE_LABELS['SCENE']}) REQUIRE sc.scene_id IS UNIQUE",
            f"CREATE CONSTRAINT choice_id_unique IF NOT EXISTS FOR (c:{cls.NODE_LABELS['CHOICE']}) REQUIRE c.choice_id IS UNIQUE",
            f"CREATE CONSTRAINT consequence_id_unique IF NOT EXISTS FOR (co:{cls.NODE_LABELS['CONSEQUENCE']}) REQUIRE co.consequence_id IS UNIQUE",
            f"CREATE CONSTRAINT character_id_unique IF NOT EXISTS FOR (ch:{cls.NODE_LABELS['CHARACTER']}) REQUIRE ch.character_id IS UNIQUE",
            f"CREATE CONSTRAINT progress_id_unique IF NOT EXISTS FOR (p:{cls.NODE_LABELS['PROGRESS']}) REQUIRE p.progress_id IS UNIQUE",
            f"CREATE CONSTRAINT skill_id_unique IF NOT EXISTS FOR (sk:{cls.NODE_LABELS['SKILL']}) REQUIRE sk.skill_id IS UNIQUE",
            f"CREATE CONSTRAINT validation_id_unique IF NOT EXISTS FOR (v:{cls.NODE_LABELS['VALIDATION']}) REQUIRE v.validation_id IS UNIQUE",
            f"CREATE CONSTRAINT intervention_id_unique IF NOT EXISTS FOR (i:{cls.NODE_LABELS['INTERVENTION']}) REQUIRE i.intervention_id IS UNIQUE",
            # Existence constraints for required properties
            f"CREATE CONSTRAINT session_user_id_exists IF NOT EXISTS FOR (s:{cls.NODE_LABELS['SESSION']}) REQUIRE s.user_id IS NOT NULL",
            f"CREATE CONSTRAINT scene_title_exists IF NOT EXISTS FOR (sc:{cls.NODE_LABELS['SCENE']}) REQUIRE sc.title IS NOT NULL",
            f"CREATE CONSTRAINT choice_text_exists IF NOT EXISTS FOR (c:{cls.NODE_LABELS['CHOICE']}) REQUIRE c.text IS NOT NULL",
        ]

    @classmethod
    def get_indexes(cls) -> list[str]:
        """Get list of indexes to create for performance."""
        return [
            # Performance indexes
            f"CREATE INDEX session_user_id_index IF NOT EXISTS FOR (s:{cls.NODE_LABELS['SESSION']}) ON (s.user_id)",
            f"CREATE INDEX session_created_at_index IF NOT EXISTS FOR (s:{cls.NODE_LABELS['SESSION']}) ON (s.created_at)",
            f"CREATE INDEX scene_type_index IF NOT EXISTS FOR (sc:{cls.NODE_LABELS['SCENE']}) ON (sc.scene_type)",
            f"CREATE INDEX choice_type_index IF NOT EXISTS FOR (c:{cls.NODE_LABELS['CHOICE']}) ON (c.choice_type)",
            f"CREATE INDEX progress_type_index IF NOT EXISTS FOR (p:{cls.NODE_LABELS['PROGRESS']}) ON (p.progress_type)",
            f"CREATE INDEX skill_category_index IF NOT EXISTS FOR (sk:{cls.NODE_LABELS['SKILL']}) ON (sk.skill_category)",
            f"CREATE INDEX validation_status_index IF NOT EXISTS FOR (v:{cls.NODE_LABELS['VALIDATION']}) ON (v.status)",
            # Composite indexes for common queries
            f"CREATE INDEX session_user_active_index IF NOT EXISTS FOR (s:{cls.NODE_LABELS['SESSION']}) ON (s.user_id, s.is_active)",
            f"CREATE INDEX scene_session_type_index IF NOT EXISTS FOR (sc:{cls.NODE_LABELS['SCENE']}) ON (sc.session_id, sc.scene_type)",
        ]

    @classmethod
    def get_sample_data_queries(cls) -> list[str]:
        """Get sample data creation queries for testing."""
        return [
            # Sample therapeutic scene
            f"""
            CREATE (scene:{cls.NODE_LABELS["SCENE"]} {{
                scene_id: 'sample_intro_scene',
                title: 'Peaceful Garden Introduction',
                description: 'A calming introduction to mindfulness in a garden setting',
                narrative_content: 'You find yourself in a peaceful garden. The gentle sound of water flowing from a small fountain fills the air. Sunlight filters through the leaves of an old oak tree, creating dancing patterns on the ground. This is a safe space where you can explore your thoughts and feelings.',
                scene_type: 'introduction',
                difficulty_level: 'gentle',
                therapeutic_focus: ['mindfulness', 'grounding', 'safety'],
                learning_objectives: ['establish_safety', 'introduce_mindfulness'],
                emotional_tone: 'calm',
                estimated_duration: 300,
                is_completed: false,
                created_at: datetime()
            }})
            """,
            # Sample therapeutic choices
            f"""
            CREATE (choice1:{cls.NODE_LABELS["CHOICE"]} {{
                choice_id: 'garden_explore_mindfully',
                scene_id: 'sample_intro_scene',
                text: 'Take a moment to notice your breathing and the sensations around you',
                description: 'Practice mindful awareness of your current experience',
                choice_type: 'therapeutic',
                difficulty_level: 'gentle',
                therapeutic_value: 0.8,
                therapeutic_outcomes: ['mindfulness_practice', 'present_moment_awareness'],
                is_available: true,
                created_at: datetime()
            }})
            """,
            f"""
            CREATE (choice2:{cls.NODE_LABELS["CHOICE"]} {{
                choice_id: 'garden_explore_curious',
                scene_id: 'sample_intro_scene',
                text: 'Walk around the garden and explore what catches your attention',
                description: 'Engage your natural curiosity about the environment',
                choice_type: 'narrative',
                difficulty_level: 'standard',
                therapeutic_value: 0.6,
                therapeutic_outcomes: ['curiosity_engagement', 'environmental_awareness'],
                is_available: true,
                created_at: datetime()
            }})
            """,
            # Link choices to scene
            f"""
            MATCH (scene:{cls.NODE_LABELS["SCENE"]} {{scene_id: 'sample_intro_scene'}}),
                  (choice1:{cls.NODE_LABELS["CHOICE"]} {{choice_id: 'garden_explore_mindfully'}}),
                  (choice2:{cls.NODE_LABELS["CHOICE"]} {{choice_id: 'garden_explore_curious'}})
            CREATE (scene)-[:{cls.RELATIONSHIPS["HAS_CHOICE"]}]->(choice1),
                   (scene)-[:{cls.RELATIONSHIPS["HAS_CHOICE"]}]->(choice2)
            """,
        ]

    @classmethod
    async def initialize_schema(cls, neo4j_driver) -> bool:
        """Initialize the complete schema in Neo4j."""
        try:
            async with neo4j_driver.session() as session:
                # Create constraints
                for constraint in cls.get_node_constraints():
                    try:
                        await session.run(constraint)
                        logger.info(f"Created constraint: {constraint[:50]}...")
                    except Exception as e:
                        logger.warning(
                            f"Constraint creation failed (may already exist): {e}"
                        )

                # Create indexes
                for index in cls.get_indexes():
                    try:
                        await session.run(index)
                        logger.info(f"Created index: {index[:50]}...")
                    except Exception as e:
                        logger.warning(
                            f"Index creation failed (may already exist): {e}"
                        )

                logger.info("Schema initialization completed successfully")
                return True

        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            return False

    @classmethod
    async def create_sample_data(cls, neo4j_driver) -> bool:
        """Create sample data for testing."""
        try:
            async with neo4j_driver.session() as session:
                for query in cls.get_sample_data_queries():
                    await session.run(query)

                logger.info("Sample data created successfully")
                return True

        except Exception as e:
            logger.error(f"Sample data creation failed: {e}")
            return False

    @classmethod
    def get_session_node_properties(cls) -> dict[str, str]:
        """Get properties for GameplaySession nodes."""
        return {
            "session_id": "string",
            "user_id": "string",
            "character_id": "string",
            "world_id": "string",
            "current_scene_id": "string",
            "emotional_state": "string",
            "difficulty_level": "string",
            "is_active": "boolean",
            "is_paused": "boolean",
            "requires_therapeutic_intervention": "boolean",
            "safety_level": "string",
            "total_session_time": "float",
            "session_start_time": "datetime",
            "last_activity_time": "datetime",
            "created_at": "datetime",
            "updated_at": "datetime",
        }

    @classmethod
    def get_scene_node_properties(cls) -> dict[str, str]:
        """Get properties for NarrativeScene nodes."""
        return {
            "scene_id": "string",
            "title": "string",
            "description": "string",
            "narrative_content": "string",
            "scene_type": "string",
            "difficulty_level": "string",
            "estimated_duration": "integer",
            "therapeutic_focus": "list",
            "learning_objectives": "list",
            "emotional_tone": "string",
            "is_completed": "boolean",
            "completion_time": "datetime",
            "created_at": "datetime",
            "updated_at": "datetime",
        }

    @classmethod
    def get_choice_node_properties(cls) -> dict[str, str]:
        """Get properties for PlayerChoice nodes."""
        return {
            "choice_id": "string",
            "scene_id": "string",
            "text": "string",
            "description": "string",
            "choice_type": "string",
            "difficulty_level": "string",
            "therapeutic_value": "float",
            "prerequisites": "list",
            "emotional_requirements": "list",
            "skill_requirements": "list",
            "immediate_consequences": "list",
            "long_term_consequences": "list",
            "therapeutic_outcomes": "list",
            "is_available": "boolean",
            "availability_reason": "string",
            "created_at": "datetime",
        }
