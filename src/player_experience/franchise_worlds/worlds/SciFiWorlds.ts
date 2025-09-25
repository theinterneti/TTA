/**
 * Science Fiction World Configurations
 * 
 * Defines the 5 sci-fi worlds adapted from popular franchises while maintaining
 * legal distinctiveness and therapeutic value.
 */

import { FranchiseWorldConfig, WorldSystemConfig, TherapeuticIntegrationPoint, NarrativeFramework, CharacterArchetype, ScenarioTemplate } from '../core/FranchiseWorldSystem';
import { TherapeuticApproach } from '../types/TTATypes';

// Reuse interfaces from FantasyWorlds
interface TherapeuticValue {
  category: string;
  impact: number;
}

interface TherapeuticMilestone {
  milestoneId: string;
  description: string;
  therapeuticValue: string;
  narrativeContext: string;
}

interface CopyrightCompliance {
  originalElements: number;
  adaptationLevel: string;
  legalReview: string;
  riskAssessment: string;
}

interface ContentRating {
  system: string;
  rating: string;
  descriptors: string[];
}

/**
 * Stellar Confederation - Space Opera Adventure
 * Inspired by Star Trek/Star Wars but legally distinct
 */
export const STELLAR_CONFEDERATION: FranchiseWorldConfig = {
  franchiseId: 'stellar_confederation',
  name: 'Stellar Confederation',
  genre: 'sci-fi',
  inspirationSource: 'Optimistic space exploration with diverse alien cultures and diplomatic challenges',
  
  worldSystems: {
    cultural: {
      complexity: 0.95,
      depth: 0.9,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.8,
      adaptationElements: [
        'Multiple alien species with unique cultures',
        'Universal translator technology',
        'Diplomatic protocols and cultural exchange'
      ],
      originalElements: [
        'Cultural competency training',
        'Bias recognition and reduction',
        'Therapeutic cultural immersion'
      ]
    },
    economic: {
      complexity: 0.8,
      depth: 0.7,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.6,
      adaptationElements: [
        'Post-scarcity resource distribution',
        'Interstellar trade networks',
        'Energy-based economy'
      ],
      originalElements: [
        'Cooperative resource sharing',
        'Value-based exchange systems',
        'Therapeutic work programs'
      ]
    },
    political: {
      complexity: 0.9,
      depth: 0.8,
      interconnectedness: 0.95,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Galactic federation governance',
        'Diplomatic missions and negotiations',
        'Conflict resolution protocols'
      ],
      originalElements: [
        'Consensus-building practices',
        'Therapeutic conflict resolution',
        'Democratic participation models'
      ]
    },
    environmental: {
      complexity: 0.9,
      depth: 0.8,
      interconnectedness: 0.7,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Diverse planetary ecosystems',
        'Terraforming and conservation',
        'Space habitats and stations'
      ],
      originalElements: [
        'Environmental mindfulness',
        'Sustainable living practices',
        'Connection with nature in space'
      ]
    },
    social: {
      complexity: 0.9,
      depth: 0.9,
      interconnectedness: 0.95,
      therapeuticRelevance: 0.9,
      adaptationElements: [
        'Multi-species crew dynamics',
        'Starfleet-style camaraderie',
        'Mentorship and training programs'
      ],
      originalElements: [
        'Therapeutic team building',
        'Social anxiety support in diverse groups',
        'Inclusive community practices'
      ]
    },
    historical: {
      complexity: 0.8,
      depth: 0.8,
      interconnectedness: 0.7,
      therapeuticRelevance: 0.6,
      adaptationElements: [
        'Galactic history and ancient civilizations',
        'First contact protocols and outcomes',
        'Wars and peace treaties'
      ],
      originalElements: [
        'Learning from historical conflicts',
        'Trauma recovery on galactic scale',
        'Building better futures'
      ]
    },
    technological: {
      complexity: 0.95,
      depth: 0.9,
      interconnectedness: 0.8,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Faster-than-light travel',
        'Advanced medical technology',
        'AI and automation systems'
      ],
      originalElements: [
        'Therapeutic technology applications',
        'Human-AI collaboration models',
        'Technology-life balance in space'
      ]
    },
    religious: {
      complexity: 0.7,
      depth: 0.8,
      interconnectedness: 0.6,
      therapeuticRelevance: 0.8,
      adaptationElements: [
        'Diverse spiritual practices across species',
        'Universal ethical principles',
        'Meditation and contemplation traditions'
      ],
      originalElements: [
        'Secular spiritual exploration',
        'Meaning-making in vast universe',
        'Therapeutic ritual practices'
      ]
    }
  },
  
  therapeuticThemes: [
    'cultural_understanding',
    'leadership_development',
    'team_collaboration',
    'ethical_decision_making',
    'overcoming_prejudice',
    'finding_purpose_in_vastness'
  ],
  
  therapeuticApproaches: [
    TherapeuticApproach.CBT,
    TherapeuticApproach.GROUP_THERAPY,
    TherapeuticApproach.SOLUTION_FOCUSED,
    TherapeuticApproach.NARRATIVE_THERAPY
  ],
  
  therapeuticIntegrationPoints: [
    {
      trigger: 'first_contact_situation',
      approach: TherapeuticApproach.CBT,
      technique: 'bias_recognition_and_challenging',
      narrativeIntegration: 'moderate',
      playerAgency: 'high',
      expectedOutcome: 'Develop cultural competency and reduce prejudice'
    },
    {
      trigger: 'crew_conflict_resolution',
      approach: TherapeuticApproach.GROUP_THERAPY,
      technique: 'mediation_and_communication_skills',
      narrativeIntegration: 'subtle',
      playerAgency: 'high',
      expectedOutcome: 'Learn healthy conflict resolution'
    },
    {
      trigger: 'moral_dilemma_decision',
      approach: TherapeuticApproach.NARRATIVE_THERAPY,
      technique: 'values_clarification',
      narrativeIntegration: 'explicit',
      playerAgency: 'high',
      expectedOutcome: 'Strengthen personal ethical framework'
    }
  ],
  
  narrativeFramework: {
    mainArcStructure: 'Exploration and diplomacy with personal growth through challenges',
    branchingPoints: [
      {
        pointId: 'first_contact_approach',
        description: 'How to approach a newly discovered alien species',
        choices: [
          {
            choiceId: 'cautious_observation',
            text: 'Observe from distance and gather information first',
            therapeuticValue: { category: 'anxiety_management', impact: 0.7 },
            consequences: ['Safer approach', 'Missed immediate connection opportunity'],
            characterDevelopment: 'Develops patience and careful assessment skills'
          },
          {
            choiceId: 'direct_peaceful_contact',
            text: 'Initiate direct but peaceful communication',
            therapeuticValue: { category: 'social_courage', impact: 0.8 },
            consequences: ['Immediate relationship building', 'Higher risk of misunderstanding'],
            characterDevelopment: 'Builds confidence in social situations'
          }
        ],
        therapeuticImpact: 'Explores approach to new social situations and anxiety management',
        convergenceStrategy: 'Both approaches lead to eventual contact with different relationship dynamics'
      }
    ],
    therapeuticMilestones: [
      {
        milestoneId: 'cultural_bridge_building',
        description: 'Successfully mediate between conflicting cultures',
        therapeuticValue: 'Builds empathy and communication skills',
        narrativeContext: 'Helping two alien species understand each other\'s perspectives'
      }
    ],
    adaptationStrategy: 'Transform space exploration into therapeutic journey of understanding and growth'
  },
  
  characterArchetypes: [
    {
      archetypeId: 'diplomatic_captain',
      name: 'Captain Harmony',
      inspirationSource: 'Diplomatic leader archetype from space opera',
      role: 'Ship captain and diplomatic leader',
      personality: {
        traits: ['diplomatic', 'decisive', 'empathetic', 'principled'],
        motivations: ['peaceful exploration', 'crew safety and growth', 'galactic harmony'],
        fears: ['making wrong decisions', 'crew member loss', 'diplomatic failures'],
        growth_arc: 'Learns to balance leadership with vulnerability',
        therapeutic_modeling: 'Models healthy leadership and emotional regulation'
      },
      therapeuticFunction: 'Demonstrates leadership skills and ethical decision-making',
      interactionPatterns: [
        {
          trigger: 'crew_member_uncertainty',
          response_style: 'Supportive guidance with clear expectations',
          therapeutic_technique: 'confidence_building_through_responsibility',
          player_impact: 'Builds leadership skills and self-efficacy'
        }
      ],
      adaptationNotes: 'Original character inspired by diplomatic captain archetypes'
    }
  ],
  
  scenarioTemplates: [
    {
      templateId: 'diplomatic_crisis',
      name: 'The Interstellar Diplomatic Crisis',
      description: 'Navigate a complex diplomatic situation between conflicting alien cultures',
      duration: 'long',
      therapeuticFocus: ['communication_skills', 'cultural_competency', 'conflict_resolution'],
      narrativeElements: ['cultural_research', 'stakeholder_meetings', 'negotiation_sessions', 'resolution_ceremony'],
      adaptationSource: 'Classic space diplomacy scenario',
      variationPoints: [
        {
          pointId: 'conflict_source',
          description: 'Root cause of the diplomatic crisis',
          options: ['resource_dispute', 'cultural_misunderstanding', 'historical_grievance', 'technological_fear'],
          therapeuticImpact: 'Different conflicts allow exploration of different communication challenges'
        }
      ]
    }
  ],
  
  sessionLengthSupport: {
    short: {
      targetDuration: 25,
      narrativeStructure: 'Single diplomatic encounter or exploration',
      therapeuticIntensity: 0.6,
      keyElements: ['cultural_learning', 'team_interaction', 'ethical_choice'],
      exitStrategies: ['successful_contact', 'mission_briefing', 'crew_reflection']
    },
    medium: {
      targetDuration: 75,
      narrativeStructure: 'Complete diplomatic mission or exploration',
      therapeuticIntensity: 0.7,
      keyElements: ['complex_negotiation', 'team_building', 'personal_growth'],
      exitStrategies: ['treaty_signing', 'successful_mission', 'crew_celebration']
    },
    long: {
      targetDuration: 150,
      narrativeStructure: 'Major galactic event or extended exploration',
      therapeuticIntensity: 0.8,
      keyElements: ['leadership_development', 'major_decisions', 'relationship_building'],
      exitStrategies: ['galactic_peace', 'major_discovery', 'personal_transformation']
    }
  },
  
  copyrightCompliance: {
    originalElements: 0.75,
    adaptationLevel: 'high',
    legalReview: 'pending',
    riskAssessment: 'low'
  },
  
  contentRatings: [
    { system: 'ESRB', rating: 'T', descriptors: ['Sci-Fi Violence', 'Mild Language'] },
    { system: 'PEGI', rating: '12', descriptors: ['Violence'] }
  ]
};

/**
 * Neon Metropolis - Cyberpunk Urban Adventure
 * Inspired by Cyberpunk 2077/Blade Runner but legally distinct
 */
export const NEON_METROPOLIS: FranchiseWorldConfig = {
  franchiseId: 'neon_metropolis',
  name: 'Neon Metropolis',
  genre: 'sci-fi',
  inspirationSource: 'Cyberpunk urban environment with focus on identity, technology, and social justice',

  worldSystems: {
    cultural: {
      complexity: 0.9,
      depth: 0.8,
      interconnectedness: 0.8,
      therapeuticRelevance: 0.8,
      adaptationElements: [
        'Diverse urban subcultures and communities',
        'Corporate culture vs street culture',
        'Digital identity and virtual communities'
      ],
      originalElements: [
        'Identity exploration in digital age',
        'Cultural authenticity vs adaptation',
        'Therapeutic community building'
      ]
    },
    economic: {
      complexity: 0.9,
      depth: 0.9,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Corporate megacorp dominance',
        'Underground economy and black markets',
        'Digital currency and virtual assets'
      ],
      originalElements: [
        'Economic justice and fairness',
        'Value of human dignity over profit',
        'Cooperative economic alternatives'
      ]
    },
    political: {
      complexity: 0.8,
      depth: 0.8,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Corporate political control',
        'Underground resistance movements',
        'Digital surveillance and privacy'
      ],
      originalElements: [
        'Grassroots organizing and activism',
        'Digital privacy and personal boundaries',
        'Peaceful resistance and change'
      ]
    },
    environmental: {
      complexity: 0.7,
      depth: 0.8,
      interconnectedness: 0.7,
      therapeuticRelevance: 0.6,
      adaptationElements: [
        'Urban decay and environmental damage',
        'Vertical city architecture',
        'Climate control and artificial environments'
      ],
      originalElements: [
        'Environmental healing and restoration',
        'Connection with nature in urban settings',
        'Sustainable living practices'
      ]
    },
    social: {
      complexity: 0.9,
      depth: 0.9,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.9,
      adaptationElements: [
        'Social stratification and inequality',
        'Digital social networks and isolation',
        'Gang culture and street families'
      ],
      originalElements: [
        'Building authentic connections',
        'Social justice and equality advocacy',
        'Healthy relationship formation'
      ]
    },
    historical: {
      complexity: 0.7,
      depth: 0.7,
      interconnectedness: 0.6,
      therapeuticRelevance: 0.6,
      adaptationElements: [
        'Corporate wars and their aftermath',
        'Technological revolution consequences',
        'Social movement histories'
      ],
      originalElements: [
        'Learning from technological mistakes',
        'Healing from systemic trauma',
        'Building better futures'
      ]
    },
    technological: {
      complexity: 0.95,
      depth: 0.9,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.8,
      adaptationElements: [
        'Advanced cybernetic implants',
        'Virtual reality and augmented reality',
        'AI and neural interfaces'
      ],
      originalElements: [
        'Healthy technology relationships',
        'Digital wellness and boundaries',
        'Human-AI collaboration ethics'
      ]
    },
    religious: {
      complexity: 0.6,
      depth: 0.7,
      interconnectedness: 0.6,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Digital spirituality and virtual temples',
        'Corporate-sponsored religions',
        'Underground spiritual movements'
      ],
      originalElements: [
        'Authentic spiritual exploration',
        'Meaning-making in technological age',
        'Community-based spiritual practices'
      ]
    }
  },

  therapeuticThemes: [
    'identity_in_digital_age',
    'social_justice_and_activism',
    'technology_life_balance',
    'authentic_relationships',
    'overcoming_systemic_oppression',
    'finding_purpose_in_urban_environment'
  ],

  therapeuticApproaches: [
    TherapeuticApproach.NARRATIVE_THERAPY,
    TherapeuticApproach.CBT,
    TherapeuticApproach.GROUP_THERAPY,
    TherapeuticApproach.SOLUTION_FOCUSED
  ],

  therapeuticIntegrationPoints: [
    {
      trigger: 'identity_crisis_moment',
      approach: TherapeuticApproach.NARRATIVE_THERAPY,
      technique: 'identity_exploration_and_values_clarification',
      narrativeIntegration: 'moderate',
      playerAgency: 'high',
      expectedOutcome: 'Develop authentic sense of self in complex world'
    },
    {
      trigger: 'social_justice_opportunity',
      approach: TherapeuticApproach.SOLUTION_FOCUSED,
      technique: 'goal_setting_and_action_planning',
      narrativeIntegration: 'explicit',
      playerAgency: 'high',
      expectedOutcome: 'Build sense of agency and purpose through activism'
    }
  ],

  narrativeFramework: {
    mainArcStructure: 'Urban survival and identity discovery with social justice themes',
    branchingPoints: [
      {
        pointId: 'corporate_vs_street',
        description: 'Choose between corporate advancement or street authenticity',
        choices: [
          {
            choiceId: 'corporate_path',
            text: 'Accept corporate job offer for security and advancement',
            therapeuticValue: { category: 'security_vs_authenticity', impact: 0.7 },
            consequences: ['Financial security', 'Potential loss of authentic identity'],
            characterDevelopment: 'Explores compromise and adaptation strategies'
          },
          {
            choiceId: 'street_path',
            text: 'Stay true to street values and community',
            therapeuticValue: { category: 'authenticity_and_community', impact: 0.8 },
            consequences: ['Authentic relationships', 'Economic challenges'],
            characterDevelopment: 'Develops strong sense of identity and values'
          }
        ],
        therapeuticImpact: 'Explores identity formation and values-based decision making',
        convergenceStrategy: 'Both paths offer opportunities for growth with different challenges'
      }
    ],
    therapeuticMilestones: [
      {
        milestoneId: 'authentic_identity_moment',
        description: 'Discover and express authentic self despite external pressures',
        therapeuticValue: 'Builds self-awareness and confidence in identity',
        narrativeContext: 'Standing up for personal values in face of corporate pressure'
      }
    ],
    adaptationStrategy: 'Transform cyberpunk themes into therapeutic exploration of identity and purpose'
  },

  characterArchetypes: [
    {
      archetypeId: 'street_mentor',
      name: 'Sage Neon',
      inspirationSource: 'Street-wise mentor from cyberpunk narratives',
      role: 'Urban guide and identity mentor',
      personality: {
        traits: ['street_smart', 'authentic', 'protective', 'insightful'],
        motivations: ['protect community', 'preserve authentic culture', 'guide youth'],
        fears: ['corporate takeover', 'loss of community', 'cultural erasure'],
        growth_arc: 'Learns to balance tradition with necessary change',
        therapeutic_modeling: 'Models authentic identity and community connection'
      },
      therapeuticFunction: 'Provides guidance on identity formation and community building',
      interactionPatterns: [
        {
          trigger: 'identity_confusion',
          response_style: 'Direct but supportive reality check with values exploration',
          therapeutic_technique: 'identity_clarification_and_grounding',
          player_impact: 'Develops stronger sense of authentic self'
        }
      ],
      adaptationNotes: 'Original character inspired by cyberpunk mentor archetypes'
    }
  ],

  scenarioTemplates: [
    {
      templateId: 'corporate_infiltration',
      name: 'The Corporate Heist',
      description: 'Infiltrate megacorp to expose corruption while maintaining personal integrity',
      duration: 'long',
      therapeuticFocus: ['identity_integrity', 'social_justice', 'ethical_decision_making'],
      narrativeElements: ['planning', 'infiltration', 'moral_choices', 'community_impact'],
      adaptationSource: 'Classic cyberpunk heist scenario',
      variationPoints: [
        {
          pointId: 'infiltration_method',
          description: 'How to approach the corporate infiltration',
          options: ['social_engineering', 'technical_hacking', 'inside_ally', 'direct_confrontation'],
          therapeuticImpact: 'Different approaches explore different problem-solving styles'
        }
      ]
    }
  ],

  sessionLengthSupport: {
    short: {
      targetDuration: 25,
      narrativeStructure: 'Single urban encounter or identity moment',
      therapeuticIntensity: 0.7,
      keyElements: ['identity_exploration', 'community_connection', 'ethical_choice'],
      exitStrategies: ['safe_house_return', 'identity_insight', 'community_support']
    },
    medium: {
      targetDuration: 75,
      narrativeStructure: 'Complete urban mission or identity arc',
      therapeuticIntensity: 0.8,
      keyElements: ['complex_planning', 'relationship_building', 'values_clarification'],
      exitStrategies: ['mission_success', 'identity_breakthrough', 'community_celebration']
    },
    long: {
      targetDuration: 150,
      narrativeStructure: 'Major corporate campaign or community transformation',
      therapeuticIntensity: 0.9,
      keyElements: ['identity_mastery', 'social_change', 'community_leadership'],
      exitStrategies: ['corporate_defeat', 'community_transformation', 'identity_integration']
    }
  },

  copyrightCompliance: {
    originalElements: 0.8,
    adaptationLevel: 'high',
    legalReview: 'pending',
    riskAssessment: 'low'
  },

  contentRatings: [
    { system: 'ESRB', rating: 'M', descriptors: ['Violence', 'Strong Language', 'Suggestive Themes'] },
    { system: 'PEGI', rating: '16', descriptors: ['Violence', 'Strong Language'] }
  ]
};
