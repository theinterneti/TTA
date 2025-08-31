# Neo4j Graph Database Architecture

This document describes the comprehensive Neo4j graph database architecture for the TTA (Therapeutic Text Adventure) gameplay loop system.

## Overview

The Neo4j graph database serves as the backbone for storing and querying complex relationships between users, sessions, narrative elements, therapeutic progress, and validation data. The graph structure enables powerful traversal queries and pattern matching for therapeutic insights.

## Node Types

### Core Gameplay Nodes

#### Session
Represents a complete therapeutic gameplay session.
- **Properties**: session_id (unique), user_id, character_id, world_id, session_state, therapeutic_goals, safety_level, created_at, last_activity
- **Relationships**: Connected to User via HAS_SESSION, contains Scenes via HAS_SCENE

#### Scene
Individual narrative scenes within a session.
- **Properties**: scene_id (unique), session_id, title, description, narrative_content, scene_type, therapeutic_focus, emotional_tone
- **Relationships**: Belongs to Session, contains Choices via HAS_CHOICE, flows to other Scenes via LEADS_TO

#### Choice
User choices available within scenes.
- **Properties**: choice_id (unique), scene_id, choice_text, choice_type, therapeutic_relevance, emotional_weight, difficulty_level
- **Relationships**: Belongs to Scene, results in Consequences via RESULTS_IN

#### Consequence
Outcomes resulting from user choices.
- **Properties**: consequence_id (unique), choice_id, consequences, consequence_type, therapeutic_outcomes
- **Relationships**: Results from Choice, triggers other effects via TRIGGERS

### User and Character Nodes

#### User
Represents system users.
- **Properties**: user_id (unique), created_at, therapeutic_preferences, progress_summary, safety_settings
- **Relationships**: Has Sessions, tracks Progress, develops Skills

#### Character
Playable characters in the therapeutic narrative.
- **Properties**: character_id (unique), character_name, background, therapeutic_profile, appearance
- **Relationships**: Played by Users via PLAYS_AS, located in Worlds

#### World
Game worlds and settings.
- **Properties**: world_id (unique), world_name, description, therapeutic_themes, safety_level
- **Relationships**: Contains Characters and Scenes via LOCATED_IN

### Therapeutic Nodes

#### TherapeuticGoal
Specific therapeutic objectives.
- **Properties**: goal_id (unique), goal_name, goal_type, description, target_metrics, completion_criteria
- **Relationships**: Addressed by Scenes via ADDRESSES_GOAL, supported by Skills

#### Skill
Therapeutic skills to be developed.
- **Properties**: skill_id (unique), skill_name, skill_category, description, learning_objectives, mastery_indicators
- **Relationships**: Supports Goals via SUPPORTS_GOAL, practiced in Scenes via PRACTICES_SKILL

#### Emotion
Emotional states and responses.
- **Properties**: emotion_id (unique), emotion_name, emotion_category, intensity_range, therapeutic_significance
- **Relationships**: Regulated through Skills via REGULATES_EMOTION, tracked in Progress

#### Behavior
Behavioral patterns and changes.
- **Properties**: behavior_id (unique), behavior_name, behavior_type, baseline_frequency, target_frequency
- **Relationships**: Changed through Interventions via CHANGES_BEHAVIOR, measured in Progress

### Progress Tracking Nodes

#### ProgressMetric
Individual progress measurements.
- **Properties**: metric_id (unique), metric_name, progress_type, current_value, baseline_value, target_value
- **Relationships**: Tracked by Users via TRACKS_PROGRESS, measured over time

#### SkillDevelopment
Skill development tracking.
- **Properties**: skill_id (unique), skill_name, current_level, proficiency_score, practice_sessions
- **Relationships**: Developed by Users via DEVELOPS_SKILL, improves over time via IMPROVES

#### Milestone
Significant therapeutic achievements.
- **Properties**: milestone_id (unique), milestone_type, title, description, therapeutic_significance, achieved_at
- **Relationships**: Achieved by Users via ACHIEVES_MILESTONE, relates to Skills and Goals

### Validation and Safety Nodes

#### SafetyCheck
Safety assessments for content.
- **Properties**: check_id (unique), content_id, safety_level, safety_score, risk_factors, protective_factors
- **Relationships**: Validates content via VALIDATES, requires review via REQUIRES_REVIEW

#### ValidationRule
Rules for content validation.
- **Properties**: rule_id (unique), rule_name, rule_type, validation_criteria, severity_level, is_active
- **Relationships**: Applied to content via APPLIES_TO, enforces safety via ENFORCES

#### TherapeuticAlignment
Therapeutic alignment assessments.
- **Properties**: alignment_id (unique), content_id, alignment_type, alignment_score, therapeutic_goals
- **Relationships**: Aligns with Goals via ALIGNS_WITH, supports Skills via SUPPORTS

## Relationship Types

### Session Relationships
- **HAS_SESSION**: User → Session (user owns session)
- **CURRENT_SCENE**: Session → Scene (current active scene)
- **COMPLETED_SCENE**: Session → Scene (completed scenes)
- **MADE_CHOICE**: User → Choice (user made choice)

### Narrative Flow Relationships
- **LEADS_TO**: Scene → Scene (narrative progression)
- **BRANCHES_TO**: Scene → Scene (conditional branching)
- **RETURNS_TO**: Scene → Scene (narrative loops)
- **UNLOCKS**: Choice → Scene (choice unlocks scene)
- **REQUIRES**: Scene → Condition (scene prerequisites)

### Choice and Consequence Relationships
- **HAS_CHOICE**: Scene → Choice (scene contains choice)
- **RESULTS_IN**: Choice → Consequence (choice outcome)
- **TRIGGERS**: Consequence → Event (consequence triggers event)
- **INFLUENCES**: Choice → Progress (choice affects progress)

### Therapeutic Relationships
- **ADDRESSES_GOAL**: Scene → TherapeuticGoal (scene addresses goal)
- **PRACTICES_SKILL**: Scene → Skill (scene practices skill)
- **DEVELOPS_SKILL**: User → SkillDevelopment (user develops skill)
- **REGULATES_EMOTION**: Skill → Emotion (skill regulates emotion)
- **CHANGES_BEHAVIOR**: Intervention → Behavior (intervention changes behavior)
- **ACHIEVES_MILESTONE**: User → Milestone (user achieves milestone)

### Progress Relationships
- **TRACKS_PROGRESS**: User → ProgressMetric (user tracks metric)
- **IMPROVES**: ProgressMetric → ProgressMetric (improvement over time)
- **MEASURES**: Metric → Value (measurement relationship)
- **CORRELATES_WITH**: Metric → Metric (correlation between metrics)

### Validation Relationships
- **VALIDATES**: SafetyCheck → Content (safety validation)
- **PASSES_CHECK**: Content → ValidationRule (content passes rule)
- **FAILS_CHECK**: Content → ValidationRule (content fails rule)
- **ALIGNS_WITH**: Content → TherapeuticGoal (therapeutic alignment)

### Temporal Relationships
- **PRECEDES**: Event → Event (temporal ordering)
- **FOLLOWS**: Event → Event (sequential relationship)
- **CONCURRENT_WITH**: Event → Event (simultaneous events)

## Schema Constraints and Indexes

### Unique Constraints
All primary identifier properties have unique constraints:
- Session.session_id
- User.user_id
- Scene.scene_id
- Choice.choice_id
- Skill.skill_id
- ProgressMetric.metric_id

### Required Property Constraints
Critical properties are marked as required:
- Session: session_id, user_id, created_at, session_state
- Scene: scene_id, session_id, title, scene_type, created_at
- User: user_id, created_at

### Performance Indexes

#### Single Property Indexes
- Session: user_id, created_at, session_state
- Scene: session_id, scene_type, created_at
- Choice: scene_id, choice_type
- ProgressMetric: progress_type, last_updated

#### Composite Indexes
- Session: (user_id, session_state) for user session queries
- Scene: (session_id, scene_type) for session scene queries
- ProgressMetric: (progress_type, last_updated) for progress queries

#### Full-Text Search Indexes
- Scene: title, description, narrative_content
- Choice: choice_text
- Skill: skill_name, description

#### Range Indexes
- Choice: therapeutic_relevance (for scoring queries)
- SafetyCheck: safety_score (for safety filtering)
- ProgressMetric: current_value (for progress analysis)

## Query Patterns

### Common Query Patterns

#### User Session History
```cypher
MATCH (u:User {user_id: $user_id})-[:HAS_SESSION]->(s:Session)
RETURN s
ORDER BY s.created_at DESC
LIMIT 10
```

#### Narrative Path Traversal
```cypher
MATCH (s:Session {session_id: $session_id})-[:HAS_SCENE]->(start:Scene)
MATCH path = (start)-[:LEADS_TO*]->(end:Scene)
RETURN path
ORDER BY length(path) DESC
```

#### Therapeutic Progress Analysis
```cypher
MATCH (u:User {user_id: $user_id})-[:TRACKS_PROGRESS]->(pm:ProgressMetric)
WHERE pm.progress_type = $progress_type
RETURN pm.metric_name, pm.current_value, pm.baseline_value, pm.target_value
ORDER BY pm.last_updated DESC
```

#### Skill Development Tracking
```cypher
MATCH (u:User {user_id: $user_id})-[:DEVELOPS_SKILL]->(sd:SkillDevelopment)
MATCH (sd)-[:PRACTICES_SKILL]-(s:Scene)
RETURN sd.skill_name, sd.current_level, count(s) as practice_sessions
ORDER BY sd.proficiency_score DESC
```

### Advanced Analytics Queries

#### Therapeutic Effectiveness
```cypher
MATCH (u:User {user_id: $user_id})-[:HAS_SESSION]->(s:Session)-[:HAS_SCENE]->(sc:Scene)
WHERE any(focus IN sc.therapeutic_focus WHERE focus = $therapeutic_focus)
MATCH (u)-[:TRACKS_PROGRESS]->(pm:ProgressMetric)
RETURN
  avg(pm.current_value - pm.baseline_value) as avg_improvement,
  count(DISTINCT s) as sessions_with_focus,
  count(DISTINCT sc) as scenes_with_focus
```

#### Narrative Flow Analysis
```cypher
MATCH (s:Session {session_id: $session_id})-[:HAS_SCENE]->(sc:Scene)
OPTIONAL MATCH (sc)-[r:LEADS_TO]->(next:Scene)
RETURN
  sc.scene_type,
  count(r) as outgoing_paths,
  collect(next.scene_type) as next_scene_types
ORDER BY sc.created_at
```

## Migration and Versioning

### Migration System
The database uses a versioned migration system:
1. **001_initial_schema**: Basic constraints and indexes
2. **002_performance_indexes**: Optimization indexes
3. **003_user_nodes**: Initial user and goal nodes
4. **004_skill_nodes**: Therapeutic skill definitions
5. **005_skill_goal_relationships**: Skill-goal connections

### Rollback Capability
Each migration includes rollback statements for safe schema changes.

### Version Tracking
Migration history is tracked in Migration nodes with application timestamps.

## Performance Considerations

### Query Optimization
- Use parameterized queries to leverage query plan caching
- Limit result sets with appropriate LIMIT clauses
- Use indexes for filtering and sorting operations
- Avoid Cartesian products in complex queries

### Connection Management
- Connection pooling with configurable pool size
- Automatic retry logic with exponential backoff
- Health check monitoring for connection status
- Graceful connection cleanup on shutdown

### Monitoring
- Query execution time tracking
- Connection pool utilization monitoring
- Index usage statistics
- Memory usage optimization

## Security and Safety

### Data Protection
- Sensitive therapeutic data encryption at rest
- Secure connection protocols (TLS/SSL)
- Access control through authentication
- Audit logging for data access

### Therapeutic Safety
- Content validation before storage
- Safety score tracking for all content
- Crisis indicator detection and alerting
- Human review flagging for sensitive content

## Integration Points

The Neo4j database integrates with:
- **Redis Cache**: For session state and real-time data
- **Therapeutic Safety System**: For content validation
- **Progress Monitoring**: For effectiveness tracking
- **Agent Orchestration**: For AI-driven interactions
- **Analytics Dashboard**: For therapeutic insights
