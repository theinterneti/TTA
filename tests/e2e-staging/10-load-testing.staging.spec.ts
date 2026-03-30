// Logseq: [[TTA.dev/Tests/E2e-staging/10-load-testing.staging.spec]]
/**
 * Load Testing Suite for TTA Staging Environment
 *
 * Tests system performance under concurrent user load:
 * - 10 concurrent users (normal load)
 * - 25 concurrent users (high load)
 * - 50 concurrent users (stress test)
 */

import { test, expect } from '@playwright/test';
import {
  simulateConcurrentUsers,
  standardUserJourney,
  NORMAL_LOAD_CONFIG,
  STRESS_TEST_CONFIG,
  validateLoadTestResults,
  generateLoadTestReport,
} from './helpers/load-testing-helpers';

test.describe('Load Testing', () => {
  test.setTimeout(600000); // 10 minutes for load tests

  test('should handle 10 concurrent users', async () => {
    const result = await simulateConcurrentUsers(NORMAL_LOAD_CONFIG, standardUserJourney);

    console.log(generateLoadTestReport(result));

    const validation = validateLoadTestResults(result, {
      maxErrorRate: 5,
      maxP95ResponseTime: 3000,
      maxP99ResponseTime: 5000,
      minThroughput: 1,
    });

    expect(validation.passed).toBeTruthy();
    expect(result.errorRate).toBeLessThan(5);
    expect(result.p95ResponseTime).toBeLessThan(3000);
  });

  test('should handle 25 concurrent users', async () => {
    const config = {
      concurrentUsers: 25,
      rampUpTime: 60,
      testDuration: 180,
      thinkTime: 1000,
    };

    const result = await simulateConcurrentUsers(config, standardUserJourney);

    console.log(generateLoadTestReport(result));

    const validation = validateLoadTestResults(result, {
      maxErrorRate: 10,
      maxP95ResponseTime: 5000,
      maxP99ResponseTime: 8000,
      minThroughput: 0.5,
    });

    expect(validation.passed).toBeTruthy();
    expect(result.errorRate).toBeLessThan(10);
  });

  test('should handle 50 concurrent users (stress test)', async () => {
    const result = await simulateConcurrentUsers(STRESS_TEST_CONFIG, standardUserJourney);

    console.log(generateLoadTestReport(result));

    const validation = validateLoadTestResults(result, {
      maxErrorRate: 20,
      maxP95ResponseTime: 10000,
      maxP99ResponseTime: 15000,
      minThroughput: 0.2,
    });

    // Stress test may have higher error rates but should still be somewhat functional
    expect(result.errorRate).toBeLessThan(20);
    expect(result.p99ResponseTime).toBeLessThan(15000);
  });

  test('should maintain response times under load', async () => {
    const result = await simulateConcurrentUsers(NORMAL_LOAD_CONFIG, standardUserJourney);

    // Response times should not degrade significantly
    expect(result.averageResponseTime).toBeLessThan(2000);
    expect(result.maxResponseTime).toBeLessThan(10000);
  });

  test('should have acceptable throughput', async () => {
    const result = await simulateConcurrentUsers(NORMAL_LOAD_CONFIG, standardUserJourney);

    // Should handle at least 1 request per second
    expect(result.throughput).toBeGreaterThan(1);
  });
});
