/**
 * Results Analyzer
 *
 * Analyzes simulation results and generates comprehensive reports
 * with insights, recommendations, and statistical analysis.
 */

import {
  SimulationResults,
  SimulationStatistics,
  PersonaStatistics,
  SessionQualityAssessment,
  WorldQualityAssessment,
  ComparativeAnalysis,
  AnalysisConfig,
  ReportGenerationOptions
} from '../types/SimulationTypes';
import { PersonaType } from '../personas/UserPersonas';
import { SessionMetrics } from '../metrics/ImmersionMetrics';
import { WorldTestResult } from '../world/WorldGenerationTester';
import { ScenarioTestResult } from '../scenarios/SessionScenarios';

export class ResultsAnalyzer {
  private config: AnalysisConfig;

  constructor(config: AnalysisConfig) {
    this.config = config;
  }

  /**
   * Analyze complete simulation results
   */
  async analyzeResults(results: SimulationResults): Promise<AnalysisReport> {
    console.log('📊 Analyzing simulation results...');

    const startTime = Date.now();

    // Calculate comprehensive statistics
    const statistics = this.calculateStatistics(results);
    results.statistics = statistics;

    // Assess session quality
    const sessionAssessments = this.assessSessionQuality(results);

    // Assess world generation quality
    const worldAssessments = this.assessWorldQuality(results.worldGenerationTests);

    // Generate persona-specific insights
    const personaInsights = this.generatePersonaInsights(results);

    // Generate scenario insights
    const scenarioInsights = this.generateScenarioInsights(results);

    // Generate overall recommendations
    const recommendations = this.generateRecommendations(results, sessionAssessments, worldAssessments);

    // Calculate success criteria
    const successCriteria = this.evaluateSuccessCriteria(results);

    const analysisTime = Date.now() - startTime;

    const report: AnalysisReport = {
      timestamp: Date.now(),
      analysisTime,
      overallScores: results.overallScores,
      statistics,
      sessionAssessments,
      worldAssessments,
      personaInsights,
      scenarioInsights,
      recommendations,
      successCriteria,
      keyFindings: this.extractKeyFindings(results, statistics),
      improvementPriorities: this.identifyImprovementPriorities(results, recommendations)
    };

    console.log(`✅ Analysis completed in ${analysisTime}ms`);
    return report;
  }

  /**
   * Calculate comprehensive statistics
   */
  private calculateStatistics(results: SimulationResults): SimulationStatistics {
    const allSessions = results.personaSimulations.map(p => p.sessionMetrics);
    const allScenarios = results.sessionPatternTests;

    // Basic counts
    const totalSessions = allSessions.length;
    const totalPersonas = new Set(allSessions.map(s => s.personaType)).size;
    const totalScenarios = new Set(allScenarios.map(s => s.scenarioId)).size;
    const totalWorldTests = results.worldGenerationTests.length;

    // Duration statistics
    const durations = allSessions.map(s => s.duration);
    const averageSessionDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
    const sortedDurations = durations.sort((a, b) => a - b);
    const medianSessionDuration = sortedDurations[Math.floor(sortedDurations.length / 2)];
    const shortestSession = Math.min(...durations);
    const longestSession = Math.max(...durations);

    // Engagement statistics
    const engagements = allSessions.map(s => s.immersionScore.engagementSustainability);
    const averageEngagement = engagements.reduce((sum, e) => sum + e, 0) / engagements.length;
    const engagementStandardDeviation = this.calculateStandardDeviation(engagements);
    const highEngagementSessions = engagements.filter(e => e > 0.8).length;
    const lowEngagementSessions = engagements.filter(e => e < 0.5).length;

    // Immersion statistics
    const immersions = allSessions.map(s => s.immersionScore.overall);
    const averageImmersion = immersions.reduce((sum, i) => sum + i, 0) / immersions.length;
    const immersionStandardDeviation = this.calculateStandardDeviation(immersions);
    const highImmersionSessions = immersions.filter(i => i > 0.8).length;
    const lowImmersionSessions = immersions.filter(i => i < 0.5).length;

    // Therapeutic statistics
    const therapeuticBenefits = allSessions.map(s => s.therapeuticBenefit);
    const averageTherapeuticBenefit = therapeuticBenefits.reduce((sum, t) => sum + t, 0) / therapeuticBenefits.length;
    const therapeuticBenefitStandardDeviation = this.calculateStandardDeviation(therapeuticBenefits);
    const highTherapeuticSessions = therapeuticBenefits.filter(t => t > 0.8).length;

    // Entertainment statistics
    const entertainmentValues = allSessions.map(s => s.entertainmentValue);
    const averageEntertainmentValue = entertainmentValues.reduce((sum, e) => sum + e, 0) / entertainmentValues.length;
    const entertainmentValueStandardDeviation = this.calculateStandardDeviation(entertainmentValues);
    const highEntertainmentSessions = entertainmentValues.filter(e => e > 0.8).length;

    // Success rates
    const scenarioSuccessRate = (allScenarios.filter(s => s.meetsExpectations).length / allScenarios.length) * 100;
    const personaSuccessRate = (results.personaSimulations.filter(p =>
      p.overallPerformance.averageEngagement > 0.7
    ).length / results.personaSimulations.length) * 100;
    const worldGenerationSuccessRate = (results.worldGenerationTests.filter(w =>
      w.overallScore > 0.7
    ).length / results.worldGenerationTests.length) * 100;

    // Persona-specific statistics
    const personaStatistics = this.calculatePersonaStatistics(results);

    return {
      totalSessions,
      totalPersonas,
      totalScenarios,
      totalWorldTests,
      averageSessionDuration,
      medianSessionDuration,
      shortestSession,
      longestSession,
      averageEngagement,
      engagementStandardDeviation,
      highEngagementSessions,
      lowEngagementSessions,
      averageImmersion,
      immersionStandardDeviation,
      highImmersionSessions,
      lowImmersionSessions,
      averageTherapeuticBenefit,
      therapeuticBenefitStandardDeviation,
      highTherapeuticSessions,
      averageEntertainmentValue,
      entertainmentValueStandardDeviation,
      highEntertainmentSessions,
      scenarioSuccessRate,
      personaSuccessRate,
      worldGenerationSuccessRate,
      personaStatistics
    };
  }

  /**
   * Calculate persona-specific statistics
   */
  private calculatePersonaStatistics(results: SimulationResults): Record<PersonaType, PersonaStatistics> {
    const personaStats: Record<PersonaType, PersonaStatistics> = {} as any;

    for (const personaType of Object.values(PersonaType)) {
      const personaSessions = results.personaSimulations.filter(p => p.personaType === personaType);

      if (personaSessions.length === 0) continue;

      const sessions = personaSessions.map(p => p.sessionMetrics);
      const scenarioResults = personaSessions.flatMap(p => p.scenarioResults);

      const sessionCount = sessions.length;
      const averageDuration = sessions.reduce((sum, s) => sum + s.duration, 0) / sessionCount;
      const averageEngagement = sessions.reduce((sum, s) => sum + s.immersionScore.engagementSustainability, 0) / sessionCount;
      const averageImmersion = sessions.reduce((sum, s) => sum + s.immersionScore.overall, 0) / sessionCount;
      const averageTherapeuticBenefit = sessions.reduce((sum, s) => sum + s.therapeuticBenefit, 0) / sessionCount;
      const averageEntertainmentValue = sessions.reduce((sum, s) => sum + s.entertainmentValue, 0) / sessionCount;
      const completionRate = scenarioResults.filter(s => s.completionRate > 0.8).length / scenarioResults.length;

      // Find most and least successful scenarios
      const scenarioPerformance = new Map<string, number[]>();
      scenarioResults.forEach(result => {
        if (!scenarioPerformance.has(result.scenarioId)) {
          scenarioPerformance.set(result.scenarioId, []);
        }
        scenarioPerformance.get(result.scenarioId)!.push(result.engagementScore);
      });

      const scenarioAverages = Array.from(scenarioPerformance.entries()).map(([id, scores]) => ({
        scenarioId: id,
        averageScore: scores.reduce((sum, score) => sum + score, 0) / scores.length
      }));

      scenarioAverages.sort((a, b) => b.averageScore - a.averageScore);
      const mostSuccessfulScenarios = scenarioAverages.slice(0, 3).map(s => s.scenarioId);
      const leastSuccessfulScenarios = scenarioAverages.slice(-3).map(s => s.scenarioId);

      const recommendedImprovements = this.generatePersonaRecommendations(personaType, {
        averageEngagement,
        averageImmersion,
        averageTherapeuticBenefit,
        averageEntertainmentValue,
        completionRate
      });

      personaStats[personaType] = {
        sessionCount,
        averageDuration,
        averageEngagement,
        averageImmersion,
        averageTherapeuticBenefit,
        averageEntertainmentValue,
        completionRate,
        mostSuccessfulScenarios,
        leastSuccessfulScenarios,
        recommendedImprovements
      };
    }

    return personaStats;
  }

  /**
   * Assess session quality
   */
  private assessSessionQuality(results: SimulationResults): SessionQualityAssessment[] {
    const assessments: SessionQualityAssessment[] = [];

    results.personaSimulations.forEach(personaResult => {
      personaResult.scenarioResults.forEach(scenarioResult => {
        const session = personaResult.sessionMetrics;

        const qualityScore = (
          scenarioResult.engagementScore * 0.25 +
          scenarioResult.immersionScore * 0.25 +
          scenarioResult.therapeuticBenefit * 0.25 +
          scenarioResult.entertainmentValue * 0.25
        );

        const assessment: SessionQualityAssessment = {
          sessionId: scenarioResult.sessionId,
          personaType: scenarioResult.personaType,
          scenarioId: scenarioResult.scenarioId,
          qualityScore,
          engagementQuality: scenarioResult.engagementScore,
          immersionQuality: scenarioResult.immersionScore,
          therapeuticQuality: scenarioResult.therapeuticBenefit,
          entertainmentQuality: scenarioResult.entertainmentValue,
          meetsPersonaNeeds: this.assessPersonaNeedsFulfillment(personaResult.personaType, scenarioResult),
          meetsScenarioExpectations: scenarioResult.meetsExpectations,
          improvementAreas: this.identifySessionImprovementAreas(scenarioResult)
        };

        assessments.push(assessment);
      });
    });

    return assessments;
  }

  /**
   * Assess world generation quality
   */
  private assessWorldQuality(worldTests: WorldTestResult[]): WorldQualityAssessment[] {
    return worldTests.map(test => ({
      worldId: test.worldId,
      overallQuality: test.overallScore,
      systemQuality: test.systems.reduce((acc, system) => {
        acc[system.name] = (system.coherence + system.depth + system.believability) / 3;
        return acc;
      }, {} as Record<string, number>),
      coherenceScore: test.systems.reduce((sum, s) => sum + s.coherence, 0) / test.systems.length,
      depthScore: test.systems.reduce((sum, s) => sum + s.depth, 0) / test.systems.length,
      believabilityScore: test.systems.reduce((sum, s) => sum + s.believability, 0) / test.systems.length,
      interconnectednessScore: test.systems.reduce((sum, s) => sum + s.interconnectedness, 0) / test.systems.length,
      strengths: test.strengths,
      weaknesses: test.weaknesses,
      recommendations: test.recommendations
    }));
  }

  /**
   * Generate persona insights
   */
  private generatePersonaInsights(results: SimulationResults): Record<PersonaType, string[]> {
    const insights: Record<PersonaType, string[]> = {} as any;

    Object.entries(results.statistics.personaStatistics).forEach(([personaType, stats]) => {
      const personaInsights: string[] = [];

      if (stats.averageEngagement > 0.8) {
        personaInsights.push(`${personaType} shows excellent engagement levels (${stats.averageEngagement.toFixed(2)})`);
      } else if (stats.averageEngagement < 0.6) {
        personaInsights.push(`${personaType} struggles with engagement (${stats.averageEngagement.toFixed(2)}) - needs attention`);
      }

      if (stats.completionRate > 0.8) {
        personaInsights.push(`High completion rate (${(stats.completionRate * 100).toFixed(1)}%) indicates good session design`);
      } else if (stats.completionRate < 0.6) {
        personaInsights.push(`Low completion rate (${(stats.completionRate * 100).toFixed(1)}%) suggests sessions may be too long or complex`);
      }

      if (stats.averageTherapeuticBenefit > 0.8) {
        personaInsights.push(`Excellent therapeutic integration for ${personaType}`);
      }

      insights[personaType as PersonaType] = personaInsights;
    });

    return insights;
  }

  /**
   * Generate scenario insights
   */
  private generateScenarioInsights(results: SimulationResults): Record<string, string[]> {
    const insights: Record<string, string[]> = {};

    // Group scenario results by scenario ID
    const scenarioGroups = new Map<string, ScenarioTestResult[]>();
    results.sessionPatternTests.forEach(result => {
      if (!scenarioGroups.has(result.scenarioId)) {
        scenarioGroups.set(result.scenarioId, []);
      }
      scenarioGroups.get(result.scenarioId)!.push(result);
    });

    scenarioGroups.forEach((results, scenarioId) => {
      const scenarioInsights: string[] = [];

      const averageEngagement = results.reduce((sum, r) => sum + r.engagementScore, 0) / results.length;
      const successRate = results.filter(r => r.meetsExpectations).length / results.length;

      if (averageEngagement > 0.8) {
        scenarioInsights.push(`High engagement scenario (${averageEngagement.toFixed(2)}) - good entertainment value`);
      } else if (averageEngagement < 0.6) {
        scenarioInsights.push(`Low engagement scenario (${averageEngagement.toFixed(2)}) - needs improvement`);
      }

      if (successRate > 0.8) {
        scenarioInsights.push(`High success rate (${(successRate * 100).toFixed(1)}%) - well-designed scenario`);
      } else if (successRate < 0.6) {
        scenarioInsights.push(`Low success rate (${(successRate * 100).toFixed(1)}%) - requires redesign`);
      }

      insights[scenarioId] = scenarioInsights;
    });

    return insights;
  }

  /**
   * Generate comprehensive recommendations
   */
  private generateRecommendations(
    results: SimulationResults,
    sessionAssessments: SessionQualityAssessment[],
    worldAssessments: WorldQualityAssessment[]
  ): string[] {
    const recommendations: string[] = [];

    // Overall performance recommendations
    if (results.overallScores.engagementScore < 0.7) {
      recommendations.push('Improve overall engagement through better pacing and interactive elements');
    }

    if (results.overallScores.immersionScore < 0.7) {
      recommendations.push('Enhance immersion through improved narrative coherence and world consistency');
    }

    if (results.overallScores.therapeuticIntegrationScore < 0.8) {
      recommendations.push('Better integrate therapeutic elements to maintain entertainment-first approach');
    }

    // Session-specific recommendations
    const lowQualitySessions = sessionAssessments.filter(s => s.qualityScore < 0.6);
    if (lowQualitySessions.length > sessionAssessments.length * 0.2) {
      recommendations.push('Address session quality issues - over 20% of sessions are below quality threshold');
    }

    // World generation recommendations
    const lowQualityWorlds = worldAssessments.filter(w => w.overallQuality < 0.7);
    if (lowQualityWorlds.length > worldAssessments.length * 0.3) {
      recommendations.push('Improve world generation algorithms - too many worlds below quality standards');
    }

    // Persona-specific recommendations
    Object.entries(results.statistics.personaStatistics).forEach(([personaType, stats]) => {
      if (stats.averageEngagement < 0.6) {
        recommendations.push(`Improve experience for ${personaType} - low engagement detected`);
      }
    });

    return recommendations;
  }

  /**
   * Evaluate success criteria
   */
  private evaluateSuccessCriteria(results: SimulationResults): Record<string, boolean> {
    return {
      worldGenerationQuality: results.overallScores.worldGenerationScore >= 0.8,
      immersionQuality: results.overallScores.immersionScore >= 0.8,
      engagementSustainability: results.overallScores.engagementScore >= 0.7,
      therapeuticIntegration: results.overallScores.therapeuticIntegrationScore >= 0.8,
      entertainmentValue: results.overallScores.entertainmentValueScore >= 0.8,
      overallSuccess: Object.values(results.overallScores).every(score => score >= 0.7)
    };
  }

  /**
   * Extract key findings
   */
  private extractKeyFindings(results: SimulationResults, statistics: SimulationStatistics): string[] {
    const findings: string[] = [];

    // Performance findings
    if (statistics.averageEngagement > 0.8) {
      findings.push(`Excellent average engagement (${statistics.averageEngagement.toFixed(2)}) across all sessions`);
    }

    if (statistics.scenarioSuccessRate > 80) {
      findings.push(`High scenario success rate (${statistics.scenarioSuccessRate.toFixed(1)}%) indicates good design`);
    }

    if (statistics.highTherapeuticSessions > statistics.totalSessions * 0.6) {
      findings.push(`Strong therapeutic integration - ${statistics.highTherapeuticSessions} sessions with high therapeutic benefit`);
    }

    // Persona findings
    const bestPersona = Object.entries(statistics.personaStatistics)
      .sort(([,a], [,b]) => b.averageEngagement - a.averageEngagement)[0];
    if (bestPersona) {
      findings.push(`${bestPersona[0]} persona shows best overall performance`);
    }

    return findings;
  }

  /**
   * Identify improvement priorities
   */
  private identifyImprovementPriorities(results: SimulationResults, recommendations: string[]): string[] {
    const priorities: string[] = [];

    // High priority: Critical failures
    if (results.overallScores.engagementScore < 0.6) {
      priorities.push('CRITICAL: Fix engagement issues immediately');
    }

    if (results.overallScores.therapeuticIntegrationScore < 0.7) {
      priorities.push('HIGH: Improve therapeutic integration subtlety');
    }

    // Medium priority: Quality improvements
    if (results.statistics.scenarioSuccessRate < 70) {
      priorities.push('MEDIUM: Redesign failing scenarios');
    }

    // Low priority: Optimizations
    if (results.overallScores.entertainmentValueScore < 0.9) {
      priorities.push('LOW: Optimize entertainment value');
    }

    return priorities;
  }

  // Helper methods
  private calculateStandardDeviation(values: number[]): number {
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
    const avgSquaredDiff = squaredDiffs.reduce((sum, val) => sum + val, 0) / squaredDiffs.length;
    return Math.sqrt(avgSquaredDiff);
  }

  private assessPersonaNeedsFulfillment(personaType: PersonaType, result: ScenarioTestResult): boolean {
    // Mock implementation - would assess if scenario meets persona's specific needs
    return result.engagementScore > 0.7 && result.therapeuticBenefit > 0.6;
  }

  private identifySessionImprovementAreas(result: ScenarioTestResult): string[] {
    const areas: string[] = [];

    if (result.engagementScore < 0.7) areas.push('Engagement');
    if (result.immersionScore < 0.7) areas.push('Immersion');
    if (result.therapeuticBenefit < 0.7) areas.push('Therapeutic Integration');
    if (result.entertainmentValue < 0.8) areas.push('Entertainment Value');

    return areas;
  }

  private generatePersonaRecommendations(personaType: PersonaType, metrics: any): string[] {
    const recommendations: string[] = [];

    if (metrics.averageEngagement < 0.7) {
      recommendations.push(`Increase engagement elements suitable for ${personaType}`);
    }

    if (metrics.completionRate < 0.8) {
      recommendations.push(`Adjust session length/complexity for ${personaType}`);
    }

    return recommendations;
  }
}

/**
 * Analysis report interface
 */
export interface AnalysisReport {
  timestamp: number;
  analysisTime: number;
  overallScores: any;
  statistics: SimulationStatistics;
  sessionAssessments: SessionQualityAssessment[];
  worldAssessments: WorldQualityAssessment[];
  personaInsights: Record<PersonaType, string[]>;
  scenarioInsights: Record<string, string[]>;
  recommendations: string[];
  successCriteria: Record<string, boolean>;
  keyFindings: string[];
  improvementPriorities: string[];
}

export default ResultsAnalyzer;
