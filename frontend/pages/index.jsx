import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import ResumeCard from '../components/ResumeCard'
import { useRouter } from 'next/router'

const API_BASE_URL = 'http://localhost:8000/api'

export default function Home() {
  const router = useRouter()
  const [file, setFile] = useState(null)
  const [jobUrl, setJobUrl] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [tailoredResume, setTailoredResume] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [originalResume, setOriginalResume] = useState('')
  const [useRag, setUseRag] = useState(true)
  const [compareVersions, setCompareVersions] = useState(true)
  const [ragInsights, setRagInsights] = useState(null)
  const [diffAnalysis, setDiffAnalysis] = useState(null)
  const [sessionId, setSessionId] = useState('')
  const [sessions, setSessions] = useState([])
  const [showDiffDetails, setShowDiffDetails] = useState(false)
  const [ragStatus, setRagStatus] = useState(null)
  
  const fileInputRef = useRef(null)

  // Check RAG status on component mount
  const checkRagStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/resumes/rag-status`)
      const data = await response.json()
      setRagStatus(data)
    } catch (error) {
      console.error('Error checking RAG status:', error)
    }
  }

  // Load session history
  const loadSessions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/resumes/sessions`)
      const data = await response.json()
      if (data.success) {
        setSessions(Object.entries(data.sessions))
      }
    } catch (error) {
      console.error('Error loading sessions:', error)
    }
  }

  useEffect(() => {
    checkRagStatus()
    loadSessions()
  }, [])

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

  const scrapeJobDescription = async () => {
    if (!jobUrl) {
      setError('Please enter a job URL')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/jobs/scrape`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_url: jobUrl })
      })

      const data = await response.json()
      
      if (data.success) {
        setJobDescription(data.job_description)
        setJobTitle(data.job_title || 'Product Manager')
        setSuccess('Job description scraped successfully!')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError(data.detail || 'Failed to scrape job description')
      }
    } catch (error) {
      setError('Network error occurred')
    } finally {
      setLoading(false)
    }
  }

  const uploadAndTailorResume = async () => {
    if (!file) {
      setError('Please upload a resume file')
      return
    }
    if (!jobDescription) {
      setError('Please scrape a job description first')
      return
    }

    setLoading(true)
    setError('')
    setTailoredResume('')
    setDiffAnalysis(null)
    setRagInsights(null)

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

      setOriginalResume(uploadData.resume_text)

      // Then tailor the resume with LangChain
      const tailorResponse = await fetch(`${API_BASE_URL}/resumes/tailor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: uploadData.resume_text,
          job_description: jobDescription,
          job_title: jobTitle || 'Product Manager',
          job_url: jobUrl,
          use_rag: useRag,
          compare_versions: compareVersions
        })
      })

      const tailorData = await tailorResponse.json()

      if (tailorData.success) {
        setTailoredResume(tailorData.tailored_resume)
        setSessionId(tailorData.session_id)
        setRagInsights(tailorData.rag_insights)
        setDiffAnalysis(tailorData.diff_analysis)
        setSuccess(`✅ Resume tailored successfully using ${tailorData.processing_mode} mode!`)
        
        // Reload sessions
        loadSessions()
        
        setTimeout(() => setSuccess(''), 5000)
      } else {
        throw new Error(tailorData.detail || 'Failed to tailor resume')
      }

    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const loadSession = async (sessionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/resumes/session/${sessionId}`)
      const data = await response.json()
      
      if (data.success) {
        const session = data.session_data
        setOriginalResume(session.original_resume)
        setTailoredResume(session.tailored_resume)
        setJobDescription(session.job_description)
        setJobTitle(session.job_title)
        setSessionId(sessionId)
        
        // Perform diff analysis for loaded session
        if (compareVersions) {
          const diffResponse = await fetch(`${API_BASE_URL}/resumes/analyze-diff`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              original_resume: session.original_resume,
              tailored_resume: session.tailored_resume,
              job_title: session.job_title
            })
          })
          
          const diffData = await diffResponse.json()
          if (diffData.success) {
            setDiffAnalysis(diffData.diff_analysis)
          }
        }
        
        setSuccess('Session loaded successfully!')
        setTimeout(() => setSuccess(''), 3000)
      }
    } catch (error) {
      setError('Failed to load session')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🚀 AI Resume Tailoring App
          </h1>
          <p className="text-lg text-gray-600">
            LangChain-Powered RAG System with Smart Diff Analysis
          </p>
          {ragStatus && (
            <div className={`inline-block mt-2 px-3 py-1 rounded-full text-sm ${
              ragStatus.rag_available 
                ? 'bg-green-100 text-green-800' 
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {ragStatus.rag_available ? '🟢 RAG System Active' : '🟡 RAG System Initializing'}
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Panel - Upload & Settings */}
          <div className="space-y-6">
            
            {/* File Upload */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">📄 Upload Resume</h2>
              
              <div className="space-y-4">
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleFileUpload}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>
                
                {file && (
                  <div className="text-sm text-green-600 bg-green-50 p-2 rounded">
                    ✅ {file.name} ready for upload
                  </div>
                )}
              </div>
            </div>

            {/* AI Settings */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">🤖 AI Settings</h2>
              
              <div className="space-y-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="useRag"
                    checked={useRag}
                    onChange={(e) => setUseRag(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="useRag" className="ml-2 text-sm text-gray-700">
                    🔍 Enable RAG (Retrieval-Augmented Generation)
                  </label>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="compareVersions"
                    checked={compareVersions}
                    onChange={(e) => setCompareVersions(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="compareVersions" className="ml-2 text-sm text-gray-700">
                    📊 Enable Diff Analysis
                  </label>
                </div>
              </div>
            </div>

            {/* Session History */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-900">📝 Session History</h2>
                <button
                  onClick={loadSessions}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  Refresh
                </button>
              </div>
              
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {sessions.length > 0 ? (
                  sessions.map(([id, session]) => (
                    <div 
                      key={id}
                      onClick={() => loadSession(id)}
                      className="p-2 bg-gray-50 rounded cursor-pointer hover:bg-blue-50 transition-colors"
                    >
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {session.job_title}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(session.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-gray-500 text-center py-4">
                    No sessions yet
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Middle Panel - Job Input */}
          <div className="space-y-6">
            
            {/* Job URL Scraping */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">🌐 Job URL Scraping</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job URL
                  </label>
                  <input
                    type="url"
                    value={jobUrl}
                    onChange={(e) => setJobUrl(e.target.value)}
                    placeholder="https://linkedin.com/jobs/view/..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <button
                  onClick={scrapeJobDescription}
                  disabled={loading || !jobUrl}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? '🔄 Scraping...' : '🔍 Scrape Job Description'}
                </button>
              </div>
            </div>

            {/* Scraped Job Info */}
            {jobDescription && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">✅ Job Details</h2>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Job Title
                    </label>
                    <div className="text-sm bg-gray-50 p-2 rounded">
                      {jobTitle}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Job Description (Preview)
                    </label>
                    <div className="text-sm bg-gray-50 p-2 rounded max-h-32 overflow-y-auto">
                      {jobDescription.substring(0, 300)}...
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Generate Button */}
            <button
              onClick={uploadAndTailorResume}
              disabled={loading || !file || !jobDescription}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold"
            >
              {loading ? '🔄 Processing...' : '✨ Tailor Resume with AI'}
            </button>

            {/* Batch Mode Tile */}
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg shadow-lg p-6 border border-purple-200">
              <div className="text-center">
                <div className="text-2xl mb-2">⚡</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Batch Mode</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Process multiple jobs at once. Upload resume + paste up to 10 job links for automated tailoring.
                </p>
                <button
                  onClick={() => router.push('/batch')}
                  className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors font-medium"
                >
                  🚀 Launch Batch Mode
                </button>
              </div>
            </div>
          </div>

          {/* Right Panel - RAG Insights & Analytics */}
          <div className="space-y-6">
            
            {/* RAG Insights */}
            {ragInsights && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">🧠 RAG Insights</h2>
                
                <div className="space-y-3">
                  <div className="text-sm">
                    <span className="font-medium">Similar Jobs Found:</span> {ragInsights.similar_jobs_found}
                  </div>
                  
                  <div className="text-sm">
                    <span className="font-medium">Processing Steps:</span>
                    <ul className="list-disc list-inside ml-2 mt-1">
                      {ragInsights.processing_steps.map((step, index) => (
                        <li key={index} className="text-gray-600">{step}</li>
                      ))}
                    </ul>
                  </div>

                  {ragInsights.insights && ragInsights.insights.length > 0 && (
                    <div className="text-sm">
                      <span className="font-medium">Industry Insights:</span>
                      <div className="space-y-1 mt-1">
                        {ragInsights.insights.map((insight, index) => (
                          <div key={index} className="text-xs bg-blue-50 p-2 rounded">
                            {insight.job_title} - {insight.job_url}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Diff Analysis Summary */}
            {diffAnalysis && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold text-gray-900">📊 Diff Analysis</h2>
                  <button
                    onClick={() => setShowDiffDetails(!showDiffDetails)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    {showDiffDetails ? 'Hide Details' : 'Show Details'}
                  </button>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-green-50 rounded">
                    <span className="text-sm font-medium">Enhancement Score</span>
                    <span className="text-lg font-bold text-green-600">
                      {diffAnalysis.enhancement_score.overall_score}/100
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="text-center p-2 bg-blue-50 rounded">
                      <div className="font-medium">{diffAnalysis.summary.sections_modified}</div>
                      <div className="text-gray-600">Sections Modified</div>
                    </div>
                    <div className="text-center p-2 bg-purple-50 rounded">
                      <div className="font-medium">{diffAnalysis.content_changes.words_added}</div>
                      <div className="text-gray-600">Words Added</div>
                    </div>
                  </div>
                  
                  <div className="text-sm">
                    <span className="font-medium">Assessment:</span>
                    <div className="text-gray-600 mt-1">
                      {diffAnalysis.enhancement_score.assessment}
                    </div>
                  </div>
                </div>

                {showDiffDetails && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h3 className="font-medium mb-3">Section Changes:</h3>
                    <div className="space-y-2 text-sm">
                      {Object.entries(diffAnalysis.section_changes).map(([section, change]) => (
                        <div key={section} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="font-medium">{section.toUpperCase()}</span>
                          <span className={`px-2 py-1 rounded text-xs ${
                            change.change_type === 'modified' ? 'bg-yellow-100 text-yellow-800' :
                            change.change_type === 'enhanced' ? 'bg-green-100 text-green-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {change.change_type}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {(originalResume || tailoredResume) && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">📋 Resume Comparison</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {originalResume && (
                <ResumeCard
                  title="📄 Original Resume"
                  content={originalResume}
                  cardClass="bg-gray-50 border-gray-200"
                />
              )}
              
              {tailoredResume && (
                <ResumeCard
                  title="✨ Tailored Resume"
                  content={tailoredResume}
                  cardClass="bg-blue-50 border-blue-200"
                />
              )}
            </div>
          </div>
        )}

        {/* Status Messages */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {success && (
          <div className="mt-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}
      </div>
    </div>
  )
} 