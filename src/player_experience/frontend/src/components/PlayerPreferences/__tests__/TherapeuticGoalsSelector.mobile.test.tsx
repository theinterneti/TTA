import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import TherapeuticGoalsSelector from '../TherapeuticGoalsSelector';

// Mock the mobile hook
jest.mock('../../../hooks/useMobile', () => ({
  useMobile: () => ({
    isMobile: true,
    isTablet: false,
    isDesktop: false,
    orientation: 'portrait',
    touchSupported: true,
    screenSize: 'sm',
  }),
}));

// Mock the services
jest.mock('../../../services/goalSuggestionEngine', () => ({
  generateGoalSuggestions: jest.fn(() => ({
    suggestions: [],
    totalConcernsAnalyzed: 0,
    suggestionStrength: 'weak'
  })),
  generateProgressAwareGoalSuggestions: jest.fn(() => ({
    suggestions: [],
    totalConcernsAnalyzed: 0,
    suggestionStrength: 'weak'
  }))
}));

jest.mock('../../../services/goalProgressService', () => ({
  analyzeGoalRelationships: jest.fn(() => ({
    relationships: [],
    conflicts: [],
    complementarySuggestions: [],
    overallCompatibility: 0.8,
    therapeuticCoherence: 0.7
  }))
}));

const mockProps = {
  selected: [],
  primaryConcerns: [],
  onChange: jest.fn(),
  goalProgresses: [],
  onProgressUpdate: jest.fn(),
  enableProgressTracking: false,
};

describe('TherapeuticGoalsSelector - Mobile Responsiveness', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock window.matchMedia for mobile testing
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: query.includes('max-width: 640px'),
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });
  });

  describe('Mobile Tab Navigation', () => {
    test('should render tabs with mobile-friendly styling', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const tabNavigation = screen.getByRole('tablist');
      expect(tabNavigation).toHaveClass('overflow-x-auto', 'scrollbar-hide');

      const tabs = screen.getAllByRole('tab');
      tabs.forEach(tab => {
        expect(tab).toHaveClass('min-w-[44px]', 'min-h-[44px]');
        expect(tab).toHaveClass('whitespace-nowrap');
      });
    });

    test('should have proper touch targets for tabs', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const tabs = screen.getAllByRole('tab');
      tabs.forEach(tab => {
        const styles = window.getComputedStyle(tab);
        // Check that tabs have minimum touch target size
        expect(tab).toHaveClass('min-h-[44px]');
        expect(tab).toHaveClass('min-w-[44px]');
      });
    });

    test('should support horizontal scrolling on mobile', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const tabNavigation = screen.getByRole('tablist');
      expect(tabNavigation).toHaveClass('overflow-x-auto');
      expect(tabNavigation).toHaveClass('scrollbar-hide');
    });
  });

  describe('Mobile Quick Selection Buttons', () => {
    test('should render quick selection buttons with mobile layout', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const quickSelectionButtons = screen.getAllByText(/🧘|💪|🤝|❤️/);
      quickSelectionButtons.forEach(button => {
        const buttonElement = button.closest('button');
        expect(buttonElement).toHaveClass('min-h-[44px]');
        expect(buttonElement).toHaveClass('grid-cols-1');
      });
    });

    test('should have proper touch targets for quick selection', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      render(<TherapeuticGoalsSelector {...mockProps} onChange={onChange} />);

      const stressButton = screen.getByText(/🧘 Stress & Anxiety/);
      const buttonElement = stressButton.closest('button');

      expect(buttonElement).toHaveClass('min-h-[44px]');

      await user.click(buttonElement!);
      expect(onChange).toHaveBeenCalled();
    });
  });

  describe('Mobile Goal Selection', () => {
    test('should render goal cards with mobile-friendly spacing', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Check that goal categories use single column layout on mobile
      const goalGrids = screen.getAllByText(/Emotional Wellness|Relationships & Communication/);
      goalGrids.forEach(categoryTitle => {
        const categorySection = categoryTitle.closest('div');
        const grid = categorySection?.querySelector('.grid');
        expect(grid).toHaveClass('grid-cols-1');
      });
    });

    test('should have larger checkboxes for mobile', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const checkboxes = screen.getAllByRole('checkbox');
      checkboxes.forEach(checkbox => {
        expect(checkbox).toHaveClass('w-5', 'h-5');
      });
    });

    test('should have proper spacing for mobile touch interaction', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const goalLabels = screen.getAllByText(/Anxiety Reduction|Stress Management/);
      goalLabels.forEach(label => {
        const labelElement = label.closest('label');
        expect(labelElement).toHaveClass('min-h-[80px]');
      });
    });
  });

  describe('Mobile Concerns Section', () => {
    test('should render concerns with single column layout on mobile', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Switch to concerns tab
      const concernsTab = screen.getByText(/📝 Primary Concerns/);
      await user.click(concernsTab);

      // Check single column layout
      const concernsGrid = screen.getByText('Common Concerns').closest('div')?.querySelector('.grid');
      expect(concernsGrid).toHaveClass('grid-cols-1');
    });

    test('should have proper touch targets for concerns', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Switch to concerns tab
      const concernsTab = screen.getByText(/📝 Primary Concerns/);
      await user.click(concernsTab);

      const concernCheckboxes = screen.getAllByRole('checkbox');
      concernCheckboxes.forEach(checkbox => {
        expect(checkbox).toHaveClass('w-5', 'h-5');
        const label = checkbox.closest('label');
        expect(label).toHaveClass('min-h-[56px]');
      });
    });
  });

  describe('Mobile Typography and Readability', () => {
    test('should use appropriate font sizes for mobile', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Check that text uses responsive sizing
      const quickSelectionTitle = screen.getByText('Quick Selection:');
      expect(quickSelectionTitle).toHaveClass('text-base', 'sm:text-lg');

      const goalLabels = screen.getAllByText(/Anxiety Reduction|Stress Management/);
      goalLabels.forEach(label => {
        expect(label).toHaveClass('text-base', 'sm:text-sm');
      });
    });

    test('should have proper line height for mobile reading', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const descriptions = screen.getAllByText(/Build skills to manage and reduce anxiety/);
      descriptions.forEach(desc => {
        expect(desc).toHaveClass('leading-relaxed');
      });
    });
  });

  describe('Mobile Performance', () => {
    test('should not cause layout shifts on mobile', () => {
      const { rerender } = render(<TherapeuticGoalsSelector {...mockProps} />);

      // Simulate props change
      rerender(<TherapeuticGoalsSelector {...mockProps} selected={['anxiety_reduction']} />);

      // Check that layout remains stable
      const tabNavigation = screen.getByRole('tablist');
      expect(tabNavigation).toHaveClass('overflow-x-auto');
    });

    test('should handle rapid touch interactions', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      render(<TherapeuticGoalsSelector {...mockProps} onChange={onChange} />);

      const stressButton = screen.getByText(/🧘 Stress & Anxiety/);
      const selfEsteemButton = screen.getByText(/💪 Self-Esteem & Growth/);

      // Rapid clicks
      await user.click(stressButton);
      await user.click(selfEsteemButton);

      expect(onChange).toHaveBeenCalledTimes(2);
    });
  });

  describe('Mobile Accessibility', () => {
    test('should maintain accessibility on mobile', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Check ARIA attributes are preserved
      const tabs = screen.getAllByRole('tab');
      tabs.forEach(tab => {
        expect(tab).toHaveAttribute('aria-selected');
        expect(tab).toHaveAttribute('aria-controls');
      });

      // Check touch targets have proper labels
      const checkboxes = screen.getAllByRole('checkbox');
      checkboxes.forEach(checkbox => {
        expect(checkbox).toHaveAttribute('aria-checked');
      });
    });

    test('should support screen reader navigation on mobile', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const tablist = screen.getByRole('tablist');
      expect(tablist).toHaveAttribute('aria-label', 'Therapeutic goals and concerns');

      const tabpanels = screen.getAllByRole('tabpanel');
      tabpanels.forEach(panel => {
        expect(panel).toHaveAttribute('aria-labelledby');
      });
    });
  });
});
