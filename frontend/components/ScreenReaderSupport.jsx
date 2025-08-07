/**
 * Screen Reader Support Components
 * Provides comprehensive screen reader support with ARIA live regions,
 * semantic HTML structure, and dynamic content announcements
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useScreenReaderAnnouncement, useAriaLiveRegion } from '../lib/accessibility';

/**
 * Live Region Component for dynamic announcements
 */
export function LiveRegion({ 
  id = 'main-live-region',
  priority = 'polite',
  atomic = true,
  className = 'sr-only'
}) {
  return (
    <div
      id={id}
      aria-live={priority}
      aria-atomic={atomic}
      className={className}
      style={{
        position: 'absolute',
        width: '1px',
        height: '1px',
        padding: '0',
        margin: '-1px',
        overflow: 'hidden',
        clip: 'rect(0, 0, 0, 0)',
        whiteSpace: 'nowrap',
        border: '0'
      }}
    />
  );
}

/**
 * Processing Status Announcer
 * Announces processing status changes to screen readers
 */
export function ProcessingStatusAnnouncer({ 
  status, 
  progress, 
  currentStep, 
  totalSteps,
  mode 
}) {
  const announce = useScreenReaderAnnouncement();
  const prevStatusRef = useRef(status);
  const prevProgressRef = useRef(progress);

  useEffect(() => {
    const prevStatus = prevStatusRef.current;
    const prevProgress = prevProgressRef.current;

    // Announce status changes
    if (status !== prevStatus) {
      let message = '';
      
      switch (status) {
        case 'idle':
          message = 'Processing ready to start';
          break;
        case 'processing':
          message = `${mode} mode processing started`;
          break;
        case 'completed':
          message = 'Processing completed successfully';
          break;
        case 'error':
          message = 'Processing encountered an error';
          break;
        case 'paused':
          message = 'Processing paused';
          break;
        case 'resumed':
          message = 'Processing resumed';
          break;
        default:
          message = `Processing status changed to ${status}`;
      }
      
      announce(message, { priority: 'assertive' });
    }

    // Announce significant progress changes (every 25%)
    if (progress !== prevProgress && progress > 0) {
      const progressPercent = Math.round(progress * 100);
      const prevProgressPercent = Math.round(prevProgress * 100);
      
      if (progressPercent % 25 === 0 && progressPercent !== prevProgressPercent) {
        const message = currentStep && totalSteps
          ? `Processing ${progressPercent}% complete. Step ${currentStep} of ${totalSteps}.`
          : `Processing ${progressPercent}% complete.`;
        
        announce(message, { priority: 'polite' });
      }
    }

    prevStatusRef.current = status;
    prevProgressRef.current = progress;
  }, [status, progress, currentStep, totalSteps, mode, announce]);

  return null;
}

/**
 * Mode Selection Announcer
 * Announces mode selection changes and availability
 */
export function ModeSelectionAnnouncer({ 
  selectedMode, 
  availableModes, 
  userTier 
}) {
  const announce = useScreenReaderAnnouncement();
  const prevModeRef = useRef(selectedMode);

  useEffect(() => {
    const prevMode = prevModeRef.current;
    
    if (selectedMode !== prevMode && selectedMode) {
      const modeConfig = availableModes.find(mode => mode.id === selectedMode);
      if (modeConfig) {
        const message = `${modeConfig.title} selected. ${modeConfig.description}`;
        announce(message, { priority: 'assertive' });
      }
    }

    prevModeRef.current = selectedMode;
  }, [selectedMode, availableModes, announce]);

  return null;
}

/**
 * Enhancement Results Announcer
 * Announces enhancement results and changes
 */
export function EnhancementResultsAnnouncer({ 
  results, 
  appliedEnhancements,
  atsScore 
}) {
  const announce = useScreenReaderAnnouncement();
  const prevResultsCountRef = useRef(0);
  const prevAtsScoreRef = useRef(atsScore);

  useEffect(() => {
    const currentResultsCount = results?.length || 0;
    const prevResultsCount = prevResultsCountRef.current;

    // Announce new results
    if (currentResultsCount > prevResultsCount) {
      const newResults = currentResultsCount - prevResultsCount;
      const message = `${newResults} new enhancement${newResults > 1 ? 's' : ''} available. Total: ${currentResultsCount} enhancements.`;
      announce(message, { priority: 'polite' });
    }

    prevResultsCountRef.current = currentResultsCount;
  }, [results, announce]);

  useEffect(() => {
    const prevAtsScore = prevAtsScoreRef.current;
    
    // Announce ATS score changes
    if (atsScore !== prevAtsScore && atsScore !== undefined) {
      const scoreDiff = atsScore - (prevAtsScore || 0);
      const direction = scoreDiff > 0 ? 'increased' : 'decreased';
      const message = `ATS compatibility score ${direction} to ${atsScore}%.`;
      announce(message, { priority: 'polite' });
    }

    prevAtsScoreRef.current = atsScore;
  }, [atsScore, announce]);

  return null;
}

/**
 * Navigation Announcer
 * Announces navigation changes and page context
 */
export function NavigationAnnouncer({ 
  currentPage, 
  breadcrumbs,
  totalSteps,
  currentStep 
}) {
  const announce = useScreenReaderAnnouncement();
  const prevPageRef = useRef(currentPage);

  useEffect(() => {
    const prevPage = prevPageRef.current;
    
    if (currentPage !== prevPage && currentPage) {
      let message = `Navigated to ${currentPage}`;
      
      if (breadcrumbs && breadcrumbs.length > 0) {
        const breadcrumbText = breadcrumbs.join(', ');
        message += `. Location: ${breadcrumbText}`;
      }
      
      if (totalSteps && currentStep) {
        message += `. Step ${currentStep} of ${totalSteps}`;
      }
      
      announce(message, { priority: 'polite' });
    }

    prevPageRef.current = currentPage;
  }, [currentPage, breadcrumbs, totalSteps, currentStep, announce]);

  return null;
}

/**
 * Error Announcer
 * Announces errors and validation messages
 */
export function ErrorAnnouncer({ 
  errors, 
  validationErrors,
  networkErrors 
}) {
  const announce = useScreenReaderAnnouncement();
  const prevErrorsRef = useRef([]);

  useEffect(() => {
    const allErrors = [
      ...(errors || []),
      ...(validationErrors || []),
      ...(networkErrors || [])
    ];
    
    const prevErrors = prevErrorsRef.current;
    const newErrors = allErrors.filter(error => 
      !prevErrors.some(prevError => prevError.id === error.id)
    );

    if (newErrors.length > 0) {
      newErrors.forEach(error => {
        const message = `Error: ${error.message || error.text}`;
        announce(message, { priority: 'assertive' });
      });
    }

    prevErrorsRef.current = allErrors;
  }, [errors, validationErrors, networkErrors, announce]);

  return null;
}

/**
 * Success Announcer
 * Announces successful operations and completions
 */
export function SuccessAnnouncer({ 
  successMessages,
  completedOperations 
}) {
  const announce = useScreenReaderAnnouncement();
  const prevSuccessRef = useRef([]);

  useEffect(() => {
    const allSuccess = [
      ...(successMessages || []),
      ...(completedOperations || [])
    ];
    
    const prevSuccess = prevSuccessRef.current;
    const newSuccess = allSuccess.filter(success => 
      !prevSuccess.some(prevSuccess => prevSuccess.id === success.id)
    );

    if (newSuccess.length > 0) {
      newSuccess.forEach(success => {
        const message = success.message || success.text || 'Operation completed successfully';
        announce(message, { priority: 'polite' });
      });
    }

    prevSuccessRef.current = allSuccess;
  }, [successMessages, completedOperations, announce]);

  return null;
}

/**
 * Form Validation Announcer
 * Announces form validation results
 */
export function FormValidationAnnouncer({ 
  isValid, 
  fieldErrors,
  formErrors 
}) {
  const announce = useScreenReaderAnnouncement();
  const prevValidRef = useRef(isValid);
  const prevFieldErrorsRef = useRef({});

  useEffect(() => {
    const prevValid = prevValidRef.current;
    
    // Announce validation state changes
    if (isValid !== prevValid) {
      const message = isValid 
        ? 'Form is now valid and ready to submit'
        : 'Form contains errors that need to be corrected';
      announce(message, { priority: 'polite' });
    }

    prevValidRef.current = isValid;
  }, [isValid, announce]);

  useEffect(() => {
    const prevFieldErrors = prevFieldErrorsRef.current;
    
    // Announce new field errors
    if (fieldErrors) {
      Object.entries(fieldErrors).forEach(([field, error]) => {
        if (error && error !== prevFieldErrors[field]) {
          const message = `${field}: ${error}`;
          announce(message, { priority: 'assertive' });
        }
      });
    }

    prevFieldErrorsRef.current = fieldErrors || {};
  }, [fieldErrors, announce]);

  return null;
}

/**
 * Comprehensive Screen Reader Support Provider
 * Combines all screen reader support components
 */
export function ScreenReaderSupportProvider({ 
  children,
  processingStatus,
  modeSelection,
  enhancementResults,
  navigation,
  errors,
  success,
  formValidation
}) {
  return (
    <>
      {/* Live regions for announcements */}
      <LiveRegion id="main-live-region" priority="polite" />
      <LiveRegion id="alert-live-region" priority="assertive" />
      
      {/* Status announcers */}
      {processingStatus && (
        <ProcessingStatusAnnouncer {...processingStatus} />
      )}
      
      {modeSelection && (
        <ModeSelectionAnnouncer {...modeSelection} />
      )}
      
      {enhancementResults && (
        <EnhancementResultsAnnouncer {...enhancementResults} />
      )}
      
      {navigation && (
        <NavigationAnnouncer {...navigation} />
      )}
      
      {errors && (
        <ErrorAnnouncer {...errors} />
      )}
      
      {success && (
        <SuccessAnnouncer {...success} />
      )}
      
      {formValidation && (
        <FormValidationAnnouncer {...formValidation} />
      )}
      
      {children}
    </>
  );
}

/**
 * Hook for managing screen reader context
 */
export function useScreenReaderContext() {
  const [announcements, setAnnouncements] = useState([]);
  const announce = useScreenReaderAnnouncement();

  const addAnnouncement = useCallback((message, priority = 'polite') => {
    const id = Date.now().toString();
    const announcement = { id, message, priority, timestamp: Date.now() };
    
    setAnnouncements(prev => [...prev, announcement]);
    announce(message, { priority });
    
    // Clean up old announcements
    setTimeout(() => {
      setAnnouncements(prev => prev.filter(a => a.id !== id));
    }, 5000);
  }, [announce]);

  const clearAnnouncements = useCallback(() => {
    setAnnouncements([]);
  }, []);

  return {
    announcements,
    addAnnouncement,
    clearAnnouncements
  };
}

export default {
  LiveRegion,
  ProcessingStatusAnnouncer,
  ModeSelectionAnnouncer,
  EnhancementResultsAnnouncer,
  NavigationAnnouncer,
  ErrorAnnouncer,
  SuccessAnnouncer,
  FormValidationAnnouncer,
  ScreenReaderSupportProvider,
  useScreenReaderContext
};