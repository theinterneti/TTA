import { test as base } from '@playwright/test';
import { startCoverage, stopCoverage } from '../utils/coverage-helper';

/**
 * Extended test fixture that automatically collects code coverage
 */
export const test = base.extend({
  page: async ({ page }, use, testInfo) => {
    // Start coverage collection before each test
    if (process.env.COLLECT_COVERAGE === 'true') {
      await startCoverage(page);
    }

    // Run the test
    await use(page);

    // Stop coverage collection after each test
    if (process.env.COLLECT_COVERAGE === 'true') {
      const testName = testInfo.title.replace(/[^a-z0-9]/gi, '-');
      await stopCoverage(page, testName);
    }
  },
});

export { expect } from '@playwright/test';
