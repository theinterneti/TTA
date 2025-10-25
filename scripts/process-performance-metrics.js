#!/usr/bin/env node

/**
 * Process Performance Metrics from E2E Tests
 *
 * Processes test results and generates:
 * - Performance baseline
 * - Trend analysis
 * - Regression detection
 * - Historical comparison
 */

const fs = require('fs');
const path = require('path');

const TEST_RESULTS_DIR = 'test-results-staging';
const BASELINE_FILE = 'performance-baseline.json';
const METRICS_HISTORY_FILE = '.github/performance-history.json';

/**
 * Read test results
 */
function readTestResults() {
  try {
    const resultsFile = path.join(TEST_RESULTS_DIR, 'results.json');

    if (!fs.existsSync(resultsFile)) {
      console.warn(`⚠️ Test results file not found: ${resultsFile}`);
      return null;
    }

    return JSON.parse(fs.readFileSync(resultsFile, 'utf8'));
  } catch (error) {
    console.error('❌ Failed to read test results:', error);
    return null;
  }
}

/**
 * Extract performance metrics from results
 */
function extractMetrics(results) {
  if (!results) return null;

  const metrics = {
    timestamp: new Date().toISOString(),
    totalTests: results.stats?.expected + results.stats?.unexpected || 0,
    passedTests: results.stats?.expected || 0,
    failedTests: results.stats?.unexpected || 0,
    passRate: results.stats?.expected / (results.stats?.expected + results.stats?.unexpected) || 0,
    performance: {
      pageLoad: 0,
      apiResponse: 0,
      aiResponse: 0,
      averageResponseTime: 0,
    },
  };

  // Extract performance data from test results
  if (results.performance) {
    metrics.performance = {
      ...metrics.performance,
      ...results.performance,
    };
  }

  return metrics;
}

/**
 * Load performance history
 */
function loadPerformanceHistory() {
  try {
    if (fs.existsSync(METRICS_HISTORY_FILE)) {
      return JSON.parse(fs.readFileSync(METRICS_HISTORY_FILE, 'utf8'));
    }
  } catch (error) {
    console.warn('⚠️ Failed to load performance history:', error);
  }

  return {
    metrics: [],
    baselines: {},
  };
}

/**
 * Save performance history
 */
function savePerformanceHistory(history) {
  try {
    const dir = path.dirname(METRICS_HISTORY_FILE);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(METRICS_HISTORY_FILE, JSON.stringify(history, null, 2));
    console.log(`✅ Performance history saved to ${METRICS_HISTORY_FILE}`);
  } catch (error) {
    console.error('❌ Failed to save performance history:', error);
  }
}

/**
 * Detect performance regressions
 */
function detectRegressions(currentMetrics, history) {
  const regressions = [];
  const REGRESSION_THRESHOLD = 0.2; // 20% increase

  if (history.baselines.pageLoad) {
    const increase = (currentMetrics.performance.pageLoad - history.baselines.pageLoad) / history.baselines.pageLoad;
    if (increase > REGRESSION_THRESHOLD) {
      regressions.push({
        metric: 'pageLoad',
        baseline: history.baselines.pageLoad,
        current: currentMetrics.performance.pageLoad,
        increase: (increase * 100).toFixed(2),
      });
    }
  }

  if (history.baselines.apiResponse) {
    const increase = (currentMetrics.performance.apiResponse - history.baselines.apiResponse) / history.baselines.apiResponse;
    if (increase > REGRESSION_THRESHOLD) {
      regressions.push({
        metric: 'apiResponse',
        baseline: history.baselines.apiResponse,
        current: currentMetrics.performance.apiResponse,
        increase: (increase * 100).toFixed(2),
      });
    }
  }

  if (history.baselines.aiResponse) {
    const increase = (currentMetrics.performance.aiResponse - history.baselines.aiResponse) / history.baselines.aiResponse;
    if (increase > REGRESSION_THRESHOLD) {
      regressions.push({
        metric: 'aiResponse',
        baseline: history.baselines.aiResponse,
        current: currentMetrics.performance.aiResponse,
        increase: (increase * 100).toFixed(2),
      });
    }
  }

  return regressions;
}

/**
 * Calculate trend
 */
function calculateTrend(history, metricKey, days = 7) {
  const recentMetrics = history.metrics.slice(-days);

  if (recentMetrics.length < 2) {
    return { trend: 'insufficient-data', change: 0 };
  }

  const values = recentMetrics.map((m) => m.performance[metricKey] || 0);
  const firstValue = values[0];
  const lastValue = values[values.length - 1];
  const change = ((lastValue - firstValue) / firstValue) * 100;

  return {
    trend: change > 5 ? 'increasing' : change < -5 ? 'decreasing' : 'stable',
    change: change.toFixed(2),
    values,
  };
}

/**
 * Generate performance report
 */
function generatePerformanceReport(currentMetrics, history, regressions) {
  let report = '=== Performance Metrics Report ===\n\n';

  report += `Timestamp: ${currentMetrics.timestamp}\n`;
  report += `Total Tests: ${currentMetrics.totalTests}\n`;
  report += `Passed: ${currentMetrics.passedTests}\n`;
  report += `Failed: ${currentMetrics.failedTests}\n`;
  report += `Pass Rate: ${(currentMetrics.passRate * 100).toFixed(2)}%\n\n`;

  report += '=== Performance Metrics ===\n';
  report += `Page Load: ${currentMetrics.performance.pageLoad.toFixed(0)}ms\n`;
  report += `API Response: ${currentMetrics.performance.apiResponse.toFixed(0)}ms\n`;
  report += `AI Response: ${currentMetrics.performance.aiResponse.toFixed(0)}ms\n\n`;

  if (regressions.length > 0) {
    report += '=== Performance Regressions Detected ===\n';
    for (const regression of regressions) {
      report += `\n${regression.metric}:\n`;
      report += `  Baseline: ${regression.baseline.toFixed(0)}ms\n`;
      report += `  Current: ${regression.current.toFixed(0)}ms\n`;
      report += `  Increase: ${regression.increase}%\n`;
    }
  } else {
    report += '✅ No performance regressions detected\n\n';
  }

  report += '=== 7-Day Trends ===\n';
  const pageLoadTrend = calculateTrend(history, 'pageLoad');
  const apiResponseTrend = calculateTrend(history, 'apiResponse');
  const aiResponseTrend = calculateTrend(history, 'aiResponse');

  report += `Page Load: ${pageLoadTrend.trend} (${pageLoadTrend.change}%)\n`;
  report += `API Response: ${apiResponseTrend.trend} (${apiResponseTrend.change}%)\n`;
  report += `AI Response: ${aiResponseTrend.trend} (${aiResponseTrend.change}%)\n`;

  return report;
}

/**
 * Main execution
 */
function main() {
  try {
    console.log('📊 Processing performance metrics...');

    // Read current test results
    const results = readTestResults();
    if (!results) {
      console.warn('⚠️ No test results to process');
      return;
    }

    // Extract metrics
    const currentMetrics = extractMetrics(results);
    console.log('✅ Metrics extracted');

    // Load history
    const history = loadPerformanceHistory();

    // Detect regressions
    const regressions = detectRegressions(currentMetrics, history.baselines);
    if (regressions.length > 0) {
      console.warn(`⚠️ ${regressions.length} performance regression(s) detected`);
    }

    // Update baselines
    history.baselines = {
      pageLoad: currentMetrics.performance.pageLoad,
      apiResponse: currentMetrics.performance.apiResponse,
      aiResponse: currentMetrics.performance.aiResponse,
    };

    // Add to history
    history.metrics.push(currentMetrics);

    // Keep only last 90 days
    const ninetyDaysAgo = new Date();
    ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
    history.metrics = history.metrics.filter((m) => new Date(m.timestamp) > ninetyDaysAgo);

    // Save history
    savePerformanceHistory(history);

    // Generate report
    const report = generatePerformanceReport(currentMetrics, history, regressions);
    console.log('\n' + report);

    // Save baseline
    fs.writeFileSync(BASELINE_FILE, JSON.stringify(currentMetrics, null, 2));
    console.log(`✅ Baseline saved to ${BASELINE_FILE}`);

    // Exit with error if regressions detected
    if (regressions.length > 0) {
      process.exit(1);
    }

    process.exit(0);
  } catch (error) {
    console.error('❌ Failed to process performance metrics:', error);
    process.exit(1);
  }
}

main();
