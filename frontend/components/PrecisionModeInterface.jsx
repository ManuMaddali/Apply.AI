/**
 * PrecisionModeInterface Component
 * Implements granular control with real-time impact preview and bullet-level customization
 * Handles tier-based features and comprehensive analytics dashboard
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings,
  Target,
  BarChart3,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Crown,
  Star,
  ArrowRight,
  RefreshCw,
  FileText,
  Zap,
  Award,
  Users,
  Clock,
  Edit3,
  Eye,
  Download,
  Sparkles,
  Brain,
  Lightbulb,
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  Info
} from 'lucide-react';
import { Button } from './ui/button';
import { EnhancedCard, EnhancedCardHeader, EnhancedCardTitle, EnhancedCardDescription, EnhancedCardContent, EnhancedCardFooter } from './ui/enhanced-card';
import { TierBadge } from './ui/tier-badge';
import { UpgradePrompt } from './UpgradePrompt';
import { useUserStore, useProcessingStore, useUIStore, useAnalyticsStore } from '../lib/store';
import { fadeInUp, staggerContainer, staggerItem, hoverLift, scaleIn } from '../lib/motion';

/**
 * ResumeAnalysisDashboard Component
 * Subtask 5.1: Current ATS score display with section-by-section breakdown
 */
function ResumeAnalysisDashboard({
  resumeData,
  jobData,
  atsScore,
  onScoreUpdate,
  isProUser,
  className = ''
}) {
  const [expandedSections, setExpandedSections] = useState(['summary']);
  const [showDetails, setShowDetails] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Mock data for demonstration - in real implementation, this would come from props/API
  const mockATSScore = atsScore || {
    current: 67,
    potential: 94,
    improvement: 27,
    sectionScores: {
      contact: { score: 100, maxScore: 100, status: 'perfect' },
      summary: { score: 45, maxScore: 100, status: 'needs-keywords' },
      experience: { score: 78, maxScore: 100, status: 'good-can-enhance' },
      skills: { score: 0, maxScore: 100, status: 'missing' },
      education: { score: 65, maxScore: 100, status: 'basic-format' },
      achievements: { score: 0, maxScore: 100, status: 'missing' }
    },
    confidenceLevel: 'high',
    lastUpdated: new Date().toISOString()
  };

  const mockJobMatch = {
    requiredSkillsMatch: 6,
    totalRequiredSkills: 12,
    matchPercentage: 50,
    missingKeywords: ['React', 'Kubernetes', 'Leadership', 'Agile', 'Python', 'AWS'],
    experienceRelevance: 78,
    industryAlignment: 85
  };

  const sectionConfigs = [
    {
      id: 'contact',
      name: 'Contact Information',
      icon: Users,
      description: 'Personal and contact details',
      essential: true
    },
    {
      id: 'summary',
      name: 'Professional Summary',
      icon: FileText,
      description: 'Opening statement and career overview',
      essential: true
    },
    {
      id: 'experience',
      name: 'Work Experience',
      icon: Award,
      description: 'Professional work history and achievements',
      essential: true
    },
    {
      id: 'skills',
      name: 'Skills Section',
      icon: Target,
      description: 'Technical and soft skills',
      essential: true
    },
    {
      id: 'education',
      name: 'Education',
      icon: Brain,
      description: 'Academic background and qualifications',
      essential: false
    },
    {
      id: 'achievements',
      name: 'Achievements',
      icon: Star,
      description: 'Awards, certifications, and notable accomplishments',
      essential: false
    }
  ];

  const getStatusColor = (status) => {
    const colors = {
      'perfect': 'text-green-600 bg-green-50 border-green-200',
      'good-can-enhance': 'text-blue-600 bg-blue-50 border-blue-200',
      'needs-keywords': 'text-amber-600 bg-amber-50 border-amber-200',
      'basic-format': 'text-gray-600 bg-gray-50 border-gray-200',
      'missing': 'text-red-600 bg-red-50 border-red-200'
    };
    return colors[status] || colors['basic-format'];
  };

  const getStatusText = (status) => {
    const texts = {
      'perfect': 'Perfect',
      'good-can-enhance': 'Good - Can Enhance',
      'needs-keywords': 'Needs Keywords',
      'basic-format': 'Basic Format',
      'missing': 'Missing Section'
    };
    return texts[status] || 'Unknown';
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-amber-600';
    return 'text-red-600';
  };

  const handleRefreshScore = async () => {
    setRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setRefreshing(false);
    onScoreUpdate?.({
      ...mockATSScore,
      current: mockATSScore.current + Math.floor(Math.random() * 5),
      lastUpdated: new Date().toISOString()
    });
  };

  const toggleSection = (sectionId) => {
    setExpandedSections(prev => 
      prev.includes(sectionId) 
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Current ATS Score Overview */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <div className="flex items-center justify-between">
              <div>
                <EnhancedCardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  ATS Score Analysis
                </EnhancedCardTitle>
                <EnhancedCardDescription>
                  Current resume performance and improvement potential
                </EnhancedCardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowDetails(!showDetails)}
                  className="text-blue-600 border-blue-300"
                >
                  <Info className="w-4 h-4 mr-2" />
                  {showDetails ? 'Hide Details' : 'Show Details'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefreshScore}
                  disabled={refreshing}
                  className="text-gray-600 border-gray-300"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
            </div>
          </EnhancedCardHeader>
          
          <EnhancedCardContent>
            {/* Score Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Current Score */}
              <div className="text-center">
                <div className="relative">
                  <div className="w-24 h-24 mx-auto mb-3">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-gray-200"
                      />
                      <motion.circle
                        cx="50"
                        cy="50"
                        r="40"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeLinecap="round"
                        className={getScoreColor(mockATSScore.current)}
                        strokeDasharray={`${2 * Math.PI * 40}`}
                        initial={{ strokeDashoffset: 2 * Math.PI * 40 }}
                        animate={{ 
                          strokeDashoffset: 2 * Math.PI * 40 * (1 - mockATSScore.current / 100) 
                        }}
                        transition={{ duration: 1.5, delay: 0.5 }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className={`text-2xl font-bold ${getScoreColor(mockATSScore.current)}`}>
                        {mockATSScore.current}
                      </span>
                    </div>
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900">Current Score</h3>
                <p className="text-sm text-gray-600">Your resume's ATS compatibility</p>
              </div>

              {/* Potential Score */}
              <div className="text-center">
                <div className="relative">
                  <div className="w-24 h-24 mx-auto mb-3">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-gray-200"
                      />
                      <motion.circle
                        cx="50"
                        cy="50"
                        r="40"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeLinecap="round"
                        className="text-green-600"
                        strokeDasharray={`${2 * Math.PI * 40}`}
                        initial={{ strokeDashoffset: 2 * Math.PI * 40 }}
                        animate={{ 
                          strokeDashoffset: 2 * Math.PI * 40 * (1 - mockATSScore.potential / 100) 
                        }}
                        transition={{ duration: 1.5, delay: 0.8 }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl font-bold text-green-600">
                        {mockATSScore.potential}
                      </span>
                    </div>
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900">Potential Score</h3>
                <p className="text-sm text-gray-600">With precision enhancements</p>
              </div>

              {/* Improvement */}
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-3 flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100 rounded-full">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">+{mockATSScore.improvement}</div>
                    <div className="text-xs text-purple-700">points</div>
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900">Improvement</h3>
                <p className="text-sm text-gray-600">Potential gain with Pro</p>
              </div>
            </div>

            {/* Confidence Level */}
            <div className="flex items-center justify-center mb-6">
              <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-full border border-green-200">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-green-800">
                  {mockATSScore.confidenceLevel.charAt(0).toUpperCase() + mockATSScore.confidenceLevel.slice(1)} Confidence
                </span>
              </div>
            </div>

            {/* Detailed Analysis */}
            <AnimatePresence>
              {showDetails && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <div className="border-t border-gray-200 pt-6">
                    <h4 className="font-medium text-gray-900 mb-4">Score Breakdown</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-600 mb-2">Strengths</div>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-sm">
                            <CheckCircle className="w-3 h-3 text-green-500" />
                            <span>Complete contact information</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <CheckCircle className="w-3 h-3 text-green-500" />
                            <span>Relevant work experience</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <CheckCircle className="w-3 h-3 text-green-500" />
                            <span>Proper formatting structure</span>
                          </div>
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600 mb-2">Areas for Improvement</div>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-sm">
                            <AlertCircle className="w-3 h-3 text-amber-500" />
                            <span>Missing key skills section</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <AlertCircle className="w-3 h-3 text-amber-500" />
                            <span>Weak professional summary</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <AlertCircle className="w-3 h-3 text-amber-500" />
                            <span>Limited keyword optimization</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Section-by-Section Analysis */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <EnhancedCardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5" />
              Section Analysis
            </EnhancedCardTitle>
            <EnhancedCardDescription>
              Detailed breakdown of each resume section
            </EnhancedCardDescription>
          </EnhancedCardHeader>
          
          <EnhancedCardContent>
            <div className="space-y-4">
              {sectionConfigs.map((section) => {
                const sectionScore = mockATSScore.sectionScores[section.id];
                const isExpanded = expandedSections.includes(section.id);
                const Icon = section.icon;

                if (!sectionScore) return null;

                return (
                  <motion.div
                    key={section.id}
                    variants={staggerItem}
                    className="border border-gray-200 rounded-lg overflow-hidden"
                  >
                    <div
                      className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                      onClick={() => toggleSection(section.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Icon className="w-5 h-5 text-gray-600" />
                          <div>
                            <h4 className="font-medium text-gray-900">{section.name}</h4>
                            <p className="text-sm text-gray-600">{section.description}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <div className={`text-lg font-bold ${getScoreColor(sectionScore.score)}`}>
                              {sectionScore.score}
                            </div>
                            <div className="text-xs text-gray-500">/ {sectionScore.maxScore}</div>
                          </div>
                          
                          <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(sectionScore.status)}`}>
                            {getStatusText(sectionScore.status)}
                          </div>
                          
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-gray-400" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-gray-400" />
                          )}
                        </div>
                      </div>
                    </div>

                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.3 }}
                          className="overflow-hidden"
                        >
                          <div className="px-4 pb-4 border-t border-gray-100 bg-gray-50">
                            <div className="pt-4">
                              {/* Progress Bar */}
                              <div className="mb-4">
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-sm font-medium text-gray-700">Section Score</span>
                                  <span className="text-sm text-gray-600">
                                    {sectionScore.score}% complete
                                  </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <motion.div
                                    className={`h-2 rounded-full ${
                                      sectionScore.score >= 90 ? 'bg-green-500' :
                                      sectionScore.score >= 70 ? 'bg-blue-500' :
                                      sectionScore.score >= 50 ? 'bg-amber-500' :
                                      'bg-red-500'
                                    }`}
                                    initial={{ width: 0 }}
                                    animate={{ width: `${sectionScore.score}%` }}
                                    transition={{ duration: 0.8, delay: 0.2 }}
                                  />
                                </div>
                              </div>

                              {/* Section-specific insights */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <h5 className="text-sm font-medium text-gray-900 mb-2">Current Status</h5>
                                  <div className="text-sm text-gray-600">
                                    {section.id === 'summary' && 'Professional summary exists but lacks industry keywords and quantified achievements.'}
                                    {section.id === 'experience' && 'Work experience is well-structured with good chronological order and relevant positions.'}
                                    {section.id === 'skills' && 'Skills section is missing. Adding this would significantly improve ATS compatibility.'}
                                    {section.id === 'contact' && 'Contact information is complete and properly formatted.'}
                                    {section.id === 'education' && 'Education section has basic formatting but could benefit from relevant coursework details.'}
                                    {section.id === 'achievements' && 'No achievements section found. Consider adding awards, certifications, or notable accomplishments.'}
                                  </div>
                                </div>
                                <div>
                                  <h5 className="text-sm font-medium text-gray-900 mb-2">Recommendations</h5>
                                  <div className="space-y-1">
                                    {section.id === 'summary' && (
                                      <>
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                          <Lightbulb className="w-3 h-3 text-amber-500" />
                                          <span>Add 3-4 relevant keywords</span>
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                          <Lightbulb className="w-3 h-3 text-amber-500" />
                                          <span>Include quantified achievements</span>
                                        </div>
                                      </>
                                    )}
                                    {section.id === 'skills' && (
                                      <>
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                          <Lightbulb className="w-3 h-3 text-amber-500" />
                                          <span>Add technical skills section</span>
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                          <Lightbulb className="w-3 h-3 text-amber-500" />
                                          <span>Include job-relevant keywords</span>
                                        </div>
                                      </>
                                    )}
                                    {section.id === 'experience' && (
                                      <>
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                          <Lightbulb className="w-3 h-3 text-amber-500" />
                                          <span>Strengthen action verbs</span>
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                          <Lightbulb className="w-3 h-3 text-amber-500" />
                                          <span>Add more metrics</span>
                                        </div>
                                      </>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
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
      </motion.div>

      {/* Job Match Analysis */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <EnhancedCardTitle className="flex items-center gap-2">
              <Search className="w-5 h-5" />
              Job Match Analysis
            </EnhancedCardTitle>
            <EnhancedCardDescription>
              How well your resume matches the job requirements
            </EnhancedCardDescription>
          </EnhancedCardHeader>
          
          <EnhancedCardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Skills Match */}
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-3 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-xl font-bold text-blue-600">
                    {mockJobMatch.requiredSkillsMatch}/{mockJobMatch.totalRequiredSkills}
                  </span>
                </div>
                <h4 className="font-medium text-gray-900">Required Skills</h4>
                <p className="text-sm text-gray-600">{mockJobMatch.matchPercentage}% match</p>
              </div>

              {/* Experience Relevance */}
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-3 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-xl font-bold text-green-600">
                    {mockJobMatch.experienceRelevance}%
                  </span>
                </div>
                <h4 className="font-medium text-gray-900">Experience Match</h4>
                <p className="text-sm text-gray-600">Relevance to role</p>
              </div>

              {/* Industry Alignment */}
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-3 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-xl font-bold text-purple-600">
                    {mockJobMatch.industryAlignment}%
                  </span>
                </div>
                <h4 className="font-medium text-gray-900">Industry Fit</h4>
                <p className="text-sm text-gray-600">Sector alignment</p>
              </div>
            </div>

            {/* Missing Keywords */}
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <div className="flex items-center gap-2 mb-3">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <h4 className="font-medium text-red-800">Missing Keywords</h4>
              </div>
              <p className="text-sm text-red-700 mb-3">
                These important keywords from the job posting are not found in your resume:
              </p>
              <div className="flex flex-wrap gap-2">
                {mockJobMatch.missingKeywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-white rounded-full text-sm font-medium text-red-700 border border-red-300"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>
    </motion.div>
  );
}

/**
 * DynamicEnhancementSelection Component
 * Subtask 5.2: High Impact, Medium Impact, and Advanced enhancement categories
 */
function DynamicEnhancementSelection({
  resumeData,
  jobData,
  atsScore,
  onEnhancementChange,
  onScoreUpdate,
  isProUser,
  onUpgradeClick,
  className = ''
}) {
  const [selectedEnhancements, setSelectedEnhancements] = useState(new Set());
  const [enhancementPreviews, setEnhancementPreviews] = useState({});
  const [expandedCategories, setExpandedCategories] = useState(['high']);
  const [showImpactScores, setShowImpactScores] = useState(true);
  const [filterCategory, setFilterCategory] = useState('all');
  const [sortBy, setSortBy] = useState('impact'); // impact, time, difficulty

  // Mock enhancement data - in real implementation, this would come from API
  const mockEnhancements = [
    // High Impact Enhancements
    {
      id: 'add-skills-section',
      title: 'Add Skills Section',
      description: 'Create a comprehensive skills section with job-relevant keywords',
      impact: 15,
      category: 'high',
      type: 'structure_improvement',
      estimatedTime: 2,
      difficulty: 'easy',
      keywords: ['React', 'Node.js', 'Python', 'Kubernetes', 'AWS', 'Docker'],
      beforeText: 'No skills section present',
      afterText: 'Technical Skills: React, Node.js, Python, Kubernetes, AWS, Docker, JavaScript, TypeScript, MongoDB, PostgreSQL',
      available: true,
      proOnly: false,
      autoApplicable: true,
      confidence: 95
    },
    {
      id: 'enhance-summary',
      title: 'Enhance Professional Summary',
      description: 'Strengthen opening statement with keywords and quantified achievements',
      impact: 12,
      category: 'high',
      type: 'content_enhancement',
      estimatedTime: 3,
      difficulty: 'medium',
      keywords: ['Senior', 'Leadership', 'Scalable', 'Performance'],
      beforeText: 'Software engineer with experience in web development.',
      afterText: 'Senior software engineer with 5+ years building scalable React applications, leading cross-functional teams of 8+ developers, and improving system performance by 40%.',
      available: true,
      proOnly: false,
      autoApplicable: true,
      confidence: 88
    },
    {
      id: 'quantify-achievements',
      title: 'Quantify Achievements',
      description: 'Add specific metrics and numbers to experience bullets',
      impact: 10,
      category: 'high',
      type: 'quantification',
      estimatedTime: 5,
      difficulty: 'medium',
      keywords: ['Improved', 'Increased', 'Reduced', 'Led'],
      beforeText: 'Improved application performance',
      afterText: 'Improved application performance by 45%, reducing load times from 3.2s to 1.8s',
      available: true,
      proOnly: false,
      autoApplicable: false,
      confidence: 92
    },
    
    // Medium Impact Enhancements
    {
      id: 'optimize-education',
      title: 'Optimize Education Section',
      description: 'Enhance education formatting and add relevant coursework',
      impact: 6,
      category: 'medium',
      type: 'structure_improvement',
      estimatedTime: 2,
      difficulty: 'easy',
      keywords: ['Computer Science', 'Relevant Coursework'],
      beforeText: 'Bachelor of Science in Computer Science, University Name, 2020',
      afterText: 'Bachelor of Science in Computer Science, University Name, 2020\nRelevant Coursework: Data Structures, Algorithms, Software Engineering, Database Systems',
      available: true,
      proOnly: false,
      autoApplicable: true,
      confidence: 75
    },
    {
      id: 'strengthen-action-verbs',
      title: 'Strengthen Action Verbs',
      description: 'Replace weak verbs with powerful action words',
      impact: 8,
      category: 'medium',
      type: 'language_strengthening',
      estimatedTime: 4,
      difficulty: 'easy',
      keywords: ['Architected', 'Spearheaded', 'Orchestrated', 'Optimized'],
      beforeText: 'Worked on web applications',
      afterText: 'Architected scalable web applications',
      available: true,
      proOnly: false,
      autoApplicable: true,
      confidence: 85
    },
    {
      id: 'add-certifications',
      title: 'Add Certifications Section',
      description: 'Highlight relevant certifications and training',
      impact: 5,
      category: 'medium',
      type: 'structure_improvement',
      estimatedTime: 2,
      difficulty: 'easy',
      keywords: ['AWS Certified', 'Scrum Master', 'PMP'],
      beforeText: 'No certifications section',
      afterText: 'Certifications: AWS Certified Solutions Architect, Certified Scrum Master (CSM), Google Cloud Professional',
      available: true,
      proOnly: true,
      autoApplicable: true,
      confidence: 70
    },

    // Advanced Enhancements
    {
      id: 'industry-keywords',
      title: 'Industry-Specific Keywords',
      description: 'Integrate advanced industry terminology and buzzwords',
      impact: 8,
      category: 'advanced',
      type: 'keyword_optimization',
      estimatedTime: 6,
      difficulty: 'hard',
      keywords: ['Microservices', 'CI/CD', 'DevOps', 'Agile', 'System Design'],
      beforeText: 'Built applications using modern practices',
      afterText: 'Architected microservices-based applications using CI/CD pipelines, implementing DevOps best practices and Agile methodologies for scalable system design',
      available: true,
      proOnly: true,
      autoApplicable: false,
      confidence: 82
    },
    {
      id: 'advanced-metrics',
      title: 'Advanced Metrics Integration',
      description: 'Add sophisticated performance and business impact metrics',
      impact: 12,
      category: 'advanced',
      type: 'quantification',
      estimatedTime: 8,
      difficulty: 'hard',
      keywords: ['ROI', 'KPI', 'Performance', 'Efficiency'],
      beforeText: 'Improved system efficiency',
      afterText: 'Optimized system architecture achieving 99.9% uptime, reducing operational costs by $2M annually and improving team productivity KPIs by 35%',
      available: true,
      proOnly: true,
      autoApplicable: false,
      confidence: 90
    },
    {
      id: 'leadership-emphasis',
      title: 'Leadership & Impact Emphasis',
      description: 'Highlight leadership experience and team impact',
      impact: 9,
      category: 'advanced',
      type: 'content_enhancement',
      estimatedTime: 7,
      difficulty: 'hard',
      keywords: ['Led', 'Mentored', 'Managed', 'Strategic'],
      beforeText: 'Worked with team members',
      afterText: 'Led cross-functional team of 12 engineers, mentored 5 junior developers, and drove strategic technical decisions resulting in 40% faster delivery cycles',
      available: true,
      proOnly: true,
      autoApplicable: false,
      confidence: 87
    }
  ];

  const categoryConfigs = {
    high: {
      name: 'High Impact',
      description: 'Essential enhancements with maximum ATS score improvement',
      color: 'red',
      icon: Zap,
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-800'
    },
    medium: {
      name: 'Medium Impact',
      description: 'Important improvements for better resume optimization',
      color: 'blue',
      icon: TrendingUp,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800'
    },
    advanced: {
      name: 'Advanced',
      description: 'Sophisticated enhancements for competitive advantage',
      color: 'purple',
      icon: Crown,
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      textColor: 'text-purple-800'
    }
  };

  const filteredEnhancements = useMemo(() => {
    let filtered = mockEnhancements;
    
    if (filterCategory !== 'all') {
      filtered = filtered.filter(e => e.category === filterCategory);
    }
    
    // Sort enhancements
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'impact':
          return b.impact - a.impact;
        case 'time':
          return a.estimatedTime - b.estimatedTime;
        case 'difficulty':
          const difficultyOrder = { easy: 1, medium: 2, hard: 3 };
          return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
        default:
          return b.impact - a.impact;
      }
    });
    
    return filtered;
  }, [filterCategory, sortBy]);

  const groupedEnhancements = useMemo(() => {
    return filteredEnhancements.reduce((groups, enhancement) => {
      if (!groups[enhancement.category]) {
        groups[enhancement.category] = [];
      }
      groups[enhancement.category].push(enhancement);
      return groups;
    }, {});
  }, [filteredEnhancements]);

  const handleEnhancementToggle = (enhancementId) => {
    const enhancement = mockEnhancements.find(e => e.id === enhancementId);
    
    if (!enhancement) return;
    
    // Check if pro-only feature
    if (enhancement.proOnly && !isProUser) {
      onUpgradeClick?.();
      return;
    }
    
    const newSelected = new Set(selectedEnhancements);
    if (newSelected.has(enhancementId)) {
      newSelected.delete(enhancementId);
    } else {
      newSelected.add(enhancementId);
    }
    
    setSelectedEnhancements(newSelected);
    onEnhancementChange?.(Array.from(newSelected));
    
    // Update ATS score based on selected enhancements
    if (atsScore) {
      const totalImpact = Array.from(newSelected).reduce((sum, id) => {
        const enh = mockEnhancements.find(e => e.id === id);
        return sum + (enh?.impact || 0);
      }, 0);
      
      const newScore = {
        ...atsScore,
        current: Math.min(100, atsScore.current + totalImpact),
        improvement: totalImpact,
        lastUpdated: new Date().toISOString()
      };
      
      onScoreUpdate?.(newScore);
    }
  };

  const handlePreviewEnhancement = async (enhancementId) => {
    const enhancement = mockEnhancements.find(e => e.id === enhancementId);
    if (!enhancement) return;
    
    // Simulate API call for preview
    setEnhancementPreviews(prev => ({
      ...prev,
      [enhancementId]: { loading: true }
    }));
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setEnhancementPreviews(prev => ({
      ...prev,
      [enhancementId]: {
        loading: false,
        beforeText: enhancement.beforeText,
        afterText: enhancement.afterText,
        impact: enhancement.impact,
        keywords: enhancement.keywords,
        confidence: enhancement.confidence
      }
    }));
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => 
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const getTotalImpact = () => {
    return Array.from(selectedEnhancements).reduce((sum, id) => {
      const enhancement = mockEnhancements.find(e => e.id === id);
      return sum + (enhancement?.impact || 0);
    }, 0);
  };

  const getEstimatedTime = () => {
    return Array.from(selectedEnhancements).reduce((sum, id) => {
      const enhancement = mockEnhancements.find(e => e.id === id);
      return sum + (enhancement?.estimatedTime || 0);
    }, 0);
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Header with Controls */}
      <motion.div variants={staggerItem}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              Enhancement Selection
            </h3>
            <p className="text-gray-600">
              Choose enhancements to optimize your resume for this specific job
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Filter */}
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Categories</option>
              <option value="high">High Impact</option>
              <option value="medium">Medium Impact</option>
              <option value="advanced">Advanced</option>
            </select>
            
            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="impact">Sort by Impact</option>
              <option value="time">Sort by Time</option>
              <option value="difficulty">Sort by Difficulty</option>
            </select>
            
            {/* Impact Scores Toggle */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowImpactScores(!showImpactScores)}
              className={showImpactScores ? 'bg-blue-50 text-blue-700 border-blue-300' : ''}
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Impact Scores
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Selection Summary */}
      {selectedEnhancements.size > 0 && (
        <motion.div variants={staggerItem}>
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{selectedEnhancements.size}</div>
                  <div className="text-sm text-gray-600">Selected</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">+{getTotalImpact()}</div>
                  <div className="text-sm text-gray-600">Total Impact</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{getEstimatedTime()}m</div>
                  <div className="text-sm text-gray-600">Est. Time</div>
                </div>
              </div>
              <Button
                onClick={() => setSelectedEnhancements(new Set())}
                variant="outline"
                size="sm"
                className="text-gray-600"
              >
                Clear All
              </Button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Enhancement Categories */}
      <motion.div variants={staggerItem} className="space-y-6">
        {Object.entries(groupedEnhancements).map(([category, enhancements]) => {
          const config = categoryConfigs[category];
          const isExpanded = expandedCategories.includes(category);
          const Icon = config.icon;
          
          return (
            <motion.div key={category} variants={staggerItem}>
              <EnhancedCard>
                <EnhancedCardHeader>
                  <div
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => toggleCategory(category)}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${config.bgColor}`}>
                        <Icon className={`w-5 h-5 ${config.textColor}`} />
                      </div>
                      <div>
                        <EnhancedCardTitle className="flex items-center gap-2">
                          {config.name}
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor} ${config.borderColor} border`}>
                            {enhancements.length} available
                          </span>
                        </EnhancedCardTitle>
                        <EnhancedCardDescription>
                          {config.description}
                        </EnhancedCardDescription>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {showImpactScores && (
                        <div className="text-right">
                          <div className="text-sm text-gray-500">Max Impact</div>
                          <div className="text-lg font-bold text-green-600">
                            +{Math.max(...enhancements.map(e => e.impact))}
                          </div>
                        </div>
                      )}
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </div>
                </EnhancedCardHeader>

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <EnhancedCardContent>
                        <div className="space-y-4">
                          {enhancements.map((enhancement) => {
                            const isSelected = selectedEnhancements.has(enhancement.id);
                            const canAccess = !enhancement.proOnly || isProUser;
                            const preview = enhancementPreviews[enhancement.id];
                            
                            return (
                              <motion.div
                                key={enhancement.id}
                                variants={staggerItem}
                                className={`
                                  border-2 rounded-lg p-4 transition-all duration-300
                                  ${isSelected && canAccess
                                    ? 'border-blue-500 bg-blue-50'
                                    : canAccess
                                    ? 'border-gray-200 hover:border-gray-300'
                                    : 'border-purple-200 bg-purple-50 opacity-75'
                                  }
                                `}
                              >
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                      <h4 className="font-medium text-gray-900">{enhancement.title}</h4>
                                      
                                      {showImpactScores && (
                                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                                          +{enhancement.impact} points
                                        </span>
                                      )}
                                      
                                      {enhancement.proOnly && (
                                        <TierBadge tier="pro" size="sm" />
                                      )}
                                      
                                      {enhancement.autoApplicable && (
                                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                                          Auto-apply
                                        </span>
                                      )}
                                    </div>
                                    
                                    <p className="text-sm text-gray-600 mb-3">{enhancement.description}</p>
                                    
                                    {/* Enhancement Details */}
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3 text-xs">
                                      <div className="flex items-center gap-1">
                                        <Clock className="w-3 h-3 text-gray-400" />
                                        <span className="text-gray-600">{enhancement.estimatedTime}m</span>
                                      </div>
                                      <div className="flex items-center gap-1">
                                        <Target className="w-3 h-3 text-gray-400" />
                                        <span className="text-gray-600 capitalize">{enhancement.difficulty}</span>
                                      </div>
                                      <div className="flex items-center gap-1">
                                        <CheckCircle className="w-3 h-3 text-gray-400" />
                                        <span className="text-gray-600">{enhancement.confidence}% confident</span>
                                      </div>
                                      <div className="flex items-center gap-1">
                                        <Search className="w-3 h-3 text-gray-400" />
                                        <span className="text-gray-600">{enhancement.keywords.length} keywords</span>
                                      </div>
                                    </div>
                                    
                                    {/* Keywords Preview */}
                                    <div className="flex flex-wrap gap-1 mb-3">
                                      {enhancement.keywords.slice(0, 4).map((keyword, index) => (
                                        <span
                                          key={index}
                                          className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                                        >
                                          {keyword}
                                        </span>
                                      ))}
                                      {enhancement.keywords.length > 4 && (
                                        <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded">
                                          +{enhancement.keywords.length - 4} more
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                  
                                  <div className="flex flex-col items-end gap-2 ml-4">
                                    {canAccess ? (
                                      <>
                                        <Button
                                          variant={isSelected ? "default" : "outline"}
                                          size="sm"
                                          onClick={() => handleEnhancementToggle(enhancement.id)}
                                          className={isSelected ? 'bg-blue-600 text-white' : ''}
                                        >
                                          {isSelected ? (
                                            <>
                                              <CheckCircle className="w-4 h-4 mr-2" />
                                              Selected
                                            </>
                                          ) : (
                                            'Select'
                                          )}
                                        </Button>
                                        
                                        <Button
                                          variant="ghost"
                                          size="sm"
                                          onClick={() => handlePreviewEnhancement(enhancement.id)}
                                          className="text-blue-600 hover:text-blue-700"
                                        >
                                          <Eye className="w-4 h-4 mr-2" />
                                          Preview
                                        </Button>
                                      </>
                                    ) : (
                                      <Button
                                        size="sm"
                                        onClick={onUpgradeClick}
                                        className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
                                      >
                                        <Crown className="w-4 h-4 mr-2" />
                                        Upgrade
                                      </Button>
                                    )}
                                  </div>
                                </div>
                                
                                {/* Enhancement Preview */}
                                <AnimatePresence>
                                  {preview && (
                                    <motion.div
                                      initial={{ height: 0, opacity: 0 }}
                                      animate={{ height: 'auto', opacity: 1 }}
                                      exit={{ height: 0, opacity: 0 }}
                                      transition={{ duration: 0.3 }}
                                      className="mt-4 pt-4 border-t border-gray-200 overflow-hidden"
                                    >
                                      {preview.loading ? (
                                        <div className="flex items-center justify-center py-4">
                                          <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
                                          <span className="ml-2 text-sm text-gray-600">Generating preview...</span>
                                        </div>
                                      ) : (
                                        <div className="space-y-3">
                                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                              <h5 className="text-sm font-medium text-gray-900 mb-2">Before</h5>
                                              <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-gray-700">
                                                {preview.beforeText}
                                              </div>
                                            </div>
                                            <div>
                                              <h5 className="text-sm font-medium text-gray-900 mb-2">After</h5>
                                              <div className="p-3 bg-green-50 border border-green-200 rounded text-sm text-gray-700">
                                                {preview.afterText}
                                              </div>
                                            </div>
                                          </div>
                                          
                                          <div className="flex items-center justify-between text-sm">
                                            <div className="flex items-center gap-4">
                                              <span className="text-green-600 font-medium">
                                                Impact: +{preview.impact} points
                                              </span>
                                              <span className="text-blue-600">
                                                Keywords: {preview.keywords.join(', ')}
                                              </span>
                                            </div>
                                            <span className="text-gray-600">
                                              {preview.confidence}% confidence
                                            </span>
                                          </div>
                                        </div>
                                      )}
                                    </motion.div>
                                  )}
                                </AnimatePresence>
                              </motion.div>
                            );
                          })}
                        </div>
                      </EnhancedCardContent>
                    </motion.div>
                  )}
                </AnimatePresence>
              </EnhancedCard>
            </motion.div>
          );
        })}
      </motion.div>
    </motion.div>
  );
}

/**
 * FreeUserPrecisionExperience Component
 * Subtask 5.3: Auto-apply smart enhancements with clear explanations
 */
function FreeUserPrecisionExperience({
  resumeData,
  jobData,
  atsScore,
  onScoreUpdate,
  onUpgradeClick,
  className = ''
}) {
  const [appliedEnhancements, setAppliedEnhancements] = useState([]);
  const [showProPreview, setShowProPreview] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  // Smart enhancements that are auto-applied for free users
  const smartEnhancements = [
    {
      id: 'basic-keywords',
      title: 'Basic Keyword Optimization',
      description: 'Added essential keywords from the job posting to improve ATS compatibility',
      impact: 8,
      applied: true,
      beforeText: 'Software engineer with experience in web development.',
      afterText: 'Software engineer with experience in React web development and JavaScript programming.',
      keywords: ['React', 'JavaScript'],
      explanation: 'We automatically identified and added the most important keywords from the job posting to your professional summary.'
    },
    {
      id: 'format-improvement',
      title: 'Format Optimization',
      description: 'Improved resume structure and formatting for better ATS parsing',
      impact: 5,
      applied: true,
      beforeText: 'Inconsistent formatting and spacing',
      afterText: 'Clean, consistent formatting with proper spacing and bullet points',
      keywords: [],
      explanation: 'We standardized your resume formatting to ensure ATS systems can properly parse your information.'
    },
    {
      id: 'contact-enhancement',
      title: 'Contact Information Enhancement',
      description: 'Optimized contact section for ATS compatibility',
      impact: 3,
      applied: true,
      beforeText: 'Basic contact info',
      afterText: 'Professional contact information with LinkedIn profile and location',
      keywords: [],
      explanation: 'We enhanced your contact section to include all essential information that recruiters look for.'
    }
  ];

  // Pro features preview
  const proFeaturesPreview = [
    {
      id: 'advanced-skills',
      title: 'Advanced Skills Section',
      description: 'Comprehensive skills section with technical and soft skills categorization',
      impact: 15,
      proOnly: true,
      beforeText: 'No skills section present',
      afterText: 'Technical Skills: React, Node.js, Python, AWS, Docker, Kubernetes\nSoft Skills: Leadership, Team Collaboration, Problem Solving, Agile Methodologies',
      keywords: ['React', 'Node.js', 'Python', 'AWS', 'Docker', 'Kubernetes', 'Leadership', 'Agile'],
      explanation: 'Pro users get a comprehensive skills section that significantly boosts ATS scores.'
    },
    {
      id: 'quantified-achievements',
      title: 'Quantified Achievements',
      description: 'Transform experience bullets with specific metrics and impact numbers',
      impact: 12,
      proOnly: true,
      beforeText: 'Improved application performance and user experience',
      afterText: 'Improved application performance by 45%, reducing load times from 3.2s to 1.8s, resulting in 23% increase in user engagement',
      keywords: ['Performance', 'Metrics', 'Impact'],
      explanation: 'Pro enhancement adds specific numbers and metrics to make your achievements more compelling.'
    },
    {
      id: 'industry-keywords',
      title: 'Industry-Specific Keywords',
      description: 'Advanced keyword optimization with industry-specific terminology',
      impact: 10,
      proOnly: true,
      beforeText: 'Built applications using modern practices',
      afterText: 'Architected scalable microservices using CI/CD pipelines, implementing DevOps best practices and Agile methodologies',
      keywords: ['Microservices', 'CI/CD', 'DevOps', 'Agile', 'Scalable'],
      explanation: 'Pro users get sophisticated industry terminology that sets them apart from other candidates.'
    }
  ];

  useEffect(() => {
    // Simulate auto-applying smart enhancements
    const applyEnhancements = async () => {
      setProcessing(true);
      
      for (let i = 0; i < smartEnhancements.length; i++) {
        setCurrentStep(i);
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        setAppliedEnhancements(prev => [...prev, smartEnhancements[i]]);
        
        // Update ATS score
        if (atsScore) {
          const totalImpact = smartEnhancements.slice(0, i + 1).reduce((sum, enh) => sum + enh.impact, 0);
          const newScore = {
            ...atsScore,
            current: Math.min(100, atsScore.current + totalImpact),
            improvement: totalImpact,
            lastUpdated: new Date().toISOString()
          };
          onScoreUpdate?.(newScore);
        }
      }
      
      setProcessing(false);
    };

    applyEnhancements();
  }, [atsScore, onScoreUpdate]);

  const getTotalFreeImpact = () => {
    return appliedEnhancements.reduce((sum, enh) => sum + enh.impact, 0);
  };

  const getTotalProImpact = () => {
    return proFeaturesPreview.reduce((sum, enh) => sum + enh.impact, 0);
  };

  const getPotentialScore = () => {
    if (!atsScore) return 0;
    return Math.min(100, atsScore.current + getTotalProImpact());
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Header */}
      <motion.div variants={staggerItem}>
        <div className="text-center">
          <h3 className="text-xl font-semibold text-gray-900 flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5" />
            Smart Enhancement Applied
          </h3>
          <p className="text-gray-600 mt-1">
            We've automatically optimized your resume with essential improvements
          </p>
        </div>
      </motion.div>

      {/* Processing Status */}
      {processing && (
        <motion.div variants={staggerItem}>
          <EnhancedCard>
            <EnhancedCardContent className="py-8">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
                  <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">
                    Applying Enhancement {currentStep + 1} of {smartEnhancements.length}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {smartEnhancements[currentStep]?.title}
                  </p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 max-w-xs mx-auto">
                  <motion.div
                    className="bg-blue-600 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${((currentStep + 1) / smartEnhancements.length) * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>
            </EnhancedCardContent>
          </EnhancedCard>
        </motion.div>
      )}

      {/* Applied Enhancements */}
      {!processing && appliedEnhancements.length > 0 && (
        <motion.div variants={staggerItem}>
          <EnhancedCard>
            <EnhancedCardHeader>
              <EnhancedCardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Enhancements Applied
              </EnhancedCardTitle>
              <EnhancedCardDescription>
                Your resume has been automatically optimized with these improvements
              </EnhancedCardDescription>
            </EnhancedCardHeader>
            
            <EnhancedCardContent>
              <div className="space-y-4">
                {appliedEnhancements.map((enhancement, index) => (
                  <motion.div
                    key={enhancement.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border border-green-200 rounded-lg p-4 bg-green-50"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle className="w-4 h-4 text-green-600" />
                          <h4 className="font-medium text-gray-900">{enhancement.title}</h4>
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                            +{enhancement.impact} points
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{enhancement.description}</p>
                        <p className="text-sm text-green-700 bg-green-100 rounded p-2">
                          <strong>What we did:</strong> {enhancement.explanation}
                        </p>
                      </div>
                    </div>
                    
                    {/* Before/After Preview */}
                    {enhancement.beforeText && enhancement.afterText && (
                      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <h5 className="text-xs font-medium text-gray-700 mb-1">Before</h5>
                          <div className="p-2 bg-red-50 border border-red-200 rounded text-xs text-gray-700">
                            {enhancement.beforeText}
                          </div>
                        </div>
                        <div>
                          <h5 className="text-xs font-medium text-gray-700 mb-1">After</h5>
                          <div className="p-2 bg-green-100 border border-green-300 rounded text-xs text-gray-700">
                            {enhancement.afterText}
                          </div>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
              
              {/* Summary */}
              <div className="mt-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600 mb-1">+{getTotalFreeImpact()}</div>
                  <div className="text-sm text-gray-600">Total ATS Score Improvement</div>
                </div>
              </div>
            </EnhancedCardContent>
          </EnhancedCard>
        </motion.div>
      )}

      {/* Pro Features Preview */}
      {!processing && (
        <motion.div variants={staggerItem}>
          <EnhancedCard>
            <EnhancedCardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <EnhancedCardTitle className="flex items-center gap-2">
                    <Crown className="w-5 h-5 text-purple-600" />
                    See What Pro Can Do
                  </EnhancedCardTitle>
                  <EnhancedCardDescription>
                    Unlock advanced enhancements for even better results
                  </EnhancedCardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowProPreview(!showProPreview)}
                  className="text-purple-600 border-purple-300"
                >
                  {showProPreview ? 'Hide Preview' : 'Show Preview'}
                </Button>
              </div>
            </EnhancedCardHeader>
            
            <EnhancedCardContent>
              {/* Score Comparison */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{atsScore?.current || 67}</div>
                  <div className="text-sm text-gray-600">Current Score</div>
                  <div className="text-xs text-green-600">+{getTotalFreeImpact()} from free enhancements</div>
                </div>
                <div className="flex items-center justify-center">
                  <ArrowRight className="w-6 h-6 text-purple-600" />
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{getPotentialScore()}</div>
                  <div className="text-sm text-gray-600">Pro Potential</div>
                  <div className="text-xs text-purple-600">+{getTotalProImpact()} additional points</div>
                </div>
              </div>

              {/* Pro Features List */}
              <AnimatePresence>
                {showProPreview && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="space-y-4 mb-6">
                      {proFeaturesPreview.map((feature, index) => (
                        <motion.div
                          key={feature.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="border-2 border-dashed border-purple-200 rounded-lg p-4 bg-purple-50"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Crown className="w-4 h-4 text-purple-600" />
                                <h4 className="font-medium text-purple-900">{feature.title}</h4>
                                <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-full">
                                  +{feature.impact} points
                                </span>
                                <TierBadge tier="pro" size="sm" />
                              </div>
                              <p className="text-sm text-purple-700 mb-3">{feature.description}</p>
                              <p className="text-sm text-purple-800 bg-purple-100 rounded p-2">
                                <strong>Pro Enhancement:</strong> {feature.explanation}
                              </p>
                            </div>
                          </div>
                          
                          {/* Pro Before/After Preview */}
                          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                              <h5 className="text-xs font-medium text-purple-700 mb-1">Current</h5>
                              <div className="p-2 bg-white border border-purple-200 rounded text-xs text-gray-700">
                                {feature.beforeText}
                              </div>
                            </div>
                            <div>
                              <h5 className="text-xs font-medium text-purple-700 mb-1">With Pro</h5>
                              <div className="p-2 bg-purple-100 border border-purple-300 rounded text-xs text-purple-800">
                                {feature.afterText}
                              </div>
                            </div>
                          </div>
                          
                          {/* Keywords */}
                          {feature.keywords.length > 0 && (
                            <div className="mt-3">
                              <h5 className="text-xs font-medium text-purple-700 mb-1">Added Keywords</h5>
                              <div className="flex flex-wrap gap-1">
                                {feature.keywords.map((keyword, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-1 bg-purple-200 text-purple-800 text-xs rounded"
                                  >
                                    {keyword}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Upgrade CTA */}
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6 text-white text-center">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold">Unlock Your Full Potential</h3>
                    <p className="text-purple-100">
                      Get +{getTotalProImpact()} additional points with Pro enhancements
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-300" />
                      <span>Bullet-by-bullet control</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-300" />
                      <span>Advanced keyword optimization</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-300" />
                      <span>Real-time impact preview</span>
                    </div>
                  </div>
                  
                  <Button
                    onClick={onUpgradeClick}
                    className="bg-white text-purple-600 hover:bg-gray-100 font-semibold px-8 py-3"
                  >
                    <Crown className="w-4 h-4 mr-2" />
                    Upgrade to Pro
                  </Button>
                  
                  <p className="text-xs text-purple-200">
                    Potential score: {getPotentialScore()}/100 (+{getTotalProImpact()} points improvement)
                  </p>
                </div>
              </div>
            </EnhancedCardContent>
          </EnhancedCard>
        </motion.div>
      )}
    </motion.div>
  );
}

/**
 * ProUserPrecisionExperience Component
 * Subtask 5.4: Full bullet-by-bullet enhancement control for Pro users
 */
function ProUserPrecisionExperience({
  resumeData,
  jobData,
  atsScore,
  onEnhancementChange,
  onScoreUpdate,
  className = ''
}) {
  const [selectedBullets, setSelectedBullets] = useState(new Set());
  const [bulletEnhancements, setBulletEnhancements] = useState({});
  const [showAdvancedAnalytics, setShowAdvancedAnalytics] = useState(false);
  const [customEnhancements, setCustomEnhancements] = useState({});
  const [activeSection, setActiveSection] = useState('experience');

  // Mock resume sections with bullets for Pro enhancement
  const resumeSections = {
    experience: {
      title: 'Work Experience',
      icon: Award,
      bullets: [
        {
          id: 'exp-1',
          original: 'Developed web applications for clients',
          section: 'Software Engineer at TechCorp (2020-2023)',
          relevance: 85,
          currentEnhancement: null,
          enhancements: {
            light: {
              text: 'Developed responsive web applications for enterprise clients using modern frameworks',
              impact: 5,
              keywords: ['responsive', 'enterprise', 'modern frameworks'],
              confidence: 88
            },
            medium: {
              text: 'Engineered scalable React applications for 15+ enterprise clients, improving load times by 60%',
              impact: 12,
              keywords: ['React', 'scalable', 'enterprise', 'performance'],
              confidence: 92
            },
            heavy: {
              text: 'Architected enterprise-grade React applications serving 50K+ users with 99.9% uptime, resulting in 40% performance improvement and $2M revenue impact',
              impact: 20,
              keywords: ['React', 'enterprise-grade', 'scalable', 'performance', 'revenue impact'],
              confidence: 95
            }
          }
        },
        {
          id: 'exp-2',
          original: 'Worked with team members on various projects',
          section: 'Software Engineer at TechCorp (2020-2023)',
          relevance: 72,
          currentEnhancement: null,
          enhancements: {
            light: {
              text: 'Collaborated with cross-functional team members on software development projects',
              impact: 4,
              keywords: ['collaborated', 'cross-functional', 'software development'],
              confidence: 85
            },
            medium: {
              text: 'Led cross-functional team of 8 developers in agile software development, delivering 12+ projects on time',
              impact: 10,
              keywords: ['led', 'cross-functional', 'agile', 'delivered'],
              confidence: 90
            },
            heavy: {
              text: 'Spearheaded cross-functional team of 8+ engineers using Agile methodologies, delivering 12+ high-impact projects with 95% on-time delivery rate and 30% faster sprint cycles',
              impact: 18,
              keywords: ['spearheaded', 'cross-functional', 'Agile', 'high-impact', 'delivery rate'],
              confidence: 93
            }
          }
        },
        {
          id: 'exp-3',
          original: 'Improved system performance',
          section: 'Software Engineer at TechCorp (2020-2023)',
          relevance: 90,
          currentEnhancement: null,
          enhancements: {
            light: {
              text: 'Improved system performance through code optimization and best practices',
              impact: 6,
              keywords: ['performance', 'optimization', 'best practices'],
              confidence: 87
            },
            medium: {
              text: 'Optimized system performance by 45%, reducing API response times from 2.1s to 1.2s through database indexing',
              impact: 13,
              keywords: ['optimized', 'performance', 'API response', 'database indexing'],
              confidence: 91
            },
            heavy: {
              text: 'Architected performance optimization strategy achieving 45% improvement in system throughput, reducing API response times from 2.1s to 1.2s and database query times by 60%, supporting 3x user growth',
              impact: 22,
              keywords: ['architected', 'performance optimization', 'system throughput', 'API response', 'database query', 'user growth'],
              confidence: 96
            }
          }
        }
      ]
    },
    summary: {
      title: 'Professional Summary',
      icon: FileText,
      bullets: [
        {
          id: 'sum-1',
          original: 'Software engineer with experience in web development.',
          section: 'Professional Summary',
          relevance: 75,
          currentEnhancement: null,
          enhancements: {
            light: {
              text: 'Experienced software engineer specializing in modern web development technologies.',
              impact: 4,
              keywords: ['experienced', 'specializing', 'modern web development'],
              confidence: 82
            },
            medium: {
              text: 'Senior software engineer with 5+ years building scalable React applications and leading development teams.',
              impact: 11,
              keywords: ['senior', 'scalable', 'React', 'leading'],
              confidence: 89
            },
            heavy: {
              text: 'Senior full-stack software engineer with 5+ years architecting scalable React applications, leading cross-functional teams of 8+ developers, and driving 40% performance improvements across enterprise systems.',
              impact: 19,
              keywords: ['senior', 'full-stack', 'architecting', 'scalable', 'React', 'leading', 'cross-functional', 'performance improvements', 'enterprise'],
              confidence: 94
            }
          }
        }
      ]
    }
  };

  const enhancementLevels = [
    {
      id: 'light',
      name: 'Light',
      description: 'Minimal changes, preserve original tone',
      color: 'green',
      icon: '🌱'
    },
    {
      id: 'medium',
      name: 'Medium',
      description: 'Moderate enhancement with metrics',
      color: 'blue',
      icon: '⚡'
    },
    {
      id: 'heavy',
      name: 'Heavy',
      description: 'Maximum impact with strong language',
      color: 'purple',
      icon: '🚀'
    }
  ];

  const handleBulletEnhancement = (bulletId, level) => {
    const bullet = findBulletById(bulletId);
    if (!bullet) return;

    const enhancement = bullet.enhancements[level];
    setBulletEnhancements(prev => ({
      ...prev,
      [bulletId]: { level, enhancement }
    }));

    // Update ATS score
    if (atsScore) {
      const totalImpact = Object.values(bulletEnhancements).reduce((sum, enh) => sum + (enh.enhancement?.impact || 0), 0) + enhancement.impact;
      const newScore = {
        ...atsScore,
        current: Math.min(100, atsScore.current + totalImpact),
        improvement: totalImpact,
        lastUpdated: new Date().toISOString()
      };
      onScoreUpdate?.(newScore);
    }

    onEnhancementChange?.({ bulletId, level, enhancement });
  };

  const handleCustomEnhancement = (bulletId, customText) => {
    setCustomEnhancements(prev => ({
      ...prev,
      [bulletId]: customText
    }));
  };

  const findBulletById = (bulletId) => {
    for (const section of Object.values(resumeSections)) {
      const bullet = section.bullets.find(b => b.id === bulletId);
      if (bullet) return bullet;
    }
    return null;
  };

  const getTotalImpact = () => {
    return Object.values(bulletEnhancements).reduce((sum, enh) => sum + (enh.enhancement?.impact || 0), 0);
  };

  const getEnhancedBulletsCount = () => {
    return Object.keys(bulletEnhancements).length;
  };

  const getAllKeywords = () => {
    const keywords = new Set();
    Object.values(bulletEnhancements).forEach(enh => {
      enh.enhancement?.keywords?.forEach(keyword => keywords.add(keyword));
    });
    return Array.from(keywords);
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Header */}
      <motion.div variants={staggerItem}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Edit3 className="w-5 h-5" />
              Bullet-by-Bullet Enhancement
              <TierBadge tier="pro" size="sm" />
            </h3>
            <p className="text-gray-600">
              Fine-tune every bullet point with precision control and real-time impact scoring
            </p>
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAdvancedAnalytics(!showAdvancedAnalytics)}
            className={showAdvancedAnalytics ? 'bg-purple-50 text-purple-700 border-purple-300' : ''}
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            Advanced Analytics
          </Button>
        </div>
      </motion.div>

      {/* Enhancement Summary */}
      {getEnhancedBulletsCount() > 0 && (
        <motion.div variants={staggerItem}>
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{getEnhancedBulletsCount()}</div>
                <div className="text-sm text-gray-600">Bullets Enhanced</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">+{getTotalImpact()}</div>
                <div className="text-sm text-gray-600">Total Impact</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{getAllKeywords().length}</div>
                <div className="text-sm text-gray-600">Keywords Added</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-amber-600">
                  {Math.round(Object.values(bulletEnhancements).reduce((sum, enh) => sum + (enh.enhancement?.confidence || 0), 0) / getEnhancedBulletsCount()) || 0}%
                </div>
                <div className="text-sm text-gray-600">Avg Confidence</div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Advanced Analytics */}
      <AnimatePresence>
        {showAdvancedAnalytics && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  Advanced Analytics & Insights
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              
              <EnhancedCardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Keyword Analysis */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Keyword Analysis</h4>
                    <div className="space-y-2">
                      {getAllKeywords().slice(0, 8).map((keyword, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">{keyword}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-1">
                              <div 
                                className="bg-blue-600 h-1 rounded-full" 
                                style={{ width: `${Math.random() * 100}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-500">{Math.floor(Math.random() * 100)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Impact Distribution */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Impact Distribution</h4>
                    <div className="space-y-2">
                      {enhancementLevels.map((level) => {
                        const count = Object.values(bulletEnhancements).filter(enh => enh.level === level.id).length;
                        const percentage = getEnhancedBulletsCount() > 0 ? (count / getEnhancedBulletsCount()) * 100 : 0;
                        
                        return (
                          <div key={level.id} className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-sm">{level.icon}</span>
                              <span className="text-sm text-gray-700">{level.name} Enhancement</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="w-16 bg-gray-200 rounded-full h-1">
                                <div 
                                  className={`h-1 rounded-full ${
                                    level.color === 'green' ? 'bg-green-600' :
                                    level.color === 'blue' ? 'bg-blue-600' :
                                    'bg-purple-600'
                                  }`}
                                  style={{ width: `${percentage}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-500">{count}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </EnhancedCardContent>
            </EnhancedCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Section Tabs */}
      <motion.div variants={staggerItem}>
        <div className="flex items-center gap-2 border-b border-gray-200">
          {Object.entries(resumeSections).map(([sectionId, section]) => {
            const Icon = section.icon;
            const isActive = activeSection === sectionId;
            
            return (
              <button
                key={sectionId}
                onClick={() => setActiveSection(sectionId)}
                className={`
                  flex items-center gap-2 px-4 py-2 border-b-2 transition-colors
                  ${isActive 
                    ? 'border-blue-500 text-blue-600 bg-blue-50' 
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{section.title}</span>
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                  {section.bullets.length}
                </span>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Bullet Enhancement Interface */}
      <motion.div variants={staggerItem}>
        <div className="space-y-6">
          {resumeSections[activeSection]?.bullets.map((bullet, index) => {
            const currentEnhancement = bulletEnhancements[bullet.id];
            const customText = customEnhancements[bullet.id];
            
            return (
              <motion.div
                key={bullet.id}
                variants={staggerItem}
                className="border border-gray-200 rounded-lg overflow-hidden"
              >
                <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">
                        Bullet Point {index + 1} of {resumeSections[activeSection].bullets.length}
                      </h4>
                      <p className="text-sm text-gray-600">{bullet.section}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="text-sm text-gray-500">Job Relevance</div>
                        <div className="flex items-center gap-1">
                          <div className="text-lg font-bold text-green-600">{bullet.relevance}%</div>
                          <div className="flex">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`w-3 h-3 ${
                                  i < Math.floor(bullet.relevance / 20) 
                                    ? 'text-yellow-400 fill-current' 
                                    : 'text-gray-300'
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="p-4">
                  {/* Original Text */}
                  <div className="mb-4">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Original Text</h5>
                    <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-gray-700">
                      {bullet.original}
                    </div>
                  </div>
                  
                  {/* Enhancement Options */}
                  <div className="mb-4">
                    <h5 className="text-sm font-medium text-gray-700 mb-3">Enhancement Options</h5>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {enhancementLevels.map((level) => {
                        const enhancement = bullet.enhancements[level.id];
                        const isSelected = currentEnhancement?.level === level.id;
                        
                        return (
                          <motion.div
                            key={level.id}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className={`
                              border-2 rounded-lg p-3 cursor-pointer transition-all
                              ${isSelected 
                                ? `border-${level.color}-500 bg-${level.color}-50` 
                                : 'border-gray-200 hover:border-gray-300'
                              }
                            `}
                            onClick={() => handleBulletEnhancement(bullet.id, level.id)}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">{level.icon}</span>
                                <span className="font-medium text-gray-900">{level.name}</span>
                              </div>
                              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                                +{enhancement.impact} pts
                              </span>
                            </div>
                            
                            <p className="text-xs text-gray-600 mb-3">{level.description}</p>
                            
                            <div className="text-sm text-gray-700 mb-3 line-clamp-3">
                              {enhancement.text}
                            </div>
                            
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-gray-500">
                                {enhancement.keywords.length} keywords
                              </span>
                              <span className="text-gray-500">
                                {enhancement.confidence}% confident
                              </span>
                            </div>
                            
                            {isSelected && (
                              <div className="mt-2 pt-2 border-t border-gray-200">
                                <div className="flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3 text-green-600" />
                                  <span className="text-xs text-green-700 font-medium">Applied</span>
                                </div>
                              </div>
                            )}
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>
                  
                  {/* Custom Enhancement */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="text-sm font-medium text-gray-700">Custom Enhancement</h5>
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-full">
                        Pro Feature
                      </span>
                    </div>
                    <textarea
                      value={customText || ''}
                      onChange={(e) => handleCustomEnhancement(bullet.id, e.target.value)}
                      placeholder="Write your own enhancement for this bullet point..."
                      className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                      rows={3}
                    />
                    {customText && (
                      <div className="mt-2 flex justify-end">
                        <Button
                          size="sm"
                          className="bg-purple-600 text-white hover:bg-purple-700"
                        >
                          Apply Custom Enhancement
                        </Button>
                      </div>
                    )}
                  </div>
                  
                  {/* Current Enhancement Display */}
                  {currentEnhancement && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="text-sm font-medium text-green-800">Current Enhancement</h5>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-green-700">
                            {currentEnhancement.level.charAt(0).toUpperCase() + currentEnhancement.level.slice(1)} Level
                          </span>
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                            +{currentEnhancement.enhancement.impact} points
                          </span>
                        </div>
                      </div>
                      <div className="text-sm text-green-700 mb-2">
                        {currentEnhancement.enhancement.text}
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {currentEnhancement.enhancement.keywords.map((keyword, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-green-200 text-green-800 text-xs rounded"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </motion.div>
  );
}

/**
 * Main PrecisionModeInterface Component
 */
export function PrecisionModeInterface({
  resumeData,
  jobData,
  onEnhancementChange,
  onScoreUpdate,
  onBackToModeSelection,
  className = ''
}) {
  const { user, tier, weeklyUsage, weeklyLimit } = useUserStore();
  const { precisionSettings, updatePrecisionSettings } = useProcessingStore();
  const { updateProcessingUI } = useUIStore();
  const { atsScores, updateATSScore } = useAnalyticsStore();

  const [currentStep, setCurrentStep] = useState('analysis'); // analysis, enhancement, preview
  const [atsScore, setATSScore] = useState(null);
  const [loading, setLoading] = useState(false);

  const isProUser = tier === 'pro';
  const jobId = jobData?.id || 'current-job';
  const currentATSScore = atsScores[jobId] || atsScore;

  useEffect(() => {
    // Initialize with mock ATS score
    const mockScore = {
      current: 67,
      potential: 94,
      improvement: 27,
      sectionScores: {
        contact: { score: 100, maxScore: 100, status: 'perfect' },
        summary: { score: 45, maxScore: 100, status: 'needs-keywords' },
        experience: { score: 78, maxScore: 100, status: 'good-can-enhance' },
        skills: { score: 0, maxScore: 100, status: 'missing' },
        education: { score: 65, maxScore: 100, status: 'basic-format' },
        achievements: { score: 0, maxScore: 100, status: 'missing' }
      },
      confidenceLevel: 'high',
      lastUpdated: new Date().toISOString()
    };
    
    setATSScore(mockScore);
    updateATSScore(jobId, mockScore);
  }, [jobId, updateATSScore]);

  const handleScoreUpdate = useCallback((newScore) => {
    setATSScore(newScore);
    updateATSScore(jobId, newScore);
    onScoreUpdate?.(newScore);
  }, [jobId, updateATSScore, onScoreUpdate]);

  const handleStepChange = (step) => {
    setCurrentStep(step);
    updateProcessingUI({ activeStep: step });
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Header */}
      <motion.div variants={staggerItem}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Settings className="w-6 h-6" />
              Precision Mode
              {!isProUser && <TierBadge tier="pro" size="sm" />}
            </h2>
            <p className="text-gray-600 mt-1">
              Granular control over every enhancement with real-time impact preview
            </p>
          </div>
          <Button
            variant="outline"
            onClick={onBackToModeSelection}
          >
            Back to Mode Selection
          </Button>
        </div>
      </motion.div>

      {/* Step Navigation */}
      <motion.div variants={staggerItem}>
        <div className="flex items-center justify-center">
          <div className="flex items-center space-x-4">
            {[
              { id: 'analysis', name: 'Analysis', icon: BarChart3 },
              { id: 'enhancement', name: 'Enhancement', icon: Sparkles },
              { id: 'preview', name: 'Preview', icon: Eye }
            ].map((step, index) => {
              const Icon = step.icon;
              const isActive = currentStep === step.id;
              const isCompleted = ['analysis', 'enhancement'].indexOf(currentStep) > ['analysis', 'enhancement'].indexOf(step.id);
              
              return (
                <React.Fragment key={step.id}>
                  <button
                    onClick={() => handleStepChange(step.id)}
                    className={`
                      flex items-center gap-2 px-4 py-2 rounded-lg transition-all
                      ${isActive 
                        ? 'bg-blue-100 text-blue-700 border border-blue-300' 
                        : isCompleted
                        ? 'bg-green-100 text-green-700 border border-green-300'
                        : 'bg-gray-100 text-gray-600 border border-gray-300 hover:bg-gray-200'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{step.name}</span>
                    {isCompleted && <CheckCircle className="w-4 h-4" />}
                  </button>
                  {index < 2 && (
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <AnimatePresence mode="wait">
        {currentStep === 'analysis' && (
          <motion.div
            key="analysis"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <ResumeAnalysisDashboard
              resumeData={resumeData}
              jobData={jobData}
              atsScore={currentATSScore}
              onScoreUpdate={handleScoreUpdate}
              isProUser={isProUser}
            />
            
            <div className="flex justify-end mt-6">
              <Button
                onClick={() => handleStepChange('enhancement')}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
              >
                Continue to Enhancement
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </motion.div>
        )}

        {currentStep === 'enhancement' && (
          <motion.div
            key="enhancement"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            {isProUser ? (
              <>
                <div className="space-y-6">
                  <DynamicEnhancementSelection
                    resumeData={resumeData}
                    jobData={jobData}
                    atsScore={currentATSScore}
                    onEnhancementChange={onEnhancementChange}
                    onScoreUpdate={handleScoreUpdate}
                    isProUser={isProUser}
                    onUpgradeClick={() => {
                      // Handle upgrade click - could open upgrade modal
                      console.log('Upgrade clicked');
                    }}
                  />
                  
                  <ProUserPrecisionExperience
                    resumeData={resumeData}
                    jobData={jobData}
                    atsScore={currentATSScore}
                    onEnhancementChange={onEnhancementChange}
                    onScoreUpdate={handleScoreUpdate}
                  />
                </div>
                
                <div className="flex justify-between mt-6">
                  <Button
                    variant="outline"
                    onClick={() => handleStepChange('analysis')}
                  >
                    Back to Analysis
                  </Button>
                  <Button
                    onClick={() => handleStepChange('preview')}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                  >
                    Continue to Preview
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </>
            ) : (
              <>
                <FreeUserPrecisionExperience
                  resumeData={resumeData}
                  jobData={jobData}
                  atsScore={currentATSScore}
                  onScoreUpdate={handleScoreUpdate}
                  onUpgradeClick={() => {
                    // Handle upgrade click - could open upgrade modal
                    console.log('Upgrade clicked');
                  }}
                />
                
                <div className="flex justify-between mt-6">
                  <Button
                    variant="outline"
                    onClick={() => handleStepChange('analysis')}
                  >
                    Back to Analysis
                  </Button>
                  <Button
                    onClick={() => handleStepChange('preview')}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                  >
                    Continue to Preview
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </>
            )}
          </motion.div>
        )}

        {currentStep === 'preview' && (
          <motion.div
            key="preview"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            {/* Placeholder for preview - will be implemented in later subtasks */}
            <EnhancedCard>
              <EnhancedCardContent className="text-center py-12">
                <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Real-time Preview</h3>
                <p className="text-gray-600">
                  Real-time impact preview will be implemented in later subtasks
                </p>
              </EnhancedCardContent>
            </EnhancedCard>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default PrecisionModeInterface;