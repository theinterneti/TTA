#!/usr/bin/env node

/**
 * Performance Budget Checker for TTA E2E Tests
 *
 * This script analyzes Playwright test results and enforces performance budgets
 * for critical user journeys in the TTA application.
 */

const fs = require('fs');
const path = require('path');

// Performance budgets (in milliseconds)
const PERFORMANCE_BUDGETS = {
  'auth-login': {
    loadTime: parseInt(process.env.PERFORMANCE_BUDGET_AUTH_LOAD_TIME) || 2000,
    fcp: 1500,
    lcp: 2500,
    cls: 0.1,
    fid: 100
  },
  'dashboard-load': {
    loadTime: parseInt(process.env.PERFORMANCE_BUDGET_DASHBOARD_LOAD_TIME) || 3000,
    fcp: 2000,
    lcp: 3500,
    cls: 0.1,
    fid: 100
  },
  'character-create': {
    loadTime: 2500,
    fcp: 1800,
    lcp: 3000,
    cls: 0.1,
    fid: 100
  },
  'chat-response': {
    loadTime: parseInt(process.env.PERFORMANCE_BUDGET_CHAT_RESPONSE_TIME) || 1500,
    fcp: 1200,
    lcp: 2000,
    cls: 0.05,
    fid: 50
  },
  'settings-save': {
    loadTime: 2000,
    fcp: 1500,
    lcp: 2500,
    cls: 0.1,
    fid: 100
  }
};

// Severity levels for budget violations
const SEVERITY_LEVELS = {
  CRITICAL: { threshold: 2.0, emoji: '🚨', color: 'red' },
  HIGH: { threshold: 1.5, emoji: '⚠️', color: 'orange' },
  MEDIUM: { threshold: 1.2, emoji: '⚡', color: 'yellow' },
  LOW: { threshold: 1.0, emoji: '📊', color: 'blue' }
};

class PerformanceBudgetChecker {
  constructor(resultsFile) {
    this.resultsFile = resultsFile;
    this.violations = [];
    this.results = [];
  }

  async checkBudgets() {
    console.log('🔍 Checking performance budgets...\n');

    try {
      const testResults = this.loadTestResults();
      this.analyzeResults(testResults);
      this.generateReport();

      if (this.violations.length > 0) {
        this.handleViolations();
        return false;
      } else {
        console.log('✅ All performance budgets passed!\n');
        return true;
      }
    } catch (error) {
      console.error('❌ Error checking performance budgets:', error.message);
      return false;
    }
  }

  loadTestResults() {
    if (!fs.existsSync(this.resultsFile)) {
      throw new Error(`Test results file not found: ${this.resultsFile}`);
    }

    const content = fs.readFileSync(this.resultsFile, 'utf8');
    return JSON.parse(content);
  }

  analyzeResults(testResults) {
    const suites = testResults.suites || [];

    suites.forEach(suite => {
      this.analyzeSuite(suite);
    });
  }

  analyzeSuite(suite) {
    if (suite.suites) {
      suite.suites.forEach(subSuite => {
        this.analyzeSuite(subSuite);
      });
    }

    if (suite.specs) {
      suite.specs.forEach(spec => {
        this.analyzeSpec(spec);
      });
    }
  }

  analyzeSpec(spec) {
    spec.tests.forEach(test => {
      this.analyzeTest(test);
    });
  }

  analyzeTest(test) {
    // Extract performance metrics from test annotations or custom measurements
    const performanceData = this.extractPerformanceData(test);

    if (performanceData) {
      const budgetKey = this.identifyBudgetCategory(test.title);
      const budget = PERFORMANCE_BUDGETS[budgetKey];

      if (budget) {
        this.checkTestAgainstBudget(test, performanceData, budget, budgetKey);
      }
    }
  }

  extractPerformanceData(test) {
    // Look for performance data in test annotations or attachments
    const annotations = test.annotations || [];
    const performanceAnnotation = annotations.find(ann =>
      ann.type === 'performance' || ann.description?.includes('performance')
    );

    if (performanceAnnotation) {
      try {
        return JSON.parse(performanceAnnotation.description);
      } catch (e) {
        // Fallback to parsing from test title or other sources
      }
    }

    // Extract from test results if available
    if (test.results && test.results.length > 0) {
      const result = test.results[0];
      if (result.attachments) {
        const perfAttachment = result.attachments.find(att =>
          att.name?.includes('performance') || att.contentType === 'application/json'
        );

        if (perfAttachment && perfAttachment.path) {
          try {
            const perfData = fs.readFileSync(perfAttachment.path, 'utf8');
            return JSON.parse(perfData);
          } catch (e) {
            // Continue without performance data
          }
        }
      }
    }

    // Mock performance data for demonstration (remove in production)
    if (process.env.NODE_ENV === 'test' || process.env.MOCK_PERFORMANCE_DATA === 'true') {
      return {
        loadTime: Math.random() * 4000,
        fcp: Math.random() * 3000,
        lcp: Math.random() * 4000,
        cls: Math.random() * 0.2,
        fid: Math.random() * 200
      };
    }

    return null;
  }

  identifyBudgetCategory(testTitle) {
    const title = testTitle.toLowerCase();

    if (title.includes('login') || title.includes('auth')) {
      return 'auth-login';
    } else if (title.includes('dashboard')) {
      return 'dashboard-load';
    } else if (title.includes('character') && title.includes('create')) {
      return 'character-create';
    } else if (title.includes('chat') || title.includes('message')) {
      return 'chat-response';
    } else if (title.includes('settings')) {
      return 'settings-save';
    }

    return null;
  }

  checkTestAgainstBudget(test, performanceData, budget, budgetKey) {
    const violations = [];

    Object.entries(budget).forEach(([metric, budgetValue]) => {
      const actualValue = performanceData[metric];

      if (actualValue !== undefined) {
        const ratio = actualValue / budgetValue;
        const severity = this.calculateSeverity(ratio);

        if (ratio > 1.0) {
          violations.push({
            test: test.title,
            category: budgetKey,
            metric,
            budget: budgetValue,
            actual: actualValue,
            ratio,
            severity,
            difference: actualValue - budgetValue
          });
        }
      }
    });

    if (violations.length > 0) {
      this.violations.push(...violations);
    }

    this.results.push({
      test: test.title,
      category: budgetKey,
      performanceData,
      budget,
      violations: violations.length,
      status: violations.length > 0 ? 'FAILED' : 'PASSED'
    });
  }

  calculateSeverity(ratio) {
    if (ratio >= SEVERITY_LEVELS.CRITICAL.threshold) return 'CRITICAL';
    if (ratio >= SEVERITY_LEVELS.HIGH.threshold) return 'HIGH';
    if (ratio >= SEVERITY_LEVELS.MEDIUM.threshold) return 'MEDIUM';
    return 'LOW';
  }

  generateReport() {
    console.log('📊 Performance Budget Report\n');
    console.log('=' .repeat(60));

    // Summary
    const totalTests = this.results.length;
    const passedTests = this.results.filter(r => r.status === 'PASSED').length;
    const failedTests = totalTests - passedTests;

    console.log(`Total Tests: ${totalTests}`);
    console.log(`Passed: ${passedTests} ✅`);
    console.log(`Failed: ${failedTests} ❌`);
    console.log('=' .repeat(60));

    // Violations by severity
    const violationsBySeverity = this.groupViolationsBySeverity();

    Object.entries(violationsBySeverity).forEach(([severity, violations]) => {
      if (violations.length > 0) {
        const level = SEVERITY_LEVELS[severity];
        console.log(`\n${level.emoji} ${severity} Violations (${violations.length}):`);

        violations.forEach(violation => {
          console.log(`  • ${violation.test}`);
          console.log(`    ${violation.metric}: ${violation.actual}ms > ${violation.budget}ms (${(violation.ratio * 100).toFixed(1)}%)`);
        });
      }
    });

    // Generate markdown report
    this.generateMarkdownReport();
  }

  groupViolationsBySeverity() {
    const groups = {
      CRITICAL: [],
      HIGH: [],
      MEDIUM: [],
      LOW: []
    };

    this.violations.forEach(violation => {
      groups[violation.severity].push(violation);
    });

    return groups;
  }

  generateMarkdownReport() {
    const reportPath = 'performance-budget-report.md';
    let markdown = '# Performance Budget Report\n\n';

    markdown += `**Generated:** ${new Date().toISOString()}\n`;
    markdown += `**Total Tests:** ${this.results.length}\n`;
    markdown += `**Violations:** ${this.violations.length}\n\n`;

    if (this.violations.length > 0) {
      markdown += '## Budget Violations\n\n';

      const violationsBySeverity = this.groupViolationsBySeverity();

      Object.entries(violationsBySeverity).forEach(([severity, violations]) => {
        if (violations.length > 0) {
          const level = SEVERITY_LEVELS[severity];
          markdown += `### ${level.emoji} ${severity} (${violations.length})\n\n`;

          violations.forEach(violation => {
            markdown += `- **${violation.test}**\n`;
            markdown += `  - Metric: ${violation.metric}\n`;
            markdown += `  - Budget: ${violation.budget}ms\n`;
            markdown += `  - Actual: ${violation.actual}ms\n`;
            markdown += `  - Ratio: ${(violation.ratio * 100).toFixed(1)}%\n\n`;
          });
        }
      });
    } else {
      markdown += '## ✅ All Performance Budgets Passed!\n\n';
    }

    markdown += '## Performance Budgets\n\n';
    Object.entries(PERFORMANCE_BUDGETS).forEach(([category, budget]) => {
      markdown += `### ${category}\n`;
      Object.entries(budget).forEach(([metric, value]) => {
        markdown += `- ${metric}: ${value}${metric.includes('Time') ? 'ms' : ''}\n`;
      });
      markdown += '\n';
    });

    fs.writeFileSync(reportPath, markdown);
    console.log(`\n📄 Detailed report saved to: ${reportPath}`);
  }

  handleViolations() {
    const criticalViolations = this.violations.filter(v => v.severity === 'CRITICAL');
    const highViolations = this.violations.filter(v => v.severity === 'HIGH');

    console.log('\n❌ Performance budget violations detected!\n');

    if (criticalViolations.length > 0) {
      console.log(`🚨 ${criticalViolations.length} CRITICAL violations found`);
    }

    if (highViolations.length > 0) {
      console.log(`⚠️ ${highViolations.length} HIGH violations found`);
    }

    console.log('\nRecommendations:');
    console.log('- Review and optimize slow-performing components');
    console.log('- Consider code splitting for large bundles');
    console.log('- Optimize images and assets');
    console.log('- Review database queries and API responses');
    console.log('- Consider implementing performance monitoring');

    // Set exit code based on severity
    if (criticalViolations.length > 0) {
      process.exitCode = 2; // Critical failures
    } else if (highViolations.length > 0) {
      process.exitCode = 1; // High severity failures
    }
  }
}

// Main execution
async function main() {
  const resultsFile = process.argv[2] || 'test-results/results.json';

  console.log('🚀 TTA Performance Budget Checker\n');
  console.log(`Results file: ${resultsFile}`);
  console.log(`Enable performance budgets: ${process.env.ENABLE_PERFORMANCE_BUDGETS || 'true'}\n`);

  if (process.env.ENABLE_PERFORMANCE_BUDGETS === 'false') {
    console.log('⏭️ Performance budget checking is disabled');
    return;
  }

  const checker = new PerformanceBudgetChecker(resultsFile);
  const success = await checker.checkBudgets();

  if (!success) {
    process.exit(process.exitCode || 1);
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error('💥 Unexpected error:', error);
    process.exit(1);
  });
}

module.exports = PerformanceBudgetChecker;
