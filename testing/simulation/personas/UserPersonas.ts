// Logseq: [[TTA.dev/Testing/Simulation/Personas/Userpersonas]]
/**
 * User Personas for TTA Simulation Testing
 *
 * Defines diverse user personas with varying play styles, session lengths,
 * and engagement patterns to comprehensively test TTA's entertainment value.
 */

export enum PersonaType {
  CASUAL_EXPLORER = 'casual_explorer',
  STORY_ENTHUSIAST = 'story_enthusiast',
  WORLD_BUILDER = 'world_builder',
  MARATHON_PLAYER = 'marathon_player',
  SOCIAL_CONNECTOR = 'social_connector',
  ACHIEVEMENT_HUNTER = 'achievement_hunter',
  THERAPEUTIC_SEEKER = 'therapeutic_seeker',
  SKEPTICAL_NEWCOMER = 'skeptical_newcomer'
}

export enum DecisionMakingStyle {
  IMPULSIVE = 'impulsive',
  ANALYTICAL = 'analytical',
  INTUITIVE = 'intuitive',
  CAUTIOUS = 'cautious',
  STRATEGIC = 'strategic',
  EMOTIONAL = 'emotional'
}

export enum InteractionStyle {
  ACTIVE = 'active',
  PASSIVE = 'passive',
  EXPLORATORY = 'exploratory',
  GOAL_ORIENTED = 'goal_oriented',
  SOCIAL = 'social',
  CONTEMPLATIVE = 'contemplative'
}

export interface SessionPreferences {
  preferredDuration: number; // minutes
  maxDuration: number; // minutes
  minDuration: number; // minutes
  breakFrequency: number; // minutes between breaks
  preferredTimeOfDay: ('morning' | 'afternoon' | 'evening' | 'night')[];
  sessionFrequency: 'daily' | 'several_times_week' | 'weekly' | 'occasional';
}

export interface EngagementTriggers {
  narrativeDepth: number; // 0-1 scale
  characterDevelopment: number;
  worldComplexity: number;
  socialInteraction: number;
  achievementProgression: number;
  mysteryAndDiscovery: number;
  emotionalResonance: number;
  intellectualChallenge: number;
}

export interface TherapeuticNeeds {
  stressReduction: number; // 0-1 scale of need
  anxietyManagement: number;
  depressionSupport: number;
  socialSkillsDevelopment: number;
  emotionalRegulation: number;
  selfEsteemBuilding: number;
  copingStrategies: number;
  mindfulnessTraining: number;
  awarenessLevel: 'unconscious' | 'subconscious' | 'conscious'; // How aware they are of seeking therapy
}

export interface BehavioralPatterns {
  decisionMakingStyle: DecisionMakingStyle;
  interactionStyle: InteractionStyle;
  riskTolerance: number; // 0-1 scale
  patienceLevel: number; // 0-1 scale
  curiosityLevel: number; // 0-1 scale
  socialComfort: number; // 0-1 scale
  complexityTolerance: number; // 0-1 scale
  attentionSpan: number; // minutes before needing stimulation change
}

export interface SuccessCriteria {
  minimumEngagementTime: number; // minutes
  requiredImmersionLevel: number; // 0-1 scale
  therapeuticBenefitThreshold: number; // 0-1 scale
  returnProbability: number; // 0-1 scale for likelihood to return
  recommendationLikelihood: number; // 0-1 scale for likelihood to recommend
}

export class UserPersona {
  public id: string;
  public type: PersonaType;
  public name: string = '';
  public description: string = '';
  public sessionPreferences: SessionPreferences = {} as SessionPreferences;
  public engagementTriggers: EngagementTriggers = {} as EngagementTriggers;
  public therapeuticNeeds: TherapeuticNeeds = {} as TherapeuticNeeds;
  public behavioralPatterns: BehavioralPatterns = {} as BehavioralPatterns;
  public successCriteria: SuccessCriteria = {} as SuccessCriteria;

  constructor(type: PersonaType, id: string) {
    this.type = type;
    this.id = id;
    this.initializePersona();
  }

  private initializePersona(): void {
    switch (this.type) {
      case PersonaType.CASUAL_EXPLORER:
        this.initializeCasualExplorer();
        break;
      case PersonaType.STORY_ENTHUSIAST:
        this.initializeStoryEnthusiast();
        break;
      case PersonaType.WORLD_BUILDER:
        this.initializeWorldBuilder();
        break;
      case PersonaType.MARATHON_PLAYER:
        this.initializeMarathonPlayer();
        break;
      case PersonaType.SOCIAL_CONNECTOR:
        this.initializeSocialConnector();
        break;
      case PersonaType.ACHIEVEMENT_HUNTER:
        this.initializeAchievementHunter();
        break;
      case PersonaType.THERAPEUTIC_SEEKER:
        this.initializeTherapeuticSeeker();
        break;
      case PersonaType.SKEPTICAL_NEWCOMER:
        this.initializeSkepticalNewcomer();
        break;
    }
  }

  private initializeCasualExplorer(): void {
    this.name = "Casual Explorer";
    this.description = "Enjoys light exploration and simple interactions. Prefers short, relaxing sessions without complex commitments.";

    this.sessionPreferences = {
      preferredDuration: 20,
      maxDuration: 30,
      minDuration: 15,
      breakFrequency: 15,
      preferredTimeOfDay: ['evening'],
      sessionFrequency: 'several_times_week'
    };

    this.engagementTriggers = {
      narrativeDepth: 0.3,
      characterDevelopment: 0.4,
      worldComplexity: 0.2,
      socialInteraction: 0.5,
      achievementProgression: 0.3,
      mysteryAndDiscovery: 0.7,
      emotionalResonance: 0.6,
      intellectualChallenge: 0.2
    };

    this.therapeuticNeeds = {
      stressReduction: 0.8,
      anxietyManagement: 0.6,
      depressionSupport: 0.3,
      socialSkillsDevelopment: 0.4,
      emotionalRegulation: 0.5,
      selfEsteemBuilding: 0.4,
      copingStrategies: 0.6,
      mindfulnessTraining: 0.7,
      awarenessLevel: 'unconscious'
    };

    this.behavioralPatterns = {
      decisionMakingStyle: DecisionMakingStyle.INTUITIVE,
      interactionStyle: InteractionStyle.EXPLORATORY,
      riskTolerance: 0.3,
      patienceLevel: 0.4,
      curiosityLevel: 0.8,
      socialComfort: 0.6,
      complexityTolerance: 0.3,
      attentionSpan: 10
    };

    this.successCriteria = {
      minimumEngagementTime: 15,
      requiredImmersionLevel: 0.6,
      therapeuticBenefitThreshold: 0.5,
      returnProbability: 0.7,
      recommendationLikelihood: 0.6
    };
  }

  private initializeStoryEnthusiast(): void {
    this.name = "Story Enthusiast";
    this.description = "Deeply invested in narrative quality and character development. Seeks rich, emotionally engaging stories.";

    this.sessionPreferences = {
      preferredDuration: 60,
      maxDuration: 90,
      minDuration: 45,
      breakFrequency: 30,
      preferredTimeOfDay: ['evening', 'night'],
      sessionFrequency: 'several_times_week'
    };

    this.engagementTriggers = {
      narrativeDepth: 0.9,
      characterDevelopment: 0.9,
      worldComplexity: 0.6,
      socialInteraction: 0.7,
      achievementProgression: 0.4,
      mysteryAndDiscovery: 0.8,
      emotionalResonance: 0.9,
      intellectualChallenge: 0.6
    };

    this.therapeuticNeeds = {
      stressReduction: 0.5,
      anxietyManagement: 0.4,
      depressionSupport: 0.6,
      socialSkillsDevelopment: 0.6,
      emotionalRegulation: 0.7,
      selfEsteemBuilding: 0.6,
      copingStrategies: 0.5,
      mindfulnessTraining: 0.4,
      awarenessLevel: 'subconscious'
    };

    this.behavioralPatterns = {
      decisionMakingStyle: DecisionMakingStyle.EMOTIONAL,
      interactionStyle: InteractionStyle.CONTEMPLATIVE,
      riskTolerance: 0.6,
      patienceLevel: 0.8,
      curiosityLevel: 0.9,
      socialComfort: 0.7,
      complexityTolerance: 0.7,
      attentionSpan: 25
    };

    this.successCriteria = {
      minimumEngagementTime: 45,
      requiredImmersionLevel: 0.8,
      therapeuticBenefitThreshold: 0.6,
      returnProbability: 0.9,
      recommendationLikelihood: 0.8
    };
  }

  private initializeWorldBuilder(): void {
    this.name = "World Builder";
    this.description = "Fascinated by complex systems, economics, politics, and world mechanics. Enjoys deep, systematic exploration.";

    this.sessionPreferences = {
      preferredDuration: 120,
      maxDuration: 180,
      minDuration: 60,
      breakFrequency: 45,
      preferredTimeOfDay: ['afternoon', 'evening'],
      sessionFrequency: 'several_times_week'
    };

    this.engagementTriggers = {
      narrativeDepth: 0.6,
      characterDevelopment: 0.5,
      worldComplexity: 0.9,
      socialInteraction: 0.6,
      achievementProgression: 0.7,
      mysteryAndDiscovery: 0.8,
      emotionalResonance: 0.4,
      intellectualChallenge: 0.9
    };

    this.therapeuticNeeds = {
      stressReduction: 0.4,
      anxietyManagement: 0.5,
      depressionSupport: 0.3,
      socialSkillsDevelopment: 0.5,
      emotionalRegulation: 0.4,
      selfEsteemBuilding: 0.6,
      copingStrategies: 0.5,
      mindfulnessTraining: 0.3,
      awarenessLevel: 'unconscious'
    };

    this.behavioralPatterns = {
      decisionMakingStyle: DecisionMakingStyle.ANALYTICAL,
      interactionStyle: InteractionStyle.GOAL_ORIENTED,
      riskTolerance: 0.7,
      patienceLevel: 0.9,
      curiosityLevel: 0.9,
      socialComfort: 0.5,
      complexityTolerance: 0.9,
      attentionSpan: 45
    };

    this.successCriteria = {
      minimumEngagementTime: 90,
      requiredImmersionLevel: 0.8,
      therapeuticBenefitThreshold: 0.5,
      returnProbability: 0.8,
      recommendationLikelihood: 0.7
    };
  }

  private initializeMarathonPlayer(): void {
    this.name = "Marathon Player";
    this.description = "Capable of very long sessions with sustained engagement. Seeks deep, complex narratives and character progression.";

    this.sessionPreferences = {
      preferredDuration: 240,
      maxDuration: 360,
      minDuration: 180,
      breakFrequency: 60,
      preferredTimeOfDay: ['afternoon', 'evening', 'night'],
      sessionFrequency: 'weekly'
    };

    this.engagementTriggers = {
      narrativeDepth: 0.8,
      characterDevelopment: 0.8,
      worldComplexity: 0.8,
      socialInteraction: 0.7,
      achievementProgression: 0.8,
      mysteryAndDiscovery: 0.9,
      emotionalResonance: 0.7,
      intellectualChallenge: 0.8
    };

    this.therapeuticNeeds = {
      stressReduction: 0.6,
      anxietyManagement: 0.5,
      depressionSupport: 0.4,
      socialSkillsDevelopment: 0.6,
      emotionalRegulation: 0.6,
      selfEsteemBuilding: 0.7,
      copingStrategies: 0.6,
      mindfulnessTraining: 0.5,
      awarenessLevel: 'subconscious'
    };

    this.behavioralPatterns = {
      decisionMakingStyle: DecisionMakingStyle.STRATEGIC,
      interactionStyle: InteractionStyle.ACTIVE,
      riskTolerance: 0.8,
      patienceLevel: 0.9,
      curiosityLevel: 0.9,
      socialComfort: 0.7,
      complexityTolerance: 0.9,
      attentionSpan: 60
    };

    this.successCriteria = {
      minimumEngagementTime: 180,
      requiredImmersionLevel: 0.9,
      therapeuticBenefitThreshold: 0.7,
      returnProbability: 0.9,
      recommendationLikelihood: 0.8
    };
  }

  private initializeSocialConnector(): void {
    this.name = "Social Connector";
    this.description = "Focuses on character relationships and social dynamics. Values emotional connections and interpersonal growth.";

    this.sessionPreferences = {
      preferredDuration: 45,
      maxDuration: 75,
      minDuration: 30,
      breakFrequency: 25,
      preferredTimeOfDay: ['afternoon', 'evening'],
      sessionFrequency: 'daily'
    };

    this.engagementTriggers = {
      narrativeDepth: 0.7,
      characterDevelopment: 0.9,
      worldComplexity: 0.4,
      socialInteraction: 0.9,
      achievementProgression: 0.5,
      mysteryAndDiscovery: 0.6,
      emotionalResonance: 0.9,
      intellectualChallenge: 0.4
    };

    this.therapeuticNeeds = {
      stressReduction: 0.6,
      anxietyManagement: 0.7,
      depressionSupport: 0.7,
      socialSkillsDevelopment: 0.9,
      emotionalRegulation: 0.8,
      selfEsteemBuilding: 0.8,
      copingStrategies: 0.7,
      mindfulnessTraining: 0.6,
      awarenessLevel: 'conscious'
    };

    this.behavioralPatterns = {
      decisionMakingStyle: DecisionMakingStyle.EMOTIONAL,
      interactionStyle: InteractionStyle.SOCIAL,
      riskTolerance: 0.5,
      patienceLevel: 0.7,
      curiosityLevel: 0.7,
      socialComfort: 0.9,
      complexityTolerance: 0.5,
      attentionSpan: 20
    };

    this.successCriteria = {
      minimumEngagementTime: 30,
      requiredImmersionLevel: 0.7,
      therapeuticBenefitThreshold: 0.8,
      returnProbability: 0.9,
      recommendationLikelihood: 0.9
    };
  }

  private initializeAchievementHunter(): void {
    this.name = "Achievement Hunter";
    this.description = "Goal-oriented player who enjoys progression systems, accomplishments, and measurable success.";

    this.sessionPreferences = {
      preferredDuration: 90,
      maxDuration: 120,
      minDuration: 60,
      breakFrequency: 30,
      preferredTimeOfDay: ['afternoon', 'evening'],
      sessionFrequency: 'several_times_week'
    };

    this.engagementTriggers = {
      narrativeDepth: 0.5,
      characterDevelopment: 0.6,
      worldComplexity: 0.6,
      socialInteraction: 0.4,
      achievementProgression: 0.9,
      mysteryAndDiscovery: 0.7,
      emotionalResonance: 0.5,
      intellectualChallenge: 0.7
    };

    this.therapeuticNeeds = {
      stressReduction: 0.5,
      anxietyManagement: 0.6,
      depressionSupport: 0.5,
      socialSkillsDevelopment: 0.5,
      emotionalRegulation: 0.6,
      selfEsteemBuilding: 0.8,
      copingStrategies: 0.6,
      mindfulnessTraining: 0.4,
      awarenessLevel: 'unconscious'
    };

    this.behavioralPatterns = {
      decisionMakingStyle: DecisionMakingStyle.STRATEGIC,
      interactionStyle: InteractionStyle.GOAL_ORIENTED,
      riskTolerance: 0.7,
      patienceLevel: 0.6,
      curiosityLevel: 0.7,
      socialComfort: 0.6,
      complexityTolerance: 0.7,
      attentionSpan: 30
    };

    this.successCriteria = {
      minimumEngagementTime: 60,
      requiredImmersionLevel: 0.7,
      therapeuticBenefitThreshold: 0.6,
      returnProbability: 0.8,
      recommendationLikelihood: 0.7
    };
  }

  private initializeTherapeuticSeeker(): void {
    this.name = "Therapeutic Seeker";
    this.description = "Consciously seeking therapeutic benefits through engaging gameplay. Values personal growth and emotional healing.";

    this.sessionPreferences = {
      preferredDuration: 60,
      maxDuration: 90,
      minDuration: 45,
      breakFrequency: 20,
      preferredTimeOfDay: ['morning', 'evening'],
      sessionFrequency: 'daily'
    };

    this.engagementTriggers = {
      narrativeDepth: 0.7,
      characterDevelopment: 0.8,
      worldComplexity: 0.5,
      socialInteraction: 0.7,
      achievementProgression: 0.6,
      mysteryAndDiscovery: 0.6,
      emotionalResonance: 0.9,
      intellectualChallenge: 0.6
    };

    this.therapeuticNeeds = {
      stressReduction: 0.9,
      anxietyManagement: 0.8,
      depressionSupport: 0.8,
      socialSkillsDevelopment: 0.7,
      emotionalRegulation: 0.9,
      selfEsteemBuilding: 0.8,
      copingStrategies: 0.9,
      mindfulnessTraining: 0.8,
      awarenessLevel: 'conscious'
    };

    this.behavioralPatterns = {
      decisionMakingStyle: DecisionMakingStyle.CAUTIOUS,
      interactionStyle: InteractionStyle.CONTEMPLATIVE,
      riskTolerance: 0.4,
      patienceLevel: 0.8,
      curiosityLevel: 0.8,
      socialComfort: 0.6,
      complexityTolerance: 0.6,
      attentionSpan: 25
    };

    this.successCriteria = {
      minimumEngagementTime: 45,
      requiredImmersionLevel: 0.8,
      therapeuticBenefitThreshold: 0.9,
      returnProbability: 0.9,
      recommendationLikelihood: 0.9
    };
  }

  private initializeSkepticalNewcomer(): void {
    this.name = "Skeptical Newcomer";
    this.description = "New to the platform and cautious about its value. Needs convincing through immediate, obvious benefits.";

    this.sessionPreferences = {
      preferredDuration: 25,
      maxDuration: 45,
      minDuration: 15,
      breakFrequency: 15,
      preferredTimeOfDay: ['afternoon', 'evening'],
      sessionFrequency: 'occasional'
    };

    this.engagementTriggers = {
      narrativeDepth: 0.4,
      characterDevelopment: 0.5,
      worldComplexity: 0.3,
      socialInteraction: 0.4,
      achievementProgression: 0.6,
      mysteryAndDiscovery: 0.7,
      emotionalResonance: 0.5,
      intellectualChallenge: 0.5
    };

    this.therapeuticNeeds = {
      stressReduction: 0.7,
      anxietyManagement: 0.6,
      depressionSupport: 0.5,
      socialSkillsDevelopment: 0.5,
      emotionalRegulation: 0.6,
      selfEsteemBuilding: 0.6,
      copingStrategies: 0.6,
      mindfulnessTraining: 0.5,
      awarenessLevel: 'unconscious'
    };

    this.behavioralPatterns = {
      decisionMakingStyle: DecisionMakingStyle.CAUTIOUS,
      interactionStyle: InteractionStyle.PASSIVE,
      riskTolerance: 0.2,
      patienceLevel: 0.4,
      curiosityLevel: 0.6,
      socialComfort: 0.4,
      complexityTolerance: 0.3,
      attentionSpan: 12
    };

    this.successCriteria = {
      minimumEngagementTime: 15,
      requiredImmersionLevel: 0.6,
      therapeuticBenefitThreshold: 0.5,
      returnProbability: 0.5,
      recommendationLikelihood: 0.4
    };
  }

  /**
   * Generate a behavioral decision based on persona characteristics
   */
  public makeDecision(options: string[], context: any): string {
    // Implementation would use persona characteristics to simulate decision-making
    // This is a simplified version
    const randomIndex = Math.floor(Math.random() * options.length);
    return options[randomIndex];
  }

  /**
   * Calculate engagement level based on current experience
   */
  public calculateEngagement(experience: any): number {
    // Implementation would calculate engagement based on persona triggers and current experience
    return Math.random(); // Simplified for now
  }

  /**
   * Determine if persona would continue session
   */
  public shouldContinueSession(currentDuration: number, engagement: number): boolean {
    if (currentDuration >= this.sessionPreferences.maxDuration) return false;
    if (currentDuration < this.sessionPreferences.minDuration) return true;

    // Factor in engagement level and persona characteristics
    const continueThreshold = 0.5 + (engagement * 0.3) + (this.behavioralPatterns.patienceLevel * 0.2);
    return Math.random() < continueThreshold;
  }
}

export default UserPersona;
