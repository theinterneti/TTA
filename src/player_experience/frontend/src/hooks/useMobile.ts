import { useState, useEffect } from 'react';

interface MobileState {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  orientation: 'portrait' | 'landscape';
  touchSupported: boolean;
  screenSize: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export const useMobile = (): MobileState => {
  const [mobileState, setMobileState] = useState<MobileState>({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    orientation: 'landscape',
    touchSupported: false,
    screenSize: 'lg',
  });

  useEffect(() => {
    const updateMobileState = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      // Breakpoints matching Tailwind CSS
      const breakpoints = {
        xs: 0,
        sm: 640,
        md: 768,
        lg: 1024,
        xl: 1280,
        '2xl': 1536,
      };

      let screenSize: MobileState['screenSize'] = 'xs';
      if (width >= breakpoints['2xl']) screenSize = '2xl';
      else if (width >= breakpoints.xl) screenSize = 'xl';
      else if (width >= breakpoints.lg) screenSize = 'lg';
      else if (width >= breakpoints.md) screenSize = 'md';
      else if (width >= breakpoints.sm) screenSize = 'sm';

      const isMobile = width < breakpoints.md;
      const isTablet = width >= breakpoints.md && width < breakpoints.lg;
      const isDesktop = width >= breakpoints.lg;
      
      const orientation = height > width ? 'portrait' : 'landscape';
      
      // Check for touch support
      const touchSupported = 
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        // @ts-ignore - for older browsers
        navigator.msMaxTouchPoints > 0;

      setMobileState({
        isMobile,
        isTablet,
        isDesktop,
        orientation,
        touchSupported,
        screenSize,
      });
    };

    // Initial check
    updateMobileState();

    // Listen for resize and orientation changes
    window.addEventListener('resize', updateMobileState);
    window.addEventListener('orientationchange', updateMobileState);

    return () => {
      window.removeEventListener('resize', updateMobileState);
      window.removeEventListener('orientationchange', updateMobileState);
    };
  }, []);

  return mobileState;
};

export default useMobile;