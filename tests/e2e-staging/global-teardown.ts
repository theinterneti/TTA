// Logseq: [[TTA.dev/Tests/E2e-staging/Global-teardown]]
/**
 * Global Teardown for Staging E2E Tests
 *
 * Cleanup after test execution
 */

import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('\n🧹 Cleaning up after staging tests...\n');

  // Add any cleanup logic here if needed
  // For staging, we typically leave the environment running

  console.log('✅ Cleanup complete\n');
}

export default globalTeardown;
