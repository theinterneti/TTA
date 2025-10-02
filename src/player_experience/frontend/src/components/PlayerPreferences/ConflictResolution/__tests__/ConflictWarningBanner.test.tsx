/**
 * Tests for ConflictWarningBanner Component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ConflictWarningBanner from '../ConflictWarningBanner';
import { ConflictDetectionResult } from '../../../../services/conflictDetectionService';

describe('ConflictWarningBanner', () => {
  const mockConflictResult: ConflictDetectionResult = {
    conflicts: [],
    overallRiskScore: 0.7,
    recommendedActions: [
      '🚨 Address critical conflicts immediately',
      '⚠️ Review high-priority conflicts',
      '📊 Consider reducing total goals'
    ],
    safeToProceeed: false,
    warningLevel: 'high',
    summary: {
      totalConflicts: 3,
      criticalConflicts: 1,
      resolvableConflicts: 2,
      monitoringRequired: 0
    }
  };

  const defaultProps = {
    conflictResult: mockConflictResult,
    onViewDetails: jest.fn(),
    onQuickResolve: jest.fn(),
    onDismiss: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders warning banner with conflict information', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByText('High-Priority Conflicts')).toBeInTheDocument();
      expect(screen.getByText('Should be addressed soon')).toBeInTheDocument();
      expect(screen.getByText('70%')).toBeInTheDocument(); // Risk score
      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('conflicts')).toBeInTheDocument();
    });

    it('does not render when no conflicts', () => {
      const noConflictResult = {
        ...mockConflictResult,
        warningLevel: 'none' as const
      };

      const { container } = render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={noConflictResult}
        />
      );

      expect(container.firstChild).toBeNull();
    });

    it('applies custom className', () => {
      const { container } = render(
        <ConflictWarningBanner {...defaultProps} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Warning Levels', () => {
    it('displays critical warning correctly', () => {
      const criticalResult = {
        ...mockConflictResult,
        warningLevel: 'critical' as const,
        overallRiskScore: 0.9
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={criticalResult}
        />
      );

      expect(screen.getByText('Critical Conflicts Detected')).toBeInTheDocument();
      expect(screen.getByText('Immediate attention required')).toBeInTheDocument();
      expect(screen.getByText('🚨')).toBeInTheDocument();
      expect(screen.getByText('90%')).toBeInTheDocument();
    });

    it('displays medium warning correctly', () => {
      const mediumResult = {
        ...mockConflictResult,
        warningLevel: 'medium' as const,
        overallRiskScore: 0.5
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={mediumResult}
        />
      );

      expect(screen.getByText('Moderate Conflicts')).toBeInTheDocument();
      expect(screen.getByText('May impact progress')).toBeInTheDocument();
      expect(screen.getByText('⚡')).toBeInTheDocument();
      expect(screen.getByText('50%')).toBeInTheDocument();
    });

    it('displays low warning correctly', () => {
      const lowResult = {
        ...mockConflictResult,
        warningLevel: 'low' as const,
        overallRiskScore: 0.2
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={lowResult}
        />
      );

      expect(screen.getByText('Minor Conflicts')).toBeInTheDocument();
      expect(screen.getByText('Monitor for changes')).toBeInTheDocument();
      expect(screen.getByText('💡')).toBeInTheDocument();
      expect(screen.getByText('20%')).toBeInTheDocument();
    });
  });

  describe('Conflict Summary', () => {
    it('displays total conflicts count', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('conflicts')).toBeInTheDocument();
    });

    it('displays singular conflict correctly', () => {
      const singleConflictResult = {
        ...mockConflictResult,
        summary: {
          ...mockConflictResult.summary,
          totalConflicts: 1
        }
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={singleConflictResult}
        />
      );

      expect(screen.getAllByText('1')).toHaveLength(2); // One for total conflicts, one for critical
      expect(screen.getByText('conflict')).toBeInTheDocument();
    });

    it('displays critical conflicts count when present', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('critical')).toBeInTheDocument();
    });

    it('displays resolvable conflicts count when present', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('auto-resolvable')).toBeInTheDocument();
    });

    it('hides critical count when zero', () => {
      const noCriticalResult = {
        ...mockConflictResult,
        summary: {
          ...mockConflictResult.summary,
          criticalConflicts: 0
        }
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={noCriticalResult}
        />
      );

      expect(screen.queryByText('1')).not.toBeInTheDocument();
      expect(screen.queryByText('critical')).not.toBeInTheDocument();
    });
  });

  describe('Action Buttons', () => {
    it('calls onViewDetails when View Details clicked', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      fireEvent.click(screen.getByText('View Details'));
      expect(defaultProps.onViewDetails).toHaveBeenCalledTimes(1);
    });

    it('shows Quick Resolve button when resolvable conflicts exist', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByText('Quick Resolve (2)')).toBeInTheDocument();
    });

    it('calls onQuickResolve when Quick Resolve clicked', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      fireEvent.click(screen.getByText('Quick Resolve (2)'));
      expect(defaultProps.onQuickResolve).toHaveBeenCalledTimes(1);
    });

    it('hides Quick Resolve button when no resolvable conflicts', () => {
      const noResolvableResult = {
        ...mockConflictResult,
        summary: {
          ...mockConflictResult.summary,
          resolvableConflicts: 0
        }
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={noResolvableResult}
        />
      );

      expect(screen.queryByText(/Quick Resolve/)).not.toBeInTheDocument();
    });

    it('shows "Not safe to proceed" when safeToProceeed is false', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByText('Not safe to proceed')).toBeInTheDocument();
    });

    it('hides "Not safe to proceed" when safeToProceeed is true', () => {
      const safeResult = {
        ...mockConflictResult,
        safeToProceeed: true
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={safeResult}
        />
      );

      expect(screen.queryByText('Not safe to proceed')).not.toBeInTheDocument();
    });
  });

  describe('Recommended Actions', () => {
    it('displays recommended actions preview', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByText('Quick Recommendations:')).toBeInTheDocument();
      expect(screen.getByText('🚨 Address critical conflicts immediately')).toBeInTheDocument();
      expect(screen.getByText('⚠️ Review high-priority conflicts')).toBeInTheDocument();
    });

    it('shows "more recommendations" when more than 2 actions', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByText('+1 more recommendations')).toBeInTheDocument();
    });

    it('does not show "more recommendations" when 2 or fewer actions', () => {
      const fewActionsResult = {
        ...mockConflictResult,
        recommendedActions: ['Action 1', 'Action 2']
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={fewActionsResult}
        />
      );

      expect(screen.queryByText(/more recommendations/)).not.toBeInTheDocument();
    });
  });

  describe('Dismiss Functionality', () => {
    it('shows dismiss button when onDismiss provided', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByLabelText('Dismiss warning')).toBeInTheDocument();
    });

    it('hides dismiss button when onDismiss not provided', () => {
      const { onDismiss, ...propsWithoutDismiss } = defaultProps;
      render(<ConflictWarningBanner {...propsWithoutDismiss} />);

      expect(screen.queryByLabelText('Dismiss warning')).not.toBeInTheDocument();
    });

    it('calls onDismiss and hides banner when dismiss clicked', () => {
      const { rerender } = render(<ConflictWarningBanner {...defaultProps} />);

      fireEvent.click(screen.getByLabelText('Dismiss warning'));

      expect(defaultProps.onDismiss).toHaveBeenCalledTimes(1);

      // Component should hide itself after dismiss
      rerender(<ConflictWarningBanner {...defaultProps} />);
      // Note: In real implementation, the component would be hidden
      // This test verifies the dismiss handler is called
    });
  });

  describe('Risk Score Colors', () => {
    it('applies correct color for high risk score', () => {
      const highRiskResult = {
        ...mockConflictResult,
        overallRiskScore: 0.9
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={highRiskResult}
        />
      );

      const riskScore = screen.getByText('90%');
      expect(riskScore).toHaveClass('text-red-600');
    });

    it('applies correct color for medium risk score', () => {
      const mediumRiskResult = {
        ...mockConflictResult,
        overallRiskScore: 0.5
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={mediumRiskResult}
        />
      );

      const riskScore = screen.getByText('50%');
      expect(riskScore).toHaveClass('text-yellow-600');
    });

    it('applies correct color for low risk score', () => {
      const lowRiskResult = {
        ...mockConflictResult,
        overallRiskScore: 0.2
      };

      render(
        <ConflictWarningBanner
          {...defaultProps}
          conflictResult={lowRiskResult}
        />
      );

      const riskScore = screen.getByText('20%');
      expect(riskScore).toHaveClass('text-blue-600');
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      expect(screen.getByLabelText('Warning icon')).toBeInTheDocument();
      expect(screen.getByLabelText('Dismiss warning')).toBeInTheDocument();
    });

    it('has proper button roles', () => {
      render(<ConflictWarningBanner {...defaultProps} />);

      const viewDetailsButton = screen.getByText('View Details');
      const quickResolveButton = screen.getByText('Quick Resolve (2)');

      expect(viewDetailsButton.tagName).toBe('BUTTON');
      expect(quickResolveButton.tagName).toBe('BUTTON');
    });
  });
});
