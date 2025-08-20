import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import TypingIndicator from '../TypingIndicator';

describe('TypingIndicator', () => {
  it('renders when visible is true', () => {
    render(<TypingIndicator isVisible={true} />);
    
    expect(screen.getByText('Assistant is typing...')).toBeInTheDocument();
    
    // Check for animated dots
    const dots = screen.container.querySelectorAll('.animate-bounce');
    expect(dots).toHaveLength(3);
  });

  it('does not render when visible is false', () => {
    render(<TypingIndicator isVisible={false} />);
    
    expect(screen.queryByText('Assistant is typing...')).not.toBeInTheDocument();
  });

  it('has correct styling and animation delays', () => {
    render(<TypingIndicator isVisible={true} />);
    
    const dots = screen.container.querySelectorAll('.animate-bounce');
    
    // Check that dots have different animation delays
    expect(dots[1]).toHaveStyle('animation-delay: 0.1s');
    expect(dots[2]).toHaveStyle('animation-delay: 0.2s');
  });

  it('has proper accessibility structure', () => {
    render(<TypingIndicator isVisible={true} />);
    
    const container = screen.getByText('Assistant is typing...').closest('div');
    expect(container).toHaveClass('bg-white', 'text-gray-900', 'shadow-sm');
  });
});