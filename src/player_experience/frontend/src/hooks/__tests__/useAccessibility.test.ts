import { renderHook, act } from '@testing-library/react';
import useAccessibility from '../useAccessibility';

// Mock matchMedia
const mockMatchMedia = (matches: boolean) => ({
  matches,
  media: '',
  onchange: null,
  addListener: jest.fn(),
  removeListener: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn(),
});

describe('useAccessibility', () => {
  beforeEach(() => {
    // Mock window.matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation((query) => {
        if (query.includes('prefers-reduced-motion')) {
          return mockMatchMedia(false);
        }
        if (query.includes('prefers-contrast')) {
          return mockMatchMedia(false);
        }
        if (query.includes('prefers-reduced-data')) {
          return mockMatchMedia(false);
        }
        return mockMatchMedia(false);
      }),
    });

    // Mock speechSynthesis
    Object.defineProperty(window, 'speechSynthesis', {
      writable: true,
      value: {},
    });

    // Mock navigator.userAgent
    Object.defineProperty(navigator, 'userAgent', {
      writable: true,
      value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with default preferences', () => {
    const { result } = renderHook(() => useAccessibility());

    expect(result.current.preferences).toEqual({
      reduceMotion: false,
      highContrast: false,
      largeText: false,
      screenReader: true, // true because speechSynthesis is mocked
    });
  });

  it('detects reduced motion preference', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query.includes('prefers-reduced-motion')) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const { result } = renderHook(() => useAccessibility());

    expect(result.current.preferences.reduceMotion).toBe(true);
  });

  it('detects high contrast preference', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query.includes('prefers-contrast')) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const { result } = renderHook(() => useAccessibility());

    expect(result.current.preferences.highContrast).toBe(true);
  });

  it('detects screen reader from user agent', () => {
    Object.defineProperty(navigator, 'userAgent', {
      writable: true,
      value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NVDA/2021.1',
    });

    const { result } = renderHook(() => useAccessibility());

    expect(result.current.preferences.screenReader).toBe(true);
  });

  it('sets focus visible on tab key press', () => {
    const { result } = renderHook(() => useAccessibility());

    expect(result.current.focusVisible).toBe(false);

    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'Tab' });
      document.dispatchEvent(event);
    });

    expect(result.current.focusVisible).toBe(true);
  });

  it('clears focus visible on mouse down', () => {
    const { result } = renderHook(() => useAccessibility());

    // First set focus visible
    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'Tab' });
      document.dispatchEvent(event);
    });

    expect(result.current.focusVisible).toBe(true);

    // Then clear it with mouse down
    act(() => {
      const event = new MouseEvent('mousedown');
      document.dispatchEvent(event);
    });

    expect(result.current.focusVisible).toBe(false);
  });

  it('announces messages to screen readers', () => {
    const { result } = renderHook(() => useAccessibility());

    act(() => {
      result.current.announce('Test announcement');
    });

    // Check that an announcement element was added to the DOM
    const announcements = document.querySelectorAll('[aria-live="polite"]');
    expect(announcements.length).toBeGreaterThan(0);
  });

  it('announces with assertive priority', () => {
    const { result } = renderHook(() => useAccessibility());

    act(() => {
      result.current.announce('Urgent announcement', 'assertive');
    });

    const announcements = document.querySelectorAll('[aria-live="assertive"]');
    expect(announcements.length).toBeGreaterThan(0);
  });

  it('skips to content when target exists', () => {
    // Create a target element
    const target = document.createElement('div');
    target.id = 'main-content';
    target.focus = jest.fn();
    target.scrollIntoView = jest.fn();
    document.body.appendChild(target);

    const { result } = renderHook(() => useAccessibility());

    act(() => {
      result.current.skipToContent('main-content');
    });

    expect(target.focus).toHaveBeenCalled();
    expect(target.scrollIntoView).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'start'
    });

    // Cleanup
    document.body.removeChild(target);
  });

  it('handles arrow navigation correctly', () => {
    const { result } = renderHook(() => useAccessibility());

    const items = [
      { focus: jest.fn() } as unknown as HTMLElement,
      { focus: jest.fn() } as unknown as HTMLElement,
      { focus: jest.fn() } as unknown as HTMLElement,
    ];

    const mockEvent = {
      key: 'ArrowDown',
      preventDefault: jest.fn(),
    } as unknown as KeyboardEvent;

    let newIndex: number;

    act(() => {
      newIndex = result.current.handleArrowNavigation(mockEvent, items, 0);
    });

    expect(mockEvent.preventDefault).toHaveBeenCalled();
    expect(newIndex!).toBe(1);
    expect(items[1].focus).toHaveBeenCalled();
  });

  it('handles Home key in arrow navigation', () => {
    const { result } = renderHook(() => useAccessibility());

    const items = [
      { focus: jest.fn() } as unknown as HTMLElement,
      { focus: jest.fn() } as unknown as HTMLElement,
      { focus: jest.fn() } as unknown as HTMLElement,
    ];

    const mockEvent = {
      key: 'Home',
      preventDefault: jest.fn(),
    } as unknown as KeyboardEvent;

    let newIndex: number;

    act(() => {
      newIndex = result.current.handleArrowNavigation(mockEvent, items, 2);
    });

    expect(mockEvent.preventDefault).toHaveBeenCalled();
    expect(newIndex!).toBe(0);
    expect(items[0].focus).toHaveBeenCalled();
  });

  it('handles Enter key in arrow navigation with callback', () => {
    const { result } = renderHook(() => useAccessibility());
    const onSelect = jest.fn();

    const items = [
      { focus: jest.fn() } as unknown as HTMLElement,
    ];

    const mockEvent = {
      key: 'Enter',
      preventDefault: jest.fn(),
    } as unknown as KeyboardEvent;

    let returnedIndex: number;

    act(() => {
      returnedIndex = result.current.handleArrowNavigation(mockEvent, items, 0, onSelect);
    });

    expect(mockEvent.preventDefault).toHaveBeenCalled();
    expect(onSelect).toHaveBeenCalledWith(0);
    expect(returnedIndex!).toBe(0);
  });
});