#!/usr/bin/env node

/**
 * Get Franchise Worlds Script
 *
 * Node.js script to retrieve franchise worlds from the TypeScript system
 * for integration with the Python TTA API.
 */

const fs = require('fs');
const path = require('path');

// Mock implementation since we can't directly import TypeScript modules
// In production, this would compile the TypeScript and import the actual modules

const FRANCHISE_WORLDS = {
  fantasy: [
    {
      franchiseId: 'eldermere_realms',
      name: 'Eldermere Realms',
      genre: 'fantasy',
      inspirationSource: 'Epic fantasy with diverse cultures and ancient mysteries',
      therapeuticThemes: [
        'courage_and_resilience',
        'friendship_and_belonging',
        'overcoming_adversity',
        'finding_purpose',
        'healing_from_trauma',
        'building_confidence'
      ],
      therapeuticApproaches: [
        'cognitive_behavioral_therapy',
        'narrative_therapy',
        'mindfulness',
        'group_therapy'
      ],
      difficultyLevel: 'intermediate',
      estimatedDuration: { hours: 2 },
      contentRatings: [
        { system: 'ESRB', rating: 'T', descriptors: ['Fantasy Violence', 'Mild Language'] }
      ]
    },
    {
      franchiseId: 'arcanum_academy',
      name: 'Arcanum Academy',
      genre: 'fantasy',
      inspirationSource: 'Magical academy with focus on learning, friendship, and personal growth',
      therapeuticThemes: [
        'academic_anxiety',
        'social_belonging',
        'self_discovery',
        'friendship_building',
        'overcoming_learning_challenges',
        'building_confidence'
      ],
      therapeuticApproaches: [
        'cognitive_behavioral_therapy',
        'group_therapy',
        'mindfulness',
        'solution_focused_therapy'
      ],
      difficultyLevel: 'beginner',
      estimatedDuration: { hours: 1.5 },
      contentRatings: [
        { system: 'ESRB', rating: 'E10+', descriptors: ['Mild Fantasy Violence'] }
      ]
    },
    {
      franchiseId: 'crowns_gambit',
      name: 'Crown\'s Gambit',
      genre: 'fantasy',
      inspirationSource: 'Political intrigue fantasy with focus on leadership, ethics, and social dynamics',
      therapeuticThemes: [
        'leadership_development',
        'ethical_decision_making',
        'social_anxiety_in_formal_settings',
        'conflict_resolution',
        'power_and_responsibility',
        'building_healthy_boundaries'
      ],
      therapeuticApproaches: [
        'cognitive_behavioral_therapy',
        'narrative_therapy',
        'solution_focused_therapy',
        'group_therapy'
      ],
      difficultyLevel: 'advanced',
      estimatedDuration: { hours: 3 },
      contentRatings: [
        { system: 'ESRB', rating: 'T', descriptors: ['Fantasy Violence', 'Mild Language', 'Simulated Gambling'] }
      ]
    }
  ],
  'sci-fi': [
    {
      franchiseId: 'stellar_confederation',
      name: 'Stellar Confederation',
      genre: 'sci-fi',
      inspirationSource: 'Optimistic space exploration with diverse alien cultures and diplomatic challenges',
      therapeuticThemes: [
        'cultural_understanding',
        'leadership_development',
        'team_collaboration',
        'ethical_decision_making',
        'overcoming_prejudice',
        'finding_purpose_in_vastness'
      ],
      therapeuticApproaches: [
        'cognitive_behavioral_therapy',
        'group_therapy',
        'solution_focused_therapy',
        'narrative_therapy'
      ],
      difficultyLevel: 'intermediate',
      estimatedDuration: { hours: 2.5 },
      contentRatings: [
        { system: 'ESRB', rating: 'T', descriptors: ['Sci-Fi Violence', 'Mild Language'] }
      ]
    },
    {
      franchiseId: 'neon_metropolis',
      name: 'Neon Metropolis',
      genre: 'sci-fi',
      inspirationSource: 'Cyberpunk urban environment with focus on identity, technology, and social justice',
      therapeuticThemes: [
        'identity_in_digital_age',
        'social_justice_and_activism',
        'technology_life_balance',
        'authentic_relationships',
        'overcoming_systemic_oppression',
        'finding_purpose_in_urban_environment'
      ],
      therapeuticApproaches: [
        'narrative_therapy',
        'cognitive_behavioral_therapy',
        'group_therapy',
        'solution_focused_therapy'
      ],
      difficultyLevel: 'advanced',
      estimatedDuration: { hours: 2.5 },
      contentRatings: [
        { system: 'ESRB', rating: 'M', descriptors: ['Violence', 'Strong Language', 'Suggestive Themes'] }
      ]
    }
  ]
};

function getAllWorlds() {
  const allWorlds = [];
  Object.values(FRANCHISE_WORLDS).forEach(genreWorlds => {
    allWorlds.push(...genreWorlds);
  });
  return allWorlds;
}

function getWorldsByGenre(genre) {
  return FRANCHISE_WORLDS[genre] || [];
}

function main() {
  try {
    // Parse command line arguments
    const args = process.argv.slice(2);
    let requestData = {};

    if (args.length > 0) {
      try {
        requestData = JSON.parse(args[0]);
      } catch (e) {
        console.error(JSON.stringify({
          success: false,
          error: 'Invalid JSON arguments'
        }));
        process.exit(1);
      }
    }

    const genre = requestData.genre;
    let worlds;

    if (genre) {
      worlds = getWorldsByGenre(genre);
    } else {
      worlds = getAllWorlds();
    }

    // Return results
    const response = {
      success: true,
      worlds: worlds,
      totalCount: worlds.length,
      genreFilter: genre || 'all'
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
  getAllWorlds,
  getWorldsByGenre,
  FRANCHISE_WORLDS
};
