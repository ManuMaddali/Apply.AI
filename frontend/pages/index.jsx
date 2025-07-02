import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import ResumeCard from '../components/ResumeCard'
import { useRouter } from 'next/router'

const API_BASE_URL = 'http://localhost:8000/api'

// Enhanced Modal component for side-by-side resume comparison
const ResumeModal = ({ isOpen, onClose, resume, jobTitle, originalResume }) => {
  if (!isOpen) return null;

  // Check if content was actually enhanced
  const wasEnhanced = (original, tailored) => {
    if (!original || !tailored) return false;
    const cleanOriginal = original.replace(/\s+/g, ' ').trim();
    const cleanTailored = tailored.replace(/\s+/g, ' ').trim();
    return cleanOriginal !== cleanTailored;
  };

  // Enhanced highlighting - highlight new sections and transformed content
  const highlightNewContent = (original, tailored) => {
    if (!original || !tailored) return tailored;

    // Normalize text for comparison
    const normalizeText = (text) => {
      return text
        .toLowerCase()
        .replace(/\s+/g, ' ')
        .replace(/[^\w\s]/g, ' ')
        .trim();
    };

    // Check if a line exists in original (with some flexibility)
    const lineExistsInOriginal = (line, originalLines) => {
      const normalizedLine = normalizeText(line);
      
      // Check for exact or near matches
      return originalLines.some(origLine => {
        const normalizedOrig = normalizeText(origLine);
        
        // Exact match
        if (normalizedOrig === normalizedLine) return true;
        
        // Very similar (for headers, titles, company names)
        const lineWords = normalizedLine.split(' ').filter(w => w.length > 2);
        const origWords = normalizedOrig.split(' ').filter(w => w.length > 2);
        
        // If it's a short line (like headers), check if most words match
        if (lineWords.length <= 5) {
          const matchingWords = lineWords.filter(w => origWords.includes(w));
          return matchingWords.length >= lineWords.length * 0.7;
        }
        
        return false;
      });
    };

    // Split text into sections and lines for better comparison
    const getTextStructure = (text) => {
      const lines = text.split('\n').map(line => line.trim()).filter(Boolean);
      const normalized = normalizeText(text);
      const words = new Set(normalized.split(/\s+/).filter(w => w.length > 2));
      
      // Identify sections
      const sections = {};
      let currentSection = 'header';
      
      lines.forEach(line => {
        const lineLower = line.toLowerCase();
        if (lineLower.includes('summary') || lineLower.includes('objective')) {
          currentSection = 'summary';
        } else if (lineLower.includes('experience') || lineLower.includes('employment')) {
          currentSection = 'experience';
        } else if (lineLower.includes('skills')) {
          currentSection = 'skills';
        } else if (lineLower.includes('education')) {
          currentSection = 'education';
        }
        
        if (!sections[currentSection]) sections[currentSection] = [];
        sections[currentSection].push(line);
      });
      
      return { lines, normalized, words, sections };
    };

    const originalStructure = getTextStructure(original);
    const tailoredStructure = getTextStructure(tailored);

    // Process tailored text line by line
    let result = '';
    const tailoredLines = tailored.split('\n');
    
    tailoredLines.forEach((line, index) => {
      if (!line.trim()) {
        result += '\n';
        return;
      }
      
      let shouldHighlight = false;
      const lineLower = line.toLowerCase();
      const normalizedLine = normalizeText(line);
      
      // Skip highlighting if this line exists in original (headers, job titles, etc.)
      if (lineExistsInOriginal(line, originalStructure.lines)) {
        result += line + '\n';
        return;
      }
      
      // 1. Check if this is professional summary content (and original didn't have one)
      if ((!originalStructure.sections.summary || originalStructure.sections.summary.length === 0) &&
          index < 15 && // Near the top
          line.length > 40 && // Substantial content
          !line.includes(':') && // Not a header
          !line.match(/^[A-Z\s]+$/) && // Not all caps
          !line.includes('•') && // Not a bullet
          !lineExistsInOriginal(line, originalStructure.lines)) {
        shouldHighlight = true;
      }
      
      // 2. Check if this is a significantly transformed bullet point
      if (line.startsWith('•') || line.startsWith('-') || line.startsWith('*')) {
        // Calculate similarity with original bullets
        let maxSimilarity = 0;
        const lineWords = new Set(normalizedLine.split(/\s+/).filter(w => w.length > 2));
        
        originalStructure.lines.forEach(origLine => {
          if (origLine.startsWith('•') || origLine.startsWith('-') || origLine.startsWith('*')) {
            const origWords = new Set(normalizeText(origLine).split(/\s+/).filter(w => w.length > 2));
            const intersection = new Set([...lineWords].filter(x => origWords.has(x)));
            const similarity = intersection.size / Math.max(lineWords.size, origWords.size);
            maxSimilarity = Math.max(maxSimilarity, similarity);
          }
        });
        
        // If less than 30% similar to any original bullet, it's significantly transformed
        if (maxSimilarity < 0.3) {
          shouldHighlight = true;
        }
      }
      
      // Apply highlighting
      if (shouldHighlight) {
        result += `<span class="bg-green-100 px-1 rounded border border-green-300">${line}</span>\n`;
      } else {
        result += line + '\n';
      }
    });
    
    // Remove trailing newline
    return result.trimEnd();
  };

  const isEnhanced = wasEnhanced(originalResume, resume);
  const highlightedResume = isEnhanced ? highlightNewContent(originalResume, resume) : resume;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200 bg-gray-50">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">📄 {jobTitle}</h2>
            <div className="text-sm text-gray-600 mt-1">
              {isEnhanced ? (
                <span className="text-green-600 font-medium">✨ Resume enhanced with AI tailoring</span>
              ) : (
                <span>Resume preview</span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold p-2 hover:bg-gray-100 rounded"
          >
            ×
          </button>
        </div>

        {/* Side-by-side comparison */}
        {originalResume ? (
          <div className="flex-1 flex overflow-hidden">
            
            {/* Original Resume - Left Side */}
            <div className="w-1/2 border-r border-gray-200 flex flex-col">
              <div className="bg-gray-100 px-4 py-3 border-b border-gray-200">
                <h3 className="font-medium text-gray-900">📝 Original Resume</h3>
                <p className="text-xs text-gray-600">Exactly as you uploaded it</p>
              </div>
              <div className="flex-1 overflow-y-auto p-4 bg-white">
                <pre className="text-sm text-gray-800 font-mono leading-relaxed whitespace-pre-wrap break-words">
{originalResume}
                </pre>
              </div>
            </div>

            {/* Tailored Resume - Right Side */}
            <div className="w-1/2 flex flex-col">
              <div className="bg-blue-50 px-4 py-3 border-b border-gray-200">
                <h3 className="font-medium text-gray-900">✨ AI-Enhanced Resume</h3>
                <p className="text-xs text-gray-600">Tailored for this specific job</p>
              </div>
              <div className="flex-1 overflow-y-auto p-4 bg-white">
                <div 
                  className="text-sm text-gray-800 font-mono leading-relaxed whitespace-pre-wrap break-words"
                  dangerouslySetInnerHTML={{ __html: highlightedResume }}
                />
              </div>
            </div>
          </div>
        ) : (
          // Single view when no original resume
          <div className="flex-1 overflow-y-auto p-6">
            <pre className="text-sm text-gray-800 font-mono leading-relaxed bg-gray-50 p-4 rounded whitespace-pre-wrap break-words">
{resume}
            </pre>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-between items-center p-6 border-t border-gray-200 bg-gray-50">
          <div className="text-sm text-gray-600">
            {isEnhanced ? (
              <div className="flex items-center space-x-4">
                <span className="flex items-center">
                  <div className="w-3 h-3 bg-green-100 border border-green-300 mr-2 rounded"></div>
                  New content highlighted
                </span>
              </div>
            ) : (
              <span className="text-gray-500">Content appears identical</span>
            )}
          </div>
          <button
            onClick={onClose}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition-colors font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default function Home() {
  const router = useRouter()
  const [file, setFile] = useState(null)
  const [jobUrls, setJobUrls] = useState('')
  const [loading, setLoading] = useState(false)
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
  
  const fileInputRef = useRef(null)

  // Clean up polling on component unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

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
    const lines = urls.trim().split('\n').filter(line => line.trim());
    if (lines.length === 0) {
      return { valid: false, message: 'Please enter at least one job URL' };
    }
    if (lines.length > 10) {
      return { valid: false, message: 'Maximum 10 job URLs allowed' };
    }
    
    const invalidUrls = lines.filter(line => {
      try {
        new URL(line.trim());
        return false;
      } catch {
        return true;
      }
    });
    
    if (invalidUrls.length > 0) {
      return { valid: false, message: `Invalid URLs found: ${invalidUrls.slice(0, 3).join(', ')}${invalidUrls.length > 3 ? '...' : ''}` };
    }
    
    return { valid: true, urls: lines.map(line => line.trim()) };
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
          output_format: outputFormat
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
          current_job: 'Starting batch processing with RAG and diff analysis...'
        })
        setSuccess(`✅ Batch processing started! Processing ${validation.urls.length} job URLs with AI enhancement...`)
        
        startStatusPolling(batchData.batch_job_id)
      } else {
        throw new Error(batchData.detail || 'Failed to start batch processing')
      }

    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const startStatusPolling = (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/batch/status/${jobId}`);
        const data = await response.json();
        
        if (data.success) {
          setBatchStatus(data.status);
          
          if (data.status.state === 'completed' || data.status.state === 'failed') {
            clearInterval(interval);
            setPollingInterval(null);
            
            if (data.status.state === 'completed') {
              loadBatchResults(jobId);
              setSuccess('✅ Batch processing completed with RAG enhancement and diff analysis!');
            } else {
              setError('❌ Batch processing failed. Please try again.');
            }
          }
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 1500);
    
    setPollingInterval(interval);
  }

  const loadBatchResults = async (jobId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/batch/results/${jobId}`);
      const data = await response.json();
      
      if (data.success) {
        setResults(data.results);
      }
    } catch (error) {
      console.error('Error loading results:', error);
    }
  }

  const viewFullResume = (result) => {
    setSelectedResume(result);
    setModalOpen(true);
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
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${result.job_title.replace(/[^a-z0-9]/gi, '_')}_tailored_resume.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        throw new Error('Failed to generate PDF');
      }
    } catch (error) {
      setError('Failed to download PDF. Please try again.');
      console.error('Error downloading PDF:', error);
    }
  }

  const downloadIndividualResumeText = (result) => {
    try {
      // Create text file with exact formatting
      const textContent = result.tailored_resume;
      const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${result.job_title.replace(/[^a-z0-9]/gi, '_')}_tailored_resume.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setError('Failed to download text file. Please try again.');
      console.error('Error downloading text:', error);
    }
  }

  const downloadAllResumesZIP = async () => {
    const successfulResults = results.filter(r => r.status === 'success' && r.tailored_resume);
    
    if (successfulResults.length === 0) {
      setError('No successful results to download');
      return;
    }

    try {
      setLoading(true);
      setError(''); // Clear any previous errors
      
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
      });

      if (response.ok) {
        const blob = await response.blob();
        
        // Check if blob has content
        if (blob.size === 0) {
          throw new Error('Generated ZIP file is empty');
        }
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `batch_tailored_resumes_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        setSuccess(`📦 Downloaded ZIP with ${successfulResults.length} tailored resume PDFs!`);
        setTimeout(() => setSuccess(''), 3000);
      } else {
        // Try to get detailed error message from response
        let errorMessage = 'Failed to generate ZIP file';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = `Server error: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('ZIP download error:', error);
      setError(`Failed to download ZIP file: ${error.message}. Please try downloading individual PDFs instead.`);
    } finally {
      setLoading(false);
    }
  }

  const getStatusColor = (state) => {
    switch (state) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-6">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🚀 AI Resume Tailoring Tool
          </h1>
          <p className="text-lg text-gray-600 mb-2">
            Batch Processing with Smart RAG Enhancement & Advanced Diff Analysis
          </p>
          <div className="inline-flex items-center space-x-4 mt-3 p-3 bg-white rounded-lg shadow-sm">
            <span className="flex items-center text-sm text-green-700 bg-green-100 px-2 py-1 rounded">
              🔍 <span className="ml-1 font-medium">RAG Enabled</span>
            </span>
            <span className="flex items-center text-sm text-blue-700 bg-blue-100 px-2 py-1 rounded">
              📊 <span className="ml-1 font-medium">Diff Analysis</span>
            </span>
            <span className="flex items-center text-sm text-purple-700 bg-purple-100 px-2 py-1 rounded">
              ⚡ <span className="ml-1 font-medium">Batch Mode</span>
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Left Panel - Input */}
          <div className="space-y-6">
            
            {/* Resume Upload */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">📄 Upload Resume</h2>
              
              <div className="space-y-4">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileUpload}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                
                {file && (
                  <div className="text-sm text-green-600 bg-green-50 p-3 rounded flex items-center">
                    <span className="mr-2">✅</span>
                    <div>
                      <div className="font-medium">{file.name}</div>
                      <div className="text-xs">Ready for batch processing with AI enhancement</div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Job URLs Input */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">🔗 Job URLs (Max 10)</h2>
              
              <div className="space-y-4">
                <textarea
                  value={jobUrls}
                  onChange={(e) => setJobUrls(e.target.value)}
                  placeholder="Paste job URLs here, one per line:
https://linkedin.com/jobs/view/123456789
https://jobs.company.com/role/product-manager
https://careers.startup.com/positions/senior-dev
..."
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">
                    {jobUrls.trim().split('\n').filter(line => line.trim()).length}/10 URLs
                  </span>
                  <span className="text-blue-600 font-medium">
                    RAG + Diff Analysis included automatically
                  </span>
                </div>
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">⚙️ Output Settings</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Download Format
                  </label>
                  <select
                    value={outputFormat}
                    onChange={(e) => setOutputFormat(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="text">PDF Downloads (Recommended)</option>
                    <option value="files">Advanced PDF/DOCX Files</option>
                  </select>
                </div>
                
                <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded">
                  <div className="font-medium mb-1">✨ Automatic Features:</div>
                  <ul className="space-y-1">
                    <li>• RAG (Retrieval-Augmented Generation) enhancement</li>
                    <li>• Advanced diff analysis with keyword highlighting</li>
                    <li>• Smart content optimization for each job</li>
                    <li>• Enhancement scoring and analytics</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Start Processing Button */}
            <button
              onClick={startBatchProcessing}
              disabled={loading || !file || !jobUrls.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-md hover:from-blue-700 hover:to-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold text-lg shadow-lg"
            >
              {loading ? '🔄 Starting AI Processing...' : '🚀 Start Batch AI Tailoring'}
            </button>
          </div>

          {/* Right Panel - Status & Results */}
          <div className="space-y-6">
            
            {/* Batch Status */}
            {batchStatus && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Processing Status</h2>
                
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Current State:</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(batchStatus.state)}`}>
                      {batchStatus.state.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Progress:</span>
                    <span className="text-sm font-bold">{batchStatus.completed}/{batchStatus.total} jobs</span>
                  </div>
                  
                  {batchStatus.total > 0 && (
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-indigo-500 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${(batchStatus.completed / batchStatus.total) * 100}%` }}
                      ></div>
                    </div>
                  )}
                  
                  {batchStatus.current_job && (
                    <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                      <span className="font-medium">Currently:</span> {batchStatus.current_job}
                    </div>
                  )}
                  
                  <div className="text-xs text-gray-500 text-center">
                    Batch ID: {batchJobId}
                  </div>
                </div>
              </div>
            )}

            {/* Results */}
            {results.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold text-gray-900">📋 Results ({results.length})</h2>
                  <button
                    onClick={downloadAllResumesZIP}
                    disabled={loading}
                    className={`text-sm font-medium flex items-center gap-2 shadow-md px-4 py-2 rounded-md transition-colors ${
                      loading 
                        ? 'bg-gray-400 text-white cursor-not-allowed' 
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {loading ? '🔄 Generating ZIP...' : '📦 Download All (ZIP)'}
                  </button>
                </div>
                
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {results.map((result, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-gray-900 truncate">{result.job_title}</h3>
                          <p className="text-xs text-gray-500 truncate">{result.job_url}</p>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium whitespace-nowrap ml-2 ${
                          result.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {result.status}
                        </span>
                      </div>
                      
                      {result.status === 'success' && result.tailored_resume && (
                        <div className="mt-3">
                          <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
                            <span>
                              Enhancement Score: <span className="font-bold text-green-600">{result.enhancement_score || 'N/A'}</span>
                            </span>
                            <span className="text-blue-600">✨ RAG + Diff Applied</span>
                          </div>
                          <div className="text-sm bg-gray-50 p-2 rounded max-h-32 overflow-y-auto">
                            {result.tailored_resume.substring(0, 200)}...
                          </div>
                          <div className="mt-3 flex flex-wrap gap-2">
                            <button
                              onClick={() => viewFullResume(result)}
                              className="text-xs bg-blue-50 text-blue-600 px-3 py-1 rounded hover:bg-blue-100 flex items-center gap-1 font-medium"
                            >
                              👁️ View with Highlights
                            </button>
                            <button
                              onClick={() => downloadIndividualResumePDF(result)}
                              className="text-xs bg-green-50 text-green-600 px-3 py-1 rounded hover:bg-green-100 flex items-center gap-1 font-medium"
                            >
                              📄 Download PDF
                            </button>
                            <button
                              onClick={() => downloadIndividualResumeText(result)}
                              className="text-xs bg-purple-50 text-purple-600 px-3 py-1 rounded hover:bg-purple-100 flex items-center gap-1 font-medium"
                            >
                              📄 Download Text
                            </button>
                          </div>
                        </div>
                      )}
                      
                      {result.status === 'failed' && (
                        <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                          Error: {result.error}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Resume View Modal with Enhanced Diff Highlighting */}
        <ResumeModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          resume={selectedResume?.tailored_resume}
          jobTitle={selectedResume?.job_title}
          originalResume={originalResumeText}
        />

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