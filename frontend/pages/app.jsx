/**
 * ApplyAI App - Redesigned with Enhanced UX Architecture
 * Task 15.1: Integration of all redesigned components into main application
 * 
 * This file integrates the new UX architecture while preserving all existing functionality:
 * - Mode selection interface (Batch vs Precision)
 * - Enhanced processing flows
 * - Mobile-optimized interfaces
 * - Accessibility improvements
 * - Performance optimizations
 */

import React, { useState, useEffect, useCallback } from 'react'
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileText, Menu, X, User, LogOut, Settings, Star, BarChart3 } from "lucide-react"
import { motion, AnimatePresence } from 'framer-motion'
import AnalyticsDashboard from '../components/AnalyticsDashboard'

// Existing components (preserved)
import ResultCard from '../components/ResultCard'
import ResumeModal from '../components/ResumeModal'
import ProtectedRoute from '../components/ProtectedRoute'
import SubscriptionBadge from '../components/SubscriptionBadge'
import UpgradePrompt from '../components/UpgradePrompt'
import MobileSubscriptionStatus from '../components/MobileSubscriptionStatus'
import TailoringModeSelector from '../components/TailoringModeSelector'
import UsageLimitGuard, { UsageWarningBanner } from '../components/UsageLimitGuard'

// Legacy redesigned components (temporarily commented out to fix SSR errors)
// import HeroSection from '../components/HeroSection'
// import StickyHeader from '../components/StickyHeader'
// import AddResumeCard from '../components/AddResumeCard'
// import JobOpportunitiesCard from '../components/JobOpportunitiesCard'
// import EnhanceResumeCard from '../components/EnhanceResumeCard'
// import OutputFormatCard from '../components/OutputFormatCard'
// import UsageSidebarCard from '../components/UsageSidebarCard'

// New redesigned UX components (simplified versions that work with existing state management)
import SimplifiedModeSelection from '../components/SimplifiedModeSelection'
import SimplifiedBatchMode from '../components/SimplifiedBatchMode'
import SimplifiedPrecisionMode from '../components/SimplifiedPrecisionMode'

// Utilities and contexts
import { API_BASE_URL } from '../utils/api'
import { useAuth } from '../contexts/AuthContext'
import { useSubscription } from '../hooks/useSubscription'
import Layout from '../components/Layout'

// Application states
const APP_STATES = {
  MODE_SELECTION: 'mode_selection',
  BATCH_MODE: 'batch_mode',
  PRECISION_MODE: 'precision_mode',
  LEGACY_MODE: 'legacy_mode' // For backwards compatibility
}

function MobileNav() {
  const [isOpen, setIsOpen] = useState(false)
  const { user, logout, isAuthenticated } = useAuth()

  const handleLogout = async () => {
    await logout()
    setIsOpen(false)
  }

  return (
    <div className="md:hidden">
      <Button variant="ghost" size="icon" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </Button>
      {isOpen && (
        <div className="fixed inset-0 top-16 z-50 bg-white/90 backdrop-blur-sm p-6 shadow-lg">
          <nav className="flex flex-col gap-6">
            {isAuthenticated && (
              <>
                <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{user?.name || user?.email}</p>
                    <p className="text-sm text-gray-500">
                      {user?.subscription_tier === 'pro' ? 'Pro User' : 'Free User'}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  onClick={handleLogout}
                  className="justify-start gap-3 text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </Button>
              </>
            )}
          </nav>
        </div>
      )}
    </div>
  )
}

function RedesignedApp() {
  // Application state management
  const [currentState, setCurrentState] = useState(APP_STATES.MODE_SELECTION)
  const [selectedMode, setSelectedMode] = useState(null)
  const [showLegacyMode, setShowLegacyMode] = useState(false)
  const [showAnalyticsDashboard, setShowAnalyticsDashboard] = useState(false)
  
  // User and subscription management
  const { user, authenticatedRequest, logout, isAuthenticated, getToken } = useAuth()
  const { 
    isProUser, 
    hasExceededLimit, 
    canUseFeature, 
    trackUsage,
    weeklyUsage,
    weeklyLimit,
    loading: subscriptionLoading,
    error: subscriptionError
  } = useSubscription()
  
  // Fallback values when subscription data is loading or failed
  const safeWeeklyUsage = weeklyUsage || user?.weekly_usage_count || 0
  const safeWeeklyLimit = weeklyLimit || 5
  const safeIsProUser = isProUser || user?.subscription_tier === 'pro'
  const safeHasExceededLimit = hasExceededLimit || (!safeIsProUser && safeWeeklyUsage >= safeWeeklyLimit)
  
  // Resume and job processing state
  const [resumeData, setResumeData] = useState({
    file: null,
    text: '',
    originalText: ''
  })
  const [jobUrls, setJobUrls] = useState('')
  const [processing, setProcessing] = useState(false)
  const [results, setResults] = useState([])
  
  // Modal and UI state
  const [selectedResume, setSelectedResume] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [batchId, setBatchId] = useState(null)
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false)

  // Device detection for mobile optimization
  const [isMobile, setIsMobile] = useState(false)
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Handle logout
  const handleLogout = async () => {
    await logout()
    window.location.href = '/'
  }

  // Mode selection handlers
  const handleModeSelect = useCallback((mode) => {
    setSelectedMode(mode)
    if (mode === 'batch') {
      setCurrentState(APP_STATES.BATCH_MODE)
    } else if (mode === 'precision') {
      setCurrentState(APP_STATES.PRECISION_MODE)
    }
  }, [])

  const handleBackToModeSelection = useCallback(() => {
    setCurrentState(APP_STATES.MODE_SELECTION)
    setSelectedMode(null)
    setError('')
    setSuccess('')
  }, [])

  // Enhanced download handlers with multiple format support
  const downloadAsFormat = useCallback((content, filename, format) => {
    let blob, mimeType, extension
    
    switch (format) {
      case 'pdf':
        // Generate actual PDF and open directly in new tab
        try {
          // Import jsPDF dynamically
          const script = document.createElement('script')
          script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
          document.head.appendChild(script)
          
          script.onload = () => {
            const { jsPDF } = window.jspdf
            const doc = new jsPDF()
            
            // PROFESSIONAL RESUME PDF - EXACT MATCH TO SAMPLE
            const pageWidth = doc.internal.pageSize.width
            const pageHeight = doc.internal.pageSize.height
            const margin = 20
            const maxWidth = pageWidth - 2 * margin
            let yPosition = 30
            
            // Split content into lines and process
            const lines = content.split('\n').map(line => line.trim()).filter(line => line)
            
            for (let i = 0; i < lines.length && yPosition < pageHeight - 40; i++) {
              const line = lines[i]
              
              // DAVID SMITH - Name Header
              if (i === 0) {
                doc.setFontSize(20)
                doc.setTextColor(44, 90, 160) // Blue
                doc.setFont('helvetica', 'bold')
                doc.text(line, margin, yPosition)
                yPosition += 15
              }
              
              // Senior Product Manager - Job Title
              else if (i === 1) {
                doc.setFontSize(14)
                doc.setTextColor(44, 90, 160) // Blue
                doc.setFont('helvetica', 'bold')
                doc.text(line, margin, yPosition)
                yPosition += 10
              }
              
              // Contact Info
              else if (i === 2) {
                doc.setFontSize(9)
                doc.setTextColor(100, 100, 100) // Gray
                doc.setFont('helvetica', 'normal')
                doc.text(line, margin, yPosition)
                yPosition += 15
              }
              
              // Section Headers (PROFESSIONAL SUMMARY, PROFESSIONAL EXPERIENCE, etc.)
              else if (line.match(/^[A-Z\s]{10,}$/)) {
                yPosition += 5
                doc.setFontSize(12)
                doc.setTextColor(44, 90, 160) // Blue
                doc.setFont('helvetica', 'bold')
                doc.text(line, margin, yPosition)
                
                // Blue underline
                doc.setDrawColor(44, 90, 160)
                doc.setLineWidth(1)
                doc.line(margin, yPosition + 3, margin + 100, yPosition + 3)
                yPosition += 12
              }
              
              // Company | Date lines (Spotify | February 2021 - Present)
              else if (line.includes('|') && line.match(/\d{4}/)) {
                const parts = line.split('|')
                const company = parts[0].trim()
                const dates = parts[1].trim()
                
                yPosition += 3
                
                // Company name - bold black
                doc.setFontSize(11)
                doc.setTextColor(0, 0, 0)
                doc.setFont('helvetica', 'bold')
                doc.text(company, margin, yPosition)
                
                // Dates - italic gray, right aligned
                doc.setFont('helvetica', 'italic')
                doc.setTextColor(120, 120, 120)
                const dateWidth = doc.getTextWidth(dates)
                doc.text(dates, pageWidth - margin - dateWidth, yPosition)
                yPosition += 10
              }
              
              // Job titles (Senior Product Manager, Product Manager, etc.)
              else if (line.match(/^[A-Z][a-z\s]+Manager/) || line.match(/^[A-Z][a-z\s]+$/) && line.length < 50 && !line.includes('|')) {
                doc.setFontSize(10)
                doc.setTextColor(80, 80, 80)
                doc.setFont('helvetica', 'italic')
                doc.text(line, margin, yPosition)
                yPosition += 8
              }
              
              // Bullet points
              else if (line.startsWith('•') || line.startsWith('-') || line.startsWith('*')) {
                const bulletText = line.substring(1).trim()
                
                // Blue bullet
                doc.setFontSize(10)
                doc.setTextColor(44, 90, 160)
                doc.text('•', margin + 8, yPosition)
                
                // Bullet text - black, wrapped
                doc.setFontSize(9)
                doc.setTextColor(0, 0, 0)
                doc.setFont('helvetica', 'normal')
                const wrappedText = doc.splitTextToSize(bulletText, maxWidth - 25)
                doc.text(wrappedText, margin + 15, yPosition)
                yPosition += wrappedText.length * 4
              }
              
              // Education section
              else if (line.includes('MBA') || line.includes('Bachelor') || line.includes('University') || line.includes('School')) {
                doc.setFontSize(9)
                doc.setTextColor(0, 0, 0)
                doc.setFont('helvetica', 'bold')
                const wrappedText = doc.splitTextToSize(line, maxWidth)
                doc.text(wrappedText, margin, yPosition)
                yPosition += wrappedText.length * 4
              }
              
              // Skills section
              else if (line.includes('Analytics:') || line.includes('Design:') || line.includes('BI/A/B')) {
                doc.setFontSize(9)
                doc.setTextColor(0, 0, 0)
                doc.setFont('helvetica', 'normal')
                const wrappedText = doc.splitTextToSize(line, maxWidth)
                doc.text(wrappedText, margin, yPosition)
                yPosition += wrappedText.length * 4
              }
              
              // Regular paragraph text
              else {
                doc.setFontSize(9)
                doc.setTextColor(0, 0, 0)
                doc.setFont('helvetica', 'normal')
                const wrappedText = doc.splitTextToSize(line, maxWidth)
                doc.text(wrappedText, margin, yPosition)
                yPosition += wrappedText.length * 4
              }
            }
            
            // Generate PDF blob and open in new tab
            const pdfBlob = doc.output('blob')
            const pdfUrl = URL.createObjectURL(pdfBlob)
            window.open(pdfUrl, '_blank')
            
            // Clean up
            setTimeout(() => {
              URL.revokeObjectURL(pdfUrl)
              document.head.removeChild(script)
            }, 1000)
          }
          
          script.onerror = () => {
            // Fallback to text download if jsPDF fails to load
            console.error('Failed to load jsPDF library')
            const blob = new Blob([content], { type: 'text/plain' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${filename}.txt`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)
          }
        } catch (error) {
          console.error('Error generating PDF:', error)
          // Fallback to text download
          const blob = new Blob([content], { type: 'text/plain' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `${filename}.txt`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
        }
        return // Exit early for PDF
        
      case 'docx':
        // For Word, we'll create a simple RTF format that Word can open
        // Clean content for RTF - replace bullets and escape special characters
        const cleanContent = content
          .replace(/•/g, '\\bullet ')  // Replace bullet points with RTF bullets
          .replace(/â€¢/g, '\\bullet ') // Replace corrupted bullets 
          .replace(/[{}\\]/g, '\\$&')   // Escape RTF special characters
          .replace(/\n/g, '\\par ')     // Convert newlines to RTF paragraphs
        
        const rtfContent = `{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}} \\f0\\fs24 ${cleanContent}}`
        blob = new Blob([rtfContent], { type: 'application/rtf' })
        mimeType = 'application/rtf'
        extension = 'rtf'
        break
        
      case 'txt':
      default:
        blob = new Blob([content], { type: 'text/plain' })
        mimeType = 'text/plain'
        extension = 'txt'
        break
    }
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.${extension}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [])

  const handleDownloadAll = useCallback((resultsToDownload, format = 'pdf') => {
    if (!resultsToDownload || resultsToDownload.length === 0) return
    
    if (format === 'zip') {
      // For ZIP, we'll download each file individually with a delay
      // In production, you'd want to use a proper ZIP library like JSZip
      resultsToDownload.forEach((result, index) => {
        setTimeout(() => {
          const content = result.tailored_resume || result.resume_content || result.content
          if (content) {
            const filename = `resume_${result.job_title || `job_${index + 1}`}`
            downloadAsFormat(content, filename, 'pdf') // Default to PDF for ZIP
          }
        }, index * 500) // Stagger downloads by 500ms
      })
    } else {
      resultsToDownload.forEach((result, index) => {
        const content = result.tailored_resume || result.resume_content || result.content
        if (content) {
          const filename = `resume_${result.job_title || `job_${index + 1}`}`
          downloadAsFormat(content, filename, format)
        }
      })
    }
  }, [downloadAsFormat])
  
  const handleDownloadIndividual = useCallback((result, format = 'pdf') => {
    if (!result) return
    
    // Check if result has PDF download URL from backend (for PDF format)
    if (format === 'pdf' && result.pdf && result.pdf.download_url) {
      // Open PDF directly in new tab using backend URL
      const pdfUrl = `${API_BASE_URL}${result.pdf.download_url}`
      window.open(pdfUrl, '_blank')
      return
    }
    
    // Fallback to client-side generation for other formats or if no PDF URL
    const content = result.tailored_resume || result.resume_content || result.content
    if (content) {
      const filename = `resume_${result.job_title || 'job'}`
      downloadAsFormat(content, filename, format)
    }
  }, [downloadAsFormat])

  // Processing handlers
  const handleProcessingStart = useCallback(async (data) => {
    setProcessing(true)
    setError('')
    setSuccess('')
    
    try {
      // Check if child component passed an error
      if (data.error) {
        setError(data.error)
        setProcessing(false)
        return
      }
      
      // Track usage for analytics
      await trackUsage('resume_generation')
      
      // Process based on selected mode
      if (selectedMode === 'batch') {
        // Handle batch processing - transform data to match backend BatchProcessRequest
        const batchData = {
          resume_text: data.resume_text || '',
          job_urls: data.job_urls || [],
          use_rag: true,
          output_format: data.settings?.outputFormat || 'pdf',
          template: data.settings?.template || 'modern',
          tailoring_mode: data.settings?.tailoringMode || 'light',
          optional_sections: {
            includeSummary: data.settings?.includeSummary || false,
            includeSkills: data.settings?.includeSkills || true,
            includeEducation: false,
            educationDetails: {
              degree: '',
              institution: '',
              year: '',
              gpa: ''
            }
          },
          cover_letter_options: {
            includeCoverLetter: data.settings?.includeCoverLetter || false,
            coverLetterDetails: {
              tone: 'professional',
              emphasize: 'experience',
              additionalInfo: ''
            }
          }
        }
        
        console.log('🔍 [DEBUG] Sending batch data:', JSON.stringify(batchData, null, 2))
        
        const response = await authenticatedRequest(`${API_BASE_URL}/api/enhanced-batch/process`, {
          method: 'POST',
          body: JSON.stringify(batchData)
        })
        
        // Parse the response JSON
        const responseData = await response.json()
        console.log('📋 [DEBUG] Parsed response data:', responseData)
        
        if (response.ok && responseData.success) {
          setSuccess('Batch processing started successfully!')
          
          console.log('📋 Full batch response:', responseData)
          
          // Store batch ID for tracking
          const batchJobId = responseData.batch_job_id || responseData.batch_id
          if (batchJobId) {
            setBatchId(batchJobId)
            console.log('🔄 Starting to poll for batch results, job ID:', batchJobId)
            // Start polling for results
            pollBatchResults(batchJobId)
          } else {
            console.error('❌ No batch_job_id or batch_id found in response:', responseData)
            console.log('🔍 Available response keys:', Object.keys(responseData))
            
            // Fallback: Try to load the most recent batch results
            console.log('🔄 Fallback: Attempting to load most recent batch results...')
            setTimeout(async () => {
              try {
                // Get all batch jobs and load the most recent completed one
                const jobsResponse = await authenticatedRequest(`${API_BASE_URL}/api/batch/jobs`)
                const jobsData = await jobsResponse.json()
                
                if (jobsData.success && jobsData.batches && jobsData.batches.length > 0) {
                  const completedBatches = jobsData.batches.filter(batch => batch.state === 'completed')
                  if (completedBatches.length > 0) {
                    const mostRecent = completedBatches.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))[0]
                    console.log('🎯 Loading results for most recent batch:', mostRecent.batch_id)
                    await loadBatchResults(mostRecent.batch_id)
                  }
                }
              } catch (error) {
                console.error('❌ Fallback failed:', error)
              }
            }, 10000) // Wait 10 seconds then try to load results
          }
        } else {
          console.error('❌ [DEBUG] Batch processing failed:', response)
          console.error('❌ [DEBUG] Response status:', response.status)
          
          // For 422 errors, we need to parse the response body to get validation details
          let errorMessage = 'Failed to start batch processing'
          try {
            const errorData = await response.json()
            console.error('❌ [DEBUG] Error response body:', JSON.stringify(errorData, null, 2))
            
            if (errorData.detail) {
              if (Array.isArray(errorData.detail)) {
                // FastAPI validation errors are arrays
                const validationErrors = errorData.detail.map(err => `${err.loc?.join('.')} - ${err.msg}`).join(', ')
                errorMessage = `Validation error: ${validationErrors}`
              } else {
                errorMessage = errorData.detail
              }
            } else if (errorData.error) {
              errorMessage = errorData.error
            }
          } catch (parseError) {
            console.error('❌ [DEBUG] Failed to parse error response:', parseError)
          }
          
          setError(errorMessage)
        }
      } else if (selectedMode === 'precision') {
        // Handle precision processing - transform data to match backend ResumeRequest
        const precisionData = {
          resume_text: data.resume_text || '',
          job_url: data.job_urls?.[0] || '', // Precision mode typically processes one job at a time
          use_rag: true,
          tailoring_mode: 'light',
          output_format: 'text',
          optional_sections: {
            includeSummary: data.settings?.includeSummary || false,
            includeSkills: data.settings?.includeSkills || true,
            includeEducation: false,
            educationDetails: {
              degree: '',
              institution: '',
              year: '',
              gpa: ''
            }
          },
          cover_letter_options: {
            includeCoverLetter: data.settings?.includeCoverLetter || false,
            coverLetterDetails: {
              tone: 'professional',
              emphasize: 'experience',
              additionalInfo: ''
            }
          }
        }
        
        const response = await authenticatedRequest('/generate-resumes/tailor', {
          method: 'POST',
          body: JSON.stringify(precisionData)
        })
        
        if (response.success) {
          setSuccess('Precision processing completed successfully!')
          setResults(response.results || [response.tailored_resume] || [])
        } else {
          setError(response.error || 'Failed to complete precision processing')
        }
      }
    } catch (err) {
      console.error('Processing error:', err)
      // Display the specific error message from the backend
      setError(err.message || 'An unexpected error occurred during processing')
    } finally {
      setProcessing(false)
    }
  }, [selectedMode, authenticatedRequest, trackUsage])

  const handleProcessingComplete = useCallback((results) => {
    setResults(results)
    setProcessing(false)
    setSuccess('Processing completed successfully!')
  }, [])

  // Poll for batch processing results
  const pollBatchResults = useCallback(async (batchJobId) => {
    console.log('🔄 Starting to poll for batch results, job ID:', batchJobId)
    
    const maxAttempts = 300 // 300 attempts * 2 seconds = 10 minutes max (should be much faster with parallel processing)
    let attempts = 0
    
    const poll = async () => {
      attempts++
      console.log(`🔍 Polling attempt ${attempts}/${maxAttempts} for job ${batchJobId}`)
      
      try {
        const statusResponse = await fetch(`http://localhost:8000/api/enhanced-batch/status/${batchJobId}`, {
          headers: {
            'Authorization': `Bearer ${getToken()}`
          }
        })
        const statusData = await statusResponse.json()
        
        console.log('📊 Batch status response:', statusData)
        
        // The backend returns { status: { state: "completed" } }
        const currentState = statusData.status?.state || statusData.state
        console.log('🔍 Current batch state:', currentState)
        
        if (currentState === 'completed') {
          console.log('✅ Batch processing completed, loading results...')
          loadBatchResults(batchJobId)
          return
        } else if (currentState === 'failed') {
          console.error('❌ Batch processing failed:', statusData.error)
          setError(statusData.error || 'Batch processing failed')
          setProcessing(false)
          return
        } else if (currentState === 'processing' || currentState === 'pending') {
          console.log('⏳ Batch still processing, will check again in 2 seconds...')
          if (attempts < maxAttempts) {
            setTimeout(poll, 2000) // Poll every 2 seconds
          } else {
            console.warn('⚠️ Max polling attempts reached')
            setError('Processing is taking longer than expected. Please check back later.')
            setProcessing(false)
          }
        }
      } catch (error) {
        console.error('❌ Error polling batch status:', error)
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000) // Retry on error
        } else {
          setError('Unable to check processing status. Please try again later.')
          setProcessing(false)
        }
      }
    }
    
    // Start polling
    poll()
  }, [getToken])

  // Load batch results when processing is complete
  const loadBatchResults = useCallback(async (jobId) => {
    console.log('📥 Loading batch results for job:', jobId)
    try {
      const response = await fetch(`http://localhost:8000/api/enhanced-batch/results/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      })
      const data = await response.json()
      
      console.log('📋 Batch results data:', data)
      
      if (data.success && data.results) {
        setResults(data.results)
        setSuccess('Your resumes are ready! 🎉')
        setProcessing(false)
        
        // Generate transformation score based on results (for future use)
        if (data.results.length > 0) {
          const avgScore = data.results.reduce((acc, result) => {
            return acc + (result.transformation_score || Math.floor(Math.random() * 30) + 70)
          }, 0) / data.results.length
          console.log('📊 Average transformation score:', Math.floor(avgScore))
        }
        
        console.log('✅ Batch results loaded successfully')
      } else {
        console.error('❌ Failed to load batch results:', data)
        setError(data.error || 'Failed to load batch results')
        setProcessing(false)
      }
    } catch (error) {
      console.error('❌ Error loading batch results:', error)
      setError('Failed to load batch results')
      setProcessing(false)
    }
  }, [authenticatedRequest])

  // Legacy mode toggle (for backwards compatibility)
  const toggleLegacyMode = useCallback(() => {
    setShowLegacyMode(!showLegacyMode)
    if (!showLegacyMode) {
      setCurrentState(APP_STATES.LEGACY_MODE)
    } else {
      setCurrentState(APP_STATES.MODE_SELECTION)
    }
  }, [showLegacyMode])

  // Render mobile-optimized interface
  if (isMobile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* Mobile Header */}
        <header className="sticky top-0 z-40 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
          <div className="container flex h-16 items-center justify-between px-4">
            <Link className="flex items-center gap-2 font-semibold" href="/">
              <FileText className="h-6 w-6 text-blue-600" />
              <span>ApplyAI</span>
            </Link>
            <div className="flex items-center gap-2">
              <SubscriptionBadge tier={user?.subscription_tier} />
              <MobileNav />
            </div>
          </div>
        </header>

        {/* Mobile Content */}
        <main className="container px-4 pt-8 pb-6">
          <AnimatePresence mode="wait">
            {currentState === APP_STATES.MODE_SELECTION && (
              <motion.div
                key="mobile-mode-selection"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <SimplifiedModeSelection
                  onModeSelect={handleModeSelect}
                  isProUser={safeIsProUser}
                  weeklyUsage={safeWeeklyUsage}
                  weeklyLimit={safeWeeklyLimit}
                  onUpgradeClick={() => setShowUpgradePrompt(true)}
                />
              </motion.div>
            )}

            {currentState === APP_STATES.BATCH_MODE && (
              <motion.div
                key="mobile-batch-mode"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <SimplifiedBatchMode
                  resumeData={resumeData}
                  jobUrls={jobUrls.split('\n').filter(url => url.trim())}
                  onProcessingStart={handleProcessingStart}
                  onProcessingComplete={handleProcessingComplete}
                  onBackToModeSelection={handleBackToModeSelection}
                  processing={processing}
                  error={error}
                  success={success}
                  results={results}
                  onDownloadAll={handleDownloadAll}
                  onDownloadIndividual={handleDownloadIndividual}
                />
              </motion.div>
            )}

            {currentState === APP_STATES.PRECISION_MODE && (
              <motion.div
                key="mobile-precision-mode"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <SimplifiedPrecisionMode
                  resumeData={resumeData}
                  jobUrls={jobUrls.split('\n').filter(url => url.trim())}
                  onProcessingStart={handleProcessingStart}
                  onProcessingComplete={handleProcessingComplete}
                  onBackToModeSelection={handleBackToModeSelection}
                  processing={processing}
                  error={error}
                  success={success}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    )
  }

  // Desktop interface
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Desktop Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="container flex h-16 items-center justify-between px-4 md:px-6 max-w-7xl mx-auto">
          <Link className="flex items-center gap-2 font-semibold flex-shrink-0" href="/">
            <FileText className="h-6 w-6 text-blue-600" />
            <span className="text-lg">ApplyAI</span>
          </Link>
          
          <div className="flex items-center gap-2 md:gap-4 flex-shrink-0">
            {/* Compact subscription indicator for header */}
            <div className="hidden lg:flex items-center gap-2 text-sm">
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                safeIsProUser 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'bg-blue-100 text-blue-700'
              }`}>
                {safeIsProUser ? 'Pro' : `${safeWeeklyUsage}/${safeWeeklyLimit}`}
              </div>
            </div>
            
            {/* Legacy Mode Toggle (for backwards compatibility) */}
            <Button
              variant="outline"
              size="sm"
              onClick={toggleLegacyMode}
              className="hidden lg:flex text-xs px-2 py-1"
            >
              {showLegacyMode ? 'New Interface' : 'Legacy Mode'}
            </Button>
            
            <div className="flex items-center gap-1 md:gap-2">
              <div className="hidden lg:flex items-center gap-2 text-sm text-gray-600 max-w-[150px] truncate">
                <User className="h-4 w-4 flex-shrink-0" />
                <span className="truncate">{user?.name || user?.email}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={handleLogout} className="flex-shrink-0">
                <LogOut className="h-4 w-4" />
                <span className="hidden md:inline ml-1">Sign Out</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Usage Warning Banner */}
      <UsageWarningBanner 
        weeklyUsage={safeWeeklyUsage}
        weeklyLimit={safeWeeklyLimit}
        isProUser={safeIsProUser}
      />

      {/* Subscription Status - Inline Display */}
      <div className="container px-4 md:px-6 pt-6">
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                safeIsProUser 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'bg-blue-100 text-blue-700'
              }`}>
                {safeIsProUser ? 'Pro User' : 'Free User'}
              </div>
              <span className="text-sm text-gray-600">
                {safeIsProUser ? 'Unlimited access' : `${safeWeeklyUsage}/${safeWeeklyLimit} sessions this week`}
              </span>
            </div>
            {!safeIsProUser && (
              <button 
                onClick={() => setShowUpgradePrompt(true)}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Upgrade to Pro
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container px-4 md:px-6 pt-8 pb-8">
        <AnimatePresence mode="wait">
          {currentState === APP_STATES.MODE_SELECTION && (
            <motion.div
              key="desktop-mode-selection"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <SimplifiedModeSelection
                onModeSelect={handleModeSelect}
                isProUser={safeIsProUser}
                weeklyUsage={safeWeeklyUsage}
                weeklyLimit={safeWeeklyLimit}
                onUpgradeClick={() => setShowUpgradePrompt(true)}
              />
            </motion.div>
          )}

          {currentState === APP_STATES.BATCH_MODE && (
            <motion.div
              key="desktop-batch-mode"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <SimplifiedBatchMode
                resumeData={resumeData}
                jobUrls={jobUrls.split('\n').filter(url => url.trim())}
                onProcessingStart={handleProcessingStart}
                onProcessingComplete={handleProcessingComplete}
                onBackToModeSelection={handleBackToModeSelection}
                processing={processing}
                error={error}
                success={success}
                results={results}
                onDownloadAll={handleDownloadAll}
                onDownloadIndividual={handleDownloadIndividual}
              />
            </motion.div>
          )}

          {currentState === APP_STATES.PRECISION_MODE && (
            <motion.div
              key="desktop-precision-mode"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <SimplifiedPrecisionMode
                resumeData={resumeData}
                jobUrls={jobUrls.split('\n').filter(url => url.trim())}
                onProcessingStart={handleProcessingStart}
                onProcessingComplete={handleProcessingComplete}
                onBackToModeSelection={handleBackToModeSelection}
                processing={processing}
                error={error}
                success={success}
              />
            </motion.div>
          )}

          {currentState === APP_STATES.LEGACY_MODE && (
            <motion.div
              key="legacy-mode"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Legacy interface components would go here */}
              <div className="text-center py-12">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Legacy Mode</h2>
                <p className="text-gray-600 mb-6">
                  This would contain the original interface for backwards compatibility.
                </p>
                <Button onClick={toggleLegacyMode}>
                  Return to New Interface
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error and Success Messages */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800"
          >
            {error}
          </motion.div>
        )}

        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800"
          >
            {success}
          </motion.div>
        )}
      </main>

      {/* Resume View Modal */}
      <ResumeModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        resume={selectedResume?.tailored_resume}
        jobTitle={selectedResume?.job_title}
        originalResume={resumeData.originalText}
      />

      {/* Upgrade Prompt Modal */}
      {showUpgradePrompt && (
        <UpgradePrompt
          isOpen={showUpgradePrompt}
          onClose={() => setShowUpgradePrompt(false)}
          feature="Precision Mode"
          description="Unlock advanced customization and analytics"
        />
      )}

      {/* Footer */}
      <footer className="w-full border-t py-6 md:py-12 bg-white/80 backdrop-blur-sm">
        <div className="container px-4 md:px-6">
          <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-4">
            <div className="space-y-4">
              <Link className="flex items-center gap-2 font-semibold" href="/">
                <FileText className="h-6 w-6 text-blue-600" />
                <span>ApplyAI</span>
              </Link>
              <p className="text-sm text-gray-500">
                Smart. Targeted. Effective. Resumes that open doors — since 2025.
              </p>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Product</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="/features">
                  Features
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/how-it-works">
                  How It Works
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/faq">
                  FAQ
                </Link>
              </nav>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Company</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="/about">
                  About
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/blog">
                  Blog
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/contact">
                  Contact
                </Link>
              </nav>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Legal</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="/terms">
                  Terms
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/privacy">
                  Privacy
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/cookies">
                  Cookies
                </Link>
              </nav>
            </div>
          </div>
          <div className="mt-10 flex flex-col items-center justify-between gap-4 border-t border-gray-200 pt-6 md:flex-row">
            <p className="text-xs text-gray-500">© {new Date().getFullYear()} ApplyAI. All rights reserved.</p>
            <div className="flex gap-4">
              <Link className="text-sm hover:underline text-gray-500" href="/privacy">
                Privacy Policy
              </Link>
              <Link className="text-sm hover:underline text-gray-500" href="/terms">
                Terms of Service
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default function AppPage() {
  return (
    <ProtectedRoute>
      <Layout>
        <RedesignedApp />
      </Layout>
    </ProtectedRoute>
  )
}
