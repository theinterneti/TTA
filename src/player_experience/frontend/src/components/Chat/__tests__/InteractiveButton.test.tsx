import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import InteractiveButton from '../InteractiveButton';

describe('InteractiveButton', () => {
  const mockOnClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders button with text', () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="Test Button"
        action="test_action"
        onClick={mockOnClick}
      />
    );

    expect(screen.getByText('Test Button')).toBeInTheDocument();
  });

  it('calls onClick with correct parameters when clicked', () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="Test Button"
        action="test_action"
        onClick={mockOnClick}
      />
    );

    fireEvent.click(screen.getByText('Test Button'));
    expect(mockOnClick).toHaveBeenCalledWith('test-btn', 'test_action');
  });

  it('applies correct variant styles', () => {
    const { rerender } = render(
      <InteractiveButton
        id="test-btn"
        text="Primary Button"
        action="test_action"
        variant="primary"
        onClick={mockOnClick}
      />
    );

    const button = screen.getByText('Primary Button');
    expect(button).toHaveClass('bg-blue-600');

    rerender(
      <InteractiveButton
        id="test-btn"
        text="Therapeutic Button"
        action="test_action"
        variant="therapeutic"
        onClick={mockOnClick}
      />
    );

    expect(screen.getByText('Therapeutic Button')).toHaveClass('bg-green-600');
  });

  it('applies correct size styles', () => {
    const { rerender } = render(
      <InteractiveButton
        id="test-btn"
        text="Small Button"
        action="test_action"
        size="sm"
        onClick={mockOnClick}
      />
    );

    expect(screen.getByText('Small Button')).toHaveClass('px-3', 'py-1.5', 'text-xs');

    rerender(
      <InteractiveButton
        id="test-btn"
        text="Large Button"
        action="test_action"
        size="lg"
        onClick={mockOnClick}
      />
    );

    expect(screen.getByText('Large Button')).toHaveClass('px-6', 'py-3', 'text-base');
  });

  it('shows safety indicator for crisis level', () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="Crisis Button"
        action="test_action"
        onClick={mockOnClick}
        metadata={{
          safety_level: 'crisis'
        }}
      />
    );

    const safetyIndicator = screen.container.querySelector('.bg-red-500');
    expect(safetyIndicator).toBeInTheDocument();
  });

  it('shows confidence bar when confidence level is provided', () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="Confident Button"
        action="test_action"
        onClick={mockOnClick}
        metadata={{
          confidence_level: 0.8
        }}
      />
    );

    const confidenceBar = screen.container.querySelector('.bg-green-500');
    expect(confidenceBar).toBeInTheDocument();
  });

  it('shows therapeutic technique indicator', () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="CBT Button"
        action="test_action"
        onClick={mockOnClick}
        metadata={{
          therapeutic_technique: 'CBT'
        }}
      />
    );

    expect(screen.getByText('CBT')).toBeInTheDocument();
  });

  it('shows tooltip on hover with metadata', async () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="Tooltip Button"
        action="test_action"
        onClick={mockOnClick}
        metadata={{
          expected_outcome: 'This will help with anxiety',
          confidence_level: 0.9
        }}
      />
    );

    const button = screen.getByText('Tooltip Button');
    fireEvent.mouseEnter(button);

    await waitFor(() => {
      expect(screen.getByText('This will help with anxiety')).toBeInTheDocument();
      expect(screen.getByText('Confidence: 90%')).toBeInTheDocument();
    });
  });

  it('is disabled when disabled prop is true', () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="Disabled Button"
        action="test_action"
        disabled={true}
        onClick={mockOnClick}
      />
    );

    const button = screen.getByText('Disabled Button');
    expect(button).toBeDisabled();
    expect(button).toHaveClass('cursor-not-allowed');

    fireEvent.click(button);
    expect(mockOnClick).not.toHaveBeenCalled();
  });

  it('shows loading state', () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="Loading Button"
        action="test_action"
        loading={true}
        onClick={mockOnClick}
      />
    );

    const button = screen.getByText('Loading Button');
    expect(button).toHaveClass('cursor-wait');

    // Should show loading spinner
    const spinner = screen.container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();

    fireEvent.click(button);
    expect(mockOnClick).not.toHaveBeenCalled();
  });

  it('renders with custom icon', () => {
    const customIcon = <span data-testid="custom-icon">🎯</span>;

    render(
      <InteractiveButton
        id="test-btn"
        text="Icon Button"
        action="test_action"
        icon={customIcon}
        onClick={mockOnClick}
      />
    );

    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });

  it('applies pressed state on mouse down', () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="Press Button"
        action="test_action"
        onClick={mockOnClick}
      />
    );

    const button = screen.getByText('Press Button');
    fireEvent.mouseDown(button);

    expect(button).toHaveClass('scale-95');
  });

  it('removes pressed state on mouse up', () => {
    render(
      <InteractiveButton
        id="test-btn"
        text="Press Button"
        action="test_action"
        onClick={mockOnClick}
      />
    );

    const button = screen.getByText('Press Button');
    fireEvent.mouseDown(button);
    fireEvent.mouseUp(button);

    expect(button).not.toHaveClass('scale-95');
  });
});
