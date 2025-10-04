/**
 * TTA Integration Module
 * 
 * Integrates the franchise world system with existing TTA components including
 * WorldDetails model, AIWorldGenerator, simulation framework, and other systems.
 */

import { FranchiseWorldSystem, FranchiseWorldConfig } from '../core/FranchiseWorldSystem';
import { WorldDetails, WorldParameters, TherapeuticApproach, DifficultyLevel } from '../types/TTATypes';
import { ELDERMERE_REALMS, ARCANUM_ACADEMY, CROWNS_GAMBIT } from '../worlds/FantasyWorlds';
import { STELLAR_CONFEDERATION, NEON_METROPOLIS } from '../worlds/SciFiWorlds';

/**
 * Integration bridge between franchise worlds and TTA's existing world system
 */
export class FranchiseWorldIntegration {
  private franchiseSystem: FranchiseWorldSystem;
  
  constructor() {
    this.franchiseSystem = new FranchiseWorldSystem();
    this.initializeFranchiseWorlds();
  }

  /**
   * Initialize all franchise worlds in the system
   */
  private initializeFranchiseWorlds(): void {
    // Register fantasy worlds
    this.franchiseSystem.registerWorld(ELDERMERE_REALMS);
    this.franchiseSystem.registerWorld(ARCANUM_ACADEMY);
    this.franchiseSystem.registerWorld(CROWNS_GAMBIT);

    // Register sci-fi worlds
    this.franchiseSystem.registerWorld(STELLAR_CONFEDERATION);
    this.franchiseSystem.registerWorld(NEON_METROPOLIS);

    // TODO: Add remaining worlds (Shadow Realms, Mystic Isles, Quantum Frontier, etc.)
  }

  /**
   * Get all franchise worlds as TTA WorldDetails
   */
  async getAllFranchiseWorlds(): Promise<WorldDetails[]> {
    const franchiseWorlds = this.franchiseSystem.getAvailableWorlds();
    return franchiseWorlds.map(world => this.convertToWorldDetails(world));
  }

  /**
   * Get franchise worlds by genre
   */
  async getFranchiseWorldsByGenre(genre: 'fantasy' | 'sci-fi'): Promise<WorldDetails[]> {
    const franchiseWorlds = this.franchiseSystem.getWorldsByGenre(genre);
    return franchiseWorlds.map(world => this.convertToWorldDetails(world));
  }

  /**
   * Get specific franchise world by ID
   */
  async getFranchiseWorld(worldId: string): Promise<WorldDetails | null> {
    const franchiseWorld = this.franchiseSystem.getWorld(worldId);
    if (!franchiseWorld) {
      return null;
    }
    return this.convertToWorldDetails(franchiseWorld);
  }

  /**
   * Convert FranchiseWorldConfig to TTA WorldDetails format
   */
  private convertToWorldDetails(config: FranchiseWorldConfig): WorldDetails {
    return {
      world_id: config.franchiseId,
      name: config.name,
      description: this.generateShortDescription(config),
      long_description: this.generateLongDescription(config),
      therapeutic_themes: config.therapeuticThemes,
      therapeutic_approaches: config.therapeuticApproaches,
      difficulty_level: this.mapDifficultyLevel(config),
      estimated_duration: this.calculateEstimatedDuration(config),
      setting_description: this.generateSettingDescription(config),
      key_characters: this.generateKeyCharacters(config),
      main_storylines: this.generateMainStorylines(config),
      therapeutic_techniques_used: this.extractTherapeuticTechniques(config),
      prerequisites: this.generatePrerequisites(config),
      recommended_therapeutic_readiness: this.calculateTherapeuticReadiness(config),
      content_warnings: this.generateContentWarnings(config)
    };
  }

  private generateShortDescription(config: FranchiseWorldConfig): string {
    return `A ${config.genre} adventure inspired by ${config.inspirationSource}. ` +
           `Explore themes of ${config.therapeuticThemes.slice(0, 3).join(', ')} through engaging storytelling.`;
  }

  private generateLongDescription(config: FranchiseWorldConfig): string {
    return `Experience the wonder of ${config.name}, a ${config.genre} world inspired by ${config.inspirationSource}. ` +
           `This therapeutic adventure combines the excitement of epic storytelling with meaningful personal growth, ` +
           `addressing themes of ${config.therapeuticThemes.join(', ')}. Journey through richly detailed environments ` +
           `where your choices matter and every interaction supports your therapeutic goals. ` +
           `The world features ${Object.keys(config.worldSystems).length} interconnected systems that create ` +
           `a living, breathing environment for your adventure.`;
  }

  private mapDifficultyLevel(config: FranchiseWorldConfig): DifficultyLevel {
    // Calculate average complexity across all world systems
    const avgComplexity = Object.values(config.worldSystems)
      .reduce((sum, system) => sum + system.complexity, 0) / Object.keys(config.worldSystems).length;
    
    if (avgComplexity < 0.4) return DifficultyLevel.BEGINNER;
    if (avgComplexity < 0.7) return DifficultyLevel.INTERMEDIATE;
    return DifficultyLevel.ADVANCED;
  }

  private calculateEstimatedDuration(config: FranchiseWorldConfig): { hours: number } {
    // Base duration on session length support and complexity
    const avgComplexity = Object.values(config.worldSystems)
      .reduce((sum, system) => sum + system.complexity, 0) / Object.keys(config.worldSystems).length;
    
    const baseDuration = config.sessionLengthSupport.medium.targetDuration / 60; // Convert to hours
    const complexityMultiplier = 1 + avgComplexity; // 1-2x multiplier
    
    return { hours: Math.round(baseDuration * complexityMultiplier) };
  }

  private generateSettingDescription(config: FranchiseWorldConfig): string {
    const systemDescriptions = Object.entries(config.worldSystems)
      .filter(([_, system]) => system.complexity > 0.6) // Only include complex systems
      .map(([systemName, system]) => {
        const elements = system.adaptationElements.slice(0, 2).join(' and ');
        return `${systemName}: ${elements}`;
      })
      .slice(0, 4) // Limit to 4 systems for readability
      .join('; ');
    
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
      `${template.name}: ${template.description} (${template.duration} session)`
    );
  }

  private extractTherapeuticTechniques(config: FranchiseWorldConfig): string[] {
    const techniques = new Set<string>();
    
    // Extract from therapeutic integration points
    config.therapeuticIntegrationPoints.forEach(point => {
      techniques.add(point.technique);
    });
    
    // Extract from character interaction patterns
    config.characterArchetypes.forEach(archetype => {
      archetype.interactionPatterns.forEach(pattern => {
        techniques.add(pattern.therapeutic_technique);
      });
    });
    
    return Array.from(techniques);
  }

  private generatePrerequisites(config: FranchiseWorldConfig): Array<{type: string, description: string}> {
    const prerequisites: Array<{type: string, description: string}> = [];
    
    // Add therapeutic readiness prerequisites
    const avgTherapeuticRelevance = Object.values(config.worldSystems)
      .reduce((sum, system) => sum + system.therapeuticRelevance, 0) / Object.keys(config.worldSystems).length;
    
    if (avgTherapeuticRelevance > 0.7) {
      prerequisites.push({
        type: 'therapeutic_readiness',
        description: 'Comfortable with moderate therapeutic content and self-reflection'
      });
    }
    
    // Add complexity prerequisites
    const avgComplexity = Object.values(config.worldSystems)
      .reduce((sum, system) => sum + system.complexity, 0) / Object.keys(config.worldSystems).length;
    
    if (avgComplexity > 0.8) {
      prerequisites.push({
        type: 'complexity_comfort',
        description: 'Comfortable with complex narratives and multiple interconnected systems'
      });
    }
    
    return prerequisites;
  }

  private calculateTherapeuticReadiness(config: FranchiseWorldConfig): number {
    // Calculate based on therapeutic intensity and integration points
    const avgTherapeuticRelevance = Object.values(config.worldSystems)
      .reduce((sum, system) => sum + system.therapeuticRelevance, 0) / Object.keys(config.worldSystems).length;
    
    const integrationIntensity = config.therapeuticIntegrationPoints.length / 10; // Normalize to 0-1
    
    return Math.min((avgTherapeuticRelevance + integrationIntensity) / 2, 1.0);
  }

  private generateContentWarnings(config: FranchiseWorldConfig): string[] {
    const warnings: string[] = [];
    
    // Extract from content ratings
    config.contentRatings.forEach(rating => {
      rating.descriptors.forEach(descriptor => {
        if (!warnings.includes(descriptor)) {
          warnings.push(descriptor);
        }
      });
    });
    
    // Add therapeutic content warnings
    if (config.therapeuticThemes.includes('trauma_recovery')) {
      warnings.push('Contains themes related to trauma and recovery');
    }
    
    if (config.therapeuticThemes.includes('anxiety_management')) {
      warnings.push('Contains scenarios that may trigger anxiety (in therapeutic context)');
    }
    
    return warnings;
  }

  /**
   * Create customized world parameters for franchise worlds
   */
  createWorldParameters(
    config: FranchiseWorldConfig,
    playerPreferences: any
  ): WorldParameters {
    return {
      therapeutic_intensity: this.calculateTherapeuticIntensity(config, playerPreferences),
      narrative_pace: this.determineNarrativePace(config, playerPreferences),
      interaction_frequency: this.determineInteractionFrequency(config, playerPreferences),
      challenge_level: this.mapDifficultyLevel(config),
      focus_areas: config.therapeuticThemes,
      avoid_topics: playerPreferences?.avoid_topics || [],
      session_length_preference: playerPreferences?.session_length || 60
    };
  }

  private calculateTherapeuticIntensity(config: FranchiseWorldConfig, playerPreferences: any): number {
    const baseIntensity = this.calculateTherapeuticReadiness(config);
    const playerPreference = playerPreferences?.therapeutic_intensity || 0.5;
    
    // Blend world capability with player preference
    return (baseIntensity + playerPreference) / 2;
  }

  private determineNarrativePace(config: FranchiseWorldConfig, playerPreferences: any): string {
    const playerPace = playerPreferences?.narrative_pace;
    if (playerPace) return playerPace;
    
    // Default based on world complexity
    const avgComplexity = Object.values(config.worldSystems)
      .reduce((sum, system) => sum + system.complexity, 0) / Object.keys(config.worldSystems).length;
    
    if (avgComplexity > 0.8) return 'slow';
    if (avgComplexity > 0.5) return 'medium';
    return 'fast';
  }

  private determineInteractionFrequency(config: FranchiseWorldConfig, playerPreferences: any): string {
    const playerFreq = playerPreferences?.interaction_frequency;
    if (playerFreq) return playerFreq;
    
    // Default based on social system complexity
    const socialComplexity = config.worldSystems.social?.complexity || 0.5;
    
    if (socialComplexity > 0.8) return 'frequent';
    if (socialComplexity > 0.5) return 'balanced';
    return 'minimal';
  }

  /**
   * Integration with simulation framework
   */
  async validateWorldForSimulation(worldId: string): Promise<boolean> {
    const world = this.franchiseSystem.getWorld(worldId);
    if (!world) return false;
    
    // Check if world has sufficient complexity for simulation
    const avgComplexity = Object.values(world.worldSystems)
      .reduce((sum, system) => sum + system.complexity, 0) / Object.keys(world.worldSystems).length;
    
    return avgComplexity >= 0.5 && world.characterArchetypes.length >= 2;
  }
}
