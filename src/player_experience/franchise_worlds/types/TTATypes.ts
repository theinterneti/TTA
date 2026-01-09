// Logseq: [[TTA.dev/Player_experience/Franchise_worlds/Types/Ttatypes]]
/**
 * TypeScript type definitions for TTA models
 *
 * These types mirror the Python models in the TTA system to ensure
 * compatibility between the franchise world system and existing TTA components.
 */

// Enums
export enum TherapeuticApproach {
  CBT = 'cognitive_behavioral_therapy',
  MINDFULNESS = 'mindfulness',
  NARRATIVE_THERAPY = 'narrative_therapy',
  SOMATIC = 'somatic_therapy',
  HUMANISTIC = 'humanistic',
  PSYCHODYNAMIC = 'psychodynamic',
  ACCEPTANCE_COMMITMENT = 'acceptance_commitment_therapy',
  DIALECTICAL_BEHAVIOR = 'dialectical_behavior_therapy',
  GROUP_THERAPY = 'group_therapy',
  SOLUTION_FOCUSED = 'solution_focused_therapy'
}

export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced'
}

export enum IntensityLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high'
}

// Core interfaces
export interface WorldDetails {
  world_id: string;
  name: string;
  description: string;
  long_description: string;
  therapeutic_themes: string[];
  therapeutic_approaches: TherapeuticApproach[];
  difficulty_level: DifficultyLevel;
  estimated_duration: { hours: number };
  setting_description: string;
  key_characters: Array<{
    name: string;
    role: string;
    description: string;
  }>;
  main_storylines: string[];
  therapeutic_techniques_used: string[];
  prerequisites: Array<{
    type: string;
    description: string;
  }>;
  recommended_therapeutic_readiness: number;
  content_warnings: string[];
}

export interface WorldParameters {
  therapeutic_intensity: number; // 0.0 to 1.0
  narrative_pace: 'slow' | 'medium' | 'fast';
  interaction_frequency: 'minimal' | 'balanced' | 'frequent';
  challenge_level: DifficultyLevel;
  focus_areas: string[];
  avoid_topics: string[];
  session_length_preference: number; // minutes
}

export interface WorldSummary {
  world_id: string;
  name: string;
  description: string;
  therapeutic_themes: string[];
  therapeutic_approaches: TherapeuticApproach[];
  difficulty_level: DifficultyLevel;
  estimated_duration: { hours: number };
  compatibility_score: number;
  preview_image?: string;
  tags: string[];
  player_count: number;
  average_rating: number;
  is_featured: boolean;
}

export interface Character {
  character_id: string;
  player_id: string;
  name: string;
  appearance: CharacterAppearance;
  background: CharacterBackground;
  therapeutic_profile: TherapeuticProfile;
  created_at: Date;
  last_active: Date;
  active_worlds: string[];
  total_session_time: number; // minutes
  session_count: number;
  is_active: boolean;
}

export interface CharacterAppearance {
  physical_description: string;
  clothing_style: string;
  distinctive_features: string[];
  avatar_preferences: Record<string, any>;
}

export interface CharacterBackground {
  backstory: string;
  personality_traits: string[];
  core_values: string[];
  relationships: Array<{
    character_id: string;
    relationship_type: string;
    description: string;
  }>;
  significant_events: Array<{
    event_description: string;
    emotional_impact: number;
    therapeutic_relevance: string;
  }>;
}

export interface TherapeuticProfile {
  therapeutic_goals: TherapeuticGoal[];
  preferred_approaches: TherapeuticApproach[];
  intensity_preference: IntensityLevel;
  focus_areas: string[];
  avoid_topics: string[];
  progress_markers: ProgressMarker[];
  therapeutic_readiness: number;
  crisis_indicators: string[];
}

export interface TherapeuticGoal {
  goal_id: string;
  title: string;
  description: string;
  category: string;
  target_metrics: Array<{
    metric_name: string;
    target_value: number;
    current_value: number;
    unit: string;
  }>;
  milestones: Array<{
    milestone_id: string;
    description: string;
    target_date?: Date;
    completed: boolean;
    completion_date?: Date;
  }>;
  priority: 'low' | 'medium' | 'high';
  status: 'active' | 'paused' | 'completed' | 'archived';
  created_at: Date;
  updated_at: Date;
}

export interface ProgressMarker {
  marker_id: string;
  marker_type: 'milestone' | 'breakthrough' | 'setback' | 'insight';
  description: string;
  therapeutic_significance: number; // 0-1 scale
  emotional_impact: number; // -1 to 1 scale
  timestamp: Date;
  context: string;
  related_goals: string[];
  notes: string;
}

export interface SessionContext {
  session_id: string;
  player_id: string;
  character_id: string;
  world_id: string;
  start_time: Date;
  end_time?: Date;
  status: 'active' | 'paused' | 'completed' | 'crisis';
  therapeutic_settings: TherapeuticSettings;
  progress_markers: ProgressMarker[];
  session_notes: string;
  ai_observations: string[];
  crisis_flags: string[];
}

export interface TherapeuticSettings {
  intensity_level: IntensityLevel;
  therapeutic_approaches: TherapeuticApproach[];
  focus_areas: string[];
  avoid_topics: string[];
  crisis_detection_enabled: boolean;
  safety_monitoring_interval: number; // seconds
  intervention_thresholds: Record<string, number>;
  customizations: Record<string, any>;
}

export interface PlayerProfile {
  player_id: string;
  username: string;
  email: string;
  created_at: Date;
  last_active: Date;
  therapeutic_preferences: TherapeuticPreferences;
  privacy_settings: PrivacySettings;
  crisis_contact_info?: CrisisContactInfo;
  progress_summary: ProgressSummary;
  characters: string[]; // character IDs
  active_sessions: string[]; // session IDs
  completed_worlds: string[]; // world IDs
  achievements: Array<{
    achievement_id: string;
    title: string;
    description: string;
    earned_at: Date;
  }>;
}

export interface TherapeuticPreferences {
  preferred_approaches: TherapeuticApproach[];
  intensity_preference: IntensityLevel;
  session_length_preference: number; // minutes
  focus_areas: string[];
  avoid_topics: string[];
  crisis_keywords: string[];
  therapeutic_goals: string[];
  comfort_level: number; // 0-1 scale
}

export interface PrivacySettings {
  data_sharing_consent: boolean;
  analytics_consent: boolean;
  research_participation_consent: boolean;
  crisis_intervention_consent: boolean;
  data_retention_period: number; // days
  anonymization_preferences: Record<string, boolean>;
}

export interface CrisisContactInfo {
  primary_contact_name: string;
  primary_contact_phone: string;
  primary_contact_relationship: string;
  secondary_contact_name?: string;
  secondary_contact_phone?: string;
  secondary_contact_relationship?: string;
  preferred_crisis_service: string;
  crisis_service_phone: string;
  emergency_instructions: string;
}

export interface ProgressSummary {
  total_session_time: number; // minutes
  total_sessions: number;
  worlds_completed: number;
  achievements_earned: number;
  therapeutic_milestones_reached: number;
  current_streak: number; // days
  longest_streak: number; // days
  last_session_date?: Date;
  progress_highlights: Array<{
    highlight_id: string;
    title: string;
    description: string;
    date: Date;
    category: string;
  }>;
  engagement_metrics: {
    average_session_length: number; // minutes
    sessions_per_week: number;
    completion_rate: number; // 0-1 scale
    satisfaction_rating: number; // 0-5 scale
  };
}

// Utility types for the franchise world system
export interface PlayerPreferences {
  therapeutic_intensity?: number;
  narrative_pace?: 'slow' | 'medium' | 'fast';
  interaction_frequency?: 'minimal' | 'balanced' | 'frequent';
  session_length?: number;
  focus_areas?: string[];
  avoid_topics?: string[];
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
}

export interface SystemStatus {
  status: 'operational' | 'degraded' | 'maintenance' | 'error';
  message: string;
  timestamp: Date;
  details?: Record<string, any>;
}
