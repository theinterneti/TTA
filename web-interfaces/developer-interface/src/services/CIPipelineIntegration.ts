/**
 * CI/CD Pipeline Integration for Debug Tools
 *
 * Connects debugging tools with the existing CI/CD pipeline to automatically
 * capture debug data during test runs, provide performance regression detection,
 * and generate automated debugging reports for failed tests.
 */

import { EventEmitter } from 'events';
import { performanceBaselineManager } from './PerformanceBaselineManager';
import { customEventManager } from './CustomEventManager';

export interface CITestRun {
  id: string;
  buildId: string;
  branch: string;
  commit: string;
  author: string;
  startTime: string;
  endTime?: string;
  status: 'running' | 'passed' | 'failed' | 'cancelled';
  testResults: CITestResult[];
  performanceMetrics: CIPerformanceMetric[];
  debugData: CIDebugData;
  regressions: CIRegression[];
  artifacts: CIArtifact[];
}

export interface CITestResult {
  testId: string;
  testName: string;
  testFile: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error?: {
    message: string;
    stack: string;
    type: string;
  };
  debugEvents: any[];
  performanceData: {
    memoryUsage: number;
    renderTime: number;
    networkRequests: number;
  };
}

export interface CIPerformanceMetric {
  name: string;
  value: number;
  unit: string;
  baseline?: number;
  threshold?: number;
  regression?: boolean;
  interfaceId: string;
  timestamp: string;
}

export interface CIDebugData {
  networkRequests: Array<{
    url: string;
    method: string;
    status: number;
    duration: number;
    timestamp: string;
  }>;
  errors: Array<{
    message: string;
    stack: string;
    context: string;
    timestamp: string;
  }>;
  consoleLogs: Array<{
    level: string;
    message: string;
    timestamp: string;
  }>;
  customEvents: Array<{
    eventType: string;
    interfaceId: string;
    data: any;
    timestamp: string;
  }>;
}

export interface CIRegression {
  id: string;
  type: 'performance' | 'functionality' | 'accessibility';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  baseline: any;
  current: any;
  difference: number;
  interfaceId: string;
  testId?: string;
}

export interface CIArtifact {
  id: string;
  type: 'screenshot' | 'video' | 'log' | 'report' | 'trace';
  name: string;
  path: string;
  size: number;
  createdAt: string;
  metadata?: any;
}

export interface CIReport {
  testRunId: string;
  summary: {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    skippedTests: number;
    duration: number;
    regressionCount: number;
  };
  performanceAnalysis: {
    overallScore: number;
    regressions: CIRegression[];
    improvements: Array<{
      metric: string;
      improvement: number;
      interfaceId: string;
    }>;
  };
  debugInsights: {
    errorPatterns: Array<{
      pattern: string;
      count: number;
      examples: string[];
    }>;
    performanceBottlenecks: Array<{
      component: string;
      issue: string;
      impact: string;
    }>;
    recommendations: string[];
  };
  artifacts: CIArtifact[];
}

export class CIPipelineIntegration extends EventEmitter {
  private currentTestRun: CITestRun | null = null;
  private testRuns: Map<string, CITestRun> = new Map();
  private isRecording: boolean = false;
  private debugDataBuffer: CIDebugData = {
    networkRequests: [],
    errors: [],
    consoleLogs: [],
    customEvents: []
  };

  constructor() {
    super();
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    // Listen for performance baseline events
    performanceBaselineManager.on('regression_detected', (regression) => {
      this.handlePerformanceRegression(regression);
    });

    // Listen for custom events
    customEventManager.on('event_instance_created', (event) => {
      if (this.isRecording) {
        this.debugDataBuffer.customEvents.push({
          eventType: event.eventType,
          interfaceId: event.interfaceId,
          data: event.data,
          timestamp: event.timestamp
        });
      }
    });

    // Listen for global errors
    if (typeof window !== 'undefined') {
      window.addEventListener('error', (event) => {
        if (this.isRecording) {
          this.debugDataBuffer.errors.push({
            message: event.message,
            stack: event.error?.stack || '',
            context: 'Global Error Handler',
            timestamp: new Date().toISOString()
          });
        }
      });
    }
  }

  public startTestRun(buildId: string, branch: string, commit: string, author: string): CITestRun {
    const testRunId = `run_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const testRun: CITestRun = {
      id: testRunId,
      buildId,
      branch,
      commit,
      author,
      startTime: new Date().toISOString(),
      status: 'running',
      testResults: [],
      performanceMetrics: [],
      debugData: {
        networkRequests: [],
        errors: [],
        consoleLogs: [],
        customEvents: []
      },
      regressions: [],
      artifacts: []
    };

    this.currentTestRun = testRun;
    this.testRuns.set(testRunId, testRun);
    this.isRecording = true;

    // Clear debug data buffer
    this.debugDataBuffer = {
      networkRequests: [],
      errors: [],
      consoleLogs: [],
      customEvents: []
    };

    console.log(`🚀 Started CI test run: ${testRunId}`);
    this.emit('test_run_started', testRun);

    return testRun;
  }

  public recordTestResult(testResult: Omit<CITestResult, 'debugEvents' | 'performanceData'>): void {
    if (!this.currentTestRun) return;

    // Collect debug events for this test
    const debugEvents = [...this.debugDataBuffer.customEvents];

    // Collect performance data
    const performanceData = {
      memoryUsage: this.getCurrentMemoryUsage(),
      renderTime: this.getAverageRenderTime(),
      networkRequests: this.debugDataBuffer.networkRequests.length
    };

    const completeTestResult: CITestResult = {
      ...testResult,
      debugEvents,
      performanceData
    };

    this.currentTestRun.testResults.push(completeTestResult);

    // Check for regressions
    this.checkTestRegressions(completeTestResult);

    this.emit('test_result_recorded', completeTestResult);
  }

  public recordPerformanceMetric(metric: Omit<CIPerformanceMetric, 'baseline' | 'regression'>): void {
    if (!this.currentTestRun) return;

    // Get baseline for comparison
    const baseline = performanceBaselineManager.getBaseline(metric.interfaceId);
    const baselineValue = baseline?.metrics[metric.name]?.baseline;

    const completeMetric: CIPerformanceMetric = {
      ...metric,
      baseline: baselineValue,
      regression: baselineValue ? metric.value > baselineValue * 1.2 : false // 20% threshold
    };

    this.currentTestRun.performanceMetrics.push(completeMetric);

    // Record with performance baseline manager
    performanceBaselineManager.recordMetric({
      name: metric.name,
      value: metric.value,
      unit: metric.unit,
      timestamp: metric.timestamp,
      interfaceId: metric.interfaceId,
      category: 'custom'
    });

    this.emit('performance_metric_recorded', completeMetric);
  }

  public recordNetworkRequest(url: string, method: string, status: number, duration: number): void {
    if (!this.isRecording) return;

    this.debugDataBuffer.networkRequests.push({
      url,
      method,
      status,
      duration,
      timestamp: new Date().toISOString()
    });
  }

  public recordError(message: string, stack: string, context: string): void {
    if (!this.isRecording) return;

    this.debugDataBuffer.errors.push({
      message,
      stack,
      context,
      timestamp: new Date().toISOString()
    });
  }

  public recordConsoleLog(level: string, message: string): void {
    if (!this.isRecording) return;

    this.debugDataBuffer.consoleLogs.push({
      level,
      message,
      timestamp: new Date().toISOString()
    });
  }

  public addArtifact(artifact: Omit<CIArtifact, 'id' | 'createdAt'>): CIArtifact {
    if (!this.currentTestRun) {
      throw new Error('No active test run');
    }

    const completeArtifact: CIArtifact = {
      ...artifact,
      id: `artifact_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date().toISOString()
    };

    this.currentTestRun.artifacts.push(completeArtifact);
    this.emit('artifact_added', completeArtifact);

    return completeArtifact;
  }

  public finishTestRun(status: 'passed' | 'failed' | 'cancelled'): CITestRun {
    if (!this.currentTestRun) {
      throw new Error('No active test run');
    }

    this.currentTestRun.endTime = new Date().toISOString();
    this.currentTestRun.status = status;
    this.currentTestRun.debugData = { ...this.debugDataBuffer };

    this.isRecording = false;

    // Generate final report
    const report = this.generateReport(this.currentTestRun);

    console.log(`✅ Finished CI test run: ${this.currentTestRun.id} (${status})`);
    this.emit('test_run_finished', { testRun: this.currentTestRun, report });

    const finishedRun = this.currentTestRun;
    this.currentTestRun = null;

    return finishedRun;
  }

  private handlePerformanceRegression(regression: any): void {
    if (!this.currentTestRun) return;

    const ciRegression: CIRegression = {
      id: `regression_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: 'performance',
      severity: this.mapSeverity(regression.severity),
      description: `Performance regression in ${regression.metricName}: ${regression.regressionPercentage.toFixed(1)}% increase`,
      baseline: regression.baselineValue,
      current: regression.currentValue,
      difference: regression.regressionPercentage,
      interfaceId: regression.interfaceId
    };

    this.currentTestRun.regressions.push(ciRegression);
    this.emit('regression_detected', ciRegression);
  }

  private checkTestRegressions(testResult: CITestResult): void {
    if (!this.currentTestRun) return;

    // Check for performance regressions in test
    const { performanceData } = testResult;

    // Memory usage regression
    if (performanceData.memoryUsage > 100 * 1024 * 1024) { // 100MB threshold
      const regression: CIRegression = {
        id: `regression_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'performance',
        severity: 'medium',
        description: `High memory usage in test ${testResult.testName}: ${(performanceData.memoryUsage / 1024 / 1024).toFixed(1)}MB`,
        baseline: 50 * 1024 * 1024, // 50MB baseline
        current: performanceData.memoryUsage,
        difference: ((performanceData.memoryUsage - 50 * 1024 * 1024) / (50 * 1024 * 1024)) * 100,
        interfaceId: 'test-runner',
        testId: testResult.testId
      };

      this.currentTestRun.regressions.push(regression);
    }

    // Render time regression
    if (performanceData.renderTime > 1000) { // 1 second threshold
      const regression: CIRegression = {
        id: `regression_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'performance',
        severity: 'high',
        description: `Slow render time in test ${testResult.testName}: ${performanceData.renderTime}ms`,
        baseline: 500, // 500ms baseline
        current: performanceData.renderTime,
        difference: ((performanceData.renderTime - 500) / 500) * 100,
        interfaceId: 'test-runner',
        testId: testResult.testId
      };

      this.currentTestRun.regressions.push(regression);
    }
  }

  private generateReport(testRun: CITestRun): CIReport {
    const summary = {
      totalTests: testRun.testResults.length,
      passedTests: testRun.testResults.filter(t => t.status === 'passed').length,
      failedTests: testRun.testResults.filter(t => t.status === 'failed').length,
      skippedTests: testRun.testResults.filter(t => t.status === 'skipped').length,
      duration: testRun.endTime ?
        new Date(testRun.endTime).getTime() - new Date(testRun.startTime).getTime() : 0,
      regressionCount: testRun.regressions.length
    };

    const performanceAnalysis = this.analyzePerformance(testRun);
    const debugInsights = this.generateDebugInsights(testRun);

    return {
      testRunId: testRun.id,
      summary,
      performanceAnalysis,
      debugInsights,
      artifacts: testRun.artifacts
    };
  }

  private analyzePerformance(testRun: CITestRun): CIReport['performanceAnalysis'] {
    const regressions = testRun.regressions.filter(r => r.type === 'performance');
    const improvements: Array<{ metric: string; improvement: number; interfaceId: string }> = [];

    // Calculate overall performance score
    let overallScore = 100;
    regressions.forEach(regression => {
      switch (regression.severity) {
        case 'critical': overallScore -= 25; break;
        case 'high': overallScore -= 15; break;
        case 'medium': overallScore -= 10; break;
        case 'low': overallScore -= 5; break;
      }
    });

    overallScore = Math.max(0, overallScore);

    return {
      overallScore,
      regressions,
      improvements
    };
  }

  private generateDebugInsights(testRun: CITestRun): CIReport['debugInsights'] {
    const errorPatterns = this.analyzeErrorPatterns(testRun.debugData.errors);
    const performanceBottlenecks = this.identifyPerformanceBottlenecks(testRun);
    const recommendations = this.generateRecommendations(testRun);

    return {
      errorPatterns,
      performanceBottlenecks,
      recommendations
    };
  }

  private analyzeErrorPatterns(errors: CIDebugData['errors']): Array<{ pattern: string; count: number; examples: string[] }> {
    const patterns = new Map<string, { count: number; examples: string[] }>();

    errors.forEach(error => {
      // Simple pattern matching - in real implementation, this would be more sophisticated
      let pattern = 'Unknown Error';

      if (error.message.includes('TypeError')) {
        pattern = 'Type Error';
      } else if (error.message.includes('ReferenceError')) {
        pattern = 'Reference Error';
      } else if (error.message.includes('Network')) {
        pattern = 'Network Error';
      } else if (error.message.includes('timeout')) {
        pattern = 'Timeout Error';
      }

      if (!patterns.has(pattern)) {
        patterns.set(pattern, { count: 0, examples: [] });
      }

      const patternData = patterns.get(pattern)!;
      patternData.count++;
      if (patternData.examples.length < 3) {
        patternData.examples.push(error.message);
      }
    });

    return Array.from(patterns.entries()).map(([pattern, data]) => ({
      pattern,
      count: data.count,
      examples: data.examples
    }));
  }

  private identifyPerformanceBottlenecks(testRun: CITestRun): Array<{ component: string; issue: string; impact: string }> {
    const bottlenecks: Array<{ component: string; issue: string; impact: string }> = [];

    // Analyze test results for performance issues
    testRun.testResults.forEach(test => {
      if (test.performanceData.renderTime > 1000) {
        bottlenecks.push({
          component: test.testName,
          issue: 'Slow render time',
          impact: `${test.performanceData.renderTime}ms render time`
        });
      }

      if (test.performanceData.memoryUsage > 100 * 1024 * 1024) {
        bottlenecks.push({
          component: test.testName,
          issue: 'High memory usage',
          impact: `${(test.performanceData.memoryUsage / 1024 / 1024).toFixed(1)}MB memory usage`
        });
      }
    });

    return bottlenecks;
  }

  private generateRecommendations(testRun: CITestRun): string[] {
    const recommendations: string[] = [];

    if (testRun.regressions.length > 0) {
      recommendations.push('Address performance regressions before deployment');
    }

    if (testRun.debugData.errors.length > 10) {
      recommendations.push('High error count detected - review error handling');
    }

    if (testRun.testResults.some(t => t.performanceData.memoryUsage > 100 * 1024 * 1024)) {
      recommendations.push('Optimize memory usage in components with high memory consumption');
    }

    if (testRun.debugData.networkRequests.some(r => r.duration > 5000)) {
      recommendations.push('Optimize slow network requests or implement proper loading states');
    }

    return recommendations;
  }

  private getCurrentMemoryUsage(): number {
    if (typeof performance !== 'undefined' && 'memory' in performance) {
      return (performance as any).memory.usedJSHeapSize;
    }
    return 0;
  }

  private getAverageRenderTime(): number {
    // This would typically be calculated from actual render measurements
    return 150; // Simulated average render time
  }

  private mapSeverity(severity: string): 'low' | 'medium' | 'high' | 'critical' {
    switch (severity) {
      case 'critical': return 'critical';
      case 'high': return 'high';
      case 'medium': return 'medium';
      default: return 'low';
    }
  }

  // Public API methods

  public getCurrentTestRun(): CITestRun | null {
    return this.currentTestRun;
  }

  public getTestRun(testRunId: string): CITestRun | null {
    return this.testRuns.get(testRunId) || null;
  }

  public getAllTestRuns(): CITestRun[] {
    return Array.from(this.testRuns.values());
  }

  public isRecordingActive(): boolean {
    return this.isRecording;
  }

  public exportTestRunData(testRunId: string): string {
    const testRun = this.testRuns.get(testRunId);
    if (!testRun) {
      throw new Error('Test run not found');
    }

    return JSON.stringify(testRun, null, 2);
  }

  public dispose(): void {
    this.isRecording = false;
    this.currentTestRun = null;
    this.removeAllListeners();
    this.testRuns.clear();
  }
}

// Singleton instance
export const ciPipelineIntegration = new CIPipelineIntegration();
