import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatMessage from '../ChatMessage';

const mockMessage = {
  id: 'test-message-1',
  type: 'assistant' as const,
  content: 'This is a test message with **bold** and *italic* text.',
  timestamp: '2024-01-15T10:30:00Z',
  metadata: {
    therapeutic_technique: 'CBT',
    safety: { crisis: false },
    interactive_elements: {
      buttons: [
        { id: 'btn1', text: 'Option 1', action: 'action1' },
        { id: 'btn2', text: 'Option 2', action: 'action2' }
      ]
    }
  }
};

const mockUserMessage = {
  id: 'test-message-2',
  type: 'user' as const,
  content: 'This is a user message.',
  timestamp: '2024-01-15T10:31:00Z'
};

const mockCrisisMessage = {
  id: 'test-message-3',
  type: 'assistant' as const,
  content: 'Crisis support message.',
  timestamp: '2024-01-15T10:32:00Z',
  metadata: {
    safety: { crisis: true }
  }
};

const mockGuidedExerciseMessage = {
  id: 'test-message-4',
  type: 'assistant' as const,
  content: 'Let\'s try a breathing exercise.',
  timestamp: '2024-01-15T10:33:00Z',
  metadata: {
    interactive_elements: {
      guided_exercise: {
        type: 'Breathing Exercise',
        instructions: 'Follow these steps to practice deep breathing.',
        steps: [
          'Breathe in slowly for 4 counts',
          'Hold your breath for 4 counts',
          'Breathe out slowly for 6 counts'
        ]
      }
    }
  }
};

describe('ChatMessage', () => {
  const mockOnInteractionClick = jest.fn();
  const mockOnFeedback = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders assistant message with formatted content', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    expect(screen.getByText(/This is a test message/)).toBeInTheDocument();
    // Check if HTML formatting is applied
    const messageContent = screen.getByText(/This is a test message/).closest('div');
    expect(messageContent?.innerHTML).toContain('<strong>bold</strong>');
    expect(messageContent?.innerHTML).toContain('<em>italic</em>');
  });

  it('renders user message with correct styling', () => {
    render(
      <ChatMessage
        message={mockUserMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    const messageContainer = screen.getByText('This is a user message.').closest('.bg-blue-600');
    expect(messageContainer).toBeInTheDocument();
    expect(messageContainer).toHaveClass('text-white');
  });

  it('displays therapeutic technique badge', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    expect(screen.getByText('CBT')).toBeInTheDocument();
  });

  it('displays crisis safety indicator', () => {
    render(
      <ChatMessage
        message={mockCrisisMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    expect(screen.getByText('Crisis support resources available')).toBeInTheDocument();
  });

  it('renders interactive buttons and handles clicks', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    const button1 = screen.getByText('Option 1');
    const button2 = screen.getByText('Option 2');

    expect(button1).toBeInTheDocument();
    expect(button2).toBeInTheDocument();

    fireEvent.click(button1);
    expect(mockOnInteractionClick).toHaveBeenCalledWith('test-message-1', 'action1');

    fireEvent.click(button2);
    expect(mockOnInteractionClick).toHaveBeenCalledWith('test-message-1', 'action2');
  });

  it('renders guided exercise component', () => {
    render(
      <ChatMessage
        message={mockGuidedExerciseMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    expect(screen.getByText('Breathing Exercise')).toBeInTheDocument();
    expect(screen.getByText('Follow these steps to practice deep breathing.')).toBeInTheDocument();
    expect(screen.getByText('Breathe in slowly for 4 counts')).toBeInTheDocument();
    expect(screen.getByText('Hold your breath for 4 counts')).toBeInTheDocument();
    expect(screen.getByText('Breathe out slowly for 6 counts')).toBeInTheDocument();
  });

  it('displays feedback buttons for assistant messages', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    const helpfulButton = screen.getByLabelText('Mark as helpful');
    const notHelpfulButton = screen.getByLabelText('Mark as not helpful');

    expect(helpfulButton).toBeInTheDocument();
    expect(notHelpfulButton).toBeInTheDocument();

    fireEvent.click(helpfulButton);
    expect(mockOnFeedback).toHaveBeenCalledWith('test-message-1', 'helpful');

    fireEvent.click(notHelpfulButton);
    expect(mockOnFeedback).toHaveBeenCalledWith('test-message-1', 'not_helpful');
  });

  it('does not display feedback buttons for user messages', () => {
    render(
      <ChatMessage
        message={mockUserMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    expect(screen.queryByLabelText('Mark as helpful')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Mark as not helpful')).not.toBeInTheDocument();
  });

  it('displays timestamp in correct format', () => {
    render(
      <ChatMessage
        message={mockMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    // The timestamp should be formatted as HH:MM
    expect(screen.getByText(/\d{1,2}:\d{2}/)).toBeInTheDocument();
  });

  it('displays status icon for user messages', () => {
    render(
      <ChatMessage
        message={mockUserMessage}
        onInteractionClick={mockOnInteractionClick}
        onFeedback={mockOnFeedback}
      />
    );

    // Check for checkmark icon (delivered status)
    const statusIcon = screen.getByRole('img', { hidden: true });
    expect(statusIcon).toBeInTheDocument();
  });
});
