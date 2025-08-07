/**
 * ATSScoringSystem Component
 * Task 11.1: Implement ATS scoring system
 * - Create real-time ATS score calculation and display
 * - Add section-by-section scoring breakdown
 * - Implement confidence level indicators for scores
 * - Create score history tracking and improvement visualization
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  BarChart3,
  Target,
  Award,
  CheckCircle,
  AlertCircle,
  Info,
  Clock,
  Star,
  Brain,
  Zap,
  ArrowUp,
  ArrowDown,
  Minus,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Eye,
  History
} from 'lucide-react';
import { Button } from '../ui/button';
import { EnhancedCard, EnhancedCardHeader, EnhancedCardTitle, EnhancedCardDescription, EnhancedCardContent } from '../ui/enhanced-card';
import { fadeInUp, staggerContainer, staggerItem, scaleIn } from '../../lib/motion';

/**
 * Main ATS Scoring System Component
 */
function ATSScoringSystem({
  resumeData,
  jobData,
  onScoreUpdate,
  realTimeUpdates = true,
  showHistory = true,
  className = ''
}) {
  const [currentScore, setCurrentScore] = useState(null);
  const [scoreHistory, setScoreHistory] = useState([]);
  const [sectionScores, setSectionScores] = useState({});
  const [confidenceLevel, setConfidenceLevel] = useState('medium');
  const [isCalculating, setIsCalculating] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [showBreakdown, setShowBreakdown] = useState(false);

  // Calculate ATS score based on resume and job data
  const calculateATSScore = useCallback(async (resume, job) => {
    setIsCalculating(true);
    
    try {
      // Simulate API call for ATS score calculation
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock calculation logic - in real implementation, this would call backend
      const sectionAnalysis = analyzeSections(resume, job);
      const overallScore = calculateOverallScore(sectionAnalysis);
      const confidence = calculateConfidence(sectionAnalysis, job);
      
      const scoreData = {
        current: overallScore,
        sectionScores: sectionAnalysis,
        confidenceLevel: confidence,
        timestamp: new Date().toISOString(),
        factors: generateScoreFactors(sectionAnalysis)
      };
      
      setCurrentScore(scoreData);
      setSectionScores(sectionAnalysis);
      setConfidenceLevel(confidence);
      setLastUpdated(new Date());
      
      // Add to history
      setScoreHistory(prev => [...prev, {
        score: overallScore,
        timestamp: new Date(),
        sections: sectionAnalysis,
        confidence: confidence
      }].slice(-20)); // Keep last 20 scores
      
      onScoreUpdate?.(scoreData);
      
    } catch (error) {
      console.error('Error calculating ATS score:', error);
    } finally {
      setIsCalculating(false);
    }
  }, [onScoreUpdate]);

  // Mock section analysis function
  const analyzeSections = (resume, job) => {
    const sections = {
      contact: {
        score: 95,
        maxScore: 100,
        weight: 0.1,
        issues: [],
        recommendations: ['Contact information is complete and professional']
      },
      summary: {
        score: resume?.summary ? 75 : 0,
        maxScore: 100,
        weight: 0.2,
        issues: resume?.summary ? [
          { type: 'weak_language', severity: 'minor', description: 'Could use stronger action verbs' }
        ] : [
          { type: 'missing_section', severity: 'critical', description: 'Professional summary is missing' }
        ],
        recommendations: resume?.summary ? 
          ['Add more specific achievements', 'Include relevant keywords'] :
          ['Add a professional summary highlighting your key qualifications']
      },
      experience: {
        score: 82,
        maxScore: 100,
        weight: 0.4,
        issues: [
          { type: 'quantification', severity: 'major', description: 'Missing quantified achievements' },
          { type: 'missing_keywords', severity: 'minor', description: 'Could include more job-relevant keywords' }
        ],
        recommendations: [
          'Add specific metrics and numbers to achievements',
          'Include more technical keywords from job description',
          'Use stronger action verbs'
        ]
      },
      skills: {
        score: resume?.skills ? 88 : 0,
        maxScore: 100,
        weight: 0.15,
        issues: resume?.skills ? [
          { type: 'relevance', severity: 'minor', description: 'Some skills may not be relevant to target role' }
        ] : [
          { type: 'missing_section', severity: 'major', description: 'Skills section is missing' }
        ],
        recommendations: resume?.skills ?
          ['Prioritize skills mentioned in job description', 'Remove outdated or irrelevant skills'] :
          ['Add a skills section with relevant technical and soft skills']
      },
      education: {
        score: 70,
        maxScore: 100,
        weight: 0.1,
        issues: [
          { type: 'formatting', severity: 'minor', description: 'Education formatting could be improved' }
        ],
        recommendations: [
          'Include relevant coursework if applicable',
          'Add graduation date if recent',
          'Highlight academic achievements'
        ]
      },
      achievements: {
        score: resume?.achievements ? 65 : 0,
        maxScore: 100,
        weight: 0.05,
        issues: resume?.achievements ? [
          { type: 'quantification', severity: 'major', description: 'Achievements lack specific metrics' }
        ] : [
          { type: 'missing_section', severity: 'suggestion', description: 'Consider adding achievements section' }
        ],
        recommendations: resume?.achievements ?
          ['Add specific numbers and percentages', 'Focus on business impact'] :
          ['Consider adding notable achievements and awards']
      }
    };

    return sections;
  };

  // Calculate overall score from section scores
  const calculateOverallScore = (sections) => {
    let totalScore = 0;
    let totalWeight = 0;

    Object.values(sections).forEach(section => {
      totalScore += section.score * section.weight;
      totalWeight += section.weight;
    });

    return Math.round(totalScore / totalWeight);
  };

  // Calculate confidence level
  const calculateConfidence = (sections, job) => {
    const hasJobData = job && Object.keys(job).length > 0;
    const completeSections = Object.values(sections).filter(s => s.score > 0).length;
    const totalSections = Object.keys(sections).length;
    
    if (hasJobData && completeSections >= totalSections * 0.8) return 'high';
    if (hasJobData && completeSections >= totalSections * 0.6) return 'medium';
    return 'low';
  };

  // Generate score factors
  const generateScoreFactors = (sections) => {
    const factors = [];
    
    Object.entries(sections).forEach(([sectionName, section]) => {
      if (section.score >= 90) {
        factors.push({
          name: `Strong ${sectionName} section`,
          impact: 5,
          description: `Your ${sectionName} section is well-optimized`,
          category: 'positive'
        });
      } else if (section.score <= 50) {
        factors.push({
          name: `Weak ${sectionName} section`,
          impact: -10,
          description: `Your ${sectionName} section needs improvement`,
          category: 'negative'
        });
      }
    });

    return factors;
  };

  // Real-time updates effect
  useEffect(() => {
    if (realTimeUpdates && resumeData && jobData) {
      calculateATSScore(resumeData, jobData);
    }
  }, [resumeData, jobData, realTimeUpdates, calculateATSScore]);

  // Manual refresh
  const handleRefresh = () => {
    if (resumeData && jobData) {
      calculateATSScore(resumeData, jobData);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-amber-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score) => {
    if (score >= 90) return 'bg-green-50 border-green-200';
    if (score >= 70) return 'bg-blue-50 border-blue-200';
    if (score >= 50) return 'bg-amber-50 border-amber-200';
    return 'bg-red-50 border-red-200';
  };

  const getConfidenceColor = (level) => {
    switch (level) {
      case 'high': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-amber-600 bg-amber-100';
      case 'low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'major': return 'text-orange-600 bg-orange-100';
      case 'minor': return 'text-amber-600 bg-amber-100';
      case 'suggestion': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (!currentScore && !isCalculating) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">ATS Score Analysis</h3>
        <p className="text-gray-600 mb-4">Upload a resume and job description to get your ATS compatibility score</p>
        <Button onClick={handleRefresh} disabled={!resumeData || !jobData}>
          <BarChart3 className="w-4 h-4 mr-2" />
          Calculate ATS Score
        </Button>
      </div>
    );
  }

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Main Score Display */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <div className="flex items-center justify-between">
              <div>
                <EnhancedCardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  ATS Compatibility Score
                  {currentScore && (
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(confidenceLevel)}`}>
                      {confidenceLevel} confidence
                    </div>
                  )}
                </EnhancedCardTitle>
                <EnhancedCardDescription>
                  {lastUpdated ? 
                    `Last updated ${lastUpdated.toLocaleTimeString()}` :
                    'Real-time ATS compatibility analysis'
                  }
                </EnhancedCardDescription>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowBreakdown(!showBreakdown)}
                >
                  <Eye className="w-4 h-4 mr-2" />
                  {showBreakdown ? 'Hide' : 'Show'} Details
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefresh}
                  disabled={isCalculating}
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${isCalculating ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
            </div>
          </EnhancedCardHeader>

          <EnhancedCardContent>
            {isCalculating ? (
              <div className="text-center py-8">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-12 h-12 mx-auto mb-4"
                >
                  <Brain className="w-full h-full text-blue-600" />
                </motion.div>
                <p className="text-gray-600">Analyzing resume compatibility...</p>
              </div>
            ) : currentScore ? (
              <div className="space-y-6">
                {/* Score Circle */}
                <div className="text-center">
                  <div className="relative w-40 h-40 mx-auto">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                      <circle
                        cx="50"
                        cy="50"
                        r="35"
                        stroke="currentColor"
                        strokeWidth="6"
                        fill="none"
                        className="text-gray-200"
                      />
                      <motion.circle
                        cx="50"
                        cy="50"
                        r="35"
                        stroke="currentColor"
                        strokeWidth="6"
                        fill="none"
                        strokeLinecap="round"
                        className={getScoreColor(currentScore.current)}
                        strokeDasharray={`${2 * Math.PI * 35}`}
                        initial={{ strokeDashoffset: 2 * Math.PI * 35 }}
                        animate={{ 
                          strokeDashoffset: 2 * Math.PI * 35 * (1 - currentScore.current / 100) 
                        }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ duration: 0.8, delay: 0.5 }}
                          className={`text-4xl font-bold ${getScoreColor(currentScore.current)}`}
                        >
                          {currentScore.current}
                        </motion.div>
                        <div className="text-sm text-gray-500">/ 100</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {currentScore.current >= 90 ? 'Excellent' :
                       currentScore.current >= 70 ? 'Good' :
                       currentScore.current >= 50 ? 'Fair' : 'Needs Improvement'}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {currentScore.current >= 90 ? 'Your resume is highly optimized for ATS systems' :
                       currentScore.current >= 70 ? 'Your resume should pass most ATS filters' :
                       currentScore.current >= 50 ? 'Your resume may face some ATS challenges' : 
                       'Your resume needs significant optimization for ATS compatibility'}
                    </p>
                  </div>
                </div>

                {/* Score Factors */}
                {currentScore.factors && currentScore.factors.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Key Factors</h4>
                    <div className="space-y-2">
                      {currentScore.factors.slice(0, 3).map((factor, index) => (
                        <div
                          key={index}
                          className={`flex items-center justify-between p-3 rounded-lg border ${
                            factor.category === 'positive' ? 'bg-green-50 border-green-200' :
                            factor.category === 'negative' ? 'bg-red-50 border-red-200' :
                            'bg-gray-50 border-gray-200'
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            {factor.category === 'positive' ? (
                              <ArrowUp className="w-4 h-4 text-green-600" />
                            ) : factor.category === 'negative' ? (
                              <ArrowDown className="w-4 h-4 text-red-600" />
                            ) : (
                              <Minus className="w-4 h-4 text-gray-600" />
                            )}
                            <div>
                              <p className="font-medium text-gray-900">{factor.name}</p>
                              <p className="text-sm text-gray-600">{factor.description}</p>
                            </div>
                          </div>
                          <div className={`px-2 py-1 rounded text-sm font-medium ${
                            factor.impact > 0 ? 'text-green-600' :
                            factor.impact < 0 ? 'text-red-600' : 'text-gray-600'
                          }`}>
                            {factor.impact > 0 ? '+' : ''}{factor.impact}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Section Breakdown */}
      <AnimatePresence>
        {showBreakdown && currentScore && (
          <motion.div
            variants={staggerItem}
            initial="hidden"
            animate="visible"
            exit="hidden"
          >
            <SectionBreakdown 
              sections={sectionScores}
              onSectionClick={(section) => console.log('Section clicked:', section)}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Score History */}
      {showHistory && scoreHistory.length > 0 && (
        <motion.div variants={staggerItem}>
          <ScoreHistory 
            history={scoreHistory}
            onHistoryItemClick={(item) => console.log('History item clicked:', item)}
          />
        </motion.div>
      )}
    </motion.div>
  );
}

export default ATSScoringSystem;
/**

 * SectionBreakdown Component
 * Shows detailed section-by-section scoring breakdown
 */
function SectionBreakdown({ sections, onSectionClick, className = '' }) {
  const [expandedSections, setExpandedSections] = useState([]);

  const toggleSection = (sectionName) => {
    setExpandedSections(prev => 
      prev.includes(sectionName)
        ? prev.filter(name => name !== sectionName)
        : [...prev, sectionName]
    );
  };

  const getSectionIcon = (sectionName) => {
    const icons = {
      contact: Target,
      summary: Star,
      experience: BarChart3,
      skills: Zap,
      education: Award,
      achievements: TrendingUp
    };
    return icons[sectionName] || CheckCircle;
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-amber-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score) => {
    if (score >= 90) return 'bg-green-50 border-green-200';
    if (score >= 70) return 'bg-blue-50 border-blue-200';
    if (score >= 50) return 'bg-amber-50 border-amber-200';
    return 'bg-red-50 border-red-200';
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'major': return 'text-orange-600 bg-orange-100';
      case 'minor': return 'text-amber-600 bg-amber-100';
      case 'suggestion': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <EnhancedCard className={className}>
      <EnhancedCardHeader>
        <EnhancedCardTitle className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          Section-by-Section Analysis
        </EnhancedCardTitle>
        <EnhancedCardDescription>
          Detailed breakdown of each resume section's ATS compatibility
        </EnhancedCardDescription>
      </EnhancedCardHeader>

      <EnhancedCardContent>
        <div className="space-y-4">
          {Object.entries(sections).map(([sectionName, section]) => {
            const Icon = getSectionIcon(sectionName);
            const isExpanded = expandedSections.includes(sectionName);
            
            return (
              <motion.div
                key={sectionName}
                variants={staggerItem}
                className={`border rounded-lg overflow-hidden ${getScoreBackground(section.score)}`}
              >
                {/* Section Header */}
                <div
                  className="p-4 cursor-pointer hover:bg-opacity-80 transition-colors"
                  onClick={() => toggleSection(sectionName)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Icon className="w-5 h-5" />
                      <div>
                        <h4 className="font-medium text-gray-900 capitalize">
                          {sectionName.replace('_', ' ')} Section
                        </h4>
                        <p className="text-sm text-gray-600">
                          Weight: {Math.round(section.weight * 100)}% of total score
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${getScoreColor(section.score)}`}>
                          {section.score}
                        </div>
                        <div className="text-sm text-gray-500">
                          / {section.maxScore}
                        </div>
                      </div>
                      
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mt-3">
                    <div className="w-full bg-white bg-opacity-50 rounded-full h-2">
                      <motion.div
                        className={`h-2 rounded-full ${
                          section.score >= 90 ? 'bg-green-500' :
                          section.score >= 70 ? 'bg-blue-500' :
                          section.score >= 50 ? 'bg-amber-500' : 'bg-red-500'
                        }`}
                        initial={{ width: 0 }}
                        animate={{ width: `${(section.score / section.maxScore) * 100}%` }}
                        transition={{ duration: 1, delay: 0.2 }}
                      />
                    </div>
                  </div>
                </div>

                {/* Section Details */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <div className="px-4 pb-4 border-t border-white border-opacity-50">
                        {/* Issues */}
                        {section.issues && section.issues.length > 0 && (
                          <div className="mt-4">
                            <h5 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                              <AlertCircle className="w-4 h-4" />
                              Issues Found ({section.issues.length})
                            </h5>
                            <div className="space-y-2">
                              {section.issues.map((issue, index) => (
                                <div
                                  key={index}
                                  className="flex items-start gap-3 p-3 bg-white bg-opacity-50 rounded-lg"
                                >
                                  <div className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                                    {issue.severity}
                                  </div>
                                  <div className="flex-1">
                                    <p className="text-sm font-medium text-gray-900">
                                      {issue.description}
                                    </p>
                                    {issue.suggestion && (
                                      <p className="text-xs text-gray-600 mt-1">
                                        Suggestion: {issue.suggestion}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Recommendations */}
                        {section.recommendations && section.recommendations.length > 0 && (
                          <div className="mt-4">
                            <h5 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                              <CheckCircle className="w-4 h-4" />
                              Recommendations ({section.recommendations.length})
                            </h5>
                            <div className="space-y-2">
                              {section.recommendations.map((recommendation, index) => (
                                <div
                                  key={index}
                                  className="flex items-start gap-3 p-3 bg-white bg-opacity-50 rounded-lg"
                                >
                                  <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                                  <p className="text-sm text-gray-700">{recommendation}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>
      </EnhancedCardContent>
    </EnhancedCard>
  );
}

/**
 * ScoreHistory Component
 * Shows score history tracking and improvement visualization
 */
function ScoreHistory({ history, onHistoryItemClick, className = '' }) {
  const [showAll, setShowAll] = useState(false);
  const [timeRange, setTimeRange] = useState('day'); // day, week, month

  const filteredHistory = useMemo(() => {
    const now = new Date();
    const cutoff = new Date();
    
    switch (timeRange) {
      case 'day':
        cutoff.setDate(now.getDate() - 1);
        break;
      case 'week':
        cutoff.setDate(now.getDate() - 7);
        break;
      case 'month':
        cutoff.setMonth(now.getMonth() - 1);
        break;
      default:
        return history;
    }
    
    return history.filter(item => new Date(item.timestamp) >= cutoff);
  }, [history, timeRange]);

  const displayHistory = showAll ? filteredHistory : filteredHistory.slice(-5);

  const getScoreChange = (current, previous) => {
    if (!previous) return null;
    return current.score - previous.score;
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-amber-600';
    return 'text-red-600';
  };

  const getChangeColor = (change) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  if (history.length === 0) {
    return null;
  }

  return (
    <EnhancedCard className={className}>
      <EnhancedCardHeader>
        <div className="flex items-center justify-between">
          <div>
            <EnhancedCardTitle className="flex items-center gap-2">
              <History className="w-5 h-5" />
              Score History
              <div className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium">
                {filteredHistory.length} entries
              </div>
            </EnhancedCardTitle>
            <EnhancedCardDescription>
              Track your ATS score improvements over time
            </EnhancedCardDescription>
          </div>
          
          <div className="flex items-center gap-2">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="day">Last 24 hours</option>
              <option value="week">Last week</option>
              <option value="month">Last month</option>
            </select>
            
            {filteredHistory.length > 5 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAll(!showAll)}
              >
                {showAll ? 'Show Less' : 'Show All'}
              </Button>
            )}
          </div>
        </div>
      </EnhancedCardHeader>

      <EnhancedCardContent>
        <div className="space-y-3">
          {displayHistory.map((item, index) => {
            const previousItem = displayHistory[index + 1];
            const change = getScoreChange(item, previousItem);
            
            return (
              <motion.div
                key={index}
                variants={staggerItem}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                onClick={() => onHistoryItemClick?.(item)}
              >
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <div className={`text-2xl font-bold ${getScoreColor(item.score)}`}>
                      {item.score}
                    </div>
                    <div className="text-xs text-gray-500">
                      {item.confidence}
                    </div>
                  </div>
                  
                  <div>
                    <div className="font-medium text-gray-900">
                      {item.timestamp.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">
                      {Object.keys(item.sections).length} sections analyzed
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  {change !== null && (
                    <div className={`flex items-center gap-1 px-2 py-1 rounded text-sm font-medium ${
                      change > 0 ? 'bg-green-100 text-green-700' :
                      change < 0 ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {change > 0 ? (
                        <ArrowUp className="w-3 h-3" />
                      ) : change < 0 ? (
                        <ArrowDown className="w-3 h-3" />
                      ) : (
                        <Minus className="w-3 h-3" />
                      )}
                      {change > 0 ? '+' : ''}{change}
                    </div>
                  )}
                  
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </div>
              </motion.div>
            );
          })}
        </div>
        
        {filteredHistory.length === 0 && (
          <div className="text-center py-8">
            <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No History Available</h3>
            <p className="text-gray-600">
              Score history will appear here as you make changes to your resume
            </p>
          </div>
        )}
      </EnhancedCardContent>
    </EnhancedCard>
  );
}