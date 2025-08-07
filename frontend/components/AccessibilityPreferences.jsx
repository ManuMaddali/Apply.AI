/**
 * Accessibility Preferences Component
 * Provides user controls for accessibility settings including reduced motion,
 * high contrast, large text, and color-blind friendly options
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings,
  Eye,
  Type,
  Palette,
  Volume2,
  Keyboard,
  Monitor,
  Sun,
  Moon,
  Contrast,
  ZoomIn,
  MousePointer,
  Headphones,
  X,
  Check,
  RotateCcw
} from 'lucide-react';
import { Button } from './ui/button';
import { 
  useAccessibilityPreferences, 
  useFocusTrap, 
  useScreenReaderAnnouncement 
} from '../lib/accessibility';

/**
 * Individual preference control component
 */
function PreferenceControl({ 
  id,
  title, 
  description, 
  icon: Icon, 
  value, 
  onChange, 
  type = 'toggle',
  options = [],
  disabled = false 
}) {
  const announce = useScreenReaderAnnouncement();

  const handleChange = (newValue) => {
    onChange(newValue);
    announce(`${title} ${type === 'toggle' ? (newValue ? 'enabled' : 'disabled') : `set to ${newValue}`}`);
  };

  return (
    <div className="flex items-start space-x-4 p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
      <div className="flex-shrink-0 p-2 bg-blue-50 rounded-lg">
        <Icon className="w-5 h-5 text-blue-600" aria-hidden="true" />
      </div>
      
      <div className="flex-grow min-w-0">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-gray-900">{title}</h3>
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          </div>
          
          <div className="flex-shrink-0 ml-4">
            {type === 'toggle' && (
              <button
                id={id}
                role="switch"
                aria-checked={value}
                aria-labelledby={`${id}-label`}
                aria-describedby={`${id}-description`}
                disabled={disabled}
                onClick={() => handleChange(!value)}
                className={`
                  relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                  ${value ? 'bg-blue-600' : 'bg-gray-200'}
                  ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                `}
              >
                <span
                  className={`
                    inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                    ${value ? 'translate-x-6' : 'translate-x-1'}
                  `}
                />
                <span className="sr-only">
                  {value ? 'Disable' : 'Enable'} {title}
                </span>
              </button>
            )}
            
            {type === 'select' && (
              <select
                id={id}
                value={value}
                onChange={(e) => handleChange(e.target.value)}
                disabled={disabled}
                aria-labelledby={`${id}-label`}
                aria-describedby={`${id}-description`}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {options.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            )}
            
            {type === 'range' && (
              <div className="flex items-center space-x-3">
                <input
                  id={id}
                  type="range"
                  min={options.min || 0}
                  max={options.max || 100}
                  step={options.step || 1}
                  value={value}
                  onChange={(e) => handleChange(Number(e.target.value))}
                  disabled={disabled}
                  aria-labelledby={`${id}-label`}
                  aria-describedby={`${id}-description`}
                  className="w-20 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-600 min-w-[3rem]">
                  {value}{options.unit || ''}
                </span>
              </div>
            )}
          </div>
        </div>
        
        {/* Hidden labels for screen readers */}
        <div id={`${id}-label`} className="sr-only">{title}</div>
        <div id={`${id}-description`} className="sr-only">{description}</div>
      </div>
    </div>
  );
}

/**
 * Preference category section
 */
function PreferenceCategory({ title, description, children, icon: Icon }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-3 pb-2 border-b border-gray-200">
        {Icon && <Icon className="w-5 h-5 text-gray-600" aria-hidden="true" />}
        <div>
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          {description && (
            <p className="text-sm text-gray-600">{description}</p>
          )}
        </div>
      </div>
      <div className="space-y-3">
        {children}
      </div>
    </div>
  );
}

/**
 * Main Accessibility Preferences Panel
 */
export function AccessibilityPreferencesPanel({ 
  isOpen, 
  onClose,
  className = '' 
}) {
  const [preferences, updatePreferences] = useAccessibilityPreferences();
  const [hasChanges, setHasChanges] = useState(false);
  const [originalPreferences, setOriginalPreferences] = useState(preferences);
  
  const containerRef = useFocusTrap(isOpen, { 
    restoreFocus: true, 
    escapeDeactivates: true 
  });
  const announce = useScreenReaderAnnouncement();

  // Track changes
  useEffect(() => {
    if (isOpen) {
      setOriginalPreferences(preferences);
      setHasChanges(false);
    }
  }, [isOpen, preferences]);

  useEffect(() => {
    const changed = JSON.stringify(preferences) !== JSON.stringify(originalPreferences);
    setHasChanges(changed);
  }, [preferences, originalPreferences]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape' && isOpen) {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      announce('Accessibility preferences panel opened');
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, announce]);

  const handleClose = () => {
    if (hasChanges) {
      announce('Accessibility preferences saved');
    }
    onClose();
  };

  const handleReset = () => {
    const defaultPreferences = {
      reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      highContrast: window.matchMedia('(prefers-contrast: high)').matches,
      largeText: false,
      screenReaderOptimized: false,
      keyboardNavigation: true,
      colorBlindFriendly: false,
      focusIndicators: true,
      soundEnabled: true,
      autoplay: false
    };
    
    updatePreferences(defaultPreferences);
    announce('Accessibility preferences reset to defaults');
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
      onClick={(e) => e.target === e.currentTarget && handleClose()}
    >
      <motion.div
        ref={containerRef}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.2 }}
        className={`
          bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden
          ${className}
        `}
        role="dialog"
        aria-modal="true"
        aria-labelledby="accessibility-preferences-title"
        aria-describedby="accessibility-preferences-description"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h1 
              id="accessibility-preferences-title" 
              className="text-xl font-semibold text-gray-900"
            >
              Accessibility Preferences
            </h1>
            <p 
              id="accessibility-preferences-description"
              className="text-sm text-gray-600 mt-1"
            >
              Customize your experience for better accessibility
            </p>
          </div>
          
          <button
            onClick={handleClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Close accessibility preferences"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div className="space-y-8">
            {/* Visual Preferences */}
            <PreferenceCategory
              title="Visual"
              description="Adjust visual elements for better readability"
              icon={Eye}
            >
              <PreferenceControl
                id="high-contrast"
                title="High Contrast Mode"
                description="Increase contrast between text and background colors"
                icon={Contrast}
                value={preferences.highContrast}
                onChange={(value) => updatePreferences({ highContrast: value })}
              />
              
              <PreferenceControl
                id="large-text"
                title="Large Text"
                description="Increase text size throughout the application"
                icon={Type}
                value={preferences.largeText}
                onChange={(value) => updatePreferences({ largeText: value })}
              />
              
              <PreferenceControl
                id="color-blind-friendly"
                title="Color-Blind Friendly"
                description="Use patterns and symbols in addition to colors"
                icon={Palette}
                value={preferences.colorBlindFriendly || false}
                onChange={(value) => updatePreferences({ colorBlindFriendly: value })}
              />
              
              <PreferenceControl
                id="focus-indicators"
                title="Enhanced Focus Indicators"
                description="Show prominent focus outlines for keyboard navigation"
                icon={MousePointer}
                value={preferences.focusIndicators !== false}
                onChange={(value) => updatePreferences({ focusIndicators: value })}
              />
            </PreferenceCategory>

            {/* Motion Preferences */}
            <PreferenceCategory
              title="Motion & Animation"
              description="Control animations and motion effects"
              icon={Monitor}
            >
              <PreferenceControl
                id="reduced-motion"
                title="Reduce Motion"
                description="Minimize animations and transitions"
                icon={RotateCcw}
                value={preferences.reducedMotion}
                onChange={(value) => updatePreferences({ reducedMotion: value })}
              />
              
              <PreferenceControl
                id="autoplay"
                title="Disable Autoplay"
                description="Prevent videos and animations from playing automatically"
                icon={Monitor}
                value={preferences.autoplay !== false}
                onChange={(value) => updatePreferences({ autoplay: !value })}
              />
            </PreferenceCategory>

            {/* Navigation Preferences */}
            <PreferenceCategory
              title="Navigation"
              description="Customize navigation and interaction methods"
              icon={Keyboard}
            >
              <PreferenceControl
                id="keyboard-navigation"
                title="Enhanced Keyboard Navigation"
                description="Enable advanced keyboard shortcuts and navigation"
                icon={Keyboard}
                value={preferences.keyboardNavigation}
                onChange={(value) => updatePreferences({ keyboardNavigation: value })}
              />
              
              <PreferenceControl
                id="screen-reader-optimized"
                title="Screen Reader Optimizations"
                description="Optimize interface for screen reader users"
                icon={Headphones}
                value={preferences.screenReaderOptimized}
                onChange={(value) => updatePreferences({ screenReaderOptimized: value })}
              />
            </PreferenceCategory>

            {/* Audio Preferences */}
            <PreferenceCategory
              title="Audio"
              description="Control sound and audio feedback"
              icon={Volume2}
            >
              <PreferenceControl
                id="sound-enabled"
                title="Sound Effects"
                description="Enable audio feedback for interactions"
                icon={Volume2}
                value={preferences.soundEnabled !== false}
                onChange={(value) => updatePreferences({ soundEnabled: value })}
              />
            </PreferenceCategory>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={handleReset}
            className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset to Defaults</span>
          </button>
          
          <div className="flex items-center space-x-3">
            {hasChanges && (
              <span className="text-sm text-green-600 flex items-center">
                <Check className="w-4 h-4 mr-1" />
                Changes saved automatically
              </span>
            )}
            
            <Button
              onClick={handleClose}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Done
            </Button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

/**
 * Accessibility Preferences Trigger Button
 */
export function AccessibilityPreferencesTrigger({ 
  onClick,
  className = '',
  variant = 'outline' 
}) {
  return (
    <button
      onClick={onClick}
      className={`
        flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        ${variant === 'outline' 
          ? 'border border-gray-300 text-gray-700 hover:bg-gray-50' 
          : 'bg-blue-600 text-white hover:bg-blue-700'
        }
        ${className}
      `}
      aria-label="Open accessibility preferences"
      title="Accessibility Preferences"
    >
      <Settings className="w-4 h-4" />
      <span className="hidden sm:inline">Accessibility</span>
    </button>
  );
}

/**
 * Quick Accessibility Controls (for header/toolbar)
 */
export function QuickAccessibilityControls({ className = '' }) {
  const [preferences, updatePreferences] = useAccessibilityPreferences();
  const announce = useScreenReaderAnnouncement();

  const toggleHighContrast = () => {
    const newValue = !preferences.highContrast;
    updatePreferences({ highContrast: newValue });
    announce(`High contrast mode ${newValue ? 'enabled' : 'disabled'}`);
  };

  const toggleLargeText = () => {
    const newValue = !preferences.largeText;
    updatePreferences({ largeText: newValue });
    announce(`Large text ${newValue ? 'enabled' : 'disabled'}`);
  };

  const toggleReducedMotion = () => {
    const newValue = !preferences.reducedMotion;
    updatePreferences({ reducedMotion: newValue });
    announce(`Reduced motion ${newValue ? 'enabled' : 'disabled'}`);
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`} role="toolbar" aria-label="Quick accessibility controls">
      <button
        onClick={toggleHighContrast}
        className={`
          p-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500
          ${preferences.highContrast 
            ? 'bg-blue-600 text-white' 
            : 'text-gray-600 hover:bg-gray-100'
          }
        `}
        aria-label={`${preferences.highContrast ? 'Disable' : 'Enable'} high contrast mode`}
        title="Toggle High Contrast"
      >
        <Contrast className="w-4 h-4" />
      </button>
      
      <button
        onClick={toggleLargeText}
        className={`
          p-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500
          ${preferences.largeText 
            ? 'bg-blue-600 text-white' 
            : 'text-gray-600 hover:bg-gray-100'
          }
        `}
        aria-label={`${preferences.largeText ? 'Disable' : 'Enable'} large text`}
        title="Toggle Large Text"
      >
        <ZoomIn className="w-4 h-4" />
      </button>
      
      <button
        onClick={toggleReducedMotion}
        className={`
          p-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500
          ${preferences.reducedMotion 
            ? 'bg-blue-600 text-white' 
            : 'text-gray-600 hover:bg-gray-100'
          }
        `}
        aria-label={`${preferences.reducedMotion ? 'Disable' : 'Enable'} reduced motion`}
        title="Toggle Reduced Motion"
      >
        <RotateCcw className="w-4 h-4" />
      </button>
    </div>
  );
}

export default {
  AccessibilityPreferencesPanel,
  AccessibilityPreferencesTrigger,
  QuickAccessibilityControls,
  PreferenceControl,
  PreferenceCategory
};