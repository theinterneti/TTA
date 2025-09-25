#!/usr/bin/env node

/**
 * Convert World Script
 * 
 * Node.js script to convert a franchise world to TTA WorldDetails format
 */

const { getAllWorlds } = require('./get-worlds.js');

function convertFranchiseWorldToTTA(franchiseWorld) {
  return {
    world_id: franchiseWorld.franchiseId,
    name: franchiseWorld.name,
    description: generateShortDescription(franchiseWorld),
    long_description: generateLongDescription(franchiseWorld),
    therapeutic_themes: franchiseWorld.therapeuticThemes,
    therapeutic_approaches: franchiseWorld.therapeuticApproaches,
    difficulty_level: franchiseWorld.difficultyLevel,
    estimated_duration: franchiseWorld.estimatedDuration,
    setting_description: generateSettingDescription(franchiseWorld),
    key_characters: generateKeyCharacters(franchiseWorld),
    main_storylines: generateMainStorylines(franchiseWorld),
    therapeutic_techniques_used: extractTherapeuticTechniques(franchiseWorld),
    prerequisites: generatePrerequisites(franchiseWorld),
    recommended_therapeutic_readiness: calculateTherapeuticReadiness(franchiseWorld),
    content_warnings: generateContentWarnings(franchiseWorld)
  };
}

function generateShortDescription(world) {
  return `A ${world.genre} adventure inspired by ${world.inspirationSource}. ` +
         `Explore themes of ${world.therapeuticThemes.slice(0, 3).join(', ')} through engaging storytelling.`;
}

function generateLongDescription(world) {
  return `Experience the wonder of ${world.name}, a ${world.genre} world inspired by ${world.inspirationSource}. ` +
         `This therapeutic adventure combines the excitement of epic storytelling with meaningful personal growth, ` +
         `addressing themes of ${world.therapeuticThemes.join(', ')}. Journey through richly detailed environments ` +
         `where your choices matter and every interaction supports your therapeutic goals.`;
}

function generateSettingDescription(world) {
  const settingMap = {
    'eldermere_realms': 'A vast fantasy realm featuring diverse cultures, ancient forests, majestic mountains, and mystical locations where fellowship and courage are tested.',
    'arcanum_academy': 'A magical academy with enchanted halls, diverse student houses, mystical libraries, and grounds where learning and friendship flourish.',
    'crowns_gambit': 'A complex political landscape of noble courts, strategic cities, and diplomatic chambers where leadership and ethics are forged.',
    'stellar_confederation': 'A galactic federation spanning multiple star systems, diverse alien worlds, and advanced starships where diplomacy and exploration thrive.',
    'neon_metropolis': 'A cyberpunk urban environment with towering megacorps, underground communities, and digital networks where identity and justice intersect.'
  };
  
  return settingMap[world.franchiseId] || `A ${world.genre} world inspired by ${world.inspirationSource}`;
}

function generateKeyCharacters(world) {
  const characterMap = {
    'eldermere_realms': [
      { name: 'Sage Elderwood', role: 'Wise Mentor', description: 'Provides guidance and wisdom for the journey ahead' },
      { name: 'Finn Trueheart', role: 'Loyal Companion', description: 'Offers unwavering friendship and support' }
    ],
    'arcanum_academy': [
      { name: 'Professor Mindwell', role: 'Supportive Teacher', description: 'Helps students overcome academic challenges' },
      { name: 'Alex Starfriend', role: 'Peer Mentor', description: 'Guides new students through academy life' }
    ],
    'crowns_gambit': [
      { name: 'Counselor Sage', role: 'Political Advisor', description: 'Provides ethical guidance in political matters' },
      { name: 'Lady Justice', role: 'Moral Compass', description: 'Represents integrity in court politics' }
    ],
    'stellar_confederation': [
      { name: 'Captain Harmony', role: 'Diplomatic Leader', description: 'Models ethical leadership and cultural understanding' },
      { name: 'Ambassador Unity', role: 'Cultural Bridge', description: 'Facilitates understanding between species' }
    ],
    'neon_metropolis': [
      { name: 'Sage Neon', role: 'Street Mentor', description: 'Guides authentic identity formation in urban environment' },
      { name: 'Justice Hacker', role: 'Social Activist', description: 'Fights for equality and social change' }
    ]
  };
  
  return characterMap[world.franchiseId] || [];
}

function generateMainStorylines(world) {
  const storylineMap = {
    'eldermere_realms': [
      'The Fellowship Quest: Unite diverse companions to face a great challenge',
      'The Ancient Mystery: Uncover secrets that test courage and wisdom',
      'The Village Crisis: Protect a community through cooperation and bravery'
    ],
    'arcanum_academy': [
      'The First Year Challenge: Navigate academic and social pressures',
      'The House Competition: Build teamwork and healthy rivalry',
      'The Magical Crisis: Use learning and friendship to solve problems'
    ],
    'crowns_gambit': [
      'The Succession Crisis: Navigate political intrigue with ethical leadership',
      'The Alliance Negotiations: Build coalitions through diplomacy',
      'The Court Conspiracy: Uncover corruption while maintaining integrity'
    ],
    'stellar_confederation': [
      'The First Contact Mission: Establish peaceful relations with new species',
      'The Diplomatic Crisis: Resolve conflicts through understanding',
      'The Exploration Discovery: Make ethical decisions about new worlds'
    ],
    'neon_metropolis': [
      'The Corporate Infiltration: Expose corruption while maintaining identity',
      'The Community Defense: Protect neighborhood from corporate takeover',
      'The Identity Quest: Discover authentic self in digital age'
    ]
  };
  
  return storylineMap[world.franchiseId] || [];
}

function extractTherapeuticTechniques(world) {
  const techniqueMap = {
    'cognitive_behavioral_therapy': ['cognitive_restructuring', 'behavioral_activation', 'thought_challenging'],
    'narrative_therapy': ['story_reframing', 'identity_exploration', 'values_clarification'],
    'mindfulness': ['present_moment_awareness', 'meditation_practices', 'mindful_breathing'],
    'group_therapy': ['peer_support', 'social_skills_practice', 'group_problem_solving'],
    'solution_focused_therapy': ['goal_setting', 'strength_identification', 'solution_building']
  };
  
  const techniques = new Set();
  world.therapeuticApproaches.forEach(approach => {
    const approachTechniques = techniqueMap[approach] || [];
    approachTechniques.forEach(technique => techniques.add(technique));
  });
  
  return Array.from(techniques);
}

function generatePrerequisites(world) {
  const prerequisites = [];
  
  if (world.difficultyLevel === 'advanced') {
    prerequisites.push({
      type: 'therapeutic_readiness',
      description: 'Comfortable with complex therapeutic content and self-reflection'
    });
    prerequisites.push({
      type: 'complexity_comfort',
      description: 'Comfortable with complex narratives and multiple interconnected systems'
    });
  } else if (world.difficultyLevel === 'intermediate') {
    prerequisites.push({
      type: 'therapeutic_readiness',
      description: 'Some experience with therapeutic content helpful'
    });
  }
  
  return prerequisites;
}

function calculateTherapeuticReadiness(world) {
  const difficultyMap = {
    'beginner': 0.3,
    'intermediate': 0.6,
    'advanced': 0.8
  };
  
  return difficultyMap[world.difficultyLevel] || 0.5;
}

function generateContentWarnings(world) {
  const warnings = [];
  
  // Extract from content ratings
  world.contentRatings.forEach(rating => {
    rating.descriptors.forEach(descriptor => {
      if (!warnings.includes(descriptor)) {
        warnings.push(descriptor);
      }
    });
  });
  
  // Add therapeutic content warnings
  if (world.therapeuticThemes.includes('healing_from_trauma')) {
    warnings.push('Contains themes related to trauma and recovery');
  }
  
  if (world.therapeuticThemes.includes('academic_anxiety') || 
      world.therapeuticThemes.includes('social_anxiety_in_formal_settings')) {
    warnings.push('Contains scenarios that may trigger anxiety (in therapeutic context)');
  }
  
  return warnings;
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
    
    // Find the franchise world
    const allWorlds = getAllWorlds();
    const franchiseWorld = allWorlds.find(world => world.franchiseId === worldId);
    
    if (!franchiseWorld) {
      console.error(JSON.stringify({
        success: false,
        error: `World not found: ${worldId}`
      }));
      process.exit(1);
    }
    
    // Convert to TTA format
    const worldDetails = convertFranchiseWorldToTTA(franchiseWorld);
    
    // Return results
    const response = {
      success: true,
      worldDetails: worldDetails
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
  convertFranchiseWorldToTTA
};
