import { useEffect, useState, useCallback, useRef } from 'react'
import { getWebSocketClient } from '../lib/websocket'

/**
 * React hook for WebSocket integration with automatic connection management
 * @param {Object} options - Configuration options
 * @param {boolean} options.autoConnect - Whether to connect automatically on mount
 * @param {Function} options.onMessage - Message handler function
 * @param {Function} options.onConnection - Connection status handler
 * @param {Function} options.onError - Error handler function
 * @returns {Object} WebSocket utilities and status
 */
export const useWebSocket = (options = {}) => {
  const {
    autoConnect = true,
    onMessage,
    onConnection,
    onError
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState(null)
  const [lastMessage, setLastMessage] = useState(null)
  const [isFallbackActive, setIsFallbackActive] = useState(false)
  
  const wsClient = useRef(null)
  const unsubscribeRefs = useRef([])

  // Initialize WebSocket client
  useEffect(() => {
    wsClient.current = getWebSocketClient()
    
    return () => {
      // Cleanup subscriptions on unmount
      unsubscribeRefs.current.forEach(unsubscribe => unsubscribe())
      unsubscribeRefs.current = []
    }
  }, [])

  // Set up event handlers
  useEffect(() => {
    if (!wsClient.current) return

    // Clear previous subscriptions
    unsubscribeRefs.current.forEach(unsubscribe => unsubscribe())
    unsubscribeRefs.current = []

    // Message handler
    const unsubscribeMessage = wsClient.current.onMessage((message) => {
      setLastMessage(message)
      if (onMessage) {
        onMessage(message)
      }
    })

    // Connection handler
    const unsubscribeConnection = wsClient.current.onConnection((connected) => {
      setIsConnected(connected)
      setIsFallbackActive(wsClient.current.isFallbackActive())
      if (onConnection) {
        onConnection(connected)
      }
    })

    // Error handler
    const unsubscribeError = wsClient.current.onError((error) => {
      setConnectionError(error)
      if (onError) {
        onError(error)
      }
    })

    unsubscribeRefs.current = [
      unsubscribeMessage,
      unsubscribeConnection,
      unsubscribeError
    ]

    // Auto-connect if enabled
    if (autoConnect) {
      wsClient.current.connect()
    }

    return () => {
      unsubscribeRefs.current.forEach(unsubscribe => unsubscribe())
      unsubscribeRefs.current = []
    }
  }, [autoConnect, onMessage, onConnection, onError])

  // Manual connection control
  const connect = useCallback(() => {
    if (wsClient.current) {
      wsClient.current.connect()
    }
  }, [])

  const disconnect = useCallback(() => {
    if (wsClient.current) {
      wsClient.current.disconnect()
    }
  }, [])

  // Send message
  const sendMessage = useCallback((message) => {
    if (wsClient.current) {
      wsClient.current.send(message)
    }
  }, [])

  return {
    isConnected,
    connectionError,
    lastMessage,
    isFallbackActive,
    connect,
    disconnect,
    sendMessage
  }
}

/**
 * Hook specifically for processing status updates
 * @param {Object} options - Configuration options
 * @param {Function} options.onJobStarted - Handler for job started events
 * @param {Function} options.onJobProgress - Handler for job progress events
 * @param {Function} options.onJobCompleted - Handler for job completed events
 * @param {Function} options.onJobFailed - Handler for job failed events
 * @param {Function} options.onBatchCompleted - Handler for batch completed events
 * @param {Function} options.onScoreUpdate - Handler for score update events
 * @param {Function} options.onEnhancementApplied - Handler for enhancement applied events
 * @returns {Object} Processing status and utilities
 */
export const useProcessingStatus = (options = {}) => {
  const {
    onJobStarted,
    onJobProgress,
    onJobCompleted,
    onJobFailed,
    onBatchCompleted,
    onScoreUpdate,
    onEnhancementApplied
  } = options

  const [processingJobs, setProcessingJobs] = useState(new Map())
  const [batchStatus, setBatchStatus] = useState(null)
  const [currentScore, setCurrentScore] = useState(null)

  const handleMessage = useCallback((message) => {
    const { type, jobId, data } = message

    switch (type) {
      case 'job_started':
        setProcessingJobs(prev => new Map(prev).set(jobId, {
          id: jobId,
          status: 'processing',
          progress: 0,
          step: 'Starting...',
          startTime: Date.now()
        }))
        if (onJobStarted) onJobStarted(jobId, data)
        break

      case 'job_progress':
        setProcessingJobs(prev => {
          const updated = new Map(prev)
          const job = updated.get(jobId) || {}
          updated.set(jobId, {
            ...job,
            progress: data.progress || 0,
            step: data.step || job.step,
            stepDetails: data.stepDetails,
            estimatedTimeRemaining: data.estimatedTimeRemaining
          })
          return updated
        })
        if (onJobProgress) onJobProgress(jobId, data)
        break

      case 'job_completed':
        setProcessingJobs(prev => {
          const updated = new Map(prev)
          const job = updated.get(jobId) || {}
          updated.set(jobId, {
            ...job,
            status: 'completed',
            progress: 100,
            step: 'Completed',
            completedTime: Date.now()
          })
          return updated
        })
        if (onJobCompleted) onJobCompleted(jobId, data)
        break

      case 'job_failed':
        setProcessingJobs(prev => {
          const updated = new Map(prev)
          const job = updated.get(jobId) || {}
          updated.set(jobId, {
            ...job,
            status: 'failed',
            step: 'Failed',
            error: data.error,
            failedTime: Date.now()
          })
          return updated
        })
        if (onJobFailed) onJobFailed(jobId, data)
        break

      case 'batch_completed':
        setBatchStatus({
          status: 'completed',
          completedJobs: data.completedJobs,
          totalJobs: data.totalJobs,
          completedTime: Date.now()
        })
        if (onBatchCompleted) onBatchCompleted(data)
        break

      case 'score_update':
        setCurrentScore(data.atsScore)
        if (onScoreUpdate) onScoreUpdate(data.atsScore)
        break

      case 'enhancement_applied':
        if (onEnhancementApplied) onEnhancementApplied(data.enhancement)
        break

      default:
        console.warn('Unknown message type:', type)
    }
  }, [
    onJobStarted,
    onJobProgress,
    onJobCompleted,
    onJobFailed,
    onBatchCompleted,
    onScoreUpdate,
    onEnhancementApplied
  ])

  const { isConnected, connectionError, connect, disconnect, sendMessage } = useWebSocket({
    onMessage: handleMessage
  })

  // Clear processing state
  const clearProcessingState = useCallback(() => {
    setProcessingJobs(new Map())
    setBatchStatus(null)
    setCurrentScore(null)
  }, [])

  // Get processing statistics
  const getProcessingStats = useCallback(() => {
    const jobs = Array.from(processingJobs.values())
    return {
      total: jobs.length,
      completed: jobs.filter(job => job.status === 'completed').length,
      failed: jobs.filter(job => job.status === 'failed').length,
      processing: jobs.filter(job => job.status === 'processing').length,
      averageProgress: jobs.length > 0 
        ? jobs.reduce((sum, job) => sum + (job.progress || 0), 0) / jobs.length 
        : 0
    }
  }, [processingJobs])

  return {
    isConnected,
    connectionError,
    processingJobs: Array.from(processingJobs.values()),
    batchStatus,
    currentScore,
    connect,
    disconnect,
    sendMessage,
    clearProcessingState,
    getProcessingStats: getProcessingStats()
  }
}

export default useWebSocket