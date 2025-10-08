/**
 * Session Scenarios Testing System
 *
 * Tests various play patterns including quick sessions, medium sessions,
 * extended sessions, and multi-session continuity scenarios.
 */

import { UserPersona, PersonaType } from '../personas/UserPersonas';
import { ImmersionMetrics, SessionMetrics } from '../metrics/ImmersionMetrics';

export interface SessionPattern {
  name: string;
  description: string;
  targetDuration: number; // minutes
  minDuration: number;
  maxDuration: number;
  breakPattern?: BreakPattern;
  interactionDensity: number; // interactions per minute
  complexityLevel: 'low' | 'medium' | 'high' | 'variable';
  therapeuticFocus: number; // 0-1 scale
  entertainmentFocus: number; // 0-1 scale
  suitablePersonas: PersonaType[];
}

export interface BreakPattern {
  frequency: number; // minutes between breaks
  duration: number; // break duration in minutes
  type: 'natural' | 'forced' | 'optional';
}

export interface SessionScenario {
  id: string;
  name: string;
  description: string;
  pattern: SessionPattern;
  worldComplexity: 'simple' | 'moderate' | 'complex' | 'epic';
  narrativeType: 'linear' | 'branching' | 'open_world' | 'episodic';
  expectedOutcomes: ExpectedOutcomes;
}

export interface ExpectedOutcomes {
  minimumEngagement: number; // 0-1 scale
  minimumImmersion: number; // 0-1 scale
  therapeuticBenefit: number; // 0-1 scale
  entertainmentValue: number; // 0-1 scale
  completionRate: number; // 0-1 scale
  returnProbability: number; // 0-1 scale
}

export interface ScenarioTestResult {
  scenarioId: string;
  sessionId: string;
  personaType: PersonaType;
  actualDuration: number;
  targetDuration: number;
  completionRate: number;
  engagementScore: number;
  immersionScore: number;
  therapeuticBenefit: number;
  entertainmentValue: number;
  meetsExpectations: boolean;
  deviations: string[];
  recommendations: string[];
  timestamp: number;
}

export class SessionScenarios {
  private scenarios: Map<string, SessionScenario> = new Map();
  private metricsCollector: ImmersionMetrics;

  constructor(metricsCollector: ImmersionMetrics) {
    this.metricsCollector = metricsCollector;
    this.initializeScenarios();
  }

  /**
   * Initialize predefined session scenarios
   */
  private initializeScenarios(): void {
    // Quick Session Scenarios (15-30 minutes)
    this.addScenario({
      id: 'quick_exploration',
      name: 'Quick Exploration Session',
      description: 'Short, casual exploration focused on immediate engagement and stress relief',
      pattern: {
        name: 'Quick Exploration',
        description: 'Light exploration with simple interactions',
        targetDuration: 20,
        minDuration: 15,
        maxDuration: 30,
        interactionDensity: 1.5, // 1.5 interactions per minute
        complexityLevel: 'low',
        therapeuticFocus: 0.6,
        entertainmentFocus: 0.8,
        suitablePersonas: [PersonaType.CASUAL_EXPLORER, PersonaType.SKEPTICAL_NEWCOMER]
      },
      worldComplexity: 'simple',
      narrativeType: 'linear',
      expectedOutcomes: {
        minimumEngagement: 0.7,
        minimumImmersion: 0.6,
        therapeuticBenefit: 0.5,
        entertainmentValue: 0.8,
        completionRate: 0.9,
        returnProbability: 0.7
      }
    });

    this.addScenario({
      id: 'quick_achievement',
      name: 'Quick Achievement Session',
      description: 'Goal-focused session with clear, achievable objectives',
      pattern: {
        name: 'Quick Achievement',
        description: 'Focused on completing specific goals quickly',
        targetDuration: 25,
        minDuration: 20,
        maxDuration: 35,
        interactionDensity: 2.0,
        complexityLevel: 'medium',
        therapeuticFocus: 0.5,
        entertainmentFocus: 0.9,
        suitablePersonas: [PersonaType.ACHIEVEMENT_HUNTER, PersonaType.SKEPTICAL_NEWCOMER]
      },
      worldComplexity: 'moderate',
      narrativeType: 'branching',
      expectedOutcomes: {
        minimumEngagement: 0.8,
        minimumImmersion: 0.7,
        therapeuticBenefit: 0.6,
        entertainmentValue: 0.9,
        completionRate: 0.85,
        returnProbability: 0.8
      }
    });

    // Medium Session Scenarios (1-2 hours)
    this.addScenario({
      id: 'story_immersion',
      name: 'Story Immersion Session',
      description: 'Deep narrative experience with character development',
      pattern: {
        name: 'Story Immersion',
        description: 'Rich narrative with character development focus',
        targetDuration: 75,
        minDuration: 60,
        maxDuration: 90,
        breakPattern: {
          frequency: 30,
          duration: 5,
          type: 'optional'
        },
        interactionDensity: 1.2,
        complexityLevel: 'high',
        therapeuticFocus: 0.7,
        entertainmentFocus: 0.9,
        suitablePersonas: [PersonaType.STORY_ENTHUSIAST, PersonaType.THERAPEUTIC_SEEKER]
      },
      worldComplexity: 'complex',
      narrativeType: 'branching',
      expectedOutcomes: {
        minimumEngagement: 0.8,
        minimumImmersion: 0.9,
        therapeuticBenefit: 0.8,
        entertainmentValue: 0.9,
        completionRate: 0.8,
        returnProbability: 0.9
      }
    });

    this.addScenario({
      id: 'world_building',
      name: 'World Building Session',
      description: 'Complex system exploration and world interaction',
      pattern: {
        name: 'World Building',
        description: 'Deep exploration of world systems and mechanics',
        targetDuration: 90,
        minDuration: 75,
        maxDuration: 120,
        breakPattern: {
          frequency: 45,
          duration: 10,
          type: 'natural'
        },
        interactionDensity: 1.8,
        complexityLevel: 'high',
        therapeuticFocus: 0.5,
        entertainmentFocus: 0.8,
        suitablePersonas: [PersonaType.WORLD_BUILDER, PersonaType.ACHIEVEMENT_HUNTER]
      },
      worldComplexity: 'complex',
      narrativeType: 'open_world',
      expectedOutcomes: {
        minimumEngagement: 0.8,
        minimumImmersion: 0.8,
        therapeuticBenefit: 0.6,
        entertainmentValue: 0.8,
        completionRate: 0.7,
        returnProbability: 0.8
      }
    });

    this.addScenario({
      id: 'social_connection',
      name: 'Social Connection Session',
      description: 'Character relationship and social dynamics focus',
      pattern: {
        name: 'Social Connection',
        description: 'Emphasis on character relationships and emotional connections',
        targetDuration: 60,
        minDuration: 45,
        maxDuration: 75,
        breakPattern: {
          frequency: 25,
          duration: 3,
          type: 'optional'
        },
        interactionDensity: 2.2,
        complexityLevel: 'medium',
        therapeuticFocus: 0.8,
        entertainmentFocus: 0.8,
        suitablePersonas: [PersonaType.SOCIAL_CONNECTOR, PersonaType.THERAPEUTIC_SEEKER]
      },
      worldComplexity: 'moderate',
      narrativeType: 'branching',
      expectedOutcomes: {
        minimumEngagement: 0.9,
        minimumImmersion: 0.8,
        therapeuticBenefit: 0.9,
        entertainmentValue: 0.8,
        completionRate: 0.85,
        returnProbability: 0.9
      }
    });

    // Extended Session Scenarios (3+ hours)
    this.addScenario({
      id: 'marathon_adventure',
      name: 'Marathon Adventure Session',
      description: 'Epic, long-form adventure with complex narratives',
      pattern: {
        name: 'Marathon Adventure',
        description: 'Extended play with complex, evolving narratives',
        targetDuration: 240,
        minDuration: 180,
        maxDuration: 360,
        breakPattern: {
          frequency: 60,
          duration: 15,
          type: 'natural'
        },
        interactionDensity: 1.5,
        complexityLevel: 'variable',
        therapeuticFocus: 0.6,
        entertainmentFocus: 0.9,
        suitablePersonas: [PersonaType.MARATHON_PLAYER, PersonaType.STORY_ENTHUSIAST]
      },
      worldComplexity: 'epic',
      narrativeType: 'open_world',
      expectedOutcomes: {
        minimumEngagement: 0.8,
        minimumImmersion: 0.9,
        therapeuticBenefit: 0.7,
        entertainmentValue: 0.9,
        completionRate: 0.6,
        returnProbability: 0.9
      }
    });

    this.addScenario({
      id: 'deep_therapeutic',
      name: 'Deep Therapeutic Session',
      description: 'Extended session with intensive therapeutic integration',
      pattern: {
        name: 'Deep Therapeutic',
        description: 'Long-form therapeutic journey with entertainment wrapper',
        targetDuration: 180,
        minDuration: 150,
        maxDuration: 240,
        breakPattern: {
          frequency: 45,
          duration: 10,
          type: 'natural'
        },
        interactionDensity: 1.3,
        complexityLevel: 'high',
        therapeuticFocus: 0.9,
        entertainmentFocus: 0.8,
        suitablePersonas: [PersonaType.THERAPEUTIC_SEEKER, PersonaType.MARATHON_PLAYER]
      },
      worldComplexity: 'complex',
      narrativeType: 'episodic',
      expectedOutcomes: {
        minimumEngagement: 0.8,
        minimumImmersion: 0.8,
        therapeuticBenefit: 0.9,
        entertainmentValue: 0.8,
        completionRate: 0.7,
        returnProbability: 0.9
      }
    });
  }

  /**
   * Add a new scenario
   */
  addScenario(scenario: SessionScenario): void {
    this.scenarios.set(scenario.id, scenario);
  }

  /**
   * Get all scenarios
   */
  getAllScenarios(): SessionScenario[] {
    return Array.from(this.scenarios.values());
  }

  /**
   * Get scenarios suitable for a specific persona
   */
  getScenariosForPersona(personaType: PersonaType): SessionScenario[] {
    return this.getAllScenarios().filter(scenario =>
      scenario.pattern.suitablePersonas.includes(personaType)
    );
  }

  /**
   * Test a specific scenario with a persona
   */
  async testScenario(scenarioId: string, persona: UserPersona): Promise<ScenarioTestResult> {
    const scenario = this.scenarios.get(scenarioId);
    if (!scenario) {
      throw new Error(`Scenario ${scenarioId} not found`);
    }

    console.log(`  🎭 Testing scenario "${scenario.name}" with ${persona.type} persona...`);

    const sessionId = `${scenarioId}_${persona.id}_${Date.now()}`;
    const startTime = Date.now();

    // Start metrics tracking
    this.metricsCollector.startSession(sessionId, persona.type);

    // Simulate session execution
    const actualDuration = await this.simulateSession(sessionId, scenario, persona);

    // Finalize metrics
    const sessionMetrics = this.metricsCollector.finalizeSession(sessionId, actualDuration);

    if (!sessionMetrics) {
      throw new Error(`Failed to collect metrics for session ${sessionId}`);
    }

    // Calculate results
    const result = this.calculateScenarioResult(scenario, persona, sessionMetrics, actualDuration);

    console.log(`    ✅ Scenario completed - Duration: ${actualDuration}min, Engagement: ${result.engagementScore.toFixed(2)}`);

    return result;
  }

  /**
   * Simulate a session execution
   */
  private async simulateSession(sessionId: string, scenario: SessionScenario, persona: UserPersona): Promise<number> {
    const pattern = scenario.pattern;
    const targetDuration = pattern.targetDuration;

    // Adjust duration based on persona preferences
    const personalityAdjustment = this.calculatePersonalityAdjustment(persona, pattern);
    const adjustedDuration = Math.max(
      pattern.minDuration,
      Math.min(pattern.maxDuration, targetDuration * personalityAdjustment)
    );

    // Simulate interactions over time
    const totalInteractions = Math.floor(adjustedDuration * pattern.interactionDensity);
    const interactionInterval = (adjustedDuration * 60 * 1000) / totalInteractions; // milliseconds

    let currentTime = 0;
    let engagement = 0.7; // Starting engagement
    let shouldContinue = true;

    for (let i = 0; i < totalInteractions && shouldContinue; i++) {
      currentTime += interactionInterval;
      const currentMinutes = currentTime / (60 * 1000);

      // Simulate different types of interactions
      const interactionType = this.selectInteractionType(scenario, persona, i, totalInteractions);

      // Record interaction
      this.metricsCollector.recordInteraction(sessionId, interactionType, {
        scenarioId: scenario.id,
        interactionIndex: i,
        totalInteractions,
        currentTime: currentMinutes
      });

      // Update engagement based on persona and scenario
      engagement = this.updateEngagement(engagement, persona, scenario, currentMinutes);

      // Check if persona would continue
      shouldContinue = persona.shouldContinueSession(currentMinutes, engagement);

      // Handle breaks if specified
      if (pattern.breakPattern && this.shouldTakeBreak(currentMinutes, pattern.breakPattern)) {
        currentTime += pattern.breakPattern.duration * 60 * 1000;
      }

      // Small delay to simulate real-time (optional, for demonstration)
      await new Promise(resolve => setTimeout(resolve, 1));
    }

    return currentTime / (60 * 1000); // Return duration in minutes
  }

  /**
   * Calculate personality adjustment factor for session duration
   */
  private calculatePersonalityAdjustment(persona: UserPersona, pattern: SessionPattern): number {
    const patienceBonus = persona.behavioralPatterns.patienceLevel * 0.3;
    const complexityTolerance = persona.behavioralPatterns.complexityTolerance;

    let adjustment = 1.0;

    // Adjust based on complexity tolerance vs pattern complexity
    if (pattern.complexityLevel === 'high' && complexityTolerance < 0.5) {
      adjustment *= 0.7; // Reduce duration for low complexity tolerance
    } else if (pattern.complexityLevel === 'low' && complexityTolerance > 0.8) {
      adjustment *= 1.2; // Increase duration for high complexity tolerance
    }

    // Apply patience bonus
    adjustment += patienceBonus;

    return Math.max(0.5, Math.min(1.5, adjustment));
  }

  /**
   * Select interaction type based on scenario and persona
   */
  private selectInteractionType(scenario: SessionScenario, persona: UserPersona, index: number, total: number): string {
    const interactionTypes = ['choice', 'exploration', 'dialogue', 'world_interaction'];

    // Weight selection based on persona preferences and scenario type
    const weights = {
      choice: persona.engagementTriggers.achievementProgression,
      exploration: persona.engagementTriggers.mysteryAndDiscovery,
      dialogue: persona.engagementTriggers.socialInteraction,
      world_interaction: persona.engagementTriggers.worldComplexity
    };

    // Select based on weighted random
    const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
    let random = Math.random() * totalWeight;

    for (const [type, weight] of Object.entries(weights)) {
      random -= weight;
      if (random <= 0) {
        return type;
      }
    }

    return interactionTypes[0]; // Fallback
  }

  /**
   * Update engagement level during session
   */
  private updateEngagement(currentEngagement: number, persona: UserPersona, scenario: SessionScenario, currentMinutes: number): number {
    // Engagement naturally declines over time
    const timeDecay = Math.max(0, 1 - (currentMinutes / (persona.behavioralPatterns.attentionSpan * 3)));

    // Scenario quality affects engagement
    const scenarioBonus = (scenario.expectedOutcomes.entertainmentValue - 0.5) * 0.2;

    // Persona compatibility affects engagement
    const compatibilityBonus = scenario.pattern.suitablePersonas.includes(persona.type as PersonaType) ? 0.1 : -0.1;

    const newEngagement = currentEngagement * timeDecay + scenarioBonus + compatibilityBonus;

    return Math.max(0.1, Math.min(1.0, newEngagement));
  }

  /**
   * Check if a break should be taken
   */
  private shouldTakeBreak(currentMinutes: number, breakPattern: BreakPattern): boolean {
    if (breakPattern.type === 'forced') {
      return currentMinutes % breakPattern.frequency < 0.1; // Within 0.1 minutes of break time
    } else if (breakPattern.type === 'natural') {
      return Math.random() < 0.3 && currentMinutes % breakPattern.frequency < 2; // 30% chance near break time
    }
    return false; // Optional breaks not implemented in simulation
  }

  /**
   * Calculate scenario test result
   */
  private calculateScenarioResult(
    scenario: SessionScenario,
    persona: UserPersona,
    sessionMetrics: SessionMetrics,
    actualDuration: number
  ): ScenarioTestResult {
    const expected = scenario.expectedOutcomes;
    const actual = {
      engagement: sessionMetrics.immersionScore.engagementSustainability,
      immersion: sessionMetrics.immersionScore.overall,
      therapeuticBenefit: sessionMetrics.therapeuticBenefit,
      entertainmentValue: sessionMetrics.entertainmentValue
    };

    const completionRate = Math.min(actualDuration / scenario.pattern.targetDuration, 1.0);

    const deviations: string[] = [];
    if (actual.engagement < expected.minimumEngagement) {
      deviations.push(`Low engagement: ${actual.engagement.toFixed(2)} < ${expected.minimumEngagement}`);
    }
    if (actual.immersion < expected.minimumImmersion) {
      deviations.push(`Low immersion: ${actual.immersion.toFixed(2)} < ${expected.minimumImmersion}`);
    }
    if (actual.therapeuticBenefit < expected.therapeuticBenefit) {
      deviations.push(`Low therapeutic benefit: ${actual.therapeuticBenefit.toFixed(2)} < ${expected.therapeuticBenefit}`);
    }
    if (actual.entertainmentValue < expected.entertainmentValue) {
      deviations.push(`Low entertainment value: ${actual.entertainmentValue.toFixed(2)} < ${expected.entertainmentValue}`);
    }

    const meetsExpectations = deviations.length === 0;

    const recommendations = this.generateScenarioRecommendations(scenario, persona, actual, expected, deviations);

    return {
      scenarioId: scenario.id,
      sessionId: sessionMetrics.sessionId,
      personaType: persona.type as PersonaType,
      actualDuration,
      targetDuration: scenario.pattern.targetDuration,
      completionRate,
      engagementScore: actual.engagement,
      immersionScore: actual.immersion,
      therapeuticBenefit: actual.therapeuticBenefit,
      entertainmentValue: actual.entertainmentValue,
      meetsExpectations,
      deviations,
      recommendations,
      timestamp: Date.now()
    };
  }

  /**
   * Generate recommendations for scenario improvement
   */
  private generateScenarioRecommendations(
    scenario: SessionScenario,
    persona: UserPersona,
    actual: any,
    expected: any,
    deviations: string[]
  ): string[] {
    const recommendations: string[] = [];

    if (actual.engagement < expected.minimumEngagement) {
      recommendations.push('Increase interaction density or add more engaging elements');
    }
    if (actual.immersion < expected.minimumImmersion) {
      recommendations.push('Improve narrative coherence and world consistency');
    }
    if (actual.therapeuticBenefit < expected.therapeuticBenefit) {
      recommendations.push('Better integrate therapeutic elements into gameplay');
    }
    if (actual.entertainmentValue < expected.entertainmentValue) {
      recommendations.push('Enhance entertainment value through better pacing and rewards');
    }

    return recommendations;
  }
}

export default SessionScenarios;
