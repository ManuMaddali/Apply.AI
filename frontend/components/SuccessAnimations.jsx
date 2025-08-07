import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckCircle, 
  Star, 
  TrendingUp, 
  Award, 
  Sparkles,
  Download,
  Eye,
  ArrowRight,
  Zap
} from 'lucide-react'

/**
 * Confetti animation component
 */
const Confetti = ({ active, duration = 3000 }) => {
  const [particles, setParticles] = useState([])

  useEffect(() => {
    if (!active) return

    const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      color: colors[Math.floor(Math.random() * colors.length)],
      size: Math.random() * 8 + 4,
      rotation: Math.random() * 360,
      delay: Math.random() * 0.5
    }))

    setParticles(newParticles)

    const timer = setTimeout(() => {
      setParticles([])
    }, duration)

    return () => clearTimeout(timer)
  }, [active, duration])

  if (!active || particles.length === 0) return null

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {particles.map(particle => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full"
          style={{
            backgroundColor: particle.color,
            width: particle.size,
            height: particle.size,
            left: `${particle.x}%`,
            top: `${particle.y}%`
          }}
          initial={{ 
            scale: 0, 
            rotate: 0,
            y: 0,
            opacity: 1
          }}
          animate={{ 
            scale: [0, 1, 0.8, 0],
            rotate: particle.rotation,
            y: [0, -100, -200],
            opacity: [1, 1, 0.5, 0]
          }}
          transition={{
            duration: 2,
            delay: particle.delay,
            ease: 'easeOut'
          }}
        />
      ))}
    </div>
  )
}

/**
 * Score reveal animation with celebration effects
 */
const ScoreRevealAnimation = ({ 
  initialScore, 
  finalScore, 
  improvement, 
  onComplete,
  showConfetti = true 
}) => {
  const [currentScore, setCurrentScore] = useState(initialScore)
  const [isAnimating, setIsAnimating] = useState(false)
  const [showCelebration, setShowCelebration] = useState(false)

  useEffect(() => {
    if (finalScore <= initialScore) return

    setIsAnimating(true)
    const duration = 2000
    const steps = 60
    const increment = (finalScore - initialScore) / steps
    const stepDuration = duration / steps

    let step = 0
    const interval = setInterval(() => {
      step++
      const newScore = Math.min(
        initialScore + (increment * step),
        finalScore
      )
      setCurrentScore(Math.round(newScore))

      if (step >= steps) {
        clearInterval(interval)
        setIsAnimating(false)
        setShowCelebration(true)
        if (onComplete) onComplete()
      }
    }, stepDuration)

    return () => clearInterval(interval)
  }, [initialScore, finalScore, onComplete])

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 75) return 'text-blue-600'
    if (score >= 60) return 'text-orange-600'
    return 'text-red-600'
  }

  const getImprovementMessage = (improvement) => {
    if (improvement >= 25) return 'Outstanding improvement!'
    if (improvement >= 15) return 'Excellent enhancement!'
    if (improvement >= 10) return 'Great progress!'
    return 'Nice improvement!'
  }

  return (
    <div className="relative">
      <Confetti active={showCelebration && showConfetti} />
      
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="text-center py-8"
      >
        {/* Score Display */}
        <motion.div
          className="relative inline-block"
          animate={isAnimating ? { scale: [1, 1.1, 1] } : {}}
          transition={{ duration: 0.3, repeat: isAnimating ? Infinity : 0 }}
        >
          <div className={`text-6xl font-bold ${getScoreColor(currentScore)}`}>
            {currentScore}
          </div>
          <div className="text-lg text-gray-600 mt-2">ATS Score</div>
          
          {/* Sparkle effects */}
          {showCelebration && (
            <motion.div
              initial={{ scale: 0, rotate: 0 }}
              animate={{ scale: [0, 1.2, 1], rotate: [0, 180, 360] }}
              transition={{ duration: 1, delay: 0.5 }}
              className="absolute -top-4 -right-4"
            >
              <Sparkles className="w-8 h-8 text-yellow-500" />
            </motion.div>
          )}
        </motion.div>

        {/* Improvement Badge */}
        {improvement > 0 && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1 }}
            className="mt-6"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-100 text-green-800 rounded-full">
              <TrendingUp className="w-5 h-5" />
              <span className="font-medium">+{improvement} points</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {getImprovementMessage(improvement)}
            </p>
          </motion.div>
        )}

        {/* Success Message */}
        {showCelebration && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1.5 }}
            className="mt-6"
          >
            <div className="flex items-center justify-center gap-2 text-lg font-medium text-gray-900">
              <CheckCircle className="w-6 h-6 text-green-500" />
              Resume Enhancement Complete!
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

/**
 * Processing completion celebration
 */
const ProcessingCompletionCelebration = ({ 
  jobTitle, 
  processingTime, 
  improvements = [],
  onViewResults,
  onDownload,
  onProcessNext
}) => {
  const [showDetails, setShowDetails] = useState(false)

  const formatProcessingTime = (ms) => {
    const seconds = Math.floor(ms / 1000)
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    return `${minutes}m ${seconds % 60}s`
  }

  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="bg-gradient-to-br from-green-50 to-blue-50 border-2 border-green-200 rounded-xl p-8 text-center"
    >
      {/* Success Icon */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
        className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-6"
      >
        <CheckCircle className="w-8 h-8 text-green-600" />
      </motion.div>

      {/* Title */}
      <motion.h2
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="text-2xl font-bold text-gray-900 mb-2"
      >
        Processing Complete!
      </motion.h2>

      {/* Job Title */}
      <motion.p
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-lg text-gray-700 mb-4"
      >
        {jobTitle}
      </motion.p>

      {/* Processing Time */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm mb-6"
      >
        <Zap className="w-4 h-4" />
        Completed in {formatProcessingTime(processingTime)}
      </motion.div>

      {/* Improvements Summary */}
      {improvements.length > 0 && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1 }}
          className="mb-6"
        >
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-sm font-medium text-blue-600 hover:text-blue-700 mb-3"
          >
            {showDetails ? 'Hide' : 'Show'} Improvements ({improvements.length})
          </button>
          
          <AnimatePresence>
            {showDetails && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="space-y-2 text-left bg-white rounded-lg p-4 border border-gray-200"
              >
                {improvements.map((improvement, index) => (
                  <motion.div
                    key={index}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-2 text-sm"
                  >
                    <Star className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                    <span>{improvement}</span>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Action Buttons */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 1.2 }}
        className="flex flex-col sm:flex-row gap-3 justify-center"
      >
        <button
          onClick={onViewResults}
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          <Eye className="w-5 h-5" />
          View Results
        </button>
        
        <button
          onClick={onDownload}
          className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
        >
          <Download className="w-5 h-5" />
          Download Resume
        </button>
        
        {onProcessNext && (
          <button
            onClick={onProcessNext}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
          >
            Process Next
            <ArrowRight className="w-5 h-5" />
          </button>
        )}
      </motion.div>
    </motion.div>
  )
}

/**
 * Batch completion celebration with statistics
 */
const BatchCompletionCelebration = ({ 
  completedJobs, 
  totalJobs, 
  totalProcessingTime,
  averageImprovement,
  onViewAllResults,
  onDownloadAll
}) => {
  const successRate = Math.round((completedJobs / totalJobs) * 100)
  
  const formatTime = (ms) => {
    const minutes = Math.floor(ms / 60000)
    const seconds = Math.floor((ms % 60000) / 1000)
    return `${minutes}m ${seconds}s`
  }

  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-xl p-8 text-center"
    >
      <Confetti active={true} duration={4000} />
      
      {/* Trophy Icon */}
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
        className="inline-flex items-center justify-center w-20 h-20 bg-yellow-100 rounded-full mb-6"
      >
        <Award className="w-10 h-10 text-yellow-600" />
      </motion.div>

      {/* Title */}
      <motion.h2
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="text-3xl font-bold text-gray-900 mb-2"
      >
        Batch Processing Complete! 🎉
      </motion.h2>

      {/* Statistics */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4 my-8"
      >
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-2xl font-bold text-green-600">{completedJobs}</div>
          <div className="text-sm text-gray-600">Jobs Completed</div>
        </div>
        
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-2xl font-bold text-blue-600">{successRate}%</div>
          <div className="text-sm text-gray-600">Success Rate</div>
        </div>
        
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-2xl font-bold text-purple-600">+{averageImprovement}</div>
          <div className="text-sm text-gray-600">Avg. Improvement</div>
        </div>
        
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-2xl font-bold text-orange-600">{formatTime(totalProcessingTime)}</div>
          <div className="text-sm text-gray-600">Total Time</div>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 1 }}
        className="flex flex-col sm:flex-row gap-3 justify-center"
      >
        <button
          onClick={onViewAllResults}
          className="inline-flex items-center gap-2 px-8 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium text-lg"
        >
          <Eye className="w-6 h-6" />
          View All Results
        </button>
        
        <button
          onClick={onDownloadAll}
          className="inline-flex items-center gap-2 px-8 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium text-lg"
        >
          <Download className="w-6 h-6" />
          Download All Resumes
        </button>
      </motion.div>
    </motion.div>
  )
}

/**
 * Encouraging messages for longer processing times
 */
const EncouragingMessage = ({ processingTime, jobTitle }) => {
  const getEncouragingMessage = (time) => {
    const seconds = Math.floor(time / 1000)
    
    if (seconds < 30) return null
    if (seconds < 60) return "Great things take time! We're crafting the perfect resume for you."
    if (seconds < 120) return "Almost there! We're adding those final touches that make all the difference."
    if (seconds < 180) return "Quality enhancement in progress! Your patience will be rewarded."
    return "We're working extra hard to make your resume shine! Thanks for your patience."
  }

  const message = getEncouragingMessage(processingTime)
  
  if (!message) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4"
    >
      <div className="flex items-center gap-3">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <Sparkles className="w-5 h-5 text-blue-500" />
        </motion.div>
        <div>
          <p className="text-sm font-medium text-blue-800">{message}</p>
          <p className="text-xs text-blue-600 mt-1">Processing: {jobTitle}</p>
        </div>
      </div>
    </motion.div>
  )
}

/**
 * Smooth transition animations between processing states
 */
const ProcessingStateTransition = ({ fromState, toState, children }) => {
  const transitions = {
    'idle-to-processing': {
      initial: { opacity: 0, scale: 0.9 },
      animate: { opacity: 1, scale: 1 },
      exit: { opacity: 0, scale: 1.1 }
    },
    'processing-to-complete': {
      initial: { opacity: 0, y: 20 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: -20 }
    },
    'complete-to-idle': {
      initial: { opacity: 0, scale: 1.1 },
      animate: { opacity: 1, scale: 1 },
      exit: { opacity: 0, scale: 0.9 }
    }
  }

  const transitionKey = `${fromState}-to-${toState}`
  const transition = transitions[transitionKey] || transitions['idle-to-processing']

  return (
    <motion.div
      key={transitionKey}
      initial={transition.initial}
      animate={transition.animate}
      exit={transition.exit}
      transition={{ duration: 0.5, ease: 'easeInOut' }}
    >
      {children}
    </motion.div>
  )
}

export default {
  Confetti,
  ScoreRevealAnimation,
  ProcessingCompletionCelebration,
  BatchCompletionCelebration,
  EncouragingMessage,
  ProcessingStateTransition
}

export {
  Confetti,
  ScoreRevealAnimation,
  ProcessingCompletionCelebration,
  BatchCompletionCelebration,
  EncouragingMessage,
  ProcessingStateTransition
}