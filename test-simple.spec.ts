import { test, expect } from '@playwright/test';

test('simple test - frontend is accessible', async ({ page }) => {
  console.log('Navigating to frontend...');
  await page.goto('http://localhost:3001');

  console.log('Waiting for page to load...');
  await page.waitForLoadState('domcontentloaded');

  const title = await page.title();
  console.log(`Page title: ${title}`);

  expect(title).toContain('TTA');
});

test('simple test - API is accessible', async ({ request }) => {
  console.log('Testing API health endpoint...');
  const response = await request.get('http://localhost:8081/health');

  console.log(`API response status: ${response.status()}`);
  expect(response.ok()).toBeTruthy();

  const body = await response.json();
  console.log(`API response:`, body);
  expect(body.status).toBe('healthy');
});
