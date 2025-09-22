import React, { useState } from 'react';
import { API_BASE_URL } from '../utils/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { 
  Download, 
  Target, 
  Info, 
  CheckCircle, 
  XCircle, 
  TrendingUp,
  Award,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  FileText,
  FileType,
  Archive,
  Sparkles
} from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';

const EnhancedBatchResults = ({ results, onDownloadAll, onDownloadIndividual, batchId }) => {
  const [expandedResults, setExpandedResults] = useState({});
  
  const isCompleted = (r) => {
    const s = (r?.status || '').toString().toLowerCase();
    const hasPdf = !!(r?.formatted_resume_data?.download_url || r?.formatted_resume_data?.has_binary_content);
    const hasText = typeof r?.tailored_resume === 'string' && r.tailored_resume.trim().length > 0;
    return s.startsWith('complete') || hasPdf || hasText;
  };

  const failedResults = results.filter(r => (r?.status || '').toString().toLowerCase() === 'failed' || (!!r?.error && !isCompleted(r)));
  const completedResults = results.filter(isCompleted);
  const completedCount = completedResults.length;
  const successRate = results.length > 0 ? Math.round((completedCount / results.length) * 100) : 0;

  const downloadFormats = [
    { key: 'pdf', label: 'PDF', icon: <FileText className="h-4 w-4" />, color: 'purple' },
    { key: 'docx', label: 'Word', icon: <FileType className="h-4 w-4" />, color: 'blue' },
    { key: 'txt', label: 'Text', icon: <FileText className="h-4 w-4" />, color: 'gray' }
  ];

  const toggleExpanded = (index) => {
    setExpandedResults(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const getATSScoreColor = (score) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getATSGradeInfo = (grade) => {
    const gradeMap = {
      'A+': { color: 'bg-green-500', description: 'Excellent match! Your resume is highly optimized.' },
      'A': { color: 'bg-green-400', description: 'Great match! Strong keyword alignment.' },
      'A-': { color: 'bg-green-300', description: 'Very strong match. Minor improvements possible.' },
      'B+': { color: 'bg-blue-500', description: 'Good match! Nearly there.' },
      'B': { color: 'bg-blue-400', description: 'Good match! Room for minor improvements.' },
      'B-': { color: 'bg-blue-300', description: 'Decent match. Add a few more relevant keywords.' },
      'C+': { color: 'bg-yellow-500', description: 'Fair match. Consider adding more relevant keywords.' },
      'C': { color: 'bg-yellow-400', description: 'Fair match. Consider adding more relevant keywords.' },
      'C-': { color: 'bg-yellow-300', description: 'Weak match. Significant improvements needed.' },
      'D': { color: 'bg-orange-400', description: 'Weak match. Significant improvements needed.' },
      'F': { color: 'bg-red-400', description: 'Poor match. Major revisions recommended.' }
    };
    return gradeMap[grade] || { color: 'bg-gray-400', description: 'Analyzing' };
  };

  const getConfidenceBadge = (level) => {
    const badges = {
      'HIGH': { icon: <CheckCircle className="h-4 w-4" />, color: 'bg-green-100 text-green-700', label: 'High Confidence' },
      'GOOD': { icon: <TrendingUp className="h-4 w-4" />, color: 'bg-blue-100 text-blue-700', label: 'Good Match' },
      'MODERATE': { icon: <AlertCircle className="h-4 w-4" />, color: 'bg-yellow-100 text-yellow-700', label: 'Moderate Match' },
      'LOW': { icon: <XCircle className="h-4 w-4" />, color: 'bg-red-100 text-red-700', label: 'Low Match' }
    };
    return badges[level] || badges['MODERATE'];
  };

  return (
    <TooltipProvider>
      <Card className="mb-6 shadow-lg border-0">
        <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-t-lg">
          <CardTitle className="flex items-center gap-2 text-xl">
            <Target className="h-6 w-6 text-purple-600" />
            Batch Processing Results
          </CardTitle>
          <CardDescription className="text-gray-700 mt-2">
            <span className="font-semibold text-lg">
              {completedCount} of {results.length} resumes generated
            </span>
          </CardDescription>
          <div className="mt-1">
            <Badge variant={successRate === 100 ? 'success' : successRate >= 50 ? 'warning' : 'destructive'}>
              {successRate}% Success Rate
            </Badge>
          </div>
        </CardHeader>
        
        <CardContent className="pt-6">
          <div className="space-y-6">
            {/* Bulk Download Section */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Download className="h-5 w-5" />
                  Bulk Download Options
                </h4>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="h-4 w-4 text-gray-400" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Download all generated resumes in your preferred format</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              
              <div className="flex flex-wrap gap-3">
                {downloadFormats.map(format => {
                  const button = (
                    <Button 
                      key={format.key}
                      onClick={() => {
                        console.log('🔽 Download button clicked:', format.key, 'Results count:', completedResults.length)
                        onDownloadAll(completedResults, format.key)
                      }} 
                      className="flex items-center gap-2"
                      variant={format.key === 'pdf' ? 'default' : 'outline'}
                    >
                      {format.icon}
                      <span>{format.label} Format</span>
                      <Badge variant="secondary" className="ml-1">
                        {completedResults.length}
                      </Badge>
                    </Button>
                  )
                  if (format.key === 'pdf' && batchId) {
                    return (
                      <a key={`bulk-${format.key}`} href={`${API_BASE_URL}/api/enhanced-batch/download-all/${batchId}`}>{button}</a>
                    )
                  }
                  return button
                })}
              </div>
            </div>

            {/* Failure Notices Section */}
            {failedResults.length > 0 && (
              <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                <h4 className="font-semibold text-red-800 mb-2 flex items-center gap-2">
                  <AlertCircle className="h-5 w-5" />
                  Some jobs could not be scraped
                </h4>
                <ul className="list-disc pl-5 text-sm text-red-800 space-y-1">
                  {failedResults.slice(0, 5).map((r, idx) => (
                    <li key={idx}>
                      <span className="font-medium">{r.job_title || `Job ${r.job_index + 1 || idx + 1}`}:</span> {r.error || 'Unable to extract job description. Please paste it manually.'}
                    </li>
                  ))}
                </ul>
                <p className="text-xs text-red-700 mt-2">Tip: If a posting is gated or script-rendered, paste the full job description manually.</p>
              </div>
            )}

            {/* Individual Results Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-semibold text-gray-900">Individual Resume Analysis</h4>
                <Badge variant="outline" className="gap-1">
                  <Sparkles className="h-3 w-3" />
                  AI-Powered Analysis
                </Badge>
              </div>
              
              <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                {completedResults.map((result, index) => {
                  const gradeInfo = getATSGradeInfo(result.ats_grade);
                  const confidenceBadge = getConfidenceBadge(result.confidence_level);
                  const isExpanded = expandedResults[index];
                  
                  return (
                    <Card key={`result-${index}`} className="border shadow-sm hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        {/* Main Result Header */}
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h5 className="font-semibold text-gray-900">
                                {result.job_title || `Position ${index + 1}`}
                              </h5>
                              {result.company && (
                                <span className="text-sm text-gray-500">at {result.company}</span>
                              )}
                            </div>
                            
                            {/* ATS Score Display */}
                            <div className="flex items-center gap-4 mb-3">
                              {/* Score Circle */}
                              <div className="relative">
                                <div className={`w-16 h-16 rounded-full border-4 ${gradeInfo.color} border-opacity-30 flex items-center justify-center`}>
                                  <div className="text-center">
                                    <div className="text-lg font-bold">{result.ats_grade || 'N/A'}</div>
                                    <div className={`text-xs font-semibold ${getATSScoreColor(result.ats_score)}`}>
                                      {result.ats_score !== 'N/A' ? `${result.ats_score}%` : 'Analyzing'}
                                    </div>
                                  </div>
                                </div>
                              </div>
                              
                              {/* Score Details */}
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <Tooltip>
                                    <TooltipTrigger>
                                      <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${confidenceBadge.color}`}>
                                        {confidenceBadge.icon}
                                        <span>{confidenceBadge.label}</span>
                                      </div>
                                    </TooltipTrigger>
                                    <TooltipContent>
                                      <p>{result.confidence_message || 'Analysis confidence level'}</p>
                                    </TooltipContent>
                                  </Tooltip>
                                  
                                  <Tooltip>
                                    <TooltipTrigger>
                                      <Badge variant="outline" className="text-xs">
                                        {result.keyword_matches || 0} keywords matched
                                      </Badge>
                                    </TooltipTrigger>
                                    <TooltipContent>
                                      <p>{result.keyword_match_percentage || 0}% of important keywords found</p>
                                    </TooltipContent>
                                  </Tooltip>
                                </div>
                                
                                <p className="text-sm text-gray-600">{gradeInfo.description}</p>
                              </div>
                            </div>
                            
                            {/* Expandable Details Section */}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleExpanded(index)}
                              className="text-purple-600 hover:text-purple-700 p-0 h-auto font-medium"
                            >
                              {isExpanded ? (
                                <>Hide Details <ChevronUp className="h-4 w-4 ml-1" /></>
                              ) : (
                                <>View Skill Analysis <ChevronDown className="h-4 w-4 ml-1" /></>
                              )}
                            </Button>
                            
                            {/* Expanded Details */}
                            {isExpanded && result.ats_details && (
                              <div className="mt-4 space-y-3 border-t pt-4">
                                {/* Keywords Matched */}
                                {result.ats_details.matched_skills && result.ats_details.matched_skills.length > 0 && (
                                  <div>
                                    <h6 className="text-sm font-semibold text-green-700 mb-2 flex items-center gap-1">
                                      <CheckCircle className="h-4 w-4" />
                                      Keywords Matched ({result.ats_details.matched_skills.length})
                                    </h6>
                                    <div className="flex flex-wrap gap-1">
                                      {result.ats_details.matched_skills.map((skill, idx) => (
                                        <Badge key={idx} variant="success" className="text-xs">
                                          {skill}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                
                                {/* Keywords to add */}
                                {result.ats_details.missing_skills && result.ats_details.missing_skills.length > 0 && (
                                  <div>
                                    <h6 className="text-sm font-semibold text-orange-700 mb-2 flex items-center gap-1">
                                      <AlertCircle className="h-4 w-4" />
                                      Keywords to add ({result.ats_details.missing_skills.length})
                                    </h6>
                                    <div className="flex flex-wrap gap-1">
                                      {result.ats_details.missing_skills.map((skill, idx) => (
                                        <Badge key={idx} variant="outline" className="text-xs border-orange-300 text-orange-700">
                                          {skill}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                
                                {/* Component Scores */}
                                {result.ats_details.component_scores && (
                                  <div>
                                    <h6 className="text-sm font-semibold text-gray-700 mb-2">Score Breakdown</h6>
                                    <div className="space-y-2">
                                      {Object.entries(result.ats_details.component_scores).map(([key, value]) => (
                                        <div key={key} className="flex items-center gap-2">
                                          <span className="text-xs text-gray-600 capitalize w-32">
                                            {key.replace(/_/g, ' ')}:
                                          </span>
                                          <Progress value={value} className="flex-1 h-2" />
                                          <span className="text-xs font-semibold text-gray-700 w-10">
                                            {value}%
                                          </span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                
                                {/* Recommendations */}
                                {result.ats_details.recommendations && result.ats_details.recommendations.length > 0 && (
                                  <div>
                                    <h6 className="text-sm font-semibold text-blue-700 mb-2 flex items-center gap-1">
                                      <Info className="h-4 w-4" />
                                      Recommendations
                                    </h6>
                                    <ul className="text-xs text-gray-600 space-y-1">
                                      {result.ats_details.recommendations.map((rec, idx) => (
                                        <li key={idx} className="flex items-start gap-1">
                                          <span className="text-blue-500 mt-0.5">•</span>
                                          <span>{rec}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                          
                          {/* Download Buttons */}
                          <div className="flex gap-2 ml-4">
                            {downloadFormats.map(format => {
                              const btn = (
                                <Button
                                  key={format.key}
                                  variant={format.key === 'pdf' ? 'default' : 'outline'}
                                  size="sm"
                                  onClick={() => onDownloadIndividual(result, format.key)}
                                  className="h-9 w-9 p-0"
                                >
                                  {format.icon}
                                </Button>
                              )
                              if (format.key === 'pdf') {
                                const directUrl = result?.formatted_resume_data?.download_url
                                  || (batchId && result?.formatted_resume_data?.filename
                                        ? `/api/enhanced-batch/download/${batchId}/${result.formatted_resume_data.filename}`
                                        : null);
                                if (directUrl) {
                                  return (
                                    <Tooltip key={`pdf-${index}`}>
                                      <TooltipTrigger asChild>
                                        <a href={`${API_BASE_URL}${directUrl}`}>
                                          <span className="sr-only">PDF</span>
                                          {btn}
                                        </a>
                                      </TooltipTrigger>
                                      <TooltipContent>
                                        <p>Download as PDF</p>
                                      </TooltipContent>
                                    </Tooltip>
                                  )
                                }
                              }
                              return (
                                <Tooltip key={format.key}>
                                  <TooltipTrigger>{btn}</TooltipTrigger>
                                  <TooltipContent>
                                    <p>Download as {format.label}</p>
                                  </TooltipContent>
                                </Tooltip>
                              )
                            })}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  );
};

export default EnhancedBatchResults;
