// TTA Therapeutic Gaming Neo4j Database Schema Initialization
// This script sets up the complete database schema for the TTA system
// ============================================================================
// CONSTRAINTS AND INDEXES
// ============================================================================
// Player Constraints
CREATE CONSTRAINT player_id_unique IF NOT EXISTS
FOR (p:Player)
REQUIRE p.player_id IS UNIQUE;
CREATE CONSTRAINT player_username_unique IF NOT EXISTS
FOR (p:Player)
REQUIRE p.username IS UNIQUE;
CREATE CONSTRAINT player_email_unique IF NOT EXISTS
FOR (p:Player)
REQUIRE p.email IS UNIQUE;

// Character Constraints
CREATE CONSTRAINT character_id_unique IF NOT EXISTS
FOR (c:Character)
REQUIRE c.character_id IS UNIQUE;

// World Constraints
CREATE CONSTRAINT world_id_unique IF NOT EXISTS
FOR (w:World)
REQUIRE w.world_id IS UNIQUE;

// Session Constraints
CREATE CONSTRAINT session_id_unique IF NOT EXISTS
FOR (s:Session)
REQUIRE s.session_id IS UNIQUE;

// Progress Constraints
CREATE CONSTRAINT progress_id_unique IF NOT EXISTS
FOR (pr:Progress)
REQUIRE pr.progress_id IS UNIQUE;

// Milestone Constraints
CREATE CONSTRAINT milestone_id_unique IF NOT EXISTS
FOR (m:Milestone)
REQUIRE m.milestone_id IS UNIQUE;

// Achievement Constraints
CREATE CONSTRAINT achievement_id_unique IF NOT EXISTS
FOR (a:Achievement)
REQUIRE a.achievement_id IS UNIQUE;

// ============================================================================
// INDEXES FOR PERFORMANCE
// ============================================================================

// Player Indexes
CREATE INDEX player_created_at IF NOT EXISTS
FOR (p:Player)
ON (p.created_at);
CREATE INDEX player_last_login IF NOT EXISTS
FOR (p:Player)
ON (p.last_login);
CREATE INDEX player_is_active IF NOT EXISTS
FOR (p:Player)
ON (p.is_active);

// Character Indexes
CREATE INDEX character_player_id IF NOT EXISTS
FOR (c:Character)
ON (c.player_id);
CREATE INDEX character_created_at IF NOT EXISTS
FOR (c:Character)
ON (c.created_at);
CREATE INDEX character_is_active IF NOT EXISTS
FOR (c:Character)
ON (c.is_active);
CREATE INDEX character_therapeutic_readiness IF NOT EXISTS
FOR (c:Character)
ON (c.therapeutic_readiness_level);

// World Indexes
CREATE INDEX world_therapeutic_themes IF NOT EXISTS
FOR (w:World)
ON (w.therapeutic_themes);
CREATE INDEX world_difficulty_level IF NOT EXISTS
FOR (w:World)
ON (w.difficulty_level);
CREATE INDEX world_is_featured IF NOT EXISTS
FOR (w:World)
ON (w.is_featured);
CREATE INDEX world_created_at IF NOT EXISTS
FOR (w:World)
ON (w.created_at);

// Session Indexes
CREATE INDEX session_character_id IF NOT EXISTS
FOR (s:Session)
ON (s.character_id);
CREATE INDEX session_world_id IF NOT EXISTS
FOR (s:Session)
ON (s.world_id);
CREATE INDEX session_status IF NOT EXISTS
FOR (s:Session)
ON (s.status);
CREATE INDEX session_created_at IF NOT EXISTS
FOR (s:Session)
ON (s.created_at);

// Progress Indexes
CREATE INDEX progress_session_id IF NOT EXISTS
FOR (pr:Progress)
ON (pr.session_id);
CREATE INDEX progress_character_id IF NOT EXISTS
FOR (pr:Progress)
ON (pr.character_id);
CREATE INDEX progress_updated_at IF NOT EXISTS
FOR (pr:Progress)
ON (pr.updated_at);

// ============================================================================
// SAMPLE DATA CREATION
// ============================================================================

// Create Sample Therapeutic Worlds
CREATE
  (w1:World
    {
      world_id: 'therapeutic_world_001',
      name: 'Mindful Meadows',
      description:
        'A peaceful therapeutic environment focused on anxiety management and mindfulness practices.',
      long_description:
        'Mindful Meadows is a serene virtual environment designed specifically for individuals working through anxiety and stress-related challenges. The world features calming natural landscapes, guided meditation spaces, and gentle interactive elements that promote relaxation and self-reflection.',
      setting_description:
        'Rolling green hills dotted with wildflowers, peaceful streams, and cozy meditation pavilions under ancient oak trees.',
      therapeutic_themes: [
        'anxiety_management',
        'mindfulness',
        'stress_reduction',
        'self_compassion'
      ],
      therapeutic_approaches: [
        'cognitive_behavioral_therapy',
        'mindfulness_based_stress_reduction',
        'acceptance_commitment_therapy'
      ],
      difficulty_level: 'beginner',
      estimated_duration_minutes: 30,
      key_characters: [
        'Sage the Wise Owl',
        'Luna the Gentle Guide',
        'River the Flowing Spirit'
      ],
      main_storylines: [
        'The Path of Inner Peace',
        'Breathing with the Seasons',
        'Finding Your Safe Space'
      ],
      therapeutic_techniques_used: [
        'progressive_muscle_relaxation',
        'guided_imagery',
        'breathing_exercises',
        'cognitive_reframing'
      ],
      prerequisites: [],
      recommended_therapeutic_readiness: 5,
      content_warnings: [],
      available_parameters: [
        'session_length',
        'guidance_level',
        'challenge_intensity',
        'interaction_frequency'
      ],
      default_parameters:
        'session_length:30_minutes,guidance_level:supportive,challenge_intensity:low,interaction_frequency:moderate',
      creator_notes:
        'Designed for individuals new to therapeutic gaming or those seeking a gentle, supportive environment for anxiety work.',
      therapeutic_goals_addressed: [
        'reduce_anxiety_symptoms',
        'develop_coping_strategies',
        'increase_self_awareness',
        'build_emotional_regulation'
      ],
      success_metrics: [
        'anxiety_level_reduction',
        'coping_skill_utilization',
        'session_completion_rate',
        'self_reported_wellbeing'
      ],
      completion_rate: 0.85,
      average_session_count: 8,
      therapeutic_effectiveness_score: 4.2,
      tags: [
        'beginner_friendly',
        'anxiety_focused',
        'nature_based',
        'mindfulness'
      ],
      player_count: 0,
      average_rating: 4.5,
      is_featured: true,
      created_at: datetime(),
      updated_at: datetime()
    });

CREATE
  (w2:World
    {
      world_id: 'therapeutic_world_002',
      name: 'Social Bridges',
      description:
        'An interactive therapeutic world designed to build social confidence and communication skills.',
      long_description:
        'Social Bridges provides a safe, structured environment for practicing social interactions and building confidence in interpersonal situations. The world features various social scenarios, from casual conversations to more challenging group dynamics.',
      setting_description:
        'A vibrant community center with various social spaces: a cozy café, a community garden, a library reading circle, and a creative arts studio.',
      therapeutic_themes: [
        'social_anxiety',
        'communication_skills',
        'confidence_building',
        'interpersonal_relationships'
      ],
      therapeutic_approaches: [
        'social_skills_training',
        'exposure_therapy',
        'cognitive_behavioral_therapy',
        'role_playing_therapy'
      ],
      difficulty_level: 'intermediate',
      estimated_duration_minutes: 45,
      key_characters: [
        'Alex the Conversation Coach',
        'Maya the Empathy Guide',
        'Sam the Confidence Builder'
      ],
      main_storylines: [
        'The Art of Small Talk',
        'Building Meaningful Connections',
        'Navigating Group Dynamics'
      ],
      therapeutic_techniques_used: [
        'gradual_exposure',
        'social_skills_practice',
        'assertiveness_training',
        'empathy_building'
      ],
      prerequisites: ['basic_anxiety_management'],
      recommended_therapeutic_readiness: 7,
      content_warnings: ['social_interaction_scenarios'],
      available_parameters: [
        'social_complexity',
        'group_size',
        'interaction_style',
        'feedback_frequency'
      ],
      default_parameters:
        'social_complexity:moderate,group_size:small,interaction_style:supportive,feedback_frequency:regular',
      creator_notes:
        'Best suited for individuals who have developed basic coping skills and are ready to practice social interactions in a supportive environment.',
      therapeutic_goals_addressed: [
        'reduce_social_anxiety',
        'improve_communication_skills',
        'build_social_confidence',
        'develop_interpersonal_relationships'
      ],
      success_metrics: [
        'social_interaction_quality',
        'confidence_level_increase',
        'communication_skill_improvement',
        'relationship_building_success'
      ],
      completion_rate: 0.78,
      average_session_count: 12,
      therapeutic_effectiveness_score: 4.0,
      tags: [
        'social_skills',
        'intermediate_level',
        'communication_focused',
        'confidence_building'
      ],
      player_count: 0,
      average_rating: 4.3,
      is_featured: true,
      created_at: datetime(),
      updated_at: datetime()
    });

CREATE
  (w3:World
    {
      world_id: 'therapeutic_world_003',
      name: 'Resilience Ridge',
      description:
        'A challenging therapeutic environment focused on building emotional resilience and overcoming adversity.',
      long_description:
        'Resilience Ridge is designed for individuals ready to face more challenging therapeutic work. This world presents various obstacles and setbacks that mirror real-life challenges, providing opportunities to practice resilience-building skills.',
      setting_description:
        'A mountainous landscape with winding paths, weather changes, and various challenges that require perseverance and adaptive thinking.',
      therapeutic_themes: [
        'resilience_building',
        'emotional_regulation',
        'stress_management',
        'personal_growth'
      ],
      therapeutic_approaches: [
        'resilience_training',
        'cognitive_behavioral_therapy',
        'acceptance_commitment_therapy',
        'post_traumatic_growth'
      ],
      difficulty_level: 'advanced',
      estimated_duration_minutes: 60,
      key_characters: [
        'Phoenix the Resilience Mentor',
        'Storm the Challenge Guide',
        'Dawn the Hope Keeper'
      ],
      main_storylines: [
        'The Mountain of Challenges',
        'Weathering the Storm',
        'Rising from Setbacks'
      ],
      therapeutic_techniques_used: [
        'stress_inoculation',
        'cognitive_restructuring',
        'emotional_regulation_skills',
        'meaning_making'
      ],
      prerequisites: [
        'anxiety_management',
        'basic_coping_skills',
        'emotional_awareness'
      ],
      recommended_therapeutic_readiness: 8,
      content_warnings: [
        'challenging_scenarios',
        'simulated_setbacks',
        'emotional_intensity'
      ],
      available_parameters: [
        'challenge_level',
        'support_availability',
        'setback_frequency',
        'recovery_guidance'
      ],
      default_parameters:
        'challenge_level:high,support_availability:moderate,setback_frequency:realistic,recovery_guidance:available',
      creator_notes:
        'Recommended for individuals who have developed foundational therapeutic skills and are ready for more intensive resilience work.',
      therapeutic_goals_addressed: [
        'build_emotional_resilience',
        'develop_stress_tolerance',
        'improve_problem_solving',
        'foster_post_traumatic_growth'
      ],
      success_metrics: [
        'resilience_score_improvement',
        'stress_tolerance_increase',
        'problem_solving_effectiveness',
        'emotional_regulation_stability'
      ],
      completion_rate: 0.65,
      average_session_count: 15,
      therapeutic_effectiveness_score: 4.4,
      tags: [
        'advanced_level',
        'resilience_focused',
        'challenging',
        'growth_oriented'
      ],
      player_count: 0,
      average_rating: 4.6,
      is_featured: false,
      created_at: datetime(),
      updated_at: datetime()
    });

// Create Sample Achievements
CREATE
  (a1:Achievement
    {
      achievement_id: 'first_steps',
      name: 'First Steps',
      description: 'Completed your first therapeutic gaming session',
      therapeutic_value:
        'Demonstrates initial engagement with therapeutic process',
      category: 'engagement',
      points: 10,
      icon: 'footsteps',
      rarity: 'common',
      created_at: datetime()
    });

CREATE
  (a2:Achievement
    {
      achievement_id: 'mindful_moments',
      name: 'Mindful Moments',
      description: 'Completed 5 mindfulness-based sessions',
      therapeutic_value:
        'Shows commitment to mindfulness practice and anxiety management',
      category: 'mindfulness',
      points: 25,
      icon: 'lotus',
      rarity: 'uncommon',
      created_at: datetime()
    });

CREATE
  (a3:Achievement
    {
      achievement_id: 'social_butterfly',
      name: 'Social Butterfly',
      description: 'Successfully completed 10 social interaction scenarios',
      therapeutic_value:
        'Demonstrates significant progress in social confidence and communication skills',
      category: 'social',
      points: 50,
      icon: 'butterfly',
      rarity: 'rare',
      created_at: datetime()
    });

CREATE
  (a4:Achievement
    {
      achievement_id: 'resilience_champion',
      name: 'Resilience Champion',
      description: 'Overcame 20 challenging scenarios in Resilience Ridge',
      therapeutic_value:
        'Shows exceptional emotional resilience and stress management capabilities',
      category: 'resilience',
      points: 100,
      icon: 'mountain',
      rarity: 'legendary',
      created_at: datetime()
    });

// Create Sample Milestones
CREATE
  (m1:Milestone
    {
      milestone_id: 'anxiety_awareness',
      name: 'Anxiety Awareness',
      description:
        'Developed ability to recognize anxiety triggers and early warning signs',
      therapeutic_significance:
        'Foundation skill for anxiety management and emotional regulation',
      category: 'awareness',
      required_sessions: 3,
      therapeutic_goals: ['anxiety_management', 'self_awareness'],
      measurement_criteria: [
        'trigger_identification_accuracy',
        'early_warning_recognition',
        'self_monitoring_consistency'
      ],
      created_at: datetime()
    });

CREATE
  (m2:Milestone
    {
      milestone_id: 'coping_toolkit',
      name: 'Coping Toolkit',
      description:
        'Built a personalized set of coping strategies and can apply them effectively',
      therapeutic_significance:
        'Essential for independent anxiety management and emotional regulation',
      category: 'skills',
      required_sessions: 5,
      therapeutic_goals: [
        'coping_skills',
        'emotional_regulation',
        'self_efficacy'
      ],
      measurement_criteria: [
        'strategy_variety',
        'application_effectiveness',
        'independent_usage'
      ],
      created_at: datetime()
    });

CREATE
  (m3:Milestone
    {
      milestone_id: 'social_confidence',
      name: 'Social Confidence',
      description:
        'Demonstrates increased confidence in social interactions and communication',
      therapeutic_significance:
        'Critical for building meaningful relationships and reducing social anxiety',
      category: 'social',
      required_sessions: 8,
      therapeutic_goals: [
        'social_confidence',
        'communication_skills',
        'relationship_building'
      ],
      measurement_criteria: [
        'interaction_initiation',
        'conversation_quality',
        'social_comfort_level'
      ],
      created_at: datetime()
    });

// Log initialization completion
CREATE
  (init:SystemLog
    {
      log_id: 'schema_init_' + toString(timestamp()),
      event_type: 'schema_initialization',
      message:
        'TTA Therapeutic Gaming database schema initialized successfully',
      timestamp: datetime(),
      details:
        'constraints_created:8,indexes_created:15,sample_worlds:3,sample_achievements:4,sample_milestones:3'
    });