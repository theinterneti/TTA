/**
 * Simulation Types
 *
 * Type definitions for the TTA simulation testing framework
 */

import { WorldTestResult } from '../world/WorldGenerationTester';
import { SessionMetrics, ImmersionScore } from '../metrics/ImmersionMetrics';
import { ScenarioTestResult } from '../scenarios/SessionScenarios';
import { PersonaType } from '../personas/UserPersonas';

/**
 * Overall simulation results
 */
export interface SimulationResults {
  startTime: number;
  endTime: number;
  totalDuration: number; // milliseconds

  // Test results by category
  worldGenerationTests: WorldTestResult[];
  personaSimulations: PersonaSimulationResult[];
  sessionPatternTests: ScenarioTestResult[];
  multiSessionTests: MultiSessionTestResult[];

  // Aggregate scores
  overallScores: OverallScores;

  // Success criteria evaluation
  successCriteria: Record<string, boolean>;

  // Improvement recommendations
  recommendations: string[];

  // Statistical summary
  statistics: SimulationStatistics;
}

/**
 * Overall scoring metrics
 */
export interface OverallScores {
  worldGenerationScore: number; // 0-1 scale
  immersionScore: number; // 0-1 scale
  engagementScore: number; // 0-1 scale
  therapeuticIntegrationScore: number; // 0-1 scale
  entertainmentValueScore: number; // 0-1 scale
}

/**
 * Results from persona-based simulations
 */
export interface PersonaSimulationResult {
  personaType: PersonaType;
  personaId: string;
  sessionMetrics: SessionMetrics;
  scenarioResults: ScenarioTestResult[];
  overallPerformance: PersonaPerformance;
  timestamp: number;
}

/**
 * Performance metrics for a specific persona
 */
export interface PersonaPerformance {
  averageEngagement: number;
  averageImmersion: number;
  averageTherapeuticBenefit: number;
  averageEntertainmentValue: number;
  sessionCompletionRate: number;
  returnProbability: number;
  recommendationLikelihood: number;
  preferredScenarios: string[];
  problematicScenarios: string[];
}

/**
 * Multi-session continuity test results
 */
export interface MultiSessionTestResult {
  testId: string;
  personaType: PersonaType;
  sessionCount: number;
  totalDuration: number; // minutes
  sessions: SessionContinuityData[];
  storyArcProgression: number; // 0-1 scale
  worldStatePersistence: number; // 0-1 scale
  characterDevelopmentContinuity: number; // 0-1 scale
  overallContinuityScore: number; // 0-1 scale
  timestamp: number;
}

/**
 * Individual session data for continuity testing
 */
export interface SessionContinuityData {
  sessionId: string;
  sessionNumber: number;
  duration: number; // minutes
  storyProgression: number; // 0-1 scale
  characterGrowth: number; // 0-1 scale
  worldStateChanges: number; // 0-1 scale
  continuityFromPrevious: number; // 0-1 scale
  immersionScore: ImmersionScore;
}

/**
 * Statistical summary of simulation results
 */
export interface SimulationStatistics {
  totalSessions: number;
  totalPersonas: number;
  totalScenarios: number;
  totalWorldTests: number;

  // Duration statistics
  averageSessionDuration: number; // minutes
  medianSessionDuration: number; // minutes
  shortestSession: number; // minutes
  longestSession: number; // minutes

  // Engagement statistics
  averageEngagement: number;
  engagementStandardDeviation: number;
  highEngagementSessions: number; // sessions with >0.8 engagement
  lowEngagementSessions: number; // sessions with <0.5 engagement

  // Immersion statistics
  averageImmersion: number;
  immersionStandardDeviation: number;
  highImmersionSessions: number; // sessions with >0.8 immersion
  lowImmersionSessions: number; // sessions with <0.5 immersion

  // Therapeutic statistics
  averageTherapeuticBenefit: number;
  therapeuticBenefitStandardDeviation: number;
  highTherapeuticSessions: number; // sessions with >0.8 therapeutic benefit

  // Entertainment statistics
  averageEntertainmentValue: number;
  entertainmentValueStandardDeviation: number;
  highEntertainmentSessions: number; // sessions with >0.8 entertainment value

  // Success rates
  scenarioSuccessRate: number; // percentage of scenarios meeting expectations
  personaSuccessRate: number; // percentage of personas having positive experiences
  worldGenerationSuccessRate: number; // percentage of worlds meeting quality standards

  // Persona-specific statistics
  personaStatistics: Record<PersonaType, PersonaStatistics>;
}

/**
 * Statistics for a specific persona type
 */
export interface PersonaStatistics {
  sessionCount: number;
  averageDuration: number;
  averageEngagement: number;
  averageImmersion: number;
  averageTherapeuticBenefit: number;
  averageEntertainmentValue: number;
  completionRate: number;
  mostSuccessfulScenarios: string[];
  leastSuccessfulScenarios: string[];
  recommendedImprovements: string[];
}

/**
 * Test results interface (generic)
 */
export interface TestResults {
  testId: string;
  testType: string;
  success: boolean;
  score: number; // 0-1 scale
  duration: number; // milliseconds
  details: Record<string, any>;
  timestamp: number;
}

/**
 * World generation quality assessment
 */
export interface WorldQualityAssessment {
  worldId: string;
  overallQuality: number; // 0-1 scale
  systemQuality: Record<string, number>; // quality scores for each system
  coherenceScore: number;
  depthScore: number;
  believabilityScore: number;
  interconnectednessScore: number;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

/**
 * Session quality assessment
 */
export interface SessionQualityAssessment {
  sessionId: string;
  personaType: PersonaType;
  scenarioId: string;
  qualityScore: number; // 0-1 scale
  engagementQuality: number;
  immersionQuality: number;
  therapeuticQuality: number;
  entertainmentQuality: number;
  meetsPersonaNeeds: boolean;
  meetsScenarioExpectations: boolean;
  improvementAreas: string[];
}

/**
 * Comparative analysis between different test runs
 */
export interface ComparativeAnalysis {
  baselineResults: SimulationResults;
  comparisonResults: SimulationResults;
  improvements: Record<string, number>; // metric name -> improvement percentage
  regressions: Record<string, number>; // metric name -> regression percentage
  significantChanges: string[];
  recommendations: string[];
}

/**
 * Real-time simulation monitoring data
 */
export interface SimulationMonitoringData {
  timestamp: number;
  activeSessions: number;
  completedSessions: number;
  averageEngagement: number;
  averageImmersion: number;
  currentPhase: string;
  estimatedTimeRemaining: number; // milliseconds
  recentEvents: SimulationEvent[];
}

/**
 * Simulation events for monitoring and logging
 */
export interface SimulationEvent {
  timestamp: number;
  type: 'session_started' | 'session_completed' | 'world_generated' | 'scenario_tested' | 'error' | 'milestone';
  sessionId?: string;
  personaType?: PersonaType;
  scenarioId?: string;
  worldId?: string;
  message: string;
  data?: Record<string, any>;
}

/**
 * Configuration for simulation analysis
 */
export interface AnalysisConfig {
  includeDetailedBreakdown: boolean;
  generateVisualReports: boolean;
  compareWithBaseline: boolean;
  baselineResultsPath?: string;
  exportFormat: 'json' | 'csv' | 'html' | 'pdf';
  includeRawData: boolean;
  confidenceLevel: number; // for statistical analysis
}

/**
 * Simulation performance metrics
 */
export interface SimulationPerformanceMetrics {
  totalExecutionTime: number; // milliseconds
  averageSessionSimulationTime: number; // milliseconds
  worldGenerationTime: number; // milliseconds
  metricsCalculationTime: number; // milliseconds
  memoryUsage: number; // bytes
  cpuUsage: number; // percentage
  concurrentSessionsHandled: number;
  errorsEncountered: number;
  warningsGenerated: number;
}

/**
 * Quality thresholds for pass/fail determination
 */
export interface QualityThresholds {
  minimumEngagement: number;
  minimumImmersion: number;
  minimumTherapeuticBenefit: number;
  minimumEntertainmentValue: number;
  minimumWorldQuality: number;
  minimumScenarioSuccessRate: number;
  minimumPersonaSuccessRate: number;
  maximumCognitiveLoad: number;
}

/**
 * Simulation configuration validation result
 */
export interface ConfigValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  recommendations: string[];
}

/**
 * Export data structure for external analysis
 */
export interface SimulationExportData {
  metadata: {
    exportTimestamp: number;
    simulationVersion: string;
    configurationHash: string;
    totalSessions: number;
    totalDuration: number;
  };
  results: SimulationResults;
  rawData: {
    sessionMetrics: SessionMetrics[];
    worldTests: WorldTestResult[];
    scenarioTests: ScenarioTestResult[];
  };
  analysis: {
    statistics: SimulationStatistics;
    qualityAssessments: SessionQualityAssessment[];
    recommendations: string[];
  };
}

/**
 * Simulation report generation options
 */
export interface ReportGenerationOptions {
  includeExecutiveSummary: boolean;
  includeDetailedMetrics: boolean;
  includePersonaBreakdown: boolean;
  includeScenarioAnalysis: boolean;
  includeWorldGenerationResults: boolean;
  includeRecommendations: boolean;
  includeVisualCharts: boolean;
  includeRawData: boolean;
  format: 'html' | 'pdf' | 'markdown' | 'json';
  outputPath: string;
}

export default SimulationResults;
