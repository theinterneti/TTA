"""
Neo4j Cypher Queries for Gameplay Loop

This module contains all Cypher queries used by the gameplay loop system,
organized by functional area for maintainability and reusability.
"""

from typing import Dict, Any


class SessionQueries:
    """Cypher queries for session management."""
    
    CREATE_SESSION = """
    CREATE (s:Session {
        session_id: $session_id,
        user_id: $user_id,
        character_id: $character_id,
        world_id: $world_id,
        session_state: $session_state,
        therapeutic_goals: $therapeutic_goals,
        safety_level: $safety_level,
        created_at: $created_at,
        last_activity: $last_activity,
        session_metrics: $session_metrics
    })
    WITH s
    MATCH (u:User {user_id: $user_id})
    CREATE (u)-[:HAS_SESSION {created_at: $created_at}]->(s)
    RETURN s
    """
    
    UPDATE_SESSION_STATE = """
    MATCH (s:Session {session_id: $session_id})
    SET s.session_state = $new_state,
        s.last_activity = $last_activity
    SET s.completed_at = CASE WHEN $completed_at IS NOT NULL THEN $completed_at ELSE s.completed_at END
    RETURN s
    """
    
    GET_SESSION_BY_ID = """
    MATCH (s:Session {session_id: $session_id})
    RETURN s as session
    """
    
    GET_USER_SESSIONS = """
    MATCH (u:User {user_id: $user_id})-[:HAS_SESSION]->(s:Session)
    RETURN s as session
    ORDER BY s.created_at DESC
    LIMIT $limit
    """
    
    GET_ACTIVE_SESSIONS = """
    MATCH (s:Session)
    WHERE s.session_state IN ['active', 'paused']
    RETURN s as session
    ORDER BY s.last_activity DESC
    """
    
    GET_SESSION_STATISTICS = """
    MATCH (u:User {user_id: $user_id})-[:HAS_SESSION]->(s:Session)
    RETURN 
        count(s) as total_sessions,
        count(CASE WHEN s.session_state = 'completed' THEN 1 END) as completed_sessions,
        avg(duration.inSeconds(datetime(s.created_at), datetime(s.completed_at)).seconds) as avg_session_duration,
        max(s.created_at) as last_session_date
    """


class NarrativeQueries:
    """Cypher queries for narrative management."""
    
    CREATE_SCENE = """
    CREATE (sc:Scene {
        scene_id: $scene_id,
        session_id: $session_id,
        title: $title,
        description: $description,
        narrative_content: $narrative_content,
        scene_type: $scene_type,
        therapeutic_focus: $therapeutic_focus,
        emotional_tone: $emotional_tone,
        scene_objectives: $scene_objectives,
        completion_criteria: $completion_criteria,
        safety_considerations: $safety_considerations,
        created_at: $created_at,
        completed_at: $completed_at
    })
    WITH sc
    MATCH (s:Session {session_id: $session_id})
    CREATE (s)-[:HAS_SCENE {created_at: $created_at}]->(sc)
    RETURN sc
    """
    
    CREATE_CHOICE = """
    CREATE (c:Choice {
        choice_id: $choice_id,
        scene_id: $scene_id,
        choice_text: $choice_text,
        choice_type: $choice_type,
        therapeutic_relevance: $therapeutic_relevance,
        emotional_weight: $emotional_weight,
        difficulty_level: $difficulty_level,
        prerequisites: $prerequisites,
        metadata: $metadata,
        timestamp: $timestamp
    })
    WITH c
    MATCH (sc:Scene {scene_id: $scene_id})
    CREATE (sc)-[:HAS_CHOICE {created_at: $timestamp}]->(c)
    RETURN c
    """
    
    CREATE_NARRATIVE_FLOW = """
    MATCH (from:Scene {scene_id: $from_scene_id})
    MATCH (to:Scene {scene_id: $to_scene_id})
    CREATE (from)-[r:LEADS_TO {
        created_at: $created_at,
        choice_id: $choice_id
    }]->(to)
    SET r += $flow_properties
    RETURN r
    """
    
    GET_SCENE_CHOICES = """
    MATCH (sc:Scene {scene_id: $scene_id})-[:HAS_CHOICE]->(c:Choice)
    RETURN c as choice
    ORDER BY c.timestamp ASC
    """
    
    GET_NARRATIVE_PATH = """
    MATCH (s:Session {session_id: $session_id})-[:HAS_SCENE]->(sc:Scene)
    OPTIONAL MATCH (sc)-[r:LEADS_TO]->(next:Scene)
    RETURN sc as scene, r as flow, next as next_scene
    ORDER BY sc.created_at ASC
    """
    
    GET_SCENE_THERAPEUTIC_CONTENT = """
    MATCH (sc:Scene {scene_id: $scene_id})
    OPTIONAL MATCH (sc)-[:ADDRESSES_GOAL]->(tg:TherapeuticGoal)
    OPTIONAL MATCH (sc)-[:PRACTICES_SKILL]->(sk:Skill)
    RETURN sc as scene, collect(DISTINCT tg) as therapeutic_goals, collect(DISTINCT sk) as skills
    """
    
    FIND_SIMILAR_SCENES = """
    MATCH (sc:Scene {scene_id: $scene_id})
    MATCH (other:Scene)
    WHERE other.scene_id <> $scene_id
    AND any(focus IN sc.therapeutic_focus WHERE focus IN other.therapeutic_focus)
    WITH other, 
         size([x IN sc.therapeutic_focus WHERE x IN other.therapeutic_focus]) as common_focus,
         size(sc.therapeutic_focus + other.therapeutic_focus) as total_focus
    RETURN other as scene, 
           toFloat(common_focus) / total_focus as similarity_score
    ORDER BY similarity_score DESC
    LIMIT $limit
    """


class ProgressQueries:
    """Cypher queries for progress tracking."""
    
    CREATE_PROGRESS_METRIC = """
    CREATE (pm:ProgressMetric {
        metric_id: $metric_id,
        user_id: $user_id,
        metric_name: $metric_name,
        progress_type: $progress_type,
        current_value: $current_value,
        baseline_value: $baseline_value,
        target_value: $target_value,
        measurement_unit: $measurement_unit,
        measurement_method: $measurement_method,
        confidence_level: $confidence_level,
        last_updated: $last_updated
    })
    WITH pm
    MATCH (u:User {user_id: $user_id})
    CREATE (u)-[:TRACKS_PROGRESS {created_at: $last_updated}]->(pm)
    RETURN pm
    """
    
    UPDATE_PROGRESS_METRIC = """
    MATCH (pm:ProgressMetric {metric_id: $metric_id})
    SET pm.current_value = $new_value,
        pm.last_updated = $last_updated
    SET pm.confidence_level = CASE WHEN $confidence_level IS NOT NULL THEN $confidence_level ELSE pm.confidence_level END
    RETURN pm
    """
    
    GET_USER_PROGRESS_METRICS = """
    MATCH (u:User {user_id: $user_id})-[:TRACKS_PROGRESS]->(pm:ProgressMetric)
    WHERE $progress_type IS NULL OR pm.progress_type = $progress_type
    RETURN pm as metric
    ORDER BY pm.last_updated DESC
    """
    
    CREATE_SKILL_DEVELOPMENT = """
    CREATE (sd:SkillDevelopment {
        skill_id: $skill_id,
        user_id: $user_id,
        skill_name: $skill_name,
        skill_category: $skill_category,
        current_level: $current_level,
        proficiency_score: $proficiency_score,
        practice_sessions: $practice_sessions,
        successful_applications: $successful_applications,
        learning_objectives: $learning_objectives,
        completed_objectives: $completed_objectives,
        created_at: $created_at,
        last_practiced: $last_practiced
    })
    WITH sd
    MATCH (u:User {user_id: $user_id})
    CREATE (u)-[:DEVELOPS_SKILL {created_at: $created_at}]->(sd)
    RETURN sd
    """
    
    UPDATE_SKILL_PROFICIENCY = """
    MATCH (sd:SkillDevelopment {skill_id: $skill_id})
    SET sd.proficiency_score = $new_proficiency,
        sd.current_level = $new_level,
        sd.practice_sessions = sd.practice_sessions + 1,
        sd.last_practiced = $practiced_at
    RETURN sd
    """
    
    GET_SKILL_PROGRESS_TREND = """
    MATCH (u:User {user_id: $user_id})-[:DEVELOPS_SKILL]->(sd:SkillDevelopment {skill_id: $skill_id})
    MATCH (sd)-[:MEASURED_BY]->(measurement)
    RETURN measurement.timestamp as timestamp, measurement.proficiency_score as score
    ORDER BY measurement.timestamp ASC
    """
    
    CREATE_MILESTONE = """
    CREATE (m:Milestone {
        milestone_id: $milestone_id,
        user_id: $user_id,
        milestone_type: $milestone_type,
        title: $title,
        description: $description,
        therapeutic_significance: $therapeutic_significance,
        achieved_at: $achieved_at,
        related_skills: $related_skills,
        related_goals: $related_goals
    })
    WITH m
    MATCH (u:User {user_id: $user_id})
    CREATE (u)-[:ACHIEVES_MILESTONE {achieved_at: $achieved_at}]->(m)
    RETURN m
    """
    
    GET_USER_MILESTONES = """
    MATCH (u:User {user_id: $user_id})-[:ACHIEVES_MILESTONE]->(m:Milestone)
    WHERE datetime(m.achieved_at) >= datetime($since_date)
    RETURN m as milestone
    ORDER BY m.achieved_at DESC
    LIMIT $limit
    """


class ValidationQueries:
    """Cypher queries for validation and safety checks."""
    
    CREATE_SAFETY_CHECK = """
    CREATE (sc:SafetyCheck {
        check_id: $check_id,
        content_id: $content_id,
        safety_level: $safety_level,
        safety_score: $safety_score,
        risk_factors: $risk_factors,
        protective_factors: $protective_factors,
        crisis_indicators: $crisis_indicators,
        intervention_recommendations: $intervention_recommendations,
        requires_human_review: $requires_human_review,
        checked_at: $checked_at
    })
    RETURN sc
    """
    
    GET_CONTENT_SAFETY_HISTORY = """
    MATCH (sc:SafetyCheck {content_id: $content_id})
    RETURN sc as safety_check
    ORDER BY sc.checked_at DESC
    LIMIT $limit
    """
    
    CREATE_VALIDATION_RULE = """
    CREATE (vr:ValidationRule {
        rule_id: $rule_id,
        rule_name: $rule_name,
        rule_type: $rule_type,
        description: $description,
        validation_criteria: $validation_criteria,
        severity_level: $severity_level,
        is_active: $is_active,
        therapeutic_context: $therapeutic_context,
        created_at: $created_at
    })
    RETURN vr
    """
    
    GET_APPLICABLE_VALIDATION_RULES = """
    MATCH (vr:ValidationRule)
    WHERE vr.is_active = true
    AND ($therapeutic_context IS NULL OR any(ctx IN vr.therapeutic_context WHERE ctx IN $therapeutic_context))
    RETURN vr as rule
    ORDER BY vr.severity_level DESC
    """
    
    CREATE_THERAPEUTIC_ALIGNMENT = """
    CREATE (ta:TherapeuticAlignment {
        alignment_id: $alignment_id,
        content_id: $content_id,
        alignment_type: $alignment_type,
        alignment_score: $alignment_score,
        therapeutic_goals: $therapeutic_goals,
        supported_skills: $supported_skills,
        emotional_benefits: $emotional_benefits,
        contraindications: $contraindications,
        assessed_at: $assessed_at
    })
    RETURN ta
    """


class AnalyticsQueries:
    """Cypher queries for analytics and insights."""
    
    GET_USER_ENGAGEMENT_METRICS = """
    MATCH (u:User {user_id: $user_id})-[:HAS_SESSION]->(s:Session)
    OPTIONAL MATCH (s)-[:HAS_SCENE]->(sc:Scene)
    OPTIONAL MATCH (sc)-[:HAS_CHOICE]->(c:Choice)
    RETURN 
        count(DISTINCT s) as total_sessions,
        count(DISTINCT sc) as total_scenes,
        count(DISTINCT c) as total_choices,
        avg(s.session_metrics.engagement_score) as avg_engagement,
        avg(s.session_metrics.therapeutic_alignment_score) as avg_therapeutic_alignment
    """
    
    GET_THERAPEUTIC_EFFECTIVENESS = """
    MATCH (u:User {user_id: $user_id})-[:TRACKS_PROGRESS]->(pm:ProgressMetric)
    WITH u, pm, 
         (pm.current_value - pm.baseline_value) / (pm.target_value - pm.baseline_value) as progress_ratio
    RETURN 
        pm.progress_type as progress_type,
        avg(progress_ratio) as avg_progress,
        count(pm) as metric_count,
        sum(CASE WHEN progress_ratio > 0 THEN 1 ELSE 0 END) as improving_metrics
    """
    
    GET_NARRATIVE_FLOW_ANALYSIS = """
    MATCH (s:Session {session_id: $session_id})-[:HAS_SCENE]->(sc:Scene)
    OPTIONAL MATCH (sc)-[r:LEADS_TO]->(next:Scene)
    RETURN 
        sc.scene_id as scene_id,
        sc.scene_type as scene_type,
        sc.therapeutic_focus as therapeutic_focus,
        collect(next.scene_id) as next_scenes,
        count(r) as outgoing_paths
    ORDER BY sc.created_at ASC
    """
    
    FIND_THERAPEUTIC_PATTERNS = """
    MATCH (u:User {user_id: $user_id})-[:HAS_SESSION]->(s:Session)-[:HAS_SCENE]->(sc:Scene)
    WHERE any(focus IN sc.therapeutic_focus WHERE focus = $therapeutic_focus)
    MATCH (sc)-[:HAS_CHOICE]->(c:Choice)
    RETURN 
        sc.scene_type as scene_type,
        c.choice_type as choice_type,
        avg(c.therapeutic_relevance) as avg_therapeutic_relevance,
        count(c) as choice_count
    ORDER BY avg_therapeutic_relevance DESC
    """
