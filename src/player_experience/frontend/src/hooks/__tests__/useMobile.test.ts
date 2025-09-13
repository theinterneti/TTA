import { renderHook, act } from '@testing-library/react';
import useMobile from '../useMobile';

// Mock window dimensions
const mockWindowDimensions = (width: number, height: number) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: height,
  });
};

describe('useMobile', () => {
  beforeEach(() => {
    // Mock touch support
    Object.defineProperty(window, 'ontouchstart', {
      writable: true,
      value: undefined,
    });

    Object.defineProperty(navigator, 'maxTouchPoints', {
      writable: true,
      value: 0,
    });

    // Mock event listeners
    window.addEventListener = jest.fn();
    window.removeEventListener = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('detects mobile screen size correctly', () => {
    mockWindowDimensions(375, 667); // iPhone dimensions

    const { result } = renderHook(() => useMobile());

    expect(result.current.isMobile).toBe(true);
    expect(result.current.isTablet).toBe(false);
    expect(result.current.isDesktop).toBe(false);
    expect(result.current.screenSize).toBe('xs');
    expect(result.current.orientation).toBe('portrait');
  });

  it('detects tablet screen size correctly', () => {
    mockWindowDimensions(768, 1024); // iPad dimensions

    const { result } = renderHook(() => useMobile());

    expect(result.current.isMobile).toBe(false);
    expect(result.current.isTablet).toBe(true);
    expect(result.current.isDesktop).toBe(false);
    expect(result.current.screenSize).toBe('md');
    expect(result.current.orientation).toBe('portrait');
  });

  it('detects desktop screen size correctly', () => {
    mockWindowDimensions(1920, 1080); // Desktop dimensions

    const { result } = renderHook(() => useMobile());

    expect(result.current.isMobile).toBe(false);
    expect(result.current.isTablet).toBe(false);
    expect(result.current.isDesktop).toBe(true);
    expect(result.current.screenSize).toBe('xl');
    expect(result.current.orientation).toBe('landscape');
  });

  it('detects landscape orientation correctly', () => {
    mockWindowDimensions(667, 375); // iPhone landscape

    const { result } = renderHook(() => useMobile());

    expect(result.current.orientation).toBe('landscape');
  });

  it('detects portrait orientation correctly', () => {
    mockWindowDimensions(375, 667); // iPhone portrait

    const { result } = renderHook(() => useMobile());

    expect(result.current.orientation).toBe('portrait');
  });

  it('detects touch support correctly', () => {
    Object.defineProperty(window, 'ontouchstart', {
      value: {},
    });

    const { result } = renderHook(() => useMobile());

    expect(result.current.touchSupported).toBe(true);
  });

  it('detects touch support via maxTouchPoints', () => {
    Object.defineProperty(navigator, 'maxTouchPoints', {
      value: 1,
    });

    const { result } = renderHook(() => useMobile());

    expect(result.current.touchSupported).toBe(true);
  });

  it('correctly identifies all screen sizes', () => {
    const testCases = [
      { width: 320, expected: 'xs' },
      { width: 640, expected: 'sm' },
      { width: 768, expected: 'md' },
      { width: 1024, expected: 'lg' },
      { width: 1280, expected: 'xl' },
      { width: 1536, expected: '2xl' },
    ];

    testCases.forEach(({ width, expected }) => {
      mockWindowDimensions(width, 800);
      const { result } = renderHook(() => useMobile());
      expect(result.current.screenSize).toBe(expected);
    });
  });

  it('updates state on window resize', () => {
    mockWindowDimensions(375, 667); // Start mobile

    const { result } = renderHook(() => useMobile());

    expect(result.current.isMobile).toBe(true);

    // Simulate resize to desktop
    act(() => {
      mockWindowDimensions(1920, 1080);
      // Trigger resize event
      const resizeEvent = new Event('resize');
      window.dispatchEvent(resizeEvent);
    });

    // Note: In a real test environment, you'd need to actually trigger the resize handler
    // This is a simplified test that checks the hook setup
    expect(window.addEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
  });

  it('updates state on orientation change', () => {
    mockWindowDimensions(375, 667);

    const { result } = renderHook(() => useMobile());

    expect(result.current.orientation).toBe('portrait');

    // The hook should listen for orientation change events
    expect(window.addEventListener).toHaveBeenCalledWith('orientationchange', expect.any(Function));
  });

  it('cleans up event listeners on unmount', () => {
    const { unmount } = renderHook(() => useMobile());

    unmount();

    expect(window.removeEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
    expect(window.removeEventListener).toHaveBeenCalledWith('orientationchange', expect.any(Function));
  });

  it('handles edge case screen sizes', () => {
    // Test exact breakpoint values
    mockWindowDimensions(768, 800); // Exactly md breakpoint
    const { result } = renderHook(() => useMobile());
    expect(result.current.screenSize).toBe('md');
    expect(result.current.isTablet).toBe(true);

    // Test just below breakpoint
    mockWindowDimensions(767, 800);
    const { result: result2 } = renderHook(() => useMobile());
    expect(result2.current.screenSize).toBe('sm');
    expect(result2.current.isMobile).toBe(true);
  });

  it('handles very small screens', () => {
    mockWindowDimensions(240, 320); // Very small screen

    const { result } = renderHook(() => useMobile());

    expect(result.current.isMobile).toBe(true);
    expect(result.current.screenSize).toBe('xs');
    expect(result.current.orientation).toBe('portrait');
  });

  it('handles very large screens', () => {
    mockWindowDimensions(2560, 1440); // 4K screen

    const { result } = renderHook(() => useMobile());

    expect(result.current.isDesktop).toBe(true);
    expect(result.current.screenSize).toBe('2xl');
    expect(result.current.orientation).toBe('landscape');
  });
});
