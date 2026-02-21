// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Types/Preferences]]
/**
 * Enhanced Player Preference Types for TTA Therapeutic Storytelling Platform
 *
 * This file defines comprehensive player preference types that enable
 * personalized therapeutic experiences through AI-powered storytelling.
 */

export enum IntensityLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high'
}

export enum TherapeuticApproach {
  CBT = 'cognitive_behavioral_therapy',
  MINDFULNESS = 'mindfulness',
  NARRATIVE = 'narrative_therapy',
  SOMATIC = 'somatic_therapy',
  HUMANISTIC = 'humanistic',
  PSYCHODYNAMIC = 'psychodynamic',
  ACCEPTANCE_COMMITMENT = 'acceptance_commitment_therapy',
  DIALECTICAL_BEHAVIOR = 'dialectical_behavior_therapy'
}

export enum ConversationStyle {
  GENTLE = 'gentle',
  DIRECT = 'direct',
  EXPLORATORY = 'exploratory',
  SUPPORTIVE = 'supportive'
}

export enum PreferredSetting {
  PEACEFUL_FOREST = 'peaceful_forest',
  MOUNTAIN_RETREAT = 'mountain_retreat',
  OCEAN_SANCTUARY = 'ocean_sanctuary',
  URBAN_GARDEN = 'urban_garden',
  COZY_LIBRARY = 'cozy_library',
  STARLIT_MEADOW = 'starlit_meadow',
  QUIET_GARDEN = 'quiet_garden',
  FOREST_CLEARING = 'forest_clearing'
}

export interface PlayerPreferences {
  player_id: string;

  // Core therapeutic settings
  intensity_level: IntensityLevel;
  preferred_approaches: TherapeuticApproach[];
  conversation_style: ConversationStyle;

  // Therapeutic goals and focus areas
  therapeutic_goals: string[];
  primary_concerns: string[];

  // Character and narrative customization
  character_name: string;
  preferred_setting: PreferredSetting;

  // Content preferences
  comfort_topics: string[];
  trigger_topics: string[];
  avoid_topics: string[];

  // Session preferences
  session_duration_preference: number; // in minutes
  reminder_frequency: 'daily' | 'weekly' | 'monthly' | 'never';

  // Advanced preferences
  crisis_contact_info?: {
    emergency_contact: string;
    therapist_contact?: string;
    preferred_crisis_resources: string[];
  };

  // Metadata
  created_at: string;
  updated_at: string;
  version: number;
}

export interface PreferenceValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface TherapeuticApproachInfo {
  id: TherapeuticApproach;
  name: string;
  description: string;
  techniques: string[];
  bestFor: string[];
  intensity: IntensityLevel[];
}

export interface PreferencePreviewContext {
  user_message: string;
  preferences: PlayerPreferences;
  preview_response: string;
  adaptations_applied: string[];
}

// Predefined therapeutic goals
export const THERAPEUTIC_GOALS = [
  'anxiety_reduction',
  'stress_management',
  'confidence_building',
  'emotional_processing',
  'mindfulness_development',
  'body_awareness',
  'relationship_skills',
  'coping_strategies',
  'self_compassion',
  'trauma_recovery',
  'grief_processing',
  'anger_management',
  'sleep_improvement',
  'communication_skills',
  'boundary_setting'
] as const;

export type TherapeuticGoal = typeof THERAPEUTIC_GOALS[number];

// Predefined comfort topics
export const COMFORT_TOPICS = [
  'nature',
  'creativity',
  'music',
  'art',
  'reading',
  'meditation',
  'breathing_exercises',
  'movement',
  'animals',
  'spirituality',
  'personal_growth',
  'achievement',
  'family',
  'friendship',
  'hobbies',
  'travel',
  'learning'
] as const;

export type ComfortTopic = typeof COMFORT_TOPICS[number];

// Therapeutic approach information
export const THERAPEUTIC_APPROACHES_INFO: Record<TherapeuticApproach, TherapeuticApproachInfo> = {
  [TherapeuticApproach.CBT]: {
    id: TherapeuticApproach.CBT,
    name: 'Cognitive Behavioral Therapy',
    description: 'Focuses on identifying and changing negative thought patterns and behaviors',
    techniques: ['Thought challenging', 'Behavioral experiments', 'Problem-solving'],
    bestFor: ['Anxiety', 'Depression', 'Phobias', 'OCD'],
    intensity: [IntensityLevel.MEDIUM, IntensityLevel.HIGH]
  },
  [TherapeuticApproach.MINDFULNESS]: {
    id: TherapeuticApproach.MINDFULNESS,
    name: 'Mindfulness-Based Therapy',
    description: 'Emphasizes present-moment awareness and acceptance',
    techniques: ['Meditation', 'Body scanning', 'Mindful breathing'],
    bestFor: ['Stress', 'Anxiety', 'Chronic pain', 'Depression'],
    intensity: [IntensityLevel.LOW, IntensityLevel.MEDIUM]
  },
  [TherapeuticApproach.NARRATIVE]: {
    id: TherapeuticApproach.NARRATIVE,
    name: 'Narrative Therapy',
    description: 'Uses storytelling to help reframe life experiences and identity',
    techniques: ['Story reconstruction', 'Externalization', 'Unique outcomes'],
    bestFor: ['Identity issues', 'Trauma', 'Life transitions'],
    intensity: [IntensityLevel.MEDIUM, IntensityLevel.HIGH]
  },
  [TherapeuticApproach.SOMATIC]: {
    id: TherapeuticApproach.SOMATIC,
    name: 'Somatic Therapy',
    description: 'Focuses on the connection between mind and body',
    techniques: ['Body awareness', 'Breathing work', 'Movement'],
    bestFor: ['Trauma', 'Anxiety', 'Chronic stress', 'Body image'],
    intensity: [IntensityLevel.LOW, IntensityLevel.MEDIUM]
  },
  [TherapeuticApproach.HUMANISTIC]: {
    id: TherapeuticApproach.HUMANISTIC,
    name: 'Humanistic Therapy',
    description: 'Emphasizes personal growth and self-actualization',
    techniques: ['Active listening', 'Empathy', 'Unconditional positive regard'],
    bestFor: ['Self-esteem', 'Personal growth', 'Relationship issues'],
    intensity: [IntensityLevel.LOW, IntensityLevel.MEDIUM]
  },
  [TherapeuticApproach.PSYCHODYNAMIC]: {
    id: TherapeuticApproach.PSYCHODYNAMIC,
    name: 'Psychodynamic Therapy',
    description: 'Explores unconscious thoughts and past experiences',
    techniques: ['Free association', 'Dream analysis', 'Transference'],
    bestFor: ['Deep-rooted issues', 'Relationship patterns', 'Self-understanding'],
    intensity: [IntensityLevel.MEDIUM, IntensityLevel.HIGH]
  },
  [TherapeuticApproach.ACCEPTANCE_COMMITMENT]: {
    id: TherapeuticApproach.ACCEPTANCE_COMMITMENT,
    name: 'Acceptance & Commitment Therapy',
    description: 'Focuses on accepting difficult thoughts and committing to values-based action',
    techniques: ['Values clarification', 'Mindfulness', 'Behavioral activation'],
    bestFor: ['Chronic conditions', 'Values conflicts', 'Avoidance behaviors'],
    intensity: [IntensityLevel.MEDIUM, IntensityLevel.HIGH]
  },
  [TherapeuticApproach.DIALECTICAL_BEHAVIOR]: {
    id: TherapeuticApproach.DIALECTICAL_BEHAVIOR,
    name: 'Dialectical Behavior Therapy',
    description: 'Combines CBT with mindfulness and distress tolerance skills',
    techniques: ['Distress tolerance', 'Emotion regulation', 'Interpersonal skills'],
    bestFor: ['Emotional dysregulation', 'Self-harm', 'Relationship difficulties'],
    intensity: [IntensityLevel.HIGH]
  }
};

// Setting descriptions
export const SETTING_DESCRIPTIONS: Record<PreferredSetting, string> = {
  [PreferredSetting.PEACEFUL_FOREST]: 'A serene woodland with gentle streams and dappled sunlight',
  [PreferredSetting.MOUNTAIN_RETREAT]: 'A tranquil mountain sanctuary with expansive views',
  [PreferredSetting.OCEAN_SANCTUARY]: 'A calming coastal space with rhythmic waves',
  [PreferredSetting.URBAN_GARDEN]: 'A peaceful garden oasis in the heart of the city',
  [PreferredSetting.COZY_LIBRARY]: 'A warm, book-filled space perfect for reflection',
  [PreferredSetting.STARLIT_MEADOW]: 'An open meadow under a canopy of stars',
  [PreferredSetting.QUIET_GARDEN]: 'A intimate garden space for gentle contemplation',
  [PreferredSetting.FOREST_CLEARING]: 'A bright clearing surrounded by protective trees'
};

// Intensity level descriptions
export const INTENSITY_DESCRIPTIONS: Record<IntensityLevel, string> = {
  [IntensityLevel.LOW]: 'Gentle guidance with minimal therapeutic intervention. Focus on comfort and gradual progress.',
  [IntensityLevel.MEDIUM]: 'Balanced therapeutic approach with moderate intervention and structured support.',
  [IntensityLevel.HIGH]: 'Intensive therapeutic work with frequent interventions and deep exploration.'
};

// Conversation style descriptions
export const CONVERSATION_STYLE_DESCRIPTIONS: Record<ConversationStyle, string> = {
  [ConversationStyle.GENTLE]: 'Soft, nurturing approach with emphasis on comfort and safety',
  [ConversationStyle.DIRECT]: 'Clear, straightforward communication with honest feedback',
  [ConversationStyle.EXPLORATORY]: 'Curious, open-ended approach encouraging discovery',
  [ConversationStyle.SUPPORTIVE]: 'Encouraging, validating approach with positive reinforcement'
};

// Default preferences for new users
export const DEFAULT_PREFERENCES: Omit<PlayerPreferences, 'player_id' | 'created_at' | 'updated_at'> = {
  intensity_level: IntensityLevel.MEDIUM,
  preferred_approaches: [TherapeuticApproach.MINDFULNESS, TherapeuticApproach.CBT],
  conversation_style: ConversationStyle.SUPPORTIVE,
  therapeutic_goals: ['stress_management', 'emotional_processing'],
  primary_concerns: [],
  character_name: 'Alex',
  preferred_setting: PreferredSetting.PEACEFUL_FOREST,
  comfort_topics: ['nature', 'personal_growth'],
  trigger_topics: [],
  avoid_topics: [],
  session_duration_preference: 30,
  reminder_frequency: 'weekly',
  version: 1
};
