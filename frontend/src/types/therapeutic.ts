/**
 * TypeScript definitions for TTA Therapeutic Gaming System
 *
 * These types correspond to the API models from our backend system
 * and provide type safety for the frontend application.
 */

// User and Authentication Types
export interface UserAccount {
  id: string;
  username: string;
  email: string;
  therapeuticPreferences: TherapeuticPreferences;
  privacySettings: PrivacySettings;
  createdAt: string;
  lastLogin?: string;
  isActive: boolean;
  characters?: string[];
  progressSummary?: ProgressSummary;
}

export interface TherapeuticPreferences {
  primaryGoals: string[];
  preferredInteractionStyle: 'supportive' | 'challenging' | 'neutral';
  comfortWithChallenge: 'low' | 'moderate' | 'high';
  sessionFrequency: string;
  focusAreas: string[];
  intensityPreference: 'low' | 'moderate' | 'high';
  sessionLengthPreference: string;
}

export interface PrivacySettings {
  shareProgressWithTherapist: boolean;
  anonymousDataContribution: boolean;
  marketingCommunications: boolean;
  dataSharing: 'minimal' | 'moderate' | 'full';
  progressVisibility: 'private' | 'therapist' | 'public';
}

// Character Types
export interface Character {
  characterId: string;
  playerId: string;
  name: string;
  appearance: CharacterAppearance;
  background: CharacterBackground;
  therapeuticProfile: TherapeuticProfile;
  createdAt: string;
  lastActive: string;
  isActive: boolean;
}

export interface CharacterAppearance {
  ageRange: string;
  genderIdentity: string;
  physicalDescription: string;
  clothingStyle: string;
  distinctiveFeatures: string[];
  avatarImageUrl?: string;
}

export interface CharacterBackground {
  name: string;
  backstory: string;
  personalityTraits: string[];
  coreValues: string[];
  fearsAndAnxieties: string[];
  strengthsAndSkills: string[];
  lifeGoals: string[];
  relationships?: Record<string, any>;
}

export interface TherapeuticProfile {
  primaryTherapeuticGoals: string[];
  therapeuticReadinessLevel: number;
  preferredCopingStrategies: string[];
  triggerTopics: string[];
  comfortZones: string[];
  growthAreas: string[];
}

// World Types
export interface WorldSummary {
  worldId: string;
  name: string;
  description: string;
  therapeuticThemes: string[];
  therapeuticApproaches: string[];
  difficultyLevel: string;
  estimatedDurationMinutes: number;
  compatibilityScore?: number;
  previewImage?: string;
  tags: string[];
  playerCount: number;
  averageRating: number;
  isFeatured: boolean;
  createdAt: string;
}

export interface WorldDetails extends WorldSummary {
  longDescription: string;
  settingDescription: string;
  keyCharacters: string[];
  mainStorylines: string[];
  therapeuticTechniquesUsed: string[];
  prerequisites: string[];
  recommendedTherapeuticReadiness: number;
  contentWarnings: string[];
  availableParameters: string[];
  defaultParameters: Record<string, any>;
  creatorNotes: string;
  therapeuticGoalsAddressed: string[];
  successMetrics: string[];
  completionRate: number;
  averageSessionCount: number;
  therapeuticEffectivenessScore: number;
  updatedAt: string;
}

export interface WorldCustomization {
  difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
  therapeuticIntensity: 'low' | 'moderate' | 'high';
  narrativeStyle: 'supportive' | 'challenging' | 'neutral';
  sessionLength: '15_minutes' | '30_minutes' | '45_minutes' | '60_minutes';
  narrativePace: 'slow' | 'relaxed' | 'moderate' | 'fast';
  interactionFrequency: 'low' | 'moderate' | 'high';
  challengeLevel: 'minimal' | 'gradual' | 'moderate' | 'intensive';
  focusAreas: string[];
  avoidTopics: string[];
  sessionLengthPreference: string;
}

// Session Types
export interface TherapeuticSession {
  sessionId: string;
  characterId: string;
  worldId: string;
  status: 'active' | 'paused' | 'completed';
  therapeuticSettings: SessionSettings;
  progress: SessionProgress;
  createdAt: string;
  updatedAt: string;
  lastActiveAt?: string;
}

export interface SessionSettings {
  sessionType: 'exploration' | 'challenge' | 'reflection' | 'practice';
  therapeuticFocus: string[];
  intensityLevel: 'low' | 'moderate' | 'high';
  durationMinutes: number;
  aiGuidanceLevel: 'minimal' | 'supportive' | 'intensive';
  realTimeFeedback: boolean;
  progressTracking: boolean;
}

export interface SessionProgress {
  currentMilestones: Milestone[];
  completedGoals: string[];
  sessionDuration: number;
  interactionCount: number;
  therapeuticMetrics: TherapeuticMetrics;
}

export interface Milestone {
  id: string;
  name: string;
  description: string;
  therapeuticSignificance: string;
  completedAt?: string;
  progress: number; // 0-100
}

export interface TherapeuticMetrics {
  anxietyLevel: number;
  confidenceLevel: number;
  engagementScore: number;
  progressTowardsGoals: number;
  socialInteractionQuality: number;
  copingSkillsUtilization: number;
}

// Progress and Export Types
export interface ProgressSummary {
  overallProgress: number;
  completedSessions: number;
  totalSessionTime: number;
  achievedMilestones: number;
  therapeuticGoalsProgress: Record<string, number>;
  recentAchievements: Achievement[];
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  therapeuticValue: string;
  earnedAt: string;
  category: 'social' | 'emotional' | 'cognitive' | 'behavioral';
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
  mfaRequired?: boolean;
  userInfo: UserAccount;
}

// Chat and WebSocket Types
export interface ChatMessage {
  id: string;
  sessionId: string;
  sender: 'user' | 'character' | 'system';
  content: string;
  timestamp: string;
  therapeuticContext?: TherapeuticContext;
  messageType: 'text' | 'milestone' | 'crisis_alert' | 'system_notification';
}

export interface TherapeuticContext {
  currentGoal?: string;
  emotionalState?: string;
  triggerDetected?: boolean;
  supportNeeded?: boolean;
  milestoneProgress?: number;
}

// Service Health Types
export interface ServiceHealth {
  timestamp: string;
  usingMocks: boolean;
  overallStatus: 'healthy' | 'degraded' | 'unhealthy';
  services: Record<string, ServiceStatus>;
  summary: HealthSummary;
}

export interface ServiceStatus {
  service: string;
  status: 'healthy' | 'degraded' | 'unhealthy' | 'mock';
  lastCheck?: string;
  lastError?: string;
  connectionAttempts: number;
  successfulOperations: number;
  failedOperations: number;
  successRate: number;
  averageResponseTimeMs: number;
  uptimeSeconds: number;
}

export interface HealthSummary {
  totalServices: number;
  healthyServices: number;
  degradedServices: number;
  healthPercentage: number;
}

// Export Data Types
export interface CharacterExport {
  character: Character;
  progressHistory: ProgressSummary;
  achievements: Achievement[];
  sessionHistory: TherapeuticSession[];
  exportMetadata: ExportMetadata;
}

export interface WorldExport {
  world: WorldDetails;
  customizations: WorldCustomization[];
  compatibilityAnalysis: CompatibilityAnalysis[];
  sessionOutcomes: SessionOutcome[];
  exportMetadata: ExportMetadata;
}

export interface SessionExport {
  session: TherapeuticSession;
  chatHistory: ChatMessage[];
  progressReports: ProgressReport[];
  therapeuticOutcomes: TherapeuticOutcome[];
  exportMetadata: ExportMetadata;
}

export interface ExportMetadata {
  exportedAt: string;
  exportedBy: string;
  format: 'json' | 'pdf' | 'csv';
  version: string;
  privacyLevel: 'full' | 'anonymized' | 'summary';
}

export interface CompatibilityAnalysis {
  characterId: string;
  worldId: string;
  compatibilityScore: number;
  strengths: string[];
  concerns: string[];
  recommendations: string[];
  therapeuticAlignment: number;
}

export interface SessionOutcome {
  sessionId: string;
  therapeuticEffectiveness: number;
  goalProgress: Record<string, number>;
  skillsDeveloped: string[];
  challengesEncountered: string[];
  recommendedNextSteps: string[];
}

export interface ProgressReport {
  reportDate: string;
  overallProgress: number;
  goalSpecificProgress: Record<string, number>;
  therapeuticInsights: string[];
  recommendedAdjustments: string[];
}

export interface TherapeuticOutcome {
  outcomeType: 'milestone' | 'skill_development' | 'goal_achievement' | 'crisis_resolution';
  description: string;
  therapeuticValue: string;
  measuredImpact: number;
  timestamp: string;
}
