/**
 * Immersion Metrics System
 *
 * Evaluates and measures immersion quality across multiple dimensions
 * including narrative coherence, character development, world consistency,
 * player agency, and therapeutic integration subtlety.
 */

export interface ImmersionScore {
  narrativeCoherence: number; // 0-1 scale
  characterDevelopment: number; // 0-1 scale
  worldConsistency: number; // 0-1 scale
  playerAgency: number; // 0-1 scale
  therapeuticIntegration: number; // 0-1 scale
  engagementSustainability: number; // 0-1 scale
  emotionalInvestment: number; // 0-1 scale
  cognitiveLoad: number; // 0-1 scale (lower is better)
  overall: number; // 0-1 scale
}

export interface SessionMetrics {
  sessionId: string;
  personaType: string;
  duration: number; // minutes
  interactionCount: number;
  choicesMade: number;
  explorationDepth: number; // 0-1 scale
  storyProgression: number; // 0-1 scale
  characterGrowth: number; // 0-1 scale
  worldEngagement: number; // 0-1 scale
  therapeuticBenefit: number; // 0-1 scale
  entertainmentValue: number; // 0-1 scale
  immersionScore: ImmersionScore;
  timestamp: number;
}

export interface NarrativeCoherenceMetrics {
  plotConsistency: number;
  characterMotivationClarity: number;
  causeEffectLogic: number;
  timelineConsistency: number;
  thematicCoherence: number;
}

export interface CharacterDevelopmentMetrics {
  characterGrowthRate: number;
  personalityConsistency: number;
  emotionalDepth: number;
  relationshipDevelopment: number;
  believabilityScore: number;
}

export interface WorldConsistencyMetrics {
  internalLogic: number;
  systemInteractions: number;
  physicalLaws: number;
  culturalConsistency: number;
  historicalContinuity: number;
}

export interface PlayerAgencyMetrics {
  choiceImpact: number;
  consequenceMeaningfulness: number;
  playerInfluence: number;
  decisionComplexity: number;
  agencyPerception: number;
}

export interface TherapeuticIntegrationMetrics {
  subtlety: number; // How well therapeutic elements are hidden
  naturalness: number; // How naturally they fit into gameplay
  effectiveness: number; // How effective they are therapeutically
  entertainmentMaintenance: number; // How well entertainment value is maintained
  awarenessLevel: number; // How aware player is of therapeutic elements (lower is better)
}

export class ImmersionMetrics {
  private sessionMetrics: Map<string, SessionMetrics> = new Map();
  private realTimeTracking: boolean = true;

  constructor(enableRealTimeTracking: boolean = true) {
    this.realTimeTracking = enableRealTimeTracking;
  }

  /**
   * Start tracking metrics for a session
   */
  startSession(sessionId: string, personaType: string): void {
    const metrics: SessionMetrics = {
      sessionId,
      personaType,
      duration: 0,
      interactionCount: 0,
      choicesMade: 0,
      explorationDepth: 0,
      storyProgression: 0,
      characterGrowth: 0,
      worldEngagement: 0,
      therapeuticBenefit: 0,
      entertainmentValue: 0,
      immersionScore: this.initializeImmersionScore(),
      timestamp: Date.now()
    };

    this.sessionMetrics.set(sessionId, metrics);
  }

  /**
   * Update session metrics during gameplay
   */
  updateSessionMetrics(sessionId: string, updates: Partial<SessionMetrics>): void {
    const metrics = this.sessionMetrics.get(sessionId);
    if (metrics) {
      Object.assign(metrics, updates);

      // Recalculate immersion score
      metrics.immersionScore = this.calculateImmersionScore(metrics);

      if (this.realTimeTracking) {
        this.emitMetricsUpdate(sessionId, metrics);
      }
    }
  }

  /**
   * Record a player interaction
   */
  recordInteraction(sessionId: string, interactionType: string, context: any): void {
    const metrics = this.sessionMetrics.get(sessionId);
    if (metrics) {
      metrics.interactionCount++;

      // Update specific metrics based on interaction type
      switch (interactionType) {
        case 'choice':
          metrics.choicesMade++;
          this.updatePlayerAgencyMetrics(sessionId, context);
          break;
        case 'exploration':
          this.updateExplorationMetrics(sessionId, context);
          break;
        case 'dialogue':
          this.updateCharacterDevelopmentMetrics(sessionId, context);
          break;
        case 'world_interaction':
          this.updateWorldEngagementMetrics(sessionId, context);
          break;
      }

      // Recalculate overall immersion score
      metrics.immersionScore = this.calculateImmersionScore(metrics);
    }
  }

  /**
   * Calculate comprehensive immersion score
   */
  calculateImmersionScore(metrics: SessionMetrics): ImmersionScore {
    const narrativeCoherence = this.calculateNarrativeCoherence(metrics);
    const characterDevelopment = this.calculateCharacterDevelopment(metrics);
    const worldConsistency = this.calculateWorldConsistency(metrics);
    const playerAgency = this.calculatePlayerAgency(metrics);
    const therapeuticIntegration = this.calculateTherapeuticIntegration(metrics);
    const engagementSustainability = this.calculateEngagementSustainability(metrics);
    const emotionalInvestment = this.calculateEmotionalInvestment(metrics);
    const cognitiveLoad = this.calculateCognitiveLoad(metrics);

    const overall = (
      narrativeCoherence * 0.20 +
      characterDevelopment * 0.15 +
      worldConsistency * 0.15 +
      playerAgency * 0.15 +
      therapeuticIntegration * 0.15 +
      engagementSustainability * 0.10 +
      emotionalInvestment * 0.10 +
      (1 - cognitiveLoad) * 0.05 // Lower cognitive load is better
    );

    return {
      narrativeCoherence,
      characterDevelopment,
      worldConsistency,
      playerAgency,
      therapeuticIntegration,
      engagementSustainability,
      emotionalInvestment,
      cognitiveLoad,
      overall
    };
  }

  /**
   * Calculate narrative coherence score
   */
  private calculateNarrativeCoherence(metrics: SessionMetrics): number {
    // Mock implementation - would analyze story consistency, plot logic, etc.
    const baseScore = 0.7 + (metrics.storyProgression * 0.2);
    const interactionBonus = Math.min(metrics.interactionCount / 50, 0.1);
    return Math.min(baseScore + interactionBonus, 1.0);
  }

  /**
   * Calculate character development score
   */
  private calculateCharacterDevelopment(metrics: SessionMetrics): number {
    // Mock implementation - would analyze character growth, believability, etc.
    const baseScore = 0.6 + (metrics.characterGrowth * 0.3);
    const durationBonus = Math.min(metrics.duration / 120, 0.1); // Bonus for longer sessions
    return Math.min(baseScore + durationBonus, 1.0);
  }

  /**
   * Calculate world consistency score
   */
  private calculateWorldConsistency(metrics: SessionMetrics): number {
    // Mock implementation - would analyze internal logic, system interactions, etc.
    const baseScore = 0.75 + (metrics.worldEngagement * 0.15);
    const explorationBonus = metrics.explorationDepth * 0.1;
    return Math.min(baseScore + explorationBonus, 1.0);
  }

  /**
   * Calculate player agency score
   */
  private calculatePlayerAgency(metrics: SessionMetrics): number {
    // Mock implementation - would analyze choice impact, consequences, etc.
    if (metrics.choicesMade === 0) return 0.5; // Default if no choices made

    const choiceRatio = metrics.choicesMade / Math.max(metrics.interactionCount, 1);
    const baseScore = 0.6 + (choiceRatio * 0.3);
    return Math.min(baseScore, 1.0);
  }

  /**
   * Calculate therapeutic integration score
   */
  private calculateTherapeuticIntegration(metrics: SessionMetrics): number {
    // Mock implementation - would analyze subtlety, naturalness, effectiveness
    const subtlety = 0.8; // How well therapeutic elements are hidden
    const naturalness = 0.7; // How naturally they fit into gameplay
    const effectiveness = metrics.therapeuticBenefit;
    const entertainmentMaintenance = metrics.entertainmentValue;

    return (subtlety * 0.3 + naturalness * 0.3 + effectiveness * 0.2 + entertainmentMaintenance * 0.2);
  }

  /**
   * Calculate engagement sustainability score
   */
  private calculateEngagementSustainability(metrics: SessionMetrics): number {
    // Mock implementation - would analyze interest maintenance over time
    const durationFactor = Math.min(metrics.duration / 60, 1.0); // Normalize to 1 hour
    const interactionDensity = metrics.interactionCount / Math.max(metrics.duration, 1);
    const baseScore = 0.6 + (durationFactor * 0.2) + (Math.min(interactionDensity / 2, 0.2));
    return Math.min(baseScore, 1.0);
  }

  /**
   * Calculate emotional investment score
   */
  private calculateEmotionalInvestment(metrics: SessionMetrics): number {
    // Mock implementation - would analyze emotional attachment, responses
    const baseScore = 0.5 + (metrics.characterGrowth * 0.3) + (metrics.storyProgression * 0.2);
    return Math.min(baseScore, 1.0);
  }

  /**
   * Calculate cognitive load score
   */
  private calculateCognitiveLoad(metrics: SessionMetrics): number {
    // Mock implementation - would analyze information processing difficulty
    // Lower scores are better (less cognitive load)
    const complexityFactor = metrics.worldEngagement; // More world engagement might mean more complexity
    const choiceComplexity = Math.min(metrics.choicesMade / 10, 0.3);
    return Math.min(complexityFactor * 0.5 + choiceComplexity, 1.0);
  }

  /**
   * Update player agency metrics based on choice context
   */
  private updatePlayerAgencyMetrics(sessionId: string, context: any): void {
    // Mock implementation - would analyze choice impact and consequences
    const metrics = this.sessionMetrics.get(sessionId);
    if (metrics) {
      // Simulate choice impact analysis
      const choiceImpact = Math.random() * 0.3 + 0.7; // Random between 0.7-1.0
      metrics.storyProgression = Math.min(metrics.storyProgression + 0.1, 1.0);
    }
  }

  /**
   * Update exploration metrics
   */
  private updateExplorationMetrics(sessionId: string, context: any): void {
    const metrics = this.sessionMetrics.get(sessionId);
    if (metrics) {
      metrics.explorationDepth = Math.min(metrics.explorationDepth + 0.05, 1.0);
      metrics.worldEngagement = Math.min(metrics.worldEngagement + 0.03, 1.0);
    }
  }

  /**
   * Update character development metrics
   */
  private updateCharacterDevelopmentMetrics(sessionId: string, context: any): void {
    const metrics = this.sessionMetrics.get(sessionId);
    if (metrics) {
      metrics.characterGrowth = Math.min(metrics.characterGrowth + 0.02, 1.0);
    }
  }

  /**
   * Update world engagement metrics
   */
  private updateWorldEngagementMetrics(sessionId: string, context: any): void {
    const metrics = this.sessionMetrics.get(sessionId);
    if (metrics) {
      metrics.worldEngagement = Math.min(metrics.worldEngagement + 0.04, 1.0);
    }
  }

  /**
   * Finalize session metrics
   */
  finalizeSession(sessionId: string, duration: number): SessionMetrics | null {
    const metrics = this.sessionMetrics.get(sessionId);
    if (metrics) {
      metrics.duration = duration;
      metrics.immersionScore = this.calculateImmersionScore(metrics);

      // Calculate final therapeutic benefit and entertainment value
      metrics.therapeuticBenefit = this.calculateFinalTherapeuticBenefit(metrics);
      metrics.entertainmentValue = this.calculateFinalEntertainmentValue(metrics);

      return metrics;
    }
    return null;
  }

  /**
   * Get session metrics
   */
  getSessionMetrics(sessionId: string): SessionMetrics | null {
    return this.sessionMetrics.get(sessionId) || null;
  }

  /**
   * Get all session metrics
   */
  getAllSessionMetrics(): SessionMetrics[] {
    return Array.from(this.sessionMetrics.values());
  }

  /**
   * Calculate aggregate metrics across multiple sessions
   */
  calculateAggregateMetrics(sessionIds?: string[]): ImmersionScore {
    const sessions = sessionIds
      ? sessionIds.map(id => this.sessionMetrics.get(id)).filter(Boolean) as SessionMetrics[]
      : this.getAllSessionMetrics();

    if (sessions.length === 0) {
      return this.initializeImmersionScore();
    }

    const aggregateScore: ImmersionScore = {
      narrativeCoherence: 0,
      characterDevelopment: 0,
      worldConsistency: 0,
      playerAgency: 0,
      therapeuticIntegration: 0,
      engagementSustainability: 0,
      emotionalInvestment: 0,
      cognitiveLoad: 0,
      overall: 0
    };

    sessions.forEach(session => {
      const score = session.immersionScore;
      aggregateScore.narrativeCoherence += score.narrativeCoherence;
      aggregateScore.characterDevelopment += score.characterDevelopment;
      aggregateScore.worldConsistency += score.worldConsistency;
      aggregateScore.playerAgency += score.playerAgency;
      aggregateScore.therapeuticIntegration += score.therapeuticIntegration;
      aggregateScore.engagementSustainability += score.engagementSustainability;
      aggregateScore.emotionalInvestment += score.emotionalInvestment;
      aggregateScore.cognitiveLoad += score.cognitiveLoad;
      aggregateScore.overall += score.overall;
    });

    const sessionCount = sessions.length;
    Object.keys(aggregateScore).forEach(key => {
      (aggregateScore as any)[key] /= sessionCount;
    });

    return aggregateScore;
  }

  /**
   * Initialize empty immersion score
   */
  private initializeImmersionScore(): ImmersionScore {
    return {
      narrativeCoherence: 0,
      characterDevelopment: 0,
      worldConsistency: 0,
      playerAgency: 0,
      therapeuticIntegration: 0,
      engagementSustainability: 0,
      emotionalInvestment: 0,
      cognitiveLoad: 0,
      overall: 0
    };
  }

  /**
   * Calculate final therapeutic benefit
   */
  private calculateFinalTherapeuticBenefit(metrics: SessionMetrics): number {
    // Mock implementation - would analyze therapeutic outcomes
    const durationFactor = Math.min(metrics.duration / 60, 1.0);
    const engagementFactor = metrics.immersionScore.overall;
    return (durationFactor * 0.4 + engagementFactor * 0.6) * Math.random() * 0.3 + 0.7;
  }

  /**
   * Calculate final entertainment value
   */
  private calculateFinalEntertainmentValue(metrics: SessionMetrics): number {
    // Mock implementation - would analyze entertainment outcomes
    const immersionFactor = metrics.immersionScore.overall;
    const interactionFactor = Math.min(metrics.interactionCount / 30, 1.0);
    return (immersionFactor * 0.6 + interactionFactor * 0.4) * Math.random() * 0.2 + 0.8;
  }

  /**
   * Emit real-time metrics update
   */
  private emitMetricsUpdate(sessionId: string, metrics: SessionMetrics): void {
    // In a real implementation, this would emit events for real-time monitoring
    console.log(`📊 Metrics update for session ${sessionId}: Overall immersion ${metrics.immersionScore.overall.toFixed(2)}`);
  }
}

export default ImmersionMetrics;
