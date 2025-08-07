import React, { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, FileType, FolderOpen, Download, ChevronDown, ChevronUp, RotateCcw, Zap } from 'lucide-react'
import { Button } from './ui/button'
import { EnhancedCard } from './ui/enhanced-card'
import { createKeyboardHandler, announceToScreenReader, A11yUtils } from '../utils/keyboardNavigation'

const OutputFormatCard = ({ 
  outputFormat, 
  onFormatChange, 
  results = [], 
  onViewResume,
  onDownloadPDF,
  onDownloadCoverLetter,
  onDownloadText,
  includeCoverLetter = false,
  tailoringMode = 'light',
  processing = false,
  canSubmit = false,
  onSubmit,
  loading = false,
  batchStatus = null,
  safeHasExceededLimit = false
}) => {
  const [expandedResults, setExpandedResults] = useState({})
  const [showComparison, setShowComparison] = useState({})
  
  // Refs for ARIA and keyboard navigation
  const cardRef = useRef(null)
  const formatButtonsRef = useRef(null)
  const resultsRef = useRef(null)
  const processingStatusRef = useRef(null)

  // Format options with icons
  const formatOptions = [
    { value: 'text', label: 'PDF', icon: FileText, description: 'Professional PDF format' },
    { value: 'docx', label: 'Word', icon: FileType, description: 'Editable Word document' },
    { value: 'files', label: 'Both', icon: FolderOpen, description: 'PDF + Word formats' }
  ]

  const toggleResultExpansion = useCallback((resultId) => {
    setExpandedResults(prev => {
      const newState = {
        ...prev,
        [resultId]: !prev[resultId]
      }
      const isExpanded = newState[resultId]
      announceToScreenReader(`Result ${isExpanded ? 'expanded' : 'collapsed'}`)
      return newState
    })
  }, [])

  const toggleComparison = useCallback((resultId) => {
    setShowComparison(prev => {
      const newState = {
        ...prev,
        [resultId]: !prev[resultId]
      }
      const isShowing = newState[resultId]
      announceToScreenReader(`Comparison view ${isShowing ? 'shown' : 'hidden'}`)
      return newState
    })
  }, [])

  // Keyboard navigation setup
  useEffect(() => {
    const handleKeyDown = createKeyboardHandler({
      'f': () => {
        // Cycle through format options
        const formats = ['text', 'docx', 'files']
        const currentIndex = formats.indexOf(outputFormat)
        const nextIndex = (currentIndex + 1) % formats.length
        onFormatChange(formats[nextIndex])
        announceToScreenReader(`Format changed to ${formats[nextIndex]}`)
      }
    }, { preventDefault: false })

    const cardElement = cardRef.current
    if (cardElement) {
      cardElement.addEventListener('keydown', handleKeyDown)
      return () => cardElement.removeEventListener('keydown', handleKeyDown)
    }
  }, [outputFormat, onFormatChange])

  // Announce processing status changes
  useEffect(() => {
    if (processing && batchStatus) {
      const message = `Processing ${batchStatus.completed || 0} of ${batchStatus.total} jobs. ${batchStatus.current_job || 'Working on your resumes'}`
      announceToScreenReader(message, 'assertive')
    } else if (!processing && results.length > 0) {
      announceToScreenReader(`Processing complete. ${results.length} results available for download.`)
    }
  }, [processing, batchStatus, results.length])

  return (
    <EnhancedCard 
      ref={cardRef}
      className="space-y-6"
      role="region"
      aria-label="Output format and results section"
    >
      <div className="flex items-center gap-4">
        <div className="p-3 bg-gradient-to-r from-green-500 to-teal-600 rounded-xl shadow-lg">
          <Download className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Output Format</h2>
          <p className="text-sm text-gray-600 mt-1">Choose format and view results</p>
        </div>
      </div>

      {/* Segmented Format Selection Buttons */}
      <div className="space-y-4">
        <label 
          id="format-selection-label"
          className="block text-sm font-medium text-gray-700"
        >
          Download Format
        </label>
        <div 
          ref={formatButtonsRef}
          className="flex bg-gray-100 rounded-lg p-1 gap-1"
          role="radiogroup"
          aria-labelledby="format-selection-label"
          aria-describedby="format-description"
        >
          {formatOptions.map((option) => {
            const Icon = option.icon
            const isSelected = outputFormat === option.value
            
            return (
              <motion.button
                key={option.value}
                onClick={() => {
                  onFormatChange(option.value)
                  announceToScreenReader(`Selected ${option.label} format`)
                }}
                className={`
                  flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-md text-sm font-medium transition-all duration-200
                  ${isSelected 
                    ? 'bg-white text-purple-600 shadow-sm border border-purple-200' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }
                `}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                role="radio"
                aria-checked={isSelected}
                aria-describedby={`format-${option.value}-description`}
                tabIndex={isSelected ? 0 : -1}
              >
                <Icon className="w-4 h-4" aria-hidden="true" />
                <span>{option.label}</span>
              </motion.button>
            )
          })}
        </div>
        
        {/* Format description */}
        <div 
          id="format-description"
          className="text-xs text-gray-500 text-center"
          aria-live="polite"
        >
          {formatOptions.find(opt => opt.value === outputFormat)?.description}
        </div>
        
        <div className="text-xs text-gray-500 text-center">
          Press 'F' to cycle through format options
        </div>
      </div>

      {/* Results Section */}
      {results.length > 0 && (
        <div className="space-y-4" ref={resultsRef}>
          <div className="flex items-center justify-between">
            <h3 
              id="results-heading"
              className="text-lg font-semibold text-gray-900"
            >
              Results
            </h3>
            <span 
              className="text-sm text-gray-500"
              aria-label={`${results.length} job result${results.length !== 1 ? 's' : ''} available`}
            >
              {results.length} job{results.length !== 1 ? 's' : ''}
            </span>
          </div>
          
          <div 
            className="space-y-3"
            role="list"
            aria-labelledby="results-heading"
          >
            {results.map((result, index) => (
              <ResultCard
                key={result.id || index}
                result={result}
                index={index}
                isExpanded={expandedResults[result.id || index]}
                showComparison={showComparison[result.id || index]}
                onToggleExpansion={() => toggleResultExpansion(result.id || index)}
                onToggleComparison={() => toggleComparison(result.id || index)}
                onDownload={onDownload}
                outputFormat={outputFormat}
              />
            ))}
          </div>
        </div>
      )}

      {/* Enhanced Processing State with Progress */}
      {processing && (
        <div 
          className="space-y-4"
          ref={processingStatusRef}
          role="status"
          aria-live="polite"
          aria-label="Resume processing status"
        >
          <div className="text-center py-6">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="w-12 h-12 border-3 border-purple-600 border-t-transparent rounded-full mx-auto mb-4"
              aria-hidden="true"
            />
            <h3 
              id="processing-heading"
              className="text-lg font-semibold text-gray-900 mb-2"
            >
              Processing Your Resumes
            </h3>
            <p 
              className="text-gray-600 mb-4"
              aria-live="polite"
              id="processing-status"
            >
              {batchStatus?.current_job || 'Analyzing job requirements and tailoring your resume...'}
            </p>
            
            {/* Progress Bar */}
            {batchStatus && batchStatus.total > 0 && (
              <div className="max-w-md mx-auto">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span aria-live="polite">
                    {batchStatus.completed || 0} of {batchStatus.total}
                  </span>
                </div>
                <div 
                  className="w-full bg-gray-200 rounded-full h-2"
                  role="progressbar"
                  aria-valuenow={batchStatus.completed || 0}
                  aria-valuemin={0}
                  aria-valuemax={batchStatus.total}
                  aria-label={`Processing progress: ${batchStatus.completed || 0} of ${batchStatus.total} jobs completed`}
                >
                  <motion.div
                    className="bg-gradient-to-r from-purple-600 to-blue-600 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ 
                      width: `${((batchStatus.completed || 0) / batchStatus.total) * 100}%` 
                    }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                  />
                </div>
              </div>
            )}
          </div>
          
          {/* Processing Steps Indicator */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 
              id="processing-steps-heading"
              className="font-medium text-gray-900 mb-3"
            >
              Processing Steps
            </h4>
            <div 
              className="space-y-2"
              role="list"
              aria-labelledby="processing-steps-heading"
            >
              {[
                { step: 'Analyzing job requirements', completed: batchStatus?.completed >= 0 },
                { step: 'Extracting key skills and keywords', completed: batchStatus?.completed >= 1 },
                { step: 'Tailoring resume content', completed: batchStatus?.completed >= 2 },
                { step: 'Optimizing for ATS systems', completed: batchStatus?.completed >= 3 },
                { step: 'Finalizing documents', completed: batchStatus?.state === 'completed' }
              ].map((item, index) => (
                <div 
                  key={index} 
                  className="flex items-center gap-3"
                  role="listitem"
                  aria-label={`Step ${index + 1}: ${item.step} - ${
                    item.completed ? 'completed' : 
                    batchStatus?.completed === index ? 'in progress' : 'pending'
                  }`}
                >
                  <div 
                    className={`w-4 h-4 rounded-full flex items-center justify-center ${
                      item.completed 
                        ? 'bg-green-500' 
                        : batchStatus?.completed === index 
                          ? 'bg-purple-600' 
                          : 'bg-gray-300'
                    }`}
                    aria-hidden="true"
                  >
                    {item.completed ? (
                      <motion.svg 
                        className="w-3 h-3 text-white" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.3 }}
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </motion.svg>
                    ) : batchStatus?.completed === index ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-2 h-2 border border-white border-t-transparent rounded-full"
                      />
                    ) : null}
                  </div>
                  <span className={`text-sm ${
                    item.completed 
                      ? 'text-green-700 font-medium' 
                      : batchStatus?.completed === index 
                        ? 'text-purple-700 font-medium' 
                        : 'text-gray-500'
                  }`}>
                    {item.step}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </EnhancedCard>
  )
}

// Individual Result Card Component
const ResultCard = ({ 
  result, 
  index,
  isExpanded, 
  showComparison, 
  onToggleExpansion, 
  onToggleComparison, 
  onDownload,
  outputFormat 
}) => {
  const mockAddedKeywords = result.added_keywords || [
    "React", "JavaScript", "Node.js", "API Development", "Team Leadership"
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50 border-green-200'
      case 'processing': return 'text-purple-600 bg-purple-50 border-purple-200'
      case 'failed': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': 
        return (
          <motion.svg 
            className="w-4 h-4 text-green-600" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </motion.svg>
        )
      case 'processing': 
        return (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full"
          />
        )
      case 'failed': 
        return (
          <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )
      default: 
        return (
          <div className="w-4 h-4 bg-gray-300 rounded-full" />
        )
    }
  }

  const cardId = `result-card-${result.id || index}`
  const headerId = `${cardId}-header`
  const contentId = `${cardId}-content`

  return (
    <motion.div
      layout
      className="border border-gray-200 rounded-lg bg-white hover:shadow-md transition-all duration-200"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      role="listitem"
      aria-labelledby={headerId}
    >
      {/* Card Header */}
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div aria-label={`Status: ${result.status}`}>
                {getStatusIcon(result.status)}
              </div>
              <h4 
                id={headerId}
                className="font-medium text-gray-900 truncate"
              >
                {result.job_title || 'Processing...'}
              </h4>
            </div>
            <p 
              className="text-sm text-gray-500 truncate"
              aria-label={`Job URL: ${result.job_url}`}
            >
              {result.job_url}
            </p>
            
            {/* Status Badge */}
            <div className="mt-2">
              <span 
                className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(result.status)}`}
                role="status"
                aria-label={`Processing status: ${
                  result.status === 'processing' ? 'Processing' : 
                  result.status === 'completed' ? 'Completed' :
                  result.status === 'failed' ? 'Failed' : 'Pending'
                }`}
              >
                {result.status === 'processing' ? 'Processing...' : 
                 result.status === 'completed' ? 'Completed' :
                 result.status === 'failed' ? 'Failed' : 'Pending'}
              </span>
            </div>
            
            {result.status === 'completed' && (
              <div className="flex items-center gap-2 mt-2">
                <div 
                  className="flex items-center gap-1 text-xs text-green-600"
                  aria-label={`Transformation score: ${result.transformation_score || 85} percent`}
                >
                  <Zap className="w-3 h-3" aria-hidden="true" />
                  <span>Transformation Score: {result.transformation_score || 85}%</span>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {result.status === 'completed' && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onToggleComparison}
                  className="text-xs"
                  aria-label={`${showComparison ? 'Hide' : 'Show'} comparison for ${result.job_title}`}
                  aria-pressed={showComparison}
                >
                  <RotateCcw className="w-3 h-3 mr-1" aria-hidden="true" />
                  Compare
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    onDownload && onDownload(result, outputFormat)
                    announceToScreenReader(`Downloading ${result.job_title} resume`)
                  }}
                  className="text-xs"
                  aria-label={`Download resume for ${result.job_title}`}
                >
                  <Download className="w-3 h-3 mr-1" aria-hidden="true" />
                  Download
                </Button>
              </>
            )}
            
            {result.status === 'failed' && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  window.location.reload()
                  announceToScreenReader('Retrying failed job processing')
                }}
                className="text-xs text-red-600 border-red-200 hover:bg-red-50"
                aria-label={`Retry processing for ${result.job_title}`}
              >
                Retry
              </Button>
            )}
            
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleExpansion}
              className="p-1"
              aria-label={`${isExpanded ? 'Collapse' : 'Expand'} details for ${result.job_title}`}
              aria-expanded={isExpanded}
              aria-controls={contentId}
            >
              {isExpanded ? 
                <ChevronUp className="w-4 h-4" aria-hidden="true" /> : 
                <ChevronDown className="w-4 h-4" aria-hidden="true" />
              }
            </Button>
          </div>
        </div>
      </div>

      {/* Expandable Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            id={contentId}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-gray-200 overflow-hidden"
            role="region"
            aria-label={`Detailed view for ${result.job_title}`}
          >
            <div className="p-4 space-y-4">
              {/* Mock PDF Thumbnail */}
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div 
                    className="w-20 h-26 border border-gray-200 rounded shadow-sm bg-gray-100 flex items-center justify-center"
                  >
                    <FileText className="w-8 h-8 text-gray-400" />
                  </div>
                </div>
                <div className="flex-1">
                  <h5 className="font-medium text-gray-900 mb-2">Resume Preview</h5>
                  <p className="text-sm text-gray-600 line-clamp-3">
                    {result.tailored_resume ? 
                      result.tailored_resume.substring(0, 150) + '...' : 
                      'Resume content will appear here after processing...'
                    }
                  </p>
                </div>
              </div>

              {/* Comparison View */}
              <AnimatePresence>
                {showComparison && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-4"
                  >
                    <div className="border-t border-gray-200 pt-4">
                      <h5 className="font-medium text-gray-900 mb-3">Transformation Highlights</h5>
                      
                      {/* Added Keywords */}
                      <div className="mb-4">
                        <h6 className="text-sm font-medium text-gray-700 mb-2">Added Keywords</h6>
                        <div className="flex flex-wrap gap-2">
                          {mockAddedKeywords.map((keyword, index) => (
                            <span 
                              key={index}
                              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Side-by-side comparison */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h6 className="text-sm font-medium text-gray-700 mb-2">Original</h6>
                          <div className="bg-gray-50 p-3 rounded text-xs text-gray-600 max-h-32 overflow-y-auto">
                            Original resume content would appear here...
                          </div>
                        </div>
                        <div>
                          <h6 className="text-sm font-medium text-gray-700 mb-2">Tailored</h6>
                          <div className="bg-blue-50 p-3 rounded text-xs text-gray-600 max-h-32 overflow-y-auto">
                            {result.tailored_resume ? 
                              result.tailored_resume.substring(0, 200) + '...' : 
                              'Tailored resume content would appear here...'
                            }
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default OutputFormatCard