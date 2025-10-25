import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import GuidedExercise from '../GuidedExercise';

const mockExercise = {
  type: 'Breathing Exercise',
  instructions: 'Follow these steps to practice deep breathing.',
  steps: [
    'Breathe in slowly for 4 counts',
    'Hold your breath for 4 counts',
    'Breathe out slowly for 6 counts'
  ]
};

const mockTimedExercise = {
  ...mockExercise,
  duration: 5, // 5 seconds per step
  interactive: true
};

describe('GuidedExercise', () => {
  const mockOnComplete = jest.fn();
  const mockOnProgress = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('renders exercise with title and instructions', () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    expect(screen.getByText('Breathing Exercise')).toBeInTheDocument();
    expect(screen.getByText('Follow these steps to practice deep breathing.')).toBeInTheDocument();
  });

  it('displays all exercise steps when not active', () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    expect(screen.getByText('Breathe in slowly for 4 counts')).toBeInTheDocument();
    expect(screen.getByText('Hold your breath for 4 counts')).toBeInTheDocument();
    expect(screen.getByText('Breathe out slowly for 6 counts')).toBeInTheDocument();
  });

  it('starts exercise when start button is clicked', () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    // Should show progress bar and current step
    expect(screen.container.querySelector('.bg-blue-600')).toBeInTheDocument(); // Progress bar
    expect(screen.getByText('1')).toBeInTheDocument(); // Step number
  });

  it('shows timer for timed exercises', () => {
    render(
      <GuidedExercise
        exercise={mockTimedExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    expect(screen.getByText('0:05')).toBeInTheDocument();
  });

  it('advances to next step automatically for timed exercises', async () => {
    render(
      <GuidedExercise
        exercise={mockTimedExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    // Fast-forward timer
    jest.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(mockOnProgress).toHaveBeenCalledWith(0, true);
    });
  });

  it('shows complete step button for interactive exercises', () => {
    render(
      <GuidedExercise
        exercise={mockTimedExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    expect(screen.getByText('Complete Step')).toBeInTheDocument();
  });

  it('allows manual step completion for interactive exercises', () => {
    render(
      <GuidedExercise
        exercise={mockTimedExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    const completeButton = screen.getByText('Complete Step');
    fireEvent.click(completeButton);

    expect(mockOnProgress).toHaveBeenCalledWith(0, true);
  });

  it('shows skip button during exercise', () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    expect(screen.getByText('Skip')).toBeInTheDocument();
  });

  it('allows skipping steps', () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    const skipButton = screen.getByText('Skip');
    fireEvent.click(skipButton);

    // Should advance to step 2
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('calls onComplete when all steps are finished', async () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    // Skip through all steps
    const skipButton = screen.getByText('Skip');
    fireEvent.click(skipButton); // Step 1 -> 2
    fireEvent.click(skipButton); // Step 2 -> 3
    fireEvent.click(skipButton); // Step 3 -> Complete

    expect(mockOnComplete).toHaveBeenCalled();
  });

  it('shows completion message when exercise is finished', () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    // Complete all steps manually by updating state
    const skipButton = screen.getByText('Skip');
    fireEvent.click(skipButton);
    fireEvent.click(skipButton);
    fireEvent.click(skipButton);

    expect(screen.getByText("Great job! You've completed the exercise.")).toBeInTheDocument();
  });

  it('resets exercise when reset button is clicked', () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    const resetButton = screen.container.querySelector('[title="Reset exercise"]');
    expect(resetButton).toBeInTheDocument();

    fireEvent.click(resetButton!);

    // Should be back to initial state
    expect(screen.getByText('Start Exercise')).toBeInTheDocument();
  });

  it('shows progress indicators for each step', () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    // Should show 3 step indicators
    const indicators = screen.container.querySelectorAll('.w-2.h-2.rounded-full');
    expect(indicators).toHaveLength(3);
  });

  it('updates progress bar as steps are completed', () => {
    render(
      <GuidedExercise
        exercise={mockExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    const progressBar = screen.container.querySelector('.bg-blue-600');
    expect(progressBar).toHaveStyle('width: 33.333333333333336%'); // 1/3 steps

    const skipButton = screen.getByText('Skip');
    fireEvent.click(skipButton);

    expect(progressBar).toHaveStyle('width: 66.66666666666667%'); // 2/3 steps
  });

  it('displays appropriate icon for exercise type', () => {
    const breathingExercise = { ...mockExercise, type: 'Breathing Exercise' };
    const { rerender } = render(
      <GuidedExercise
        exercise={breathingExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    // Should render heart icon for breathing
    expect(screen.container.querySelector('svg')).toBeInTheDocument();

    const mindfulnessExercise = { ...mockExercise, type: 'Mindfulness' };
    rerender(
      <GuidedExercise
        exercise={mindfulnessExercise}
        onComplete={mockOnComplete}
        onProgress={mockOnProgress}
      />
    );

    // Should still render an icon
    expect(screen.container.querySelector('svg')).toBeInTheDocument();
  });
});
