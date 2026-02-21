// Logseq: [[TTA.dev/Tests/E2e/Fixtures/Test-data]]
/**
 * Test data factories for TTA E2E tests
 */

export interface TestUser {
  username: string;
  password: string;
  email: string;
  playerId?: string;
}

export interface TestCharacter {
  name: string;
  appearance: {
    description: string;
    avatar_url?: string;
  };
  background: {
    story: string;
    personality_traits: string[];
    goals: string[];
  };
  therapeutic_profile: {
    comfort_level: number;
    preferred_intensity: 'LOW' | 'MEDIUM' | 'HIGH';
    therapeutic_goals: string[];
  };
}

export interface TestWorld {
  name: string;
  description: string;
  therapeutic_themes: string[];
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  estimated_duration: number;
}

export const testUsers = {
  default: {
    username: 'testuser',
    password: 'testpass',
    email: 'test@example.com',
  },
  premium: {
    username: 'premiumuser',
    password: 'premiumpass',
    email: 'premium@example.com',
  },
  newUser: {
    username: 'newuser',
    password: 'newpass',
    email: 'new@example.com',
  },
} as const;

export const testCharacters = {
  warrior: {
    name: 'Brave Warrior',
    appearance: {
      description: 'A courageous warrior with kind eyes and a determined spirit.',
    },
    background: {
      story: 'Once a simple villager who discovered inner strength through adversity.',
      personality_traits: ['Brave', 'Compassionate', 'Determined'],
      goals: ['Protect others', 'Find inner peace', 'Overcome past trauma'],
    },
    therapeutic_profile: {
      comfort_level: 7,
      preferred_intensity: 'MEDIUM' as const,
      therapeutic_goals: ['Build confidence', 'Process trauma', 'Develop coping skills'],
    },
  },
  healer: {
    name: 'Gentle Healer',
    appearance: {
      description: 'A wise healer with gentle hands and a calming presence.',
    },
    background: {
      story: 'A natural empath who learned to channel healing energy.',
      personality_traits: ['Empathetic', 'Wise', 'Patient'],
      goals: ['Help others heal', 'Master healing arts', 'Find balance'],
    },
    therapeutic_profile: {
      comfort_level: 8,
      preferred_intensity: 'LOW' as const,
      therapeutic_goals: ['Develop empathy', 'Learn self-care', 'Build relationships'],
    },
  },
} as const;

export const testWorlds = {
  peacefulForest: {
    name: 'Peaceful Forest',
    description: 'A serene woodland where healing and growth flourish.',
    therapeutic_themes: ['Mindfulness', 'Nature Connection', 'Inner Peace'],
    difficulty: 'BEGINNER' as const,
    estimated_duration: 30,
  },
  mysticalRealm: {
    name: 'Mystical Realm',
    description: 'A magical world where inner strength is discovered.',
    therapeutic_themes: ['Self-Discovery', 'Empowerment', 'Transformation'],
    difficulty: 'INTERMEDIATE' as const,
    estimated_duration: 45,
  },
} as const;

export const testMessages = {
  welcome: 'Welcome to your therapeutic journey. How are you feeling today?',
  encouragement: 'You\'re doing great! Remember, every step forward is progress.',
  reflection: 'Take a moment to reflect on what you\'ve learned so far.',
  crisis: 'I notice you might be struggling. Would you like to talk to someone?',
} as const;

export const testSettings = {
  therapeutic: {
    intensity_level: 'MEDIUM' as const,
    preferred_approaches: ['CBT', 'Mindfulness'],
    trigger_warnings: ['Violence', 'Abandonment'],
    comfort_topics: ['Nature', 'Animals', 'Art'],
    avoid_topics: ['Death', 'Abuse'],
    crisis_contact_info: {
      emergency_contact: 'Emergency Services: 911',
      therapist_contact: 'Dr. Smith: (555) 123-4567',
      crisis_hotline: 'Crisis Hotline: 988',
    },
  },
  privacy: {
    data_sharing_consent: false,
    research_participation: true,
    contact_preferences: ['email'],
    data_retention_period: 365,
  },
  accessibility: {
    high_contrast: false,
    large_text: false,
    screen_reader_optimized: true,
    reduced_motion: false,
    keyboard_navigation: true,
  },
} as const;

// Helper functions for generating dynamic test data
export function generateRandomUser(): TestUser {
  const timestamp = Date.now();
  return {
    username: `testuser_${timestamp}`,
    password: 'testpass123',
    email: `test_${timestamp}@example.com`,
  };
}

export function generateRandomCharacter(): TestCharacter {
  const timestamp = Date.now();
  return {
    name: `Test Character ${timestamp}`,
    appearance: {
      description: `A unique character created for testing purposes.`,
    },
    background: {
      story: `This character was created during test run ${timestamp}.`,
      personality_traits: ['Test Trait 1', 'Test Trait 2'],
      goals: ['Test Goal 1', 'Test Goal 2'],
    },
    therapeutic_profile: {
      comfort_level: Math.floor(Math.random() * 10) + 1,
      preferred_intensity: ['LOW', 'MEDIUM', 'HIGH'][Math.floor(Math.random() * 3)] as any,
      therapeutic_goals: ['Test Therapeutic Goal'],
    },
  };
}

// Test data for various scenarios
export const testScenarios = {
  newUser: {
    hasCharacters: false,
    hasPreferences: false,
    hasProgress: false,
  },
  experiencedUser: {
    hasCharacters: true,
    hasPreferences: true,
    hasProgress: true,
    characterCount: 5,
    sessionCount: 25,
  },
  premiumUser: {
    hasCharacters: true,
    hasPreferences: true,
    hasProgress: true,
    isPremium: true,
    characterCount: 10,
    sessionCount: 100,
  },
};

// Model management test data
export const testModels = [
  {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'openai',
    cost_per_token: 0.002,
    max_tokens: 4096,
    is_free: false,
    performance_score: 8.5,
    description: 'Fast and efficient model for general tasks',
    capabilities: ['chat', 'completion', 'reasoning'],
  },
  {
    id: 'llama-2-7b',
    name: 'Llama 2 7B',
    provider: 'meta',
    cost_per_token: 0.0,
    max_tokens: 4096,
    is_free: true,
    performance_score: 7.2,
    description: 'Open source model suitable for basic tasks',
    capabilities: ['chat', 'completion'],
  },
  {
    id: 'claude-3-sonnet',
    name: 'Claude 3 Sonnet',
    provider: 'anthropic',
    cost_per_token: 0.003,
    max_tokens: 200000,
    is_free: false,
    performance_score: 9.1,
    description: 'Advanced model with excellent reasoning capabilities',
    capabilities: ['chat', 'completion', 'reasoning', 'analysis'],
  },
  {
    id: 'gpt-4-turbo',
    name: 'GPT-4 Turbo',
    provider: 'openai',
    cost_per_token: 0.01,
    max_tokens: 128000,
    is_free: false,
    performance_score: 9.5,
    description: 'Most advanced OpenAI model with superior reasoning',
    capabilities: ['chat', 'completion', 'reasoning', 'analysis', 'vision'],
  },
];

// Progress tracking test data
export const testProgressData = {
  basic: {
    total_sessions: 15,
    current_streak: 7,
    completed_goals: 3,
    progress_percentage: 68,
    weekly_progress: [
      { date: '2024-01-01', sessions: 2, mood_score: 7 },
      { date: '2024-01-02', sessions: 1, mood_score: 8 },
      { date: '2024-01-03', sessions: 3, mood_score: 6 },
      { date: '2024-01-04', sessions: 2, mood_score: 7 },
      { date: '2024-01-05', sessions: 1, mood_score: 9 },
      { date: '2024-01-06', sessions: 2, mood_score: 8 },
      { date: '2024-01-07', sessions: 3, mood_score: 8 },
    ],
    milestones: [
      {
        id: 'milestone-1',
        name: 'First Week Complete',
        description: 'Complete 7 consecutive days',
        completed: true,
        completion_date: '2024-01-07',
        category: 'consistency',
      },
      {
        id: 'milestone-2',
        name: 'Anxiety Management',
        description: 'Complete anxiety-focused sessions',
        completed: false,
        progress: 0.6,
        category: 'therapeutic',
      },
      {
        id: 'milestone-3',
        name: 'Social Skills',
        description: 'Practice social interaction scenarios',
        completed: false,
        progress: 0.3,
        category: 'skills',
      },
    ],
    achievements: [
      {
        id: 'achievement-1',
        name: 'Consistent Learner',
        description: 'Maintained a 7-day streak',
        earned_date: '2024-01-07',
        badge_icon: 'streak',
        rarity: 'common',
      },
      {
        id: 'achievement-2',
        name: 'Mood Tracker',
        description: 'Logged mood for 10 consecutive days',
        earned_date: '2024-01-05',
        badge_icon: 'mood',
        rarity: 'uncommon',
      },
    ],
    insights: [
      {
        category: 'mood',
        title: 'Mood Improvement',
        description: 'Your mood scores have improved by 15% this week',
        trend: 'improving',
        confidence: 0.85,
      },
      {
        category: 'engagement',
        title: 'High Engagement',
        description: 'You\'ve been consistently engaging with sessions',
        trend: 'stable',
        confidence: 0.92,
      },
    ],
  },
  advanced: {
    total_sessions: 150,
    current_streak: 45,
    completed_goals: 12,
    progress_percentage: 89,
    monthly_progress: Array.from({ length: 12 }, (_, i) => ({
      month: `2024-${String(i + 1).padStart(2, '0')}`,
      sessions: Math.floor(Math.random() * 20) + 10,
      mood_average: Math.random() * 3 + 7,
      goals_completed: Math.floor(Math.random() * 3),
    })),
    therapeutic_metrics: {
      anxiety_reduction: 0.75,
      stress_management: 0.68,
      social_confidence: 0.82,
      emotional_regulation: 0.71,
      coping_skills: 0.79,
    },
  },
};

// Chat test data
export const testChatData = {
  messages: [
    {
      message_id: 'msg-1',
      content: 'Hello, I\'m feeling anxious about an upcoming presentation.',
      timestamp: '2024-01-07T10:00:00Z',
      sender: 'user',
      session_id: 'session-1',
    },
    {
      message_id: 'msg-2',
      content: 'I understand that presentations can feel overwhelming. Let\'s explore some techniques that might help you feel more confident.',
      timestamp: '2024-01-07T10:00:30Z',
      sender: 'assistant',
      session_id: 'session-1',
    },
    {
      message_id: 'msg-3',
      content: 'That would be helpful. I always get nervous and forget what I want to say.',
      timestamp: '2024-01-07T10:01:00Z',
      sender: 'user',
      session_id: 'session-1',
    },
  ],
  sessions: [
    {
      session_id: 'session-1',
      date: '2024-01-07',
      duration: 45,
      rating: 4,
      notes: 'Great session on presentation anxiety',
      therapeutic_goals: ['anxiety_reduction', 'confidence_building'],
      message_count: 15,
    },
    {
      session_id: 'session-2',
      date: '2024-01-06',
      duration: 30,
      rating: 5,
      notes: 'Breakthrough moment with CBT techniques',
      therapeutic_goals: ['stress_management', 'coping_skills'],
      message_count: 12,
    },
  ],
};

// Error scenarios for testing
export const testErrorScenarios = {
  networkErrors: [
    { status: 500, message: 'Internal Server Error' },
    { status: 502, message: 'Bad Gateway' },
    { status: 503, message: 'Service Unavailable' },
    { status: 504, message: 'Gateway Timeout' },
  ],
  clientErrors: [
    { status: 400, message: 'Bad Request' },
    { status: 401, message: 'Unauthorized' },
    { status: 403, message: 'Forbidden' },
    { status: 404, message: 'Not Found' },
    { status: 422, message: 'Validation Error' },
  ],
  validationErrors: {
    character: {
      name: ['Name is required', 'Name must be at least 2 characters'],
      description: ['Description is required', 'Description is too long'],
    },
    preferences: {
      intensity_level: ['Intensity level must be between 1 and 10'],
      character_name: ['Character name is required'],
    },
  },
};

// Performance test data
export const testPerformanceData = {
  largeCharacterList: Array.from({ length: 100 }, (_, i) => ({
    character_id: `char-${i}`,
    name: `Character ${i}`,
    description: `Description for character ${i}`.repeat(5),
    appearance: {
      description: `Appearance description for character ${i}`.repeat(3),
    },
    personality: {
      traits: [`trait-${i}-1`, `trait-${i}-2`, `trait-${i}-3`],
    },
    created_at: new Date(Date.now() - i * 86400000).toISOString(),
  })),
  largeWorldList: Array.from({ length: 50 }, (_, i) => ({
    world_id: `world-${i}`,
    name: `World ${i}`,
    description: `Description for world ${i}`.repeat(10),
    difficulty: ['BEGINNER', 'INTERMEDIATE', 'ADVANCED'][i % 3],
    themes: [`theme-${i}-1`, `theme-${i}-2`],
    estimated_duration: Math.floor(Math.random() * 120) + 30,
  })),
  largeChatHistory: Array.from({ length: 500 }, (_, i) => ({
    message_id: `msg-${i}`,
    content: `Message ${i} content`.repeat(Math.floor(Math.random() * 10) + 1),
    timestamp: new Date(Date.now() - i * 60000).toISOString(),
    sender: i % 2 === 0 ? 'user' : 'assistant',
  })),
};

// Accessibility test data
export const testAccessibilityData = {
  keyboardNavigationElements: [
    'button[data-testid="create-character"]',
    'input[name="character-name"]',
    'textarea[name="character-description"]',
    'select[name="character-type"]',
    'button[type="submit"]',
  ],
  ariaLabels: {
    'create-character-button': 'Create new character',
    'character-list': 'List of your characters',
    'world-selection': 'Available worlds to explore',
    'preferences-form': 'Therapeutic preferences settings',
  },
  screenReaderText: [
    'Navigate to main content',
    'Character creation form',
    'World selection grid',
    'Progress dashboard',
  ],
};

// File upload test data
export const testFileData = {
  validPreferencesFile: {
    name: 'preferences.json',
    content: JSON.stringify({
      intensity_level: 7,
      therapeutic_approach: 'CBT',
      character_name: 'TestCharacter',
      conversation_style: 'supportive',
    }),
    mimeType: 'application/json',
  },
  invalidPreferencesFile: {
    name: 'invalid.txt',
    content: 'This is not JSON',
    mimeType: 'text/plain',
  },
  corruptedPreferencesFile: {
    name: 'corrupted.json',
    content: '{ invalid json content }',
    mimeType: 'application/json',
  },
  largeFile: {
    name: 'large.json',
    content: JSON.stringify({ data: 'x'.repeat(10 * 1024 * 1024) }), // 10MB
    mimeType: 'application/json',
  },
};
