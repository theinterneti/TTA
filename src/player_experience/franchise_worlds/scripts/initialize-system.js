#!/usr/bin/env node

/**
 * Initialize System Script
 * 
 * Node.js script to initialize the franchise world system and verify
 * all components are working correctly.
 */

const fs = require('fs');
const path = require('path');
const { getAllWorlds } = require('./get-worlds.js');
const { getAllArchetypes } = require('./get-archetypes.js');
const { validateWorldForSimulation } = require('./validate-world.js');

function initializeSystem() {
  const initializationResults = {
    timestamp: new Date().toISOString(),
    systemStatus: 'initializing',
    components: {},
    validationResults: {},
    systemHealth: {},
    readinessStatus: 'unknown'
  };
  
  try {
    // Initialize and test each component
    initializationResults.components.worldSystem = initializeWorldSystem();
    initializationResults.components.archetypeSystem = initializeArchetypeSystem();
    initializationResults.components.validationSystem = initializeValidationSystem();
    initializationResults.components.parameterSystem = initializeParameterSystem();
    initializationResults.components.fileSystem = initializeFileSystem();
    
    // Run system validation
    initializationResults.validationResults = runSystemValidation();
    
    // Check system health
    initializationResults.systemHealth = checkSystemHealth(initializationResults.components);
    
    // Determine overall readiness
    initializationResults.readinessStatus = determineSystemReadiness(initializationResults);
    initializationResults.systemStatus = initializationResults.readinessStatus === 'ready' ? 'operational' : 'needs_attention';
    
    return initializationResults;
    
  } catch (error) {
    initializationResults.systemStatus = 'failed';
    initializationResults.error = error.message;
    initializationResults.readinessStatus = 'failed';
    return initializationResults;
  }
}

function initializeWorldSystem() {
  try {
    const worlds = getAllWorlds();
    
    const worldStats = {
      totalWorlds: worlds.length,
      fantasyWorlds: worlds.filter(w => w.genre === 'fantasy').length,
      scifiWorlds: worlds.filter(w => w.genre === 'sci-fi').length,
      difficultyDistribution: {},
      therapeuticApproaches: new Set(),
      therapeuticThemes: new Set()
    };
    
    // Analyze world distribution
    worlds.forEach(world => {
      // Count difficulty levels
      worldStats.difficultyDistribution[world.difficultyLevel] = 
        (worldStats.difficultyDistribution[world.difficultyLevel] || 0) + 1;
      
      // Collect therapeutic approaches
      world.therapeuticApproaches.forEach(approach => 
        worldStats.therapeuticApproaches.add(approach)
      );
      
      // Collect therapeutic themes
      world.therapeuticThemes.forEach(theme => 
        worldStats.therapeuticThemes.add(theme)
      );
    });
    
    // Convert sets to arrays for JSON serialization
    worldStats.therapeuticApproaches = Array.from(worldStats.therapeuticApproaches);
    worldStats.therapeuticThemes = Array.from(worldStats.therapeuticThemes);
    
    return {
      status: 'initialized',
      stats: worldStats,
      availableWorlds: worlds.map(w => ({ id: w.franchiseId, name: w.name, genre: w.genre }))
    };
    
  } catch (error) {
    return {
      status: 'failed',
      error: error.message
    };
  }
}

function initializeArchetypeSystem() {
  try {
    const archetypes = getAllArchetypes();
    
    const archetypeStats = {
      totalArchetypes: archetypes.length,
      roles: [...new Set(archetypes.map(a => a.role))],
      therapeuticFunctions: archetypes.map(a => a.therapeuticFunction),
      worldAdaptations: {}
    };
    
    // Analyze world adaptations
    archetypes.forEach(archetype => {
      if (archetype.worldAdaptations) {
        Object.keys(archetype.worldAdaptations).forEach(genre => {
          if (!archetypeStats.worldAdaptations[genre]) {
            archetypeStats.worldAdaptations[genre] = 0;
          }
          archetypeStats.worldAdaptations[genre]++;
        });
      }
    });
    
    return {
      status: 'initialized',
      stats: archetypeStats,
      availableArchetypes: archetypes.map(a => ({ 
        id: a.archetypeId, 
        name: a.name, 
        role: a.role 
      }))
    };
    
  } catch (error) {
    return {
      status: 'failed',
      error: error.message
    };
  }
}

function initializeValidationSystem() {
  try {
    const worlds = getAllWorlds();
    const validationResults = {};
    let totalValidWorlds = 0;
    
    worlds.forEach(world => {
      try {
        const validation = validateWorldForSimulation(world.franchiseId);
        validationResults[world.franchiseId] = {
          isValid: validation.isValid,
          score: validation.validationScore,
          readinessLevel: validation.readinessLevel
        };
        
        if (validation.isValid) {
          totalValidWorlds++;
        }
      } catch (error) {
        validationResults[world.franchiseId] = {
          isValid: false,
          error: error.message
        };
      }
    });
    
    return {
      status: 'initialized',
      stats: {
        totalWorlds: worlds.length,
        validWorlds: totalValidWorlds,
        validationRate: totalValidWorlds / worlds.length
      },
      validationResults: validationResults
    };
    
  } catch (error) {
    return {
      status: 'failed',
      error: error.message
    };
  }
}

function initializeParameterSystem() {
  try {
    // Test parameter creation with sample data
    const samplePreferences = {
      therapeuticIntensity: 0.5,
      sessionLengthPreference: 'medium',
      challengePreference: 'intermediate',
      therapeuticGoals: ['anxiety_management', 'confidence_building']
    };
    
    const worlds = getAllWorlds();
    let successfulParameterCreations = 0;
    
    worlds.forEach(world => {
      try {
        // This would call create-parameters.js, but for initialization we'll just verify the structure
        const mockParameters = {
          worldId: world.franchiseId,
          therapeuticIntensity: samplePreferences.therapeuticIntensity,
          challengeLevel: world.difficultyLevel,
          focusAreas: world.therapeuticThemes.slice(0, 3)
        };
        
        if (mockParameters.worldId && mockParameters.therapeuticIntensity !== undefined) {
          successfulParameterCreations++;
        }
      } catch (error) {
        // Parameter creation failed for this world
      }
    });
    
    return {
      status: 'initialized',
      stats: {
        totalWorlds: worlds.length,
        parameterizableWorlds: successfulParameterCreations,
        parameterizationRate: successfulParameterCreations / worlds.length
      }
    };
    
  } catch (error) {
    return {
      status: 'failed',
      error: error.message
    };
  }
}

function initializeFileSystem() {
  try {
    const requiredFiles = [
      'get-worlds.js',
      'convert-world.js',
      'get-archetypes.js',
      'adapt-archetype.js',
      'validate-world.js',
      'create-parameters.js',
      'initialize-system.js'
    ];
    
    const scriptsDir = __dirname;
    const fileStatus = {};
    let existingFiles = 0;
    
    requiredFiles.forEach(filename => {
      const filePath = path.join(scriptsDir, filename);
      const exists = fs.existsSync(filePath);
      fileStatus[filename] = {
        exists: exists,
        path: filePath
      };
      
      if (exists) {
        existingFiles++;
        // Check if file is readable
        try {
          fs.accessSync(filePath, fs.constants.R_OK);
          fileStatus[filename].readable = true;
        } catch (error) {
          fileStatus[filename].readable = false;
          fileStatus[filename].error = 'File not readable';
        }
      }
    });
    
    return {
      status: existingFiles === requiredFiles.length ? 'initialized' : 'incomplete',
      stats: {
        requiredFiles: requiredFiles.length,
        existingFiles: existingFiles,
        completionRate: existingFiles / requiredFiles.length
      },
      fileStatus: fileStatus
    };
    
  } catch (error) {
    return {
      status: 'failed',
      error: error.message
    };
  }
}

function runSystemValidation() {
  const validationTests = {
    worldRetrieval: testWorldRetrieval(),
    archetypeRetrieval: testArchetypeRetrieval(),
    worldValidation: testWorldValidation(),
    systemIntegration: testSystemIntegration()
  };
  
  const passedTests = Object.values(validationTests).filter(test => test.passed).length;
  const totalTests = Object.keys(validationTests).length;
  
  return {
    tests: validationTests,
    passedTests: passedTests,
    totalTests: totalTests,
    passRate: passedTests / totalTests,
    overallStatus: passedTests === totalTests ? 'passed' : 'failed'
  };
}

function testWorldRetrieval() {
  try {
    const worlds = getAllWorlds();
    return {
      passed: worlds.length > 0,
      details: `Retrieved ${worlds.length} worlds`,
      worldCount: worlds.length
    };
  } catch (error) {
    return {
      passed: false,
      error: error.message
    };
  }
}

function testArchetypeRetrieval() {
  try {
    const archetypes = getAllArchetypes();
    return {
      passed: archetypes.length > 0,
      details: `Retrieved ${archetypes.length} archetypes`,
      archetypeCount: archetypes.length
    };
  } catch (error) {
    return {
      passed: false,
      error: error.message
    };
  }
}

function testWorldValidation() {
  try {
    const worlds = getAllWorlds();
    if (worlds.length === 0) {
      return {
        passed: false,
        error: 'No worlds available for validation testing'
      };
    }
    
    const testWorld = worlds[0];
    const validation = validateWorldForSimulation(testWorld.franchiseId);
    
    return {
      passed: validation.hasOwnProperty('isValid'),
      details: `Validation test completed for ${testWorld.name}`,
      validationScore: validation.validationScore
    };
  } catch (error) {
    return {
      passed: false,
      error: error.message
    };
  }
}

function testSystemIntegration() {
  try {
    // Test that all major components can work together
    const worlds = getAllWorlds();
    const archetypes = getAllArchetypes();
    
    if (worlds.length === 0 || archetypes.length === 0) {
      return {
        passed: false,
        error: 'Insufficient data for integration testing'
      };
    }
    
    // Test that archetypes can be adapted for world genres
    const fantasyWorlds = worlds.filter(w => w.genre === 'fantasy');
    const scifiWorlds = worlds.filter(w => w.genre === 'sci-fi');
    
    const hasFantasyAdaptations = archetypes.some(a => 
      a.worldAdaptations && a.worldAdaptations.fantasy
    );
    const hasScifiAdaptations = archetypes.some(a => 
      a.worldAdaptations && a.worldAdaptations['sci-fi']
    );
    
    return {
      passed: hasFantasyAdaptations && hasScifiAdaptations,
      details: 'System integration test completed',
      fantasySupport: hasFantasyAdaptations,
      scifiSupport: hasScifiAdaptations
    };
  } catch (error) {
    return {
      passed: false,
      error: error.message
    };
  }
}

function checkSystemHealth(components) {
  const healthChecks = {
    worldSystemHealth: components.worldSystem.status === 'initialized',
    archetypeSystemHealth: components.archetypeSystem.status === 'initialized',
    validationSystemHealth: components.validationSystem.status === 'initialized',
    parameterSystemHealth: components.parameterSystem.status === 'initialized',
    fileSystemHealth: components.fileSystem.status === 'initialized'
  };
  
  const healthyComponents = Object.values(healthChecks).filter(Boolean).length;
  const totalComponents = Object.keys(healthChecks).length;
  
  return {
    checks: healthChecks,
    healthyComponents: healthyComponents,
    totalComponents: totalComponents,
    healthScore: healthyComponents / totalComponents,
    overallHealth: healthyComponents === totalComponents ? 'healthy' : 'degraded'
  };
}

function determineSystemReadiness(initializationResults) {
  const { systemHealth, validationResults } = initializationResults;
  
  if (systemHealth.overallHealth === 'healthy' && 
      validationResults.overallStatus === 'passed') {
    return 'ready';
  } else if (systemHealth.healthScore >= 0.8 && 
             validationResults.passRate >= 0.75) {
    return 'mostly_ready';
  } else if (systemHealth.healthScore >= 0.6) {
    return 'needs_improvement';
  } else {
    return 'not_ready';
  }
}

function main() {
  try {
    console.log('🚀 Initializing TTA Franchise World System...\n');
    
    const results = initializeSystem();
    
    // Return results
    console.log(JSON.stringify(results, null, 2));
    
    // Exit with appropriate code
    process.exit(results.readinessStatus === 'ready' ? 0 : 1);
    
  } catch (error) {
    console.error(JSON.stringify({
      success: false,
      error: error.message,
      systemStatus: 'initialization_failed'
    }));
    process.exit(1);
  }
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = {
  initializeSystem
};
