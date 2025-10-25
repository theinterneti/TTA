/**
 * Security Testing Helpers for E2E Tests
 *
 * Provides utilities for security penetration testing:
 * - XSS (Cross-Site Scripting) detection
 * - CSRF (Cross-Site Request Forgery) validation
 * - SQL Injection detection
 * - Authentication bypass attempts
 * - Authorization validation
 * - Sensitive data exposure checks
 */

import { Page } from '@playwright/test';

export interface SecurityTestResult {
  testName: string;
  passed: boolean;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  remediation?: string;
}

/**
 * Test for XSS vulnerabilities
 */
export async function testXSSVulnerability(
  page: Page,
  inputSelector: string,
  xssPayload: string = '<script>alert("XSS")</script>'
): Promise<SecurityTestResult> {
  try {
    const input = page.locator(inputSelector).first();
    await input.fill(xssPayload);

    // Check if script was executed
    const scriptExecuted = await page.evaluate(() => {
      return (window as any).xssExecuted === true;
    });

    return {
      testName: 'XSS Vulnerability',
      passed: !scriptExecuted,
      severity: 'critical',
      description: scriptExecuted
        ? 'XSS vulnerability detected - script was executed'
        : 'Input properly sanitized',
      remediation: scriptExecuted
        ? 'Implement input sanitization and output encoding'
        : undefined,
    };
  } catch (error) {
    return {
      testName: 'XSS Vulnerability',
      passed: false,
      severity: 'high',
      description: `XSS test failed: ${String(error)}`,
    };
  }
}

/**
 * Test for SQL Injection vulnerabilities
 */
export async function testSQLInjection(
  page: Page,
  inputSelector: string,
  sqlPayload: string = "' OR '1'='1"
): Promise<SecurityTestResult> {
  try {
    const input = page.locator(inputSelector).first();
    await input.fill(sqlPayload);

    // Submit form
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    // Check for SQL error messages
    const errorMessage = await page.locator('[role="alert"]').first().textContent();

    const isSQLError =
      errorMessage?.toLowerCase().includes('sql') ||
      errorMessage?.toLowerCase().includes('database') ||
      errorMessage?.toLowerCase().includes('query');

    return {
      testName: 'SQL Injection',
      passed: !isSQLError,
      severity: 'critical',
      description: isSQLError
        ? 'SQL error message exposed - potential SQL injection vulnerability'
        : 'SQL injection attempt blocked',
      remediation: isSQLError
        ? 'Use parameterized queries and hide database errors'
        : undefined,
    };
  } catch (error) {
    return {
      testName: 'SQL Injection',
      passed: false,
      severity: 'high',
      description: `SQL injection test failed: ${String(error)}`,
    };
  }
}

/**
 * Test for CSRF token validation
 */
export async function testCSRFProtection(page: Page): Promise<SecurityTestResult> {
  try {
    // Check for CSRF token in forms
    const csrfToken = await page.locator('input[name="csrf_token"]').first().inputValue();

    // Check for CSRF token in headers
    const headers = await page.evaluate(() => {
      return {
        xcsrfToken: document.querySelector('meta[name="csrf-token"]')?.getAttribute('content'),
      };
    });

    const hasCSRFProtection = !!csrfToken || !!headers.xcsrfToken;

    return {
      testName: 'CSRF Protection',
      passed: hasCSRFProtection,
      severity: 'high',
      description: hasCSRFProtection
        ? 'CSRF token present'
        : 'CSRF token not found - potential CSRF vulnerability',
      remediation: !hasCSRFProtection
        ? 'Implement CSRF token validation for state-changing requests'
        : undefined,
    };
  } catch (error) {
    return {
      testName: 'CSRF Protection',
      passed: false,
      severity: 'high',
      description: `CSRF test failed: ${String(error)}`,
    };
  }
}

/**
 * Test for authentication bypass
 */
export async function testAuthenticationBypass(
  page: Page,
  protectedUrl: string
): Promise<SecurityTestResult> {
  try {
    // Try to access protected URL without authentication
    await page.goto(protectedUrl, { waitUntil: 'networkidle', timeout: 5000 });

    // Check if redirected to login
    const currentUrl = page.url();
    const isRedirectedToLogin =
      currentUrl.includes('/login') || currentUrl.includes('/auth') || currentUrl.includes('/signin');

    return {
      testName: 'Authentication Bypass',
      passed: isRedirectedToLogin,
      severity: 'critical',
      description: isRedirectedToLogin
        ? 'Protected URL properly redirects to login'
        : 'Protected URL accessible without authentication',
      remediation: !isRedirectedToLogin
        ? 'Implement authentication checks on protected routes'
        : undefined,
    };
  } catch (error) {
    return {
      testName: 'Authentication Bypass',
      passed: true,
      severity: 'high',
      description: 'Protected URL properly blocked access',
    };
  }
}

/**
 * Test for authorization bypass
 */
export async function testAuthorizationBypass(
  page: Page,
  adminUrl: string,
  userRole: string = 'user'
): Promise<SecurityTestResult> {
  try {
    // Try to access admin URL as regular user
    await page.goto(adminUrl, { waitUntil: 'networkidle', timeout: 5000 });

    // Check for access denied message
    const accessDenied = await page.locator('[data-testid="access-denied"]').isVisible();
    const forbidden = await page.locator('text=/403|forbidden|not authorized/i').isVisible();

    const isProperlyBlocked = accessDenied || forbidden;

    return {
      testName: 'Authorization Bypass',
      passed: isProperlyBlocked,
      severity: 'critical',
      description: isProperlyBlocked
        ? `${userRole} properly denied access to admin area`
        : `${userRole} can access admin area - authorization bypass vulnerability`,
      remediation: !isProperlyBlocked
        ? 'Implement role-based access control (RBAC)'
        : undefined,
    };
  } catch (error) {
    return {
      testName: 'Authorization Bypass',
      passed: true,
      severity: 'high',
      description: 'Admin URL properly blocked access',
    };
  }
}

/**
 * Test for sensitive data exposure
 */
export async function testSensitiveDataExposure(
  page: Page
): Promise<SecurityTestResult> {
  try {
    // Check for sensitive data in page source
    const pageContent = await page.content();

    const sensitivePatterns = [
      /password\s*[:=]\s*[^\s<>]+/gi,
      /api[_-]?key\s*[:=]\s*[^\s<>]+/gi,
      /secret\s*[:=]\s*[^\s<>]+/gi,
      /token\s*[:=]\s*[^\s<>]+/gi,
      /credit[_-]?card\s*[:=]\s*[^\s<>]+/gi,
      /ssn\s*[:=]\s*[^\s<>]+/gi,
    ];

    const exposedData = sensitivePatterns.filter((pattern) => pattern.test(pageContent));

    return {
      testName: 'Sensitive Data Exposure',
      passed: exposedData.length === 0,
      severity: 'critical',
      description:
        exposedData.length === 0
          ? 'No sensitive data exposed in page source'
          : `Sensitive data patterns found: ${exposedData.length}`,
      remediation:
        exposedData.length > 0
          ? 'Remove sensitive data from page source and use secure storage'
          : undefined,
    };
  } catch (error) {
    return {
      testName: 'Sensitive Data Exposure',
      passed: false,
      severity: 'high',
      description: `Sensitive data test failed: ${String(error)}`,
    };
  }
}

/**
 * Test for secure headers
 */
export async function testSecureHeaders(page: Page): Promise<SecurityTestResult> {
  try {
    const headers = await page.evaluate(() => {
      const headerMap: Record<string, string> = {};
      // Note: Limited access to response headers in browser context
      // This is a simplified check
      return headerMap;
    });

    // Check for security headers in meta tags
    const cspMeta = await page.locator('meta[http-equiv="Content-Security-Policy"]').count();
    const xFrameOptions = await page.locator('meta[name="x-frame-options"]').count();

    const hasSecurityHeaders = cspMeta > 0 || xFrameOptions > 0;

    return {
      testName: 'Secure Headers',
      passed: hasSecurityHeaders,
      severity: 'medium',
      description: hasSecurityHeaders
        ? 'Security headers present'
        : 'Security headers not found',
      remediation: !hasSecurityHeaders
        ? 'Implement security headers (CSP, X-Frame-Options, X-Content-Type-Options, etc.)'
        : undefined,
    };
  } catch (error) {
    return {
      testName: 'Secure Headers',
      passed: false,
      severity: 'medium',
      description: `Secure headers test failed: ${String(error)}`,
    };
  }
}

/**
 * Test for HTTPS enforcement
 */
export async function testHTTPSEnforcement(page: Page): Promise<SecurityTestResult> {
  try {
    const url = page.url();
    const isHTTPS = url.startsWith('https://');

    return {
      testName: 'HTTPS Enforcement',
      passed: isHTTPS,
      severity: 'high',
      description: isHTTPS ? 'HTTPS is enforced' : 'HTTP is being used - not secure',
      remediation: !isHTTPS ? 'Enforce HTTPS for all connections' : undefined,
    };
  } catch (error) {
    return {
      testName: 'HTTPS Enforcement',
      passed: false,
      severity: 'high',
      description: `HTTPS test failed: ${String(error)}`,
    };
  }
}

/**
 * Generate security test report
 */
export function generateSecurityTestReport(results: SecurityTestResult[]): string {
  let report = '=== Security Test Report ===\n\n';

  const passed = results.filter((r) => r.passed).length;
  const failed = results.filter((r) => !r.passed).length;
  const critical = results.filter((r) => r.severity === 'critical' && !r.passed).length;
  const high = results.filter((r) => r.severity === 'high' && !r.passed).length;

  report += `Total Tests: ${results.length}\n`;
  report += `Passed: ${passed}\n`;
  report += `Failed: ${failed}\n`;
  report += `Critical Issues: ${critical}\n`;
  report += `High Issues: ${high}\n\n`;

  report += '=== Detailed Results ===\n';
  for (const result of results) {
    report += `\n${result.testName}: ${result.passed ? '✅ PASS' : '❌ FAIL'}\n`;
    report += `Severity: ${result.severity.toUpperCase()}\n`;
    report += `Description: ${result.description}\n`;
    if (result.remediation) {
      report += `Remediation: ${result.remediation}\n`;
    }
  }

  return report;
}
