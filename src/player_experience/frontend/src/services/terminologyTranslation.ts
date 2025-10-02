/**
 * Terminology Translation Service
 * 
 * Provides entertainment-first language translations for clinical terminology
 * while maintaining therapeutic accuracy in the backend systems.
 */

export enum UIMode {
  ENTERTAINMENT = 'entertainment',
  CLINICAL = 'clinical'
}

export interface TranslationContext {
  mode: UIMode;
  userRole?: 'player' | 'clinician' | 'admin';
  section?: 'navigation' | 'settings' | 'chat' | 'progress' | 'onboarding';
}

/**
 * Core terminology mappings from clinical to entertainment language
 */
const TERMINOLOGY_MAPPINGS = {
  // Core System Terms
  'therapeutic': {
    entertainment: 'adventure',
    clinical: 'therapeutic'
  },
  'therapy': {
    entertainment: 'adventure experience',
    clinical: 'therapy'
  },
  'patient': {
    entertainment: 'player',
    clinical: 'patient'
  },
  'session': {
    entertainment: 'adventure',
    clinical: 'session'
  },
  'treatment': {
    entertainment: 'experience',
    clinical: 'treatment'
  },
  'intervention': {
    entertainment: 'story guidance',
    clinical: 'intervention'
  },
  'crisis_support': {
    entertainment: 'emergency help',
    clinical: 'crisis support'
  },
  
  // Goals and Progress
  'therapeutic_goals': {
    entertainment: 'personal objectives',
    clinical: 'therapeutic goals'
  },
  'progress_tracking': {
    entertainment: 'achievement progress',
    clinical: 'progress tracking'
  },
  'therapeutic_compliance': {
    entertainment: 'engagement level',
    clinical: 'therapeutic compliance'
  },
  'clinical_assessment': {
    entertainment: 'personal insights',
    clinical: 'clinical assessment'
  },
  
  // Emotional and Mental Health
  'emotional_regulation': {
    entertainment: 'emotional mastery',
    clinical: 'emotional regulation'
  },
  'coping_strategies': {
    entertainment: 'life skills',
    clinical: 'coping strategies'
  },
  'mental_health': {
    entertainment: 'wellbeing',
    clinical: 'mental health'
  },
  'psychological_wellbeing': {
    entertainment: 'inner balance',
    clinical: 'psychological wellbeing'
  },
  
  // Settings and Preferences
  'therapeutic_intensity': {
    entertainment: 'experience depth',
    clinical: 'therapeutic intensity'
  },
  'therapeutic_approach': {
    entertainment: 'story style',
    clinical: 'therapeutic approach'
  },
  'therapeutic_preferences': {
    entertainment: 'adventure preferences',
    clinical: 'therapeutic preferences'
  },
  
  // Safety and Crisis
  'risk_assessment': {
    entertainment: 'wellness check',
    clinical: 'risk assessment'
  },
  'crisis_monitoring': {
    entertainment: 'safety monitoring',
    clinical: 'crisis monitoring'
  },
  'emergency_contact': {
    entertainment: 'emergency support',
    clinical: 'emergency contact'
  },
  
  // Character and Story Elements
  'character_development': {
    entertainment: 'character growth',
    clinical: 'character development'
  },
  'narrative_therapy': {
    entertainment: 'story exploration',
    clinical: 'narrative therapy'
  },
  'therapeutic_storytelling': {
    entertainment: 'interactive storytelling',
    clinical: 'therapeutic storytelling'
  }
} as const;

/**
 * Context-specific phrase translations
 */
const PHRASE_MAPPINGS = {
  // Page Titles
  'Therapeutic Gaming Session': {
    entertainment: 'Interactive Story Adventure',
    clinical: 'Therapeutic Gaming Session'
  },
  'Therapeutic Preferences': {
    entertainment: 'Adventure Preferences',
    clinical: 'Therapeutic Preferences'
  },
  'Crisis Support': {
    entertainment: 'Emergency Help',
    clinical: 'Crisis Support'
  },
  'Progress Tracking': {
    entertainment: 'Achievement Dashboard',
    clinical: 'Progress Tracking'
  },
  
  // Navigation Items
  'Therapeutic Settings': {
    entertainment: 'Experience Settings',
    clinical: 'Therapeutic Settings'
  },
  'Clinical Dashboard': {
    entertainment: 'Adventure Dashboard',
    clinical: 'Clinical Dashboard'
  },
  
  // Form Labels
  'Therapeutic Goals': {
    entertainment: 'Personal Growth Goals',
    clinical: 'Therapeutic Goals'
  },
  'Comfort Level': {
    entertainment: 'Adventure Comfort Level',
    clinical: 'Therapeutic Comfort Level'
  },
  'Intensity Level': {
    entertainment: 'Story Intensity',
    clinical: 'Therapeutic Intensity'
  },
  
  // Button Labels
  'Start Therapeutic Session': {
    entertainment: 'Begin Adventure',
    clinical: 'Start Therapeutic Session'
  },
  'Crisis Support Button': {
    entertainment: 'Emergency Help',
    clinical: 'Crisis Support'
  },
  
  // Descriptions
  'therapeutic intervention': {
    entertainment: 'story guidance',
    clinical: 'therapeutic intervention'
  },
  'clinical monitoring': {
    entertainment: 'wellness tracking',
    clinical: 'clinical monitoring'
  }
} as const;

/**
 * Translation service class
 */
export class TerminologyTranslationService {
  private static instance: TerminologyTranslationService;
  private currentMode: UIMode = UIMode.ENTERTAINMENT;
  
  private constructor() {}
  
  public static getInstance(): TerminologyTranslationService {
    if (!TerminologyTranslationService.instance) {
      TerminologyTranslationService.instance = new TerminologyTranslationService();
    }
    return TerminologyTranslationService.instance;
  }
  
  /**
   * Set the current UI mode
   */
  public setMode(mode: UIMode): void {
    this.currentMode = mode;
  }
  
  /**
   * Get the current UI mode
   */
  public getMode(): UIMode {
    return this.currentMode;
  }
  
  /**
   * Translate a single term based on current mode
   */
  public translateTerm(term: string, context?: TranslationContext): string {
    const mode = context?.mode || this.currentMode;
    const normalizedTerm = term.toLowerCase().replace(/\s+/g, '_');
    
    const mapping = TERMINOLOGY_MAPPINGS[normalizedTerm as keyof typeof TERMINOLOGY_MAPPINGS];
    if (mapping) {
      return mapping[mode];
    }
    
    return term; // Return original if no mapping found
  }
  
  /**
   * Translate a complete phrase based on current mode
   */
  public translatePhrase(phrase: string, context?: TranslationContext): string {
    const mode = context?.mode || this.currentMode;
    
    const mapping = PHRASE_MAPPINGS[phrase as keyof typeof PHRASE_MAPPINGS];
    if (mapping) {
      return mapping[mode];
    }
    
    // Fallback: try to translate individual words
    return phrase.split(' ').map(word => this.translateTerm(word, context)).join(' ');
  }
  
  /**
   * Get entertainment-friendly description for therapeutic concepts
   */
  public getEntertainmentDescription(concept: string): string {
    const descriptions: Record<string, string> = {
      'cbt': 'Learn practical problem-solving skills through interactive stories',
      'mindfulness': 'Develop focus and awareness through guided adventures',
      'narrative_therapy': 'Explore your personal story and create new chapters',
      'dbt': 'Master emotional balance through challenging scenarios',
      'crisis_support': 'Get immediate help when you need it most',
      'progress_tracking': 'See how your character grows and develops over time',
      'therapeutic_goals': 'Set meaningful objectives for your personal journey'
    };
    
    return descriptions[concept] || concept;
  }
  
  /**
   * Check if entertainment mode is active
   */
  public isEntertainmentMode(): boolean {
    return this.currentMode === UIMode.ENTERTAINMENT;
  }
  
  /**
   * Check if clinical mode is active
   */
  public isClinicalMode(): boolean {
    return this.currentMode === UIMode.CLINICAL;
  }
}

/**
 * Convenience function for quick translations
 */
export const translate = (text: string, context?: TranslationContext): string => {
  const service = TerminologyTranslationService.getInstance();
  return service.translatePhrase(text, context);
};

/**
 * React hook for using translations in components
 */
export const useTranslation = () => {
  const service = TerminologyTranslationService.getInstance();
  
  return {
    translate: (text: string, context?: TranslationContext) => service.translatePhrase(text, context),
    translateTerm: (term: string, context?: TranslationContext) => service.translateTerm(term, context),
    isEntertainmentMode: () => service.isEntertainmentMode(),
    isClinicalMode: () => service.isClinicalMode(),
    setMode: (mode: UIMode) => service.setMode(mode),
    getMode: () => service.getMode()
  };
};

export default TerminologyTranslationService;
