// Logseq: [[TTA.dev/Player_experience/Franchise_worlds/Core/Franchiseworldsystem]]
/**
 * Franchise World System - Core Framework
 *
 * Provides the foundation for creating TTA-compatible adaptations of popular
 * fantasy and science fiction franchises while maintaining therapeutic value
 * and avoiding copyright issues through creative adaptation.
 */

import { WorldDetails, WorldParameters, TherapeuticApproach, DifficultyLevel } from '../types/TTATypes';
import { WorldSystem } from '../../../testing/simulation/world/WorldGenerationTester';

export interface FranchiseWorldConfig {
  franchiseId: string;
  name: string;
  genre: 'fantasy' | 'sci-fi';
  inspirationSource: string; // e.g., "Middle-earth-inspired epic fantasy"

  // Core world systems (8 validated systems)
  worldSystems: {
    cultural: WorldSystemConfig;
    economic: WorldSystemConfig;
    political: WorldSystemConfig;
    environmental: WorldSystemConfig;
    social: WorldSystemConfig;
    historical: WorldSystemConfig;
    technological: WorldSystemConfig;
    religious: WorldSystemConfig;
  };

  // Therapeutic integration
  therapeuticThemes: string[];
  therapeuticApproaches: TherapeuticApproach[];
  therapeuticIntegrationPoints: TherapeuticIntegrationPoint[];

  // Narrative structure
  narrativeFramework: NarrativeFramework;
  characterArchetypes: CharacterArchetype[];
  scenarioTemplates: ScenarioTemplate[];

  // Session support
  sessionLengthSupport: {
    short: SessionConfig; // 15-30 minutes
    medium: SessionConfig; // 30-90 minutes
    long: SessionConfig; // 90+ minutes
  };

  // Legal and ethical
  copyrightCompliance: CopyrightCompliance;
  contentRatings: ContentRating[];
}

export interface WorldSystemConfig {
  complexity: number; // 0-1 scale
  depth: number; // 0-1 scale
  interconnectedness: number; // 0-1 scale with other systems
  therapeuticRelevance: number; // 0-1 scale
  adaptationElements: string[]; // Elements adapted from source material
  originalElements: string[]; // Original TTA elements
}

export interface TherapeuticIntegrationPoint {
  trigger: string; // What triggers this therapeutic moment
  approach: TherapeuticApproach;
  technique: string;
  narrativeIntegration: 'subtle' | 'moderate' | 'explicit';
  playerAgency: 'low' | 'medium' | 'high'; // How much choice player has
  expectedOutcome: string;
}

export interface NarrativeFramework {
  mainArcStructure: string; // e.g., "Hero's Journey", "Political Intrigue"
  branchingPoints: BranchingPoint[];
  therapeuticMilestones: TherapeuticMilestone[];
  adaptationStrategy: string; // How we adapt the source material
}

export interface BranchingPoint {
  pointId: string;
  description: string;
  choices: NarrativeChoice[];
  therapeuticImpact: string;
  convergenceStrategy: string; // How branches reconverge
}

export interface NarrativeChoice {
  choiceId: string;
  text: string;
  therapeuticValue: TherapeuticValue;
  consequences: Consequence[];
  characterDevelopment: string;
}

export interface TherapeuticValue {
  approach: TherapeuticApproach;
  intensity: number; // 0-1 scale
  subtlety: number; // 0-1 scale (higher = more subtle)
  playerReflection: string; // What the player might reflect on
}

export interface Consequence {
  type: 'immediate' | 'delayed' | 'cascading';
  scope: 'personal' | 'interpersonal' | 'world';
  description: string;
  therapeuticRelevance: string;
}

export interface TherapeuticMilestone {
  milestoneId: string;
  description: string;
  requiredProgress: string[];
  therapeuticGoal: string;
  celebrationMechanic: string;
}

export interface CharacterArchetype {
  archetypeId: string;
  name: string;
  inspirationSource: string; // e.g., "Wise mentor archetype"
  role: string;
  personality: PersonalityProfile;
  therapeuticFunction: string;
  interactionPatterns: InteractionPattern[];
  adaptationNotes: string; // How we made it legally distinct
}

export interface PersonalityProfile {
  traits: string[];
  motivations: string[];
  fears: string[];
  growth_arc: string;
  therapeutic_modeling: string; // What therapeutic behavior they model
}

export interface InteractionPattern {
  trigger: string;
  response_style: string;
  therapeutic_technique: string;
  player_impact: string;
}

export interface ScenarioTemplate {
  templateId: string;
  name: string;
  description: string;
  duration: 'short' | 'medium' | 'long';
  therapeuticFocus: string[];
  narrativeElements: string[];
  adaptationSource: string;
  variationPoints: VariationPoint[];
}

export interface VariationPoint {
  pointId: string;
  description: string;
  options: string[];
  therapeuticImpact: string;
}

export interface SessionConfig {
  targetDuration: number; // minutes
  narrativeStructure: string;
  therapeuticIntensity: number; // 0-1 scale
  keyElements: string[];
  exitStrategies: string[]; // How to gracefully end if needed
}

export interface CopyrightCompliance {
  adaptationStrategy: string;
  originalElements: string[];
  legalDistinctions: string[];
  riskAssessment: 'low' | 'medium' | 'high';
  reviewNotes: string;
}

export interface ContentRating {
  system: string; // e.g., "ESRB", "PEGI"
  rating: string;
  contentDescriptors: string[];
  therapeuticSafety: string;
}

/**
 * Core Franchise World System Manager
 */
export class FranchiseWorldSystem {
  private worldConfigs: Map<string, FranchiseWorldConfig> = new Map();
  private activeWorlds: Map<string, FranchiseWorldInstance> = new Map();

  constructor() {
    this.initializeDefaultWorlds();
  }

  /**
   * Register a new franchise world configuration
   */
  registerWorld(config: FranchiseWorldConfig): void {
    this.worldConfigs.set(config.franchiseId, config);
  }

  /**
   * Get all available franchise worlds
   */
  getAvailableWorlds(): FranchiseWorldConfig[] {
    return Array.from(this.worldConfigs.values());
  }

  /**
   * Get worlds by genre
   */
  getWorldsByGenre(genre: 'fantasy' | 'sci-fi'): FranchiseWorldConfig[] {
    return Array.from(this.worldConfigs.values())
      .filter(world => world.genre === genre);
  }

  /**
   * Create a world instance for a player session
   */
  async createWorldInstance(
    franchiseId: string,
    sessionId: string,
    parameters: WorldParameters
  ): Promise<FranchiseWorldInstance> {
    const config = this.worldConfigs.get(franchiseId);
    if (!config) {
      throw new Error(`Franchise world not found: ${franchiseId}`);
    }

    const instance = new FranchiseWorldInstance(config, sessionId, parameters);
    await instance.initialize();

    this.activeWorlds.set(sessionId, instance);
    return instance;
  }

  /**
   * Get an active world instance
   */
  getWorldInstance(sessionId: string): FranchiseWorldInstance | undefined {
    return this.activeWorlds.get(sessionId);
  }

  /**
   * Convert franchise world to TTA WorldDetails format
   */
  toWorldDetails(config: FranchiseWorldConfig): WorldDetails {
    return {
      world_id: config.franchiseId,
      name: config.name,
      description: `${config.inspirationSource} - A therapeutic adventure`,
      long_description: this.generateLongDescription(config),
      therapeutic_themes: config.therapeuticThemes,
      therapeutic_approaches: config.therapeuticApproaches,
      difficulty_level: DifficultyLevel.INTERMEDIATE,
      estimated_duration: { hours: 2 }, // Default 2 hours

      setting_description: this.generateSettingDescription(config),
      key_characters: this.generateKeyCharacters(config),
      main_storylines: this.generateMainStorylines(config),
      therapeutic_techniques_used: this.extractTherapeuticTechniques(config),

      tags: [config.genre, 'franchise-inspired', ...config.therapeuticThemes],
      therapeutic_goals_addressed: config.therapeuticThemes,
      success_metrics: this.generateSuccessMetrics(config)
    };
  }

  private initializeDefaultWorlds(): void {
    // This will be populated with our franchise world configurations
    // in separate files to keep this core file manageable
  }

  private generateLongDescription(config: FranchiseWorldConfig): string {
    return `Experience the wonder of ${config.name}, a ${config.genre} world inspired by ${config.inspirationSource}. ` +
           `This therapeutic adventure combines the excitement of epic storytelling with meaningful personal growth, ` +
           `addressing themes of ${config.therapeuticThemes.join(', ')}. Journey through richly detailed environments ` +
           `where your choices matter and every interaction supports your therapeutic goals.`;
  }

  private generateSettingDescription(config: FranchiseWorldConfig): string {
    const systemDescriptions = Object.entries(config.worldSystems)
      .map(([system, systemConfig]) =>
        `${system}: ${systemConfig.adaptationElements.join(', ')}`
      ).join('; ');

    return `A ${config.genre} world featuring: ${systemDescriptions}`;
  }

  private generateKeyCharacters(config: FranchiseWorldConfig): Array<{name: string, role: string, description: string}> {
    return config.characterArchetypes.map(archetype => ({
      name: archetype.name,
      role: archetype.role,
      description: `${archetype.inspirationSource} - ${archetype.therapeuticFunction}`
    }));
  }

  private generateMainStorylines(config: FranchiseWorldConfig): string[] {
    return config.scenarioTemplates.map(template =>
      `${template.name}: ${template.description}`
    );
  }

  private extractTherapeuticTechniques(config: FranchiseWorldConfig): string[] {
    const techniques = new Set<string>();
    config.therapeuticIntegrationPoints.forEach(point => {
      techniques.add(point.technique);
    });
    return Array.from(techniques);
  }

  private generateSuccessMetrics(config: FranchiseWorldConfig): string[] {
    return [
      'Player engagement with therapeutic content',
      'Completion of therapeutic milestones',
      'Character development progression',
      'Narrative choice satisfaction',
      'Therapeutic goal achievement'
    ];
  }
}

/**
 * Active instance of a franchise world for a specific player session
 */
export class FranchiseWorldInstance {
  constructor(
    private config: FranchiseWorldConfig,
    private sessionId: string,
    private parameters: WorldParameters
  ) {}

  async initialize(): Promise<void> {
    // Initialize world state, characters, and narrative progression
    // This will integrate with the existing TTA systems
  }

  // Additional methods for managing the active world instance...
}
