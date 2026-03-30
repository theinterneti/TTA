// Logseq: [[TTA.dev/Tests/E2e-staging/Helpers/Performance-helpers]]
/**
 * Performance Monitoring Helpers for E2E Tests
 *
 * Provides utilities for measuring and validating performance metrics
 * including page load times, API response times, and user interaction latency.
 */

import { Page } from '@playwright/test';
import { STAGING_CONFIG } from './staging-config';

export interface PerformanceMetrics {
  pageLoadTime: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  timeToInteractive: number;
  apiResponseTimes: number[];
  averageApiResponseTime: number;
}

/**
 * Measure page load performance
 */
export async function measurePageLoadPerformance(page: Page): Promise<PerformanceMetrics> {
  const metrics = await page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const paintEntries = performance.getEntriesByType('paint');
    const resourceEntries = performance.getEntriesByType('resource');

    const fcp = paintEntries.find((entry) => entry.name === 'first-contentful-paint')?.startTime || 0;
    const lcp = Math.max(
      ...performance.getEntriesByType('largest-contentful-paint').map((entry) => entry.startTime)
    );

    const cls = performance.getEntriesByType('layout-shift').reduce((sum, entry: any) => {
      return sum + (entry.hadRecentInput ? 0 : entry.value);
    }, 0);

    const apiTimes = resourceEntries
      .filter((entry) => entry.name.includes('/api/'))
      .map((entry) => entry.duration);

    return {
      pageLoadTime: navigation.loadEventEnd - navigation.loadEventStart,
      firstContentfulPaint: fcp,
      largestContentfulPaint: lcp,
      cumulativeLayoutShift: cls,
      timeToInteractive: navigation.domInteractive - navigation.fetchStart,
      apiResponseTimes: apiTimes,
      averageApiResponseTime: apiTimes.length > 0 ? apiTimes.reduce((a, b) => a + b) / apiTimes.length : 0,
    };
  });

  return metrics;
}

/**
 * Measure API response time
 */
export async function measureApiResponseTime(
  page: Page,
  urlPattern: string | RegExp,
  action: () => Promise<void>
): Promise<number> {
  const startTime = Date.now();

  const responsePromise = page.waitForResponse((response) => {
    const url = response.url();
    if (typeof urlPattern === 'string') {
      return url.includes(urlPattern);
    }
    return urlPattern.test(url);
  });

  await action();
  await responsePromise;

  return Date.now() - startTime;
}

/**
 * Measure interaction latency
 */
export async function measureInteractionLatency(
  page: Page,
  selector: string,
  action: 'click' | 'type' = 'click'
): Promise<number> {
  const startTime = Date.now();

  const element = page.locator(selector).first();

  if (action === 'click') {
    await element.click();
  } else if (action === 'type') {
    await element.type('test');
  }

  // Wait for any resulting network activity
  await page.waitForLoadState('networkidle').catch(() => {});

  return Date.now() - startTime;
}

/**
 * Validate performance against budgets
 */
export function validatePerformanceBudgets(metrics: PerformanceMetrics): {
  passed: boolean;
  violations: string[];
} {
  const violations: string[] = [];

  if (metrics.pageLoadTime > STAGING_CONFIG.performance.pageLoad) {
    violations.push(
      `Page load time ${metrics.pageLoadTime}ms exceeds budget ${STAGING_CONFIG.performance.pageLoad}ms`
    );
  }

  if (metrics.averageApiResponseTime > STAGING_CONFIG.performance.apiResponse) {
    violations.push(
      `Average API response time ${metrics.averageApiResponseTime}ms exceeds budget ${STAGING_CONFIG.performance.apiResponse}ms`
    );
  }

  if (metrics.firstContentfulPaint > 2000) {
    violations.push(`First Contentful Paint ${metrics.firstContentfulPaint}ms exceeds 2000ms`);
  }

  if (metrics.cumulativeLayoutShift > 0.1) {
    violations.push(`Cumulative Layout Shift ${metrics.cumulativeLayoutShift} exceeds 0.1`);
  }

  return {
    passed: violations.length === 0,
    violations,
  };
}

/**
 * Monitor performance during user journey
 */
export class PerformanceMonitor {
  private page: Page;
  private metrics: PerformanceMetrics[] = [];
  private apiResponseTimes: Map<string, number[]> = new Map();

  constructor(page: Page) {
    this.page = page;
    this.setupResponseListener();
  }

  /**
   * Setup listener for API responses
   */
  private setupResponseListener(): void {
    this.page.on('response', (response) => {
      const url = response.url();
      const status = response.status();

      if (url.includes('/api/')) {
        const timing = response.request().postDataBuffer?.length || 0;
        const endpoint = new URL(url).pathname;

        if (!this.apiResponseTimes.has(endpoint)) {
          this.apiResponseTimes.set(endpoint, []);
        }

        this.apiResponseTimes.get(endpoint)!.push(timing);
      }
    });
  }

  /**
   * Record page load metrics
   */
  async recordPageLoadMetrics(): Promise<void> {
    const metrics = await measurePageLoadPerformance(this.page);
    this.metrics.push(metrics);
  }

  /**
   * Get average metrics
   */
  getAverageMetrics(): PerformanceMetrics {
    if (this.metrics.length === 0) {
      return {
        pageLoadTime: 0,
        firstContentfulPaint: 0,
        largestContentfulPaint: 0,
        cumulativeLayoutShift: 0,
        timeToInteractive: 0,
        apiResponseTimes: [],
        averageApiResponseTime: 0,
      };
    }

    const sum = this.metrics.reduce(
      (acc, metric) => ({
        pageLoadTime: acc.pageLoadTime + metric.pageLoadTime,
        firstContentfulPaint: acc.firstContentfulPaint + metric.firstContentfulPaint,
        largestContentfulPaint: acc.largestContentfulPaint + metric.largestContentfulPaint,
        cumulativeLayoutShift: acc.cumulativeLayoutShift + metric.cumulativeLayoutShift,
        timeToInteractive: acc.timeToInteractive + metric.timeToInteractive,
        apiResponseTimes: [],
        averageApiResponseTime: 0,
      }),
      {
        pageLoadTime: 0,
        firstContentfulPaint: 0,
        largestContentfulPaint: 0,
        cumulativeLayoutShift: 0,
        timeToInteractive: 0,
        apiResponseTimes: [],
        averageApiResponseTime: 0,
      }
    );

    const count = this.metrics.length;

    return {
      pageLoadTime: sum.pageLoadTime / count,
      firstContentfulPaint: sum.firstContentfulPaint / count,
      largestContentfulPaint: sum.largestContentfulPaint / count,
      cumulativeLayoutShift: sum.cumulativeLayoutShift / count,
      timeToInteractive: sum.timeToInteractive / count,
      apiResponseTimes: [],
      averageApiResponseTime: sum.averageApiResponseTime / count,
    };
  }

  /**
   * Get API response time statistics
   */
  getApiStats(): Record<string, { min: number; max: number; average: number }> {
    const stats: Record<string, { min: number; max: number; average: number }> = {};

    for (const [endpoint, times] of this.apiResponseTimes) {
      if (times.length > 0) {
        stats[endpoint] = {
          min: Math.min(...times),
          max: Math.max(...times),
          average: times.reduce((a, b) => a + b) / times.length,
        };
      }
    }

    return stats;
  }

  /**
   * Generate performance report
   */
  generateReport(): string {
    const avgMetrics = this.getAverageMetrics();
    const apiStats = this.getApiStats();

    let report = '=== Performance Report ===\n\n';
    report += `Page Load Time: ${avgMetrics.pageLoadTime.toFixed(2)}ms\n`;
    report += `First Contentful Paint: ${avgMetrics.firstContentfulPaint.toFixed(2)}ms\n`;
    report += `Largest Contentful Paint: ${avgMetrics.largestContentfulPaint.toFixed(2)}ms\n`;
    report += `Cumulative Layout Shift: ${avgMetrics.cumulativeLayoutShift.toFixed(3)}\n`;
    report += `Time to Interactive: ${avgMetrics.timeToInteractive.toFixed(2)}ms\n\n`;

    report += '=== API Response Times ===\n';
    for (const [endpoint, stats] of Object.entries(apiStats)) {
      report += `${endpoint}: min=${stats.min.toFixed(2)}ms, avg=${stats.average.toFixed(2)}ms, max=${stats.max.toFixed(2)}ms\n`;
    }

    return report;
  }
}
