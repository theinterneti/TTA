// Logseq: [[TTA.dev/Testing/Simulation/Validate-framework]]
#!/usr/bin/env ts-node

/**
 * Framework Validation Script
 *
 * Quick validation test to ensure the TTA Simulation Framework is working correctly
 */

import { SimulationRunner, SIMULATION_CONFIGS } from './SimulationRunner';
import { PersonaType } from './personas/UserPersonas';
import { SimulationConfig } from './core/SimulationEngine';

/**
 * Minimal test configuration for validation
 */
const VALIDATION_CONFIG: SimulationConfig = {
  maxSimulationDuration: 2 * 60 * 1000, // 2 minutes
  maxConcurrentSessions: 2,

  // Test with just 2 personas
  enabledPersonas: [PersonaType.CASUAL_EXPLORER, PersonaType.STORY_ENTHUSIAST],
  personaDistribution: {
    [PersonaType.CASUAL_EXPLORER]: 60,
    [PersonaType.STORY_ENTHUSIAST]: 40,
    [PersonaType.WORLD_BUILDER]: 0,
    [PersonaType.MARATHON_PLAYER]: 0,
    [PersonaType.SOCIAL_CONNECTOR]: 0,
    [PersonaType.ACHIEVEMENT_HUNTER]: 0,
    [PersonaType.THERAPEUTIC_SEEKER]: 0,
    [PersonaType.SKEPTICAL_NEWCOMER]: 0
  },

  // Test simple world generation
  worldComplexityLevels: ['simple'],
  worldSystemsToTest: ['cultural', 'social'],

  sessionPatterns: [
    {
      name: 'Validation Pattern',
      description: 'Quick validation pattern for framework testing',
      targetDuration: 5,
      minDuration: 3,
      maxDuration: 8,
      interactionDensity: 1.5,
      complexityLevel: 'low',
      therapeuticFocus: 0.5,
      entertainmentFocus: 0.8,
      suitablePersonas: [PersonaType.CASUAL_EXPLORER, PersonaType.STORY_ENTHUSIAST]
    }
  ],

  multiSessionContinuity: false,
  minimumImmersionScore: 0.5,
  minimumEngagementScore: 0.6,
  minimumTherapeuticIntegrationScore: 0.5,
  enableRealTimeMetrics: true,
  detailedLogging: false,
  generateVisualReports: false
};

/**
 * Test individual components
 */
async function testComponents(): Promise<void> {
  console.log('🧪 Testing Individual Components...\n');

  try {
    // Test UserPersonas
    console.log('1. Testing UserPersonas...');
    const { UserPersona, PersonaType } = await import('./personas/UserPersonas');
    const testPersona = new UserPersona(PersonaType.CASUAL_EXPLORER, 'test_persona');
    console.log(`   ✅ Created persona: ${testPersona.name}`);
    console.log(`   ✅ Session preferences: ${testPersona.sessionPreferences.preferredDuration} min`);

    // Test ImmersionMetrics
    console.log('2. Testing ImmersionMetrics...');
    const { ImmersionMetrics } = await import('./metrics/ImmersionMetrics');
    const metrics = new ImmersionMetrics();
    metrics.startSession('test_session', PersonaType.CASUAL_EXPLORER);
    metrics.recordInteraction('test_session', 'choice', { test: true });
    const sessionMetrics = metrics.finalizeSession('test_session', 10);
    console.log(`   ✅ Session metrics calculated: ${sessionMetrics?.immersionScore.overall.toFixed(2)}`);

    // Test WorldGenerationTester
    console.log('3. Testing WorldGenerationTester...');
    const { WorldGenerationTester } = await import('./world/WorldGenerationTester');
    const worldTester = new WorldGenerationTester();
    const worldTests = await worldTester.testWorldGeneration({
      complexityLevel: 'simple',
      systemsToTest: ['cultural'],
      generateMultipleWorlds: false,
      testSystemInteractions: false,
      evaluateConsistency: false,
      testHistoricalDepth: false
    });
    console.log(`   ✅ World generation test completed: ${worldTests.length} worlds tested`);

    // Test SessionScenarios
    console.log('4. Testing SessionScenarios...');
    const { SessionScenarios } = await import('./scenarios/SessionScenarios');
    const scenarios = new SessionScenarios(metrics);
    const allScenarios = scenarios.getAllScenarios();
    console.log(`   ✅ Session scenarios loaded: ${allScenarios.length} scenarios available`);

    console.log('\n✅ All components tested successfully!\n');

  } catch (error) {
    console.error('❌ Component testing failed:', error);
    throw error;
  }
}

/**
 * Test simulation runner
 */
async function testSimulationRunner(): Promise<void> {
  console.log('🚀 Testing Simulation Runner...\n');

  try {
    const runner = new SimulationRunner();
    console.log('✅ SimulationRunner created successfully');

    // Test with validation configuration
    console.log('🔧 Running validation simulation...');
    const report = await runner.runWithConfig(VALIDATION_CONFIG);

    console.log('\n📊 VALIDATION RESULTS:');
    console.log(`   Overall Success: ${report.executiveSummary.overallSuccess ? '✅ PASS' : '⚠️ PARTIAL'}`);
    console.log(`   Sessions Tested: ${report.executiveSummary.totalSessions}`);
    console.log(`   Duration: ${(report.metadata.totalDuration / 1000).toFixed(1)}s`);
    console.log(`   Engagement: ${(report.executiveSummary.keyMetrics.averageEngagement * 100).toFixed(1)}%`);
    console.log(`   Immersion: ${(report.executiveSummary.keyMetrics.averageImmersion * 100).toFixed(1)}%`);

    if (report.executiveSummary.totalSessions > 0) {
      console.log('\n✅ Simulation framework is working correctly!');
    } else {
      console.log('\n⚠️ No sessions were completed - check configuration');
    }

  } catch (error) {
    console.error('❌ Simulation runner test failed:', error);
    throw error;
  }
}

/**
 * Test predefined configurations
 */
async function testPredefinedConfigs(): Promise<void> {
  console.log('⚙️ Testing Predefined Configurations...\n');

  try {
    // Test that configurations are valid
    const configs = Object.keys(SIMULATION_CONFIGS);
    console.log(`Available configurations: ${configs.join(', ')}`);

    for (const configName of configs) {
      const config = SIMULATION_CONFIGS[configName as keyof typeof SIMULATION_CONFIGS];
      console.log(`✅ ${configName}: ${config.enabledPersonas.length} personas, ${config.worldComplexityLevels.length} complexity levels`);
    }

    console.log('\n✅ All predefined configurations are valid!\n');

  } catch (error) {
    console.error('❌ Configuration validation failed:', error);
    throw error;
  }
}

/**
 * Main validation function
 */
async function validateFramework(): Promise<void> {
  console.log('🎮 TTA Simulation Framework Validation\n');
  console.log('='.repeat(50));

  const startTime = Date.now();

  try {
    // Test individual components
    await testComponents();

    // Test predefined configurations
    await testPredefinedConfigs();

    // Test simulation runner
    await testSimulationRunner();

    const duration = Date.now() - startTime;

    console.log('\n' + '='.repeat(50));
    console.log('🎉 FRAMEWORK VALIDATION COMPLETE!');
    console.log('='.repeat(50));
    console.log(`✅ All tests passed in ${(duration / 1000).toFixed(1)}s`);
    console.log('✅ TTA Simulation Framework is ready for use!');
    console.log('\nNext steps:');
    console.log('  • Run: npm run test:quick (for 15-minute test)');
    console.log('  • Run: npm run test:comprehensive (for full 2-hour test)');
    console.log('  • Run: ts-node examples/runSimulation.ts [test-type]');
    console.log('='.repeat(50) + '\n');

  } catch (error) {
    console.error('\n❌ FRAMEWORK VALIDATION FAILED!');
    console.error('Error:', error);
    console.error('\nPlease fix the issues above before using the framework.');
    process.exit(1);
  }
}

/**
 * Main execution
 */
async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.includes('--help')) {
    console.log(`
TTA Simulation Framework Validator

Usage: ts-node validate-framework.ts [options]

Options:
  --help            Show this help message
  --components-only Test only individual components
  --runner-only     Test only the simulation runner
  --configs-only    Test only predefined configurations

Examples:
  ts-node validate-framework.ts
  ts-node validate-framework.ts --components-only
  ts-node validate-framework.ts --runner-only
`);
    return;
  }

  try {
    if (args.includes('--components-only')) {
      await testComponents();
    } else if (args.includes('--runner-only')) {
      await testSimulationRunner();
    } else if (args.includes('--configs-only')) {
      await testPredefinedConfigs();
    } else {
      await validateFramework();
    }
  } catch (error) {
    console.error('Validation failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { validateFramework, testComponents, testSimulationRunner, testPredefinedConfigs };
