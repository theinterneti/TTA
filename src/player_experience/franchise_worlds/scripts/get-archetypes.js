// Logseq: [[TTA.dev/Player_experience/Franchise_worlds/Scripts/Get-archetypes]]
#!/usr/bin/env node

/**
 * Get Character Archetypes Script
 *
 * Node.js script to retrieve character archetypes from the TypeScript system
 * for integration with the Python TTA API.
 */

const CHARACTER_ARCHETYPES = [
  {
    archetypeId: 'wise_mentor',
    name: 'Wise Mentor',
    inspirationSource: 'Classic mentor figures from literature and film',
    role: 'Guide and Teacher',
    therapeuticFunction: 'Provides CBT-style guidance, reframing techniques, and emotional support through wisdom and experience',
    personality: {
      traits: [
        'patient',
        'wise',
        'encouraging',
        'insightful',
        'calm',
        'supportive',
        'experienced',
        'trustworthy'
      ],
      communicationStyle: 'Gentle questioning, metaphorical stories, reflective listening',
      therapeuticApproach: 'Socratic method, cognitive restructuring, values exploration'
    },
    adaptationNotes: 'Can be adapted as elderly wizard, experienced captain, wise elder, or seasoned professional depending on world context',
    interactionPatterns: [
      {
        trigger: 'player_expresses_doubt',
        response: 'Gentle reframing and confidence building',
        therapeuticTechnique: 'cognitive_restructuring'
      },
      {
        trigger: 'player_faces_challenge',
        response: 'Wisdom sharing and problem-solving guidance',
        therapeuticTechnique: 'solution_focused_therapy'
      },
      {
        trigger: 'player_needs_direction',
        response: 'Values clarification and purpose exploration',
        therapeuticTechnique: 'narrative_therapy'
      }
    ],
    worldAdaptations: {
      fantasy: 'Wise wizard, ancient druid, experienced knight-commander',
      'sci-fi': 'Veteran captain, AI mentor, experienced scientist',
      modern: 'Therapist, teacher, experienced professional'
    }
  },
  {
    archetypeId: 'loyal_companion',
    name: 'Loyal Companion',
    inspirationSource: 'Faithful friends and companions from adventure stories',
    role: 'Supportive Friend',
    therapeuticFunction: 'Models healthy relationships, provides peer support, and demonstrates loyalty and friendship skills',
    personality: {
      traits: [
        'loyal',
        'brave',
        'optimistic',
        'reliable',
        'caring',
        'honest',
        'encouraging',
        'steadfast'
      ],
      communicationStyle: 'Direct but caring, humor to lighten mood, unwavering support',
      therapeuticApproach: 'Peer support, social skills modeling, emotional validation'
    },
    adaptationNotes: 'Represents the ideal friend - someone who stands by you through challenges and celebrates successes',
    interactionPatterns: [
      {
        trigger: 'player_feels_alone',
        response: 'Reassurance of friendship and belonging',
        therapeuticTechnique: 'social_support'
      },
      {
        trigger: 'player_lacks_confidence',
        response: 'Encouragement and belief in player abilities',
        therapeuticTechnique: 'strength_identification'
      },
      {
        trigger: 'player_faces_social_anxiety',
        response: 'Social skills modeling and practice',
        therapeuticTechnique: 'behavioral_rehearsal'
      }
    ],
    worldAdaptations: {
      fantasy: 'Brave hobbit, loyal dwarf, faithful animal companion',
      'sci-fi': 'Trusted crew member, loyal android, alien friend',
      modern: 'Best friend, supportive colleague, therapy group member'
    }
  },
  {
    archetypeId: 'reluctant_hero',
    name: 'Reluctant Hero',
    inspirationSource: 'Heroes who initially doubt themselves but find courage',
    role: 'Fellow Traveler',
    therapeuticFunction: 'Models overcoming anxiety and self-doubt, demonstrates that courage comes from facing fears',
    personality: {
      traits: [
        'anxious',
        'self-doubting',
        'ultimately_brave',
        'relatable',
        'growing',
        'determined',
        'empathetic',
        'resilient'
      ],
      communicationStyle: 'Vulnerable sharing, mutual support, growth-oriented',
      therapeuticApproach: 'Anxiety management, courage building, self-efficacy development'
    },
    adaptationNotes: 'Mirrors player journey - starts uncertain but grows in confidence through shared experiences',
    interactionPatterns: [
      {
        trigger: 'player_expresses_anxiety',
        response: 'Shared vulnerability and coping strategies',
        therapeuticTechnique: 'anxiety_management'
      },
      {
        trigger: 'player_avoids_challenge',
        response: 'Mutual encouragement and small steps approach',
        therapeuticTechnique: 'behavioral_activation'
      },
      {
        trigger: 'player_achieves_success',
        response: 'Celebration and confidence building',
        therapeuticTechnique: 'success_amplification'
      }
    ],
    worldAdaptations: {
      fantasy: 'Uncertain young mage, reluctant chosen one, anxious squire',
      'sci-fi': 'Nervous cadet, reluctant pilot, anxious scientist',
      modern: 'Anxious student, uncertain professional, hesitant leader'
    }
  },
  {
    archetypeId: 'wise_healer',
    name: 'Wise Healer',
    inspirationSource: 'Healing figures who provide comfort and restoration',
    role: 'Healer and Nurturer',
    therapeuticFunction: 'Teaches self-care, mindfulness, and emotional healing through compassionate presence',
    personality: {
      traits: [
        'compassionate',
        'nurturing',
        'intuitive',
        'peaceful',
        'healing',
        'mindful',
        'gentle',
        'restorative'
      ],
      communicationStyle: 'Soft-spoken, mindful presence, healing-focused language',
      therapeuticApproach: 'Mindfulness, self-care, emotional regulation, trauma-informed care'
    },
    adaptationNotes: 'Focuses on healing and restoration - both physical and emotional wellness',
    interactionPatterns: [
      {
        trigger: 'player_shows_stress',
        response: 'Mindfulness and relaxation techniques',
        therapeuticTechnique: 'mindfulness_practice'
      },
      {
        trigger: 'player_needs_comfort',
        response: 'Compassionate presence and validation',
        therapeuticTechnique: 'emotional_validation'
      },
      {
        trigger: 'player_experiences_trauma',
        response: 'Gentle healing and safety building',
        therapeuticTechnique: 'trauma_informed_care'
      }
    ],
    worldAdaptations: {
      fantasy: 'Gentle cleric, nature druid, healing priestess',
      'sci-fi': 'Medical officer, empathic alien, healing AI',
      modern: 'Therapist, nurse, mindfulness teacher'
    }
  },
  {
    archetypeId: 'reformed_antagonist',
    name: 'Reformed Antagonist',
    inspirationSource: 'Characters who have overcome their past and found redemption',
    role: 'Redemption Guide',
    therapeuticFunction: 'Models change and growth, demonstrates that people can overcome their past and make positive changes',
    personality: {
      traits: [
        'reformed',
        'wise_from_experience',
        'honest_about_past',
        'committed_to_change',
        'empathetic',
        'protective',
        'understanding',
        'growth_oriented'
      ],
      communicationStyle: 'Honest about struggles, non-judgmental, change-focused',
      therapeuticApproach: 'Change processes, redemption narratives, moral development'
    },
    adaptationNotes: 'Represents hope for change and redemption - shows that past mistakes don\'t define future potential',
    interactionPatterns: [
      {
        trigger: 'player_feels_guilt',
        response: 'Redemption and forgiveness guidance',
        therapeuticTechnique: 'guilt_processing'
      },
      {
        trigger: 'player_wants_to_change',
        response: 'Change process support and encouragement',
        therapeuticTechnique: 'change_facilitation'
      },
      {
        trigger: 'player_judges_others',
        response: 'Empathy building and perspective taking',
        therapeuticTechnique: 'empathy_development'
      }
    ],
    worldAdaptations: {
      fantasy: 'Reformed dark knight, redeemed sorcerer, changed thief',
      'sci-fi': 'Reformed pirate, changed corporate executive, redeemed soldier',
      modern: 'Reformed addict, changed criminal, redeemed professional'
    }
  }
];

function getAllArchetypes() {
  return CHARACTER_ARCHETYPES;
}

function getArchetypeById(archetypeId) {
  return CHARACTER_ARCHETYPES.find(archetype => archetype.archetypeId === archetypeId);
}

function getArchetypesByRole(role) {
  return CHARACTER_ARCHETYPES.filter(archetype =>
    archetype.role.toLowerCase().includes(role.toLowerCase())
  );
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

    const archetypeId = requestData.archetypeId;
    const role = requestData.role;

    let archetypes;

    if (archetypeId) {
      const archetype = getArchetypeById(archetypeId);
      archetypes = archetype ? [archetype] : [];
    } else if (role) {
      archetypes = getArchetypesByRole(role);
    } else {
      archetypes = getAllArchetypes();
    }

    // Return results
    const response = {
      success: true,
      archetypes: archetypes,
      totalCount: archetypes.length,
      filters: {
        archetypeId: archetypeId || null,
        role: role || null
      }
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
  getAllArchetypes,
  getArchetypeById,
  getArchetypesByRole,
  CHARACTER_ARCHETYPES
};
