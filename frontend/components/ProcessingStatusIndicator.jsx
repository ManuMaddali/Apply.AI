import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, AlertCircle, Clock, Loader2, Play, Pause } from 'lucide-react'

/**
 * Individual processing step indicator with timing and status
 */
const ProcessingStep = ({ step, status, duration, details, isActive }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      case 'active':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'text-green-700 bg-green-50 border-green-200'
      case 'failed':
        return 'text-red-700 bg-red-50 border-red-200'
      case 'active':
        return 'text-blue-700 bg-blue-50 border-blue-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`flex items-center gap-3 p-3 rounded-lg border ${getStatusColor()}`}
    >
      <div className="flex-shrink-0">
        {getStatusIcon()}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium truncate">{step}</p>
          {duration && (
            <span className="text-xs opacity-75">
              {duration < 1000 ? `${duration}ms` : `${(duration / 1000).toFixed(1)}s`}
            </span>
          )}
        </div>
        
        {details && (
          <p className="text-xs opacity-75 mt-1 truncate">{details}</p>
        )}
      </div>
      
      {isActive && (
        <motion.div
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className="w-2 h-2 bg-blue-500 rounded-full"
        />
      )}
    </motion.div>
  )
}

/**
 * Progress bar with animated fill and percentage
 */
const ProgressBar = ({ progress, showPercentage = true, color = 'blue', size = 'md' }) => {
  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4'
  }

  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500'
  }

  return (
    <div className="w-full">
      {showPercentage && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Progress</span>
          <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
        </div>
      )}
      
      <div className={`w-full bg-gray-200 rounded-full ${sizeClasses[size]}`}>
        <motion.div
          className={`${colorClasses[color]} ${sizeClasses[size]} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

/**
 * Job processing card with live status updates
 */
const JobProcessingCard = ({ job, onRetry, onCancel }) => {
  const {
    id,
    title,
    status,
    progress = 0,
    step,
    stepDetails,
    steps = [],
    estimatedTimeRemaining,
    startTime,
    error
  } = job

  const getStatusBadge = () => {
    const badges = {
      queued: { text: 'Queued', color: 'bg-gray-100 text-gray-700' },
      processing: { text: 'Processing', color: 'bg-blue-100 text-blue-700' },
      completed: { text: 'Completed', color: 'bg-green-100 text-green-700' },
      failed: { text: 'Failed', color: 'bg-red-100 text-red-700' }
    }
    
    const badge = badges[status] || badges.queued
    
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badge.color}`}>
        {badge.text}
      </span>
    )
  }

  const formatTimeRemaining = (seconds) => {
    if (!seconds) return null
    if (seconds < 60) return `${Math.round(seconds)}s remaining`
    return `${Math.round(seconds / 60)}m ${Math.round(seconds % 60)}s remaining`
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-gray-900 truncate">{title}</h3>
          <p className="text-xs text-gray-500 mt-1">Job ID: {id}</p>
        </div>
        <div className="flex items-center gap-2 ml-3">
          {getStatusBadge()}
        </div>
      </div>

      {/* Progress */}
      {status === 'processing' && (
        <div className="mb-4">
          <ProgressBar 
            progress={progress} 
            color={status === 'failed' ? 'red' : 'blue'} 
          />
          
          {step && (
            <div className="mt-2 flex items-center justify-between text-sm">
              <span className="text-gray-600">{step}</span>
              {estimatedTimeRemaining && (
                <span className="text-gray-500">
                  {formatTimeRemaining(estimatedTimeRemaining)}
                </span>
              )}
            </div>
          )}
          
          {stepDetails && (
            <p className="text-xs text-gray-500 mt-1">{stepDetails}</p>
          )}
        </div>
      )}

      {/* Steps */}
      {steps.length > 0 && (
        <div className="space-y-2 mb-4">
          {steps.map((stepItem, index) => (
            <ProcessingStep
              key={index}
              step={stepItem.name}
              status={stepItem.status}
              duration={stepItem.duration}
              details={stepItem.details}
              isActive={stepItem.status === 'active'}
            />
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800">Processing Failed</p>
              <p className="text-xs text-red-600 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      {(status === 'failed' || status === 'processing') && (
        <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
          {status === 'failed' && onRetry && (
            <button
              onClick={() => onRetry(id)}
              className="px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded hover:bg-blue-100 transition-colors"
            >
              Retry
            </button>
          )}
          
          {status === 'processing' && onCancel && (
            <button
              onClick={() => onCancel(id)}
              className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-50 border border-gray-200 rounded hover:bg-gray-100 transition-colors"
            >
              Cancel
            </button>
          )}
          
          {startTime && (
            <span className="text-xs text-gray-500 ml-auto">
              Started {new Date(startTime).toLocaleTimeString()}
            </span>
          )}
        </div>
      )}
    </motion.div>
  )
}

/**
 * Processing queue visualization with overall progress
 */
const ProcessingQueue = ({ jobs, batchStatus, onRetryJob, onCancelJob, onRetryBatch }) => {
  const stats = {
    total: jobs.length,
    completed: jobs.filter(job => job.status === 'completed').length,
    failed: jobs.filter(job => job.status === 'failed').length,
    processing: jobs.filter(job => job.status === 'processing').length,
    queued: jobs.filter(job => job.status === 'queued').length
  }

  const overallProgress = stats.total > 0 
    ? ((stats.completed + stats.failed) / stats.total) * 100 
    : 0

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Processing Queue</h2>
          {batchStatus?.status === 'completed' && (
            <span className="px-3 py-1 text-sm font-medium text-green-700 bg-green-100 rounded-full">
              Batch Completed
            </span>
          )}
        </div>

        <ProgressBar 
          progress={overallProgress} 
          color={stats.failed > 0 ? 'orange' : 'blue'}
          size="lg"
        />

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            <div className="text-sm text-gray-600">Total Jobs</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            <div className="text-sm text-gray-600">Completed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.processing}</div>
            <div className="text-sm text-gray-600">Processing</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
            <div className="text-sm text-gray-600">Failed</div>
          </div>
        </div>

        {stats.failed > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <button
              onClick={onRetryBatch}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Retry Failed Jobs ({stats.failed})
            </button>
          </div>
        )}
      </div>

      {/* Individual Jobs */}
      <div className="space-y-4">
        <AnimatePresence>
          {jobs.map(job => (
            <JobProcessingCard
              key={job.id}
              job={job}
              onRetry={onRetryJob}
              onCancel={onCancelJob}
            />
          ))}
        </AnimatePresence>
      </div>

      {jobs.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium">No jobs in queue</p>
          <p className="text-sm">Jobs will appear here when processing starts</p>
        </div>
      )}
    </div>
  )
}

/**
 * Main processing status indicator component
 */
const ProcessingStatusIndicator = ({ 
  jobs = [], 
  batchStatus = null,
  showQueue = true,
  onRetryJob,
  onCancelJob,
  onRetryBatch,
  className = ""
}) => {
  if (!showQueue && jobs.length === 0) {
    return null
  }

  return (
    <div className={`processing-status-indicator ${className}`}>
      <ProcessingQueue
        jobs={jobs}
        batchStatus={batchStatus}
        onRetryJob={onRetryJob}
        onCancelJob={onCancelJob}
        onRetryBatch={onRetryBatch}
      />
    </div>
  )
}

export default ProcessingStatusIndicator
export { ProcessingStep, ProgressBar, JobProcessingCard, ProcessingQueue }