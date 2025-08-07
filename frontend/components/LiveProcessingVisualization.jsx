import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useProcessingStatus } from '../hooks/useWebSocket'
import { 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  Play, 
  Pause,
  BarChart3,
  TrendingUp,
  Zap
} from 'lucide-react'

/**
 * Real-time processing step visualization
 */
const ProcessingStepVisualizer = ({ step, status, progress, details, duration }) => {
  const stepIcons = {
    'analyzing': <BarChart3 className="w-5 h-5" />,
    'enhancing': <TrendingUp className="w-5 h-5" />,
    'optimizing': <Zap className="w-5 h-5" />,
    'generating': <CheckCircle className="w-5 h-5" />
  }

  const getStepIcon = () => {
    const stepKey = step.toLowerCase()
    return stepIcons[stepKey] || <Clock className="w-5 h-5" />
  }

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100'
      case 'active':
        return 'text-blue-600 bg-blue-100'
      case 'failed':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`flex items-center gap-3 p-4 rounded-lg ${getStatusColor()}`}
    >
      <div className="flex-shrink-0">
        {status === 'active' ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          getStepIcon()
        )}
      </div>
      
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <h4 className="font-medium">{step}</h4>
          {duration && (
            <span className="text-sm opacity-75">
              {duration < 1000 ? `${duration}ms` : `${(duration / 1000).toFixed(1)}s`}
            </span>
          )}
        </div>
        
        {details && (
          <p className="text-sm opacity-75 mt-1">{details}</p>
        )}
        
        {status === 'active' && progress !== undefined && (
          <div className="mt-2">
            <div className="w-full bg-white bg-opacity-50 rounded-full h-2">
              <motion.div
                className="bg-current h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

/**
 * Job processing timeline with live updates
 */
const JobProcessingTimeline = ({ job, isActive }) => {
  const { title, status, steps = [], progress, estimatedTimeRemaining } = job

  const formatTimeRemaining = (seconds) => {
    if (!seconds) return null
    if (seconds < 60) return `${Math.round(seconds)}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.round(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`bg-white border-2 rounded-xl p-6 transition-all duration-300 ${
        isActive ? 'border-blue-300 shadow-lg' : 'border-gray-200'
      }`}
    >
      {/* Job Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>Progress: {Math.round(progress || 0)}%</span>
            {estimatedTimeRemaining && (
              <span>ETA: {formatTimeRemaining(estimatedTimeRemaining)}</span>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {status === 'processing' && (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <Loader2 className="w-5 h-5 text-blue-500" />
            </motion.div>
          )}
          {status === 'completed' && (
            <CheckCircle className="w-5 h-5 text-green-500" />
          )}
          {status === 'failed' && (
            <AlertCircle className="w-5 h-5 text-red-500" />
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="w-full bg-gray-200 rounded-full h-3">
          <motion.div
            className={`h-3 rounded-full transition-colors duration-300 ${
              status === 'completed' ? 'bg-green-500' :
              status === 'failed' ? 'bg-red-500' : 'bg-blue-500'
            }`}
            initial={{ width: 0 }}
            animate={{ width: `${progress || 0}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Processing Steps */}
      <div className="space-y-3">
        {steps.map((step, index) => (
          <ProcessingStepVisualizer
            key={index}
            step={step.name}
            status={step.status}
            progress={step.progress}
            details={step.details}
            duration={step.duration}
          />
        ))}
      </div>
    </motion.div>
  )
}

/**
 * Batch processing overview with statistics
 */
const BatchProcessingOverview = ({ jobs, batchStatus, startTime }) => {
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    if (!startTime) return

    const interval = setInterval(() => {
      setElapsedTime(Date.now() - startTime)
    }, 1000)

    return () => clearInterval(interval)
  }, [startTime])

  const stats = {
    total: jobs.length,
    completed: jobs.filter(job => job.status === 'completed').length,
    processing: jobs.filter(job => job.status === 'processing').length,
    failed: jobs.filter(job => job.status === 'failed').length,
    queued: jobs.filter(job => job.status === 'queued').length
  }

  const overallProgress = stats.total > 0 
    ? ((stats.completed + stats.failed) / stats.total) * 100 
    : 0

  const formatElapsedTime = (ms) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`
    } else {
      return `${seconds}s`
    }
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Batch Processing</h2>
        {batchStatus?.status === 'completed' && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-800 rounded-full"
          >
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Completed</span>
          </motion.div>
        )}
      </div>

      {/* Overall Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm text-gray-600">{Math.round(overallProgress)}%</span>
        </div>
        <div className="w-full bg-white rounded-full h-4 shadow-inner">
          <motion.div
            className="bg-gradient-to-r from-blue-500 to-indigo-500 h-4 rounded-full shadow-sm"
            initial={{ width: 0 }}
            animate={{ width: `${overallProgress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-sm text-gray-600">Total</div>
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
          <div className="text-2xl font-bold text-orange-600">{stats.queued}</div>
          <div className="text-sm text-gray-600">Queued</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
          <div className="text-sm text-gray-600">Failed</div>
        </div>
      </div>

      {/* Elapsed Time */}
      {startTime && (
        <div className="mt-4 pt-4 border-t border-blue-200">
          <div className="text-center">
            <span className="text-sm text-gray-600">Elapsed Time: </span>
            <span className="text-sm font-medium text-gray-900">
              {formatElapsedTime(elapsedTime)}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Main live processing visualization component
 */
const LiveProcessingVisualization = ({ 
  className = "",
  showBatchOverview = true,
  maxVisibleJobs = 3,
  onJobRetry,
  onJobCancel,
  onBatchRetry
}) => {
  const {
    isConnected,
    connectionError,
    processingJobs,
    batchStatus,
    getProcessingStats
  } = useProcessingStatus({
    onJobStarted: (jobId, data) => {
      console.log('Job started:', jobId, data)
    },
    onJobProgress: (jobId, data) => {
      console.log('Job progress:', jobId, data)
    },
    onJobCompleted: (jobId, data) => {
      console.log('Job completed:', jobId, data)
    },
    onJobFailed: (jobId, data) => {
      console.log('Job failed:', jobId, data)
    },
    onBatchCompleted: (data) => {
      console.log('Batch completed:', data)
    }
  })

  const [startTime] = useState(Date.now())
  const activeJobs = processingJobs.filter(job => 
    job.status === 'processing' || job.status === 'queued'
  )
  const visibleJobs = processingJobs.slice(0, maxVisibleJobs)

  // Connection status indicator
  if (!isConnected && connectionError) {
    return (
      <div className={`live-processing-visualization ${className}`}>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            <div>
              <p className="text-sm font-medium text-yellow-800">
                Connection Issue
              </p>
              <p className="text-xs text-yellow-600 mt-1">
                Using fallback polling for updates
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (processingJobs.length === 0) {
    return (
      <div className={`live-processing-visualization ${className}`}>
        <div className="text-center py-8 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium">Ready to Process</p>
          <p className="text-sm">Live updates will appear here during processing</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`live-processing-visualization ${className}`}>
      {/* Batch Overview */}
      {showBatchOverview && (
        <BatchProcessingOverview
          jobs={processingJobs}
          batchStatus={batchStatus}
          startTime={startTime}
        />
      )}

      {/* Active Jobs */}
      <div className="space-y-4">
        <AnimatePresence>
          {visibleJobs.map(job => (
            <JobProcessingTimeline
              key={job.id}
              job={job}
              isActive={job.status === 'processing'}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Show more indicator */}
      {processingJobs.length > maxVisibleJobs && (
        <div className="text-center py-4">
          <p className="text-sm text-gray-600">
            And {processingJobs.length - maxVisibleJobs} more jobs...
          </p>
        </div>
      )}

      {/* Connection Status */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            {isConnected ? '🟢 Connected' : '🟡 Fallback Mode'}
          </span>
          <span>
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  )
}

export default LiveProcessingVisualization
export { ProcessingStepVisualizer, JobProcessingTimeline, BatchProcessingOverview }