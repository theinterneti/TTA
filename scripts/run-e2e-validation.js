// Logseq: [[TTA.dev/Scripts/Run-e2e-validation]]
#!/usr/bin/env node
/**
 * Comprehensive E2E Validation Runner
 *
 * Executes all 7 phases of E2E testing and generates detailed reports
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const REPORT_DIR = 'test-results-staging';
const TIMESTAMP = new Date().toISOString().replace(/[:.]/g, '-');
const SUMMARY_FILE = path.join(REPORT_DIR, `validation-summary-${TIMESTAMP}.md`);

// Ensure report directory exists
if (!fs.existsSync(REPORT_DIR)) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

// Test phases
const phases = [
  {
    num: 1,
    name: 'Authentication & Core Flow',
    file: '01-authentication.staging.spec.ts',
    priority: 'CRITICAL'
  },
  {
    num: 2,
    name: 'UI/UX Functionality',
    file: '02-ui-functionality.staging.spec.ts',
    priority: 'HIGH'
  },
  {
    num: 3,
    name: 'Integration Testing',
    file: '03-integration.staging.spec.ts',
    priority: 'HIGH'
  },
  {
    num: 4,
    name: 'Error Handling & Resilience',
    file: '04-error-handling.staging.spec.ts',
    priority: 'MEDIUM'
  },
  {
    num: 5,
    name: 'Responsive Design & Mobile',
    file: '05-responsive.staging.spec.ts',
    priority: 'MEDIUM'
  },
  {
    num: 6,
    name: 'Accessibility Compliance',
    file: '06-accessibility.staging.spec.ts',
    priority: 'LOW'
  },
  {
    num: 7,
    name: 'Complete User Journey',
    file: 'complete-user-journey.staging.spec.ts',
    priority: 'FINAL'
  }
];

// Results tracking
const results = {
  total: phases.length,
  passed: 0,
  failed: 0,
  phases: []
};

console.log('╔══════════════════════════════════════════════════════════════════╗');
console.log('║     TTA Staging - Comprehensive E2E Validation Execution        ║');
console.log('╚══════════════════════════════════════════════════════════════════╝');
console.log('');
console.log(`Timestamp: ${new Date().toLocaleString()}`);
console.log(`Report Directory: ${REPORT_DIR}`);
console.log('');

// Initialize summary file
let summary = `# TTA Staging Environment - E2E Validation Summary\n\n`;
summary += `**Execution Started:** ${new Date().toLocaleString()}\n\n`;
summary += `## Test Execution Overview\n\n`;

// Run each phase
for (const phase of phases) {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`Phase ${phase.num}/${phases.length}: ${phase.name}`);
  console.log(`Priority: ${phase.priority} | Test File: ${phase.file}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('');

  summary += `### Phase ${phase.num}: ${phase.name}\n\n`;
  summary += `- **Priority:** ${phase.priority}\n`;
  summary += `- **Test File:** \`tests/e2e-staging/${phase.file}\`\n`;
  summary += `- **Started:** ${new Date().toLocaleString()}\n\n`;

  const logFile = path.join(REPORT_DIR, `phase-${phase.num}-execution.log`);
  const testPath = `tests/e2e-staging/${phase.file}`;

  console.log(`▶ Running tests on Chromium browser...`);

  try {
    const output = execSync(
      `npx playwright test "${testPath}" --config=playwright.staging.config.ts --project=chromium --reporter=list --retries=1 --timeout=90000`,
      {
        encoding: 'utf8',
        stdio: 'pipe',
        maxBuffer: 10 * 1024 * 1024 // 10MB buffer
      }
    );

    // Write output to log file
    fs.writeFileSync(logFile, output);

    console.log(`✓ Phase ${phase.num} PASSED`);
    summary += `- **Status:** ✅ PASSED\n`;
    results.passed++;

    results.phases.push({
      ...phase,
      status: 'PASSED',
      output: output.substring(0, 500) // First 500 chars
    });

  } catch (error) {
    const output = error.stdout || error.stderr || error.message;

    // Write output to log file
    fs.writeFileSync(logFile, output);

    console.log(`✗ Phase ${phase.num} FAILED`);
    console.log(`  See log: ${logFile}`);
    summary += `- **Status:** ❌ FAILED\n`;
    summary += `\n**Failure Summary:**\n\`\`\`\n${output.substring(output.length - 1000)}\n\`\`\`\n`;
    results.failed++;

    results.phases.push({
      ...phase,
      status: 'FAILED',
      output: output.substring(output.length - 500) // Last 500 chars
    });
  }

  summary += `- **Completed:** ${new Date().toLocaleString()}\n\n`;
  summary += `---\n\n`;

  console.log('');
}

// Generate final summary
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('Validation Complete - Generating Summary');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('');

summary += `## Final Results\n\n`;
summary += `### Statistics\n\n`;
summary += `- **Total Phases:** ${results.total}\n`;
summary += `- **Passed:** ${results.passed}\n`;
summary += `- **Failed:** ${results.failed}\n`;
summary += `- **Success Rate:** ${Math.round((results.passed / results.total) * 100)}%\n\n`;
summary += `### Production Readiness Assessment\n\n`;

if (results.failed === 0) {
  summary += `**Overall Status:** ✅ PRODUCTION READY\n\n`;
  console.log('╔══════════════════════════════════════════════════════════════════╗');
  console.log('║                  ✓ ALL PHASES PASSED                             ║');
  console.log('║              STAGING ENVIRONMENT IS READY                        ║');
  console.log('╚══════════════════════════════════════════════════════════════════╝');
} else if (results.failed <= 2) {
  summary += `**Overall Status:** ⚠️  NEEDS ATTENTION (Minor Issues)\n\n`;
  console.log('╔══════════════════════════════════════════════════════════════════╗');
  console.log('║              ⚠ SOME PHASES FAILED                                ║');
  console.log('║          REVIEW FAILURES BEFORE PRODUCTION                       ║');
  console.log('╚══════════════════════════════════════════════════════════════════╝');
} else {
  summary += `**Overall Status:** ❌ NOT PRODUCTION READY (Critical Issues)\n\n`;
  console.log('╔══════════════════════════════════════════════════════════════════╗');
  console.log('║            ✗ MULTIPLE PHASES FAILED                              ║');
  console.log('║        CRITICAL ISSUES MUST BE RESOLVED                          ║');
  console.log('╚══════════════════════════════════════════════════════════════════╝');
}

summary += `\n**Execution Completed:** ${new Date().toLocaleString()}\n\n`;

// Write summary file
fs.writeFileSync(SUMMARY_FILE, summary);

// Write JSON results
const jsonFile = path.join(REPORT_DIR, `validation-results-${TIMESTAMP}.json`);
fs.writeFileSync(jsonFile, JSON.stringify(results, null, 2));

console.log('');
console.log(`Results Summary:`);
console.log(`  Passed: ${results.passed}/${results.total}`);
console.log(`  Failed: ${results.failed}/${results.total}`);
console.log('');
console.log(`Detailed Report: ${SUMMARY_FILE}`);
console.log(`JSON Results: ${jsonFile}`);
console.log(`HTML Report: npx playwright show-report playwright-staging-report`);
console.log('');

process.exit(results.failed > 0 ? 1 : 0);
