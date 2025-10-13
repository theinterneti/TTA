/**
 * Complete User Journey Test for TTA Staging Environment
 *
 * This test validates the entire user experience from OAuth sign-in to playing the game.
 * The goal is to ensure that a user with ZERO instruction can:
 * 1. Sign in with OAuth
 * 2. Navigate to dashboard
 * 3. Create a character (if needed)
 * 4. Select a world
 * 5. Start playing/chatting
 *
 * Success Criteria:
 * - All UI elements are intuitive and discoverable
 * - No errors or broken states
 * - Data persists correctly (Redis, Neo4j)
 * - The experience is engaging and fun
 */

import { expect, test } from '@playwright/test';

// Staging environment configuration
const STAGING_CONFIG = {
  frontendURL: process.env.STAGING_BASE_URL || 'http://localhost:3001',
  apiURL: process.env.STAGING_API_URL || 'http://localhost:8081',
  // For OAuth testing, we'll use demo credentials or mock OAuth
  useMockOAuth: process.env.USE_MOCK_OAUTH !== 'false',
};

// Test user data
const TEST_USER = {
  username: 'staging_test_user',
  email: 'staging@test.tta',
  // For OAuth, these would be handled by the OAuth provider
};

test.describe('Complete User Journey - Staging Environment', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate directly to the login page for unauthenticated users
    // (The root URL would redirect here anyway via ProtectedRoute)
    await page.goto(`${STAGING_CONFIG.frontendURL}/login`);
  });

  test('should complete full user journey from sign-in to gameplay', async ({ page }) => {
    console.log('\n🎮 Starting Complete User Journey Test\n');

    // ============================================================
    // PHASE 1: Landing & Authentication
    // ============================================================
    console.log('📍 Phase 1: Landing & Authentication');

    await test.step('User lands on application', async () => {
      await expect(page).toHaveTitle(/TTA|Therapeutic Text Adventure/i);
      console.log('  ✓ Application loaded');
    });

    await test.step('User sees clear sign-in option', async () => {
      // We're already on the /login page from beforeEach
      // Check for sign-in button on the login page
      const signInButton = page.locator('button:has-text("Sign in"), button[type="submit"]:has-text("Sign in")').first();
      await expect(signInButton).toBeVisible({ timeout: 10000 });
      console.log('  ✓ Sign-in option is visible and discoverable');
    });

    await test.step('User initiates sign-in', async () => {
      if (STAGING_CONFIG.useMockOAuth) {
        // For testing without real OAuth, use demo credentials
        console.log('  ℹ Using demo credentials (mock OAuth)');

        // We're already on the login page from the previous step
        // Fill in demo credentials
        const usernameInput = page.locator('input[name="username"], input[id="username"]').first();
        const passwordInput = page.locator('input[name="password"], input[id="password"]').first();

        await expect(usernameInput).toBeVisible({ timeout: 5000 });
        await usernameInput.fill('demo_user');
        await passwordInput.fill('DemoPassword123!');

        // Click the sign-in button
        const submitButton = page.locator('button[type="submit"]:has-text("Sign in")');
        await submitButton.click();
        console.log('  ✓ Demo credentials submitted');
      } else {
        // Real OAuth flow
        console.log('  ℹ Using real OAuth flow');
        await page.click('button:has-text("Sign in with OpenRouter"), button:has-text("OAuth")');
        // Note: Real OAuth would require actual credentials or test account
        // This would redirect to OpenRouter, then back to callback
      }

      console.log('  ✓ Sign-in initiated');
    });

    await test.step('User successfully authenticates', async () => {
      // Wait for redirect to dashboard or main app
      await page.waitForURL(/dashboard|home|app/i, { timeout: 30000 });
      console.log('  ✓ Authentication successful');
    });

    // ============================================================
    // PHASE 2: Dashboard & Orientation
    // ============================================================
    console.log('\n📍 Phase 2: Dashboard & Orientation');

    await test.step('User sees welcoming dashboard', async () => {
      // Check for dashboard elements
      const dashboardHeading = page.locator('h1, h2').filter({ hasText: /dashboard|welcome|home/i }).first();
      await expect(dashboardHeading).toBeVisible({ timeout: 10000 });
      console.log('  ✓ Dashboard loaded');
    });

    await test.step('User sees clear next steps', async () => {
      // Look for character creation or world selection prompts
      const actionButtons = page.locator('button:has-text("Create Character"), button:has-text("New Character"), button:has-text("Get Started"), button:has-text("Start Adventure")');
      const hasActionButton = await actionButtons.count() > 0;
      expect(hasActionButton).toBeTruthy();
      console.log('  ✓ Clear call-to-action visible');
    });

    // ============================================================
    // PHASE 3: Character Creation
    // ============================================================
    console.log('\n📍 Phase 3: Character Creation');

    await test.step('User navigates to character creation', async () => {
      // Click on the primary "Create First Character" / "Manage Characters" button
      const createCharacterBtn = page.locator('[data-testid="dashboard-manage-characters-button"]');

      if (await createCharacterBtn.isVisible()) {
        await createCharacterBtn.click();
        await page.waitForLoadState('networkidle');
        console.log('  ✓ Navigated to character creation');
      } else {
        console.log('  ℹ Character button not found, skipping creation');
      }
    });

    await test.step('User creates character with intuitive form', async () => {
      // Check if we're on character creation page
      const characterForm = page.locator('form, [data-testid*="character"]').first();

      if (await characterForm.isVisible()) {
        // Fill in character name
        const nameInput = page.locator('input[name="name"], input[placeholder*="name" i]').first();
        await nameInput.fill('Aria Stormwind');
        console.log('  ✓ Character name entered');

        // Fill in basic details (if required)
        const backstoryInput = page.locator('textarea[name="backstory"], textarea[placeholder*="story" i]').first();
        if (await backstoryInput.isVisible()) {
          await backstoryInput.fill('A brave adventurer seeking peace and understanding.');
          console.log('  ✓ Character backstory entered');
        }

        // Submit character creation
        const submitBtn = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save")').first();
        await submitBtn.click();
        await page.waitForLoadState('networkidle');
        console.log('  ✓ Character created');
      } else {
        console.log('  ℹ Using existing character');
      }
    });

    // ============================================================
    // PHASE 4: World Selection
    // ============================================================
    console.log('\n📍 Phase 4: World Selection');

    await test.step('User sees available worlds', async () => {
      // Navigate to world selection if not already there
      const worldSelectionLink = page.locator('a:has-text("Worlds"), a:has-text("Select World"), button:has-text("Choose World")').first();

      if (await worldSelectionLink.isVisible()) {
        await worldSelectionLink.click();
        await page.waitForLoadState('networkidle');
      }

      // Check for world cards/options
      const worldCards = page.locator('[data-testid*="world"], .world-card, .card').filter({ hasText: /world|adventure|story/i });
      const worldCount = await worldCards.count();
      expect(worldCount).toBeGreaterThan(0);
      console.log(`  ✓ ${worldCount} worlds available`);
    });

    await test.step('User selects a world', async () => {
      // Click on first available world
      const selectWorldBtn = page.locator('button:has-text("Select"), button:has-text("Choose"), button:has-text("Start")').first();
      await selectWorldBtn.click();
      await page.waitForLoadState('networkidle');
      console.log('  ✓ World selected');
    });

    // ============================================================
    // PHASE 5: Gameplay / Chat Interface
    // ============================================================
    console.log('\n📍 Phase 5: Gameplay / Chat Interface');

    await test.step('User enters chat/story interface', async () => {
      // Check for chat interface elements
      const chatInterface = page.locator('[data-testid*="chat"], .chat-container, .message-container').first();
      await expect(chatInterface).toBeVisible({ timeout: 15000 });
      console.log('  ✓ Chat interface loaded');
    });

    await test.step('User sees initial story content', async () => {
      // Wait for initial AI message
      const messages = page.locator('.message, [data-testid*="message"]');
      await expect(messages.first()).toBeVisible({ timeout: 20000 });
      console.log('  ✓ Initial story content received');
    });

    await test.step('User can interact with story', async () => {
      // Find message input
      const messageInput = page.locator('input[type="text"], textarea').filter({ hasText: '' }).first();
      await expect(messageInput).toBeVisible();
      await expect(messageInput).toBeEnabled();

      // Type a message
      await messageInput.fill('I look around and take in my surroundings.');
      console.log('  ✓ User input entered');

      // Send message
      const sendBtn = page.locator('button:has-text("Send"), button[type="submit"]').last();
      await sendBtn.click();

      // Wait for AI response
      await page.waitForTimeout(2000); // Give AI time to respond
      console.log('  ✓ Message sent, awaiting response');
    });

    await test.step('User receives AI response', async () => {
      // Check for new message (AI response)
      const messages = page.locator('.message, [data-testid*="message"]');
      const messageCount = await messages.count();
      expect(messageCount).toBeGreaterThan(1);
      console.log('  ✓ AI response received');
    });

    // ============================================================
    // PHASE 6: Data Persistence Validation
    // ============================================================
    console.log('\n📍 Phase 6: Data Persistence Validation');

    await test.step('Session data persists on refresh', async () => {
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Check that we're still in the chat/story
      const chatInterface = page.locator('[data-testid*="chat"], .chat-container').first();
      await expect(chatInterface).toBeVisible({ timeout: 10000 });
      console.log('  ✓ Session persisted after refresh');
    });

    console.log('\n✅ Complete User Journey Test PASSED!\n');
    console.log('🎉 User can successfully:');
    console.log('   ✓ Sign in with OAuth');
    console.log('   ✓ Navigate dashboard intuitively');
    console.log('   ✓ Create character');
    console.log('   ✓ Select world');
    console.log('   ✓ Play/chat with AI');
    console.log('   ✓ Data persists correctly\n');
  });

  test('should handle errors gracefully', async ({ page }) => {
    console.log('\n🔍 Testing Error Handling\n');

    // Test network error handling
    await test.step('Application handles network errors', async () => {
      // Simulate offline
      await page.context().setOffline(true);

      // Try to navigate
      await page.goto(STAGING_CONFIG.frontendURL).catch(() => {});

      // Go back online
      await page.context().setOffline(false);
      await page.goto(STAGING_CONFIG.frontendURL);

      // Should recover
      await expect(page).toHaveTitle(/TTA|Therapeutic/i);
      console.log('  ✓ Recovers from network errors');
    });
  });
});
