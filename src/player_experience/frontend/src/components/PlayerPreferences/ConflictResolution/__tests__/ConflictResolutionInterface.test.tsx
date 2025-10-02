/**
 * Tests for ConflictResolutionInterface Component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ConflictResolutionInterface from '../ConflictResolutionInterface';
import { EnhancedGoalConflict, ConflictResolutionStrategy } from '../../../../services/conflictDetectionService';

describe('ConflictResolutionInterface', () => {
  const mockStrategy: ConflictResolutionStrategy = {
    strategyId: 'test-strategy',
    title: 'Test Strategy',
    description: 'A test resolution strategy',
    steps: ['Step 1', 'Step 2', 'Step 3'],
    expectedOutcome: 'Improved goal alignment',
    timeframe: '2-4 weeks',
    difficulty: 'moderate',
    clinicalEvidence: 'high',
    priority: 1
  };

  const mockConflict: EnhancedGoalConflict = {
    conflictId: 'test-conflict-1',
    conflictingGoals: ['anxiety_reduction', 'perfectionism_management'],
    conflictType: 'approach_incompatibility',
    severity: 'high',
    description: 'Perfectionism conflicts with anxiety reduction goals',
    resolutionSuggestions: ['Focus on progress over perfection'],
    clinicalGuidance: 'Address perfectionism patterns first',
    detectedAt: new Date(),
    severityLevel: {
      level: 'high',
      score: 0.7,
      description: 'High-priority conflict',
      urgency: 'address_now'
    },
    resolutionStrategies: [mockStrategy],
    impactAnalysis: {
      affectedGoals: ['anxiety_reduction', 'perfectionism_management'],
      therapeuticRisk: 0.6,
      progressImpact: 0.7,
      userExperienceImpact: 0.5
    },
    contextualFactors: {
      userProgressLevel: 'intermediate',
      goalComplexity: 0.8,
      timeConstraints: false,
      resourceLimitations: false
    },
    autoResolvable: false,
    userActionRequired: true
  };

  const mockAutoResolvableConflict: EnhancedGoalConflict = {
    ...mockConflict,
    conflictId: 'auto-conflict-1',
    severityLevel: {
      level: 'medium',
      score: 0.5,
      description: 'Medium-priority conflict',
      urgency: 'address_soon'
    },
    autoResolvable: true,
    userActionRequired: false
  };

  const defaultProps = {
    conflicts: [mockConflict],
    selectedGoals: ['anxiety_reduction', 'perfectionism_management'],
    onResolveConflict: jest.fn(),
    onApplyAutomaticResolution: jest.fn(),
    onModifyGoals: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders conflict resolution interface with conflicts', () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      expect(screen.getByText('Conflict Resolution')).toBeInTheDocument();
      expect(screen.getByText('1 conflict detected')).toBeInTheDocument();
      expect(screen.getByText('Conflicts Requiring Your Attention')).toBeInTheDocument();
    });

    it('renders nothing when no conflicts', () => {
      const { container } = render(
        <ConflictResolutionInterface {...defaultProps} conflicts={[]} />
      );

      expect(container.firstChild).toBeNull();
    });

    it('displays conflict severity correctly', () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      expect(screen.getByText('HIGH PRIORITY')).toBeInTheDocument();
      expect(screen.getByText('address now')).toBeInTheDocument();
    });

    it('shows goal labels correctly', () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      // Should show formatted goal names
      expect(screen.getByText(/Anxiety Reduction/)).toBeInTheDocument();
      expect(screen.getByText(/Perfectionism Management/)).toBeInTheDocument();
    });

    it('applies custom className', () => {
      const { container } = render(
        <ConflictResolutionInterface {...defaultProps} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Auto-Resolvable Conflicts', () => {
    it('displays auto-resolvable conflicts section', () => {
      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={[mockAutoResolvableConflict]}
        />
      );

      expect(screen.getByText('Auto-Resolvable Conflicts')).toBeInTheDocument();
      expect(screen.getByText('Apply Auto-Resolution')).toBeInTheDocument();
    });

    it('calls onApplyAutomaticResolution when button clicked', () => {
      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={[mockAutoResolvableConflict]}
        />
      );

      fireEvent.click(screen.getByText('Apply Auto-Resolution'));
      expect(defaultProps.onApplyAutomaticResolution).toHaveBeenCalledTimes(1);
    });

    it('shows count of auto-resolvable conflicts', () => {
      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={[mockAutoResolvableConflict, { ...mockAutoResolvableConflict, conflictId: 'auto-2' }]}
        />
      );

      expect(screen.getByText('2 conflicts can be resolved automatically with recommended adjustments.')).toBeInTheDocument();
    });
  });

  describe('Manual Conflict Resolution', () => {
    it('expands and collapses conflict details', async () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      // Initially collapsed
      expect(screen.queryByText('Impact Analysis')).not.toBeInTheDocument();

      // Click to expand
      const expandButton = screen.getByLabelText('Expand details');
      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(screen.getByText('Impact Analysis')).toBeInTheDocument();
      });

      // Click to collapse
      const collapseButton = screen.getByLabelText('Collapse details');
      fireEvent.click(collapseButton);

      await waitFor(() => {
        expect(screen.queryByText('Impact Analysis')).not.toBeInTheDocument();
      });
    });

    it('displays impact analysis when expanded', async () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      fireEvent.click(screen.getByLabelText('Expand details'));

      await waitFor(() => {
        expect(screen.getByText('Impact Analysis')).toBeInTheDocument();
        expect(screen.getByText('60%')).toBeInTheDocument(); // Therapeutic Risk
        expect(screen.getByText('70%')).toBeInTheDocument(); // Progress Impact
        expect(screen.getByText('50%')).toBeInTheDocument(); // UX Impact
      });
    });

    it('displays resolution strategies when expanded', async () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      fireEvent.click(screen.getByLabelText('Expand details'));

      await waitFor(() => {
        expect(screen.getByText('Resolution Strategies')).toBeInTheDocument();
        expect(screen.getByText('Test Strategy')).toBeInTheDocument();
        expect(screen.getByText('A test resolution strategy')).toBeInTheDocument();
        expect(screen.getByText('moderate')).toBeInTheDocument();
        expect(screen.getByText('high evidence')).toBeInTheDocument();
      });
    });

    it('allows strategy selection', async () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      fireEvent.click(screen.getByLabelText('Expand details'));

      await waitFor(() => {
        const strategyCard = screen.getByText('Test Strategy').closest('div');
        fireEvent.click(strategyCard!);

        expect(screen.getByText('Apply Selected Strategy')).toBeInTheDocument();
      });
    });

    it('applies selected strategy', async () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      fireEvent.click(screen.getByLabelText('Expand details'));

      await waitFor(() => {
        const strategyCard = screen.getByText('Test Strategy').closest('div');
        fireEvent.click(strategyCard!);
      });

      fireEvent.click(screen.getByText('Apply Selected Strategy'));

      expect(defaultProps.onResolveConflict).toHaveBeenCalledWith(
        'test-conflict-1',
        mockStrategy
      );
    });

    it('displays clinical guidance', async () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      fireEvent.click(screen.getByLabelText('Expand details'));

      await waitFor(() => {
        expect(screen.getByText('Clinical Guidance')).toBeInTheDocument();
        expect(screen.getByText('Address perfectionism patterns first')).toBeInTheDocument();
      });
    });
  });

  describe('Severity Levels', () => {
    it('displays critical severity correctly', () => {
      const criticalConflict = {
        ...mockConflict,
        severityLevel: {
          level: 'critical' as const,
          score: 0.9,
          description: 'Critical conflict',
          urgency: 'immediate_action' as const
        }
      };

      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={[criticalConflict]}
        />
      );

      expect(screen.getByText('CRITICAL PRIORITY')).toBeInTheDocument();
      expect(screen.getByText('🚨')).toBeInTheDocument();
    });

    it('displays medium severity correctly', () => {
      const mediumConflict = {
        ...mockConflict,
        severityLevel: {
          level: 'medium' as const,
          score: 0.5,
          description: 'Medium conflict',
          urgency: 'address_soon' as const
        }
      };

      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={[mediumConflict]}
        />
      );

      expect(screen.getByText('MEDIUM PRIORITY')).toBeInTheDocument();
      expect(screen.getByText('⚡')).toBeInTheDocument();
    });

    it('displays low severity correctly', () => {
      const lowConflict = {
        ...mockConflict,
        severityLevel: {
          level: 'low' as const,
          score: 0.2,
          description: 'Low conflict',
          urgency: 'monitor' as const
        }
      };

      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={[lowConflict]}
        />
      );

      expect(screen.getByText('LOW PRIORITY')).toBeInTheDocument();
      expect(screen.getByText('💡')).toBeInTheDocument();
    });
  });

  describe('Multiple Conflicts', () => {
    it('handles multiple conflicts correctly', () => {
      const multipleConflicts = [
        mockConflict,
        { ...mockConflict, conflictId: 'conflict-2' },
        mockAutoResolvableConflict
      ];

      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={multipleConflicts}
        />
      );

      expect(screen.getByText('3 conflicts detected')).toBeInTheDocument();
      expect(screen.getByText('Auto-Resolvable Conflicts')).toBeInTheDocument();
      expect(screen.getByText('Conflicts Requiring Your Attention')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels for expand/collapse buttons', () => {
      render(<ConflictResolutionInterface {...defaultProps} />);

      expect(screen.getByLabelText('Expand details')).toBeInTheDocument();
    });

    it('has proper button roles and labels', () => {
      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={[mockAutoResolvableConflict]}
        />
      );

      const autoResolveButton = screen.getByText('Apply Auto-Resolution');
      expect(autoResolveButton.tagName).toBe('BUTTON');
    });
  });

  describe('Strategy Difficulty and Evidence Display', () => {
    it('displays strategy difficulty badges correctly', async () => {
      const strategies = [
        { ...mockStrategy, strategyId: 'easy', difficulty: 'easy' as const },
        { ...mockStrategy, strategyId: 'challenging', difficulty: 'challenging' as const }
      ];

      const conflictWithStrategies = {
        ...mockConflict,
        resolutionStrategies: strategies
      };

      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={[conflictWithStrategies]}
        />
      );

      fireEvent.click(screen.getByLabelText('Expand details'));

      await waitFor(() => {
        expect(screen.getByText('easy')).toBeInTheDocument();
        expect(screen.getByText('challenging')).toBeInTheDocument();
      });
    });

    it('displays clinical evidence badges correctly', async () => {
      const strategies = [
        { ...mockStrategy, strategyId: 'high-evidence', clinicalEvidence: 'high' as const },
        { ...mockStrategy, strategyId: 'low-evidence', clinicalEvidence: 'low' as const }
      ];

      const conflictWithStrategies = {
        ...mockConflict,
        resolutionStrategies: strategies
      };

      render(
        <ConflictResolutionInterface
          {...defaultProps}
          conflicts={[conflictWithStrategies]}
        />
      );

      fireEvent.click(screen.getByLabelText('Expand details'));

      await waitFor(() => {
        expect(screen.getByText('high evidence')).toBeInTheDocument();
        expect(screen.getByText('low evidence')).toBeInTheDocument();
      });
    });
  });
});
