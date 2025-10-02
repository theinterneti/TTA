import type { Meta, StoryObj } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import TherapeuticGoalsSelector from './TherapeuticGoalsSelector';

const meta: Meta<typeof TherapeuticGoalsSelector> = {
  title: 'Components/PlayerPreferences/TherapeuticGoalsSelector',
  component: TherapeuticGoalsSelector,
  parameters: {
    layout: 'padded',
    // Visual regression testing configuration
    visualRegression: {
      // Enable visual regression testing for all stories by default
      disable: false,
      // Configure screenshot options
      options: {
        fullPage: false,
        clip: { x: 0, y: 0, width: 1200, height: 800 },
      },
    },
    // Chromatic configuration
    chromatic: {
      // Pause animations for consistent screenshots
      pauseAnimationAtEnd: true,
      // Disable animations
      disableSnapshot: false,
      // Configure viewports for testing
      viewports: [320, 768, 1200, 1920],
    },
    docs: {
      description: {
        component: `
# TherapeuticGoalsSelector

A comprehensive component for selecting therapeutic goals and primary concerns in the TTA therapeutic platform.

## Features
- **Dual Tab Interface**: Separate tabs for Therapeutic Goals and Primary Concerns
- **Predefined Options**: 15+ therapeutic goals across 5 categories and 8 common concerns
- **Custom Entries**: Users can add custom goals and concerns
- **Quick Selection**: Preset combinations for common therapeutic focuses
- **Real-time Summary**: Live display of selected items
- **Accessibility**: Full keyboard navigation and screen reader support

## Therapeutic Categories
- **Emotional Wellbeing**: Anxiety reduction, stress management, mood regulation
- **Self-Development**: Confidence building, personal growth, habit formation
- **Relationships & Communication**: Social skills, boundary setting, conflict resolution
- **Mind-Body Connection**: Mindfulness, body awareness, sleep improvement
- **Coping & Recovery**: Healthy coping strategies, trauma recovery

## Usage
This component is designed for therapeutic intake and preference setting, helping users identify their primary areas of focus for personalized therapeutic experiences.

## Visual Regression Testing
This component includes comprehensive visual regression testing to ensure:
- Consistent rendering across browsers and viewports
- Proper responsive design behavior
- Visual accessibility indicators remain intact
- Interactive states render correctly
        `,
      },
    },
  },
  argTypes: {
    selected: {
      control: 'object',
      description: 'Array of selected therapeutic goal IDs',
      table: {
        type: { summary: 'string[]' },
        defaultValue: { summary: '[]' },
      },
    },
    primaryConcerns: {
      control: 'object',
      description: 'Array of selected primary concerns',
      table: {
        type: { summary: 'string[]' },
        defaultValue: { summary: '[]' },
      },
    },
    onChange: {
      action: 'changed',
      description: 'Callback fired when selections change',
      table: {
        type: { summary: '(goals: string[], concerns: string[]) => void' },
      },
    },
  },
  args: {
    onChange: action('selection-changed'),
  },
} satisfies Meta<typeof TherapeuticGoalsSelector>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default state with no selections - the initial state users see
 */
export const Default: Story = {
  args: {
    selected: [],
    primaryConcerns: [],
  },
};

/**
 * State with pre-selected therapeutic goals from different categories
 */
export const WithSelectedGoals: Story = {
  args: {
    selected: ['anxiety_reduction', 'stress_management', 'confidence_building'],
    primaryConcerns: [],
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows the component with several therapeutic goals pre-selected across different categories.',
      },
    },
  },
};

/**
 * State with pre-selected primary concerns
 */
export const WithSelectedConcerns: Story = {
  args: {
    selected: [],
    primaryConcerns: ['Work stress', 'Relationship issues', 'Social anxiety'],
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows the component with the Primary Concerns tab active and several concerns selected.',
      },
    },
  },
};

/**
 * Comprehensive selection with both goals and concerns
 */
export const WithBothSelections: Story = {
  args: {
    selected: ['anxiety_reduction', 'stress_management', 'social_skills'],
    primaryConcerns: ['Work stress', 'Social anxiety'],
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows the component with both therapeutic goals and primary concerns selected, demonstrating the selection summary.',
      },
    },
  },
};

/**
 * State with custom goals and concerns added by the user
 */
export const WithCustomEntries: Story = {
  args: {
    selected: ['anxiety_reduction', 'Custom Goal: Improve Work-Life Balance', 'Custom Goal: Better Sleep Routine'],
    primaryConcerns: ['Work stress', 'Custom Concern: Perfectionism', 'Custom Concern: Time Management'],
  },
  parameters: {
    docs: {
      description: {
        story: 'Demonstrates the component with custom goals and concerns that users have added beyond the predefined options.',
      },
    },
  },
};

/**
 * Stress and anxiety focused selection (common therapeutic combination)
 */
export const StressAndAnxietyFocus: Story = {
  args: {
    selected: ['anxiety_reduction', 'stress_management', 'mindfulness_practice', 'coping_strategies'],
    primaryConcerns: ['Work stress', 'Social anxiety', 'Health concerns'],
  },
  parameters: {
    docs: {
      description: {
        story: 'A common therapeutic focus combining stress and anxiety management goals with related concerns.',
      },
    },
  },
};

/**
 * Self-development and growth focused selection
 */
export const SelfDevelopmentFocus: Story = {
  args: {
    selected: ['confidence_building', 'personal_growth', 'habit_formation', 'goal_setting'],
    primaryConcerns: ['Life transitions', 'Financial worries'],
  },
  parameters: {
    docs: {
      description: {
        story: 'Focused on personal development and growth, suitable for users working on self-improvement.',
      },
    },
  },
};

/**
 * Relationship and communication focused selection
 */
export const RelationshipFocus: Story = {
  args: {
    selected: ['social_skills', 'boundary_setting', 'conflict_resolution', 'communication_skills'],
    primaryConcerns: ['Relationship issues', 'Family problems', 'Social anxiety'],
  },
  parameters: {
    docs: {
      description: {
        story: 'Focused on relationships and communication skills, ideal for users working on interpersonal challenges.',
      },
    },
  },
};

/**
 * Edge case with very long custom entries to test UI handling
 */
export const WithLongCustomEntries: Story = {
  args: {
    selected: [
      'anxiety_reduction',
      'Custom Goal: Develop comprehensive strategies for managing overwhelming work responsibilities while maintaining personal relationships and self-care practices',
    ],
    primaryConcerns: [
      'Work stress',
      'Custom Concern: Difficulty balancing multiple competing priorities including career advancement, family obligations, and personal health goals',
    ],
  },
  parameters: {
    docs: {
      description: {
        story: 'Tests the component\'s handling of very long custom entries to ensure proper text wrapping and UI layout.',
      },
    },
  },
};

/**
 * Maximum selections to test UI with many items
 */
export const MaximumSelections: Story = {
  args: {
    selected: [
      'anxiety_reduction',
      'stress_management',
      'mood_regulation',
      'confidence_building',
      'personal_growth',
      'habit_formation',
      'social_skills',
      'boundary_setting',
      'mindfulness_practice',
      'body_awareness',
      'coping_strategies',
      'trauma_recovery',
      'Custom Goal: Career Development',
      'Custom Goal: Creative Expression',
    ],
    primaryConcerns: [
      'Work stress',
      'Relationship issues',
      'Family problems',
      'Financial worries',
      'Health concerns',
      'Life transitions',
      'Social anxiety',
      'Depression',
      'Custom Concern: Academic Pressure',
      'Custom Concern: Technology Addiction',
    ],
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows the component with maximum selections to test UI performance and layout with many items.',
      },
    },
  },
};

/**
 * Interactive playground for testing different combinations
 */
export const Playground: Story = {
  args: {
    selected: ['anxiety_reduction'],
    primaryConcerns: ['Work stress'],
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive playground for testing different combinations of goals and concerns. Use the controls panel to modify selections.',
      },
    },
  },
};
