#!/usr/bin/env node

/**
 * Validate World Script
 * 
 * Node.js script to validate franchise worlds for simulation testing
 * and production readiness.
 */

const { getAllWorlds } = require('./get-worlds.js');
const { getAllArchetypes } = require('./get-archetypes.js');

function validateWorldForSimulation(worldId) {
  const world = getAllWorlds().find(w => w.franchiseId === worldId);
  
  if (!world) {
    return {
      isValid: false,
      validationResults: {
        worldExists: false,
        error: `World not found: ${worldId}`
      }
    };
  }
  
  const validationResults = {
    worldExists: true,
    basicConfiguration: validateBasicConfiguration(world),
    therapeuticIntegration: validateTherapeuticIntegration(world),
    contentSafety: validateContentSafety(world),
    technicalReadiness: validateTechnicalReadiness(world),
    characterSupport: validateCharacterSupport(world),
    narrativeStructure: validateNarrativeStructure(world),
    sessionFlexibility: validateSessionFlexibility(world),
    accessibilityCompliance: validateAccessibilityCompliance(world)
  };
  
  // Calculate overall validity
  const validationChecks = Object.values(validationResults).filter(result => 
    typeof result === 'object' && result.hasOwnProperty('isValid')
  );
  
  const passedChecks = validationChecks.filter(check => check.isValid).length;
  const totalChecks = validationChecks.length;
  const validationScore = passedChecks / totalChecks;
  
  const isValid = validationScore >= 0.8; // 80% pass rate required
  
  return {
    isValid,
    validationScore,
    passedChecks,
    totalChecks,
    validationResults,
    recommendations: generateRecommendations(validationResults),
    readinessLevel: determineReadinessLevel(validationScore)
  };
}

function validateBasicConfiguration(world) {
  const checks = {
    hasName: !!world.name,
    hasGenre: !!world.genre && ['fantasy', 'sci-fi'].includes(world.genre),
    hasTherapeuticThemes: Array.isArray(world.therapeuticThemes) && world.therapeuticThemes.length > 0,
    hasTherapeuticApproaches: Array.isArray(world.therapeuticApproaches) && world.therapeuticApproaches.length > 0,
    hasDifficultyLevel: !!world.difficultyLevel && ['beginner', 'intermediate', 'advanced'].includes(world.difficultyLevel),
    hasEstimatedDuration: !!world.estimatedDuration && world.estimatedDuration.hours > 0,
    hasContentRatings: Array.isArray(world.contentRatings) && world.contentRatings.length > 0
  };
  
  const passedChecks = Object.values(checks).filter(Boolean).length;
  const totalChecks = Object.keys(checks).length;
  
  return {
    isValid: passedChecks === totalChecks,
    score: passedChecks / totalChecks,
    checks,
    issues: Object.entries(checks)
      .filter(([key, value]) => !value)
      .map(([key]) => `Missing or invalid: ${key}`)
  };
}

function validateTherapeuticIntegration(world) {
  const requiredApproaches = ['cognitive_behavioral_therapy', 'narrative_therapy', 'mindfulness'];
  const hasRequiredApproaches = requiredApproaches.some(approach => 
    world.therapeuticApproaches.includes(approach)
  );
  
  const therapeuticThemeCategories = [
    'anxiety_management',
    'relationship_building', 
    'confidence_building',
    'emotional_regulation',
    'social_skills'
  ];
  
  const hasTherapeuticThemesCoverage = world.therapeuticThemes.some(theme =>
    therapeuticThemeCategories.some(category => theme.includes(category.split('_')[0]))
  );
  
  const checks = {
    hasRequiredTherapeuticApproaches: hasRequiredApproaches,
    hasTherapeuticThemesCoverage: hasTherapeuticThemesCoverage,
    hasMinimumTherapeuticThemes: world.therapeuticThemes.length >= 3,
    hasMinimumTherapeuticApproaches: world.therapeuticApproaches.length >= 2
  };
  
  const passedChecks = Object.values(checks).filter(Boolean).length;
  const totalChecks = Object.keys(checks).length;
  
  return {
    isValid: passedChecks >= totalChecks * 0.75, // 75% pass rate for therapeutic integration
    score: passedChecks / totalChecks,
    checks,
    supportedApproaches: world.therapeuticApproaches,
    therapeuticThemes: world.therapeuticThemes
  };
}

function validateContentSafety(world) {
  const contentRating = world.contentRatings[0];
  const acceptableRatings = ['E', 'E10+', 'T', 'M'];
  
  const checks = {
    hasContentRating: !!contentRating,
    hasAcceptableRating: contentRating && acceptableRatings.includes(contentRating.rating),
    hasContentDescriptors: contentRating && Array.isArray(contentRating.descriptors),
    noExtremeContent: !contentRating?.descriptors?.some(desc => 
      desc.toLowerCase().includes('extreme') || 
      desc.toLowerCase().includes('graphic') ||
      desc.toLowerCase().includes('intense')
    )
  };
  
  const passedChecks = Object.values(checks).filter(Boolean).length;
  const totalChecks = Object.keys(checks).length;
  
  return {
    isValid: passedChecks === totalChecks,
    score: passedChecks / totalChecks,
    checks,
    contentRating: contentRating?.rating,
    contentDescriptors: contentRating?.descriptors || []
  };
}

function validateTechnicalReadiness(world) {
  const checks = {
    hasUniqueId: !!world.franchiseId && world.franchiseId.length > 0,
    hasValidIdFormat: /^[a-z_]+$/.test(world.franchiseId),
    hasInspirationSource: !!world.inspirationSource,
    hasEstimatedDuration: world.estimatedDuration && world.estimatedDuration.hours > 0,
    durationIsReasonable: world.estimatedDuration && 
      world.estimatedDuration.hours >= 0.25 && 
      world.estimatedDuration.hours <= 8
  };
  
  const passedChecks = Object.values(checks).filter(Boolean).length;
  const totalChecks = Object.keys(checks).length;
  
  return {
    isValid: passedChecks === totalChecks,
    score: passedChecks / totalChecks,
    checks,
    worldId: world.franchiseId,
    estimatedDuration: world.estimatedDuration
  };
}

function validateCharacterSupport(world) {
  const archetypes = getAllArchetypes();
  const supportedArchetypes = archetypes.filter(archetype => 
    archetype.worldAdaptations && archetype.worldAdaptations[world.genre]
  );
  
  const checks = {
    hasArchetypeSupport: supportedArchetypes.length > 0,
    hasMinimumArchetypes: supportedArchetypes.length >= 3,
    hasTherapeuticCharacters: supportedArchetypes.some(archetype => 
      archetype.therapeuticFunction && archetype.therapeuticFunction.length > 0
    ),
    hasVariedRoles: new Set(supportedArchetypes.map(a => a.role)).size >= 2
  };
  
  const passedChecks = Object.values(checks).filter(Boolean).length;
  const totalChecks = Object.keys(checks).length;
  
  return {
    isValid: passedChecks >= totalChecks * 0.75,
    score: passedChecks / totalChecks,
    checks,
    supportedArchetypes: supportedArchetypes.length,
    availableRoles: [...new Set(supportedArchetypes.map(a => a.role))]
  };
}

function validateNarrativeStructure(world) {
  // This would integrate with actual narrative structure validation
  // For now, we'll do basic checks based on world configuration
  
  const checks = {
    hasGenreConsistency: !!world.genre,
    hasThematicCoherence: world.therapeuticThemes.length >= 3,
    hasAppropriateComplexity: world.difficultyLevel && 
      ['beginner', 'intermediate', 'advanced'].includes(world.difficultyLevel),
    hasEngagementPotential: world.inspirationSource && world.inspirationSource.length > 10
  };
  
  const passedChecks = Object.values(checks).filter(Boolean).length;
  const totalChecks = Object.keys(checks).length;
  
  return {
    isValid: passedChecks >= totalChecks * 0.75,
    score: passedChecks / totalChecks,
    checks,
    narrativeComplexity: world.difficultyLevel,
    thematicDepth: world.therapeuticThemes.length
  };
}

function validateSessionFlexibility(world) {
  const duration = world.estimatedDuration.hours;
  
  const checks = {
    supportsShortSessions: duration >= 0.25, // 15 minutes
    supportsMediumSessions: duration >= 1.0,  // 1 hour
    supportsLongSessions: duration <= 4.0,    // Up to 4 hours
    hasReasonableDuration: duration >= 0.25 && duration <= 8.0,
    allowsFlexiblePacing: true // Assume all worlds support flexible pacing
  };
  
  const passedChecks = Object.values(checks).filter(Boolean).length;
  const totalChecks = Object.keys(checks).length;
  
  return {
    isValid: passedChecks >= totalChecks * 0.8,
    score: passedChecks / totalChecks,
    checks,
    estimatedDuration: duration,
    sessionFlexibility: 'high'
  };
}

function validateAccessibilityCompliance(world) {
  // Basic accessibility checks - would be expanded in production
  const checks = {
    hasContentWarnings: world.contentRatings && world.contentRatings.length > 0,
    hasAppropriateRating: world.contentRatings && 
      world.contentRatings[0] && 
      ['E', 'E10+', 'T', 'M'].includes(world.contentRatings[0].rating),
    supportsDiverseThemes: world.therapeuticThemes.length >= 3,
    hasInclusiveDesign: true // Assume inclusive design - would check actual content
  };
  
  const passedChecks = Object.values(checks).filter(Boolean).length;
  const totalChecks = Object.keys(checks).length;
  
  return {
    isValid: passedChecks >= totalChecks * 0.75,
    score: passedChecks / totalChecks,
    checks,
    accessibilityFeatures: ['content_warnings', 'flexible_pacing', 'diverse_themes']
  };
}

function generateRecommendations(validationResults) {
  const recommendations = [];
  
  Object.entries(validationResults).forEach(([category, result]) => {
    if (typeof result === 'object' && result.hasOwnProperty('isValid') && !result.isValid) {
      if (result.issues) {
        recommendations.push(...result.issues.map(issue => `${category}: ${issue}`));
      } else {
        recommendations.push(`${category}: Review and improve this area`);
      }
    }
  });
  
  if (recommendations.length === 0) {
    recommendations.push('World passes all validation checks and is ready for simulation');
  }
  
  return recommendations;
}

function determineReadinessLevel(validationScore) {
  if (validationScore >= 0.95) return 'production_ready';
  if (validationScore >= 0.8) return 'simulation_ready';
  if (validationScore >= 0.6) return 'development_ready';
  return 'needs_improvement';
}

function main() {
  try {
    // Parse command line arguments
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
      console.error(JSON.stringify({
        success: false,
        error: 'World ID required'
      }));
      process.exit(1);
    }
    
    let requestData;
    try {
      requestData = JSON.parse(args[0]);
    } catch (e) {
      console.error(JSON.stringify({
        success: false,
        error: 'Invalid JSON arguments'
      }));
      process.exit(1);
    }
    
    const worldId = requestData.worldId;
    if (!worldId) {
      console.error(JSON.stringify({
        success: false,
        error: 'worldId is required'
      }));
      process.exit(1);
    }
    
    // Validate the world
    const validationResult = validateWorldForSimulation(worldId);
    
    // Return results
    const response = {
      success: true,
      worldId: worldId,
      ...validationResult
    };
    
    console.log(JSON.stringify(response, null, 2));
    
  } catch (error) {
    console.error(JSON.stringify({
      success: false,
      error: error.message
    }));
    process.exit(1);
  }
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = {
  validateWorldForSimulation
};
