// Logseq: [[TTA.dev/Tests/E2e/Debug-login.spec]]
import { test, expect } from '@playwright/test';

test('debug login flow', async ({ page }) => {
  // Listen to console messages
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));

  // Listen to network requests
  page.on('request', request => {
    if (request.url().includes('/auth/login')) {
      console.log('LOGIN REQUEST:', request.url(), request.method());
      console.log('REQUEST BODY:', request.postDataJSON());
    }
  });

  page.on('response', async response => {
    if (response.url().includes('/auth/login')) {
      console.log('LOGIN RESPONSE:', response.status());
      try {
        const body = await response.json();
        console.log('RESPONSE BODY:', JSON.stringify(body, null, 2));
      } catch (e) {
        console.log('Could not parse response body');
      }
    }
  });

  // Go to login page
  await page.goto('http://localhost:3000/login');

  // Fill in credentials
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'testpass');

  // Click login button
  await page.click('button[type="submit"]');

  // Wait a bit to see what happens
  await page.waitForTimeout(5000);

  // Check current URL
  console.log('CURRENT URL:', page.url());

  // Take screenshot
  await page.screenshot({ path: 'debug-login.png', fullPage: true });
});
