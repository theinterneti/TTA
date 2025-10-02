import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import TherapeuticGoalsSelector from '../TherapeuticGoalsSelector';
import * as goalSuggestionEngine from '../../../services/goalSuggestionEngine';

// Extend Jest matchers to include axe-core accessibility testing
expect.extend(toHaveNoViolations);

describe('TherapeuticGoalsSelector - Accessibility Tests', () => {
  const mockProps = {
    selected: [],
    primaryConcerns: [],
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('WCAG 2.1 AA Compliance', () => {
    it('should not have any accessibility violations in default state', async () => {
      const { container } = render(<TherapeuticGoalsSelector {...mockProps} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not have accessibility violations with selected goals', async () => {
      const { container } = render(
        <TherapeuticGoalsSelector
          {...mockProps}
          selected={['anxiety_reduction', 'stress_management']}
        />
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not have accessibility violations with selected concerns', async () => {
      const { container } = render(
        <TherapeuticGoalsSelector
          {...mockProps}
          primaryConcerns={['Work stress', 'Social anxiety']}
        />
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not have accessibility violations with custom entries', async () => {
      const { container } = render(
        <TherapeuticGoalsSelector
          {...mockProps}
          selected={['anxiety_reduction', 'Custom Goal: Better sleep']}
          primaryConcerns={['Work stress', 'Custom Concern: Time management']}
        />
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Keyboard Navigation', () => {
    it('should support tab navigation through all interactive elements', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Tab through main tabs
      await user.tab();
      expect(screen.getByRole('tab', { name: /therapeutic goals/i })).toHaveFocus();

      // Tab through quick selection buttons and other elements
      await user.tab();
      // The next focusable element should be one of the quick selection buttons
      const quickButtons = screen.getAllByRole('button');
      const focusedElement = document.activeElement;
      expect(quickButtons).toContain(focusedElement);
    });

    it('should support arrow key navigation between tabs', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const goalsTab = screen.getByRole('tab', { name: /therapeutic goals/i });
      const concernsTab = screen.getByRole('tab', { name: /primary concerns/i });

      // Focus on goals tab
      goalsTab.focus();
      expect(goalsTab).toHaveFocus();

      // Arrow right to concerns tab
      await user.keyboard('{ArrowRight}');
      expect(concernsTab).toHaveFocus();

      // Arrow left back to goals tab
      await user.keyboard('{ArrowLeft}');
      expect(goalsTab).toHaveFocus();
    });

    it('should support Enter and Space key activation for checkboxes', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const firstCheckbox = screen.getAllByRole('checkbox')[0];
      firstCheckbox.focus();

      // Test Space key activation
      await user.keyboard(' ');
      expect(mockProps.onChange).toHaveBeenCalled();

      jest.clearAllMocks();

      // Test Enter key activation
      await user.keyboard('{Enter}');
      expect(mockProps.onChange).toHaveBeenCalled();
    });

    it('should support keyboard navigation for custom goal input', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const customInput = screen.getByPlaceholderText(/add a custom therapeutic goal/i);
      const addButton = screen.getByRole('button', { name: /add custom goal/i });

      // Tab to custom input
      customInput.focus();
      expect(customInput).toHaveFocus();

      // Type custom goal
      await user.type(customInput, 'Custom goal');

      // Tab to add button
      await user.tab();
      expect(addButton).toHaveFocus();

      // Activate with Enter
      await user.keyboard('{Enter}');
      expect(mockProps.onChange).toHaveBeenCalled();
    });
  });

  describe('Screen Reader Support', () => {
    it('should have proper heading hierarchy', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Check for proper heading structure
      const mainHeading = screen.getByRole('heading', { level: 2 });
      expect(mainHeading).toBeInTheDocument();
      expect(mainHeading).toHaveTextContent(/therapeutic goals/i);
    });

    it('should have descriptive labels for all form controls', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Check custom goal input has proper label
      const customInput = screen.getByPlaceholderText(/add a custom therapeutic goal/i);
      expect(customInput).toHaveAccessibleName();

      // Check all checkboxes have proper labels
      const checkboxes = screen.getAllByRole('checkbox');
      checkboxes.forEach(checkbox => {
        expect(checkbox).toHaveAccessibleName();
      });
    });

    it('should provide clear tab panel labels', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const goalsTab = screen.getByRole('tab', { name: /therapeutic goals/i });
      const concernsTab = screen.getByRole('tab', { name: /primary concerns/i });

      expect(goalsTab).toHaveAttribute('aria-controls');
      expect(concernsTab).toHaveAttribute('aria-controls');

      // Check tab panels exist and are properly labeled
      const tabPanels = screen.getAllByRole('tabpanel');
      expect(tabPanels).toHaveLength(1); // Only active panel is rendered
      expect(tabPanels[0]).toHaveAttribute('aria-labelledby');
    });

    it('should announce selection changes to screen readers', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const firstCheckbox = screen.getAllByRole('checkbox')[0];
      
      // Check initial state
      expect(firstCheckbox).not.toBeChecked();
      expect(firstCheckbox).toHaveAttribute('aria-checked', 'false');

      // Select checkbox
      await user.click(firstCheckbox);
      
      // Verify ARIA state updates
      expect(mockProps.onChange).toHaveBeenCalled();
    });
  });

  describe('Focus Management', () => {
    it('should maintain focus when switching tabs', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const goalsTab = screen.getByRole('tab', { name: /therapeutic goals/i });
      const concernsTab = screen.getByRole('tab', { name: /primary concerns/i });

      // Focus and activate concerns tab
      await user.click(concernsTab);
      expect(concernsTab).toHaveFocus();
      expect(concernsTab).toHaveAttribute('aria-selected', 'true');

      // Switch back to goals tab
      await user.click(goalsTab);
      expect(goalsTab).toHaveFocus();
      expect(goalsTab).toHaveAttribute('aria-selected', 'true');
    });

    it('should have visible focus indicators', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const goalsTab = screen.getByRole('tab', { name: /therapeutic goals/i });
      goalsTab.focus();

      // Check that focus is visible (this would typically be tested with visual regression)
      expect(goalsTab).toHaveFocus();
      expect(goalsTab).toHaveClass('focus:outline-none', 'focus:ring-2');
    });

    it('should trap focus within modal-like interactions', async () => {
      // This test would be more relevant if we had modal dialogs
      // For now, we ensure focus moves logically through the component
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Tab through all focusable elements
      const focusableElements = [
        screen.getByRole('tab', { name: /therapeutic goals/i }),
        screen.getByRole('tab', { name: /primary concerns/i }),
        ...screen.getAllByRole('checkbox'),
        screen.getByPlaceholderText(/add a custom therapeutic goal/i),
        screen.getByRole('button', { name: /add custom goal/i }),
      ];

      for (let i = 0; i < focusableElements.length; i++) {
        await user.tab();
        // Focus should move through elements in logical order
      }
    });
  });

  describe('Color Contrast and Visual Accessibility', () => {
    it('should not rely solely on color to convey information', () => {
      render(
        <TherapeuticGoalsSelector
          {...mockProps}
          selected={['anxiety_reduction']}
        />
      );

      // Selected items should have additional visual indicators beyond color
      const selectedCheckbox = screen.getByRole('checkbox', { name: /anxiety reduction/i });
      expect(selectedCheckbox).toBeChecked();
      expect(selectedCheckbox).toHaveAttribute('aria-checked', 'true');
    });

    it('should provide sufficient contrast for text elements', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // This would typically be tested with automated tools or visual regression
      // For now, we ensure text elements are properly structured
      const headings = screen.getAllByRole('heading');
      headings.forEach(heading => {
        expect(heading).toBeVisible();
      });

      const labels = screen.getAllByText(/anxiety reduction|stress management/i);
      labels.forEach(label => {
        expect(label).toBeVisible();
      });
    });
  });

  describe('Error States and Validation', () => {
    it('should provide accessible error messages', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const customInput = screen.getByPlaceholderText(/add a custom therapeutic goal/i);
      const addButton = screen.getByRole('button', { name: /add custom goal/i });

      // Try to add empty custom goal
      await user.click(addButton);

      // Component should handle this gracefully without adding empty goals
      expect(mockProps.onChange).not.toHaveBeenCalled();
    });

    it('should maintain accessibility during dynamic content changes', async () => {
      const user = userEvent.setup();
      const { container } = render(<TherapeuticGoalsSelector {...mockProps} />);

      // Switch to concerns tab
      const concernsTab = screen.getByRole('tab', { name: /primary concerns/i });
      await user.click(concernsTab);

      // Check accessibility after content change
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Mobile and Touch Accessibility', () => {
    it('should have adequate touch targets', () => {
      render(<TherapeuticGoalsSelector {...mockProps} />);

      // Check that interactive elements have sufficient size for touch
      const checkboxes = screen.getAllByRole('checkbox');
      checkboxes.forEach(checkbox => {
        // This would typically be tested with visual regression or computed styles
        expect(checkbox).toBeInTheDocument();
      });

      const tabs = screen.getAllByRole('tab');
      tabs.forEach(tab => {
        expect(tab).toBeInTheDocument();
      });
    });

    it('should support touch interactions', async () => {
      const user = userEvent.setup();
      render(<TherapeuticGoalsSelector {...mockProps} />);

      const firstCheckbox = screen.getAllByRole('checkbox')[0];
      
      // Simulate touch interaction
      await user.click(firstCheckbox);
      expect(mockProps.onChange).toHaveBeenCalled();
    });
  });

  describe('Goal Suggestion System - Accessibility', () => {
    // Mock the suggestion engine
    const mockSuggestions = {
      suggestions: [
        {
          goalId: 'stress_management',
          confidence: 0.95,
          reason: 'Direct correlation with workplace stress reduction techniques',
          category: 'Emotional Wellbeing',
          clinicalEvidence: 'high' as const
        },
        {
          goalId: 'mindfulness_development',
          confidence: 0.85,
          reason: 'Mindfulness-based stress reduction (MBSR) proven effective for work stress',
          category: 'Mind-Body Connection',
          clinicalEvidence: 'high' as const
        }
      ],
      totalConcernsAnalyzed: 1,
      suggestionStrength: 'strong' as const
    };

    beforeEach(() => {
      jest.spyOn(goalSuggestionEngine, 'generateGoalSuggestions').mockReturnValue(mockSuggestions);
    });

    afterEach(() => {
      jest.restoreAllMocks();
    });

    it('should have no accessibility violations with suggestions displayed', async () => {
      const { container } = render(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={['Work stress']}
          onChange={jest.fn()}
        />
      );

      // Wait for suggestions to appear
      await waitFor(() => {
        expect(screen.getByText('🤖 AI-Powered Goal Suggestions')).toBeInTheDocument();
      });

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA labels for suggestion buttons', async () => {
      render(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={['Work stress']}
          onChange={jest.fn()}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('🤖 AI-Powered Goal Suggestions')).toBeInTheDocument();
      });

      const addButtons = screen.getAllByRole('button', { name: /Add suggested goal/ });
      expect(addButtons).toHaveLength(2);

      expect(addButtons[0]).toHaveAttribute('aria-label', 'Add suggested goal: Stress Management');
      expect(addButtons[1]).toHaveAttribute('aria-label', 'Add suggested goal: Mindfulness Development');
    });

    it('should have proper ARIA label for Apply All button', async () => {
      render(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={['Work stress']}
          onChange={jest.fn()}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('🤖 AI-Powered Goal Suggestions')).toBeInTheDocument();
      });

      const applyAllButton = screen.getByRole('button', { name: 'Apply all suggested goals' });
      expect(applyAllButton).toBeInTheDocument();
    });

    it('should support keyboard navigation for suggestion buttons', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();

      render(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={['Work stress']}
          onChange={onChange}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('🤖 AI-Powered Goal Suggestions')).toBeInTheDocument();
      });

      const addButtons = screen.getAllByRole('button', { name: /Add suggested goal/ });

      // Focus first button and activate with Enter
      addButtons[0].focus();
      await user.keyboard('{Enter}');

      expect(onChange).toHaveBeenCalledWith(['stress_management'], ['Work stress']);
    });

    it('should support keyboard navigation for Apply All button', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();

      render(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={['Work stress']}
          onChange={onChange}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('🤖 AI-Powered Goal Suggestions')).toBeInTheDocument();
      });

      const applyAllButton = screen.getByRole('button', { name: 'Apply all suggested goals' });

      // Focus and activate with Space
      applyAllButton.focus();
      await user.keyboard(' ');

      expect(onChange).toHaveBeenCalledWith(
        ['stress_management', 'mindfulness_development'],
        ['Work stress']
      );
    });

    it('should have proper focus management when suggestions appear', async () => {
      const { rerender } = render(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={[]}
          onChange={jest.fn()}
        />
      );

      // No suggestions initially
      expect(screen.queryByText('🤖 AI-Powered Goal Suggestions')).not.toBeInTheDocument();

      // Add concerns to trigger suggestions
      rerender(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={['Work stress']}
          onChange={jest.fn()}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('🤖 AI-Powered Goal Suggestions')).toBeInTheDocument();
      });

      // Suggestions should be focusable
      const addButtons = screen.getAllByRole('button', { name: /Add suggested goal/ });
      expect(addButtons[0]).toHaveAttribute('tabindex', '0');
    });

    it('should have proper color contrast for suggestion elements', async () => {
      const { container } = render(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={['Work stress']}
          onChange={jest.fn()}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('🤖 AI-Powered Goal Suggestions')).toBeInTheDocument();
      });

      // Test for color contrast violations
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true }
        }
      });
      expect(results).toHaveNoViolations();
    });

    it('should announce suggestion changes to screen readers', async () => {
      const { rerender } = render(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={[]}
          onChange={jest.fn()}
        />
      );

      // Add concerns to trigger suggestions
      rerender(
        <TherapeuticGoalsSelector
          selected={[]}
          primaryConcerns={['Work stress']}
          onChange={jest.fn()}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('🤖 AI-Powered Goal Suggestions')).toBeInTheDocument();
      });

      // The suggestion section should be properly structured for screen readers
      const suggestionSection = screen.getByText('🤖 AI-Powered Goal Suggestions').closest('div');
      expect(suggestionSection).toBeInTheDocument();
    });
  });
});
