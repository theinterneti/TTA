/**
 * Fantasy World Configurations
 * 
 * Defines the 5 fantasy worlds adapted from popular franchises while maintaining
 * legal distinctiveness and therapeutic value.
 */

import { FranchiseWorldConfig, WorldSystemConfig, TherapeuticIntegrationPoint, NarrativeFramework, CharacterArchetype, ScenarioTemplate } from '../core/FranchiseWorldSystem';
import { TherapeuticApproach } from '../types/TTATypes';

// Missing interfaces that need to be defined
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
 * Eldermere Realms - Epic Fantasy Adventure
 * Inspired by Middle-earth but legally distinct
 */
export const ELDERMERE_REALMS: FranchiseWorldConfig = {
  franchiseId: 'eldermere_realms',
  name: 'Eldermere Realms',
  genre: 'fantasy',
  inspirationSource: 'Epic fantasy with diverse cultures and ancient mysteries',
  
  worldSystems: {
    cultural: {
      complexity: 0.9,
      depth: 0.95,
      interconnectedness: 0.8,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Multiple distinct cultures with rich traditions',
        'Ancient languages and lore systems',
        'Cultural exchange and diplomacy mechanics'
      ],
      originalElements: [
        'Therapeutic cultural healing practices',
        'Mindfulness-based meditation traditions',
        'Community support networks'
      ]
    },
    economic: {
      complexity: 0.7,
      depth: 0.6,
      interconnectedness: 0.8,
      therapeuticRelevance: 0.5,
      adaptationElements: [
        'Guild-based trade systems',
        'Resource scarcity and abundance cycles',
        'Barter and currency systems'
      ],
      originalElements: [
        'Cooperative economic models',
        'Therapeutic work programs',
        'Value-based exchange systems'
      ]
    },
    political: {
      complexity: 0.8,
      depth: 0.7,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.6,
      adaptationElements: [
        'Council-based governance',
        'Alliance and conflict dynamics',
        'Leadership succession systems'
      ],
      originalElements: [
        'Consensus-building practices',
        'Conflict resolution mechanisms',
        'Therapeutic leadership models'
      ]
    },
    environmental: {
      complexity: 0.9,
      depth: 0.8,
      interconnectedness: 0.7,
      therapeuticRelevance: 0.8,
      adaptationElements: [
        'Diverse biomes and ecosystems',
        'Magical environmental interactions',
        'Seasonal and weather patterns'
      ],
      originalElements: [
        'Nature-based healing environments',
        'Therapeutic garden spaces',
        'Mindful environmental interaction'
      ]
    },
    social: {
      complexity: 0.8,
      depth: 0.9,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.9,
      adaptationElements: [
        'Fellowship and companionship bonds',
        'Mentorship relationships',
        'Community celebration traditions'
      ],
      originalElements: [
        'Therapeutic support groups',
        'Peer counseling networks',
        'Social anxiety support systems'
      ]
    },
    historical: {
      complexity: 0.8,
      depth: 0.9,
      interconnectedness: 0.6,
      therapeuticRelevance: 0.6,
      adaptationElements: [
        'Ancient wars and their consequences',
        'Lost civilizations and artifacts',
        'Cyclical historical patterns'
      ],
      originalElements: [
        'Trauma recovery narratives',
        'Healing from historical wounds',
        'Learning from past mistakes'
      ]
    },
    technological: {
      complexity: 0.4,
      depth: 0.5,
      interconnectedness: 0.5,
      therapeuticRelevance: 0.4,
      adaptationElements: [
        'Magical technology integration',
        'Crafting and smithing traditions',
        'Communication networks'
      ],
      originalElements: [
        'Therapeutic tool creation',
        'Mindful crafting practices',
        'Technology-life balance'
      ]
    },
    religious: {
      complexity: 0.7,
      depth: 0.8,
      interconnectedness: 0.7,
      therapeuticRelevance: 0.8,
      adaptationElements: [
        'Multiple pantheons and belief systems',
        'Spiritual quests and pilgrimages',
        'Divine intervention mechanics'
      ],
      originalElements: [
        'Secular spiritual practices',
        'Meaning-making frameworks',
        'Therapeutic ritual systems'
      ]
    }
  },
  
  therapeuticThemes: [
    'courage_and_resilience',
    'friendship_and_belonging',
    'overcoming_adversity',
    'finding_purpose',
    'healing_from_trauma',
    'building_confidence'
  ],
  
  therapeuticApproaches: [
    TherapeuticApproach.CBT,
    TherapeuticApproach.NARRATIVE_THERAPY,
    TherapeuticApproach.MINDFULNESS,
    TherapeuticApproach.GROUP_THERAPY
  ],
  
  therapeuticIntegrationPoints: [
    {
      trigger: 'facing_overwhelming_challenge',
      approach: TherapeuticApproach.CBT,
      technique: 'cognitive_restructuring',
      narrativeIntegration: 'subtle',
      playerAgency: 'high',
      expectedOutcome: 'Reframe negative thoughts about capabilities'
    },
    {
      trigger: 'fellowship_formation',
      approach: TherapeuticApproach.GROUP_THERAPY,
      technique: 'peer_support_modeling',
      narrativeIntegration: 'moderate',
      playerAgency: 'medium',
      expectedOutcome: 'Experience healthy relationship dynamics'
    },
    {
      trigger: 'ancient_wisdom_discovery',
      approach: TherapeuticApproach.MINDFULNESS,
      technique: 'present_moment_awareness',
      narrativeIntegration: 'subtle',
      playerAgency: 'high',
      expectedOutcome: 'Develop mindfulness skills through exploration'
    }
  ],
  
  narrativeFramework: {
    mainArcStructure: 'Hero\'s Journey with Fellowship Support',
    branchingPoints: [
      {
        pointId: 'fellowship_choice',
        description: 'Choose companions for the journey',
        choices: [
          {
            choiceId: 'diverse_fellowship',
            text: 'Gather companions from different cultures',
            therapeuticValue: { category: 'social_skills', impact: 0.8 },
            consequences: ['Enhanced cultural understanding', 'Diverse problem-solving approaches'],
            characterDevelopment: 'Develops appreciation for diversity and collaboration'
          },
          {
            choiceId: 'solo_journey',
            text: 'Undertake the quest alone',
            therapeuticValue: { category: 'self_reliance', impact: 0.6 },
            consequences: ['Greater personal challenge', 'Missed social learning opportunities'],
            characterDevelopment: 'Builds self-reliance but may reinforce isolation'
          }
        ],
        therapeuticImpact: 'Explores relationship patterns and social anxiety',
        convergenceStrategy: 'Both paths lead to the same destination but with different support systems'
      }
    ],
    therapeuticMilestones: [
      {
        milestoneId: 'courage_awakening',
        description: 'First act of courage despite fear',
        therapeuticValue: 'Builds confidence and self-efficacy',
        narrativeContext: 'Standing up to a bully or defending someone vulnerable'
      }
    ],
    adaptationStrategy: 'Transform classic quest narrative into therapeutic journey of personal growth'
  },
  
  characterArchetypes: [
    {
      archetypeId: 'wise_mentor',
      name: 'Sage Elderwood',
      inspirationSource: 'Wise mentor archetype from fantasy literature',
      role: 'Guide and teacher',
      personality: {
        traits: ['patient', 'wise', 'encouraging', 'mysterious'],
        motivations: ['guide others to their potential', 'preserve ancient wisdom'],
        fears: ['failing to prepare students', 'loss of knowledge'],
        growth_arc: 'Learns to trust in others\' abilities',
        therapeutic_modeling: 'Models healthy mentorship and unconditional positive regard'
      },
      therapeuticFunction: 'Provides CBT-style guidance and reframing techniques',
      interactionPatterns: [
        {
          trigger: 'player_expresses_self_doubt',
          response_style: 'Gentle questioning and evidence gathering',
          therapeutic_technique: 'Socratic questioning',
          player_impact: 'Helps identify cognitive distortions'
        }
      ],
      adaptationNotes: 'Original character inspired by but legally distinct from Gandalf-type mentors'
    }
  ],
  
  scenarioTemplates: [
    {
      templateId: 'village_crisis',
      name: 'The Threatened Village',
      description: 'A peaceful village faces an external threat, requiring courage and community cooperation',
      duration: 'medium',
      therapeuticFocus: ['anxiety_management', 'social_cooperation', 'problem_solving'],
      narrativeElements: ['community_meeting', 'resource_gathering', 'defensive_planning', 'confrontation'],
      adaptationSource: 'Classic fantasy village defense scenario',
      variationPoints: [
        {
          pointId: 'threat_type',
          description: 'Nature of the threat facing the village',
          options: ['bandits', 'magical_creature', 'natural_disaster', 'political_pressure'],
          therapeuticImpact: 'Different threats allow exploration of different anxiety types'
        }
      ]
    }
  ],
  
  sessionLengthSupport: {
    short: {
      targetDuration: 20,
      narrativeStructure: 'Single encounter or discovery',
      therapeuticIntensity: 0.6,
      keyElements: ['character_interaction', 'small_challenge', 'therapeutic_insight'],
      exitStrategies: ['natural_rest_point', 'mentor_guidance', 'safe_haven_arrival']
    },
    medium: {
      targetDuration: 60,
      narrativeStructure: 'Complete mini-quest or significant story beat',
      therapeuticIntensity: 0.7,
      keyElements: ['fellowship_building', 'moderate_challenge', 'skill_development', 'therapeutic_breakthrough'],
      exitStrategies: ['quest_completion', 'fellowship_celebration', 'wisdom_gained']
    },
    long: {
      targetDuration: 120,
      narrativeStructure: 'Major story arc with multiple challenges',
      therapeuticIntensity: 0.8,
      keyElements: ['character_growth', 'major_challenges', 'relationship_development', 'therapeutic_integration'],
      exitStrategies: ['epic_achievement', 'major_revelation', 'transformation_moment']
    }
  },
  
  copyrightCompliance: {
    originalElements: 0.7,
    adaptationLevel: 'high',
    legalReview: 'pending',
    riskAssessment: 'low'
  },
  
  contentRatings: [
    { system: 'ESRB', rating: 'T', descriptors: ['Fantasy Violence', 'Mild Language'] },
    { system: 'PEGI', rating: '12', descriptors: ['Violence'] }
  ]
};

/**
 * Arcanum Academy - Magical School Adventure
 * Inspired by magical school settings but legally distinct
 */
export const ARCANUM_ACADEMY: FranchiseWorldConfig = {
  franchiseId: 'arcanum_academy',
  name: 'Arcanum Academy',
  genre: 'fantasy',
  inspirationSource: 'Magical academy with focus on learning, friendship, and personal growth',

  worldSystems: {
    cultural: {
      complexity: 0.7,
      depth: 0.8,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.9,
      adaptationElements: [
        'House system fostering belonging',
        'Academic traditions and ceremonies',
        'Diverse student backgrounds and cultures'
      ],
      originalElements: [
        'Therapeutic peer support groups',
        'Mindfulness-based study practices',
        'Inclusive community building'
      ]
    },
    economic: {
      complexity: 0.4,
      depth: 0.5,
      interconnectedness: 0.6,
      therapeuticRelevance: 0.4,
      adaptationElements: [
        'Merit-based advancement system',
        'Resource sharing among students',
        'Academic achievement rewards'
      ],
      originalElements: [
        'Cooperative learning economics',
        'Value of effort over outcome',
        'Therapeutic work-study programs'
      ]
    },
    political: {
      complexity: 0.6,
      depth: 0.7,
      interconnectedness: 0.8,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Student council governance',
        'Faculty-student relationships',
        'Inter-house competition and cooperation'
      ],
      originalElements: [
        'Restorative justice practices',
        'Conflict mediation systems',
        'Democratic decision-making'
      ]
    },
    environmental: {
      complexity: 0.8,
      depth: 0.7,
      interconnectedness: 0.6,
      therapeuticRelevance: 0.8,
      adaptationElements: [
        'Magical castle with shifting architecture',
        'Enchanted grounds and gardens',
        'Seasonal magical phenomena'
      ],
      originalElements: [
        'Therapeutic healing gardens',
        'Quiet contemplation spaces',
        'Nature-based learning environments'
      ]
    },
    social: {
      complexity: 0.9,
      depth: 0.9,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.95,
      adaptationElements: [
        'Dormitory life and friendships',
        'Study groups and academic partnerships',
        'Extracurricular clubs and activities'
      ],
      originalElements: [
        'Social anxiety support networks',
        'Peer mentoring programs',
        'Therapeutic group activities'
      ]
    },
    historical: {
      complexity: 0.6,
      depth: 0.7,
      interconnectedness: 0.5,
      therapeuticRelevance: 0.5,
      adaptationElements: [
        'Academy founding legends',
        'Famous alumni achievements',
        'Historical magical discoveries'
      ],
      originalElements: [
        'Learning from past mistakes',
        'Growth through challenges',
        'Legacy of healing and helping'
      ]
    },
    technological: {
      complexity: 0.7,
      depth: 0.6,
      interconnectedness: 0.7,
      therapeuticRelevance: 0.6,
      adaptationElements: [
        'Magical tools and instruments',
        'Enchanted learning aids',
        'Communication systems'
      ],
      originalElements: [
        'Therapeutic technology integration',
        'Mindful use of magical tools',
        'Balance between magic and mundane'
      ]
    },
    religious: {
      complexity: 0.5,
      depth: 0.6,
      interconnectedness: 0.6,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Diverse spiritual practices',
        'Meditation and reflection traditions',
        'Ethical magical use principles'
      ],
      originalElements: [
        'Secular mindfulness practices',
        'Ethical decision-making frameworks',
        'Purpose and meaning exploration'
      ]
    }
  },

  therapeuticThemes: [
    'academic_anxiety',
    'social_belonging',
    'self_discovery',
    'friendship_building',
    'overcoming_learning_challenges',
    'building_confidence'
  ],

  therapeuticApproaches: [
    TherapeuticApproach.CBT,
    TherapeuticApproach.GROUP_THERAPY,
    TherapeuticApproach.MINDFULNESS,
    TherapeuticApproach.SOLUTION_FOCUSED
  ],

  therapeuticIntegrationPoints: [
    {
      trigger: 'academic_failure_or_struggle',
      approach: TherapeuticApproach.CBT,
      technique: 'growth_mindset_development',
      narrativeIntegration: 'moderate',
      playerAgency: 'high',
      expectedOutcome: 'Reframe failure as learning opportunity'
    },
    {
      trigger: 'social_isolation_or_bullying',
      approach: TherapeuticApproach.GROUP_THERAPY,
      technique: 'peer_support_activation',
      narrativeIntegration: 'moderate',
      playerAgency: 'medium',
      expectedOutcome: 'Experience healthy peer relationships'
    }
  ],

  narrativeFramework: {
    mainArcStructure: 'Coming-of-age through academic and social challenges',
    branchingPoints: [
      {
        pointId: 'house_selection',
        description: 'Choose which house/group to join',
        choices: [
          {
            choiceId: 'courage_house',
            text: 'Join the house known for bravery',
            therapeuticValue: { category: 'confidence_building', impact: 0.8 },
            consequences: ['Face fears directly', 'Build courage through challenges'],
            characterDevelopment: 'Develops courage and assertiveness'
          },
          {
            choiceId: 'wisdom_house',
            text: 'Join the house known for learning',
            therapeuticValue: { category: 'intellectual_growth', impact: 0.7 },
            consequences: ['Deep academic exploration', 'Analytical problem-solving'],
            characterDevelopment: 'Develops critical thinking and patience'
          }
        ],
        therapeuticImpact: 'Explores identity formation and belonging needs',
        convergenceStrategy: 'All houses face similar core challenges with different approaches'
      }
    ],
    therapeuticMilestones: [
      {
        milestoneId: 'first_friend',
        description: 'Form first meaningful friendship at academy',
        therapeuticValue: 'Builds social confidence and trust',
        narrativeContext: 'Overcoming initial shyness to connect with a peer'
      }
    ],
    adaptationStrategy: 'Transform magical school tropes into therapeutic growth experiences'
  },

  characterArchetypes: [
    {
      archetypeId: 'supportive_professor',
      name: 'Professor Mindwell',
      inspirationSource: 'Caring teacher archetype from school stories',
      role: 'Academic mentor and emotional support',
      personality: {
        traits: ['patient', 'encouraging', 'insightful', 'approachable'],
        motivations: ['help students reach potential', 'create safe learning environment'],
        fears: ['student failure', 'not being available when needed'],
        growth_arc: 'Learns to balance support with independence building',
        therapeutic_modeling: 'Models unconditional positive regard and growth mindset'
      },
      therapeuticFunction: 'Provides academic anxiety support and confidence building',
      interactionPatterns: [
        {
          trigger: 'student_academic_anxiety',
          response_style: 'Calm reassurance with practical strategies',
          therapeutic_technique: 'anxiety_management_techniques',
          player_impact: 'Reduces academic stress and builds coping skills'
        }
      ],
      adaptationNotes: 'Original character inspired by supportive teacher archetypes'
    }
  ],

  scenarioTemplates: [
    {
      templateId: 'first_exam',
      name: 'The Challenging Examination',
      description: 'Face your first major academic test with anxiety and preparation challenges',
      duration: 'short',
      therapeuticFocus: ['test_anxiety', 'preparation_strategies', 'self_efficacy'],
      narrativeElements: ['study_preparation', 'peer_support', 'exam_experience', 'result_processing'],
      adaptationSource: 'Classic school examination scenario',
      variationPoints: [
        {
          pointId: 'preparation_approach',
          description: 'How to prepare for the challenging exam',
          options: ['solo_intensive_study', 'group_study_session', 'balanced_approach', 'seek_help_early'],
          therapeuticImpact: 'Explores different coping strategies for academic pressure'
        }
      ]
    }
  ],

  sessionLengthSupport: {
    short: {
      targetDuration: 15,
      narrativeStructure: 'Single class or social interaction',
      therapeuticIntensity: 0.5,
      keyElements: ['peer_interaction', 'learning_moment', 'confidence_building'],
      exitStrategies: ['class_completion', 'friendship_moment', 'small_achievement']
    },
    medium: {
      targetDuration: 45,
      narrativeStructure: 'Full day of academy life with multiple interactions',
      therapeuticIntensity: 0.7,
      keyElements: ['academic_challenge', 'social_navigation', 'personal_growth'],
      exitStrategies: ['day_reflection', 'meaningful_conversation', 'skill_mastery']
    },
    long: {
      targetDuration: 90,
      narrativeStructure: 'Major academy event or extended challenge',
      therapeuticIntensity: 0.8,
      keyElements: ['significant_growth', 'relationship_development', 'major_achievement'],
      exitStrategies: ['celebration', 'major_breakthrough', 'semester_completion']
    }
  },

  copyrightCompliance: {
    originalElements: 0.8,
    adaptationLevel: 'high',
    legalReview: 'pending',
    riskAssessment: 'low'
  },

  contentRatings: [
    { system: 'ESRB', rating: 'E10+', descriptors: ['Mild Fantasy Violence'] },
    { system: 'PEGI', rating: '7', descriptors: ['Mild Violence'] }
  ]
};

/**
 * Crown's Gambit - Political Intrigue Fantasy
 * Inspired by Game of Thrones but legally distinct
 */
export const CROWNS_GAMBIT: FranchiseWorldConfig = {
  franchiseId: 'crowns_gambit',
  name: 'Crown\'s Gambit',
  genre: 'fantasy',
  inspirationSource: 'Political intrigue fantasy with focus on leadership, ethics, and social dynamics',

  worldSystems: {
    cultural: {
      complexity: 0.8,
      depth: 0.9,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Multiple noble houses with distinct cultures',
        'Court traditions and ceremonial practices',
        'Regional customs and dialects'
      ],
      originalElements: [
        'Therapeutic conflict resolution traditions',
        'Mindful leadership practices',
        'Cultural empathy building exercises'
      ]
    },
    economic: {
      complexity: 0.9,
      depth: 0.8,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.6,
      adaptationElements: [
        'Complex trade networks between regions',
        'Resource management and taxation',
        'Economic warfare and sanctions'
      ],
      originalElements: [
        'Cooperative economic models',
        'Ethical business practices',
        'Sustainable resource management'
      ]
    },
    political: {
      complexity: 0.95,
      depth: 0.9,
      interconnectedness: 0.95,
      therapeuticRelevance: 0.8,
      adaptationElements: [
        'Complex alliance systems',
        'Court intrigue and diplomacy',
        'Power struggles and succession'
      ],
      originalElements: [
        'Ethical leadership development',
        'Conflict mediation skills',
        'Democratic decision-making processes'
      ]
    },
    environmental: {
      complexity: 0.7,
      depth: 0.6,
      interconnectedness: 0.6,
      therapeuticRelevance: 0.5,
      adaptationElements: [
        'Diverse kingdoms with unique climates',
        'Strategic geographical features',
        'Resource distribution affecting politics'
      ],
      originalElements: [
        'Environmental stewardship themes',
        'Sustainable development practices',
        'Connection between environment and wellbeing'
      ]
    },
    social: {
      complexity: 0.9,
      depth: 0.95,
      interconnectedness: 0.9,
      therapeuticRelevance: 0.9,
      adaptationElements: [
        'Complex social hierarchies',
        'Court social dynamics',
        'Inter-house relationships'
      ],
      originalElements: [
        'Social anxiety management in formal settings',
        'Healthy boundary setting',
        'Assertiveness training through roleplay'
      ]
    },
    historical: {
      complexity: 0.8,
      depth: 0.9,
      interconnectedness: 0.7,
      therapeuticRelevance: 0.6,
      adaptationElements: [
        'Ancient conflicts and their consequences',
        'Dynastic histories and bloodlines',
        'Historical precedents for current events'
      ],
      originalElements: [
        'Learning from historical mistakes',
        'Breaking cycles of conflict',
        'Healing generational trauma'
      ]
    },
    technological: {
      complexity: 0.5,
      depth: 0.6,
      interconnectedness: 0.6,
      therapeuticRelevance: 0.4,
      adaptationElements: [
        'Medieval technology with strategic applications',
        'Communication networks (ravens, riders)',
        'Siege warfare and defensive technologies'
      ],
      originalElements: [
        'Ethical use of power and technology',
        'Communication skills development',
        'Strategic thinking for personal goals'
      ]
    },
    religious: {
      complexity: 0.7,
      depth: 0.8,
      interconnectedness: 0.7,
      therapeuticRelevance: 0.7,
      adaptationElements: [
        'Multiple competing faiths',
        'Religious influence on politics',
        'Spiritual guidance and prophecy'
      ],
      originalElements: [
        'Secular meaning-making frameworks',
        'Ethical decision-making systems',
        'Purpose and values clarification'
      ]
    }
  },

  therapeuticThemes: [
    'leadership_development',
    'ethical_decision_making',
    'social_anxiety_in_formal_settings',
    'conflict_resolution',
    'power_and_responsibility',
    'building_healthy_boundaries'
  ],

  therapeuticApproaches: [
    TherapeuticApproach.CBT,
    TherapeuticApproach.NARRATIVE_THERAPY,
    TherapeuticApproach.SOLUTION_FOCUSED,
    TherapeuticApproach.GROUP_THERAPY
  ],

  therapeuticIntegrationPoints: [
    {
      trigger: 'political_decision_point',
      approach: TherapeuticApproach.CBT,
      technique: 'values_clarification_and_ethical_reasoning',
      narrativeIntegration: 'moderate',
      playerAgency: 'high',
      expectedOutcome: 'Develop ethical decision-making framework'
    },
    {
      trigger: 'court_social_situation',
      approach: TherapeuticApproach.GROUP_THERAPY,
      technique: 'social_skills_practice_and_anxiety_management',
      narrativeIntegration: 'subtle',
      playerAgency: 'high',
      expectedOutcome: 'Build confidence in formal social settings'
    }
  ],

  narrativeFramework: {
    mainArcStructure: 'Political rise with ethical challenges and relationship building',
    branchingPoints: [
      {
        pointId: 'alliance_choice',
        description: 'Choose which noble house to ally with',
        choices: [
          {
            choiceId: 'honorable_alliance',
            text: 'Ally with the house known for honor and integrity',
            therapeuticValue: { category: 'ethical_development', impact: 0.8 },
            consequences: ['Stronger moral foundation', 'Potential political disadvantage'],
            characterDevelopment: 'Develops strong ethical framework'
          },
          {
            choiceId: 'pragmatic_alliance',
            text: 'Ally with the house that offers strategic advantage',
            therapeuticValue: { category: 'strategic_thinking', impact: 0.7 },
            consequences: ['Political advantage', 'Ethical compromises required'],
            characterDevelopment: 'Learns to balance idealism with pragmatism'
          }
        ],
        therapeuticImpact: 'Explores values-based decision making under pressure',
        convergenceStrategy: 'Both paths lead to similar challenges with different ethical frameworks'
      }
    ],
    therapeuticMilestones: [
      {
        milestoneId: 'first_leadership_decision',
        description: 'Make first major decision as a leader',
        therapeuticValue: 'Builds confidence in leadership abilities',
        narrativeContext: 'Taking responsibility for others\' wellbeing in a crisis'
      }
    ],
    adaptationStrategy: 'Transform political intrigue into therapeutic exploration of leadership and ethics'
  },

  characterArchetypes: [
    {
      archetypeId: 'wise_advisor',
      name: 'Counselor Sage',
      inspirationSource: 'Wise political advisor archetype',
      role: 'Political mentor and ethical guide',
      personality: {
        traits: ['strategic', 'ethical', 'patient', 'insightful'],
        motivations: ['guide ethical leadership', 'prevent political disasters', 'build just society'],
        fears: ['corruption of power', 'political chaos', 'moral compromise'],
        growth_arc: 'Learns to balance idealism with political reality',
        therapeutic_modeling: 'Models ethical reasoning and values-based decision making'
      },
      therapeuticFunction: 'Provides guidance on ethical leadership and decision-making',
      interactionPatterns: [
        {
          trigger: 'ethical_dilemma',
          response_style: 'Socratic questioning about values and consequences',
          therapeutic_technique: 'values_clarification',
          player_impact: 'Develops personal ethical framework'
        }
      ],
      adaptationNotes: 'Original character inspired by wise advisor archetypes'
    }
  ],

  scenarioTemplates: [
    {
      templateId: 'court_intrigue',
      name: 'The Court Conspiracy',
      description: 'Navigate complex political intrigue while maintaining ethical standards',
      duration: 'long',
      therapeuticFocus: ['ethical_decision_making', 'social_navigation', 'leadership_skills'],
      narrativeElements: ['information_gathering', 'alliance_building', 'ethical_choices', 'consequences'],
      adaptationSource: 'Classic court intrigue scenario',
      variationPoints: [
        {
          pointId: 'conspiracy_type',
          description: 'Nature of the political conspiracy',
          options: ['succession_plot', 'economic_manipulation', 'foreign_influence', 'religious_conflict'],
          therapeuticImpact: 'Different conspiracies explore different ethical challenges'
        }
      ]
    }
  ],

  sessionLengthSupport: {
    short: {
      targetDuration: 30,
      narrativeStructure: 'Single political encounter or decision',
      therapeuticIntensity: 0.7,
      keyElements: ['ethical_choice', 'social_interaction', 'leadership_moment'],
      exitStrategies: ['decision_made', 'alliance_formed', 'crisis_resolved']
    },
    medium: {
      targetDuration: 90,
      narrativeStructure: 'Complete political arc or major decision sequence',
      therapeuticIntensity: 0.8,
      keyElements: ['complex_negotiation', 'ethical_development', 'relationship_building'],
      exitStrategies: ['political_victory', 'ethical_breakthrough', 'alliance_secured']
    },
    long: {
      targetDuration: 180,
      narrativeStructure: 'Major political campaign or crisis resolution',
      therapeuticIntensity: 0.9,
      keyElements: ['leadership_development', 'ethical_mastery', 'political_transformation'],
      exitStrategies: ['kingdom_saved', 'ethical_leadership_established', 'political_reform']
    }
  },

  copyrightCompliance: {
    originalElements: 0.75,
    adaptationLevel: 'high',
    legalReview: 'pending',
    riskAssessment: 'low'
  },

  contentRatings: [
    { system: 'ESRB', rating: 'T', descriptors: ['Fantasy Violence', 'Mild Language', 'Simulated Gambling'] },
    { system: 'PEGI', rating: '12', descriptors: ['Violence'] }
  ]
};
