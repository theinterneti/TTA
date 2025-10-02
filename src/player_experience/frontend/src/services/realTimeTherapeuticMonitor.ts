import { store } from '../store/store';
import { goalSuggestionEngine } from './goalSuggestionEngine';
import { conflictDetectionService } from './conflictDetectionService';
import { progressTrackingService } from './progressTrackingService';
import { therapeuticSessionService } from './therapeuticSessionService';

// Types for real-time monitoring
export interface EmotionalState {
  valence: number; // -1 to 1 (negative to positive)
  arousal: number; // 0 to 1 (calm to excited)
  dominance: number; // 0 to 1 (submissive to dominant)
  confidence: number; // 0 to 1 (confidence in assessment)
  timestamp: number;
  indicators: string[];
}

export interface RiskAssessment {
  riskLevel: 'low' | 'moderate' | 'high' | 'critical';
  riskScore: number; // 0 to 1
  riskFactors: RiskFactor[];
  protectiveFactors: string[];
  interventionRecommendations: InterventionRecommendation[];
  timestamp: number;
  confidence: number;
}

export interface RiskFactor {
  type: 'behavioral' | 'emotional' | 'cognitive' | 'social' | 'environmental';
  severity: 'low' | 'moderate' | 'high' | 'critical';
  description: string;
  indicators: string[];
  duration: number; // minutes
  trend: 'improving' | 'stable' | 'worsening';
}

export interface InterventionRecommendation {
  type: 'immediate' | 'short_term' | 'long_term';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  intervention: string;
  rationale: string;
  expectedOutcome: string;
  timeframe: string;
  resources: string[];
}

export interface MonitoringSession {
  sessionId: string;
  userId: string;
  startTime: number;
  endTime?: number;
  emotionalStates: EmotionalState[];
  riskAssessments: RiskAssessment[];
  interventions: InterventionRecord[];
  therapeuticGoals: string[];
  sessionContext: Record<string, any>;
}

export interface InterventionRecord {
  interventionId: string;
  type: InterventionRecommendation['type'];
  intervention: string;
  timestamp: number;
  outcome: 'successful' | 'partial' | 'unsuccessful' | 'pending';
  userResponse: string;
  followUpRequired: boolean;
}

export interface MonitoringMetrics {
  averageRiskScore: number;
  emotionalStability: number;
  engagementLevel: number;
  therapeuticProgress: number;
  interventionEffectiveness: number;
  sessionQuality: number;
}

class RealTimeTherapeuticMonitor {
  private activeSessions: Map<string, MonitoringSession> = new Map();
  private monitoringCallbacks: Map<string, (data: any) => void> = new Map();
  private riskThresholds = {
    low: 0.25,
    moderate: 0.5,
    high: 0.75,
    critical: 0.9
  };

  /**
   * Start monitoring a therapeutic session
   */
  startMonitoring(sessionId: string, userId: string, therapeuticGoals: string[]): MonitoringSession {
    const session: MonitoringSession = {
      sessionId,
      userId,
      startTime: Date.now(),
      emotionalStates: [],
      riskAssessments: [],
      interventions: [],
      therapeuticGoals,
      sessionContext: {}
    };

    this.activeSessions.set(sessionId, session);
    return session;
  }

  /**
   * Stop monitoring a therapeutic session
   */
  stopMonitoring(sessionId: string): MonitoringSession | null {
    const session = this.activeSessions.get(sessionId);
    if (session) {
      session.endTime = Date.now();
      this.activeSessions.delete(sessionId);
      return session;
    }
    return null;
  }

  /**
   * Analyze user input for emotional state and risk factors
   */
  async analyzeUserInput(
    sessionId: string, 
    userInput: string, 
    context: Record<string, any> = {}
  ): Promise<{ emotionalState: EmotionalState; riskAssessment: RiskAssessment }> {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error(`No active monitoring session found for ${sessionId}`);
    }

    // Analyze emotional state from user input
    const emotionalState = await this.assessEmotionalState(userInput, context);
    
    // Perform risk assessment
    const riskAssessment = await this.performRiskAssessment(
      sessionId, 
      userInput, 
      emotionalState, 
      context
    );

    // Store in session
    session.emotionalStates.push(emotionalState);
    session.riskAssessments.push(riskAssessment);

    // Trigger interventions if necessary
    if (riskAssessment.riskLevel === 'high' || riskAssessment.riskLevel === 'critical') {
      await this.triggerInterventions(sessionId, riskAssessment);
    }

    // Notify callbacks
    this.notifyCallbacks(sessionId, { emotionalState, riskAssessment });

    return { emotionalState, riskAssessment };
  }

  /**
   * Assess emotional state from user input using NLP and pattern analysis
   */
  private async assessEmotionalState(
    userInput: string, 
    context: Record<string, any>
  ): Promise<EmotionalState> {
    // Emotional indicators based on text analysis
    const indicators: string[] = [];
    let valence = 0; // -1 to 1
    let arousal = 0; // 0 to 1
    let dominance = 0.5; // 0 to 1, default neutral

    // Negative emotion indicators
    const negativeWords = [
      'sad', 'depressed', 'anxious', 'worried', 'scared', 'angry', 'frustrated',
      'hopeless', 'worthless', 'overwhelmed', 'stressed', 'panic', 'fear',
      'hate', 'terrible', 'awful', 'horrible', 'devastating', 'crushing'
    ];

    // Positive emotion indicators
    const positiveWords = [
      'happy', 'joy', 'excited', 'grateful', 'proud', 'confident', 'hopeful',
      'peaceful', 'calm', 'content', 'satisfied', 'amazing', 'wonderful',
      'great', 'fantastic', 'excellent', 'love', 'blessed', 'optimistic'
    ];

    // High arousal indicators
    const highArousalWords = [
      'excited', 'panic', 'frantic', 'energetic', 'intense', 'overwhelming',
      'explosive', 'racing', 'urgent', 'desperate', 'manic', 'hyper',
      'anxious', 'panicked'
    ];

    // Low dominance indicators (feeling powerless)
    const lowDominanceWords = [
      'helpless', 'powerless', 'trapped', 'stuck', 'controlled', 'victim',
      'weak', 'submissive', 'dependent', 'vulnerable', 'defeated'
    ];

    const inputLower = userInput.toLowerCase();

    // Calculate valence
    const negativeCount = negativeWords.filter(word => inputLower.includes(word)).length;
    const positiveCount = positiveWords.filter(word => inputLower.includes(word)).length;
    
    if (negativeCount > 0) {
      valence = Math.max(-1, -0.3 * negativeCount);
      indicators.push(...negativeWords.filter(word => inputLower.includes(word)));
    }
    if (positiveCount > 0) {
      valence = Math.min(1, valence + 0.3 * positiveCount);
      indicators.push(...positiveWords.filter(word => inputLower.includes(word)));
    }

    // Calculate arousal
    const highArousalCount = highArousalWords.filter(word => inputLower.includes(word)).length;
    if (highArousalCount > 0) {
      arousal = Math.min(1, 0.5 + 0.2 * highArousalCount);
      indicators.push(...highArousalWords.filter(word => inputLower.includes(word)));
    }

    // Calculate dominance
    const lowDominanceCount = lowDominanceWords.filter(word => inputLower.includes(word)).length;
    if (lowDominanceCount > 0) {
      dominance = Math.max(0, 0.5 - 0.2 * lowDominanceCount);
      indicators.push(...lowDominanceWords.filter(word => inputLower.includes(word)));
    }

    // Additional context-based adjustments
    if (context.messageLength && context.messageLength < 10) {
      arousal = Math.max(0, arousal - 0.1); // Short messages might indicate low engagement
    }

    if (context.responseTime && context.responseTime > 30000) {
      arousal = Math.max(0, arousal - 0.2); // Long response times might indicate low arousal
    }

    const confidence = Math.min(1, 0.5 + (indicators.length * 0.1));

    return {
      valence,
      arousal,
      dominance,
      confidence,
      timestamp: Date.now(),
      indicators
    };
  }

  /**
   * Perform comprehensive risk assessment
   */
  private async performRiskAssessment(
    sessionId: string,
    userInput: string,
    emotionalState: EmotionalState,
    context: Record<string, any>
  ): Promise<RiskAssessment> {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error(`No active session found for ${sessionId}`);
    }

    const riskFactors: RiskFactor[] = [];
    const protectiveFactors: string[] = [];
    let riskScore = 0;

    // Analyze emotional risk factors
    if (emotionalState.valence < -0.4) {
      riskFactors.push({
        type: 'emotional',
        severity: emotionalState.valence < -0.7 ? 'critical' : emotionalState.valence < -0.5 ? 'high' : 'moderate',
        description: 'Negative emotional state detected',
        indicators: emotionalState.indicators.filter(i =>
          ['sad', 'depressed', 'hopeless', 'worthless'].some(neg => i.includes(neg))
        ),
        duration: this.calculateEmotionalStateDuration(session, 'negative'),
        trend: this.calculateEmotionalTrend(session, 'valence')
      });
      riskScore += emotionalState.valence < -0.7 ? 0.4 : emotionalState.valence < -0.5 ? 0.3 : 0.2;
    }

    // High arousal with negative valence (anxiety, panic)
    if (emotionalState.arousal > 0.7 && emotionalState.valence < -0.3) {
      riskFactors.push({
        type: 'emotional',
        severity: emotionalState.arousal > 0.9 ? 'critical' : 'high',
        description: 'High anxiety or panic state detected',
        indicators: emotionalState.indicators.filter(i => 
          ['panic', 'anxious', 'overwhelmed', 'frantic'].some(anx => i.includes(anx))
        ),
        duration: this.calculateEmotionalStateDuration(session, 'high_arousal'),
        trend: this.calculateEmotionalTrend(session, 'arousal')
      });
      riskScore += 0.35;
    }

    // Low dominance (feeling powerless)
    if (emotionalState.dominance < 0.3) {
      riskFactors.push({
        type: 'cognitive',
        severity: emotionalState.dominance < 0.1 ? 'high' : 'moderate',
        description: 'Feelings of powerlessness or helplessness',
        indicators: emotionalState.indicators.filter(i => 
          ['helpless', 'powerless', 'trapped', 'stuck'].some(pow => i.includes(pow))
        ),
        duration: this.calculateEmotionalStateDuration(session, 'low_dominance'),
        trend: this.calculateEmotionalTrend(session, 'dominance')
      });
      riskScore += 0.25;
    }

    // Crisis language detection
    const crisisIndicators = this.detectCrisisLanguage(userInput);
    if (crisisIndicators.length > 0) {
      riskFactors.push({
        type: 'behavioral',
        severity: 'critical',
        description: 'Crisis language or self-harm indicators detected',
        indicators: crisisIndicators,
        duration: 0, // Immediate concern
        trend: 'worsening'
      });
      riskScore += 0.6;
    }

    // Protective factors
    if (emotionalState.valence > 0.3) {
      protectiveFactors.push('Positive emotional state');
    }
    if (context.therapeuticGoalsProgress && context.therapeuticGoalsProgress > 0.7) {
      protectiveFactors.push('Good therapeutic progress');
    }
    if (context.socialSupport) {
      protectiveFactors.push('Social support available');
    }

    // Adjust risk score based on protective factors
    const protectiveFactor = Math.min(0.3, protectiveFactors.length * 0.1);
    riskScore = Math.max(0, riskScore - protectiveFactor);

    // Determine risk level
    let riskLevel: RiskAssessment['riskLevel'] = 'low';

    // Crisis language always triggers critical risk level
    if (crisisIndicators.length > 0) {
      riskLevel = 'critical';
      riskScore = Math.max(riskScore, 0.95); // Ensure critical risk score
    } else if (riskScore >= this.riskThresholds.critical) {
      riskLevel = 'critical';
    } else if (riskScore >= this.riskThresholds.high) {
      riskLevel = 'high';
    } else if (riskScore >= this.riskThresholds.moderate) {
      riskLevel = 'moderate';
    }

    // Generate intervention recommendations
    const interventionRecommendations = this.generateInterventionRecommendations(
      riskLevel, 
      riskFactors, 
      protectiveFactors
    );

    return {
      riskLevel,
      riskScore,
      riskFactors,
      protectiveFactors,
      interventionRecommendations,
      timestamp: Date.now(),
      confidence: Math.min(1, 0.6 + (riskFactors.length * 0.1))
    };
  }

  /**
   * Detect crisis language patterns
   */
  private detectCrisisLanguage(userInput: string): string[] {
    const crisisPatterns = [
      // Self-harm indicators
      'hurt myself', 'kill myself', 'end it all', 'not worth living',
      'better off dead', 'want to die', 'suicide', 'self harm',
      'cut myself', 'overdose', 'jump off', 'hang myself',

      // Severe distress
      'can\'t take it anymore', 'nothing left', 'no way out',
      'completely hopeless', 'give up', 'end the pain',

      // Crisis situations
      'emergency', 'crisis', 'desperate', 'urgent help'
    ];

    const inputLower = userInput.toLowerCase();
    const detectedPatterns = crisisPatterns.filter(pattern => inputLower.includes(pattern));

    // Also check for individual crisis words that might indicate self-harm
    const crisisWords = ['suicide', 'kill', 'die', 'death', 'hurt'];
    const selfWords = ['myself', 'me', 'i'];

    for (const crisisWord of crisisWords) {
      for (const selfWord of selfWords) {
        if (inputLower.includes(crisisWord) && inputLower.includes(selfWord)) {
          detectedPatterns.push(`${crisisWord} ${selfWord}`);
        }
      }
    }

    return [...new Set(detectedPatterns)]; // Remove duplicates
  }

  /**
   * Calculate duration of specific emotional states
   */
  private calculateEmotionalStateDuration(
    session: MonitoringSession, 
    stateType: 'negative' | 'high_arousal' | 'low_dominance'
  ): number {
    const recentStates = session.emotionalStates.slice(-10); // Last 10 states
    let duration = 0;
    
    for (let i = recentStates.length - 1; i >= 0; i--) {
      const state = recentStates[i];
      let matches = false;
      
      switch (stateType) {
        case 'negative':
          matches = state.valence < -0.3;
          break;
        case 'high_arousal':
          matches = state.arousal > 0.6;
          break;
        case 'low_dominance':
          matches = state.dominance < 0.4;
          break;
      }
      
      if (matches) {
        duration += 1; // Increment by 1 interaction
      } else {
        break; // Stop counting if pattern breaks
      }
    }
    
    return duration * 2; // Approximate 2 minutes per interaction
  }

  /**
   * Calculate emotional trend over recent interactions
   */
  private calculateEmotionalTrend(
    session: MonitoringSession, 
    dimension: 'valence' | 'arousal' | 'dominance'
  ): 'improving' | 'stable' | 'worsening' {
    const recentStates = session.emotionalStates.slice(-5);
    if (recentStates.length < 3) return 'stable';
    
    const values = recentStates.map(state => state[dimension]);
    const firstHalf = values.slice(0, Math.floor(values.length / 2));
    const secondHalf = values.slice(Math.floor(values.length / 2));
    
    const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
    
    const difference = secondAvg - firstAvg;
    
    if (dimension === 'valence' || dimension === 'dominance') {
      // For valence and dominance, higher is better
      if (difference > 0.1) return 'improving';
      if (difference < -0.1) return 'worsening';
    } else {
      // For arousal, moderate levels are better
      const targetArousal = 0.5;
      const firstDistance = Math.abs(firstAvg - targetArousal);
      const secondDistance = Math.abs(secondAvg - targetArousal);
      
      if (secondDistance < firstDistance - 0.1) return 'improving';
      if (secondDistance > firstDistance + 0.1) return 'worsening';
    }
    
    return 'stable';
  }

  /**
   * Generate intervention recommendations based on risk assessment
   */
  private generateInterventionRecommendations(
    riskLevel: RiskAssessment['riskLevel'],
    riskFactors: RiskFactor[],
    protectiveFactors: string[]
  ): InterventionRecommendation[] {
    const recommendations: InterventionRecommendation[] = [];

    if (riskLevel === 'critical') {
      recommendations.push({
        type: 'immediate',
        priority: 'urgent',
        intervention: 'Crisis intervention protocol activation',
        rationale: 'Critical risk level detected requiring immediate professional intervention',
        expectedOutcome: 'Immediate safety and stabilization',
        timeframe: 'Immediate (0-15 minutes)',
        resources: ['Crisis hotline', 'Emergency services', 'Mental health professional']
      });
    }

    if (riskLevel === 'high' || riskLevel === 'critical') {
      recommendations.push({
        type: 'immediate',
        priority: 'high',
        intervention: 'Grounding and stabilization techniques',
        rationale: 'High emotional distress requires immediate coping strategies',
        expectedOutcome: 'Reduced emotional intensity and improved stability',
        timeframe: 'Immediate (0-30 minutes)',
        resources: ['Breathing exercises', 'Grounding techniques', 'Mindfulness practices']
      });
    }

    if (riskFactors.some(rf => rf.type === 'emotional' && (rf.severity === 'high' || rf.severity === 'moderate'))) {
      recommendations.push({
        type: 'short_term',
        priority: riskFactors.some(rf => rf.severity === 'high') ? 'high' : 'medium',
        intervention: 'Emotional regulation support',
        rationale: 'Emotional distress requires targeted emotional support',
        expectedOutcome: 'Improved emotional regulation and coping',
        timeframe: 'Short-term (1-24 hours)',
        resources: ['Therapeutic techniques', 'Coping strategies', 'Support network']
      });
    }

    if (riskLevel === 'moderate') {
      recommendations.push({
        type: 'short_term',
        priority: 'medium',
        intervention: 'Enhanced therapeutic support',
        rationale: 'Moderate risk requires increased therapeutic attention',
        expectedOutcome: 'Risk reduction and improved therapeutic progress',
        timeframe: 'Short-term (1-7 days)',
        resources: ['Increased session frequency', 'Therapeutic homework', 'Progress monitoring']
      });
    }

    return recommendations;
  }

  /**
   * Trigger interventions based on risk assessment
   */
  private async triggerInterventions(
    sessionId: string, 
    riskAssessment: RiskAssessment
  ): Promise<void> {
    const session = this.activeSessions.get(sessionId);
    if (!session) return;

    for (const recommendation of riskAssessment.interventionRecommendations) {
      if (recommendation.priority === 'urgent' || recommendation.priority === 'high') {
        // Create intervention record
        const intervention: InterventionRecord = {
          interventionId: `int_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          type: recommendation.type,
          intervention: recommendation.intervention,
          timestamp: Date.now(),
          outcome: 'pending',
          userResponse: '',
          followUpRequired: true
        };

        session.interventions.push(intervention);

        // Notify monitoring callbacks about intervention
        this.notifyCallbacks(sessionId, {
          type: 'intervention_triggered',
          intervention,
          riskAssessment
        });
      }
    }
  }

  /**
   * Register callback for monitoring updates
   */
  registerCallback(sessionId: string, callback: (data: any) => void): void {
    this.monitoringCallbacks.set(sessionId, callback);
  }

  /**
   * Unregister monitoring callback
   */
  unregisterCallback(sessionId: string): void {
    this.monitoringCallbacks.delete(sessionId);
  }

  /**
   * Notify registered callbacks
   */
  private notifyCallbacks(sessionId: string, data: any): void {
    const callback = this.monitoringCallbacks.get(sessionId);
    if (callback) {
      try {
        callback(data);
      } catch (error) {
        console.error('Error in monitoring callback:', error);
      }
    }
  }

  /**
   * Get current monitoring metrics for a session
   */
  getMonitoringMetrics(sessionId: string): MonitoringMetrics | null {
    const session = this.activeSessions.get(sessionId);
    if (!session) return null;

    const recentStates = session.emotionalStates.slice(-10);
    const recentRisks = session.riskAssessments.slice(-10);

    if (recentStates.length === 0) {
      return {
        averageRiskScore: 0,
        emotionalStability: 0.5,
        engagementLevel: 0.5,
        therapeuticProgress: 0.5,
        interventionEffectiveness: 0.5,
        sessionQuality: 0.5
      };
    }

    const averageRiskScore = recentRisks.reduce((sum, risk) => sum + risk.riskScore, 0) / recentRisks.length;
    
    const valenceVariance = this.calculateVariance(recentStates.map(s => s.valence));
    const emotionalStability = Math.max(0, 1 - valenceVariance);
    
    const averageConfidence = recentStates.reduce((sum, state) => sum + state.confidence, 0) / recentStates.length;
    const engagementLevel = averageConfidence;
    
    // Calculate therapeutic progress (placeholder - would integrate with actual progress data)
    const therapeuticProgress = 0.7; // Would be calculated from actual therapeutic goals progress
    
    // Calculate intervention effectiveness
    const successfulInterventions = session.interventions.filter(i => i.outcome === 'successful').length;
    const totalInterventions = session.interventions.length;
    const interventionEffectiveness = totalInterventions > 0 ? successfulInterventions / totalInterventions : 0.5;
    
    // Overall session quality
    const sessionQuality = (emotionalStability + engagementLevel + therapeuticProgress + interventionEffectiveness) / 4;

    return {
      averageRiskScore,
      emotionalStability,
      engagementLevel,
      therapeuticProgress,
      interventionEffectiveness,
      sessionQuality
    };
  }

  /**
   * Calculate variance for emotional stability metrics
   */
  private calculateVariance(values: number[]): number {
    if (values.length === 0) return 0;
    
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const squaredDifferences = values.map(val => Math.pow(val - mean, 2));
    return squaredDifferences.reduce((sum, val) => sum + val, 0) / values.length;
  }

  /**
   * Get active monitoring sessions
   */
  getActiveSessions(): MonitoringSession[] {
    return Array.from(this.activeSessions.values());
  }

  /**
   * Get session by ID
   */
  getSession(sessionId: string): MonitoringSession | null {
    return this.activeSessions.get(sessionId) || null;
  }
}

export const realTimeTherapeuticMonitor = new RealTimeTherapeuticMonitor();
export default realTimeTherapeuticMonitor;
