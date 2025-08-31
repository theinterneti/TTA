"""
Neo4j Graph Database Schema

This module defines the comprehensive graph database schema for the therapeutic
gameplay loop, including node types, relationships, constraints, and indexes.
"""

from dataclasses import dataclass
from enum import Enum


class NodeType(str, Enum):
    """Node types in the therapeutic gameplay graph."""

    # Core gameplay nodes
    SESSION = "Session"
    SCENE = "Scene"
    CHOICE = "Choice"
    CONSEQUENCE = "Consequence"

    # User and character nodes
    USER = "User"
    CHARACTER = "Character"
    WORLD = "World"

    # Therapeutic nodes
    THERAPEUTIC_GOAL = "TherapeuticGoal"
    SKILL = "Skill"
    EMOTION = "Emotion"
    BEHAVIOR = "Behavior"
    MILESTONE = "Milestone"

    # Progress tracking nodes
    PROGRESS_METRIC = "ProgressMetric"
    SKILL_DEVELOPMENT = "SkillDevelopment"
    EMOTIONAL_GROWTH = "EmotionalGrowth"
    BEHAVIORAL_CHANGE = "BehavioralChange"

    # Narrative nodes
    NARRATIVE_ARC = "NarrativeArc"
    STORY_BEAT = "StoryBeat"
    THEME = "Theme"

    # Validation and safety nodes
    SAFETY_CHECK = "SafetyCheck"
    VALIDATION_RULE = "ValidationRule"
    THERAPEUTIC_ALIGNMENT = "TherapeuticAlignment"


class RelationshipType(str, Enum):
    """Relationship types in the therapeutic gameplay graph."""

    # Session relationships
    HAS_SESSION = "HAS_SESSION"
    CURRENT_SCENE = "CURRENT_SCENE"
    COMPLETED_SCENE = "COMPLETED_SCENE"
    MADE_CHOICE = "MADE_CHOICE"

    # Narrative flow relationships
    LEADS_TO = "LEADS_TO"
    BRANCHES_TO = "BRANCHES_TO"
    RETURNS_TO = "RETURNS_TO"
    UNLOCKS = "UNLOCKS"
    REQUIRES = "REQUIRES"

    # Choice and consequence relationships
    HAS_CHOICE = "HAS_CHOICE"
    RESULTS_IN = "RESULTS_IN"
    TRIGGERS = "TRIGGERS"
    INFLUENCES = "INFLUENCES"

    # Therapeutic relationships
    ADDRESSES_GOAL = "ADDRESSES_GOAL"
    PRACTICES_SKILL = "PRACTICES_SKILL"
    DEVELOPS_SKILL = "DEVELOPS_SKILL"
    REGULATES_EMOTION = "REGULATES_EMOTION"
    CHANGES_BEHAVIOR = "CHANGES_BEHAVIOR"
    ACHIEVES_MILESTONE = "ACHIEVES_MILESTONE"

    # Progress relationships
    TRACKS_PROGRESS = "TRACKS_PROGRESS"
    IMPROVES = "IMPROVES"
    MEASURES = "MEASURES"
    CORRELATES_WITH = "CORRELATES_WITH"

    # Character and world relationships
    PLAYS_AS = "PLAYS_AS"
    INTERACTS_WITH = "INTERACTS_WITH"
    LOCATED_IN = "LOCATED_IN"
    BELONGS_TO = "BELONGS_TO"

    # Validation relationships
    VALIDATES = "VALIDATES"
    PASSES_CHECK = "PASSES_CHECK"
    FAILS_CHECK = "FAILS_CHECK"
    ALIGNS_WITH = "ALIGNS_WITH"

    # Temporal relationships
    PRECEDES = "PRECEDES"
    FOLLOWS = "FOLLOWS"
    CONCURRENT_WITH = "CONCURRENT_WITH"

    # Similarity and clustering relationships
    SIMILAR_TO = "SIMILAR_TO"
    PART_OF = "PART_OF"
    CONTAINS = "CONTAINS"


@dataclass
class NodeProperties:
    """Standard properties for different node types."""

    required: set[str]
    optional: set[str]
    indexed: set[str]
    unique: set[str]


@dataclass
class RelationshipProperties:
    """Standard properties for different relationship types."""

    required: set[str]
    optional: set[str]
    indexed: set[str]


class GraphSchema:
    """Comprehensive graph schema definition for therapeutic gameplay."""

    # Node property definitions
    NODE_PROPERTIES: dict[NodeType, NodeProperties] = {
        NodeType.SESSION: NodeProperties(
            required={"session_id", "user_id", "created_at", "session_state"},
            optional={
                "character_id",
                "world_id",
                "therapeutic_goals",
                "safety_level",
                "completed_at",
                "last_activity",
                "session_metrics",
            },
            indexed={"session_id", "user_id", "created_at", "session_state"},
            unique={"session_id"},
        ),
        NodeType.SCENE: NodeProperties(
            required={"scene_id", "session_id", "title", "scene_type", "created_at"},
            optional={
                "description",
                "narrative_content",
                "therapeutic_focus",
                "emotional_tone",
                "completion_criteria",
                "completed_at",
            },
            indexed={"scene_id", "session_id", "scene_type", "created_at"},
            unique={"scene_id"},
        ),
        NodeType.CHOICE: NodeProperties(
            required={"choice_id", "scene_id", "choice_text", "choice_type"},
            optional={
                "therapeutic_relevance",
                "emotional_weight",
                "difficulty_level",
                "prerequisites",
                "metadata",
            },
            indexed={"choice_id", "scene_id", "choice_type"},
            unique={"choice_id"},
        ),
        NodeType.USER: NodeProperties(
            required={"user_id", "created_at"},
            optional={"therapeutic_preferences", "progress_summary", "safety_settings"},
            indexed={"user_id", "created_at"},
            unique={"user_id"},
        ),
        NodeType.THERAPEUTIC_GOAL: NodeProperties(
            required={"goal_id", "goal_name", "goal_type"},
            optional={
                "description",
                "target_metrics",
                "completion_criteria",
                "priority",
            },
            indexed={"goal_id", "goal_name", "goal_type"},
            unique={"goal_id"},
        ),
        NodeType.SKILL: NodeProperties(
            required={"skill_id", "skill_name", "skill_category"},
            optional={
                "description",
                "learning_objectives",
                "mastery_indicators",
                "practice_opportunities",
            },
            indexed={"skill_id", "skill_name", "skill_category"},
            unique={"skill_id"},
        ),
        NodeType.PROGRESS_METRIC: NodeProperties(
            required={"metric_id", "metric_name", "progress_type", "current_value"},
            optional={
                "baseline_value",
                "target_value",
                "measurement_method",
                "confidence_level",
                "last_updated",
            },
            indexed={"metric_id", "metric_name", "progress_type"},
            unique={"metric_id"},
        ),
        NodeType.MILESTONE: NodeProperties(
            required={"milestone_id", "milestone_type", "title", "achieved_at"},
            optional={
                "description",
                "achievement_criteria",
                "therapeutic_significance",
                "celebration_content",
                "related_skills",
            },
            indexed={"milestone_id", "milestone_type", "achieved_at"},
            unique={"milestone_id"},
        ),
        NodeType.SAFETY_CHECK: NodeProperties(
            required={
                "check_id",
                "content_id",
                "safety_level",
                "safety_score",
                "checked_at",
            },
            optional={
                "risk_factors",
                "protective_factors",
                "crisis_indicators",
                "intervention_recommendations",
                "requires_human_review",
            },
            indexed={"check_id", "content_id", "safety_level", "checked_at"},
            unique={"check_id"},
        ),
    }

    # Relationship property definitions
    RELATIONSHIP_PROPERTIES: dict[RelationshipType, RelationshipProperties] = {
        RelationshipType.LEADS_TO: RelationshipProperties(
            required={"created_at"},
            optional={"probability", "conditions", "narrative_weight"},
            indexed={"created_at"},
        ),
        RelationshipType.MADE_CHOICE: RelationshipProperties(
            required={"timestamp", "choice_id"},
            optional={"processing_time", "confidence_level", "context"},
            indexed={"timestamp", "choice_id"},
        ),
        RelationshipType.PRACTICES_SKILL: RelationshipProperties(
            required={"practice_timestamp", "skill_id"},
            optional={"proficiency_demonstrated", "success_level", "context"},
            indexed={"practice_timestamp", "skill_id"},
        ),
        RelationshipType.TRACKS_PROGRESS: RelationshipProperties(
            required={"measurement_timestamp", "metric_value"},
            optional={"measurement_method", "confidence_level", "notes"},
            indexed={"measurement_timestamp"},
        ),
        RelationshipType.VALIDATES: RelationshipProperties(
            required={"validation_timestamp", "validation_result"},
            optional={"validation_score", "validation_notes", "validator_id"},
            indexed={"validation_timestamp"},
        ),
    }

    @classmethod
    def get_node_constraints(cls) -> list[str]:
        """Generate Neo4j constraint statements for all node types."""
        constraints = []

        for node_type, properties in cls.NODE_PROPERTIES.items():
            # Unique constraints
            for unique_prop in properties.unique:
                constraint = f"CREATE CONSTRAINT {node_type.value.lower()}_{unique_prop}_unique IF NOT EXISTS FOR (n:{node_type.value}) REQUIRE n.{unique_prop} IS UNIQUE"
                constraints.append(constraint)

            # Required property constraints
            for required_prop in properties.required:
                constraint = f"CREATE CONSTRAINT {node_type.value.lower()}_{required_prop}_exists IF NOT EXISTS FOR (n:{node_type.value}) REQUIRE n.{required_prop} IS NOT NULL"
                constraints.append(constraint)

        return constraints

    @classmethod
    def get_node_indexes(cls) -> list[str]:
        """Generate Neo4j index statements for all node types."""
        indexes = []

        for node_type, properties in cls.NODE_PROPERTIES.items():
            # Single property indexes
            for indexed_prop in properties.indexed:
                if (
                    indexed_prop not in properties.unique
                ):  # Unique constraints create indexes automatically
                    index = f"CREATE INDEX {node_type.value.lower()}_{indexed_prop}_index IF NOT EXISTS FOR (n:{node_type.value}) ON (n.{indexed_prop})"
                    indexes.append(index)

            # Composite indexes for common query patterns
            if node_type == NodeType.SESSION:
                indexes.append(
                    "CREATE INDEX session_user_state_index IF NOT EXISTS FOR (n:Session) ON (n.user_id, n.session_state)"
                )
                indexes.append(
                    "CREATE INDEX session_created_state_index IF NOT EXISTS FOR (n:Session) ON (n.created_at, n.session_state)"
                )

            elif node_type == NodeType.SCENE:
                indexes.append(
                    "CREATE INDEX scene_session_type_index IF NOT EXISTS FOR (n:Scene) ON (n.session_id, n.scene_type)"
                )

            elif node_type == NodeType.PROGRESS_METRIC:
                indexes.append(
                    "CREATE INDEX metric_type_updated_index IF NOT EXISTS FOR (n:ProgressMetric) ON (n.progress_type, n.last_updated)"
                )

        return indexes

    @classmethod
    def get_relationship_indexes(cls) -> list[str]:
        """Generate Neo4j relationship index statements."""
        indexes = []

        for rel_type, properties in cls.RELATIONSHIP_PROPERTIES.items():
            for indexed_prop in properties.indexed:
                index = f"CREATE INDEX {rel_type.value.lower()}_{indexed_prop}_rel_index IF NOT EXISTS FOR ()-[r:{rel_type.value}]-() ON (r.{indexed_prop})"
                indexes.append(index)

        return indexes

    @classmethod
    def get_all_schema_statements(cls) -> list[str]:
        """Get all schema creation statements in proper order."""
        statements = []

        # First create constraints (these also create indexes for unique properties)
        statements.extend(cls.get_node_constraints())

        # Then create additional indexes
        statements.extend(cls.get_node_indexes())
        statements.extend(cls.get_relationship_indexes())

        return statements


class GraphConstraints:
    """Additional graph constraints and validation rules."""

    @staticmethod
    def get_business_logic_constraints() -> list[str]:
        """Get business logic constraints for the therapeutic gameplay graph."""
        return [
            # Session constraints
            "// Ensure sessions have valid state transitions",
            "// Ensure completed sessions have completion timestamps",
            # Narrative flow constraints
            "// Ensure scenes belong to valid sessions",
            "// Ensure choices belong to valid scenes",
            "// Ensure narrative flow is acyclic (no infinite loops)",
            # Therapeutic constraints
            "// Ensure therapeutic goals are measurable",
            "// Ensure progress metrics have valid ranges",
            "// Ensure safety checks are current",
            # Temporal constraints
            "// Ensure timestamps are chronologically consistent",
            "// Ensure session activities occur within session timeframe",
        ]


class GraphIndexes:
    """Performance optimization indexes for common query patterns."""

    @staticmethod
    def get_performance_indexes() -> list[str]:
        """Get performance optimization indexes."""
        return [
            # Full-text search indexes
            "CREATE FULLTEXT INDEX scene_content_fulltext IF NOT EXISTS FOR (n:Scene) ON EACH [n.title, n.description, n.narrative_content]",
            "CREATE FULLTEXT INDEX choice_content_fulltext IF NOT EXISTS FOR (n:Choice) ON EACH [n.choice_text]",
            "CREATE FULLTEXT INDEX skill_content_fulltext IF NOT EXISTS FOR (n:Skill) ON EACH [n.skill_name, n.description]",
            # Range indexes for numerical queries
            "CREATE RANGE INDEX therapeutic_relevance_range IF NOT EXISTS FOR (n:Choice) ON (n.therapeutic_relevance)",
            "CREATE RANGE INDEX safety_score_range IF NOT EXISTS FOR (n:SafetyCheck) ON (n.safety_score)",
            "CREATE RANGE INDEX progress_value_range IF NOT EXISTS FOR (n:ProgressMetric) ON (n.current_value)",
            # Point indexes for exact matches
            "CREATE POINT INDEX session_location IF NOT EXISTS FOR (n:Session) ON (n.location) OPTIONS {indexConfig: {`spatial.cartesian.min`: [-100.0, -100.0], `spatial.cartesian.max`: [100.0, 100.0]}}",
        ]
