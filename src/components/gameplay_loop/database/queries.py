"""
Database Queries for Gameplay Loop

This module provides pre-defined Cypher queries for common gameplay loop operations
including session management, scene navigation, choice processing, and progress tracking.
"""

from .schema import GameplayLoopSchema


class GameplayQueries:
    """Collection of Cypher queries for gameplay loop operations."""

    def __init__(self):
        self.schema = GameplayLoopSchema()

    # Session Queries
    def get_active_sessions_for_user(self) -> str:
        """Get all active sessions for a user."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{user_id: $user_id, is_active: true}})
        RETURN s
        ORDER BY s.last_activity_time DESC
        """

    def get_session_with_current_scene(self) -> str:
        """Get session with its current scene."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{session_id: $session_id}})
        OPTIONAL MATCH (s)-[:{self.schema.RELATIONSHIPS["CURRENT_SCENE"]}]->(current_scene:{self.schema.NODE_LABELS["SCENE"]})
        RETURN s, current_scene
        """

    def get_session_history(self) -> str:
        """Get session with scene history."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{session_id: $session_id}})
        OPTIONAL MATCH (s)-[:{self.schema.RELATIONSHIPS["HAS_SCENE"]}]->(scenes:{self.schema.NODE_LABELS["SCENE"]})
        RETURN s, collect(scenes) as scene_history
        ORDER BY scenes.created_at
        """

    # Scene Navigation Queries
    def get_scene_with_choices(self) -> str:
        """Get scene with all available choices."""
        return f"""
        MATCH (sc:{self.schema.NODE_LABELS["SCENE"]} {{scene_id: $scene_id}})
        OPTIONAL MATCH (sc)-[:{self.schema.RELATIONSHIPS["HAS_CHOICE"]}]->(c:{self.schema.NODE_LABELS["CHOICE"]})
        WHERE c.is_available = true
        RETURN sc, collect(c) as choices
        ORDER BY c.therapeutic_value DESC, c.created_at
        """

    def get_next_scenes_from_choice(self) -> str:
        """Get possible next scenes from a choice."""
        return f"""
        MATCH (c:{self.schema.NODE_LABELS["CHOICE"]} {{choice_id: $choice_id}})
              -[:{self.schema.RELATIONSHIPS["LEADS_TO"]}]->
              (next_scene:{self.schema.NODE_LABELS["SCENE"]})
        RETURN next_scene
        ORDER BY next_scene.difficulty_level, next_scene.created_at
        """

    def link_scene_to_session(self) -> str:
        """Link a scene to a session."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{session_id: $session_id}}),
              (sc:{self.schema.NODE_LABELS["SCENE"]} {{scene_id: $scene_id}})
        MERGE (s)-[:{self.schema.RELATIONSHIPS["HAS_SCENE"]}]->(sc)
        RETURN s, sc
        """

    def set_current_scene(self) -> str:
        """Set the current scene for a session."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{session_id: $session_id}})
        OPTIONAL MATCH (s)-[old_current:{self.schema.RELATIONSHIPS["CURRENT_SCENE"]}]->()
        DELETE old_current
        WITH s
        MATCH (new_scene:{self.schema.NODE_LABELS["SCENE"]} {{scene_id: $scene_id}})
        CREATE (s)-[:{self.schema.RELATIONSHIPS["CURRENT_SCENE"]}]->(new_scene)
        SET s.current_scene_id = $scene_id,
            s.updated_at = datetime()
        RETURN s, new_scene
        """

    # Choice Processing Queries
    def record_user_choice(self) -> str:
        """Record a user's choice and create consequence relationship."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{session_id: $session_id}}),
              (c:{self.schema.NODE_LABELS["CHOICE"]} {{choice_id: $choice_id}})
        CREATE (s)-[made:{self.schema.RELATIONSHIPS["MADE_CHOICE"]} {{
            made_at: datetime(),
            response_time: $response_time,
            emotional_state_before: $emotional_state_before,
            emotional_state_after: $emotional_state_after
        }}]->(c)
        RETURN made
        """

    def create_choice_consequence(self) -> str:
        """Create a consequence set for a choice."""
        return f"""
        MATCH (c:{self.schema.NODE_LABELS["CHOICE"]} {{choice_id: $choice_id}})
        CREATE (consequence:{self.schema.NODE_LABELS["CONSEQUENCE"]} {{
            consequence_id: $consequence_id,
            choice_id: $choice_id,
            session_id: $session_id,
            immediate_effects: $immediate_effects,
            delayed_effects: $delayed_effects,
            narrative_changes: $narrative_changes,
            character_attribute_changes: $character_attribute_changes,
            skill_developments: $skill_developments,
            relationship_changes: $relationship_changes,
            therapeutic_progress: $therapeutic_progress,
            emotional_impact: $emotional_impact,
            learning_outcomes: $learning_outcomes,
            is_applied: $is_applied,
            application_time: $application_time,
            created_at: datetime()
        }})
        CREATE (c)-[:{self.schema.RELATIONSHIPS["HAS_CONSEQUENCE"]}]->(consequence)
        RETURN consequence
        """

    # Progress Tracking Queries
    def create_progress_marker(self) -> str:
        """Create a progress marker for therapeutic development."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{session_id: $session_id}})
        CREATE (progress:{self.schema.NODE_LABELS["PROGRESS"]} {{
            progress_id: $progress_id,
            session_id: $session_id,
            user_id: $user_id,
            progress_type: $progress_type,
            title: $title,
            description: $description,
            triggered_by_choice: $triggered_by_choice,
            scene_context: $scene_context,
            progress_value: $progress_value,
            difficulty_level: $difficulty_level,
            therapeutic_domains: $therapeutic_domains,
            skills_involved: $skills_involved,
            achieved_at: datetime()
        }})
        CREATE (s)-[:{self.schema.RELATIONSHIPS["ACHIEVES_PROGRESS"]}]->(progress)
        RETURN progress
        """

    def get_user_progress_summary(self) -> str:
        """Get comprehensive progress summary for a user."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{user_id: $user_id}})
              -[:{self.schema.RELATIONSHIPS["ACHIEVES_PROGRESS"]}]->
              (p:{self.schema.NODE_LABELS["PROGRESS"]})
        RETURN
            count(p) as total_progress_markers,
            collect(DISTINCT p.progress_type) as progress_types,
            collect(DISTINCT p.therapeutic_domains) as therapeutic_domains,
            avg(p.progress_value) as average_progress_value,
            max(p.achieved_at) as latest_progress
        """

    def get_skill_development_history(self) -> str:
        """Get skill development history for a user."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{user_id: $user_id}})
              -[:{self.schema.RELATIONSHIPS["DEVELOPS_SKILL"]}]->
              (skill:{self.schema.NODE_LABELS["SKILL"]})
        RETURN skill
        ORDER BY skill.last_practiced DESC
        """

    # Therapeutic Validation Queries
    def create_validation_result(self) -> str:
        """Create a validation result record."""
        return f"""
        CREATE (validation:{self.schema.NODE_LABELS["VALIDATION"]} {{
            validation_id: $validation_id,
            session_id: $session_id,
            validation_type: $validation_type,
            status: $status,
            content_type: $content_type,
            content_id: $content_id,
            is_valid: $is_valid,
            confidence_score: $confidence_score,
            issues_found: $issues_found,
            warnings: $warnings,
            recommendations: $recommendations,
            user_context: $user_context,
            therapeutic_context: $therapeutic_context,
            validated_at: datetime(),
            validator_version: $validator_version
        }})
        RETURN validation
        """

    def get_session_validations(self) -> str:
        """Get all validation results for a session."""
        return f"""
        MATCH (v:{self.schema.NODE_LABELS["VALIDATION"]} {{session_id: $session_id}})
        RETURN v
        ORDER BY v.validated_at DESC
        """

    # Analytics Queries
    def get_session_analytics(self) -> str:
        """Get comprehensive analytics for a session."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{session_id: $session_id}})
        OPTIONAL MATCH (s)-[:{self.schema.RELATIONSHIPS["MADE_CHOICE"]}]->(choices:{self.schema.NODE_LABELS["CHOICE"]})
        OPTIONAL MATCH (s)-[:{self.schema.RELATIONSHIPS["ACHIEVES_PROGRESS"]}]->(progress:{self.schema.NODE_LABELS["PROGRESS"]})
        OPTIONAL MATCH (s)-[:{self.schema.RELATIONSHIPS["HAS_SCENE"]}]->(scenes:{self.schema.NODE_LABELS["SCENE"]})
        RETURN
            s,
            count(DISTINCT choices) as total_choices,
            count(DISTINCT progress) as total_progress_markers,
            count(DISTINCT scenes) as total_scenes,
            avg(choices.therapeutic_value) as avg_therapeutic_value,
            collect(DISTINCT choices.choice_type) as choice_types_used,
            collect(DISTINCT progress.progress_type) as progress_types_achieved
        """

    def get_therapeutic_effectiveness_metrics(self) -> str:
        """Get therapeutic effectiveness metrics for a user."""
        return f"""
        MATCH (s:{self.schema.NODE_LABELS["SESSION"]} {{user_id: $user_id}})
        OPTIONAL MATCH (s)-[made:{self.schema.RELATIONSHIPS["MADE_CHOICE"]}]->(c:{self.schema.NODE_LABELS["CHOICE"]})
        WHERE c.choice_type IN ['therapeutic', 'skill_building', 'emotional_regulation']
        OPTIONAL MATCH (s)-[:{self.schema.RELATIONSHIPS["ACHIEVES_PROGRESS"]}]->(p:{self.schema.NODE_LABELS["PROGRESS"]})
        RETURN
            count(DISTINCT s) as total_sessions,
            sum(s.total_session_time) as total_time,
            count(made) as therapeutic_choices_made,
            avg(c.therapeutic_value) as avg_therapeutic_choice_value,
            count(p) as total_progress_markers,
            avg(p.progress_value) as avg_progress_value
        """
