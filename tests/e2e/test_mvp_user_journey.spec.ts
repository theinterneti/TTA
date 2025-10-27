/**
 * TTA MVP End-to-End User Journey Tests
 *
 * This test suite validates the complete user journey through the TTA platform,
 * with special focus on session data persistence across page refreshes and
 * browser restarts.
 *
 * Test Coverage:
 * 1. Authentication Flow
 * 2. Character Creation
 * 3. World Selection
 * 4. Session Management
 * 5. Therapeutic Conversation
 * 6. Progress Tracking
 * 7. Safety Monitoring
 */

import { test, expect, Page } from '@playwright/test';

// Configuration
const BASE_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:8080';

// Test data
const testUser = {
  username: `e2e_test_${Date.now()}`,
  email: `e2e_test_${Date.now()}@test.com`,
  password: 'TestPassword123!',
};

const testCharacter = {
  name: 'Alex Journey',
  age_range: '25-35',
  gender_identity: 'non-binary',
  physical_description: 'Medium height, thoughtful expression, casual style',
  clothing_style: 'Comfortable and practical',
  distinctive_features: ['Warm smile', 'Expressive eyes'],
  backstory: 'A person seeking to understand and manage anxiety through therapeutic exploration',
  personality_traits: ['Thoughtful', 'Curious', 'Resilient'],
  core_values: ['Growth', 'Authenticity', 'Compassion'],
  fears_and_anxieties: ['Social anxiety', 'Fear of failure'],
  strengths_and_skills: ['Good listener', 'Creative problem solver'],
  life_goals: ['Develop better coping strategies', 'Build meaningful connections'],
  therapeutic_goals: [
    {
      goal_id: 'goal_1',
      description: 'Manage social anxiety',
      progress_percentage: 0,
      is_active: true,
      therapeutic_approaches: ['CBT', 'Mindfulness'],
    },
  ],
  primary_concerns: ['Anxiety', 'Social connection'],
  preferred_intensity: 'moderate',
  comfort_zones: ['Mindfulness exercises', 'Journaling'],
  readiness_level: 7,
};

// Helper functions
async function login(page: Page, username: string, password: string) {
  await page.goto(`${BASE_URL}/login`);
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(`${BASE_URL}/dashboard`, { timeout: 10000 });
}

async function logout(page: Page) {
  await page.click('[data-testid="user-menu"]');
  await page.click('[data-testid="logout-button"]');
  await page.waitForURL(`${BASE_URL}/login`);
}

async function getLocalStorageItem(page: Page, key: string): Promise<string | null> {
  return await page.evaluate((k) => localStorage.getItem(k), key);
}

// Test Suite
test.describe('TTA MVP User Journey', () => {
  test.beforeEach(async ({ page }) => {
    // Clear storage before each test
    await page.goto(BASE_URL);
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('1. Authentication Flow - Register, Login, Logout, Re-login', async ({ page }) => {
    // Step 1: Register new user
    await page.goto(`${BASE_URL}/register`);
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="email"]', testUser.email);
    await page.fill('input[name="password"]', testUser.password);
    await page.fill('input[name="confirmPassword"]', testUser.password);
    await page.click('button[type="submit"]');

    // Verify redirect to dashboard after registration
    await page.waitForURL(`${BASE_URL}/dashboard`, { timeout: 10000 });

    // Verify JWT token is stored
    const token = await getLocalStorageItem(page, 'tta_access_token');
    expect(token).toBeTruthy();

    // Step 2: Logout
    await logout(page);

    // Verify token is cleared
    const tokenAfterLogout = await getLocalStorageItem(page, 'tta_access_token');
    expect(tokenAfterLogout).toBeNull();

    // Step 3: Login again
    await login(page, testUser.username, testUser.password);

    // Verify token is restored
    const tokenAfterLogin = await getLocalStorageItem(page, 'tta_access_token');
    expect(tokenAfterLogin).toBeTruthy();

    // Step 4: Refresh page and verify session persists
    await page.reload();
    await page.waitForURL(`${BASE_URL}/dashboard`);
    const tokenAfterRefresh = await getLocalStorageItem(page, 'tta_access_token');
    expect(tokenAfterRefresh).toBeTruthy();
  });

  test('2. Character Creation - Create and Verify Persistence', async ({ page }) => {
    // Login first
    await login(page, testUser.username, testUser.password);

    // Navigate to character creation
    await page.goto(`${BASE_URL}/characters/create`);

    // Fill character form
    await page.fill('input[name="name"]', testCharacter.name);
    await page.selectOption('select[name="age_range"]', testCharacter.age_range);
    await page.fill('input[name="gender_identity"]', testCharacter.gender_identity);
    await page.fill('textarea[name="physical_description"]', testCharacter.physical_description);
    await page.fill('textarea[name="backstory"]', testCharacter.backstory);

    // Add personality traits
    for (const trait of testCharacter.personality_traits) {
      await page.fill('input[name="personality_trait"]', trait);
      await page.click('button[data-testid="add-personality-trait"]');
    }

    // Add therapeutic goals
    await page.fill('input[name="therapeutic_goal"]', testCharacter.therapeutic_goals[0].description);
    await page.click('button[data-testid="add-therapeutic-goal"]');

    // Submit form
    await page.click('button[type="submit"]');

    // Verify redirect to character list
    await page.waitForURL(`${BASE_URL}/characters`, { timeout: 10000 });

    // Verify character appears in list
    await expect(page.locator(`text=${testCharacter.name}`)).toBeVisible();

    // Refresh page and verify character persists
    await page.reload();
    await expect(page.locator(`text=${testCharacter.name}`)).toBeVisible();

    // Click on character to view details
    await page.click(`text=${testCharacter.name}`);

    // Verify character details are correct
    await expect(page.locator(`text=${testCharacter.backstory}`)).toBeVisible();
  });

  test('3. World Selection - Browse and Select World', async ({ page }) => {
    // Login and create character first
    await login(page, testUser.username, testUser.password);

    // Navigate to world selection
    await page.goto(`${BASE_URL}/worlds`);

    // Verify 5 worlds are displayed (from P1.3)
    const worldCards = page.locator('[data-testid="world-card"]');
    await expect(worldCards).toHaveCount(5);

    // Click on first world to view details
    await worldCards.first().click();

    // Verify world details modal appears
    await expect(page.locator('[data-testid="world-details-modal"]')).toBeVisible();

    // Verify world information is displayed
    await expect(page.locator('[data-testid="world-name"]')).toBeVisible();
    await expect(page.locator('[data-testid="world-description"]')).toBeVisible();
    await expect(page.locator('[data-testid="therapeutic-approach"]')).toBeVisible();

    // Close modal
    await page.click('[data-testid="close-modal"]');

    // Select a world for session
    await page.click('[data-testid="select-world-button"]');
  });

  test('4. Session Management - Create and Verify Persistence', async ({ page }) => {
    // Login, create character, and select world first
    await login(page, testUser.username, testUser.password);

    // Navigate to session creation
    await page.goto(`${BASE_URL}/sessions/create`);

    // Select character
    await page.selectOption('select[name="character"]', { label: testCharacter.name });

    // Select world
    await page.selectOption('select[name="world"]', { index: 0 });

    // Create session
    await page.click('button[data-testid="create-session"]');

    // Verify redirect to chat
    await page.waitForURL(/\/chat\/session_/, { timeout: 10000 });

    // Get session ID from URL
    const url = page.url();
    const sessionId = url.match(/session_([^/]+)/)?.[1];
    expect(sessionId).toBeTruthy();

    // Refresh page and verify session persists
    await page.reload();
    await page.waitForURL(/\/chat\/session_/);

    // Verify session data is still loaded
    await expect(page.locator('[data-testid="character-name"]')).toHaveText(testCharacter.name);
  });

  test('5. Therapeutic Conversation - Send Messages and Verify History', async ({ page }) => {
    // Login and start session first
    await login(page, testUser.username, testUser.password);
    await page.goto(`${BASE_URL}/chat/session_test`);

    // Send first message
    const message1 = "Hello, I'm feeling anxious today.";
    await page.fill('textarea[name="message"]', message1);
    await page.click('button[data-testid="send-message"]');

    // Verify message appears in chat
    await expect(page.locator(`text=${message1}`)).toBeVisible();

    // Wait for AI response
    await page.waitForSelector('[data-testid="ai-message"]', { timeout: 30000 });

    // Send second message
    const message2 = "Can you help me with breathing exercises?";
    await page.fill('textarea[name="message"]', message2);
    await page.click('button[data-testid="send-message"]');

    // Verify second message appears
    await expect(page.locator(`text=${message2}`)).toBeVisible();

    // Refresh page and verify conversation history persists
    await page.reload();
    await expect(page.locator(`text=${message1}`)).toBeVisible();
    await expect(page.locator(`text=${message2}`)).toBeVisible();
  });

  test('6. Progress Tracking - View Progress Visualization', async ({ page }) => {
    // Login first
    await login(page, testUser.username, testUser.password);

    // Navigate to progress page
    await page.goto(`${BASE_URL}/progress`);

    // Verify progress visualization is displayed
    await expect(page.locator('[data-testid="progress-chart"]')).toBeVisible();

    // Verify milestones section exists
    await expect(page.locator('[data-testid="milestones-section"]')).toBeVisible();

    // Verify therapeutic metrics are displayed
    await expect(page.locator('[data-testid="therapeutic-metrics"]')).toBeVisible();
  });

  test('7. Safety Monitoring - Test Crisis Detection', async ({ page }) => {
    // Login and start session first
    await login(page, testUser.username, testUser.password);
    await page.goto(`${BASE_URL}/chat/session_test`);

    // Send concerning message
    const concerningMessage = "I feel hopeless and don't know what to do.";
    await page.fill('textarea[name="message"]', concerningMessage);
    await page.click('button[data-testid="send-message"]');

    // Verify safety warning appears
    await expect(page.locator('[data-testid="safety-warning"]')).toBeVisible({ timeout: 10000 });

    // Verify crisis resources are displayed
    await expect(page.locator('[data-testid="crisis-resources"]')).toBeVisible();

    // Verify emergency contact information is shown
    await expect(page.locator('text=988')).toBeVisible(); // Suicide & Crisis Lifeline
  });
});
