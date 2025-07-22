import React, { useState, useCallback, useEffect } from 'react';
import { testResumes } from '../data/testResumes';
import { jobUrlCollections, testScenarios } from '../data/testJobUrls';
import FileUpload from '../components/FileUpload';
import JobUrlsInput from '../components/JobUrlsInput';
import CoverLetter from '../components/CoverLetter';
import OptionalSections from '../components/OptionalSections';
import OutputSettings from '../components/OutputSettings';
import ResultCard from '../components/ResultCard';
import TestingUtils from '../components/TestingUtils';
import SubscriptionTestPage from '../components/SubscriptionTestPage';
import { API_BASE_URL, checkBackendHealth } from '../utils/api';

export default function TestingPage() {
  // Check feature flag and environment access
  useEffect(() => {
    // Redirect if testing suite is disabled via feature flag
    if (process.env.ENABLE_TESTING_SUITE !== 'true') {
      window.location.href = '/';
    }
    // Also redirect in production unless specifically enabled
    else if (process.env.NODE_ENV === 'production' && process.env.ENABLE_TESTING_SUITE !== 'true') {
      window.location.href = '/';
    }
  }, []);

  // State management - same as main page
  const [file, setFile] = useState(null);
  const [jobUrls, setJobUrls] = useState('');
  const [coverLetterEnabled, setCoverLetterEnabled] = useState(false);
  const [coverLetterOptions, setCoverLetterOptions] = useState({
    tone: 'professional',
    emphasis: 'experience',
    additionalInfo: ''
  });
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
  });
  const [outputSettings, setOutputSettings] = useState({
    format: 'pdf',
    jobTitle: '',
    companyName: '',
    includeKeywords: true,
    useRAG: true
  });
  const [results, setResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [error, setError] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('');

  // Testing-specific state
  const [selectedTestResume, setSelectedTestResume] = useState('');
  const [selectedJobCategory, setSelectedJobCategory] = useState('');
  const [selectedTestScenario, setSelectedTestScenario] = useState('');
  const [testingMode, setTestingMode] = useState('manual'); // 'manual' or 'scenario'
  const [activeTab, setActiveTab] = useState('resume'); // 'resume' or 'subscription'

  // Helper functions
  const loadTestResume = useCallback((resumeId) => {
    const resume = testResumes.find(r => r.id === resumeId);
    if (resume) {
      // Create a mock file object
      const mockFile = new File(
        [resume.content],
        `${resume.name}.txt`,
        { type: 'text/plain' }
      );
      setFile(mockFile);
      setSelectedTestResume(resumeId);
    }
  }, []);

  const loadJobUrls = useCallback((category) => {
    const urls = jobUrlCollections[category];
    if (urls) {
      setJobUrls(urls.slice(0, 3).join('\n')); // Load first 3 URLs as string
      setSelectedJobCategory(category);
    }
  }, []);

  const loadTestScenario = useCallback((scenarioId) => {
    const scenario = testScenarios.find(s => s.id === scenarioId);
    if (scenario) {
      loadTestResume(scenario.resumeId);
      setJobUrls(scenario.jobUrls.join('\n')); // Convert array to string
      setSelectedTestScenario(scenarioId);
      setTestingMode('scenario');
    }
  }, [loadTestResume]);

  const clearAll = useCallback(() => {
    setFile(null);
    setJobUrls('');
    setSelectedTestResume('');
    setSelectedJobCategory('');
    setSelectedTestScenario('');
    setResults([]);
    setTestingMode('manual');
    setError('');
    setProcessingStatus('');
    setConnectionStatus('');
  }, []);

  // Test backend connectivity
  const testBackendConnection = async () => {
    try {
      console.log('Testing backend connection...');
      setConnectionStatus('Testing backend connection...');
      setError('');
      
      const data = await checkBackendHealth();
      console.log('Backend response:', data);
      setConnectionStatus(`✅ Backend connection successful! Status: ${data.status}`);
      setTimeout(() => setConnectionStatus(''), 3000);
    } catch (error) {
      console.error('Backend connection error:', error);
      setError(`Backend connection failed: ${error.message}. Make sure the backend server is running.`);
      setConnectionStatus('');
    }
  };

  // Main processing function (matching main page)
  const handleTailorApplication = async () => {
    const jobUrlsArray = jobUrls.trim().split('\n').filter(url => url.trim());
    
    if (!file || jobUrlsArray.length === 0) {
      alert('Please upload a resume and add at least one job URL');
      return;
    }

    setIsProcessing(true);
    setProcessingStatus('Starting batch processing...');
    setResults([]);
    setError('');
    
    console.log('Testing: Starting processing with:', {
      file: file.name,
      jobUrls: jobUrlsArray,
      coverLetterEnabled,
      optionalSections,
      outputSettings
    });

    try {
      // First upload the resume
      const formData = new FormData();
      formData.append('file', file);

      setProcessingStatus('Uploading resume...');
      const uploadResponse = await fetch(`${API_BASE_URL}/resumes/upload`, {
        method: 'POST',
        body: formData
      });

      const uploadData = await uploadResponse.json();

      if (!uploadData.success) {
        throw new Error(uploadData.detail || 'Failed to upload resume');
      }

      setProcessingStatus('Starting AI processing...');

      // Start batch processing with uploaded resume text
      const batchResponse = await fetch(`${API_BASE_URL}/batch/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: uploadData.resume_text,
          job_urls: jobUrlsArray,
          use_rag: true,
          compare_versions: true,
          output_format: outputSettings.format || 'pdf',
          optional_sections: optionalSections,
          cover_letter_options: coverLetterEnabled ? coverLetterOptions : null
        })
      });

      const batchData = await batchResponse.json();

      if (batchData.success) {
        // Start polling for results
        const batchJobId = batchData.batch_job_id;
        setProcessingStatus('Processing resumes...');
        
        // Initialize results with processing state
        const initialResults = jobUrlsArray.map((url, index) => ({
          job_url: url,
          status: 'processing',
          job_title: 'Processing...'
        }));
        setResults(initialResults);
        
        // Poll for completion
        pollForResults(batchJobId);
      } else {
        throw new Error(batchData.detail || 'Failed to start batch processing');
      }

    } catch (error) {
      console.error('Error processing application:', error);
      setError(error.message);
      setProcessingStatus('');
      setIsProcessing(false);
    }
  };

  // Polling function for batch processing results
  const pollForResults = async (batchJobId) => {
    const maxAttempts = 60; // 5 minutes max
    let attempts = 0;

    const poll = async () => {
      try {
        attempts++;
        const response = await fetch(`${API_BASE_URL}/batch/status/${batchJobId}`);
        const data = await response.json();
        
        if (data.success) {
          const status = data.status;
          setProcessingStatus(`Processing: ${status.completed}/${status.total} completed`);
          
          if (status.state === 'completed') {
            // Get final results
            const resultsResponse = await fetch(`${API_BASE_URL}/batch/results/${batchJobId}`);
            const resultsData = await resultsResponse.json();
            
            if (resultsData.success) {
              setResults(resultsData.results);
              setProcessingStatus('Processing complete! 🎉');
            }
            setIsProcessing(false);
            return;
          } else if (status.state === 'failed') {
            throw new Error('Batch processing failed');
          }
        }
        
        // Continue polling if not complete and under max attempts
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000); // Poll every 2 seconds
        } else {
          throw new Error('Processing timeout - please try again');
        }
             } catch (error) {
         console.error('Error polling results:', error);
         setError(error.message);
         setProcessingStatus('');
         setIsProcessing(false);
       }
    };

    // Start polling
    setTimeout(poll, 2000);
  };

  // Feature flag check - redirect if testing is disabled
  if (process.env.ENABLE_TESTING_SUITE !== 'true') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Testing Suite Not Available</h1>
          <p className="text-gray-600 mb-6">Testing features are currently disabled. Enable with ENABLE_TESTING_SUITE=true.</p>
          <button
            onClick={() => window.location.href = '/'}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
          >
            Go to Main App
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 scroll-optimized">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-light border-b border-gray-200 sticky top-0 z-50 sticky-optimized">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
                  </svg>
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Apply.AI Testing
                  </h1>
                  <p className="text-sm text-gray-600">Development Mode - AI Tailoring Test Suite</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => window.location.href = '/'}
                className="text-gray-600 hover:text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                ← Back to Main App
              </button>
              <button
                onClick={testBackendConnection}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors mr-2"
              >
                Test Connection
              </button>
              <button
                onClick={clearAll}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Clear All
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
            <button
              onClick={() => setActiveTab('resume')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'resume'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Resume Testing
            </button>
            <button
              onClick={() => setActiveTab('subscription')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'subscription'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Subscription Testing
            </button>
          </div>
        </div>

        {activeTab === 'subscription' ? (
          <SubscriptionTestPage />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Testing Controls */}
          <div className="lg:col-span-2 space-y-6">
            {/* Testing Mode Selector */}
            <div className="bg-white/80 backdrop-blur-light rounded-xl p-6 border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Testing Mode</h2>
              <div className="flex space-x-4 mb-4">
                <button
                  onClick={() => setTestingMode('manual')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    testingMode === 'manual' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  }`}
                >
                  Manual Testing
                </button>
                <button
                  onClick={() => setTestingMode('scenario')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    testingMode === 'scenario' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  }`}
                >
                  Scenario Testing
                </button>
              </div>

              {testingMode === 'manual' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Load Test Resume
                    </label>
                    <select
                      value={selectedTestResume}
                      onChange={(e) => loadTestResume(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Select a test resume...</option>
                      {testResumes.map(resume => (
                        <option key={resume.id} value={resume.id}>
                          {resume.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Load Job URLs
                    </label>
                    <select
                      value={selectedJobCategory}
                      onChange={(e) => loadJobUrls(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Select job category...</option>
                      {Object.keys(jobUrlCollections).map(category => (
                        <option key={category} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {testingMode === 'scenario' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Load Test Scenario
                  </label>
                  <select
                    value={selectedTestScenario}
                    onChange={(e) => loadTestScenario(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a test scenario...</option>
                    {testScenarios.map(scenario => (
                      <option key={scenario.id} value={scenario.id}>
                        {scenario.name}
                      </option>
                    ))}
                  </select>
                  {selectedTestScenario && (
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-gray-700">
                        {testScenarios.find(s => s.id === selectedTestScenario)?.description}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* File Upload */}
            <FileUpload onFileSelect={setFile} selectedFile={file} />

            {/* Job URLs Input */}
            <JobUrlsInput
              jobUrls={jobUrls}
              onJobUrlsChange={setJobUrls}
            />

            {/* Cover Letter Options */}
            <CoverLetter
              enabled={coverLetterEnabled}
              onEnabledChange={setCoverLetterEnabled}
              options={coverLetterOptions}
              onOptionsChange={setCoverLetterOptions}
            />

            {/* Optional Sections */}
            <OptionalSections
              options={optionalSections}
              onOptionsChange={setOptionalSections}
            />

            {/* Output Settings */}
            <OutputSettings
              settings={outputSettings}
              onSettingsChange={setOutputSettings}
            />

            {/* Advanced Testing Utilities */}
            <TestingUtils
              onRunBatchTest={handleTailorApplication}
              onRunPerformanceTest={handleTailorApplication}
            />
          </div>

          {/* Right Column - Actions & Results */}
          <div className="lg:col-span-1 space-y-6">
            {/* Action Panel */}
            <div className="bg-white/80 backdrop-blur-light rounded-xl p-6 border border-gray-200 sticky top-24 sticky-optimized">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Testing Actions</h2>
              
              {/* Current Test Status */}
              {(selectedTestResume || selectedTestScenario) && (
                <div className="mb-4 p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-700 font-medium">
                    {testingMode === 'scenario' 
                      ? `Scenario: ${testScenarios.find(s => s.id === selectedTestScenario)?.name}`
                      : `Resume: ${testResumes.find(r => r.id === selectedTestResume)?.name}`
                    }
                  </p>
                  {selectedJobCategory && (
                    <p className="text-sm text-green-600">
                      Category: {selectedJobCategory}
                    </p>
                  )}
                </div>
              )}

              {/* Connection Status */}
              {connectionStatus && (
                <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center">
                    <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <p className="text-sm text-green-700 font-medium">{connectionStatus}</p>
                  </div>
                </div>
              )}

              {/* Processing Status */}
              {isProcessing && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mb-2"></div>
                  <p className="text-sm text-blue-700">{processingStatus}</p>
                </div>
              )}

              {/* Error Display */}
              {error && (
                <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center">
                    <svg className="w-4 h-4 text-red-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <p className="text-sm text-red-700 font-medium">Error:</p>
                  </div>
                  <p className="text-sm text-red-600 mt-1">{error}</p>
                  <button
                    onClick={() => setError('')}
                    className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
                  >
                    Dismiss
                  </button>
                </div>
              )}

              {/* Main Action Button */}
              <button
                onClick={handleTailorApplication}
                disabled={isProcessing || !file || jobUrls.trim().split('\n').filter(url => url.trim()).length === 0}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white py-3 px-6 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed"
              >
                {isProcessing ? 'Processing...' : 'Test AI Tailoring'}
              </button>

              {/* Quick Actions */}
              <div className="mt-4 grid grid-cols-2 gap-2">
                <button
                  onClick={() => loadTestResume('entry_level_swe')}
                  className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-3 rounded-lg transition-colors"
                >
                  Quick: Entry SWE
                </button>
                <button
                  onClick={() => loadJobUrls('Software Engineering')}
                  className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-3 rounded-lg transition-colors"
                >
                  Quick: SWE Jobs
                </button>
                <button
                  onClick={() => loadTestScenario('entry_level_swe_big_tech')}
                  className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-3 rounded-lg transition-colors col-span-2"
                >
                  Quick: Full Scenario
                </button>
              </div>
            </div>

            {/* Results */}
            {results.length > 0 && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-800">Test Results</h2>
                {results.map((result, index) => (
                  <ResultCard
                    key={index}
                    result={result}
                    coverLetterEnabled={coverLetterEnabled}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
        )}
      </div>
    </div>
  );
} 