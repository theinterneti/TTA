// Logseq: [[TTA.dev/Testing/Simulation/Scripts/Generatereport]]
#!/usr/bin/env ts-node
/**
 * Production Report Generator for TTA Simulation Framework
 *
 * Generates comprehensive production validation reports from simulation results
 * including metrics, analysis, and readiness assessment.
 */

import * as fs from 'fs';
import * as path from 'path';

interface SimulationResult {
  sessionId: string;
  persona: string;
  scenario: string;
  timestamp: string;
  duration: number;
  success: boolean;
  metrics: {
    narrativeCoherence: number;
    worldConsistency: number;
    userEngagement: number;
    therapeuticAlignment: number;
    immersionScore: number;
    responseTime: number;
  };
  errors?: string[];
  warnings?: string[];
}

interface ProductionReport {
  generatedAt: string;
  testDuration: number;
  totalSessions: number;
  successfulSessions: number;
  failedSessions: number;
  successRate: number;
  averageMetrics: {
    narrativeCoherence: number;
    worldConsistency: number;
    userEngagement: number;
    therapeuticAlignment: number;
    immersionScore: number;
    responseTime: number;
  };
  qualityGates: {
    narrativeCoherence: { threshold: number; actual: number; passed: boolean };
    worldConsistency: { threshold: number; actual: number; passed: boolean };
    userEngagement: { threshold: number; actual: number; passed: boolean };
    therapeuticAlignment: { threshold: number; actual: number; passed: boolean };
    immersionScore: { threshold: number; actual: number; passed: boolean };
    responseTime: { threshold: number; actual: number; passed: boolean };
  };
  productionReadiness: {
    overallScore: number;
    recommendation: 'READY' | 'READY_WITH_WARNINGS' | 'NOT_READY';
    blockers: string[];
    warnings: string[];
    strengths: string[];
  };
  detailedAnalysis: {
    performanceAnalysis: string;
    qualityAnalysis: string;
    riskAssessment: string;
    recommendations: string[];
  };
}

class ProductionReportGenerator {
  private resultsDir: string;
  private outputDir: string;

  constructor() {
    this.resultsDir = path.join(__dirname, '..');
    this.outputDir = path.join(this.resultsDir, 'reports');

    // Ensure output directory exists
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  /**
   * Find the most recent simulation results file
   */
  private findLatestResultsFile(): string | null {
    const files = fs.readdirSync(this.resultsDir)
      .filter(f => f.startsWith('simulation-results-') && f.endsWith('.json'))
      .sort()
      .reverse();

    return files.length > 0 ? path.join(this.resultsDir, files[0]) : null;
  }

  /**
   * Load simulation results from file
   */
  private loadResults(filePath: string): SimulationResult[] {
    const content = fs.readFileSync(filePath, 'utf-8');
    const data = JSON.parse(content);
    return data.results || [];
  }

  /**
   * Calculate average metrics across all sessions
   */
  private calculateAverageMetrics(results: SimulationResult[]) {
    const successfulResults = results.filter(r => r.success);

    if (successfulResults.length === 0) {
      return {
        narrativeCoherence: 0,
        worldConsistency: 0,
        userEngagement: 0,
        therapeuticAlignment: 0,
        immersionScore: 0,
        responseTime: 0,
      };
    }

    const sum = successfulResults.reduce((acc, r) => ({
      narrativeCoherence: acc.narrativeCoherence + r.metrics.narrativeCoherence,
      worldConsistency: acc.worldConsistency + r.metrics.worldConsistency,
      userEngagement: acc.userEngagement + r.metrics.userEngagement,
      therapeuticAlignment: acc.therapeuticAlignment + r.metrics.therapeuticAlignment,
      immersionScore: acc.immersionScore + r.metrics.immersionScore,
      responseTime: acc.responseTime + r.metrics.responseTime,
    }), {
      narrativeCoherence: 0,
      worldConsistency: 0,
      userEngagement: 0,
      therapeuticAlignment: 0,
      immersionScore: 0,
      responseTime: 0,
    });

    const count = successfulResults.length;
    return {
      narrativeCoherence: sum.narrativeCoherence / count,
      worldConsistency: sum.worldConsistency / count,
      userEngagement: sum.userEngagement / count,
      therapeuticAlignment: sum.therapeuticAlignment / count,
      immersionScore: sum.immersionScore / count,
      responseTime: sum.responseTime / count,
    };
  }

  /**
   * Evaluate quality gates
   */
  private evaluateQualityGates(avgMetrics: any) {
    const thresholds = {
      narrativeCoherence: 7.5,
      worldConsistency: 7.5,
      userEngagement: 7.0,
      therapeuticAlignment: 7.0,
      immersionScore: 7.0,
      responseTime: 2000, // ms
    };

    return {
      narrativeCoherence: {
        threshold: thresholds.narrativeCoherence,
        actual: avgMetrics.narrativeCoherence,
        passed: avgMetrics.narrativeCoherence >= thresholds.narrativeCoherence,
      },
      worldConsistency: {
        threshold: thresholds.worldConsistency,
        actual: avgMetrics.worldConsistency,
        passed: avgMetrics.worldConsistency >= thresholds.worldConsistency,
      },
      userEngagement: {
        threshold: thresholds.userEngagement,
        actual: avgMetrics.userEngagement,
        passed: avgMetrics.userEngagement >= thresholds.userEngagement,
      },
      therapeuticAlignment: {
        threshold: thresholds.therapeuticAlignment,
        actual: avgMetrics.therapeuticAlignment,
        passed: avgMetrics.therapeuticAlignment >= thresholds.therapeuticAlignment,
      },
      immersionScore: {
        threshold: thresholds.immersionScore,
        actual: avgMetrics.immersionScore,
        passed: avgMetrics.immersionScore >= thresholds.immersionScore,
      },
      responseTime: {
        threshold: thresholds.responseTime,
        actual: avgMetrics.responseTime,
        passed: avgMetrics.responseTime <= thresholds.responseTime,
      },
    };
  }

  /**
   * Assess production readiness
   */
  private assessProductionReadiness(
    qualityGates: any,
    successRate: number,
    results: SimulationResult[]
  ) {
    const blockers: string[] = [];
    const warnings: string[] = [];
    const strengths: string[] = [];

    // Check critical quality gates
    if (!qualityGates.narrativeCoherence.passed) {
      blockers.push(`Narrative coherence below threshold: ${qualityGates.narrativeCoherence.actual.toFixed(2)} < ${qualityGates.narrativeCoherence.threshold}`);
    } else if (qualityGates.narrativeCoherence.actual >= 8.5) {
      strengths.push(`Excellent narrative coherence: ${qualityGates.narrativeCoherence.actual.toFixed(2)}/10`);
    }

    if (!qualityGates.worldConsistency.passed) {
      blockers.push(`World consistency below threshold: ${qualityGates.worldConsistency.actual.toFixed(2)} < ${qualityGates.worldConsistency.threshold}`);
    } else if (qualityGates.worldConsistency.actual >= 8.5) {
      strengths.push(`Excellent world consistency: ${qualityGates.worldConsistency.actual.toFixed(2)}/10`);
    }

    if (!qualityGates.userEngagement.passed) {
      warnings.push(`User engagement below threshold: ${qualityGates.userEngagement.actual.toFixed(2)} < ${qualityGates.userEngagement.threshold}`);
    } else if (qualityGates.userEngagement.actual >= 8.0) {
      strengths.push(`Strong user engagement: ${qualityGates.userEngagement.actual.toFixed(2)}/10`);
    }

    if (!qualityGates.responseTime.passed) {
      warnings.push(`Response time above threshold: ${qualityGates.responseTime.actual.toFixed(0)}ms > ${qualityGates.responseTime.threshold}ms`);
    } else if (qualityGates.responseTime.actual <= 1000) {
      strengths.push(`Excellent response time: ${qualityGates.responseTime.actual.toFixed(0)}ms`);
    }

    // Check success rate
    if (successRate < 0.95) {
      blockers.push(`Success rate too low: ${(successRate * 100).toFixed(1)}% < 95%`);
    } else if (successRate >= 0.99) {
      strengths.push(`Excellent success rate: ${(successRate * 100).toFixed(1)}%`);
    }

    // Calculate overall score (0-100)
    const gatesPassed = Object.values(qualityGates).filter((g: any) => g.passed).length;
    const totalGates = Object.keys(qualityGates).length;
    const overallScore = (gatesPassed / totalGates) * 100 * successRate;

    // Determine recommendation
    let recommendation: 'READY' | 'READY_WITH_WARNINGS' | 'NOT_READY';
    if (blockers.length > 0) {
      recommendation = 'NOT_READY';
    } else if (warnings.length > 0) {
      recommendation = 'READY_WITH_WARNINGS';
    } else {
      recommendation = 'READY';
    }

    return {
      overallScore,
      recommendation,
      blockers,
      warnings,
      strengths,
    };
  }

  /**
   * Generate production report
   */
  public generateReport(): void {
    console.log('🔍 Searching for simulation results...');

    const resultsFile = this.findLatestResultsFile();
    if (!resultsFile) {
      console.error('❌ No simulation results found');
      process.exit(1);
    }

    console.log(`📊 Loading results from: ${path.basename(resultsFile)}`);
    const results = this.loadResults(resultsFile);

    if (results.length === 0) {
      console.error('❌ No simulation results to analyze');
      process.exit(1);
    }

    console.log(`✅ Loaded ${results.length} simulation results`);
    console.log('📈 Generating production report...');

    const successfulSessions = results.filter(r => r.success).length;
    const failedSessions = results.length - successfulSessions;
    const successRate = successfulSessions / results.length;
    const avgMetrics = this.calculateAverageMetrics(results);
    const qualityGates = this.evaluateQualityGates(avgMetrics);
    const readiness = this.assessProductionReadiness(qualityGates, successRate, results);

    const report: ProductionReport = {
      generatedAt: new Date().toISOString(),
      testDuration: 0, // Would be calculated from actual test duration
      totalSessions: results.length,
      successfulSessions,
      failedSessions,
      successRate,
      averageMetrics: avgMetrics,
      qualityGates,
      productionReadiness: readiness,
      detailedAnalysis: {
        performanceAnalysis: this.generatePerformanceAnalysis(avgMetrics, qualityGates),
        qualityAnalysis: this.generateQualityAnalysis(avgMetrics, qualityGates),
        riskAssessment: this.generateRiskAssessment(readiness),
        recommendations: this.generateRecommendations(readiness, qualityGates),
      },
    };

    // Save report
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const reportPath = path.join(this.outputDir, `production-report-${timestamp}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log(`✅ Production report generated: ${reportPath}`);
    console.log('\n' + '='.repeat(80));
    console.log('PRODUCTION READINESS ASSESSMENT');
    console.log('='.repeat(80));
    console.log(`Overall Score: ${readiness.overallScore.toFixed(1)}/100`);
    console.log(`Recommendation: ${readiness.recommendation}`);
    console.log(`Success Rate: ${(successRate * 100).toFixed(1)}%`);
    console.log('='.repeat(80));

    if (readiness.blockers.length > 0) {
      console.log('\n❌ BLOCKERS:');
      readiness.blockers.forEach(b => console.log(`  - ${b}`));
    }

    if (readiness.warnings.length > 0) {
      console.log('\n⚠️  WARNINGS:');
      readiness.warnings.forEach(w => console.log(`  - ${w}`));
    }

    if (readiness.strengths.length > 0) {
      console.log('\n✅ STRENGTHS:');
      readiness.strengths.forEach(s => console.log(`  - ${s}`));
    }

    console.log('\n' + '='.repeat(80));
  }

  private generatePerformanceAnalysis(metrics: any, gates: any): string {
    return `Performance analysis based on ${Object.keys(metrics).length} metrics. ` +
           `Response time: ${metrics.responseTime.toFixed(0)}ms (threshold: ${gates.responseTime.threshold}ms).`;
  }

  private generateQualityAnalysis(metrics: any, gates: any): string {
    const passedGates = Object.values(gates).filter((g: any) => g.passed).length;
    return `Quality analysis: ${passedGates}/${Object.keys(gates).length} quality gates passed.`;
  }

  private generateRiskAssessment(readiness: any): string {
    if (readiness.blockers.length > 0) {
      return `HIGH RISK: ${readiness.blockers.length} critical blockers identified.`;
    } else if (readiness.warnings.length > 0) {
      return `MEDIUM RISK: ${readiness.warnings.length} warnings identified.`;
    }
    return 'LOW RISK: All quality gates passed.';
  }

  private generateRecommendations(readiness: any, gates: any): string[] {
    const recommendations: string[] = [];

    if (readiness.recommendation === 'NOT_READY') {
      recommendations.push('Address all blockers before production deployment');
      recommendations.push('Run additional validation tests');
    } else if (readiness.recommendation === 'READY_WITH_WARNINGS') {
      recommendations.push('Monitor warnings closely in production');
      recommendations.push('Plan improvements for next release');
    } else {
      recommendations.push('System ready for production deployment');
      recommendations.push('Continue monitoring metrics post-deployment');
    }

    return recommendations;
  }
}

// Run report generation
const generator = new ProductionReportGenerator();
generator.generateReport();
