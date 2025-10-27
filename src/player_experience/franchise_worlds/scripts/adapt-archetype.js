#!/usr/bin/env node

/**
 * Adapt Archetype Script
 *
 * Node.js script to adapt character archetypes for specific world contexts
 * and therapeutic needs.
 */

const { getArchetypeById } = require('./get-archetypes.js');

function adaptArchetypeForWorld(archetypeId, worldGenre, worldContext) {
  const baseArchetype = getArchetypeById(archetypeId);

  if (!baseArchetype) {
    throw new Error(`Archetype not found: ${archetypeId}`);
  }

  // Create adapted version
  const adaptedArchetype = {
    ...baseArchetype,
    adaptedFor: {
      worldGenre: worldGenre,
      worldContext: worldContext,
      adaptationTimestamp: new Date().toISOString()
    }
  };

  // Apply world-specific adaptations
  if (baseArchetype.worldAdaptations && baseArchetype.worldAdaptations[worldGenre]) {
    adaptedArchetype.worldSpecificForm = baseArchetype.worldAdaptations[worldGenre];
  }

  // Adapt personality traits for world context
  adaptedArchetype.adaptedPersonality = adaptPersonalityForWorld(
    baseArchetype.personality,
    worldGenre,
    worldContext
  );

  // Adapt interaction patterns for world context
  adaptedArchetype.adaptedInteractionPatterns = adaptInteractionPatternsForWorld(
    baseArchetype.interactionPatterns,
    worldGenre,
    worldContext
  );

  // Generate world-specific dialogue examples
  adaptedArchetype.dialogueExamples = generateDialogueExamples(
    baseArchetype,
    worldGenre,
    worldContext
  );

  // Adapt therapeutic techniques for world context
  adaptedArchetype.contextualTherapeuticTechniques = adaptTherapeuticTechniques(
    baseArchetype.interactionPatterns,
    worldGenre,
    worldContext
  );

  return adaptedArchetype;
}

function adaptPersonalityForWorld(personality, worldGenre, worldContext) {
  const adaptedPersonality = { ...personality };

  // Add world-specific personality elements
  const worldSpecificTraits = getWorldSpecificTraits(worldGenre, worldContext);
  adaptedPersonality.worldSpecificTraits = worldSpecificTraits;

  // Adapt communication style for world
  adaptedPersonality.adaptedCommunicationStyle = adaptCommunicationStyle(
    personality.communicationStyle,
    worldGenre,
    worldContext
  );

  return adaptedPersonality;
}

function getWorldSpecificTraits(worldGenre, worldContext) {
  const traitMap = {
    fantasy: {
      'eldermere_realms': ['mystical_wisdom', 'ancient_knowledge', 'connection_to_nature'],
      'arcanum_academy': ['scholarly', 'pedagogical', 'academically_supportive'],
      'crowns_gambit': ['politically_astute', 'diplomatically_skilled', 'ethically_grounded']
    },
    'sci-fi': {
      'stellar_confederation': ['technologically_adept', 'culturally_aware', 'diplomatically_minded'],
      'neon_metropolis': ['street_smart', 'digitally_native', 'socially_conscious']
    }
  };

  return traitMap[worldGenre]?.[worldContext] || ['adaptable', 'contextually_aware'];
}

function adaptCommunicationStyle(baseCommunicationStyle, worldGenre, worldContext) {
  const styleAdaptations = {
    fantasy: {
      'eldermere_realms': 'Uses nature metaphors and ancient wisdom sayings',
      'arcanum_academy': 'Employs academic language and learning-focused analogies',
      'crowns_gambit': 'Speaks with diplomatic precision and political awareness'
    },
    'sci-fi': {
      'stellar_confederation': 'Uses space exploration metaphors and diplomatic language',
      'neon_metropolis': 'Employs tech-savvy language and urban cultural references'
    }
  };

  const adaptation = styleAdaptations[worldGenre]?.[worldContext];
  return adaptation ? `${baseCommunicationStyle}. ${adaptation}` : baseCommunicationStyle;
}

function adaptInteractionPatternsForWorld(interactionPatterns, worldGenre, worldContext) {
  return interactionPatterns.map(pattern => ({
    ...pattern,
    worldAdaptedResponse: adaptResponseForWorld(pattern.response, worldGenre, worldContext),
    contextualExamples: generateContextualExamples(pattern, worldGenre, worldContext)
  }));
}

function adaptResponseForWorld(response, worldGenre, worldContext) {
  const responseAdaptations = {
    fantasy: {
      'eldermere_realms': 'Incorporates wisdom from the ancient forests and mystical traditions',
      'arcanum_academy': 'References magical learning principles and academic growth',
      'crowns_gambit': 'Draws from political wisdom and ethical leadership principles'
    },
    'sci-fi': {
      'stellar_confederation': 'References interstellar exploration and diplomatic protocols',
      'neon_metropolis': 'Incorporates digital age wisdom and urban survival skills'
    }
  };

  const adaptation = responseAdaptations[worldGenre]?.[worldContext];
  return adaptation ? `${response} (${adaptation})` : response;
}

function generateContextualExamples(pattern, worldGenre, worldContext) {
  const exampleMap = {
    fantasy: {
      'eldermere_realms': {
        'player_expresses_doubt': 'Like a young tree doubting its ability to reach the canopy, you have roots deeper than you know.',
        'player_faces_challenge': 'Even the mightiest oak was once an acorn that held its ground.',
        'player_needs_direction': 'The path through the forest is clearest when you know which star guides you home.'
      },
      'arcanum_academy': {
        'player_expresses_doubt': 'Every great wizard once struggled with their first spell. Your potential is like a book waiting to be written.',
        'player_faces_challenge': 'This challenge is like a difficult potion - each ingredient must be added with patience and precision.',
        'player_needs_direction': 'Your magical path is unique, like a spell that only you can cast.'
      }
    },
    'sci-fi': {
      'stellar_confederation': {
        'player_expresses_doubt': 'Every great explorer once stood at the edge of unknown space, wondering if they were ready for the journey.',
        'player_faces_challenge': 'This situation requires the same careful navigation as approaching a new star system.',
        'player_needs_direction': 'Your mission parameters are clear when you understand your core values and objectives.'
      }
    }
  };

  return exampleMap[worldGenre]?.[worldContext]?.[pattern.trigger] ||
         `Contextual example for ${pattern.trigger} in ${worldContext}`;
}

function generateDialogueExamples(archetype, worldGenre, worldContext) {
  const dialogueMap = {
    wise_mentor: {
      fantasy: {
        'eldermere_realms': [
          '"The ancient trees whisper of courage found not in the absence of fear, but in the choice to act despite it."',
          '"Young one, your heart carries the wisdom of those who came before. Trust in that guidance."'
        ],
        'arcanum_academy': [
          '"Every spell begins with belief in oneself. Your magic is stronger than you know."',
          '"The greatest lessons are learned not from books, but from the courage to try and try again."'
        ]
      },
      'sci-fi': {
        'stellar_confederation': [
          '"In the vastness of space, we find that our greatest strength lies in our connections to others."',
          '"Every successful mission begins with understanding both your destination and your purpose."'
        ]
      }
    },
    loyal_companion: {
      fantasy: {
        'eldermere_realms': [
          '"I\'ll stand with you through whatever storms may come, just as the mountains stand firm through the ages."',
          '"Together we\'re stronger than any challenge this realm can throw at us!"'
        ]
      }
    }
  };

  return dialogueMap[archetype.archetypeId]?.[worldGenre]?.[worldContext] || [
    `"I believe in you and your ability to overcome this challenge."`,
    `"We'll face this together, one step at a time."`
  ];
}

function adaptTherapeuticTechniques(interactionPatterns, worldGenre, worldContext) {
  const techniques = new Set();

  interactionPatterns.forEach(pattern => {
    techniques.add(pattern.therapeuticTechnique);
  });

  // Add world-specific therapeutic adaptations
  const worldSpecificTechniques = {
    fantasy: {
      'eldermere_realms': ['nature_based_mindfulness', 'mythological_reframing', 'fellowship_building'],
      'arcanum_academy': ['academic_anxiety_management', 'peer_learning_support', 'magical_thinking_restructuring'],
      'crowns_gambit': ['leadership_confidence_building', 'ethical_decision_frameworks', 'political_anxiety_management']
    },
    'sci-fi': {
      'stellar_confederation': ['cultural_empathy_building', 'exploration_courage_development', 'diplomatic_communication_skills'],
      'neon_metropolis': ['digital_identity_exploration', 'urban_stress_management', 'social_justice_empowerment']
    }
  };

  const specificTechniques = worldSpecificTechniques[worldGenre]?.[worldContext] || [];
  specificTechniques.forEach(technique => techniques.add(technique));

  return Array.from(techniques);
}

function main() {
  try {
    // Parse command line arguments
    const args = process.argv.slice(2);

    if (args.length === 0) {
      console.error(JSON.stringify({
        success: false,
        error: 'Arguments required: archetypeId, worldGenre, worldContext'
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

    const { archetypeId, worldGenre, worldContext } = requestData;

    if (!archetypeId || !worldGenre || !worldContext) {
      console.error(JSON.stringify({
        success: false,
        error: 'Missing required parameters: archetypeId, worldGenre, worldContext'
      }));
      process.exit(1);
    }

    // Adapt the archetype
    const adaptedArchetype = adaptArchetypeForWorld(archetypeId, worldGenre, worldContext);

    // Return results
    const response = {
      success: true,
      adaptedArchetype: adaptedArchetype
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
  adaptArchetypeForWorld
};
