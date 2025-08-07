/**
 * useMobileOptimizations Hook
 * Provides mobile-specific optimizations including touch gestures, keyboard handling,
 * performance optimizations, and device-specific adaptations
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useMotionValue, useTransform, animate } from 'framer-motion';

/**
 * Touch Gesture Hook
 * Handles swipe gestures, pinch-to-zoom, and touch interactions
 */
export function useTouchGestures({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onPinch,
  threshold = 50,
  enabled = true
}) {
  const [isGesturing, setIsGesturing] = useState(false);
  const [gestureStart, setGestureStart] = useState(null);
  const [initialDistance, setInitialDistance] = useState(null);

  const calculateDistance = useCallback((touches) => {
    const touch1 = touches[0];
    const touch2 = touches[1];
    return Math.sqrt(
      Math.pow(touch2.clientX - touch1.clientX, 2) +
      Math.pow(touch2.clientY - touch1.clientY, 2)
    );
  }, []);

  const handleTouchStart = useCallback((event) => {
    if (!enabled) return;

    setIsGesturing(true);
    
    if (event.touches.length === 1) {
      // Single touch - start swipe detection
      setGestureStart({
        x: event.touches[0].clientX,
        y: event.touches[0].clientY,
        timestamp: Date.now()
      });
    } else if (event.touches.length === 2) {
      // Two touches - start pinch detection
      setInitialDistance(calculateDistance(event.touches));
    }
  }, [enabled, calculateDistance]);

  const handleTouchMove = useCallback((event) => {
    if (!enabled || !isGesturing) return;

    if (event.touches.length === 2 && initialDistance && onPinch) {
      // Handle pinch gesture
      const currentDistance = calculateDistance(event.touches);
      const scale = currentDistance / initialDistance;
      onPinch(scale);
    }
  }, [enabled, isGesturing, initialDistance, calculateDistance, onPinch]);

  const handleTouchEnd = useCallback((event) => {
    if (!enabled || !gestureStart) return;

    setIsGesturing(false);
    
    if (event.changedTouches.length === 1) {
      const endTouch = event.changedTouches[0];
      const deltaX = endTouch.clientX - gestureStart.x;
      const deltaY = endTouch.clientY - gestureStart.y;
      const deltaTime = Date.now() - gestureStart.timestamp;
      
      // Only trigger if gesture is fast enough (within 500ms) and exceeds threshold
      if (deltaTime < 500) {
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
          // Horizontal swipe
          if (Math.abs(deltaX) > threshold) {
            if (deltaX > 0 && onSwipeRight) {
              onSwipeRight();
            } else if (deltaX < 0 && onSwipeLeft) {
              onSwipeLeft();
            }
          }
        } else {
          // Vertical swipe
          if (Math.abs(deltaY) > threshold) {
            if (deltaY > 0 && onSwipeDown) {
              onSwipeDown();
            } else if (deltaY < 0 && onSwipeUp) {
              onSwipeUp();
            }
          }
        }
      }
    }
    
    setGestureStart(null);
    setInitialDistance(null);
  }, [enabled, gestureStart, threshold, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown]);

  return {
    touchHandlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd
    },
    isGesturing
  };
}

/**
 * Mobile Keyboard Hook
 * Handles virtual keyboard appearance/disappearance and input optimization
 */
export function useMobileKeyboard() {
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const [keyboardHeight, setKeyboardHeight] = useState(0);
  const [viewportHeight, setViewportHeight] = useState(window.innerHeight);
  const originalViewportHeight = useRef(window.innerHeight);

  useEffect(() => {
    const handleResize = () => {
      const currentHeight = window.innerHeight;
      const heightDifference = originalViewportHeight.current - currentHeight;
      
      // Keyboard is likely visible if viewport height decreased significantly
      if (heightDifference > 150) {
        setKeyboardVisible(true);
        setKeyboardHeight(heightDifference);
      } else {
        setKeyboardVisible(false);
        setKeyboardHeight(0);
      }
      
      setViewportHeight(currentHeight);
    };

    const handleFocusIn = (event) => {
      // Input elements that trigger virtual keyboard
      const inputTypes = ['input', 'textarea', 'select'];
      if (inputTypes.includes(event.target.tagName.toLowerCase())) {
        // Scroll element into view with some padding
        setTimeout(() => {
          event.target.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
        }, 300); // Wait for keyboard animation
      }
    };

    const handleFocusOut = () => {
      // Reset scroll position when keyboard hides
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }, 300);
    };

    window.addEventListener('resize', handleResize);
    document.addEventListener('focusin', handleFocusIn);
    document.addEventListener('focusout', handleFocusOut);

    return () => {
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('focusin', handleFocusIn);
      document.removeEventListener('focusout', handleFocusOut);
    };
  }, []);

  const adjustForKeyboard = useCallback((element) => {
    if (keyboardVisible && element) {
      const rect = element.getBoundingClientRect();
      const availableHeight = viewportHeight;
      
      if (rect.bottom > availableHeight) {
        const scrollAmount = rect.bottom - availableHeight + 20; // 20px padding
        window.scrollBy({ top: scrollAmount, behavior: 'smooth' });
      }
    }
  }, [keyboardVisible, viewportHeight]);

  return {
    keyboardVisible,
    keyboardHeight,
    viewportHeight,
    adjustForKeyboard
  };
}

/**
 * Device Detection Hook
 * Detects device type, capabilities, and performance characteristics
 */
export function useDeviceDetection() {
  const [deviceInfo, setDeviceInfo] = useState({
    type: 'desktop', // 'mobile', 'tablet', 'desktop'
    os: 'unknown', // 'ios', 'android', 'windows', 'macos', 'linux'
    browser: 'unknown',
    touchSupport: false,
    screenSize: 'large', // 'small', 'medium', 'large'
    pixelRatio: 1,
    connectionSpeed: 'fast', // 'slow', 'medium', 'fast'
    reducedMotion: false,
    darkMode: false
  });

  useEffect(() => {
    const detectDevice = () => {
      const userAgent = navigator.userAgent.toLowerCase();
      const screenWidth = window.screen.width;
      const pixelRatio = window.devicePixelRatio || 1;
      
      // Device type detection
      let type = 'desktop';
      if (screenWidth <= 768) {
        type = 'mobile';
      } else if (screenWidth <= 1024) {
        type = 'tablet';
      }

      // OS detection
      let os = 'unknown';
      if (userAgent.includes('iphone') || userAgent.includes('ipad')) {
        os = 'ios';
      } else if (userAgent.includes('android')) {
        os = 'android';
      } else if (userAgent.includes('windows')) {
        os = 'windows';
      } else if (userAgent.includes('mac')) {
        os = 'macos';
      } else if (userAgent.includes('linux')) {
        os = 'linux';
      }

      // Browser detection
      let browser = 'unknown';
      if (userAgent.includes('chrome')) {
        browser = 'chrome';
      } else if (userAgent.includes('firefox')) {
        browser = 'firefox';
      } else if (userAgent.includes('safari')) {
        browser = 'safari';
      } else if (userAgent.includes('edge')) {
        browser = 'edge';
      }

      // Screen size classification
      let screenSize = 'large';
      if (screenWidth <= 640) {
        screenSize = 'small';
      } else if (screenWidth <= 1024) {
        screenSize = 'medium';
      }

      // Connection speed estimation
      let connectionSpeed = 'fast';
      if (navigator.connection) {
        const connection = navigator.connection;
        if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
          connectionSpeed = 'slow';
        } else if (connection.effectiveType === '3g') {
          connectionSpeed = 'medium';
        }
      }

      // Accessibility preferences
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

      setDeviceInfo({
        type,
        os,
        browser,
        touchSupport: 'ontouchstart' in window,
        screenSize,
        pixelRatio,
        connectionSpeed,
        reducedMotion,
        darkMode
      });
    };

    detectDevice();

    // Listen for changes
    const mediaQueries = [
      window.matchMedia('(prefers-reduced-motion: reduce)'),
      window.matchMedia('(prefers-color-scheme: dark)')
    ];

    const handleChange = () => detectDevice();
    
    mediaQueries.forEach(mq => mq.addEventListener('change', handleChange));
    window.addEventListener('resize', handleChange);

    return () => {
      mediaQueries.forEach(mq => mq.removeEventListener('change', handleChange));
      window.removeEventListener('resize', handleChange);
    };
  }, []);

  return deviceInfo;
}

/**
 * Performance Optimization Hook
 * Provides performance monitoring and optimization utilities
 */
export function usePerformanceOptimization() {
  const [performanceMetrics, setPerformanceMetrics] = useState({
    fps: 60,
    memoryUsage: 0,
    renderTime: 0,
    isLowPerformance: false
  });

  const frameTimeRef = useRef([]);
  const lastFrameTime = useRef(performance.now());
  const animationFrameId = useRef(null);

  const measurePerformance = useCallback(() => {
    const now = performance.now();
    const frameTime = now - lastFrameTime.current;
    lastFrameTime.current = now;

    // Keep track of last 60 frame times
    frameTimeRef.current.push(frameTime);
    if (frameTimeRef.current.length > 60) {
      frameTimeRef.current.shift();
    }

    // Calculate average FPS
    const avgFrameTime = frameTimeRef.current.reduce((a, b) => a + b, 0) / frameTimeRef.current.length;
    const fps = Math.round(1000 / avgFrameTime);

    // Memory usage (if available)
    let memoryUsage = 0;
    if (performance.memory) {
      memoryUsage = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024); // MB
    }

    // Determine if device is low performance
    const isLowPerformance = fps < 30 || memoryUsage > 100;

    setPerformanceMetrics({
      fps,
      memoryUsage,
      renderTime: avgFrameTime,
      isLowPerformance
    });

    animationFrameId.current = requestAnimationFrame(measurePerformance);
  }, []);

  useEffect(() => {
    animationFrameId.current = requestAnimationFrame(measurePerformance);

    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [measurePerformance]);

  const optimizeForPerformance = useCallback((options = {}) => {
    const {
      reduceAnimations = performanceMetrics.isLowPerformance,
      simplifyUI = performanceMetrics.isLowPerformance,
      throttleUpdates = performanceMetrics.isLowPerformance
    } = options;

    return {
      shouldReduceAnimations: reduceAnimations,
      shouldSimplifyUI: simplifyUI,
      shouldThrottleUpdates: throttleUpdates,
      animationDuration: reduceAnimations ? 0.1 : 0.3,
      updateInterval: throttleUpdates ? 100 : 16 // ms
    };
  }, [performanceMetrics.isLowPerformance]);

  return {
    performanceMetrics,
    optimizeForPerformance
  };
}

/**
 * Haptic Feedback Hook
 * Provides haptic feedback for supported devices
 */
export function useHapticFeedback() {
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    setIsSupported('vibrate' in navigator);
  }, []);

  const triggerHaptic = useCallback((type = 'light') => {
    if (!isSupported) return;

    const patterns = {
      light: [10],
      medium: [20],
      heavy: [30],
      success: [10, 50, 10],
      error: [50, 50, 50],
      warning: [20, 20, 20]
    };

    const pattern = patterns[type] || patterns.light;
    navigator.vibrate(pattern);
  }, [isSupported]);

  return {
    isSupported,
    triggerHaptic
  };
}

/**
 * Orientation Hook
 * Handles device orientation changes and provides orientation-specific optimizations
 */
export function useOrientation() {
  const [orientation, setOrientation] = useState({
    angle: 0,
    type: 'portrait-primary', // 'portrait-primary', 'portrait-secondary', 'landscape-primary', 'landscape-secondary'
    isPortrait: true,
    isLandscape: false
  });

  useEffect(() => {
    const updateOrientation = () => {
      const angle = screen.orientation?.angle || window.orientation || 0;
      const type = screen.orientation?.type || 'portrait-primary';
      const isPortrait = type.includes('portrait');
      const isLandscape = type.includes('landscape');

      setOrientation({
        angle,
        type,
        isPortrait,
        isLandscape
      });
    };

    updateOrientation();

    const handleOrientationChange = () => {
      // Small delay to ensure screen dimensions are updated
      setTimeout(updateOrientation, 100);
    };

    if (screen.orientation) {
      screen.orientation.addEventListener('change', handleOrientationChange);
    } else {
      window.addEventListener('orientationchange', handleOrientationChange);
    }

    return () => {
      if (screen.orientation) {
        screen.orientation.removeEventListener('change', handleOrientationChange);
      } else {
        window.removeEventListener('orientationchange', handleOrientationChange);
      }
    };
  }, []);

  const lockOrientation = useCallback(async (orientationType) => {
    if (screen.orientation && screen.orientation.lock) {
      try {
        await screen.orientation.lock(orientationType);
        return true;
      } catch (error) {
        console.warn('Orientation lock failed:', error);
        return false;
      }
    }
    return false;
  }, []);

  const unlockOrientation = useCallback(() => {
    if (screen.orientation && screen.orientation.unlock) {
      screen.orientation.unlock();
    }
  }, []);

  return {
    orientation,
    lockOrientation,
    unlockOrientation
  };
}

/**
 * Safe Area Hook
 * Handles safe area insets for devices with notches, rounded corners, etc.
 */
export function useSafeArea() {
  const [safeArea, setSafeArea] = useState({
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  });

  useEffect(() => {
    const updateSafeArea = () => {
      const computedStyle = getComputedStyle(document.documentElement);
      
      setSafeArea({
        top: parseInt(computedStyle.getPropertyValue('env(safe-area-inset-top)') || '0'),
        right: parseInt(computedStyle.getPropertyValue('env(safe-area-inset-right)') || '0'),
        bottom: parseInt(computedStyle.getPropertyValue('env(safe-area-inset-bottom)') || '0'),
        left: parseInt(computedStyle.getPropertyValue('env(safe-area-inset-left)') || '0')
      });
    };

    updateSafeArea();
    window.addEventListener('resize', updateSafeArea);

    return () => {
      window.removeEventListener('resize', updateSafeArea);
    };
  }, []);

  const getSafeAreaStyle = useCallback((options = {}) => {
    const { 
      includePadding = true, 
      includeMargin = false,
      sides = ['top', 'right', 'bottom', 'left']
    } = options;

    const style = {};

    if (includePadding) {
      sides.forEach(side => {
        if (safeArea[side] > 0) {
          style[`padding${side.charAt(0).toUpperCase() + side.slice(1)}`] = `${safeArea[side]}px`;
        }
      });
    }

    if (includeMargin) {
      sides.forEach(side => {
        if (safeArea[side] > 0) {
          style[`margin${side.charAt(0).toUpperCase() + side.slice(1)}`] = `${safeArea[side]}px`;
        }
      });
    }

    return style;
  }, [safeArea]);

  return {
    safeArea,
    getSafeAreaStyle
  };
}

/**
 * Main Mobile Optimizations Hook
 * Combines all mobile optimization hooks into a single interface
 */
export function useMobileOptimizations(options = {}) {
  const {
    enableTouchGestures = true,
    enableKeyboardOptimization = true,
    enablePerformanceMonitoring = true,
    enableHapticFeedback = true,
    enableOrientationHandling = true,
    enableSafeAreaHandling = true
  } = options;

  const deviceInfo = useDeviceDetection();
  
  const touchGestures = useTouchGestures({
    enabled: enableTouchGestures && deviceInfo.touchSupport,
    ...options.touchGestures
  });

  const keyboard = useMobileKeyboard();
  const performance = usePerformanceOptimization();
  const haptic = useHapticFeedback();
  const orientation = useOrientation();
  const safeArea = useSafeArea();

  // Determine if we should use mobile optimizations
  const isMobile = deviceInfo.type === 'mobile';
  const isTablet = deviceInfo.type === 'tablet';
  const isTouchDevice = deviceInfo.touchSupport;
  const isLowPerformance = performance.performanceMetrics.isLowPerformance;

  const optimizations = performance.optimizeForPerformance({
    reduceAnimations: isLowPerformance || deviceInfo.reducedMotion,
    simplifyUI: isLowPerformance || deviceInfo.connectionSpeed === 'slow',
    throttleUpdates: isLowPerformance
  });

  return {
    // Device information
    deviceInfo,
    isMobile,
    isTablet,
    isTouchDevice,
    isLowPerformance,

    // Feature hooks
    touchGestures: enableTouchGestures ? touchGestures : null,
    keyboard: enableKeyboardOptimization ? keyboard : null,
    performance: enablePerformanceMonitoring ? performance : null,
    haptic: enableHapticFeedback ? haptic : null,
    orientation: enableOrientationHandling ? orientation : null,
    safeArea: enableSafeAreaHandling ? safeArea : null,

    // Optimization settings
    optimizations,

    // Utility functions
    shouldReduceAnimations: optimizations.shouldReduceAnimations,
    shouldSimplifyUI: optimizations.shouldSimplifyUI,
    shouldThrottleUpdates: optimizations.shouldThrottleUpdates,
    animationDuration: optimizations.animationDuration,
    updateInterval: optimizations.updateInterval
  };
}

export default useMobileOptimizations;