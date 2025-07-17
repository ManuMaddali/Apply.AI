import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileText, Menu, X, User, LogOut, Settings, Star, CreditCard } from "lucide-react"
import FileUpload from '../components/FileUpload'
import JobUrlsInput from '../components/JobUrlsInput'
import OutputSettings from '../components/OutputSettings'
import OptionalSections from '../components/OptionalSections'
import CoverLetter from '../components/CoverLetter'
import ResultCard from '../components/ResultCard'
import ResumeModal from '../components/ResumeModal'
import ProtectedRoute from '../components/ProtectedRoute'
import { API_BASE_URL } from '../utils/api'
import { useAuth } from '../contexts/AuthContext'

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

  // Clean up polling on component unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
  }, [pollingInterval])

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
    if (!file && !resumeText.trim()) {
      setError('Please upload a resume file or enter resume text')
      return
    }

    const validation = validateJobUrls(jobUrls)
    if (!validation.valid) {
      setError(validation.message)
      return
    }

    setLoading(true)
    setProcessing(true)
    setError('')
    setResults([])

    try {
      let processedResumeText = ''

      if (file) {
        // Handle file upload
        const formData = new FormData()
        formData.append('file', file)

        const uploadResponse = await authenticatedRequest(`${API_BASE_URL}/resumes/upload`, {
          method: 'POST',
          body: formData,
          headers: {} // Let authenticatedRequest handle headers
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
      const batchResponse = await authenticatedRequest(`${API_BASE_URL}/batch/process`, {
        method: 'POST',
        body: JSON.stringify({
          resume_text: processedResumeText,
          job_urls: validation.urls,
          use_rag: true, // Always enabled
          compare_versions: true, // Always enabled
          output_format: outputFormat,
          optional_sections: optionalSections, // Include the optional sections preferences
          cover_letter_options: coverLetterOptions // Include cover letter options
        })
      })

      const batchData = await batchResponse.json()

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
        const initialResults = validation.urls.map((url, index) => ({
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
      setError(error.message)
      setProcessing(false)
    } finally {
      setLoading(false)
    }
  }

  const startStatusPolling = (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await authenticatedRequest(`${API_BASE_URL}/batch/status/${jobId}`)
        const data = await response.json()
        
        if (data.success) {
          setBatchStatus(data.status)
          
          if (data.status.state === 'completed' || data.status.state === 'failed') {
            clearInterval(interval)
            setPollingInterval(null)
            setProcessing(false)
            
            if (data.status.state === 'completed') {
              loadBatchResults(jobId)
            } else {
              setError('Batch processing failed. Please try again.')
            }
          }
        }
      } catch (error) {
        console.error('Error polling status:', error)
      }
    }, 1500)
    
    setPollingInterval(interval)
  }

  const loadBatchResults = async (jobId) => {
    try {
      const response = await authenticatedRequest(`${API_BASE_URL}/batch/results/${jobId}`)
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
      const response = await authenticatedRequest(`${API_BASE_URL}/batch/generate-pdf`, {
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
      const response = await authenticatedRequest(`${API_BASE_URL}/batch/generate-cover-letter-pdf`, {
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

  const canSubmit = (file || resumeText.trim()) && jobUrls.trim() && !loading && !processing

  return (
    <div className="flex min-h-[100dvh] flex-col">
      <header className="px-4 lg:px-6 h-16 flex items-center justify-between border-b bg-white/80 backdrop-blur-sm">
        <Link className="flex items-center gap-2 font-semibold" href="/">
          <FileText className="h-6 w-6 text-blue-600" />
          <span>ApplyAI</span>
        </Link>
        <MobileNav />
        <nav className="hidden md:flex gap-6">
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/how-it-works">
            How It Works
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/faq">
            FAQ
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/about">
            About
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/blog">
            Blog
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/contact">
            Contact
          </Link>
        </nav>
        <div className="hidden md:flex gap-4 items-center">
          {/* User profile and logout for desktop */}
          {isAuthenticated && (
            <>
              <div className="flex items-center gap-2 mr-2">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm font-medium">{user?.full_name || user?.email}</span>
              </div>
              <Button 
                variant="outline" 
                className="flex items-center gap-2 text-red-600 border-red-200 hover:bg-red-50"
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </Button>
            </>
          )}
        </div>
      </header>

      <main className="flex-1 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        {/* App Title Section */}
        <div className="relative bg-white/80 backdrop-light border-b border-white/50 shadow-sm scroll-optimized">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5"></div>
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Testing Button - Only visible when feature flag is enabled */}
            {process.env.ENABLE_TESTING_SUITE === 'true' && (
              <div className="absolute top-4 right-4">
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
            
            <div className="text-center">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
                </div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                  Apply.AI
                </h1>
              </div>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
                Transform your resume for every opportunity. Our AI analyzes job descriptions and tailors your resume to match what employers are looking for.
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          
          {/* Left Column - Inputs (Takes 2/3 of space) */}
          <div className="xl:col-span-2 space-y-6">
            <FileUpload 
              file={file} 
              onFileChange={handleFileUpload}
              resumeText={resumeText}
              onResumeTextChange={handleResumeTextChange}
            />
            
            <JobUrlsInput 
              jobUrls={jobUrls} 
              onJobUrlsChange={setJobUrls} 
            />
            
            <CoverLetter 
              options={coverLetterOptions}
              onOptionsChange={setCoverLetterOptions}
            />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <OptionalSections 
                options={optionalSections}
                onOptionsChange={setOptionalSections}
              />
              
              <OutputSettings 
                outputFormat={outputFormat} 
                onFormatChange={setOutputFormat} 
              />
            </div>
          </div>

          {/* Right Column - Results & Action */}
          <div className="xl:col-span-1 space-y-6">
            {/* Sticky Action Card */}
            <div className="sticky top-8 z-20 sticky-optimized">
              <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-6 scroll-optimized">
                <div className="text-center mb-6">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready to Apply?</h3>
                  <p className="text-sm text-gray-600">Your tailored resumes will appear below</p>
                </div>

                {/* Submit Button */}
                <button
                  onClick={startBatchProcessing}
                  disabled={!canSubmit}
                  className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-300 transform ${
                    canSubmit
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl hover:scale-105'
                      : 'bg-gray-300 cursor-not-allowed'
                  }`}
                >
                  {(loading || processing) ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Tailoring Your Resume...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Tailor My Resume
                    </span>
                  )}
                </button>

                {/* Status Indicators */}
                <div className="mt-4 space-y-2">
                  <div className={`flex items-center text-sm ${(file || resumeText.trim()) ? 'text-green-600' : 'text-gray-400'}`}>
                    <div className={`w-2 h-2 rounded-full mr-2 ${(file || resumeText.trim()) ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    Resume {(file || resumeText.trim()) ? 'ready' : 'required'}
                  </div>
                  <div className={`flex items-center text-sm ${jobUrls.trim() ? 'text-green-600' : 'text-gray-400'}`}>
                    <div className={`w-2 h-2 rounded-full mr-2 ${jobUrls.trim() ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    Job URLs {jobUrls.trim() ? 'added' : 'required'}
                  </div>
                  {coverLetterOptions.includeCoverLetter && (
                    <div className="flex items-center text-sm text-indigo-600">
                      <div className="w-2 h-2 rounded-full mr-2 bg-indigo-500"></div>
                      Cover letter enabled
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Progress Indicator */}
            {processing && batchStatus && (
              <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-6 scroll-optimized">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Processing</h3>
                  <span className="text-sm text-gray-500">
                    {batchStatus.completed}/{batchStatus.total} completed
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${(batchStatus.completed / batchStatus.total) * 100}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600 mt-2">{batchStatus.current_job}</p>
              </div>
            )}

            {/* Results Section */}
            {results.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Your Tailored Resumes</h3>
                  {results.some(r => r.status === 'success') && (
                    <button
                      onClick={async () => {
                        const successfulResults = results.filter(r => r.status === 'success' && r.tailored_resume)
                        
                        if (successfulResults.length === 0) {
                          setError('No successful results to download')
                          return
                        }

                        try {
                          setLoading(true)
                          
                          const response = await authenticatedRequest(`${API_BASE_URL}/batch/generate-zip`, {
                            method: 'POST',
                            body: JSON.stringify({
                              resumes: successfulResults.map(result => ({
                                resume_text: result.tailored_resume,
                                job_title: result.job_title,
                                job_url: result.job_url,
                                enhancement_score: result.enhancement_score,
                                cover_letter: result.cover_letter || null
                              })),
                              batch_id: batchJobId,
                              include_cover_letters: coverLetterOptions.includeCoverLetter
                            })
                          })

                          if (response.ok) {
                            const blob = await response.blob()
                            
                            if (blob.size === 0) {
                              throw new Error('Generated ZIP file is empty')
                            }
                            
                            const url = window.URL.createObjectURL(blob)
                            const a = document.createElement('a')
                            a.href = url
                            a.download = `Apply_AI_Resumes_${new Date().toISOString().split('T')[0]}.zip`
                            document.body.appendChild(a)
                            a.click()
                            document.body.removeChild(a)
                            window.URL.revokeObjectURL(url)
                          } else {
                            throw new Error('Failed to generate ZIP file')
                          }
                        } catch (error) {
                          setError('Failed to download ZIP file. Please try downloading individual PDFs instead.')
                        } finally {
                          setLoading(false)
                        }
                      }}
                      className="text-sm bg-gradient-to-r from-green-600 to-green-700 text-white px-4 py-2 rounded-lg hover:from-green-700 hover:to-green-800 transition-all duration-200 font-medium flex items-center gap-2 shadow-md"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                      </svg>
                      Download All
                      {outputFormat === 'files' && <span className="text-xs opacity-75 ml-1">PDF + Word</span>}
                      {outputFormat === 'docx' && <span className="text-xs opacity-75 ml-1">Word</span>}
                      {outputFormat === 'text' && <span className="text-xs opacity-75 ml-1">PDF</span>}
                    </button>
                  )}
                </div>
                
                <div className="space-y-4 max-h-[800px] overflow-y-auto custom-scrollbar">
                  {results.map((result, index) => (
                    <ResultCard
                      key={index}
                      result={result}
                      onView={viewFullResume}
                      onDownloadPDF={downloadIndividualResumePDF}
                      onDownloadCoverLetter={downloadIndividualCoverLetterPDF}
                      onDownloadText={downloadIndividualResumeText}
                      includeCoverLetter={coverLetterOptions.includeCoverLetter}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {!processing && results.length === 0 && (
              <div className="bg-white/50 backdrop-light rounded-2xl border border-white/50 p-12 text-center scroll-optimized">
                <div className="mx-auto w-16 h-16 bg-gradient-to-r from-gray-200 to-gray-300 rounded-2xl flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-gray-600 text-lg">Upload your resume and add job URLs to get started</p>
                <p className="text-gray-500 text-sm mt-2">Your tailored resumes will appear here</p>
              </div>
            )}
          </div>
        </div>

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
        </div>
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
      <Home />
    </ProtectedRoute>
  )
}