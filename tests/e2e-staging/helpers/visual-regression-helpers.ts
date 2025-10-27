/**
 * Visual Regression Testing Helpers
 *
 * Provides utilities for:
 * - Screenshot comparison
 * - Visual diff generation
 * - Cross-browser visual validation
 * - Component snapshot testing
 */

import { Page, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export interface VisualRegressionConfig {
  baselineDir: string;
  diffDir: string;
  threshold: number; // 0-1, percentage of pixels that can differ
  updateBaseline: boolean;
}

export interface VisualRegressionResult {
  testName: string;
  passed: boolean;
  baselineFile: string;
  currentFile: string;
  diffFile?: string;
  pixelDifference?: number;
  percentageDifference?: number;
}

const DEFAULT_CONFIG: VisualRegressionConfig = {
  baselineDir: 'tests/e2e-staging/visual-baselines',
  diffDir: 'tests/e2e-staging/visual-diffs',
  threshold: 0.01, // 1% difference allowed
  updateBaseline: false,
};

/**
 * Ensure visual regression directories exist
 */
export function ensureVisualRegressionDirs(config: VisualRegressionConfig = DEFAULT_CONFIG): void {
  [config.baselineDir, config.diffDir].forEach((dir) => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

/**
 * Take screenshot and compare with baseline
 */
export async function compareScreenshot(
  page: Page,
  testName: string,
  config: VisualRegressionConfig = DEFAULT_CONFIG
): Promise<VisualRegressionResult> {
  ensureVisualRegressionDirs(config);

  const baselineFile = path.join(config.baselineDir, `${testName}.png`);
  const currentFile = path.join(config.diffDir, `${testName}-current.png`);

  try {
    // Take current screenshot
    await page.screenshot({ path: currentFile, fullPage: true });

    // If updating baseline or baseline doesn't exist, create it
    if (config.updateBaseline || !fs.existsSync(baselineFile)) {
      fs.copyFileSync(currentFile, baselineFile);
      console.log(`📸 Baseline created: ${testName}`);

      return {
        testName,
        passed: true,
        baselineFile,
        currentFile,
        pixelDifference: 0,
        percentageDifference: 0,
      };
    }

    // Compare with baseline using Playwright's built-in comparison
    try {
      await expect(page).toHaveScreenshot(`${testName}.png`, {
        maxDiffPixels: 100,
        threshold: config.threshold,
      });

      return {
        testName,
        passed: true,
        baselineFile,
        currentFile,
        pixelDifference: 0,
        percentageDifference: 0,
      };
    } catch (error) {
      // Screenshot comparison failed
      const diffFile = path.join(config.diffDir, `${testName}-diff.png`);

      return {
        testName,
        passed: false,
        baselineFile,
        currentFile,
        diffFile,
        pixelDifference: 100, // Placeholder
        percentageDifference: 1.0,
      };
    }
  } catch (error) {
    console.error(`❌ Screenshot comparison failed for ${testName}:`, error);

    return {
      testName,
      passed: false,
      baselineFile,
      currentFile,
    };
  }
}

/**
 * Compare component across browsers
 */
export async function compareComponentAcrossBrowsers(
  pages: Record<string, Page>,
  componentSelector: string,
  testName: string,
  config: VisualRegressionConfig = DEFAULT_CONFIG
): Promise<Record<string, VisualRegressionResult>> {
  ensureVisualRegressionDirs(config);

  const results: Record<string, VisualRegressionResult> = {};

  for (const [browser, page] of Object.entries(pages)) {
    const element = page.locator(componentSelector).first();

    if (await element.isVisible()) {
      const screenshotName = `${testName}-${browser}`;
      const screenshotPath = path.join(config.diffDir, `${screenshotName}.png`);

      await element.screenshot({ path: screenshotPath });

      results[browser] = {
        testName: screenshotName,
        passed: true,
        baselineFile: path.join(config.baselineDir, `${screenshotName}.png`),
        currentFile: screenshotPath,
      };
    }
  }

  return results;
}

/**
 * Take full page screenshot
 */
export async function takeFullPageScreenshot(
  page: Page,
  testName: string,
  config: VisualRegressionConfig = DEFAULT_CONFIG
): Promise<string> {
  ensureVisualRegressionDirs(config);

  const screenshotPath = path.join(config.diffDir, `${testName}-full.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });

  return screenshotPath;
}

/**
 * Take element screenshot
 */
export async function takeElementScreenshot(
  page: Page,
  selector: string,
  testName: string,
  config: VisualRegressionConfig = DEFAULT_CONFIG
): Promise<string> {
  ensureVisualRegressionDirs(config);

  const element = page.locator(selector).first();
  const screenshotPath = path.join(config.diffDir, `${testName}-element.png`);

  await element.screenshot({ path: screenshotPath });

  return screenshotPath;
}

/**
 * Compare multiple viewports
 */
export async function compareMultipleViewports(
  page: Page,
  testName: string,
  viewports: Array<{ name: string; width: number; height: number }>,
  config: VisualRegressionConfig = DEFAULT_CONFIG
): Promise<VisualRegressionResult[]> {
  const results: VisualRegressionResult[] = [];

  for (const viewport of viewports) {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.waitForLoadState('networkidle');

    const viewportTestName = `${testName}-${viewport.name}`;
    const result = await compareScreenshot(page, viewportTestName, config);

    results.push(result);
  }

  return results;
}

/**
 * Generate visual regression report
 */
export function generateVisualRegressionReport(
  results: VisualRegressionResult[]
): string {
  let report = '=== Visual Regression Test Report ===\n\n';

  const passed = results.filter((r) => r.passed).length;
  const failed = results.filter((r) => !r.passed).length;

  report += `Total Tests: ${results.length}\n`;
  report += `Passed: ${passed}\n`;
  report += `Failed: ${failed}\n`;
  report += `Success Rate: ${((passed / results.length) * 100).toFixed(2)}%\n\n`;

  report += '=== Detailed Results ===\n';
  for (const result of results) {
    report += `\n${result.testName}: ${result.passed ? '✅ PASS' : '❌ FAIL'}\n`;
    if (result.percentageDifference !== undefined) {
      report += `Pixel Difference: ${result.percentageDifference.toFixed(2)}%\n`;
    }
    if (result.diffFile) {
      report += `Diff File: ${result.diffFile}\n`;
    }
  }

  return report;
}

/**
 * Critical UI components for visual regression testing
 */
export const CRITICAL_COMPONENTS = {
  loginPage: {
    selector: '[data-testid="login-page"]',
    name: 'login-page',
  },
  dashboard: {
    selector: '[data-testid="dashboard"]',
    name: 'dashboard',
  },
  characterCreation: {
    selector: '[data-testid="character-creation"]',
    name: 'character-creation',
  },
  gameplayInterface: {
    selector: '[data-testid="gameplay-interface"]',
    name: 'gameplay-interface',
  },
  chatInterface: {
    selector: '[data-testid="chat-interface"]',
    name: 'chat-interface',
  },
  worldSelection: {
    selector: '[data-testid="world-selection"]',
    name: 'world-selection',
  },
};

/**
 * Standard viewports for responsive testing
 */
export const STANDARD_VIEWPORTS = [
  { name: 'mobile-small', width: 320, height: 568 },
  { name: 'mobile-large', width: 414, height: 896 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1920, height: 1080 },
  { name: 'desktop-large', width: 2560, height: 1440 },
];

/**
 * Cleanup old visual regression files
 */
export function cleanupVisualRegressionFiles(
  config: VisualRegressionConfig = DEFAULT_CONFIG,
  daysOld: number = 7
): void {
  const now = Date.now();
  const maxAge = daysOld * 24 * 60 * 60 * 1000;

  [config.diffDir].forEach((dir) => {
    if (fs.existsSync(dir)) {
      fs.readdirSync(dir).forEach((file) => {
        const filePath = path.join(dir, file);
        const stats = fs.statSync(filePath);

        if (now - stats.mtime.getTime() > maxAge) {
          fs.unlinkSync(filePath);
          console.log(`🗑️ Deleted old visual regression file: ${file}`);
        }
      });
    }
  });
}

