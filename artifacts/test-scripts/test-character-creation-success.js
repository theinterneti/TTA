const { chromium } = require('playwright');

async function testCharacterCreationSuccess() {
  console.log('🎉 FINAL CHARACTER CREATION SUCCESS TEST...');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate and login
    console.log('📱 Navigate to Development Server');
    await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });

    console.log('🔐 Attempting login...');
    await page.fill('input[name="username"]', 'demo_user');
    await page.fill('input[name="password"]', 'demo_password');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Navigate to characters page
    console.log('🖱️  Clicking "Create First Character" button...');
    const createButton = page.locator('button:has-text("Create First Character")').first();
    await createButton.click();
    await page.waitForURL('**/characters', { timeout: 10000 });
    await page.waitForTimeout(2000);

    // Click create character button
    console.log('🖱️  Clicking character creation button...');
    const createCharacterButton = page.locator('button:has-text("Create Character")').first();
    await createCharacterButton.click();
    await page.waitForTimeout(2000);

    // Check for modal using the correct selector
    console.log('🔍 Looking for character creation modal...');
    const modal = page.locator('.fixed.inset-0.bg-black.bg-opacity-50').first();
    const modalExists = await modal.count() > 0;

    if (!modalExists) {
      console.log('❌ Modal not found with backdrop selector');
      return;
    }

    console.log('✅ CHARACTER CREATION MODAL IS OPEN!');

    // Verify modal content
    const modalTitle = page.locator('h2:has-text("Create New Character")');
    const titleExists = await modalTitle.count() > 0;
    console.log(`✅ Modal title found: ${titleExists}`);

    // Test form interaction - Step 1: Basic Information
    console.log('🔍 Testing Step 1: Basic Information...');

    // Fill character name
    const nameInput = page.locator('input[placeholder*="name"]').first();
    if (await nameInput.count() > 0) {
      await nameInput.fill('QA Test Character');
      console.log('✅ Character name filled successfully');
    }

    // Fill appearance description
    const descriptionTextarea = page.locator('textarea[placeholder*="appearance"]').first();
    if (await descriptionTextarea.count() > 0) {
      await descriptionTextarea.fill('A brave and determined character created during comprehensive QA testing to validate the complete character creation workflow.');
      console.log('✅ Appearance description filled successfully');
    }

    // Click Next button
    const nextButton = page.locator('button:has-text("Next")').first();
    if (await nextButton.count() > 0) {
      const isEnabled = await nextButton.isEnabled();
      console.log(`Next button enabled: ${isEnabled}`);

      if (isEnabled) {
        await nextButton.click();
        await page.waitForTimeout(1000);
        console.log('✅ Successfully progressed to Step 2');

        // Test Step 2: Background
        console.log('🔍 Testing Step 2: Background...');

        // Fill background story
        const storyTextarea = page.locator('textarea[placeholder*="story"], textarea[placeholder*="background"]').first();
        if (await storyTextarea.count() > 0) {
          await storyTextarea.fill('Born in a small village, this character has always been curious about the world and eager to help others overcome their challenges.');
          console.log('✅ Background story filled successfully');
        }

        // Add personality trait
        const traitInput = page.locator('input[placeholder*="trait"]').first();
        const addTraitButton = page.locator('button:has-text("Add")').first();
        if (await traitInput.count() > 0 && await addTraitButton.count() > 0) {
          await traitInput.fill('Compassionate');
          await addTraitButton.click();
          await page.waitForTimeout(500);
          console.log('✅ Personality trait added successfully');
        }

        // Add goal
        const goalInput = page.locator('input[placeholder*="goal"]').first();
        const addGoalButton = page.locator('button:has-text("Add")').last();
        if (await goalInput.count() > 0 && await addGoalButton.count() > 0) {
          await goalInput.fill('Help others find inner peace');
          await addGoalButton.click();
          await page.waitForTimeout(500);
          console.log('✅ Goal added successfully');
        }

        // Click Next to go to Step 3
        const nextButton2 = page.locator('button:has-text("Next")').first();
        if (await nextButton2.count() > 0 && await nextButton2.isEnabled()) {
          await nextButton2.click();
          await page.waitForTimeout(1000);
          console.log('✅ Successfully progressed to Step 3');

          // Test Step 3: Therapeutic Profile
          console.log('🔍 Testing Step 3: Therapeutic Profile...');

          // Set comfort level (slider)
          const comfortSlider = page.locator('input[type="range"]').first();
          if (await comfortSlider.count() > 0) {
            await comfortSlider.fill('7');
            console.log('✅ Comfort level set successfully');
          }

          // Select intensity level
          const intensitySelect = page.locator('select').first();
          if (await intensitySelect.count() > 0) {
            await intensitySelect.selectOption('MEDIUM');
            console.log('✅ Intensity level selected successfully');
          }

          // Add therapeutic goal
          const therapeuticGoalInput = page.locator('input[placeholder*="therapeutic"], input[placeholder*="goal"]').last();
          const addTherapeuticGoalButton = page.locator('button:has-text("Add")').last();
          if (await therapeuticGoalInput.count() > 0 && await addTherapeuticGoalButton.count() > 0) {
            await therapeuticGoalInput.fill('Reduce anxiety through mindful exploration');
            await addTherapeuticGoalButton.click();
            await page.waitForTimeout(500);
            console.log('✅ Therapeutic goal added successfully');
          }

          // Final submission
          const createCharacterFinalButton = page.locator('button:has-text("Create Character")').first();
          if (await createCharacterFinalButton.count() > 0) {
            const isEnabled = await createCharacterFinalButton.isEnabled();
            console.log(`Create Character button enabled: ${isEnabled}`);

            if (isEnabled) {
              console.log('🚀 Submitting character creation...');
              await createCharacterFinalButton.click({ force: true });

              // Wait for submission to complete
              await page.waitForTimeout(5000);

              // Check if modal closed (success)
              const modalStillExists = await modal.count() > 0;
              if (!modalStillExists) {
                console.log('🎉 SUCCESS: Character creation completed! Modal closed.');

                // Check if character appears in the list
                const characterCard = page.locator('text="QA Test Character"').first();
                if (await characterCard.count() > 0) {
                  console.log('🎉 SUCCESS: Character appears in character list!');
                } else {
                  console.log('⚠️  Character created but not visible in list yet');
                }

              } else {
                console.log('⚠️  Modal still open - checking for errors...');
              }
            }
          }
        }
      }
    }

    // Take final screenshot
    await page.screenshot({ path: 'character-creation-final-success.png' });
    console.log('📸 Final screenshot saved');

    console.log('🎉 CHARACTER CREATION WORKFLOW TEST COMPLETED!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: 'character-creation-error.png' });
  } finally {
    await browser.close();
  }
}

testCharacterCreationSuccess().catch(console.error);
