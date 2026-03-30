// Logseq: [[TTA.dev/Player_experience/Franchise_worlds/Scripts/Create-parameters]]
#!/usr/bin/env node

/**
 * Create Parameters Script
 *
 * Node.js script to create customized world parameters based on player preferences
 * and therapeutic needs.
 */

const { getAllWorlds } = require('./get-worlds.js');
const { validateWorldForSimulation } = require('./validate-world.js');

function createCustomizedWorldParameters(worldId, playerPreferences) {
  const world = getAllWorlds().find(w => w.franchiseId === worldId);

  if (!world) {
    throw new Error(`World not found: ${worldId}`);
  }

  // Validate world is suitable for customization
  const validation = validateWorldForSimulation(worldId);
  if (!validation.isValid) {
    throw new Error(`World ${worldId} is not ready for parameter customization`);
  }

  // Create base parameters from world configuration
  const baseParameters = {
    worldId: worldId,
    worldName: world.name,
    genre: world.genre,
    baseDifficulty: world.difficultyLevel,
    baseEstimatedDuration: world.estimatedDuration.hours,
    baseTherapeuticApproaches: world.therapeuticApproaches,
    baseTherapeuticThemes: world.therapeuticThemes
  };

  // Apply player preferences to create customized parameters
  const customizedParameters = {
    ...baseParameters,
    therapeuticIntensity: calculateTherapeuticIntensity(world, playerPreferences),
    narrativePace: determineNarrativePace(world, playerPreferences),
    interactionFrequency: determineInteractionFrequency(world, playerPreferences),
    challengeLevel: determineChallengeLevel(world, playerPreferences),
    focusAreas: determineFocusAreas(world, playerPreferences),
    avoidTopics: determineAvoidTopics(playerPreferences),
    sessionLengthPreference: determineSessionLength(world, playerPreferences),
    adaptiveFeatures: determineAdaptiveFeatures(world, playerPreferences),
    accessibilitySettings: determineAccessibilitySettings(playerPreferences),
    therapeuticGoals: determineTherapeuticGoals(world, playerPreferences),
    customizationMetadata: {
      createdAt: new Date().toISOString(),
      playerPreferencesApplied: Object.keys(playerPreferences),
      customizationLevel: calculateCustomizationLevel(playerPreferences)
    }
  };

  return customizedParameters;
}

function calculateTherapeuticIntensity(world, playerPreferences) {
  let intensity = 0.5; // Default medium intensity

  // Adjust based on world difficulty
  const difficultyMap = {
    'beginner': 0.3,
    'intermediate': 0.5,
    'advanced': 0.7
  };
  intensity = difficultyMap[world.difficultyLevel] || 0.5;

  // Adjust based on player preferences
  if (playerPreferences.therapeuticIntensity) {
    intensity = Math.max(0.1, Math.min(0.9, playerPreferences.therapeuticIntensity));
  }

  if (playerPreferences.experienceLevel) {
    const experienceAdjustments = {
      'new_to_therapy': -0.2,
      'some_experience': 0.0,
      'experienced': 0.1,
      'very_experienced': 0.2
    };
    intensity += experienceAdjustments[playerPreferences.experienceLevel] || 0;
  }

  if (playerPreferences.comfortWithTherapy) {
    const comfortAdjustments = {
      'very_uncomfortable': -0.3,
      'somewhat_uncomfortable': -0.1,
      'neutral': 0.0,
      'comfortable': 0.1,
      'very_comfortable': 0.2
    };
    intensity += comfortAdjustments[playerPreferences.comfortWithTherapy] || 0;
  }

  return Math.max(0.1, Math.min(0.9, intensity));
}

function determineNarrativePace(world, playerPreferences) {
  let pace = 'medium'; // Default

  if (playerPreferences.preferredPace) {
    pace = playerPreferences.preferredPace;
  } else if (playerPreferences.sessionLengthPreference) {
    const paceMap = {
      'short': 'fast',
      'medium': 'medium',
      'long': 'slow',
      'flexible': 'adaptive'
    };
    pace = paceMap[playerPreferences.sessionLengthPreference] || 'medium';
  }

  // Adjust based on therapeutic intensity
  if (playerPreferences.therapeuticIntensity > 0.7) {
    pace = pace === 'fast' ? 'medium' : pace; // Slow down for high intensity
  }

  return pace;
}

function determineInteractionFrequency(world, playerPreferences) {
  let frequency = 'balanced'; // Default

  if (playerPreferences.interactionPreference) {
    const frequencyMap = {
      'minimal': 'low',
      'occasional': 'balanced',
      'frequent': 'high',
      'constant': 'very_high'
    };
    frequency = frequencyMap[playerPreferences.interactionPreference] || 'balanced';
  }

  // Adjust based on social comfort
  if (playerPreferences.socialComfort) {
    const socialAdjustments = {
      'very_uncomfortable': 'low',
      'somewhat_uncomfortable': 'balanced',
      'neutral': 'balanced',
      'comfortable': 'high',
      'very_comfortable': 'high'
    };
    frequency = socialAdjustments[playerPreferences.socialComfort] || frequency;
  }

  return frequency;
}

function determineChallengeLevel(world, playerPreferences) {
  let challengeLevel = world.difficultyLevel; // Start with world default

  if (playerPreferences.challengePreference) {
    challengeLevel = playerPreferences.challengePreference;
  }

  // Adjust based on confidence level
  if (playerPreferences.confidenceLevel) {
    const confidenceAdjustments = {
      'very_low': 'beginner',
      'low': 'beginner',
      'medium': 'intermediate',
      'high': 'intermediate',
      'very_high': 'advanced'
    };
    const suggestedLevel = confidenceAdjustments[playerPreferences.confidenceLevel];
    if (suggestedLevel) {
      challengeLevel = suggestedLevel;
    }
  }

  return challengeLevel;
}

function determineFocusAreas(world, playerPreferences) {
  let focusAreas = [...world.therapeuticThemes]; // Start with world themes

  if (playerPreferences.therapeuticGoals && Array.isArray(playerPreferences.therapeuticGoals)) {
    // Merge player goals with world themes
    const playerGoals = playerPreferences.therapeuticGoals;
    focusAreas = [...new Set([...focusAreas, ...playerGoals])];
  }

  if (playerPreferences.primaryConcerns && Array.isArray(playerPreferences.primaryConcerns)) {
    focusAreas = [...new Set([...focusAreas, ...playerPreferences.primaryConcerns])];
  }

  // Prioritize based on player preferences
  if (playerPreferences.priorityAreas && Array.isArray(playerPreferences.priorityAreas)) {
    const prioritized = playerPreferences.priorityAreas.filter(area => focusAreas.includes(area));
    const remaining = focusAreas.filter(area => !playerPreferences.priorityAreas.includes(area));
    focusAreas = [...prioritized, ...remaining];
  }

  return focusAreas.slice(0, 8); // Limit to 8 focus areas for manageability
}

function determineAvoidTopics(playerPreferences) {
  const avoidTopics = [];

  if (playerPreferences.triggersToAvoid && Array.isArray(playerPreferences.triggersToAvoid)) {
    avoidTopics.push(...playerPreferences.triggersToAvoid);
  }

  if (playerPreferences.uncomfortableTopics && Array.isArray(playerPreferences.uncomfortableTopics)) {
    avoidTopics.push(...playerPreferences.uncomfortableTopics);
  }

  if (playerPreferences.contentSensitivities && Array.isArray(playerPreferences.contentSensitivities)) {
    avoidTopics.push(...playerPreferences.contentSensitivities);
  }

  return [...new Set(avoidTopics)]; // Remove duplicates
}

function determineSessionLength(world, playerPreferences) {
  let sessionLength = world.estimatedDuration.hours * 60; // Convert to minutes

  if (playerPreferences.sessionLengthPreference) {
    const lengthMap = {
      'short': 30,
      'medium': 60,
      'long': 120,
      'extended': 180,
      'flexible': sessionLength
    };
    sessionLength = lengthMap[playerPreferences.sessionLengthPreference] || sessionLength;
  }

  if (playerPreferences.availableTime) {
    sessionLength = Math.min(sessionLength, playerPreferences.availableTime);
  }

  return Math.max(15, Math.min(240, sessionLength)); // 15 minutes to 4 hours
}

function determineAdaptiveFeatures(world, playerPreferences) {
  const adaptiveFeatures = {
    dynamicDifficulty: playerPreferences.adaptiveDifficulty !== false,
    personalizedPacing: playerPreferences.adaptivePacing !== false,
    contextualSupport: playerPreferences.contextualHelp !== false,
    progressiveDisclosure: playerPreferences.progressiveComplexity !== false,
    emotionalResponsiveness: playerPreferences.emotionalAdaptation !== false
  };

  // Enable additional features based on preferences
  if (playerPreferences.needsExtraSupport) {
    adaptiveFeatures.enhancedSupport = true;
    adaptiveFeatures.frequentCheckIns = true;
  }

  if (playerPreferences.learningStyle) {
    adaptiveFeatures.learningStyleAdaptation = playerPreferences.learningStyle;
  }

  return adaptiveFeatures;
}

function determineAccessibilitySettings(playerPreferences) {
  const accessibilitySettings = {};

  if (playerPreferences.accessibilityNeeds) {
    Object.assign(accessibilitySettings, playerPreferences.accessibilityNeeds);
  }

  // Default accessibility features
  accessibilitySettings.contentWarnings = true;
  accessibilitySettings.pauseAnytime = true;
  accessibilitySettings.skipContent = true;
  accessibilitySettings.adjustablePacing = true;

  return accessibilitySettings;
}

function determineTherapeuticGoals(world, playerPreferences) {
  const goals = [];

  // Extract goals from world themes
  world.therapeuticThemes.forEach(theme => {
    goals.push({
      area: theme,
      priority: 'medium',
      source: 'world_theme'
    });
  });

  // Add player-specific goals
  if (playerPreferences.therapeuticGoals) {
    playerPreferences.therapeuticGoals.forEach(goal => {
      goals.push({
        area: goal,
        priority: 'high',
        source: 'player_preference'
      });
    });
  }

  if (playerPreferences.primaryConcerns) {
    playerPreferences.primaryConcerns.forEach(concern => {
      goals.push({
        area: concern,
        priority: 'high',
        source: 'primary_concern'
      });
    });
  }

  return goals;
}

function calculateCustomizationLevel(playerPreferences) {
  const preferenceKeys = Object.keys(playerPreferences);
  const totalPossiblePreferences = 20; // Approximate number of possible preferences

  const customizationLevel = preferenceKeys.length / totalPossiblePreferences;

  if (customizationLevel >= 0.8) return 'highly_customized';
  if (customizationLevel >= 0.5) return 'moderately_customized';
  if (customizationLevel >= 0.2) return 'lightly_customized';
  return 'minimally_customized';
}

function main() {
  try {
    // Parse command line arguments
    const args = process.argv.slice(2);

    if (args.length === 0) {
      console.error(JSON.stringify({
        success: false,
        error: 'Arguments required: worldId and playerPreferences'
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

    const { worldId, playerPreferences } = requestData;

    if (!worldId || !playerPreferences) {
      console.error(JSON.stringify({
        success: false,
        error: 'Missing required parameters: worldId and playerPreferences'
      }));
      process.exit(1);
    }

    // Create customized parameters
    const parameters = createCustomizedWorldParameters(worldId, playerPreferences);

    // Return results
    const response = {
      success: true,
      parameters: parameters
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
  createCustomizedWorldParameters
};
