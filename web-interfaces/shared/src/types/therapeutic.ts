// Core therapeutic types for the TTA platform
export interface TherapeuticSession {
  id: string;
  patientId: string;
  startTime: Date;
  endTime?: Date;
  status: 'active' | 'paused' | 'completed' | 'crisis';
  therapeuticFramework: TherapeuticFramework;
  progressMetrics: ProgressMetrics;
  interventions: TherapeuticIntervention[];
}

export interface TherapeuticFramework {
  type: 'CBT' | 'DBT' | 'Mindfulness' | 'ACT' | 'Narrative';
  techniques: string[];
  goals: TherapeuticGoal[];
  adaptiveDifficulty: AdaptiveDifficulty;
}

export interface TherapeuticGoal {
  id: string;
  description: string;
  category: 'emotional_regulation' | 'coping_skills' | 'social_interaction' | 'self_awareness';
  targetMetric: string;
  currentProgress: number; // 0-100
  milestones: Milestone[];
}

export interface Milestone {
  id: string;
  description: string;
  achieved: boolean;
  achievedAt?: Date;
  evidence?: string[];
}

export interface ProgressMetrics {
  emotionalState: EmotionalState;
  engagementLevel: number; // 0-100
  therapeuticCompliance: number; // 0-100
  skillAcquisition: SkillProgress[];
  riskAssessment: RiskAssessment;
}

export interface EmotionalState {
  valence: number; // -100 to 100 (negative to positive)
  arousal: number; // 0-100 (calm to excited)
  dominance: number; // 0-100 (submissive to dominant)
  timestamp: Date;
  confidence: number; // 0-100
}

export interface SkillProgress {
  skillId: string;
  skillName: string;
  proficiencyLevel: number; // 0-100
  practiceCount: number;
  lastPracticed: Date;
  improvementRate: number;
}

export interface RiskAssessment {
  overallRisk: 'low' | 'medium' | 'high' | 'crisis';
  factors: RiskFactor[];
  lastAssessed: Date;
  interventionsTriggered: string[];
}

export interface RiskFactor {
  type: 'suicidal_ideation' | 'self_harm' | 'substance_abuse' | 'social_isolation' | 'emotional_dysregulation';
  severity: number; // 0-100
  indicators: string[];
  mitigationStrategies: string[];
}

export interface TherapeuticIntervention {
  id: string;
  type: 'crisis_support' | 'skill_building' | 'cognitive_restructuring' | 'mindfulness_exercise' | 'narrative_therapy';
  trigger: InterventionTrigger;
  content: InterventionContent;
  effectiveness: number; // 0-100
  timestamp: Date;
}

export interface InterventionTrigger {
  type: 'automatic' | 'manual' | 'scheduled';
  conditions: TriggerCondition[];
  priority: 'low' | 'medium' | 'high' | 'emergency';
}

export interface TriggerCondition {
  metric: string;
  operator: '>' | '<' | '=' | '>=' | '<=';
  threshold: number;
  duration?: number; // seconds
}

export interface InterventionContent {
  title: string;
  description: string;
  instructions: string[];
  resources: Resource[];
  estimatedDuration: number; // minutes
  accessibility: AccessibilityFeatures;
}

export interface Resource {
  type: 'text' | 'audio' | 'video' | 'interactive' | 'external_link';
  url: string;
  title: string;
  description?: string;
  accessibility?: AccessibilityFeatures;
}

export interface AccessibilityFeatures {
  screenReaderCompatible: boolean;
  highContrast: boolean;
  largeText: boolean;
  audioDescription?: boolean;
  closedCaptions?: boolean;
  keyboardNavigation: boolean;
}

export interface AdaptiveDifficulty {
  currentLevel: number; // 1-10
  adjustmentRate: number; // How quickly difficulty adapts
  factors: DifficultyFactor[];
  lastAdjustment: Date;
}

export interface DifficultyFactor {
  name: string;
  weight: number; // 0-1
  currentValue: number;
  targetRange: [number, number];
}

// Patient interface specific types
export interface PatientProfile {
  id: string;
  demographics: Demographics;
  therapeuticHistory: TherapeuticHistory;
  preferences: PatientPreferences;
  consentStatus: ConsentStatus;
  emergencyContacts: EmergencyContact[];
}

export interface Demographics {
  age: number;
  gender?: string;
  location?: string;
  timezone: string;
  language: string;
  culturalBackground?: string[];
}

export interface TherapeuticHistory {
  previousSessions: number;
  totalEngagementTime: number; // minutes
  completedPrograms: string[];
  currentPrograms: string[];
  clinicalNotes?: ClinicalNote[];
}

export interface ClinicalNote {
  id: string;
  authorId: string;
  authorRole: 'therapist' | 'psychiatrist' | 'counselor' | 'system';
  content: string;
  timestamp: Date;
  confidentiality: 'public' | 'clinical_only' | 'restricted';
}

export interface PatientPreferences {
  therapeuticFrameworks: string[];
  communicationStyle: 'formal' | 'casual' | 'supportive' | 'direct';
  sessionLength: number; // minutes
  reminderFrequency: 'none' | 'daily' | 'weekly' | 'custom';
  accessibilityNeeds: AccessibilityFeatures;
  crisisContactPreference: 'immediate' | 'delayed' | 'family_first';
}

export interface ConsentStatus {
  dataCollection: boolean;
  therapeuticInterventions: boolean;
  emergencyContact: boolean;
  researchParticipation: boolean;
  dataSharing: boolean;
  lastUpdated: Date;
}

export interface EmergencyContact {
  id: string;
  name: string;
  relationship: string;
  phone: string;
  email?: string;
  priority: number; // 1 = primary
  availability: string; // e.g., "24/7", "9am-5pm weekdays"
}

// Clinical dashboard types
export interface ClinicalDashboardData {
  patients: PatientSummary[];
  alerts: ClinicalAlert[];
  metrics: ClinicalMetrics;
  schedule: ClinicalSchedule;
}

export interface PatientSummary {
  patientId: string;
  name: string;
  lastSession: Date;
  riskLevel: 'low' | 'medium' | 'high' | 'crisis';
  progressTrend: 'improving' | 'stable' | 'declining';
  nextAppointment?: Date;
  activeInterventions: number;
}

export interface ClinicalAlert {
  id: string;
  patientId: string;
  type: 'crisis' | 'missed_session' | 'progress_concern' | 'technical_issue';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: Date;
  acknowledged: boolean;
  resolvedAt?: Date;
}

export interface ClinicalMetrics {
  totalPatients: number;
  activePatients: number;
  averageEngagement: number;
  interventionEffectiveness: number;
  crisisInterventions: number;
  patientSatisfaction: number;
}

export interface ClinicalSchedule {
  appointments: Appointment[];
  availability: AvailabilitySlot[];
}

export interface Appointment {
  id: string;
  patientId: string;
  patientName: string;
  startTime: Date;
  duration: number; // minutes
  type: 'initial' | 'follow_up' | 'crisis' | 'group';
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled';
}

export interface AvailabilitySlot {
  startTime: Date;
  endTime: Date;
  available: boolean;
  reason?: string;
}
