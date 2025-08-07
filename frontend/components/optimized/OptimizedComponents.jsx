/**
 * Optimized versions of key components with React.memo and performance enhancements
 */
import React, { memo, useMemo, useCallback } from 'react'
import { createOptimizedComponent, shallowEqual, deepEqual } from '../../lib/state-optimization'

// Optimized AddResumeCard with selective re-rendering
export const OptimizedAddResumeCard = createOptimizedComponent(
  ({ file, resumeText, onFileChange, onTextChange, onScanIssues, ...props }) => {
    // Memoize expensive computations
    const fileInfo = useMemo(() => {
      if (!file) return null
      return {
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified
      }
    }, [file])

    const textStats = useMemo(() => {
      if (!resumeText) return { wordCount: 0, charCount: 0 }
      return {
        wordCount: resumeText.split(/\s+/).filter(word => word.length > 0).length,
        charCount: resumeText.length
      }
    }, [resumeText])

    // Memoize callbacks to prevent unnecessary re-renders
    const handleFileChange = useCallback((event) => {
      onFileChange?.(event)
    }, [onFileChange])

    const handleTextChange = useCallback((text) => {
      onTextChange?.(text)
    }, [onTextChange])

    const handleScanIssues = useCallback(() => {
      onScanIssues?.()
    }, [onScanIssues])

    // Import the actual component dynamically to avoid circular dependencies
    const AddResumeCard = React.lazy(() => import('../AddResumeCard'))

    return (
      <React.Suspense fallback={<div>Loading...</div>}>
        <AddResumeCard
          file={file}
          resumeText={resumeText}
          onFileChange={handleFileChange}
          onTextChange={handleTextChange}
          onScanIssues={handleScanIssues}
          fileInfo={fileInfo}
          textStats={textStats}
          {...props}
        />
      </React.Suspense>
    )
  },
  {
    displayName: 'OptimizedAddResumeCard',
    propsAreEqual: (prevProps, nextProps) => {
      // Custom comparison for file objects
      const fileEqual = prevProps.file === nextProps.file || 
        (prevProps.file && nextProps.file && 
         prevProps.file.name === nextProps.file.name &&
         prevProps.file.size === nextProps.file.size &&
         prevProps.file.lastModified === nextProps.file.lastModified)
      
      return fileEqual && 
        prevProps.resumeText === nextProps.resumeText &&
        prevProps.onFileChange === nextProps.onFileChange &&
        prevProps.onTextChange === nextProps.onTextChange &&
        prevProps.onScanIssues === nextProps.onScanIssues
    },
    trackUpdates: true
  }
)

// Optimized JobOpportunitiesCard with debounced input
export const OptimizedJobOpportunitiesCard = createOptimizedComponent(
  ({ jobUrls, onUrlsChange, isProUser, maxUrls, ...props }) => {
    const urlStats = useMemo(() => {
      if (!jobUrls) return { count: 0, validUrls: 0 }
      
      const urls = jobUrls.trim().split('\n').filter(line => line.trim())
      const validUrls = urls.filter(url => {
        try {
          new URL(url.trim())
          return true
        } catch {
          return false
        }
      })
      
      return {
        count: urls.length,
        validUrls: validUrls.length
      }
    }, [jobUrls])

    const handleUrlsChange = useCallback((urls) => {
      onUrlsChange?.(urls)
    }, [onUrlsChange])

    const JobOpportunitiesCard = React.lazy(() => import('../JobOpportunitiesCard'))

    return (
      <React.Suspense fallback={<div>Loading...</div>}>
        <JobOpportunitiesCard
          jobUrls={jobUrls}
          onUrlsChange={handleUrlsChange}
          isProUser={isProUser}
          maxUrls={maxUrls}
          urlStats={urlStats}
          {...props}
        />
      </React.Suspense>
    )
  },
  {
    displayName: 'OptimizedJobOpportunitiesCard',
    propsAreEqual: shallowEqual,
    trackUpdates: true
  }
)

// Optimized ProcessingStatusIndicator with minimal re-renders
export const OptimizedProcessingStatusIndicator = createOptimizedComponent(
  ({ processing, batchStatus, error, ...props }) => {
    const statusInfo = useMemo(() => {
      if (error) {
        return { type: 'error', message: error }
      }
      
      if (!processing) {
        return { type: 'idle', message: 'Ready to process' }
      }
      
      if (batchStatus) {
        const progress = batchStatus.total > 0 
          ? Math.round((batchStatus.completed / batchStatus.total) * 100)
          : 0
        
        return {
          type: 'processing',
          message: batchStatus.current_job || 'Processing...',
          progress,
          completed: batchStatus.completed,
          total: batchStatus.total,
          failed: batchStatus.failed
        }
      }
      
      return { type: 'processing', message: 'Starting...' }
    }, [processing, batchStatus, error])

    const ProcessingStatusIndicator = React.lazy(() => import('../ProcessingStatusIndicator'))

    return (
      <React.Suspense fallback={<div>Loading...</div>}>
        <ProcessingStatusIndicator
          processing={processing}
          batchStatus={batchStatus}
          error={error}
          statusInfo={statusInfo}
          {...props}
        />
      </React.Suspense>
    )
  },
  {
    displayName: 'OptimizedProcessingStatusIndicator',
    propsAreEqual: (prevProps, nextProps) => {
      return prevProps.processing === nextProps.processing &&
        prevProps.error === nextProps.error &&
        deepEqual(prevProps.batchStatus, nextProps.batchStatus)
    },
    trackUpdates: true
  }
)

// Optimized ResultCard with memoized calculations
export const OptimizedResultCard = createOptimizedComponent(
  ({ result, onDownload, onCompare, outputFormat, ...props }) => {
    const resultMetrics = useMemo(() => {
      if (!result) return null
      
      return {
        wordCount: result.tailored_resume ? 
          result.tailored_resume.split(/\s+/).filter(word => word.length > 0).length : 0,
        transformationScore: result.transformation_score || 0,
        hasKeywords: result.matched_keywords?.length > 0,
        keywordCount: result.matched_keywords?.length || 0,
        hasCoverLetter: !!result.cover_letter
      }
    }, [result])

    const handleDownload = useCallback((format) => {
      onDownload?.(result, format)
    }, [onDownload, result])

    const handleCompare = useCallback(() => {
      onCompare?.(result)
    }, [onCompare, result])

    const ResultCard = React.lazy(() => import('../ResultCard'))

    return (
      <React.Suspense fallback={<div>Loading...</div>}>
        <ResultCard
          result={result}
          onDownload={handleDownload}
          onCompare={handleCompare}
          outputFormat={outputFormat}
          resultMetrics={resultMetrics}
          {...props}
        />
      </React.Suspense>
    )
  },
  {
    displayName: 'OptimizedResultCard',
    propsAreEqual: (prevProps, nextProps) => {
      return deepEqual(prevProps.result, nextProps.result) &&
        prevProps.outputFormat === nextProps.outputFormat &&
        prevProps.onDownload === nextProps.onDownload &&
        prevProps.onCompare === nextProps.onCompare
    },
    trackUpdates: true
  }
)

// Optimized UsageSidebarCard with smart updates
export const OptimizedUsageSidebarCard = createOptimizedComponent(
  ({ weeklyUsage, weeklyLimit, isProUser, resetDate, onUpgradeClick, compact, ...props }) => {
    const usageMetrics = useMemo(() => {
      const percentage = weeklyLimit > 0 ? Math.round((weeklyUsage / weeklyLimit) * 100) : 0
      const remaining = Math.max(0, weeklyLimit - weeklyUsage)
      const isNearLimit = percentage >= 80
      const isAtLimit = weeklyUsage >= weeklyLimit
      
      return {
        percentage,
        remaining,
        isNearLimit,
        isAtLimit,
        status: isAtLimit ? 'exceeded' : isNearLimit ? 'warning' : 'normal'
      }
    }, [weeklyUsage, weeklyLimit])

    const timeUntilReset = useMemo(() => {
      if (!resetDate) return null
      
      const now = new Date()
      const reset = new Date(resetDate)
      const diff = reset.getTime() - now.getTime()
      
      if (diff <= 0) return 'Resetting soon'
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
      
      if (days > 0) return `${days}d ${hours}h`
      return `${hours}h`
    }, [resetDate])

    const handleUpgradeClick = useCallback(() => {
      onUpgradeClick?.()
    }, [onUpgradeClick])

    const UsageSidebarCard = React.lazy(() => import('../UsageSidebarCard'))

    return (
      <React.Suspense fallback={<div>Loading...</div>}>
        <UsageSidebarCard
          weeklyUsage={weeklyUsage}
          weeklyLimit={weeklyLimit}
          isProUser={isProUser}
          resetDate={resetDate}
          onUpgradeClick={handleUpgradeClick}
          compact={compact}
          usageMetrics={usageMetrics}
          timeUntilReset={timeUntilReset}
          {...props}
        />
      </React.Suspense>
    )
  },
  {
    displayName: 'OptimizedUsageSidebarCard',
    propsAreEqual: (prevProps, nextProps) => {
      return prevProps.weeklyUsage === nextProps.weeklyUsage &&
        prevProps.weeklyLimit === nextProps.weeklyLimit &&
        prevProps.isProUser === nextProps.isProUser &&
        prevProps.compact === nextProps.compact &&
        prevProps.resetDate === nextProps.resetDate &&
        prevProps.onUpgradeClick === nextProps.onUpgradeClick
    },
    trackUpdates: true
  }
)

// Optimized TailoringModeSelector with minimal re-renders
export const OptimizedTailoringModeSelector = createOptimizedComponent(
  ({ mode, onChange, disabled, ...props }) => {
    const modeInfo = useMemo(() => {
      const modes = {
        light: {
          label: 'Light Tailoring',
          description: 'Minimal changes, preserves original structure',
          intensity: 25
        },
        moderate: {
          label: 'Moderate Tailoring',
          description: 'Balanced approach with targeted improvements',
          intensity: 50
        },
        aggressive: {
          label: 'Aggressive Tailoring',
          description: 'Comprehensive restructuring for maximum impact',
          intensity: 75
        }
      }
      
      return modes[mode] || modes.light
    }, [mode])

    const handleModeChange = useCallback((newMode) => {
      if (newMode !== mode) {
        onChange?.(newMode)
      }
    }, [mode, onChange])

    const TailoringModeSelector = React.lazy(() => import('../TailoringModeSelector'))

    return (
      <React.Suspense fallback={<div>Loading...</div>}>
        <TailoringModeSelector
          mode={mode}
          onChange={handleModeChange}
          disabled={disabled}
          modeInfo={modeInfo}
          {...props}
        />
      </React.Suspense>
    )
  },
  {
    displayName: 'OptimizedTailoringModeSelector',
    propsAreEqual: shallowEqual,
    trackUpdates: true
  }
)

// Export all optimized components
export {
  OptimizedAddResumeCard as AddResumeCard,
  OptimizedJobOpportunitiesCard as JobOpportunitiesCard,
  OptimizedProcessingStatusIndicator as ProcessingStatusIndicator,
  OptimizedResultCard as ResultCard,
  OptimizedUsageSidebarCard as UsageSidebarCard,
  OptimizedTailoringModeSelector as TailoringModeSelector
}

// Component registry for dynamic loading
export const optimizedComponents = {
  AddResumeCard: OptimizedAddResumeCard,
  JobOpportunitiesCard: OptimizedJobOpportunitiesCard,
  ProcessingStatusIndicator: OptimizedProcessingStatusIndicator,
  ResultCard: OptimizedResultCard,
  UsageSidebarCard: OptimizedUsageSidebarCard,
  TailoringModeSelector: OptimizedTailoringModeSelector
}