import React from 'react';
import { render, screen } from '@testing-library/react';

// Simple test to verify testing setup
describe('Test Setup', () => {
  it('should render a simple component', () => {
    const TestComponent = () => <div>Test Component</div>;
    render(<TestComponent />);
    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });
});