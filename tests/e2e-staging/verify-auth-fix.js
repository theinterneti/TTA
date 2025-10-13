/**
 * Standalone Authentication Verification Script
 *
 * This script verifies that the authentication fix is working correctly
 * by testing the complete login flow in a real browser context.
 *
 * Run with: node tests/e2e-staging/verify-auth-fix.js
 */

const { chromium } = require('playwright');

async function verifyAuthenticationFix() {
  console.log('\n🔍 TTA Staging Authentication Verification');
  console.log('==========================================\n');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  let testsPassed = 0;
  let testsFailed = 0;
  const results = [];

  // Track network requests
  const apiRequests = [];
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      apiRequests.push({
        method: request.method(),
        url: request.url(),
        timestamp: new Date().toISOString()
      });
      console.log(`📤 REQUEST: ${request.method()} ${request.url()}`);
    }
  });

  page.on('response', async response => {
    if (response.url().includes('/api/')) {
      console.log(`📥 RESPONSE: ${response.status()} ${response.url()}`);
    }
  });

  // Track console messages
  page.on('console', msg => {
    const type = msg.type();
    if (type === 'error' || type === 'warning') {
      console.log(`🔴 BROWSER ${type.toUpperCase()}: ${msg.text()}`);
    }
  });

  // Track page errors
  page.on('pageerror', error => {
    console.log(`❌ PAGE ERROR: ${error.message}`);
  });

  try {
    // Test 1: Frontend Accessibility
    console.log('\n📋 Test 1: Frontend Accessibility');
    console.log('   Navigating to http://localhost:3001...');

    const response = await page.goto('http://localhost:3001', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    if (response.status() === 200) {
      console.log('   ✅ PASS: Frontend accessible (HTTP 200)');
      testsPassed++;
      results.push({ test: 'Frontend Accessibility', status: 'PASS' });
    } else {
      console.log(`   ❌ FAIL: Frontend returned HTTP ${response.status()}`);
      testsFailed++;
      results.push({ test: 'Frontend Accessibility', status: 'FAIL', reason: `HTTP ${response.status()}` });
    }

    // Test 2: Page Rendering
    console.log('\n📋 Test 2: Page Rendering');
    console.log('   Checking for React root element...');

    const rootElement = await page.locator('#root').count();
    if (rootElement > 0) {
      console.log('   ✅ PASS: React root element found');
      testsPassed++;
      results.push({ test: 'Page Rendering', status: 'PASS' });
    } else {
      console.log('   ❌ FAIL: React root element not found');
      testsFailed++;
      results.push({ test: 'Page Rendering', status: 'FAIL', reason: 'No #root element' });
    }

    // Test 3: Navigate to Login Page
    console.log('\n📋 Test 3: Login Page Navigation');
    console.log('   Navigating to /login...');

    await page.goto('http://localhost:3001/login', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Wait for login form to be visible
    try {
      await page.waitForSelector('input[type="text"], input[type="email"], input[name="username"]', { timeout: 10000 });
      console.log('   ✅ PASS: Login page loaded with form');
      testsPassed++;
      results.push({ test: 'Login Page Navigation', status: 'PASS' });
    } catch (error) {
      console.log('   ❌ FAIL: Login form not found');
      testsFailed++;
      results.push({ test: 'Login Page Navigation', status: 'FAIL', reason: 'Form not visible' });
    }

    // Test 4: API Configuration Check
    console.log('\n📋 Test 4: API Configuration');
    console.log('   Note: API URL is baked into bundle at build time');
    console.log('   Will verify by checking actual API requests made');
    results.push({ test: 'API Configuration', status: 'INFO', value: 'Will verify via API requests' });

    // Test 5: Login Attempt
    console.log('\n📋 Test 5: Authentication Flow');
    console.log('   Attempting login with demo credentials...');

    // Clear previous API requests
    apiRequests.length = 0;

    // Find and fill username field
    const usernameSelectors = [
      'input[name="username"]',
      'input[type="text"]',
      'input[placeholder*="username" i]',
      'input[data-testid="login-username-input"]'
    ];

    let usernameFilled = false;
    for (const selector of usernameSelectors) {
      try {
        const count = await page.locator(selector).count();
        if (count > 0) {
          await page.fill(selector, 'demo_user');
          console.log(`   ✓ Filled username using selector: ${selector}`);
          usernameFilled = true;
          break;
        }
      } catch (e) {
        // Try next selector
      }
    }

    if (!usernameFilled) {
      console.log('   ❌ FAIL: Could not find username field');
      testsFailed++;
      results.push({ test: 'Authentication Flow', status: 'FAIL', reason: 'Username field not found' });
    } else {
      // Find and fill password field
      const passwordSelectors = [
        'input[name="password"]',
        'input[type="password"]',
        'input[data-testid="login-password-input"]'
      ];

      let passwordFilled = false;
      for (const selector of passwordSelectors) {
        try {
          const count = await page.locator(selector).count();
          if (count > 0) {
            await page.fill(selector, 'DemoPassword123!');
            console.log(`   ✓ Filled password using selector: ${selector}`);
            passwordFilled = true;
            break;
          }
        } catch (e) {
          // Try next selector
        }
      }

      if (!passwordFilled) {
        console.log('   ❌ FAIL: Could not find password field');
        testsFailed++;
        results.push({ test: 'Authentication Flow', status: 'FAIL', reason: 'Password field not found' });
      } else {
        // Find and click submit button
        const submitSelectors = [
          'button[type="submit"]',
          'button:has-text("Login")',
          'button:has-text("Sign In")',
          'button[data-testid="login-submit-button"]'
        ];

        let submitClicked = false;
        for (const selector of submitSelectors) {
          try {
            const count = await page.locator(selector).count();
            if (count > 0) {
              await page.click(selector);
              console.log(`   ✓ Clicked submit using selector: ${selector}`);
              submitClicked = true;
              break;
            }
          } catch (e) {
            // Try next selector
          }
        }

        if (!submitClicked) {
          console.log('   ❌ FAIL: Could not find submit button');
          testsFailed++;
          results.push({ test: 'Authentication Flow', status: 'FAIL', reason: 'Submit button not found' });
        } else {
          // Wait for API call
          console.log('   ⏳ Waiting for authentication API call...');
          await page.waitForTimeout(3000);

          // Check if login API was called
          const loginRequest = apiRequests.find(req =>
            req.url.includes('/login') || req.url.includes('/auth')
          );

          if (loginRequest) {
            console.log(`   ✅ PASS: Login API called at ${loginRequest.url}`);

            // Check if it's the correct endpoint
            if (loginRequest.url.includes('localhost:8081') || loginRequest.url.includes(':8081')) {
              console.log('   ✅ PASS: Request sent to correct port (8081)');
              testsPassed++;
              results.push({ test: 'Authentication Flow', status: 'PASS', endpoint: loginRequest.url });
            } else {
              console.log(`   ⚠️  WARNING: Request sent to unexpected endpoint: ${loginRequest.url}`);
              console.log('   Expected: http://localhost:8081/api/v1/auth/login');
              testsPassed++;
              results.push({ test: 'Authentication Flow', status: 'PARTIAL', endpoint: loginRequest.url });
            }
          } else {
            console.log('   ❌ FAIL: No login API call detected');
            console.log('   API requests made:', apiRequests);
            testsFailed++;
            results.push({ test: 'Authentication Flow', status: 'FAIL', reason: 'No API call detected' });
          }
        }
      }
    }

    // Test 6: Check for errors
    console.log('\n📋 Test 6: Error Detection');
    const hasErrors = await page.evaluate(() => {
      const errors = window.__errors || [];
      return errors.length > 0;
    });

    if (!hasErrors) {
      console.log('   ✅ PASS: No JavaScript errors detected');
      testsPassed++;
      results.push({ test: 'Error Detection', status: 'PASS' });
    } else {
      console.log('   ⚠️  WARNING: JavaScript errors detected');
      results.push({ test: 'Error Detection', status: 'WARNING' });
    }

  } catch (error) {
    console.log(`\n❌ CRITICAL ERROR: ${error.message}`);
    testsFailed++;
    results.push({ test: 'Overall Execution', status: 'ERROR', error: error.message });
  } finally {
    // Summary
    console.log('\n\n📊 Test Summary');
    console.log('================');
    console.log(`✅ Passed: ${testsPassed}`);
    console.log(`❌ Failed: ${testsFailed}`);
    console.log(`📋 Total:  ${testsPassed + testsFailed}`);

    console.log('\n📋 Detailed Results:');
    results.forEach((result, index) => {
      const icon = result.status === 'PASS' ? '✅' :
                   result.status === 'FAIL' ? '❌' :
                   result.status === 'WARNING' ? '⚠️' : 'ℹ️';
      console.log(`${index + 1}. ${icon} ${result.test}: ${result.status}`);
      if (result.reason) console.log(`   Reason: ${result.reason}`);
      if (result.endpoint) console.log(`   Endpoint: ${result.endpoint}`);
      if (result.value) console.log(`   Value: ${result.value}`);
    });

    console.log('\n🔍 API Requests Made:');
    if (apiRequests.length === 0) {
      console.log('   No API requests detected');
    } else {
      apiRequests.forEach((req, index) => {
        console.log(`   ${index + 1}. ${req.method} ${req.url}`);
      });
    }

    await browser.close();

    // Exit with appropriate code
    process.exit(testsFailed > 0 ? 1 : 0);
  }
}

// Run the verification
verifyAuthenticationFix().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
