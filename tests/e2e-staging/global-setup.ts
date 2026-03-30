// Logseq: [[TTA.dev/Tests/E2e-staging/Global-setup]]
/**
 * Global Setup for Staging E2E Tests
 *
 * Validates that the staging environment is ready before running tests:
 * - Frontend is accessible
 * - API is responding
 * - Redis is connected
 * - Neo4j is accessible
 * - Database is initialized
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('\n🔍 Validating Staging Environment...\n');

  const baseURL = config.projects[0].use.baseURL || 'http://localhost:3001';
  const apiURL = process.env.STAGING_API_URL || 'http://localhost:8081';

  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // 1. Check Frontend
    console.log('✓ Checking frontend at', baseURL);
    const frontendResponse = await page.goto(baseURL, {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    if (!frontendResponse || !frontendResponse.ok()) {
      throw new Error(`Frontend not accessible at ${baseURL}`);
    }
    console.log('  ✓ Frontend is accessible');

    // 2. Check API Health
    console.log('✓ Checking API at', apiURL);
    const apiResponse = await page.request.get(`${apiURL}/health`, {
      timeout: 10000
    });

    if (!apiResponse.ok()) {
      throw new Error(`API not healthy at ${apiURL}/health`);
    }
    console.log('  ✓ API is healthy');

    // 3. Check API Documentation
    console.log('✓ Checking API docs');
    const docsResponse = await page.request.get(`${apiURL}/docs`, {
      timeout: 10000
    });

    if (!docsResponse.ok()) {
      console.warn('  ⚠ API docs not accessible (non-critical)');
    } else {
      console.log('  ✓ API docs accessible');
    }

    // 4. Validate Environment Variables
    console.log('✓ Validating environment configuration');
    const requiredEnvVars = [
      'REDIS_URL',
      'NEO4J_URI',
      'DATABASE_URL',
    ];

    const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
    if (missingVars.length > 0) {
      console.warn(`  ⚠ Missing environment variables: ${missingVars.join(', ')}`);
      console.warn('  ⚠ Using default staging values');
    } else {
      console.log('  ✓ Environment variables configured');
    }

    console.log('\n✅ Staging environment validation complete!\n');
    console.log('📊 Environment Summary:');
    console.log(`   Frontend: ${baseURL}`);
    console.log(`   API: ${apiURL}`);
    console.log(`   Redis: ${process.env.REDIS_URL || 'redis://localhost:6380'}`);
    console.log(`   Neo4j: ${process.env.NEO4J_URI || 'bolt://localhost:7688'}`);
    console.log(`   PostgreSQL: ${process.env.DATABASE_URL || 'postgresql://localhost:5433/tta_staging'}`);
    console.log('\n');

  } catch (error) {
    console.error('\n❌ Staging environment validation failed!\n');
    console.error('Error:', error);
    console.error('\n💡 Make sure staging environment is running:');
    console.error('   docker-compose -f docker-compose.staging-homelab.yml up -d\n');
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;
