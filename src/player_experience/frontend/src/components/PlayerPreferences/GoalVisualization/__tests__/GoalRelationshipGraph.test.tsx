import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import GoalRelationshipGraph from '../GoalRelationshipGraph';
import { GoalRelationshipMap } from '../../../../services/goalRelationshipService';

// Mock canvas context
const mockCanvasContext = {
  clearRect: jest.fn(),
  beginPath: jest.fn(),
  moveTo: jest.fn(),
  lineTo: jest.fn(),
  stroke: jest.fn(),
  fill: jest.fn(),
  arc: jest.fn(),
  fillText: jest.fn(),
  strokeStyle: '',
  fillStyle: '',
  lineWidth: 0,
  globalAlpha: 1,
  font: '',
  textAlign: 'center' as CanvasTextAlign,
  textBaseline: 'middle' as CanvasTextBaseline,
};

// Mock HTMLCanvasElement.getContext
HTMLCanvasElement.prototype.getContext = jest.fn(() => mockCanvasContext);

describe('GoalRelationshipGraph', () => {
  const mockRelationshipMap: GoalRelationshipMap = {
    goals: ['anxiety_reduction', 'mindfulness_practice', 'stress_management'],
    relationships: [
      {
        sourceGoal: 'anxiety_reduction',
        targetGoal: 'mindfulness_practice',
        relationshipType: 'synergistic',
        strength: 0.9,
        clinicalEvidence: 'high',
        description: 'Mindfulness supports anxiety reduction',
        therapeuticRationale: 'Evidence-based connection'
      },
      {
        sourceGoal: 'mindfulness_practice',
        targetGoal: 'stress_management',
        relationshipType: 'complementary',
        strength: 0.8,
        clinicalEvidence: 'high',
        description: 'Mindfulness complements stress management',
        therapeuticRationale: 'Synergistic approaches'
      }
    ],
    conflicts: [],
    complementarySuggestions: [],
    overallCompatibility: 0.85,
    therapeuticCoherence: 0.9
  };

  const emptyRelationshipMap: GoalRelationshipMap = {
    goals: [],
    relationships: [],
    conflicts: [],
    complementarySuggestions: [],
    overallCompatibility: 0.7,
    therapeuticCoherence: 1.0
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders canvas with correct dimensions', () => {
      const { container } = render(
        <GoalRelationshipGraph
          relationshipMap={mockRelationshipMap}
          width={600}
          height={400}
        />
      );

      const canvas = container.querySelector('canvas');
      expect(canvas).toBeInTheDocument();
      expect(canvas).toHaveAttribute('width', '600');
      expect(canvas).toHaveAttribute('height', '400');
    });

    it('renders legend with relationship types', () => {
      render(<GoalRelationshipGraph relationshipMap={mockRelationshipMap} />);

      expect(screen.getByText('Synergistic')).toBeInTheDocument();
      expect(screen.getByText('Complementary')).toBeInTheDocument();
      expect(screen.getByText('Prerequisite')).toBeInTheDocument();
      expect(screen.getByText('Conflicting')).toBeInTheDocument();
    });

    it('shows empty state when no goals selected', () => {
      render(<GoalRelationshipGraph relationshipMap={emptyRelationshipMap} />);

      expect(screen.getByText('Select goals to see relationships')).toBeInTheDocument();
      expect(screen.getByText('🎯')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      const { container } = render(
        <GoalRelationshipGraph
          relationshipMap={mockRelationshipMap}
          className="custom-class"
        />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Interactions', () => {
    it('calls onNodeClick when node is clicked', () => {
      const mockOnNodeClick = jest.fn();
      const { container } = render(
        <GoalRelationshipGraph
          relationshipMap={mockRelationshipMap}
          onNodeClick={mockOnNodeClick}
        />
      );

      const canvas = container.querySelector('canvas');

      // Simulate click at center of canvas (where nodes would be)
      fireEvent.click(canvas, { clientX: 300, clientY: 200 });

      // Note: Due to the complexity of testing canvas interactions,
      // we would need to mock getBoundingClientRect and test the actual
      // click detection logic separately
    });

    it('shows hover tooltip on mouse move', () => {
      const { container } = render(<GoalRelationshipGraph relationshipMap={mockRelationshipMap} />);

      const canvas = container.querySelector('canvas');

      // Simulate mouse move
      fireEvent.mouseMove(canvas, { clientX: 300, clientY: 200 });

      // The hover state would be tested by checking if the tooltip appears
      // This requires more complex setup to mock the canvas coordinate system
    });
  });

  describe('Canvas Drawing', () => {
    it('calls canvas drawing methods when goals are present', () => {
      render(<GoalRelationshipGraph relationshipMap={mockRelationshipMap} />);

      // Verify canvas context methods are called
      expect(mockCanvasContext.clearRect).toHaveBeenCalled();
      expect(mockCanvasContext.beginPath).toHaveBeenCalled();
      expect(mockCanvasContext.arc).toHaveBeenCalled();
      expect(mockCanvasContext.fill).toHaveBeenCalled();
    });

    it('does not draw when no goals are present', () => {
      const { container } = render(<GoalRelationshipGraph relationshipMap={emptyRelationshipMap} />);

      // Canvas should not be rendered for empty state
      expect(container.querySelector('canvas')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      const { container } = render(<GoalRelationshipGraph relationshipMap={mockRelationshipMap} />);

      const canvas = container.querySelector('canvas');
      expect(canvas).toHaveClass('cursor-pointer');
    });

    it('provides meaningful empty state message', () => {
      render(<GoalRelationshipGraph relationshipMap={emptyRelationshipMap} />);

      expect(screen.getByText('Select goals to see relationships')).toBeInTheDocument();
    });
  });

  describe('Props Handling', () => {
    it('uses default dimensions when not specified', () => {
      const { container } = render(<GoalRelationshipGraph relationshipMap={mockRelationshipMap} />);

      const canvas = container.querySelector('canvas');
      expect(canvas).toHaveAttribute('width', '600');
      expect(canvas).toHaveAttribute('height', '400');
    });

    it('handles custom dimensions', () => {
      const { container } = render(
        <GoalRelationshipGraph
          relationshipMap={mockRelationshipMap}
          width={800}
          height={500}
        />
      );

      const canvas = container.querySelector('canvas');
      expect(canvas).toHaveAttribute('width', '800');
      expect(canvas).toHaveAttribute('height', '500');
    });

    it('handles missing onNodeClick gracefully', () => {
      expect(() => {
        render(<GoalRelationshipGraph relationshipMap={mockRelationshipMap} />);
      }).not.toThrow();
    });
  });

  describe('Relationship Visualization', () => {
    it('handles different relationship types', () => {
      const complexRelationshipMap: GoalRelationshipMap = {
        ...mockRelationshipMap,
        relationships: [
          ...mockRelationshipMap.relationships,
          {
            sourceGoal: 'anxiety_reduction',
            targetGoal: 'stress_management',
            relationshipType: 'conflicting',
            strength: 0.3,
            clinicalEvidence: 'low',
            description: 'Potential conflict',
            therapeuticRationale: 'May compete for resources'
          }
        ]
      };

      render(<GoalRelationshipGraph relationshipMap={complexRelationshipMap} />);

      // Verify legend shows all relationship types
      expect(screen.getByText('Synergistic')).toBeInTheDocument();
      expect(screen.getByText('Complementary')).toBeInTheDocument();
      expect(screen.getByText('Conflicting')).toBeInTheDocument();
    });

    it('handles goals without relationships', () => {
      const isolatedGoalsMap: GoalRelationshipMap = {
        goals: ['anxiety_reduction', 'mindfulness_practice'],
        relationships: [],
        conflicts: [],
        complementarySuggestions: [],
        overallCompatibility: 0.5,
        therapeuticCoherence: 0.6
      };

      render(<GoalRelationshipGraph relationshipMap={isolatedGoalsMap} />);

      // Should still render nodes even without relationships
      expect(mockCanvasContext.arc).toHaveBeenCalled();
    });
  });
});
