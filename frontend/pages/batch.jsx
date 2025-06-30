import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/router';
import ResumeCard from '../components/ResumeCard';

const API_BASE_URL = 'http://localhost:8000/api';

// Modal component for viewing full resume with diff highlighting
const ResumeModal = ({ isOpen, onClose, resume, jobTitle, originalResume }) => {
  if (!isOpen) return null;

  // Simple diff highlighting function
  const highlightChanges = (original, tailored) => {
    if (!original || !tailored) return tailored;
    
    const originalLines = original.split('\n');
    const tailoredLines = tailored.split('\n');
    
    let highlightedText = '';
    
    tailoredLines.forEach((line, index) => {
      const originalLine = originalLines[index] || '';
      
      if (line !== originalLine && line.trim() !== '') {
        // This line is different - highlight it
        highlightedText += `<div class="bg-yellow-100 border-l-4 border-yellow-400 p-1 my-1 rounded">${line}</div>\n`;
      } else {
        highlightedText += `${line}\n`;
      }
    });
    
    return highlightedText;
  };

  const highlightedResume = originalResume ? highlightChanges(originalResume, resume) : resume;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-5xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">📄 {jobTitle}</h2>
            {originalResume && (
              <p className="text-sm text-yellow-600 mt-1">
                💡 Highlighted sections show changes made during tailoring
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          {originalResume ? (
            <div 
              className="whitespace-pre-wrap text-sm text-gray-800 font-mono bg-gray-50 p-4 rounded"
              dangerouslySetInnerHTML={{ __html: highlightedResume }}
            />
          ) : (
            <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono bg-gray-50 p-4 rounded">
              {resume}
            </pre>
          )}
        </div>
        <div className="flex justify-between items-center p-6 border-t border-gray-200">
          <div className="text-sm text-gray-500">
            {originalResume && "🔧 Changes are highlighted for easy review"}
          </div>
          <button
            onClick={onClose}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default function BatchMode() {
  const router = useRouter();
  const [file, setFile] = useState(null);
  const [jobUrls, setJobUrls] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [batchJobId, setBatchJobId] = useState('');
  const [batchStatus, setBatchStatus] = useState(null);
  const [results, setResults] = useState([]);
  const [useRag, setUseRag] = useState(true);
  const [outputFormat, setOutputFormat] = useState('text'); // 'text' or 'files'
  const [pollingInterval, setPollingInterval] = useState(null);
  const [selectedResume, setSelectedResume] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [originalResumeText, setOriginalResumeText] = useState('');
  
  const fileInputRef = useRef(null);

  // Clean up polling on component unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const handleFileUpload = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf' || 
          selectedFile.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Please upload a PDF or DOCX file');
        setFile(null);
      }
    }
  };

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
  };

  const startBatchProcessing = async () => {
    if (!file) {
      setError('Please upload a resume file');
      return;
    }

    const validation = validateJobUrls(jobUrls);
    if (!validation.valid) {
      setError(validation.message);
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      // First upload the resume
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch(`${API_BASE_URL}/resumes/upload`, {
        method: 'POST',
        body: formData
      });

      const uploadData = await uploadResponse.json();

      if (!uploadData.success) {
        throw new Error(uploadData.detail || 'Failed to upload resume');
      }

      setOriginalResumeText(uploadData.resume_text);

      // Start batch processing
      const batchResponse = await fetch(`${API_BASE_URL}/batch/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: uploadData.resume_text,
          job_urls: validation.urls,
          use_rag: useRag,
          output_format: outputFormat
        })
      });

      const batchData = await batchResponse.json();

      if (batchData.success) {
        setBatchJobId(batchData.batch_job_id);
        // Initialize batch status immediately
        setBatchStatus({
          state: 'processing',
          total: validation.urls.length,
          completed: 0,
          failed: 0,
          current_job: 'Starting batch processing...'
        });
        setSuccess(`✅ Batch processing started! Processing ${validation.urls.length} job URLs...`);
        
        // Start polling for status updates immediately
        startStatusPolling(batchData.batch_job_id);
      } else {
        throw new Error(batchData.detail || 'Failed to start batch processing');
      }

    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

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
              // Load results
              loadBatchResults(jobId);
              setSuccess('✅ Batch processing completed!');
            } else {
              setError('❌ Batch processing failed. Please try again.');
            }
          }
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 1500); // Poll every 1.5 seconds for more responsive updates
    
    setPollingInterval(interval);
  };

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
  };

  const viewFullResume = (result) => {
    setSelectedResume(result);
    setModalOpen(true);
  };

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
  };

  const downloadAllResumesZIP = async () => {
    const successfulResults = results.filter(r => r.status === 'success' && r.tailored_resume);
    
    if (successfulResults.length === 0) {
      setError('No successful results to download');
      return;
    }

    try {
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
        throw new Error('Failed to generate ZIP file');
      }
    } catch (error) {
      setError('Failed to download ZIP file. Please try again.');
      console.error('Error downloading ZIP:', error);
    }
  };

  const getStatusColor = (state) => {
    switch (state) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 py-6">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <button
              onClick={() => router.push('/')}
              className="mr-4 text-gray-600 hover:text-gray-800 flex items-center"
            >
              ← Back to Single Mode
            </button>
            <h1 className="text-4xl font-bold text-gray-900">
              ⚡ Batch Mode
            </h1>
          </div>
          <p className="text-lg text-gray-600">
            Process Multiple Jobs Simultaneously with AI-Powered Resume Tailoring
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Left Panel - Input & Settings */}
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
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                />
                
                {file && (
                  <div className="text-sm text-green-600 bg-green-50 p-3 rounded">
                    ✅ {file.name} ready for batch processing
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                />
                
                <div className="text-sm text-gray-500">
                  {jobUrls.trim().split('\n').filter(line => line.trim()).length}/10 URLs
                </div>
              </div>
            </div>

            {/* Batch Settings */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">⚙️ Batch Settings</h2>
              
              <div className="space-y-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="batchUseRag"
                    checked={useRag}
                    onChange={(e) => setUseRag(e.target.checked)}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  />
                  <label htmlFor="batchUseRag" className="ml-2 text-sm text-gray-700">
                    🔍 Enable RAG Enhancement
                  </label>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Output Format
                  </label>
                  <select
                    value={outputFormat}
                    onChange={(e) => setOutputFormat(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="text">PDF Downloads (Recommended)</option>
                    <option value="files">Advanced PDF/DOCX Files</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Start Processing Button */}
            <button
              onClick={startBatchProcessing}
              disabled={loading || !file || !jobUrls.trim()}
              className="w-full bg-purple-600 text-white py-3 px-6 rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold text-lg"
            >
              {loading ? '🔄 Starting Batch...' : '🚀 Start Batch Processing'}
            </button>
          </div>

          {/* Right Panel - Status & Results */}
          <div className="space-y-6">
            
            {/* Batch Status */}
            {batchStatus && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Batch Status</h2>
                
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Current State:</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(batchStatus.state)}`}>
                      {batchStatus.state.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Progress:</span>
                    <span className="text-sm">{batchStatus.completed}/{batchStatus.total} jobs</span>
                  </div>
                  
                  {batchStatus.total > 0 && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(batchStatus.completed / batchStatus.total) * 100}%` }}
                      ></div>
                    </div>
                  )}
                  
                  {batchStatus.current_job && (
                    <div className="text-sm text-gray-600">
                      Currently processing: {batchStatus.current_job}
                    </div>
                  )}
                  
                  <div className="text-xs text-gray-500">
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
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm font-medium flex items-center gap-2"
                  >
                    📦 Download All PDFs (ZIP)
                  </button>
                </div>
                
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {results.map((result, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
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
                          <div className="text-xs text-gray-600 mb-2">
                            Enhancement Score: {result.enhancement_score || 'N/A'}
                          </div>
                          <div className="text-sm bg-gray-50 p-2 rounded max-h-32 overflow-y-auto">
                            {result.tailored_resume.substring(0, 200)}...
                          </div>
                          <div className="mt-2 flex flex-wrap gap-2">
                            <button
                              onClick={() => viewFullResume(result)}
                              className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded hover:bg-blue-100 flex items-center gap-1"
                            >
                              👁️ View Full
                            </button>
                            <button
                              onClick={() => downloadIndividualResumePDF(result)}
                              className="text-xs bg-green-50 text-green-600 px-2 py-1 rounded hover:bg-green-100 flex items-center gap-1"
                            >
                              📄 Download PDF
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

        {/* Resume View Modal */}
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
  );
} 