import React, { useState, useRef, useEffect } from 'react'
import FileUpload from '../components/FileUpload'
import JobUrlsInput from '../components/JobUrlsInput'
import OutputSettings from '../components/OutputSettings'
import OptionalSections from '../components/OptionalSections'
import ResultCard from '../components/ResultCard'
import ResumeModal from '../components/ResumeModal'

const API_BASE_URL = 'http://localhost:8000/api'

export default function Home() {
  const [file, setFile] = useState(null)
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

  // Clean up polling on component unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
  }, [pollingInterval])

  const handleFileUpload = (event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf' || 
          selectedFile.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        setFile(selectedFile)
        setError('')
      } else {
        setError('Please upload a PDF or DOCX file')
        setFile(null)
      }
    }
  }

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
    if (!file) {
      setError('Please upload a resume file')
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
      // First upload the resume
      const formData = new FormData()
      formData.append('file', file)

      const uploadResponse = await fetch(`${API_BASE_URL}/resumes/upload`, {
        method: 'POST',
        body: formData
      })

      const uploadData = await uploadResponse.json()

      if (!uploadData.success) {
        throw new Error(uploadData.detail || 'Failed to upload resume')
      }

      setOriginalResumeText(uploadData.resume_text)

      // Start batch processing with RAG and diff analysis enabled by default
      const batchResponse = await fetch(`${API_BASE_URL}/batch/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: uploadData.resume_text,
          job_urls: validation.urls,
          use_rag: true, // Always enabled
          compare_versions: true, // Always enabled
          output_format: outputFormat,
          optional_sections: optionalSections // Include the optional sections preferences
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
        const response = await fetch(`${API_BASE_URL}/batch/status/${jobId}`)
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
      const response = await fetch(`${API_BASE_URL}/batch/results/${jobId}`)
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
      const response = await fetch(`${API_BASE_URL}/batch/generate-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">
              AI Resume Tailoring
            </h1>
            <p className="mt-2 text-lg text-gray-600">
              Create personalized resumes for every job application
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Left Column - Input */}
          <div className="space-y-6">
            <FileUpload 
              file={file} 
              onFileChange={handleFileUpload} 
            />
            
            <JobUrlsInput 
              jobUrls={jobUrls} 
              onJobUrlsChange={setJobUrls} 
            />
            
            <OptionalSections 
              options={optionalSections}
              onOptionsChange={setOptionalSections}
            />
            
            <OutputSettings 
              outputFormat={outputFormat} 
              onFormatChange={setOutputFormat} 
            />

            {/* Submit Button */}
            <button
              onClick={startBatchProcessing}
              disabled={loading || processing || !file || !jobUrls.trim()}
              className={`w-full py-4 px-6 rounded-xl font-medium text-white transition-all duration-200 ${
                loading || processing || !file || !jobUrls.trim()
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg hover:shadow-xl'
              }`}
            >
              {(loading || processing) ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating…
                </span>
              ) : (
                'Tailor My Resume'
              )}
            </button>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            {/* Progress Indicator */}
            {processing && batchStatus && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Tailoring in Progress</h3>
                  <span className="text-sm text-gray-500">
                    {batchStatus.completed}/{batchStatus.total} completed
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(batchStatus.completed / batchStatus.total) * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* Results */}
            {results.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Results</h3>
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
                          
                          const response = await fetch(`${API_BASE_URL}/batch/generate-zip`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                              resumes: successfulResults.map(result => ({
                                resume_text: result.tailored_resume,
                                job_title: result.job_title,
                                job_url: result.job_url,
                                enhancement_score: result.enhancement_score
                              })),
                              batch_id: batchJobId
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
                            a.download = `batch_tailored_resumes_${new Date().toISOString().split('T')[0]}.zip`
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
                      className="text-sm bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                      </svg>
                      Download All
                    </button>
                  )}
                </div>
                
                <div className="space-y-4 max-h-[600px] overflow-y-auto custom-scrollbar pr-2">
                  {results.map((result, index) => (
                    <ResultCard
                      key={index}
                      result={result}
                      onView={viewFullResume}
                      onDownloadPDF={downloadIndividualResumePDF}
                      onDownloadText={downloadIndividualResumeText}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {!processing && results.length === 0 && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
                <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-gray-600">Your tailored resumes will appear here</p>
              </div>
            )}
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
            {error}
          </div>
        )}
        
        {success && (
          <div className="mt-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl flex items-center gap-2">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            {success}
          </div>
        )}
      </div>

      {/* Resume View Modal */}
      <ResumeModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        resume={selectedResume?.tailored_resume}
        jobTitle={selectedResume?.job_title}
        originalResume={originalResumeText}
      />
    </div>
  )
} 