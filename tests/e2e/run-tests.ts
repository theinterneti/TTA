#!/usr/bin/env ts-node

/**
 * Comprehensive E2E Test Runner for TTA Application
 * 
 * This script provides various test execution modes:
 * - Full test suite
 * - Specific test categories
 * - Performance testing
 * - Accessibility testing
 * - Cross-browser testing
 * - Parallel execution
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import path from 'path';

interface TestConfig {
  category: string;
  description: string;
  specs: string[];
  parallel?: boolean;
  timeout?: number;
  retries?: number;
}

const TEST_CATEGORIES: Record<string, TestConfig> = {
  core: {
    category: 'Core Functionality',
    description: 'Essential user flows and basic functionality',
    specs: [
      'authentication.spec.ts',
      'dashboard.spec.ts',
      'character-management.spec.ts',
      'chat.spec.ts',
    ],
    parallel: true,
    timeout: 30000,
    retries: 2,
  },
  features: {
    category: 'Feature Testing',
    description: 'Comprehensive feature testing',
    specs: [
      'world-selection.spec.ts',
      'preferences.spec.ts',
      'model-management.spec.ts',
      'progress-tracking.spec.ts',
    ],
    parallel: true,
    timeout: 45000,
    retries: 1,
  },
  quality: {
    category: 'Quality Assurance',
    description: 'Performance, accessibility, and error handling',
    specs: [
      'performance.spec.ts',
      'accessibility.spec.ts',
      'error-handling.spec.ts',
      'data-persistence.spec.ts',
    ],
    parallel: false, // Sequential for accurate performance measurements
    timeout: 60000,
    retries: 0,
  },
  responsive: {
    category: 'Responsive Design',
    description: 'Cross-device and responsive design testing',
    specs: [
      'responsive-design.spec.ts',
    ],
    parallel: false,
    timeout: 30000,
    retries: 1,
  },
  settings: {
    category: 'Settings & Configuration',
    description: 'Settings, preferences, and configuration testing',
    specs: [
      'settings.spec.ts',
    ],
    parallel: true,
    timeout: 30000,
    retries: 1,
  },
};

const BROWSER_CONFIGS = {
  chromium: { name: 'Chromium', project: 'chromium' },
  firefox: { name: 'Firefox', project: 'firefox' },
  webkit: { name: 'WebKit', project: 'webkit' },
  mobile: { name: 'Mobile Chrome', project: 'Mobile Chrome' },
  tablet: { name: 'Mobile Safari', project: 'Mobile Safari' },
};

class TestRunner {
  private baseCommand = 'npx playwright test';
  private testDir = 'tests/e2e/specs';
  
  constructor() {
    this.validateEnvironment();
  }

  private validateEnvironment(): void {
    // Check if Playwright is installed
    try {
      execSync('npx playwright --version', { stdio: 'ignore' });
    } catch (error) {
      console.error('❌ Playwright is not installed. Run: npm install @playwright/test');
      process.exit(1);
    }

    // Check if test directory exists
    if (!existsSync(this.testDir)) {
      console.error(`❌ Test directory not found: ${this.testDir}`);
      process.exit(1);
    }

    // Check if config file exists
    if (!existsSync('playwright.config.ts')) {
      console.error('❌ Playwright config file not found: playwright.config.ts');
      process.exit(1);
    }
  }

  private buildCommand(options: {
    specs?: string[];
    project?: string;
    headed?: boolean;
    debug?: boolean;
    parallel?: boolean;
    timeout?: number;
    retries?: number;
    reporter?: string;
    outputDir?: string;
  }): string {
    let command = this.baseCommand;

    if (options.specs && options.specs.length > 0) {
      const specPaths = options.specs.map(spec => path.join(this.testDir, spec));
      command += ` ${specPaths.join(' ')}`;
    }

    if (options.project) {
      command += ` --project="${options.project}"`;
    }

    if (options.headed) {
      command += ' --headed';
    }

    if (options.debug) {
      command += ' --debug';
    }

    if (options.parallel === false) {
      command += ' --workers=1';
    }

    if (options.timeout) {
      command += ` --timeout=${options.timeout}`;
    }

    if (options.retries !== undefined) {
      command += ` --retries=${options.retries}`;
    }

    if (options.reporter) {
      command += ` --reporter=${options.reporter}`;
    }

    if (options.outputDir) {
      command += ` --output=${options.outputDir}`;
    }

    return command;
  }

  private executeCommand(command: string, description: string): boolean {
    console.log(`\n🚀 ${description}`);
    console.log(`📝 Command: ${command}\n`);

    try {
      execSync(command, { stdio: 'inherit' });
      console.log(`\n✅ ${description} - PASSED\n`);
      return true;
    } catch (error) {
      console.log(`\n❌ ${description} - FAILED\n`);
      return false;
    }
  }

  public runCategory(categoryName: string, options: {
    browser?: string;
    headed?: boolean;
    debug?: boolean;
  } = {}): boolean {
    const category = TEST_CATEGORIES[categoryName];
    if (!category) {
      console.error(`❌ Unknown test category: ${categoryName}`);
      console.log('Available categories:', Object.keys(TEST_CATEGORIES).join(', '));
      return false;
    }

    const command = this.buildCommand({
      specs: category.specs,
      project: options.browser,
      headed: options.headed,
      debug: options.debug,
      parallel: category.parallel,
      timeout: category.timeout,
      retries: category.retries,
      reporter: 'html',
      outputDir: `test-results/${categoryName}`,
    });

    return this.executeCommand(command, `${category.category} Tests`);
  }

  public runAll(options: {
    browser?: string;
    headed?: boolean;
    skipQuality?: boolean;
  } = {}): boolean {
    console.log('🎯 Running Complete E2E Test Suite\n');
    
    const categories = Object.keys(TEST_CATEGORIES);
    if (options.skipQuality) {
      categories.splice(categories.indexOf('quality'), 1);
      console.log('⚠️  Skipping quality tests (performance, accessibility, error handling)\n');
    }

    let allPassed = true;
    const results: Record<string, boolean> = {};

    for (const categoryName of categories) {
      const passed = this.runCategory(categoryName, options);
      results[categoryName] = passed;
      allPassed = allPassed && passed;
    }

    // Print summary
    console.log('\n📊 TEST SUMMARY');
    console.log('================');
    for (const [category, passed] of Object.entries(results)) {
      const status = passed ? '✅ PASSED' : '❌ FAILED';
      const config = TEST_CATEGORIES[category];
      console.log(`${status} - ${config.category}`);
    }

    console.log(`\n🎯 Overall Result: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}\n`);
    return allPassed;
  }

  public runCrossBrowser(categoryName?: string): boolean {
    console.log('🌐 Running Cross-Browser Tests\n');
    
    const category = categoryName || 'core';
    let allPassed = true;

    for (const [browserKey, browserConfig] of Object.entries(BROWSER_CONFIGS)) {
      console.log(`\n🔍 Testing on ${browserConfig.name}...`);
      
      const passed = this.runCategory(category, {
        browser: browserConfig.project,
      });
      
      allPassed = allPassed && passed;
    }

    console.log(`\n🌐 Cross-Browser Result: ${allPassed ? '✅ ALL BROWSERS PASSED' : '❌ SOME BROWSERS FAILED'}\n`);
    return allPassed;
  }

  public runPerformance(): boolean {
    console.log('⚡ Running Performance Tests\n');
    
    const command = this.buildCommand({
      specs: ['performance.spec.ts'],
      parallel: false,
      timeout: 120000,
      retries: 0,
      reporter: 'json',
      outputDir: 'test-results/performance',
    });

    return this.executeCommand(command, 'Performance Tests');
  }

  public runAccessibility(): boolean {
    console.log('♿ Running Accessibility Tests\n');
    
    const command = this.buildCommand({
      specs: ['accessibility.spec.ts'],
      parallel: true,
      timeout: 60000,
      retries: 1,
      reporter: 'html',
      outputDir: 'test-results/accessibility',
    });

    return this.executeCommand(command, 'Accessibility Tests');
  }

  public runSmoke(): boolean {
    console.log('💨 Running Smoke Tests\n');
    
    // Run a subset of critical tests quickly
    const smokeSpecs = [
      'authentication.spec.ts',
      'dashboard.spec.ts',
      'character-management.spec.ts',
    ];

    const command = this.buildCommand({
      specs: smokeSpecs,
      parallel: true,
      timeout: 15000,
      retries: 0,
      reporter: 'line',
    });

    return this.executeCommand(command, 'Smoke Tests');
  }

  public runDebug(specFile: string): boolean {
    console.log(`🐛 Running Debug Mode for ${specFile}\n`);
    
    const command = this.buildCommand({
      specs: [specFile],
      headed: true,
      debug: true,
      parallel: false,
      timeout: 0, // No timeout in debug mode
      retries: 0,
    });

    return this.executeCommand(command, `Debug: ${specFile}`);
  }
}

// CLI Interface
function main() {
  const args = process.argv.slice(2);
  const runner = new TestRunner();

  if (args.length === 0) {
    console.log(`
🎭 TTA E2E Test Runner

Usage:
  npm run test:e2e [command] [options]

Commands:
  all                    Run all test categories
  smoke                  Run smoke tests (quick validation)
  core                   Run core functionality tests
  features               Run feature tests
  quality                Run quality tests (performance, accessibility, errors)
  cross-browser [cat]    Run tests across all browsers
  performance            Run performance tests only
  accessibility          Run accessibility tests only
  debug <spec-file>      Run specific test in debug mode

Options:
  --browser <name>       Run on specific browser (chromium, firefox, webkit)
  --headed               Run in headed mode (visible browser)
  --skip-quality         Skip quality tests in 'all' mode

Examples:
  npm run test:e2e all
  npm run test:e2e core --browser firefox --headed
  npm run test:e2e debug character-management.spec.ts
  npm run test:e2e cross-browser core
    `);
    return;
  }

  const command = args[0];
  const options = {
    browser: args.includes('--browser') ? args[args.indexOf('--browser') + 1] : undefined,
    headed: args.includes('--headed'),
    skipQuality: args.includes('--skip-quality'),
  };

  let success = false;

  switch (command) {
    case 'all':
      success = runner.runAll(options);
      break;
    case 'smoke':
      success = runner.runSmoke();
      break;
    case 'core':
    case 'features':
    case 'quality':
    case 'responsive':
    case 'settings':
      success = runner.runCategory(command, options);
      break;
    case 'cross-browser':
      const category = args[1] && !args[1].startsWith('--') ? args[1] : undefined;
      success = runner.runCrossBrowser(category);
      break;
    case 'performance':
      success = runner.runPerformance();
      break;
    case 'accessibility':
      success = runner.runAccessibility();
      break;
    case 'debug':
      if (args[1]) {
        success = runner.runDebug(args[1]);
      } else {
        console.error('❌ Debug command requires a spec file name');
      }
      break;
    default:
      console.error(`❌ Unknown command: ${command}`);
      console.log('Run without arguments to see usage information.');
  }

  process.exit(success ? 0 : 1);
}

if (require.main === module) {
  main();
}
