/**
 * SimplifiedPrecisionMode Component
 * A simplified version of the precision mode interface that works with existing state management
 * Task 15.1: Integration component for precision processing
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Target,
  Settings,
  Clock,
  CheckCircle,
  AlertCircle,
  Play,
  Download,
  BarChart3,
  TrendingUp,
  ArrowLeft,
  RefreshCw,
  FileText,
  Eye,
  Upload,
  Link as LinkIcon,
  Crown,
  Star,
  Zap
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './ui/card';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

function ATSScorePreview({ score = 0, improvements = [] }) {
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Improvement';
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Real-time ATS Score Preview
        </CardTitle>
        <CardDescription>
          Live analysis of your resume's compatibility with this job
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="text-center">
            <div className={`text-4xl font-bold ${getScoreColor(score)}`}>
              {score}/100
            </div>
            <div className={`text-lg font-medium ${getScoreColor(score)}`}>
              {getScoreLabel(score)}
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>ATS Compatibility</span>
              <span>{score}%</span>
            </div>
            <Progress value={score} className="w-full" />
          </div>

          {improvements.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Suggested Improvements:</h4>
              <div className="space-y-2">
                {improvements.slice(0, 3).map((improvement, index) => (
                  <div key={index} className="flex items-start gap-2 text-sm">
                    <TrendingUp className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{improvement}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function JobSpecificCustomization({ settings, onSettingsChange, disabled = false }) {
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
          Job-Specific Customization
        </CardTitle>
        <CardDescription>
          Fine-tune your resume for this specific role
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="enhancement" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="enhancement">Enhancement</TabsTrigger>
            <TabsTrigger value="keywords">Keywords</TabsTrigger>
            <TabsTrigger value="sections">Sections</TabsTrigger>
          </TabsList>
          
          <TabsContent value="enhancement" className="space-y-4">
            <div>
              <Label htmlFor="enhancement-level">Enhancement Level</Label>
              <select
                id="enhancement-level"
                value={localSettings.enhancementLevel || 'moderate'}
                onChange={(e) => handleSettingChange('enhancementLevel', e.target.value)}
                disabled={disabled}
                className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="light">Light - Minimal changes</option>
                <option value="moderate">Moderate - Balanced optimization</option>
                <option value="aggressive">Aggressive - Maximum enhancement</option>
              </select>
            </div>

            <div>
              <Label htmlFor="tone">Tone & Style</Label>
              <select
                id="tone"
                value={localSettings.tone || 'professional'}
                onChange={(e) => handleSettingChange('tone', e.target.value)}
                disabled={disabled}
                className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="professional">Professional</option>
                <option value="conversational">Conversational</option>
                <option value="confident">Confident</option>
                <option value="analytical">Analytical</option>
                <option value="creative">Creative</option>
              </select>
            </div>
          </TabsContent>

          <TabsContent value="keywords" className="space-y-4">
            <div>
              <Label htmlFor="target-keywords">Target Keywords</Label>
              <Textarea
                id="target-keywords"
                value={localSettings.targetKeywords || ''}
                onChange={(e) => handleSettingChange('targetKeywords', e.target.value)}
                disabled={disabled}
                placeholder="Enter specific keywords to emphasize (comma-separated)"
                rows={3}
                className="mt-1"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={localSettings.optimizeKeywords || false}
                  onChange={(e) => handleSettingChange('optimizeKeywords', e.target.checked)}
                  disabled={disabled}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">Auto-optimize keywords</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={localSettings.keywordDensity || false}
                  onChange={(e) => handleSettingChange('keywordDensity', e.target.checked)}
                  disabled={disabled}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">Optimize keyword density</span>
              </label>
            </div>
          </TabsContent>

          <TabsContent value="sections" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={localSettings.includeSummary || false}
                  onChange={(e) => handleSettingChange('includeSummary', e.target.checked)}
                  disabled={disabled}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">Professional Summary</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={localSettings.includeSkills || false}
                  onChange={(e) => handleSettingChange('includeSkills', e.target.checked)}
                  disabled={disabled}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">Skills Section</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={localSettings.includeCoverLetter || false}
                  onChange={(e) => handleSettingChange('includeCoverLetter', e.target.checked)}
                  disabled={disabled}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">Cover Letter</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={localSettings.includeEducation || false}
                  onChange={(e) => handleSettingChange('includeEducation', e.target.checked)}
                  disabled={disabled}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">Education Details</span>
              </label>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

function ProcessingResult({ result, onDownload, onViewDetails }) {
  if (!result) return null;

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CheckCircle className="h-5 w-5 text-green-600" />
          Processing Complete
        </CardTitle>
        <CardDescription>
          Your tailored resume is ready for {result.job_title || 'this position'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {result.ats_score || 85}
              </div>
              <div className="text-sm text-gray-600">ATS Score</div>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {result.keyword_matches || 12}
              </div>
              <div className="text-sm text-gray-600">Keywords Matched</div>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {result.improvements || 8}
              </div>
              <div className="text-sm text-gray-600">Improvements Made</div>
            </div>
          </div>

          <div className="flex gap-3">
            <Button onClick={onDownload} className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Download Resume
            </Button>
            <Button variant="outline" onClick={onViewDetails} className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              View Details
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function SimplifiedPrecisionMode({
  resumeData,
  jobUrls = [],
  onProcessingStart,
  onProcessingComplete,
  onBackToModeSelection,
  processing = false,
  error = '',
  success = ''
}) {
  const [settings, setSettings] = useState({
    enhancementLevel: 'moderate',
    tone: 'professional',
    targetKeywords: '',
    optimizeKeywords: true,
    keywordDensity: false,
    includeSummary: true,
    includeSkills: true,
    includeCoverLetter: false,
    includeEducation: false
  });

  const [currentJobUrl, setCurrentJobUrl] = useState(jobUrls[0] || '');
  const [localResumeText, setLocalResumeText] = useState(resumeData.text || '');
  const [localFile, setLocalFile] = useState(resumeData.file);
  
  const [atsScore, setAtsScore] = useState(0);
  const [improvements, setImprovements] = useState([]);
  const [result, setResult] = useState(null);
  const [processingProgress, setProcessingProgress] = useState(0);

  const canProcess = (localResumeText || localFile) && currentJobUrl.trim().length > 0;

  const handleFileUpload = useCallback((event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setLocalFile(selectedFile);
      setLocalResumeText(''); // Clear text input when file is selected
    }
  }, []);

  // Simulate real-time ATS score updates
  useEffect(() => {
    if (currentJobUrl && (localResumeText || localFile)) {
      // Simulate analysis
      const timer = setTimeout(() => {
        setAtsScore(Math.floor(Math.random() * 40) + 60); // 60-100 range
        setImprovements([
          'Add more industry-specific keywords',
          'Strengthen action verbs in experience section',
          'Include quantifiable achievements',
          'Optimize skills section for ATS parsing'
        ]);
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [currentJobUrl, localResumeText, localFile]);

  const handleStartProcessing = async () => {
    if (!canProcess) return;

    setProcessingProgress(0);
    setResult(null);

    // Simulate processing progress
    const progressInterval = setInterval(() => {
      setProcessingProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          // Simulate completion
          setResult({
            job_title: 'Software Engineer',
            ats_score: 92,
            keyword_matches: 15,
            improvements: 12,
            tailored_resume: 'Tailored resume content...'
          });
          if (onProcessingComplete) {
            onProcessingComplete([{
              job_title: 'Software Engineer',
              ats_score: 92,
              tailored_resume: 'Tailored resume content...'
            }]);
          }
          return 100;
        }
        return prev + 10;
      });
    }, 500);

    const processData = {
      resume_text: localResumeText,
      resume_file: localFile,
      job_url: currentJobUrl,
      settings
    };

    if (onProcessingStart) {
      await onProcessingStart(processData);
    }
  };

  const handleDownload = () => {
    // Implementation would download the result
    console.log('Download result:', result);
  };

  const handleViewDetails = () => {
    // Implementation would show detailed view
    console.log('View details:', result);
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
          <div className="flex items-center gap-2 text-purple-600">
            <Crown className="h-4 w-4" />
            <span className="text-sm font-medium">Pro Feature</span>
          </div>
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Precision Mode</h1>
        <p className="text-lg text-gray-600">
          Fine-tune your resume with job-specific optimizations and real-time feedback
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

          {/* Job URL Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LinkIcon className="h-5 w-5" />
                Target Job
              </CardTitle>
              <CardDescription>
                Enter the job posting URL for precise optimization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div>
                <Label htmlFor="job-url">Job Posting URL</Label>
                <input
                  id="job-url"
                  type="url"
                  value={currentJobUrl}
                  onChange={(e) => setCurrentJobUrl(e.target.value)}
                  disabled={processing}
                  placeholder="https://example.com/job-posting"
                  className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </CardContent>
          </Card>

          {/* ATS Score Preview */}
          {atsScore > 0 && (
            <ATSScorePreview score={atsScore} improvements={improvements} />
          )}

          {/* Job-Specific Customization */}
          <JobSpecificCustomization
            settings={settings}
            onSettingsChange={setSettings}
            disabled={processing}
          />

          {/* Processing Progress */}
          {processing && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <RefreshCw className="h-5 w-5 animate-spin" />
                  Processing Your Resume
                </CardTitle>
                <CardDescription>
                  Applying job-specific optimizations...
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{processingProgress}%</span>
                  </div>
                  <Progress value={processingProgress} className="w-full" />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Processing Result */}
          <ProcessingResult
            result={result}
            onDownload={handleDownload}
            onViewDetails={handleViewDetails}
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
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {processing ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Target className="mr-2 h-4 w-4" />
                    Start Precision Processing
                  </>
                )}
              </Button>

              {!canProcess && (
                <p className="text-sm text-gray-500">
                  Please provide resume content and a job URL to start processing.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Processing Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Processing Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Current ATS Score:</span>
                <span className="font-medium">{atsScore}/100</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Enhancement Level:</span>
                <span className="font-medium capitalize">{settings.enhancementLevel}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Tone:</span>
                <span className="font-medium capitalize">{settings.tone}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Estimated time:</span>
                <span className="font-medium">2-3 minutes</span>
              </div>
            </CardContent>
          </Card>

          {/* Pro Features */}
          <Card className="border-purple-200 bg-purple-50/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-purple-700">
                <Crown className="h-5 w-5" />
                Pro Features Active
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-purple-700">
                <Star className="h-4 w-4" />
                Real-time ATS score preview
              </div>
              <div className="flex items-center gap-2 text-sm text-purple-700">
                <Star className="h-4 w-4" />
                Advanced keyword optimization
              </div>
              <div className="flex items-center gap-2 text-sm text-purple-700">
                <Star className="h-4 w-4" />
                Job-specific customization
              </div>
              <div className="flex items-center gap-2 text-sm text-purple-700">
                <Star className="h-4 w-4" />
                Detailed analytics dashboard
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

        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800"
          >
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              {success}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
