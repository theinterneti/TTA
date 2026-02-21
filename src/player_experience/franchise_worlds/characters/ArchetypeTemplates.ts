// Logseq: [[TTA.dev/Player_experience/Franchise_worlds/Characters/Archetypetemplates]]
/**
 * Character Archetype Templates
 *
 * Defines reusable character archetypes that can be adapted across different
 * franchise worlds while maintaining therapeutic value and legal distinctiveness.
 */

import { CharacterArchetype, PersonalityProfile, InteractionPattern } from '../core/FranchiseWorldSystem';

/**
 * Core therapeutic character archetypes that appear across multiple worlds
 */

export const WISE_MENTOR_ARCHETYPE: CharacterArchetype = {
  archetypeId: 'wise_mentor',
  name: 'The Wise Mentor',
  inspirationSource: 'Classic mentor figure from hero\'s journey narratives',
  role: 'Guide, teacher, and emotional support',
  personality: {
    traits: ['patient', 'wise', 'encouraging', 'mysterious', 'supportive'],
    motivations: ['guide others to their potential', 'preserve and share wisdom', 'protect students from harm'],
    fears: ['failing to prepare students adequately', 'loss of important knowledge', 'student making dangerous mistakes'],
    growth_arc: 'Learns to trust in others\' abilities and let them make their own choices',
    therapeutic_modeling: 'Models unconditional positive regard, active listening, and growth mindset'
  },
  therapeuticFunction: 'Provides CBT-style guidance, reframing techniques, and emotional support',
  interactionPatterns: [
    {
      trigger: 'player_expresses_self_doubt',
      response_style: 'Gentle questioning and evidence gathering',
      therapeutic_technique: 'socratic_questioning',
      player_impact: 'Helps identify and challenge cognitive distortions'
    },
    {
      trigger: 'player_faces_overwhelming_challenge',
      response_style: 'Breaking down problems into manageable steps',
      therapeutic_technique: 'problem_solving_skills',
      player_impact: 'Builds confidence through structured approach'
    },
    {
      trigger: 'player_makes_mistake',
      response_style: 'Compassionate reframing as learning opportunity',
      therapeutic_technique: 'growth_mindset_reinforcement',
      player_impact: 'Reduces shame and builds resilience'
    }
  ],
  adaptationNotes: 'Can be adapted as wizard, professor, captain, elder, or other authority figure'
};

export const LOYAL_COMPANION_ARCHETYPE: CharacterArchetype = {
  archetypeId: 'loyal_companion',
  name: 'The Loyal Companion',
  inspirationSource: 'Faithful friend archetype from adventure stories',
  role: 'Peer support, emotional anchor, and practical helper',
  personality: {
    traits: ['loyal', 'optimistic', 'practical', 'brave', 'empathetic'],
    motivations: ['support friends through difficulties', 'maintain group morale', 'provide practical solutions'],
    fears: ['letting friends down', 'being left behind', 'not being useful'],
    growth_arc: 'Develops self-worth independent of others\' approval',
    therapeutic_modeling: 'Models healthy friendship, emotional support, and self-advocacy'
  },
  therapeuticFunction: 'Demonstrates peer support, emotional regulation, and healthy relationships',
  interactionPatterns: [
    {
      trigger: 'player_feels_isolated',
      response_style: 'Warm inclusion and shared activities',
      therapeutic_technique: 'social_connection_building',
      player_impact: 'Reduces loneliness and builds social skills'
    },
    {
      trigger: 'player_experiences_setback',
      response_style: 'Practical help combined with emotional support',
      therapeutic_technique: 'problem_solving_and_emotional_validation',
      player_impact: 'Builds resilience and coping strategies'
    },
    {
      trigger: 'player_needs_encouragement',
      response_style: 'Genuine praise and belief in abilities',
      therapeutic_technique: 'strength_identification_and_reinforcement',
      player_impact: 'Builds self-esteem and confidence'
    }
  ],
  adaptationNotes: 'Can be adapted as best friend, sidekick, crew member, or study partner'
};

export const RELUCTANT_HERO_ARCHETYPE: CharacterArchetype = {
  archetypeId: 'reluctant_hero',
  name: 'The Reluctant Hero',
  inspirationSource: 'Hero who initially resists the call to adventure',
  role: 'Peer model for growth and courage development',
  personality: {
    traits: ['anxious', 'self-doubting', 'ultimately_brave', 'relatable', 'growing'],
    motivations: ['protect loved ones', 'do the right thing despite fear', 'prove self-worth'],
    fears: ['failure', 'inadequacy', 'letting others down', 'facing unknown challenges'],
    growth_arc: 'Overcomes self-doubt to become confident leader',
    therapeutic_modeling: 'Models anxiety management, courage building, and personal growth'
  },
  therapeuticFunction: 'Provides relatable model for overcoming anxiety and building confidence',
  interactionPatterns: [
    {
      trigger: 'facing_new_challenge',
      response_style: 'Initial hesitation followed by determined action',
      therapeutic_technique: 'anxiety_management_and_gradual_exposure',
      player_impact: 'Normalizes anxiety while modeling courage'
    },
    {
      trigger: 'experiencing_failure',
      response_style: 'Processing disappointment then trying again',
      therapeutic_technique: 'resilience_building_and_persistence',
      player_impact: 'Demonstrates healthy response to setbacks'
    },
    {
      trigger: 'receiving_praise',
      response_style: 'Humble acceptance with growing confidence',
      therapeutic_technique: 'self_worth_development',
      player_impact: 'Models healthy self-esteem building'
    }
  ],
  adaptationNotes: 'Can be adapted as student, young warrior, new recruit, or ordinary person in extraordinary circumstances'
};

export const WISE_HEALER_ARCHETYPE: CharacterArchetype = {
  archetypeId: 'wise_healer',
  name: 'The Wise Healer',
  inspirationSource: 'Healing practitioner archetype from various traditions',
  role: 'Therapeutic guide and emotional healer',
  personality: {
    traits: ['compassionate', 'intuitive', 'calm', 'knowledgeable', 'patient'],
    motivations: ['heal suffering', 'teach self-care', 'maintain balance and harmony'],
    fears: ['being unable to help', 'causing harm', 'losing healing abilities'],
    growth_arc: 'Learns to balance helping others with self-care',
    therapeutic_modeling: 'Models self-compassion, mindfulness, and holistic wellness'
  },
  therapeuticFunction: 'Provides mindfulness training, self-care guidance, and emotional healing',
  interactionPatterns: [
    {
      trigger: 'player_shows_emotional_distress',
      response_style: 'Calm presence with gentle healing techniques',
      therapeutic_technique: 'mindfulness_and_emotional_regulation',
      player_impact: 'Learns emotional self-regulation skills'
    },
    {
      trigger: 'player_neglects_self_care',
      response_style: 'Gentle reminder about importance of balance',
      therapeutic_technique: 'self_care_education',
      player_impact: 'Develops healthy self-care habits'
    },
    {
      trigger: 'player_seeks_healing',
      response_style: 'Holistic approach addressing mind, body, and spirit',
      therapeutic_technique: 'integrated_wellness_approach',
      player_impact: 'Learns comprehensive approach to wellbeing'
    }
  ],
  adaptationNotes: 'Can be adapted as medic, counselor, shaman, doctor, or wellness teacher'
};

export const REFORMED_ANTAGONIST_ARCHETYPE: CharacterArchetype = {
  archetypeId: 'reformed_antagonist',
  name: 'The Reformed Antagonist',
  inspirationSource: 'Former enemy who becomes ally through redemption',
  role: 'Model for change, growth, and second chances',
  personality: {
    traits: ['complex', 'remorseful', 'determined_to_change', 'insightful', 'protective'],
    motivations: ['make amends for past actions', 'protect others from making same mistakes', 'find redemption'],
    fears: ['reverting to old patterns', 'not being forgiven', 'causing more harm'],
    growth_arc: 'Transforms from antagonist to trusted ally through consistent positive actions',
    therapeutic_modeling: 'Models accountability, change, and the possibility of redemption'
  },
  therapeuticFunction: 'Demonstrates that people can change and provides hope for personal transformation',
  interactionPatterns: [
    {
      trigger: 'player_makes_poor_choice',
      response_style: 'Understanding without excusing, guidance toward better choices',
      therapeutic_technique: 'accountability_with_compassion',
      player_impact: 'Learns to take responsibility while maintaining self-worth'
    },
    {
      trigger: 'player_doubts_ability_to_change',
      response_style: 'Sharing personal transformation story',
      therapeutic_technique: 'hope_instillation_through_modeling',
      player_impact: 'Builds belief in personal capacity for change'
    },
    {
      trigger: 'player_judges_others_harshly',
      response_style: 'Gentle challenge to consider complexity and potential',
      therapeutic_technique: 'empathy_building_and_perspective_taking',
      player_impact: 'Develops more nuanced understanding of others'
    }
  ],
  adaptationNotes: 'Can be adapted as former bully, ex-villain, recovered addict, or anyone with a redemption arc'
};

/**
 * Archetype Template Manager
 * Provides utilities for working with character archetypes
 */
export class ArchetypeTemplateManager {
  private static archetypes: Map<string, CharacterArchetype> = new Map([
    ['wise_mentor', WISE_MENTOR_ARCHETYPE],
    ['loyal_companion', LOYAL_COMPANION_ARCHETYPE],
    ['reluctant_hero', RELUCTANT_HERO_ARCHETYPE],
    ['wise_healer', WISE_HEALER_ARCHETYPE],
    ['reformed_antagonist', REFORMED_ANTAGONIST_ARCHETYPE]
  ]);

  /**
   * Get all available archetype templates
   */
  static getAllArchetypes(): CharacterArchetype[] {
    return Array.from(this.archetypes.values());
  }

  /**
   * Get specific archetype by ID
   */
  static getArchetype(archetypeId: string): CharacterArchetype | undefined {
    return this.archetypes.get(archetypeId);
  }

  /**
   * Get archetypes suitable for specific therapeutic approaches
   */
  static getArchetypesForTherapeuticApproach(approach: string): CharacterArchetype[] {
    return this.getAllArchetypes().filter(archetype =>
      archetype.interactionPatterns.some(pattern =>
        pattern.therapeutic_technique.includes(approach.toLowerCase())
      )
    );
  }

  /**
   * Adapt archetype for specific world context
   */
  static adaptArchetypeForWorld(
    archetype: CharacterArchetype,
    worldGenre: 'fantasy' | 'sci-fi',
    worldContext: string
  ): CharacterArchetype {
    const adapted = { ...archetype };

    // Customize name and appearance based on world
    if (worldGenre === 'fantasy') {
      adapted.name = this.generateFantasyName(archetype.archetypeId, worldContext);
    } else {
      adapted.name = this.generateSciFiName(archetype.archetypeId, worldContext);
    }

    // Add world-specific adaptation notes
    adapted.adaptationNotes += ` - Adapted for ${worldContext}`;

    return adapted;
  }

  private static generateFantasyName(archetypeId: string, worldContext: string): string {
    const nameMap: Record<string, string> = {
      'wise_mentor': 'Sage Elderwood',
      'loyal_companion': 'Finn Trueheart',
      'reluctant_hero': 'Kira Brightblade',
      'wise_healer': 'Serenity Moonwhisper',
      'reformed_antagonist': 'Thane Shadowmend'
    };
    return nameMap[archetypeId] || 'Unknown Character';
  }

  private static generateSciFiName(archetypeId: string, worldContext: string): string {
    const nameMap: Record<string, string> = {
      'wise_mentor': 'Commander Wisdom',
      'loyal_companion': 'Alex Starfriend',
      'reluctant_hero': 'Jordan Novastrike',
      'wise_healer': 'Dr. Harmony Chen',
      'reformed_antagonist': 'Zara Redemption'
    };
    return nameMap[archetypeId] || 'Unknown Character';
  }
}
