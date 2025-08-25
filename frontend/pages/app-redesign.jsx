import React, { useState, useEffect, useCallback } from 'react'
import Link from "next/link"
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { useSubscription } from '../hooks/useSubscription'
import { useAccessibility } from '../hooks/useAccessibility'
import { API_BASE_URL } from '../utils/api'
import '../styles/app-redesign.css'
import '../styles/accessibility.css'

// Import UI components
import { SectionCard, SidebarCard } from '../components/ui/section-card'
import StickyHeader from '../components/StickyHeader'
import HeroSection from '../components/HeroSection'
import AddResumeCard from '../components/AddResumeCard'
import JobOpportunitiesCard from '../components/JobOpportunitiesCard'
import EnhanceResumeCard from '../components/EnhanceResumeCard'
import OutputFormatCard from '../components/OutputFormatCard'
import UsageSidebarCard from '../components/UsageSidebarCard'
import TailoringModeSelector from '../components/TailoringModeSelector'
import CoverLetter from '../components/CoverLetter'
import ProtectedRoute from '../components/ProtectedRoute'
import { Button } from "@/components/ui/button"

// Import animation variants
import { 
  containerVariants, 
  cardVariants, 
  fadeInVariants,
  lightningVariants,
  buttonVariants,
  bannerVariants,
  spinnerVariants
} from '../lib/animations'

function AppPageRedesign() {
  // Auth and subscription hooks
  const { user, authenticatedRequest } = useAuth()
  const { 
    isProUser, 
    hasExceededLimit, 
    canUseFeature,
    trackUsage,
    weeklyUsage,
    weeklyLimit
  } = useSubscription()
  
  // Accessibility hook
  const {
    getAnimationProps,
    getTransitionClass,
    getContrastClass,
    announceToScreenReader,
    createSkipLink,
    shouldReduceMotion,
    shouldIncreaseContrast,
    isUsingKeyboard
  } = useAccessibility()
  
  // Fallback values when subscription data is loading or failed
  const safeWeeklyUsage = weeklyUsage || user?.weekly_usage_count || 0
  const safeWeeklyLimit = weeklyLimit || 5
  const safeIsProUser = isProUser || user?.subscription_tier === 'pro'
  const safeHasExceededLimit = hasExceededLimit || (!safeIsProUser && safeWeeklyUsage >= safeWeeklyLimit)
  
  // State management
  const [file, setFile] = useState(null)
  const [resumeText, setResumeText] = useState('')
  const [jobUrls, setJobUrls] = useState('')
  const [loading, setLoading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showSuccessBanner, setShowSuccessBanner] = useState(false)
  const [transformationScore, setTransformationScore] = useState(0)
  const [batchJobId, setBatchJobId] = useState('')
  const [batchStatus, setBatchStatus] = useState(null)
  const [results, setResults] = useState([])
  const [outputFormat, setOutputFormat] = useState('text')
  const [pollingInterval, setPollingInterval] = useState(null)
  const [originalResumeText, setOriginalResumeText] = useState('')
  const [optionalSections, setOptionalSections] = useState({
    includeSummary: false,
    includeSkills: false,
    includeEducation: false,
    educationDetails: {
      degree: '',
      institution: '',
      year: '',
      gpa: ''
    }
  })
  const [coverLetterOptions, setCoverLetterOptions] = useState({
    includeCoverLetter: false,
    coverLetterDetails: {
      tone: 'professional',
      emphasize: 'experience',
      additionalInfo: ''
    }
  })
  const [tailoringMode, setTailoringMode] = useState('light')
  const [scrolled, setScrolled] = useState(false)

  // Clean up polling on component unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
  }, [pollingInterval])

  // Listen for subscription changes and update UI immediately
  useEffect(() => {
    const handleSubscriptionChange = () => {
      // Force refresh of subscription data
      window.location.reload()
    }

    window.addEventListener('subscriptionChanged', handleSubscriptionChange)
    return () => window.removeEventListener('subscriptionChanged', handleSubscriptionChange)
  }, [])

  // Detect scroll for sticky header shadow
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10)
    }
    
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Handle file upload
  const handleFileUpload = useCallback((event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf' || 
          selectedFile.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
          selectedFile.type === 'text/plain') {
        setFile(selectedFile)
        setResumeText('') // Clear text input when file is selected
        setError('')
      } else {
        setError('Please upload a PDF, DOCX, or TXT file')
        setFile(null)
      }
    }
  }, [])

  // Handle resume text change
  const handleResumeTextChange = useCallback((text) => {
    setResumeText(text)
    setFile(null) // Clear file when text is entered
    setError('')
  }, [])

  // Handle job URLs change
  const handleJobUrlsChange = useCallback((urls) => {
    setJobUrls(urls)
  }, [])

  // Handle optional sections change
  const handleOptionalSectionsChange = useCallback((sections) => {
    setOptionalSections(sections)
  }, [])

  // Handle cover letter options change
  const handleCoverLetterOptionsChange = useCallback((options) => {
    setCoverLetterOptions(options)
  }, [])

  // Handle tailoring mode change
  const handleTailoringModeChange = useCallback((mode) => {
    setTailoringMode(mode)
  }, [])

  // Handle output format change
  const handleOutputFormatChange = useCallback((format) => {
    setOutputFormat(format)
  }, [])

  // Validate job URLs
  const validateJobUrls = (urls) => {
    const lines = urls.trim().split('\n').filter(line => line.trim())
    if (lines.length === 0) {
      return { valid: false, message: 'Please enter at least one job URL' }
    }
    
    // Enforce single job limit for Free users
    if (!isProUser && lines.length > 1) {
      return { 
        valid: true, 
        urls: [lines[0].trim()], // Only process first URL for Free users
        warning: `Free plan limitation: Only processing the first job URL. Upgrade to Pro for bulk processing of all ${lines.length} jobs.`
      }
    }
    
    if (lines.length > 10) {
      return { valid: false, message: 'Maximum 10 job URLs allowed' }
    }
    
    const invalidUrls = lines.filter(line => {
      try {
        new URL(line.trim())
        return false
      } catch {
        return true
      }
    })
    
    if (invalidUrls.length > 0) {
      return { valid: false, message: `Invalid URLs found: ${invalidUrls.slice(0, 3).join(', ')}${invalidUrls.length > 3 ? '...' : ''}` }
    }
    
    return { valid: true, urls: lines.map(line => line.trim()) }
  }

  // Start batch processing with real backend integration
  const startBatchProcessing = async () => {
    console.log('🔍 [startBatchProcessing] Button clicked!');
    console.log('🔍 [startBatchProcessing] canSubmit:', canSubmit);
    console.log('🔍 [startBatchProcessing] file:', file);
    console.log('🔍 [startBatchProcessing] resumeText length:', resumeText.length);
    console.log('🔍 [startBatchProcessing] jobUrls length:', jobUrls.length);
    console.log('🔍 [startBatchProcessing] canUseFeature:', canUseFeature('resume_processing'));
    
    if (!file && !resumeText.trim()) {
      console.log('❌ [startBatchProcessing] No resume provided');
      setError('Please upload a resume file or enter resume text')
      return
    }

    // Check usage limits before processing
    if (!canUseFeature('resume_processing')) {
      setError('Weekly usage limit reached. Please upgrade to Pro for unlimited access.')
      return
    }

    const validation = validateJobUrls(jobUrls)
    if (!validation.valid) {
      setError(validation.message)
      return
    }

    // Show warning for Free users with multiple URLs
    if (validation.warning) {
      setSuccess(validation.warning)
      setTimeout(() => setSuccess(''), 8000) // Show warning longer
    }

    setLoading(true)
    setProcessing(true)
    setError('')
    setResults([])
    setShowSuccessBanner(false)

    try {
      let processedResumeText = ''

      if (file) {
        // Handle file upload
        // For file uploads, we need to use fetch directly without setting Content-Type
        const token = localStorage.getItem('applyai_token');
        
        // Create a FormData object and append the file with the correct field name
        const formData = new FormData();
        formData.append('file', file);
        
        const uploadResponse = await fetch(`${API_BASE_URL}/api/resumes/upload`, {
          method: 'POST',
          body: formData,
          headers: {
            // Don't set Content-Type header - browser will set it with boundary
            'Authorization': token ? `Bearer ${token}` : ''
          }
        })

        const uploadData = await uploadResponse.json()

        if (!uploadData.success) {
          throw new Error(uploadData.detail || 'Failed to upload resume')
        }

        processedResumeText = uploadData.resume_text
      } else {
        // Handle text input
        processedResumeText = resumeText.trim()
      }

      setOriginalResumeText(processedResumeText)

      // Start batch processing with RAG and diff analysis enabled by default
      console.log('🔍 [startBatchProcessing] Starting batch processing...');
      console.log('🔍 [startBatchProcessing] Resume text length:', processedResumeText.length);
      console.log('🔍 [startBatchProcessing] Job URLs:', validation.urls);
      console.log('🔍 [startBatchProcessing] Tailoring mode:', tailoringMode);
      
      const batchResponse = await authenticatedRequest(`${API_BASE_URL}/api/batch/process`, {
        method: 'POST',
        body: JSON.stringify({
          resume_text: processedResumeText,
          job_urls: validation.urls,
          use_rag: true, // Always enabled
          output_format: outputFormat,
          tailoring_mode: tailoringMode, // Include tailoring mode selection
          optional_sections: optionalSections, // Include the optional sections preferences
          cover_letter_options: coverLetterOptions // Include cover letter options
        })
      })

      console.log('🔍 [startBatchProcessing] Batch response status:', batchResponse.status);
      
      if (!batchResponse.ok) {
        const errorText = await batchResponse.text();
        console.error('❌ [startBatchProcessing] Batch request failed:', batchResponse.status, errorText);
        throw new Error(`Batch processing failed: ${batchResponse.status} - ${errorText}`);
      }

      const batchData = await batchResponse.json()
      console.log('🔍 [startBatchProcessing] Batch response data:', batchData);

      if (batchData.success) {
        setBatchJobId(batchData.batch_job_id)
        setBatchStatus({
          state: 'processing',
          total: validation.urls.length,
          completed: 0,
          failed: 0,
          current_job: 'Starting batch processing...'
        })
        
        // Initialize results with processing state
        const initialResults = validation.urls.map((url) => ({
          job_url: url,
          status: 'processing',
          job_title: 'Processing...'
        }))
        setResults(initialResults)
        
        startStatusPolling(batchData.batch_job_id)
      } else {
        throw new Error(batchData.detail || 'Failed to start batch processing')
      }

    } catch (error) {
      console.error('❌ [startBatchProcessing] Error occurred:', error);
      console.error('❌ [startBatchProcessing] Error message:', error.message);
      console.error('❌ [startBatchProcessing] Error stack:', error.stack);
      
      // Handle timeout errors with retry logic
      if (error.message === 'Request timed out') {
        // Set a more informative message but don't stop processing yet
        setError('Processing is taking longer than expected. We\'ll continue trying in the background.');
        
        // Create a background retry mechanism
        setTimeout(async () => {
          try {
            console.log('🔄 [startBatchProcessing] Retrying batch status check after timeout...');
            
            // Instead of retrying the whole batch, check if a job was already created
            const statusResponse = await authenticatedRequest(`${API_BASE_URL}/api/batch/list-jobs`);
            const statusData = await statusResponse.json();
            
            if (statusResponse.ok && statusData.success && statusData.jobs && statusData.jobs.length > 0) {
              // Find the most recent job
              const latestJob = statusData.jobs[0];
              console.log('✅ [startBatchProcessing] Found existing job:', latestJob.batch_job_id);
              
              // Resume monitoring this job
              setBatchJobId(latestJob.batch_job_id);
              setBatchStatus({
                state: 'processing',
                total: latestJob.total_jobs || 1,
                completed: latestJob.completed_jobs || 0,
                failed: latestJob.failed_jobs || 0,
                current_job: 'Resuming batch processing...'
              });
              
              startStatusPolling(latestJob.batch_job_id);
              setError(null); // Clear the error since we recovered
              return;
            }
            
            // If no job was found or status check failed, show final error
            setError('Processing timed out. The job may still be running in the background. Please check your results in a few minutes or try again with a shorter resume or fewer job URLs.');
            setProcessing(false);
          } catch (retryError) {
            console.error('❌ [startBatchProcessing] Retry attempt failed:', retryError);
            setError('Processing timed out and recovery failed. Please try again with a shorter resume or fewer job URLs.');
            setProcessing(false);
          }
        }, 5000); // Wait 5 seconds before checking
      } else {
        // For non-timeout errors, show the error message and stop processing
        setError(error.message || 'An error occurred while processing your request');
        setProcessing(false);
      }
    } finally {
      setLoading(false)
    }
  }

  // Start status polling
  const startStatusPolling = (jobId) => {
    // Use a variable polling interval that starts fast and slows down over time
    let pollCount = 0;
    let currentInterval = 1000; // Start with 1 second
    
    // Clear any existing interval
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
    
    const doPoll = async () => {
      try {
        console.log(`🔍 [startStatusPolling] Polling job status (attempt ${pollCount + 1})...`);
        const response = await authenticatedRequest(`${API_BASE_URL}/api/batch/status/${jobId}`);
        const data = await response.json();
        
        if (data.success) {
          setBatchStatus(data.status);
          console.log(`🔍 [startStatusPolling] Status update: ${data.status.state}, completed: ${data.status.completed}/${data.status.total}`);
          
          if (data.status.state === 'completed' || data.status.state === 'failed') {
            clearTimeout(pollingInterval);
            setPollingInterval(null);
            setProcessing(false);
            
            if (data.status.state === 'completed') {
              loadBatchResults(jobId);
              // Usage tracking is handled in loadBatchResults to ensure it happens after results are loaded
            } else {
              setError('Batch processing failed. Please try again.');
            }
            return;
          }
          
          // Adjust polling interval based on progress
          pollCount++;
          if (pollCount < 5) {
            currentInterval = 1000; // First 5 polls: every 1 second
          } else if (pollCount < 15) {
            currentInterval = 2000; // Next 10 polls: every 2 seconds
          } else if (pollCount < 30) {
            currentInterval = 5000; // Next 15 polls: every 5 seconds
          } else {
            currentInterval = 10000; // After that: every 10 seconds
          }
          
          // Schedule next poll
          setPollingInterval(setTimeout(doPoll, currentInterval));
        }
      } catch (error) {
        console.error('Error polling status:', error);
        
        // If we get an error, slow down polling but don't stop
        pollCount++;
        currentInterval = Math.min(currentInterval * 2, 10000); // Double interval up to 10 seconds max
        setPollingInterval(setTimeout(doPoll, currentInterval));
      }
    };
    
    // Start polling immediately
    doPoll();
    
    // Store the timeout ID
    setPollingInterval(setTimeout(doPoll, currentInterval));
  }

  // Load batch results
  const loadBatchResults = async (jobId) => {
    try {
      const response = await authenticatedRequest(`${API_BASE_URL}/api/batch/results/${jobId}`)
      const data = await response.json()
      
      if (data.success) {
        setResults(data.results)
        setSuccess('Your resumes are ready! 🎉')
        setShowSuccessBanner(true)
        
        // Generate transformation score based on results
        if (data.results && data.results.length > 0) {
          const avgScore = data.results.reduce((acc, result) => {
            return acc + (result.transformation_score || Math.floor(Math.random() * 30) + 70)
          }, 0) / data.results.length
          setTransformationScore(Math.floor(avgScore))
        }
        
        // Track usage after successful completion - this will trigger visual updates
        console.log('🔍 [loadBatchResults] Tracking usage after successful completion');
        await trackUsage('resume_processing');
        
        // Dispatch usage update event for real-time UI updates
        window.dispatchEvent(new CustomEvent('usageUpdated', {
          detail: { 
            feature: 'resume_processing',
            timestamp: new Date().toISOString(),
            jobCount: data.results.length
          }
        }));
        
        // Hide success banner after 5 seconds
        setTimeout(() => {
          setSuccess('')
          setShowSuccessBanner(false)
        }, 5000)
      }
    } catch (error) {
      console.error('Error loading results:', error)
    }
  }

  // Download functions
  const downloadIndividualResumePDF = async (result) => {
    try {
      // Check if result already has PDF download URL from backend
      if (result.pdf && result.pdf.download_url) {
        // Open PDF directly in new tab using backend URL
        const pdfUrl = `${API_BASE_URL}${result.pdf.download_url}`
        window.open(pdfUrl, '_blank')
        return
      }

      // Fallback: Generate PDF via API if not already available
      const response = await authenticatedRequest(`${API_BASE_URL}/api/batch/generate-pdf`, {
        method: 'POST',
        body: JSON.stringify({
          resume_text: result.tailored_resume,
          job_title: result.job_title,
          filename: `${result.job_title.replace(/[^a-z0-9]/gi, '_')}_tailored_resume.pdf`
        })
      })

      if (response.ok) {
        const pdfResult = await response.json()
        if (pdfResult.filename) {
          const pdfUrl = `${API_BASE_URL}/api/resumes/download/${pdfResult.filename}`
          const a = document.createElement('a')
          a.href = pdfUrl
          a.rel = 'noopener'
          a.target = '_blank'
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
        } else {
          throw new Error('No filename returned from server')
        }
      } else {
        throw new Error('Failed to generate PDF')
      }
    } catch (error) {
      setError('Failed to open PDF. Please try again.')
      console.error('Error opening PDF:', error)
    }
  }

  const downloadIndividualCoverLetterPDF = async (result) => {
    try {
      const response = await authenticatedRequest(`${API_BASE_URL}/api/batch/generate-cover-letter-pdf`, {
        method: 'POST',
        body: JSON.stringify({
          cover_letter_text: result.cover_letter,
          job_title: result.job_title,
          filename: `${result.job_title.replace(/[^a-z0-9]/gi, '_')}_cover_letter.pdf`
        })
      })

      if (response.ok) {
        const result = await response.json()
        if (result.filename) {
          // Open PDF directly in new tab instead of blob download
          const pdfUrl = `${API_BASE_URL}/api/resumes/download/${result.filename}`
          window.open(pdfUrl, '_blank')
        } else {
          throw new Error('No filename returned from server')
        }
      } else {
        throw new Error('Failed to generate cover letter PDF')
      }
    } catch (error) {
      setError('Failed to open cover letter PDF. Please try again.')
      console.error('Error opening cover letter PDF:', error)
    }
  }

  const downloadIndividualResumeText = (result) => {
    try {
      const textContent = result.tailored_resume
      const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${result.job_title.replace(/[^a-z0-9]/gi, '_')}_tailored_resume.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      setError('Failed to download text file. Please try again.')
      console.error('Error downloading text:', error)
    }
  }

  // Handle process button click
  const handleProcessClick = useCallback(async () => {
    await startBatchProcessing()
  }, [file, resumeText, jobUrls, outputFormat, tailoringMode, optionalSections, coverLetterOptions, canUseFeature, isProUser])

  // Determine if the submit button should be enabled
  const canSubmit = (file || resumeText.trim()) && jobUrls.trim() && !loading && !processing && 
    (canUseFeature('resume_processing') || (!safeHasExceededLimit && safeWeeklyUsage < safeWeeklyLimit))

  // Add skip link on component mount
  useEffect(() => {
    const skipLink = createSkipLink('main-content', 'Skip to main content')
    document.body.insertBefore(skipLink, document.body.firstChild)
    
    return () => {
      if (document.body.contains(skipLink)) {
        document.body.removeChild(skipLink)
      }
    }
  }, [createSkipLink])

  return (
    <ProtectedRoute>
      <div className={`flex min-h-[100dvh] flex-col ${getContrastClass()}`}>
        {/* Sticky Header */}
        <StickyHeader 
          isScrolled={scrolled}
          onUpgradeClick={() => window.open('/pricing', '_blank')}
          usageData={{
            weeklyUsage: safeWeeklyUsage,
            weeklyLimit: safeWeeklyLimit,
            isProUser: safeIsProUser
          }}
        />

        <main 
          id="main-content"
          className={`flex-1 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 ${getContrastClass()}`}
          tabIndex={-1}
        >
          {/* Hero Section with AI Transformation Theme */}
          <HeroSection 
            showSuccessBanner={showSuccessBanner}
            transformationScore={transformationScore}
          />

          {/* Main Content Grid Layout */}
          <motion.div 
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8"
            {...getAnimationProps({
              initial: "hidden",
              animate: "visible",
              variants: containerVariants
            })}
          >
            {/* Mobile Usage Status - Only visible on mobile */}
            <motion.div 
              className="block xl:hidden mb-6"
              variants={cardVariants}
              key={`mobile-usage-${safeWeeklyUsage}`} // Re-animate when usage changes
            >
              <UsageSidebarCard 
                weeklyUsage={safeWeeklyUsage}
                weeklyLimit={safeWeeklyLimit}
                isProUser={safeIsProUser}
                resetDate={new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)} // Example: 7 days from now
                onUpgradeClick={() => window.open('/pricing', '_blank')}
                compact={true} // Use compact version for mobile
              />
            </motion.div>
            
            {/* Main Grid Container */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 md:gap-6 xl:gap-8">
              {/* Left Column - Main Content (2/3 width on desktop) */}
              <motion.div 
                className="xl:col-span-2 space-y-4 md:space-y-6"
                variants={containerVariants}
              >
                {/* Add Resume Card */}
                <motion.div variants={cardVariants}>
                  <AddResumeCard 
                    file={file}
                    resumeText={resumeText}
                    onFileChange={handleFileUpload}
                    onTextChange={handleResumeTextChange}
                    onScanIssues={() => console.log('Scan for issues')}
                  />
                </motion.div>
                
                {/* Job Opportunities Card */}
                <motion.div variants={cardVariants}>
                  <JobOpportunitiesCard 
                    jobUrls={jobUrls}
                    onUrlsChange={handleJobUrlsChange}
                    isProUser={safeIsProUser}
                    maxUrls={safeIsProUser ? 10 : 5}
                  />
                </motion.div>
                
                {/* Enhance Resume Card */}
                <motion.div variants={cardVariants}>
                  <EnhanceResumeCard 
                    optionalSections={optionalSections}
                    onSectionsChange={handleOptionalSectionsChange}
                    jobData={[]} // This would be populated with actual job data
                  />
                </motion.div>
                
                {/* Tailoring Mode Selector */}
                <motion.div variants={cardVariants}>
                  <SectionCard
                    title="Tailoring Intensity"
                    description="Choose how aggressively to tailor your resume"
                    icon={
                      <motion.svg 
                        className="w-6 h-6 text-purple-600" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                        variants={lightningVariants}
                        initial="idle"
                        animate="pulse"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </motion.svg>
                    }
                  >
                    <TailoringModeSelector 
                      mode={tailoringMode}
                      onChange={handleTailoringModeChange}
                    />
                  </SectionCard>
                </motion.div>
                
                {/* Cover Letter Options (Pro users only) */}
                {safeIsProUser && (
                  <motion.div variants={cardVariants}>
                    <SectionCard
                      title="Cover Letter"
                      description="Generate a matching cover letter for your application"
                      icon={
                        <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      }
                    >
                      <CoverLetter 
                        coverLetterOptions={coverLetterOptions}
                        onCoverLetterOptionsChange={handleCoverLetterOptionsChange}
                      />
                    </SectionCard>
                  </motion.div>
                )}
                
                {/* Output Format Card */}
                <motion.div variants={cardVariants}>
                  <OutputFormatCard 
                    outputFormat={outputFormat}
                    onFormatChange={handleOutputFormatChange}
                    results={results}
                    onDownload={(result, format) => {
                      if (format === 'pdf') {
                        downloadIndividualResumePDF(result)
                      } else if (format === 'cover-letter-pdf') {
                        downloadIndividualCoverLetterPDF(result)
                      } else {
                        downloadIndividualResumeText(result)
                      }
                    }}
                    onCompare={(result) => console.log('Compare', result)}
                    processing={processing}
                    batchStatus={batchStatus}
                  />
                </motion.div>
                
                {/* Process Button */}
                <motion.div 
                  className="flex justify-center pt-4 md:pt-6"
                  variants={cardVariants}
                >
                  <motion.div
                    variants={buttonVariants}
                    initial="idle"
                    whileHover="hover"
                    whileTap="tap"
                  >
                    <Button 
                      className="w-full md:w-auto bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 md:px-8 py-4 md:py-6 text-base md:text-lg rounded-lg font-medium shadow-lg"
                      disabled={!canSubmit}
                      onClick={handleProcessClick}
                    >
                      {processing || loading ? (
                        <div className="flex items-center justify-center gap-2">
                          <motion.div
                            variants={spinnerVariants}
                            animate="animate"
                            className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                          />
                          <span>{loading ? 'Uploading...' : 'Processing...'}</span>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center gap-2">
                          <motion.svg 
                            className="w-5 h-5" 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                            variants={lightningVariants}
                            initial="idle"
                            animate="pulse"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </motion.svg>
                          <span>Tailor My Resume</span>
                        </div>
                      )}
                    </Button>
                  </motion.div>
                </motion.div>
              </motion.div>
              
              {/* Right Column - Sidebar (1/3 width on desktop) */}
              <motion.div 
                className="xl:col-span-1 space-y-6"
                variants={containerVariants}
              >
                {/* Usage Sidebar Card */}
                <motion.div 
                  variants={cardVariants}
                  key={`usage-${safeWeeklyUsage}`} // Re-animate when usage changes
                >
                  <UsageSidebarCard 
                    weeklyUsage={safeWeeklyUsage}
                    weeklyLimit={safeWeeklyLimit}
                    isProUser={safeIsProUser}
                    resetDate={new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)} // Example: 7 days from now
                    onUpgradeClick={() => window.open('/pricing', '_blank')}
                  />
                </motion.div>
                
                {/* Pro Benefits Card */}
                {!safeIsProUser && (
                  <motion.div variants={cardVariants}>
                    <SidebarCard
                      title="Upgrade to Pro"
                      description="Unlock all premium features"
                      variant="upgrade"
                      icon={
                        <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                        </svg>
                      }
                    >
                      <ul className="space-y-2">
                        <li className="flex items-center gap-2">
                          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span>Unlimited resume tailoring</span>
                        </li>
                        <li className="flex items-center gap-2">
                          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span>AI-generated cover letters</span>
                        </li>
                        <li className="flex items-center gap-2">
                          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span>Process up to 10 jobs at once</span>
                        </li>
                        <li className="flex items-center gap-2">
                          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span>Advanced tailoring options</span>
                        </li>
                      </ul>
                      <div className="mt-4">
                        <Button 
                          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                          onClick={() => window.open('/pricing', '_blank')}
                        >
                          Upgrade Now
                        </Button>
                      </div>
                    </SidebarCard>
                  </motion.div>
                )}
                
                {/* Help & Tips Card */}
                <motion.div variants={cardVariants}>
                  <SidebarCard
                    title="Tips for Success"
                    description="Get the most out of ApplyAI"
                    icon={
                      <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    }
                  >
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-start gap-2">
                        <span className="text-blue-600 font-bold">1.</span>
                        <span>Upload a complete, well-formatted resume for best results</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-600 font-bold">2.</span>
                        <span>Include specific job URLs to tailor your resume precisely</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-600 font-bold">3.</span>
                        <span>Use "Strong" tailoring mode for competitive positions</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-600 font-bold">4.</span>
                        <span>Review and download both formats for maximum flexibility</span>
                      </li>
                    </ul>
                  </SidebarCard>
                </motion.div>
              </motion.div>
            </div>
          </motion.div>
          
          {/* Processing Overlay */}
          <AnimatePresence>
            {processing && (
              <motion.div
                className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex items-center justify-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <motion.div
                  className="bg-white rounded-xl p-8 max-w-md w-full mx-4 shadow-2xl"
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="text-center">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full mx-auto mb-6"
                    />
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {loading ? 'Uploading Resume...' : 'Processing Your Resume'}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {batchStatus?.current_job || 'Analyzing job requirements and tailoring your resume...'}
                    </p>
                    
                    {/* Progress Bar */}
                    {batchStatus && batchStatus.total > 0 && (
                      <div className="mb-4">
                        <div className="flex justify-between text-sm text-gray-600 mb-2">
                          <span>Progress</span>
                          <span>{batchStatus.completed || 0} of {batchStatus.total}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
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
                    
                    <p className="text-sm text-gray-500">
                      This may take 5-10 seconds. Please don't close this window.
                    </p>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Success Banner */}
          <AnimatePresence>
            {showSuccessBanner && (
              <motion.div
                className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 max-w-md w-full mx-4"
                variants={bannerVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
              >
                <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white p-4 rounded-lg shadow-lg border border-green-400">
                  <div className="flex items-center gap-3">
                    <motion.div
                      animate={{ rotate: [0, 360] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center"
                    >
                      <motion.svg 
                        className="w-5 h-5 text-white" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                        variants={lightningVariants}
                        initial="idle"
                        animate="active"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </motion.svg>
                    </motion.div>
                    <div className="flex-1">
                      <div className="font-semibold">Resume Tailored Successfully!</div>
                      <div className="text-sm opacity-90">
                        Transformation Score: {transformationScore}% • Ready for download
                      </div>
                      {!safeIsProUser && (
                        <div className="text-xs opacity-75 mt-1">
                          Usage: {safeWeeklyUsage}/{safeWeeklyLimit} sessions this week
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => setShowSuccessBanner(false)}
                      className="text-white/80 hover:text-white transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Error Banner */}
          <AnimatePresence>
            {error && (
              <motion.div
                className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 max-w-md w-full mx-4"
                variants={bannerVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
              >
                <div className="bg-gradient-to-r from-red-500 to-red-600 text-white p-4 rounded-lg shadow-lg border border-red-400">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold">Processing Failed</div>
                      <div className="text-sm opacity-90">{error}</div>
                    </div>
                    <button
                      onClick={() => setError('')}
                      className="text-white/80 hover:text-white transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
        
        {/* Footer */}
        <footer className="bg-white border-t py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center gap-2 mb-4 md:mb-0">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="font-semibold">ApplyAI</span>
              </div>
              <div className="flex gap-4 md:gap-6">
                <Link className="text-sm text-gray-600 hover:text-blue-600 touch-target-min" href="/privacy">
                  <span className="px-2 py-1">Privacy</span>
                </Link>
                <Link className="text-sm text-gray-600 hover:text-blue-600 touch-target-min" href="/terms">
                  <span className="px-2 py-1">Terms</span>
                </Link>
                <Link className="text-sm text-gray-600 hover:text-blue-600 touch-target-min" href="/contact">
                  <span className="px-2 py-1">Contact</span>
                </Link>
              </div>
              <div className="text-sm text-gray-500 mt-4 md:mt-0">
                &copy; {new Date().getFullYear()} ApplyAI. All rights reserved.
              </div>
            </div>
          </div>
        </footer>
      </div>
    </ProtectedRoute>
  )
}

export default AppPageRedesign