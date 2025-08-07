/**
 * useAccessibility Hook
 * Manages accessibility preferences and provides utilities for reduced motion and high contrast
 */

import { useState, useEffect, useCallback } from 'react';

export function useAccessibility() {
  const [preferences, setPreferences] = useState({
    prefersReducedMotion: false,
    prefersHighContrast: false,
    prefersDarkMode: false,
    keyboardNavigation: false,
  });

  // Check for media query preferences
  useEffect(() => {
    const checkPreferences = () => {
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const highContrast = window.matchMedia('(prefers-contrast: high)').matches;
      const darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

      setPreferences(prev => ({
        ...prev,
        prefersReducedMotion: reducedMotion,
        prefersHighContrast: highContrast,
        prefersDarkMode: darkMode,
      }));
    };

    // Initial check
    checkPreferences();

    // Set up media query listeners
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleReducedMotionChange = (e) => {
      setPreferences(prev => ({ ...prev, prefersReducedMotion: e.matches }));
    };

    const handleHighContrastChange = (e) => {
      setPreferences(prev => ({ ...prev, prefersHighContrast: e.matches }));
    };

    const handleDarkModeChange = (e) => {
      setPreferences(prev => ({ ...prev, prefersDarkMode: e.matches }));
    };

    // Add listeners
    reducedMotionQuery.addEventListener('change', handleReducedMotionChange);
    highContrastQuery.addEventListener('change', handleHighContrastChange);
    darkModeQuery.addEventListener('change', handleDarkModeChange);

    // Cleanup
    return () => {
      reducedMotionQuery.removeEventListener('change', handleReducedMotionChange);
      highContrastQuery.removeEventListener('change', handleHighContrastChange);
      darkModeQuery.removeEventListener('change', handleDarkModeChange);
    };
  }, []);

  // Detect keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Tab') {
        setPreferences(prev => ({ ...prev, keyboardNavigation: true }));
        document.body.classList.add('keyboard-navigation-active');
      }
    };

    const handleMouseDown = () => {
      setPreferences(prev => ({ ...prev, keyboardNavigation: false }));
      document.body.classList.remove('keyboard-navigation-active');
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  // Apply accessibility classes to document
  useEffect(() => {
    const { prefersReducedMotion, prefersHighContrast } = preferences;

    if (prefersReducedMotion) {
      document.documentElement.classList.add('motion-reduce');
    } else {
      document.documentElement.classList.remove('motion-reduce');
    }

    if (prefersHighContrast) {
      document.documentElement.classList.add('contrast-high');
    } else {
      document.documentElement.classList.remove('contrast-high');
    }
  }, [preferences]);

  // Utility functions
  const getAnimationProps = useCallback((defaultProps = {}) => {
    if (preferences.prefersReducedMotion) {
      return {
        ...defaultProps,
        animate: defaultProps.animate || {},
        transition: { duration: 0.01 },
        initial: false,
      };
    }
    return defaultProps;
  }, [preferences.prefersReducedMotion]);

  const getTransitionClass = useCallback((defaultClass = '') => {
    if (preferences.prefersReducedMotion) {
      return defaultClass.replace(/transition-\w+/g, 'transition-none');
    }
    return defaultClass;
  }, [preferences.prefersReducedMotion]);

  const getContrastClass = useCallback((defaultClass = '') => {
    if (preferences.prefersHighContrast) {
      return `${defaultClass} contrast-high border-contrast`;
    }
    return defaultClass;
  }, [preferences.prefersHighContrast]);

  const announceToScreenReader = useCallback((message, priority = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    // Remove after announcement
    setTimeout(() => {
      if (document.body.contains(announcement)) {
        document.body.removeChild(announcement);
      }
    }, 1000);
  }, []);

  const createSkipLink = useCallback((targetId, text = 'Skip to main content') => {
    const skipLink = document.createElement('a');
    skipLink.href = `#${targetId}`;
    skipLink.textContent = text;
    skipLink.className = 'skip-link';

    skipLink.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.getElementById(targetId);
      if (target) {
        target.focus();
        target.scrollIntoView({ behavior: preferences.prefersReducedMotion ? 'auto' : 'smooth' });
      }
    });

    return skipLink;
  }, [preferences.prefersReducedMotion]);

  const manageFocus = useCallback({
    trap: (container) => {
      const focusableElements = container.querySelectorAll(
        'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), a[href], [tabindex]:not([tabindex="-1"]), [contenteditable="true"]'
      );
      
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      const handleTabKey = (e) => {
        if (e.key === 'Tab') {
          if (e.shiftKey) {
            if (document.activeElement === firstElement) {
              e.preventDefault();
              lastElement?.focus();
            }
          } else {
            if (document.activeElement === lastElement) {
              e.preventDefault();
              firstElement?.focus();
            }
          }
        }
      };

      container.addEventListener('keydown', handleTabKey);
      firstElement?.focus();

      return () => {
        container.removeEventListener('keydown', handleTabKey);
      };
    },

    restore: (element) => {
      if (element && typeof element.focus === 'function') {
        element.focus();
      }
    },

    moveTo: (element) => {
      if (element && typeof element.focus === 'function') {
        element.focus();
        if (element.scrollIntoView) {
          element.scrollIntoView({ 
            behavior: preferences.prefersReducedMotion ? 'auto' : 'smooth',
            block: 'nearest'
          });
        }
      }
    }
  }, [preferences.prefersReducedMotion]);

  return {
    preferences,
    getAnimationProps,
    getTransitionClass,
    getContrastClass,
    announceToScreenReader,
    createSkipLink,
    manageFocus,
    
    // Convenience flags
    shouldReduceMotion: preferences.prefersReducedMotion,
    shouldIncreaseContrast: preferences.prefersHighContrast,
    isUsingKeyboard: preferences.keyboardNavigation,
    prefersDark: preferences.prefersDarkMode,
  };
}

// Higher-order component for accessibility
export function withAccessibility(Component) {
  return function AccessibleComponent(props) {
    const accessibility = useAccessibility();
    
    return (
      <Component 
        {...props} 
        accessibility={accessibility}
      />
    );
  };
}

// Context for accessibility preferences
import { createContext, useContext } from 'react';

const AccessibilityContext = createContext(null);

export function AccessibilityProvider({ children }) {
  const accessibility = useAccessibility();
  
  return (
    <AccessibilityContext.Provider value={accessibility}>
      {children}
    </AccessibilityContext.Provider>
  );
}

export function useAccessibilityContext() {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibilityContext must be used within an AccessibilityProvider');
  }
  return context;
}

// Utility for creating accessible motion components
export function createAccessibleMotion(MotionComponent) {
  return function AccessibleMotionComponent(props) {
    const { getAnimationProps } = useAccessibility();
    const accessibleProps = getAnimationProps(props);
    
    return <MotionComponent {...accessibleProps} />;
  };
}

// Hook for managing ARIA live regions
export function useAriaLive() {
  const [liveRegion, setLiveRegion] = useState(null);

  useEffect(() => {
    // Create live region if it doesn't exist
    let region = document.getElementById('aria-live-region');
    if (!region) {
      region = document.createElement('div');
      region.id = 'aria-live-region';
      region.setAttribute('aria-live', 'polite');
      region.setAttribute('aria-atomic', 'true');
      region.className = 'sr-only';
      document.body.appendChild(region);
    }
    setLiveRegion(region);

    return () => {
      // Clean up on unmount
      if (region && document.body.contains(region)) {
        document.body.removeChild(region);
      }
    };
  }, []);

  const announce = useCallback((message, priority = 'polite') => {
    if (liveRegion) {
      liveRegion.setAttribute('aria-live', priority);
      liveRegion.textContent = message;
      
      // Clear after announcement
      setTimeout(() => {
        if (liveRegion) {
          liveRegion.textContent = '';
        }
      }, 1000);
    }
  }, [liveRegion]);

  return { announce };
}

export default useAccessibility;