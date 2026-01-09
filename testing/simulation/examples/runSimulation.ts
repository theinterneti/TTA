// Logseq: [[TTA.dev/Testing/Simulation/Examples/Runsimulation]]
#!/usr/bin/env ts-node

/**
 * TTA Simulation Testing Example
 *
 * Example script demonstrating how to run comprehensive simulation testing
 * for the TTA (Therapeutic Text Adventure) platform.
 */

import { SimulationRunner, SIMULATION_CONFIGS, runTTASimulation } from '../SimulationRunner';
import { PersonaType } from '../personas/UserPersonas';
import { SimulationConfig } from '../core/SimulationEngine';

/**
 * Example 1: Quick validation test
 */
async function runQuickTest() {
  console.log('🚀 Running Quick Validation Test...\n');

  try {
    const report = await runTTASimulation('QUICK_TEST');

    console.log('Quick test completed!');
    console.log(`Success: ${report.executiveSummary.overallSuccess}`);
    console.log(`Sessions: ${report.executiveSummary.totalSessions}`);
    console.log(`Average Engagement: ${(report.executiveSummary.keyMetrics.averageEngagement * 100).toFixed(1)}%`);

    return report;
  } catch (error) {
    console.error('Quick test failed:', error);
    throw error;
  }
}

/**
 * Example 2: Comprehensive testing
 */
async function runComprehensiveTest() {
  console.log('🚀 Running Comprehensive Test...\n');

  try {
    const report = await runTTASimulation('COMPREHENSIVE');

    console.log('Comprehensive test completed!');
    console.log('See detailed results above.');

    return report;
  } catch (error) {
    console.error('Comprehensive test failed:', error);
    throw error;
  }
}

/**
 * Example 3: Custom configuration
 */
async function runCustomTest() {
  console.log('🚀 Running Custom Configuration Test...\n');

  // Create custom configuration focusing on specific personas
  const customConfig: SimulationConfig = {
    maxSimulationDuration: 30 * 60 * 1000, // 30 minutes
    maxConcurrentSessions: 8,

    // Focus on entertainment-oriented personas
    enabledPersonas: [
      PersonaType.CASUAL_EXPLORER,
      PersonaType.STORY_ENTHUSIAST,
      PersonaType.ACHIEVEMENT_HUNTER
    ],
    personaDistribution: {
      [PersonaType.CASUAL_EXPLORER]: 40,
      [PersonaType.STORY_ENTHUSIAST]: 35,
      [PersonaType.ACHIEVEMENT_HUNTER]: 25,
      [PersonaType.WORLD_BUILDER]: 0,
      [PersonaType.MARATHON_PLAYER]: 0,
      [PersonaType.SOCIAL_CONNECTOR]: 0,
      [PersonaType.THERAPEUTIC_SEEKER]: 0,
      [PersonaType.SKEPTICAL_NEWCOMER]: 0
    },

    // Test moderate to complex worlds
    worldComplexityLevels: ['moderate', 'complex'],
    worldSystemsToTest: ['cultural', 'economic', 'social', 'environmental'],

    sessionPatterns: [
      {
        name: 'Entertainment Focus',
        description: 'High entertainment value with subtle therapeutic integration',
        targetDuration: 45,
        minDuration: 30,
        maxDuration: 60,
        interactionDensity: 1.8,
        complexityLevel: 'medium',
        therapeuticFocus: 0.4, // Lower therapeutic focus
        entertainmentFocus: 0.9, // Higher entertainment focus
        suitablePersonas: [
          PersonaType.CASUAL_EXPLORER,
          PersonaType.STORY_ENTHUSIAST,
          PersonaType.ACHIEVEMENT_HUNTER
        ]
      }
    ],

    multiSessionContinuity: false,
    minimumImmersionScore: 0.75,
    minimumEngagementScore: 0.8,
    minimumTherapeuticIntegrationScore: 0.7, // Lower threshold for entertainment focus
    enableRealTimeMetrics: true,
    detailedLogging: true,
    generateVisualReports: false
  };

  try {
    const runner = new SimulationRunner();
    const report = await runner.runWithConfig(customConfig);

    console.log('Custom test completed!');
    console.log('Configuration focused on entertainment value with subtle therapeutic integration.');

    return report;
  } catch (error) {
    console.error('Custom test failed:', error);
    throw error;
  }
}

/**
 * Example 4: Persona-specific analysis
 */
async function analyzeSpecificPersona() {
  console.log('🚀 Running Persona-Specific Analysis...\n');

  // Configuration focusing on therapeutic seekers
  const therapeuticConfig: SimulationConfig = {
    ...SIMULATION_CONFIGS.COMPREHENSIVE,
    maxSimulationDuration: 45 * 60 * 1000, // 45 minutes
    enabledPersonas: [PersonaType.THERAPEUTIC_SEEKER, PersonaType.SOCIAL_CONNECTOR],
    personaDistribution: {
      [PersonaType.THERAPEUTIC_SEEKER]: 70,
      [PersonaType.SOCIAL_CONNECTOR]: 30,
      [PersonaType.CASUAL_EXPLORER]: 0,
      [PersonaType.STORY_ENTHUSIAST]: 0,
      [PersonaType.WORLD_BUILDER]: 0,
      [PersonaType.MARATHON_PLAYER]: 0,
      [PersonaType.ACHIEVEMENT_HUNTER]: 0,
      [PersonaType.SKEPTICAL_NEWCOMER]: 0
    },
    minimumTherapeuticIntegrationScore: 0.9 // Higher therapeutic requirement
  };

  try {
    const runner = new SimulationRunner();
    const report = await runner.runWithConfig(therapeuticConfig);

    console.log('Persona-specific analysis completed!');
    console.log('Focus: Therapeutic Seeker and Social Connector personas');

    // Analyze therapeutic integration specifically
    const therapeuticScore = report.results.overallScores.therapeuticIntegrationScore;
    console.log(`Therapeutic Integration Score: ${(therapeuticScore * 100).toFixed(1)}%`);

    if (therapeuticScore > 0.85) {
      console.log('✅ Excellent therapeutic integration for therapy-focused personas');
    } else {
      console.log('⚠️ Therapeutic integration needs improvement for therapy-focused personas');
    }

    return report;
  } catch (error) {
    console.error('Persona-specific analysis failed:', error);
    throw error;
  }
}

/**
 * Example 5: World generation focus test
 */
async function testWorldGeneration() {
  console.log('🚀 Running World Generation Focus Test...\n');

  const worldFocusConfig: SimulationConfig = {
    ...SIMULATION_CONFIGS.COMPREHENSIVE,
    maxSimulationDuration: 20 * 60 * 1000, // 20 minutes

    // Test all world complexity levels
    worldComplexityLevels: ['simple', 'moderate', 'complex', 'epic'],

    // Test all world systems
    worldSystemsToTest: [
      'cultural', 'economic', 'political', 'environmental',
      'social', 'historical', 'technological', 'religious'
    ],

    // Focus on world-building personas
    enabledPersonas: [PersonaType.WORLD_BUILDER, PersonaType.MARATHON_PLAYER],
    personaDistribution: {
      [PersonaType.WORLD_BUILDER]: 60,
      [PersonaType.MARATHON_PLAYER]: 40,
      [PersonaType.CASUAL_EXPLORER]: 0,
      [PersonaType.STORY_ENTHUSIAST]: 0,
      [PersonaType.SOCIAL_CONNECTOR]: 0,
      [PersonaType.ACHIEVEMENT_HUNTER]: 0,
      [PersonaType.THERAPEUTIC_SEEKER]: 0,
      [PersonaType.SKEPTICAL_NEWCOMER]: 0
    }
  };

  try {
    const runner = new SimulationRunner();
    const report = await runner.runWithConfig(worldFocusConfig);

    console.log('World generation test completed!');

    // Analyze world generation results
    const worldScore = report.results.overallScores.worldGenerationScore;
    const worldTests = report.results.worldGenerationTests;

    console.log(`World Generation Score: ${(worldScore * 100).toFixed(1)}%`);
    console.log(`Total Worlds Tested: ${worldTests.length}`);

    // Analyze by complexity level
    const complexityResults = worldTests.reduce((acc, test) => {
      if (!acc[test.complexityLevel]) {
        acc[test.complexityLevel] = [];
      }
      acc[test.complexityLevel].push(test.overallScore);
      return acc;
    }, {} as Record<string, number[]>);

    console.log('\nResults by Complexity Level:');
    Object.entries(complexityResults).forEach(([level, scores]) => {
      const avgScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
      console.log(`  ${level}: ${(avgScore * 100).toFixed(1)}% (${scores.length} worlds)`);
    });

    return report;
  } catch (error) {
    console.error('World generation test failed:', error);
    throw error;
  }
}

/**
 * Main execution function
 */
async function main() {
  console.log('🎮 TTA Simulation Testing Examples\n');

  const args = process.argv.slice(2);
  const testType = args[0] || 'comprehensive';

  try {
    switch (testType.toLowerCase()) {
      case 'quick':
        await runQuickTest();
        break;

      case 'comprehensive':
        await runComprehensiveTest();
        break;

      case 'custom':
        await runCustomTest();
        break;

      case 'persona':
        await analyzeSpecificPersona();
        break;

      case 'world':
        await testWorldGeneration();
        break;

      case 'all':
        console.log('Running all test examples...\n');
        await runQuickTest();
        console.log('\n' + '-'.repeat(50) + '\n');
        await runCustomTest();
        console.log('\n' + '-'.repeat(50) + '\n');
        await analyzeSpecificPersona();
        console.log('\n' + '-'.repeat(50) + '\n');
        await testWorldGeneration();
        break;

      default:
        console.log('Available test types:');
        console.log('  quick         - Quick validation test (15 minutes)');
        console.log('  comprehensive - Full comprehensive test (2 hours)');
        console.log('  custom        - Custom configuration example');
        console.log('  persona       - Persona-specific analysis');
        console.log('  world         - World generation focus test');
        console.log('  all           - Run all examples (except comprehensive)');
        console.log('\nUsage: ts-node runSimulation.ts [test-type]');
        break;
    }
  } catch (error) {
    console.error('Simulation failed:', error);
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

export {
  runQuickTest,
  runComprehensiveTest,
  runCustomTest,
  analyzeSpecificPersona,
  testWorldGeneration
};
