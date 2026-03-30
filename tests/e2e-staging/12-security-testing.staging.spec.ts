// Logseq: [[TTA.dev/Tests/E2e-staging/12-security-testing.staging.spec]]
/**
 * Security Testing Suite for TTA Staging Environment
 *
 * Tests security vulnerabilities:
 * - XSS (Cross-Site Scripting)
 * - CSRF (Cross-Site Request Forgery)
 * - SQL Injection
 * - Authentication bypass
 * - Authorization bypass
 * - Sensitive data exposure
 * - Secure headers
 */

import { test, expect } from '@playwright/test';
import {
  testXSSVulnerability,
  testSQLInjection,
  testCSRFProtection,
  testAuthenticationBypass,
  testAuthorizationBypass,
  testSensitiveDataExposure,
  testSecureHeaders,
  testHTTPSEnforcement,
  generateSecurityTestReport,
} from './helpers/security-testing-helpers';
import { STAGING_CONFIG } from './helpers/staging-config';

test.describe('Security Testing', () => {
  test.setTimeout(60000); // 1 minute for security tests

  test('should protect against XSS attacks', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const result = await testXSSVulnerability(page, 'input[name="username"]');

    expect(result.passed).toBeTruthy();
    expect(result.severity).toBe('critical');
  });

  test('should protect against SQL injection', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const result = await testSQLInjection(page, 'input[name="username"]');

    expect(result.passed).toBeTruthy();
    expect(result.severity).toBe('critical');
  });

  test('should implement CSRF protection', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const result = await testCSRFProtection(page);

    expect(result.passed).toBeTruthy();
    expect(result.severity).toBe('high');
  });

  test('should prevent authentication bypass', async ({ page }) => {
    const result = await testAuthenticationBypass(page, `${STAGING_CONFIG.frontend.url}/gameplay`);

    expect(result.passed).toBeTruthy();
    expect(result.severity).toBe('critical');
  });

  test('should prevent authorization bypass', async ({ page }) => {
    // First login as regular user
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const usernameInput = page.locator('input[name="username"]').first();
    const passwordInput = page.locator('input[name="password"]').first();

    await usernameInput.fill('testuser');
    await passwordInput.fill('password123');

    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    await page.waitForTimeout(2000);

    // Try to access admin area
    const result = await testAuthorizationBypass(
      page,
      `${STAGING_CONFIG.frontend.url}/admin`,
      'user'
    );

    expect(result.passed).toBeTruthy();
    expect(result.severity).toBe('critical');
  });

  test('should not expose sensitive data', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const result = await testSensitiveDataExposure(page);

    expect(result.passed).toBeTruthy();
    expect(result.severity).toBe('critical');
  });

  test('should implement secure headers', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const result = await testSecureHeaders(page);

    // Should have at least some security headers
    expect(result.passed).toBeTruthy();
  });

  test('should enforce HTTPS', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const result = await testHTTPSEnforcement(page);

    // In staging, HTTPS may not be enforced, but should be noted
    if (STAGING_CONFIG.frontend.url.startsWith('https')) {
      expect(result.passed).toBeTruthy();
    }
  });

  test('should validate all security tests', async ({ page }) => {
    const results = [];

    // Run all security tests
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    results.push(await testXSSVulnerability(page, 'input[name="username"]'));
    results.push(await testSQLInjection(page, 'input[name="username"]'));
    results.push(await testCSRFProtection(page));
    results.push(await testAuthenticationBypass(page, `${STAGING_CONFIG.frontend.url}/gameplay`));
    results.push(await testSensitiveDataExposure(page));
    results.push(await testSecureHeaders(page));

    console.log(generateSecurityTestReport(results));

    // Count critical issues
    const criticalIssues = results.filter((r) => r.severity === 'critical' && !r.passed);

    // Should have no critical security issues
    expect(criticalIssues.length).toBe(0);
  });

  test('should handle malicious input gracefully', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const maliciousInputs = [
      '<script>alert("XSS")</script>',
      "'; DROP TABLE users; --",
      '<img src=x onerror="alert(\'XSS\')">',
      '${7*7}',
      '{{7*7}}',
    ];

    for (const input of maliciousInputs) {
      const usernameInput = page.locator('input[name="username"]').first();
      await usernameInput.fill(input);

      // Should not crash or execute malicious code
      const isPageStable = await page.evaluate(() => {
        return document.readyState === 'complete';
      });

      expect(isPageStable).toBeTruthy();
    }
  });

  test('should validate input sanitization', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const usernameInput = page.locator('input[name="username"]').first();

    // Try to inject HTML
    await usernameInput.fill('<b>bold</b>');

    // Get the value back
    const value = await usernameInput.inputValue();

    // Should be sanitized (not contain HTML tags)
    expect(value).not.toContain('<');
    expect(value).not.toContain('>');
  });
});
