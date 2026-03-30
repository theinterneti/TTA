// Logseq: [[TTA.dev/Tests/E2e/Utils/Coverage-helper]]
import { Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Coverage collection helper for Playwright E2E tests
 * Uses Chrome DevTools Protocol (CDP) to collect V8 coverage
 */

const COVERAGE_DIR = path.join(process.cwd(), '.nyc_output');
const COVERAGE_REPORT_DIR = path.join(process.cwd(), 'coverage');

/**
 * Ensure coverage directories exist
 */
export function ensureCoverageDirectories(): void {
  if (!fs.existsSync(COVERAGE_DIR)) {
    fs.mkdirSync(COVERAGE_DIR, { recursive: true });
  }
  if (!fs.existsSync(COVERAGE_REPORT_DIR)) {
    fs.mkdirSync(COVERAGE_REPORT_DIR, { recursive: true });
  }
}

/**
 * Start coverage collection for a page
 */
export async function startCoverage(page: Page): Promise<void> {
  try {
    // Enable coverage via CDP
    const client = await page.context().newCDPSession(page);
    await client.send('Profiler.enable');
    await client.send('Profiler.startPreciseCoverage', {
      callCount: true,
      detailed: true,
    });

    // Store CDP session on page for later retrieval
    (page as any)._coverageSession = client;
  } catch (error) {
    console.warn('Failed to start coverage collection:', error);
  }
}

/**
 * Stop coverage collection and save results
 */
export async function stopCoverage(page: Page, testName: string): Promise<void> {
  try {
    const client = (page as any)._coverageSession;
    if (!client) {
      console.warn('No coverage session found for page');
      return;
    }

    // Collect coverage data
    const { result } = await client.send('Profiler.takePreciseCoverage');
    await client.send('Profiler.stopPreciseCoverage');
    await client.detach();

    // Filter coverage to only include our source files
    const filteredCoverage = result.filter((entry: any) => {
      const url = entry.url;
      return (
        url.includes('/src/') &&
        !url.includes('node_modules') &&
        !url.includes('test') &&
        (url.endsWith('.js') || url.endsWith('.jsx') || url.endsWith('.ts') || url.endsWith('.tsx'))
      );
    });

    if (filteredCoverage.length > 0) {
      // Save coverage data
      ensureCoverageDirectories();
      const coverageFile = path.join(
        COVERAGE_DIR,
        `coverage-${testName.replace(/[^a-z0-9]/gi, '-')}-${Date.now()}.json`
      );

      fs.writeFileSync(
        coverageFile,
        JSON.stringify({ result: filteredCoverage }, null, 2)
      );
    }
  } catch (error) {
    console.warn('Failed to stop coverage collection:', error);
  }
}

/**
 * Merge all coverage files and generate report
 */
export async function generateCoverageReport(): Promise<void> {
  try {
    const coverageFiles = fs.readdirSync(COVERAGE_DIR).filter(f => f.startsWith('coverage-'));

    if (coverageFiles.length === 0) {
      console.log('No coverage data collected');
      return;
    }

    console.log(`\n📊 Merging ${coverageFiles.length} coverage files...`);

    // Merge all coverage data
    const allCoverage: any[] = [];
    for (const file of coverageFiles) {
      const data = JSON.parse(fs.readFileSync(path.join(COVERAGE_DIR, file), 'utf-8'));
      if (data.result) {
        allCoverage.push(...data.result);
      }
    }

    // Calculate basic coverage statistics
    const stats = calculateCoverageStats(allCoverage);

    // Save merged coverage
    const mergedFile = path.join(COVERAGE_DIR, 'coverage-final.json');
    fs.writeFileSync(mergedFile, JSON.stringify({ result: allCoverage }, null, 2));

    // Generate HTML report (simplified version)
    generateHTMLReport(stats);

    // Print summary
    printCoverageSummary(stats);
  } catch (error) {
    console.error('Failed to generate coverage report:', error);
  }
}

/**
 * Calculate coverage statistics from V8 coverage data
 */
function calculateCoverageStats(coverage: any[]): any {
  const fileStats: Map<string, any> = new Map();

  for (const entry of coverage) {
    const url = entry.url;
    if (!fileStats.has(url)) {
      fileStats.set(url, {
        url,
        totalBytes: 0,
        coveredBytes: 0,
        functions: [],
      });
    }

    const stats = fileStats.get(url);
    for (const func of entry.functions || []) {
      stats.functions.push(func);
      for (const range of func.ranges || []) {
        stats.totalBytes += range.endOffset - range.startOffset;
        if (range.count > 0) {
          stats.coveredBytes += range.endOffset - range.startOffset;
        }
      }
    }
  }

  // Calculate overall statistics
  let totalBytes = 0;
  let coveredBytes = 0;
  let totalFunctions = 0;
  let coveredFunctions = 0;

  for (const stats of fileStats.values()) {
    totalBytes += stats.totalBytes;
    coveredBytes += stats.coveredBytes;
    totalFunctions += stats.functions.length;
    coveredFunctions += stats.functions.filter((f: any) =>
      f.ranges && f.ranges.some((r: any) => r.count > 0)
    ).length;
  }

  return {
    files: Array.from(fileStats.values()),
    overall: {
      totalBytes,
      coveredBytes,
      byteCoverage: totalBytes > 0 ? (coveredBytes / totalBytes) * 100 : 0,
      totalFunctions,
      coveredFunctions,
      functionCoverage: totalFunctions > 0 ? (coveredFunctions / totalFunctions) * 100 : 0,
    },
  };
}

/**
 * Generate HTML coverage report
 */
function generateHTMLReport(stats: any): void {
  const html = `
<!DOCTYPE html>
<html>
<head>
  <title>E2E Test Coverage Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
    .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
    .metric { background: #f9f9f9; padding: 15px; border-radius: 4px; border-left: 4px solid #4CAF50; }
    .metric h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
    .metric .value { font-size: 32px; font-weight: bold; color: #333; }
    .metric .label { font-size: 12px; color: #999; margin-top: 5px; }
    .high { border-left-color: #4CAF50; }
    .medium { border-left-color: #FF9800; }
    .low { border-left-color: #F44336; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #4CAF50; color: white; font-weight: bold; }
    tr:hover { background: #f5f5f5; }
    .coverage-bar { height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; }
    .coverage-fill { height: 100%; background: #4CAF50; transition: width 0.3s; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 E2E Test Coverage Report</h1>
    <p>Generated: ${new Date().toLocaleString()}</p>

    <div class="summary">
      <div class="metric ${getCoverageClass(stats.overall.byteCoverage)}">
        <h3>Byte Coverage</h3>
        <div class="value">${stats.overall.byteCoverage.toFixed(2)}%</div>
        <div class="label">${stats.overall.coveredBytes} / ${stats.overall.totalBytes} bytes</div>
      </div>

      <div class="metric ${getCoverageClass(stats.overall.functionCoverage)}">
        <h3>Function Coverage</h3>
        <div class="value">${stats.overall.functionCoverage.toFixed(2)}%</div>
        <div class="label">${stats.overall.coveredFunctions} / ${stats.overall.totalFunctions} functions</div>
      </div>

      <div class="metric">
        <h3>Files Analyzed</h3>
        <div class="value">${stats.files.length}</div>
        <div class="label">Source files</div>
      </div>
    </div>

    <h2>File Coverage Details</h2>
    <table>
      <thead>
        <tr>
          <th>File</th>
          <th>Coverage</th>
          <th>Functions</th>
        </tr>
      </thead>
      <tbody>
        ${stats.files.map((file: any) => {
          const coverage = file.totalBytes > 0 ? (file.coveredBytes / file.totalBytes) * 100 : 0;
          const coveredFuncs = file.functions.filter((f: any) =>
            f.ranges && f.ranges.some((r: any) => r.count > 0)
          ).length;
          return `
            <tr>
              <td>${file.url.split('/').pop()}</td>
              <td>
                <div class="coverage-bar">
                  <div class="coverage-fill" style="width: ${coverage}%"></div>
                </div>
                ${coverage.toFixed(1)}%
              </td>
              <td>${coveredFuncs} / ${file.functions.length}</td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  </div>
</body>
</html>
  `;

  fs.writeFileSync(path.join(COVERAGE_REPORT_DIR, 'index.html'), html);
  console.log(`\n✅ HTML report generated: ${path.join(COVERAGE_REPORT_DIR, 'index.html')}`);
}

function getCoverageClass(percentage: number): string {
  if (percentage >= 80) return 'high';
  if (percentage >= 50) return 'medium';
  return 'low';
}

/**
 * Print coverage summary to console
 */
function printCoverageSummary(stats: any): void {
  console.log('\n' + '='.repeat(60));
  console.log('📊 E2E TEST COVERAGE SUMMARY');
  console.log('='.repeat(60));
  console.log(`\n📁 Files Analyzed: ${stats.files.length}`);
  console.log(`\n📈 Overall Coverage:`);
  console.log(`   Bytes:     ${stats.overall.byteCoverage.toFixed(2)}% (${stats.overall.coveredBytes}/${stats.overall.totalBytes})`);
  console.log(`   Functions: ${stats.overall.functionCoverage.toFixed(2)}% (${stats.overall.coveredFunctions}/${stats.overall.totalFunctions})`);
  console.log('\n' + '='.repeat(60) + '\n');
}
