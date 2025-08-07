import React, { useState, useEffect, useCallback } from 'react'
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileText, Menu, X, User, LogOut, Settings, Star } from "lucide-react"
import { motion } from 'framer-motion'
import ResultCard from '../components/ResultCard'
import ResumeModal from '../components/ResumeModal'
import ProtectedRoute from '../components/ProtectedRoute'
import SubscriptionStatus from '../components/SubscriptionStatus'
import SubscriptionBadge from '../components/SubscriptionBadge'
import UpgradePrompt from '../components/UpgradePrompt'
import MobileSubscriptionStatus from '../components/MobileSubscriptionStatus'
import TailoringModeSelector from '../components/TailoringModeSelector'
import UsageLimitGuard, { UsageWarningBanner } from '../components/UsageLimitGuard'

// New redesigned components
import HeroSection from '../components/HeroSection'
import StickyHeader from '../components/StickyHeader'
import AddResumeCard from '../components/AddResumeCard'
import JobOpportunitiesCard from '../components/JobOpportunitiesCard'
import EnhanceResumeCard from '../components/EnhanceResumeCard'
import OutputFormatCard from '../components/OutputFormatCard'
import UsageSidebarCard from '../components/UsageSidebarCard'

import { API_BASE_URL } from '../utils/api'
import { useAuth } from '../contexts/AuthContext'
import { useSubscription } from '../hooks/useSubscription'
import Layout from '../components/Layout'

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
                    <p className="font-medium text-gray-900">{user?.full_name || user?.email}</p>
                    <p className="text-sm text-gray-600 capitalize">{user?.role || 'free'} plan</p>
                  </div>
                </div>
                <div className="border-t pt-4">
                  <Link className="text-lg font-medium hover:underline flex items-center gap-2" href="/dashboard" onClick={() => setIsOpen(false)}>
                    <Settings className="h-4 w-4" />
                    Dashboard
                  </Link>
                  <Link className="text-lg font-medium hover:underline flex items-center gap-2" href="/pricing" onClick={() => setIsOpen(false)}>
                    <Star className="h-4 w-4" />
                    Upgrade
                  </Link>
                  <button 
                    onClick={handleLogout}
                    className="text-lg font-medium hover:underline flex items-center gap-2 text-red-600"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </button>
                </div>
              </>
            )}
            <Link className="text-lg font-medium hover:underline" href="/features" onClick={() => setIsOpen(false)}>
              Features
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/how-it-works" onClick={() => setIsOpen(false)}>
              How It Works
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/faq" onClick={() => setIsOpen(false)}>
              FAQ
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/about" onClick={() => setIsOpen(false)}>
              About
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/blog" onClick={() => setIsOpen(false)}>
              Blog
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/contact" onClick={() => setIsOpen(false)}>
              Contact
            </Link>
            {/* Only show Back to Home for non-authenticated users */}
            {!isAuthenticated && (
              <div className="flex flex-col gap-2 mt-4">
                <Link href="/" onClick={() => setIsOpen(false)}>
                  <Button variant="outline" className="w-full bg-transparent">
                    Back to Home
                  </Button>
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </div>
  )
}

function Home() {
  const [file, setFile] = useState(null)
  const { user, authenticatedRequest, logout, isAuthenticated } = useAuth()
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
  
  const handleLogout = async () => {
    await logout()
    // Redirect to home page after logout
    window.location.href = '/'
  }
  const [resumeText, setResumeText] = useState('')
  const [jobUrls, setJobUrls] = useState('')
  const [loading, setLoading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [batchJobId, setBatchJobId] = useState('')
  const [batchStatus, setBatchStatus] = useState(null)
  const [results, setResults] = useState([])
  const [outputFormat, setOutputFormat] = useState('text')
  const [pollingInterval, setPollingInterval] = useState(null)
  const [selectedResume, setSelectedResume] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
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

  const handleResumeTextChange = useCallback((text) => {
    setResumeText(text)
    setFile(null) // Clear file when text is entered
    setError('')
  }, [])

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
          compare_versions: true, // Always enabled
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
              // Track usage after successful completion
              trackUsage('resume_processing');
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

  const loadBatchResults = async (jobId) => {
    try {
      const response = await authenticatedRequest(`${API_BASE_URL}/api/batch/results/${jobId}`)
      const data = await response.json()
      
      if (data.success) {
        setResults(data.results)
        setSuccess('Your resumes are ready! 🎉')
        setTimeout(() => setSuccess(''), 5000)
      }
    } catch (error) {
      console.error('Error loading results:', error)
    }
  }

  const viewFullResume = (result) => {
    setSelectedResume(result)
    setModalOpen(true)
  }

  const downloadIndividualResumePDF = async (result) => {
    try {
      const response = await authenticatedRequest(`${API_BASE_URL}/api/batch/generate-pdf`, {
        method: 'POST',
        body: JSON.stringify({
          resume_text: result.tailored_resume,
          job_title: result.job_title,
          filename: `${result.job_title.replace(/[^a-z0-9]/gi, '_')}_tailored_resume.pdf`
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${result.job_title.replace(/[^a-z0-9]/gi, '_')}_tailored_resume.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else {
        throw new Error('Failed to generate PDF')
      }
    } catch (error) {
      setError('Failed to download PDF. Please try again.')
      console.error('Error downloading PDF:', error)
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
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${result.job_title.replace(/[^a-z0-9]/gi, '_')}_cover_letter.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else {
        throw new Error('Failed to generate cover letter PDF')
      }
    } catch (error) {
      setError('Failed to download cover letter PDF. Please try again.')
      console.error('Error downloading cover letter PDF:', error)
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

  const canSubmit = (file || resumeText.trim()) && jobUrls.trim() && !loading && !processing && (canUseFeature('resume_processing') || (!safeHasExceededLimit && safeWeeklyUsage < safeWeeklyLimit))

  const [showSuccessBanner, setShowSuccessBanner] = useState(false)
  const [transformationScore, setTransformationScore] = useState(0)

  return (
    <div className="flex min-h-[100dvh] flex-col">
      {/* Sticky Header */}
      <StickyHeader 
        user={user}
        isAuthenticated={isAuthenticated}
        onLogout={handleLogout}
        weeklyUsage={safeWeeklyUsage}
        weeklyLimit={safeWeeklyLimit}
        isProUser={safeIsProUser}
      />

      {/* Hero Section */}
      <HeroSection 
        showSuccessBanner={showSuccessBanner}
        transformationScore={transformationScore}
      />

      <main className="flex-1 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        {/* Testing Button - Only visible when feature flag is enabled */}
        {process.env.ENABLE_TESTING_SUITE === 'true' && (
          <div className="fixed top-20 right-4 z-50">
            <button
              onClick={() => {
                // Always link to dev instance on port 3000
                const devUrl = 'http://localhost:3000/testing';
                window.open(devUrl, '_blank');
              }}
              className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 transform hover:scale-105 flex items-center space-x-2 shadow-lg"
              title="Open Testing Suite in Development Mode"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Testing Suite</span>
              <svg className="w-3 h-3 ml-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        )}

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Mobile Subscription Status */}
          <div className="xl:hidden mb-6">
            <MobileSubscriptionStatus 
              onUpgradeClick={() => window.open('/pricing', '_blank')}
            />
          </div>
          
          {/* Card-based Grid Layout */}
          <motion.div 
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, staggerChildren: 0.1 }}
          >
            {/* Main Content Cards - 2 columns on desktop */}
            <div className="lg:col-span-2 space-y-6">
              {/* Usage Warning Banner */}
              <UsageWarningBanner 
                onUpgradeClick={() => window.open('/pricing', '_blank')}
              />

              <UsageLimitGuard 
                feature="resume_processing"
                showWarnings={false}
                blockWhenExceeded={false}
              >
                {/* Add Resume Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  <AddResumeCard 
                    file={file}
                    resumeText={resumeText}
                    onFileUpload={handleFileUpload}
                    onTextChange={setResumeText}
                    loading={loading}
                  />
                </motion.div>

                {/* Job Opportunities Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <JobOpportunitiesCard 
                    jobUrls={jobUrls}
                    onJobUrlsChange={setJobUrls}
                    loading={loading}
                    isProUser={safeIsProUser}
                  />
                </motion.div>

                {/* Enhance Resume Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <EnhanceResumeCard 
                    tailoringMode={tailoringMode}
                    onModeChange={setTailoringMode}
                    optionalSections={optionalSections}
                    onOptionalSectionsChange={setOptionalSections}
                    coverLetterOptions={coverLetterOptions}
                    onCoverLetterOptionsChange={setCoverLetterOptions}
                    isProUser={safeIsProUser}
                  />
                </motion.div>

                {/* Output Format Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <OutputFormatCard 
                    outputFormat={outputFormat}
                    onFormatChange={setOutputFormat}
                    results={results}
                    onViewResume={viewFullResume}
                    onDownloadPDF={downloadIndividualResumePDF}
                    onDownloadCoverLetter={downloadIndividualCoverLetterPDF}
                    onDownloadText={downloadIndividualResumeText}
                    includeCoverLetter={coverLetterOptions.includeCoverLetter}
                    tailoringMode={tailoringMode}
                    processing={processing}
                    canSubmit={canSubmit}
                    onSubmit={startBatchProcessing}
                    loading={loading}
                    batchStatus={batchStatus}
                    safeHasExceededLimit={safeHasExceededLimit}
                  />
                </motion.div>
              </UsageLimitGuard>
            </div>

            {/* Right Column - Usage Sidebar */}
            <div className="lg:col-span-1">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <UsageSidebarCard 
                  weeklyUsage={safeWeeklyUsage}
                  weeklyLimit={safeWeeklyLimit}
                  isProUser={safeIsProUser}
                  hasExceededLimit={safeHasExceededLimit}
                  onUpgradeClick={() => window.open('/pricing', '_blank')}
                />
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* Success Banner Integration */}
        {results.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
            onAnimationComplete={() => {
              setShowSuccessBanner(true)
              setTransformationScore(85) // Mock transformation score
              setTimeout(() => setShowSuccessBanner(false), 5000)
            }}
          >
            {/* Results will be shown in OutputFormatCard */}
          </motion.div>
        )}

        {/* Error/Success Messages */}
        {error && (
          <div className="mt-6 bg-red-50/80 backdrop-light border border-red-200 text-red-700 px-6 py-4 rounded-xl shadow-sm scroll-optimized">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          </div>
        )}
        
        {success && (
          <div className="mt-6 bg-green-50/80 backdrop-light border border-green-200 text-green-700 px-6 py-4 rounded-xl shadow-sm scroll-optimized">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              {success}
            </div>
          </div>
        )}
      </main>

      {/* Resume View Modal */}
      <ResumeModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        resume={selectedResume?.tailored_resume}
        jobTitle={selectedResume?.job_title}
        originalResume={originalResumeText}
      />

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
        <Home />
      </Layout>
    </ProtectedRoute>
  )
}