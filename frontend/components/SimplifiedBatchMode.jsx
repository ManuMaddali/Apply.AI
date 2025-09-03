/**
 * SimplifiedBatchMode Component
 * A simplified version of the batch mode interface that works with existing state management
 * Task 15.1: Integration component for batch processing
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ATSScoreDisplay from './ATSScoreDisplay';
import EnhancedBatchResults from './EnhancedBatchResults';
import { 
  Upload,
  FileText,
  Clock,
  CheckCircle,
  AlertCircle,
  Play,
  Pause,
  Square,
  Download,
  BarChart3,
  TrendingUp,
  ArrowLeft,
  RefreshCw,
  Target,
  Link as LinkIcon
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './ui/card';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Progress } from './ui/progress';



function ProcessingVisualization({ jobs = [], currentProgress = 0, isPaused = false, estimatedTimeRemaining = 0 }) {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Processing Progress
        </CardTitle>
        <CardDescription>
          {jobs.length} jobs • {Math.round(currentProgress)}% complete
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Overall Progress</span>
              <span>{Math.round(currentProgress)}%</span>
            </div>
            <Progress value={currentProgress} className="w-full" />
          </div>

          {estimatedTimeRemaining > 0 && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Clock className="h-4 w-4" />
              <span>Estimated time remaining: {Math.ceil(estimatedTimeRemaining / 60)} minutes</span>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-64 overflow-y-auto">
            {jobs.map((job, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${
                  job.status === 'completed'
                    ? 'bg-green-50 border-green-200'
                    : job.status === 'processing'
                    ? 'bg-blue-50 border-blue-200'
                    : job.status === 'error'
                    ? 'bg-red-50 border-red-200'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-center gap-2">
                  {job.status === 'completed' && <CheckCircle className="h-4 w-4 text-green-600" />}
                  {job.status === 'processing' && <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />}
                  {job.status === 'error' && <AlertCircle className="h-4 w-4 text-red-600" />}
                  {job.status === 'pending' && <Clock className="h-4 w-4 text-gray-400" />}
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {job.title || `Job ${index + 1}`}
                    </p>
                    <p className="text-xs text-gray-500 capitalize">{job.status}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// BatchResults function has been replaced with EnhancedBatchResults component

export default function SimplifiedBatchMode({
  resumeData,
  jobUrls = [],
  onProcessingStart,
  onProcessingComplete,
  onBackToModeSelection,
  processing = false,
  error = '',
  success = '',
  results = [],
  onDownloadAll,
  onDownloadIndividual
}) {
  const [settings, setSettings] = useState({
    format: 'professional',
    outputFormat: 'pdf'
  });

  const [localJobUrls, setLocalJobUrls] = useState(jobUrls.join('\n'));
  const [localResumeText, setLocalResumeText] = useState(resumeData.text || '');
  const [localFile, setLocalFile] = useState(resumeData.file);
  
  const [processingJobs, setProcessingJobs] = useState([]);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  // Parse job URLs
  const jobUrlList = localJobUrls
    .split('\n')
    .map(url => url.trim())
    .filter(url => url.length > 0);

  const canProcess = (localResumeText || localFile) && jobUrlList.length > 0;

  const handleFileUpload = useCallback((event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setLocalFile(selectedFile);
      setLocalResumeText(''); // Clear text input when file is selected
    }
  }, []);

  const handleStartProcessing = async () => {
    if (!canProcess) return;

    const jobs = jobUrlList.map((url, index) => ({
      id: index,
      url,
      title: `Job ${index + 1}`,
      status: 'pending'
    }));

    setProcessingJobs(jobs);
    setCurrentProgress(0);
    setEstimatedTimeRemaining(jobs.length * 30); // 30 seconds per job estimate

    let resumeTextToSend = localResumeText;
    
    // If we have a file but no text, we need to upload the file first to extract text
    if (!resumeTextToSend && localFile) {
      try {
        // Upload file to extract text content
        const token = localStorage.getItem('applyai_token');
        const formData = new FormData();
        formData.append('file', localFile);
        
        const uploadResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/resumes/upload`, {
          method: 'POST',
          body: formData,
          headers: {
            'Authorization': token ? `Bearer ${token}` : ''
          }
        });

        if (!uploadResponse.ok) {
          throw new Error('Failed to upload resume file');
        }

        const uploadData = await uploadResponse.json();
        if (uploadData.success && uploadData.resume_text) {
          resumeTextToSend = uploadData.resume_text;
          // Update local state with extracted text
          setLocalResumeText(uploadData.resume_text);
        } else {
          throw new Error('Failed to extract text from resume file');
        }
      } catch (error) {
        console.error('❌ Error uploading file:', error);
        // Handle error through parent component
        if (onProcessingStart) {
          await onProcessingStart({ error: `Failed to process resume file: ${error.message}` });
        }
        return;
      }
    }

    // Ensure we have resume text before proceeding
    if (!resumeTextToSend) {
      console.error('❌ No resume text available for processing');
      if (onProcessingStart) {
        await onProcessingStart({ error: 'Please provide resume text or upload a resume file' });
      }
      return;
    }

    const processData = {
      resume_text: resumeTextToSend,
      job_urls: jobUrlList,
      settings
    };

    if (onProcessingStart) {
      await onProcessingStart(processData);
    }
  };

  // Local pause/stop handlers to prevent runtime errors and provide basic UX
  const handlePauseProcessing = useCallback(() => {
    setIsPaused(true);
  }, []);

  const handleStopProcessing = useCallback(() => {
    setIsPaused(false);
    setProcessingJobs([]);
    setCurrentProgress(0);
    setEstimatedTimeRemaining(0);
    if (onProcessingComplete) {
      onProcessingComplete([]);
    }
  }, [onProcessingComplete]);



  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <div className="flex items-center gap-4 mb-4">
          <Button
            variant="ghost"
            onClick={onBackToModeSelection}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Mode Selection
          </Button>
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Batch Processing Mode</h1>
        <p className="text-lg text-gray-600">
          Generate professional resumes for multiple job applications using our standardized format
        </p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Resume Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Resume Input
              </CardTitle>
              <CardDescription>
                Upload your resume file or paste the text content
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="resume-file">Upload Resume File</Label>
                <input
                  id="resume-file"
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileUpload}
                  disabled={processing}
                  className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                {localFile && (
                  <p className="text-sm text-green-600 mt-1">
                    File selected: {localFile.name}
                  </p>
                )}
              </div>

              <div className="text-center text-gray-500">or</div>

              <div>
                <Label htmlFor="resume-text">Paste Resume Text</Label>
                <Textarea
                  id="resume-text"
                  value={localResumeText}
                  onChange={(e) => setLocalResumeText(e.target.value)}
                  disabled={processing}
                  placeholder="Paste your resume content here..."
                  rows={8}
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>

          {/* Job URLs Input */}
          <Card className="shadow-sm">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <LinkIcon className="h-5 w-5 text-blue-600" />
                Job URLs
              </CardTitle>
              <CardDescription className="text-gray-600">
                Enter job URLs (one per line, up to 10 jobs). Each job will be processed with our standardized professional resume format.
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-0">
              <Textarea
                value={localJobUrls}
                onChange={(e) => setLocalJobUrls(e.target.value)}
                disabled={processing}
                placeholder="https://linkedin.com/jobs/job1&#10;https://indeed.com/viewjob?jk=job2&#10;https://company.com/careers/job3"
                rows={8}
                className="font-mono text-sm resize-none border-gray-300 focus:border-blue-500 focus:ring-blue-500"
              />
              <div className="flex items-center justify-between mt-3">
                <p className="text-sm text-gray-500">
                  {jobUrlList.length} job{jobUrlList.length !== 1 ? 's' : ''} entered
                </p>
                {jobUrlList.length > 0 && (
                  <p className="text-xs text-blue-600 font-medium">
                    Ready to process with standardized format
                  </p>
                )}
              </div>
            </CardContent>
          </Card>



          {/* Processing Visualization */}
          {processing && (
            <ProcessingVisualization
              jobs={processingJobs}
              currentProgress={currentProgress}
              estimatedTimeRemaining={estimatedTimeRemaining}
            />
          )}

          {/* Results */}
          <EnhancedBatchResults
            results={results}
            onDownloadAll={onDownloadAll}
            onDownloadIndividual={onDownloadIndividual}
            batchId={settings?.batchId || undefined}
          />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Processing Controls */}
          <Card className="shadow-sm border-gray-200">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg font-semibold">Processing Controls</CardTitle>
              <CardDescription className="text-gray-600">
                Generate professional resumes for all your job applications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 pt-0">
              <Button
                onClick={handleStartProcessing}
                disabled={!canProcess || processing}
                className="w-full h-12 text-base font-medium bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-md"
              >
                {processing ? (
                  <>
                    <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
                    Processing {processingJobs.filter(j => j.status === 'completed').length} of {processingJobs.length}
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-5 w-5" />
                    Start Batch Processing
                  </>
                )}
              </Button>
              
              {processing && (
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    onClick={handlePauseProcessing}
                    disabled={isPaused}
                    variant="outline"
                    size="sm"
                    className="border-gray-300 hover:border-gray-400"
                  >
                    <Pause className="mr-1 h-4 w-4" />
                    Pause
                  </Button>
                  <Button
                    onClick={handleStopProcessing}
                    variant="destructive"
                    size="sm"
                    className="bg-red-500 hover:bg-red-600"
                  >
                    <Square className="mr-1 h-4 w-4" />
                    Stop
                  </Button>
                </div>
              )}

              {!canProcess && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <p className="text-sm text-amber-800">
                    Please provide resume content and at least one job URL to start processing.
                  </p>
                </div>
              )}
              
              {!processing && jobUrlList.length > 0 && canProcess && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-center gap-2 text-green-800">
                    <CheckCircle className="h-4 w-4" />
                    <span className="text-sm font-medium">Ready to process {jobUrlList.length} job{jobUrlList.length !== 1 ? 's' : ''}</span>
                  </div>
                  <p className="text-xs text-green-700 mt-1">
                    Using standardized professional format with consistent bullet points
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">Batch Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 gap-3">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm text-blue-800 font-medium">Jobs queued:</span>
                  <span className="font-bold text-blue-900 text-lg">{jobUrlList.length}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                  <span className="text-sm text-purple-800 font-medium">Estimated time:</span>
                  <span className="font-bold text-purple-900 text-lg">{Math.ceil(jobUrlList.length * 0.5)} min</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-sm text-green-800 font-medium">Format:</span>
                  <span className="font-bold text-green-900">Professional</span>
                </div>
              </div>
              
              {processing && (
                <div className="pt-2 border-t border-gray-200">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Progress:</span>
                    <span className="font-medium">{Math.round(currentProgress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${currentProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Error/Success Messages */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800"
          >
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              {error}
            </div>
          </motion.div>
        )}

        {/* Success message is now handled by BatchResults component */}
      </AnimatePresence>
    </div>
  );
}
