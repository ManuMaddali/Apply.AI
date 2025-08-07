/**
 * Mobile Performance Optimization Utilities
 * Provides performance optimizations specifically for mobile devices
 */

/**
 * Debounce function for touch events and frequent updates
 */
export function debounce(func, wait, immediate = false) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func(...args);
  };
}

/**
 * Throttle function for scroll and resize events
 */
export function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Intersection Observer for lazy loading and viewport detection
 */
export class MobileIntersectionObserver {
  constructor(options = {}) {
    this.options = {
      root: null,
      rootMargin: '50px',
      threshold: 0.1,
      ...options
    };
    
    this.observer = new IntersectionObserver(
      this.handleIntersection.bind(this),
      this.options
    );
    
    this.callbacks = new Map();
  }

  observe(element, callback) {
    this.callbacks.set(element, callback);
    this.observer.observe(element);
  }

  unobserve(element) {
    this.callbacks.delete(element);
    this.observer.unobserve(element);
  }

  handleIntersection(entries) {
    entries.forEach(entry => {
      const callback = this.callbacks.get(entry.target);
      if (callback) {
        callback(entry);
      }
    });
  }

  disconnect() {
    this.observer.disconnect();
    this.callbacks.clear();
  }
}

/**
 * Image lazy loading with mobile optimization
 */
export class MobileLazyLoader {
  constructor() {
    this.observer = new MobileIntersectionObserver({
      rootMargin: '100px' // Load images 100px before they come into view
    });
    
    this.loadedImages = new Set();
  }

  loadImage(img) {
    return new Promise((resolve, reject) => {
      if (this.loadedImages.has(img.src)) {
        resolve(img);
        return;
      }

      const image = new Image();
      
      image.onload = () => {
        // Use requestAnimationFrame to ensure smooth transition
        requestAnimationFrame(() => {
          img.src = image.src;
          img.classList.add('loaded');
          this.loadedImages.add(img.src);
          resolve(img);
        });
      };
      
      image.onerror = reject;
      
      // Load appropriate image size based on device pixel ratio
      const pixelRatio = window.devicePixelRatio || 1;
      const dataSrc = img.dataset.src;
      
      if (dataSrc) {
        // If multiple sizes are available, choose based on pixel ratio
        if (pixelRatio > 2 && img.dataset.srcHigh) {
          image.src = img.dataset.srcHigh;
        } else if (pixelRatio > 1 && img.dataset.srcMedium) {
          image.src = img.dataset.srcMedium;
        } else {
          image.src = dataSrc;
        }
      }
    });
  }

  observe(img) {
    this.observer.observe(img, (entry) => {
      if (entry.isIntersecting) {
        this.loadImage(entry.target).catch(console.error);
        this.observer.unobserve(entry.target);
      }
    });
  }

  observeAll(selector = 'img[data-src]') {
    const images = document.querySelectorAll(selector);
    images.forEach(img => this.observe(img));
  }

  disconnect() {
    this.observer.disconnect();
  }
}

/**
 * Virtual scrolling for large lists on mobile
 */
export class MobileVirtualScroller {
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      itemHeight: 60,
      overscan: 5,
      threshold: 100,
      ...options
    };
    
    this.scrollTop = 0;
    this.containerHeight = 0;
    this.totalItems = 0;
    this.visibleItems = [];
    this.renderCallback = null;
    
    this.init();
  }

  init() {
    this.updateContainerHeight();
    this.bindEvents();
  }

  bindEvents() {
    const throttledScroll = throttle(this.handleScroll.bind(this), 16); // 60fps
    this.container.addEventListener('scroll', throttledScroll, { passive: true });
    
    const throttledResize = throttle(this.updateContainerHeight.bind(this), 100);
    window.addEventListener('resize', throttledResize);
  }

  updateContainerHeight() {
    this.containerHeight = this.container.clientHeight;
    this.calculateVisibleItems();
  }

  handleScroll() {
    this.scrollTop = this.container.scrollTop;
    this.calculateVisibleItems();
  }

  calculateVisibleItems() {
    const { itemHeight, overscan } = this.options;
    
    const startIndex = Math.max(0, Math.floor(this.scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      this.totalItems - 1,
      Math.ceil((this.scrollTop + this.containerHeight) / itemHeight) + overscan
    );
    
    const newVisibleItems = [];
    for (let i = startIndex; i <= endIndex; i++) {
      newVisibleItems.push({
        index: i,
        top: i * itemHeight,
        height: itemHeight
      });
    }
    
    // Only update if items have changed
    if (!this.arraysEqual(this.visibleItems, newVisibleItems)) {
      this.visibleItems = newVisibleItems;
      this.render();
    }
  }

  arraysEqual(a, b) {
    if (a.length !== b.length) return false;
    return a.every((item, index) => item.index === b[index]?.index);
  }

  setData(items, renderCallback) {
    this.totalItems = items.length;
    this.renderCallback = renderCallback;
    
    // Update container height to accommodate all items
    const totalHeight = this.totalItems * this.options.itemHeight;
    this.container.style.height = `${totalHeight}px`;
    
    this.calculateVisibleItems();
  }

  render() {
    if (this.renderCallback) {
      this.renderCallback(this.visibleItems);
    }
  }

  scrollToIndex(index) {
    const targetScrollTop = index * this.options.itemHeight;
    this.container.scrollTo({
      top: targetScrollTop,
      behavior: 'smooth'
    });
  }

  destroy() {
    // Remove event listeners
    this.container.removeEventListener('scroll', this.handleScroll);
    window.removeEventListener('resize', this.updateContainerHeight);
  }
}

/**
 * Touch-optimized animation utilities
 */
export class MobileAnimationManager {
  constructor() {
    this.activeAnimations = new Set();
    this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.lowPerformance = this.detectLowPerformance();
  }

  detectLowPerformance() {
    // Simple heuristics for low-performance devices
    const memory = navigator.deviceMemory || 4; // Default to 4GB if not available
    const cores = navigator.hardwareConcurrency || 4; // Default to 4 cores
    const connection = navigator.connection?.effectiveType || '4g';
    
    return memory < 2 || cores < 4 || ['slow-2g', '2g', '3g'].includes(connection);
  }

  createAnimation(element, keyframes, options = {}) {
    // Adjust animation based on device capabilities
    const adjustedOptions = {
      duration: this.reducedMotion ? 0 : (this.lowPerformance ? options.duration * 0.5 : options.duration),
      easing: options.easing || 'ease-out',
      fill: 'forwards',
      ...options
    };

    if (this.reducedMotion) {
      // Skip animation, just apply final state
      const finalKeyframe = keyframes[keyframes.length - 1];
      Object.assign(element.style, finalKeyframe);
      return { finished: Promise.resolve() };
    }

    const animation = element.animate(keyframes, adjustedOptions);
    this.activeAnimations.add(animation);

    animation.finished.finally(() => {
      this.activeAnimations.delete(animation);
    });

    return animation;
  }

  pauseAll() {
    this.activeAnimations.forEach(animation => {
      if (animation.playState === 'running') {
        animation.pause();
      }
    });
  }

  resumeAll() {
    this.activeAnimations.forEach(animation => {
      if (animation.playState === 'paused') {
        animation.play();
      }
    });
  }

  cancelAll() {
    this.activeAnimations.forEach(animation => {
      animation.cancel();
    });
    this.activeAnimations.clear();
  }
}

/**
 * Memory management utilities for mobile
 */
export class MobileMemoryManager {
  constructor() {
    this.cache = new Map();
    this.maxCacheSize = this.calculateMaxCacheSize();
    this.cleanupInterval = null;
    
    this.startCleanupInterval();
    this.bindVisibilityEvents();
  }

  calculateMaxCacheSize() {
    const memory = navigator.deviceMemory || 4;
    // Allocate cache size based on available memory
    if (memory < 2) return 50; // 50 items for low-memory devices
    if (memory < 4) return 100; // 100 items for medium-memory devices
    return 200; // 200 items for high-memory devices
  }

  set(key, value, ttl = 300000) { // 5 minutes default TTL
    // Remove oldest items if cache is full
    if (this.cache.size >= this.maxCacheSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      ttl
    });
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    // Check if item has expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  clear() {
    this.cache.clear();
  }

  cleanup() {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(key);
      }
    }
  }

  startCleanupInterval() {
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 60000); // Cleanup every minute
  }

  bindVisibilityEvents() {
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        // App is in background, perform aggressive cleanup
        this.cleanup();
        
        // Clear non-essential caches
        if (this.cache.size > this.maxCacheSize * 0.5) {
          const keysToDelete = Array.from(this.cache.keys()).slice(0, Math.floor(this.cache.size * 0.3));
          keysToDelete.forEach(key => this.cache.delete(key));
        }
      }
    });
  }

  destroy() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.clear();
  }
}

/**
 * Touch event optimization
 */
export class TouchEventOptimizer {
  constructor() {
    this.touchStartTime = 0;
    this.touchStartPos = { x: 0, y: 0 };
    this.isScrolling = false;
    this.scrollTimeout = null;
  }

  optimizeTouchEvents(element) {
    // Use passive listeners for better scroll performance
    element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
    element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: true });
    element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
    
    // Prevent 300ms click delay on mobile
    element.style.touchAction = 'manipulation';
  }

  handleTouchStart(event) {
    this.touchStartTime = Date.now();
    this.touchStartPos = {
      x: event.touches[0].clientX,
      y: event.touches[0].clientY
    };
    this.isScrolling = false;
  }

  handleTouchMove(event) {
    if (!this.isScrolling) {
      const touch = event.touches[0];
      const deltaX = Math.abs(touch.clientX - this.touchStartPos.x);
      const deltaY = Math.abs(touch.clientY - this.touchStartPos.y);
      
      // Determine if user is scrolling
      if (deltaY > deltaX && deltaY > 10) {
        this.isScrolling = true;
      }
    }
    
    // Clear any existing scroll timeout
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }
    
    // Set timeout to detect end of scrolling
    this.scrollTimeout = setTimeout(() => {
      this.isScrolling = false;
    }, 150);
  }

  handleTouchEnd(event) {
    const touchDuration = Date.now() - this.touchStartTime;
    
    // Distinguish between tap and scroll
    if (!this.isScrolling && touchDuration < 200) {
      // This was likely a tap
      this.handleTap(event);
    }
  }

  handleTap(event) {
    // Provide haptic feedback for taps if available
    if (navigator.vibrate) {
      navigator.vibrate(10);
    }
  }
}

/**
 * Battery optimization utilities
 */
export class BatteryOptimizer {
  constructor() {
    this.batteryLevel = 1;
    this.isCharging = true;
    this.lowBatteryMode = false;
    
    this.initBatteryAPI();
  }

  async initBatteryAPI() {
    if ('getBattery' in navigator) {
      try {
        const battery = await navigator.getBattery();
        this.batteryLevel = battery.level;
        this.isCharging = battery.charging;
        this.updateLowBatteryMode();
        
        battery.addEventListener('levelchange', () => {
          this.batteryLevel = battery.level;
          this.updateLowBatteryMode();
        });
        
        battery.addEventListener('chargingchange', () => {
          this.isCharging = battery.charging;
          this.updateLowBatteryMode();
        });
      } catch (error) {
        console.warn('Battery API not available:', error);
      }
    }
  }

  updateLowBatteryMode() {
    // Enable low battery mode when battery is below 20% and not charging
    this.lowBatteryMode = this.batteryLevel < 0.2 && !this.isCharging;
  }

  getOptimizationSettings() {
    return {
      reduceAnimations: this.lowBatteryMode,
      lowerFrameRate: this.lowBatteryMode,
      disableBackgroundTasks: this.lowBatteryMode,
      simplifyUI: this.lowBatteryMode,
      batteryLevel: this.batteryLevel,
      isCharging: this.isCharging,
      lowBatteryMode: this.lowBatteryMode
    };
  }
}

// Export singleton instances for common use
export const mobileIntersectionObserver = new MobileIntersectionObserver();
export const mobileLazyLoader = new MobileLazyLoader();
export const mobileAnimationManager = new MobileAnimationManager();
export const mobileMemoryManager = new MobileMemoryManager();
export const touchEventOptimizer = new TouchEventOptimizer();
export const batteryOptimizer = new BatteryOptimizer();

// Utility functions
export const isMobileDevice = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

export const isLowEndDevice = () => {
  const memory = navigator.deviceMemory || 4;
  const cores = navigator.hardwareConcurrency || 4;
  return memory < 2 || cores < 4;
};

export const getOptimalImageSize = (baseWidth, baseHeight) => {
  const pixelRatio = window.devicePixelRatio || 1;
  const screenWidth = window.screen.width;
  
  // Don't load images larger than screen width
  const maxWidth = Math.min(baseWidth * pixelRatio, screenWidth * pixelRatio);
  const aspectRatio = baseHeight / baseWidth;
  
  return {
    width: Math.round(maxWidth),
    height: Math.round(maxWidth * aspectRatio)
  };
};

export const prefersReducedMotion = () => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

export const isDarkMode = () => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
};

export default {
  debounce,
  throttle,
  MobileIntersectionObserver,
  MobileLazyLoader,
  MobileVirtualScroller,
  MobileAnimationManager,
  MobileMemoryManager,
  TouchEventOptimizer,
  BatteryOptimizer,
  mobileIntersectionObserver,
  mobileLazyLoader,
  mobileAnimationManager,
  mobileMemoryManager,
  touchEventOptimizer,
  batteryOptimizer,
  isMobileDevice,
  isLowEndDevice,
  getOptimalImageSize,
  prefersReducedMotion,
  isDarkMode
};