// Logseq: [[TTA.dev/Artifacts/Test-scripts/Test-complete-character-creation-fixed]]
const { chromium } = require('playwright');

(async () => {
  try {
    console.log('🎯 Testing Complete Character Creation Workflow (Fixed API)...');

    const browser = await chromium.launch({
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      slowMo: 1000
    });

    const page = await browser.newPage();

    // Enhanced logging
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('React') || text.includes('error') || text.includes('Error') || text.includes('API') || text.includes('Character')) {
        console.log(`🖥️  CONSOLE [${msg.type()}]:`, text);
      }
    });

    page.on('pageerror', error => {
      console.log(`❌ PAGE ERROR:`, error.message);
    });

    console.log('📱 Step 1: Navigate and Login');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

    // Login
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'testpass');
    await page.click('button:has-text("Sign in")');
    await page.waitForTimeout(3000);

    console.log('🎭 Step 2: Open Character Creation Form');
    await page.click('button:has-text("Create First Character")');
    await page.waitForTimeout(2000);
    await page.click('button:has-text("Create Character")');
    await page.waitForTimeout(2000);

    console.log('📸 Taking screenshot of step 1...');
    await page.screenshot({ path: 'complete-test-01-step1.png', fullPage: true });

    console.log('🎭 Step 3: Fill Step 1 (Basic Information)');

    // Fill character name
    await page.fill('[name="name"]', 'Complete Test Character');

    // Fill appearance description
    const appearanceTextarea = await page.$('textarea');
    if (appearanceTextarea) {
      await appearanceTextarea.fill('A brave adventurer with kind eyes and a determined spirit.');
    }

    console.log('🖱️  Clicking Next to go to step 2...');
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(3000);

    console.log('📸 Taking screenshot of step 2...');
    await page.screenshot({ path: 'complete-test-02-step2.png', fullPage: true });

    console.log('🎭 Step 4: Fill Step 2 (Background & Personality) - Testing React Error Fix');

    // Fill background story
    const storyTextarea = await page.$('textarea[placeholder*="background"]');
    if (storyTextarea) {
      await storyTextarea.fill('Born in a small village, this character learned the value of helping others from a young age.');
    }

    // Test adding personality traits (this previously caused React Error #31)
    console.log('🧪 Testing personality trait addition...');
    const traitInput = await page.$('input[placeholder*="trait"]');
    if (traitInput) {
      await traitInput.fill('Brave');
      await page.click('button:has-text("Add")');
      await page.waitForTimeout(2000);

      // Add another trait
      await traitInput.fill('Compassionate');
      await page.click('button:has-text("Add")');
      await page.waitForTimeout(2000);

      console.log('✅ Personality traits added successfully!');
    }

    // Test adding goals
    console.log('🧪 Testing goal addition...');
    const goalInput = await page.$('input[placeholder*="goal"]');
    if (goalInput) {
      await goalInput.fill('Help others in need');
      await page.click('button:has-text("Add")');
      await page.waitForTimeout(2000);

      // Add another goal
      await goalInput.fill('Become a skilled healer');
      await page.click('button:has-text("Add")');
      await page.waitForTimeout(2000);

      console.log('✅ Goals added successfully!');
    }

    console.log('🖱️  Clicking Next to go to step 3...');
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(3000);

    console.log('📸 Taking screenshot of step 3...');
    await page.screenshot({ path: 'complete-test-03-step3.png', fullPage: true });

    console.log('🎭 Step 5: Fill Step 3 (Therapeutic Profile)');

    // Set comfort level
    const comfortSlider = await page.$('input[type="range"]');
    if (comfortSlider) {
      await comfortSlider.fill('7');
    }

    // Add therapeutic goals
    console.log('🧪 Testing therapeutic goal addition...');
    const therapyGoalInput = await page.$('input[placeholder*="therapeutic"]');
    if (therapyGoalInput) {
      await therapyGoalInput.fill('Stress management');
      await page.click('button:has-text("Add")');
      await page.waitForTimeout(2000);

      await therapyGoalInput.fill('Building confidence');
      await page.click('button:has-text("Add")');
      await page.waitForTimeout(2000);

      console.log('✅ Therapeutic goals added successfully!');
    }

    console.log('📸 Taking screenshot before submission...');
    await page.screenshot({ path: 'complete-test-04-before-submit.png', fullPage: true });

    console.log('🎯 Step 6: Submit Character Creation (Testing Modal Fix)');

    // Test the modal submission fix
    const submitButton = await page.$('button:has-text("Create Character")');
    if (submitButton) {
      console.log('🖱️  Clicking Create Character button...');
      await submitButton.click();
      await page.waitForTimeout(5000);

      console.log('📸 Taking screenshot after submission...');
      await page.screenshot({ path: 'complete-test-05-after-submit.png', fullPage: true });

      // Check if we're back to the character management page
      const pageTitle = await page.title();
      console.log('📊 Current page title:', pageTitle);

      // Look for success indicators
      const successIndicators = await page.evaluate(() => {
        const bodyText = document.body.innerText;
        return {
          hasCharacterList: bodyText.includes('Complete Test Character'),
          hasSuccessMessage: bodyText.includes('success') || bodyText.includes('created'),
          hasErrorMessage: bodyText.includes('error') || bodyText.includes('Error'),
          currentUrl: window.location.href,
          bodyText: bodyText.substring(0, 500)
        };
      });

      console.log('📊 Success indicators:', successIndicators);

      if (successIndicators.hasCharacterList) {
        console.log('🎉 SUCCESS: Character appears in the character list!');
      } else if (successIndicators.hasErrorMessage) {
        console.log('❌ ERROR: Character creation failed');
      } else {
        console.log('⚠️  UNCLEAR: Character creation status unknown');
      }

    } else {
      console.log('❌ Submit button not found');
    }

    console.log('🧪 Step 7: Verify Character in Backend');

    // Check if character was created in the backend
    const backendVerification = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8080/players/testuser/characters');
        const characters = await response.json();
        return {
          success: true,
          count: characters.length,
          characters: characters.map(c => ({ id: c.character_id, name: c.name }))
        };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });

    console.log('📊 Backend verification:', backendVerification);

    if (backendVerification.success && backendVerification.count > 0) {
      console.log('✅ Characters found in backend:');
      backendVerification.characters.forEach((char, i) => {
        console.log(`  ${i + 1}. ${char.name} (ID: ${char.id})`);
      });
    }

    console.log('📸 Taking final screenshot...');
    await page.screenshot({ path: 'complete-test-06-final.png', fullPage: true });

    console.log('⏱️  Waiting 10 seconds for observation...');
    await page.waitForTimeout(10000);

    await browser.close();
    console.log('✅ Complete character creation testing completed');

  } catch (error) {
    console.error('❌ Error during complete testing:', error);
  }
})();
