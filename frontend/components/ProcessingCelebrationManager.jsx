import React, { useState, useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import {
  ScoreRevealAnimation,
  ProcessingCompletionCelebration,
  BatchCompletionCelebration,
  EncouragingMessage,
  ProcessingStateTransition
} from './SuccessAnimations'

/**
 * Manages celebration animations and encouraging messages during processing
 */
const ProcessingCelebrationManager = ({
  processingJobs = [],
  batchStatus = null,
  currentScore = null,
  previousScore = null,
  onViewResults,
  onDownload,
  onDownloadAll,
  onProcessNext,
  className = ""
}) => {
  const [celebrationState, setCelebrationState] = useState('idle')
  const [completedJob, setCompletedJob] = useState(null)
  const [processingStartTime, setProcessingStartTime] = useState(null)
  const [showEncouragement, setShowEncouragement] = useState(false)

  // Track processing state changes
  useEffect(() => {
    const activeJobs = processingJobs.filter(job => 
      job.status === 'processing' || job.status === 'queued'
    )
    const completedJobs = processingJobs.filter(job => job.status === 'completed')
    const recentlyCompleted = completedJobs.find(job => 
      job.completedTime && Date.now() - job.completedTime < 5000
    )

    // Start processing
    if (activeJobs.length > 0 && celebrationState === 'idle') {
      setCelebrationState('processing')
      setProcessingStartTime(Date.now())
      setShowEncouragement(false)
    }

    // Job completed
    if (recentlyCompleted && celebrationState === 'processing') {
      setCompletedJob(recentlyCompleted)
      setCelebrationState('job-completed')
      setShowEncouragement(false)
    }

    // Batch completed
    if (batchStatus?.status === 'completed' && celebrationState !== 'batch-completed') {
      setCelebrationState('batch-completed')
      setShowEncouragement(false)
    }

    // Return to idle
    if (activeJobs.length === 0 && completedJobs.length === 0 && celebrationState !== 'idle') {
      setCelebrationState('idle')
      setCompletedJob(null)
      setProcessingStartTime(null)
      setShowEncouragement(false)
    }
  }, [processingJobs, batchStatus, celebrationState])

  // Show encouraging messages for long processing times
  useEffect(() => {
    if (celebrationState !== 'processing' || !processingStartTime) return

    const timer = setTimeout(() => {
      setShowEncouragement(true)
    }, 30000) // Show after 30 seconds

    return () => clearTimeout(timer)
  }, [celebrationState, processingStartTime])

  // Calculate batch statistics
  const getBatchStats = () => {
    const completed = processingJobs.filter(job => job.status === 'completed')
    const totalProcessingTime = completed.reduce((sum, job) => {
      if (job.startTime && job.completedTime) {
        return sum + (job.completedTime - job.startTime)
      }
      return sum
    }, 0)

    const averageImprovement = completed.reduce((sum, job) => {
      return sum + (job.scoreImprovement || 0)
    }, 0) / Math.max(completed.length, 1)

    return {
      completedJobs: completed.length,
      totalJobs: processingJobs.length,
      totalProcessingTime,
      averageImprovement: Math.round(averageImprovement)
    }
  }

  // Get current processing job for encouragement
  const getCurrentProcessingJob = () => {
    return processingJobs.find(job => job.status === 'processing')
  }

  const renderCelebrationContent = () => {
    switch (celebrationState) {
      case 'processing':
        const currentJob = getCurrentProcessingJob()
        return (
          <div>
            {showEncouragement && currentJob && (
              <EncouragingMessage
                processingTime={Date.now() - processingStartTime}
                jobTitle={currentJob.title}
              />
            )}
          </div>
        )

      case 'job-completed':
        if (!completedJob) return null
        
        return (
          <div className="space-y-6">
            {/* Score Reveal */}
            {currentScore && previousScore && currentScore > previousScore && (
              <ScoreRevealAnimation
                initialScore={previousScore}
                finalScore={currentScore}
                improvement={currentScore - previousScore}
                onComplete={() => {
                  // Auto-transition after score reveal
                  setTimeout(() => {
                    if (processingJobs.filter(job => job.status === 'processing').length === 0) {
                      setCelebrationState('idle')
                    }
                  }, 3000)
                }}
              />
            )}

            {/* Job Completion */}
            <ProcessingCompletionCelebration
              jobTitle={completedJob.title}
              processingTime={completedJob.completedTime - completedJob.startTime}
              improvements={completedJob.improvements || []}
              onViewResults={() => onViewResults && onViewResults(completedJob)}
              onDownload={() => onDownload && onDownload(completedJob)}
              onProcessNext={processingJobs.filter(job => job.status === 'queued').length > 0 ? onProcessNext : null}
            />
          </div>
        )

      case 'batch-completed':
        const stats = getBatchStats()
        return (
          <BatchCompletionCelebration
            completedJobs={stats.completedJobs}
            totalJobs={stats.totalJobs}
            totalProcessingTime={stats.totalProcessingTime}
            averageImprovement={stats.averageImprovement}
            onViewAllResults={onViewResults}
            onDownloadAll={onDownloadAll}
          />
        )

      default:
        return null
    }
  }

  const content = renderCelebrationContent()
  if (!content) return null

  return (
    <div className={`processing-celebration-manager ${className}`}>
      <AnimatePresence mode="wait">
        <ProcessingStateTransition
          fromState={celebrationState === 'processing' ? 'idle' : 'processing'}
          toState={celebrationState}
          key={celebrationState}
        >
          {content}
        </ProcessingStateTransition>
      </AnimatePresence>
    </div>
  )
}

/**
 * Hook for managing celebration state
 */
export const useCelebrationManager = () => {
  const [celebrationQueue, setCelebrationQueue] = useState([])
  const [currentCelebration, setCurrentCelebration] = useState(null)

  const addCelebration = (celebration) => {
    setCelebrationQueue(prev => [...prev, celebration])
  }

  const processCelebrationQueue = () => {
    if (celebrationQueue.length > 0 && !currentCelebration) {
      const next = celebrationQueue[0]
      setCurrentCelebration(next)
      setCelebrationQueue(prev => prev.slice(1))
    }
  }

  const completeCelebration = () => {
    setCurrentCelebration(null)
    // Process next celebration after a delay
    setTimeout(processCelebrationQueue, 1000)
  }

  // Auto-process queue
  React.useEffect(() => {
    processCelebrationQueue()
  }, [celebrationQueue, currentCelebration])

  return {
    addCelebration,
    currentCelebration,
    completeCelebration,
    queueLength: celebrationQueue.length
  }
}

/**
 * Simple celebration trigger for individual events
 */
export const CelebrationTrigger = ({ 
  type, 
  data, 
  onComplete,
  autoComplete = true,
  autoCompleteDelay = 5000 
}) => {
  useEffect(() => {
    if (autoComplete) {
      const timer = setTimeout(() => {
        if (onComplete) onComplete()
      }, autoCompleteDelay)
      
      return () => clearTimeout(timer)
    }
  }, [autoComplete, autoCompleteDelay, onComplete])

  const renderCelebration = () => {
    switch (type) {
      case 'score-reveal':
        return (
          <ScoreRevealAnimation
            initialScore={data.initialScore}
            finalScore={data.finalScore}
            improvement={data.improvement}
            onComplete={onComplete}
          />
        )
      
      case 'job-completed':
        return (
          <ProcessingCompletionCelebration
            jobTitle={data.jobTitle}
            processingTime={data.processingTime}
            improvements={data.improvements}
            onViewResults={data.onViewResults}
            onDownload={data.onDownload}
            onProcessNext={data.onProcessNext}
          />
        )
      
      case 'batch-completed':
        return (
          <BatchCompletionCelebration
            completedJobs={data.completedJobs}
            totalJobs={data.totalJobs}
            totalProcessingTime={data.totalProcessingTime}
            averageImprovement={data.averageImprovement}
            onViewAllResults={data.onViewAllResults}
            onDownloadAll={data.onDownloadAll}
          />
        )
      
      default:
        return null
    }
  }

  return renderCelebration()
}

export default ProcessingCelebrationManager