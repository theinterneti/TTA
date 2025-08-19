import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SkipLink from '../SkipLink';

describe('SkipLink', () => {
  beforeEach(() => {
    // Create a target element for the skip link
    const target = document.createElement('div');
    target.id = 'main-content';
    target.tabIndex = -1;
    document.body.appendChild(target);
  });

  afterEach(() => {
    // Clean up
    const target = document.getElementById('main-content');
    if (target) {
      document.body.removeChild(target);
    }
  });

  it('renders skip link with correct text', () => {
    render(
      <SkipLink href="#main-content">
        Skip to main content
      </SkipLink>
    );

    const skipLink = screen.getByText('Skip to main content');
    expect(skipLink).toBeInTheDocument();
    expect(skipLink).toHaveAttribute('href', '#main-content');
  });

  it('is hidden by default but visible on focus', () => {
    render(
      <SkipLink href="#main-content">
        Skip to main content
      </SkipLink>
    );

    const skipLink = screen.getByText('Skip to main content');
    expect(skipLink).toHaveClass('sr-only');
    
    // Focus the skip link
    skipLink.focus();
    expect(skipLink).toHaveClass('focus:not-sr-only');
  });

  it('focuses target element when clicked', () => {
    const mockFocus = jest.fn();
    const mockScrollIntoView = jest.fn();
    
    // Mock the target element
    const target = document.getElementById('main-content');
    if (target) {
      target.focus = mockFocus;
      target.scrollIntoView = mockScrollIntoView;
    }

    render(
      <SkipLink href="#main-content">
        Skip to main content
      </SkipLink>
    );

    const skipLink = screen.getByText('Skip to main content');
    fireEvent.click(skipLink);

    expect(mockFocus).toHaveBeenCalled();
    expect(mockScrollIntoView).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'start'
    });
  });

  it('prevents default link behavior', () => {
    render(
      <SkipLink href="#main-content">
        Skip to main content
      </SkipLink>
    );

    const skipLink = screen.getByText('Skip to main content');
    const clickEvent = new MouseEvent('click', { bubbles: true });
    const preventDefaultSpy = jest.spyOn(clickEvent, 'preventDefault');
    
    fireEvent(skipLink, clickEvent);
    expect(preventDefaultSpy).toHaveBeenCalled();
  });

  it('applies custom className', () => {
    render(
      <SkipLink href="#main-content" className="custom-class">
        Skip to main content
      </SkipLink>
    );

    const skipLink = screen.getByText('Skip to main content');
    expect(skipLink).toHaveClass('custom-class');
  });

  it('has proper accessibility attributes', () => {
    render(
      <SkipLink href="#main-content">
        Skip to main content
      </SkipLink>
    );

    const skipLink = screen.getByText('Skip to main content');
    expect(skipLink).toHaveAttribute('href', '#main-content');
    expect(skipLink).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-blue-500');
  });

  it('handles missing target gracefully', () => {
    // Remove the target element
    const target = document.getElementById('main-content');
    if (target) {
      document.body.removeChild(target);
    }

    render(
      <SkipLink href="#nonexistent">
        Skip to nonexistent
      </SkipLink>
    );

    const skipLink = screen.getByText('Skip to nonexistent');
    
    // Should not throw an error when target doesn't exist
    expect(() => {
      fireEvent.click(skipLink);
    }).not.toThrow();
  });
});