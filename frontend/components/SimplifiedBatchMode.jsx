/**
 * SimplifiedBatchMode Component
 * A simplified version of the batch mode interface that works with existing state management
 * Task 15.1: Integration component for batch processing
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import TemplateSelector from './TemplateSelector';
import ATSScoreDisplay from './ATSScoreDisplay';
import EnhancedBatchResults from './EnhancedBatchResults';
import { 
  Upload,
  FileText,
  Settings,
  Clock,
  CheckCircle,
  AlertCircle,
  Play,
  Pause,
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

function GlobalSettings({ settings, onSettingsChange, disabled = false }) {
  const [localSettings, setLocalSettings] = useState(settings);

  const handleSettingChange = (key, value) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    onSettingsChange(newSettings);
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Global Enhancement Settings
        </CardTitle>
        <CardDescription>
          These settings will be applied to all jobs in your batch
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="enhancement-level">Enhancement Level</Label>
          <select
            id="enhancement-level"
            value={localSettings.enhancementLevel || 'moderate'}
            onChange={(e) => handleSettingChange('enhancementLevel', e.target.value)}
            disabled={disabled}
            className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="light">Light - Quick improvements</option>
            <option value="moderate">Moderate - Balanced optimization</option>
            <option value="aggressive">Aggressive - Maximum enhancement</option>
          </select>
        </div>

        {/* Template Selection */}
        <TemplateSelector
          selectedTemplate={localSettings.template}
          onTemplateChange={(template) => handleSettingChange('template', template)}
          isPro={true} // TODO: Connect to actual subscription status
        />

        <div className="grid grid-cols-2 gap-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={localSettings.includeSummary || false}
              onChange={(e) => handleSettingChange('includeSummary', e.target.checked)}
              disabled={disabled}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Include Summary</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={localSettings.includeSkills || false}
              onChange={(e) => handleSettingChange('includeSkills', e.target.checked)}
              disabled={disabled}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Enhance Skills</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={localSettings.includeCoverLetter || false}
              onChange={(e) => handleSettingChange('includeCoverLetter', e.target.checked)}
              disabled={disabled}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Generate Cover Letter</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={localSettings.optimizeKeywords || false}
              onChange={(e) => handleSettingChange('optimizeKeywords', e.target.checked)}
              disabled={disabled}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Optimize Keywords</span>
          </label>
        </div>
      </CardContent>
    </Card>
  );
}

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
    enhancementLevel: 'moderate',
    includeSummary: false,
    includeSkills: true,
    includeCoverLetter: false,
    optimizeKeywords: true,
    template: 'modern',
    outputFormat: 'pdf',
    tailoringMode: 'light'
  });

  const [localJobUrls, setLocalJobUrls] = useState(jobUrls.join('\n'));
  const [localResumeText, setLocalResumeText] = useState(resumeData.text || '');
  const [localFile, setLocalFile] = useState(resumeData.file);
  
  const [processingJobs, setProcessingJobs] = useState([]);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(0);

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
          Process multiple job applications quickly with global settings
        </p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-8">
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
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LinkIcon className="h-5 w-5" />
                Job URLs
              </CardTitle>
              <CardDescription>
                Enter job URLs (one per line, up to 10 jobs)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                value={localJobUrls}
                onChange={(e) => setLocalJobUrls(e.target.value)}
                disabled={processing}
                placeholder="https://example.com/job1&#10;https://example.com/job2&#10;..."
                rows={6}
                className="font-mono text-sm"
              />
              <p className="text-sm text-gray-500 mt-2">
                {jobUrlList.length} job{jobUrlList.length !== 1 ? 's' : ''} entered
              </p>
            </CardContent>
          </Card>

          {/* Global Settings */}
          <GlobalSettings
            settings={settings}
            onSettingsChange={setSettings}
            disabled={processing}
          />

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
          />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Processing Controls */}
          <Card>
            <CardHeader>
              <CardTitle>Processing Controls</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={handleStartProcessing}
                disabled={!canProcess || processing}
                className="w-full"
              >
                {processing ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Start Batch Processing
                  </>
                )}
              </Button>

              {!canProcess && (
                <p className="text-sm text-gray-500">
                  Please provide resume content and at least one job URL to start processing.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Batch Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Jobs queued:</span>
                <span className="font-medium">{jobUrlList.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Estimated time:</span>
                <span className="font-medium">{Math.ceil(jobUrlList.length * 0.5)} min</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Enhancement level:</span>
                <span className="font-medium capitalize">{settings.enhancementLevel}</span>
              </div>
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
