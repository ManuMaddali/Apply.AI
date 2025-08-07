import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Globe, CheckCircle, AlertCircle, Clock, Infinity, Lock, Crown } from 'lucide-react'
import { useSubscription } from '../hooks/useSubscription'
import { Button } from '@/components/ui/button'
import { EnhancedCard } from '@/components/ui/enhanced-card'
import { createKeyboardHandler, FocusManager, announceToScreenReader, RovingTabIndex } from '../utils/keyboardNavigation'

const JobOpportunitiesCard = ({ jobUrls, onJobUrlsChange, isProUser }) => {
  const [urlList, setUrlList] = useState([])
  const [newUrl, setNewUrl] = useState('')
  const [validationStates, setValidationStates] = useState({})
  const [inputMode, setInputMode] = useState('url') // 'url' or 'paste'
  const [pasteText, setPasteText] = useState('')
  
  const maxUrls = isProUser ? 10 : 5
  
  // Refs for keyboard navigation
  const cardRef = useRef(null)
  const urlInputRef = useRef(null)
  const pasteTextareaRef = useRef(null)
  const addButtonRef = useRef(null)
  const urlCardsRef = useRef(null)
  const rovingTabIndexRef = useRef(null)
  
  // Parse jobUrls string into array on mount and when it changes
  useEffect(() => {
    if (jobUrls) {
      const urls = jobUrls.trim().split('\n').filter(line => line.trim())
      setUrlList(urls)
      // Initialize validation states for existing URLs
      const initialValidation = {}
      urls.forEach(url => {
        initialValidation[url] = { status: 'pending', title: '', favicon: '' }
      })
      setValidationStates(initialValidation)
      // Validate existing URLs
      urls.forEach(url => validateUrl(url))
    } else {
      setUrlList([])
      setValidationStates({})
    }
  }, [jobUrls])

  // Add URL function - MOVED UP to fix hoisting issue
  const addUrl = useCallback(() => {
    const url = newUrl.trim()
    if (!url) return
    
    // Check tier-based limits
    if (urlList.length >= maxUrls) {
      const message = isProUser 
        ? 'Maximum URL limit reached' 
        : 'Free plan allows up to 5 job URLs. Upgrade to Pro for up to 10 URLs!'
      announceToScreenReader(message)
      if (!isProUser) {
        alert(message)
      }
      return
    }
    
    if (urlList.includes(url)) {
      announceToScreenReader('URL already added')
      setNewUrl('')
      return
    }
    
    const updatedUrls = [...urlList, url]
    setUrlList(updatedUrls)
    onJobUrlsChange(updatedUrls.join('\n'))
    setNewUrl('')
    validateUrl(url)
    announceToScreenReader(`Added job URL. ${updatedUrls.length} of ${maxUrls} URLs added.`)
  }, [newUrl, urlList, maxUrls, isProUser, onJobUrlsChange])

  // Keyboard navigation setup
  useEffect(() => {
    const handleKeyDown = createKeyboardHandler({
      'j': () => {
        if (inputMode === 'url') {
          urlInputRef.current?.focus()
        } else {
          pasteTextareaRef.current?.focus()
        }
        announceToScreenReader('Focused on job input field')
      },
      'Enter': (e) => {
        if (e.target === urlInputRef.current && newUrl.trim()) {
          e.preventDefault()
          addUrl()
        }
      }
    }, { preventDefault: false })

    const cardElement = cardRef.current
    if (cardElement) {
      cardElement.addEventListener('keydown', handleKeyDown)
      return () => cardElement.removeEventListener('keydown', handleKeyDown)
    }
  }, [inputMode, newUrl, addUrl])

  // Set up roving tab index for URL cards
  useEffect(() => {
    if (urlCardsRef.current && urlList.length > 0) {
      rovingTabIndexRef.current = new RovingTabIndex(urlCardsRef.current, {
        selector: '[data-url-card]',
        orientation: 'vertical'
      })
      
      return () => {
        rovingTabIndexRef.current?.destroy()
      }
    }
  }, [urlList.length])

  // Mode switching with keyboard support
  const handleModeSwitch = useCallback((mode) => {
    setInputMode(mode)
    announceToScreenReader(`Switched to ${mode === 'url' ? 'URL input' : 'paste job ad'} mode`)
    
    // Focus appropriate input after mode switch
    setTimeout(() => {
      if (mode === 'url') {
        urlInputRef.current?.focus()
      } else {
        pasteTextareaRef.current?.focus()
      }
    }, 100)
  }, [])

  // URL validation function with mock data
  const validateUrl = async (url) => {
    if (!url.trim()) return

    // Set to validating state
    setValidationStates(prev => ({
      ...prev,
      [url]: { status: 'validating', title: 'Validating...', favicon: '' }
    }))

    try {
      // Basic URL validation
      new URL(url.trim())
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Mock validation results based on URL patterns
      let title = 'Job Posting'
      let favicon = ''
      
      if (url.includes('linkedin.com')) {
        title = 'Software Engineer at Tech Corp'
        favicon = 'https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca'
      } else if (url.includes('indeed.com')) {
        title = 'Frontend Developer Position'
        favicon = 'https://d2q79iu7y748jz.cloudfront.net/s/_squarelogo/256x256/6ce2b9c4b9b8b5e4b8b4b8b4b8b4b8b4.png'
      } else if (url.includes('glassdoor.com')) {
        title = 'Senior Developer Role'
        favicon = 'https://www.glassdoor.com/favicon.ico'
      } else {
        // Extract domain for generic jobs
        const domain = new URL(url).hostname.replace('www.', '')
        title = `Position at ${domain.charAt(0).toUpperCase() + domain.slice(1)}`
        favicon = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`
      }
      
      setValidationStates(prev => ({
        ...prev,
        [url]: { status: 'valid', title, favicon }
      }))
    } catch (error) {
      setValidationStates(prev => ({
        ...prev,
        [url]: { status: 'invalid', title: 'Invalid URL', favicon: '' }
      }))
    }
  }

  const removeUrl = useCallback((urlToRemove) => {
    const updatedUrls = urlList.filter(url => url !== urlToRemove)
    setUrlList(updatedUrls)
    onJobUrlsChange(updatedUrls.join('\n'))
    
    // Remove from validation states
    setValidationStates(prev => {
      const newStates = { ...prev }
      delete newStates[urlToRemove]
      return newStates
    })
    
    announceToScreenReader(`Removed job URL. ${updatedUrls.length} of ${maxUrls} URLs remaining.`)
  }, [urlList, onJobUrlsChange, maxUrls])

  const handlePasteMode = () => {
    if (!pasteText.trim()) return
    
    // Extract URLs from pasted text
    const urlRegex = /https?:\/\/[^\s]+/g
    const extractedUrls = pasteText.match(urlRegex) || []
    
    if (extractedUrls.length === 0) {
      // If no URLs found, create a mock job entry from the description
      const availableSlots = maxUrls - urlList.length
      if (availableSlots > 0) {
        // Create a mock URL for the job description
        const mockUrl = `job-description-${Date.now()}`
        const updatedUrls = [...urlList, mockUrl]
        setUrlList(updatedUrls)
        onJobUrlsChange(updatedUrls.join('\n'))
        
        // Set validation state for the job description
        setValidationStates(prev => ({
          ...prev,
          [mockUrl]: { 
            status: 'valid', 
            title: 'Job Description (Pasted)', 
            favicon: '' 
          }
        }))
      } else {
        alert(`Cannot add more jobs. ${isProUser ? 'Maximum' : 'Free plan'} limit reached.`)
      }
      
      setPasteText('')
      return
    }
    
    // Add extracted URLs (up to limit)
    const availableSlots = maxUrls - urlList.length
    const urlsToAdd = extractedUrls.slice(0, availableSlots).filter(url => !urlList.includes(url))
    
    if (urlsToAdd.length > 0) {
      const updatedUrls = [...urlList, ...urlsToAdd]
      setUrlList(updatedUrls)
      onJobUrlsChange(updatedUrls.join('\n'))
      
      // Validate new URLs
      urlsToAdd.forEach(url => validateUrl(url))
      
      // Show success message
      if (extractedUrls.length > urlsToAdd.length) {
        alert(`Added ${urlsToAdd.length} URLs. ${extractedUrls.length - urlsToAdd.length} URLs were skipped (duplicates or limit reached).`)
      }
    } else if (extractedUrls.length > 0) {
      alert('All extracted URLs are already added or limit reached.')
    }
    
    setPasteText('')
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'valid':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'invalid':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'validating':
        return <Clock className="h-4 w-4 text-yellow-500 animate-spin" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  return (
    <EnhancedCard 
      ref={cardRef}
      className="p-6"
      role="region"
      aria-label="Job opportunities section"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl shadow-lg">
            <Globe className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Job Opportunities</h2>
            <p className="text-sm text-gray-600 mt-1">
              Add job URLs to tailor your resume for each position
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {isProUser && (
            <div className="flex items-center gap-1 text-purple-600 bg-purple-50 px-3 py-1 rounded-full text-sm font-medium">
              <Infinity className="h-4 w-4" />
              <span>Pro</span>
            </div>
          )}
          <div className="text-sm font-semibold px-3 py-1 rounded-full bg-gray-100 text-gray-700">
            {urlList.length}/{maxUrls}
          </div>
        </div>
      </div>

      {/* Input Mode Toggle */}
      <div 
        className="flex gap-2 mb-4"
        role="tablist"
        aria-label="Job input methods"
      >
        <Button
          variant={inputMode === 'url' ? 'default' : 'outline'}
          size="sm"
          onClick={() => handleModeSwitch('url')}
          className="flex-1"
          role="tab"
          aria-selected={inputMode === 'url'}
          aria-controls="url-input-panel"
          id="url-input-tab"
        >
          Add URLs
        </Button>
        <Button
          variant={inputMode === 'paste' ? 'default' : 'outline'}
          size="sm"
          onClick={() => handleModeSwitch('paste')}
          className="flex-1"
          role="tab"
          aria-selected={inputMode === 'paste'}
          aria-controls="paste-input-panel"
          id="paste-input-tab"
        >
          Paste Job Ad
        </Button>
      </div>

      {/* URL Input Mode */}
      {inputMode === 'url' && (
        <div 
          className="space-y-4"
          role="tabpanel"
          id="url-input-panel"
          aria-labelledby="url-input-tab"
        >
          <div className="flex gap-2">
            <input
              ref={urlInputRef}
              type="url"
              value={newUrl}
              onChange={(e) => setNewUrl(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addUrl()}
              placeholder="https://example.com/job-posting"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent hover:border-purple-300 hover:shadow-sm transition-all duration-200 disabled:bg-gray-100 disabled:cursor-not-allowed disabled:hover:border-gray-300 disabled:hover:shadow-none"
              disabled={urlList.length >= maxUrls}
              aria-label="Job URL input"
              aria-describedby="url-input-help"
            />
            <Button
              ref={addButtonRef}
              onClick={addUrl}
              disabled={!newUrl.trim() || urlList.length >= maxUrls}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 hover:shadow-lg hover:shadow-blue-500/25 hover:shadow-blue-400/50 hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none"
              aria-describedby="add-button-help"
            >
              Add Job
            </Button>
          </div>
          
          <div className="text-xs text-gray-500 space-y-1">
            <div id="url-input-help">Press Enter to add URL, or press 'J' to focus this field</div>
            <div id="add-button-help">
              {urlList.length}/{maxUrls} URLs added
              {!isProUser && urlList.length >= 3 && ' (approaching free plan limit)'}
            </div>
          </div>
          
          {/* Tier-based limit warning */}
          {!isProUser && urlList.length >= 3 && (
            <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <AlertCircle className="h-4 w-4 text-yellow-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-yellow-800">
                  Approaching free plan limit ({urlList.length}/{maxUrls})
                </p>
                <p className="text-xs text-yellow-700 mt-1">
                  Upgrade to Pro for up to 10 job URLs
                </p>
              </div>
              <Button
                size="sm"
                variant="outline"
                className="border-yellow-300 text-yellow-700 hover:bg-yellow-100"
                onClick={() => window.open('/pricing', '_blank')}
              >
                Upgrade
              </Button>
            </div>
          )}
          
          {urlList.length >= maxUrls && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
              <Lock className="h-4 w-4 text-red-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-800">
                  {isProUser ? 'Maximum URLs reached' : 'Free plan limit reached'}
                </p>
                <p className="text-xs text-red-700 mt-1">
                  {isProUser 
                    ? 'Remove a URL to add a new one' 
                    : 'Upgrade to Pro for up to 10 job URLs'
                  }
                </p>
              </div>
              {!isProUser && (
                <Button
                  size="sm"
                  variant="outline"
                  className="border-red-300 text-red-700 hover:bg-red-100"
                  onClick={() => window.open('/pricing', '_blank')}
                >
                  Upgrade
                </Button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Paste Mode */}
      {inputMode === 'paste' && (
        <div 
          className="space-y-4"
          role="tabpanel"
          id="paste-input-panel"
          aria-labelledby="paste-input-tab"
        >
          <div className="relative">
            <textarea
              ref={pasteTextareaRef}
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
              placeholder={`Paste job description or URLs here...

You can:
• Paste full job descriptions (we'll extract key requirements)
• Paste multiple URLs (one per line)
• Mix job descriptions and URLs

${!isProUser ? 'Free plan: First 5 URLs will be processed' : 'Pro plan: Up to 10 URLs supported'}`}
              rows={6}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent hover:border-purple-300 hover:shadow-sm transition-all duration-200 resize-none bg-gradient-to-br from-gray-50/50 to-purple-50/30"
              aria-label="Job description or URLs paste area"
              aria-describedby="paste-textarea-help"
            />
            
            {/* Character counter */}
            <div className="absolute bottom-3 right-3 text-xs text-gray-500 bg-white/80 px-2 py-1 rounded" aria-live="polite">
              {pasteText.length} chars
            </div>
          </div>
          
          <div id="paste-textarea-help" className="text-xs text-gray-500">
            Paste job descriptions or URLs. Press 'J' to focus this field.
          </div>
          
          <div className="flex gap-2">
            <Button
              onClick={handlePasteMode}
              disabled={!pasteText.trim()}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 hover:shadow-lg hover:shadow-blue-500/25 hover:shadow-blue-400/50 hover:scale-105 transition-all duration-200 flex-1 disabled:hover:scale-100 disabled:hover:shadow-none"
            >
              Process Content
            </Button>
            <Button
              variant="outline"
              onClick={() => setPasteText('')}
              disabled={!pasteText.trim()}
              className="px-4"
            >
              Clear
            </Button>
          </div>
          
          {/* Help text */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">Smart Content Processing</p>
                <ul className="text-xs space-y-1 text-blue-700">
                  <li>• Automatically extracts URLs from mixed content</li>
                  <li>• Processes job descriptions for key requirements</li>
                  <li>• Handles multiple formats and sources</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* URL Cards */}
      <div 
        ref={urlCardsRef}
        className="space-y-3 mt-6"
        role="list"
        aria-label="Added job URLs"
      >
        <AnimatePresence>
          {urlList.map((url, index) => {
            const validation = validationStates[url] || { status: 'pending', title: '', favicon: '' }
            
            return (
              <motion.div
                key={url}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-md hover:bg-white transition-all duration-200"
                role="listitem"
                data-url-card
                tabIndex={index === 0 ? 0 : -1}
                aria-label={`Job URL ${index + 1}: ${validation.title || url}`}
                onKeyDown={(e) => {
                  if (e.key === 'Delete' || e.key === 'Backspace') {
                    e.preventDefault()
                    removeUrl(url)
                  }
                }}
              >
                {/* Favicon */}
                <div className="flex-shrink-0 w-8 h-8 bg-white rounded border border-gray-200 flex items-center justify-center">
                  {validation.favicon ? (
                    <img
                      src={validation.favicon}
                      alt=""
                      className="w-4 h-4"
                      onError={(e) => {
                        e.target.style.display = 'none'
                        e.target.nextSibling.style.display = 'block'
                      }}
                    />
                  ) : null}
                  <Globe className="w-4 h-4 text-gray-400" style={{ display: validation.favicon ? 'none' : 'block' }} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(validation.status)}
                    <p className="font-medium text-gray-900 truncate">
                      {validation.title || 'Loading...'}
                    </p>
                  </div>
                  <p className="text-sm text-gray-500 truncate">{url}</p>
                </div>

                {/* Remove Button */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeUrl(url)}
                  className="flex-shrink-0 text-gray-400 hover:text-red-500 hover:bg-red-50"
                  aria-label={`Remove job URL: ${validation.title || url}`}
                  title="Press Delete or Backspace to remove when focused on URL card"
                >
                  <X className="h-4 w-4" />
                </Button>
              </motion.div>
            )
          })}
        </AnimatePresence>

        {/* Empty Slots for Free Users */}
        {!isProUser && urlList.length < maxUrls && (
          <div className="space-y-3">
            {Array.from({ length: maxUrls - urlList.length }, (_, index) => (
              <motion.div
                key={`empty-${index}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="relative group"
              >
                <div className="flex items-center gap-3 p-3 bg-gray-100/50 rounded-lg border-2 border-dashed border-gray-300 opacity-60">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded border border-gray-300 flex items-center justify-center">
                    <Globe className="w-4 h-4 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-500">Available slot</p>
                    <p className="text-sm text-gray-400">Add more job URLs</p>
                  </div>
                </div>
                
                {/* Upgrade Tooltip */}
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-lg p-3 border border-purple-200 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 whitespace-nowrap">
                    <div className="flex items-center gap-2 text-sm">
                      <Crown className="h-4 w-4 text-purple-600" />
                      <span className="font-medium text-gray-900">Upgrade to Pro</span>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">Get up to 10 job URLs</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Pro User Infinity Badge */}
        {isProUser && urlList.length >= 5 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center justify-center gap-2 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200"
          >
            <Infinity className="h-5 w-5 text-purple-600" />
            <span className="text-sm font-medium text-purple-700">
              Pro User - Add up to {maxUrls} job URLs
            </span>
          </motion.div>
        )}
      </div>

      {/* Empty State */}
      {urlList.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Globe className="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p className="text-sm">No job URLs added yet</p>
          <p className="text-xs mt-1">Add job posting URLs to get started</p>
        </div>
      )}

      {/* Supported Platforms */}
      <div className="mt-6 bg-gradient-to-r from-purple-50/50 to-pink-50/50 rounded-xl p-4 border border-purple-100/50">
        <div className="flex items-center gap-3 mb-3">
          <CheckCircle className="w-5 h-5 text-purple-600" />
          <span className="text-sm font-semibold text-gray-900">Supported Platforms</span>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="flex items-center gap-2 p-2 bg-white/60 rounded-lg">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-700 font-medium">LinkedIn</span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-white/60 rounded-lg">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-700 font-medium">Company Sites</span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-white/60 rounded-lg">
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
            <span className="text-sm text-gray-700 font-medium">Job Boards</span>
          </div>
        </div>
      </div>
    </EnhancedCard>
  )
}

export default JobOpportunitiesCard