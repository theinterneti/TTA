import { test, expect } from '@playwright/test';

test.describe('Debug Login Flow', () => {
  test('Test login with detailed Redux state logging', async ({ page }) => {
    console.log('\n=== Testing Login Flow with Redux State Tracking ===');

    // Listen to all network requests
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        console.log(`REQUEST: ${request.method()} ${request.url()}`);
      }
    });

    page.on('response', async response => {
      if (response.url().includes('/api/')) {
        console.log(`RESPONSE: ${response.status()} ${response.url()}`);
        if (response.url().includes('/login')) {
          try {
            const body = await response.json();
            console.log('LOGIN RESPONSE BODY:', JSON.stringify(body, null, 2));
          } catch (e) {
            console.log('Could not parse login response as JSON');
          }
        }
      }
    });

    // Listen to console messages
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      console.log(`BROWSER CONSOLE [${type}]:`, text);
    });

    // Listen to page errors
    page.on('pageerror', error => {
      console.log('BROWSER PAGE ERROR:', error.message);
      console.log('Stack:', error.stack);
    });

    // Navigate to login page
    console.log('\n1. Navigating to login page...');
    await page.goto('http://localhost:3001/login');
    await page.waitForLoadState('networkidle');
    console.log('✓ Navigated to login page');

    // Fill in credentials
    console.log('\n2. Filling in credentials...');
    await page.fill('[data-testid="login-username-input"]', 'demo_user');
    await page.fill('[data-testid="login-password-input"]', 'DemoPassword123!');
    console.log('✓ Filled in credentials');

    // Check Redux state before login
    console.log('\n3. Checking Redux state BEFORE login...');
    const stateBeforeLogin = await page.evaluate(() => {
      // Try multiple ways to access Redux state
      const win = window as any;

      // Method 1: Redux DevTools Extension
      if (win.__REDUX_DEVTOOLS_EXTENSION__?.store) {
        return {
          method: 'DevTools',
          auth: win.__REDUX_DEVTOOLS_EXTENSION__.store.getState().auth
        };
      }

      // Method 2: Direct store access (if exposed)
      if (win.store) {
        return {
          method: 'Direct',
          auth: win.store.getState().auth
        };
      }

      return { method: 'None', auth: 'Redux state not accessible' };
    });
    console.log('Redux auth state BEFORE login:', JSON.stringify(stateBeforeLogin, null, 2));

    // Click submit
    console.log('\n4. Clicking submit button...');
    await page.click('[data-testid="login-submit-button"]');
    console.log('✓ Clicked submit button');

    // Wait for API call to complete
    console.log('\n5. Waiting for API call to complete...');
    await page.waitForTimeout(3000);

    // Check Redux state after login
    console.log('\n6. Checking Redux state AFTER login...');
    const stateAfterLogin = await page.evaluate(() => {
      const win = window as any;

      if (win.__REDUX_DEVTOOLS_EXTENSION__?.store) {
        return {
          method: 'DevTools',
          auth: win.__REDUX_DEVTOOLS_EXTENSION__.store.getState().auth
        };
      }

      if (win.store) {
        return {
          method: 'Direct',
          auth: win.store.getState().auth
        };
      }

      return { method: 'None', auth: 'Redux state not accessible' };
    });
    console.log('Redux auth state AFTER login:', JSON.stringify(stateAfterLogin, null, 2));

    // Check current URL
    console.log('\n7. Checking URL...');
    const currentURL = page.url();
    console.log('Current URL after login:', currentURL);

    // Check if useEffect is being triggered
    console.log('\n8. Checking if Login component useEffect would trigger...');
    const effectCheck = await page.evaluate(() => {
      const win = window as any;
      let authState = null;

      if (win.__REDUX_DEVTOOLS_EXTENSION__?.store) {
        authState = win.__REDUX_DEVTOOLS_EXTENSION__.store.getState().auth;
      } else if (win.store) {
        authState = win.store.getState().auth;
      }

      return {
        isAuthenticated: authState?.isAuthenticated,
        shouldTriggerRedirect: authState?.isAuthenticated === true,
        user: authState?.user,
        token: authState?.token ? 'EXISTS' : 'MISSING',
        error: authState?.error,
      };
    });
    console.log('Effect trigger check:', JSON.stringify(effectCheck, null, 2));

    // Wait a bit more to see if redirect happens
    console.log('\n9. Waiting additional 5 seconds for potential redirect...');
    await page.waitForTimeout(5000);
    const finalURL = page.url();
    console.log('Final URL after waiting:', finalURL);

    // Check if we're still on login page
    if (finalURL.includes('/login')) {
      console.log('\n⚠️  STILL ON LOGIN PAGE - Redirect did not occur!');

      // Check for any React Router issues
      const routerCheck = await page.evaluate(() => {
        const win = window as any;
        return {
          hasReactRouter: typeof win.React !== 'undefined',
          location: window.location.href,
          pathname: window.location.pathname,
        };
      });
      console.log('Router check:', JSON.stringify(routerCheck, null, 2));
    } else {
      console.log('\n✓ Redirect occurred to:', finalURL);
    }

    // Take a screenshot
    await page.screenshot({ path: 'test-results-staging/debug-login-flow.png', fullPage: true });
    console.log('\nScreenshot saved to test-results-staging/debug-login-flow.png');

    // Final assertion - just check that we got a response
    expect(currentURL).toBeTruthy();
  });
});
