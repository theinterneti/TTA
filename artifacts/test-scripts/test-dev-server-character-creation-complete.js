// Logseq: [[TTA.dev/Artifacts/Test-scripts/Test-dev-server-character-creation-complete]]
const { chromium } = require('playwright');

async function testCompleteCharacterCreation() {
  console.log('🔍 Complete Character Creation Test on Development Server...');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 1000,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  // Listen for console messages
  page.on('console', msg => {
    const type = msg.type();
    if (type === 'error' || type === 'warning') {
      console.log(`🖥️  CONSOLE [${type}]:`, msg.text());
    }
  });

  try {
    console.log('📱 Navigate to Development Server');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

    // Check for webpack overlay and dismiss it
    console.log('⚠️  Checking for webpack overlay...');
    const overlayFrame = await page.$('iframe[title="Webpack App"]');
    if (overlayFrame) {
      console.log('⚠️  Webpack overlay detected - trying to dismiss it...');
      await page.keyboard.press('Escape');
      await page.waitForTimeout(2000);
    }

    console.log('📸 Taking screenshot of initial page...');
    await page.screenshot({ path: 'dev-server-initial.png' });

    // Login
    console.log('🔐 Attempting login...');
    await page.fill('input[type="text"]', 'demo_user');
    await page.fill('input[type="password"]', 'demo_password');
    await page.click('button:has-text("Sign in")');

    // Wait for navigation after login
    console.log('⏱️  Waiting for post-login navigation...');
    await page.waitForTimeout(3000);

    console.log('📸 Taking screenshot after login...');
    await page.screenshot({ path: 'dev-server-post-login.png' });

    // Check if we're logged in successfully
    const currentUrl = page.url();
    console.log('📍 Current URL:', currentUrl);

    // Look for character creation button
    const createButton = await page.$('button:has-text("Create First Character"), button:has-text("Create Character")');
    if (createButton) {
      console.log('✅ Found character creation button');
      await createButton.click();
      await page.waitForTimeout(2000);

      console.log('📸 Taking screenshot after clicking create button...');
      await page.screenshot({ path: 'dev-server-create-clicked.png' });

      // Check if modal opened
      const modal = await page.$('[role="dialog"], .modal, .fixed.inset-0');
      if (modal) {
        console.log('✅ Character creation modal opened');

        // Fill out the form
        console.log('📝 Filling out character creation form...');

        // Step 1: Basic Info
        await page.fill('input[placeholder*="name"], input[name*="name"]', 'Test Character');
        await page.fill('input[placeholder*="age"], input[name*="age"]', '25');
        await page.selectOption('select[name*="gender"], select:has(option:text("Male"))', 'male');

        console.log('📸 Taking screenshot after filling basic info...');
        await page.screenshot({ path: 'dev-server-basic-info.png' });

        // Click Next
        const nextButton = await page.$('button:has-text("Next")');
        if (nextButton) {
          await nextButton.click();
          await page.waitForTimeout(1000);

          console.log('📸 Taking screenshot after clicking Next...');
          await page.screenshot({ path: 'dev-server-step2.png' });

          // Step 2: Background - Add personality traits
          console.log('🎭 Adding personality traits...');
          const traitInput = await page.$('input[placeholder*="trait"], input[placeholder*="personality"]');
          if (traitInput) {
            await traitInput.fill('Brave');
            const addButton = await page.$('button:has-text("Add"), button[type="button"]:near(input[placeholder*="trait"])');
            if (addButton) {
              await addButton.click();
              await page.waitForTimeout(500);

              console.log('📸 Taking screenshot after adding trait...');
              await page.screenshot({ path: 'dev-server-trait-added.png' });

              // Add another trait
              await traitInput.fill('Curious');
              await addButton.click();
              await page.waitForTimeout(500);
            }
          }

          // Add goals
          console.log('🎯 Adding goals...');
          const goalInput = await page.$('input[placeholder*="goal"]');
          if (goalInput) {
            await goalInput.fill('Find the truth');
            const addGoalButton = await page.$('button:has-text("Add"):near(input[placeholder*="goal"])');
            if (addGoalButton) {
              await addGoalButton.click();
              await page.waitForTimeout(500);
            }
          }

          console.log('📸 Taking screenshot after adding goals...');
          await page.screenshot({ path: 'dev-server-goals-added.png' });

          // Click Next again
          const nextButton2 = await page.$('button:has-text("Next")');
          if (nextButton2) {
            await nextButton2.click();
            await page.waitForTimeout(1000);

            console.log('📸 Taking screenshot of step 3...');
            await page.screenshot({ path: 'dev-server-step3.png' });

            // Step 3: Therapeutic Goals
            console.log('🏥 Adding therapeutic goals...');
            const therapyInput = await page.$('input[placeholder*="therapeutic"], input[placeholder*="therapy"]');
            if (therapyInput) {
              await therapyInput.fill('Build confidence');
              const addTherapyButton = await page.$('button:has-text("Add"):near(input[placeholder*="therapeutic"])');
              if (addTherapyButton) {
                await addTherapyButton.click();
                await page.waitForTimeout(500);
              }
            }

            console.log('📸 Taking screenshot after adding therapeutic goals...');
            await page.screenshot({ path: 'dev-server-therapy-added.png' });

            // Submit the form
            console.log('✅ Submitting character creation form...');
            const submitButton = await page.$('button:has-text("Create Character"), button[type="submit"]');
            if (submitButton) {
              await submitButton.click();
              await page.waitForTimeout(3000);

              console.log('📸 Taking screenshot after submission...');
              await page.screenshot({ path: 'dev-server-submitted.png' });

              // Check if character was created successfully
              const successMessage = await page.$('text="Character created successfully", text="Success", .success');
              const characterList = await page.$('text="Test Character"');

              if (successMessage || characterList) {
                console.log('🎉 SUCCESS: Character creation completed successfully!');
              } else {
                console.log('⚠️  Character creation may have completed but no clear success indicator found');
              }
            } else {
              console.log('❌ Submit button not found');
            }
          } else {
            console.log('❌ Second Next button not found');
          }
        } else {
          console.log('❌ First Next button not found');
        }
      } else {
        console.log('❌ Character creation modal did not open');
      }
    } else {
      console.log('❌ Character creation button not found');

      // Check what's on the page
      const bodyText = await page.textContent('body');
      console.log('📄 Page content:', bodyText.substring(0, 500));
    }

    console.log('⏱️  Waiting 10 seconds for final observation...');
    await page.waitForTimeout(10000);

  } catch (error) {
    console.error('❌ Test failed:', error);
    await page.screenshot({ path: 'dev-server-error.png' });
  } finally {
    await browser.close();
    console.log('✅ Complete character creation test finished');
  }
}

testCompleteCharacterCreation();
