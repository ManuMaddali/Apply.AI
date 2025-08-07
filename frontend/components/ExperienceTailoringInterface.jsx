/**
 * ExperienceTailoringInterface Component
 * Implements bullet-by-bullet enhancement control with real-time impact preview
 * Handles job relevance scoring, enhancement impact visualization, and tier-based features
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Edit3,
  Eye,
  Target,
  TrendingUp,
  BarChart3,
  Star,
  Award,
  Zap,
  Brain,
  Lightbulb,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Plus,
  Minus,
  RefreshCw,
  Crown,
  Sparkles,
  Clock,
  Users,
  FileText,
  Settings,
  Info,
  Search,
  Filter
} from 'lucide-react';
import { Button } from './ui/button';
import { EnhancedCard, EnhancedCardHeader, EnhancedCardTitle, EnhancedCardDescription, EnhancedCardContent, EnhancedCardFooter } from './ui/enhanced-card';
import { TierBadge } from './ui/tier-badge';
import { UpgradePrompt } from './UpgradePrompt';
import { useUserStore, useProcessingStore, useUIStore, useAnalyticsStore } from '../lib/store';
import { fadeInUp, staggerContainer, staggerItem, hoverLift, scaleIn } from '../lib/motion';

/**
 * BulletEnhancementInterface Component
 * Subtask 6.1: Individual bullet point enhancement options with Light, Medium, Heavy levels
 */
function BulletEnhancementInterface({
  experienceItem,
  bulletIndex,
  bulletText,
  jobRelevance,
  onEnhancementChange,
  onImpactUpdate,
  isProUser,
  onUpgradeClick,
  className = ''
}) {
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [customEdit, setCustomEdit] = useState(false);
  const [customText, setCustomText] = useState(bulletText);
  const [enhancementOptions, setEnhancementOptions] = useState([]);
  const [keywordAnalysis, setKeywordAnalysis] = useState({});
  const [impactScore, setImpactScore] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  // Mock enhancement options - in real implementation, this would come from API
  const mockEnhancementOptions = useMemo(() => [
    {
      level: 'light',
      impact: 5,
      text: `Developed responsive web applications for enterprise clients using modern frameworks`,
      keywords: ['responsive', 'enterprise', 'modern frameworks'],
      metrics: [],
      confidence: 85,
      estimatedTime: 1,
      description: 'Light enhancement with basic keyword optimization'
    },
    {
      level: 'medium',
      impact: 12,
      text: `Engineered scalable React applications for 15+ enterprise clients, improving load times by 60%`,
      keywords: ['engineered', 'scalable', 'React', 'enterprise'],
      metrics: ['15+ clients', '60% improvement'],
      confidence: 92,
      estimatedTime: 2,
      description: 'Balanced enhancement with metrics and stronger language',
      recommended: true
    },
    {
      level: 'heavy',
      impact: 20,
      text: `Architected enterprise-grade React applications serving 50K+ users with 99.9% uptime, resulting in 40% performance improvement and $2M revenue impact`,
      keywords: ['architected', 'enterprise-grade', 'React', 'scalable', 'performance'],
      metrics: ['50K+ users', '99.9% uptime', '40% improvement', '$2M revenue'],
      confidence: 88,
      estimatedTime: 3,
      description: 'Heavy rewriting with maximum keyword optimization and quantified impact',
      proOnly: !isProUser
    }
  ], [isProUser]);

  useEffect(() => {
    setEnhancementOptions(mockEnhancementOptions);
  }, [mockEnhancementOptions]);

  const handleLevelSelect = useCallback(async (level) => {
    if (level === 'heavy' && !isProUser) {
      onUpgradeClick?.();
      return;
    }

    setIsProcessing(true);
    setSelectedLevel(level);
    
    const selectedOption = enhancementOptions.find(opt => opt.level === level);
    if (selectedOption) {
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 800));
      
      setImpactScore(selectedOption.impact);
      setKeywordAnalysis({
        added: selectedOption.keywords,
        metrics: selectedOption.metrics,
        confidence: selectedOption.confidence
      });
      
      onEnhancementChange?.({
        bulletIndex,
        level,
        originalText: bulletText,
        enhancedText: selectedOption.text,
        impact: selectedOption.impact,
        keywords: selectedOption.keywords,
        metrics: selectedOption.metrics
      });
      
      onImpactUpdate?.({
        bulletIndex,
        impact: selectedOption.impact,
        type: 'enhancement'
      });
    }
    
    setIsProcessing(false);
  }, [enhancementOptions, isProUser, bulletIndex, bulletText, onEnhancementChange, onImpactUpdate, onUpgradeClick]);

  const handleCustomEdit = useCallback(() => {
    setCustomEdit(true);
    setCustomText(selectedLevel ? enhancementOptions.find(opt => opt.level === selectedLevel)?.text || bulletText : bulletText);
  }, [selectedLevel, enhancementOptions, bulletText]);

  const handleCustomSave = useCallback(async () => {
    if (!isProUser) {
      onUpgradeClick?.();
      return;
    }

    setIsProcessing(true);
    
    // Simulate API call for custom enhancement analysis
    await new Promise(resolve => setTimeout(resolve, 1200));
    
    const estimatedImpact = Math.floor(Math.random() * 15) + 5; // 5-20 points
    const extractedKeywords = ['custom', 'enhanced', 'optimized']; // Mock keyword extraction
    
    setImpactScore(estimatedImpact);
    setKeywordAnalysis({
      added: extractedKeywords,
      metrics: [],
      confidence: 75
    });
    
    onEnhancementChange?.({
      bulletIndex,
      level: 'custom',
      originalText: bulletText,
      enhancedText: customText,
      impact: estimatedImpact,
      keywords: extractedKeywords,
      metrics: []
    });
    
    onImpactUpdate?.({
      bulletIndex,
      impact: estimatedImpact,
      type: 'custom'
    });
    
    setCustomEdit(false);
    setSelectedLevel('custom');
    setIsProcessing(false);
  }, [isProUser, customText, bulletIndex, bulletText, onEnhancementChange, onImpactUpdate, onUpgradeClick]);

  const getImpactColor = (impact) => {
    if (impact >= 15) return 'text-green-600 bg-green-50 border-green-200';
    if (impact >= 10) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (impact >= 5) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-gray-600 bg-gray-50 border-gray-200';
  };

  const getLevelColor = (level) => {
    const colors = {
      light: 'border-blue-200 bg-blue-50 text-blue-700',
      medium: 'border-purple-200 bg-purple-50 text-purple-700',
      heavy: 'border-green-200 bg-green-50 text-green-700',
      custom: 'border-orange-200 bg-orange-50 text-orange-700'
    };
    return colors[level] || colors.light;
  };

  return (
    <motion.div
      variants={staggerItem}
      className={`space-y-4 ${className}`}
    >
      <EnhancedCard>
        <EnhancedCardHeader>
          <div className="flex items-center justify-between">
            <div>
              <EnhancedCardTitle className="flex items-center gap-2">
                <Edit3 className="w-5 h-5" />
                Bullet Point {bulletIndex + 1}
                {jobRelevance && (
                  <div className="flex items-center gap-1 ml-2">
                    <Star className="w-4 h-4 text-amber-500" />
                    <span className="text-sm text-amber-600 font-medium">
                      {jobRelevance}% relevant
                    </span>
                  </div>
                )}
              </EnhancedCardTitle>
              <EnhancedCardDescription>
                Choose enhancement level or create custom version
              </EnhancedCardDescription>
            </div>
            
            {selectedLevel && (
              <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getImpactColor(impactScore)}`}>
                +{impactScore} points
              </div>
            )}
          </div>
        </EnhancedCardHeader>

        <EnhancedCardContent>
          {/* Original Text */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Current Text</span>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
              <p className="text-gray-800">{bulletText}</p>
            </div>
          </div>

          {/* Enhancement Options */}
          <div className="space-y-4 mb-6">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-gray-700">Enhancement Options</span>
            </div>

            {enhancementOptions.map((option) => (
              <motion.div
                key={option.level}
                variants={staggerItem}
                className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                  selectedLevel === option.level
                    ? getLevelColor(option.level)
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                } ${option.proOnly ? 'opacity-75' : ''}`}
                onClick={() => handleLevelSelect(option.level)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      option.level === 'light' ? 'bg-blue-100 text-blue-700' :
                      option.level === 'medium' ? 'bg-purple-100 text-purple-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {option.level.charAt(0).toUpperCase() + option.level.slice(1)}
                    </div>
                    
                    {option.recommended && (
                      <div className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs font-medium">
                        Recommended
                      </div>
                    )}
                    
                    {option.proOnly && (
                      <div className="flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-medium">
                        <Crown className="w-3 h-3" />
                        Pro Only
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <div className={`px-2 py-1 rounded text-xs font-medium ${getImpactColor(option.impact)}`}>
                      +{option.impact} pts
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      {option.estimatedTime}min
                    </div>
                  </div>
                </div>

                <p className="text-sm text-gray-600 mb-3">{option.description}</p>

                <div className="p-3 bg-white rounded border border-gray-100">
                  <p className="text-gray-800 text-sm">{option.text}</p>
                </div>

                {/* Keywords and Metrics Preview */}
                {(option.keywords.length > 0 || option.metrics.length > 0) && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {option.keywords.length > 0 && (
                        <div>
                          <div className="text-xs font-medium text-gray-600 mb-2">Keywords Added</div>
                          <div className="flex flex-wrap gap-1">
                            {option.keywords.map((keyword, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {option.metrics.length > 0 && (
                        <div>
                          <div className="text-xs font-medium text-gray-600 mb-2">Metrics Added</div>
                          <div className="flex flex-wrap gap-1">
                            {option.metrics.map((metric, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs"
                              >
                                {metric}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Confidence Score */}
                <div className="mt-3 flex items-center gap-2">
                  <div className="flex items-center gap-1">
                    <Target className="w-3 h-3 text-gray-500" />
                    <span className="text-xs text-gray-600">Confidence: {option.confidence}%</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Custom Edit Option */}
          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-orange-500" />
                <span className="text-sm font-medium text-gray-700">Custom Enhancement</span>
                {!isProUser && (
                  <div className="flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-medium">
                    <Crown className="w-3 h-3" />
                    Pro Only
                  </div>
                )}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleCustomEdit}
                disabled={!isProUser}
                className="text-orange-600 border-orange-300"
              >
                <Edit3 className="w-4 h-4 mr-2" />
                Custom Edit
              </Button>
            </div>

            <AnimatePresence>
              {customEdit && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <div className="space-y-4">
                    <textarea
                      value={customText}
                      onChange={(e) => setCustomText(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      rows={4}
                      placeholder="Write your custom enhancement..."
                    />
                    
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={handleCustomSave}
                        disabled={isProcessing || !customText.trim()}
                        className="bg-orange-600 hover:bg-orange-700"
                      >
                        {isProcessing ? (
                          <>
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Apply Custom
                          </>
                        )}
                      </Button>
                      
                      <Button
                        variant="outline"
                        onClick={() => setCustomEdit(false)}
                        disabled={isProcessing}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Processing Indicator */}
          <AnimatePresence>
            {isProcessing && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex items-center justify-center py-4"
              >
                <div className="flex items-center gap-2 text-blue-600">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Processing enhancement...</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </EnhancedCardContent>

        {/* Applied Enhancement Summary */}
        {selectedLevel && !isProcessing && (
          <EnhancedCardFooter>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-700 font-medium">
                  {selectedLevel === 'custom' ? 'Custom' : selectedLevel.charAt(0).toUpperCase() + selectedLevel.slice(1)} enhancement applied
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowPreview(!showPreview)}
                >
                  <Eye className="w-4 h-4 mr-2" />
                  {showPreview ? 'Hide' : 'Show'} Preview
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedLevel(null);
                    setImpactScore(0);
                    setKeywordAnalysis({});
                    onEnhancementChange?.({
                      bulletIndex,
                      level: null,
                      originalText: bulletText,
                      enhancedText: bulletText,
                      impact: 0,
                      keywords: [],
                      metrics: []
                    });
                  }}
                >
                  Reset
                </Button>
              </div>
            </div>

            <AnimatePresence>
              {showPreview && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden mt-4 pt-4 border-t border-gray-200"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-2">Before</div>
                      <div className="p-3 bg-red-50 rounded border border-red-200">
                        <p className="text-sm text-gray-800">{bulletText}</p>
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-2">After</div>
                      <div className="p-3 bg-green-50 rounded border border-green-200">
                        <p className="text-sm text-gray-800">
                          {selectedLevel === 'custom' 
                            ? customText 
                            : enhancementOptions.find(opt => opt.level === selectedLevel)?.text || bulletText
                          }
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Impact Summary */}
                  {keywordAnalysis.added && (
                    <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">Enhancement Impact</span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-blue-700 font-medium">ATS Score: </span>
                          <span className="text-blue-800">+{impactScore} points</span>
                        </div>
                        <div>
                          <span className="text-blue-700 font-medium">Keywords: </span>
                          <span className="text-blue-800">+{keywordAnalysis.added?.length || 0}</span>
                        </div>
                        <div>
                          <span className="text-blue-700 font-medium">Confidence: </span>
                          <span className="text-blue-800">{keywordAnalysis.confidence}%</span>
                        </div>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </EnhancedCardFooter>
        )}
      </EnhancedCard>
    </motion.div>
  );
}

/**
 * JobRelevanceScoring Component
 * Subtask 6.2: Display job relevance percentage and requirements matching
 */
function JobRelevanceScoring({
  experienceItem,
  jobData,
  onRelevanceUpdate,
  className = ''
}) {
  const [relevanceScore, setRelevanceScore] = useState(0);
  const [matchingRequirements, setMatchingRequirements] = useState([]);
  const [gapAnalysis, setGapAnalysis] = useState([]);
  const [contextualSuggestions, setContextualSuggestions] = useState([]);
  const [expandedAnalysis, setExpandedAnalysis] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Mock job relevance data - in real implementation, this would come from API
  const mockRelevanceData = useMemo(() => ({
    overallRelevance: 78,
    skillsMatch: 85,
    experienceMatch: 72,
    industryMatch: 90,
    matchingRequirements: [
      { requirement: 'React Development', match: 95, type: 'technical' },
      { requirement: 'Team Leadership', match: 80, type: 'soft_skill' },
      { requirement: 'Agile Methodology', match: 70, type: 'process' },
      { requirement: 'JavaScript/TypeScript', match: 90, type: 'technical' },
      { requirement: 'Problem Solving', match: 85, type: 'soft_skill' }
    ],
    gapAnalysis: [
      { requirement: 'Kubernetes', impact: 'high', suggestion: 'Add container orchestration experience' },
      { requirement: 'AWS Cloud Services', impact: 'medium', suggestion: 'Mention cloud deployment experience' },
      { requirement: 'Performance Optimization', impact: 'medium', suggestion: 'Quantify performance improvements' }
    ],
    contextualSuggestions: [
      {
        type: 'keyword_addition',
        priority: 'high',
        suggestion: 'Add "scalable" and "microservices" to highlight architecture experience',
        impact: 12
      },
      {
        type: 'metric_enhancement',
        priority: 'high',
        suggestion: 'Include team size and project timeline metrics',
        impact: 8
      },
      {
        type: 'responsibility_emphasis',
        priority: 'medium',
        suggestion: 'Emphasize cross-functional collaboration',
        impact: 6
      }
    ]
  }), []);

  useEffect(() => {
    const analyzeRelevance = async () => {
      setIsAnalyzing(true);
      
      // Simulate API call for relevance analysis
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setRelevanceScore(mockRelevanceData.overallRelevance);
      setMatchingRequirements(mockRelevanceData.matchingRequirements);
      setGapAnalysis(mockRelevanceData.gapAnalysis);
      setContextualSuggestions(mockRelevanceData.contextualSuggestions);
      
      onRelevanceUpdate?.({
        experienceId: experienceItem.id,
        relevanceScore: mockRelevanceData.overallRelevance,
        matchingRequirements: mockRelevanceData.matchingRequirements,
        gaps: mockRelevanceData.gapAnalysis
      });
      
      setIsAnalyzing(false);
    };

    if (experienceItem && jobData) {
      analyzeRelevance();
    }
  }, [experienceItem, jobData, mockRelevanceData, onRelevanceUpdate]);

  const getRelevanceColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 40) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getImpactColor = (impact) => {
    const colors = {
      high: 'text-red-600 bg-red-50 border-red-200',
      medium: 'text-amber-600 bg-amber-50 border-amber-200',
      low: 'text-green-600 bg-green-50 border-green-200'
    };
    return colors[impact] || colors.medium;
  };

  const getPriorityIcon = (priority) => {
    if (priority === 'high') return <AlertCircle className="w-4 h-4 text-red-500" />;
    if (priority === 'medium') return <Info className="w-4 h-4 text-amber-500" />;
    return <CheckCircle className="w-4 h-4 text-green-500" />;
  };

  return (
    <motion.div
      variants={staggerItem}
      className={`space-y-4 ${className}`}
    >
      <EnhancedCard>
        <EnhancedCardHeader>
          <div className="flex items-center justify-between">
            <div>
              <EnhancedCardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Job Relevance Analysis
                <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getRelevanceColor(relevanceScore)}`}>
                  {relevanceScore}% Match
                </div>
              </EnhancedCardTitle>
              <EnhancedCardDescription>
                How well this experience aligns with job requirements
              </EnhancedCardDescription>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setExpandedAnalysis(!expandedAnalysis)}
              className="text-blue-600 border-blue-300"
            >
              {expandedAnalysis ? (
                <>
                  <ChevronUp className="w-4 h-4 mr-2" />
                  Hide Details
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4 mr-2" />
                  Show Details
                </>
              )}
            </Button>
          </div>
        </EnhancedCardHeader>

        <EnhancedCardContent>
          {isAnalyzing ? (
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center gap-2 text-blue-600">
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Analyzing job relevance...</span>
              </div>
            </div>
          ) : (
            <>
              {/* Relevance Score Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-2 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-xl font-bold text-blue-600">{relevanceScore}%</span>
                  </div>
                  <div className="text-sm font-medium text-gray-900">Overall</div>
                  <div className="text-xs text-gray-600">Job Match</div>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-2 bg-gradient-to-br from-green-100 to-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xl font-bold text-green-600">{mockRelevanceData.skillsMatch}%</span>
                  </div>
                  <div className="text-sm font-medium text-gray-900">Skills</div>
                  <div className="text-xs text-gray-600">Technical Match</div>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-2 bg-gradient-to-br from-amber-100 to-orange-100 rounded-full flex items-center justify-center">
                    <span className="text-xl font-bold text-amber-600">{mockRelevanceData.experienceMatch}%</span>
                  </div>
                  <div className="text-sm font-medium text-gray-900">Experience</div>
                  <div className="text-xs text-gray-600">Role Match</div>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-2 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center">
                    <span className="text-xl font-bold text-purple-600">{mockRelevanceData.industryMatch}%</span>
                  </div>
                  <div className="text-sm font-medium text-gray-900">Industry</div>
                  <div className="text-xs text-gray-600">Sector Fit</div>
                </div>
              </div>

              {/* High-Impact Suggestions */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <Lightbulb className="w-4 h-4 text-amber-500" />
                  <span className="text-sm font-medium text-gray-700">Enhancement Suggestions</span>
                </div>
                
                <div className="space-y-3">
                  {contextualSuggestions.map((suggestion, index) => (
                    <motion.div
                      key={index}
                      variants={staggerItem}
                      className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200"
                    >
                      <div className="flex-shrink-0 mt-0.5">
                        {getPriorityIcon(suggestion.priority)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-gray-900">
                            {suggestion.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </span>
                          <div className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                            +{suggestion.impact} pts
                          </div>
                        </div>
                        <p className="text-sm text-gray-700">{suggestion.suggestion}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Expanded Analysis */}
              <AnimatePresence>
                {expandedAnalysis && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden border-t border-gray-200 pt-6"
                  >
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* Matching Requirements */}
                      <div>
                        <div className="flex items-center gap-2 mb-4">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="text-sm font-medium text-gray-700">Matching Requirements</span>
                        </div>
                        
                        <div className="space-y-3">
                          {matchingRequirements.map((req, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded border border-green-200">
                              <div>
                                <div className="text-sm font-medium text-gray-900">{req.requirement}</div>
                                <div className="text-xs text-gray-600 capitalize">{req.type.replace('_', ' ')}</div>
                              </div>
                              <div className="text-right">
                                <div className="text-sm font-bold text-green-600">{req.match}%</div>
                                <div className="text-xs text-green-700">Match</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Gap Analysis */}
                      <div>
                        <div className="flex items-center gap-2 mb-4">
                          <AlertCircle className="w-4 h-4 text-amber-500" />
                          <span className="text-sm font-medium text-gray-700">Areas for Improvement</span>
                        </div>
                        
                        <div className="space-y-3">
                          {gapAnalysis.map((gap, index) => (
                            <div key={index} className={`p-3 rounded border ${getImpactColor(gap.impact)}`}>
                              <div className="flex items-center justify-between mb-2">
                                <div className="text-sm font-medium text-gray-900">{gap.requirement}</div>
                                <div className={`px-2 py-1 rounded text-xs font-medium ${getImpactColor(gap.impact)}`}>
                                  {gap.impact.charAt(0).toUpperCase() + gap.impact.slice(1)} Impact
                                </div>
                              </div>
                              <p className="text-sm text-gray-700">{gap.suggestion}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </>
          )}
        </EnhancedCardContent>
      </EnhancedCard>
    </motion.div>
  );
}

/**
 * ExperienceContextDisplay Component
 * Shows experience item context with job relevance indicators
 */
function ExperienceContextDisplay({
  experienceItem,
  jobRelevance,
  className = ''
}) {
  const getRelevanceStars = (relevance) => {
    const stars = Math.round(relevance / 20); // Convert to 1-5 star rating
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < stars ? 'text-amber-500 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  const getRelevanceLabel = (relevance) => {
    if (relevance >= 80) return { label: 'Highly Relevant', color: 'text-green-600 bg-green-50 border-green-200' };
    if (relevance >= 60) return { label: 'Relevant', color: 'text-blue-600 bg-blue-50 border-blue-200' };
    if (relevance >= 40) return { label: 'Somewhat Relevant', color: 'text-amber-600 bg-amber-50 border-amber-200' };
    return { label: 'Low Relevance', color: 'text-red-600 bg-red-50 border-red-200' };
  };

  const relevanceInfo = getRelevanceLabel(jobRelevance);

  return (
    <motion.div
      variants={staggerItem}
      className={`mb-6 ${className}`}
    >
      <EnhancedCard>
        <EnhancedCardContent className="pt-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <Award className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  {experienceItem.title}
                </h3>
              </div>
              
              <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  <span>{experienceItem.company}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{experienceItem.duration}</span>
                </div>
              </div>

              <p className="text-sm text-gray-700 mb-4">
                {experienceItem.description}
              </p>
            </div>

            <div className="flex-shrink-0 ml-6 text-right">
              <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${relevanceInfo.color} mb-2`}>
                <Target className="w-4 h-4" />
                <span className="text-sm font-medium">{jobRelevance}% Match</span>
              </div>
              
              <div className="flex items-center gap-1 justify-end mb-2">
                {getRelevanceStars(jobRelevance)}
              </div>
              
              <div className={`text-xs font-medium ${relevanceInfo.color.split(' ')[0]}`}>
                {relevanceInfo.label}
              </div>
            </div>
          </div>
        </EnhancedCardContent>
      </EnhancedCard>
    </motion.div>
  );
}

/**
 * Main ExperienceTailoringInterface Component
 * Combines all sub-components for complete experience tailoring functionality
 */
function ExperienceTailoringInterface({
  experienceData,
  jobData,
  onEnhancementChange,
  onImpactUpdate,
  isProUser,
  onUpgradeClick,
  className = ''
}) {
  const [selectedExperience, setSelectedExperience] = useState(null);
  const [bulletChanges, setBulletChanges] = useState([]);
  const [totalImpact, setTotalImpact] = useState(0);
  const [relevanceData, setRelevanceData] = useState({});

  // Mock experience data
  const mockExperienceData = useMemo(() => [
    {
      id: 'exp1',
      title: 'Senior Software Engineer',
      company: 'TechCorp Inc.',
      duration: '2020 - 2023',
      description: 'Led development of scalable web applications using React and Node.js',
      bullets: [
        'Developed web applications for clients',
        'Worked with team members on projects',
        'Implemented new features and bug fixes',
        'Participated in code reviews and meetings'
      ],
      relevance: 85
    },
    {
      id: 'exp2',
      title: 'Full Stack Developer',
      company: 'StartupXYZ',
      duration: '2018 - 2020',
      description: 'Built and maintained full-stack applications with modern technologies',
      bullets: [
        'Created responsive user interfaces',
        'Developed backend APIs and services',
        'Managed database operations'
      ],
      relevance: 72
    }
  ], []);

  useEffect(() => {
    if (mockExperienceData.length > 0 && !selectedExperience) {
      setSelectedExperience(mockExperienceData[0]);
    }
  }, [mockExperienceData, selectedExperience]);

  const handleBulletEnhancement = useCallback((enhancementData) => {
    setBulletChanges(prev => {
      const updated = prev.filter(change => change.bulletIndex !== enhancementData.bulletIndex);
      if (enhancementData.impact > 0) {
        updated.push(enhancementData);
      }
      return updated;
    });

    // Update total impact
    const newTotal = bulletChanges.reduce((sum, change) => sum + (change.impact || 0), 0) + (enhancementData.impact || 0);
    setTotalImpact(newTotal);

    onEnhancementChange?.(enhancementData);
  }, [bulletChanges, onEnhancementChange]);

  const handleRelevanceUpdate = useCallback((data) => {
    setRelevanceData(prev => ({
      ...prev,
      [data.experienceId]: data
    }));
  }, []);

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Experience Selection */}
      <motion.div variants={staggerItem}>
        <div className="flex items-center gap-4 mb-6">
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-blue-600" />
            <span className="text-lg font-semibold text-gray-900">Experience Tailoring</span>
          </div>
          
          <select
            value={selectedExperience?.id || ''}
            onChange={(e) => {
              const exp = mockExperienceData.find(exp => exp.id === e.target.value);
              setSelectedExperience(exp);
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {mockExperienceData.map(exp => (
              <option key={exp.id} value={exp.id}>
                {exp.title} at {exp.company}
              </option>
            ))}
          </select>
        </div>
      </motion.div>

      {selectedExperience && (
        <>
          {/* Experience Context */}
          <ExperienceContextDisplay
            experienceItem={selectedExperience}
            jobRelevance={selectedExperience.relevance}
          />

          {/* Job Relevance Analysis */}
          <JobRelevanceScoring
            experienceItem={selectedExperience}
            jobData={jobData}
            onRelevanceUpdate={handleRelevanceUpdate}
          />

          {/* Bullet Enhancement Interfaces */}
          <div className="space-y-6">
            <div className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Edit3 className="w-5 h-5" />
              Bullet Point Enhancements
            </div>
            
            {selectedExperience.bullets.map((bullet, index) => (
              <BulletEnhancementInterface
                key={index}
                experienceItem={selectedExperience}
                bulletIndex={index}
                bulletText={bullet}
                jobRelevance={selectedExperience.relevance}
                onEnhancementChange={handleBulletEnhancement}
                onImpactUpdate={onImpactUpdate}
                isProUser={isProUser}
                onUpgradeClick={onUpgradeClick}
              />
            ))}
          </div>
        </>
      )}
    </motion.div>
  );
}

export default ExperienceTailoringInterface;
export { 
  BulletEnhancementInterface, 
  JobRelevanceScoring, 
  ExperienceContextDisplay,
  ExperienceTailoringInterface
};