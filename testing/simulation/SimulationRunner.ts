/**
 * TTA Simulation Runner
 *
 * Main entry point for running comprehensive TTA simulation testing.
 * Orchestrates all simulation components and generates final reports.
 */

import { SimulationEngine, SimulationConfig } from './core/SimulationEngine';
import { PersonaType } from './personas/UserPersonas';
import { SessionPattern, SessionScenarios } from './scenarios/SessionScenarios';
import { ResultsAnalyzer, AnalysisReport } from './analysis/ResultsAnalyzer';
import { SimulationResults, AnalysisConfig, ReportGenerationOptions } from './types/SimulationTypes';
import { ImmersionMetrics } from './metrics/ImmersionMetrics';

/**
 * Get default session patterns
 */
function getDefaultSessionPatterns(): SessionPattern[] {
  const metricsCollector = new ImmersionMetrics();
  const sessionScenarios = new SessionScenarios(metricsCollector);
  return sessionScenarios.getAllScenarios().map(scenario => scenario.pattern);
}

/**
 * Predefined simulation configurations
 */
export const SIMULATION_CONFIGS = {
  // Quick validation test (15 minutes)
  QUICK_TEST: {
    maxSimulationDuration: 15 * 60 * 1000, // 15 minutes
    maxConcurrentSessions: 5,
    enabledPersonas: [PersonaType.CASUAL_EXPLORER, PersonaType.SKEPTICAL_NEWCOMER],
    personaDistribution: {
      [PersonaType.CASUAL_EXPLORER]: 60,
      [PersonaType.SKEPTICAL_NEWCOMER]: 40,
      [PersonaType.STORY_ENTHUSIAST]: 0,
      [PersonaType.WORLD_BUILDER]: 0,
      [PersonaType.MARATHON_PLAYER]: 0,
      [PersonaType.SOCIAL_CONNECTOR]: 0,
      [PersonaType.ACHIEVEMENT_HUNTER]: 0,
      [PersonaType.THERAPEUTIC_SEEKER]: 0
    },
    worldComplexityLevels: ['simple', 'moderate'] as const,
    worldSystemsToTest: ['cultural', 'environmental', 'social'],
    sessionPatterns: [
      {
        name: 'Quick Test Pattern',
        description: 'Fast validation pattern',
        targetDuration: 10,
        minDuration: 5,
        maxDuration: 15,
        interactionDensity: 2.0,
        complexityLevel: 'low' as const,
        therapeuticFocus: 0.5,
        entertainmentFocus: 0.8,
        suitablePersonas: [PersonaType.CASUAL_EXPLORER, PersonaType.SKEPTICAL_NEWCOMER]
      }
    ],
    multiSessionContinuity: false,
    minimumImmersionScore: 0.6,
    minimumEngagementScore: 0.7,
    minimumTherapeuticIntegrationScore: 0.6,
    enableRealTimeMetrics: true,
    detailedLogging: false,
    generateVisualReports: false
  } as SimulationConfig,

  // Comprehensive test (2 hours)
  COMPREHENSIVE: {
    maxSimulationDuration: 2 * 60 * 60 * 1000, // 2 hours
    maxConcurrentSessions: 10,
    enabledPersonas: Object.values(PersonaType),
    personaDistribution: {
      [PersonaType.CASUAL_EXPLORER]: 15,
      [PersonaType.STORY_ENTHUSIAST]: 15,
      [PersonaType.WORLD_BUILDER]: 10,
      [PersonaType.MARATHON_PLAYER]: 10,
      [PersonaType.SOCIAL_CONNECTOR]: 15,
      [PersonaType.ACHIEVEMENT_HUNTER]: 15,
      [PersonaType.THERAPEUTIC_SEEKER]: 15,
      [PersonaType.SKEPTICAL_NEWCOMER]: 5
    },
    worldComplexityLevels: ['simple', 'moderate', 'complex', 'epic'] as const,
    worldSystemsToTest: [
      'cultural', 'economic', 'political', 'environmental',
      'social', 'historical', 'technological', 'religious'
    ],
    sessionPatterns: getDefaultSessionPatterns().slice(0, 3), // Use first 3 scenarios for comprehensive testing
    multiSessionContinuity: true,
    minimumImmersionScore: 0.8,
    minimumEngagementScore: 0.7,
    minimumTherapeuticIntegrationScore: 0.8,
    enableRealTimeMetrics: true,
    detailedLogging: true,
    generateVisualReports: true
  } as SimulationConfig,

  // Production validation (4 hours)
  PRODUCTION_VALIDATION: {
    maxSimulationDuration: 4 * 60 * 60 * 1000, // 4 hours
    maxConcurrentSessions: 20,
    enabledPersonas: Object.values(PersonaType),
    personaDistribution: {
      [PersonaType.CASUAL_EXPLORER]: 20,
      [PersonaType.STORY_ENTHUSIAST]: 15,
      [PersonaType.WORLD_BUILDER]: 10,
      [PersonaType.MARATHON_PLAYER]: 5,
      [PersonaType.SOCIAL_CONNECTOR]: 15,
      [PersonaType.ACHIEVEMENT_HUNTER]: 15,
      [PersonaType.THERAPEUTIC_SEEKER]: 15,
      [PersonaType.SKEPTICAL_NEWCOMER]: 5
    },
    worldComplexityLevels: ['simple', 'moderate', 'complex', 'epic'] as const,
    worldSystemsToTest: [
      'cultural', 'economic', 'political', 'environmental',
      'social', 'historical', 'technological', 'religious'
    ],
    sessionPatterns: getDefaultSessionPatterns(), // Use all scenarios for production validation
    multiSessionContinuity: true,
    minimumImmersionScore: 0.85,
    minimumEngagementScore: 0.8,
    minimumTherapeuticIntegrationScore: 0.85,
    enableRealTimeMetrics: true,
    detailedLogging: true,
    generateVisualReports: true
  } as SimulationConfig
};

/**
 * Main simulation runner class
 */
export class SimulationRunner {
  private engine: SimulationEngine;
  private analyzer: ResultsAnalyzer;
  private config: SimulationConfig;

  constructor(configName: keyof typeof SIMULATION_CONFIGS = 'COMPREHENSIVE') {
    this.config = SIMULATION_CONFIGS[configName];
    this.engine = new SimulationEngine(this.config);

    const analysisConfig: AnalysisConfig = {
      includeDetailedBreakdown: this.config.detailedLogging,
      generateVisualReports: this.config.generateVisualReports,
      compareWithBaseline: false,
      exportFormat: 'json',
      includeRawData: true,
      confidenceLevel: 0.95
    };

    this.analyzer = new ResultsAnalyzer(analysisConfig);
  }

  /**
   * Run the complete simulation suite
   */
  async runSimulation(): Promise<SimulationReport> {
    console.log('🚀 Starting TTA Comprehensive Simulation Testing Framework');
    console.log(`📋 Configuration: ${this.getConfigDescription()}`);
    console.log(`⏱️  Estimated duration: ${this.config.maxSimulationDuration / (60 * 1000)} minutes`);
    console.log('');

    const startTime = Date.now();

    try {
      // Run the simulation
      const results = await this.engine.startSimulation();

      // Analyze results
      const analysis = await this.analyzer.analyzeResults(results);

      // Generate final report
      const report = this.generateFinalReport(results, analysis, startTime);

      // Print summary
      this.printSummary(report);

      return report;

    } catch (error) {
      console.error('❌ Simulation failed:', error);
      throw error;
    }
  }

  /**
   * Run simulation with custom configuration
   */
  async runWithConfig(config: SimulationConfig): Promise<SimulationReport> {
    this.config = config;
    this.engine = new SimulationEngine(config);
    return this.runSimulation();
  }

  /**
   * Generate final simulation report
   */
  private generateFinalReport(
    results: SimulationResults,
    analysis: AnalysisReport,
    startTime: number
  ): SimulationReport {
    const totalDuration = Date.now() - startTime;

    return {
      metadata: {
        timestamp: Date.now(),
        totalDuration,
        configurationUsed: this.getConfigDescription(),
        simulationVersion: '1.0.0'
      },
      executiveSummary: this.generateExecutiveSummary(results, analysis),
      results,
      analysis,
      conclusions: this.generateConclusions(results, analysis),
      nextSteps: this.generateNextSteps(analysis)
    };
  }

  /**
   * Generate executive summary
   */
  private generateExecutiveSummary(results: SimulationResults, analysis: AnalysisReport): ExecutiveSummary {
    const overallSuccess = Object.values(analysis.successCriteria).every(Boolean);

    return {
      overallSuccess,
      totalSessions: results.statistics.totalSessions,
      totalDuration: results.totalDuration,
      keyMetrics: {
        averageEngagement: results.statistics.averageEngagement,
        averageImmersion: results.statistics.averageImmersion,
        averageTherapeuticBenefit: results.statistics.averageTherapeuticBenefit,
        averageEntertainmentValue: results.statistics.averageEntertainmentValue,
        scenarioSuccessRate: results.statistics.scenarioSuccessRate,
        worldGenerationSuccessRate: results.statistics.worldGenerationSuccessRate
      },
      criticalFindings: analysis.keyFindings.slice(0, 5),
      topRecommendations: analysis.improvementPriorities.slice(0, 3)
    };
  }

  /**
   * Generate conclusions
   */
  private generateConclusions(results: SimulationResults, analysis: AnalysisReport): string[] {
    const conclusions: string[] = [];

    // Overall assessment
    const overallSuccess = Object.values(analysis.successCriteria).every(Boolean);
    if (overallSuccess) {
      conclusions.push('✅ TTA platform successfully demonstrates entertainment-first therapeutic gaming capabilities');
    } else {
      conclusions.push('⚠️ TTA platform shows promise but requires improvements before production deployment');
    }

    // World building assessment
    if (results.overallScores.worldGenerationScore > 0.8) {
      conclusions.push('🌍 World generation system creates believable, immersive environments suitable for extended gameplay');
    } else {
      conclusions.push('🌍 World generation system needs enhancement to create more compelling environments');
    }

    // Therapeutic integration assessment
    if (results.overallScores.therapeuticIntegrationScore > 0.8) {
      conclusions.push('🎭 Therapeutic elements are successfully integrated without compromising entertainment value');
    } else {
      conclusions.push('🎭 Therapeutic integration requires refinement to maintain entertainment-first approach');
    }

    // User experience assessment
    if (results.statistics.averageEngagement > 0.8) {
      conclusions.push('👥 Platform successfully engages diverse user personas across different session lengths');
    } else {
      conclusions.push('👥 User engagement needs improvement to ensure sustained platform adoption');
    }

    return conclusions;
  }

  /**
   * Generate next steps
   */
  private generateNextSteps(analysis: AnalysisReport): string[] {
    const nextSteps: string[] = [];

    // Immediate actions
    if (analysis.improvementPriorities.some(p => p.startsWith('CRITICAL'))) {
      nextSteps.push('🚨 Address critical issues identified in the analysis before any production deployment');
    }

    // Development priorities
    nextSteps.push('🔧 Implement top 3 improvement recommendations from the analysis');
    nextSteps.push('📊 Set up continuous monitoring using the metrics framework developed');
    nextSteps.push('🧪 Conduct user acceptance testing with real users based on simulation insights');

    // Long-term planning
    nextSteps.push('📈 Establish baseline metrics for ongoing performance monitoring');
    nextSteps.push('🔄 Schedule regular simulation testing to validate improvements');
    nextSteps.push('🎯 Develop persona-specific optimization strategies based on simulation results');

    return nextSteps;
  }

  /**
   * Print simulation summary
   */
  private printSummary(report: SimulationReport): void {
    console.log('\n' + '='.repeat(80));
    console.log('🎮 TTA SIMULATION TESTING RESULTS SUMMARY');
    console.log('='.repeat(80));

    const summary = report.executiveSummary;

    console.log(`\n📊 OVERALL RESULT: ${summary.overallSuccess ? '✅ SUCCESS' : '⚠️ NEEDS IMPROVEMENT'}`);
    console.log(`⏱️  Total Duration: ${(report.metadata.totalDuration / (60 * 1000)).toFixed(1)} minutes`);
    console.log(`🎭 Sessions Tested: ${summary.totalSessions}`);

    console.log('\n📈 KEY METRICS:');
    console.log(`   Engagement: ${(summary.keyMetrics.averageEngagement * 100).toFixed(1)}%`);
    console.log(`   Immersion: ${(summary.keyMetrics.averageImmersion * 100).toFixed(1)}%`);
    console.log(`   Therapeutic Benefit: ${(summary.keyMetrics.averageTherapeuticBenefit * 100).toFixed(1)}%`);
    console.log(`   Entertainment Value: ${(summary.keyMetrics.averageEntertainmentValue * 100).toFixed(1)}%`);
    console.log(`   Scenario Success Rate: ${summary.keyMetrics.scenarioSuccessRate.toFixed(1)}%`);
    console.log(`   World Generation Success: ${summary.keyMetrics.worldGenerationSuccessRate.toFixed(1)}%`);

    console.log('\n🔍 CRITICAL FINDINGS:');
    summary.criticalFindings.forEach(finding => console.log(`   • ${finding}`));

    console.log('\n🎯 TOP RECOMMENDATIONS:');
    summary.topRecommendations.forEach(rec => console.log(`   • ${rec}`));

    console.log('\n📋 CONCLUSIONS:');
    report.conclusions.forEach(conclusion => console.log(`   ${conclusion}`));

    console.log('\n🚀 NEXT STEPS:');
    report.nextSteps.slice(0, 5).forEach(step => console.log(`   ${step}`));

    console.log('\n' + '='.repeat(80));
    console.log('Simulation testing completed successfully! 🎉');
    console.log('='.repeat(80) + '\n');
  }

  /**
   * Get configuration description
   */
  private getConfigDescription(): string {
    const personaCount = this.config.enabledPersonas.length;
    const worldComplexity = this.config.worldComplexityLevels.join(', ');
    const duration = this.config.maxSimulationDuration / (60 * 1000);

    return `${personaCount} personas, ${worldComplexity} worlds, ${duration}min duration`;
  }
}

/**
 * Simulation report interfaces
 */
export interface SimulationReport {
  metadata: {
    timestamp: number;
    totalDuration: number;
    configurationUsed: string;
    simulationVersion: string;
  };
  executiveSummary: ExecutiveSummary;
  results: SimulationResults;
  analysis: AnalysisReport;
  conclusions: string[];
  nextSteps: string[];
}

export interface ExecutiveSummary {
  overallSuccess: boolean;
  totalSessions: number;
  totalDuration: number;
  keyMetrics: {
    averageEngagement: number;
    averageImmersion: number;
    averageTherapeuticBenefit: number;
    averageEntertainmentValue: number;
    scenarioSuccessRate: number;
    worldGenerationSuccessRate: number;
  };
  criticalFindings: string[];
  topRecommendations: string[];
}

/**
 * Convenience function to run simulation
 */
export async function runTTASimulation(
  configName: keyof typeof SIMULATION_CONFIGS = 'COMPREHENSIVE'
): Promise<SimulationReport> {
  const runner = new SimulationRunner(configName);
  return runner.runSimulation();
}

export default SimulationRunner;
